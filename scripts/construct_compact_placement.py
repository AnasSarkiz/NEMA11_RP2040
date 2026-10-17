#!/usr/bin/env python3
"""Construct a placement using real copper/model extents and explicit assembly rules.

Outputs are development candidates, never routing/assembly release certificates.
Supplier copper, models and original imports are unchanged. A 0.05 mm search
lattice rounds every envelope outwards. Native/solid audits remain mandatory.
"""
import argparse
import itertools
import json
import math
from pathlib import Path
from ortools.sat.python import cp_model

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--seconds',type=float,default=120)
parser.add_argument('--mounts',type=int,choices=[0,2],default=2)
parser.add_argument('--seed',type=int,default=11)
parser.add_argument('--fixed-core',action='store_true')
parser.add_argument('--fix',default='')
parser.add_argument('--omit-critical',action='store_true')
parser.add_argument('--explain',action='store_true')
parser.add_argument('--hint')
parser.add_argument('--radius',type=float,default=1.0)
args=parser.parse_args()
data=json.loads((ROOT/'artifacts/compact-controller/placement-envelopes.json').read_text())
m=cp_model.CpModel();S=20;FRAME=283;BOUND=283
ceil=lambda v:math.ceil(v*S-1e-7)
floor=lambda v:math.floor(v*S+1e-7)
nearest=lambda v:round(v*S)
def rotate(point,angle):
 c=round(math.cos(math.radians(angle)));s=round(math.sin(math.radians(angle)))
 return [c*point[0]-s*point[1],s*point[0]+c*point[1]]
def rb(b,angle):
 p=[rotate((x,y),angle) for x in [b[0],b[2]] for y in [b[1],b[3]]]
 return [min(t[0] for t in p),min(t[1] for t in p),max(t[0] for t in p),max(t[1] for t in p)]
variables={};ix=[];iy=[];objective=[]
preferred={'U_MCU':(-.5,.5),'U_DRV':(2,-8),'U_PD':(-9,5),'J_PD':(-5.5,10),'J_DATA':(5.5,10),
 'J_MOTOR':(10.9,1),'C_BULK':(-8,-9),'BZ1':(10,-10),'L_BUCK':(-10,-2.8),'U_BUCK':(-11,1)}
for p in sorted(data['parts'],key=lambda p:-p['bbox_area_mm2']):
 name=p['name'];x=m.new_int_var(-BOUND,BOUND,name+'_x');y=m.new_int_var(-BOUND,BOUND,name+'_y')
 angle=m.new_int_var(0,3,name+'_rotation_index')
 bounds=[rb(p['construction_envelope_relative_mm'],a) for a in [0,90,180,270]]
 copper=[rb(p['copper_relative_to_pivot_mm'],a) for a in [0,90,180,270]]
 body=[rb(p['nominal_component_including_leads_relative_mm'],a) for a in [0,90,180,270]] if p['nominal_component_including_leads_relative_mm'] else None
 def delta(values,label):
  v=m.new_int_var(min(values),max(values),name+'_'+label);m.add_element(angle,values,v);return v
 left=m.new_int_var(-600,600,name+'_left');bottom=m.new_int_var(-600,600,name+'_bottom')
 right=m.new_int_var(-600,600,name+'_right');top=m.new_int_var(-600,600,name+'_top')
 m.add(left==x+delta([floor(b[0]) for b in bounds],'lx'));m.add(bottom==y+delta([floor(b[1]) for b in bounds],'ly'))
 m.add(right==x+delta([ceil(b[2]) for b in bounds],'rx'));m.add(top==y+delta([ceil(b[3]) for b in bounds],'ry'))
 w=m.new_int_var(1,600,name+'_width');h=m.new_int_var(1,600,name+'_height')
 m.add(w==right-left);m.add(h==top-bottom)
 ix.append(m.new_interval_var(left,w,right,name+'_ix'));iy.append(m.new_interval_var(bottom,h,top,name+'_iy'))
 m.add(left>=-FRAME);m.add(right<=FRAME);m.add(bottom>=-FRAME);m.add(top<=FRAME)
 for coord,boxes,lo,hi in [(x,copper,0,2),(y,copper,1,3)]:
  m.add(coord+delta([floor(b[lo]) for b in boxes],'c'+str(lo))>=-275)
  m.add(coord+delta([ceil(b[hi]) for b in boxes],'c'+str(hi))<=275)
 bb=None
 if body:bb=[x+delta([floor(b[0]) for b in body],'bl'),y+delta([floor(b[1]) for b in body],'bb'),x+delta([ceil(b[2]) for b in body],'br'),y+delta([ceil(b[3]) for b in body],'bt')]
 pins={}
 for pin,point in p['pin_centers_relative_mm'].items():
  pts=[rotate(point,a) for a in [0,90,180,270]]
  pins[pin]=[x+delta([nearest(t[0]) for t in pts],'p'+pin+'x'),y+delta([nearest(t[1]) for t in pts],'p'+pin+'y')]
 if name in ['J_PD','J_DATA']:
  m.add(angle==0);m.add(x>=-183);m.add(x<=183);m.add(y<=203);m.add(y>=150)
 if name=='J_PD':m.add(x<=-85)
 if name=='J_DATA':m.add(x>=85)
 if name=='J_MOTOR':m.add(angle==1);m.add(x>=195)
 if name=='U_MCU':m.add(angle==0);m.add(x>=-40);m.add(x<=30);m.add(y>=-50);m.add(y<=30)
 if name=='U_DRV':m.add(y<=-80);m.add(x>=-30)
 if name=='U_PD':m.add(x<=-100);m.add(y>=0)
 variables[name]=dict(x=x,y=y,angle=angle,bounds=bounds,p=p,body=bb,pins=pins)
 if name in preferred:
  for axis,target in zip([x,y],preferred[name]):
   d=m.new_int_var(0,1132,name+'_pref');m.add_abs_equality(d,axis-nearest(target));objective.append(d)
