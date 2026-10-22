// Diagnostic fixture using the untouched latest supported C5815189 import.
import { USB4145_03_0070_C } from "../../imports/USB4145_03_0070_C/USB4145_03_0070_C";
export default function UsbImportReview() {
  return (
    <board
      width={14}
      height={8}
      layers={2}
      routingDisabled={true}
      minViaHoleDiameter={0.3}
      minViaPadDiameter={0.45}
    >
      <schematicsheet name="USB import review" sheetSize="A4">
        <USB4145_03_0070_C name="J1" />
      </schematicsheet>
    </board>
  );
}
