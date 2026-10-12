# fusion-tea switch to the study layer installed from sysml-codegen

This runbook moves fusion-tea from its local study layer to the one sysml-codegen ships: the run-study skill, the study-policy template, and the tools in `sysml_codegen.study`. Its local tools become aliases of the installed modules, its nine route modules import the installed package, it declares its two repo-scope gates for `integrate`, and `sysml-codegen install-commands` replaces its local skill. Every committed study record stays valid as written.

It runs after the owner merges and pushes agentic-mbse `study-layer-to-codegen` and then sysml-codegen `study-layer-to-codegen`, in that order (ADR-0008), by the orchestrator or the owner. It runs on the fusion-tea branch that orchestrator step O4 created, which already holds the fusion-tea homes of every line the shipped text dropped. The owner then pushes and merges that branch.

**Sources.** The steps are spec SC9's nine, in its order, with design Appendix H3's actions, rehearsal and expected observations. The drafts cited below live in sysml-codegen `.project/active/study-layer-to-codegen/evidence/` (`$EV`) until close, when this runbook moves to agentic-mbse (D10). Phase 5 wrote this draft while Phase 4 ran in parallel, and Phase 6 checked every citation of Phase 4's files against the files themselves: `$EV/fusion-tea/wrappers/scripts/`, `routes.sed`, `declaration.toml`, `step5-tests.patch`, `SMOKE.md`, and `$EV/rehearsal/{env.sh.example,junit-diff.py}`.

**Names used below.**

- `FT` — the fusion-tea worktree holding the O4 branch. Run every command from `$FT`. Never touch the owner's main fusion-tea checkout.
- `M_AMBSE`, `M_CODEGEN` — the full SHAs of the two merge commits. A pin can name only a pushed commit.
- `EV` — the evidence directory above, in a sysml-codegen checkout at `M_CODEGEN`.
- `FTC` — in the rehearsal only, a disposable worktree of fusion-tea `b06585709` with the O4 branch's text commits applied.

## Before you start

- `git status --short` in `$FT` is empty, and `git log --oneline b06585709..HEAD` shows O4's text commit: the policy's § 6 "Execution routes", § 12 and § 13, the integration-guide supplement, the `CLAUDE.md` "Study layer" section and the stellarator annex's line 5 (`$EV/fusion-tea/text/`).
- The environment file `$EV/rehearsal/env.sh` (copied from `env.sh.example`, its `FTC` line filled in, kept out of git) is sourced: the licence (present, never printed), fusion-tea's `STOP_PARSER_*` values, and `TEAX_SIMKIT_PATH=$STOP_PARSER_TEAX_ROOT/packages/teax-simkit`.

**Observed in the rehearsal:** *(O3 fills this in.)*

## Step 1: drift check

fusion-tea's local copies stay in use until this switch, so a fix made to them since `b06585709` must reach sysml-codegen or its fusion-tea home first, or this switch drops it.

```bash
git fetch origin
git diff b06585709 origin/main -- .claude/skills/run-study modeling_project/STUDY_POLICY.md scripts/study scripts/integrate.py docs/integration_seam_operator_guide.md
```

**Expected:** it prints nothing. If it prints a change, stop until that change is in sysml-codegen (an ordinary change there) or in its fusion-tea home (`$EV/read-through.md` names each one).

**Rehearsal:** the same, on `$FT`. **Observed in the rehearsal:** *(O3)*

## Step 2: agentic-mbse pin check

sysml-codegen's `install-commands` uses agentic-mbse's installer through the API marked `installer/v1`, which fusion-tea's agentic-mbse pin `adbef75` predates. The agentic-mbse version stays 0.1.3; only the SHA moves (design DD5, Appendix B).

```bash
uv run --no-sync python -c "from agentic_mbse.cli.installation import INSTALLER_API_VERSION as v; print(v)"
```

