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
