"""Offline regression of the pinned counterfactual, never mutable dist output."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'references/opposite-usb-20261110'
spec=importlib.util.spec_from_file_location('opposite_geometry',ROOT/'scripts/audit_opposite_usb_geometry.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OppositeUsbGeometry(unittest.TestCase):
    def setUp(self):
        self.circuit=json.loads((REF/'counterfactual-geometry.json').read_text())
        self.poses=json.loads((REF/'anchor-reference.json').read_text())

    def report(self):return module.audit(self.circuit,self.poses,self.poses)

    def test_pinned_counterfactual_passes_without_approving_native_boundary(self):
        r=self.report()
        self.assertTrue(r['independent_geometry_pass'])
        self.assertFalse(r['usb_courtyard_boundary_approval'])
        self.assertGreaterEqual(r['copper_min_conservative_AABB_gap_mm'],.15)
        self.assertGreaterEqual(r['npth_min_conservative_copper_gap_mm'],.25)
        self.assertGreaterEqual(r['copper_min_conservative_edge_gap_mm'],.25)
        self.assertGreaterEqual(r['minimum_conservative_bolt_head_envelope_gap_mm'],.07499)
        self.assertTrue(all(x<-.25 for x in r['usb_courtyard_edge_gaps_mm'].values()))
        saved=json.loads((REF/'counterfactual-screen.json').read_text())
        saved.pop('evidence_kind')
        self.assertEqual(r,saved)

    def test_active_poses_and_opposite_edge_orientations(self):
        current=json.loads((ROOT/'config/placement.json').read_text())
        self.assertEqual(current['placements'],self.poses['placements'])
        p=current['placements']
        self.assertEqual((p['J_PD']['pcbX'],p['J_PD']['pcbY'],p['J_PD']['pcbRotation']),(0,8.65,180))
        self.assertEqual((p['J_DATA']['pcbX'],p['J_DATA']['pcbY'],p['J_DATA']['pcbRotation']),(3.8,-8.65,0))
        self.assertFalse(current['placement_pass'])

    def test_missing_or_changed_locator_fails_closed(self):
        i=next(i for i,e in enumerate(self.circuit) if e['type']=='pcb_hole' and e.get('pcb_component_id'))
        self.circuit[i]['hole_diameter']=.4
        with self.assertRaises(ValueError):self.report()
        self.circuit.pop(i)
        with self.assertRaises(ValueError):self.report()

    def test_moved_motor_axis_fails_closed(self):
        next(e for e in self.circuit if e['type']=='pcb_hole' and not e.get('pcb_component_id'))['x']+=.1
        with self.assertRaises(ValueError):self.report()

    def test_npth_collision_with_other_component_copper_fails(self):
        h=next(e for e in self.circuit if e['type']=='pcb_hole' and e.get('pcb_component_id'))
        e=next(e for e in self.circuit if e['type']=='pcb_smtpad' and e['shape']=='rect' and e['pcb_component_id']!=h['pcb_component_id'])
        e['x'],e['y']=h['x'],h['y']
        r=self.report();self.assertFalse(r['independent_geometry_pass']);self.assertTrue(r['npth_copper_pairs_below_025mm'])

    def test_npth_body_overlap_fails(self):
        h=next(e for e in self.circuit if e['type']=='pcb_hole' and e.get('pcb_component_id'))
        e=next(e for e in self.circuit if e['type']=='pcb_courtyard_outline' and e['pcb_component_id']!=h['pcb_component_id'])
        e['outline']=[{'x':h['x']+x,'y':h['y']+y} for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        r=self.report();self.assertFalse(r['independent_geometry_pass']);self.assertTrue(r['npth_body_overlaps'])

    def test_dnp_copper_remains_included(self):
        ids={e['pcb_component_id'] for e in self.circuit if e['type']=='pcb_component' and e.get('do_not_place')}
        dnp=next(e for e in self.circuit if e['type']=='pcb_smtpad' and e['pcb_component_id'] in ids)
        other=next(e for e in self.circuit if e['type']=='pcb_smtpad' and e['pcb_component_id'] not in ids and e.get('layer')==dnp.get('layer') and 'x' in e)
        dnp['x'],dnp['y']=other['x'],other['y']
        self.assertFalse(self.report()['independent_geometry_pass'])

    def test_fitted_courtyard_overlap_is_not_copper_pass(self):
        bodies=[e for e in self.circuit if e['type']=='pcb_courtyard_outline' and e.get('layer')=='top']
        bodies[2]['outline']=copy.deepcopy(bodies[0]['outline'])
        r=self.report();self.assertFalse(r['independent_geometry_pass']);self.assertTrue(r['fitted_courtyard_overlap_pairs'])

    def test_stale_native_pose_and_nonfinite_pose_fail_closed(self):
        component=next(e for e in self.circuit if e['type']=='pcb_component')
        for value in (42,float('nan')):
            component['footprint_origin']['x']=value
            with self.assertRaises(ValueError):self.report()

    def test_nonfinite_hole_geometry_fails_closed(self):
        hole=next(e for e in self.circuit if e['type']=='pcb_hole')
        for key in ('x','y','hole_diameter'):
            old=hole[key];hole[key]=float('nan')
            with self.assertRaises(ValueError):self.report()
            hole[key]=old

    def test_duplicate_locator_cannot_replace_missing_locator(self):
        indexes=[i for i,e in enumerate(self.circuit) if e['type']=='pcb_hole' and e.get('pcb_component_id')]
        self.circuit[indexes[1]]=copy.deepcopy(self.circuit[indexes[0]])
        with self.assertRaises(ValueError):self.report()

    def test_same_connector_locator_to_copper_is_checked(self):
        h=next(e for e in self.circuit if e['type']=='pcb_hole' and e.get('pcb_component_id'))
        e=next(e for e in self.circuit if e['type']=='pcb_smtpad' and e.get('shape')=='rect' and e['pcb_component_id']==h['pcb_component_id'])
        e['x'],e['y']=h['x'],h['y']
        r=self.report();self.assertFalse(r['independent_geometry_pass']);self.assertTrue(r['npth_own_copper_pairs_below_015mm'])

    def test_board_center_cannot_silently_shift_edge_rules(self):
        next(e for e in self.circuit if e['type']=='pcb_board')['center']['x']=1
        with self.assertRaises(ValueError):self.report()

    def test_bulk_physical_rotation_preserves_positive_and_ground_pins(self):
        pose=self.poses['placements']['C_BULK']
        self.assertEqual(pose['pcbRotation'],270)
        sources={e['source_component_id']:e['name'] for e in self.circuit if e['type']=='source_component'}
        cid=next(e['pcb_component_id'] for e in self.circuit if e['type']=='pcb_component' and sources[e['source_component_id']]=='C_BULK')
        pads={pin:e for e in self.circuit if e['type']=='pcb_smtpad' and e['pcb_component_id']==cid for pin in e['port_hints']}
        self.assertGreater(pads['pin1']['y'],pose['pcbY'])
        self.assertLess(pads['pin2']['y'],pose['pcbY'])
        wiring=json.loads((ROOT/'config/connections.json').read_text())['components']['C_BULK']['connections']
        self.assertEqual(wiring,{'1':'PD_VBUS','2':'GND'})
        review=json.loads((REF/'bulk-rotation-review.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT/'config/connections.json').read_bytes()).hexdigest(),review['unchanged_connections_sha256'])

    def test_new_review_artifact_hashes_match(self):
        manifest=json.loads((REF/'artifact-hashes.json').read_text())
        for name,expected in manifest['files'].items():
            self.assertEqual(hashlib.sha256((REF/name).read_bytes()).hexdigest(),expected,name)

    def test_all_actual_test_pads_clear_fitted_courtyards(self):
        r=self.report()
        self.assertEqual(len(r['testpoint_pad_edge_to_fitted_courtyard']),7)
        self.assertEqual(r['testpoint_centers_inside_fitted_courtyards'],[])
        self.assertEqual(r['testpoint_pad_courtyard_overlaps'],[])
        self.assertFalse(r['probe_access_qualified'])
        self.assertGreaterEqual(min(x['pad_edge_gap_mm'] for x in r['testpoint_pad_edge_to_fitted_courtyard']),.1999)

    def test_original_native_testpoint_error_is_preserved(self):
        review=json.loads((REF/'testpoint-access-review.json').read_text())
        self.assertEqual(review['initial_fresh_native_sha256'],'11d68f0dcf975618857600955ad9aa564c7c25f97412d5123aa413c222dd7a3f')
        self.assertEqual(review['initial_native_testpoint_error'][0]['message'],'Test point TP_BOOT_GND is not accessible because it is inside the courtyard of U_DRV')
        self.assertEqual(review['before_center_exclusions'],[['TP_BOOT_GND','U_DRV']])
        self.assertEqual({x['testpoint'] for x in review['before_full_pad_overlaps']},{'TP_BOOT','TP_BOOT_GND','TP_3V3'})

    def test_boot_ground_courtyard_access_regression(self):
        names={e['source_component_id']:e['name'] for e in self.circuit if e['type']=='source_component'}
        ids={e['pcb_component_id']:names[e['source_component_id']] for e in self.circuit if e['type']=='pcb_component'}
        pad=next(e for e in self.circuit if e['type']=='pcb_smtpad' and ids[e['pcb_component_id']]=='TP_BOOT_GND')
        pad['x'],pad['y']=4.9911,1.435391
        r=self.report()
        self.assertFalse(r['independent_geometry_pass'])
        self.assertIn(['TP_BOOT_GND','U_DRV'],r['testpoint_centers_inside_fitted_courtyards'])

    def test_partial_pad_overlap_without_center_inclusion(self):
        names={e['source_component_id']:e['name'] for e in self.circuit if e['type']=='source_component'}
        ids={e['pcb_component_id']:names[e['source_component_id']] for e in self.circuit if e['type']=='pcb_component'}
        pad=next(e for e in self.circuit if e['type']=='pcb_smtpad' and ids[e['pcb_component_id']]=='TP_BOOT')
        pad['x'],pad['y']=4.9911,2.695392
        r=self.report()
        self.assertFalse(r['independent_geometry_pass'])
        self.assertNotIn(['TP_BOOT','U_DRV'],r['testpoint_centers_inside_fitted_courtyards'])
        self.assertTrue(any(x['testpoint']=='TP_BOOT' and x['body']=='U_DRV' for x in r['testpoint_pad_courtyard_overlaps']))

    def test_testpoint_screen_uses_actual_polygon_not_rectangle_proxy(self):
        triangle=[{'x':0,'y':0},{'x':1,'y':0},{'x':0,'y':1}]
        distance,inside=module.circle_outline_gap(.9,.9,.1,triangle)
        self.assertFalse(inside)
        self.assertGreater(distance,.4)
        distance,inside=module.circle_outline_gap(.2,.2,.1,triangle)
        self.assertTrue(inside)
        self.assertLess(distance,0)

    def test_limiting_nominal_pairs_are_identified(self):
        r=self.report()
        body=r['fitted_courtyard_limiting_pair']
        self.assertEqual({body['a'],body['b']},{'C_BUZZER','R_DM'})
        self.assertAlmostEqual(body['conservative_gap_mm'],r['fitted_courtyard_min_conservative_gap_mm'])
        tab=r['plated_tab_body_limiting_pair']
        self.assertEqual({tab['a'],tab['b']},{'R_PWR_LED','J_MOTOR'})
        self.assertAlmostEqual(tab['conservative_gap_mm'],r['plated_tab_body_min_conservative_gap_mm'])

    def test_circle_rectangle_distances_and_positive_clearance(self):
        b={'lo':[0,0],'hi':[1,1]}
        self.assertAlmostEqual(module.circle_bounds_gap(1.75,.5,.5,b),.25)
        self.assertLess(module.circle_bounds_gap(1.7499999,.5,.5,b),.25)
        self.assertEqual(module.circle_bounds_gap(.5,.5,.5,b),-.5)


if __name__=='__main__':unittest.main()
