# Technical Design: Stop Reinventing the Parser

**Status:** Draft — Revision 6; Revision-5 review resolutions incorporated, targeted confirmation required
**Revision:** 6
**Date:** 2026-08-17
**Branch:** `stop-reinventing-the-parser`
**Contract:** `spec.md`, approved revision 4
**Prior review:** `design-review.md`, Revision 5 `Revise`; all owner resolutions finalized 2026-08-17
**Product lens:** `BLOCKED` at `audit3-F1` until the Revision-6 indexed-consumer proof passes
**Revision input:**
`.project/research/20260817-164828_expression-evidence-boundary-convergence-assessment.md`

## Outcome

The occurrence core remains unchanged: the exact route resolves occurrences from parser identities,
semantic ownership, modeled containment, and the consumer's occurrence domain. D1-D4 stay intact.
The correction is at the evidence edges feeding that core. Every production expression consumer
that derives dependency or occurrence identity must receive exact reference evidence from one
Agentic inspection operation. Indexed shapes become non-resolvable values, incomplete paths fail
before a value exists, and every raw semantic selector has one reviewed owner.
Codegen converts owned failures once at the bridge shared by live generation and snapshot capture.
Registry generation derives its own wrapper set from the graph and accepts no caller-supplied copy.

Revision 6 supersedes Revision 4's D5, D7, D9, evidence matrix, and the review claims that F4 and F7
were closed. It also corrects the route inventory and adds a mechanical closure condition. D1-D4,
D6, the general `ExpressionIR`, the occurrence mutation proof, and the acyclic
`C_prod -> F_final -> C_evidence` topology remain intact. The committed runner remains the only
producer of final run evidence; the failed candidate's externally staged report is not reusable.

Shaping and the spec are not rerun. The fresh research found that A5 and B3/B4/B9 still state the
right required behavior; the defect is that the approved mechanisms did not make alternate weaker
routes illegal. Revision 6 incorporates every finalized Revision-5 review resolution. It still
needs the review's targeted confirmation and a replacement plan before any production edit.

## The Point

**[INHERITED: P-003 and P-004]** The product parses the models, walks the parser's resolved tree to
reconstruct the authored math, and writes that math into TEAx Python. A reference the toolchain
cannot honor is refused by name. It is never silently changed into another expression and never
recovered through a manual fallback. This revision makes that obligation structural: there is one
closed path from parser evidence to occurrence resolution, and completion requires proof that no
weaker sibling path remains.

## Product and authority frame

The design preserves these existing product decisions:

- P-001 requires search-free variation. Consumer position and candidate counts cannot stand in for
  modeled identity.
- P-002 requires exact owner anchoring. The closed usage-owner repair stays intact.
- P-003 requires named refusal instead of a workaround for evidence the product needs.
- P-004 defines the product identity as parse, walk, emit. Parser-owned classification is consumed,
  not reconstructed.

The premise-audit census is location evidence only. Its fallback counts and conclusions remain
retracted. Appendix B accounts for every surviving location row so implementation cannot silently
inherit the census's old interpretation.

### Product-lens design-F1 correction

The design-F1 correction is this exact rule:

> B5 reads `element.document.document_tier` and compares the returned member directly with SysIDE's
> `DocumentTier.StandardLibrary`. A missing document, missing tier, `None`, or a value outside the
> installed `DocumentTier` enum raises `SemanticEvidenceError`. A qualified name, URL, filesystem
> path, normalized origin, or package name never classifies standard-library status. Document URL
> and path remain source-location evidence only, including the B10 probe.

This answers the finding recorded at `product-lens.md:447-455` and follows SysIDE 0.8.4's public
`BasicDocument.document_tier` property and `DocumentTier` enum
(`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:1420,5676-5690`). The Revision-3 final
product-lens rerun records `Gate: CLEAR` and design-F1 `FIXED (remains fixed)` at
`product-lens.md:503-535`. That is the historical result for D6. The latest product-lens gate is
`BLOCKED` for `audit3-F1`; it does not reopen the `DocumentTier` correction.

## Current code facts

These facts describe the audited failed candidate, not this documentation checkout:

- `occurrence.py` now owns stable feature slots, occurrence IDs, containment addresses, type
  closures, and exact multiplicity/redefinition behavior. The fresh audit reproduced D1-D4 on
  their intended routes.
- Codegen still walks expressions independently for calculation-definition dependencies,
  calculation and constraint bindings, aliases, computed attributes, and predicates. Some walks
  consume Agentic facts; others reconstruct references or dependencies from raw expression nodes.
- The indexed-source preflight covers direction-`In` top-level feature chains. The computed
  attribute route reads a fact that retains `has_index_segment`, ignores that field, and resolves
  the remaining path. The licensed probe therefore maps `cells#(2).mass` to `cells[0].mass`.
- Agentic owns typed operand materialization, exact reference facts, and the general ExpressionIR.
  Codegen nevertheless retains a raw-AST unit unwrapping helper, a recursive dependency walk with
  its own depth behavior, and a bare-binding constructor whose semantic path may be `None`.
- Deep literal overrides build relationship paths separately and filter missing target segments,
  so a valid/missing/valid path can silently shorten.
- CLI generation derives and validates exit-point wrapper types before mutation, but the exported
  registry generator accepts a caller-provided type list. An empty or incorrect second account can
  bypass the invariant. The existing collector raises an untyped `RuntimeError` on an unsupported
  root; there is no warning-and-omit branch at the audited commit.
- `usage_extractor.py`, `computed_attribute_extractor.py`, and `hierarchy_resolver.py` are off the
  audited public route. Their raw selectors still prevent a repository-wide ownership claim unless
  reachability is proved or they enter the manifest.

### Revision-6 implementation base

**[OWNER 2026-08-17]** Implementation branches from the audited failed-candidate Codegen tree, the
old `C_prod` (called `C_base` in this revision),
`78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, and corrects it in place. The corresponding
Agentic input is `A_base = 2171016d3e3e0805525aa4cf787c55c6293dd00c`. The current documentation
checkout is not an implementation base. D1-D4, the retained probes, and the committed verification
harness in `C_base` are preserved; gate 6 assigns fresh target identities `A_final`, `C_prod`,
`F_final`, and `C_evidence`.

### Load-bearing bets

- **B1 — the raw-source route set is finite.** The reviewed live and admitted/capture arms plus the
  sealed from-snapshot exclusion account for every public entry. *If false → the closure matrix can
  certify a subset while another public route still loses evidence.*
- **B2 — the reviewed selector vocabulary covers raw expression evidence acquisition.** SysIDE's
  expression API exposes operands, referents, target features, feature chaining, and mapped
  metatypes at these seams. The AST gate also covers literal/dynamic `getattr` and local aliases.
  *If false → the selector manifest can be exactly green while an unscanned raw read survives.*
- **B3 — SysIDE 0.8.4 exposes `IndexExpression` as a mappable metatype.** The installed stub defines
  it as an `OperatorExpression` (`syside/core/__init__.pyi:10897-10920`). *If false → Agentic cannot
  own index classification and implementation stops before semantic-evidence/v2 lands.*

## One architecture

There is one resolution architecture and one evidence-acquisition route per semantic fact:

```text
SysIDE document + AST
        |
        | exact IDs, DocumentTier, resolved targets, semantic owners
        v
Agentic reference inspection + existing ExpressionIR extraction
        |                         |
        | closed ReferenceUse     | neutral math/predicate IR
        v                         v
codegen pre-graph evidence inventory -- indexed/incomplete use refuses here
        |
        v
exact resolver (accepts ExactReferenceUse only)
        |
        v
ContainmentAddress + OccurrenceIndex + calculation-output producer index
        |
        v
InstanceGraph -> projection -> graph-derived generation preflights -> TEAx package
```

`ContainmentAddress` is a private immutable value. The producer index is a private dictionary of
immutable records. Neither is a strategy object, a selectable resolver, or a compatibility layer.
`ReferenceUse` is a small closed evidence union beside the existing `ExpressionIR`; it is not a
replacement expression tree. Deep redefinition paths use a separate total factory because they are
relationship paths, not expressions. The existing exact route is changed in place. No flag or
fallback can select the retired behavior.

## Detailed decisions

### D1. One general semantic-owner selector

`elaboration/occurrence.py` will define the only semantic-owner selector used by occurrence
building, address construction, calculation contextualization, multiplicity ownership, attachment,
formal-domain handling, and elaboration:

```python
def semantic_owner(element: Any) -> Any:
    owning_type = getattr(element, "owning_type", None)
    return owning_type if owning_type is not None else getattr(element, "owner", None)
```

The selector does only acquisition. It returns any semantic owner kind, including
`CalculationDefinition`, `ConstraintDefinition`, and `RequirementDefinition`, or `None`. It does
not validate identity, attachability, or containment capability. Truthiness never selects the
branch; only `owning_type is not None` does.

Existing attachment and formal-domain behavior remains authoritative. `_attachment` continues to
attach `PartDefinition`, `PartUsage`, and `Package`; it continues to report `owner_absent` for
`None`, and `owner_kind_unattachable` for a valid owner such as `CalculationDefinition` that has no
occurrence attachment. `_owner_kind` retains its broader closed grading vocabulary, including
calculation- and requirement-definition owners. No formal is rejected merely because its semantic
owner cannot anchor a containment address (`elaboration/elaborate.py:680-735,757-768`).

The old `getattr(..., "owning_type", None) or getattr(..., "owner", None)` copies are deleted. A
static test permits the selection expression only inside `semantic_owner`. The existing
calculation-definition attachment regression in `tests/unit/test_constraint_attachment_cause.py`
stays green and a direct selector test pins `CalculationDefinition` and `None` as legal results.

### D2. The modeled containment address

The private value is:

```python
@dataclass(frozen=True)
class ContainmentAddress:
    anchor_kind: Literal["package", "part_definition"]
    anchor_id: DeclarationId
    steps: tuple[FeatureSlotId, ...]
