# Design Review: Multi-Entry Candidate Bridge (Lifecycle Item 9)

**Design:** `.project/active/constraint-lifecycle-multi-entry/design.md`
**Spec:** `.project/active/constraint-lifecycle-multi-entry/spec.md`
**Review File:** `.project/active/constraint-lifecycle-multi-entry/design-review.md`
**Date:** 2026-07-20
**Verified against:** codegen `589c8c4`, teax `0a49b89`(+), fusion-tea `8eb010f4` (item8 branch)

---

## Fundamental Assessment

**Sound.** The core move is right and well-evidenced: the evaluate seam is already
multi-channel, so the fix is to stop the *bridge* from collapsing to one channel, not to
re-architect the evaluator. The design deletes the stale fusion wrapper rather than shimming
around it, builds every channel from `entry_models` (the executable truth the evaluator
validates against), and keeps the two "single-entry" assumptions properly separate (one
channel = target; one entry *module* = correct invariant, preserved). Partition-by-model-field
ownership with a fail-closed ambiguity guard is a clean, honest choice.

I am **not** recommending rework. But two of the design's load-bearing claims are wrong as
written, and one consumer is missed. Both errors converge on the same seam — the runner's
failure switch — and both are fixable with localized, stated revisions. Verdict:
**Approve-with-revisions.**

The rest of this doc is the evidence. The two that matter are R1 (the classified-failure
routing gap) and R2 (A1's rationale is false; the baseline guarantee must be scoped).

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every success criterion has a design element, and the provenance is carried faithfully — the
`[INFERRED]` catalog-default source from the spec's Open Questions is correctly *not* treated
as settled (D1 picks model defaults over the catalog and records the rejected alternative as a
decision note, not a prohibition). Good capture fidelity.

The concern is the **"Validation before evaluation"** criterion (spec.md:100-102) and its
`[NEED]` (spec.md:147-151). The design's mechanism for it (D4) does not actually route the
classified failure — see R1. The spec's own words name the gap precisely ("runs at
`runner.py:94` *outside* the runner's failure switch"), and the design quotes that same fact,
then claims a fix that doesn't address it. So the criterion is *targeted* but not *met* by the
design as written.

### 2. Pattern Consistency
**Assessment:** Pass

Reuses the existing taxonomy (`EvaluationFailed` / `EvaluationPhase.ENTRY_VALIDATION`,
confirmed at `evaluation/failure.py:13-46`) instead of minting a new failure type — matches
how `entry_source.py:47-52` already raises. Fixture convention (committed `package_live/` +
`generate_fixture.py`) follows `tests/evaluation/fixtures/f1_arithmetic/`. No new pattern
invented where an existing one fits.

### 3. Abstraction Quality
**Assessment:** Pass

`CandidateBridge(entry_models)` is the right level: it holds exactly the channel→model map and
a field→owner index, nothing more. No wrapper, no new `ModelContractData` field, no catalog
reader. Each abstraction earns its place. `_index_fields` is the only new helper and it does
one thing (build the owner index, fail closed on collision).

### 4. Duplication Avoidance
**Assessment:** Concerns

The design's intent is strong deletion (D3 removes the scalar `entry_channel`/`entry_model`
across config + definition; D6 deletes the wrapper). But the deletion inventory (§6) misses a
live consumer of the *config-level* scalars it deletes — `prove_catalog_seam.py` (R3). Left
unaddressed, that file breaks when D3 removes `StudyConfig.entry_channel`/`entry_model`.

### 5. Data Structure Clarity
**Assessment:** Pass

`entry_models: Mapping[str, type[BaseModel]]` and `_owner: dict[str, str]` are explicit and
typed. The zero/one/many table (§4) makes the data flow legible at a glance. No untyped dicts
smuggling channel knowledge.

### 6. Route Safety
**Assessment:** Concerns

The fail-closed branches (unknown field → `ENTRY_VALIDATION`; ambiguous field → construction-
time raise) are correctly explicit and safe *in the bridge*. The unsafe route is the escape
path: a bridge-raised `EvaluationFailed` (or a `Model()` `ValidationError` on a defaultless
baseline) exits at `runner.py:94`, which sits outside the `try` at `:95` — so it propagates
uncaught rather than being recorded as a `StudyBridgeDefect`. A classified exception that
crashes the runner instead of committing a failure record is a route-safety defect (R1).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

Decisions are genuine and each names its rejected alternative (D1 vs catalog defaults, D2 vs
`param_group`). The assumptions section is honest about being pinned-to-a-phase where cheap
verification wasn't done.

