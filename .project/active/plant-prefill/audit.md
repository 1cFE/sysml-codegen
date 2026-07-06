# Audit: Plant-Idiom Literal Pre-Fill (SC-5 stage 1) — Item 9

**Verdict:** CONDITIONAL (clears to PASS on the gate re-run + the ife_plant path-drift resolution)
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 5140432

---

## Summary

The substance is sound. The three one-function edits match the design exactly; the
literal filter genuinely excludes CHAIN/EXPRESSION; the four snapshot deltas are
semantically correct; every pin flip is correct and re-anchored as designed; the
divergent-sibling regression test genuinely catches the shared-object bug; docs, matrix,
backlog, and close-out notes all landed.

Two items block a clean PASS, neither a correctness defect in the shipped code:

1. **The final gate was never executed** — the same `uv run` sandbox block that hit
   Items 1/2/6/7/8 also blocked this auditor. Two re-anchors rest on static reasoning
   only. This is the pivotal open item.
2. **The ife_plant committed snapshot absorbed ~90 lines of environmental path-drift**
   unrelated to Item 9, of the same class that was *reverted* on three other fixtures.
   It breaks no test, but it makes the release-notes "calc_usages unchanged / every
   other snapshot byte-identical" claim inaccurate for ife_plant, and leaves the corpus
   in a mixed path-convention state the deferred chore does not account for.

---

## Findings

### Plan completion

All four phases verified against the commit.

- **Phase 0/1 (three edits + red-first unit tests):** verified.
  - `hierarchy_resolver.py` — `_keep_plain_usage_override` added (returns
    `redefinition_type is RedefinitionType.LITERAL`); guard relaxed exactly as designed
    (`is_part_redefines = bool(...)`, always scan members, `continue` on a plain-usage
    non-LITERAL override). Matches Architecture edit 1 / Implementation Notes.
  - `pipeline_builder.py:242` — bare-name `raise ValueError` → `logger.debug(...)` +
    `continue`. Matches edit 2 / REQ-VBR-09.
  - `usage_extractor.py:399` — `list(template.bindings)` →
    `[copy.copy(b) for b in template.bindings]` + `import copy`. Matches edit 3 / D2.
- **Phase 2 (capture + pin-flip + sweep):** snapshot deltas and pin flips verified
  statically (below). The gate re-run is the OPEN item the plan itself flags.
- **Phase 3 (docs/matrix/close-out):** verified (below).

### Spec conformance

- **Plain-usage `:>>` captured (SC-1).** `test_shape5_plain_usage_override_captured`
  (`test_ife_plant.py:163`) rewritten from "asserts absence" to "asserts capture": it
  reads `design_overrides` for a bare-name LITERAL `baseline_plant.capacity_factor = 0.95`
  and confirms the def-level 0.90 stays. The ife_plant snapshot carries exactly that
  override (`is_deep_path:false`, `literal_value:0.95`). Verified. Shape-5 is capture-only
  (unconsumed) per the signed-off correction — the test asserts capture, not a param flip.
- **alias_agg_probe / issue22 generate cleanly (SC-2).** All four pin rows verified in
  the committed tests: two collector pins → `[]` (`test_uncovered_params.py:90,101`);
  `test_alias_agg_probe_generation.py` rewritten to `test_plain_usage_literal_fixture_
  generates_clean`, parametrized over both fixtures (D4), asserting `run_codegen is True`,
  every `.py` `ast.parse`-valid, and quote/space-free identifiers (restores REQ-NC-08).
  Snapshots confirm `base_cost` → LITERAL 50.0 / 100.0, `source_path:null`.
- **Shared-BindingInfo divergent-sibling fixed + regression-tested (SC-3).** Verified the
  test is *real* by tracing the rewrite: `_create_virtual_calc_usage(t,
  "Design__plant__widgetA")` sets `qualified_name = "Design__plant__widgetA__cost_model"`;
  the rewrite's `parent_path = rsplit("__",1)[0] = "Design__plant__widgetA"`, matching the
  per-instance override key `("Design__plant__widgetA","base_cost")`. Without `copy.copy`,
  iA and iB share one `BindingInfo`; iA rewrites it to LITERAL 50.0, iB is then skipped at
  `pipeline_builder.py:230` (already LITERAL) and reads 50.0 — the `iB == 100.0` assertion
  fails. The test asserts the rewrite respects the instance boundary, not mere object
  distinctness, exactly as the design specifies.