```

`build_containment_address` is the only caller that applies the closed owner-kind validation.
Construction starts with the referenced element when it is a `PartUsage`; otherwise it starts with
the element's `semantic_owner`. At each address hop it accepts only a live `PartUsage`,
`PartDefinition`, or `Package`, checked through mapped SysIDE metatypes. Every accepted hop must
have a stable declaration ID and qualified name. A `PartUsage` prepends its feature slot and the
walk continues. A `PartDefinition` or `Package` creates the anchor and stops the walk. A missing
owner, another owner kind, missing identity, repeated identity, or cycle refuses address
construction without changing the general selector or attachment policy. Thus:

- a feature directly owned by a definition has a definition anchor and no containment steps;
- a nested feature has the definition or package anchor followed by every modeled part-usage slot;
- a package-owned part usage has a package anchor and one step;
- redefined usages contribute their canonical `FeatureSlotId`, never the redefining declaration ID;
- occurrence indices are not part of the modeled address. They enter only when the address is
  instantiated in a consumer domain.

The address is derived from resolved parser elements. Rendered names and source order are not
inputs.

#### Instantiating an address

`OccurrenceIndex.resolve_address(address, consumer_domain, *, plural)` is the only operation that
turns a modeled address into concrete occurrences. `ConsumerDomain` is an immutable query value,
not a resolver. It contains the consumer's exact `ScopeId` plus a closed map from every modeled
package/definition anchor on that scope's occurrence lineage to the concrete scope that realizes
it. The map is built once from the consumer occurrence and its recorded ancestors and type
closures. A repeated anchor maps to all concrete scopes so ambiguity is retained rather than
resolved by distance.

`OccurrenceIndex` adds direct `roots_by_package_and_slot` and `children_by_parent_and_slot` maps.
Address resolution reads those maps; it does not rescan the occurrence population.

1. Read the exact anchor key from the consumer domain.
   - For a definition anchor, zero concrete scopes is `SI_OCCURRENCE_MISSING` and more than one is
     `SI_OCCURRENCE_AMBIGUOUS`. Exactly one is the start scope. No nearest scope is elected.
   - For a package anchor, the consumer must be `PackageScopeId(anchor_id)` or an occurrence whose
     root belongs to that exact package. No other package is searched.
2. Walk `steps` in order through `OccurrenceIndex.children(parent, slot)`. At a step shared with the
   consumer's own address, reuse the consumer's exact occurrence index. After the first divergent
   step, accept only children carrying the requested slot.
3. A scalar step requires exactly one child. A plural step returns all modeled indices in
   `OccurrenceId` order. Zero is missing and more than one scalar child is ambiguous.
4. The walk never examines a descendant not named by the remaining address, never retries from an
   ancestor, and never uses a model-root population as a fallback.

This gives repeated outer instances a precise behavior: the shared address prefix copies the
consumer's outer occurrence index, so a consumer in `plant[2]` cannot bind a source in `plant[1]`.

#### No-prefix package references

A no-prefix reference may start from a package only when the resolved target itself is directly
package-owned: `semantic_owner(target)` is that `Package`, and the ownership walk has exactly one
edge `target -> Package`. The target is then resolved at that exact `PackageScopeId`.

If a package anchor would require any intervening `PartUsage`, the no-prefix form refuses with
`SI_OCCURRENCE_MISSING` and identifies the missing modeled prefix. This includes a target nested one
or more parts below a package, even if the model contains only one such target. An explicit resolved
prefix may carry the same nested target and is processed through the full address.

This is the complete A4 rule. There is no longest-common-prefix search and no package-wide sole
candidate exception.

### D3. Calculation-output producer ownership

Calculation outputs receive a dedicated index while calculation nodes are built:

```python
@dataclass(frozen=True)
class CalculationOutputProducer:
    output_declaration_id: DeclarationId
    calculation_usage_id: DeclarationId
    effective_usage_id: DeclarationId
    calculation_definition_id: DeclarationId
    owner_address: ContainmentAddress
    scope: ScopeId
    node_id: NodeId
    port_id: OutputPortId

CalculationOutputProducerIndex = dict[
    DeclarationId, tuple[CalculationOutputProducer, ...]
]
```

The dictionary key is the exact output declaration from the calculation definition. A record is
added for every applicable calculation-usage declaration under which the node is entered in the
existing `_calcs[(scope, declaration)]` map, including authored/redefined alternatives.
`calculation_usage_id` is that referenceable declaration; `effective_usage_id` is the selected
writer stored on the node. This preserves redefinition parity without duplicating graph nodes.
Each record also carries exact scope, node, and output port. Records are sorted by
`(calculation_usage_id, scope, node_id)` for stable diagnostics. Duplicate full keys are an
invariant failure.

For each record, `owner_address` is derived by applying D1/D2 to the semantic owner of that
record's applicable `calculation_usage_id`. The usage is not treated as a part-containment step.
The calculation node's `scope` is the concrete instantiation of that owner address.

Resolution of an output declaration is exact:

1. Read only the bucket for `output_declaration_id`.
2. If the resolved expression names a calculation-usage root, filter by that exact
   `calculation_usage_id`. A bare output has no such filter.
3. For every remaining record, instantiate its `owner_address` in the `ConsumerDomain` using D2.
   Retain the record only when its stored `scope` is one of those exact instantiated scopes.
4. Collapse records only when `(scope, node_id, port_id, effective_usage_id)` is identical. This
   joins authored/redefined declaration aliases that name the same effective producer; it never
   joins distinct nodes or ports.
5. Require exactly one scalar producer and return its stored `port_id`. Zero is
   `SI_OCCURRENCE_MISSING`; more than one is `SI_OCCURRENCE_AMBIGUOUS` and lists every usage and node
   identity.

There is no scan of `graph.calcs`, no nearest calculation selection, and no model-wide sole
producer rule. Two sibling calculation usages that share an output declaration are ambiguous for a
bare reference. A repeated-outer consumer selects the producer under its own outer occurrence. A
direct package-owned producer resolves only in its exact package. A producer in an unrelated owner
domain remains missing even when it is the only producer in the model.

### D4. Leaf, multiplicity, and redefinition rules

- A bare definition-owned leaf is looked up only on the consumer's exact occurrence lineage. A
  lineage miss is final. The descendant-count arm in `_resolve_leaf` is deleted.
- A usage-owned leaf is resolved by its full containment address. It does not first elect an owner
  occurrence and then retry the leaf elsewhere.
- A multiplicity bound reference is resolved through the bound expression's exact referent, its
  canonical feature slot, the multiplicity-owning part's address, and that part's concrete parent
  domain. An unrelated model-wide writer cannot participate. Zero, incomparable, or multiple exact
  writers produce `SI_MULTIPLICITY_UNRESOLVED`; an unsupported finite shape keeps the existing
  multiplicity-specific refusal.
- `build_feature_slot_index` requires stable identity for every authored and implied redefinition
  endpoint. Missing wrapper or endpoint identity raises `SI_REDEFINITION_INVALID`. It never skips an
  endpoint or creates another slot family.
- `cells#(2).mass` reaches the pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED` capability refusal. The
  index marker is never dropped and indexed-element support is not added in this item.

### D5. Public agentic evidence contract

Agentic keeps the public `SemanticEvidenceError` contract in `agentic_mbse.errors`, re-exported from
`agentic_mbse.__init__`, and advances its API marker before codegen consumes the revision:

```python
SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v2"

class SemanticEvidenceError(AgenticMBSEError):
    code: SemanticEvidenceCode
    operation: str
    detail: str
    location: tuple[str, int] | None
    reference: str | None
    cause: BaseException | None
```

`SemanticEvidenceCode` is the closed string enum
`METATYPE_CHECK_FAILED`, `EXPRESSION_KIND_UNSUPPORTED`, `OPERAND_ITERATION_FAILED`,
`EXPRESSION_DEPTH_EXHAUSTED`, `RESOLVED_TARGET_MISSING`, `DOCUMENT_TIER_MISSING`,
`DOCUMENT_TIER_UNKNOWN`, `RESOLVED_LEAF_MISSING`, and `INDEXED_REFERENCE_UNSUPPORTED`. The last code
is for Agentic consumers that require an exact use; Codegen's public bridge maps it to the existing
valid-but-unimplemented `SI_INDEXED_SOURCE_UNSUPPORTED` diagnostic. The exception's `detail` never
embeds its code. When wrapping a parser exception, construction stores it in `cause` and the raise
site uses `raise ... from cause`.

#### Closed reference-use values

Agentic adds frozen, valid-by-construction values beside the existing general `ExpressionIR`:

```python
ReferenceUse = ExactReferenceUse | IndexedReferenceUse

def inspect_reference_uses(expression: Any) -> tuple[ReferenceUse, ...]: ...
```

`ExactReferenceUse` contains one non-empty `ExactSemanticPath`, the authored reference form
(`bare`, `qualified`, or `chain`), authored text, authored segments and qualifier, scalar/plural
consumption context, and source location. The returned tuple preserves first-seen expression order.
Each root, member, and leaf target record carries its stable declaration identity, resolved member
name, qualified name, owner identity and kind, document URL and tier, and target source location.
That is the one provenance-complete payload used by calculation dependency ordering, cross-file
binding checks, aggregation terms, and ADR002; those consumers do not reconstruct an
`ExpressionRef` from names or a live element.

`ExactSemanticPath` requires a non-null root and leaf, one fact for every segment,
`segments[0] == root`, and `segments[-1] == leaf`. Its constructor enforces those invariants; there
is no public optional-root or optional-leaf state.

`IndexedReferenceUse` contains only the authored reference and location needed for the existing
unsupported-capability diagnostic. It carries no `ExactSemanticPath`. The exact resolver's type
signature accepts `ExactReferenceUse`, never the union and never the permissive
`ResolvedSemanticReferenceFact`. Accidentally dropping an index therefore requires an explicit,
review-visible conversion that the static ownership gate forbids.

The resolver also checks the concrete value at runtime and performs no duck-typed coercion. Passing
an `IndexedReferenceUse`, legacy fact, IR node, or arbitrary lookalike is an invariant failure. This
backstop matters because the repository's full static type lane is not currently a green gate.

The existing `ExpressionIR` remains the neutral math/predicate representation. Its optional
reference metadata is not occurrence authority. Codegen may consume an IR for rendering or
compilation and the strict reference uses for dependencies, but it cannot resolve a producer from
the IR. A new universal expression tree or an aggregate that duplicates the IR is rejected: the
problem needs a strict reference view, not a second math representation.

`FeatureReferenceFact.target: IdentityFact | None` remains only as an IR leaf for neutral math
reconstruction. Agentic's ownership manifest records it as a non-authoritative typed surface, and
the exact-route import/type gate forbids it in the inspector, inventory, binding-source factory, or
resolver entry. Its optional state can describe undecoded math; it cannot create a dependency edge.

#### One total inspection operation

`inspect_reference_uses` owns the complete production reference walk:

- `SysideAdapter` adds `IndexExpression` to its mapped metatype table. Runtime class names never
  identify it. A kept adapter test pins the SysIDE 0.8.4 stub/runtime mapping before any consumer
  migration.
- Operand sequences are materialized only through `materialize_operands`; getter or iteration
  failure raises `OPERAND_ITERATION_FAILED`.
- One non-caller-selectable depth limit is shared by `inspect_reference_uses`,
  `extract_expression_ir`, expression reconstruction reached by extraction, and every other
  recursive production expression entry. Exhaustion raises `EXPRESSION_DEPTH_EXHAUSTED`.
- A structural unit annotation visits its value operand and validates its shape but never emits the
  unit operand as a data reference. Codegen's raw-AST `annotated_ast_value` entry is deleted and
  de-exported; IR consumers keep `annotated_ir_value`.
- A supported `sum` invocation marks its contained reference uses plural. Other existing supported
  scalar contexts remain scalar. The operation preserves the current aggregation semantics without
  choosing concrete occurrences.
- A feature reference uses only its exact `referent`. A feature chain uses only its exact root,
  every `target_feature.chaining_features` segment, and leaf. The first missing fact raises
  `RESOLVED_TARGET_MISSING` or `RESOLVED_LEAF_MISSING`; partial paths never return.
- Authored bare/qualified/chain form, reference text, and location are acquired here once. Codegen
  does not reread the CST to decide no-prefix semantics.
- An index at any supported depth returns `IndexedReferenceUse`, regardless of whether the enclosing
  site is a binding, alias, computed attribute, predicate, or calculation-definition expression.

#### Delete the permissive production surface

