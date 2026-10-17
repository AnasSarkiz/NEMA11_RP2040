#!/usr/bin/env python3
"""Hash-bound checks for the routed review checkpoint, never a factory release."""
import hashlib,json
from pathlib import Path
from verify_four_mounts import check_mounts

ROOT=Path(__file__).resolve().parents[1];F=ROOT/'artifacts/compact-six-layer'
def read(name):return json.loads((F/name).read_text())
def sha(name):return hashlib.sha256((F/name).read_bytes()).hexdigest()
source=sha('unrouted.circuit.json');pcb=sha('board.circuit.json');r=read('board.circuit.json')
assert not check_mounts(r,json.loads((ROOT/'config/compact-four-mounts.json').read_text()))
assert next(e for e in r if e['type']=='pcb_board')['num_layers']==6
for name in ['electrical-parity.json','placement-verification.json','nominal-assembly-audit.json']:
    d=read(name);assert d['circuit_sha256']==source,name
assert not read('electrical-parity.json')['errors']
p=read('placement-verification.json');assert p['placement_pass'] and p['all_fitted_on_top'] and p['fitted_parts']==76
for name in ['PCB-build.json','independent-copper-audit.json','all-pin-connectivity.json','native-drc.json','independent-cam-audit.json','electrical-thermal-screen.json','filled-capped-via-policy.json','CLI-shorts.json','clock-layout-audit.json']:
    d=read(name);assert d['circuit_sha256']==pcb,name
    assert not d.get('errors',[]),name
for entry in read('PCB-build.json')['inputs']:assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
pins=read('all-pin-connectivity.json');assert (pins['components_checked'],pins['physical_pins_checked'],pins['required_connected_pins'],pins['intentional_NC_pins'],pins['nets_checked'],pins['opens'],pins['shorts'])==(86,326,290,36,61,0,0)
assert pins['passed'] and read('native-drc.json')['native_drc_pass'] and read('independent-cam-audit.json')['CAM_roundtrip_pass'] and read('electrical-thermal-screen.json')['trace_screens_pass']
assert read('CLI-shorts.json')['exit_code']==0
assert read('clock-layout-audit.json')['clock_construction_pass'] and read('clock-layout-audit.json')['full_controller_routing_complete']
schematic=read('schematic-verification.json');assert schematic['passed'] and schematic['source_sha256']==source and schematic['schematic_sha256']==sha('schematic.circuit.json')
assert (schematic['sheet_count'],schematic['components'],schematic['physical_pins'],schematic['connected_nets'],schematic['explicit_NC_pins'])==(6,86,326,61,36)
pdf=read('pdf-verification.json');assert pdf['pdf_sha256']==sha('schematic-a4.pdf') and pdf['page_count']==6 and pdf['schematic_sha256']==sha('schematic.circuit.json')
for check in read('native-source-checks.json'):assert check['exit_code']==0 and check['input_sha256']==hashlib.sha256((ROOT/check['input']).read_bytes()).hexdigest()
nominal=read('nominal-assembly-audit.json');assert nominal['nominal_solid_and_lead_fit_pass'] and nominal['all_fitted_on_top'] and nominal['whole_fitted_parts_within_28_3mm_frame']
assert len(nominal['errors'])==2 and all('invalid_original_supplier_STEP' in e and e['part'] in ['J_PD','J_DATA'] for e in nominal['errors'])
assembly=read('assembly-build.json');assert assembly['PCB_routed'] and assembly['source_sha256']==pcb
geometry=read('assembly-geometry-verification.json');assert geometry['passed'] and geometry['native_models_checked']==78 and geometry['GLB_sha256']==sha('development-assembly.glb')
export=read('assembly-3d-export-verification.json');assert export['circuit_sha256']==sha('assembly.circuit.json') and export['glb_sha256']==sha('development-assembly.glb')
bom=read('assembly-data/export-verification.json');assert bom['circuit_sha256']==pcb and (bom['fitted_purchased_parts'],bom['SMT_BOM_CPL_parts'],bom['manual_through_hole_parts'],bom['supplier_rotation_warnings'])==(76,75,1,0)
report=dict(scope='Routed six-layer compact review checkpoint; factory, USB and physical qualification incomplete',source_sha256=source,circuit_sha256=pcb,assembly_sha256=sha('assembly.circuit.json'),GLB_sha256=sha('development-assembly.glb'),layers=6,outline_mm=[28,28],PCB_mount_count=4,PCB_hole_pitch_mm=25,PCB_hole_diameter_mm=1.8,fitted_components_top=76,native_DRC_errors=0,native_source_warnings=len(read('native-drc.json')['warnings']),independent_copper_errors=0,physical_opens=0,physical_shorts=0,required_connected_pins=290,intentional_NC_pins=36,connected_nets=61,schematic_A4_sheets=6,native_3D_models=78,CAM_roundtrip_errors=0,CLI_Gerber_shorts_exit_code=0,SMT_BOM_CPL_parts=75,manual_PH_headers=1,buzzer_omitted_with_user_authorization=True,native_copper_review_pass=True,USB_pair_geometry_and_impedance_qualified=False,carrier_fasteners_harness_and_maximum_tolerances_qualified=False,stock_reserved=False,factory_process_acceptance_received=False,physical_bringup_and_thermal_qualification_complete=False,manufacturing_release=False)
(F/'milestone-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
