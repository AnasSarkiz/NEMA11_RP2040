#!/usr/bin/env bash
# Dependencies live outside version control; all source and locks are retained.
set -euo pipefail
project_root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p /workspace/.cache/npm /workspace/.cache/uv /workspace/.config /workspace/.local/share
export XDG_CONFIG_HOME=/workspace/.config
export XDG_CACHE_HOME=/workspace/.cache
export XDG_DATA_HOME=/workspace/.local/share
cd "$project_root/tools/pcb"
npm ci --legacy-peer-deps --cache /workspace/.cache/npm --no-audit --no-fund
# npm omits its registry integrity check for this locked Git dependency.
sha256sum --check trace-linter.sha256
python3 "$project_root/scripts/apply_native_keepout_fix.py"
if [ ! -e "$project_root/node_modules" ] && [ ! -L "$project_root/node_modules" ]; then
  ln -s tools/pcb/node_modules "$project_root/node_modules"
fi
export UV_CACHE_DIR=/workspace/.cache/uv
uv venv --python python3 --allow-existing /workspace/.venvs/nema11-cad
uv pip install \
  --python /workspace/.venvs/nema11-cad/bin/python \
  -r "$project_root/tools/requirements-cad.lock"
uv venv --python python3 --allow-existing /workspace/.venvs/nema11-cam
uv pip install \
  --python /workspace/.venvs/nema11-cam/bin/python \
  -r "$project_root/tools/requirements-cam.lock"
uv venv --python python3 --allow-existing /workspace/.venvs/nema11-layout
uv pip install \
  --python /workspace/.venvs/nema11-layout/bin/python \
  -r "$project_root/tools/requirements-layout.lock"
cd "$project_root"
"$project_root/tools/pcb/node_modules/.bin/bun" test tests-native
python3 -m unittest discover -s tests -v
/workspace/.venvs/nema11-cad/bin/python -m unittest discover -s tests-pcb -v
python3 scripts/current_budget.py --output artifacts/requirements/current-budget.json
