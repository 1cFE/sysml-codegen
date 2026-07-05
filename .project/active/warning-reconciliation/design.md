# Design: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Branch:** upstream-findings-epic
**Base commit:** 88115b8 (re-anchor to Item 6's committed state at implement)
**Epic Item:** UPSTREAM-FINDINGS Item 7

---

## Overview

Make the codegen "Registry unresolved" warnings mean something: fix the two
matcher bugs so benign misses resolve at the right stage with the right ADR-001
kind, then add a hard params-coverage check (V11) plus a single post-assembly
reconciliation summary so a genuinely uncovered input fails loudly and precisely.

## Related Artifacts

- **Spec (contract):** `.project/active/warning-reconciliation/spec.md`
- **Spec review + resolutions:** `.project/active/warning-reconciliation/spec-review.md`
- **Research §SC-8:** `.project/research/20260705_upstream-findings-deep-research.md`
- **Item 5 close-out (lockstep obligation):** `.project/active/identifier-sanitization/close-out.md`
- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 7 + R1/R2/R3)
- **V-pattern:** `docs/architecture/modeling-assumptions.md`

---

## Research Findings

Line numbers are HEAD (88115b8); re-verify at implement against Item 6's commit.

**The two matcher bugs, at the resolution seam.**
`_resolve_binding` (`dependency_backtracker.py:517-563`) dispatches a binding
through REFERENCE or CHAIN, then Step-3 design-attribute match
(`_resolve_to_design_attribute:614`), then a Step-4 warn-and-fallback
(`:553-563`). Both bugs live in Step-3's dotted/`::` branches:

- **`::`-QN branch (`:659-666`)** converts with `sysml_to_python_qualified_name`
  (a bare `::`→`__` swap, `qualified_names.py:103`) and compares against
  `attr.qualified_name`, which is **per-segment sanitized**
  (`build_element_qualified_name` → `sanitize_name` per segment,
  `qualified_names.py:57,76`). A quoted owner never matches.
- **dotted branch (`:642-654`)** matches on
  `attr.name == attr_name and attr.parent_part == parent_part`. A design
  attribute owned by a part **def** has `parent_part == ''` (from
  `get_parent_part_name`, agentic-mbse), while the binding's `parent_part` is the
  part **usage** name. Never matches.

**Why a miss is lossy.** On a Step-3 miss the binding drops to Step-4, which
mints `f"{usage.qualified_name}__{param_name}"` as the entry-point QN. Downstream
`_classify_entry_points` (`graph_builder.py:386`) keys classification off that QN:
- the fallback QN is not in `design_attr_by_qname` → **Strategy 3 USAGE_LITERAL**
  (`:463-473`), default = `float(source_path)`, which for a dotted/`::` reference
  is unparseable → **default_value None**;
- had Step-3 returned the design-attr QN, classification hits **Strategy 1
  DESIGN_ATTRIBUTE** (`:439-447`), default = `attr.default_value`, and two calcs
  reading one attribute collapse to one entry-point QN (Step-3 dedup).
So one fix flips both the ADR-001 kind **and** the default-value source, and
restores dedup. This is the behavioral churn the review procedure enumerates.

**The deriver follows the backtracker for free.** `ParameterGroupDeriver.classify`
(`parameter_groups.py:506`) resolves group membership by looking the QN up in
`_attr_index`, which is keyed by every design attribute's own `qualified_name`
(`:305-310`) — def-owned attrs included. So once the backtracker returns the
design-attr QN, grouping (`classify`), default (`get_default_value:530`), and
graph classification all land correctly with no deriver change. **The def-owned
matcher belongs in the backtracker, not the deriver** (resolves the spec's open
ownership question for REQ-PGD-08; see Key Decisions).

**The lockstep registry keys are not serialized.** The FORMULA sysml-QN registry
is built at orchestration time (`output_registry_builder.py:129-131`) and never
written to a snapshot. `output_registry_builder.py:124` already sanitizes the
module_eqn; only the registration key at `:130` remains raw. On every committed
model no calc-def owner is quoted, so `sanitize_qualified_name` is the identity
there and the flip is byte-invariant on snapshots/baselines. Only the *matcher*
fixes churn baselines (via reclassification), not the flip.

