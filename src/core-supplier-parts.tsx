import React from "react"
import { RP2040 } from "../imports/supplier/RP2040/RP2040"
import { GD25Q16EEIGR } from "../imports/supplier/GD25Q16EEIGR/GD25Q16EEIGR"
import { ABM8_272_T3 } from "../imports/supplier/ABM8_272_T3/ABM8_272_T3"
import { CL05B104KO5NNNC } from "../imports/supplier/CL05B104KO5NNNC/CL05B104KO5NNNC"
import { CL05A105KA5NQNC } from "../imports/supplier/CL05A105KA5NQNC/CL05A105KA5NQNC"
import { A_0402CG150J500NT } from "../imports/supplier/A_0402CG150J500NT/A_0402CG150J500NT"
import { A_0402WGF1001TCE } from "../imports/supplier/A_0402WGF1001TCE/A_0402WGF1001TCE"
import { A_0402WGF1002TCE } from "../imports/supplier/A_0402WGF1002TCE/A_0402WGF1002TCE"
import { A_0402WGF270JTCE } from "../imports/supplier/A_0402WGF270JTCE/A_0402WGF270JTCE"
import catalog from "./core-supplier-catalog.json"

const parts: Record<string, React.ComponentType<any>> = {
  C2040: RP2040, C2986331: GD25Q16EEIGR, C20625731: ABM8_272_T3,
  C1525: CL05B104KO5NNNC, C52923: CL05A105KA5NQNC,
  C1548: A_0402CG150J500NT, C11702: A_0402WGF1001TCE,
  C25744: A_0402WGF1002TCE, C25100: A_0402WGF270JTCE,
}

/** Preserve the supplier's complete land pattern and model transforms. */
export function CorePart({ name, ...props }: { name: string; [key: string]: any }) {
  if (props.footprint || props.cadModel) throw new Error("Supplier geometry override: " + name)
  const id = (catalog.components as Record<string, string>)[name]
  if (!id || !parts[id]) throw new Error("Missing verified cached import: " + name)
  return React.createElement(parts[id], { name, ...props })
}
