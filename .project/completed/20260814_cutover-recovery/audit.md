# Audit: Item 7 Cutover Recovery

**Verdict:** Needs Work
**Audited:** 2026-08-11
**Branch:** `item7-rebuild`
**Commit:** `ceaade4`

---

## The Point

Item 7 must replace the legacy string-resolution front end with one exact instance-graph authority
without breaking the product. One modeled source occurrence must produce one runtime source for
every and only its calculation, constraint, aggregation, FORMULA, and alias consumers. The answer
must survive public live and portable snapshot routes. Unsupported self-bindings must fail before
generation and must never be reinterpreted as an outer feature. The cutover is complete only when
the old authority, adapters, wrong-oracle tests, and dual-run scaffolding are gone and the owner has
accepted the singular recapture batch.

## Summary

The recovery produced a stable pre-acceptance candidate: the public CLI uses the exact route, the
licensed codegen suite passes 3,862 tests, and 53 real-TEAx execution tests pass. Certification is
blocked because the companion validator still blesses an owner-forbidden self-binding category,
the duplicate legacy authority remains callable through a test shim, public all-route mutation
evidence is incomplete, and the owner acceptance/retirement sequence has not run.

## Product Judgment

This is the right architectural direction, but it is not yet the completed piece of work. The
product-lens ledger is **BLOCKED** by `audit-F1` and `audit-F2`; the earlier Atomic Cutover ledger
contains only CLEAR blocks, but none resolves these new findings by citation. No live epic-level
Product-Lens gate was found.

Two owner-grade contradictions control the verdict:

- The authoring validator exempts a true `in P = P` self-binding when an outer same-named feature
  exists (`../agentic-mbse-item7-rebuild/src/agentic_mbse/validation/level2_structure.py:309` and
  `:358`), and tests require the exemption (`../agentic-mbse-item7-rebuild/tests/test_validation/
  test_item12_checks.py:73`). The owner ruled that the diagnostic must never be suppressed by a
  same-named outer attribute or sibling output. Remove the exemption, align validator tests with
  exact elaboration, and correct the guidance at
  `../agentic-mbse-item7-rebuild/docs/patterns/plant-idiom.md:35`.
- The legacy builders, v5 exports, and CLI-shaped test adapter remain executable
  (`src/sysml_codegen/orchestration/__init__.py:10`, `src/sysml_codegen/snapshot/__init__.py:80`,
  `tests/helpers/legacy_route.py:34`). That conflicts with the owner-stated structural result of
  one authority with no duplicate route or shim. Execute the reviewed retirement after an
  authorized owner disposition; remove the exports, adapter, and dual-run route.

Product-drift smells 1, 3, 4, 5, and 6 fired: two synchronized authorities, a special self-binding
category, validation that depends on downstream rescue knowledge, compatibility policy retained
for an unreachable fallback, and tests that select different route answers. These remain
unresolved and independently forbid certification.

## Findings

### Plan completion

- Phases 1–3 are complete. The current tree contains the preserved recovery record, clean-base
  rebuild, vertical exact route, public authority switch, corpus checks, and customer execution
  proof (`.project/active/cutover-recovery/plan.md:158`).
- Phase 4 is partial by design. The plan explicitly postpones v5/G2/G3/G4 retirement, legacy test
  dispositions, and snapshot removal until owner acceptance (`plan.md:652`, `plan.md:765`,
  `plan.md:776`). The prepared runbook is useful evidence, not completed retirement.
- Phase 5 candidate assembly and this independent audit are complete, but owner acceptance remains
  pending (`plan.md:1011`, `plan.md:1040`). Phase 5 and the item cannot close yet.

### Spec conformance

- **SC1 Mission outcome — partial.** Exact public generation works, but the authoring validator
  contradicts the self-binding rule and all-route public mutation is incomplete.
- **SC2 FORMULA/alias extension — partial.** Calculation, constraint, and FORMULA fan-out is pinned
  at `tests/conformance/test_elaboration_public_mutation.py:26`; the full public live/relocated
  mutation obligation is not.
- **SC3 Instance-graph snapshot — verified.** Public v6 capture writes the elaborated graph and the
  offline builder loads that graph (`src/sysml_codegen/snapshot/capture.py:86`,
  `src/sysml_codegen/orchestration/exact_pipeline_context.py:250`).
- **SC4 One atomic shipped authority — not met.** Legacy builders, v5 APIs, and the test adapter
  remain callable; owner acceptance is pending.
- **SC5 Outcome-specific route acceptance — partial.** The 29-cell test uses internal
  elaborate/codec/project/render seams (`tests/conformance/test_elaboration_contract_matrix.py:670`),
  while the proposed 15/22 public recapture batch is explicitly unaccepted
  (`tests/conformance/test_v6_recapture_batch.py:37`).
- **SC6 C25/C2 customer routes — partial.** Live typed-entry mutations prove exact consumer sets
  (`tests/execution/test_fusion_tea_mutation_teax.py:141` and `:178`); kept in-place and relocated
  snapshot mutation tests are absent.
- **SC7 C19 runtime proof — partial.** The named fixture has internal structural/codec coverage
  (`tests/conformance/test_elaboration_contract_matrix.py:402`), and Fusion Tea executes the same
  80.0 behavior live and relocated (`tests/execution/test_fusion_tea_real_teax.py:248`), but the
  named fixture lacks a kept public-v6 route test.
- **SC8 C19 legacy deletion — not met.** The legacy tripwire remains at
  `tests/unit/test_supplied_values.py:414`.
- **SC9 Closed API/deletion surface — not met.** The legacy public exports and helper remain.
- **SC10 F26/dual-run removal — not met.** The comparator and dual-run test remain at
  `src/sysml_codegen/elaboration/diff.py:1` and
  `tests/conformance/test_elaboration_dual_run.py:1`.
