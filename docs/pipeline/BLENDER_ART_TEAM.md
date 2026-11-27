# Blender Art Team — hero/weapon production checklist (AETHERFALL)

**Authority:** preserve current `VISUAL_CANON_LOCK.md` and exact-source SHA. **Output status:** PROPOSED / NATIVE_UNVERIFIED until actual proof.

## FIND + PLAN: source identity, licence, stance

- [ ] Work-order ID, asset registry ID, hero plan, rights/credit and exact pinned concept master image recorded. Resolve name/variant conflict with owner; no auto remapping.
- [ ] Store the original Meshy/AI sculpt verbatim, with provenance, terms, consent for export/commercial use and SHA-256; no hidden provider licence assumptions.
- [ ] Inspect **real** front, side, rear and three-quarter views of the input (not one projected image). Compare against exact approved face, hair, antlers/ears, palette, cloth/armor, signature weapon and silhouette.
- [ ] Record height/width/body volume and scale 1 Blender Unit = 1 metre, +Z up, -Y forward in the **editable source**. Final GLB coordinate conversion verified after Godot import.

## BUILD A — base and neutral rig pose (source-preserving)

- [ ] Duplicate the original into a new version and place any circular display base in `PRP_<ID>_DisplayStand` **separate** collection; don't silently delete owner art. Export excludes it unless explicitly approved.
- [ ] Remove stray disconnected mesh debris, merge only intended welded surfaces and preserve props as separate modules.
- [ ] Convert frozen/statued humanoid to neutral **A-pose** (arms ~30–45° from torso, fingers separated, cloth clear of elbows); nonhumanoid to neutral 4-foot stance; winged/hovering sets document balance and rest orientation. Posing must not stretch/deform a locked face or change identity.
- [ ] Check limb/head separation, hands/thumbs/toes, weapon and cape clearance in neutral and test poses; no intersecting props in rest pose.
- [ ] Feet/hoof/claw contact at local Z=0; `root` at character local origin; eyes, forward axis, ground socket and camera pivot marked.

## BUILD B — topology, modularity, LOD (INITIAL budgets, calibrate on device)

| Target | LOD0 first-pass budget | LOD1 | LOD2 | Release caveat |
|---|---:|---:|---:|---|
| 3P humanoid hero (visible body including costume) | 40k–70k triangles | <=55% of LOD0 | <=25% | Higher creature/unique props need explicit perf waiver; budgets not proof of art quality. |
| 3P large quadruped | 40k–70k triangles target | <=55% | <=25% | Test skinning at shoulders/hips/jaws/tail; silhouette must survive LOD changes. |
| 1P viewmodel arms/hands/weapon assembly | 20k–35k triangles | optional lower mobile tier | optional | **Separate mesh/camera layer**; never reuse world hurtboxes or show both arms twice. |
| Weapon/hero focus | Character-specific approved budget | <=60% | <=30% | Hero's weapon must remain uniquely readable. |

- [ ] Quad-dominant retopology around shoulder/armpit/elbow, hip/knee, eyelid/lip/jaw and finger knuckles; no n-gons on deforming meshes, flipped normals, isolated internal shells or open cuts in intended closed armour.
- [ ] Use controlled submeshes `GEO_Head`, `GEO_Hair`, `GEO_Torso`, `GEO_Arms`, `GEO_Legs`, `GEO_Armor`, `GEO_Cape`, `GEO_Weapon` as applicable, with character-specific extras (`GEO_Antlers`, `GEO_Tail`, `GEO_Wings`). Don't force human anatomy onto Razor or Thorndell.
- [ ] Baked high-to-low normal/cavity test for silhouette fidelity; topology report includes triangles per mesh, UV island and distortion checks; isolate mirrored UV decisions for asymmetric tattoos/blood-tears/antlers.
- [ ] LOD0–2 pivot/scale/pose/material slots retained, with visual transitions captured at hero gameplay distances, not only turntable.

## BUILD C — UV and PBR (candidate atlas plan)

- [ ] UV0 non-overlapping except approved mirrored/tiling sections, consistent texel density documented; UV1/lightmap where required by chosen Godot material/runtime workflow.
- [ ] Bake normal (tangent-space), AO, curvature (source helper), base colour, metallic, roughness, ORM pack where supported, emissive and translucency/subsurface where required. Verify normal Y convention in Godot; never rely on Blender shader graphs being fully carried by glTF.
- [ ] Candidate 3 × 2048² atlases: head/skin/hair; torso/metal/limbs; cloth/accessories/weapon. 1P hero may have independently approved higher-resolution hands/weapon maps. Record source resolutions, compression and VRAM cost.
- [ ] Materials named `MAT_<ID>_<Surface>`; real metal/stone/bark/glass/cloth/skin/magic differentiation; correct alpha/depth/transparent ordering, backface culling and accessibility-friendly emissive values.
- [ ] Skin softness via supported material/subsurface target (not assume all Blender SSS controls export unchanged). Magic VFX flow masks/shaders implemented/verified in Godot separately; texture emissive values alone do not imply animation or bloom.

