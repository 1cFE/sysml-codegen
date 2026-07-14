# Brief: Item 6 — `module_kind` and the Generation-Seam Refactor (spec stage)

You are one stage of the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously. Never pause for background agents, never schedule check-backs.
- Do NOT run `git commit` — the orchestrator commits. Leave files in the working tree.
- Artifact: `spec.md` in `.project/active/module-kind-refactor/`.

## Provenance of what you're given
- The concept (`.project/concepts/constraint-execution-and-design-space-studies-claude.md`) is the owner-ratified design (see its `PipelineModule` paragraph in "Concrete Lowering").
- S4 spike result + carry-forwards (concept Appendix B, S4 section) are verified agent-grade evidence. S4 confirmed `module_kind` empirically: four calc-shaped generation seams had to be bypassed by test-only emitters to make a constraint module render at all.

## Intent
This is a pure refactor of existing generation — byte-identity for existing kinds is the whole point. It clears the path for Item 7 (constraint-kind emission) without mixing refactor risk into new-emission risk. Task-type cohesion: refactor-of-existing is deliberately separated from new code.

## Objective
Replace the accreted Boolean flags with a real `PipelineModule.module_kind` and make the four calc-shaped generation seams kind-dispatched, byte-identically for existing kinds.

## Scope
1. `module_kind` enum (calculation, formula, aggregation, constraint, report_aggregator) replacing Boolean flags on `PipelineModule` (`models.py` — flags around lines 181-182 at last verification); structured output schema identity becomes graph data (retiring the float-specialized wrapper assumption for structured modules).
2. The four seams S4 named: `_get_python_path`/`_check_duplicate_output_paths` (assume `calc_def_qualified_name`), `generate_registry` class naming/dedup, `_generate_modules` wrapper rendering, `_generate_stencils`.
3. Migration of every flag consumer; snapshot serialization of the new field (coordinate with Item 8's version bump — flag in the spec if sequencing matters; Item 8 has not started yet).

## Out of scope
- Emitting constraint-kind modules (Item 7); any behavior change for existing kinds.

## Success criteria (from the epic)
- Entire existing fixture corpus regenerates byte-identically (timestamps excepted) with flags gone.
- The four seams dispatch on `module_kind`; a constraint-kind module reaching any of them no longer mis-renders as a calc (guarded by unit tests; exercised for real in Item 7).
- mypy/Ruff clean; suite green.

## Required reading
1. Concept `PipelineModule` paragraph + Appendix B S4 seam findings.
2. `.project/active/spike-vertical-slice-constraint-execution/findings.md` — the seam findings section (exact code paths the test-only emitters bypassed).
3. Byte-identity gate mechanics: a full snapshot re-capture rewrites every `captured_at` timestamp; the gate is timestamp-only-diff check + revert. Re-capture per-fixture, verify diff classes before accepting.
