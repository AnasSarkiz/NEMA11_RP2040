import { EEHZC1V680XP } from "../../imports/compact-candidates/EEHZC1V680XP/EEHZC1V680XP"
import { CompactSupplierPart, applyCompactCourtyard } from "./supplier-parts"

/** Next-iteration genuine capacitor; the other supplier parts are unchanged. */
export function HybridBulkSupplierPart(props:any) {
 if(props.name!=="C_BULK")return CompactSupplierPart(props)
 return applyCompactCourtyard(props,EEHZC1V680XP(props))
}
