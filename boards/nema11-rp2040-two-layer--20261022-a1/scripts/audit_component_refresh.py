"""Compare untouched new imports with baseline; no manufacturing approval."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

root = Path.cwd()
manifest = json.loads(Path('checks/import-refresh/fresh-imports.json').read_text())
baseline = json.loads(Path('checks/import-refresh/baseline.json').read_text())
baseline_hashes = {f['path']: f['sha256'] for f in baseline['files']}
prefix = subprocess.check_output(['git', 'rev-parse', '--show-prefix']).decode().strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(path, original_bytes=None):
    data = path.read_bytes() if original_bytes is None else original_bytes
    source = data.decode('utf8')
    pins = re.search(r'const pinLabels\s*=\s*(\{.*?\})\s*as const', source, re.S)
    labels = json.loads(re.sub(r'\b(pin\d+)\s*:', r'"\1":', pins[1])) if pins else None
    mpn = re.search(r'manufacturerPartNumber="([^"]+)"', source)
    values = {name: (m[1] if (m := re.search(r'\b' + name + r'="([^"]+)"', source)) else None) for name in ['resistance', 'capacitance', 'inductance']}
    pads = []
    for tag in re.findall(r'<(?:smtpad|platedhole)\b[^>]*>', source):
        hints = re.search(r'portHints=\{(\[.*?\])\}', tag)
        attrs = {key: value for key, value in re.findall(r'\b(\w+)="([^"]*)"', tag)}
        coordinates = {key: float(attrs.pop(key).removesuffix('mm')) for key in ['pcbX', 'pcbY'] if key in attrs}
        pads.append({'kind': re.match(r'<(\w+)', tag)[1], 'hints': json.loads(hints[1]) if hints else [], 'attrs': attrs, **coordinates})
    origin = re.search(r'modelOriginPosition:\s*\{([^}]+)\}', source)
    origin_values = {axis: float(value) for axis, value in re.findall(r'([xyz]):\s*([-+\d.eE]+)', origin[1])} if origin else None
    return {'mpn': mpn[1] if mpn else None, 'pin_labels': labels, 'values': values, 'pads': pads, 'origin': origin_values, 'holes': len(re.findall(r'<hole\b', source)), 'cutouts': len(re.findall(r'<cutout\b', source)), 'sha256': hashlib.sha256(data).hexdigest()}


results = []
for record in manifest['imports']:
    part = record['part']
    sources = [root / f['path'] for f in record['files'] if f['path'].endswith('.tsx')]
    old = [p for p in Path('imports').glob('*/*.tsx') if '"' + part + '"' in p.read_text()]
    item = {'part': part, 'import_exit_code': record['exit_code'], 'assets_present': record['required_assets_present'], 'full_component_approved': False}
    if len(sources) == len(old) == 1:
        old_data = subprocess.check_output(['git', 'show', baseline['commit'] + ':' + prefix + str(old[0])])
        assert hashlib.sha256(old_data).hexdigest() == baseline_hashes[str(old[0])]
        before, after = inspect(old[0], old_data), inspect(sources[0])
        # Electrical pads may be uniformly re-centered by the released importer.
        # All hints, types, dimensions and relative coordinates must remain equal.
        pad_map = len(before['pads']) == len(after['pads'])
        offsets = []
        for a, b in zip(before['pads'], after['pads']):
            pad_map &= all(a[k] == b[k] for k in ['kind', 'hints', 'attrs'])
            if all(k in a and k in b for k in ['pcbX', 'pcbY']):
                offsets.append((b['pcbX'] - a['pcbX'], b['pcbY'] - a['pcbY']))
            else:
                pad_map = False
        pad_map &= all(abs(x - offsets[0][0]) < 1e-6 and abs(y - offsets[0][1]) < 1e-6 for x, y in offsets) if offsets else False
        # Byte-identical source is direct proof even for polygon pads without pcbX/Y.
        pad_map = pad_map or before['sha256'] == after['sha256']
        model_matches = {}
        for ext in ['.obj', '.step']:
            previous = next(old[0].parent.glob('*' + ext))
            fresh = next((root / f['path'] for f in record['files'] if f['path'].endswith(ext)), None)
            model_matches[ext] = fresh is not None and baseline_hashes[str(previous)] == sha(fresh)
        item.update({'baseline_source': str(old[0]), 'fresh_source': str(sources[0].relative_to(root)), 'baseline_source_sha256': before['sha256'], 'fresh_source_sha256': after['sha256'], 'mpn_unchanged': before['mpn'] == after['mpn'], 'pin_labels_unchanged': before['pin_labels'] == after['pin_labels'], 'passive_values_unchanged': before['values'] == after['values'], 'electrical_pad_mapping_unchanged_up_to_translation': pad_map, 'pad_translation_mm': list(offsets[0]) if offsets else None, 'model_files_byte_equal': model_matches, 'model_origin_changed': before['origin'] != after['origin'], 'before_model_origin': before['origin'], 'after_model_origin': after['origin'], 'mechanical_hole_counts': {'before': before['holes'], 'after': after['holes']}, 'cutout_counts': {'before': before['cutouts'], 'after': after['cutouts']}})
    else:
        item['comparison_error'] = {'old_source_count': len(old), 'new_source_count': len(sources)}
    results.append(item)
report = {'baseline_commit': baseline['commit'], 'scope': 'Import integrity and baseline electrical mapping comparison only; all geometry, ratings and CAD poses still require review', 'parts': results, 'checked': len(results), 'expected': len(manifest['expected_parts']), 'all_imports_succeeded_with_assets': len(results) == len(manifest['expected_parts']) and all(x['import_exit_code'] == 0 and x['assets_present'] for x in results), 'all_electrical_mappings_and_values_unchanged': all(all(x.get(key, False) for key in ['mpn_unchanged', 'pin_labels_unchanged', 'passive_values_unchanged', 'electrical_pad_mapping_unchanged_up_to_translation']) for x in results), 'source_files_changed': sum(x.get('baseline_source_sha256') != x.get('fresh_source_sha256') for x in results), 'cad_origins_changed': sum(x.get('model_origin_changed', False) for x in results), 'full_bom_approved': False}
Path('checks/import-refresh/comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'parts'}, indent=2))
for item in results:
    if not all(item.get(key, False) for key in ['mpn_unchanged', 'pin_labels_unchanged', 'passive_values_unchanged', 'electrical_pad_mapping_unchanged_up_to_translation']):
        print('REVIEW', item['part'], {k: v for k, v in item.items() if k.endswith('unchanged') or k.endswith('translation') or k == 'comparison_error'})
