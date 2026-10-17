#!/usr/bin/env python3
"""Record the native CLI checks against the exact current source artifacts."""
import concurrent.futures
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CHECKS=[('source','artifacts/controller/schematic.circuit.json','native-source.txt'),
        ('pin_specification','artifacts/controller/schematic.circuit.json','native-pin-specification.txt'),
        ('netlist','examples/full-controller-netlist.circuit.tsx','native-netlist-tsx.txt'),
        ('schematic-placement','artifacts/controller/schematic.circuit.json','native-schematic-placement.txt')]


def run(item):
    check,path,log=item
    result=subprocess.run(['tsci','check',check,path],cwd=ROOT,capture_output=True,text=True,timeout=180)
    output='artifacts/controller/'+log
    (ROOT/output).write_text(result.stdout+result.stderr)
    return {'check':check,'input':path,'input_sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
            'exit_code':result.returncode,'log':output}


if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(run,CHECKS))
    (ROOT/'artifacts/controller/native-source-checks.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'native_check_exit_codes':{e['check']:e['exit_code'] for e in results}}))
    raise SystemExit(any(e['exit_code'] for e in results))
