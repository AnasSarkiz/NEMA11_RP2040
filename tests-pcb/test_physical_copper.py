"""Fault checks for real copper connectivity and shorts, independent of native IDs."""
import copy, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from pcb_geometry import Copper
from audit_core_pcb import audit


def fixture():
    records = [{'type':'pcb_board','pcb_board_id':'board','width':10,'height':10}]
    for number, x in enumerate([-1., 1.]):
        records.extend([
            {'type':'source_component','source_component_id':f'sc{number}','name':f'R{number}'},
            {'type':'source_port','source_port_id':f'sp{number}','source_component_id':f'sc{number}',
             'pin_number':1,'subcircuit_connectivity_map_key':'n'},
            {'type':'pcb_port','pcb_port_id':f'pp{number}','source_port_id':f'sp{number}'},
            {'type':'pcb_smtpad','pcb_smtpad_id':f'pad{number}','pcb_port_id':f'pp{number}',
             'shape':'rect','x':x,'y':0.,'width':.4,'height':.4,'layer':'top'}])
    records.append({'type':'source_net','source_net_id':'sn','name':'SIGNAL','subcircuit_connectivity_map_key':'n'})
    records.append({'type':'pcb_trace','pcb_trace_id':'trace','subcircuit_connectivity_map_key':'n',
                    'route':[{'route_type':'wire','x':x,'y':0.,'width':.16,'layer':'top'} for x in [-1.,1.]]})
    return records


class PhysicalCopperTests(unittest.TestCase):
    def test_real_connected_copper(self):
        self.assertEqual(audit(fixture())['errors'], [])

    def test_same_net_ids_do_not_bridge_gap(self):
        records = fixture()
        records[-1]['route'][1]['x'] = 0.
        self.assertTrue(Copper(records).connectivity())

    def test_trace_id_does_not_bridge_layers(self):
        records = fixture()
        records[-1]['route'][1]['layer'] = 'bottom'
        self.assertTrue(Copper(records).connectivity())

    def test_foreign_copper_short(self):
        records = fixture()
        records.append({'type':'pcb_trace','pcb_trace_id':'short','subcircuit_connectivity_map_key':'foreign',
                        'route':[{'route_type':'wire','x':0.,'y':y,'width':.16,'layer':'top'} for y in [-1.,1.]]})
        self.assertTrue(any(e['type']=='short' for e in audit(records)['errors']))

    def test_foreign_copper_clearance(self):
        records = fixture()
        other = copy.deepcopy(records[-1])
        other.update(pcb_trace_id='too_close',subcircuit_connectivity_map_key='foreign')
        for point in other['route']:
            point['y'] = .3
        records.append(other)
        self.assertTrue(any(e['type']=='clearance' for e in audit(records)['errors']))

    def test_minimum_drill_is_enforced(self):
        records = fixture()
        records.append({'type':'pcb_via','pcb_via_id':'small','subcircuit_connectivity_map_key':'n',
                        'x':0.,'y':0.,'outer_diameter':.45,'hole_diameter':.25,'layers':['top','bottom']})
        self.assertTrue(any(e['type']=='via_minimum' for e in audit(records)['errors']))

    def test_board_edge_is_enforced(self):
        records = fixture()
        records[-1]['route'][1]['x'] = 4.8
        self.assertTrue(any(e['type']=='board_edge' for e in audit(records)['errors']))


if __name__ == '__main__':
    unittest.main()