- **CHAIN/EXPRESSION stay inert; no bare-name crash (SC-4).** The LITERAL filter is a pure
  predicate applied at capture, so CHAIN/EXPRESSION plain overrides never enter
  `design_overrides`. Counter-case confirmed: catf_mfe's cross-part `:>>` is CHAIN →
  `_keep_plain_usage_override` returns False → not captured → catf_mfe snapshot is
  byte-identical (not in the changed-files set) → stays V11-pinned
  (`test_collector_pins_catf_mfe_dangle` unchanged). Bare-name safety covered by
  `test_rewrite_skips_bare_name_source_path_without_raising` (non-empty index, no raise,
  DEBUG logged, binding unchanged).
- **Existing 4 baselines byte-identical except the flip fixtures (SC-5).** File-level
  INV-5 holds: `git show --stat` shows exactly four `extraction_snapshot.json` changed
  (alias_agg_probe, ife_plant, issue22_model, unresolvable_attr_probe), plus code / tests
  / docs. No `baseline_outputs/` churn. **But see Design conformance finding 1** — the
  ife_plant diff is not confined to the promised single `design_overrides` entry.
- **REQ IDs / matrix / docs move with the code (R1).** Verified: matrix rows REQ-HR-08,
  REQ-VBR-08, REQ-VBR-09 (counts 209→212, PASS 195→198); doc 25 (guard relaxation +
  LITERAL filter + performance note); doc 12 (shallow-copy + bare-name skip with the m1
  by-branch reachability correction). Doc 18 (LVP) untouched — scope 2 cut, correct.
- **agentic-mbse impact recorded (R2).** Present in release-notes and design: plain-usage
  literal overrides now honored (teach in Item 12); self-named check stays a FAIL until
  Item 10; no checker script here.

### Design conformance

**Finding 1 (CONDITIONAL) — ife_plant snapshot carries un-reverted environmental
path-drift.** `tests/fixtures/ife_plant/extraction_snapshot.json`. The design's Baseline
regen and release-notes state ife_plant's change is "`design_overrides` gains one entry;
`calc_usages` unchanged." The actual diff is ~90 extra lines of path canonicalization,
unrelated to the capacity_factor change:

- `source_file` relativized on every calc_def **and calc_usage** entry
  (`tests/fixtures/ife_plant/library.sysml` → bare `library.sysml`) — so "calc_usages
  unchanged" is factually wrong.
- `design_attributes` map keys turned into machine-specific **absolute paths**
  (`/home/reid/1cfe/sysml-codegen/tests/fixtures/ife_plant/library.sysml`).
- `exposed_computations` `document_path` rewritten `file:...` → `file:///home/...`.

This is the exact drift class that Phase 2 *reverted* on `wi014_toy`,
`self_named_binding_trap`, and `quoted_owner_formula` and filed as a deferred chore. It
rode along in ife_plant because that fixture also had the wanted change, so a
`git show HEAD:… > …` revert was not applied. Impact: no test breaks (tests key on
`qualified_name`, not paths, and `baseline_outputs/` is untouched), but the committed
corpus is left in a mixed path convention (ife_plant migrated; three others pending),
and the release-notes / design "byte-identical / calc_usages unchanged" statements are
inaccurate for ife_plant. **Fix:** either strip the path-drift lines from the ife_plant
snapshot (keep only the capacity_factor `design_overrides` delta, so it matches the
reverted fixtures and the stated scope), or amend release-notes + the BACKLOG chore to
record that ife_plant was migrated to the new path convention ahead of the other three
and correct the "calc_usages unchanged" claim. Note: `/home/reid` already appears in ~14
committed snapshots, so machine-specificity is a pre-existing corpus property — this
finding is about the *un-reverted drift* and the *inaccurate claim*, not new
non-portability per se.

The other three snapshot diffs are clean and match the design exactly: alias_agg_probe
(base_cost→50.0 + deep-path override), issue22 (100.0), unresolvable_attr_probe (6
`design_overrides`: base_rate/base_factor/local_multiplier on derived_instance,
base_rate/base_factor/local_val on design_derived_instance; `my_calc.x`→LITERAL 5.0). No
path-drift on those three (single-file fixtures / empty `compilation_results` — nothing to
drift).

**Adjudicated deviations — verified recorded and sound:**

1. **Scope 2 cut.** Recorded in spec (scope-2 finding) and design; the def-literal
   pre-fill is already met by the Item 8 ife_plant baseline. Sound.
2. **D5 re-anchor.** `unresolvable_attr_probe`'s `my_calc.x` now pre-fills (correct — its
   valueless-ness *was* the bug); the committed V11 proof re-anchors to catf_mfe (strict
   raise, `test_reconcile_raises_v11_on_wired_gap` → `catf_mfe_model`) and ife_plant
   shape-4 (`test_seeded_strict_generation_aborts_independently_of_catf_mfe` → `ife_plant`).
   Both re-anchors present and correct in code. The ife_plant strict-abort re-anchor is
   **statically sound but unrun** (see gate finding).
