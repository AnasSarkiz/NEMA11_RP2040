#!/usr/bin/env python3
"""Conservative placement envelopes from unchanged native copper, courtyard and STEP."""
import hashlib
import json
from pathlib import Path
import cadquery as cq
from pcb_geometry import pad_shape

ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'artifacts/controller-pcb/board.circuit.json'
samples=ROOT/'artifacts/compact-controller/supplier-samples.circuit.json'
records=json.loads(base.read_text())
sample_records=json.loads(samples.read_text())
models={row['part']:row['bounds_mm'] for row in json.loads((ROOT/'artifacts/controller/nominal-assembly-audit.json').read_text())['parts']}
placements=json.loads((ROOT/'src/controller/supplier-placement.json').read_text())
catalog=json.loads((ROOT/'src/controller/jlcpcb-catalog.json').read_text())
for s in [e for e in sample_records if e['type']=='source_component']:
    cad=next(e for e in sample_records if e['type']=='cad_component' and e['source_component_id']==s['source_component_id'])
    model=ROOT/'imports'/cad['model_step_url'].split('/imports/')[1]
    shape=cq.importers.importStep(str(model)).val()
    origin=cad.get('model_origin_position',dict(x=0,y=0,z=0))
    shape=shape.translate(tuple(-origin[k] for k in 'xyz'))
    for k,axis in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
        if cad['rotation'][k]:shape=shape.rotate((0,0,0),axis,cad['rotation'][k])
    shape=shape.translate(tuple(cad['position'][k] for k in 'xyz'))
    b=shape.BoundingBox();models[s['name']]=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
parts=[]
for p in [e for e in records if e['type']=='pcb_component' and e['layer']=='top']:
    source=next(e for e in records if e['type']=='source_component' and e['source_component_id']==p['source_component_id'])
    name=source['name'];source_records=records;source_p=p;sample_name=None
    if name=='BZ1':
        sample_name='BZ_COMPACT';source_records=sample_records
        s=next(e for e in sample_records if e['type']=='source_component' and e['name']==sample_name)
        source_p=next(e for e in sample_records if e['type']=='pcb_component' and e['source_component_id']==s['source_component_id'])
    pivot=placements[name] if not sample_name else dict(pcbX=-10,pcbY=0,pcbRotation=0)
    bounds=[];cu=[]
    for e in source_records:
        if e.get('pcb_component_id')!=source_p['pcb_component_id']:continue
        if e['type'] in ['pcb_smtpad','pcb_plated_hole']:
            b=pad_shape(e).bounds;bounds.append(b);cu.append(b)
        elif e['type']=='pcb_courtyard_outline':
            bounds.append((min(t['x'] for t in e['outline']),min(t['y'] for t in e['outline']),max(t['x'] for t in e['outline']),max(t['y'] for t in e['outline'])))
    body=[]
    if (sample_name or name) in models:
        b=models[sample_name or name];body.append((b[0],b[1],b[3],b[4]));bounds.extend(body)
    merge=lambda boxes:[min(b[0] for b in boxes)-pivot['pcbX'],min(b[1] for b in boxes)-pivot['pcbY'],
                         max(b[2] for b in boxes)-pivot['pcbX'],max(b[3] for b in boxes)-pivot['pcbY']]
    b=merge(bounds)
    # Construction variant only: unchanged copper and nominal supplier body,
    # including leads, enlarged by 0.10 mm on every side. Pair-specific JLC
    # component spacing is an ADDITIONAL constraint. This does not approve a
    # replacement courtyard or qualify model dimensional tolerances.
    cb=merge(cu+body)
    construction=[cb[0]-.10,cb[1]-.10,cb[2]+.10,cb[3]+.10]
    if name.startswith('J_') or name.startswith('TP_'):construction=b
    mpn=catalog['parts'].get(catalog['components'].get(name),{}).get('manufacturerPartNumber','')
    package='other'
    if name in ['U_MCU','U_DRV','U_FLASH']:package='QFN'
    elif name=='U_PD':package='SOP'
    elif name in ['U_BUCK','U_ESD','U_TEMP','Q_BUZZER','Q_STATUS_R','Q_STATUS_G','Q_STATUS_B']:package='SOT'
    elif name[0] in ['R','C'] and name!='C_BULK':
        package=next((v for v in ['0402','0603','0805','1206'] if v in mpn),'other')
        if mpn.startswith('CL05') or mpn.startswith('HP05'):package='0402' if mpn.startswith('CL05') else '0805'
        elif mpn.startswith('CL10'):package='0603'
        elif mpn.startswith('CL21'):package='0805'
        elif mpn.startswith('CL31'):package='1206'
    ports={}
    for port in source_records:
        if port['type']!='pcb_port' or port['pcb_component_id']!=source_p['pcb_component_id']:continue
        source_port=next(e for e in source_records if e['type']=='source_port' and e['source_port_id']==port['source_port_id'])
        ports[str(source_port['pin_number'])]=[port['x']-pivot['pcbX'],port['y']-pivot['pcbY']]
    parts.append({'name':name,'original_rotation':pivot['pcbRotation'],'envelope_relative_to_pivot_mm':b,
                  'copper_relative_to_pivot_mm':merge(cu),'bbox_area_mm2':(b[2]-b[0])*(b[3]-b[1]),
                  'nominal_component_including_leads_relative_mm':merge(body) if body else None,
                  'construction_envelope_relative_mm':construction,'pin_centers_relative_mm':ports,
                  'assembly_spacing_class':package,
                  'candidate_substitution':sample_name is not None})
report={'scope':'Conservative top-side rectangular envelopes for placement construction; not a routed or tolerance-qualified assembly',
        'base_circuit_sha256':hashlib.sha256(base.read_bytes()).hexdigest(),
        'native_samples_sha256':hashlib.sha256(samples.read_bytes()).hexdigest(),
        'parts':parts,'top_side_parts_including_bare_test_points':len(parts),
        'total_envelope_area_mm2':sum(p['bbox_area_mm2'] for p in parts),
        'sample_STEP_bounds_mm':{k:v for k,v in models.items() if k.endswith('COMPACT')},
        'motor_frame_maximum_mm':[28.3,28.3],'PCB_target_mm':[28,28],
        'current_candidate_buzzer':'C94598 MLT-5020','compact_placement_verified':False,'manufacturing_release':False}
(ROOT/'artifacts/compact-controller/placement-envelopes.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['parts','sample_STEP_bounds_mm']}))
