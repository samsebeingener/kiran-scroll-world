"""Shared Kie.ai API utilities (auth, polling, download)."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

# Markdown agent notes must NEVER reach Kie createTask `prompt`.
_TEXT_FENCE_RE = re.compile(r"```text\s*\n(.*?)```", re.IGNORECASE | re.DOTALL)
_PROMPT_FILE_LEAK_MARKERS = (
    "slug:",
    "# storyboard board prompt",
    "# video leg prompt",
    "mode: text-to-image",
    "mode: image-to-image",
    "if kie 2k",
    "1k+3:1 workaround",
    "05-image-prompts",
    "project.meta.json",
    "generate_storyboard_panels",
    "kie_seedance",
)

try:
    import requests
except ImportError as exc:
    raise SystemExit("Install requests: pip install requests") from exc

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore

DEFAULT_BASE = "https://api.kie.ai/api/v1"

RETRY_DELAY_SEC = 5.0

FATAL_KIE_CODES: dict[int, str] = {
    401: "Unauthorized — check KIE_API_KEY",
    402: "Insufficient Credits — top up the Kie balance",
    404: "Not Found — check endpoint/model",
    422: "Validation Error — check request payload",
    433: "Sub-key Usage Limit reached",
    505: "Feature Disabled for this account/model",
}
TRANSIENT_KIE_CODES = frozenset({429, 455, 500, 501})


class KieTransientError(RuntimeError):
    """Retryable Kie failure (network, 429/455/5xx, task state=fail)."""


class KieTaskFailedError(KieTransientError):
    """Task reached state=fail; caller should re-submit a new task."""


def extract_kie_prompt_from_markdown(
    raw: str,
    *,
    require_text_fence: bool = False,
    source: str | Path | None = None,
) -> str:
    """Return only the visual prompt for Kie.

    Prompt markdown may contain agent notes (slug, M, grid, workarounds) **outside**
    a ```text fence. Kie must receive **only** the fenced body — never the header.

    - If one or more ```text ... ``` fences exist → use the **first** fence body.
    - If none and ``require_text_fence`` → SystemExit.
    - If none and not required → whole file (legacy bare prompts), with leak check.
    """
    text = (raw or "").lstrip("\ufeff").strip()
    if not text:
        label = str(source) if source else "prompt file"
        raise SystemExit(f"Empty prompt file: {label}")

    matches = _TEXT_FENCE_RE.findall(text)
    if matches:
        prompt = matches[0].strip()
    elif require_text_fence:
        label = str(source) if source else "prompt file"
        raise SystemExit(
            f"Missing ```text fence in {label}. "
            "Put only the Kie visual prompt inside ```text … ```; "
            "keep slug/M/grid/notes outside the fence "
            "(see templates/storyboard-prompt.template.md)."
        )
    else:
        prompt = text

    if not prompt:
        label = str(source) if source else "prompt file"
        raise SystemExit(f"Empty ```text fence in {label}")

    lower = prompt.lower()
    for marker in _PROMPT_FILE_LEAK_MARKERS:
        if marker in lower:
            label = str(source) if source else "prompt"
            raise SystemExit(
                f"Pipeline/meta leak in Kie prompt from {label}: found {marker!r}. "
                "Agent notes (slug, mode, resolution workarounds) belong OUTSIDE "
                "the ```text fence — never in the createTask prompt."
            )
    return prompt


def check_kie_body(body: dict[str, Any], context: str) -> None:
    """Classify Kie API body code: fatal → SystemExit, transient → KieTransientError."""
    code = body.get("code")
    if code == 200:
        return
    msg = body.get("msg", body)
    if isinstance(code, int):
        if code in FATAL_KIE_CODES:
            raise SystemExit(f"{context}: Kie {code} {FATAL_KIE_CODES[code]}: {msg}")
        if code in TRANSIENT_KIE_CODES or code >= 500:
            raise KieTransientError(f"{context}: Kie {code}: {msg}")
    raise RuntimeError(f"{context}: unexpected Kie code {code}: {msg}")


def find_env_file(workspace: Path | str | None = None) -> Path | None:
    """Resolve .env: --workspace first, then cwd parents, then legacy Desktop fallback."""
    roots: list[Path] = []
    if workspace is not None:
        roots.append(Path(workspace).resolve())
    roots.extend([Path.cwd(), *Path.cwd().parents])
    seen: set[Path] = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        candidate = resolved / ".env"
        if candidate.is_file():
            return candidate
    for fallback in (
        Path.home() / ".cursor" / "plugins" / "local" / "scroll-world" / ".env",
        Path.home() / "Desktop" / "Carusel" / ".env",
    ):
        if fallback.is_file():
            return fallback
    return None


def load_api_key(
    explicit_key: str | None = None,
    workspace: Path | str | None = None,
) -> str:
    if explicit_key:
        return explicit_key.strip()

    env_path = find_env_file(workspace)
    if load_dotenv and env_path:
        load_dotenv(env_path, override=False)

    key = os.getenv("KIE_API_KEY", "").strip()
    if not key:
        hint = str(env_path) if env_path else "{workspace}/.env or cwd/.env"
        raise ValueError(
            f"KIE_API_KEY not set. Add your key to: {hint}\n"
            "Get key: https://kie.ai/api-key\n"
            "Hint: pass --workspace to the script so .env is loaded from that folder first."
        )
    return key


