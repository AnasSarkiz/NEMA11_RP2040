"""Hidden inner layers must participate in shorts, continuity and barrel checks."""
import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from test_all_pin_connectivity import fixture
from audit_controller_connectivity import inspect
from audit_controller_pcb import inspect as geometry

def six_layer_fixture(layer='inner4'):
 r=fixture(False)
 r.insert(0,dict(type='pcb_board',pcb_board_id='board',width=20,height=20,num_layers=6,outline=[dict(x=x,y=y) for x,y in [(-10,-10),(10,-10),(10,10),(-10,10)]]))
 for i,x in [(1,0),(2,2)]:
  r.append(dict(type='pcb_via',pcb_via_id='via'+str(i),x=x,y=0,outer_diameter=.45,hole_diameter=.3,layers=['top','inner1','inner2','inner3','inner4','bottom'],from_layer='top',to_layer='bottom',subcircuit_connectivity_map_key='n1'))
 r.append(dict(type='pcb_trace',pcb_trace_id='hidden',subcircuit_connectivity_map_key='n1',route=[dict(route_type='wire',x=x,y=0,width=.16,layer=layer) for x in [0,2]]))
 return r
class SixLayerCopperTests(unittest.TestCase):
 def test_inner4_is_a_real_electrical_connection(self):
  self.assertTrue(inspect(six_layer_fixture())['passed'])
 def test_inner3_foreign_contact_is_a_real_short(self):
  r=six_layer_fixture('inner3')
  r.append(dict(type='source_net',source_net_id='net2',name='OTHER',subcircuit_connectivity_map_key='n2'))
  next(e for e in r if e['type']=='source_port' and e['source_port_id']=='s2')['subcircuit_connectivity_map_key']='n2'
  next(e for e in r if e.get('pcb_via_id')=='via2')['subcircuit_connectivity_map_key']='n2'
  r[-2]['route'][-1]['x']=1
  r.append(dict(type='pcb_trace',pcb_trace_id='other_hidden',subcircuit_connectivity_map_key='n2',route=[dict(route_type='wire',x=x,y=0,width=.16,layer='inner3') for x in [2,1]]))
  self.assertEqual(inspect(r)['shorts'],1)
  self.assertTrue(any(e['type']=='short' for e in geometry(r)['errors']))
 def test_through_barrel_cannot_omit_an_inner_layer(self):
  r=six_layer_fixture();next(e for e in r if e.get('pcb_via_id')=='via1')['layers'].remove('inner3')
  self.assertTrue(any(e['type']=='through_barrel_layer_coverage' for e in geometry(r)['errors']))
 def test_copper_outside_declared_stack_is_rejected(self):
  r=six_layer_fixture();r[0]['num_layers']=4
  self.assertTrue(any(e['type']=='unknown_copper_layer' for e in geometry(r)['errors']))
