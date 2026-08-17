# Expected transition allow-list

This seed names the only before-state changes permitted by approved design revision 4. A row is an
allow-list entry, not a claim that its required result has passed. Each row must gain its proving
test and measured reconciliation before final evidence is accepted.

| Transition | Old behavior | Required result | Proof owner |
|---|---|---|---|
| A1 occurrence selection | nearest, descendant, or sole candidate may answer | exact address in the consumer domain or named missing/ambiguous refusal | `test_occurrence_domain_derivation.py`; public mutation test |
| A2 calculation output | nearest or globally sole calculation may answer | exact output-index record contextualized by usage owner and consumer domain | `test_occurrence_calc_domain_derivation.py`; public mutation test |
| A3 lineage miss | one descendant may answer | lineage-local result or `SI_OCCURRENCE_MISSING` | `test_definition_owned_reference_positions.py` |
| A4 package/model root | model root may answer a consumer miss | direct one-step package-owned no-prefix result; nested no-prefix refusal | B2 probe; `test_occurrence_domain_derivation.py` |
| A5 indexed expression | index is ignored | pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED` | `test_expression_evidence_integrity.py` |
| A6 multiplicity writer | unrelated sole writer may answer | owner-address writer or `SI_MULTIPLICITY_UNRESOLVED` | `test_occurrence_multiplicity_authority.py`; public mutation test |
| B1-B5 evidence | fallback, partial traversal, name recovery, or qualified-name filtering continues | exact evidence and `DocumentTier`, or `SI_EVIDENCE_INCOMPLETE` | agentic adapter/expression tests; codegen boundary tests |
| B6/B7 metadata | weak type or skipped redefinition identity may pass | sole qualified type and one exact slot family, or named refusal | `test_feature_typing_integrity.py`; occurrence tests |
| B8 leaf | resolved fact may be skipped | real corpus is total before D5; missing leaf raises typed error after D5 | B8a retained probe; B8b agentic/codegen tests |
| B9 exit type | warning plus incomplete registry may pass | `EXIT_POINT_TYPE_UNSUPPORTED` before mutation | `test_generation_exit_type_preflight.py` |
| B10 source origin | sole glob may supply a file | measured `DELETE_UNREACHABLE`, then fallback deletion | B10 retained probe; metadata test |