class KieTaskClient:
    """Base client for Kie.ai createTask + recordInfo polling."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        poll_interval: float = 5.0,
        poll_timeout: float = 1200.0,
        workspace: Path | str | None = None,
    ) -> None:
        self.api_key = load_api_key(api_key, workspace=workspace)
        self.base_url = (base_url or os.getenv("KIE_API_BASE") or DEFAULT_BASE).rstrip("/")
        self.poll_interval = float(os.getenv("KIE_POLL_INTERVAL_SEC", poll_interval))
        self.poll_timeout = float(os.getenv("KIE_POLL_TIMEOUT_SEC", poll_timeout))
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, url: str, context: str, **kwargs: Any) -> dict[str, Any]:
        try:
            resp = self.session.request(method, url, timeout=60, **kwargs)
        except requests.RequestException as exc:
            raise KieTransientError(f"{context}: network error: {exc}") from exc
        if resp.status_code in FATAL_KIE_CODES:
            raise SystemExit(
                f"{context}: HTTP {resp.status_code} "
                f"{FATAL_KIE_CODES[resp.status_code]}: {resp.text[:300]}"
            )
        if resp.status_code == 429 or resp.status_code >= 500:
            raise KieTransientError(
                f"{context}: HTTP {resp.status_code}: {resp.text[:300]}"
            )
        resp.raise_for_status()
        body = resp.json()
        check_kie_body(body, context)
        return body

    def create_task_raw(self, payload: dict[str, Any]) -> str:
        url = f"{self.base_url}/jobs/createTask"
        body = self._request("POST", url, "createTask", json=payload)
        task_id = body.get("data", {}).get("taskId")
        if not task_id:
            raise RuntimeError(f"No taskId in response: {body}")
        return task_id

    def get_task(self, task_id: str) -> dict[str, Any]:
        qs = urlencode({"taskId": task_id})
        url = f"{self.base_url}/jobs/recordInfo?{qs}"
        body = self._request("GET", url, "recordInfo")
        return body.get("data", {})

    PENDING_STATES = frozenset(
        {"waiting", "queuing", "queue", "pending", "generating", "running", "processing", None}
    )

    def wait_for_task(self, task_id: str) -> dict[str, Any]:
        deadline = time.time() + self.poll_timeout
        attempt = 0
        while time.time() < deadline:
            try:
                data = self.get_task(task_id)
            except KieTransientError as exc:
                print(
                    f"  poll transient error ({exc}); retry in {RETRY_DELAY_SEC}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(RETRY_DELAY_SEC)
                continue
            state = data.get("state")
            if state == "success":
                return data
            if state == "fail":
                raise KieTaskFailedError(
                    f"Task failed: {data.get('failCode')} — {data.get('failMsg')}"
                )
            if state not in self.PENDING_STATES:
                raise RuntimeError(f"Task {task_id} unknown terminal state: {state!r} — {data}")
            attempt += 1
            if attempt == 1 or attempt % 6 == 0:
                elapsed = int(time.time() - (deadline - self.poll_timeout))
                print(f"  poll #{attempt} state={state!r} elapsed={elapsed}s ...")
            time.sleep(self.poll_interval)
        raise TimeoutError(f"Task {task_id} timed out after {self.poll_timeout}s")

    @staticmethod
    def extract_result_urls(task_data: dict[str, Any]) -> list[str]:
        raw = task_data.get("resultJson")
        if not raw:
            return []
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"resultJson is not valid JSON: {exc}; raw={raw[:200]!r}"
                ) from exc
        else:
            parsed = raw
        urls = parsed.get("resultUrls") or []
        if not isinstance(urls, list):
            return []
        return [u for u in urls if isinstance(u, str) and u]

    def download(self, url: str, dest: Path) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)
        resp = self.session.get(url, timeout=300)
        resp.raise_for_status()
        content_type = (resp.headers.get("Content-Type") or "").lower()
        body = resp.content
        if not body:
            raise SystemExit(f"Download failed: empty body from {url}")
        if "text/html" in content_type or body.lstrip()[:15].lower().startswith(
            (b"<!doctype", b"<html")
        ):
            raise SystemExit(
                f"Download failed: CDN returned HTML instead of media "
                f"(status {resp.status_code}, content-type {content_type or 'n/a'}) for {url}. "
                "Not writing garbage to file."
            )
        dest.write_bytes(body)
        return dest


def run_task_with_retry(
    client: KieTaskClient,
    payload: dict[str, Any],
    *,
    max_attempts: int = 5,
    retry_delay: float = RETRY_DELAY_SEC,
) -> dict[str, Any]:
    """Create task + poll; on transient failure re-submit a NEW task after retry_delay.

    Fatal Kie codes (401/402/404/422/433/505) raise SystemExit immediately —
    retry cannot fix auth/credits/validation.
    """
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            task_id = client.create_task_raw(payload)
        except KieTransientError as exc:
            last_exc = exc
            print(
                f"attempt {attempt}/{max_attempts}: createTask transient error ({exc}); "
                f"re-submit in {retry_delay}s",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(retry_delay)
            continue
        print(f"taskId={task_id} (attempt {attempt}/{max_attempts})", flush=True)
        try:
            return client.wait_for_task(task_id)
        except KieTaskFailedError as exc:
            last_exc = exc
            print(
                f"attempt {attempt}/{max_attempts}: task {task_id} failed ({exc}); "
                f"re-submitting new task in {retry_delay}s",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(retry_delay)
    raise SystemExit(f"Kie task failed after {max_attempts} attempts: {last_exc}")
