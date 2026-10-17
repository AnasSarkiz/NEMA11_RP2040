#!/usr/bin/env python3
"""Apply the reference's 100 um stencil and 60% EP window policy natively."""
import math
from shapely.affinity import scale
from pcb_geometry import pad_shape


def prepare(records):
    source={e['source_component_id']:e for e in records if e['type']=='source_component'}
    components={e['pcb_component_id']:e for e in records if e['type']=='pcb_component'}
    records[:]=[e for e in records if e['type']!='pcb_solder_paste']
    paste=[]
    for pad in records:
        if pad['type']!='pcb_smtpad':continue
        component=components[pad['pcb_component_id']]
        name=source[component['source_component_id']]['name']
        if component.get('do_not_place') or name.startswith('TP_'):continue
        common={'type':'pcb_solder_paste','pcb_component_id':pad['pcb_component_id'],
                'pcb_smtpad_id':pad['pcb_smtpad_id'],'layer':pad['layer'],
                'subcircuit_id':pad['subcircuit_id']}
        if pad['shape']=='polygon':
            geometry=scale(pad_shape(pad),xfact=.7,yfact=.7,origin='centroid')
            assert geometry.geom_type=='Polygon' and not geometry.interiors
            paste.append({**common,'pcb_solder_paste_id':f'controller_paste_{len(paste)}','shape':'polygon',
                          'points':[{'x':x,'y':y} for x,y in geometry.exterior.coords]})
            continue
        assert pad['shape'] in ['rect','pill','rotated_pill'],(name,pad['shape'])
        w,h=pad['width'],pad['height']
        if name in ['U_MCU','U_DRV','U_PD'] and w>2 and h>2:
            aw,ah=w*math.sqrt(.6)/2,h*math.sqrt(.6)/2
            windows=[(pad['x']+dx*w/4,pad['y']+dy*h/4,aw,ah) for dx in [-1,1] for dy in [-1,1]]
        else:
            factor=.7
            while min(w,h)*factor/.1<1.5 or w*h*factor/(2*(w+h)*.1)<.70:
                factor=round(factor+.05,2)
            assert factor<=.95,(name,pad['pcb_smtpad_id'],'100 um stencil release screen')
            windows=[(pad['x'],pad['y'],w*factor,h*factor)]
        for x,y,aw,ah in windows:
            aperture={**common,'pcb_solder_paste_id':f'controller_paste_{len(paste)}',
                      'shape':pad['shape'],'x':x,'y':y,'width':aw,'height':ah,
                      'ccw_rotation':pad.get('ccw_rotation',0)}
            if pad['shape'] in ['pill','rotated_pill']:aperture['radius']=min(aw,ah)/2
            paste.append(aperture)
    records.extend(paste)
