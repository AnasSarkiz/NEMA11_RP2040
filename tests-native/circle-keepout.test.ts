import { describe, expect, test } from "bun:test"
import { checkEachPcbTraceNonOverlapping } from "@tscircuit/checks"

function inspect({ start = [.9, .9], end = [1.2, .9], width = .1,
  center = [0, 0], radius = 1, shape = "circle", traceLayer = "top",
  keepoutLayer = "top", warningOnly = false } = {}) {
  const records: any[] = [
    { type: "pcb_board", pcb_board_id: "board", center: { x: 0, y: 0 }, width: 40, height: 40,
      min_trace_to_pad_edge_clearance: .15 },
    { type: "pcb_keepout", pcb_keepout_id: "keepout", shape,
      center: { x: center[0], y: center[1] }, radius, width: radius * 2, height: radius * 2,
      layers: [keepoutLayer], warning_only: warningOnly },
    { type: "pcb_trace", pcb_trace_id: "trace", source_trace_id: "source_trace", route: [
      { route_type: "wire", x: start[0], y: start[1], width, layer: traceLayer },
      { route_type: "wire", x: end[0], y: end[1], width, layer: traceLayer },
    ] },
  ]
  return checkEachPcbTraceNonOverlapping(records)
}

describe("native trace versus true circular keepout", () => {
  test("clears a circle while inside its bounding rectangle", () => {
    expect(inspect()).toHaveLength(0)
  })
  test("uses translated center and radius", () => {
    expect(inspect({ start: [15.5, -10.5], end: [16, -10.5], center: [13, -13], radius: 3.2 })).toHaveLength(0)
  })
  test("finite segment uses its closest endpoint, not the infinite line", () => {
    expect(inspect({ start: [1.05, 1.05], end: [2, 2] })).toHaveLength(0)
  })
  test("detects a center-crossing trace", () => {
    expect(inspect({ start: [-2, 0], end: [2, 0] }).some(e => e.type.endsWith("_error"))).toBe(true)
  })
  test("detects a trace inside the circle", () => {
    expect(inspect({ start: [.3, .3], end: [.6, .3] }).some(e => e.type.endsWith("_error"))).toBe(true)
  })
  test("enforces the 0.15 mm edge clearance", () => {
    expect(inspect({ start: [1.15, -.2], end: [1.15, .2] }).some(e => e.type.endsWith("_error"))).toBe(true)
  })
  test("includes half the full trace width", () => {
    expect(inspect({ start: [1.3, -.2], end: [1.3, .2], width: .4 }).some(e => e.type.endsWith("_error"))).toBe(true)
  })
  test("a rectangle still blocks its corner", () => {
    expect(inspect({ shape: "rect" }).some(e => e.type.endsWith("_error"))).toBe(true)
  })
  test("respects the keepout layer", () => {
    expect(inspect({ start: [-2, 0], end: [2, 0], traceLayer: "bottom" })).toHaveLength(0)
  })
  test("advisory violations remain visible warnings", () => {
    expect(inspect({ start: [-2, 0], end: [2, 0], warningOnly: true })[0]?.type).toBe("pcb_keepout_overlap_warning")
  })
})
