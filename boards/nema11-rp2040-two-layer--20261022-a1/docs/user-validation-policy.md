# tscircuit store board workspace

## Purpose and task isolation

This workspace is for designing and validating boards for the existing tscircuit
store. Work on board designs; do not rebuild the store application unless asked.

- Every new task/thread must work in a separate directory under
  `boards/<board-slug>--<unique-task-id>/`. Choose a descriptive lowercase,
  hyphenated board name and a unique task suffix before creating files.
- Follow-up messages in the same task continue in that task's directory. A new
  task continuing an existing board must use its own directory and record the
  source board directory and revision it started from.
- Keep each task's circuit sources, components, dependencies, configuration,
  tests, snapshots, build output and fabrication files inside its directory.
  Run board commands from that directory, never from the workspace root.
- Do not modify another task's directory or overwrite its generated files.
  Change shared workspace instructions only when the task calls for it.
- Use `index.circuit.tsx` as the board entry point. Keep a board `README.md` for
  usage and a `VALIDATION.md` for requirements, evidence and stage status.

## Publish every implementation step and version

- After every completed board implementation step and every new board version,
  commit the task's changes, push them to its configured GitHub repository and
  branch, and publish the same board revision to its configured tscircuit
  package using the supported publishing workflow.
- This is standing user authorization for these GitHub pushes and tscircuit
  publications. Do not request permission again for each step or version.
- Every board's GitHub repository and tscircuit package must be **public**.
  Create new board repositories and packages with public visibility. For an
  existing destination dedicated to the board, this is standing authorization
  to make it public; do not change the visibility of unrelated repositories or
  packages.
- Before publishing, run the checks applicable to the current implementation
  stage and record their results. Intermediate revisions must be labeled as
  work-in-progress prototypes, with unfinished stages and limitations clearly
  documented. Publication does not mean fabrication approval or hardware testing.
  Do not enable routing early, bypass checks or hide failures to publish a step.
- Give each implementation step a descriptive commit message and record the
  board revision and completed step in `VALIDATION.md`. Keep the GitHub source
  and tscircuit package contents consistent; do not publish unrelated task files
  or credentials.
- Include the generated circuit JSON in every published build. Rebuild it from
  the same source revision being published, commit and push
  `dist/index/circuit.json` to GitHub, and include the corresponding circuit JSON
  in the tscircuit package build through the supported publishing workflow.
  If the toolchain uses a different output path, record and use that actual path.
  Ensure ignore rules do not exclude this required artifact. Never hand-edit
  circuit JSON or publish stale output; preserve the routing state required by
  the current validation stage.
- Verify both remote updates succeeded and report the GitHub commit link and
  tscircuit package link, including the published version or revision identifier
  when available. Verify that both destinations are public and accessible
  without signing in. Record visibility verification in `VALIDATION.md`.
  Verify that both published builds contain the circuit JSON matching the
  validated local build; missing or mismatched circuit JSON is a blocking issue.
  A local commit or a private publication does not complete this requirement.
- If the destination repository, branch or package is unknown, or validation,
  authentication, pushing, publishing or public-visibility verification fails,
  report a **blocking issue** with
  the exact missing information or failure. State which remote updates succeeded
  if only one succeeded; do not claim the step is fully published.
- This authorization covers board pushes and package publications; merging pull
  requests and placing fabrication orders require their own user authorization.

## Mandatory JLCPCB component imports

**NOTE: Never use custom components or create component definitions. All
electronic components must be imported from JLCPCB.**

- Use the supported JLCPCB import workflow and record each component's exact
  JLCPCB/LCSC part number.
- Do not hand-create, recreate or manually patch component symbols, footprints,
  pin mappings or imported component definitions. Do not replace a failed import
  with a generic component, placeholder or locally authored substitute.
- If a required part cannot be imported, or an imported component has any issue,
  report it to the user explicitly as a **blocking issue**. Include the part
  number, the error or discrepancy, and the affected validation stage. Record
  the blocker in `VALIDATION.md` and stop dependent work; do not work around it
  by creating or modifying a component.
- Board structure, wiring, schematic sheets and PCB features such as mounting
  holes remain native tscircuit elements; they are not purchased components.

## Schematic sheets and sections

- Every board must use native tscircuit schematic sheets in A4 format.
- Use schematic sections only when a sheet is complicated and grouping related
  circuitry into labeled functional blocks improves readability. Simple sheets
  should remain without sections.
- Keep symbols, wiring, labels and sheet information readable within the A4
  boundary. Use additional A4 sheets when needed rather than crowding a sheet.
- Verify the supported sheet and section APIs in the installed tscircuit
  version, and inspect the rendered sheets during schematic validation.

## Validation record and gates

Validate every new board through the stages below, in order. Record each stage
as `not started`, `in progress`, `blocked` or `passed` in the board's
`VALIDATION.md`. Include the board revision, source commit when available,
dependency and CLI versions, commands and results, reviewed artifact paths,
datasheet references, accepted warnings and unresolved issues. If Git is not
available, preserve a versioned source and dependency manifest with checksums
so that evidence identifies the exact design that was checked.

Do not mark a check as passed without running it or a visual review as complete
without inspecting the output. Missing requirements, unavailable checks and
unperformed physical tests must remain explicit. Resolve blockers before
claiming the corresponding stage is complete.

