#!/usr/bin/env python3
"""Package exact review manufacturing files and verify each archived member."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
check=argparse.ArgumentParser()
check.add_argument('--check',action='store_true')
args=check.parse_args()
files=sorted(list((ROOT/'artifacts/controller-pcb/review-cam').glob('*'))+
             list((ROOT/'artifacts/controller-pcb/assembly-data').glob('*.csv'))+
             [ROOT/'docs/manufacturing-requirements.md',ROOT/'docs/full-controller-pcb.md',
              ROOT/'artifacts/controller-pcb/milestone-verification.json',ROOT/'artifacts/controller/schematic-a4.pdf'])
manifest={'scope':'Exact development review Gerbers, BOM/CPL, six-page schematic and process requirements; DO NOT FABRICATE',
          'manufacturing_release':False,
          'files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,
                    'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
mp=ROOT/'artifacts/controller-pcb/manufacturing-review-manifest.json'
serialized=(json.dumps(manifest,indent=2)+'\n').encode()
archive=ROOT/'artifacts/controller-pcb/manufacturing-review.zip'
if args.check:
    assert mp.read_bytes()==serialized,'Review manifest is stale'
else:
    mp.write_bytes(serialized)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files+[mp]:
            info=zipfile.ZipInfo(str(p.relative_to(ROOT)),(2026,10,17,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes())
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist())=={str(p.relative_to(ROOT)) for p in files+[mp]}
    for p in files+[mp]:assert z.read(str(p.relative_to(ROOT)))==p.read_bytes(),str(p)
print('Exact review archive: 23 members verified; manufacturing_release=false')
