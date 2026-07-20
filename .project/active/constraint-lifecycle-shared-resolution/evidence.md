# Evidence: Lifecycle Item 2 — Shared Producer Resolution and Gate A

**Status:** Candidate for independent audit
**Owner:** Reid W
**Branch:** `constraint-exec-epic`
**RED coordinate:** `287afc47ab06826de27c38e203ffffb45398f972` (Item 1 certified)
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — Item 2, register row 2
**Artifacts:** `spec.md`, `design.md` (rev 2 + implementation notes), `design-review.md`

---

## What this item did

Three independently-ordered resolvers answered the same question — *which real thing
produces this consumed value?* — and had drifted in ordering, in candidate
identification, and in what they did when nothing matched. They are now one declared
table in `resolution/producer_resolution.py`. Separately and upstream, Gate A is fixed:
a constraint owned by a concrete `PartUsage` is no longer misclassified as
package-owned.

Read the design's Implementation Notes for the phase-by-phase record. This document is
the per-requirement account and the honest list of what did not land.

---

## Per-requirement record

### A. Scope and authority

| Req | Status | Evidence |
|---|---|---|
| SR-R01 | **Met** | `resolve_producer` is the only positive-resolution path; tier 1 (channel) exhausts before tier 2 (design attribute), pinned by `test_tier_one_exhausts_before_tier_two` |
| SR-R02 | **Met** | Strictness is read once, after the table and the climb (`_terminal_miss`); pinned by `test_terminal_policy_is_the_only_fork` |
| SR-R03 | **Met** | Gate A: `GateA__the_host__gain` resolves on the public live route with no passthrough; `test_gate_a_usage_owned_attribute_resolves_under_its_real_qn` |
| SR-R04 | **Met** | Modeled defaults are read from the design attribute, never synthesized; `_modeled_default` |
| SR-R05 | **Met** | The register/backfill pair is gone; `_mint_entry_point_once` writes once |
| SR-R06 | **Met** | `resolve_logical_demand`, `select_group_source`, `enrich_graph_design_attributes` untouched; `prepare_constraint_usages` gained exactly one branch |
| SR-R07 | **Met** | V11 widening left to Item 3 (I10); written-reference carry referred to Item 4 (PC-4) |
| SR-R08 | **Met** | Same-checkout replay used as regression evidence only; the Gate A fixtures carry committed snapshots |

### B. The one resolution procedure

| Req | Status | Evidence |
|---|---|---|
| SR-R10 | **Met** | One `ProducerRequest` / `ProducerResolution`; all three consumers build and read them |
| SR-R11 | **Met, refined** | Two *tiers*, 21 key forms. The contract's claim is the tier count; the form count is what the ladders actually did (~24 lookups). Order is data, pinned by `test_table_order_and_admissibility_are_declared` |
| SR-R12 | **Met** | All four guessing behaviors deleted. Every surviving name-based form returns a result only when exactly one candidate survives, and records the tie otherwise |
| SR-R13 | **Met** | One guard predicate, applied at every tier-1 hit for every consumer; a rejection skips the candidate and continues the table |
| SR-R14 | **Met** | One terminal fork. The strict error now names the usage, formal, reference, attempted forms, and tied candidates |
| SR-R15 | **Met** | Every lenient terminal miss emits one WARNING (I7). Severity vocabulary stays Item 4's |
| SR-R16 | **Met** | One writer, default resolved at creation. Two minters disagreeing on a default refuse rather than race |
| SR-R17 | **Met** | The leaf-name tier survives (no exact form covers its population) but refuses on collision instead of returning the first value |

### C. Gate A

