#!/usr/bin/env python3
"""Check every controller physical pin against the immutable reference manifest."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(records, reference, compact=False, no_buzzer=False, hybrid_bulk=False):
    errors = []
    components = {e['source_component_id']: e for e in records if e['type'] == 'source_component'}
    names = {e['name']: e for e in components.values()}
    nets = {e['subcircuit_connectivity_map_key']: e['name'] for e in records if e['type'] == 'source_net'}
    pins = {(components[e['source_component_id']]['name'], e['pin_number']):
            nets.get(e.get('subcircuit_connectivity_map_key'))
            for e in records if e['type'] == 'source_port'}
    expected = copy.deepcopy(reference['components'])
    expected['R_REF_H'].update(manufacturer_part_number='0603WAF2002T5E', resistance=20000,
                              supplier_part_numbers={'jlcpcb': ['C4184']})
    expected['J_MOTOR'].update(manufacturer_part_number='B4B-PH-K-S(LF)(SN)',
                              supplier_part_numbers={'jlcpcb': ['C131334']})
    for name in ['R_SA','R_SB']:
        expected[name].update(manufacturer_part_number='HP05W3F240LT5E',
                              supplier_part_numbers={'jlcpcb':['C7434086']})
    if hybrid_bulk:
        expected['C_BULK'].update(manufacturer_part_number='EEHZC1V680XP',capacitance=68e-6,
                                 supplier_part_numbers={'jlcpcb':['C178649']})
    if compact:
        expected['BZ1'].update(manufacturer_part_number='MLT-5020',supplier_part_numbers={'jlcpcb':['C94598']})
    omitted = json.loads((ROOT/'config/compact-four-mounts.json').read_text())['omitted_components'] if no_buzzer else []
    for name in omitted: expected.pop(name)
    if names.keys() != expected.keys():
        errors.append({'component_set_difference': sorted(names.keys() ^ expected.keys())})
    for name, fields in expected.items():
        for field, value in fields.items():
            if names.get(name, {}).get(field) != value:
                errors.append({'component': name, 'field': field,
                               'expected': value, 'actual': names.get(name, {}).get(field)})
    expected_pins = {(e['component'], e['pin']): e['net'] for e in reference['ports']}
    # SH has two electrically unused hold-downs; the genuine PH footprint has none.
    for pin in [('J_MOTOR', 5), ('J_MOTOR', 6)]:
        assert expected_pins.pop(pin) is None
    if compact:
        assert expected_pins.pop(('BZ1',4)) is None
    removed_pins = [pin for pin in expected_pins if pin[0] in omitted]
    for pin in removed_pins: expected_pins.pop(pin)
    if no_buzzer:
        expected_pins[('U_MCU',27)] = None
        if set(nets.values()) & {'BUZZER_PWM','BUZZER_GATE','BUZZER_SINK'}:
            errors.append({'orphaned_buzzer_nets': sorted(set(nets.values()) & {'BUZZER_PWM','BUZZER_GATE','BUZZER_SINK'})})
    for pin in sorted(pins.keys() | expected_pins.keys()):
        if pin not in pins or pin not in expected_pins or pins.get(pin) != expected_pins.get(pin):
            errors.append({'pin': pin, 'expected': expected_pins.get(pin), 'actual': pins.get(pin)})
    expected_count=(340 if compact else 341)-len(removed_pins)
    if len(pins) != expected_count:
        errors.append({'physical_pin_count': len(pins), 'expected': expected_count})
    pcb = {e['source_component_id']: e for e in records if e['type'] == 'pcb_component'}
    dnp = sorted(components[k]['name'] for k, e in pcb.items() if e.get('do_not_place'))
    expected_dnp = ['C_ENCODER', 'C_ENCODER_BULK', 'U_ENCODER'] + [n for n in names if n.startswith('TP_')]
    if dnp != sorted(expected_dnp):
        errors.append({'unexpected_DNP_set': dnp})
    for name in ['R_SA', 'R_SB']:
        if names.get(name, {}).get('resistance') != .24:
            errors.append({'sense_resistance_changed': name})
    for name in ['J_PD','J_DATA']:
        component=pcb[names[name]['source_component_id']]
        holes=[e for e in records if e['type']=='pcb_hole' and e.get('pcb_component_id')==component['pcb_component_id']]
        positions=sorted((e['x'],e['y']) for e in holes)
        if len(holes)!=2 or abs(positions[1][0]-positions[0][0]-8)>.001 or abs(positions[1][1]-positions[0][1])>.001:
            errors.append({'manufacturer_USB_locator_pattern':name,'actual':positions,'expected':'Two NPTH holes, 8 mm X pitch'})
        if any(abs(e['hole_diameter']-.71)>.001 for e in holes):
            errors.append({'manufacturer_USB_locator_diameter':name})
    for e in records:
        if e['type'] == 'pcb_trace':
            errors.append({'unexpected_copper_in_source_candidate': e['pcb_trace_id']})
    return errors


def main():
    import sys
    compact='--compact' in sys.argv
    no_buzzer='--no-buzzer' in sys.argv
    hybrid_bulk='--hybrid-bulk' in sys.argv
    if hybrid_bulk and not (compact and no_buzzer):raise ValueError('Hybrid bulk is only selected in the separate compact four-hole iteration')
    if no_buzzer and not compact: raise ValueError('Buzzer omission is only authorized for compact four-hole development')
    folder=sys.argv[sys.argv.index('--folder')+1] if '--folder' in sys.argv else 'artifacts/compact-controller' if compact else 'artifacts/controller'
    path = ROOT / folder / 'unrouted.circuit.json'
    records = json.loads(path.read_text())
    reference = json.loads((ROOT / 'references/manifests/nema14-v1.13-electrical.json').read_text())
    errors = check(records, reference, compact=compact, no_buzzer=no_buzzer, hybrid_bulk=hybrid_bulk)
    report = {'scope': 'All physical controller pins and component values; no copper qualification',
              'circuit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'reference_board_sha256': reference['reference_board_sha256'],
              'components_compared': sum(e['type']=='source_component' for e in records), 'physical_pins_compared': sum(e['type']=='source_port' for e in records),
              'intentional_changes': ['R_REF_H: 39k/C23153 to 20k/C4184',
                                      'J_MOTOR: SH/C160390 to PH/C131334; two unused hold-down terminals removed',
                                      'R_SA/R_SB: 125mW C2930216 to 1/3W C7434086; same 0.24 ohm value and identical copper pads'],
              'metadata_correction': '12MHz four-pad crystal uses SI load_capacitance=1e-11 F; reference stored 10 without SI conversion',
              'assembly_metadata': 'Seven bare PCB test pads are doNotPlace; PH mates from above; encoder and both capacitors remain DNP',
              'manufacturer_footprint_correction':'Two GCT-required 0.71 mm NPTH locating holes per USB, 8.00 mm pitch; original supplier import omitted the right hole',
              'errors': errors, 'manufacturing_release': False}
    if no_buzzer:report['intentional_changes'].append('User-authorized complete buzzer circuit removal: '+', '.join(json.loads((ROOT/'config/compact-four-mounts.json').read_text())['omitted_components'])+'; MCU GPIO16 explicitly NC')
    elif compact:report['intentional_changes'].append('BZ1: HYG-8503A/C7544813 to MLT-5020/C94598; three rather than four terminals, one dummy NC removed')
    if hybrid_bulk:report['intentional_changes'].append('C_BULK: RVT1V470M0605/C72522, 47uF to Panasonic EEHZC1V680XP/C178649, 68uF/35V; genuine imported lands and official manufacturer CAD; ripple screen documented separately')
    (ROOT / folder / 'electrical-parity.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
