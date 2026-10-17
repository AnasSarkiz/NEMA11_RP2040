import React from "react"
import { assembly } from "tscircuit"
import Controller from "../src/controller/board"
import { compactProfile } from "../src/compact/board"

// Real OEM geometry and the separately collision-checked original front carrier.
// Fasteners, full harness and purchasing tolerances remain unqualified.
const revision="e1c16a078dd10286f883a2b9c0775f5d13a366e7"
const carrierRevision="ed9fc64663a01454d8a1da2327abef489ce4b6e2"
export default () => <assembly.device name="NEMA11_COMPACT_PLACEMENT_CLEARANCE_REVIEW">
 <Controller routingDisabled schematicDisabled profile={compactProfile} />
 <assembly.part name="OEM_11HS12_0674S"
  displayName="OEM 11HS12-0674S; front mounting only"
  cadModel={{objUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.obj`,
   stepUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${revision}/imports/motor/11HS12-0674S.step`,
   modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-42},
   rotationOffset:{x:0,y:0,z:90}}} />
 <assembly.part name="FRONT_CARRIER_PROPOSAL"
  displayName="Compact front carrier proposal; corner radii/strength/hardware unqualified"
  cadModel={{objUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${carrierRevision}/imports/mechanical/nema11-compact-front-carrier.obj`,
   stepUrl:`https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/${carrierRevision}/imports/mechanical/nema11-compact-front-carrier.step`,
   modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:0},
   rotationOffset:{x:0,y:0,z:0}}} />
</assembly.device>