**[OWNER 2026-08-17]** Agentic deletes `extract_feature_refs`, `feature_reference_facts`,
`feature_chain_facts`, `ResolvedSemanticReferenceFact`, and their lazy/barrel exports. The
index-bearing `has_index_segment: bool` state disappears from production data models. No deprecated
alias, compatibility wrapper, or manifest exemption keeps that surface alive. `ExpressionRef` and
`BindingInfo.references: list[ExpressionRef]` are also removed; the reviewed tree has no unrelated
consumer. The rejected alternative was to keep the permissive API and manifest its consumers,
which would preserve the second interpretation this item is removing.

All production consumers migrate to `inspect_reference_uses`:

- `aggregation.py` stores an `ExactReferenceUse` in exact reference/chain nodes. It calls a private
  exhaustive `require_exact_reference_use` guard before appending a `SingletonTerm`; an indexed use
  raises `INDEXED_REFERENCE_UNSUPPORTED`, so neither aggregation site can manufacture an index-free
  term.
- `binding.py` stores the ordered `ReferenceUse` tuple. Cross-file checks read the exact target's
  document URL; an indexed use cannot be projected into path metadata.
- `validation/adr002.py` treats both variants as a present dynamic reference, uses exact document,
  qualified-name, and owner-kind evidence only for the exact variant, and never converts the
  indexed variant into an exact path or an empty reference list.
- `expression.py` rebuilds its internal reference consumers over the same tuple. Codegen's
  calculation compiler, binding lane, and elaborator migrate in D7.

The measured migration at the pinned trees is five direct on-route Codegen helper calls, four
external Agentic runtime calls (`aggregation.py` twice, `binding.py`, and `validation/adr002.py`),
plus three internal `expression.py` calls. Counts are sizing evidence, not a closure oracle; the
static gates must rediscover the final set before deletion.

#### Existing B1-B5/B8 behavior retained

The prior typed operations remain, with the exclusivity correction above:

- B1: a live SysIDE element is recognized by the installed SysIDE `Element` base. Its mapped
  `.isinstance()` result is authoritative. If that call raises, the adapter raises
  `SemanticEvidenceError(METATYPE_CHECK_FAILED)` from the parser exception. Class-name matching is
  allowed only for an object that is not a live SysIDE element, which is the explicit test-double
  path. Unknown type-map names remain errors.
- B2: operator, feature-reference, and feature-chain dispatch use mapped SysIDE metatypes. The
  explicit non-live test-double path uses the same closed mapped names. No production class-name
  substring selects a branch.
- B3: operands are materialized once per visit. Failure and depth exhaustion are distinct typed
  outcomes with the expression location. Successful traversal visits every materialized operand.
- B4: `FeatureReferenceExpression.referent` and `FeatureChainExpression.target_feature` are the only
  identity authorities. The exact element and ID are retained in `ExactSemanticPath`. Membership,
  node-name, qualified-name, optional-target, and empty-result ladders are removed. A missing
  resolved target is `SemanticEvidenceError(RESOLVED_TARGET_MISSING)`.
- B8: a fact marked resolved but lacking its exact leaf raises
  `SemanticEvidenceError(RESOLVED_LEAF_MISSING)`. It can never be skipped.

### D6. DocumentTier owns B5

`SysideAdapter.document_tier(element)` performs one direct read:

1. Read `element.document`. Missing or false is `SemanticEvidenceError(DOCUMENT_TIER_MISSING)`.
2. Read `document.document_tier`. Missing or `None` is the same named error.
3. Load the installed `DocumentTier` through the adapter and require the value to be an exact enum
   member. A foreign or unknown value is `SemanticEvidenceError(DOCUMENT_TIER_UNKNOWN)`.
4. Return that enum member unchanged.

`expression.py` filters a reference only when the exact resolved element's tier is
`DocumentTier.StandardLibrary`. `DocumentTier.Project` and `DocumentTier.External` are retained.
`constraint_extraction.py` uses the same adapter operation for its inherited-context filter so the
repository has no second standard-library classifier. The exact target's document URL, source-file
path, package name, and qualified name have no classification role.

Removing `STANDARD_LIBRARY_PREFIXES` also removes its lazy barrel/export entry in
`agentic_mbse.sysml.__init__` and updates the public-export assertion. No dead compatibility export
remains.

A reference requested with standard-library filtering but lacking an exact resolved element raises
the B4 evidence error before B5. A real user package named `SI` remains project evidence. A real SI
unit reference is filtered because its document tier says StandardLibrary.

### D7. One codegen conversion boundary

The existing exported `orchestration/elaborated_pipeline.py` function
`elaborate_loaded_extractor(extractor, *, model_paths, source_referents, strict)` becomes the sole
conversion boundary. Both
`elaborate_model_paths` and `elaborate_admitted_sources` load and validate their own source sets,
then call this same function. Snapshot capture already reaches the admitted-source arm, so live
generation, snapshot capture, and other admitted-source callers share the conversion.

The sealed from-snapshot route decodes an `InstanceGraph` and never touches a raw expression. It is
outside the raw-source consumer matrix, and the reachability gate proves it cannot import the site
enumerator or reference inspector.

`source_referents` is an immutable raw-source-path-to-`root-N/<relative-path>` mapping, not a
resolver selection. The live arm constructs it from the caller's ordered model roots. The admitted
arm passes the admission manifest's staged-path mapping. It is used only to render public locations
and the finished graph; it does not classify documents or choose semantic targets.

Inside that one boundary:

1. Enumerate the closed set of production expression sites and build one private pre-graph
   `ExpressionEvidenceInventory` by exact expression-site identity.
2. Refuse every `IndexedReferenceUse` before calculation-definition extraction, `_ExactElaborator`,
   or `InstanceGraph` allocation.
3. Extract calculation definitions with the inventory. The calculation dependency compiler accepts
   its exact inventory row and performs no raw reference/dependency walk; text and IR reconstruction
   remain separate consumers of the shared traversal policy.
4. Run the internal exact graph builder with the inventory and no raw-expression dependency walk.
5. Validate the graph and executable-content gate.
6. Catch `SemanticEvidenceError`, `ElaborationInvariantError`, and `GraphValidationError` once and
   convert them to the existing `ElaborationDiagnosticError`.

The inventory covers every live expression-bearing consumer: calculation-definition dependency
compilation, calculation and constraint bindings, aliases, computed attributes, and constraint
predicates. Each row is keyed by the owning declaration ID plus a closed role, and contains only
the `ReferenceUse` tuple returned by D5. Pending elaboration records carry those values instead of a
raw expression for dependency resolution. `extract_expression_ir` remains a separate call for math
reconstruction and uses the same depth policy; its output cannot create a dependency edge.

The site enumerator is Codegen-owned contextual routing. It identifies only the closed consumer
roles above; it does not inspect operands or resolve a target. Calculation extraction receives a
private inventory lookup rather than a compatibility default. A missing or duplicate required site
is an invariant failure, so the compiler cannot fall back to `extract_feature_refs` when the
inventory is incomplete.

The pre-graph scan is not the sole index defense. Every consumer branches exhaustively over the
closed union, and the exact resolver accepts only `ExactReferenceUse`. An
`IndexedReferenceUse` reaching a consumer raises `SI_INDEXED_SOURCE_UNSUPPORTED` again. The two
layers keep the same public diagnostic, so tests distinguish them by control flow:

- Each normal indexed natural-route test instruments the downstream compiler, elaborator, and
  consumer entry and proves the inventory refuses before any of them runs.
- A targeted internal test bypasses only the inventory gate, injects an `IndexedReferenceUse` into
  each consumer adapter, and proves that consumer's exhaustive branch refuses it.

Both proofs must stay green. An end-to-end refusal by itself cannot show which layer caught the
index and cannot close an omitted preflight category.

#### Binding and deep-path values are valid by construction

The permissive `SourceReferenceEvidence` record is replaced on the exact route by a closed binding
union:

```python
BindingSourceEvidence = (
    ExactBindingSource | IndexedBindingSource | ExpressionBindingSource | LiteralBindingSource
)
```

`ExactBindingSource` requires an `ExactReferenceUse`; `IndexedBindingSource` requires an
`IndexedReferenceUse`; and expression/literal variants have no semantic path field. Common formal
metadata is composed into each variant. A bare or qualified binding with
`semantic_reference=None` cannot be constructed, and `_resolve_bindings` has no raw `RuntimeError`
arm for that state.

Deep literal overrides do not enter the expression union. One Codegen-owned
`exact_path_from_relationship(redefined_feature)` factory materializes the complete
`chaining_features` sequence. SysIDE types that selector as a sequence of `Feature`, not an
expression sequence. The factory requires every materialized segment to be a mapped `Feature` and
requires one typed target fact for each segment. It raises on the first absent or non-feature middle
segment and names its ordinal, authored target, and location. A mapped `IndexExpression` receives
`SI_INDEXED_SOURCE_UNSUPPORTED`; any other absent or non-feature segment receives
`SI_EVIDENCE_INCOMPLETE`. The factory never filters missing elements and never returns a shortened
path. This is the sole reviewed Codegen owner of that relationship selector.

The deep-override proof has two parts. A kept real-model contract test shows that every parsed deep
override segment is a `Feature` and that no `IndexExpression` can enter `chaining_features`. A
defensive factory test forces a mapped `IndexExpression`, which is necessarily non-`Feature`, and
requires `SI_INDEXED_SOURCE_UNSUPPORTED` before any target fact or shortened path is produced.
Structural exclusion and explicit refusal are both recorded; “not an expression route” is not
accepted as the whole index proof.

The dead name/path reconstruction cluster on the live `SysMLDataExtractor`
(`_extract_binding_source`, `_parse_expression_to_path`, `_extract_simple_reference`, and
`_build_reference_path`) has no `C_prod` caller and is deleted. The three audited off-route
modules (`usage_extractor.py`, `computed_attribute_extractor.py`, and `hierarchy_resolver.py`) are
not silently included in a public-route claim: they remain separately inventoried and a static
reachability test proves that neither raw-source arm imports or calls them.

#### Checked consumer and ownership manifests

Each repository keeps a local, source-controlled raw-selector manifest in its boundary test. A row
is `(module, qualified function, selector, semantic owner, route state, closure proof)`. A live
row's proof is its public failure test; an off-route row's proof is the reachability exclusion.
Agentic owns operand materialization, mapped metatype/index recognition, exact expression targets,
authored reference form, and the shared depth budget. Codegen owns only the reviewed contextual
exceptions: redefinition endpoints, multiplicity contextualization, enumeration discrimination,
and the total deep-relationship-path factory. Off-route rows are explicit and cannot satisfy a
live-route row.

Agentic also keeps a distinct typed-surface row for `FeatureReferenceFact.target`. That optional
field remains available only to the existing math-oriented `ExpressionIR`; it is non-authoritative
for semantic dependency evidence. The exact-route modules may neither import it nor accept it. This
row is not a raw-selector exemption and cannot make the raw-selector equality test green.

The boundary gates use the Python AST to discover direct attributes for `.operands`, `.referent`,
`.target_feature`, and `.chaining_features`; literal `getattr` calls for those names; simple local
or imported aliases of either form; and runtime metatype-name dispatch in the raw-SysIDE module
set. Every non-literal `getattr` in that module set is rejected because its selector cannot be
reviewed. Mutation tests introduce one direct read, one string-literal `getattr`, one local alias,
one imported alias, and one dynamic `getattr`; every mutation must kill the gate. The discovered
tuple set must equal the reviewed manifests exactly. A new selector, missing manifest row, stale
row, unexercised exemption, or live import of an off-route module fails.

