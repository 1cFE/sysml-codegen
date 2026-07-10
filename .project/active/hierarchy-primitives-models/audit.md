# Audit: Hierarchy Primitives and Data Models

**Verdict:** Certify
**Audited:** 2026-07-08
**Branch:** push-down-item1-expression
**Commit:** sysml-codegen `e01361b`; agentic-mbse `243a15e`

---

## Summary

PUSH-DOWN Item 3 satisfies the spec and design boundary. The implementation moves only the neutral
hierarchy primitive layer and the three primitive models into agentic-mbse, while sysml-codegen keeps
design overrides, usage indexing, aggregation, orchestration, and `HierarchyExtractionResult`.

The Phase 2 profile disposition is acceptable. Rows that need codegen-local precedence, expression
policy, multiplicity integration, or usage-type selection were filed in agentic-mbse instead of
implemented as shallow Level-6 checks.

## Findings

### Plan completion

All phases verified.

- Phase 1: shared dataclasses and hierarchy primitive extraction are present in
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py:46` and
  `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py:35`. The shared module imports
  only agentic-mbse/stdlib surfaces.
- Phase 2: hierarchy-profile close-out is recorded in the plan and agentic-mbse backlog. The filed
  rows include exact rule, fixture shape, severity, and rationale
  (`/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:365`,
  `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:386`,
  `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:407`,
  `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:428`).
- Phase 3: sysml-codegen re-exports shared runtime class objects and delegates primitive extractors
  (`src/sysml_codegen/extraction/data_models.py:62`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:93`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:165`).
- Phase 4: validation evidence is recorded in the plan
  (`.project/active/hierarchy-primitives-models/plan.md:454`).

### Spec conformance

- SC-1 verified: `agentic_mbse.sysml.hierarchy` exposes `classify_redefinition`,
  `extract_redefinitions`, and `extract_multiplicities`
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py:25`).
- SC-2 verified: `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` live as standard
  dataclasses/enum in agentic-mbse with the required field order and defaults
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py:46`).
- SC-3 verified: sysml-codegen runtime imports the identical shared class objects, with object
  identity tests in `tests/conformance/test_data_models.py:322`.
- SC-4 verified: wrapper delegation tests prove `extract_redefinitions` and
  `extract_multiplicities` call the shared implementation
  (`tests/unit/test_hierarchy_resolver.py:602`, `tests/unit/test_hierarchy_resolver.py:611`).
- SC-5 verified: TYPE_MAP inventory is generated from the moved hierarchy source and scoped to direct
  adapter strings only (`/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_hierarchy.py:260`).
- SC-6 verified: fixture diff is empty per the plan (`.project/active/hierarchy-primitives-models/plan.md:460`).
- SC-7 verified: design overrides and hierarchy policy remain in sysml-codegen
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:119`,
  `src/sysml_codegen/extraction/data_models.py:334`).
- SC-8 verified: profile impact is closed by existing rule or filed backlog rows. Missing
  instantiations remain covered by `L6_CALC_DEF_NO_INSTANTIATION`
  (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:689`).
- SC-9 verified from recorded gates: agentic-mbse full suite `1278 passed, 1 skipped, 33 deselected`;
  sysml-codegen full suite `2127 passed, 4 skipped`; ruff clean in required scopes; mypy remains at
  known baselines (`.project/active/hierarchy-primitives-models/plan.md:454`).

### Design conformance

Implementation follows the approved design.

- The shared API matches the design's primitive extractor shape and includes the one-member
  classifier (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/hierarchy.py:35`).
- sysml-codegen keeps local design override filtering and uses the shared classifier without moving
  design-level scanning or precedence (`src/sysml_codegen/extraction/hierarchy_resolver.py:119`).
- Aggregation decomposition, usage-type indexing, warnings, and `HierarchyExtractionResult` remain
  local (`src/sysml_codegen/extraction/hierarchy_resolver.py:181`,
  `src/sysml_codegen/extraction/data_models.py:334`).
- The TYPE_MAP cache concern from design review is addressed by resetting/bypassing adapter cache in
  the inventory test (`/home/reid/1cfe/agentic-mbse/tests/test_sysml/test_hierarchy.py:273`).

### Code integrity

No issues found. I did not find policy leakage into generic utilities, broad silent fallbacks, copied
compatibility bodies, or placeholder/TODO implementation. The only wrappers are narrow compatibility
delegates with tests proving delegation.

---

## Certification

Certified PUSH-DOWN Item 3. I verified the spec criteria, plan phases, design boundary, profile
disposition, compatibility tests, and recorded validation evidence. I marked the spec success
criteria and epic Item 3 criteria as complete. No pre-pr or item-level PR closeout was performed.

---

## Addendum — 2026-07-10 (remediation)

Independent epic audit findings closed for this item's surfaces:
- `test_direct_type_map_inventory_is_mapped` no longer monkeypatches a fake map built from
  the inventory itself (true by construction); it now asserts the inventory against the
  REAL `SysideAdapter._get_type_map()`.
- The `TYPE_CHECKING` mirror dataclasses in sysml-codegen `extraction/data_models.py`
  (an unpinned drift surface) were deleted: agentic-mbse now ships a `py.typed` marker, so
  mypy checks the real shared classes directly. Runtime re-export identity unchanged.
