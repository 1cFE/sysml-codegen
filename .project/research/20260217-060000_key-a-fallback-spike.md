# Key_A Fallback Removal Spike — The Design Docs Are Wrong

**Date**: 2026-02-17
**Commit under review**: 86cf995 (docs-only: prohibit silent Key_A fallback)
**Branch**: cost-pattern-refactor
**Spike test**: `tests/spikes/test_key_a_fallback_usage.py`

## Scope

This report audits the design docs in `.project/concepts/refactor-design-intent/`
against the current production code and empirical spike results. All code
references are to current production (`src/sysml_codegen/`). All doc references
are to the design intent corpus (`refactor-design-intent/`).

## Question

Commit 86cf995 formalized REQ-OR-08 and REQ-BT-08 in the design docs, which
say Step 1 in `_resolve_binding_via_registry()` should raise
`UnscopedResolutionError` instead of silently returning. The commit is
docs-only — no production code changed.

**Will the pipeline work if we implement REQ-BT-08 as written?**

## Answer

**No. Implementing REQ-BT-08 as written would break 12 correct resolutions
across 2 models.**

The design docs misidentify what Step 1 does. The requirements are written
against the wrong target. This report documents the precise gaps.

---

## Definitions: Where Steps and Keys Are Specified

### Resolution steps (defined in `11-analysis-backtracker.md`)

The backtracker's `_resolve_binding_via_registry()` tries steps in order.
First match wins. Production code: `dependency_backtracker.py:477-577`.

| Step | Doc name | Production code (lines) | What it does |
|------|----------|------------------------|-------------|
| 0 | "Scoped resolve" | 510-519 | `consumer_scope + "." + source_path` → registry lookup. Skips `::` paths. |
| 1 | "Direct registry resolve (unscoped fallback)" | 521-523 | `registry.resolve(source_path)` — flat `dict.get()` against entire index |
| 1b | "SysML QN normalization + retry" | 525-533 | Converts `::` to dotted, retries |
| 2 | "REFERENCE secondary resolution" | 545-547 | Leaf + parent scope for `BindingType.REFERENCE` only |
| 3 | "Design attribute resolution" | 557-565 | Matches design_attrs dict → ENTRY_POINT |
| 4 | "Fallback entry point" | 567-577 | Guaranteed ENTRY_POINT with warning |

### Aggregation resolution (in graph_builder, NOT the backtracker)

The graph_builder has a separate resolution path for aggregation inputs.
Production code: `_resolve_aggregation_input_channel()` in
`graph_builder.py:760-865`. Two-step cascade:

| Step | Production code (lines) | What it does |
|------|------------------------|-------------|
| Scoped | 840-849 | `dotted_scope + "." + part_usage + "." + attr` → registry lookup |
| Unscoped (Key_D) | 851-859 | `part_usage + "." + attr` → registry lookup. Comment says "Unscoped Key_D fallback" |

### FORMULA resolution (in graph_builder, NOT the backtracker or registry)

FORMULA modules do NOT resolve through the registry at all. They use a
pre-computed attribute resolution map: `_build_attribute_resolution_map()`
in `graph_builder.py:585-640`. The one exception is `_resolve_expose_pure()`
(`graph_builder.py:543-582`) which constructs `{instance_name}.{output_attr}`
and looks it up in the registry — this is Key_A format.

### Registry key formats (defined in `10-output-registry.md` and `15-naming-conventions.md`)

The design docs define these named formats in REQ-OR-05 and the Phase 1a/1b/1c
tables. Production code: `build_output_registry()` in `initialization.py:502-660`.

**Phase 1a — CalcUsage outputs** (`initialization.py:538-548`):

| Key | Format | Example | Scope-ambiguous? |
|-----|--------|---------|-----------------|
| Key_A | `{instance_name}.{attr}` | `lcoe.lcoe_per_mwh` | **YES** — collides when two scopes have same instance name |
| Key_B | canonical EQN (self-registered) | `SBD__sbp__lcoe__lcoe_per_mwh` | No — globally unique by construction |
| Key_C | dotted hierarchy, design prefix stripped | `solar_battery_plant.lcoe.lcoe_per_mwh` | No — derived from EQN |

**Phase 1b — Aggregation outputs** (`initialization.py:551-584`):

