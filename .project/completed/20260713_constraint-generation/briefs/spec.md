# Brief: Item 7 spec — Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

You are the spec stage for Item 7 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `spec.md` in `.project/active/constraint-generation/`.

## RESOLVED OWNER GATE
**Module identity = class-per-concrete-assertion** — `[OWNER]` (Reid, 2026-07-12), decided WITH the measured scale evidence in this directory (`identity-gate-evidence.md` + `bench_aggregator_scale.py`). Record with that provenance. Module fusion is a documented far-future revisit, never first-scope.

## Provenance
- Concept (owner-ratified): `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — "Catalog, Evaluation, and Report" + Required Invariants + S2/S4 results and ALL their carry-forwards (Appendix B).
- Epic Item 7: `.project/backlog/epic_constraint_execution.md`.
- **Certified upstream on this branch**: Item 2 (expression_ir + parse_expression — the compiler's input is ConcreteConstraint.predicate_ir, a serialized IR string re-parsed at compile time; the serialization-equality same-IR arm applies here, per Item 3's design D7 and the wiring note in agentic-mbse's sysml-codegen-wiring.md), Item 3 (profile gates upstream), Item 5 (ConcreteConstraint with inputs/IDs/channels; `lower_constraints_enabled` transitional flag — Item 7's generation tests run with it True; the DEFAULT flip belongs to Item 8), Item 6 (ModuleKind.constraint / report_aggregator with fail-loud seams awaiting real emission).
- S4's test-only emitters (`.project/active/spike-vertical-slice-constraint-execution/s4_lib.py`) are the proven shapes being productionized; S2's Kleene compiler probe semantics are binding (concept Appendix B).

## Scope (epic Item 7 §1–5)
1. **Kleene predicate compiler** (codegen-owned, from S2): def-level compile with formal-named arguments, usage-level wiring; non-finite operand → leaf unknown; Kleene propagation; status vs expected value (negated polarity); margin only where structure fixes its sign, polarity-respecting; **boundary margin is zero with no meaningful sign** (S2 carry-forward (3)).
2. **Constraint modules**: `ConstraintEvaluation` output (ID, actual value, status, margin, bounded observed operands) on one structured channel; class-per-concrete-assertion [OWNER]; never raises on a verdict.
3. **Aggregator**: generated exact input schema (one required field per concrete assertion), exists for zero assertions, headline precedence (violation > indeterminate > all-satisfied > not-assessed); **guaranteed exit ancestor** — explicit exit membership or a generation-time ancestry assertion, never incidental (S4 carry-forward (1)). Vocabulary note: teax Item 10 pinned the runtime evidence vocabulary as underscore forms (`not_assessed`); the generated side conforms to the runtime (ownership direction decided in Item 10's spec) — align the emitted headline vocabulary accordingly and record it.
4. **Catalog**: source records (per asserted/applied usage) + concrete entries (per expansion, keyed by constraint_id, including the recorded producer binding from Item 5's B1 adjudication); unused definitions are inventory, never unassessed coverage.
5. **Runtime-facing tests** incl. break-the-YAML: a missing upstream evaluation surfaces as an execution failure through the executor, not a silent gap (S4 carry-forward (2)).

## Out of scope
Contracts/sealing (Item 9); drop-manifest retirement (Item 14); calc-side IR rendering (Item 13); flipping the lowering default (Item 8).

## Success criteria (from the epic)
- S4's slice reproduced by production generation end-to-end under real simkit: both truth values complete, identical ordinary outputs, correct margins, report persisted; plus the cases S4 didn't exercise — zero-assertion aggregator, indeterminate (non-finite) point, negated and inline assertions at execution, multi-instance expansion, modeled-default formals.
- Exit-ancestry holds under a deliberately narrowed exit (test); break-the-YAML test passes.
- Live/snapshot generation byte-identical for a constraint-bearing fixture — NOTE: this criterion is only meetable once Item 8 lands (snapshots can't carry facts yet); spec it as the Item 8 handoff gate, not an Item 7 exit gate, and record that sequencing honestly.
- Suite green; byte-identity for constraint-free corpus.

## Environment notes
- Real-simkit execution: teax's venv on the epic branch works (Items 10–12 provisioned it); Item 0/S4 findings hold the incantations.
- The orchestrator's shell keyring is flaky; stage sessions' envs are fine. Live tests via uv run pytest in-repo.
