# Run Report: Migration, Docs, and IFE Acceptance (CONSTRAINT-EXEC Item 14)

**Status:** sysml-codegen (S-CODEGEN) phases complete. S-MBSE, S-TEAX, S-FUSION pending.
**Branch:** `constraint-exec-epic`

## W1 — Gain fix + grandfather re-land

- Added the instance-self-redefinition tier to `_match_override`
  (`resolution/supplied_values.py`) and the constraint-actual demand widening it
  needs (`collect_bare_actual_demand`, `analysis/constraint_lowering.py`) —
  discovered mid-implementation: the materializer only ever scanned calc-usage
  bindings, so a constraint's own bare-name actual with no calc-usage binding of
  its own (fusion_tea's self-named `in gain = gain`) was invisible to it
  regardless of the tier fix.
- `plant_values`' `gain` turned out to be a structurally different shape (a
  plain base-def literal default, not an instance `:>>` override) — B2 was false
  for that fixture specifically. Owner-approved fix (option 2, scope-fenced):
  one additional definition-scoped `resolve_actual` rung, the constraint-actual
  twin of ADR-001's `LIBRARY_DEFAULT` — a modeled value recognized via a third
  key shape, not synthesis.
- **Byte-identity result:** re-generated all 29 committed snapshots; exactly
  `plant_values` and `fusion_tea` changed structurally (the other 27 diffs were
  `captured_at`-only, reverted). Re-ran the gate again after W2's
  `dropped_constraints` key removal — same two files, for a second, expected
  reason.
- `GRANDFATHERED` emptied in `scripts/capture_extraction_snapshots.py` (kept as
  a named frozenset, not deleted, for a future real gap).
- Commits: `9dcd1ab` (mechanism), `8d337bd` (def-scoped rung + re-land).

## W2 — Manifest→catalog mapping test + retirement

- `tests/conformance/test_constraint_migration_mapping.py` (11 tests): proves,
  for every constraint-bearing fixture (`catf_mfe_model`, `fusion_tea`,
  `plant_values`, `wi014_toy`, `constraint_inline`, `constraint_multi_instance`),
  that every usage `collect_constraint_manifest()` sweeps has a catalog carrier
  — an eligible concrete entry, an unassessed record, or a named requirement/
  satisfy exclusion. Landed and green **before** any retirement (commit
  `cd7a204`).
- Retired the drop-manifest report/render/serialize/replay surface
  (`report_dropped_constraints`, `render_constraint_report`,
  `manifest_to_records`/`manifest_from_records`, the two blanket warnings, the
  `constraint_manifest` ctx field and its snapshot pass-through). **Deviation
  (owner-confirmed):** `collect_constraint_manifest` itself and its kind
  vocabulary (`ConstraintManifestEntry`/`ConstraintKind`/`OwnerKind`) were kept,
  not deleted, since the kept mapping test calls the sweep directly. Design
  Appendix B literally named it as a deletion target; the mapping test's
  dependency takes precedence.
- Re-anchored `test_extractor.py`'s REQ-EXT-09 family and
  `test_snapshot_contract.py`'s wi014 round-trip onto the catalog; deleted
  `tests/unit/test_constraint_report.py` (its whole subject retired).
- **grep-clean (INV-B):** zero hits for `report_dropped_constraints`/
  `render_constraint_report`, `"not executable"`, and `dropped_constraints` in
  `src/`.
- Commits: `cd7a204` (mapping test), `b994112` (retirement + re-anchor).

## W3 — Docs (sysml-codegen slice; W3a)

- Flipped `docs/architecture/modeling-assumptions.md` §8 from "constraints are
  not executable" to the three profile outcomes (ADMIT/BLOCK/unassessed), the
  verified block list, and the real-equality → explicit two-inequality-band
  idiom.
- Added `docs/architecture/reference/28-constraint-lowering-and-catalog.md`
  (lowering phase incl. Item 14's def-scoped rung, catalog assembly, contracts
  seam pointer; explicit pointer to agentic-mbse/teax for what's documented
  there instead of duplicated here).
- Updated `reference/01-extraction.md` and `reference/02-orchestration.md`
  cross-refs; added the **CL — Constraint Lowering & Catalog** family (5 rows,
  explicitly a partial register, not a full Items 5-9 sweep) to
  `verification-matrix.md`, backed by 5 new `@pytest.mark.req` markers.
  Recounted index/summary numbers from the actual table (259→264 total,
  30→31 families, 66→71 test files).
- **W3b (agentic-mbse) / W3c (teax): pending** — parallel sessions, Appendices
  A/B.
- Commit: `ccfe9db`.

## W4 — IFE acceptance (S-FUSION)

**Pending.** Not startable until this repo's W1 (done) and teax's W5b loader
seal wiring (parallel, S-TEAX) both land, and Items 10-12 are green on the
branch. The acceptance table, boundary-row disposition, and prepare-once
benchmark land under fusion-tea's harness dir per Appendix C; link here once
committed.

## W5 — Seam dispositions

- **W5a (GENERATOR_MISMATCH, this repo):** disposition = document-and-remove.
  `GENERATOR_MISMATCH` was defined, exported, and named in `verify_package`'s
  `strict` fatal-check, but no call path ever produced it — no caller-supplied
  expected generator version exists to compare `seal["generator_version"]`
  against, unlike `runtime_version`. Chose not to wire a new comparison axis
  specifically to avoid touching `verify_package`'s signature while the
  parallel teax session wires its loader against that exact signature
  (`verify_package(dir, name, runtime_version, strict)`). Removed the dead
  expectation from the `strict` check, added a reserved-seam comment, added a
  confirming test. Commit `78951a4`.
- **W5b (teax loader seal wiring) / W5c (tracking-key note): pending** —
  S-TEAX, Appendix B.

## Prepare-once benchmark

**Pending** — lands with W4 (S-FUSION), on the real IFE package.

## Naming-divergence note (boxed decision, not a premise conflict)

Concept: "source record" = per applied *usage*. Landed catalog:
`ConstraintCatalogSourceRecord` = per *definition*, with the per-usage identity
living on the concrete entry / unassessed record instead. The manifest→catalog
mapping test proves the per-usage join through those two carriers; the
divergence is a naming gap between the concept's vocabulary and the shipped
field, not a concept amendment and not an Item 7 rework. Invariant **met as
written** — no amendment needed.

## Gates (sysml-codegen, as of commit `78951a4`)

- Full suite: 2330 passed / 23 skipped, 7 deselected.
- `ruff check src/`: clean.
- `mypy src/`: 76 errors (baseline, unchanged across all five phases).
- Byte-identity: exactly `plant_values`/`fusion_tea` differ from the pre-Item-14
  baseline; both changes are structural and expected (gain fix, then
  `dropped_constraints` key removal).

## Next steps

1. S-MBSE and S-TEAX land their doc/wiring work (parallel, in progress).
2. S-FUSION runs last, after S-TEAX's W5b and Items 10-12 are confirmed green.
3. Re-run this Phase 6 reconcile once S-FUSION's acceptance table lands, to
   close the epic's remaining Success Criteria boxes (Acceptance, full
   three-repo doc/suite checks).
