# Brief: design revision — study-layer-to-codegen

Sent by the orchestrator to the design session (resume), 2026-10-12, after the fresh review at `.project/active/study-layer-to-codegen/design-review.md` (verdict Revise). Read the review in full. Then revise `design.md`: apply M1–M4, S1–S8 and the minor items (m1–m7), subject to the decisions below. Where a decision settles a point differently from the review, follow the decision and record it.

## Orchestrator decisions [AGENT, orchestrator, 2026-10-12]

**Premise conflicts 1, 3, 4: accepted.** The review confirmed all three. Record them as accepted by the orchestrator. For conflict 1, make the `INSTALLER_API_VERSION` import lazy (inside `install-commands`), so an older agentic-mbse cannot break `generate` or any other subcommand. For conflict 4, apply the review's wording fix. The orchestrator amends the spec's B9/SC3 wording and its L3-9 requirement to match, citing this design.

**M1 → new closed-list item B12, "declared gate claims".**
- Each declared repo gate carries its own `checked` text (and whatever else the return states about what the gate examined) in the target's declaration.
- fusion-tea's declaration supplies today's strings byte for byte, so fusion-tea's returns stay identical. SC12 checks this for fusion-tea's declaration.
- A target that declares a gate without that text is an invalid declaration, which blocks at gate 0 with `input-invalid`. There is no default text, because a default would claim a check nobody declared.
- Add B12 to the design's edit map. The orchestrator adds B12 to the spec's closed list.

**M2: accept the review's fix.** fusion-tea's runbook step 5 rewrites the eight `study_route.py` imports from `scripts.study` to the installed package. State whether this changes any sealed identity a committed record depends on. If it does, the re-verify step has to say so.

**M3: accept.** The teax revision comes only from `TEAX_SIMKIT_PATH`. Without it, gate 1b blocks (could-not-run). It never passes, and it never records a revision it did not read from a teax checkout. `read_coverage`'s teax roots follow the same rule.

**M4: an explicit, narrow allowance, not a dodge.**
- The study package reads environment variables in exactly one module, `sysml_codegen/study/roots.py`. The conformance test gains one named allowance for that module, with a comment giving the reason: study location settings, which do not affect generation authority. A second test asserts that no other study module reads the environment.
- Do not make the import lazy just so the test can't see the read. That would hide the read, not justify it.
- `cli.__all__` and the `CODEGEN_COMMANDS` pin are updated with the reason recorded.
- Name the exact test edits in the design.

**S1: anchor the project root to the input, not the working directory.**
- The project root is `SYSML_CODEGEN_PROJECT_ROOT` when set. Otherwise it is the git work tree that contains the tool's `--package` argument. Tools without a package argument use their primary input path; name it per tool.
- If the working directory's work tree differs from the package's, the tool refuses with exit 2 and names both, rather than guessing.
- The declaration is read from the project root this produces.
- Fix Key Bet B1's text to match.
- Library callers (Appendix C) keep explicit-root behaviour as the design defines it. Implement m1 as the review suggests: an in-process root override in `roots.py`, with no `os.environ` mutation on import.

**S2: tighten the rehearsal (Appendix H).**
- Give each run a pass rule that isn't circular.
- Control the environment and record it.
- Count skips per run and compare the counts.
- Add one `integrate` run on a real fusion-tea package in run C. It is the step that would have exposed M2.
- Mark it as needing teax and the syside license. The orchestrator runs it.

**S3: mask subfields, not whole fields.** In the parity script, mask only the noisy parts: paths, digests, timestamps and the closed-list strings. Do not mask whole blocks. A changed blocker message must show up as a difference.

**S4–S8, m2–m7: apply as the review proposes.** For m4, reject absolute paths and paths that escape the project root at declaration validation.

**Estimate.** Add the hours the review found missing: the fusion-tea test edits (assign who drafts them; the implementing stage drafts them in this item folder for the orchestrator to apply on the fusion-tea branch), M2 and M4. Take the review's two trims only if they don't touch a never-cut criterion. State the new total plainly.

When done, add a short "Revision 2026-10-12" section mapping each change to its review ID. Do not commit. Do not start background tasks. Finish with `ARTIFACT: <path>`.
