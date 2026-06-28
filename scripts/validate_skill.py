#!/usr/bin/env python3
"""Validate the minimal Codex skill folder structure."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9-]{1,63}$")


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")

    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise ValueError("SKILL.md frontmatter must be closed with ---") from exc

    frontmatter = lines[1:end]
    result: dict[str, str] = {}
    current_key: str | None = None
    for line in frontmatter:
        if not line.strip():
            continue
        if line.startswith((" ", "\t")) and current_key:
            result[current_key] = f"{result[current_key]} {line.strip()}"
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current_key = key.strip()
        result[current_key] = value.strip().strip('"').strip("'").strip(">").strip()
    return result


def validate_skill(path: Path) -> list[str]:
    errors: list[str] = []
    skill_md = path / "SKILL.md"
    if not path.exists():
        return [f"skill path does not exist: {path}"]
    if not skill_md.exists():
        return ["missing SKILL.md"]

    try:
        frontmatter = parse_frontmatter(skill_md)
    except Exception as exc:  # noqa: BLE001 - CLI should report validation failure plainly.
        return [str(exc)]

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")
    if not name:
        errors.append("frontmatter.name is required")
    elif not NAME_RE.fullmatch(name):
        errors.append("frontmatter.name must use lowercase letters, digits, and hyphens only")
    elif path.name != name and not (path / ".git").exists():
        errors.append(f"folder name '{path.name}' must match frontmatter.name '{name}'")

    if not description or len(description) < 40:
        errors.append("frontmatter.description must describe what the skill does and when to use it")

    openai_yaml = path / "agents" / "openai.yaml"
    if openai_yaml.exists():
        content = openai_yaml.read_text(encoding="utf-8")
        for key in ("display_name", "short_description", "default_prompt"):
            if key not in content:
                errors.append(f"agents/openai.yaml missing interface.{key}")

    return errors


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_path", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors = validate_skill(args.skill_path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: skill structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
