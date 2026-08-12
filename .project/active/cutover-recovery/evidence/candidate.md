# Phase 5 candidate — the repeatable two-repository candidate, and the owner's decision surface

**Status:** ASSEMBLED. Owner disposition **PENDING**. The independent audit is a separate stage
and has not run against this record.
**Assembled:** 2026-08-11
**Authority:** `.project/active/cutover-recovery/plan.md` — Phase 5, "Changes required"
**Record commit:** `013d6a1` — this record and its run artifacts only; it changes no production
or test file, so the candidate under review is the tree at `c4e9b76`.
**Machine-readable twin:** `evidence/candidate.json` (every number below is derived there; the
builder is `evidence/phase5-runs/build_candidate.py`)

This record does two things and nothing else. It **certifies what the current tree pair is** —
measured three times, identically — and it **prices the decisions the owner has to make**. It
takes no decision itself. Every entry in the decision surface was recorded earlier, in the plan
or in an audit; this collates them with their evidence pointers and their costs.

What the candidate contains, stated plainly:

- The exact route is the **sole public generation authority**, since Slice 3E.
- The legacy string-resolution stack is **present in the tree, importable, and unreachable from
  any public caller**. Nothing has been retired.
- The retirement of that stack is **prepared**: a runbook whose four steps were each executed in
  order in a scratch worktree and measured green, 55 reviewable patches, and a PROPOSED v6
  recapture batch. Executing it is gated on owner acceptance.
- **Seven items need an owner ruling** before the retirement runs. Every "green at every
  boundary" in the runbook is green *with those seven held out*, as a named 113-node trim.

---

## 1. The candidate

