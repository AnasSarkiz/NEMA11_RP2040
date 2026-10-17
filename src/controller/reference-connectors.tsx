import { B4B_PH_K_S_LF__SN_ } from "../../imports/supplier/B4B_PH_K_S_LF__SN_/B4B_PH_K_S_LF__SN_"
import { ABM8_272_T3 } from "../../imports/supplier/ABM8_272_T3/ABM8_272_T3"
import React, { Children, cloneElement, type ReactElement } from "react"
import { USB4145_03_0070_C } from "../../imports/supplier/USB4145_03_0070_C/USB4145_03_0070_C"
import { BM04B_SRSS_TB_LF__SN_ } from "../../imports/supplier/BM04B_SRSS_TB_LF__SN_/BM04B_SRSS_TB_LF__SN_"

// Keep the exact supplier land patterns and CAD. Split common mechanical pads
// into source terminals so every real shell tab/hold-down is checked and routed.
function footprint(element: any, commonPin: string, firstPin: number) {
  let terminal = firstPin
  const fp = element.props.footprint as ReactElement<any>
  const children=Children.toArray(Children.map(fp.props.children, child => {
    const pad = child as ReactElement<any>
    if (!pad.props.portHints?.includes(commonPin)) return pad
    return cloneElement(pad, { portHints: [`pin${terminal++}`] })
  }))
  if(commonPin === "pin17") {
    // GCT USB4145 A2 sheet 2 requires two 0.71 mm locating holes on an
    // 8.00 mm pattern. The original supplier import omitted the right hole.
    // Preserve every imported pad/model and add that verified missing NPTH.
    children.push(cloneElement(<hole pcbX="4.1524872mm"
      pcbY="0.000127mm" diameter="0.7099808mm" />, {key:"manufacturer_right_locator"}))
  }
  return cloneElement(fp, { insertionDirection: "from_above" }, children)
}

const usb = USB4145_03_0070_C({ name: "USB" })
const usbLabels = {...usb.props.pinLabels, pin6:["DM1","DN1","A7"], pin10:["DM2","DN2","B7"], pin17:["EH1","SHELL1"],pin18:["EH2","SHELL2"],pin19:["EH3","SHELL3"],pin20:["EH4","SHELL4"]}
export const StandardUsbConnector = (props:any) => (
 <connector {...USB4145_03_0070_C(props as any).props} standard="usb_c" pinLabels={usbLabels} footprint={footprint(usb,"pin17",17)} {...props} />
)

const motor = BM04B_SRSS_TB_LF__SN_({ name: "MOTOR" })
const motorLabels = {
  pin1: ["A_PLUS"], pin2: ["A_MINUS"], pin3: ["B_PLUS"], pin4: ["B_MINUS"],
  pin5: ["MOUNT1"], pin6: ["MOUNT2"],
}
export const SmtMotorConnector = (props: any) => (
  <connector {...motor.props} standard="jst_sh" pinCount={4} pinLabels={motorLabels}
    footprint={footprint(motor, "pin5", 5)} {...props} />
)

// Genuine PH land pattern/model; logical coil aliases do not change geometry.
export const ThroughHoleMotorConnector = (props:any) => {
 const raw = B4B_PH_K_S_LF__SN_(props)
 return <connector {...raw.props} {...props} standard="jst_ph" pinCount={4}
  footprint={cloneElement(raw.props.footprint as ReactElement<any>,{insertionDirection:"from_above"})}
  pinLabels={{pin1:["A_PLUS"],pin2:["A_MINUS"],pin3:["B_PLUS"],pin4:["B_MINUS"]}} />
}

// The imported four-pad crystal retains its exact footprint and supplier CAD.
// Native crystal classification avoids treating this passive part as a powered IC.
export const SupplierCrystal = (props:any) => {
 const raw = ABM8_272_T3(props)
 const originalSymbol = raw.props.symbol as ReactElement<any>
 const nativeSymbol = cloneElement(originalSymbol, {}, Children.map(originalSymbol.props.children, child => {
  const port = child as ReactElement<any>
  const alias = ({pin1:"X1",pin2:"GND1",pin3:"X2",pin4:"GND2"} as Record<string,string>)[port.props.name]
  return alias ? cloneElement(port, {aliases:[...(port.props.aliases ?? []),alias]}) : port
 }))
 return React.createElement("crystal", {...raw.props, ...props, frequency: 12e6, pinVariant:"four_pin", loadCapacitance: "10pF", symbol:nativeSymbol,
  pinLabels:{pin1:["pin1","X1"],pin2:["GND1","pin2"],pin3:["pin3","X2"],pin4:["GND2","pin4"]},
  pinAttributes:{pin1:{isPassive:true},pin2:{isPassive:true,requiresGround:true},
                 pin3:{isPassive:true},pin4:{isPassive:true,requiresGround:true}}})
}
