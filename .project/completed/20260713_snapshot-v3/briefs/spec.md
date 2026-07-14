# Brief: Item 8 spec — Snapshot v3: Constraint Facts Load-Bearing

You are the spec stage for Item 8 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `spec.md` in `.project/active/snapshot-v3/`.

## Provenance
- Concept (owner-ratified): Required Invariants (snapshot bullets) + S3/S4 results and carry-forwards.
- Epic Item 8: `.project/backlog/epic_constraint_execution.md`.
- **Certified upstream**: Item 1 (the versioned facts JSON — `constraint-facts/v1` envelope with `expression-ir/v1` predicate sub-document; Item 8 pins BOTH versions, per Item 1's design D9 and its amended forward-record), Item 5 (lowering + the `lower_constraints_enabled` transitional flag).

## Named responsibilities this item inherits from the run (all recorded in Item 5's plan/audit)
1. **The default flip**: `build_pipeline_context(lower_constraints_enabled=...)` defaults False today because snapshots can't carry facts. THIS item makes facts load-bearing in snapshots, proves live/snapshot parity for a constraint-bearing fixture, and FLIPS THE DEFAULT under that parity gate. The 22 previously-measured live/snapshot divergences become the parity test's baseline expectation to eliminate.
2. **The hif_plant `gain` handoff**: a top-level design-instance self-redefinition the supplied-value materializer doesn't synthesize (hierarchy-extraction gap, recorded in Item 5's plan third pass). When the default flips, hif_plant's admitted constraint resolution hits it. Spec its disposition: fix the extraction gap here, or block that fixture's constraint with a named diagnostic and hand to Item 14's migration — decide from evidence, record loudly.
3. Corpus re-capture discipline: timestamp-only churn check + revert (memory: byte-identity captured_at churn); review diffs deliberately (known pre-existing drift: deep_cross_scope, ife_plant stale baselines).

## Scope (epic Item 8 §1–4)
1. Serialize Item 1's fact section (+ lowering-relevant fields) into the extraction snapshot; bump `snapshot_format_version`.
2. Rejection semantics: old version rejected by the existing hard-gate; a current-version snapshot missing the constraint-facts section fails with a re-capture instruction — never loads as an empty catalog.
3. Live/snapshot parity: IDs and catalog ordering byte-identical through `generate --from-snapshot`; serialization fidelity a named property (S4 carry-forward (3)).
4. Corpus re-capture under the byte-identity discipline.

## Out of scope
The facts schema itself (Item 1); graph rebuild beyond wiring facts in; Item 7's emission (coordinate: the parity fixture needs Item 7's generation if sequenced after — spec the dependency direction explicitly; if Item 7 hasn't landed when this implements, parity is proven at the ComputationGraph/catalog level and re-proven at the artifact level in Item 7's wake).

## Success criteria (from the epic)
- Both rejection cases fire with re-capture messages (kept tests, mirroring S3's strict boundary).
- A constraint-bearing fixture generates byte-identically live and from snapshot.
- Re-captured corpus shows only expected diffs; conformance suite green.
