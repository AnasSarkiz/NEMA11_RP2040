"""Continuous construction checks must reject real copper, drill and edge faults."""
import sys,unittest
from pathlib import Path
from shapely.geometry import box
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compact_via_geometry import via_site_errors,top_stub_errors
class Geometry:
 def __init__(self,elements):
  self._elements=elements;self.nets={'S':'SIGNAL','F':'FOREIGN'};self.ports={};self.source={};self.names={}
 def elements(self):return self._elements
class ViaConstructionTests(unittest.TestCase):
 def setUp(self):
  self.board={'type':'pcb_board','outline':[dict(x=x,y=y) for x,y in [(-5,-5),(5,-5),(5,5),(-5,5)]]}
  self.pad={'type':'pcb_smtpad','pcb_smtpad_id':'owner'}
 def test_ordinary_via_cannot_enter_an_unreviewed_land(self):
  c=Geometry([(self.pad,'S',{'top':box(-.3,-.2,.3,.2)})])
  self.assertTrue(via_site_errors([self.board],c,'S',0,0))
  self.assertEqual(via_site_errors([self.board],c,'S',0,0,allowed_pad_ids=['owner']),[])
 def test_reviewed_owner_never_exempts_foreign_bottom_copper(self):
  c=Geometry([(self.pad,'S',{'top':box(-.3,-.2,.3,.2)}),({'type':'pcb_smtpad','pcb_smtpad_id':'other'},'F',{'bottom':box(-.3,-.2,.3,.2)})])
  self.assertTrue(any('foreign copper' in e for e in via_site_errors([self.board],c,'S',0,0,allowed_pad_ids=['owner'])))
 def test_foreign_copper_clearance_is_not_rounded_away(self):
  c=Geometry([(self.pad,'F',{'top':box(-.3,-.2,.3,.2)})])
  self.assertTrue(via_site_errors([self.board],c,'S',.65,0))
  self.assertEqual(via_site_errors([self.board],c,'S',.7,0),[])
 def test_drill_web_below_point_two_is_rejected(self):
  hole={'type':'pcb_hole','pcb_hole_id':'hole','x':0,'y':0,'hole_diameter':.3}
  self.assertTrue(any('drill spacing' in e for e in via_site_errors([self.board,hole],Geometry([]),'S',.499,0)))
 def test_via_copper_to_board_edge_is_checked(self):
  self.assertTrue(via_site_errors([self.board],Geometry([]),'S',4.6,0))
 def test_via_annulus_must_clear_NPTH_even_when_drill_web_passes(self):
  hole={'type':'pcb_hole','pcb_hole_id':'USB_locator','x':0,'y':0,'hole_diameter':.71}
  self.assertTrue(any('copper to NPTH' in e for e in via_site_errors([self.board,hole],Geometry([]),'S',.715,0)))
  self.assertEqual(via_site_errors([self.board,hole],Geometry([]),'S',.8,0),[])
 def test_prescribed_stub_crossing_foreign_land_is_rejected(self):
  c=Geometry([(self.pad,'F',{'top':box(-.3,-.2,.3,.2)})])
  self.assertTrue(top_stub_errors([self.board],c,'S',[(-1,0),(1,0)]))
 def test_same_net_land_contact_remains_legal(self):
  c=Geometry([(self.pad,'S',{'top':box(-.3,-.2,.3,.2)})])
  self.assertEqual(top_stub_errors([self.board],c,'S',[(-1,0),(1,0)]),[])
