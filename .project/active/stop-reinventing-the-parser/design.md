# Technical Design: Stop Reinventing the Parser

**Status:** Revision 8 — targeted amendment of Revision 7, after the Phase 3 stop-rule halt
**Revision:** 8
**Date:** 2026-08-18
**Branch:** `stop-reinventing-the-parser`
**Contract:** `spec.md`, approved revision 4
**Prior review:** `design-review.md`, Revision 6 `Approve`; Revision-7 targeted amendment review
`Revise` — must-fix set applied and orchestrator-verified 2026-08-17 (verification note in
`design-review.md`)
**Product lens:** `BLOCKED` at `audit3-F1` until the indexed-consumer proof passes
**Revision input:**
`.project/research/20260817-164828_expression-evidence-boundary-convergence-assessment.md`;
`run-records/phase1-stop-report.md` (revision 3, rulings 1-7 owner-ratified 2026-08-17);
`run-records/phase3-stop-report.md` (rulings 1-4 owner-ruled 2026-08-18)

## Revision history

- **Revision 8 (2026-08-18) — targeted amendment.** Cause: `run-records/phase3-stop-report.md`.
  Phase 3 halted under the stop rule because a Revision-7 premise is false — the unit operand of a
  `[` annotation is **not** a feature reference for any compound unit (`[kg/m^3]` is an
  `OperatorExpression`), so `inspect_reference_uses` refused every compound-unit model on the real
  corpus. The owner ruled on the falsified premise and on three items surfaced beside it. This
  amendment encodes those four rulings and changes exactly four areas:
  1. **[One total inspection operation](#one-total-inspection-operation)** — the unit-annotation
     bullet is replaced: the unit operand is **opaque**, not shape-validated (ruling 1).
  2. **[Public agentic evidence contract](#d5-public-agentic-evidence-contract)** and the
     [Agentic semantic contract](#agentic-semantic-contract) export list — one shared structural
     primitive `unit_annotation_value`, called by both `inspect_reference_uses` and Codegen; the
     Codegen value-site rule becomes policy over that primitive (ruling 2).
  3. **[Checked consumer and ownership manifests](#checked-consumer-and-ownership-manifests)** —
     the Codegen raw-selector gate keeps repository-wide discovery and gains collision-aware
     reviewed rows; adapter-import scoping is rejected for Codegen (ruling 3).
  4. **[Current code facts](#current-code-facts)** behavior matrix and the
     [`Cell[3]` red-set case](#the-indexed-red-set--both-cases-are-required-kept-tests) — the
     measured **lenient** arm of the plural bare chain is stated (ruling 4).

  Also touched, mechanically, by those four rulings: Outcome, Data and responsibility ownership,
  the transition ledger's A5b row, the evidence and public-boundary matrix, the file-level
  implementation map, and Next-stage handoff.

  Where a ruling contradicts Revision-7 text, the ruling wins: ruling 1 **deletes** the
  "validates its shape" requirement on the unit operand, and ruling 3 **rejects** extending Phase
  2's adapter-import gate scope to Codegen. **No D1-D10 mechanism changes**; D5 gains the shared
  primitive as new text. The closed-variant architecture, the artifact chain, the acyclic topology,
  the three-leg closure condition, and the probe/fixture lock are untouched, and no closure
  requirement is weakened.

  **Review incorporation (2026-08-18).** The targeted review of this amendment returned `Revise`.
  Its four must-fixes are applied here — the arity behavior of `unit_annotation_value` is stated as
  an [AGENT ruling] rather than left to the implementer, the retired Phase-2 assertions are named
  with m3's closure re-established on non-emission, and the handoff is retargeted and given its two
  missing items. Should-fixes 1-2 (the collision row's proof artifact; the evasion mutant's kill
  criterion) are taken with them, and should-fixes 3-7 are taken as well: each was a one-clause
  correction of something an implementer or auditor would otherwise have to guess at. This is
  review incorporation, so the document stays Revision 8.
- **Revision 7 (2026-08-17) — targeted amendment.** Evidence source:
  `run-records/phase1-stop-report.md`, whose `[verified]` claims were reproduced by the orchestrator
  in a clean worktree at `C_base`, and whose seven rulings the owner ratified on 2026-08-17. The
  amendment corrects false factual claims in Revision 6 and records the ratified rulings. It changes
  exactly five areas: the lock and inventory semantics, the current-code account of the indexed
  escape, the test design for the indexed red set, the `deep_cross_scope` graph→refusal ruling, and
  the revision-base prose. **No approved mechanism changes.** D1-D10, the closed-variant
  architecture, the artifact chain, the acyclic topology, and the consumer/ownership manifests are
  untouched, and no Revision-6 closure requirement is weakened.
- **Revision 6 (2026-08-17).** Review verdict `Approve`. Superseded Revision 4's D5, D7, D9, and
  evidence matrix; added the three-leg closure condition.

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

Revision 7 changes nothing in that mechanism. It corrects factual claims about the base tree and the
escape's trigger, splits the indexed red set into the two cases that actually go red for the right
reason, and records the ratified `deep_cross_scope_probe` ruling. See the revision history above.

Revision 8 changes nothing in that mechanism either. It removes a falsified premise about unit
annotations, gives the annotation's parser-shape reading one owner, corrects the Codegen
raw-selector gate's scope ruling, and states the lenient arm the behavior matrix omitted. See the
revision history above.

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
- The indexed-source preflight screens **only calc-usage in-direction bindings**. `screen_source_readiness`
  iterates `usage.bindings` (`extraction/source_evidence.py:195`), and the elaborator's binding
  classification serves consumer ports the same way. A bare computed-attribute initializer never
  enters that population: it becomes a **typed alias** (the refusal text names it as such), and alias
  resolution carries the indexed fact into semantic resolution, where the index has no representable
  role — the index's role is dropped, not screened. This is the verified mechanism
  [`run-records/phase1-stop-report.md`, Finding 3, verified in source at `C_base`].

  The measured behavior at `C_base` follows directly from that mechanism:

  | Authored shape | Arm | Result at `C_base` | Provenance |
  |---|---|---|---|
  | `picked = cells#(2).mass`, `cells : Cell[3]` (Revision-6 plan stencil) | `strict=True` | REFUSED — `SI_OCCURRENCE_AMBIGUOUS`; wrong name, incidental to the plural slot | [verified] orchestrator |
  | `picked = cells#(2).mass`, `cells : Cell[3]` | `strict=False` | **Graph returned**, carrying `SI_OCCURRENCE_AMBIGUOUS` + `SI_OCCURRENCE_MISSING`; all three `cells[i]__mass` attributes present, `picked` unresolved | [OWNER 2026-08-18] ruling 4; measured in Phase 1 |
  | `picked = cells#(2).mass * 1.0` (any operator wrapper) | both | REFUSED — `SI_INDEXED_SOURCE_UNSUPPORTED`; correct code | [AGENT] retained probe |
  | `picked = cells#(1).mass`, `Cell[1]` | both | zero-diagnostic graph, silently `cells[0].mass` | [AGENT] retained probe |
  | `picked = cells#(2).mass`, `Cell[1]` — index out of range | both | zero-diagnostic graph, silently `cells[0].mass` | [verified] orchestrator |

  A **singular** slot silently binds occurrence zero for any authored index, in range or not. A
  **plural** slot refuses incidentally as ambiguous, on a name that describes occurrence selection
  rather than the unsupported index. **Operator-wrapped forms are real expressions, enter the screen,
  and refuse correctly today** — they are not part of the escape. The escape is the bare chain.

  **The plural slot's two arms** (**[OWNER 2026-08-18]** — ruling 4, closing the gap surfaced at
  plan.md Phase 1 "Issues / deviations" item 3 and Phase 1 audit Minor 9). The plural row's refusal
  is the **strict** arm. Under `strict=False` the same fixture returns a graph carrying the same two
  diagnostics instead of refusing. The diagnostic identity does not change between arms, so this is
  the documented strict/lenient delivery contract, not a contradiction: lenient mode collects
  reference/readiness diagnostics for which a complete graph remains meaningful. After this item,
  **both arms refuse pre-graph with `SI_INDEXED_SOURCE_UNSUPPORTED`**, because the inventory runs
  before any occurrence resolution and evidence refusals are not a leniency choice
  ([D7](#d7-one-codegen-conversion-boundary)). Case 2's kept test already parameterizes both arms
  and both are red at `C_base`; this row states what they pin.
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

**[AGENT] (ratified by owner, 2026-08-17)** — ruling 1. `C_base` and `A_base` are unchanged. The
Phase-1 stop did not disqualify the base: the lock is intact and the tree is coherent
(`run-records/phase1-stop-report.md`, Finding 1). Do not re-root.

`C_base` is a **descendant** of the frozen evidence commits, not a byte copy of them. Nothing in this
design requires the current tree to byte-match the `P_seed` evidence state. Historical evidence,
generated output expectations, and the evolving validator are **versioned states**; every difference
between `P_seed` and `C_base` is either metadata-only or owned by a named transition row, and the
committed validators prove that. See [Probe/fixture commit lock](#probefixture-commit-lock) for the
rule that replaces byte identity.

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
- A structural unit annotation is read through the shared `unit_annotation_value` primitive below.
  **[OWNER-VERBATIM 2026-08-18]** — ruling 1:

  > For a parser-accepted `[` annotation with exactly two operands, reference inspection visits the
  > value operand and treats the unit operand as opaque. It neither traverses nor emits the unit
  > operand. SysIDE owns the validity of the unit expression.

  **[OWNER 2026-08-18]** The feature-reference and exact-referent requirements on the unit operand
  are **dropped**. This boundary does not validate unit grammar at all — which is not the same as
  saying any unit shape passes validation; a shape SysIDE rejects never reaches here. That last
  clause is measured, not assumed: the Phase-2 audit probed two project-scoped unit spellings at
  SysIDE 0.8.4 and the parser refused both (`run-records/phase2-audit.md`, m3 confirmation,
  "Referent must be a feature but is AttributeDefinition" / "Invalid quantity expression, expected a
  measurement unit as the second argument"). Codegen's raw-AST `annotated_ast_value` entry is still
  deleted and de-exported; IR consumers keep `annotated_ir_value`.

  This replaces Revision 7's "visits its value operand and validates its shape" text, whose premise
  is false: Phase 2 read "its shape" as "the unit operand is a feature reference", which holds for
  `[m]` and fails for every compound unit — `[kg/m^3]` is an `OperatorExpression`, and the resulting
  `EXPRESSION_KIND_UNSUPPORTED` refused every compound-unit model on the real corpus
  (`run-records/phase3-stop-report.md`). Required coverage, per the owner: `[m]`; representative
  compound forms such as `[kg/m^3]` and `[W/(m·K)]`; wrong arity through a synthetic node; and
  confirmation that references in the **value** operand are still visited.

  **What this retires in the Phase-2 tree.** Agentic's `_unit_annotation_value`
  (`reference_use.py:316` at the audited `68bca37`) refuses a non-feature-reference unit operand with
  `EXPRESSION_KIND_UNSUPPORTED` and an unresolved unit referent with `RESOLVED_TARGET_MISSING`, and
  kept tests pin both. **Those two refusals and their assertions are superseded by this contract and
  go.** They encode exactly the dropped requirements. What survives is the arity refusal below.

  **m3's closure moves to non-emission.** The Phase-2 audit accepted the m3 closure partly because
  shape validation survived. It no longer does, so the closure now rests on the single stronger fact
  that the unit operand is never traversed and never emitted at all — a project-scoped unit cannot
  appear as a design dependency because nothing on this route ever looks at it. The Agentic landing
  of ruling 1 re-establishes m3's disposition on that mechanism; it is not inherited from the
  Phase-2 audit, whose evidence is dated to the retired one.
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

**One owner for the annotation's parser shape.** **[OWNER 2026-08-18]** — ruling 2. Codegen
legitimately owns the *policy* decision that `0.2 [m]` is a literal value site rather than a computed
expression. The *parser-shape reading* underneath it must have one owner, so Agentic's boundary adds
one shared primitive:

> `unit_annotation_value(expression) -> Any | None` — it should recognize `[`, enforce exactly two
> operands, return the value operand, and leave the unit operand opaque. Both
> `inspect_reference_uses` and Codegen should call it.

**What "enforce" produces** — **[AGENT ruling 2026-08-18]**, derived from the owner's verbatim
"enforce exactly two operands", recorded so the reading is not left to the implementer. A recognized
`[` annotation whose operand count is not exactly two **raises**
`SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED)`. `None` means strictly one thing: the expression
is not a `[` annotation at all. `None` never describes a malformed annotation, so a malformed one can
never fall through and be walked as general math — which is what would re-emit the unit operand and
undo the m3 closure. Codegen's value-site policy does not catch that error; it reaches the D7
boundary and converts once to `SI_EVIDENCE_INCOMPLETE`. Recognition is by mapped metatype and
operator, never a runtime class name. Consequences:

- `inspect_reference_uses` traverses only what the primitive returns, so the unit operand is never
  reached and never emitted.
- Codegen's `expression_evidence.unit_annotated_value` keeps the **value-site policy** and delegates
  **all** structural interpretation — metatype, operator, and operand shape — to the primitive. It
  performs no operand indexing, no arity check, and no metatype test of its own. The value-site
  rule's home is Codegen policy over a shared Agentic primitive, not a second reading of the AST.
- The design's `annotated_ast_value` deletion stands. Phase 3 recorded a Codegen-owned AST unit walk
  as a surfaced residual (`run-records/phase3-stop-report.md`, premise conflict 2); this primitive is
  its resolution, and no Codegen-owned unit walk survives.

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

#### Inventory refusal precedes occurrence resolution

The inventory refuses an `IndexedReferenceUse` **before** any occurrence-domain resolution runs, so an
indexed use can never be diagnosed as an occurrence problem. The public refusal for an authored index
is always `SI_INDEXED_SOURCE_UNSUPPORTED`, never `SI_OCCURRENCE_MISSING` or
`SI_OCCURRENCE_AMBIGUOUS`, regardless of the consumer slot's multiplicity.

*Rejected: letting whichever check fires first name the failure.* That is `C_base`'s behavior, and it
makes the public diagnostic depend on the declared multiplicity of the consumer's slot rather than on
the defect. A user who wrote an index gets told their occurrence is ambiguous, which points at the
wrong thing to fix and hides an unimplemented capability behind a resolution error.

This is a named clause of D7, not a new decision: step 2 above already refuses every
`IndexedReferenceUse` before extraction, `_ExactElaborator`, or `InstanceGraph` allocation. It is
called out because it now carries a required diagnostic transition (A5b) and an explicit test
obligation ([the indexed red set](#the-indexed-red-set--both-cases-are-required-kept-tests)). It adds
no mechanism.

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
one imported alias, and one dynamic `getattr`; every mutation must kill the gate. Codegen adds one
**adapter-free evasion mutant** — a module importing nothing, receiving the node as an argument, such
as `def consume(node): return node.referent` ([ruling
3](#the-codegen-gate-keeps-repository-wide-scope)). Its kill criterion is stated in the gate's own
terms, not as discovery: the mutant's `(module, function, selector)` tuple must appear in the
discovered set **and fail the manifest equality gate**. Discovery alone is not a kill, and an
unannotated receiver like this one can never qualify for a collision-aware receiver-contract row —
that is what stops ruling 3's own mechanism from becoming the escape it exists to close. The discovered
tuple set must equal the reviewed manifests exactly. A new selector, missing manifest row, stale
row, unexercised exemption, or live import of an off-route module fails.

#### The Codegen gate keeps repository-wide scope

**[OWNER 2026-08-18]** — ruling 3, rejecting the adapter-import scoping proposed for the Codegen
gate. Phase 2 scoped Agentic's gate to adapter-importing modules (audited deviation 2), and the
Phase 2 audit recorded the hole that leaves open: a helper can receive a live SysIDE node as an
argument and read a raw selector off it without importing the adapter at all
(`run-records/phase2-audit.md`, m2, still open in the fix-round addendum). Making adapter-import
scope load-bearing on the Codegen side would turn that known residual into a legal escape. This
ruling governs the **Codegen** gate only; it does not reopen the audited Agentic gate.

The Codegen requirements, verbatim:

> - Keep repository-wide selector discovery.
> - Add explicit reviewed rows for neutral `ExpressionIR.operands` and `SourceFile.referent` reads.
> - Give each row a field owner or receiver contract and a real closure proof.
> - Add an adapter-free evasion mutant such as `def consume(node): return node.referent`; it must
>   still be discovered.
> - Leave the genuine raw reads in `usage_extractor` and any unresolved off-route modules red until
>   migrated or mechanically excluded.

So a collision-aware row is the mechanism, not a narrowed scan. `.operands` on a neutral
`ExpressionIR` dataclass and `.referent` on Codegen's own `SourceFile` dataclass are name collisions
with SysIDE selectors, not raw parser reads: `SourceFile.referent` is a **serialized snapshot key**,
so renaming it changes sealed bytes. Each such row names the declaring type as the field owner, or
the receiver contract that establishes the argument is never a live SysIDE element, plus its closure
proof — the same proof obligation every other row carries. A row asserting an owner it cannot prove
fails like any stale row.

**What the collision row's closure proof is.** Every other row class names its artifact — a live
row's proof is its public failure test, an off-route row's is the reachability exclusion — so this
class needs one too, or "receiver contract" is satisfiable by a docstring. The proof is:

- The declaring type must be **provable at the read site**, from a type annotation on the receiving
  parameter or attribute, or from module-local construction of the value being read. A prose or
  docstring claim is not a proof, and an **unannotated receiver can never qualify for a
  receiver-contract row** — it falls back to being an unowned raw read and stays red.
- The row's proof artifact is a kept test that fails if that annotation or declaring type changes.
  For `SourceFile.referent`, whose serialized-snapshot-key status makes renaming it a sealed-bytes
  change, that test is cheap and is also the row's rename guard.

Implementer and auditor arbitrate a disputed row against those two facts, not against the row's
wording.

**[OWNER 2026-08-18]** The current manifest failure contains 20 rows, so neutral-IR plus `referent`
is **not** the whole closure. The remaining rows are closed by migration or by mechanical exclusion,
and `usage_extractor`'s genuine raw reads stay red until one of those lands. A red count that shrinks
because the scan narrowed is not progress.

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
| Unit-annotation parser shape (`[` recognition, arity, which operand is the value) | Agentic `unit_annotation_value` | `inspect_reference_uses`; codegen `expression_evidence.unit_annotated_value` |
| Whether an annotated value is a literal value site or computed math | Codegen `expression_evidence.unit_annotated_value` policy | codegen elaboration |
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
`IndexedReferenceUse`, `inspect_reference_uses`, and `unit_annotation_value`
([ruling 2](#one-total-inspection-operation)). Version `0.1.3` is retained because the failed
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

At gate 1, the committed runner requires `probe_fixture_commit` to equal `20f9e60a`, requires its
recorded parent relationship, and recomputes every probe/fixture hash **against that commit's tree**,
not against the working tree. The recorded verdicts must name the same probe and lock commits. A dirty
implementation worktree, or a failure in any of the three legs below, stops the plan.

**When the probes rerun (D10's locked-input trigger).** Two conditions, and only these:

1. **A lock-vs-historical-tree mismatch** — a locked hash no longer recomputes against `20f9e60a`.
   That means evidence tampering or a history rewrite, not ordinary work.
2. **An unowned current-byte change to a locked verification or probe file** — one of the six
   non-fixture rows moved without a named ledger row.

A ledger-owned current-output transition is not a trigger; that is the system working. Neither is a
ledger-owned change to a verification file. The trigger is stated in terms of the current tree
precisely so it can fire: the historical bytes live in Git and nothing in this item writes them, so a
trigger phrased against those bytes alone would be inert.

The lock stores SHA-256 for 118 rows in two classes:

- **Fixture inputs** — every source fixture file in the 37 canonical roots, every added fixture file,
  the item fixture manifest, and the canonical batch manifest.
- **Verification and probe code** — the five probe scripts under
  `.project/active/stop-reinventing-the-parser/probes/` and `verification/capture_baseline.py`.

The two classes are verified differently, because one is frozen history and the other is live code
the item still runs. Both are pinned.

#### What the lock is verified against

**[AGENT] (ratified by owner, 2026-08-17)** — rulings 2-3, `run-records/phase1-stop-report.md`.
Verification runs on three legs. Leg 1 verifies the lock against the historical tree it names, leg 2
verifies current outputs through the transition ledger, and leg 3 pins the live verification and probe
code at current bytes. Every locked byte is covered by exactly one leg.

**Which commit the hashes are authoritative against.** The lock file's own `probe_fixture_commit`
field is `20f9e60a19b30bc1ec9a27aacb08380f4bc45602`, with `probe_fixture_parent`
`7b29d8b636e284364a4fdce9079f153c51c867ea`. `43edf9bde4db44e7973458ada732d2cd75e764f6` is the
manifest-only lock **child**: its entire diff is adding `verification/probe-fixture-lock.json`, one
file, one insertion [verified]. Because the child adds only the lock file, the two trees are identical
in every path the lock names — so hashes recompute against either tree, and they do so **by
construction, not by coincidence**. The authoritative tree is the one the lock itself names,
`20f9e60a`; `43edf9bd` is where the lock file lives.

1. **Lock leg — fixture inputs against the named historical tree.** Every one of the 118 hashes in
   `verification/probe-fixture-lock.json` must recompute against `20f9e60a`'s tree, read from Git. All
   118 recompute with zero mismatches [verified]. **The lock is preserved unchanged and is never
   re-derived.** Re-locking against `C_base` would erase the provenance the lock exists to preserve,
   so a mismatch here returns the item to design; it never authorizes a replacement lock.
2. **Current-output leg.** Current outputs are *not* checked against the lock. They are validated
   through the transition-ledger machinery already committed in `verification/capture_baseline.py`:
   - `_frozen_batch` (`capture_baseline.py:76`) loads the batch manifest **from Git at the named
     `P_seed` commit** `52a03cd2d0a9fdd340b60b16cea79a5b72234b08` and checks it against
     `FROZEN_BATCH_SHA256`. `build_manifest` (`:86`) reconstructs the frozen source inventory from
     that, and `validate_manifest` (`:134`) requires the on-disk manifest to equal both the frozen
     `P_seed` manifest bytes and that reconstruction. The manifest's `canonical_batch` pin names the
     frozen bytes by construction, never the working-tree file.
   - `validate_current_batch` (`:166`) validates the current batch separately, at its own pinned hash,
     and requires its record inventory to be closed.
   - `validate_output_transitions` (`:241`) covers the generated outputs under `tests/fixtures` — that
     is the path scope it diffs. Within that scope it proves every post-`P_seed` byte is either
     metadata-only — `_snapshot_semantics` strips two version fields plus `integrity.digest` and
     requires byte-identical structures otherwise — or owned by a named A/B row in
     `verification/expected-transitions.md`. It does not cover `verification/`; leg 3 does.

   `verification/expected-transitions.md` states the same semantics outright: "The Phase 1 probe lock
   is authoritative only at `P_seed`," and the current batch "must not be presented as a current
   member of the frozen `P_seed` byte inventory."
3. **Verification-code leg — locked probe/verification files pinned at current bytes.** The six
   non-fixture rows in the lock are live code, not frozen evidence, so neither leg above pins them.
   The Phase-1 kept test pins each at its **current** SHA-256 in the implementation tree. Any
   difference between a file's lock-time bytes and its current bytes must be **ledger-owned**: a named
   row in `verification/expected-transitions.md` giving the file, both hashes, the owning commits, and
   the reason.

   One such difference exists today. `verification/capture_baseline.py` moved from its lock-time bytes
   in `da4aa78` ("docs: reconcile parser evidence contract") and `46694e2` ("fix verification artifact
   source inputs") [verified]. That change gets its named row, citing both commits. The five probe
   scripts are unchanged from lock-time bytes and are pinned there.

   A future change to any of these six files requires a new named row in the same landing unit. An
   unowned byte change is a hard failure.

A failure in **any** leg stops the plan and returns the item to design. An unowned current-byte change
to locked verification code is exactly as fatal as a lock mismatch; the difference is only which
authority names it.

#### The missing committed check — Phase 1 adds it

Today the lock leg exists only as a hand-run: no committed test verifies the lock against its named
historical tree. That is the one real residual gap in `C_base`'s evidence contract.

**Phase 1 must add that check as a kept test.** It must:

- read `probe_fixture_commit` **from the lock file itself** and assert it equals
  `20f9e60a19b30bc1ec9a27aacb08380f4bc45602`, then recompute against *that* tree. It must not hard-code
  `43edf9bd` as the tree to check — that is the lock file's home commit, not the tree its hashes
  describe;
- read each locked path's bytes from Git at that commit (the same `git show` route `_git_bytes`
  already uses), recompute SHA-256, and require an exact match for all 118 rows;
- assert anti-vacuity: the row count is 118 and every row was actually read;
- separately assert leg 3 — each of the six verification/probe rows matches its current on-disk bytes,
  and any file differing from its lock-time bytes has a named ledger row;
- never read the working tree for the historical bytes, and never rewrite the lock on mismatch.

It lands in `C_prod` beside the other verification tests.

### Closed fixture inventory

`verification/fixture-manifest.json` is the only input inventory for this item. It expands the
canonical `tests/fixtures/v6_recapture_batch/batch.json` and requires exactly 37 fixture roots and 37
records.

The batch manifest has **two states, and each count must be labeled with its state.**

| State | Batch SHA-256 | Records | What it is |
|---|---|---|---|
| **Frozen, at `P_seed` `52a03cd`** | `bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288` | 15 graph / 22 typed refusals | The input inventory. Reconstructed from Git, never read from the working tree. This is what `canonical_batch` pins. |
| **Current, at `C_base` `78a9beb9`** | `7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40` | 14 graph / 23 typed refusals | The output expectation. Validated by `validate_current_batch` at its own pinned hash. |

The 15/22 → 14/23 move is one record, `deep_cross_scope_probe`, going graph → refusal. It is a named,
ledger-owned A2 transition, ruled on below. `plant_value_shapes` also moved in the same
reconciliation without changing the graph/refusal totals.

Neither state may be presented as the other. A frozen count quoted as current, or the current batch
quoted as a member of the frozen `P_seed` byte inventory, is a defect in the document that states it.

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

Anti-vacuity checks require: 37 canonical roots; 15 graph and 22 typed-refusal records **in the frozen
`P_seed` state**, and 14 graph and 23 typed-refusal records **in the current state**; at
least one enumerated source file per canonical root; six added roots; seven added source files; seven B2
topology rows; at least one real feature-reference and one real feature-chain fact in B8a; at least
two parser documents and one unit-bearing feature from each in B10; and at least one graph or named
refusal record for every inventory root. All evidence paths are repository-root-relative
`root-N/<relative-path>` values, never machine-absolute paths.

### Baseline capture

The retained baseline record captured the 37 canonical roots at the comparison baseline and the
six added roots at the probe/fixture commit while production source was byte-identical to the
baseline parent. That record is preserved unchanged. It stores:

- source commit, fixture path/hash, Python/SysIDE/agentic versions;
- graph codec bytes and semantic node/edge identity rows;
- public diagnostic code, reference, and location for refusals;
- generated package relative paths and SHA-256 for successful models;
- live/snapshot parity and executable output hashes where applicable.

`verification/expected-transitions.md` is the only allow list. Every changed edge, diagnostic, or
generated byte must name a transition row and proving test. All other maintained outputs stay
byte-identical.

### `deep_cross_scope_probe` — graph to refusal is intended tightening

**[AGENT] (ratified by owner, 2026-08-17)** — rulings 4-5. The `deep_cross_scope_probe` record moved from graph to
refusal between `P_seed` and `C_base`. That move is **correct and is never reverted.**

The evidence [verified, `run-records/phase1-stop-report.md`, Finding 2]: the fixture's Pattern B
authors an input aimed at the one concrete produced output
(`tests/fixtures/deep_cross_scope_probe/design.sysml:77`). The pre-transition baseline graph did not
wire that consumer to the concrete producer channel — a sibling consumer in the same fixture,
`derived_calc`, did receive it. It wired the consumer instead to
`DeepCrossScopeProducer__Core_Metric__metric_value`, a definition-scoped name surfaced as a
**caller-supplied entry-point parameter with `default_value: null`**.

That is this item's forbidden class verbatim: a reference the toolchain could not honor was silently
changed into another expression through a caller-supplied substitute. The old capture was not a
capability being lost; it was the defect this item exists to remove. At `C_base` the fixture refuses
with the named, fail-closed `SI_OCCURRENCE_MISSING` diagnostic and the authored reference preserved,
which is the contract.

Two consequences bind implementation:

- **Never restore the old graph.** A change that returns `deep_cross_scope_probe` to a captured graph
  restores the substitution defect and fails the item, regardless of what the batch counts look like.
  This is a stop condition, not a reconciliation to negotiate.
- **The exact deep qualified-output shape is a separately owned capability, not a silent gap.** The
  authored shape is legitimate; the product simply does not implement exact wiring for it yet.
  Refusing it by name is the correct behavior in this item. The follow-up is filed as its own row in
  the documentation and backlog obligations below.

### Transition ledger seed

| Transition | Old behavior | Required result | Proof owner |
|---|---|---|---|
| A1 occurrence selection | nearest/descendant/sole candidate may answer | exact address in consumer domain or named missing/ambiguous refusal | `test_occurrence_domain_derivation.py`; public mutation test |
| A2 calculation output | nearest or globally sole calculation may answer | exact output-index record contextualized by usage owner and consumer domain | `test_occurrence_calc_domain_derivation.py`; public mutation test |
| A3 lineage miss | one descendant may answer | lineage-local result or `SI_OCCURRENCE_MISSING` | expanded `test_definition_owned_reference_positions.py` |
| A4 package/model root | model root may answer a consumer miss | direct one-step package-owned no-prefix result; nested no-prefix refusal | B2 probe and `test_occurrence_domain_derivation.py` |
| A5 indexed expression | one input route refuses while computed/alias/predicate routes may erase the index | every expression site returns `IndexedReferenceUse` and refuses pre-graph; consumer backstop also refuses | consumer matrix in `test_expression_evidence_integrity.py` |
| A5a indexed bare chain, singular slot | zero-diagnostic graph; authored index silently rewritten to occurrence zero, in range or not | pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED` naming the authored reference | `test_expression_evidence_integrity.py`, `Cell[1]` out-of-range case |
| A5b indexed bare chain, plural slot | strict: incidental `SI_OCCURRENCE_AMBIGUOUS` — a name about occurrence selection, for an index defect; lenient: a graph carrying `SI_OCCURRENCE_AMBIGUOUS` + `SI_OCCURRENCE_MISSING` | both arms refuse pre-graph with `SI_INDEXED_SOURCE_UNSUPPORTED`; the inventory refuses before occurrence resolution runs, so the lenient graph disappears too | `test_expression_evidence_integrity.py`, `Cell[3]` case |
| A6 multiplicity writer | unrelated sole writer may answer | owner-address writer or `SI_MULTIPLICITY_UNRESOLVED` | `test_occurrence_multiplicity_authority.py`; public mutation test |
| B1-B5 evidence | fallback, partial traversal, raw unit/depth walk, optional target, or QN filter continues | exact evidence/DocumentTier or `SI_EVIDENCE_INCOMPLETE`; no alternate raw route | agentic owner tests; codegen consumer/ownership matrix |
| Deep relationship path | missing middle segment is filtered | total exact path or `SI_EVIDENCE_INCOMPLETE` at that segment | public deep-override regression |
| B6/B7 metadata | weak type or skipped redefinition identity may pass | sole qualified type and one exact slot family, or named refusal | `test_feature_typing_integrity.py`; occurrence tests |
| B8 leaf | resolved fact may be skipped | pre-change real corpus is total; post-D5 missing leaf raises the typed error | B8a retained real probe; B8b agentic/codegen regressions |
| B9 exit type | CLI preflight is correct but exported registry accepts a second caller account | graph-derived wrappers in every seam; `EXIT_POINT_TYPE_UNSUPPORTED` before mutation | `test_generation_exit_type_preflight.py`; exported-API proof |
| B10 source origin | sole glob may supply a file | measured `DELETE_UNREACHABLE`, then fallback deletion | B10 retained probe and metadata test |

A4 has its own row because package anchoring and consumer-root fallback are separate behavior from
A1/A2 contextual selection.

A5a and A5b are new in Revision 7. They are the two measured `C_base` behaviors of the bare indexed
chain, split because they fail differently and prove different things: A5a proves the silent rewrite
exists at all, A5b proves the *name* of the refusal changes. Phase 4's reconciliation gate must expect
both, and specifically must expect the `SI_OCCURRENCE_AMBIGUOUS → SI_INDEXED_SOURCE_UNSUPPORTED`
diagnostic transition rather than flagging it as an unlisted change. The pre-existing A5 row already
anticipated the direction ("an element index is ignored → pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED`");
A5a/A5b make the two starting states explicit so neither reads as unowned drift.

`verification/expected-transitions.md` gains the corresponding rows in the same landing unit as the
tests that prove them.

## Test design

### The indexed red set — both cases are required kept tests

**[AGENT] (ratified by owner, 2026-08-17)** — ruling 6. A single indexed stencil on a `Cell[3]` slot
does not establish the red. Measured at `C_base`, that shape already refuses, as
`SI_OCCURRENCE_AMBIGUOUS`; a red that comes from the wrong diagnostic is not the proof point. The red
set is therefore two cases, and both are kept tests, not throwaway probes.

**Case 1 — `Cell[1]` bare chain, index out of range.** `picked = cells#(2).mass` against a singular
`cells : Cell[1]`. At `C_base` this produces a **zero-diagnostic graph** in which the authored index
is silently rewritten to `cells[0].mass`. This is the escape itself, and the out-of-range index makes
the rewrite unarguable: no reading of the model makes occurrence zero the authored intent. The test
asserts, at `C_base`, that the graph is produced and carries zero diagnostics — that is the recorded
red. After the item lands, it asserts pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED` with the authored
reference and root-relative `file:line`, through the live, admitted, and capture arms, with no graph
and no snapshot byte written.

**Case 2 — `Cell[3]` bare chain.** `picked = cells#(2).mass` against a plural `cells : Cell[3]`. At
`C_base` this refuses as `SI_OCCURRENCE_AMBIGUOUS` in the **strict** arm and returns a graph carrying
`SI_OCCURRENCE_AMBIGUOUS` + `SI_OCCURRENCE_MISSING` in the **lenient** arm — both recorded in the
[behavior matrix](#current-code-facts) under ruling 4. The test parameterizes both arms, pins those
starting states explicitly, and requires each to become a pre-graph
`SI_INDEXED_SOURCE_UNSUPPORTED`. Its job is to prove the **ordering**, not merely that something
refuses: an end-to-end "it refused" assertion passes at `C_base` and proves nothing.

Neither case substitutes for the other. Case 1 alone cannot show that the inventory runs before
occurrence resolution, because nothing refuses on that path today. Case 2 alone cannot show the silent
rewrite, because that path already refuses. Both must be red at `C_base` for their stated reason, and
both must be green at close.

Operator-wrapped forms (`cells#(2).mass * 1.0`) are **not** red-set members. They refuse correctly at
`C_base` with the right code. They stay in the matrix as positive regression coverage, and a test that
treats them as the escape is measuring the wrong thing.

Both cases assert the ordering D7 fixes under
[inventory refusal precedes occurrence resolution](#inventory-refusal-precedes-occurrence-resolution).

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
- Unit annotations are covered at the required shapes ([ruling 1](#one-total-inspection-operation)):
  a simple `[m]`; representative compound forms such as `[kg/m^3]` and `[W/(m·K)]`, which must
  elaborate rather than refuse; a wrong-arity annotation through a synthetic node, which must raise
  `SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED)` and reach the public boundary as
  `SI_EVIDENCE_INCOMPLETE` — never return `None` and never be walked as general math; and a value
  operand carrying a reference, proving the value side is still visited while the unit side is
  never emitted.
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
| agentic `src/agentic_mbse/errors.py`, `sysml/reference_use.py`, `data_models.py`, `__init__.py` | Public semantic-evidence enum, error, API version, provenance-complete closed reference-use values, the shared `unit_annotation_value` primitive with an opaque unit operand, and deletion/de-export of the permissive facts and bool marker |
| agentic `sysml/syside_adapter.py`, `sysml/__init__.py` | Live metatype propagation, mapped index dispatch, direct `document_tier`, and obsolete export removal |
| agentic `sysml/expression.py`, `aggregation.py`, `binding.py`, `validation/adr002.py`, `constraint_extraction.py` | One reference inspector, shared traversal budget, total operand materialization, exact targets, and migration of every production helper consumer to the closed union |
| agentic `pyproject.toml`, `uv.lock`, tests, test ownership manifest, `docs/patterns/plant-idiom.md` | 0.1.3 package contract, semantic-evidence/v2 proofs, selector closure, and supported/refused modeling shapes |
| codegen `elaboration/occurrence.py` | General owner selector; containment-local kind/identity validation; address resolver; exact multiplicity owner; strict redefinition identities |
| codegen `elaboration/elaborate.py`, `elaboration/expression_evidence.py`, `expression_compiler.py`, `elaboration/__init__.py` | Producer index, strict expression-evidence inventory/adapter, exact-reference-only resolution, total deep-relationship path factory, and raw private graph builder |
| codegen `extraction/binding_source.py`, `elaboration/expression_evidence.py`, `source_evidence.py` (`elaboration/binding_evidence.py` and `extraction/unit_annotation.py` are deleted) | Strict closed binding-source variants, removal of optional semantic paths, and the value-site rule kept as Codegen policy in `expression_evidence.unit_annotated_value` over Agentic's `unit_annotation_value` primitive |
| codegen `orchestration/elaborated_pipeline.py` | Single evidence conversion boundary for live/admitted extraction and elaboration |
| codegen `extraction/extractor.py`, `feature_metadata.py` | Delete dead reference reconstruction helpers; exact typing; B10 fallback deletion after verdict |
| codegen `cli/__init__.py`, `generation/registry.py` | Graph-derived exit-wrapper authority on every exported route and replacement of the untyped collector failure with fail-before-mutate `CodeGenerationError` |
| codegen `_upstream_pins.py`, `pyproject.toml`, `uv.lock` | Exact agentic package/API pins, codegen 0.1.1, dependency minimum, lock |
| codegen tests and local test ownership manifest | Dual-layer natural-route closure, deep-path index exclusion/refusal, repository-wide selector discovery with collision-aware reviewed rows and the adapter-free evasion mutant, scoped strict gates, off-route reachability, and direct exported-registry rejection tests |
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
- **`[DEEP-QUALIFIED-OUTPUT-WIRING]` as a separate agent-grade backlog row before close.** Exact
  wiring for a deep qualified reference to a concrete calculation output is a real, separately owned
  capability. This item refuses it by name; it does not implement it. The row names the authored shape
  in `tests/fixtures/deep_cross_scope_probe/design.sysml`, the current `SI_OCCURRENCE_MISSING`
  contract, and the A2 transition record.
- **Fix the stale fixture comment at
  `tests/fixtures/deep_cross_scope_probe/design.sysml:75`.** It currently reads "Exact projection
  wires this input to the one concrete core output," which contradicts the recorded refusal and
  describes the substitution defect that was removed. Replace it with the current contract — this
  reference refuses with `SI_OCCURRENCE_MISSING` because no producer exists in the consumer's domain —
  and point at `[DEEP-QUALIFIED-OUTPUT-WIRING]`. The comment is documentation, not a fixture-behavior
  change; the fixture's authored reference and its refusal are unchanged.
- P-003's agent-written first-application status so every definition-owned lineage miss is described
  as refusing after A3. Its owner-verbatim promise is unchanged.
- The epic's stale predecessor wording, `.project/CURRENT_WORK.md`, product index/status, and the
  explicit block on `elaborator-downstream` during close-out.

## Sequencing and landing gates

This design does not resume the failed candidate's implementation checklist. It needs the review's
targeted confirmation and a replacement plan. That plan uses these gates:

1. **Branch from the audited production tree.** Create the implementation branch directly from the
   old `C_prod`, `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, and use Agentic input
   `2171016d3e3e0805525aa4cf787c55c6293dd00c`. Do not branch from this documentation checkout or
   from a parent of the failed candidate. Preserve D1-D4, the probes, and the verification harness.
   Verify the lock through all three legs above: fixture inputs against the tree the lock names
   (`20f9e60a`), current outputs through the transition-ledger validators, and the six
   verification/probe rows pinned at current bytes with any difference ledger-owned. Add the missing
   committed historical-tree lock check as a kept test. Add failing natural-route tests — including
   **both** indexed red cases — and the initial local ownership manifests before production edits.
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
| CI-2: raw operand and depth bypass | D5/D7 | One shared budget and total operand materialization fail through each natural consumer, including a unit wrapper — whose proof runs against the annotation-level materialization and the **value** operand, since ruling 1 leaves the unit operand untraversed |
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

Revision 8's four rulings are settled owner material, not open questions. The plan revision that
resumes Phase 3 must carry:

- the opaque unit operand and its required coverage — `[m]`, compound forms, wrong arity, and the
  value operand's references still visited (ruling 1);
- the shared `unit_annotation_value` primitive landing in Agentic, with Codegen's
  `expression_evidence.unit_annotated_value` reduced to value-site policy over it, and the arity
  refusal stated above (ruling 2 plus the [AGENT ruling] on what "enforce" produces);
- the Codegen selector gate's repository-wide scope, its collision-aware rows for neutral
  `ExpressionIR.operands` and `SourceFile.referent` with their stated proof artifact, the
  adapter-free evasion mutant and its equality-gate kill criterion, and the remaining rows staying
  red until migrated or mechanically excluded (ruling 3);
- both arms of the plural `Cell[3]` case in the behavior matrix and in Phase 4's reconciliation
  expectations (ruling 4).

Two consequences the plan revision has to act on, not merely carry:

1. **Reopening Agentic reopens Phase 2's audited surface.** Phase 3 treated the Agentic tree as
   read-only; rulings 1 and 2 land there, so the phase boundary must allow it — under the same
   `0.1.3` / `semantic-evidence/v2` contract, since that artifact was never released.
   [Agentic semantic contract](#agentic-semantic-contract) already requires the scoped strict lane,
   standalone tests, and lint to pass from the committed Agentic tree before Codegen consumes it;
   **that requirement applies again to this landing**, and the Phase-2 audit's m3 disposition is
   re-established there on the non-emission mechanism (see ruling 1 above). Otherwise the plan lands
   an Agentic change on a tree whose audit is dated to different bytes.
2. **Plan Phase 3's "removes the ~26 unowned reads" premise is falsified — restate that checklist
   item.** Phase 1 recorded removal as the route to a green manifest (plan.md, Phase 1 deviations
   item 5). The stop report's premise conflict 1 falsifies it for 11 of those reads, and ruling 3
   replaces removal with collision-aware rows plus migration or mechanical exclusion, against the
   owner's measured 20-row failure. The plan revision must rewrite the item to that target rather
   than restate the old one.

This document's own review scope is Revision 8's four areas. Everything Revision 6's review approved
stays approved, and the closed Revision-7 amendment is not reopened. The current product-lens gate
stays `BLOCKED` until the indexed-consumer architecture and its three-leg closure proof are proven
green in production.

The consuming artifact is the **next plan revision**, which resumes at **Phase 3** from the stop
report's rollback point (`git reset --hard d257ef1` on `stop-parser-impl-r2`). Phases 1 and 2 are
complete and audited; plan rev 3 already consumed Revision 7's carry-list — the three-leg lock rule
and committed historical-tree check in Phase 1, the D10 rerun trigger, both indexed red cases, the
A5a/A5b reconciliation rows, the `deep_cross_scope_probe` never-restore stop condition, and the
fixture-comment plus `[DEEP-QUALIFIED-OUTPUT-WIRING]` obligations. Those stay in force; none is
rebuilt.

The plan must keep both local ownership manifests, the scoped strict gates, full natural-route
matrices, probe/fixture lock, and `C_prod`, `F_final`, and `C_evidence` boundaries as checked
deliverables. Implementation is followed by an independent `my-audit`; the implementing agent does
not self-certify.
