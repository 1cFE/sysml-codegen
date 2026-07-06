# Audit: Item 11 — Derived-Attribute Alias Surfacing (SC-7)

**Verdict:** PASS / Certify
**Audited:** 2026-07-06
**Branch:** upstream-findings-epic
**Commits:** `4f6ba40` (feat), `0672cae` (docs) — HEAD

---

## Summary

Item 11 delivers what it specified. The modeler's EXPOSE_PURE name now reaches
both the graph (`ComputationGraph.output_aliases`) and the pipeline YAML (exit-line
filename), for both shapes, and the shape-A malformed-refs warning retires for the
resolvable case. Every HARD invariant is implemented and pinned by a live test on a
real committed snapshot (no mocks). The two-commit scope is clean: production +
tests + baselines in the feat commit, docs-only in the second. Three non-blocking
observations are recorded below — all either documented-and-accepted in the design
or pre-existing outside Item 11's scope. None block certification.

The recorded suite gate (1989 passed / 4 skipped / 5 xfailed; ruff src/ 21; mypy
src/ 109) could not be re-run — `uv run` is approval-gated this session, matching
the Item 8–10 audit pattern. Certification rests on the recorded gate plus direct
static inspection of code, tests, baselines, and YAML diffs.

## Findings

### Plan completion

All 5 phases verified complete.

- **Phase 1 (the product).** `OutputAlias` + `ComputationGraph.output_aliases`
  (serialized, no `exclude`) at `resolution/models.py:193,257`. `_build_output_aliases`
  at `graph_builder.py:686` reads both provenance sources, resolves shape B
  `alias_lookup`-first with `scoped_lookup` fallback (C1), splits the dangling filter
  by run mode (D4), stable-sorts by `(instance_path, alias_name)` (INV-5). Threaded
  through **all three** build sites: live (`pipeline_builder.py:813`), snapshot
  (`graph_rebuild.py:150`, F-A), and the test factory (`test_factory_purity.py:493`).
  `owning_part_leaf` extracted to `core/qualified_names.py:140` and called from the
  two `output_registry_builder` sites + the builder (no drift). `scoped_alias_items()`
  read accessor at `output_registry.py:170`.
- **Phase 2 (reroute).** `_build_attribute_resolution_map` splits EXPOSE_PURE on
  `ca.is_on_part_definition` (`graph_builder.py:1006`). Shape A → LITERAL + a
  `_scoped_alias`-leaf-gated warning; shape B unchanged (`_resolve_expose_pure`, the
  `:796` branch byte-identical). `test_wi014_toy.py` flipped to assert silent+surfaced.
- **Phase 3 (YAML).** `_build_alias_filename_map` (first-wins over the sorted list, M4)
  + `_build_exit_points(modules, alias_filenames)` (required param, no papering default)
  + template `pipeline_yaml.jinja2:47` → `{{ exit.filename }}`. Key + type tokens
  unchanged (REQ-PY-06 untouched).
- **Phase 4 (regen).** 7 graph baselines + 3 YAML baselines regenerated; diffs match
  their enumerated classes (verified below).
- **Phase 5 (docs).** Docs 09/16/21, modeling-assumptions §3, verification-matrix
  rows + reconciled counts, release notes, spec §1 amendment. Docs commit touches no
  production code.

### Spec conformance

**SC-7 headline — names in generated YAML, both shapes.** Verified in committed
baselines:
- Shape A: `wi014_toy` graph carries `total_cost` (`part_def`, `demo_plant`); new
  `wi014_toy.yaml` renames the `…cost_calc__cost` exit filename to
  `demo_plant__total_cost.json`.
- Shape B: `attr_expr_probe` graph carries `scale_result`/`half_vol`/`quarter_vol`;
  YAML renames exactly those three exit filenames, keys unchanged, all other lines
  byte-identical.
- `solar_battery`: one shape-A `misc_hardware_cost` entry; YAML renames exactly the
  `…total_allocation` filename.

**output_aliases populated in the expected 5, EMPTY-not-absent in the rest.** Verified
directly: attr_expr_probe (3), solar_battery (1), wi014_toy (1), ife_plant (2),
catf_mfe (44); `sample_model` and `chain_spike` serialize `output_aliases: []`
(present, not absent — the D1 field-addition class).

