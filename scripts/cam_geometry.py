#!/usr/bin/env python3
"""Independent CAM parser helpers adapted from the inspected NEMA14 reference.

Read-only source: AnasSarkiz/NEMA14_RP2040@596a8b8a5187dfd60924de4b8ac0c93e13d99680,
scripts/audit-manufacturing.py. Original CAM bytes are never modified. Explicit
right-angle LR aperture and unambiguous G85 parser compatibility is retained.
"""
import math, re, warnings
from collections import Counter
from shapely.geometry import Point, LineString, Polygon, box
from shapely.affinity import rotate
from shapely.ops import unary_union
from gerbonara import GerberFile, ExcellonFile
from gerbonara.graphic_objects import Flash
from gerbonara.utils import MM

def primitive(p):
 n=type(p).__name__
 if n=='Circle':return Point(p.x,p.y).buffer(p.r,quad_segs=64)
 if n=='Rectangle':return rotate(box(p.x-p.w/2,p.y-p.h/2,p.x+p.w/2,p.y+p.h/2),math.degrees(p.rotation),origin=(p.x,p.y))
 if n=='Line':return LineString([(p.x1,p.y1),(p.x2,p.y2)]).buffer(p.width/2,quad_segs=64)
 if n=='ArcPoly':
  if any(x is not None for x in p.arc_centers):raise ValueError('ArcPoly arc unsupported: explicit failure rather than silent polygon approximation')
  return Polygon(p.outline).buffer(0)
 if n=='Arc':
  r=math.hypot(p.x1-p.cx,p.y1-p.cy);a=math.atan2(p.y1-p.cy,p.x1-p.cx);b=math.atan2(p.y2-p.cy,p.x2-p.cx)
  sweep=((a-b)%(2*math.pi))*(-1) if p.clockwise else (b-a)%(2*math.pi)
  if abs(sweep)<1e-12:sweep=(-1 if p.clockwise else 1)*2*math.pi
  steps=max(8,math.ceil(abs(sweep)*max(r,1)/.001));pts=[(p.cx+r*math.cos(a+sweep*i/steps),p.cy+r*math.sin(a+sweep*i/steps)) for i in range(steps+1)]
  return LineString(pts).buffer(p.width/2,quad_segs=64)
 raise ValueError(f'Unsupported primitive {n}')
def gerber(path):
 raw=path.read_text();rot=0.;angles=[]
 for token in re.findall(r'%[^%]*%|[^*%]+\*',raw):
  m=re.search(r'%LR([+-]?[\d.]+)\*%',token)
  if m:rot=float(m[1]);continue
  if re.search(r'D0?3\*$',token.strip()):angles.append(rot)
 with warnings.catch_warnings(record=True) as ws:
  warnings.simplefilter('always');g=GerberFile.open(path)
 unknown=[str(w.message) for w in ws if not re.search(r'Unknown statement found: \"LR[+\-\d.]+\"',str(w.message))]
 if unknown:raise ValueError(f'{path.name} parser warnings: {unknown}')
 flashes=[o for o in g.objects if isinstance(o,Flash)]
 if len(flashes)!=len(angles):raise ValueError(f'Flash correspondence failure {path.name}: {len(flashes)} / {len(angles)}')
 for o,a in zip(flashes,angles):
  if a%360 not in (0,90,180,270):raise ValueError(f'Rotation {a} requires independently validated analytic support')
  if a%360:o.aperture=o.aperture.rotated(math.radians(a))
 result=Polygon();batch=[];last=True
 for o in g.objects:
  for p in o.to_primitives(unit=MM):
   dark=p.polarity_dark
   if dark!=last and batch:
    u=unary_union(batch);result=result.union(u) if last else result.difference(u);batch=[]
   batch.append(primitive(p));last=dark
 if batch:
  u=unary_union(batch);result=result.union(u) if last else result.difference(u)
 return result,len(g.objects),{'LR_applied':sum(bool(a%360) for a in angles),'warnings':unknown}
def drill(path):
 raw=path.read_text();lines=raw.splitlines();out=[];joined=0
 for l in lines:
  if l.startswith('G85'):
   if not out or not re.fullmatch(r'X[-+\d.]+Y[-+\d.]+',out[-1]):raise ValueError('Ambiguous G85 start')
   start=out.pop();out.extend(['G00'+start,'M15','G01'+l[3:],'M16','G05']);joined+=1;continue
  out.append(l)
 with warnings.catch_warnings(record=True) as ws:
  warnings.simplefilter('always');d=ExcellonFile.from_string('\n'.join(out)+'\n')
 unhandled=[str(w.message) for w in ws if 'G90 header statement found after end of header' not in str(w.message)]
 if unhandled:raise ValueError(f'{path.name} drill warnings: {unhandled}')
 gs=[primitive(p) for o in d.objects for p in o.to_primitives(unit=MM)]
 return unary_union(gs),gs,{'objects':len(d.objects),'G85_joined':joined,'parser_notices':[str(w.message) for w in ws],'tools_mm':dict(Counter(round(o.tool.diameter,6) for o in d.objects))}
