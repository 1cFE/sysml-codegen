# Audit: Exact-Identity Completion (ELABORATE-FIRST Item 6) — Phases 3–4

**Verdict:** Needs Work (narrow — two findings to resolve before Phase 5 certification)
**Audited:** 2026-08-09
**Branch:** `source-identity-epic`
**Commit:** codegen `b9c22c0` + uncommitted phases 1–4; agentic-mbse `2e67953` + uncommitted

**Scope:** Plan Phases 3–4 only. Phases 1–2 were audited in `audit.md` (remediated; audit-F1/F2/F3
fixes verified incidentally here). Phase 5 is unstarted.

---

## The Point

SysIDE has already resolved which semantic declaration a reference denotes. Codegen must carry that
exact identity through executable payload, concrete occurrence context, validated graph, and public
projection — a name, QN, rendered path, or iteration order may describe an element after resolution,
never select it or reconstruct its relationships. Phases 3–4 close the last two structural gaps
before the guard-and-certify phase: SysIDE's native `Usage.usages` becomes the sole authority for
effective child declarations (codegen keeps only finite concrete expansion), and the validated graph
gains the structured occurrences and typed IR that make projection mechanical and one-way. The
shipped legacy route and snapshot v5 stay byte-identical; Item 7 owns the authority switch.

## Summary

Phases 3–4 substantively deliver what they claim, and every recorded evidence count reproduced live
in this audit. Child declarations genuinely come from SysIDE's native view with fail-closed winner
selection; the global owner/type-closure reconstruction and `alternatives[0]` fallbacks are deleted;
the graph carries validated occurrence records, typed IR, and closed eligibility/compilability; the
internal codec is a fingerprinted v2 that rejects malformed state; projection orders from typed
producer edges and renders ownership from occurrence records. audit-F4 (deferred here from the
Phases 1–2 audit) is verified fixed.

Two things keep this from certifying: projection still joins constraint formal provenance by
rendered name and fabricates the identity on a miss (audit-F5, the same fail-open class Phase 4
claimed to close), and the corpus-ledger gate is red on a Phase 3–4 regression — `return_styles`
now dies on `SI_REDEFINITION_INVALID` before its owner-ruled self-binding diagnostics can fire
(audit-F6), while both phases read complete because neither validation checklist listed that gate.

## Product Judgment

**Is this the right piece of work? Yes.** The owner inserted Item 6 precisely to remove reconstructed
occurrence inputs, name-keyed payload joins, and fail-open defaults before cutover, and Phases 3–4
remove exactly those defects on the declared surface. Nothing contradicts the owner-grade mission
invariant.

**Product-lens ledger gate: DISPOSED** (audit-F5, audit-F6, this run; audit-F4 resolved by citation
with in-code verification; all earlier blocks re-scanned — spec-F1 was resolved by owner authority,
audit-F1/F2/F3 by the remediation block; no unresolved BLOCK exists in the item ledger or the epic).
Two §4 smells fired and control the verdict:

- **Smell 4 / audit-F5 — not disposable, drives the verdict.** The constraint catalog's formal
  provenance is recovered by matching two independently rendered spellings of the same feature
  (raw `source_name` vs sanitized `param_name`), with a fabricated
  `ConstraintFormalIdentity(qualified_name=None)` on a miss. The downstream name-safety validator
  checks only `formal_identity is None`, so the fabricated identity passes it. This is projection
  re-deriving semantic association by string in the one place Phase 4's own bullet said "do not
  recover formal identity from an IR name/QN." Fix required before Phase 5.
- **Smell 6 / audit-F6 — not disposable, drives the verdict.** The Phase 3–4 green evidence is a set
  of focused selections that excludes the one gate comparing every corpus row's exact-route outcome
  to its classified record — and that gate is red on a real regression the phases introduced. The
  Phases 1–2 remediation record explicitly assigned classifying this signal to "the in-flight
  Phase 3–4 work before Phase 5 certification"; it was instead deferred forward.
