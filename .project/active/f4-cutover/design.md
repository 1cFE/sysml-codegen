# Design: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** truth-debt-epic
**Commit:** a32ae45
**Epic:** TRUTH-DEBT, Item 1 (SC-A, SC-G)

## Overview

Wire the live aggregation path through `resolve_input(AGG_STRATEGIES)`, delete the
channel-only `_resolve_aggregation_input_channel`, collapse the SumTerm/SingletonTerm
inline entry-point fallbacks into one reconciled helper (LocalTerm keeps its own, D5), and
reconcile the fallback so the baseline stays byte-identical. Fold in the `param_groups`
bind-mutate typing cleanup.

## Related Artifacts

- **Spec:** `.project/active/f4-cutover/spec.md` (revised post spec-review)
- **Spec review:** `.project/active/f4-cutover/spec-review.md`
- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 1; R1–R4); parent
  `.project/backlog/epic_pipeline_truth.md`
- **Required Reading (background):** `.project/active/matrix-truth/design.md` +
  `design-review.md` (F4 LAND-with-split; M3/M4); `probes/probe_iv_ep_key_divergence.md`
  (the coexisting-key evidence); `probes/probe_i_extended_parity.py`
- **Reference docs to move with code (R1):** `docs/architecture/reference/03,04,05,07,24`
- **Memory:** `f4-cutover-fallback-divergence`, `byte-identity-captured-at-churn`,
  `multihop-expose-offline-parity`, `verify-then-fix-protocol`

---

## Core Concept

**The mental model in three lines.** Aggregation input resolution today is split in two.
`_resolve_aggregation_input_channel` (`graph_builder.py:1212`) resolves *only the channel* —
it returns a channel string or `None`. When it returns `None`, a separate *inline `else:`
block at each of the three call sites* (SumTerm `1453-1493`, SingletonTerm `1562-1608`,
LocalTerm `1650-1666`) builds the entry point. `resolve_input(AGG_STRATEGIES)` does strictly
more: it never returns `None` and owns the channel-vs-entry-point decision itself. So the
cutover is not a function swap — it **moves fallback ownership out of three inline blocks into
one place**, and that place has to reproduce the live entry point exactly.

The key insight that makes this clean: the fallback splits into a **value** and its **side
effects**, and only the value is `resolve_input`'s job.

- The **value** is "channel or entry-point, and if entry-point, which QN." That is pure — it
  depends only on the ref and the registries. It stays in `resolve_input`. The only thing
  wrong with it today is the fallback QN: `resolve_input` mints `{module_eqn}__{leaf}`; every
  live call site mints `{module_eqn}__{ref-with-dots-as-underscores}`. Reconciling the value is
  a one-line key fix (see D1).
- The **side effects** are: look up a literal default, register the `EntryPoint` entity into
  `new_entry_points` with a dedup guard, backfill a default onto an EP created earlier without
  one, classify its param-group, type it `DESIGN_ATTRIBUTE`, and — load-bearing — flip the
  module's `compilability` to `MANUAL_REQUIRED` when a term is unresolved and has no default.
  These need the mutable EP dicts, the `group_deriver`, and `redefinitions`. A pure
  value-returning function cannot own them without becoming a side-effecting god function and
  breaking the very parity contract the cutover's safety net depends on.

So the reconciliation lives in **one new choke-point helper in `graph_builder.py`** —
`_build_agg_input_source(...)` — that wraps `resolve_input` and owns the side effects. The
three inline `else:` blocks collapse into calls to it. `resolve_input` stays pure and
parity-testable. This is the house style: a pure typed resolver, plus a compute-once build
helper that materializes entities. It composes with the pieces already there — the four
`AGG_STRATEGIES`, `_find_literal_redefinition` (`:1326`), `group_deriver.classify`, the
`InputSource`/`EntryPoint` models — and adds no parallel mechanism.

One channel case does not fit a strategy today: SingletonTerm "Try 2" (`:1548-1560`) builds a
channel directly from `instance_path`, and no `AGG_STRATEGY` reproduces it. That is a
channel-half gap, so it becomes a new strategy, not part of the fallback (D3).

