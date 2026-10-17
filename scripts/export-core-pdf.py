#!/usr/bin/env python3
"""Export the three native review sheets as a verified A4 vector PDF."""
import hashlib
import sys
from io import BytesIO
import json
from pathlib import Path
import cairosvg
from pypdf import PdfReader, PdfWriter

compact='--compact' in sys.argv
controller = '--controller' in sys.argv or compact
count = 6 if controller else 3
root = Path(__file__).resolve().parents[1] / ('artifacts/compact-controller' if compact else 'artifacts/controller' if controller else 'artifacts/rp2040-core')
writer = PdfWriter()
sizes = []
for n in range(1, count+1):
    source = root / f'schematic-a4-{n}.svg'
    reader = PdfReader(BytesIO(cairosvg.svg2pdf(bytestring=source.read_bytes())))
    assert len(reader.pages) == 1
    page = reader.pages[0]
    size = [float(page.mediabox.width) * 25.4 / 72, float(page.mediabox.height) * 25.4 / 72]
    assert abs(size[0] - 297) < .01 and abs(size[1] - 210) < .01, size
    writer.add_page(page)
    sizes.append(size)
target = root / 'schematic-a4.pdf'
with target.open('wb') as stream:
    writer.write(stream)
assert len(PdfReader(target).pages) == count
report = {'scope': 'full controller schematic review' if controller else 'subsystem schematic review only', 'page_count': count,
          'page_sizes_mm': sizes, 'pdf_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
          'schematic_sha256': hashlib.sha256((root / ('schematic.circuit.json' if controller else 'core-schematic.circuit.json')).read_bytes()).hexdigest(),
          'manufacturing_release': False}
(root / 'pdf-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
