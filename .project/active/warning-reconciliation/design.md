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

## Implement-Time Deviations (Item 7, applied 2026-07-05)

Phase 0 ran `run_codegen` against the committed snapshots (which the design session
could not) and found the Appendix-B worksheet mis-modeled the corpus. Orchestrator
rulings A1/B1/C1 resolve these. Full evidence: plan.md "Phase 0 Completion".

- **DEV-1 (worksheet correction; B1 ruling).** The two "confirmed dedup collapses"
  (pack_count, p_net_mw in solar_battery) **do not occur** and are removed:
  - `pack_count` is a **literal** binding (`source_path=None`); literals are
    classified USAGE_LITERAL directly (`dependency_backtracker.py:341-361`) and never
    reach `_resolve_to_design_attribute`. No matcher fix can dedup a literal.
  - `p_net_mw` is a **`::`-form reference** → the `::` exact-match branch, not the
    dotted branch of Bug B. Sanitize is a no-op (unquoted); exact-match still fails.
  The **actual** Bug-A churn is in **retype_model** (3 EPs: `ife_calc|p`, `hif_calc|q`
  ×2 — quoted-owner `::` refs to def-owned design attrs `RetypeLibrary__IFE_Driver__power`
  = 10.0, `RetypeLibrary__HIF_Driver__torque` = 20.0; USAGE_LITERAL→DESIGN_ATTRIBUTE,
  values change). This is the deliberate Phase-4 regen churn.

