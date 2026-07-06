# Design: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Status:** Draft (revised after design-review — `design-review.md`, verdict Revise; C1/M1/M2/m1/m2 resolved)
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM (~0.5–1 day)
**Branch:** upstream-findings-epic
**Git HEAD at design:** 354a09c
**Epic Item:** UPSTREAM-FINDINGS Item 9

## Overview

Capture literal `:>>` overrides on *plain* part usages so they reach generated inputs,
and harden the virtual-binding rewrite (deep-copy per instance, crash-safe bare names)
so it stays correct once those overrides flow through it. Three small, targeted changes.

## Related Artifacts

- **Spec (the contract):** `.project/active/plant-prefill/spec.md`
- **Spec review + probe:** `.project/active/plant-prefill/spec-review.md`
- **Design review (this revision resolves it):** `.project/active/plant-prefill/design-review.md`
- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 9 + R1/R2/R3, Item 10)
- **Required Reading:** `.project/research/20260705_upstream-findings-deep-research.md` (SC-5,
  four mechanisms; D → Item 10); `docs/architecture/modeling-assumptions.md` (§5, V1–V11);
  fusion-tea register `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
- **Code:** `extraction/hierarchy_resolver.py:167,187` (guard), `:54` (`_extract_single_redefinition`);
  `orchestration/pipeline_builder.py:190` (`_rewrite_virtual_bindings`, deep-path `:206`, raise `:242`);
  `extraction/usage_extractor.py:393` (shared `BindingInfo`), `:48` (dataclass)
- **Snapshot path:** `snapshot/capture.py` (live, license), `snapshot/graph_rebuild.py:25`
  (offline build — does **not** re-run the rewrite), `snapshot/loader.py`

## Research Findings

**The guard.** `extract_design_overrides` (`hierarchy_resolver.py:186–197`) skips any usage
whose *own* `owned_redefinitions` is empty — true for every plain typed usage. The `:>>`
override lives on a *member* `ReferenceUsage`, and `_extract_single_redefinition` (`:54`)
already reads `member.owned_redefinitions` and classifies the RHS into LITERAL / CHAIN /
EXPRESSION. So the member-level extractor is already correct; only the outer per-usage skip
blocks it.

**The rewrite already handles deep-path literals.** `_rewrite_virtual_bindings`
(`pipeline_builder.py:190`) builds an override index (deep-path key
`(owning_qn__intermediate, leaf)`, `:206`), then for each non-template CalcUsage binding
extracts the `source_path` leaf and rewrites a match to `BindingType.LITERAL` (`:248–252`).
For `:>> widget.base_cost = 50.0` the deep-path branch matches the `cost_model.base_cost`
binding (`source_path = AliasAggProbeLibrary::Widget::cost_model::base_cost`, leaf
`base_cost`). The recorded live probe confirmed this fires with the guard relaxed **alone**.

**`BindingInfo` is a mutable dataclass holding AST-node references.** Fields
(`usage_extractor.py:63–73`): scalars (`param_name`, `source_path`, `binding_type`,
`literal_value`, …) plus three raw SysIDE nodes (`source_instance_elem`,
`source_attribute_elem`, `expression_ast`). `_create_virtual_calc_usage` shares these objects
across sibling instances via `bindings=list(template.bindings)` (`:393`). The rewrite mutates
in place, reassigning only the *scalar* fields (`:249–254`).

**The offline test path bakes rewritten bindings; it does not re-apply the rewrite.**
`build_full_graph_from_snapshot` → `build_classifier_inputs_from_snapshot`
(`graph_rebuild.py:25`) loads the snapshot, builds the registry, runs the backtracker, and
classifies entry points. It never calls `_rewrite_virtual_bindings`. The rewrite runs only in
the **live** capture (`build_pipeline_context` → `_extract_hierarchy_and_rewrite_bindings`),
and its result is frozen into the snapshot's `calc_usages`. **Consequence:** the committed
collector-pin, generation, and V11-proof tests read the snapshot's stored bindings — flipping
them requires regenerating the four affected snapshots (see the B2 sweep and Decision D1).

**`capacity_factor` (ife_plant shape 5) is consumed by no calc.** `lcoe_calc` binds 14 plant
literals; `capacity_factor` is not among them, and it appears nowhere in the committed
`baseline_outputs/ife_plant/computation_graph.json`. So shape 5's outcome is *capture*, not a
param value (see the shape-5 correction under Key Bets and Test Design).

## Core Concept

The literal is already stated plainly in the model and the rewrite already knows how to plant
it. One over-broad guard is the only thing dropping it. **Relax the guard to scan every part
usage's members, filter the newly-scanned plain usages to LITERAL RHS, and let the existing
deep-path rewrite do the rest.** Nothing new is built — the fix removes a skip and adds a
filter. Because relaxing the guard makes the override index non-empty for models it was
previously empty for, two dormant hazards in the rewrite wake up: sibling virtual instances
that share a `BindingInfo` object, and a bare-name `source_path` that raises. Both are made
safe with the smallest correct change — a shallow per-instance copy and a skip-with-DEBUG —
so the rewrite stays correct under the wider input the guard now admits.

The design composes with existing pieces and adds no parallel mechanism: `_extract_single_redefinition`
(RHS classification), `_rewrite_virtual_bindings` (deep-path matching + literal rewrite), and
the snapshot capture/load split. The LITERAL filter is the boundary that keeps CHAIN/EXPRESSION
plain overrides — Item 10's job — inert.

## Key Bets

- **B1.** The live probe faithfully represents live extraction: with the guard relaxed, SysIDE
  yields the deep-path `base_cost` override and the rewrite plants `50.0`. *If false → the
  regenerated snapshots (or the offline patch encoding the probe result) misrepresent live
  output, and the committed gate tests a fiction.*
- **B2 (corrected after review — the sweep was run).** The guard relaxation touches *exactly
  four* committed-snapshot fixtures: `ife_plant`, `alias_agg_probe`, `issue22_model`, and
  `unresolvable_attr_probe` (the license-free `:>>` sweep, tabulated under Architecture →
  B2 sweep). Every other committed snapshot's extraction output is byte-identical. *If false →
  a fixture this item promises stays byte-identical churns; the full re-capture sweep is the
  guard.* (The original design asserted three fixtures and marked this bet settled without
  running the sweep — the review refuted it; `unresolvable_attr_probe` is the fourth. Now run.)
- **B3.** The rewrite mutates only scalar `BindingInfo` fields, never the shared AST-node
  references. *If false → a shallow per-instance copy is insufficient and a deeper copy is
  needed (but deep-copying AST nodes is itself unsafe — see D2).*

## Key Decisions

- **D1 — snapshot regeneration path (pivotal; needs sign-off).** The guard relaxation is a
  change to *live* extraction; the committed collector-pins / generation / shape-5 / V11-proof
  tests read the snapshot's baked bindings, so they only flip once the **four** affected
  snapshots (alias_agg_probe, issue22_model, ife_plant, **unresolvable_attr_probe**) are
  regenerated.
  - **Chosen:** regenerate by **live re-capture if a license is available at implement time**
    (faithful — `capture_snapshot`); **else apply a deterministic offline patch** to the four
    snapshot JSONs encoding the known delta (design_overrides entries + affected `reference`
    bindings → LITERAL), validated against the recorded live probe, with live re-capture tracked
    as opportunistic follow-up. This mirrors Item 3's D6 (committed fixture = executable gate,
    live run = opportunistic), the precedent the spec itself cites.
  - *Rejected: live re-capture as a hard gate* — blocks the item on license availability, which
    the epic treats as a blocker. *Rejected: offline patch only, no live intent* — leaves the
    snapshot unverified against true live output on the multiplicity (`widget [3]`) expansion.
  - **Do NOT skip `unresolvable_attr_probe` from the regen set.** If it is not regenerated, its
    offline collector pin keeps passing on stale bindings while live extraction diverges — the
    latent-snapshot hazard the review flagged (C1, way 2). All four regenerate together.
- **D5 — `unresolvable_attr_probe`'s `my_calc.x` IS pre-filled; the V11 proof re-anchors
  (settled by review C1).** Filling `x` from `:>> local_val = 5.0` is correct — its
  valueless-ness was itself the dropped-plain-usage-override bug Item 9 fixes; keeping it broken
  to preserve a test would be backwards. So the "dedicated committed V11 proof" role moves off
  this fixture to the two genuinely cross-part inputs that *stay* wired-valueless until Item 10:
  **catf_mfe's `[cryo_load.magnet_volume]`** and **ife_plant's shape-4 `magnet_volume`** (both
  CHAIN — the LITERAL filter keeps them out, so they remain valueless and keep tripping V11).
  *Rejected: narrow the guard predicate so this fixture is untouched* — the LITERAL filter alone
  can't (these are literals), and it would mean deliberately not fixing a real instance of the
  bug. *Rejected: hold the fixture constant* — same objection.
- **D2 — shallow per-instance copy, not `copy.deepcopy`.** In `_create_virtual_calc_usage`, mint
  each instance's bindings as `[copy.copy(b) for b in template.bindings]`. The rewrite reassigns
  only scalar fields (B3), so a shallow copy gives each instance independent scalars while the
  read-only AST references stay shared. *Rejected: `copy.deepcopy(b)`* — would recurse into
  `source_instance_elem` / `expression_ast` (a SysIDE model subgraph: slow, possibly cyclic,
  and needlessly duplicating the parse tree). *Rejected: field-wise manual copy of the three
  mutated fields* — more code, same effect, and brittle if a future field joins the mutated set.
- **D3 — LITERAL filter at capture, in `extract_design_overrides`.** Keep a newly-scanned plain
  usage's override only when `redefinition_type == LITERAL`; the existing `part redefines` branch
  keeps all RHS types. *Rejected: filter at the rewrite site* — `RedefinitionData` carries no
  "came from a plain usage" flag, and filtering there still lets CHAIN/EXPRESSION plain overrides
  enter `design_overrides`, where other consumers (chain aliases, aggregation scoping) could see
  them and churn a baseline. Filtering at capture means those overrides are never captured →
  zero downstream effect → the strongest byte-identical guarantee.
- **D4 — issue22 clean-generation coverage: a sibling generation test.** Add an
  `issue22_model` clean-generation assertion mirroring the rewritten alias_agg_probe generation
  test (shared body or a second parametrization). *Rejected: rely on the collector pin alone* —
  the pin proves no valueless EP, not that files parse and the registry imports resolve
  (REQ-NC-08 file-parse coverage). A generation test proves both.

## Architecture

Three edits, each in one function, along the existing extraction → orchestration → snapshot flow:

1. **Extraction (`hierarchy_resolver.extract_design_overrides`).** Drop the per-usage
   `owned_redefinitions` skip; scan every part usage's members. Filter newly-scanned plain
   usages to LITERAL (D3). Output: `hierarchy_data.design_overrides` gains the plain-usage
   literals.
2. **Orchestration (`pipeline_builder._rewrite_virtual_bindings`).** Unchanged matching logic;
   the now-populated index drives it. Replace the bare-name `raise` (`:242`) with
   skip-with-DEBUG (REQ-VBR-09).
3. **Extraction (`usage_extractor._create_virtual_calc_usage`).** Shallow-copy each
   `BindingInfo` (D2) so sibling virtual instances never share a binding object (REQ-VBR-08).

Data flow for the flip (live): guard relaxed → `base_cost` override in `design_overrides` →
rewrite plants `LITERAL 50.0` on each virtual `cost_model` binding, clears `source_path` →
`base_cost` never becomes a valueless entry point → V11 clean. The result is frozen into the
snapshot; offline tests then read it.

### B2 sweep — the definitive affected set (license-free `:>>` grep, run at design)

A static grep for plain-usage (non-`redefines`) LITERAL `:>>` across every committed-snapshot
fixture settles B2 deterministically. Result: **four** fixtures change under the relaxed guard.

| Fixture | Plain-usage LITERAL `:>>` | Committed snapshot | Affected |
|---|---|---|---|
| `ife_plant` | `capacity_factor = 0.95` | yes | **yes** (shape-5 capture) |
| `alias_agg_probe` | `widget.base_cost = 50.0` | yes | **yes** (base_cost → literal) |
| `issue22_model` | `widget.base_cost = 100.0` | yes | **yes** (base_cost → literal) |
| `unresolvable_attr_probe` | `base_rate`, `base_factor`, `local_multiplier` (derived_instance); `base_rate`, `base_factor`, `local_val` (design_derived_instance) | yes | **yes** (`local_val=5.0` fills `my_calc.x`; V11 proof re-anchors — D5) |
| `deep_cross_scope_probe` | `reading = 10.0`, `baseline_value = 2.0` | **no** | live-only; no test asserts it (m2) |
| `solar_battery_model` | `pv_module.wattage = 400.0`, … | yes | no — overrides sit on a `part redefines` usage, already captured today |
| `chain_override_probe` | `base_cost = 100.0` | yes | no — on a `part redefines` usage; `sensitivity` is CHAIN |
| `catf_mfe_model` | (CHAIN only) | yes | no — LITERAL filter keeps it out; stays V11-pinned |
| `wi014_toy` and all others | none | yes | no |

`deep_cross_scope_probe` has plain-usage LITERAL `:>>` but **no committed snapshot and no test
reference** — its live extraction changes with nothing asserting it. Flagged (m2) so a future
snapshot capture is not a surprise.

## Required Invariants

- **INV-1.** CHAIN/EXPRESSION overrides on plain usages never enter `design_overrides`
  (never captured) → they cannot rewrite a binding or churn a baseline here.
- **INV-2.** No two virtual CalcUsage instances share a `BindingInfo` object after
  `_create_virtual_calc_usage`.
- **INV-3.** `_rewrite_virtual_bindings` raises on no input (bare-name source paths are skipped).
- **INV-4.** The existing `part redefines` capture path is behaviorally unchanged (all RHS types
  still captured; same objects, same order).
- **INV-5 (restated).** Exactly the four fixtures enumerated in the B2 sweep
  (`ife_plant`, `alias_agg_probe`, `issue22_model`, `unresolvable_attr_probe`) change their
  extraction output; **every other committed snapshot is byte-identical**, including the four
  byte-exact baselines (solar_battery, attr_expr_probe, chain_spike, sample_model) and catf_mfe.
  Verified by the full re-capture sweep at implement (not deferred as a bet — the static `:>>`
  grep already settled it; the sweep confirms).

## Component Overview

- **`extract_design_overrides`** (`hierarchy_resolver.py:167`) — outer scan over part usages;
  now unconditional over members, LITERAL-filtered for plain usages.
- **`_extract_single_redefinition`** (`hierarchy_resolver.py:54`) — unchanged; already classifies
  RHS and reads member `owned_redefinitions`.
- **`_rewrite_virtual_bindings`** (`pipeline_builder.py:190`) — unchanged matching; bare-name
  raise → DEBUG skip.
- **`_create_virtual_calc_usage`** (`usage_extractor.py:366`) — `list(template.bindings)` →
  `[copy.copy(b) for b in template.bindings]`.

## Non-Goals

Per spec: cross-part channel wiring (Item 10); CHAIN/EXPRESSION plain-override *rewrite*
(captured-inert at most — here, not captured); self-named-binding *rescue* (Item 10 handoff —
only crash-safety lands); flipping catf_mfe / ife_plant shape 4; wiring ife_plant shape 2;
scope-2 LVP backfill (cut). This design adds no V-rule and no schema field.

## Implementation Notes

- **Guard relaxation shape.** Compute `is_part_redefines = bool(usage.owned_redefinitions)`
  once per usage, always scan members, and `continue` on a plain-usage override whose
  `redefinition_type != RedefinitionType.LITERAL`. ~6 changed lines.
- **Performance.** Previously the outer loop early-continued on nearly all usages; now every
  `PartUsage`'s `owned_members` runs through `_extract_single_redefinition` (cheap: returns
  `None` for non-`ReferenceUsage` / no-`owned_redefinitions` members). O(usages × members),
  one-shot at extraction, corpus is tens of usages — negligible. No caching. Note it in doc 25.
- **Deep-copy site.** In `_create_virtual_calc_usage` only — the single place siblings are minted
  from a template. `import copy` at module top. `unbound_params=list(...)` (strings) stays as-is.
- **Bare-name skip.** `logger.debug("bare-name source_path %r on %s; skipping override match",
  source, usage.qualified_name)` then `continue`. Condition is the existing `else` (no `::`,
  no `.`).
- **Extend, don't fork (R1).** Reuse the deep-path matcher; add no parallel matcher.

## Test Design

**Pin-flip checklist (the definitive flip set):**

| Test | From → To |
|---|---|
| `test_uncovered_params.py::test_collector_pins_alias_agg_probe` | `[("base_cost","cost_model")]` → `[]` |
| `test_uncovered_params.py::test_collector_pins_issue22_model` | `[("base_cost","cost_model")]` → `[]` |
| `test_uncovered_params.py::test_collector_pins_unresolvable_attr_probe` (`:104`) | `[("x","my_calc")]` → `[]` — `local_val=5.0` fills `x` (traced empty below) |
| `test_uncovered_params.py::test_reconcile_raises_v11_on_wired_gap` (`:129`) | feeds `unresolvable_attr_probe`, asserts V11 raise → **re-anchor to `catf_mfe_model`** (still wired-valueless → still raises) |
| `test_uncovered_params.py::test_seeded_strict_generation_aborts_independently_of_catf_mfe` (`:139`) | feeds `unresolvable_attr_probe` → **re-anchor to `ife_plant`** (a non-catf_mfe fixture that still trips strict V11 on shape-4 `magnet_volume`, preserving the "independent of catf_mfe" purpose) |
| `test_uncovered_params.py` module docstring (`:9–19`) + `test_collector_pins_unresolvable_attr_probe` docstring | drop "the only committed real-fixture / dedicated V11 proof" wording — that title moves to catf_mfe + ife_plant shape-4 (D5) |
| `test_alias_agg_probe_generation.py::test_alias_agg_probe_aborts_with_v11...` | raises-V11 → clean, `ast.parse`-valid, importable package (restores REQ-NC-08 file-parse coverage); rename to drop "aborts" |
| `test_ife_plant.py::test_shape5_plain_usage_override_dropped` | asserts `design_attributes` absence → asserts `design_overrides` **capture** (see correction) |
| **new** `test_issue22_generates_clean` (D4) | issue22 generates a clean, parseable package |
| optional: `unresolvable_attr_probe` clean-generation | `run_codegen` on it now returns `True` (x filled, everything resolves) — an added assertion, restoring its file-parse coverage |

**`unresolvable_attr_probe` violation list traced (not assumed).** Its only wired binding is
`my_calc.x = local_val` (`'Design Derived'` is the only def with a calc; `'Derived Component'`
has computed attributes but no calc). `:>> local_val = 5.0` on the plain `design_derived_instance`
is a non-deep-path LITERAL → override key `(…design_derived_instance, local_val)`; the `my_calc`
binding's parent is `…design_derived_instance`, leaf `local_val` (via `::` rsplit) → match →
`x` rewritten to `LITERAL 5.0`, `source_path` cleared. No other calc, no other unresolved
binding, so the collector list goes to **`[]`** and strict generation is **clean**. The other
captured overrides (`base_rate`, `base_factor`, `local_multiplier`) feed only FORMULA computed
attributes, which the collector never counted — they add no violation.

**Shape-5 correction (flag for sign-off).** The spec SC reads "capacity_factor reaches params
as 0.95." It does not — `capacity_factor` is consumed by no calc and appears nowhere in the
ife_plant graph, so like shape 2 it is *captured-but-unwired*. The rewritten test asserts the
verifiable outcome: `hierarchy_data.design_overrides` now contains
`baseline_plant.capacity_factor = 0.95` (bare-name LITERAL), and the def-level 0.90 default
stays. The genuine "reaches params" evidence is alias_agg_probe / issue22, where `base_cost`
*is* consumed → rewritten → V11 clean.

**Divergent-sibling regression (REQ-VBR-08).** No committed fixture has multiplicity siblings
with *divergent* overrides (`widget [3]` all get the same 50.0). Build a constructed unit test
on `_rewrite_virtual_bindings` from **real objects** (precedent: `test_unwired_fallthrough_partition`
builds real Pydantic models, not mocks): one template with a `base_cost` reference binding →
two instances via `_create_virtual_calc_usage(template, pathA/pathB)` → a
`HierarchyExtractionResult` with two deep-path LITERAL overrides keyed to pathA (50.0) and
pathB (100.0) → run the rewrite → assert `iA.base_cost == 50.0` **and** `iB.base_cost == 100.0`.
Without the copy, iA's rewrite mutates the shared object to LITERAL, iB is then skipped as
already-LITERAL, and iB reads 50.0 — the test fails. This asserts the *rewrite* respects the
instance boundary, not mere object distinctness.

**Bare-name crash-safety (REQ-VBR-09).** The raise at `pipeline_builder.py:242` fires only when a
binding has a **bare-name** `source_path` (no `::`, no `.`) *and* the index is non-empty. After
relaxation, `unresolvable_attr_probe` and ife_plant both have a **non-empty** index — so the
"empty index shields the raise" reasoning no longer holds for them. What actually shields the
raise is that their reachable bindings are all `::`-qualified (`unresolvable_attr_probe`'s
`my_calc.x` source_path is `UnresolvableAttrProbeDesign::'Design Derived'::local_val`; ife_plant's
`lcoe_calc` self-named bindings are `IfePlantLib::'Ife Power Plant'::…`) — they take the `::`
branch, never the bare-name `else`. And `self_named_binding_trap` has no plain-usage literal
override, so *its* index stays empty. So no committed fixture reaches the bare-name `else`; the
guarantee holds by branch, not by empty index. Cover it with a constructed unit test: a
calc_usage with a bare-name `source_path` binding + a `HierarchyExtractionResult` carrying one
override (non-empty index) → assert `_rewrite_virtual_bindings` does not raise, logs DEBUG, and
leaves the binding unchanged.

**Baseline regen (enumerate the diff classes):**

- **ife_plant `extraction_snapshot.json`** — `design_overrides` gains one entry
  (`baseline_plant.capacity_factor = 0.95`). `calc_usages` unchanged (unconsumed).
- **ife_plant `baseline_outputs/…/computation_graph.json` + `registry_init.py`** — byte-identical
  (capacity_factor never enters the graph).
- **alias_agg_probe `extraction_snapshot.json`** — `design_overrides` gains the deep-path
  `base_cost` override; each virtual `cost_model` `base_cost` binding → `LITERAL 50.0`,
  `source_path: null`. (No `baseline_outputs` dir for this fixture.)
- **issue22_model `extraction_snapshot.json`** — same with `100.0`.
- **unresolvable_attr_probe `extraction_snapshot.json`** — `design_overrides` gains ≥6 entries
  (`base_rate`, `base_factor`, `local_multiplier` on `derived_instance`; `base_rate`,
  `base_factor`, `local_val` on `design_derived_instance`); the `my_calc.x` binding → `LITERAL
  5.0`, `source_path: null`. (No `baseline_outputs` dir.) **Must be regenerated** — omitting it
  leaves the offline pins passing on stale bindings (D1 caveat).
- **Everything else** — byte-identical (the 4 byte-exact baselines, catf_mfe, wi014_toy, all
  other snapshots). The deep-copy alone churns nothing (value-based serialization).
- **`deep_cross_scope_probe`** — no committed snapshot; its live extraction changes but nothing
  asserts it (m2). No committed artifact to regenerate; noted for a future capture.

## Docs / Matrix

- **Doc 25** (`reference/25-hierarchy-resolver.md`) — guard relaxation + LITERAL filter +
  performance note (REQ-HR-08).
- **Doc 12** (`reference/12-virtual-binding-rewrite.md`) — `BindingInfo` deep-copy (REQ-VBR-08)
  and bare-name skip-with-DEBUG (REQ-VBR-09).
- **Verification matrix** (`docs/architecture/verification-matrix.md`) — rows for REQ-HR-08,
  REQ-VBR-08, REQ-VBR-09. `modeling-assumptions.md` §5 as applicable. **Doc 18 (LVP) untouched.**
- **agentic-mbse (R2):** plain-usage `:>>` **literal** overrides now honored — teach
  `part x : Type { :>> nested.attr = <literal>; }` as supported (executed in Item 12, once
  Item 10 lands). Self-named check stays a FAIL against self_named_binding_trap (rescue → Item
  10). No checker script lands here. Confirm at close-out.

## Potential Risks

- **Snapshot faithfulness (highest).** If D1 lands as an offline patch, the patched snapshot
  must match true live output — especially the `widget [3]` expansion (how many virtual
  `cost_model` instances carry a `base_cost` binding, and whether the rewrite hits each). The
  recorded probe minted a single design-level key; confirm the instance count when patching.
  Mitigation: prefer live re-capture; the constructed unit tests prove the code independent of
  the snapshot.
- **Unintended capture (B2) — now bounded.** The `:>>` sweep enumerated the affected set as
  exactly four fixtures (Architecture → B2 sweep). The residual risk is a fixture the static grep
  missed (e.g. a literal `:>>` on a plain usage whose enclosing kind the grep misjudged);
  mitigation: the full re-capture / byte-exact sweep at implement is the deterministic guard.
- **V11 proof re-anchor (from C1).** `unresolvable_attr_probe` stops being a V11 case once `x`
  fills; the strict-boundary raise proof must move to catf_mfe (`test_reconcile_raises_v11...`)
  and ife_plant (`test_seeded_strict_generation...`). Risk: ife_plant shape-4 must actually trip
  V11 at *strict generation* (not just the in-memory collector) to serve the independent-of-
  catf_mfe role — implement verifies this; if it does not, author a minimal genuinely-unbound
  seeded fixture instead. This keeps a live V11 raise proof committed.
- **Bare-name reachability.** REQ-VBR-09 is defensive: no committed fixture reaches the bare-name
  `else` (guaranteed by branch — reachable bindings are `::`-qualified — not by an empty index;
  see m1 correction). Constructed test is the coverage.

## Integration Strategy

Pure extraction + orchestration-phase changes; no schema change, no generation-template change,
no new module. Slots into the existing capture → load → build flow. Complements Item 8's
fixtures (the diff base) and sets Item 10's precondition (per-instance-safe rewrite).

## Validation Approach

1. Constructed unit tests (divergent-sibling REQ-VBR-08; bare-name REQ-VBR-09) — license-free,
   prove the code.
2. Regenerate the **four** affected snapshots (D1: ife_plant, alias_agg_probe, issue22_model,
   unresolvable_attr_probe); run the full pin-flip checklist — the executable gate.
3. Full baseline / byte-exact sweep — proves INV-5 (exactly the four change, nothing else).
4. Confirm the re-anchored V11 raise proof fires (catf_mfe strict raise; ife_plant strict abort).
5. `mypy src/` + `ruff check src/`.
6. Opportunistic: live fusion-tea IFE re-run (license-blocked) recorded if run.

## Next-Stage Handoff

- **Fixed:** the three edits (guard relax + LITERAL filter, shallow copy, bare-name skip); D2/D3/D4;
  D5 (unresolvable_attr_probe pre-fills; V11 proof re-anchors — settled by review C1); the
  four-fixture affected set (B2 sweep); the full pin-flip checklist; scope-2 cut; self-named
  rescue → Item 10.
- **Open (needs sign-off):** D1 (live re-capture vs offline patch) and the shape-5 correction
  (capture-only, not "reaches params").
- **De-risk first:** D1 — confirm license availability, the `widget [3]` instance count, and that
  ife_plant shape-4 trips *strict* V11 (the re-anchor). Land the constructed unit tests first
  (they need no snapshot), then regenerate the four snapshots, then the sweep.

## Appendix — Evidence

- **base_cost binding (alias_agg_probe snapshot):** `source_path =
  "AliasAggProbeLibrary::Widget::cost_model::base_cost"`, `binding_type = "reference"`,
  `literal_value = null`; `design_overrides = []`; `multiplicities` carries `widget`
  (`Widget_Assembly`). Leaf via `rsplit("::",1)[-1]` = `base_cost` → matches deep-path key.
- **Shape-5 model:** `design.sysml` — `part baseline_plant : 'Ife Power Plant' { :>>
  capacity_factor = 0.95; }` (plain usage, bare-name literal). `library.sysml` — `lcoe_calc`
  binds 14 literals, not `capacity_factor`; `capacity_factor : Real default := 0.90` unconsumed.
- **ife_plant graph:** no `capacity_factor` token in `baseline_outputs/ife_plant/computation_graph.json`.
- **Offline path:** `build_classifier_inputs_from_snapshot` (`graph_rebuild.py:25`) has no
  `_rewrite_virtual_bindings` call; the rewrite runs only under `capture.py` → `build_pipeline_context`.

---
**Next Step:** After approval → `/_my_plan` (or `/_my_implement`).
