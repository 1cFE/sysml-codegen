# Brief: Item 5 design review — Concrete Lowering

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design-review.md` in `.project/active/constraint-lowering/`.

## Review target
`.project/active/constraint-lowering/design.md` (spec, spec-review, briefs beside it).

## Ground truth
S4 code (`s4_lib.py` + findings); landed types (`.project/reference/agentic-mbse-landed/` + editable install); Item 4's index (`analysis/part_instance_index.py`); the real pipeline (`orchestration/pipeline_builder.py` Step 5.65→7 region, `analysis/dependency_backtracker.py`, `core/output_registry.py`, `resolution/graph_builder.py`).

## What to probe hardest
1. **D1's terminal-switch claim.** "Fallback unreachable in strict mode" — walk the designed seam against the backtracker's real code paths: is there any entry into the fallback that bypasses the switch (helper functions, recursive calls, the V11 boundary check's own resolution)? The F4 lesson says the fallback is subtle; verify the unreachability is structural.
2. **B1 (per-occurrence producer channels) — characterize it precisely for an orchestrator-run probe.** Read the output-registry + virtual-calc-expansion code and state exactly what a live probe must check: for a `[3]`-multiplicity part whose instances each own a calc, does `OutputRegistry` hold three distinct owner-scoped channels (and under what QN scheme)? Write the probe recipe (model shape + registry query + expected outcomes for confirm/refute) in your review — the orchestrator will execute it.
3. **The Step 5.65→7 threading.** Three threading points claimed — check each against `build_pipeline_context`'s real signature/flow; does anything at those points mutate after lowering reads it (ordering hazard)?
4. **constraint_id encoding**: scannable-prefix + sha256[:8] — collision behavior (spec: collision = generation error) actually detectable? Deterministic across load orders (inputs all from sorted facts)?
5. **ConcreteConstraint serializability**: every field JSON-serializable graph data (Item 8) and sufficient for Item 7's emission (module identity, catalog entries, margins metadata)?
6. **Fixture adequacy (D6)**: do the two new fixtures + reused probe fixture actually cover the four success criteria (control-prune/retain, V11 extended, repeated-load identity, corpus byte-identity) plus multi-instance and inline-form?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the design's word.
