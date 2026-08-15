# Audit: Exact-Identity Completion (ELABORATE-FIRST Item 6) — Full Item

**Verdict:** Certify (re-audit addendum 2026-08-10; original 2026-08-09 verdict was Needs Work)
**Audited:** 2026-08-09; targeted re-audit 2026-08-10
**Branch:** `source-identity-epic`
**Commit:** codegen `b9c22c0` + uncommitted phases 1–5 + audit_v3 remediation; agentic-mbse
`2e67953` + uncommitted

**Scope:** The complete item — all five plan phases, all spec success criteria, and the
remediations from the two earlier audit rounds (`audit.md`, `audit_v2.md`).

---

## The Point

SysIDE has already resolved which semantic declaration a reference denotes. Codegen must carry
that exact identity through executable payload, concrete occurrence context, validated graph, and
public projection — a name, QN, rendered path, or iteration order may describe an element after
resolution, never select it or reconstruct its relationships. Item 5 proved exact consumer edges;
Item 6 closes the remaining places where executable data still attaches by QN/member name, where
occurrence declarations are reconstructed, where projection parses its own strings, and where
misses silently become `UNKNOWN`, `float`, null metadata, or `ADMIT`. The shipped legacy route and
snapshot v5 stay byte-identical; Item 7 owns the authority switch and may not begin until this
item certifies.

## Summary

The substance is nearly all there, and every recorded gate reproduced exactly in this audit: exact
UUID payload attachment, native `Usage.usages` child authority, structured occurrences and typed IR,
one-way projection with semantic collision guards, the expanded F30 guard with falsifiers, and
every-and-only public mutation across the 29-cell matrix. All six prior findings (audit-F1..F6)
verify as fixed in code.

One new fail-open blocks certification: the exact route generates an executable constraint module
for a `BLOCK`-eligibility predicate where the shipped legacy route halts generation by name
(audit-F7, reproduced live). That is the exact defect class this item was inserted to remove,
sitting on the route Item 7 would promote to sole authority. Two lower-grade findings need
dispositions: the four transitional dual mechanisms are absent from Item 7's deletion ledger
(audit-F8), and the F30 guard protects an enumerated function list, not the "full boundary" the
spec claims (audit-F9).

## Product Judgment

**Is this the right piece of work? Yes — and the blocking finding proves why it exists.** The
owner inserted Item 6 precisely so that no silent default or fail-open survives into the
authoritative route. Phases 1–5 removed every previously known instance; audit-F7 is one more of
the same species, found by the independent lens at the eligibility-enforcement seam the plan never
listed.

**Product-lens ledger gate: BLOCKED (audit-F7).** All earlier blocks re-scanned
(resolution-by-citation): spec-F1 resolved by owner authority; audit-F1/F2/F3 resolved by the
remediation block and re-verified in code this round; audit-F4/F5/F6 verified fixed in code. The
epic carries no unresolved Product-Lens block. audit-F8 and audit-F9 are DISPOSE-grade. One §4
smell fired and controls the verdict:

