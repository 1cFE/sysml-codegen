# Design: Derived-Attribute Alias Surfacing (SC-7)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** upstream-findings-epic
**HEAD at design:** `21b61be`
**Epic Item:** UPSTREAM-FINDINGS Item 11 (the epic's last code item)

---

## Overview

Take the name→channel mapping Item 10 already computed and surface the modeler's
exposed name into the generated graph (a new `output_aliases` field) and pipeline
YAML (named exit-point captures), for both EXPOSE_PURE shapes. Route the graph
builder's shape-A handling through the same landed `_scoped_alias` registrations so
it stops warning.

## Related Artifacts

- **Spec (contract):** `.project/active/alias-surfacing/spec.md`
- **Spec review + resolutions:** `.project/active/alias-surfacing/spec-review.md`
- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 11; R1/R2/R3)
- **Required Reading:** `.project/research/20260705_upstream-findings-deep-research.md`
  (SC-7); `.project/active/cross-part-wiring/design.md` (Item 10 machinery);
  `docs/architecture/reference/09-data-models.md`, `.../21-pipeline-yaml-generation.md`,
  `.../16-computed-attributes.md`; `docs/architecture/modeling-assumptions.md` §3/§7.
- **Auto-memory:** `multihop-expose-offline-parity`, `plant-idiom-fixtures`.

## Research Findings

The two EXPOSE_PURE sources are already computed by Item 10 and carry provenance
(the [HARD] source constraint, spec L2-1):

- **Shape A (part def)** — `output_registry._scoped_alias`, a dict keyed
  `(instance_path, python_name) → canonical_channel`. Written exclusively by
  `_register_partdef_expose_scoped_aliases` (`pipeline_builder.py:463-513`), guarded
  on `EXPOSE_PURE and is_on_part_definition`. Confirmed: it is the *only* writer to
  `register_scoped_alias` (`output_registry.py:134`), so `_scoped_alias` == shape-A
  EXPOSE_PURE exactly. `wi014_toy` registers `("demo_plant","total_cost") → …cost_calc__cost`.
- **Shape B (part usage)** — the `expose_pure` `ChannelAlias` objects
  (`core/models.py:71`): `alias_name = python_name` (bare), `canonical_name =
  "{instance}.{output}"` (a bare Key_A key resolvable via `registry.alias_lookup`, with
  `scoped_lookup` as fallback — see C1), `owning_part_qn`, `source == "expose_pure"`. Built at
  `computed_attribute_extractor.py:317`, merged into `all_channel_aliases`
  (`pipeline_builder.py:707`).

Neither is the flat `_alias` dict — it merges CHAIN + design_override + expose_pure
into source-erased `key→channel` pairs (`output_registry_builder.py:241/269`), so it
can't be filtered to EXPOSE_PURE. Confirmed against the spec's [HARD] constraint.

Key integration facts:

- `build_computation_graph` (`graph_builder.py:150`) already receives
  `output_registry` (so `_scoped_alias` is in hand) but **not** the ChannelAlias
  list — shape B must be threaded in.
- `_build_attribute_resolution_map` (`:820`) routes *all* EXPOSE_PURE CAs through
  `_resolve_expose_pure` (`:773`) with no part-def guard. For a part def the
  calc-usage instance names are absent from `calc_usage_names`, so it can't split the
  refs and hits the malformed-refs warning at `:796` — the branch that actually fires
  for shape A (spec L1-1, pinned by `test_wi014_toy.py:28-32`). The `:809` name-drop
  branch is downstream and never reached for shape A.
- The resolution map is consumed **only** by `_build_computed_attr_module` (`:890`),
  and only to wire a FORMULA CA's inputs (`:951-959`). No in-repo shape-A fixture has
  a FORMULA CA that consumes an exposed name, so today the shape-A resolution entry is
  never read for wiring — its sole observable effect is the warning.
- Exit points render at `pipeline.py:202` (`_build_exit_points`) + template
  `templates/pipeline_yaml.jinja2:41-49`. Grammar per line: `{key}: {type} {third}`.
  For raw exits, `key` = the channel and `third` = `{channel}.json`. The REQ-PY-06
  conformance test (`test_gen_pipeline_yaml.py:377`) asserts every exit **key** is a
  declared module-output channel and checks the type; it ignores the `.json` token.
