# Audit: Exact-Identity Completion (ELABORATE-FIRST Item 6) — Phases 1–2

**Verdict:** Needs Work (narrow — three findings to resolve before Phase 3 approval)
**Audited:** 2026-08-09
**Branch:** `source-identity-epic`
**Commit:** codegen `b9c22c0` + uncommitted phases 1–2; agentic-mbse `2e67953` + uncommitted

**Scope:** Plan Phases 1–2 only. Phases 3–5 are unstarted and were not evaluated.

## Remediation — 2026-08-09

**Status:** audit-F1, audit-F2, and audit-F3 implemented; independent re-audit pending. The verdict
below is the original audit judgment and has not been self-certified away.

- **audit-F1 fixed:** definition-typed graph nodes no longer mint a parser UUID source key.
  Projection renders the public `definition:{qualified-name}` key from the exact definition's
  display metadata. The internal `effective_definition_id` remains the semantic identity.
- **audit-F2 fixed:** shared extraction captures stable live UUID sidecars opportunistically and
  leaves them empty for null-QN or non-v5 declarations. The exact route remains fail-closed with
  `SI_ID_MISSING`; the shipped shared extraction path no longer raises the audit's bare identity
  `ValueError`.
- **audit-F3 repaired:** the ledger gate points to
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md`. Both ledger/discovery structure
  checks pass. The live comparison now runs and reports a current Phase 3–4 mismatch for
  `return_styles` (`SI_REDEFINITION_INVALID` versus archived `3× SI_SELF_BINDING`). That is live
  gate output to classify or correct before Phase 5, not the stale-path failure audited here.

Remediation evidence: two focused regressions passed; the 45-test impacted extraction/elaboration/
codec/projection selection passed; all 83 legacy/v5 freeze tests passed; changed-scope ruff and both
repository `git diff --check` gates passed. Full mypy reported 81 errors, none on the F1/F2
remediation lines; the increase from the audited 71-error baseline is in concurrent Phase-4 work.

---

## The Point

SysIDE has already resolved which semantic declaration a reference denotes. Codegen must carry that
exact identity through executable payload, concrete occurrence context, validated graph, and public
projection — a name, QN, rendered path, or iteration order may describe an element after resolution,
never select it or reconstruct its relationships. Item 5 proved exact consumer edges; Item 6 closes
the remaining places where executable data still attaches by QN/member name and where misses
silently become `UNKNOWN`, `float`, null metadata, or `ADMIT`. The shipped legacy route and snapshot
v5 stay byte-identical; Item 7 owns the authority switch.

## Summary

Phases 1–2 substantively deliver what they claim: calculation payload, compilation, and port
metadata now attach by exact declaration UUID; constraint profile decisions attach by exact usage
UUID across the repository boundary; the missing-decision→ADMIT default is gone; eligibility is a
closed enum; the neutral constraint schema and all shipped bytes are frozen. All recorded evidence
reproduced live — full suites, focused gates, freeze gates, ruff, mypy, zero license skips.

Three things keep this from certifying: the exact route now mints a SysIDE parser UUID into the
public constraint-catalog key (audit-F1, a spec non-goal violation), the shared live extractor
narrowed the frozen shipped route's accepted-model set with a bare `ValueError` (audit-F2), and the
one gate that mechanically classifies cross-route public-output diffs is dead on a stale path
(audit-F3, pre-existing but now load-bearing).

## Product Judgment

**Is this the right piece of work? Yes.** The owner inserted Item 6 precisely to remove
name-keyed payload attachment and fail-open defaults before cutover, and phases 1–2 remove exactly
those defects on the declared surface. Nothing contradicts the owner-grade mission invariant.

**Product-lens ledger gate: DISPOSED** (audit-F1 through audit-F4, this run; the earlier spec-F1
BLOCK was resolved by citation with owner authority — verified across all blocks). No unresolved
BLOCK exists. But four §4 smells fired and control the verdict:

- **Smell 4 / audit-F1 — not disposable, drives the verdict.** `_constraint_metadata` builds
  `predicate_source_key = "definition:{uuid}"` in the semantic layer; it flows unmodified through
  `project.py:942` into the TEAx-consumed catalog entry (`constraint_catalog.py:116`) and its
  fingerprint. The legacy route publishes the model-derived QN there. This changes generated public
  naming on the exact route — a spec Non-Goal — and makes public bytes hostage to a
  SysIDE-internal identity scheme. The exact identity already lives in
  `ConstraintNode.effective_definition_id`; the public string must be rendered from display
  metadata at the projection seam (design D8), not minted upstream. Fix required.
- **Smell 6 / audit-F3 — partially disposed.** The two `test_elaboration_corpus_ledger.py`
  failures are the recorded pre-change baseline (stale `active/elaborator-breadth/` path after the
  Item-5 archive move), not a selection introduced to pass. Reproduced:
  `FileNotFoundError` at collection of the ledger. Not a phases 1–2 regression — but the corpus
  diff signature includes the catalog dump (`elaboration/diff.py:76-85`), so this is the gate that
  would surface F1's corpus-wide consequences, and it must be repaired before Phase 5 cites it.
- **Smell 1 — disposed.** The paired name-keyed/ID-keyed extraction maps and the second compiler
  walk (`compile_calc_def_exact` beside `compile_calc_def`) are the item's declared transitional
  state: legacy fields are frozen for the shipped route and Item 7 deletes them. Both surfaces run
  over the same fixtures. Noted: the plan's own risk mitigation ("share the AST walk internally")
  was not implemented; acceptable only because the legacy walk is deleted at Item 7.
- **Smell 3 — disposed.** The `is_computed` early-return in `_validate_calculation_payload` exempts
  FORMULA computed attributes, which have no extracted calc-def payload by construction — a
  genuinely different case, not a same-meaning carve-out. The `if not self.diagnostics` lenient
  branch cannot reach projection: `require_projectable()` rejects diagnostic-carrying graphs.

## Findings

### Plan completion

Phases 1–2 checkboxes are implemented and their evidence reproduces, with two bullets not delivered
as written:

- **Phase 1 "Additive live identity sidecars" — partial (audit-F2).**
  `extractor.py:531-541` (`_required_declaration_id`) raises a bare `ValueError` unconditionally on
  the shared live-extraction path for any calc definition/member with a null QN or non-v5 UUID. The
  plan's risk posture says sidecars are "optional at the shared extraction dataclass but mandatory
  at the live exact-route boundary." Enforcement landed at shared extraction instead, narrowing the
  frozen shipped live route's accepted-model set (anonymous parameter members and
  namespace-collision victims previously extracted by name now fail extraction) with an unnamed
  exception. No corpus fixture trips it, and the direction is fail-closed, but it crossed the
  "new route only" scope line. Fix: enforce at the exact-elaboration boundary (which already
  raises `SI_ID_MISSING`), or keep the extraction check but surface it as an owner-visible scope
  note with a named diagnostic.
- **Phase 1 "Extraction unit pins" — partial (test gap).** The plan bullet says "prove
  anonymous/unstable executable members fail closed." Fail-closed is proven at the elaboration
  boundary (`test_missing_required_calc_payload_identity_fails_closed`, SI_ID_MISSING), but the
  extraction-time `ValueError` paths (null QN, non-v5 UUID) have no direct test. If F2 resolves by
  moving enforcement, this gap closes with it.
- All other Phase 1–2 changes-required and validation items verified genuinely complete (evidence
  below). Red-first evidence is recorded in Implementation Notes and is plausible but not
  independently re-verifiable post hoc.

Evidence reproduced live in this audit: Phase-1 focused + extraction pins 188 passed; legacy/v5
freeze 83 passed; committed snapshot/baseline files untouched in git status (byte freeze holds);
Phase-2 agentic focus 66 passed; codegen focus 19 passed; neutral golden serialization 15 passed
with fixtures untouched; codegen full suite (excluding the archived-ledger file) 3,324 passed /
47 skipped; agentic full suite 1,818 passed / 1 skipped; ruff clean on changed source; mypy 71
errors (72 pre-change baseline, none in changed route files); `git diff --check` clean both repos;
licensed collection with zero `no live syside license` skip lines.

### Spec conformance

Scoped to the phase 1–2 surface; no spec success criterion is fully closable yet (each spans
phases 3–5 work), so none were checked off.

- **SC1 (exact attachment, perturbation-proof) — delivered for calc payload and constraint
  decisions.** `test_calc_payload_attachment_is_exact_and_total` reverses member/definition order
  and lies in display name/QN while holding UUIDs fixed; attachment does not move
  (`test_elaboration_payload_identity.py:101-138`). Constraint side proven with colliding
  normalized definition names (`'Payload Guard'` vs `Payload_Guard`) and reversed enumeration
  (`:179-222`; agentic ordering test covers anonymous usages under reversed enumeration).
  Occurrence selection and projected dependencies remain (phases 3–4).
- **SC2 (no silent defaults) — delivered for the declared surface, minus audit-F4.** Missing
  definition/formal/output identity → `SI_ID_MISSING`; duplicate/conflicting → `SI_EDGE_DANGLING`;
  missing/duplicate/foreign profile decisions → `SI_EDGE_DANGLING`
  (`test_elaboration_payload_identity.py:141-176, 225-257`). The QN decision join and
  `decision is None → ADMIT` are deleted (`elaborate.py` diff). The codec now rejects absent or
  invalid eligibility (`test_elaboration_graph_roundtrip.py`). Remaining: constraint consumer
  input ports still default `python_type="float"` (`elaborate.py:1063-1072, 1117-1123, 1660-1663`)
  — audit-F4, deferred to Phase 4's "Closed executable state" bullet, which explicitly owns it.
- **R2/R3 — met on this surface.** New-route calc/constraint payload lookups are UUID-keyed
  (`_index_calculation_payloads`, `_index_constraint_associations`, `compile_calc_def_exact`).
- **R9 (cross-repo authority) — met.** Neutral facts gain no parser identity (goldens
  byte-identical, field inventory pinned); UUID access goes only through `SysideAdapter.element_id`
  (AST-enforced: `test_constraint_extraction_reads_uuid_only_through_syside_adapter`).
- **R10 (no authority switch) — met with the F2 caveat.** v5 serializer untouched (sidecars use the
  existing `snapshot_exclude` metadata, `serializer.py:271`); committed snapshots and baselines
  byte-identical; legacy `compile_calc_def` and `evaluate_profile` unchanged. The F2 extractor
  narrowing is the one shipped-route behavior change.
- **Non-goals — one violation: audit-F1** (generated public naming changed on the exact route via
  the UUID `predicate_source_key`). All other non-goals respected: no `build_pipeline_context`
  change, no snapshot version change (internal codec still `instance-graph/v1`; recorded
  deviation), no recapture, no legacy deletion.

### Design conformance

Implementation follows the design authority map with recorded deviations:

- D1 (identity = adapter element_id), D7 (typed consumer/output ports), D10 (fixed diagnostic
  catalog) — followed. Diagnostic code mapping matches the item-local choice (absent identity →
  `SI_ID_MISSING`; conflicting/dangling associations → `SI_EDGE_DANGLING`).
- Item-local choices — followed: live-only sidecars beside frozen fields; identified wrapper
  around unchanged neutral facts; typed `ExpressionIR` held in the graph and serialized only at
  the internal codec and the public catalog seam.
- Deviations recorded honestly in the plan (serializer `snapshot_exclude` reuse; internal codec
  stays v1 while carrying new fields until Phase 4's v2 bump). One deviation NOT recorded:
  the D8 boundary ("projection owns strings") is violated by minting the public
  `predicate_source_key` in `elaborate.py` — audit-F1.

### Code integrity

- **audit-F1** — `elaborate.py` `_constraint_metadata`: parser UUID minted into a public string in
  the semantic layer. What should change: keep `effective_definition_id` typed-internal; render the
  public key from definition display metadata in `project.py`.
- **audit-F2** — `extractor.py:531-541`: shared-path hard failure with a bare `ValueError`. What
  should change: move enforcement to the exact-route boundary or name the diagnostic and record
  the scope change.
- **audit-F4** — `elaborate.py:1063-1072`: constraint consumer port metadata fail-open float
  default. Deferred to Phase 4 by the plan; record kept here so it cannot silently survive.
- Minor: `_output_ports` filters `if item.element_id is not None` on a path where
  `_index_calculation_payloads` already guarantees non-null — dead defense; the totality check
  after it is the real guard. Harmless.
- Positional fact/UUID alignment in `extract_identified_constraint_facts`
  (`constraint_extraction.py:214-232`): live usages are paired to neutral facts by re-sorting with
  the same total order (`_constraint_sort_key`: line, QN, file, column) used by
  `extract_constraint_facts`, guarded by a length check. Structurally this is two sweeps kept in
  sync by a shared sort contract (smell-1-adjacent), but the neutral schema is forbidden from
  carrying parser IDs, the order is a documented total order (D-R5), and reversed-enumeration
  parity is adversarially tested. Acceptable; worth a comment pinning the pairing contract.

---

## Certification

**Verdict: Needs Work.** The product-lens gate is not BLOCKED and phases 1–2 evidence reproduces
completely, but smell 4 fired via audit-F1 and is not disposable within this judgment — plus
audit-F2 and audit-F3 need resolution before Phase 3 approval:

1. **audit-F1 (fix):** render the public constraint `predicate_source_key` at the projection seam
   from display metadata; keep the UUID internal.
2. **audit-F2 (fix or ruling):** move anonymous/non-v5 identity enforcement to the exact-route
   boundary, or keep it at extraction with a named diagnostic and an owner-visible scope note.
3. **audit-F3 (repair):** point `test_elaboration_corpus_ledger.py` at the archived ledger path
   (`.project/completed/20260809_elaborator-breadth/diff-ledger.md`) or its maintained successor;
   pre-existing, but Phase 5's corpus gate depends on it.

What was checked and marked: plan Phase 1–2 progress boxes stand as implemented (left checked;
this audit is the verification record, and the findings above are localized defects, not
unimplemented bullets). No spec success criteria were checked (none fully met — all span later
phases). No epic checkboxes were changed. audit-F4 is deferred to Phase 4 with a ledger record.

**Not checked:** Phases 3–5 entirely (occurrence authority, structured graph/one-way projection,
F30/F31, guard expansion, 29-cell matrix and 37-fixture corpus re-runs, scale smoke — the matrix
and corpus were NOT re-run in this audit; recorded counts are the pre-change baseline). Red-first
evidence taken from Implementation Notes, not independently reproducible. Generated-output parity
of the exact route against Item-5 rows (Phase 4's gate) — which is exactly where audit-F1 would
have surfaced mechanically. Performance. The `sysmlv2` upstream version gate.
