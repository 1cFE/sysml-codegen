# Brief: Item 4 design — Part-Instance Index

You are the design stage for Item 4 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design.md` in `.project/active/part-instance-index/`.

## Input
- Spec (committed, orchestrator-accepted): `.project/active/part-instance-index/spec.md`. Honor its provenance tags; its Open Questions are yours to decide and record.
- Original stage brief: `.project/active/part-instance-index/briefs/spec.md` (context + required reading).
- S3 probe + fixture: `.project/active/spike-concrete-expansion-instance-index/` — the probe's subtype-closure projection is a proven starting shape; the fixture model is promotable to a test fixture.

## Design guidance (orchestrator, agent-grade)
- The index must be a clean, separately testable module — Item 5 (lowering) is its only planned consumer, but design the API so it doesn't presume constraint-specific callers (it's a part-structure fact provider).
- Decide and record: module placement, API shape (inputs: what part-structure facts; outputs: instance paths + multiplicity occurrences with owning-def+feature keys), determinism mechanism (ordering guarantee), diagnostic type for non-finite cardinality, and how the S3 fixture becomes a kept test.
- The "additive, byte-identical" `[HARD]` constraint means: no changes to existing discovery call paths in this item; the index is new code beside them. Item 5 wires it in.
- A skeptical design_review follows; make the risky parts explicit (subtype-closure traversal against SysIDE heritage APIs, retyped-path dedup rule, occurrence identity).
