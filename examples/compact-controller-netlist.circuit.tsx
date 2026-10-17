import React from "react"
import Controller from "../src/controller/board"
import { compactProfile } from "../src/compact/board"
export default () => <Controller routingDisabled schematicDisabled profile={compactProfile} />
