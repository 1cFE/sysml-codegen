# Brief: audit — docs-explainer-refresh

Audit the implemented item at `.project/active/docs-explainer-refresh/` against its spec
success criteria. Read: `spec.md` (the contract; amended twice, see Amendments below),
`design.md` (decisions D1–D5, invariants INV-1..6), `plan.md` (phase gates + Implementation
Notes with 5 recorded discrepancies), `staleness-survey.md` (evidence base).

Work synchronously; never pause for or spawn background agents. If a verification command is
blocked by permissions, write a "Requested live probes" section (exact command + expected
result) and continue — the orchestrator runs them.

## What was implemented (claims to audit, not trust)

Seven phases, one commit each: sysml-codegen `0fad7bf`, `78a6a7d`, `dbc60b8`, `d5328cc`
(branch `constraint-exec-epic`); agentic-mbse `9e24c93`; teax `4c96b99` (same branch, repos
at `/home/reid/1cfe/{agentic-mbse,teax}`); fusion-tea `bfff2b4f` (`main`,
`/home/reid/1cfe/fusion-tea`). If the cross-repo paths are sandbox-blocked, audit those legs
via requested probes.

Claimed gates: retired symbols zero-hit outside marked history; matrix recount 32 families /
274 reqs / 73 test files with summary = Index = overview; CON family anchored to
`tests/unit/test_contract_models.py` + `tests/conformance/test_seal_step9.py`; explainer
mechanical checklist clean + spot-read pass; fusion-tea `py_compile` OK.

## Amendments and ratified deviations (not defects; verify they're recorded, don't re-litigate)

- SC-4 amended: `is_droppable_constraint` is a LIVE symbol (`syside_adapter.py:418`) — kept
  as an accurate reframed reference; only the drop framing retired. Orchestrator-verified.
- SC-7 alias default = drop (three sites + stale comment), decided at orchestration.
- Five discrepancies recorded in plan Implementation Notes, two spawning BACKLOG follow-ons
  (`[DOC19-DISPATCH-REAUDIT]`, `[MODULEKIND-DOC-SWEEP]`) — check the follow-ons exist in
  `.project/backlog/BACKLOG.md` and that the out-of-scope calls were legitimate (scope was a
  targeted sweep, not a scrub).

## Audit hardest

1. **SC-6 both bars.** Mechanical: greps for retired caveats/anchors. Judgment: sample ≥8
   substantive claims from the refreshed `EXPLAINER_PROMPT.md` across the eight new areas and
   verify each against code at HEAD. Also INV-6 buildability: responsibility-map rows,
   reading-list data sources, reuse-guidance delta, corrected counts.
2. **Inherited-history criterion (INV-1/2/3)** across every new/edited doc: flag = landed
   history; `collect_constraint_manifest` not claimed removed; CE-F1/F2 as open follow-ons.
3. **Matrix truth:** recount families/reqs/test files from the Index yourself; CON rows
   anchor to test functions that exist and exercise the claimed behavior.
4. **One-story check:** the specific contradictions the survey inventoried are gone at the
   cited surfaces (re-grep them).
5. **Scope discipline:** no docs-scrub creep; Item-14 surfaces untouched.

Verdict: Certify / PASS-WITH-NOTES / FAIL, per criterion, with evidence. End with
ARTIFACT: .project/active/docs-explainer-refresh/audit.md