## BUILD D — rig, expressive face and physics

- [ ] Separate deform `DEF-*`, IK control, helper and socket bones; root/pelvis/spine/head/arm twist/leg twist hierarchy consistent. Do not enforce one bone count for humanoid and quadruped.
- [ ] 4 weights/vertex target unless renderer/asset profile explicitly permits more; no zero-weight vertices, severe normalization errors, backwards bone rolls, unit-scale mismatches or accessory bones weighted to the wrong limb.
- [ ] Shape keys: `EXP_Neutral` basis, approved hero-specific expression set; face rig and weapon grip pose; export test proves targets are included in GLB (a source shape key alone is insufficient).
- [ ] Test A/T poses, arms +75°, full sprint, jumping, crouch, slide, casting, hit-react, death, full melee and support stance; capture penetration report for shoulder-collar, weapon-cloth, hair-face, thighs-cape and heel-floor.
- [ ] Cloth, tassels, chains, hair, wings/antlers and tendrils: collision proxy volumes, spring hierarchy, deterministic reset on teleport and LOD fallback. **Godot PhysicsBone/SpringBone import must be implemented/tested**, not assumed carried inside generic GLB as scene physics.
- [ ] Stable sockets `SOCK_Hand_L`, `SOCK_Hand_R`, `SOCK_Muzzle`, `SOCK_Camera_1P`, `SOCK_Chest`, `SOCK_Ground`, `SOCK_AoE_Origin`, `SOCK_VFX_Focus`; extra unique hero sockets declared in manifest. Socket origin/direction must match 1P aim and 3P projectile animation.

## BUILD E — distinct 1P and 3P export

- [ ] Create 3P full body with readable ally/enemy team silhouette, weapon draw/sheathe animations, foot-IK markers and camera/occlusion checks.
- [ ] Create 1P arms/hands/focus as `VM_<CHR_ID>` without rest of body or pedestal, independent animation timing/visibility FOV test. 1P viewmodel is cosmetic-only: damage comes from single server-validated combat simulation, never from viewmodel mesh collision.
- [ ] 1P hands don't block reticle while aiming/charging; muzzle flash inside sightline limits; use same ability event times as 3P, not two gameplay simulations.
- [ ] Export glTF2 `.glb` as canonical, Blender +Z/-Y local transform mapped to Godot and verified; embedded PBR images/animations/morphs/bone skin/LOD names validated. FBX only when justified and separately accepted.
- [ ] Export `CHR_<ID>_3P_LOD0.glb`, `VM_<ID>_ArmsFocus_1P.glb`, `WPN_<ID>.glb`, optional distinct LOD GLBs. No new master overwrites; SHA-256 all binaries and keep .blend editable source.

## TEST → REPAIR → RETEST → SHOW → HARDEN → PROVE

- [ ] Native Blender tool report: transforms, geometry, UV, material/image dependency, skin/shape keys/rig animation, file integrity; manually inspect topology and bad weights rather than trusting counts alone.
- [ ] **Four independent real source-rendered** 0°, 90°, 180°, 270° views for every model, plus genuine complete recorded animation clip and weapon/1P FOV capture. Record capture application, executable version, native session, source SHA, file SHA.
- [ ] Fresh Godot 4.7.2 import: check actual Skeleton3D hierarchy, AnimationPlayer/Tree, bone/socket targets, material look, shadows, alpha, LOD, collision and real runtime frame-time; attach real logs and real game-window evidence.
- [ ] Side-by-side with owner approved original; reviewer marks same face/shape/palette/prop/kit across all views. Any critical FAIL means PROPOSAL only.
- [ ] Tested normal, stretched, low-LOD, crouch and spectator/killcam/1P states; fallbacks for physics budget and console/mobile limitations documented.

**Reject**: raw 1M–7M sculpt exported as a single motionless character; pedestal attached to gameplay collision; stock skeleton name with no remap; flipped normals; weapon fused into both views; missing real source; source hash mismatch; procedural screenshot passed off as Blender/Godot; unchanged placeholder promoted as finished hero.