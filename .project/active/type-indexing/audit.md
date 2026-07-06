# Audit: Part-Usage Type Indexing (SC-3) — Item 4

**Verdict:** PASS / Certify
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 82b70b8

---

## Summary

The fix is sound and fully evidenced. Both first-type picks are replaced by an owned-FeatureTyping
heritage walk; the retyped `the_variant.driver` instantiates its subtype template, its supertype
template still flows, the same-named collision resolves to the most-specific owner with V9, and the
plain sibling is untouched — all six pinned shapes are present in the committed snapshot. The one
recorded deviation (FIX 2 fallback for untyped parts) is correctly scoped and cannot reintroduce the
bug for retyped usages. Docs, REQ tags, V9/V10, and the agentic-mbse carry-through are all in place.

Tests were not re-run (the sandbox blocked `uv run`). Certification rests on the recorded gate
(1870 passed / 4 skipped / 5 xfailed; ruff 21; mypy 109 — all == baseline) plus direct inspection of
the committed `retype_model` snapshot, whose contents map one-to-one onto the offline test assertions.

## Findings

### Plan completion

All three phases verified complete against committed artifacts.

- **Phase 0 (probe gate).** Outcomes recorded verbatim in plan Implementation Notes (B1 owned-only,
  B2-plain excludes supertype, Q2b multi-typing order, Q4 library-excluded). B1/B2-plain both
  CONFIRMED — no hard stop. The chosen accessor (raw `usage.heritage` filtered to `FeatureTyping`)
  and user filter (`user_qn_set` intersection) match what the code does (`usage_extractor.py:161-163,
  292-300`).
- **Phase 1 (helpers + unit test).** Four helpers present (`usage_extractor.py:144-263`):
  `owned_feature_typing_targets`, `user_partdef_types`, `_supertype_closure`, `most_specific`, plus
  `user_partdef_lookup`. `most_specific` uses the maximal-element rule (plan design note), sorts by QN
  for the incomparable tiebreak (machine-independent). Unit test `test_type_indexing_helpers.py` has
  6 cases (chain sink, order-independence, incomparable→sorted-first, single, zero→(None,False),
  dedup) — matches plan stencil plus the extra cases claimed.
- **Phase 2 (three fixes + fixture + snapshot).** FIX 1 (`_build_part_usage_index:266-304`), FIX 2
  (`hierarchy_resolver.py:533-562`), FIX 3 (`_expand_template_calc_usages:441-506`) all landed. Fixture
  + committed snapshot + `test_type_indexing.py` (7 tests) present.
- **Phase 3 (baseline zero-diff + docs).** Recorded as a runtime re-run with content zero-diff across
  all 4 baselines; `test_factory_purity` green. Docs/matrix/REQ tags landed. No baseline snapshot file
  is in the commit's 17 files — consistent with the "content invariant, files restored" note.

No placeholder code, TODOs, or partial implementations found in the changed source.

### Spec conformance

Success criteria — each verified:

- **SC: subtype template instantiates.** ✅ Snapshot has `...the_variant__driver__hif_calc` owned by
  `RetypeLibrary__HIF_Driver` (snapshot line 313-315). Test:
  `test_subtype_and_supertype_templates_both_instantiate`.
- **SC: supertype flow preserved.** ✅ Snapshot has `...the_variant__driver__ife_calc` owned by
  `RetypeLibrary__IFE_Driver` (line 238-240). Same test asserts owner == IFE.
- **SC: usage_type_map resolves retyped to declared PartDef.** ✅ `(Variant, driver) → HIF_Driver`,
  `(Facility, driver) → IFE_Driver` (snapshot line 421-422). Test:
  `test_usage_type_map_resolves_retyped_to_declared`.
- **SC: 4 baselines zero-diff by runtime re-run.** ✅ Recorded PASS (content diff = 0 excl.
  `captured_at`); the first re-run surfaced the catf_mfe regression, the fallback fixed it, the second
  re-run was clean. `test_factory_purity` green (offline byte-identity). Not re-run by auditor —
  relying on recorded evidence.
- **SC: same-named collision → deterministic winner + warning naming both candidates.** ✅ Snapshot
  has exactly one `...the_variant__driver__shared_calc`, owned by HIF (line 255-257). V9 text names
  both owners and the winner (`usage_extractor.py:500-504`). Tests:
  `test_same_named_collision_tiebreak` (offline winner) + `test_collision_emits_v9_warning_live`
  (asserts both owners + `kept most-specific owner '{HIF}'`).
