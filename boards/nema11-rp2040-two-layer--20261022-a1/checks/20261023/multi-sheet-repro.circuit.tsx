import { A_0402WGF1000TCE } from "../../imports/A_0402WGF1000TCE/A_0402WGF1000TCE";
export default function MultiSheetReproduction() {
  return (
    <board width={12} height={8} layers={2} routingDisabled={true}>
      <net name="TEST" />
      <net name="GND" isGroundNet />
      <schematicsheet name="First A4" sheetSize="A4" sheetIndex={0}>
        <A_0402WGF1000TCE
          name="R_FIRST"
          pcbX={-3}
          schX={0}
          schY={0}
          connections={{ pin1: "net.TEST", pin2: "net.GND" }}
        />
      </schematicsheet>
      <schematicsheet name="Second A4" sheetSize="A4" sheetIndex={1}>
        <A_0402WGF1000TCE
          name="R_SECOND"
          pcbX={3}
          schX={0}
          schY={0}
          connections={{ pin1: "net.TEST", pin2: "net.GND" }}
        />
      </schematicsheet>
    </board>
  );
}
