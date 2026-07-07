# Spec: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Status:** Draft (revised post spec-review, 2026-07-06 — all findings incorporated)
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT, Item 1 (SC-A, SC-G)

---

## Problem

**The shape in two lines.** Aggregation input resolution today has two halves that live in two
places. `_resolve_aggregation_input_channel` (`graph_builder.py:1212`) resolves **only the
channel** — it returns a channel string or `None`. When it returns `None`, a separate **inline
`else:` fallback at each of the three call sites** (`1453-1493` SumTerm, `1562-1608`
SingletonTerm, `1650-1666` LocalTerm) builds the entry point. The consolidated replacement,
`resolve_input(AGG_STRATEGIES)` (`input_resolver.py`), does **strictly more** than the deleted
function: it never returns `None` and owns the fallback itself. So the cutover is not a
function swap — it **moves fallback ownership into `resolve_input` and deletes the three inline
`else:` blocks**. That asymmetry is exactly why the entry-point keys must be reconciled first
(the M4 blocker below).

`resolve_input(AGG_STRATEGIES)` was built and parity-validated during PIPELINE-TRUTH but **never
wired to the live path**. That left three pieces of standing debt:

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
  `_resolve_aggregation_input_channel` is deleted (def + the `__all__` export at `:1925`); the
  three inline `else:` fallbacks are deleted, fallback ownership having moved into `resolve_input`.
- [ ] Before rewiring, `resolve_input`'s entry-point fallback is reconciled to the live path's
  richer entry-point construction — the key format, `_find_literal_redefinition` defaults,
  param-group classification, `DESIGN_ATTRIBUTE` typing, multiplicity entry points, **and the
  `Compilability.MANUAL_REQUIRED` signal plus the EP register/dedup/backfill semantics** — so no
  input entry point collides with an output channel, no disambiguator is dropped, and no
  unresolved term is silently marked compilable (the M4 blocker is resolved, not worked around).
- [ ] A parity gate compares the **full `InputSource` the call-site block produces** — the old
  inline block (channel resolution **and** entry-point fallback) against the new `resolve_input`
  path — over the aggregation fixtures, runs in CI, and is green **before** the rewire
  (design-review M3, sharpened per spec-review L3-1: a channel-only, function-to-function gate is
  structurally blind to the M4 fallback divergence).
- [ ] The aggregation baseline is **byte-identical** after the cutover (the reconciliation is
  designed to reproduce the live EP construction exactly, so zero aggregation churn is the
  expected outcome). Any aggregation diff **blocks the cutover pending root-cause** — it is a
  defect to explain, not a deliverable to sign off. Every non-aggregation baseline (including any
  snapshot-generation fixture that carries aggregation EP construction) is byte-identical (R3).
- [ ] Strategy D is removed from `AGG_STRATEGIES`, its function deleted, and its lying docstring
  gone (the residual ghost Item 7 left noted).
- [ ] The IR-family matrix rows drop the "not-yet-wired" note and pin live code; REQ text +
  reference docs 03/04/05 + `24-dual-resolution-architecture.md` move in the same change (R1).
- [ ] The `param_groups` bind-mutate chain is untangled: the discarded Step-5 result (`:228`) is
  isolated so the live variable carries one type from `:331` onward; both `type: ignore`s at
  `:408`/`:412` are cleared.
- [ ] Gates hold: full suite green; `mypy src/` ≤ 104; `ruff check src/` ≤ 17.

## Known Requirements

- **[HARD]** **Reconcile the fallback before rewiring (M4).** When the live call site falls
  through to its inline `else:` block, it does more than mint a key. The reconciliation target —
  everything `resolve_input`'s fallback must reproduce so nothing regresses — is:
  - the part-usage-prefixed entry-point QN (`{module_eqn}__{part_usage}_{attr}`), not the module's
    bare `{module_eqn}__{leaf}`;
  - `_find_literal_redefinition` default propagation and `DESIGN_ATTRIBUTE` typing;
  - `param_group` classification via `group_deriver.classify(ep_qn)` and the multiplicity entry point;
  - the **EP register/dedup guard** (`if ep_qn not in entry_points and ep_qn not in
    new_entry_points`) and the **literal-default backfill** onto an EP created earlier without one
    (`graph_builder.py:1468-1487`, `:1582-1602`);
  - the **`Compilability.MANUAL_REQUIRED` signal** the fallback sets when a term is unresolved and
    has no literal default (`:1465`, `:1579`). This one is load-bearing: if the cutover moves the
    fallback into `resolve_input` and drops this assignment, a genuinely-unresolved aggregation term
    is silently marked compilable and gets a wrong auto-impl — the exact silent-regression class
    this epic exists to kill (spec-review L3-2).

  Forced by the coexisting-key evidence in `probe_iv_ep_key_divergence.md`. Note the SingletonTerm
  "Try 2" construction (`:1548-1560`) is **not** part of this fallback target — it builds a
  `module_output` channel, not an entry point (see Open Questions).

