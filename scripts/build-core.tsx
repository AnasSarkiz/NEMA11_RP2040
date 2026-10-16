import React from "react"
import { Circuit } from "tscircuit"
import { createHash } from "node:crypto"
import { mkdirSync, writeFileSync } from "node:fs"
import * as schemas from "circuit-json"
import Example from "../examples/rp2040-core.circuit"

const circuit = new Circuit()
circuit.schematicDisabled = true // Functional sheets are generated from physical pins separately.
circuit.add(<Example />)
await circuit.renderUntilSettled()
const raw = circuit.getCircuitJson() as any[]
const sources = new Map(raw.filter(e => e.type === "source_component").map(e => [e.source_component_id, e]))
const debugParts = new Set(raw.filter(e => e.type === "pcb_component" &&
  sources.get(e.source_component_id)?.name.startsWith("TP_")).map(e => e.pcb_component_id))
// The compiler adds default paste to every custom SMT pad. Debug pads must stay bare.
const records = raw.filter(e => !(e.type === "pcb_solder_paste" && debugParts.has(e.pcb_component_id)))
const revision = "596a8b8a5187dfd60924de4b8ac0c93e13d99680"
for (const record of records) {
  // This compiler emits numeric label offsets; Circuit JSON requires strings.
  if (record.type === "pcb_component") {
    for (const field of ["display_offset_x", "display_offset_y"]) {
      if (typeof record[field] === "number") record[field] = String(record[field])
    }
  }
  if (record.type !== "cad_component") continue
  for (const field of ["model_obj_url", "model_step_url"]) {
    if (typeof record[field] === "string") record[field] = record[field].replace(
      "/NEMA14_RP2040/main/imports/supplier/", `/NEMA14_RP2040/${revision}/imports/supplier/`)
  }
}
const errors = records.filter(e => e.type.endsWith("_error"))
const schemaErrors = records.flatMap((record, index) => {
  const registry = schemas as any
  const schema = record.type === "source_component" ? registry.any_source_component : registry[record.type] ?? registry.any_circuit_element
  const result = schema.safeParse(record)
  return result.success ? [] : [{ index, type: record.type, issues: result.error.issues }]
})
mkdirSync("artifacts/rp2040-core", { recursive: true })
const bytes = JSON.stringify(records, null, 2) + "\n"
writeFileSync("artifacts/rp2040-core/core.circuit.json", bytes)
writeFileSync("artifacts/rp2040-core/schema-verification.json", JSON.stringify({
  circuit_sha256: createHash("sha256").update(bytes).digest("hex"),
  passed: schemaErrors.length === 0, records_checked: records.length, errors: schemaErrors,
}, null, 2) + "\n")
const report = {
  scope: "RP2040 subsystem source and supplier CAD only; not a controller PCB",
  sha256: createHash("sha256").update(bytes).digest("hex"),
  source_components: records.filter(e => e.type === "source_component").length,
  source_ports: records.filter(e => e.type === "source_port").length,
  routed_traces: records.filter(e => e.type === "pcb_trace").length,
  bare_debug_pad_paste_records_removed: raw.length - records.length,
  native_render_errors: errors,
  native_schema_errors: schemaErrors,
  final_NEMA11_layout: false, manufacturing_release: false,
}
writeFileSync("artifacts/rp2040-core/build-report.json", JSON.stringify(report, null, 2) + "\n")
console.log(JSON.stringify(report, null, 2))
if (errors.length || schemaErrors.length) process.exitCode = 1
