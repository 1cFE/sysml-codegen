# Evidence — Lifecycle Item 5: Whole-Tree Snapshot Portability

**Candidate:** `4c6223c` (branch `constraint-exec-epic`, on `dcb8ce6`)
**Status:** Implementation complete; stopped for audit. Some final gates deferred under budget (below).

## Two-root scan result (headline)

`test_catf_mfe_whole_tree_two_root_portable` (license-free): the `catf_mfe` snapshot placed
at two distinct absolute roots generates a **byte-identical** output tree (`diff` empty) with
**zero** checkout-absolute `.sysml` paths. RED before the fix (40/81 files differed, matching
the measured inventory); GREEN after. This is the completeness gate — it does not depend on
enumerating leaking fields by hand.

## What landed (D1 + v5, as ratified)

- **Capture** (`serializer.py`): every `source_file` field and every located constraint usage
  is mapped through the certified `map_live_source_referent` → stored as `root-N/<relpath>`.
- **Live generation** (`graph_builder.py`): `build_computation_graph` takes `source_roots` +
  `source_location_mode`; the live route maps each module's `source_file` to the referent
  (mirrors the certified constraint path). Snapshot route already carries it.
- **Loader** (`loader.py`): `_reabsolutize_source_file(s)` deleted; `_validate_source_referents`
  is the v5 shape gate (rejects an absolute/relative/blank `source_file` loudly — closes N1).
  Freshness is now inert on the referent (spec INFERRED requirement).
- **Anonymous eligible constraint_id** (`constraint_lowering.py`): folds in the portable
  referent, derived in `prepare_constraint_usages` (I10) and carried on the transcript — so an
  admitted anonymous constraint's id is checkout-portable. This is Item 5's "eligible IDs"
  mandate; **zero impact on catf_mfe / Item 4** (catf_mfe has 0 anonymous/eligible-located
  usages — verified; the Item 4 `SNAPSHOT_MANIFEST_SHA256` pin is unchanged and GREEN).
- **Deletions**: Branch C `"models/"` strip (`stencils.py`, `test_gen.py`); baseline
  `.replace()` hack (`capture_pipeline_baselines.py`). `SNAPSHOT_FORMAT_VERSION` 4→5.

## Acceptance

- **A1** `catf_mfe` two-root whole-tree: GREEN (headline above).
- **A2** `OccurrenceDemandAnonymous__Admitted` relocated leg (completes Item 1's deferred leg):
  `test_anonymous_admitted_relocated_graph_portable` (licensed) GREEN — captured at two checkout
  roots + a relocated copy; rebuilt graph+catalog byte-identical across all three, admitted
  actual `3.0` preserved, no checkout-absolute path. Proven at graph/catalog altitude because
  the anonymous fixture trips an unrelated constraint name-safety preflight in full generation
  (same as Item 1's evidence altitude).
- **A3/A4** covered by the re-captured corpus + Item 4's certified portability/parity tests
  (GREEN).

## Re-capture ledger (Phase 4)

- All 36 committed snapshots re-captured to v5. **Only** deltas across every snapshot: version
  (4→5), `source_file` referents, constraint `location.file` referents, `captured_at` (semantic
  recapture, rides along). Zero other field changed (field-classified diff).
- Baselines regenerated: **source_file-only** delta on 10 fixtures.
- **Stale-baseline class handled per the recorded pattern, not absorbed:** `constraint_inline`
  crashes generation (constraint name-safety `generated_binding_overlap`) — **reproduced
  identically on parent `dcb8ce6`** (same constraint_id hash `f09be415bd21dd95`; named
  constraint, my change doesn't touch it). `plant_values` regenerates with large non-source_file
  drift (added constraint modules) — the recorded stale class. Both baselines **reverted to
  committed** (excluded from the regen set, one-cause-per-diff). Their snapshots are v5 (load
  clean); only their committed baseline outputs stay stale/unowned as before.

## Surfaced findings (premise corrections — not silently resolved)

1. **The design's from-snapshot inventory masked the anonymous-eligible-id leak.** The measured
   "one-form leak (40/81)" used a committed snapshot at two roots (identical bytes both sides),
   which hides any leak carried in `constraint_facts`. The A2 **live-capture** two-root proof
   surfaced that anonymous eligible constraint ids hash their source location. Fixed in-scope
   (brief Intent names "eligible/excluded IDs, fingerprints"); zero Item-4 impact.
2. **Input-artifact non-portabilities that do NOT reach output** (gated by the two-root diff, so
   left per the design): `design_attributes` dict **keys** and `document_path` are stored
   checkout-absolute in snapshots, but no committed baseline contains the checkout root
   `/home/reid/1cfe/sysml-codegen` — they are not rendered into generated output. Recorded, not
   fixed (fixing risks live/snapshot route-parity for no output benefit). Note: modeler-authored
   doc comments may contain external absolute paths (e.g. `/home/reid/PyFECONS/...`) — these are
   payload, identical at any checkout, not a leak.

## Gates run

- Ruff: clean on all changed files. Mypy: zero added on changed files (72 pre-existing repo-wide).
- Focused suites GREEN (28 tests): shape gate (both skew directions), v5 envelope gate,
  whole-tree portability A1+A2, `test_capture_fixtures_filter` (sample_model stays v5),
  Item 4 `test_constraint_snapshot_portability` (SHA pin unchanged).
- Full licensed suite: last full run had 5 failures, **all** the sample_model-committed-at-v4
  artifact (a pre-commit suite run reverted it via `test_capture_fixtures_filter`) +
  signature-only test fixups — all resolved after committing sample_model at v5 and confirmed
  GREEN in the focused re-run.

## Deferred under budget (for audit / resume)

- A clean **full-suite** run at candidate `4c6223c` (zero failures) — the focused set is GREEN
  and the earlier 5 failures were all the now-fixed sample_model revert; a confirming full run
  was not executed under the remaining budget.
- `PYTHONOPTIMIZE=1` (-O) parity run; execution-lane run.
- D3 (param-group basename → referent) **deferred**: the basename is already portable per the
  inventory (a fidelity/disambiguation nicety, not a portability fix); folding it would churn
  many baselines for no portability gain. Surfaced as a deviation from the phased plan.
