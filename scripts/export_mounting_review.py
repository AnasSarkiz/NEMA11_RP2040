#!/usr/bin/env python3
"""Draw the checked PCB mounts separately from the verified motor front threads.

This is a dimensioned review drawing, not a toleranced fabrication drawing.
It reads the actual routed native PCB and retains all release limitations.
"""
import datetime
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from pypdf import PdfReader
from verify_four_mounts import check_mounts

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/requirements/mounting-review"
OUT.mkdir(exist_ok=True)
paths = ["artifacts/compact-six-layer/board.circuit.json",
         "config/compact-four-mounts.json", "artifacts/requirements/motor-originals.json",
         "artifacts/compact-six-layer/milestone-verification.json"]
board, config, motor, milestone = [json.loads((ROOT / path).read_text()) for path in paths]
assert not check_mounts(board, config)
native_board = next(r for r in board if r["type"] == "pcb_board")
assert native_board["num_layers"] == 6
assert [native_board["width"], native_board["height"]] == config["PCB_outline_mm"] == [28, 28]
assert milestone["circuit_sha256"] == hashlib.sha256((ROOT/paths[0]).read_bytes()).hexdigest()
assert all(milestone[k] == 0 for k in ["native_DRC_errors", "physical_opens", "physical_shorts"])
assert milestone["fitted_components_top"] == 76 and not milestone["manufacturing_release"]
assert config["motor_attachment"]["verified_thread"] == "M2.5"
assert config["motor_attachment"]["pitch_mm"] == 23
assert config["motor_attachment"]["pitch_tolerance_mm"] == .15
assert config["motor_attachment"]["minimum_thread_depth_mm"] == 3.5
names = {r["name"] for r in board if r["type"] == "source_component"}
assert not names.intersection(config["omitted_components"])
assert not motor["rear_mounting_inferred"] and not motor["rear_shaft_inferred"]
extent = max(abs(m[axis]) + m["diameter"] / 2 for m in config["mounts"] for axis in ["x", "y"])
web = config["PCB_outline_mm"][0] / 2 - extent
reference = config["reference"]
old_extent = reference["PCB_hole_pitch_mm"] / 2 + reference["PCB_hole_diameter_mm"] / 2
frame = config["assembly_frame_maximum_mm"][0]
assert abs(web - .6) < 1e-9 and old_extent > frame / 2

plt.rcParams.update({"font.size": 8, "svg.hashsalt": "nema11-four-mount-review",
                     "svg.fonttype": "none", "pdf.fonttype": 42})
fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4), facecolor="white")
fig.text(.06, .945, "NEMA11 RP2040 — four mounting holes", fontsize=17, weight="bold")
fig.text(.06, .913, "Dimensioned comparison · millimetres · centre datums · review only · A4 landscape", fontsize=9)
blue, grey, red = "#176499", "#777777", "#ae253b"

def setup(left, title):
    ax = fig.add_axes([left, .365, .28, .505], aspect="equal")
    ax.set_xlim(-19, 19); ax.set_ylim(-19, 19); ax.axis("off")
    ax.set_title(title, fontsize=10, weight="bold", pad=10)
    ax.add_patch(Rectangle((-frame/2, -frame/2), frame, frame,
                           fill=False, edgecolor=blue, linestyle="--", linewidth=1))
    ax.plot([-1, 1], [0, 0], color=grey, linewidth=.5)
    ax.plot([0, 0], [-1, 1], color=grey, linewidth=.5)
    return ax

def pitch(ax, half, label):
    y = -17.4
    for x in [-half, half]:
        ax.plot([x, x], [-half, y-.7], color=grey, linewidth=.5)
    ax.annotate("", xy=(-half, y), xytext=(half, y),
                arrowprops={"arrowstyle": "<->", "color": "black", "lw": .7})
    ax.text(0, y+.4, label, ha="center", va="bottom", fontsize=8,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})

ax = setup(.045, "Reference NEMA14 v1.13.0")
ax.add_patch(Rectangle((-17.5, -17.5), 35, 35, fill=False, edgecolor=grey, linewidth=.7))
for x, y in itertools.product([-13, 13], repeat=2):
    ax.add_patch(Circle((x, y), 3.2, fill=False, edgecolor=red, linestyle=":", linewidth=.8))
    ax.add_patch(Circle((x, y), 1.6, fill=False, edgecolor="black", linewidth=1))
pitch(ax, 13, "26 pitch in X and Y")
fig.text(.185, .325, "4 × Ø3.2 holes; Ø6.4 head exclusions\n35 × 35 reference PCB\nHole bounds exceed frame by 0.45 per side", ha="center", linespacing=1.5)

