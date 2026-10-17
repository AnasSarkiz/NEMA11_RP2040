import React from "react"
import { Circuit } from "tscircuit"
import { createHash } from "node:crypto"
import { mkdirSync, readFileSync, existsSync, writeFileSync } from "node:fs"
import { execFileSync } from "node:child_process"
import * as schemas from "circuit-json"
import Example from "../examples/full-controller.circuit"
import catalog from "../src/controller/jlcpcb-catalog.json"

const circuit = new Circuit()
circuit.schematicDisabled = true
circuit.add(<Example />)
await circuit.renderUntilSettled()
const raw = circuit.getCircuitJson() as any[]
const source = new Map(raw.filter(e => e.type === "source_component").map(e => [e.source_component_id,e]))
const bare = new Set(raw.filter(e => e.type === "pcb_component" && source.get(e.source_component_id)?.name.startsWith("TP_")).map(e => e.pcb_component_id))
const dnp = new Set(raw.filter(e => e.type === "pcb_component" && e.do_not_place).map(e => e.pcb_component_id))
const unownedSilk = raw.filter(e => ["pcb_silkscreen_circle","pcb_silkscreen_text"].includes(e.type) && !e.pcb_component_id)
// This compiler produces invalid null ownership for board-level silk primitives.
// Keep supplier-owned silk intact; board annotations will be rebuilt during final silk layout.
const records = raw.filter(e => !unownedSilk.includes(e) && !(e.type === "pcb_solder_paste" && (bare.has(e.pcb_component_id) || dnp.has(e.pcb_component_id))))
const dirty = execFileSync("git",["status","--porcelain","--","imports/supplier"],{encoding:"utf8"}).trim()
const assetRevision = dirty ? "main" : execFileSync("git",["log","-n","1","--format=%H","--","imports/supplier"],{encoding:"utf8"}).trim()
const missingAssets: string[] = []
const cadPoseCorrections: any[] = []
for (const e of records) {
 if (e.pcb_component_id === null) delete e.pcb_component_id
 if (e.type === "pcb_component") for (const field of ["display_offset_x","display_offset_y"]) if (typeof e[field] === "number") e[field]=String(e[field])
 if (e.type !== "cad_component") continue
 if (source.get(e.source_component_id)?.name === "J_MOTOR") {
  // The genuine STEP lead section is 0.5500383 mm below the native holes.
  // Correct the assembly pose, preserving the supplier model and land pattern.
  const component=records.find(p=>p.type === "pcb_component" && p.pcb_component_id === e.pcb_component_id)
  const angle=component.rotation*Math.PI/180
  const localY=0.5500383
  const delta={x:-Math.sin(angle)*localY,y:Math.cos(angle)*localY,z:0}
  e.position.x+=delta.x;e.position.y+=delta.y
  cadPoseCorrections.push({component:"J_MOTOR",local_y_mm:localY,global_delta_mm:delta,
   reason:"Independent STEP lead sections versus native plated-hole centres"})
 }
 for (const field of ["model_obj_url","model_step_url"]) {
  if (typeof e[field] !== "string") continue
  const at=e[field].indexOf("/imports/supplier/")
  if (at < 0) {missingAssets.push(e[field]);continue}
  let relative=e[field].slice(at+1)
  // Exact native CH224A import now has its own committed identical-package models.
  if (source.get(e.source_component_id)?.name === "U_PD") relative=relative.replaceAll("CH224K","CH224A")
  if (!existsSync(relative)) missingAssets.push(relative)
  e[field]=`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${assetRevision}/${relative}`
 }
}
const schemaErrors=records.flatMap((r:any,index:number)=>{
 const registry=schemas as any
 const schema=r.type === "source_component" ? registry.any_source_component : registry[r.type] ?? registry.any_circuit_element
 const result=schema.safeParse(r)
 return result.success ? [] : [{index,type:r.type,issues:result.error.issues}]
})
const renderErrors=records.filter(e=>e.type.endsWith("_error"))
const bytes=JSON.stringify(records,null,2)+"\n"
mkdirSync("artifacts/controller",{recursive:true})
writeFileSync("artifacts/controller/unrouted.circuit.json",bytes)
const report={scope:"Full electrical source development candidate; copper, motor mounting and manufacturing not released",
 circuit_sha256:createHash("sha256").update(bytes).digest("hex"),
 source_components:records.filter(e=>e.type === "source_component").length,
 source_ports:records.filter(e=>e.type === "source_port").length,
 pcb_traces:records.filter(e=>e.type === "pcb_trace").length,
 source_asset_revision:assetRevision,source_assets_uncommitted:!!dirty,
 bare_or_DNP_paste_removed:raw.length-records.length-unownedSilk.length,
 unsupported_unowned_board_silk_excluded:unownedSilk.length,
 render_errors:renderErrors,schema_errors:schemaErrors,missing_supplier_models:missingAssets,
 cad_pose_corrections:cadPoseCorrections,
 motor_connector:"C131334 B4B-PH-K-S(LF)(SN), through-hole/manual assembly candidate",
 current_divider_high_ohms:20000,manufacturing_release:false}
writeFileSync("artifacts/controller/source-build.json",JSON.stringify(report,null,2)+"\n")
console.log(JSON.stringify(report,null,2))
if (renderErrors.length || schemaErrors.length || missingAssets.length) process.exitCode=1
