# Brief: design review, named-subset-members

Run as a fresh subagent by the orchestrating session on 2026-10-26. You did not write the spec or design.

## Task

Review `.project/active/named-subset-members/design.md` against `spec.md` beside it, following `~/.claude/commands/_my_design_review.md` (if absent, `/home/reid/src/agentic-mbse/.claude/commands/_my_design_review.md`). Work in `/home/reid/src/sysml-codegen` on branch `named-subset-members`. Write `design-review.md` beside the design. Don't change `src/`, don't commit. The prototype patch and probes are in `evidence/` beside the design; you may apply the patch in a scratch worktree under `/tmp/claude-1000/nsm-review/`.

## Intent

[OWNER] option A: named subsets count as members of the collection they subset, so the generator builds the declared number of parts and `sum()` includes them. The owner's priority across this whole effort: no silent wrong numbers.

## What matters most

- **Silent wrong numbers.** Try to make the prototype build a wrong count or a wrong sum: named members plus values on the collection's body (the design's D7 refusal), nested collections with named members at two levels, a named member in a specializing def, named members under a redefined collection, a sum over a collection read from outside its parent, the sibling-leak shapes with named members. Run values in real TEAx (`PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python`).
- **The count fix (D4)** inheriting count and `ordered`/`nonunique` through redefinition: is it right per KerML, and are the accept/refuse flips (`g1__redefinition_drops_ordered_bounds`, `usage_owner_bare_subset_def_owned`, `f1_inherited_ordered_redef`) correct and honestly handled?
- **Engineering quality.** Is membership read once in the right place, is the slot-filing approach in `OccurrenceIndex.__init__` sound (could a by-name read or another caller of `children_for_slot` now see members it shouldn't)? Are seven new refusal sites justified, or could fewer, clearer rules do?
- **Proof.** Are the dc3 byte-identity and corpus claims reproducible, and does the plan prove them again on the real code?

Rank findings must-fix / should-fix / note. End with `ARTIFACT: <path>`.
