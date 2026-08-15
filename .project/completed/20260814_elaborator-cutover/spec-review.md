# Spec Review: Atomic Cutover — Switch, Delete, Snapshot, Recapture

**Spec:** `.project/active/elaborator-cutover/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/elaborator-cutover/spec-review.md`
**Date:** 2026-08-10

---

## Reality Check

**Concerns, but not a Stage-0 failure.** The spec is about the right work item. Its core direction
matches the epic: make the resolved instance graph the sole shipped front end, replace snapshot v5,
delete the string-resolution authority, and recapture the corpus in one cutover unit. Design would
still be misled by several contract defects, but they are repairable without reshaping Item 7.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim [P0]:** The spec collapses distinct authority grades into a blanket
`[INHERITED]` grade and then calls the resulting direction “settled.” That violates the required
absorb mapping. The epic distinguishes owner-originated rulings (`epic_elaborate_first_architecture.md:61-72`)
from the agent-authored, owner-ratified strategy and gates (`:113-137`). The spec instead marks the
one-authority gate, atomic landing, envelope, deletion, F19/F26 proofs, and operational gates alike
as `[INHERITED]` (`spec.md:35-94`) and says owner-ratified artifacts “settle the problem and
direction” (`:14-16`). Owner-originated outcomes must become `[NEED]`; agent-authored recommendations,
even when ratified, remain `[INFERRED]`; genuinely inherited items must retain their source and
grade. Regrade each decision-carrying item and cite the exact upstream ruling. Until then a reviewer
cannot tell which parts may be challenged and which came from the owner.

**L1-2 · Direct claim [P0]:** The F19 criterion drops a binding migration decision that controls
both scope and corpus cardinality. The governing contract records the customer migration as
bare-renamed **in place** (`constraint-execution-authoritative-lifecycle-contract.md:443-458,
472-476`) and assigns the exact customer targets to C25 and C2 (`:1201-1224`, `:932-947`). The draft
reduces this to “a maintained, valid correction” (`spec.md:54-59`). Today the sole inherited
`fusion_tea` corpus row still fails with 15 `SI_SELF_BINDING` diagnostics
(`diff-ledger.md:31`), and the fixture contains those self-bindings
(`tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml:114-168` and
`designs/hif_ife/hif_plant.sysml:215`). As written, an implementation could add a parallel corrected
fixture, fix only one binding, or expand the 37-path corpus. Restore the in-place migration force,
the C25/C2 topology, and the exact maintained referent without importing Item 8's external package
regeneration.

**L1-3 · Direct claim [P0]:** R7 invents a snapshot behavior that contradicts the inherited
29-cell authority. The contract derives route behavior from outcome: `AUTHORING_DIAGNOSTIC` means
capture refuses, `LOAD_ERROR` has no snapshot route, and only `RUNTIME_SOURCE` requires full
live/in-place/relocated parity (`constraint-execution-authoritative-lifecycle-contract.md:760-768`).
The spec first says the 29 cells pass at live and relocated-snapshot boundaries (`spec.md:49-53`),
then allows a diagnostic-bearing envelope as review evidence (`:165-171`). A persisted envelope for
an authoring-diagnostic cell is not an allowed alternative to capture refusal. Rewrite acceptance
by contract outcome. Remove the diagnostic-envelope option unless an upstream owner-grade amendment
explicitly changes the contract.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim [P0]:** Atomicity, “exactly once,” and the owner recapture checkpoint are not
yet one coherent completion rule. The epic requires one atomic cutover/format-bump/recapture unit
and separately requires owner review of the Item-7 recapture (`epic_elaborate_first_architecture.md:124-137`).
The spec repeats atomic landing (`spec.md:91-94`) and says the checkpoint is pending after a
37-path capture protocol (`:82-87`), but it never says that recorded owner disposition gates the
final landable unit or what “exactly once” counts when review rejects a batch. Design could either
land before owner review or violate the literal once-only rule while correcting review findings.
Define the accepted recapture batch, make owner disposition a prerequisite to completion/merge,
and keep exploratory or rejected evidence from becoming a second committed corpus authority.

**L2-2 · Rewrite request [P1]:** The F19 proof and real-TEAx smoke can silently consume Item 8.
Item 7 explicitly owes a customer-scale cutover proof and one real TEAx smoke, but Item 8 owns
committed Fusion Tea/Stellarator package regeneration, study reruns, certification repair, modeling
guidance, and architecture documentation (`epic_elaborate_first_architecture.md:472-501`). The
draft's phrases “recorded Fusion Tea customer composition” and “customer-scale model”
(`spec.md:54-75`) do not say which in-repo model may change, whether generated output is temporary,
or whether TEAx is evidence-only. Tighten the boundary so Item 7 can correct the maintained codegen
fixture and generate/seal/execute a temporary package through stock APIs, while any committed
downstream package, study, guidance, or TEAx product change remains Item 8.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim [P0]:** R3 does not provide a complete public API disposition, so “API
closure” is not auditable. The current surfaces are materially different: live
`build_pipeline_context(model_paths, targets, include_all, design_path_filter,
lower_constraints_enabled) -> PipelineContext`
(`src/sysml_codegen/orchestration/pipeline_builder.py:833-839`), public capture writes a path and
accepts only model paths/output/filter (`snapshot/capture.py:20-24`), snapshot load returns a
`PipelineContext` (`orchestration/snapshot_context.py:26-34`), and the internal exact wrapper returns
only `ComputationGraph` (`orchestration/elaborated_pipeline.py:22-47`). `PipelineContext` is also
re-exported through orchestration, generation, and the backward-compatibility initialization module
(`orchestration/__init__.py:10-33`, `generation/__init__.py:23-27`,
`generation/initialization.py:1-17`). The draft names only “target/filter” examples and three possible
return shapes (`spec.md:100-107`). Require a named disposition for every public live, capture,
snapshot-load, CLI, return-type, parameter, exception, and re-export surface. The design may choose
the shape, but the spec must make omission impossible.

