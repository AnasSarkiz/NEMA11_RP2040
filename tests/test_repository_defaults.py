"""Offline regression for the sole active board and scoped legacy removal.

These tests inspect source/configuration only. They never import or execute the
native tscircuit runtime and do not establish hardware correctness.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BOARD = 'boards/nema11-rp2040-two-layer--20261022-a1'
ENTRY = BOARD + '/index.circuit.tsx'


def load(relative):
    return json.loads((ROOT / relative).read_text())


class RepositoryDefaults(unittest.TestCase):
    def test_only_active_two_layer_entry_is_selected(self):
        self.assertTrue((ROOT / ENTRY).is_file())
        self.assertEqual(load('package.json')['main'], ENTRY)
        self.assertEqual(load('package.json')['version'], load(BOARD + '/package.json')['version'])
        config = load('tscircuit.config.json')
        self.assertEqual(config['includeBoardFiles'], [ENTRY])
        self.assertEqual(config['previewComponentPath'], ENTRY)
        self.assertEqual(load('tsconfig.json'), {'extends': './' + BOARD + '/tsconfig.json'})
        source = (ROOT / ENTRY).read_text()
        self.assertRegex(source, r'layers=\{2\}')
        self.assertRegex(source, r'routingDisabled=\{true\}')

    def test_root_commands_forward_current_source_checks(self):
        scripts = load('package.json')['scripts']
        for name in ['source:generate', 'source:check', 'test:prebuild', 'check:contracts', 'typecheck', 'format:check']:
            self.assertEqual(scripts[name], f'npm --prefix {BOARD} run {name}')
        self.assertEqual(scripts['verify:offline'],
                         f'npm run test:repository && npm --prefix {BOARD} run verify:offline')
        self.assertIn('test:repository', scripts['test'])
        self.assertIn('test:prebuild', scripts['test'])
        for name, command in scripts.items():
            self.assertNotIn('compact-six-layer', command, name)
            self.assertNotIn('compact-current', command, name)
            self.assertNotIn('artifacts/', command, name)
        self.assertEqual(scripts['build'], f'npm --prefix {BOARD} run build')
        self.assertIn(ENTRY.split('/')[-1], scripts['dev'])
        self.assertIn(BOARD, scripts['dev'])

    def test_removed_paths_stay_absent(self):
        manifest = load('docs/legacy-six-layer-removal.json')
        self.assertEqual(manifest['base_revision'], 'eace9ede8d825d7d0c28e2a7484c8af5d252ff9c')
        self.assertGreater(manifest['deleted_file_count'], 100)
        for path in manifest['removed_paths']:
            with self.subTest(path=path):
                self.assertFalse((ROOT / path).exists(), 'Retired design must not return silently')
        for path in manifest['preserved_paths']:
            with self.subTest(preserved=path):
                self.assertTrue((ROOT / path).exists())
        self.assertFalse(manifest['manufacturing_release'])

    def test_shared_runtime_has_no_deleted_path_references(self):
        forbidden = ['artifacts/compact-six-layer', 'prototypes/compact-current',
                     'src/compact/six-layer', 'config/compact-motor-bolts.json',
                     'config/compact-routing-placement.json', './six-layer-board',
                     '/hybrid-bulk-parts']
        for folder in ['src', 'scripts', 'examples', 'config']:
            for path in (ROOT / folder).rglob('*'):
                if path.suffix not in {'.py', '.tsx', '.ts', '.json', '.sh', '.cpp'}:
                    continue
                for retired in forbidden:
                    self.assertNotIn(retired, path.read_text(), str(path.relative_to(ROOT)))

    def test_shared_builders_reject_removed_modes(self):
        source = (ROOT / 'scripts/build-controller.tsx').read_text()
        self.assertIn('layerCount!==4', source)
        self.assertIn('Retired six-layer design options are no longer supported', source)
        assembly = (ROOT / 'scripts/build-controller-assembly.tsx').read_text()
        self.assertIn('if (!process.argv.includes("--historical-carrier"))', assembly)
        inspection = (ROOT / 'scripts/inspect_direct_motor_bolts.py').read_text()
        for option in ['--input', '--out']:
            self.assertRegex(inspection, re.escape(f"parser.add_argument('{option}'") + r'.*required=True')

    def test_ci_runs_offline_source_workflow_only(self):
        workflows = list((ROOT / '.github/workflows').glob('*.yml'))
        self.assertEqual(len(workflows), 1)
        workflow = workflows[0].read_text()
        self.assertIn('name: NEMA11 offline source checks', workflow)
        self.assertIn('name: Two-layer prebuild source only', workflow)
        self.assertIn('npm run verify:offline', workflow)
        self.assertIn('npm ci --prefix ' + BOARD + ' --ignore-scripts', workflow)
        self.assertNotIn('git diff', workflow)
        self.assertIn('--legacy-peer-deps', workflow)
        executable = '\n'.join(line for line in workflow.splitlines()
                               if not line.lstrip().startswith('#'))
        for forbidden in ['tsci ', 'bun ', 'run build', 'run verify\n',
                          'run_milestone_checks.py', 'artifacts/', 'tools/pcb',
                          'api.tscircuit.com', 'registry-api', 'publish']:
            self.assertNotIn(forbidden, executable)

    def test_active_offline_pipeline_cannot_invoke_native_tools(self):
        scripts = load(BOARD + '/package.json')['scripts']
        approved = {
            'check:contracts': 'python3 scripts/check_nema14_alignment.py',
            'test:prebuild': 'python3 -m unittest discover -s tests -v',
            'source:check': 'python3 scripts/generate_source.py --check',
            'typecheck': 'tsc --noEmit',
        }
        stages = [part.strip() for part in scripts['verify:offline'].split('&&')]
        self.assertEqual(stages, [f'npm run {name}' for name in [
            'check:contracts', 'test:prebuild', 'source:check', 'typecheck', 'format:check']])
        for name, command in approved.items():
            self.assertEqual(scripts[name], command)
        self.assertTrue(scripts['format:check'].startswith('prettier --check '))
        for name in [*approved, 'format:check', 'verify:offline']:
            self.assertNotIn('pre' + name, scripts)
            self.assertNotIn('post' + name, scripts)
        root_scripts = load('package.json')['scripts']
        for name in ['test:repository', 'test:prebuild', 'test', 'verify:offline']:
            self.assertNotIn('pre' + name, root_scripts)
            self.assertNotIn('post' + name, root_scripts)

    def test_documents_do_not_link_removed_runtime(self):
        for name in ['README.md', 'docs/development.md', 'docs/direct-motor-bolts.md',
                     'docs/four-mount-compact.md', 'docs/bulk-capacitor-review.md']:
            source = (ROOT / name).read_text()
            for target in re.findall(r'\]\(([^)]+)\)', source):
                if '://' in target or target.startswith('#'):
                    continue
                path = (ROOT / name).parent / target.split('#')[0]
                self.assertTrue(path.exists(), f'{name}: broken local link {target}')


if __name__ == '__main__':
    unittest.main()
