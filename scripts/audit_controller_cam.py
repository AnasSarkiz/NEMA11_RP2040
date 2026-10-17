#!/usr/bin/env python3
"""Independently parse native full-controller CAM, including component slots/NPTH."""
import hashlib
import json
from pathlib import Path
from shapely.ops import unary_union, polygonize
from shapely.geometry import LineString, Polygon, box
from shapely.strtree import STRtree
from gerbonara import GerberFile
from gerbonara.utils import MM
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
silk_clearances={}
for side,area in silk.items():
    if area > 1e-5:
        errors.append({'silkscreen_over_mask_opening':side,'area_mm2':area})
    metal=geometry[side+'_SilkScreen'];mask=geometry[side+'_Mask']
    silk_clearances[side]={'minimum_mask_opening_gap_mm':metal.distance(mask),
        'inside_0_15mm_mask_guard_mm2':metal.intersection(mask.buffer(.1499)).area,
        'outside_0_20mm_board_inset_mm2':metal.difference(box(-17.3,-17.3,17.3,22.3)).area}
    if silk_clearances[side]['inside_0_15mm_mask_guard_mm2']>1e-5 or silk_clearances[side]['outside_0_20mm_board_inset_mm2']>1e-5:
        errors.append({'silkscreen_clearance':side,**silk_clearances[side]})
mask_webs={}
for side in ['F','B']:
    shape=geometry[side+'_Mask'];polys=list(shape.geoms) if hasattr(shape,'geoms') else [shape]
    tree=STRtree(polys);gaps=[]
    for i,p in enumerate(polys):
        gaps += [p.distance(polys[int(j)]) for j in tree.query(p.buffer(.25)) if j>i]
    minimum=min(gaps) if gaps else None
    mask_webs[side]={'minimum_distinct_opening_web_mm':minimum,'opening_polygons':len(polys)}
    if minimum is not None and minimum<.09999:errors.append({'mask_web':side,'minimum_mm':minimum})
stencil=[]
for side in ['F','B']:
    shape=geometry[side+'_Paste'];polys=list(shape.geoms) if hasattr(shape,'geoms') else [shape]
    for p in polys:
        if p.is_empty:continue
        x0,y0,x1,y1=p.bounds
        row={'layer':side,'bounds_mm':list(p.bounds),'aspect_ratio_at_100um':min(x1-x0,y1-y0)/.1,
             'area_ratio_at_100um':p.area/(p.length*.1)}
        stencil.append(row)
        if row['aspect_ratio_at_100um']<1.5-1e-4 or row['area_ratio_at_100um']<.66-1e-4:
            errors.append({'stencil_release_screen':row})
source={e['source_component_id']:e['name'] for e in records if e['type']=='source_component'}
components={e['pcb_component_id']:e for e in records if e['type']=='pcb_component'}
EP=[]
for e in records:
    if e['type']=='pcb_smtpad' and e.get('width',0)>2 and e.get('height',0)>2:
        name=source[components[e['pcb_component_id']]['source_component_id']]
        if name in ['U_MCU','U_DRV','U_PD']:
            pad=pad_shape(e);coverage=geometry['F_Paste'].intersection(pad).area/pad.area
            EP.append({'part':name,'coverage_fraction':coverage})
            if abs(coverage-.6)>.001:errors.append({'EP_paste_coverage':name,'fraction':coverage})
assert len(EP)==3
edges=[]
for obj in GerberFile.open(CAM/'Edge_Cuts.gbr').objects:
    for edge in obj.to_primitives(unit=MM):
        assert type(edge).__name__=='Line'
        edges.append(LineString([(edge.x1,edge.y1),(edge.x2,edge.y2)]))
outlines=list(polygonize(edges))
if len(outlines)!=1 or abs(outlines[0].area-1400)>1e-6 or outlines[0].bounds!=(-17.5,-17.5,17.5,22.5):
    errors.append({'outline':{'contours':len(outlines),'areas_mm2':[p.area for p in outlines]}})
report = {'scope':'Actual native full-controller review CAM; manufacturing qualification remains separate',
          'circuit_sha256':sha,'parser':'Gerbonara 1.5 with explicit LR/G85 compatibility',
          'files':files,'copper_comparisons':comparisons,'drilled_features':len(drill_shapes),
          'silkscreen_mask_overlap_mm2':silk,'errors':errors,'CAM_roundtrip_pass':not errors,
          'silkscreen_clearances':silk_clearances,'soldermask_webs':mask_webs,
          'stencil_thickness_candidate_mm':.10,'stencil_release_screens':stencil,'exposed_pad_paste':EP,
          'closed_outline_contours':len(outlines),'outline_area_mm2':outlines[0].area if outlines else None,
          'manufacturing_release':False}
(OUT / 'independent-cam-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'CAM_errors':len(errors),'drilled_features':len(drill_shapes),'silkscreen_mask_overlap_mm2':silk}))
raise SystemExit(bool(errors))
