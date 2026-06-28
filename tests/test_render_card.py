from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts" / "render_card.py"
VALIDATOR = ROOT / "scripts" / "validate_result.py"
FIXTURES = ROOT / "tests" / "fixtures"


class RenderCardTests(unittest.TestCase):
    def render_fixture(self, name: str) -> str:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "card.html"
            subprocess.run(
                [sys.executable, str(RENDERER), str(FIXTURES / name), "--output", str(output)],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            return output.read_text(encoding="utf-8")

    def test_standard_health_card_renders_mfs_and_sources(self) -> None:
        html = self.render_fixture("standard_health.json")
        self.assertIn("Fact-Check Card", html)
        self.assertIn("MFS Score", html)
        self.assertIn("badge-misleading", html)
        self.assertIn("WHO vaccine safety guidance", html)
        self.assertIn("Evidence Ledger", html)

    def test_comparison_card_validates(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(FIXTURES / "comparison_energy.json")],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertIn("OK:", result.stdout)
        self.assertIn("MFS", result.stdout)

    def test_prebunking_card_omits_mfs(self) -> None:
        html = self.render_fixture("prebunking_elections.json")
        self.assertIn("Prebunking Briefing", html)
        self.assertIn("Active Narratives", html)
        self.assertNotIn("MFS Score", html)

    def test_validator_rejects_unknown_source_reference(self) -> None:
        fixture = json.loads((FIXTURES / "standard_health.json").read_text(encoding="utf-8"))
        fixture["claims"][0]["source_ids"] = ["MISSING"]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown source id", result.stderr)


if __name__ == "__main__":
    unittest.main()
