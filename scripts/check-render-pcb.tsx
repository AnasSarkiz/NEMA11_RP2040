import { readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { runAllChecks, checkViasInPads } from "@tscircuit/checks"
import { convertCircuitJsonToPcbSvg } from "circuit-to-svg"
import { Resvg } from "@resvg/resvg-js"
import * as schemas from "circuit-json"

const path = "artifacts/rp2040-pcb/"
const bytes = readFileSync(path + "board.circuit.json")
const records = JSON.parse(bytes.toString())
const registry = schemas as any
const schemaErrors = records.flatMap((r: any, index: number) => {
  const schema = r.type === "source_component" ? registry.any_source_component : registry[r.type] ?? registry.any_circuit_element
  const result = schema.safeParse(r)
  return result.success ? [] : [{ index, type: r.type, issues: result.error.issues }]
})
if (schemaErrors.length) throw new Error(JSON.stringify(schemaErrors))
const mcu = records.find((r: any) => r.type === "source_component" && r.name === "U_MCU")
const component = records.find((r: any) => r.type === "pcb_component" && r.source_component_id === mcu.source_component_id)
const ep = records.find((r: any) => r.type === "pcb_smtpad" && r.pcb_component_id === component.pcb_component_id && r.width > 1 && r.height > 1)
const ground = records.find((r: any) => r.type === "source_net" && r.name === "GND")
// Only the inherited MCU exposed-pad thermal barrel is an allowed via-in-pad.
const thermal = records.filter((r: any) => r.type === "pcb_via" && r.source_net_id === ground.source_net_id &&
  Math.hypot(r.x - (ep.x - .7), r.y - (ep.y + .2)) < .001)
if (thermal.length !== 1) throw new Error("Expected exactly one reviewed MCU thermal barrel")
const strict = records.filter((r: any) => !thermal.includes(r)).map((r: any) => r.type === "pcb_board" ? {...r, is_via_in_pad_allowed: false} : r)
const checks = await runAllChecks(strict)
checks.push(...checkViasInPads(strict))
const errors = [...records.filter((r: any) => r.type.endsWith("_error")), ...checks.filter((r: any) => r.type.endsWith("_error"))]
const unique = [...new Map(errors.map((r: any) => [r.message, r])).values()]
const warnings = checks.filter((r: any) => r.type.endsWith("_warning"))
const scope = JSON.parse(readFileSync("config/core-pcb-scope.json", "utf8"))
const expected = scope.expected_open_external_interfaces as Record<string, string>
const observed = new Set<string>()
const expectedOpen = (error: any): boolean => {
  if (error.type !== "pcb_port_not_connected_error" || error.pcb_port_ids?.length !== 1) return false
  const pp = records.find((r: any) => r.type === "pcb_port" && r.pcb_port_id === error.pcb_port_ids[0])
  const sp = records.find((r: any) => r.type === "source_port" && r.source_port_id === pp?.source_port_id)
  const component = records.find((r: any) => r.type === "source_component" && r.source_component_id === sp?.source_component_id)
  const net = records.find((r: any) => r.type === "source_net" && r.subcircuit_connectivity_map_key === sp?.subcircuit_connectivity_map_key)
  const pin = `${component?.name}.${sp?.pin_number}`
  if (expected[pin] !== net?.name || observed.has(pin)) return false
  observed.add(pin)
  return true
}
const unexpected = unique.filter((r: any) => !expectedOpen(r))
const missingExpected = Object.keys(expected).filter(pin => !observed.has(pin))
writeFileSync(path + "native-drc.json", JSON.stringify({scope: "MCU subsystem only", tool: "@tscircuit/checks",
  circuit_sha256: createHash("sha256").update(bytes).digest("hex"), strict_schema_pass: true,
  reviewed_thermal_vias: thermal.map((r: any) => r.pcb_via_id), errors: unique, warnings,
  expected_open_external_interfaces: expected, observed_expected_open_interfaces: [...observed],
  unexpected_errors: unexpected, missing_expected_open_interfaces: missingExpected,
  subsystem_internal_drc_pass: unexpected.length === 0 && missingExpected.length === 0,
  full_controller_drc_pass: false,
  manufacturing_release: false}, null, 2) + "\n")
for (const layer of ["top", "inner1", "inner2", "bottom"] as const) {
  const svg = convertCircuitJsonToPcbSvg(records, {layer, width: 1400, height: 1400,
    showSolderMask: false, showSolderPaste: false, shouldDrawRatsNest: false, showPinNumbers: true})
    .replace(/[ \t]+$/gm, "")
  writeFileSync(path + layer + ".svg", svg)
  writeFileSync(path + layer + ".png", new Resvg(svg).render().asPng())
}
console.log(JSON.stringify({schema_errors: 0, native_drc_errors: unique.length,
  expected_external_opens: observed.size, unexpected_errors: unexpected.length,
  missing_expected_open_interfaces: missingExpected.length, warnings: warnings.length}))
if (unexpected.length || missingExpected.length) process.exitCode = 1
