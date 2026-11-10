import copy
import json
import unittest
from pathlib import Path
import audit

HERE = Path(__file__).resolve().parent


class OppositeUsbScreen(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((HERE/'baseline-geometry.json').read_text())
        self.geometry = self.fixture['geometry']
        self.poses = self.fixture['placement']['placements']

    def test_saved_results_reproduce(self):
        self.assertEqual(audit.run(), json.loads((HERE/'results.json').read_text()))

    def test_all_candidates_remain_rejected(self):
        for result in audit.run()['candidates'].values():
            self.assertFalse(result['candidate_adopted'])
            self.assertFalse(result['native_build_run'])
            self.assertFalse(result['historical_frozen_anchors_unchanged'])
            self.assertTrue(result['copper_AABB_pairs_below_015mm'])

    def test_empty_transform_is_identity(self):
        self.assertEqual(audit.transform(self.geometry, self.poses, {}), self.geometry)

    def test_inputs_not_modified(self):
        before = copy.deepcopy(self.geometry)
        new = {'J_DATA': dict(self.poses['J_DATA'], pcbX=0, pcbY=-8.65, pcbRotation=0)}
        audit.transform(self.geometry, self.poses, new)
        self.assertEqual(self.geometry, before)

    def test_quarter_turn_round_trip(self):
        new = {'J_DATA': dict(self.poses['J_DATA'], pcbX=0, pcbY=-8.65, pcbRotation=0)}
        out = audit.transform(self.geometry, self.poses, new)
        back = audit.transform(out, dict(self.poses, **new), {'J_DATA': self.poses['J_DATA']})
        for a,b in zip(self.geometry,back):
            if a['type'] not in {'pcb_smtpad','pcb_plated_hole','pcb_courtyard_outline'}:
                continue
            for aa,bb in zip(audit.geometry.geometry_bounds(a),audit.geometry.geometry_bounds(b)):
                for x,y in zip(aa,bb):
                    self.assertAlmostEqual(x,y,places=10)

    def test_source_population_and_mount_axes_retained(self):
        self.assertEqual(sum(e['type']=='source_component' for e in self.geometry),99)
        axes={(e['center']['x'],e['center']['y']) for e in self.geometry if e['type']=='pcb_keepout'}
        self.assertEqual(axes,{(-11.5,-11.5),(-11.5,11.5),(11.5,-11.5),(11.5,11.5)})

    def test_nonquarter_turn_rejected(self):
        with self.assertRaises(ValueError):
            audit.transform(self.geometry,self.poses,{'J_DATA':dict(self.poses['J_DATA'],pcbRotation=37)})

    def test_nonfinite_and_layer_flip_rejected(self):
        for changes in ({'pcbX':float('nan')},{'layer':'bottom'}):
            with self.assertRaises(ValueError):
                audit.transform(self.geometry,self.poses,{'J_DATA':dict(self.poses['J_DATA'],**changes)})

    def test_unknown_component_rejected(self):
        with self.assertRaises(ValueError):
            audit.transform(self.geometry,self.poses,{'missing':self.poses['J_DATA']})


if __name__=='__main__':
    unittest.main()
