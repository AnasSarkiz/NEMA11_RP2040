# Compact NEMA11 replacements: fresh documentary requalification

Reviewed 2026-11-09 UTC. This is a source, geometry and electrical paper review of **CH224Q / C46061833** and **DMN2300UFB4-7B / C154728** in the existing NEMA11 board, not a new V2 board and not manufacturing release. No imports, circuitry, placements, native output, configuration or public project were changed by this review. Matching old import hashes establishes provenance, not qualification.

## Decision

Retain these exact candidates for continued design work. The observed pins and nominal operating intent agree with manufacturer evidence. DMN copper agrees with the manufacturer's suggested footprint after rotation. CH224 exposed-pad numbering requires an explicit interpretation: supplier pin11/EP is the manufacturer's pad0/GND, not another signal. Remaining thermal, transient, stencil, assembly-orientation and application tests prevent unconditional qualification. Do not handpatch source imports.

## Sources and reproducibility

Supporting PDFs, extracted text, inspected page images, provenance and hashes are in `references/compact-replacements/`. The read-only `python references/compact-replacements/check.py` prints import hashes, copper geometry, raw OBJ bounds and screening calculations. Saved output is `check-results.json`. These checks do not build or route the PCB and do not establish inter-component clearance.

- WCH CH224 manual 1, **v2.1**, 16 pages, obtained from the exact C46061833 LCSC listing → datasheet viewer → manufacturer-authored PDF. Pages 2–3: pins; 5: resistor selection; 8: reference circuit; 13–14: limits; 15: package. The WCH English landing page advertises v2.0; it is not the source of the archived v2.1 bytes. The legacy LCSC URL returned HTML rather than a PDF; that failed response is separately labeled.
- Diodes **DS35269 Rev. 5-2, July 2019**, 7 pages, downloaded directly from Diodes' manufacturer datasheet endpoint. Page 1 includes the exact -7B order code; page 2 electrical/thermal conditions; pages 3–5 typical curves; page 6 package and suggested land pattern.
- Raspberry Pi RP2040 manufacturer datasheet, current downloaded bytes, §5.5.3.4/Table 625, printed pages 615–616: GPIO VOH. Retain document bytes/hash because the online PDF may change.
- Exact C11702 and C25744 supplier pages are archived as HTML. Their product structured metadata confirms 1 kΩ / 10 kΩ and ±1%; extracted identity/ratings are in `resistor-supplier-metadata.json`. These are supplier specifications, not a fresh manufacturer resistor-series qualification.
- Buzzer application context uses `../../docs/reconstruction-20261108/exact-buzzer/` and its C94598-linked Huawha 2021-05-27 PDF, not the older buzzer sheet. This review does not repeat its hardware qualification.

## CH224Q pin and electrical audit

| Imported physical pad | Manufacturer identity | Observed board connection |
|---|---|---|
| 1 | VHV | PD_VHV, through retained 0 Ω R_PD to PD_VBUS |
| 2, 3 | CFG2/SCL, CFG3/SDA | noConnect |
| 4, 5 | DP, DM | noConnect |
| 6, 7 | CC2, CC1 | PD_CC2, PD_CC1 |
| 8 | VBUS voltage sense | PD_VBUS |
| 9 | CFG1 | PD_CFG, 56 kΩ to GND |
| 10 | PG, active-low open-drain | PD_GOOD |
| supplier 11/EP | manufacturer **0/GND**, exposed thermal pad | GND |

The v2.1 top-view package drawing shows pin1 bottom-left, pin5 bottom-right, pin6 top-right, pin10 top-left, matching the import. Supplier EP11 sits centrally. Pad-number aliasing is documented here; no source renaming was done. Both logical connection and physical exposure must remain ground through downstream exports/assembly.

56 kΩ requests **15 V**, with CFG2/3 allowed floating in single-resistor mode. This is a request, not assurance every charger supplies 15 V. Leaving DP/DM unconnected limits use of protocols needing those lines; USB-C CC-based PD remains the intended route. VBUS must be shorted to VHV, matching the retained 0 Ω path rather than the old CH224K shunt-regulator resistor arrangement. The reference circuit calls for 1 µF VHV-to-ground bypass and voltage-appropriate capacitor selection.