- `_validate_channel_references` (`:627`) is the validation precedent: collect
  declared output channels, then check references against them.
- Baseline capture: 7 graph fixtures (`capture_pipeline_baselines.py:51`, all
  snapshot-driven / license-free, incl. `wi014_toy`); YAML capture
  (`capture_baseline_yaml.py:23`) lists only `attr_expr_probe` — `wi014_toy` must be
  added.

## Core Concept

The value already arrives on its canonical channel; Item 10 already computed the
mapping from the modeler's name to that channel and stored it, with provenance, in
two typed registries. This item does not resolve anything new — it **reads those two
provenance-carrying sources (the `_scoped_alias` registry and the `expose_pure`
ChannelAlias list) at the end of graph construction, normalizes their entries into one
instance-qualified list (`output_aliases`) on the `ComputationGraph`, and renders
each entry as the destination filename on its canonical channel's exit line in the
YAML.** The instance path (already the
scope half of every `_scoped_alias` key, and the owning scope of every shape-B
ChannelAlias) is what makes two siblings exposing the same name land on distinct
output filenames. Separately, the graph builder's shape-A branch stops calling the naive
refs-parser that can't handle a part def, and instead lets `_scoped_alias` decide
whether the EXPOSE is resolvable (silent) or genuinely broken (warn) — connecting
the landed machinery to the one consumer Item 10 left wired to the old path.

The design is one derived list plus two small edits (a warning reroute, an exit-point
render). It invents no lookup, rewrite, or classification — the Non-Goal boundary.

## Key Bets

- **B1.** `_scoped_alias` contains exactly the shape-A EXPOSE_PURE aliases and nothing
  else. *If false → `output_aliases` surfaces non-EXPOSE_PURE names, violating the
  [HARD] "EXPOSE_PURE only" scope.* (Verified: single writer, part-def+EXPOSE guarded.)
- **B2.** Every `expose_pure` ChannelAlias's `canonical_name` (bare `instance.attr`)
  resolves through the persisted **Key_A alias registration** — `registry.alias_lookup`,
  which reads the `_alias` entry Phase 1 wrote at `output_registry_builder.py:172` — with
  `scoped_lookup` only as a fallback. This is the *value* Phase 3's primary resolver
  (`instance_attr_to_channel`, a build-local map) computes; `alias_lookup` is its
  persisted twin, reachable at graph-build time. *If false → shape-B aliases can't name a
  channel and are silently dropped, so `scale_result` never surfaces.* (Corrected after
  design review C1: the earlier `scoped_lookup`-only claim was wrong — `scoped_lookup`
  keeps the full nested path and matches only a top-level usage, so a nested part-usage
  EXPOSE like the plant idiom would miss.)
- **B3.** Nothing in-repo reads the shape-A EXPOSE_PURE entry of the per-def
  resolution map for wiring. *If false → changing that branch to a literal fallback
  mis-wires a FORMULA input.* (Verified: only consumer is `_build_computed_attr_module`
  and no shape-A FORMULA-consumes-exposed-name fixture exists.)

## Key Decisions

- **D1. `output_aliases` is a real, always-serialized field (not `exclude=True`).**
  *Rejected: exclude-when-empty (the `fallback_entry_points` precedent).* That
  precedent is `exclude=True` because it is a derived in-memory analysis artifact
  consumed at the generation boundary — it carries no output. `output_aliases` is a
  genuine schema field describing real generated output, and R1's field-set
  conformance test wants it present and inspectable on every graph. Cost: the 3
  non-EXPOSE baselines gain `output_aliases: []`. Accepted — the spec pre-accounted
  this as the field-addition review class.

- **D2. Entry shape = `{alias_name, canonical_channel, instance_path, shape}`;
  destination filename = `{instance_path}__{alias_name}.json`.** *Rejected: dropping the
  `shape` tag for minimalism.* The two shapes surface from two different sources;
  carrying the provenance tag makes each baseline entry self-documenting (which source
  produced it) for the one item whose entire point is these entries, at the cost of one
  short enum field. The `instance_path` is load-bearing: it instance-qualifies the
  filename so two siblings exposing the same name produce distinct filenames
  (`chamber_a__power.json`, `chamber_b__power.json`), keeping simkit's per-exit-module
  duplicate-filename check green (INV-4).