- **SC: differently-named → both instantiate.** ✅ `ife_calc` (IFE) and `hif_calc` (HIF) both present
  on `the_variant.driver`; covered by `test_subtype_and_supertype_templates_both_instantiate`.
- **SC: plain subtype usage NOT reached by supertype template.** ✅ No `plain_hif__ife_calc` in the
  snapshot; `plain_hif__hif_calc` and `plain_hif__shared_calc` (both HIF-owned) present. Test:
  `test_plain_sibling_not_reached_by_supertype_template`.
- **SC: unique, consumer-scope-prefixed keys.** ✅ Keys are `__`-form PartDef QNs (globally unique);
  no ambiguous string keys introduced.
- **SC: docs updated with REQ tags.** ✅ See Design conformance.
- **SC: agentic-mbse impact recorded.** ✅ Spec §"agentic-mbse impact" (teach retyping; Level-6
  "instantiated" now includes retyped usages); echoed in epic lines 196, 410, 413. Recorded, not
  executed — Item 12 runs it.

Multi-typing V10: ✅ `(MultiHolder, multi) → IFE_Driver` (sorted-first of {IFE, Other}) with the V10
warning in `hierarchy_data.warnings` (snapshot line 406). Test:
`test_usage_type_map_incomparable_resolves_and_warns`.

Tagged requirements:

- **REQ-EXT-13** (superset index) — met (`_build_part_usage_index:296-302` unions owned typings ∪
  user `.types`; live test asserts the retyped driver under both IFE and HIF).
- **REQ-EXT-14** (collision policy) — met (FIX 3 tiebreak + V9; differently-named both survive).
- **REQ-LVP-08** (most-specific `usage_type_map`) — met (FIX 2).

Non-goals respected: no supertype-chain walk for plain usages (shape 5 negative proves it); no
backtracker/generation change (INFERRED constraint — the commit touches only
`usage_extractor.py` + `hierarchy_resolver.py` in `src/`); no template-detection change.

### Design conformance

Implementation follows the design.

- **D1** (one shared helper, two projections) — helpers live in `usage_extractor.py`, imported by
  `hierarchy_resolver.py`. ✅
- **D2** (most-specific = specialization-chain walk, prebuilt `qn_to_partdef`, sorted-first tiebreak)
  — `most_specific` + `_supertype_closure`; lookup built once per pass
  (`hierarchy_resolver.py:515`, `usage_extractor.py:423`). ✅
