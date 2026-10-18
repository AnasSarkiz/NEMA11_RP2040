import React from "react"
import Controller, { type ControllerProfile } from "../controller/board"
import { compactProfile } from "./board"
import geometry from "../../config/compact-motor-bolts.json"
import placement from "../../config/compact-routing-placement.json"

export const sixLayerProfile:ControllerProfile={...compactProfile,layers:6,
 mounts:geometry.mounts,placementOverrides:placement.placements,buzzerEnabled:false}

// Current controller: actual 23 mm OEM rear case-bolt axes. Hole diameter and
// head envelope are provisional until the rear hardware is measured. Copper
// and placement must be rechecked after this mechanical change.
export default function SixLayerController(){
 return <Controller routingDisabled schematicDisabled profile={sixLayerProfile} />
}