---

## Key Bets

- **B1.** Every live call site builds its fallback param name as `ref.replace(".", "_")` —
  SumTerm `{part_usage}_{attr}`, SingletonTerm `source_path.replace(".","_")`, LocalTerm the
  undotted `attr`. So one uniform key rule in `resolve_input` reproduces all three. *If false →
  a per-site key divergence survives the one-line fix and churns the baseline for whichever site
  disagrees.* Mitigated: the three constructions were read directly (`:1442`, `:1533`, `:1652`)
  and all reduce to `ref.replace(".", "_")`.
- **B2.** `resolve_input`'s channel resolution (Strategies A/C/B) plus the new Strategy E is a
  faithful replacement for `_resolve_aggregation_input_channel` on the corpus — including the
  self-reference guard (REQ-IR-03) the old function lacks. *If false → a ref that resolved to a
  channel now falls to entry-point (or vice-versa), churning the baseline.* Mitigated: the M3
  full-`InputSource` gate is designed to catch exactly this before the rewire; the self-ref
  guard only changes behavior for a self-wiring agg input, which the corpus does not contain
  (to be confirmed by the gate).
- **B3.** Strategy E (direct channel construction) is a no-op for SumTerm and LocalTerm refs on
  the corpus — it only returns a channel when the constructed CalcUsage-format channel actually
  exists in `canonical_channels`, which happens for SingletonTerm targets, not array-child costs
  or locals. *If false → adding E to the shared `AGG_STRATEGIES` resolves a SumTerm/LocalTerm ref
  that previously fell to entry-point, churning the baseline.* Mitigated: the M3 gate compares the
  full `InputSource` for SumTerm and SingletonTerm; a red gate triggers the fallback plan (a
  SingletonTerm-only strategy list, D3). **Note the coverage boundary (design-review Major 3):**
  the M3 gate iterates `sum_terms` + `singleton_terms` only — the **LocalTerm expose-alias**
  channel reroute (`:1640`), the one route that newly gains Strategy E *and* the self-ref guard,
  has **no** M3 coverage. It is guarded by (a) the `module_output`-only route guard (D5, Major 2),
  (b) byte-identity on the alias-bearing fixtures, and (c) a dedicated LocalTerm reroute pin run
  before the rewire (see Component Overview, Major 3). Do not claim M3 covers LocalTerm.
- **B4.** The Step-5 `param_groups` computation (`:228`) is dead: its result is discarded by the
  Step-6.6 rebuild (`:331`) and is not read in between. *If false → deleting it drops a
  depended-on value or side effect.* Mitigated: `derive_groups_filtered` writes no instance state
  (read `parameter_groups.py:569-585`), and its `_warn_nonfloat_entry_points` warning fires **only
  at Step 6.6** — via `derive_groups()` (`parameter_groups.py:524`), which `derive_groups_filtered`
  does not reach — so the deleted Step-5 path emits no warning to lose (design-review Note 6).
  Deletion is strictly safe; there is no "asserted twice" worry.

## Key Decisions

- **D1. Reconcile the fallback in one graph_builder helper; keep `resolve_input` pure.**
  `resolve_input`'s fallback QN is fixed to `param_name = ref.replace(".", "_")` (the value
  half). A new `_build_agg_input_source(...)` owns the EP side effects. *Rejected: widening
  `resolve_input` to own registration/compilability (needs the frozen `ResolutionContext` to
  carry mutable EP dicts + `group_deriver` + a compilability channel — it stops being a pure
  resolver and breaks the parity suite's contract, the cutover's own safety net).*
