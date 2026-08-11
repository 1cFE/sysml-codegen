# Exact-ID Dual-Run Corpus Ledger

- **Observed:** 2026-08-09
- **Command:** `uv run python scripts/run_elaboration_corpus.py`
- **Corpus:** the 37 fixture directories carrying `extraction_snapshot.json`
- **Routes:** shipped `build_pipeline_context` and internal `build_elaborated_pipeline`
- **Authority:** every classification is `[AGENT] (ratified by owner, 2026-08-09)`; the reasons are
  the Phase-5 remediation decisions recorded in `plan.md`

Both routes ran independently from each fixture's SysML. A `graph` is a complete public
`ComputationGraph`; an `error` is a typed boundary outcome. Counts use `m/e/c/a` for modules,
entry points, eligible constraints, and aliases. Difference sections use `M` modules, `E` entry
points, `O` order, `A` aliases, and `C` constraint catalog.

| # | Fixture | Legacy | Exact-ID | Diff | `[AGENT]` class | Basis |
|---:|---|---|---|---|---|---|
| 1 | `agg_literal_probe` | error: `CodeGenerationError` | error: `CodeGenerationError` | — | expected-collapse | Both routes stop at the pre-elaboration calc-def presence gate, so the elaborator never sees the fixture. Not a semantic control — see the B37-01 ruling below. |
| 2 | `agg_localterm_probe` | graph 2/2/0/0 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 replaces the legacy mint. |
| 3 | `alias_agg_probe` | graph 4/3/0/0 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 replaces the legacy mint. |
| 4 | `attr_expr_probe` | graph 16/16/0/3 | graph 17/16/0/3 | M/O | expected-fix | `scaled_area` is modeled runtime behavior that legacy dropped. |
| 5 | `catf_mfe_model` | graph 43/60/0/44 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 replaces the legacy rescue. |
| 6 | `chain_override_probe` | graph 2/3/0/0 | error: 2× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks both rescued sources. |
| 7 | `chain_spike_model` | graph 3/3/0/0 | error: 3× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks all three rescued sources. |
| 8 | `constraint_inline` | graph 2/1/1/0 | graph 2/1/1/0 | M/E | expected-fix | The inline predicate reads its modeled `value` occurrence. |
| 9 | `constraint_multi_instance` | graph 5/1/3/0 | graph 7/3/3/0 | M/E/O | expected-fix | Concrete instances keep independent calculation and constraint sources. |
| 10 | `constraint_non_numerical` | graph 2/1/1/0 | graph 2/1/1/0 | M/E/C | expected-fix | Numerical execution remains; string equality is cataloged as excluded. |
| 11 | `crosspart_rollup_twolevel` | graph 4/2/0/0 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks the base calculation binding. |
| 12 | `d38_caret` | graph 1/1/0/0 | graph 2/6/0/0 | M/E/O | expected-fix | Modeled finite `[count]`, where `count = 4`, expands four occurrences. |
| 13 | `deep_cross_scope_probe` | graph 5/7/0/0 | graph 5/4/0/1 | M/E/O/A | expected-fix | Explicit `:>>` makes the nested witness valid. The exact route keeps one sensor/core occurrence, applies `reading = 10.0`, and wires DCS:82 to the core output; legacy still mints the producer output as a public input. |
| 14 | `expression_binding_probe` | graph 5/7/0/0 | error: 6× `SI_EXPRESSION_SOURCE_UNSUPPORTED` + 3× `SI_SELF_BINDING` | — | expected-collapse | C22 and SRC-01 replace legacy invented inputs. |
| 15 | `fusion_tea` | graph 9/31/1/5 | error: 15× `SI_SELF_BINDING` | — | expected-collapse | The contract requires the customer self-bindings to block. |
| 16 | `gate_a` | graph 3/3/1/0 | error: 2× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks both rescued sources. |
| 17 | `gate_a_package_owner` | graph 3/3/1/0 | error: 2× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks both rescued sources. |
| 18 | `ife_plant` | graph 8/25/0/2 | error: 21× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 replaces legacy per-consumer mints. |
| 19 | `invocation_binding_probe` | graph 1/1/0/0 | error: `SI_EXPRESSION_SOURCE_UNSUPPORTED` | — | expected-collapse | C22 blocks the unsupported invocation source. |
| 20 | `issue22_model` | graph 3/3/0/0 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks the rescued source. |
| 21 | `modeled_default_fidelity` | graph 5/6/3/0 | graph 5/6/3/0 | M/E/O/C | expected-fix | Omitted formals remain visible with resolved scalar or explicit unsupported defaults. |
| 22 | `plant_value_shapes` | graph 6/7/0/0 | error: 2× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks both rescued sources. |
| 23 | `plant_values` | graph 3/5/1/1 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks the viability rescue. |
| 24 | `quoted_owner_formula` | graph 2/2/0/0 | graph 2/2/0/0 | none | expected-collapse | Public module and `_params` group records now agree. |
| 25 | `return_styles` | graph 4/4/0/0 | error: 3× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks three rescued inputs. |
| 26 | `retype_model` | graph 5/4/0/0 | graph 6/6/0/0 | M/E/O | expected-fix | Each occurrence instantiates only its most-specific calculation writer. |
| 27 | `sample_model` | graph 0/0/0/0 | graph 0/0/0/0 | none | expected-collapse | Byte-equal empty control. |
| 28 | `self_named_binding_trap` | graph 1/1/0/0 | error: `SI_SELF_BINDING` | — | expected-collapse | Direct SRC-01 negative. |
| 29 | `self_named_rescue` | graph 2/1/0/1 | error: `SI_SELF_BINDING` | — | expected-collapse | The prohibited rescue is removed. |
| 30 | `shadowed_reference` | graph 1/1/0/0 | graph 1/1/0/0 | M/E | expected-fix | C20 keeps the parser-resolved outer occurrence rather than the inner name match. |
| 31 | `shared_producer` | graph 3/2/1/0 | error: 2× `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks calculation and constraint rescues. |
| 32 | `sibling_channel_ambiguity` | graph 3/2/0/2 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks the same-name rescue. |
| 33 | `solar_battery_model` | graph 36/60/0/1 | error: 24× `SI_SELF_BINDING` | — | expected-collapse | Finite modeled multiplicities expand; the next boundary is the required SRC-01 diagnostic. |
| 34 | `spec_chain_channel` | graph 2/1/0/0 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks the inherited base binding. |
| 35 | `spec_chain_twolevel` | graph 5/3/0/0 | error: `SI_SELF_BINDING` | — | expected-collapse | SRC-01 blocks the inherited base binding; C21 is proven by its clean focused fixture. |
| 36 | `unresolvable_attr_probe` | graph 1/1/0/0 | graph 10/9/0/0 | M/E/O | expected-fix | Nine concrete modeled formulas are runtime behavior that legacy dropped. |
| 37 | `wi014_toy` | graph 4/4/1/1 | graph 4/4/1/1 | M/E | expected-fix | Public names and stable IDs remain compatible; source keys now use concrete occurrences and modeled attributes. |

## Totals

- 37/37 rows have two complete route outcomes; zero rows are unclassified.
- 26 `expected-collapse`; 11 `expected-fix`; zero `needs-review`; zero `new-bug`.
- Exact-ID produced 13 public graphs and 24 typed errors. Legacy produced 36 public graphs and one
  shared no-calculation-definition error.
- Thirteen fixtures produced graphs on both routes. Two are byte-equal (`sample_model` and
  `quoted_owner_formula`); eleven carry reviewed expected fixes.

## B37-01 ruling — `agg_literal_probe` is executable, not a control

**[OWNER 2026-08-10] Modeled aggregation is accepted as executable.** Re-verified on the clean
Item 6 baseline during recovery Phase 2; all four evidence legs matched, so the ruling applies.

Row 1's outcome cells are a true record of the Item 6 measurement and are unchanged. Its original
basis — "equal non-executable control: neither route finds a calculation definition" — was wrong
about *why*, and that wrong reason is what made a real Item 7 behavior change read as a defect:

- The fixture deliberately models a literal-bearing aggregation:
  `:>> total_cost = sum(module.cost) + 5.0;` (`tests/fixtures/agg_literal_probe/library.sysml:24`).
  Its header states the literal is meant to be *observed* (Row-D / REQ-AST-10 probe).
- Item 5 commit `483443e` deliberately made a `:>>` expression redefinition convert into a computed
  calculation node, which is exactly this shape.
- Both routes nonetheless raise `CodeGenerationError: No calculation definitions found in models` —
  legacy at `orchestration/pipeline_builder.py:885`, exact at
  `orchestration/elaborated_pipeline.py:37`. Both are the same pre-elaboration `calc def` presence
  gate. The elaborator is never reached, so this row measures a front-gate, not aggregation
  semantics.

Consequence: when a cutover moves or removes that front-gate, this fixture correctly produces a
graph. That outcome is the ruling being satisfied, not a regression, and it must not be re-filed as
an unexpected `B37-01` result.

**Obligations carried to Phase 3/4** (not discharged here; Phase 2 measures and rules only):

- Restore a literal-bearing aggregation test that asserts the `5.0` operand is observed in the
  produced graph, rather than asserting the fixture collapses.
- Create a genuinely empty control fixture to hold the no-calculation-definition responsibility that
  row 1 was incorrectly serving.
- Do not resolve the `14/22/1` versus `15/22/0` count by preferring whichever is already written
  down; re-derive it from the restored test and control.

## Owner checkpoint resolution

The prior checkpoint questions are resolved by the owner-ratified decisions in `plan.md`:

- Finite modeled multiplicities expand. `d38_caret` now projects, and `solar_battery_model` advances
  to its independently required SRC-01 boundary. Focused C17/C26 fixtures prove the producer-backed
  and literal-backed aggregation behaviors without weakening customer diagnostics.
- C18 is a language load error. The authoritative contract and fixture provenance now preserve the
  parser's missing-feature detail instead of requiring an unreachable codegen policy branch.
- Every former `needs-review` or `new-bug` delta is classified above from its ratified semantic
  decision. DCS:92 remains C5 referent evidence and the focused fixture remains its public
  acceptance. The corrected ratified ruling also supports DCS:82: the repaired valid DCS witness
  projects its one concrete producer edge, while the former invalid part shape now blocks before
  occurrence expansion.

The customer-scale corrected-composition execution proof remains Item 6. This ledger does not begin
that cutover work or change the shipped legacy route.