- Smell 3 was checked and NOT escalated: the `if not self.diagnostics` totality relaxation in
  `_validate_consumer` survives (`graph.py:388`), but `require_projectable` (`graph.py:631-635`)
  rejects any diagnostics-carrying graph before projection, so the relaxed path cannot reach
  generation.

## Findings

### Plan completion

Phases 3–4 checkboxes are implemented and their recorded evidence reproduces, with two bullets not
delivered as written:

- **Phase 4 "Projection IR" — partial (audit-F5).** The bullet requires mapping each
  feature-reference occurrence to its exact typed port and forbids recovering formal identity from
  an IR name/QN. IR traversal and input identity are typed, but the formal-provenance join in
  `_build_constraint_modules` is by rendered-name dict lookup with a fabricated fallback
  (`project.py:650-683`, `754-767`). See Code integrity.
- **Corpus classification obligation — not done (audit-F6).** The Phases 1–2 remediation record
  (audit.md and plan Implementation Notes) assigned the live `return_styles` mismatch to the
  Phase 3–4 work. Phases 3–4 completed without classifying it, and the mechanism is a Phase 3–4
  regression, not bookkeeping. **[AGENT] 2026-08-09 causal correction:** the rejected slot is the
  unscoped `StyleD::y` return attribute, whose root is the library declaration
  `Performances::Evaluation::result`; it is not `BareInC::x`. Phase 3 removed the prior scope gate,
  so that unscoped declaration entered value population and then had no loaded exact root. Neither
  phase's validation checklist listed the corpus-ledger gate, which is why both read complete over
  a red one.
- All other Phase 3–4 changes-required and validation items verified genuinely complete (evidence
  below). Red-first evidence is recorded in Implementation Notes and is plausible but not
  independently re-verifiable post hoc.

Evidence reproduced live in this audit: Phase-3 focused selections 28 + 9 passed, zero license-skip
lines; Phase-4 focused selection 22 passed; broad exact-route conformance 173 passed with the one
recorded corpus-ledger failure; legacy/v5 freeze 83 passed; committed snapshot/baseline files
untouched in git status (byte freeze holds); spike probe re-run reproduces the kept 6/5/3/4/2
concrete-occurrence counts across `d38_caret`, `deep_cross_scope_probe`,
`nested_occurrence_override_probe`, `retype_model`, `spec_chain_twolevel`, with exact
parent/index/effective-usage/effective-type IDs per record; SysIDE confirmed at exactly 0.8.4;
changed-scope ruff clean; mypy at the recorded 71-error baseline with none in a changed new-route
file; `git diff --check` clean in both repositories.

### Spec conformance

- **SC3 (occurrence ownership boundary) — met; checked off.** The `elab_native_plural_scope`
  fixture combines inherited children, a retype, explicit/implied redefinition, finite multiplicity,
  and an out-of-scope shadow (PROVENANCE carries the design/spike referents). Child declarations
  come from the native `usages` view filtered to loaded-user-model composite parts, with the unique
  effective declaration chosen through exact redefinition endpoints and a fail-closed error on a
  repeated declaration (`occurrence.py:470-502`). Reversed enumeration is adversarially pinned
  (`test_native_child_order_does_not_change_occurrence_identity`). The probe re-run matches the kept
  spike findings, and R4's split (SysIDE supplies declarations, codegen expands concrete contexts)
  is visible in the occurrence records.
- **SC4 (graph structure sufficient for one-way projection) — not met (audit-F5).** Ownership,
  aliases, execution order, and entry-point classification are derived from typed structure
  (occurrence records, `ProducerRef` edges, `ValueSite`), and the adversarial display-mutation tests
  prove it for those surfaces. But constraint formal provenance — part of "expression/predicate
  inputs" — is still recovered by parsing/matching rendered names. Left unchecked.
- **SC5 (guard + plural disposition) — partial, on track.** F31 has its kept valid-model
  disposition: "supported with scoped witness," both plural branches driven by the fixture,
  model-wide fallback deleted. The full-boundary guard expansion is Phase 5.