- **D2. The M3 gate is the existing `TestRegression` test extended to compare the full
  `InputSource`, and its new-side assertion SURVIVES the cutover.** `test_input_resolver.py:779`
  already compares old-vs-new but is blind in the fallback branch — it asserts only
  `source_type == "entry_point"`, never the EP `qualified_name` (the L3-1 blind spot, confirmed at
  `:820-825`). The gate has two halves: an **old-comparand** half (calls the deleted
  `_resolve_aggregation_input_channel`) and a **new-side** half
  (`_build_agg_input_source(...).qualified_name == f"{agg.module_eqn}__{ref.replace('.','_')}"`,
  `param_group` included). Only the old-comparand half depends on the deleted function. So at
  cutover, **delete only the old-comparand half and keep the new-side assertion as a permanent
  test** — it needs no deleted function and it is the only thing besides the (regenerable)
  byte-identity baseline that guards the reconciled part-usage EP key (design-review Major 1).
  (`param_group` follows for free: it is `classify(ep_qn)`, deterministic from the QN, so equal
  QNs imply equal groups.) *Rejected: deleting the whole gate at cutover (the review's own
  contradiction — leaves the key guarded by a regenerable baseline alone); comparing `resolve_input`
  alone (its fallback carries no `param_group`, so it is not the full `InputSource` the spec's
  [HARD] M3 requires); a channel-only function-to-function gate (structurally blind to M4).*
