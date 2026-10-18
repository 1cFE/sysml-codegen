# Brief: /_my_spec for EXEC-SUBSET-CONTRACT Item 2a (sysml-codegen)

Write the spec at `.project/active/subset-profile-conformance/spec.md` in this repository (sysml-codegen, worktree on branch `subset-conformance`).

## The work item

agentic-mbse epic Item 2a: read `/home/reid/src/subset-conformance/agentic-mbse/.project/backlog/epic_executable-subset-contract.md`, sections "Design principles", "Success Criteria", "Item 2 … split", "Item 2a", "Item 2b" (for the boundary: 2b is out of scope here), "Owner decisions". Also read `.project/active/subset-profile-conformance/briefs/align.md` here: route, worktrees and reserved gates.

## Intent to serve

[AGENT] (ratified by owner) Prove, with evidence independent of the new screen, that the shared subset contract (agentic-mbse `src/agentic_mbse/sysml/subset_profile.py`, `SUBSET_PROFILE_VERSION = subset-profile/v1`) matches what this generator actually does, and make drift fail a test. Not the goal: test volume, or tests that check the screen against itself.

## Inputs Item 1 left you (agentic-mbse sibling worktree, `.project/completed/20261018_exec-subset-profile/`)

- `evidence/r3-proposal.md`: approved disposition (owner, 2026-10-18, "agreed on all"); every row routed to Item 2 is now 2a's. `part-multiplicity/nonunique` and `negative_bound` are retired (owner).
- `evidence/re-estimate.md`: the 2a work lines and their basis.
- `evidence/matrix.md`, `evidence/site-reconciliation.md`; site account `tests/fixtures/subset_profile/inventory/site_account.csv`; 80 probes under `tests/fixtures/subset_profile/probes/`; `evidence/acceptance.md`.
- `scripts/subset_profile/`: dev scripts whose evidence output defaults to Item 1's archive folder. Parameterize before reuse.
- Occurrence parity: `occurrence_parity.py`, `tests/helpers/occurrence_oracle_schema.py` (agentic-mbse); 73/73 parity at Item 1's close.
- agentic-mbse ADR 0001 (capability-policy ownership) and promise P-0001; sysml-codegen ADR 0012 and the unfiled amendment draft. agentic-mbse must never import sysml-codegen.

## Provenance of what I pass you

- `[OWNER]` the split, the three reserved gates (RG-1..3 in align.md), D1/D2/D3 in the epic, R3 approval.
- `[AGENT] (ratified by owner)` the silent-loss scope limit (known families only; general detector is a recorded limit).
- `[AGENT]` (mine, challengeable) the 17–27 day estimate; that the spec should be phaseable into independently auditable chunks because the item is large.

## What I need from the spec

- Requirements graded per the capture-fidelity vocabulary, each evaluatable by a test or a recorded artifact.
- An explicit treatment of every R3 row routed to Item 2: what outcome closes it (rule, reproduced gap with code, retired, deferred with owner).
- Where a requirement would need a generator behavior change, mark it as an RG-1 dependency and keep the rest of the spec independent of the answer.
- G1/G2: a requirement to run the `kerml-expert` semantics check (`.claude/agents/kerml-expert.md`) and record findings; the fix itself is RG-1.
- String metadata policy: requirement to produce fixtures and a recommendation for RG-2, not to decide.
- Scope boundaries against 2b (no `check` CLI, no preparation-path refactor, no snapshot authority work) and against Items 3–5.
- Quality bar: conformance tests must exercise the generator's own route with the new screen bypassed; each detector needs a witness and a detector-disable mutation that fails; no circularity.

Decide and record anything this brief and the epic leave open. Ask me only for what genuinely blocks.
