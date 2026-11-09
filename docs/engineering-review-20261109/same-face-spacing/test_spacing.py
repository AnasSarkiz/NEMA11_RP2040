import copy
import math
import unittest

from audit_spacing import convex_distance, hull, pairs, transform


def square(x=0, y=0):
    return [(x,y), (x+1,y), (x+1,y+1), (x,y+1)]


class SpacingTests(unittest.TestCase):
    def test_hull_omits_interior_and_duplicate_points(self):
        self.assertEqual(hull(square()+[(.5,.5),(0,0)]), square())

    def test_disjoint_parallel(self):
        distance, a, b = convex_distance(square(), square(1.2))
        self.assertAlmostEqual(distance,.2)
        self.assertAlmostEqual(math.dist(a,b),distance)

    def test_diagonal_separation_and_symmetry(self):
        a,b=square(),square(2,2)
        self.assertAlmostEqual(convex_distance(a,b)[0], math.sqrt(2))
        self.assertAlmostEqual(convex_distance(a,b)[0], convex_distance(b,a)[0])

    def test_overlap_touch_and_containment_are_not_clear(self):
        for b in (square(.5),square(1),[(.2,.2),(.8,.2),(.5,.8)]):
            self.assertEqual(convex_distance(square(),b)[0],0)

    def test_crossing_edges_without_vertex_containment(self):
        self.assertEqual(convex_distance([(-2,-.1),(2,-.1),(2,.1),(-2,.1)],
            [(-.1,-2),(.1,-2),(.1,2),(-.1,2)])[0],0)

    def test_opposite_faces_are_not_same_face_pairs(self):
        rows=[dict(name='a',layer='top',projected_convex_hull=square()),
              dict(name='b',layer='bottom',projected_convex_hull=square()),
              dict(name='c',layer='top',projected_convex_hull=square(2))]
        self.assertEqual(len(pairs(rows)),1)
        self.assertEqual(len(pairs(rows,False)),2)
        self.assertEqual(pairs(rows)[0]['conservative_whole_model_convex_gap_mm'],1)

    def test_authored_origin_and_bottom_rotation(self):
        cad=dict(rotation=dict(x=0,y=180,z=90),model_origin_position=dict(x=1,y=2,z=3),
                 position=dict(x=10,y=20,z=-.8))
        self.assertEqual(transform(cad,[2,4,6]),[12,21,-3.8])
        bad=copy.deepcopy(cad)
        bad['model_unit_to_mm_scale_factor']=2
        with self.assertRaises(ValueError): transform(bad,[2,4,6])


if __name__=='__main__':
    unittest.main()
