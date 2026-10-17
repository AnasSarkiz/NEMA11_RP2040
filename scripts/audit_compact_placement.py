#!/usr/bin/env python3
"""Independent native pad/assembly-envelope audit; never a routing certificate."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from shapely.affinity import rotate,translate
from shapely.geometry import Polygon,Point,box
from pcb_geometry import Copper,pad_shape
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--folder',default='artifacts/compact-controller');parser.add_argument('--placement');parser.add_argument('--USB-escape',action='store_true',dest='usb_escape');args=parser.parse_args();OUT=ROOT/args.folder
path=OUT/'unrouted.circuit.json';records=json.loads(path.read_text());base=json.loads((ROOT/'artifacts/controller/unrouted.circuit.json').read_text());samples=json.loads((ROOT/'artifacts/compact-controller/supplier-samples.circuit.json').read_text());envelopes=json.loads((ROOT/'artifacts/compact-controller/placement-envelopes.json').read_text())['parts'];poses=json.loads((ROOT/'src/compact/placement.json').read_text());
placement_report=json.loads(Path(args.placement).read_text()) if args.placement else {}
if args.placement:poses.update(placement_report['placements'])
oldposes=json.loads((ROOT/'src/controller/supplier-placement.json').read_text());errors=[]
C=Copper(records);B=Copper(base);S=Copper(samples)
def named_pads(c):
 result={}
 for e in c.records:
  if e['type'] not in ['pcb_smtpad','pcb_plated_hole']:continue
  sp=c.source[c.ports[e['pcb_port_id']]['source_port_id']];result[(c.names[sp['source_component_id']],sp['pin_number'])]=e
 return result
pads=named_pads(C);oldpads=named_pads(B);samplepads=named_pads(S)
for (name,pin),pad in pads.items():
 if name=='BZ1':original=samplepads[('BZ_COMPACT',pin)];old=dict(pcbX=-10,pcbY=0,pcbRotation=0)
 else:original=oldpads[(name,pin)];old=oldposes[name]
 new=poses[name];expected=translate(rotate(pad_shape(original),new['pcbRotation']-old['pcbRotation'],origin=(old['pcbX'],old['pcbY'])),new['pcbX']-old['pcbX'],new['pcbY']-old['pcbY'])
 difference=expected.hausdorff_distance(pad_shape(pad))
 if difference>1e-5:errors.append({'part':name,'pin':pin,'supplier_copper_changed_mm':difference})

elements=C.elements();shorts=[];min_gap=100;pad_clearances=0
for (a,ka,sa),(b,kb,sb) in itertools.combinations(elements,2):
 if ka is not None and ka==kb:continue
 for layer in sa.keys() & sb.keys():
  d=sa[layer].distance(sb[layer]);min_gap=min(min_gap,d);pad_clearances+=1
  if d<.15-1e-6:errors.append({'foreign_pad_clearance_mm':d,'required_mm':.15,'a':a.get('pcb_smtpad_id',a.get('pcb_plated_hole_id')),'b':b.get('pcb_smtpad_id',b.get('pcb_plated_hole_id')),'layer':layer})
  if sa[layer].intersects(sb[layer]):shorts.append([a.get('pcb_port_id'),b.get('pcb_port_id'),layer])
board=next(e for e in records if e['type']=='pcb_board');outline=Polygon([(v['x'],v['y']) for v in board['outline']]);min_edge=100
for e,k,shapes in elements:
 for shape in shapes.values():
  d=shape.distance(outline.boundary);min_edge=min(min_edge,d)
  if not outline.covers(shape) or d<.25-1e-6:errors.append({'copper_edge_clearance_mm':d,'element':e.get('pcb_port_id')})
body_bounds={};courts={};constraints=[]
for p in envelopes:
 name=p['name']
 if name not in C.names.values():continue
 q=poses[name];angle=q['pcbRotation']-p['original_rotation']
 if p['nominal_component_including_leads_relative_mm'] is not None:
  body_bounds[name]=translate(rotate(box(*p['nominal_component_including_leads_relative_mm']),angle,origin=(0,0)),q['pcbX'],q['pcbY'])
for e in records:
 if e['type']=='pcb_courtyard_outline':
  pc=next(p for p in records if p['type']=='pcb_component' and p['pcb_component_id']==e['pcb_component_id'])
  if pc['layer']=='top':courts[C.names[pc['source_component_id']]]=Polygon([(v['x'],v['y']) for v in e['outline']])
for a,b in itertools.combinations(courts,2):
 if courts[a].intersection(courts[b]).area>1e-8:errors.append({'courtyard_overlap':[a,b]})
spacing=json.loads((ROOT/'artifacts/requirements/compact-JLC-component-spacing.json').read_text());classes={p['name']:p['assembly_spacing_class'] for p in envelopes};chips=spacing['chip_classes'];checked=0;minimum_spacing_surplus=100
for a,b in itertools.combinations(body_bounds,2):
 aa,bb=classes[a],classes[b];g=None
 if aa in chips and bb in chips:g=spacing['chip_spacing_mm'][chips.index(aa)][chips.index(bb)]
 elif aa in chips:g=spacing['chip_to_package_spacing_mm'].get(bb)
 elif bb in chips:g=spacing['chip_to_package_spacing_mm'].get(aa)
 else:g=spacing['other_pairs_mm'].get(aa+','+bb,spacing['other_pairs_mm'].get(bb+','+aa))
 if g is None:continue
 actual=body_bounds[a].distance(body_bounds[b]);checked+=1;minimum_spacing_surplus=min(minimum_spacing_surplus,actual-g)
 if actual<g-1e-6:errors.append({'JLC_component_spacing':[a,b],'actual_mm':actual,'required_mm':g})
for name,shape in body_bounds.items():
 if not box(-14.15,-14.15,14.15,14.15).covers(shape):errors.append({'component_frame':name,'bounds':shape.bounds})
parts={p['name']:p for p in envelopes}
def pin(name,number):
 p=parts[name];x,y=p['pin_centers_relative_mm'][number];q=poses[name];a=math.radians(q['pcbRotation']-p['original_rotation']);c=round(math.cos(a));s=round(math.sin(a));return [c*x-s*y+q['pcbX'],s*x+c*y+q['pcbY']]
critical=json.loads((ROOT/'config/compact-critical-pin-constraints.json').read_text())['constraints']
if args.usb_escape:critical += [['R_DM','1','U_MCU','46',3.0],['R_DP','1','U_MCU','47',3.0]]
anchors={(v['a'],v['b']):v for v in placement_report.get('power_copper_connection_anchors',[])} if args.usb_escape else {}
allowed_anchors={('L_BUCK.1','U_BUCK.5'),('C_BUCK_OUT1.1','L_BUCK.2'),('C_BUCK_OUT2.1','L_BUCK.2'),('C_USB.1','U_MCU.48')}
if not set(anchors)<=allowed_anchors:errors.append({'unexpected_power_anchor_links':sorted(set(anchors)-allowed_anchors)})
for an,ap,bn,bp,maximum in critical:
 aa=pin(an,ap);bb=pin(bn,bp);measurement='pin centres'
 if (an+'.'+ap,bn+'.'+bp) in anchors:
  anchor=anchors[(an+'.'+ap,bn+'.'+bp)];positions=[]
  for name,number,which in [(an,ap,'a'),(bn,bp,'b')]:
   offset=anchor[which+'_relative_mm'];position=[poses[name]['pcbX']+offset[0],poses[name]['pcbY']+offset[1]]
   shape=pad_shape(pads[(name,int(number))])
   if not shape.buffer(-.049).covers(Point(*position)):errors.append({'power_anchor_outside_original_copper':[name,number],'position_mm':position})
   positions.append(position)
  aa,bb=positions;measurement='points verified at least 0.049 mm inside unchanged native copper'
 d=sum(abs(x-y) for x,y in zip(aa,bb));constraints.append({'a':an+'.'+ap,'b':bn+'.'+bp,'L1_mm':d,'maximum_construction_budget_mm':maximum,'measurement':measurement})
 if d>maximum+1e-6:errors.append({'critical_pin_budget':[an,bn],'actual_mm':d,'maximum_mm':maximum})
components=[e for e in records if e['type']=='pcb_component'];fitted=[e for e in components if not e.get('do_not_place')]
if any(e['layer']!='top' for e in fitted):errors.append({'fitted_component_on_bottom':True})
mount_checks=[]
for h in (e for e in records if e['type']=='pcb_hole' and not e.get('pcb_component_id')):
 keepout=next((e for e in records if e['type']=='pcb_keepout' and abs(e['center']['x']-h['x'])<1e-6 and abs(e['center']['y']-h['y'])<1e-6),None)
 if keepout is None:
  errors.append({'mount_without_head_keepout':h});continue
 head=Point(h['x'],h['y']).buffer(keepout['radius'],quad_segs=64)
 for name,shape in courts.items():
  if shape.intersection(head).area>1e-8:errors.append({'mount_head_courtyard_overlap':name,'mount':[h['x'],h['y']]})
 # This mechanical exclusion already includes the fastener-head allowance.
 # Copper-to-copper clearance does not add another gap to a non-copper head.
 head_copper_gap=min(shape.distance(head) for e,k,shapes in elements for shape in shapes.values())
 for e,k,shapes in elements:
  if any(shape.intersection(head).area>1e-8 for shape in shapes.values()):errors.append({'mount_head_copper_overlap':e.get('pcb_port_id'),'mount':[h['x'],h['y']]})
 mount_checks.append({'centre_mm':[h['x'],h['y']],'hole_diameter_mm':h['hole_diameter'],'head_keepout_radius_mm':keepout['radius'],'minimum_copper_to_head_keepout_mm':head_copper_gap,'hole_edge_to_PCB_edge_mm':outline.boundary.distance(Point(h['x'],h['y']))-h['hole_diameter']/2,'head_within_28_3mm_frame':box(-14.15,-14.15,14.15,14.15).covers(head)})
 if not mount_checks[-1]['head_within_28_3mm_frame']:errors.append({'mount_head_outside_frame':mount_checks[-1]})
report={'PCB_mounts':mount_checks,'scope':'Unrouted compact full-circuit placement, supplier copper and nominal envelopes only','circuit_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'components':len(components),'fitted_parts':len(fitted),'all_fitted_on_top':all(e['layer']=='top' for e in fitted),'original_supplier_pad_geometries_verified':len(pads),'top_courtyards_checked':len(courts),'foreign_pad_clearance_comparisons':pad_clearances,'minimum_foreign_pad_clearance_mm':min_gap,'minimum_copper_edge_clearance_mm':min_edge,'nominal_component_spacing_pairs_checked':checked,'minimum_JLC_spacing_surplus_mm':minimum_spacing_surplus,'critical_pin_construction_distances':constraints,'nominal_fitted_envelopes_within_28_3mm_frame':not any('component_frame' in e for e in errors),'PCB_outline_mm':[28,28],'shorted_pad_pairs':shorts,'routing_traces':sum(e['type']=='pcb_trace' for e in records),'physical_routing_complete':False,'placement_pass':not errors and not shorts,'manufacturer_tolerances_verified':False,'manufacturing_release':False,'errors':errors}
(OUT/'placement-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='critical_pin_construction_distances'}));raise SystemExit(bool(errors or shorts))
