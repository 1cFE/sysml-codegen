# Brief: Item 14 design — Migration, Docs, and IFE Acceptance

You are the design stage for Item 14 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents (your spec stage tripped this — everything must be inline tool calls).
- Do NOT run `git commit` — the orchestrator commits.
- An Item 13 implement session may be committing to this tree — write ONLY design.md (+ CURRENT_WORK entry); touch no code.
- Artifact: `design.md` in `.project/active/constraint-migration-acceptance/`.

## Input
- Spec (committed): `.project/active/constraint-migration-acceptance/spec.md`.
- **The fusion-tea access gap is CLOSED**: `.project/reference/fusion-tea-ife-sweep/` holds the harness copy + orchestrator-verified FACTS.md — including the deletion target (`sweep_ife.py:82`, `viable = eta_g > ETA_G_MIN`), the LCOE overlay that STAYS hand-coded (it is study policy, not a modeled constraint), the outputs location, and one real hazard: the hand-coded strict `>` vs the modeled `>=` — design the acceptance comparison to detect a boundary point and surface it rather than paper over it.
- The gain-gap prerequisite: Item 5's plan third pass (the materializer miss on `:>> gain = 80.0` at hif_plant.sysml:87); Item 8's GRANDFATHERED set.

## Design guidance (orchestrator, agent-grade)
- Workstream order: (1) gain-gap fix in materialize_supplied_values + re-land the two grandfathered fixtures lowered (their own byte-identity/diff review); (2) drop-manifest retirement + 1:1 mapping test + REQ-EXT-09-family re-anchor; (3) docs across the three repos (enumerate the exact files: authoring guidance, architecture refs, verification matrix rows — use the doc surfaces the spec verified); (4) the IFE acceptance run (regenerate fusion-tea package lowered → replace the rule with the study-layer evaluation → row-by-row classification comparison → prepare-once benchmark); (5) the three small seams.
- The acceptance's execution home: fusion-tea's harness dir, driven via teax's study CLI/API (certified Items 10–12). Design the exact comparison artifact (a table: grid point → old viable → new verdict → match) committed as the acceptance report.
- Cross-repo work splits: sysml-codegen (gain fix, manifest retirement, docs), agentic-mbse (docs, L4/L6 doc rows), teax (docs), fusion-tea (sweep replacement + report). Name which sessions/repos each phase runs in — the orchestrator sequences them.
- A design_review follows given the epic-closing stakes; make the acceptance comparison and gain-fix blast radius explicit.
