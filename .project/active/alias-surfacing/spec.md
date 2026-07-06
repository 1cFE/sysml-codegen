# Spec: Derived-Attribute Alias Surfacing (SC-7)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** MEDIUM
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 11

---

## Problem

A modeler writes `attribute total_cost : Real = cost_calc.cost` to give a calc
output a meaningful name. That name never reaches the generated output. The value
flows on the canonical channel (`...__cost_calc__cost`), but `total_cost` — the
name the modeler chose — appears nowhere in the pipeline YAML, the graph, or the
JSON outputs. A downstream consumer sees the raw channel name, not `total_cost`.

(What surfaces is the *sanitized* identifier per Item 5's naming contract — the
derived `python_name`, e.g. `total_cost` for `'total cost'`. Identifiers are
derived once at extraction and looked up downstream, REQ-NC-06. See the naming
requirement below; for `total_cost` the literal and sanitized forms coincide.)

EXPOSE is officially supported (modeling-assumptions §3 promises consumers bind to
`subsystem.exposed_name`), so the missing name is a gap in promised functionality,
not a missing feature request. Two prior items set this up but stopped short:

- **Item 1** added interim warnings for the drop. There are three distinct
  EXPOSE_PURE warning branches, and the one that fires depends on the shape — the
  spec review corrected an earlier mis-anchoring here (L1-1):
  - `graph_builder.py:809` — name-drop: refs resolved, but the canonical channel is
    absent from the registry. Fires for a resolved-but-unregistered shape-B case.
  - `graph_builder.py:796` — **malformed-refs**: `_resolve_expose_pure` could not
    separate the instance ref from the output ref. **This is the branch that fires
    for shape A** — on a part def the calc-usage instance names are absent from
    `calc_usage_names`, so it returns before reaching `:809`. Pinned as the current
    baseline by `tests/conformance/test_wi014_toy.py:28-32`.
  - `output_registry_builder.py:273` — Phase-3 shape-B alias-drop when the channel
    is unregistered at registry-build time.
- **Item 10** made both shapes *resolve* internally, but through a **different code
  path** than the graph-builder warning above. Shape A resolves per instance via the
  structured `_scoped_alias` namespace (populated only for part-def EXPOSE_PURE,
  keyed by `(instance_path, python_name)`); shape B's name→channel mapping lives on
  the `expose_pure` `ChannelAlias` objects. Item 10 did **not** reroute
  `_build_attribute_resolution_map`, which still calls the old `_resolve_expose_pure`
  and still logs the malformed-refs warning for shape A. So today the value resolves
  for cross-part consumers, but the graph builder still warns and no name is emitted.

This item is the last step: take the mapping Item 10 already computed and **surface
the name** into the generated graph and YAML, and route the graph builder's shape-A
EXPOSE_PURE handling through those same `_scoped_alias` registrations so it stops
warning. That reroute **connects landed machinery to its consumer** — it adds no new
resolution logic (the Non-Goal covers genuinely new resolution). It also completes
Item 1's interim measure and lands the warning-test handoff that
`test_wi014_toy.py:34-40` explicitly deferred to "Items 10/11": once the name
surfaces, the "name is dropped" / malformed-refs warnings are wrong for the
resolvable case and retire.

## Success Criteria

- [ ] A graph-level alias field (`output_aliases` or equivalent) exists on
  `ComputationGraph`, populated from the EXPOSE_PURE typed alias registrations for
  **both** shapes, each entry carrying the modeler's name, the canonical channel it
  aliases, and enough instance qualification to be unique.
- [ ] `total_cost`-style names appear in generated **pipeline YAML** as named
  exit-point captures wired to the correct canonical channel, demonstrated
  end-to-end for both shapes: shape A via `wi014_toy` (`total_cost` on a part def),
  shape B via `attr_expr_probe` (`scale_result`, `half_vol`, `quarter_vol` on a part
  usage).
- [ ] Two instances that expose the same name produce distinct output-capture keys
  — no duplicate YAML keys, no collision — **demonstrated by committed coverage**
  (the Item-10 `sibling_channel_ambiguity` fixture already carries this shape:
  `attribute power = power_calc.power` on `part def Chamber`, instantiated as
  `chamber_a` and `chamber_b`; both expose `power`).