Closure has three jointly load-bearing legs:

1. **Acquisition.** The repository raw-selector inventory equals the reviewed manifest exactly.
   Its public-root-reachable subset equals the manifest's live subset, with zero unowned reads.
   Every live row names a green public failure proof, and every off-route row has a green
   reachability exclusion. The AST evasion mutations above are green.
2. **Representation.** Production exposes only the closed `ReferenceUse` and binding-source
   variants. The deleted permissive helper/fact identifiers, their exports, compatibility aliases,
   and `has_index_segment: bool` are absent. Scoped strict type checks and runtime constructor tests
   prove that an index marker cannot be represented as an exact reference.
3. **Routes.** The natural-route matrices cover every live, admitted, and capture consumer. They
   prove both inventory-before-consumer refusal and the bypassed-inventory consumer backstop.

No leg substitutes for another. Work stops only when all three are green. This is stronger than one
exception converter or one manifest: it proves that the typed owner is the only legal evidence-
acquisition route and that weaker evidence cannot be reconstructed downstream.

#### Scoped strict type boundary

Strict checking applies only to the small closed-variant boundary files introduced or rewritten by
this revision. Agentic places the error/value types and inspector entry in `errors.py` and new
`sysml/reference_use.py`. Codegen puts the closed binding union/factory in new
`extraction/binding_source.py` and the evidence inventory,
site identity, and exact-only resolver adapter in new `elaboration/expression_evidence.py`. The
large existing `elaboration/elaborate.py` calls that adapter; it is not relabeled as a strict module.

The scoped lane must return zero errors:

```bash
uv run mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py
uv run --extra dev mypy --strict src/sysml_codegen/extraction/binding_source.py \
  src/sysml_codegen/elaboration/expression_evidence.py
```

Each command runs in its own repository. The existing repository-wide mypy command runs separately
and must match or improve its recorded baseline. A green scoped lane cannot hide a new repo-wide
error, and pre-existing repo-wide errors cannot waive the scoped zero-error gate.

The current public `elaboration.elaborate()` call shape is replaced atomically by this loaded-
extractor boundary and all repository callers migrate. The raw graph builder becomes private and
does not convert or render public errors. There is no overload preserving the old two-stage API.
`ElaborationError` remains the separate collected readiness result; parsing/admission errors remain
`SysMLParsingError` or snapshot errors.

Conversion preserves evidence as follows:

- The diagnostic code is selected once from a closed mapping. Agentic evidence failures map to
  `SI_EVIDENCE_INCOMPLETE`; exact type failures map to `SI_TYPE_INVALID`; existing elaboration and
  graph codes retain their code.
- `Diagnostic.consumer_display` receives the exact `reference` when present, otherwise `<model>`.
- `Diagnostic.detail` contains the operation, error detail, and `root-N/<relative-path>:line`
  location. It does not contain the diagnostic code.
- `raise ElaborationDiagnosticError(...) from error` preserves `__cause__`; an agentic wrapper's own
  `cause` field preserves the original SysIDE failure below it.
- `ElaborationDiagnosticError.__str__` remains the only renderer that prefixes the code. Tests
  assert exactly one code token in the public message.

Evidence integrity is not a leniency choice. In `strict=True` and `strict=False`, B1-B8 evidence,
type, stable-ID, and graph-integrity failures raise the same public `ElaborationDiagnosticError` and
produce no graph or snapshot. Lenient mode continues to collect only the already-supported
reference/readiness diagnostics for which a complete graph remains meaningful. Tests pin both
modes through live and admitted-source arms. Snapshot capture adds an atomic-output assertion: on
failure, no snapshot path is created or changed.

### D8. Diagnostic ownership

| Condition | Public code | Owner |
|---|---|---|
| B1-B5/B8 incomplete parser evidence or depth exhaustion | `SI_EVIDENCE_INCOMPLETE` | agentic cause; codegen public rendering |
| Incomplete deep relationship path | `SI_EVIDENCE_INCOMPLETE` | codegen total path factory; codegen public rendering |
| Missing/multiple/unsupported exact typing | `SI_TYPE_INVALID` | codegen extraction/elaboration |
| Missing/ambiguous contextual occurrence or producer | `SI_OCCURRENCE_MISSING` / `SI_OCCURRENCE_AMBIGUOUS` | codegen elaboration |
| Invalid redefinition family | `SI_REDEFINITION_INVALID` | codegen slot index |
| Unresolved/unsupported multiplicity | existing `SI_MULTIPLICITY_*` code | codegen occurrence construction |
| Valid indexed element expression not implemented | `SI_INDEXED_SOURCE_UNSUPPORTED` | agentic closed variant; codegen inventory/consumer refusal and rendering |
| Unsupported generated root output | `EXIT_POINT_TYPE_UNSUPPORTED` | codegen generation preflight |

Every public refusal includes exact reference identity when available and a root-relative
`file:line`. No B10 source-origin code is carried into production; D10 selects the single deletion
branch before production starts.

### D9. B9 fails before output mutation

The graph is the sole authority for registry wrapper types. The pure
`required_exit_point_wrapper_types(graph)` operation visits every module and output, validates root
outputs against the one `_EXIT_POINT_WRAPPERS` mapping, and returns the sorted unique wrapper tuple.
No public or private registry-generation function accepts a caller-supplied type collection.

`cli._generate_package_from_graph` calls this operation beside the existing preflights and before
link checks, constraint-plan rendering, output clearing, directory creation, or any write.
`generate_registry(graph, package_name, template_env, output_path)` calls the same operation again
inside the exported generation seam and uses its returned tuple directly. Re-deriving from the same
immutable graph is not a second authority; accepting another value is forbidden.

The `generate_registry_from_graph` and `generate_registry_function` aliases either remain direct
aliases of that four-argument function or are removed. They cannot wrap it with a fifth argument.
For `field_name == "root"`, only `float`, `int`, `str`, and `bool` are valid registry primitive
types.

An unsupported type raises `CodeGenerationError` with one stable token and fields:

```text
EXIT_POINT_TYPE_UNSUPPORTED: module='<module name>' output='<field name>/<channel name>' \
python_type='<type>' source='root-N/<relative-path>:<line>'
```

At `C_base`, the collector already rejects an unsupported root type with an untyped `RuntimeError`;
there is no warning-and-omit branch. The change replaces that exception with the named
`CodeGenerationError` and moves graph-derived validation into every exported generation seam. A
direct exported call on an unsupported graph raises the same error; it never relies on a caller
having run CLI preflight first.

The public proof calls `cmd_generate` with the exact pipeline-context builder replaced by a forced
context whose graph contains the unsupported root output. This retains the real public command,
`run_codegen`, `_generate_package_from_graph`, preflight, logging, and exit-status path while
injecting only the otherwise unrepresentable invalid graph. It asserts:

- return status is nonzero (`1`);
- the log contains `EXIT_POINT_TYPE_UNSUPPORTED` exactly once;
- the module name, `field_name/channel_name`, `python_type`, and source `file:line` are present;
- the output directory's complete relative-path-to-bytes map, including a sentinel, is byte-for-byte
  identical before and after the call.

The proof lives in `tests/conformance/test_generation_exit_type_preflight.py`.

A second API proof inspects every exported registry callable and shows the caller-supplied
`exit_point_primitive_types` parameter is absent. Graph mutations covering no root outputs, one
primitive, repeated primitives, and multiple primitive types produce exactly the graph-derived
sorted set. The empty, incorrect, or duplicate caller accounts reproduced by the audit are
unrepresentable because there is no input slot for them.

### D10. Retained probes and production gate

The three licensed pre-production probes, B2, B8a, and B10, were committed and run before the
failed candidate's production changes. Their locked inputs and measured verdicts remain historical
evidence for D1-D4 and B10; Revision 6 does not reinterpret them as evidence-edge closure. They are
rerun only if a locked input changes. B8b remains the separate post-D5 regression specified below.

#### B2 containment-address feasibility

`b2_containment_address_feasibility.py` loads real SysIDE fixtures and applies the D1 owner walk and
a minimal read-only prototype of D2. It has exactly seven topology rows:

1. direct package-owned target;
2. definition-owned target;
3. explicitly prefixed nested package target plus a no-prefix refusal for the same target;
4. repeated outer occurrences pinned to the consumer's index;
5. redefined usage mapped to one canonical feature slot;
6. calculation usage owner address and output scope;
7. multiplicity-bound writer in the multiplicity owner's domain.

Each row must visit at least one live element, record stable IDs and owner kinds, and produce the
expected address and concrete domain. Any unsupported stable owner shape, unstable/cyclic walk,
cross-outer result, split redefinition slot, unrelated writer, or nested no-prefix success kills
this design before production.

#### B8a pre-change real-corpus totality

`b8_resolved_fact_totality.py` runs against the frozen pre-change agentic/codegen commits and visits
only real reference and chain facts from the closed corpus. It imports no Revision-3 error API and
does not synthesize a missing leaf. It records fixture roots, source hashes, total resolved facts,
feature-reference facts, feature-chain facts, and missing-leaf facts. Both reference-kind counts and
the total must be nonzero. The only passing verdict is `REAL_CORPUS_TOTAL`, with
`missing_leaf_count == 0`. Any genuine resolved fact without a leaf kills the plan and returns to
design before D1-D7 production changes.

#### B8b post-D5 forced typed regression

After D5 lands `SemanticEvidenceError`, agentic's kept expression test constructs one resolved fact,
removes only its leaf, and asserts
`SemanticEvidenceError(RESOLVED_LEAF_MISSING)` with reference, location, and cause behavior. Codegen
then proves D7 converts the same error once at the live and admitted-source public boundary. This is
a post-API regression, not a pre-change probe and not a production kill-gate input.

#### B10 exact document-origin totality

`b10_document_origin.py` loads the two-file metadata fixture through both live and admitted-source
arms. It must observe at least one unit-bearing feature from each file, prove every feature has a
direct `element.document.url`, and prove `_source_file` selects that exact URL without consulting
`model_paths`.

The recorded verdict is `DELETE_UNREACHABLE`, with the probe/fixture commit SHA, SysIDE version,
counts, and per-file root-relative evidence. The sole-glob branch therefore stays deleted and no
replacement is added. If a locked input changes and a rerun differs, implementation stops and this
design returns for revision.

The canonical pre-change verdict files are `verification/probes/b2-verdict.json`,
`b8-real-verdict.json`, and `b10-verdict.json`. Probe scripts and verdicts remain after
implementation. B8b remains as ordinary kept agentic and codegen regression tests.

## Data and responsibility ownership