**Coverage-check precedent.** `_validate_channel_references`
(`graph_builder.py:612`) walks `module.inputs`, collects declared channels, and
raises on a `module_output` input whose `producer_channel` is undeclared. V11's
collector is its sibling for the `entry_point` input case: the referenced params
key is `f"{param_group}.{qualified_name}"` (`generation/pipeline.py:167-168`).

**The real V11 gap is null-default filtering, not group membership (crux).**
`build_computation_graph` Step 6.8 (`graph_builder.py:303-337`) sweeps any entry
point not covered by a derived group into a synthetic `system_design` group, and
Step 6.9 back-fills `inp.source.param_group`. So within the graph every
`entry_point` input names a group that exists **and is a member of it** — group
membership can never be the gap. The gap is downstream: the JSON generator emits
a key **only when `ep.default_value is not None`** (`generation/entry_point.py:297`,
key = `ep.qualified_name`). The catf_mfe `magnet_volume` EP is a full member of
`magnets_params` in the graph (`computation_graph.json:3537-3586`,
`entry_type: usage_literal`, `default_value: null`), so its JSON key is silently
skipped, while the pipeline still emits
`magnets_params.CATFMFEMagnets__catf_tf_system__cryo_load__magnet_volume`
(`pipeline.py:167-168`) — a reference to a key the JSON declined to mint. That is
the runtime failure.

So **the V11 collector must mirror the JSON filter**: compare each module input's
`{param_group}.{qualified_name}` against the set of EPs whose `default_value is
not None` (the keys actually written). Comparing against param-group *membership*
would report catf_mfe as covered and miss the real gap.
`catf_radial_build__magnet_volume_total` (the FORMULA source) is a computed
attribute, never an entry point, so it is in no group and no JSON — it is not what
the input references; the input references the null-default `cryo_load` EP.

---

## Core Concept

Three defects compound into warnings that fire on healthy models and go silent
on a broken one. The fix works in the same order the defects compound:

1. **Resolve the benign misses at the source.** Two one-line matcher corrections
   in Step-3 (`::`-QN per-segment sanitize; def-owned dotted match) turn
   first-pass misses into correct DESIGN_ATTRIBUTE resolutions. The Step-4
   fallback stops firing for them. This is behavioral — entry points reclassify,
   keys dedup, default-value sources switch — and that churn is *intended output*,
   captured in regenerated baselines and enumerated in release notes.

2. **Flip the FORMULA sysml-QN registry to sanitized keys atomically.** One
   producer and five consumers/twins of the raw-QN paths move to
   `sanitize_qualified_name` together. Raw→raw becomes sanitized→sanitized in one
   change, so the FORMULA REFERENCE match works on quoted owners and never breaks
   partway. An implement-time grep for any leftover bare-swap or raw
   `sysml_qn_lookup` key is a hard stop.

3. **Make the residue loud and precise.** With the benign noise gone, two loud
   signals remain: **V11** (hard error, aborts) — a wired module input references
   a `*_params.X` key the JSON never mints (its EP has a null default); and the
   **reconciliation summary** (WARNING, does not abort) — the operator digest of
   every Step-4 fall-through that still lacks a value. They overlap on the
   catf_mfe case (both fire) but play different roles: V11 is the hard
   runtime-safety backstop at the wiring level; the summary is the non-fatal "here
   is what didn't resolve" digest that replaces the demoted per-binding lines and
   also covers fall-throughs V11 doesn't abort on. The per-binding Step-4 line
   demotes to DEBUG; the repetitive alias-collision lines collapse to one
   count-summary.

The key insight: the warnings are worthless because one text covers three
different situations. The fix separates them by *stage and severity* — resolve
what should resolve, hard-fail what is genuinely uncovered, warn once on what is
known-unresolved-and-tracked — rather than tuning a log level.

## Key Bets