| Key | Format | Example | Scope-ambiguous? |
|-----|--------|---------|-----------------|
| Key_D | `{part_usage}.{attr}` | `solar_array.total_capex` | **YES** — same risk as Key_A |
| Key_E | full dotted instance path | `SBD.sbp.solar_array.total_capex` | No |
| Key_E_stripped | Key_E minus `segments[0]` | `sbp.solar_array.total_capex` | No |
| bare | just attribute name | `total_capex` | **YES** — maximally ambiguous |
| alias variants | same 4 patterns per `expression.aliases` entry | varies | Same as above |

**Phase 1c — FORMULA outputs** (`initialization.py:587-605`):

| Key | Format | Example | Scope-ambiguous? |
|-----|--------|---------|-----------------|
| Key_F | `{owning_part}.{python_name}` | `Solar_Array.panel_cost` | Same risk as Key_A |
| bare | just python name | `panel_cost` | **YES** |
| SysML QN | `{part_qn}::{name}` | `AttrExprProbeDesign::probe_design::area` | No — fully qualified |

**Phases 2-4 — Aliases** (`initialization.py:608-660`):

| Phase | Source | Format | Scope-ambiguous? |
|-------|--------|--------|-----------------|
| 2 | CHAIN redefinition | varies (resolved before registering) | No — references existing canonical |
| 3 | EXPOSE_PURE | `{owning_part_short}.{alias_name}` | No — part-scoped |
| 4 | Transitive design attr | varies | No — rare (2 across all models) |

The docs flag these for removal in Phase 7.4: bare-name registration keys,
SysML QN normalization (Step 1b). The SysML QN **registration** (Phase 1c)
is not flagged for removal but contradicts REQ-NC-07 (see Finding 3).

---

## Spike Results

### Method

The spike (`tests/spikes/test_key_a_fallback_usage.py`) instruments the
backtracker's resolution cascade to record which step resolved each binding,
**and which key format that step hit**. It runs against all 6 extraction
snapshots without SysIDE.

A second analysis traces the graph_builder's aggregation resolution path
(`_resolve_aggregation_input_channel`) to determine which key format it hits
for each SumTerm and SingletonTerm.

### Backtracker results (CalcUsage resolution)

| Model | Total bindings | Step 0 (scoped) | Step 1 (unscoped) | Step 1b | Step 2 | Step 3 | Step 4 |
|-------|---------------|-----------------|---------------------|---------|--------|--------|--------|
| solar_battery | 16 | 4 (25%) | **0** | 1 | 1 | 0 | 10 |
| chain_spike | 6 | 3 (50%) | **0** | 0 | 0 | 0 | 3 |
| catf_mfe | 122 | 20 (16%) | **10 (8.2%)** | 0 | 0 | 90 | 2 |
| attr_expr_probe | 3 | 0 | **2 (67%)** | 0 | 0 | 1 | 0 |
| sample | 3 | 0 | **0** | 0 | 0 | 0 | 0 |
| issue22 | 3 | 0 | **0** | 0 | 0 | 0 | 0 |

**Which key format each step hit:**

| Resolution path | Key format hit | Count | Models |
|----------------|---------------|-------|--------|
| Step 0 (scoped) | Key_C | 27 | solar_battery, chain_spike, catf_mfe |
| Step 1 (unscoped) | EXPOSE_PURE alias | 10 | catf_mfe |
| Step 1 (unscoped) | SysML QN | 2 | attr_expr_probe |
| Step 1 (unscoped) | Key_A | **0** | — |
| Step 1b | Key_E_stripped | 1 | solar_battery |
| Step 2 | (composite) | 2 | solar_battery, issue22 |
| Step 3 | (design_attrs dict) | 91 | catf_mfe, attr_expr_probe |
| Step 4 | (fallback) | 16 | solar_battery, chain_spike, catf_mfe, issue22 |

### Aggregation results (graph_builder resolution)

solar_battery is the only model with aggregation data (20 aggregation
expressions, 46 SumTerm + SingletonTerm inputs).

| Resolution path | Count |
|----------------|-------|
| Scoped (Key_E_stripped / CHAIN alias) | 46 |
| Unscoped Key_D fallback | **0** |
| Unresolved | 3 |

**Key_D fallback: zero hits.** The scoped path handles all 46 aggregation
term resolutions.

---

