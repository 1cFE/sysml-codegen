# Brief: implement round 2, named-subset-members

Sent to the implement session on 2026-10-26 after `audit.md` (verdict Needs Work). Orchestrator decisions [AGENT]. The audit's probes are in `evidence/audit-probes/`.

1. **B1: fix.** Decide membership per parent, from the sibling declaration and the declarations it redefines, so `rack_a : Rack { part :>> spare :> servers {...} }` makes `spare` a member only in `rack_a` (and in whatever specializes or uses that declaration), not in `rack_b`. Add the audit's model and its specializing-def variant as tests with TEAx values (`rack_a` 25, `rack_b` 20).
2. **B2: fix.** A read of the collection from inside one of its own members (and from inside an indexed copy, the older bug the audit notes, if it is the same mechanism in `resolve_address`'s path-prefix narrowing) must reach every member once. Add the audit's three shapes as tests with TEAx values (25; share 0.5; fractions 0.75 and 0.25). If the indexed-copy case has a different cause, fix only the member case here and file a backlog row for the other with its reproducer.
3. **S1: fix** the `[MEMBERSHIP-LIST-IGNORED]` note: base gives 10; the branch's 35 comes from subsetting, the list is still not read; a list of non-subsetting parts gives 20 where the model means 35.
4. **S2: fix** the wording in `docs/architecture/modeling-assumptions.md` to say what the code refuses: any non-part feature in the collection's own body.
5. **Note:** compute `child_members` once per usage if it is a small change.

Then: real-TEAx values for every earlier probe still match; whole-corpus byte check (record the new differences, if any, in the receipt); dc3 at `8a98af8` byte-identical; default suite (9 known failures); `ruff` and `mypy` clean. Commit each fix on the branch (explicit paths, trailer). Don't push. Report SHAs and results. End with `ARTIFACT: <path>`.