CH224Q/A absolute limits: VHV, PG/VBUS and CC pins −0.5 to 32 V; DP/DM/CFG1 −0.5 to 3.8 V; CFG2/3 −0.5 to 6.5 V; total chip dissipation 300 mW. The feature list says 4–30 V input; the 25°C electrical table gives VHV 3.3–30 V and ICC 1.8 mA typical/12 mA max. Do not treat 32 V absolute maximum as an operating rating or infer all maxima are simultaneously usable. At nominal 15 V × 12 mA = 180 mW, below 300 mW as a simple screen, not a junction-temperature proof. The internal reset threshold of 32–34 V is not protection that permits exceeding the 32 V absolute limit. PG is open-drain, not a push-pull 15 V output.

## CH224Q assembly geometry

- Manufacturer body: 2.0 ±0.1 mm square, 0.4 mm pitch. Import pitch approximately 0.4000 mm, pads 0.2240 × 0.5050 mm at y=±0.9275 mm, correctly sequenced.
- Manufacturer exposed metal: 1.5 ±0.2 × 0.9 ±0.15 mm with a clipped corner. Import copper EP: 1.4000 × 0.9000 mm, rectangular. This is within the stated exposed-metal size range, but **package metal dimensions are not a recommended PCB land pattern**. The supplier copper need not equal package metal. WCH provides no stencil/land recommendation in this sheet. EP paste volume, voiding, mask, solder bridging and solderability at package tolerance extremes remain assembly-review items.
- Import courtyard 2.5000 × 2.8600 mm encloses copper and maximum 2.1 mm body. Nominal side body clearance is 0.25 mm, worst stated body side clearance 0.20 mm. No claim of an IPC courtyard class is made.
- Raw OBJ bounds: 2.000 × 2.020 × 0.813 mm; STEP header names DFN-10 2×2 H0.8 P0.40. WCH drawing gives 0.75±0.05 mm height (also an alternative parenthetical 0.55±0.05) and 0.025±0.025 mm standoff. The generic model is broadly size-consistent, not evidence of the exact supplied height option or seating interpretation. Do not use it alone to approve an enclosure.
- Pin1 silkscreen circle extends beyond the courtyard: center y=−1.4800, radius 0.0750, versus courtyard y=−1.4300. Copper/body containment passes; silk extent needs separate collision review. It does not justify modifying the untouched import.

## DMN2300UFB4-7B pins, footprint and model

The manufacturer's top view identifies a large drain on one side and gate/source split on the other; the bottom-view package drawing identifies pin1. Rotating to the import's axis gives **pin1 gate lower-left, pin2 drain above, pin3 source lower-right**. Board Q_BUZZER and Q_STATUS_R/G/B all use pin1 for gate, pin2 for load sink, pin3 for ground. The bar marking denotes the gate/source side, not by itself which split pad is gate. Verify placement rotation against the complete top/bottom-view drawing, not only the bar.

Page 6 suggested lands are 0.40×0.25 mm split pads, 0.40×0.70 mm drain pad, 0.70 mm opposing-row centers, 0.20 mm split-pad gap, 0.30 mm opposing-pad gap, total 1.10×0.70 mm. Import after rotation: split pads 0.2500×0.4000, drain 0.7000×0.4000, row centers ±0.3500, split x approximately ±0.2250. Thus copper matches to import rounding (under 0.001 mm), despite the package's physical split-pin pitch being 0.35 mm rather than the land-center spacing 0.45 mm. Do not confuse package pitch with the suggested larger land layout.

Manufacturer body 0.95–1.05 ×0.55–0.65 mm, height ≤0.40 mm. Raw OBJ 0.620×1.020 mm in-plane is within those rotated limits; raw z −0.01…0.40 mm and import origin z −0.01 warrant a seating/render check, not a claim of precision. STEP header identifies X2-DFN1006-3 H0.4 P0.35. STEP BREP pin solids and final renderer transforms were not independently qualified. Courtyard is 1.2000×1.6000 mm, enclosing copper and body, giving approximately 0.25 mm copper clearance. The pin1 silk circle reaches y≈−0.9075 outside courtyard y=−0.8000. Final neighboring silk/assembly overlap review remains necessary.

## Static drive and load screening

RP2040 Table 625 specifies VOH minimum **2.62 V at IOVDD=3.3 V**, for the selected 2/4/8/12 mA drive setting. With 1 kΩ series and 10 kΩ gate pulldown, use the unfavorable 1% values Rg=1010 Ω and Rpd=9900 Ω, and provisionally the DMN 10 µA maximum gate leakage:

