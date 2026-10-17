#!/usr/bin/env python3
"""Make an exact native DRC allow-list for the explicitly selected Type VII process.

This selects a manufacturing feature, not a clearance/connectivity waiver.
Native and independent copper/drill checks still inspect every barrel.
"""
import argparse,hashlib,json
from pathlib import Path
from shapely.geometry import Point
from pcb_geometry import Copper,LAYERS
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);args=p.parse_args();path=args.input;records=json.loads(path.read_text());c=Copper(records);LAYERS=c.layers;elements=c.elements();rows=[]
requirements=json.loads((ROOT/'config/design-requirements.json').read_text());capabilities=json.loads((ROOT/'artifacts/requirements/jlcpcb-published-capabilities.json').read_text())
# The reviewed global process applies to every 0.30 mm via, not component holes.
assert 'Type VII' in json.dumps(requirements) and capabilities['published_via_diameter_difference_rule_met']
for via in (e for e in records if e['type']=='pcb_via'):
 assert via['outer_diameter']>=.45 and abs(via['hole_diameter']-.3)<1e-7 and set(via['layers'])==set(LAYERS),via['pcb_via_id']
 disk=Point(via['x'],via['y']).buffer(via['outer_diameter']/2,quad_segs=128);owners=[]
 for e,k,ss in elements:
  if e['type']!='pcb_smtpad':continue
  if any(disk.intersection(g).area>1e-8 for g in ss.values()):
   assert k==c.key(via),'Via overlaps foreign terminal: '+via['pcb_via_id']
   owners.append(e['pcb_smtpad_id'])
 if not owners:continue
 identifier=via['pcb_via_id']
 assert identifier.startswith('compact_terminal_') or identifier in ['compact_GND_U_MCU_EP','compact_GND_U_DRV_EP','compact_GND_U_FLASH_EP'],'Unexpected ordinary via in a terminal: '+identifier
 if identifier.startswith('compact_terminal_'):
  assert via['tented_on_top'] and via['tented_on_bottom'],'Preserve original pad mask apertures: '+identifier
 rows.append(dict(via_id=identifier,source_net_id=via['source_net_id'],pad_diameter_mm=via['outer_diameter'],drill_diameter_mm=via['hole_diameter'],owner_pad_ids=sorted(set(owners)),required_process='IPC-4761 Type VII epoxy-filled and copper-capped',factory_acceptance_received=False))
report=dict(scope='Explicit filled/capped land-via process selection; all clearance, drill, short and connection checks remain mandatory',circuit_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),required_process='IPC-4761 Type VII epoxy-filled and copper-capped on all 0.30 mm vias only',reviewed_vias=rows,ordinary_vias_in_pads_permitted=False,original_supplier_lands_mask_and_paste_preserved=True,factory_acceptance_received=False,manufacturing_release=False)
out=path.parent/'filled-capped-via-policy.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(reviewed_land_vias=len(rows),factory_acceptance_received=False,manufacturing_release=False)))
