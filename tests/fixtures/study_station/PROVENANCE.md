# Provenance: the neutral station study fixture

Everything in this directory was written for study-layer-to-codegen (2026-10-12). Nothing is copied from another project. The model is a stormwater pump station sized against the flow it must remove; `models/station.sysml` carries its baseline arithmetic in a comment.

The directory is a project of its own: every path inside it is relative to this directory. A study tool run on it in place needs `SYSML_CODEGEN_PROJECT_ROOT` set to this directory, because the git work tree that contains it is the sysml-codegen repository.

## What is here

- `models/station.sysml`: the model.
- `station.snapshot.json`: the v6 instance-graph snapshot captured from `models/`.
- `pkg/station_study/`: the package generated from that snapshot. Its bytes belong to the generator: never edit or reformat them.
- `studies/manifest.json`: the study-package manifest, with the indicator-input fingerprint pinned.
- `studies/axes.json`: three axis groups, `basin_area`, `installed_capacity` and `energy_price`.
- `studies/oracle_entry.py`: the independent oracle `verify` imports, and its operand bindings.
- `studies/study_route.py`: the execution route, stock teax only: `execute_baseline` and `run_grid`.
- `studies/baseline/`: the two documents `execute_baseline` deposits, which `preflight gates` reads.
- `census.json`: the package's tracked entry-point census. `integrate`'s gate 4 compares the package against it.
- `pyproject.toml`: the station's declaration for `integrate`, under `[tool.sysml-codegen.integrate]`. It declares both repo-scope gates, each with its own `checked` text, no extra environment variable, and the backup prefix `station-integration-backup-`.
- `gates/check_pins.py` and `gates/check_census.py`: the two repo-scope gates that declaration names. `check_pins.py` (gate 1a) checks that the toolchain imports. `check_census.py` (gate 5) checks `census.json` against the committed package. pytest runs them because `integrate` names them explicitly; this repository's suite never collects them.

## Regenerating

Run these from the repository root, in order. Each later step depends on the bytes the earlier ones write.

1. Capture the snapshot. This needs the syside license: `uv run --no-sync --env-file <file holding SYSIDE_LICENSE_KEY> sysml-codegen snapshot --models tests/fixtures/study_station/models --output tests/fixtures/study_station/station.snapshot.json`
2. Generate the package from the snapshot: `uv run --no-sync sysml-codegen generate --from-snapshot tests/fixtures/study_station/station.snapshot.json --output tests/fixtures/study_station/pkg/station_study --package-name station_study`
3. Re-pin the manifest. Print the fingerprint with `SYSML_CODEGEN_PROJECT_ROOT=$PWD/tests/fixtures/study_station uv run --no-sync sysml-codegen study indicators --package tests/fixtures/study_station/pkg/station_study --print-fingerprint`, and copy its digest and file list into `fingerprints.indicator_inputs`. Copy `executable_fingerprint` from `pkg/station_study/contracts/package_contract.json` and `semantic_fingerprint` from `pkg/station_study/contracts/model_contract.json` into `fingerprints.recorded_provenance`.
4. Refresh `studies/baseline/` in the teax lane, with `TEAX_SIMKIT_PATH` naming a simkit root: `out=$(mktemp -d) && SYSML_CODEGEN_PROJECT_ROOT=$PWD/tests/fixtures/study_station PYTHONPATH="$TEAX_SIMKIT_PATH:tests/fixtures/study_station/studies" uv run --no-sync python -c 'import sys; from pathlib import Path; import study_route as r; f = Path("tests/fixtures/study_station"); r.execute_baseline(Path(sys.argv[1]), package_dir=f / "pkg/station_study", manifest_path=f / "studies/manifest.json")' "$out" && cp "$out/package_identity.json" "$out/baseline_result.json" tests/fixtures/study_station/studies/baseline/`
5. Re-derive `census.json` whenever step 2 changes the package. `derived_against_semantic_fingerprint` is `pkg/station_study/contracts/model_contract.json`'s `semantic_fingerprint`, `entry_points` is its parameter count, and `by_entry_type` is `sysml_codegen.study.census.by_entry_type` of the package with each list sorted.

`tests/study/test_study_fixture_current.py` (license lane) fails when steps 1 and 2 would change a committed byte. `tests/execution/test_study_station.py` (teax lane) fails when step 4 would. `tests/study/test_census.py` fails when step 5 would.

## The snapshot rule

`integrate`'s gate 4 requires exactly one `*.snapshot.json` beside the models root. That is why the snapshot is `station.snapshot.json`, next to `models/`. This repository's usual name, `instance_graph_snapshot.json`, does not match that pattern.
