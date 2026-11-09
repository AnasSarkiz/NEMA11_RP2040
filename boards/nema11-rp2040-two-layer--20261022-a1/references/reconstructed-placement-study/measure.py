exec(open('optimize-final.py').read().split('p2=json.load')[0])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
reports={}
for file in ['baseline.placement.json','placement-stable.json']:
 pp=json.load(open(file));xy=np.array([[pp['placements'][n]['pcbX'],pp['placements'][n]['pcbY']] for n in names]);ct=xy[ri]+off;gap=hs-np.abs(ct[a]-ct[b]);pen=np.maximum(np.minimum(gap[:,0],gap[:,1]),0);worst={}
 for k in np.argsort(pen)[::-1]:
  if pen[k]<.01:break
  pair=' / '.join(sorted([names[ri[a[k]]],names[ri[b[k]]]]));worst[pair]=max(worst.get(pair,0),round(float(pen[k]),4))
 boltsbad={}
 for k,r in enumerate(rect):
  dis=np.linalg.norm(np.maximum(np.abs(ct[k]-bolts)-half[k],0),axis=1)-2.35
  if dis.min()<0:boltsbad[names[r[0]]]=min(boltsbad.get(names[r[0]],0),round(float(dis.min()),4))
 reports[file]={'conservative_box_conflicting_pairs':len(worst),'pairs_overlap_mm':worst,'bolt_head_rectangle_conflicts_mm':boltsbad}
 # Render both measured inputs
 fig,axs=plt.subplots(1,2,figsize=(14,7))
 for ax,side in zip(axs,['top','bottom']):
  ax.add_patch(Rectangle((-14,-14),28,28,fill=False,lw=2));ax.set(xlim=(-15,15),ylim=(-15,15),aspect='equal',title=side+' (viewed from top)')
  for bolt in bolts:ax.add_patch(Circle(bolt,2.35,fill=False,color='red',ls='--'));ax.add_patch(Circle(bolt,1.35,color='gray',alpha=.3))
  for k,r in enumerate(rect):
   if side not in r[3]:continue
   ax.add_patch(Rectangle(ct[k]-half[k],*half[k]*2,fill=r[4]=='copper',edgecolor='orange' if r[4]=='copper' else 'blue',facecolor='orange' if r[4]=='copper' else 'none',alpha=.4,lw=.6))
  for i,n in enumerate(names):
   if pp['placements'][n]['layer']==side:ax.text(*xy[i],n,fontsize=5,ha='center')
 fig.suptitle('UNVERIFIED placement study: translated fresh-baseline native geometry, not a new native PCB build')
 fig.tight_layout();fig.savefig('baseline-local-geometry.png' if file=='baseline.placement.json' else 'candidate-local-geometry.png',dpi=160)
json.dump(reports,open('local-geometry-measurements.json','w'),indent=2)
print(json.dumps(reports,indent=2))
