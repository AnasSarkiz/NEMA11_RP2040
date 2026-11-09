import json,sys,math,hashlib,importlib.util,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
B=Path(os.environ.get('NEMA11_BOARD_DIR',ROOT/'inputs/board'))
O=Path(os.environ.get('NEMA11_OUTPUT_DIR',ROOT)); O.mkdir(parents=True,exist_ok=True)
CIRCUIT=Path(globals().get('CIRCUIT_OVERRIDE',os.environ.get('NEMA11_BASELINE_JSON',B/'dist/index/circuit.json')))
EXPECTED_SHA=globals().get('EXPECTED_SHA_OVERRIDE','b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51')
assert hashlib.sha256(CIRCUIT.read_bytes()).hexdigest()==EXPECTED_SHA, 'Circuit SHA256 binding mismatch'
bindings=json.loads((ROOT/'input-bindings.json').read_text())['files']
for relative in ['config/placement.json','config/connections.json','scripts/audit_placement_geometry.py']:
 assert hashlib.sha256((B/relative).read_bytes()).hexdigest()==bindings['inputs/board/'+relative], f'Baseline input mismatch: {relative}'
spec=importlib.util.spec_from_file_location('geo',B/'scripts/audit_placement_geometry.py'); geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
x=json.loads(CIRCUIT.read_text()); src={e['source_component_id']:e['name'] for e in x if e['type']=='source_component'}; sp={e['source_port_id']:(src[e['source_component_id']],str(e.get('pin_number'))) for e in x if e['type']=='source_port'}; pp={e['pcb_port_id']:sp[e['source_port_id']] for e in x if e['type']=='pcb_port'}
pads={}
for e in x:
 if e['type'] in ['pcb_smtpad','pcb_plated_hole'] and e.get('pcb_port_id') in pp:
  lo,hi=geo.geometry_bounds(e); pads.setdefault(pp[e['pcb_port_id']],[]).append(dict(lo=lo,hi=hi,layers=e.get('layers',[e.get('layer')]),id=e.get('pcb_smtpad_id',e.get('pcb_plated_hole_id'))))
pairs=[]
def pair(a,p,b,q,label):
 aa=pads[(a,str(p))];bb=pads[(b,str(q))];d=min(geo.gap(i,j) for i in aa for j in bb); pairs.append(dict(a=f'{a}.{p}',b=f'{b}.{q}',group=label,lower_bound_mm=round(d,4),same_layer=bool(set(aa[0]['layers'])&set(bb[0]['layers']))))
for cap,p in [('C_IO1',1),('C_IO10',10),('C_IO22',22),('C_IO33',33),('C_IO42',42),('C_IO49',49),('C_DV23',23),('C_DV50',50),('C_USB',48),('C_ADC',43),('C_VREG_IN',44),('C_VREG_OUT',45)]:pair('U_MCU',p,cap,1,'MCU decoupling')
for a,p,b,q in [('U_MCU',20,'Y_MCU',1),('U_MCU',21,'R_XOUT',1),('R_XOUT',2,'Y_MCU',3),('Y_MCU',1,'C_XIN',1),('Y_MCU',3,'C_XOUT',1),('U_BUCK',3,'C_BUCK_IN',1),('U_BUCK',4,'C_BUCK_IN',2),('U_BUCK',5,'L_BUCK',1),('U_BUCK',6,'C_BOOTSTRAP',1),('U_BUCK',5,'C_BOOTSTRAP',2),('L_BUCK',2,'C_BUCK_OUT1',1),('L_BUCK',2,'C_BUCK_OUT2',1),('U_BUCK',1,'C_BUCK_OUT1',1),('U_DRV',22,'C_VM',1),('U_DRV',28,'C_VM',1),('U_DRV',29,'C_VM',2),('U_DRV',4,'C_CP',1),('U_DRV',5,'C_CP',2),('U_DRV',6,'C_VCP',1),('U_DRV',8,'C_VREG',1),('U_DRV',15,'C_DRV_LOGIC',1),('U_DRV',23,'R_SA',1),('U_DRV',27,'R_SB',1),('U_DRV',29,'R_SA',2),('U_DRV',29,'R_SB',2),('U_DRV',17,'C_REF',1),('U_ESD',5,'C_ESD',1),('U_ESD',2,'C_ESD',2),('J_DATA',8,'U_ESD',1),('J_DATA',7,'U_ESD',3),('U_MCU',46,'R_DM',1),('U_MCU',47,'R_DP',1),('U_MCU',52,'U_FLASH',6)]:pair(a,p,b,q,'critical')
(O/'metrics.json').write_text(json.dumps(dict(sha256=hashlib.sha256(CIRCUIT.read_bytes()).hexdigest(),pairs=pairs,pads={f'{k[0]}.{k[1]}':v for k,v in pads.items()}),indent=2))
for r in pairs:print(r)

con=json.loads((B/'config/connections.json').read_text())['components']; nearest={}
for p in [1,10,22,33,42,43,44,45,48,49,50,23]:
 net=con['U_MCU']['connections'][str(p)];opts=[]
 for n,c in con.items():
  if n.startswith('C_') and c['connections'].get('1')==net and c['connections'].get('2')=='GND' and (n,'1') in pads:
   d=min(geo.gap(a,b) for a in pads[('U_MCU',str(p))] for b in pads[(n,'1')]);opts.append((round(d,4),n,c['capacitance']))
 nearest[str(p)]=sorted(opts)[:3]
(O/'nearest_rail_caps.json').write_text(json.dumps(nearest,indent=2))
