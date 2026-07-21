# Audit: CONSTRAINT-WAVE Item 2 — Generated Constraint Name Safety

**Verdict:** Certify
**Audited:** 2026-07-18
**Branch:** `constraint-exec-epic`
**Commit:** `512786c`
**Scope:** License-free implementation; external execution and licensed live parity remain open

---

## Summary

The prior Needs Work finding is remediated. A graph containing constraint modules without a
constraint catalog now produces a deterministic structured join violation at the shared preflight,
so direct renderers, all nine graph-aware writers, and `run_codegen()` reject before mutation.
Kept permutation and historical-impact tests close the two prior evidence gaps. The license-free
Item 2 implementation is certified; TEAx execution and licensed live/snapshot parity remain
unclaimed.

## Findings

### Plan completion

All license-free phases are verified. The three Phase 4 boxes reopened by the prior audit are now
supported by the shared validator fix and kept direct-renderer, writer, and orchestration tests
(`plan.md:455-470,502-515`). The separate historical-impact overlay closes the Phase 1 evidence gap,
and the 16 kept permutations close the deterministic-diagnostic test gap.

The external execution box remains correctly open at `plan.md:572-573,609-611`. The plan also
honestly leaves its broader per-route lowering matrix, exhaustive Python binding-form matrix, and
separate CLI process assertion unchecked; none is required to resolve the prior production finding.

### Spec conformance

- **SC-1 — Verified.** Four fresh, separate baseline processes reproduced the reviewed outcomes:
  `value` returned a wrongly positive `3.0` margin for a violation; `status` returned `margin=None`;
  `verdict` raised `TypeError` after wrapper rebinding; and `self` raised duplicate-argument
  `SyntaxError` (`evidence/test_name_safety_historical_impact.py:73-211`). The overlay hash is
  `f9ce55ab…a741864`; the original rejection overlay remains `e4212334…ebe7`.
- **SC-2 — Verified.** `value`/`status` reject at predicate compilation and `self`/`verdict` reject
  at wrapper/package preflight. All four orchestration cases preserve absent and populated targets.
- **SC-3 — Verified.** Predicate inventory rejects generated-binding overlap and distinct identities
  sharing a final name before first-occurrence deduplication; safe repeated references retain one
  parameter (`constraint_name_safety.py:125-203`, `predicate_compiler.py:214-228`).
- **SC-4 — Verified.** Wrapper inventory reserves `self`/`verdict`, rejects duplicate final bindings,
  and verifies the exact emitted `run` scope (`constraint_name_safety.py:41-45,158-203`,
  `modules.py:249-343`).
- **SC-5 — Verified.** Catalog-bearing graphs enforce identity correspondence. A constraint module
  with no catalog now emits structured `catalog_module_join`, while a truly constraint-free graph
  remains valid (`constraint_name_safety.py:341-355`, `test_constraint_name_safety.py:154-174`).
- **SC-6 — Verified.** Python `symtable` checks both emitted scopes against structured policies and
  fails when an unowned binding appears (`constraint_name_safety.py:274-328`).
- **SC-7 — Verified.** The frozen rejection overlay covers the four names, both identity collapses,
  and cross-path disagreement. Sixteen kept combinations independently permute catalog, formal,
  leaf, and input order and pin one exact diagnostic; a safe control retains argument order
  `second, first` (`test_constraint_name_safety.py:177-274`).
- **SC-8 — Verified.** Fresh missing-catalog tests pass for all nine writers across absent/populated
  targets and for both `run_codegen()` target states (`test_cli_generation.py:298-319,370-387`).
  Re-running the original audit probe returned structured `catalog_module_join`; the renderer
  rejected and `run_codegen()` left the absent target absent.
- **SC-9 — Not checked.** The real `x <= limit` package still cannot import TEAx because `pandas` is
  unavailable. Exact satisfied/violated tuples remain unclaimed.
- **SC-10 — Verified.** Direct predicate failures remain structured `PredicateCompileError`; shared
  compile/render/package paths normalize to structured `CodeGenerationError` with cause chaining.
