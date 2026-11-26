#!/usr/bin/env python3
"""Verify AETHERFALL media intake bytes. This does NOT verify GLBs or gameplay."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

MAGIC = {
    'image/png': lambda b: b.startswith(b'\x89PNG\r\n\x1a\n'),
    'image/webp': lambda b: len(b) >= 12 and b[:4] == b'RIFF' and b[8:12] == b'WEBP',
    'image/gif': lambda b: b.startswith((b'GIF87a', b'GIF89a')),
    'video/mp4': lambda b: len(b) >= 12 and b[4:8] == b'ftyp',
}
PREFIXES = ('art/concepts/characters/', 'docs/characters/owner-notes/', 'evidence/prototype-previews/')

def verify(manifest, media_root):
    try:
        document = json.loads(Path(manifest).read_text(encoding='utf-8'))
    except (OSError, ValueError) as e:
        print(f'FAIL manifest: {e}', file=sys.stderr)
        return 1
    entries = document.get('entries', [])
    if document.get('schema_version') != 1 or document.get('project') != 'AETHERFALL: REALMS COLLIDE' or not entries:
        print('FAIL malformed manifest/project', file=sys.stderr)
        return 1
    root = Path(media_root).resolve()
    seen = set()
    ok = 0
    missing = 0
    failed = 0
    for entry in entries:
        rel = entry.get('path')
        if not isinstance(rel, str) or not rel.startswith(PREFIXES) or '\\' in rel or any(p in ('', '.', '..') for p in rel.split('/')):
            print(f'FAIL invalid path: {rel}', file=sys.stderr)
            failed += 1
            continue
        if rel.casefold() in seen:
            print(f'FAIL duplicate/case collision: {rel}', file=sys.stderr)
            failed += 1
            continue
        seen.add(rel.casefold())
        path = root / rel
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            print(f'FAIL unsafe path: {rel}', file=sys.stderr)
            failed += 1
            continue
        if not path.is_file():
            print(f'MISSING {rel}', file=sys.stderr)
            missing += 1
            continue
        content = path.read_bytes()
        sha = hashlib.sha256(content).hexdigest()
        mime = entry.get('mime')
        problems = []
        if sha != entry.get('sha256'):
            problems.append('SHA-256 mismatch')
        if len(content) != entry.get('bytes'):
            problems.append('byte-length mismatch')
        if mime not in MAGIC or not MAGIC[mime](content):
            problems.append(f'content signature does not match {mime}')
        if problems:
            print(f'FAIL {rel}: {", ".join(problems)}', file=sys.stderr)
            failed += 1
        else:
            print(f'OK {rel}')
            ok += 1
    print(f'MEDIA INTAKE RESULT: verified={ok}, missing={missing}, failed={failed}, expected={len(entries)}; source-media only, NOT engine proof')
    return 0 if not missing and not failed and ok == len(entries) else 1

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='docs/art/MEDIA_INTAKE_2026-11-26.json')
    parser.add_argument('--media-root', default='.')
    args = parser.parse_args()
    return verify(args.manifest, args.media_root)

if __name__ == '__main__':
    sys.exit(main())
