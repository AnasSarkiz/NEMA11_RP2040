import React from "react"
import notes from "./schematic-notes.json"

export const SchematicNotes = () => <>
  <schematictext text="NEMA11_RP2040 - USB-C NEMA11 MOTOR CONTROLLER" schX={-15} schY={10.35} fontSize={0.3} anchor="top_left" />
  <schematictext text="COMPONENT PURPOSE" schX={8} schY={9.3} fontSize={0.28} anchor="top_left" />
  {notes.map(([title, purpose], i) => <React.Fragment key={title}>
    <schematictext text={title} schX={8} schY={8.6-i*2.35} fontSize={0.23} anchor="top_left" />
    <schematictext text={purpose} schX={8} schY={8.2-i*2.35} fontSize={0.19} anchor="top_left" />
  </React.Fragment>)}
  <schematictext text="PD PORT: motor power, 15 V requested. DATA PORT: USB computer control.\nMotor: 11HS12-0674S, bipolar, 0.67 A/phase. Prototype: current/thermal and front-anchored adapter validation pending."
    schX={-15} schY={-9.45} fontSize={0.19} anchor="top_left" />
</>
