#!/usr/bin/env python3
"""Pre-layout screening of the published v1.13 A4988 and original motor drawing.

This is a design calculation, not component selection, thermal simulation, a
manufacturer-guaranteed current bound, or hardware validation.
"""
import argparse
import itertools
import json
import math
from pathlib import Path


def trip_current(vdd, high, low, sense, gain_error=0.0, reference_input_a=0.0):
    vref = vdd * low / (high + low) - reference_input_a * high * low / (high + low)
    return vref / (8 * sense) * (1 + gain_error)


def corner_currents(high, low, sense, rail_tolerance=.05,
                    resistor_tolerance=.01, driver_allowance=.05, reference_input_allowance_a=3e-6):
    return [trip_current(3.3 * (1 + a * rail_tolerance),
                         high * (1 + b * resistor_tolerance),
                         low * (1 + c * resistor_tolerance),
                         sense * (1 + d * resistor_tolerance),
                         e * driver_allowance, f * reference_input_allowance_a)
            for a, b, c, d, e, f in itertools.product((-1, 1), repeat=6)]


def ipc2221_width_mm(current, copper_um, rise_c, internal=False):
    """Legacy isolated-trace screen; not an IPC-2152 layout qualification."""
    k = .024 if internal else .048
    area_mil2 = (current / (k * rise_c ** .44)) ** (1 / .725)
    return area_mil2 / (copper_um / 25.4) * .0254


def report():
    req = json.loads((Path(__file__).resolve().parents[1] /
                      'config/design-requirements.json').read_text())
    rated = req['motor']['phase_current_a']
    rs = .24
    proposed_high, proposed_low = 20000, 10000
    nominal = trip_current(3.3, proposed_high, proposed_low, rs)
    corners = corner_currents(proposed_high, proposed_low, rs)
    reference = trip_current(3.3, 39000, 10000, rs)
    # Full rated current is used for copper/thermal sizing, including return paths.
    # Transients and input/regeneration need separate budgets and measurements.
    return {
        'status': 'pre_layout_conditional_calculation_only',
        'driver_assumption': 'A4988SETTR-T verified in exact published NEMA14 v1.13.0; accuracy/thermal qualification remains open',
        'motor_phase_current_ceiling_a': rated,
        'assumptions': {
            'logic_rail_v': 3.3, 'logic_rail_tolerance_fraction': .05,
            'resistor_tolerance_fraction': .01,
            'unqualified_driver_gain_allowance_fraction': .05,
            'reference_input_current_allowance_a': 3e-6,
            'accuracy_limitation': 'A4988 5% accuracy specification is at VREF=2V and 100%/70.71% DAC; this 1.1V candidate is not covered by that test condition. 38.27% DAC specifies 15% at 2V.',
            'thermal_screen_rise_c': 30,
            'external_copper_um': 35, 'internal_copper_um': req['fabrication']['inner_copper_um']
        },
        'reference_v1_12_trip_a': reference,
        'selected_source_candidate': {'divider_high_jlcpcb': 'C4184', 'divider_low_ohm': 10000, 'divider_high_ohm': 20000},
        'selected_sense_resistor': {
            'manufacturer': 'UNI-ROYAL / ROYALOHM', 'part': 'HP05W3F240LT5E',
            'jlcpcb': 'C7434086', 'resistance_ohm': rs,
            'initial_tolerance_fraction': .01, 'TCR_ppm_per_K': 100,
            'rating_w_at_ambient_70c': 1 / 3,
            'linear_derated_rating_w': {str(t): (1 / 3) * (155 - t) / (155 - 70) for t in [85, 100]},
            'rated_current_loading_fraction_at_70c': rated ** 2 * rs / (1 / 3),
            'reference_125mW_loading_fraction_before_derating': rated ** 2 * rs / .125,
            'qualification': 'Initial tolerance and nominal ambient derating only; post-reflow resistance, pulse behavior and hot current need verification.'
        },
        'vref_for_exact_nominal_rated_trip_v': rated * 8 * rs,
        'source_candidate_screening': {
            'divider_high_ohm': proposed_high, 'divider_low_ohm': proposed_low,
            'each_phase_sense_ohm': rs,
            'nominal_vref_v': 3.3 * proposed_low / (proposed_high + proposed_low),
            'nominal_trip_a': nominal, 'corner_count': len(corners),
            'minimum_screened_trip_a': min(corners),
            'maximum_screened_trip_a': max(corners),
            'below_motor_rating_under_assumed_budget': max(corners) <= rated,
            'full_step_each_phase_a_at_70_71_percent': nominal / math.sqrt(2),
            'nominal_sense_loss_w_each_at_trip': nominal ** 2 * rs
        },
        'thermal_screen': {
            'sense_loss_w_each_at_rated_current': rated ** 2 * rs,
            'sense_loss_w_both_if_both_at_rated_current': 2 * rated ** 2 * rs,
            'minimum_sense_nameplate_w_at_50_percent_loading': 2 * rated ** 2 * rs,
            'selected_sense_rating_w_before_temperature_derating': 1 / 3,
            'driver_conduction_w_per_ohm_of_bridge_path_two_phases': 2 * rated ** 2,
            'conduction_loss_multiplier_vs_v1_12_at_same_rds': (rated / reference) ** 2,
            'motor_copper_loss_w_per_ohm_per_phase_two_phases_at_rated_current': 2 * rated ** 2,
            'motor_copper_loss_w': 2 * rated ** 2 * req['motor']['phase_resistance_ohms'],
            'motor_two_phase_DC_loss_at_25c_max_resistance_w': 2 * rated ** 2 * req['motor']['phase_resistance_ohms'] * (1 + req['motor']['phase_resistance_tolerance_fraction']),
            'ideal_sine_microstep_total_loss_at_nominal_trip_and_25c_w': nominal ** 2 * req['motor']['phase_resistance_ohms'],
            'motor_loss_scope': 'Two phases at rated DC current versus ideal sine current regulation; excludes winding heating, drive losses and mechanical losses',
            'junction_temperature_c': None
        },
        'isolated_trace_screen_minimum_width_mm_at_0_67a': {
            'external_35um': ipc2221_width_mm(rated, 35, 30),
            'legacy_default_internal_17_5um': ipc2221_width_mm(rated, 17.5, 30, True),
            'selected_internal_35um': ipc2221_width_mm(rated, 35, 30, True)
        },
        'release_blockers': [
            'Verify routed sense-path resistance, shared returns and current regulation on hardware.',
            'Verify selected genuine shunt pulse behavior and hot/post-reflow performance.',
            'Verify manufacturer current accuracy across microsteps and actual VDD limits.',
            'Review Kelvin sense, shared returns, exposed pad, copper and via thermal paths.',
            'Measure phase current, junction/case temperature and regenerative overshoot.'
        ],
        'manufacturing_release': False
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    data = json.dumps(report(), indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
    else:
        print(data, end='')
