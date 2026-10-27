# Named-subset double counting: findings

Read-only investigation run by a subagent on 2026-10-26 at `b4ba01fc` (stock, and with the leak investigation's `fix.patch`). Recorded here by the orchestrator from the subagent's report. Probe models are in `shapes/` and scripts in `scripts/` beside this file; generated packages and TEAx runs were in `/tmp/claude-1000/double-count/` (temporary).

## Answer

In SysML, `part server_1 :> servers;` names one of the members of `servers`; it does not add one. The generator builds every named subset as an extra copy beside the indexed ones (`servers[0]`, `servers[1]`, `server_1`, ...), and a `sum()` over the collection adds only the indexed copies, which hold defaults, and leaves out the named parts and their values. Both happen on stock code. dc3 is not affected today.

## SysML meaning

KerML 7.3.4.4 Subsetting (`agentic-mbse/docs/sysmlv2/SysML_KerMLSpec/full_document.md:1617`): "the values of the subsetting feature are also values of the subsetted feature on each instance (separately)"; the example at `:1637-1640` has `driveWheels[2] subsets wheels[4]` as two of the four wheels; formal semantics at `:5448`. KerML does not require two named subsets to be distinct members; with different values they must be. SysIDE's docs (`agentic-mbse/docs/syside/examples/unit_evaluation.md:19, :129`) say subsetting "could lead to multiple possible values" and write membership out (`part redefines subcomponents = (chassis, engine);`).

## Native SysIDE 0.8.4

Cannot settle it: `sum(servers.power)` with the rack as scope gives 10.0 in every shape (it neither expands the multiplicity nor collects subset members). It gives 35.0 only with membership written out (`part :>> servers = (server_1, server_2);`).

## What the generator builds (stock; `Server.power default 10.0`, `Rack.total = sum(servers.power)`, run in real TEAx)

| Shape | Parts built in the rack | Terms in the sum | Generated | SysML implies |
|---|---|---|---|---|
| No subsets, `[2]` (s6) | `servers[0..1]` | both | 20 | 20 |
| One named subset (15), `[2]` (s1) | `servers[0..1]`, `server_1` | indexed only | 20 | 25 |
| Two named subsets (15, 20), `[2]` (s2) | `servers[0..1]`, `server_1`, `server_2` | indexed only | 20 | 35 |
| Named subsets, `[*]` (s3) | refused `SI_MULTIPLICITY_UNRESOLVED` | | | 35 if named parts are the only members |
| dc3 shape (s4): library `racks[*]`, `part :>> racks[2]` in a specializing def, `rack_1`/`rack_2 :> racks` | `racks[0..1]`, `rack_1`, `rack_2` | indexed only | 20 | 35 |
| Same, no default (s9) | same | same | builds with two `null` inputs; 15 and 20 ignored | 35 |
| dc3 nested form, `racks[2] { servers[0]; }`, rack-level sum (s5) | refused `SI_OCCURRENCE_MISSING` | | | |

With the leak fix, `nested_named_subset` builds 12 PSUs where the model has 4. `plain_nesting`, `one_subset_redefines` and `outer_redefinition` already build 11-12 PSUs on stock.

Two related wrong numbers with a different cause, both building on stock, no backlog row:
- A redefinition that doesn't restate its count drops it: `part :>> servers { :>> power = 15.0; }` in a `Server[2]` gives one copy, total 15 where SysML implies 30 (s8).
- The written-out membership form is ignored: `part :>> servers = (server_1, server_2);` collapses to one default copy, total 10; native gives 35 (s7).

## dc3 impact: none today

Regenerating dc3's models gives a package identical to the committed `exploration/ac_dc_baseline/dc3_baseline/`, stock and with the leak fix. Its occurrence index (153 entries) holds the extra indexed copies beside 28 named subsets, but no dc3 model reads a whole collection (no `sum(`, `size(` or collection-wide read), and no generated file mentions an indexed path. dc3 sets every count to exactly its number of named members (`racks[2]` with 2, AC `path_elements[6]` with 6, DC `[5]` with 5). Risk: a future rollup such as `sum(path_elements.capital_cost)` would build silently over the extra copies with `null` inputs.

## Cause (`elaboration/occurrence.py`)

- Subsetting is never read: `build_feature_slot_index` follows only `owned_redefinitions` (`:396`), so `server_1 :> servers` gets its own slot.
- `native_child_declarations` (`:946-981`) groups part usages by slot and keeps one per slot (`:975-976`), so both `servers` and `server_1` survive as children.
- `_multiplicity_indices` reads only the usage's own multiplicity (`:833`); with none written it returns one unindexed copy (`:835`). The same line causes s8.
- `resolve_address` collects members by slot (`children_for_slot`, `:602`), so a sum finds `servers[0..1]` and never `server_1`.

This breaks ADR 0004 ("exactly one concrete occurrence, a modeled plural result, or a named refusal"), which also rules out choosing by arrival order.

## Options

- **A. Named subsets count as members.** A named subset of a fixed-count collection under the same parent becomes one of the `n`; build only `n − k` unnamed copies, and collection lookup also returns children that subset the slot. Don't assign named parts index positions (that would be order-based choice). Still refuse: more named subsets than the count, a subset of a subset, and probably `[*]` (treating named parts as the only members goes beyond SysML; owner call). Changes: dc3's extra copies disappear (expected no file change, not checked); `plain_nesting`, `one_subset_redefines`, `outer_redefinition` shrink (12 PSUs to 4); the three leak fixtures build with the right count; `occurrence_seed/f1_effective_declaration_slot` changes. Larger change.
- **B. Refuse a named subset beside indexed copies of the collection it subsets.** Small; dc3 refuses (all 28 named subsets) until it drops the subsetting; the three generating fixtures flip to refused.
- **B′. Refuse only when a computed value reads such a collection.** dc3 builds; the wrong sums become refusals; the extra per-copy inputs and outputs remain.

None fixes s7 or s8.

## Not checked

No fix prototyped; no suite or lane run on a change; only `fixture_classes.json` fixtures, `refusal_cases` and dc3 scanned (four unparseable fixtures skipped); constraints on extra copies; units; smart regeneration; whether `comp_b :> comp_a` should inherit `comp_a`'s nested redefinition.
