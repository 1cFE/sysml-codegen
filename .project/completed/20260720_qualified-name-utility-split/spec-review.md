# Spec Review: Qualified-Name Utility Split

**Spec:** `.project/active/qualified-name-utility-split/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec-review/SKILL.md`
**Review File:** `.project/active/qualified-name-utility-split/spec-review.md`
**Date:** 2026-07-08

---

## Reality Check

Sound. The revised spec is about the right PUSH-DOWN item and is now precise enough to use as
the design contract. It keeps the split line faithful to the epic: SysML-general name helpers move
to agentic-mbse, codegen identifier builders and alias/scoping policy stay local, sysml-codegen
re-exports remain permanent compatibility surfaces, and the work stays on the full PUSH-DOWN epic
branch without item-level PR closeout.

---

## Audit

### Lens 1 - Faithfulness

**L1-1 - Direct claim:** The spec now names the exact moved public helper set:
`sanitize_name`, `build_element_qualified_name`, `sysml_to_python_qualified_name`,
`sanitize_qualified_name`, `python_to_sysml_qualified_name`, and `extract_simple_name`
(`.project/active/qualified-name-utility-split/spec.md:30`,
`.project/active/qualified-name-utility-split/spec.md:66`). That matches the general public
subset in `src/sysml_codegen/core/qualified_names.py:14`, `:48`, `:112`, `:117`, `:133`, and
`:138`. The private owner-chain helper remains implementation detail, and the spec does not
accidentally require it as public API.

**L1-2 - Direct claim:** The codegen-owned exclusions are correctly preserved. The spec keeps
`build_parameter_qualified_name`, `get_module_name`, `get_channel_name`, and `owning_part_leaf`
local (`.project/active/qualified-name-utility-split/spec.md:36`,
`.project/active/qualified-name-utility-split/spec.md:63`), matching the codegen-specific
builders and alias/scoping helper in `src/sysml_codegen/core/qualified_names.py:97`, `:102`,
`:107`, and `:149`.

**L1-3 - Direct claim:** The stale truth-debt artifact path from the prior review is fixed. The
spec points at `.project/completed/20260708_epic_truth_debt.md`
(`.project/active/qualified-name-utility-split/spec.md:121`), and that file exists.

### Lens 2 - Problem & Approach

**L2-1 - Direct claim:** The spec now captures the sharp `sanitize_qualified_name` boundary that
design must preserve. The requirement says the helper applies exactly once at the `::` to `__`
boundary and must not run over an already `__`-joined name
(`.project/active/qualified-name-utility-split/spec.md:70`). That matches the current helper
contract in `src/sysml_codegen/core/qualified_names.py:117`.

**L2-2 - Direct claim:** The public-export question is correctly deferred to design. The
agentic-mbse package already re-exports shared SysML helpers from `agentic_mbse.sysml.__init__`,
so adding qualified-name exports is a plausible continuation, but the spec does not need to lock
that packaging choice before design (`.project/active/qualified-name-utility-split/spec.md:85`,
`:103`; `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/__init__.py:1`).

### Lens 3 - Pipeline Risk

**L3-1 - Direct claim:** The checking-profile close-out is now strong enough for downstream work.
The spec requires a helper-by-helper table with `DONE`, `EXISTING`, `NEW RULE`, or `FILED`, and
requires every filed row to name the backlog item, rule, fixture shape, severity, and rationale
(`.project/active/qualified-name-utility-split/spec.md:43`). That is the right contract shape for
the epic's "update or file validation rules" requirement (`.project/backlog/epic_push_down.md:158`).

**L3-2 - Direct claim:** The existing agentic-mbse `ITEM-SYNC-C8` row is no longer at risk of
being duplicated silently. The spec requires it to be updated, superseded, discharged, or
explicitly kept with a reason (`.project/active/qualified-name-utility-split/spec.md:46`,
`:79`). That matches the backlog row's current dependency on a shared sanitizer
(`/home/reid/1cfe/agentic-mbse/.project/backlog/BACKLOG.md:118`).

**L3-3 - Direct claim:** The INV-5/no-churn requirement is now concrete enough. The spec requires
coverage for non-empty output, `.isidentifier()`, Python-keyword safety, and no dangerous
fixture-corpus identifier churn for already-safe names
(`.project/active/qualified-name-utility-split/spec.md:39`). Those properties line up with
`sanitize_name`'s current guarantees (`src/sysml_codegen/core/qualified_names.py:14`) and the
committed fixture-corpus no-churn checks in `tests/conformance/test_sanitize_invariance.py:144`.

**L3-4 - Direct claim:** The branch and closeout rules are clear enough for this stage. The spec
states that Item 2 continues on top of certified Item 1 on the full PUSH-DOWN epic branch and
forbids item-level PR closeout (`.project/active/qualified-name-utility-split/spec.md:7`, `:24`,
`:57`, `:99`). No remaining process ambiguity should block design.

### Lens 4 - Hygiene

No material hygiene issues. The spec is short, the reading list is executable, and the current
branch wording is explicit enough for a stacked epic branch.

### Lens 5 - Reader Comprehension

No material comprehension blockers. A reviewer can see the split line, the behavior-preservation
requirements, and the design-stage choices in one pass.

---

## Engagement Summary

**Overall take:** The revised spec is ready to become the design contract. The prior blockers were
fixed: the helper set is exact, `sanitize_qualified_name` has its apply-once/non-reentrant boundary,
the checking-profile close-out is helper-by-helper, `ITEM-SYNC-C8` must be dispositioned, and the
fixture-corpus no-churn requirement is explicit.

**Here's what I need you to weigh in on:**

No reviewer decisions are needed before design. The remaining choices are minor and objectively
fixable in design: whether to re-export from `agentic_mbse.sysml.__init__`, which profile hazards
become immediate rules versus named backlog rows, and which sysml-codegen tests stay as re-export
pins.

---

## Resolutions

- **Prior L1-2 / L2-2:** Resolved by naming the exact moved helper set and explicitly preserving
  `sanitize_qualified_name` as a shared, apply-once boundary helper.
- **Prior L3-1 / L3-2:** Resolved by requiring a helper-by-helper checking-profile disposition
  table and an explicit `ITEM-SYNC-C8` disposition.
- **Prior L3-3:** Resolved by spelling out the INV-5 properties and the no-dangerous-fixture-churn
  requirement.
- **Prior L4-1 / L1-3:** Resolved by clarifying branch metadata and correcting the truth-debt
  artifact path.

---

**Verdict:** Approve
**Next Steps:** Proceed to `my-design`. The design should carry the remaining deferred choices
explicitly, but they do not require another spec revision.
