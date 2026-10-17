import React from "react"
import { Circuit } from "tscircuit"
import { readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import * as schemas from "circuit-json"
import Preview from "../examples/controller-assembly.circuit"

const circuit=new Circuit()
circuit.schematicDisabled=true
circuit.add(<Preview />)
await circuit.renderUntilSettled()
const fresh=circuit.getCircuitJson() as any[]
const baseBytes=readFileSync("artifacts/controller/schematic.circuit.json")
const base=JSON.parse(baseBytes.toString()) as any[]
const motor=fresh.find(e=>e.type === "source_component" && e.name === "OEM_11HS12_0674S")
if(!motor)throw new Error("Native assembly omitted the OEM motor")
const cad=fresh.find(e=>e.type === "cad_component" && e.source_component_id === motor.source_component_id)
if(!cad || cad.position.x !== 0 || cad.position.y !== 0 || cad.position.z !== -42 || cad.rotation.z !== 90) {
 throw new Error("Unexpected native OEM motor pose: "+JSON.stringify(cad))
}
const extra=[{...motor,source_component_id:"source_component_OEM_motor"},
 {...cad,source_component_id:"source_component_OEM_motor",cad_component_id:"cad_component_OEM_motor"}]
for(const e of extra)delete e.subcircuit_id
const output=[...base,...extra]
const schemaErrors=output.flatMap((r:any,index:number)=>{
 const registry=schemas as any
 const schema=r.type === "source_component" ? registry.any_source_component : registry[r.type] ?? registry.any_circuit_element
 const result=schema.safeParse(r)
 return result.success?[]:[{index,type:r.type,issues:result.error.issues}]
})
if(schemaErrors.length)throw new Error(JSON.stringify(schemaErrors))
writeFileSync("artifacts/controller/assembly.circuit.json",JSON.stringify(output,null,2)+"\n")
writeFileSync("artifacts/controller/assembly-build.json",JSON.stringify({
 scope:"Native PCB and exact OEM motor clearance arrangement; front carrier, harness and retention absent",
 source_sha256:createHash("sha256").update(baseBytes).digest("hex"),
 original_PCB_electrical_schematic_CAD_records_preserved:true,
 motor_raw_front_datum_z_mm:-42,motor_rotation_z_degrees:90,
 motor_max_body_rear_z_mm:-9,PCB_bottom_z_mm:-.8,
 drawing_maximum_body_to_PCB_gap_mm:8.2,
 motor_rear_mounting_holes_or_rear_shaft_assumed:false,
 carrier_harness_fasteners_included:false,manufacturing_release:false},null,2)+"\n")
console.log("Native assembly arrangement generated with exact OEM motor geometry.")