But **A1 is stated as a bet that is actually false**, and the design leans on its *rationale*
rather than its *fallback*. A1 says the baseline "rests on ADR-001: every entry-point kind
carries a value, so codegen always emits a Pydantic default." Codegen does **not** guarantee
this (R2, verified). The design's saving grace is the fallback clause ("if a field ever lacks
one, `Model()` raises and the bridge surfaces it as fail-closed") — but that clause depends on
the very routing the design gets wrong (R1), and the framing buries the true state: defaultless
required entry fields are an *intended, documented* codegen state, not a rare edge. The bet
should be inverted — "codegen may emit defaultless required fields; the bridge fails closed
when an unselected field has no default" — and the D1/D5 baseline guarantee scoped accordingly.

Hidden bet surfaced: the design bets that **changing the exception *type* the bridge raises is
sufficient to classify the failure.** It is not — the call site, not the exception type, is
what's outside the switch (R1). This unstated belief is the most expensive one in the design.

### 8. Reader Comprehension
**Assessment:** Pass

The "one picture" (§2) and the zero/one/many table give a reader the model fast. The
frame-first structure (structural fact → what changes → decisions) reads well. Terms are
anchored to file:line. No comprehension-blocking jargon.

---

## Issues by Severity

### Critical
*(none — no foundation-breaking issue; the approach is sound)*

### Major

- **R1 — The classified-failure routing is not actually closed; the fix needs an unstated
  runner change.** [Dimensions 1, 6, 7] D4 says "raising `EvaluationFailed` from the bridge
  routes it through the existing switch to `StudyBridgeDefect`." Verified false: `bridge.build`
  is called at `runner.py:94`, and the `try/except EvaluationFailed` opens at `runner.py:95` —
  the call is *outside* it. Changing the bridge to raise `EvaluationFailed` (or letting a
  `Model()` `ValidationError` escape) still propagates uncaught, because the type of the
  exception is irrelevant when the *call site* is outside the catch. Nothing upstream catches
  it either (`_evaluate_candidate` at `runner.py:74-83` catches only `RetryableStoreError`).
  **Fix:** the design must explicitly relocate the `bridge.build` call inside the failure
  switch (move `:94` into the `try`, or wrap it in its own `try/except EvaluationFailed →
  _commit_execution_failure`), and add that `runner.py` change to §6 and the Phase-3/Phase-5
  plan. As written, an implementer who follows D4 literally (change only the bridge) does not
  close the `[NEED]` gap.

- **R2 — A1's rationale is false: codegen does not guarantee a default on every entry field.**
  [Dimensions 1, 7] Verified in codegen `589c8c4`: the schema template has an explicit
  defaultless branch — `templates/parameter_group_schema.py.jinja2:9-14` emits
  `name: type = Field(description=...)` (a **required** field, no default) whenever
  `field.default is None`. And `default_value` can be `None` in all three ADR-001
  classifications (`resolution/graph_builder.py:534-591`): DESIGN_ATTRIBUTE on a `None`/parse-
  fail (`:551-552`), LIBRARY_DEFAULT on an absent or non-numeric/expression default
  (`_get_library_default`, `:673-679`), USAGE_LITERAL on no-source/parse-fail (`:578-579`). The
  codebase treats this as *intended*: "the schema still declares them required, so add them
  before pipeline execution" (`generation/entry_point.py:117-120`, and `:270-275`;
  `resolution/models.py:300`). Consequence: for a package with a defaultless entry field, a
  candidate that does not select that field makes `Model()` raise — so D1's "a channel's
  complete baseline is `ModelClass()`" and the D5 guarantee ("`supplied ⊇ expected` by
  construction") hold **only for packages whose every entry field resolved to a numeric
  default** — true for IFE (27/27 verified in `generated/schemas/`), not universal. **Fix:**
  correct A1's rationale (it's fail-closed-on-absence, not always-present), and scope the
  D1/D5 baseline guarantee to numeric-default packages. Note the fail-closed only becomes a
  *recorded* failure once R1 is fixed; until then a defaultless baseline crashes the runner.

- **R3 — Missed consumer of the deleted config scalars: `prove_catalog_seam.py`.**
  [Dimension 4] D3 deletes `StudyConfig.entry_channel`/`entry_model` (`config.py:50-51`), but
  `fusion-tea/exploration/ife_e2e/study/prove_catalog_seam.py` is a **live, separate** consumer
  of that exact idiom — it defines its own `ENTRY_CHANNEL` (`:47`) and passes
  `entry_channel=`/`entry_model=prepared.package.IfePlantParams` (`:100-101`). It is *not* a
  `MultiChannelEvaluator` user (it fills the three channels directly), so §6 doesn't catch it —
  but it breaks the moment D3 removes those config fields. **Fix:** add it to the migration
  inventory (rewire to the flat namespace / `prepared.entry_models`, like the other consumers),
  or the D3 deletion strands a working file.

