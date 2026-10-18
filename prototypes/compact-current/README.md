# Current controller: motor-bolt hole revision

**WORK IN PROGRESS — 121 native DRC errors. NOT FABRICATION READY.**

This updates the existing NEMA11_RP2040_Compact_Prototype package. The actual current
28 × 28 mm controller PCB has four Ø2.7 mm holes on the OEM motor's nominal
23 mm bolt pattern (X/Y = ±11.5 mm), with radius 2.35 mm head exclusions.
The diameter is a provisional clearance envelope for a shank up to 2.5 mm;
rear bolt thread, length, engagement and torque remain unverified.

The native assembly contains the current PCB and genuine OEM motor, 77 models
with no carrier. All 76 fitted electrical components remain on top. All fitted
STEP poses match native GLB bounds within 0.011 mm. This geometry check does not
certify electrical routing, component collisions, clamp hardware or harness fit.
The original motor and original wire stubs are preserved; final terminated leads
and mating plug fit within the frame remain unresolved.

Placement/routing must be corrected around the new holes before new Gerbers,
BOM/CPL and full checks can be accepted. Prior 0.4.1 zero-error checks describe the
old 25 mm carrier-based layout and do not qualify this changed PCB. The complete
buzzer circuit is the user-authorized omission; the remaining source features
and optional DNP encoder remain present.

[Current source and review](https://github.com/AnasSarkiz/NEMA11_RP2040/tree/edca7e902da1d081cb8a99e8aba7ac66a36fa04e)

New controller milestones revise this same package; they do not create another
separately named controller package. Historical versions remain unchanged.
