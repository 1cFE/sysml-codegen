# Technical Design: Stop Reinventing the Parser

**Status:** Approved — final design review, Revision 4
**Revision:** 4
**Date:** 2026-08-16
**Branch:** `stop-reinventing-the-parser`
**Contract:** `spec.md`, approved revision 4
**Final review:** `design-review.md`, Approve, Revision 4
**Product lens:** `CLEAR`; the Revision-4 final rerun keeps design-F1 `FIXED`

## Outcome

The exact route will resolve occurrences from parser identities, semantic ownership, modeled
containment, and the consumer's occurrence domain. It will stop choosing candidates by distance,
descendant count, model-wide uniqueness, or declaration order. The agentic extraction boundary will
either return complete parser evidence or raise one public typed error. Codegen will convert that
error, and its own exact-evidence failures, at one boundary shared by live generation and snapshot
capture.

Revision 4 changes only F5's cross-repository evidence topology and the exact agentic full-suite
command. The final review confirms that F5 is resolved. The review's resolved F1-F4 and F6-F8
decisions remain unchanged.

Shaping and spec reruns are intentionally skipped. The approved revision-4 contract is already
clear, the owner requires no further gates, and this revision changes implementation decisions
rather than requirements.

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
`product-lens.md:503-535`. F5 is an engineering-evidence finding and does not alter that
product-lens result.

## Current code facts

- `occurrence.py` already owns stable feature slots, occurrence IDs, type closures, and modeled
  multiplicity. It also contains the model-wide sole multiplicity-writer branch that A6 removes.
- `elaborate.py` builds value and calculation nodes, then resolves references. Its
  `_select_occurrences`, `_select_calc_nodes`, and `_resolve_leaf` methods still perform the
  candidate elections prohibited by A1-A4.
- `_resolve_leaf` currently scans every calculation node for a matching output declaration. That is
  the A2 producer-selection hole.
- `elaborated_pipeline.py` extracts calculation definitions before it calls `elaborate()`, so an
  upstream evidence exception can currently miss the elaboration diagnostic conversion.
- Agentic `SysideAdapter.is_instance` catches a live SysIDE exception and then uses a class-name
  answer. `expression.py` also uses class-name dispatch, partial traversal, staged name recovery,
  and QN-prefix library filtering.
- `feature_metadata.py::_source_file` has a final sole-glob fallback after exact document-origin
  attempts.
- Registry generation warns and omits an unsupported root wrapper. The output tree may later be
  unusable even though generation reported success.

## One architecture

There is one resolution architecture:

```text
SysIDE document + AST
        |
        | exact IDs, DocumentTier, resolved targets, semantic owners
        v
agentic evidence extraction -- SemanticEvidenceError on incomplete evidence
        |
        v
codegen extract-and-elaborate boundary -- ElaborationDiagnosticError on refusal
        |
        v
ContainmentAddress + OccurrenceIndex + calculation-output producer index
        |
        v
InstanceGraph -> projection -> generation preflights -> TEAx package
```

`ContainmentAddress` is a private immutable value. The producer index is a private dictionary of
immutable records. Neither is a strategy object, a selectable resolver, or a compatibility layer.
The existing exact route is changed in place. No flag or fallback can select the retired behavior.

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

Agentic adds the following public API in `agentic_mbse.errors`, re-exported from
`agentic_mbse.__init__`:

```python
SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v1"

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
`RESOLVED_TARGET_MISSING`, `DOCUMENT_TIER_MISSING`, `DOCUMENT_TIER_UNKNOWN`, and
`RESOLVED_LEAF_MISSING`. The exception's `detail` never embeds its code. When wrapping a parser
exception, construction stores it in `cause` and the raise site uses `raise ... from cause`.

The operations are:

- B1: a live SysIDE element is recognized by the installed SysIDE `Element` base. Its mapped
  `.isinstance()` result is authoritative. If that call raises, the adapter raises
  `SemanticEvidenceError(METATYPE_CHECK_FAILED)` from the parser exception. Class-name matching is
  allowed only for an object that is not a live SysIDE element, which is the explicit test-double
  path. Unknown type-map names remain errors.
- B2: operator, feature-reference, and feature-chain dispatch use mapped SysIDE metatypes. The
  explicit non-live test-double path uses the same closed mapped names. No production class-name
  substring selects a branch.
- B3: operands are materialized once with `tuple(expression.operands)`. Failure raises
  `SemanticEvidenceError(OPERAND_ITERATION_FAILED)` with the expression location. Successful
  traversal visits every materialized operand.
- B4: `FeatureReferenceExpression.referent` and `FeatureChainExpression.target_feature` are the only
  identity authorities. The exact element and ID are retained in the evidence record. Membership,
  node-name, qualified-name, and empty-result ladders are removed. A missing resolved target is
  `SemanticEvidenceError(RESOLVED_TARGET_MISSING)`.
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
repository has no second standard-library classifier. `ExpressionRef.document_path`, document URL,
source-file path, package name, and qualified name have no classification role.

Removing `STANDARD_LIBRARY_PREFIXES` also removes its lazy barrel/export entry in
`agentic_mbse.sysml.__init__` and updates the public-export assertion. No dead compatibility export
remains.

A reference requested with standard-library filtering but lacking an exact resolved element raises
the B4 evidence error before B5. A real user package named `SI` remains project evidence. A real SI
unit reference is filtered because its document tier says StandardLibrary.

### D7. One codegen conversion boundary

`orchestration/elaborated_pipeline.py` gains one function,
`elaborate_loaded_extractor(extractor, *, model_paths, source_referents, strict)`. Both
`elaborate_model_paths` and `elaborate_admitted_sources` load and validate their own source sets,
then call this same function. Snapshot capture already reaches the admitted-source arm, so live
generation, snapshot capture, and other admitted-source callers share the conversion.

`source_referents` is an immutable raw-source-path-to-`root-N/<relative-path>` mapping, not a
resolver selection. The live arm constructs it from the caller's ordered model roots. The admitted
arm passes the admission manifest's staged-path mapping. It is used only to render public locations
and the finished graph; it does not classify documents or choose semantic targets.

Inside that one boundary:

1. Extract calculation definitions.
2. Run the internal exact graph builder.
3. Validate the graph and executable-content gate.
4. Catch `SemanticEvidenceError`, `ElaborationInvariantError`, and `GraphValidationError` once and
   convert them to the existing `ElaborationDiagnosticError`.

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
modes through live and admitted-source arms.

### D8. Diagnostic ownership

| Condition | Public code | Owner |
|---|---|---|
| B1-B5/B8 incomplete parser evidence | `SI_EVIDENCE_INCOMPLETE` | agentic cause; codegen public rendering |
| Missing/multiple/unsupported exact typing | `SI_TYPE_INVALID` | codegen extraction/elaboration |
| Missing/ambiguous contextual occurrence or producer | `SI_OCCURRENCE_MISSING` / `SI_OCCURRENCE_AMBIGUOUS` | codegen elaboration |
| Invalid redefinition family | `SI_REDEFINITION_INVALID` | codegen slot index |
| Unresolved/unsupported multiplicity | existing `SI_MULTIPLICITY_*` code | codegen occurrence construction |
| Valid indexed element expression not implemented | `SI_INDEXED_SOURCE_UNSUPPORTED` | codegen pre-graph gate |
| Unsupported generated root output | `EXIT_POINT_TYPE_UNSUPPORTED` | codegen generation preflight |

Every public refusal includes exact reference identity when available and a root-relative
`file:line`. No B10 source-origin code is carried into production; D10 selects the single deletion
branch before production starts.

### D9. B9 fails before output mutation

`cli._generate_package_from_graph` adds `_preflight_exit_point_types(graph)` beside the existing
preflights and before link checks, constraint-plan rendering, output clearing, directory creation,
or any write. It visits every module and every output. For `field_name == "root"`, only
`float`, `int`, `str`, and `bool` are valid registry primitive types.

An unsupported type raises `CodeGenerationError` with one stable token and fields:

```text
EXIT_POINT_TYPE_UNSUPPORTED: module='<module name>' output='<field name>/<channel name>' \
python_type='<type>' source='root-N/<relative-path>:<line>'
```

The warning branch in `generation/registry.py` is deleted. Registry generation may assume the
preflight passed and treats a later miss as a programming invariant, not a second public behavior.

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

### D10. Retained probes and production gate

The three licensed pre-production probes, B2, B8a, and B10, are committed and retained under
`.project/active/stop-reinventing-the-parser/probes/` before production code changes. B8b is the
separate post-D5 regression specified alongside them below.

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

This design has one permitted measured verdict: `DELETE_UNREACHABLE`. The verdict file must contain
that literal, the probe/fixture commit SHA, SysIDE version, counts, and per-file root-relative
evidence. Only then is the sole-glob branch deleted and no replacement is added. If the measured
result differs, production does not start and this design returns for revision. The probe has not
yet run, so this is a production gate rather than a claim that B10 is already proved unreachable.

The canonical pre-change verdict files are `verification/probes/b2-verdict.json`,
`b8-real-verdict.json`, and `b10-verdict.json`. Probe scripts and verdicts remain after
implementation. B8b remains as ordinary kept agentic and codegen regression tests.

## Data and responsibility ownership

| Data or invariant | Single owner | Consumers |
|---|---|---|
| SysIDE metatype truth and `DocumentTier` | SysIDE through agentic adapter | agentic expression/fact extraction |
| Complete semantic evidence and public evidence error | agentic-mbse | codegen boundary |
| General semantic-owner selection | codegen `elaboration/occurrence.py` | attachment, formals, occurrence builder, elaborator |
| Closed owner-kind/identity validation for `ContainmentAddress` | `build_containment_address` only | multiplicity and producer/address resolution |
| Feature slot and occurrence population | existing `FeatureSlotIndex` / `OccurrenceIndex` | address instantiation |
| Calculation output producer records | codegen exact elaborator | leaf/reference resolution |
| Public evidence-error rendering | `elaborate_loaded_extractor` | live and admitted-source routes |
| Exit-point type refusal before writes | codegen generation preflight | CLI live/snapshot generation |
| TEAx behavior | generated package and Fusion tests | final product verification |
| Cross-repository artifact/import provenance | `verification/dependencies.json` and execution manifest | isolated test runners and Fusion lock proof |

Agentic does not choose codegen occurrences. Codegen does not infer parser metatypes, reference
identity, or standard-library status. Fusion does not patch around either repository.

## Cross-repository API and independent landing

### Agentic semantic contract

Agentic makes a backward-compatible public API addition and behavior correction, then bumps its
package version from `0.1.2` to `0.1.3` in `pyproject.toml`, `agentic_mbse.__version__`, and
`uv.lock`. It exports `SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v1"`,
`SemanticEvidenceCode`, and `SemanticEvidenceError`. The standalone agentic test suite, type check,
and lint must pass from its committed tree before codegen changes consume it.

