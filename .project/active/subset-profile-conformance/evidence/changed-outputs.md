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

## P6: reasons at the tail sites, one O8 conversion, three new locations

Forty-one raises now pass a new site reason (the tail's public sites, plus two re-checks behind a preflight), and `generation_constraint_name_unsafe` moved from inside the `constraint_name_safety_error` factory to its caller's raise. Elaboration-stage refusals print the P1.3 suffix ` (reason: <id>)`; projection- and generation-stage refusals (`ProjectionError`, `CodeGenerationError`) print unchanged text and carry the reason as structured data only. Every new member is in `SiteReason` (`src/sysml_codegen/elaboration/diagnostics.py`); the account's `reason` column names the site of each.

Three changes go past a suffix. None changes what is generated or which models are accepted or refused.

- **O8: an untyped calc usage now refuses with a code.** `_typed_definition` (`elaboration/elaborate.py`) raised a plain `ValueError`, which reached the user as `SI_INTERNAL_DEFECT`. It now raises `ElaborationInvariantError(SI_TYPE_INVALID)` with the same message, a source location and reason `elaboration_usage_definition_typing_count`. O8 permits this: the plain exception reached users as `SI_INTERNAL_DEFECT` with it in the cause chain. Outcome (refused) is unchanged; the code changes from `SI_INTERNAL_DEFECT` to `SI_TYPE_INVALID`. Its site ID changes from `…::_typed_definition::builtin::ValueError::1` to `…::_typed_definition::coded::SI_TYPE_INVALID::1`.
- **Three refusals gain a source location.** The `_typed_definition` refusal and both deep-literal-override refusals (`_apply_deep_literal_redefinitions`, `OVERRIDE_TARGET_MISSING`) now name the authored line, as other elaboration refusals do.
- **The unsupported-IR check raises its own exception class.** `InstanceGraph._expression_reference_count` (`elaboration/graph.py`) raised a plain `TypeError` for an `UnsupportedNode`, which `validate()` caught and reported as `SI_EDGE_DANGLING`. It now raises `UnsupportedExpressionIRError`, a `TypeError` subclass that carries reason `graph_computed_ir_unsupported`, and `validate()` passes the reason into the same diagnostic. The code, outcome and text are unchanged apart from the suffix. Site IDs: the unsupported-IR raise is now `…::_expression_reference_count::unrecognized::UnsupportedExpressionIRError::1`, and the invalid-IR raise (an internal invariant) moves from `builtin::TypeError::2` to `builtin::TypeError::1`.

Plumbing that carries the reasons, with no output effect: `IdentityBoundaryError` gained `reason`; `constraint_name_safety_error` and `residual_class_name_collision_error` (`generation/errors.py`) take the reason from their caller; `_generation_error` (`generation/modules.py`) passes an optional reason to `CodeGenerationError`; elaboration's relay of a `CompilationError` copies its reason.

Examples, from `sysml-codegen generate` on the cases named (paths shortened):

- `SI_TYPE_INVALID: <model>: syside.core.QualifiedName(['fx', 'Site', 'c']) has 0 exact CalculationDefinition typings [root-0/model.sysml:6] (reason: elaboration_usage_definition_typing_count)` (`calc-usage-typing__untyped`; was `SI_INTERNAL_DEFECT` with the same message body)
- `OVERRIDE_TARGET_MISSING: fx__site: deep literal override does not target an attribute node [root-0/model.sysml:9] (reason: elaboration_deep_override_target_computed)` (`deep-override__computed_target`; gains the location and the suffix)
- `SI_EDGE_DANGLING: fx__site__t: computed calculation contains unsupported typed IR (reason: graph_computed_ir_unsupported)` (`push-down-sum-shape__sequence_argument`)
- `SI_ID_UNSTABLE: <model>: CalculationUsage has no reload-stable qualified declaration identity (reason: identity_qualified_name_missing)` (`anonymous-declaration__calc_usage`)
- unchanged: `Code generation failed: DUPLICATE_OUTPUT_PATH: SysML names "fx::'Twice-x'" and 'fx::Twice_x' both derive modules/fx/twice_x.py. …` (`output-naming__module_path_collision`)

The site account changed with this code: line numbers refreshed below each edit, three site IDs renamed as above, and the 84 tail rows given their Phase 6 verdicts. These are test expectations, not generator output. Checked at the phase gate: snapshots, oracle baseline and batch (Implementation Notes, Phase 6).
