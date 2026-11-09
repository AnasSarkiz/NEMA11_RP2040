"""Serialized, fail-closed verification. Reports do not approve fabrication."""
import fcntl
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('dist/index/circuit.json')
RECEIPT = Path('checks/native-build-status.json')
STATUS = Path('checks/milestone-status.json')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(root=ROOT):
    files = set()
    if (root / 'checks/import-manifest.json').is_file():
        files.add(root / 'checks/import-manifest.json')
    for folder in ('config', 'imports', 'scripts', 'tests', 'emitted-tests', 'references'):
        files.update(p for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    files.update(p for p in root.iterdir() if p.is_file() and (p.suffix in ('.json', '.tsx', '.ts', '.lock', '.lockb') or p.name == 'AGENTS.md'))
    return {str(p.relative_to(root)): digest(p) for p in sorted(files)}


def fresh_receipt(root=ROOT):
    try:
        receipt = json.loads((root / RECEIPT).read_text())
        return (receipt['fresh_output'] and receipt['inputs_before'] == receipt['inputs_after'] == fingerprint(root)
                and receipt['source_sha256'] == digest(root / 'index.circuit.tsx')
                and receipt['output_sha256'] == digest(root / OUTPUT))
    except (OSError, ValueError, KeyError):
        return False


def run(name, command):
    path = Path('checks') / (name + '.txt')
    with path.open('w') as log:
        try:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
            code = result.returncode
        except OSError as error:
            log.write(str(error) + '\n')
            code = 127
    print(f'{name}: exit {code}', flush=True)
    return {'command': command, 'exit_code': code, 'log': str(path)}


def write_status(phase, results, **extra):
    """Invalidate prior success before work; interruptions retain partial evidence."""
    report = {'passed': False, 'manufacturing_approved': False,
              'incomplete': True, 'phase': phase, 'results': results, **extra}
    temporary = STATUS.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(STATUS)


def main():
    import os
    os.chdir(ROOT)
    os.environ['PATH'] = str(ROOT / 'node_modules/.bin') + os.pathsep + os.environ.get('PATH', '')
    os.environ['XDG_CONFIG_HOME'] = str(ROOT / '.cache/config')
    os.environ['XDG_CACHE_HOME'] = str(ROOT / '.cache/xdg')
    Path('checks').mkdir(exist_ok=True)
    with Path('checks/milestone.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        results = {}
        def check(name, command):
            write_status('running:' + name, results)
            results[name] = run(name, command)
            write_status('finished:' + name, results)
            return results[name]['exit_code'] == 0
        # Invalidate old evidence even if a prerequisite fails.
        RECEIPT.unlink(missing_ok=True)
        write_status('starting', results)
        for name, command in [('format-check', ['npm', 'run', 'format:check']), ('typecheck', ['npm', 'run', 'typecheck']), ('prebuild-tests', ['python3', '-m', 'unittest', 'discover', '-s', 'tests', '-v'])]:
            if not check(name, command):
                write_status('prerequisite_failed', results, incomplete=False,
                             skipped='Build and dependent checks: prerequisite failed')
                return 1
        before = fingerprint()
        shutil.rmtree('dist/index', ignore_errors=False) if Path('dist/index').exists() else None
        started = time.time_ns()
        check('native-build', ['npm', 'run', 'build'])
        after = fingerprint()
        fresh = False
        if OUTPUT.exists():
            try:
                records = json.loads(OUTPUT.read_text())
                fresh = isinstance(records, list) and bool(records) and all(isinstance(x, dict) and 'type' in x for x in records)
            except (OSError, ValueError):
                pass
        receipt = {'source_sha256': before.get('index.circuit.tsx'), 'inputs_before': before, 'inputs_after': after, 'output_sha256': digest(OUTPUT) if OUTPUT.exists() else None, 'fresh_output': fresh and before == after, 'build_exit_code': results['native-build']['exit_code'], 'started_ns': started, 'finished_ns': time.time_ns(), 'build_passed': results['native-build']['exit_code'] == 0 and fresh and before == after}
        RECEIPT.write_text(json.dumps(receipt, indent=2) + '\n')
        if receipt['fresh_output']:
            check('emitted-tests', ['python3', '-m', 'unittest', 'discover', '-s', 'emitted-tests', '-v'])
            check('source-integrity', ['python3', 'scripts/verify_source.py'])
            check('independent-geometry', ['python3', 'scripts/audit_placement_geometry.py', '--baseline', 'references/electrical-placement-20261109/anchor-reference.json', '--output', 'checks/20261108-reconstruction/current-geometry-audit.json'])
            # Independent read-only native diagnostics use unique logs and no dist output.
            write_status('running:native-diagnostics', results)
            with ThreadPoolExecutor(max_workers=3) as pool:
                pending = {kind: pool.submit(run, 'check-' + kind, ['node_modules/.bin/tsci', 'check', kind, 'index.circuit.tsx'])
                           for kind in ('netlist', 'pin_specification', 'source', 'schematic-placement', 'placement')}
                for kind, future in pending.items():
                    results['check-' + kind] = future.result()
                    write_status('running:native-diagnostics', results)
            for kind in ('netlist', 'pin_specification', 'source'):
                check('strict-' + kind, ['python3', 'scripts/check_diagnostic_summary.py', 'checks/check-' + kind + '.txt', '--native-exit', str(results['check-' + kind]['exit_code']), '--output', 'checks/strict-' + kind + '.json'])
            check('strict-schematic', ['python3', 'scripts/check_schematic_findings.py', 'checks/check-schematic-placement.txt', '--native-exit', str(results['check-schematic-placement']['exit_code']), '--output', 'checks/strict-schematic.json'])
            check('export-schematic', ['npm', 'run', 'export:schematic-pdf'])
            check('export-pcb-views', ['node', 'scripts/export_pcb_views.mjs'])
        passed = receipt['build_passed'] and fresh_receipt() and all(x['exit_code'] == 0 for x in results.values())
        write_status('complete', results, passed=passed, incomplete=False,
                     dependent_checks_skipped=not receipt['fresh_output'])
        return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
