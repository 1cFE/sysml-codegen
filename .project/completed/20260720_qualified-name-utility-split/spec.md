# Spec: Qualified-Name Utility Split

**Status:** Certified
**Owner:** Reid W
**Created:** 2026-07-08 15:43 PDT
**Complexity:** MEDIUM
**Branch:** push-down-item1-expression (full PUSH-DOWN epic branch; Item 2 continues on top of
certified Item 1)

---

## Problem

PUSH-DOWN Item 1 moved reusable expression reconstruction into `agentic_mbse.sysml`, but
qualified-name handling is still split by package ownership in the wrong place.
`sysml_codegen.core.qualified_names` contains both SysML-general utilities and codegen-specific
identifier builders. That blocks reuse in agentic-mbse validation and keeps name-profile checks
dependent on codegen-local behavior.

This item needs to split the module boundary without changing generated names. The shared
agentic-mbse API should own the general SysML name operations, while sysml-codegen should keep
ADR-003 builders for modules, channels, parameters, and local alias/scoping policy.

Implementation is gated on PUSH-DOWN Item 1 being complete in both repositories. Item 1 is
complete, audited, and committed on the current full-epic branch, so Item 2 may proceed on top
of that state.

## Success Criteria

- [x] `agentic_mbse.sysml.qualified_names` exposes only the general name subset:
  `sanitize_name`, `build_element_qualified_name`, `sysml_to_python_qualified_name`,
  `sanitize_qualified_name`, `python_to_sysml_qualified_name`, and `extract_simple_name`.
- [x] sysml-codegen keeps permanent compatibility imports from
  `sysml_codegen.core.qualified_names` and `sysml_codegen.core`, because existing conformance
  tests assert those import paths.
- [x] Codegen-specific identifier builders stay local to sysml-codegen:
  `build_parameter_qualified_name`, `get_module_name`, `get_channel_name`, and
  `owning_part_leaf`.
- [x] INV-5 name tests move with the shared implementation or are duplicated only where needed
  to prove the permanent sysml-codegen re-export surface. The moved coverage must pin
  non-empty output, `.isidentifier()`, Python-keyword safety, and no dangerous fixture-corpus
  identifier churn for already-safe names.
- [x] The checking-profile loop is closed in agentic-mbse with a helper-by-helper disposition
  table. Each moved helper must be marked `DONE`, `EXISTING`, `NEW RULE`, or `FILED`; every
  `FILED` row must name a backlog item with rule, fixture shape, severity, and rationale.
  Existing agentic-mbse `ITEM-SYNC-C8` must be updated, superseded, discharged, or explicitly
  kept with a reason; do not file a duplicate row for the same "two names one identifier"
  hazard.
- [x] Both repository suites pass after the split, and sysml-codegen fixture baselines are
  byte-identical.

## Known Requirements

- **[HARD]** This work depends on PUSH-DOWN Item 1. The implementation must start from the
  branch state where expression reconstruction has already landed in both sysml-codegen and
  agentic-mbse.
- **[HARD]** The split must not create item-level PR closeout. This item feeds the full
  PUSH-DOWN epic branch.
- **[HARD]** The shared agentic-mbse API must not import sysml-codegen. Checking-profile rules
  must be expressed over SysML facts available in agentic-mbse.
- **[HARD]** The sysml-codegen import paths for qualified-name utilities are permanent
  compatibility surfaces.
- **[HARD]** `build_parameter_qualified_name`, `get_module_name`, `get_channel_name`, and
  `owning_part_leaf` remain sysml-codegen-owned because they encode codegen identifier and
  alias/scoping policy.
- **[HARD]** The moved public helper set is exactly `sanitize_name`,
  `build_element_qualified_name`, `sysml_to_python_qualified_name`, `sanitize_qualified_name`,
  `python_to_sysml_qualified_name`, and `extract_simple_name`, unless design records a reviewed
  reason to exclude one.
- **[HARD]** `sanitize_qualified_name` remains a per-segment SysML `::` to Python `__`
  conversion. It is applied exactly once at the `::`-form to `__`-form boundary. The split must
  preserve the current non-reentrant behavior: do not run it over an already `__`-joined name,
  because segment sanitizer underscore collapse can destroy the ADR-003 separator.
- **[NEED]** Name sanitization remains non-empty, Python-identifier-safe, and keyword-safe for
  every input shape currently covered by INV-5.
- **[NEED]** Name-profile validation catches or files the hazards that generation currently
  needs to fail early: non-injective sanitization, invalid generated identifiers, and
  qualified-name ambiguity.
- **[NEED]** The profile close-out must include existing `ITEM-SYNC-C8`
  (`two names one identifier`) from agentic-mbse backlog. Item 2 creates the shared sanitizer
  that row was waiting for, so the final disposition must update or deliberately preserve that
  existing row rather than silently creating a parallel rule.
- **[NEED]** The move preserves behavior. It should not cause snapshot recapture, generated
  baseline churn, or name-format changes.
- **[INFERRED]** `agentic_mbse.sysml.__init__` should export the new shared qualified-name API
  if the surrounding sysml package continues its current public-export pattern.
- **[INFERRED]** sysml-codegen should keep local coverage for codegen-only builders after the
  shared tests move, so the split line is protected from future drift.

## Non-Goals

- Moving parameter, module, or channel builders into agentic-mbse.
- Moving `owning_part_leaf` into agentic-mbse.
- Redesigning ADR-003 naming formats.
- Changing expression compiler `_sanitize_name` behavior beyond documenting or preserving its
  intentional divergence from `sanitize_name`.
- Moving hierarchy, aggregation, template detection, virtual-binding matching, parameter-group
  derivation, module construction, channel construction, or alias/scoping policy.
- Opening or preparing an item-level PR.

## Open Questions / Deferred to design

- Decide whether `agentic_mbse.sysml.qualified_names` is also re-exported from
  `agentic_mbse.sysml.__init__`, or whether direct module imports are preferred for the first
  landing.
- Decide the exact agentic-mbse validation shape for naming hazards through a helper-by-helper
  close-out table: implement rules now where the validation substrate is ready, or file/update
  named backlog entries with concrete fixtures, severity, and rationale where more validation
  plumbing is needed.
- Decide which sysml-codegen tests remain as import-path/re-export pins after INV-5 coverage
  moves to agentic-mbse.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_push_down.md`
- **Prior item gate:** `.project/active/expression-reconstruction-push-down/{spec,design,plan,audit}.md`
- **Required Reading:** `.project/concepts/agentic-mbse-push-down-design.md`
- **Required Reading:** `.project/research/20260220-163000_agentic-mbse-boundary-analysis.md`
- **Required Reading:** `.project/completed/20260708_epic_truth_debt.md`
- **Required Reading:** `.project/backlog/BACKLOG.md` `[PUSH-DOWN]` entry
- **Required Reading:** `src/sysml_codegen/core/qualified_names.py`
- **Required Reading:** `src/sysml_codegen/core/__init__.py`
- **Required Reading:** `tests/conformance/test_naming_conventions.py`
- **Required Reading:** `tests/conformance/test_sanitize_invariance.py`
- **Required Reading:** `tests/conformance/test_silent_failure_sc4a1.py`
- **Required Reading:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/helpers.py`
- **Required Reading:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py`
- **Required Reading:** `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`
- **Design:** `.project/active/qualified-name-utility-split/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `my-design`.
