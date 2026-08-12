# 24 -- Resolution Architecture: One Authority, Called at Two Pipeline Stages

> **Status: historical.** This document explains why the calculation consumer resolved *during*
> the backtracker's DFS while the constraint and aggregation consumers resolved after. Both
> owners — `analysis/dependency_backtracker.py` and `resolution/producer_resolution.py` — were
> **deleted** by the Item 7 retirement (2026-08-12, `19072ad` / `82c7951` / `882fc8d` /
> `3071fba`) and are not in the tree.
>
> **The distinction this document exists to explain does not survive.** There is no DFS to
> resolve during: the elaborator resolves every reference while building the instance graph, and
> projection reads what it resolved. One stage, not two.
>
> Everything below is retained as the record of the deleted design. It is accurate about the
> two-stage arrangement and is **not a description of what the product does**. It also cites
> `resolution/input_resolver.py`, which was deleted before the recovery began (at `936315c`).
> For the shipped route, read [00-pipeline-overview](00-pipeline-overview.md).

## The Shape

Resolution answers one question for every input: "which real thing produces this
value?" ([03-resolution-overview](03-resolution-overview.md)). Lifecycle Item 2
made it answer that in **one place** — `resolve_producer()` in
`resolution/producer_resolution.py` ([04-producer-resolution](04-producer-resolution.md)).
The calculation, constraint, and aggregation consumers all build a request and
read a result; the ordered `KEY_FORMS` table, the self-reference guard, and the
terminal fork live in that one module.

There is still a real distinction, but it is about **when** a consumer resolves,
not **how**. The backtracker's DFS must resolve a calc binding *during* traversal
to decide whether to recurse:

```python
# dependency_backtracker.py, _trace_dependencies:
resolution = self._resolve_binding_via_registry(binding, usage)  # calls resolve_producer
if resolution.resolution_type == MODULE_OUTPUT:
    producing_usage = self._find_usage_for_channel(resolution.qualified_name)
    self._trace_dependencies(producing_usage, visited, path)  # RECURSE
```

Aggregation modules are discovered differently — by scanning aggregation
expressions — and are built *after* the DFS completes, so their resolution runs
after traversal. Both call the same `resolve_producer()`. The timing differs; the
resolver does not.

FORMULA modules are the one mechanism that does **not** call `resolve_producer()`:
they use a pre-computed [attribute resolution map](16-computed-attributes.md) built
at classification time, where channels are already known.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-DRA-01 | CalcUsage resolution SHALL happen during backtracker DFS; the DFS decision (recurse vs stop) depends on the resolution result. | `_trace_dependencies` calls `_resolve_binding_via_registry` (→ `resolve_producer`); branches on `resolution_type` |
| REQ-DRA-02 | Positive resolution SHALL run through the one shared `resolve_producer()` table for calc bindings, constraint actuals, and aggregation terms. FORMULA SHALL use the pre-computed attribute resolution map. | Call-site inspection; `resolve_producer` is the only positive-resolution entry point ([04](04-producer-resolution.md)) |
| REQ-DRA-03 | Resolution SHALL use typed registries ([10-output-registry](10-output-registry.md)): `scoped_lookup(ScopedKey)` for CHAIN, `sysml_qn_lookup(SysMLQN)` for REFERENCE, `alias_lookup(ScopedKey)` for cross-package. No untyped `dict.get()`. | `KEY_FORMS` lookups use typed accessors; backtracker type-directed dispatch (REQ-BT-08) |
| REQ-DRA-04 | The same reference in the same scope SHALL resolve to the same wiring regardless of which consumer asks — now true by construction, since all consumers run the one table. | `test_shared_producer_convergence.py`; `test_dual_resolution.py` (backtracker/aggregation parity over the corpus) |
| REQ-DRA-05 | A resolution SHALL encode one of {`MODULE_OUTPUT`, `DESIGN_ATTRIBUTE`, `ENTRY_POINT`}, or — under STRICT — raise. | `ProducerResolution.outcome`; STRICT terminal miss raises `CodeGenerationError` |

---

## The Backtracker's Own Dispatch (calc consumer, during DFS)

