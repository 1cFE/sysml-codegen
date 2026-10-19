# Changed outputs

Every change 2a makes to text the generator prints, by step. What the generator accepts or refuses does not change (RG-1); the 22 committed v6 snapshots stay byte-identical to `d73a4fc5`.

## P1.3: the reason suffix

A refusal whose carrier has a site reason now ends its message in ` (reason: <id>)`. The suffix is added in two renderers, `_render_readiness_finding` and `_render_public_diagnostic` (`src/sysml_codegen/elaboration/elaborate.py:143`, `:210`, through `_reason_suffix` at `:147`). Nothing else in the message changes.

`CodeGenerationError` text does not change. Its new `code` and `reason` fields reach the log only as structured data (`extra={"refusal": ...}`), so generation-stage refusals print exactly what they printed before (design D15).

Which refusals print the suffix after P1.3:

| Site reason | Where it is set | Code it accompanies |
|---|---|---|
| `binding_source_form_unsupported` | the one `_record_readiness` call, `elaborate.py` | `SI_EXPRESSION_SOURCE_UNSUPPORTED` (readiness) |
| `constraint_profile_blocked` | the `SI_CONSTRAINT_BLOCKED` `_diagnose` call, `elaborate.py` | `SI_CONSTRAINT_BLOCKED` |
| `occurrence_multiplicity_ordered` | the ordered-multiplicity raise, `elaboration/occurrence.py` | `SI_MULTIPLICITY_UNSUPPORTED` |
| `extraction_typing_target_unsupported` | the unsupported typing-target raise, `extraction/extractor.py` | `SI_TYPE_INVALID` |
| `evidence_<code>` (nine members) | `_EVIDENCE_REASONS`, `orchestration/elaborated_pipeline.py` | every relayed agentic-mbse `SemanticEvidenceError`, whatever its code |
| `internal_failure_unclassified` | `unexpected_public_failure`, `elaborate.py` | `SI_INTERNAL_DEFECT` |

The relayed-evidence row is the widest: every refusal relayed from agentic-mbse's semantic evidence now ends in a suffix, because the table is total over `SemanticEvidenceCode`.

Examples, from `run_codegen` on the reach witnesses in `tests/conformance/subset_profile/test_site_reason_reaches_harness.py` (temporary paths shortened):

- `SI_EXPRESSION_SOURCE_UNSUPPORTED: fx__Site__t.xs: reference='a, b': unsupported exact source form expression_source ('a, b') [root-0/model.sysml:11] (reason: binding_source_form_unsupported)`
- `SI_MULTIPLICITY_UNSUPPORTED: <model>: reference='fx::Rack::servers': ordered multiplicity on 'servers' is outside the supported occurrence model [root-0/model.sysml:9] (reason: occurrence_multiplicity_ordered)`
- `SI_INDEXED_SOURCE_UNSUPPORTED: qs#(1).v: reference='qs#(1).v': expression_evidence: indexed element reference is valid SysML but not implemented by this executable subset; the index is never flattened into a supported source [root-0/model.sysml:8] (reason: evidence_indexed_reference_unsupported)`

What was checked: the public package oracle (`tests/conformance/test_public_package_oracle.py`) and the v6 recapture batch (`tests/conformance/test_v6_recapture_batch.py`) pass unchanged, so no oracle or batch text depends on these messages. No existing test asserted a full message that gained a suffix; the full licensed suite shows no new failure from the text change.

## P4: the manual-stub notice

A successful live run now logs one WARNING per calc def output that compiles to a `MANUAL_REQUIRED` stub. Before P4 a stub was silent. The record is `ManualStubNotice` (`src/sysml_codegen/elaboration/diagnostics.py`), logged by `_announce_stubs` in `src/sysml_codegen/elaboration/elaborate.py` with `extra={"manual_stub": notice}`, right after each calc def compiles. A from-snapshot run compiles nothing and logs nothing new.

Example, from `sysml-codegen generate` on `tests/fixtures/subset_profile/calc-def-output-stub__invocation`:

- `WARNING: Calculation fx::C output r is a manual stub: unsupported node: invocation (['NumericalFunctions', 'sum']) (reason: compile_invocation)`

The reason is one of twelve new `SiteReason` members, `compile_*`: one per raise in `extraction/calc_compat_renderer.py` and one for each of the two compiler paths that stub without raising (`compile_dependency_cycle`, `compile_no_expression`). `CompilationError` text does not change; the reason travels as a field.