| Req | Status | Evidence |
|---|---|---|
| SR-R20 | **Met** | Live route, `tests/fixtures/gate_a/` |
| SR-R21 | **Met** | Usage-owned attribute on a concrete `PartUsage`, def-typed constraint, self-named actual. Not the weaker `constraint_inline` shape |
| SR-R22 | **Met** | Real simkit: `satisfied` at 40.0, `violated` at 5.0 (`tests/execution/test_gate_a_execution.py`) |
| SR-R23 | **NOT MET — referred to Item 4** | See PC-4 below and `tests/fixtures/shared_producer/PROVENANCE.md` |

### D. Preservation and parity

| Req | Status | Evidence |
|---|---|---|
| SR-R30 | **Met** | Live and snapshot routes agree; Gate A fixtures captured and replayed |
| SR-R31 | **Met** | Every pre-existing fixture byte-identical. Five forced differences enumerated in the design, none with a corpus population |
| SR-R32 | **Met** | Item 1's acceptance file and `constraint_occurrence_demand/` untouched |
| SR-R33 | **Met** | All six precedence pins pass **unchanged**. No pin deleted, none changed |
| SR-R34 | **Met** | Full suite, execution lane, byte-identity gate, all at one coordinate |

### E. Deletion and simplification

| Req | Status | Evidence |
|---|---|---|
| SR-R40 | **Met** | One authority. `input_resolver.py` deleted outright, not shimmed |
| SR-R41 | **Met** | Absence checks below |
| SR-R42 | **Met** | `_get_parent_part_for_usage` and `_consumer_scope_dotted` survive as request builders; `_is_self_reference`, `_is_calc_def_owned`, `_deindexed_scope` moved into the resolver; `_reference_dotted` and `occurrence_scope` stay (surviving callers) |
| SR-R43 | **Met** | Migrations listed below |
| SR-R44 | **Met** | Six docstrings amended to describe the one procedure. Zero references to deleted mechanisms remain in `src/` |

### F. Acceptance rows

| ID | Status |
|---|---|
| SR-A01 Gate A | **GREEN** — live + real simkit verdict, flips with the literal |
| SR-A02 two-consumer convergence | **NOT DELIVERED** — referred to Item 4 (PC-4), pinned known-incomplete |
| SR-A03 precedence observable | **GREEN** — one declared table; six pins unchanged |
| SR-A04 ambiguity refuses | **GREEN** — `test_dotted_pair_form_refuses_on_multiple_candidates`, `test_chain_redefinition_follow_refuses_on_multiple_matches` |
| SR-A05 leaf collision refuses | **GREEN** — `test_d310_leaf_redef_collision_refuses_rather_than_guessing` |
| SR-A06 terminal fork | **GREEN** — `test_terminal_policy_is_the_only_fork` |
| SR-A07 written once | **GREEN** — `test_two_minters_disagreeing_on_a_default_refuse_rather_than_race`; backfill absent |
| SR-A08 modeled default only when declared | **GREEN** — carried by the existing constraint suite, unchanged |
| SR-A09 self-reference refused on every route | **GREEN** — one predicate, all three consumers; `test_self_reference_is_skipped_and_the_table_continues` |
| SR-A10 live/replay parity | **GREEN**, replay labeled non-certifying |
| SR-A11 unchanged RED nodes | **GREEN** — Gate A nodes authored once, failed at the predicted terminal raise pre-fix, pass post-fix |
| SR-A12 deletion proof | **GREEN** — absence table below |
| SR-A13 regression union | **GREEN** — battery below |

---

## Deletion absence proof (SR-A12)

Occurrences in `src/` after the cutover:

| Deleted | Count |
|---|---|
| `_resolve_chain_dispatch`, `_resolve_reference_dispatch`, `_resolve_reference_via_registry`, `_resolve_to_design_attribute` | 0 |
| `resolve_input`, `AGG_STRATEGIES`, `ResolutionStrategy` | 0 |
| `ScopedRegistryLookup`, `ChainRedefinitionFollow`, `SysMLQNLookup`, `DirectChannelConstruction` | 0 |
| `ResolutionContext` | 2 — both naming it as *replaced*, in the docstrings of what replaced it |

