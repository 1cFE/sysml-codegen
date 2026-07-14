# Brief: Item 5 design — Concrete Lowering

You are the design stage for Item 5 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design.md` in `.project/active/constraint-lowering/`.

## Input
- Spec (committed, review-revised): `.project/active/constraint-lowering/spec.md` — four-kind dispatch, ordered resolution, LocationFact identity, dual axes, phase call-site (build_pipeline_context Step 5.65→7) are fixed. Open Questions (resolver-seam factoring, constraint_id encoding, tracking_key surface, modeled-default representation, per-occurrence channel resolution, Item 5/7 line) are yours to decide and record.
- Landed types: `.project/reference/agentic-mbse-landed/` (+ the editable install for truth).
- S4's proven code: `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py` — the shape being productionized.
- Item 4's index: `analysis/part_instance_index.py` (AllOccurrencesResult surfaces blocked defs — lowering must turn a blocked constraint-owning def into a validation error naming it, never a skip).
- The backtracker fallback (`analysis/dependency_backtracker.py`) is NOT reusable for strict resolution — design the shared resolver seam with explicit strict mode (memory: F4 EP-key collapse).

## Design guidance (orchestrator, agent-grade)
- Decide and record all spec Open Questions with rejected alternatives. For constraint_id encoding: deterministic, human-scannable-prefix + hash-suffix shapes have precedent in this repo — check existing ID minting idioms and match.
- Design ConcreteConstraint as graph-serializable data (Item 8 serializes it; Item 7 consumes it — keep both consumers' needs visible; coordinate with ComputationGraph model placement).
- The multi-instance and inline-form fixtures are new test assets — design them concretely (extend Item 4's promoted S3 fixture or author new; say which).
- A skeptical design_review follows; make the resolver-seam factoring and the Step 5.65→7 threading explicit with rejected alternatives.
