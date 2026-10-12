# SC12 parity: the original study tools against the moved ones

This directory is the evidence for spec SC12 (design Appendix G). It runs fusion-tea's original study tools (staged at `b06585709`) and the moved `sysml_codegen.study` tools, installed from a wheel, on the same inputs. It then checks that their exit codes and output documents are equal, except in the fields the closed list B1–B13 names.

**Status (2026-10-12): stopped, five cases `DIFFERENT`.** 23 of 28 cases are `EQUAL` or `EQUAL after closed-list fields`, and library parity holds. The five cases whose route runs under read coverage (gates 7, 8 and 9, and `CANDIDATE`) differ only in receipt entries about the installed `sysml_codegen` package. Those differences are outside the rules as written, so the phase stops for the orchestrator's decision. The plan's Phase 4 notes give the full account and the options.

## Run it

```bash
S=/tmp/study-parity-$(date +%Y%m%d-%H%M%S)
EV=.project/active/study-layer-to-codegen/evidence/parity
bash $EV/make_venv.sh $S /home/reid/1cfe/sysml-codegen-study-layer /home/reid/1cfe/agentic-mbse-study-layer /home/reid/1cfe/teax
set -a; source /home/reid/1cfe/sysml-codegen/.env; set +a        # SYSIDE_LICENSE_KEY
$S/venv/bin/python $EV/parity.py --scratch $S --staged .orchestrate-logs/src/fusion-tea@b06585709 \
    --fixture tests/fixtures/study_station --teax /home/reid/1cfe/teax all
```

Run both commands from the repository root. `all` sets up, runs every case and writes the report, in about two minutes. It exits 0 only when every case is `EQUAL…` and library parity holds. The steps also run alone: `setup`, `run [CASE…]` and `report`.

## What it builds

- **`make_venv.sh`** builds both wheels from `git archive HEAD`, never from a working tree. It creates `$S/venv` on `/usr/bin/python3.12`, fusion-tea's interpreter (plan Phase 4, decision Q2), so `sys.base_prefix` is `/usr` and neither B13 allowance fires on either side.
  - Everything installed is byte-compiled at install time, so no run writes a `.pyc` into the venv.
  - teax's simkit is importable through a `.pth` file naming `teax/packages/teax-simkit`, which is what an editable install amounts to, without building into the teax checkout.
  - `wheels/sources.json` records both commits and both wheel digests; the report copies them.
- **`$S/project`** is a git repository holding the fixture's tree at its root, the staged originals at `scripts/study/` and `scripts/integrate.py`, and two stand-in gate files at fusion-tea's paths.
  - The spine stand-in carries fusion-tea's `_contract` and `_by_entry_type` (lines 174–182) verbatim, because the original seam imports them.
  - `pyproject.toml` is `../fusion-tea/declaration.toml`, Appendix D's fusion-tea declaration. So rows 1a and 5 must reproduce fusion-tea's strings.
- **Runs.** Every case runs three times from the same base commit: `orig` (`python scripts/<tool>.py`), `orig2` (the same again) and `moved` (`python -m sysml_codegen.study.<tool>`).
  - Each case's mutation is committed with fixed dates, so its commit id is the same in every run.
  - Each run starts from a cleaned tree (`git clean -fdx`), so no run inherits another's bytecode.
  - Every path in the arguments is relative to the project, which is the working directory.
  - `out/` is `$S/out`, moved aside into `$S/runs/<case>/<mode>/` after each run.
- **The environment** is built from nothing, not inherited. Both modes get fusion-tea's four wheel variables (dummies) and `STOP_PARSER_TEAX_ROOT`. Each mode adds one variable, the harness side of a closed-list item:
  - a `uv` shim first on `PATH` runs `uv run X …` as `X …` (B3);
  - moved: `TEAX_SIMKIT_PATH` (B7);
  - orig: `SYSML_CODEGEN_PROJECT_ROOT`, which no original tool reads. The fixture route imports the moved `identity` in both modes (Appendix G), and its `build_sealed` needs a project root. The moved seam hands that root to its producers (B1, DD2); the original seam predates it. Without it, the moved `roots` falls back to running `git`, and read coverage refuses that child process at gate 7. That refusal, `unsupported integer-descriptor open: 3`, is what the first run showed.
