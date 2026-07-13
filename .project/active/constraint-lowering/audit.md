# Audit: Item 5 — Concrete Constraint Lowering

**Verdict:** Certify-with-notes
**Audited:** 2026-07-12
**Branch:** constraint-exec-epic
**Commit:** dd181ae (Phase 5 tail; wiring `0d6eba1`, Item 3 preflight `a1fe7a4`)

---

## Summary

The code delivers the spec: a fact-to-structure expander with a strict resolver whose only
outcomes are a real producer channel, a real design attribute, an overridable modeled default,
or a named generation error. The two classification axes are kept orthogonal, the terminal
switch makes fallback synthesis structurally unreachable in strict mode, and all six success
criteria have committed asserting tests that are correct by inspection. Turbulence — the
default-off flag, the widened ladder, the circular-import fix, the Item 8 handoff — is handled
soundly and (mostly) recorded honestly.

Two things hold this back from a clean Certify. First, **I could not execute anything this
session** — every interpreter invocation (`uv run`, `.venv/bin/python`, even `bash -c`) returns
"requires approval" with no approval path in this non-interactive run. So the plan's third-pass
green run (2202 passed, mypy 76, ruff clean, corpus empty-diff) is verified by static reading of
the code and tests, **not reproduced**. Second, the amended strict ladder is recorded in
`plan.md` + code comments but `design.md`'s D1/Architecture ladder enumeration is now stale.
Neither is a code defect; both are stated below.

## Findings

### Plan completion

All five phases are present in the tree and match their completion notes.

- **Phase 1** (`resolution/models.py:242-322`, `analysis/constraint_lowering.py`
  `mint_constraint_id`/`assert_unique_constraint_ids`) — `ConcreteConstraint`/
  `ConcreteConstraintInput`/`ConstraintInputResolution` land as plain-scalar Pydantic (no
  `arbitrary_types_allowed`); `predicate_ir`/`default_ir` are serialized `str`. ID minter is
  `{instance_path}__{source_local}__sha256[:16]` over a `sort_keys`/fixed-separator canonical
  tuple (`constraint_lowering.py:259-270`). Matches D3/N1/D4/D5-IR.
- **Phase 2** (`dependency_backtracker.py:38-76` `terminal_disposition`; `constraint_lowering.py`
  `resolve_actual`, `occurrence_scope`, `guard_polarity`) — the divergent step is one shared
  switch; the backtracker Step-4 block is a 5-line call plus the module function
  (`dependency_backtracker.py:626-635`), rungs above untouched. Verified by diff-reading, not
  the mini byte-identity run (blocked).
- **Phase 3** (`_expand_owner_instances`, `lower_constraints`) — four-kind dispatch, blocked-owner
  `NonFiniteCardinalityError`→named generation error (`constraint_lowering.py:349-356`),
  D7 unassessed inline. All three fixtures + `PROVENANCE.md` present.
- **Phase 4** (`pipeline_builder.py:754-979`, `pipeline_context.py:115`) — Step 2.6 extract, P1
  after Step 5.7, P2 before Step 6 pruning, P3 after Step 7, all behind
  `lower_constraints_enabled` (`:697`, default `False`) AND non-empty `constraint_facts.usages`.
- **Phase 5** — `test_constraint_pipeline_threading.py` (6 tests) + `test_constraint_lowering.py`
  (10) cover all six criteria through the wired path. Plan Phase 4/5 checkboxes in the "Changes
  Required" lists are still `- [ ]` though the completion notes say done — a bookkeeping lag, not
  missing work (the files/tests they name all exist).

### Spec conformance

All six success criteria have a committed asserting test; each is correct by inspection.
**Execution not reproduced this session — requested live probes** (see Certification).

1. **S4 reproduced** — `test_roots_before_pruning_retains_producer_s4_reproduction`
   (`test_constraint_pipeline_threading.py:20`): control (flag off) asserts `cost_calc` absent
   *and* `concrete_constraints == []`; lowered (flag on) asserts `cost_calc` present via the
   joined root plus the aggregator node. Correct shape.
2. **Strict resolution, no fallback** — `test_strict_resolution_no_fallback...` (`:48`) re-runs
   `_validate_channel_references` + `collect_uncovered_params` independently on the wired graph
   and asserts `fallback_entry_points == set()`; `test_strict_terminal_raises_never_synthesizes`
   (`test_constraint_resolver.py:178`) names the actual. The [HARD] is real in code: after every
   ladder rung misses, `resolve_actual` calls `terminal_disposition(strict=True)` which raises,
   then an `AssertionError("unreachable")` guards the impossible fall-through
   (`constraint_lowering.py:250-256`). No synthesis branch is reachable when `strict=True`.
