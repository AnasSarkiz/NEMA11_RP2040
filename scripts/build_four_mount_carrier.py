#!/usr/bin/env python3
"""Four separately fitted carrier quarters, anchored only at verified front threads.

Nominal geometry and sampled insertion paths only. This is a custom proposal;
no supplier model, tolerance, stiffness or hardware qualification is implied.
"""
import hashlib,json,math
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'imports/mechanical';OUT.mkdir(exist_ok=True)
config=json.loads((ROOT/'config/compact-four-mounts.json').read_text())
front_z=-42
motor=cq.importers.importStep(str(ROOT/'imports/motor/11HS12-0674S.step')).val().rotate((0,0,0),(0,0,1),90).translate((0,0,front_z))
def cylinder(x,y,z,r,h):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
# The small gaps separate the front plate into four independent pieces. Each
# piece slides radially over its own motor corner before the PCB is installed.
plate=cq.Workplane('XY').box(13.9,13.9,1).translate((7.05,7.05,front_z-.5)).val()
quarter=plate.cut(cylinder(0,0,front_z-1.1,11.7,1.2))
quarter=quarter.cut(cylinder(11.5,11.5,front_z-1.1,1.45,1.2))
triangle=[(14,12.85),(12.85,14),(14,14)]
rail=cq.Workplane('XY').polyline(triangle).close().extrude(38.2).translate((0,0,front_z)).val()
quarter=quarter.fuse(rail).fuse(cylinder(12.5,12.5,-3.8,1.5,3)).cut(cylinder(12.5,12.5,-3.9,.625,3.2)).clean()
assert quarter.isValid() and len(quarter.Solids())==1
parts=[quarter.rotate((0,0,0),(0,0,1),a) for a in [0,90,180,270]]
shape=cq.Compound.makeCompound(parts)
assert shape.isValid() and len(shape.Solids())==4
step=OUT/'nema11-four-mount-front-carrier.step';cq.exporters.export(shape,str(step))
step.write_text('\n'.join(line.rstrip() for line in step.read_text().splitlines())+'\n')
obj=OUT/'nema11-four-mount-front-carrier.obj'
vertices,triangles=shape.tessellate(.05,.15)
with obj.open('w') as f:
 f.write('# Custom four-piece front carrier proposal; mm; not supplier CAD.\n')
 for v in vertices:f.write(f'v {v.x:.8f} {v.y:.8f} {v.z:.8f}\n')
 for a,b,c in triangles:f.write(f'f {a+1} {b+1} {c+1}\n')
collisions=[];paths=[]
for i,part in enumerate(parts):
 volume=max(0,part.intersect(motor).Volume())
 collisions.append({'quarter':i,'motor_intersection_mm3':volume})
 assert volume<1e-5
 angle=math.radians(45+90*i)
 for distance in [0,.1,.25,.5,1,2,3,5,8,12,20,30]:
  moved=part.translate((math.cos(angle)*distance,math.sin(angle)*distance,0))
  motor_volume=max(0,moved.intersect(motor).Volume())
  other_volume=sum(max(0,moved.intersect(other).Volume()) for j,other in enumerate(parts) if j!=i)
  paths.append({'quarter':i,'radial_displacement_mm':distance,'motor_intersection_mm3':motor_volume,'other_quarters_intersection_mm3':other_volume})
  assert max(motor_volume,other_volume)<1e-5
b=shape.BoundingBox();bounds=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
assert max(abs(bounds[i]) for i in [0,1,3,4])<=14.15
report={'scope':'Custom four-piece, front-anchored carrier: nominal CAD and sampled radial insertion paths only',
 'bounds_mm':bounds,'valid_solids':4,'separate_carrier_quarters':4,'front_mount_pitch_mm':23,
 'front_mount_thread':'Existing motor M2.5 front threads only','front_clearance_hole_diameter_mm':2.9,
 'front_plate_thickness_mm':1,'pilot_clearance_diameter_mm':23.4,
 'PCB_mount_centres_mm':[[m['x'],m['y']] for m in config['mounts']],
 'PCB_mount_thread_candidate':'M1.6x0.35; 1.25 mm tap-drill shown, not a finished thread model',
 'PCB_support_bearing_z_mm':-.8,'PCB_support_bearing_diameter_mm':3,
 'motor_rear_holes_or_shaft_assumed':False,'within_28_3mm_frame_XY':True,
 'nominal_motor_intersection_mm3':sum(r['motor_intersection_mm3'] for r in collisions),
 'nominal_quarter_collision_checks':collisions,'sampled_radial_installation_checks':paths,
 'assembly_sequence':['Slide each separate quarter radially inward at its front datum','Fit four front M2.5 screws, leaving alignment adjustment','Fit PCB onto four rear support faces and install four M1.6 screws','Align quarters, then tighten front screws; torque and access require hardware qualification'],
 'required_motor_corner_channel':{'inner_diagonal_absX_plus_absY_mm':26.85,'nominal_OEM_STEP_corner_radius_mm':3,'corner_radius_guaranteed_by_drawing':False},
 'rail_cross_section_mm2':.5*1.15**2,'strength_qualified':False,
 'unresolved_requirements':['Extremely narrow corner rails require a load, stiffness, vibration and thermal assessment; current proposal is not approved for use','OEM minimum corner relief over full body is not guaranteed by drawing','Genuine M2.5 front and M1.6 PCB screw drawings, maximum head/tool envelopes, lengths, engagement, torque and availability','Continuous swept-path, tolerance, physical assembly and tool-access validation; finite sampled paths are not a full proof','Front-machine mounting and lost shaft/pilot reach after adding the 1 mm plate','Harness insulation OD, termination, bend radius and strain relief'],
 'files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [step,obj]],
 'manufacturing_release':False}
(ROOT/'artifacts/requirements/four-mount-carrier-proposal.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['files','unresolved_requirements','sampled_radial_installation_checks','assembly_sequence']}))