## FINDING 1: The 12 Step 1 hits are NOT Key_A. Zero Key_A hits observed.

The docs call Step 1 "Key_A fallback" (`11-analysis-backtracker.md` REQ-BT-08,
section header). This is wrong. Step 1 is `registry.resolve(source_path)` — a
`dict.get()` against the entire registry index. It hits whatever key matches.

**Of the 12 Step 1 hits, zero are Key_A.** Breakdown:

### catf_mfe: 10 hits — all Phase 3 EXPOSE_PURE aliases

These are cross-package CHAIN bindings. The consumer is in one SysML package,
the producer in a different package. Traced example:

```
Producer:  CATFMFERadialBuild__catf_radial_build__magnet_surface_calc
  Key_A for this producer = "magnet_surface_calc.area"
  Key_C for this producer = "catf_radial_build.magnet_surface_calc.area"

Consumer:  CATFMFEMagnets__catf_tf_system__cryo_load
  consumer_scope = "catf_tf_system"
  source_path   = "catf_radial_build.magnet_surface_area"

Step 0 constructs: "catf_tf_system.catf_radial_build.magnet_surface_area"
  -> None (catf_radial_build is NOT a child of catf_tf_system)

Step 1 looks up: "catf_radial_build.magnet_surface_area"
  -> MATCH: Phase 3 EXPOSE_PURE alias
  -> This is NOT Key_A. Key_A is "magnet_surface_calc.area" — a different string.
```

Step 0 structurally cannot work here. The consumer and producer are in
different packages. The consumer's scope does not contain the producer.
Prepending it produces a key that will never exist.

All 10 hits follow this pattern — cross-package references resolving through
EXPOSE_PURE aliases registered in Phase 3.

### attr_expr_probe: 2 hits — both Phase 1c SysML QN keys

```
Consumer:  AttrExprProbeDesign__probe_design__scale_calc
  source_path = "AttrExprProbeDesign::probe_design::area"

Step 0: skipped (source_path contains "::", explicit guard in code line 512)
Step 1: "AttrExprProbeDesign::probe_design::area" -> MATCH
  This is a Phase 1c SysML QN key. Not Key_A.
```

These are fully-qualified SysML names. They contain `::`. They are not
`{instance_name}.{attr}` format. They are globally unique by definition.

---

## FINDING 2: The docs conflate "Step 1" with "Key_A" throughout

Step 1 is a flat `dict.get()` against the entire registry. The registry
contains Key_A, Key_B, Key_C, Key_D, Key_E, Key_E_stripped, Key_F, bare names,
SysML QN keys, CHAIN aliases, EXPOSE_PURE aliases, and transitive aliases.
Step 1 does not distinguish between them.

The docs treat Step 1 and Key_A as synonymous. Exact quotes:

**`11-analysis-backtracker.md`, REQ-BT-08 (line 26):**
> "Step 1 (unscoped Key_A fallback) SHALL raise `UnscopedResolutionError`"

**`11-analysis-backtracker.md`, section heading (line 89):**
> "Step 1: Unscoped Key_A guard (REQ-BT-08) — RAISES ERROR"

**`10-output-registry.md`, REQ-OR-08 (line 30):**
> "Key_A SHALL be registered for diagnostic visibility but SHALL NOT be used
> as a silent resolution fallback."

**`03-resolution-overview.md`, REQ-RES-07 (line 65):**
> "Unscoped Key_A fallback is prohibited — if scoped resolution fails but
> unscoped Key_A would match, the system SHALL raise UnscopedResolutionError"

**`24-dual-resolution-architecture.md`, strategy table (line 125):**
> "Direct lookup (Key_A guard) | Stage 1 (RAISES on hit — REQ-BT-08)"

REQ-OR-08 says "resolution paths that would match Key_A SHALL raise." But
Step 1 doesn't match Key_A — it matches **any key**. The proposed pseudocode
in `11-analysis-backtracker.md` lines 91-104 raises on `channel is not None`
— i.e., on any match at all, not only Key_A matches:

```python
channel = self._output_registry.resolve(source_path)
if channel is not None:        # <-- raises on ANY match, not just Key_A
    raise UnscopedResolutionError(...)
```

This would raise on the 10 EXPOSE_PURE alias hits and 2 SysML QN hits that
are correct resolutions.

---

