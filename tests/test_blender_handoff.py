"""Negative/positive STATIC integrity tests; no test below certifies actual engine art."""
import base64
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import validate_blender_handoff as gate

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9s6R9L4AAAAASUVORK5CYII=')
MP4_STUB = b'\x00\x00\x00\x18ftypisom\x00\x00\x00\x00isomiso2'
BLEND_STUB = b'BLENDER-v410' + b'\x00' * 30
SHA = '1' * 40


def glb(payload=b'{}'):
    # Syntactically consistent GLB header, intentionally NOT a game-ready asset.
    content = payload + b' ' * ((-len(payload)) % 4)
    return b'glTF' + struct.pack('<II', 2, 20 + len(content)) + struct.pack('<I', len(content)) + b'JSON' + content


class BlenderHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.asset = 'CHR_TestHero'
        self.folder = self.root / 'art/blender/characters' / self.asset
        self.folder.mkdir(parents=True)
        self.registry = {
            'project': gate.PROJECT,
            'assets': [{'id': self.asset, 'type': 'character', 'concept_status': 'aetherfall_approved',
                        'source_dir': f'art/blender/characters/{self.asset}',
                        'concept_dir': f'art/concepts/characters/{self.asset}',
                        'runtime_dir': f'game/assets/characters/heroes/{self.asset}',
                        'status': 'reserved_no_source'}],
        }
        self.plan = {
            'project': gate.PROJECT, 'character_id': self.asset,
            'concept_reference': {'repo_path': f'art/concepts/characters/{self.asset}/source.png',
                                  'archive_status': 'pending_source_upload', 'sha256': None},
            'gates': {key: False for key in gate.CHARACTER_GATES},
        }
        self.locks = {'locked_characters': {}}
        self.doc = {
            'schema_version': 1, 'project': gate.PROJECT, 'asset_id': self.asset,
            'source_commit': None, 'production_status': 'NOT_VERIFIED',
            'provenance': {}, 'blender': {}, 'mesh': {}, 'textures': {}, 'export': {},
            'owner_signoff': {},
            'stages': {stage: {'status': 'NOT_RUN', 'evidence_path': None,
                               'evidence_sha256': None, 'capture_source': None,
                               'tool_version': None, 'source_commit': None}
                       for stage in gate.STAGE_NAMES},
        }
        self.save()

    def file(self, path, content):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return p.relative_to(self.root).as_posix(), hashlib.sha256(content).hexdigest()

    def save(self):
        self.file('art/asset_registry.json', json.dumps(self.registry).encode())
        self.file(f'docs/characters/plans/{self.asset}.json', json.dumps(self.plan).encode())
        self.file('docs/characters/CANON_LOCKS.json', json.dumps(self.locks).encode())
        self.file(f'art/blender/characters/{self.asset}/handoff.json', json.dumps(self.doc).encode())

    def issues(self):
        self.save()
        return gate.check(self.root)

    def assert_blocked(self, fragment):
        issues = self.issues()
        self.assertTrue(any(fragment in issue for issue in issues), issues)

    def source(self):
        ref_path, ref_sha = self.file(f'art/concepts/characters/{self.asset}/source.png', PNG)
        self.doc['provenance'].update(source_reference_path=ref_path, source_reference_sha256=ref_sha,
                                      rights_cleared=True, owner_visual_reference_approved=True)
        self.plan['concept_reference'].update(repo_path=ref_path, sha256=ref_sha, archive_status='source_verified')
        self.locks['locked_characters'][self.asset] = {'source': {'path': ref_path, 'sha256': ref_sha}}

    def complete(self):
        self.source()
        for key in gate.CHARACTER_GATES:
            self.plan['gates'][key] = True
        raw, rawhash = self.file(f'art/blender/characters/{self.asset}/raw/original.glb', glb(b'{"asset":{"version":"2.0"}}'))
        model, modelhash = self.file(f'art/blender/characters/{self.asset}/Hero.blend', BLEND_STUB)
        self.doc['provenance'].update(raw_sculpt_path=raw, raw_sculpt_sha256=rawhash)
        self.doc['blender'].update(source_blend_path=model, source_blend_sha256=modelhash)
        self.doc['mesh'].update(third_person_triangle_count=60000, first_person_triangle_count=28000,
                                lod1_triangle_count=30000, lod2_triangle_count=10000,
                                weight_paint_reviewed=True, armature_name='Hero_Rig')
        self.doc['textures'].update(uv_nonoverlap_verified=True, all_maps_saved=True)
        third, thirdhash = self.file(f'game/assets/characters/heroes/{self.asset}/hero_3p.glb', glb(b'{"asset":{"version":"2.0"},"scene":0}'))
        first, firsthash = self.file(f'game/assets/characters/heroes/{self.asset}/hero_1p.glb', glb(b'{"asset":{"version":"2.0"},"scene":1}'))
        self.doc['export'].update(third_person_glb_path=third, third_person_glb_sha256=thirdhash,
                                  first_person_glb_path=first, first_person_glb_sha256=firsthash,
                                  animation_clips=['Idle', 'Run'], sockets=['Hand_R_Weapon'], godot_version='4.7.2')
        self.doc['source_commit'] = SHA
        for stage in gate.STAGE_NAMES:
            kind = gate.STAGE_CAPTURE[stage]
            if stage == 'owner_review':
                name, content = stage + '.md', b'FICTIONAL review fixture (NOT owner approval)'
            elif stage == 'camera_animation_gameplay':
                name, content = stage + '.mp4', MP4_STUB
            else:
                name, content = stage + '.png', PNG
            location, digest = self.file(f'evidence/characters/{self.asset}/{name}', content)
            self.doc['stages'][stage].update(status='PASS', evidence_path=location, evidence_sha256=digest,
                                             source_commit=SHA, capture_source=kind, tool_version='fixture-1.0')
        self.doc['owner_signoff'].update(approved=True, reviewer='FICTIONAL_TEST_REVIEWER',
                                         review_evidence_path=self.doc['stages']['owner_review']['evidence_path'],
                                         review_evidence_sha256=self.doc['stages']['owner_review']['evidence_sha256'])
        self.doc['production_status'] = 'GAME_READY'

    def test_no_manifests_does_not_assert_model(self):
        (self.folder / 'handoff.json').unlink()
        self.assertEqual(gate.check(self.root), [])

    def test_unverified_registered_manifest_allowed(self):
        self.assertEqual(self.issues(), [])

    def test_honestly_formatted_synthetic_game_ready_static_pass(self):
        self.complete()
        self.assertEqual(self.issues(), [])  # Fake binary headers are not a real 3D runtime.

    def test_unregistered_hero_rejected(self):
        self.registry['assets'] = []
        self.assert_blocked('not linked to registered')

    def test_missing_plan_rejected(self):
        self.plan['character_id'] = 'CHR_Other'
        self.assert_blocked('not linked to registered')

    def test_nonapproved_legacy_char_cannot_promote(self):
        self.complete()
        self.registry['assets'][0]['concept_status'] = 'legacy_owner_approved_candidate_for_aetherfall'
        self.assert_blocked('approved archived character plan')

    def test_missing_approval_gate_blocks_promotion(self):
        self.complete()
        self.plan['gates']['model_verified'] = False
        self.assert_blocked('production gates incomplete')

    def test_unarchived_source_blocks_promotion(self):
        self.complete()
        self.plan['concept_reference']['archive_status'] = 'pending_source_upload'
        self.assert_blocked('approved archived character plan')

    def test_stage_order_rejected(self):
        self.doc['source_commit'] = SHA
        stage = self.doc['stages']['godot_native_import']
        stage['status'] = 'PASS'
        self.assert_blocked('stage out of order')

    def test_stage_no_evidence_rejected(self):
        self.source()
        self.doc['source_commit'] = SHA
        self.doc['stages']['reference_lock']['status'] = 'PASS'
        self.assert_blocked('Unverified Blender stage PASS')

    def test_stage_tool_type_mismatch(self):
        self.complete()
        self.doc['stages']['godot_native_import']['capture_source'] = 'BLENDER_NATIVE'
        self.assert_blocked('Unverified Blender stage PASS')

    def test_stage_source_commit_mismatch(self):
        self.complete()
        self.doc['stages']['retopo_3p_1p_lods']['source_commit'] = 'f' * 40
        self.assert_blocked('Unverified Blender stage PASS')

    def test_stage_binary_disguised_as_png_rejected(self):
        self.complete()
        stage = self.doc['stages']['blender_native_review']
        location, digest = self.file(stage['evidence_path'], b'just a text file named .png')
        stage['evidence_sha256'] = digest
        self.assert_blocked('Unverified Blender stage PASS')

    def test_gameplay_requires_video(self):
        self.complete()
        stage = self.doc['stages']['camera_animation_gameplay']
        location, digest = self.file(f'evidence/characters/{self.asset}/renamed.png', PNG)
        stage.update(evidence_path=location, evidence_sha256=digest)
        self.assert_blocked('Unverified Blender stage PASS')

    def test_other_heros_evidence_rejected(self):
        self.complete()
        stage = self.doc['stages']['blender_native_review']
        location, digest = self.file('evidence/characters/CHR_SomeoneElse/screenshot.png', PNG)
        stage.update(evidence_path=location, evidence_sha256=digest)
        self.assert_blocked('Unverified Blender stage PASS')

    def test_stage_path_traversal_rejected(self):
        self.complete()
        self.doc['stages']['godot_native_import']['evidence_path'] = 'evidence/characters/../other.png'
        self.assert_blocked('Unverified Blender stage PASS')

    def test_symlinked_parent_asset_rejected(self):
        self.complete()
        image = self.root / f'evidence/characters/{self.asset}/blender_native_review.png'
        image.unlink()
        target = self.root / 'outside.png'
        target.write_bytes(PNG)
        image.symlink_to(target)
        self.assert_blocked('Unverified Blender stage PASS')

    def test_glb_wrong_header_rejected(self):
        self.complete()
        loc, digest = self.file(self.doc['export']['third_person_glb_path'], b'not glb but has glb extension')
        self.doc['export']['third_person_glb_sha256'] = digest
        self.assert_blocked('engine exports missing/unsafe')

    def test_glb_declared_length_mismatch_rejected(self):
        self.complete()
        path = self.doc['export']['third_person_glb_path']
        content = bytearray((self.root / path).read_bytes())
        content[8:12] = struct.pack('<I', len(content) + 10)
        _, digest = self.file(path, bytes(content))
        self.doc['export']['third_person_glb_sha256'] = digest
        self.assert_blocked('engine exports missing/unsafe')

    def test_1p_cannot_borrow_other_heros_glb(self):
        self.complete()
        target, digest = self.file('game/assets/characters/heroes/CHR_Other/hero_1p.glb', glb(b'{"other":true}'))
        self.doc['export']['first_person_glb_path'] = target
        self.doc['export']['first_person_glb_sha256'] = digest
        self.assert_blocked('engine exports missing/unsafe')

    def test_1p_identical_3p_not_accepted(self):
        self.complete()
        third = self.doc['export']['third_person_glb_path']
        self.doc['export']['first_person_glb_path'] = third
        self.doc['export']['first_person_glb_sha256'] = self.doc['export']['third_person_glb_sha256']
        self.assert_blocked('engine exports missing/unsafe')

    def test_invalid_fbx_raw_source_rejected(self):
        self.complete()
        location, digest = self.file(f'art/blender/characters/{self.asset}/raw/invalid.fbx', b'text pretending to be binary fbx')
        self.doc['provenance'].update(raw_sculpt_path=location, raw_sculpt_sha256=digest)
        self.assert_blocked('raw sculpt missing/unsafe')

    def test_raw_source_outside_scoped_folder_rejected(self):
        self.complete()
        location, digest = self.file('art/concepts/characters/other.glb', glb())
        self.doc['provenance'].update(raw_sculpt_path=location, raw_sculpt_sha256=digest)
        self.assert_blocked('raw sculpt missing/unsafe')

    def test_reference_inconsistent_with_plan_rejected(self):
        self.complete()
        self.plan['concept_reference']['sha256'] = '3' * 64
        self.assert_blocked('source differs from character plan')

    def test_reference_inconsistent_with_immutable_lock_rejected(self):
        self.complete()
        self.locks['locked_characters'][self.asset]['source']['sha256'] = '4' * 64
        self.assert_blocked('differs from pinned art lock')

    def test_no_source_commit_with_pass_rejected(self):
        self.complete()
        self.doc['source_commit'] = None
        self.assert_blocked('Unverified Blender stage PASS')

    def test_incomplete_mesh_metrics_rejected(self):
        self.complete()
        self.doc['mesh']['third_person_triangle_count'] = True
        self.assert_blocked('mesh audit incomplete')

    def test_lod_out_of_order_rejected(self):
        self.complete()
        self.doc['mesh']['lod1_triangle_count'] = 70000
        self.assert_blocked('mesh audit incomplete')

    def test_empty_animation_clip_rejected(self):
        self.complete()
        self.doc['export']['animation_clips'] = [""]
        self.assert_blocked('engine exports missing/unsafe')

    def test_owner_approval_without_matching_review_receipt_rejected(self):
        self.complete()
        self.doc['owner_signoff']['review_evidence_sha256'] = '5' * 64
        self.assert_blocked('owner signoff missing/unmatched')

    def test_ready_cannot_already_assert_approved(self):
        self.complete()
        self.doc['production_status'] = 'READY_FOR_OWNER_REVIEW'
        self.assert_blocked('owner review already asserted')

    def test_ready_requires_pending_owner_review(self):
        self.complete()
        self.doc['production_status'] = 'READY_FOR_OWNER_REVIEW'
        self.doc['owner_signoff']['approved'] = False
        self.doc['stages']['owner_review']['status'] = 'FAIL'
        self.assert_blocked('owner review already asserted')

    def test_bad_stage_type_fails_closed(self):
        self.doc['stages']['uv_pbr_bakes']['status'] = ['PASS']
        self.assert_blocked('Missing/invalid Blender stage')

    def test_bad_production_status_type_fails_closed(self):
        self.doc['production_status'] = {'value': 'GAME_READY'}
        self.assert_blocked('Unknown Blender handoff production status')

    def test_wrong_identity_rejected(self):
        self.doc['asset_id'] = 'CHR_Other'
        self.assert_blocked('identity mismatch')

    def test_bool_schema_version_rejected(self):
        self.doc['schema_version'] = True
        self.assert_blocked('identity mismatch')

    def test_malformed_stage_does_not_crash_game_ready(self):
        self.complete()
        self.doc['stages']['owner_review'] = ['PASS']
        self.assert_blocked('Missing/invalid Blender stage')

    def test_malformed_plan_reference_does_not_crash(self):
        self.complete()
        self.plan['concept_reference'] = ['not a dict']
        self.assert_blocked('approved archived character plan')

    def test_oversized_manifest_rejected(self):
        self.doc['blockers'] = ['x' * gate.MAX_MANIFEST_BYTES]
        self.assert_blocked('Malformed or oversized')


if __name__ == '__main__':
    unittest.main()