# Spec Review: Runtime Evaluation Contract — Exceptional Arithmetic and Predicate Naming

**Spec:** `.project/active/gap-runtime-contract/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/gap-runtime-contract/spec-review.md`
**Date:** 2026-07-18

---

## Reality Check

**Resolved.** The revised spec remains focused on GAP-CLOSE Item 1, preserves the owner ruling, and
keeps F2 agent-grade. It now defines the observable normalized failure record, preserves TEAx's
causal traceback, separates the codegen and TEAx repository boundaries, and separates the two
byte-comparison axes.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Rewrite request:** The third `[NEED]` combines the owner's “small and clean” direction
with “uses the existing execution-failure model” (`spec.md:68-71`). The owner ruling states the
policy, the small/clean constraint, and the no-partial-report consequence; the following “F1 fix
shape” selects reuse of the evaluator model (`20260718_gap-review-verification.md:45-56`). Preserve
the owner-originated outcome as `[NEED]`, but move the reuse mechanism to `[INFERRED]` or let the
existing TEAx API force a separately evidenced `[HARD]` item. Ratification by proximity does not
promote an agent mechanism to owner-grade.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** The spec requires both evaluator paths to name the failed constraint, but
it does not establish who owns the required change. Both TEAx evaluators catch the executor's
top-level exception and build `EvaluationFailure` without `module_or_channel`
(`../teax/packages/teax-simkit/simkit/evaluation/evaluator.py:112-123,185-199`), after the serial
executor has let the module exception escape without attaching its module key
(`../teax/packages/teax-simkit/simkit/core/pipeline_executor.py:181-197`). GAP-CLOSE Item 1 is
declared a sysml-codegen implementation item, while its epic risk says a TEAx-side seam may be
booked as a separate leg (`epic_gap_close.md`, Risks). Before design, the spec must state the
completion boundary: either a narrow TEAx change is part of Item 1, or codegen must provide an
exception envelope that satisfies the exact normalized contract, or the TEAx leg is an explicit
dependency and Item 1 cannot claim the end-to-end criterion alone.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** “Identifies the constraint” and “useful cause” are not observable
enough for two engineers to build the same contract (`spec.md:26-29,110-112`).
`EvaluationFailure` already exposes `module_or_channel`, `cause`, `retryable`, and
`partial_artifacts` (`../teax/packages/teax-simkit/simkit/evaluation/failure.py:26-45`), but the
spec never says whether identity must be the stable `constraint_id`, the generated module key, a
source name embedded in `cause`, or some combination. Tighten the outcome so tests can assert the
same fields and values in `PreparedEvaluator` and `FileBackedEvaluator`, including where the
original exception class and message are preserved. Leave the attachment seam to design.

**L3-2 · Rewrite request:** “It is not ... a raw traceback” is ambiguous against the existing
normalization behavior (`spec.md:29`). TEAx raises `EvaluationFailed` *from* the original exception,
so callers receive a normalized exception and record while Python deliberately retains the causal
chain (`evaluator.py:117-123,193-199`). State the observable boundary: whether the requirement is
only that the original arithmetic exception does not escape the evaluation API, or whether the
causal traceback must also be suppressed. The latter would change the current diagnostics contract
and should not happen accidentally.

**L3-3 · Rewrite request:** The byte-stability criteria mix two different comparisons without
naming their baselines (`spec.md:48-56`). “Live/snapshot ... byte-identical for the same model and
revision” is route parity. “All other generated content is byte-identical” is a pre-fix versus
post-fix diff boundary. Name those two comparison axes separately, identify the pre-fix revision or
record that must anchor the second, and say whether non-generated TEAx/runtime files are outside the
byte comparison. Otherwise a green live/snapshot parity test can appear to discharge a before/after
stability promise that it never exercised.

**L3-4 · Direct claim:** The F2 regression scope is appropriately broader than the single original
probe. The verified reachable classes are case-fold, underscore-run collapse, and quoted hyphen
(`20260718_gap-review-verification.md:21`), while production lowercases the sanitized key and emits
all definitions into one module (`src/sysml_codegen/generation/modules.py:117-153`). Keep all three
classes and the opposite-predicate execution proof. Do not narrow this to the original
`Foo-Bar`/`Foo_Bar` pair during rewrite or design; that would leave two verified collision classes
without RED coverage.

### Lens 4 — Hygiene

No material hygiene finding beyond the provenance and baseline rewrites above.

### Lens 5 — Reader Comprehension

No separate finding. The spec is skimmable; the blocking comprehension problem is the undefined
failure identity already covered by L3-1.

---

## Engagement Summary

**Overall take after revision:** The spec now provides a testable contract without crossing the
epic's repository boundary. The owner policy, agent-selected reuse mechanism, sysml-codegen
boundary, separately booked TEAx dependency, byte baselines, and three F2 RED classes are distinct
and explicit. No owner input remains necessary before design.

---

## Resolutions

- **L1-1 — Resolved.** The owner-grade requirement now contains only “small and clean.” Reuse of
  `EvaluationFailure` is separately tagged `[INFERRED]` and identified as an agent-selected
  mechanism constrained by the located interface.
- **L2-1 — Resolved.** The serial executor is the first seam that knows both the module key and the
  escaping exception. Item 1 remains sysml-codegen-only: generated code propagates the original
  exception unchanged. `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` is booked in `BACKLOG.md` as a separate
  P0 TEAx dependency; GAP-CLOSE F1 requires both legs.
- **L3-1 — Resolved.** Both evaluators must expose `phase=module_execution`,
  `module_or_channel=constraint_id.lower()` (the generated pipeline module key), the original
  exception class and message in `cause`, `retryable=False`, and `partial_artifacts=()`.
- **L3-2 — Resolved.** “No raw traceback” now means the original arithmetic exception is not the
  top-level API exception. `EvaluationFailed` remains explicitly chained from it, preserving
  `__cause__` and the causal traceback.
- **L3-3 — Resolved.** Route parity compares live with snapshot at one post-fix revision.
  Before/after stability compares generated artifacts against pre-fix revision
  `6db321225a5c8568db0287b67ed1d04c03079cc2`; TEAx source and tests are outside that byte gate.
- **L3-4 — Resolved.** Separate opposite-predicate RED records are required for case-fold,
  underscore-run collapse, and quoted-hyphen collisions.

---

**Verdict:** Approved after revision
**Next Steps:** Proceed to `my-design`. Treat the separately booked TEAx normalization leg as an
external dependency; Item 1 does not authorize changes in that repository.
