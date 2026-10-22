"""Screen untouched exact-import JSX against the GCT USB4145 locating holes.

This checks only explicit numeric hole geometry, not the complete footprint,
pin mapping, CAD pose, electrical ratings or assembly approval.
"""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
data = args.source.read_bytes()
text = data.decode('utf8')
holes = []
unsupported = []
for tag in re.findall(r'<hole\b[^>]*>', text):
    attrs = {}
    for name in ['pcbX', 'pcbY', 'diameter']:
        match = re.search(r'\b' + name + r'''=["']([-+\d.eE]+)mm["']''', tag)
        if match:
            attrs[name] = float(match.group(1))
    if len(attrs) == 3:
        holes.append(attrs)
    else:
        unsupported.append(tag)
geometry = False
spacing = None
if len(holes) == 2 and not unsupported:
    a, b = holes
    spacing = math.hypot(a['pcbX'] - b['pcbX'], a['pcbY'] - b['pcbY'])
    geometry = (all(abs(h['diameter'] - 0.71) <= 0.01 for h in holes)
                and abs(spacing - 8.0) <= 0.02
                and abs(a['pcbY'] - b['pcbY']) <= 0.02)
report = {
    'part': 'C5815189',
    'manufacturer_part': 'USB4145-03-0070-C',
    'source': str(args.source),
    'source_sha256': hashlib.sha256(data).hexdigest(),
    'manufacturer_evidence': 'docs/GCT-USB4145-drawing.pdf, page 2',
    'required': {'locating_holes': 2, 'diameter_mm': 0.71, 'pitch_mm': 8.0},
    'observed_explicit_holes': holes,
    'observed_pitch_mm': spacing,
    'unsupported_hole_syntax': unsupported,
    'locator_geometry_passed': geometry,
    'full_component_approved': False,
    'limitations': 'Explicit numeric exact-import JSX only. Unsupported syntax blocks this screen; review native output instead. This screen does not approve the rest of the footprint or model.'
}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(0 if geometry else 1)
