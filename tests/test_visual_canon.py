"""Visual canon SHA/identity and proposed-image fail-closed tests. No engine claims."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("visual_canon_guard", ROOT / "tools/verify_visual_canon.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class VisualCanonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="aetherfall-visual-")
        self.root = Path(self.tmp.name)
        paths = [
            "docs/characters/CANON_LOCKS.json",
            "docs/characters/plans/CHR_Vellaris_Bloodshield.json",
            "docs/characters/plans/CHR_ThornDell.json",
            "art/asset_registry.json",
        ]
        for rel in paths:
            dst = self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dst)
        for cid in guard.PINNED:
            (self.root / "art/concepts/characters" / cid).mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def change(self, relative, modify):
        path = self.root / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        modify(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def rejected(self, needle):
        issues = guard.check(self.root)
        self.assertTrue(any(needle in problem for problem in issues), issues)

    def test_valid_missing_source_stays_pending_not_approved(self):
        self.assertEqual(guard.check(self.root), [])

    def test_original_webp_filename_and_format_are_pinned(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Vellaris_Bloodshield"]["source"].update(path="art/concepts/characters/CHR_Vellaris_Bloodshield/fake.png"))
        self.rejected("Approved reference identity/hash drift")

    def test_swapped_image_digest_is_rejected(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Vellaris_Bloodshield"]["source"].update(sha256="a"*64))
        self.rejected("Approved reference identity/hash drift")

    def test_canonical_source_false_claim_is_rejected(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Vellaris_Bloodshield"]["source"].update(state="source_verified"))
        self.rejected("Character source promoted without original image bytes")

    def test_changed_hero_face_anchor_is_rejected(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Vellaris_Bloodshield"].update(visual_lock=["Generic silver-haired mage"]))
        self.rejected("Approved character missing visual anchor")

    def test_changed_thorndell_weapon_is_rejected(self):
        self.change("docs/characters/plans/CHR_ThornDell.json",
                    lambda d: d["design"].update(signature_prop="Generic iron hammer"))
        self.rejected("Approved character design/prop changed in plan")

    def test_changed_vellaris_ability_is_rejected(self):
        self.change("docs/characters/plans/CHR_Vellaris_Bloodshield.json",
                    lambda d: d["design"]["active_abilities"][0].update(name="New random spell"))
        self.rejected("Approved character active kit drift")

    def test_infographic_hierarchy_cannot_be_dropped(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["presentation_standard"]["required_panel_order"].pop())
        self.rejected("Vellaris infographic panel hierarchy drift")

    def test_unregistered_art_in_canonical_directory_fails(self):
        (self.root / "art/concepts/characters/CHR_Vellaris_Bloodshield/random_replacement.png").write_bytes(b"image bytes")
        self.rejected("Unregistered art in approved character master folder")

    def test_untracked_proposal_fails(self):
        proposed = self.root / "art/concepts/characters/CHR_Vellaris_Bloodshield/proposals/v02.webp"
        proposed.parent.mkdir()
        proposed.write_bytes(b"not canonical")
        self.rejected("Untracked character art proposal")

    def test_reviewed_proposal_still_cannot_self_promote(self):
        proposed = self.root / "art/concepts/characters/CHR_Vellaris_Bloodshield/proposals/v02.webp"
        proposed.parent.mkdir()
        proposed.write_bytes(b"not canonical")
        review = {
            "character_id": "CHR_Vellaris_Bloodshield",
            "status": "PROPOSAL_PENDING_OWNER_REVIEW",
            "canonical_source_sha256": guard.PINNED["CHR_Vellaris_Bloodshield"]["sha256"],
            "candidate_sha256": __import__("hashlib").sha256(proposed.read_bytes()).hexdigest(),
            "source_note": "Test candidate, not approved",
            "is_canonical": True
        }
        proposed.with_name(proposed.name + ".review.json").write_text(json.dumps(review))
        self.rejected("Proposal cannot self-promote")

    def test_valid_unapproved_proposal_can_be_kept_for_review(self):
        proposed = self.root / "art/concepts/characters/CHR_Vellaris_Bloodshield/proposals/v02.webp"
        proposed.parent.mkdir()
        proposed.write_bytes(b"example unapproved candidate data")
        review = {
            "character_id": "CHR_Vellaris_Bloodshield",
            "status": "PROPOSAL_PENDING_OWNER_REVIEW",
            "canonical_source_sha256": guard.PINNED["CHR_Vellaris_Bloodshield"]["sha256"],
            "candidate_sha256": __import__("hashlib").sha256(proposed.read_bytes()).hexdigest(),
            "source_note": "Test candidate only"
        }
        proposed.with_name(proposed.name + ".review.json").write_text(json.dumps(review))
        self.assertEqual(guard.check(self.root), [])

    def test_webp_bytes_mislabelled_as_png_fail_canon_byte_checks(self):
        target = self.root / guard.PINNED["CHR_ThornDell"]["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"RIFF" + b"bad" + b"WEBP" + b"x"*40)
        self.rejected("Approved image signature/size drift")
        self.rejected("Approved image checksum drift")

    def test_unresolved_corvex_korvex_duplicate_fails(self):
        def mutate(d):
            d["assets"].append({**d["assets"][0], "id": "CHR_Corvex"})
        self.change("art/asset_registry.json", mutate)
        self.rejected("Unresolved Corvex/Korvex alias collision")


if __name__ == "__main__":
    unittest.main()
