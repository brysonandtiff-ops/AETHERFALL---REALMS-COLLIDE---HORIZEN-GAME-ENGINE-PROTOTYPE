#!/usr/bin/env python3
"""Owner-run AETHERFALL document intake from Android Download.

Safe default: preview only. Explicit --apply copies eligible documents into
'Internal storage/AETHERFALL – REALMS COLIDE/Docs/Inbox' and verifies SHA-256.
No files are deleted, originals overwritten, remote services contacted,
permissions installed or background tasks started.

Termux: run termux-setup-storage once and approve Android storage access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config/local-documents.json"
EXPECTED_ROOT = "AETHERFALL – REALMS COLIDE"
EXPECTED_SUBDIR = ("Docs", "Inbox")
MAX_BYTES = 100 * 1024 * 1024
COPIED = "COPIED"
SKIPPED = "SKIPPED_IDENTICAL"


def configuration():
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise ValueError(f"Local documents policy missing/malformed: {exc}") from exc
    if (not isinstance(config, dict)
        or config.get("schema_version") != 1
        or config.get("physical_folder_name") != EXPECTED_ROOT
        or config.get("destination_relative") != "/".join(EXPECTED_SUBDIR)
        or config.get("copy_only") is not True
        or config.get("preview_default") is not True
        or config.get("no_overwrite") is not True
        or config.get("verify_sha256") is not True
        or config.get("auto_install") is not False
        or config.get("background_service") is not False):
        raise ValueError("Document intake policy must retain canonical phone path and copy-only safety")
    extensions = config.get("extensions")
    names = config.get("project_markers")
    if not isinstance(extensions, list) or not extensions or not all(
        isinstance(v, str) and re.fullmatch(r"\.[a-z0-9]{2,5}", v) for v in extensions
    ):
        raise ValueError("Document extension allowlist malformed")
    if not isinstance(names, list) or not names or not all(
        isinstance(v, str) and re.fullmatch(r"[a-z0-9_]{3,40}", v) for v in names
    ):
        raise ValueError("Project marker allowlist malformed")
    return config


def default_paths():
    base = Path.home() / "storage"
    return base / "downloads", base / "shared" / EXPECTED_ROOT


def validate_folder(root: Path, downloads: Path, apply: bool):
    if not downloads.is_dir():
        raise ValueError("Android Download is unavailable. In Termux, run termux-setup-storage and grant access.")
    if root.is_symlink() or (not root.is_dir()):
        raise ValueError("Project destination folder does not exist. Use the exact existing name: " + EXPECTED_ROOT)
    root_real, downloads_real = root.resolve(), downloads.resolve()
    if root_real == downloads_real or root_real.is_relative_to(downloads_real):
        raise ValueError("Project docs destination cannot be inside Android Download")
    dest = root / EXPECTED_SUBDIR[0] / EXPECTED_SUBDIR[1]
    if dest.exists() and (dest.is_symlink() or not dest.is_dir()):
        raise ValueError("Unsafe existing Docs/Inbox destination")
    if apply:
        dest.mkdir(parents=True, exist_ok=True)
    return dest


def valid_source(candidate: Path, downloads: Path, extensions: set[str]):
    if candidate.is_symlink() or candidate.name.startswith("."):
        raise ValueError("Hidden or symbolic-link source blocked")
    if candidate.suffix.lower() not in extensions:
        raise ValueError("Not an allowed document type: " + candidate.name)
    if not candidate.is_file() or candidate.resolve().parent != downloads.resolve():
        raise ValueError("Source must be a regular top-level file in Android Download")
    size = candidate.stat().st_size
    if not 0 < size <= MAX_BYTES:
        raise ValueError("Document must be nonempty and no larger than 100 MiB")
    if re.search(r'[\x00-\x1f<>:"\\|?*]', candidate.name) or candidate.name.endswith((" ", ".")):
        raise ValueError("Non-portable document filename")
    return candidate


def project_document(filename: str, markers: tuple[str, ...]):
    """Only scan project-tagged filenames; explicit --file can include others."""
    name = filename.lower().replace(" ", "_").replace("-", "_").replace("–", "_")
    return any(name.startswith(marker) for marker in markers)


def select_documents(downloads: Path, filename: str | None, scan: bool, config: dict):
    allowed = set(config["extensions"])
    if filename:
        path = Path(filename).expanduser()
        if not path.is_absolute():
            path = downloads / path
        return [valid_source(path, downloads, allowed)]
    if not scan:
        raise ValueError("Specify one --file or --scan to search only project-named documents")
    markers = tuple(config["project_markers"])
    found = []
    for path in sorted(downloads.iterdir(), key=lambda item: item.name.casefold()):
        if not path.is_file() or path.is_symlink():
            continue
        if path.suffix.lower() not in allowed or not project_document(path.name, markers):
            continue
        try:
            found.append(valid_source(path, downloads, allowed))
        except ValueError:
            continue
    return found


def sha256(path: Path):
    result = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def target_for(source: Path, inbox: Path):
    """Never overwrite an existing document, even if filenames match."""
    checksum = sha256(source)
    first = inbox / source.name
    if first.is_file() and not first.is_symlink() and sha256(first) == checksum:
        return first, checksum, True
    if not first.exists() and not first.is_symlink():
        return first, checksum, False
    alternate = inbox / f"{source.stem}__sha256-{checksum[:12]}{source.suffix}"
    if alternate.is_file() and not alternate.is_symlink() and sha256(alternate) == checksum:
        return alternate, checksum, True
    if not alternate.exists() and not alternate.is_symlink():
        return alternate, checksum, False
    for index in range(1, 1000):
        path = inbox / f"{source.stem}__sha256-{checksum[:12]}-{index:03d}{source.suffix}"
        if path.is_file() and not path.is_symlink() and sha256(path) == checksum:
            return path, checksum, True
        if not path.exists() and not path.is_symlink():
            return path, checksum, False
    raise ValueError("Too many conflicting filenames; no source has been modified")


def perform_copy(source: Path, target: Path, checksum: str):
    before = source.stat()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(target, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output, source.open("rb") as input_file:
            shutil.copyfileobj(input_file, output, 1024 * 1024)
        after = source.stat()
        if (before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns
            or sha256(target) != checksum or sha256(source) != checksum):
            raise ValueError("Source changed during copy or SHA-256 readback failed")
    except BaseException:
        # Only remove the new failed copy; never touch original download.
        target.unlink(missing_ok=True)
        raise


def process(downloads: Path, root: Path, sources: list[Path], apply: bool):
    destination = validate_folder(root, downloads, apply)
    status = []
    for source in sources:
        # Selection may precede a download finishing; revalidate when actually copying.
        valid_source(source, downloads, set(configuration()["extensions"]))
        target, checksum, identical = target_for(source, destination)
        if identical:
            state = SKIPPED
        elif apply:
            perform_copy(source, target, checksum)
            state = COPIED
        else:
            state = "PREVIEW_ONLY"
        status.append({
            "source_name": source.name,
            "destination": str(target),
            "sha256": checksum,
            "result": state,
            "source_retained": True,
        })
    return status


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preview/copy AETHERFALL docs into the existing Android phone folder")
    parser.add_argument("--file", help="Document filename/path inside Android Download (single file)")
    parser.add_argument("--scan", action="store_true", help="Top-level Download only, project-named documents")
    parser.add_argument("--apply", action="store_true", help="Explicit opt-in: COPY, never move/delete originals")
    parser.add_argument("--watch", action="store_true", help="Visible foreground watching; Ctrl+C stops")
    parser.add_argument("--poll-seconds", type=int, default=20, help="Foreground scan interval, minimum 5s")
    parser.add_argument("--download-dir", type=Path, help="Override download folder (test/custom owner selection)")
    parser.add_argument("--project-root", type=Path, help="Override exact existing AETHERFALL folder")
    parser.add_argument("--status", action="store_true", help="Display target setup without creating files")
    args = parser.parse_args(argv)
    try:
        config = configuration()
        default_download, default_root = default_paths()
        downloads = (args.download_dir or default_download).expanduser()
        root = (args.project_root or default_root).expanduser()
        if args.status:
            print(json.dumps({
                "target": str(root / EXPECTED_SUBDIR[0] / EXPECTED_SUBDIR[1]),
                "folder_exists": root.is_dir(),
                "downloads_available": downloads.is_dir(),
                "automatic_android_download_redirection": False,
                "installed_background_watcher": False,
                "mode": "OWNER_OPT_IN_ONLY"
            }, indent=2))
            return 0
        if bool(args.file) == bool(args.scan):
            raise ValueError("Choose exactly one of --file or --scan")
        if args.watch and (not args.apply or not args.scan or args.poll_seconds < 5):
            raise ValueError("--watch requires --scan --apply and poll interval >=5 seconds")
        validate_folder(root, downloads, args.apply)
        if args.watch:
            print("OWNER-STARTED foreground watcher; only project-named document files, Ctrl+C to stop.", flush=True)
            previous = {}
            try:
                while True:
                    sources = select_documents(downloads, None, True, config)
                    current = {str(file): (file.stat().st_size, file.stat().st_mtime_ns) for file in sources}
                    stable = [file for file in sources if str(file) in previous and previous[str(file)] == current[str(file)]]
                    if stable:
                        for result in process(downloads, root, stable, True):
                            if result["result"] == COPIED:
                                print(json.dumps(result, ensure_ascii=False), flush=True)
                    previous = current
                    time.sleep(args.poll_seconds)
            except KeyboardInterrupt:
                print("Watcher stopped; downloads and project documents preserved.")
                return 0
        sources = select_documents(downloads, args.file, args.scan, config)
        results = process(downloads, root, sources, args.apply)
        print(json.dumps({
            "project_folder": str(root), "target_subfolder": "/".join(EXPECTED_SUBDIR),
            "mode": "COPY" if args.apply else "PREVIEW_ONLY",
            "documents": results, "total": len(results),
            "original_downloads_deleted": False
        }, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
