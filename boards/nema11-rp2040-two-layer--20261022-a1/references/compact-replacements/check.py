#!/usr/bin/env python3
"""Read-only qualification checks. Writes no board/build/import data."""
import hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
result={}
for part in ('CH224Q','DMN2300UFB4_7B'):
    folder=ROOT/'imports'/part
    text=(folder/(part+'.tsx')).read_text()
    pads=[]
    for pin,x,y,w,h in re.findall(r'<smtpad portHints=\{\["(pin\d+)"\]\} pcbX="([\-\d.]+)mm" pcbY="([\-\d.]+)mm" width="([\d.]+)mm" height="([\d.]+)mm"',text):
        pads.append(dict(pin=pin,x=float(x),y=float(y),width=float(w),height=float(h)))
    vertices=[list(map(float,s.split()[1:4])) for s in (folder/(part+'.obj')).read_text().splitlines() if s.startswith('v ')]
    box=[[min(p[i] for p in vertices),max(p[i] for p in vertices)] for i in range(3)]
    courtyard=json.loads(re.search(r'<courtyardoutline outline=\{(\[.*?\])\}',text).group(1))
    cx=[min(p['x'] for p in courtyard),max(p['x'] for p in courtyard)]
    cy=[min(p['y'] for p in courtyard),max(p['y'] for p in courtyard)]
    assert all(cx[0] <= p['x']-p['width']/2 and p['x']+p['width']/2<=cx[1] and cy[0]<=p['y']-p['height']/2 and p['y']+p['height']/2<=cy[1] for p in pads)
    assert cx[0]<=box[0][0] and box[0][1]<=cx[1] and cy[0]<=box[1][0] and box[1][1]<=cy[1]
    result[part]={'pads_mm':pads,'courtyard_bounds_mm':[cx,cy],'raw_obj_bounds_mm':box,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file()}}
# 25 C screening assumptions, not hot/cold or measured waveform guarantees.
voh,rg,rpd,ig=2.62,1010,9900,10e-6
vgs=(voh-ig*rg)*rpd/(rg+rpd)
i=3.3/9
result['static_screen']={'VGS_V':vgs,'GPIO_current_A':(voh-vgs)/rg,'buzzer_DC_resistance_screen_A':i,'MOSFET_conduction_W_using_0.36_ohm':i*i*.36,'datasheet_thermal_screen_C_using_250_C_per_W':i*i*.36*250,'gate_leakage_A_to_reduce_VGS_to_1.8V':(voh-1.8)/rg-1.8/rpd,'hiZ_VGS_V_at_10uA_and_10k_plus_1pct':10e-6*10100}
assert 1.8<vgs<2.5
print(json.dumps(result,indent=2))
