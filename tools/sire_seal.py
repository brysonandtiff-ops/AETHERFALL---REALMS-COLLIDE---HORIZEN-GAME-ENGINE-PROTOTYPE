#!/usr/bin/env python3
"""AETHERFALL S.I.R.E.-compatible SOURCE integrity record (not release authority).

Reads the exact local Git HEAD, verifies a trusted ancestor and the existing
AETHERFALL guards, hashes tracked Git blobs with SHA-256 and SHA3-256, and
emits a source-only inventory/Merkle root. Fails closed on dirty or mismatched
source, untrusted LFS pointers, missing canonical paths, bad remote branch
ancestry, and unverified policy changes.

NO signing key, installation, agent dispatch, network access, deletion,
automatic approval, graphical capture or release command is implemented.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "config/sire-source-seal.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
SEALED_REPOSITORY = "brysonandtiff-ops/AETHERFALL---REALMS-COLLIDE---HORIZEN-GAME-ENGINE-PROTOTYPE"
MAX_TRACKED_FILES = 200000


class IntegrityBlocked(ValueError):
    pass


def _pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntegrityBlocked("Repeated JSON key: " + key)
        result[key] = value
    return result


def strict_json(data: str):
    return json.loads(
        data,
        object_pairs_hook=_pairs_unique,
        parse_constant=lambda value: (_ for _ in ()).throw(IntegrityBlocked("Invalid JSON constant")),
    )


def policy_at(root: Path):
    try:
        data = strict_json((root / POLICY_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise IntegrityBlocked("Source seal policy unavailable/invalid: " + str(exc)) from exc
    expected = {
        "schema_version": 1,
        "id": "SIRE-AETHERFALL-SOURCE-001",
        "project": "AETHERFALL: REALMS COLLIDE",
        "repository": SEALED_REPOSITORY,
        "seal_level": "UNANCHORED_INTEGRITY_ONLY",
        "approval_state": "BLOCKED",
        "automatic_release": False,
        "automatic_merge": False,
        "trust_independent_signature_required": True,
        "clean_tree_required": True,
        "fixed_phone_folder": "AETHERFALL – REALMS COLIDE",
        "fixed_phone_docs_subfolder": "Docs/Inbox",
        "main_godot_project": "game/project.godot",
    }
    if not isinstance(data, dict):
        raise IntegrityBlocked("Seal policy is not a JSON object")
    for key, value in expected.items():
        if type(data.get(key)) is not type(value) or data[key] != value:
            raise IntegrityBlocked("Seal policy deviation: " + key)
    max_bytes = data.get("max_blob_bytes")
    if not isinstance(max_bytes, int) or not 1000000 <= max_bytes <= 150000000:
        raise IntegrityBlocked("Seal blob-size ceiling increased or invalid")
    paths = data.get("required_paths")
    if not isinstance(paths, list) or len(paths) < 13 or len(paths) != len(set(paths)):
        raise IntegrityBlocked("Seal required-path inventory missing/duplicated")
    required = {
        "config/sire-source-seal.json", "config/layout-contract.json",
        "config/local-documents.json", "game/project.godot", "art/asset_registry.json",
        "tools/sire_seal.py", "tools/phone_docs.py", "tools/structure_guard.py",
        "tools/validate_structure.py", ".github/workflows/foundation-check.yml",
        ".sire/integration.json", "AGENTS.md",
    }
    if not required.issubset(paths):
        raise IntegrityBlocked("Seal policy omits protected game/S.I.R.E. files")
    server_controls = data.get("required_server_controls")
    if (not isinstance(server_controls, dict)
        or server_controls.get("branch") != "main"
        or server_controls.get("required_pull_request_review") != "NOT_ENABLED"
        or server_controls.get("required_independent_reviewer") != "NOT_CONFIGURED"
        or server_controls.get("mandatory_status_checks") != "NOT_ENABLED"):
        raise IntegrityBlocked("No externally verified server-side approval rules: BLOCKED")
    gates = data.get("evidence_gates")
    if not isinstance(gates, dict) or any(
        gates.get(name) != "NOT_VERIFIED"
        for name in (
            "blender_source_and_four_views", "original_animation_full_videos",
            "graphical_gameplay", "physical_android", "external_trust_anchor",
            "independent_reviewer_signature", "owner_release_authorisation",
        )
    ):
        raise IntegrityBlocked("Release gates must stay NOT_VERIFIED")
    return data


def _git_bytes(root: Path, *args: str, timeout: int = 60) -> bytes:
    try:
        done = subprocess.run(["git", "-C", str(root), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              check=False, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise IntegrityBlocked("Git inspection unavailable: " + type(exc).__name__) from exc
    if done.returncode:
        raise IntegrityBlocked("Git inspection failed: " + " ".join(args[:2]))
    return done.stdout


def _git_text(root: Path, *args: str) -> str:
    return _git_bytes(root, *args).decode("utf-8", errors="strict").strip()


def _assert_source(root: Path, base: str, expected_head: str):
    if not isinstance(base, str) or not isinstance(expected_head, str) or not SHA40.fullmatch(base) or not SHA40.fullmatch(expected_head):
        raise IntegrityBlocked("Base and expected HEAD must be independently provided 40-hex SHAs")
    actual = _git_text(root, "rev-parse", "--verify", "HEAD")
    if actual != expected_head:
        raise IntegrityBlocked("Source SHA mismatch: refusing stale/different candidate")
    dirty = _git_bytes(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if dirty:
        raise IntegrityBlocked("Working tree dirty or untracked; no source inventory may be sealed")
    _git_bytes(root, "cat-file", "-e", base + "^{commit}")
    _git_bytes(root, "merge-base", "--is-ancestor", base, expected_head)
    return actual


def _monotonic_policy(root: Path, base: str, current: dict):
    """Earlier source policy cannot be silently weakened in a later commit."""
    try:
        previous_entry = _git_bytes(
            root, "ls-tree", "-r", "--name-only", base, "--", POLICY_PATH
        ).decode("utf-8", "strict").strip()
    except UnicodeError as exc:
        raise IntegrityBlocked("Unparseable source policy path in base") from exc
    if not previous_entry:
        return  # This policy was introduced in the current review branch.
    prior = strict_json(_git_bytes(root, "show", base + ":" + POLICY_PATH).decode("utf-8", "strict"))
    if not isinstance(prior, dict):
        raise IntegrityBlocked("Untrusted base policy structure")
    old_paths, new_paths = prior.get("required_paths"), current.get("required_paths")
    if not isinstance(old_paths, list) or not isinstance(new_paths, list):
        raise IntegrityBlocked("Cannot compare required source paths")
    if set(old_paths) - set(new_paths):
        raise IntegrityBlocked("Attempted weakening of earlier S.I.R.E. source seal paths")
    old_max = prior.get("max_blob_bytes")
    new_max = current.get("max_blob_bytes")
    if not isinstance(old_max, int) or new_max > old_max:
        raise IntegrityBlocked("Attempted loosening of earlier source byte limit")
    old_gates, new_gates = prior.get("evidence_gates"), current.get("evidence_gates")
    if not isinstance(old_gates, dict) or not isinstance(new_gates, dict):
        raise IntegrityBlocked("Cannot compare S.I.R.E. proof gates")
    for name, status in old_gates.items():
        if name not in new_gates or status != new_gates[name]:
            raise IntegrityBlocked("Attempted modification of inherited proof gate: " + name)


def _guard_existing(root: Path, base: str):
    tool = root / "tools/structure_guard.py"
    if not tool.is_file() or tool.is_symlink():
        raise IntegrityBlocked("Missing original structure guard")
    spec = importlib.util.spec_from_file_location("aetherfall_original_guard", tool)
    if spec is None or spec.loader is None:
        raise IntegrityBlocked("Could not import structure guard")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    problems = guard.workspace_issues(root) + guard.compare_issues(root, base)
    if problems:
        raise IntegrityBlocked("Existing structural gate FAIL: " + "; ".join(problems[:8]))


def _blob_digests(root: Path, oid: str, limit: int):
    try:
        size = int(_git_text(root, "cat-file", "-s", oid))
    except (ValueError, IntegrityBlocked) as exc:
        raise IntegrityBlocked("Unreadable tracked Git blob") from exc
    if size < 0 or size > limit:
        raise IntegrityBlocked("Blob exceeds verified size ceiling; use reviewed binary storage")
    content = _git_bytes(root, "cat-file", "blob", oid, timeout=90)
    if len(content) != size:
        raise IntegrityBlocked("Git blob size changed while verifying")
    if content.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        raise IntegrityBlocked("LFS pointer is not independently resolved: NOT VERIFIED")
    return len(content), hashlib.sha256(content).hexdigest(), hashlib.sha3_256(content).hexdigest()


def _source_inventory(root: Path, policy: dict):
    raw = _git_bytes(root, "ls-tree", "-r", "-z", "--full-tree", "HEAD")
    entries = []
    seen = set()
    for item in raw.split(b"\0"):
        if not item:
            continue
        try:
            hdr, name = item.split(b"\t", 1)
            mode, kind, oid = hdr.decode("ascii").split(" ")
            path = name.decode("utf-8", errors="strict")
        except (ValueError, UnicodeError) as exc:
            raise IntegrityBlocked("Unparseable tracked Git tree entry") from exc
        if mode not in ("100644", "100755") or kind != "blob" or not SHA40.fullmatch(oid):
            raise IntegrityBlocked("Unsupported Git entry (symlink/submodule/nonblob): " + path)
        if (not path or path.startswith("/") or "\\" in path or
            any(part in ("", ".", "..") for part in path.split("/"))):
            raise IntegrityBlocked("Unsafe Git path in source inventory")
        if path.casefold() in seen:
            raise IntegrityBlocked("Case-colliding tracked Git paths")
        seen.add(path.casefold())
        size, sha2, sha3 = _blob_digests(root, oid, policy["max_blob_bytes"])
        entries.append({"path": path, "bytes": size, "sha256": sha2, "sha3_256": sha3})
        if len(entries) > MAX_TRACKED_FILES:
            raise IntegrityBlocked("Source inventory exceeds supported entry count")
    if not entries:
        raise IntegrityBlocked("No tracked files to inventory")
    known = {row["path"] for row in entries}
    missing = set(policy["required_paths"]) - known
    if missing:
        raise IntegrityBlocked("Missing locked file(s): " + ", ".join(sorted(missing)))
    return sorted(entries, key=lambda item: item["path"].encode("utf-8"))


def _merkle(entries):
    """Domain-separated binary Merkle tree over canonical tracked file entries."""
    leaves = []
    for entry in entries:
        canonical = json.dumps(
            entry, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        leaves.append(hashlib.sha256(b"AETHERFALL-LEAF-V1\x00" + canonical).digest())
    while len(leaves) > 1:
        if len(leaves) % 2:
            leaves.append(leaves[-1])
        leaves = [
            hashlib.sha256(b"AETHERFALL-NODE-V1\x00" + leaves[i] + leaves[i + 1]).digest()
            for i in range(0, len(leaves), 2)
        ]
    return leaves[0].hex()


def source_receipt(root: Path, base: str, expected_head: str):
    root = Path(root).resolve()
    policy = policy_at(root)
    observed_sha = _assert_source(root, base, expected_head)
    _monotonic_policy(root, base, policy)
    _guard_existing(root, base)
    inventory = _source_inventory(root, policy)
    tree_oid = _git_text(root, "rev-parse", "HEAD^{tree}")
    receipt = {
        "schema": "sire.aetherfall.source-integrity.v1",
        "project": policy["project"],
        "repository": policy["repository"],
        "source_commit_sha": observed_sha,
        "trusted_base_sha": base,
        "git_tree_object_id": tree_oid,
        "source_inventory": inventory,
        "merkle_root_sha256": _merkle(inventory),
        "artifact_status": "UNANCHORED_INTEGRITY_ONLY",
        "independent_external_signature": "ABSENT",
        "law104_release_predicate": "NOT_SATISFIED",
        "law105_graphical_and_animation_proof": "NOT_VERIFIED",
        "law106_release_badge": "NOT_MINTED",
        "server_side_branch_review": "NOT_ENABLED",
        "law108_12_stage_signed_pipeline": "NOT_VERIFIED",
        "phone_downloads_access": "NOT_VERIFIED",
        "sire_agent_mcp_runtime": "NOT_CONNECTED",
        "release_status": "BLOCKED",
        "mutation_performed": False,
        "auto_merge": False,
        "auto_deploy": False,
        "notes": "Hashes bind inspected Git blobs only. This receipt has no independent trust anchor or signature; GitHub CI and original Godot logs are separately observable. NOT a game/runtime/release certification.",
    }
    return receipt


def canonical_json(data):
    return (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _write_outside_repo(destination: Path, data: bytes, root: Path):
    if not destination.is_absolute():
        raise IntegrityBlocked("--output must be an absolute path outside the checkout")
    if destination.resolve().is_relative_to(root.resolve()):
        raise IntegrityBlocked("Receipts must stay outside tracked source (no self-hash circularity)")
    if not destination.parent.is_dir() or destination.parent.is_symlink():
        raise IntegrityBlocked("Receipt destination parent missing or unsafe")
    flags = os.O_CREAT | os.O_WRONLY | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(destination, flags, 0o600)
    except OSError as exc:
        raise IntegrityBlocked("Refusing to overwrite existing receipt: " + str(exc)) from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if hashlib.sha256(destination.read_bytes()).digest() != hashlib.sha256(data).digest():
            raise IntegrityBlocked("Receipt readback did not match source bytes")
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def _parse_receipt_file(path: Path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 50 * 1024 * 1024:
        raise IntegrityBlocked("Untrusted/missing/oversize receipt file")
    return strict_json(path.read_text(encoding="utf-8"))


def check_saved_receipt(root: Path, receipt_file: Path, expected_head: str, expected_digest: str | None):
    if not isinstance(expected_head, str) or not SHA40.fullmatch(expected_head):
        raise IntegrityBlocked("Expected Git SHA must be exact")
    if expected_digest is not None and (not isinstance(expected_digest, str) or not SHA64.fullmatch(expected_digest)):
        raise IntegrityBlocked("Independent receipt digest format invalid")
    report = _parse_receipt_file(receipt_file)  # Size/symlink check before reading bytes
    if expected_digest is not None:
        if hashlib.sha256(receipt_file.read_bytes()).hexdigest() != expected_digest:
            raise IntegrityBlocked("Saved receipt failed independently supplied digest anchor")
    if not isinstance(report, dict) or report.get("schema") != "sire.aetherfall.source-integrity.v1":
        raise IntegrityBlocked("Saved receipt schema invalid")
    if report.get("release_status") != "BLOCKED" or report.get("artifact_status") != "UNANCHORED_INTEGRITY_ONLY":
        raise IntegrityBlocked("Saved receipt makes an unsupported release claim")
    if report.get("source_commit_sha") != expected_head:
        raise IntegrityBlocked("Saved receipt belongs to another Git commit")
    recomputed = source_receipt(root, report.get("trusted_base_sha", ""), expected_head)
    if canonical_json(recomputed) != canonical_json(report):
        raise IntegrityBlocked("Saved receipt does not match source Git inventory")
    return {
        "source_commit_sha": expected_head,
        "inventory_matches": True,
        "receipt_digest_matches_independent_pin": expected_digest is not None,
        "result": "ANCHORED_INTEGRITY_ONLY" if expected_digest is not None else "UNANCHORED_INTEGRITY_ONLY",
        "release_status": "BLOCKED",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="S.I.R.E. source integrity only — NOT a release seal")
    sub = parser.add_subparsers(dest="command", required=True)
    source = sub.add_parser("source", help="Compute SHA256/SHA3 + Merkle over real tracked Git HEAD")
    source.add_argument("--base", required=True, help="Trusted exact 40-hex ancestor SHA")
    source.add_argument("--expected-head", required=True, help="Expected exact candidate Git SHA")
    source.add_argument("--output", type=Path, help="Absolute external receipt path, created without overwrite")
    saved = sub.add_parser("verify", help="Verify a stored receipt and optional external digest anchor")
    saved.add_argument("--receipt", type=Path, required=True)
    saved.add_argument("--expected-head", required=True)
    saved.add_argument("--expected-receipt-sha256", help="Independently trusted digest, not self-reported")
    args = parser.parse_args(argv)
    try:
        if args.command == "source":
            result = source_receipt(ROOT, args.base, args.expected_head)
            data = canonical_json(result)
            if args.output:
                _write_outside_repo(args.output, data, ROOT)
                print(json.dumps({
                    "receipt_path": str(args.output),
                    "receipt_sha256": hashlib.sha256(data).hexdigest(),
                    "source_commit_sha": result["source_commit_sha"],
                    "tracked_files": len(result["source_inventory"]),
                    "merkle_root_sha256": result["merkle_root_sha256"],
                    "integrity": result["artifact_status"],
                    "release_status": "BLOCKED"
                }, sort_keys=True))
            else:
                sys.stdout.buffer.write(data)
        else:
            print(json.dumps(check_saved_receipt(
                ROOT, args.receipt, args.expected_head, args.expected_receipt_sha256
            ), sort_keys=True))
        return 0
    except (IntegrityBlocked, OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
