"""Check retained geometry constraints, not actual motor fit or assembly approval."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MechanicalContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('runner', ROOT / 'scripts/run_milestone_checks.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        if not runner.fresh_receipt(ROOT):
            raise AssertionError('Fresh complete-input native receipt required')
        cls.records = json.loads((ROOT / 'dist/index/circuit.json').read_text())
        cls.components = {r['name']: r for r in cls.records if r['type'] == 'source_component'}
        cls.placements = {r['source_component_id']: r for r in cls.records if r['type'] == 'pcb_component'}

    def test_existing_motor_axes_and_provisional_keepouts(self):
        axes = {(x, y) for x in (-11.5, 11.5) for y in (-11.5, 11.5)}
        holes = [r for r in self.records if r['type'] == 'pcb_hole' and r.get('pcb_component_id') is None]
        self.assertEqual(len(holes), 4)
        self.assertEqual({(r['x'], r['y']) for r in holes}, axes)
        for r in holes:
            self.assertEqual(r['hole_shape'], 'circle')
            self.assertEqual(r['hole_diameter'], 2.7)
        keepouts = [r for r in self.records if r['type'] == 'pcb_keepout']
        self.assertEqual(len(keepouts), 4)
        self.assertEqual({(r['center']['x'], r['center']['y']) for r in keepouts}, axes)
        for r in keepouts:
            self.assertEqual(r['shape'], 'circle')
            self.assertEqual(r['radius'], 2.35)
            self.assertEqual(set(r['layers']), {'top', 'bottom'})
            self.assertFalse(r['allow_placements'])

    def test_edge_anchors_and_no_offboard_exemptions(self):
        anchors = {'J_PD': (0, 8.65, 180), 'J_DATA': (8.65, 0, 90),
                   # Reviewed placement-only adjustment; motor hole axes unchanged.
                   'J_MOTOR': (3.874997, -11.1, 180), 'C_BULK': (-4.9, -9, 90),
                   'U_DRV': (2, -3.2, 270)}
        for name, (x, y, angle) in anchors.items():
            pose = self.placements[self.components[name]['source_component_id']]
            self.assertEqual(pose['layer'], 'top', name)
            self.assertAlmostEqual(pose['footprint_origin']['x'], x, places=6, msg=name)
            self.assertAlmostEqual(pose['footprint_origin']['y'], y, places=6, msg=name)
            self.assertEqual(pose['rotation'] % 360, angle, name)
        self.assertFalse(any(p.get('is_allowed_to_be_off_board', False) for p in self.placements.values()))

    def test_optional_encoder_and_construction_limits_retained(self):
        for name in ('U_ENCODER', 'C_ENCODER', 'C_ENCODER_BULK'):
            pose = self.placements[self.components[name]['source_component_id']]
            self.assertTrue(pose['do_not_place'], name)
        encoder = self.placements[self.components['U_ENCODER']['source_component_id']]
        self.assertEqual(encoder['footprint_origin'], {'x': 0, 'y': 0})
        board = next(r for r in self.records if r['type'] == 'pcb_board')
        for key, value in {'min_trace_width': 0.16, 'min_via_hole_diameter': 0.30,
                           'min_via_pad_diameter': 0.45, 'min_board_edge_clearance': 0.25,
                           'min_pad_edge_to_pad_edge_clearance': 0.15}.items():
            self.assertEqual(board[key], value, key)


if __name__ == '__main__':
    unittest.main()
