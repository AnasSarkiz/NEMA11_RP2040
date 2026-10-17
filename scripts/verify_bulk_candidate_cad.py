#!/usr/bin/env python3
"""Retain every solid from the official Panasonic STEP in a native OBJ mesh."""
import hashlib,json,re
from pathlib import Path
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1];F=ROOT/'imports/compact-candidates/EEHZC1V680XP';step=F/'EEHZC1V680XP.official.step';shape=cq.importers.importStep(str(step)).val();assert shape.isValid() and len(shape.Solids())==4
b=shape.BoundingBox();bounds=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax];assert abs(b.ylen-7.701)<.01 and abs(b.xlen-7.3)<.01 and abs(b.zlen-6.6)<.01
vertices,faces=shape.tessellate(.02,.1);obj=F/'EEHZC1V680XP.official.obj'
with obj.open('w') as f:
    f.write('# Derived from unchanged official Panasonic DS_Alumi_D8 STEP; original mm coordinates; all four solids.\n')
    for v in vertices:f.write(f'v {v.x:.8f} {v.y:.8f} {v.z:.8f}\n')
    for a,b,c in faces:f.write(f'f {a+1} {b+1} {c+1}\n')
# Express the unchanged manufacturer geometry in a reusable PCB R0 frame.
# This is a rigid datum conversion, not a body/lead/polarity geometry edit.
# The original STEP is retained byte-for-byte. A single PCB-Z rotation then
# suffices in native component CAD, avoiding ambiguous mixed-axis Euler order.
aligned=shape.rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),180)
assert aligned.isValid() and len(aligned.Solids())==4 and abs(aligned.Volume()-shape.Volume())<1e-8
aligned_step=F/'EEHZC1V680XP.board-frame.step';cq.exporters.export(aligned,str(aligned_step))
text=aligned_step.read_text();text=re.sub(r"(FILE_NAME\([^\n]*,)'\d{4}-\d\d-\d\dT[^']*'",r"\1'2026-01-01T00:00:00'",text);aligned_step.write_text(text)
aligned_vertices,aligned_faces=aligned.tessellate(.02,.1)
with (F/'EEHZC1V680XP.board-frame.obj').open('w') as f:
    f.write('# Official Panasonic DS_Alumi_D8 geometry; mm; rigid X+90 then Z+180 datum conversion; all four solids.\n')
    for v in aligned_vertices:f.write(f'v {v.x:.8f} {v.y:.8f} {v.z:.8f}\n')
    for a,b,c in aligned_faces:f.write(f'f {a+1} {b+1} {c+1}\n')
# OCCT enlarges a tessellated shape's bounding box by its mesh deflection.
# Read the exported exact BRep afresh, independently of that display mesh.
converted=cq.importers.importStep(str(aligned_step)).val().BoundingBox();converted_bounds=[converted.xmin,converted.ymin,converted.zmin,converted.xmax,converted.ymax,converted.zmax]
assert abs(converted.zmin)<1e-5 and abs(converted.zmax-7.701)<.01
def pads(text):
    return {int(pin):[float(v) for v in [x,y,w,h]] for pin,x,y,w,h in re.findall(r'<smtpad portHints=\{\["pin([12])"\]\} pcbX="([\-\d.]+)mm" pcbY="([\-\d.]+)mm" width="([\d.]+)mm" height="([\d.]+)mm"',text)}
old=pads((ROOT/'imports/supplier/RVT1V470M0605/RVT1V470M0605.tsx').read_text());new=pads((F/'EEHZC1V680XP.tsx.original').read_text());assert set(old)==set(new)=={1,2}
report=dict(scope='Genuine JLC native import and exact official manufacturer CAD candidate; not yet selected in a routed PCB',part='Panasonic EEHZC1V680XP',LCSC='C178649',native_import_command='tsci import C178649 --jlcpcb --download --use-exact-footprint --exclude-pin-attributes',native_import_exit_code=0,official_CAD_URL='https://industrial.panasonic.com/ww/system/files/data/download/cad/DS_Alumi_D8.zip',official_datasheet_URL='https://industrial.panasonic.com/cdbs/www-data/pdf/RDD0000/ABA0000C1234.pdf',official_STEP_valid=True,official_STEP_solids=4,official_STEP_raw_bounds_mm=bounds,official_raw_height_axis='+Y; PCB pose needs +90 degrees X rotation',mesh_vertices=len(vertices),mesh_triangles=len(faces),mesh_linear_tolerance_mm=.02,mesh_angular_tolerance_rad=.1,all_official_solids_retained=True,manufacturer_geometry_not_rescaled_or_cropped=True,original_supplier_pad_definitions=new,maximum_pad_parameter_difference_from_RVT_mm=max(abs(a-b) for pin in old for a,b in zip(old[pin],new[pin])),native_3D_pose_polarity_and_board_fit_verified=False,stock_observation=json.loads((ROOT/'artifacts/requirements/hybrid-bulk-stock-observation.json').read_text()),files=[dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(F.iterdir()) if p.is_file()],manufacturing_release=False)
report['files']=[entry for entry in report['files'] if not entry['path'].endswith('.tsx')]
report['board_frame_conversion']=dict(rigid_rotations_degrees=[dict(axis='X',angle=90),dict(axis='Z',angle=180)],valid_solids=4,source_and_converted_volume_mm3=[shape.Volume(),aligned.Volume()],source_STEP_preserved=True,body_and_leads_not_rescaled_or_cropped=True,board_R0_bounds_mm=converted_bounds,PCB_contact_plane_z_mm=0,positive_terminal_axis='Negative X after conversion; matches native pin1 left footprint',native_board_pose_verified=False)
(ROOT/'artifacts/requirements/hybrid-bulk-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(official_STEP_solids=4,official_STEP_valid=True,board_frame_bounds_mm=converted_bounds,maximum_pad_parameter_difference_from_RVT_mm=report['maximum_pad_parameter_difference_from_RVT_mm'],proposed_part_in_routed_board=False)))
