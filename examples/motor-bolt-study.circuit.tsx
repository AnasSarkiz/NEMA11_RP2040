import React from "react"
import { assembly } from "tscircuit"

// Original OEM model only. No carrier, invented rear holes, replacement bolts
// or PCB-to-motor attachment is represented by this mechanical study.
const revision="e1c16a078dd10286f883a2b9c0775f5d13a366e7"
export default () => <assembly.device name="NEMA11_EXISTING_MOTOR_BOLT_STUDY">
 <assembly.part name="OEM_11HS12_0674S"
  displayName="OEM motor; four rear bolt axes at 23 mm nominal; bolt specifications pending"
  cadModel={{objUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.obj`,
   stepUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.step`,
   modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:0},
   rotationOffset:{x:0,y:0,z:0}}} />
</assembly.device>
