"""Preserve the frozen 25 mm carrier snapshot and reference feature contract.

This fixture is historical; it does not define the current direct-motor-bolt
interface, whose nominal STEP axes are at 23 mm pitch.
"""
import copy,json,unittest
from pathlib import Path
from scripts.verify_controller import check
from scripts.verify_four_mounts import check_mounts
ROOT=Path(__file__).resolve().parents[1]
class FourMountContractTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.records=json.loads((ROOT/'artifacts/compact-four-mounts/unrouted.circuit.json').read_text())
  cls.config=json.loads((ROOT/'config/compact-four-mounts.json').read_text())
  cls.reference=json.loads((ROOT/'references/manifests/nema14-v1.13-electrical.json').read_text())
 def test_reference_features_preserved_with_authorized_buzzer_omission(self):
  self.assertEqual(check(self.records,self.reference,compact=True,no_buzzer=True),[])
  self.assertEqual(check_mounts(self.records,self.config),[])
 def test_missing_corner_hole_is_rejected(self):
  r=copy.deepcopy(self.records);r.remove(next(e for e in r if e['type']=='pcb_hole' and not e.get('pcb_component_id')))
  self.assertTrue(check_mounts(r,self.config))
 def test_changed_pitch_in_frozen_carrier_snapshot_is_rejected(self):
  r=copy.deepcopy(self.records)
  next(e for e in r if e['type']=='pcb_hole' and not e.get('pcb_component_id'))['x']=-11.5
  self.assertTrue(check_mounts(r,self.config))
 def test_missing_inner_layer_screw_exclusion_is_rejected(self):
  r=copy.deepcopy(self.records);next(e for e in r if e['type']=='pcb_keepout')['layers'].remove('inner2')
  self.assertTrue(check_mounts(r,self.config))
 def test_released_buzzer_GPIO_must_be_explicit_NC(self):
  r=copy.deepcopy(self.records);mcu=next(e for e in r if e['type']=='source_component' and e['name']=='U_MCU')
  pin=next(e for e in r if e['type']=='source_port' and e['source_component_id']==mcu['source_component_id'] and e['pin_number']==27)
  pin['subcircuit_connectivity_map_key']=next(e for e in r if e['type']=='source_net' and e['name']=='STEP')['subcircuit_connectivity_map_key']
  self.assertTrue(check(r,self.reference,compact=True,no_buzzer=True))
 def test_missing_temperature_sensor_is_rejected(self):
  r=copy.deepcopy(self.records);sid=next(e for e in r if e['type']=='source_component' and e['name']=='U_TEMP')['source_component_id']
  r=[e for e in r if e.get('source_component_id')!=sid]
  self.assertTrue(check(r,self.reference,compact=True,no_buzzer=True))
