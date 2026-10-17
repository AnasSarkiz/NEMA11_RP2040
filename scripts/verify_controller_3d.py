#!/usr/bin/env python3
"""Check the actual native GLB geometry against STEP poses and OEM motor bounds."""
import hashlib
import itertools
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'artifacts/controller'
path = folder / 'development-assembly.glb'
data = path.read_bytes()
assert data[:4] == b'glTF' and struct.unpack_from('<I', data, 8)[0] == len(data)
length, kind = struct.unpack_from('<II', data, 12)
assert kind == 0x4e4f534a
gltf = json.loads(data[20:20+length])
audit = json.loads((folder / 'nominal-assembly-audit.json').read_text())
expected = {e['part']: e['bounds_mm'] for e in audit['parts']}
original = json.loads((ROOT / 'artifacts/requirements/motor-originals.json').read_text())
assert hashlib.sha256((ROOT / 'imports/motor/11HS12-0674S.step').read_bytes()).hexdigest() == original['STEP_sha256']
b = original['bounds_mm']
corners = [(-y, x, z-42) for x,y,z in itertools.product([b[0],b[3]], [b[1],b[4]], [b[2],b[5]])]
expected['OEM_11HS12_0674S'] = [min(p[i] for p in corners) for i in range(3)] + [max(p[i] for p in corners) for i in range(3)]
checked, errors = [], []
for node in gltf['nodes']:
    name = node.get('name')
    if name not in expected:
        continue
    assert 'matrix' not in node and 'rotation' not in node and 'scale' not in node
    accessors = [gltf['accessors'][p['attributes']['POSITION']]
                 for p in gltf['meshes'][node['mesh']]['primitives']]
    translation = node.get('translation', [0,0,0])
    lo = [min(a['min'][i] for a in accessors) + translation[i] for i in range(3)]
    hi = [max(a['max'][i] for a in accessors) + translation[i] for i in range(3)]
    # This native exporter reflects scene X and swaps board Y/Z globally.
    actual = [-hi[0],lo[2],lo[1],-lo[0],hi[2],hi[1]]
    delta = max(abs(a-b) for a,b in zip(actual, expected[name]))
    checked.append({'part': name, 'native_GLB_board_coordinates_bbox_mm': actual,
                    'maximum_STEP_bbox_deviation_mm': delta})
    if delta > .05:
        errors.append({'part': name, 'bbox_deviation_mm': delta})
assert {e['part'] for e in checked} == set(expected) and len(checked) == 83
motor = next(e for e in checked if e['part'] == 'OEM_11HS12_0674S')['native_GLB_board_coordinates_bbox_mm']
assert motor[3] > 34 and motor[0] > -14.11, 'Motor lead stubs must exit positive X toward the JST side'
lowest = min(e['bounds_mm'][2] for e in audit['parts'])
report = {'scope': 'Actual native GLB bounds versus 82 fitted supplier STEP poses plus genuine OEM motor',
          'GLB_sha256': hashlib.sha256(data).hexdigest(), 'native_models_checked': 83,
          'scene_to_board_coordinates': {'X': '-glTF.X', 'Y': 'glTF.Z', 'Z': 'glTF.Y'},
          'parts': checked, 'errors': errors, 'passed': not errors,
          'nominal_motor_to_PCB_bottom_gap_mm': -.8-motor[5],
          'nominal_motor_to_lowest_fitted_component_vertical_gap_mm': lowest-motor[5],
          'drawing_maximum_body_to_PCB_bottom_gap_mm': 8.2,
          'motor_lead_stubs_point_toward_JST_side': True,
          'carrier_harness_hardware_included': False, 'manufacturing_release': False}
(folder / 'assembly-geometry-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k != 'parts'}))
raise SystemExit(bool(errors))
