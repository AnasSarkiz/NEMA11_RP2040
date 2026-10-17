import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_controller_connectivity import inspect


def fixture(connected=True):
    records=[{'type':'source_net','source_net_id':'net1','name':'SIGNAL','subcircuit_connectivity_map_key':'n1'}]
    for pin,x in [(1,0),(2,2),(3,4)]:
        s={'type':'source_port','source_port_id':f's{pin}','source_component_id':f'c{pin}','name':'P','pin_number':1}
        s.update({'do_not_connect':True} if pin==3 else {'subcircuit_connectivity_map_key':'n1'})
        records += [{'type':'source_component','source_component_id':f'c{pin}','name':f'R{pin}','ftype':'simple_chip'},
                    {'type':'pcb_component','pcb_component_id':f'c{pin}','source_component_id':f'c{pin}'},s,
                    {'type':'pcb_port','pcb_port_id':f'p{pin}','source_port_id':f's{pin}'},
                    {'type':'pcb_smtpad','pcb_smtpad_id':f'pad{pin}','pcb_port_id':f'p{pin}',
                     'pcb_component_id':f'c{pin}','shape':'rect','x':x,'y':0,'width':.5,'height':.5,'layer':'top'}]
    if connected:
        records.append({'type':'pcb_trace','pcb_trace_id':'t','subcircuit_connectivity_map_key':'n1',
                        'route':[{'route_type':'wire','x':x,'y':0,'width':.16,'layer':'top'} for x in [0,2]]})
    return records


class AllPinConnectivityTests(unittest.TestCase):
    def test_real_copper_and_isolated_NC_pass(self):
        report=inspect(fixture());self.assertTrue(report['passed']);self.assertEqual(report['required_connected_pins'],2)
    def test_same_logical_net_without_copper_fails(self):
        self.assertEqual(inspect(fixture(False))['opens'],1)
    def test_missing_physical_pad_fails(self):
        r=[e for e in fixture() if e.get('pcb_smtpad_id')!='pad2']
        self.assertTrue(any(e['type']=='missing_or_duplicate_physical_pad' for e in inspect(r)['errors']))
    def test_NC_accidental_copper_contact_fails(self):
        r=fixture();r[-1]['route'][-1]['x']=4
        self.assertTrue(any(e['type']=='intentional_NC_has_copper_contact' for e in inspect(r)['errors']))
    def test_foreign_net_contact_is_a_short(self):
        r=fixture()
        r.append({'type':'source_net','source_net_id':'net2','name':'OTHER','subcircuit_connectivity_map_key':'n2'})
        next(e for e in r if e.get('source_port_id')=='s2' and e['type']=='source_port')['subcircuit_connectivity_map_key']='n2'
        self.assertEqual(inspect(r)['shorts'],1)
    def test_DNP_footprint_is_still_physically_checked(self):
        r=fixture(False);next(e for e in r if e.get('pcb_component_id')=='c2' and e['type']=='pcb_component')['do_not_place']=True
        report=inspect(r);self.assertEqual(report['opens'],1)
        self.assertEqual(next(c for c in report['components'] if c['designator']=='R2')['assembly'],'optional_encoder_DNP')