- **B1.** The resolved `qualified_name` of a def-owned design attribute contains
  the owning part-**usage** name as a segment (`...__{usage}__{leaf}`), so a
  binding's dotted `parent_part` (that same usage name) plus leaf uniquely picks
  it via QN suffix — the backtracker needs no part-usage→part-def map.
  *(Agent-verified on solar_battery: `...__battery_system__pack_count`,
  `...__solar_battery_plant__p_net_mw`.) If false → the QN-suffix guard misses
  (falls back to leaf-only/same-file, then refuses — safe miss, V11/summary catch
  it) or, worst case, two defs share a usage-segment+leaf and cross-wire (a silent
  wrong value).* De-risk first (Handoff): the guard **refuses to match on
  ambiguity**, so the bad branch is "miss," never "cross-wire."
- **B2.** Every quoted-owner FORMULA REFERENCE match runs through exactly the six
  enumerated sites; no seventh raw site exists. *If false → a leftover raw site
  silently re-breaks matching on quoted models.* De-risked by the [HARD]
  implement-time grep completeness stop.
- **B3.** For every entry point that *should* resolve to a design attribute, the
  design attribute's `default_value` equals the literal the USAGE_LITERAL
  fallback carries today — so correctly-resolving keys keep their value and only
  genuinely-different values move. *If false → a value silently changes.*
  De-risked by the value-level before/after in the review procedure (this is the
  regression class the procedure exists to catch, not an assumption to trust).
- **B4.** V11 at the generation boundary catches *uncovered params keys*, and the
  reconciliation summary catches *covered-but-valueless fall-throughs*; together
  they cover every loud case the epic requires to stay loud until Items 9–11.
  *If false → an SC-5 cross-part case goes quiet.* De-risked by the seeded fixture
  (V11) and the catf_mfe collector-list assertion (both paths exercised).

## Key Decisions

