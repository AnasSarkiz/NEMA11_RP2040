import React, { Children, cloneElement, type ReactElement } from "react"
import { SupplierPart } from "../controller/supplier-parts"
import { MLT_5020 } from "../../imports/compact-candidates/MLT_5020/MLT_5020"
import courtyards from "./construction-courtyards.json"

/** Compact construction courtyards; original copper/silk/holes/models are preserved.
 * Pair-specific component spacing and dimensional tolerances need separate checks.
 * Original native imports and original authored courtyards remain in imports/.
 */
export function CompactSupplierPart(props:any) {
 let element:ReactElement<any> = props.name === "BZ1"
  ? MLT_5020({...props,noConnect:["NC"],pinAttributes:{...props.pinAttributes,pin3:{doNotConnect:true}}})
  : SupplierPart(props)
 return applyCompactCourtyard(props,element)
}

export function applyCompactCourtyard(props:any,element:ReactElement<any>) {
 while(typeof element.type === "function") element=(element.type as any)(element.props)
 const b=(courtyards as Record<string,number[]>)[props.name]
 if(!b) return element // The three documented bottom-side DNP encoder parts.
 const fp=element.props.footprint as ReactElement<any>
 if(!fp || fp.type !== "footprint")throw new Error("Missing native footprint: "+props.name)
 const children=Children.toArray(fp.props.children).filter(c=>(c as ReactElement<any>).type !== "courtyardoutline")
 const [x0,y0,x1,y1]=b
 children.push(cloneElement(<courtyardoutline outline={[{x:x0,y:y0},{x:x1,y:y0},{x:x1,y:y1},{x:x0,y:y1},{x:x0,y:y0}]} />,{key:"compact_construction_courtyard"}))
 return cloneElement(element,{footprint:cloneElement(fp,{},children)})
}
