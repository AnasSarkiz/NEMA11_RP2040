# Proposed bench qualification, not executed

## Purpose and boundaries

Qualify the preserved MLT-5020 / C94598 on the actual board with its DMN2300UFB4-7B, PMEG6020ELRX clamp, and local bypass. Do not remove the clamp, substitute a buzzer, change the PCB, or assume firmware generates 4 kHz/50%. These tests require physical hardware and an operator. No test below has been performed.

The manufacturer sheet leaves current metric, reverse-pulse tolerance, coil temperature, and continuous-tone duration undefined. Gather evidence and obtain those limits where necessary; do not turn an arbitrary laboratory stop threshold into a manufacturer rating.

## Equipment and preparation

- Record board revision, firmware hash/build configuration, buzzer reel/lot marking, supplier SKU and datasheet identity.
- Use a current-limited supply with sufficient total board budget, an oscilloscope, a suitable differential probe, a non-invasive current probe where the buzzer path is physically accessible, and temperature instrumentation appropriate to a 5 mm plastic part. Record calibration and uncertainty.
- For acoustic work, use a calibrated sound meter or measurement microphone; record weighting, bandwidth, integration time, background noise, microphone orientation, distance, and room/enclosure geometry.
- A board-input current limit does not precisely limit coil RMS current. The AP63203 may support substantially more current than the buzzer tolerates. Do not rely on either as the sole buzzer protection.
- Use proper differential probing. Do not attach an earth-ground oscilloscope clip to the switched node or either arbitrary buzzer terminal. Observe applicable power-supply isolation and probe voltage limits.
- If the coil conductor is inaccessible to a suitable probe, report the limitation. Do not equate input/supply average current to coil peak/RMS current. A future sense fixture or modification requires its own engineering plan; it is not authorized or implemented by this study.

## 1. Unpowered identity and continuity

1. Verify actual fitted MLT-5020/C94598 and polarity against the manufacturer drawing, not footprint labels alone. Verify the third support land's intended treatment from the footprint/source; do not guess its electrical role.
2. Confirm flyback cathode is on 3.3 V and anode on the buzzer sink; confirm MOSFET gate/source/drain and local bypass connection.
3. If resistance can be measured without parallel-path error, compare with 12 ±3 ohm at documented temperature. A contaminated or out-of-range measurement is a reason to investigate, not automatically a rejected part.
4. Inspect the acoustic opening for solder/flux obstruction, mechanical damage and final enclosure clearance. Confirm the assembly thermal profile separately.

## 2. Safe startup and firmware inspection

1. Review GPIO assignment, timer/PWM clock, divider/top values, polarity and shutdown behavior from the actual firmware. Calculate intended frequency and high-time from those values, then measure them.
2. Confirm the gate is low/off through cold power-up, reset, bootloader, watchdog and brownout sequences. Check that enabling/disabling tones does not leave a static high level.
3. Before any long tone, establish a means of immediately stopping drive and power. Start with isolated short bursts, for example 100 ms followed by at least 1 s off, while observing waveform and current. These are cautious test settings, not guaranteed safe-duration ratings.
4. Record the actual carrier frequency/duty and any envelope gating. A nominal target of 4.000 kHz/50.0% may be used for initial tests but must not be reported as firmware behavior until observed.

## 3. Electrical waveform capture

Capture simultaneously where practical:

- GPIO before 1 kohm, gate-to-source voltage, and drain/sink-to-ground voltage.
- Local buzzer positive rail and **differential voltage across the buzzer**, positive terminal minus sink.
- Coil current during on-time and diode freewheel, including startup and final decay.

Record frequency, high-time, gate steady-high level, transition times, Vrail minimum/maximum, differential positive and negative extrema, drain overshoot/ringing, coil Ipeak/Imean/Irms, decay time and whether current returns to zero before the next pulse. Save traces with timebase, bandwidth and probe settings.

Acceptance/interpretation:

