#!/usr/bin/env python3
"""Read-only checks for AETHERFALL 1P/3P handoff contract and staged hashes.

No native Blender, Godot, device, platform or independent signature is certified.
Exit 0: locally supplied SPEC structure or bytes validated; exit 2: rejected/blocked.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

PROJECT = 'AETHERFALL: REALMS COLLIDE'
HEX64 = re.compile(r'^[0-9a-f]{64}$')
ID = re.compile(r'^CHR_[A-Za-z][A-Za-z0-9_]*$')
SHA40 = re.compile(r'^[0-9a-f]{40}$')
SOCKETS = {
    'SOCK_Hand_L', 'SOCK_Hand_R', 'SOCK_Muzzle', 'SOCK_Camera_1P',
    'SOCK_Chest', 'SOCK_Ground', 'SOCK_AoE_Origin', 'SOCK_VFX_Focus'
}
STATES = {'Idle', 'Walk', 'Sprint', 'Strafe', 'Jump', 'Airborne', 'Crouch', 'Slide', 'Disabled'}
PHASES = ('windup','telegraph','active','follow_through','recovery','cooldown')


def safe_rel(raw: str) -> bool:
    if not isinstance(raw, str) or not raw or '\\' in raw or '\0' in raw or raw.startswith('/'):
        return False
    parts = raw.split('/')
    return not any(p in ('', '.', '..') or ':' in p for p in parts)


def load_json(path: Path):
    with path.open('r',encoding='utf-8') as f:
        return json.load(f)


def validate_hero(x: dict) -> list[str]:
    errors=[]
    if not isinstance(x,dict): return ['Hero contract is not JSON object']
    if x.get('schema_version') != 1 or x.get('project') != PROJECT: errors.append('project/schema mismatch')
    ident=x.get('hero_id');
    if not isinstance(ident,str) or not ID.fullmatch(ident): errors.append('bad hero_id (must be registered separately)')
    if x.get('approval_state') != 'SPEC_ONLY' or x.get('release_state') != 'BLOCKED': errors.append('unverified release/approval promoted')
    concept=x.get('concept') or {}
    if not isinstance(concept,dict): return errors+['concept not object']
    if not safe_rel(concept.get('source_path')): errors.append('unsafe source path')
    srcsha=concept.get('source_sha256')
    if srcsha is not None and (not isinstance(srcsha,str) or not HEX64.fullmatch(srcsha)): errors.append('bad original source hash')
    if concept.get('binary_in_repo') and not srcsha: errors.append('binary claim without pinned source hash')
    if concept.get('original_ai_mesh_path') is not None:
        if not safe_rel(concept['original_ai_mesh_path']):errors.append('unsafe AI-mesh path')
        if not isinstance(concept.get('original_ai_mesh_sha256'),str) or not HEX64.fullmatch(concept['original_ai_mesh_sha256']): errors.append('unhashed original AI mesh')
    blender=x.get('blender') or {}
    if not isinstance(blender,dict): return errors+['blender not object']
    if blender.get('unit_scale') != 1.0 or blender.get('up_axis') != '+Z' or blender.get('forward_axis') != '-Y': errors.append('Blender metres / +Z / -Y mismatch')
    if blender.get('pedestal_policy') != 'EXCLUDE_FROM_CHARACTER_EXPORT_SAVE_SEPARATELY':errors.append('pedestal policy mismatch')
    if blender.get('target_pose') != 'A_POSE_OR_NEUTRAL_SPECIES_STANCE':errors.append('no clean rigging pose')
    parts=blender.get('model_parts');
    if not isinstance(parts,list) or not parts or len(parts)!=len(set(map(str,parts))):errors.append('missing/duplicate model parts')
    three=blender.get('three_p') or {}
    one=blender.get('one_p') or {}
    if not isinstance(three,dict) or not isinstance(one,dict):return errors+['1P/3P declarations missing']
    if three.get('asset_id')!=ident:errors.append('3P asset ID mismatch')
    if one.get('asset_id')!='VM_'+str(ident) or one.get('render_only') is not True: errors.append('1P viewmodel separate/render-only rule broken')
    for info,key in ((three,'observed_lod0_triangles'),(one,'observed_triangles')):
        low = info.get('lod0_triangle_target_min' if info is three else 'triangle_target_min')
        hi = info.get('lod0_triangle_target_max' if info is three else 'triangle_target_max')
        if not isinstance(low,int) or not isinstance(hi,int) or not (0<low<=hi<=150000): errors.append('invalid triangle targets '+key)
        obs=info.get(key)
        if obs is not None and (not isinstance(obs,int) or obs<0): errors.append('invalid measured triangle count '+key)
    lod1=three.get('lod1_fraction_max'); lod2=three.get('lod2_fraction_max')
    if not (type(lod1) in (int,float) and type(lod2) in (int,float) and 0<lod2<=lod1<1): errors.append('bad LOD fractions')
    socks=blender.get('sockets')
    if not isinstance(socks,list) or not all(isinstance(s,str) for s in socks) or not SOCKETS.issubset(set(socks or [])) or len(socks)!=len(set(map(str,socks))): errors.append('required sockets absent or repeated')
    mat=blender.get('materials') or {}
    if not isinstance(mat,dict) or type(mat.get('atlases_max')) is not int or type(mat.get('atlas_dimension_max')) is not int or not (1<=mat['atlases_max']<=6) or not (512<=mat['atlas_dimension_max']<=8192):errors.append('invalid PBR atlas plan')
    elif not {'normal','ao','roughness','metallic','emissive'}.issubset(set(mat.get('required_bakes',[]))):errors.append('required PBR bakes not included')
    rig=blender.get('rig') or {}
    if (not isinstance(rig,dict) or rig.get('skeleton_required') is not True or
            rig.get('deformation_test_verified') is not False or
            type(rig.get('max_vertex_weights_target')) is not int or
            not 1<=rig['max_vertex_weights_target']<=8 or
            not isinstance(rig.get('named_clips'),list) or not rig['named_clips']):
        errors.append('rig/animation plan absent or falsely native-verified')
    gameplay=x.get('gameplay') or {}
    if not isinstance(gameplay,dict):return errors+['gameplay contract not object']
    if gameplay.get('single_authoritative_combat') is not True or gameplay.get('pvp_server_authority_required') is not True or gameplay.get('collision_uses_vfx') is not False:errors.append('combat authority or VFX collision mismatch')
    cameras=gameplay.get('camera_variants')
    if not isinstance(cameras,list) or not all(isinstance(v,str) for v in cameras) or set(cameras)!={'1P','3P'}:errors.append('must support distinct 1P and 3P')
    states=gameplay.get('locomotion_states')
    if not isinstance(states,list) or not all(isinstance(v,str) for v in states) or not STATES.issubset(set(states)):errors.append('locomotion base states absent')
    if not safe_rel(gameplay.get('abilities_contract_path')): errors.append('bad ability contract path')
    ev=x.get('evidence') or {}
    if not isinstance(ev,dict):return errors+['evidence not object']
    expected={'native_blender_0_90_180_270':'NOT_RUN','native_godot_4_7_2':'NOT_RUN','one_p_camera_proof':'NOT_RUN', 'three_p_camera_proof':'NOT_RUN','full_ability_clip':'NOT_RUN','independent_signed_law108':'NOT_AVAILABLE','phone_acceptance':'NOT_RUN'}
    if any(ev.get(k)!=v for k,v in expected.items()):errors.append('SPEC_ONLY cannot assert native/device/signed evidence')
    return errors


def validate_ability(x: dict) -> list[str]:
    errors=[]
    if not isinstance(x,dict):return ['Ability contract not object']
    if x.get('project')!=PROJECT or x.get('schema_version')!=1: errors.append('ability project/schema mismatch')
    if not isinstance(x.get('ability_id'),str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]+',x['ability_id']): errors.append('bad ability ID')
    if not isinstance(x.get('hero_id'),str) or not ID.fullmatch(x['hero_id']):errors.append('bad hero ID in ability')
    phases=x.get('phases_ticks') or {}
    if not isinstance(phases,dict) or any(type(phases.get(p)) is not int or phases[p]<0 for p in PHASES):errors.append('phase timestamps invalid')
    elif phases['active']<1:errors.append('active duration missing')
    target=x.get('targeting') or {}
    if not isinstance(target,dict) or target.get('team') not in ('ally','enemy','self','all') or target.get('requires_line_of_sight') not in (True,False):errors.append('invalid target team/LOS')
    elif not isinstance(target.get('min_range_m'),(float,int)) or not isinstance(target.get('max_range_m'),(float,int)) or not 0<=target['min_range_m']<=target['max_range_m']:errors.append('invalid target range')
    hit=x.get('hit_volume') or {}
    if not isinstance(hit,dict) or hit.get('owner')!='SERVER_COMBAT_SIMULATION' or hit.get('kind') not in ('sphere','box','capsule','arc','ray'):
        errors.append('hit volume must be server owned explicit geometry')
    if x.get('visual_effects_are_hit_detection') is not False:errors.append('visual effects must NOT be hit detection')
    events=x.get('animation_events') or {}
    if not isinstance(events,dict) or not all(isinstance(events.get(k),str) and events.get(k) for k in ('first_person','third_person','server_hit_event')): errors.append('missing dual-view/simulation event hooks')
    anti=x.get('anti_replay') or {}
    if not isinstance(anti,dict) or any(anti.get(k) is not True for k in ('event_id_required','server_seed_required','double_commit_rejected')):errors.append('anti-replay / server seed missing')
    tele=x.get('telegraph') or {}
    if not isinstance(tele,dict) or not all(tele.get(k) for k in ('enemy_shape','ally_shape','caption_cue','audible_cue')):errors.append('ally/enemy readable telegraph absent')
    if x.get('status')!='TEST_FIXTURE_NOT_HERO_CANON_NOT_IMPLEMENTED':errors.append('ability fixture promoted as implemented/canon')
    return errors


def verify_files(root: Path, manifest: dict) -> list[str]:
    errors=[]
    if not isinstance(manifest,dict) or manifest.get('project')!=PROJECT or manifest.get('stage')!='INTEGRITY_ONLY_NOT_NATIVE_PROOF':return ['bad file-manifest identity/stage']
    sha=manifest.get('source_commit_sha')
    if not isinstance(sha,str) or not SHA40.fullmatch(sha):errors.append('source commit sha unverified/invalid')
    entries=manifest.get('files')
    if not isinstance(entries,list) or not entries: return errors+['no files in manifest']
    seen=set()
    for e in entries:
        if not isinstance(e,dict):errors.append('invalid file record');continue
        rel=e.get('path')
        if not safe_rel(rel):errors.append('unsafe file path');continue
        if rel.casefold() in seen:errors.append('duplicate/case-colliding path '+rel);continue
        seen.add(rel.casefold())
        path = root / rel
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):errors.append('missing/symlink/unsafe file '+rel);continue
        if e.get('bytes')!=path.stat().st_size:errors.append('size mismatch '+rel)
        digest=e.get('sha256')
        if not isinstance(digest,str) or not HEX64.fullmatch(digest) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:errors.append('hash mismatch '+rel)
        if path.suffix.lower()=='.glb':
            header=path.read_bytes()[:12]
            if len(header)!=12 or header[:4]!=b'glTF' or struct.unpack_from('<I',header,4)[0]!=2 or struct.unpack_from('<I',header,8)[0]!=path.stat().st_size: errors.append('bad GLB header '+rel)
    return errors


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--hero',type=Path)
    p.add_argument('--ability',type=Path)
    p.add_argument('--files-manifest',type=Path)
    p.add_argument('--root',type=Path,default=Path.cwd())
    p.add_argument('--demand-native',action='store_true',help='fail closed: native/signed validation is delegated to independently authenticated S.I.R.E. proof gate')
    args=p.parse_args(argv)
    if not any((args.hero,args.ability,args.files_manifest,args.demand_native)):
        p.error('select --hero / --ability / --files-manifest / --demand-native')
    problems=[]
    try:
        if args.hero: problems.extend('hero: '+s for s in validate_hero(load_json(args.hero)))
        if args.ability: problems.extend('ability: '+s for s in validate_ability(load_json(args.ability)))
        if args.files_manifest:problems.extend('file: '+s for s in verify_files(args.root, load_json(args.files_manifest)))
    except (OSError,ValueError,TypeError) as exc:problems.append('invalid file/format: '+str(exc))
    if args.demand_native:
        problems.append('native engine + independent LAW-108 signature + real owner-phone evidence required; offline validator cannot certify')
    result={'check':'AETHERFALL_SPEC_OR_INTEGRITY_ONLY', 'result':'BLOCKED' if problems else 'PASS_SPEC_OR_BYTE_INTEGRITY_ONLY','native_certified':False, 'gameplay_certified':False, 'release_certified':False, 'errors':problems}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if problems else 0

if __name__=='__main__':raise SystemExit(main())