- **Setup** also makes the grid store both `verify` cases read (`$S/inputs`, from the fixture's own `run_grid`). It measures the B13 preload set into `preloads.json` and runs library parity.

## The comparison rules

Each rule is a constant or one small function in `parity.py`, and every application is counted in `cases/<case>/comparison.json` and `report.md`.

1. **Exit codes** must be equal across the three runs.
2. **Noise** is masked by the token patterns in `patterns.json`, never by whole field. Each pattern states its reason and scope. orig and orig2 must then be equal; any residue is reported as `NOISE` and fails the case.
3. **Determined closed-list values are mapped** from orig to moved, only in the fields named:
   - `tool.path` and `command[0]` (B2), by `TOOL_PATHS`;
   - integrate's gate and blocker `producer` strings (B2, B11), by `TOOL_PATHS` and `CENSUS_PRODUCERS`;
   - gate 1b's refusal detail, which names the simkit root `TEAX_SIMKIT_PATH` where the original named the checkout root `STOP_PARSER_TEAX_ROOT` (B7, `teax_detail_mapping`);
   - rows 1a and 5 are not mapped; they must equal the declaration's `target` and `checked` (B5, B12, `declared_rows_hold`).
4. **Content-derived closed-list values are masked by token**, on both sides:
   - `source_digest.digest`, and the `sha256` of each `.py` in `source_digest.files[]` (B2). Schema entries keep their `sha256`, which must be equal. Files only the moved tools digest (`roots.py`, `census.py`, `declarations.py`) are counted as B2 additions; any other extra file is a difference.
   - The receipt's `dependency_digest`, and the 64-hex digest inside gate 7's pass detail (B8).
   - Read-coverage receipts, by `receipt_view`:
     - Entries under each run's tool root (orig `$S/project/scripts/`, moved `TOOL_HOME/sysml_codegen/`) are compared as path sets after mapping, and their category and `sha256` may differ (B8, B2).
     - orig's `runtime-observed` reads of the measured preloaded standard-library `.pyc` files are dropped where moved does not record them (spec B13 consequence; `preloads.json`). Exactly that set is excluded. Every one of those modules is checked to be in the import closure of `sysml_codegen.study.roots` or `zoneinfo`.
     - Every other entry is compared whole: path, category and `sha256`.
5. **Everything else must be equal**, every `detail` string included.
   - integrate's stderr is its human summary. Each run's stderr is checked to equal `human_summary` of its own return, and the returns are then compared.
   - teax's work area `out/_work/` (SQLite stores, package links) is compared by file listing; its bytes are teax's, not tool documents.
6. **Library parity.** With the moved root pinned by `use_project_root`, these agree between the originals and the moved modules: `indicator_input_fingerprint`, `build_sealed`, `repo_relative_posix` on four paths, and `rederived_census`.

## Where this departs from Appendix G, and why

- **`SYSML_CODEGEN_PROJECT_ROOT` in the orig environment.** See "The environment" above. It is harness plumbing that gives the moved library the root the moved seam would export. It masks nothing.
- **A B7 row in rule 3's table.** Appendix G's table lists tool paths, producers and rows 1a and 5. Phase 3 recorded that gate 1b's refusal now names the simkit root, and said parity must map it. The mapping is one exact string, scoped to gate 1b's detail.
- **Three noise patterns beyond Appendix G's list.** orig against orig2 shows that each is noise.
  - `junit-clock`: pytest's junit `time` and `timestamp`, the same timing as `in N.NNs`.
  - `atomic-write-temp`: `common.write_document`'s `mkstemp` names.
  - `teax-staging-directory`: teax's uuid staging directories.

  The last two appear only in a receipt's `attempted_new_output_creations`. Appendix G's read-coverage token pattern is matched as the run's own token, exactly, rather than as any 32-hex string.
- **The preflight stale-manifest case** stales `recorded_provenance`, because that is what `preflight gates`' `manifest_currency` check reads. integrate's gate-6 case stales the pin, which is what gate 6 reads.
- **Evidence size.** `cases/<case>/{orig,moved}.json` hold each run's normalized outputs. A receipt is summarized there by category counts, and the recaptured snapshot by its length, because the full bytes (about 800 kB per receipt) stay in `$S/runs`. `comparison.json` lists every difference in full.

## Files

- `parity.py`, `make_venv.sh`, `patterns.json`: the harness.
- `preloads.json`: the measured preload set (B13 consequence).
- `report.md`: generated; the sources, environment, library parity, per-case status, rule and pattern counts, and every difference.
- `results.json`: the same, machine-readable, with the setup record.
- `cases/<case>/`: `comparison.json`, `orig.json` and `moved.json` per case.
