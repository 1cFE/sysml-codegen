# Audit: Resolution Matcher Fixes & Warning Reconciliation (SC-8) — Item 7

**Verdict:** CONDITIONAL
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 7aec029

---

## Summary

The implementation is sound and faithful to the design. All six lockstep flip sites
sanitize (INV-1 grep clean), the V11 collector is pure and correctly predicated on
fell-through ∩ valueless ∩ wired, the M1 partition order matches the design (summary
logged before the V11 raise), and the warning demotions + count-summary + zero-WARNING
assertions are all present with real fixtures and no mocks. Docs, matrix rows, README
correction, and the three-part release-notes review all landed.

Two items keep it short of PASS, both auditable:

1. **The item's central behavioral churn — retype_model's 3-EP reclassification — has
   no regression pin and is gate-unconfirmed.** The mechanism is unit-tested with
   synthetic data, but the one real corpus reclassification (USAGE_LITERAL →
   DESIGN_ATTRIBUTE, values → 10.0/20.0/20.0) is asserted nowhere and rests on a
   Phase-0 computation the release notes mark "*(Gate-confirm.)*". This is the
   "behavioral change without a pin" the audit task flagged.
2. **The suite gate could not be re-run in this session** (execution approval-gated,
   same block as Items 1/2/6). Certification of "suite green" rests on the recorded
   gate, not an independent run.

Fix #1 (add a pin) and re-run the gate → PASS.

## Findings

### Plan completion

All six phases are complete per plan.md's completion notes, and the code matches.
Phase 0 (before-capture + leaf-uniqueness) produced the DEV-1..3 corrections;
Phases 1–5 landed as recorded. One gap in the Phase-4 deliverable — see Spec
conformance (retype pin).

### Spec conformance

- **Zero-WARNING clean fixtures** — MET. `test_warning_reconciliation.py` asserts
  strict zero-WARNING for attr_expr_probe / sample_model / chain_spike; solar_battery
  is category-scoped (DEV-3/C1 — two out-of-scope warnings it does not own). Sound.
- **Two matcher fixes reclassify at the correct stage/kind** — MECHANISM MET, corpus
  instance UNPINNED. Bug A (`::` per-segment sanitize) and Bug B (def-owned leaf-unique
  with the A1 calc-def-I/O pool restriction) are correct in `dependency_backtracker.py`
  and unit-tested in `test_matcher_fixes_item7.py` (6 tests: leaf-unique resolve,
  ambiguous refuse, calc-I/O excluded, calc-I/O collision still resolves, quoted-owner
  `::` match, no-false-match). But these use synthetic `DesignAttributeData` mirroring
  the retype shape; **no test exercises retype_model's real graph** and asserts the 3
  EPs classify DESIGN_ATTRIBUTE with values 10.0/20.0/20.0. See the retype finding below.
- **Six lockstep sites flip in one change; grep clean** — MET. All six sanitize
  (`output_registry_builder.py:134`, `dependency_backtracker.py:625` + `::`-branch,
  `pipeline_builder.py:73`, `input_resolver.py:127`, `parameter_groups.py:442`).
  `grep sysml_to_python_qualified_name src/` returns only the definition + export in
  `qualified_names.py`/`core/__init__.py` — zero production consumers. `sysml_qn_lookup`
  callers both sanitize. INV-1 holds.
- **Step-3 dedup returns** — MET as designed, but VACUOUS on the corpus (DEV-1): the
  two worksheet dedup pairs (pack_count, p_net_mw) were shown in Phase 0 not to occur
  (literal binding; `::`-exact branch). Recorded and sound. No corpus key collapses.
- **V11 hard error on uncovered params; catches catf_mfe magnet_volume** — MET.
  `collect_uncovered_params` (`graph_builder.py`) pins catf_mfe exactly to
  `[cryo_load.magnet_volume]` (`test_uncovered_params.py`, INV-4). Strict raise at the
  generation boundary (`cli/__init__.py:_reconcile_params_coverage`), no escape hatch.
- **Seeded fixture proves V11 fires independently of catf_mfe** — MET via deviation
  (Q2-b): `unresolvable_attr_probe` (a pre-existing purpose-built fixture) is the
  seeded proof; `test_seeded_strict_generation_aborts_independently_of_catf_mfe`
  asserts run_codegen → False + logged V11. No new SysML fixture authored (recorded
  spec deviation). Acceptable — the fixture genuinely exercises all three V11 predicate
  components.
