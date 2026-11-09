# Scoped removal of the obsolete six-layer design

The user requested deletion of the old six-layer NEMA11 design while the
existing two-layer board is refactored around NEMA14. This is a working-tree
removal, not a rewrite of Git history or a deletion from the remote registry.

The exact scope is in [the removal manifest](legacy-six-layer-removal.json).
It removes 135 tracked files (169,682,310 bytes): the six-layer artifact folder,
its 0.4.0/0.4.1 and `compact-current` prototype packages, six-layer source and
routing data, configuration, dedicated generators/checkers/publication receipts,
and the dependent hybrid six-layer implementation. Six-layer-only branches were
also removed from shared historical builders. Unsupported retired options now
fail explicitly rather than silently building another design.

## Preserved

- The active `boards/nema11-rp2040-two-layer--20261022-a1` board. Its electrical
  refactor is separate from this deletion.
- Historical four-layer compact, controller and MCU sources, artifacts and
  prototypes, including generic multilayer geometry-auditor regressions.
- Original supplier imports, OEM motor STEP/drawing, NEMA14 references and
  hardware requirements.
- Shared mechanical inspection tools and historical motor-bolt/mounting drawings.
  Those drawings and their board hashes describe the original snapshots only,
  not the refactored two-layer board.

The shared OEM rear-bolt inspection script now requires explicit `--input` and
`--out` paths. It must not silently read a removed board or overwrite retained
historical evidence. The historical carrier-assembly builder requires explicit
`--historical-carrier`; it does not build the active design.

## Recover a specific deleted file or folder

All removed files existed at the complete pre-removal revision:

`eace9ede8d825d7d0c28e2a7484c8af5d252ff9c`

For inspection without changing the worktree:

```sh
git show eace9ede8d825d7d0c28e2a7484c8af5d252ff9c:src/compact/six-layer-board.tsx
```

To recover a selected folder intentionally:

```sh
git restore --source=eace9ede8d825d7d0c28e2a7484c8af5d252ff9c -- artifacts/compact-six-layer
```

Use the manifest's `removed_paths` for the other recoverable paths. Restoring
files does not make them active, qualify their hardware, or justify restoring
old package defaults. Do not restore the whole repository over current work.
A separate pre-edit Git bundle was also retained by the coordinating task.

## Validation boundary

The repository-selection regression enforces the single active entry point,
absence of retired runtime paths and offline-only CI. Root verification runs
active-board prebuild source checks, generation, types and formatting only.
No new native build, routing, CAM or registry upload was performed for this
removal, and no hardware pass is claimed.
