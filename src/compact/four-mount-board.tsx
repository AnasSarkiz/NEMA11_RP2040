import React from "react"
import Controller, { type ControllerProfile } from "../controller/board"
import { compactProfile } from "./board"
import geometry from "../../config/compact-four-mounts.json"
import placements from "./four-mount-placement.json"

// Four-corner PCB interface to a separate front-anchored carrier proposal.
// These holes are not motor rear threads. Routing and hardware are unqualified.
export const fourMountProfile:ControllerProfile={
 ...compactProfile,mounts:geometry.mounts,placementOverrides:placements,buzzerEnabled:false,
}
export default function FourMountController(){
 return <Controller routingDisabled schematicDisabled profile={fourMountProfile} />
}
