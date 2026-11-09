import objPath from "./CH224Q.obj"
import stepPath from "./CH224Q.step"
import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["VHV"],
  pin2: ["CFG2","SCL"],
  pin3: ["CFG3","SDA"],
  pin4: ["DP"],
  pin5: ["DM"],
  pin6: ["CC2"],
  pin7: ["CC1"],
  pin8: ["VBUS"],
  pin9: ["CFG1"],
  pin10: ["PG"],
  pin11: ["EP"]
} as const

const pinAttributes = {
  pin8: {requiresPower: true}
} as const

export const CH224Q = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C46061833"
  ]
}}
      manufacturerPartNumber="CH224Q"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.7999984mm" pcbY="-0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-0.3999992mm" pcbY="-0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="0mm" pcbY="-0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="0.3999992mm" pcbY="-0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="0.7999984mm" pcbY="-0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="0.7999984mm" pcbY="0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="0.3999992mm" pcbY="0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin8"]} pcbX="0mm" pcbY="0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin9"]} pcbX="-0.3999992mm" pcbY="0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin10"]} pcbX="-0.7999984mm" pcbY="0.9275064mm" width="0.2240026mm" height="0.5050028mm" shape="rect" />
<smtpad portHints={["pin11"]} pcbX="0mm" pcbY="0mm" width="1.3999972mm" height="0.8999982mm" shape="rect" />
<silkscreenpath route={[{"x":-1.0761979999999767,"y":-1.0761979999999767},{"x":-1.0761979999999767,"y":1.0761980000000904}]} />
<silkscreenpath route={[{"x":1.0761979999999767,"y":-1.0761979999999767},{"x":1.0761979999999767,"y":1.0761980000000904}]} />
<silkscreencircle pcbX="-0.7999984mm" pcbY="-1.4800072mm" radius="0.0750062mm" />
<silkscreentext text="{NAME}" pcbX="-0.0889mm" pcbY="2.1938mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.249998000000005,"y":1.4300078000001122},{"x":1.2499979999998914,"y":1.4300078000001122},{"x":1.2499979999998914,"y":-1.4300078000001122},{"x":-1.249998000000005,"y":-1.4300078000001122},{"x":-1.249998000000005,"y":1.4300078000001122}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -0.000012700000070253736, z: 0 },
      }}
      {...props}
    />
  )
}