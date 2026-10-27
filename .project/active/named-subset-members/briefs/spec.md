# Brief: spec stage, named-subset-members

Run as a subagent by the orchestrating session on 2026-10-26.

## Task

Write `.project/active/named-subset-members/spec.md` following `~/.claude/commands/_my_spec.md` (if absent, `/home/reid/src/agentic-mbse/.claude/commands/_my_spec.md`). Work in `/home/reid/src/sysml-codegen` on branch `named-subset-members`, which stacks on `repeated-rollup-collision` (collision, import and sibling-leak fixes, not yet merged). Don't change `src/`, don't commit.

## Intent

[OWNER] 2026-10-26: fix `[NAMED-SUBSET-DOUBLE-COUNT]` with option A, named subsets count as members of the collection they subset ("ok understood, proceed with the fix", after the orchestrator recommended A). The owner's understanding, which the spec should keep plain: the generator reads declarations from SysIDE but expands them into concrete parts itself; it understands redefinition (`:>>`) but never reads subsetting (`:>`), so `server_1 :> servers` becomes an extra child instead of one of the servers, and `sum(servers.x)` leaves it out.

Everything you need is in `.project/active/repeated-rollup-collision/evidence/double-count/report.md` (SysML meaning with KerML citations, shapes s1-s9 with models in `shapes/`, cause with file:line, the options, dc3 impact) and the backlog row `[NAMED-SUBSET-DOUBLE-COUNT]`.

## What the spec must settle

- The behaviour, as acceptance criteria a test can check, with numbers: for s1, s2 and dc3's shape s4, which copies exist and what `sum()` gives (25, 35, 35); per-copy values stay separate; the three `candidate-es-008` cases and `plain_nesting`, `one_subset_redefines`, `outer_redefinition` build the declared count (e.g. 4 PSUs, not 12).
- Named subsets keep their own names; they are not assigned index positions (ADR 0004 rules out choosing by declaration order).
- Refusals, each with a named code and reason: more named subsets than the count; a subset of a subset; `[*]` with named subsets stays refused as today (s3). [AGENT, reserved for the owner if the design wants to change it] treating the named parts as the only members of a `[*]` collection is out of scope.
- dc3: regenerating `/home/reid/src/dc3/models` must give a package identical to today's committed one, or every difference explained (the investigation expects none, unchecked). dc3 is read-only.
- Nothing else that builds today changes, proven by the whole-corpus byte check method in `.project/active/repeated-rollup-collision/evidence/corpus-receipt.md`.
- Non-goals: `[REDEFINITION-DROPS-COUNT]` and `[MEMBERSHIP-LIST-IGNORED]` (separate rows; say if the design finds the count fix unavoidable), and the open question of whether `comp_b :> comp_a` inherits nested redefinitions.

Use the provenance grades from `.claude/rules/capture-fidelity.md` (here or in agentic-mbse). Keep it short, plain, one line per paragraph. End with `ARTIFACT: <path>`.
