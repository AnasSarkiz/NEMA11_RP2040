#!/usr/bin/env python3
"""Readable board legends; supplier copper/models remain unchanged."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
labels = [('top', 'PD 15V', -10, 20.2, 1),
          ('top', '1', 16.95, 18.55, .9),
          ('bottom', '1', 14.5, 20.5, .9), ('bottom', '2', 12.5, 20.5, .9),
          ('bottom', '3', 10.5, 20.5, .9), ('bottom', '4', 8.5, 20.5, .9),
          ('bottom', 'NEMA11 RP2040', 0, 10, 1.2),
          ('bottom', 'DEVELOPMENT V0.3', 0, 8.2, .9),
          ('bottom', '1 A+ BLACK   2 A- GREEN', 0, 13.5, 1.0),
          ('bottom', '3 B+ RED     4 B- BLUE', 0, 12, 1.0),
          ('bottom', 'USB DATA', -4.6, -12.4, 1.0),
          ('bottom', 'PD 15V', .6, 17.7, 1.0)]


def annotate(records):
    records[:] = [e for e in records if not e['type'].startswith('pcb_silkscreen_')]
    source = {e['name']:e['source_component_id'] for e in records if e['type']=='source_component'}
    owners = {name:next(e['pcb_component_id'] for e in records if e['type']=='pcb_component'
                       and e['source_component_id']==source[name]) for name in ['J_PD','J_DATA','J_MOTOR','U_MCU']}
    font=json.loads((ROOT/'config/controller-silkscreen-font.json').read_text())
    stroke=.15
    for i, (layer, text, x, y, size) in enumerate(labels):
        # Native vector paths decouple readable character height from the
        # exporter's fixed text stroke ratio (0.09, too thin for these legends).
        # All coordinates are physical board coordinates; bottom text is mirrored.
        owner = 'J_PD' if 'PD 15V' in text else 'J_DATA' if 'USB DATA' in text else 'J_MOTOR' if text in ['1','2','3','4'] or 'A+' in text or 'B+' in text else 'U_MCU'
        cursor=0.;segments=[]
        for char in text:
            for q in font['lineAlphabet'].get(char,[]):
                segments.append([(cursor+q['x1'],q['y1']),(cursor+q['x2'],q['y2'])])
            cursor += font['glyphAdvanceRatio'].get(char,.692052)
        xs=[q[0] for segment in segments for q in segment]
        ys=[q[1] for segment in segments for q in segment]
        scale=(size-stroke)/(max(ys)-min(ys))
        cx=(max(xs)+min(xs))/2;cy=(max(ys)+min(ys))/2
        for k,segment in enumerate(segments):
            route=[{'x':round(x+(px-cx)*scale*(-1 if layer=='bottom' else 1),6),
                    'y':round(y+(py-cy)*scale,6)} for px,py in segment]
            records.append({'type':'pcb_silkscreen_path','pcb_silkscreen_path_id':f'controller_legend_{i}_{k}',
                            'route':route,'stroke_width':stroke,'layer':layer,
                            'pcb_component_id':owners[owner],'subcircuit_id':'subcircuit_source_group_0'})


if __name__ == '__main__':
    path = ROOT / 'artifacts/controller-pcb/board.circuit.json'
    records = json.loads(path.read_text())
    annotate(records)
    path.write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({'functional_board_legends':len(labels), 'supplier_copper_modified':False}))