- **Smell: a special category exempts a case whose user-visible meaning is unchanged /
  fail-open — audit-F7, not disposable, drives the verdict.** `_build_constraint_modules` skips
  `NON_NUMERICAL` (warn) and `UNASSESSED` (silent) and lets `BLOCK` fall through to an executable
  `ModuleKind.CONSTRAINT` module with a live catalog entry (`project.py:727-747`). Nothing in
  `elaborate()`, `graph.validate()`/`require_projectable()`, or projection is the analogue of
  legacy `_raise_on_blocking` (`analysis/constraint_lowering.py:588`). Reproduced live on the
  item's own fixture: `project(elaborate(...))` over `tests/fixtures/elab_payload_identity`
  returns a `ComputationGraph` containing
  `payloadidentitydesign__system__blocked_guard__4ab986ad7a2a345f`, for the numerical-equality
  predicate `observed == limit` that the contract classifies `BLOCK` and the legacy route refuses
  to generate. The mission invariant this violates ("unsupported forms fail loudly, by name,
  before generation") is owner-grade.
- **Smell 1 (two representations manually kept synchronized) — escalated, disposed as findings
  F8/F9.** Three instances: the positional `zip` pairing of live UUIDs to neutral constraint facts
  (`agentic-mbse/constraint_extraction.py:203-222`), the paired name-keyed/ID-keyed extraction
  maps, and the F30 guard's hand-maintained function allowlist versus the real module contents.
  The dual mechanisms themselves are the item's declared transitional state — but their deletion
  is recorded nowhere (audit-F8), and the guard's allowlist is the weakest of the three (audit-F9).
- Smell 3 checked and NOT escalated, same basis as the prior round: `require_projectable` rejects
  any diagnostics-carrying graph before projection, so the `if not self.diagnostics` relaxation
  and the `is_computed` early return cannot reach generation.

## Findings

### Plan completion

All five phase checkbox sets are implemented and every recorded evidence count reproduced live in
this audit (evidence list under Certification). Two notes:

- **The plan itself never listed BLOCK enforcement at projection.** Phase 2's "closed graph state"
  and Phase 4's "closed executable state" made eligibility an explicit validated field — delivered
  — but no bullet requires the projection seam to refuse a `BLOCK` node, and
  `test_constraint_profile_attachment_is_exact_closed_and_total`
  (`test_elaboration_payload_identity.py:194`) pins `BLOCK` surviving graph construction without
  asserting any halt. audit-F7 is therefore a spec-level gap (SC2's "admits execution" clause),
  not an unimplemented plan bullet. Phase checkboxes stand.
- **Process deviation:** the spec success criteria and epic Item-6 criteria were pre-marked `[x]`
  by the implementer before this audit. Certification marking belongs to the audit. The marks are
  corrected below (SC2 and SC5 unchecked); the rest survive verification and stand.

### Spec conformance

- **SC1 (exact attachment, perturbation-proof) — verified met.** Payload-identity tests reverse
  member/definition enumeration and lie in display metadata while holding UUIDs fixed; attachment
  does not move. Projection one-way tests extend this through occurrence selection and projected
  dependencies. Left checked.
- **SC2 (no silent defaults, nothing admits execution) — NOT met (audit-F7); unchecked.** Missing,
  duplicate, mismatched, anonymous, and invalid-vocabulary payload all have named tested outcomes
  (`SI_ID_MISSING`, `SI_EDGE_DANGLING`, codec rejections — verified), but a present `BLOCK`
  decision admits execution at the projection seam. The one surviving fail-open.
- **SC3 (occurrence ownership boundary) — verified met** in the Phases 3–4 audit; the remediation
  did not touch that surface, and the Phase-3 selections (37 tests) plus the spike-probe
  occurrence counts (6/5/3/4/2) reproduced again this round. Stays checked.
- **SC4 (graph structure sufficient for one-way projection) — verified met.** audit-F5's fix
  carries formal provenance on the typed port through graph validation
  (`graph.py:320-360`), codec v2, and projection (`project.py:431-449`); the rendered-name join
  and fabricated null-QN identity are deleted (`_predicate_identities` is gone). Ownership,
  aliases, order, and entry classification derive from occurrence records, `ProducerRef` edges,
  and `ValueSite`. Stays checked.
- **SC5 (full boundary protected + F31 disposition) — partially met; unchecked (audit-F9).** F31
  has its kept valid-model disposition ("supported with scoped witness," fixture + PROVENANCE
  verified). The guard scans all six boundary files for legacy imports and has 8 verified
  falsifiers — but its selector checks cover an enumerated allowlist (5 of 35 `project.py`
  functions), so "the full semantic-resolution boundary is protected" overstates what is
  delivered. Cheap fix: deny-by-default with named exemptions, or narrow the criterion's wording.
- **SC6 (matrix/corpus green, freeze) — verified met.** 177-test broad conformance including all
  29 matrix cells; corpus runner discovers and classifies all 37 fixtures; the ledger gate (3/3)
  matches the archived Item-5 ledger, with `return_styles` back at its recorded
  `3× SI_SELF_BINDING` (audit-F6 fix reproduced live). Legacy/v5 freeze 83/83; no committed
  snapshot or baseline modified in either working tree. Stays checked.
- **SC7 (every-and-only public mutation per runtime cell) — verified met.** `RUNTIME_CELLS`
  declares complete expected edge/alias sets per cell; `_assert_complete_public_topology` rejects
  extra consumers; `_assert_only_expected_public_changes` requires the changed public-key set to
  equal exactly the declared defaults, on live and rebuilt routes, with a phantom-input falsifier.
  Stays checked.
- **R2/R3/R5/R7 — met except where F7 lands** (R7's "fail closed" holds for identity/payload/
  occurrence surfaces; the eligibility seam is the exception). **R4 — met** (spike probe re-run
  matches). **R9 — met** (adapter-only UUID access AST-enforced; neutral goldens byte-identical).
  **R10 — met** (serializer untouched, CLI/capture proven legacy-only by the guard's static
  checks, byte freeze holds).
- **Non-goals — respected.** No `build_pipeline_context` change, no shipped snapshot change (codec
  v2 internal only), no recapture, no legacy deletion, no public renaming (audit-F1 fix renders
  the definition source key from model metadata; verified).

### Design conformance

Implementation follows the design authority map. D1/D3/D4/D7/D9/D10 conformance was verified in
the earlier rounds and re-holds; the D8 violation found there (audit-F5) is fixed with three-layer
enforcement. One new deviation surfaces at the same D8 seam: projection's eligibility handling
treats `BLOCK` as renderable executable state (audit-F7) where the design's fail-closed posture
(D6/D10) and the lifecycle contract require a named pre-generation halt. The item-local choice
"existing D10 diagnostics remain the vocabulary" gives the fix its shape: a named diagnostic at
elaboration or projection, not a warning or a skip.

### Code integrity

- **audit-F7 (blocking)** — `project.py:722-747` (`_build_constraint_modules`) and the absence of
  any `BLOCK` check in `elaborate.py`/`graph.py`. What should change: a `BLOCK`-eligibility
  constraint node must halt the exact route with a named D10 diagnostic before generation (the
  natural seams: elaboration after decision attachment, or `require_projectable`). The pinned
  payload-identity test should then assert the halt, not node acceptance; a graph-construction
  assertion may keep the closed-state check via a non-strict path if one is designed.
- **audit-F8** — positional `zip` pairing of live UUID records to neutral facts
  (`agentic-mbse/constraint_extraction.py:203-222`), `compile_calc_def_exact` beside
  `compile_calc_def`, paired name/ID-keyed maps on `CalculationDefinitionData`, and
  `evaluate_identified_profile` beside the QN-keyed `_evaluate_usage`. All four are authorized
  transitional duals — but Item 7's deletion ledger predates Item 6 and names none of them. What
  should change: add the four to the epic's Item-7 deletion inventory before this item closes;
  replace the positional pairing with an identity-keyed join (or carry the audit.md round-1
  pairing-contract comment into code).
- **audit-F9** — `test_elaboration_import_boundaries.py:84-90`: allowlist scoping leaves
  association-building projection functions (`_build_output_aliases`, `_entry_source`,
  `_index_output_channels`, `_constraint_identity`, `_build_constraint_catalog`) outside the
  selector guard, and `_constraint_module_type` (`project.py:709-720`) still re-splits a rendered
  path with no collision guard on the resulting public module type (a type collision without a
  guarded name collision needs bracket/underscore aliasing between sibling paths — narrow, but
  unguarded). `_group_identity` derives group identity by filename stem. What should change:
  deny-by-default guard with named exemptions, or re-scope SC5's claim; optionally claim
  module-type spellings like the other public names.
- Minor, recorded not blocking: the FORMULA computed-attribute output metadata still writes a
  fixed `python_type="float"` (`elaborate.py:670-675`) — pre-existing certified Item-5 behavior,
  public-seam parity protects it this item; carried residue for the Item-7/8 horizon.
  `test_value_site_controls_entry_point_classification` cannot discriminate: all four `ValueSite`
  values map to `DESIGN_ATTRIBUTE` (`project.py:341-346`); keep the totality dict, rename or
  strengthen the test.

---

## Certification

**Verdict: Needs Work (narrow).** The product-lens ledger gate is BLOCKED on audit-F7, which is a
fired, unresolved fail-open against the owner-grade mission invariant; certification is forbidden
regardless of the green rubric. audit-F8 and audit-F9 are required dispositions, not blockers.

1. **audit-F7 (fix, blocking):** the exact route must halt with a named D10 diagnostic on any
   `BLOCK`-eligibility constraint before generation, matching the legacy `_raise_on_blocking`
   obligation; pin it with the fixture that reproduces today's fail-open.
2. **audit-F8 (disposition):** name the four transitional dual mechanisms in Item 7's deletion
   ledger; replace or contract-comment the positional fact/UUID pairing.
3. **audit-F9 (disposition):** deny-by-default guard or narrowed SC5 wording; consider claiming
   module-type spellings.

Evidence reproduced live in this audit: guard 13/13 (8 falsifiers verified by reading);
matrix/public/generation 34/34; broad exact-route conformance 177/177 with zero license-skip
lines; corpus-ledger gate 3/3; corpus runner 37/37 rows with `return_styles` at
`3× SI_SELF_BINDING` and `solar_battery_model` at the recorded 24 `SI_SELF_BINDING`; legacy/v5
freeze 83/83; codegen full suite 3,356 passed / 47 skipped / 18 deselected, zero license-skip
lines; agentic constraint focus 66/66 and full suite 1,818 passed / 1 skipped / 33 deselected;
ruff/mypy at the recorded baselines in both repositories (codegen 71 mypy errors in 17 legacy
files, none in a changed route file; agentic 105 in 23); `git diff --check` clean in both;
committed snapshot/v5/baseline paths untouched in both working trees. audit-F1/F2/F4/F5/F6 fixes
verified in code; audit-F3's repaired gate is the live 3/3 above.

What was marked: plan phase boxes stand (implemented; the blocking gap is spec-level). Spec SC1,
SC3, SC4, SC6, SC7 verified and stand checked; **SC2 and SC5 unchecked** (audit-F7, audit-F9). No
epic checkbox appended ✅; the epic Current block and CURRENT_WORK.md updated to "needs work."

**Not checked:** Red-first evidence (taken from Implementation Notes; not independently
reproducible post hoc). The scale smoke's time/memory figures (its diagnostic outcome was
reproduced via the corpus runner; `/usr/bin/time -v` was not re-run). Generated-output parity of
the exact route beyond the fixtures the matrix/corpus selections cover. Whether any corpus fixture
besides the item's own carries a `BLOCK`-eligibility constraint (the dual-run ledger would not
reveal F7 if none does). Performance beyond the recorded smoke. The lens's specific claim that a
QN-less definition classifies differently across the two profile entry points (the dual-authority
structure it evidences was verified; that exact divergence scenario was not exercised).

