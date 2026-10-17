#!/usr/bin/env python3
"""Linear local refinement of a heuristic placement; independently audited later."""
import argparse
import itertools
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('input');a.add_argument('--omit-critical',action='store_true');a.add_argument('--clock-corridor',action='store_true');a.add_argument('--output',default='refined-placement.json');args=a.parse_args()
parts=json.loads((ROOT/'artifacts/compact-controller/placement-envelopes.json').read_text())['parts']
q=json.loads(Path(args.input).read_text())['placements'];cs=json.loads((ROOT/'config/compact-critical-pin-constraints.json').read_text())['constraints']
names=[p['name'] for p in parts];idx={n:i for i,n in enumerate(names)};N=len(names);rows=[];limits=[];labels=[]
def point(p,v):
 angle=math.radians(q[p['name']]['pcbRotation']-p['original_rotation']);c=round(math.cos(angle));s=round(math.sin(angle));return [c*v[0]-s*v[1],s*v[0]+c*v[1]]
def bbox(p,key):
 b=p[key];vs=[point(p,[x,y]) for x in [b[0],b[2]] for y in [b[1],b[3]]];return [min(v[0] for v in vs),min(v[1] for v in vs),max(v[0] for v in vs),max(v[1] for v in vs)]
def add(terms,limit,label):
 row=np.zeros(4*N)
 for col,v in terms:row[col]+=v
 rows.append(row);limits.append(limit);labels.append(label)
def bound(i,axis,low,high,label):add([(2*i+axis,1)],high,label);add([(2*i+axis,-1)],-low,label)
for i,p in enumerate(parts):
 b=bbox(p,'construction_envelope_relative_mm');cu=bbox(p,'copper_relative_to_pivot_mm')
 bound(i,0,max(-14.14-b[0],-13.745-cu[0]),min(14.14-b[2],13.745-cu[2]),p['name']+' edgeX')
 bound(i,1,max(-14.14-b[1],-13.745-cu[1]),min(14.14-b[3],13.745-cu[3]),p['name']+' edgeY')
 for axis,key in [(0,'pcbX'),(1,'pcbY')]:
  add([(2*i+axis,1),(2*N+2*i+axis,-1)],q[p['name']][key],'shift+');add([(2*i+axis,-1),(2*N+2*i+axis,-1)],-q[p['name']][key],'shift-')
 if p['name'] in ['J_PD','J_DATA']:
  bound(i,0,-9.15,9.15,p['name']+' plugX');bound(i,1,-10.15,10.15,p['name']+' plugY')
 # Provisional carrier corner-head/tool envelope, not a motor rear thread.
 for xx in [-12.5,12.5]:
  mount=[xx-1.6,10.9,xx+1.6,14.1];pose=q[p['name']];bx=[b[0]+pose['pcbX'],b[1]+pose['pcbY'],b[2]+pose['pcbX'],b[3]+pose['pcbY']]
  vals=[mount[0]-bx[2],bx[0]-mount[2],mount[1]-bx[3],bx[1]-mount[3]];side=int(np.argmax(vals))
  if side==0:add([(2*i,1)],mount[0]-b[2]-.02,'mount left')
  elif side==1:add([(2*i,-1)],b[0]-mount[2]-.02,'mount right')
  elif side==2:add([(2*i+1,1)],mount[1]-b[3]-.02,'mount below')
  else:add([(2*i+1,-1)],b[1]-mount[3]-.02,'mount above')
chips=['0201','0402','0603','0805','1206']
def gap(a,b):
 if a=='QFN' or b=='QFN':return 1 if a!='other' and b!='other' else 0
 if a=='SOP' or b=='SOP':
  o=b if a=='SOP' else a;return .5 if o=='SOP' else .4 if o in chips+['SOT'] else 0
 if a=='SOT' or b=='SOT':
  o=b if a=='SOT' else a;return .4 if o=='SOT' else .2 if o in chips else 0
 if a in chips and b in chips:return .35 if a==b=='1206' else .25 if '1206' in [a,b] else .18 if any(c in ['0603','0805'] for c in [a,b]) else .15
 return 0