ax = setup(.36, "Current native NEMA11 PCB")
ax.add_patch(Rectangle((-14, -14), 28, 28, fill=False, edgecolor="black", linewidth=1.1))
for m in config["mounts"]:
    ax.add_patch(Circle((m["x"], m["y"]), m["radius"], fill=False, edgecolor=red, linestyle=":", linewidth=.9))
    ax.add_patch(Circle((m["x"], m["y"]), m["diameter"]/2, fill=False, edgecolor="black", linewidth=1.1))
pitch(ax, 12.5, "25 pitch in X and Y")
fig.text(.50, .325, "4 × Ø1.8 NPTH; Ø3.2 head exclusions on all 6 layers\n28 × 28 PCB; 0.60 nominal hole-to-edge web\nCandidate M1.6 screws: maximum head Ø3.0", ha="center", linespacing=1.5)

ax = setup(.675, "OEM motor — FRONT face only")
for x, y in itertools.product([-11.5, 11.5], repeat=2):
    ax.add_patch(Circle((x, y), 1.25, fill=False, edgecolor="black", linewidth=1.1))
    ax.plot([x-1.6, x+1.6], [y, y], color=grey, linewidth=.5)
    ax.plot([x, x], [y-1.6, y+1.6], color=grey, linewidth=.5)
pitch(ax, 11.5, "23 ±0.15 pitch in X and Y")
fig.text(.815, .325, "4 × M2.5 FRONT threads; depth 3.5 MIN\n28.3 MAX frame; 33 MAX body length\nBounding frame shown; corner profile is not specified", ha="center", linespacing=1.5)

fig.text(.06, .242, "Blue dashed square: the same 28.3 × 28.3 assembly limit in every view. Views are drawn at the same scale.", color=blue)
notes = [
    "The PCB holes attach to a separate front-anchored carrier proposal. No motor rear holes or rear shaft are assumed.",
    "The complete buzzer circuit is omitted; GPIO16 is explicitly NC. All 76 fitted electrical components remain on top.",
    "Actual native PCB mount positions and six-layer exclusions are checked. This drawing omits component placement and tool envelopes.",
    "Dimensions are nominal unless the OEM limit is stated. Fasteners, carrier strength, centring and manufacturing tolerances remain unqualified.",
    "NOT A FABRICATION RELEASE. Current copper checks: 0 DRC errors, 0 opens, 0 shorts; remaining release requirements still apply.",
]
for i, text in enumerate(notes):
    fig.text(.06, .207 - i*.026, text, fontsize=8)
sha = hashlib.sha256((ROOT / paths[0]).read_bytes()).hexdigest()
fig.text(.06, .04, "Native PCB SHA256 " + sha, fontsize=7, color=grey)
fig.text(.94, .04, "A0071 rev 2 · 11HS12-0674S", fontsize=7, color=grey, ha="right")
fixed = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
fig.savefig(OUT / "four-mount-comparison.pdf", metadata={"CreationDate": fixed, "ModDate": fixed, "Title": "NEMA11 four-mount review — NOT FOR FABRICATION"})
fig.savefig(OUT / "four-mount-comparison.svg", metadata={"Date": fixed.isoformat()})
fig.savefig(OUT / "four-mount-comparison.png", dpi=160)
plt.close(fig)
pdf = PdfReader(OUT / "four-mount-comparison.pdf")
assert len(pdf.pages) == 1
paper_mm = [float(pdf.pages[0].mediabox.width)*25.4/72,
            float(pdf.pages[0].mediabox.height)*25.4/72]
assert max(abs(actual-wanted) for actual, wanted in zip(paper_mm, [297, 210])) < .01
report = dict(scope="Actual native PCB mount geometry and nominal dimensional comparison only",
              circuit_sha256=sha, PCB_holes=4, PCB_hole_pitch_mm=25, PCB_hole_diameter_mm=1.8,
              head_exclusion_layers=6, nominal_hole_edge_web_mm=round(web, 6),
              reference_hole_bounds_exceed_28_3_frame_per_side_mm=round(old_extent-frame/2, 6),
              motor_front_thread="M2.5", motor_front_pitch_mm=23, motor_front_pitch_tolerance_mm=.15,
              motor_front_minimum_thread_depth_mm=3.5, rear_threads_or_shaft_assumed=False,
              native_mount_geometry_pass=True, fasteners_carrier_and_maximum_tolerances_qualified=False,
              PDF_pages=1, PDF_paper_mm=[round(v, 3) for v in paper_mm],
              manufacturing_release=False,
              inputs=[dict(path=p, sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
              drawings=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(OUT.glob("four-mount-comparison.*"))])
(OUT / "verification.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k not in ["inputs", "drawings"]}))
