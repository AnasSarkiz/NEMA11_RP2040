import unittest
from review import gap, same_face_pairs, validate_transform

class GeometryTests(unittest.TestCase):
 def box(self,name,side,lo,hi):return dict(name=name,side=side,lo=lo,hi=hi)
 def test_axis_gap(self):
  self.assertAlmostEqual(gap(self.box('a','top',[0,0],[1,1]),self.box('b','top',[1.2,0],[2,1])),.2)
 def test_diagonal_gap(self):
  self.assertEqual(gap(self.box('a','top',[0,0],[1,1]),self.box('b','top',[4,5],[6,6])),5)
 def test_overlap_zero(self):
  self.assertEqual(gap(self.box('a','top',[0,0],[2,2]),self.box('b','top',[1,1],[3,3])),0)
 def test_opposite_faces_excluded(self):
  rows=[self.box('a','top',[0,0],[1,1]),self.box('b','bottom',[0,0],[1,1]),self.box('c','top',[2,2],[3,3])]
  self.assertEqual([(a['name'],b['name']) for a,b in same_face_pairs(rows)],[('a','c')])
 def test_unsupported_transform_rejected(self):
  with self.assertRaises(ValueError):validate_transform(dict(rotation=dict(x=90,y=0,z=0)),dict(layer='top'))

if __name__=='__main__':unittest.main()
