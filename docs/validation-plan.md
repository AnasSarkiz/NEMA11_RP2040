# Validation and release gates

Every receipt must identify the actual source/board hash, command, exit code,
log and current-run output. Preserve warnings, failures and skipped/unrun checks.
Do not reuse inherited reference passes after changing geometry or electrical
values. A source import or a zero-test result does not validate a board.

| Gate | Required evidence | Current status |
|---|---|---|
| Baseline | Exact public v1.13.0 release ID, source files and hashes | Blocked by registry network policy |
| Motor | Original PDF/STEP hashes, drawing review, measured STEP bounds and lead exit | Blocked by motor host network policy |
| Feature parity | Reference-to-NEMA11 physical pins, nets, values and DNP matrix | Not run; exact baseline missing |
| Electrical | Actual driver current bounds, shunt derating, hot losses, power/ADC/PG review | Preliminary conditional calculation only |
| Source | Frozen dependency install, TypeScript, native source/netlist/pin checks | NEMA11 MCU subsystem render, strict schema, physical-pin contract and 10 tests pass; full controller pending |
| Schematic | Function groups, connected symbol pins, net labels, ERC and inspected A4 PDF | Not run; no NEMA11 schematic |
| PCB | DRC, all intended physical nets, pad identity and no unintended copper | Not run; no NEMA11 PCB |
| Layout | Short top-layer crystal signals, ground return/reference, decoupling, thermal and every-trace widths | Not run |
| Fabrication | Actual ≥0.30 mm via drills, ≥0.45 mm pads, copper/mask/drill/edge clearances | Not run |
| CAM | Independent opens/shorts/islands, outline/drills, source-to-Gerber and layer order | Not run; no Gerbers |
| PCBA | Exact MPN/JLC codes, fitted/DNP policy, BOM/CPL datum/polarity/rotation and stencil | Not run; no manufacturing BOM/CPL |
| Mechanical | Native tscircuit assembly with genuine supplier models and original motor STEP | Not run |
| Harness | Mating part, contacts, wire/termination, coil order, JST-edge routing and strain relief | Not run |
| Attachment | Real mounting method, fasteners/thread engagement, insertion/tool and dynamic clearances | Not run |
| Publication | Separate prototype package, immutable source provenance and downloaded artifact verification | Blocked by registry access and missing tscircuit authentication |

## Milestones

1. Requirements, observed reference identity, conditional current/thermal
   calculation and executable calculation tests. Commit and push this completed
   milestone with the unresolved inputs explicit.
2. Retrieve exact baseline and motor evidence; commit the full feature matrix,
   verified supplier imports and attachment/placement decision.
3. Commit the connected schematic, A4 PDF, native circuit source and reviewed
   current/thermal values after source/ERC checks.
   The independent RP2040 subsystem source milestone is now implemented;
   its scope and outstanding full-controller checks are documented separately.
4. Commit routed PCB, native assembly, exact BOM/CPL/Gerbers and full current
   check receipts after routing/CAM/assembly review. Publish only the qualified
   prototype content to the separate NEMA11 tscircuit package.

Bench operation remains distinct from CAD qualification: USB programming/data
in both orientations, 15 V negotiation/fallback and host isolation, PG/ADC
gating, all accessories, both coil currents, disabled/reset behavior,
temperature/ripple/regeneration and actual harness/fastener fit require physical
prototype tests. Confirm stock, assembly-process acceptance and unresolved
manufacturing requirements before placing an order. No order is authorized here.
