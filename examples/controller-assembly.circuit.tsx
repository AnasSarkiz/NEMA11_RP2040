import React from "react"
import { assembly } from "tscircuit"
import Controller from "../src/controller/board"

// Real OEM geometry in a proposed clearance position. Retention, carrier,
// harness and fasteners must still be designed; no rear motor holes are inferred.
const revision="e1c16a078dd10286f883a2b9c0775f5d13a366e7"
export default () => <assembly.device name="NEMA11_CONTROLLER_CLEARANCE_REVIEW">
 <Controller routingDisabled schematicDisabled />
 <assembly.part name="OEM_11HS12_0674S"
  displayName="OEM 11HS12-0674S; front mounting carrier and harness required"
  cadModel={{objUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.obj`,
   stepUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.step`,
   modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-42},
   rotationOffset:{x:0,y:0,z:90}}} />
</assembly.device>