## FINDING 3: REQ-NC-07 contradicts `10-output-registry.md` Phase 1c

`15-naming-conventions.md`, REQ-NC-07:
> "Registry keys SHALL use dotted format; no `::` keys are registered"

`10-output-registry.md`, Phase 1c table:
> | SysML QN | `{owning_part_qn}::{name}` |

Production code (`initialization.py:600-602`):
```python
sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
keys.append(sysml_qn)
```

Empirical: 14 SysML QN keys with `::` registered in attr_expr_probe. Bindings
resolve through them. REQ-NC-07 is factually wrong about the current code, and
`10-output-registry.md` describes the `::` registration that REQ-NC-07 says
doesn't exist.

---

## FINDING 4: Key_A ambiguity IS real, but Step 0 handles it

Key_A collisions exist. catf_mfe build logs:

```
OutputRegistry key collision: 'pump_load.pump_power' already maps to
  'CATFMFEBlanket__catf_blanket__pump_load__pump_power',
  refusing to overwrite with
  'CATFMFEVacuum__catf_vacuum_pumping__pump_load__pump_power'

OutputRegistry key collision: 'minor_calc.a' already maps to
  '...plasma_region__minor_calc__a',
  refusing to overwrite with '...vacuum_gap__minor_calc__a'
  (10+ collisions across plasma_region, vacuum_gap, first_wall, blanket, etc.)
```

These are exactly the ambiguity the design docs describe. But the bindings
that reference these colliding instance names are all intra-scope CHAIN
bindings where Step 0 (scoped) resolves them correctly before Step 1 is
reached.

**The dangerous scenario — Step 0 fails AND Step 1 hits a colliding Key_A —
has zero occurrences across all 6 models.**

---

## FINDING 5: Most key formats are dead weight

Across both the backtracker (CalcUsage) and graph_builder (Aggregation)
resolution paths, here is which key format is actually hit by a binding
resolution:

| Key format | Backtracker hits | Graph_builder agg hits | Graph_builder FORMULA | Status |
|-----------|-----------------|----------------------|----------------------|--------|
| **Key_C** | 27 | — | — | **Load-bearing** (primary backtracker path) |
| **Key_E_stripped** | 1 | 46 | — | **Load-bearing** (primary aggregation path) |
| **CHAIN aliases** | (hit via Step 0 scoped keys) | (hit via scoped keys) | — | **Load-bearing** (scoped keys match these) |
| **EXPOSE_PURE aliases** | 10 | — | — | **Load-bearing** (only path for cross-package refs) |
| **Key_B** | 0 | 0 | — | **Needed for setup** (Phase 2-4 alias registration calls `registry.resolve(canonical)`) |
| **Key_A** | **0** | **0** | Used by `_resolve_expose_pure()` line 573 | **One consumer.** `_resolve_expose_pure()` constructs `{instance}.{attr}` directly. |
| **Key_D** | — | **0** | — | **Dead.** Unscoped fallback in `_resolve_aggregation_input_channel` line 852. Scoped path handles all 46 terms. |
| **Key_E** | **0** | **0** | — | **Dead.** No code path constructs a key that would match this format. |
| **Key_F** | **0** | — | FORMULA bypasses registry | **Dead.** FORMULA uses `_build_attribute_resolution_map`, not registry lookup. |
| **bare** | **0** | **0** | — | **Dead.** Already flagged `REMOVAL_CANDIDATE` in design docs. |
| **SysML QN** | 2 | — | — | **Contradicts REQ-NC-07.** Could move to Step 1b normalization if `::` registration removed. |

**5 key formats are load-bearing: Key_C, Key_E_stripped, CHAIN aliases,
EXPOSE_PURE aliases, Key_B (for setup).** Key_A has exactly one consumer
(`_resolve_expose_pure` in graph_builder).

**5 key formats are dead: Key_D, Key_E, Key_F, bare, SysML QN.** They are
registered but no resolution code path ever constructs a lookup that hits them.
They exist as fallbacks for cases that never occur.

Key_D deserves specific mention: it is `{part_usage}.{attr}` — the aggregation
equivalent of Key_A. The code at `graph_builder.py:851` explicitly labels it
"Unscoped Key_D fallback." It has the same scope-ambiguity problem as Key_A.
And like Key_A in the backtracker, it has **zero hits** because the scoped path
(Key_E_stripped) handles everything.

