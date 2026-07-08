# Audit: Qualified-Name Utility Split

**Verdict:** Certify
**Audited:** 2026-07-08
**Branch:** `push-down-item1-expression`
**Commit:** `810fed3` plus uncommitted Item 2 changes

---

## Summary

Item 2 meets the spec and design. The SysML-general qualified-name helpers now live in agentic-mbse, sysml-codegen keeps the permanent compatibility path, and fixture baselines are unchanged.

The only retained gap is deliberately filed: the Level-6 non-injective-name warning still needs a sibling-scope collector. The existing `ITEM-SYNC-C8` row was updated with the rule, fixture shape, severity, and rationale, so the checking-profile loop is closed for this item.

## Findings

### Plan Completion

All phases verified.

- Phase 1 is complete. `agentic_mbse.sysml.qualified_names` defines exactly the six shared helpers and a private owner-chain helper at `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:13`, `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:33`, `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:71`, `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:76`, `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:86`, and `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:91`. The exported surface is exact at `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:102`.
- Phase 2 is complete by the allowed filed path. `ITEM-SYNC-C8` now names the shared sanitizer, same-owner collision rule, positive and negative fixture shape, WARNING severity, and rationale at `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:118`.
- Phase 3 is complete. sysml-codegen imports the six shared helpers at `src/sysml_codegen/core/qualified_names.py:10` and keeps the four codegen-owned builders local at `src/sysml_codegen/core/qualified_names.py:20`, `src/sysml_codegen/core/qualified_names.py:25`, `src/sysml_codegen/core/qualified_names.py:30`, and `src/sysml_codegen/core/qualified_names.py:35`.
- Phase 4 is complete. Full suites passed in both repos, touched-file ruff passed, `ruff check src/` passed in sysml-codegen, and `git diff -- tests/fixtures` was empty. Full mypy remains baseline-dirty in both repos, with no new qualified-name errors.

### Spec Conformance

- Shared API subset: verified. The module exports only `sanitize_name`, `build_element_qualified_name`, `sysml_to_python_qualified_name`, `sanitize_qualified_name`, `python_to_sysml_qualified_name`, and `extract_simple_name` at `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:102`.
- Permanent sysml-codegen imports: verified. The shim re-exports shared helpers at `src/sysml_codegen/core/qualified_names.py:10`; the package-level surface preserves existing exports and still omits `sanitize_qualified_name` at `src/sysml_codegen/core/__init__.py:35` and `src/sysml_codegen/core/__init__.py:46`.
- Codegen-specific builders stay local: verified at `src/sysml_codegen/core/qualified_names.py:20`, `src/sysml_codegen/core/qualified_names.py:25`, `src/sysml_codegen/core/qualified_names.py:30`, and `src/sysml_codegen/core/qualified_names.py:35`. The shared module has no matching exports.
- INV-5 coverage moved appropriately: verified by agentic-mbse tests for non-empty identifier-safe keyword-safe output at `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_qualified_names.py:71` and already-safe segment identity at `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_qualified_names.py:130`.
- Checking-profile loop: verified. The helper-by-helper outcome is recorded in plan notes, and `ITEM-SYNC-C8` is updated rather than duplicated.
- Suites and byte identity: verified. agentic-mbse full suite passed with `1268 passed, 1 skipped, 33 deselected`; sysml-codegen full suite passed with `2122 passed, 4 skipped`; fixture diff was empty.
- Non-goals respected. Parameter/module/channel builders and `owning_part_leaf` were not moved to agentic-mbse; ADR-003 formats and expression compiler sanitizer behavior were not redesigned; no item-level PR artifact was added.

### Design Conformance

Implementation follows the design.

- D1/D2: shared module plus package export are present at `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:1` and `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py:39`.
- D3: sysml-codegen remains a permanent mixed shim at `src/sysml_codegen/core/qualified_names.py:1`.
- D4: `sanitize_qualified_name` keeps the apply-once/non-reentrant contract at `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/qualified_names.py:76`, with a regression pin at `/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_qualified_names.py:118`.
- D5: `ITEM-SYNC-C8` took the design-approved filed path because the remaining collector is broader than the utility move.
- Object identity pins prove that sysml-codegen did not keep copied helper bodies at `tests/unit/test_qualified_names_shim.py:9`.

### Code Integrity

No issues found.

The shared module is small, standard-library-only, and policy-free. The sysml-codegen shim is explicit about what delegates and what remains local. No broad fallbacks, hidden modes, copied sanitizer implementation, or dependency inversion were found.

## Certification

Certified Item 2 as implemented and ready to continue the PUSH-DOWN epic.

Checked:

- `.project/active/qualified-name-utility-split/{spec,design,plan}.md`
- `.project/backlog/epic_push_down.md`
- agentic-mbse shared module, exports, tests, and `ITEM-SYNC-C8`
- sysml-codegen compatibility shim, package exports, and shim tests
- full and targeted validation results recorded in `plan.md`

Marked:

- Item 2 success criteria in the spec.
- Item 2 success criteria in the PUSH-DOWN epic.
- Current work status for Item 2.
