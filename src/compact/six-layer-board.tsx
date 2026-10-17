import React from "react"
import Controller, { type ControllerProfile } from "../controller/board"
import { compactProfile } from "./board"
import geometry from "../../config/compact-four-mounts.json"
import placement from "../../config/compact-routing-placement.json"

export const sixLayerProfile:ControllerProfile={...compactProfile,layers:6,
 mounts:geometry.mounts,placementOverrides:placement.placements,buzzerEnabled:false}

// Native source for rebuilding the checked routing placement. The fixed copper
// construction is in six-layer-routing.json; this source alone is unrouted.
export default function SixLayerController(){
 return <Controller routingDisabled schematicDisabled profile={sixLayerProfile} />
}
