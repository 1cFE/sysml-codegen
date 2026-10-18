Fresh design review verdict: Rework (`design-review.md`). Spike S1 is done (`spikes/s1/findings.md`). Revise `design.md` to resolve every must-fix review finding and fold in the spike's amendments. My calls, all [AGENT] orchestrator decisions; record them as such:

**Review findings**
1. Record backing without CI. Neither repo has CI. Keep a required pre-merge run in agentic-mbse that exercises codegen against the screen (keep `scripts/subset_profile/codegen_suite.py` and what it imports from `probe.py`, parameterizing its output directory as the epic requires). Stage a fuller ADR 0001 amendment: cases replace probes as evidence, codegen enforces invariant 1, how a `case:<id>` citation resolves, and the pre-merge run. Also say plainly that extractor/evaluator code changes are caught only by that run.
2. agentic-mbse must keep screen tests on real models. Constraint: one copy of each model. Choose between (a) models stay in agentic-mbse and codegen cases reference them through the sibling dependency, or (b) another single-source layout. A duplicated copy guarded only by a hash check is the fallback, not the default. Record the reasoning.
3. Screen mutations are judged against the stored generator answer, not the screen's own.
4. `disagreements.json` is hand-edited only; no tool writes it. State it and make the test fail if a writer is introduced (or document why that can't be enforced).
5. `SiteReason` typing: fix the renderer field typed `SiteReason` holding a subset reason. `Diagnostic` reason must not invalidate or silently drop on the 22 committed v6 snapshots; 2a does no snapshot-format change (that is 2b). Choose a carrier that keeps snapshots byte-stable.
6. Define the agreement rule for generation-stage refusals that have no code.
7. Fixtures with several constructs: apply the per-case agreement rule as the spec asks, not stricter; say how multi-construct fixtures are judged.
8. A plain exception becomes a coded refusal outside RG-1 only if it already reaches `run_codegen` as a refusal today. Otherwise it is an RG-1 candidate.
9. Give group E an estimate so its split point can trigger; move the E5 rescan to the final phase so taking the split does not drop it.

**Spike amendments**
10. D5 becomes "neutralize the one statement that emits the site", with the 4 named hand patches.
11. Mutation tests compare stored reasons and stub causes, not codes. So D8 reasons are a prerequisite for each site's mutation test; order phases accordingly. Sites that can shadow each other need distinct reasons.
12. Mutating a shared agentic-mbse site moves both sides; record that as non-independent evidence alongside the shared-table limit.
13. Record the spike's unchecked shapes (`lru_cache` wrappers, zero-arg `super()`, shared-site cases) as known limits the implementation must handle or list.

**Baseline**: the spike saw 10 pre-existing failures in the licensed suite (`test_self_binding_guidance_contract` on agentic-mbse's `MODELING_PROCESS.md.template`, and nine in `test_check_ledger_4a.py` that diff commits this worktree lacks). Add a design note that the plan's first phase records the baseline and determines whether each is pre-existing at `b5663c07` + agentic-mbse `ccd57d83`, so 2a is not blamed for or silently absorbing them.

Do not commit. End with `ARTIFACT: <path>`.
