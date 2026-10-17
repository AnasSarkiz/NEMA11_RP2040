# Compact routing construction

The published four-hole prototype 0.3.0 remains the checked **unrouted** source,
A4 schematic and native 3D checkpoint. Routing candidates are development work;
they are not manufacturing files and their global DRC/connectivity failures
remain visible. The active six-layer experiment retains the 28 mm outline,
four Ø1.8 mm holes at 25 mm pitch, 76 fitted parts on top and all remaining
reference features. The complete buzzer circuit is the user-authorized omission.

Native source for the current routing placement can be reproduced separately:

```sh
bun scripts/build-controller.tsx --compact --four-mounts --no-buzzer --layers 6 \
  --placement config/compact-routing-placement.json --out /tmp/nema11-routing
python3 scripts/verify_controller.py --compact --no-buzzer --folder /tmp/nema11-routing
python scripts/audit_compact_placement.py --folder /tmp/nema11-routing \
  --placement config/compact-routing-placement.json --USB-escape \
  --extra-constraints config/compact-four-mount-routing-constraints.json
```

The added C_REF proximity constraint places the current-reference filter at
the driver input. The encoder stays on the motor axis; its two DNP capacitors
are repositioned to free MCU escapes. Supplier lands, symbols and component
models retain their original geometry. This is nominal placement validation,
not manufacturer tolerance or mechanical-carrier qualification.

The routing constructors retain **0.30 mm drills and at least 0.45 mm pads**.
Inner1 remains the clock ground reference. Crystal signals stay on top without
signal vias; the short MCU-to-USB-resistor nets also retain their direct top
connections. The explicit MCU pin-13 construction path is continuously checked
against real copper, drill openings, board edge and the clock guard. It changes
no physical clearance rule. Construction-grid margins are not DRC clearances.

Selected terminal escapes require the already specified **IPC-4761 Type VII
filled and copper-capped process**, on via drills only. Their top/bottom tenting
preserves the original terminal mask and paste apertures. The process-policy
script binds an explicit list of affected vias and their same-net owner lands
to the exact board hash. Native DRC still checks every barrel for clearance,
shorts and connectivity; ordinary vias remain prohibited in component lands.
Published JLC capability is not factory acceptance of this board.

Physical geometry checks derive all layers from the native board stack. Tests
cover continuity and foreign-net shorts on inner3/inner4, omitted through-barrel
layers, and copper on undeclared layers. NPTH checks separately enforce via
**annulus** clearance, even when the drill-to-drill web already passes. Retrying
a net allocates fresh trace IDs rather than duplicating an earlier route.

[Tool validation](../artifacts/requirements/routing-tool-validation.json) records
24 source tests, 29 physical fault tests, exact four-layer baseline reproduction
and its unchanged zero-error copper/connectivity/native results. These baseline
results do not qualify the compact routing experiment. Complete native DRC,
all-pin connectivity, USB/clock review, CAM and assembly checks are required
before a new routed design is published or manufacturing files are released.
