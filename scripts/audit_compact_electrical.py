#!/usr/bin/env python3
"""Current and temperature screens tied to actual compact trace geometry.

These are conditional calculations, not guarantees at the proposed 1.1 V VREF,
an IPC-2152 thermal model, or measurements on a manufactured board.
"""
import hashlib,json,math
from pathlib import Path
from current_budget import report as current_report
from pcb_geometry import Copper

ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'artifacts/compact-six-layer';path=folder/'board.circuit.json'
records=json.loads(path.read_text());c=Copper(records);base=current_report();rho=1.724e-5;thickness=.035;rated=.67;trip=base['source_candidate_screening']['nominal_trip_a'];errors=[]
length=lambda e:sum(math.dist((a['x'],a['y']),(b['x'],b['y'])) for a,b in zip(e['route'],e['route'][1:]))
sense=[]
for net,pin,part in [('SENSE1',23,'R_SA'),('SENSE2',27,'R_SB')]:
    ids=[f'compact_terminal_U_DRV_{pin}_stub','compact_positive_land_contact_'+part]
    traces=[next(e for e in records if e.get('pcb_trace_id')==id) for id in ids]
    resistance=sum(rho*math.dist((a['x'],a['y']),(b['x'],b['y']))/(a['width']*thickness) for e in traces for a,b in zip(e['route'],e['route'][1:]))
    if any(p['layer']!='top' for e in traces for p in e['route']):errors.append('Unexpected multilayer force path '+net)
    sense.append(dict(net=net,explicit_force_trace_ids=ids,trace_length_mm=sum(length(e) for e in traces),top_trace_R_20c_upper_screen_ohm=resistance,top_trace_R_85c_upper_screen_ohm=resistance*(1+.00393*65),series_barrels_in_this_TOP_force_path=0,nominal_peak_with_trace_screen_A=1.1/(8*(.24+resistance)),scope='Full explicit trace lengths counted even inside supplier lands; a conservative positive trace-only screen. Ground return, shunt TCR and switching offset excluded. The terminal via is not a series barrel in this top-only path.'))
widths=[]
for e in records:
    if e['type']!='pcb_trace':continue
    net=c.nets.get(c.key(e))
    if net not in ['A_PLUS','A_MINUS','B_PLUS','B_MINUS','SENSE1','SENSE2','PD_VBUS','LOGIC_IN','DATA_VBUS']:continue
    # In-land topology markers add no copper or independent current bottleneck.
    if e['pcb_trace_id'].endswith('_land_contact') or e['pcb_trace_id'].startswith('compact_existing_land_'):continue
    for a,b in zip(e['route'],e['route'][1:]):
        bridge_supply_neck=e['pcb_trace_id'] in ['compact_terminal_U_DRV_22_stub','compact_terminal_U_DRV_28_stub']
        current=rated if bridge_supply_neck else 1.1 if net=='PD_VBUS' else .5 if net in ['LOGIC_IN','DATA_VBUS'] else rated
        internal=a['layer'].startswith('inner');k=.024 if internal else .048;area_mil2=a['width']/.0254*(thickness/.0254);rise=(current/(k*area_mil2**.725))**(1/.44)
        row=dict(trace=e['pcb_trace_id'],net=net,layer=a['layer'],width_mm=a['width'],length_mm=math.dist((a['x'],a['y']),(b['x'],b['y'])),current_screen_A=current,load_role='One bridge VBB terminal, bounded by that phase current; shared PD trunks retain 1.1 A' if bridge_supply_neck else 'Shared PD input' if net=='PD_VBUS' else 'Logic power' if net in ['LOGIC_IN','DATA_VBUS'] else 'Phase or sense current',legacy_IPC2221_isolated_rise_C=rise);widths.append(row)
        if rise>30:errors.append(dict(trace_width_temperature_screen=row))
phase_vias=[e for e in records if e['type']=='pcb_via' and c.nets.get(c.key(e)) in ['A_PLUS','A_MINUS','B_PLUS','B_MINUS','SENSE1','SENSE2']]
wall=.020;barrel_area=math.pi*((.15+wall)**2-.15**2);via_resistance=rho*1.6/barrel_area;via_thermal=1.6e-3/(400*barrel_area*1e-6)
data=dict(scope='Conditional electrical/thermal screens for exact native compact copper; hardware and fabricator qualification incomplete',circuit_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_nominal_VREF_V=1.1,source_nominal_peak_A=trip,conditional_64_corner_upper_A=base['source_candidate_screening']['maximum_screened_trip_a'],manufacturer_accuracy_guaranteed_at_1_1V=False,accuracy_limitation=base['assumptions']['accuracy_limitation'],sense_paths=sense,sense_resistors=base['selected_sense_resistor'],sense_loss_each_at_0_67A_W=rated**2*.24,all_copper_layers_required_finished_thickness_mm=thickness,trace_screens=widths,maximum_trace_temperature_screen_C=max(r['legacy_IPC2221_isolated_rise_C'] for r in widths),via_screen=dict(drill_diameter_mm=.3,assumed_finished_wall_mm=wall,assumed_board_thickness_mm=1.6,full_length_barrel_R_20c_ohm=via_resistance,full_length_barrel_loss_at_0_67A_W=rated**2*via_resistance,one_barrel_end_to_end_thermal_resistance_K_per_W=via_thermal,phase_and_sense_barrels=len(phase_vias),finished_plating_and_actual_heat_spreading_verified=False),driver_conduction_screen=dict(MOS_R_on_max_at_datasheet_25c_test_ohm=.43,ideal_sine_vector_at_nominal_trip_W=trip**2*.86,two_phases_at_rated_DC_W=2*rated**2*.86,datasheet_JEDEC_four_layer_theta_JA_K_per_W=32,this_28mm_six_layer_board_theta_JA_verified=False,junction_temperature_C=None,excluded='Hot MOS resistance, switching/recirculation losses, board/case/motor temperatures and real copper thermal resistance'),motor_copper_screen=dict(ideal_sine_at_nominal_trip_25c_W=trip**2*5.6,two_phases_at_rated_DC_25c_W=2*rated**2*5.6,rated_holding_torque_at_this_current_setting_verified=False),bulk_capacitor_ripple_ESR_DC_bias_and_regeneration_qualified=False,errors=errors,trace_screens_pass=not errors,bench_qualified=False,manufacturing_release=False)
(folder/'electrical-thermal-screen.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(dict(sense_paths=sense,maximum_trace_rise_screen_C=data['maximum_trace_temperature_screen_C'],errors=errors,manufacturing_release=False)));raise SystemExit(bool(errors))
