#!/usr/bin/env python3
"""Version helpers for scroll-world assets (001, 002, …). Never delete old versions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VERSION_RE = re.compile(r"^(\d{3})-")


def parse_version_prefix(name: str) -> int | None:
    m = VERSION_RE.match(name)
    return int(m.group(1)) if m else None


def format_version(n: int) -> str:
    if n < 1:
        raise ValueError("version must be >= 1")
    return f"{n:03d}"


def list_versions(directory: Path, suffix_glob: str) -> list[int]:
    directory = Path(directory)
    if not directory.is_dir():
        return []
    found: set[int] = set()
    for path in directory.glob(suffix_glob):
        v = parse_version_prefix(path.name)
        if v is not None:
            found.add(v)
    return sorted(found)


def next_version(directory: Path, suffix_glob: str) -> int:
    versions = list_versions(directory, suffix_glob)
    return (versions[-1] + 1) if versions else 1


def load_manifest(project: Path) -> dict:
    path = project / "assets" / "manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(project: Path, manifest: dict) -> Path:
    path = project / "assets" / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def register_storyboard(project: Path, version: int, rel_path: str, *, set_active: bool = True) -> dict:
    manifest = load_manifest(project)
    sb = manifest.setdefault("storyboard", {})
    versions = sb.setdefault("versions", {})
    key = format_version(version)
    versions[key] = rel_path.replace("\\", "/")
    sb["latest_version"] = max(int(k) for k in versions)
    if set_active:
        sb["active_version"] = version
    manifest["storyboard"] = sb
    save_manifest(project, manifest)
    return manifest


def register_leg(
    project: Path,
    leg: int,
    version: int,
    rel_path: str,
    *,
    set_active: bool = True,
) -> dict:
    manifest = load_manifest(project)
    legs = manifest.setdefault("legs", {})
    entry = legs.setdefault(str(leg), {"versions": {}})
    versions = entry.setdefault("versions", {})
    key = format_version(version)
    versions[key] = rel_path.replace("\\", "/")
    entry["latest_version"] = max(int(k) for k in versions)
    if set_active:
        entry["active_version"] = version
    legs[str(leg)] = entry
    manifest["legs"] = legs
    save_manifest(project, manifest)
    return manifest


def active_leg_files(project: Path) -> list[Path]:
    """Active versioned leg MP4s from manifest, in leg order."""
    manifest = load_manifest(project)
    legs_meta = manifest.get("legs") or {}
    files: list[Path] = []
    if isinstance(legs_meta, dict) and legs_meta:
        numeric_ids: list[tuple[int, str]] = []
        for leg_id in legs_meta:
            try:
                numeric_ids.append((int(leg_id), leg_id))
            except (TypeError, ValueError):
                print(
                    f"WARN: skipping non-numeric leg key {leg_id!r} in manifest.legs",
                    file=sys.stderr,
                    flush=True,
                )
        missing: list[str] = []
        for _, leg_id in sorted(numeric_ids):
            entry = legs_meta[leg_id]
            if not isinstance(entry, dict):
                continue
            active = entry.get("active_version")
            versions = entry.get("versions") or {}
            if active is None:
                continue
            key = format_version(int(active))
            rel = versions.get(key)
            if not rel:
                continue
            path = project / rel
            if path.is_file():
                files.append(path)
            else:
                missing.append(rel)
        if missing:
            print(
                "WARN: active leg files from manifest are missing on disk: "
                + ", ".join(missing),
                file=sys.stderr,
                flush=True,
            )
        if files:
            return files

    legs_dir = project / "assets" / "video" / "legs"
    fallback = sorted(legs_dir.glob("*-leg-*.mp4"))
    prefixes = {parse_version_prefix(p.name) for p in fallback}
    prefixes.discard(None)
    if len(prefixes) > 1:
        print(
            "WARN: fallback leg glob mixes version prefixes "
            f"{sorted(prefixes)} — files from different versions are used together",
            file=sys.stderr,
            flush=True,
        )
    return fallback


def set_frame_active_map(project: Path, active_map: dict[str, str], *, merge: bool = True) -> dict:
    manifest = load_manifest(project)
    frames = manifest.setdefault("frames", {})
    current = frames.get("active_map", {}) if merge else {}
    if not isinstance(current, dict):
        current = {}
    normalized = {str(k): str(v).replace("\\", "/") for k, v in active_map.items()}
    current.update(normalized)
    frames["active_map"] = dict(sorted(current.items(), key=lambda kv: int(kv[0])))
    manifest["frames"] = frames
    save_manifest(project, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Scroll World asset version helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("next")
    n.add_argument("--dir", required=True, type=Path)
    n.add_argument("--glob", required=True, help="e.g. '*-board.png' or '*-leg-00.mp4'")

    l = sub.add_parser("list")
    l.add_argument("--dir", required=True, type=Path)
    l.add_argument("--glob", required=True)

    args = parser.parse_args()
    if args.cmd == "next":
        print(format_version(next_version(args.dir, args.glob)))
    elif args.cmd == "list":
        print(",".join(format_version(v) for v in list_versions(args.dir, args.glob)) or "(none)")


if __name__ == "__main__":
    main()
