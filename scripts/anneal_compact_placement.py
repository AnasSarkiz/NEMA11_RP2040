#!/usr/bin/env python3
"""Heuristic compact placement construction, with explicit residual reporting."""
import argparse
import itertools
import json
import math
import random
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--seconds',type=float,default=120);a.add_argument('--seed',type=int,default=11);a.add_argument('--mounts',type=int,choices=[0,2,4],default=2);a.add_argument('--start');a.add_argument('--no-buzzer',action='store_true');a.add_argument('--USB-escape',action='store_true',dest='usb_escape');args=a.parse_args()
data=json.loads((ROOT/'artifacts/compact-controller/placement-envelopes.json').read_text())
parts=[p for p in data['parts'] if not args.no_buzzer or p['name'] not in ['BZ1','Q_BUZZER','D_BUZZER','R_BUZZER_GATE','R_BUZZER_PD','C_BUZZER']];poses=json.loads((ROOT/'src/controller/supplier-placement.json').read_text())
constraints=json.loads((ROOT/'config/compact-critical-pin-constraints.json').read_text())['constraints']
if args.usb_escape:constraints += [['R_DM','1','U_MCU','46',3.0],['R_DP','1','U_MCU','47',3.0]]
preferred={'U_MCU':(-.5,.5),'U_DRV':(2,-8),'U_PD':(-9,5),'J_PD':(-5.5,10),'J_DATA':(5.5,10),'J_MOTOR':(10.9,1),'C_BULK':(-8,-9),'BZ1':(10,-10),'L_BUCK':(-10,-2.8),'U_BUCK':(-11,1)}
def rotate(v,r):
 c=round(math.cos(math.radians(r*90)));s=round(math.sin(math.radians(r*90)));return [c*v[0]-s*v[1],s*v[0]+c*v[1]]
def rb(b,r):
 p=[rotate([x,y],r) for x in [b[0],b[2]] for y in [b[1],b[3]]];return [min(v[0] for v in p),min(v[1] for v in p),max(v[0] for v in p),max(v[1] for v in p)]
chips=['0201','0402','0603','0805','1206']
def gap(a,b):
 if a=='QFN' or b=='QFN':return 1.0 if a!='other' and b!='other' else 0
 if a=='SOP' or b=='SOP':
  other=b if a=='SOP' else a;return .5 if other=='SOP' else .4 if other in chips+['SOT'] else 0
 if a=='SOT' or b=='SOT':
  other=b if a=='SOT' else a;return .4 if other=='SOT' else .2 if other in chips else 0
 if a in chips and b in chips:return .35 if a==b=='1206' else .25 if '1206' in [a,b] else .18 if any(c in ['0603','0805'] for c in [a,b]) else .15
 return 0
if args.mounts:
 for xx,yy in itertools.product([-12.5,12.5],[-12.5,12.5] if args.mounts==4 else [12.5]):
  name=f'MOUNT_{xx}_{yy}';parts.append(dict(name=name,original_rotation=0,construction_envelope_relative_mm=[-1.6,-1.6,1.6,1.6],copper_relative_to_pivot_mm=[-.9,-.9,.9,.9],nominal_component_including_leads_relative_mm=[-1.6,-1.6,1.6,1.6],assembly_spacing_class='other',pin_centers_relative_mm={}))
  preferred[name]=(xx,yy)