**When**: during DFS traversal, before graph construction.
**File**: `analysis/dependency_backtracker.py`, `_resolve_binding_via_registry()`
(`:571`), which builds a `LENIENT` `ProducerRequest` and calls `resolve_producer()`
(`:596`).
**Output**: `BindingResolution` stored in `binding_resolutions`, keyed
`"{usage_qn}|{param_name}"`, consumed by `_build_pipeline_module()`
([05](05-module-factory.md#2-calcusage-modules)).

The backtracker still owns the type-directed *pre-classification* of a binding
(CHAIN vs REFERENCE `source_path` shape, REQ-BT-08) and the cross-part binding
rewrites that run before it (below). The ordered lookup itself — scoped, alias,
scoped-alias, SysML-QN, design-attribute, and the name-based lenient forms — is the
shared `KEY_FORMS` table, not a backtracker-private ladder. A `LENIENT` terminal
miss becomes an entry point recorded for V11 coverage (only this consumer records
V11; design invariant I10). See [04](04-producer-resolution.md) for the table, the
self-reference guard, and the terminal fork.

## Cross-Part Wiring: Two Cooperating Resolvers (Item 10)

Distinct from the one resolution *authority* above: a cross-part binding — a
consumer that references a calc output through a nested part — is *prepared* by two
mechanisms that run at different pipeline stages, then resolved by the shared
table. They stay in their existing homes; nothing new is unified here.

**Resolver A — the pre-resolution rewrite (`orchestration/pipeline_builder.py`).**
Before the backtracker runs, `_rewrite_virtual_bindings` rewrites a
`part_usage.attr` binding through the retyped part usage's specialized-def `:>>`
redefinition (the three-tier merge, REQ-VBR-10/REQ-VBR-11,
[12-virtual-binding-rewrite](12-virtual-binding-rewrite.md)), and
`_rescue_self_named_bindings` redirects a self-named `in x = x` to its upstream
EXPOSE. Both mutate `source_path` in place, so the backtracker sees an
already-corrected binding.

**Resolver B — the shared-table lookup.** The (possibly rewritten) CHAIN binding
then resolves through the shared `KEY_FORMS` table's structured `_scoped_alias`
forms (rows 6–9), which `_register_partdef_expose_scoped_aliases`
(`orchestration/pipeline_builder.py`, Step 5.55) populated per design instance for
part-def EXPOSE consumers (REQ-CA-03). Confirmed multi-hop aliases (REQ-CA-10,
[16-computed-attributes](16-computed-attributes.md)) register in the flat alias
registry and are reached by the bare-alias form (row 10), not the scoped-alias
rows.

They compose: Resolver A turns `driver.cost_per_joule` into `driver.meier_cost.gamma`
or a self-named binding into `{instance}.{leaf}`; the shared table wires the result
to the canonical channel. Each is additive (INV-A) — it only adds a hit where the
old ladder fell through to a fallback entry point.

### Offline == Live Parity (D-C)

Resolution must produce the same wiring from a committed snapshot as from a live
extraction (REQ-DRA-04 extended to the offline path). The multi-hop EXPOSE confirm
walk is the risk: M6 serializes the post-confirm `EXPOSE_PURE` state, but the
confirm walk gates on the transient tentative marker, so on reload it would skip
the CA and a naive 2-segment path would resolve the ambiguous terminal through the
first-wins-corrupted flat `_alias` — the wrong channel, a lying sim.
`build_output_registry` reconstructs the pre-confirm tentative state for exactly
the multi-hop candidates before Phase 3
(see [16-computed-attributes](16-computed-attributes.md#multi-hop-expose-tentative-leaf-tag--confirm-pass-req-ca-10)),
so the confirm pass reproduces the live registration order on both paths.

Resolver A splits across the snapshot boundary. The specialized-def rewrite
(`_rewrite_virtual_bindings`) runs at hierarchy-extraction time, so its result is
baked into the recaptured snapshot. The part-def scoped-alias registration and the
self-named rescue need a built registry, so the snapshot path re-runs both on load
— `build_classifier_inputs_from_snapshot` (`snapshot/graph_rebuild.py`) calls
`_register_partdef_expose_scoped_aliases` and `_rescue_self_named_bindings` before
the backtracker, mirroring the live Steps 5.55/5.56.

Alias surfacing has the same both-sites guarantee: `build_computation_graph`
receives `channel_aliases` at both build sites (live
`orchestration/pipeline_builder.py` and snapshot `graph_rebuild.py`), so
`ComputationGraph.output_aliases` is populated identically offline and live.

## Data Models

| Model | File | Role |
|-------|------|------|
| `ProducerRequest` / `ProducerResolution` | `resolution/producer_resolution.py` | The shared request/result for all three consumers |
| `ProducerContext` | `resolution/producer_resolution.py` | Immutable context the table reads (typed OutputRegistry, design-attr map, redefinitions) |
| `BindingResolution` | `core/models.py` | Calc-binding resolution result stored by the backtracker |
| `InputSource` | `resolution/models.py` | The wiring a factory attaches to a `ModuleInput` |
| `BindingInfo` | `extraction/usage_extractor.py` | Calc-binding input |
| `SumTerm` / `SingletonTerm` / `LocalTerm` | `extraction/data_models.py` | Aggregation term inputs |
| `OutputRegistry` | `core/output_registry.py` | Typed registries: scoped, SysML QN, alias, scoped-alias |
| `ScopedKey` / `ScopedAliasKey` / `SysMLQN` / `CanonicalChannel` | `core/identifier_types.py` | Typed keys and values for registry lookups |

---

## Dated history — the pre-unification "two resolvers" story

> **Historical, not current.** Before lifecycle Item 2, this doc described two
> *separate resolvers*: the backtracker's own CalcUsage ladder, and a standalone
> `resolve_input()` in `resolution/input_resolver.py` (with an `AGG_STRATEGIES`
> strategy chain and an immutable `ResolutionContext`) for aggregation. The two
> had drifted apart — different lookup order, guard placement, and terminal
> behavior — and the "two paths, and they must stay that way" framing argued the
> split was structural. Item 2 falsified the *how* half: the split was never
> structural; only the DFS-timing distinction above is. `input_resolver.py`,
> `resolve_input`, `AGG_STRATEGIES`, and `ResolutionContext` were **deleted** and
> replaced by the one `resolve_producer()` table. This block is retained so a
> reader who remembers the old names knows where they went; it describes no live
> code.

## Related Documents

- **Architecture**: [03-resolution-overview](03-resolution-overview.md) — the one question and where each consumer sits
- **Resolver**: [04-producer-resolution](04-producer-resolution.md) — the shared table, guard, and terminal fork
- **Backtracker**: [11-analysis-backtracker](11-analysis-backtracker.md) — DFS algorithm and CalcUsage type-directed pre-classification
- **Factories**: [05-module-factory](05-module-factory.md) — how each consumer feeds module construction
- **Registry**: [10-output-registry](10-output-registry.md) — typed O(1) lookup
- **Data models**: [09-data-models](09-data-models.md) — BindingResolution, InputSource, BacktrackingResult
