#!/usr/bin/env python3
"""Optional bounded search of rejected poses. Requires numpy and scipy.

This search never edits active board files. Run audit.py on recorded candidates
for the standard-library-only reproducible rejection evidence. Search order and
floating-point results can depend on numpy/scipy/platform versions.
"""
import json
import math
import argparse
import sys
import numpy as np
from pathlib import Path
from audit import transform, geometry, HERE
fixture = json.loads((HERE/'baseline-geometry.json').read_text())
j = fixture['geometry']
p = fixture['placement']['placements']
s = {e['source_component_id']:e['name'] for e in j if e['type']=='source_component'}
c = {e['pcb_component_id']:e for e in j if e['type']=='pcb_component'}
geometry_bounds = geometry.geometry_bounds
audit = geometry.audit
def transformed(candidate):
    return transform(j,p,candidate)
from scipy.optimize import minimize
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path)
parser.add_argument("--mcu-right", action="store_true")
args=parser.parse_args()
# All bottom circuitry can move coherently, but preserve data/ESD, power conversion and encoder anchors.
fixednames={'J_PD','J_DATA','J_MOTOR','C_BULK','U_DRV','U_ESD','C_ESD','U_ENCODER','D_DATA','R_CC1','R_CC2'}
new={'J_PD':dict(p['J_PD'],pcbX=-8.65,pcbY=3.8,pcbRotation=270),'BZ1':dict(p['BZ1'],pcbX=0,pcbY=9)}
base=transformed(new);poses=dict(p,**new);names=[n for n in p if n not in fixednames];idx={n:i for i,n in enumerate(names)}
geo=[]
for e in base:
 if e['type'] not in ['pcb_smtpad','pcb_plated_hole','pcb_courtyard_outline']:continue
 n=s[c[e['pcb_component_id']]['source_component_id']];lo,hi=map(np.array,geometry_bounds(e));layer=e.get('layers',[e.get('layer')]);geo.append((n,(lo+hi)/2,(hi-lo)/2,layer,e['type']=='pcb_courtyard_outline'))
cent=np.array([g[1] for g in geo]);w=np.array([g[2] for g in geo]);owner=np.array([idx.get(g[0],len(names)) for g in geo]);i,k=np.triu_indices(len(geo),1)
mask=np.array([geo[a][0]!=geo[b][0] and bool(set(geo[a][3])&set(geo[b][3])) and geo[a][4]==geo[b][4] for a,b in zip(i,k)])
i,k=i[mask],k[mask];clear=np.array([.08 if geo[a][4] else .17 for a in i]);# conservative nominal margin
# Don't constrain intentional connector courtyard overhang at the mating edge.
edgeidx=np.array([z for z,g in enumerate(geo) if g[0] not in {'J_PD','J_DATA'} or not g[4]])
axes=np.array([[-11.5,-11.5],[-11.5,11.5],[11.5,-11.5],[11.5,11.5]])
mcunames=['U_MCU','C_IO1','C_IO10','C_IO22','C_IO33','C_IO42','C_IO49','C_DV23','C_DV50','C_USB','C_ADC','C_VREG_IN','C_VREG_OUT','Y_MCU','R_XOUT','C_XIN','C_XOUT','R_DM','R_DP']
clusters=[mcunames,['U_PD','R_PD','C_PD','R_PG','R_PD_CFG']]
links=[(idx[a[0]],idx[n]) for a in clusters for n in a[1:]]

def fun(x):
 delta=np.vstack([x.reshape(-1,2),[0,0]]);pos=cent+delta[owner];gradient=np.zeros_like(pos)
 diff=pos[i]-pos[k];sep=np.abs(diff)-w[i]-w[k];axis=np.argmax(sep,axis=1);v=np.maximum(clear-sep[np.arange(len(i)),axis],0)
 penalty=np.sum(v*v);sgn=np.sign(diff[np.arange(len(i)),axis]);g=-2*v*sgn
 np.add.at(gradient,(i,axis),g);np.add.at(gradient,(k,axis),-g)
 ed=np.maximum(np.abs(pos[edgeidx])+w[edgeidx]-13.9,0);penalty+=np.sum(ed*ed);gradient[edgeidx]+=2*ed*np.sign(pos[edgeidx])
 d=pos[:,None,:]-axes;out=np.maximum(np.abs(d)-w[:,None,:],0);dist=np.linalg.norm(out,axis=2);v=np.maximum(2.45-dist,0);penalty+=np.sum(v*v)
 gradient+=np.sum((-2*v/np.maximum(dist,1e-10))[:,:,None]*out*np.sign(d),axis=1)
 agg=np.zeros_like(delta);np.add.at(agg,owner,gradient);f=penalty*10000+np.sum(x*x)*.01;gr=agg[:-1]*10000+delta[:-1]*.02
 for a,b in links:
  d=delta[a]-delta[b];f+=np.sum(d*d)*.3;gr[a]+=d*.6;gr[b]-=d*.6
 return f,gr.ravel()
x=np.zeros((len(names),2))
for n in mcunames:x[idx[n]]=[1.2 if args.mcu_right else .4,-.3]
for seed in range(3 if args.mcu_right else 8):
 xx=x.copy() if seed==0 else bestx.reshape(-1,2)+np.random.default_rng(seed).normal(0,.4,x.shape)
 bounds=[(None,None)]*len(xx.ravel())
 if args.mcu_right:bounds[2*idx['U_MCU']]=(.8,2.5)
 res=minimize(fun,xx.ravel(),bounds=bounds,jac=True,method='L-BFGS-B',options={'maxiter':4000,'ftol':1e-12,'gtol':1e-6})
 if seed==0 or res.fun<best:best=res.fun;bestx=res.x;print(seed,best,flush=True)
 candidate=dict(new)
 for n,d in zip(names,bestx.reshape(-1,2)):
  if max(abs(d))>1e-6:candidate[n]=dict(poses[n],pcbX=round(poses[n]['pcbX']+d[0],6),pcbY=round(poses[n]['pcbY']+d[1],6))
 args.output.write_text(json.dumps(candidate,indent=2)+'\n') if args.output else None
 pl={'placements':dict(p,**candidate)};rpt=audit(transformed(candidate),pl,pl)
 print('pairs',len(rpt['conservative_pad_pairs_below_015mm']),'bolt',rpt['minimum_conservative_bolt_head_envelope_gap_mm'],flush=True)
 if not rpt['conservative_pad_pairs_below_015mm'] and rpt['minimum_conservative_bolt_head_envelope_gap_mm']>=.074:break
