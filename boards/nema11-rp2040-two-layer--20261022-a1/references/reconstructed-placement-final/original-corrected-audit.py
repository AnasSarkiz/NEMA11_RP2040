import json,math,collections
from pathlib import Path
j=json.load(open('best-native/dist/index/circuit.json'));s={x['source_component_id']:x['name'] for x in j if x['type']=='source_component'};p={x['pcb_component_id']:x for x in j if x['type']=='pcb_component'};name={k:s[v['source_component_id']] for k,v in p.items()};pads=[];courts=[]
for x in j:
 typ=x['type']
 if typ not in ['pcb_smtpad','pcb_plated_hole','pcb_courtyard_outline']:continue
 if typ=='pcb_smtpad' and x.get('shape') not in ['rect','rotated_rect','pill','rotated_pill','circle','polygon']:raise ValueError('Unsupported SMT shape: '+str(x.get('shape')))
 n=name.get(x.get('pcb_component_id'))
 if not n:continue
 if typ=='pcb_courtyard_outline' or x.get('shape')=='polygon':
  pts=x.get('outline',x.get('points'));lo=[min(q[k] for q in pts) for k in ['x','y']];hi=[max(q[k] for q in pts) for k in ['x','y']]
 else:
  w=x.get('width',x.get('outer_width',x.get('outer_diameter',x.get('radius',0)*2)));h=x.get('height',x.get('outer_height',x.get('outer_diameter',x.get('radius',0)*2)))
  # Width/height are local for plated slots and rotated SMT rect/pill shapes.
  # circuit-to-svg applies a centered rotation after sizing; core carries ccwRotationDegrees.
  rotation=x.get('ccw_rotation',0) if typ=='pcb_plated_hole' or x.get('shape') in ['rotated_pill','rotated_rect'] else 0
  angle=math.radians(rotation);c=abs(math.cos(angle));ss=abs(math.sin(angle));w,h=w*c+h*ss,w*ss+h*c
  lo=[x['x']-w/2,x['y']-h/2];hi=[x['x']+w/2,x['y']+h/2]
 r={'name':n,'lo':lo,'hi':hi,'layers':x.get('layers',[x.get('layer')]),'id':x.get(typ+'_id'),'dnp':p[x['pcb_component_id']].get('do_not_place',False)}
 (courts if typ=='pcb_courtyard_outline' else pads).append(r)
def gap(a,b):return math.hypot(*[max(a['lo'][k]-b['hi'][k],b['lo'][k]-a['hi'][k],0) for k in [0,1]])
viol=[];dnpmin=99;minimum=99
for i,a in enumerate(pads):
 for b in pads[:i]:
  if a['name']==b['name'] or not set(a['layers'])&set(b['layers']):continue
  d=gap(a,b);minimum=min(minimum,d)
  if a['dnp'] or b['dnp']:dnpmin=min(dnpmin,d)
  if d<.15-1e-6:viol.append({'a':a['name'],'b':b['name'],'a_id':a['id'],'b_id':b['id'],'conservative_AABB_gap_mm':d})
edge=min(min(a['lo'][0]+14,a['lo'][1]+14,14-a['hi'][0],14-a['hi'][1]) for a in pads)
bolts=[(-11.5,-11.5),(-11.5,11.5),(11.5,-11.5),(11.5,11.5)]
boltmin=min(math.hypot(max(a['lo'][0]-x,x-a['hi'][0],0),max(a['lo'][1]-y,y-a['hi'][1],0))-2.35 for a in pads+courts for x,y in bolts)
ps=json.load(open('best-native/placement.json'))['placements'];old=json.load(open('baseline.placement.json'))['placements'];frozen=['J_PD','J_DATA','J_MOTOR','C_BULK','U_DRV','U_ESD','C_ESD','U_ENCODER']
report={'source_count':sum(x['type']=='source_component' for x in j),'pcb_count':len(p),'fitted_sides':dict(collections.Counter(v['layer'] for v in p.values() if not v.get('do_not_place'))),'frozen_anchors_unchanged':all(ps[n]==old[n] for n in frozen),'pcb_traces':sum(x['type']=='pcb_trace' for x in j),'pcb_vias':sum(x['type']=='pcb_via' for x in j),'copper_min_conservative_AABB_gap_mm':minimum,'DNP_inclusive_min_conservative_AABB_gap_mm':dnpmin,'copper_min_conservative_edge_gap_mm':edge,'minimum_conservative_bolt_head_envelope_gap_mm':boltmin,'conservative_pad_pairs_below_015mm':viol,'native_top_level_errors':dict(collections.Counter(x['type'] for x in j if 'error' in x['type'])),'native_nested_errors':dict(collections.Counter(y['type'] for x in j for y in x.get('related_errors',[])))}
rotated=[x for x in j if x['type']=='pcb_smtpad' and x.get('shape') in ['rotated_rect','rotated_pill']]
report['rotated_smt_shape_counts']={str(k):v for k,v in collections.Counter((x['shape'],x.get('ccw_rotation',0)) for x in rotated).items()}
example=next(x for x in pads if x['id']=='pcb_smtpad_201');report['rotation_regression_pad201_bounds']=example
assert abs((example['hi'][0]-example['lo'][0])-.2800096)<1e-8
assert abs((example['hi'][1]-example['lo'][1])-.8999982)<1e-8
json.dump(report,open('best-native/independent-geometry-audit.json','w'),indent=2);print(json.dumps(report,indent=2))
