# Spec: Model and Seal Boundary Guards

**Status:** Certified in GAP-CLOSE independent audit (2026-07-18)
**Owner:** Reid W
**Created:** 2026-07-18 15:39 PDT
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** GAP-CLOSE — Item 3

---

## Problem

Two localized integrity guards do not cover the full boundary they claim to protect.
`ConcreteConstraint` prevalidates assignment only when the target field was explicitly supplied
at construction. Fields initialized from defaults bypass that prevalidation, so Pydantic can raise
for a rejected cross-field change after leaving the live object invalid. This is production-exposed:
the eligible lowering path omits the defaulted `exclusion` field. Separately, package verification
walks regular files but overlooks directory symlinks. An unrecorded symlink can therefore add an
importable tree, whether its target is inside or outside the package root, while verification still
reports success.

Both findings were independently reproduced at pinned HEAD. They are verified agent findings, not
owner-originated requirements. The correction is confined to model-lifetime validation and the
sealed-package walk; it does not require a new architecture or interface.

## Success Criteria

- [x] Every assignment to a Pydantic model field after initialization is validated against a
      complete candidate model before the live instance changes, including fields whose initial
      values came from defaults.
- [x] On an eligible `ConcreteConstraint` built without explicitly passing `eligible` or
      `exclusion`, rejecting `eligible = False` and rejecting installation of an exclusion each
      leave the complete object unchanged. After each rejection, both `model_dump_json()` and
      validate-from-JSON round trip succeed and reproduce the original object.
- [x] The inverse eligible/excluded mutation cases remain transactional, and the existing
      `ConstraintCatalogEntry` polarity mutation remains rejected without mutation and remains
      serializable. This pins its already-safe behavior rather than claiming a newly found hole.
- [x] Valid deliberate post-initialization assignments continue to work. Generation-time code may
      still mutate models where existing invariants permit the new value; the implementation does
      not freeze models or replace assignment with a new lifecycle.
- [x] Package verification rejects every directory symlink found anywhere beneath the package
      root. Each result is fatal and identifies the symlink's package-relative path, regardless of
      whether the target remains inside the root or escapes it.
- [x] The kept F9 regression matrix covers both verified cases:

      | Directory symlink case | Required result |
      |---|---|
      | Target is inside the package root | Fatal diagnostic whose `path` is the symlink path |
      | Target escapes the package root | Fatal diagnostic whose `path` is the symlink path |

      A matching real directory remains governed by the existing seal policy, and existing
      regular-file and recorded-file-symlink checks retain their current behavior.
- [x] The verifier remains standalone and standard-library-only. The canonical verifier source is
      still copied verbatim into generated packages, and the emitted copy enforces the same
      directory-symlink rule.
- [x] Before production changes, kept regression tests are run in isolation against exact pre-fix
      HEAD `6db321225a5c8568db0287b67ed1d04c03079cc2`. F6 RED evidence fails because the rejected
      default-field assignment changed the live object or broke serialization. F9 RED evidence
      fails because verification returned `ok=True` or omitted the path-specific fatal diagnostic
      for each case. Setup, import, collection, or unrelated failures do not count as RED.
- [x] The evidence record identifies the tested revision, exact commands, resolved source paths,
      test-input hash, exit status, and defect-specific output. Baseline and candidate runs use the
      same test input in source-isolated fresh processes so the dirty working tree or editable
      install cannot satisfy the historical run.
- [x] Validation is green at three levels:
      - focused:
        `uv run pytest -q tests/unit/test_concrete_constraint_model.py tests/unit/test_verify_package.py`;
      - broader:
        `uv run pytest -q tests/unit/test_contract_models.py tests/unit/test_constraint_graph_extension.py tests/unit/test_constraint_emission.py tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py`;
      - full: the repository's default `uv run pytest tests/` gate.
      Touched-file Ruff and formatting checks pass, and project mypy is no worse than its recorded
      baseline.
- [x] `tests/fixtures/` is byte-identical before and after this item. If implementation uncovers an
      unavoidable fixture change, work stops until the change is justified in the plan and its
      exact byte diff is reviewed; a blanket recapture is not allowed.

## Known Requirements

