# Design: Identifier Sanitization (SC-4 + SC-11 riders)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** cecc76c
**Epic:** UPSTREAM-FINDINGS — Item 5
**Complexity:** MEDIUM (1-day item; one new helper is the only new surface)

---

## Overview

Quoted SysML names (`calc def 'Margin Calc'`) are legal but leak into generated
Python today — `'margin calc'.py` filenames, `class 'Margin Calc'Input`, a registry
importing a class its module never declares. This design sanitizes every emitted
identifier at the **derivation layer** via one new helper, adds a fail-fast for
duplicate output paths across three write key spaces, and closes SC-11 with a
gated post-alias uniqueness re-check.

## Related Artifacts

- **Spec (contract):** `.project/active/identifier-sanitization/spec.md`
- **Spec review + resolutions:** `.project/active/identifier-sanitization/spec-review.md`
- **Research:** `.project/research/20260705_upstream-findings-deep-research.md`
  (SC-4 §137-147, SC-11 §236-240, name-form-mismatch §57-63, fixture blind spot §67)
- **Epic:** `.project/backlog/epic_upstream_findings.md` — Item 5; R1/R2/R3
- **Naming contract:** `docs/architecture/reference/15-naming-conventions.md` (REQ-NC-06);
  `docs/architecture/reference/20-module-registry-generation.md` (REQ-REG-03/04/07)
- **Modeling assumptions:** `docs/architecture/modeling-assumptions.md` §7 (compute once, look up)

## Research Findings

**The split that causes the leak.** `name` is sanitized at capture
(`usage_extractor.py:573` — `sanitize_name(get_calc_def_name(elem))`), but
`qualified_name` is stored raw. The ADR-003 derivation layer then builds identifiers
straight from the raw QN with **no** per-segment sanitize:

- `ModuleType.from_sysml` (`identifier_types.py:104-108`) → `f"{sqn.element_name}Module"`
  and `PythonModulePath.from_sysml` (`:140-143`) → `sqn.element_name.lower()`. Both use
  the **raw** element name. This is the CalcUsage class-name / module-path leak.
- The FORMULA `module_eqn`/channel is derived via `sysml_to_python_qualified_name`
  (`qualified_names.py:103-105`) — a bare `::`→`__` `replace` with no per-segment
  sanitize. Sites: `output_registry_builder.py:124`, `graph_builder.py:745/789/818`.

**Channels (PQN) are already clean** — built per-segment via `build_element_qualified_name`
(`qualified_names.py:39-62`, sanitizes each segment). The defect is confined to the
class-name / module-path / FORMULA-module_eqn derivation.

**The primitive already exists.** `sanitize_name` (`qualified_names.py:13-36`) applies
the 6 REQ-NC-06 transforms to one segment. Its docstring is explicit: it "operates on
individual segments, not qualified names — the `__` ADR-003 separator is applied later"
(the `_+`→`_` collapse at `:31` would eat a `__` separator). An ad-hoc per-segment
sanitize already exists at `graph_builder.py:271-275` (EXPOSE_PURE normalization) —
`"__".join(sanitize_name(seg) for seg in owner.split("::"))`. That expression **is** the
helper this design factors out.

**Why 1,500+ tests missed it.** No baseline model has a quoted **calc def** or a FORMULA
computed attribute on a quoted owner. The 3 snapshots with `formula` classifications
(attr_expr_probe, solar_battery_model, catf_mfe_model) all have unquoted owners; the one
quoted owner in the corpus (`SolarBatteryLibrary::'Solar Array'`) carries only
`expose_pure` attributes, which the `:271-275` normalization already handles.
`alias_agg_probe` has `computed_attributes: []` and never flows through module generation.

## Core Concept

**Sanitize where identifiers are emitted, not where data is captured.** Every Python
identifier — class name, module file path, FORMULA module_eqn/channel — becomes a pure
function of the raw SysML qualified name through a now-sanitizing derivation layer. One
new helper, `sanitize_qualified_name(qn)`, does per-segment sanitize at the `::`→`__`
boundary. It reuses `sanitize_name` (never forks it) and is dropped in at exactly the
FORMULA module_eqn sites; the two `from_sysml` methods sanitize their segments inline
(they also lowercase and append `Module`, so they call `sanitize_name` per segment
directly rather than through the helper).

