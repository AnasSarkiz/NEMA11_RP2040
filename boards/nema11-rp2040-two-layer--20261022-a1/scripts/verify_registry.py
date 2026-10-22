"""Compare public registry contents with local source/assets; never prints credentials."""
import base64
import concurrent.futures
import hashlib
import json
import urllib.request
import urllib.error
import time
import sys
from pathlib import Path

NAME = 'AnasSarkiz/NEMA11_RP2040_Compact_Prototype'
VERSION = '0.6.2-issues-review-wip'
TARGET = NAME + '@' + VERSION
BASE = 'https://registry-api.tscircuit.com/'


def post(endpoint, payload):
    request = urllib.request.Request(BASE + endpoint, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code not in [429, 502, 503, 504] or attempt == 3:
                raise
            time.sleep(1 + attempt)
        except (OSError, TimeoutError) as error:
            if attempt == 3:
                raise
            time.sleep(1 + attempt)


def local_files():
    return sorted(p for p in Path('.').rglob('*') if p.is_file() and not any(part.startswith('.') or part in ['node_modules', '__pycache__'] for part in p.parts) and str(p) not in ['checks/registry-verification.json', 'checks/publication-status.json'])


def compare(path):
    data = path.read_bytes()
    try:
        file = post('package_files/get', {'package_name_with_version': TARGET, 'file_path': str(path)})['package_file']
        if not file.get('is_text', True):
            with urllib.request.urlopen(BASE + 'package_files/download?package_file_id=' + file['package_file_id'], timeout=20) as response:
                remote = response.read()
        else:
            remote = file.get('content_text', '').encode()
        return {'file_path': str(path), 'byte_equal': remote == data, 'local_sha256': hashlib.sha256(data).hexdigest(), 'remote_sha256': hashlib.sha256(remote).hexdigest(), 'bytes': len(data)}
    except Exception as error:
        return {'file_path': str(path), 'byte_equal': False, 'error_type': type(error).__name__, 'http_status': getattr(error, 'code', None)}


if __name__ == '__main__':
    paths = local_files()
    prior = {}
    receipt = Path('checks/registry-verification.json')
    if '--retry-unmatched' in sys.argv and receipt.exists():
        previous = json.loads(receipt.read_text())
        if previous.get('version') == VERSION:
            prior = {x['file_path']: x for x in previous['files'] if x['byte_equal']}
    partial = Path('.cache/publication/' + VERSION + '-verification-file-results.json')
    if '--retry-unmatched' in sys.argv and partial.exists():
        prior.update({x['file_path']: x for x in json.loads(partial.read_text()) if x['byte_equal']})
    preserved = [prior[str(p)] for p in paths if str(p) in prior and hashlib.sha256(p.read_bytes()).hexdigest() == prior[str(p)]['local_sha256']]
    remaining = [p for p in paths if str(p) not in {x['file_path'] for x in preserved}]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = sorted(preserved + list(executor.map(compare, remaining)), key=lambda x: x['file_path'])
    Path('.cache/publication/' + VERSION + '-verification-file-results.json').write_text(json.dumps(results, indent=2) + '\n')
    public = post('packages/get', {'name': NAME})['package'].get('is_private') is False
    release = post('package_releases/get', {'package_name_with_version': TARGET})['package_release']
    report = {'package': NAME, 'version': VERSION, 'public': public, 'files': results, 'matched': sum(x['byte_equal'] for x in results), 'checked': len(results), 'release': {k: release.get(k) for k in ['package_release_id', 'version', 'is_latest', 'ready_to_build', 'build_status', 'build_error']}, 'manufacturing_approved': False, 'excludes': ['dot files/directories', 'node_modules', '__pycache__', 'registry-verification.json and publication-status.json receipts, verified separately']}
    Path('checks/registry-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))
    for file in results:
        if not file['byte_equal']:
            print('MISMATCH', file['file_path'], file.get('error_type', 'different bytes'))
    raise SystemExit(not public or any(not x['byte_equal'] for x in results))