- **[INFERRED]** All post-initialization field assignments on
  `_TransactionalAssignmentModel` prevalidate a complete candidate before mutating the live
  instance, including assignments to fields initialized from defaults. Sources:
  `.project/research/20260718-123558_constraint-expression-final-gap-review.md`, F6;
  `.project/research/20260718_gap-review-verification.md`, F6; and
  `.project/backlog/epic_gap_close.md`, Item 3.
- **[INFERRED]** Rejected eligible/exclusion mutations leave `ConcreteConstraint` exactly
  unchanged and serializable. Both default-omission directions are kept regressions because the
  current helper explicitly supplies those fields and misses the verified production-exposed
  route. Sources: both F6 research records and
  `tests/unit/test_concrete_constraint_model.py`.
- **[INFERRED]** `ConstraintCatalogEntry`'s existing transactional assignment behavior remains
  pinned. Independent verification found no corresponding default-field hole because every entry
  field is required. Source: `.project/research/20260718_gap-review-verification.md`, F6.
- **[INFERRED]** Valid deliberate assignment remains supported. Model freezing and replacement of
  the existing mutable generation lifecycle are outside the localized correction. Source:
  `.project/backlog/epic_gap_close.md`, Item 3, and the current assignment-validating model
  boundary at `src/sysml_codegen/resolution/models.py`.
- **[INFERRED]** Any directory symlink beneath the package root is rejected outright, including
  internal and escaping targets, with a fatal diagnostic carrying the symlink's package-relative
  path. This selects the lean strict policy from the verified F9 alternatives. Sources:
  `.project/research/20260718-123558_constraint-expression-final-gap-review.md`, F9;
  `.project/research/20260718_gap-review-verification.md`, F9; and
  `.project/backlog/epic_gap_close.md`, Item 3.
- **[HARD]** `src/sysml_codegen/contracts/verify.py` must remain standard-library-only and usable
  without importing sysml-codegen or agentic-mbse because it is copied verbatim into each generated
  package for verification in the loading environment. Existing interface:
  `src/sysml_codegen/contracts/verify.py` and
  `tests/conformance/test_seal_step9.py`.
- **[INFERRED]** Implementation starts with kept regressions and isolated pre-fix RED evidence at
  exact HEAD `6db321225a5c8568db0287b67ed1d04c03079cc2`. Focused, broader, and default full gates plus
  fixture byte identity form the completion evidence. Source:
  `.project/backlog/epic_gap_close.md` epic strategy and Item 3; the exact evidence controls are
  agent-grade PR-gating requirements.

## Non-Goals

- Freezing `ConcreteConstraint`, `ConstraintCatalogEntry`, or their shared base model.
- Removing or redesigning deliberate generation-time model assignment.
- Changing model fields, serialized model shapes, package seals, archive formats, coverage-policy
  schema, or generated-package layout.
- Following directory symlinks, accepting selected internal directory symlinks, or adding a
  non-standard-library filesystem dependency to the verifier.
- Refactoring model, catalog, generation, or package-verification architecture beyond the two
  boundary guards.
- Closing other GAP-CLOSE findings or changing constraint execution, lowering, profile, metadata,
  or documentation behavior.

## Open Questions / Deferred to design

None. The verified cases, strict symlink policy, mutation contract, and validation boundary are
mechanically specified. The implementation plan may choose local helper names and test placement
without changing architecture or interfaces.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_gap_close.md`, Item 3
- **Required Reading:**
  - `.project/research/20260718-123558_constraint-expression-final-gap-review.md`, F6 and F9
  - `.project/research/20260718_gap-review-verification.md`, F6 production exposure and F9 case
    findings
- **Current context:** `.project/CURRENT_WORK.md`
- **Current implementation and tests:**
  - `src/sysml_codegen/resolution/models.py`
  - `src/sysml_codegen/contracts/verify.py`
  - `tests/unit/test_concrete_constraint_model.py`
  - `tests/unit/test_verify_package.py`
  - `tests/conformance/test_seal_step9.py`
- **Plan:** `.project/active/gap-boundary-guards/plan.md` (required next artifact)
- **Audit:** independent GAP-CLOSE epic audit after implementation (required)

---

**Pipeline decision:** Explicit `my-spec-review`, `my-design`, and `my-design-review` stages are
skipped. They would not change architecture or interfaces for these localized, mechanically
specified guards. Proceed to `my-plan`; implementation remains test-first, and the independent
epic audit remains required after all GAP-CLOSE items are complete.