- **Per-binding Step-4 → DEBUG; post-assembly summary at WARNING** — MET.
  `dependency_backtracker.py` Step-4 line is DEBUG; `collect_unwired_fallthrough` +
  the WARNING summary in `_reconcile_params_coverage`. Summary logged first, then V11
  raised (design seam-4 order).
- **Alias collisions collapse to one count-summary** — MET. `output_registry.py`
  records collisions + DEBUG per-line; `output_registry_builder.py:227` emits one
  WARNING summary. `test_alias_collisions_collapse_to_one_summary` pins it.
- **Reclassification/dedup churn reviewed, captured in baselines + release notes,
  with keys AND values** — PARTIAL. release-notes.md enumerates the reclassified EPs
  (retype 3), the (empty) key collapses, and the value moves (10/20/20). But the
  "captured in regenerated baselines (R3)" half is a no-op by circumstance: retype_model
  has no committed pipeline baseline to regenerate, and no test was added in its place.
  So the enumeration exists in prose but has no executable guard. See finding.

### Design conformance

- **INV-1 (flip completeness)** — HELD (grep clean, six sites).
- **INV-2 (no cross-wire)** — HELD. Leaf-unique refuses on 0/>1 candidates; the A1
  `_is_calc_def_owned` filter excludes calc-def I/O so a dotted calc-output reference
  (chain_override_probe) stays loud rather than cross-wiring. Unit-pinned.
- **INV-3 (collector purity)** — HELD. Both collectors return lists, raise nothing;
  only `_reconcile_params_coverage` raises. `test_collector_is_pure_on_clean_graph`.
- **INV-4 (catf_mfe == [cryo_load.magnet_volume])** — HELD, pinned exact.
- **INV-5 (zero-WARNING)** — HELD, scoped per DEV-3.
- **INV-6 (flip byte-invariant on baselines)** — HELD; no committed baseline churned
  (release notes §3; DEV-4 keeps `fallback_entry_points` out of serialization).
- **DEV-4 (`exclude=True`, --from-snapshot parity)** — SOUND and TESTED.
  `test_fallback_entry_points_populated_in_memory_but_not_serialized` confirms the
  field is populated in-memory by the snapshot-driven backtracker run (so V11 fires
  identically on `--from-snapshot`), absent from `model_dump()`/`model_dump_json()`,
  and empty on a round-tripped graph. The field-count contract tests (REQ-DM-03,
  REQ-GA-05) flip to 4 fields as green assertions, not weakened.
- **M1 partition order** — MATCHES design: summary WARNING logged first, V11 raised
  second, so the digest reaches the operator even on abort (`cli/__init__.py`).
- Orchestrator nit #6 (per-segment identifier check for dotted `module_type`) — present
  in `test_alias_agg_probe_generation.py` (`seg.isidentifier() for seg in
  module_type.split(".")`).

### Code integrity

No slop or failure-honesty issues. The collectors are single-purpose and pure; the
CLI boundary raises loudly (no silent fallback); the A1 pool restriction is a real
safety property, not a papered-over default. `_is_calc_def_owned` uses
`getattr(cd, "qualified_name", "")` — a mild defensive default, but calc defs
reliably carry the attribute, and an empty QN simply excludes nothing extra; benign.

### The retype_model pin gap (the CONDITIONAL driver)

`release-notes.md:40-46` enumerates the only real behavioral churn in the corpus:
retype_model's `ife_calc|p`, `hif_calc|q` (×2) move USAGE_LITERAL → DESIGN_ATTRIBUTE
with default values 10.0 / 20.0 / 20.0 (via Bug A). This is the item's headline SC-8
output. It is:

- **Not asserted end-to-end.** `test_matcher_fixes_item7.py::test_quoted_owner_reference_matches_after_flip`
  proves the resolver returns the sanitized design-attr QN for a synthetic
  `RetypeLibrary::'IFE Driver'::power` shape — the mechanism — but never builds
  retype_model's graph nor asserts the EP kind/value. `test_type_indexing.py` touches
  retype_model but only for type-indexing shapes, not entry-point classification.
- **Not baseline-captured.** retype_model has no committed pipeline baseline, so
  Phase-4 regen was a no-op for it (release-notes §3 confirms).
- **Gate-unconfirmed.** The 10/20/20 values are Phase-0-computed; release-notes marks
  them "*(Gate-confirm.)*"; execution was blocked at implement and again at audit.

