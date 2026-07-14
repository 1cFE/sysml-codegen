# Audit: `module_kind` and the Generation-Seam Refactor (Item 6)

**Verdict:** Certify-with-notes
**Audited:** 2026-07-12
**Branch:** constraint-exec-epic
**Commit:** 58ce68f (implementation tip; audit run at HEAD 7f20d04)
**Auditor:** fresh audit session (did not implement)

---

## Summary

The refactor is done correctly. The two Boolean flags are gone from the entire repo, `module_kind`
is a single required enum set at all three construction sites and dispatched at all six generation
sites, and the fail-loud contract is real: every seam entry point raises for `CONSTRAINT` /
`REPORT_AGGREGATOR`, including the fails-open registry seam whose guard-pass is present. Every static
gate I could execute passes (repo-wide zero-hit grep, baseline-diff shape, `output_schema_type`
inertness), and every code-trace check against the design's per-site notes matches — including the two
tricky sites the reviews contested (the `_raw_source_name` two-arm and the registry guard-pass).

The "with-notes" is procedural, not a code defect. **This sandbox blocks all Python execution**
(`uv run`, direct `.venv/bin/pytest|mypy|ruff`, and `python3` all require approval that is
unavailable in this non-interactive run). So the four *dynamic* gates — full suite, ruff, mypy, and
the guard-mutation RED/GREEN — I could not run myself. Their recorded outcomes are internally
consistent with everything I traced statically, but per the execution-fallback protocol I did not
downgrade to code-trace-only silently: the exact commands and the one guard mutation are listed under
**Requested live probes** for the orchestrator (full permissions) to run and append. One genuine
spec-vs-implementation gap: the spec criterion "mypy clean" is not literally met (78 pre-existing
errors); the item reframes it as "no new errors," consistent with standing project-wide debt.

## Findings

| # | Severity | Area | Finding |
|---|----------|------|---------|
| 1 | Note | Spec conformance | Spec success criterion "mypy clean" (spec:48) is **not literally met** — Phase 6 records 78 pre-existing errors and reframes the bar as "no new errors from this refactor." Consistent with CURRENT_WORK's standing note that the project-wide mypy baseline is dirty (~97–98). Owner-visible reframe, recorded in the plan; not a code defect, but the literal criterion is unmet. Cannot re-run mypy here → probe P3. |
| 2 | Note (process) | All dynamic gates | Full suite (2142 passed / 4 skipped), ruff, mypy, and the guard-mutation RED/GREEN could **not be executed** in this sandbox. Recorded outcomes are plausible and consistent with static trace, but unverified-by-execution here. Probes P1–P4. |
| — | — | — | No code-integrity findings. No placeholder code, no silent scope cuts, no TODOs, no unproven claim found false. |

## What I verified by execution (read-only tools available)

- **INV-4 zero-hit grep (ran it):** `grep -rn 'is_computed_attribute\|is_aggregation' src/ tests/`
  → **zero hits.** The flags are gone repo-wide. Spec criterion 4 met.
- **`output_schema_type` inert (ran it):** `grep -rn 'output_schema_type' src/` → **only** the field
  declaration (`resolution/models.py:194`). No `src/` code reads it. Design Risk mitigation holds.
- **Baseline-diff shape (git show f867aed):** the change touches exactly the **9** flag-carrying
  `computation_graph.json` files; `sample_model` absent (correct — zero modules). Filtering every
  changed baseline line that is *not* one of the four expected keys returns **empty** — no other key
  moved. Per module: `-is_computed_attribute`, `-is_aggregation`, `+module_kind`,
  `+output_schema_type: null`, at the ordered position between `compiled_expression` and
  `auto_impl_context`. The added `module_kind` values tally 84 calculation / 20 aggregation / 15
  formula (119 modules) — all three kinds represented, none mis-mapped. Matches the design
  baseline-diff spec byte-for-byte.

## Spec conformance — success-criteria walk

1. **Fixture corpus regenerates byte-identically, flags gone** (spec:33) — **Partial (static side
   proven).** The committed **graph baselines** I verified myself: diff shape is exactly the
   two-out/two-in-plus-null swap, nothing else (above). The **generated-package** byte-identity is
   enforced by the conformance suite (regenerate-to-temp + compare), recorded green but not runnable
   here → probe **P1**. Left unmarked pending P1.
2. **Single `module_kind` enum, five members, flags gone everywhere** (spec:37) — **MET.**
   `ModuleKind(str, Enum)` with `calculation/formula/aggregation/constraint/report_aggregator`
   (`models.py:161-170`); `module_kind: ModuleKind` required, no default, at the flags' old position
   (`models.py:193`); `output_schema_type` after it (`:194`); grep confirms flags gone. Marked.
3. **Four seams dispatch on `module_kind`; constraint/report_aggregator fails loud** (spec:39) —
   **MET by trace; test execution → probe.** All six sites traced against the design (see below); the
   raise is wired at every seam entry; the 7 seam-entry tests exist and call entry points, not inner
   helpers. Test pass recorded; guard-mutation RED/GREEN → probe **P4**.