- **D3** (tiebreak at `seen_qns`, set→dict, compares stored virtual's owner) — `usage_extractor.py:444,
  472-506`; compares `existing.owning_part_def_qn` vs incoming, same-owner stays silent. ✅
- **D4 / M1** (keys stay plain `__`-form `str`, NOT `SysMLQN`) — confirmed: all keys/values produced
  by `build_element_qualified_name` (default `__`-form); no `SysMLQN` wrapper anywhere in the changed
  code. ✅
- **D5** (one fixture, shapes 1–5; shape 6 = existing baselines) — `retype_model/{library,design}.sysml`
  holds all shapes; no new baseline fixture. ✅
- Invariants INV-1..5 hold: per-usage key set built as a `set` (INV-1, `:296`); plain usage keyed under
  its one declared type (INV-2, proven by shape 5 + baseline zero-diff); `usage_type_map` single-valued
  (INV-3); collision only on same path + same calc name (INV-4/5).

Recorded deviations — both verified sound:

1. **FIX 2 fallback for untyped parts.** `hierarchy_resolver.py:543-552`. When `most_specific` returns
   `None` (empty owned-typing list, i.e. an untyped `part x {}` or a typing-inheriting redefinition),
   the code falls back to `next(iter(member.types))` to restore the historical `Parts__Part` entry.
   **This cannot reintroduce the first-type bug for a retyped usage:** a retyped `:>> driver : Sub`
   carries an owned FeatureTyping (probe B1), so `owned_feature_typing_targets` is non-empty,
   `most_specific` returns a non-None winner, and the fallback branch is never entered. Verified by
   tracing the code path — the fallback is gated strictly on `winner is None`. The dead `Parts__Part`
   entries it preserves never match a user redef's `owning_part_qn`; kept only for the hard
   byte-identity requirement, and proven harmless by the zero-diff re-run. Recorded in plan Phase 2
   notes and doc 25. Sound.
2. **Probe model syntax fixes** (`attr`→`attribute`, `Real` import). Shapes unchanged; recorded in
   plan Phase 0. Sound.

Docs verified present and correct:

- `modeling-assumptions.md` — §5 "Type Redefinition (Retyping)" subsection (line 269); V9 (line 378)
  and V10 (line 379) in the Validation table **after** V8 (line 377, Item 3's). V-style text matches
  the emitted strings.
- `reference/01-extraction.md` — REQ-EXT-13/14 rows (lines 24-25) + index/collision paragraph.
- `reference/25-hierarchy-resolver.md` — REQ-LVP-08 row (line 28) + most-specific rule including the
  untyped-usage fallback (line 43).
- `verification-matrix.md` — REQ-EXT-13, REQ-EXT-14, REQ-LVP-08 → `test_type_indexing.py`, all PASS
  (lines 208-209, 279).

### Code integrity

No blocking issues. The change is well-abstracted: one primitive (`owned_feature_typing_targets`),
two projections, a maximal-element comparison, and a local dedup tiebreak. No god functions, no policy
leaked into utilities, no broad excepts (the one `try/except` at `:549-552` catches a specific
`StopIteration, TypeError, AttributeError` triple around a single `next(iter(...))`, not a blanket
swallow). No mocks in the fix's fixture path — a real SysML model + live-captured snapshot (R1
satisfied). The one mock touched (`test_template_detection.py` `_mock_elements_of_type`) is an existing
unit test legitimately extended to serve the new `PartDefinition` query the index now issues.

Two low-severity observations (non-blocking, no change required):

- **V9 wording on an incomparable collision.** `usage_extractor.py:487` calls
  `most_specific([existing_owner, owner_qn], lookup)` and ignores the returned `incomparable` flag; the
  V9 text always says "kept most-specific owner". If two *incomparable* owners ever collided on one
  virtual QN (e.g. a `multi : A, B` usage where both A and B own a same-named calc), the winner would
  be sorted-first, not genuinely "most-specific," and the message would be slightly misleading. This is
  outside the pinned 2-owner super/subtype fixture matrix — a same-path collision in the retyping shape
  is always between comparable super/subtype (design B4) — so it cannot arise in the tested shapes.
  Worth a one-line comment if the incomparable-multi-typing collision is ever pinned; not a defect now.
- **Fallback writes library QNs into `usage_type_map`.** Preserved deliberately for byte-identity;
  documented; proven inert by the zero-diff gate. Noted for completeness, not action.

---

## Certification

Checked and certified:

- All six fixture shapes present in the committed `retype_model` snapshot; each has a test asserting
  the spec'd outcome (shapes 1/2/4 → one test; shape 3 → tiebreak + live V9; shape 5 → negative;
  multi-typing → V10; superset index → live). Plus `usage_type_map` most-specific and V10.
- FIX 2 fallback traced: fires only when owned FeatureTyping is absent; does not reach retyped usages.
- Committed snapshot keys match the design's superset rule (retyped driver under both IFE and HIF;
  plain sibling under HIF only).
- V9/V10 V-style, placed after V8; REQ-EXT-13/14 + REQ-LVP-08 rows real and PASS; docs 01/25 + §5
  updated.
- Scope: 17 files, no scope creep; no mocks in the fix path; `__`-form `str` keys (not `SysMLQN`).
- agentic-mbse impact recorded for Item 12.

**Verification limits:** the suite, mypy, and ruff were not re-run (sandbox blocked `uv run`). Green
rests on the recorded gate (1870/4/5; ruff 21; mypy 109 == baseline) and direct inspection of the
committed snapshot + test assertions. Live-layer tests (index key set, V9) skip without a license and
were not exercised here; their offline mirrors are all verified against the committed snapshot.

Marked: spec success criteria, plan phases, and epic Item-4 success checkboxes.


---

## Orchestrator close-out (2026-07-05)

Verification limit covered: orchestrator ran the full gate at the committed code state
immediately before the item-4 commit: 1870 passed / 4 skipped / 5 xfailed; ruff 21; mypy 109
(== baseline). Verdict stands: **PASS**. Item 4 complete.
