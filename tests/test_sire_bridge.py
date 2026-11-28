import importlib.util
import json
import shutil
import subprocess
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("sire_bridge", ROOT / "tools/sire_bridge.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class PrivateSireBridgeTests(unittest.TestCase):
    def setUp(self):
        self.lock = bridge.load_lock()

    def test_actual_lock(self):
        self.assertEqual(bridge.lock_errors(self.lock), [])

    def test_reject_changed_source_identity(self):
        for key, value in (("commit", "a" * 40), ("repository", "elsewhere"),
                           ("registry_blob", "b" * 40), ("studio_blob", "c" * 40),
                           ("visibility", "public"), ("runtime_status", "CONNECTED")):
            with self.subTest(key=key):
                altered = dict(self.lock, **{key: value})
                self.assertTrue(bridge.lock_errors(altered))

    def test_reject_ambient_authority(self):
        for key in bridge.FALSE_FLAGS:
            for value in (True, 0, None):
                with self.subTest(key=key, value=value):
                    self.assertTrue(bridge.lock_errors(dict(self.lock, **{key: value})))

    def test_no_checkout_is_blocked_and_does_not_run_git(self):
        with patch.object(bridge, "git") as git:
            result = bridge.source_report(None)
            git.assert_not_called()
        self.assertEqual(result["source"], "BLOCKED")
        self.assertEqual(result["runtime"], "NOT_VERIFIED")
        self.assertFalse(result["dispatch"])

    def test_checkout_inside_game_rejected_before_git(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            nested = root / "private"
            nested.mkdir()
            with patch.object(bridge, "git") as git:
                result = bridge.source_report(nested, project=root)
                git.assert_not_called()
            self.assertEqual(result["source"], "BLOCKED")

    def test_wrong_origin_and_wrong_pin_fail_closed(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            for responses in ([str(root), "https://example.org/other"],
                              [str(root), next(iter(bridge.ORIGINS)), "a" * 40]):
                with self.subTest(responses=responses), patch.object(bridge, "git", side_effect=responses):
                    self.assertEqual(bridge.source_report(root)["source"], "BLOCKED")

    def test_dirty_checkout_is_blocked(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            responses = [str(root), next(iter(bridge.ORIGINS)), bridge.PIN, "?? injected.py"]
            with patch.object(bridge, "git", side_effect=responses):
                self.assertEqual(bridge.source_report(root)["source"], "BLOCKED")

    def test_catalog_does_not_execute_blocked_checkout(self):
        with tempfile.TemporaryDirectory() as name:
            with patch.object(bridge, "source_report", return_value={"source": "BLOCKED"}), \
                    patch.object(bridge.subprocess, "run") as run:
                self.assertEqual(bridge.catalog(name)["source"], "BLOCKED")
                run.assert_not_called()

    def test_studio_ids_are_extracted_without_execution(self):
        source = 'raise RuntimeError("must not execute")\nCAPABILITIES: tuple = (StudioCapability("first", "x"), StudioCapability("second", "y"))'
        with patch.object(bridge, "git", return_value=source):
            self.assertEqual(bridge.studio_ids(ROOT), ["first", "second"])

    def test_studio_rejects_duplicate_ids(self):
        source = 'CAPABILITIES: tuple = (StudioCapability("first"), StudioCapability("first"))'
        with patch.object(bridge, "git", return_value=source):
            with self.assertRaises(ValueError):
                bridge.studio_ids(ROOT)

    def test_actual_git_rejects_unrelated_checkout(self):
        import shutil
        import subprocess
        if not shutil.which("git"):
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "remote", "add", "origin",
                            "https://github.com/other/repo.git"], check=True)
            self.assertEqual(bridge.source_report(root)["source"], "BLOCKED")


    @unittest.skipUnless(shutil.which("git"), "git unavailable")
    def test_real_git_and_subprocess_positive_catalog_fixture(self):
        # A real isolated Git checkout exercises the bridge; fixture data is
        # not S.I.R.E. production source, nor evidence of its live runtime.
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            def run(*args):
                return subprocess.check_output(
                    ["git", "-C", str(root), *args], text=True).strip()
            run("init", "-q")
            run("remote", "add", "origin", "https://github.com/" + bridge.REPO + ".git")
            registry = root / bridge.REGISTRY
            studio = root / bridge.STUDIO
            for file in (registry, studio):
                file.parent.mkdir(parents=True, exist_ok=True)
            registry.write_text(
                'import json\nnames = ("agents", "skills", "plugins", "abilities", "execution")\n'
                'print(json.dumps(dict(success=True, counts={n: 1 for n in names}, '
                '**{n: [{"id": "fixture"}] for n in names})))\n', encoding="utf-8")
            studio.write_text(
                'CAPABILITIES: tuple = (StudioCapability("fixture"),)\n', encoding="utf-8")
            run("add", ".")
            run("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
            pin = run("rev-parse", "HEAD")
            registry_blob = run("rev-parse", "HEAD:" + bridge.REGISTRY)
            studio_blob = run("rev-parse", "HEAD:" + bridge.STUDIO)
            with patch.multiple(bridge, PIN=pin, REGISTRY_BLOB=registry_blob,
                                STUDIO_BLOB=studio_blob):
                report = bridge.source_report(root)
                self.assertEqual(report["source"], "PINNED_SOURCE_VERIFIED")
                self.assertEqual(report["tracked_paths"], 2)
                result = bridge.catalog(root)
                self.assertEqual(result["catalogue"], "EXECUTED_SOURCE_REGISTRY")
                self.assertEqual(result["studio_capability_ids"], ["fixture"])
                self.assertEqual(result["studio_verified_count"], 0)
                self.assertEqual(result["runtime"], "NOT_VERIFIED")
                self.assertEqual(result["runner"], "NOT_VERIFIED")
                self.assertFalse(result["dispatch"])
                registry.write_text("raise RuntimeError('unexpected execution')\n",
                                    encoding="utf-8")
                self.assertEqual(bridge.source_report(root)["source"], "BLOCKED")
                self.assertEqual(bridge.catalog(root)["source"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