- [ ] The ComputationGraph schema rev is documented per R1: doc 09 field list
  updated, REQ-* tags allocated, verification-matrix rows added, and a conformance
  field-set test asserting the new field's presence and shape.
- [ ] `output_aliases` serializes in a **deterministic order** (sorted by a stable
  key), so regen never produces an ordering-only baseline diff — the exact failure
  class Item 1 was created to kill.
- [ ] Every `output_aliases` entry's canonical channel is **validated to exist** as a
  declared output channel in the graph (precedent: `_validate_channel_references`,
  `graph_builder.py:627`), so a dropped module can't leave a dangling alias.
- [ ] The warning **case-matrix** holds after this item:
  - *resolvable and surfaced* (both shapes, incl. shape A via `_scoped_alias`) →
    **silent**, the name is emitted;
  - *unresolvable refs* (`_resolve_expose_pure` cannot identify instance/output) →
    the malformed-refs warning at `:796` **stays**;
  - *EXPOSE_COMPUTED* → **rejected** per modeling-assumptions §3, its warning stays.
- [ ] `test_wi014_toy.py`'s recorded-deferral assertion (`:28-40`) flips from pinning
  the malformed-refs warning to asserting shape-A resolution **and** the surfaced
  `total_cost` alias — closing the deferral it hands to "Items 10/11."
- [ ] All 7 committed `computation_graph.json` baselines regenerated (field-addition
  review class — see Baseline Regeneration); `attr_expr_probe`'s YAML baseline gains
  the alias captures; a new `wi014_toy` YAML baseline is committed. No extraction
  snapshot changes (they carry no graph).
- [ ] agentic-mbse impact recorded: the EXPOSE-pattern docs describe what the
  exposed name now does downstream (it surfaces as a named output capture).

## Known Requirements

