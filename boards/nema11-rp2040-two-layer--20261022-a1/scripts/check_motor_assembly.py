#!/usr/bin/env python3
"""Nominal mesh/AABB review only. Never qualifies hardware or physical assembly."""
import argparse
import hashlib
import json
import math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vertices(path):
    return [tuple(map(float, line.split()[1:4])) for line in path.read_text().splitlines() if line.startswith('v ')]


def transform(v, origin, rotation, translation):
    """Three.js Euler XYZ: subtract explicit model origin, rotate Z/Y/X, translate."""
    x, y, z = [v[i]-origin[k] for i, k in enumerate('xyz')]
    a, b, c = [math.radians(rotation[k]) for k in 'xyz']
    x, y = x*math.cos(c)-y*math.sin(c), x*math.sin(c)+y*math.cos(c)
    x, z = x*math.cos(b)+z*math.sin(b), -x*math.sin(b)+z*math.cos(b)
    y, z = y*math.cos(a)-z*math.sin(a), y*math.sin(a)+z*math.cos(a)
    return tuple(v+translation[k] for v,k in zip((x,y,z),'xyz'))


def bounds(points):
    return {'min': [min(p[i] for p in points) for i in range(3)],
            'max': [max(p[i] for p in points) for i in range(3)]}


def contract(root=ROOT):
    cfg = json.loads((root/'config/motor-assembly.json').read_text())
    for ext in ('obj', 'step'):
        assert sha(root/f'references/motor-assets/11HS12-0674S.{ext}') == cfg[f'{ext}_sha256'], f'OEM {ext} changed'
    assert cfg['motor_rotation_deg'] == dict.fromkeys('xyz', 0), 'OEM orientation changed'
    assert cfg['motor_translation_mm']['x'] == cfg['motor_translation_mm']['y'] == 0
    assert abs(cfg['motor_translation_mm']['z'] + cfg['oem_rear_max_z_mm'] + cfg['board_thickness_mm']/2 + cfg['exploded_review_gap_mm']) < 1e-9
    assert cfg['exploded_review_gap_mm'] == 10, 'Review separation changed; re-review required'
    expected = {(x,y) for x in (-11.5,11.5) for y in (-11.5,11.5)}
    transformed = [transform((x,y,31.5), dict.fromkeys('xyz',0), cfg['motor_rotation_deg'],cfg['motor_translation_mm']) for x,y in cfg['nominal_rear_axes_mm']]
    assert {(round(x,6),round(y,6)) for x,y,z in transformed} == expected
    assert all(cfg[k] is False for k in ('rear_thread_qualified','replacement_fasteners_qualified','stack_gap_and_insulation_qualified','harness_qualified','manufacturing_release'))
    return cfg


def validate_assembly(index_records, assembly_records, cfg):
    """Validate emitted motor and exact electrical records, never alter either input."""
    from collections import Counter
    name = 'OEM_11HS12_0674S_EXPLODED_REFERENCE'
    motors = [e for e in assembly_records if e['type'] == 'source_component' and e.get('name') == name]
    assert len(motors) == 1, 'Expected exactly one emitted OEM motor source'
    motor = motors[0]
    assert motor.get('ftype') == 'subassembly', 'Motor must be a mechanical subassembly'
    sid = motor['source_component_id']
    cads = [e for e in assembly_records if e['type'] == 'cad_component' and e.get('source_component_id') == sid]
    assert len(cads) == 1, 'Expected exactly one emitted OEM motor CAD'
    cad = cads[0]
    expected = {
        'model_obj_url': './references/motor-assets/11HS12-0674S.obj',
        'model_step_url': './references/motor-assets/11HS12-0674S.step',
        'position': cfg['motor_translation_mm'], 'rotation': cfg['motor_rotation_deg'],
        'model_origin_position': dict.fromkeys('xyz', 0), 'model_unit_to_mm_scale_factor': 1,
    }
    for key, value in expected.items():
        assert cad.get(key) == value, f'Emitted motor CAD mismatch: {key}'
    assert not cad.get('pcb_component_id'), 'Motor must not add an electrical PCB component'
    assert not any(key in cad for key in ('model_jscad', 'model_gltf_url', 'model_glb_url', 'model_stl_url')), 'Unexpected substitute motor geometry'
    boms = [e for e in assembly_records if e['type'] == 'cad_assembly_bom_item' and e.get('source_component_id') == sid]
    assert len(boms) == 1, 'Expected exactly one emitted OEM motor BOM item'
    bom = boms[0]
    assert bom.get('quantity') == 1 and bom.get('cad_component_ids') == [cad['cad_component_id']], 'Motor BOM quantity/CAD link mismatch'
    assert bom.get('name') == motor.get('display_name'), 'Motor BOM label mismatch'
    # Warning/error records are tool diagnostics, not netlist/PCB geometry; report
    # their counts separately. Project metadata hashes may differ by entrypoint.
    excluded = lambda e: e['type'] == 'source_project_metadata' or e['type'].endswith(('_warning', '_error'))
    canonical = lambda e: json.dumps(e, sort_keys=True, separators=(',', ':'))
    original = Counter(canonical(e) for e in index_records if not excluded(e))
    preserved = Counter(canonical(e) for e in assembly_records if not excluded(e) and e is not motor and e is not cad and e is not bom)
    missing, extra = original - preserved, preserved - original
    assert not missing and not extra, 'Assembly mutated electrical/PCB/CAD records or added unexpected parts: ' + str({'missing':list(missing)[:2], 'extra':list(extra)[:2]})
    return dict(emitted_motor_source_id=sid, emitted_motor_cad_id=cad['cad_component_id'], emitted_motor_transform_verified=True, emitted_motor_bom_verified=True, electrical_pcb_and_existing_cad_records_identical=True, compared_records=sum(original.values()), excluded_diagnostic_counts={'index':dict(Counter(e['type'] for e in index_records if excluded(e))), 'assembly':dict(Counter(e['type'] for e in assembly_records if excluded(e)))})