**Instance-qualified filename + sibling collision.** `OutputAlias.output_filename` =
`{instance_path}__{alias_name}.json`. The collision unit test
(`test_exit_point_aliases.py:151`) is real: `sibling_channel_ambiguity` yields
`twin_plant.chamber_a__power.json` and `twin_plant.chamber_b__power.json` — distinct,
asserted in both `output_aliases` and the rendered YAML.

**C1 guard — has teeth.** `test_output_aliases.py:89`
(`test_shape_b_resolves_via_alias_lookup_not_scoped`) asserts, for every
attr_expr_probe expose_pure alias, `scoped_lookup(key) is None` **and**
`alias_lookup(key) is not None`. If the resolver regressed to `scoped_lookup`-only,
every shape-B channel drops to null and the assertion fails. Note the fixture-shape
correction (recorded in the plan, not a defect): `ife_plant`'s nested exposure turned
out to be **shape A** (`_scoped_alias`, scope `radial_build.tf_coil`), so the genuine
nested-shape-B C1 guard rides on `attr_expr_probe` + `catf_mfe`, not `ife_plant`. The
`ife_plant` test is a valid shape-A nested-scope guard in its own right
(`test_output_aliases.py:60`).

**Warning case-matrix (INV-6).**
- *Resolvable → silent, name emitted:* `test_wi014_toy.py:135` asserts `total_cost`
  surfaces and none of the three warning strings appear. **Live.**
- *EXPOSE_COMPUTED → rejected:* pre-existing live assertions
  (`test_graph_builder_computed_attrs.py:198`, `test_backtracker_computed_attrs.py:148`);
  Item 11 did not touch the EXPOSE_COMPUTED path. **Live.**
- *Unresolvable refs → warning stays:* the `:796` branch is byte-identical and still
  reached by shape B. Positive coverage is a gap (Observation 1) — no test asserts the
  warning *fires*; only the negative (resolvable-is-silent) assertions exist.

**ComputationGraph rev discipline.** Field-set tests flipped deliberately: GA-05 exact
set (`test_graph_assembly.py:369`, 4→5) and DM-03 (`test_data_models.py`, 4→5) both
name `output_aliases`; new DM-09 pins the four `OutputAlias` fields. Ordering invariant
tested (`test_output_aliases.py:124`). Channel-existence validated + include_all raise
tested (`:136`, `:195`). Doc 09 updated (field + `OutputAlias` entry + the
"present-because-not-excluded" contrast).

**include_all dangling assertion + tie-break.** `test_dangling_include_all_run_errors`
asserts the raise; `test_dangling_targeted_run_silent` asserts drop+DEBUG;
`test_two_names_one_channel_both_retained` asserts both entries survive with distinct
filenames.

**Recorded deviations — verified sound.**
1. *solar_battery recapture.* Snapshot diff is the `captured_at` timestamp
   (inherent to recapture) + `reference_chain` added to two computed attributes
   (`misc_hardware_cost` populated `["allocation_model","total_allocation"]`,
   `p_net_kw` null). No other bytes change. Matches "diff exactly reference_chain"
   and the additive-field recapture Item 10 used. The two repointed tests are sound:
   degrade test → `unresolvable_attr_probe` (6 CAs, none EXPOSE, no `reference_chain`
   — exercises the degrade path non-vacuously); empty-field test → `quoted_owner_formula`
   (2 FORMULA attrs, no EXPOSE → `output_aliases == []`, non-vacuous). Both repoints
   hold the original test's bar.
2. *capture_baseline_yaml.py → snapshot path.* Now renders from
   `build_full_graph_from_snapshot` (license-free); `wi014_toy` registered in `MODELS`.
   The byte-identical-for-unaffected claim is consistent with the observed YAML diffs
   (only alias renames). Not independently re-run (license/uv gated).
3. *Matrix counts 233/221/12.* Spot-checked by direct count: 233 REQ rows, 221 `| PASS |`,
   12 non-PASS. Arithmetic exact.

**Release-notes coordination + agentic-mbse.** The filename-move table enumerates all
five committed moves (attr_expr ×3, solar ×1, new wi014 ×1); the catf first-wins
collapse and the agentic-mbse Item-12 impact are recorded. Complete.

### Design conformance

Implementation follows the design. INV-1 (two sources only, never `_alias`), INV-2
(channel read from registry), INV-3 (existence + run-mode split), INV-4 (instance-
qualified filenames), INV-5 (stable sort) all present as designed. The `alias_lookup`
read for shape B is used only to resolve an already-source-selected `expose_pure`
alias's channel string, per the design's stated INV-1 non-violation — not to source
entries. D1–D5 all implemented as decided. No undocumented deviations.

