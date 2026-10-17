#!/usr/bin/env python3
"""Package exact reviewed compact CAM/BOM/CPL; never authorize fabrication."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];F=ROOT/'artifacts/compact-six-layer'
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
proof=json.loads((F/'milestone-verification.json').read_text());assert proof['native_copper_review_pass'] and proof['manufacturing_release'] is False
mount=json.loads((ROOT/'artifacts/requirements/direct-motor-bolts/nominal-step-bolt-audit.json').read_text())
assert mount['PCB_sha256']==proof['circuit_sha256']
files=sorted(list((F/'review-cam').iterdir())+list((F/'assembly-data').iterdir())+[F/name for name in ['milestone-verification.json','schematic-a4.pdf','README.md','electrical-thermal-screen.json','filled-capped-via-policy.json']]+[ROOT/name for name in ['docs/compact-six-layer.md','docs/direct-motor-bolts.md','config/direct-motor-bolt-mounting.json','artifacts/requirements/direct-motor-bolts/nominal-step-bolt-audit.json','artifacts/requirements/direct-motor-bolts/OEM-rear-bolt-view.png']])
entries=[dict(path=str(f.relative_to(ROOT)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files]
manifest=dict(scope='Historical electrical PCB Gerber/BOM/CPL review archive; carrier mount superseded; DO NOT FABRICATE',circuit_sha256=proof['circuit_sha256'],current_mount_requirement='Direct existing motor case-bolts; no carrier or enclosure',PCB_direct_motor_bolt_axis_alignment_pass=mount['PCB_motor_bolt_axis_alignment_pass'],files=entries,manufacturing_release=False)
manifest_bytes=(json.dumps(manifest,indent=2)+'\n').encode();stream=io.BytesIO()
with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for name,data in [(str(f.relative_to(ROOT)),f.read_bytes()) for f in files]+[('review-manifest.json',manifest_bytes)]:
        entry=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16;archive.writestr(entry,data)
outputs={'manufacturing-review-manifest.json':manifest_bytes,'manufacturing-review.zip':stream.getvalue()}
for name,data in outputs.items():
    if a.check:assert (F/name).read_bytes()==data,name+' does not match reviewed source'
    else:(F/name).write_bytes(data)
print(json.dumps(dict(exact_review_archive_verified=True,members=len(entries)+1,manufacturing_release=False)))