The **key insight** is that this is a no-op on every unquoted model — `sanitize_name` on
a segment already matching `[A-Za-z0-9_]` returns it unchanged — so all 11 committed
snapshots and all 4 baselines stay byte-identical. The fix only changes output for the
one thing no baseline has: a quoted name reaching identifier derivation.

**Why the derivation layer, not the source.** This is *item-boundary discipline*, not
permanent superiority. Source-sanitizing `owning_part_qualified_name` would flip the
FORMULA registration key at `output_registry_builder.py:130` to sanitized, which forces
the matching lookups (`dependency_backtracker.py:595/:660`, `parameter_groups.py:439`) to
sanitize *in the same change* — and those are exactly the sites Item 7 (SC-8) owns. So
Item 5 takes the name-**emission** slice; the both-sides key sanitization is **deferred**
to Item 7, not rejected. The raw registration key at `:130` staying raw is a **temporary
state**, flipped in lockstep by Item 7 (see Next-Stage Handoff).

This composes with existing pieces and adds no parallel mechanism: `sanitize_name` (the
primitive), the `from_sysml` derivation methods (the emission points), the CLI generation
orchestrator (`cli/__init__.py:717-749`, where the fail-fast pre-pass slots in), and
`_resolve_class_name_collisions` (`registry.py:60-129`, where the SC-11 re-check lands).

## Key Bets

- **B1.** A per-segment sanitize is a no-op on every segment without quotes or special
  characters. *If false → existing snapshots/baselines change, breaking the invariance
  claim the whole direction rests on.*
- **B2.** With M1 applied, producer/consumer channel coincidence is **structural, not a
  bet**: both the *produced* channel (`output_registry_builder.py:124`) and the *consumed*
  channel (`graph_builder.py:745/789`) build the module_eqn leaf from the same
  `ca.python_name`. The residual bet is only **"no derivation site was missed."** *If false
  → a "sanitized-but-mismatched" wire that `ast.parse` passes but never resolves; the new
  fixture's resolved-channel==registered-channel assertion catches it.*
  - **Why this replaces the old bet.** `ca.python_name` is produced by a *second*,
    divergent sanitizer — `expression_compiler._sanitize_name`
    (`expression_compiler.py:167`, consumed at `computed_attribute_extractor.py:226`) —
    which **drops the reserved-word suffix** that `core.sanitize_name` applies
    (`expression_compiler.py:174-175` says so explicitly). So for a FORMULA attr whose name
    sanitizes to a keyword (`class/def/import/from/return/yield`), `core.sanitize_name(name)`
    → `class_` but `python_name` → `class`. Re-sanitizing `ca.name` through the helper at
    the consumer would produce `class_`, mismatching the producer's `class` — a wire that
    matches *today* (both raw) and would **break after the fix**. Building the leaf directly
    from `python_name` (M1) makes the two sides identical by construction and erases the
    keyword edge. The two sanitizers are flagged for eventual consolidation (out of scope).
- **B3.** The `::` raw QN is the sole extraction-boundary form; no downstream consumer
  reads an emitted identifier expecting the raw quoted spelling. *If false → sanitizing
  emission breaks a consumer that matched on the raw form (this is the Item 7 boundary —
  the match sites DO read raw, which is why we leave them raw).*
- **B4.** No committed fixture/baseline hits the SC-11 grandparent-collision case (two
  same-named scopes under different grandparents). *If false → a hard fail-fast turns a
  currently-generating model into an error, breaking byte-identical; the static scan
  (plan phase) demotes the re-check to WARN-first.*

## Key Decisions

- **D1. New `sanitize_qualified_name` helper; leave `sysml_to_python_qualified_name`
  unchanged.** *Rejected: fix `sysml_to_python_qualified_name` in place (per-segment
  sanitize, all uses) — baseline-safe, but it silently does Item 7's behavioral work at
  `dependency_backtracker.py:660` and blurs the item boundary.* The helper is also the
  "shared sanitized-QN matching helper" Item 7 reuses.
