import { readFileSync, writeFileSync } from "node:fs"
import { convertCircuitJsonToPcbSvg } from "circuit-to-svg"
import { Resvg } from "@resvg/resvg-js"

const records = JSON.parse(readFileSync("artifacts/controller/unrouted.circuit.json", "utf8"))
for (const layer of ["top", "bottom"] as const) {
  const svg = convertCircuitJsonToPcbSvg(records, {layer, width:1400, height:1560,
    showSolderMask:false, showSolderPaste:false, shouldDrawRatsNest:false, showPinNumbers:true})
    .replace(/[ \t]+$/gm, "")
  writeFileSync(`artifacts/controller/${layer}.svg`, svg)
  writeFileSync(`artifacts/controller/${layer}.png`, new Resvg(svg).render().asPng())
}
