#!/usr/bin/env python3
"""Run actual authenticated-install CLI checks without dumping private CLI errors."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/compact-controller'
checks=[]
for check,input_path in [('source','artifacts/compact-controller/schematic.circuit.json'),('pin_specification','artifacts/compact-controller/schematic.circuit.json'),('netlist','examples/compact-controller-netlist.circuit.tsx'),('schematic-placement','artifacts/compact-controller/schematic.circuit.json')]:
 p=ROOT/input_path;result=subprocess.run(['tsci','check',check,input_path],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 log=OUT/('native-'+check+'.txt');log.write_bytes(result.stdout)
 checks.append(dict(check=check,input=input_path,input_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),exit_code=result.returncode,log=str(log.relative_to(ROOT))))
 print(check+': '+str(result.returncode),flush=True)
(OUT/'native-source-checks.json').write_text(json.dumps(checks,indent=2)+'\n');raise SystemExit(any(c['exit_code'] for c in checks))