3. **Deterministic identity** — `test_deterministic_identity_across_repeated_live_loads` (`:67`)
   asserts two fresh `build_pipeline_context` loads give byte-identical, sorted `constraint_id`
   lists; `assert_unique_constraint_ids` + `.sort()` enforce ordering (`constraint_lowering.py:592`).
4. **Corpus byte-identity** — proven structurally: with the flag off `concrete_constraints`
   stays `[]`, so P2's set-comprehension is empty and P3 is skipped
   (`pipeline_builder.py:864-979`). `extract_constraint_facts` runs unconditionally at Step 2.6
   but only reads the model — no graph effect. Inertness holds by construction; the empty-diff
   run itself is requested-live.
5. **Multi-instance** — `test_multi_instance_..._shared_binding` (`test_constraint_lowering.py:43`)
   and the wired `test_multi_instance_end_to_end...` (`:83`): 3 ids / 3 evaluation channels /
   `len(bound)==1` (the B1-settled recorded shared de-indexed producer binding). Fixture is a
   `part_def`-owned `assert` nested in `Cell[3]` — genuinely three occurrences.
6. **Inline** — `test_inline_source_form_selects_usage_predicate` (`:95`) asserts
   `source_form=="inline"` and `predicate_ir == serialize_expression(usage.predicate)`. Note:
   predicate selection is not done in Item 5 — extraction pre-selects the effective predicate
   onto `usage.predicate`; lowering only serializes it (`constraint_lowering.py:528-537`). The
   fixture and test still exercise the inline source-form end to end.

Tagged-requirement spot checks: INV-2 (fallback-unreachable) — confirmed above. INV-3 (own
id/channel per sibling, recorded shared input) — `evaluation_channel=f"{constraint_id}__evaluation"`
per occurrence (`:587`), `bound_channel` recorded per input. INV-5 (QN-keyed/deduped mint) —
`extend_graph_with_constraints.mint` dedupes by `existing_param_qns` (`:690,712`). INV-8
(nullable guard) — scoped to `is_negated` only; the `membership_kind` narrowing is a recorded
correction (see below). Non-goals respected: no module/compiler/aggregator *emission* — P3 builds
graph *nodes* only, `module_type` is an explicit placeholder deferred to Item 7
(`constraint_lowering.py:609-621`).

### Design conformance

Implementation follows design rev 2, with one recorded reinterpretation and one
recorded-but-under-propagated amendment.