| Data or invariant | Single owner | Consumers |
|---|---|---|
| SysIDE metatype truth and `DocumentTier` | SysIDE through agentic adapter | agentic expression/fact extraction |
| Operand materialization, exact expression targets, index classification, authored form, and expression depth | Agentic `inspect_reference_uses` and its shared traversal primitives | codegen evidence inventory; Agentic IR/reconstruction entries |
| Closed `ReferenceUse` values and public evidence error | agentic-mbse | codegen boundary and exact resolver |
| Pre-graph expression-site coverage | Codegen `ExpressionEvidenceInventory` | calc-definition compiler, bindings, aliases, computed attributes, predicates |
| Closed binding-source variants | Codegen exact binding factory | pending-binding resolution and readiness screening |
| Complete deep relationship paths | Codegen `exact_path_from_relationship` | deep literal override resolution |
| General semantic-owner selection | codegen `elaboration/occurrence.py` | attachment, formals, occurrence builder, elaborator |
| Closed owner-kind/identity validation for `ContainmentAddress` | `build_containment_address` only | multiplicity and producer/address resolution |
| Feature slot and occurrence population | existing `FeatureSlotIndex` / `OccurrenceIndex` | address instantiation |
| Calculation output producer records | codegen exact elaborator | leaf/reference resolution |
| Raw-selector ownership and public-route membership | repository-local checked manifests | static boundary gates and final audit |
| Public evidence-error rendering | `elaborate_loaded_extractor` | live and admitted-source routes |
| Registry wrapper set | `required_exit_point_wrapper_types(graph)` | CLI preflight and every exported registry seam |
| TEAx behavior | generated package and Fusion tests | final product verification |
| Cross-repository artifact/import provenance | `verification/dependencies.json` and execution manifest | isolated test runners and Fusion lock proof |

Agentic does not choose codegen occurrences. Codegen does not infer parser metatypes, reference
identity, authored reference form, index presence, or standard-library status. Fusion does not
patch around either repository.

## Cross-repository API and independent landing

### Agentic semantic contract

Agentic makes an intentional pre-1.0 breaking contraction and behavior correction, then bumps its
package version from `0.1.2` to `0.1.3` in `pyproject.toml`, `agentic_mbse.__version__`, and
`uv.lock`. It exports `SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v2"`,
`SemanticEvidenceCode`, `SemanticEvidenceError`, `ExactSemanticPath`, `ExactReferenceUse`,
`IndexedReferenceUse`, and `inspect_reference_uses`. Version `0.1.3` is retained because the failed
candidate was never the certified or shipped artifact; Revision 6 replaces that candidate before
the first release of this API. `extract_feature_refs`, `feature_reference_facts`,
`feature_chain_facts`, `ResolvedSemanticReferenceFact`, `ExpressionRef`, and
`BindingInfo.references` are removed from the production surface and exports. The scoped strict
lane, standalone tests, and lint must pass from the committed tree before Codegen consumes it. The
repository-wide type check must match or improve its recorded baseline.

### Codegen pin and dependency contract

Codegen changes `agentic-mbse>=0.1.2` to `agentic-mbse>=0.1.3,<0.2` in `pyproject.toml` and refreshes
`uv.lock`. `_upstream_pins.py` adds
`AGENTIC_MBSE_PACKAGE_VERSION = "0.1.3"` and
`SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v2"` to `__all__`, and removes its obsolete
claim that the dependency floor is not real. `test_upstream_pins.py` compares the installed
`agentic_mbse.__version__` and semantic-evidence API constant to those exact pins. An editable
sibling remains a developer convenience only and is never landing evidence.

Because this item produces a materially different installable codegen artifact, codegen bumps from
`0.1.0` to `0.1.1` in `pyproject.toml`, `sysml_codegen.__version__`, and its lock/package-version
tests. Fusion pins that version exactly.

### Immutable artifact set

The proof uses source archives where tests or monorepo layout are part of the evidence, and wheels
where a downstream consumer only imports an installed distribution:

| Input | Frozen source/version | Verification artifacts |
|---|---|---|
| agentic-mbse | final descendant; package `0.1.3`; `https://github.com/1cFE/agentic-mbse.git` | source archive for its own suite; wheel for codegen/Fusion |
| sysml-codegen | production-artifact commit `C_prod`; package `0.1.1`; `https://github.com/1cFE/sysml-codegen.git` | source archive for its own default/execution suites; wheel for Fusion; later evidence-only commit excluded |
| TEAx / simkit | `744745f895677f3344b9884627369a6a47ed987f`; workspace `0.1.0`; `packages/teax-simkit` distribution `0.1.0`; `git@github.com:rwestwood89/teax.git`; source-tar SHA-256 `3dea651f0b67340a11e28bac61ff1710b3cf20ef8b7ce498172f79c7ca0f8346` | source archive, because TEAx tests and codegen execution import the monorepo's `simkit` tree |
| 1costingfe | `02543850089be175ea7c28b92a8b2a4184e1637e`; package `0.1.0`; `https://github.com/1cFE/1costingfe.git`; source-tar SHA-256 `f8c38bb58af43d667931ad8db9eb4ebd86168f77352d90c98462ae47376d056a` | source archive for its own suite; wheel for Fusion |
| Fusion Tea | final lock/evidence commit `F_final`, descended from `824a876e281a3b9aef58b1873bfbd0b20c4ab77b`; package `0.1.0`; `https://github.com/1cFE/fusion-tea.git`; parent source-tar SHA-256 `f83e056ce799a1105aba920baa1d5370891615a4530899bdc4eecbaf41ed38e7` | source archive, because its models, tests, lock, and project files are the evidence |

For every row, the later evidence-only `verification/dependencies.json` records repository URL,
full commit SHA, declared package/workspace version, deterministic `git archive` filename and
SHA-256, and any built wheel's filename, distribution/version tag, and SHA-256. It records `C_prod`,
never the later codegen evidence commit. The dependency record also pins Python, SysIDE `0.8.4`,
the complete transitive wheelhouse inventory, and its hash-pinned requirements file.

Each source suite runs from a fresh extraction of its recorded archive, not a named sibling
checkout. Each downstream wheel is built from that extraction and installed from the recorded
wheelhouse with `--no-index`, `--find-links`, and `--require-hashes`. The runner rejects a dirty
source, a commit/archive mismatch, a wheel whose metadata version differs, or an imported file
outside the recorded extraction/install roots.

### Acyclic production and evidence topology

Codegen has two final commits with different jobs:

1. `C_prod`, the production-artifact commit, contains every production source, test, fixture,
   public document, package-version change, dependency minimum, `_upstream_pins.py` value, and
   `uv.lock` entry needed to build, consume, and test codegen. It does not contain the final
   cross-repository dependency record or evidence lock.
2. Build the deterministic source archive and `sysml_codegen-0.1.1` wheel from `C_prod`, then record
   both SHA-256 values outside the repository while downstream verification is in progress.
3. Fusion pins the exact full `C_prod` SHA in `pyproject.toml` and `uv.lock`, consumes the wheel with
   the recorded hash in the isolated composed run, and lands `F_final`. Build and hash Fusion's
   source archive from `F_final`, then run the required Fusion verification.
4. `C_evidence` is a direct child of `C_prod` created only after `F_final` passes. It records the
   production-artifact SHA/archive/wheel hashes and the final agentic, TEAx/simkit, 1costingfe, and
   Fusion SHAs/artifact hashes. `C_evidence` is not a codegen production artifact, no downstream
   repository pins it, and no artifact identity in the record names it.

The certified codegen identity is exactly the tuple `(C_prod full SHA, C_prod source-archive
SHA-256, sysml_codegen-0.1.1 wheel filename and SHA-256)`. A `git archive` of `C_evidence` is never
built or certified for this item. No record contains its own hash or commit SHA. Git identifies
`C_evidence` from outside its tree when audit checks it; that SHA is not written back into an
evidence file.

The commit boundary is closed:

| Commit | Verification files in that commit |
|---|---|
| `C_prod` | `verification/fixture-manifest.json`, `verification/probe-fixture-lock.json`, `verification/probes/b2-verdict.json`, `verification/probes/b8-real-verdict.json`, `verification/probes/b10-verdict.json`, and `verification/expected-transitions.md`; retained probe scripts/fixtures and all verification tests also land here |
| `C_evidence` only | `verification/dependencies.json`, `verification/wheelhouse-requirements.txt`, `verification/execution-provenance.json`, `verification/independent-green.json`, `verification/reconciliation-ledger.md`, and `verification/evidence-lock.json` |

`verification/evidence-lock.json` hashes `dependencies.json`, `execution-provenance.json`,
`independent-green.json`, `reconciliation-ledger.md`, the hash-pinned requirements file,
`probe-fixture-lock.json`, and `expected-transitions.md`. It does not hash itself. The other five
evidence-only files do not name or hash `C_evidence` or `evidence-lock.json`.

Audit receives `C_prod`, `F_final`, and `C_evidence` as command inputs and checks this boundary
mechanically:

1. `C_evidence^` equals `C_prod`, and the `C_prod..C_evidence` changed-path set equals the six
   evidence-only paths in the table. No production source, test, fixture, docs, package metadata,
   pin, lock, probe verdict, or expected-transition file differs.
2. A fresh archive and wheel rebuilt from `C_prod` match the filenames and hashes in
   `dependencies.json`; the codegen row names `C_prod`, and neither the record nor the lock names
   `C_evidence`.
3. Fusion's final `pyproject.toml` and `uv.lock` name `C_prod` exactly and contain neither
   `C_evidence` nor a sibling path/editable source. The installed codegen wheel hash in the Fusion
   run matches the certified `C_prod` wheel.
4. Every other artifact SHA/hash and every evidence-file digest recomputes. The independent-green
   report contains the required command, import-root, status, and no-unexpected-skip records.

### Executable codegen execution pins

The current execution pin deliberately rejects site-packages and hard-codes sibling checkout shape
(`tests/execution/environment_pins.py:19-37`; `tests/helpers/teax_discovery.py:17-30`). It changes to
artifact provenance rather than becoming less strict:

1. The isolated runner writes `verification/execution-provenance.json` from the verified dependency
   record. It contains the explicit Python executable, extracted codegen source root, installed
   agentic wheel root, extracted TEAx root, `packages/teax-simkit` root, and the source/wheel hashes
   that established each root. The environment variable `CODEGEN_EXECUTION_PROVENANCE` names that
   file.
2. `environment_pins.py` loads that closed manifest and requires the resolved
   `sysml_codegen`, `agentic_mbse`, and `simkit` files to be under their exact declared roots. A
   site-packages agentic import is valid only when it is the recorded wheel install. Codegen remains
   the extracted source under test, and simkit remains the recorded TEAx source subtree.
3. `teax_discovery.py` requires explicit `TEAX_SIMKIT_PATH`; the checkout-relative sibling fallback
   is removed. `tests/execution/conftest.py` requires it to equal the manifest's simkit root before
   adding that root to `sys.path`.
4. `tests/unit/test_environment_pins.py` and `test_teax_discovery.py` create temporary manifests and
   prove wrong source roots, a different wheel root, wrong artifact hashes, absent explicit TEAx
   path, and the old sibling shape all fail. The execution fixture records the manifest digest and
   resolved import files with its results.

This preserves the purpose of the existing pin: acceptance evidence still fails on the wrong tree.
It now recognizes immutable extracted source and wheel artifacts instead of assuming the developer's
adjacent worktrees.

### Fusion dependency and lock changes

Fusion's required landing changes `pyproject.toml` and `uv.lock` even when no model violates the new
occurrence rules:

- Pin `agentic-mbse[extract-full,web]==0.1.3`, `sysml-codegen==0.1.1`, and
  `1costingfe==0.1.0` in project dependencies.
