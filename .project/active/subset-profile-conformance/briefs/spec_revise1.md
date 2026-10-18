Spec review (fresh session) verdict: Revise. Read `.project/active/subset-profile-conformance/spec-review.md` and fix every must-fix finding. My calls on the points it raised, all execution details I decide as orchestrator ([AGENT], record them in the spec as such):

1. L3-1: add a criterion that, for every case, the stored screen outcome and the stored generator outcome agree under the reason-to-code mapping, or the pair is listed in the disagreement record. Applies to all cases, not only `tests/fixtures/` directories.
2. L2-1: state honestly that `invocation-callable` and `constraint-predicate` share decision tables with the generator (`invocation_allowlist.py`, `executable_profile.py`), so screen-vs-generator independence does not hold for them. Their evidence is generator-route behavior on fixtures with hand-written expectations; record the limit explicitly instead of a detector-disable mutation that cannot fail.
3. L1-1: include the six further calc-def-output stub causes from the site account as known silent-loss families.
4. L3-2: adding a stable reason or diagnostic to a stub site or plain-exception site without changing accept/refuse is not RG-1; turning a stub or omission into a refusal is RG-1 (record a candidate with a recommendation, pin current behavior).
5. L1-2: 2a drafts an agentic-mbse ADR 0001 invariant 1 amendment (corpus cases become admissible evidence alongside probes), staged in this item folder; filing is the owner's at merge (RG-3).
6. L2-2: keep scope. Re-estimate to the reviewer's 25–35 engineer-days [AGENT]. State that the plan should order group E so its tail (stable reasons beyond sites witnessing a shared rule or recorded disagreement) comes last with an explicit split point; the split is taken only if E grows past its estimate, and that would be surfaced to the owner.
7. L3-6: when the screen refuses a model the generator builds, the default is to narrow the contract. If the generator's acceptance looks semantically wrong per P-0003, run the `kerml-expert` check, record a known disagreement and park the generator side as RG-1.
8. L3-3: move B1 (the part needing a readiness path) to Non-Goals as Item 2b.
9. L3-4: `omitted` outcomes need evidence from the generated contract/catalog or runtime, not text search.
10. L3-5: agentic-mbse version bump/publish: decide in design; list it as a design question.

Do not commit. End with `ARTIFACT: <path>`.
