#!/usr/bin/env python3
"""Freeze a verified compact placement assembly as a separate native package."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'artifacts/compact-controller';OUT=ROOT/'prototypes/compact-placement-0.1.0'
subprocess.run(['python3','scripts/verify_compact_milestone.py'],cwd=ROOT,check=True)
path=SRC/'assembly.circuit.json';revision=subprocess.check_output(['git','log','-n','1','--format=%H','--',str(path.relative_to(ROOT))],cwd=ROOT,text=True).strip()
assert subprocess.check_output(['git','show',revision+':'+str(path.relative_to(ROOT))],cwd=ROOT)==path.read_bytes()
records=json.loads(path.read_text());assert sum(e['type']=='source_port' for e in records)==340 and not any(e['type']=='pcb_trace' for e in records)
OUT.mkdir(parents=True,exist_ok=True);data=(json.dumps(records,separators=(',',':'))+'\n').encode();index=OUT/'index.circuit.json'
if index.exists():assert index.read_bytes()==data,'Existing prototype snapshots must not be rewritten'
index.write_bytes(data)
package=dict(name='@tsci/AnasSarkiz.NEMA11_RP2040_Compact_Prototype',version='0.1.0',description='UNROUTED 28 mm all-top controller placement, six A4 schematic sheets and native OEM motor/carrier assembly; NOT fabrication ready',main='index.circuit.json',type='module',private=False,repository=dict(type='git',url='https://github.com/AnasSarkiz/NEMA11_RP2040.git'))
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n');(OUT/'tscircuit.config.json').write_text(json.dumps(dict(includeBoardFiles=['index.circuit.json'],previewComponentPath='index.circuit.json'),indent=2)+'\n')
proof=json.loads((SRC/'milestone-verification.json').read_text());receipt=dict(package=package['name'],version='0.1.0',scope=proof['scope'],source_milestone_commit=revision,circuit_sha256=hashlib.sha256(data).hexdigest(),source_components=94,electrical_components=92,physical_ports=340,native_models=84,schematic_sheets=6,placement_schematic_and_nominal_3D_verified=True,physical_routing_complete=False,registry_published=False,manufacturing_release=False,limitations=proof['limitations'])
(OUT/'package-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
(OUT/'README.md').write_text('''# NEMA11 RP2040 compact placement prototype 0.1.0

**UNROUTED DEVELOPMENT MILESTONE — DO NOT FABRICATE.**

Native tscircuit full controller source, six connected A4 schematic sheets,
82 genuine supplier component models, the unchanged OEM 11HS12-0674S motor and
a custom front-anchored compact carrier proposal. All fitted electrical parts
are on top of a nominal 28 × 28 mm PCB; their nominal bodies fit within the
motor drawing's 28.3 × 28.3 mm maximum frame. The optional encoder remains DNP.

92 electrical components, 340 physical terminals and all 64 reference functional
nets are preserved. The smaller genuine MLT-5020 buzzer removes one dummy NC
terminal; the PH motor connector, 20k/10k reference divider and rated 0.24 ohm
shunts are documented changes from exact published NEMA14 v1.13.0. NEMA14 is
unchanged.

Native source/pin/netlist/schematic checks pass. Independent checks verify all
340 original supplier pad geometries, zero touching pad pairs, minimum 0.199619
mm foreign-pad gap, 0.255 mm copper-edge clearance and 2,346 nominal JLC
component spacing pairs. Six-sheet drawing/ERC and all 84 native 3D bounds pass.
These are placement/source results, not a zero-open routed PCB certificate.

**Remaining requirements:** complete copper routing, clock/USB escape paths,
USB impedance/stackup, grounding, thermal/current/regen qualification, final
readable silkscreen, exact routed BOM/CPL/CAM, panel/process/stock acceptance,
manufacturer dimensional tolerances, full harness/plug/contact/wire-OD validation
and genuine fasteners. The compact carrier uses the motor's front threads only;
its narrow corner rails need OEM corner-radius acceptance and strength testing.
No rear motor holes or rear shaft are invented. The original GCT STEP compound
validity limitation remains reported; its nominal solids and connector hole fit
pass. OEM lead stubs extend beyond the frame; arbitrary cables are not covered
by the PCB component-body fit result.

[Source and review artifacts](https://github.com/AnasSarkiz/NEMA11_RP2040)
''')
print('Prepared immutable compact native placement prototype 0.1.0 from '+revision)
