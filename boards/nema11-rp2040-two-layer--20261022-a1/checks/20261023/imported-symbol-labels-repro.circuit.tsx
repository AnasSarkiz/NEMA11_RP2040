import { TMP102AIDRLR } from "../../imports/TMP102AIDRLR/TMP102AIDRLR";
import { LTST_C19HE1WT } from "../../imports/LTST_C19HE1WT/LTST_C19HE1WT";
export default function ImportedSymbolLabels() {
  return (
    <board
      width={18}
      height={10}
      layers={2}
      routingDisabled={true}
      schAutoLayoutEnabled={false}
    >
      <net name="DATA_VBUS" />
      <net name="GND" isGroundNet />
      <net name="STATUS_B_K" />
      <net name="STATUS_G_K" />
      <net name="STATUS_R_K" />
      <net name="TEMP_SCL" />
      <net name="TEMP_SDA" />
      <net name="V3V3" isPowerNet />
      <schematicsheet name="Untouched imported symbols" sheetSize="A4">
        <TMP102AIDRLR
          name="U_TEMP"
          pcbX={-4}
          schX={-4}
          schY={0}
          connections={{
            pin1: "net.TEMP_SCL",
            pin2: "net.GND",
            pin4: "net.GND",
            pin5: "net.V3V3",
            pin6: "net.TEMP_SDA",
          }}
          noConnect={["pin3"]}
        />
        <LTST_C19HE1WT
          name="D_STATUS"
          pcbX={4}
          schX={4}
          schY={0}
          connections={{
            pin1: "net.STATUS_R_K",
            pin2: "net.STATUS_G_K",
            pin3: "net.STATUS_B_K",
            pin4: "net.DATA_VBUS",
          }}
          noConnect={[]}
        />
      </schematicsheet>
    </board>
  );
}
