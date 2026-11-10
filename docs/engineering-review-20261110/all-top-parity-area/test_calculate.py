import unittest

from calculate import area, calculate, polygon, verify, verify_baseline


class Tests(unittest.TestCase):
    def test_rectangle_and_reverse(self):
        points = [dict(x=0, y=0), dict(x=2, y=0), dict(x=2, y=3), dict(x=0, y=3)]
        self.assertEqual(area(points), 6)
        self.assertEqual(area(points[::-1]), 6)

    def test_bad_polygon(self):
        with self.assertRaises(ValueError):
            area([])

    def test_non_finite_coordinates(self):
        for value in (float("inf"), float("-inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                area([dict(x=0, y=0), dict(x=value, y=0), dict(x=1, y=2)])

    def test_missing_geometry(self):
        with self.assertRaises(ValueError):
            polygon("<chip />")

    def test_modified_snapshot_rejected(self):
        with self.assertRaises(ValueError):
            verify(b"modified", "0" * 40)

    def test_modified_baseline_rejected(self):
        with self.assertRaises(ValueError):
            verify_baseline(b"modified", "0" * 64)

    def test_exact_snapshots_and_totals(self):
        result = calculate()
        self.assertAlmostEqual(result["telemetry_added_mm2"], 79.96631878417439, places=8)
        self.assertAlmostEqual(result["parity_total_mm2"], 763.147730986022, places=6)
        self.assertGreater(result["parity_excess_mm2"], 0)


if __name__ == "__main__":
    unittest.main()
