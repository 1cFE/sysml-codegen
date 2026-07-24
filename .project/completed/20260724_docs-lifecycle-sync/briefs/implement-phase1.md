# Brief — implement: docs-lifecycle-sync, Phase 1 ONLY (Inventory Sweep)

**Work item:** `.project/active/docs-lifecycle-sync/` — read `spec.md` (R1–R7) and `plan.md`
(Phase 1) in full before touching anything. Method referent:
`.project/completed/20260720_constraint-lifecycle-docs-f1/spec.md` §2–§3 — match that
register's discipline (per-claim disposition STALE/ACCURATE/AMBIGUOUS/GAP, every STALE
verdict carrying the code citation that proves it).

**Scope guard:** Phase 1 only. Produce the register + apply SMALL in-place STALE fixes.
Whole-doc work (spec R6: docs 04/24) is Phase 2 — register those claims, do NOT fix them.
Stop after committing Phase 1; do not start Phase 2.

**Baseline:** merged main `936315c`, branch `docs-lifecycle-sync` (you are on it). Docs and
`.project/` only — no `src/`, no `tests/` changes.

**Intent (owner-approved spec, orchestrator-relayed):** make every claim in
`docs/architecture/` agree with merged main. Corrections shrink or amend the stale claim in
place with a citation — never "this used to say X" prose. No release-readiness claims.

**Orchestrator-verified facts (2026-07-24, at `936315c`) — seed the sweep, but re-verify
anything you put in the register yourself:**
- `SNAPSHOT_FORMAT_VERSION = 5` (`snapshot/__init__.py:30`); `_validate_source_referents`
  (`snapshot/loader.py:912`, called at `:837`).
- `CATALOG_SCHEMA_VERSION = "2.0.0"` (`contracts/versions.py:18`); docs 28/29 carry NO
  version mention.
- Severity: only public mention is doc 27:86 (one changelog line); contract lives in
  `analysis/diagnostic_screen.py`, `_upstream_pins.py:24-27`, `loader.py:588-591`.
- Resolver refs to deleted architecture (`input_resolver`, `resolve_input`, `AGG_STRATEGIES`,
  `DesignAttributeLookup`) in exactly these files: docs 03, 04, 05, 24, `overview.md`,
  `verification-matrix.md`. Zero docs mention `producer_resolution`/`resolve_producer`/
  `producer_completeness`.
- Matrix has 274 REQ rows — unchanged through the whole epic.
- `written_qualifier` fields (`extraction/usage_extractor.py:97-108`) and trust manifest
  (`contracts/manifest.py`) have no doc coverage.
- Two `-O` test failures and the ruff-format/mypy baselines are pre-existing; not your concern.

**Deliverables (in order):**
1. `.project/active/docs-lifecycle-sync/inventory.md` — the register, organized by sweep
   (A version/format literals, B snapshot/catalog/trust, C semantics incl. module_kind bool
   flags + doc-19 table, D resolver architecture). Every row: claim file:line, disposition,
   citation, fix-disposition (fixed-here / Phase-2 / Phase-3 / Phase-4 / GAP-filed).
2. Small STALE fixes applied in place (sweeps A–C class; R5 override-correctness notes too).
3. Run the plan's Phase 1 validation greps and record results in the register.
4. One commit: `docs-lifecycle-sync Phase 1: inventory register + in-place STALE fixes`
   (+ `Co-Authored-By: Claude <noreply@anthropic.com>` trailer). Tick the Phase 1 boxes in
   plan.md and fill its Implementation Notes in the same commit.

Finish with `ARTIFACT: .project/active/docs-lifecycle-sync/inventory.md`.
