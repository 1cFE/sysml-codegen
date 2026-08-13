# Companion-side evidence for Item 4 design (gathered by the orchestrator, 2026-08-13)

Stage sandboxes cannot read `/home/reid/1cfe/agentic-mbse-item7-rebuild`; the orchestrator
(full permissions) read it directly at companion tip `bc69f04`. These are verbatim findings,
cited by file:line, superseding the spec's research-record-only companion claims.

## The tautology is the companion's default message, confirmed

`src/agentic_mbse/sysml/executable_profile.py:357-374` — `_diagnostic(reason, construct,
identity, location, message=None)` defaults `message = f"{construct}: {reason}"`. For the two
chain-block sites that pass no message, that yields exactly `feature_chain:
block_feature_chain`. Codegen then renders `f"{diagnostic.reason}: {diagnostic.message}"`
(codegen `elaboration/elaborate.py:1097-1108`), so the modeler sees
`block_feature_chain: feature_chain: block_feature_chain` material — reason twice, reference
never.

## The payload for a real message already exists at the decision point

Both block sites hold the offending reference when they decide:

- `executable_profile.py:535-537` (`_walk_value`): `isinstance(node, FeatureReferenceNode)`
  and `node.reference.chain_segments` non-empty → `_diagnostic("block_feature_chain",
  "feature_chain", identity, location)`.
- `executable_profile.py:702-707` (proposition walk): same shape, same default message.

`node.reference` is a `FeatureReferenceFact` (`expression_facts.py:65-77`): `source_name:
str | None`, `target: IdentityFact | None`, `target_types: list[str]`, `chain_segments:
list[str]` — "the ordered path names for a feature chain (e.g. `["sensor", "reading"]`)".
So the written reference is reconstructible as the joined segments at the block site, and
`source_name` may carry the leaf's authored spelling.

`EligibilityDiagnostic` (`executable_profile.py:113-132`): `reason`, `construct`,
`location: LocationFact | None`, `constraint_identity: IdentityFact`, `message`, `force`.
`LocationFact` (`constraint_facts.py:106-111`) is `file`/`line`/`column`. Note the
`__post_init__` enforces `reason in REASON_CODES` (closed vocabulary, DD-R05) — a fix that
mints a new reason code must extend `REASON_CODES` deliberately; a fix that only rephrases
`message` does not touch the vocabulary.

## Consequence for the design split

The minimal paired fix suggested by this evidence (design's call, not settled here): the
companion passes an explicit `message` naming the joined chain (and states the bindings
rewrite, or leaves the rewrite phrasing to codegen's renderer), and codegen's rendering
de-duplicates repeated identical diagnostics (the 13-copy `LayerContinuity` case) with a
deterministic order. Both chain-block sites (`:537`, `:704`) must be covered, or the fix
covers one lane of two.

## Working constraints for design/implement stages

- Design stage: no companion reads, no execution — design from this file + codegen source
  (readable) + the spec. Where a claim here is insufficient, write a "Requested probe" note;
  the orchestrator runs it and resumes you with results.
- Implement stage: runs with full permissions and must re-verify the citations above before
  editing the companion.

## P4 verdict (orchestrator, static read at companion `bc69f04`)

`extract_feature_chain_segments` (`expression.py:611-637`) appends the *root* first —
`reconstruct_expression(operands[0])` — then the target's chaining feature names. So a chain
authored `bioshield.outer_radius` yields `["bioshield", "outer_radius"]`: segments include the
root, and the primary branch (`".".join(chain_segments)`) reproduces the authored spelling.
`_reference_node` (`constraint_extraction.py:505-518`) also sets
`source_name = reconstruct_expression(expression)` — the full authored text as a second
carrier. B3 holds. Static evidence only: the implement stage's multi-chain characterization
asserts the exact rendered references against a live fixture, which confirms this live.
P1–P3 are post-fix discriminators and run inside the implement stage at the designed points.

## M3 totality (orchestrator, verbatim from companion `executable_profile.py:66-100`)

`REASON_CODES` contains exactly 23 `block_*` members and 4 `warn_*` members:
block_assert_by_reference, block_derived_unit_unsupported, block_feature_chain,
block_implies, block_incompatible_dimensions, block_integer_equality_unpreservable,
block_invalid_assertion_polarity, block_invocation, block_malformed_operand_fact,
block_missing_predicate, block_non_numerical_containment, block_non_predicate_root,
block_ordering_category_pair, block_real_equality_requires_tolerance,
block_unit_conversion_required, block_unitless_dimensioned, block_unknown_exact_unit,
block_unresolved_definition, block_unresolved_operand, block_unsupported_node,
block_unsupported_operand_category, block_unsupported_operator, block_xor;
warn_non_numerical_equality, warn_non_numerical_implies, warn_non_numerical_predicate,
warn_non_numerical_xor. The design's residue table (nine published reasons) must be
reconciled against THIS list in the close record — which of the 23 still cannot "name the
exact construct to fix" after this item, and why that is acceptable or filed.
