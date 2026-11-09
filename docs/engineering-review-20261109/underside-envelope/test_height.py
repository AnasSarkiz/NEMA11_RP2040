import unittest
from audit_height import z_bounds


class HeightTests(unittest.TestCase):
    def cad(self, bottom=False, origin=0):
        return dict(rotation=dict(x=0,y=180 if bottom else 0,z=90),
                    position=dict(z=-.8 if bottom else .8),model_origin_position=dict(z=origin))

    def test_top_through_hole_tail(self):
        self.assertEqual(z_bounds(self.cad(), 'top', -3, 6, 1.6), [-2.2, 6.8])

    def test_bottom_origin_and_height(self):
        lo,hi=z_bounds(self.cad(True,-.02), 'bottom', -.02, 1.81, 1.6)
        self.assertAlmostEqual(lo,-2.63)
        self.assertAlmostEqual(hi,-.8)

    def test_unsupported_transform_rejected(self):
        for change in [dict(size=dict(x=1,y=1,z=1)),dict(model_unit_to_mm_scale_factor=10),dict(model_board_normal_direction='x+')]:
            with self.assertRaises(ValueError):
                z_bounds(self.cad()|change,'top',0,1,1.6)
        with self.assertRaises(ValueError):
            z_bounds(self.cad(True),'top',0,1,1.6)


if __name__ == '__main__':
    unittest.main()