- **D3. Alias YAML capture = the modeler's name lands as the destination FILENAME on
  the canonical channel's existing exit line: `{canonical_channel}: {Type}
  {instance_qualified_alias}.json`.** *Rejected: a new line keyed by the alias with the
  canonical channel in the value slot.* Verified against the real TEAx consumer
  (`simkit`, `pipeline_schema.py` `_parse_exit_outputs`, read 2026-07-06): each exit
  output becomes `PipelineChannelBinding(channel_name=<key>, destination_filename=<the
  single value token>)`, the **key must be an existing channel** (simkit raises
  "ExitPoint module references unknown channel '<channel_name>'"), and the value is
  strictly `<Type> <filename>` — no directories, with a duplicate-filename check across
  the exit module. So the rejected new-line form fails twice: the alias key is not a
  channel (validation error), and a channel in the filename slot is a bogus filename.
  The filename-rename form is the one the grammar accepts. **Surfacing semantics:** an
  aliased channel keeps its single exit line; the modeler's name *replaces* the
  channel-derived default filename on that line (the name lands on the output artifact,
  and in `output_aliases` on the graph for programmatic consumers). Unaliased channels
  keep today's `{channel}.json`. Bonus: the exit key stays a channel, so REQ-PY-06 and
  the existing conformance tests need **no** change, and simkit's key validation is a
  real consumer-side backstop for INV-3.

- **D4. Dangling aliases are filtered, but the filter is only silent on targeted runs.**
  *Rejected: an unconditional raise, and an unconditional silent filter.* `_scoped_alias`
  and the ChannelAlias list are built before backtracking prunes modules, so a targeted
  (non-`include_all`) run can *legitimately* drop a channel an EXPOSE still references —
  an unconditional raise would crash valid targeted generation. But on an `include_all` /
  full run (every baseline), nothing legitimate prunes, so a dropped alias is a real
  wiring regression, and an unconditional silent filter would swallow it (design-review
  M3). Split by run mode: **targeted run** → drop + debug-log; **`include_all` run** →
  dropping any alias is an error (raise, or at minimum a WARNING the reviewed baseline
  diff surfaces). The [HARD] guarantee (no emitted entry dangles) holds both ways; the
  silent path fires only on the case it was written for. `build_computation_graph`
  already knows the run mode via the backtracking result / `include_all` flag threaded
  from `pipeline_builder`.

- **D5. Collision coverage = a unit test on `sibling_channel_ambiguity`, not a new
  baseline.** *Rejected: committing a graph/YAML baseline for the fixture.* The fixture
  has no committed baseline today; adding one is more churn than the guarantee needs.
  A unit test asserting the two siblings produce two distinct `output_aliases` capture
  keys (`chamber_a__power`, `chamber_b__power`) pins the uniqueness guarantee directly.

## Architecture

Two independent seams, both inside the existing `build_computation_graph`
call, plus one render edit downstream. No new module, no new input to the generator
(REQ-PIPE-07 / REQ-ORCH-06 boundary preserved).

```
pipeline_builder.build_pipeline_context
  └─ build_computation_graph(..., channel_aliases=expose_pure_subset)   # NEW param
       ├─ _build_attribute_resolution_map(...)      # EDIT: shape-A reroute (warning)
       ├─ ... existing module build ...
       ├─ _validate_channel_references(modules)      # existing; returns None, raises on bad ref
       └─ _build_output_aliases(scoped_alias, expose_pure_aliases,      # NEW step 8.5
                                registry, modules)  # recomputes its own declared-channel set
            → ComputationGraph(..., output_aliases=[...])                # NEW field

generation.pipeline.generate_pipeline_yaml(graph)
  └─ _build_exit_points(graph.modules, alias_filenames)                 # EDIT: pass
       → per-channel filename = alias filename when aliased, else default # override