start_poses=json.loads(Path(args.start).read_text())['placements'] if args.start else {}
indices={p['name']:i for i,p in enumerate(parts)};pins={p['name']:list(p['pin_centers_relative_mm']) for p in parts}
lines=[f'{len(parts)} {len(constraints)} {args.seconds} {args.seed} {indices['Y_MCU']} {indices['U_MCU']} {indices['R_DP'] if args.usb_escape else -1} {indices['R_DM'] if args.usb_escape else -1}'];random.seed(args.seed)
for p in parts:
 name=p['name'];xmin=xmax=ymin=ymax=None
 bounds=[-14.15,14.15,-14.15,14.15];mask=15
 if name in ['J_PD','J_DATA']:mask=1;bounds=[-9.15,-4.25,7.5,10.15] if name=='J_PD' else [4.25,9.15,7.5,10.15]
 if name=='J_MOTOR':mask=2;bounds=[9.75,11.5,-2,4]
 if name=='U_MCU':mask=1;bounds=[-2,1.5,-2.5,1.5]
 if name=='U_DRV':bounds=[-1.5,7,-10.5,-4]
 if name=='U_PD':bounds=[-10.5,-5,0,7]
 if name.startswith('MOUNT_'):mask=1;xx,yy=preferred[name];bounds=[xx,xx,yy,yy]
 if name in preferred:xx,yy=preferred[name]
 else:
  parent=next((b for a,pa,b,pb,d in constraints if a==name and b in preferred),None)
  if parent:
   xx=poses[name]['pcbX']-poses[parent]['pcbX']+preferred[parent][0];yy=poses[name]['pcbY']-poses[parent]['pcbY']+preferred[parent][1]
  else:xx=random.uniform(-12,12);yy=random.uniform(-12,12)
 rr=1 if name=='J_MOTOR' else 0
 if name in start_poses:
  h=start_poses[name];xx=h['pcbX'];yy=h['pcbY'];rr=((h['pcbRotation']-p['original_rotation'])%360)//90
 if args.usb_escape:
  if name in ['J_PD','J_DATA']:bounds[3]=8.55
  rotations={'R_DP':90,'R_DM':90,'C_IO49':90,'C_DV50':90,'C_USB':0,'C_ADC':90,'C_VREG_OUT':90,'U_ESD':90}
  limits={'R_DP':[.8,3.2,4.9,6.0],'R_DM':[.8,3.5,4.9,6.0],'C_IO49':[-.6,1.6,5.5,6.6],'C_DV50':[-.6,1.6,5.5,6.6],'C_USB':[1.2,3,6,7],'C_ADC':[3.8,5.2,5.0,6.5],'C_VREG_OUT':[3,4,5.0,6.3],'U_ESD':[7,9.5,11.7,12.4]}
  rotations.update({'D_TVS':0,'U_FLASH':0,'C_FLASH':90,'U_TEMP':0})
  limits.update({'D_TVS':[-9,-6,11.5,12.8],'U_FLASH':[.3,1.4,8.8,9.6],'C_FLASH':[-.8,.2,12.0,13.0],'U_TEMP':[-12.3,-11.6,7.7,8.5]})
  if name=='J_MOTOR':bounds=[9.75,11.5,-3,-1.25]
  if name in rotations:
   rr=((rotations[name]-p['original_rotation'])%360)//90;mask=1<<rr;bounds=limits[name]
 lines.append(' '.join(map(str,[mask,*bounds,round(xx*20)/20,round(yy*20)/20,rr,len(pins[name])])))
 for r in range(4):
  values=[]
  for bbox in [p['construction_envelope_relative_mm'],p['nominal_component_including_leads_relative_mm'] or p['construction_envelope_relative_mm'],p['copper_relative_to_pivot_mm']]:
   vv=rb(bbox,r);values += [math.floor(vv[0]*20+1e-7)/20,math.floor(vv[1]*20+1e-7)/20,math.ceil(vv[2]*20-1e-7)/20,math.ceil(vv[3]*20-1e-7)/20]
  for key in pins[name]:values+=rotate(p['pin_centers_relative_mm'][key],r)
  lines.append(' '.join(map(str,values)))
for p,q in itertools.combinations(parts,2):lines.append(str(gap(p['assembly_spacing_class'],q['assembly_spacing_class'])))
for a,pa,b,pb,d in constraints:lines.append(' '.join(map(str,[indices[a],pins[a].index(pa),indices[b],pins[b].index(pb),d])))
binary=Path('/workspace/.cache/nema11-compact-placer')
source=ROOT/'scripts/anneal_compact_placement.cpp'
if not binary.exists() or source.stat().st_mtime>binary.stat().st_mtime:subprocess.run(['g++','-std=c++20','-O3',str(source),'-o',str(binary)],check=True)
r=subprocess.run([str(binary)],input='\n'.join(lines)+'\n',text=True,stdout=subprocess.PIPE,check=True)
rows=r.stdout.splitlines();score,iterations=rows[0].split();placements={}
for p,row in zip(parts,rows[1:]):
 xx,yy,rr=map(float,row.split());placements[p['name']]=dict(pcbX=xx,pcbY=yy,pcbRotation=(p['original_rotation']+int(rr)*90)%360)
report={'scope':'Heuristic placement construction; residual cost is not a DRC result','seconds':args.seconds,'seed':args.seed,'heuristic_cost':float(score),'iterations':int(iterations),'buzzer_omitted':args.no_buzzer,'provisional_PCB_mount_count':args.mounts,'placements':placements,'compact_routing_verified':False,'manufacturing_release':False}
path=ROOT/f'artifacts/compact-controller/annealed-placement-{args.seed}.json';path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='placements'}))
