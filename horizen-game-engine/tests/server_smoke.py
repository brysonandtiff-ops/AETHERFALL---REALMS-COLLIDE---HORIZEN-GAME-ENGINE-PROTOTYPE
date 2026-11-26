#!/usr/bin/env python3
"""Real localhost HTTP server contract; does not test browser SW/offline or game engine."""
import json
import pathlib
import sys
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from serve import ShellHandler
from http.server import ThreadingHTTPServer


class LocalServerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),ShellHandler)
        cls.port=cls.server.server_port
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def get(self,path):
        return urlopen(f'http://127.0.0.1:{self.port}/{path}',timeout=3)

    def test_index_and_headers(self):
        with self.get('index.html') as res:
            self.assertEqual(res.status,200)
            self.assertEqual(res.headers['Cache-Control'],'no-store, no-cache, must-revalidate')
            self.assertEqual(res.headers['X-Content-Type-Options'],'nosniff')
            self.assertIn("script-src 'self'",res.headers['Content-Security-Policy'])
            self.assertIn(b'HORIZEN GAME ENGINE',res.read())

    def test_manifest_exact_name_and_install_icons(self):
        with self.get('manifest.webmanifest') as res:
            self.assertEqual(res.headers['Content-Type'],'application/manifest+json')
            data=json.load(res)
            self.assertEqual(data['name'],'HORIZEN GAME ENGINE')
            self.assertEqual(data['short_name'],'HORIZEN GAME ENGINE')
            self.assertEqual(data['display'],'standalone')
        for icon in ('icons/icon-192.png','icons/icon-512.png','icons/icon.svg'):
            with self.get(icon) as res:
                self.assertEqual(res.status,200)

    def test_sw_exists_and_root_is_private_to_loopback(self):
        with self.get('sw.js') as res:
            self.assertIn(b'horizen-shell-v0.1.0',res.read())
        self.assertEqual(self.server.server_address[0],'127.0.0.1')

    def test_directory_listing_forbidden(self):
        with self.assertRaises(HTTPError) as err:
            self.get('tests/fixtures/')
        self.assertEqual(err.exception.code,403)


if __name__=='__main__':
    unittest.main(verbosity=2)
