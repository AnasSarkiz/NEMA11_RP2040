import React from "react"
import { CorePart } from "./core-supplier-parts"
import placements from "./core-placements.json"

const n = (name: string) => `net.${name}`
const place = (name: string) =>
  (placements as Record<string, { pcbX: number; pcbY: number; pcbRotation: number }>)[name]

export const mcuPhysicalNets: Record<number, string> = {
  1: "V3V3", 4: "LED_G", 5: "LED_B", 8: "STEP", 9: "DIR", 10: "V3V3",
  11: "ENABLE_N", 12: "SLEEP", 13: "PD_GOOD", 19: "GND", 20: "XIN", 21: "XOUT",
  22: "V3V3", 23: "V1V1", 24: "SWCLK", 25: "SWDIO", 26: "RUN", 27: "BUZZER_PWM",
  33: "V3V3", 37: "LED_R", 38: "TEMP_SDA", 39: "TEMP_SCL", 40: "VM_SENSE",
  41: "DATA_PRESENT", 42: "V3V3", 43: "V3V3", 44: "V3V3", 45: "V1V1",
  46: "MCU_DM", 47: "MCU_DP", 48: "V3V3", 49: "V3V3", 50: "V1V1",
  51: "QSPI_SD3", 52: "QSPI_SCLK", 53: "QSPI_SD0", 54: "QSPI_SD2",
  55: "QSPI_SD1", 56: "QSPI_SS", 57: "GND",
}

const cap = (name: string, rail: string) =>
  <CorePart key={name} name={name} {...place(name)} connections={{ pin1: n(rail), pin2: n("GND") }} />
const resistor = (name: string, a: string, b: string) =>
  <CorePart name={name} {...place(name)} connections={{ pin1: n(a), pin2: n(b) }} />

function DebugPad({ name, net }: { name: string; net: string }) {
  return <testpoint name={name} {...place(name)} layer="top" footprintVariant="pad"
    padDiameter="1.1mm" connections={{ pin1: n(net) }}
    footprint={<footprint><smtpad portHints={["pin1"]} shape="circle" radius={.55} />
      <courtyardoutline outline={[{ x: -.7, y: -.7 }, { x: .7, y: -.7 },
        { x: .7, y: .7 }, { x: -.7, y: .7 }, { x: -.7, y: -.7 }]} /></footprint>} />
}

/** Reusable MCU subsystem. The surrounding controller supplies 3.3 V and I/O nets.
 * GPIO allocation follows the inspected v1.12 reference pending v1.13 comparison.
 * This module does not assert CH224A, board routing or motor attachment readiness.
 */
export function Rp2040Core() {
  const networks = [...new Set([...Object.values(mcuPhysicalNets), "USB_DP", "USB_DM",
    "XTAL_OUT", "BOOT_PAD"])]
  return <>
    {networks.map(name => <React.Fragment key={name}><net name={name} isGroundNet={name === "GND"}
      isPowerNet={["V3V3", "V1V1"].includes(name)} nominalTraceWidth={.16} /></React.Fragment>)}
    <CorePart name="U_MCU" {...place("U_MCU")}
      connections={Object.fromEntries(Object.entries(mcuPhysicalNets).map(([pin, net]) => [`pin${pin}`, n(net)]))}
      noConnect={Array.from({ length: 57 }, (_, i) => i + 1)
        .filter(pin => !(pin in mcuPhysicalNets)).map(pin => `pin${pin}`)} />
    {['C_IO1', 'C_IO10', 'C_IO22', 'C_IO33', 'C_IO42', 'C_IO49', 'C_USB', 'C_ADC']
      .map(name => cap(name, "V3V3"))}
    {['C_DV23', 'C_DV50'].map(name => cap(name, "V1V1"))}
    {cap("C_VREG_IN", "V3V3")}{cap("C_VREG_OUT", "V1V1")}
    <CorePart name="U_FLASH" {...place("U_FLASH")} connections={{
      pin1: n("QSPI_SS"), pin2: n("QSPI_SD1"), pin3: n("QSPI_SD2"), pin4: n("GND"),
      pin5: n("QSPI_SD0"), pin6: n("QSPI_SCLK"), pin7: n("QSPI_SD3"),
      pin8: n("V3V3"), pin9: n("GND"),
    }} />
    {cap("C_FLASH", "V3V3")}
    {resistor("R_FLASH_CS", "V3V3", "QSPI_SS")}
    {resistor("R_BOOT", "QSPI_SS", "BOOT_PAD")}
    <CorePart name="Y_MCU" {...place("Y_MCU")} connections={{
      pin1: n("XIN"), pin2: n("GND"), pin3: n("XTAL_OUT"), pin4: n("GND"),
    }} />
    {resistor("R_XOUT", "XOUT", "XTAL_OUT")}
    {cap("C_XIN", "XIN")}{cap("C_XOUT", "XTAL_OUT")}
    {resistor("R_RUN", "V3V3", "RUN")}
    {resistor("R_DM", "MCU_DM", "USB_DM")}{resistor("R_DP", "MCU_DP", "USB_DP")}
    {Object.entries({ TP_3V3: "V3V3", TP_GND: "GND", TP_SWCLK: "SWCLK",
      TP_SWDIO: "SWDIO", TP_RUN: "RUN", TP_BOOT: "BOOT_PAD", TP_BOOT_GND: "GND" })
      .map(([name, net]) => <DebugPad key={name} name={name} net={net} />)}
  </>
}