`src/sysml_codegen/resolution/input_resolver.py` is deleted from the tree. No wrapper,
flag, alias, or route adapter survives; each deletion happened in the same change set as
its consumer's cutover.

**The four guessing behaviors, specifically:** the calculation bare-name multi-candidate
first-pick and same-file tiebreak; the dotted arm's first-hit scan; `_find_literal_redefinition`'s
warn-and-return-first collision arm; and `ChainRedefinitionFollow`'s case-insensitive
first-`break`. All four are gone. The deterministic unique-or-refuse forms survive as
declared lenient-only key forms, which is where they already lived.

**I10 one-writer check:** `_fallback_entry_points.add` appears exactly once in `src/`, in
the calculation consumer. V11 scope is calculation-only, unchanged.

---

## Validation battery

| Gate | Result |
|---|---|
| Full suite | **3003 passed, 38 skipped, 0 failed** |
| `-O` | 3001 passed; the only 2 failures are pre-existing (`test_expression_compiler`, bare `assert` stripped by `-O`), reproduced with production stashed |
| Real simkit execution lane | **17 passed** |
| Byte-identity gate (`test_baselines.py`) | **17 passed** |
| Byte-identity manifest | `git status` over `tests/fixtures/` shows **only the four new fixture directories**; every pre-existing fixture byte-identical |
| EP-key identity (F4 control) | **0 diffs** across 34 fixtures / 273 entry points / 484 module inputs, before vs after the aggregation cutover |
| `ruff check src/` | clean |
| `mypy src/` | 72 errors — **below** the 76-error baseline (deletions removed untyped code) |
| `ruff check tests/` | 165 fixable — was 171 before this item; tests are not a project gate and are format-exempt |

The EP-key manifest is the control the F4-cutover lesson demanded: `resolve_input`'s
fallback was *not* a drop-in for the live aggregation path, and an EP-key collapse would
have been invisible to the baseline gate on fixtures with no committed baseline. Captured
before Phase 5b, re-run after, zero movement.

---

## Recorded deviations

### Surfaced premise conflicts

- **PC-1 — Gate A is an owner-classification defect touching an Item 1 seam.** Confirmed
  first-hand before any production edit. Resolved: one added branch, three existing
  branches unchanged, zero admitted usage-owned constraints existed to disturb.
- **PC-2 — the entry-point backfill is not post-build mutation.** SR-R16's stated basis
  was wrong; the requirement survives on cross-source order-dependence. Spec text should
  be amended to its true basis when next touched.
- **PC-3 — V11's scope is narrower than "one mint point" implies.** Aggregation-minted
  entry points are invisible to V11 today. Preserved exactly (I10); widening is Item 3's.
- **PC-4 — the calculation consumer cannot express the reference as written.** Binding
  extraction discards the written name; for a self-named binding the referent is the
  calc's own formal. So the occurrence-materialized form is unreachable from that
  consumer, **I9 is falsified for the self-named shape, and SR-A02 is not deliverable by
  Item 2's means.** Referred to Item 4. Measured alternative (exact structural recovery)
  rejected: it newly resolves 22 single-consumer bindings across six fixtures, fixing no
  wrong value while renaming entry-point identity and shrinking V11 membership ahead of
  Item 3's vacuity proof.

### D2 falsified as stated

No single total order reproduces all three ladders' current precedence: the calculation
ladder tries the structured-alias forms (rows 6, 8) before the bare-alias form (row 5),
the constraint ladder does the opposite. Two irreconcilable pairs, both on the
LENIENT/STRICT axis. The table takes the constraint order. Measured: 44 of 249
calculation bindings hit exactly one of the conflicting rows, **none hits two**, so the
conflict is latent rather than exercised. Recorded in the module docstring; byte identity
is the standing control. **A reviewer should look here first.**

### Five forced differences

Each with no corpus population, so no pre-existing generated byte moved:

