import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('motor',ROOT/'scripts/check_motor_assembly.py');motor=importlib.util.module_from_spec(spec);spec.loader.exec_module(motor)

class MotorAssemblyTests(unittest.TestCase):
    def test_genuine_model_hashes_and_axes(self):
        self.assertEqual(motor.contract()['motor'],'STEPPERONLINE 11HS12-0674S')
    def test_transform_origin_rotation_translation(self):
        actual=motor.transform((2,2,3),{'x':1,'y':2,'z':3},{'x':0,'y':0,'z':90},{'x':4,'y':5,'z':6})
        for a,b in zip(actual,(4,6,6)): self.assertAlmostEqual(a,b)
    def test_bottom_flip(self):
        self.assertAlmostEqual(motor.transform((0,0,2),dict.fromkeys('xyz',0),{'x':180,'y':0,'z':0},{'x':0,'y':0,'z':-.8})[2],-2.8)
    def test_motor_bounds_and_nominal_review_separation(self):
        cfg=motor.contract();vs=motor.vertices(ROOT/'references/motor-assets/11HS12-0674S.obj')
        bb=motor.bounds([motor.transform(v,dict.fromkeys('xyz',0),cfg['motor_rotation_deg'],cfg['motor_translation_mm']) for v in vs])
        self.assertAlmostEqual(bb['max'][2],-10.8,places=5)
        self.assertAlmostEqual(bb['min'][2],-62.3,places=5)
    def test_bad_hash_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'config').mkdir();(root/'references/motor-assets').mkdir(parents=True)
            cfg=motor.contract();(root/'config/motor-assembly.json').write_text(json.dumps(cfg));(root/'references/motor-assets/11HS12-0674S.obj').write_text('not OEM')
            with self.assertRaisesRegex(AssertionError,'OEM obj changed'):motor.contract(root)
    def test_source_uses_exact_contract_transform_and_assets(self):
        source=(ROOT/'assembly-preview.circuit.tsx').read_text()
        for expression in ['positionOffset: mechanical.motor_translation_mm', 'rotationOffset: mechanical.motor_rotation_deg', 'modelOriginPosition: { x: 0, y: 0, z: 0 }', 'objUrl: motorObj', 'stepUrl: motorStep', 'import Controller from "./index.circuit"', './references/motor-assets/11HS12-0674S.obj', './references/motor-assets/11HS12-0674S.step']:
            self.assertIn(expression, source)
        self.assertNotIn('<board',source)
        self.assertEqual(source.count('<assembly.part'),1)
    def test_uncropped_motor_fails_whole_frame(self):
        bb=motor.bounds(motor.vertices(ROOT/'references/motor-assets/11HS12-0674S.obj'))
        target=json.loads((ROOT/'config/requirements.json').read_text())['whole_assembly_frame_maximum_mm']
        self.assertGreater(bb['max'][1]-bb['min'][1],target[1])
        self.assertAlmostEqual(bb['max'][1]-bb['min'][1],48.2,places=5)
    def test_entrypoint_preserves_real_board_and_omits_fake_hardware(self):
        source=(ROOT/'assembly-preview.circuit.tsx').read_text()
        self.assertIn('<Controller />',source)
        self.assertNotIn('<assembly.bolt',source)
        self.assertNotIn('<assembly.motor',source)
        self.assertIn('EXPLODED_REVIEW_NOT_QUALIFIED',source)


class EmittedMotorAssemblyTests(unittest.TestCase):
    def fixture(self):
        cfg=motor.contract()
        base=[{'type':'pcb_board','width':28,'height':28,'thickness':1.6}, {'type':'source_trace','source_trace_id':'trace0','connected_source_port_ids':['p1','p2']}]
        source={'type':'source_component','source_component_id':'m','ftype':'subassembly','name':'OEM_11HS12_0674S_EXPLODED_REFERENCE','display_name':'OEM review'}
        cad={'type':'cad_component','cad_component_id':'c','source_component_id':'m','model_obj_url':'./references/motor-assets/11HS12-0674S.obj','model_step_url':'./references/motor-assets/11HS12-0674S.step','position':copy.deepcopy(cfg['motor_translation_mm']),'rotation':copy.deepcopy(cfg['motor_rotation_deg']),'model_origin_position':dict.fromkeys('xyz',0),'model_unit_to_mm_scale_factor':1}
        bom={'type':'cad_assembly_bom_item','name':'OEM review','source_component_id':'m','quantity':1,'cad_component_ids':['c']}
        return base,copy.deepcopy(base)+[source,cad,bom],cfg
    def test_matching_native_records(self):
        self.assertTrue(motor.validate_assembly(*self.fixture())['electrical_pcb_and_existing_cad_records_identical'])
    def test_native_transform_mismatches(self):
        for field,bad in [('position',dict(x=0,y=0,z=0)),('rotation',dict(x=180,y=0,z=0)),('model_origin_position',dict(x=0,y=0,z=1)),('model_unit_to_mm_scale_factor',1000),('model_obj_url','generic-motor.obj')]:
            with self.subTest(field=field):
                base,assembly,cfg=self.fixture();assembly[-2][field]=bad
                with self.assertRaisesRegex(AssertionError,'CAD mismatch'):motor.validate_assembly(base,assembly,cfg)
    def test_bom_mismatch(self):
        base,assembly,cfg=self.fixture();assembly[-1]['quantity']=4
        with self.assertRaisesRegex(AssertionError,'BOM'):motor.validate_assembly(base,assembly,cfg)
    def test_electrical_mutation(self):
        base,assembly,cfg=self.fixture();assembly[1]['connected_source_port_ids']=['p1','p3']
        with self.assertRaisesRegex(AssertionError,'mutated'):motor.validate_assembly(base,assembly,cfg)
    def test_unexpected_part(self):
        base,assembly,cfg=self.fixture();assembly.append({'type':'source_component','source_component_id':'fake','name':'invented_bolt'})
        with self.assertRaisesRegex(AssertionError,'unexpected'):motor.validate_assembly(base,assembly,cfg)
    def test_missing_motor(self):
        base,assembly,cfg=self.fixture()
        with self.assertRaisesRegex(AssertionError,'exactly one'):motor.validate_assembly(base,base,cfg)

if __name__=='__main__': unittest.main()