- **[HARD]** **Parity gate over the full `InputSource` (M3, sharpened).** The gate must compare the
  **full `InputSource` the call-site block produces** — the old inline block (channel resolution
  **and** its entry-point fallback) against the new `resolve_input` path — over the aggregation
  fixtures, green **before** the rewire. A function-to-function gate comparing only
  `_resolve_aggregation_input_channel` (channel-or-`None`) is structurally blind to the M4
  divergence: the replaced function never builds an entry point, so a channel-only gate is silent
  on exactly the fallback keys that diverge (spec-review L3-1). Backtracker parity (probe (i), the
  committed `TestResolveInputParityExtended`) remains general-correctness evidence, not
  parity-with-the-replaced-path. The gate must capture the old block's behavior before the inline
  fallbacks are deleted.

- **[HARD]** **R3 baseline discipline, tightened for this item.** All baseline/snapshot
  regeneration runs through `scripts/capture_*.py`; one regen at a time; the byte-identity gate
  proves non-aggregation baselines are untouched (timestamp-churn method: memory note
  `byte-identity-captured-at-churn`). For *this* item the aggregation baseline bar is **byte-identity**,
  not "byte-identical or reviewed diff": the reconciliation is designed to reproduce the live EP
  construction exactly, so any aggregation diff is a defect to root-cause, not expected churn to
  accept. Include any snapshot-generation fixture that carries aggregation EP construction in the
  gate scope (memory note `multihop-expose-offline-parity`). The syside license is on monthly
  renewal — no expiry pressure.

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
    stale. Reproduce the actual mypy error (capture the exact message) before committing to a fix;
    do not fix against the comment's account of the cause.

- **[HARD]** **Gate ceilings (no regression).** `mypy src/` ≤ 104; `ruff check src/` ≤ 17; full
  suite green. Current baseline is exactly 104 / 17 (PIPELINE-TRUTH close gate; re-confirm the live
  counts at pickup). The **expected** typing fix is the two-named-variable split (isolate the
  discarded Step-5 result so the live variable carries one type from `:331`) — a root annotation
  was proven not to clear it (epic Risks table). This is the expected fix, not a mandate: it stays
  contingent on what the reproduced mypy error actually shows (R4 above). Whatever the fix, it must
  clear both ignores without raising mypy above 104.

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
  (including the `MANUAL_REQUIRED` signal and register/dedup/backfill) into `resolve_input`'s
  fallback, or have the call sites pass the extra context so the module builds the same key and
  raises the same signal. The design picks the cleaner choke point; the [HARD] outcome (no
  collision, no dropped disambiguator, no lost compilability signal, byte-identical baseline) is
  fixed, the mechanism is not.

- **Is SingletonTerm "Try 2" covered by an `AGG_STRATEGY`?** Try-2 (`graph_builder.py:1548-1560`)
  builds a `module_output` **channel** (`get_channel_name(...)` checked against
  `canonical_channels`), not an entry point — it belongs in a **strategy** (the channel half), not
  the fallback. Replacing the SingletonTerm block with `resolve_input` **drops Try-2 unless one of
  the four `AGG_STRATEGIES` reproduces it** (ScopedRegistryLookup / ChainRedefinitionFollow /
  SysMLQNLookup). Design must confirm coverage; if none reproduces Try-2, add a strategy that does.
  This is a channel-resolution gap the M3 full-`InputSource` gate would catch — but design should
  answer it deliberately, not discover it in a baseline diff.

- **The shape of the M3 parity gate.** Whether it is a new conformance test parametrized over the
  aggregation fixtures, or an extension of `test_dual_resolution.py`, and how it captures the old
  call-site block's full `InputSource` before the inline fallbacks are deleted (snapshot the
  values, or run old and new side-by-side in the test). Design decides — the [HARD] outcome (full
  `InputSource`, green before rewire) is fixed.

- **LocalTerm-EXPOSE is excluded from the fallback reconciliation — confirm the reason holds.**
  Its ref is undotted, so the entry-point fallback builds `{module_eqn}__{attr}`
  (`graph_builder.py:1652`), which equals `resolve_input`'s leaf-only key — they already agree, so
  there is nothing to reconcile. Design should state this so implement does not "reconcile" it and
  break the agreement. Its channel-resolution call site (`:1640`, the expose-alias branch) is still
  in the 3-site deletion scope.

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
