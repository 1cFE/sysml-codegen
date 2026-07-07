# Design: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** truth-debt-epic
**Commit:** a32ae45
**Epic:** TRUTH-DEBT, Item 1 (SC-A, SC-G)

## Overview

Wire the live aggregation path through `resolve_input(AGG_STRATEGIES)`, delete the
channel-only `_resolve_aggregation_input_channel` and the three inline entry-point
fallbacks, and reconcile the fallback so the baseline stays byte-identical. Fold in the
`param_groups` bind-mutate typing cleanup.

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
  that previously fell to entry-point, churning the baseline.* Mitigated: the M3 gate compares
  the full `InputSource` for all three term types; a red gate triggers the fallback plan (a
  SingletonTerm-only strategy list, D3).
- **B4.** The Step-5 `param_groups` computation (`:228`) is dead: its result is discarded by the
  Step-6.6 rebuild (`:331`), and its only side effect (`_warn_nonfloat_entry_points` logging)
  fires again independently at Step 6.6. *If false → deleting it drops a depended-on side effect
  or a warning a test asserts.* Mitigated: `derive_groups_filtered` writes no instance state
  (read `parameter_groups.py:569-585`); verify at implement that no `caplog` test asserts the
  non-float warning fires twice.

## Key Decisions

- **D1. Reconcile the fallback in one graph_builder helper; keep `resolve_input` pure.**
  `resolve_input`'s fallback QN is fixed to `param_name = ref.replace(".", "_")` (the value
  half). A new `_build_agg_input_source(...)` owns the EP side effects. *Rejected: widening
  `resolve_input` to own registration/compilability (needs the frozen `ResolutionContext` to
  carry mutable EP dicts + `group_deriver` + a compilability channel — it stops being a pure
  resolver and breaks the parity suite's contract, the cutover's own safety net).*