1. A colliding leaf-name literal redefinition refuses, so `literal_default` is `None` and
   the term's compilability flips to `MANUAL_REQUIRED`. *This changes a verdict, not just
   a diagnostic.* (SR-R12/SR-R17)
2. Every lenient terminal miss emits one WARNING. (SR-R15/I7)
3. The strict error names attempted forms and tied candidates. (SR-R14)
4. The LocalTerm mint carries its modeled default; reachable only on the new
   `agg_localterm_probe`. (SR-R16)
5. Two minters disagreeing on one QN's default leave it defaultless and warn. (I5)

### Other deviations

- **Dispatch placement.** The `part_usage` branch sits inside the `package` arm rather
  than ahead of the dispatch: a `PartUsage` nested in a part def also has
  `owner.owner.kind == "PartUsage"`, and an unconditional check would have pulled those
  out of `_expand_part_owner` — rework, not extension.
- **`owner_kind` unchanged.** A usage-owned constraint still records `"package"`, the
  owning-*definition* kind that field documents.
- **`LibraryPackage` allowlisted** as a package-owner kind; omitting it would have made
  D10's raise fire on a shape that works today.
- **Fixtures carry an unrelated calc.** The pipeline refuses a model with no calc
  definition; the added calc neither produces nor consumes the constrained attribute, so
  it cannot mask the defect (confirmed by the RED re-run).
- **`param_group` on LocalTerm mints stays `None`.** Out of scope by ruling — a
  classification question, `group_deriver`'s domain. The parameter still emits through
  the post-aggregation group rebuild. State pinned in
  `test_localterm_entry_point_is_rendered_in_a_parameter_group`.

### Test migrations (SR-R43)

Private mechanics of deleted internals were deleted; observable coverage moved onto the
table. `test_input_resolver.py` (27 strategy-internal tests) → `test_agg_key_forms.py`
(9 tests, one per surviving form family plus the terminal miss). Six
`test_dual_resolution.py` parity classes retired — they compared two independent
resolvers that are now one, making the comparison tautological — replaced by
`TestOneResolutionAuthority`, which pins the property the sweep existed to protect.
`test_matcher_fixes_item7`, the climb tests, and the leaf+parent tests re-pointed at
`resolve_producer` with their assertions intact.
`test_silent_failure_family3.py` migrated from warn-and-first-wins to refusal, as
declared. Three architectural guards (untyped `resolve()`, typed lookups present, untyped
`dict.get`) re-pointed at `producer_resolution`, which now owns every lookup.

Chain-redefinition probe data moved to matching case: those probes were written with a
part-def leaf whose case differed from the reference's part usage, which the deleted
case-folding papered over. Refusal on a case-folded match is pinned separately.

---

## What stays open

- **Item 3 (Gate B):** whether V11 should widen to aggregation entry points (PC-3).
  Preserved exactly here; the decision must not be made silently by refactor.
- **Item 4:** the written-reference carry — extraction preserves the reference as
  written and the snapshot format carries it. That completes SR-A02/SR-R23 on real data
  with no name inference. Folded into Item 4's coordinated `agentic-mbse` + codegen
  change set per orchestrator ruling.
- **Item 4/10 territory:** whether `param_group` should be populated on LocalTerm mints.
- **Spec text:** SR-R16's stated basis (PC-2) should be amended to order-dependence.
- **Item 5:** relocated whole-tree replay remains the certifying route; same-checkout
  replay here is labeled non-certifying.

---

## New fixtures

| Fixture | Purpose |
|---|---|
| `gate_a` | Usage-owned literal on a concrete `PartUsage`, def-typed constraint, self-named actual (SR-A01) |
| `gate_a_package_owner` | The genuinely package-owned control — no fixture covered this shape before (M6) |
| `agg_localterm_probe` | The only model that reaches the aggregation LocalTerm mint |
| `shared_producer` | **Recorded known-incomplete** — two consumers, two entry points. See its `PROVENANCE.md` |