- **DEV-2 (Bug B pool restriction; A1 ruling; corrects B1/INV-2).** `_design_attributes`
  is populated from every AttributeUsage with a value expression, so it **includes
  calc-def `out attribute y = expr` outputs**, not only user design-part attributes
  (confirmed: `FusionPhysicsGeometry__TorusMinorRadius__a`,
  `ChainOverrideLibrary__CalibrationCalc__calibrated_factor`, etc.). The leaf-unique
  matcher (Bug B) therefore **filters the candidate pool to design-part attributes**,
  excluding calc-def I/O (`_is_calc_def_owned`: an attr is calc-def-owned when its QN
  minus the leaf equals a calc def's sanitized QN). Without this, a dotted calc-output
  reference (e.g. chain_override_probe `calibration.calibrated_factor`) would cross-wire
  into a DESIGN_ATTRIBUTE entry point with a library default — the silent mis-wiring
  this epic exists to kill. With it, that reference stays unresolved and LOUD
  (V11/summary), correct for an Items-9–11 cross-part/chained reference. Consequence:
  Bug B may have **zero corpus effect** (acceptable per A1); the seeded fixture proves
  the mechanism, the pool restriction is the safety property. B1 is reformulated:
  leaf-uniqueness is asserted over **design-part** attributes, not the raw pool.

- **DEV-3 (INV-5 scope; C1 ruling).** solar_battery emits two out-of-scope WARNINGs
  this item does not own — `EXPOSE_PURE misc_hardware_cost` (`graph_builder.py:689`)
  and `Module class name collisions` (`generation/registry.py:91`). They are real
  signals owned elsewhere (Item 11 / registry design) and are **not** silenced. INV-5's
  strict zero-WARNING assertion therefore applies to **attr_expr_probe, sample_model,
  chain_spike** only; for solar_battery the assertion is scoped to this item's
  categories (no Registry-unresolved noise, no reconciliation summary, alias collisions
  summarized).

---

## Design-Review Resolutions (design-review.md)

- **C1 — narrow V11.** Applied. V11's population is `fallback_entry_points` ∩
  valueless ∩ wired, not "wired + null-default." A null default is the user-fill
  signature (schema-required, JSON-omitted), so it never enters V11 unless the
  binding also *fell through* resolution. Verified from code that catf_mfe
  `magnet_volume` fell through (dotted CHAIN miss → Step-3 miss → Step-4), is
  valueless, and is wired — still caught. See Research Findings crux, D4, Concept.
- **M1 — partition V11 vs. summary.** Applied. Added the partition table
  (Architecture): wired → V11 (abort), unwired + residue → summary (WARNING); every
  fell-through-valueless EP in exactly one bucket.
- **C2 — drop the QN-suffix guard.** Applied. The QN segment is the part-**def**
  name for def-owned attrs, so the usage-name suffix guard was dead. Cascade is now
  exact `parent_part` → leaf-unique → refuse (same-file tiebreak removed). See D2,
  B1, INV-2, the pseudo-code, and the worksheet uniqueness check.
- **m1 — verbatim capture → Phase 0.** Applied. The before-baseline warning/JSON
  capture is now the plan's Phase 0 (Validation, Handoff, worksheet).
- **m2 — README null-key claim.** Applied. `entry_point.py:118` misstates that
  null keys appear in the JSON; the generator omits them. Correction added to the
  docs plan and Component Overview; it grounds the C1 rationale.

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

**V11 keys off fallthrough, not null-default (crux).** Two facts constrain the
predicate:
- *Group membership can never be the gap.* `build_computation_graph` Step 6.8
  (`graph_builder.py:303-337`) sweeps any orphan EP into a synthetic
  `system_design` group and Step 6.9 back-fills `inp.source.param_group`, so
  every `entry_point` input names a group it belongs to.
- *A null default is the normal user-fill signature, not a defect.* The JSON
  generator omits a key when `ep.default_value is None`
  (`generation/entry_point.py:297`); the Pydantic schema still declares it
  required. That is the documented mechanism for "user must supply this before
  running" — a legitimate required LIBRARY_DEFAULT or unset design attribute is
  null-default-and-wired and is *working as intended*. (README `entry_point.py:118`
  misstates this — it says null keys appear in the JSON awaiting values; they are
  omitted. Correct it, per m2.)

So V11 cannot fire on "null-default + wired" — that would redden every
user-supplied parameter. What makes catf_mfe `magnet_volume` a defect is that it
**fell through resolution**: a bound binding
(`magnet_volume = catf_radial_build.magnet_volume_total`, a removed FORMULA) that
matched no strategy and dropped to the Step-4 fallback, has no literal value, and
is still wired into the `cryo_load` module input. The pipeline emits
`magnets_params.CATFMFEMagnets__catf_tf_system__cryo_load__magnet_volume`
(`pipeline.py:167-168`); the JSON omits it (null default); no value can
legitimately fill it (it should have been an upstream output). That is a
guaranteed runtime `KeyError`, and the user cannot fix it by editing JSON.

So **V11's population is `fallback_entry_points` ∩ valueless ∩ wired** — bound
bindings that failed all resolution, carry no default, and are referenced by a
surviving module input. Verified for catf_mfe: `magnet_volume`'s source_path
`catf_radial_build.magnet_volume_total` is dotted → CHAIN dispatch misses
(cross-part FORMULA, unregistered) → Step-3 design-attr miss (the FORMULA source
was removed from `design_attrs`) → **Step-4 fallback**, `default_value=null`,
wired to `cryo_load`. All three hold.

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

3. **Make the residue loud and precise.** With the benign noise gone, the
   fall-through population (`fallback_entry_points`) that still lacks a value
   **partitions** by whether pipeline wiring references it: the **wired** half is
   a guaranteed runtime `KeyError` and raises **V11** (hard error, aborts); the
   **unwired** half plus any other tracked residue is the **reconciliation
   summary** (WARNING, does not abort). No fall-through EP is in both. The
   per-binding Step-4 line demotes to DEBUG; the repetitive alias-collision lines
   collapse to one count-summary.

The key insight: the warnings are worthless because one text covers three
different situations. The fix separates them by *stage and severity* — resolve
what should resolve, hard-fail what is genuinely uncovered, warn once on what is
known-unresolved-and-tracked — rather than tuning a log level.

## Key Bets

- **B1.** A design-attribute leaf name that a binding fails to match by exact
  `parent_part` is **unique across the model's design attributes** — so leaf name
  alone identifies the def-owned target. *If false (two design attrs share the
  leaf) → the matcher refuses and the EP falls through to V11/summary (a safe
  miss, never a cross-wire).* The design cannot key off the QN segment (it is the
  part-**def** name for def-owned attrs, not the binding's usage name), so
  leaf-uniqueness is the identifying signal; verify it holds for the corpus dedup
  cases in the worksheet (Appendix B). De-risk first (Handoff).
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
- **D2. Def-owned match = exact-first, then leaf-unique, else refuse.**
  Precedence: try the existing `parent_part == parent_part` exact match first
  (preserves per-usage `:>>` overrides, which extract as usage-owned attrs with
  their own value); only on a miss gather candidates by leaf name across all
  design attributes (`attr.name == attr_name`). **Exactly one candidate → use it;
  otherwise return None** (fall to Step-4, kept loud by V11/summary). Uniqueness
  is the whole guarantee: if one design attribute in the model carries the leaf,
  it is unambiguously the target; if two do, we refuse rather than guess.
  *Rejected: a QN-suffix guard `endswith("__{parent_part}__{leaf}")` — for a
  **def**-owned attribute `build_element_qualified_name` walks the def's ownership
  chain, so the segment is the part-**def** name, not the binding's usage name;
  the guard would never fire (C2). Rejected: a same-file tiebreak on multiple
  candidates — two same-named design attrs in one design file would cross-wire.
  Rejected: resolving usage→part-def — the backtracker holds no part-usage→def
  map.*
- **D3. Lockstep flip mechanism = `sanitize_qualified_name` on both registry
  producer and every consumer/twin.** Registration wraps the `::`-form key in
  `sanitize_qualified_name`; every lookup sanitizes its `source_path`/`ref`
  before `sysml_qn_lookup`; every bare-swap twin switches to
  `sanitize_qualified_name`. *Rejected: leaving `input_resolver.py:120` and
  `parameter_groups.py:439` on the old form (Item 5's under-count) — a registry
  whose key form changes cannot leave a consumer on the old form; both flip or
  the invariant is a lie.*
- **D4. V11 collector = fell-through ∩ valueless ∩ wired, at the generation
  boundary.** A pure collector returns the violation list from a
  `ComputationGraph`: a module `entry_point` input is a violation when its
  `qualified_name` is in `fallback_entry_points` (Step-4 fall-through), its EP
  `default_value is None`, and a surviving module input references it. The CLI
  (`run_codegen`) calls it and raises V11 on any non-empty result — **always
  strict, no escape-hatch flag**. *Rejected: "wired + null-default" alone — a null
  default is the user-fill signature (schema-required, JSON-omitted), so this
  reddens every user-supplied parameter (C1). Rejected: comparing against
  param-group membership — Step 6.8 makes every EP a member, so membership can
  never fail. Rejected: enforcing inside `build_computation_graph` — the invariant
  is cross-artifact and collector-only conformance tests must assert the list
  without tripping strict enforcement (keeps catf_mfe's 42-module coverage green).*
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
   `run_codegen` calls `collect_uncovered_params(ctx.computation_graph)` and raises
   **V11** on any violation (the wired fall-through-valueless set), and logs the
   **reconciliation summary** at WARNING for the unwired remainder plus tracked
   residue. Both sit beside the existing `_check_duplicate_output_paths` fail-fast
   (`cli/__init__.py:773`). Ordering: log the summary first, then raise V11, so the
   digest reaches the operator even when generation aborts.

Data flow for one binding: `binding → _resolve_binding → (Step-3 match → design
attr QN | Step-4 fallback QN) → entry_points/binding_resolutions →
_classify_entry_points → EntryPoint(kind,default) → ParameterGroup → module input
source "group.qn" → [V11: fell-through ∧ valueless ∧ wired?] → pipeline YAML`.

**V11 vs. reconciliation summary — a partition of the fell-through-valueless set
(M1).** Every EP in `fallback_entry_points` with `default_value is None` lands in
exactly one bucket, keyed on whether a surviving module input references it:

| Predicate | Fate | Level | Rationale |
|---|---|---|---|
| fell-through ∧ valueless ∧ **wired** | **V11**, generation aborts | ERROR | JSON omits the key, pipeline references it → guaranteed runtime `KeyError` |
| fell-through ∧ valueless ∧ **unwired** | reconciliation summary | WARNING | tracked residue; no runtime `KeyError` (nothing references it), but not silently benign |
| *(other tracked residue, e.g. demoted per-binding notes rolled up)* | reconciliation summary | WARNING | operator digest, replaces the DEBUG'd per-binding lines |

Fell-through EPs that *do* carry a value (a bound literal parsed to a float) are
minted normally and are in neither bucket. Non-fall-through null-default EPs
(legitimate user-fill) are in neither.

## Required Invariants

- **INV-1.** After the flip, the FORMULA sysml-QN registry producer and all
  consumers use `sanitize_qualified_name`; grep for bare `sysml_to_python_qualified_name`
  on a comparison-bound QN and for raw `sysml_qn_lookup(SysMLQN(...))` returns
  zero hits at the six sites. (Completeness stop.)
- **INV-2.** The def-owned matcher returns a QN only when exactly one design
  attribute carries the binding's leaf name; on 0 or >1 it returns None. It never
  picks among ambiguous candidates. (No cross-wire.)
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
- **Def-owned match** — new leaf-unique branch inside
  `_resolve_to_design_attribute` (`dependency_backtracker.py:642`). Pure over
  `self._design_attributes`.
- **`fallback_entry_points`** — new set field on `BacktrackingResult`
  (`dependency_backtracker.py:74`), populated at the Step-4 site; propagated onto
  `ComputationGraph` in `build_computation_graph` so the collector is pure over
  the graph alone.
- **Alias-collision accumulator** — collisions recorded on `OutputRegistry`
  (`core/output_registry.py`), summarized once by `output_registry_builder`.
- **`collect_uncovered_params(graph) -> list[UncoveredInput]`** — new pure
  collector, sibling to `_validate_channel_references` (`graph_builder.py`). Reads
  `graph.fallback_entry_points`, EP defaults, and module-input wiring; each item
  names module, input, and missing key.
- **README null-key note** — correct `entry_point.py:118` (m2): the JSON template
  **omits** null-default keys; the schema declares them required for user fill.
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
- **Def-owned branch shape** (pseudo, ~6 lines):
  ```
  # dotted branch, after the existing exact-match loop returns nothing:
  cands = [a for attrs in self._design_attributes.values() for a in attrs
           if a.name == attr_name]          # leaf match across all design attrs
  if len(cands) == 1:
      return cands[0].qualified_name         # unique leaf → unambiguous target
  return None                                # 0 or >1: fall to Step-4, kept loud
  ```
- **V11 message (V-style):** name the module, the input param, and the missing
  key; state the fix. E.g. `V11: module '<name>' input '<param>' references params
  key '<group>.<qn>', but that binding fell through resolution with no value — the
  JSON never mints the key, so the pipeline will KeyError at load. Cause: an
  unresolved cross-part reference not yet wired (Items 9–11) or a resolution bug.`
- **Reconciliation summary format:** one WARNING line —
  `Unresolved after assembly: N entry point(s) fell through and still lack a value
  (unwired): [<usage|param source_path>, ...]`.
- **Alias-collision count-summary:** one WARNING line —
  `OutputRegistry: N alias collision(s) resolved first-wins (M distinct keys).`
- **Seeded fixture shape (real SysML, R1):** the trigger is a binding that
  **falls through resolution** (Step-4), carries no value, and stays wired — the
  three V11 conditions. Minimal model: one calc def with one input and one output;
  one calc usage that binds the input (non-literal) to a dotted reference matching
  no resolution strategy and no design attribute (a dangling reference to a
  name/attribute that resolves to no channel and no design default). Result: one
  EP in `fallback_entry_points`, `default_value=None`, referenced by the module
  input → `collect_uncovered_params` returns exactly `[that input]` and strict
  generation raises V11. Keep it to two or three definitions so the assertion is
  unambiguous. It must NOT collide with the leaf-unique matcher — the referenced
  leaf must not name a real design attribute. Confirm the fall-through path at
  implement (the design session could not run codegen).
- **V11 diagnostic number:** confirm V11 still free at implement (V1–V10 at
  `modeling-assumptions.md:370-379`); Item 5 did not consume it.

## Potential Risks

- **Under-count of the def-owned mechanism.** If a real model has two design
  attributes sharing a leaf, D2 refuses (safe miss) and the intended resolution
  won't happen — the EP falls to Step-4 and stays loud, so a correctness
  regression is impossible, but a benign miss could persist. Mitigation: the
  reclassification worksheet confirms leaf-uniqueness for the corpus dedup cases;
  if a real collision appears, escalate to usage→def resolution (new data
  plumbing) — flagged in Handoff as the risk to de-risk first.
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
  is "clean" only if, after the matcher fixes, it has zero fell-through-and-valueless
  EPs, zero uncovered keys, and zero alias collisions.)*
- **catf_mfe E2E xfail set** (enumerate at implement, spec-review L2-1):
  `test_computed_attributes_e2e.py::test_catf_mfe_still_works`, and each test
  consuming the class-scoped `catf_mfe_output` fixture in
  `test_expression_compilation_e2e.py::TestCATFMFEValidation`. Prefer structuring
  the check so generation still completes for the non-coverage assertions if
  cheap; otherwise xfail each with a reason tracked to Items 9–11.
- **Reclassification review worksheet** (R3, keys AND values before/after): the
  appendix worksheet is the audit deliverable; regenerate baselines via capture
  scripts and diff key sets and values.
- **Plan Phase 0 — verbatim before-baseline capture (m1).** The first plan phase
  runs `run_codegen` on solar_battery and catf_mfe against Item 6's committed
  state and captures the verbatim "Registry unresolved" lines, the alias-collision
  count, and the current params-JSON key/value sets. This is the "before" half of
  the review worksheet; the design session's sandbox blocked it.
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
- **De-risk first:** B1 / leaf-uniqueness (D2). In Phase 0, confirm from the
  captured design-attribute set that the dedup-target leaves (`pack_count`, and
  any others that reclassify) are unique across the model's design attributes. If
  a real leaf collision appears, the refuse-branch keeps it loud (safe), but
  decide whether to add usage→def plumbing. This is the one place the design could
  be wrong in a way that matters (a benign miss, never a cross-wire).

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

| Before (two keys) | Values | After (one key) | Value | Path fixed |
|---|---|---|---|---|
| `...battery_bos__cost_model__pack_count` (usage_literal) + `...battery_system__pack_count` (design_attribute) | 8.0 / 8.0 | `...battery_system__pack_count` | 8.0 | **Bug B** def-owned dotted (leaf-unique) |
| `...energy_production__p_net_mw` (usage_literal) + `...solar_battery_plant__p_net_mw` (design_attribute) | 0.008 / 0.008 | `...solar_battery_plant__p_net_mw` | 0.008 | bare-name path (existing `:668`), not Bug A/B — confirm at implement |

(Prefix `SolarBatteryDesign__solar_battery_plant__`; groups `design_params` /
`system_design` respectively.) Values match, so B3 holds for these — no value
moves. **Leaf-uniqueness check (D2/B1):** the dedup targets `pack_count` and
`p_net_mw` each appear as exactly one *design attribute* — the twins
(`battery_bos__cost_model__pack_count`, `energy_production__p_net_mw`) are calc
input params (`usage_literal`), not design attributes, so they do not count
against uniqueness. Confirm at implement (Phase 0). The `p_net_mw` binding is a
**bare name**, so it flows through the pre-existing bare-name branch, not the
def-owned dotted fix; the def-owned dotted fix (Bug B, leaf-unique) is proven by
`pack_count`.

**catf_mfe V11 target (INV-4).** The collector returns exactly one uncovered
input: module `cryo_load`, input `magnet_volume`, referencing
`magnets_params.CATFMFEMagnets__catf_tf_system__cryo_load__magnet_volume` — a
fell-through, valueless, wired EP (Items 9–11 cross-part gap). A genuine dangle,
not a reclassification target.

**Bug A** (`::`-QN sanitize) does not appear in solar_battery's plain bindings; it
is exercised by quoted-owner fixtures (`quoted_owner_formula`, catf quoted magnet
parts) via the FORMULA REFERENCE path.

**To fill at implement (Phase 0):** verbatim ~10 solar_battery "Registry
unresolved" lines; catf_mfe 25/29 alias-collision count; complete before→after key
set and value diff per model; confirmation that no clean-fixture value moved; and
leaf-uniqueness of every reclassified design-attribute leaf.

---
Next Step: After approval → `/_my_plan`
