"""Audit native output without modifying generated data or supplier imports."""
import collections
import hashlib
import json
import math
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


records = load('dist/index/circuit.json')
components = {x['name']: x for x in records if x['type'] == 'source_component'}
nets = {x['name']: x for x in records if x['type'] == 'source_net'}
ports = {(x['source_component_id'], str(x.get('pin_number'))): x for x in records if x['type'] == 'source_port'}
checks = []


def check(name, passed, detail=None):
    checks.append({'check': name, 'passed': bool(passed), 'detail': detail})


check('native output belongs to current source', digest('index.circuit.tsx') == load('checks/native-build-status.json')['source_sha256'])
plan = load('config/component-plan.json')['components']
for name, part in plan.items():
    check(name + ' genuine supplier identity', part in components.get(name, {}).get('supplier_part_numbers', {}).get('jlcpcb', []))
for item in load('checks/import-manifest.json')['imports']:
    for file in item['files']:
        check('untouched import ' + file['path'], digest(file['path']) == file['sha256'])
for name, spec in load('config/connections.json')['components'].items():
    component = components.get(name, {})
    for pin, net in spec['connections'].items():
        port = ports.get((component.get('source_component_id'), pin), {})
        key = port.get('subcircuit_connectivity_map_key')
        check(name + ' pin ' + pin + ' -> ' + net, key is not None and key == nets[net].get('subcircuit_connectivity_map_key'))
    for field in ['resistance', 'capacitance', 'inductance']:
        if field in spec:
            actual = component.get(field)
            if actual == '4.7uH':
                actual = 4.7e-6
            expected = 4.7e-6 if spec[field] == '4.7uH' else spec[field]
            check(name + ' supplier ' + field, isinstance(actual, (int, float)) and math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-15), {'expected': spec[field], 'actual': actual})
board = next(x for x in records if x['type'] == 'pcb_board')
check('two copper layers', board['num_layers'] == 2)
check('28 mm square outline', board['width'] == board['height'] == 28)
check('routing remains disabled', not any(x['type'] in ['pcb_trace', 'pcb_via'] for x in records))
check('full buzzer stage present', all(n in components for n in ['BZ1', 'Q_BUZZER', 'D_BUZZER', 'R_BUZZER_GATE', 'R_BUZZER_PD', 'C_BUZZER']))
placement = {x['source_component_id']: x for x in records if x['type'] == 'pcb_component'}
check('optional encoder remains DNP', all(placement[components[n]['source_component_id']]['do_not_place'] for n in ['U_ENCODER', 'C_ENCODER', 'C_ENCODER_BULK']))
errors = dict(collections.Counter(x['type'] for x in records if x['type'].endswith('_error')))
report = {'source_sha256': digest('index.circuit.tsx'), 'circuit_json_sha256': digest('dist/index/circuit.json'), 'structural_checks': checks, 'structural_failure_count': sum(not c['passed'] for c in checks), 'native_errors': errors, 'native_error_count': sum(errors.values()), 'manufacturing_approved': False, 'scope': 'Source preservation and import integrity only; does not approve schematic, placement, routing, shorts, mechanics or manufacturing.'}
Path('checks/source-integrity.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'structural_checks'}, indent=2))
for c in checks:
    if not c['passed']:
        print('FAIL', c)
raise SystemExit(bool(report['structural_failure_count']))
