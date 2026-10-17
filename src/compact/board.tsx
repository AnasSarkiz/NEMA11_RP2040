import React from "react"
import Nema11Controller, { type ControllerProfile } from "../controller/board"
import { CompactSupplierPart } from "./supplier-parts"
import placements from "./placement.json"

// DEVELOPMENT ONLY. This native full-circuit candidate is unrouted; placement,
// motor-carrier tolerance, assembly and manufacturing gates remain mandatory.
export const compactProfile:ControllerProfile={
 width:28,height:28,outline:[{x:-14,y:-14},{x:14,y:-14},{x:14,y:14},{x:-14,y:14}],
 mounts:[{x:-12.5,y:12.5,diameter:1.8,radius:1.6},{x:12.5,y:12.5,diameter:1.8,radius:1.6}],
 placementOverrides:placements,Part:CompactSupplierPart,compactLabels:true,
}
export default function CompactController() {
 return <Nema11Controller routingDisabled profile={compactProfile} />
}
