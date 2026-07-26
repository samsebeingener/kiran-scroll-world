#!/usr/bin/env python3
"""Validate Scroll World plugin layout and core script imports."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    ".cursor-plugin/plugin.json",
    "agents/director.md",
    "commands/scroll-world-start.md",
    "commands/scroll-world-run.md",
    "rules/scroll-world-orchestrator.mdc",
    "skills/scroll-world-director/SKILL.md",
    "shared/media-format-contract.md",
    "shared/storyboard-generation-contract.md",
    "shared/video-generation-contract.md",
    "shared/agent-data-flow-contract.md",
    "scripts/generate_storyboard_panels.py",
    "scripts/kie_seedance_2_mini.py",
    "scripts/media_format.py",
    "scripts/encode_scrub_clips.py",
    "requirements.txt",
    "README.md",
    "LICENSE",
    ".env.example",
]

REQUIRED_AGENTS = {
    "director",
    "intake",
    "journey",
    "storyboard",
    "slicer",
    "video",
    "encoder",
    "builder",
    "qa",
    "fixic",
}


def main() -> None:
    errors: list[str] = []

    for rel in REQUIRED_PATHS:
        if not (ROOT / rel).exists():
            errors.append(f"missing:{rel}")

    agent_dir = ROOT / "agents"
    found_agents = {p.stem for p in agent_dir.glob("*.md")}
    missing_agents = REQUIRED_AGENTS - found_agents
    if missing_agents:
        errors.append(f"missing-agents:{sorted(missing_agents)}")

    plugin = json.loads((ROOT / ".cursor-plugin/plugin.json").read_text(encoding="utf-8"))
    if plugin.get("name") != "scroll-world":
        errors.append("plugin-name-mismatch")

    # Import core scripts (syntax + top-level deps)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import media_format  # noqa: F401
        import kie_seedance_2_mini as seedance  # noqa: F401

        if seedance.DEFAULT_DURATION != 4:
            errors.append(f"seedance-default-duration:{seedance.DEFAULT_DURATION}")
        if seedance.DURATION_MIN != 4:
            errors.append(f"seedance-duration-min:{seedance.DURATION_MIN}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"script-import:{exc}")

    if errors:
        print(json.dumps({"status": "blocked", "errors": errors}, indent=2))
        raise SystemExit(2)

    pytest = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if pytest.returncode != 0:
        print(pytest.stdout)
        print(pytest.stderr, file=sys.stderr)
        raise SystemExit(pytest.returncode)

    print(
        json.dumps(
            {
                "status": "ok",
                "artifacts": len(REQUIRED_PATHS),
                "agents": len(found_agents),
                "pytest": "pass",
            }
        )
    )


if __name__ == "__main__":
    main()
