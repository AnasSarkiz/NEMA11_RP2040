#!/usr/bin/env python3
"""Compare every actual native controller-only GLB mesh with its STEP pose."""
import argparse,hashlib,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True);a=p.parse_args();f=a.folder;data=(f/'unrouted.circuit.json').read_bytes();source_sha=hashlib.sha256(data).hexdigest();audit=json.loads((f/'nominal-assembly-audit.json').read_text());assert audit['circuit_sha256']==source_sha
expected={r['part']:r['bounds_mm'] for r in audit['parts']};b=(f/'development-controller.glb').read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b);n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);rows=[];errors=[]
for node in g['nodes']:
    if node.get('name') not in expected:continue
    assert not any(k in node for k in ['matrix','rotation','scale'])
    accessors=[g['accessors'][p['attributes']['POSITION']] for p in g['meshes'][node['mesh']]['primitives']];t=node.get('translation',[0,0,0]);lo=[min(v['min'][i] for v in accessors)+t[i] for i in range(3)];hi=[max(v['max'][i] for v in accessors)+t[i] for i in range(3)];actual=[-hi[0],lo[2],lo[1],-lo[0],hi[2],hi[1]];deviation=max(abs(x-y) for x,y in zip(actual,expected[node['name']]))
    rows.append(dict(part=node['name'],native_GLB_bounds_mm=actual,STEP_bound_deviation_mm=deviation))
    if deviation>.05:errors.append(dict(part=node['name'],maximum_STEP_deviation_mm=deviation))
assert len(rows)==len(expected) and {r['part'] for r in rows}==set(expected)
report=dict(scope='Actual native controller-only GLB versus every fitted STEP pose; hardware/carrier absent',source_sha256=source_sha,native_GLB_sha256=hashlib.sha256(b).hexdigest(),models_checked=len(rows),parts=rows,errors=errors,passed=not errors,manufacturing_release=False);(f/'native-controller-model-bounds.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(models_checked=len(rows),maximum_STEP_bound_deviation_mm=max(r['STEP_bound_deviation_mm'] for r in rows),errors=len(errors))));raise SystemExit(bool(errors))