assumptions={}
if args.fixed_core or args.fix:
 for name in (args.fix.split(',') if args.fix else ['U_MCU','U_DRV','U_PD','J_PD','J_DATA','J_MOTOR','C_BULK','BZ1','L_BUCK','U_BUCK']):
  v=variables[name];xx,yy=preferred[name]
  a=m.new_bool_var(name+'_fixed');assumptions[a.index]=name;m.add_assumption(a)
  m.add(v['x']==nearest(xx)).only_enforce_if(a);m.add(v['y']==nearest(yy)).only_enforce_if(a)
# Package-specific physical-component spacing, including protruding leads.
# JLC help table updated Sep 9 2026. Pad clearance is independently constrained.
chips=['0201','0402','0603','0805','1206']
def gap(a,b):
 if a=='QFN' or b=='QFN':return 1.0 if a!='other' and b!='other' else None
 if a=='SOP' or b=='SOP':
  other=b if a=='SOP' else a
  return .5 if other=='SOP' else .4 if other in chips+['SOT'] else None
 if a=='SOT' or b=='SOT':
  other=b if a=='SOT' else a
  return .4 if other=='SOT' else .2 if other in chips else None
 if a in chips and b in chips:
  if a==b=='1206':return .35
  if '1206' in [a,b]:return .25
  return .18 if any(c in ['0603','0805'] for c in [a,b]) else .15
 return None
pair_count=0
for (an,a),(bn,b) in itertools.combinations(variables.items(),2):
 g=gap(a['p']['assembly_spacing_class'],b['p']['assembly_spacing_class'])
 if g is None or not a['body'] or not b['body']:continue
 # The construction envelope already supplies >=0.20 mm. Larger rules need
 # a separate pair disjunction. Smaller rules are retained in the audit.
 if g<=.2:continue
 al,ab,ar,at=a['body'];bl,bb,br,bt=b['body'];v=[m.new_bool_var('sep') for _ in range(4)]
 for cond,on in zip([ar+ceil(g)<=bl,br+ceil(g)<=al,at+ceil(g)<=bb,bt+ceil(g)<=ab],v):m.add(cond).only_enforce_if(on)
 m.add_bool_or(v);pair_count+=1
constraints=[]
def close(a,pa,b,pb,max_mm,weight=3):
 if args.omit_critical:return
 av=variables[a]['pins'][str(pa)];bv=variables[b]['pins'][str(pb)]
 dx=m.new_int_var(0,1132,'pin_dx');dy=m.new_int_var(0,1132,'pin_dy')
 m.add_abs_equality(dx,av[0]-bv[0]);m.add_abs_equality(dy,av[1]-bv[1]);m.add(dx+dy<=floor(max_mm))
 objective.extend([weight*dx,weight*dy]);constraints.append([a,str(pa),b,str(pb),max_mm])
