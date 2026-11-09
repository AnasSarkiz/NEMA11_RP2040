"""Offline positive and negative controls for the NEMA14 source refactor."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('alignment', ROOT / 'scripts/check_nema14_alignment.py')
alignment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alignment)


class Nema14Alignment(unittest.TestCase):
    def setUp(self):
        self.inputs = alignment.load_inputs()

    def assert_rejected(self):
        self.assertFalse(alignment.audit(self.inputs)['source_contract_passed'])

    def test_source_contract_is_consistent_but_full_parity_is_incomplete(self):
        report = alignment.audit(self.inputs)
        self.assertEqual(report['failures'], [])
        self.assertFalse(report['nema14_feature_parity_complete'])
        self.assertFalse(report['native_validation_run'])
        self.assertIn('current_telemetry', report['unresolved'])

    def test_i2c_must_use_gpio4_and_gpio5(self):
        self.inputs['connections']['components']['U_MCU']['connections']['6'] = 'WRONG_NET'
        self.assert_rejected()

    def test_current_adc_cannot_be_falsely_connected(self):
        self.inputs['connections']['components']['U_MCU']['connections']['38'] = 'TEMP_SDA'
        self.assert_rejected()

    def test_duplicate_sheet_component_fails(self):
        self.inputs['schematic-layout']['sheets']['07 Buzzer'].append('U_MCU')
        self.assert_rejected()

    def test_missing_seventh_sheet_fails(self):
        self.inputs['schematic-layout']['sheets'].pop('07 Buzzer')
        self.assert_rejected()

    def test_old_six_layer_defaults_fail(self):
        self.inputs['requirements']['PCB_layers'] = ['top', 'inner1', 'inner2', 'inner3', 'inner4', 'bottom']
        self.assert_rejected()

    def test_buzzer_cannot_be_removed(self):
        self.inputs['component-plan']['components'].pop('BZ1')
        self.assert_rejected()

    def test_routing_cannot_be_silently_enabled(self):
        self.inputs['requirements']['routing_enabled'] = True
        self.assert_rejected()

    def test_false_telemetry_completion_fails(self):
        self.inputs['nema14-alignment']['independent_telemetry']['implemented'] = True
        self.assert_rejected()


if __name__ == '__main__':
    unittest.main()
