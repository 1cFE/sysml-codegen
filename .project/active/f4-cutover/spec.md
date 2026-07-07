# Spec: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT, Item 1 (SC-A, SC-G)

---

## Problem

The generated pipeline resolves aggregation inputs (SumTerm / SingletonTerm / LocalTerm-EXPOSE)
through an inline function, `_resolve_aggregation_input_channel` (`graph_builder.py:1212`). A
consolidated replacement, `resolve_input(AGG_STRATEGIES)` (`input_resolver.py`), was built and
parity-validated during PIPELINE-TRUTH but **never wired to the live path**. That left three
pieces of standing debt:

1. **The IR matrix family lies by omission.** REQ-IR rows now describe `resolve_input` as a
   "parity-validated, not-yet-wired consolidation" — honest, but it means an entire requirement
   family pins code the pipeline never calls. The matrix and the code will only fully agree once
   the live path runs through the module.

2. **A naive drop-in silently corrupts the aggregation baseline.** `resolve_input`'s fallback
   mints a leaf-only entry-point key (`{module_eqn}__{leaf}`) where the live path builds a
   part-usage-prefixed key (`{module_eqn}__{part_usage}_{attr}`). The leaf-only string
   **already coexists in the same graph as the module's own output channel**
   (`tests/fixtures/baseline_outputs/solar_battery/computation_graph.json:2472/2483/3270/3486`,
   captured in `probes/probe_iv_ep_key_divergence.md`). Wiring without first reconciling the
   fallback collides an input entry point with an output channel and drops the disambiguator that
   keeps sibling part-usage inputs distinct. This is the load-bearing blocker (design-review M4).

3. **Two dead/co-located debts sit in the same region.** Strategy D (`DesignAttributeLookup`,
   `input_resolver.py:200`) is a `return None` stub with a docstring that claims it is "included
   in AGG_STRATEGIES for future extensibility" — probe (ii) proved it has zero live surface.
   And `param_groups` in `build_computation_graph` is bound twice (`graph_builder.py:228` then
   rebound at `:331`), guarded by two `type: ignore`s at `:408`/`:412`.

This item is the critical-path head of TRUTH-DEBT: it churns the aggregation baseline (R3), and
Item 2's multi-hop chain work edits adjacent chain-follow code, so it lands **first**.

## Success Criteria

- [ ] The live aggregation path calls `resolve_input(AGG_STRATEGIES)`;
  `_resolve_aggregation_input_channel` is deleted (def + the `__all__` export at `:1925`).
- [ ] Before rewiring, `resolve_input`'s entry-point fallback is reconciled to the live path's
  richer entry-point construction, so no input entry point collides with an output channel and
  no part-usage disambiguator is dropped (the M4 blocker is resolved, not worked around).
- [ ] A parity gate compares `resolve_input(AGG_STRATEGIES)` against **the replaced function
  `_resolve_aggregation_input_channel`** (not only the backtracker DFS), runs in CI, and is green
  — added and green **before** the rewire (design-review M3).
- [ ] Aggregation baselines are byte-identical after the cutover, OR land as one reviewed
  `scripts/capture_*.py` diff; every non-aggregation baseline is byte-identical (R3). A
  non-byte-identical aggregation diff is a signal the fallback reconciliation is incomplete —
  it is reviewed, not rubber-stamped.
- [ ] Strategy D is removed from `AGG_STRATEGIES`, its function deleted, and its lying docstring
  gone (the residual ghost Item 7 left noted).
- [ ] The IR-family matrix rows drop the "not-yet-wired" note and pin live code; REQ text +
  reference docs 03/04/05 + `24-dual-resolution-architecture.md` move in the same change (R1).
- [ ] `param_groups` double-binding is split into two distinctly-named variables (the Step-5
  computation removed if confirmed dead); both `type: ignore`s at `:408`/`:412` are cleared.
- [ ] Gates hold: full suite green; `mypy src/` ≤ 104; `ruff check src/` ≤ 17.

## Known Requirements

- **[HARD]** **Reconcile the fallback before rewiring (M4).** The live call sites build the
  SumTerm/SingletonTerm entry point with the part-usage-prefixed QN plus
  `_find_literal_redefinition` default propagation, `param_group` classification,
  `DESIGN_ATTRIBUTE` typing, multiplicity entry points, and the SingletonTerm "Try 2"
  direct-channel construction. `resolve_input`'s fallback emits a bare `{module_eqn}__{leaf}`.
  The reconciliation must make the module produce the live path's richer entry point so the
  baseline does not churn. Forced by the coexisting-key evidence in `probe_iv_ep_key_divergence.md`.

- **[HARD]** **Parity gate against the replaced function (M3).** The cutover's own safety net
  must compare `resolve_input(AGG_STRATEGIES)` against `_resolve_aggregation_input_channel`
  directly. Backtracker parity (probe (i), the committed `TestResolveInputParityExtended`) is
  general-correctness evidence, not parity-with-the-replaced-function. This gate lands and is
  green before the rewire, and captures the replaced function before it is deleted.

- **[HARD]** **R3 baseline discipline.** All baseline/snapshot regeneration runs through
  `scripts/capture_*.py` with reviewed diffs; one regen at a time; the byte-identity gate proves
  non-aggregation baselines are untouched (timestamp-churn method: memory note
  `byte-identity-captured-at-churn`). The syside license is on monthly renewal — no expiry pressure.

