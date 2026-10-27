# Brief: spec stage, repeated-rollup-collision

Run as a subagent by the orchestrating session (in agentic-mbse) on 2026-10-25.

## Task

Find the root cause, then write `.project/active/repeated-rollup-collision/spec.md` following `~/.claude/commands/_my_spec.md`. Work in `/home/reid/src/sysml-codegen` on branch `repeated-rollup-collision`. Don't change source code and don't commit (the orchestrator commits). Read `CLAUDE.md` and `.project/CURRENT_WORK.md` first; the repo's ADRs are in `.project/adr/`.

## Intent

[OWNER-VERBATIM] 2026-10-25: "yes file it and orchestrate a fix in sysml-codegen". The owner authorized changing generator behaviour for this case (refused today, should build), so it does not wait on the open RG-1 gate.

Why [AGENT]: several identical sub-assemblies, each rolling up its own children's cost (a facility with `Rack[2]`, each rack summing its servers), is the most ordinary costing shape. Today it is refused, so consumer project dc3 cannot use the toolkit's costing pattern. agentic-mbse now documents the refusal with a wrong-way example that will turn red when this is fixed.

## The defect

Backlog row `[REPEATED-ROLLUP-REGISTRY-COLLISION]` in `.project/backlog/BACKLOG.md`. Reproducers in `.project/active/repeated-rollup-collision/repro/`: `one/` builds, `two/` fails `check` with `REGISTRY_CLASS_NAME_COLLISION ... (grandparent collision): 'Sub_capital_costModule' <- ['p.sub.capital_costModule', 'p.sub.capital_costModule']`, `twoplain/` (two copies with a literal cost) builds. Run with `uv run --env-file /home/reid/src/agentic-mbse/.env sysml-codegen check --models <dir>/models` (and `generate` to a scratch dir under `/tmp/claude-1000/` to look at output). Note the two colliding module paths are identical, which suggests the occurrence index is lost when the module path is built, or that two occurrences of one definition feature should share one module class and differ only in pipeline entries. Find out which, from the code and from how the generator already handles the leaf group (`Leaf[3]` builds per-occurrence entries without colliding) and calc defs used more than once. See `docs/architecture/reference/20-module-registry-generation.md` and `docs/architecture/modeling-assumptions.md` § 6.

## What the spec must settle

- The root cause, with file and line.
- What the generated package should look like for `two/`: module classes, pipeline entries and input keys, consistent with how the generator already treats repeated occurrences. State it as acceptance criteria a test can check, including computed values (e.g. `Top.capital_cost` = 60.0 for two subs of three 10.0 leaves) and that each copy's inputs stay separate (a different leaf value in `sub[1]` changes only its term).
- Cover both forms: `Sub[2]`, and two named parts typed `Sub`. Also a nested case (three levels, each repeated), and the named-total variant (`attribute sub_total = sum(...)`).
- That a real grandparent collision (two genuinely different modules that alias identically) still fails fast; the registry check stays.
- Non-goals: other backlog rows, including `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`, unless the root cause is shared; if it is, say so and stop for the orchestrator rather than widening scope.

Use the provenance grades in `.claude/rules/capture-fidelity.md` if present, else agentic-mbse's. Keep it short. Plain words, one line per paragraph. End with `ARTIFACT: <path>`.
