import React from "react"
import { Rp2040Core } from "../src/rp2040-core"

/** Source/3D development canvas only. Not the final NEMA11 outline or layout. */
export default function Rp2040CoreExample() {
  return <board width={35} height={35} layers={4} thickness={1.6}
    routingDisabled minViaHoleDiameter={.30} minViaPadDiameter={.45}
    minTraceWidth={.16} minBoardEdgeClearance={.25}>
    <Rp2040Core />
  </board>
}
