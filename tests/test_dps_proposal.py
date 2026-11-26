"""Razor/Raven DPS proposal-only repository consistency checks.

These do not assert native Blender/Godot execution or imply that binary assets are checked in.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class DpsProposalTests(unittest.TestCase):
    def test_new_ids_are_distinct_and_not_promoted(self):
        assets = {item["id"]: item for item in json.loads(
            (ROOT/"art/asset_registry.json").read_text(encoding="utf-8"))["assets"]}
        expectation = {
          "CHR_Razor": ("character", "melee_dps_flanker"),
          "CHR_Raven": ("character", "ranged_dps_precision_marksman"),
          "WPN_Razor_RiftTalons": ("weapon", "dual_wrist_blades"),
          "WPN_Raven_Nightpiercer": ("weapon", "precision_long_range_rifle"),
        }
        for key,(typ,role) in expectation.items():
            with self.subTest(asset=key):
                self.assertIn(key, assets)
                self.assertEqual(assets[key]["type"],typ)
                self.assertEqual(assets[key]["role"],role)
                self.assertEqual(assets[key]["status"],"reserved_no_source")
                self.assertEqual(assets[key]["concept_status"],"aetherfall_design_brief")
                for k in ("concept_dir","source_dir","runtime_dir"):
                    self.assertTrue((ROOT/assets[key][k]).is_dir())

    def test_review_brief_remains_truthful(self):
        doc=(ROOT/"docs/characters/DPS_RAZOR_RAVEN_V01.md").read_text(encoding="utf-8").lower()
        for word in ("not locked canon","not verified","no shields","vtk","glb"):
            self.assertIn(word,doc)
        for name in ("CHR_Razor","CHR_Raven"):
            self.assertFalse((ROOT/f"game/assets/characters/heroes/{name}/{name}_blockout_v01.glb").exists())

if __name__ == "__main__":
    unittest.main()