VGS = (2.62 − 10 µA ×1010) ×9900/(1010+9900) = **2.36829 V**.

GPIO static load is about **0.2492 mA**, comfortably below even the 2 mA test current. This does **not** establish guaranteed 2.5 V gate drive, so use the **1.8 V / 360 mΩ max RDS(on)** specification at ID=500 mA, not the 2.5 V / 240 mΩ entry. Gate threshold 0.45–0.95 V at only 250 µA is not a full-on criterion. The 1% calculation excludes resistor temperature coefficient, rail tolerance/ground bounce and firmware faults; the 2.62 V VOH value specifically assumes 3.3 V IOVDD.

Important qualification: Diodes specifies IGSS≤10 µA at VGS=±8 V, VDS=0 V, at its default **25°C** conditions. Applying this as a conservative low-voltage static screen is reasonable engineering screening, but is not a separately specified maximum across every bias/temperature. It must not become an all-temperature guarantee. At the same resistor/VOH assumptions, total sink leakage about **630 µA** would reduce VGS to 1.8 V. That is a sensitivity threshold, not an allowable or guaranteed hot leakage value. In high impedance, 10 µA sourced into a 10.1 kΩ pulldown gives 0.101 V; again this is conditional, not a cold/hot/startup proof. Active-low VOL and transient Miller behavior also require checking in the application.

DMN limits: VDS 20 V, VGS ±8 V, junction/storage −55…150°C. The listed 1.30 A continuous rating is at VGS=4.5 V/25°C and must not be borrowed for this gate drive. The 6 A pulse rating is for 10 µs/1% duty test-board conditions, not an allowable 4 kHz buzzer peak. RDS(on) uses short pulse tests to minimize self heating. Rated 500 mW and 250°C/W are for the specified minimum recommended FR-4 land arrangement; they are not a measured thermal model of this compact board. The transient thermal plot separately prints 262°C/W, another reason not to infer exact board thermal performance from one number.

For BZ1, nominal 3.3 V and minimum stated DC resistance 9 Ω give **0.3667 A** as a resistance-only DC screen. At 0.36 Ω that gives **48.4 mW** MOSFET conduction and **12.1°C** rise if 250°C/W were applicable. These are deliberately conditional calculations, not actual waveform/current/temperature or guaranteed peak claims. Real excitation, inductance, winding temperature, flyback recirculation, supply tolerance and switching loss change the result. The 2021 buzzer 100 mA specification is measurement-ambiguous and is not used as peak current. 4 kHz/50% is the manufacturer's starting excitation condition, not a guarantee that this board meets it. Retained PMEG6020ELRX clamp and 10 µF bypass support the topology but do not prove clamp overshoot, dissipation or safe continuous-on behavior. Measure VGS/VDS and coil current/temperature, including startup/reset and stuck-on behavior; do not intentionally exceed component ratings.

For the three LED sinks, the common anode is DATA_VBUS and each channel has 1 kΩ. If DATA_VBUS is a conventional 5 V rail, ignoring LED drop gives an upper screen of 5/990≈5.05 mA per branch and about 9.2 µW MOSFET conduction at 0.36 Ω. This remains conditional on actual rail voltage; do not connect these drains to the 15 V PD rail by assumption. Their low current gives ample nominal conduction margin, but no hot off-leakage/ghosting guarantee. The datasheet IDSS≤1 µA at 20 V is specified at 25°C; hot curves are typical, not guaranteed maxima.

## Release gates still open

1. Exact delivered lot/package option and manufacturer/supplier change status; current sourcing availability and assembly process capability.
2. Manufacturer/assembler acceptance of CH224 EP land and paste, solder mask/stencil, pin1 conventions, actual seating/model orientation, and independent neighboring courtyard/silk checks.
3. PD negotiation/startup/fallback, 15 V rail transient limits, correct PG use and bypass derating/layout. This chip does not itself guarantee downstream system overvoltage safety.
4. Rail/IO tolerance and all-temperature gate/leakage analysis; measured gate transitions, drain overshoot, buzzer winding/current/clamp heating and LED off-state behavior.
5. Board-level native/ERC/DRC/export/assembly validation and real hardware checks, outside this documentary task. Existing hash equality or successful software checks cannot close these hardware gates.