```

Data flow for one alias (shape A, `total_cost`): `_scoped_alias[("demo_plant",
"total_cost")] = "…demo_plant__cost_calc__cost"` → `OutputAlias(alias_name=
"total_cost", canonical_channel="…cost_calc__cost", instance_path="demo_plant",
shape="part_def")` → filename `demo_plant__total_cost.json` overrides the default on
that channel's exit line → YAML line
`…demo_plant__cost_calc__cost: RootModel[float] demo_plant__total_cost.json`
(key stays the channel; only the filename changes).

## Required Invariants

- **INV-1 (scope).** Every `output_aliases` entry originates from `_scoped_alias`
  (shape A) or an `expose_pure` ChannelAlias (shape B). Never `_alias`. [HARD]
- **INV-2 (channel identity).** Each entry's `canonical_channel` is the *same* channel
  the value already flows on — read from the registry, never re-derived. [HARD, §7]
- **INV-3 (existence).** Every emitted entry's `canonical_channel` is a declared graph
  output channel. No dangling alias survives — on `include_all` runs a would-be drop is
  an error, not a silent filter (D4). Consumer-side backstop: simkit re-validates every
  exit key against known channels (`_parse_exit_outputs`). [HARD]
- **INV-4 (uniqueness).** Two instances exposing the same `alias_name` produce distinct
  output filenames — `{instance_path}__{alias_name}.json` — so simkit's per-exit-module
  duplicate-filename check stays green. [HARD]
- **INV-5 (determinism).** `output_aliases` is stable-sorted by `(instance_path,
  alias_name)`. *Uniqueness assumption (M6):* this key is unique because one name cannot
  be both part-def- and part-usage-exposed on a single instance, so shape A and shape B
  never emit the same `(instance_path, alias_name)`; source iteration order (dict-insertion
  + list order, both deterministic) then never affects the result. So regen
  never yields an ordering-only diff (the failure class Item 1 was created to kill).
  [HARD]
- **INV-6 (warning matrix).** Resolvable EXPOSE (both shapes, incl. shape A via
  `_scoped_alias`) → silent + name surfaced; unresolvable refs → `:796` stays;
  EXPOSE_COMPUTED → rejected per §3, its warning stays. [NEED]

## Component Overview

- **`OutputAlias` model** (`resolution/models.py`, new BaseModel). Fields per D2. The
  serialized entry; `ComputationGraph.output_aliases: list[OutputAlias]` (default
  empty, no `exclude`).

- **`_build_output_aliases`** (`resolution/graph_builder.py`, new; Step 8.5). Reads
  the two sources, normalizes to `OutputAlias`, filters to the declared-channel set
  (INV-3, D4), stable-sorts by `(instance_path, alias_name)` (INV-5). Shape A: iterate a
  new read accessor over `_scoped_alias` items → `instance_path` is the key's scope half.
  Shape B: iterate the threaded `expose_pure` ChannelAliases; resolve `canonical_name`
  the same two-step way Phase 3 does — `registry.alias_lookup(ScopedKey(canonical_name))`
  first (the persisted Key_A twin), `scoped_lookup` as fallback (C1); `instance_path` =
  `owning_part_leaf(alias.owning_part_qn)` (the shared helper below). **Why the
  `alias_lookup` read does not violate INV-1:** INV-1 governs which entries *surface* —
  only `expose_pure` ChannelAliases + `_scoped_alias`, never a scan of `_alias`. Here the
  entry is *already* source-selected as `expose_pure`; `alias_lookup` is used only to
  resolve that already-chosen alias's channel string. The spec's ban on `_alias` was
  against *sourcing* from it (source-erased, un-filterable), not against a targeted channel
  lookup for an already-EXPOSE_PURE alias. Implementation must not "fix" this back to
  `scoped_lookup`.

- **`owning_part_leaf` shared helper** (`core/` or `output_registry_builder.py`, new;
  Dim-4). The leaf derivation `qn.rsplit("::",1)[-1] if "::" in qn else qn.split("__")[-1]`
  is already copied twice (`output_registry_builder.py:260-263`, `308-311`).
  `_build_output_aliases` needs the identical rule; extract one helper and call it from all
  three sites so shape A and shape B can't drift (a `::`-form `owning_part_qn` must not
  yield a `__`-split wrong leaf).

- **Registry read accessor** (`core/output_registry.py`, new small property, e.g.
  `scoped_alias_items()` → the `(scope, leaf) → channel` pairs). Tests already read
  `registry._scoped_alias`; a public read accessor keeps `_build_output_aliases` off
  the private attribute.

- **Shape-A reroute** (`_build_attribute_resolution_map`, EDIT). Split the EXPOSE_PURE
  branch on `ca.is_on_part_definition`. Part usage (shape B): unchanged
  `_resolve_expose_pure` path. Part def (shape A): do **not** call the refs-parser;
  set the resolution to LITERAL (today's post-warning behavior, B3), and consult
  `_scoped_alias` to decide the warning — resolvable → silent, unresolvable → a
  warning that names the real cause, not "Item 10/11".

- **Exit-point filename override** (`generation/pipeline.py` `_build_exit_points`,
  `templates/pipeline_yaml.jinja2`, EDIT). Build a `canonical_channel → filename` map
  from `graph.output_aliases` (filename = `{instance_path}__{alias_name}.json`). In
  `_build_exit_points`, each channel's exit uses its alias filename when present, else
  today's `{channel}.json`. The template's exit line gains a `filename` field
  (`{{ exit.name }}: {{ exit.type }} {{ exit.filename }}`) — key and type unchanged, so
  no conformance-test change. If one channel carries two aliases (two names on one
  channel), pick the filename deterministically (first by sorted `alias_name`); both
  entries still appear in `output_aliases` for programmatic consumers.

## Non-Goals

- Redefinition (`:>>`) / design_override name surfacing (BACKLOG follow-up; they
  resolve as channels but their names aren't EXPOSE_PURE-sourced).
- EXPOSE_COMPUTED surfacing — stays rejected per §3; its warning stays.
- New resolution logic. The shape-A reroute connects landed machinery; it adds no
  lookup, rewrite, or classification.
- Wiring a FORMULA CA input that consumes a *shape-A* exposed name. No fixture; the
  per-def resolution map is structurally instance-blind (pre-existing limitation, B3).
  Documented, not fixed.
- Extraction-snapshot format change (snapshots carry no graph).

## Implementation Notes

- **Thread shape B in:** add `channel_aliases: list[ChannelAlias] | None = None` to
  `build_computation_graph`; pipeline_builder passes `all_channel_aliases`. Filter to
  `.source == "expose_pure"` inside `_build_output_aliases`.
- **instance_path for shape B** = `owning_part_leaf(alias.owning_part_qn)`, the shared
  helper (Dim-4) that both Phase 3 (`output_registry_builder.py:260-263`) and the
  `_scoped_alias` registration (`308-311`) already need. Extracting it — rather than a
  third hand-copied `rsplit("::") / split("__")` — is what keeps `instance_path` (and thus
  the filename) matched to the registered scope for both `::`- and `__`-form QNs.
- **Reroute placement:** the EXPOSE_PURE `is_on_part_definition` split is the only
  edit to `_build_attribute_resolution_map`; leave the FORMULA and shape-B arms byte
  identical. The shape-A resolvability probe can leaf-match `_scoped_alias` on
  `ca.python_name`; if precise instance-qualified matching is wanted (to avoid
  silencing a genuinely-broken def that shares a sanitized name with a resolvable
  one), thread the part-def's instance paths — a plan-time precision call, low stakes.
- **Warning retirement diff:** `:796` and `:809` are inside `_resolve_expose_pure`,
  which shape A no longer calls — so shape A goes silent by *not reaching* them, while
  shape B still calls the function and an unresolvable shape B still warns at `:796`.
  Do not delete the branches; they remain the shape-B / unresolvable path.
- **YAML type unchanged:** the alias only renames the filename on the channel's own
  exit line, so the line's `Type` stays the channel's exit type — no type derivation
  needed. Only the third (filename) token changes.
- **`output_aliases` order is graph-level determinism (INV-5); the YAML filename map is
  a lookup by channel** — independent of `output_aliases` list order, so the two can't
  disagree.

Interface sketch (≤10 lines):

```python
class OutputAlias(BaseModel):
    alias_name: str          # sanitized python_name (Item 5 / REQ-NC-06)
    canonical_channel: str   # the channel the value flows on (INV-2)
    instance_path: str       # scope: "demo_plant", "chamber_a" (INV-4)
    shape: Literal["part_def", "part_usage"]
    @property
    def output_filename(self) -> str:
        return f"{self.instance_path}__{self.alias_name}.json"
