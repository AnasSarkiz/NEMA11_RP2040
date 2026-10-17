#!/usr/bin/env python3
"""Run actual authenticated-install CLI checks without dumping private CLI errors."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=sys.argv[sys.argv.index('--folder')+1] if '--folder' in sys.argv else 'artifacts/compact-controller';OUT=ROOT/folder
checks=[]
for check,input_path in [('source',folder+'/schematic.circuit.json'),('pin_specification',folder+'/schematic.circuit.json'),('netlist','examples/compact-controller-netlist.circuit.tsx'),('schematic-placement',folder+'/schematic.circuit.json')]:
 p=ROOT/input_path;result=subprocess.run(['tsci','check',check,input_path],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 log=OUT/('native-'+check+'.txt');log.write_bytes(result.stdout)
 checks.append(dict(check=check,input=input_path,input_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),exit_code=result.returncode,log=str(log.relative_to(ROOT))))
 print(check+': '+str(result.returncode),flush=True)
(OUT/'native-source-checks.json').write_text(json.dumps(checks,indent=2)+'\n');raise SystemExit(any(c['exit_code'] for c in checks))
