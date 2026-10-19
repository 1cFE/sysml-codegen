# Brief: /_my_audit (final) of EXEC-SUBSET-CONTRACT Item 2a

Audit the whole of Item 2a against `.project/active/subset-profile-conformance/spec.md` and `design.md` (rev 3), with `plan.md` as the claimed record. A mid-run audit of Phases 1–2 is in `audit.md`; confirm its blocker and advisories were resolved, then audit Phases 3–7 and the item as a whole. Append to `audit.md` (or supersede per the command's convention).

Code: sysml-codegen this worktree, branch `subset-conformance` (base `b5663c07`); agentic-mbse `/home/reid/src/subset-conformance/agentic-mbse`, branch `subset-conformance` (rebased on agentic-mbse `main` with Item 4). dc3 at `/home/reid/src/dc3` is read-only (export pinned revisions to temp trees if you rerun). Agentic-mbse needs `uv sync --all-extras`; licenses in each `.env`.

Intent [AGENT] (ratified by owner): prove, independently of the new screen, that the shared contract matches what the generator actually does, and make drift fail a test.

Look hardest at:
- **Does drift actually fail?** Make real perturbations and confirm a test goes red: widen and narrow a screen rule; disable a generator site from Phases 3–6 (not only the ones the mid-run audit tried); edit a stored answer; add an unclassified `raise` in codegen; change a file under agentic-mbse `sysml/` without a new receipt.
- **Disagreement record (78+ entries)**: are entries justified, or is it a place where real drift was parked to make tests pass? Sample and check reasons.
- **Gate discipline**: no change to generator accept/refuse (verify independently, e.g. base vs HEAD over the model roots); RG-1/RG-2/RG-3 artifacts are recommendations only; the new stub warning is the only behavior change.
- **Code quality**: well-factored, idiomatic, no dead code or placeholders; the test machinery (harness, tracer, mutate helper, receipts) is maintainable, not a pile of one-offs.
- **Honest records**: `r3-closure.md`, `rg1-recommendations.md`, `rg2-string-policy.md`, the staged amendments and the backlog rows say what is true and no more.
- Spec criteria left unchecked, with reasons.

Write the audit artifact; do not fix code. Give a clear verdict. End with `ARTIFACT: <path>`.
