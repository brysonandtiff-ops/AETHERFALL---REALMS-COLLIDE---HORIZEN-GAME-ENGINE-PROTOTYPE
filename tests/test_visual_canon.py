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
            "docs/characters/plans/CHR_Dreadhull.json",
            "docs/characters/plans/CHR_KRAIT.json",
            "docs/characters/plans/CHR_Korvex.json",
            "art/asset_registry.json",
        ]
        for rel in paths:
            dst = self.root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dst)
        manifest = json.loads((ROOT / "docs/characters/CANON_LOCKS.json").read_text(encoding="utf-8"))
        for cid, lock in manifest["locked_characters"].items():
            (self.root / "art/concepts/characters" / cid).mkdir(parents=True, exist_ok=True)
            relative = Path(lock["source"]["path"])
            original = ROOT / relative
            if original.is_file():
                target = self.root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original, target)

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

    def test_current_source_archive_states_are_valid(self):
        self.assertEqual(guard.check(self.root), [])


    def test_new_owner_approved_character_requires_own_canon_lock(self):
        def approve(d):
            template = {**d["assets"][0]}
            template["id"] = "CHR_Razor"
            template["concept_status"] = "aetherfall_approved"
            template["concept_dir"] = "art/concepts/characters/CHR_Razor"
            template["source_dir"] = "art/blender/characters/CHR_Razor"
            template["runtime_dir"] = "game/assets/characters/heroes/CHR_Razor"
            d["assets"].append(template)
        self.change("art/asset_registry.json", approve)
        self.rejected("Approved character missing visual lock")

    def test_extra_lock_cannot_approve_unregistered_hero(self):
        def add(d):
            d["locked_characters"]["CHR_Unregistered"] = d["locked_characters"]["CHR_Vellaris_Bloodshield"]
        self.change("docs/characters/CANON_LOCKS.json", add)
        self.rejected("Unregistered/unapproved extra visual lock")

    def test_original_webp_filename_and_format_are_pinned(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Vellaris_Bloodshield"]["source"].update(path="art/concepts/characters/CHR_Vellaris_Bloodshield/fake.png"))
        self.rejected("Approved reference identity/hash drift")

    def test_swapped_image_digest_is_rejected(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Vellaris_Bloodshield"]["source"].update(sha256="a"*64))
        self.rejected("Approved reference identity/hash drift")

    def test_canonical_source_false_claim_is_rejected(self):
        # Isolate the missing-source case even after a genuine archive is added.
        (self.root / guard.PINNED["CHR_Vellaris_Bloodshield"]["path"]).unlink(missing_ok=True)
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

    def test_dreadhull_reference_is_immutable(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Dreadhull"]["source"].update(sha256="a"*64))
        self.rejected("Approved reference identity/hash drift: CHR_Dreadhull")

    def test_dreadhull_dredge_cannot_be_replaced(self):
        self.change("docs/characters/plans/CHR_Dreadhull.json",
                    lambda d: d["design"].update(signature_prop="Anchor-scythe"))
        self.rejected("Approved character design/prop changed in plan: CHR_Dreadhull")

    def test_dreadhull_kit_cannot_be_replaced(self):
        self.change("docs/characters/plans/CHR_Dreadhull.json",
                    lambda d: d["design"]["active_abilities"][0].update(name="Tide Chain"))
        self.rejected("Approved character active kit drift: CHR_Dreadhull")

    def test_dreadhull_approval_cannot_be_downgraded(self):
        self.change("art/asset_registry.json", lambda d: next(a for a in d["assets"]
                    if a["id"] == "CHR_Dreadhull").update(concept_status="legacy_owner_approved_candidate_for_aetherfall"))
        self.rejected("Pinned owner-approved character registry status removed: CHR_Dreadhull")

    def test_dreadhull_weapon_keyword_cannot_hide_replacement(self):
        self.change("docs/characters/plans/CHR_Dreadhull.json",
                    lambda d: d["design"].update(signature_prop="Ossuary Dredge converted into an anchor-scythe"))
        self.rejected("Dreadhull approved design contract drift")

    def test_dreadhull_ability_mechanics_cannot_be_replaced_under_same_name(self):
        self.change("docs/characters/plans/CHR_Dreadhull.json",
                    lambda d: d["design"]["active_abilities"][0].update(summary="An unrelated spell"))
        self.rejected("Dreadhull approved design contract drift")

    def test_dreadhull_passive_mechanics_are_pinned(self):
        self.change("docs/characters/plans/CHR_Dreadhull.json",
                    lambda d: d["design"]["passive"].update(summary="Infinite damage immunity"))
        self.rejected("Dreadhull approved design contract drift")

    def test_dreadhull_visual_traits_cannot_be_silently_extended(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Dreadhull"]["visual_lock"].append("Replace wreck frame with full galleon"))
        self.rejected("Dreadhull approved design contract drift")

    def test_dreadhull_visual_identity_cannot_be_rewritten(self):
        self.change("docs/characters/plans/CHR_Dreadhull.json",
                    lambda d: d["design"].update(visual_identity="Octopus captain with keel oar"))
        self.rejected("Dreadhull approved design contract drift")

    def test_dreadhull_mime_cannot_be_changed(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Dreadhull"]["source"].update(media_type="image/png"))
        self.rejected("Dreadhull original source provenance drift")

    def test_krait_master_fingerprint_cannot_drift(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_KRAIT"]["source"].update(sha256="a"*64))
        self.rejected("Approved reference identity/hash drift: CHR_KRAIT")

    def test_krait_visual_contract_cannot_drift(self):
        self.change("docs/characters/plans/CHR_KRAIT.json",
                    lambda d: d["design"].update(signature_prop="Replacement sword"))
        self.rejected("K.R.A.I.T approved visual contract drift")

    def test_krait_replacement_record_cannot_be_removed(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["character_replacements"].pop("CHR_Bryskar"))
        self.rejected("K.R.A.I.T owner replacement decision drift")

    def test_bryskar_cannot_return_as_active_hero(self):
        def add(d):
            d["assets"].append({**d["assets"][0], "id": "CHR_Bryskar"})
        self.change("art/asset_registry.json", add)
        self.rejected("Superseded Bryskar cannot be registered")

    def test_krait_unreadable_kit_cannot_be_promoted(self):
        self.change("docs/characters/plans/CHR_KRAIT.json",
                    lambda d: d["design"].update(kit_status="owner_locked"))
        self.rejected("K.R.A.I.T unapproved gameplay kit promotion")

    def test_krait_missing_master_cannot_be_marked_archived(self):
        (self.root / guard.PINNED["CHR_KRAIT"]["path"]).unlink(missing_ok=True)
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_KRAIT"]["source"].update(state="source_verified"))
        self.rejected("Character source promoted without original image bytes: CHR_KRAIT")

    def test_korvex_exact_master_cannot_drift(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Korvex"]["source"].update(sha256="a"*64))
        self.rejected("Approved reference identity/hash drift: CHR_Korvex")

    def test_korvex_maul_cannot_be_replaced(self):
        self.change("docs/characters/plans/CHR_Korvex.json",
                    lambda d: d["design"].update(signature_prop="Grave Maul renamed shield"))
        self.rejected("Korvex approved design contract drift")

    def test_korvex_kit_mechanics_cannot_drift(self):
        self.change("docs/characters/plans/CHR_Korvex.json",
                    lambda d: d["design"]["active_abilities"][0].update(summary="Unrelated attack"))
        self.rejected("Korvex approved design contract drift")

    def test_korvex_visual_traits_cannot_be_changed(self):
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Korvex"]["visual_lock"].append("Replace with pirate"))
        self.rejected("Korvex approved design contract drift")

    def test_korvex_archive_cannot_be_forged(self):
        (self.root / guard.PINNED["CHR_Korvex"]["path"]).unlink(missing_ok=True)
        self.change("docs/characters/CANON_LOCKS.json",
                    lambda d: d["locked_characters"]["CHR_Korvex"]["source"].update(state="source_verified"))
        self.rejected("Character source promoted without original image bytes: CHR_Korvex")

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
