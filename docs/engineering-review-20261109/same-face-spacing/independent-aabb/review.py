"""Offline nominal whole-model AABB screen; no native build or network."""
import argparse
import json,math,pathlib,numpy as np,itertools,hashlib

def validate_transform(e, pcb):
 if e['rotation']['x'] != 0 or e['rotation']['y'] not in (0,180):
  raise ValueError('Unsupported X/Y model rotation')
 if e.get('size') or e.get('model_board_normal_direction') or e.get('model_unit_to_mm_scale_factor',1)!=1:
  raise ValueError('Unsupported model fit, orientation or scale')
 if pcb['layer'] not in ('top','bottom') or (e['rotation']['y']==180)!=(pcb['layer']=='bottom'):
  raise ValueError('Model rotation and PCB side disagree')
 if pcb.get('do_not_place'):
  raise ValueError('Unexpected DNP model')
 if '/imports/' not in e['model_obj_url'] or '://' in e['model_obj_url']:
  raise ValueError('Expected a local imported model')

def gap(a,b):
 return math.hypot(*[max(a['lo'][k]-b['hi'][k],b['lo'][k]-a['hi'][k],0) for k in range(2)])

def same_face_pairs(rows):
 return ((a,b) for a,b in itertools.combinations(rows,2) if a['side']==b['side'] and a['name']!=b['name'])

def calc(path,order,B,R):
 x=json.load(path.open());names={e['source_component_id']:e['name'] for e in x if e['type']=='source_component'};pc={e['pcb_component_id']:e for e in x if e['type']=='pcb_component'};rows=[]
 for e in x:
  if e['type']!='cad_component':continue
  validate_transform(e, pc[e['pcb_component_id']])
  p=(B/'imports'/e['model_obj_url'].split('/imports/')[-1]).resolve()
  if not p.is_relative_to((B/'imports').resolve()): raise ValueError('OBJ path escapes board imports')
  v=np.array([list(map(float,l.split()[1:4])) for l in p.read_text().splitlines() if l.startswith('v ')])-np.array([e['model_origin_position'][k] for k in 'xyz'])
  for axis in order:
   a=math.radians(e['rotation'][axis]);c,s=math.cos(a),math.sin(a);m={'x':[[1,0,0],[0,c,-s],[0,s,c]],'y':[[c,0,s],[0,1,0],[-s,0,c]],'z':[[c,-s,0],[s,c,0],[0,0,1]]}[axis];v=v@np.array(m).T
  v+=np.array([e['position'][k] for k in 'xyz']);rows.append(dict(name=names[e['source_component_id']],side=pc[e['pcb_component_id']]['layer'],lo=v.min(axis=0).tolist(),hi=v.max(axis=0).tolist(),model=str(p.relative_to(R))))
 return rows

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--repo',type=pathlib.Path,required=True)
 parser.add_argument('--output',type=pathlib.Path,default=pathlib.Path(__file__).parent)
 args=parser.parse_args()
 R=args.repo.resolve(); O=args.output.resolve(); O.mkdir(parents=True,exist_ok=True)
 B=R/'boards/nema11-rp2040-two-layer--20261022-a1'
 base=B/'references/reconstructed-placement-final/circuit.json'; cand=B/'references/electrical-placement-20261109/integrated.circuit.json'
 official=json.loads((R/'docs/engineering-review-20261109/underside-envelope/official-loader-bounds.json').read_text())
 off={e['name']:e for e in official}
 assert len(official)==89 and len(off)==89, 'Official baseline must have 89 unique names'
 good=None
 for order in ['xyz','zyx']:
  rows=calc(base,order,B,R)
  assert len(rows)==89 and len(off)==89 and {r['name'] for r in rows}==set(off), 'Baseline/official 89-name mismatch'
  err=max(abs(a-b) for r in rows for a,b in zip(r['lo']+r['hi'],off[r['name']]['min']+off[r['name']]['max']));print(order,err)
  if err<1e-7: good=order
 if good is None: raise ValueError('No transform order agrees with official baseline bounds')
 rows=calc(cand,good,B,R)
 assert len(rows)==89 and {r['name'] for r in rows}==set(off), 'Candidate model-name mismatch'
 pairs=[]
 for a,b in same_face_pairs(rows):
  d=gap(a,b)
  if d<.65:pairs.append(dict(a=a['name'],b=b['name'],side=a['side'],whole_model_AABB_gap=d))
 pairs.sort(key=lambda r:r['whole_model_AABB_gap']);result=dict(scope='Whole imported OBJ model XY AABB screening, not body-only, no native build',input=str(cand.relative_to(R)),sha256=hashlib.sha256(cand.read_bytes()).hexdigest(),verified_transform_order=good,rows=rows,pairs=pairs);(O/'model_spacing.json').write_text(json.dumps(result,indent=2));print(json.dumps(pairs,indent=2))
 for path in [base,cand]:
  x=json.load(path.open())
  names={e['source_component_id']:e['name'] for e in x if e['type']=='source_component'}; pc={e['pcb_component_id']:e for e in x if e['type']=='pcb_component'}
  cy=[]
  for e in x:
   if e['type']!='pcb_courtyard_outline' or pc[e['pcb_component_id']].get('do_not_place'):continue
   v=np.array([[p['x'],p['y']] for p in e['outline']]);cy.append(dict(name=names[pc[e['pcb_component_id']]['source_component_id']],side=e['layer'],lo=v.min(axis=0).tolist(),hi=v.max(axis=0).tolist()))
  cp=[]
  for a,b in same_face_pairs(cy):
   d=gap(a,b)
   if d<.2:cp.append(dict(a=a['name'],b=b['name'],side=a['side'],courtyard_AABB_gap=d))
  print(path.name,'courtyard count',len(cy),'pairs<.2',len(cp));(O/(path.stem+'-courtyard.json')).write_text(json.dumps(cp,indent=2))
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Rectangle,Circle
 fig,axes=plt.subplots(1,2,figsize=(16,8))
 for ax,side in zip(axes,['top','bottom']):
  ax.add_patch(Rectangle((-14,-14),28,28,fill=False,color='black'))
  for xx in [-11.5,11.5]:
   for yy in [-11.5,11.5]:ax.add_patch(Circle((xx,yy),2.35,fill=False,color='orange',linestyle='--'))
  for r in rows:
   if r['side']!=side:continue
   lo,hi=r['lo'],r['hi'];ax.add_patch(Rectangle(lo[:2],hi[0]-lo[0],hi[1]-lo[1],facecolor='lightblue',edgecolor='navy',alpha=.6));ax.text((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,r['name'],ha='center',va='center',fontsize=5)
  ax.set(xlim=(-15,15),ylim=(-15,15),aspect='equal',title=f'{side}: whole-model XY AABBs, top-view coordinates',xlabel='mm',ylabel='mm')
 fig.suptitle('Saved isolated candidate, nominal imported models only. Not body-only, native render or manufacturing approval.')
 fig.tight_layout();fig.savefig(O/'model-xy-screen.png',dpi=160)

if __name__=='__main__':
 main()
