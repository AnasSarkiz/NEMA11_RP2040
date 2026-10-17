"""Fault injection must detect missing NC pins and misconnected coil/sense paths."""
import copy
import json
import unittest
from pathlib import Path
from scripts.verify_controller import check

ROOT = Path(__file__).resolve().parents[1]


class ControllerParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads((ROOT / 'artifacts/controller/unrouted.circuit.json').read_text())
        cls.reference = json.loads((ROOT / 'references/manifests/nema14-v1.13-electrical.json').read_text())

    def test_candidate_matches_with_explicit_changes(self):
        self.assertEqual(check(self.records, self.reference), [])

    def test_missing_nc_pin_is_detected(self):
        records = copy.deepcopy(self.records)
        nc = next(e for e in records if e['type'] == 'source_port'
                  and e['source_component_id'] == 'source_component_45' and e['pin_number'] == 7)
        records.remove(nc)
        self.assertTrue(check(records, self.reference))

    def test_swapped_sense_net_is_detected(self):
        records = copy.deepcopy(self.records)
        net = next(e for e in records if e['type'] == 'source_net' and e['name'] == 'SENSE2')
        pin = next(e for e in records if e['type'] == 'source_port'
                   and e['source_component_id'] == 'source_component_45' and e['pin_number'] == 23)
        pin['subcircuit_connectivity_map_key'] = net['subcircuit_connectivity_map_key']
        self.assertTrue(check(records, self.reference))

    def test_missing_USB_locating_hole_is_detected(self):
        records=copy.deepcopy(self.records)
        hole=next(e for e in records if e['type']=='pcb_hole' and e.get('pcb_component_id')=='pcb_component_0')
        records.remove(hole)
        self.assertTrue(check(records,self.reference))


if __name__ == '__main__':
    unittest.main()
