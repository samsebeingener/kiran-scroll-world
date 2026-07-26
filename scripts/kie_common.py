"""Shared Kie.ai API utilities (auth, polling, download)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

try:
    import requests
except ImportError as exc:
    raise SystemExit("Install requests: pip install requests") from exc

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore

DEFAULT_BASE = "https://api.kie.ai/api/v1"


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

    def create_task_raw(self, payload: dict[str, Any]) -> str:
        url = f"{self.base_url}/jobs/createTask"
        resp = self.session.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        body = resp.json()
        if body.get("code") != 200:
            raise RuntimeError(f"createTask failed: {body.get('msg', body)}")
        task_id = body.get("data", {}).get("taskId")
        if not task_id:
            raise RuntimeError(f"No taskId in response: {body}")
        return task_id

    def get_task(self, task_id: str) -> dict[str, Any]:
        qs = urlencode({"taskId": task_id})
        url = f"{self.base_url}/jobs/recordInfo?{qs}"
        resp = self.session.get(url, timeout=60)
        resp.raise_for_status()
        body = resp.json()
        if body.get("code") != 200:
            raise RuntimeError(f"recordInfo failed: {body.get('msg', body)}")
        return body.get("data", {})

    def wait_for_task(self, task_id: str) -> dict[str, Any]:
        deadline = time.time() + self.poll_timeout
        attempt = 0
        while time.time() < deadline:
            data = self.get_task(task_id)
            state = data.get("state")
            if state == "success":
                return data
            if state == "fail":
                raise RuntimeError(
                    f"Task failed: {data.get('failCode')} — {data.get('failMsg')}"
                )
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
            parsed = json.loads(raw)
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
        dest.write_bytes(resp.content)
        return dest