def audit(path, root=ROOT):
    cfg = contract(root)
    from run_milestone_checks import fresh_receipt, OUTPUT
    assert path.resolve() == (root/OUTPUT).resolve(), 'Use current electrical native output with its receipt'
    assert fresh_receipt(root), 'Native input receipt is stale; regenerate before mechanical acceptance'
    records = json.loads(path.read_text())
    source = {e['source_component_id']:e.get('name') for e in records if e['type']=='source_component'}
    pcb = {e['pcb_component_id']:e for e in records if e['type']=='pcb_component'}
    boards = [e for e in records if e['type']=='pcb_board']
    assert len(boards)==1 and boards[0]['thickness']==1.6
    poses=json.loads((root/'config/placement.json').read_text())['placements']
    for e in pcb.values():
        name=source.get(e['source_component_id'])
        if name not in poses: continue
        p=poses[name]
        assert abs(e['footprint_origin']['x']-p['pcbX'])<1e-6 and abs(e['footprint_origin']['y']-p['pcbY'])<1e-6 and e['layer']==p['layer'] and abs((e['rotation']-p.get('pcbRotation',0))%360)<1e-6, f'Stale native pose: {name}'
    holes=[e for e in records if e['type']=='pcb_hole' and not e.get('pcb_component_id')]
    assert {(e['x'],e['y']) for e in holes}==set(map(tuple,cfg['nominal_rear_axes_mm']))
    model=root/'references/motor-assets/11HS12-0674S.obj'
    mv=vertices(model)
    motor=bounds([transform(v,dict.fromkeys('xyz',0),cfg['motor_rotation_deg'],cfg['motor_translation_mm']) for v in mv])
    components=[]; unmodeled=[]
    for cad in records:
        if cad['type']!='cad_component' or cad.get('pcb_component_id') not in pcb: continue
        p=pcb[cad['pcb_component_id']];name=source[cad['source_component_id']]
        if p.get('do_not_place'): continue
        url=cad.get('model_obj_url','')
        if not url.startswith('./imports/'):
            unmodeled.append(name);continue
        asset=root/url
        vs=vertices(asset)
        origin=cad.get('model_origin_position')
        assert origin is not None, f'Unknown origin: {name}'
        bb=bounds([transform(v,origin,cad['rotation'],cad['position']) for v in vs])
        components.append(dict(name=name,layer=p['layer'],model=url,sha256=sha(asset),source_bounds_mm=bounds(vs),origin_mm=origin,rotation_deg=cad['rotation'],position_mm=cad['position'],world_bounds_mm=bb,conservative_vertical_gap_to_motor_mm=bb['min'][2]-motor['max'][2]))
    modeled={c['name'] for c in components}
    unmodeled=sorted({source[p['source_component_id']] for p in pcb.values() if not p.get('do_not_place')} - modeled)
    return dict(native_input_receipt_current=True,scope='Exploded preview nominal mesh/AABB check, not physical qualification',input=str(path),input_sha256=sha(path),placement_sha256=sha(root/'config/placement.json'),motor_source_bounds_mm=bounds(mv),motor_preview_bounds_mm=motor,whole_motor_xy_extent_mm=[motor['max'][i]-motor['min'][i] for i in (0,1)],whole_assembly_frame_maximum_mm=json.loads((root/'config/requirements.json').read_text())['whole_assembly_frame_maximum_mm'],whole_assembly_frame_pass=False,frame_failure_reason='Uncropped OEM motor and straight lead stubs alone span 28.2 x 48.2mm; main motor solid also has a lead-exit protrusion to Y=-17.1mm',nominal_bolt_axes_aligned=True,pcb_bottom_to_motor_rear_mm=-.8-motor['max'][2],minimum_component_vertical_gap_mm=min(c['conservative_vertical_gap_to_motor_mm'] for c in components),components=components,unmodeled_placed_components=unmodeled,actual_stack_gap_mm=None,fastener_thread_length_engagement_and_tool_access_qualified=False,harness_clearance_qualified=False,manufacturing_release=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path);p.add_argument('--output',type=Path);p.add_argument('--assembly-input',type=Path);a=p.parse_args()
    result=audit(a.input) if a.input else {'source_contract_passed':bool(contract()),'native_geometry_checked':False,'manufacturing_release':False}
    if a.assembly_input:
        assert a.input, '--assembly-input requires --input with a current receipt'
        result['native_assembly'] = validate_assembly(json.loads(a.input.read_text()), json.loads(a.assembly_input.read_text()), contract())
        result['native_assembly'].update(input=str(a.assembly_input), input_sha256=sha(a.assembly_input))
    data=json.dumps(result,indent=2)+'\n'
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(data)
    print(data)
