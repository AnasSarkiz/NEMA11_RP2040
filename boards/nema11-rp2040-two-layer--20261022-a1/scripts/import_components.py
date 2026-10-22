#!/usr/bin/env python3
"""Run the supported importer; never author, modify or repair a component."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
assert Path.cwd() == ROOT, 'Run only from this task board directory'
plan = json.loads((ROOT / 'config/component-plan.json').read_text())
env = dict(os.environ)
env['PATH'] = str(ROOT / 'node_modules/.bin') + os.pathsep + env['PATH']
manifest = []
for part in sorted(set(plan['components'].values())):
    matches = [p for p in (ROOT / 'imports').glob('*/*.tsx') if '"'+part+'"' in p.read_text()]
    command = ['tsci', 'import', '--jlcpcb', '--download', '--use-exact-footprint', part]
    if not matches:
        with (ROOT / 'checks' / f'import-{part}.txt').open('w') as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            report = dict(status='blocked', part=part, command=command, exit_code=result.returncode,
                          stage='JLCPCB import feasibility; schematic/BOM/placement dependent work blocked',
                          log=f'checks/import-{part}.txt', custom_workaround_used=False)
            (ROOT / 'checks/import-blocker.json').write_text(json.dumps(report, indent=2)+'\n')
            print(json.dumps(report), flush=True)
            raise SystemExit(1)
        matches = [p for p in (ROOT / 'imports').glob('*/*.tsx') if '"'+part+'"' in p.read_text()]
    assert len(matches) == 1, (part, matches)
    source = matches[0]
    text = source.read_text()
    exported = re.search(r'export const (\w+)\s*=', text)
    assets = list(source.parent.iterdir())
    missing = [ext for ext in ['.obj', '.step'] if not any(p.suffix == ext for p in assets)]
    if missing:
        (ROOT / 'checks/import-blocker.json').write_text(json.dumps(dict(status='blocked', part=part, missing_supplier_assets=missing, custom_workaround_used=False), indent=2)+'\n')
        raise SystemExit('Missing original supplier models for '+part)
    manifest.append(dict(part=part, exported_symbol=exported[1], command=command,
                         files=[dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size) for p in sorted(assets) if p.is_file()],
                         definitions_symbols_footprints_and_models_unmodified=True,
                         full_component_approval=False))
    (ROOT / 'checks/import-manifest.json').write_text(json.dumps(dict(imports=manifest), indent=2)+'\n')
    print('Imported unmodified', part, exported[1], flush=True)
