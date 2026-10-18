# Orchestration Align record: EXEC-SUBSET-CONTRACT Item 2a

**Date**: 2026-10-18
**Input**: agentic-mbse `.project/backlog/epic_executable-subset-contract.md` Item 2 (split into 2a and 2b at agentic-mbse `71f59820`, branch `subset-conformance`).
**Owner reply to Align**: "ok I'm good with the split. and Item 1 is now merged. good with the rest, please proceed"

## Reading of the work

[AGENT] (ratified by owner, 2026-10-18) Item 1 wrote down what the generator accepts. Item 2 makes sysml-codegen prove the contract matches what the generator really does, then adds a read-only `check`. The aim is that a model the contract calls fine does not surprise anyone at generation time, not a box labelled "conformance tests".

## Route

- [AGENT] (ratified by owner) Item 2 splits: 2a conformance corpus and per-site codes (this item) first; 2b readiness check and snapshot authority later, specced separately.
- This run: spec → spec_review → design → design_review → plan → implement → audit for 2a. `close` and `pre_pr` are the owner's.
- Worktrees: sysml-codegen `/home/reid/src/subset-conformance/sysml-codegen` (branch `subset-conformance`, base `b5663c07`) and its sibling agentic-mbse `/home/reid/src/subset-conformance/agentic-mbse` (branch `subset-conformance`, base `ccd57d83` = Item 1 merge, PR #30). The codegen path dependency `../agentic-mbse` resolves to the sibling. A concurrent session runs epic Item 4 in `/home/reid/src/agentic-mbse`; this run does not touch that checkout or `/home/reid/src/sysml-codegen`.

## Reserved gates (owner decides; the run parks them)

- **RG-1**: any change to what the generator accepts or refuses, including a G1/G2 fix after the `kerml-expert` semantics check. The run may do the check and record findings.
- **RG-2**: String metadata policy (epic open decision 3). The run brings fixtures and a recommendation.
- **RG-3**: merges, PRs and filing the ADR 0012 amendment (draft at agentic-mbse `.project/completed/20261018_exec-subset-profile/evidence/adr-0012-amendment-draft.md`).

## Settled at Align

- [AGENT] (ratified by owner, 2026-10-18) The silent-loss requirement covers the known families, each with an explicit presence/absence model and an admitted control. A general detector for unknown losses is a recorded limit, not an acceptance gate.
- Item 4's hazard reference is not available yet; the POSITIONAL-FORMAL-REDEFINITION link is recorded as pending.
