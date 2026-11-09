import importlib.util
import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('geometry_audit', ROOT/'scripts/audit_placement_geometry.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PlacementGeometryTests(unittest.TestCase):
    def extents(self, element):
        lo, hi = module.geometry_bounds(element)
        return hi[0]-lo[0], hi[1]-lo[1]

    def test_rotated_smt_quarter_turns(self):
        for shape in ('rotated_rect', 'rotated_pill'):
            for rotation in (90, 270, -90):
                with self.subTest(shape=shape, rotation=rotation):
                    extents = self.extents(dict(type='pcb_smtpad', shape=shape, width=.8999982, height=.2800096, x=3, y=-2, ccw_rotation=rotation))
                    self.assertAlmostEqual(extents[0], .2800096)
                    self.assertAlmostEqual(extents[1], .8999982)

    def test_rotated_smt_general_angle(self):
        for shape in ('rotated_rect', 'rotated_pill'):
            w, h = self.extents(dict(type='pcb_smtpad', shape=shape, width=4, height=2, x=0, y=0, ccw_rotation=30))
            self.assertAlmostEqual(w, 4*math.cos(math.pi/6)+1)
            self.assertAlmostEqual(h, 2+2*math.cos(math.pi/6))

    def test_slot_outer_annulus_and_rotation(self):
        e = dict(type='pcb_plated_hole', shape='pill', outer_width=1.2, outer_height=2, hole_width=.8, hole_height=1.5, x=7, y=4, ccw_rotation=90)
        self.assertAlmostEqual(self.extents(e)[0], 2)
        self.assertAlmostEqual(self.extents(e)[1], 1.2)
        e['ccw_rotation'] = 45
        self.assertAlmostEqual(self.extents(e)[0], 3.2/math.sqrt(2))

    def test_circle_annulus_uses_outer_diameter(self):
        self.assertEqual(self.extents(dict(type='pcb_plated_hole', shape='circle', outer_diameter=1.6, hole_diameter=1, x=0, y=0)), (1.6, 1.6))

    def test_polygon_is_already_in_world_coordinates(self):
        e = dict(type='pcb_smtpad', shape='polygon', ccw_rotation=90, points=[dict(x=1,y=2),dict(x=3,y=2),dict(x=3,y=5)])
        self.assertEqual(module.geometry_bounds(e), ([1,2],[3,5]))

    def test_unknown_shapes_fail_closed(self):
        for kind in ('pcb_smtpad', 'pcb_plated_hole'):
            with self.assertRaises(ValueError):
                module.geometry_bounds(dict(type=kind, shape='unrecognized', x=0, y=0, width=1, height=1))

    def test_nonfinite_and_missing_dimensions_fail(self):
        with self.assertRaises(ValueError):
            module.geometry_bounds(dict(type='pcb_smtpad', shape='rotated_pill', width=1, height=2, x=0,y=0,ccw_rotation=float('nan')))
        with self.assertRaises(KeyError):
            module.geometry_bounds(dict(type='pcb_plated_hole', shape='circle', hole_diameter=1,x=0,y=0))

    def test_preserved_native_evidence_includes_dnp_copper(self):
        folder = ROOT/'references/reconstructed-placement-final'
        circuit = json.loads((folder/'circuit.json').read_text())
        placement = json.loads((folder/'placement.json').read_text())
        baseline = json.loads((folder/'baseline.placement.json').read_text())
        report = module.audit(circuit, placement, baseline)
        self.assertTrue(report['independent_geometry_pass'])
        self.assertAlmostEqual(report['DNP_inclusive_min_conservative_AABB_gap_mm'], .16)
        self.assertEqual(sum(report['rotated_smt_shape_counts'].values()), 40)
        self.assertEqual(report['native_top_level_errors'], {'pcb_component_outside_board_error':2})
        self.assertEqual(report['native_nested_errors'], {})
        # Demonstrate DNP is not discarded: force a DNP pad onto fitted copper.
        dnp_ids = {e['pcb_component_id'] for e in circuit if e['type']=='pcb_component' and e.get('do_not_place')}
        dnp = next(e for e in circuit if e['type']=='pcb_smtpad' and e['pcb_component_id'] in dnp_ids and e.get('shape')=='rect')
        fitted = next(e for e in circuit if e['type']=='pcb_smtpad' and e['pcb_component_id'] not in dnp_ids and e.get('layer')==dnp['layer'] and e.get('shape')=='rect')
        dnp['x'], dnp['y'] = fitted['x'], fitted['y']
        report = module.audit(circuit, placement, baseline)
        self.assertFalse(report['independent_geometry_pass'])
        self.assertEqual(report['DNP_inclusive_min_conservative_AABB_gap_mm'], 0)


if __name__ == '__main__':
    unittest.main()