Nothing else changes: what is generated, what is accepted or refused, and every refusal message. Checked: the 22 v6 snapshots are byte-identical to `d73a4fc5`; `public_package_oracle/baseline.json` and `batch.json` are unchanged since `d73a4fc5`, and their tests pass in the full licensed run.

The site account (`tests/expectations/subset_profile/site_account.csv`) changed with this code: line numbers refreshed for every row in `elaborate.py` below the new helper and in the renderer, the `reason` column filled for the ten renderer rows, one new `internal_invariant` row for `ExactCompilationResult.__post_init__` (stub fields set together or not at all), and notes on four renderer rows saying no model reaches them. These are test expectations, not generator output.

## P5: reasons at the R3-row sites

Nine raises now pass a site reason. Six refusals print the P1.3 suffix ` (reason: <id>)` at the end of their message; the two projection-stage refusals do not, because `ProjectionError` renders its diagnostics without the suffix, so their text is unchanged and the reason reaches the log only as structured data (`extra={"refusal": ...}`). Nothing else changes: no code, no outcome, no other part of any message.

| Site reason | Site | Code | Message gains the suffix |
|---|---|---|---|
| `occurrence_containment_unanchored` | `build_containment_address`, `elaboration/occurrence.py` (ES-002) | `SI_OCCURRENCE_MISSING` | yes |
| `occurrence_containment_step_missing` | `OccurrenceIndex.resolve_address`, `elaboration/occurrence.py` (ES-009, through a ref part) | `SI_OCCURRENCE_MISSING` | yes |
| `elaboration_value_writers_incomparable` | `_require_one_writer`, `elaboration/elaborate.py` (ES-008) | `SI_REDEFINITION_INVALID` | yes |
| `elaboration_owner_address_target_missing` | `_resolve_semantic_reference`, `elaboration/elaborate.py` (ES-009) | `SI_OCCURRENCE_MISSING` | yes |
| `elaboration_calculation_output_unproduced` | `_resolve_calculation_output`, `elaboration/elaborate.py` (DEEP-QUALIFIED-WIRING) | `SI_OCCURRENCE_MISSING` | yes |
| `elaboration_feature_declaration_unindexed` | `_feature_python_type`, `elaboration/elaborate.py` (ES-011) | `SI_EDGE_DANGLING` | yes |
| `extraction_calc_def_no_output` | `_extract_calculation_definition`, `extraction/extractor.py` (CALC-DEF-BARE-RESULT) | `SI_EVIDENCE_INCOMPLETE` | yes |
| `projection_default_non_numeric` | `_float_default`, `elaboration/project.py` (ES-010 refusal side) | `SI_RENDERING_COLLISION` | no |
| `projection_sum_argument_count` | the computed-expression renderer, `elaboration/project.py` (PUSH-DOWN-AGG-PROFILE-SUM-SHAPE) | `SI_SNAPSHOT_INVALID` | no |

To carry the first two reasons to the log, `_ReferenceResolutionError` (`elaboration/elaborate.py`) gained a `reason` field, its three re-raises from `OccurrenceResolutionError` copy it, and the five `_diagnose` calls that report it pass it on. Projection's `_diagnostic` and `_fail` (`elaboration/project.py`) gained the same optional field.

Examples, from `sysml-codegen generate` on the cases named (paths shortened):

- `SI_OCCURRENCE_MISSING: fx__site__g: reference='t.v': semantic owner kind 'CalculationUsage' cannot anchor containment [root-0/model.sysml:8] (reason: occurrence_containment_unanchored)` (`candidate-es-002__constraint_binds_calc_input__binding_value`)
- `SI_OCCURRENCE_MISSING: fx__site__double: reference='facility.area': exact owner address has no target for leaf a339ea2b-… [root-0/model.sysml:4] (reason: elaboration_owner_address_target_missing)` (`candidate-es-009__composition_by_subsetting__part_usage`)
- unchanged: `Code generation failed: exact graph projection failed: SI_SNAPSHOT_INVALID: sum on 'fx__site__t' must have one argument` (`push-down-sum-shape__zero_arguments`)

Checked at the phase gate: snapshots, oracle baseline and batch (Implementation Notes, Phase 5).
