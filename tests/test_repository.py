"""Source-layout contract tests; no native-engine claims."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScaffoldTests(unittest.TestCase):
    def test_structure_validator(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_structure.py")],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_bootstrap_is_explicitly_not_gameplay(self):
        scene = (ROOT / "game/scenes/bootstrap/main.tscn").read_text(encoding="utf-8")
        self.assertIn('type="Node3D"', scene)
        self.assertIn("no gameplay implemented yet", scene)

    def test_each_character_has_a_registered_blueprint(self):
        data = json.loads((ROOT / "art/asset_registry.json").read_text(encoding="utf-8"))
        for asset in data["assets"]:
            if asset["type"] == "character":
                plan = ROOT / "docs/characters/plans" / (asset["id"] + ".json")
                self.assertTrue(plan.is_file(), asset["id"])
                payload = json.loads(plan.read_text(encoding="utf-8"))
                self.assertEqual(payload["character_id"], asset["id"])
                self.assertEqual(payload["registry_concept_status"], asset["concept_status"])

    def test_asset_ids_are_unique_and_unfinished(self):
        data = json.loads((ROOT / "art/asset_registry.json").read_text(encoding="utf-8"))
        assets = data["assets"]
        self.assertEqual(len({item["id"] for item in assets}), len(assets))
        self.assertTrue(all(item["status"] == "reserved_no_source" for item in assets))


if __name__ == "__main__":
    unittest.main()
