"""Safe, offline phone Docs/Inbox intake checks. No Android or background work."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aetherfall_phone_docs", ROOT / "tools/phone_docs.py")
phone = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(phone)


class PhoneDocumentsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="aetherfall-phone-docs-")
        self.base = Path(self.tmp.name)
        self.downloads = self.base / "Download"
        self.downloads.mkdir()
        self.root = self.base / phone.EXPECTED_ROOT
        self.root.mkdir()
        (self.root / "korvex_blockout_v01").mkdir()
        self.original_marker = self.root / "korvex_blockout_v01" / "original.txt"
        self.original_marker.write_text("do-not-touch")
        self.config = phone.configuration()

    def tearDown(self):
        self.tmp.cleanup()

    def upload(self, name="AETHERFALL_game_plan.pdf", data=b"real owner document bytes"):
        path = self.downloads / name
        path.write_bytes(data)
        return path

    def test_canonical_screenshot_phone_location_not_repo_spelling(self):
        self.assertEqual(phone.EXPECTED_ROOT, "AETHERFALL – REALMS COLIDE")
        self.assertEqual(self.config["destination_relative"], "Docs/Inbox")
        self.assertFalse(self.config["background_service"])

    def test_preview_does_not_create_docs_or_move_download(self):
        original = self.upload()
        files = phone.select_documents(self.downloads, original.name, False, self.config)
        result = phone.process(self.downloads, self.root, files, apply=False)
        self.assertEqual(result[0]["result"], "PREVIEW_ONLY")
        self.assertFalse((self.root / "Docs").exists())
        self.assertTrue(original.is_file())
        self.assertEqual(self.original_marker.read_text(), "do-not-touch")

    def test_apply_creates_docs_copies_and_verifies_hash(self):
        original = self.upload()
        result = phone.process(self.downloads, self.root, [original], apply=True)
        dest = self.root / "Docs/Inbox" / original.name
        self.assertEqual(result[0]["result"], "COPIED")
        self.assertEqual(dest.read_bytes(), original.read_bytes())
        self.assertEqual(result[0]["sha256"], phone.sha256(dest))
        self.assertTrue(original.is_file())
        self.assertEqual(self.original_marker.read_text(), "do-not-touch")

    def test_idempotent_second_apply_skips_identical_file(self):
        original = self.upload()
        phone.process(self.downloads, self.root, [original], apply=True)
        status = phone.process(self.downloads, self.root, [original], apply=True)
        self.assertEqual(status[0]["result"], "SKIPPED_IDENTICAL")
        self.assertEqual(len(list((self.root / "Docs/Inbox").glob("*"))), 1)

    def test_collision_keeps_existing_file_and_writes_versioned_copy(self):
        original = self.upload(data=b"new version")
        inbox = self.root / "Docs/Inbox"
        inbox.mkdir(parents=True)
        existing = inbox / original.name
        existing.write_bytes(b"older approved document")
        status = phone.process(self.downloads, self.root, [original], apply=True)
        self.assertEqual(existing.read_bytes(), b"older approved document")
        self.assertEqual(status[0]["result"], "COPIED")
        self.assertIn("__sha256-", status[0]["destination"])
        self.assertEqual(Path(status[0]["destination"]).read_bytes(), b"new version")

    def test_project_named_scan_only_includes_relevant_documents(self):
        matching = self.upload("Korvex_blockout_notes.docx")
        self.upload("holiday_schedule.pdf")
        self.upload("AETHERFALL_sprite.png")
        files = phone.select_documents(self.downloads, None, True, self.config)
        self.assertEqual(files, [matching])

    def test_explicit_non_prefixed_download_document_is_allowed(self):
        file = self.upload("notes_about_a_character.md")
        candidates = phone.select_documents(self.downloads, file.name, False, self.config)
        self.assertEqual(candidates, [file])

    def test_non_document_extension_is_rejected(self):
        file = self.upload("AETHERFALL_binary.apk")
        with self.assertRaisesRegex(ValueError, "Not an allowed document type"):
            phone.valid_source(file, self.downloads, set(self.config["extensions"]))

    def test_source_must_be_top_level_download_file(self):
        sibling = self.base / "private_document.pdf"
        sibling.write_bytes(b"private")
        with self.assertRaisesRegex(ValueError, "top-level file"):
            phone.valid_source(sibling, self.downloads, set(self.config["extensions"]))

    def test_symlink_source_is_rejected(self):
        original = self.upload()
        alias = self.downloads / "AETHERFALL_alias.pdf"
        try:
            alias.symlink_to(original)
        except OSError:
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "symbolic-link source blocked"):
            phone.valid_source(alias, self.downloads, set(self.config["extensions"]))

    def test_destination_folder_symlink_is_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.root / "Docs").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "Unsafe existing Docs folder"):
            phone.validate_folder(self.root, self.downloads, apply=True)
        self.assertEqual(list(outside.iterdir()), [])

    def test_missing_phone_project_root_does_not_create_duplicate_folder(self):
        other = self.base / "AETHERFALL – REALMS COLLIDE"
        with self.assertRaisesRegex(ValueError, "exact existing name"):
            phone.validate_folder(other, self.downloads, apply=True)
        self.assertFalse(other.exists())

    def test_identical_existing_versioned_copy_is_skipped(self):
        src = self.upload(data=b"same content as versioned")
        dest = self.root / "Docs/Inbox"
        dest.mkdir(parents=True)
        (dest / src.name).write_bytes(b"other content")
        first = phone.process(self.downloads, self.root, [src], apply=True)
        second = phone.process(self.downloads, self.root, [src], apply=True)
        self.assertEqual(first[0]["result"], "COPIED")
        self.assertEqual(second[0]["result"], "SKIPPED_IDENTICAL")

    def test_empty_or_oversize_documents_rejected(self):
        empty = self.upload("AETHERFALL_empty.pdf", b"")
        with self.assertRaisesRegex(ValueError, "nonempty"):
            phone.valid_source(empty, self.downloads, set(self.config["extensions"]))
        huge = self.downloads / "AETHERFALL_huge.pdf"
        with huge.open("wb") as output:
            output.seek(phone.MAX_BYTES)
            output.write(b"X")
        with self.assertRaisesRegex(ValueError, "100 MiB"):
            phone.valid_source(huge, self.downloads, set(self.config["extensions"]))

    def test_watch_without_explicit_apply_is_blocked(self):
        from unittest.mock import patch
        with patch("sys.argv", [
            "phone_docs.py", "--scan", "--watch",
            "--download-dir", str(self.downloads), "--project-root", str(self.root)
        ]):
            self.assertEqual(phone.main(), 2)

    def test_status_is_read_only_and_reports_no_auto_redirection(self):
        from contextlib import redirect_stdout
        from io import StringIO
        buffer = StringIO()
        from unittest.mock import patch
        with patch("sys.argv", [
            "phone_docs.py", "--status", "--download-dir", str(self.downloads),
            "--project-root", str(self.root)
        ]):
            with redirect_stdout(buffer):
                self.assertEqual(phone.main(), 0)
        report = json.loads(buffer.getvalue())
        self.assertFalse(report["automatic_android_download_redirection"])
        self.assertFalse(report["installed_background_watcher"])
        self.assertFalse((self.root / "Docs").exists())

    def test_security_contract_requires_copy_only_policy(self):
        from unittest.mock import patch
        from io import StringIO
        bad = dict(self.config)
        bad["copy_only"] = False
        # The live policy reader must refuse arbitrary removal of copy-only checks.
        with patch.object(phone.Path, "read_text", return_value=json.dumps(bad)):
            with self.assertRaisesRegex(ValueError, "copy-only safety"):
                phone.configuration()


if __name__ == "__main__":
    unittest.main()
