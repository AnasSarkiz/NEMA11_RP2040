import json,numpy as np
from scipy.optimize import minimize
from pathlib import Path
j=json.load(open('baseline.circuit.json')); p=json.load(open('config/placement.json')); names=list(p['placements']); ix={n:i for i,n in enumerate(names)}
s={x['source_component_id']:x['name'] for x in j if x['type']=='source_component'}; pcs={x['pcb_component_id']:s[x['source_component_id']] for x in j if x['type']=='pcb_component'}
orig=np.array([[p['placements'][n]['pcbX'],p['placements'][n]['pcbY']] for n in names]); start=orig.copy()
# Conservative courtyard boxes and emitted physical copper. Coordinates are offsets to actual footprint origin.
rect=[]
for x in j:
 n=pcs.get(x.get('pcb_component_id'))
 if not n:continue
 i=ix[n];typ=x['type'];z=None
 if typ=='pcb_courtyard_outline':
  pts=np.array([[q['x'],q['y']] for q in x['outline']]);lo=pts.min(0);hi=pts.max(0);z=((lo+hi)/2,(hi-lo)/2,[x['layer']],'body')
 elif typ in ('pcb_smtpad','pcb_plated_hole'):
  wh=np.array([x.get('width',x.get('outer_width',x.get('radius',0)*2)),x.get('height',x.get('outer_height',x.get('radius',0)*2))]);z=(np.array([x.get('x',x.get('center',{}).get('x',0)),x.get('y',x.get('center',{}).get('y',0))]),wh/2,x.get('layers',[x.get('layer')]),'copper')
 if z:rect.append((i,z[0]-orig[i],z[1],z[2],z[3]))
ri=np.array([r[0] for r in rect]);off=np.array([r[1] for r in rect]);half=np.array([r[2] for r in rect]); pairs=[]
for a in range(len(rect)):
 for b in range(a):
  if ri[a]==ri[b] or not set(rect[a][3])&set(rect[b][3]):continue
  # bodies with pads also checks through-hole underside mounting and DNP copper
  pairs.append((a,b,.16 if rect[a][4]==rect[b][4]=='copper' else .035))
a,b,clear=np.array(pairs).T;a=a.astype(int);b=b.astype(int);hs=half[a]+half[b]+clear[:,None]
frozen=['J_PD','J_DATA','J_MOTOR','C_BULK','U_DRV','U_ESD','C_ESD','U_ENCODER'];free=np.array([i for i,n in enumerate(names) if n not in frozen]);
# move the whole original MCU bypass/clock arrangement as a unit initially; optimizer keeps local constraints
mcu=['U_MCU','Y_MCU','R_XOUT','C_XIN','C_XOUT','C_IO1','C_IO10','C_IO22','C_IO33','C_IO42','C_IO49','C_ADC','C_USB','C_VREG_IN','C_VREG_OUT','C_DV23','C_DV50','R_DP','R_DM']
for n in mcu:start[ix[n]]+=np.array([-6,8])
start[ix['BZ1']]=[-10,0]
# explicit functional starting regions
for n,xy in {'U_PD':(0,9),'R_PD_CFG':(2,9),'C_PD':(0,11),'R_PD':(-2,10),'D_TVS':(0,12.5),'R_PG':(3,8),'D_PD':(-6,10),'D_DATA':(8,7),'R_CC1':(8,-3),'R_CC2':(9,-3),'R_USB_SENSE_H':(6,2),'R_USB_SENSE_L':(6,3),'R_FLASH_CS':(4,6),'R_BOOT':(4,7),'R_RUN':(-2,5),'R_VM_H':(5,-6),'R_VM_L':(6,-6),'C_VM_SENSE':(7,-6),'R_REF_H':(5,-7),'R_REF_L':(6,-7),'R_ENABLE':(5,-4),'R_SLEEP':(5,-5),'R_TEMP_SDA':(8,-7),'R_TEMP_SCL':(9,-7),'R_PWR_LED':(10,6)}.items():start[ix[n]]=xy
for c,y in zip('RGB',[9,6,3]):
 for n,xy in {f'Q_STATUS_{c}':(11,y),f'R_STATUS_{c}_PD':(12.5,y),f'R_STATUS_{c}_GATE':(9.5,y),f'R_STATUS_{c}':(11,y-1.5)}.items():start[ix[n]]=xy
