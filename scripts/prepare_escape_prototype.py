#!/usr/bin/env python3
"""Freeze the committed, explicitly partial compact escape checkpoint."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'artifacts/compact-escape';OUT=ROOT/'prototypes/compact-escape-0.2.0'
subprocess.run(['/workspace/.venvs/nema11-cad/bin/python','scripts/verify_compact_escape.py'],cwd=ROOT,check=True)
relative='artifacts/compact-escape/assembly.circuit.json';data=(ROOT/relative).read_bytes()
revision=subprocess.check_output(['git','log','-n','1','--format=%H','--',relative],cwd=ROOT,text=True).strip()
assert subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)==data
records=json.loads(data);snapshot=(json.dumps(records,separators=(',',':'))+'\n').encode()
OUT.mkdir(exist_ok=True,parents=True);p=OUT/'index.circuit.json'
if p.exists():assert p.read_bytes()==snapshot,'Never rewrite a published prototype snapshot'
p.write_bytes(snapshot)
package=dict(name='@tsci/AnasSarkiz.NEMA11_RP2040_Compact_Prototype',version='0.2.0',description='PARTIALLY ROUTED 28 mm all-top controller: checked crystal/short USB escapes, six A4 schematics and native motor/carrier 3D; 58 nets remain open; DO NOT FABRICATE',main='index.circuit.json',type='module',private=False,repository=dict(type='git',url='https://github.com/AnasSarkiz/NEMA11_RP2040.git'))
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n')
(OUT/'tscircuit.config.json').write_text(json.dumps(dict(includeBoardFiles=['index.circuit.json'],previewComponentPath='index.circuit.json'),indent=2)+'\n')
(OUT/'README.md').write_bytes((SRC/'README.md').read_bytes())
proof=json.loads((SRC/'escape-verification.json').read_text())
receipt=dict(package=package['name'],version='0.2.0',scope=proof['scope'],source_milestone_commit=revision,circuit_sha256=hashlib.sha256(snapshot).hexdigest(),source_components=94,electrical_components=92,physical_ports=340,native_models=84,schematic_sheets=6,disconnected_controller_nets=58,native_port_connectivity_findings=270,native_DRC_pass=False,full_controller_routing_complete=False,registry_published=False,manufacturing_release=False)
(OUT/'package-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Prepared immutable native compact escape prototype 0.2.0 from '+revision)
