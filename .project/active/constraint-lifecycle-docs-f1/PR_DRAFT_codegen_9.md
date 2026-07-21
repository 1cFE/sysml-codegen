# sysml-codegen PR #9 description (FINAL — Item 13 composed proof complete)

**Status: FINAL.** All 14 lifecycle items complete: Items 1–12 certified, and Item 13's composed
41-case public proof (register row 17) passes **41/41** at the pinned set. Merge pending human.

Landed pin: sysml-codegen **`7526665`** (certified src surface); branch tip **`d7ad714`** adds the
Item 13 evidence + fixtures only (`git diff 7526665 d7ad714 -- src tests` is empty).
Companion: agentic-mbse `4c18d61`; teax `c342b10`.

**⚠️ Merge order — merge agentic-mbse PR #11 FIRST.** This branch pins `constraint-facts/v2` and
`executable-profile/v4` in `_upstream_pins.py`; merging before #11 breaks `main`
(`test_upstream_pins` compares each pin against the installed `agentic_mbse`). teax's PR is
independent; fusion-tea / stellarator stay local.

## What this delivers (model-to-graph correctness + generation + composed proof)

- **Item 1 — Occurrence/demand integrity.** Occurrence-stable identity; recursive containment and
  non-finite multiplicity fail with named errors; deduplicated shared demand without overwriting.
- **Item 2 — Shared producer resolution + Gate A.** One positive resolver (real producer channel,
  then real design attribute under exact QN) replaces the three drifted ladders; direct literal
  design attributes resolve with no passthrough.
- **Item 3 — Gate B coverage-scope.** Append-only extension proven vacuous w.r.t. V11; the
  extension-time check deleted; final generation V11 remains whole-graph strict.
- **Item 4 — Diagnostic severity + modeled-default fidelity.** Versioned severity fail-closed on
  skew; signed/unit modeled defaults preserved through typed entry points. Moves the agentic-mbse
  pin to `4c18d61`.
- **Item 5 — Whole-tree snapshot portability (format v5).** Portable `root-N/<relpath>` referents;
  two-checkout-root generation byte-identical, no same-machine cancellation.
- **Item 6 — Docs + F1 reconciliation.** Public docs corrected to the landed candidate; profile
  literals single-sourced.
- **Item 7 — Package trust/provenance.** Seal/verify, symlink/provenance, trusted-verifier bootstrap.
- **Item 8 — Canonical embedded catalog.** Stock codegen/TEAx catalog seam; no materializer,
  no alternate schema, no predicate-text reconstruction.
- **Item 9 — Multi-entry bridge.** Zero/one/many typed channel mappings; excluded-only invents no inputs.
- **Item 10 — Producer completeness + stellarator.** Instance-scoped aggregation producers; five
  verdicts + six bit-exact anchors; WI-027 D7 passthroughs removed.
- **Item 11 — TEAx evidence durability** (teax `c342b10`). Write-phase signal, evidence immutability,
  file-backed persistence/harvest.
- **Item 12 — Legacy/tracking identity.** Grandfathered product path fails closed at generate;
  dead `tracking_key` deleted.
- **Item 13 — Composed public proof (row 17).** 41/41 (rerun 22 / compose 19); the sealed artifact
  thread (generate→seal→trusted-load→prepared+file-backed evaluate→persist→resume/query); IFE
  2,301-point + stellarator five-constraint consumer acceptances; 16 negative mutations at their
  boundaries; 6 full-tree byte checks.

## Evidence

- **Full licensed suite: 3115 passed, 47 skipped.** Optimized (`-O`): 2 pre-existing baseline
  failures. `ruff check` clean; mypy zero-new (src byte-identical to `7526665`).
- Composed proof: `.project/active/constraint-lifecycle-composed-proof/{release-readiness.md,
  evidence-coordinate-register.md}`. Per-item spec/design/evidence/audits under
  `.project/active/constraint-lifecycle-*`.
- Snapshot format v5; live and from-snapshot artifacts byte-identical across checkout roots.

## Scope honesty

All 14 items complete and the composed proof passes 41/41. One general gap
(`[NESTED-OCCURRENCE-OVERRIDE]`, nested-usage `:>>` override) is filed to the Item-10
occurrence-materialization family — nested shapes only; not a row requirement and not a proof
blocker. Consumer-repo delivery (fusion-tea, stellarator) is a separate human decision.
