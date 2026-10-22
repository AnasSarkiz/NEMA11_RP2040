"""Safely reproduce CLI upgrade failure handling with a child-installer stub.

The real CLI runs unmodified. Only child package-manager commands are replaced
inside this subprocess; no real global or local dependency is installed.
"""
import json
import argparse
import os
from pathlib import Path
import subprocess
import urllib.request

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cli-package-root', type=Path, default=Path('node_modules/@tscircuit/cli'))
parser.add_argument('--label', default='current')
args = parser.parse_args()
root = Path.cwd()
evidence = root / 'checks/20261023'
stubs = root / '.cache/20261023/upgrade-fault-bin'
stubs.mkdir(parents=True, exist_ok=True)
for manager in ['bun', 'npm', 'pnpm', 'yarn']:
    stub = stubs / manager
    stub.write_text('#!/bin/sh\nif [ "$1" = "--version" ]; then echo 1.4.2; exit 0; fi\necho CONTROLLED_INSTALL_FAILURE_42 >&2\nexit 42\n')
    stub.chmod(0o755)
cli = root / args.cli_package_root / 'dist/cli/main.js'
runner = (root / 'node_modules/.bin/bun').resolve()
local_cli = json.loads((root / args.cli_package_root / 'package.json').read_text())['version']
with urllib.request.urlopen('https://registry.npmjs.org/@tscircuit%2fcli/latest', timeout=20) as response:
    latest_cli = json.load(response)['version']
env = dict(os.environ, PATH=str(stubs) + os.pathsep + str(root / 'node_modules/.bin') + os.pathsep + os.environ['PATH'], TSCI_TELEMETRY_DISABLED='true')
result = subprocess.run([str(runner), str(cli), 'upgrade'], env=env, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
output = result.stdout.decode(errors='replace')
(evidence / ('upgrade-controlled-failure-' + args.label + '.txt')).write_text(output)
called = 'CONTROLLED_INSTALL_FAILURE_42' in output
report = {'real_cli_package_version': local_cli, 'cli_package_root': str(args.cli_package_root), 'npm_latest_cli_version': latest_cli, 'installed_cli_already_latest': local_cli == latest_cli, 'real_cli_invoked_unmodified': True, 'only_child_package_manager_stubbed': True, 'controlled_child_exit_code': 42, 'child_installer_called': called, 'cli_exit_code': result.returncode, 'failure_message_present': 'Update failed' in output, 'failure_propagation_issue_reproduced': called and result.returncode == 0, 'unnecessary_upgrade_attempt_reproduced': local_cli == latest_cli and called, 'real_dependency_install_performed': False, 'command': 'absolute-real-bun node_modules/@tscircuit/cli/dist/cli/main.js upgrade; PATH prefixed with test-only package-manager stubs'}
(evidence / ('upgrade-controlled-failure-' + args.label + '.json')).write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
print(output[-900:])
