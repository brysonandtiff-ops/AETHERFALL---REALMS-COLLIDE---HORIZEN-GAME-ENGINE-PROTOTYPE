# AETHERFALL — User-supplied prototype preview evidence audit

**Date:** 26 November 2026 (Australia/Perth)  
**Reviewer:** ChatGPT (file-format and frame inspection only)  
**Classification:** PROVIDED MEDIA / VISUAL BLOCKOUT PREVIEW; not native-engine/model-source/gameplay verification.  
**Repository main at inspection:** `a600e72f9ed7638d0dddce59123e855c511a84a1`.

| Source | What was directly inspected | What cannot be claimed |
| --- | --- | --- |
| `39441.png` (WebP-encoded) | Korvex labelled front, three-quarter, back and Grave Maul images; text claims exported GLB and VTK 9.6 renderer. | No raw GLB file, topology test, Blender/Godot proof or verified 5,244 triangle count was received. |
| `39442.gif` | Animated Korvex turntable; 650×650, 16 GIF frames; visible front/side/back blockout. | Animated raster preview is not a verified mesh, rig, engine runtime, or gameplay recording. |
| `39408.mp4` | ThornDell rotating low-poly blockout; H.264, 850×900, 3.000 seconds, 16 fps, 48 frames, no audio. Label visible: “real GLB model turn — offline VTK render”; another says “procedural blockout / no rig / not Godot or Blender proof”. | No actual source GLB/`.blend`, mesh structure, topology or playable controls verified. |
| `39406.png`, `39412.png`, `39403.png` (WebP-encoded) | ThornDell, Korvex, Vellaris *concept sheets*. Each contains composite turnaround/ability/material infographic sections. | No game-ready 3D asset, engine import or test. |
| `39409.jpg`, `39385.jpg` (WebP-encoded) | Owner handwriting and design/role notes. | No measured status or completed 3D build established. |

## Provenance and limits

- Eight conversation uploads were inspected; the original full-resolution ThornDell PNG from the previously approved art generation is a ninth separate staged source.
- Exact-byte SHA-256 hashes and proposed destinations are stored in `docs/art/MEDIA_INTAKE_2026-11-26.json`. The GitHub PR currently contains **documentation only**: the media files are staged in a separate conversation attachment, **not checked into GitHub**.
- Preview text refers to GLB exports, but neither corresponding `.glb` file was supplied in this intake. Never report source files, Blender execution, Godot import, animations, performance or gameplay as passed.
- The preview images show useful silhouettes but should not be used to certify agreement with detailed approved concept sheets.
- The provided MP4/GIF should be preserved unmodified; any later derivative contact sheet or cropped thumbnail must be identified as a derivative.

## Outstanding proof for completion

Acquire the model/source project, verify cryptographic hashes, inspect mesh and material data, render real Blender turnarounds with version, import in pinned Godot 4.x, run functional and regression tests, capture genuine full-length evidence and attach the tested Git commit. Until then: `PROTOTYPE_PREVIEW_ONLY`.