- Replace the three editable path entries in `[tool.uv.sources]` with immutable Git sources at the
  exact agentic production commit, codegen `C_prod`, and frozen 1costingfe commit. Those identities
  come from the external artifact-build record used to prepare Fusion and are copied unchanged into
  the later `dependencies.json`. The 1costingfe rev is the frozen SHA above.
- Regenerate `uv.lock` and require the three package rows to contain immutable Git source URLs and
  precise commit IDs. Any `editable =` or sibling `path =` row for them fails a static lock test.
- Prove `uv lock --check` from the Fusion source archive. The offline composed run does not invoke
  `uv run`; it installs the hash-pinned agentic, codegen, and 1costingfe wheels into the fresh
  environment and runs Fusion's suite with that environment's explicit Python.

### Required isolated runs

The artifact set is accepted only after these clean runs:

1. agentic source archive: the fast suite, focused semantic-evidence tests, type check, and lint.
   From the fresh extracted archive root, the runner uses the repository's `SYSIDE_LICENSE_KEY`
   environment pattern:

   ```bash
   set -a
   source /home/reid/1cfe/agentic-mbse/.env
   set +a
   uv run pytest tests/ -m "not slow"
   uv run mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py
   uv run mypy src/
   uv run ruff check src/ tests/
   ```

   The sourced file supplies the license secret only. It is not copied into an archive or report,
   and no Python import may resolve under that sibling checkout. `tests/conftest.py:1-8` retains its
   `load_dotenv()` behavior, while the exported value makes the isolated run independent of a
   copied `.env`. A missing license key or an undeclared parser-test skip fails the gate.
   **[OWNER-VERBATIM, 2026-08-17]** “do not rerun the PDF suite anymore.” The slow PDF/HTML corpus
   suite is permanently outside parser-work validation and is not invoked or counted here. The 15
   paid/network cases remain unrun external inputs, not passes or skips;
2. 1costingfe source archive: its complete pytest suite and configured lint;
3. TEAx source archive: the root-configured simkit and battery-demo suites;
4. codegen source archive: scoped strict checking of `extraction/binding_source.py` and
   `elaboration/expression_evidence.py`, the recorded repository-wide mypy baseline, default
   unit/conformance suite, licensed real-model suite, snapshot/live parity, generated-package
   tests, and the complete `execution` marker lane using the manifest and extracted TEAx source;
5. Fusion source archive: `uv lock --check`, full configured pytest suite, model validation, and the
   final generated Fusion/TEAx execution proofs using installed agentic/codegen/1costingfe wheels.

The run records `pip freeze`, artifact/manifest digests, Python, SysIDE, TEAx/simkit, 1costingfe,
agentic, codegen, and Fusion versions, resolved import files, test commands, statuses, and skips. An
unexpected skip or any sibling working-tree import fails the gate. Model sources change only if the
semantic tests find a real violation; the Fusion dependency/lock changes above are mandatory.

For both Agentic and Codegen, the scoped strict command must return zero. The repository-wide mypy
command is a separate baseline comparison and must introduce no new errors. Neither result is
reported as the other.

## Baseline, fixture, and transition evidence

### Frozen production baseline

`verification/probe-fixture-lock.json` starts with these immutable full SHAs:

| Repository/input | Production baseline / closed predecessor descendant | Version/role |
|---|---|---|
| sysml-codegen | `7b29d8b636e284364a4fdce9079f153c51c867ea` | production parent; package `0.1.0` before this item |
| agentic-mbse | `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb` | evidence parent; package `0.1.2` before this item |
| fusion-tea | `824a876e281a3b9aef58b1873bfbd0b20c4ab77b` | verification parent; package `0.1.0` |
| TEAx / teax-simkit | `744745f895677f3344b9884627369a6a47ed987f` | immutable execution source; workspace/package `0.1.0` |
| 1costingfe | `02543850089be175ea7c28b92a8b2a4184e1637e` | immutable runtime/test source; package `0.1.0` |

The codegen comparison baseline is the production parent. It remains the historical “before” tree;
it is not the Revision-6 branch base, which is `C_base` above. No baseline is recaptured after
production code changes and then called “before.”

### Probe/fixture commit lock

The retained probe/fixture commit already exists at
`20f9e60a19b30bc1ec9a27aacb08380f4bc45602`, with comparison-baseline parent
`7b29d8b636e284364a4fdce9079f153c51c867ea`. Its manifest-only lock child is
`43edf9bde4db44e7973458ada732d2cd75e764f6`. Both are ancestors of `C_base` and are preserved in
place; Revision 6 does not recreate them or call a new commit the pre-change probe boundary.

At Revision-6 gate 1, the committed runner requires `probe_fixture_commit` to equal that locked
40-character SHA, requires its recorded parent relationship, and recomputes every probe/fixture
hash. The recorded verdicts must name the same probe and lock commits. A dirty tree or mismatch
stops the plan. The probes rerun only under D10's locked-input rule.

The lock stores SHA-256 for every probe, every source fixture file in the 37 canonical roots, every
added fixture file, the item fixture manifest, and the canonical batch manifest. Any changed byte
invalidates the verdicts and returns the item to design before any replacement lock or rerun.

### Closed fixture inventory

`verification/fixture-manifest.json` is the only input inventory for this item. It expands the
existing canonical `tests/fixtures/v6_recapture_batch/batch.json`, requires exactly 37 fixture roots
and 37 records (15 graph records and 22 typed refusals), and pins that file's current SHA-256:
`bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288`.

For those 37 roots, the item manifest explicitly enumerates every `.sysml` and `.kerml` source by
repository-root-relative path and SHA-256. The batch manifest's snapshot hashes do not substitute
for source hashes.

It then adds exactly these root-relative source files:

1. `tests/fixtures/occurrence_domain_derivation/model.sysml`
2. `tests/fixtures/occurrence_calc_domain_derivation/model.sysml`
3. `tests/fixtures/multiplicity_writer_authority/model.sysml`
4. `tests/fixtures/indexed_expression_source/model.sysml`
5. `tests/fixtures/feature_typing_integrity/model.sysml`
6. `tests/fixtures/feature_metadata_multifile/library.sysml`
7. `tests/fixtures/feature_metadata_multifile/design.sysml`

The inventory therefore has 37 canonical roots plus six added roots containing seven added source
files. The loader rejects an unlisted `.sysml` or `.kerml` file under any listed root and rejects a
missing, duplicate, absolute, `..`-containing, or hash-mismatched path.

Explicit exclusions are:

- Fusion Tea sources, which are verified separately at the immutable Fusion commit;
- negative/forced objects synthesized in unit tests, which are test inputs but not baseline models;
- generated snapshots and package outputs, which are outputs hashed by the baseline ledger rather
  than source inputs;
- SysIDE standard-library documents, which are installed dependencies and are recorded by SysIDE
  version and document tier rather than copied into project fixtures;
- every pre-existing dirty, staged, or untracked worktree artifact outside the manifest.

Anti-vacuity checks require: 37 canonical roots; 15 graph and 22 typed-refusal baseline records; at
least one enumerated source file per canonical root; six added roots; seven added source files; seven B2
topology rows; at least one real feature-reference and one real feature-chain fact in B8a; at least
two parser documents and one unit-bearing feature from each in B10; and at least one graph or named
refusal record for every inventory root. All evidence paths are repository-root-relative
`root-N/<relative-path>` values, never machine-absolute paths.

### Baseline capture

The retained baseline record captured the 37 canonical roots at the comparison baseline and the
six added roots at the probe/fixture commit while production source was byte-identical to the
baseline parent. Revision 6 preserves that record. It stores:

- source commit, fixture path/hash, Python/SysIDE/agentic versions;
- graph codec bytes and semantic node/edge identity rows;
- public diagnostic code, reference, and location for refusals;
- generated package relative paths and SHA-256 for successful models;
- live/snapshot parity and executable output hashes where applicable.

`verification/expected-transitions.md` is the only allow list. Every changed edge, diagnostic, or
generated byte must name a transition row and proving test. All other maintained outputs stay
byte-identical.

### Transition ledger seed

| Transition | Old behavior | Required result | Proof owner |
|---|---|---|---|
| A1 occurrence selection | nearest/descendant/sole candidate may answer | exact address in consumer domain or named missing/ambiguous refusal | `test_occurrence_domain_derivation.py`; public mutation test |
| A2 calculation output | nearest or globally sole calculation may answer | exact output-index record contextualized by usage owner and consumer domain | `test_occurrence_calc_domain_derivation.py`; public mutation test |
| A3 lineage miss | one descendant may answer | lineage-local result or `SI_OCCURRENCE_MISSING` | expanded `test_definition_owned_reference_positions.py` |
| A4 package/model root | model root may answer a consumer miss | direct one-step package-owned no-prefix result; nested no-prefix refusal | B2 probe and `test_occurrence_domain_derivation.py` |
| A5 indexed expression | one input route refuses while computed/alias/predicate routes may erase the index | every expression site returns `IndexedReferenceUse` and refuses pre-graph; consumer backstop also refuses | consumer matrix in `test_expression_evidence_integrity.py` |
| A6 multiplicity writer | unrelated sole writer may answer | owner-address writer or `SI_MULTIPLICITY_UNRESOLVED` | `test_occurrence_multiplicity_authority.py`; public mutation test |
| B1-B5 evidence | fallback, partial traversal, raw unit/depth walk, optional target, or QN filter continues | exact evidence/DocumentTier or `SI_EVIDENCE_INCOMPLETE`; no alternate raw route | agentic owner tests; codegen consumer/ownership matrix |
| Deep relationship path | missing middle segment is filtered | total exact path or `SI_EVIDENCE_INCOMPLETE` at that segment | public deep-override regression |
| B6/B7 metadata | weak type or skipped redefinition identity may pass | sole qualified type and one exact slot family, or named refusal | `test_feature_typing_integrity.py`; occurrence tests |
| B8 leaf | resolved fact may be skipped | pre-change real corpus is total; post-D5 missing leaf raises the typed error | B8a retained real probe; B8b agentic/codegen regressions |
| B9 exit type | CLI preflight is correct but exported registry accepts a second caller account | graph-derived wrappers in every seam; `EXIT_POINT_TYPE_UNSUPPORTED` before mutation | `test_generation_exit_type_preflight.py`; exported-API proof |
| B10 source origin | sole glob may supply a file | measured `DELETE_UNREACHABLE`, then fallback deletion | B10 retained probe and metadata test |

A4 has its own row because package anchoring and consumer-root fallback are separate behavior from
A1/A2 contextual selection.

## Test design

### Occurrence and producer matrix

Real licensed tests cover:

- same-domain and nested definition/usage ownership;
- a direct package-owned no-prefix target;
- the same nested package target with an explicit prefix (success) and without it (refusal);
- sibling part and calculation usages;
- two repeated outer occurrences with the consumer pinned to each one in turn;
- a redefined usage sharing one canonical slot;
- a package-owned calculation and its output;
- an unrelated globally sole occurrence, calculation producer, and multiplicity writer, all refused;
- scalar ambiguity and modeled plural expansion;
- valid root/nested multiplicity writers plus incomparable/multiple writers;
- declaration and source-file order reversed.

For the calculation index specifically, assertions inspect the bucket records and then the public
result for sibling, repeated-outer, package, and unrelated domains. The sibling bare output is
ambiguous; an explicitly rooted sibling is exact. Each repeated outer selects its own node. The
package producer resolves only from its package. The unrelated sole producer refuses.

