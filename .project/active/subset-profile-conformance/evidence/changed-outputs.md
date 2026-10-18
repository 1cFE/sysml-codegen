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
