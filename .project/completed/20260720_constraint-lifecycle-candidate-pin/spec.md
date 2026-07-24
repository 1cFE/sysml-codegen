# Item 0: Compatible Candidate Pin

**Status:** Implementation-ready — owner simplified scope on 2026-07-19
**Epic:** `CONSTRAINT-LIFECYCLE-REMEDIATION`, Item 0, register row 0

## Purpose

Establish one committed agentic-mbse, sysml-codegen, and TEAx revision set that installs together
and gives later items stable hashes and a production-code baseline.

Item 0 is integration bookkeeping. It does not certify lifecycle behavior.

## Requirements

- **PIN-01 [NEED]** Keep the committed agentic-mbse work intact. The modeling-orchestrator commit
  `4ed2a07` may remain in the PR #11 candidate; no branch surgery or patch replay is required.
- **PIN-02 [NEED]** Reconcile the current local agentic-mbse tip `205debd` with the existing PR #11
  remote tip `54a95d2`, preserving both committed lines.
- **PIN-03 [NEED]** Use the existing agentic-mbse PR #11 first and sysml-codegen PR #9 second. Do
  not open replacement upstream PRs.
- **PIN-04 [INHERITED]** Select exact committed agentic-mbse, sysml-codegen, and TEAx revisions whose
  declared dependencies and lockfiles install together and select executable profile v4.
- **PIN-05 [INFERRED]** Run the smallest existing install/import/profile smoke checks needed to
  detect an incompatible pin. Later items own schema, runtime, catalog, and acceptance matrices.
- **PIN-06 [NEED]** Record production LOC by repository and touched subsystem before later
  remediation starts. Use one reproducible counting command and keep tests, fixtures, generated
  output, docs, and project artifacts separate from production code.
- **PIN-07 [INHERITED]** Record exact commits, package versions, lockfile digests, commands, and
  results. Label the record non-certifying; Item 13 performs lifecycle certification.
- **PIN-08 [NEED]** Do not re-audit completed superseded Items 1/2/4/6.

## Execution

1. Combine the current agentic-mbse local and remote PR lines with an ordinary merge or equivalent
   non-destructive reconciliation.
2. Resolve only real dependency/version/lock incompatibilities.
3. Build or install the three pinned repositories in an isolated environment and run narrow smoke
   checks for imports and profile-v4 selection.
4. Record the exact revision set, lock digests, and production LOC baseline in `evidence.md`.
5. Commit the Item 0 evidence. Do not push or update PRs during this local step.

## Success Criteria

- [ ] The agentic-mbse candidate contains both `205debd` and `54a95d2` histories.
- [ ] The selected agentic-mbse, sysml-codegen, and TEAx revisions install together.
- [ ] The intended executable profile v4 is selected by the pinned codegen candidate.
- [ ] Exact commits, lock digests, smoke commands/results, and production LOC baseline are recorded.
- [ ] No later lifecycle item or acceptance cell is claimed complete.

## Deliverable

- `.project/active/constraint-lifecycle-candidate-pin/evidence.md`
