"""Adversarial source-only tests for the AETHERFALL no-drift submission gate."""

import copy
import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path

from tools.verify_art_style_contract import LOCK_ID, PANELS, REFERENCE_PINS, check

SOURCE_ROOT = Path(__file__).resolve().parents[1]


def _fake_png(width, height):
    # PNG header/IHDR payload only; test fixture for parser, not art or proof.
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x08\x06\x00\x00\x00" + b"fixture"


class ArtStyleContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = json.loads((SOURCE_ROOT / "docs/art/ART_STYLE_LOCK.json").read_text())
        self.style_path = self.root / "docs/art/ART_STYLE_LOCK.json"
        self.style_path.parent.mkdir(parents=True)
        self.canon_path = self.root / "docs/characters/CANON_LOCKS.json"
        self.canon_path.parent.mkdir(parents=True)
        self.canon = {
            "presentation_standard": {
                "required_panel_order": list(PANELS),
                "master_ratio": "4:3", "reference_size": [1536, 1152]
            },
            "locked_characters": {
                "CHR_Vellaris_Bloodshield": {"source": {"sha256": REFERENCE_PINS["vellaris_infographic"][5]}}
            }
        }
        self.save()

    def save(self):
        self.style_path.write_text(json.dumps(self.manifest))
        self.canon_path.write_text(json.dumps(self.canon))

    def expect_fail(self, token):
        errors = check(self.root)
        self.assertTrue(any(token in e for e in errors), errors)

    def make_proposal(self, name="sample.png", mode="FULL_CHARACTER_INFOGRAPHIC", dims=(1536, 1152)):
        path = self.root / "art/concepts/characters/CHR_Korvex/proposals" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_fake_png(*dims))
        sidecar = path.with_name(path.name + ".review.json")
        meta = {
            "character_id": "CHR_Korvex",
            "status": "PROPOSAL_PENDING_OWNER_REVIEW",
            "canonical_source_sha256": None,
            "candidate_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_note": "source was supplied for character review",
            "style_lock_id": LOCK_ID,
            "style_reference_sha256": {k: REFERENCE_PINS[k][5] for k in ("vellaris_infographic", "korvex_infographic")},
            "branding": "AETHERFALL: REALMS COLLIDE",
            "presentation_mode": mode,
            "review_state": "PENDING_OWNER_VISUAL_COMPARISON",
            "panel_attestation": list(PANELS) if mode == "FULL_CHARACTER_INFOGRAPHIC" else [],
            "not_a_full_sheet": mode != "FULL_CHARACTER_INFOGRAPHIC",
            "reference_attestation": "Saw both exact style references with separate character source",
            "render_origin": "AI_GENERATED_CONCEPT_ONLY",
        }
        sidecar.write_text(json.dumps(meta))
        return path, sidecar, meta

    def test_lock_passes_when_intact(self):
        self.assertEqual([], check(self.root))

    def test_vellaris_hash_swapped_fails(self):
        self.manifest["references"]["vellaris_infographic"]["sha256"] = "0" * 64
        self.save()
        self.expect_fail("reference identity/hash drift")

    def test_korvex_hash_swapped_fails(self):
        self.manifest["references"]["korvex_infographic"]["sha256"] = "0" * 64
        self.save()
        self.expect_fail("reference identity/hash drift")

    def test_roster_is_not_a_canon_master(self):
        self.manifest["references"]["legacy_roster_capture"]["use"] = "FULL_ART_CANON"
        self.save()
        self.expect_fail("reference identity/hash drift")

    def test_brand_cannot_be_nexusfall(self):
        self.manifest["brand"]["logo_text"] = "NEXUSFALL"
        self.save()
        self.expect_fail("Wrong project branding")

    def test_required_sheet_panels_cannot_be_removed(self):
        self.manifest["full_infographic"]["panel_order"].pop()
        self.save()
        self.expect_fail("infographic hierarchy")

    def test_key_art_cannot_replace_sheet(self):
        self.manifest["hero_key_art"]["cannot_replace_full_sheet"] = False
        self.save()
        self.expect_fail("Poster substituted")

    def test_canon_layout_drift_fails(self):
        self.canon["presentation_standard"]["required_panel_order"].reverse()
        self.save()
        self.expect_fail("Existing character canon contradicts")

    def test_valid_full_sheet_attestation_passes(self):
        self.make_proposal()
        self.assertEqual([], check(self.root))

    def test_wrong_character_hash_fails(self):
        _, sidecar, data = self.make_proposal()
        data["candidate_sha256"] = "f" * 64
        sidecar.write_text(json.dumps(data))
        self.expect_fail("checksum mismatch")

    def test_missing_proposal_sidecar_fails(self):
        _, sidecar, _ = self.make_proposal()
        sidecar.unlink()
        self.expect_fail("lacks .review.json")

    def test_missing_style_reference_attestation_fails(self):
        _, sidecar, data = self.make_proposal()
        data["style_reference_sha256"].pop("korvex_infographic")
        sidecar.write_text(json.dumps(data))
        self.expect_fail("references wrong infographic")

    def test_unapproved_promotion_fails(self):
        _, sidecar, data = self.make_proposal()
        data["status"] = "OWNER_APPROVED"
        sidecar.write_text(json.dumps(data))
        self.expect_fail("unapproved canon promotion")

    def test_false_native_engine_proof_fails(self):
        _, sidecar, data = self.make_proposal()
        data["render_origin"] = "GODOT_NATIVE_CAPTURE"
        sidecar.write_text(json.dumps(data))
        self.expect_fail("Native engine proof")

    def test_portrait_cannot_claim_full_infographic(self):
        _, sidecar, data = self.make_proposal(mode="BLACK_BACKGROUND_HERO_KEY_ART")
        data["not_a_full_sheet"] = False
        sidecar.write_text(json.dumps(data))
        self.expect_fail("Portrait was not separated")

    def test_bad_infographic_dimensions_fails(self):
        self.make_proposal(dims=(1024, 1024))
        self.expect_fail("not 4:3")

    def test_cannot_drop_required_panel_in_sidecar(self):
        _, sidecar, data = self.make_proposal()
        data["panel_attestation"].remove("silhouette_explorations_top_right")
        sidecar.write_text(json.dumps(data))
        self.expect_fail("lacks canonical 11-panel")

    def test_new_master_image_outside_proposals_fails(self):
        path = self.root / "art/concepts/characters/CHR_Korvex/new_unreviewed.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_fake_png(1536, 1152))
        self.expect_fail("Unreviewed hero image outside proposals")


if __name__ == "__main__":
    unittest.main()