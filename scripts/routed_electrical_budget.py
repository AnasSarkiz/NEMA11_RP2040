#!/usr/bin/env python3
"""Conditional routed-copper, hot-loss and regeneration screens; no bench claims."""
import hashlib
import json
import math
from pathlib import Path
from current_budget import report

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'artifacts/controller-pcb/board.circuit.json'
records=json.loads(path.read_text())
nets={e['subcircuit_connectivity_map_key']:e['name'] for e in records if e['type']=='source_net'}
base=report()
rated=.67
trip=base['source_candidate_screening']['nominal_trip_a']
rho20=1.724e-5 # ohm mm; copper at 20 C
thickness=.035 # required 1 oz finished copper, every layer
plating=.020 # assumed uniform finished wall, not a vendor guarantee
rows=[]
for name in ['SENSE1','SENSE2']:
    resistance=0
    lengths={}
    for e in records:
        if e['type']!='pcb_trace' or nets.get(e.get('subcircuit_connectivity_map_key'))!=name:continue
        for a,b in zip(e['route'],e['route'][1:]):
            length=math.dist((a['x'],a['y']),(b['x'],b['y']))
            resistance += rho20*length/(a['width']*thickness)
            lengths[a['layer']]=lengths.get(a['layer'],0)+length
    vias=[e for e in records if e['type']=='pcb_via' and nets.get(e.get('subcircuit_connectivity_map_key'))==name]
    via_R=sum(rho20*1.6/(math.pi*((e['hole_diameter']/2+plating)**2-(e['hole_diameter']/2)**2)) for e in vias)
    total=resistance+via_R
    rows.append({'net':name,'trace_lengths_mm':lengths,'via_count':len(vias),
                 'trace_R_20c_ohm':resistance,'assumed_via_R_20c_ohm':via_R,
                 'series_R_20c_ohm':total,'series_R_85c_ohm':total*(1+.00393*(85-20)),
                 'nominal_trip_with_series_R_20c_a':1.1/(8*(.24+total)),
                 'scope':'Series-path screen; ground offset, switching inductance, shunt temperature and actual plating excluded'})
inertia=9e-7 # 9 g cm^2 -> kg m^2
Cmin=47e-6*.8
Vstart=15*1.05
coil_energy=.5*(.004*1.2)*rated**2 # ideal sine vector sum Ia^2+Ib^2 = Itrip^2
speeds=[]
for rpm in [1000,3000]:
    energy=.5*inertia*(rpm*2*math.pi/60)**2
    speeds.append({'rpm':rpm,'rotor_kinetic_energy_J':energy,
                   'hypothetical_bus_V_without_TVS_or_loss':math.sqrt(Vstart**2+2*(energy+coil_energy)/Cmin)})
data={'scope':'Conditional engineering screens from current native copper and original motor drawing',
      'circuit_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'source_candidate_nominal_peak_A':trip,'source_candidate_64_corner_upper_A':base['source_candidate_screening']['maximum_screened_trip_a'],
      'current_accuracy_at_1_1V_VREF_manufacturer_guaranteed':False,
      'sense_path_assumptions':{'copper_thickness_mm_all_layers':thickness,'uniform_via_wall_mm':plating,'board_thickness_mm':1.6},
      'sense_paths':rows,
      'driver_conduction_only':{'maximum_25c_MOS_R_on_ohm_each':.43,
          'ideal_sine_vector_loss_at_nominal_trip_W':trip**2*(2*.43),
          'two_phases_at_rated_DC_loss_W':2*rated**2*(2*.43),
          'excludes':'Hot RDS(on), switching/recirculation losses and actual board thermal resistance',
          'predicted_junction_temperature_C':None},
      'motor_copper_loss':{'both_phases_at_rated_DC_25c_W':2*rated**2*5.6,
          'both_phases_at_rated_DC_130c_and_plus_10_percent_R_W':2*rated**2*5.6*(1+.00393*(130-25))*1.1,
          'ideal_sine_vector_at_nominal_trip_25c_W':trip**2*5.6,
          'rated_0_07Nm_holding_torque_delivered_by_this_current_setting_verified':False},
      'shunts':base['selected_sense_resistor'],
      'regeneration':{'bulk_capacitance_minimum_assumed_F':Cmin,'initial_bus_V':Vstart,
          'motor_only_inertia_kg_m2':inertia,'coil_energy_at_0_67A_vector_and_L_plus20percent_J':coil_energy,
          'examples_without_protection_or_loss':speeds,
          'TVS_part':'SMF18A / C19077512','rated_standoff_V':18,'breakdown_range_V':[20,22.1],
          'specified_clamp_V_at_6_8A_and_25c':29.2,'rated_peak_power_W':200,
          'rated_pulse_waveform':'10/1000 us; non-repetitive, derated above 25 C; not a general joule rating',
          'actual_regenerative_load_qualified':False},
      'bringup_acceptance_requirements':['Measure both actual phase currents across microstep positions; peak must not exceed the selected motor limit',
          'Run locked-rotor and motion thermal tests at the drawing 50 C maximum ambient, with the intended hot motor/carrier and enclosure',
          'Confirm every component stays within its data-sheet limits; correlate TMP102 board temperature with the hottest driver region before choosing firmware shutdown thresholds',
          'Measure bus overshoot for the actual external inertia, stop profile and repetition rate; verify TVS current/pulse derating and component voltage limits',
          'Confirm current-sense offsets/noise, actual via plating and finished stackup; do not assume rated holding torque at the conservative current setting'],
      'manufacturing_release':False}
(ROOT/'artifacts/requirements/routed-electrical-budget.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'sense_paths':rows,'driver_conduction_W':data['driver_conduction_only']['ideal_sine_vector_loss_at_nominal_trip_W']}))
