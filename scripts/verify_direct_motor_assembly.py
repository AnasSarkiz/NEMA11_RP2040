#!/usr/bin/env python3
"""Verify the current native GLB and original STEP poses without a carrier.

This is a geometry/export check. It does not certify clamp hardware, tolerances,
component collisions, or the electrical layout.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--folder', type=Path, default=ROOT / 'artifacts/compact-six-layer')
args = parser.parse_args()
folder = args.folder
board_bytes = (folder / 'board.circuit.json').read_bytes()
assembly_bytes = (folder / 'assembly.circuit.json').read_bytes()
records = json.loads(assembly_bytes)
board = json.loads(board_bytes)
assert records[:len(board)] == board, 'Assembly must include the exact current PCB'
assert not any('CARRIER' in e.get('name', '') for e in records), 'Carrier is prohibited'
names = {e['source_component_id']: e['name'] for e in records if e['type'] == 'source_component'}
pcbs = {e['pcb_component_id']: e for e in records if e['type'] == 'pcb_component'}
mounts = json.loads((ROOT / 'config/compact-motor-bolts.json').read_text())['mounts']
holes = [e for e in board if e['type'] == 'pcb_hole' and not e.get('pcb_component_id')]
assert len(holes) == 4
assert all(any(h['x'] == m['x'] and h['y'] == m['y'] and h['hole_diameter'] == m['diameter'] for h in holes) for m in mounts)
original = json.loads((ROOT / 'artifacts/requirements/motor-originals.json').read_text())
assert hashlib.sha256((ROOT / 'imports/motor/11HS12-0674S.step').read_bytes()).hexdigest() == original['STEP_sha256']
expected, cache, invalid = {}, {}, []
for e in records:
    if e['type'] != 'cad_component' or not e.get('model_step_url'):
        continue
    pcb = pcbs.get(e.get('pcb_component_id'))
    if pcb and pcb.get('do_not_place'):
        continue
    if pcb:
        assert pcb['layer'] == 'top', 'All fitted components must be on top'
    name = names[e['source_component_id']]
    local = ROOT / 'imports' / e['model_step_url'].split('/imports/')[1]
    if local not in cache:
        cache[local] = cq.importers.importStep(str(local)).val()
    shape = cache[local]
    if not shape.isValid():
        invalid.append(name)
    origin = e.get('model_origin_position', dict(x=0, y=0, z=0))
    shape = shape.translate(tuple(-origin[k] for k in 'xyz'))
    for axis, vector in [('x', (1, 0, 0)), ('y', (0, 1, 0)), ('z', (0, 0, 1))]:
        if e['rotation'][axis]:
            shape = shape.rotate((0, 0, 0), vector, e['rotation'][axis])
    shape = shape.translate(tuple(e['position'][k] for k in 'xyz'))
    b = shape.BoundingBox()
    expected[name] = [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]
assert len(expected) == 77 and 'OEM_11HS12_0674S' in expected
motor = next(e for e in records if e['type'] == 'cad_component' and names[e['source_component_id']] == 'OEM_11HS12_0674S')
assert motor['rotation'] == dict(x=0, y=0, z=90) and motor['position']['x'] == motor['position']['y'] == 0
# Rotation maps this square bolt pattern onto itself.
assert all(any(abs(-m['y']-h['x']) < 1e-6 and abs(m['x']-h['y']) < 1e-6 for h in holes) for m in mounts)
data = (folder / 'development-assembly.glb').read_bytes()
assert data[:4] == b'glTF' and struct.unpack_from('<I', data, 8)[0] == len(data)
length, kind = struct.unpack_from('<II', data, 12)
assert kind == 0x4e4f534a
gltf = json.loads(data[20:20+length])
checked, errors = [], []
for node in gltf['nodes']:
    name = node.get('name')
    if name not in expected:
        continue
    assert not any(k in node for k in ['matrix', 'rotation', 'scale'])
    accessors = [gltf['accessors'][p['attributes']['POSITION']] for p in gltf['meshes'][node['mesh']]['primitives']]
    translation = node.get('translation', [0, 0, 0])
    lo = [min(a['min'][i] for a in accessors)+translation[i] for i in range(3)]
    hi = [max(a['max'][i] for a in accessors)+translation[i] for i in range(3)]
    actual = [-hi[0], lo[2], lo[1], -lo[0], hi[2], hi[1]]
    delta = max(abs(a-b) for a, b in zip(actual, expected[name]))
    checked.append(dict(part=name, maximum_STEP_bbox_deviation_mm=delta))
    if delta > .05:
        errors.append(dict(part=name, bbox_deviation_mm=delta))
assert len(checked) == 77 and {e['part'] for e in checked} == set(expected)
report = dict(scope='Current PCB and OEM motor native GLB versus 77 original STEP poses; geometry/export only',
              PCB_sha256=hashlib.sha256(board_bytes).hexdigest(),
              assembly_sha256=hashlib.sha256(assembly_bytes).hexdigest(),
              native_GLB_sha256=hashlib.sha256(data).hexdigest(), models_checked=len(checked),
              carrier_present=False, motor_bolt_axis_alignment_pass=True,
              nominal_motor_to_PCB_bottom_gap_mm=-.8-expected['OEM_11HS12_0674S'][5],
              original_supplier_STEP_invalid_parts=invalid,
              maximum_STEP_bbox_deviation_mm=max(e['maximum_STEP_bbox_deviation_mm'] for e in checked),
              native_geometry_bounds_pass=not errors, current_full_PCB_DRC_and_hardware_qualified=False,
              motor_original_wire_stubs_extend_outside_frame=True,
              final_harness_termination_and_frame_fit_qualified=False,
              manufacturing_release=False, parts=checked, errors=errors)
(folder / 'current-assembly-geometry.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k: v for k, v in report.items() if k not in ['parts']}))
raise SystemExit(bool(errors))