### Codegen pin and dependency contract

Codegen changes `agentic-mbse>=0.1.2` to `agentic-mbse>=0.1.3,<0.2` in `pyproject.toml` and refreshes
`uv.lock`. `_upstream_pins.py` adds
`AGENTIC_MBSE_PACKAGE_VERSION = "0.1.3"` and
`SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v1"` to `__all__`, and removes its obsolete
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

1. agentic source archive: its full pytest suite, type check, and lint. From the fresh extracted
   archive root, the runner uses the repository's `SYSIDE_LICENSE_KEY` environment pattern and the
   documented empty marker override that replaces `pyproject.toml`'s `-m 'not slow'` default
   (`../agentic-mbse/CLAUDE.md:52-65`; `../agentic-mbse/pyproject.toml:93-100`):

   ```bash
   set -a
   source /home/reid/1cfe/agentic-mbse/.env
   set +a
   uv run pytest tests/ -m ""
   uv run mypy src/
   uv run ruff check src/ tests/
   ```

   The sourced file supplies the license secret only. It is not copied into an archive or report,
   and no Python import may resolve under that sibling checkout. `tests/conftest.py:1-8` retains its
   `load_dotenv()` behavior, while the exported value makes the isolated run independent of a
   copied `.env`. A missing license key, any deselected slow test, or any license skip fails the
   gate;
