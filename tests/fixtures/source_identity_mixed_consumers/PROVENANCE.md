# Provenance — SOURCE-IDENTITY Item 4 foundation fixture

Authored for Item 4 Phase 1 (extraction-evidence foundation) against the ratified lifecycle
contract's "Source-identity scenarios" (Appendix C). One exact supported route per assigned
cell, in one model, rather than one fixture per consumer — the plan's anti-duplication rule.
All authored forms are inside the supported executable subset; unsupported forms live in
isolated fixtures (`source_identity_indexed_source`, `expression_binding_probe`,
`self_named_binding_trap`) so this model stays full-pipeline capable.

## Route → cell map (exact keys)

| Route (package member) | Cell | Key realized |
|---|---|---|
| `'Twin Bay'`: `sensor_a`/`sensor_b` (`:>> reading = 11.0 / 22.0`), `calc_a`/`calc_b` chains | C8 | one definition (`'Twin Sensor'::reading`), two concrete occurrences, distinct occurrence `:>>` overrides, one chain calculation per occurrence |
| `'Station'`: `rig` (`:>> gain_setting = 42.0`), `chain_calc` + `chain_guard` + `:>> station_total` | C11 | feature chain × 1 calc + 1 constraint + 1 aggregation, single occurrence override |
| `'Qual Plant'` / `'Qual Station'`: `'Qual Plant'::level` bindings, `qual_plant` (`:>> level = 70.0`) | C12 | owner-qualified (definition qualifier) × mixed consumers; def-level referent, occurrence bridge required |
| `'Bare Station'`: bindings authored inside concrete usage `bare_rig` (`:>> intensity = 30.0`) | C13 | bare renamed (usage context) × mixed consumers |
| `'Parent Unit'`: `shared_rate`, child-part `child.child_calc`, parent-owned `parent_guard` + `:>> parent_total` | C15 | cross-owner parent attribute; parent-owned aggregation + constraint + child-part calculation |
| `'Computed Station'`: `source_identity_computed.producer_calc.result` chains (calc + constraint + aggregation) | C24 | feature chain to computed output `'Source Identity Producer'::result` on concrete calc usage `source_identity_computed.producer_calc` — the contract's published names, verbatim |
| `'Avail Plant'` / `'Avail Design Ctx'`: `def_authored_calc` (def context) + `usage_authored_calc` (usage context), `avail_plant` (`:>> availability = 0.8`) | C25 | bare renamed × mixed definition/usage binding contexts × single-occurrence `:>>` override × 2 calculations |
| `'Stamp Plant'` + package-level `stamp_plant` (`:>> efficiency = 0.75`) | C1-kin | Path-A stamp route: the legacy VBR literal-stamps the def-context bare-renamed binding; its immutable evidence must keep the reference form |
| `'Stamp Plant'::lit_calc` (`in value_in = 9.5`) | C16-kin | authored usage literal — must remain distinguishable from the stamped reference-derived literal |
| `'Bank'`: `:>> bank_total = sum(cell.cell_cost)` over `cell : 'Bank Cell'[3]` | agg evidence | sum() term retains the exact resolved leaf target before names are rendered |
| `'Deep Design'`: `station_two` (`:>> rig.gain_setting = 43.0`) | C19-kin | deep-path occurrence override captured with exact chained target QNs (value-site evidence; the C19 repair itself stays on `nested_occurrence_override_probe`) |

## Interpretation notes (surfaced, not silently resolved)

- **C15 child leg form.** The cell name says "chain × cross-owner"; the child-part
  calculation here reaches the parent attribute by bare renamed reference (`in value_in =
  shared_rate`), the supported form for an enclosing-feature referent — an upward feature
  chain does not exist in KerML. The chain legs of this fixture (C11, C24) cover the chain
  form itself. If Phase-5 acceptance mapping needs the C15 key's authored form read
  differently, reconcile there rather than silently here.
- **C25 referent classes.** The def-authored leg resolves to the def-level feature
  (`'Avail Plant'::availability`); the usage-authored leg resolves occurrence-level.
  Extraction evidence records both referent classes; their convergence on one occurrence is
  the Phase-2/3 authority's job, not extraction's.

## Phase-1 consumers

`tests/conformance/test_source_identity_extraction.py` (live, `@requires_license`): target
fidelity per route, deep-chain (3-segment) resolution via the C24 route, redefinition
value-site identity, post-rewrite evidence immutability via the Path-A stamp route.
Phase 2 reuses the same routes for contextual occurrence projection.

No extraction snapshot is committed for this fixture in Phase 1; the atomic v6
recapture (Phase 4) owns snapshot registration.