4. **Every flag consumer migrated src+tests; repo-wide grep zero** (spec:44) — **MET.** Grep run,
   zero hits. Marked.
5. **Committed `computation_graph.json` baselines carry `module_kind`, round-trip via
   `model_validate_json`** (spec:46) — **Partial.** The baselines carry `module_kind` (verified
   diff). The round-trip is `test_baselines.py`, recorded green → probe **P2**.
6. **mypy clean, Ruff clean, full suite green** (spec:48) — **See Finding 1 (mypy) + probes
   P1/P3.** ruff and suite recorded green; mypy not literally clean.

### Non-goals respected
No constraint/report-aggregator *emission* was built (only the refusal). `output_schema_type` is an
inert `None`-default carrier read by nothing (grep-confirmed). No snapshot-format-version bump —
`module_kind` is a graph field only. All non-goals honored.

## Design conformance — the six dispatch sites (traced against the per-site authority)

Every site matches the design's per-site notes, including the two the reviews flagged as
easy-to-break:

- **Seam 1a `_get_python_path` (`cli/__init__.py:156-163`)** — three-arm FORMULA/AGGREGATION/
  CALCULATION, bodies unchanged, `else: raise …(module,"python-path")`. ✓
- **Seam 1b `_raw_source_name` (`cli/__init__.py:179-183`)** — the **M1 two-arm**: FORMULA →
  `{qn}::{name}`; **AGGREGATION joins CALCULATION** in the `calc_def_qualified_name or name` arm;
  `raise …(module,"raw-source-name")`. Aggregation is *not* given its own arm and *not* routed to the
  raise — exactly as the design demands (else every aggregation module breaks). ✓
- **Seam 2 `generate_registry` (`registry.py:223-232`)** — the **M2 fails-open** seam. Guard-pass
  raises for CONSTRAINT/REPORT_AGGREGATOR **before** the partition; then partitions by
  `module_kind ==` equality. The guard is the only thing preventing a silent drop; it is present. ✓
- **Seam 3 `_get_module_sysml_qn` (`modules.py:43-50`)** — three-arm + `else: raise …(module,
  "module-wrapper")`. Float-wrapper body untouched (D5). ✓
- **Seam 4a `_get_module_sysml_qn` (`stencils.py:45-52`)** — three-arm + `else: raise …(module,
  "stencil")`. ✓
- **Seam 4b auto-impl counter `generate_backlog_report` (`stencils.py:216-226`)** — guard-`continue`:
  FORMULA→continue, AGGREGATION→elif continue, CONSTRAINT/REPORT_AGGREGATOR→raise "backlog-report",
  CALCULATION falls through. ✓