- **D2. Pre-generation pass for the duplicate-path fail-fast, covering both key spaces.**
  *Rejected: write-time guard per site — simpler but fails on the second write with a
  worse message; and a module-`full_path`-only pre-pass (the spec's earlier draft) misses
  the schema `calc_def_name.lower()` collision entirely.*
- **D3. Collapse the `graph_builder.py:271-275` EXPOSE_PURE ad-hoc into a helper call.**
  *Rejected: leave the duplication and file a follow-up — the expression is character-for-
  character the helper; leaving it invites drift.*
- **D4. FORMULA channel `module_eqn` sites call the helper; `from_sysml` sanitizes inline.**
  *Rejected: route `from_sysml` through the helper too — it can't, because `from_sysml`
  lowercases package segments and appends `Module`, so it needs `sanitize_name` per
  segment, not the `__`-joining helper.*
- **D5. SC-11 post-alias re-check lands as fail-fast IF the static scan is clean, else
  WARN-first.** *Rejected: unconditional fail-fast (risks B4) or unconditional WARN (leaves
  a silent collision hole the spec wants closed).*

## Architecture

**Data flow (unchanged shape, one transform inserted).** Extraction → analysis →
`ComputationGraph` → generation. The raw `::` QN rides on `CalculationDefinitionData.
qualified_name` and `ComputedAttributeData.owning_part_qualified_name` all the way to
generation. The only change: at the four FORMULA module_eqn sites and inside the two
`from_sysml` methods, the `::`→`__` conversion becomes a per-segment sanitize instead of a
bare replace. Everything downstream (registry, module, stencil, schema rendering) consumes
the already-sanitized identifiers.

**Two boundaries this design does NOT cross:**

1. **The FORMULA registration key** (`output_registry_builder.py:130`) and every
   QN-**matching** site stay raw. The *value* (`:124` channel) is sanitized; the *key*
   (`:130`) is not. Raw-key-to-raw-lookup match is preserved on all models. Item 7 flips
   the key + lookups atomically.
2. **Extraction.** No capture code runs; no snapshot is re-captured. The one new fixture
   is an *additive* live capture, not a re-capture of the 11 existing snapshots.

**The fail-fast pre-pass** sits in the generation orchestrator (`cli/__init__.py`), after
the computation graph is built (`:707`) and **before `_clear_output_directory` (`:709`)** —
so a collision error fires before any existing output is wiped or any file is written. It
iterates `ctx.computation_graph.modules` once, derives every output path in both key
spaces, and raises on the first collision.

## Required Invariants

- **INV-1 (corpus-scoped, not algebraic).** `sanitize_name` is the **identity** on every
  segment appearing in the 11 committed snapshots — verified by scan, not by regex. It is
  NOT identity on all of `[A-Za-z0-9_]+`: `value_`, `_x`, `a__b`, and `class` all match
  that regex yet `sanitize_name` changes them (edge-underscore strip, `_+` collapse,
  reserved-word suffix). The byte-identical guarantee holds because no committed segment has
  a leading/trailing underscore, an internal `__` run, or is a Python keyword. The plan MUST
  re-run this scan (Item 4 churn) and the new FORMULA fixture's *unquoted* segments MUST
  avoid these accidental-change forms (see M3 in Validation Approach).
- **INV-2.** `sanitize_qualified_name` is applied **exactly once**, at the `::`-form → `__`-
  form boundary. It is NOT re-entrant on a `__`-joined string (the `_+`→`_` collapse in
  `sanitize_name` would eat the separator). Idempotence holds per-segment
  (`sanitize_name∘sanitize_name == sanitize_name`), not across the join.
- **INV-3.** The three QN-matching sites (`dependency_backtracker.py:660`,
  `parameter_groups.py:439`, `pipeline_builder.py:70`) and the registration key
  (`output_registry_builder.py:130`) are byte-for-byte unchanged by this item.
- **INV-4.** No EXISTING snapshot (all 11) or baseline (all 4) changes — including
  `alias_agg_probe`'s own snapshot, which holds raw quoted QNs the fix never re-captures.
- **INV-5.** For a FORMULA computed attribute, the channel produced by the registry
  builder equals the channel consumed by the graph builder — structural under M1 (both
  build the leaf from `ca.python_name`). The new fixture asserts the *resolved* input
  channel equals the *registered canonical* channel (the path resolved, not just two
  strings compared).

## Component Overview

- **`sanitize_qualified_name(sysml_qname: str) -> str`** — new helper in
  `core/qualified_names.py`, beside `sysml_to_python_qualified_name`. Splits on `::`,
  `sanitize_name`s each segment, joins with `__`. ~2 lines. Exported in `__all__`.
- **`ModuleType.from_sysml` / `PythonModulePath.from_sysml`** (`core/identifier_types.py`)
  — sanitize element name and package segments inline (`sanitize_name` per segment, then
  `.lower()` for path/namespace). Class name preserves case: `f"{sanitize_name(elem)}Module"`.
- **FORMULA module_eqn sites** — the **owner-QN** segments go through
  `sanitize_qualified_name`; the **leaf** is built from `ca.python_name` **directly** (M1),
  not by re-sanitizing `ca.name`. So `output_registry_builder.py:124` (already uses
  `python_name`) and `graph_builder.py:745/789` become
  `f"{sanitize_qualified_name(owner)}__{ca.python_name}"` — identical by construction.
  `graph_builder.py:818` (`part_eqn`, no leaf) is a straight helper swap.
  `graph_builder.py:271-275` collapses to a helper call. The module_type/class-name at
  `:791` (via `derive_module_type`→`from_sysml` on `ca.name`) is a *different* identifier
  and need not equal `python_name` — it stays sanitized through `from_sysml`.
- **`_check_duplicate_output_paths(modules)`** — new pre-pass in `cli/__init__.py`, called
  **before `_clear_output_directory` (`:709`)** so a collision never wipes existing output
  first (m2). Raises with both raw source names + shared path on collision.
- **SC-11 re-check** — extends `_resolve_class_name_collisions` (`registry.py:60-129`):
  after aliasing, re-group by aliased class name; if any group still has >1 member, WARN or
  raise per the static-scan gate (B4).

## Non-Goals

- Banning quoted names (contradicts REQ-NC-06, fixtures, docs).
- Channel-name (PQN) changes — already per-segment-sanitized; verified, not touched.
- The QN-matching sites and REFERENCE/FORMULA-twin resolution behavior — Item 7 (SC-8),
  including the lockstep flip of `output_registry_builder.py:130`.
- Source-level extraction sanitization; re-capture of any existing snapshot.
- The SC-11 AST import rewrite (substring-based, first-match) — filed as a follow-up.
- Fixing fusion-tea's `sanitize_names.py` — flagged for their coordinated retirement.

## Implementation Notes

**Helper shape (interface, not implementation):**

```python
def sanitize_qualified_name(sysml_qname: str) -> str:
    """Per-segment sanitize a :: QN into a __ EQN. Apply ONCE, at the :: boundary.
    Not re-entrant on __ form (sanitize_name collapses _ runs). Reuses sanitize_name."""
    return "__".join(sanitize_name(seg) for seg in sysml_qname.split("::"))
```

**Segment-order gotcha in `from_sysml`.** For path/namespace segments the current code
does `s.lower()`. Sanitize **then** lower (`sanitize_name(s).lower()`), so the reserved-word
guard sees the pre-lowercased form — matching `build_element_qualified_name`'s existing
per-segment behavior (`qualified_names.py:57`). Do not lower-then-sanitize; it changes the
reserved-word branch for names like `Class`.

**Build the FORMULA module_eqn leaf from `ca.python_name`, never from `ca.name` (M1).**
Make producer and consumer identical by construction:
- `output_registry_builder.py:124` (producer): already
  `f"{sanitize_qualified_name(owner)}__{ca.python_name}"`.
- `graph_builder.py:745/789` (consumer / module identity): build the **same** way —
  `f"{sanitize_qualified_name(owner)}__{ca.python_name}"`. Do **not** write
  `sanitize_qualified_name(f"{owner}::{ca.name}")`; that routes the leaf through
  `core.sanitize_name(ca.name)`, which diverges from `python_name` on keyword names (see
  B2). Only the owner segments go through the helper; the leaf is `python_name`.

This makes B2 structural: a missed site (not a keyword collision) is the only remaining
failure mode, and the fixture's resolved==registered channel assertion is the lock.

**Fail-fast key spaces (two, three write paths):**
- **Modules + stencils** — one key: `_get_python_path(module).full_path` (equivalently the
  `(directory, filename)` pair). Stencils write `{filename}_impl.py` from the same
  `_get_python_path` output (`cli/__init__.py:258/260`), so a module-key collision implies
  a stencil collision — one check covers both. Verify no stencil path is derived elsewhere.
- **Schemas** — separate key: `module.calc_def_name.lower()`, only for modules with ≥2
  outputs (`:175` skip). For calc-usage modules `calc_def_name` is sanitized at extraction
  (`usage_extractor.py:573` on current HEAD — Item 4 churn, re-anchor at implement), so the
  filename is clean; the collision is that `.lower()` maps `Margin_Calc` and `margin_calc`
  to one `margin_calc_output.py` even when module paths differ. (FORMULA modules carry raw
  `calc_def_name=ca.name` but are single-output, so they never reach the schema pass.)

**Raw-name provenance for the error text (m3).** After sanitize the colliding modules share
an identifier, so the message must recover each raw spelling from `PipelineModule`:
`calc_def_qualified_name` (raw) for calc-usage modules, and for FORMULA modules
`calc_def_qualified_name=ca.owning_part_qualified_name` + `calc_def_name=ca.name` (both raw,
verified populated at the FORMULA `PipelineModule(...)` construction in `graph_builder.py`
~`:890-892`). Both fields are non-None for every colliding module type.

**Error text (V-style, names BOTH sources):**
```
Duplicate output path: SysML names 'Margin Calc' and 'margin calc' both derive
modules/aliasaggprobelibrary/margin_calc.py. Rename one, or this would silently overwrite.
```

**REQ / doc numbering** (verified free at HEAD): doc 15 stops at REQ-NC-07, doc 20 at
REQ-REG-07, V-rules at V8 (V9/V10 reserved by Item 4). Assign **REQ-NC-08** (derivation
sanitize), **REQ-NC-09** or a generation-layer REQ (duplicate-path), **REQ-REG-08** (SC-11
re-check). **V11** only if the duplicate-path guard is framed as a model-validation rule —
but it is more naturally a generation-time invariant; recommend a generation REQ, not a V.

## Potential Risks

- **A missed FORMULA site** yields a sanitized-but-mismatched wire (B2). *Mitigation:* the
  new fixture's produced==consumed assertion; enumerate all four sites in the plan.
- **`from_sysml` sanitize accidentally changes an unquoted baseline** if the sanitize/lower
  order differs from today for some segment. *Mitigation:* INV-1 + the byte-identical
  snapshot/baseline gate is the hard stop; run the full suite before and after.
- **SC-11 fail-fast breaks a baseline** (B4). *Mitigation:* the static grandparent-collision
  scan is an explicit plan phase; WARN-first if any hit.
- **Item 7 lockstep missed** — if Item 7 sanitizes `:595` without flipping `:130`, the
  FORMULA REFERENCE match breaks. *Mitigation:* the loud handoff note (below) + close-out.

## Integration Strategy

Drops into the existing derivation layer and generation orchestrator with no new module and
no new data model. The helper joins `sanitize_name`'s family in `qualified_names.py`. The
fail-fast follows the precedent of the SC-2 zero-output fail-fast and
`_validate_channel_references`. The SC-11 re-check extends existing collision-resolution
code. fusion-tea's `sanitize_names.py` becomes dead once this lands — flagged for their
coordinated (reviewed) retirement, not dropped by us.

## Validation Approach

- **`alias_agg_probe` full-generation test (new):** drive the fixture through full registry
  + module generation into `tmp_path` via `run_codegen` (`cli/__init__.py`) from its
  committed snapshot (`--from-snapshot`, the license-free path per `test_snapshot_generation.py`).
  Assert (1) every generated file `ast.parse`s; (2) each class name the registry imports is
  declared by the module file it imports from (import-name match). Locks the CalcUsage
  class-name / module-path leak. R1: real fixture, no mocks.
- **New quoted-owner FORMULA fixture:** minimal model — a quoted-named part def owning a
  FORMULA computed attribute wired to a consumer. Live extraction capture → new committed
  `extraction_snapshot.json` (additive). Conformance test asserts the FORMULA channel is
  **produced and consumed under the identical name** (INV-5), not merely parseable. This is
  the R1 lock for SC #2 — the leak was code-inferred until now.
- **Invariance gate:** the full suite + a byte-diff of all 11 snapshots and all 4 baselines
  shows zero change (existing `_tree_diff` pattern, `test_snapshot_generation.py:50`).
- **Fail-fast tests:** three tests, one per key space (module, stencil-via-module, schema),
  each asserting the error names both sources and the shared path.
- **SC-11:** static scan test proving no committed baseline hits the grandparent case;
  then the re-check test (fail-fast or WARN per the gate).

## Next-Stage Handoff

**Fixed (do not relitigate):** derivation-layer direction; the helper as the only new
surface; `sysml_to_python_qualified_name` left unchanged; the three match sites + `:130`
untouched; per-key-space fail-fast; SC-11 re-check gated on the static scan; one additive
FORMULA fixture.

**Open for the plan:** exact helper location/name confirm (recommend
`core/qualified_names.py`, name as specced); whether the duplicate-path guard is a generation
REQ vs V11 (recommend REQ); the fixture's concrete SysML (quoted part def + one FORMULA attr
+ one consumer).