---

## Re-audit addendum — 2026-08-10 — CERTIFY

Targeted independent recheck of audit-F7, audit-F8, and audit-F9 against the remediation recorded
in `plan.md` ("audit_v3 remediation"). All three verify; the product-lens gate clears; the item
certifies.

### audit-F7 — VERIFIED FIXED (the blocking finding)

Reproduced the original falsifier live, in both modes plus the codec round-trip:

- **Strict elaboration halts.** `project(elaborate(...))` never gets past `elaborate` on
  `tests/fixtures/elab_payload_identity`: it raises `ElaborationDiagnosticError` with
  `SI_CONSTRAINT_BLOCKED: PayloadIdentityDesign__system__blocked_guard: constraint profile
  blocked execution: block_real_equality_requires_tolerance: ...` — the named diagnostic carries
  the exact consumer and the profile reason. Enforcement records the diagnostic for every `BLOCK`
  decision at node construction (`elaborate.py:900-911`); `SI_CONSTRAINT_BLOCKED` is a new D10
  code (`elaboration/diagnostics.py:24`).
- **Lenient mode retains the typed node for inspection but cannot generate.** With
  `strict=False`, the graph carries the `blocked_guard` node (eligibility `BLOCK`) plus the
  `SI_CONSTRAINT_BLOCKED` diagnostic; `project()` refuses it with `ProjectionError
  SI_CONSTRAINT_BLOCKED`.