- **D3. Add Strategy E `DirectChannelConstruction` to the single shared `AGG_STRATEGIES`.**
  Reproduces SingletonTerm Try 2 as a strategy (the channel half). *Rejected: a separate
  SingletonTerm-only strategy list (more faithful but adds a second constant and contradicts the
  spec's single-`AGG_STRATEGIES` framing) — held as the fallback if the M3 gate reddens for
  SumTerm/LocalTerm.*
- **D4. The typing fix is a loop-variable two-variable split — now evidence-backed (R4
  closed).** The orchestrator ran the reproduction the sandbox blocked. With both ignores removed,
  `mypy` reports exactly: `:408 Incompatible types in assignment (expression has type
  "ParameterGroup", variable has type "DerivedParameterGroup") [assignment]` and `:412
  "ParameterSource" has no attribute "qualified_name" [attr-defined]`. Both chain from the **stale
  loop variable `group`**: it is first bound at `:325` (`for group in raw_groups`, a
  `list[DerivedParameterGroup]`), so at `:408`/`:412` `group` is still typed
  `DerivedParameterGroup` (whose `.parameters` is `list[ParameterSource]`, no `qualified_name`).
  The comment's "typed from its earlier `DerivedParameterGroup` binding" (`:410`) was pointing at
  the loop variable, not `param_groups`. **Fix:** give the `DerivedParameterGroup` loop (`:325`) a
  distinct variable name (e.g. `dg`) so the `ParameterGroup` loops (`:335/:373/:408`) bind a `group`
  cleanly typed `ParameterGroup`; both ignores clear. Baseline `mypy = 104` confirmed at HEAD.
  *Rejected: a root type annotation (epic Risks proved it does not clear the errors — they are a
  loop-variable, not a binding-site, problem); the earlier hypothesis that deleting the Step-5
  binding clears them (the reproduced errors are about `group`, not `param_groups`, so it does
  not).*
- **D4b. Separately, delete the dead Step-5 `param_groups` computation (INFERRED).** The `:228`
  binding is discarded by the Step-6.6 rebuild and never read between (design-review CONFIRMED);
  its only caller makes `_group_entry_points_via_deriver` an orphan. Delete both. This satisfies
  the SC-7 "isolate the discarded Step-5 result" clause; it is dead-code hygiene, **not** what
  clears the ignores (D4 does). *Rejected: keep the call and drop only the binding (the warning
  fires only at Step 6.6, B4 — the Step-5 call is a fully discarded pure computation, so removing
  it outright is cleaner and loses nothing).*
- **D5. LocalTerm keeps its own simpler entry-point fallback; its channel call (`:1640`) is
  rewired with a `source_type == "module_output"` guard.** `resolve_input` never returns `None`
  and keys its fallback on the **alias target** (`alias_source`), not `l_term.attribute_name`. So
  the reroute must take the channel **only** when `resolve_input(alias_source, ...).source_type ==
  "module_output"`, else fall through to LocalTerm's own inline fallback — otherwise LocalTerm's EP
  key diverges and it wrongly inherits literal-lookup/`MANUAL_REQUIRED` semantics (design-review
  Major 2). *Rejected: routing LocalTerm's fallback through `_build_agg_input_source` (gains the
  literal-lookup + `MANUAL_REQUIRED` semantics LocalTerm does not have today — behavior change and
  churn risk; the spec's Open Question says LocalTerm already agrees and must not be "reconciled");
  treating the `resolve_input` result as truthy-channel without the guard (its never-`None`
  fallback would silently rewrite the LocalTerm key).*

---

## Architecture

**Data flow after the cutover, per aggregation term:**

```
SumTerm / SingletonTerm:
  ref ──▶ _build_agg_input_source(ref, ctx, part_usage, attr, *mutable_ep_state)
            └─▶ resolve_input(ref, ctx, AGG_STRATEGIES)     # pure: channel | entry_point value
                  ├─ module_output ──────────────▶ return (InputSource, manual=False)
                  └─ entry_point (ep_qn correct) ─▶ side effects here:
                       _find_literal_redefinition → default
                       register/dedup/backfill EntryPoint (DESIGN_ATTRIBUTE, param_group)
                       manual = (default is None)
                     return (InputSource+param_group, manual)
  call site: if manual: compilability = MANUAL_REQUIRED ; append ModuleInput
             (SumTerm also appends its multiplicity EP — unchanged, inline)

LocalTerm:
  sibling-channel try (unchanged)
    → expose-alias try: resolve_input(alias_source); take producer_channel ONLY IF
      source_type == "module_output" (D5 guard) — else fall through
    → simpler inline entry_point fallback, keyed {module_eqn}__{attribute_name} (unchanged, D5)
```

**Boundaries:**
- `input_resolver.py` — pure resolution layer. Change: one-line fallback key fix; add Strategy
  E; delete Strategy D + its docstring; drop D from `AGG_STRATEGIES`.
- `graph_builder.py` — orchestration + entity materialization. Change: add
  `_build_agg_input_source`; collapse the SumTerm/SingletonTerm inline blocks into it; rewire
  LocalTerm's channel call with the `module_output`-only guard (D5); delete
  `_resolve_aggregation_input_channel` (def + `__all__:1925`); rename the `:325`
  `DerivedParameterGroup` loop variable to clear the two `param_groups` ignores (D4); delete the
  dead Step-5 call + orphan `_group_entry_points_via_deriver` (D4b).
- Tests — `test_input_resolver.py::TestRegression` becomes the M3 gate; its new-side assertion
  survives permanently, only the old-comparand half is deleted at cutover (D2, Major 1); add a
  LocalTerm expose-alias reroute pin (Major 3); `test_graph_builder_aggregation.py` (~11 direct
  calls to the deleted function) migrates to `resolve_input`/strategies or is deleted.

## Required Invariants

- **INV-1.** After the cutover, `resolve_input`'s fallback and every reconciled call site mint
  the identical EP QN `{module_eqn}__{ref.replace('.','_')}` — no input EP collides with an
  output channel, no part-usage disambiguator is dropped (probe iv).
- **INV-2.** A genuinely-unresolved aggregation term with no literal default still flips the
  module to `Compilability.MANUAL_REQUIRED`. The signal is never lost in the move (L3-2).
- **INV-3.** The M3 full-`InputSource` gate (source_type, producer_channel, qualified_name) is
  green **before** the call-site rewire lands.
- **INV-4.** Aggregation baseline is **byte-identical** post-cutover. Any aggregation diff blocks
  the cutover pending root-cause (not a reviewed-and-accepted diff). Every non-aggregation
  baseline and aggregation-bearing snapshot fixture is byte-identical (R3).
- **INV-5.** `resolve_input` stays a pure function of `(ref, ctx, strategies)`; no strategy and
  not `resolve_input` mutates `ResolutionContext` or any EP registry.
- **INV-6.** Gates: full suite green; `mypy src/` ≤ 104; `ruff check src/` ≤ 17; both
  `param_groups` `type: ignore`s (`:408`, `:412`) cleared.
- **INV-7.** The helper builds `ctx` with `module_eqn = agg.module_eqn`. `resolve_input` mints the
  fallback QN from `ctx.module_eqn` (`input_resolver.py:271`) while the call sites use
  `agg.module_eqn` (`:1467`, `:1581`); the key only matches if they are the same. If `ctx` is wired
  with any other `module_eqn`, **every** fallback key shifts silently (design-review Note 5).

## Component Overview

- **`_build_agg_input_source` (new, `graph_builder.py`).** The reconciliation choke point.
  Input: `ref`, `ctx` (built with `module_eqn = agg.module_eqn`, INV-7), the literal-lookup keys,
  `redefinitions`, `usage_type_map`, `owning_part_qn`, `group_deriver`, and the
  `entry_points`/`new_entry_points` dicts. Wraps `resolve_input`; on an entry_point result, owns
  literal-default lookup, register/dedup/backfill, param-group, `DESIGN_ATTRIBUTE` typing. Returns
  `(InputSource, manual_required: bool)`. Reproduces `graph_builder.py:1453-1493` / `:1562-1608`
  byte-for-byte in behavior. **It must absorb both literal-lookup shapes (design-review Minor 4):**
  SumTerm looks up from pre-split fields (`term.part_usage_name`, `term.attribute_name`); a
  SingletonTerm guards the lookup on `"." in source_path` and skips it when dotless
  (`literal_default` stays `None`). The interface takes an optional split (`part_usage`/`attr` or
  "no split → skip lookup"), so the dotless SingletonTerm does not regress.
- **`resolve_input` fallback fix (`input_resolver.py:270`).** `param_name = ref.rsplit(".",1)[-1]`
  → `ref.replace(".", "_")`. The only value-half change.
- **Strategy E `DirectChannelConstruction` (new, `input_resolver.py`).** For dotted refs, builds
  `get_channel_name(f"{instance_path}__{prefix.replace('.','__')}", output)` and returns it iff
  in `canonical_channels`. Appended after A/C/B in `AGG_STRATEGIES`. Reproduces Try 2 (`:1548`);
  in-idiom with `ChainRedefinitionFollow`'s existing `{instance_path}__…` construction (`:184-188`).
- **M3 gate (`test_input_resolver.py::TestRegression`).** Extended so "new" is the helper's full
  `InputSource` and the fallback branch asserts `qualified_name`. **Two halves with different
  fates (Major 1):** the old-comparand half (calls the deleted function) is removed at cutover; the
  **new-side assertion survives as a permanent test** — the durable guard on the reconciled EP key.
- **LocalTerm expose-alias reroute pin (new test, Major 3).** The `:1640` reroute has no M3
  coverage. Add a small pin, green **before** the rewire, over the alias-bearing fixtures
  (`alias_agg_probe`, `solar_battery`): assert `resolve_input(alias_source, ...)` yields the same
  `producer_channel` the old function did when a channel exists, and that a non-channel result
  leaves the LocalTerm EP key at `{module_eqn}__{attribute_name}` (D5 guard holds). Byte-identity
  is the backstop, not the sole guard.
- **param_groups typing fix (`graph_builder.py:325`, `:408`, `:412`).** Rename the `:325`
  `DerivedParameterGroup` loop variable (to `dg`) so the `ParameterGroup` loops bind cleanly; both
  ignores clear (D4). Separately delete the dead Step-5 call (`:228-233`) + orphan
  `_group_entry_points_via_deriver` (`:534-566`) (D4b).

## Non-Goals

- Strategy D as a capability (delete-only; probe ii proved zero surface).
- Multi-hop chain resolution (Item 2) — adjacent chain-follow code, sequenced after.
- Any ComputationGraph schema change beyond the EP-key reconciliation the cutover forces.
- Reworking the 22 `test_input_resolver.py` skipifs, Strategy B, or the parity suite — they test
  correct code and gain a live consumer; they are not rewritten.

## Implementation Notes

- **R4 — mypy error REPRODUCED (contingency closed).** The orchestrator ran the reproduction the
  sandbox blocked. With both ignores removed, `mypy` reports exactly two errors:
  `:408 Incompatible types in assignment (expression has type "ParameterGroup", variable has type
  "DerivedParameterGroup") [assignment]` and `:412 "ParameterSource" has no attribute
  "qualified_name" [attr-defined]`; baseline `mypy = 104` at HEAD. Root cause: the loop variable
  `group` is first bound at `:325` (`for group in raw_groups`, `list[DerivedParameterGroup]`) and
  stays typed `DerivedParameterGroup` at `:408`/`:412`. The `:410` comment named the wrong
  variable (the loop var, not `param_groups`). **Fix (D4): rename the `:325` loop variable** so the
  `ParameterGroup` loops bind a clean `group`; both ignores clear. This is the two-variable split
  the epic anticipated, now evidence-backed — not contingent. Re-confirm `mypy ≤ 104` live after
  the rename.
- **The MANUAL_REQUIRED signal is the load-bearing side effect (L3-2).** `resolve_input` returns
  a value and cannot set the module's `compilability`. `_build_agg_input_source` must return the
  `manual_required` flag and each SumTerm/SingletonTerm call site must apply it. Losing it
  silently marks an unresolved term compilable → wrong auto-impl — the exact regression class this
  epic kills.
- **Sequencing (green-before-rewire).** (1) Fix `resolve_input` key + add Strategy E + write
  `_build_agg_input_source`, no call-site rewire yet. (2) Extend the M3 gate (full-`InputSource`)
  and add the LocalTerm expose-alias reroute pin; run both green. (3) Rewire the three call sites
  (LocalTerm with the `module_output`-only guard, D5); delete the inline blocks + the old function
  + Strategy D. (4) Re-capture baselines; assert byte-identity. (5) Delete only the M3 gate's
  old-comparand half (the new-side assertion stays permanent, Major 1); apply the param_groups
  loop-variable rename (D4) + delete the dead Step-5 call (D4b). (6) R1 docs + matrix in the same
  change.
- **Test-surgery tail the spec under-counted.** Deleting `_resolve_aggregation_input_channel`
  breaks ~11 direct-call tests in `tests/unit/test_graph_builder_aggregation.py` (`:107-247`,
  `:364`) and the `TestRegression` old-function call. Migrate the still-meaningful cases to
  `resolve_input(ref, ctx, AGG_STRATEGIES)` assertions, or delete cases already covered by
  `test_dual_resolution.py`. Budget this as real work, not a line delete.
- **Baseline scope (Design Problem 5).** All 10 `tests/fixtures/baseline_outputs/*` are in the
  byte-identity gate — the gate boundary, not a targeting hint, so any un-anticipated divergent
  baseline still surfaces as a diff. `solar_battery` is the **only** baseline carrying the divergent
  part-usage-prefixed agg EP construction: the orchestrator corroborated that `raw_material_cost`
  appears only under `baseline_outputs/solar_battery` (plus `baseline_yaml` and the model source),
  no other baseline carries the named key. It is the reconciliation's direct target.
  Aggregation-bearing snapshot fixtures (`solar_battery_model`, `alias_agg_probe`,
  `agg_literal_probe`, `ep_key_collision_probe`) and the `test_dual_resolution` fixtures
  (`plant_values`, `plant_value_shapes`, `spec_chain_twolevel`) exercise the reconciled path.
  Include any snapshot-generation baseline that carries aggregation EP construction (memory:
  `multihop-expose-offline-parity`). Use the timestamp-churn byte-identity method (memory:
  `byte-identity-captured-at-churn`): a full re-capture rewrites every `captured_at`; diff, confirm
  only `captured_at` churned on untouched fixtures, revert those so only the intended change shows.

## Potential Risks

- **Strategy E churns SumTerm/LocalTerm (B3 false).** *Mitigation:* the M3 full-`InputSource`
  gate catches it pre-rewire; fallback is the SingletonTerm-only strategy list (D3).
- **The self-reference guard changes a channel result (B2).** The old function has no self-ref
  guard; `resolve_input` does. *Mitigation:* the M3 gate compares the channel branch too; a
  divergence is a diff to root-cause, and a self-wiring agg input would be a latent bug the guard
  correctly fixes — root-cause before accepting.
- **LocalTerm's expose-alias channel now routes through `resolve_input` (Strategy E + self-ref
  guard) instead of the old function, and has no M3 coverage.** *Mitigation:* the D5
  `module_output`-only route guard keeps the fallback key unchanged; a dedicated reroute pin (Major
  3) runs green before the rewire; byte-identity on `alias_agg_probe`/`solar_battery` is the
  backstop.
