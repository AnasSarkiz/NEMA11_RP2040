import { readFileSync, writeFileSync, realpathSync } from "node:fs"
import { resolve, sep } from "node:path"
import { createHash } from "node:crypto"
import { convertCircuitJsonToGltf } from "circuit-json-to-gltf"

const root = process.cwd()
const compact=process.argv.includes("--compact")
const routed = process.argv.includes("--pcb")
const assembly = process.argv.includes("--assembly")
const fullPcb = process.argv.includes("--controller-pcb")
const controller = process.argv.includes("--controller") || assembly || fullPcb || compact
const path = compact ? "artifacts/compact-controller/" : fullPcb ? "artifacts/controller-pcb/" : controller ? "artifacts/controller/" : routed ? "artifacts/rp2040-pcb/" : "artifacts/rp2040-core/"
const filename = assembly ? "assembly.circuit.json" : fullPcb ? "board.circuit.json" : controller ? "unrouted.circuit.json" : routed ? "board.circuit.json" : "core.circuit.json"
const output = assembly ? "development-assembly.glb" : fullPcb ? "development-pcb.glb" : controller ? "development-controller.glb" : routed ? "development-pcb.glb" : "development-core.glb"
const bytes = readFileSync(path + filename)
const records = JSON.parse(bytes.toString())
const modelPaths = new Map<string, string>()
for (const record of records) {
  if (record.type !== "cad_component") continue
  for (const field of ["model_obj_url", "model_step_url"]) {
    const url = record[field]
    if (typeof url !== "string") continue
    const marker = "/imports/"
    const at = url.indexOf(marker)
    if (at < 0) throw new Error("Unexpected model source: " + url)
    const local = realpathSync(resolve(root, url.slice(at + 1)))
    if (!local.startsWith(resolve(root, "imports") + sep)) throw new Error("Model path escapes supplier directory")
    modelPaths.set(url, local)
  }
}
const used = new Map<string, { path: string; sha256: string; bytes: number }>()
// All requested supplier models must resolve to committed local assets. No
// remote model fallback or replacement geometry is used by this exporter.
globalThis.fetch = (async (input: any) => {
  const url = String(input instanceof Request ? input.url : input)
  const local = modelPaths.get(url)
  if (!local) throw new Error("Unrecognized model request: " + url)
  const data = readFileSync(local)
  used.set(local, { path: local.slice(root.length + 1),
    sha256: createHash("sha256").update(data).digest("hex"), bytes: data.length })
  return new Response(data, { status: 200 })
}) as typeof fetch
const result = await convertCircuitJsonToGltf(records, {
  format: "glb", boardTextureResolution: 1000, includeModels: true,
})
const glb = Buffer.from(result as ArrayBuffer)
if (glb.toString("ascii", 0, 4) !== "glTF" || glb.readUInt32LE(4) !== 2 || glb.readUInt32LE(8) !== glb.length) {
  throw new Error("Invalid GLB header")
}
if (!used.size) throw new Error("No original supplier model assets were loaded")
writeFileSync(path + output, glb)
writeFileSync(path + (assembly ? "assembly-3d-export-verification.json" : "3d-export-verification.json"), JSON.stringify({
  scope: assembly ? "Native PCB, OEM motor and original front carrier proposal; hardware and full harness absent" : controller ? "Full controller native development PCB; motor carrier and harness not included" : `${routed ? "Routed" : "Unrouted"} MCU subsystem development canvas; not completed motor assembly`,
  circuit_sha256: createHash("sha256").update(bytes).digest("hex"),
  glb_sha256: createHash("sha256").update(glb).digest("hex"), bytes: glb.length,
  original_supplier_assets_loaded: [...used.values()],
  motor_model_included: assembly, final_NEMA11_layout: false, manufacturing_release: false,
}, null, 2) + "\n")
console.log(JSON.stringify({ exported: path + output, bytes: glb.length,
  supplier_assets_loaded: used.size, manufacturing_release: false }))
