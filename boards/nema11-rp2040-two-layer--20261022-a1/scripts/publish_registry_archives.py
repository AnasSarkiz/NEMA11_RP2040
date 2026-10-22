"""Publish exact local bytes via the registry archive API used by tsci push.

Use bounded archives because a single complete model archive exceeded the API
request-size limit in prior native CLI pushes. Never edits generated circuit JSON.
"""
import argparse
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version', required=True)
parser.add_argument('--files', nargs='*')
parser.add_argument('--request-preview', action='store_true')
args = parser.parse_args()
ROOT = Path.cwd()
NAME = 'AnasSarkiz/NEMA11_RP2040_Compact_Prototype'
TARGET = NAME + '@' + args.version
BASE = 'https://registry-api.tscircuit.com/'
config_home = Path(os.environ.get('XDG_CONFIG_HOME', '/workspace/.config'))
config = json.loads((config_home / 'tscircuit-nodejs/config.json').read_text())
token = config.get('sessionToken')
if not token:
    raise SystemExit('Existing CLI authentication unavailable; no credential printed')


def post(endpoint, payload, auth=False):
    headers = {'Content-Type': 'application/json'}
    if auth:
        headers['Authorization'] = 'Bearer ' + token
    request = urllib.request.Request(BASE + endpoint, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def remote_bytes(path):
    file = post('package_files/get', {'package_name_with_version': TARGET, 'file_path': path})['package_file']
    if file.get('is_text'):
        return file['content_text'].encode()
    with urllib.request.urlopen(BASE + 'package_files/download?package_file_id=' + file['package_file_id'], timeout=45) as response:
        return response.read()


def upload(paths):
    files = []
    for path in paths:
        data = path.read_bytes()
        binary = path.suffix.lower() in ['.obj', '.glb', '.gltf', '.stl', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.zip', '.gz', '.tar'] or b'\x00' in data[:8192]
        if not binary:
            try:
                data.decode('utf8')
            except UnicodeDecodeError:
                binary = True
        files.append({'file_path': str(path), 'content_base64': base64.b64encode(data).decode()} if binary else {'file_path': str(path), 'content_text': data.decode('utf8')})
    archive = gzip.compress(json.dumps({'files': files}, separators=(',', ':')).encode(), compresslevel=9)
    try:
        post('package_files/upload_archive', {'package_name_with_version': TARGET, 'archive_base64': base64.b64encode(archive).decode()}, auth=True)
    except urllib.error.HTTPError as error:
        if error.code == 413 and len(paths) > 1:
            midpoint = len(paths) // 2
            upload(paths[:midpoint])
            upload(paths[midpoint:])
            return
        if error.code >= 500:
            # A server error can follow a committed upload. Verify before retrying.
            try:
                verified = all(remote_bytes(str(p)) == p.read_bytes() for p in paths)
            except Exception:
                verified = False
            if verified:
                print('Verified uncertain archive outcome:', len(paths), 'files', flush=True)
                return
        print('Archive upload blocked:', error.code, 'paths', [str(p) for p in paths], flush=True)
        raise SystemExit(1)
    print('Uploaded archive:', len(paths), 'files;', len(archive), 'compressed bytes', flush=True)


package = post('packages/get', {'name': NAME})['package']
assert package.get('is_private') is False, 'Existing destination must be public'
try:
    release = post('package_releases/get', {'package_name_with_version': TARGET})['package_release']
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise
    post('package_releases/create', {'package_name_with_version': TARGET}, auth=True)
    print('Created version in existing package:', TARGET, flush=True)
if args.files:
    paths = [Path(p) for p in args.files]
else:
    paths = sorted(p for p in Path('.').rglob('*') if p.is_file() and not any(x.startswith('.') or x in ['node_modules', '__pycache__'] for x in p.parts) and str(p) not in ['checks/registry-verification.json', 'checks/publication-status.json'])
    assert Path('dist/index/circuit.json') in paths
batch, size = [], 0
for path in paths:
    assert path.is_file() and not any(x in ['node_modules', '__pycache__', '.cache'] or x.startswith('.env') for x in path.parts)
    if batch and size + path.stat().st_size > 3 * 1024 * 1024:
        upload(batch)
        batch, size = [], 0
    batch.append(path)
    size += path.stat().st_size
if batch:
    upload(batch)
if args.request_preview:
    post('package_releases/update', {'package_name_with_version': TARGET, 'ready_to_build': True}, auth=True)
    print('Requested registry preview build; not fabrication approval', flush=True)
print('Archive upload complete:', TARGET, flush=True)
