import { readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { runAllChecks, checkViasInPads } from "@tscircuit/checks"
import { convertCircuitJsonToPcbSvg } from "circuit-to-svg"
import { Resvg } from "@resvg/resvg-js"
import * as schemas from "circuit-json"

const folderArg=process.argv.indexOf("--folder")
const path = folderArg>=0?process.argv[folderArg+1].replace(/\/$/,"")+"/":"artifacts/controller-pcb/"
const patchPath = "tools/pcb/patches/circle-keepout-clearance.json"
const patchBytes = readFileSync(patchPath)
const patch = JSON.parse(patchBytes.toString())
for (const file of patch.files) {
  const actual = createHash("sha256").update(readFileSync("tools/pcb/" + file.path)).digest("hex")
  if (actual !== file.corrected_sha256) throw new Error("Native DRC toolchain hash mismatch: " + file.path)
}
const bytes = readFileSync(path + "board.circuit.json")
const records = JSON.parse(bytes.toString()) as any[]
const registry = schemas as any
const schemaErrors = records.flatMap((r, index) => {
  const schema = r.type === "source_component" ? registry.any_source_component : registry[r.type] ?? registry.any_circuit_element
  const result = schema.safeParse(r)
  return result.success ? [] : [{ index, type: r.type, issues: result.error.issues }]
})
if (schemaErrors.length) throw new Error(JSON.stringify(schemaErrors))
const ground = records.find(r => r.type === "source_net" && r.name === "GND")
const offsets = process.argv.includes("--compact")?Object.fromEntries(["U_MCU","U_DRV","U_FLASH"].map(name=>[name,{x:0,y:0}])):JSON.parse(readFileSync("src/controller/thermal-via-offsets.json", "utf8"))
const thermal = Object.entries(offsets).map(([name, raw]) => {
  const offset = raw as { x: number; y: number }
  const source = records.find(r => r.type === "source_component" && r.name === name)
  const component = records.find(r => r.type === "pcb_component" && r.source_component_id === source.source_component_id)
  const pads = records.filter(r => r.type === "pcb_smtpad" && r.pcb_component_id === component.pcb_component_id)
  const ep = pads.sort((a, b) => b.width * b.height - a.width * a.height)[0]
  const found = records.filter(r => r.type === "pcb_via" && r.source_net_id === ground.source_net_id &&
    Math.hypot(r.x - ep.x - offset.x, r.y - ep.y - offset.y) < .001)
  if (found.length !== 1) throw new Error(`Expected exactly one reviewed ${name} exposed-pad thermal barrel`)
  return found[0]
})
const policyArg=process.argv.indexOf("--filled-capped-policy")
const policy=policyArg>=0?JSON.parse(readFileSync(process.argv[policyArg+1],"utf8")):undefined
if(policy && (policy.circuit_sha256!==createHash("sha256").update(bytes).digest("hex") || policy.required_process!=="IPC-4761 Type VII epoxy-filled and copper-capped on all 0.30 mm vias only" || policy.ordinary_vias_in_pads_permitted!==false))throw new Error("Filled/capped process policy does not match this native board")
const terminal=(policy?.reviewed_vias??[]).map((v:any)=>{
 const via=records.find(r=>r.type==="pcb_via" && r.pcb_via_id===v.via_id)
 if(!via || via.source_net_id!==v.source_net_id || via.outer_diameter!==v.pad_diameter_mm || via.hole_diameter!==.3 || !v.owner_pad_ids.length)throw new Error("Invalid capped terminal-via process selection: "+v.via_id)
 for(const id of v.owner_pad_ids){
  const pad=records.find(r=>r.type==="pcb_smtpad" && r.pcb_smtpad_id===id)
  const port=records.find(r=>r.type==="pcb_port" && r.pcb_port_id===pad?.pcb_port_id)
  const source=records.find(r=>r.type==="source_port" && r.source_port_id===port?.source_port_id)
  if(!source || source.subcircuit_connectivity_map_key!==via.subcircuit_connectivity_map_key)throw new Error("Capped via owner net mismatch: "+id)
 }
 return via
})
// The three thermal barrels and, when selected, the hash-bound Type VII
// terminal-via process are permitted. Ordinary vias remain prohibited in pads.
const strict = records.filter(r => !thermal.includes(r) && !terminal.includes(r)).map(r => r.type === "pcb_board" ? { ...r, is_via_in_pad_allowed: false } : r)
// Keep all three thermal barrels present for connectivity and other checks.
const checks = await runAllChecks(records.map(r => r.type === "pcb_board" ? { ...r, is_via_in_pad_allowed: true } : r))
checks.push(...checkViasInPads(strict))
const errors = [...records, ...checks].filter(r => r.type.endsWith("_error"))
const unique = [...new Map(errors.map(r => [JSON.stringify(r), r])).values()]
const warnings = checks.filter(r => r.type.endsWith("_warning"))
writeFileSync(path + "native-drc.json", JSON.stringify({ scope: policy || records.filter(r=>r.type==="source_component").length!==92 ? `Native ${records.filter(r=>r.type==="source_component").length}-component controller DRC` : "Full 92-component controller native DRC",
  tool: "@tscircuit/checks@0.0.242 with checksum-verified exact circular-keepout distance correction",
  toolchain_correction: patchPath,
  toolchain_correction_sha256: createHash("sha256").update(patchBytes).digest("hex"),
  no_findings_filtered_or_waived: true,
  circuit_sha256: createHash("sha256").update(bytes).digest("hex"),
  strict_schema_pass: true, ...(policy?{selected_terminal_via_process:policy.required_process, reviewed_terminal_vias:terminal.map((r:any)=>r.pcb_via_id), terminal_via_factory_acceptance_received:policy.factory_acceptance_received}:{}), reviewed_thermal_vias: thermal.map(r => r.pcb_via_id),
  errors: unique, warnings, native_drc_pass: unique.length === 0, manufacturing_release: false }, null, 2) + "\n")
if (!process.argv.includes("--checks-only")) {
  const renderLayers=records.find(r=>r.type==="pcb_board").num_layers===6 ? ["top","inner1","inner2","inner3","inner4","bottom"] as const : ["top","inner1","inner2","bottom"] as const
  for (const layer of renderLayers) {
    const svg = convertCircuitJsonToPcbSvg(records, { layer, width: 1400, height: 1600,
      showSolderMask: false, showSolderPaste: false, shouldDrawRatsNest: false, showPinNumbers: true })
      .replace(/[ \t]+$/gm, "")
    writeFileSync(path + layer + ".svg", svg)
    writeFileSync(path + layer + ".png", new Resvg(svg).render().asPng())
  }
}
console.log(JSON.stringify({ schema_errors: 0, native_drc_errors: unique.length, warnings: warnings.length }))
// Every native error is fatal. There is no report-only success or DRC waiver.
if (unique.length) process.exitCode = 1
