#!/usr/bin/env python3
"""Linear local refinement of a heuristic placement; independently audited later."""
import argparse
import itertools
import json
import math
import random
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('input');a.add_argument('--omit-critical',action='store_true');a.add_argument('--clock-corridor',action='store_true');a.add_argument('--USB-escape',action='store_true',dest='usb_escape');a.add_argument('--output',default='refined-placement.json');a.add_argument('--diagnose-critical',action='store_true');a.add_argument('--seed',type=int,default=0);a.add_argument('--IIS',action='store_true',dest='iis')
a.add_argument('--mount-count',type=int,choices=[2,4],default=2);a.add_argument('--no-buzzer',action='store_true');args=a.parse_args()
parts=json.loads((ROOT/'artifacts/compact-controller/placement-envelopes.json').read_text())['parts']
if args.no_buzzer:parts=[p for p in parts if p['name'] not in ['BZ1','Q_BUZZER','D_BUZZER','R_BUZZER_GATE','R_BUZZER_PD','C_BUZZER']]
q=json.loads(Path(args.input).read_text())['placements'];cs=json.loads((ROOT/'config/compact-critical-pin-constraints.json').read_text())['constraints']
if args.usb_escape:cs += [['R_DM','1','U_MCU','46',3.0],['R_DP','1','U_MCU','47',3.0]]
rng=random.Random(args.seed);switched=[]
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
 for xx,yy in itertools.product([-12.5,12.5],[-12.5,12.5] if args.mount_count==4 else [12.5]):
  mount=[xx-1.6,yy-1.6,xx+1.6,yy+1.6];pose=q[p['name']];bx=[b[0]+pose['pcbX'],b[1]+pose['pcbY'],b[2]+pose['pcbX'],b[3]+pose['pcbY']]
  vals=[mount[0]-bx[2],bx[0]-mount[2],mount[1]-bx[3],bx[1]-mount[3]]
  # The frame leaves no usable space outside or above a corner fastener.
  side=max([1 if xx<0 else 0,2 if yy>0 else 3],key=lambda direction:vals[direction])
  if args.usb_escape and yy>0 and p['name'] in ['J_PD','J_DATA']:side=2
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
 relations=[];pp=q[p['name']];rr=q[r['name']]
 for key,g in [('construction_envelope_relative_mm',.001),('nominal_component_including_leads_relative_mm',gap(p['assembly_spacing_class'],r['assembly_spacing_class'])+.005)]:
  if p[key] is None or r[key] is None:continue
  b=bbox(p,key);c=bbox(r,key)
  constants=[c[0]-b[2]-g,b[0]-c[2]-g,c[1]-b[3]-g,b[1]-c[3]-g]
  differences=[pp['pcbX']-rr['pcbX'],rr['pcbX']-pp['pcbX'],pp['pcbY']-rr['pcbY'],rr['pcbY']-pp['pcbY']]
  relations.append((key,constants,[v-w for v,w in zip(differences,constants)]))
 # Use a common separating direction for copper/body and package-pair rules.
 # Choosing independent directions can create artificial ordering cycles.
 scores=[max(v[2][axis] for v in relations) for axis in range(4)]
 order=sorted(range(4),key=lambda axis:scores[axis]);side=order[0]
 if args.seed and scores[order[1]]-scores[side]<.3 and rng.random()<.08:
  side=order[1];switched.append([p['name'],r['name'],side])
 for key,constants,violations in relations:
  label=p['name']+' / '+r['name']+' '+key
  if side==0:add([(2*i,1),(2*j,-1)],constants[0],label)
  elif side==1:add([(2*j,1),(2*i,-1)],constants[1],label)
  elif side==2:add([(2*i+1,1),(2*j+1,-1)],constants[2],label)
  else:add([(2*j+1,1),(2*i+1,-1)],constants[3],label)
if args.clock_corridor:
 i=idx['Y_MCU'];j=idx['U_MCU'];yy=bbox(parts[i],'copper_relative_to_pivot_mm')[3];mm=bbox(parts[j],'copper_relative_to_pivot_mm')[1]
 add([(2*i+1,1),(2*j+1,-1)],mm-yy-.55,'Reserved top-layer crystal escape corridor')
if args.usb_escape:
 i=idx['R_DP'];j=idx['R_DM']
 add([(2*i+1,1),(2*j+1,-1)],.1,'USB resistor row alignment');add([(2*j+1,1),(2*i+1,-1)],.1,'USB resistor row alignment')
 add([(2*i,1),(2*j,-1)],-.7,'USB resistor order/minimum pitch');add([(2*j,1),(2*i,-1)],.9,'USB resistor maximum pitch')
 # Leave a real top-layer bend corridor above the MCU lands. The resistor
 # copper must not cut off the outward USB_DM escape from adjacent pin 46.
 for n in ['R_DP','R_DM']:
  ri=idx[n];mi=idx['U_MCU'];res_bottom=bbox(parts[ri],'copper_relative_to_pivot_mm')[1];mcu_top=bbox(parts[mi],'copper_relative_to_pivot_mm')[3]
  add([(2*mi+1,1),(2*ri+1,-1)],res_bottom-mcu_top-.55,'USB top trace escape corridor')