### Public every-and-only mutation proofs

`tests/execution/test_occurrence_derivation_mutation_teax.py` parameterizes every positive
A1-A4/A6 topology, including calculation-output producers:

1. Generate a package through the live public route and through a v6 snapshot; require byte parity.
2. Record the modeled source's single public input token, producer module/output identity, and every
   intended consumer channel.
3. Change only that input off its modeled default and execute the generated TEAx package.
4. Assert every intended consumer/output changes, every sibling and unrelated output is unchanged,
   and repeated outer occurrence `i` changes only consumers in occurrence `i`.
5. Assert the public input surface contains the modeled source exactly once and the graph contains
   no extra edge for it.

Internal graph assertions localize a failure but do not satisfy a row without the public mutation
leg.

### Evidence and public-boundary matrix

- Agentic adapter tests force a live `.isinstance()` exception and inspect the preserved cause.
  Separate non-live test doubles prove the mock path.
- Real operator, feature-reference, feature-chain, and `IndexExpression` nodes prove mapped
  dispatch. A failing operand iterator and depth-exhausted tree prove no partial result escapes.
- Real bare and chain references construct `ExactReferenceUse`. Forced missing referent, target,
  leaf, and middle segment cases raise `SemanticEvidenceError` with reference and location.
- Real StandardLibrary, Project, and External document tiers prove B5. A project document whose
  package is named `SI` remains. Missing, `None`, and foreign tier values fail.
- Boolean/Integer/Real/String qualified typings succeed. User-defined `Real`, zero, multiple, and
  unsupported typings fail as `SI_TYPE_INVALID`.
- Strict and lenient calls through both live and admitted-source arms assert the same public class,
  code, cause chain, reference, root-relative location, one rendered code token, and no graph,
  snapshot, or generated output on evidence-integrity failure.
- B2, B8a, and B10 pre-change probes include their anti-vacuity counts and kill verdicts. B8b's
  forced regression runs only after D5 exists.
- B9 asserts token, module/output identity, type, file:line, status `1`, byte-identical output
  preservation, graph-derived wrapper-set changes, and the absence of any caller type-set parameter
  on every exported alias.

The natural-route closure matrix is mandatory; calling an internal helper is not a substitute:

| Consumer | Exact positive | Indexed refusal | Operand/depth failure | Missing exact target | Public arms |
|---|---|---|---|---|---|
| calculation-definition dependency compiler | required | required | required | required | live + admitted/capture |
| calculation and constraint binding | required | required | required where structural | required | live + admitted/capture |
| alias | required | required | required | required | live + admitted/capture |
| computed attribute | required | required | required | required | live + admitted/capture |
| constraint predicate | required | required | required | required | live + admitted/capture |
| deep literal override | required | structural exclusion + forced mapped-index refusal | not an expression route | missing middle required | live + admitted/capture |

Every failing cell asserts the exact public diagnostic, authored reference, root-relative
`file:line`, preserved cause chain, and no returned graph. The capture arm additionally asserts no
snapshot file creation or byte change. The matrix includes a unit wrapper and a nested index, and
runs strict and lenient modes wherever the public API offers both.

For every indexed expression row, the normal public route proves the inventory refuses before the
compiler, elaborator, or consumer runs. Its paired internal test bypasses the inventory and proves
the named consumer's closed-union backstop. The deep-override row instead pairs a real-model
`Feature`-only shape proof with a forced mapped `IndexExpression` refusal at the total path factory.

Deletion of the Agentic helpers has its own natural-consumer matrix:

| Agentic consumer | Exact behavior | Indexed behavior | Closure proof |
|---|---|---|---|
| aggregation reference and chain sites | retain exact root, members, and leaf before term construction | refuse before `SingletonTerm` | both executable sites |
| binding extraction | retain ordered uses and exact target document identity | retain closed variant; never project to a path | cross-file and same-file cases |
| ADR002 validation | use exact owner/document metadata | count as dynamic but never flatten to exact or empty | ordinary and dynamic scan routes |
| internal expression/IR entries | consume the shared traversal result | preserve closed variant or issue the named refusal required by that entry | all three internal call sites |

Every row runs through its natural public or package entry. Symbol-absence tests then prove that no
old helper, fact type, bool marker, alias, or barrel export remains.

### Static removal checks

Tests fail if production code retains:

- nearest/descendant/model-root/sole-candidate selector arms;
- the graph-wide calculation-output scan;
- production class-name metatype dispatch or swallowed operand iteration;
- QN/path/origin standard-library classifiers;
- first-typing/simple-name/unknown-pass-through type mapping;
- skipped redefinition endpoints;
- the sole-glob source fallback;
- the untyped registry collector failure for unsupported root outputs;
- a registry parameter or context field carrying caller-supplied exit-point types;
- the deleted Agentic helper/fact identifiers, `has_index_segment`, their aliases, or their exports;
- a raw SysIDE selector not equal to one reviewed ownership-manifest row;
- literal or dynamic `getattr` and local/import alias routes that evade raw-selector ownership;
- a stale ownership-manifest row, an unexercised exemption, or a live edge to an off-route module;
- the dead `SysMLDataExtractor` name/path reference-reconstruction helper cluster.

The scoped strict gates are also required static checks. Symbol absence cannot substitute for
closed-variant exhaustiveness, and a strict type result cannot substitute for route coverage.

## File-level implementation map

| Repository / files | Change |
|---|---|
| agentic `src/agentic_mbse/errors.py`, `sysml/reference_use.py`, `data_models.py`, `__init__.py` | Public semantic-evidence enum, error, API version, provenance-complete closed reference-use values, and deletion/de-export of the permissive facts and bool marker |
| agentic `sysml/syside_adapter.py`, `sysml/__init__.py` | Live metatype propagation, mapped index dispatch, direct `document_tier`, and obsolete export removal |
| agentic `sysml/expression.py`, `aggregation.py`, `binding.py`, `validation/adr002.py`, `constraint_extraction.py` | One reference inspector, shared traversal budget, total operand materialization, exact targets, and migration of every production helper consumer to the closed union |
| agentic `pyproject.toml`, `uv.lock`, tests, test ownership manifest, `docs/patterns/plant-idiom.md` | 0.1.3 package contract, semantic-evidence/v2 proofs, selector closure, and supported/refused modeling shapes |
| codegen `elaboration/occurrence.py` | General owner selector; containment-local kind/identity validation; address resolver; exact multiplicity owner; strict redefinition identities |
| codegen `elaboration/elaborate.py`, `elaboration/expression_evidence.py`, `expression_compiler.py`, `elaboration/__init__.py` | Producer index, strict expression-evidence inventory/adapter, exact-reference-only resolution, total deep-relationship path factory, and raw private graph builder |
| codegen `extraction/binding_source.py`, `elaboration/binding_evidence.py`, `source_evidence.py`, `unit_annotation.py` | Strict closed binding-source variants, removal of optional semantic paths, and typed-IR-only unit unwrapping |
| codegen `orchestration/elaborated_pipeline.py` | Single evidence conversion boundary for live/admitted extraction and elaboration |
| codegen `extraction/extractor.py`, `feature_metadata.py` | Delete dead reference reconstruction helpers; exact typing; B10 fallback deletion after verdict |
| codegen `cli/__init__.py`, `generation/registry.py` | Graph-derived exit-wrapper authority on every exported route and replacement of the untyped collector failure with fail-before-mutate `CodeGenerationError` |
| codegen `_upstream_pins.py`, `pyproject.toml`, `uv.lock` | Exact agentic package/API pins, codegen 0.1.1, dependency minimum, lock |
| codegen tests and local test ownership manifest | Dual-layer natural-route closure, deep-path index exclusion/refusal, exact selector-manifest equality with AST-evasion mutations, scoped strict gates, off-route reachability, and direct exported-registry rejection tests |
| codegen `tests/execution/environment_pins.py`, `tests/helpers/teax_discovery.py`, execution tests | Manifest-pinned immutable source/wheel imports; explicit TEAx path; rejection tests |
| codegen fixtures/tests/probes and `C_prod` verification files | Closed inputs, retained probes, A/B/public proofs, probe lock, expected transitions, and production tests |
| codegen `C_evidence` verification files | Final dependency/wheelhouse record, execution and independent-green results, reconciliation ledger, and non-self-hashing evidence lock only |
| Fusion `pyproject.toml`, `uv.lock` | Exact package versions, immutable Git source revs, no sibling editable/path sources |
| Fusion models | Edit only on a measured semantic violation |
| TEAx and 1costingfe | No source changes; archive, hash, test, and consume only at their frozen commits |

## Documentation and backlog obligations

The same landing unit updates:

- `docs/architecture/overview.md` and reference documents 00, 01, and 19 for the one owner walk,
  containment address, producer index, conversion boundary, and exact typing/evidence behavior.
- `docs/architecture/reference/20-module-registry-generation.md` REQ-REG-09. Correct the stale
  warning wording: the baseline collector raised an untyped `RuntimeError`. Document its replacement
  by graph-derived `CodeGenerationError` refusal before output mutation, including
  `EXIT_POINT_TYPE_UNSUPPORTED`, identity, location, status, and preservation proof.
- `docs/architecture/verification-matrix.md` REQ-REG-09. Replace
  `test_hygiene_tail_registry.py` with
  `tests/conformance/test_generation_exit_type_preflight.py` and record PASS only after the complete
  public proof passes.
- Diagnostic reference documentation for `SI_EVIDENCE_INCOMPLETE`, `SI_TYPE_INVALID`,
  `SI_INDEXED_SOURCE_UNSUPPORTED`, and `EXIT_POINT_TYPE_UNSUPPORTED`.
- A checked-in semantic-selector ownership manifest in each production repository. Each row names
  the raw selector, typed owner, route state, and public failure proof; the manifest and AST/alias/
  `getattr` discovery must agree exactly. Agentic separately records the math-only optional IR target
  as non-authoritative and forbidden at the exact-route boundary.
- Agentic's single authoritative `docs/patterns/plant-idiom.md` with supported bare, qualified,
  feature-chain, package, definition-domain, plural, and refusal shapes. Indexed form is documented
  as valid but not implemented.
- `[INDEXED-ELEMENT-EXPRESSION-SUPPORT]` under P-001 and
  `[OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE]` as separate agent-grade backlog rows before close.
- P-003's agent-written first-application status so every definition-owned lineage miss is described
  as refusing after A3. Its owner-verbatim promise is unchanged.
- The epic's stale predecessor wording, `.project/CURRENT_WORK.md`, product index/status, and the
  explicit block on `elaborator-downstream` during close-out.

## Sequencing and landing gates

Revision 6 does not resume the current implementation checklist. It needs the review's targeted
confirmation and a replacement plan. That plan uses these gates:

