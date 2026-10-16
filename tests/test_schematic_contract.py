import copy
import json
from pathlib import Path
import unittest
from scripts.verify_core_schematic import validate


class SchematicContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1] / 'artifacts/rp2040-core'
        cls.base = json.loads((root / 'core.circuit.json').read_text())
        cls.records = json.loads((root / 'core-schematic.circuit.json').read_text())

    def test_native_symbols_are_connected_to_real_nets(self):
        self.assertEqual(validate(self.base, self.records), [])

    def test_wire_gap_at_symbol_pin_is_rejected(self):
        records = copy.deepcopy(self.records)
        edge = next(e for e in records if e['type'] == 'schematic_trace')['edges'][0]
        # deepcopy preserves the deliberately shared point object; replace it
        # so this fault moves the wire without also moving its symbol pin.
        edge['from'] = {**edge['from'], 'x': edge['from']['x'] + .1}
        self.assertTrue(any('does not touch' in e for e in validate(self.base, records)))

    def test_wrong_net_label_is_rejected(self):
        records = copy.deepcopy(self.records)
        label = next(e for e in records if e['type'] == 'schematic_net_label')
        label['text'] = 'WRONG_NET'
        self.assertTrue(any('correct net label' in e for e in validate(self.base, records)))

    def test_missing_symbol_pin_is_rejected(self):
        records = copy.deepcopy(self.records)
        records.remove(next(e for e in records if e['type'] == 'schematic_port'))
        self.assertTrue(any('exactly one symbol port' in e for e in validate(self.base, records)))


if __name__ == '__main__':
    unittest.main()
