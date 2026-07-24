# Inventory — Docs Lifecycle Sync, Phase 1 sweep register

**Baseline:** merged main `936315c` (sysml-codegen). Every citation below was re-verified
against `936315c` in this run. Method referent: `20260720_constraint-lifecycle-docs-f1/spec.md`
§2–§3 — per-claim disposition (STALE / ACCURATE / AMBIGUOUS / GAP), every STALE verdict
carrying the code citation that proves it.

**Scope of this register:** all four sweeps (A version/format literals, B snapshot/catalog/
trust, C semantics incl. `module_kind` bool flags + doc-19 dispatch table, D resolver
architecture). Phase 1 *applies* only the small, isolated STALE fixes and the R5 override-
honesty note. Whole-doc and grouped work is registered here with its downstream phase and is
**not** touched in this commit.

**Fix column vocabulary:** `fixed-here` (applied in this Phase-1 commit) · `Phase-2` (resolver
family + module_kind sweep) · `Phase-3` (severity doc) · `Phase-4` (portability matrix row) ·
`GAP-filed` (no stale claim exists; coverage gap recorded, a filing decision, not required by
this item).

---

## ⚠ Surfaced: brief-vs-plan boundary on the `module_kind` sweep (sweep C)

The brief's deliverable 2 lists "sweeps A–C class" small STALE fixes as Phase-1 work. The
plan's Phase 2 explicitly assigns the `module_kind` bool-flag sweep to Phase 2, bundled with
the matrix "so doc 05 and the matrix don't split" (`plan.md:100-102`). These two instructions
conflict for the sweep-C bool-flag rows (C1–C9 below).

Resolution taken (owner not reachable — surfaced loudly here per capture-fidelity rule 4, not
resolved silently): **defer the `module_kind` fixes to Phase 2**, matching the plan's specific
bundling. Reasons: (1) the retired flags live in `05-module-factory.md`, which is itself a
Phase-2 resolver-rewrite target, so an isolated Phase-1 edit would collide; (2) doc 05 and
matrix REQ-MF-03 must change together to avoid a split, which is exactly a whole-pass change,
not a small isolated fix. Sweep-C rows are registered STALE with fix = `Phase-2`. If the owner
wants them pulled into Phase 1, they are mechanical (flag name → `module_kind`) and the rows
below carry the citations.

---

## Sweep A — version / format literals

| # | Claim (file:line) | Disposition | Citation proving it | Fix |
|---|---|---|---|---|
| A1 | `27-snapshot-generation.md:37` — "Current: **5** (`…SNAPSHOT_FORMAT_VERSION`, `snapshot/__init__.py:28`)" | STALE (citation line) | Constant is at `snapshot/__init__.py:30`, not `:28` (moved since Item 6). Value `5` is correct. | **fixed-here** → `:30` |
| A2 | `27-snapshot-generation.md:137` — profile "`executable-profile/v4`" (`_upstream_pins.py:33`) | ACCURATE | `PROFILE_SEMANTIC_VERSION = "executable-profile/v4"` (`_upstream_pins.py:33`) | none |
| A3 | `27-snapshot-generation.md:92` — "the current 5 is a hard error … no cross-version coexistence" | ACCURATE | `SNAPSHOT_FORMAT_VERSION = 5` (`snapshot/__init__.py:30`) | none |
| A4 | `verification-matrix.md:531` (REQ-SNAP-09) — "(current: 5) … no cross-version coexistence" | ACCURATE | `snapshot/__init__.py:30` | none |
| A5 | `overview.md:36` — snapshot format "carries a `snapshot_format_version` that hard-errors on mismatch" | ACCURATE | version gate in `snapshot/loader.py` | none |

Note: doc 27's version literals were already corrected to v5/v4 by Item 6 (S1–S8). This sweep
confirms they survived Items 7–13's landings. The only residue is the A1 line-number drift.

## Sweep B — snapshot / catalog / trust surfaces

