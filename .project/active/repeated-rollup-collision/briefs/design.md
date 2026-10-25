# Brief: design stage, repeated-rollup-collision

Run as a subagent by the orchestrating session on 2026-10-25.

## Task

Write `.project/active/repeated-rollup-collision/design.md` from `spec.md` beside it, following `~/.claude/commands/_my_design.md`. Include a phased plan with checkboxes at the end (a separate plan stage is skipped for this small item). Work in `/home/reid/src/sysml-codegen` on branch `repeated-rollup-collision`. You may run scratch probes; don't change `src/` and don't commit.

## Intent

[OWNER-VERBATIM] "yes file it and orchestrate a fix in sysml-codegen". The point is that several identical sub-assemblies, each rolling up its own children, generate and compute the right numbers. The spec is the contract; read it fully, including its [AGENT] assumptions.

## Orchestrator guidance [AGENT]

- **Engineering bar.** The fix should make the registry treat a computed module type the way it already treats a calc def module: one class per identity, registered once, used by many pipeline entries. Prefer one clear rule in one place over a special case for rollups. No new name-mangling heuristics in the registry; identity is decided at projection, as the spec says.
- **Copies of different shapes** (the spec's arity case, `b : Sub { part :>> leaf[2]; }`). Decide build or refuse on engineering grounds and record why. If building needs a second identity, it is decided at projection.
- **Scope stop.** If the clean design is "one registry entry per module type for every module kind", which would also change `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`, stop and say so in your final message instead of designing it; the orchestrator takes that to the owner.
- **Value checks are available.** dc3's venv has `simkit`: `/home/reid/src/dc3/.venv/bin/python -c 'import simkit'` works (teax checkout at `/home/reid/src/teax`). Use it to run generated packages for the spec's value criteria, and say in the design how the execution-lane tests (`pytest -m execution`, see `pyproject.toml:47-50`) get run with it. The default suite still needs the structural, simkit-free check the spec asks for.
- **Fixtures that flip.** `tests/fixtures/unresolvable_attr_probe` and its pins (`tests/conformance/test_public_authority_switch.py:516`, the `public_package_oracle` baseline) will change from refused to built. Say how each pin is updated, and correct `docs/architecture/reference/20-module-registry-generation.md`.
- Keep the design short. Plain words, one line per paragraph.

End with `ARTIFACT: <path>`.
