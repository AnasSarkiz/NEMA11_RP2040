"""Regression tests for reconstructed validation, independent of native builds."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

runner = module('run_milestone_checks')
parser = module('check_schematic_findings')

class SemanticReports(unittest.TestCase):
    def test_findings_fail_despite_zero_exit(self):
        self.assertFalse(parser.analyze('<SchematicPlacementIssues><Collision /></SchematicPlacementIssues>', 0)['strict_gate_passed'])

    def test_clean_xml(self):
        self.assertTrue(parser.analyze('<SchematicSheet><SchematicPlacementIssues /></SchematicSheet>', 0)['strict_gate_passed'])

    def test_truncated_or_malformed_fail(self):
        for text in ['', 'success', '<SchematicPlacementIssues><Collision />', '<SchematicSheet><SchematicPlacementIssues /></Schematic', '<SchematicPlacementIssues><X></SchematicPlacementIssues>', '<SchematicSheet><SchematicPlacementIssues /></SchematicSheet><SchematicPlacementIssues', '<SchematicPlacementIssues /></SchematicPlacementIssues>']:
            with self.subTest(text=text):
                self.assertFalse(parser.analyze(text, 0)['strict_gate_passed'])

    def test_nonzero_and_exceptions_fail(self):
        for text, code in [('<SchematicPlacementIssues />', 1), ('No issues found\nTypeError: oops', 0)]:
            self.assertFalse(parser.analyze(text, code)['strict_gate_passed'])

    def test_all_sheets_counted(self):
        text = '<SchematicSheet><SchematicPlacementIssues /></SchematicSheet><SchematicSheet><SchematicPlacementIssues><Collision /></SchematicPlacementIssues></SchematicSheet>'
        self.assertEqual(parser.analyze(text, 0)['reported_issue_count'], 1)

class Freshness(unittest.TestCase):
    def test_inputs_include_every_relevant_category(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            names = ['index.circuit.tsx', 'package-lock.json', 'package.json', 'tsconfig.json', 'tscircuit.config.json', 'config/x.json', 'imports/a/a.tsx', 'scripts/a.py', 'tests/a.py', 'emitted-tests/a.py', 'references/fixture.json']
            for name in names:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('initial')
            before = runner.fingerprint(root)
            self.assertEqual(set(names), set(before))
            for name in names:
                (root / name).write_text('changed')
                self.assertNotEqual(before, runner.fingerprint(root))
                (root / name).write_text('initial')

    def test_receipt_detects_changed_input_output_and_missing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'index.circuit.tsx').write_text('source')
            (root / 'checks').mkdir()
            (root / runner.OUTPUT).parent.mkdir(parents=True)
            (root / runner.OUTPUT).write_text('[{"type":"pcb_board"}]')
            inputs = runner.fingerprint(root)
            receipt = {'fresh_output': True, 'inputs_before': inputs, 'inputs_after': inputs, 'source_sha256': runner.digest(root / 'index.circuit.tsx'), 'output_sha256': runner.digest(root / runner.OUTPUT)}
            (root / runner.RECEIPT).write_text(json.dumps(receipt))
            self.assertTrue(runner.fresh_receipt(root))
            (root / 'package-lock.json').write_text('{}')
            self.assertFalse(runner.fresh_receipt(root))
            (root / 'package-lock.json').unlink()
            (root / runner.OUTPUT).write_text('[]')
            self.assertFalse(runner.fresh_receipt(root))
            (root / runner.OUTPUT).unlink()
            self.assertFalse(runner.fresh_receipt(root))

    def test_build_failure_cannot_be_masked_by_fresh_json(self):
        # Exercise the orchestration itself without invoking or racing a native build.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'index.circuit.tsx').write_text('source')
            (root / 'checks').mkdir()
            (root / runner.OUTPUT).parent.mkdir(parents=True)
            (root / runner.OUTPUT).write_text('stale')
            (root / runner.RECEIPT).write_text('stale')
            seen = []
            def fake_run(name, command):
                seen.append(name)
                if name == 'native-build':
                    self.assertFalse((root / runner.OUTPUT).exists())
                    self.assertFalse((root / runner.RECEIPT).exists())
                    (root / runner.OUTPUT).parent.mkdir(parents=True)
                    (root / runner.OUTPUT).write_text('[{"type":"pcb_board"}]')
                return {'command': command, 'exit_code': 1 if name == 'native-build' else 0}
            import os
            previous = Path.cwd()
            try:
                with patch.object(runner, 'ROOT', root), patch.object(runner, 'fingerprint', side_effect=lambda: {'index.circuit.tsx': runner.digest(root / 'index.circuit.tsx')}), patch.object(runner, 'run', side_effect=fake_run), patch.object(runner, 'fresh_receipt', return_value=True):
                    self.assertEqual(runner.main(), 1)
            finally:
                os.chdir(previous)
            self.assertEqual(seen[:3], ['format-check', 'typecheck', 'prebuild-tests'])
            self.assertIn('emitted-tests', seen)
            self.assertFalse(json.loads((root / runner.RECEIPT).read_text())['build_passed'])

    def test_no_fresh_output_skips_dependent_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'index.circuit.tsx').write_text('source')
            seen = []
            def fake_run(name, command):
                seen.append(name)
                return {'exit_code': 0, 'command': command}
            import os
            previous = Path.cwd()
            try:
                with patch.object(runner, 'ROOT', root), patch.object(runner, 'fingerprint', return_value={}), patch.object(runner, 'run', side_effect=fake_run):
                    self.assertEqual(runner.main(), 1)
            finally:
                os.chdir(previous)
            self.assertNotIn('emitted-tests', seen)
            self.assertNotIn('export-schematic', seen)

if __name__ == '__main__':
    unittest.main()
