#!/usr/bin/env python3
"""Every-trace width, inner-layer budgets and actual grounded-plane area."""
import hashlib
import json
import math
from pathlib import Path
from shapely.geometry import Polygon, LineString, box

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'artifacts/controller-pcb/board.circuit.json'
records=json.loads(path.read_text())
policy=json.loads((ROOT/'src/controller/layer-routing-policy.json').read_text())
nets={e['subcircuit_connectivity_map_key']:e['name'] for e in records if e['type']=='source_net'}
phase={'A_PLUS','A_MINUS','B_PLUS','B_MINUS'}
high=phase|{'SENSE1','SENSE2'}
# The 0.67 A requirement belongs to coil/sense paths. USB-data logic power,
# voltage-monitor branches and TVS pulse branches have different load budgets.
PD_aux={
 'controller_same_side_repair_0_PD_VBUS_0_layer_section_1':3.1,
 'controller_same_side_repair_0_PD_VBUS_0_layer_section_2':1.6,
}
TVS_monitor='controller_same_side_repair_6_PD_VBUS_1'
errors,rows=[],[]
phase_inner=0
for e in records:
    if e['type']!='pcb_trace':continue
    name=nets[e['subcircuit_connectivity_map_key']]
    by_layer={}
    widths=[]
    for a,b in zip(e['route'],e['route'][1:]):
        assert a['route_type']==b['route_type']=='wire' and a['layer']==b['layer']
        length=math.dist((a['x'],a['y']),(b['x'],b['y']))
        by_layer[a['layer']]=by_layer.get(a['layer'],0)+length
        widths += [a['width'],b['width']]
    minimum=.30 if name in high else .16
    role='0.67 A phase/sense' if name in high else 'Logic/control; minimum 0.16 mm'
    if name=='PD_VBUS':
        if e['pcb_trace_id']==TVS_monitor:
            minimum=.16;role='High-impedance VM monitor and TVS pulse branch; transient screen is separate'
        elif e['pcb_trace_id'] in PD_aux:
            minimum=.20;role='Short external PD auxiliary neck; bounded end-cooled thermal screen'
            if set(by_layer)-{'top','bottom'} or sum(by_layer.values())>PD_aux[e['pcb_trace_id']]:
                errors.append({'PD_auxiliary_neck_geometry':e['pcb_trace_id']})
        else:
            minimum=.50 if any(layer in ['inner1','inner2'] for layer in by_layer) else .30
            role='Shared PD power; 1.1 A design budget, 1 oz copper'
    if min(widths)<minimum-1e-8:errors.append({'trace_width':e['pcb_trace_id'],'width_mm':min(widths),'minimum_mm':minimum})
    if 'inner1' in by_layer:
        if name not in policy['inner1_allowed_nets']:errors.append({'inner1_net':name})
        if by_layer['inner1']>policy['maximum_inner1_trace_section_length_mm']:errors.append({'inner1_section_length':e['pcb_trace_id']})
        if name.startswith('QSPI_') and by_layer['inner1']>policy['maximum_clock_or_flash_inner1_section_mm']:errors.append({'flash_section_length':e['pcb_trace_id']})
        if name in phase:
            phase_inner += by_layer['inner1']
            if name=='A_MINUS' and by_layer['inner1']>policy['maximum_A_MINUS_inner1_section_mm']:
                errors.append({'A_MINUS_inner1_section_length':e['pcb_trace_id']})
            if e['pcb_trace_id'].startswith('controller_connection_'):
                w=policy['new_phase_inner1_repair_window_mm']
                window=box(w['xmin'],w['ymin'],w['xmax'],w['ymax'])
                if not window.buffer(1e-6).covers(LineString([(q['x'],q['y']) for q in e['route']])):
                    errors.append({'phase_outside_driver_repair_window':e['pcb_trace_id']})
    rows.append({'trace':e['pcb_trace_id'],'net':name,'minimum_width_mm':min(widths),
                 'required_width_mm':minimum,'load_role':role,'lengths_mm':by_layer})
if phase_inner>policy['maximum_total_phase_inner1_length_mm']:errors.append({'total_inner1_phase_length_mm':phase_inner})
areas=[]
for e in records:
    if e['type']=='pcb_copper_pour' and e['layer']=='inner1' and nets[e['subcircuit_connectivity_map_key']]=='GND':
        pts=lambda r:[(p['x'],p['y']) for p in r['vertices']]
        b=e['brep_shape'];areas.append(Polygon(pts(b['outer_ring']),[pts(r) for r in b['inner_rings']]).area)
if max(areas)<policy['required_main_inner1_ground_region_area_mm2']:errors.append({'main_inner1_ground_region_mm2':max(areas)})
report={'scope':'All native trace segments and bounded layer policy; 1 oz copper required on every layer',
        'circuit_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'traces_checked':len(rows),
        'total_inner1_phase_length_mm':phase_inner,'largest_inner1_ground_region_mm2':max(areas),
        'logic_and_DATA_VBUS_continuous_input_budget_A':.5,
        'PD_shared_design_budget_A':1.1,
        'PD_aux_neck_thermal_assumptions':'4.60 mm total, 0.20 x 0.035 mm copper, 400 W/mK; 1.1 A end-cooled 1-D screen gives approximately 2.8 C above the two boundary temperatures, excluding via/end heating. Boundary temperatures require hardware qualification.',
        'traces':rows,'errors':errors,'passed':not errors,'manufacturing_release':False}
(path.parent/'trace-and-layer-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['traces']}))
raise SystemExit(bool(errors))