- **Deleting Step-5 loses a needed value or warning (B4).** *Mitigation:* the result is discarded
  and the non-float warning fires only at Step 6.6 (design-review confirmed), so there is nothing
  to lose; a quick `caplog`/`_warn_nonfloat` grep at implement is a cheap final check.
- **The loop-variable rename does not clear the ignores.** *Mitigation:* the error is reproduced
  and traced to the `:325` loop variable (R4 closed); re-confirm `mypy ≤ 104` live after the
  rename. Low residual risk.

## Integration Strategy

The cutover replaces the inline aggregation-resolution path with the consolidated module that
PIPELINE-TRUTH built and parity-validated. The M3 gate has **two halves with different fates**
(Major 1): the **old-comparand** half proves the reconciled fallback reproduces the *executed* old
block before the live path is touched, then it is deleted in the cutover commit (it cannot compile
against the deleted `_resolve_aggregation_input_channel`); the **new-side** assertion
(`_build_agg_input_source(...).qualified_name == formula`) has no dependency on the deleted function
and **survives as a permanent test** — the durable guard on the reconciled part-usage EP key, which
a regenerable byte-identity baseline alone would not provide. The rest of the permanent safety net
is the committed `test_dual_resolution.py` parity suite plus the byte-identical baselines. R1
requires the IR-family matrix rows (drop the "not-yet-wired" note), REQ text, and reference docs
03/04/05/24 to move in the same change that wires the path.

