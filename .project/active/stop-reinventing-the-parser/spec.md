# Spec: Exact occurrence derivation and evidence integrity

**Status:** Implementation in progress — rev 4; Phases 1–3 closed; Phase 4 implemented, audit
pending; Phase 5 not started; product lens `CLEAR`; spec review `Approve`
**Owner:** Reid W
**Created:** 2026-08-16 20:42
**Updated:** 2026-08-18
**Complexity:** HIGH
**Branches:** codegen `main`; agentic-mbse `self-binding-replacement`

---

## Problem

The public pipeline still follows the intended architecture:

```text
SysIDE semantic model
  -> exact declaration and occurrence elaboration
  -> InstanceGraph
  -> ComputationGraph
  -> Python / TEAx
```

Two boundaries can still corrupt that result.

First, SysIDE resolves a reference to an exact Feature and identifies its owning declaration, but it
does not emit concrete occurrence identities. Codegen must materialize occurrences from modeled
usage, containment, domain, and multiplicity. Some current paths instead choose by nearest ancestor,
descendant search, sole candidate, or first match. Those rules can name an occurrence the model did
not identify.

Second, extraction can discard or misclassify SysIDE evidence before the exact-ID compiler receives
it. Broad exception handling, Python-class-name tests, qualified-name prefix tests, staged name
fallbacks, and warn-and-continue behavior can silently produce an incomplete or incorrect graph.

This item removes both failure modes. For occurrence resolution, the contract is:

```text
exact referent Feature
  + exact owning declaration supplied by SysIDE
  + consumer domain occurrence
  + complete modeled containment path and multiplicity
  -> exactly one concrete occurrence, a modeled plural result, or a named refusal
```

Owner class is one required input, not the whole answer. A usage-owned referent such as
`comp_a::length` carries exact declaration authority and still needs contextual instantiation. A
definition-owned referent such as `'Unit'::cost` does not identify an occurrence by itself. Either
case refuses when the modeled context cannot derive the required occurrence.

**[NEED]** This item enforces the owner's product definition and parser-authority rule recorded in
`.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`: parse the model, walk the resolved
semantic tree to reconstruct the math, and emit that math through TEAx; do not replace an unresolved
reference with a manual fallback or workaround. P-002 remains the product promise for exact
usage-owner anchoring.

### Immutable baseline and entry gate

The inspected committed baselines are:

- sysml-codegen: `26e19f9`
- agentic-mbse: `8b105b3`
- fusion-tea verification corpus: `be1ee7c0`

Uncommitted worktrees are not part of the contract. The closed `self-binding-replacement` changes
must be landed on named commits before design begins. Design records the resulting descendant SHAs
for every repository it changes and reconciles any overlap with this item. This item does not absorb
or reopen the predecessor's certified scope.

---

## Scoped Sites and Required Proof

The two lanes share one completion authority. Each row carries its own proof. A green corpus cannot
substitute for a forced-failure test, and a forced failure cannot substitute for correct positive
semantics.

### Lane A — occurrence derivation

| ID | Site and defect | Required outcome | Required proof |
|---|---|---|---|
| A1 | `_select_occurrences`: nearest ancestor, descendant, or sole-candidate election | Derive from exact declaration ownership and consumer domain; refuse when scalar context is not singular | Real models through SysIDE: same-domain success, nested-domain success, multiplicity, unrelated target, and ambiguous target |
| A2 | `_select_calc_nodes`: the same election for calculation usages | The same derivation-or-refusal rule as A1 | Real SysIDE models covering positive and refusal outcomes |
| A3 | `_resolve_leaf`: descendant search after a consumer-lineage miss | A lineage or other modeled relationship must establish the target; descendant count never does | Real SysIDE models for local lineage, one descendant, several descendants, and sibling subtrees |
| A4 | `_select_occurrences` / `_select_calc_nodes` model-root arm | Package-scope results derive from exact top-level declarations and modeled multiplicity; consumer scope never falls back to model roots | Package-scope and consumer-scope real-model tests |
| A5 | `_expression_references`: `#(i)` evidence is present but ignored | Refuse as a valid-but-unimplemented capability before graph construction; do not label the model ill-formed | Real model proving `cells#(2).mass` cannot silently become all cells; exact unsupported-capability diagnostic |
| A6 | `occurrence.py::_modeled_integer_bound`: model-wide sole candidate can determine occurrence count | A modeled bound resolves through an ownership-qualified writer; otherwise occurrence construction refuses | Real models for root and nested usages, valid bound, unrelated sole candidate, and ambiguous writers |

