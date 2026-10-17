"""Plated barrels connect layers; their drilled void must never count as copper."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from pcb_geometry import Copper, pad_shape
from shapely.geometry import Point


def fixture():
    result = [{'type':'source_net','source_net_id':'sn','name':'SIGNAL','subcircuit_connectivity_map_key':'n'}]
    for i in range(3):
        result.extend([
            {'type':'source_component','source_component_id':f'c{i}','name':f'P{i}'},
            {'type':'source_port','source_port_id':f's{i}','source_component_id':f'c{i}',
             'pin_number':1,'subcircuit_connectivity_map_key':'n'},
            {'type':'pcb_port','pcb_port_id':f'p{i}','source_port_id':f's{i}'}])
    result.append({'type':'pcb_plated_hole','pcb_plated_hole_id':'hole','pcb_port_id':'p0',
                   'shape':'circle','x':0,'y':0,'outer_diameter':.8,'hole_diameter':.4,
                   'layers':['top','inner1','inner2','bottom']})
    for i, layer in [(1,'top'),(2,'bottom')]:
        result.append({'type':'pcb_smtpad','pcb_smtpad_id':f'pad{i}','pcb_port_id':f'p{i}',
                       'shape':'rect','x':1,'y':0,'width':.4,'height':.4,'layer':layer})
        result.append({'type':'pcb_trace','pcb_trace_id':f't{i}','subcircuit_connectivity_map_key':'n',
                       'route':[{'route_type':'wire','layer':layer,'x':x,'y':0,'width':.16} for x in [.3,1.]]})
    return result


class PlatedHoleTests(unittest.TestCase):
    def test_real_barrel_connects_top_to_bottom(self):
        self.assertEqual(Copper(fixture()).connectivity(), [])

    def test_drilled_void_is_not_copper(self):
        record = next(e for e in fixture() if e['type'] == 'pcb_plated_hole')
        ring = next(shapes['top'] for e,_,shapes in Copper([*fixture()]).elements()
                    if e['type'] == 'pcb_plated_hole')
        self.assertFalse(ring.intersects(Point(0,0).buffer(.1)))
        self.assertTrue(ring.contains(Point(.3,0)))

    def test_open_trace_to_annulus_is_detected(self):
        records = fixture()
        for e in records:
            if e['type'] == 'pcb_trace' and e['pcb_trace_id'] == 't2':
                e['route'][0]['x'] = .6
        self.assertTrue(Copper(records).connectivity())

    def test_slot_rotation_and_dimensions_are_used(self):
        shape = pad_shape({'shape':'pill','x':0,'y':0,'outer_width':1.,'outer_height':2.,'ccw_rotation':90})
        self.assertAlmostEqual(shape.bounds[2]-shape.bounds[0], 2.)
        self.assertAlmostEqual(shape.bounds[3]-shape.bounds[1], 1.)


if __name__ == '__main__':
    unittest.main()
