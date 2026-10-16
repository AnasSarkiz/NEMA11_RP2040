#!/usr/bin/env python3
"""Inspect original supplier STEP solids without substituting model geometry."""
import hashlib
import json
from pathlib import Path
import cadquery as cq

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'artifacts/rp2040-core/supplier-provenance.json').read_text())
expected = {e['path']: e['sha256'] for e in manifest['files']}
parts = []
for relative in sorted(p for p in expected if p.endswith('.step')):
    path = root / relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected[relative], relative
    shape = cq.importers.importStep(str(path)).val()
    bounds = shape.BoundingBox()
    assert shape.isValid() and shape.Volume() > 0, relative
    parts.append({'part': path.parent.name, 'valid': True,
                  'bounds_mm': [bounds.xmin, bounds.ymin, bounds.zmin,
                                bounds.xmax, bounds.ymax, bounds.zmax],
                  'overall_size_mm': [bounds.xlen, bounds.ylen, bounds.zlen],
                  'solid_volume_mm3': shape.Volume()})
assert len(parts) == 9
report = {'scope': 'raw supplier STEP solid and bounds inspection only; not full assembly clearance qualification',
          'parts': parts, 'manufacturer_tolerance_envelopes_verified': False,
          'manufacturing_release': False}
(root / 'artifacts/rp2040-core/supplier-STEP-inspection.json').write_text(json.dumps(report, indent=2) + '\n')
print('Imported and inspected nine unchanged supplier STEP models; all are valid solids.')