- For reproducing the paper test, use a measured 4 kHz/50% carrier and document instrument error. The sheet's ±200 Hz is the component frequency entry, not permission to accept arbitrary firmware timing errors.
- Compare the applied positive excitation with the stated 2-4 Vo-p operating range. Rated acoustic comparison is at 3.0 Vo-p; a nominal 3.3 V board run is a different condition. Measure negative off pulses separately; the sheet does not supply their permissible magnitude/duration.
- Check MOSFET and diode stresses against their own manufacturer conditions with design margin, not at absolute maxima. A rail-plus-Schottky clamp expectation is not evidence that layout ringing is controlled.
- Treat 100 mA as an unresolved measurement definition. Record all current metrics. If any exceeds 100 mA, stop escalation and resolve its meaning and waveform acceptability with the supplier before claiming compliance. A brief peak above 100 mA is not automatically proof of failure; a low supply average is not proof of safety.
- Stop immediately on unexpected sustained DC, uncontrolled current growth, abnormal heating, rail collapse, smoke/odor, unstable operation or loss of tone. Do not run deliberate long DC faults on the buzzer.

## 4. Acoustic characterization

1. Begin at the verified 4 kHz/50% setting using the actual retained circuit. Place the microphone 10 cm from the sound outlet with reproducible orientation and low background noise. Record rail/differential drive, all current metrics and temperature alongside SPL.
2. The component minimum is 75 dB under its own 3.0 Vo-p standard-drive condition. If the board cannot reproduce that condition without alteration, label the result application characterization, not an exact manufacturer acceptance test.
3. Measure the final enclosed/installed board as well as the open board. Set a product audibility criterion based on listening distance and background noise; do not assume the component figure transfers to the enclosure.
4. A small sweep near 3.8, 4.0 and 4.2 kHz may characterize resonance if current and thermal behavior remain controlled. It is not necessary to sweep broadly or vary pulse duty to search for maximum loudness. The frequency-response graph is not a guaranteed acoustic specification across its plotted range.

## 5. Thermal and endurance screening

1. Begin at room temperature with short bursts. After electrical behavior is understood, increase toward the **longest intended application beep and repetition pattern**, not an arbitrary continuous-tone life test.
2. Measure ambient temperature near the buzzer, buzzer surface temperature, MOSFET/diode temperatures, rail voltage, current metrics and SPL over time. Consider thermocouple loading, adhesive placement and IR emissivity error on the tiny package.
3. Record temperatures at start, during the pattern and during cooldown. Capture changes in resistance/current/SPL that may indicate heating. Document a conservative engineering stop criterion before the test; supplier winding-temperature and rise limits are still needed for a defensible lifetime qualification.
4. Repeat at the product's actual low/high operating ambient, rail/load extremes and relevant motor activity only after the initial tests are acceptable. Do not assume the whole product is qualified to the component's -20 to +70 °C range.
5. A stable surface temperature alone does not establish safe winding temperature or lifetime. No powered-life duration from the older 2017 sheet should be used as a promise for the current part.

## 6. Interference and off-state checks

- Run motor commutation and both USB interfaces in their expected modes while sounding and stopping the buzzer. Observe 3.3 V ripple, resets, encoder/ADC interference and audible modulation.
- Check normal mute/timeout, reboot during a burst, watchdog and low-supply behavior. Verify the gate returns low and coil current decays.
- To assess a static-high software fault, use analysis or an appropriately current-limited test arrangement designed for the purpose. Do not leave the actual buzzer DC-powered merely to demonstrate that it heats.

## Minimum supplier questions, not sent

1. Does C94598 currently ship the attached 2021-05-27 MLT-5020 specification? Is there a newer revision or a change notice from the 2017 3.6 V version?
2. For Max100mA, is the measurement peak, RMS, time-average coil current or supply current? At which exact waveform, voltage, frequency, temperature and driver?
3. Is 3.3 V, 4 kHz, 50% low-side drive with a Schottky across the buzzer acceptable? What reverse/freewheel pulse, continuous tone duration, repetition/envelope and coil-temperature limits apply?
4. What reflow pass count, peak duration, moisture handling and cleaning process are approved? Please resolve listing/drawing dimensions and the reflow plot's explicit 250 °C peak versus the 265 °C axis mark.

No supplier contact is authorized by this report. These are review questions for a future approved inquiry.
