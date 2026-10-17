# Bulk capacitor review after routed prototype 0.4.0

The 0.4.0 BOM still contains the original **ROQANG RVT1V470M0605 / C72522**,
47 µF / 35 V. Its public distributor listing specifies 54 mA RMS at 120 Hz;
the original ROQANG sheet gives a 1.40 high-frequency correction. No source-cable
impedance or measured capacitor current establishes that part's suitability.
Routing/DRC success does not qualify its ripple heating.

The native CLI successfully imported **Panasonic EEHZC1V680XP / C178649** as a
candidate for the next revision. It is 68 µF / 35 V, 6.3 × 7.7 mm, rated 1.4 A
RMS at 100 kHz / 125 °C with maximum 35 mΩ ESR at 100 kHz / 20 °C. Its published
frequency multipliers must be applied at the actual chopping frequency. The
47 µF / 900 mA part considered first does not pass the conservative screen below.

[The calculation](../scripts/screen_bulk_ripple.py) includes the A4988's grounded
ROSC configuration: **20–40 µs** off-time and **31.25% fast decay** before slow
decay. It models bus current levels +I / −I / 0, rather than assuming a simple
on/off input current. For each frequency band it analytically bounds waveform
variance over possible duties, then combines the two phases with the triangle
inequality and the sine-vector current bound. It credits no ripple sharing by
the source cable. A separate 0.10 A frequency-equivalent logic-converter budget
is included. Under the stated constant-current assumptions, the proposed 68 µF
part loads its corrected ripple rating to **86.9%**; the 47 µF candidate reaches
135.1%. These are conservative selection screens, not measured waveforms.

The [original native import and official Panasonic STEP/mesh](../imports/compact-candidates/EEHZC1V680XP/)
are retained. The official STEP has four valid solids, all retained in its
derived OBJ, with no resizing or cropping. Its raw height axis is +Y; its native
PCB pose, polarity and maximum-tolerance assembly checks remain to be completed.
An additional PCB-frame STEP/OBJ uses only rigid X+90° and Z+180° rotations:
the lead plane becomes Z=0 and native pin 1 stays on the left. All four solids
and their exact volume are retained; the original STEP remains unchanged.
The imported 68 µF lands retain a 0.000127 mm coordinate difference from the
old footprint; they are not falsely described as byte-identical. The imported
generic supplier CAD is also preserved separately from the official CAD.

[Stock observation](../artifacts/requirements/hybrid-bulk-stock-observation.json)
records 1,218 pieces on LCSC's public page at the observation time. This is not
reserved stock or confirmation of JLC machine availability. The candidate is
**not yet installed in the published 0.4.0 PCB/BOM/prototype**. Its native source,
unchanged-feature parity, complete DRC/short/connectivity/CAM, frame, lead pose,
BOM/CPL and 3D checks must pass before a new version is published. Changing bulk
capacitance also requires USB-PD attachment/inrush review. Actual peak current,
PWM spectrum/overshoot, capacitor temperature and regenerative stops still need
hardware validation.

The [separate integration validation](../artifacts/requirements/hybrid-bulk-source-validation.json)
now records zero native DRC, independent copper, opens and shorts with the 68 µF
part. All 76 fitted native GLB model bounds match their STEP poses within
0.011 mm. The corrected PCB-frame model is upright in the actual native exporter.
The new connected A4 sheets and 75-placement SMT BOM/CPL also pass locally.
This remains a development candidate; it has not replaced the public 0.4.0 package.

```sh
bun scripts/build-controller.tsx --compact --four-mounts --no-buzzer --layers 6 \
  --hybrid-bulk --placement config/compact-hybrid-placement.json --out /tmp/nema11-hybrid
python scripts/build_hybrid_candidate.py --folder /tmp/nema11-hybrid
```

Use the CAD Python environment for the construction and geometry checks. The
explicit source profile enables the selected native filled/capped via feature;
the strict process-policy check still rejects ordinary vias in component lands.
The old 0.4.0 source reproduces byte-for-byte after these optional changes.

Maximum frame tolerance is a known open layout issue. The Panasonic drawing
specifies 6.6 ±0.2 mm base dimensions and a 6.3 ±0.5 mm can. At the present Y
position, a 6.8 mm maximum part and an assumed ±0.05 mm placement error can
extend 0.039 mm beyond the 28.3 mm frame. Nominal CAD fit is therefore not a
maximum-tolerance pass. USB routing, that placement budget, carrier/hardware,
the new CAM release and factory/physical qualification remain separate gates.
