#!/usr/bin/env python3
"""Prepare a separate native tscircuit subsystem package; never publish implicitly."""
import hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'prototypes/rp2040-core'
board_path = ROOT/'artifacts/rp2040-pcb/board.circuit.json'
board = json.loads(board_path.read_text())
base = json.loads((ROOT/'artifacts/rp2040-core/core.circuit.json').read_text())
schematic = json.loads((ROOT/'artifacts/rp2040-core/core-schematic.circuit.json').read_text())
assert schematic[:len(base)] == base
sha = hashlib.sha256(board_path.read_bytes()).hexdigest()
for name in ['native-drc.json','independent-copper-audit.json','clock-layout-audit.json','nominal-assembly-audit.json','3d-export-verification.json','independent-cam-audit.json']:
    proof = json.loads((board_path.parent/name).read_text())
    assert proof['circuit_sha256'] == sha, name
    if name == 'native-drc.json':
        assert proof['subsystem_internal_drc_pass'] and len(proof['errors']) == 15
    elif 'errors' in proof:
        assert not proof['errors'], name
assert (board_path.parent/'native-gerber-shorts.txt').read_text().strip() == 'No shorts detected in board.circuit.json'
# All electrical, physical and CAD records in the source subsystem must survive.
# Extra routed copper is native data; only existing schematic presentation is appended.
for record in base:
    assert record in board, record['type']
combined = board + schematic[len(base):]
OUT.mkdir(parents=True,exist_ok=True)
path = OUT/'index.circuit.json'
path.write_text(json.dumps(combined,separators=(',',':'))+'\n')
package = {'name':'NEMA11_RP2040_MCU_Prototype','version':'0.1.0',
           'description':'Native tscircuit RP2040 subsystem PCB prototype; incomplete NEMA11 controller, NOT fabrication ready',
           'main':'index.circuit.json','type':'module','private':False,
           'repository':{'type':'git','url':'https://github.com/AnasSarkiz/NEMA11_RP2040.git'}}
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n')
config = {'includeBoardFiles':['index.circuit.json'],'previewComponentPath':'index.circuit.json'}
(OUT/'tscircuit.config.json').write_text(json.dumps(config,indent=2)+'\n')
proof = {'package':package['name'],'version':package['version'], 'scope':'MCU subsystem prototype only',
         'circuit_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'routed_board_sha256':sha,
         'source_board_records_preserved':True,'schematic_sheets':3,
         'source_repository':'https://github.com/AnasSarkiz/NEMA11_RP2040',
         'registry_published':False,'publication_blocker':'Cloud policy denies registry-api.tscircuit.com; no CLI authorization URL issued',
         'manufacturing_release':False}
revision = subprocess.check_output(['git','log','-n','1','--format=%H','--','artifacts/rp2040-pcb/board.circuit.json'],cwd=ROOT,text=True).strip()
committed = subprocess.check_output(['git','show',revision+':artifacts/rp2040-pcb/board.circuit.json'],cwd=ROOT)
assert hashlib.sha256(committed).hexdigest() == sha, 'Commit the checked PCB milestone before staging publication'
proof['source_milestone_commit'] = revision
(OUT/'package-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'prepared':str(OUT.relative_to(ROOT)),'native_records':len(combined),'registry_published':False}))
