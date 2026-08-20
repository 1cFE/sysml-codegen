# Brief — design Revision 8: targeted amendment after the Phase 3 stop

Item: `.project/active/stop-reinventing-the-parser/`. Amend `design.md` **Revision 7 →
Revision 8** as a **targeted amendment** — the same form Revision 7 took: change only what the
rulings below require, mark the revision and its cause at the top, and leave every other section
untouched. Do not restructure the document.

Read first: `design.md` (rev 7), `run-records/phase3-stop-report.md` (the cause),
`run-records/phase2-audit.md` (findings m2/m3 and the confirmation addendum — context for two
rulings), plan.md's Phase 1 completion "Issues/deviations" item 3 (the lenient-arm surfaced gap).

Provenance: everything in the "Owner rulings" section below is **[OWNER]** material, ruled
2026-08-18 after the Phase 3 stop-rule halt; quoted blocks are **[OWNER-VERBATIM]**. Carry these
grades into the design text. This brief's operational notes are orchestrator [AGENT] material.

## Owner rulings to encode

### 1. Compound-unit annotations — the unit operand is opaque

The design's `#one-total-inspection-operation` bullet "A structural unit annotation visits its
value operand and validates its shape…" rests on a falsified premise: Phase 2 implemented "its
shape" as "the unit operand is a feature reference," which is false for every compound unit
(`[kg/m^3]` is an `OperatorExpression`). The owner's replacement contract, verbatim:

> For a parser-accepted `[` annotation with exactly two operands, reference inspection visits the
> value operand and treats the unit operand as opaque. It neither traverses nor emits the unit
> operand. SysIDE owns the validity of the unit expression.

The owner adds (ruled, near-verbatim): drop the feature-reference **and** exact-referent
requirements on the unit operand; "This boundary should not validate unit grammar at all" —
which is different from saying any unit shape passes validation. Required test coverage, per the
owner: `[m]`; representative compound forms such as `[kg/m^3]` and `[W/(m·K)]`; wrong arity
through a synthetic node; confirmation that references in the **value** operand are still
visited.

### 2. One shared Agentic structural primitive for the annotation

**[OWNER]:** Codegen legitimately owns the decision that `0.2 [m]` is a literal value site
rather than a computed expression — but the parser-shape reading must have one owner. Add to the
Agentic boundary one shared primitive:

> `unit_annotation_value(expression) -> Any | None` — it should recognize `[`, enforce exactly
> two operands, return the value operand, and leave the unit operand opaque. Both
> `inspect_reference_uses` and Codegen should call it.

Consequence for the Codegen side: `expression_evidence.unit_annotated_value` keeps the
value-site **policy** but must delegate all structural interpretation (metatype, operator,
operand shape) to this primitive. The design's existing "annotated_ast_value is deleted"
direction stands; state that the value-site rule's home is Codegen policy over the shared
primitive.

### 3. Codegen raw-selector manifest — collision-aware rows, no adapter-only scope

**[OWNER], rejecting the adapter-import scoping proposed for the Codegen gate:** the Phase 2
audit recorded the unresolved hole (a helper can receive a SysIDE node as an argument without
importing the adapter); making adapter-import scope load-bearing would turn that known residual
into a legal escape. Verbatim requirements:

> - Keep repository-wide selector discovery.
> - Add explicit reviewed rows for neutral `ExpressionIR.operands` and `SourceFile.referent`
>   reads.
> - Give each row a field owner or receiver contract and a real closure proof.
> - Add an adapter-free evasion mutant such as `def consume(node): return node.referent`; it
>   must still be discovered.
> - Leave the genuine raw reads in `usage_extractor` and any unresolved off-route modules red
>   until migrated or mechanically excluded.

The owner notes the current manifest failure contains 20 rows, so the neutral-IR-plus-`referent`
resolution is not the entire closure. (This ruling governs the **Codegen** gate; it does not
reopen the audited Agentic gate.)

### 4. The plural-lenient behavior-matrix row

Close the known gap (plan Phase 1 deviations item 3; Phase 1 audit Minor 9): the behavior matrix
states only the strict arm for the plural `Cell[3]` bare chain. Add the measured lenient row —
under `strict=False` the route returns a graph carrying the `SI_OCCURRENCE_AMBIGUOUS` +
`SI_OCCURRENCE_MISSING` diagnostics (the documented strict/lenient delivery contract), while
after this item both arms refuse pre-graph with `SI_INDEXED_SOURCE_UNSUPPORTED`. The kept tests
already pin both arms; the matrix must state what they pin.

## Constraints [AGENT]

- Rulings 1-4 are settled by the owner: encode them, do not redesign around them. Where a ruling
  contradicts existing rev-7 text, the ruling wins and the amendment note names the change.
- Do not touch sections outside the amendment's reach; do not renumber D1-D9; keep all anchors
  other documents cite stable.
- The amendment must state its cause (the Phase 3 stop report) and list its changed sections at
  the top, as Revision 7 did.
- Plan revision is a separate later stage — do not edit plan.md.

## Deliverable

`design.md` updated in place to Revision 8 (do not commit; the orchestrator commits). Final
message: prose summary of exactly which sections changed and how each ruling landed, ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/design.md`.
