# Epic Audit: agentic-mbse Push-Down

**Verdict:** Certify
**Audited:** 2026-07-08
**Branch:** push-down-item1-expression
**Commit:** sysml-codegen `87729fd`; agentic-mbse `66476f3`

---

## Summary

The PUSH-DOWN epic is certified. All four item audits exist with `Certify` verdicts, and the
delivered split matches the shaping intent: reusable SysML facts moved into agentic-mbse while
sysml-codegen kept transformation policy, Python rendering, aliases, design overrides, scoping,
pipeline assembly, and deferred template/virtual-binding work.

No pre_pr or PR preparation was run in this audit stage.

## Item Certification Check

- Item 1, Expression Reconstruction Push-Down: certified in
  `.project/active/expression-reconstruction-push-down/audit.md`.
- Item 2, Qualified-Name Utility Split: certified in
  `.project/active/qualified-name-utility-split/audit.md`.
- Item 3, Hierarchy Primitives and Data Models: certified in
  `.project/active/hierarchy-primitives-models/audit.md`.
- Item 4, Aggregation Decomposition and Compatibility Gates: certified in
  `.project/active/aggregation-decomposition/audit.md`.

All item-level gates required by the epic have passed or are recorded as unchanged baseline caveats.
The known tree state is unchanged: sysml-codegen only has unrelated untracked `.claude/projects/`;
agentic-mbse only has unrelated untracked command-refresh project files.

## Source-Intent Assessment

- Boundary intent: fulfilled. The research asked for a selective push-down of SysML model
  understanding, not codegen concerns. The implementation moved expression reconstruction,
  general qualified-name helpers, primitive hierarchy facts, primitive models, and neutral
  aggregation decomposition into agentic-mbse. It did not move OutputRegistry, typed codegen
  identifiers, expression compilation, computed-attribute classification, generation, analysis, or
  resolution policy.
- Design refresh intent: fulfilled. The refreshed concept-design required the updated inventory,
  branch-lockstep execution, permanent shims/re-exports, dataclass preservation, TYPE_MAP checks,
  INV-1/INV-5 coverage, and TRUTH-DEBT sequencing. The item audits verify those controls at the
  moved surfaces.
- Checking-profile intent: fulfilled by the allowed mix of implemented/existing/filed rules.
  agentic-mbse contains the shared SysML facts and validation/backlog rows for the codegen-compatible
  profile. Direct grep found no `sysml-codegen` imports under
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml` or
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation`.
- Deferral intent: fulfilled. Tier 2c template detection and virtual-binding matching remain
  deferred with the post-refactor function inventory named in the epic. `constraint_report.py`
  remains a codegen reporting artifact by recorded disposition.
- Sequencing intent: fulfilled. The TRUTH-DEBT sequencing gate is satisfied by
  `.project/completed/20260708_epic_truth_debt.md`, which records the completed epic and the ruling
  that TRUTH-DEBT had to land before PUSH-DOWN.

## Top-Level Success Criteria

- SC-A: verified. Expression reconstruction, feature-chain, chain-segment, literal helpers, and
  general qualified-name helpers are in agentic-mbse; sysml-codegen keeps compatibility shims.
- SC-B: verified. Hierarchy primitives and primitive models moved to agentic-mbse; aggregation
  decomposition moved as neutral facts; sysml-codegen keeps local adapters, codegen containers,
  Python rendering, design overrides, and policy.
- SC-C: verified. Dispatch and sanitize invariants traveled with the moved code, TYPE_MAP checks
  were rerun per item, and each move landed through the coordinated cross-repo branch process.
- SC-D: verified. The literal-node rename, BindingInfo boundary, sanitizer divergence comment, and
  feature-chain/reference-name cross-reference hazards were resolved in the relevant item scopes.
- SC-E: verified with baseline caveats. Both suites passed at every item landing point; fixture
  diffs remained empty; ruff stayed clean in required scopes; mypy remained at unchanged known
  baseline counts.
- SC-F: verified. Template detection and virtual binding stayed deferred with the updated inventory,
  and `constraint_report.py` stayed local to sysml-codegen with a recorded disposition.
- SC-G: verified. Every pushed-down helper either powers an existing validation path, maps to an
  existing profile row, or filed a named agentic-mbse backlog row with rule, fixture shape, severity,
  and rationale.

## Certification

Marked the verified top-level epic success criteria in `.project/backlog/epic_push_down.md` and
updated `.project/CURRENT_WORK.md` with the epic certification status. No item-level checkboxes were
changed during this epic audit.