**L3-2 · Direct claim [P0]:** The deletion and test-replacement criteria are too open to prove
complete closure. R4 lists responsibility classes and R6 gives example tests (`spec.md:108-164`),
but neither requires a closed file/symbol/caller census or a one-to-one replacement record. The live
tree has legacy behavior spread across public exports, CLI and capture callers, executable scripts,
snapshot rebuild, and many independently useful tests, including `test_backtracker.py`,
`test_dual_resolution.py`, `test_agg_key_forms.py`, `test_output_registry.py`,
`test_virtual_binding_rewrite.py`, `test_orchestrator.py`, the graph-builder suites, snapshot suites,
and execution/runtime routes. The 29-cell source-identity matrix does not cover every public behavior
those tests protect. Require the design/plan to produce a durable closed census mapping each
production owner, export, caller, script, and affected test responsibility to delete, migrate, or
retain-with-nonlegacy-justification; require static no-residue gates; and require every deleted
behavioral oracle to name its independent replacement. “Nearest kept test” is not sufficient
evidence.

**L3-3 · Direct claim [P1]:** Envelope integrity acceptance is underspecified. R2 requires model
identity, capture provenance, source-staleness data, schema/certifiability markers, diagnostics, and
the graph (`spec.md:95-99`), while the existing internal graph fingerprint covers only
`schema_version + graph` (`src/sysml_codegen/snapshot/instance_graph.py:83-86`). The spec properly
leaves exact nesting and fingerprint boundaries to design, but its success criterion tests only a
generic “fingerprint failure” (`spec.md:39-43`). A design could preserve graph integrity while
allowing load-bearing envelope metadata to be changed or skewed. Add outcome-level acceptance that
every load-bearing envelope field is either integrity-bound and validated before projection or
explicitly classified as non-authoritative; include tamper/skew cases for outer-envelope fields as
well as the inner graph.

**L3-4 · Direct claim [P1]:** The scale and real-TEAx criteria can be satisfied by reports that do
not prove a usable cutover. The only recorded Item-6 scale run reached the expected
`SI_SELF_BINDING` boundary on `solar_battery_model`; it did not produce a projectable graph or
execute TEAx (`elaborator-identity-completion/plan.md:815-818`). The draft asks for a pre-recorded
budget and an “observable modeled result” but names no environment, pass thresholds, maintained
model path, independent expected result, TEAx revision/discovery contract, or seal verification
oracle (`spec.md:54-59,72-75`). Preserve mechanism freedom, but make success testable: the budget
must have pass/fail thresholds and environment metadata, and the smoke must name the selected
maintained model, independently expected modeled result, real TEAx state, stock discovery/execution
surface, and emitted-seal check.

**L3-5 · Direct claim [P1]:** The repository quality gate is ambiguous and conflicts with the
recorded baselines unless “both repositories” and “Ruff pass” are defined. Item 6's certified state
is codegen plus `agentic-mbse`; its re-audit records exact test counts, changed-file Ruff success,
nonzero full Ruff/mypy baselines, and separate totals for both repositories
(`elaborator-identity-completion/audit_v3.md:287-296`). The TEAx smoke introduces a third checkout
but not necessarily a modified repository. The draft says only “both repositories” and “Ruff, mypy
against their recorded baselines” (`spec.md:76-81`). Name the two coordinated repositories, the
maintained commands, zero-new versus clean expectations, and whether TEAx is evidence-only. Fresh
post-deletion counts are correct; historical counts must remain context, as the draft already says.

### Lens 4 — Hygiene

No material hygiene-only finding. The blocking problems are contract and acceptance defects, not
formatting.

### Lens 5 — Reader Comprehension

No separate voice finding. Resolving L1-1, L1-3, L2-1, and L3-1 will also make the decision and
acceptance boundaries legible without forcing the reader to reverse-engineer shorthand grades and
route names.

---

## Engagement Summary

**Overall take:** Item 7 is correctly framed, but this draft is not safe to hand to design. Its
highest-risk defects are a provenance collapse, a contradiction with the 29-cell capture-refusal
contract, and closure criteria that cannot prove the legacy API and test authority are actually
gone.

**Here's what I need you to weigh in on:**

1. **[L1-1]** Regrade every decision by its actual upstream authority; owner-ratified agent strategy
   must not be presented as owner-settled requirements.
2. **[L1-3]** Restore the contract's outcome-specific route matrix. Authoring-diagnostic cells refuse
   capture; load-error cells have no snapshot route.
3. **[L2-1]** Make the owner recapture disposition gate the one final atomic landing and define the
   accepted meaning of “exactly once.”
4. **[L1-2, L2-2]** Pin the in-place C25/C2 Fusion Tea fixture correction while keeping committed
   downstream packages, studies, guidance, and TEAx changes in Item 8.
5. **[L3-1, L3-2]** Require closed API/deletion/test censuses and independent replacement oracles;
   category prose is not enough to certify removal.
6. **[L3-3, L3-4, L3-5]** Make envelope tamper handling, customer-scale/TEAx proof, and repository
   gates measurable against named fields, models, environments, repositories, and baselines.

---

## Resolutions

None recorded. This is a fresh non-interactive review.

---

**Verdict:** Revise
**Next Steps:** Return to the spec agent and point it at this review. Amend `spec.md`, then rerun
`my-spec-review` before technical design. The reviewer does not edit the spec.
