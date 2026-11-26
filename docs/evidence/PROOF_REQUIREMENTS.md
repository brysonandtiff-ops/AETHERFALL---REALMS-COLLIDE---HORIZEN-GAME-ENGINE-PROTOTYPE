# Real evidence requirements

Store genuine original captures in the corresponding `evidence/` folder, named with task, timestamp and source commit SHA. Add a short capture note with tool version, device/renderer, result, checksum and known limitations.

| Folder | Required real source when work reaches that stage |
| --- | --- |
| `evidence/blender/` | Blender scene-derived four-angle renders, rig/UV and animation checks. |
| `evidence/godot/` | Actual Godot editor/game screenshots, import report and unedited playable video. |
| `evidence/device/` | Android/other physical-device capture with device, OS, controls and performance. |
| `evidence/performance/` | Real FPS/frame-time and memory measurements with test configuration. |

Static syntax or folder tests are STRUCTURE_ONLY; screenshots of concept art are CONCEPT_ONLY; neither is gameplay or native-engine proof. Never generate imitation runtime screenshots/videos. Before release, validate actual build, play, saves, accessibility, regression, security and device performance.
