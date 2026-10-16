import { mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { convertCircuitJsonToGerberFiles } from "circuit-json-to-gerber"

const path = "artifacts/rp2040-pcb/"
const bytes = readFileSync(path + "board.circuit.json")
const records = JSON.parse(bytes.toString())
const report = JSON.parse(readFileSync(path + "native-drc.json", "utf8"))
if (report.circuit_sha256 !== createHash("sha256").update(bytes).digest("hex") || !report.subsystem_internal_drc_pass) {
  throw new Error("Current PCB subsystem internal checks must pass before review CAM export")
}
const directory = path + "review-cam/"
mkdirSync(directory, { recursive: true })
const files = convertCircuitJsonToGerberFiles(records)
const hashes = Object.entries(files).map(([name, data]) => {
  if (!/^[A-Za-z0-9_.-]+$/.test(name)) throw new Error("Unexpected CAM filename")
  writeFileSync(directory + name, data)
  return {name, bytes: Buffer.byteLength(data), sha256: createHash("sha256").update(data).digest("hex")}
})
writeFileSync(directory + "DO-NOT-FABRICATE.txt", "MCU SUBSYSTEM DEVELOPMENT CANVAS ONLY.\nFull motor controller, power inputs, mounting, motor/harness and manufacturing qualification are incomplete.\nThese files exist for CAM toolchain review, not a PCB order.\nDo not assemble or connect a motor from this incomplete design.\n")
writeFileSync(path + "review-cam-export.json", JSON.stringify({scope: "native tscircuit CAM exporter review only",
  circuit_sha256: createHash("sha256").update(bytes).digest("hex"), files: hashes,
  production_BOM_CPL_included: false, manufacturing_release: false}, null, 2) + "\n")
console.log(JSON.stringify({review_cam_files: hashes.length, manufacturing_release: false}))