1. **Branch from the audited production tree.** Create the implementation branch directly from the
   old `C_prod`, `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, and use Agentic input
   `2171016d3e3e0805525aa4cf787c55c6293dd00c`. Do not branch from this documentation checkout or
   from a parent of the failed candidate. Preserve D1-D4, the probes, and the verification harness.
   Add failing natural-route tests and the initial local ownership manifests before production
   edits.
2. **Close Agentic's evidence surface.** Land semantic-evidence/v2 with one provenance-complete
   reference inspector, mapped index retention, shared traversal budget, exact targets, and exact
   manifest equality. Delete the permissive helpers/facts, bool marker, aliases, and exports. Migrate
   aggregation, binding, ADR002, and internal expression consumers. Make the scoped boundary files
   pass the scoped strict gate. Build a clean Agentic source archive and wheel and run its fast plus
   focused evidence suites. The PDF suite is outside this contract.
3. **Make Codegen consume only typed evidence.** Build the private evidence inventory before graph
   construction. Convert every binding and dependency site to closed variants or
   `ExactReferenceUse`. Add the total deep-relationship path factory, delete the raw AST unit helper
   and dead reference reconstruction helpers, and make the Codegen ownership manifest exact. The
   scoped boundary files pass the strict gate. D1-D4 source and behavior remain unchanged.
4. **Make registry authority graph-derived.** Remove caller-supplied exit-point type sets from the
   registry API and aliases. Derive the required wrappers inside the exported generator and prove
   identical refusal before output mutation through CLI and direct-call routes.
5. **Close the public route matrix.** Prove exact success and index, depth, operand, and missing-
   target refusal for every live, admitted, and capture consumer in strict and lenient modes. For
   each indexed expression consumer, prove both inventory-before-consumer refusal and the targeted
   bypassed-inventory backstop. Prove the deep override's real `Feature`-only shape and forced
   mapped-index refusal. Capture failures create or change no snapshot. Re-run the existing
   occurrence mutation and output reconciliation proofs to show D1-D4 stayed intact.
6. **Rebuild the immutable chain.** Seal a new `C_prod`, build its source archive and wheel, pin it in
   Fusion, land and verify a new `F_final`, then create a direct-child evidence-only `C_evidence`.
   Every final command runs through the committed runner. No result cites an editable sibling
   checkout, and no downstream repository pins `C_evidence`.
7. **Audit the closure invariant.** A fresh audit requires all three legs: exact selector ownership
   with evasion coverage, closed representation with deleted weak surfaces and scoped strict gates,
   and the full natural-route matrices with layer-distinguishing assertions. It also verifies
   off-route reachability and artifact topology. Any missing leg refuses certification.

Any failure in steps 2–5 changes the owning production repository and restarts the affected
artifact chain. It is never patched in `C_evidence`.

## Integration strategy

This is an in-place contract replacement, not a parallel implementation. Agentic lands
semantic-evidence/v2 first. Codegen then pins that artifact and removes every production import or
raw read that can reconstruct weaker evidence. The Codegen public API remains the conversion
boundary; its private pregraph inventory changes without adding a second public elaboration mode.
Fusion changes only after the replacement Codegen artifact is sealed.

Compatibility is deliberately narrow. Agentic's permissive fact/helper surface is deleted from
production rather than manifested or wrapped; every in-repository consumer migrates atomically.
Existing Codegen public elaboration arms keep their signatures and diagnostics. The other intended
breaking contraction removes caller-supplied wrapper-type authority from the registry generator and
every exported alias.

## Potential risks

| Risk | Control |
|---|---|
| The ownership manifest becomes a stale allowlist | AST and alias/`getattr` discovery must have exact set equality with the checked-in manifest; stale rows and every evasion mutation fail as hard as new unowned reads |
| A new consumer bypasses the pregraph inventory | Production dependency edges accept only closed variants; the natural-route matrix proves both the inventory and each consumer backstop over every live/admitted/capture arm |
| ExpressionIR grows into a second universal semantic tree | D5 keeps it neutral and existing-purpose; only the reference inspector owns dependency-reference evidence |
| Index refusal is added only to another preflight | `IndexedReferenceUse` cannot enter exact resolution, and every consumer must prove the same public failure independently |
| Scoped strict checking is weakened by a monolithic import surface | Closed variants and adapters live in four narrow boundary files; their zero-error strict lane is reported separately from each repository-wide baseline |
| Off-route legacy modules hide a live selector | Reachability is tested from the public roots; a reachable module must enter the manifest or be removed before closure |
| Cross-repository artifacts certify different code | The existing `A_final` → `C_prod` → `F_final` → `C_evidence` topology is rebuilt, and final commands run only through the committed runner |

## Closed predecessor reconciliation

| Repository | Approved immutable baseline | Current closed-predecessor descendant | Reconciliation |
|---|---|---|---|
| sysml-codegen | `26e19f9044a66ae267fe313684bf1c698a1c1f70` | `7b29d8b636e284364a4fdce9079f153c51c867ea` | Verified descendant. It includes usage-owner repair `98970c994882b91c69f3ee21132192e64c0a566a`, evidence remediation `c2fa657442a9a3944aaed669cc0f8354be1a1fa0`, and closure. This item preserves the P-002 repair and replaces only the remaining broader fallbacks. |
| agentic-mbse | `8b105b3fe5cdb2a172f813600791a1b76471423c` | `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb` | Verified descendant on `self-binding-replacement`. Preserve landed validation/types/guidance; extend its adapter/expression/error API. |
| fusion-tea | `be1ee7c0c40a092ebe6750f262902501e377bbd0` | `824a876e281a3b9aef58b1873bfbd0b20c4ab77b` | Verified descendant through `9e1ff87b` and `7703ba1e`; contains the closed predecessor model/test changes. Verify from a clean named-commit worktree. |

The implementation reconciliation ledger records the new descendants only after their commits
exist. This corrects the epic's stale statement that the predecessor set was uncommitted without
inventing future SHAs.

## Historical census reconciliation ledger

| Historical row | Design owner | Final proof/disposition |
|---|---|---|
| L-01 definition descendant search | A3/D4 | Delete; local positive plus descendant/sibling refusals |
| L-02 nearest occurrence/calc selection | A1/A2/A4, D1-D3 | Exact address and producer index; real domain matrix |
| L-03 dropped expression index | A5/D4/D8 | `SI_INDEXED_SOURCE_UNSUPPORTED`; backlog capability |
| L-04 model-wide multiplicity writer | A6/D4 | Exact owner-domain writer; adversarial proofs |
| L-05 skipped redefinition endpoint | B7/D4 | Strict endpoint/wrapper identity; real and forced proofs |
| L-06 live metatype fallback | B1/D5 | Public evidence cause; non-live mock-only path |
| L-07 class-name expression dispatch | B2/D5 | Mapped metatypes; real subtype proof |
| L-08 swallowed operands | B3/D5 | Total materialization or typed evidence error |
| L-09 staged reference ladder | B4/D5 | Exact referent/target only |
| L-10 QN library filter | B5/D6 | Direct `Document.document_tier`; no origin/name classifier |
| L-11 simple/first type mapping | B6/D8 | Sole qualified type or `SI_TYPE_INVALID` |
| L-12 omitted exit wrapper | B9/D9 | Public fail-before-mutate refusal |
| L-13 output alias first-wins | Backlog only | File separate agent-grade row before close |
| L-14 source-file parameter groups | Out of scope | Preserve documented rendering policy |
| U-1 sole-glob source file | B10/D10 | Retain measured `DELETE_UNREACHABLE` and the deleted branch; rerun only if a locked input changes |
| U-2 resolved fact without leaf | B8/D5/D10 | B8a pre-change real totality kill gate; B8b post-D5 forced typed regression |

`verification/reconciliation-ledger.md` copies this table, adds exact test IDs and implementation
commits, and closes every row before audit. Its codegen production row names `C_prod`, not
`C_evidence`.

## Review-finding closure map

| Finding | Revision-6 disposition |
|---|---|
| F1 | Remains resolved. D6 consumes `DocumentTier`; no Revision-6 change touches that authority |
| F2 | Remains resolved. D1/D2 retain the exact address and direct-one-step package rule |
| F3 | Remains resolved. D3 retains the contextual output-producer index |
| F4 | Reopened by the fresh audit. D5/D7 now require all three closure legs: exact selector ownership, closed representation with the permissive surface deleted, and dual-layer natural-route proof; verification is pending |
| F5 | Remains resolved in design by the acyclic `C_prod` → `F_final` → `C_evidence` topology and exact production/evidence boundary. The owner has removed the Agentic PDF suite from this evidence contract |
| F6 | Remains resolved for its original premise gate. Revision 6 does not change D1-D4 or reinterpret the real-corpus totality result |
| F7 | Reopened by direct-call evidence. D9 now removes caller-supplied wrapper types and derives them from the graph inside every exported generator; verification is pending |
| F8 | Resolved in design by keeping `semantic_owner` general and applying the three-kind validation only in `build_containment_address` while preserving attachment/formal domains |

The fresh-audit findings map to concrete design owners:

| Fresh finding | Revision-6 owner | Required closure proof |
|---|---|---|
| `audit3-F1` / CI-1: discarded index marker | D5/D7 | Indexed computed attribute, alias, predicate, calculation dependency, and binding all refuse through live and capture arms before graph construction |
| CI-2: raw operand and depth bypass | D5/D7 | One shared budget and total operand materialization fail through each natural consumer, including a unit wrapper |
| CI-3: weaker bare-binding interpretation | D7 | Closed binding-source union and exact-reference-only resolver; no optional semantic path or raw pending-binding fallback |
| CI-4: shortened deep relationship path | D7/D8 | Real `Feature`-only path proof plus forced mapped-`IndexExpression` refusal; the total factory also fails on the first missing middle target and preserves the authored path and location |
| CI-5: caller-provided registry invariant | D9 | Caller type-set parameter is absent; no-root, one-type, repeated-type, and multiple-type graphs derive their own wrappers, while unsupported types refuse through direct and CLI routes |
| CI-6: untrusted final-run construction | Sequencing gate 6 | Every final record is produced by the committed runner from pinned artifacts |

The finalized Revision-5 review resolutions close in Revision 6 as follows:

| Review item | Revision-6 change |
|---|---|
| M1 | Branch from old `C_prod` `78a9beb9`; preserve D1-D4, probes, and harness; reseal a fresh `C_prod` |
| C1(a) | Make selector ownership, closed representation, and natural-route proof jointly required |
| C1(b) | Delete the permissive Agentic API, bool marker, aliases, and exports; migrate every measured Agentic and Codegen consumer |
| C1(c) | Cover direct selectors, literal/dynamic `getattr`, and local/import aliases with discovery and mutation kills |
| C2 | Distinguish normal inventory refusal from a targeted bypassed-inventory consumer backstop; add the deep-path index proof |
| M2 | Treat `elaborate_loaded_extractor` as existing and replace the actual untyped registry failure rather than a nonexistent warning branch |
| M3 | Add zero-error strict checking only for four narrow boundary files, separate from repo-wide baselines |
| m1–m3 | Record the math-only optional IR target, measured migration size, and The Point |

## Next-stage handoff

Revision 6 is draft and needs targeted `my-design-review` confirmation that the finalized findings
are incorporated without reopening D1-D4. The current product-lens gate stays `BLOCKED` until that
confirmation accepts the indexed-consumer architecture and its three-leg closure proof. After
approval, `my-plan` replaces the existing checklist; it does not append remediation tasks to the
Revision-4 plan. The replacement plan must keep both local ownership manifests, the scoped strict
gates, full natural-route matrices, probe/fixture lock, and `C_prod`, `F_final`, and `C_evidence`
boundaries as checked deliverables. Implementation is followed by an independent `my-audit`; the
implementing agent does not self-certify.
