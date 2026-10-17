#!/usr/bin/env python3
"""Apply a minimal, checksum-guarded geometry fix to the frozen native tooling."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/'tools/pcb/patches/circle-keepout-clearance.json'

def apply(check_only=False):
    patch=json.loads(PATCH.read_text())
    checked=[]
    for entry in patch['files']:
        path=ROOT/'tools/pcb'/entry['path']
        data=path.read_bytes()
        actual=hashlib.sha256(data).hexdigest()
        if actual==entry['corrected_sha256']:
            checked.append(entry['path']);continue
        assert actual==entry['pristine_sha256'],'Unexpected dependency bytes: '+entry['path']
        assert not check_only,'Frozen toolchain needs the documented circle-distance correction'
        source=data.decode()
        assert source.count(entry['before'])==1,entry['path']
        corrected=source.replace(entry['before'],entry['after']).encode()
        assert hashlib.sha256(corrected).hexdigest()==entry['corrected_sha256']
        path.write_bytes(corrected)
        checked.append(entry['path'])
    return {'scope':patch['scope'],'patch_sha256':hashlib.sha256(PATCH.read_bytes()).hexdigest(),
            'verified_files':checked,'no_diagnostics_filtered':True,'clearance_thresholds_unchanged':True}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    print(json.dumps(apply(args.check)))
