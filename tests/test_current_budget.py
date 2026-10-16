"""Check engineering bounds and scaling, not hardware operation."""
import unittest
from scripts.current_budget import corner_currents, ipc2221_width_mm, report, trip_current


class CurrentBudgetTests(unittest.TestCase):
    def test_exact_rated_vref_does_not_provide_tolerance_margin(self):
        # A divider set for precisely 0.67 A nominal exceeds the rating with
        # high supply, high low-side resistor, low high-side/sense resistor.
        exact_high = 3.3 * 10000 / (.67 * 8 * .24) - 10000
        self.assertAlmostEqual(trip_current(3.3, exact_high, 10000, .24), .67)
        self.assertGreater(max(corner_currents(exact_high, 10000, .24)), .67)

    def test_candidate_covers_all_tolerance_corners(self):
        values = corner_currents(19600, 10000, .24)
        analytic_max = trip_current(3.465, 19600 * .99, 10000 * 1.01, .24 * .99, .05)
        self.assertEqual(len(values), 32)
        self.assertAlmostEqual(max(values), analytic_max)
        self.assertLess(max(values), .67)
        # This range guards against accidentally retaining the old 0.35 A
        # setting or confusing peak trip with full-step RMS phase current.
        self.assertGreater(trip_current(3.3, 19600, 10000, .24), .57)

    def test_copper_screen_is_conservative_with_thinner_internal_copper(self):
        external = ipc2221_width_mm(.67, 35, 30)
        internal = ipc2221_width_mm(.67, 17.5, 30, True)
        self.assertGreater(internal, external * 4)
        self.assertGreater(ipc2221_width_mm(1.0, 35, 30), external)

    def test_unknown_thermal_values_are_not_invented(self):
        result = report()
        self.assertIsNone(result['thermal_screen']['motor_copper_loss_w'])
        self.assertIsNone(result['thermal_screen']['junction_temperature_c'])
        self.assertFalse(result['manufacturing_release'])
        self.assertGreater(result['thermal_screen']['conduction_loss_multiplier_vs_v1_12_at_same_rds'], 3.5)


if __name__ == '__main__':
    unittest.main()
