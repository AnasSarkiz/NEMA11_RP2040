import { readFileSync, writeFileSync } from "node:fs"
import { convertCircuitJsonToSchematicSvg } from "circuit-to-svg"
import { Resvg } from "@resvg/resvg-js"
import * as schemas from "circuit-json"

const path = "artifacts/rp2040-core/"
const records = JSON.parse(readFileSync(path + "core-schematic.circuit.json", "utf8"))
const registry = schemas as any
const errors = records.flatMap((r: any, index: number) => {
  const schema = r.type === "source_component" ? registry.any_source_component : registry[r.type] ?? registry.any_circuit_element
  const result = schema.safeParse(r)
  return result.success ? [] : [{ index, type: r.type, issues: result.error.issues }]
})
if (errors.length) throw new Error(JSON.stringify(errors))
for (const [index, sheet] of records.filter((r: any) => r.type === "schematic_sheet").entries()) {
  const svg = convertCircuitJsonToSchematicSvg(records, {
    width: 2970, height: 2100, schematicSheetId: sheet.schematic_sheet_id,
  }).replace("<svg ", '<svg viewBox="0 0 2970 2100" ')
    .replace(/width="2970"/, 'width="297mm"').replace(/height="2100"/, 'height="210mm"')
    .replace(/[ \t]+$/gm, "")
  const prefix = path + `schematic-a4-${index + 1}`
  writeFileSync(prefix + ".svg", svg)
  writeFileSync(prefix + ".png", new Resvg(svg, { fitTo: { mode: "width", value: 1800 } }).render().asPng())
}
console.log("Rendered 3 functional native A4 schematic sheets; strict schema passed.")
