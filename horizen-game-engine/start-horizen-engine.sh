#!/data/data/com.termux/files/usr/bin/bash
# HORIZEN GAME ENGINE - Android Termux local-only launcher.
# Does not kill an existing server or modify any source art.
set -euo pipefail

APPDIR="$HOME/horizen-game-engine"
BASE_PORT="${HORIZEN_PORT:-8080}"

if ! command -v python3 >/dev/null 2>&1; then
  echo 'Python 3 is required. Run: pkg install python' >&2
  exit 1
fi
if ! [[ "$BASE_PORT" =~ ^[0-9]{4,5}$ ]] || (( BASE_PORT < 1024 || BASE_PORT > 65529 )); then
  echo 'HORIZEN_PORT must be an integer between 1024 and 65529.' >&2
  exit 1
fi

if [[ ! -f "$APPDIR/serve.py" ]]; then
  # Files may have been extracted to Android shared storage instead of Termux HOME.
  if [[ ! -d "$HOME/storage/shared" ]]; then
    echo 'Android shared storage is unavailable.' >&2
    echo 'Run termux-setup-storage, answer y, and grant Android storage access.' >&2
    exit 1
  fi
  SOURCE_FILE="$(find -L "$HOME/storage/shared" -maxdepth 8 -type f -path '*/horizen-game-engine/serve.py' -print -quit 2>/dev/null || true)"
  if [[ -z "$SOURCE_FILE" ]]; then
    echo 'No horizen-game-engine/serve.py found in Android shared storage.' >&2
    echo 'Check the PWA folder under AETHERFALL / 02_GAME_AND_ENGINE.' >&2
    exit 1
  fi
  SOURCE_DIR="${SOURCE_FILE%/serve.py}"
  mkdir -p "$APPDIR"
  cp -Rn "$SOURCE_DIR/." "$APPDIR/"
  echo 'Copied HORIZEN PWA source to Termux HOME; existing files preserved.'
fi

for relative in serve.py index.html manifest.webmanifest sw.js icons/icon-192.png icons/icon-512.png; do
  if [[ ! -f "$APPDIR/$relative" ]]; then
    echo "Incomplete PWA folder: missing $APPDIR/$relative" >&2
    exit 1
  fi
done

command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true
cd "$APPDIR"

# Never terminate an unrelated listener. Try 8080, then 8081-8085 if occupied.
PORT="$(python3 - "$BASE_PORT" <<'PYPORT'
import socket
import sys
base = int(sys.argv[1])
for port in range(base, base + 6):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            continue
        print(port)
        break
else:
    sys.exit('No free local port found within the six-port window.')
PYPORT
)"

printf '\nHORIZEN GAME ENGINE - LOCAL ONLY\n'
printf 'Open http://127.0.0.1:%s in Chrome on this phone.\n' "$PORT"
printf 'Keep this Termux session running; Ctrl+C stops the server.\n\n'
exec python3 serve.py --port "$PORT"
