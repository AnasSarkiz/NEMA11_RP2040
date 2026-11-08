# Exact buzzer qualification: MLT-5020 / C94598

Review date: 2026-11-08 UTC. Status: source identity materially improved; circuit and hardware qualification remain open.

## Decision

Preserve MLT-5020 / C94598 and the existing driver/clamp. The current C94598-linked manufacturer sheet supports using **4 kHz, 50% square-wave excitation as a starting test target**. The board's nominal 3.3 V is inside its stated 2-4 Vo-p operating range. Neither fact proves the actual board is acoustically or thermally qualified. No firmware or physical waveform was inspected or measured in this review.

Do not use the older sheet's 5 V ceiling, 80 dB minimum, wider temperature range, or powered-life test as specifications for the present C94598 part. Do not describe 100 mA as an established instantaneous current limit or assume it is the actual board current.

## Identity and source chain

1. [JLCPCB C94598](https://jlcpcb.com/partdetail/MLT-5020/C94598) identifies Jiangsu Huaneng Elec, MLT-5020, and the 3 V / 2-4 V version. The page's direct signed PDF download returned HTTP 403 with a stale signed link. The signature was not altered or reused. Therefore the bytes behind that specific JLC link were not verified.
2. [LCSC C94598](https://www.lcsc.com/product-detail/C94598.html) independently identifies the same manufacturer/model/stock code and links to [its C94598 datasheet viewer](https://www.lcsc.com/datasheet/C94598.pdf).
3. That viewer loads [the manufacturer PDF](https://datasheet.lcsc.com/datasheet/pdf/23f5c6599ed9cb614c21ac31ad2b1106.pdf?productCode=C94598), titled Jiangsu Huawha Electronics Co., Ltd., with the same Chinese company name 江苏华能电子有限公司. The cover identifies MLT-5020 and is dated **2021-05-27**. It has five pages. No explicit revision code or historical revision table was found.
4. The exact LCSC-linked PDF was downloaded through its normal browser download control and visually checked. Local SHA-256: `db73c860afd42abdf9a2e69c4a34ac915d68e07108a2188d6ee0a9c02f723be9`, 492,825 bytes.
5. The [older Huaneng manufacturer document](https://file.elecfans.com/web1/M00/A2/2B/pIYBAF1JIOGAJiicAAXD2xPzpTw612.pdf?filename=MLT-5020_HNDZ.pdf) is six pages, dated 2017-07-20, with MLT-5020 and a central-hole description on its cover. Its searchable text was available through web retrieval. Its browser load was blocked, and its original bytes/graphics were not locally verified. It is historical comparison material, not a replacement specification.

The manufacturer naming and model agree, but no manufacturer change notice, interchangeability statement, or lot-specific certificate connecting the 2017 and 2021 specifications was found. A distributor-linked sheet establishes a much stronger stock-code association than a generic model search, but it is not a guarantee of the revision of a future supplied lot. Use the linked 2021 specification as the procurement baseline and resolve deviations with the supplier before release.

## Manufacturer facts and differences

The following table summarizes the two manufacturer documents. Electrical values apply with each sheet's own test conditions, not arbitrary drive waveforms.

| Parameter | C94598-linked sheet, 2021-05-27 | Older sheet, 2017-07-20 |
|---|---|---|
| Rated excitation | 3.0 Vo-p | 3.6 Vo-p |
| Operating excitation | 2-4 Vo-p | 2-5 Vo-p |
| Current | Maximum 100 mA | Maximum 100 mA |
| Coil resistance | 12 ±3 ohm | 12 ±3 ohm |
| Frequency | 4,000 ±200 Hz | 4,000 Hz |
| SPL | Minimum 75 dB at 10 cm | Minimum 80 dB at 10 cm |
| Test waveform | Resonance, square wave, 50% duty | Resonance, square wave, 50% duty |
| Operating temperature | -20 to +70 °C | -30 to +70 °C |
| Storage temperature | -30 to +85 °C | -40 to +85 °C |
| Powered endurance | No powered-life duration specified | 96 h at rated drive, 25 ±10 °C |

Sources: 2021 PDF pp. 2-4; 2017 PDF pp. 2-5. Vo-p is the sheet's voltage notation; do not reinterpret these numbers as RMS or as permission for symmetric ±voltage excitation. The newer sheet's recommended-drive drawing is an unspecified four-pin VDD/EN/OUT/GND driver with a 1 µF supply bypass and the buzzer between supply and OUT. It does not identify the IC or specify an external flyback clamp.

The newer sheet's frequency-response figure uses its rated drive at 10 cm. Its curve is characterization, not a guaranteed SPL at every frequency. No acoustic weighting, microphone calibration uncertainty, distortion limit, directivity limit, or enclosure loss is specified. There is also a mechanical-data discrepancy: the general table says 5.2 × 5.2 × 2 mm, the drawing shows 5.0 ±0.3 mm and 2.0 ±0.2 mm, while distributor listings say 2.5 mm high. Check the drawing, supplied sample, and assembly clearance rather than silently choosing a listing value.

## What is still not specified

- The 100 mA entry is under the standard-drive/rated-voltage conditions, but does not identify peak, mean, or RMS measurement. It is not accompanied by a pulse-current rating, current-versus-frequency curve, or maximum allowable winding dissipation.
- No coil inductance, back-EMF model, reverse-voltage limit, clamp-energy limit, maximum on-time, maximum total beep duration, or envelope duty limit is supplied.
- No winding maximum temperature, permitted temperature rise, thermal resistance, or current derating curve is supplied. Ambient operating temperature is not an internal hot-spot limit.
- The 2021 reliability page contains storage/environmental and assembly tests, not the older document's 96-hour powered life statement. Do not import that old duration.
- The exact source does not qualify the board's MOSFET, retained Schottky clamp, rail layout, enclosure, or firmware. Those remain application measurements.

## Thermal and assembly constraints

The 2021 sheet's reflow plot specifies **250 °C maximum peak**, 170-190 °C preheat for 90 ±30 s, heating ramps no faster than 4 °C/s, and a 10 s maximum interval shown at the 245 °C threshold, followed by air cooling. The plot also has a 265 °C axis mark; that mark is **not permission to use a 265 °C peak**, given the explicit 250 °C limit. The solderability dip test is a separate condition, not a reflow-profile substitute. Have assembly review the original page 3 plot and confirm the proposed process against it. Reflow-pass count, wash compatibility, and moisture handling are not sufficiently defined in this sheet to infer production permissions.

Keep flux/cleaner and particulate contamination away from the sound opening. The old sheet explicitly warns about foreign material, but its warning does not establish the present part's wash rating. Obtain current supplier instructions if cleaning or additional thermal cycles are planned.

## Consequences for the retained board circuit

Circuit supplied by the parent: AP63203 3.3 V rail; DMN2300UFB4-7B low-side MOSFET; 1 kohm gate series resistor; 10 kohm gate pulldown; PMEG6020ELRX with cathode at 3.3 V and anode at the switched buzzer node; local bypass. This topology is assessed as provided, not freshly verified from board files.

### Voltage and waveform

- During MOSFET on-time, buzzer differential voltage is approximately Vrail minus MOSFET and wiring drop. Nominal 3.3 V is 10% above the 3.0 V rated-test value but inside the 2-4 Vo-p operating range. This is not a reason to assume identical current, life, or SPL to the rated test.
- During off-time while coil current continues, the correctly oriented diode is expected to clamp the switched node to roughly Vrail + VF. Across the buzzer, defined positive-terminal minus switched-terminal, this is about **-VF**. Once current decays, the differential voltage approaches zero. Therefore a 50% gate square wave does not imply a 50% rectangular coil-current waveform, or an ideal 0-to-3.3 V buzzer-terminal waveform.
- The Schottky generally lengthens current decay compared with a higher-voltage release path. It can change magnetic excitation and acoustic output. No inductance or magnetic model is available here to quantify the effect. Keep the clamp; do not remove it based on acoustic speculation.
- Measure the actual positive excursion, negative excursion, and Vpp separately. Do not compare rail-referenced drain voltage or total Vpp directly against the sheet's positive Vo-p operating value. Reverse-pulse acceptance remains unresolved.

### Current and heating

- The gate resistor controls the gate drive, not coil current. The pulldown establishes an off state only when the GPIO is not actively driving high. Verify power-on/reset behavior.
- With the 10 kohm pulldown on the gate side of the 1 kohm resistor, the ideal steady high gate voltage is GPIO-high ×10/11, approximately 3.0 V for an ideal 3.3 V GPIO. Confirm actual connection and loaded GPIO level.
- [DMN2300UFB4 datasheet, DS35269 Rev. 5-2](https://www.diodes.com/datasheet/download/DMN2300UFB4.pdf) explicitly covers the -7B ordering suffix and specifies on-resistance at 2.5 V gate drive. This supports evaluating the part as a logic-level switch, not from threshold voltage alone. It does not establish the board's switching losses or temperature. Its 20 V drain-source and ±8 V gate-source absolute maxima are not normal design targets.
- The [PMEG6020ELR manufacturer sheet](https://assets.nexperia.com/documents/data-sheet/PMEG6020ELR.pdf) identifies a 60 V Schottky with 2 A average-current rating under stated test conditions. Its generic current rating is not a buzzer-current qualification, and VF depends on current and temperature. Do not assume a fixed 0.2 V clamp.
- A supply-current meter misses circulating coil current during diode freewheel. Coil heating is related to coil RMS current and resistance; measure the coil current through the full cycle, or retain an explicit qualification gap.
- A sustained high output is a credible fault. Ignoring MOSFET/wiring resistance and using 3.3 V with the stated 9-15 ohm resistance interval gives **0.22-0.37 A** DC after electrical settling; nominal 12 ohm gives 0.275 A. The corresponding initial resistive dissipation is **0.73-1.21 W**, nominal 0.91 W. These are fault estimates, not normal 4 kHz predictions or safe ratings. Heating changes resistance and real behavior.
- An ideal resistive load driven by the same waveform would dissipate 21% more at 3.3 V than at 3.0 V. The buzzer is electromechanical and the retained clamp changes current, so this is only a sensitivity warning, not a power prediction.

The [AP63203 family sheet, DS41326 Rev. 3-2](https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf) identifies the fixed 3.3 V version and its operating requirements. The regulator's rated output capacity does not protect a small buzzer from excessive DC current. Verify actual startup, transient excursion, local supply impedance, and simultaneous system loading.

## Release gates

1. Pin the procurement record to C94598 plus the saved 2021-05-27 manufacturer sheet; obtain supplier clarification for lot/revision, 100 mA metric, reverse/freewheel pulse allowance, continuous-use limits, and assembly discrepancies when required for release.
2. Verify firmware implementation and measure **actual** GPIO/gate, buzzer differential voltage, coil current, and 3.3 V transients. The current statement is only a paper target, never a hardware result.
3. Establish acoustic performance at 10 cm under controlled conditions and in the intended enclosure, using the retained clamp and final placement. Define the product's required audibility separately from a component free-air specification.
4. Measure temperature over the longest intended beep/repetition pattern and application temperature/load extremes. Without a supplier winding-temperature criterion, this is an engineering screening result, not complete lifetime qualification.
5. Confirm safe off behavior at reset, brownout, interrupted tone generation, and firmware failure. Do not intentionally perform a long DC-on stress test on the buzzer.
6. Confirm the assembly profile respects the actual buzzer sheet. Do not treat generic lead-free reflow defaults as acceptable.

## Work performed and limitations

Completed: public stock-code/specification lookup; exact LCSC source-link chain; original PDF download/hash/text extraction; visual inspection of the electrical table, driver schematic, thermal plot, dimensions, and response graph; historical text comparison; supporting transistor/diode/regulator manufacturer references; proposed bench plan.

Not performed: board inspection, footprint verification, simulation with measured magnetic parameters, firmware inspection, hardware testing, acoustic measurement, thermal measurement, supplier contact, ordering, model edits, upload, or publication.

Requested board path `/workspace/scratch/07b71d1575ce/nema11_work/boards/nema11-rp2040-two-layer--20261022-a1` was absent in this worker's available workspace. The supplied commit `1180e9a` and native JSON SHA-256 `3323aa0f2322cafc0713d6c94e5841ff43ebf47c8a5281acf4744c58ac088600` are parent-provided identifiers, not independently verified here. No board files were modified.
