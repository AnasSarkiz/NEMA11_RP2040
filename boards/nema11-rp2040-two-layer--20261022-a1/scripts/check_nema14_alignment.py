"""Offline source contracts. Passing these does not close native/hardware gates."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_inputs(root=ROOT):
    return {name: json.loads((root / 'config' / (name + '.json')).read_text())
            for name in ('requirements', 'nema14-alignment', 'component-plan',
                         'connections', 'placement', 'schematic-layout')}


def audit(inputs):
    req, contract = inputs['requirements'], inputs['nema14-alignment']
    parts = inputs['component-plan']['components']
    wiring = inputs['connections']['components']
    poses = inputs['placement']['placements']
    layout = inputs['schematic-layout']
    failures = []

    def check(ok, detail):
        if not ok:
            failures.append(detail)

    check(req['PCB_layers'] == ['top', 'bottom'], 'Two copper layers required')
    check(req['PCB_outline_mm'] == [28, 28] and req['PCB_thickness_mm'] == 1.6,
          '28 x 28 x 1.6 mm PCB required')
    check(req['motor'] == '11HS12-0674S' and req['motor_phase_current_A'] == 0.67,
          'Preserve the NEMA11 motor, not the NEMA14 ratings')
    check(req['mounts_nominal_XY_mm'] == [[-11.5, -11.5], [-11.5, 11.5], [11.5, -11.5], [11.5, 11.5]],
          'Preserve four 23 mm motor bolt axes')
    check(not req['routing_enabled'] and not contract['routing_enabled'], 'Routing must remain disabled')
    check(not req['manufacturing_release'] and not contract['manufacturing_release'],
          'No manufacturing approval follows from source checks')
    check(len(wiring) == contract['source_component_count'] == 99, 'Preserve all 99 source components')
    check(set(parts) | {n for n in wiring if n.startswith('TP_')} == set(wiring),
          'Every purchased component must have a supplier part')
    check(set(poses) == set(wiring) == set(layout['placements']),
          'Wiring, PCB placement and schematic placement populations must match')
    coverage = Counter(n for names in layout['sheets'].values() for n in names)
    check(set(coverage) == set(wiring) and all(n == 1 for n in coverage.values()),
          'Every component must occur on exactly one schematic sheet')
    check(len(layout['sheets']) == req['schematic_sheet_count'] == contract['schematic_sheet_count'] == 7,
          'Seven functional schematic sheets required')
    mcu = wiring['U_MCU']
    for pin, net in {'6': 'TEMP_SDA', '7': 'TEMP_SCL', '40': 'VM_SENSE',
                     '41': 'DATA_PRESENT', '13': 'PD_GOOD', '8': 'STEP', '9': 'DIR',
                     '11': 'ENABLE_N', '12': 'SLEEP', '27': 'BUZZER_PWM'}.items():
        check(mcu['connections'].get(pin) == net, f'MCU physical pin {pin} must connect to {net}')
    check(all(pin in mcu['no_connect'] and pin not in mcu['connections'] for pin in ('38', '39')),
          'ADC0/1 must be explicitly NC until real telemetry is implemented')
    check(all(pin not in mcu['no_connect'] for pin in ('6', '7')), 'I2C0 pins cannot also be NC')
    for name, part in {'U_MCU': 'C2040', 'U_DRV': 'C38437', 'BZ1': 'C94598',
                       'U_TEMP': 'C99269', 'U_ENCODER': 'C79815', 'U_PD': 'C46061833',
                       'R_SA': 'C7434086', 'R_SB': 'C7434086', 'C_BULK': 'C72522'}.items():
        check(parts.get(name) == part, f'Preserve {name} supplier identity {part}')
    for name in ('BZ1', 'Q_BUZZER', 'D_BUZZER', 'R_BUZZER_GATE', 'R_BUZZER_PD', 'C_BUZZER'):
        check(name in parts, f'Required buzzer stage missing {name}')
    check(req['buzzer_required'], 'Buzzer remains required')
    check(all(wiring[n]['resistance'] == 10000 for n in ('R_ENABLE', 'R_SLEEP')),
          'Keep NEMA14 review correction: 10 kohm enable/sleep bias')
    check(wiring['C_ESD']['connections'] == {'1': 'DATA_VBUS', '2': 'GND'}
          and wiring['C_ESD']['capacitance'] == 1e-7, 'Keep 100 nF ESD rail bypass')
    check(not contract['independent_telemetry']['implemented']
          and not req['independent_coil_current_telemetry_implemented'],
          'Reserved ADC pins are not implemented winding-current telemetry')
    check(not contract['motor_terminal']['qualified']
          and not req['spring_clamp_motor_connection_qualified'],
          'Current JST and AWG26 leads do not establish spring-clamp qualification')
    check(not req['upright_USB_verified'] and not req['all_top_assembly_verified'],
          'Flat USB/two-sided placement cannot be reported as upright/all-top')
    for name, spec in wiring.items():
        check(not (set(spec['connections']) & set(spec['no_connect'])), f'{name}: connected pin also NC')
    return {'source_contract_passed': not failures, 'failures': failures,
            'nema14_feature_parity_complete': False,
            'unresolved': contract['unresolved'], 'native_validation_run': False,
            'routing_enabled': False, 'manufacturing_release': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-complete', action='store_true',
                        help='Also fail on unfinished NEMA14 features; expected to fail for this WIP')
    args = parser.parse_args()
    result = audit(load_inputs())
    provenance = json.loads((ROOT / 'references/nema14-v2-20261109/provenance.json').read_text())
    for entry in provenance['files']:
        path = ROOT / 'references/nema14-v2-20261109' / entry['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            result['failures'].append('Reference digest mismatch: ' + entry['path'])
    manifest = json.loads((ROOT / 'checks/import-manifest.json').read_text())
    for part in manifest['imports']:
        for entry in part['files']:
            if hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() != entry['sha256']:
                result['failures'].append('Supplier import digest mismatch: ' + entry['path'])
    result['source_contract_passed'] = not result['failures']
    encoded = json.dumps(result, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(encoded, end='')
    return int(not result['source_contract_passed'] or
               (args.require_complete and not result['nema14_feature_parity_complete']))


if __name__ == '__main__':
    raise SystemExit(main())