3. **12 non-enumerated re-captures reverted; 3-fixture path-drift chore filed.** BACKLOG
   entry present and names the `quoted_owner_formula` reclassification question explicitly
   ("confirm net_margin/total_payout SHOULD be computed, not design attributes"). Sound.
4. **Two stale hierarchy-structure pins flipped.** `test_hierarchy_resolver.py`
   `test_cross_model_issue22_hierarchy` and `TestAliasAggProbe::test_hierarchy_structure`
   both flipped 0→1 `design_overrides` with content assertions (`target_path ==
   ["widget","base_cost"]`, `literal_value == 100.0 / 50.0`). Reviewed to the same bar as
   the checklist rows — they assert the captured override content, not a bare count. Sound.

### Code integrity

No slop or failure-honesty issues.

- `_keep_plain_usage_override` is a one-line pure predicate at the correct altitude — the
  keep/drop policy lives at the capture site (D3), not buried in the rewrite utility.
- The bare-name branch replaces a raise with a DEBUG-skip that is honest about *why* it is
  safe (no deep-path key matches a bare leaf) and defers the rescue to Item 10 — not a
  silent swallow.
- `copy.copy` (not `deepcopy`) is the minimal correct copy, with the reasoning (AST-node
  references are read-only, deepcopy would recurse the parse subgraph) documented at the
  site and in doc 12. No parameter sprawl, no god function, no leaky name.

---

## Certification

**Statically verified (would clear to PASS on execution):** the three edits vs. design;
the LITERAL filter's CHAIN/EXPRESSION exclusion (catf_mfe counter-case); the four snapshot
deltas' semantic content; file-level INV-5 (exactly four snapshots, no baseline_outputs
churn); every pin flip and the two V11 re-anchors; the divergent-sibling test's ability to
catch the shared-object bug; the bare-name crash-safety test; docs 12/25, matrix rows,
BACKLOG chore, release-notes, agentic-mbse impact, deep_cross_scope drift note.

**Conditions to clear to PASS:**

1. **Run the gate** — `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/`
   (expected 1932 / 4 / 11; mypy 109; ruff 21). This auditor was blocked from all
   `uv run` / python execution (only git + shell builtins pass — the same block recorded
   for Items 1/2/6/7/8). Two re-anchors are verified by static reasoning only and must be
   confirmed by the run: (a) ife_plant trips **strict** V11 at generation (run_codegen
   False + V11 log), not just the in-memory collector; (b) ife_plant `baseline_outputs`
   byte-identity. If (a) fails, author a minimal genuinely-unbound seeded fixture (design
   → Potential Risks).
2. **Resolve the ife_plant path-drift** (Design conformance finding 1) — strip the drift
   or amend the release-notes/BACKLOG to record the migration and correct the "calc_usages
   unchanged" claim.

**Epic mapping (Item 9 success criteria):**
- *BindingInfo aliasing covered by a regression test* — **met** (verified real).
- *Existing 4 baselines unchanged; plant-fixture diff reviewed* — **met with condition 2**
  (file-level yes; ife_plant diff exceeds the stated scope).
- *Fresh IFE generation pre-fills plant/driver JSONs (WI-015: 2/16 → )* — **fixture-
  evidenced, real-run opportunistic.** The 16 def-literals are already pre-filled in the
  committed `baseline_outputs/ife_plant/computation_graph.json` (Item 8 baseline;
  `usage_literal` EPs with non-null defaults — only shape-4 `magnet_volume` is null →
  Item 10), and Item 9 adds the capacity_factor capture without regressing it. The actual
  fresh fusion-tea IFE run is license-blocked and opportunistic (spec executable gate =
  fixture diff; Item 3 D6 precedent) — not evidenced in this commit.

Epic heading left unmarked (verdict CONDITIONAL). No production changes made; no commits.


---

## Orchestrator close-out (2026-07-05)

Both conditions cleared:
1. Gate run by the orchestrator at the committed state and re-run after the docs amendment:
   **1932 passed / 4 skipped / 11 xfailed; ruff 21; mypy 109** (== baseline). The two
   static-only re-anchors are covered by the passing suite (ife_plant strict-V11 test and
   the baseline conformance tests are in it).
2. ife_plant path-drift: ACCEPTED as canonical-form migration (stripping it would leave the
   snapshot permanently non-script-reproducible). Release notes amended to record the
   migration precisely; BACKLOG chore updated to remove ife_plant from the deferred list.

Verdict upgraded: **PASS**. Item 9 complete.