Use the board project's configured formatting, TypeScript and test commands.
Verify CLI support using the installed version's help or official source. The
commands below are required checks; if one is unavailable or incompatible,
record the blocker and resolve the tooling issue instead of silently skipping
it, substituting a weaker check or claiming success.

### 1. Confirm requirements

Record the intended function, supply voltage, current limits, interfaces, board
dimensions, mounting arrangement, layer count and target manufacturer's
capabilities. Include the applicable trace width, clearance, drill, via and
stackup limits. Identify assumptions and resolve design-critical unknowns
before relying on them.

### 2. Review the schematic and BOM

Verify connections against manufacturer datasheets: pin numbers, power rails,
component values, protection, decoupling, startup states and unused pins.
Verify exact part numbers, packages, footprints, polarity and supplier
availability. Record datasheet links and the date of availability checks.

### 3. Validate placement before routing

Keep routing disabled until connectivity, BOM and placement are checked. Use
the installed tscircuit version's supported routing controls and verify that
the placement output is unrouted.

Inspect component bodies, courtyards, connector access, test-point access,
mounting clearances and mechanical fit.

Run from the task's board directory:

```sh
tsci check netlist index.circuit.tsx
tsci check pin_specification index.circuit.tsx
tsci check source index.circuit.tsx
tsci check schematic-placement index.circuit.tsx
tsci check placement index.circuit.tsx
```

Resolve connectivity, BOM and placement issues before enabling routing.

### 4. Route and validate the generated copper

Enable native routing, build the board and verify:

- Every required connection is physically routed.
- There are no shorts, disconnected segments or copper crossing keepouts.
- Actual trace widths, clearances, via dimensions and layer spans meet the
  recorded requirements.
- Power paths and their narrow sections support the intended current.
- Ordinary drills clear component and test pads, including same-net cases.
- Intentional thermal vias or other exceptions are explicitly identified and
  reviewed.

Inspect generated geometry; configuration values alone do not prove compliance.
Record measured dimensions and the basis for current-carrying limits for
critical paths.

### 5. Run automated and visual checks

Run formatting, TypeScript checks and meaningful board tests. Check the routed
output:

```sh
tsci build index.circuit.tsx --pcb-png --pcb-svgs --schematic-svgs
tsci check shorts dist/index/circuit.json
tsci snapshot index.circuit.tsx
```

Confirm that the output being checked was generated from the current source
revision with routing enabled. Inspect the schematic, each copper layer and
detailed views of critical areas. Review snapshot changes before accepting them.

Require zero unresolved errors. Fix actionable warnings; document the reason
for accepting any remaining warning. Do not hide failures, weaken checks,
suppress violations or accept snapshots merely to obtain a passing result.

### 6. Approve prototype fabrication

Generate Gerbers, drill files, BOM and placement files from the same validated
revision. Review stackup, holes, slots, board outline, solder mask, paste,
component orientation and assembler feedback. Keep the fabrication package
linked to the source revision and validation evidence.

Passing this stage means **ready to order a prototype**. It does not mean the
physical hardware has been tested. Report this status without placing an order
unless the user has explicitly authorized ordering.

### 7. Test the physical prototype

Verify assembly, mechanical fit, power-up, programming, interfaces, sensors and
the intended load. Measure relevant current, voltage and temperatures. Test
applicable protection and fault behavior.

Record the physical board revision, assembly configuration, firmware versions,
test setup, operating conditions, measurements, results and failures. Obtain
actual physical test evidence; automated design checks or simulations do not
complete this stage. If no prototype is available, leave this stage pending
and identify the design as an untested prototype.

### 8. Prepare the store release

Include a descriptive name, revision, pinout, supported operating limits,
usage instructions, photos, test results and known limitations. Ensure the
published package builds and matches the validated revision. Distinguish
intended limits from limits verified by physical testing.

Label untested designs as **prototypes**. An explicitly labeled prototype
release may be prepared while stage 7 remains pending; it must disclose the
missing physical tests and must not imply that all validation stages passed.
Claim **hardware tested** only for the configuration and operating conditions
actually tested. Do not present rendered images as physical prototype photos
or invent test results.

Revalidate affected areas after design or dependency changes, including new
fabrication outputs when the validated design changes. Record which earlier
results remain applicable and why. Publish each completed implementation step
and version under the standing authorization in "Publish every implementation
step and version" above, preserving the prototype labels and validation gates.

## GitHub authentication

- Use the configured GitHub account `AnasSarkiz` for GitHub operations unless
  the user explicitly requests another account.
- Prefer the authenticated GitHub app connector for pull-request, issue,
  review and repository API actions.
- On macOS, sandboxed commands may be unable to read GitHub CLI credentials
  stored in Keychain. If `gh auth status` fails inside the sandbox, retry with
  escalated sandbox permissions before concluding that authentication is invalid.
- Run authenticated `gh` commands and Git network operations with the narrowly
  scoped escalated permissions needed for Keychain and network access.
- Ask for reauthentication only if the escalated `gh auth status` check also
  fails.
- Keep GitHub credentials in macOS Keychain. Never print, copy or persist tokens
  in prompts, repositories, environment files or plaintext configuration.
