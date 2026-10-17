import { mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { convertCircuitJsonToGerberFiles } from "circuit-json-to-gerber"

const folderArg=process.argv.indexOf("--folder")
const path = folderArg>=0?process.argv[folderArg+1].replace(/\/$/,"")+"/":"artifacts/controller-pcb/"
const bytes = readFileSync(path + "board.circuit.json")
const sha = createHash("sha256").update(bytes).digest("hex")
const audit = JSON.parse(readFileSync(path + "independent-copper-audit.json", "utf8"))
if (audit.circuit_sha256 !== sha || audit.errors.length) throw new Error("Current physical copper audit must pass")
const directory = path + "review-cam/"
mkdirSync(directory, { recursive: true })
const files = convertCircuitJsonToGerberFiles(JSON.parse(bytes.toString()))
const manifest = Object.entries(files).map(([name, data]) => {
  if (!/^[A-Za-z0-9_.-]+$/.test(name)) throw new Error("Unexpected CAM filename")
  writeFileSync(directory + name, data)
  return { name, bytes: Buffer.byteLength(data), sha256: createHash("sha256").update(data).digest("hex") }
})
writeFileSync(directory + "DO-NOT-FABRICATE.txt", "Full controller CAM development review only.\nIndependent CAM comparison, native DRC review, assembly/harness, stencil and supplier process acceptance remain required.\nThese files are not a fabrication release.\n")
writeFileSync(path + "review-cam-export.json", JSON.stringify({ scope: "Full controller native CAM development review",
  circuit_sha256: sha, files: manifest, manufacturing_release: false }, null, 2) + "\n")
console.log(JSON.stringify({ review_cam_files: manifest.length, manufacturing_release: false }))
