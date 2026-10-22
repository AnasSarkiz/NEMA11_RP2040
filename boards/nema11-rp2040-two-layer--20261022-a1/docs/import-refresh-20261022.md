# Full import refresh attempt — 2026-10-22

Request: update tscircuit, freshly re-import every purchased component and report
issues. This attempt is **blocked**, not a successful upgrade or import refresh.

The npm registry responded long enough to verify published versions:

| Package          | Installed working version | Requested published version |
| ---------------- | ------------------------- | --------------------------- |
| `@tscircuit/cli` | 0.1.2261                  | 0.1.2400                    |
| `tscircuit`      | 0.0.2764                  | 0.0.3003                    |

Metadata, source package integrity values, exact installation commands and exits
are recorded in `checks/import-refresh/`. The normal `bun install` failed on
HTTP 503 responses. Serial retries with `--network-concurrency 1 --prefer-offline`
fetched additional dependency metadata but failed on required tarballs, including:

- `@tscircuit/core@0.0.2196`
- `@tscircuit/checks@0.0.261`
- `@tscircuit/runframe@0.0.3055`
- `circuit-to-svg@0.0.453`
- the new dependency `@tscircuit/pcb-trace-linter` from its pinned GitHub commit

Requests retain the cloud proxy, TLS verification and package integrity checks.
Some metadata reads succeeded while package tarball reads failed; successful
metadata alone does not prove the toolchain was installed.

The CLI 0.1.2400 tarball was downloaded to Bun's cache. Its launcher defaults to
the older project-local CLI, so simply executing that downloaded entrypoint would
not prove a new-version import. The supported `--use-global` selector chooses
0.1.2400; startup then fails because the installed old `circuit-json` does not
export `simulation_return_current_excitation`. This is an incomplete/mixed
installation problem, not evidence that a correctly installed new CLI is broken.

The pending refresh includes 47 unique parts: all 46 selected BOM parts and the
excluded C5815189 USB connector. **Zero fresh imports were run with the new
release.** No result from the old CLI is counted as a fresh new-version result.
The original imported assets are byte-for-byte unchanged. The original package
manifest was restored to its working pins; the requested manifest is preserved
as `checks/import-refresh/requested-package.json` rather than committed as an
installed upgrade. The existing native board output remains unchanged.

`scripts/refresh_components.py` provides the candidate import workflow after a
complete verified installation. It checks actual package versions before doing
any work, imports C5815189 first, imports every other part independently, and
records untouched source/model hashes and exit codes. Candidate output stays
under this task's ignored `.cache/import-refresh/candidate/` until reviewed and
promoted. No purchased component definition is authored or patched.

No new footprint, pin mapping, model alignment or complete-board result can be
reported from this blocked attempt. The previously documented missing USB hole,
placement findings and hardware dimensions remain unresolved. Do not claim that
updating alone fixes them.

The same existing registry release accepted the diagnostic archive upload after
these failures. A further serial install still failed on the same required
tarballs. Registry write access therefore does not establish npm tarball access.
GitHub push also returned HTTP 503. The working package pins were restored after
the last attempt; full upgrade and all 47 imports remain pending.