- **[HARD]** `output_aliases` is populated **only** from the two EXPOSE_PURE-specific
  sources that retain their provenance: the `expose_pure` `ChannelAlias` objects
  (shape B — they carry `.source == "expose_pure"`) and the `_scoped_alias` registry
  (shape A — populated exclusively for part-def EXPOSE_PURE). **Not** the flat
  `_alias` dict: it merges CHAIN aliases, design overrides, and expose_pure into bare
  `key → channel` pairs with the `source` discriminator erased, so it cannot be
  filtered to EXPOSE_PURE. CHAIN redefinition, design_override, and transitive
  design-attribute aliases are not surfaced. (Q1 / L2-1 — SC-7 is "Derived-Attribute
  Alias Surfacing.")
- **[HARD]** What surfaces is the derived **`python_name`** (the sanitized
  identifier), not the raw SysML name. `ChannelAlias.alias_name` and the
  `_scoped_alias` key's leaf are both `python_name = _sanitize_name(attr_name)`. This
  is Item 5's contract (identifiers derived once at extraction, REQ-NC-06). Reconcile
  with modeling-assumptions §3: the consumer binds to `subsystem.exposed_name` in its
  *sanitized* form. (L1-2)
- **[HARD]** Each surfaced alias wires to the **same** canonical channel the value
  already flows on. The Item-10 registry mapping is the source of truth — this item
  reads it, it does not re-derive or re-resolve. ("Compute once, look up
  thereafter," modeling-assumptions §7.)
- **[HARD]** Alias emission must be instance-qualified so that the same exposed name
  on two instances (sibling parts of one def) yields unique output-capture keys.
  Un-qualified, they collide into invalid YAML. (The *scheme* is design; the
  *uniqueness guarantee* is the requirement.)
- **[HARD]** `output_aliases` serializes in a deterministic, stable-sorted order, and
  every entry's canonical channel is validated to exist as a declared graph output
  channel (precedent `_validate_channel_references`). Both are non-negotiable: the
  first prevents the ordering-only baseline churn Item 1 was born to fix; the second
  matches R1's typed-registry-plus-validation discipline. (L3-1)
- **[HARD]** The `ComputationGraph` schema change is a deliberate, reviewed rev (R1):
  it lands with REQ tags, a doc 09 update, verification-matrix rows, and a
  conformance field-set test. Generation still consumes only `ComputationGraph`
  (REQ-PIPE-07 / REQ-ORCH-06 boundary preserved) — no new input to the generator.
- **[NEED]** Item 1's interim EXPOSE_PURE warnings are retired for every case the
  alias now surfaces — including the shape-A **malformed-refs** branch (`:796`), not
  only the name-drop branch (`:809`). The residual warning fires only on genuinely
  unresolvable refs and names those real cases, not "Item 10/11." This is SC-7's full
  closure of Item 1's interim measure: a resolvable EXPOSE no longer warns and
  instead emits its name. (See the warning case-matrix in Success Criteria.)
- **[NEED]** Both shapes are demonstrated in generated YAML, not just at the graph
  level — shape A gets a committed `wi014_toy` pipeline-YAML baseline; shape B is the
  reviewed `attr_expr_probe` YAML diff.
- **[INFERRED]** Baseline regeneration goes through the capture scripts only (R3),
  with reviewed diffs. Graph-baseline regen is license-free (snapshot-driven, via
  `scripts/capture_pipeline_baselines.py`). `wi014_toy` must be registered in
  `scripts/capture_baseline_yaml.py`'s `MODELS` set (currently absent).

## Non-Goals

- **Redefinition (`:>>`) and design_override name surfacing.** These already resolve
  as channels (Item 10); surfacing their *names* as output captures is a different
  feature. Recorded as a **BACKLOG follow-up candidate**, not done here. (Q1)
- **EXPOSE_COMPUTED surfacing** (calc output + arithmetic) — stays rejected per
  modeling-assumptions §3. Its warning stays.
- **Genuinely new resolution logic.** Item 10 owns the name→channel resolution for
  both shapes. This item adds no new lookup algorithm, rewrite, or classification.
  Rerouting `_build_attribute_resolution_map`'s shape-A EXPOSE_PURE branch to read
  Item 10's existing `_scoped_alias` registrations (so it stops hitting the
  malformed-refs warning) is explicitly **in scope** — that is connecting landed
  machinery to its consumer, not new resolution. (L1-3)
- **Extraction snapshot format change.** Verified: extraction snapshots carry no
  ComputationGraph (their keys are calc_usages / calc_defs / computed_attributes /
  aggregation_expressions / etc.). The schema rev touches generation baselines only.

## Open Questions / Deferred to design

- **Shape of an `output_aliases` entry and the instance-qualification scheme.** What
  fields (alias name, canonical channel, instance path, python type?), and how the
  qualification guarantees uniqueness across sibling/multiple instances. (The
  stable-sort key and the channel-existence validation are pinned as HARD above; the
  entry's field layout is the design's to choose.)
- **How the same-name collision case earns committed coverage.** The
  `sibling_channel_ambiguity` fixture carries the shape (two `Chamber` siblings each
  exposing `power`), but has no committed `computation_graph.json` or YAML baseline
  today. Design decides the artifact: a unit test asserting the two distinct
  `output_aliases` keys, or a new graph/YAML baseline for the fixture. The spec
  requires the case *covered*; it does not mandate which. (L3-2)
- **Empty-field serialization / baseline-churn control.** Does `output_aliases`
  serialize when empty (adds `output_aliases: []` to all 7 graph baselines) or is it
  excluded-when-empty (churn limited to the 4 alias-bearing fixtures: `wi014_toy`,
  `attr_expr_probe`, `ife_plant`, `catf_mfe`)? R1's conformance field-set test leans
  toward the field always being present and inspectable; weigh against baseline
  noise. (Contrast: `fallback_entry_points` uses `exclude=True`.)
- **YAML exit-point capture syntax.** The current exit-point template reuses the
  channel name for both the capture key and the output filename
  (`{{ exit.name }}: {{ exit.type }} {{ exit.name }}.json`,
  `pipeline_yaml.jinja2:47`). An alias capture needs the *alias* as the display/key
  and the *canonical channel* as the wired source — the render must separate the two.
- **Which docs beyond 09 host the behavior.** Candidates: doc 09 (the field), doc 21
  (pipeline-YAML exit-point render), doc 16 (the EXPOSE_PURE → surfaced-name story).
- **Whether `wi014_toy`'s YAML baseline can be captured license-free** (snapshot-
  driven) or needs live extraction — an R3 / plan-time detail.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 11; R1/R2/R3)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` (SC-7 section,
    lines 190–201 — both shapes, the `output_aliases` recommendation, the
    instance-qualification risk)
  - `.project/active/cross-part-wiring/design.md` + `release-notes.md` (Item 10 — the
    `_scoped_alias` namespace, part-def EXPOSE expansion, the typed alias
    registrations this item reads)
  - `docs/architecture/reference/09-data-models.md` (the ComputationGraph field
    reference this rev updates; REQ-DM-01..08)
  - `docs/architecture/reference/21-pipeline-yaml-generation.md` (exit-point render)
  - `docs/architecture/reference/16-computed-attributes.md` (EXPOSE_PURE story)
  - `docs/architecture/modeling-assumptions.md` §3 (EXPOSE contract), §7 (compute
    once)
- **Code touch-points (for design):**
  - `src/sysml_codegen/resolution/models.py` (`ComputationGraph`)
  - `src/sysml_codegen/core/output_registry.py` (`_scoped_alias` for shape A;
    `ChannelAlias` objects with `.source == "expose_pure"` for shape B — **not** the
    flat `_alias`, which is source-erased)
  - `src/sysml_codegen/resolution/graph_builder.py` `_build_attribute_resolution_map`
    (`:865` — routes shape-A EXPOSE_PURE through `_resolve_expose_pure`; reroute
    through `_scoped_alias`) and `_validate_channel_references` (`:627` — validation
    precedent)
  - `src/sysml_codegen/generation/pipeline.py` `_build_exit_points` +
    `templates/pipeline_yaml.jinja2` (exit-point render)
  - Warning sites to retire for resolvable cases: `graph_builder.py:796`
    (malformed-refs — shape A), `graph_builder.py:809` (name-drop),
    `output_registry_builder.py:273` (Phase-3 shape-B alias-drop)
  - `tests/conformance/test_wi014_toy.py:28-40` (the deferred name-drop-warning
    assertion this item closes)
  - `tests/fixtures/wi014_toy/` (shape A), `tests/fixtures/attr_expr_probe/`
    (shape B), `tests/fixtures/sibling_channel_ambiguity/` (same-name collision),
    `tests/fixtures/baseline_outputs/*/computation_graph.json` (7),
    `tests/fixtures/baseline_yaml/` (YAML baselines)
  - `scripts/capture_pipeline_baselines.py`, `scripts/capture_baseline_yaml.py`
- **Auto-memory:** `multihop-expose-offline-parity`, `plant-idiom-fixtures`
- **Design:** `.project/active/alias-surfacing/design.md` (to be created)

## Baseline Regeneration (spec'd up front per R1 cross-cutting)

The new graph field churns every committed generation baseline. Spec the review
classes now so the diffs are attributable, not surprising:

1. **Graph baselines gaining the field (7 total).** `computation_graph.json` for
   `solar_battery`, `sample_model`, `chain_spike`, `attr_expr_probe`, `ife_plant`,
   `catf_mfe`, `wi014_toy`. Review class: **field-addition only.** Only two have no
   EXPOSE_PURE derived attribute (`sample_model`, `chain_spike`) and gain an empty
   `output_aliases`; everything else in those files is byte-identical. The other five
   gain populated entries. Regen: `capture_pipeline_baselines.py` (license-free,
   snapshot-driven).
   **Amendment (implement-time correction):** this section originally listed
   `solar_battery` as having no EXPOSE_PURE attribute. That is wrong — `solar_battery`
   carries a shape-A EXPOSE `misc_hardware_cost = allocation_model.total_allocation` on
   `solar_array`, so it gains one populated `output_aliases` entry (`part_def`,
   instance_path `solar_battery_plant.solar_array`) and its YAML gains the matching
   filename rename. Its stale pre-Item-10 snapshot was recaptured so the snapshot path
   surfaces the alias (the approved SC-1 reconciliation).
2. **YAML baseline diff — `attr_expr_probe` (shape B).** Gains named exit-point
   captures for `scale_result` / `half_vol` / `quarter_vol`. Reviewed diff.
3. **New YAML baseline — `wi014_toy` (shape A).** Adds `total_cost` as a named
   exit-point capture. Requires registering `wi014_toy` in
   `capture_baseline_yaml.py`'s `MODELS`. New committed artifact.
4. **No extraction-snapshot change.** Verified: snapshots carry no graph.

---

**Next Steps:** After approval, proceed to `/_my_design`.
