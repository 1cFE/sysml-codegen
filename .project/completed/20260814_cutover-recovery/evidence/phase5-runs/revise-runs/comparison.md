# REVISE step 7a — three consecutive gate runs on the retired tree

**Measured:** 2026-08-12. **Verdict: no divergence.** Every semantic field is identical across
the three runs, and every field matches the value the stage notes predicted.

This is measurement and record only. No product, test, ledger, or doc file was changed. The only
files this stage adds are the record tooling under `evidence/phase5-runs/` and the run artifacts
under `evidence/phase5-runs/revise-runs/`.

## What was measured

| | |
|---|---|
| codegen HEAD | `c0ceb24b886c595b55dcf1cea4c0d1cc5b183446` (branch `item7-rebuild`) |
| agentic-mbse HEAD | `3fbda2fbfa82f43d59b0262cedd7a7ae241f37d0` (branch `item7-rebuild`) |
| TEAx HEAD | `fa0e06a99b070346e68a3b3c29cfec546f3ac728` (branch `main`, ahead 1) |

The three HEADs were re-read at the start of every run and recorded in each run's `heads.tsv`;
all three files are byte-identical, so the three runs measured the same trees.

## Environment gate

Asserted first in every run, and the run aborts if it fails. All three `env.json` files are
byte-identical (`a515d899…`).

| | |
|---|---|
| import-path gate | PASS |
| `sysml_codegen` | `/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py` |
| `agentic_mbse` | `/home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py` |
| `simkit` | `/home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py` |
| interpreter | `/home/reid/1cfe/item7-rebuild-venv/bin/python`, 3.12.11 |
| licence key present | true |
| toolchain | syside 0.8.4, ruff 0.16.2, mypy 2.3.0, pytest 9.1.1, pydantic 2.13.4, jinja2 3.1.6 |

Neither protected original (`/home/reid/1cfe/agentic-mbse`, `/home/reid/1cfe/sysml-codegen`) was
touched. The `.env` in the companion checkout was read for the licence key and nothing else.

## The three-run comparison

| field | run1 | run2 | run3 | identical |
|---|---|---|---|---|
| env import-path gate | PASS | PASS | PASS | yes |
| licence key present | true | true | true | yes |
| HEAD codegen | `c0ceb24` | `c0ceb24` | `c0ceb24` | yes |
| HEAD agentic | `3fbda2f` | `3fbda2f` | `3fbda2f` | yes |
| HEAD teax | `fa0e06a` | `fa0e06a` | `fa0e06a` | yes |
| codegen licensed suite | 1705 passed, 34 skipped, 65 deselected | 1705 passed, 34 skipped, 65 deselected | 1705 passed, 34 skipped, 65 deselected | yes |
| codegen suite `no live syside license` lines | 0 | 0 | 0 | yes |
| codegen suite skip-reason set | identical (`0b9cbd64…`) | identical | identical | yes |
| execution lane (`tests/execution -m execution`) | 65 passed | 65 passed | 65 passed | yes |
| `-k corpus` | 9 passed, 1795 deselected | 9 passed, 1795 deselected | 9 passed, 1795 deselected | yes |
| `capture_v6_batch.py --verify` | 15 captured, 22 refused, 0 deviations | same | same | yes |
| `--verify` per-fixture body | identical (`4c5bee16…`) | identical | identical | yes |
| non-timestamp fixture diff lines after `--verify` | 0 | 0 | 0 | yes |
| `capture_v6_batch.py --check` | 15 captured, 22 refused, 0 deviations | same | same | yes |
| `ruff check src` | 14 errors | 14 errors | 14 errors | yes |
| `ruff check src tests scripts` | 641 errors | 641 errors | 641 errors | yes |
| `mypy src` | 57 errors in 11 files (71 checked) | same | same | yes |
| agentic default suite (`pytest tests/`) | 1826 passed, 1 skipped, 5 deselected | same | same | yes |
| agentic `ruff check src` | 1 error | 1 error | 1 error | yes |
| agentic `ruff check tests` | 120 errors | 120 errors | 120 errors | yes |
| agentic `mypy src` | 108 errors in 26 files (59 checked) | same | same | yes |
| `check_ledger_4a.py paths` | 304 rows checked, 0 problems | same | same | yes |
| `check_ledger_4a.py surface` | 0 unrowed breakages | same | same | yes |
| `check_ledger_4a.py groups` | all six affected=0, READY | same | same | yes |
| `check_ledger_4a.py replacements` | 221 green / 81 not-required / 0 FAIL | same | same | yes |
| replacements per-row verdicts | identical (`383a6045…`) | identical | identical | yes |
| `check_proof_integrity.py` | 0 problems over 0 blocked files | same | same | yes |
| `check_doc_distinctness.py` | 31 documents, 0 identical-content groups | same | same | yes |
| `git diff --check` codegen | clean (empty, rc=0) | clean | clean | yes |
| `git diff --check` agentic | clean (empty, rc=0) | clean | clean | yes |
| `git status` codegen | `item7-rebuild`, 4 untracked record-tooling paths | same | same | yes |
| `git status` agentic | `item7-rebuild`, clean | same | same | yes |
| `git status` teax | `main…origin/main [ahead 1]` | same | same | yes |
| scale node/module/entry-point counts + envelope bytes | identical (`c52a35f8…`) | identical | identical | yes |

