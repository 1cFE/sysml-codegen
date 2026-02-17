# PROMPT: Plan a Refactor Component

---

## Your Task

You are planning the implementation of component **{COMPONENT_CODE}** for the sysml-codegen refactor.

Your job is to produce a high-quality, validated implementation plan — NOT to write any code.

## Step 1: Load Context

Read these files in order:

1. `.project/concepts/refactor-design-intent/IMPLEMENTATION_PLAN.md` — overall phasing and sequence
2. `.project/concepts/refactor-design-intent/COMPONENT_CHECKLIST.md` — find the entry for {COMPONENT_CODE}
3. The design intent doc(s) referenced in the checklist entry (e.g., `10-output-registry.md`)
4. `.project/concepts/refactor-design-intent/component-loop.md` — the plan template

Check `IMPLEMENTATION_PLAN.md` for:
- Prerequisites: are upstream components complete?
- Accumulated learnings that affect this component (bottom of file)
- Design doc amendments that change requirements (bottom of file)

Also read the current source files listed in the checklist entry ("Current location") to understand what exists today.

## Step 2: Design Consistency Review

This is the most important step. Before filling in the template, critically evaluate:

### a) Are the acceptance criteria testable?
For each AC in the checklist, ask: "Can I write a test for this using real data (no mocks) that has a clear pass/fail?" If not, the AC needs to be refined. Document what's wrong and propose a fix.

### b) Are the requirements internally consistent?
Read every REQ-XX-NN in the design intent doc. Do any contradict each other? Do any contradict requirements from upstream/downstream components? Check the "Related Documents" footer for cross-cutting concerns.

### c) Do the interfaces match?
Check that the inputs this component expects match what upstream components actually produce. Check that the outputs match what downstream components consume. Use the data model doc (09-data-models.md) as the reference.

### d) Are there gaps?
Is there behavior the component needs that isn't covered by any requirement or AC? Common gaps: error handling, edge cases in real fixture data, ordering assumptions.

### e) Check accumulated learnings
Read the Learnings sections from completed components in `.project/active/*/plan.md` (if any exist). Did any prior component discover something that changes what this component should do?

## Step 3: Fill the Template

Copy `.project/concepts/refactor-design-intent/component-loop.md` to `.project/active/{component-name}/plan.md`.

Fill in every section:

- **Assessment**: What the component does, current state, design consistency findings
- **Spike**: Make an explicit SPIKE or SKIP decision with rationale. Spike if there are unknowns that could invalidate the build plan. Skip if the design is clear and the existing code confirms it.
- **Test Plan**: Concrete test cases with real assertions. Every REQ must map to at least one test. Use fixture model names (sample_model, solar_battery_model, catf_mfe_model, attr_expr_probe) — never "mock data."
- **Build Plan**: Specific files and changes. Reference line numbers from the current source.
- **Validation**: Copy the AC from the checklist as checkboxes.
- **Learnings**: Leave blank (filled during/after build).

## Step 4: Self-Review

Before finishing, verify:

- [ ] Every REQ-XX-NN from the design intent doc appears in the test plan table
- [ ] Every AC from the checklist appears in the validation section
- [ ] No test case mentions "mock", "patch", "MagicMock", or "stub" (except SysIDE adapter boundary)
- [ ] Spike decision has a concrete rationale (not "seems fine")
- [ ] Build plan references specific files and the changes needed
- [ ] Any issues found in the design consistency review are documented with resolutions
- [ ] If design docs need updating, this is noted (but NOT done — that happens in the LEARN phase)

## Constraints

- **DO NOT write any code.** Not even test stubs. That is the build prompt's job.
- **DO NOT modify design intent docs.** Flag issues for the LEARN phase.
- **DO NOT skip the design consistency review.** This is the whole point of separating plan from build.
- If you find a blocker (missing upstream component, contradictory requirements), document it clearly and stop. Do not plan around a known inconsistency.

## Output

The deliverable is: `.project/active/{component-name}/plan.md`
It should be complete enough that a different agent context can pick it up and build from it without needing to re-read the design docs.
