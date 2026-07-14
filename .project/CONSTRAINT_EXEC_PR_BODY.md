# CONSTRAINT-EXEC: modeled assertions execute — lowering, generation, contracts, snapshot v3 (Items 4–9, 13, 14)

**⚠️ Merge order: merge agentic-mbse's `constraint-exec-epic` PR FIRST** — this branch imports
symbols added there (coordinated pair). teax's PR is independent; fusion-tea's `main` push
comes last, after this merges.

## What this delivers

Modeled physical limits (`assert constraint`) now execute inside the generated forward model.
Before: constraints died at a drop-report warning and every design study re-implemented the
judgment by hand. After:

- **Lowering (Items 4–5):** a part-instance index (subtype closure + cardinality expansion)
  finds every concrete owner; a new pipeline phase expands assertions per instance, strictly
  resolves actuals (unresolved = generation error, never synthesis), and mints deterministic
  `constraint_id`s.
- **Generation (Items 6–7):** `module_kind` enum + seam refactor; constraint modules with a
  Kleene three-valued compiler (`satisfied | violated | indeterminate` as data, never
  exceptions), an exact-schema report aggregator guaranteed to be an exit ancestor, and a
  graph-owned constraint catalog. Module identity = class-per-assertion ([OWNER]).
- **Snapshot v3 (Item 8):** constraint facts are load-bearing in snapshots; live and
  from-snapshot artifacts byte-identical; stale/sectionless snapshots rejected loudly.
- **Contracts (Item 9):** `PackageContract` seals generated artifacts (content hashes,
  verified on load, stdlib-only in-package verifier); graph-only `ModelContract` with semantic
  fingerprint.
- **Calc-seam cutover (Item 13):** `ExpressionAST` retired onto the shared `ExpressionIR`
  under byte-identity gates.
- **Migration + acceptance (Item 14):** drop manifest and blanket warnings retired with a
  proven 1:1 migration mapping; docs flipped; the IFE sweep's hand-coded viability rule is
  DELETED — the generated assertion replays the full 2301-point grid with **2294 exact matches;
  the 7 divergences are exactly the `eta*gain == 10.0` boundary where the hand rule's strict
  `>` was unfaithful to the modeled `>=`** ([OWNER] ratified 2026-07-13: the hand rule's bug,
  surfaced as data).

## Evidence

- All items audit-certified with orchestrator-executed probes (mutation RED/GREEN where guards
  matter). Independent findings audit (owner session, 2026-07-13) reproduced every sampled
  claim exactly — both mutation probes verbatim, all gates to exact counts:
  `.project/completed/20260713_epic_constraint_execution_audit_independent.md`.
- Gates: **2330 passed / 23 skipped** (license env), **mypy 76 = baseline**, **ruff clean**.
- Epic + all item artifacts archived under `.project/completed/20260713_*`; follow-ons CE-F1/F2
  registered in BACKLOG (CE-F3 fixed in teax).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
