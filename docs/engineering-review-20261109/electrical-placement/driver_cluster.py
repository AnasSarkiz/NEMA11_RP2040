from pathlib import Path
exec(open(str(Path(__file__).parent/'review.py')).read().split('for r in pairs:print(r)')[0])
placements=json.loads((B/'config/placement.json').read_text())['placements']; comps={e['pcb_component_id']:src[e['source_component_id']] for e in x if e['type']=='pcb_component'}
geoms=[]
for e in x:
 if e['type'] in ['pcb_smtpad','pcb_plated_hole','pcb_courtyard_outline']:
  lo,hi=geo.geometry_bounds(e);geoms.append(dict(name=comps[e['pcb_component_id']],lo=lo,hi=hi,layers=e.get('layers',[e.get('layer')]),kind=e['type'],pin=pp.get(e.get('pcb_port_id'),(None,None))[1]))
def moved(g,name,cx,cy,angle):
 o=placements[name];th=math.radians(angle-o['pcbRotation']);c,s=round(math.cos(th)),round(math.sin(th));corners=[(cx+c*(u-o['pcbX'])-s*(v-o['pcbY']),cy+s*(u-o['pcbX'])+c*(v-o['pcbY'])) for u in [g['lo'][0],g['hi'][0]] for v in [g['lo'][1],g['hi'][1]]];return dict(g,lo=[min(v[k] for v in corners) for k in [0,1]],hi=[max(v[k] for v in corners) for k in [0,1]])
def legal(gs,obstacles):
 for a in gs:
  if min(a['lo'])< -13.85 or max(a['hi'])>13.85:return False
  for cx in [-11.5,11.5]:
   for cy in [-11.5,11.5]:
    if math.hypot(max(a['lo'][0]-cx,cx-a['hi'][0],0),max(a['lo'][1]-cy,cy-a['hi'][1],0))<2.50:return False
  for b in obstacles:
   if not set(a['layers'])&set(b['layers']):continue
   if a['kind']=='pcb_courtyard_outline' and b['kind']=='pcb_courtyard_outline':
    if geo.gap(a,b)<0.05:return False
   elif a['kind']!='pcb_courtyard_outline' and b['kind']!='pcb_courtyard_outline' and geo.gap(a,b)<0.15:return False
 return True
jobs=[('C_VM',[(1,'U_DRV',22),(1,'U_DRV',28),(2,'U_DRV',29)]),('R_SA',[(1,'U_DRV',23),(2,'U_DRV',29)]),('R_SB',[(1,'U_DRV',27),(2,'U_DRV',29)]),('C_CP',[(1,'U_DRV',4),(2,'U_DRV',5)]),('C_VCP',[(1,'U_DRV',6),(2,'C_VM',1)]),('C_VREG',[(1,'U_DRV',8),(2,'U_DRV',29)]),('C_DRV_LOGIC',[(1,'U_DRV',15),(2,'U_DRV',18)]),('C_REF',[(1,'U_DRV',17),(2,'U_DRV',18)])]
pending={n for n,t in jobs}
results=[]
for name,targets in jobs:
 own=[g for g in geoms if g['name']==name];obs=[g for g in geoms if g['name']!=name and g['name'] not in pending]; tgs=[(str(p),pads[(a,str(q))]) for p,a,q in targets];anchor=tgs[0][1][0];ax=sum(anchor['lo'][0:1]+anchor['hi'][0:1])/2;ay=(anchor['lo'][1]+anchor['hi'][1])/2;best=None
 for rot in [0,90,180,270]:
  for i in range(-16,17):
   for j in range(-16,17):
    cx=round(ax+i*.25,4);cy=round(ay+j*.25,4);gs=[moved(g,name,cx,cy,rot) for g in own];ds=[min(geo.gap(g,t) for g in gs if g['pin']==p for t in ts) for p,ts in tgs];score=sum(ds)
    if best and score>=best['score']:continue
    if not legal(gs,obs):continue
    best=dict(name=name,pcbX=cx,pcbY=cy,pcbRotation=rot,layer=placements[name]['layer'],score=score,distances=[round(v,4) for v in ds],targets=targets)
 results.append(best);print(best,flush=True)
 if best:
  gs=[moved(g,name,best['pcbX'],best['pcbY'],best['pcbRotation']) for g in own]
  geoms=[g for g in geoms if g['name']!=name]+gs
  for key in list(pads):
   if key[0]==name:pads[key]=[g for g in gs if g['pin']==key[1]]
  placements[name].update({k:best[k] for k in ['pcbX','pcbY','pcbRotation']})
  pending.remove(name)
(O/'driver_cluster_candidates.json').write_text(json.dumps(results,indent=2))
