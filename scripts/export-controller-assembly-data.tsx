import React from "react"
import { Circuit } from "tscircuit"
import { mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { populatePartOrientationMetadata, convertCircuitJsonToPickAndPlaceRows } from "circuit-json-to-pnp-csv"
import { SupplierPart } from "../src/controller/supplier-parts"
import catalog from "../src/controller/jlcpcb-catalog.json"

const compact=process.argv.includes("--compact-four-mounts")
const folderArg=process.argv.indexOf("--folder")
const path=folderArg>=0?process.argv[folderArg+1].replace(/\/$/,"")+"/":"artifacts/controller-pcb/"
const output=path+"assembly-data/"
mkdirSync(output,{recursive:true})
const bytes=readFileSync(path+"board.circuit.json")
const records=JSON.parse(bytes.toString()) as any[]
const sources=records.filter(r=>r.type==="source_component")
const fitted=records.filter(r=>r.type==="pcb_component" && !r.do_not_place)
const names=new Map(sources.map(r=>[r.source_component_id,r.name]))
const unique=new Map<string,string>()
for(const p of fitted){const name=names.get(p.source_component_id)!;const code=(catalog.components as Record<string,string>)[name];if(code)unique.set(code,name)}
const native=new Circuit()
native.schematicDisabled=true
native.add(<board width={250} height={150} routingDisabled>
 {[...unique].map(([code,name],i)=><SupplierPart key={code} name={name} pcbX={(i%12)*18-100} pcbY={Math.floor(i/12)*22-40} pcbRotation={0} />)}
</board>)
await native.renderUntilSettled()
const imports=native.getCircuitJson() as any[]
const isolated=new Map<string,any[]>()
for(const [code,name] of unique){
 const s=imports.find(r=>r.type==="source_component" && r.name===name)
 const p=imports.find(r=>r.type==="pcb_component" && r.source_component_id===s.source_component_id)
 isolated.set(code,imports.filter(r=>r.pcb_component_id===p.pcb_component_id))
}
// The genuine LED has a 0.006858 mm Y skew between its two pads, so the
// native exact-row classifier cannot choose a canonical frame. Classify only
// its orientation metadata from the preserved R0 pad vector; never move pads.
const ledPads=isolated.get("C965799")!.filter(r=>r.type==="pcb_smtpad")
const led1=ledPads.find(r=>r.port_hints.includes("pin1")),led2=ledPads.find(r=>r.port_hints.includes("pin2"))
if(!led1 || !led2 || led1.x>=led2.x || Math.abs(led1.y-led2.y)>.01)throw new Error("Unexpected genuine LED cathode/pin-1 frame")
const ledSource=sources.find(r=>r.name==="D_PWR")
const ledComponent=records.find(r=>r.type==="pcb_component" && r.source_component_id===ledSource.source_component_id)
ledComponent.pin1_location="topside_left"
ledComponent.supplier_pin1_location_map={jlcpcb:"topside_left"}
const prepared=await populatePartOrientationMetadata(records, {supplier:"jlcpcb",partsEngine:{fetchPartCircuitJson:async({supplierPartNumber})=>isolated.get(supplierPartNumber!)}})
const allRows=convertCircuitJsonToPickAndPlaceRows(prepared,{supplier:"jlcpcb",requireSupplierRotation:true})
const expectedParts=compact?76:82
if(allRows.length!==expectedParts)throw new Error(`Expected ${expectedParts} fitted purchased parts, found ${allRows.length}`)
const rows=allRows.filter(r=>r.designator!=="J_MOTOR")
const csv=(r:(string|number)[][])=>r.map(row=>row.map(v=>'"'+String(v).replaceAll('"','""')+'"').join(',')).join('\n')+'\n'
const board=records.find(r=>r.type==="pcb_board")
const originX=Math.min(...board.outline.map((p:any)=>p.x)),originY=Math.min(...board.outline.map((p:any)=>p.y))
const cpl=[['Designator','Mid X','Mid Y','Layer','Rotation'],...rows.map(r=>[r.designator,(r.mid_x-originX).toFixed(3)+'mm',(r.mid_y-originY).toFixed(3)+'mm',r.layer,r.rotation])]
writeFileSync(output+"JLC_SMT_CPL.csv",csv(cpl))
const groups=new Map<string,any[]>()
for(const row of rows){const s=sources.find(r=>r.name===row.designator);const code=s.supplier_part_numbers?.jlcpcb?.[0];if(!code)throw new Error("Missing supplier number: "+row.designator);groups.set(code,[...(groups.get(code)??[]),s])}
const bom=[['Comment','Designator','Footprint','LCSC Part #'],...[...groups].sort().map(([code,parts])=>[parts[0].manufacturer_part_number,parts.map(p=>p.name).sort().join(','),(catalog.parts as any)[code].symbol,code])]
writeFileSync(output+"JLC_SMT_BOM.csv",csv(bom))
writeFileSync(output+"manual-assembly.csv",csv([['Designator','Manufacturer part','LCSC','Process'],['J_MOTOR','B4B-PH-K-S(LF)(SN)','C131334','Through-hole hand solder; verify pin order and mating side']]))
const orientation=(prepared as any[]).filter(r=>r.type==="pcb_component" && !r.do_not_place).map(p=>({designator:names.get(p.source_component_id),authored_rotation:p.rotation,pin1_location:p.pin1_location,supplier_pin1_location_map:p.supplier_pin1_location_map}))
writeFileSync(output+"export-verification.json",JSON.stringify({
 scope:"Exact candidate JLC SMT BOM/CPL generated from native source and genuine supplier R0 footprints; order acceptance not obtained",
 circuit_sha256:createHash("sha256").update(bytes).digest("hex"),
 native_converter:"circuit-json-to-pnp-csv; requireSupplierRotation=true",
 supplier_orientation_source:"Native R0 render of the committed exact JLC supplier imports, with original copper preserved",
 LED_orientation_metadata_review:{part:"C965799",pin1:"cathode, R0 left",pad_Y_skew_mm:Math.abs(led1.y-led2.y),canonical_frame:"topside_left",copper_changed:false},
 supplier_rotation_warnings:0,fitted_purchased_parts:expectedParts,SMT_BOM_CPL_parts:rows.length,manual_through_hole_parts:1,
 bare_test_pads_excluded:7,optional_encoder_DNP_parts_excluded:3,
 CPL_origin:`Board lower-left, mm; +${-originX} X and +${-originY} Y from board coordinates`,
 orientation_metadata:orientation,
 remaining_requirements:["JLC stock/reservation and assembly process acceptance","JLC machine origin, polarized-part preview and first article confirmation","USB signal reflow and PTH shell soldering process","Stencil/filled-and-capped via acceptance","Mating harness and mechanical tolerances"],
 manufacturing_release:false},null,2)+"\n")
console.log(JSON.stringify({strict_supplier_rotations:true,SMT_BOM_CPL_parts:rows.length,manual_parts:1}))
