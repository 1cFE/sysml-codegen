# Component Implementation Template

> Copy this file to `.project/active/{component-name}/plan.md` and fill in all sections.
> This is the single source of truth for the component's state across agent contexts.

---

# Component: {COMPONENT_NAME} ({CODE})

**Status**: PLANNING | SPIKE | TEST | BUILD | VALIDATE | DONE
**Created**: {date}
**Last updated**: {date}
**Updated by**: {agent context description}

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — {CODE}
- **Design intent**: {list of doc numbers and filenames}
- **Requirements**: {REQ-XX-01 through REQ-XX-NN}
- **Depends on**: {list of component codes that must be complete first, or "none"}

---

## 1. Assessment

### What This Component Does
{1-3 sentences: what it is, what it consumes, what it produces}

### Current State
- **Exists?** {yes (file path) | no (needs creation) | partial (explain)}
- **Needs extraction/refactoring?** {describe structural changes needed}
- **Current test coverage**: {describe existing tests, if any}

### Design Consistency Check
{This is the critical quality gate from PROMPT-plan. Document the review here.}

- [ ] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [ ] AC are consistent with the requirements in the design intent doc(s)
- [ ] No contradictions with other component specs
- [ ] Input/output interfaces match what upstream/downstream components expect
- [ ] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**
{List any inconsistencies, ambiguities, or gaps. For each: what the issue is, how it was resolved, whether design docs need updating.}

### Risks & Unknowns
{What could go wrong? What don't we know? What needs spiking?}

---

## 2. Spike

**Decision**: SPIKE | SKIP
**Rationale**: {Why spike or skip. Reference specific unknowns from Assessment.}

### Spike Questions (if spiking)
1. {Question to answer}
2. {Question to answer}

### Spike Approach
{What to prototype, what to measure, how to evaluate}

### Spike Findings
{Filled in after spike. Concrete answers to each question above.}
{Include code snippets, measurements, or observations that inform the build.}

### Spike Impact on Plan
{Did spike findings change the test plan or build plan? Document changes.}

---

## 3. Test Plan

**Test file**: `tests/conformance/test_{name}.py`
**Fixture data**: {which extraction snapshots / fixture models are used}

### Test Cases

> Every requirement (REQ-XX-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_xx_01_...` | REQ-XX-01 | {concrete assertion} |
| `test_req_xx_02_...` | REQ-XX-02 | {concrete assertion} |
| ... | ... | ... |

### Test Infrastructure Needed
{Any fixtures, helpers, or setup needed that doesn't exist yet}

### Gate: Ready for BUILD
- [ ] Test file exists with all test cases written
- [ ] Tests run (expected: most/all FAIL at this point)
- [ ] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| `path/to/file.py` | {description} | {links to requirement} |
| ... | ... | ... |

### Files to Create
| File | Purpose |
|------|---------|
| `path/to/new_file.py` | {description} |
| ... | ... |

### Implementation Notes
{Key decisions, patterns to follow, gotchas from spike or design review}

### Gate: Ready for VALIDATE
- [ ] All test cases pass
- [ ] No regressions in full test suite (`uv run pytest tests/`)
- [ ] Lint clean (`uv run ruff check src/`)

---

## 5. Validation

- [ ] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [ ] Every REQ-XX-NN has at least one passing test
- [ ] Full test suite passes (record count: ___ tests, 0 failures)
- [ ] Cross-check: re-read design intent doc, verify implementation matches
- [ ] No unresolved TODOs or FIXMEs in new/modified code

### Baseline Impact
{Did this component change any output baselines? If yes, document what changed and why.}

---

## 6. Commit

**Branch**: `refactor/{component-name}`
**Commit convention**: one commit per component, message references component code

- [ ] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor({CODE}): {one-line summary}

  - Tests: {N} new conformance tests in tests/conformance/test_{name}.py
  - Refs: {REQ-XX-01 through REQ-XX-NN}
  - Design intent: {doc number(s)}
  ```
- [ ] Committed successfully

---

## 7. Learnings

### Findings
{What did we learn during implementation that wasn't obvious from the design docs?}

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| {doc number} | {change needed} | {finding that triggered it} |

### Cross-Component Impact
{Did anything discovered here affect the plan for other components?}
| Component | Impact | Action needed |
|-----------|--------|---------------|
| {code} | {what changed} | {what to do about it} |

### Deviations from Plan
{Where did the actual implementation differ from the plan? Why?}

---

## Progress Log

> Each agent context that does work on this component adds an entry here.
> This is how the next context knows where to pick up.

### Session: {date} — {brief description}
**Phase**: {which phase was worked on}
**Work done**:
- {what was accomplished}
**Stopped at**: {exactly where work stopped — be specific}
**Next step**: {what the next context should do first}
**Blockers**: {anything preventing progress, or "none"}
