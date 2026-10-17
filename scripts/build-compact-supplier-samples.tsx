import React from "react"
import { Circuit } from "tscircuit"
import { mkdirSync, writeFileSync } from "node:fs"
import { MLT_5020 } from "../imports/compact-candidates/MLT_5020/MLT_5020"
import { B4B_PH_SM4_TB_LF__SN_ } from "../imports/compact-candidates/B4B_PH_SM4_TB_LF__SN_/B4B_PH_SM4_TB_LF__SN_"
const c=new Circuit()
c.schematicDisabled=true
c.add(<board width={50} height={30} routingDisabled>
 <MLT_5020 name="BZ_COMPACT" pcbX={-10} noConnect={["_POS","_NEG","NC"]} />
 <B4B_PH_SM4_TB_LF__SN_ name="J_PH_COMPACT" pcbX={10} noConnect={["pin1","pin2","pin3","pin4","pin5","pin6"]} />
</board>)
await c.renderUntilSettled()
mkdirSync("artifacts/compact-controller",{recursive:true})
writeFileSync("artifacts/compact-controller/supplier-samples.circuit.json",JSON.stringify(c.getCircuitJson(),null,2)+"\n")
console.log("Native unmodified supplier samples rendered for compact envelope evaluation; not a controller PCB")
