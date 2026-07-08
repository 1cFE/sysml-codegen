# Design Review: Qualified-Name Utility Split

**Design:** `.project/active/qualified-name-utility-split/design.md`
**Spec:** `.project/active/qualified-name-utility-split/spec.md`
**Review File:** `.project/active/qualified-name-utility-split/design-review.md`
**Date:** 2026-07-08

---

## Fundamental Assessment

Sound. The design chooses the simple approach the spec calls for: move one pure helper subset into
`agentic_mbse.sysml.qualified_names`, keep codegen naming policy in sysml-codegen, and preserve the
old sysml-codegen import paths through shims. I do not see a simpler design that meets the
cross-repo reuse goal without either duplicating sanitizer behavior or making agentic-mbse depend on
sysml-codegen.

The abstraction earns its place. A new shared module is enough; the design does not introduce new
classes, registries, adapters, or indirection beyond package exports and a compatibility shim.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Pass

The design covers every hard requirement in the spec.

- The moved public API is exactly the six helpers named in the spec:
  `sanitize_name`, `build_element_qualified_name`, `sysml_to_python_qualified_name`,
  `sanitize_qualified_name`, `python_to_sysml_qualified_name`, and `extract_simple_name`
  (`design.md:79`, `spec.md:30`, `spec.md:66`).
- The four codegen-owned helpers stay local:
  `build_parameter_qualified_name`, `get_module_name`, `get_channel_name`, and
  `owning_part_leaf` (`design.md:82`, `design.md:170`, `spec.md:36`).
- The permanent compatibility surface is explicit. `sysml_codegen.core.qualified_names` remains
  the old import path, and `sysml_codegen.core` keeps its existing package exports unless
  implementation deliberately adds and pins `sanitize_qualified_name` (`design.md:87`,
  `design.md:111`, `design.md:193`).
- The checking-profile close-out is present and includes `ITEM-SYNC-C8` rather than filing a
  duplicate row (`design.md:153`, `design.md:168`, `design.md:175`; `spec.md:43`, `spec.md:79`).
- The no-baseline-churn requirement is carried into validation with `git diff -- tests/fixtures`
  as a hard byte-identity check (`design.md:265`, `design.md:267`).

### 2. Pattern Consistency

**Assessment:** Pass

The design follows the pattern established by PUSH-DOWN Item 1. Shared SysML helpers are exposed
from an agentic-mbse `sysml` module and re-exported from `agentic_mbse.sysml.__init__`
(`design.md:84`, `design.md:107`). The existing agentic-mbse package already re-exports shared
expression helpers through that surface, so qualified-name helpers fit the local API shape
(`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py:12`).

The shim pattern is also consistent with compatibility needs. Existing sysml-codegen callers import
from `sysml_codegen.core.qualified_names` across extraction, analysis, resolution, orchestration,
and tests, so keeping that module as the stable surface is the right choice.

### 3. Abstraction Quality

**Assessment:** Pass

The module boundary is at the right level. The six moved helpers operate on SysML names, ownership
chains, and separator conversions. The four retained helpers turn those names into generated
artifacts or alias scopes. That split matches the implementation: `sanitize_name` and
`build_element_qualified_name` are pure name/owner helpers (`qualified_names.py:14`,
`qualified_names.py:48`), while `get_module_name`, `get_channel_name`, and
`build_parameter_qualified_name` encode ADR-003 artifact naming (`qualified_names.py:97`,
`qualified_names.py:102`, `qualified_names.py:107`), and `owning_part_leaf` exists for
EXPOSE_PURE alias/scoping behavior (`qualified_names.py:149`).

The only small caution is that the research range in the design says `qualified_names.py:14`
through `:146` is the shared subset, but that range includes the three codegen-owned builders at
`:97` through `:109`. The next bullet corrects the split, so this is a documentation precision
issue, not a design flaw.

### 4. Duplication Avoidance

**Assessment:** Pass

The design removes sanitizer duplication by making agentic-mbse the implementation owner and
sysml-codegen the compatibility consumer. It avoids the bad alternative: copying codegen's
sanitizer into agentic-mbse validation, which is exactly why `ITEM-SYNC-C8` was deferred.

