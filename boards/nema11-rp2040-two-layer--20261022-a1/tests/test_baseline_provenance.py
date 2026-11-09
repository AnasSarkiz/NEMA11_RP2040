"""Pin public baseline fixture bytes before any native build is attempted."""
import hashlib
import json
from pathlib import Path
import unittest

FIXTURE = Path(__file__).resolve().parents[1] / 'references/baseline-1233ccdf'
HASHES = {'config/connections.json': '99f84c98b2f45c06c7842307fa57942e677848d229f971270004457179872876', 'config/component-plan.json': '09180ed32dd9131cacbd8367baac4cdce752d7f0207e4b86bfa3c3182cae8e7d', 'dist/index/circuit.json': '300e1da00d0fd55563e730e58af7a33664b25be90b24aba92f6fec9b714760ac'}

class PublicBaseline(unittest.TestCase):
    def test_known_public_revision_and_bytes(self):
        metadata = json.loads((FIXTURE / 'provenance.json').read_text())
        self.assertEqual(metadata['revision'], '1233ccdf803a1221820f28eabf4791b4a7cfe90e')
        self.assertEqual(metadata['files'], HASHES)
        for path, expected in HASHES.items():
            self.assertEqual(hashlib.sha256((FIXTURE / path).read_bytes()).hexdigest(), expected, path)
