# DRAFT — sysml-codegen PR #9 description (Item 6 reconciliation)

**Status: DRAFT for Item 13.** Not pushed, not applied to the PR. Reflects Items 1–5 as
landed **locally** on `constraint-exec-epic` plus this Item 6. **No release-readiness
claim** — Items 7–12 are open and Item 13 owns the final composed proof, PR update, and
push.

Landed pin this describes: sysml-codegen through Item 5 (`4c6223c`) + Item 6;
agentic-mbse `4c18d61`; TEAx `d545701`.

---

# CONSTRAINT-EXEC lifecycle: occurrence/demand, shared resolver, Gate B, diagnostics, whole-tree portability (Items 1–5), docs/F1 (Item 6)

**⚠️ Merge order: merge agentic-mbse PR #11 FIRST.** This branch pins `constraint-facts/v2`
and `executable-profile/v4` in `_upstream_pins.py`; merging this before #11 breaks its
`main` (`test_upstream_pins` fails). teax's PR is independent; fusion-tea's `main` push comes
last.

## What this delivers (model-to-graph correctness path)

- **Item 1 — Occurrence/demand integrity.** Occurrence-stable usage identity; recursive
  containment fails with a contextual non-finite/cycle error; deduplicated shared demand
  without overwriting grouping/counts. Superseded nullable-QN and duplicate-demand branches
  deleted.
- **Item 2 — Shared producer resolution + Gate A.** One positive resolver (real producer
  channel, then real design attribute under exact QN) replaces the three drifted
  calculation/constraint/aggregation ladders; direct literal design attributes resolve with
  no passthrough. Audit **Pass with notes** at `039d66e`.
- **Item 3 — Gate B coverage-scope proof.** Append-only constraint extension proven
  **vacuous** with respect to V11; the extension-time coverage check is **deleted**. Final
  generation V11 remains whole-graph strict (`collect_uncovered_params` retained for the
  final generation gate only).
- **Item 4 — Diagnostic severity + modeled-default fidelity.** Versioned severity through
  facts/codecs/validation/codegen with fail-closed skew; signed/unit modeled defaults
  (`-0.1`, `[MW]`) preserved through typed entry points. Audit **Pass with notes** at
  `caa149c`. Moves the agentic-mbse pin `515e08b` → `4c18d61`.
- **Item 5 — Whole-tree snapshot portability (format v5).** Every `source_file` becomes a
  portable `root-N/<relpath>` referent; the loader reconstructs no absolute path and validates
  referent shape. Two-checkout-root generation is byte-identical with no same-machine
  cancellation.
- **Item 6 — Docs + F1 reconciliation.** Public docs corrected to the landed candidate
  (snapshot format v5, profile v4, package floor 0.1.2, the settled final-gate V11 branch);
  duplicate profile-version literals single-sourced. TEAx F1 recorded at `d545701` (the audit
  reference `927a9e1` corrected); complete cross-evaluator report parity confirmed.

## Evidence

- Full suite (license sourced): **3,064 passed / 44 skipped / 0 failed**. Mypy 72 =
  baseline; ruff clean.
- Per-item spec/design/evidence and audits under `.project/active/constraint-lifecycle-*`.
- Snapshot format v5; live and from-snapshot artifacts byte-identical across checkout roots.

## Scope honesty

Items 1–6 close the correctness and documentation path. Package trust/provenance (7),
canonical catalog/store (8), multi-entry bridge (9), producer completeness/stellarator (10),
TEAx evidence durability (11), and legacy/tracking identity (12) are open. The composed
41-case public lifecycle proof is Item 13 and has not run. This description does not claim
release readiness.