The test strategy duplicates only compatibility assertions, not behavior. Object-identity pins for
the six moved helpers are the right way to prove the shim uses the shared implementation
(`design.md:190`).

### 5. Data Structure Clarity

**Assessment:** Pass

No new data structures are introduced. The signatures are explicit and unchanged
(`design.md:204`). The design keeps the private owner-chain helper private and forbids exporting it
from either repo (`design.md:217`), which prevents a new semi-public data-shaping API from forming
by accident.

### 6. Route Safety

**Assessment:** Pass

No HTTP routes or endpoint routing are involved. The relevant "routing" surface is import routing,
and that is explicit: shared helpers route through `agentic_mbse.sysml.qualified_names`, old
sysml-codegen imports route through `sysml_codegen.core.qualified_names`, and
`sysml_codegen.core.__init__` preserves its current export set unless intentionally expanded
(`design.md:111`, `design.md:193`).

### 7. Bets & Decisions Integrity

**Assessment:** Pass

The stated bets are real claims about the codebase, not implementation choices dressed up as bets.

- B1 is the main boundary bet. The current implementation supports it: the six moved helpers are
  general name operations, while the excluded helpers are generated-artifact or alias policy
  (`design.md:68`, `qualified_names.py:97`, `qualified_names.py:149`).
- B2 is the behavior-preservation bet. The design backs it with identity pins, full suites, and
  fixture byte-identity checks (`design.md:132`, `design.md:190`, `design.md:259`,
  `design.md:265`).
- B3 is honest about the validation home. agentic-mbse Level 6 already has qualified-name checks,
  but it currently uses local format checks rather than the shared sanitizer
  (`design.md:47`; `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:144`).

The main hidden bet is that a model-wide sibling-name collector may not be cheap enough to build
inside this item. The design surfaces that through D5 and the `ITEM-SYNC-C8` fallback instead of
pretending the WARN is guaranteed to land (`design.md:94`, `design.md:168`, `design.md:175`).
That is acceptable for planning because the fallback names the rule, fixture shape, severity, and
rationale.

### 8. Reader Comprehension

**Assessment:** Pass

The design is readable and gives the mental model before the mechanism. The core concept states the
boundary plainly: agentic-mbse owns SysML name normalization, sysml-codegen composes it into
generated artifacts (`design.md:57`). The implementation handoff is concrete enough for a planner
to sequence the work without reconstructing the design intent (`design.md:273`).

---

## Issues by Severity

### Critical

- None.

### Major

- None.

### Minor

- **Imprecise shared-subset source range:** The research note says `qualified_names.py:14` through
  `:146` is shared, but that range includes codegen-owned builders at `:97` through `:109`.
  The surrounding design resolves the split correctly, so this does not block implementation.
  Dimension: Abstraction Quality.
- **C8 implementation remains conditional:** The design allows either implementing the WARN or
  updating `ITEM-SYNC-C8` if the sibling collector is too broad. This is realistic, but
  implementation must not mark the profile loop closed unless the final artifact records one of
  those two concrete outcomes. Dimension: Bets & Decisions Integrity.

---

## Recommendations

1. In planning, make the first agentic-mbse phase land `qualified_names.py`, package exports, and
   pure tests before touching sysml-codegen. That de-risks the import direction and gives the shim a
   stable target.
2. Add an explicit non-reentrant test for `sanitize_qualified_name`: a `::` input sanitizes once,
   and applying the helper to an already `__`-joined value collapses the separator. That pins the
   current warning as observable behavior rather than just doc text.
3. Keep fixture-corpus scans that need sysml-codegen machinery in sysml-codegen. Only pure segment
   tables or pure helper tests should move into agentic-mbse.
4. For `ITEM-SYNC-C8`, require implementation notes to say exactly one of: `NEW RULE` with the
   sibling-scope positive and unrelated-namespace negative fixtures, or `FILED` with the existing
   backlog row updated to "shared sanitizer landed; needs sibling-name collector."

---

## Resolutions

- No user resolutions recorded. This non-interactive review has no blocking findings.

---

**Overall:** Approve
**Next Steps:** Proceed to `my-plan` or `my-implement` for PUSH-DOWN Item 2. The implementation
agent should carry the minor recommendations into the plan; the reviewer does not edit the design.
