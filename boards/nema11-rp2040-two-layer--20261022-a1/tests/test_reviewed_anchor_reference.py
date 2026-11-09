"""Explicitly constrain the one reviewed historical-anchor change."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReviewedAnchorReference(unittest.TestCase):
    def test_only_reviewed_motor_header_x_changed(self):
        old=json.loads((ROOT/'references/reconstructed-placement-final/baseline.placement.json').read_text())['placements']
        new=json.loads((ROOT/'references/electrical-placement-20261109/anchor-reference.json').read_text())['placements']
        self.assertEqual(set(new),{'J_PD','J_DATA','J_MOTOR','C_BULK','U_DRV','U_ESD','C_ESD','U_ENCODER'})
        for name,pose in new.items():
            expected=dict(old[name])
            if name=='J_MOTOR':
                self.assertEqual(expected['pcbX'],3.9)
                expected['pcbX']=3.874997
            self.assertEqual(pose,expected,name)


if __name__=='__main__':
    unittest.main()
