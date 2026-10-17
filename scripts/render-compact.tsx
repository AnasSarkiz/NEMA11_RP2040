import {readFileSync,writeFileSync} from "node:fs"
import {convertCircuitJsonToPcbSvg} from "circuit-to-svg"
import {Resvg} from "@resvg/resvg-js"
const path="artifacts/compact-controller/"
const records=JSON.parse(readFileSync(path+(process.argv.includes("--routing")?"routing-construction.circuit.json":"unrouted.circuit.json"),"utf8"))
const svg=convertCircuitJsonToPcbSvg(records,{layer:"top",width:1800,height:1800,showSolderMask:false,showSolderPaste:false,shouldDrawRatsNest:false,showPinNumbers:true})
writeFileSync(path+"placement-top.svg",svg)
writeFileSync(path+"placement-top.png",new Resvg(svg).render().asPng())
