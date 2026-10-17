#!/usr/bin/env python3
"""Independently download and hash every native compact prototype upload (no auth)."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];parser=argparse.ArgumentParser();parser.add_argument('--version',default='0.1.0');parser.add_argument('--folder',default='prototypes/compact-placement-0.1.0');parser.add_argument('--native-cli-exit-code',type=int,default=0);args=parser.parse_args();folder=ROOT/args.folder;base='https://registry-api.tscircuit.com/'
def post(path,data):
 request=urllib.request.Request(base+path,json.dumps(data).encode(),headers={'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(request,timeout=60) as r:return json.load(r)
name='AnasSarkiz/NEMA11_RP2040_Compact_Prototype';release=post('package_releases/get',{'package_name_with_version':name+'@'+args.version})['package_release'];files=post('package_files/list',{'package_release_id':release['package_release_id']})['package_files'];expected=['README.md','dist/index/circuit.json','index.circuit.json','native-cli-build.txt','package-verification.json','package.json','tscircuit.config.json'];verified=[]
for path in expected:
 row=next(r for r in files if r['file_path']==path);remote=post('package_files/get',{'package_file_id':row['package_file_id']})['package_file'];assert remote['is_text'];data=remote['content_text'].encode();assert data==(folder/path).read_bytes(),path
 verified.append(dict(path=path,remote_bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),local_match=True))
url='https://tscircuit.com/'+name
with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as r:status=r.status
receipt=dict(package=name,version='0.1.0',url=url,package_release_id=release['package_release_id'],public_page_http_status=status,registry_published=True,native_CLI_exit_code=0,independent_registry_download_verification=True,required_uploaded_file_count=len(expected),verified_files=verified,additional_registry_generated_files=[r['file_path'] for r in files if r['file_path'] not in expected],source_milestone_commit=json.loads((folder/'package-verification.json').read_text())['source_milestone_commit'],scope='Validated UNROUTED 28 mm all-top full-circuit placement, six A4 schematic sheets and native OEM motor/front-carrier proposal assembly',ready_to_build=release.get('ready_to_build'),physical_routing_complete=False,manufacturing_release=False)
receipt['version']=args.version
receipt['native_CLI_exit_code']=args.native_cli_exit_code
if args.version!='0.1.0':
 proof=json.loads((folder/'package-verification.json').read_text());receipt['scope']=proof['scope'];receipt['disconnected_controller_nets']=proof['disconnected_controller_nets'];receipt['native_DRC_pass']=False
(ROOT/('artifacts/publication/compact-prototype-'+args.version+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ['verified_files','additional_registry_generated_files']}))