- **D1. Def-owned matcher lands in the backtracker (`_resolve_to_design_attribute`),
  REQ-BT-10.** *Rejected: the deriver (spec's tentative REQ-PGD-08 owner) — the
  deriver's `classify`/`get_default_value` are already keyed by the design-attr
  QN via `_attr_index`, so a backtracker fix propagates to grouping, default, and
  graph classification with no deriver change; a parallel deriver matcher would
  be redundant.* REQ-PGD-08 is reframed to "confirmed no deriver change required"
  (or retired) — see Handoff.
- **D2. Def-owned match = exact-first, then QN-suffix keyed on the binding's
  usage segment, else same-file, else refuse.** Precedence: try the existing
  `parent_part == parent_part` exact match first (preserves per-usage `:>>`
  overrides, which extract as usage-owned attrs with their own value); only on a
  miss consult def-owned candidates (`attr.name == leaf and attr.parent_part ==
  ''`). Disambiguate primarily by the QN suffix: the resolved
  `attr.qualified_name` contains the owning part-**usage** name as a segment even
  for def-owned attrs (agent-verified: `...__battery_system__pack_count`,
  `...__solar_battery_plant__p_net_mw`), so
  `attr.qualified_name.endswith(f"__{parent_part}__{leaf}")` uses the binding's
  own usage name as the guard. Exactly one such candidate → use it; a different
  parent usage yields a different suffix, so two defs cannot cross-wire. Fall
  back: one leaf-only candidate → use; same-file tiebreak → use; else return None
  (fall to Step-4, caught loudly). *Rejected: bare QN-suffix `endswith("__leaf")`
  with no usage-segment guard — over-matches sibling attrs across defs and can
  cross-wire (B1's bad branch). Rejected: resolving usage→part-def — the
  backtracker holds no part-usage→def map, and the QN suffix already carries the
  usage name.*
- **D3. Lockstep flip mechanism = `sanitize_qualified_name` on both registry
  producer and every consumer/twin.** Registration wraps the `::`-form key in
  `sanitize_qualified_name`; every lookup sanitizes its `source_path`/`ref`
  before `sysml_qn_lookup`; every bare-swap twin switches to
  `sanitize_qualified_name`. *Rejected: leaving `input_resolver.py:120` and
  `parameter_groups.py:439` on the old form (Item 5's under-count) — a registry
  whose key form changes cannot leave a consumer on the old form; both flip or
  the invariant is a lie.*
- **D4. V11 collector compares wired references against MINTED JSON keys
  (non-null default), at the generation boundary.** A pure collector returns the
  violation list from a `ComputationGraph`; a violation is a module `entry_point`
  input whose `{param_group}.{qualified_name}` names an EP with `default_value is
  None` (mirroring the JSON filter, `entry_point.py:297`). The CLI (`run_codegen`)
  calls it and raises V11 on any non-empty result — **always strict, no
  escape-hatch flag**. *Rejected: comparing against param-group membership — Step
  6.8 makes every EP a member, so membership can never fail and catf_mfe reads as
  covered (the crux finding); the true gap is the null-default filter. Also
  rejected: enforcing inside `build_computation_graph` — the invariant is
  cross-artifact (graph EPs vs. generated JSON) and conformance tests that only
  build the graph must call the collector and assert on the list without tripping
  strict enforcement (keeps catf_mfe's 42-module coverage green).*
- **D5. Reconciliation summary and alias-collision summary computed post-assembly,
  logged at WARNING when non-empty; per-binding lines demote to DEBUG.**
  *Rejected: blanket-demoting all Step-4/alias lines to DEBUG/INFO — buries the
  SC-5 cross-part cases the epic requires loud.*

## Architecture

Four seams, in pipeline order:

1. **Registry build (orchestration).** `output_registry_builder` registers the
   FORMULA sysml-QN key sanitized. `output_registry.register_alias` stops logging
   per-collision at WARNING (demotes to DEBUG) and records collisions; the
   builder emits one WARNING count-summary after Phase 1a–4.

2. **Resolution (analysis).** `_resolve_to_design_attribute` gains the two
   matcher fixes. `_resolve_binding` Step-4 demotes its per-binding line to DEBUG
   and records the fall-through in a new `BacktrackingResult` field
   (`fallback_entry_points`), so the summary is exact, not re-derived.

3. **Graph assembly (resolution).** Unchanged structurally. Its existing
   `_classify_entry_points` now sees resolved design-attr QNs and classifies them
   DESIGN_ATTRIBUTE — the churn originates here as a consequence of seam 2.

4. **Generation boundary (CLI).** After `build_pipeline_context` returns `ctx`,
   `run_codegen` calls the **params-coverage collector** on
   `ctx.computation_graph` and raises **V11** on any violation, and computes the
   **reconciliation summary** from `ctx` (fall-through EPs whose final
   `default_value is None`), logging WARNING when non-empty. Both sit beside the
   existing `_check_duplicate_output_paths` fail-fast (`cli/__init__.py:773`).

Data flow for one binding: `binding → _resolve_binding → (Step-3 match → design
attr QN | Step-4 fallback QN) → entry_points/binding_resolutions →
_classify_entry_points → EntryPoint(kind,default) → ParameterGroup → module input
source "group.qn" → [V11 collector: is "qn" minted (non-null default)?] → pipeline YAML`.

## Required Invariants

- **INV-1.** After the flip, the FORMULA sysml-QN registry producer and all
  consumers use `sanitize_qualified_name`; grep for bare `sysml_to_python_qualified_name`
  on a comparison-bound QN and for raw `sysml_qn_lookup(SysMLQN(...))` returns
  zero hits at the six sites. (Completeness stop.)
- **INV-2.** The def-owned matcher never returns a QN whose leaf ≠ the binding's
  attribute leaf, and never picks among >1 def-owned candidates unless the
  QN-suffix (`__{parent_part}__{leaf}`) or same-file guard resolves to exactly
  one; otherwise it returns None. (No cross-wire.)
- **INV-3.** The V11 collector is pure: it returns a (possibly empty) list and
  raises nothing. Only the generation boundary raises. Collector-only conformance
  tests never trip strict enforcement.
- **INV-4.** For catf_mfe, the collector returns exactly
  `[cryo_load.magnet_volume]` (list content pinned; grow/shrink fails the test).
- **INV-5.** Clean fixtures (see Validation) generate with zero WARNING lines.
- **INV-6.** The flip is byte-invariant on every committed snapshot/baseline; only
  the matcher fixes change baseline bytes.

## Component Overview

- **`sanitize_qualified_name`** (`core/qualified_names.py:108`) — existing Item-5
  helper; the flip's single tool. No change.
- **Def-owned match** — new branch inside `_resolve_to_design_attribute`
  (`dependency_backtracker.py:642`). Pure function over `self._design_attributes`
  and the consuming usage.
- **`fallback_entry_points`** — new set field on `BacktrackingResult`
  (`dependency_backtracker.py:74`), populated at the Step-4 site.
- **Alias-collision accumulator** — collisions recorded on `OutputRegistry`
  (`core/output_registry.py`), summarized once by `output_registry_builder`.
- **`collect_uncovered_params(graph) -> list[UncoveredInput]`** — new pure
  collector, sibling to `_validate_channel_references` (`graph_builder.py`). Each
  item names module, input, and missing key.
- **V11 enforcement + reconciliation summary** — new calls in `run_codegen`
  (`cli/__init__.py`), after context build, before output clear.
- **Seeded fixture** — new minimal SysML model producing one uncovered
  `*_params.X` input (see Implementation Notes).

## Non-Goals

- Wiring cross-part references (`tf_coil.volume` and kind) — Items 9–11. The
  coverage check keeps them loud meanwhile.
- Altering the catf_mfe fixture model (spec decision).
- Changing channel-name (PQN) derivation — already sanitized (Item 5).
- A deriver-side def-owned matcher (D1 — not needed).

## Implementation Notes

- **Six lockstep sites (exact before → after):** see the Lockstep appendix.
- **Def-owned branch shape** (pseudo, ~10 lines):
  ```
  # dotted branch, after the existing exact-match loop returns nothing:
  cands = [a for attrs in self._design_attributes.values() for a in attrs
           if a.name == attr_name and a.parent_part == ""]
  suffixed = [a for a in cands
              if a.qualified_name.endswith(f"__{parent_part}__{attr_name}")]
  if len(suffixed) == 1: return suffixed[0].qualified_name
  if len(cands) == 1:    return cands[0].qualified_name
  same_file = [a for a in cands if a.source_file == usage_file]
  if len(same_file) == 1: return same_file[0].qualified_name
  return None   # ambiguous or none: fall to Step-4, caught loudly
  ```
- **V11 message (V-style):** name the module, the input param, and the missing
  key; state the fix. E.g. `V11: module '<name>' input '<param>' references params
  key '<group>.<qn>', which no parameter JSON provides (its entry point has no
  default value, so the key is never minted). Cause: an unresolved cross-part
  reference not yet wired (Items 9–11) or a resolution bug.`
- **Reconciliation summary format:** one WARNING line —
  `Unresolved after assembly: N entry point(s) fell through and still lack a
  value: [<usage|param source_path>, ...]`.
- **Alias-collision count-summary:** one WARNING line —
  `OutputRegistry: N alias collision(s) resolved first-wins (M distinct keys).`
- **Seeded fixture shape (real SysML, R1):** the trigger is a *wired module input
  whose entry point has a null default* (so the JSON skips its key). Minimal
  model: one calc def with one input and one output; one calc usage that binds
  that input (non-literal) to a reference the resolver cannot give a numeric
  default — the reliable, cross-part-free trigger is a binding to an attribute
  whose `feature_value_expression` is symbolic/non-numeric (so `float(...)` →
  None), or a design-attribute reference with no default. Result: one EP,
  `default_value=None`, referenced by the module input → `collect_uncovered_params`
  returns exactly `[that input]` and strict generation raises V11. Keep it to two
  or three definitions so the assertion is unambiguous. Confirm the null-default
  path at implement (the design session could not run codegen).
- **V11 diagnostic number:** confirm V11 still free at implement (V1–V10 at
  `modeling-assumptions.md:370-379`); Item 5 did not consume it.

## Potential Risks

- **Under-count of the def-owned mechanism.** If a real fixture has two def-owned
  attrs with the same leaf and no same-file discriminator, D2 refuses (safe miss),
  but the intended resolution won't happen. Mitigation: the seeded fixture and the
  reclassification worksheet exercise the real shapes; if ambiguity appears,
  escalate the guard to a usage→def resolution (needs new data plumbing) — flagged
  in Handoff as the risk to de-risk first.
- **Item 6 baseline drift.** This item's files don't overlap Item 6's
  (`expression_utils`), but committed baselines churn under Item 6. Re-anchor
  baseline expectations to Item 6's commit at implement; regenerate via capture
  scripts only (R3), never hand-edit.
- **xfail footprint wider than one mark** (spec-review L2-1): catf_mfe E2E runs in
  two files, one via a class-scoped fixture whose failure cascades. See Validation
  for the enumerated set.

## Integration Strategy

The four seams extend existing mechanisms rather than introducing parallel ones:
the flip reuses Item 5's helper; the collector mirrors
`_validate_channel_references`; the summary reuses the Step-4 site and the
generation boundary already hosting `_check_duplicate_output_paths`. No new module
or subsystem. Docs move with code (R1): 11, 24 (matcher fixes + dispatch), 10
(sanitized FORMULA registration), 17 (def-owned ownership note / PGD-08 reframe),
07 (V11 collector, sibling to GA-03), modeling-assumptions (V11 + SC-8 note);
verification-matrix rows for REQ-BT-09/10, OR-09, PGD-08, GA-08, V11.

## Validation Approach

- **No mocks (R1).** All tests use real SysML fixtures.
- **Collector-list tests.** catf_mfe: assert `collect_uncovered_params(graph) ==
  [cryo_load.magnet_volume]` (INV-4). Seeded fixture: assert the list is exactly
  its one seeded input; assert strict generation raises V11 on it.
- **Zero-WARNING assertion (clean fixtures).** solar_battery, chain_spike,
  attr_expr_probe (models with no known cross-part gap). Capture the log at
  WARNING level over a full `run_codegen` and assert no line emitted.
  *(Confirm the clean-fixture set against live output in the worksheet — a fixture
  is "clean" only if it has zero fell-through-and-valueless EPs and zero uncovered
  keys.)*
- **catf_mfe E2E xfail set** (enumerate at implement, spec-review L2-1):
  `test_computed_attributes_e2e.py::test_catf_mfe_still_works`, and each test
  consuming the class-scoped `catf_mfe_output` fixture in
  `test_expression_compilation_e2e.py::TestCATFMFEValidation`. Prefer structuring
  the check so generation still completes for the non-coverage assertions if
  cheap; otherwise xfail each with a reason tracked to Items 9–11.
- **Reclassification review worksheet** (R3, keys AND values before/after): the
  appendix worksheet is the audit deliverable; regenerate baselines via capture
  scripts and diff key sets and values.
- **Gate:** full suite green except the enumerated catf_mfe xfails; ruff/mypy at
  or better than the pre-item baseline.

## Next-Stage Handoff

- **Fixed:** the six lockstep sites and their flip mechanism (D3); collector +
  always-strict boundary, no CLI escape hatch (D4); WARNING levels (D5);
  backtracker ownership of the def-owned matcher (D1); catf_mfe xfail + pinned
  collector list.
- **Open for plan:** exact xfail test list (enumerate live); the seeded fixture's
  concrete SysML; whether to restructure the check so catf_mfe's unrelated E2E
  assertions stay live vs. xfail-each; REQ-PGD-08 reframe vs. retire.
- **De-risk first:** B1 / the def-owned guard (D2). Before writing the matcher,
  confirm from the reclassification worksheet whether any corpus fixture presents
  >1 def-owned candidate for one leaf. If yes and same-file doesn't disambiguate,
  the refuse-branch leaves it for V11/summary — acceptable, but decide whether to
  add usage→def plumbing. This is the one place the design could be wrong in a way
  that matters (cross-wire vs. safe miss).

---

## Appendix A — Six-Site Lockstep Flip (exact before → after)

Registry keys are built at orchestration time and never serialized; the flip is
byte-invariant on all committed baselines (no quoted calc-def owner in the
corpus). Re-verify line numbers against Item 6's commit at implement.

| # | Site | Before | After |
|---|------|--------|-------|
| 1 | `orchestration/output_registry_builder.py:130` (registration) | `SysMLQN(f"{owning}::{ca.name}")` | `SysMLQN(sanitize_qualified_name(f"{owning}::{ca.name}"))` |
| 2 | `analysis/dependency_backtracker.py:595` (primary REFERENCE consumer) | `sysml_qn_lookup(SysMLQN(source_path))` | `sysml_qn_lookup(SysMLQN(sanitize_qualified_name(source_path)))` |
| 3 | `analysis/dependency_backtracker.py:660` (`_resolve_to_design_attribute` `::` branch) | `sysml_to_python_qualified_name(source_path)` | `sanitize_qualified_name(source_path)` |
| 4 | `orchestration/pipeline_builder.py:70` (`_remove_formula_from_design_attrs` twin) | `sysml_to_python_qualified_name(ca.owning_part_qualified_name)` | `sanitize_qualified_name(ca.owning_part_qualified_name)` |
| 5 | `resolution/input_resolver.py:120` (Strategy B, 2nd consumer) | `sysml_qn_lookup(SysMLQN(ref))` | `sysml_qn_lookup(SysMLQN(sanitize_qualified_name(ref)))` |
| 6 | `analysis/parameter_groups.py:439` (`_find_source_file` twin) | `sysml_to_python_qualified_name(source_path)` | `sanitize_qualified_name(source_path)` |

Note: `output_registry_builder.py:124` already sanitizes the module_eqn; site 1
is the last raw producer. Sites 2/5 are the two `sysml_qn_lookup` consumers of the
one registry; sites 3/4/6 are bare-swap twins whose comparison target is a
sanitized QN.

## Appendix B — Reclassification Worksheet (review procedure, R1/R2/R3)

Seeded from the committed baselines (`computation_graph.json`). The **verbatim
"Registry unresolved" line set** and the **full reclassification list** need a
live `run_codegen` at implement (this design session's sandbox blocked `uv run`);
the confirmed dedup pairs below are the anchors, and the value column is the
regression-catch (B3). Capture via the R3 scripts, never hand-edit.

**Confirmed Step-3 dedup collapses (solar_battery)** — a `usage_literal` twin and
its `design_attribute` share one value today and should collapse to the single
design-attribute key after the fix:

| Before (two keys) | Values | After (one key) | Value | Bug fixed |
|---|---|---|---|---|
| `...energy_production__p_net_mw` (usage_literal) + `...solar_battery_plant__p_net_mw` (design_attribute) | 0.008 / 0.008 | `...solar_battery_plant__p_net_mw` | 0.008 | dotted / def-owned (B) |
| `...battery_bos__cost_model__pack_count` (usage_literal) + `...battery_system__pack_count` (design_attribute) | 8.0 / 8.0 | `...battery_system__pack_count` | 8.0 | dotted / def-owned (B) |

(Prefix `SolarBatteryDesign__solar_battery_plant__`; groups `design_params` /
`system_design` respectively.) Values match, so B3 holds for these — no value
moves. The review must confirm the same for every reclassified key at implement.

**catf_mfe V11 target (INV-4).** The collector returns exactly one uncovered
input: module `cryo_load`, input `magnet_volume`, referencing
`magnets_params.CATFMFEMagnets__catf_tf_system__cryo_load__magnet_volume` — a
null-default EP (Items 9–11 cross-part gap). This is a genuine dangle, not a
reclassification target.

**Bug attribution (from source, agent-verified):**
- **Bug A** (`::`-QN sanitize) does not appear in solar_battery's plain bindings;
  it is exercised by quoted-owner fixtures (`quoted_owner_formula`, catf quoted
  magnet parts). The FORMULA REFERENCE path is where it bites.
- **Bug B** (def-owned dotted) is the solar_battery dedup driver above.

**To fill at implement:** the verbatim ~10 solar_battery "Registry unresolved"
lines; the catf_mfe 25/29 alias-collision count; the complete before→after key
set and value diff for every affected model; confirmation that no clean-fixture
value moved.

---
Next Step: After approval → `/_my_plan`