### Minor

- **R4 — Stale doc/reference dangles after deletion.** Not code consumers, but they reference
  deleted names: `prove_catalog_seam.py:11` and `findings.md:82` mention
  `MultiChannelEvaluator`; `run_viability_study.py:10` (docstring) and `findings.md:79`
  reference the removed `ife_hif.yaml`. Sweep them in Phase 4/5 so the deletion is clean. (The
  `generated_bridged/pipelines/ife_hif.yaml` copy belongs to a different path and is out of
  scope — leave it.)

- **R5 — D3 no-migration claim rests on the Item-8 store ruling, unverified here.** The logic
  is sound in isolation: changing the fingerprint basis (config.py:63-64 → `entry_models`
  identity) creates a *new* store lineage, which is the opposite of a silent rebind — a changed
  key can't silently reinterpret old runs. But the design should confirm no store-*read* path
  keys off the old `entry_channel`/`entry_model` fingerprint (archival invariant covers old
  lineage). Cheap to check in Phase 3; call it out.

### Passed cleanly (priority items confirmed sound)

- **A2 global-uniqueness guard (priority 2):** The design *adds* it (`_index_fields` raising on
  a two-channel collision, §4/A2) rather than assuming an existing one — fail-closed, named,
  Phase-2 test planned. Correct. Entry-model field names are globally-unique PQNs for real
  packages (verified for IFE), so the >1-owner branch is a genuine guard, not a hot path.
- **A3 / Phase 0 zero-channel routing (priority 5):** Sound. The design generates the fixture
  through the *real* CLI and inspects the pipeline for exactly one `EntryPoint`; if codegen
  emits none, it routes a finding to codegen's owner rather than shimming TEAx. That's the right
  discipline — the `pipeline_validator.py:83-87` one-module gate and
  `entry_source.from_spec`'s bare `next(...)` (`:30`, raises `StopIteration`) are both real and
  correctly identified as the reasons the fixture must be verified, not assumed.
- **D4 taxonomy members (priority 4, the enum half):** `EvaluationPhase.ENTRY_VALIDATION` and
  `EvaluationFailed(EvaluationFailure(phase=..., cause=...))` exist exactly as §4 uses them
  (`evaluation/failure.py:13-46`). Only the *routing* is broken (R1), not the taxonomy.
- **Evaluate seam unchanged:** `entry_models` (`evaluator.py:119-123`),
  `evaluate(Mapping[...])` (`:125`), `MappingEntrySource.validate` missing/extra/wrong-typed
  (`entry_source.py:42-68`) all confirmed — the design correctly leaves them untouched.
- **MultiChannelEvaluator code deletion (priority 6):** Complete for *code* consumers — exactly
  the two files the design names (`run_viability_study.py`, `bench_prepare_once.py`); no hidden
  importer or subclass. `ife_hif.yaml` is gone from `generated/`; `pipeline.yaml` replacement
  exists. Only R3 (a *different* deletion — the config scalars) and R4 (docs) remain.

---

## Recommendations

1. **Fix R1 first — it's the crux.** Make the runner change explicit: relocate `bridge.build`
   inside the failure switch (or wrap it) so a bridge-raised `EvaluationFailed` reaches
   `_commit_execution_failure`. Add `runner.py` to §6 and the phased plan. Without this, the
   headline `[NEED]` ("classified failure before evaluation") is not delivered, and R2's
   fail-closed baseline path crashes instead of recording.
2. **Rewrite A1 (R2)** to state the true codegen behavior — defaultless required entry fields
   are an intended, documented state — and scope the D1/D5 baseline guarantee to numeric-default
   packages. Keep the fail-closed fallback; that instinct is right. Consider a Phase-2 test with
   a defaultless-field package asserting a *recorded classified* failure (which also exercises
   the R1 fix).
3. **Add `prove_catalog_seam.py` to the migration inventory (R3)** so the D3 config-scalar
   deletion doesn't strand it.
4. Sweep the stale doc references (R4) and confirm the store-read path in Phase 3 (R5).

---

## Resolutions

*(To be filled in by the owner. Non-interactive review — no resolutions recorded yet.)*

---

**Overall:** Approve-with-revisions
**Next Steps:** Record resolutions above, then return to the design-agent session and point it
at this review to incorporate R1–R3 (and R4–R5). The reviewer does not edit the design. R1 and
R2 are the load-bearing revisions; R3 prevents a broken deletion. Max two rounds — a second
pass should only need to confirm the runner-relocation and the A1/D5 scoping landed.