```

## Potential Risks

- **TEAx ExitPoint runtime grammar — DISCHARGED (2026-07-06).** Confirmed against the
  real consumer (`simkit`, `pipeline_schema.py` `_parse_exit_outputs`): the exit key
  must be an existing channel and the value is `<Type> <filename>` with a
  duplicate-filename check. D3 adopts the grammar-conforming filename-rename form; the
  earlier new-line form is rejected because it fails simkit's key-is-a-channel
  validation. No residual runtime-grammar risk.
- **Baseline churn misread as behavior change.** All 7 graphs churn (field addition).
  *Mitigation:* the spec's Baseline Regeneration section pins the review classes;
  regen only via the capture scripts with reviewed diffs.
- **Over-silencing shape-A warnings** if leaf-only `_scoped_alias` matching is used and
  two defs share a sanitized name (one resolvable, one not). *Mitigation:* low
  likelihood; instance-qualified matching available if a case appears (Impl Notes).

## Integration Strategy

Complements Item 10 (which resolves both shapes for consumers) by surfacing the name
into the artifact. Adds no exit line; an aliased channel's existing exit line gets the
modeler's name as its output filename, unaliased lines are byte-identical to today.
Completes Item 1's interim warning measure for the resolvable case. Generation still
consumes only `ComputationGraph`.

## Validation Approach

- **Field-set conformance — the graph-rev gate (R1), incl. the tests that MUST flip
  (M1).** Adding `output_aliases` deliberately hard-fails the exact-set assertion at
  `tests/conformance/test_graph_assembly.py:365`
  (`set(ComputationGraph.model_fields.keys()) == {modules, entry_point_groups,
  execution_order, fallback_entry_points}`). That failure *is* the discipline working —
  update it to name `output_aliases` in the set. Also add an `output_aliases` case to the
  per-field annotation test in `tests/unit/test_data_models.py`. (`test_orchestrator.py:744`
  uses `in` checks and survives — no change.) Plus a new positive test asserting
  `output_aliases` is a `list[OutputAlias]` with the four fields.
- **Shape A end-to-end** (`wi014_toy`): graph carries `OutputAlias(total_cost,
  …cost_calc__cost, demo_plant, part_def)`; new committed YAML baseline shows the
  `…cost_calc__cost` exit line's filename is `demo_plant__total_cost.json`.
- **Shape B end-to-end** (`attr_expr_probe`): graph gains the three
  `scale_result`/`half_vol`/`quarter_vol` entries; the YAML diff renames those three
  channels' exit filenames to the modeler's names; all other lines byte-identical.
- **Nested shape-B — the C1 guard** (`ife_plant`, the plant-idiom fixture whose EXPOSE
  sits at `plant.subsystem.calc.output`, a *nested* usage): assert its exposed names
  surface as `OutputAlias` entries with a resolved (non-null) `canonical_channel` — the
  test that fails if the resolver ever regresses to `scoped_lookup`-only and silently
  drops nested exposures. This is the coverage that keeps the item from no-oping exactly
  where the spec wants it populated.
- **Collision** (`sibling_channel_ambiguity`, unit test, D5): the two shape-A siblings
  produce two distinct output filenames (`chamber_a__power.json`, `chamber_b__power.json`)
  — no duplicate. (Note per Dim-1: this exercises the shape-A `_scoped_alias` scope half;
  shape-B instance-qualification collision is uncovered but low-risk — distinct owning
  parts give distinct leaves.)
- **Tie-break (M4):** a unit test for one channel carrying two aliases (two attributes
  exposing the same calc output under two names) → the exit filename is the deterministic
  first-by-sorted-`alias_name`, and *both* entries still appear in `output_aliases`.
- **Determinism (INV-5):** a test asserting `output_aliases` equals its
  `(instance_path, alias_name)`-sorted copy.
- **Warning matrix (INV-6):** `test_wi014_toy.py:28-40` flips from pinning the
  malformed-refs warning to asserting shape-A resolution + the surfaced `total_cost`
  alias, and that the resolvable case emits no warning; unresolvable-refs and
  EXPOSE_COMPUTED warnings still fire.
- **Regen:** 7 graph baselines (`capture_pipeline_baselines.py`, license-free);
  `attr_expr_probe` YAML; new `wi014_toy` YAML (register in
  `capture_baseline_yaml.py` `MODELS`; confirm license-free at plan time). No snapshot
  changes.
- **Gate:** `pytest`, `ruff check src/`, `mypy src/` (record counts; `uv run` may be
  approval-gated).

## Docs & REQ Census

- **Tags (next free):** `REQ-DM-09` (the `output_aliases` field: shape, existence
  validation INV-3, deterministic order INV-5); `REQ-PY-08` (aliased channel's exit
  line renders the modeler's name as its output filename); `REQ-CA-11` (shape-A
  EXPOSE_PURE routed via `_scoped_alias` in the
  attribute resolution map, warning retired for the resolvable case).
- **Doc 09** (`09-data-models.md:224`): add `output_aliases: list[OutputAlias]` to the
  ComputationGraph field list and an `OutputAlias` model entry; the current list omits
  `fallback_entry_points` (exclude=True) — `output_aliases` is present precisely
  because it is not excluded (contrast noted). Fix the stale `models.py:174` line ref.
- **Doc 21** (`21-pipeline-yaml-generation.md`): document exit-point filename override
  — an aliased channel's exit line carries the modeler's name as its `.json` filename;
  cite the simkit `<Type> <filename>` grammar; add the REQ-PY-08 matrix row.
- **Doc 16** (`16-computed-attributes.md`): the EXPOSE_PURE → surfaced-name story end
  (name now emitted as a named capture); the shape-A warning retirement.
- **modeling-assumptions §3:** reconcile "consumers bind to `subsystem.exposed_name`"
  with the sanitized `python_name` form (Item 5 / REQ-NC-06) — the consumer binds the
  sanitized exposed name.
- **verification-matrix.md:** rows for REQ-DM-09, REQ-PY-08, REQ-CA-11.
- **agentic-mbse:** record the EXPOSE-pattern docs impact — the exposed name now
  surfaces downstream as a named output capture (documentation-only note; no code).
- **Release notes — the filename move is a downstream-coordination change (M2).** Add
  `.project/active/alias-surfacing/release-notes.md` (Item 10's
  `.project/active/cross-part-wiring/release-notes.md` is the template). This is not mere
  baseline churn: aliased channels' output files MOVE `{channel}.json` →
  `{instance}__{alias}.json` — `attr_expr_probe` moves three (`scale_result`, `half_vol`,
  `quarter_vol`), `wi014_toy` moves one. Any consumer reading generated output by the old
  `{channel}.json` path (e.g. a fusion-tea harness) sees the move. Enumerate which
  baselines' exit filenames change and the consumer-visible effect, so it's a coordination
  note, not a surprise.

## Next-Stage Handoff

- **Fixed:** the two sources (INV-1); shape-B resolution via the Key_A `alias_lookup`
  twin with `scoped_lookup` fallback, INV-1 non-violation stated (C1); channel identity
  read-not-derived (INV-2); the five HARD invariants; EXPOSE_PURE-only scope; the entry
  shape (D2); always-serialized field (D1); filename-rename YAML capture confirmed against
  simkit (D3); run-mode-split filter (D4/M3); collision + nested-shape-B + tie-break +
  field-flip tests pinned (D5/C1/M4/M1); shared `owning_part_leaf` helper (Dim-4);
  release-notes deliverable (M2). The TEAx grammar handoff is **discharged**.
- **Open (plan-time):** precise vs leaf-only `_scoped_alias` matching in the reroute;
  whether `wi014_toy` YAML captures license-free; exact wording of the `include_all`-drop
  error (raise vs WARNING, D4).

---
Next Step: After approval → `/_my_plan` (or `/_my_implement`).
