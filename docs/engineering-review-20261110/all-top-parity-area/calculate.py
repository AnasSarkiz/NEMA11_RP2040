"""Local courtyard-area screen; not a native build or physical-fit proof."""

import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TELEMETRY_PARTS = (
    "INA240A1PWR",
    "ERJL06KF50MV",
    "A_0402WGF1000TCE",
    "CL05B103KB5NNNC",
    "CL05B104KO5NNNC",
)


def area(points):
    if len(points) < 3:
        raise ValueError("Polygon needs at least three vertices")
    if any(not math.isfinite(point[axis]) for point in points for axis in ("x", "y")):
        raise ValueError("Polygon coordinates must be finite")
    edges = zip(points, points[1:] + points[:1])
    return abs(sum(p["x"] * q["y"] - q["x"] * p["y"] for p, q in edges)) / 2


def polygon(text):
    match = re.search(r'<courtyardoutline outline=\{(\[[\s\S]*?\])\}', text)
    if not match:
        raise ValueError("Missing exact courtyard polygon")
    return json.loads(match[1])


def verify(data, expected):
    actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if actual != expected:
        raise ValueError("Git blob mismatch: " + actual)


def verify_baseline(data, expected):
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("Archived NEMA11 baseline digest mismatch")


def calculate():
    provenance = json.loads((ROOT / "provenance.json").read_text())
    for source in provenance["sources"]:
        verify((ROOT / source["local"]).read_bytes(), source["git_blob_sha"])
    baseline = provenance["baseline"]
    verify_baseline((ROOT / baseline["source"]).read_bytes(), baseline["source_sha256"])
    areas = {
        name: area(polygon((ROOT / "sources" / (name + ".tsx")).read_text()))
        for name in TELEMETRY_PARTS
    }
    added = 2 * sum(areas.values())
    total = baseline["hypothetical_upright_mm2"] + added
    capacitors = areas["CL05B104KO5NNNC"] + area(
        polygon((ROOT / "sources/CL05A105KA5NQNC.tsx").read_text())
    )
    return {
        "per_part_mm2": areas,
        "telemetry_added_mm2": added,
        "telemetry_total_mm2": total,
        "telemetry_excess_mm2": total - baseline["usable_mm2"],
        "encoder_caps_mm2": capacitors,
        "parity_total_mm2": total + capacitors,
        "parity_excess_mm2": total + capacitors - baseline["usable_mm2"],
    }


if __name__ == "__main__":
    print(json.dumps(calculate(), indent=2))
