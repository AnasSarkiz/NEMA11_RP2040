#!/usr/bin/env python3
"""Motor-face-sized front-anchored carrier proposal; not a qualified supplier part.

The nominal OEM STEP has nominal R3 rounded corners. The drawing does NOT guarantee
those radii: minimum channel clearance is an explicit unresolved requirement.
No rear motor holes or rear shaft are added or assumed.
"""
import hashlib
import json
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'imports/mechanical';OUT.mkdir(exist_ok=True)
front_z=-42
plate=cq.Workplane('XY').box(28,28,1).translate((0,0,front_z-.5)).val()
def cylinder(x,y,z,r,h):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
carrier=plate.cut(cylinder(0,0,front_z-1.1,11.7,1.2))
for x in [-11.5,11.5]:
 for y in [-11.5,11.5]:carrier=carrier.cut(cylinder(x,y,front_z-1.1,1.45,1.2))
for sign in [-1,1]:
 # Nominal corner is R3 at (11.1,11.1), not a straight chamfer.
 # The rail inner diagonal is 26.85 mm; its XY outer limits are 14.0 mm, within the frame.
 triangle=[(sign*14,12.85),(sign*12.85,14),(sign*14,14)]
 rail=cq.Workplane('XY').polyline(triangle).close().extrude(38.2).translate((0,0,front_z)).val()
 cap=cylinder(sign*12.5,12.5,-3.8,1.5,3)
 carrier=carrier.fuse(rail).fuse(cap)
 carrier=carrier.cut(cylinder(sign*12.5,12.5,-3.9,.625,3.2))
carrier=carrier.clean();assert carrier.isValid() and len(carrier.Solids())==1
step=OUT/'nema11-compact-front-carrier.step';cq.exporters.export(carrier,str(step))
vertices,triangles=carrier.tessellate(.05,.15)
obj=OUT/'nema11-compact-front-carrier.obj'
with obj.open('w') as f:
 f.write('# Custom compact front carrier proposal; mm; global PCB coordinates; NOT supplier CAD.\n')
 for v in vertices:f.write(f'v {v.x:.8f} {v.y:.8f} {v.z:.8f}\n')
 for a,b,c in triangles:f.write(f'f {a+1} {b+1} {c+1}\n')
motor=cq.importers.importStep(str(ROOT/'imports/motor/11HS12-0674S.step')).val().rotate((0,0,0),(0,0,1),90).translate((0,0,front_z))
volume=max(0,carrier.intersect(motor).Volume());gap=carrier.distance(motor)
b=carrier.BoundingBox()
report={'scope':'Custom 28 mm front-anchored carrier proposal, nominal OEM STEP collision check only','bounds_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],'valid_single_solid':True,'nominal_motor_intersection_mm3':volume,'nominal_motor_surface_distance_mm':gap,'within_28_3mm_frame_XY':max(abs(b.xmin),abs(b.xmax),abs(b.ymin),abs(b.ymax))<=14.15,'front_mount_pitch_mm':23,'front_hole_diameter_mm':2.9,'front_plate_thickness_mm':1,'pilot_clearance_diameter_mm':23.4,'PCB_mount_centres_mm':[[-12.5,12.5],[12.5,12.5]],'PCB_thread':'M1.6x0.35; tap-drill representation only','PCB_hole_candidate_diameter_mm':1.8,'motor_rear_holes_or_shaft_assumed':False,'all_fitted_electrical_parts_top':True,'required_motor_corner_channel':{'inner_diagonal_absX_plus_Y_mm':26.85,'nominal_OEM_STEP_corner_radius_mm':3.0,'corner_radius_guaranteed_by_OEM_drawing':False},'unresolved_requirements':['OEM minimum corner chamfer/fillet dimensions along complete body; nominal STEP is not a tolerance guarantee','Machining/flatness/chamfer/thread tolerances and 6061-T6 material approval','Two narrow rearward rails need strength, vibration and hot-motor validation','Genuine M2.5x4 front and M1.6x4 PCB fastener drawings, head/tool envelopes and tolerance-qualified engagement','Machine-side mounting interface and front pilot/shaft reach after the plate','Full harness bend radius, retention and wire-exit clearance','Finished PCB thickness maximum and mount positions require acceptance'],'files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [step,obj]],'manufacturing_release':False}
(ROOT/'artifacts/requirements/compact-front-carrier-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['unresolved_requirements','files']}))
assert volume<1e-5
