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

    def test_asset_ids_are_unique_and_have_supported_stages(self):
        data = json.loads((ROOT / "art/asset_registry.json").read_text(encoding="utf-8"))
        assets = data["assets"]
        self.assertEqual(len({item["id"] for item in assets}), len(assets))
        stages = {
            "reserved_no_source", "concept_recorded", "blender_source_recorded",
            "runtime_export_recorded", "native_import_reviewed",
        }
        self.assertTrue(all(item["status"] in stages for item in assets))
        # Do not freeze source inventory as 'always empty': future real imports must be possible.
        intake = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_asset_handoffs.py"), "--validate"],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        self.assertEqual(intake.returncode, 0, intake.stdout + intake.stderr)


if __name__ == "__main__":
    unittest.main()