| # | Claim / area (file:line) | Disposition | Citation | Fix |
|---|---|---|---|---|
| B1 | Catalog schema version — docs 28/29 carry **no** version mention | GAP | `CATALOG_SCHEMA_VERSION = "2.0.0"` (`contracts/versions.py:18`); no stale doc claim exists (nothing says "1.x") | GAP-filed (matrix GAP-row candidate per spec R2; not required this item) |
| B2 | `written_qualifier` extraction fields — no doc coverage | GAP | `stored_source_written_qualifier` / `source_written_qualifier` (`extraction/usage_extractor.py:97-108`) | GAP-filed (owed writing; no stale claim to amend) |
| B3 | Trust manifest / anchor / reseal provenance — no doc coverage | GAP | `build_generation_manifest` (`contracts/manifest.py:31`), `check_reseal_provenance` (`:56`), `MANIFEST_REL_PATH` (`:19`) | GAP-filed |
| B4 | Diagnostics severity **contract** — no public doc beyond one changelog line | GAP (Item 6 G1) | `screen_extraction_diagnostics` (`analysis/diagnostic_screen.py:51`), BLOCKING/ADVISORY skew (`:59,:64`), `_upstream_pins.py:24-27`, `snapshot/loader.py:588-591` | **Phase-3** (new reference doc) |
| B5 | `27-snapshot-generation.md:86` — "v4 carried the diagnostic-severity field … v5 replaced `source_file` with the portable `root-N/<relpath>` referent" | ACCURATE (changelog) | matches `snapshot/__init__.py:30` + Item 6 S2 referent rewrite | none |
| B6 | Portability referent-shape gate + whole-tree portability — **no** verification-matrix REQ-SNAP row (family stops at REQ-SNAP-20) | GAP (Item 6 G2) | `_validate_source_referents` (`snapshot/loader.py:912`, called `:837`); portability tests `tests/conformance/test_constraint_snapshot_portability.py` | **Phase-4** (matrix row + recount) |

## Sweep C — semantics (module_kind bool flags, doc-19 dispatch table)

Retired flags `is_computed_attribute` / `is_aggregation` have **zero live surface** in `src/`
(grep empty); they were replaced by `module_kind` (`resolution/models.py:229`; `ModuleKind`
enum `:197`) at CONSTRAINT-EXEC Item 6. Rows C1–C9 defer to Phase 2 (see surfaced note above).

| # | Claim (file:line) | Disposition | Citation | Fix |
|---|---|---|---|---|
| C1 | `05-module-factory.md:20` (REQ-MF-03) — "SHALL set `is_computed_attribute=True`" + assert text | STALE | flag retired; `module_kind` at `resolution/models.py:229` | Phase-2 |
| C2 | `05-module-factory.md:41-42` — `is_computed_attribute: bool` / `is_aggregation: bool` field decls | STALE | fields absent from `PipelineModule` (`resolution/models.py:209-229`) | Phase-2 |
| C3 | `05-module-factory.md:110` — "**Flags**: `is_computed_attribute=True`" | STALE | `resolution/models.py:229` | Phase-2 |
| C4 | `05-module-factory.md:128` — "`is_computed_attribute=True, compilability=FULLY_COMPILABLE`" | STALE | `resolution/models.py:229` | Phase-2 |
| C5 | `05-module-factory.md:206` — "**Flags**: `is_aggregation=True`" | STALE | `resolution/models.py:229` | Phase-2 |
| C6 | `05-module-factory.md:228` — "`is_aggregation=True`" | STALE | `resolution/models.py:229` | Phase-2 |
| C7 | `22-output-schema-rules.md:179` — "`PipelineModule` … Module with is_aggregation flag" | STALE | `resolution/models.py:229` (`module_kind`) | Phase-2 |
| C8 | `verification-matrix.md:362` (REQ-MF-03) — "SHALL set `is_computed_attribute=True`" | STALE | `resolution/models.py:229`; bundle with C1 so doc 05 + matrix don't split | Phase-2 |
| C9 | `09-data-models.md:71,301` — "`module_kind` … **replaced** the two accreted Boolean flags" | ACCURATE | retirement narrative, matches `resolution/models.py:197-229` | none |
| C10 | `19-ast-dispatch-invariant.md:98,132` — prose dispatch-site table | AMBIGUOUS | doc self-marks the table "illustrative … predates the cross-repo moves" and points to the authoritative `DUAL_CHECK_SITES` (`tests/conformance/test_ast_dispatch_invariant.py`); R7 asks to reconcile the prose to it | Phase-2 (R7 second half) |

