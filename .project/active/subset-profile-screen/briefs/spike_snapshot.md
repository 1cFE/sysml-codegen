Spike for EXEC-SUBSET-CONTRACT Item 2b (`subset-profile-screen`, sysml-codegen, branch `subset-profile-screen`). Throwaway code only, in a scratch folder under `.project/active/subset-profile-screen/spike-snapshot/` (findings write-up kept; code may stay there as evidence but must not touch `src/` or `tests/`). The agentic-mbse sibling worktree is `/home/reid/src/subset-conformance/agentic-mbse`; do not edit its `src/` either (a change there needs a gate rerun).

Read first: `.project/active/subset-profile-screen/spec.md` (approved, with minor fixes), especially Open Questions "How a snapshot carries the screen" and the split trigger; `briefs/align.md`.

Context and grades:
- [OWNER] Snapshots saved before 2b need not keep loading. A new envelope format that refuses older ones by name is acceptable (website check pending with the owner).
- [OWNER-ratified] The generator's own route alone decides refusal; the screen only reports. Screen findings from a snapshot must equal the live findings for the same model, or be named as not assessed.
- [INHERITED: ADR 0011 "Why", owner premise as paraphrase] Snapshots are a serialization choice, not an architectural constraint.

The bet to confirm or kill: option 2 in the spec, "seal the screen's facts (`SubsetFacts`, agentic-mbse `sysml/subset_facts.py`) into the snapshot and re-run the screen on replay", is feasible and gives live/replay parity.

Answer these with evidence (commands run, counts, file paths):
1. What exactly does the screen consume? Does building the screen's input need anything beyond `SubsetFacts` (parse tree, SysIDE handles, document paths, the elaborated graph)? Where are facts extracted, and does extraction need the license?
2. Are `SubsetFacts` serializable to JSON and back without loss (identity, ordering, locations)? Write a throwaway round-trip and run it over every admitted 2a corpus case and every committed snapshot fixture's source models where available. Report: for how many does `screen(facts)` == `screen(roundtrip(facts))`, byte-for-byte on findings and unverified checks? List every mismatch.
3. Size and time: how much bigger would each committed snapshot get, and how long does extraction add to `snapshot` capture?
4. Where the screen's findings carry locations (file, line), are those stable when replayed on another machine (absolute paths, document IDs)?
5. Anything that would make option 2 worse than option 1 (seal findings) or option 3 (keep v6, not assessed), with reasons.
6. Restate the effort for the snapshot half of 2b in engineer-days, and say whether the split trigger fires.

Write `spike-snapshot/FINDINGS.md`: lead with the verdict (option 2 confirmed / killed / confirmed with conditions), then the evidence per question, then what you did not check. Run with the SysIDE license from `.env`.