- **D1 terminal-switch reinterpretation** ("one code path with an explicit switch" → "one
  terminal switch, two ladders sharing the terminal") is surfaced in `design.md` D1's own
  surfacing note and adjudicated agent-grade. The load-bearing intent (fallback structurally
  unreachable in strict mode) is verified in code. Conformant.
- **INV-8 `membership_kind` correction** — live extraction shows `membership_kind` is `None` for
  every ordinary in-profile `assert`; guarding it would reject 100% of real input. `guard_polarity`
  correctly scopes to `is_negated`, and the correction is recorded in `plan.md` Phase 1/3 notes and
  the `guard_polarity` docstring (`constraint_lowering.py:291-318`). Surfaced, not silent.
- **Widened strict ladder — recorded, but design.md is stale (Note 2).** Code adds two rungs
  beyond design.md's stated `scoped_lookup → alias_lookup → design-attr-by-QN`: a
  `scoped_alias_lookup` rung (`constraint_lowering.py:188-212`) and an occurrence-scoped
  design-attribute form matching the materializer-synthesized QN
  `{owner_instance_path}__{dotted}` (`:230-237`). Both are **pre-authorized** by design.md B4/R5
  ("add it to the strict ladder if a further omitted rung turns out in-profile — the terminal
  switch stays") and recorded in `plan.md` Phase 4 third pass + code comments. The [HARD] holds:
  `scoped_alias_lookup` returns an existing registry channel (MODULE_OUTPUT, `bound_channel`
  recorded), and the occurrence-scoped design-attr rung only resolves when `occ_attr_qn` is
  already a real key in `design_attr_by_qn` — so it mints against a real attribute QN, never a
  synthesized EP key. No F4-style EP-key collapse is reintroduced. The gap is documentation:
  `design.md` D1 and the §Architecture resolver-seam still enumerate three rungs, so the design
  of record understates the ladder by two forms.

### Code integrity

Strong. No god-functions; `resolve_actual` is a single ordered ladder, `lower_constraints`
splits expand/select/resolve/mint cleanly. Failure honesty is good — the whole item exists to
replace silent drops with named errors, and it does: blocked owner
(`constraint_lowering.py:351`), no-occurrences validation error (`:358`), non-reference actual
(`:410`), missing LocationFact (`:387`), profile BLOCK with per-diagnostic reasons (`:481`).

- **No broad excepts / no silent fallbacks.** The one `try/except` catches exactly
  `NonFiniteCardinalityError` and re-raises named (`:349-356`). `_literal_float` narrows
  `(TypeError, ValueError)` around a float cast only (`:631`).
- **Circular-import fix is legitimate and recorded** — `_generation_error` lazy-import helper
  (`:61-74`) with a docstring explaining the `orchestration/__init__.py` eager-import cycle;
  mirrors the existing `terminal_disposition` pattern. Recorded in `plan.md` Phase 4 third pass.
- **P2 `_find_usage_for_channel` private-access** (`pipeline_builder.py:897`, `# noqa: SLF001`)
  reuses the S4-proven seam unchanged, with a guard raising when no producer is found — no silent
  skip. Acceptable.
- **Minor: `zip(facts.usages, profile.decisions, strict=True)`** (`:490`) assumes the profile
  returns index-aligned decisions. `strict=True` makes a length mismatch loud (ValueError) rather
  than silent — correct defensive choice; flagged only so a future reader knows the coupling.

## Certification

**Verified by static inspection (code + tests read, execution blocked this session):**
- All six success criteria have committed, correctly-shaped asserting tests.
- The fallback-unreachable [HARD]: `resolve_actual` always terminates in
  `terminal_disposition(strict=True)` (raises) guarded by an unreachable-assert; the widened
  ladder adds no synthesis path.
- **Mutation probe (reasoned, not executed):** flipping `resolve_actual`'s terminal call to
  `strict=False` makes `terminal_disposition` *return* a fallback QN instead of raising; control
  then hits `raise AssertionError("unreachable...")`. `test_strict_terminal_raises_never_synthesizes`
  expects `CodeGenerationError`, so the propagating `AssertionError` fails the test → RED.
  Revert restores GREEN. The guard is mutation-sensitive.
- Flag semantics: default path yields `concrete_constraints == []` (P2 empty, P3 skipped →
  byte-identical by construction); enabled path is exercised by 6 wired tests.
- Widened ladder preserves the [HARD] (no EP-key synthesis) and is recorded (plan + comments +
  B4/R5 pre-authorization).
- Circular-import fix and the `gain` hierarchy-extraction gap are both recorded; the latter is
  genuinely outside Item 5's ownership — Item 5 consumes `graph_design_attrs`/`hierarchy_data` as
  given and does not own their extraction — correctly handed to Item 8's spec.

**Notes (do before/at Item 8, none blocking):**
1. **Reproduce the gates.** Re-run in an exec-capable session: the 16 live tests, the mutation
   probe, full suite, `mypy src/` (baseline 76), `ruff check src/`, and the corpus
   regenerate→timestamp-only-diff→revert gate. The plan's third pass reports all green; this
   audit did not reproduce them.
2. **Amend `design.md` D1/§Architecture** to enumerate the five resolution forms the code
   actually tries (add `scoped_alias_lookup` and the occurrence-scoped materialized-QN
   design-attribute form). The amendment is recorded elsewhere; the design of record should not
   understate its own ladder.
3. **Add a wired-path halt test.** The profile-BLOCK halt and the blocked-owner error are tested
   only against `lower_constraints` directly. A static trace confirms `build_pipeline_context`
   does not wrap the P1 call in `try/except`, so the halt propagates — but there is no committed
   end-to-end test asserting a blocked assert halts `build_pipeline_context` with the flag on.

**Not checked:**
- **No live execution at all** — no test, mypy, ruff, or corpus run was possible this session
  (sandbox denies all interpreter invocation). Every "test passes" claim here is static reading
  of the test body against the implementation, not an observed green run.
- **The corpus byte-identity gate was not run.** Inertness is argued structurally (flag-off →
  empty concrete list → P2/P3 no-op); the empty-diff regenerate itself is unverified this session.
- **The 22 measured live/snapshot divergences with the flag ON** (the Item 8 rationale) were not
  re-measured — taken from the plan/pipeline_builder comment as recorded fact.
- **`fusion_tea`/`plant_values` `gain` gap** — accepted as an out-of-scope Item 8 handoff on the
  strength of the plan's live trace; not independently reproduced (execution blocked).
- **Snapshot round-trip, module emission, fingerprinting** — out of scope (Items 7/8/9), not
  examined.
