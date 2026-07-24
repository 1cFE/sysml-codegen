# Design Review: Hierarchy Primitives and Data Models

**Design:** `.project/active/hierarchy-primitives-models/design.md`
**Spec:** `.project/active/hierarchy-primitives-models/spec.md`
**Review File:** `.project/active/hierarchy-primitives-models/design-review.md`
**Date:** 2026-07-08

---

## Fundamental Assessment

Sound. The design chooses the right split for PUSH-DOWN Item 3: move the neutral fact layer into
`agentic_mbse.sysml.hierarchy`, keep policy and orchestration in sysml-codegen, and preserve existing
sysml-codegen import paths through permanent wrappers and re-exports.

The core abstraction earns its place. `classify_redefinition(member, owning_qn)` is the smallest
shared unit that prevents copying `_extract_single_redefinition` while still keeping the
design-level `PartUsage` scanner, plain-usage filter, override precedence, usage-type indexing,
aggregation rewriting, and `HierarchyExtractionResult` local to sysml-codegen (`design.md:114`,
`design.md:133`, `design.md:214`). A simpler design that moves only the two list extractors would
force either copied classifier code or a private cross-package dependency in `extract_design_overrides`.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Pass

The design covers the spec requirements directly:

- Shared redefinition and multiplicity extraction are exposed from `agentic_mbse.sysml.hierarchy`
  (`design.md:114`, `design.md:230`), matching the success criterion for reusable hierarchy
  primitives (`spec.md:33`).
- The three models move as standard-library dataclasses or enum/dataclass pairs and remain
  field-identical (`design.md:147`, `design.md:257`), matching the dataclass and exact-field
  requirements (`spec.md:35`, `spec.md:65`).
- sysml-codegen re-exports exact class objects and keeps stable compatibility paths (`design.md:126`,
  `design.md:267`, `design.md:280`), matching the identity and compatibility requirements
  (`spec.md:38`, `spec.md:71`).
- Codegen policy stays local: design overrides, usage indexing, orchestration, aggregation,
  scoping, module construction, and `HierarchyExtractionResult` are all explicitly retained in
  sysml-codegen (`design.md:162`, `design.md:214`), matching the hard boundary (`spec.md:49`,
  `spec.md:111`).
- The checking-profile loop has a per-idiom disposition matrix with rule, fixture shape, severity,
  rationale, and backlog ID when filed (`design.md:312`), matching the spec (`spec.md:92`).

### 2. Pattern Consistency
**Assessment:** Pass

The re-export and wrapper strategy follows the pattern already used by PUSH-DOWN Items 1 and 2:
shared implementation in agentic-mbse, permanent sysml-codegen compatibility import paths, and tests
that prove the local path is delegating rather than copying (`design.md:280`). The data model home
also follows the existing `AttributeInfo` pattern in `agentic_mbse.sysml.data_models` (`design.md:122`).

### 3. Abstraction Quality
**Assessment:** Pass

The design has one new shared module and one new public helper. That is the right level of
abstraction for the existing code shape:

- The current single-member classifier is already the shared unit inside sysml-codegen
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:85`).
- The two list extractors are thin owned-member scanners (`src/sysml_codegen/extraction/hierarchy_resolver.py:175`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:252`).
- `extract_design_overrides` adds policy on top of the same classifier and is explicitly kept local
  (`src/sysml_codegen/extraction/hierarchy_resolver.py:209`, `design.md:291`).

This avoids a heavy hierarchy service abstraction and avoids moving the whole resolver.

### 4. Duplication Avoidance
**Assessment:** Pass

The design removes the future duplication risk by moving the classifier body once and making
sysml-codegen wrappers delegate to it (`design.md:287`). The planned monkeypatch tests are a good
guard against accidentally leaving copied implementations in the compatibility layer (`design.md:287`,
`design.md:291`).

### 5. Data Structure Clarity
**Assessment:** Pass

The data structure contract is explicit enough to implement and test. The design names the exact
field order, defaults, default factories, and value types (`design.md:172`, `design.md:257`). It also
requires object identity through the sysml-codegen import path, not only shape compatibility
(`design.md:180`, `design.md:276`).

One implementation detail to preserve: compare field order and defaults with an ordered
`dataclasses.fields()` projection, not the current conformance test's set-of-field-names style
(`tests/conformance/test_data_models.py:297`). The design already calls for the stronger check.

### 6. Route Safety
**Assessment:** Pass

No web routes or endpoint routing are involved. The analogous safety concern is extraction routing:
the design keeps scans explicit and bounded. `extract_redefinitions` remains an owned-member scan and
must not call `elements_of_type`; `extract_multiplicities` scans only child `PartUsage` members
(`design.md:183`, `design.md:184`). This preserves the existing behavior
(`src/sysml_codegen/extraction/hierarchy_resolver.py:190`, `src/sysml_codegen/extraction/hierarchy_resolver.py:269`).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets are real and mostly backed by code. B1 and B4 are the load-bearing bets: primitive
redefinition/multiplicity facts can move without policy, and profile rows that need indexing can be
filed without weakening the item (`design.md:100`, `design.md:108`). The design supports both by
keeping usage-type indexing and most-specific selection local (`design.md:219`) and filing the
ambiguous inherited-attributes row (`design.md:324`).

Minor hidden bet: the TYPE_MAP inventory test will only be reliable if it clears or bypasses
`SysideAdapter._type_map` before using a monkeypatched fake syside. The adapter caches the generated
map (`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py:160`), so a test that
does not reset that cache can pass or fail depending on test order. This is an implementation risk,
not a design flaw.

Minor hidden bet: the hierarchy-source inventory only covers direct `SysideAdapter` calls in the
moved hierarchy module (`design.md:307`). That is correct for Item 3's boundary, but implementation
should rely on existing expression-helper TYPE_MAP coverage for transitive literal-node and
reconstruction calls. Do not expand Item 3's inventory to every expression helper string unless an
actual new hierarchy call introduces one.

### 8. Reader Comprehension
**Assessment:** Pass

The design is readable and gives the reader the model before the mechanism. The core concept states
the boundary in plain terms: shared facts in agentic-mbse, generated-package behavior in sysml-codegen
(`design.md:89`). The later sections then repeat the same boundary in decisions, invariants, and
test placement without introducing a competing mental model.

---

## Issues by Severity

### Critical
- None.

### Major
- None.

### Minor
- TYPE_MAP cache reset is not called out: the implementation-site inventory test should reset or
  bypass `SysideAdapter._type_map` before monkeypatching fake syside, or test order can affect the
  result. - Bets & Decisions Integrity
- Transitive TYPE_MAP scope needs discipline: Item 3 should inventory direct adapter strings in the
  moved hierarchy module and rely on existing expression-helper coverage for transitive helper calls,
  unless the move introduces new direct strings. - Bets & Decisions Integrity

---

## Recommendations

1. Approve the design for planning/implementation.
2. Add a plan note for the TYPE_MAP test to reset `SysideAdapter._type_map` around the fake syside
   inventory check.
3. Keep the hierarchy inventory scoped to direct adapter strings in `agentic_mbse.sysml.hierarchy`;
   verify transitive expression-helper coverage through existing expression tests or a targeted
   smoke test, not by widening this item into expression-profile revalidation.

---

## Resolutions

No user resolutions recorded yet. The review is approved with minor implementation notes.

---

**Overall:** Approve
**Next Steps:** Proceed to `$my-plan` or `$my-implement` for the cross-repo move. Carry the two minor
TYPE_MAP notes into the plan so implementation does not depend on test order or over-expand the
inventory scope. The reviewer does not edit the design.
