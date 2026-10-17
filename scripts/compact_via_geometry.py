"""Exact fixed-site via construction checks; final independent audits still apply."""
import math
from shapely.geometry import Point,Polygon,LineString
from shapely.ops import unary_union
from pcb_geometry import pad_shape

def via_site_errors(records,copper,key,x,y,diameter=.45,allowed_pad_ids=()):
 errors=[];point=Point(x,y);metal=point.buffer(diameter/2+.0001,quad_segs=64);drill=point.buffer(.15+.0001,quad_segs=64)
 board=next(e for e in records if e['type']=='pcb_board');outline=Polygon([(p['x'],p['y']) for p in board['outline']])
 if not outline.covers(metal) or metal.distance(outline.boundary)<.25:errors.append('board edge')
 for e,k,shapes in copper.elements():
  for layer,shape in shapes.items():
   if k!=key and metal.distance(shape)<.15:errors.append('foreign copper '+e[e['type']+'_id'])
   if k==key and e['type'] in ['pcb_smtpad','pcb_plated_hole'] and e[e['type']+'_id'] not in allowed_pad_ids and point.distance(shape)<.30:errors.append('ordinary same-net pad web '+e[e['type']+'_id'])
 for e in records:
  if e['type']=='pcb_keepout':
   assert e['shape']=='circle'
   if metal.distance(Point(e['center']['x'],e['center']['y']).buffer(e['radius'],quad_segs=128))<.15:errors.append('mount keepout')
  if e['type'] in ['pcb_hole','pcb_plated_hole','pcb_via']:
   h={**e,'shape':'circle' if e['type']!='pcb_plated_hole' else e['shape'],'width':e.get('hole_width',e.get('hole_diameter')),'height':e.get('hole_height',e.get('hole_diameter'))}
   opening=pad_shape(h)
   if drill.distance(opening)<(.45 if e['type']=='pcb_plated_hole' else .20):errors.append('drill spacing '+e[e['type']+'_id'])
   if e['type']=='pcb_hole' and metal.distance(opening)<.20:errors.append('via copper to NPTH '+e[e['type']+'_id'])
   if e['type']=='pcb_plated_hole' and copper.key(e)!=key and metal.distance(opening)<.30:errors.append('via inner copper to foreign PTH '+e[e['type']+'_id'])
 if copper.nets[key] not in ['GND','XIN','XOUT','XTAL_OUT']:
  clock=[];exempt=[]
  for e,k,shapes in copper.elements():
   if e['type']=='pcb_trace' and copper.nets.get(k) in ['XIN','XOUT','XTAL_OUT']:
    clock.extend(LineString([(a['x'],a['y']),(b['x'],b['y'])]).buffer(.25) for a,b in zip(e['route'],e['route'][1:]))
  for p in copper.ports.values():
   sp=copper.source[p['source_port_id']]
   if copper.names[sp['source_component_id']]=='U_MCU' and sp['pin_number'] in [20,21]:exempt.append(Point(p['x'],p['y']).buffer(.55))
  if clock and metal.intersects(unary_union(clock).difference(unary_union(exempt))):errors.append('crystal guard')
 return sorted(set(errors))

def top_stub_errors(records,copper,key,points,width=.16):
 """Continuous physical checks for a prescribed top-side construction path."""
 errors=[];wire=LineString(points).buffer(width/2+.0001,cap_style=1,join_style=1,quad_segs=64)
 board=next(e for e in records if e['type']=='pcb_board');outline=Polygon([(v['x'],v['y']) for v in board['outline']])
 if not outline.covers(wire) or wire.distance(outline.boundary)<.25:errors.append('board edge')
 for e,k,shapes in copper.elements():
  if k!=key and 'top' in shapes and wire.distance(shapes['top'])<.15:errors.append('foreign top copper '+e[e['type']+'_id'])
 for e in records:
  if e['type']=='pcb_keepout' and wire.intersects(Point(e['center']['x'],e['center']['y']).buffer(e['radius'],quad_segs=128)):errors.append('mount exclusion')
  if e['type']=='pcb_hole' and wire.distance(Point(e['x'],e['y']).buffer(e['hole_diameter']/2,quad_segs=64))<.20:errors.append('NPTH clearance')
 if copper.nets[key] not in ['GND','XIN','XOUT','XTAL_OUT']:
  clock=[];exempt=[]
  for e,k,shapes in copper.elements():
   if e['type']=='pcb_trace' and copper.nets.get(k) in ['XIN','XOUT','XTAL_OUT']:
    clock.extend(LineString([(a['x'],a['y']),(b['x'],b['y'])]).buffer(.25) for a,b in zip(e['route'],e['route'][1:]))
  for p in copper.ports.values():
   sp=copper.source[p['source_port_id']]
   if copper.names[sp['source_component_id']]=='U_MCU' and sp['pin_number'] in [20,21]:exempt.append(Point(p['x'],p['y']).buffer(.55))
  if clock and wire.intersects(unary_union(clock).difference(unary_union(exempt))):errors.append('crystal guard')
 return sorted(set(errors))