### Code integrity

No slop or failure-honesty problems. `_build_output_aliases` is single-purpose with a
readable contract. The dangling filter does **not** silently swallow on full runs — it
raises with a precise message (the honest choice). `_build_exit_points`'s new
`alias_filenames` is a required parameter (no `=None` papering). The shape-A LITERAL
fallback is justified by B3 (verified: only consumer is `_build_computed_attr_module`,
no shape-A FORMULA-consumes-exposed-name fixture). The warning branches are gated on a
concrete registry-membership check, not a broad except.

**Observation 1 (non-blocking, test coverage).** The INV-6 "unresolvable refs still
warn" leg has no positive live assertion. The retained shape-B `:796` warning and the
**new** shape-A "no scoped alias registered" warning (`graph_builder.py:~1020`) are
only asserted *absent* for resolvable cases. The branches are structurally sound; this
is a coverage gap, not a defect. Pre-existing for `:796` (Item 1 never landed the
positive test — the deferral note in `test_wi014_toy.py:20-32` records why); newly
introduced for the shape-A warning. Worth a follow-up test.

**Observation 2 (non-blocking, documented/accepted).** Shape B instance-qualifies via
`owning_part_leaf` (leaf only), while shape A uses the full nested `_scoped_alias`
scope. Two distinct shape-B owning parts sharing a leaf name and exposing the same
`alias_name` to different channels would produce a duplicate `(instance_path,
alias_name)` sort key — a non-deterministic INV-5 tie and an INV-4 filename collision.
Not triggered in-repo (catf's 44 keys are all distinct; sibling leaves differ). The
design acknowledges this as uncovered/low-risk (Validation Approach, Dim-1). Inherited
from Item 10's shape-B qualification scheme. Backlog note candidate.

**Observation 3 (non-blocking, inherited semantics).** catf_mfe surfaces 44 shape-B
entries; 28 collapse onto 3 shared channels (`minor_calc__a` ×13, `volume_calc__volume`
×13, `pump_power` ×2) via Item 10's first-wins `_alias`. Item 11 faithfully emits all
44 with distinct instance_paths pointing at the shared (single-valued) channels — so a
programmatic consumer of `output_aliases` sees 13 "distinct" minor_radius entries that
all resolve to one value. This is Item 10's nested-collapse semantics (INV-2 requires
reading the channel the value flows on), documented in the release notes, and out of
Item 11's scope. INV-2/3/4 hold as defined against the registry.

---

## Certification

Certified PASS. Verified and marked:

- **SC-7 both shapes** surface in committed graph baselines and YAML (wi014 shape A,
  attr_expr_probe shape B, solar misc_hardware_cost) — direct baseline/YAML inspection.
- **Schema rev documented** (doc 09 + REQ-DM-09/PY-08/CA-11 in the verification matrix,
  counts reconciled 233/221/12).
- All HARD invariants (INV-1..5) implemented and live-tested on real snapshots; the
  C1 guard has teeth; field-set flips deliberate; include_all raise + tie-break +
  determinism + channel-existence all pinned.
- Both recorded deviations verified sound (solar recapture = timestamp + reference_chain
  only; capture-script refactor consistent with observed diffs); repointed tests hold
  their bar.
- Scope clean across both commits; no mocks.

**Open (non-blocking):** three observations above — one test-coverage gap (INV-6
positive warning assertions), two documented/inherited edge cases. Recommend the
shape-B leaf-collision case (Obs. 2) be filed as a backlog note and a positive
unresolvable-warning test (Obs. 1) added opportunistically. Neither gates close.

**Verification limits:** `uv run` (pytest/ruff/mypy) approval-gated this session; the
gate (1989/4/5, ruff 21, mypy 109) rests on the recorded value + static inspection,
per the Item 8–10 audit pattern.


---

## Orchestrator close-out (2026-07-06)

Verification limit covered: the orchestrator ran the full gate at the committed code state
before both Item 11 commits (1989 passed / 4 skipped / 5 xfailed; ruff 21; mypy 109). The
three non-blocking observations (INV-6 positive-warn assertion; shape-B leaf-collision
candidate; catf first-wins semantics) carry to Item 12's sweep / BACKLOG.

Verdict: **PASS**. Item 11 complete — all eleven sysml-codegen items landed.
