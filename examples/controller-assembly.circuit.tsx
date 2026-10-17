import React from "react"
import { assembly } from "tscircuit"
import Controller from "../src/controller/board"

// Real OEM geometry and the separately collision-checked original front carrier.
// Fasteners, full harness and purchasing tolerances remain unqualified.
const revision="e1c16a078dd10286f883a2b9c0775f5d13a366e7"
const carrierRevision="11fa1a152c52dcea39f67a157485aba4e8d552db"
export default () => <assembly.device name="NEMA11_CONTROLLER_CLEARANCE_REVIEW">
 <Controller routingDisabled schematicDisabled />
 <assembly.part name="OEM_11HS12_0674S"
  displayName="OEM 11HS12-0674S; front mounting only"
  cadModel={{objUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.obj`,
   stepUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.step`,
   modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-42},
   rotationOffset:{x:0,y:0,z:90}}} />
 <assembly.part name="FRONT_CARRIER_PROPOSAL"
  displayName="Original front carrier proposal; machining and hardware not released"
  cadModel={{objUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${carrierRevision}/imports/mechanical/nema11-front-carrier.obj`,
   stepUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${carrierRevision}/imports/mechanical/nema11-front-carrier.step`,
   modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:0},
   rotationOffset:{x:0,y:0,z:0}}} />
</assembly.device>
