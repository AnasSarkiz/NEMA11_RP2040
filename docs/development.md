# Development environment

Use the existing `/workspace/NEMA11_RP2040` checkout. Cloud tasks are already
isolated; do not create a Git worktree unless the user explicitly requests one.

Run `bash scripts/setup-tools.sh` from the checkout to install the frozen native
PCB toolchain and isolated CAD Python environment. Lockfile-based npm install
retains TLS/integrity checks; the locked Git trace-linter sources receive an
additional SHA-256 check. Python transitive versions are retained in
`tools/requirements-cad.lock`; the direct requirements are documented alongside
it. Dependencies/caches are excluded from Git. The tooling
currently follows the inspected GitHub v1.12.0 lock; compare it against the
published v1.13.0 before rendering NEMA11 source.

For native commands in each new shell:

```sh
cd /workspace/NEMA11_RP2040
export PATH="$PWD/tools/pcb/node_modules/.bin:$PATH"
export XDG_CONFIG_HOME=/workspace/.config
export XDG_CACHE_HOME=/workspace/.cache
export XDG_DATA_HOME=/workspace/.local/share
tsci version
```

Use `/workspace/.venvs/nema11-cad/bin/python` for native STEP geometry, PDF,
routing and CAM utilities. No service is required for the current requirements
milestone. No NEMA11 circuit exists yet, so do not run inherited NEMA14 scripts
against this checkout or claim reference validation applies to it.

Never print tokens or credential files. Configure `TSCIRCUIT_TOKEN` securely
through environment settings for registry publication; GitHub uses the existing
platform HTTPS Git authentication. No new GitHub token is required for native
Git operations that already succeed.

Future work must first retrieve and verify the exact v1.13.0 package and motor
PDF/STEP. See [validation gates](validation-plan.md). This setup is a development
tooling environment, not evidence of an electrically working motor controller.
