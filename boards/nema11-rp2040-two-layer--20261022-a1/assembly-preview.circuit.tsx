import { assembly } from "tscircuit";
import Controller from "./index.circuit";
import mechanical from "./config/motor-assembly.json";
import motorObj from "./references/motor-assets/11HS12-0674S.obj";
import motorStep from "./references/motor-assets/11HS12-0674S.step";

// OEM motor is unchanged. Z translates its rear maximum (31.5 mm) to
// -10.8 mm, 10 mm below the PCB bottom (-0.8 mm). This is an EXPLODED
// inspection gap, NOT a spacer specification or an assembled mounting stack.
// Original OEM recessed heads remain visible; no replacement bolts, threads,
// carrier, rear shaft, or connected harness are invented.
export default function Nema11ExplodedAssemblyReview() {
  return (
    <assembly.device name="NEMA11_EXPLODED_REVIEW_NOT_QUALIFIED_FOR_ASSEMBLY">
      <Controller />
      <assembly.part
        name="OEM_11HS12_0674S_EXPLODED_REFERENCE"
        displayName="OEM 11HS12-0674S; 10mm exploded review gap; rear hardware and insulation unqualified"
        cadModel={{
          objUrl: motorObj,
          stepUrl: motorStep,
          modelOriginPosition: { x: 0, y: 0, z: 0 },
          positionOffset: mechanical.motor_translation_mm,
          rotationOffset: mechanical.motor_rotation_deg,
        }}
      />
    </assembly.device>
  );
}