## Sweep D — resolver architecture (deleted module still described as live)

`resolution/input_resolver.py` is **DELETED**; `resolve_input` / `AGG_STRATEGIES` /
`DesignAttributeLookup` have **zero live surface** in `src/` (grep empty). Item 2 replaced the
dual ladders with one registry-owned ordered table: `resolve_producer`
(`resolution/producer_resolution.py:616`), `KEY_FORMS` (`:527`), strict/lenient split only at
`TerminalPolicy` (`:84`); producer completeness at `check_producer_completeness`
(`resolution/producer_completeness.py:98`). **No** doc mentions
`producer_resolution`/`resolve_producer`/`producer_completeness`. Whole family → **Phase-2**
(docs 04/24 whole-doc; 03/05/overview/matrix in-place references). Registered per-file below;
not fixed in Phase 1.

| # | File — stale-ref locations | Disposition | Citation | Fix |
|---|---|---|---|---|
| D1 | `04-input-resolver.md` — whole doc (309 lines) documents the deleted module: `resolve_input`/`AGG_STRATEGIES` at `:5,12,30,34,36,41,53,187,269,284,290,295` | STALE | `input_resolver.py` deleted; `resolve_producer` (`producer_resolution.py:616`) | Phase-2 (replace w/ producer-resolution reference doc) |
| D2 | `24-dual-resolution-architecture.md` — pre-unification narrative: `resolve_input`/`AGG_STRATEGIES` at `:26,35,36` (+ dual-resolution framing throughout) | STALE | unified ladder `producer_resolution.py:616`; no dual ladders | Phase-2 (amend to unified-ladder narrative) |
| D3 | `03-resolution-overview.md` — `resolve_input`/`input_resolver.py` at `:21,54,105,149,155,167,177,200,212,221,224,242,246,247` | STALE | `producer_resolution.py`; `input_resolver.py` deleted | Phase-2 (in-place refs) |
| D4 | `05-module-factory.md` — `resolve_input(AGG_STRATEGIES)` at `:8,157-159,174-176,192-195,247,251,259` | STALE | `producer_resolution.py:616` | Phase-2 (in-place refs; same doc as C1–C6) |
| D5 | `overview.md` — `resolve_input()`/`input_resolver.py` at `:66,111,178` | STALE | `input_resolver.py` deleted | Phase-2 (in-place refs) |
| D6 | `verification-matrix.md` — REQ-DRA/REQ-IR/REQ-RES rows citing `resolve_input`/`AGG_STRATEGIES`/`input_resolver.py`: `:218,223,225,226,326,330-336,509,514` | STALE | `producer_resolution.py`; `input_resolver.py` deleted | Phase-2 (in-place rows) |

## R5 — override-capture honesty (nested-occurrence limitation)

Gap `[NESTED-OCCURRENCE-OVERRIDE]` (BACKLOG.md:168): a `:>>` override on a usage nested inside
an *instantiated* part def is captured **definition-relative** while demand resolves
**occurrence-relative**, so the supplied-value materializer never matches and the value is lost
(calc → silent manual-required drop; constraint → halt under strict INV-2). Probe fixture:
`tests/fixtures/nested_occurrence_override_probe/`.

| # | Claim (file:line) | Disposition | Citation | Fix |
|---|---|---|---|---|
| R5a | `modeling-assumptions.md:336-353` — "Cross-Part Supplied Values": lists four *supported* value-provision shapes (incl. (b) a bare override block on a nested usage) with **no** nested-occurrence caveat — reads as "all these capture correctly" | STALE (implies correctness) | `[NESTED-OCCURRENCE-OVERRIDE]` (BACKLOG.md:168); probe `tests/fixtures/nested_occurrence_override_probe/PROVENANCE.md` | **fixed-here** (add def-relative limitation note) |
| R5b | `modeling-assumptions.md:294,376` — deep-path row "`:>> pv_module.wattage=400.0` … Traversed through hierarchy to leaf attribute" / "applies to all instances in the array" | ACCURATE for the array-uniform deep-path shape; not the nested-occurrence shape | array deep-path is a different, working path; the limitation note at R5a is the single honest home | covered by R5a note |
| R5c | `01-extraction.md:167-168` — "Deep-path overrides … are captured in `design_overrides` with `is_deep_path=True`" | ACCURATE | this is *extraction* capture (def-relative), which is correct; the loss is downstream at materialization, not here | none (no correctness claim about materialization) |