2. 1costingfe source archive: its complete pytest suite and configured lint;
3. TEAx source archive: the root-configured simkit and battery-demo suites;
4. codegen source archive: default unit/conformance suite, licensed real-model suite, snapshot/live
   parity, generated-package tests, and the complete `execution` marker lane using the manifest and
   extracted TEAx source;
5. Fusion source archive: `uv lock --check`, full configured pytest suite, model validation, and the
   final generated Fusion/TEAx execution proofs using installed agentic/codegen/1costingfe wheels.

The run records `pip freeze`, artifact/manifest digests, Python, SysIDE, TEAx/simkit, 1costingfe,
agentic, codegen, and Fusion versions, resolved import files, test commands, statuses, and skips. An
unexpected skip or any sibling working-tree import fails the gate. Model sources change only if the
semantic tests find a real violation; the Fusion dependency/lock changes above are mandatory.

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

The codegen baseline is the production parent. No baseline is recaptured after production code
changes and then called “before.”

### Probe/fixture commit lock

The first implementation commit in codegen contains only retained probes, their real fixtures, the
fixture inventory, and baseline-capture tooling. Its parent is the codegen production baseline
above. After that commit exists, a second manifest-only commit writes the first commit's actual full
SHA to `verification/probe-fixture-lock.json` as `probe_fixture_commit`, records the parent relationship,
and changes no probe, fixture, capture tool, or production source. This avoids the impossible
self-referential requirement that a commit contain its own SHA.

Before any probe runs, the runner requires `probe_fixture_commit` to be 40 lowercase hexadecimal
characters, equal to the lock commit's parent, and a tree whose recorded probe/fixture hashes match.
The lock commit SHA is recorded externally with the probe run and then in each verdict. The plan
cannot advance on a dirty tree or a mismatch. This freezes the later probe/fixture commit without
inventing a SHA before it exists.

The lock stores SHA-256 for every probe, every source fixture file in the 37 canonical roots, every
added fixture file, the item fixture manifest, and the canonical batch manifest. Any changed byte
invalidates the verdicts and requires a new probe/fixture commit, lock commit, and rerun before
production.

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

