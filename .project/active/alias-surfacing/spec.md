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

EXPOSE is officially supported (modeling-assumptions §3 promises consumers bind to
`subsystem.exposed_name`), so the missing name is a gap in promised functionality,
not a missing feature request. Two prior items set this up but stopped short:

- **Item 1** added an interim warning at both drop sites
  (`output_registry_builder.py:273`, `graph_builder.py:809`) that plainly states
  the derived-attribute name is dropped and names the channel where the value went.
  It even points forward: "part-def shape-A resolution is Item 10/11."
- **Item 10** made both shapes *resolve* internally. The registry now holds the
  name→channel mapping for both — shape A (part def) in the structured
  `_scoped_alias` namespace, shape B (part usage) in the flat `_alias` /
  `expose_pure` `ChannelAlias` entries. But that mapping lives only in-memory to
  resolve *other* references. Nothing emits the name.

This item is the last step: take the mapping Item 10 already computed and **surface
the name** into the generated graph and YAML. The machinery exists; this item
renders it. It also completes Item 1's interim measure — once the name surfaces,
the "name is dropped" warning is wrong for the resolvable case and must retire.

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
  — no duplicate YAML keys, no collision.
- [ ] The ComputationGraph schema rev is documented per R1: doc 09 field list
  updated, REQ-* tags allocated, verification-matrix rows added, and a conformance
  field-set test asserting the new field's presence and shape.
- [ ] Item 1's "name is dropped" warning **disappears** for any alias that now
  resolves and surfaces; it remains only for genuinely-unsurfaced cases (canonical
  channel truly absent; EXPOSE_COMPUTED, which stays rejected). The residual
  warning's wording names the actual residual cases, not "Item 10/11."
- [ ] All 7 committed `computation_graph.json` baselines regenerated (field-addition
  review class — see Baseline Regeneration); `attr_expr_probe`'s YAML baseline gains
  the alias captures; a new `wi014_toy` YAML baseline is committed. No extraction
  snapshot changes (they carry no graph).
- [ ] agentic-mbse impact recorded: the EXPOSE-pattern docs describe what the
  exposed name now does downstream (it surfaces as a named output capture).

## Known Requirements

- **[HARD]** `output_aliases` is populated **only** from EXPOSE_PURE-sourced alias
  registrations — the `expose_pure` `ChannelAlias` entries (shape B) and the
  part-def `_scoped_alias` entries (shape A). CHAIN redefinition aliases,
  design_override aliases, and transitive design-attribute aliases are **not**
  surfaced. (Q1 — SC-7 is "Derived-Attribute Alias Surfacing.")
- **[HARD]** Each surfaced alias wires to the **same** canonical channel the value
  already flows on. The registry mapping from Item 10 is the source of truth — this
  item reads it, it does not re-derive or re-resolve. ("Compute once, look up
  thereafter," modeling-assumptions §7.)
- **[HARD]** Alias emission must be instance-qualified so that the same exposed name
  on two instances (two `demo_plant`s, or sibling parts of one def) yields unique
  output-capture keys. Un-qualified, they collide into invalid YAML. (The *scheme*
  is design; the *uniqueness guarantee* is the requirement.)
- **[HARD]** The `ComputationGraph` schema change is a deliberate, reviewed rev (R1):
  it lands with REQ tags, a doc 09 update, verification-matrix rows, and a
  conformance field-set test. Generation still consumes only `ComputationGraph`
  (REQ-PIPE-07 / REQ-ORCH-06 boundary preserved) — no new input to the generator.
- **[NEED]** Item 1's interim "name is dropped" warning is retired for every case
  the alias now surfaces, and the residual warning points at the real residual
  cases. This is SC-7's full closure of Item 1's interim measure — the outcome is
  that a resolvable EXPOSE no longer warns and instead emits its name.
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
- **New resolution machinery.** Item 10 owns the name→channel resolution for both
  shapes. This item reads the existing registrations; it adds no lookup, no rewrite,
  no classification.
- **Extraction snapshot format change.** Verified: extraction snapshots carry no
  ComputationGraph (their keys are calc_usages / calc_defs / computed_attributes /
  aggregation_expressions / etc.). The schema rev touches generation baselines only.

## Open Questions / Deferred to design

- **Shape of an `output_aliases` entry and the instance-qualification scheme.** What
  fields (alias name, canonical channel, instance path, python type?), and how the
  qualification guarantees uniqueness across sibling/multiple instances.
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
  - `src/sysml_codegen/core/output_registry.py` (`_scoped_alias`, `_alias`,
    `ChannelAlias` source discrimination)
  - `src/sysml_codegen/generation/pipeline.py` `_build_exit_points` +
    `templates/pipeline_yaml.jinja2` (exit-point render)
  - `src/sysml_codegen/orchestration/output_registry_builder.py:273`,
    `src/sysml_codegen/resolution/graph_builder.py:809` (Item 1 warnings to retire)
  - `tests/fixtures/wi014_toy/` (shape A), `tests/fixtures/attr_expr_probe/`
    (shape B), `tests/fixtures/baseline_outputs/*/computation_graph.json` (7),
    `tests/fixtures/baseline_yaml/` (YAML baselines)
  - `scripts/capture_pipeline_baselines.py`, `scripts/capture_baseline_yaml.py`
- **Auto-memory:** `multihop-expose-offline-parity`, `plant-idiom-fixtures`
- **Design:** `.project/active/alias-surfacing/design.md` (to be created)

## Baseline Regeneration (spec'd up front per R1 cross-cutting)

The new graph field churns every committed generation baseline. Spec the review
classes now so the diffs are attributable, not surprising:

1. **Graph baselines gaining the field (7 total).** `computation_graph.json` for
   `solar_battery`, `sample_model`, `chain_spike`, `attr_expr_probe`, `ife_plant`,
   `catf_mfe`, `wi014_toy`. Review class: **field-addition only.** The three with no
   EXPOSE_PURE derived attribute (`solar_battery`, `sample_model`, `chain_spike`)
   gain an empty `output_aliases` (or no line, if excluded-when-empty — Open
   Question); everything else in those files is byte-identical. The four with
   EXPOSE_PURE aliases gain populated entries. Regen: `capture_pipeline_baselines.py`
   (license-free, snapshot-driven).
2. **YAML baseline diff — `attr_expr_probe` (shape B).** Gains named exit-point
   captures for `scale_result` / `half_vol` / `quarter_vol`. Reviewed diff.
3. **New YAML baseline — `wi014_toy` (shape A).** Adds `total_cost` as a named
   exit-point capture. Requires registering `wi014_toy` in
   `capture_baseline_yaml.py`'s `MODELS`. New committed artifact.
4. **No extraction-snapshot change.** Verified: snapshots carry no graph.

---

**Next Steps:** After approval, proceed to `/_my_design`.
