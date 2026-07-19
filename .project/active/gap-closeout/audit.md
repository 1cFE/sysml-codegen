# Audit: GAP-CLOSE — Constraint-Expression Gap Closure

**Verdict:** Certify — local/in-scope partial wave
**Epic verdict:** Needs Work — external F1 normalization remains open
**Audited:** 2026-07-18
**Branches:** `constraint-exec-epic` in sysml-codegen and agentic-mbse
**Commits:** sysml-codegen `6db3212`; agentic-mbse `4ed2a07` plus the classified dirty worktrees

---

## Summary

All local and in-scope GAP-CLOSE work is certifiable. The second cure round closes the last two
local findings: the hash-identified rebuilt wheel contains an accurate guide, and every explicit
TEAx candidate path failure now crosses the route-aware normalization boundary. Warning-byte parity
and F2 through F9 remain intact.

The full epic is not certified. External `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` still owns evaluator
normalization and failed constraint-module identity. Pre-PR may proceed only as an explicitly
partial wave that preserves that open dependency and does not claim F1 or epic completion.

## Findings

### Blocking findings

No local or in-scope blocking findings remain.

The sole epic blocker is external F1 normalization. Generated arithmetic propagates the original
exception, but the required TEAx `EvaluationFailure` module identity is still absent. The runtime
criterion remains open at `.project/active/gap-runtime-contract/spec.md:35`, and the separately
booked dependency remains open at `.project/backlog/BACKLOG.md:41`.

### Plan completion

- Runtime Item 1 remains partial by design: the codegen propagation and F2 work are complete; the
  external evaluator leg remains open.
- Lowering Item 2, Boundary Item 3, and Profile Item 4 are complete and re-certified.
- Closeout Item 5's local implementation, documentation, metadata, hygiene, and validation phases
  are complete. Its externalizing PR actions remain for pre-PR and are not certified here.

### Spec conformance

| Finding | Result | Evidence |
|---|---|---|
| F1 exceptional arithmetic | **Open (external)** | Codegen propagation is pinned; evaluator normalization and failed module identity remain booked externally. |
| F2 predicate collision | **Certify** | Deterministic central rejection and direct-call recheck remain green at `src/sysml_codegen/generation/modules.py:100`. |
| F3 package lockstep | **Certify** | Companion build/runtime version `0.1.1`, codegen floor `agentic-mbse>=0.1.1`, and recorded old/new resolver evidence agree. |
| F4 warning before halt | **Certify** | Warning reporting runs before BLOCK aggregation at `src/sysml_codegen/analysis/constraint_lowering.py:861`. |
| F5 anonymous exclusions | **Certify** | Portable anonymous identity and the 128-bit suffix remain at `src/sysml_codegen/analysis/constraint_lowering.py:895`. |
| F6 transactional assignment | **Certify** | Complete-candidate prevalidation precedes mutation at `src/sysml_codegen/resolution/models.py:24`. |
| F7 malformed arity | **Certify** | Exact-two `xor`/`implies` gate remains at `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:605`. |
| F8 contradictory ratio | **Certify** | Dimension rejection still precedes equal-unit admission at `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:294`. |
| F9 directory symlinks | **Certify** | Canonical and emitted verifiers still reject internal and escaping directory symlinks at `src/sysml_codegen/contracts/verify.py:263`. |
| F10 durable docs | **Certify** | Every relevant source and hash-identified wheel guide statement now matches the v3 profile and L4/L6 consumers. |

### Second-cure verification

- **Companion guide and shipped bytes:** the opening contract states that BLOCK stops generation
  and produces named L6 `ERROR` diagnostics, and the subtype summary includes asserted
  `NON_NUMERICAL` outcomes (`../agentic-mbse/docs/patterns/constraints.md:25` and `:338`). These
  statements match the L6 severity loop at
  `../agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:600` and L4 accounting at
  `../agentic-mbse/src/agentic_mbse/validation/level4_constraints.py:47`.
- **Guide regression:** the kept test pins all four outcomes, both corrected `ERROR` passages, the
  three asserted routes, and the retired-wording exclusions
  (`../agentic-mbse/tests/test_constraint_documentation.py:6`).
- **Wheel inspection:** the preserved second-cure wheel has SHA-256
  `160e7eb55eb6bf4bfba3b422166e6e8f4eef50f7a6c09aa2f7ed91a7cd8a8d4f`. Its packaged
  `agentic_mbse_data/docs/patterns/constraints.md` is byte-identical to source. Older temporary
  wheels are not the recorded candidate and are not certification evidence.
- **TEAx boundary:** candidate expansion, resolution, and SimKit validation share the specific
  `OSError`/`RuntimeError` boundary at `tests/helpers/teax_discovery.py:24`; final failure names both
  accepted routes at `:40`. The symlink-loop and injected `expanduser()` regressions pin both former
  escape paths (`tests/unit/test_teax_discovery.py:42` and `:56`).
- **Warning-byte parity:** the exact `root-0/model.sysml` strings remain equal across repeated live,
  relocated live, and snapshot replay routes
  (`tests/conformance/test_constraint_snapshot_identity.py:128`).

### Design conformance

Item 5 intentionally has no separate design. The implementation follows the spec's fixed local
mechanisms and preserves the external F1 and merge-order boundaries.

### Code integrity

No new abstraction-quality or failure-honesty issue was found. TEAx discovery catches only the
filesystem exceptions normalized by that route boundary, preserves each cause in the final
diagnostic, and still fails after all candidates are invalid.

### Validation

- Fresh codegen focused selection: **132 passed**; corresponding optimized selection: **110
  passed**.
- Supplemental codegen F2-F9 and warning selections: **118 passed**, then **24 passed / 3
  license-skipped**.
- Fresh companion guide/profile/L6 selection: **89 passed**; broader guide/profile selection:
  **143 passed**.
- Preserved second-cure wheel hash and source-byte comparison passed. Both repository worktree
  `git diff --check` gates remain clean.
- Carried licensed evidence remains **9 passed** through real SimKit, with unchanged fixture
  manifests and empty fixture diffs.

## Certification

Certified all local and in-scope GAP-CLOSE work, including F10 and the complete TEAx discovery
failure boundary. Re-certified warning-byte parity and F2 through F9. Updated the local status and
verified epic/item checkboxes. Authorized the next stage as an explicitly partial pre-PR wave only.

Did not certify F1 or the full epic. Did not mark the conjunctive audit/pre-PR/PR-comment criterion
complete, and did not mark the wave gate complete.

**Not checked:** The external TEAx evaluator implementation does not exist to test. Pre-PR, PR
pushes/comments, and merge behavior were intentionally not performed. Full licensed suites were not
rerun after the narrowly scoped prose and test-helper cures. A new wheel build was not repeated;
the recorded rebuilt candidate was hash-checked and inspected byte-for-byte instead.
