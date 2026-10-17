import React from "react"
import Controller from "../src/controller/board"

// Electrical checks do not need temporary automatic schematic wire routing.
export default () => <Controller routingDisabled schematicDisabled />
