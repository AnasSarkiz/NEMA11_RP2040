#!/usr/bin/env python3
"""Freeze the committed native routed review; never rewrite older prototypes."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];F=ROOT/'artifacts/compact-six-layer';OUT=ROOT/'prototypes/compact-six-layer-0.4.0'
subprocess.run(['python3','scripts/verify_compact_six_layer.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
relative='artifacts/compact-six-layer/assembly.circuit.json';data=(ROOT/relative).read_bytes();revision=subprocess.check_output(['git','log','-n','1','--format=%H','--',relative],cwd=ROOT,text=True).strip();assert subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)==data
records=json.loads(data);snapshot=(json.dumps(records,separators=(',',':'))+'\n').encode();OUT.mkdir(parents=True,exist_ok=True);target=OUT/'index.circuit.json'
if (OUT/'package-verification.json').exists():
 existing=json.loads((OUT/'package-verification.json').read_text());assert target.read_bytes()==snapshot and existing['source_milestone_commit']==revision and existing['version']=='0.4.0';print('Preserved immutable prototype 0.4.0; rebuild dist separately if needed');raise SystemExit(0)
if target.exists():assert target.read_bytes()==snapshot,'Never rewrite a published prototype'
target.write_bytes(snapshot)
package=dict(name='@tsci/AnasSarkiz.NEMA11_RP2040_Compact_Prototype',version='0.4.0',description='Routed 28 mm six-layer four-hole all-top prototype: zero native copper DRC/opens/shorts; six A4 sheets and native 3D. USB/carrier/factory/hardware qualification incomplete; NOT FABRICATION READY',main='index.circuit.json',type='module',private=False,repository=dict(type='git',url='https://github.com/AnasSarkiz/NEMA11_RP2040.git'))
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n');(OUT/'tscircuit.config.json').write_text(json.dumps(dict(includeBoardFiles=['index.circuit.json'],previewComponentPath='index.circuit.json'),indent=2)+'\n')
readme=(F/'README.md').read_text().replace('../../docs/compact-six-layer.md',f'https://github.com/AnasSarkiz/NEMA11_RP2040/blob/{revision}/docs/compact-six-layer.md').replace('](milestone-verification.json)',f'](https://github.com/AnasSarkiz/NEMA11_RP2040/blob/{revision}/artifacts/compact-six-layer/milestone-verification.json)')
(OUT/'README.md').write_text(readme)
proof=json.loads((F/'milestone-verification.json').read_text());receipt={**proof,'package':package['name'],'version':'0.4.0','source_milestone_commit':revision,'circuit_sha256':hashlib.sha256(snapshot).hexdigest(),'source_board_sha256':proof['circuit_sha256'],'registry_published':False}
(OUT/'package-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Prepared immutable routed native prototype 0.4.0 from '+revision)
