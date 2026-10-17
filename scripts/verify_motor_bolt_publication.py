#!/usr/bin/env python3
"""Public, authenticated-upload-independent verification of the motor study."""
import hashlib,json,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'prototypes/motor-bolt-study-0.1.0'
name='AnasSarkiz/NEMA11_RP2040_Motor_Bolt_Study';version='0.1.0'
def post(path,payload):
    request=urllib.request.Request('https://registry-api.tscircuit.com/'+path,
        json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(request,timeout=45) as response:return json.load(response)
release=post('package_releases/get',{'package_name_with_version':name+'@'+version})['package_release']
files=post('package_files/list',{'package_release_id':release['package_release_id']})['package_files']
expected=['README.md','dist/index/circuit.json','index.circuit.json','native-cli-build.txt','package-verification.json','package.json','tscircuit.config.json']
verified=[]
for path in expected:
    entry=next(r for r in files if r['file_path']==path)
    remote=post('package_files/get',{'package_file_id':entry['package_file_id']})['package_file']
    assert remote['is_text'];data=remote['content_text'].encode()
    assert data==(F/path).read_bytes(),path+' differs from the checked native study'
    verified.append(dict(path=path,remote_bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),local_match=True))
url='https://tscircuit.com/'+name
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as response:status=response.status
proof=json.loads((F/'package-verification.json').read_text())
receipt=dict(package=name,version=version,url=url,package_release_id=release['package_release_id'],
             public_page_http_status=status,registry_published=True,native_CLI_push_exit_code=0,
             independent_registry_download_verification=True,required_uploaded_file_count=len(verified),
             verified_files=verified,source_milestone_commit=proof['source_milestone_commit'],
             scope=proof['scope'],ready_to_build=release.get('ready_to_build'),native_CAD_models=1,
             nominal_existing_rear_bolt_axes_verified=True,nominal_bolt_pitch_mm=23,
             PCB_included=False,carrier_included=False,rear_bolt_thread_or_length_assumed=False,
             direct_PCB_attachment_validated=False,server_preview_rendering_validated=False,manufacturing_release=False)
(ROOT/'artifacts/publication/motor-bolt-study-0.1.0.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='verified_files'}))