for n,xy in {'Q_BUZZER':(-11,2),'R_BUZZER_PD':(-12,3),'R_BUZZER_GATE':(-10,3),'C_BUZZER':(-11,4),'D_BUZZER':(-11,0),'D_STATUS':(-11.5,6)}.items():start[ix[n]]=xy
# Soft local-distance constraints, no placement suppressions
links=[]
def link(n,m,d,w=1):links.append((ix[n],ix[m],d,w))
for n in mcu:
 if n!='U_MCU':link(n,'U_MCU',7 if n in ['Y_MCU','C_XOUT','R_XOUT','C_XIN'] else 6,2)
for n in ['R_XOUT','C_XIN','C_XOUT']:link(n,'Y_MCU',3,3)
for n in ['R_PD_CFG','C_PD','R_PD','R_PG']:link(n,'U_PD',3.8,2)
for n in ['C_BOOTSTRAP','C_BUCK_IN','L_BUCK','C_BUCK_OUT1','C_BUCK_OUT2']:link(n,'U_BUCK',5,2)
for c in 'RGB':
 for suffix in ['PD','GATE']:link(f'R_STATUS_{c}_{suffix}',f'Q_STATUS_{c}',2.2,5)
 link(f'R_STATUS_{c}',f'Q_STATUS_{c}',3,1)
for n in ['R_BUZZER_PD','R_BUZZER_GATE','D_BUZZER','C_BUZZER']:link(n,'Q_BUZZER',3,3)
for n in ['C_CP','C_VCP','C_VREG','C_DRV_LOGIC','C_VM','R_SA','R_SB','C_REF']:link(n,'U_DRV',5,2)
for n in ['C_TEMP','R_TEMP_SDA','R_TEMP_SCL']:link(n,'U_TEMP',3,1)
for n in ['C_FLASH','R_FLASH_CS','R_BOOT']:link(n,'U_FLASH',3,2)
li,lj,ld,lw=np.array(links).T;li=li.astype(int);lj=lj.astype(int)
# bolts use true rectangle-to-circle distances
bolts=np.array([[-11.5,-11.5],[-11.5,11.5],[11.5,-11.5],[11.5,11.5]])
edgeidx=np.array([k for k,r in enumerate(rect) if names[r[0]] not in ['J_PD','J_DATA']]);padidx=np.array([k for k,r in enumerate(rect) if r[4]=='copper'])
def fun(v):
 xy=start.copy();xy[free]=v.reshape(-1,2);ct=xy[ri]+off
 gap=hs-np.abs(ct[a]-ct[b]);pen=np.maximum(np.minimum(gap[:,0],gap[:,1]),0)
 ed=np.maximum(np.abs(ct[edgeidx])+half[edgeidx]-13.8,0)
 ep=np.maximum(np.abs(ct[padidx])+half[padidx]-13.74,0)
 dd=np.maximum(np.abs(ct[:,None,:]-bolts)-half[:,None,:],0);bp=np.maximum(2.4-np.linalg.norm(dd,axis=2),0)
 local=np.maximum(np.linalg.norm(xy[li]-xy[lj],axis=1)-ld,0)
 return 150*(pen@pen+np.sum(ed**2)+np.sum(ep**2)+np.sum(bp**2))+np.sum(lw*local**2)+.002*np.sum((xy-start)**2)
best=None
for k in range(3):
 res=minimize(fun,start[free].ravel(),method='L-BFGS-B',options={'maxiter':500,'ftol':1e-9,'maxfun':200000}); print(k,res.fun,res.message,flush=True)
 if best is None or res.fun<best.fun:best=res
 start[free]=res.x.reshape(-1,2)
for i,n in enumerate(names):p['placements'][n]['pcbX']=round(float(start[i,0]),4);p['placements'][n]['pcbY']=round(float(start[i,1]),4)
p['scope']='New conservative geometry optimization study, not recovered historical placement. Unrouted and unapproved.'
json.dump(p,open('config/placement.json','w'),indent=2)