**De-risk first:** the FORMULA wire (B2/INV-5) — build the fixture and its produced==consumed
assertion before touching the four derivation sites, so the wire is proven, not assumed.

**⚠️ ITEM 7 LOCKSTEP OBLIGATION (must survive to Item 7's spec author).** When Item 7
sanitizes the REFERENCE lookup at `dependency_backtracker.py:595` (reusing
`sanitize_qualified_name`), it MUST flip the FORMULA registration key at
`output_registry_builder.py:130` to sanitized **in the same change** — raw-to-raw becomes
sanitized-to-sanitized atomically — or the FORMULA REFERENCE match breaks. The
`pipeline_builder.py:70` FORMULA-twin match set moves with it. Record this in the Item 5
close-out and the agentic-mbse coordination note.

## Docs & agentic-mbse carry-through

- **Doc 15** (`15-naming-conventions.md`): add REQ-NC-08 (derivation sanitize) and the
  duplicate-path REQ to the table; update §8 to note per-segment sanitize now happens at the
  FORMULA module_eqn sites via `sanitize_qualified_name`, not a bare replace.
- **Doc 20** (`20-module-registry-generation.md`): add REQ-REG-08 (post-alias uniqueness
  re-check); record SC-11 as "confirmed intended, documented, tested" (REQ-REG-03/04/07 PASS).
- **agentic-mbse impact** (Item 12, R2 — recorded, not built): MODELING_GUIDE/sysml-conventions
  gets "quoted names are fine — identifiers are derived"; a Level-2/6 validation-warning
  candidate for two SysML names that sanitize to one Python identifier; the fusion-tea
  `sanitize_names.py` retirement note; the Item 7 lockstep obligation above.

## Appendix: Site-by-site before/after (quoted example)

CalcUsage `AliasAggProbeLibrary::'Unit Cost Calc'`:

| Site | Before (leaks) | After (sanitized) |
|---|---|---|
| `PythonModulePath.from_sysml` | `aliasaggprobelibrary/'unit cost calc'.py` | `aliasaggprobelibrary/unit_cost_calc.py` |
| `ModuleType.from_sysml` | `aliasaggprobelibrary.'Unit Cost Calc'Module` | `aliasaggprobelibrary.Unit_Cost_CalcModule` |

FORMULA attr on owner `QuotedOwnerLib::'Margin Part'`, `name='net margin'`,
`python_name='net_margin'`:

| Site | Before | After |
|---|---|---|
| `output_registry_builder.py:124` module_eqn | `QuotedOwnerLib__'Margin Part'__net_margin` | `QuotedOwnerLib__Margin_Part__net_margin` |
| `graph_builder.py:745` module_eqn | `QuotedOwnerLib__'Margin Part'__'net margin'` | `QuotedOwnerLib__Margin_Part__net_margin` |
| `graph_builder.py:789` module_eqn / `:791` module_type | same leak / via `derive_module_type` | sanitized / via sanitized `from_sysml` |
| `graph_builder.py:818` part_eqn | `QuotedOwnerLib__'Margin Part'` | `QuotedOwnerLib__Margin_Part` |

**Match sites (UNCHANGED, raw on all models):** `output_registry_builder.py:130`
(`SysMLQN(f"{owner}::{ca.name}")`), `dependency_backtracker.py:595` (`SysMLQN(source_path)`),
`dependency_backtracker.py:660`, `parameter_groups.py:439`, `pipeline_builder.py:70`.
On unquoted models the `:124`↔`:130` pairing is raw==sanitized (INV-1), so the raw key still
matches the sanitized value's source. On the new quoted fixture the FORMULA output resolves
via the ScopedKey path (`output_registry_builder.py:137`, `key_f`), which is per-segment
clean — the REFERENCE-QN path that needs `:130` sanitized is Item 7's.

---
**Next Step:** After approval → `/_my_plan` (multi-file item with an explicit static-scan
gate and a de-risk-first ordering — warrants a checkboxed plan over direct implement).
</content>
</invoke>