- **Reader pipeline label `_module_to_context` (`pipeline.py:130-140`)** — guard raise "pipeline-yaml"
  hoisted **above** the return (a ternary can't raise inline); labels rekeyed byte-identically
  (AGGREGATION→"source: aggregation …", FORMULA→"source: computed_attribute …", else
  `module_type`). ✓
- **Reader test-gen skip `generate_test_implementations` (`test_gen.py:50-53`)** — `in (FORMULA,
  AGGREGATION): continue` + raise "test-gen". ✓

**Construction (`graph_builder.py:1184/1587/1790`)** — FORMULA / AGGREGATION / CALCULATION set at the
three mutually-exclusive sites, one-to-one with the flag each set before. ✓

**Shared error helper (`generation/errors.py`)** — `unrenderable_module_kind_error(module, seam_name)`
returns `CodeGenerationError` with name + kind value + seam, per D4. Lazy import avoids the cycle. ✓

## The two deviations (brief item 4)

Both are sound; neither drops spec-required coverage.

- **`test_aggregation_takes_priority_over_computed_attr` deleted.** It tested the old seam's behavior
  when **both flags were True** — aggregation wins. Spec [HARD] (spec:65-70) explicitly declares that
  cell unreachable and safe to drop, *because no construction site sets both flags*. Under a
  single-value enum the state is **unconstructible**, so the priority question is moot. Correct
  deletion — no spec requirement covers the dropped behavior.
- **`test_is_aggregation_false` deleted; `test_is_computed_attribute_true` renamed to
  `test_module_kind_is_formula`.** The positive test was **kept**, now asserting `module.module_kind
  == ModuleKind.FORMULA` for every FORMULA module (`test_factory_formula.py`). "FORMULA is not
  aggregation" is structurally guaranteed by a single-value enum, so the negative test is redundant.
  Formula-kind coverage is preserved, not lost.
- **ModuleKind docstring reworded.** The Phase-1 docstring named the old flags verbatim, which would
  itself trip the INV-4 zero-hit grep. Reworded (`models.py:162-164`) to state the same fact without
  naming them. No behavior change; it is what keeps INV-4 green. Confirmed the docstring no longer
  contains the flag identifiers.

**"Both flags true is unconstructible" — verified structurally.** `module_kind: ModuleKind` is a
single enum value; the flags no longer exist (grep zero). No code path can express the ambiguous
cell. The claim recorded as proven is proven.

---

## Requested live probes (sandbox blocked execution — orchestrator to run and append)

Attempted execution first: `uv run …`, `.venv/bin/pytest|mypy|ruff …`, and `python3 -c …` all return
"This command requires approval," which is unavailable in this non-interactive run. Read-only
`git`/`grep`/`ls`/`sed` work — everything above marked "ran it" was executed. The four dynamic gates
below were not.

- **P1 — full suite / package byte-identity.** `uv run pytest tests/`
  → **Expect GREEN: 2142 passed, 4 skipped** (the conformance suite regenerate-compares the package;
  green = byte-identical). Closes success criteria 1 and 6 (suite).
- **P2 — baseline round-trip (INV-5).** `uv run pytest tests/conformance/test_baselines.py`
  → **Expect GREEN.** Confirms the regenerated `module_kind` baselines round-trip through
  `ComputationGraph.model_validate_json`. Closes criterion 5.
- **P3 — mypy / ruff.** `uv run mypy src/` → **Expect 78 errors, all pre-existing** (NOT clean; see
  Finding 1 — compare against the pre-Item-6 commit `a4319e8^` to confirm zero *new* errors).
  `uv run ruff check src/` → **Expect clean.** Closes criterion 6 (ruff) and quantifies the mypy note.
- **P4 — guard-mutation RED/GREEN (fail-loud contract, brief item 2).** Pick the fails-open registry
  seam:
  1. `uv run pytest tests/conformance/test_module_kind_faildloud.py -v` → **Expect 7 passed (GREEN).**
  2. Delete the guard-pass at `src/sysml_codegen/generation/registry.py:223-225` (the
     `for m in graph.modules: if m.module_kind in (…CONSTRAINT, …REPORT_AGGREGATOR): raise …` block).
  3. Re-run → **Expect `test_registry_seam_refuses_constraint` FAILS with "DID NOT RAISE"** (a
     CONSTRAINT module matches no partition list and is silently dropped — proving the test guards the
     fails-open path, per design INV-3 / M2).
  4. Revert the guard → re-run → **Expect 7 passed (GREEN)** again.
  (The plan's Phase-4 notes record this exact mutation was performed during implementation and behaved
  as expected; P4 re-confirms it independently.)

---

## Certification

**Checked and verified (by execution or code-trace):**
- INV-4 repo-wide zero-hit grep — ran, zero hits.
- Baseline-diff shape — `git show f867aed`, exactly the two-out/two-in-plus-null swap on 9 files,
  `sample_model` unchanged, no other key moved, all three kinds mapped correctly.
- `output_schema_type` inertness — ran, only the field declaration in `src/`.
- Enum definition, five members, values, and required-field placement (D1/D2).
- All three construction sites set `module_kind` one-to-one (B1).
- All six dispatch sites + the two readers against the design's per-site authority (incl. M1 two-arm,
  M2 registry guard-pass).
- Shared error helper (D3/D4).
- The 7 seam-entry tests exist and target entry points (not inner helpers), matching `"constraint"`.
- The two test deletions and the docstring reword — sound, no lost coverage.
- The "both flags true unconstructible" claim — structurally proven.

**Not checked (requires the live probes P1–P4):**
- Full suite actually green (recorded 2142/4; enforces package byte-identity — criterion 1).
- Baseline round-trip via `model_validate_json` passing (criterion 5).
- mypy error set = pre-existing only, and ruff clean by execution (criterion 6; mypy is Finding 1).
- Guard-mutation RED/GREEN by execution (the fail-loud contract confirmed dynamically — traced and
  test-covered, but not run here).

**Marked:** spec success criteria 2 and 4 (fully static-verified). Criteria 1, 3, 5, 6 left unmarked
pending P1–P4 — the code is traced-correct and the outcomes are recorded green, but this session could
not execute them, and byte-identity/suite-green is precisely the kind of claim that must be run, not
inferred. Once the orchestrator runs P1–P4 and they land as expected, this becomes a clean Certify and
the remaining criteria can be marked.

---

## Addendum: P1–P4 executed by orchestrator (2026-07-12)

- **P1 (full suite + package byte-identity):** `uv run pytest tests/` → **2142 passed, 4 skipped**. GREEN as expected. Criteria 1 and 6 (suite) closed.
- **P2 (baseline round-trip):** `tests/conformance/test_baselines.py` → **17 passed**. Criterion 5 closed.
- **P3 (mypy/ruff):** ruff clean. mypy initially **78 vs 77 pre-item** — the audit's "all pre-existing" expectation was wrong by one: the new `generation/errors.py:4` lacked annotations. **Cured by the orchestrator** (typed signature + TYPE_CHECKING imports; audit-as-evidence, one-line-class fix): mypy now **77 errors = exact pre-Item-6 baseline**, so the reframed "no new errors" bar is genuinely met, cure verified by re-run. Finding 1's literal-criterion note stands (project baseline dirty), Finding-1-adjacent gap closed.
- **P4 (guard mutation):** fail-loud suite 7 passed → registry guard-pass deleted → exactly `test_registry_seam_refuses_constraint` FAILED (silent-drop path exposed) → revert → 7 passed. INV-3's test has teeth.

**Final verdict: Certify** (upgraded from Certify-with-notes; both notes resolved — dynamic gates executed, mypy delta cured to zero).
