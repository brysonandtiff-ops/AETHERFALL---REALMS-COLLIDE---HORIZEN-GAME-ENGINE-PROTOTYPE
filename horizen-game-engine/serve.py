#!/usr/bin/env python3
"""Local-only no-store PWA server. Does not expose phone files or launch a game."""
import argparse
import functools
import http.server
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent


class ShellHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cross-Origin-Resource-Policy', 'same-origin')
        self.send_header('Content-Security-Policy',
                         "default-src 'self'; script-src 'self'; style-src 'self'; "
                         "img-src 'self' data: blob:; connect-src 'self'; "
                         "worker-src 'self'; object-src 'none'; "
                         "base-uri 'self'; frame-ancestors 'none'; form-action 'self'")
        super().end_headers()

    def guess_type(self, path):
        if path.endswith('.webmanifest'):
            return 'application/manifest+json'
        if path.endswith('.js'):
            return 'text/javascript'
        return super().guess_type(path)

    def list_directory(self, path):
        self.send_error(403, 'Directory listing unavailable')
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    with http.server.ThreadingHTTPServer(('127.0.0.1', args.port), ShellHandler) as server:
        print(f'HORIZEN GAME ENGINE / LOCAL ONLY / http://127.0.0.1:{args.port}', flush=True)
        server.serve_forever()


if __name__ == '__main__':
    main()
