"""Fresh supported imports into a candidate tree; original components are untouched."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
assert Path.cwd() == ROOT, 'Run from the board task directory'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--resume', action='store_true')
args = parser.parse_args()
versions = json.loads((ROOT / 'checks/import-refresh/npm-versions.json').read_text())
for package in ['@tscircuit/cli', 'tscircuit']:
    installed = json.loads((ROOT / 'node_modules' / package / 'package.json').read_text())['version']
    assert installed == versions[package]['version'], f'{package}: expected new version, installed {installed}'
plan = json.loads((ROOT / 'config/component-plan.json').read_text())
parts = sorted(set(plan['components'].values()) | set(plan.get('excluded_parts', {})))
# Check the known defective part first, but continue independent imports on failures.
parts.remove('C5815189')
parts.insert(0, 'C5815189')
base = ROOT / '.cache/import-refresh/candidate'
base.mkdir(parents=True, exist_ok=True)
logdir = ROOT / '.cache/import-refresh/logs'
logdir.mkdir(parents=True, exist_ok=True)
manifest_path = ROOT / 'checks/import-refresh/fresh-imports.json'
prior = {}
if args.resume and manifest_path.exists():
    prior = {x['part']: x for x in json.loads(manifest_path.read_text())['imports']}
manifest = []
env = dict(os.environ, PATH=str(ROOT / 'node_modules/.bin') + os.pathsep + os.environ['PATH'])
for part in parts:
    previous = prior.get(part)
    if previous and previous['exit_code'] == 0 and all((ROOT / f['path']).exists() and hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'] for f in previous['files']):
        manifest.append(previous)
        print('Resumed verified new-version import', part, flush=True)
        continue
    destination = base / part
    destination.mkdir(exist_ok=True)
    command = [str(ROOT / 'node_modules/.bin/tscircuit-cli'), 'import', '--jlcpcb', '--download', '--use-exact-footprint', part]
    started = time.monotonic()
    log = logdir / (part + '.txt')
    with log.open('wb') as output:
        result = subprocess.run(command, cwd=destination, env=env, stdout=output, stderr=subprocess.STDOUT, timeout=300)
    files = [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in sorted((destination / 'imports').rglob('*')) if p.is_file()]
    record = {'part': part, 'command': ['tscircuit-cli'] + command[1:], 'cwd': str(destination.relative_to(ROOT)), 'exit_code': result.returncode, 'elapsed_seconds': round(time.monotonic() - started, 2), 'files': files, 'tool_versions': versions, 'definitions_unmodified': True, 'component_approved': False}
    sources = [ROOT / f['path'] for f in files if f['path'].endswith('.tsx')]
    if len(sources) == 1:
        exported = re.search(r'export const (\w+)\s*=', sources[0].read_text())
        record['exported_symbol'] = exported[1] if exported else None
    record['required_assets_present'] = all(any(f['path'].endswith(ext) for f in files) for ext in ['.tsx', '.obj', '.step'])
    manifest.append(record)
    manifest_path.write_text(json.dumps({'imports': manifest, 'expected_parts': parts, 'old_imports_modified': False}, indent=2) + '\n')
    print('Fresh import', part, 'exit', result.returncode, 'files', len(files), flush=True)
print('Finished', len(manifest), 'of', len(parts), 'imports; failures', sum(x['exit_code'] != 0 or not x['required_assets_present'] for x in manifest), flush=True)
raise SystemExit(any(x['exit_code'] != 0 or not x['required_assets_present'] for x in manifest))
