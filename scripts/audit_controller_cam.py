#!/usr/bin/env python3
"""Independently parse native full-controller CAM, including component slots/NPTH."""
import hashlib
import json
from pathlib import Path
from shapely.ops import unary_union
from pcb_geometry import Copper, LAYERS, pad_shape
from cam_geometry import gerber, drill

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/controller-pcb'
CAM = OUT / 'review-cam'
path = OUT / 'board.circuit.json'
records = json.loads(path.read_text())
receipt = json.loads((OUT / 'review-cam-export.json').read_text())
sha = hashlib.sha256(path.read_bytes()).hexdigest()
assert receipt['circuit_sha256'] == sha
errors, geometry, files, drill_shapes = [], {}, {}, []
for entry in receipt['files']:
    source = CAM / entry['name']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256']
    if source.suffix == '.gbr':
        shape, count, notices = gerber(source)
        geometry[source.stem] = shape
        files[source.name] = {'objects':count,'area_mm2':shape.area,**notices}
    elif source.suffix == '.drl':
        holes, shapes, notices = drill(source)
        drill_shapes.extend(shapes)
        files[source.name] = notices
        plated = source.name != 'drill_npth.drl'
        expected = [e for e in records if e['type'] in (['pcb_via','pcb_plated_hole'] if plated else ['pcb_hole'])]
        unmatched = list(shapes)
        for e in expected:
            hole = {**e,'shape':'circle' if e['type'] in ['pcb_via','pcb_hole'] else e['shape'],
                    'width':e.get('hole_width',e.get('hole_diameter')), 'height':e.get('hole_height',e.get('hole_diameter'))}
            target = pad_shape(hole)
            matches = [i for i,s in enumerate(unmatched) if s.hausdorff_distance(target) < .001]
            if len(matches) != 1:
                errors.append({'drill_mismatch':e[e['type']+'_id'],'matches':len(matches)})
            else:
                unmatched.pop(matches[0])
        if unmatched:
            errors.append({'extra_drills':source.name,'count':len(unmatched)})
        if plated and 'TF.FileFunction,Plated,1,4,PTH' not in source.read_text():
            errors.append({'missing_plated_drill_attribute':source.name})
        if not plated and 'TF.FileFunction,NonPlated,1,4,NPTH' not in source.read_text():
            errors.append({'missing_NPTH_drill_attribute':source.name})
    else:
        raise ValueError(source.name)
holes = unary_union(drill_shapes)
elements = Copper(records).elements()
comparisons = []
for layer, name in zip(LAYERS,['F_Cu','In1_Cu','In2_Cu','B_Cu']):
    expected = unary_union([s[layer] for _,_,s in elements if layer in s]).difference(holes)
    actual = geometry[name].difference(holes)
    extra = actual.difference(expected.buffer(.003)).area
    missing = expected.difference(actual.buffer(.003)).area
    row = {'layer':layer,'source_mm2':expected.area,'CAM_mm2':actual.area,
           'extra_beyond_3um_mm2':extra,'missing_beyond_3um_mm2':missing}
    comparisons.append(row)
    if extra > 1e-5 or missing > 1e-5:
        errors.append({'copper_CAM_mismatch':row})
for layer,name in [('top','F_Paste'),('bottom','B_Paste')]:
    expected = unary_union([pad_shape(e) for e in records if e['type']=='pcb_solder_paste' and e['layer']==layer])
    actual = geometry[name]
    if actual.difference(expected.buffer(.003)).area > 1e-5 or expected.difference(actual.buffer(.003)).area > 1e-5:
        errors.append({'paste_CAM_mismatch':layer})
silk = {side:geometry[side+'_SilkScreen'].intersection(geometry[side+'_Mask']).area for side in ['F','B']}
for side,area in silk.items():
    if area > 1e-5:
        errors.append({'silkscreen_over_mask_opening':side,'area_mm2':area})
report = {'scope':'Actual native full-controller review CAM; manufacturing qualification remains separate',
          'circuit_sha256':sha,'parser':'Gerbonara 1.5 with explicit LR/G85 compatibility',
          'files':files,'copper_comparisons':comparisons,'drilled_features':len(drill_shapes),
          'silkscreen_mask_overlap_mm2':silk,'errors':errors,'CAM_roundtrip_pass':not errors,
          'manufacturing_release':False}
(OUT / 'independent-cam-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'CAM_errors':len(errors),'drilled_features':len(drill_shapes),'silkscreen_mask_overlap_mm2':silk}))
raise SystemExit(bool(errors))