- **The codec preserves the refusal.** `decode_instance_graph(encode_instance_graph(graph))`
  retains the diagnostic and projection refuses the rebuilt graph identically.
- **The fixture now pins the halt, not node acceptance:**
  `test_elaboration_payload_identity.py:243` (strict raise with reason match), `:251-255`
  (lenient diagnostic contents), `:261-265` (round-trip `ProjectionError`).

### audit-F8 — VERIFIED DISPOSED

- **The positional pairing is gone.** `extract_constraint_facts` now returns each neutral fact
  bound to its live producing element in one record built inside the single sweep
  (`_ExtractedConstraintUsage`, `agentic-mbse/constraint_extraction.py`);
  `extract_identified_constraint_facts` derives UUIDs through `SysideAdapter.element_id` from
  those records, rejects duplicate usage UUIDs, and keeps definitions in a UUID-keyed map. No
  second sweep, re-sort, or `zip` remains. Neutral schema and goldens unchanged (serialization/
  shape/banned-heuristics selection 23 passed; golden fixtures untouched in git).
- **The deletion ledger names the duals.** Epic Item 7 scope 2 now carries an
  `[AGENT] (audit_v3 disposition, 2026-08-10)` entry converging all four:
  `extract_identified_constraint_facts` folded into one extraction pass, exact-ID profile
  evaluation as the sole codegen path with the QN adapter's removal condition,
  `compile_calc_def_exact` promoted to the single compiler core, and the paired name-keyed maps/
  ID sidecars removed with snapshot v5.

