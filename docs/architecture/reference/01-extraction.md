# Step 1: Extraction

`src/sysml_codegen/extraction/extractor.py` loads SysML through the Agentic SysIDE adapter and extracts calculation definitions. The exact elaborator walks modeled owners, occurrences, references, and constraints; [02-orchestration](02-orchestration.md) connects that authority to generation.

## The semantic-evidence boundary

`elaborate_loaded_extractor` in `orchestration/elaborated_pipeline.py` consumes mapped metatype, exact referent/target, operand, origin, and `DocumentTier` evidence. It converts `SemanticEvidenceError` once into the located `SI_EVIDENCE_INCOMPLETE` diagnostic for live generation and admitted snapshot capture. The private graph builder does not reinterpret incomplete evidence.

Features need one qualified supported primitive type. Missing, multiple, user-defined lookalike, and unsupported primitive outcomes refuse as `SI_TYPE_INVALID`. Valid indexed-element expressions currently refuse as `SI_INDEXED_SOURCE_UNSUPPORTED`. Evidence: `tests/conformance/test_expression_evidence_integrity.py` and `test_feature_typing_integrity.py`.

## Calculation definitions

Each `calc def` yields `CalculationDefinitionData` in `extraction/data_models.py`, with input/output attributes, source provenance, and UUID-keyed expression/member sidecars. Declaration identity drives compilation; names supply Python rendering. See [09-data-models](09-data-models.md#extraction-models) and [14-expression-compiler](14-expression-compiler.md).

```sysml
calc def battery_cost_calc {
    in capacity : Real;
    in unit_cost : Real;
    return total_cost : Real = capacity * unit_cost;
}
```

Direction-carrying `ReferenceUsage` members include bare inputs and named returns. Inline return expressions populate the output AST sidecar. Anonymous returns refuse before the zero-output diagnostic; a body assignment does not duplicate its declared output. Evidence: `tests/conformance/test_return_style_extraction.py`.

## Occurrences and sums

The elaborator owns calculation usages and attribute values within modeled containment. It resolves redefinitions and aliases against exact declaration/occurrence identity. A modeled plural sum reads each member's concrete occurrence; it does not multiply one sampled value by multiplicity. See [the pipeline overview](00-pipeline-overview.md) and `tests/conformance/test_occurrence_domain_derivation.py`.

Every authored constraint usage belongs to the instance graph's usage domain before owner-to-scope expansion. Eligible, excluded, and non-reaching dispositions remain visible; unsupported requirement forms do not disappear. See `tests/conformance/test_constraint_population_oracle.py`, `test_constraint_usage_domain_totality.py`, and `test_constraint_catalog_totality.py`.

## Units and metadata

Declaration comments, description parentheses, and type names do not create unit labels. Parser-native units on written values remain part of value/expression facts; constraint operand validation retains its existing unit rules. Codegen does not add automatic unit conversion. Human `// [units] - Description` notes require no special parser in codegen.

The live extraction layer retains declaration UUIDs and AST sidecars. V6 serializes the normalized instance graph rather than extraction dataclasses. See [27-snapshot-generation](27-snapshot-generation.md).

## Requirement traceability

The current [verification matrix](../verification-matrix.md#ext) records retained extraction obligations and the retirement of the old usage/hierarchy extraction mechanisms. Their deleted virtual-usage, binding-taxonomy, and type-index machinery is recoverable from Git history; it is not a second current route.
