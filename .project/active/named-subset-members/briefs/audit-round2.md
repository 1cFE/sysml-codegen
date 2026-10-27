# Brief: audit round 2, named-subset-members

Run as a fresh subagent by the orchestrating session on 2026-10-26. You did not write any of this.

## Task

Re-audit the round-2 fixes on branch `named-subset-members` in `/home/reid/src/sysml-codegen`: commits `550b3ee1` (B1, per-parent membership), `3cc2fb98` (B2, `resolve_address` narrows only steps the reader did not write), `9e809ee0`, `27037160`. Read `audit.md` (the first audit) and `briefs/implement-round2.md` beside the design. Append a "Round 2" section to `audit.md` with a verdict. Don't fix or commit; comparison worktrees go under `/tmp/claude-1000/nsm-audit2/` and are removed after. dc3 is read-only.

## What matters most

B2 changes how every reference is resolved, not just named members. Try to break it:
- a copy reading its own nested part, and reading a sibling copy's nested part by index;
- reads from inside nested collections at two levels (`racks[i].servers[j]` reading `servers` and reading `racks`);
- a chain that starts with a name the reader also has locally (shadowing);
- reads inside repeated rolled-up sub-assemblies (the previous item's fixtures under `tests/fixtures/repeated_rollup/`);
- the sibling-leak shapes (`tests/fixtures/sibling_override_leak/`).

For B1, try membership added in a usage, in a specializing def, and in a redefinition two levels down, with other usages left alone.

Check values in real TEAx (`PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python`) and work the expected numbers out by hand from KerML. Confirm the round-2 corpus claim (no existing root changed between `153d09e2` and `27037160`) on at least a sample, and the default suite (9 known failures). End with `ARTIFACT: <path>`.
