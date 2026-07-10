# Spec Review: Hierarchy Primitives and Data Models

**Spec:** `.project/active/hierarchy-primitives-models/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/hierarchy-primitives-models/spec-review.md`
**Date:** 2026-07-08

---

## Reality Check

Concerns. The spec is about the right PUSH-DOWN Item 3 work item: move reusable hierarchy primitives and the three primitive data models, while leaving codegen hierarchy policy in sysml-codegen. The main risk is not item drift. The risk is that several sentences are loose enough to let design either move too much policy or satisfy the checking-profile loop with a shallow filing pass.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The spec is faithful to the epic's Item 3 boundary in the headline, but it undercuts that boundary in the API deferral. The open question asks whether to expose a private helper equivalent to `_extract_single_redefinition` (`spec.md:107`). That helper is currently shared by `extract_redefinitions` and `extract_design_overrides`; the latter is explicitly out of scope (`src/sysml_codegen/extraction/hierarchy_resolver.py:85`, `src/sysml_codegen/extraction/hierarchy_resolver.py:209`, `src/sysml_codegen/extraction/hierarchy_resolver.py:241`). The spec needs to say that any shared helper may classify one `ReferenceUsage`, but must not move the design-level `PartUsage` scanner, plain-usage filtering, or override policy.

**L1-2 · Direct claim:** The checking-profile list includes shapes that are not all primitive hierarchy facts. `missing instantiations` and `ambiguous inherited attributes` depend on usage-type and most-specific-type indexing that the spec correctly leaves in sysml-codegen (`spec.md:48`, `spec.md:92`; `src/sysml_codegen/extraction/hierarchy_resolver.py:574`, `src/sysml_codegen/extraction/hierarchy_resolver.py:670`). The spec should either mark those as file-only profile follow-ups for this item, or explicitly require that they be closed without moving usage-type indexing support.

### Lens 2 — Problem & Approach

**L2-1 · Rewrite request:** The TYPE_MAP criterion is testable in spirit but too imprecise for design. It says to verify every string used by the moved functions, then gives an example list that includes `PartDefinition` even though the primitive functions do not call `is_instance(..., "PartDefinition")`; that string is used by the orchestration sweep that must stay local (`spec.md:40`; `src/sysml_codegen/extraction/hierarchy_resolver.py:654`). Ask the spec agent to require an implementation-site inventory of moved `SysideAdapter.is_instance` / `elements_of_type` strings and a test against that inventory, instead of a partly illustrative list.

**L2-2 · If-then tradeoff:** The spec treats `RedefinitionData` as a reusable primitive model, which is probably right because it is the payload for primitive redefinition extraction. It also carries design-override fields, `target_path` and `is_deep_path`, and is consumed by design override and downstream codegen paths (`src/sysml_codegen/extraction/data_models.py:245`, `src/sysml_codegen/extraction/data_models.py:262`). This is acceptable if the model is moved as a neutral fact carrier, but problematic if design interprets those fields as permission to move design override extraction. The spec should state that moving the data carrier does not move any scanner or policy that populates it for design overrides.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** The checking-profile closure is not specific enough. The success criterion requires exact rule, fixture shape, severity, and rationale (`spec.md:48`), but the requirement drops `exact rule` and `rationale` (`spec.md:80`). Existing agentic-mbse backlog rows use those fields explicitly (`/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:118`, `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:128`, `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:131`, `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:134`, `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:136`). The spec should require a per-idiom disposition matrix: existing rule, new rule, filed backlog row, or no-op, with exact rule, fixture shape, severity, rationale, and backlog ID when filed.

**L3-2 · Direct claim:** Required Reading is not sufficient for the design stage. The spec names source files, but omits the tests that pin the contract: primitive behavior in `tests/unit/test_hierarchy_resolver.py`, dataclass field sets in `tests/conformance/test_data_models.py`, and snapshot round-trip consumers in `src/sysml_codegen/snapshot/loader.py`. It also omits agentic-mbse validation/backlog surfaces needed for profile closure, especially `/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md` and `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`.

**L3-3 · Rewrite request:** The success criteria do not explicitly require identity tests for shared functions, only for class objects (`spec.md:38`). Item 1 and Item 2 both used permanent compatibility shims and identity pins to prove sysml-codegen was not keeping copied bodies. This spec should require the same for `extract_redefinitions` and `extract_multiplicities`, or clearly say wrapper delegation tests are enough if the design keeps wrappers.

### Lens 4 — Hygiene

No material hygiene findings.

### Lens 5 — Reader Comprehension

No material reader-comprehension findings. The spec is readable; the issues above are contract precision issues, not prose clarity issues.

---

## Engagement Summary

**Overall take:** The spec is pointed at the right item and respects the epic's main scope line. It needs revision before design because the boundary around `_extract_single_redefinition`, TYPE_MAP verification, and checking-profile closure is still loose enough to produce a scope leak or a weak closure.

**Here's what I need you to weigh in on:**

1. **[L1-1, L2-2]** Tighten the helper/model boundary: shared primitive classification is allowed, but design override scanning and filtering must stay local.
2. **[L1-2]** Decide how to treat profile idioms that require usage-type indexing facts. For Item 3, they should probably be filed unless they can be closed from moved primitive facts alone.
3. **[L2-1]** Replace the illustrative TYPE_MAP list with an implementation-site inventory requirement, so the design cannot accidentally pull in orchestration just to satisfy `PartDefinition`.
4. **[L3-1]** Make checking-profile closure require exact rule, fixture shape, severity, rationale, and filed backlog ID when filed.
5. **[L3-2]** Add the hierarchy tests, dataclass field tests, snapshot loader, agentic validation file, and agentic backlog to Required Reading.
6. **[L3-3]** Require function-level shim/delegation identity coverage, not only class identity coverage.

---

## Resolutions

- 2026-07-08: Updated the spec to allow only primitive single-`ReferenceUsage` classification helpers and explicitly keep design-level `PartUsage` scanning, plain-usage filtering, design-override filtering, and override policy in sysml-codegen.
- 2026-07-08: Replaced the illustrative TYPE_MAP list with an implementation-site inventory requirement for moved `is_instance(...)` / `elements_of_type(...)` strings.
- 2026-07-08: Added a requirement for per-idiom checking-profile dispositions with exact rule, fixture shape, severity, rationale, and backlog ID when filed.
- 2026-07-08: Added required reading for hierarchy resolver tests, dataclass field tests, snapshot loader, agentic-mbse Level-6 validation, agentic-mbse types, and agentic-mbse backlog.
- 2026-07-08: Added function-level shim/delegation coverage for `extract_redefinitions` and `extract_multiplicities`.

---

## Re-review

Approved. The revised spec now gives design a clear contract: move the reusable primitive hierarchy layer and neutral dataclasses, keep design overrides, usage/type indexing, orchestration, aggregation, scoping, and module construction in sysml-codegen. The prior findings are resolved by explicit helper/model boundaries, implementation-site TYPE_MAP inventory, per-idiom profile dispositions, required-reading coverage, and function shim/delegation coverage.

---

**Verdict:** Approve
**Next Steps:** Proceed to `$my-design` for `.project/active/hierarchy-primitives-models/design.md`. No item-level PR closeout; the whole PUSH-DOWN epic closes together.