- **SC6 (matrix/corpus green-or-named-diagnostic, zero unclassified) — currently red (audit-F6).**
- **SC1/SC2/SC7** span Phase 5 surfaces and were not closable; SC2's Phase 3–4 slice (closed
  eligibility/compilability, no codec defaults, `FeatureTyping`-derived port types) is delivered
  except for the F5 fabricated-identity path.
- **R5 (projection one-way) — met except the F5 join.** R7 (fail closed, never first match) — met on
  the occurrence/graph/codec surface; F5's fabricated identity is the one surviving fail-open. R10
  (no authority switch) — met: serializer untouched, committed snapshots and baselines
  byte-identical, CLI default route unchanged.
- **Non-goals — respected.** No `build_pipeline_context` change, no shipped snapshot change (codec
  v2 is internal evidence only), no recapture, no legacy deletion, no public renaming (collisions
  still block via `SI_RENDERING_COLLISION`; verified the audit-F1 fix renders the public source key
  from display metadata at `project.py:148`).

### Design conformance

Implementation follows the design authority map:

- **D3 (native declaration authority)** — followed, with the deviation honestly recorded in the
  plan: `Usage.usages` returns base and redefining declarations for one slot, so the walker selects
  the sole declaration that redefines every other native candidate through the exact endpoint graph.
  That is winner selection over SysIDE's own view, not owner/name/type-closure reconstruction.
- **D4/D9 (structured occurrences, typed IR, graph as payload)** — followed. `OccurrenceRecord`
  with exact parent/slot/effective usage/types, `InstanceGraph.occurrences` validated for totality
  and parent existence, typed `ExpressionIR` in memory, canonical fingerprinted `instance-graph/v2`
  that rejects v1/unknown tags and malformed state (strict `Eligibility` decode, no ADMIT default).
- **D8 (projection owns strings, complete seam)** — followed for ownership, aliases, topological
  order (`ProducerRef`-derived with the explicit aggregator dependency, `project.py:885-966`), and
  entry-point classification (`ValueSite` map total over the enum, `project.py:332-337`); violated
  at the formal-provenance join (audit-F5). Remaining `project.py` string splits render public
  module-type spellings only (`project.py:711-723`).
- **D10 (fixed diagnostic catalog)** — followed; malformed-codec and validation failures land on
  named `SI_*` codes, each pinned by a test.

### Code integrity

- **audit-F5** — `project.py:650-683` + `754-767`: `_predicate_identities` keys constraint formal
  identities by the IR leaf's raw `source_name`; `_build_constraint_modules` looks up by the
  sanitized `param_name` and fabricates `ConstraintFormalIdentity(raw_name=param_name,
  qualified_name=None)` on a miss. Any formal whose authored name is not already a Python
  identifier (e.g. `'max power'`) misses the join; the name-safety guard's `is None` check passes
  the fabricated identity, and null-QN identity keys let distinct same-raw-named formals collapse
  in `validate_scope_bindings`. The frozen legacy route builds this field structurally
  (`constraint_lowering.py:850-857`), so the exact route is currently the weaker one. What should
  change: join the IR feature reference to its exact `ConsumerPortId`/target declaration, and make
  an unjoinable formal a named D10 diagnostic instead of a synthesized identity.
- **audit-F6** — `elaborate.py:515-537`: `_build_value_nodes` admitted an unscoped output attribute
  from `StyleD`, then required its library-rooted slot to have one root in the loaded exact
  `AttributeUsage` population. That produced `SI_REDEFINITION_INVALID` before the downstream
  `SI_SELF_BINDING` diagnostics the archived ledger records. **[AGENT] 2026-08-09 causal
  correction:** the rejected root is `Performances::Evaluation::result`, not the supported bare-`in`
  `BareInC::x` formal. What should change: restore the scoped-value admission boundary so the
  supported model reaches binding diagnostics; the corpus gate must be green before Phase 5
  certifies.
- **audit-F4 — verified fixed.** The four fail-open `python_type="float"` defaults on
  calculation/constraint consumer ports are replaced with extracted types or
  `_feature_python_type`, which resolves exactly one `FeatureTyping` off the exact declaration and
  raises `SI_EDGE_DANGLING` otherwise; pinned by
  `test_constraint_port_type_comes_from_exact_feature_typing`.