for suffix,pin in [('IO1',1),('IO10',10),('IO22',22),('IO33',33),('IO42',42),('IO49',49),('DV23',23),('DV50',50),('USB',48),('ADC',43),('VREG_IN',44),('VREG_OUT',45)]:close('C_'+suffix,1,'U_MCU',pin,2.8)
close('Y_MCU',1,'U_MCU',20,4.5,6);close('R_XOUT',1,'U_MCU',21,3.2,6);close('R_XOUT',2,'Y_MCU',3,2.5,6)
close('C_XIN',1,'Y_MCU',1,2.8);close('C_XOUT',1,'Y_MCU',3,2.8)
close('U_FLASH',1,'U_MCU',56,6);close('C_FLASH',1,'U_FLASH',8,3)
for a,pa,b,pb,d in [('R_SA',1,'U_DRV',23,2.8),('R_SB',1,'U_DRV',27,2.8),('C_CP',1,'U_DRV',4,3),('C_CP',2,'U_DRV',5,3),('C_VCP',1,'U_DRV',6,3),('C_VREG',1,'U_DRV',8,3),('C_DRV_LOGIC',1,'U_DRV',15,3),('C_VM',1,'U_DRV',28,3),('C_BUCK_IN',1,'U_BUCK',3,3),('C_BOOTSTRAP',1,'U_BUCK',6,2.5),('L_BUCK',1,'U_BUCK',5,3.5),('C_BUCK_OUT1',1,'L_BUCK',2,4),('C_BUCK_OUT2',1,'L_BUCK',2,4),('C_PD',1,'U_PD',1,3)]:close(a,pa,b,pb,d)
if args.mounts:
 for xx in [-12.5,12.5]:
  ix.append(m.new_fixed_size_interval_var(nearest(xx-1.6),64,'mount_x'))
  iy.append(m.new_fixed_size_interval_var(nearest(12.5-1.6),64,'mount_y'))
m.add_no_overlap_2d(ix,iy)
if args.hint:
 hints=json.loads(Path(args.hint).read_text())['placements']
 for name,v in variables.items():
  h=hints[name];r=((h['pcbRotation']-v['p']['original_rotation'])%360)//90
  a=m.new_bool_var(name+'_hint_fixed');assumptions[a.index]=name;m.add_assumption(a)
  m.add_hint(v['angle'],r)
  if name in ['U_MCU','J_MOTOR','J_PD','J_DATA']:m.add(v['angle']==r).only_enforce_if(a)
  for axis,key in [('x','pcbX'),('y','pcbY')]:
   m.add_hint(v[axis],nearest(h[key]));m.add(v[axis]>=nearest(h[key]-args.radius)).only_enforce_if(a);m.add(v[axis]<=nearest(h[key]+args.radius)).only_enforce_if(a)
m.minimize(sum(objective))
solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=args.seconds;solver.parameters.num_search_workers=8;solver.parameters.random_seed=args.seed
status=solver.solve(m)
report={'scope':'Full-circuit placement construction only; no routing or manufacturing release', 'status':solver.status_name(status),'frame_mm':[28.3,28.3],'PCB_mm':[28,28], 'all_fitted_on_top':True,'provisional_PCB_mount_count':args.mounts,'parts':len(variables),'pair_specific_spacing_constraints':pair_count,'critical_pin_distance_constraints':constraints,'search_lattice_mm':.05,'solver':'OR-Tools CP-SAT 9.14.6206','wall_seconds':solver.wall_time,'manufacturing_release':False,'compact_routing_verified':False,'original_supplier_copper_and_models_unchanged':True,'construction_envelope_is_not_a_qualified_supplier_courtyard':True}
if status in [cp_model.FEASIBLE,cp_model.OPTIMAL]:
 report['placements']={n:dict(pcbX=solver.value(v['x'])/S,pcbY=solver.value(v['y'])/S,pcbRotation=(v['p']['original_rotation']+solver.value(v['angle'])*90)%360) for n,v in variables.items()}
 report['objective']=solver.objective_value
if status==cp_model.INFEASIBLE:
 core=list(solver.sufficient_assumptions_for_infeasibility())
 if args.explain:
  for candidate in list(core):
   trial=[i for i in core if i!=candidate];m.clear_assumptions()
   m.add_assumptions([m.get_bool_var_from_proto_index(i) for i in trial])
   check=cp_model.CpSolver();check.parameters.max_time_in_seconds=.2;check.parameters.num_search_workers=1
   if check.solve(m)==cp_model.INFEASIBLE:core=trial
 report['infeasible_fixed_core_subset']=[assumptions.get(i,i) for i in core]
path=ROOT/f'artifacts/compact-controller/placement-construction-jlc-{args.mounts}-mounts.json'
path.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['placements','critical_pin_distance_constraints']}),flush=True)
