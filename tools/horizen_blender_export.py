"""Non-destructive Blender scripting-tab / background export for HORIZEN Model Forge.

Use inside Blender: blender your_scene.blend --background --python tools/horizen_blender_export.py --
    --asset-id CHR_Example --output-dir /path/to/exports

Exports GLB, binary STL scaled to millimetres, and SHA-256 report, without moving,
scaling, solidifying or deleting source mesh. No printable/game-ready claims.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

# Blender --python does not guarantee the script directory is importable.
SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from horizen_mesh_io import audit_triangles, binary_stl, safe_asset_id, sha256_file, MAX_BINARY_STL_TRIANGLES


def blender_export(args=None):
    parser = argparse.ArgumentParser(description="HORIZEN selected mesh export; no native/gameplay certification")
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--output-dir", required=True, help="Explicit output parent directory (no phone or cloud sync)")
    parser.add_argument("--millimetres-per-metre", default=1000.0, type=float)
    options = parser.parse_args(args)
    asset_id = safe_asset_id(options.asset_id)
    import bpy  # Import ONLY in actual Blender; pure mesh helpers are unit-testable separately.

    if not bpy.data.filepath or not Path(bpy.data.filepath).is_file() or bpy.data.is_dirty:
        raise ValueError("Save all current .blend scene changes before generating a traceable export receipt")
    source_digest = sha256_file(bpy.data.filepath)
    selected = list(bpy.context.selected_objects)
    if len(selected) != 1 or selected[0].type != "MESH":
        raise ValueError("Select exactly one genuine mesh object before export")
    obj = selected[0]
    dep = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(dep)
    mesh = obj_eval.to_mesh()
    if mesh is None:
        raise ValueError("Blender could not evaluate the selected mesh")
    try:
        mesh.calc_loop_triangles()
        # Values from Blender are in scene coordinates; require explicit metric scene unit.
        units = bpy.context.scene.unit_settings
        if units.system != "METRIC" or abs(units.scale_length - 1.0) > 1e-6:
            raise ValueError("Set Blender Scene Units to METRIC, scale_length=1.0 before export")
        matrix = obj_eval.matrix_world
        vertices = [tuple(float(x) for x in (matrix @ v.co)) for v in mesh.vertices]
        faces = [tuple(int(i) for i in tri.vertices) for tri in mesh.loop_triangles]
        if len(faces) > MAX_BINARY_STL_TRIANGLES:
            raise ValueError("Selected mesh exceeds the 64 MiB binary STL intake limit; simplify in a separate approved source version")
        audit = audit_triangles(vertices, faces)
        if not audit["triangles"]:
            raise ValueError("Selected mesh has no triangles")
        output_root = Path(options.output_dir).expanduser().resolve()
        run_key = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        out = output_root / asset_id / run_key
        out.mkdir(parents=True, exist_ok=False)
        glb = out / (asset_id + ".glb")
        stl = out / (asset_id + "_millimetres.stl")
        # glTF exporter reads original selection. It does not overwrite Blender source.
        result = bpy.ops.export_scene.gltf(
            filepath=str(glb), export_format="GLB", use_selection=True
        )
        if "FINISHED" not in result or not glb.is_file():
            raise RuntimeError("Actual Blender glTF/GLB export failed")
        stl.write_bytes(binary_stl(vertices, faces, millimetres_per_metre=options.millimetres_per_metre))
        with glb.open("rb") as stream:
            glb_magic = stream.read(4)
        if glb.stat().st_size < 20 or glb_magic != b"glTF":
            raise RuntimeError("GLB header invalid; export requires Blender reinspection")
        artifacts = {p.name: {"sha256": sha256_file(p), "bytes": p.stat().st_size} for p in (glb, stl)}
        receipt = {
            "schema_version": 1,
            "asset_id": asset_id,
            "tool": "HORIZEN Blender selected-mesh export",
            "source_blend_basename": Path(bpy.data.filepath).name,
            "source_blend_sha256": source_digest,
            "source_object": obj.name,
            "blender_version": bpy.app.version_string,
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "mesh_audit": audit,
            "stl_scale_intended_mm_per_scene_metre": options.millimetres_per_metre,
            "artifacts": artifacts,
            "stage": "BLENDER_EXPORT_UNDER_REVIEW",
            "claims": {
                "glb_exported_from_selected_real_mesh": True,
                "stl_scaled_for_millimetres": True,
                "stl_thickened_or_slicer_verified": False,
                "godot_import_verified": False,
                "gameplay_verified": False,
                "phone_saved": False,
            },
            "warnings": [
                "Standalone source hash and 4-angle owner-identity comparison still required",
                "STL is only scaled to mm; no automatic solidify, wall-thickness check or print certification",
                "This receipt is not Godot import, playable game or Android runtime proof",
            ],
        }
        (out / "export_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        return out
    finally:
        obj_eval.to_mesh_clear()


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    print("HORIZEN Blender export receipt:", blender_export(argv))
