import React from "react"
const objPath = "https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/main/imports/supplier/HP05W3F240LT5E/HP05W3F240LT5E.obj"
const stepPath = "https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/main/imports/supplier/HP05W3F240LT5E/HP05W3F240LT5E.step"
import type { ResistorProps } from "@tscircuit/props"

export const HP05W3F240LT5E = (props: Omit<ResistorProps, "resistance">) => {
  const { name = "R1", ...restProps } = props

  return (
    <resistor
      name={name}
      resistance="240mohm"
      supplierPartNumbers={{
  "jlcpcb": [
    "C7434086"
  ]
}}
      manufacturerPartNumber="HP05W3F240LT5E"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="0.999998mm" pcbY="0mm" width="1.1325352mm" height="1.3770102mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-0.999998mm" pcbY="0mm" width="1.1325352mm" height="1.3770102mm" shape="rect" />
<silkscreenpath route={[{"x":0.4761991999999964,"y":-0.9170924000000014},{"x":1.7611343999999463,"y":-0.9170924000000014},{"x":1.7611343999999463,"y":0.9170924000000014},{"x":0.4761991999999964,"y":0.9170924000000014}]} />
<silkscreenpath route={[{"x":-0.47619920000011007,"y":-0.9170924000000014},{"x":-1.7611343999999463,"y":-0.9170924000000014},{"x":-1.7611343999999463,"y":0.9170924000000014},{"x":-0.47619920000011007,"y":0.9170924000000014}]} />
<silkscreentext text="{NAME}" pcbX="0.0127mm" pcbY="1.9144mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.8162655999998378,"y":0.9385051000000431},{"x":1.8162655999998378,"y":0.9385051000000431},{"x":1.8162655999998378,"y":-0.9385051000000431},{"x":-1.8162655999998378,"y":-0.9385051000000431},{"x":-1.8162655999998378,"y":0.9385051000000431}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0.000012699999842880061, z: 0 },
      }}
      {...restProps}
    />
  )
}