Copies under different outer occurrences are separated by the consumer's modeled domain. Multiple
indexed copies in one exact context require modeled plural or index semantics. Proximity and global
uniqueness never add authority.

`sum(cells.mass)` fan-out is kept. A chain over a multiplicity yields all modeled occurrences and
`sum` aggregates them. The valid but unimplemented `cells#(2).mass` form is different: the current
generator cannot honor its index and must say so rather than compute a different expression.

### Lane B — evidence integrity and fail-closed handoff

| ID | Site and defect | Required outcome | Required proof |
|---|---|---|---|
| B1 | `syside_adapter.py::is_instance`: catches a live SysIDE failure and answers by class-name substring | Live metatype failures propagate; the explicit no-SysIDE mock path remains separate | Forced adapter failure plus no-parser mock coverage |
| B2 | `expression.py::_is_operator_expression`: Python class-name test | Dispatch uses the mapped SysIDE metatype | Real SysIDE subtype cases, including `FeatureChainExpression` |
| B3 | `expression.py::traverse_expression`: operand-iteration errors are swallowed | Iteration failure is named; no subtree disappears | Forced failing iterator that would otherwise remove a dependency |
| B4 | `expression.py::extract_feature_refs`: staged name ladder can return nothing | Exact `referent` or `target_feature` identity is retained; an unanswerable reference fails | Real reference and chain extraction plus forced missing-identity failure |
| B5 | `expression.py::_is_standard_library_ref`: qualified-name prefix decides origin | Standard-library filtering uses exact document origin | Real standard-library reference and a real user package named `SI` |
| B6 | `extractor.py::_map_sysml_to_python_type`: simple name, first typing, unknown pass-through | Type mapping uses exact qualified typing; missing, multiple, or unsupported typing refuses | Real models for supported primitives, a user-defined `Real`, and multiple/unsupported typings |
| B7 | `occurrence.py::build_feature_slot_index`: resolved redefinition endpoint can be skipped | A required stable identity is retained or fails by name; one feature slot cannot silently split into two | Forced missing-identity case plus a real redefinition fixture |
| B8 | `_expression_references`: a resolved fact with no leaf may be skipped | Prove the state unreachable, or emit a named diagnostic before dependency counts diverge | Targeted probe retained in the repository, followed by a regression for the measured outcome |
| B9 | `generation/registry.py`: an unmapped exit-point type warns and omits its wrapper | Generation stops with a named error; it never emits a package that fails later at load | Forced unsupported output type through the public generation boundary |
| B10 | `feature_metadata.py::_source_file`: a sole globbed file can substitute for exact document origin | Prove the branch unreachable on the public route, or replace it with exact origin/refusal | Licensed multi-file probe retained in the repository |

### Explicit dispositions outside the lanes

- Parameter groups named after source files are a documented rendering policy and stay unchanged.
- Output-alias first-wins stays out of scope, but its silent loss of the second authored file must be
  filed as a separate backlog row before this item closes.
- The three off-route extraction modules stay out of scope because they cannot reach public
  generation. Their eventual deletion remains a coverage problem.
- The Stellarator model remains held under its existing backlog item.
- Implementing indexed-element expression support is not part of A5. A5 files that capability and
  makes the current limitation honest.

---

## Success Criteria

- [ ] Every A1–A6 row produces the modeled occurrence result or a named refusal, proved by the real
      SysIDE model cases listed in its row. No result depends on proximity, arrival order, or global
      uniqueness.
- [ ] Every B1–B10 row retains exact evidence, returns the correct positive result, or fails by name,
      proved by the evidence type listed in its row. No row is certified only by a corpus that never
      exercises its failure branch.
- [ ] P-002 still holds: one modeled source occurrence becomes exactly one runtime source, including
      usage-owned qualified references and nested modeled containment paths.
- [x] Every positive A1-A4/A6 occurrence shape has an off-default public mutation proof: changing
      one modeled source changes every and only the generated runtime consumers bound to that
      source. Internal occurrence or graph assertions alone do not certify the result.
- [ ] A checked reconciliation ledger maps every historical census row L-01–L-14 and U-1–U-2 to an
      A/B row, an explicit disposition above, or a separately filed follow-up. Nothing disappears by
      omission.
- [x] The implementation captures a pre-change output baseline from the named implementation SHAs.
      Every maintained model outside an explicit expected-transition ledger remains byte-identical.
      Each transition row names its old behavior, required new result, and proving test.
