#!/usr/bin/env python3
"""Proposed front-anchored carrier, with open OEM wire exit; not a qualified part."""
import hashlib
import json
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'imports/mechanical'
OUT.mkdir(exist_ok=True)


def block(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz).translate((x, y, z)).val()


def cylinder(x, y, bottom, radius, height):
    return cq.Solid.makeCylinder(radius, height, cq.Vector(x, y, bottom))


# Absolute board coordinates: PCB center plane Z=0; OEM front face Z=-42.
carrier = block(0, 0, -42.5, 39, 39, 1)
# The unchanged OEM STEP also has a shallow front collar beyond the drawing's
# 22 mm pilot. This is a clearance opening, not a precision locating feature.
carrier = carrier.cut(cylinder(0, 0, -43.1, 11.7, 1.2))
for x in [-11.5, 11.5]:
    for y in [-11.5, 11.5]:
        carrier = carrier.cut(cylinder(x, y, -43.1, 1.7, 1.2))
for side in [-1, 1]:
    carrier = carrier.fuse(block(0, side * 17.5, (-42-3.8)/2, 39, 4, 38.2))
    for x in [-13, 13]:
        carrier = carrier.fuse(block(x, side * 15.75, -4.8, 5, 7.5, 2))
        carrier = carrier.fuse(cylinder(x, side * 13, -3.8, 2.5, 3))
for x in [-13, 13]:
    for y in [-13, 13]:
        # Tap-drill representation only; manufacturing callout is M2.5x0.45 THRU.
        carrier = carrier.cut(cylinder(x, y, -5.9, 1.025, 5.2))
carrier = carrier.clean()
assert carrier.isValid() and len(carrier.Solids()) == 1
step = OUT / 'nema11-front-carrier.step'
cq.exporters.export(carrier, str(step))
vertices, triangles = carrier.tessellate(.05, .15)
obj = OUT / 'nema11-front-carrier.obj'
with obj.open('w') as f:
    f.write('# Original proposed carrier; mm; global board coordinates. Not supplier CAD.\n')
    for v in vertices:
        f.write(f'v {v.x:.8f} {v.y:.8f} {v.z:.8f}\n')
    for a, b, c in triangles:
        f.write(f'f {a+1} {b+1} {c+1}\n')
b = carrier.BoundingBox()
proof = {'scope': 'Original front-anchored carrier CAD proposal, excluding fasteners/harness qualification',
         'material_requirement': '6061-T6 aluminum; surface finish and strength validation pending',
         'bounds_mm': [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],
         'valid_single_solid': True, 'body_side_clearance_to_max_28_3mm_motor_mm': (31-28.3)/2,
         'front_plate_thickness_mm': 1, 'front_pilot_clearance_hole_mm': 23.4,
         'pilot_opening_is_precision_locator': False,
         'motor_front_mount_holes': {'pitch_mm': 23, 'clearance_diameter_mm': 3.4, 'count': 4},
         'PCB_mount_threads': {'pitch_mm': 26, 'thread': 'M2.5x0.45 THRU', 'tap_drill_model_mm': 2.05, 'count': 4},
         'fastener_requirements': ['Four M2.5x4 front screws; actual length tolerance and head dimensions need a supplier drawing',
                                   'Four M2.5x5 PCB screws; actual tolerance/head/tool envelope and thread engagement need supplier verification'],
         'motor_rear_holes_or_shaft_assumed': False,
         'wire_exit_positive_X_open': True,
         'files': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in [step,obj]],
         'release_requirements': ['Machining tolerances, deburring and M2.5 thread acceptance',
                                  'Motor front screw engagement must remain below 3.5 mm minimum tapped depth',
                                  'Retain usable pilot projection and shaft clearance at worst-case tolerances',
                                  'Assembly and tool clearance, vibration/strength and hot motor validation',
                                  'Machine-side attachment interface is unspecified'],
         'manufacturing_release': False}
(ROOT / 'artifacts/requirements/front-carrier-proposal.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'single_valid_solid': True, 'triangles': len(triangles), 'manufacturing_release': False}))