---

## What the design docs must fix

### 1. REQ-BT-08 is wrong as written

The requirement says "Step 1 SHALL raise `UnscopedResolutionError` instead of
silently returning a result." Step 1 is a flat `dict.get()`. The requirement
should say what it means: raise when the unscoped match is **a Key_A entry
specifically**, not any match. The proposed pseudocode raises on
`channel is not None` which catches all keys, not just Key_A.

**Affected docs:** `11-analysis-backtracker.md` (REQ-BT-08, Step 1 section,
proposed pseudocode, concrete walkthrough), `24-dual-resolution-architecture.md`
(REQ-DRA-03, Stage 1 description, strategy table), `COMPONENT_CHECKLIST.md`
(C11 acceptance criteria).

### 2. REQ-OR-08 scope is unclear

The requirement says "resolution paths that would match Key_A SHALL raise an
error instead." This is ambiguous: does it mean raise when the lookup key is
in Key_A format, or raise when the lookup happens to hit a Key_A entry in the
dict? The former requires the backtracker to classify the source_path format.
The latter requires the registry to track which keys are Key_A entries.
Neither is specified.

**Affected docs:** `10-output-registry.md` (REQ-OR-08), `03-resolution-overview.md`
(REQ-RES-07).

### 3. REQ-NC-07 is factually wrong

"No `::` keys are registered" — the production code registers them, the
design doc (`10-output-registry.md`) describes the registration, and bindings
resolve through them. Fix REQ-NC-07 or remove the `::` registration.

**Affected docs:** `15-naming-conventions.md` (REQ-NC-07, line 92 prose).

### 4. Step 1 analysis omits EXPOSE_PURE and SysML QN paths

The design docs analyze Step 1 purely through the lens of Key_A ambiguity.
They do not account for the fact that Step 1 is the only resolution path for:
- Cross-package references (resolved via Phase 3 EXPOSE_PURE aliases)
- REFERENCE bindings with `::` source_paths (resolved via Phase 1c SysML QN keys)

These paths are correct, load-bearing, and would break under REQ-BT-08.

**Affected docs:** `11-analysis-backtracker.md` (Step 1 section, concrete
walkthrough), `24-dual-resolution-architecture.md` (Stage 1 analysis).

### 5. Dead key formats should be acknowledged and scheduled for removal

Key_D, Key_E, Key_F, bare names, and SysML QN registration are dead weight.
They are registered but never hit by any resolution path. They exist as
unscoped fallbacks for cases that the scoped paths already handle. The design
docs should explicitly flag them for removal alongside the existing
`REMOVAL_CANDIDATE` annotations for bare-name handling and Step 1b.

**Affected docs:** `10-output-registry.md` (Phase 1a/1b/1c tables),
`15-naming-conventions.md` (Section 7 key format tables).

---

## Recommendations

### Do not implement REQ-BT-08 as written

It will break catf_mfe (10 bindings) and attr_expr_probe (2 bindings).

### To actually guard against Key_A ambiguity

The registry needs to track which keys are Key_A entries. Then the guard
can be precise:

```python
# Step 1: unscoped resolve with Key_A guard
if channel is None:
    channel = self._output_registry.resolve(source_path)
    if channel is not None and self._output_registry.is_key_a(source_path):
        raise UnscopedResolutionError(...)
    # Phase 3 alias, SysML QN, etc. — safe, proceed
```

This requires `OutputRegistry` to maintain a `_key_a_keys: set[str]` populated
during Phase 1a registration.

### Remove dead key registrations

Stop registering Key_D, Key_E, Key_F, bare names, and SysML QN keys. This
shrinks the registry, eliminates ambiguous fallback keys, and makes the
remaining key formats' purpose clear. Validate with the spike test after
each removal.

### Amend the design docs before implementing any resolution changes

The requirements, the analysis, and the proposed pseudocode are all written
against "Key_A fallback" when the mechanism is "unscoped dict lookup against
everything." Fix the docs to match reality before writing code against them.

---

## Spike test

Reusable for validating future changes:

```bash
uv run pytest tests/spikes/test_key_a_fallback_usage.py -s -v
```

- `test_key_a_fallback_not_needed[model]` — asserts 0 Step 1 hits per model
- `test_full_resolution_report` — prints full breakdown across all models
