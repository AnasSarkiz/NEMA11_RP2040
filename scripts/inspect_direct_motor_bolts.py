#!/usr/bin/env python3
"""Inspect existing OEM rear bolt heads; never infer a thread from their size.

Reads the unchanged supplier solid and the current electrical baseline. A
successful inspection does not mean that baseline meets the new mount contract.
Use --require-compatible-pcb to fail explicitly on a pattern mismatch.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

import cadquery as cq
import cairosvg
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--input',type=Path,default=ROOT/'artifacts/compact-six-layer/board.circuit.json')
parser.add_argument('--out',type=Path,default=ROOT/'artifacts/requirements/direct-motor-bolts')
parser.add_argument('--require-compatible-pcb',action='store_true')
args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
path=ROOT/'imports/motor/11HS12-0674S.step'
sha=hashlib.sha256(path.read_bytes()).hexdigest()
original=json.loads((ROOT/'artifacts/requirements/motor-originals.json').read_text())
assert sha==original['STEP_sha256'],'The original motor model changed'
shape=cq.importers.importStep(str(path)).val()
assert shape.isValid() and len(shape.Solids())==5
body=max(shape.Solids(),key=lambda solid:solid.Volume())
rear=body.BoundingBox().zmax
heads={}
for face in body.Faces():
    surface=BRepAdaptor_Surface(face.wrapped)
    if surface.GetType()!=GeomAbs_Cylinder:continue
    cylinder=surface.Cylinder();origin=cylinder.Location();direction=cylinder.Axis().Direction()
    bounds=face.BoundingBox();radius=cylinder.Radius()
    # This known OEM model has small convex rear head surfaces, distinct from
    # its larger corner fillets, concave recesses and front mounting bores.
    if not (abs(direction.Z())>.999 and 1.5<radius<2.75 and bounds.zmin>rear-5 and min(abs(origin.X()),abs(origin.Y()))>8):continue
    point=surface.Value((surface.FirstUParameter()+surface.LastUParameter())/2,
                        (surface.FirstVParameter()+surface.LastVParameter())/2)
    normal=face.normalAt(cq.Vector(point.X(),point.Y(),point.Z()))
    radial_dot=normal.x*(point.X()-origin.X())+normal.y*(point.Y()-origin.Y())
    if radial_dot<.9*radius:continue
    key=(round(origin.X(),6),round(origin.Y(),6))
    entry=dict(axis_XY_mm=list(key),head_diameter_mm=round(2*radius,6),
               convex_cylindrical_surface_Z_mm=[round(bounds.zmin,6),round(bounds.zmax,6)])
    if key in heads:assert heads[key]==entry
    heads[key]=entry
policy=json.loads((ROOT/'config/direct-motor-bolt-mounting.json').read_text())
assert sorted(heads)==sorted(map(tuple,policy['nominal_STEP_axes_mm']))
assert len(heads)==4 and all(e['head_diameter_mm']==4 for e in heads.values())
records=json.loads(args.input.read_text())
holes=[r for r in records if r['type']=='pcb_hole' and not r.get('pcb_component_id')]
best=min(itertools.permutations(holes),key=lambda rows:sum((h['x']-p[0])**2+(h['y']-p[1])**2 for h,p in zip(rows,sorted(heads)))) if len(holes)==4 else []
matches=[]
for h,p in zip(best,sorted(heads)):
    distance=((h['x']-p[0])**2+(h['y']-p[1])**2)**.5
    matches.append(dict(PCB_hole_XY_mm=[h['x'],h['y']],motor_axis_XY_mm=list(p),axis_error_mm=round(distance,9)))
compatible=len(matches)==4 and all(m['axis_error_mm']<1e-6 for m in matches)
input_name=str(args.input.resolve().relative_to(ROOT)) if args.input.resolve().is_relative_to(ROOT) else str(args.input.resolve())
svg=args.out/'OEM-rear-bolt-view.svg'
cq.exporters.export(body,str(svg),opt=dict(width=800,height=800,marginLeft=30,marginTop=30,
                                         projectionDir=(0,0,1),showHidden=False,showAxes=False,strokeWidth=.5))
cairosvg.svg2png(url=str(svg),write_to=str(svg.with_suffix('.png')),background_color='white')
report=dict(scope='Original OEM STEP nominal rear bolt-head inspection and PCB-axis comparison only',
            motor=policy['motor'],STEP_sha256=sha,original_model_unchanged=True,original_valid_solids=5,
            nominal_rear_head_axes_verified=True,nominal_rear_heads=[heads[k] for k in sorted(heads)],
            nominal_rear_bolt_pitch_mm=23,nominal_motor_body_rear_max_Z_mm=round(rear,6),
            rear_bolt_thread_or_shank_diameter_inferred=False,rear_bolt_length_or_engagement_inferred=False,
            front_M2_5_threads_do_not_establish_rear_bolt_thread=True,
            PCB_file=input_name,PCB_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
            PCB_hole_axis_comparisons=matches,PCB_motor_bolt_axis_alignment_pass=compatible,
            PCB_hole_diameter_hardware_and_tolerance_qualified=False,
            custom_carrier_allowed=False,new_rear_motor_threads_or_shaft_assumed=False,
            inspection_pass=True,manufacturing_release=False)
(args.out/'nominal-step-bolt-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['nominal_rear_heads','PCB_hole_axis_comparisons']}))
if args.require_compatible_pcb and not compatible:raise SystemExit('PCB holes do not align with the existing motor bolt axes')
