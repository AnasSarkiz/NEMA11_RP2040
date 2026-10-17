#!/usr/bin/env python3
"""Conservative mixed-decay ripple screen from published A4988/Panasonic data.

This is a bounded constant-current chopping model, not a transient simulation,
PD inrush qualification or a hardware measurement. Source-cable sharing is not
credited. Real current overshoot, switching edges and regeneration need tests.
"""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
alpha=.3125;off_min=20e-6;off_max=40e-6;peak=.67
# Panasonic EEH-ZC, 47 <= C < 150 uF, fundamental-frequency factors. Applying
# the fundamental factor to all higher harmonics is conservative for these bands.
bands=[(100,200,.15),(200,300,.20),(300,500,.25),(500,1000,.30),
       (1000,2000,.40),(2000,3000,.45),(3000,5000,.55),(5000,10000,.60),
       (10000,15000,.70),(15000,20000,.75),(20000,30000,.80),
       (30000,40000,.80),(40000,50000,.85),(50000,100000,.90)]
# On-state +I, first 31.25% of off-time -I, remainder zero bus current.
# Mean/I = (1+alpha)*D-alpha; AC RMS/I is sqrt(E[x^2]-E[x]^2).
def variance(d):return d+alpha*(1-d)-((1+alpha)*d-alpha)**2
optimum=(1+alpha+2*alpha**2)/(2*(1+alpha)**2)
rows=[]
for low,high,factor in bands:
    lower=max(0,1-high*off_max);upper=min(1,1-low*off_min)
    if lower>upper:continue
    d=min(upper,max(lower,optimum));gain=math.sqrt(max(0,variance(d)))
    # Independently sample the three actual waveform levels to catch a wrong
    # stationary-point/band-bound calculation before recording an upper bound.
    for i in range(1001):
        sample=lower+(upper-lower)*i/1000;fast=alpha*(1-sample)
        waveform_variance=sample+fast-(sample-fast)**2
        assert waveform_variance<=gain**2+1e-12
    rows.append(dict(frequency_band_Hz=[low,high],Panasonic_frequency_factor=factor,duty_interval=[lower,upper],maximum_AC_RMS_per_phase_amp=gain,frequency_weighted_RMS_gain=gain/factor))
gain=max(r['frequency_weighted_RMS_gain'] for r in rows)
# |Ia|+|Ib| <= sqrt(2)*Itrip for the A4988 sine-vector DAC. Triangle inequality
# bounds arbitrary phase correlation and frequency-weighted capacitor heating.
motor_equivalent=math.sqrt(2)*peak*gain;logic_equivalent=.10
choices=[]
for part,uf,rating in [('EEHZC1V470P',47,.9),('EEHZC1V680XP',68,1.4)]:
    loading=(motor_equivalent+logic_equivalent)/rating
    choices.append(dict(part=part,capacitance_uF=uf,rated_RMS_A_at_100kHz_125C=rating,conservative_frequency_weighted_current_A=motor_equivalent+logic_equivalent,normalized_ripple_loading=loading,within_published_frequency_adjusted_rating_under_assumptions=loading<=1))
report=dict(scope='Candidate bulk-capacitor ripple selection screen, not complete board qualification',motor_peak_current_limit_A=peak,ROSC_configuration='Grounded, as retained in the source',A4988_fixed_off_time_range_us=[20,40],mixed_decay_fast_off_fraction=alpha,source_cable_ripple_sharing_credited=False,ideal_current_vector_assumed=True,additional_logic_converter_frequency_equivalent_ripple_budget_A=logic_equivalent,bands=rows,motor_frequency_equivalent_RMS_bound_A=motor_equivalent,candidates=choices,proposed_next_iteration_part='EEHZC1V680XP / C178649',proposed_part_selected_in_published_0_4_0=False,unresolved=['Verify actual peak/overshoot, waveform spectrum, temperature and capacitor RMS current','DC-bias/ripple/regen waveform and source cable behavior','USB-PD attachment/inrush and negotiation with the changed capacitance','Manufacturer maximum body dimensions, placement and mechanical tolerances','Actual JLC assembly stock/allocation, vendor process approval and hardware tests'],manufacturing_release=False)
(ROOT/'artifacts/requirements/bulk-ripple-screen.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(motor_frequency_equivalent_RMS_bound_A=motor_equivalent,candidates=choices,manufacturing_release=False)))
assert not choices[0]['within_published_frequency_adjusted_rating_under_assumptions'] and choices[1]['within_published_frequency_adjusted_rating_under_assumptions']
