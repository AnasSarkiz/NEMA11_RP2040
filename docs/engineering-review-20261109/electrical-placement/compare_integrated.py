from pathlib import Path
import json,hashlib,os
ROOT=Path(__file__).resolve().parent
O=Path(os.environ.get('NEMA11_OUTPUT_DIR',ROOT));O.mkdir(parents=True,exist_ok=True)
candidate=Path(os.environ.get('NEMA11_CANDIDATE_JSON',ROOT/'inputs/integrated.circuit.json'))
expected='f590d22ad18feff381969d4dfc4032eb65f51c80465a360de8063ea7953ab538'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==expected
baseline=json.loads((O/'metrics.json').read_text())
code=(ROOT/'review.py').read_text().split("(O/'metrics.json').write_text")[0]
ns={'__file__':str(ROOT/'review.py'),'CIRCUIT_OVERRIDE':candidate,'EXPECTED_SHA_OVERRIDE':expected};exec(code,ns)
new=ns['pairs'];old=baseline['pairs'];assert len(new)==len(old)
comparison=[]
for a,b in zip(old,new):
 assert (a['a'],a['b'])==(b['a'],b['b'])
 comparison.append(dict(a=a['a'],b=a['b'],baseline_mm=a['lower_bound_mm'],integrated_mm=b['lower_bound_mm'],delta_mm=round(b['lower_bound_mm']-a['lower_bound_mm'],4),same_layer=b['same_layer']))
# Additional return legs omitted from original44, relevant to changed driver capacitors.
extras=[]
for cap,pin in [('C_VREG',29),('C_DRV_LOGIC',18)]:
 key=f'{cap}.2';other=f'U_DRV.{pin}';basepads=baseline['pads'];g=ns['geo'];bp=min(g.gap(a,b)for a in basepads[key] for b in basepads[other]);np=min(g.gap(a,b) for a in ns['pads'][(cap,'2')] for b in ns['pads'][('U_DRV',str(pin))]);extras.append(dict(a=key,b=other,baseline_mm=round(bp,6),integrated_mm=round(np,6),delta_mm=round(np-bp,6)))
result=dict(baseline_sha256=baseline['sha256'],candidate_sha256=expected,pair_count=len(comparison),comparison=comparison,additional_driver_returns=extras,summary=dict(improved=[r for r in comparison if r['delta_mm']<-.0001],worsened=[r for r in comparison if r['delta_mm']>.0001],unchanged_count=sum(abs(r['delta_mm'])<=.0001 for r in comparison)))
(O/'integrated_comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result['summary'],indent=2));print(extras)