**Impact:** a future change that silently reverts this reclassification (e.g. back to
USAGE_LITERAL / None) would pass the entire suite. The spec elevates this behavioral
review to "a first-class deliverable, not a rubber stamp" and requires the value churn
"captured in regenerated baselines" — the prose enumeration is there, the executable
guard is not.

**Fix (one of):**
- Add a snapshot-driven conformance test that builds retype_model's graph
  (`build_full_graph_from_snapshot(snapshot_fixture("retype_model"))`) and asserts the
  3 EPs are `DESIGN_ATTRIBUTE` with `default_value` 10.0 / 20.0 / 20.0. License-free,
  cheap, and it is the actual SC-8 deliverable. **Preferred.**
- Or commit a retype_model pipeline baseline via the capture scripts (R3) so the diff
  is guarded.

### Execution / gate (certification caveat, not a code defect)

`uv run pytest`, `uv run ruff`, `uv run mypy`, and even `uv run python -c` are
approval-gated in this session (same turn-scoped block plan.md records as the
"Execution Blocker", and the same one that left Item 6 CONDITIONAL). I verified
everything statically. The recorded gate (commit message + plan.md) is **1909 passed /
4 skipped / 11 xfailed; ruff 21; mypy 109**. The xfail arithmetic reconciles: 5
pre-existing + 6 catf_mfe TestCATFMFEValidation downstream `pytest.xfail`s = 11; the 2
inverted V11 assertions (catf_mfe_aborts, alias_agg_probe_aborts) are passing tests,
not xfails. Certification of "suite green" rests on that recorded run.

---

## Certification

**Verified (static):**
- Six-site lockstep flip: all six sanitize; INV-1 grep clean (no production consumer of
  the bare swap; both `sysml_qn_lookup` callers sanitized).
- V11 collector: pure (INV-3), predicated fell-through ∩ valueless ∩ wired (D4/C1);
  catf_mfe pinned exact (INV-4); five-fixture corpus surface pinned (catf_mfe +
  alias_agg_probe abort tests, three green collector pins for issue22 /
  unresolvable_attr / chain_override).
- M1 partition: summary-first / V11-raise-second order matches design seam 4.
- Warning demotions (Step-4 → DEBUG, alias per-line → DEBUG) + one WARNING alias
  count-summary; zero-WARNING asserted for the three clean fixtures; solar category-scoped.
- Inverted E2E tests carry Item-9 / Items-9-11 tracking comments; REQ-NC-08 preserved
  at the identifier level (nit #6).
- DEV-4 exclude=True + --from-snapshot parity test present and sound.
- Docs: V11 row + SC-8 note in modeling-assumptions; matrix rows REQ-BT-09/10, GA-08,
  OR-09, PGD-08; README null-key correction (entry_point.py); release notes enumerate
  keys AND values.
- No mocks in any changed test (R1); field-count contract flips are green assertions.

**Open (blocks PASS):**
1. Add a retype_model reclassification pin (kind + values 10/20/20), or commit its
   baseline — the item's central behavioral churn is otherwise unguarded and
   gate-unconfirmed.
2. Re-run `uv run pytest tests/` (expect 1909/4/11), `ruff check src/` (≤21),
   `mypy src/` (≤109) in a Python-enabled env; confirm the retype 10/20/20 value churn
   by a snapshot-driven generate if a definitive record is wanted.

No spec/epic success-criteria checkboxes are marked here: SC-8's reclassification-capture
criterion is only partially met (prose yes, guard no), and the gate is unverified.
Clears to PASS on the two open items.


---

## Orchestrator close-out (2026-07-05)

Both conditions cleared:
1. **Reclassification pinned**: `tests/conformance/test_matcher_reclassification.py` (3 tests,
   snapshot-driven) asserts the two design-attribute entry points
   (`RetypeLibrary__IFE_Driver__power` = 10.0, `RetypeLibrary__HIF_Driver__torque` = 20.0,
   collapsed from two usages), and zero valueless USAGE_LITERAL residue. Values gate-confirmed
   live (the release notes' "3 EPs" enumerates per-usage; the two torque usages collapse to one
   key, which the pin also asserts).
2. **Gate re-run at the committed+pin state**: 1912 passed / 4 skipped / 11 xfailed; ruff 21;
   mypy 109 (== baseline).

Verdict upgraded: **PASS**. Item 7 complete.