- **SC-11 — Verified for available routes.** The augmented focused selection passes 174/174 normally
  and under `PYTHONOPTIMIZE=1`. Collision-free baseline/candidate manifests remain 27-file
  byte-identical, and fixture hashes are unchanged.

### Design conformance

The prior I6/I7 violation is closed. When `constraint_catalog is None`, the validator now returns
one sorted join violation per constraint module instead of treating the graph as constraint-free
(`constraint_name_safety.py:341-355`). The same adapter runs before renderer projection and writer
or orchestration mutation. Fresh results: validator/permutation/order **19 passed**; direct renderer
coverage **4 passed**; missing-catalog writer/orchestration matrix **20 passed**.

I1-I10 and I12 follow the revised design. I11 is verified for license-free snapshot reconstruction;
licensed live parity is outside this certification because the required license is unavailable.

### Code integrity

The previous silent fallback is removed. The replacement is narrow, deterministic, and preserves
the valid zero-constraint case. No new abstraction-quality, parameter-sprawl, broad-exception,
compatibility-shim, or failure-honesty issue was found in the remediated Item 2 delta.

### Isolation and repository evidence

- The Item-2-only patch (`c8f03e72…fa580e`) passes `git apply --check` against detached baseline
  `512786c`. It contains 11 production paths and records
  `generation/constraint_name_safety.py` as `new file mode 100644`.
- The patch contains no `ensure_package_tree_is_link_free`, `contracts/seal.py`, or
  `contracts/verify.py` hunk. Live Item 6 call sites remain present; the overlap selection passes
  **122 passed, 2 skipped**.
- Ruff passes the complete Item 2 scope with an explicit `I001` exemption for the immutable frozen
  rejection overlay. The overlay hash is unchanged. `git diff --check`, the fixture manifest
  comparison, and `git diff -- tests/fixtures` pass.
- The recorded broader gate is **149 passed, 28 skipped**. The recorded full suite is
  **2,320 passed, 205 skipped, 23 failed, 96 errors, 10 deselected**; the failures/errors are the
  known Syside-license-dependent families. The full suite was inspected but not rerun in this
  re-audit.

---

## Certification

- Confirmed spec SC-1 through SC-8 and SC-10 through SC-11 checked.
- Left SC-9 and the epic execution criterion open because TEAx cannot import without `pandas`.
- Verified the reopened Phase 4 plan claims and left their completed boxes checked.
- Certified Item 2's license-free implementation in current work and the epic status note. The epic
  item heading remains without ✅ because one spec success criterion is still unavailable.
- No production code, Item 4 artifact, commit, push, or PR state was changed by this audit.

**Not checked:** Exact TEAx satisfied/violated runtime tuples; licensed Syside live lowering and
live/snapshot parity; remote PR state. The full repository suite was not independently rerun in this
pass; its recorded classification was reviewed against the evidence artifact. Full mypy was not
rerun; the recorded 76-error baseline remains carried evidence.

---

## Post-audit addendum — 2026-07-19 (execution leg executed)

This addendum records new evidence only; it does not revise the certification verdict above.

At audit time SC-9 and the epic execution criterion were left open solely because `pandas` was
unavailable on the TEAx import path. `pandas` is now available, so the previously-blocked leg was
run in the real configured environment (agentic-mbse venv, pandas 2.3.3, teax-simkit on
`sys.path`), in fresh subprocesses, not mocked.

- Pinned execution-gate node
  (`test_name_safety_collision_free_exact_evidence`): **1 passed, 14 deselected**.
- Exact tuples — satisfied `(True, 'satisfied', 1.0, {'x': 2.0, 'limit': 3.0})`, violated
  `(False, 'violated', -1.0, {'x': 4.0, 'limit': 3.0})` — both equal the node's asserted values
  (`evidence/collision-free-execution-tuples.txt`, `evidence/evidence.md` §"Execution gate").

SC-9 is now met; verdict/status/margin/observed are correct for both truth values. The audit's
"Certify (license-free scope)" verdict is unchanged; the one criterion it left unavailable is now
closed. Licensed Syside live lowering and live/snapshot parity (design I11) remain out of this
item's scope, tracked under Item 8.
