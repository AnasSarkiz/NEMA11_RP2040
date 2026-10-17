#!/usr/bin/env python3
"""Verify the actual native motor-only GLB, not an invented mounting assembly."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'artifacts/requirements/direct-motor-bolts'
source=F/'motor-bolt-study.circuit.json';records=json.loads(source.read_text())
assert {r['type'] for r in records}=={'cad_component','source_component','source_project_metadata'}
components=[r for r in records if r['type']=='source_component'];cad=[r for r in records if r['type']=='cad_component']
assert len(components)==len(cad)==1 and components[0]['name']=='OEM_11HS12_0674S'
assert cad[0]['source_component_id']==components[0]['source_component_id']
assert all(v==0 for k in ['position','rotation'] for v in cad[0][k].values())
revision='e1c16a078dd10286f883a2b9c0775f5d13a366e7'
assets=[]
for extension,field in [('obj','model_obj_url'),('step','model_step_url')]:
    relative='imports/motor/11HS12-0674S.'+extension
    assert cad[0][field]==f'https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/{revision}/{relative}'
    data=(ROOT/relative).read_bytes()
    assert data==subprocess.check_output(['git','show',revision+':'+relative],cwd=ROOT)
    assets.append(dict(path=relative,sha256=hashlib.sha256(data).hexdigest(),immutable_revision=revision))
original=json.loads((ROOT/'artifacts/requirements/motor-originals.json').read_text())
assert assets[1]['sha256']==original['STEP_sha256']
data=(F/'OEM-motor-native.glb').read_bytes()
assert data[:4]==b'glTF' and struct.unpack_from('<I',data,8)[0]==len(data)
length,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a
gltf=json.loads(data[20:20+length])
nodes=[n for n in gltf['nodes'] if 'mesh' in n]
assert len(nodes)==1 and nodes[0]['name']=='OEM_11HS12_0674S'
node=nodes[0];assert not any(k in node for k in ['matrix','rotation','scale'])
accessors=[gltf['accessors'][p['attributes']['POSITION']] for p in gltf['meshes'][node['mesh']]['primitives']]
translation=node.get('translation',[0,0,0])
lo=[min(a['min'][i] for a in accessors)+translation[i] for i in range(3)]
hi=[max(a['max'][i] for a in accessors)+translation[i] for i in range(3)]
# Native exporter reflects X and swaps Y/Z. The study uses the raw OEM pose.
actual=[-hi[0],lo[2],lo[1],-lo[0],hi[2],hi[1]]
deviation=max(abs(a-b) for a,b in zip(actual,original['bounds_mm']))
assert deviation<=.05,('Native motor geometry differs from OEM STEP',actual,deviation)
assert actual[1]<-34 and actual[2]<-19.9,'Original lead stubs and front shaft must remain in the study'
report=dict(scope='Actual native CLI motor-only 3D export versus original OEM STEP bounds',
            source_example='examples/motor-bolt-study.circuit.tsx',
            source_example_sha256=hashlib.sha256((ROOT/'examples/motor-bolt-study.circuit.tsx').read_bytes()).hexdigest(),
            native_circuit_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            native_GLB_sha256=hashlib.sha256(data).hexdigest(),native_CAD_models=1,
            original_OEM_assets=assets,native_GLB_OEM_coordinates_bbox_mm=actual,
            maximum_STEP_bbox_deviation_mm=deviation,original_leads_and_front_shaft_preserved=True,
            PCB_present=False,carrier_present=False,replacement_bolt_geometry_invented=False,
            direct_PCB_attachment_validated=False,passed=True,manufacturing_release=False)
(F/'native-motor-study-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['original_OEM_assets','native_GLB_OEM_coordinates_bbox_mm']}))
