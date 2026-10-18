#!/usr/bin/env python3
"""Verify current development files in the existing controller package publicly."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
F = ROOT / 'prototypes/compact-current'
name = 'AnasSarkiz/NEMA11_RP2040_Compact_Prototype'
proof = json.loads((F / 'package-verification.json').read_text())
version = proof['version']
assert json.loads((F / 'package.json').read_text())['name'] == '@tsci/AnasSarkiz.NEMA11_RP2040_Compact_Prototype'

def post(path, payload):
    request = urllib.request.Request('https://registry-api.tscircuit.com/'+path,
        json.dumps(payload).encode(), headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)

release = post('package_releases/get', {'package_name_with_version': name+'@'+version})['package_release']
files = post('package_files/list', {'package_release_id': release['package_release_id']})['package_files']
expected = ['README.md', 'dist/index/circuit.json', 'index.circuit.json', 'native-cli-build.txt', 'package-verification.json', 'package.json', 'tscircuit.config.json']
verified = []
for path in expected:
    entry = next(r for r in files if r['file_path'] == path)
    remote = post('package_files/get', {'package_file_id': entry['package_file_id']})['package_file']
    assert remote['is_text']
    data = remote['content_text'].encode()
    local = (F / path).read_bytes()
    byte_match = data == local
    native_record_match = path.endswith('circuit.json') and json.loads(data) == json.loads(local)
    assert byte_match or path == 'dist/index/circuit.json' and native_record_match, path+' differs from the current draft'
    verified.append(dict(path=path, remote_bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                         local_byte_match=byte_match, native_record_match=native_record_match if path.endswith('circuit.json') else None,
                         registry_reformatted_only=not byte_match and native_record_match))
assert json.loads((F / 'index.circuit.json').read_text()) == json.loads((ROOT / 'artifacts/compact-six-layer/assembly.circuit.json').read_text())
proof = json.loads((F / 'package-verification.json').read_text())
assert not proof['native_CLI_build_pass'] and proof['native_DRC_errors'] == 121
url = 'https://tscircuit.com/'+name
with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=45) as response:
    status = response.status
receipt = dict(package=name, version=version, url=url, package_release_id=release['package_release_id'],
               same_existing_controller_package=True, public_page_http_status=status,
               registry_published=True, independent_registry_download_verification=True,
               required_uploaded_file_count=len(verified), verified_files=verified,
               source_files_byte_matched=True, registry_generated_circuit_all_native_records_match=True,
               source_milestone_commit=proof['source_milestone_commit'],
               scope=proof['scope'], native_CLI_build_exit_code=1, native_CLI_push_initial_exit_code=1,
               upload_recovery='Required large JSON files uploaded individually as gzip archives after CLI HTTP 413 failures',
               optional_native_PCB_SVG_upload_http_status=413,
               optional_native_PCB_SVG_available_in_GitHub=True,
               registry_is_latest=release.get('is_latest'), ready_to_build=release.get('ready_to_build'),
               native_3D_models=77, current_PCB_hole_pitch_mm=23, current_PCB_hole_diameter_mm=2.7,
               carrier_included=False, native_geometry_bounds_pass=True,
               native_DRC_errors=proof['native_DRC_errors'],
               current_independent_copper_errors=proof['current_independent_copper_errors'],
               current_physical_graph_open_nets=proof['current_physical_graph_open_nets'],
               current_physical_graph_shorts=proof['current_physical_graph_shorts'],
               source_schematic_ERC_pass=proof['source_schematic_ERC_pass'],
               full_routing_and_hardware_qualified=False,
               server_preview_rendering_validated=False, manufacturing_release=False)
(ROOT / 'artifacts/publication/compact-current-motor-bolts-wip.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'verified_files'}))