- **D2. The M3 gate is the existing `TestRegression` test extended to compare the full
  `InputSource`.** `test_input_resolver.py:779` already compares old-vs-new but is blind in the
  fallback branch — it asserts only `source_type == "entry_point"`, never the EP `qualified_name`
  (the L3-1 blind spot, confirmed at `:820-825`). Extend that branch so "new" is the
  **`_build_agg_input_source` result** (the full `InputSource` the call-site block produces,
  `param_group` included), and "old" replicates the inline block's `InputSource` — the
  load-bearing assertion being `qualified_name == f"{agg.module_eqn}__{ref.replace('.','_')}"`.
  (`param_group` follows for free: it is `classify(ep_qn)`, deterministic from the QN, so equal
  QNs imply equal groups.) *Rejected: comparing `resolve_input` alone (its fallback carries no
  `param_group`, so it is not the full `InputSource` the spec's [HARD] M3 requires); a new
  parametrized conformance test (duplicates scaffolding this test already has); a channel-only
  function-to-function gate (structurally blind to M4).*
- **D3. Add Strategy E `DirectChannelConstruction` to the single shared `AGG_STRATEGIES`.**
  Reproduces SingletonTerm Try 2 as a strategy (the channel half). *Rejected: a separate
  SingletonTerm-only strategy list (more faithful but adds a second constant and contradicts the
  spec's single-`AGG_STRATEGIES` framing) — held as the fallback if the M3 gate reddens for
  SumTerm/LocalTerm.*
- **D4. Delete the Step-5 `param_groups` call outright (not just its binding), making Step 6.6
  the sole binding site.** Also deletes the now-orphan `_group_entry_points_via_deriver` (its
  only caller was `:228`). *Rejected: drop the binding but keep the call (`derive_groups_filtered`
  has no depended-on side effect, so keeping a discarded pure computation only to re-emit a
  duplicate warning is worse); a root type annotation (epic Risks proved it does not clear the
  ignores).* **Contingent on R4:** reproduce the actual mypy error first (see Implementation
  Notes — I could not run mypy in this sandbox).
- **D5. LocalTerm keeps its own simpler entry-point fallback; only its channel call (`:1640`) is
  rewired.** *Rejected: routing LocalTerm's fallback through `_build_agg_input_source` (it would
  gain the literal-lookup + `MANUAL_REQUIRED` semantics LocalTerm does not have today — a
  behavior change and churn risk; the spec's own Open Question says LocalTerm already agrees and
  must not be "reconciled").*

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
  sibling-channel try (unchanged) → expose-alias try (channel via resolve_input) →
  simpler inline entry_point fallback (unchanged, D5)
```

**Boundaries:**
- `input_resolver.py` — pure resolution layer. Change: one-line fallback key fix; add Strategy
  E; delete Strategy D + its docstring; drop D from `AGG_STRATEGIES`.
- `graph_builder.py` — orchestration + entity materialization. Change: add
  `_build_agg_input_source`; collapse the SumTerm/SingletonTerm inline blocks into it; rewire
  LocalTerm's channel call; delete `_resolve_aggregation_input_channel` (def + `__all__:1925`);
  delete Step-5 call + `_group_entry_points_via_deriver`; clear the two `param_groups` ignores.
- Tests — `test_input_resolver.py::TestRegression` becomes the M3 gate (extended, then its
  old-function dependency removed post-cutover); `test_graph_builder_aggregation.py` (~11 direct
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

## Component Overview

- **`_build_agg_input_source` (new, `graph_builder.py`).** The reconciliation choke point.
  Input: `ref`, `ctx`, the split `part_usage`/`attr`, `redefinitions`, `usage_type_map`,
  `owning_part_qn`, `group_deriver`, and the `entry_points`/`new_entry_points` dicts. Wraps
  `resolve_input`; on an entry_point result, owns literal-default lookup, register/dedup/backfill,
  param-group, `DESIGN_ATTRIBUTE` typing. Returns `(InputSource, manual_required: bool)`.
  Reproduces `graph_builder.py:1453-1493` / `:1562-1608` byte-for-byte in behavior.
- **`resolve_input` fallback fix (`input_resolver.py:270`).** `param_name = ref.rsplit(".",1)[-1]`
  → `ref.replace(".", "_")`. The only value-half change.
- **Strategy E `DirectChannelConstruction` (new, `input_resolver.py`).** For dotted refs, builds
  `get_channel_name(f"{instance_path}__{prefix.replace('.','__')}", output)` and returns it iff
  in `canonical_channels`. Appended after A/C/B in `AGG_STRATEGIES`. Reproduces Try 2 (`:1548`).
- **M3 gate (`test_input_resolver.py::TestRegression`).** Extended so "new" is the helper's full
  `InputSource` and the fallback branch asserts `qualified_name`. Transitional — deleted
  post-cutover (D2, Integration Strategy).
- **param_groups typing fix (`graph_builder.py:228-233`, `:408-412`, `:534-566`).** Delete the
  Step-5 call and the orphan helper; Step 6.6 becomes the sole binding; clear both ignores.

## Non-Goals

- Strategy D as a capability (delete-only; probe ii proved zero surface).
- Multi-hop chain resolution (Item 2) — adjacent chain-follow code, sequenced after.
- Any ComputationGraph schema change beyond the EP-key reconciliation the cutover forces.
- Reworking the 22 `test_input_resolver.py` skipifs, Strategy B, or the parity suite — they test
  correct code and gain a live consumer; they are not rewritten.

## Implementation Notes

- **R4 — reproduce the mypy error first (blocked in this sandbox).** `mypy`/`ruff` are
  approval-gated here; I could not run them. Static read is conclusive on the *cause*: the ignore
  comment (`:409-411`) claims `param_groups` "is typed from its earlier `DerivedParameterGroup`
  binding," but **both** producers (`_group_entry_points_via_deriver` `:539`, `_convert_derived_groups`
  `:572`) return `list[ParameterGroup]`, and `ParameterGroup.parameters: list[EntryPoint]` with
  `EntryPoint.qualified_name` — so the stated cause is stale and `.parameters.sort(...)` should
  type-check. At implement: remove both ignores, run `uv run mypy src/`, capture the exact
  error+code. Then apply D4 (delete Step-5 → single binding site) and re-run. If the reproduced
  error shows the ignores were merely unused, deleting them is the whole fix. Do not commit the
  fix against the comment's account (R4).
- **The MANUAL_REQUIRED signal is the load-bearing side effect (L3-2).** `resolve_input` returns
  a value and cannot set the module's `compilability`. `_build_agg_input_source` must return the
  `manual_required` flag and each SumTerm/SingletonTerm call site must apply it. Losing it
  silently marks an unresolved term compilable → wrong auto-impl — the exact regression class this
  epic kills.
- **Sequencing (green-before-rewire).** (1) Fix `resolve_input` key + add Strategy E + write
  `_build_agg_input_source`, no call-site rewire yet. (2) Extend the M3 gate; run it green. (3)
  Rewire the three call sites; delete the inline blocks + the old function + Strategy D. (4)
  Re-capture baselines; assert byte-identity. (5) Remove the M3 gate's old-function dependency;
  do the param_groups fix. (6) R1 docs + matrix in the same change.
- **Test-surgery tail the spec under-counted.** Deleting `_resolve_aggregation_input_channel`
  breaks ~11 direct-call tests in `tests/unit/test_graph_builder_aggregation.py` (`:107-247`,
  `:364`) and the `TestRegression` old-function call. Migrate the still-meaningful cases to
  `resolve_input(ref, ctx, AGG_STRATEGIES)` assertions, or delete cases already covered by
  `test_dual_resolution.py`. Budget this as real work, not a line delete.
- **Baseline scope (Design Problem 5).** All 10 `tests/fixtures/baseline_outputs/*` are in the
  byte-identity gate. `solar_battery` is the **only** baseline carrying the divergent
  part-usage-prefixed agg EP construction (grep-confirmed) — the reconciliation's direct target.
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
  guard) instead of the old function.** *Mitigation:* covered by byte-identity on the
  alias-bearing fixtures (`alias_agg_probe`, `solar_battery`).
- **Deleting Step-5 drops a warning a test asserts (B4).** *Mitigation:* grep `caplog`/
  `_warn_nonfloat` in tests before deleting; if asserted-twice, keep the call and drop only the
  binding (D4's rejected alternative).
- **The mypy fix does not clear the ignores as predicted.** *Mitigation:* R4 reproduce-first; the
  fix is contingent on the captured error, not this design's static hypothesis.

## Integration Strategy

The cutover replaces the inline aggregation-resolution path with the consolidated module that
PIPELINE-TRUTH built and parity-validated. The M3 gate is **transitional scaffolding**: it exists
to prove the reconciled fallback reproduces the old `InputSource` before the live path is touched,
then its dependency on the deleted `_resolve_aggregation_input_channel` is removed in the same
cutover commit — **deleted, not retired-in-place**, because it cannot compile against a deleted
function. The permanent safety net is the committed `test_dual_resolution.py` parity suite plus the
byte-identical baselines. R1 requires the IR-family matrix rows (drop the "not-yet-wired" note),
REQ text, and reference docs 03/04/05/24 to move in the same change that wires the path.

## Validation Approach

- **M3 gate green before rewire** (INV-3): full `InputSource` parity over the aggregation
  fixtures, fallback branch included.
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
  pure (D1); the M3 gate is the extended `TestRegression`, deleted post-cutover (D2); Try 2
  becomes Strategy E in the shared list (D3); Step-5 deletion is the typing approach (D4);
  LocalTerm keeps its simpler fallback (D5); byte-identity is the hard aggregation bar.
- **Open at implement:** the exact mypy error and whether D4 clears both ignores (R4 —
  reproduce first, this sandbox could not); the precise migration of the ~11
  `test_graph_builder_aggregation.py` direct-call tests; whether any `caplog` test pins the
  non-float warning count.
- **De-risk first:** re-run mypy/ruff live to confirm the 104/17 baseline and reproduce the
  ignore error **before** writing the typing fix; then get the M3 gate green **before** any
  call-site rewire.

---
Next Step: After approval → `/_my_plan` or `/_my_implement`.
