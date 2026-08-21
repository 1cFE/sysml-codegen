---
date: 2026-08-20T20:19:45-07:00
researcher: Claude
topic: "Line-count anatomy of the repo and PR #13; is the codebase salvageable?"
tags: [research, repo-health, process-cost, dead-code, tests, project-artifacts]
status: complete
last_updated: 2026-08-20
---

# Research: Where the lines actually are, and whether this is salvageable

**Date**: 2026-08-20T20:19:45-07:00
**Researcher**: Claude
**Research Type**: Codebase / repo health

## Research Question

`stop-reinventing-the-parser` shipped as +37,131 / −4,471 (PR #13), after ELABORATE-FIRST
shipped as +384,503 / −107,730. The point of both was simplification. Why is the line count
not going down? Break the lines down for the PR and for the repo — `.project`, `tests/`, and
production code broken out by function. How much is redundant or dead? Is this salvageable?

## Summary

- **Production code is not growing.** `src/` went 23,537 lines (2026-07-20) → 22,139 (main
  today) → 23,195 (PR head). ELABORATE-FIRST **removed 1,544 net lines** of `src/`.
  PR #13 adds **1,056 net lines** across 137 commits. The scary headline numbers are
  process artifacts, not code.
- **`.project` is 78% of the repository** — 675,740 lines across 1,781 files, 30.5× the size
  of `src/`. Of that, **109,720 lines are byte-exact duplicates** of another committed file.
  One lint log, `ruff_all.log`, is committed **ten times for 120,736 lines** — 18% of all of
  `.project`, and 5× the size of the entire product.
- **`tests/` is bloated in committed data, not in test code.** ~73,400 of its 148,391 lines
  are removable, but only ~2,600 of the 48,370 lines of Python. Cross-tier duplication — the
  thing you'd most expect — is ~390 lines. There are 6 duplicated test names across 1,700
  test functions.
- **The product code is well-factored, and the slop hypothesis fails on measurement.**
  Copy-paste duplication in `src/` is 2.0%. Median function is 15 lines. Reference
  resolution, entry-point classification, and occurrence walking each have exactly one live
  implementation. What *is* there is ~2,370 lines (15%) of **dead** code — the cutover's
  unswept residue, not parallel implementations.
- **The real cost is a second product.** ~11,400 lines outside `src/` exist to verify the
  process rather than the model: a top-level `verification/` package (3,858 lines, added
  whole by PR #13), process scripts (2,657), and ~4,900 lines of tests testing those. That is
  half the size of the product, maintained inside the product's repo.

**Verdict: salvageable, and the product is in better shape than it looks.** The problem is
not the code. It is that the workflow commits its own scrollback into the repository the code
lives in.

## Detailed Findings

### 1. PR #13 (`stop-reinventing-the-parser`), bucketed

Base `7b29d8b`, head `origin/stop-parser-integration`. 269 files, +37,131 / −4,471.

| bucket | added | deleted | net | files |
|---|---:|---:|---:|---:|
| `.project/` | 20,119 | 49 | **+20,070** | 70 |
| `tests/` | 9,737 | 1,861 | +7,876 | 138 |
| `verification/` (new top-level) | 4,004 | 0 | +4,004 | 12 |
| `src/` | **3,058** | **2,002** | **+1,056** | 35 |
| `docs/` | 160 | 538 | −378 | 9 |
| `scripts/`, lockfiles | 53 | 21 | +32 | 5 |

The `.project` half is **19,249 lines of markdown across 64 files** (plus 795 lines of probe
`.py` and one 75-line JSON). The largest entries:

- `.project/completed/20260819_stop-reinventing-the-parser/plan.md` — 2,883 lines
- `…/plan.failed-candidate.md` — **2,356 lines** (a plan that was abandoned, committed in full)
- `…/design.md` — 1,983; `…/product-lens.md` — 1,676; `…/design-review.md` — 1,039;
  `…/audit.md` — 930
- `…/run-records/phase{1,2,3,4}-audit.md` — 561 + 776 + 851 + 368 = 2,556

**Ratio for this PR: 19,249 lines of process prose per 1,056 net lines of production code —
18:1.**

Within `src/`, the largest single entry is `elaboration/elaborate.py` at **+698 / −697** —
pure rewrite churn. The one real deletion is
`extraction/computed_attribute_extractor.py` (−413, removed entirely).

### 2. ELABORATE-FIRST (PR #10, `385e163`) — the number that alarmed you

1,570 files, +384,503 / −107,730.

| bucket | added | deleted | net |
|---|---:|---:|---:|
| `.project/` | 276,333 | 1,578 | **+274,755** |
| `tests/` | 90,476 | 91,192 | −716 |
| `src/` | 11,521 | 13,065 | **−1,544** |
| `docs/` | 2,596 | 1,295 | +1,301 |
| `scripts/` | 3,487 | 578 | +2,909 |

**ELABORATE-FIRST did exactly what it was supposed to do.** It deleted 1,544 net lines of
production code and was net-neutral on tests. 72% of its +385k was `.project` markdown, and
the `.project` half deleted almost nothing (1,578 lines) because process artifacts are only
ever appended.

### 3. Repository composition over time

Line counts at monthly checkpoints on `main`:

| date | commit | `src/` | `tests/` | `.project/` | `scripts/` | `docs/` |
|---|---|---:|---:|---:|---:|---:|
| 2025-12-31 | `36bd2c2` | 8,640 | 521 | 0 | 0 | 0 |
| 2026-01-23 | `b2559a3` | 9,129 | 723 | 1,882 | 0 | 0 |
| 2026-02-22 | `d6c725f` | 12,995 | 79,050 | 101,375 | 14,752 | 7,237 |
| 2026-07-20 | `936315c` | 23,537 | 138,374 | 243,670 | 15,539 | 9,205 |
| 2026-08-16 | `7b29d8b` | **22,139** | 140,514 | **656,567** | 18,818 | 10,507 |

Read the last two rows together. Between 2026-07-20 and 2026-08-16, `src/` **shrank by 1,398
lines** and `tests/` grew 2,140 — while `.project` grew **412,897 lines**. In August alone,
`src/` churned 11,700 lines (add+delete) against 450,169 lines added to `.project`: a **38:1
month**.

Since 2026-02-22, `src/` has taken 26,105 additions and 16,961 deletions across 179 commits
for a net of +9,144. The code is being *worked*, not accreted.

### 4. `src/` — 22,520 lines, of which 14,947 are code

| measure | value |
|---|---|
| total lines | 22,520 across 75 files |
| blank | 2,953 (13.1%) |
| comments | 686 (3.0%) |
| docstrings | 3,934 (17.5%) |
| **code** | **14,947 (66.4%)** |
| functions / classes | 670 / 156 |
| function length | median **15**, mean 24.3, p90 57, max 184 |
| functions > 100 lines | 20 |
| copy-paste duplication (8-line windows) | **309 lines, 2.0%** |

By subpackage: `elaboration` 7,187 · `extraction` 4,452 · `generation` 3,903 · `snapshot`
1,869 · `cli` 1,414 · `contracts` 1,116 · `orchestration` 869 · `resolution` 856 · `core` 679
· `analysis` 98.

By function role (name-pattern classification over 16,290 function lines):

| lines | % | role |
|---:|---:|---|
| 3,616 | 22.2% | resolve / elaborate / extract / project |
| 2,239 | 13.7% | generation / emit |
| 1,900 | 11.7% | validation / contract / preflight |
| 1,273 | 7.8% | render / naming / identifiers |
| 1,030 | 6.3% | serialize / snapshot |
| 959 | 5.9% | diagnostics / refusal |
| 5,273 | 32.4% | uncategorized (small accessors, helpers, dataclass bodies) |

Defensive machinery — validation, contracts, diagnostics, refusal — is **2,859 lines, 17.6%**.
For a compiler front-end whose stated contract is to refuse models it cannot elaborate
cleanly, that is proportionate, and each layer's docstring names what it uniquely catches.

**The largest file is not slop.** `elaboration/elaborate.py` is 2,753 lines, but it is one
class (`_ExactElaborator`) decomposed into ~85 methods at a median of 15 lines. It is a
SysML v2 elaborator. 14,947 code lines for a SysML v2 elaborator plus a full code generator
is small, not bloated.

### 5. Dead code in `src/` — ~2,370 lines (15%), all residue, no duplication

Two scans disagreed in an instructive way.

- A **symbol-level** scan (defined in `src/`, referenced nowhere else in `src/`) found only
  **8 symbols / 98 lines** referenced nowhere at all, plus 12 symbols / 109 lines kept alive
  only by tests.
- A **lane-level** review found ~2,370 lines, because whole modules are unreachable from the
  CLI while still being imported by test files. The symbol scan cannot see this; the modules
  look "used."

The lane-level findings, in priority order:

1. **The legacy extraction lane is unreachable from the CLI — 941 code lines.**
   `extraction/hierarchy_resolver.py` (641 lines) and `extraction/usage_extractor.py` (989).
   Verified: the only `import` of either anywhere in `src/` is `hierarchy_resolver.py:56`
   importing `usage_extractor` — they import each other and nothing else imports them. These
   are the old string-keyed twins of `elaboration/occurrence.py` (supertype closure,
   most-specific pick, part-tree enumeration). *Removal is design work* — their tie-break
   semantics differ from the survivor's (`most_specific` warns where
   `_most_specific_definition` raises).

2. **The hand-written snapshot codec — ~550 net lines.**
   `snapshot/instance_graph.py` (1,192 lines, 1,080 code, 19 doc) mirrors the 14 dataclasses
   in `elaboration/graph.py` by hand. ~783 lines are pure field-copying; ~289 are real logic
   (digest ordering, fingerprint round-trip, duplicate-identity rejection). Collapsing it
   needs dataclass→Pydantic, discriminators on three untagged unions, and an
   `instance-graph/v4` bump with 22 fixture re-captures. **Its own decision.**

3. **One of the five advertised preflights is dead by construction — 85 lines. Verified.**
   `ComputationGraph.fallback_entry_points` is constructed as `set()` at
   `elaboration/project.py:287` and `:322` — the only two construction sites in `src/`. Both
   loops in `resolution/uncovered_params.py` (`:67`, `:107`) iterate it, so
   `collect_uncovered_params` can never return anything, and the `PARAMS_KEY_UNCOVERED: V11`
   branch at `cli/__init__.py:298` can never fire. A test at
   `test_warning_reconciliation_exact_route.py:167` *pins* the set as permanently empty.
   **`CLAUDE.md:65` lists "params coverage (V11)" as one of the five live preflights.** That
   line is wrong and should be corrected regardless of what else happens.

4. **Deriver-era generators with zero callers anywhere — 123 lines.**
   `generation/entry_point.py:21` and `:154` both take `DerivedParameterGroup`, a type that
   does not exist in the repo. Mechanical delete.

5. **`ConcreteConstraint` family — 105 lines.** `resolution/models.py:284-460`, never
   constructed in `src/`. What ships is `ConstraintCatalogEntry`, whose own docstring calls
   itself "a thin, catalog-shaped projection of `ConcreteConstraint`." 37 test references
   hold it up.

6. **Dead extractor and model classes — 126 lines.** `extract_part_definitions` (no callers
   at all), `ComputedAttributeData`, `AttributeRef`, `ScopedAggregationData`,
   `PartDefinitionData`, `ConstraintInfo`, `BindingResolution*`, `ChannelAlias`,
   `ValueSiteKind`. Mechanical.

7. **A third predicate compiler, dead — 54 lines. Verified.**
   `generation/predicate_compiler.py` exports two compilers; only `compile_predicate_body`
   (`:303`) is called in production, from `generation/modules.py:172`. **`compile_predicate`
   (`:342`) has zero production callers** — it is the superseded polarity-applying variant,
   and it says so itself by building its own `legacy_policy` inline at `:353` instead of using
   the module-level `PREDICATE_SCOPE_POLICY`. `load_predicate` (`:419`) is likewise test-only.
   26 test references across `test_predicate_compiler.py` and `test_constraint_name_safety.py`
   hold it up — a suite asserting on the emitted source of a function the product never
   invokes.

8. **Error-subclass constructor boilerplate — ~50 lines.** Eight subclasses of
   `ElaborationInvariantError` (`extraction/errors.py:11,27`, `elaboration/occurrence.py:45,
   63,77,95`, `elaboration/identity.py:40`, `snapshot/instance_graph.py:74`), most carrying a
   13-line `__init__` whose only job is binding one fixed `ElaborationCode` before delegating.
   A class-level `code = ...` on the base collapses each to about two lines. Mechanical.

9. **Smaller mechanical items — ~390 lines.** "Which file declares this module" derived four
   times (`cli:158`, `modules.py:40`, `stencils.py:34`, `registry.py:295`); six canonical-JSON
   encoders of which three are byte-identical; two ExpressionIR→Python numeric compilers
   (`calc_compat_renderer.py:66-129`, `predicate_compiler.py:151-202`) differing mainly in
   spacing; near-duplicate pairs like `_collect_unbound_{constraint,calculation}_formals`
   (`elaborate.py:1958` / `:1993`, identical control flow); a test-only identifier façade in
   `core/qualified_names.py` whose docstrings cite deleted modules.

**The pattern worth naming: tests are what keep this code alive.** Items 1, 5, 7 and 8 above
are all production-unreachable code pinned by conformance or unit suites that outlived their
subject. This is why a symbol-level dead-code scan reports 98 lines and a lane-level review
reports 2,370 — the tooling cannot distinguish "used" from "referenced by a test of a deleted
feature." Any deletion pass has to retire the test family and the code together, in one
commit, or the tests will look like a reason not to delete.

Two candidates were investigated and **dismissed**: `source_manifest.py:540` / `:556`
(`_admitted_membership` / `_scanned_membership`) project two genuinely different input shapes
onto one comparable tuple — that normalization is the point. And
`expression_compiler.py:160` / `expression_evidence.py:119` share the six-line "dict lookup,
raise a domain error on `KeyError`" idiom across different layers with different maps and
error types; a shared helper would cost more indirection than it saves.

**What is NOT redundant, checked specifically:** reference resolution runs one path
(`elaborate.py:2297` → `occurrence.py:559` → `elaborate.py:2500`), identity-keyed, with no
string matching. `EntryPointType` is decided only at `project.py:564-588` and `:606` — CLAUDE.md's
claim is accurate. The two topological sorts (`project.py:1135`, `expression_compiler.py:125`)
are different domains. The `contracts/seal.py` ↔ `contracts/verify.py` duplication is
deliberate and documented: `verify.py` is stdlib-only, ships inside every generated package,
and its sha256 is pinned at `contracts/versions.py:54`. Leave it.

### 6. Dead weight outside `src/` that is unambiguously deletable

- **`scripts/archive/` — 8,274 lines, 19 files. Referenced by nothing**, and most of them
  `import` modules the cutover deleted (`pipeline_builder`, `graph_builder`,
  `output_registry`, `constraint_lowering`). They cannot execute. Straight delete.
- **`docs/architecture/reference/` — 3,633 of 8,609 lines (42%) describe deleted code.**
  Documents 03, 04, 05, 07, 10, 11, 12, 13, 17, 24, 25, 28, each carrying a "retiring" banner
  and a CLAUDE.md warning not to read them as descriptions of the product. The largest are
  `10-output-registry.md` (478), `11-analysis-backtracker.md` (412), `07-graph-assembly.md`
  (392), `25-hierarchy-resolver.md` (377).

### 7. `tests/` — 148,391 lines, of which 30,824 are test code

| area | lines | files |
|---|---:|---:|
| `tests/unit/` | 63,118 | 61 |
| `tests/fixtures/` | 49,781 | 388 |
| `tests/conformance/` | 28,124 | 114 |
| `tests/execution/` | 2,749 | 12 |
| `tests/expectations/` | 2,102 | 58 |
| `tests/helpers/` | 1,009 | 12 |
| `tests/integration/` | 981 | 6 |
| `tests/runtime/` | 371 | 3 |

Python only: 48,370 lines, 63.7% code (30,824), 2,492 test functions, median function 10
lines, copy-paste duplication 1,194 lines (3.9%).

**Removable: ~73,400 lines (49%), of which only ~2,600 is Python.**

1. **`tests/unit/data/item8-snapshot-inventory-{pre,final}.json` — ~47,000 lines.**
   48,170 lines / 7.2 MB, of which **98.0% is the `unit_map` arrays**. The only reader is
   `tests/conformance/test_v6_snapshot_inventory.py`, and its entire assertion on that 7 MB is
   `assert isinstance(committed["unit_map"], list)` (`:63`, `:67`). The real comparison was
   precomputed at capture time into a boolean stored in the same file
   (`scripts/assess_v6_snapshot_churn.py:300`), read at `:141`, `:151`, `:161`. Replacing each
   array with its digest preserves every live assertion. It is also a frozen receipt from an
   item closed on 2026-08-13.

2. **`tests/fixtures/baseline_outputs/` + its only reader — 13,923 lines.** Nothing
   regenerates anything to compare against it. `tests/conformance/test_baselines.py`'s four
   assertions are: the committed JSON parses (`:47`), it is internally self-consistent
   (`:56`), the committed `registry_init.py` is valid Python (`:65`), and `"modules" in data`
   (`:76`). All four pass on hand-written stubs, despite a docstring claiming it "validates
   that pipeline output is deterministic and matches captured baselines." The suite already
   admits this at `tests/conformance/test_zero_entry_package_golden.py:11-13`. This is how
   `solar_battery`'s aggregation `module_type` can disagree with its `calc_def_qualified_name`
   without failing anything.

3. **Two confirmed-dead golden sets — 4,098 lines.**
   `tests/fixtures/golden/calc_def_compilation_golden.json` (3,254) has zero readers; its
   consumer was deleted. `tests/fixtures/baseline_yaml/` (844) has zero readers; its capture
   script retired with the v5 family.

4. **D-5 fixture forks — ~5,770 lines.** `catf_mfe_d5` is a 5,718-line copy of
   `catf_mfe_model` **differing by four lines in two files** (one rename,
   `pumping_speed_total` → `pumping_speed_total_in`); 26 of its 28 `.sysml` files are
   byte-identical. `chain_spike_d5` is a 53-line byte-identical copy.
   `scripts/make_d5_variant.py` already generates them and has a `--check` mode proving
   byte-for-byte reversal. Repo-wide, 9,138 of 28,126 fixture `.sysml` lines (32%) are
   byte-identical duplicates. **Caveat:** the committed `instance_graph_snapshot.json` beside
   each variant is what keeps repointed tests license-free and cannot be regenerated without a
   license. Only the `.sysml` half is safely derivable. Also note that 838 lines of
   `tests/conformance/test_d5_variants.py` exist largely to police these copies — ~20 of its
   31 tests (`:425-810`) test the generator script's CLI argument handling, not the product.

5. **Retired-migration process tests — ~2,200 lines.** 13 test files (3,829 lines, 174 test
   functions) never import `sysml_codegen` and assert on repo meta-artifacts. The clear
   retire-with-their-item candidates: `test_evidence_artifact_topology.py` (1,046 lines, of
   the `verification/` harness), `test_check_ledger_4a.py` (876, of a one-off recovery ledger
   checker whose migration already ran), `test_retirement_worklist.py` (150, of the retirement
   script for that same completed retirement), `test_check_proof_integrity.py` (117 — its own
   docstring admits the live tree can no longer exercise it),
   `test_elaboration_corpus_ledger.py` (35, asserting on a markdown table in
   `.project/completed/`). Keep `test_probe_fixture_lock.py`, `test_reference_doc_distinctness.py`,
   `test_gated_manifest_identity.py` — those have real hygiene value.

6. **Cross-tier duplication — ~390 lines (0.9%).** Almost absent. 6 duplicated test names
   across 1,700 test functions. Tiers separate cleanly: integration calls `run_codegen` under
   a live license with zero mocks, unit is mock-driven, execution runs generated packages
   under real simkit. The one leak is the expression compiler: `_ir_ref`/`_ir_literal`/
   `_ir_binary`/`_ir_unary`/`_ir_unsupported` are verbatim at
   `tests/unit/test_expression_compiler.py:37-92` and
   `tests/conformance/test_expression_compiler.py:37-96`, with five identical rollup tests.
   Separately, `tests/conformance/test_data_models.py:30-155` is 24 tests of the form
   `import X; assert X is not None`, subsumed by the field checks below them, and contains a
   byte-for-byte duplicate at `:79` and `:911`.

**What is NOT bloat in `tests/`, checked:** the 154-directory fixture corpus is cheap — 139
of them total 6,855 lines (14%), and only 2 are unreferenced. Docstrings are 12% and carry
provenance. `tests/helpers/` earns its place (`raw_elaboration.py` has 30 consumers). Skips
are 16 total with **zero xfail** — there is no dead-test problem.

**Coverage caveat:** 544 of 1,700 test functions (32%) are license-gated, and
`pyproject.toml:46` sets `addopts = -m "not execution"`, excluding 12 files / 2,749 lines. A
default run without `SYSIDE_LICENSE_KEY` exercises about two-thirds of the suite.

### 8. `.project/` — 675,740 lines, 78% of the repository

| lines | files | % | category |
|---:|---:|---:|---|
| 156,201 | 303 | 23.1% | **raw evidence logs** (`.log`, `.txt`, `.console`) |
| 156,059 | 543 | 23.1% | **durable prose** (spec, design, concept, research, ADR) |
| 137,712 | 46 | 20.4% | **JSON dumps & snapshot inventories** |
| 88,748 | 163 | 13.1% | **plans** (`plan.md` ×155 = 82,991 lines alone) |
| 78,689 | 332 | 11.6% | audits / reviews / verdicts / findings |
| 19,548 | 138 | 2.9% | scripts & probe harnesses |
| 11,371 | 41 | 1.7% | evidence write-ups (prose) |
| 10,571 | 106 | 1.6% | fixtures / misc data |
| 9,566 | 44 | 1.4% | handoff / close / status / brief |
| 7,272 | 63 | 1.1% | patches (`runbook-patches/`) |

Durable decision content is **~23%**, generously counted. Files under `evidence/`,
`verification/`, and `probes/` account for **303,663 lines — 45% of `.project`**.

**Literal duplication: 109,720 lines are byte-exact copies** of another committed file
(27 duplicate groups over 2KB). The worst case is `ruff_all.log`, committed **10 times for
120,736 lines** under `completed/20260814_cutover-recovery/evidence/phase5-runs/`. The
`run1/run2/run3` triplication is genuine triplication: 19 of 24 files are byte-identical
across replicates; only the 5 pytest logs with timings differ. A determinism claim needs a
hash manifest, not three full copies.

**Prose redundancy is semantic, not literal.** In `20260819_stop-reinventing-the-parser`, only
1% of long lines appear in more than one file. Nothing is copy-pasted — but the same item is
independently re-narrated across spec → design → design-review → plan → audit → 5 phase-audits
→ 11 briefs, 47 markdown files, 17,219 lines.

**Process cost per unit of work — the key table:**

| item | `src/` churn (add+del) | `.project` lines | ratio |
|---|---:|---:|---:|
| `20260816_qualified-reference-occurrence-anchoring` | **74** | 128,193 | **1,732 : 1** |
| `20260816_self-binding-replacement` | **17** | 7,207 | **424 : 1** |
| `20260819_stop-reinventing-the-parser` | 1,042 | 17,219 | 17 : 1 |
| `20260814_cutover-recovery` | 31,240 | 175,878 | 5.6 : 1 |
| `20260814_elaborator-cutover` | 15,735 | 15,267 | 1.0 : 1 |

**The cost is roughly constant per *item*, not per unit of work.** Average completed item =
4,433 lines across 124 items. A 74-line source change bought a 128,193-line archive.

**Almost nothing in `.project` is load-bearing.** Exactly one path is read by code:
`.project/ledger/ledger-4a.json` (7,118 lines), read by `scripts/_ledger_edit.py:17`,
`scripts/check_ledger_4a.py`, and `scripts/retirement_worklist.py`.
`.project/product/INDEX.md` is referenced by CLAUDE.md but by no code or test. There are 139
prose citations of `.project` paths from `src/` and `tests/`, and **25 of the 48 distinct
cited paths no longer exist** — including `.project/active/cutover-recovery/plan.md`, cited
from 12 places. The archive is already failing its own citation contract.

**`.project/active/` is a second archive.** 48 directories, 486 files. **40 of them (74,233
lines, 292 files) were last touched before 2026-08-01.** Thirteen date to 2026-07-20 — the
constraint-exec wave that is already sitting, closed, in `.project/completed/20260720_*`.
Per `CURRENT_WORK.md` the only live item is `elaborator-downstream`. Items are being closed
in `CURRENT_WORK.md` but never archived, so the tree carries two copies of the process.

### 9. The cost nobody priced: a second product

Outside `src/`, roughly **11,400 lines exist to verify the process rather than the model**:

- `verification/` — 3,858 Python lines in 5 files, added whole by PR #13:
  `run_independent_green.py` (1,595), `capture_baseline.py` (766), `audit_evidence.py` (633),
  `build_artifacts.py` (619), `artifact_sources.py` (245). Purpose: build deterministic source
  archives and wheels from five explicit Git inputs and stage six evidence-only files.
- ~2,657 lines of process scripts in `scripts/`.
- ~4,900 lines of tests testing those, led by
  `tests/conformance/test_evidence_artifact_topology.py` (1,046) and
  `tests/unit/test_check_ledger_4a.py` (876).

Against a product of 22,520 lines. It is not duplicated — one checker, one test file, testing
its failure paths — but it is **half the size of the thing it verifies**, and it grew by 4,004
lines in a single PR.

## Incidental bugs found

1. **`contracts/serialize.py:28` omits `allow_nan=False`.** Verified: the other three
   canonical encoders set it (`snapshot/instance_graph.py:87`, `snapshot/envelope.py:180`,
   `extraction/source_manifest.py:342`). `serialize.py` is the `ModelContract` fingerprint
   payload and `ContractParameter.default_value` is `float | None`, so a NaN default would
   silently hash non-standard JSON.
2. **`CLAUDE.md:65` advertises a preflight that cannot fire** (params coverage / V11) — see
   §5 item 3. Verified.
3. **`_preflight_constraint_names` runs 10× on the same graph** (`cli/__init__.py:504…833`,
   once at the top of every `_generate_*`), with `validate_constraint_graph_or_raise` from
   three more sites. `ComputationGraph` is not frozen so it is defensible; cost is CPU, not
   lines.
4. **`tests/conformance/test_baselines.py` does not do what its docstring says** — see §7
   item 2.

## Code References

- `src/sysml_codegen/elaboration/project.py:287,322` — the only two `fallback_entry_points`
  construction sites, both `set()`
- `src/sysml_codegen/resolution/uncovered_params.py:67,107` — loops over that always-empty set
- `src/sysml_codegen/cli/__init__.py:298` — the `V11` branch that can never fire
- `src/sysml_codegen/contracts/serialize.py:28` — missing `allow_nan=False`
- `src/sysml_codegen/extraction/hierarchy_resolver.py:56` — the only `src/` import of the
  legacy extraction lane, from inside the lane itself
- `src/sysml_codegen/elaboration/elaborate.py:521` — `_ExactElaborator`, ~85 methods, the
  well-factored core
- `tests/conformance/test_v6_snapshot_inventory.py:63,67` — `isinstance(..., list)` over 7 MB
- `tests/conformance/test_zero_entry_package_golden.py:11-13` — the suite naming its own dead
  fixtures
- `tests/conformance/test_baselines.py:47,56,65,76` — the four assertions that pass on stubs
- `.project/ledger/ledger-4a.json` — the only `.project` file any tool reads

## Feasibility Assessment

**Salvageable — and the framing needs correcting before any work starts.** "The codebase is
filled with slop" is not what the measurements show. Three independent structural metrics say
`src/` is in good shape: 2.0% copy-paste, median function 15 lines, one live implementation
per concept. The `.project` explosion is a *workflow* artifact that happens to be committed to
the same git repository as the product, and it has been misreading as code volume ever since.

Risks:
- The dead-code deletions are gated on retiring test families that reference them (37 test
  refs on `ConcreteConstraint` alone; named REQ conformance families on
  `core/qualified_names.py`). This is a deletion PR with a test-retirement plan, not a
  refactor.
- The `.project` cleanup is safe but touches 25 already-broken citations that should be fixed
  in the same pass.
- The snapshot-codec consolidation costs a schema bump and 22 fixture re-captures, which
  requires a license. Keep it separate.
- Deleting fixture `.sysml` copies must not delete the committed
  `instance_graph_snapshot.json` beside them — those are what keep tests license-free.

## Recommendations

Four independent tracks, ordered by payoff per unit of risk.

**Track 1 — stop committing scrollback (highest payoff, near-zero risk, ~300k lines).**
`.gitignore` the log family repo-wide (`.project/**/*.log`, `*.console`, `*.err`,
`*full-suite.txt`) and `git rm` the existing ones: −156,201. Delete
`completed/20260814_cutover-recovery/runbook-patches/`: −7,272 (diffs of commits already in
git). Replace the six snapshot-inventory JSONs under
`20260816_qualified-reference-occurrence-anchoring/verification/` with digests: −115,315.
Collapse `run1/run2/run3` to one run plus a three-hash manifest: −~28,000. If a run must be
pinned, commit `sha256 + counts + failing lines only`, never the transcript.

**Track 2 — fix the archive-on-close hygiene bug (~74k lines, and it stops recurring).**
40 of 48 `.project/active/` directories are closed items that were never archived. Archive
them, enforce archive-on-close in the workflow, and prune the 25 broken `.project` citations
in `tests/fixtures/**/PROVENANCE.md`. Consider moving `.project/completed/` older than the
current epic out of the repo entirely (separate archive repo, or just leave it in git history
and `git rm` from HEAD), keeping each item's `spec.md`, `design.md`, and audit verdict. That
is the difference between 549,651 lines and roughly 60–70k of actual decision record. Keep
`.project/research/` intact — at 20,408 lines it is the highest value-per-line content in the
tree.

**Track 3 — sweep the cutover residue from `src/` (~1,500–2,370 lines).**
One deletion PR, gated on retiring the test families that hold the dead lanes up:
the V11 preflight (85 lines) + the `CLAUDE.md:65` correction, deriver-era generators (123),
`ConcreteConstraint` (105), dead extractor/model classes (126), the dead
`compile_predicate` / `load_predicate` pair (54), error-subclass boilerplate (~50), the small
mechanical duplicates (~390), and the legacy extraction lane (941, needs a semantics ruling on
the tie-break difference). Also delete `scripts/archive/` (8,274 lines, cannot execute) and the 12
retired reference docs (3,633 lines). Hold the snapshot codec (~550) as its own decision.
Fix the `allow_nan` bug in the same pass.

**Track 4 — decide what `verification/` is for.** 3,858 lines of release-evidence tooling plus
~4,900 lines of tests for it entered the repo to ship one PR. Either it is a durable part of
the product's release process — in which case it belongs in its own package with its own
lifecycle — or it was scaffolding for `stop-reinventing-the-parser` and should retire with the
item. Right now it is a second product with no owner, and it is the single largest recurring
cost in the "why is this repo so big" question after `.project`.

**What not to do:** do not refactor `src/`. Do not consolidate the "duplicate" preflight and
contract layers — they were checked and each earns its keep. Do not collapse the test tiers;
cross-tier duplication is 0.9%.

Expected outcome of tracks 1–3: repository drops from ~880k lines to roughly **150–180k**,
`src/` drops to ~13,500 code lines, and every spec, design, verdict, ADR, and research
document survives. What disappears is console scrollback, machine-generated JSON, and code no
production path can reach.

## Open Questions

1. **Is `verification/` durable or scaffolding?** Owner call. It determines whether ~8,700
   lines stay.
2. **Does the legacy extraction lane's tie-break semantics difference matter?**
   `most_specific` warns where `_most_specific_definition` raises. Someone must rule before
   the 941 lines go.
3. **Should `.project/completed/` leave the repo?** Git history preserves it either way; the
   question is whether agents need it readable at HEAD.
4. **What is the intended contract of `tests/fixtures/baseline_outputs/`?** It should either
   regain a regenerating comparison test or be deleted. Today it is 13,923 lines asserting
   that a static file parses.
5. **Why is the process cost constant per item rather than proportional to it?** A 74-line
   change producing 128k lines of archive is the strongest signal in this document, and it is
   a workflow question, not a codebase one.
