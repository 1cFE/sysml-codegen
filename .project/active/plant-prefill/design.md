# Design: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Status:** Draft
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
collector-pin and generation tests read the snapshot's stored bindings — flipping them
requires regenerating three snapshots (see Decision D1).

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
- **B2.** Relaxing the guard captures no plain-usage LITERAL override in any committed fixture
  besides `capacity_factor` (ife_plant) and `base_cost` (alias_agg_probe, issue22). *If false →
  a fixture whose baseline this item promises is byte-identical churns; the byte-exact suite
  catches it, but the promise breaks.*
- **B3.** The rewrite mutates only scalar `BindingInfo` fields, never the shared AST-node
  references. *If false → a shallow per-instance copy is insufficient and a deeper copy is
  needed (but deep-copying AST nodes is itself unsafe — see D2).*

## Key Decisions

- **D1 — snapshot regeneration path (pivotal; needs sign-off).** The guard relaxation is a
  change to *live* extraction; the committed collector-pins / generation / shape-5 tests read
  the snapshot's baked bindings, so they only flip once the three snapshots
  (alias_agg_probe, issue22_model, ife_plant) are regenerated.
  - **Chosen:** regenerate by **live re-capture if a license is available at implement time**
    (faithful — `capture_snapshot`); **else apply a deterministic offline patch** to the three
    snapshot JSONs encoding the known delta (design_overrides entry + `base_cost` binding →
    LITERAL), validated against the recorded live probe, with live re-capture tracked as
    opportunistic follow-up. This mirrors Item 3's D6 (committed fixture = executable gate,
    live run = opportunistic), the precedent the spec itself cites.
  - *Rejected: live re-capture as a hard gate* — blocks the item on license availability, which
    the epic treats as a blocker. *Rejected: offline patch only, no live intent* — leaves the
    snapshot unverified against true live output on the multiplicity (`widget [3]`) expansion.
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

## Required Invariants

- **INV-1.** CHAIN/EXPRESSION overrides on plain usages never enter `design_overrides`
  (never captured) → they cannot rewrite a binding or churn a baseline here.
- **INV-2.** No two virtual CalcUsage instances share a `BindingInfo` object after
  `_create_virtual_calc_usage`.
- **INV-3.** `_rewrite_virtual_bindings` raises on no input (bare-name source paths are skipped).
- **INV-4.** The existing `part redefines` capture path is behaviorally unchanged (all RHS types
  still captured; same objects, same order).
- **INV-5.** The four byte-exact baselines (solar_battery, attr_expr_probe, chain_spike,
  sample_model) and every snapshot except the three named stay byte-identical.

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
| `test_alias_agg_probe_generation.py::test_alias_agg_probe_aborts_with_v11...` | raises-V11 → clean, `ast.parse`-valid, importable package (restores REQ-NC-08 file-parse coverage); rename to drop "aborts" |
| `test_ife_plant.py::test_shape5_plain_usage_override_dropped` | asserts `design_attributes` absence → asserts `design_overrides` **capture** (see correction) |
| **new** `test_issue22_generates_clean` (D4) | issue22 generates a clean, parseable package |

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

**Bare-name crash-safety (REQ-VBR-09).** No committed fixture combines a non-empty index with a
bare-name source path: ife_plant's self-named bindings are qualified (`::`), and
self_named_binding_trap has no plain-usage literal override (its index stays empty). Cover it
with a constructed unit test: a calc_usage with a bare-name `source_path` binding + a
`HierarchyExtractionResult` carrying one override (to populate the index) → assert
`_rewrite_virtual_bindings` does not raise, logs DEBUG, and leaves the binding unchanged.

**Baseline regen (enumerate the diff classes):**

- **ife_plant `extraction_snapshot.json`** — `design_overrides` gains one entry
  (`baseline_plant.capacity_factor = 0.95`). `calc_usages` unchanged (unconsumed).
- **ife_plant `baseline_outputs/…/computation_graph.json` + `registry_init.py`** — byte-identical
  (capacity_factor never enters the graph).
- **alias_agg_probe `extraction_snapshot.json`** — `design_overrides` gains the deep-path
  `base_cost` override; each virtual `cost_model` `base_cost` binding → `LITERAL 50.0`,
  `source_path: null`. (No `baseline_outputs` dir for this fixture.)
- **issue22_model `extraction_snapshot.json`** — same with `100.0`.
- **Everything else** — byte-identical (the 4 byte-exact baselines, catf_mfe, wi014_toy, all
  other snapshots). The deep-copy alone churns nothing (value-based serialization).

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
- **Unintended capture (B2).** A plain-usage literal override in another fixture would churn a
  baseline. Mitigation: the byte-exact suite + a full baseline sweep is the guard.
- **Bare-name reachability.** REQ-VBR-09 is defensive (no committed fixture triggers it).
  Documented as such; constructed test is the coverage.

## Integration Strategy

Pure extraction + orchestration-phase changes; no schema change, no generation-template change,
no new module. Slots into the existing capture → load → build flow. Complements Item 8's
fixtures (the diff base) and sets Item 10's precondition (per-instance-safe rewrite).

## Validation Approach

1. Constructed unit tests (divergent-sibling REQ-VBR-08; bare-name REQ-VBR-09) — license-free,
   prove the code.
2. Regenerate the three snapshots (D1); run the pin-flip checklist — the executable gate.
3. Full baseline / byte-exact sweep — proves INV-5 (nothing else churns).
4. `mypy src/` + `ruff check src/`.
5. Opportunistic: live fusion-tea IFE re-run (license-blocked) recorded if run.

## Next-Stage Handoff

- **Fixed:** the three edits (guard relax + LITERAL filter, shallow copy, bare-name skip); D2/D3/D4;
  the pin-flip checklist; scope-2 cut; self-named rescue → Item 10.
- **Open (needs sign-off):** D1 (live re-capture vs offline patch) and the shape-5 correction
  (capture-only, not "reaches params"). Both are surfaced in the presentation below.
- **De-risk first:** D1 — confirm license availability and the `widget [3]` instance count before
  touching the alias_agg_probe / issue22 snapshots. Land the constructed unit tests first (they
  need no snapshot), then the snapshots, then the sweep.

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