| | sysml-codegen | agentic-mbse |
|---|---|---|
| Path | `/home/reid/1cfe/sysml-codegen-item7-rebuild` | `/home/reid/1cfe/agentic-mbse-item7-rebuild` |
| Branch | `item7-rebuild` | `item7-rebuild` |
| OID | `c4e9b76c024b7852da6ebccb46ab62ac4e7a4bfb` | `cc6c7a7411f6338a4811a7cc58ca002c29ef177b` |
| Item 6 base | `1672c5766f67e7716f3c9f8f636c21e2ea444601` (`source-identity-epic`) | `5088b417c9e5453271291d46cd5fb23fc0579b1e` (`elaborate-first-salvage`) |
| Diff vs base | 362 files changed, 63,324 insertions, 2,074 deletions | 5 files changed, 268 insertions, 53 deletions |
| Name-status | 249 added / 111 modified / **2 deleted** | 5 modified, 0 added, 0 deleted |
| Commits since base | 108 | 2 |
| Status at the recorded OID | clean (two untracked paths, both this stage's own: the Phase 5 brief and `evidence/phase5-runs/`) | clean |

The two deleted paths are `src/sysml_codegen/analysis/signature_extractor.py` and
`tests/unit/test_signature_extractor.py` — ledger rows **L-006** and **L-241**, group 4B-G1,
executed at `6ba346e`. Nothing else has been deleted anywhere in the recovery.

The two agentic-mbse commits are `8b63393` (an exact constraint gate beside the neutral one) and
`cc6c7a7` (a mis-encoded manifest warns instead of aborting the check).

**Pinned TEAx:** `/home/reid/1cfe/teax` at `fa0e06a99b070346e68a3b3c29cfec546f3ac728`, as
expected.

**Forensic, do-not-merge** (preserved in Phase 1, referenced by nothing in the candidate):
sysml-codegen `07531e64ed912d6046afce47ef0d958605e6ca08`, agentic-mbse
`ed5b8b02a3064e767799cc6ee58e0119e9bfecba`, both on `item7-forensic-20260810`.

### Path inventory

| | sysml-codegen | agentic-mbse |
|---|---:|---:|
| Tracked files | 1,888 | 1,834 |
| Production modules (`src/**.py`) | 87 | — |
| Test modules | 257 | 67 |
| Fixture directories | 94 | — |
| Numbered reference documents | 31 | — |
| Scripts (`scripts/**.py`) | 47 | — |

---

## 2. Environment

Asserted **before** any measurement in each of the three runs, as the plan requires after the 4D
resolution trap. The gate reads PASS in all three: no import resolves into an original or
forensic worktree.

```
python       3.12.11   /home/reid/1cfe/item7-rebuild-venv/bin/python
sysml_codegen  /home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py
agentic_mbse   /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py
simkit         /home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py
jinja2         3.1.6      syside 0.8.4      pydantic 2.13.4
pytest         9.1.1      ruff   0.16.2     mypy     2.3.0
license      set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a   (key present)
```

Installed distributions: `sysml-codegen 0.1.0`, `agentic-mbse 0.1.2`, `teax-simkit 0.1.0`,
`syside 0.8.4`. There is no separate producer distribution — the SysML producer ships inside
`syside`, so 0.8.4 is the producer version too.

**One harness correction, recorded rather than hidden.** The first attempt at run 1 reported ten
agentic-mbse failures, all `FileNotFoundError: 'python'`: several of that suite's tests shell out
to a bare `python`, and the host's PATH carries only `python3`. That is a property of the runner,
not of the candidate. The runner now puts the acceptance venv's `bin` on PATH, and the discarded
run is kept in full at `evidence/phase5-runs/run0-harness-defect/` so the correction can be
checked rather than taken on trust. The three runs below are the first three runs after it.

---

## 3. Three consecutive complete runs

Every field below was compared across the three runs programmatically, not by eye
(`build_candidate.py`, `three_runs_identical`). **All identical.**

| Gate | run 1 | run 2 | run 3 |
|---|---|---|---|
| Full licensed codegen suite | **3862 passed / 47 skipped / 53 deselected**, 0 failed | 3862 / 47 / 53 | 3862 / 47 / 53 |
| `no live syside license` skip lines | 0 | 0 | 0 |
| agentic-mbse suite, from the paired worktree | **1825 passed / 1 skipped / 5 deselected** | 1825 / 1 / 5 | 1825 / 1 / 5 |
| Execution lane (`-m execution`), incl. real TEAx | **53 passed**, 0 skipped | 53 | 53 |
| Corpus ledger tests | **12 passed** | 12 | 12 |
| Corpus driver, 37 paths — exact arm | **15 graphs / 22 `ElaborationError`** | 15 / 22 | 15 / 22 |
| Corpus driver — legacy arm | 36 graphs / 1 `CodeGenerationError` | 36 / 1 | 36 / 1 |
| Exact code multiset | `SI_SELF_BINDING` ×75, `SI_EXPRESSION_SOURCE_UNSUPPORTED` ×7 | same | same |
| Per-fixture outcome digest | `f8da45e7…9393` | same | same |
| `capture_v6_batch.py --verify` | **15 captured / 22 refused / 0 deviations** | 15 / 22 / 0 | 15 / 22 / 0 |
| `capture_v6_batch.py --check` | 15 / 22 / 0 | 15 / 22 / 0 | 15 / 22 / 0 |
| `ruff check src` | 16 | 16 | 16 |
| `ruff check src tests scripts` | 866 | 866 | 866 |
| `mypy src` | 69 errors in 16 files (87 checked) | same | same |
| `check_ledger_4a.py paths` | **303 rows, 0 problems** | 303 / 0 | 303 / 0 |
| `check_ledger_4a.py surface` | 0 unrowed breakages | 0 | 0 |
| `check_ledger_4a.py groups` | all six READY | all six READY | all six READY |
| `check_proof_integrity.py` | 0 problems over 0 blocked files | same | same |
| Doc distinctness | 31 documents, 0 identical-content groups | same | same |
| `git diff --check`, both repos | clean | clean | clean |
| Wall clock, whole battery | ~3m 40s | ~3m 45s | ~3m 45s |

**Both error classes are classified separately in every run.** The driver records `error_type`
beside the code list and never collapses one class into the other. Across the 37 paths the exact
route raises `ElaborationError` 22 times and `ElaborationDiagnosticError` **zero** times; the
single legacy error is a `CodeGenerationError`. That the diagnostic class is unexercised is a
property of this corpus, not a relaxation of the rule.

**The `--verify` run writes nothing.** After each of the three `--verify` runs — which re-capture
all 15 v6 snapshots through the shipped public capture entry point — `git status --porcelain`
reported **no modified tracked file**, and the non-timestamp diff filter caught 0 lines. Capture is
byte-deterministic, and the committed batch is reproducible from the model.

**Real TEAx, at the anchor values.** The execution lane's real-TEAx nodes build the package
through the shipped `run_codegen` on both the live and relocated-v6 routes, discover modules
through the generated `create_*_registry` surface, and execute through SimKit's own pipeline. The
anchors are asserted inside the tests, not restated here: exactly eleven published channels, LCOE
`270.1211779380445` within `1e-6` of the independently hand-transcribed value in
`tests/execution/fusion_tea_arithmetic.py`, live and relocated executing to equal outputs, and the
relocated package built with no model tree present.

**The 40-minute gate, run once out of band.** `check_ledger_4a.py replacements` runs one pytest
invocation per proof-node row, so it is measured separately rather than three times:
**219 green / 82 not-required / 0 fail**, on
the current tree. Those are the same three numbers the plan records for the *post-retirement*
state, which is the point of the gate: the replacement proofs hold on both sides of the
retirement. It covers **301 of the ledger's 303 rows**; the two it emits nothing for are `L-036`
and `L-037`, which are exactly the two owner-gated dual rows that cannot execute at all (§7.3,
item 1).

---

## 4. Reconciliation against the Phase 2 baseline

The Phase 2 inventory is `evidence/baseline.json`, measured 2026-08-10 on the clean rebuild
worktrees. Test inventory is compared at module granularity from `git ls-files tests`, and node
counts from the suite summaries.

### sysml-codegen — 218 modules → 257

| Delta | Count | Authority |
|---|---:|---|
| Removed | **1** | `tests/unit/test_signature_extractor.py` — ledger **L-241** with production row **L-006**, group 4B-G1, executed at `6ba346e`. The responsibility moved to `generation/preservation.py`, and the checker re-proves it green (73 nodes). |
| Added | **40** | Every one is traceable to the commit that introduced it, and every commit is a named slice or gate. Full mapping in `candidate.json`. |

The 40 additions group as: 5 from Slice 3A (`fe0b855`, v6 snapshot and source admission), 5 from
3B (`d91431b`, receipt-bound context and exact projection), 2 from 3C (`7af5dc9`, constraint
identity), 2 from 3D (`848628b`, real TEAx), 1 from 3E (`430e26a`, the authority switch), 13 from
Gate 4C part 1 (`5dfb900`, the exact-route specimens), and 12 from the later 4C parts, 4D and the
Phase 4 audit follow-up (`6d58ad2`, `d2d032f`, `b146ec6`, `bba3d92`, `c674064`, `1935af3`,
`804d8a2`, `f40a745`, `ab30659`, `31f973d`, `858a6a6`).

**Node count.** Phase 2 collected 3,423 nodes (3,358 passed / 47 skipped / 18 deselected). The
candidate reads 3,862 passed / 47 skipped / 53 deselected. The skip count has not moved once in
the whole recovery. The last recorded suite total before this stage was **3,854** at `ab30659`;
the **+8** since is exactly the two test modules added after it — `test_runbook_patches.py` and
`test_public_route_baselines.py`, 8 nodes between them, measured by collection.

### agentic-mbse — 67 modules → 67

No module added, none removed. Nodes move from 1,819 passed to **1,825 passed** (+6), from the two
coordinated commits `8b63393` and `cc6c7a7`, which add `test_executable_profile.py` and
`test_sysml_quality_checks.py` nodes beside the existing ones.

### Corpus — two rows moved since Phase 2, both with ledger authority

The Phase 2 baseline recorded the exact arm at 13 graphs / 23 errors. It now reads **15 graphs /
22 errors**. Comparing per fixture, exactly two rows moved, and no other row moved at all:

| Fixture | Phase 2 | Candidate | Authority |
|---|---|---|---|
| `agg_literal_probe` | `CodeGenerationError` | graph | diff-ledger row **1**, `expected-fix` — the B37-01 ruling, which predicted this cell moving when the front gate became a graph-level emptiness gate in Slice 3A |
| `fusion_tea` | `ElaborationError`, 3× `SI_SELF_BINDING` | graph | diff-ledger row **15**, `expected-fix` — Slice 3D migrated the customer model's fifteen self-named bindings to the D-5 form (census obligation `B37-15`) |

`test_elaboration_corpus_ledger.py` compares the per-fixture outcome **strings** for all 37
against the amended ledger on every suite run, so this reconciliation is enforced continuously,
not just here.

---

## 5. Scale

**Budget authority.** The Item 7 spec records one, `[INFERRED] R10` in
`.project/active/elaborator-cutover/spec.md`: thresholds stated for the migrated `fusion_tea`
fixture, with the explicit note that changing them takes a spec amendment. Measured with one
warm-up plus three timed runs per fixture, through public entry points only, on an otherwise
quiet machine after the three battery runs.

### fusion_tea — measured against the declared budget

| Phase | Budget | run 1 | run 2 | run 3 | |
|---|---:|---:|---:|---:|---|
| Live load + elaboration | 10.0 s | 0.113 | 0.116 | 0.114 | ✅ |
| Projection | 2.0 s | 0.0029 | 0.0028 | 0.0028 | ✅ |
| Capture + envelope serialization | 5.0 s | 0.160 | 0.163 | 0.163 | ✅ |
| Generation + seal (live) | 30.0 s | 0.187 | 0.189 | 0.185 | ✅ |
| Generation + seal (from v6 snapshot) | — | 0.085 | 0.098 | 0.086 | — |
| Peak RSS (process, cumulative over all runs) | 512 MiB | 222 | 237 | 237 | ✅ |
| v6 envelope size | 25 MiB | 0.107 MiB (112,046 bytes, identical in all three) | | | ✅ |

Real-TEAx execution has a 30.0 s budget. The whole 53-node execution lane — which builds and
executes both the live and the relocated Fusion Tea packages inside it — completes in **3.4 s** in
every run, so the budget holds with a wide margin. Graph counts are identical across the three
runs: 56 attribute nodes, 7 calculations, 1 constraint, 8 occurrences, 9 modules, 27 entry points.

### The two D-5 scale variants — recorded as their own declared baseline

R10's thresholds are declared for `fusion_tea` only. These numbers are the new baseline for the
variants, with **no pass/fail claim**, and are shown against fusion_tea's shape for reference.

| Fixture | Live elaborate | Project | Capture | Generate (live) | Generate (snapshot) | Envelope | Graph |
|---|---:|---:|---:|---:|---:|---:|---|
| `solar_battery_d5` | 0.318–0.330 s | 0.035 s | 0.558–0.574 s | 0.747–0.769 s | 0.571–0.586 s | 1,104,445 B | 350 attrs / 77 calcs / 42 occ / 77 modules / 199 EPs |
| `catf_mfe_d5` | 4.999–5.049 s | 0.014 s | 5.149–5.221 s | 5.213–5.304 s | 0.260–0.283 s | 621,270 B | 376 attrs / 42 calcs / 9 constraints / 61 occ / 42 modules / 60 EPs |

Two things a reader should take from that table rather than re-derive:

- **`catf_mfe_d5` costs five seconds in live elaboration, and everything live inherits it.**
  Capture and live generation are elaboration plus a small tail. Generating the same model from a
  sealed v6 snapshot takes 0.26 s — roughly twenty times faster. That is the offline route's
  practical argument, measured.
- **Held against fusion_tea's thresholds, `catf_mfe_d5`'s capture would sit just over the 5.0 s
  capture line** (5.15–5.22 s), for that same reason. It is not a budget breach, because no budget
  is declared for this fixture; it is the number an owner would want before declaring one.

Envelope bytes and every graph count are identical across the three runs for all three fixtures.

---

## 6. Residue and boundary checks

Run by `evidence/phase5-runs/check_residue.sh`; raw output in
`evidence/phase5-runs/residue.json`. The greps are scoped to shipped code and data — `src`,
`tests`, `scripts`, `docs`, `pyproject.toml`. The recovery's own records under `.project/` cite
the forensic OIDs deliberately; that is the archive, not an import.

| Check | Result |
|---|---|
| Forensic OIDs or `item7-forensic` referenced from shipped paths | **none** |
| Import-boundary tests (`test_elaboration_import_boundaries.py`) | 14 passed |
| Single-authority pins (`test_public_authority_switch.py`) | 19 passed |
| v6 batch pins (`test_v6_recapture_batch.py`) | 58 passed |
| Runbook patch pins (`test_runbook_patches.py`, `test_retirement_worklist.py`) | 12 passed |
| `retirement_worklist.py check` | 0 problems |
| `git diff --check`, both repos | clean, all three runs |

**One residue class found, named rather than rounded down.** 38 tracked files carry an absolute
path into an *original* checkout (`/home/reid/1cfe/sysml-codegen/…`). Thirty-five of them are v5
`extraction_snapshot.json` fixtures — captured long ago in the original worktree, and exactly the
non-portability the v6 batch and the L-118 fix exist to end. They belong to the retiring v5 family
and go with it. The other three are the documented license-`.env` convention, not imports:
`tests/fixtures/v6_recapture_batch/README.md`, `scripts/spikes/_helpers.py`,
`scripts/probes/probe_item1_phase0.py`. **No v6 snapshot and no manifest entry contains an
absolute path** — re-checked by the batch's own test on every suite run.

**Clean status at the recorded OIDs.** Both repositories report clean at every one of the three
runs. The only untracked entries in sysml-codegen are this stage's own: the Phase 5 brief and
`evidence/phase5-runs/`, both committed with this record.

---

## 7. The owner decision surface

Nothing here is new. Each entry names what it is, where the evidence is, and what accepting or
deferring costs.

### 7.1 Decision — the PROPOSED v6 recapture batch

**What it is.** 15 v6 snapshots at `tests/fixtures/<name>/instance_graph_snapshot.json` plus 22
typed refusal records in `tests/fixtures/v6_recapture_batch/batch.json`, produced by
`scripts/capture_v6_batch.py` through the shipped public capture entry point, so the batch cannot
drift from the product. Every outcome matches the amended Phase 2 corpus ledger with **0
deviations**, both error classes with exact code multisets. It is marked **PROPOSED** and is
authority for nothing until the owner accepts.

**Evidence.** Plan, "Gate 4C part 4 / Part A" (commit `d2d032f`);
`tests/conformance/test_v6_recapture_batch.py`, 58 nodes that re-derive every claim from the
committed bytes, most of them license-free; re-verified 15/22/0 in all three runs above, writing
nothing.

**Accepting costs** nothing beyond the review: the batch is already in the tree and green.

**Revising costs a measured 95 outcomes.** Removing the 15 snapshots the batch added leaves **38
failed and 57 errors** across the suite. Revising means re-running `capture_v6_batch.py` and
re-greening those, not reverting a commit. It is Git-reversible, and it is not free. (Phase 4
audit F4.)

### 7.2 Decision — the prepared retirement

**What it is.** The legacy stack ships **present-but-unreachable**. Its removal is prepared as a
four-step runbook, and every step was executed in order in a scratch `git worktree` with the full
battery run at each boundary. All four end with **0 failed and 0 errors**. The audited tree was
never mutated; nothing has retired.

| Step | Subject | Rows | Post-state |
|---|---|---:|---|
| 1 | G2′, the v5 read path | 99 | 2352 passed / 43 skipped / 145 deselected, 0 failed |
| 2 | the v5 family | 155 | 1582 / 34 / 148, 0 failed |
| 3 | G3′ (`resolution/producer_completeness.py`) | 1 | 1582 / 34 / 148, 0 failed |
| 4 | G4′ (`elaboration/diff.py`, `tests/helpers/legacy_route.py`) | 3 | 1582 / 34 / 148, 0 failed |

The step lists are **derived** from the ledger's own columns by
`scripts/retirement_worklist.py` and checked by a test node — 257 rows placed across the four
steps and the owner-gated entry. The per-file edits ship as **55 reviewable patches** (12 in
`runbook-patches/step1/`, 43 in `runbook-patches/step2/`), each re-checked against the tree by
`tests/unit/test_runbook_patches.py`. After the retirement,
`check_ledger_4a.py replacements` reads **219 green / 82 not-required / 0 fail** — measured, not
projected.

**The property that holds it in place.** Two conformance nodes in
`tests/conformance/test_public_authority_switch.py` pin the present-but-unreachable state: the
construction closure reaches no legacy authority, transitively; and the CLI's *import* closure
still reaches a pinned four-module set, of which three are reached, pinned by name so the residual
cannot silently grow. `CLAUDE.md` states the honest measured number beside it — `sysml_codegen.cli`
imports **10 of the 11** listed legacy modules. Importable is not reachable, and the number to
carry into a retirement decision is ten, not three.

**Accepting** means the four steps become mechanical work after the seven rulings below.
**Deferring** costs nothing immediately and keeps a dead stack in the tree that every future
reader has to be told about — which is what the retiring banners on documents 03, 04, 05, 07, 09,
10, 11, 12, 13, 17, 24 and 25 currently do.

**One condition, stated in the open.** "Mechanical" holds *only* with the seven items below ruled
on first, or held out deliberately, exactly as the simulation held them.

### 7.3 The seven owner-gated items

Together these are the 113-node provisional trim in `runbook-patches/provisional-trim.txt`. Every
"0 failed" in §7.2 is measured with them held out.

| # | Item | Measurement | What the ruling costs |
|---|---|---|---|
| 1 | **The dual qualifier drop** — L-033, L-034, L-036, L-037 | All eight retained 3C duals fail under the prescribed drop (chunks 12 and 16). L-036/L-037 cannot execute at all: `agentic_mbse/validation/level4_constraints.py:55-56` and `level6_architecture.py:620-621` call the legacy members and are outside this ledger | A type migration crossing the repository boundary, or a decision to keep the name-keyed members |
| 2 | **L-033's deletion, and L-034 with it** | `compile_calc_def_exact` — the survivor — constructs a legacy `CompilationResult` at `extraction/expression_compiler.py:378`, inside its own body. L-034's name-keyed `data_models.py` fields lose their only reader at step 2 while the extractor still writes them | The same migration as item 1. Step 2 is green with both held out, which is what says the entry is separable, not optional |
| 3 | **L-135 `test_extractor.py`** | 58 of 74 collected nodes read the retiring v5 fixtures at step 1, and one more at step 2 — the constraint-drop diagnostic whose second arm asserts where catf_mfe's 65 swept constraints land. It cannot be repointed: the exact route **refuses** `catf_mfe_model`. **59 nodes** | A coverage decision about a retained subject: drop the arm, or move the subject to a fixture the exact route accepts |
| 4 | **L-153 `test_hierarchy_resolver.py` and L-100 `test_ast_dispatch_invariant.py`** | Both are `retain` rows carrying no disposition, and both break at step 1 through the conformance v5 fixtures: 44 of 46 and 3 of 20 — **47 nodes**. Their subjects survive; only their evidence source retires | Authorship: repointing them onto v6 or live evidence |
| 5 | **L-281 `test_expression_compiler.py`** | Five nodes beyond the sixteen its per-node table names read the conformance v5 fixtures | The same authorship, smaller |
| 6 | **`scripts/capture_filter.py` loses its last caller at step 2** | Two `test_capture_fixtures_filter.py` nodes go red; the four `select_fixtures` nodes that stay green cover a module nothing calls. `capture_v6_batch.py` takes positional fixture names but has no license-free unknown-name refusal, so L-292's "the same responsibility is carried" is half true | Delete the filter, or wire it into the v6 capture |
| 7 | **`snapshot/__init__.py` keeps a dead v5 surface, named by no row** | After step 2, `SNAPSHOT_FORMAT_VERSION`, `CONSTRAINT_LOWERING_MODE_*`, `VALID_CONSTRAINT_LOWERING_MODES`, `SnapshotFormatError`, `GrandfatheredSnapshotError` and `assert_snapshot_certifiable` have zero readers in `src/`, `scripts/` or `tests/` | How much v5 vocabulary the tree keeps. Nothing breaks either way, which is why no step needs it |

Items 3, 4, 6 and 7 are the class audit 4 found in L-298: a disposition note, or a silence, that
is false against the code. They were found the only way that class can be found — by executing the
step and running the suite.

**What used to be an eighth item is closed.** The nine rows whose replacement proof the retirement
itself deletes: six repoint mechanically, and the other three are answered by
`tests/conformance/test_public_route_baselines.py`, four license-free nodes that state the two
capture scripts' responsibility as a property of the public route rather than as a stored file.

### 7.4 The named residuals carried from Phases 3 and 4

| # | Residual | What it is | Evidence | Accepting / deferring |
|---|---|---|---|---|
| R1 | **Offline provenance limit** | A v6 snapshot records its sources under the portable `root-0/` referent, never the checkout path — that portability is the point. So every generated file carrying a `SysML Source:` comment differs between the live and snapshot routes **by construction**. Live-vs-snapshot byte identity is not an exact-route property and must not be asserted as one. What holds: the difference is *only* the provenance comment, and the model contract's **semantic** fingerprint is equal across the two | Plan, "Notes a reviewer should not have to re-derive"; pinned on ledger rows L-179 and L-140 | Accepting records the limit as product behaviour. There is nothing to fix without giving up snapshot portability |
| R2 | **Module `source_file` divergence** | Module `source_file` still differs across routes: live records absolute checkout paths (one still carrying a leftover `//` URI prefix), v6 records the portable referent. It reaches generated bytes only as a `SysML Source:` comment. The v6 spelling is the one the design intends (`generation/stencils.py:243`) | Plan, Slice 3B completion, "A second residual, pinned rather than fixed"; asserted by value on both sides, and the generated-package test pins the exact file set the difference reaches | Deferring keeps one cosmetic divergence. Fixing means routing the live path through admission, which would undo the arm independence Slice 3A's F2 fix established |
| R3 | **`d38_caret` — diff-ledger row 12** | A shipped-package cell amendment. A modelled finite multiplicity mints keys carrying an occurrence index; the generated `schemas/*_params.py` wrote those keys straight into a class body. Pre-existing and reachable from public `generate` — it reproduced at HEAD on this ratified corpus fixture. **Fixed** at Gate 4C part 2 (surfacing S3), with a new coverage module of 21 nodes, and the fixtures pin the *set* of unparseable files rather than asserting emptiness | Plan, S3; diff-ledger row 12 | The amendment is the record of a fixed defect. Accepting the row is accepting that the shipped key spelling changed |
| R4 | **`unresolvable_attr_probe` — diff-ledger row 36** | On the exact route this fixture now reaches generation and the module-class collision guard **refuses the package**, because two of nine formulas alias to one class name. The refusal was untyped and fired *after* the output tree was cleared, leaving a half-written package (measured: 34 files, no contracts, no seal). Ruled C2 and **fixed in Gate 4B-G0**: typed refusal, ordered before the clear, with a specimen | Plan, 3E audit F5 and the 4A approval's C2 ruling; `test_public_authority_switch.py::test_a_registry_class_name_collision_refuses_before_the_writer_runs` | Accepting the row is accepting a public refusal on a fixture legacy accepted. The defect it exposed is closed |
| R5 | **The zero-constraint report aggregator** | Legacy emits a `constraint_report_aggregator` whenever the constraint pathway runs, even with zero eligible constraints — a deliberate D11 choice. The exact route returns early instead (`elaboration/project.py:887`), and that early return **stands**: no synthetic module without content. Measured on `catf_mfe`: legacy 43 modules, exact 42 | Plan, "Named mechanism — the zero-constraint report aggregator" (orchestrator ruling 2); `test_zero_assertion_aggregator_not_assessed` is the live subject of the retiring behaviour | **A product question, not a test question.** Whether the empty-report surface is a behaviour the exact route should carry. Deferring means the surface disappears with the retirement |
| R6 | **V11 coverage is structural, not behavioural** | `elaboration/project.py` constructs every graph with `fallback_entry_points=set()` in both `run()` and `select()`, and both collectors filter on membership, so `cli._reconcile_params_coverage` runs on every generation and **cannot fire**. No fixture can seed the gap through the public surface | Plan, S2 / ledger row L-249, closed by proof on three nodes: two rot pins plus `tests/unit/test_uncovered_params.py` as the named V11 coverage owner | Accepting means the guard is a rot pin, not a live gate. The day the exact route produces fall-through entry points, the pins fail and the row becomes authorable as a behavioural specimen |
| R7 | **The units gap — surfaced, then closed** | The exact route refused a model carrying unit annotations, isolated to one character (` [m]`). Remodelling would have meant deleting annotations from **148 sites** in a customer-derived model. Ruled a bounded product gap and then **fixed** as one rule applied once: `_ExactElaborator._without_unit_annotation` unwraps the annotation before anything downstream classifies the expression. `catf_mfe_d5` now elaborates, 42 modules | Plan, Gate 4C part 6 ruling 2 (the finding) and ruling 1 (the fix); `tests/fixtures/unit_annotation_lanes` carries both spellings in one model, with the bare model as its control | Nothing outstanding. Recorded because the fixture, the pins and the deleted probe are all consequences an owner should see once |
| R8 | **S4 / Item 10 — the same-name rollup refusal** | An assembly cannot write `sum(deck_panel.capital_cost) + sum(caster.capital_cost)`: projection names an expression parameter after the reference's last member and drops the qualifier (`elaboration/elaborate.py:1901`), so both terms render `capital_cost` and the model is refused with `SI_RENDERING_COLLISION`. Every child of a costed assembly exposes the same names by construction, so this is the pattern, not an edge case. **Ruling: the refusal stands**; the workaround (one named intermediate attribute per child role) is a remodelling requirement the route imposes | Plan, S4; `test_costed_component_exact_route.py::test_a_two_term_same_name_rollup_is_refused`; documented at Gate 4D subject 4 in `modeling-assumptions.md` §4, §6 | **This is the same qualifier-dropping collapse filed as the Item 10 cross-part `child.attr` blocker.** Accepting means the modelling requirement is documentation, not a defect. It is the one entry here that reaches outside Item 7 |
| R9 | **The fingerprint residual** | The provenance-comment `executable_fingerprint` differs between the live and relocated packages. Unchanged since Slice 3D and carried through the 3E switch | Plan, Slice 3E completion, "the ruling-2 residual"; newly pinned on L-140 alongside the semantic fingerprint's equality, so the difference is recorded rather than ignored | The same shape as R1: it follows from provenance, and closing it means giving up portability |
| R10 | **The constraint-threshold disambiguator drop** | On the shipped input-key surface the exact route drops the disambiguating id from a constraint threshold key (`…__viability__81ddf10fb1d1749b__threshold` → `…__viability__threshold`). The id is retained identically in the module id and the evaluation channel. Two constraint usages with the same name under one owner would mint the same key — **no corpus model has that shape and no failure was measured** | Plan, 3E audit F1; diff-ledger row 15 | A packet question, not a defect claim. Accepting means the operator-facing surface keeps the shorter key |
| R11 | **The customer-visible entry-point key rename** | The largest customer-visible change in the recovery. Legacy names an entry point after the consuming calc-usage formal; the exact route names it after the modelled attribute that supplies it. `fusion_tea`: legacy publishes 31 keys, exact 27, sharing 13 — three collapses, ten one-to-one renames, the threshold above, and ten group moves | `evidence/3e-package-comparison.md` enumerates every delta with its consumer set | **An owner accepting this candidate should read the table, not a summary of it.** Every legacy-only key is matched to an exact-only or shared key by identical consumer set, which is the proof that no entry point was lost or gained |

Three further items are recorded rather than resolved, from Gate 4D, and belong to whoever
touches those files next: `reference/07` cites `core/graph_algorithms.py`, which has never existed
in this tree (pre-existing, needs an owner); two production docstrings are stale in the way the
documents were, and belong to the retirement commit that touches those files; and `reference/16`
and `reference/18` are stale-minor with no settled replacement content, which is authorship rather
than repair.

---

## 8. Evidence hashes

Full SHA-256 table in `candidate.json` under `evidence_hashes_sha256` — it covers the plan, both
ledger forms, the 4D update list, every audit and evidence document, the v6 batch manifest, all 55
runbook patches, the provisional trim, and this stage's own scripts. The headline entries:

| Artifact | SHA-256 |
|---|---|
| `.project/active/cutover-recovery/plan.md` | `ee37cf2ed005ad8f642fe0fbd790e48127fdd8e3a7b68455fbc92e85777630bb` |
| `evidence/baseline.json` | `8162966c0ede1b58bb4562def9e862c794d25b505b2753fb4e2a4e8ddd66aa55` |
| `ledger-4a.json` | `ee6d1a4b48628b1b06063c48cb99d7a9824769af7f9514c191d2d3213a833c48` |
| `ledger-4a.md` | `4f7a1a8395b7adf92652d70103256ee4dfaaeef346727925ec41656106ef2da6` |
| `doc-update-list-4d.md` | `a48b69bae7b2510538707a2140fd1d72fc05b854e90f533eae6e8539afc42de4` |
| `tests/fixtures/v6_recapture_batch/batch.json` | `7c72e34c6bb23d92294d27530c7d40bc26661358a6186858fbee1a6ff8c79ef7` |
| `evidence/audit-4.md` | `efb23e2a3c6205286636f683f386770162882d90e7f57814eab9eeac5968500c` |
| `evidence/3e-package-comparison.md` | `6653acb04f7b40160b650ad6e909092375cdf5dcd307fcdb2c291b961f278d97` |

Audit verdicts, for the auditor's convenience: 3A FINDINGS then CERTIFY with one named residual,
3B CERTIFY (7 findings), 3C CERTIFY (4), 3D CERTIFY (5), 3E CERTIFY (6), audit 4 FINDINGS (8, all
closed at the Phase 4 audit follow-up).

---

## 9. What this record does not claim

- It is **not** an audit. The independent audit is the next stage and has not read this.
- It does **not** accept anything. The PROPOSED batch is still PROPOSED, the retirement has not
  run, and the seven gated items are unruled.
- "Green at every boundary" in §7.2 is green **with the 113-node trim held out**, named in
  `runbook-patches/provisional-trim.txt`.
- `check_proof_integrity.py` reading `0 problems over 0 blocked files` means *nothing left to
  check*, not *checked and clean*. It is in the battery as a tripwire.
- The v6 envelope digest is unkeyed. It proves coherence, not authenticity.
- The corpus exercises `ElaborationDiagnosticError` zero times. The separate-classification rule
  still binds; this corpus does not test it.