**33 / 33 fields identical across all three runs. No rule-10 stop.**

`check_ledger_4a.py groups` reads all six 4B groups at `affected=0 READY`. That is not the Phase 5
reading (`4B-G2 affected=76`, `4B-v5-family affected=158`) because the retirement has since
executed those groups; zero affected is the retired tree's correct value.

### How "identical" was established

Not by eye. Every log that carries no wall-clock number was compared by MD5 across the three run
directories and is byte-identical: `env.json`, `heads.tsv`, `batch_verify.log`, `batch_check.log`,
`ledger_paths.log`, `ledger_surface.log`, `ledger_groups.log`, `proof_integrity.log`,
`doc_distinct.log`, `ruff_src.log`, `ruff_all.log`, `mypy_src.log`, `mb_ruff_src.log`,
`mb_ruff_tests.log`, `mb_mypy_src.log`, `diff_check_cg.log`, `diff_check_mb.log`, `status_cg.log`,
`status_mb.log`, `status_teax.log`.

The four logs that do carry timings were compared on their semantic content with the timings
stripped:

- the four pytest logs — the count clauses and the full `SKIPPED` reason list,
- `ledger_replace.log` — the `<verdict> <row-id>` pair and every collected/passed count for all
  302 rows (`383a6045ccb28c271d7ca2f6ea72a6fb` in all three runs),
- `scale.log` — every node, module, entry-point and envelope-byte count
  (`c52a35f84fb6b8ddb59f539e290ce0cf` in all three runs).

### Against the expected values

Every field the brief predicted was measured, and every one matched: codegen 1705 / 34 / 65,
exec 65, `--verify` 15/22/0, corpus 9, ruff 14 / 641, mypy 57 in 11, paths 304/0, surface 0,
groups all-affected-0 READY, replacements 221/81/0, proof 0/0, distinctness 31/0; agentic
1826 / 1 / 5, ruff src 1 / tests 120, mypy 108 in 26. Nothing had to be explained.

The licence proof is the one that matters most and it is direct: the codegen suite ran with
`-rs`, so every skip prints its reason, and `no live syside license` appears **zero** times in all
three runs. The 34 skips are model-content skips, not licence skips.

## Scale and RSS (measurement, not an identity field)

Wall-clock is not a semantic result, so it is reported rather than compared for identity. Warm-up
plus three measured runs per fixture, per battery run — nine measured samples per fixture in total.

| fixture | live elaborate s | generate live s | peak RSS MiB (cumulative) |
|---|---|---|---|
| `fusion_tea` | 0.117–0.133 | 0.192–0.196 | 222.7–244.7 |
| `solar_battery_d5` | 0.326–0.349 | 0.808–0.827 | 264.8–285.0 |
| `catf_mfe_d5` | 5.005–5.228 | 5.218–5.426 | 308.9–326.4 |

RSS is the process-cumulative peak, so it rises monotonically within a battery run by construction;
the spread across runs is a few percent. Node counts and envelope bytes are byte-stable
(`fusion_tea` 112 046 B, `solar_battery_d5` 1 104 445 B, `catf_mfe_d5` 621 270 B).

## Step wall-clock

| step | run1 s | run2 s | run3 s |
|---|---|---|---|
| codegen licensed suite | 86 | 87 | 86 |
| agentic suite | 15 | 14 | 15 |
| execution lane | 4 | 5 | 4 |
| `-k corpus` | 1 | 1 | 1 |
| `--verify` | 8 | 7 | 7 |
| ledger replacements | 666 | 665 | 667 |
| scale | 78 | 75 | 75 |
| whole run | ~870 | ~865 | ~870 |

## What the scripts had to be adapted for

`run_candidate_battery.sh` was written before the retirement. `run_revise_battery.sh` is its
adaptation, and the differences are these:

- **`scripts/run_elaboration_corpus.py` no longer exists** — the retirement deleted it. The
  surviving corpus gate is the ledger test reached by `-k corpus`, which is what the brief names,
  so the driver step is gone rather than replaced.
- **The codegen suite runs with `-rs`.** Without it the skip reasons never print, and the
  zero-licence-skip claim would rest on a count instead of on the reasons.
- **The agentic suite is invoked as `pytest tests/`**, per the brief, not as a bare `pytest`.
- **Four gates were added** that the Phase 5 battery did not run: `check_ledger_4a.py
  replacements`, and the agentic side's `ruff check src`, `ruff check tests`, and `mypy src`.
- **The import-path gate is stricter.** Phase 5 accepted any of the four allowed prefixes for any
  module; this one additionally pins `sysml_codegen`, `agentic_mbse` and `simkit` each to its own
  required worktree, so a cross-wired venv cannot pass.
- **Scale measurement still applies unchanged** — `measure_scale.py` imports only surviving
  modules and all three fixtures are present.

## Files

```
evidence/phase5-runs/run_revise_battery.sh    one complete run
evidence/phase5-runs/chain_revise.sh          the three runs, back to back
evidence/phase5-runs/compare_revise_runs.py   the field-by-field comparator
evidence/phase5-runs/build_comparison.sh      comparator wrapper
evidence/phase5-runs/revise-runs/run{1,2,3}/  every step's log, exit code and duration
evidence/phase5-runs/revise-runs/run{1,2,3}.console
evidence/phase5-runs/revise-runs/comparison.md   this file
```
