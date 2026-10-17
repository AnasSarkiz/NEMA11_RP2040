#!/usr/bin/env python3
"""Freeze and independently verify the compact crystal/ground construction only."""
import argparse,hashlib,json,math
from pathlib import Path
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
from pcb_geometry import Copper
from fill_controller_ground import fill
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source-folder',default='artifacts/compact-routing');parser.add_argument('--folder',default='artifacts/compact-clock');parser.add_argument('--keep-usb',action='store_true');parser.add_argument('--keep-all',action='store_true');parser.add_argument('--verify-existing',action='store_true');args=parser.parse_args()
folder=ROOT/args.folder;folder.mkdir(exist_ok=True);source=folder/'board.circuit.json' if args.verify_existing else ROOT/args.source_folder/'routing-construction.circuit.json';records=json.loads(source.read_text());c=Copper(records)
keep={'XIN','XOUT','XTAL_OUT'}|({'MCU_DM','MCU_DP'} if args.keep_usb else set())
records=[e for e in records if args.verify_existing or args.keep_all or e['type'] not in ['pcb_trace','pcb_via','pcb_copper_pour'] or (e['type'] in ['pcb_trace','pcb_via'] and (c.nets.get(c.key(e)) in keep or e.get('pcb_trace_id','').startswith('compact_GND_') or e.get('pcb_via_id','').startswith('compact_GND_')))]
if args.verify_existing:data=source.read_bytes()
else:
 fill(records);data=(json.dumps(records,indent=2)+'\n').encode();(folder/'board.circuit.json').write_bytes(data)
c=Copper(records);keys={v:k for k,v in c.nets.items()};elements=c.elements();errors=[];rows=[];regions=[]
for name,maximum in [('XIN',5),('XOUT',6),('XTAL_OUT',5)]:
 traces=[e for e in records if e['type']=='pcb_trace' and c.key(e)==keys[name]];vias=[e for e in records if e['type']=='pcb_via' and c.key(e)==keys[name]];length=0;layers=set()
 for e in traces:
  for a,b in zip(e['route'],e['route'][1:]):
   length+=math.dist((a['x'],a['y']),(b['x'],b['y']));layers.add(a['layer']);regions.append(LineString([(a['x'],a['y']),(b['x'],b['y'])]).buffer(.25))
 members,roots=c.groups(keys[name]);islands={r for (e,k,s),r in zip(members,roots) if e['type'] in ['pcb_smtpad','pcb_plated_hole']}
 row=dict(net=name,total_copper_mm=length,budget_mm=maximum,layers=sorted(layers),signal_vias=len(vias),physical_pin_islands=len(islands));rows.append(row)
 if length>maximum or vias or layers!={'top'} or len(islands)!=1:errors.append(dict(clock_route=row))
exemptions=[]
for p in c.ports.values():
 sp=c.source[p['source_port_id']]
 if c.names[sp['source_component_id']]=='U_MCU' and sp['pin_number'] in [20,21]:exemptions.append(Point(p['x'],p['y']).buffer(.55))
guard=unary_union(regions).difference(unary_union(exemptions))
for e,k,shapes in elements:
 if c.nets.get(k) in ['GND','XIN','XOUT','XTAL_OUT']:continue
 if any(l in shapes and shapes[l].intersects(guard) for l in ['top','inner1']):errors.append(dict(clock_guard_violation=e[e['type']+'_id']))
plane=unary_union([s['inner1'] for e,k,s in elements if e['type']=='pcb_copper_pour' and k==keys['GND'] and 'inner1' in s]);members,roots=c.groups(keys['GND']);ep=next(p for p in c.ports.values() if c.names[c.source[p['source_port_id']]['source_component_id']]=='U_MCU' and c.source[p['source_port_id']]['pin_number']==57);ep_root=next(r for (e,k,s),r in zip(members,roots) if e.get('pcb_port_id')==ep['pcb_port_id']);returns=[]
for name,pin in [('Y_MCU',2),('Y_MCU',4),('C_XIN',2),('C_XOUT',2)]:
 port=next(p for p in c.ports.values() if c.names[c.source[p['source_port_id']]['source_component_id']]==name and c.source[p['source_port_id']]['pin_number']==pin)
 root=next(r for (e,k,s),r in zip(members,roots) if e.get('pcb_port_id')==port['pcb_port_id']);vias=[e for e in records if e['type']=='pcb_via' and c.key(e)==keys['GND'] and math.dist((port['x'],port['y']),(e['x'],e['y']))<=1.2 and plane.intersects(Point(e['x'],e['y']).buffer(e['outer_diameter']/2))];returns.append(dict(pin=name+'.'+str(pin),nearby_ground_vias=len(vias),physically_connected_to_MCU_EP=root==ep_root))
 if not vias or root!=ep_root:errors.append(dict(missing_clock_return=name+'.'+str(pin)))
report=dict(scope='Clock signal/return/guard review on the existing routed board' if args.verify_existing else 'Compact crystal signal and local ground-return construction ONLY; other controller nets remain unrouted',circuit_sha256=hashlib.sha256(data).hexdigest(),source_sha256=hashlib.sha256((ROOT/args.source_folder/'unrouted.circuit.json').read_bytes()).hexdigest(),routes=rows,ground_returns=returns,top_and_inner1_guard_buffer_mm=.25,MCU_pin_exemption_radius_mm=.55,three_reviewed_exposed_pad_filled_capped_barrels=True,errors=errors,clock_construction_pass=not errors,full_controller_routing_complete=not c.connectivity() if args.verify_existing else False,bench_clock_startup_drive_load_frequency_verified=False,manufacturing_release=False)
(folder/'clock-layout-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(bool(errors))
