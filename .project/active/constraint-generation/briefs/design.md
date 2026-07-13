# Brief: Item 7 design — Constraint Generation

You are the design stage for Item 7 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design.md` in `.project/active/constraint-generation/`.

## Input
- Spec (committed, review-revised): `.project/active/constraint-generation/spec.md` — [OWNER] class-per-assertion identity, compile-once-per-definition bridge, same-IR generation guard, modeled-default-as-EP, falsifying exit test, runtime vocabulary conformance are fixed. Deferred items (exit-ancestry mechanism choice, runtime field schema, template structure, naming) are yours to decide and record.
- S4's proven emitters: `spike-vertical-slice-constraint-execution/s4_lib.py` (module template, aggregator schema, catalog assembly — the productionization base). S2's Kleene compile shapes: `spike-expression-tree-parity/` probes.
- Certified seams: Item 6's five kind-dispatched generation entry points (design + code); Item 5's ConcreteConstraint/catalog + `lower_constraints_enabled` (generation tests run flag-on); Item 2's parse_expression.
- The generated output runs under real teax simkit — Item 10/11's committed test fixtures show the runtime's expectations (`~/1cfe/teax/packages/teax-simkit/simkit/tests/evaluation/fixtures/sealed_package/` is S4-lineage generated output — a concrete reference for what a working package looks like).

## Design guidance (orchestrator, agent-grade)
- Decide exit-ancestry mechanism: explicit exit membership vs generation-time ancestry assertion — weigh against how exits are selected today (`cli`/pipeline YAML emission) and pick the one that survives a user-narrowed exit; record the rejected one.
- The Kleene compiler is codegen-owned: design its module home, the compiled-function shape (def-level, formal-named args), and how non-finite leaf-unknown + propagation render as Python (S2's probe is the semantic oracle; keep the compiled code readable).
- Design the five-seam emission concretely (template additions per seam, wrapper/stencil/registry/YAML/test-gen), each replacing Item 6's fail-loud guard with real rendering for constraint/report_aggregator kinds — the guards' unit tests flip to positive tests.
- ConstraintEvaluation/ConstraintReport runtime models: generated (per-package schemas) per S4's shape; the report vocabulary conforms to the runtime's underscore forms.
- Execution tests run the generated package under real simkit (teax venv works on the epic branch; Item 0/S4 findings hold incantations) — design the test harness shape (subprocess? direct executor?) concretely for the plan.
- A skeptical design_review follows; make emitter and compiler decisions explicit with rejected alternatives.
