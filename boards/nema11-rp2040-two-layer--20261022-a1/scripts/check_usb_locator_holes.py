"""Screen untouched GCT USB4145 exact-import locator geometry, not full approval."""
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
cutouts = []
for tag in re.findall(r'<cutout\b[^>]*>', text):
    points = re.search(r'points=\{(\[.*?\])\}', tag, re.S)
    if points:
        cutouts.append(json.loads(points[1]))
    else:
        unsupported.append(tag)


def inside(point, polygon):
    x, y = point
    result = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        dx, dy = b['x'] - a['x'], b['y'] - a['y']
        cross = (x - a['x']) * dy - (y - a['y']) * dx
        if abs(cross) < 1e-9 and min(a['x'], b['x']) - 1e-9 <= x <= max(a['x'], b['x']) + 1e-9 and min(a['y'], b['y']) - 1e-9 <= y <= max(a['y'], b['y']) + 1e-9:
            return True
        if (a['y'] > y) != (b['y'] > y) and x < a['x'] + (y - a['y']) * dx / dy:
            result = not result
    return result


geometry = False
slot = None
pitch = None
if len(holes) == 1 and len(cutouts) == 1 and not unsupported:
    polygon = cutouts[0]
    xs, ys = [p['x'] for p in polygon], [p['y'] for p in polygon]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    width, height = max(xs) - min(xs), max(ys) - min(ys)
    area = abs(sum(a['x'] * b['y'] - b['x'] * a['y'] for a, b in zip(polygon, polygon[1:] + polygon[:1]))) / 2
    pitch = math.hypot(cx - holes[0]['pcbX'], cy - holes[0]['pcbY'])
    # Drawing tolerance is ±0.05 mm. Require clearance for the minimum
    # 0.96 x 0.66 capsule, including its middle; a bow-tie cutout must fail.
    samples = [(cx + offset + 0.33 * math.cos(i * math.tau / 64), cy + 0.33 * math.sin(i * math.tau / 64)) for offset in [-0.15, 0, 0.15] for i in range(64)]
    interior = all(inside(p, polygon) for p in samples)
    slot = {'center': {'x': cx, 'y': cy}, 'width_mm': width, 'height_mm': height, 'polygon_area_mm2': area, 'nominal_capsule_area_mm2': 0.71 * (1.01 - 0.71) + math.pi * (0.71 / 2) ** 2, 'contains_minimum_slot_interior': interior, 'polygon': polygon}
    geometry = (abs(holes[0]['diameter'] - 0.71) <= 0.05 and abs(width - 1.01) <= 0.05 and abs(height - 0.71) <= 0.05 and abs(pitch - 8.0) <= 0.05 and abs(cy - holes[0]['pcbY']) <= 0.05 and interior)
report = {'part': 'C5815189', 'manufacturer_part': 'USB4145-03-0070-C', 'source': str(args.source), 'source_sha256': hashlib.sha256(data).hexdigest(), 'manufacturer_evidence': 'docs/GCT-USB4145-drawing.pdf, page 2', 'required': {'circular_hole_diameter_mm': 0.71, 'horizontal_slot_mm': [1.01, 0.71], 'pitch_mm': 8.0, 'drawing_tolerance_mm': 0.05}, 'observed_circular_holes': holes, 'observed_polygon_cutout_count': len(cutouts), 'observed_slot': slot, 'observed_pitch_mm': pitch, 'unsupported_syntax': unsupported, 'locator_geometry_passed': geometry, 'full_component_approved': False, 'correction': 'Earlier two-circle interpretation was incorrect. Drawing specifies one circle and one horizontal slot.', 'limitations': 'Explicit numeric hole and polygon-cutout JSX only. Unsupported syntax requires native-output review. Does not approve remaining footprint, pins, CAD pose or assembly.'}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'observed_slot'}, indent=2))
if slot:
    print(json.dumps({k: v for k, v in slot.items() if k != 'polygon'}, indent=2))
raise SystemExit(0 if geometry else 1)
