# Spec Review: Expression Reconstruction Push-Down

**Spec:** `.project/active/expression-reconstruction-push-down/spec.md`
**Contract:** `/home/reid/agentic-project-init/claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/expression-reconstruction-push-down/spec-review.md`
**Date:** 2026-07-08

---

## Reality Check

Sound. The revised spec is about PUSH-DOWN Item 1 and matches the epic objective: move reusable
reconstruction, feature-chain, chain-segment, and literal helpers into
`agentic_mbse.sysml.expression` while preserving the sysml-codegen compatibility module. The
previous gate issue is resolved: the spec now says implementation must not begin until
`truth-debt-epic` is merged to the selected sysml-codegen landing base and both agentic-mbse
prerequisites are merged. The code-facing claims checked during review still line up:
`extract_feature_chain_segments` exists but is absent from `expression_utils.__all__`,
agentic-mbse already uses `is_literal_expression` for true-static detection, and
`agentic_mbse.sysml.binding` has a duplicate private literal extractor.

---

## Audit

### Lens 1 - Faithfulness

No must-fix findings.

The prior **L1-1** is resolved. The revised spec now has `R6 - Merged Landing Base Before
Implementation [HARD]`, which states that implementation must not begin from an unmerged
truth-debt or agentic-mbse branch stack. It requires `truth-debt-epic` to be merged to the
selected sysml-codegen landing base and requires merged agentic-mbse `upstream-findings-sync`
plus merged `pipeline-truth-item4` before PUSH-DOWN Item 1 implementation starts.

### Lens 2 - Problem & Approach

No must-fix findings.

The problem framing remains faithful to the epic: shared SysML expression meaning currently
lives in sysml-codegen, which blocks agentic-mbse validation and creates duplicate logic. The
spec is conservative about mechanism except where the epic already decided the target module,
permanent shim, literal predicate rename, and checking-profile closure loop.

### Lens 3 - Pipeline Risk

No must-fix findings.

The prior **L3-1** is resolved. The merge gate is now checkable as both a HARD requirement and
the first Success Criterion. A downstream plan or audit can verify whether implementation began
only after the selected sysml-codegen base contained merged `truth-debt-epic` and agentic-mbse
contained merged `upstream-findings-sync` plus merged `pipeline-truth-item4`.

One non-blocking note for design and implementation: existing static tests inspect
`src/sysml_codegen/extraction/expression_utils.py` for implementation-body ordering. The spec
already covers the needed contract by requiring moved invariant coverage next to the shared
implementation and sysml-codegen shim tests for old imports, so this is not a spec blocker.

### Lens 4 - Hygiene

No must-fix findings.

### Lens 5 - Reader Comprehension

No must-fix findings. The revised gate is easy to find in `R6`, the Success Criteria, and the
Implementation Gate.

---

## Engagement Summary

**Overall take:** The revised spec is ready to use as the design contract. The one prior
must-fix issue was the possibility of starting implementation from an unmerged truth-debt or
agentic-mbse branch stack; the revised spec closes that loophole in a requirement, a success
criterion, and the gate prose.

**Here's what I need you to weigh in on:**

No reviewer decision is needed before design. Carry the implementation-base gate into design
and plan as a checkable pre-flight condition.

---

## Resolutions

- **[L1-1] Resolved:** The Implementation Gate now requires `truth-debt-epic` to be merged to
  the selected sysml-codegen landing base before implementation begins. The previous loophole
  allowing a stacked truth-debt base is gone.
- **[L3-1] Resolved:** The merge gate is now checkable as both `R6 - Merged Landing Base Before
  Implementation [HARD]` and the first Success Criterion. It explicitly requires merged
  truth-debt, merged agentic-mbse `upstream-findings-sync`, and merged agentic-mbse
  `pipeline-truth-item4` before implementation begins.

---

**Verdict:** Approve
**Next Steps:** Proceed to design. Carry `R6` forward as a pre-flight gate; the reviewer does
not edit the spec.
