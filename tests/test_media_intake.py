"""Offline intake verifier regression tests; do not claim engine evidence."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('intake_verifier', Path(__file__).resolve().parents[1] / 'tools' / 'verify_media_intake.py')
verify_module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_module)

class MediaIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.content = b'GIF89a' + b'X' * 24
        self.rel = 'evidence/prototype-previews/CHR_Korvex/test.gif'
        self.source = self.root / self.rel
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(self.content)
        import hashlib
        self.entry = {'path': self.rel, 'mime':'image/gif','bytes':len(self.content),'sha256':hashlib.sha256(self.content).hexdigest()}
        self.manifest = self.root / 'manifest.json'
        self.make_manifest(self.entry)

    def tearDown(self):
        self.temp.cleanup()

    def make_manifest(self,entry):
        self.manifest.write_text(json.dumps({'schema_version':1,'project':'AETHERFALL: REALMS COLLIDE','entries':[entry]}))

    def test_valid_bytes_pass(self):
        self.assertEqual(verify_module.verify(self.manifest,self.root),0)

    def test_modified_source_fails(self):
        self.source.write_bytes(self.content+b'changed')
        self.assertNotEqual(verify_module.verify(self.manifest,self.root),0)

    def test_missing_source_fails(self):
        self.source.unlink()
        self.assertNotEqual(verify_module.verify(self.manifest,self.root),0)

    def test_path_traversal_fails(self):
        self.make_manifest({**self.entry,'path':'evidence/prototype-previews/../test.gif'})
        self.assertNotEqual(verify_module.verify(self.manifest,self.root),0)

    def test_lied_about_mime_fails(self):
        self.make_manifest({**self.entry,'mime':'image/png'})
        self.assertNotEqual(verify_module.verify(self.manifest,self.root),0)

if __name__ == '__main__':
    unittest.main()
