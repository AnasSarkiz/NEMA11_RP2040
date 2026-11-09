#!/usr/bin/env python3
"""Read-only nominal OBJ Z-envelope audit, not a physical fit qualification."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def z_bounds(cad, layer, low, high, thickness):
    """Restricted analytic case checked against the official mesh loader."""
    if cad.get('model_board_normal_direction') or cad.get('size') or cad.get('model_unit_to_mm_scale_factor', 1) != 1:
        raise ValueError('Unsupported authored model orientation/fit/scale')
    rotation = cad['rotation']
    if rotation['x'] != 0 or rotation['y'] not in (0, 180):
        raise ValueError('Unsupported X/Y rotation')
    if (rotation['y'] == 180) != (layer == 'bottom'):
        raise ValueError('Layer/rotation mismatch')
    sign = -1 if layer == 'bottom' else 1
    if not math.isclose(cad['position']['z'], sign*thickness/2, abs_tol=1e-9):
        raise ValueError('Unexpected surface offset')
    origin = cad['model_origin_position']['z']
    values = [cad['position']['z'] + sign*(z-origin) for z in (low, high)]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Nonfinite geometry')
    return sorted(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board', type=Path, required=True)
    parser.add_argument('--official', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    board = args.board.resolve()
    native = board/'dist/index/circuit.json'
    raw = native.read_bytes()
    circuit = json.loads(raw)
    boards = [e for e in circuit if e['type'] == 'pcb_board']
    assert len(boards) == 1
    thickness = boards[0]['thickness']
    source = {e['source_component_id']: e for e in circuit if e['type'] == 'source_component'}
    pcb = {e['pcb_component_id']: e for e in circuit if e['type'] == 'pcb_component'}
    cad = [e for e in circuit if e['type'] == 'cad_component']
    fitted = {e['pcb_component_id'] for e in pcb.values() if not e.get('do_not_place')}
    assert {e['pcb_component_id'] for e in cad} == fitted
    official = {e['name']: e for e in json.loads(args.official.read_bytes())}
    output = []
    for e in cad:
        component, owner = pcb[e['pcb_component_id']], source[e['source_component_id']]
        url = e['model_obj_url']
        path = (board/url).resolve()
        if not path.is_relative_to(board/'imports') or path.suffix != '.obj':
            raise ValueError('Only local imported OBJ allowed')
        model_bytes = path.read_bytes()
        vertices = [list(map(float, line.split()[1:4])) for line in model_bytes.decode().splitlines() if line.startswith('v ')]
        if not vertices or any(len(v) != 3 or not all(math.isfinite(x) for x in v) for v in vertices):
            raise ValueError('Missing or malformed vertices')
        low = [min(v[k] for v in vertices) for k in range(3)]
        high = [max(v[k] for v in vertices) for k in range(3)]
        bounds = z_bounds(e, component['layer'], low[2], high[2], thickness)
        loaded = official[owner['name']]
        difference = max(abs(bounds[0]-loaded['min'][2]), abs(bounds[1]-loaded['max'][2]))
        if difference > 1e-8:
            raise ValueError('Official loaded model Z bounds disagree')
        output.append(dict(name=owner['name'], supplier_part_numbers=owner.get('supplier_part_numbers'),
            layer=component['layer'], raw_obj_bounds_mm=dict(min=low,max=high),
            model_origin_mm=e['model_origin_position'], native_world_z_bounds_mm=bounds,
            protrusion_below_pcb_bottom_mm=max(0, -thickness/2-bounds[0]),
            official_loader_difference_mm=difference,
            model_path=str(path.relative_to(board)), model_sha256=hashlib.sha256(model_bytes).hexdigest()))
    assert native.read_bytes() == raw
    output.sort(key=lambda e: e['protrusion_below_pcb_bottom_mm'], reverse=True)
    report = dict(scope='Nominal imported OBJ mesh envelope only; not manufacturer maximum dimensions, mating, motor geometry, tolerances, solder or insulation qualification.',
        native_sha256=hashlib.sha256(raw).hexdigest(), board_thickness_mm=thickness,
        fitted_models_checked=len(output), models_match_official_world_loader=True,
        official_loader='circuit-json-to-gltf 0.0.164 loadCadComponentMesh, Bun 1.4.4 file URL loading',
        max_model_protrusion_below_bottom_mm=output[0]['protrusion_below_pcb_bottom_mm'], components=output,
        physical_fit_approved=False, manufacturing_approved=False)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='components'},indent=2))


if __name__ == '__main__':
    main()
