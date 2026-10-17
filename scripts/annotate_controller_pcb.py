#!/usr/bin/env python3
"""Readable board legends; supplier copper/models remain unchanged."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
labels = [('top', 'PD 15V', -10, 20.2, 1),
          ('top', '1A+', 14.5, 21.8, .8), ('top', '2A-', 12.5, 21.8, .8),
          ('top', '3B+', 10.5, 21.8, .8), ('top', '4B-', 8.5, 21.8, .8),
          ('bottom', 'NEMA11 RP2040', 0, 10, 1.2),
          ('bottom', 'DEVELOPMENT v0.3', 0, 8.2, .9),
          ('bottom', '1 A+ BLACK   2 A- GREEN', 0, 5.5, .9),
          ('bottom', '3 B+ RED     4 B- BLUE', 0, 4, .9),
          ('bottom', 'USB DATA', -4.6, -12.4, .9),
          ('bottom', 'PD 15V', .6, 17.7, .9)]


def annotate(records):
    records[:] = [e for e in records if not e['type'].startswith('pcb_silkscreen_')]
    source = {e['name']:e['source_component_id'] for e in records if e['type']=='source_component'}
    owners = {name:next(e['pcb_component_id'] for e in records if e['type']=='pcb_component'
                       and e['source_component_id']==source[name]) for name in ['J_PD','J_DATA','J_MOTOR','U_MCU']}
    for i, (layer, text, x, y, size) in enumerate(labels):
        # This circuit-json schema requires component ownership even for board
        # legends. Use the associated real connector or MCU, retaining absolute
        # board coordinates and introducing no artificial electrical component.
        owner = 'J_PD' if 'PD 15V' in text else 'J_DATA' if 'USB DATA' in text else 'J_MOTOR' if i in [1,2,3,4,7,8] else 'U_MCU'
        records.append({'type':'pcb_silkscreen_text', 'pcb_silkscreen_text_id':f'controller_legend_{i}',
                        'anchor_alignment':'center', 'anchor_position':{'x':x,'y':y},
                        'font':'tscircuit2024', 'font_size':size, 'layer':layer, 'text':text,
                        'ccw_rotation':0, 'pcb_component_id':owners[owner], 'subcircuit_id':'subcircuit_source_group_0'})


if __name__ == '__main__':
    path = ROOT / 'artifacts/controller-pcb/board.circuit.json'
    records = json.loads(path.read_text())
    annotate(records)
    path.write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps({'functional_board_legends':len(labels), 'supplier_copper_modified':False}))