- **[HARD]** **R4 verify-then-fix, applied to two filed reads.** A filed line number is a
  static-read verdict until reproduced at pickup:
  - **Call sites.** Filed as `graph_builder.py:1444/1539/1640` (filing) vs `:1437/1532/1633`
    (design). Spec-time re-read confirms the current call sites are **1444 / 1539 / 1640** and the
    def is at **1212**; implement must re-verify again before editing, since baseline/typing edits
    in this same item shift line numbers.
  - **The typing cause.** The `type: ignore` comment (`graph_builder.py:409-411`) claims
    `param_groups` "is typed from its earlier `DerivedParameterGroup` binding." Spec-time read
    shows **both** `_group_entry_points_via_deriver` (Step 5) and `_convert_derived_groups`
    (Step 6.6) are annotated `-> list[ParameterGroup]` — the same type — so the stated cause looks
    stale. Reproduce the actual mypy error (capture the exact message) before choosing the split;
    do not fix against the comment's account of the cause.

- **[HARD]** **Gate ceilings (no regression).** `mypy src/` ≤ 104; `ruff check src/` ≤ 17; full
  suite green. Current baseline is exactly 104 / 17 (PIPELINE-TRUTH close gate). Clearing the two
  ignores must not raise mypy above 104 — a root annotation was proven not to clear it, so the
  fix is the two-named-variable split, not a re-annotation (epic Risks table).

- **[HARD]** **R1 docs-move-with-code.** The IR-family rows (REQ-IR-01..07, with IR-05/IR-07
  carrying the false live-usage text Item 7 rewrote to capability claims), the reframed
  RES/DRA/BT rows, and reference docs 03/04/05 + 24 are updated in the same change that wires the
  path — no reader inherits either the old "not-yet-wired" note or a re-lie. Recount the matrix
  from rows, not the summary block.

- **[INFERRED]** **Delete Strategy D, do not implement it.** Probe (ii) settled this: zero key
  churn on catf_mfe/solar_battery, no trigger co-occurrence, and the function is a `return None`
  stub. The epic and BACKLOG both say delete. Tagged INFERRED only because "delete vs implement"
  was a live fork the evidence closed.

- **[INFERRED]** **Remove the Step-5 `param_groups` computation only if confirmed dead.** Line
  228's binding is discarded by the Step-6.6 rebuild at line 331 and is not read in between. But
  `_group_entry_points_via_deriver` calls `group_deriver.derive_groups_filtered(...)`; before
  deleting the call (vs just dropping the binding), verify it has no side effect the later
  `derive_groups()` at line 324 depends on. If side-effecting, keep the call and drop only the
  binding.

- **[INFERRED]** **Keep the module's existing correct code.** The 22 `test_input_resolver.py`
  skipifs, Strategy B (`SysMLQNLookup`), and the committed parity suite test real, correct code —
  they stay. The cutover gives them a live consumer; it does not rewrite them.

## Non-Goals

- Strategy D as a *new* capability — implement-or-delete only, and probe (ii) chose delete.
- Any ComputationGraph schema revision beyond the entry-point-key reconciliation the cutover
  forces.
- The multi-hop chain resolution path (TRUTH-DEBT Item 2) — adjacent chain-follow code, sequenced
  after this item so baseline churn and adjacent edits do not overlap.
- The matrix test-gap authoring, classifier fix, sweep residue, and hygiene tail (Items 3–6).

## Open Questions / Deferred to design

- **Where the reconciliation lives.** Either move the live path's richer entry-point construction
  into `resolve_input`'s fallback, or have the call sites pass the extra context so the module
  builds the same key. The design picks the cleaner choke point; the [HARD] outcome (no
  collision, no dropped disambiguator, byte-identical baseline) is fixed, the mechanism is not.

- **The shape of the M3 parity gate.** Whether it is a new conformance test parametrized over the
  aggregation fixtures, or an extension of `test_dual_resolution.py`, and how it captures the
  replaced function's output before deletion (snapshot the values, or run both functions
  side-by-side in the test). Design decides.

- **Whether reconciling the fallback shifts any entry point the multiplicity/param-group logic
  classifies.** If the richer construction is reproduced faithfully, baselines stay byte-identical
  and this is moot; if design finds an unavoidable, reviewed diff, it names the exact rows in the
  capture diff. Surfaced here so implement does not treat a diff as automatically benign.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 1; R1–R4; Risks; SC-A, SC-G)
- **Parent epic (R1–R4 full text):** `.project/backlog/epic_pipeline_truth.md`
- **Required Reading:**
  - `.project/active/matrix-truth/design.md` + `design-review.md` (the F4 LAND-with-split verdict;
    M3 comparand, M4 EP-key blocker)
  - `.project/active/matrix-truth/probes/` — `probe_i_extended_parity.py` (+ run log),
    `probe_ii_strategy_d_dedup.py` (+ run log), `probe_iii_module_drift.md`,
    `probe_iv_ep_key_divergence.md`
  - BACKLOG `[ITEM7-F4-CUTOVER]` and `[GB-PARAMGROUPS-TYPING]` (`.project/backlog/BACKLOG.md`)
  - `docs/architecture/reference/03-resolution-overview.md`, `04-input-resolver.md`,
    `05-module-factory.md`, `07-graph-assembly.md`, `24-dual-resolution-architecture.md`
- **Memory notes:** `f4-cutover-fallback-divergence`, `byte-identity-captured-at-churn`,
  `verify-then-fix-protocol`, `verification-matrix-drift-modes`
- **Design:** `.project/active/f4-cutover/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