At the production baseline, capture the 37 canonical roots. At the probe/fixture commit, capture
the six added roots while production source remains byte-identical to the baseline parent. Store:

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
| A5 indexed expression | index is ignored | pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED` | `test_expression_evidence_integrity.py` |
| A6 multiplicity writer | unrelated sole writer may answer | owner-address writer or `SI_MULTIPLICITY_UNRESOLVED` | `test_occurrence_multiplicity_authority.py`; public mutation test |
| B1-B5 evidence | fallback, partial traversal, name recovery, or QN filter continues | exact evidence/DocumentTier or `SI_EVIDENCE_INCOMPLETE` | agentic adapter/expression tests; codegen boundary tests |
| B6/B7 metadata | weak type or skipped redefinition identity may pass | sole qualified type and one exact slot family, or named refusal | `test_feature_typing_integrity.py`; occurrence tests |
| B8 leaf | resolved fact may be skipped | pre-change real corpus is total; post-D5 missing leaf raises the typed error | B8a retained real probe; B8b agentic/codegen regressions |
| B9 exit type | warning plus incomplete registry | `EXIT_POINT_TYPE_UNSUPPORTED` before mutation | `test_generation_exit_type_preflight.py` |
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
- Real operator, feature-reference, and feature-chain nodes prove mapped dispatch. A failing operand
  iterator proves no partial results escape.
- Real bare and chain references retain exact IDs. Forced missing referent/target and missing leaf
  cases raise `SemanticEvidenceError` with reference and location.
- Real StandardLibrary, Project, and External document tiers prove B5. A project document whose
  package is named `SI` remains. Missing, `None`, and foreign tier values fail.
- Boolean/Integer/Real/String qualified typings succeed. User-defined `Real`, zero, multiple, and
  unsupported typings fail as `SI_TYPE_INVALID`.
- Strict and lenient calls through both live and admitted-source arms assert the same public class,
  code, cause chain, reference, root-relative location, one rendered code token, and no graph,
  snapshot, or generated output on evidence-integrity failure.
- B2, B8a, and B10 pre-change probes include their anti-vacuity counts and kill verdicts. B8b's
  forced regression runs only after D5 exists.
- B9 asserts token, module/output identity, type, file:line, status `1`, and byte-identical output
  preservation as specified in D9.

### Static removal checks

Tests fail if production code retains:

- nearest/descendant/model-root/sole-candidate selector arms;
- the graph-wide calculation-output scan;
- production class-name metatype dispatch or swallowed operand iteration;
- QN/path/origin standard-library classifiers;
- first-typing/simple-name/unknown-pass-through type mapping;
- skipped redefinition endpoints;
- the sole-glob source fallback;
- the registry warning for unsupported root outputs.

## File-level implementation map

| Repository / files | Change |
|---|---|
| agentic `src/agentic_mbse/errors.py`, `__init__.py` | Public semantic-evidence enum, error, and API version |
| agentic `sysml/syside_adapter.py`, `sysml/__init__.py` | Live metatype propagation, mapped dispatch support, direct `document_tier`, obsolete export removal |
| agentic `sysml/expression.py`, `constraint_extraction.py` | Total traversal, exact targets, resolved leaf failure, DocumentTier filtering |
| agentic `pyproject.toml`, `uv.lock`, tests, `docs/patterns/plant-idiom.md` | 0.1.3 contract, proofs, and supported/refused modeling shapes |
| codegen `elaboration/occurrence.py` | General owner selector; containment-local kind/identity validation; address resolver; exact multiplicity owner; strict redefinition identities |
| codegen `elaboration/elaborate.py`, `elaboration/__init__.py` | Producer index, address-only reference resolution, raw private graph builder |
| codegen `orchestration/elaborated_pipeline.py` | Single evidence conversion boundary for live/admitted extraction and elaboration |
| codegen `extraction/extractor.py`, `feature_metadata.py` | Exact typing; B10 fallback deletion after verdict |
| codegen `cli/__init__.py`, `generation/registry.py` | B9 fail-before-mutate preflight and warning deletion |
| codegen `_upstream_pins.py`, `pyproject.toml`, `uv.lock` | Exact agentic package/API pins, codegen 0.1.1, dependency minimum, lock |
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
- `docs/architecture/reference/20-module-registry-generation.md` REQ-REG-09. Replace the warning
  contract with refusal before output mutation, including `EXIT_POINT_TYPE_UNSUPPORTED`, identity,
  location, status, and preservation proof.
- `docs/architecture/verification-matrix.md` REQ-REG-09. Replace
  `test_hygiene_tail_registry.py` with
  `tests/conformance/test_generation_exit_type_preflight.py` and record PASS only after the complete
  public proof passes.
- Diagnostic reference documentation for `SI_EVIDENCE_INCOMPLETE`, `SI_TYPE_INVALID`,
  `SI_INDEXED_SOURCE_UNSUPPORTED`, and `EXIT_POINT_TYPE_UNSUPPORTED`.
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

1. **Freeze inputs.** Record the production SHAs, create the probes/fixtures-only commit, create the
   manifest-only `probe-fixture-lock.json` commit that records its actual SHA and all hashes,
   capture before baselines, and validate the closed inventory.
2. **Run pre-production kill gates.** Run B2, B8a real-corpus totality, and B10 against the frozen
   pre-change commits. All anti-vacuity checks pass, B8a records `REAL_CORPUS_TOTAL`, and B10 records
   exactly `DELETE_UNREACHABLE`, or the plan stops and returns to design.
3. **Land agentic evidence and B8b.** Add the public error/API version, B1-B5 behavior, the
   post-D5 forced `RESOLVED_LEAF_MISSING` regression, version/lock/docs, standalone tests, clean
   commit, source archive, and wheel.
4. **Adopt the codegen boundary.** Pin/install the agentic wheel, update dependency metadata, replace
   the public elaboration call shape, and prove strict/lenient live/admitted conversion.
5. **Replace occurrence resolution.** Add D1-D4, producer index, A1-A6 tests, and public mutation
   proofs. Delete the selector and scan branches in the same change.
6. **Finish evidence and generation integrity.** Land B6/B7, delete B10's proved-unreachable glob,
   add B9 preflight, and run all B tests.
7. **Reconcile outputs and docs.** Complete the production-tracked expected-transition file,
   compare every baseline byte, update required docs/backlog rows, and prepare the historical
   reconciliation rows for the later evidence-only record. Seal `C_prod` only after all production
   code, tests, docs, fixtures, package metadata, pins, and locks are complete.
8. **Prove and attest the acyclic landing.** Build and hash the codegen source archive and wheel
   from `C_prod`. Make Fusion pin `C_prod`, land `F_final`, build and hash its source archive, and
   verify Fusion. Run every required isolated suite from the declared source/wheel artifacts and
   write the six final verification files. Land only those files as direct-child `C_evidence`, then
   run the four audit boundary checks above. A failure changes the owning production repository and
   repeats from a new `C_prod` or `F_final`; it is never patched in `C_evidence`.

No D1-D4 occurrence-identity production change starts before all three step-2 gates pass. No
codegen or Fusion result cites an editable sibling checkout, and no execution result cites TEAx or
1costingfe outside the recorded artifacts. No downstream repository pins `C_evidence`.

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
| U-1 sole-glob source file | B10/D10 | Probe must select `DELETE_UNREACHABLE`; delete before production continues |
| U-2 resolved fact without leaf | B8/D5/D10 | B8a pre-change real totality kill gate; B8b post-D5 forced typed regression |

`verification/reconciliation-ledger.md` copies this table, adds exact test IDs and implementation
commits, and closes every row before audit. Its codegen production row names `C_prod`, not
`C_evidence`.

## Review-finding closure map

| Finding | Revision-4 disposition |
|---|---|
| F1 | Remains resolved. D6 consumes `DocumentTier`; the product-lens rerun records `CLEAR` / design-F1 `FIXED` |
| F2 | Remains resolved. D1/D2 retain the exact address and direct-one-step package rule |
| F3 | Remains resolved. D3 retains the contextual output-producer index |
| F4 | Remains resolved. D5/D7 retain one public evidence conversion boundary |
| F5 | Resolved in design by the acyclic `C_prod` → `F_final` → `C_evidence` topology, the closed production/evidence file boundary, audit reconstruction checks, and the exact slow-inclusive agentic command `uv run pytest tests/ -m ""` |
| F6 | Resolved in design by B8a pre-change real totality and B8b post-D5 typed regression; D1-D4 remain behind B2/B8a/B10 |
| F7 | Remains resolved. D9 retains the B9 contract, docs, diagnostic, status, and byte-preservation proof |
| F8 | Resolved in design by keeping `semantic_owner` general and applying the three-kind validation only in `build_containment_address` while preserving attachment/formal domains |

## Next-stage handoff

With the final `my-design-review` approval, `my-plan` must turn the eight sequencing steps
into persistent checklists. The product-lens record is already `CLEAR` and is not reopened by these
engineering corrections. The plan must keep the probe/fixture lock, `C_prod`, `F_final`, and
`C_evidence` boundaries explicit, make each ledger and public proof a checked deliverable, and
retain the five-input independent-green artifact evidence. Implementation is followed by an
independent `my-audit`; the implementing agent does not self-certify.
