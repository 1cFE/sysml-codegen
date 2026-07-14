# Brief: Item 14 audit — Migration, Docs, and IFE Acceptance (epic-closing)

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it. This item closes the epic — audit against the epic's Success Criteria as well as the item's.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/constraint-migration-acceptance/`.
- License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run ...`. If execution blocked, static audit + exact probes.
- Cross-repo evidence you cannot read directly: the orchestrator will run probes; the fusion-tea findings are summarized below.

## Audit target
All Item 14 commits (in-repo Phases 1–6: `9dcd1ab..c4a8618`; plus the recorded cross-repo results) against `spec.md`, `design.md` (rev 2), `plan.md` (+ notes), `run-report.md`.

## Cross-repo results (orchestrator-verified summaries)
- Appendix A (agentic-mbse `d83109a`): constraints.md flipped to the profile; grep shows one decision-record mention only.
- Appendix B (teax, two commits): W5b loader-seal wiring + evaluator/study docs + tracking-key note; suites green except the 4 known.
- Appendix C (fusion-tea, two commits): **acceptance 2294/2301 exact matches; 7 divergent rows are exactly the eta*gain==10.0 epsilon-boundary rows (hand rule strict > vs modeled >=)**; hand rule deleted; ~168× prepare-once benchmark; 200/200 verdict parity. THREE integration gaps surfaced and bridged consumer-side (findings.md there): (1) no standalone constraint_catalog.json emitted (embedded in model_contract.json under different names); (2) teax CandidateBridge single-entry-channel-only; (3) PreparedEvaluator hardcodes ToyPlantParams.

## What to verify
1. **In-repo phases by execution**: mapping/no-silent-drop test; retirement grep; the gain-fix regression tests + exactly-two-snapshot blast radius (git evidence); docs flip; suite/mypy/ruff gates.
2. **Adjudicate the acceptance against the epic's Critical Success Factor** ("every existing grid classification matches"): the design pre-decided boundary rows are surfaced as real semantic differences (B3/D5); the divergence favors the MODEL (>= is what fusion_cycle.sysml says — the hand rule was unfaithful). State plainly whether the criterion is met as-worded, met-with-recorded-divergence, or unmet — and what the honest epic-close-out record should say. This goes to the owner.
3. **Adjudicate the three integration gaps**: each is a real defect-or-limitation in a certified item's claim surface (Items 9/12/10). None invalidates this item's work (bridged consumer-side, documented) — but say which certified-item claims they narrow, and confirm the findings recommend real follow-on items rather than permanent adapters.
4. **Epic Success Criteria walk**: every epic checkbox — checked boxes have evidence; unchecked boxes named with what remains.

Verdict: Certify / Certify-with-notes / Fail — plus a one-paragraph epic-level assessment for the close-out.
