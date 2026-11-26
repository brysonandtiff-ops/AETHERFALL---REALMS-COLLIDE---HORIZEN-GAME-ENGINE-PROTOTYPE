#!/data/data/com.termux/files/usr/bin/bash
# User-installed launcher at ~/start-horizen-engine.sh. Never claims a remote link.
set -euo pipefail
command -v termux-wake-lock >/dev/null 2>&1 && termux-wake-lock || true
cd "$HOME/horizen-game-engine" || { printf 'Install the PWA files into ~/horizen-game-engine first.\n' >&2; exit 1; }
command -v python3 >/dev/null || { printf 'Python 3 is required. Run: pkg install python\n' >&2; exit 1; }
# Stop a prior listener on this explicitly reserved local port.
if command -v fuser >/dev/null 2>&1; then
  fuser -k 8080/tcp >/dev/null 2>&1 || true
elif command -v lsof >/dev/null 2>&1; then
  old=$(lsof -tiTCP:8080 -sTCP:LISTEN || true)
  if [ -n "$old" ]; then kill $old; fi
else
  printf 'No fuser/lsof detected. If 8080 is busy, install psmisc or stop the existing server.\n' >&2
fi
printf '\nHORIZEN GAME ENGINE — LOCAL SERVER\nOpen http://127.0.0.1:8080 in Chrome.\nCtrl+C stops the server.\n\n'
exec python3 serve.py --port 8080
