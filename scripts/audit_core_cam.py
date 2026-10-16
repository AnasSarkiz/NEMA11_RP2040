#!/usr/bin/env python3
"""Review-only native CAM roundtrip, independently parsed from actual files."""
import hashlib, json
from pathlib import Path
from shapely.geometry import Point
from shapely.ops import unary_union
from pcb_geometry import Copper, LAYERS, pad_shape
from cam_geometry import gerber, drill

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'artifacts/rp2040-pcb'
CAM = OUT/'review-cam'
board = OUT/'board.circuit.json'
records = json.loads(board.read_text())
receipt = json.loads((OUT/'review-cam-export.json').read_text())
sha = hashlib.sha256(board.read_bytes()).hexdigest()
assert receipt['circuit_sha256'] == sha
errors, files, geometry = [], {}, {}
assert {p.name for p in CAM.iterdir() if p.suffix in ['.gbr','.drl']} == {e['name'] for e in receipt['files']}
for entry in receipt['files']:
    path = CAM/entry['name']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
    if path.suffix == '.gbr':
        shape, count, notices = gerber(path)
        geometry[path.stem] = shape
        files[path.name] = {'sha256': entry['sha256'], 'objects': count, 'area_mm2': shape.area, **notices}
    elif path.suffix == '.drl':
        holes, hole_shapes, notices = drill(path)
        files[path.name] = {'sha256': entry['sha256'], **notices}
        assert path.name == 'drill-L1-L4.drl'
        assert 'TF.FileFunction,Plated,1,4,PTH' in path.read_text()
        expected = [e for e in records if e['type'] == 'pcb_via']
        unmatched = list(hole_shapes)
        for via in expected:
            matches = [i for i, shape in enumerate(unmatched) if shape.centroid.distance(Point(via['x'],via['y'])) <= .0001
                       and abs(shape.bounds[2]-shape.bounds[0]-via['hole_diameter']) <= 1e-6]
            if len(matches) != 1:
                errors.append({'drill_mismatch': via['pcb_via_id'], 'matches': len(matches)})
            else:
                unmatched.pop(matches[0])
        if unmatched:
            errors.append({'extra_drills': len(unmatched)})
        if len(hole_shapes) != len(expected):
            errors.append({'drill_count': [len(hole_shapes),len(expected)]})
    else:
        raise ValueError('Unrecognized CAM file')

copper = Copper(records)
elements = copper.elements()
comparisons = []
for layer, filename in zip(LAYERS, ['F_Cu','In1_Cu','In2_Cu','B_Cu']):
    expected = unary_union([shapes[layer] for _, _, shapes in elements if layer in shapes]).difference(holes)
    actual = geometry[filename].difference(holes)
    extra = actual.difference(expected.buffer(.003)).area
    missing = expected.difference(actual.buffer(.003)).area
    row = {'layer': layer, 'parsed_mm2': actual.area, 'source_mm2': expected.area,
           'symmetric_difference_mm2': actual.symmetric_difference(expected).area,
           'extra_beyond_3um_mm2': extra, 'missing_beyond_3um_mm2': missing}
    comparisons.append(row)
    if extra > 1e-5 or missing > 1e-5:
        errors.append({'copper_CAM_mismatch': row})

paste = [e for e in records if e['type'] == 'pcb_solder_paste']
for layer, filename in [('top','F_Paste'), ('bottom','B_Paste')]:
    expected = unary_union([pad_shape(e) for e in paste if e['layer'] == layer])
    actual = geometry[filename]
    if actual.difference(expected.buffer(.003)).area > 1e-5 or expected.difference(actual.buffer(.003)).area > 1e-5:
        errors.append({'paste_CAM_mismatch': layer})
# Expose unresolved manufacturing presentation, rather than calling a copper
# roundtrip pass a complete manufacturing/CAM approval.
silk_overlap = geometry['F_SilkScreen'].intersection(geometry['F_Mask']).area
report = {'scope': 'Actual native MCU development CAM files only; not production order data',
          'circuit_sha256': sha, 'export_manifest_sha256': hashlib.sha256((OUT/'review-cam-export.json').read_bytes()).hexdigest(),
          'parser': 'Gerbonara 1.5.0 with explicit right-angle LR compatibility',
          'files': files, 'copper_comparison': comparisons,
          'drill_count': len(hole_shapes), 'errors': errors, 'copper_drill_paste_roundtrip_pass': not errors,
          'front_silkscreen_mask_opening_overlap_mm2': silk_overlap,
          'manufacturing_findings': ['Reference silkscreen is crowded; review overlap and board-edge clipping.',
             'MCU exposed-pad via needs approved fill/cap and stencil process or redesign.',
             'Minimum nominal radial via annulus is 0.075 mm; JLCPCB drill and registration capability is unverified.',
             'Full motor controller, motor fit, harness and source parity remain incomplete.'],
          'whole_controller_CAM_pass': False, 'manufacturing_release': False}
(OUT/'independent-cam-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'copper_drill_paste_errors':len(errors),'drills':len(hole_shapes),
                  'silk_opening_overlap_mm2':silk_overlap,'manufacturing_release':False}))
raise SystemExit(bool(errors))
