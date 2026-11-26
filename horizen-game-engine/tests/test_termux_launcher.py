#!/usr/bin/env python3
"""Linux shell contract for Android launcher. This is NOT a real phone acceptance test."""
import os
import pathlib
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
from urllib.request import urlopen

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAUNCHER = ROOT / 'start-horizen-engine.sh'
MINIMUM = (
    'serve.py', 'index.html', 'manifest.webmanifest', 'sw.js',
    'icons/icon-192.png', 'icons/icon-512.png',
)

def available_port():
    for _ in range(15):
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
            if 10000 < port < 65000:
                return port
    raise AssertionError('Could not allocate a test port')

class TermuxLauncherContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='horizen-termux-smoke-')
        self.addCleanup(self.temp.cleanup)
        self.home = pathlib.Path(self.temp.name)
        self.base_port = available_port()
        self.env = {**os.environ, 'HOME': str(self.home), 'HORIZEN_PORT': str(self.base_port)}

    def put_shared_source(self):
        source = self.home / 'storage' / 'shared' / 'AETHERFALL – REALMS COLIDE' / '02_GAME_AND_ENGINE' / 'horizen-game-engine'
        source.mkdir(parents=True)
        for rel in MINIMUM:
            to = source / rel
            to.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, to)
        return source

    def run_server(self, expected_port):
        process = subprocess.Popen(
            ['bash', str(LAUNCHER)], env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.addCleanup(lambda: self.stop(process))
        for _ in range(80):
            if process.poll() is not None:
                out, err = process.communicate(timeout=2)
                self.fail(f'Launcher died unexpectedly: {process.returncode}: {out!r} {err!r}')
            try:
                with urlopen(f'http://127.0.0.1:{expected_port}/', timeout=0.2) as response:
                    self.assertEqual(response.status, 200)
                    self.assertIn(b'HORIZEN GAME ENGINE', response.read())
                    return process
            except OSError:
                time.sleep(0.05)
        self.fail('Launcher failed to serve the expected port')

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.terminate()
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=3)

    def test_locates_shared_android_folder_and_copies_without_original_changes(self):
        original = self.put_shared_source()
        self.run_server(self.base_port)
        installed = self.home / 'horizen-game-engine'
        self.assertTrue((installed / 'serve.py').is_file())
        self.assertEqual((installed / 'serve.py').read_bytes(), (original / 'serve.py').read_bytes())
        self.assertTrue((original / 'serve.py').is_file())

    def test_follows_real_termux_storage_shared_symlink(self):
        # termux-setup-storage creates a symlink; default find does not traverse it.
        real_shared = self.home / 'android-emulated-0'
        source = real_shared / 'AETHERFALL – REALMS COLIDE' / '02_GAME_AND_ENGINE' / 'horizen-game-engine'
        source.mkdir(parents=True)
        for rel in MINIMUM:
            destination = source / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, destination)
        storage = self.home / 'storage'
        storage.mkdir()
        (storage / 'shared').symlink_to(real_shared, target_is_directory=True)
        self.run_server(self.base_port)
        self.assertTrue((self.home / 'horizen-game-engine' / 'serve.py').is_file())
        self.assertEqual((source / 'serve.py').read_bytes(), (self.home / 'horizen-game-engine' / 'serve.py').read_bytes())

    def test_occupied_port_chooses_another_without_killing_existing_listener(self):
        self.put_shared_source()
        with socket.socket() as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind(('127.0.0.1', self.base_port))
            listener.listen(1)
            self.run_server(self.base_port + 1)
            self.assertEqual(listener.getsockname()[1], self.base_port)
            self.assertEqual(listener.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR), 0)

    def test_no_storage_refuses_missing_app_without_creating_fake_install(self):
        run = subprocess.run(['bash', str(LAUNCHER)], env=self.env, capture_output=True, text=True, timeout=3)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('termux-setup-storage', run.stderr)
        self.assertFalse((self.home / 'horizen-game-engine').exists())

if __name__ == '__main__':
    unittest.main(verbosity=2)
