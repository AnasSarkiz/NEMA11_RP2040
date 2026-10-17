import { readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { runAllChecks, checkViasInPads } from "@tscircuit/checks"
import { convertCircuitJsonToPcbSvg } from "circuit-to-svg"
import { Resvg } from "@resvg/resvg-js"
import * as schemas from "circuit-json"

const path = "artifacts/controller-pcb/"
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
const offsets = JSON.parse(readFileSync("src/controller/thermal-via-offsets.json", "utf8"))
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
// Only the three explicitly reviewed ground thermal vias are omitted from the
// via-in-pad prohibition. Their required filled/capped fabrication is separate.
const strict = records.filter(r => !thermal.includes(r)).map(r => r.type === "pcb_board" ? { ...r, is_via_in_pad_allowed: false } : r)
// Keep all three thermal barrels present for connectivity and other checks.
const checks = await runAllChecks(records.map(r => r.type === "pcb_board" ? { ...r, is_via_in_pad_allowed: true } : r))
checks.push(...checkViasInPads(strict))
const errors = [...records, ...checks].filter(r => r.type.endsWith("_error"))
const unique = [...new Map(errors.map(r => [JSON.stringify(r), r])).values()]
const warnings = checks.filter(r => r.type.endsWith("_warning"))
writeFileSync(path + "native-drc.json", JSON.stringify({ scope: "Full 92-component controller native DRC",
  tool: "@tscircuit/checks", circuit_sha256: createHash("sha256").update(bytes).digest("hex"),
  strict_schema_pass: true, reviewed_thermal_vias: thermal.map(r => r.pcb_via_id),
  errors: unique, warnings, native_drc_pass: unique.length === 0, manufacturing_release: false }, null, 2) + "\n")
if (!process.argv.includes("--checks-only")) {
  for (const layer of ["top", "inner1", "inner2", "bottom"] as const) {
    const svg = convertCircuitJsonToPcbSvg(records, { layer, width: 1400, height: 1600,
      showSolderMask: false, showSolderPaste: false, shouldDrawRatsNest: false, showPinNumbers: true })
      .replace(/[ \t]+$/gm, "")
    writeFileSync(path + layer + ".svg", svg)
    writeFileSync(path + layer + ".png", new Resvg(svg).render().asPng())
  }
}
console.log(JSON.stringify({ schema_errors: 0, native_drc_errors: unique.length, warnings: warnings.length }))
// CI runs the independent geometric review next; report-only does not change
// the retained raw result or claim a native pass.
if (unique.length && !process.argv.includes("--report-only")) process.exitCode = 1