**Expected:** `installer/v1`. If it raises or prints anything else, move fusion-tea's agentic-mbse pin to `M_AMBSE` first, as Item 2's runbook moved it (`[tool.uv.sources]` `rev`, the hand-edited `uv.lock`, `uv sync --frozen --extra e2e`, restore removed packages, `uv lock --check`) and set `A_FINAL` in `tests/test_dependency_provenance.py`. If Item 2's pin move has not run yet, pin straight to `M_AMBSE`.

**Rehearsal:** after `uv pip install --python $FTC/.venv/bin/python --no-deps $AMBSE_WHEEL $CODEGEN_WHEEL`, wheels built from the two branch heads; this is run B's state. **Observed in the rehearsal:** *(O3)*

## Step 3: no-loss check

Before anything local is removed, every ledger destination must be in fusion-tea's tree. Each `moved` row of `$EV/read-through.md` names its home and a fixed-string anchor; the shared ledger's Item 3 rows (`$EV/ledger-rows.md`, appended by O4) group them.

```bash
python3 $EV/fusion-tea/text/check_anchors.py $EV/read-through.md .
```

The script greps all 75 anchors in their homes in the working tree and exits non-zero naming any it cannot find. By hand, one row: `git grep -nF 'Two routes, and no third.' -- modeling_project/STUDY_POLICY.md`.

