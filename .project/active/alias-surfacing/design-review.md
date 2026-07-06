# Design Review: Derived-Attribute Alias Surfacing (SC-7)

**Design:** `.project/active/alias-surfacing/design.md`
**Spec:** `.project/active/alias-surfacing/spec.md`
**Review File:** `.project/active/alias-surfacing/design-review.md`
**Date:** 2026-07-06
**Reviewer HEAD:** `21b61be` (verified against source, not the design's prose)

---

## Fundamental Assessment

**Sound.** The approach is the minimal correct one: read the two provenance-carrying
sources Item 10 already built (`_scoped_alias` for shape A, `expose_pure` ChannelAliases
for shape B), normalize them into one instance-qualified list, stable-sort, validate
existence, and render each as the destination filename on its canonical channel's exit
line. It invents no new lookup or classification — it connects landed machinery to the
one consumer Item 10 left on the old path. No over-engineering: one new model, one derived
list, two small edits. The `OutputAlias` model earns its place (it is the serialized
artifact this whole item exists to produce). The D3 grammar (filename-rename) is correct
against the real simkit consumer and I did not re-litigate it.

I verified the load-bearing code claims directly and they hold: the resolution map's only
consumer is `_build_computed_attr_module` (B3 confirmed — `graph_builder.py:258/937`);
`_scoped_alias` has a single writer (`pipeline_builder.py:504`, part-def+EXPOSE guarded,
B1 confirmed); the exit template is `{{ exit.name }}: {{ exit.type }} {{ exit.name }}.json`
exactly as the design says; REQ-DM-09 / REQ-PY-08 / REQ-CA-11 are all free.

But four things need to close before implementation, and one of them (the shape-B
resolver) can make the item **silently no-op for a whole class of exposures**. This is a
**Revise**, not a Rework — the foundation is right; the gaps are specific.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec success criterion has a design element, and the HARD invariants map cleanly
(INV-1..6). Two compliance gaps:

- **Shape-B resolution may not satisfy the "reads the Item-10 mapping" HARD requirement
  for nested usages** (see Critical C1 below). The spec says surfacing reads the registry
  source of truth and does not re-derive. The design's chosen lookup (`scoped_lookup`)
  is *not* the lookup that actually resolves shape-B `canonical_name`s in the general
  case, so the item can drop exactly the aliases it must surface.
- **The collision SC ("two instances → distinct keys, demonstrated by committed
  coverage") is met via a unit test (D5), which the spec explicitly permits** — fine. But
  note `sibling_channel_ambiguity` (`power` on `part def Chamber`, two siblings) is a
  **shape-A** case, so the unit test exercises the `_scoped_alias` scope half, not shape
  B. Shape-B instance-qualification (owning-part-qn leaf) has no collision coverage. Low
  risk (distinct owning parts give distinct leaves), but state it.

### 2. Pattern Consistency
**Assessment:** Pass

Uses the existing precedents well: `_validate_channel_references` for existence checking,
the `fallback_entry_points` `exclude=` decision as the explicit contrast for D1, the
Phase-3 short-form scope derivation for `instance_path`. The Step-8.5 placement inside
`build_computation_graph` matches how every other derived graph artifact is assembled. No
new pattern invented where an old one fits.

### 3. Abstraction Quality
**Assessment:** Pass

`OutputAlias` is the right level — a flat record of the four facts a consumer needs. The
`output_filename` property co-locates the filename derivation with the data it derives
from, so the graph field and the YAML render can't disagree on the scheme. The registry
read accessor (`scoped_alias_items()`) to keep `_build_output_aliases` off the private
attribute is a reasonable small courtesy, consistent with the typed-registry discipline.

### 4. Duplication Avoidance
**Assessment:** Concerns

The `instance_path` derivation for shape B is specified as "keep the two derivations
identical" to Phase 3's `output_registry_builder.py:258-264` — but "keep identical" by
convention is exactly how parallel structures drift. The Phase-3 code handles both `::`
and `__` forms (lines 260-263). If `_build_output_aliases` re-implements only the `__`
split, a `::`-form `owning_part_qn` yields a wrong `instance_path` and thus a wrong
filename. Recommend a shared helper for the leaf derivation rather than a second copy.

### 5. Data Structure Clarity
**Assessment:** Pass

Fields are explicit and typed; the `shape` Literal is self-documenting and cheap. The flow
from source → `OutputAlias` → filename is traceable. Determinism (INV-5) is pinned to a
concrete key, `(instance_path, alias_name)`.

### 6. Route Safety
**Assessment:** Concerns

The shape-A reroute is safe (B3 verified). Two routing concerns:

- **D4's dangling-alias filter is a silent route in full runs.** The design's rationale
  for filtering-not-raising is sound *for targeted runs* (modules pruned before the alias
  registries are built). But the same filter runs on `include_all` baseline generation,
  where a dropped alias is not legitimate — it signals a real wiring regression — and it
  is swallowed with a debug log. INV-3 ("no dangling alias survives") is satisfied either
  way, but a genuine bug hides. Add: on an `include_all` run, dropping any alias is an
  error (or at minimum a WARNING the baseline diff would catch), so the filter only ever
  fires on the targeted-run case it was designed for.
- **The one-channel-two-aliases tie-break is specified but not routed to a test** (Minor
  M4 below).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1 and B3 are genuine, stated with the right failure mode, and I verified both. **B2 is
the problem.** As written — "every `expose_pure` ChannelAlias's `canonical_name` resolves
via `registry.scoped_lookup` — the same lookup Phase-3 registration uses" — B2 is not
true in the general case. Phase 3 (`output_registry_builder.py:265-267`) resolves
`instance_attr_to_channel.get(canonical_name)` **first** (a Key_A map, bare
`instance.attr`) and only falls back to `scoped_lookup`. `scoped_lookup` reads `_scoped`,
keyed by `make_scoped_key`, which drops the design prefix but keeps the **full nested
path** (`identifier_types.py:49-51`). So `scoped_lookup("component_cost.total_cost")`
matches only when the exposed calc usage sits directly under the design root. For a nested
part-usage EXPOSE (`plant.subsystem.calc.output` → bare `canonical_name` `calc.output`),
`scoped_lookup` misses. B2 is stated as verified; it is not. This is a **hidden bet**
surfaced: *the design bets shape-B canonical_names are all shallow (top-level usages),
and it doesn't say so.* If that bet is wrong for any populated baseline (ife_plant /
catf_mfe are the nested plant-idiom fixtures), the alias silently drops via D4.

D1, D2, D4, D5 each name their rejected alternative honestly. D3 is well-argued and
verified. Good.

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept states the mental model plainly before the mechanism (value already on
the channel → Item 10 mapped the name → this item reads two sources and renders them). The
shape-A/shape-B thread is carried consistently. The one worked data-flow example
(`total_cost`) is exactly what a reader needs. No jargon blocking the model.

---

## Issues by Severity

### Critical

- **C1 — Shape-B resolution uses the wrong lookup; nested exposures silently no-op.**
  `_build_output_aliases` is specified to resolve shape-B `canonical_name` via
  `registry.scoped_lookup` (B2, Component Overview, Impl Notes). Phase 3's actual primary
  resolver is `instance_attr_to_channel` (Key_A, bare `instance.attr`), with `scoped_lookup`
  only as fallback. `scoped_lookup` matches a bare `canonical_name` only for a top-level
  usage; a nested part-usage EXPOSE misses. Combined with D4's silent filter, a nested
  shape-B alias is dropped with only a debug log — the feature no-ops exactly where the
  spec wants it populated, and no test catches it. *Fix:* resolve shape-B `canonical_name`
  the same two-step way Phase 3 does — the Key_A map is also registered into `_alias`
  (`output_registry_builder.py:172`), so `registry.alias_lookup(ScopedKey(canonical_name))`
  reaches it. Using `alias_lookup` *to resolve a channel for an already-source-selected
  expose_pure alias* does not violate INV-1 (INV-1 governs which entries surface, not how
  their channel is looked up) — but the design must say so explicitly so implementation
  doesn't "fix" it back to the private `_alias` read the spec warned against. Alternatively
  confirm-in-writing that every shape-B fixture is shallow and pin a test that would fail
  if a nested shape-B case is ever added.

### Major

- **M1 — The field-set conformance test that will hard-fail is not enumerated.**
  `tests/conformance/test_graph_assembly.py:365` asserts
  `set(ComputationGraph.model_fields.keys()) == {modules, entry_point_groups,
  execution_order, fallback_entry_points}` — exact-set equality. Adding `output_aliases`
  breaks it. The design's Validation Approach lists a *new* `test_data_models`-style field
  presence test but never names this *existing* breaking test (nor
  `test_data_models.py:767-777`, which reads per-field annotations and should gain an
  `output_aliases` case). `test_orchestrator.py:744` uses `in` checks and survives.
  *Fix:* enumerate the exact-set test as a must-update artifact in the regen/validation
  plan, alongside the 7 graph baselines.

- **M2 — No release-notes / downstream-coordination note for the filename-rename
  behavioral change.** Aliased channels' output files MOVE:
  `{channel}.json` → `{instance}__{alias}.json`. `attr_expr_probe` moves three
  (`scale_result`, `half_vol`, `quarter_vol`); `wi014_toy` moves one. Anyone consuming
  attr_expr_probe-style generated output by path (fusion-tea harnesses reading
  `{channel}.json`) sees moved files. The design frames this only as internal *baseline
  churn* ("misread as behavior change" risk). It is an actual behavior change to generated
  artifacts. Item 10 shipped a `release-notes.md` (`.project/active/cross-part-wiring/`)
  documenting exactly this class of downstream impact; Item 11's design has none and the
  Docs & REQ Census doesn't plan one. *Fix:* add a release-notes entry enumerating which
  baselines' exit filenames change and the consumer-visible effect, so the file move is a
  coordination note, not a surprise.

- **M3 — D4's filter should assert-none-dropped on `include_all` runs.** As designed the
  filter is correct for targeted runs and silent everywhere. On a full/baseline run a
  dropped alias is a real regression, not a legitimate prune. *Fix:* elevate a drop during
  an `include_all` run to an error (or a WARNING the reviewed diff would surface), so the
  silent path only fires on the case D4 was written for.

### Minor

- **M4 — One-channel-two-aliases tie-break is specified but untested and self-flagged
  "open."** D3 / Component Overview picks "first by sorted `alias_name`"; the Next-Stage
  Handoff lists it as open plan-time wording; the Validation Approach has no test for it.
  Either pin a unit test (two attributes exposing the same calc output under two names →
  deterministic filename, both entries in `output_aliases`) or explicitly defer with a
  one-line "no fixture; behavior defined, unpinned" rationale. Don't leave it half-specified.

- **M5 — Architecture diagram overstates `_validate_channel_references`.** The diagram
  says it "yields declared_channels." It returns `None` and raises (`graph_builder.py:627`);
  it does not expose the channel set. `_build_output_aliases` must recompute the declared-
  channel set itself (or the validator must be refactored to return it). Small, but the
  design reads as if the set is handed over.

- **M6 — INV-5 sort key isn't proven unique.** `(instance_path, alias_name)` is a stable
  sort, deterministic given deterministic source iteration (dict insertion order +
  list order — both hold). But if one `(instance_path, alias_name)` ever came from both a
  shape-A and a shape-B source, order would depend on which source is iterated first. Almost
  certainly impossible (a name can't be both part-def- and part-usage-exposed on one
  instance), so note it as an assumption rather than fixing it.

---

## Recommendations

1. **Fix C1 first** — it is the one issue that can make the item silently fail its own
   success criterion. Resolve shape-B `canonical_name` via Phase-3's actual resolver
   (Key_A, reachable through `alias_lookup`), and state in the design why that read does
   not violate INV-1. Add a nested-shape-B guard test.
2. **Enumerate the breaking conformance test (M1)** in the regen plan — one line, but it's
   the graph-rev discipline the spec's R1 requires.
3. **Add a release-notes entry for the filename move (M2)** — match the Item 10 precedent.
4. **Harden D4 for full runs (M3)** and **pin or defer the two-alias tie-break (M4).**
5. **Fix the two prose inaccuracies (M5 `_validate_channel_references` "yields"; M6 sort-key
   uniqueness note)** and **share the `instance_path` leaf helper (Dim 4)** so shape A and
   shape B can't drift.

---

## Resolutions

*(Incorporated into design.md 2026-07-06; all findings applied.)*

- **C1 — FIXED.** Shape-B resolves `canonical_name` via the persisted Key_A path:
  `registry.alias_lookup(ScopedKey(canonical_name))` first (the twin of Phase 3's
  `instance_attr_to_channel`, registered at `output_registry_builder.py:172`),
  `scoped_lookup` as fallback. B2 rewritten (the `scoped_lookup`-only claim was wrong —
  it keeps the full nested path and misses nested part-usage EXPOSE). Stated why this
  `alias_lookup` read does not violate INV-1: INV-1 governs which entries *surface* (only
  expose_pure ChannelAliases + `_scoped_alias`); the entry is already source-selected as
  expose_pure and `alias_lookup` only resolves that chosen alias's channel string — not a
  scan of `_alias`. Added a nested-shape-B guard test on `ife_plant` (asserts the plant-
  idiom exposures surface with a non-null channel).
- **M1 — FIXED.** Validation Approach now names the breaking exact-set test
  `test_graph_assembly.py:365` as a must-flip artifact (add `output_aliases` to the set —
  the graph-rev discipline working), plus the `test_data_models.py` per-field case;
  `test_orchestrator.py:744` survives (noted).
- **M2 — FIXED.** Added a `release-notes.md` deliverable (Item 10's is the template):
  the `{channel}.json` → `{instance}__{alias}.json` filename move as a downstream-
  coordination note (attr_expr_probe moves 3, wi014_toy moves 1).
- **M3 — FIXED.** D4 split by run mode: targeted → drop + debug; `include_all` → dropping
  any alias is an error/WARNING (a real regression, not a legitimate prune). INV-3
  updated.
- **M4 — FIXED.** Tie-break pinned as a unit test (one channel, two aliases →
  deterministic first-by-sorted-`alias_name` filename, both entries retained). Removed
  from the "open plan-time" list.
- **M5 / M6 / Dim-4 helper — FIXED.** M5: diagram corrected —
  `_validate_channel_references` returns None/raises; `_build_output_aliases` recomputes
  its own declared-channel set. M6: INV-5 now states the sort-key uniqueness assumption
  (a name can't be both part-def- and part-usage-exposed on one instance). Dim-4: a
  shared `owning_part_leaf` helper replaces the third hand-copy of the `::`/`__` split,
  called by Phase 3, the `_scoped_alias` registration, and `_build_output_aliases`.

---

**Overall:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The highest-leverage
edit is C1 — verify shape-B `canonical_name` resolution against the real Phase-3 resolver,
not `scoped_lookup`, before any baseline is captured. The reviewer does not edit the design.