- Residual notes, not Phase 3–4 defects: the FORMULA computed-attribute *output* metadata still
  writes a fixed `python_type="float"` (`elaborate.py:664-671`) — pre-existing Item-5 behavior
  (base `elaborate.py:497`), untouched by this diff, worth a look when F5 is fixed;
  `_constraint_module_type` re-splits a rendered instance path to mint the module-type namespace
  (`project.py:711-723`) — rendering from rendering with no collision guard on the result, noted
  under smell 4.

---

## Certification

**Verdict: Needs Work (narrow).** The product-lens gate is not BLOCKED, phases 3–4 evidence
reproduces completely, and the phase substance is sound — but smells 4 and 6 fired via audit-F5 and
audit-F6 and are not disposable within this judgment:

1. **audit-F5 (fix):** join constraint formal provenance through the exact typed port/target
   declaration; an unjoinable formal is a named D10 diagnostic, never a fabricated identity.
2. **audit-F6 (fix or classify):** restore the scoped-value admission boundary so `return_styles`
   reproduces its ledger outcome, or reclassify the row with owner-visible evidence. The
   corpus-ledger gate must be green before Phase 5 certification.

What was checked and marked: plan Phase 3–4 progress boxes stand as implemented (left checked; this
audit is the verification record, and the findings are localized defects at the edges of otherwise
sound phases). Spec SC3 checked off as verified met. No other spec criteria and no epic checkboxes
were changed. The product-lens ledger gained the audit block above (gate DISPOSED; audit-F4
resolved by citation).

**Not checked:** Phase 5 entirely (F30 guard expansion, guard falsifiers, 29-cell matrix re-run,
strengthened runtime-cell/public-mutation evidence, scale smoke, full repository suites — the
matrix and full suites were NOT re-run in this audit; broad conformance was run at 173 passed / 1
recorded failure). Red-first evidence taken from Implementation Notes, not independently
reproduced. Agentic-mbse full suite (unchanged since the Phases 1–2 audit reproduced it; its
working tree still carries only the Phase-2 coordinated set). Generated-output parity of the exact
route against every Item-5 row beyond the fixtures the focused selections cover. Performance.

---

## Implementation response — 2026-08-09

**[AGENT] Both findings are implemented; independent re-audit remains pending.**

- **audit-F5 accepted and fixed.** Constraint ports now carry `FormalProvenance` from their exact
  declaration ID. Graph validation and the v2 decoder reject missing, mismatched, or incomplete
  provenance. Projection constructs `ConstraintFormalIdentity` only from that port payload; the
  rendered-name join and fabricated null-QN fallback are deleted
  (`graph.py:101-116,320-360`; `elaborate.py:1100-1132`; `project.py:382-439`). A quoted
  `'max power'` fixture proves that changing IR display spelling cannot redirect the identity, and a
  re-fingerprinted malformed codec payload is rejected.
- **audit-F6 outcome accepted; proposed cause rejected and corrected above.** The bare-`in`
  `ReferenceUsage` was not the rejected slot. Restoring the pre-Phase-3 rule that only attributes
  with real scopes enter value population removes the unscoped `StyleD::y` slot while preserving
  the supported bare-`in` path (`elaborate.py:515-523`). `return_styles` again produces exactly
  three `SI_SELF_BINDING` diagnostics (`test_elaboration_phase5_remediation.py:52-57`).
- **Validation:** Phase-3 selection 38 passed; Phase-4 selection 24 passed; corpus-ledger selection
  3 passed; broad exact-route conformance 177 passed; legacy/v5 freeze 83 passed; the corpus runner
  discovered and classified all 37 fixtures. Changed-file ruff is clean. Mypy remains at the
  recorded 71-error baseline with no error in the changed elaboration/projection/codec files.
  `git diff --check` is clean in both repositories, and committed snapshot/generated-baseline
  paths remain unchanged.

This response records remediation evidence. It does not replace the independent audit verdict or
certify Phase 5.
