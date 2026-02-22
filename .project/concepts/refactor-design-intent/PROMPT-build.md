# PROMPT: Build a Refactor Component

---

## Your Task

You are building (or continuing to build) the component at `.project/active/{COMPONENT_NAME}/plan.md`.

## Step 1: Load the Plan

Read `.project/active/{COMPONENT_NAME}/plan.md` completely.

Pay attention to:
- **Status**: Which phase is the component in? (SPIKE / TEST / BUILD / VALIDATE)
- **Progress Log**: What did the last session do? Where did it stop? What should you do first?
- **Gates**: Has the current phase's gate been satisfied? If yes, advance to the next phase.

Also read:
- `CLAUDE.md` for environment setup and commands
- `.project/concepts/refactor-design-intent/IMPLEMENTATION_PLAN.md` — check Accumulated Learnings and Design Doc Amendments (bottom of file) for anything new since the plan was written

## Step 2: Identify Your Work

Based on the plan's status and progress log, determine what to do next:

### If status is SPIKE:
- Execute the spike approach described in the plan
- Fill in "Spike Findings" and "Spike Impact on Plan"
- If findings change the test or build plan, update those sections
- When spike questions are answered, update status to TEST
- Add a Progress Log entry

### If status is TEST:
- Write the test file and all test cases listed in the test plan
- Use real fixture data as specified — no mocks
- Run the tests to confirm they execute (most should FAIL — that's expected)
- When the gate is satisfied (test file exists, tests run, no mocks), update status to BUILD
- Add a Progress Log entry

### If status is BUILD:
- Implement the changes listed in the build plan
- After each logical chunk, run the relevant tests to check progress
- When all tests pass, run the full suite: `uv run pytest tests/`
- When the gate is satisfied (all tests pass, no regressions, lint clean), update status to VALIDATE
- Add a Progress Log entry

### If status is VALIDATE:
- Work through every checkbox in section 5
- Re-read the design intent doc(s) and cross-check the implementation
- If everything passes, update status to DONE
- Fill in section 6 (Learnings): findings, design doc updates needed, cross-component impact, deviations
- Update `.project/concepts/refactor-design-intent/IMPLEMENTATION_PLAN.md`:
  - Mark the component's phase step as complete
  - Add any learnings to the Accumulated Learnings section
  - Add any design doc amendments to the Design Doc Amendments section
  - Update the Test Count Tracking table
- Add a final Progress Log entry

## Step 3: If You Can't Finish

If you hit the end of your context window or encounter a blocker:

1. **Save your progress**: Update all checkboxes in the plan to reflect what's done
2. **Add a Progress Log entry** with:
   - What you accomplished
   - Exactly where you stopped (be specific: file, function, test case)
   - What the next session should do first
   - Any blockers
3. **Do not leave partially written code uncommitted** — either finish the current logical unit or revert

## Constraints

- **Follow the plan.** If the plan says to modify file X, modify file X. If you think the plan is wrong, document why in the Progress Log but don't silently deviate.
- **No mocks.** If a test needs data you don't have, document it as a blocker.
- **Tests before code** in the TEST→BUILD transition. Don't skip ahead.
- **Update the plan.md** after every significant chunk of work. This is how the next context picks up.
- **Don't modify design intent docs.** If you find issues, note them in section 6 (Learnings) for a future planning session to address.

## Output

Your deliverable is working code with passing tests AND an updated plan.md that reflects exactly what was done, what remains, and what was learned.
