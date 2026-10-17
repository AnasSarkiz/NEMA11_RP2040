import React from "react"
import { Circuit } from "tscircuit"
import { readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import * as schemas from "circuit-json"
import BaselinePreview from "../examples/controller-assembly.circuit"
import CompactPreview from "../examples/compact-assembly.circuit"
import FourMountPreview from "../examples/four-mount-assembly.circuit"

// Carrier files are retained solely to reproduce frozen historical checkpoints.
// The active user requirement is direct mounting on the OEM motor case bolts.
if(!process.argv.includes("--historical-carrier"))throw new Error(
 "Carrier assembly is superseded by direct motor-bolt mounting. Rear bolt thread/length and the matching PCB are pending verification. Use --historical-carrier only to reproduce an archived carrier checkpoint.")

const compact=process.argv.includes("--compact")
const folderArg=process.argv.indexOf("--folder")
const folder=folderArg>=0?process.argv[folderArg+1]:compact?"artifacts/compact-controller":"artifacts/controller"
const Preview=process.argv.includes("--four-mounts")?FourMountPreview:compact?CompactPreview:BaselinePreview
const circuit=new Circuit()
circuit.schematicDisabled=true
circuit.add(<Preview />)
await circuit.renderUntilSettled()
const fresh=circuit.getCircuitJson() as any[]
const routed=process.argv.includes("--pcb")
const basePath=compact?folder+(routed?"/board.circuit.json":"/schematic.circuit.json"):routed?"artifacts/controller-pcb/board.circuit.json":"artifacts/controller/schematic.circuit.json"
const baseBytes=readFileSync(basePath)
const base=JSON.parse(baseBytes.toString()) as any[]
if(routed)base.push(...JSON.parse(readFileSync(folder+"/schematic.circuit.json","utf8")).filter((e:any)=>e.type.startsWith("schematic_")))
const motor=fresh.find(e=>e.type === "source_component" && e.name === "OEM_11HS12_0674S")
if(!motor)throw new Error("Native assembly omitted the OEM motor")
const cad=fresh.find(e=>e.type === "cad_component" && e.source_component_id === motor.source_component_id)
if(!cad || cad.position.x !== 0 || cad.position.y !== 0 || cad.position.z !== -42 || cad.rotation.z !== 90) {
 throw new Error("Unexpected native OEM motor pose: "+JSON.stringify(cad))
}
const extra=[{...motor,source_component_id:"source_component_OEM_motor"},
 {...cad,source_component_id:"source_component_OEM_motor",cad_component_id:"cad_component_OEM_motor"}]
const carrier=fresh.find(e=>e.type === "source_component" && e.name === "FRONT_CARRIER_PROPOSAL")
const carrierCad=fresh.find(e=>e.type === "cad_component" && e.source_component_id === carrier?.source_component_id)
if(!carrier || !carrierCad || Object.values(carrierCad.position).some(v=>v!==0) || Object.values(carrierCad.rotation).some(v=>v!==0))throw new Error("Unexpected carrier CAD pose")
extra.push({...carrier,source_component_id:"source_component_front_carrier"},
 {...carrierCad,source_component_id:"source_component_front_carrier",cad_component_id:"cad_component_front_carrier"})
for(const e of extra)delete e.subcircuit_id
const output=[...base,...extra]
const schemaErrors=output.flatMap((r:any,index:number)=>{
 const registry=schemas as any
 const schema=r.type === "source_component" ? registry.any_source_component : registry[r.type] ?? registry.any_circuit_element
 const result=schema.safeParse(r)
 return result.success?[]:[{index,type:r.type,issues:result.error.issues}]
})
if(schemaErrors.length)throw new Error(JSON.stringify(schemaErrors))
writeFileSync(folder+"/assembly.circuit.json",JSON.stringify(output,null,2)+"\n")
writeFileSync(folder+"/assembly-build.json",JSON.stringify({
 scope:"Native PCB, exact OEM motor and original front carrier proposal; hardware and full harness absent",
 PCB_source_file:basePath,PCB_routed:routed,
 source_sha256:createHash("sha256").update(baseBytes).digest("hex"),
 original_PCB_electrical_schematic_CAD_records_preserved:true,
 motor_raw_front_datum_z_mm:-42,motor_rotation_z_degrees:90,
 motor_max_body_rear_z_mm:-9,PCB_bottom_z_mm:-.8,
 drawing_maximum_body_to_PCB_gap_mm:8.2,
 motor_rear_mounting_holes_or_rear_shaft_assumed:false,
 front_carrier_proposal_included:true,
 carrier_harness_fasteners_included:false,manufacturing_release:false},null,2)+"\n")
console.log("Native assembly generated with exact OEM motor and front carrier proposal.")
