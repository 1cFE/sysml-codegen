# Audit Brief — Lifecycle Item 1: Occurrence and Demand Integrity

**Stage:** audit (independent; the implementing session does not self-certify)
**Candidate coordinate:** sysml-codegen `28bc8b0f` (evidence-only commit `87c505b` follows it),
agentic-mbse `515e08bb`, TEAx `d545701f`.
**Artifacts:** `.project/active/constraint-lifecycle-occurrence-demand/{spec,design,plan,evidence}.md`

## What to audit

Item 1 against its approved spec/design and the plan's Final Completion Gate, with these
already-ratified amendments (do not re-litigate):

- **Owner ruling 2026-07-19 (epic commit `a1435e1`):** all numeric LOC gates/baselines/caps are
  retired. LOC rows are correctly marked `[~] retired`, recorded once informationally. Simplicity
  is judged qualitatively (deletion over shims, no collapsed intentional boundaries).
- **Orchestrator-accepted recorded deviations** (evidence §6): `predicate_source_key` seventh
  prepared field; `ResolvedDemand` at four fields with `select_group_source` split out (compelled
  by a confirmed collision/provenance defect found in independent review); indirect-cycle fixture
  gap covered at unit level; design-vs-plan edge-field definition; Phase 0 fixture-digest
  correction.

## Priorities

1. **RED/GREEN integrity:** same public overlay bytes (`aea7c821…`) at Phase 0 RED and candidate
   GREEN; five stable nodes fail-then-pass for the named R-4/R-5/R-7 reasons.
2. **Invariants:** no re-query path from lowering; all-or-nothing transcript; structural cycle
   error with intact cause fields; copy-on-write enrichment; deterministic ordering; no package
   fallback for unsupported owners; excluded/unsupported zero queries.
3. **Deletion reality:** RecordingOccurrenceIndex, collect_bare_actual_demand,
   materialize_supplied_values, route-counted loops, last-write-wins synthesis — absent with no
   wrapper/flag/alias replacement.
4. **Evidence honesty:** claims match recorded outputs; same-checkout replay labeled
   non-certifying; Items 4/5/13 left open; no unsupported checkbox in plan/spec/epic.
5. **Scope firewall:** Item 2's resolver not absorbed; no schema/version/lock drift; existing
   fixtures and baseline_outputs byte-identical.

Known environment facts (do not misdiagnose): TEAx lane needs the agentic-mbse venv +
`PYTHONPATH` (evidence §3); license env comes from `set -a; source
/home/reid/1cfe/agentic-mbse/.env; set +a`; format-check debt of 19 files is pre-existing
baseline (20 at Phase 0); `.claude/projects/` is user-owned — never touch it.

Verdict: Certify / Pass-with-notes / Needs-work, with reproduced evidence for any finding.
