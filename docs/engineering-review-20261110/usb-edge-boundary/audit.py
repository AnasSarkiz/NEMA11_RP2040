#!/usr/bin/env python3
"""Pinned read-only investigation; stdout only, never a DRC waiver.

Bounds reuse the board's conservative AABB helper. Exact gaps are circle versus
simple filled polygon or unrotated rectangle. Dimensions are millimetres.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOARD = ROOT / "boards/nema11-rp2040-two-layer--20261022-a1"
PINNED = {
    'index.circuit.tsx': 'e534b89873edec43ccdd36525f7566f7a63e1ff36d9e1778b2a6ebedb37199ce',
    'dist/index/circuit.json': '37e2f0f8123048bf3c87dbaed27447afeeebb32125d14c78fac18f444e827903',
    'scripts/audit_placement_geometry.py': 'f722d20a367b33fa372f0c42efe965c7097c0ebea4197c991bdc17c37782ae55',
    'config/requirements.json': '37df7df1b28430867702d6327f5c9a25148a7a24844936840fc8a64953207955',
    'config/placement.json': '164443f6acd85aaed9f1e0e49c2048a0ae7a2113b9420d07c7c5f66cc8808aae',
    'imports/TYPE_C_31_M_12/TYPE_C_31_M_12.tsx': 'f72ec6955f7f982441478d44f69e2f67961da1195766faefe651de29dd2b0cbd',
    'imports/TYPE_C_31_M_12/TYPE_C_31_M_12.obj': '9d7e957178f20137fdd5d62ae84281fe3b5bb3a44262f348d8e129b0a4182320',
    'imports/TYPE_C_31_M_12/TYPE_C_31_M_12.step': '3806dacd6082a75cfb24d3ba4b86b3d0c96213134c67e1385eb1599a89b2c461',
}


def verify_inputs():
    for relative_path, expected_hash in PINNED.items():
        actual_hash = hashlib.sha256((BOARD / relative_path).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ValueError(f"Stale investigation input: {relative_path}: {actual_hash}")


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Expected finite numeric coordinate or dimension")
    return value


def point_coordinates(point):
    if not isinstance(point, (tuple, list)) or len(point) != 2:
        raise ValueError("Expected a two-coordinate point")
    return tuple(finite_number(value) for value in point)


def segment_distance(point, segment):
    point_x, point_y = point_coordinates(point)
    if not isinstance(segment, (tuple, list)) or len(segment) != 2:
        raise ValueError("Expected two segment endpoints")
    start_x, start_y = point_coordinates(segment[0])
    end_x, end_y = point_coordinates(segment[1])
    delta_x, delta_y = end_x - start_x, end_y - start_y
    squared_length = delta_x * delta_x + delta_y * delta_y
    projection = ((point_x - start_x) * delta_x + (point_y - start_y) * delta_y) / squared_length if squared_length else 0
    fraction = max(0, min(1, projection))
    return math.hypot(point_x - start_x - fraction * delta_x, point_y - start_y - fraction * delta_y)


def validated_polygon(points):
    if not isinstance(points, (tuple, list)):
        raise ValueError("Expected polygon point sequence")
    coordinates = [point_coordinates(point) for point in points]
    if len(set(coordinates)) < 3:
        raise ValueError("Polygon needs three distinct vertices")
    edges = list(zip(coordinates, coordinates[1:] + coordinates[:1]))
    twice_area = sum(start[0] * end[1] - end[0] * start[1] for start, end in edges)
    if not math.isfinite(twice_area) or twice_area == 0:
        raise ValueError("Polygon has invalid or zero area")
    # Simple polygons are a documented input assumption, not a full topology check.
    return coordinates


def polygon_points(pad, translation=(0, 0)):
    if not isinstance(pad, dict):
        raise ValueError("Expected pad object")
    translate_x, translate_y = point_coordinates(translation)
    shape = pad.get("shape")
    if shape not in {"polygon", "rect"}:
        raise ValueError(f"Unsupported exact-distance shape: {shape}")
    rotation = finite_number(pad.get("ccw_rotation", 0))
    if rotation != 0:
        raise ValueError("Exact-distance helper requires unrotated emitted geometry")
    try:
        if shape == "polygon":
            points = [(point["x"], point["y"]) for point in pad["points"]]
        else:
            width, height = finite_number(pad["width"]), finite_number(pad["height"])
            center_x, center_y = finite_number(pad["x"]), finite_number(pad["y"])
            if width <= 0 or height <= 0:
                raise ValueError("Nonpositive rectangle size")
            points = [(center_x - width / 2, center_y - height / 2),
                      (center_x + width / 2, center_y - height / 2),
                      (center_x + width / 2, center_y + height / 2),
                      (center_x - width / 2, center_y + height / 2)]
    except (KeyError, TypeError) as error:
        raise ValueError("Malformed pad geometry") from error
    coordinates = validated_polygon(points)
    return validated_polygon([(x + translate_x, y + translate_y) for x, y in coordinates])


def circle_polygon_gap(circle, points):
    """Unsigned separation, zero for touching/overlap, not penetration depth.

    Polygon must be simple. Repeated/closing vertices are accepted.
    """
    if not isinstance(circle, dict) or circle.get("shape") != "circle":
        raise ValueError("Expected circle object")
    try:
        center_x, center_y = finite_number(circle["x"]), finite_number(circle["y"])
        radius = finite_number(circle["radius"])
    except KeyError as error:
        raise ValueError("Malformed circle geometry") from error
    if radius <= 0:
        raise ValueError("Expected positive-radius circle")
    coordinates = validated_polygon(points)
    edges = list(zip(coordinates, coordinates[1:] + coordinates[:1]))
    inside = False
    for (start_x, start_y), (end_x, end_y) in edges:
        if (start_y > center_y) != (end_y > center_y):
            crossing_x = start_x + (center_y - start_y) * (end_x - start_x) / (end_y - start_y)
            if center_x < crossing_x:
                inside = not inside
    distance = min(segment_distance((center_x, center_y), edge) for edge in edges)
    return 0.0 if inside else max(0.0, distance - radius)


def audit():
    verify_inputs()
    specification = importlib.util.spec_from_file_location("board_geometry", BOARD / "scripts/audit_placement_geometry.py")
    geometry_helper = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(geometry_helper)
    circuit = json.loads((BOARD / "dist/index/circuit.json").read_text())
    source_names = {element["source_component_id"]: element["name"]
                    for element in circuit if element["type"] == "source_component"}
    component_names = {element["pcb_component_id"]: source_names[element["source_component_id"]]
                       for element in circuit if element["type"] == "pcb_component"}
    board, = [element for element in circuit if element["type"] == "pcb_board"]
    requirements = json.loads((BOARD / "config/requirements.json").read_text())
    minimum_clearance = requirements["minimum_copper_clearance_mm"]
    result = {"input_sha256": PINNED, "units": "mm", "minimum_copper_clearance": minimum_clearance, "connectors": {}}
    for name, outward_axis in [("J_PD", 1), ("J_DATA", 0)]:
        own_elements = [element for element in circuit if component_names.get(element.get("pcb_component_id")) == name]
        courtyard, = [element for element in own_elements if element["type"] == "pcb_courtyard_outline"]
        copper = [element for element in own_elements if element["type"] in {"pcb_smtpad", "pcb_plated_hole"}]
        bounds = [geometry_helper.geometry_bounds(element) for element in copper]
        copper_bounds = [[min(bound[0][axis] for bound in bounds) for axis in (0, 1)],
                         [max(bound[1][axis] for bound in bounds) for axis in (0, 1)]]
        courtyard_bounds = geometry_helper.geometry_bounds(courtyard)
        edge = board["center"]["xy"[outward_axis]] + board["height" if outward_axis else "width"] / 2
        overrun = courtyard_bounds[1][outward_axis] - edge
        result["connectors"][name] = {
            "copper_bounds": copper_bounds, "courtyard_bounds": courtyard_bounds,
            "outward_board_edge": edge, "outward_copper_edge_gap": edge - copper_bounds[1][outward_axis],
            "courtyard_overrun": overrun,
        }
        if name != "J_DATA":
            continue
        pairs = []
        for target in ("TP_BOOT", "TP_BOOT_GND"):
            circle, = [element for element in circuit if element["type"] == "pcb_smtpad"
                       and component_names.get(element["pcb_component_id"]) == target]
            candidates = [element for element in copper if element["type"] == "pcb_smtpad"
                          and element["layer"] == circle["layer"]]
            for translate_x in (0, -overrun):
                distances = [(circle_polygon_gap(circle, polygon_points(element, (translate_x, 0))),
                              element["pcb_smtpad_id"], element["shape"]) for element in candidates]
                distance, pad_id, shape = min(distances)
                pairs.append({"target": target, "usb_pad": pad_id, "usb_shape": shape,
                              "dx": translate_x, "gap": distance, "meets_clearance": distance >= minimum_clearance})
        result["data_move_exact_distances"] = pairs
    return result


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
