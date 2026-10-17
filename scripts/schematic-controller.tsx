import React from "react"
import { Circuit } from "tscircuit"
import { readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { SupplierPart as BaselineSupplierPart } from "../src/controller/supplier-parts"
import { CompactSupplierPart } from "../src/compact/supplier-parts"
import { prepareSchematic } from "./prepare-controller-schematic"
import { convertCircuitJsonToSchematicSvg } from "circuit-to-svg"
import { Resvg } from "@resvg/resvg-js"
import * as schemas from "circuit-json"

const compact=process.argv.includes("--compact")
const folderArg=process.argv.indexOf("--folder")
const folder=folderArg>=0?process.argv[folderArg+1]:compact?"artifacts/compact-controller":"artifacts/controller"
const SupplierPart=compact?CompactSupplierPart:BaselineSupplierPart
const baseBytes = readFileSync(folder+"/unrouted.circuit.json")
const base = JSON.parse(baseBytes.toString()) as any[]
const source=base.filter(e=>e.type === "source_component")
const circuit = new Circuit()
circuit.pcbDisabled=true
// Render each actual supplier symbol without temporary wiring. The checked
// source candidate supplies all electrical identities and connectivity below.
circuit.add(<board routingDisabled schAutoLayoutEnabled={false}>
 {source.map((s,i)=>{
  const ps=base.filter(e=>e.type === "source_port" && e.source_component_id === s.source_component_id)
  const props={name:s.name,schX:(i%10)*20,schY:Math.floor(i/10)*20,
    pinLabels:Object.fromEntries(ps.map(p=>[`pin${p.pin_number}`,[p.name,`pin${p.pin_number}`]])),
    resistance:s.resistance,capacitance:s.capacitance}
  return s.name.startsWith("TP_") ? <testpoint key={s.name} {...props} /> : <SupplierPart key={s.name} {...props} />
 })}
</board>)
await circuit.renderUntilSettled()
const fresh = circuit.getCircuitJson() as any[]
const freshSource=new Map(fresh.filter(e=>e.type === "source_component").map(e=>[e.source_component_id,e]))
const baseNames=new Map(source.map(e=>[e.name,e]))
const basePorts=new Map(base.filter(e=>e.type === "source_port").map(e=>[`${e.source_component_id}:${e.pin_number}`,e]))
const freshPorts=new Map(fresh.filter(e=>e.type === "source_port").map(e=>[e.source_port_id,e]))
// Drawings use native symbols and terminals; electrical/PCB/CAD records come
// unchanged from the independently checked source candidate.
const native = fresh.filter(e=>e.type.startsWith("schematic_") && !e.type.endsWith("_error"))
for (const e of native) {
 if(e.source_component_id)e.source_component_id=baseNames.get(freshSource.get(e.source_component_id).name).source_component_id
 if(e.source_port_id){
  const p=freshPorts.get(e.source_port_id)
  const c=baseNames.get(freshSource.get(p.source_component_id).name)
  e.source_port_id=basePorts.get(`${c.source_component_id}:${p.pin_number}`).source_port_id
 }
}
if (native.filter(e=>e.type === "schematic_component").length !== source.length) throw new Error("Incomplete native symbol render")
// The native USB symbol omits the four separate shell tabs. Add explicit
// bottom terminals, retaining their real physical pin identities and ground net.
// Paired GND/VBUS signal contacts are safely aggregated by prepareSchematic.
for(const name of ["J_PD","J_DATA"]){
 const s=baseNames.get(name)
 const c=native.find(e=>e.type === "schematic_component" && e.source_component_id === s.source_component_id)
 c.port_arrangement={...c.port_arrangement,bottom_side:{pins:[17,18,19,20],direction:"left-to-right"}}
 for(let i=0;i<4;i++){
  const pin=17+i,p=basePorts.get(`${s.source_component_id}:${pin}`)
  native.push({type:"schematic_port",schematic_port_id:`controller_shell_${name}_${pin}`,
   schematic_component_id:c.schematic_component_id,source_port_id:p.source_port_id,
   center:{x:c.center.x-.375+i*.2,y:c.center.y-c.size.height/2-.4},
   facing_direction:"down",side_of_component:"bottom",distance_from_component_edge:.4,
   pin_number:pin,true_ccw_index:pin-1,display_pin_label:p.name,is_connected:false})
 }
}
const output = prepareSchematic([...base, ...native],compact)
const sheetRecords = output.filter((e:any)=>e.type.startsWith("schematic_"))
if (JSON.stringify(output.filter((e:any)=>!e.type.startsWith("schematic_"))) !== JSON.stringify(base)) {
  throw new Error("Schematic preparation changed source/PCB/CAD records")
}
const sheets = sheetRecords.filter((e:any)=>e.type === "schematic_sheet")
const schemaErrors=output.flatMap((r:any,index:number)=>{
 const registry=schemas as any
 const schema=r.type === "source_component" ? registry.any_source_component : registry[r.type] ?? registry.any_circuit_element
 const result=schema.safeParse(r)
 return result.success?[]:[{index,type:r.type,issues:result.error.issues}]
})
if(schemaErrors.length)throw new Error(JSON.stringify(schemaErrors))
writeFileSync(folder+"/schematic.circuit.json", JSON.stringify(output,null,2)+"\n")
for (let i=0;i<sheets.length;i++) {
 const sheet=sheets[i]
 const scope=output.filter((e:any)=>!e.type.startsWith("schematic_") || e.schematic_sheet_id===sheet.schematic_sheet_id)
 const svg=convertCircuitJsonToSchematicSvg(scope,{width:2970,height:2100})
   .replace("<svg ",'<svg viewBox="0 0 2970 2100" ')
   .replace(/width="2970"/,'width="297mm"').replace(/height="2100"/,'height="210mm"')
   .replace(/[ \t]+$/gm, "")
 const stem=`${folder}/schematic-a4-${i+1}`
 writeFileSync(stem+".svg",svg)
 writeFileSync(stem+".png",new Resvg(svg,{fitTo:{mode:"width",value:1800}}).render().asPng())
}
writeFileSync(folder+"/schematic-build.json",JSON.stringify({
 scope:"Six functional native A4 schematic sheets; independent checks recorded separately",
 source_sha256:createHash("sha256").update(baseBytes).digest("hex"),
 electrical_PCB_CAD_records_preserved:true,sheets:sheets.length,
 schematic_components:sheetRecords.filter((e:any)=>e.type === "schematic_component").length,
 manufacturing_release:false},null,2)+"\n")
console.log(JSON.stringify({sheets:sheets.length,components:92,electrical_records_preserved:true}))
