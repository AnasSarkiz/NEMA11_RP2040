#!/usr/bin/env python3
"""Freeze the verified genuine motor-only study, not a completed PCB assembly."""
import hashlib,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'artifacts/requirements/direct-motor-bolts'
OUT=ROOT/'prototypes/motor-bolt-study-0.1.0'
subprocess.run(['python3','scripts/verify_motor_bolt_study.py'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
relative='artifacts/requirements/direct-motor-bolts/motor-bolt-study.circuit.json'
source=(ROOT/relative).read_bytes()
revision=subprocess.check_output(['git','log','-n','1','--format=%H','--',relative],cwd=ROOT,text=True).strip()
for path in [relative,'examples/motor-bolt-study.circuit.tsx','config/direct-motor-bolt-mounting.json','docs/direct-motor-bolts.md']:
    assert subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT)==(ROOT/path).read_bytes(),path+' differs from the committed study'
OUT.mkdir(exist_ok=True)
if (OUT/'package-verification.json').exists():
    proof=json.loads((OUT/'package-verification.json').read_text())
    assert (OUT/'index.circuit.json').read_bytes()==source and proof['source_milestone_commit']==revision
    print('Preserved immutable motor-only prototype 0.1.0');raise SystemExit(0)
(OUT/'index.circuit.json').write_bytes(source)
package=dict(name='@tsci/AnasSarkiz.NEMA11_RP2040_Motor_Bolt_Study',version='0.1.0',main='index.circuit.json',
             description='Original OEM NEMA11 motor-only study: four existing rear bolt axes at 23 mm nominal. No carrier, PCB attachment or selected replacement hardware. NOT fabrication ready',
             type='module',private=False,repository=dict(type='git',url='https://github.com/AnasSarkiz/NEMA11_RP2040.git'))
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n')
(OUT/'tscircuit.config.json').write_text(json.dumps(dict(includeBoardFiles=['index.circuit.json'],previewComponentPath='index.circuit.json'),indent=2)+'\n')
blob=f'https://github.com/AnasSarkiz/NEMA11_RP2040/blob/{revision}/'
raw=f'https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/{revision}/'
(OUT/'README.md').write_text(f'''# NEMA11 existing motor bolt study\n\nThe current requirement is a PCB mounted directly using the motor's existing\ncase-bolt locations, **without a custom carrier, case clamp or enclosure**.\nThis package contains only the genuine, unchanged STEPPERONLINE\n11HS12-0674S motor in its original OEM coordinates. It adds no PCB, carrier,\nrear shaft, new motor holes or invented replacement bolts.\n\nThe original STEP shows four rear bolt heads on a nominal **23 × 23 mm square**,\nat X/Y = ±11.5 mm. Their modeled heads have nominal Ø4 mm cylindrical surfaces.\nThe front drawing's M2.5 threads do not specify the rear case-bolt thread or\nlength. Actual bolts, engagement, motor clamping, insulation/support and final\nPCB hole/tool dimensions remain to be verified.\n\n![OEM rear bolt view]({raw}artifacts/requirements/direct-motor-bolts/OEM-rear-bolt-view.png)\n\nThe historical 25 mm carrier PCB is 1.414 mm off each actual motor bolt axis\nand **fails** the direct-mount alignment check. Its zero-error electrical\nchecks do not qualify a new PCB layout.\n\n[Native CLI motor GLB]({blob}artifacts/requirements/direct-motor-bolts/OEM-motor-native.glb) ·\n[actual native 3D verification]({blob}artifacts/requirements/direct-motor-bolts/native-motor-study-verification.json) ·\n[STEP bolt inspection]({blob}artifacts/requirements/direct-motor-bolts/nominal-step-bolt-audit.json) ·\n[current mounting requirements]({blob}docs/direct-motor-bolts.md).\n\nNative GLB bounds match the original STEP within 0.05 mm. Original lead stubs\nand front shaft remain intact. This is a **mechanical-only inspection study**,\nnot a validated direct-mount PCB or fabrication release.\n''')
verification=json.loads((F/'native-motor-study-verification.json').read_text())
proof=dict(package=package['name'],version=package['version'],source_milestone_commit=revision,
           scope='Verified original OEM motor-only native study; PCB mounting redesign incomplete',
           circuit_sha256=hashlib.sha256(source).hexdigest(),native_CAD_models=1,
           original_STEP_sha256=verification['original_OEM_assets'][1]['sha256'],
           native_GLB_sha256=verification['native_GLB_sha256'],
           maximum_STEP_bbox_deviation_mm=verification['maximum_STEP_bbox_deviation_mm'],
           nominal_existing_rear_bolt_axes_verified=True,nominal_bolt_pitch_mm=23,
           PCB_included=False,carrier_included=False,rear_bolt_thread_or_length_assumed=False,
           direct_PCB_attachment_validated=False,registry_published=False,manufacturing_release=False)
(OUT/'package-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Prepared verified motor-only native prototype; actual CLI build and publication pending')
