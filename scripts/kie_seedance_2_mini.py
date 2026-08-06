#!/usr/bin/env python3
"""Create bytedance/seedance-2-mini leg from first_frame_url + last_frame_url.

Frame chain (default):
  leg 0 — start: storyboard frame 1, end: storyboard frame 2
  leg i>0 — start: last frame of active leg i-1 MP4, end: storyboard frame i+2

With project.meta.json playback_chain=[1..K]: leg i connects chain[i]→chain[i+1]
(max leg = K-2). Duration: CLI > video_durations[leg] > video_duration > 5 (range 4–10).

Docs: https://docs.kie.ai/market/bytedance/seedance-2-mini
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from asset_versions import format_version, load_manifest, next_version, register_leg
from kie_common import KieTaskClient, extract_kie_prompt_from_markdown, run_task_with_retry
from kie_file_upload import KieFileUploadClient
from media_format import load_project_meta, resolve_cell_aspect
from video_frame_chain import resolve_leg_frame_paths, save_leg_last_frame

MODEL = "bytedance/seedance-2-mini"
SUPPORTED_ASPECT = frozenset({"1:1", "4:3", "3:4", "16:9", "9:16", "21:9", "adaptive"})
SUPPORTED_RESOLUTION = frozenset({"480p", "720p"})
DURATION_MIN = 4
DURATION_MAX = 10
DEFAULT_DURATION = 5
DEFAULT_RESOLUTION = "480p"

FORBIDDEN_URL_MARKERS = ("example.com", "localhost", "127.0.0.1", "placeholder")
MIN_PROMPT_CHARS = 800
MAX_PROMPT_CHARS = 20000
RECOMMENDED_PROMPT_CHARS = 1200
FORBIDDEN_PROMPT_SUBSTRINGS = (
    "frame sources",
    "previous leg",
    "next leg",
    "storyboard slice",
    "intermediate storyboard",
    "preserve rendered",
    "rendered end",
    "previous generation",
    "previous video",
    "snap-back",
    "snap back to storyboard",
    "momentum from previous",
    "continue the velocity",
    "continue momentum",
    "active_map",
    "ffmpeg",
    "@image1",
    "@image2",
)
FORBIDDEN_PROMPT_PATTERNS = (
    r"\bstoryboard\b",
    r"\bmp4\b",
    r"\bleg\s*\d+\b",
)

# Variant C / P0–P2 structure (templates/video-leg-prompt.template.md)
PLATE_LOCK_KEYS = (
    "silhouette_axis",
    "accent_color_position",
    "ground_plane",
    "horizon",
    "materials",
    "prop_count",
)
_TIMED_INTERVAL_RE = re.compile(r"\d+(?:\.\d+)?\s*[–-]\s*\d+(?:\.\d+)?")
_TECH_DUMP_RE = re.compile(r"\b(?:480p|720p)\b|settings:", re.IGNORECASE)
_SECTION_HEADER_RE = re.compile(r"^[A-Z][A-Z0-9 /&-]{2,}:\s*$")
# Section starts that end the CAMERA PATH region even when body shares the line
_CAMERA_PATH_END_PREFIXES = (
    "landing contract",
    "world continuity",
    "object transform",
    "material & light",
    "motion quality",
    "count:",
    "exclusions:",
    "forbidden:",
)


def _resolve_project_path(project: Path, path: Path) -> Path:
    return path if path.is_absolute() else (project / path)


def _extract_camera_path_region(prompt: str) -> str:
    """Prefer CAMERA PATH block for beat counting; else whole prompt."""
    lines = prompt.splitlines()
    start_i: int | None = None
    for i, line in enumerate(lines):
        if "camera path" in line.lower():
            start_i = i
            break
    if start_i is None:
        return prompt
    region = [lines[start_i]]
    for line in lines[start_i + 1 :]:
        stripped = line.strip()
        lower = stripped.lower()
        if stripped and (
            _SECTION_HEADER_RE.match(stripped)
            or any(lower.startswith(p) for p in _CAMERA_PATH_END_PREFIXES)
        ):
            break
        region.append(line)
    return "\n".join(region)


def _beat_budget_limit(duration: int) -> int | None:
    if 4 <= duration <= 6:
        return 3
    if 7 <= duration <= 10:
        return 4
    if 11 <= duration <= 15:
        return 5
    return None


def _prompt_structure_issues(prompt: str) -> list[str]:
    """P0–P2 hard structure checks (Variant C). Empty list = OK."""
    lower = prompt.lower()
    issues: list[str] = []
    tmpl = "templates/video-leg-prompt.template.md"
    if "stages" not in lower and "stage a" not in lower:
        issues.append(
            f"Missing STAGES / STAGE A marker (P0–P2). Fill per {tmpl}."
        )
    if "landing contract" not in lower:
        issues.append(
            f"Missing LANDING CONTRACT section (P0–P2). Fill per {tmpl}."
        )
    if "count:" not in lower:
        issues.append(
            f"Missing COUNT: marker (P0–P2). Fill per {tmpl}."
        )
    if "exclusions:" not in lower:
        issues.append(
            f"Missing EXCLUSIONS: marker (P0–P2). Fill per {tmpl}."
        )
    if "creative direction" not in lower:
        issues.append(
            f"Missing CREATIVE DIRECTION section (P0–P2). Fill per {tmpl}."
        )
    return issues


def _prompt_structure_soft_warnings(
    prompt: str, duration: int | None = None
) -> list[str]:
    """P0–P2 soft heuristics — WARN only, never exit."""
    lower = prompt.lower()
    warnings: list[str] = []

    lock_hits = sum(1 for key in PLATE_LOCK_KEYS if key in lower)
    if lock_hits < 4:
        warnings.append(
            f"plate lock keys sparse ({lock_hits}/6 of "
            f"{', '.join(PLATE_LOCK_KEYS)}); prefer ≥4 — "
            "see templates/video-leg-prompt.template.md (P0–P2)"
        )

    tech_hits = _TECH_DUMP_RE.findall(prompt)
    if tech_hits:
        unique = sorted({h.lower() if isinstance(h, str) else h for h in tech_hits})
        warnings.append(
            f"tech dump in prompt (pipeline settings belong in CLI/meta, not Kie text): "
            f"{unique} — see templates/video-leg-prompt.template.md (P0–P2)"
        )

    if duration is not None:
        limit = _beat_budget_limit(duration)
        if limit is not None:
            region = _extract_camera_path_region(prompt)
            intervals = _TIMED_INTERVAL_RE.findall(region)
            if len(intervals) > limit:
                warnings.append(
                    f"beat budget overflow heuristic: {len(intervals)} timed intervals "
                    f"for duration={duration}s (soft max {limit}) — "
                    "see templates/video-leg-prompt.template.md (P0–P2)"
                )

    if "landing contract" in lower:
        has_settle = (
            "settle" in lower
            or "0.4" in prompt
            or "0.5" in prompt
            or "0.6" in prompt
        )
        if not has_settle:
            warnings.append(
                "LANDING CONTRACT present but no settle window "
                "(0.4 / 0.5 / 0.6 / 'settle') — "
                "see templates/video-leg-prompt.template.md (P0–P2)"
            )

    return warnings


def resolve_resolution(cli_value: str | None, meta: dict[str, Any]) -> str:
    raw = (cli_value or meta.get("video_resolution") or DEFAULT_RESOLUTION).strip().lower()
    if raw in {"480", "480p"}:
        return "480p"
    if raw in {"720", "720p"}:
        return "720p"
    raise SystemExit(
        f"Unsupported resolution {raw!r}. Use 480p (default) or 720p."
    )


def resolve_duration(
    cli_value: int | None,
    meta: dict[str, Any],
    leg_index: int | None = None,
) -> int:
    """Resolve leg duration: CLI > video_durations[leg] > video_duration > default."""
    if cli_value is not None:
        duration = int(cli_value)
    else:
        duration = None
        durations = meta.get("video_durations")
        if (
            isinstance(durations, list)
            and leg_index is not None
            and 0 <= leg_index < len(durations)
            and durations[leg_index] is not None
        ):
            try:
                duration = int(durations[leg_index])
            except (TypeError, ValueError):
                raise SystemExit(
                    f"video_durations[{leg_index}] must be a number of seconds, "
                    f"got {durations[leg_index]!r} in project.meta.json"
                )
        if duration is None:
            hint = meta.get("video_duration")
            if hint is not None:
                try:
                    duration = int(hint)
                except (TypeError, ValueError):
                    raise SystemExit(
                        f"video_duration must be a number of seconds, "
                        f"got {hint!r} in project.meta.json"
                    )
            else:
                duration = DEFAULT_DURATION
    if duration < DURATION_MIN or duration > DURATION_MAX:
        raise SystemExit(
            f"duration must be {DURATION_MIN}–{DURATION_MAX} (got {duration}). "
            f"Default: {DEFAULT_DURATION}s; complex morphs often need 8–10s."
        )
    return duration


def validate_local_leg_inputs(
    *,
    start_path: Path,
    end_path: Path,
    prompt: str,
    duration: int | None = None,
) -> None:
    """Validate local frames + prompt (length, forbidden meta, Variant C P0–P2)."""
    if not start_path.is_file():
        raise SystemExit(f"Missing start frame: {start_path}")
    if not end_path.is_file():
        raise SystemExit(f"Missing end frame: {end_path}")

    prompt_stripped = prompt.strip()
    plen = len(prompt_stripped)
    if plen < MIN_PROMPT_CHARS:
        raise SystemExit(
            f"Prompt too short ({plen} chars, min {MIN_PROMPT_CHARS}). "
            "Expand per templates/video-leg-prompt.template.md (P0–P2) — "
            "STAGES / CREATIVE DIRECTION / LANDING CONTRACT, timed beats, "
            "plate locks (target 1200–4000 chars)."
        )
    if plen > MAX_PROMPT_CHARS:
        raise SystemExit(
            f"Prompt too long ({plen} chars, Kie max {MAX_PROMPT_CHARS}). Trim redundant lines."
        )
    if plen < RECOMMENDED_PROMPT_CHARS:
        print(
            f"WARN: prompt {plen} chars < recommended {RECOMMENDED_PROMPT_CHARS} — "
            "consider richer camera/object detail for Seedance 2 Mini.",
            flush=True,
        )
    if prompt_stripped.lower() in {"test", "testing", "prompt"}:
        raise SystemExit("Refusing placeholder prompt 'test'. Use 05-image-prompts/*-leg-*.md.")
    if "@image1" in prompt_stripped or "@image2" in prompt_stripped:
        raise SystemExit(
            "Prompt still uses @image1/@image2. Replace with 'first frame' / 'last frame' "
            "(see templates/video-leg-prompt.template.md)."
        )
    lower = prompt_stripped.lower()
    for phrase in FORBIDDEN_PROMPT_SUBSTRINGS:
        if phrase in lower:
            raise SystemExit(
                f"Prompt contains pipeline meta Kie cannot use: {phrase!r}. "
                "Describe only motion between the two uploaded PNGs. "
                "See shared/kie-prompt-contract.md"
            )
    for pattern in FORBIDDEN_PROMPT_PATTERNS:
        if re.search(pattern, lower):
            raise SystemExit(
                f"Prompt matches forbidden pattern {pattern!r} (pipeline meta). "
                "See shared/kie-prompt-contract.md"
            )

    # Variant C hard structure (P0–P2) — SystemExit immediately
    hard = _prompt_structure_issues(prompt_stripped)
    if hard:
        raise SystemExit("Prompt structure invalid (P0–P2):\n- " + "\n- ".join(hard))

    for msg in _prompt_structure_soft_warnings(prompt_stripped, duration=duration):
        print(f"WARN: {msg}", flush=True)


def validate_frame_urls(*, first_frame_url: str, last_frame_url: str) -> None:
    for label, url in (("first_frame_url", first_frame_url), ("last_frame_url", last_frame_url)):
        lower = url.lower()
        if not lower.startswith("https://"):
            raise SystemExit(f"{label} must be HTTPS Kie upload URL, got: {url!r}")
        if any(marker in lower for marker in FORBIDDEN_URL_MARKERS):
            raise SystemExit(f"{label} looks like a placeholder URL: {url!r}")


class Seedance2MiniClient(KieTaskClient):
    def leg_payload(
        self,
        *,
        first_frame_url: str,
        last_frame_url: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "480p",
        duration: int = DEFAULT_DURATION,
        generate_audio: bool = False,
        nsfw_checker: bool = False,
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        if aspect_ratio not in SUPPORTED_ASPECT:
            raise ValueError(f"Unsupported aspect_ratio {aspect_ratio!r}")
        if resolution not in SUPPORTED_RESOLUTION:
            raise ValueError(f"Unsupported resolution {resolution!r}; use 480p or 720p")
        if duration < DURATION_MIN or duration > DURATION_MAX:
            raise ValueError(f"duration must be {DURATION_MIN}–{DURATION_MAX}")

        payload: dict[str, Any] = {
            "model": MODEL,
            "input": {
                "prompt": prompt,
                "first_frame_url": first_frame_url,
                "last_frame_url": last_frame_url,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "generate_audio": generate_audio,
                "nsfw_checker": nsfw_checker,
            },
        }
        if callback_url:
            payload["callBackUrl"] = callback_url
        return payload

    def create_leg(self, **kwargs: Any) -> str:
        return self.create_task_raw(self.leg_payload(**kwargs))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seedance 2.0 Mini leg with video chain (prev leg last frame → storyboard end)"
    )
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--leg", type=int, required=True, help="0-based leg index")
    parser.add_argument(
        "--start",
        type=Path,
        default=None,
        help="Override first frame (default: storyboard #1 or last frame of leg-1)",
    )
    parser.add_argument(
        "--end",
        type=Path,
        default=None,
        help="Override last frame (default: storyboard frame leg+2 from active_map)",
    )
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--aspect-ratio", default=None)
    parser.add_argument("--resolution", default=None)
    parser.add_argument("--duration", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--generate-audio", action="store_true")
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--version", type=int, default=None)
    args = parser.parse_args()

    project = args.project.resolve()
    workspace = args.workspace or project
    meta = load_project_meta(project)
    resolution = resolve_resolution(args.resolution, meta)
    duration = resolve_duration(args.duration, meta, args.leg)
    aspect_ratio = resolve_cell_aspect(args.aspect_ratio, meta)
    if aspect_ratio not in SUPPORTED_ASPECT:
        raise SystemExit(f"Unsupported aspect_ratio {aspect_ratio!r} for Seedance")

    insert = meta.get("insert_placement") or meta.get("insert_place")
    if not insert and not args.force and not args.dry_run:
        raise SystemExit(
            "insert_placement not set in project.meta.json. Ask user (RU), write to meta, "
            "or pass --force after confirmation."
        )
    if not insert and args.dry_run:
        print("WARN: insert_placement not set — dry-run only.", flush=True)

    prompt_path = _resolve_project_path(project, args.prompt_file)
    if not prompt_path.is_file():
        raise SystemExit(f"Missing --prompt-file: {prompt_path}")
    raw_prompt = prompt_path.read_text(encoding="utf-8-sig")
    # Prefer ```text fence; bare files still allowed (legacy). Leak markers hard-fail.
    prompt = extract_kie_prompt_from_markdown(
        raw_prompt,
        require_text_fence=False,
        source=prompt_path,
    )

    start_override = _resolve_project_path(project, args.start) if args.start else None
    end_override = _resolve_project_path(project, args.end) if args.end else None
    start_path, end_path, chain_meta = resolve_leg_frame_paths(
        project,
        args.leg,
        start_override=start_override,
        end_override=end_override,
    )
    validate_local_leg_inputs(
        start_path=start_path,
        end_path=end_path,
        prompt=prompt,
        duration=duration,
    )

    legs_dir = project / "assets" / "video" / "legs"
    if args.version is not None:
        ver = args.version
        if ver < 1:
            raise SystemExit(f"--version must be >= 1, got {ver}")
        ver_s = format_version(ver)
        out_candidate = legs_dir / f"{ver_s}-leg-{args.leg:02d}.mp4"
        manifest_versions = (
            (load_manifest(project).get("legs") or {}).get(str(args.leg), {}) or {}
        ).get("versions") or {}
        if out_candidate.exists() or ver_s in manifest_versions:
            raise SystemExit(
                f"version {ver_s} already exists for leg {args.leg} "
                f"({out_candidate.name}); use next one — never overwrite (asset versioning contract)"
            )
    else:
        ver = next_version(legs_dir, f"*-leg-{args.leg:02d}.mp4")
        ver_s = format_version(ver)

    summary: dict[str, Any] = {
        "model": MODEL,
        "leg": args.leg,
        "chain": chain_meta,
        "start_file": str(start_path).replace("\\", "/"),
        "end_file": str(end_path).replace("\\", "/"),
        "prompt_file": str(prompt_path),
        "prompt_chars": len(prompt),
        "prompt_preview": prompt[:160] + ("…" if len(prompt) > 160 else ""),
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "duration": duration,
        "generate_audio": bool(args.generate_audio),
        "insert_placement": insert,
    }

    if args.dry_run:
        summary["first_frame_url"] = "(skipped — dry-run)"
        summary["last_frame_url"] = "(skipped — dry-run)"
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print("dry-run: skipped Kie upload + createTask")
        return

    uploader = KieFileUploadClient(workspace=workspace)
    first_frame_url = uploader.upload_stream(
        start_path, upload_path=f"scroll-world/{project.name}", file_name=start_path.name
    )["publicUrl"]
    last_frame_url = uploader.upload_stream(
        end_path, upload_path=f"scroll-world/{project.name}", file_name=end_path.name
    )["publicUrl"]
    validate_frame_urls(first_frame_url=first_frame_url, last_frame_url=last_frame_url)
    summary["first_frame_url"] = first_frame_url
    summary["last_frame_url"] = last_frame_url
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    client = Seedance2MiniClient(workspace=workspace)
    print(f"createTask {MODEL} leg={args.leg} resolution={resolution} duration={duration}")
    payload = client.leg_payload(
        first_frame_url=first_frame_url,
        last_frame_url=last_frame_url,
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        duration=duration,
        generate_audio=bool(args.generate_audio),
    )
    data = run_task_with_retry(client, payload, max_attempts=5)
    urls = client.extract_result_urls(data)
    if not urls:
        raise SystemExit(f"No resultUrls: {data}")
    if len(urls) > 1:
        print(
            f"WARN: API returned {len(urls)} result urls; using only the first",
            file=sys.stderr,
            flush=True,
        )

    legs_dir.mkdir(parents=True, exist_ok=True)
    out = legs_dir / f"{ver_s}-leg-{args.leg:02d}.mp4"
    client.download(urls[0], out)
    print(out)

    last_png = save_leg_last_frame(project, out, args.leg)
    print(f"last_frame_cache={last_png}")

    rel = str(out.relative_to(project)).replace("\\", "/")
    register_leg(project, args.leg, ver, rel, set_active=True)

    log_path = legs_dir / f"{ver_s}-leg-{args.leg:02d}.json"
    log_path.write_text(
        json.dumps(
            {
                "model": MODEL,
                "taskId": data.get("taskId"),
                "version": ver_s,
                "leg": args.leg,
                "chain": chain_meta,
                "start_file": str(start_path).replace("\\", "/"),
                "end_file": str(end_path).replace("\\", "/"),
                "last_frame_cache": str(last_png).replace("\\", "/"),
                "first_frame_url": first_frame_url,
                "last_frame_url": last_frame_url,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "duration": duration,
                "result_url": urls[0],
                "local": rel,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