## Validation Approach

- **M3 gate green before rewire** (INV-3): full `InputSource` parity over the SumTerm/SingletonTerm
  aggregation fixtures, fallback branch included; the new-side assertion survives permanently.
- **LocalTerm reroute pin green before rewire** (Major 3): expose-alias channel parity + the D5
  `module_output`-only guard, over `alias_agg_probe`/`solar_battery`.
- **Byte-identity** (INV-4): re-capture all baselines one at a time; aggregation byte-identical
  or blocked pending root-cause; non-aggregation + snapshot fixtures byte-identical via the
  timestamp-churn method.
- **MANUAL_REQUIRED preserved** (INV-2): a targeted test that an unresolved no-default agg term
  yields `MANUAL_REQUIRED` through the new helper.
- **Gates** (INV-6): full suite green; `mypy ≤ 104`, `ruff ≤ 17`, both ignores cleared —
  re-confirmed live at implement.
- **Strategy D gone:** not in `AGG_STRATEGIES`, function + docstring deleted.

## Next-Stage Handoff

- **Fixed:** reconciliation lives in a graph_builder choke-point helper, `resolve_input` stays
  pure (D1); the M3 gate's new-side assertion survives permanently, only the old-comparand half is
  deleted (D2, Major 1); Try 2 becomes Strategy E in the shared list (D3); the typing fix is the
  `:325` loop-variable rename, evidence-backed (D4), with the dead Step-5 deletion separate (D4b);
  LocalTerm keeps its simpler fallback and its reroute takes the channel only when
  `module_output` (D5, Major 2); byte-identity is the hard aggregation bar; the helper absorbs the
  dotless-SingletonTerm case and `ctx.module_eqn = agg.module_eqn` is INV-7.
- **Open at implement:** the precise migration of the ~11 `test_graph_builder_aggregation.py`
  direct-call tests; the exact shape of the LocalTerm reroute pin; a final `caplog`/`_warn_nonfloat`
  grep before deleting Step-5.
- **De-risk first:** get the M3 gate **and** the LocalTerm reroute pin green **before** any
  call-site rewire; re-confirm `mypy = 104` / `ruff = 17` live, then apply the loop-variable rename
  and re-confirm `mypy ≤ 104`.

---
Next Step: After approval → `/_my_plan` or `/_my_implement`.