---

## Phase 1 fixes applied (in-place)

1. **A1** — `27-snapshot-generation.md:37` citation `snapshot/__init__.py:28` → `:30`.
2. **R5a** — added the nested-occurrence def-relative limitation note to
   `modeling-assumptions.md` Cross-Part Supplied Values section, citing the backlog marker and
   probe fixture.

## Phase 1 validation greps (run at `936315c`)

- **Version literals** — `grep -rnE 'snapshot_format_version|executable-profile/v[0-9]|2\.0\.0' docs/`:
  every live literal matches its pinned constant. `snapshot_format_version` current = **5**
  (`snapshot/__init__.py:30`); profile = **v4** (`_upstream_pins.py:33`). No stale version
  literal remains. Catalog `2.0.0` appears in **no** doc (B1 GAP, not a stale literal).
- **`is_computed_attribute|is_aggregation`** — 9 live-claim hits remain (C1–C8 + doc 09
  narrative C9); **deferred to Phase 2** per the surfaced boundary note. Not yet zero (that is
  Phase 2's exit gate, plan.md:108).
- **`input_resolver|resolve_input|AGG_STRATEGIES|DesignAttributeLookup`** — present in 6 doc
  files (D1–D6); **deferred to Phase 2** (plan.md:106). Not yet zero (Phase 2's exit gate).
- **Nested-occurrence override capture** — after the R5a note, no doc implies nested-occurrence
  override capture works.

**What we know after Phase 1:** the full claim surface across `docs/architecture/` is
enumerated with dispositions and citations. Remaining phases are additive writing (Phase 3
severity doc, Phase 4 matrix row, Phase 5 EXPLAINER) and the grouped Phase-2 resolver +
module_kind rewrite — not fresh discovery.


---

## Phase 2 dispositions (closed 2026-07-24)

Sweep-C `module_kind` rows: **C1–C8 → fixed** (`05-module-factory.md` field decl, REQ-MF-03,
flag mentions, concrete-example blocks; `22-output-schema-rules.md:179`; matrix REQ-MF-03 `:362`
— all `is_computed_attribute`/`is_aggregation` → `module_kind`/`ModuleKind`). **C9** ACCURATE,
untouched (retirement narrative, correct dated history). **C10 → fixed** (doc 19 dual-check prose
table reconciled to `DUAL_CHECK_SITES`: three entries — agentic-mbse `_decompose_node` if/if/if,
`_extract_single_binding` / `_extract_default_value` elif; stale "8 functions across 6 files" count
dropped; the two promoted elif rows removed from the "Other Sites" table).

Sweep-D resolver rows: **D1 → fixed** (`04-input-resolver.md` renamed to `04-producer-resolution.md`
and rewritten). **D2 → fixed** (doc 24 rewritten to the unified narrative; dual-path story kept only
as marked dated history). **D3–D5 → fixed** in place (`03`, `05`, `overview.md` reframed to
`resolve_producer`). **D6 → fixed** (matrix DRA/IR banners + rows re-projected; dead-test citations
replaced). Inbound `04-input-resolver` links across all of `docs/` repointed.

**Exit greps (run at `936315c`):**
- `grep -rn 'input_resolver|resolve_input|AGG_STRATEGIES|DesignAttributeLookup' docs/architecture/`
  — zero LIVE claims. Residual = dated history only: doc 24 "Dated history" block (`:140,145,146`),
  matrix DRA deletion note (`:218`).
- `grep -rn 'is_computed_attribute|is_aggregation' docs/architecture/` — zero LIVE claims.
  Residual = `09-data-models.md:71,301` (ACCURATE retirement narrative, register C9).
