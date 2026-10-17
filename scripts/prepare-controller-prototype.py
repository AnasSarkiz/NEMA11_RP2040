#!/usr/bin/env python3
"""Stage the committed electrical/schematic milestone as a separate native package."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'prototypes/full-controller'
path = ROOT / 'artifacts/controller/schematic.circuit.json'
records = json.loads(path.read_text())
proof = json.loads((path.parent / 'schematic-verification.json').read_text())
assert proof['passed'] and proof['components'] == 92 and proof['physical_pins'] == 341
assert proof['schematic_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
assert not any(e['type'] == 'pcb_trace' for e in records)
revision = subprocess.check_output(['git', 'log', '-n', '1', '--format=%H', '--', str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip()
assert subprocess.check_output(['git', 'show', revision + ':' + str(path.relative_to(ROOT))], cwd=ROOT) == path.read_bytes()
OUT.mkdir(parents=True, exist_ok=True)
serialized = (json.dumps(records, separators=(',', ':')) + '\n').encode()
published = ROOT / 'artifacts/publication/controller-prototype-0.1.0.json'
if published.exists():
    receipt = json.loads(published.read_text())
    remote = next(e for e in receipt['verified_files'] if e['path'] == 'index.circuit.json')
    if receipt['registry_published'] and remote['sha256'] == hashlib.sha256(serialized).hexdigest():
        assert (OUT / 'index.circuit.json').read_bytes() == serialized
        print('Published controller snapshot unchanged; package metadata preserved.')
        raise SystemExit(0)
(OUT / 'index.circuit.json').write_bytes(serialized)
package = {'name': '@tsci/AnasSarkiz.NEMA11_RP2040_Controller_Prototype', 'version': '0.1.0',
           'description': 'Unrouted NEMA11 controller source, six A4 schematics and genuine supplier CAD; NOT fabrication ready',
           'main': 'index.circuit.json', 'type': 'module', 'private': False,
           'repository': {'type': 'git', 'url': 'https://github.com/AnasSarkiz/NEMA11_RP2040.git'}}
(OUT / 'package.json').write_text(json.dumps(package, indent=2) + '\n')
(OUT / 'tscircuit.config.json').write_text(json.dumps({'includeBoardFiles': ['index.circuit.json'],
                                                     'previewComponentPath': 'index.circuit.json'}, indent=2) + '\n')
receipt = {'package': package['name'], 'version': package['version'],
           'scope': 'Unrouted full electrical source and functional schematic prototype',
           'source_milestone_commit': revision, 'source_repository': package['repository']['url'],
           'circuit_sha256': hashlib.sha256(serialized).hexdigest(),
           'source_components': 92, 'physical_ports': 341, 'schematic_sheets': 6,
           'pin_value_parity_verified': True, 'visual_schematic_ERC_verified': True,
           'registry_published': False, 'manufacturing_release': False,
           'limitations': ['No routed copper or complete motor/carrier/harness assembly',
                           'Nine native pin metadata warnings retained',
                           'Original USB STEP validity limitation retained',
                           'Current accuracy, thermal performance, JLC process and stock unqualified']}
(OUT / 'package-verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('Staged separate native full-controller prototype from committed source.')