**Expected:** `75 anchors found, 0 missing`, exit 0 (74 from O4's text commit, plus IG-43 from `fusion-tea/text/audit-f8-supplement.patch`, which the orchestrator applies on the O4 branch after the audit). If one is missing, the script names it: stop, because the branch's text is incomplete.

**Rehearsal:** on `$FTC` with O4's text commits applied. **Observed in the rehearsal:** *(O3)*

## Step 4: move the sysml-codegen pin

This is the step that needs `M_CODEGEN`.

1. Save the package list: `uv pip list > /tmp/study-switch-pip-before.txt`.
2. In `pyproject.toml` (`[tool.uv.sources]`), set sysml-codegen's `rev` to `M_CODEGEN`. Do not change `sysml-codegen==0.1.1`: the version is unchanged.
3. In `uv.lock`, replace the old SHA `8a758e9240707b58fe32a509c3b509941ca4fa01` with `M_CODEGEN` by hand. `grep -c` the old SHA before and after; after must be 0. Do not run `uv lock`.
4. `uv sync --frozen --extra e2e`, then `uv pip list > /tmp/study-switch-pip-after.txt` and diff the two lists. Restore every removed package except sysml-codegen's own change.
5. `uv lock --check` reports the lock fresh.
6. In `tests/test_dependency_provenance.py`, set `C_PROD` to `M_CODEGEN`. Then `uv run --no-sync pytest tests/test_dependency_provenance.py -q` passes with the environment of "Before you start".

**What this item changed in sysml-codegen's `pyproject.toml`, and the lock.** Re-check before the move with `git -C <sysml-codegen> diff aa35f06 M_CODEGEN -- pyproject.toml`. At the time of drafting:

- `jsonschema` joined the `dev` extra. fusion-tea does not request that extra, so its lock does not change.
- `[tool.mypy]` overrides and `[tool.ruff.lint.per-file-ignores]` entries for the study modules. Tool tables do not enter dependency metadata.
- No runtime dependency was added, the agentic-mbse bound stays `>=0.1.3,<0.2`, no console script was added, and the skill files, policy template and schemas are package data inside `sysml_codegen`.

So the hand-edited lock holds. If the re-check shows a new runtime dependency or a changed agentic-mbse bound, it does not: stop and re-plan the pin move.

**Rehearsal:** not rehearsable — it needs `M_CODEGEN`. **Observed in the rehearsal:** not run.

## Step 5: switch

1. **Wrappers.** Copy each module alias over its namesake: `cp $EV/fusion-tea/wrappers/scripts/study/*.py scripts/study/` (the seven `common`, `manifest`, `identity`, `indicators`, `preflight`, `verify` and `read_coverage`) and `cp $EV/fusion-tea/wrappers/scripts/integrate.py scripts/integrate.py`. Each pins fusion-tea's root in-process from its own location, never touches `os.environ`, runs `main()` when executed, and otherwise replaces itself in `sys.modules` (design DD14).
2. **Route modules.** Rewrite the import in the nine live `study_route.py` files that import `scripts.study` (`CONSUMER_SURFACE.md:43,50,57,62,67,72,89,97,106`). They then import `sysml_codegen.study`, which keeps read coverage inside its permitted sources (B8). Name the nine files; never use a pathspec glob. git's pathspec `*` crosses `/`, so in a git command a pattern such as `exploration/*/studies/study_route.py` also matches the route copies inside committed records (`<record>/results/sources/`, `<record>/preparation/`), which must never change.

   ```bash
   ROUTES=(
     exploration/aries_integrated/studies/study_route.py
     exploration/component_alternatives/studies/study_route.py
     exploration/costed_loop_brayton/studies/study_route.py
     exploration/exchanger_architecture/thermal_requirements/studies/study_route.py
     exploration/ife_e2e/studies/study_route.py
     exploration/magnet_materials/studies/study_route.py
     exploration/stellarator_e2e/studies/study_route.py
     exploration/stellarator_materials/studies/study_route.py
     exploration/whole_plant_conversion/studies/study_route.py
   )
   sed -i -f $EV/fusion-tea/routes.sed "${ROUTES[@]}"
   ```

3. **Schemas.** `git rm -r scripts/study/schemas`. They ship in `sysml_codegen/study/schemas/`, byte-identical.
4. **Tests.** Apply the two test patches in this order: `patch -p1 < $EV/fusion-tea/step5-tests.patch` (Phase 4, 17 files), then `patch -p1 < $EV/fusion-tea/step5-guide-contract.patch` (Phase 5, one file). They touch no file in common. Phase 6 checked that both apply cleanly in that order to a fresh copy of `b06585709`, alone and after the four text patches of O4's branch. The first carries design Appendix H3's edits: schema home, tool paths, `TEAX_SIMKIT_PATH`, `REQUIRED_ENV` plus the declared environment, and `tests/models/test_model_family_spines.py` importing `by_entry_type` from `sysml_codegen.study.census`, so gates 4 and 5 share one implementation. The second reduces `tests/study/test_integrate_guide_contract.py` to the supplement's own facts: the sealed-wheel home, `WHEEL_HASHES` and ADR-0009.

**Expected:**

```bash
uv run --no-sync python -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)"   # True
git grep -n 'from scripts.study' -- "${ROUTES[@]}"            # nothing: no live route imports scripts.study
git grep -c 'from sysml_codegen.study' -- "${ROUTES[@]}"      # each of the nine files listed
git status --porcelain --untracked-files=all -- exploration/ | cut -c4- | grep -vxF -f <(printf '%s\n' "${ROUTES[@]}")   # nothing: no other file under exploration/ changed, record copies included
```

**Rehearsal:** applied on `$FTC`; `$EV/fusion-tea/SMOKE.md` records the drafts' smoke test in the parity layout. **Observed in the rehearsal:** *(O3)*

## Step 6: declare

1. Append `$EV/fusion-tea/declaration.toml` to `pyproject.toml`. It is design Appendix D's fusion-tea table: both repo-scope gates with today's `checked` texts, the five `STOP_PARSER_*` variables, `record-distributions = { costingfe = "1costingfe" }` and the backup prefix `fusion-tea-integration-backup-`. With it, fusion-tea's returns keep rows 1a and 5, the environment sweep, the toolchain block and the prefix byte for byte (B4–B6, B10, B12; SC12).
2. Add `TEAX_SIMKIT_PATH=$STOP_PARSER_TEAX_ROOT/packages/teax-simkit` to `.venv/integration.env`, written with the expanded path. Gate 1b reads the teax revision there, and without it gate 1b blocks (B7, DD10).

**Expected:** `uv lock --check` still reports the lock fresh: a `[tool]` table does not enter it.

**Rehearsal:** applied on `$FTC`. **Observed in the rehearsal:** *(O3)*

## Step 7: re-install

1. `git rm -r -q .claude/skills/run-study .agents/skills/run-study`
2. In `.gitignore`, delete the whitelist line `!.claude/skills/run-study/`. Find it by text; the other lines stay.
3. `uv run --no-sync sysml-codegen install-commands . < /dev/null`

Both assistants are the default. With no terminal, the installer keeps a differing file it does not manage instead of prompting. fusion-tea's ratified `modeling_project/STUDY_POLICY.md` is a project document, so it is kept.

**Expected:**

- five files under `.agents/skills/run-study/`: `SKILL.md`, `runbook.md`, `record-template.md`, `annex-template.md`, `integration-guide.md`;
- `.claude/skills/run-study` is a link into `.agents/skills/run-study`;
- the output says "Preserved modeling_project/STUDY_POLICY.md";
- `.sysml-codegen/install.json` exists and lists the installed files; `.agentic-mbse/install.json` names none of them.
- If fusion-tea's `.claude/commands/teax-completion.md` differs from the shipped file, the output says "Preserved .claude/commands/teax-completion.md: …" and the file stays. That is the installer's first-run rule (DD6), not a failure. A copy the old installer left differs, because the shipped file has since lost a machine path. Do not re-run with `--force` to replace it: `--force` also replaces fusion-tea's ratified `modeling_project/STUDY_POLICY.md`. To take the shipped command, delete the file and re-run, or re-run at a terminal and answer `o` for that file alone.

fusion-tea's own tests that read the skill text keep passing on the installed copy, as Phase 5 checked against the shipped files: `tests/study/test_annex.py` (the runbook cites only the four annex sections), `tests/study/test_record_template.py` (two full `source_digest` blocks) and `tests/study/test_policy_path.py` (the skill and runbook name `modeling_project/STUDY_POLICY.md`).

**Rehearsal:** the same, on `$FTC`. **Observed in the rehearsal:** *(O3)*

## Step 8: verify

### 8a. The study suite (cut 1)

```bash
uv run --no-sync pytest tests/study tests/models/test_model_family_spines.py -q -rs --junitxml=<run>/junit.xml
```

**Pass rule:** compare run C (after step 7) with run B (dependencies moved, nothing switched) using `$EV/rehearsal/junit-diff.py`. No test fails or skips in C that passed in B, and a test failing in both fails with the same message. B against A (as-is) is recorded and classified for step 9; it is not a gate on the move.

**Rehearsal:** runs A, B and C on `$FTC`, one shell, `env.sh` sourced, each run's `env.txt` written by `record_env <run>` (`python -V`, `uv pip list`, teax HEAD, the licence by presence, and `env | grep -E '^(STOP_PARSER_[A-Z_]*|TEAX_SIMKIT_PATH|SYSML_CODEGEN_PROJECT_ROOT|PYTHONPATH)='`). Design Appendix H3's pattern `'^(STOP_PARSER_|…)='` needs `=` straight after the prefix, so it matches no `STOP_PARSER_` name; `STOP_PARSER_[A-Z_]*` is the corrected form. Compare with `python3 $EV/rehearsal/junit-diff.py <B>/junit.xml <C>/junit.xml`, which exits non-zero when C breaks the pass rule. **Observed in the rehearsal:** *(O3)*

### 8b. Re-verify one existing record

Use `exploration/stellarator_e2e/studies/20260916-primary-loop-sizing` if its sealed identity recomputes; otherwise the newest sealed-identity record that does.

1. Before and after step 5, run `identity.assert_matches` over the record's identity document and its package. The digest is the same both times: no sealed identity changes, because every route calls `build_sealed`, whose digest is the package's sealed fingerprint (DD14).
2. Run the installed `verify` over the record's store, package and manifest with the record's seed and sample size: `uv run --no-sync sysml-codegen study verify --package … --manifest … --identity … --store … --seed <record's> --sample-size <record's> --out /tmp/reverify.json`.
3. Compare `/tmp/reverify.json` with the record's `results/verification_summary.json`. The sampled cases, the re-derived verdicts and the worst deviation agree. Only `tool.path`, `tool.source_digest` and `command[0]` differ, from `scripts/study/verify.py` to `sysml_codegen/study/verify.py` (B2): that is expected, not a failure.
4. `git status --short -- <record directory>` prints nothing: the record's committed files are untouched.
5. List every committed `package_identity.json` of kind `effective` whose adapter sources name a rewritten route file. None is expected.

**Rehearsal:** on `$FTC`. **Observed in the rehearsal:** *(O3)*

### 8c. `integrate` on a real package (needs teax and the licence)

In run B (local tools) and run C (installed), run `integrate` with the supplement's full stellarator request (`docs/integration_seam_operator_guide.md` § The full invocation in fusion-tea). In C, also run the gate-7 driver directly:

```bash
PYTHONPATH=$FTC:$TEAX_SIMKIT_PATH SYSML_CODEGEN_PROJECT_ROOT=$FTC uv run --no-sync python -c 'import sys; from sysml_codegen.study.read_coverage import run_route; run_route(*sys.argv[1:])' exploration/stellarator_e2e/studies study_route execute_baseline /tmp/rc exploration/stellarator_e2e/pkg/stellarator_tea exploration/stellarator_e2e/studies/manifest.json rehearsal
```

`SYSML_CODEGEN_PROJECT_ROOT` is set to match what the seam hands its producers; the driver does not need it. The package is in `$FTC`'s git work tree, and since sysml-codegen `2e21955` the driver resolves the root from the package before it observes the route. Only a package in no work tree needs the variable, and the driver then refuses with a message naming it.

**Expected:** B and C stop at the same gate with the same class and condition, or both return `CANDIDATE`. Their returns differ only in closed-list fields under SC12's comparator (`$EV/parity/`). The C driver writes `read_coverage.json` with `outcome: pass` and `violations: []`.

**Rehearsal:** the orchestrator runs it on `$FTC`. **Observed in the rehearsal:** *(O3)*

## Step 9: consequence note

Moving the sysml-codegen pin also moves the code generator fusion-tea's packages are built with, by about 142 commits at the time of drafting (count `8a758e9..M_CODEGEN`). `integrate`'s regeneration gate requires regeneration to move no byte, so gate 2 may refuse fusion-tea packages, and gate 4's snapshots may drift, until each package is regenerated in its own modeling item. That is the pin move's consequence, not this switch's. Record what B against A (8a) and 8c showed, so the owner decides the pin move with it in view.

**Observed in the rehearsal:** *(O3)*

## Commit

Stage the paths from `git status --short` by name, never with `git add -A`: the step 2 and step 4 files if those steps ran, `pyproject.toml`, `uv.lock`, `tests/test_dependency_provenance.py`, the eight wrappers, the nine route modules (`"${ROUTES[@]}"`), the removed `scripts/study/schemas/`, the step-5 test files, `.gitignore`, the removed `.claude/skills/run-study` and `.agents/skills/run-study`, the installed `.agents/skills/run-study/`, and `.sysml-codegen/install.json`. The `.claude/skills/run-study` link and `.claude/commands/teax-completion.md` stay untracked: fusion-tea's `.gitignore` ignores `.claude/skills/*` and `.claude/commands/*`, and a link is not matched by a directory whitelist, so this is how Item 2 left `run-goal`'s link. `install-commands` makes them in each checkout. `.venv/integration.env` is gitignored and stays out. A subject that fits: "Use the study layer installed from sysml-codegen at M_CODEGEN". Do not push; the owner pushes and merges the branch.
