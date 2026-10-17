#!/usr/bin/env python3
"""Losslessly compact actual CLI JSON output to meet registry file-size limits."""
import hashlib,json
from pathlib import Path
F=Path(__file__).resolve().parents[1]/'prototypes/compact-six-layer-0.4.0';p=F/'dist/index/circuit.json';original=p.read_bytes();records=json.loads(original);assert records==json.loads((F/'index.circuit.json').read_text())
compact=(json.dumps(records,separators=(',',':'))+'\n').encode();proof_path=F/'package-verification.json';proof=json.loads(proof_path.read_text())
if original!=compact:
    proof['native_build_output_formatting']=dict(native_CLI_output_sha256=hashlib.sha256(original).hexdigest(),published_compact_JSON_sha256=hashlib.sha256(compact).hexdigest(),reason='Lossless whitespace compaction for registry decompressed-file limit; every native CLI output record retained',native_CLI_record_roundtrip_verified=True)
else:assert proof['native_build_output_formatting']['published_compact_JSON_sha256']==hashlib.sha256(compact).hexdigest()
p.write_bytes(compact);proof_path.write_text(json.dumps(proof,indent=2)+'\n');print('Every native CLI JSON record preserved; whitespace compacted for registry upload')
