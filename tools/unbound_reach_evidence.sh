#!/usr/bin/env bash
# From the repository root: GODOT=/path/to/Godot bash tools/unbound_reach_evidence.sh /tmp/new-evidence-directory
set -euo pipefail
GODOT="${GODOT:-godot}"
OUT="${1:?Supply a new output directory}"
mkdir "$OUT"
OUT=$(cd "$OUT" && pwd)
mkdir "$OUT/frames"
"$GODOT" --version | tee "$OUT/engine.txt"
grep -q '^4\.7\.2\.stable' "$OUT/engine.txt"
git rev-parse HEAD > "$OUT/tested-commit.txt"
printf '%s\n' "${PR_HEAD_SHA:-$(git rev-parse HEAD)}" > "$OUT/source-head.txt"
printf '%s\n' 'Graphical Linux native software-rendered scripted test; NOT Android, human input or production FPS.' > "$OUT/scope.txt"
"$GODOT" --headless --path game --editor --import --quit 2>&1 | tee "$OUT/import.log"
timeout 75 "$GODOT" --headless --path game --script res://tests/unbound_reach_test.gd 2>&1 | tee "$OUT/native.log"
grep -q '^UNBOUND_REACH_NATIVE_PASS:' "$OUT/native.log"
if grep -Eiq '(SCRIPT ERROR|ERROR|FATAL):' "$OUT/import.log" "$OUT/native.log"; then exit 1; fi
export AF_CAPTURE_DIR="$OUT/frames" LIBGL_ALWAYS_SOFTWARE=1
xvfb-run -a timeout 220 "$GODOT" --display-driver x11 --audio-driver Dummy --rendering-method gl_compatibility --resolution 960x540 --fixed-fps 24 --path game --script res://tests/unbound_reach_capture.gd 2>&1 | tee "$OUT/graphics.log"
grep -q '^UNBOUND_REACH_GRAPHICAL_CAPTURE:' "$OUT/graphics.log"
if grep -Eiq '(SCRIPT ERROR|ERROR|FATAL):' "$OUT/graphics.log"; then exit 1; fi
for item in '015 hub' '059 arena-hit' '077 sniper' '132 support'; do read -r frame name <<< "$item"; cp "$OUT/frames/frame-$frame.png" "$OUT/$name.png"; done
ffmpeg -v error -framerate 24 -start_number 0 -i "$OUT/frames/frame-%03d.png" -frames:v 180 -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$OUT/range-interactions.mp4"
ffprobe -v error -show_entries stream=width,height,nb_frames,duration -of json "$OUT/range-interactions.mp4" > "$OUT/video-metadata.json"
(cd "$OUT" && sha256sum *.png *.mp4 *.txt > SHA256SUMS)