power_anchor_proofs=[]
if not args.omit_critical:
 for an,ap,bn,bp,d in cs:
  i=idx[an];j=idx[bn];aa=point(parts[i],parts[i]['pin_centers_relative_mm'][ap]);bb=point(parts[j],parts[j]['pin_centers_relative_mm'][bp])
  # Power/decoupling lands are connection surfaces. Use fixed points 0.05 mm
  # inside their original rectangular copper, rather than requiring a trace
  # to travel to the centre of a 3.8 mm long inductor terminal. The original
  # 2.8/3.5/4.0 mm connection budgets remain unchanged. Final copper/trace checks
  # and the independent placement audit are still mandatory.
  if args.usb_escape and (an,bn) in [('L_BUCK','U_BUCK'),('C_BUCK_OUT1','L_BUCK'),('C_BUCK_OUT2','L_BUCK'),('C_USB','U_MCU')]:
   def anchor(part,pin,other):
    bounds=part['pin_copper_bounds_relative_mm'][pin]
    corners=[point(part,[x,y]) for x in [bounds[0],bounds[2]] for y in [bounds[1],bounds[3]]]
    lo=[min(t[k] for t in corners)+.05 for k in range(2)];hi=[max(t[k] for t in corners)-.05 for k in range(2)]
    pose=q[part['name']]
    return [min(hi[k],max(lo[k],other[k]-pose[['pcbX','pcbY'][k]])) for k in range(2)]
   world_a=[aa[k]+q[an][['pcbX','pcbY'][k]] for k in range(2)]
   world_b=[bb[k]+q[bn][['pcbX','pcbY'][k]] for k in range(2)]
   aa=anchor(parts[i],ap,world_b);bb=anchor(parts[j],bp,world_a)
   power_anchor_proofs.append(dict(a=an+'.'+ap,b=bn+'.'+bp,a_relative_mm=aa,b_relative_mm=bb,maximum_L1_mm=d,inset_mm=.05))
  for sx,sy in itertools.product([-1,1],repeat=2):add([(2*i,sx),(2*j,-sx),(2*i+1,sy),(2*j+1,-sy)],d-sx*(aa[0]-bb[0])-sy*(aa[1]-bb[1]),an+' -> '+bn+' critical')
c=np.concatenate([np.zeros(2*N),np.ones(2*N)])
result=linprog(c,A_ub=np.array(rows),b_ub=np.array(limits),bounds=[(None,None)]*(2*N)+[(0,None)]*(2*N),method='highs')
report={'scope':'Local LP placement construction; routing, solid and manufacturing checks are separate','buzzer_omitted':args.no_buzzer,'provisional_PCB_mount_count':args.mount_count,'success':result.success,'message':result.message,'constraints':len(rows),'separation_seed':args.seed,'alternative_separation_choices':switched,'critical_pin_constraints_enabled':not args.omit_critical,'manufacturing_release':False}
report['power_copper_connection_anchors']=power_anchor_proofs
if result.success:
 report['placements']={n:dict(pcbX=round(float(result.x[2*i]),7),pcbY=round(float(result.x[2*i+1]),7),pcbRotation=q[n]['pcbRotation']) for i,n in enumerate(names)}
 report['total_absolute_displacement_mm']=float(result.fun)
if not result.success and args.iis:
 from scipy.sparse import csr_matrix
 from scipy.optimize._highspy._core import _Highs,HighsLp,HighsIis,MatrixFormat
 lp=HighsLp();lp.num_col_=4*N;lp.num_row_=len(rows);lp.col_cost_=c
 lp.col_lower_=[-float('inf')]*(2*N)+[0]*(2*N);lp.col_upper_=[float('inf')]*(4*N)
 lp.row_lower_=[-float('inf')]*len(rows);lp.row_upper_=limits
 matrix=csr_matrix(rows);lp.a_matrix_.format_=MatrixFormat.kRowwise
 lp.a_matrix_.start_=matrix.indptr;lp.a_matrix_.index_=matrix.indices;lp.a_matrix_.value_=matrix.data
 h=_Highs();h.setOptionValue('output_flag',False);h.setOptionValue('time_limit',20.0);h.passModel(lp);h.run()
 iis=HighsIis();h.getIis(iis)
 report['infeasible_subsystem_valid']=iis.valid
 report['infeasible_subsystem']=[{'constraint':labels[i],'limit':limits[i],'terms':[(int(j),float(rows[i][j])) for j in np.flatnonzero(rows[i])]} for i in iis.row_index]
 print('IIS: '+json.dumps(report['infeasible_subsystem']),flush=True)
if not result.success and args.diagnose_critical:
 base_indices=[i for i,label in enumerate(labels) if not label.endswith(' critical')]
 critical_groups={}
 for i,label in enumerate(labels):
  if label.endswith(' critical'):critical_groups.setdefault(label,[]).append(i)
 chosen=base_indices[:];diagnostic=[]
 for label,indices in critical_groups.items():
  chosen+=indices
  test=linprog(c,A_ub=np.array(rows)[chosen],b_ub=np.array(limits)[chosen],bounds=[(None,None)]*(2*N)+[(0,None)]*(2*N),method='highs')
  if not test.success:
   diagnostic.append(label);chosen=chosen[:-len(indices)]
 report['critical_groups_conflicting_with_previous_accepted_groups']=diagnostic
 print('Conflicting critical groups: '+json.dumps(diagnostic),flush=True)
if not result.success:
 # A common nonnegative slack diagnoses construction conflicts; it never
 # converts a failed placement into an accepted candidate.
 relax=linprog(np.concatenate([np.zeros(4*N),[1]]),A_ub=np.column_stack([rows,-np.ones(len(rows))]),b_ub=limits,bounds=[(None,None)]*(2*N)+[(0,None)]*(2*N)+[(0,None)],method='highs')
 if relax.success:
  residual=np.dot(rows,relax.x[:-1])-limits
  report['minimum_common_constraint_relaxation_mm']=float(relax.x[-1])
  report['conflicting_constraints']=[{'constraint':labels[i],'violation_mm':float(residual[i])} for i in np.flatnonzero(residual>1e-5)]
path=ROOT/'artifacts/compact-controller'/args.output;path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['placements','conflicting_constraints']}))