- **SC11 Scale and real TEAx — partial.** Fresh execution passed 53/53 and the recorded Fusion Tea
  budget is within bounds, but the complete R11 verifier pair was not independently reproduced.
- **SC12 Coordinated repository gates — partial.** Both suites pass, but `ruff check src` reports
  16 codegen findings, contrary to R12's clean-production requirement.
- **SC13 Accepted recapture batch — not met.** The batch remains `PROPOSED`; owner disposition is
  pending (`tests/conformance/test_v6_recapture_batch.py:37`).

Non-goals were respected: no TEAx product changes or promotion were made, and v5 receives no new
public compatibility path.

### Design conformance

The exact graph, receipt-bound context, v6 loader, and one-way projection implement the design's
core architecture. Four load-bearing deviations remain:

- D1/D2 are unfinished: `build_pipeline_context` remains the legacy canonical name while the exact
  builders live separately (`src/sysml_codegen/orchestration/pipeline_builder.py:833`,
  `src/sysml_codegen/orchestration/exact_pipeline_context.py:239`). Retire the legacy builder and
  leave one canonical public construction surface.
- D3 requires one staged source-admission owner, but live elaboration reads caller paths while
  capture uses staged admission; a test deliberately pins the separation
  (`tests/conformance/test_snapshot_v6_routes.py:201`). Converge the routes or record an authorized
  design amendment.
- R2's designed envelope includes capture/model provenance. The implementation intentionally omits
  the `capture` object and documents a narrower guarantee (`src/sysml_codegen/snapshot/envelope.py:1`
  and `:107`). Reconcile the spec/design before certification.
- Invariants 34–35 require portable referents and generated-byte parity. Live nodes retain absolute
  checkout paths, and tests explicitly accept provenance-only byte differences
  (`src/sysml_codegen/orchestration/elaborated_pipeline.py:52`,
  `tests/conformance/test_exact_route_snapshot_generation.py:17`). Amend the contract with proper
  authority or make live provenance portable.

### Code integrity

- **Order-dependent constraint validation.** Neutral profile evaluation overwrites duplicate QNs
  by dictionary order (`../agentic-mbse-item7-rebuild/src/agentic_mbse/sysml/
  executable_profile.py:1036`), while Levels 4 and 6 still call the neutral route
  (`../agentic-mbse-item7-rebuild/src/agentic_mbse/validation/level4_constraints.py:55` and
  `level6_architecture.py:620`). Migrate both consumers to identified evaluation or refuse
  ambiguous inventories explicitly.
- **Invalid manifest fallback.** Malformed and unreadable manifests collapse to `None`, are skipped,
  and can leave Level 6 green (`../agentic-mbse-item7-rebuild/src/agentic_mbse/validation/
  level6_architecture.py:47` and `:111`); the test blesses that result at
  `../agentic-mbse-item7-rebuild/tests/test_sysml_quality_checks.py:969`. Represent invalid input
  explicitly and report a failing validation issue.
- **Duplicated snapshot pins.** `src/sysml_codegen/snapshot/envelope.py:98` repeats authority
  markers owned by `src/sysml_codegen/_upstream_pins.py:29`, and projector semantics is copied again
  at `src/sysml_codegen/orchestration/exact_pipeline_context.py:55`. Give each compatibility marker
  one owner.
- **Leaky snapshot/template protocol.** `auto_impl_context` is an untyped dictionary
  (`src/sysml_codegen/elaboration/graph.py:150`), the decoder checks only that it is a dictionary
  (`src/sysml_codegen/snapshot/instance_graph.py:587`), and generation merges arbitrary keys into
  template context (`src/sysml_codegen/generation/stencils.py:176`). Replace it with an exact typed
  record and named template inputs.
- **Silent unexpected-failure fallback.** The public write helper catches every unexpected
  exception after output mutation may have started and returns `False`
  (`src/sysml_codegen/cli/__init__.py:1133`). Catch named operational refusals, let programming
  defects reach the CLI boundary, and make partial-output cleanup explicit.
- **Manually synchronized semantics.** Unit annotation handling is duplicated between AST
  elaboration and ExpressionIR defaults (`src/sysml_codegen/elaboration/elaborate.py:723`,
  `src/sysml_codegen/extraction/modeled_defaults.py:37`). Normalize once, then apply one policy.
- **Stale contracts.** Module docstrings still describe the exact route as Item-5-only or absent
  from the CLI (`src/sysml_codegen/orchestration/elaborated_pipeline.py:1`,
  `src/sysml_codegen/orchestration/exact_pipeline_context.py:1`,
  `src/sysml_codegen/snapshot/instance_graph.py:1`). Amend them to the current authority state.

No new production TODO/FIXME/placeholder implementation was found in the Item 7 delta. New source
admission and capture broad catches translate to typed errors or clean up and re-raise.

---

## Certification

Verified the current codegen and companion heads, upstream contract/spec/design, both product-lens
ledgers, public route implementation, focused customer/cutover checks, full licensed suites, real
TEAx execution, Ruff/mypy baselines, deletion-ledger checks, and the proposed corpus batch. Marked
only the instance-graph snapshot success criterion. The epic heading and remaining plan/spec
criteria stay open. The item remains **Needs Work** until the product-lens BLOCKs are resolved by
authorized citation and the unfinished retirement/acceptance work is implemented and re-audited.

**Not checked:** Every Phase-1 archive digest was not recomputed; the 303-row ledger was not read
row by row; scale timings/RSS were not remeasured; the 301-node replacement battery was not rerun;
all architecture prose was not re-derived claim by claim; TEAx internals were treated as a pinned
dependency; promotion/release behavior was outside the recovery plan and was not exercised.
