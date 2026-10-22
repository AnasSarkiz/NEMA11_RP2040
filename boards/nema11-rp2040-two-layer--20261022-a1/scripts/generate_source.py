#!/usr/bin/env python3
"""Generate native board wiring; imported component definitions are never edited."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert Path.cwd() == ROOT
plan = json.loads((ROOT/'config/component-plan.json').read_text())
manifest = json.loads((ROOT/'checks/import-manifest.json').read_text())['imports']
parts = {e['part']: e for e in manifest}
assert set(plan['components'].values()) <= set(parts), 'Complete supported imports before source construction'
for part in parts.values():
    for entry in part['files']:
        assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest() == entry['sha256'], 'Imported component changed'
connections = json.loads((ROOT/'config/connections.json').read_text())['components']
layout = json.loads((ROOT/'config/schematic-layout.json').read_text())
lines = ['// WIP source construction. Native PCB routing is intentionally disabled.',
         '// Supplier definitions are fresh JLCPCB imports; no footprint/symbol/pin/CAD overrides.',
         'import poses from "./config/placement.json"',
         'import requirements from "./config/requirements.json"']
for key, part in sorted(parts.items()):
    source = next(e['path'] for e in part['files'] if e['path'].endswith('.tsx'))[:-4]
    lines.append(f'import {{ {part["exported_symbol"]} }} from "./{source}"')
lines += ['','const position = (name: keyof typeof poses.placements) => ({',
          '  ...poses.placements[name], layer: poses.placements[name].layer as "top" | "bottom",','})',
          '', 'export default function Nema11TwoLayerBuzzer() {',
          '  return (', '    <board width={28} height={28} thickness={1.6} layers={2}',
          '      routingDisabled={true} schAutoLayoutEnabled={false}',
          '      minTraceWidth={0.16} minTraceToPadEdgeClearance={0.15}',
          '      minPadEdgeToPadEdgeClearance={0.15} minBoardEdgeClearance={0.25}',
          '      minViaHoleDiameter={0.30} minViaPadDiameter={0.45}',
          '      minViaHoleEdgeToViaHoleEdgeClearance={0.20}',
          '      minPlatedHoleDrillEdgeToDrillEdgeClearance={0.45}>']
allnets = sorted({n for c in connections.values() for n in c['connections'].values()})
for net in allnets:
    attrs = ' isGroundNet={true}' if net=='GND' else ' isPowerNet={true}' if net in ['PD_VBUS','DATA_VBUS','PD_VHV','V3V3','V1V1','LOGIC_IN'] else ''
    width=.30 if net in ['PD_VBUS','A_PLUS','A_MINUS','B_PLUS','B_MINUS','SENSE1','SENSE2'] else .16
    lines.append(f'      <net name="{net}"{attrs} nominalTraceWidth={{{width}}} />')
for i,(x,y) in enumerate([(-11.5,-11.5),(-11.5,11.5),(11.5,-11.5),(11.5,11.5)]):
    lines += [f'      <hole name="M{i+1}" pcbX={{{x}}} pcbY={{{y}}} diameter={{requirements.provisional_hole_diameter_mm}} />',
              f'      <keepout pcbX={{{x}}} pcbY={{{y}}} shape="circle" radius={{requirements.provisional_head_exclusion_radius_mm}} layers={{["top","bottom"]}} allowPlacements={{false}} />']
for sheet_index, (title,names) in enumerate(layout['sheets'].items()):
    lines.append(f'      <schematicsheet name="{title.replace("&","&amp;")}" sheetIndex={{{sheet_index}}} sheetSize="A4">')
    for name in names:
        c = connections[name]
        attrs = [f'name="{name}"', f'{{...position("{name}")}}']
        sch = layout['placements'][name]
        attrs += [f'schX={{{sch["schX"]}}}',f'schY={{{sch["schY"]}}}']
        if name in ['U_ENCODER','C_ENCODER','C_ENCODER_BULK'] or name.startswith('TP_'):
            attrs.append('doNotPlace={true}')
        if c['no_connect']:
            attrs.append('noConnect={'+json.dumps(['pin'+n for n in c['no_connect']])+'}')
        wiring = {('pin'+pin):('net.'+net) for pin,net in c['connections'].items()}
        attrs.append('connections={'+json.dumps(wiring)+'}')
        if name.startswith('TP_'):
            tag='testpoint';attrs+=['footprintVariant="pad"','padDiameter="1.1mm"']
        else:
            tag = parts[plan['components'][name]]['exported_symbol']
            # Purchased part values are fixed by the genuine imported definitions.
            # Verify their emitted values against config/connections.json; never override them.
        lines.append('        <'+tag+' '+' '.join(attrs)+' />')
    lines.append('      </schematicsheet>')
lines += ['    </board>','  )','}','']
(ROOT/'index.circuit.tsx').write_text('\n'.join(lines))
print('Generated native full-controller source: two layers, restored complete buzzer circuit, top/bottom fitted components, native A4 sheets; routing disabled')
