"""New reconstruction contracts, not evidence of historical unpublished passes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'references/baseline-1233ccdf'
HASHES = {'config/connections.json': '99f84c98b2f45c06c7842307fa57942e677848d229f971270004457179872876', 'config/component-plan.json': '09180ed32dd9131cacbd8367baac4cdce752d7f0207e4b86bfa3c3182cae8e7d', 'dist/index/circuit.json': '300e1da00d0fd55563e730e58af7a33664b25be90b24aba92f6fec9b714760ac'}
CHANGED = {'U_PD', 'Q_BUZZER', 'Q_STATUS_R', 'Q_STATUS_G', 'Q_STATUS_B', 'R_ENABLE', 'R_SLEEP', 'R_BUZZER_GATE', 'R_BUZZER_PD'}
ADDED = {'C_ESD'} | {f'R_STATUS_{c}_{suffix}' for c in 'RGB' for suffix in ('GATE', 'PD')}


def read(path):
    return json.loads(path.read_text())


class ElectricalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('runner', ROOT / 'scripts/run_milestone_checks.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not module.fresh_receipt(ROOT):
            raise AssertionError('Missing or stale complete-input native receipt; run the milestone runner')
        for path, expected in HASHES.items():
            if hashlib.sha256((FIXTURE / path).read_bytes()).hexdigest() != expected:
                raise AssertionError('Immutable public baseline hash mismatch: ' + path)
        cls.records = read(ROOT / 'dist/index/circuit.json')
        cls.components = {x['name']: x for x in cls.records if x['type'] == 'source_component'}
        cls.nets = {x['name']: x for x in cls.records if x['type'] == 'source_net'}
        cls.ports = {(x['source_component_id'], str(x.get('pin_number'))): x for x in cls.records if x['type'] == 'source_port'}

    def part(self, name, expected):
        self.assertIn(expected, self.components[name]['supplier_part_numbers']['jlcpcb'], name)

    def connection(self, name, pin, net):
        key = self.ports[(self.components[name]['source_component_id'], str(pin))].get('subcircuit_connectivity_map_key')
        self.assertIsNotNone(key, (name, pin))
        self.assertEqual(key, self.nets[net].get('subcircuit_connectivity_map_key'), (name, pin, net))

    def no_connect(self, name, pin):
        port_key = (self.components[name]['source_component_id'], str(pin))
        self.assertIn(port_key, self.ports, ('missing physical NC port', name, pin))
        port = self.ports[port_key]
        self.assertTrue(port.get('do_not_connect'), ('missing explicit NC marker', name, pin))
        self.assertIsNone(port.get('subcircuit_connectivity_map_key'), ('NC port connected', name, pin))

    def test_preserved_physical_no_connect_ports(self):
        baseline = read(FIXTURE / 'config/connections.json')['components']
        for name, spec in baseline.items():
            for pin in spec.get('no_connect', []):
                self.no_connect(name, pin)

    def test_fixture_provenance(self):
        metadata = read(FIXTURE / 'provenance.json')
        self.assertEqual(metadata['revision'], '1233ccdf803a1221820f28eabf4791b4a7cfe90e')
        self.assertEqual(metadata['files'], HASHES)

    def test_board_envelope_counts_and_unrouted_state(self):
        boards = [x for x in self.records if x['type'] == 'pcb_board']
        self.assertEqual(len(boards), 1)
        self.assertEqual(tuple(boards[0][x] for x in ('width', 'height', 'thickness', 'num_layers')), (28, 28, 1.6, 2))
        self.assertEqual(len(self.components), 99)
        placement = [x for x in self.records if x['type'] == 'pcb_component']
        self.assertEqual(sum(not x.get('do_not_place', False) for x in placement), 89)
        self.assertFalse(any(x['type'] in ('pcb_trace', 'pcb_via') for x in self.records))

    def test_pd_physical_pins_and_configuration(self):
        self.part('U_PD', 'C46061833')
        for pin, net in {1: 'PD_VHV', 6: 'PD_CC2', 7: 'PD_CC1', 8: 'PD_VBUS', 9: 'PD_CFG', 10: 'PD_GOOD', 11: 'GND'}.items():
            self.connection('U_PD', pin, net)
        for pin in range(2, 6):
            self.no_connect('U_PD', pin)
        self.assertEqual(self.components['R_PD_CFG']['resistance'], 56000)
        self.connection('R_PD_CFG', 1, 'PD_CFG')
        self.connection('R_PD_CFG', 2, 'GND')
        self.assertEqual(self.components['R_PD']['resistance'], 0)

    def test_low_side_fets_and_startup_networks(self):
        for label in ['BUZZER'] + ['STATUS_' + c for c in 'RGB']:
            name = 'Q_' + label
            self.part(name, 'C154728')
            self.connection(name, 1, label + '_GATE')
            self.connection(name, 2, 'BUZZER_SINK' if label == 'BUZZER' else label + '_C')
            self.connection(name, 3, 'GND')
            gate, pull = 'R_' + label + '_GATE', 'R_' + label + '_PD'
            self.part(gate, 'C11702')
            self.part(pull, 'C25744')
            self.assertEqual(self.components[gate]['resistance'], 1000)
            self.assertEqual(self.components[pull]['resistance'], 10000)
            self.connection(pull, 1, label + '_GATE')
            self.connection(pull, 2, 'GND')
            self.connection(gate, 2, label + '_GATE')
            if label.startswith('STATUS_'):
                self.connection(gate, 1, 'LED_' + label[-1])
                self.assertEqual(self.components['R_' + label]['resistance'], 1000)
        self.connection('R_BUZZER_GATE', 1, 'BUZZER_PWM')
        self.connection('D_STATUS', 4, 'DATA_VBUS')
        for name in ('R_ENABLE', 'R_SLEEP'):
            self.part(name, 'C25744')
            self.assertEqual(self.components[name]['resistance'], 10000)
        self.part('C_ESD', 'C1525')
        self.assertAlmostEqual(self.components['C_ESD']['capacitance'], 100e-9, places=12)
        self.connection('C_ESD', 1, 'DATA_VBUS')
        self.connection('C_ESD', 2, 'GND')

    def test_unchanged_features_match_public_baseline(self):
        baseline_parts = read(FIXTURE / 'config/component-plan.json')['components']
        baseline_connections = read(FIXTURE / 'config/connections.json')['components']
        self.assertEqual(set(self.components), set(baseline_connections) | ADDED)
        for name, part in baseline_parts.items():
            if name not in CHANGED:
                self.part(name, part)
        for name, spec in baseline_connections.items():
            if name in {'U_PD', 'Q_BUZZER', 'Q_STATUS_R', 'Q_STATUS_G', 'Q_STATUS_B'}:
                continue
            for pin, net in spec['connections'].items():
                self.connection(name, pin, net)
            for field in ('resistance', 'capacitance', 'inductance'):
                if field in spec and name not in {'R_ENABLE', 'R_SLEEP', 'R_BUZZER_GATE', 'R_BUZZER_PD'}:
                    expected = 4.7e-6 if spec[field] == '4.7uH' else spec[field]
                    actual = self.components[name].get(field)
                    actual = 4.7e-6 if actual == '4.7uH' else actual
                    self.assertAlmostEqual(actual, expected, delta=max(abs(expected) * 1e-8, 1e-15), msg=name)

if __name__ == '__main__':
    unittest.main()