- [ ] Ill-formed models receive diagnostics naming the reference, source file and line, and missing
      modeled authority. Valid but unimplemented forms receive a distinct unsupported-capability
      diagnostic that does not blame the model.
- [x] The indexed-expression capability and output-alias silence each have a separately owned
      backlog row before this item closes.
- [x] Agentic-mbse guidance states the supported reference shapes, the context each requires, and
      the refusal or limitation for unsupported shapes. Owner class is described as one input to
      derivation, not as the sole decision.
- [x] Fusion Tea models are verified against the final rules. They are edited only if a real
      violation is found.
- [ ] P-003's agent-written application status is reconciled with the final A3 behavior at close;
      its owner-verbatim promise is unchanged.
- [ ] `elaborator-downstream` design and implementation do not start until this item is implemented,
      audited, and closed.

## Known Requirements

- **[HARD]** SysIDE's resolved referent and exact owning declaration are authoritative. Codegen reads
  them and never infers owner class from written spelling.
- **[HARD]** SysIDE does not emit the concrete occurrence identities this generator needs.
  Materializing finite, parent-contextual, multiplicity-indexed occurrences from semantic usage
  declarations remains codegen's job.
- **[HARD]** `'CAS Scope'::shared` identifies an enumeration value and must keep working. The six
  `::` uses in `fusion-tea/models` are this shape.
- **[INHERITED]** Each risk-bearing unresolved site opens with a retained probe or learning test and
  written kill criteria; a failed probe returns the item to design before production changes. Source:
  `.project/backlog/epic_elaborate_first_architecture.md`, Success Criteria fail-fast gate.
- **[INFERRED]** (agent recommendation ratified by owner, 2026-08-16) This item completes before
  `elaborator-downstream` design or implementation. The recommendation was made in
  `spec-review.md` L4-1 and the owner directed the spec fixes to be applied; it remains agent-grade.
- **[INFERRED]** Candidate enumeration and uniqueness checks are allowed implementation techniques.
  The required outcome is exact semantic derivation or named refusal; no particular algorithm is
  mandated here.
- **[INFERRED]** The inline sibling form is supported because SysML v2 uses it in its normative
  examples and SysIDE resolves it. Codegen still has to derive its concrete target from the modeled
  shared domain.
- **[INHERITED]** This item serves P-003, preserves P-002, and files the valid-but-unimplemented A5
  gap under P-001. Sources: `.project/product/P-001-design-search-free-variation.md`,
  `P-002-exact-owner-anchoring.md`, and `P-003-no-workarounds-for-bad-models.md`.

## Non-Goals

- Retiring or weakening P-002.
- Blanket refusal of `::` references.
- Rewriting models merely to avoid supported qualified references.
- Implementing indexed-element expression evaluation.
- Changing unrelated rendering policy or off-route legacy extractors.
- Adding strategy objects, registries, compatibility layers, or a second resolution architecture.

## Open Questions / Deferred to design

- The data structures and algorithm used to derive the complete modeled declaration path from the
  consumer domain to the target owner at arbitrary supported depth.
- Whether refusal cases share one diagnostic code or use several codes. Every message must still
  satisfy the outcome requirements above.
- The landing order across codegen and agentic-mbse after the immutable predecessor commits are
  recorded. Each repository must remain independently green.
- The detailed implementation sequence after the required B8/B10 probes. Tests, code changes,
  guidance, and the Fusion Tea sweep must all land, but their order beyond the fail-fast gate is plan
  work.
- The measured disposition of B8 and B10 after their retained probes run.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_elaborate_first_architecture.md`
- **Primary research:**
  `.project/research/20260816-205035_premise-audit-fallback-census.md`
- **Prior review:** `.project/active/stop-reinventing-the-parser/spec-review.md`
- **Product lens:** `.project/active/stop-reinventing-the-parser/product-lens.md`
- **Product promises:** `.project/product/P-001-design-search-free-variation.md`,
  `.project/product/P-002-exact-owner-anchoring.md`,
  `.project/product/P-003-no-workarounds-for-bad-models.md`, and
  `.project/product/P-004-product-identity-parse-walk-emit.md`
- **Blocked consumer:** `.project/active/elaborator-downstream/spec.md`
- **Design:** `.project/active/stop-reinventing-the-parser/design.md` (to be created)

---

**Next Steps:** Land and record the closed predecessor commits, rerun `my-spec-review` on rev 4, then
proceed to `my-design` only after the review approves the contract.
