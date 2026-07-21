# Brief: Item 5 spec — Concrete Lowering: New Phase, Strict Resolution, Execution IDs

You are the spec stage for Item 5 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `spec.md` in `.project/active/constraint-lowering/`.

## Provenance
- Concept (owner-ratified): `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — "Concrete Lowering" + Required Invariants (Semantics and Identity; Graph and Evaluation) + S3/S4 results and carry-forwards (Appendix B).
- Epic Item 5: `.project/backlog/epic_constraint_execution.md`.
- **Upstream landed on the epic branches**: Item 1 (agentic-mbse, CERTIFIED — `ConstraintUsageFact` with tagged owner facts, actuals, operand leaf facts), Item 2 (agentic-mbse, implemented, audit in flight — `expression_ir.py`), Item 4 (this repo, CERTIFIED — `analysis/part_instance_index.py` with `AllOccurrencesResult` surfacing blocked defs), Item 6 (this repo, CERTIFIED — `ModuleKind` incl. `constraint`). agentic-mbse is the editable install at `~/1cfe/agentic-mbse` — read the real types.
- S4's test-only lowering path (`.project/active/spike-vertical-slice-constraint-execution/s4_lib.py`) is the proven shape being productionized.
- Memory (binding risk note): the F4-cutover lesson — the backtracker's entry-point fallback is NOT a drop-in for strict resolution (EP-key collapse risk); Item 5 builds one shared resolver seam with an explicit strict mode.

## Objective (from the epic)
Land the new lowering pipeline phase: expand assertions per concrete instance, strictly resolve actuals, join constraint roots before pruning, and mint deterministic execution IDs.

## Scope (epic Item 5 §1–5)
1. **Phase placement**: after aliases, output registry, and supplied-value materialization are final; before dependency backtracking.
2. **`ConcreteConstraint`**: source facts, resolved actuals, expected Boolean value, deterministic `constraint_id`, optional simple-inequality response metadata. Part-def-owned + inherited assertions expand once per concrete part instance (via Item 4's index); calc-def-owned once per concrete calc usage; direct-usage-owned expand once (Item 1's tagged owner semantics); an expected instance that cannot form is a validation error.
3. **Strict resolution** through one shared resolver seam with explicit strict mode: chain actuals via `OutputRegistry.scoped_lookup` in owner-instance scope; reference actuals against design attributes, minting `DESIGN_ATTRIBUTE` entry points in their derived groups; defaulted formals become overridable contract parameters retaining the modeled default; **unresolved = generation error, never synthesis**.
4. **Roots before pruning**: resolved constraint input channels join backtracking roots via the `_find_usage_for_channel` seam (S4 proved this exact seam).
5. **Identity**: `constraint_id` = source-local identity + concrete owner instance + membership kind + polarity, scoped to one fingerprint; collision = generation error; deterministic catalog ordering; optional author-controlled `tracking_key`; fixed-multiplicity siblings each get their own channels (S3 carry-forward (3)).

## Out of scope
Module/aggregator emission (Item 7); snapshot round-trip (Item 8); profile decisions (Item 3 gates upstream — but note the coordination seam: what reaches lowering is already profile-admitted).

## Success criteria (from the epic)
- S4's vertical-slice behavior reproduced by production code: control run prunes `cost_calc`; lowered run retains it via the constraint root only.
- V11 coverage and channel-reference validation pass on extended graphs; no fallback path executes for constraint actuals (probe: unresolvable actual → generation error naming the actual).
- IDs and catalog ordering byte-identical across repeated live loads; multiplicity siblings independently wired.
- Existing corpus (no constraints in executable profile) regenerates byte-identically.
