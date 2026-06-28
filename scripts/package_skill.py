#!/usr/bin/env python3
"""Build a clean distributable zip for the fact-check skill."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCLUDES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".git",
    ".github",
    "dist",
    "out",
}

DEFAULT_EXCLUDED_FILES = {
    ".gitignore",
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def should_include(path: Path, include_tests: bool) -> bool:
    relative = path.relative_to(SKILL_ROOT)
    parts = set(relative.parts)
    if parts & DEFAULT_EXCLUDES:
        return False
    if relative.as_posix() in DEFAULT_EXCLUDED_FILES:
        return False
    if not include_tests and "tests" in parts:
        return False
    if path.suffix.lower() in {".pyc", ".pyo", ".zip", ".skill"}:
        return False
    return True


def build_package(output: Path, include_tests: bool = False, layout: str = "folder") -> Path:
    required = ["SKILL.md", "agents/openai.yaml"]
    for item in required:
        if not (SKILL_ROOT / item).exists():
            raise FileNotFoundError(f"missing required file: {item}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(SKILL_ROOT.rglob("*")):
            if not path.is_file() or not should_include(path, include_tests):
                continue
            relative = path.relative_to(SKILL_ROOT)
            arcname = Path("fact-check") / relative if layout == "folder" else relative
            archive.write(path, arcname.as_posix())
    return output


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "-o", type=Path, default=SKILL_ROOT / "dist" / "fact-check-codex.zip")
    parser.add_argument("--include-tests", action="store_true")
    parser.add_argument(
        "--layout",
        choices=["folder", "root"],
        default="folder",
        help="Use folder for Codex-style fact-check/ archive root, or root for SKILL.md at zip root.",
    )
    args = parser.parse_args()
    package = build_package(args.output, include_tests=args.include_tests, layout=args.layout)
    print(f"Wrote {package}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
