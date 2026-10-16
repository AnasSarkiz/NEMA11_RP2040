#!/usr/bin/env python3
"""Create functional native sheets from real source ports and supplier symbols."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def create(records, templates):
    source = {e['name']: e for e in records if e['type'] == 'source_component'}
    ports = {e['source_port_id']: e for e in records if e['type'] == 'source_port'}
    nets = {e['subcircuit_connectivity_map_key']: e for e in records if e['type'] == 'source_net'}
    template = {t['name']: t for t in templates}
    output = copy.deepcopy(records)
    sequence = 0
    sheet = ''
    group = None

    def uid(prefix):
        nonlocal sequence
        sequence += 1
        return f'core_{prefix}_{sequence}'

    def text(value, x, y, size=.25):
        output.append(dict(type='schematic_text', schematic_text_id=uid('text'),
                           schematic_sheet_id=sheet, text=value, position=dict(x=x, y=y),
                           rotation=0, font_size=size, anchor='left', color='#17465b'))

    def line(x1, y1, x2, y2, color='#99aabb'):
        output.append(dict(type='schematic_line', schematic_line_id=uid('line'),
                           schematic_sheet_id=sheet, x1=x1, y1=y1, x2=x2, y2=y2,
                           stroke_width=.015, color=color))

    def section(title, x1, y1, x2, y2):
        nonlocal group
        group = dict(type='schematic_group', schematic_group_id=uid('group'), name=title,
                     source_group_id=next(e['source_group_id'] for e in records if e['type'] == 'source_group'),
                     center=dict(x=(x1 + x2) / 2, y=(y1 + y2) / 2), width=x2 - x1, height=y2 - y1,
                     schematic_component_ids=[], show_as_schematic_box=False)
        output.append(group)
        text(title, x1 + .3, y2 - .45, .30)
        for a, b in [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)),
                     ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]:
            line(*a, *b)

    def page(index, name):
        nonlocal sheet, group
        sheet = f'core_sheet_{index}'
        group = None
        output.append(dict(type='schematic_sheet', schematic_sheet_id=sheet,
                           name=f'{index:02} {name}', display_name=name, sheet_index=index,
                           sheet_size='a4', sheet_width=297, sheet_height=210,
                           center=dict(x=16, y=11)))
        text('NEMA11 / RP2040 CORE', .8, 21.3, .42)
        text(name, 13, 21.3, .32)
        text('SUBSYSTEM REVIEW ONLY - external controller and final PCB incomplete', .8, .45, .23)
        text(f'{index}/3', 30, .45, .23)
        for a, b in [((.4, .2), (31.6, .2)), ((31.6, .2), (31.6, 21.8)),
                     ((31.6, 21.8), (.4, 21.8)), ((.4, 21.8), (.4, .2))]:
            line(*a, *b)

    def part(name, x, y, mcu=False):
        original = template[name]
        c = copy.deepcopy(original['component'])
        old_center = c['center']
        c.update(schematic_component_id=uid('component'), center=dict(x=x, y=y),
                 schematic_sheet_id=sheet, source_component_id=source[name]['source_component_id'])
        c.pop('schematic_group_id', None)
        if group:
            c['schematic_group_id'] = group['schematic_group_id']
            group['schematic_component_ids'].append(c['schematic_component_id'])
        physical = {p['pin_number']: p for p in ports.values()
                    if p['source_component_id'] == source[name]['source_component_id']}
        c['port_labels'] = {f'pin{pin}': p['name'] for pin, p in physical.items()}
        left = [p for p in range(2, 19) if p != 10] + [p for p in range(27, 42) if p != 33]
        right = [p for p in range(1, 58) if p not in left]
        custom_box = mcu or name == 'U_FLASH'
        width, height = (3.0, 16.4) if mcu else (2.3, 4.4)
        if name == 'U_FLASH':
            left, right = [1, 6, 5, 2, 3, 7], [8, 4, 9]
        if custom_box:
            c.update(size=dict(width=width, height=height), pin_spacing=.53,
                     port_arrangement={'left_side': {'pins': left, 'direction': 'top-to-bottom'},
                                       'right_side': {'pins': right, 'direction': 'top-to-bottom'}})
        output.append(c)
        if not c.get('symbol_name'):
            text(name, x - c['size']['width'] / 2, y + c['size']['height'] / 2 + .4, .30)
            text(source[name]['manufacturer_part_number'], x - c['size']['width'] / 2,
                 y - c['size']['height'] / 2 - .4, .24)
        for t in original['ports']:
            p = physical[t['pin_number']]
            q = copy.deepcopy(t['port'])
            direction = q['facing_direction']
            if custom_box:
                side = left if t['pin_number'] in left else right
                direction = 'left' if side is left else 'right'
                center = dict(x=x + (-1 if direction == 'left' else 1) * (width / 2 + .35),
                              y=y + ((len(side) - 1) / 2 - side.index(t['pin_number'])) * .53)
            else:
                center = dict(x=x + q['center']['x'] - old_center['x'],
                              y=y + q['center']['y'] - old_center['y'])
            q.update(schematic_port_id=uid('port'), schematic_component_id=c['schematic_component_id'],
                     source_port_id=p['source_port_id'], schematic_sheet_id=sheet, center=center,
                     facing_direction=direction, side_of_component={'up': 'top', 'down': 'bottom'}.get(direction, direction),
                     display_pin_label=p['name'], display_pin_label_font_size=.21,
                     is_connected=bool(p.get('subcircuit_connectivity_map_key')))
            output.append(q)
            key = p.get('subcircuit_connectivity_map_key')
            if not key:
                for dy in (-1, 1):
                    line(center['x'] - .07, center['y'] - dy * .07,
                         center['x'] + .07, center['y'] + dy * .07, '#334455')
                continue
            net = nets[key]
            dx, dy = {'left': (-1, 0), 'right': (1, 0), 'up': (0, 1), 'down': (0, -1)}[direction]
            length = 1.2 if mcu else .55
            end = dict(x=center['x'] + dx * length, y=center['y'] + dy * length)
            st = next(e for e in records if e['type'] == 'source_trace' and
                      p['source_port_id'] in e.get('connected_source_port_ids', []) and
                      e.get('subcircuit_connectivity_map_key') == key)
            output.append(dict(type='schematic_trace', schematic_trace_id=uid('trace'),
                               schematic_sheet_id=sheet, source_trace_id=st['source_trace_id'],
                               subcircuit_connectivity_map_key=key,
                               edges=[{'from': center, 'to': end, 'from_schematic_port_id': q['schematic_port_id']}],
                               junctions=[]))
            output.append(dict(type='schematic_net_label', schematic_net_label_id=uid('label'),
                               schematic_sheet_id=sheet, source_net_id=net['source_net_id'],
                               subcircuit_connectivity_map_key=key, text=net['name'], anchor_position=end,
                               center=end, anchor_side={'left': 'right', 'right': 'left'}.get(direction, 'left')))

    page(1, 'MCU / controller interfaces')
    part('U_MCU', 16, 10.9, mcu=True)
    text('Named nets continue to the controller; NC crosses are intentionally unused GPIO.', 1.2, 1.3, .23)
    page(2, 'Flash / clock / USB / debug')
    section('QSPI flash and ROM BOOT pads', 1, 10.1, 16, 20.3)
    for name, x, y in [('U_FLASH', 6.8, 15.7), ('R_FLASH_CS', 12.8, 17),
                       ('C_FLASH', 12.8, 13.5), ('R_BOOT', 5.2, 11.7),
                       ('TP_BOOT', 10.5, 11.7), ('TP_BOOT_GND', 14, 11.7)]:
        part(name, x, y)
    section('12 MHz oscillator', 1, 1.8, 16, 9.7)
    for name, x, y in [('Y_MCU', 6.5, 6.2), ('R_XOUT', 12, 6.2),
                       ('C_XIN', 4, 3.4), ('C_XOUT', 10, 3.4)]:
        part(name, x, y)
    section('SWD / RUN / bare test pads', 16.5, 10.1, 31, 20.3)
    for name, x, y in [('TP_SWCLK', 21.2, 17.6), ('TP_SWDIO', 27.7, 17.6),
                       ('TP_RUN', 21.2, 14.7), ('R_RUN', 27.7, 14.7),
                       ('TP_3V3', 21.2, 11.8), ('TP_GND', 27.7, 11.8)]:
        part(name, x, y)
    section('USB series termination - connector / ESD external', 16.5, 1.8, 31, 9.7)
    part('R_DM', 21.2, 6.4)
    part('R_DP', 27.7, 6.4)
    text('Two 15 pF loads assume about 2.5 pF stray for CL=10 pF.', 1.2, 1.1, .22)
    page(3, 'Supply rails / local decoupling')
    section('3.3 V IOVDD - one 100 nF capacitor per physical supply pin', 1, 11, 31, 20.3)
    for i, name in enumerate(['C_IO1', 'C_IO10', 'C_IO22', 'C_IO33', 'C_IO42', 'C_IO49']):
        part(name, 10.5 + 2.1 * i, 15.8)
    section('3.3 V USB / ADC / regulator input', 1, 2.5, 16, 10.4)
    for i, name in enumerate(['C_USB', 'C_ADC', 'C_VREG_IN']):
        part(name, 6.4 + 2.1 * i, 6.6)
    section('1.1 V core / regulator output', 16.5, 2.5, 31, 10.4)
    for i, name in enumerate(['C_DV23', 'C_DV50', 'C_VREG_OUT']):
        part(name, 21.65 + 2.1 * i, 6.6)
    text('VREG_OUT and DVDD are 1.1 V. Regulated 3.3 V comes from the surrounding controller.', 1.2, 1.4, .23)
    return output


if __name__ == '__main__':
    path = ROOT / 'artifacts/rp2040-core/core.circuit.json'
    data = json.loads(path.read_text())
    result = create(data, json.loads((ROOT / 'src/core-symbol-templates.json').read_text()))
    assert result[:len(data)] == data, 'Presentation changed electrical or PCB/CAD records'
    target = path.with_name('core-schematic.circuit.json')
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'schematic_sheets': 3, 'physical_ports': 119,
                      'base_circuit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'electrical_PCB_CAD_records_preserved': True}))
