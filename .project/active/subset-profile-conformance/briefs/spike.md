# Brief: /_my_spike S1 for EXEC-SUBSET-CONTRACT Item 2a

Run spike S1 as described in `.project/active/subset-profile-conformance/design.md` (assumptions B2, B3; decision D5; "De-risk first" section). Sibling agentic-mbse worktree: `/home/reid/src/subset-conformance/agentic-mbse`; Item 1's probe models are under its `tests/fixtures/subset_profile/probes/`.

Questions to answer with throwaway code:
1. B2: can a test helper elide one `raise` (chosen by scanner site ID) in-process, for: a module function, an `_ExactElaborator` method, a nested function, an agentic-mbse `reference_use` site, and a `calc_compat_renderer` stub site, including re-binding names imported elsewhere? Does each elision flip its case's outcome, and only that case's?
2. B3: end-to-end time for ten cases (live generator run with the screen made to raise, plus screen evaluation), extrapolated to ~200 cases, ~150 fixtures and ~120 mutation runs.

Put throwaway code under `.project/active/subset-profile-conformance/spikes/s1/` (not `src/` or `tests/`). Do not modify product code. Write findings to `.project/active/subset-profile-conformance/spikes/s1/findings.md`: per question, the observed result, the evidence (command + output), and what it means for D5 and the estimate. Do not commit. End with `ARTIFACT: <path>`.
