"""Confirm the pin contract catches faults that can damage or disable the MCU."""
import copy
import json
from pathlib import Path
import unittest
from scripts.verify_core import validate


class CoreContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / 'artifacts/rp2040-core/core.circuit.json'
        cls.records = json.loads(path.read_text())

    def move_pin(self, records, ref, number, net):
        source = next(e for e in records if e['type'] == 'source_component' and e['name'] == ref)
        port = next(e for e in records if e['type'] == 'source_port'
                    and e['source_component_id'] == source['source_component_id'] and e['pin_number'] == number)
        target = next(e for e in records if e['type'] == 'source_net' and e['name'] == net)
        port['subcircuit_connectivity_map_key'] = target['subcircuit_connectivity_map_key']

    def test_built_subsystem_satisfies_contract(self):
        self.assertEqual(validate(self.records), [])

    def test_core_rail_cannot_be_shortened_to_3v3(self):
        records = copy.deepcopy(self.records)
        self.move_pin(records, 'U_MCU', 45, 'V3V3')
        self.assertTrue(any('physical pin 45' in e for e in validate(records)))

    def test_flash_io2_io3_swap_is_rejected(self):
        records = copy.deepcopy(self.records)
        self.move_pin(records, 'U_FLASH', 3, 'QSPI_SD3')
        self.move_pin(records, 'U_FLASH', 7, 'QSPI_SD2')
        self.assertTrue(any('U_FLASH physical pin 3' in e for e in validate(records)))

    def test_missing_bypass_is_rejected(self):
        records = [e for e in self.records if not(e['type'] == 'source_component' and e['name'] == 'C_IO49')]
        self.assertTrue(any('Missing C_IO49' in e for e in validate(records)))

    def test_boot_ground_short_is_rejected(self):
        records = copy.deepcopy(self.records)
        self.move_pin(records, 'TP_BOOT', 1, 'GND')
        self.assertTrue(any('TP_BOOT physical pin 1' in e for e in validate(records)))

    def test_paste_on_bare_debug_pad_is_rejected(self):
        records = copy.deepcopy(self.records)
        source = next(e for e in records if e['type'] == 'source_component' and e['name'] == 'TP_BOOT')
        part = next(e for e in records if e['type'] == 'pcb_component'
                    and e['source_component_id'] == source['source_component_id'])
        records.append({'type': 'pcb_solder_paste', 'pcb_component_id': part['pcb_component_id']})
        self.assertIn('Bare debug pad has stencil paste', validate(records))


if __name__ == '__main__':
    unittest.main()
