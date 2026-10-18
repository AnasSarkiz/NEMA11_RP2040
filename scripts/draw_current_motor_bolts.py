#!/usr/bin/env python3
"""A4 mechanical review of the actual current PCB holes; not a drill release."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / 'artifacts/requirements/direct-motor-bolts'
path = ROOT / 'artifacts/compact-six-layer/board.circuit.json'
records = json.loads(path.read_text())
config = json.loads((ROOT / 'config/compact-motor-bolts.json').read_text())
audit = json.loads((folder / 'nominal-step-bolt-audit.json').read_text())
assert audit['PCB_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
assert audit['PCB_motor_bolt_axis_alignment_pass']
drc = json.loads((ROOT / 'artifacts/compact-six-layer/native-drc.json').read_text())
assert drc['circuit_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
error_count = len(drc['errors'])
holes = [e for e in records if e['type'] == 'pcb_hole' and not e.get('pcb_component_id')]
assert len(holes) == 4
fig = plt.figure(figsize=(210/25.4, 297/25.4))
fig.text(.08, .95, 'CURRENT PCB — MOTOR BOLT PATTERN', size=15, weight='bold')
fig.text(.08, .922, '11HS12-0674S  |  Native tscircuit PCB  |  Dimensions in mm', size=10)
fig.text(.08, .89, 'DESIGN REVIEW ONLY — NOT FABRICATION READY', color='#a02020', size=11, weight='bold')
ax = fig.add_axes([.12, .35, .76, .51])
ax.add_patch(Rectangle((-14.15, -14.15), 28.3, 28.3, fill=False, edgecolor='gray', linestyle='--', label='28.3 maximum motor frame'))
ax.add_patch(Rectangle((-14, -14), 28, 28, fill=False, edgecolor='black', lw=1.5, label='28.0 PCB outline'))
for h in holes:
    x, y = h['x'], h['y']
    m = next(m for m in config['mounts'] if m['x'] == x and m['y'] == y)
    assert h['hole_diameter'] == m['diameter']
    ax.add_patch(Circle((x, y), m['radius'], color='#ffe1c2', ec='#ab641f', lw=.6))
    ax.add_patch(Circle((x, y), h['hole_diameter']/2, color='white', ec='black', lw=1))
    ax.plot([x-2.7, x+2.7], [y, y], color='#555555', lw=.4, linestyle='-.')
    ax.plot([x, x], [y-2.7, y+2.7], color='#555555', lw=.4, linestyle='-.')
    ax.text(x+(2 if x < 0 else -2), y+(2.6 if y < 0 else -3), f'({x:g}, {y:g})', ha='left' if x < 0 else 'right', fontsize=7)
for x in [-11.5, 11.5]:ax.plot([x, x], [14.5, 18], color='black', lw=.5)
ax.annotate('', xy=(-11.5, 17), xytext=(11.5, 17), arrowprops=dict(arrowstyle='<->', lw=.7))
ax.text(0, 17.4, '23.00 bolt pitch', ha='center', fontsize=9)
for y in [-11.5, 11.5]:ax.plot([-14.5, -18], [y, y], color='black', lw=.5)
ax.annotate('', xy=(-17, -11.5), xytext=(-17, 11.5), arrowprops=dict(arrowstyle='<->', lw=.7))
ax.text(-17.8, 0, '23.00 bolt pitch', va='center', rotation=90, fontsize=9)
ax.text(0, -16, '4 × Ø2.70 THROUGH — PROVISIONAL', ha='center', fontsize=9, weight='bold')
ax.text(0, -18, 'Head exclusion R2.35 on every copper layer', ha='center', fontsize=8)
ax.set(xlim=(-20, 20), ylim=(-20, 20), aspect='equal');ax.axis('off')
notes = [
    '• Hole centres: X/Y = ±11.50 about PCB and motor centre.',
    '• Axes match four existing rear bolt heads in unchanged OEM STEP.',
    '• OEM rear head Ø4 nominal; design head envelope Ø4.5 + 0.1 radial.',
    '• Ø2.70 drill reserves clearance for shank up to 2.5; thread unverified.',
    '• Front M2.5 callout does not specify the rear motor case bolts.',
    '• Rear bolt length, engagement, torque and insulation remain open.',
    '• No custom carrier. No invented motor rear threads or rear shaft.',
    '• Component placement/routing must clear the changed holes.',
    f'• Current native DRC: {error_count} errors. Prior CAM/BOM/CPL are superseded.',
]
for i, line in enumerate(notes):fig.text(.08, .29-i*.019, line, fontsize=8.5)
sha = hashlib.sha256(path.read_bytes()).hexdigest()
fig.text(.08, .085, 'Current native PCB SHA-256:', size=7)
fig.text(.08, .071, sha, size=6.5, family='monospace')
fig.text(.08, .045, 'Nominal geometry review. Hardware tolerances and complete assembly are not qualified.', size=7)
pdf = folder / 'current-PCB-motor-bolts-A4.pdf'
fig.savefig(pdf)
fig.savefig(folder / 'current-PCB-motor-bolts.svg')
fig.savefig(folder / 'current-PCB-motor-bolts.png', dpi=140)
reader = PdfReader(pdf);assert len(reader.pages) == 1
page = reader.pages[0];size = [float(page.mediabox.width)*25.4/72, float(page.mediabox.height)*25.4/72]
assert max(abs(a-b) for a,b in zip(size,[210,297])) < .01
proof = dict(scope='A4 drawing from current native PCB hole geometry and OEM-axis audit', PCB_sha256=sha,
             PDF_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(), PDF_page_mm=size,
             holes=[dict(x=h['x'], y=h['y'], diameter=h['hole_diameter']) for h in holes],
             current_motor_bolt_axis_alignment_pass=True, native_DRC_errors=error_count, rear_hardware_qualified=False,
             manufacturing_release=False)
(folder / 'current-drawing-verification.json').write_text(json.dumps(proof, indent=2)+'\n')
print(json.dumps(proof))
