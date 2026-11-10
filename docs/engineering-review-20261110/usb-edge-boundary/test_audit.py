import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch
import audit


def circle(center=(0, 0), radius=0.5):
    return dict(shape="circle", x=center[0], y=center[1], radius=radius)


class GeometryTests(unittest.TestCase):
    polygon = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def test_segment_endpoints_and_duplicate_vertices(self):
        self.assertEqual(audit.segment_distance((3, 0), ((0, 0), (1, 0))), 2)
        self.assertEqual(audit.segment_distance((3, 0), ((1, 0), (1, 0))), 2)

    def test_exact_face_corner_and_overlap(self):
        self.assertEqual(audit.circle_polygon_gap(circle((2, 0)), self.polygon), 0.5)
        self.assertAlmostEqual(audit.circle_polygon_gap(circle((2, 2)), self.polygon), math.sqrt(2) - 0.5)
        for center_x in (0, 1, 1.5):
            self.assertEqual(audit.circle_polygon_gap(circle((center_x, 0)), self.polygon), 0)

    def test_polygon_winding_closure_and_repeated_points(self):
        polygon = [(-1, -1), (1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)]
        for points in (polygon, list(reversed(polygon))):
            self.assertEqual(audit.circle_polygon_gap(circle((2, 0)), points), 0.5)

    def test_unrotated_rectangle_translation(self):
        rectangle = dict(shape="rect", x=0, y=0, width=4, height=2)
        points = audit.polygon_points(rectangle, (10, 20))
        self.assertEqual(audit.circle_polygon_gap(circle((13, 20)), points), 0.5)
        self.assertEqual(audit.circle_polygon_gap(circle((10, 22)), points), 0.5)

    def test_rotation_and_unsupported_shapes_rejected(self):
        for pad in (dict(shape="pill"), dict(shape="rotated_rect"),
                    dict(shape="rect", x=0, y=0, width=4, height=2, ccw_rotation=90)):
            with self.subTest(pad=pad), self.assertRaises(ValueError):
                audit.polygon_points(pad)

    def test_malformed_polygon_and_rectangle_rejected(self):
        malformed = [None, {}, dict(shape="polygon"), dict(shape="polygon", points=None),
                     dict(shape="polygon", points=[{"x": 0, "y": 0}]),
                     dict(shape="polygon", points=[{"x": 0}]),
                     dict(shape="rect", x=0, y=0, width=0, height=2),
                     dict(shape="rect", x=0, y=0, width=-1, height=2),
                     dict(shape="rect", x=0, y=0, width="1", height=2)]
        for pad in malformed:
            with self.subTest(pad=pad), self.assertRaises(ValueError):
                audit.polygon_points(pad)
        for points in ([], [(0, 0), (1, 1), (2, 2)], [(0,), (1, 1), (2, 0)]):
            with self.subTest(points=points), self.assertRaises(ValueError):
                audit.circle_polygon_gap(circle(), points)

    def test_malformed_circle_rejected(self):
        for value in (None, {}, dict(shape="circle"), circle(radius=0), circle(radius=-1)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.circle_polygon_gap(value, self.polygon)

    def test_nonfinite_inputs_rejected(self):
        for number in (float("nan"), float("inf"), -float("inf"), True):
            with self.subTest(number=number):
                with self.assertRaises(ValueError):
                    audit.circle_polygon_gap(circle((number, 0)), self.polygon)
                with self.assertRaises(ValueError):
                    audit.circle_polygon_gap(circle(radius=number), self.polygon)
                with self.assertRaises(ValueError):
                    audit.polygon_points(dict(shape="rect", x=0, y=0, width=number, height=1))
                with self.assertRaises(ValueError):
                    audit.polygon_points(dict(shape="rect", x=0, y=0, width=1, height=1), (number, 0))
                with self.assertRaises(ValueError):
                    audit.segment_distance((number, 0), ((0, 0), (1, 1)))

    def test_stale_receipt_rejected(self):
        with patch.dict(audit.PINNED, {"index.circuit.tsx": "0" * 64}):
            with self.assertRaisesRegex(ValueError, "Stale investigation input"):
                audit.verify_inputs()


class NativeRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.audit()

    def test_copper_inside_courtyard_outside(self):
        for connector in self.result["connectors"].values():
            self.assertAlmostEqual(connector["courtyard_overrun"], 0.250021, places=9)
            self.assertAlmostEqual(connector["outward_copper_edge_gap"], 1.675871, places=9)
            for lower, upper in zip(*connector["copper_bounds"]):
                self.assertGreater(lower, -14)
                self.assertLess(upper, 14)

    def test_actual_inward_move_clearance_violations(self):
        expected = {"TP_BOOT": (0.2847692, 0.0347482, "polygon"),
                    "TP_BOOT_GND": (0.2848581, 0.0348371, "rect")}
        for pair in self.result["data_move_exact_distances"]:
            before, after, shape = expected[pair["target"]]
            moved = pair["dx"] < 0
            self.assertAlmostEqual(pair["gap"], after if moved else before, places=9)
            self.assertEqual(pair["usb_shape"], shape)
            self.assertEqual(pair["meets_clearance"], not moved)
            self.assertEqual(pair["gap"] >= 0.15, not moved)

    def test_saved_results_byte_identical(self):
        generated = json.dumps(self.result, indent=2) + "\n"
        self.assertEqual(generated, Path(__file__).with_name("results.json").read_text())


if __name__ == "__main__":
    unittest.main()
