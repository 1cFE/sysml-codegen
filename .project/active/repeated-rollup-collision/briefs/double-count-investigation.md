# Brief: investigate named-subset double counting

Run as a read-only subagent by the orchestrating session on 2026-10-26.

## Intent

[OWNER-VERBATIM] 2026-10-26: "ok fix the leak and investigate the double counting". Another agent is fixing the leak on branch `repeated-rollup-collision` at the same time; do not edit or commit anything in `/home/reid/src/sysml-codegen` and do not switch its branch. Use a git worktree and scratch under `/tmp/claude-1000/double-count/`.

## The suspected defect

From `.project/active/repeated-rollup-collision/evidence/leak-investigation/report.md` (§ "What changes"): the generator seems to build a named subset (`server_1 :> servers`) as an extra copy beside the indexed ones, so `rack_1` gets `servers[0]`, `servers[1]`, `server_1`, `server_2`: four servers in a `Server[2]`. The cases are `candidate-es-008__nested_named_subset__part_usage`, `..._single_rack`, `candidate-es-008__sibling_subsets_redefine__part_usage` in `tests/fixtures/refusal_cases/`.

## Find out

1. **What SysML means.** Does `part server_1 :> servers;` inside a part with `part servers : Server[2];` name one of the two servers, or add a third? Check the SysML v2 spec in `/home/reid/src/agentic-mbse/docs/sysmlv2/` (subsetting, multiplicity) and what native SysIDE 0.8.4 reports (e.g. evaluating `sum(servers.x)` or the size of `servers`, docs in `/home/reid/src/agentic-mbse/docs/syside/`).
2. **What the generator builds**, for: one named subset; two named subsets filling `[2]`; named subsets with no indexed count (`[*]`); and dc3's shape, a library `[*]` collection with the count set by redefinition in a specializing def (`part :>> racks[2] { servers[0]; }`) plus named subsets `rack_1 :> racks`. Count the copies in `inputs/` and in any `sum()` over the collection.
3. **Whether dc3's numbers are affected.** dc3 (`/home/reid/src/dc3`, read-only) has a committed generated package at `exploration/ac_dc_baseline/dc3_baseline/` and models in `models/`; its design is `work/completed/20261024_WI-008_generator-idiom/design.md` (P8 explains its `[0]` templates). Check whether any generated value in dc3 sums over a collection that also has named subsets, and whether the result double counts. Generate dc3 to scratch if needed (`uv run --env-file /home/reid/src/dc3/.env sysml-codegen generate --models /home/reid/src/dc3/models ...` from the sysml-codegen checkout).
4. **The cause**, with file and line, in `elaboration/occurrence.py` (occurrence index build) or nearby, and ADR 0004 in `.project/adr/`.
5. **The fix options and their costs**: make named subsets fill indexed slots, or refuse the ambiguous shapes by name; what each changes in output that builds today.

Don't write a fix. Report plainly: SysML meaning with citation, native values, generator behaviour per shape, dc3 impact, cause with file:line, options, what you didn't check. Put your report in your final message (you may not be able to write files outside scratch).
