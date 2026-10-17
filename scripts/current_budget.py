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


def trip_current(vdd, high, low, sense, gain_error=0.0):
    return vdd * low / (high + low) / (8 * sense) * (1 + gain_error)


def corner_currents(high, low, sense, rail_tolerance=.05,
                    resistor_tolerance=.01, driver_allowance=.05):
    return [trip_current(3.3 * (1 + a * rail_tolerance),
                         high * (1 + b * resistor_tolerance),
                         low * (1 + c * resistor_tolerance),
                         sense * (1 + d * resistor_tolerance),
                         e * driver_allowance)
            for a, b, c, d, e in itertools.product((-1, 1), repeat=5)]


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
    proposed_high, proposed_low = 19600, 10000
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
            'thermal_screen_rise_c': 30,
            'external_copper_um': 35, 'internal_copper_um': 17.5
        },
        'reference_v1_12_trip_a': reference,
        'vref_for_exact_nominal_rated_trip_v': rated * 8 * rs,
        'screening_candidate_not_selected_parts': {
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
            'suggested_sense_rating_w_before_temperature_derating': .25,
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
            'internal_17_5um': ipc2221_width_mm(rated, 17.5, 30, True)
        },
        'release_blockers': [
            'Complete physical-pin parity and current-sense topology review of exact published v1.13.0.',
            'Select genuine supplier parts; verify tolerance, pulse power and hot derating.',
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
