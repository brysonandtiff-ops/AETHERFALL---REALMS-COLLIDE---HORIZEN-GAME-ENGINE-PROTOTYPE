"""Adversarial and legitimate specification checks. No native render/gameplay claim."""
from __future__ import annotations
import importlib.util
import json
import hashlib
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('handoff_validator',ROOT/'tools/verify_production_contract.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
HERO=json.loads((ROOT/'docs/pipeline/examples/CHR_Vellaris_Bloodshield_SPEC_ONLY.json').read_text())
ABILITY=json.loads((ROOT/'docs/pipeline/contracts/ABILITY_CONTRACT_EXAMPLE.json').read_text())

class ContractTests(unittest.TestCase):
    def test_spec_passes_structurally_only(self):self.assertEqual([],mod.validate_hero(deepcopy(HERO)))
    def test_ability_passes_as_not_implemented_fixture(self):self.assertEqual([],mod.validate_ability(deepcopy(ABILITY)))
    def test_rejects_visual_canonless_name(self):
        x=deepcopy(HERO);x['hero_id']='CHR_../leak';self.assertTrue(mod.validate_hero(x))
    def test_rejects_traversal(self):
        x=deepcopy(HERO);x['concept']['source_path']='art/../../secrets';self.assertTrue(mod.validate_hero(x))
    def test_rejects_unverified_promotion(self):
        x=deepcopy(HERO);x['approval_state']='GAME_READY';self.assertTrue(mod.validate_hero(x))
    def test_rejects_fake_blender_evidence(self):
        x=deepcopy(HERO);x['evidence']['native_blender_0_90_180_270']='PASS';self.assertTrue(mod.validate_hero(x))
    def test_rejects_1p_reusing_3p(self):
        x=deepcopy(HERO);x['blender']['one_p']['asset_id']=x['hero_id'];self.assertTrue(mod.validate_hero(x))
    def test_rejects_doubled_sockets(self):
        x=deepcopy(HERO);x['blender']['sockets'].append('SOCK_Ground');self.assertTrue(mod.validate_hero(x))
    def test_rejects_bad_orientation(self):
        x=deepcopy(HERO);x['blender']['forward_axis']='+Y';self.assertTrue(mod.validate_hero(x))
    def test_rejects_vfx_as_collision(self):
        x=deepcopy(HERO);x['gameplay']['collision_uses_vfx']=True;self.assertTrue(mod.validate_hero(x))
    def test_ability_rejects_client_damage_auth(self):
        x=deepcopy(ABILITY);x['hit_volume']['owner']='CLIENT';self.assertTrue(mod.validate_ability(x))
    def test_ability_rejects_zero_active(self):
        x=deepcopy(ABILITY);x['phases_ticks']['active']=0;self.assertTrue(mod.validate_ability(x))
    def test_ability_rejects_missing_telegraph_caption(self):
        x=deepcopy(ABILITY);x['telegraph']['caption_cue']='';self.assertTrue(mod.validate_ability(x))
    def test_ability_rejects_double_commit_allowed(self):
        x=deepcopy(ABILITY);x['anti_replay']['double_commit_rejected']=False;self.assertTrue(mod.validate_ability(x))
    def test_path_refuses_windows_drive_absolute_and_symlink_style(self):
        for p in ['../evil','C:/temp/data','/etc/passwd','a//b','a/./b','a\\b']:
            self.assertFalse(mod.safe_rel(p))
    def test_rig_proof_cannot_be_faked_in_spec(self):
        x=deepcopy(HERO); x['blender']['rig']['deformation_test_verified']=True; self.assertTrue(mod.validate_hero(x))
    def test_bad_lod_fraction_type_is_rejected_not_crash(self):
        x=deepcopy(HERO); x['blender']['three_p']['lod1_fraction_max']='not-a-number'; self.assertTrue(mod.validate_hero(x))
    def test_missing_locomotion_states_rejected(self):
        x=deepcopy(HERO); x['gameplay']['locomotion_states']=['Idle'];self.assertTrue(mod.validate_hero(x))
    def test_spec_only_rejects_false_signed_receipt(self):
        x=deepcopy(HERO);x['evidence']['independent_signed_law108']='SIGNED';self.assertTrue(mod.validate_hero(x))
    def test_integrity_happy_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'a.txt';p.write_text('asset')
            man={'project':mod.PROJECT,'source_commit_sha':'a'*40,'stage':'INTEGRITY_ONLY_NOT_NATIVE_PROOF','files':[{'path':'a.txt','sha256':hashlib.sha256(b'asset').hexdigest(),'bytes':5}]}
            self.assertEqual([],mod.verify_files(root,man))
    def test_integrity_detects_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'a.txt';p.write_text('asset')
            man={'project':mod.PROJECT,'source_commit_sha':'a'*40,'stage':'INTEGRITY_ONLY_NOT_NATIVE_PROOF','files':[{'path':'a.txt','sha256':'0'*64,'bytes':5}]}
            self.assertTrue(mod.verify_files(root,man))
    def test_integrity_detects_case_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'a.txt').write_text('a');(root/'A.txt').write_text('b')
            man={'project':mod.PROJECT,'source_commit_sha':'a'*40,'stage':'INTEGRITY_ONLY_NOT_NATIVE_PROOF','files':[{'path':n,'sha256':hashlib.sha256((root/n).read_bytes()).hexdigest(),'bytes':1} for n in ('a.txt','A.txt')]}
            self.assertTrue(mod.verify_files(root,man))
    def test_release_gate_always_needs_external_proof(self):
        self.assertEqual(2,mod.main(['--hero',str(ROOT/'docs/pipeline/examples/CHR_Vellaris_Bloodshield_SPEC_ONLY.json'),'--demand-native']))

if __name__=='__main__':unittest.main()