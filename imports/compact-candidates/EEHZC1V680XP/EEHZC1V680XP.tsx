import React from "react"
const objPath = "https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/007e0f41fcd5a649d8b2f1a12c8c5f2f16f67c10/imports/compact-candidates/EEHZC1V680XP/EEHZC1V680XP.board-frame.obj"
const stepPath = "https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/007e0f41fcd5a649d8b2f1a12c8c5f2f16f67c10/imports/compact-candidates/EEHZC1V680XP/EEHZC1V680XP.board-frame.step"
import type { CapacitorProps } from "@tscircuit/props"

export const EEHZC1V680XP = (props: Omit<CapacitorProps, "capacitance">) => {
  const { name = "C1", ...restProps } = props

  return (
    <capacitor
      name={name}
      capacitance="68uF"
      polarized
      supplierPartNumbers={{
  "jlcpcb": [
    "C178649"
  ]
}}
      manufacturerPartNumber="EEHZC1V680XP"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="2.669921mm" pcbY="0mm" width="3.499993mm" height="1.1999976mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-2.669921mm" pcbY="0mm" width="3.499993mm" height="1.1999976mm" shape="rect" />
<silkscreenpath route={[{"x":3.3555939999998827,"y":-0.7393431999997802},{"x":3.375634600000012,"y":-3.375736199999892},{"x":-1.9812254000000848,"y":-3.375736199999892},{"x":-3.375685400000066,"y":-1.9812762000000248},{"x":-3.3623250000000553,"y":-0.6858761999999388}]} />
<silkscreenpath route={[{"x":3.369462399999861,"y":0.7076186000001599},{"x":3.37614259999998,"y":3.376091800000154},{"x":-1.980056999999988,"y":3.376091800000154},{"x":-3.3761934000000338,"y":1.9799554000002217},{"x":-3.3761934000000338,"y":0.6857238000000052}]} />
<silkscreentext text="{NAME}" pcbX="-0.010033mm" pcbY="4.375914mm" anchorAlignment="center" fontSize="1mm" />
<fabricationnotepath route={[{"x":-2.8050236000001405,"y":0.659917400000154},{"x":-2.8050236000001405,"y":-0.6600697999998602},{"x":-2.60703060000003,"y":-0.6600697999998602},{"x":-2.60703060000003,"y":0.659917400000154},{"x":-2.8050236000001405,"y":0.659917400000154}]} strokeWidth="0.254mm" />
<fabricationnotepath route={[{"x":-3.102025800000206,"y":0.09893300000010186},{"x":-3.102025800000206,"y":-0.09908539999980803},{"x":-2.3100284000000784,"y":-0.09908539999980803},{"x":-2.3100284000000784,"y":0.09893300000010186},{"x":-3.102025800000206,"y":0.09893300000010186}]} strokeWidth="0.254mm" />
<fabricationnotepath route={[{"x":3.101974999999811,"y":0.09893300000010186},{"x":3.101974999999811,"y":-0.09908539999980803},{"x":2.309977599999911,"y":-0.09908539999980803},{"x":2.309977599999911,"y":0.09893300000010186},{"x":3.101974999999811,"y":0.09893300000010186}]} strokeWidth="0.254mm" />
<courtyardoutline outline={[{"x":-4.669917499999997,"y":3.5499172000000954},{"x":4.669917499999997,"y":3.5499172000000954},{"x":4.669917499999997,"y":-3.5500695999998015},{"x":-4.669917499999997,"y":-3.5500695999998015},{"x":-4.669917499999997,"y":3.5499172000000954}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: 0 },
      }}
      {...restProps}
    />
  )
}
