#!/usr/bin/env python3
"""Physical-pin contract for the MCU subsystem, not a full-board ERC or DRC."""
import hashlib
import json
from pathlib import Path
import sys


MCU_NETS = {
    1: 'V3V3', 4: 'LED_G', 5: 'LED_B', 8: 'STEP', 9: 'DIR', 10: 'V3V3',
    11: 'ENABLE_N', 12: 'SLEEP', 13: 'PD_GOOD', 19: 'GND', 20: 'XIN', 21: 'XOUT',
    22: 'V3V3', 23: 'V1V1', 24: 'SWCLK', 25: 'SWDIO', 26: 'RUN', 27: 'BUZZER_PWM',
    33: 'V3V3', 37: 'LED_R', 38: 'TEMP_SDA', 39: 'TEMP_SCL', 40: 'VM_SENSE',
    41: 'DATA_PRESENT', 42: 'V3V3', 43: 'V3V3', 44: 'V3V3', 45: 'V1V1',
    46: 'MCU_DM', 47: 'MCU_DP', 48: 'V3V3', 49: 'V3V3', 50: 'V1V1',
    51: 'QSPI_SD3', 52: 'QSPI_SCLK', 53: 'QSPI_SD0', 54: 'QSPI_SD2',
    55: 'QSPI_SD1', 56: 'QSPI_SS', 57: 'GND',
}
FLASH_NETS = {1: 'QSPI_SS', 2: 'QSPI_SD1', 3: 'QSPI_SD2', 4: 'GND',
              5: 'QSPI_SD0', 6: 'QSPI_SCLK', 7: 'QSPI_SD3', 8: 'V3V3', 9: 'GND'}


def validate(records):
    errors = []
    components = {e['name']: e for e in records if e['type'] == 'source_component'}
    nets = {e['subcircuit_connectivity_map_key']: e['name'] for e in records if e['type'] == 'source_net'}
    ports = {(e['source_component_id'], e['pin_number']): e for e in records if e['type'] == 'source_port'}

    def require(ok, message):
        if not ok:
            errors.append(message)

    def pin(ref, number):
        component = components.get(ref)
        port = ports.get((component['source_component_id'], number)) if component else None
        return nets.get(port.get('subcircuit_connectivity_map_key')) if port else None

    def mapping(ref, expected):
        require(ref in components, 'Missing ' + ref)
        for number, net in expected.items():
            require(pin(ref, number) == net, f'{ref} physical pin {number}: expected {net}, got {pin(ref, number)}')

    mapping('U_MCU', {p: MCU_NETS.get(p) for p in range(1, 58)})
    mapping('U_FLASH', FLASH_NETS)
    mapping('Y_MCU', {1: 'XIN', 2: 'GND', 3: 'XTAL_OUT', 4: 'GND'})
    for ref, (a, b, value) in {
        'R_FLASH_CS': ('V3V3', 'QSPI_SS', 10000), 'R_BOOT': ('QSPI_SS', 'BOOT_PAD', 1000),
        'R_XOUT': ('XOUT', 'XTAL_OUT', 1000), 'R_RUN': ('V3V3', 'RUN', 10000),
        'R_DM': ('MCU_DM', 'USB_DM', 27), 'R_DP': ('MCU_DP', 'USB_DP', 27),
    }.items():
        mapping(ref, {1: a, 2: b})
        require(components.get(ref, {}).get('resistance') == value, ref + ' incorrect resistance')
    capacitors = {n: ('V3V3', 1e-7) for n in (
        'C_IO1', 'C_IO10', 'C_IO22', 'C_IO33', 'C_IO42', 'C_IO49', 'C_USB', 'C_ADC', 'C_FLASH')}
    capacitors.update({n: ('V1V1', 1e-7) for n in ('C_DV23', 'C_DV50')})
    capacitors.update(C_VREG_IN=('V3V3', 1e-6), C_VREG_OUT=('V1V1', 1e-6),
                      C_XIN=('XIN', 15e-12), C_XOUT=('XTAL_OUT', 15e-12))
    for ref, (rail, value) in capacitors.items():
        mapping(ref, {1: rail, 2: 'GND'})
        actual = components.get(ref, {}).get('capacitance')
        require(actual is not None and abs(actual - value) <= value * 1e-9, ref + ' incorrect capacitance')
    for ref, net in dict(TP_3V3='V3V3', TP_GND='GND', TP_SWCLK='SWCLK',
                         TP_SWDIO='SWDIO', TP_RUN='RUN', TP_BOOT='BOOT_PAD', TP_BOOT_GND='GND').items():
        mapping(ref, {1: net})
    for ref, mpn, code in [('U_MCU', 'RP2040', 'C2040'),
                            ('U_FLASH', 'GD25Q16EEIGR', 'C2986331'),
                            ('Y_MCU', 'ABM8-272-T3', 'C20625731')]:
        c = components.get(ref, {})
        require(c.get('manufacturer_part_number') == mpn, ref + ' incorrect MPN')
        require(c.get('supplier_part_numbers', {}).get('jlcpcb') == [code], ref + ' incorrect supplier ID')
    require(len(components) == 31, 'Expected exactly 31 core components')
    by_id = {c['source_component_id']: c for c in components.values()}
    pcb = {e['pcb_component_id']: by_id.get(e['source_component_id'])
           for e in records if e['type'] == 'pcb_component'}
    for e in records:
        if e['type'] == 'pcb_solder_paste':
            owner = pcb.get(e.get('pcb_component_id'))
            require(not(owner and owner['name'].startswith('TP_')), 'Bare debug pad has stencil paste')
    board = next((e for e in records if e['type'] == 'pcb_board'), {})
    require(board.get('min_via_hole_diameter', 0) >= .30, 'Via drill requirement was reduced')
    require(board.get('min_via_pad_diameter', 0) >= .45, 'Via pad requirement was reduced')
    require(board.get('min_trace_to_pad_edge_clearance', 0) >= .15, 'Trace-to-pad clearance requirement was reduced')
    require(board.get('min_pad_edge_to_pad_edge_clearance', 0) >= .15, 'Pad-to-pad clearance requirement was reduced')
    for e in records:
        if e['type'].endswith('_error'):
            errors.append(str(e))
    return errors


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    path = root / 'artifacts/rp2040-core/core.circuit.json'
    errors = validate(json.loads(path.read_text()))
    receipt = {'scope': 'physical-pin subsystem contract; full-board ERC/DRC not run',
               'circuit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'passed': not errors, 'errors': errors,
               'native_ports_checked': 119, 'manufacturing_release': False}
    (path.parent / 'physical-pin-verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    sys.exit(bool(errors))
