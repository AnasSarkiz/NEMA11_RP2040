#!/usr/bin/env python3
"""Freeze a committed four-hole UNROUTED source/3D prototype, never manufacturing data."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'artifacts/compact-four-mounts';OUT=ROOT/'prototypes/compact-four-mounts-0.3.0'
subprocess.run(['python3','scripts/verify_four_mounts.py','--assembly'],cwd=ROOT,check=True)
relative='artifacts/compact-four-mounts/assembly.circuit.json';data=(ROOT/relative).read_bytes()
revision=subprocess.check_output(['git','log','-n','1','--format=%H','--',relative],cwd=ROOT,text=True).strip()
assert subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)==data
records=json.loads(data);snapshot=(json.dumps(records,separators=(',',':'))+'\n').encode()
OUT.mkdir(exist_ok=True,parents=True);p=OUT/'index.circuit.json'
if p.exists():assert p.read_bytes()==snapshot,'Never rewrite a published prototype snapshot'
p.write_bytes(snapshot)
package=dict(name='@tsci/AnasSarkiz.NEMA11_RP2040_Compact_Prototype',version='0.3.0',description='UNROUTED four-hole 28 mm all-top controller: buzzer omitted with user authorization; 6 connected A4 sheets and native motor/carrier 3D; NOT FABRICATION READY',main='index.circuit.json',type='module',private=False,repository=dict(type='git',url='https://github.com/AnasSarkiz/NEMA11_RP2040.git'))
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n')
(OUT/'tscircuit.config.json').write_text(json.dumps(dict(includeBoardFiles=['index.circuit.json'],previewComponentPath='index.circuit.json'),indent=2)+'\n')
(OUT/'README.md').write_bytes((SRC/'README.md').read_bytes())
proof=json.loads((SRC/'assembly-milestone-verification.json').read_text())
receipt=dict(package=package['name'],version='0.3.0',scope='Validated UNROUTED four-hole compact source, placement, connected A4 sheets and native motor/carrier proposal 3D',source_milestone_commit=revision,circuit_sha256=hashlib.sha256(snapshot).hexdigest(),source_components=88,electrical_components=86,physical_ports=326,PCB_mount_count=4,PCB_mount_pitch_mm=25,PCB_hole_diameter_mm=1.8,fitted_components_top=76,native_models=78,schematic_sheets=6,controller_nets=61,disconnected_controller_nets=61,native_DRC_pass=False,full_controller_routing_complete=False,registry_published=False,manufacturing_release=False)
(OUT/'package-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('Prepared immutable four-hole native prototype 0.3.0 from '+revision)
