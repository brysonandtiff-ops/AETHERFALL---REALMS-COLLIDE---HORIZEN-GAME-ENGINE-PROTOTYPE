"""Reject false canon/model promotions and mutated owner-screen records."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("verify_raw_sculpt_intake",ROOT/"tools/verify_raw_sculpt_intake.py")
assert SPEC and SPEC.loader
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)
DATA=json.loads((ROOT/mod.REGISTER_REL).read_text(encoding="utf-8"))

class OwnerSculptSealTests(unittest.TestCase):
    def setUp(self): self.data=copy.deepcopy(DATA)
    def assertRejects(self): self.assertTrue(mod.validate_register(self.data))
    def test_valid_spec_only(self): self.assertEqual(mod.validate_register(self.data),[])
    def test_eight_exact_screens(self): self.assertEqual(set(x["original_upload_name"] for x in self.data["items"]),set(mod.EXPECTED_SHA256))
    def test_missing_screenshot_rejected(self): self.data["items"].pop(); self.assertRejects()
    def test_duplicate_screenshot_rejected(self): self.data["items"][0]=copy.deepcopy(self.data["items"][1]); self.assertRejects()
    def test_wrong_source_sha_rejected(self): self.data["items"][0]["original_bytes_sha256"]="0"*64; self.assertRejects()
    def test_wrong_original_size_rejected(self): self.data["items"][0]["original_bytes"]+=1; self.assertRejects()
    def test_wrong_mime_rejected(self): self.data["items"][0]["detected_media_type"]="image/jpeg"; self.assertRejects()
    def test_wrong_dimensions_rejected(self): self.data["items"][0]["dimensions_pixels"]=[1920,1080]; self.assertRejects()
    def test_path_traversal_rejected(self): self.data["items"][0]["archived_filename"]="../evil.webp"; self.assertRejects()
    def test_canon_override_rejected(self): self.data["items"][0]["canon_replacement"]=True; self.assertRejects()
    def test_fake_godot_rejected(self): self.data["items"][1]["native_blender_or_godot_verified"]=True; self.assertRejects()
    def test_fake_glb_rejected(self): self.data["items"][1]["actual_3d_source_file_verified"]=True; self.assertRejects()
    def test_false_github_binary_rejected(self): self.data["items"][1]["git_binary_status"]="COMMITTED"; self.assertRejects()
    def test_unnamed_hero_misassigned_rejected(self): self.data["items"][2]["character_id"]="CHR_Morrigan"; self.assertRejects()
    def test_razor_humanoid_identity_swap_rejected(self): self.data["items"][4]["character_id"]="CHR_Raven"; self.assertRejects()
    def test_stat_ui_promotion_rejected(self): self.data["reported_external_mesh_statistics"]["status"]="SOURCE_MESH_VERIFIED"; self.assertRejects()
    def test_false_final_model_gate_rejected(self): self.data["production_gate"]["owner_final_model_approval"]=True; self.assertRejects()
    def test_missing_source_files_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            issues=mod.validate_local_screenshot_bytes(self.data,Path(d))
            self.assertEqual(len(issues),8)
    def test_wrong_webp_payload_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,"40174.jpg").write_bytes(b"FAKE-DATA")
            issues=mod.validate_local_screenshot_bytes(self.data,Path(d))
            self.assertTrue(any("not WEBP" in v for v in issues))
            self.assertTrue(any("file hash differs" in v for v in issues))
    def test_readonly_manifest_cli_passes_without_source(self):
        self.assertEqual(mod.main(["--manifest",str(ROOT/mod.REGISTER_REL)]),0)
    def test_cli_missing_files_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(mod.main(["--manifest",str(ROOT/mod.REGISTER_REL),"--source-dir",d]),2)

if __name__=="__main__":unittest.main()