for (i,p),(j,r) in itertools.combinations(enumerate(parts),2):
 for key,g in [('construction_envelope_relative_mm',.001),('nominal_component_including_leads_relative_mm',gap(p['assembly_spacing_class'],r['assembly_spacing_class'])+.005)]:
  if p[key] is None or r[key] is None:continue
  b=bbox(p,key);c=bbox(r,key);pp=q[p['name']];rr=q[r['name']]
  vals=[c[0]+rr['pcbX']-b[2]-pp['pcbX'],b[0]+pp['pcbX']-c[2]-rr['pcbX'],c[1]+rr['pcbY']-b[3]-pp['pcbY'],b[1]+pp['pcbY']-c[3]-rr['pcbY']];side=int(np.argmax(vals));label=p['name']+' / '+r['name']+' '+key
  if side==0:add([(2*i,1),(2*j,-1)],c[0]-b[2]-g,label)
  elif side==1:add([(2*j,1),(2*i,-1)],b[0]-c[2]-g,label)
  elif side==2:add([(2*i+1,1),(2*j+1,-1)],c[1]-b[3]-g,label)
  else:add([(2*j+1,1),(2*i+1,-1)],b[1]-c[3]-g,label)
if args.clock_corridor:
 i=idx['Y_MCU'];j=idx['U_MCU'];yy=bbox(parts[i],'copper_relative_to_pivot_mm')[3];mm=bbox(parts[j],'copper_relative_to_pivot_mm')[1]
 add([(2*i+1,1),(2*j+1,-1)],mm-yy-.55,'Reserved top-layer crystal escape corridor')
if not args.omit_critical:
 for an,ap,bn,bp,d in cs:
  i=idx[an];j=idx[bn];aa=point(parts[i],parts[i]['pin_centers_relative_mm'][ap]);bb=point(parts[j],parts[j]['pin_centers_relative_mm'][bp])
  for sx,sy in itertools.product([-1,1],repeat=2):add([(2*i,sx),(2*j,-sx),(2*i+1,sy),(2*j+1,-sy)],d-sx*(aa[0]-bb[0])-sy*(aa[1]-bb[1]),an+' -> '+bn+' critical')
c=np.concatenate([np.zeros(2*N),np.ones(2*N)])
result=linprog(c,A_ub=np.array(rows),b_ub=np.array(limits),bounds=[(None,None)]*(2*N)+[(0,None)]*(2*N),method='highs')
report={'scope':'Local LP placement construction; routing, solid and manufacturing checks are separate','success':result.success,'message':result.message,'constraints':len(rows),'critical_pin_constraints_enabled':not args.omit_critical,'manufacturing_release':False}
if result.success:
 report['placements']={n:dict(pcbX=round(float(result.x[2*i]),7),pcbY=round(float(result.x[2*i+1]),7),pcbRotation=q[n]['pcbRotation']) for i,n in enumerate(names)}
 report['total_absolute_displacement_mm']=float(result.fun)
if not result.success:
 # A common nonnegative slack diagnoses construction conflicts; it never
 # converts a failed placement into an accepted candidate.
 relax=linprog(np.concatenate([np.zeros(4*N),[1]]),A_ub=np.column_stack([rows,-np.ones(len(rows))]),b_ub=limits,bounds=[(None,None)]*(2*N)+[(0,None)]*(2*N)+[(0,None)],method='highs')
 if relax.success:
  residual=np.dot(rows,relax.x[:-1])-limits
  report['minimum_common_constraint_relaxation_mm']=float(relax.x[-1])
  report['conflicting_constraints']=[{'constraint':labels[i],'violation_mm':float(residual[i])} for i in np.flatnonzero(residual>1e-5)]
path=ROOT/'artifacts/compact-controller'/args.output;path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['placements','conflicting_constraints']}))
