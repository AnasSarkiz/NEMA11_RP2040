#!/usr/bin/env python3
"""Offline counterfactual screen, not native output, DRC or assembly approval."""
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BOARD = ROOT / 'boards/nema11-rp2040-two-layer--20261022-a1'
spec = importlib.util.spec_from_file_location('geometry_audit', BOARD / 'scripts/audit_placement_geometry.py')
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)


def transform(circuit, baseline, candidate):
    """Rigid quarter-turn and translation of genuine emitted copper/courtyards.

    Keeps all geometry dimensions/layers unchanged. Component records remain
    historical metadata; this is deliberately not usable as a generated circuit.
    """
    sources = {e['source_component_id']: e['name'] for e in circuit if e['type'] == 'source_component'}
    components = {e['pcb_component_id']: e for e in circuit if e['type'] == 'pcb_component'}
    if not set(candidate) <= set(baseline):
        raise ValueError('Unknown candidate component')
    out = copy.deepcopy(circuit)
    for e in out:
        if e['type'] not in {'pcb_smtpad', 'pcb_plated_hole', 'pcb_courtyard_outline'}:
            continue
        name = sources[components[e['pcb_component_id']]['source_component_id']]
        if name not in candidate:
            continue
        old, new = baseline[name], candidate[name]
        values = [new[k] for k in ('pcbX', 'pcbY', 'pcbRotation')]
        if not all(math.isfinite(v) for v in values) or new['layer'] != old['layer']:
            raise ValueError('Only finite, same-layer rigid transforms supported')
        rotation = new['pcbRotation'] - old['pcbRotation']
        if rotation % 90:
            raise ValueError('Only quarter turns supported')
        angle = math.radians(rotation)
        co, si = math.cos(angle), math.sin(angle)
        def point(q):
            x, y = q['x'] - old['pcbX'], q['y'] - old['pcbY']
            return {'x': new['pcbX'] + co*x - si*y, 'y': new['pcbY'] + si*x + co*y}
        if 'x' in e:
            e.update(point(e))
        for key in ('outline', 'points'):
            if key in e:
                e[key] = [point(q) for q in e[key]]
        if e['type'] == 'pcb_smtpad' and e.get('shape') in {'rect', 'pill'} and rotation:
            e['shape'] = 'rotated_' + e['shape']
        if e.get('shape') != 'circle':
            e['ccw_rotation'] = e.get('ccw_rotation', 0) + rotation
    return out


def run():
    fixture = json.loads((HERE / 'baseline-geometry.json').read_text())
    candidates = json.loads((HERE / 'candidates.json').read_text())
    baseline = fixture['placement']['placements']
    reports = {}
    for name, candidate in candidates.items():
        poses = {'placements': dict(baseline, **candidate)}
        report = geometry.audit(transform(fixture['geometry'], baseline, candidate), poses, fixture['placement'])
        # The historical-anchor gate is intentionally false for a changed USB.
        # The other fields quantify obstacles; none can bless a candidate.
        reports[name] = {
            'candidate_adopted': False,
            'native_build_run': False,
            'copper_AABB_pairs_below_015mm': report['conservative_pad_pairs_below_015mm'],
            'copper_min_edge_gap_mm': report['copper_min_conservative_edge_gap_mm'],
            'minimum_bolt_envelope_gap_mm': report['minimum_conservative_bolt_head_envelope_gap_mm'],
            'historical_frozen_anchors_unchanged': report['frozen_anchors_unchanged'],
        }
    return {'scope': 'Counterfactual rigid-transform AABB screen only; all candidates rejected, active placement unchanged. No routing, native build, assembly, tolerance or fabrication approval.',
            'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'baseline-geometry.json', HERE/'candidates.json', BOARD/'scripts/audit_placement_geometry.py')},
            'candidates': reports}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, allow_nan=False))
