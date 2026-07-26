#!/usr/bin/env python3
"""Build assets/overlays.json from 03-journey.md section table."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from asset_versions import active_leg_files

SECTION_HEADER = re.compile(r"^#{2,3}\s+Scene\s+(\d+)\s*[:—-]\s*(.+)$", re.I)
FIELD = re.compile(
    r"^\-\s+\*\*(title|body|accent|scroll|linger|cta_primary|cta_secondary|cta_primary_href|cta_secondary_href):\*\*\s*(.+)$",
    re.I,
)


def sections_for_legs(journey_sections: list[dict], n_legs: int) -> list[dict]:
    """Map journey overlay scenes to one scene per video leg."""
    n = len(journey_sections)
    if n < n_legs:
        raise SystemExit(
            f"Journey has {n} overlay scene(s) but {n_legs} leg(s) need {n_legs}. "
            "Add scenes in 03-journey.md."
        )
    if n == n_legs:
        return journey_sections
    # M keyframe scenes for M-1 legs: scenes 1..L-1 + finale (CTA on last leg)
    if n == n_legs + 1:
        return journey_sections[: n_legs - 1] + [journey_sections[-1]]
    return journey_sections[:n_legs]


def parse_journey(text: str) -> dict:
    sections: list[dict] = []
    current: dict | None = None
    cta: dict | None = None

    for line in text.splitlines():
        m = SECTION_HEADER.match(line.strip())
        if m:
            if current:
                sections.append(current)
            idx = int(m.group(1))
            current = {
                "id": f"scene-{idx:02d}",
                "label": m.group(2).strip(),
                "title": "",
                "body": "",
                "scroll": 1.5,
                "linger": 0.45,
                "accent": "#8FB98A",
            }
            continue
        if current is None:
            continue
        fm = FIELD.match(line.strip())
        if not fm:
            continue
        key = fm.group(1).lower()
        val = fm.group(2).strip().strip("`\"'")
        if key in {"scroll", "linger"}:
            current[key] = float(val.replace(",", "."))
        elif key == "cta_primary":
            label, _, href = val.partition("|")
            cta = cta or {}
            cta["primary"] = {
                "label": label.strip(),
                "href": (href or cta.get("primary", {}).get("href") or "#cta").strip(),
            }
        elif key == "cta_secondary":
            label, _, href = val.partition("|")
            cta = cta or {}
            cta["secondary"] = {
                "label": label.strip(),
                "href": (href or cta.get("secondary", {}).get("href") or "#more").strip(),
            }
        elif key == "cta_primary_href":
            cta = cta or {}
            entry = cta.setdefault("primary", {"label": "", "href": "#cta"})
            entry["href"] = val
        elif key == "cta_secondary_href":
            cta = cta or {}
            entry = cta.setdefault("secondary", {"label": "", "href": "#more"})
            entry["href"] = val
        else:
            current[key] = val

    if current:
        sections.append(current)

    return {
        "diveScroll": 1.3,
        "crossfade": 0.12,
        "scrubLerp": 0.08,
        "scrubEps": 0.002,
        "sections": sections,
        "cta": cta,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()

    project = args.project.resolve()
    journey = project / "03-journey.md"
    if not journey.exists():
        raise SystemExit(f"Missing {journey}")

    data = parse_journey(journey.read_text(encoding="utf-8"))
    if not data["sections"]:
        raise SystemExit(
            "No scenes parsed. Use headers like `## Scene 1: Farms` and "
            "`- **title**: …` fields (see templates/journey.example.md)."
        )

    legs = active_leg_files(project)
    if legs:
        before = len(data["sections"])
        data["sections"] = sections_for_legs(data["sections"], len(legs))
        if len(data["sections"]) != before:
            print(f"overlay scenes: {before} journey -> {len(data['sections'])} legs")

    out = project / "assets" / "overlays.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)

    manifest_path = project / "assets" / "manifest.json"
    manifest: dict = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["overlays"] = "assets/overlays.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
