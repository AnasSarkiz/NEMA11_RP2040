#!/usr/bin/env python3
"""Freeze a mounting-documentation patch release of the validated 0.4 copper.

No component, placement, copper, model or fabrication-status change is implied.
Actual CLI build, lossless compaction and remote verification remain required.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'prototypes/compact-six-layer-0.4.0'
OUT=ROOT/'prototypes/compact-six-layer-0.4.1'
subprocess.run(['python3','scripts/verify_compact_six_layer.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
review=json.loads((ROOT/'artifacts/requirements/mounting-review/verification.json').read_text())
base=json.loads((OLD/'package-verification.json').read_text())
assert review['circuit_sha256']==base['source_board_sha256']
assert review['native_mount_geometry_pass'] and not review['manufacturing_release']
for entry in review['inputs']+review['drawings']:
    assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
relative='artifacts/requirements/mounting-review/verification.json'
revision=subprocess.check_output(['git','log','-n','1','--format=%H','--',relative],cwd=ROOT,text=True).strip()
assert subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)==(ROOT/relative).read_bytes()
assert not subprocess.check_output(['git','status','--porcelain','--','docs/four-mount-compact.md','artifacts/requirements/mounting-review'],cwd=ROOT,text=True).strip()
snapshot=(OLD/'index.circuit.json').read_bytes()
OUT.mkdir(exist_ok=True)
if (OUT/'package-verification.json').exists():
    proof=json.loads((OUT/'package-verification.json').read_text())
    assert (OUT/'index.circuit.json').read_bytes()==snapshot and proof['mounting_documentation_commit']==revision and proof['version']=='0.4.1'
    print('Preserved immutable 0.4.1 mounting-review package')
    raise SystemExit(0)
(OUT/'index.circuit.json').write_bytes(snapshot)
(OUT/'tscircuit.config.json').write_bytes((OLD/'tscircuit.config.json').read_bytes())
package=json.loads((OLD/'package.json').read_text());package['version']='0.4.1'
package['description']='Validated 0.4 routed native PCB/3D plus A4 four-mount comparison; no copper changes. NOT FABRICATION READY'
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n')
link=f'https://github.com/AnasSarkiz/NEMA11_RP2040/blob/{revision}/'
readme=(OLD/'README.md').read_text()+f'''\n\n## Four-mount review, 0.4.1\n\nThis documentation patch retains every native circuit/PCB/3D record from 0.4.0.\nThe [A4 mounting comparison]({link}artifacts/requirements/mounting-review/four-mount-comparison.pdf)\nshows the four PCB holes (25 mm pitch, Ø1.8 mm) separately from the verified\nmotor FRONT threads (23 ±0.15 mm, M2.5). NEMA14's exact 26 mm pitch/Ø3.2 mm\nholes exceed the permitted frame. The complete buzzer circuit remains omitted,\nand all 76 fitted electrical components remain on top.\n\n[Mounting verification]({link}artifacts/requirements/mounting-review/verification.json)\nand [current mounting explanation]({link}docs/four-mount-compact.md)\nretain the unresolved carrier, screw/tool, maximum-tolerance and physical checks.\nThis release does not integrate the optional 68 µF capacitor development variant.\nIt is NOT a fabrication release.\n'''
(OUT/'README.md').write_text(readme)
proof={k:v for k,v in base.items() if k!='native_build_output_formatting'}
proof.update(version='0.4.1',scope='Validated 0.4 routed native PCB/3D with separate A4 four-mount documentation review; no copper or component changes',mounting_documentation_commit=revision,mounting_review_sha256=hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(),unchanged_native_records_from='0.4.0',registry_published=False)
(OUT/'package-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Prepared native 0.4.1 documentation patch; actual CLI build and publication verification pending')