### audit-F9 — VERIFIED FIXED

- **Deny-by-default.** The guard walks every function — module-level, class-scoped, nested,
  async — in all six boundary files; the `SELECTION_FUNCTIONS` allowlist is deleted.
- **Exemptions are narrow, named, and self-policing.** Five `(file, qualified function) →
  waived-rule` entries, each covering only wire decoding (`from_wire` × 2), upstream-enum
  vocabulary decoding (`_direction` — decodes SysIDE's direction enum repr, not a name
  selection), or public rendering (`_group_identity`, `_constraint_module_type`).
  `test_guard_exemptions_are_narrow_and_exercised` fails if a waived rule stops firing, and the
  subtraction is per-rule, so an exempted function is still caught for any other violation
  family.
- **The original falsifier is now a pinned test.**
  `test_new_boundary_function_is_guarded_by_default` proves an unlisted selector function
  (sync, async, and lambda-wrapped) trips the guard. The 8 banned-family falsifiers are
  retained. SC5 was not narrowed — it is now claimable as written.
- Open, recorded, non-blocking: the `_constraint_module_type` public-spelling collision guard
  remains a separate rendering-policy question (a type collision without a guarded name
  collision requires bracket/underscore aliasing between sibling paths); the remediation
  explicitly declined to fold it in. Carried as a policy note, not a defect.

### Gates reproduced this recheck (2026-08-10)

Guard 14/14; F7-focused selection (payload identity + phase5 remediation + roundtrip +
projection one-way) 43/43; broad exact-route conformance 178/178; matrix/public/generation +
legacy/v5 freeze 117/117; corpus runner 37/37 with `return_styles` at `3× SI_SELF_BINDING`;
agentic constraint focus 67/67 and neutral serialization/shape selection 23/23; codegen full
suite 3,358 passed / 47 skipped / 18 deselected (skip count identical to the licensed
baseline); agentic full suite 1,819 passed / 1 skipped / 33 deselected; ruff/mypy at the
recorded baselines in both repositories (codegen 71 in 17 legacy files, agentic 105 in 23);
`git diff --check` clean in both; committed snapshot/v5/baseline and golden paths untouched.

### Certification

**Verdict: Certify.** The product-lens ledger gate is CLEAR (audit-F7 resolved by this
verification; F8/F9 dispositions delivered; all earlier blocks re-scanned and resolved). Spec
SC2 and SC5 are now checked; all seven success criteria stand verified. Epic Item 6 criteria
stand and the item heading is marked certified. Item 7 (atomic cutover) is unblocked.

**Not checked (this recheck):** everything re-verified 2026-08-09 was not re-derived beyond the
gates above (SC1/SC3/SC4/SC6/SC7 evidence, occurrence/spike probes, scale-smoke timing);
red-first evidence for the remediation taken from Implementation Notes; the F8
alternating-sweep red probe (described, not re-run — the structural fix makes the failure mode
unconstructible); whether `UNASSESSED` skip semantics deserve their own halt review (they
predate this item and were accepted in prior rounds).
