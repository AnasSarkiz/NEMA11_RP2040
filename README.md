# NEMA11 RP2040 controller

Hardware development for the STEPPERONLINE **11HS12-0674S**, to preserve the
published `AnasSarkiz/NEMA14_RP2040@1.13.0` feature set in a separate project.
The NEMA14 repository is a read-only reference.

**Current milestone: requirements and preliminary electrical screening. No PCB,
schematic, Gerbers, production BOM/CPL or assembly is released.** The requested
v1.13.0 source and original motor PDF/STEP are blocked by the environment's
network policy. GitHub main is v1.8.2; the accessible review branch is v1.12.0,
which is inspection evidence, not a replacement for the requested baseline.

- [Design requirements](config/design-requirements.json)
- [Engineering review and attachment constraints](docs/design-review.md)
- [Validation and release plan](docs/validation-plan.md)
- [Preliminary current/thermal calculation](artifacts/requirements/current-budget.json)
- [Observed v1.12.0 component/pin inventory](artifacts/requirements/reference-1.12-inspection.json)

Run the current milestone checks with:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/current_budget.py --output artifacts/requirements/current-budget.json
```

These checks validate calculation bounds, not a circuit or physical motor.
Pending external prerequisites are documented in the engineering review. No
substitutions, fabricated rear holes or assumed rear shaft are authorized.
