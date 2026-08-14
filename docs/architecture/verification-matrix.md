# Verification Matrix

Traceability matrix mapping every REQ-\* tag to its conformance test file and status.

## Summary

| Metric | Count |
|--------|-------|
| Total requirements | 280 |
| PASS (a kept test proves it and passes) | 136 |
| PARTIAL (a kept test covers part of the requirement; the gap is named in the cell) | 3 |
| RETIRED (subject deleted with the legacy stack) | 131 |
| UNTESTED (subject live, no test proves it) | 10 |
| DEFERRED | 0 |
| REQ families | 33 |
| Distinct kept test files cited | 55 |

> **Recounted from the tables 2026-08-14** (CONSTRAINT-SEMANTICS Item 7), per the recount discipline
> — index totals **and** per-family counts, never the summary block on trust. The recount **falsified
> the previous block**, which read PASS 133 / PARTIAL 3 / distinct test files 50 against tables that
> already held PASS 134 / PARTIAL 2 / 57 files. The drift was `REQ-CL-04`, upgraded PARTIAL → PASS
> when audit-7 F2 closed without the summary following it, plus a test-file count that had not been
> recomputed in some time. The remaining delta to the numbers above is this item's own four REQ-DIAG
> rows. Method and raw output: `.project/completed/20260814_constraint-docs-agent-sync/verification.md`.

**Status definitions:**
- **PASS**: At least one test **that exists in the tree** proves this requirement and passes
- **PARTIAL**: A kept, passing test covers part of the requirement, and the cell names exactly what a violation could do without failing it (audit-7 finding F2: a partially-covered row must not sit beside full-strength green unmarked)
- **RETIRED**: The requirement's subject was deleted by the Item 7 retirement. The row is the record of a removed design, not a claim about the product. The cell names the deletion-ledger row that carries the deletion and, through its `replacement_proof_node`, whatever behaviour survived
- **UNTESTED**: The subject is live but nothing proves it — either it never had a dedicated test, or its test retired with no replacement. The cell says which
- **DEFERRED**: Behavior implemented; real-fixture test deferred to a later item (none open — REQ-CA-09 discharged by Item 10)
- **Contract disposition** (SOURCE-IDENTITY Item 3): a row-local `> **Contract disposition — REQ-…**` line under a family table records how the source-identity contract treats that row's reading — `SUPERSEDED`, `PARTIAL` (every clause labeled `stands` or `SUPERSEDED`), or `FAILED` — pointing to the owning contract Appendix B row or Appendix C cell (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`; the contract's Current conclusion is the sole authority-state statement). Status stays test-state only: historical tests remain evidence of old behavior, not certification of the new contract.

> **This matrix was re-cited against the retired tree (Revise step 6d, 2026-08-12).** Before
> that pass, 56 of the 81 test modules it cited no longer existed, so 205 rows carried a PASS
> beside a file nobody could run. Every one of those rows was re-read against its requirement
> text and given one of two endings:
>
> - **The subject is live and the proof moved.** The row now cites the kept node(s) that prove
>   it. Where the recovery's deletion ledger recorded where a deleted module's responsibility
>   went (`.project/active/cutover-recovery/ledger-4a.json`, `replacement_proof_node`), that
>   recorded heir is what the row cites — the mapping carries the ledger's authority, not this
>   pass's guess. Nine rows found no heir: their subject is live, nothing proves it, and they
>   read UNTESTED with the gap named.
> - **The subject died with its shape.** The row reads RETIRED and names the ledger row that
>   deleted it. No dangling citation is left behind. 131 rows ended here, which is the honest
>   size of what the retirement removed.
>
> **Every test file named in a PASS row exists in this tree.** A test filename inside an
> UNTESTED cell is part of the disposition — it says which retired module took the proof with
> it — and is deliberately not a citation.
>
> Read the RETIRED families — AS, BT, DRA, IR, MF, OR, ORCH, PGD, SVM, VBR, most of SNAP and
> RES — as the record of a deleted design. Where a row's requirement text names a legacy
> function (`build_pipeline_context()`, `build_computation_graph()`, `resolve_producer()`), it
> is naming code that was removed, not the product. The shipped route's own evidence is in
> `test_public_authority_switch.py`, `test_exact_*`, `test_elaboration_*`, and
> `test_snapshot_v6_*`, which is what the PASS rows now point at.
>
> **What this pass did not do.** It did not write REQ families for mechanisms the elaborator
> introduced and the legacy stack never had — the v6 envelope, occurrence identity, the
> projection receipt. Those are unwritten, named in the SNAP banner below, and still need an
> owner. Status stays test-state, as the contract-disposition convention above establishes.

> **Sweep note (PIPELINE-TRUTH Item 7).** The ~175-row deep-read sweep found ~30 PASS
> rows whose cited test passes but pins *less* than the full requirement text (e.g.
> field-name-only compares, `>=` count floors, self-contained parse checks). None is a
> correctness lie. They are enumerated with per-row dispositions in
> `[ITEM7-MATRIX-SWEEP-RESIDUE]` (backlog), to fix when each owning component is next
> touched. ~46 qualifying rows remain un-deep-read (named there — not asserted swept).

## Index

- [AS — Aggregation Scoping](#as) (8 retired)
- [AST — AST Dispatch Invariant](#ast) (10/10 pass)
- [BASE — Baseline Conformance](#base) (5/5 pass, 1 retired)
- [BT — Backtracker](#bt) (13 retired)
- [CA — Computed Attributes](#ca) (9/9 pass, 3 retired)
- [CL — Constraint Lowering & Catalog](#cl) (4/4 pass, 1 retired)
- [CON — Contracts & Sealing](#con) (10/10 pass)
- [DIAG — Diagnostic Severity](#diag) (2/4 pass, 1 partial, 1 untested)
- [DM — Data Models](#dm) (9/9 pass)
- [DRA — Resolution Architecture](#dra) (5 retired)
- [EC — Expression Compiler](#ec) (7/7 pass)
- [EPC — Entry Point Classification](#epc) (1/1 pass, 7 retired)
- [EXT — Extraction](#ext) (14/14 pass)
- [GA — Graph Assembly](#ga) (5/5 pass, 2 retired, 1 untested)
- [GEN — Generation](#gen) (6/6 pass, 1 untested)
- [HR — Hierarchy Resolver](#hr) (8/8 pass)
- [IR — Producer Resolution (re-projected)](#ir) (7 retired)
- [LVP — Literal Value Propagation](#lvp) (1/1 pass, 8 retired)
- [MF — Module Factory](#mf) (9 retired)
- [NC — Naming Conventions](#nc) (9/9 pass)
- [OR — Output Registry](#or) (9 retired)
- [ORCH — Orchestration](#orch) (7 retired)
- [OSR — Output Schema Rules](#osr) (4/4 pass, 3 untested)
- [PGD — Parameter Group Deriver](#pgd) (8 retired)
- [PIPE — Pipeline](#pipe) (7/7 pass)
- [PMM — PipelineModule Migration](#pmm) (4/4 pass, 1 retired)
- [PY — Pipeline YAML](#py) (8/8 pass)
- [REG — Module Registry](#reg) (9/9 pass)
- [RES — Resolution Overview](#res) (2/2 pass, 6 retired)
- [SNAP — Snapshots: Extraction Format & Snapshot-Driven Generation](#snap) (1/1 pass, 21 retired)
- [SR — Smart Regen / Preservation](#sr) (3/3 pass, 4 untested)
- [SVM — Supplied-Value Materializer](#svm) (4 retired)
- [VBR — Virtual Binding Rewrite](#vbr) (11 retired)

---

## Requirements by Family

### AS

**Aggregation Scoping** — Component C10 — [reference/13-aggregation-scoping.md](reference/13-aggregation-scoping.md)

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_elaboration_aggregations.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-AS-01 | Each PartDef-level aggregation SHALL produce one `ScopedAggregationData` per design insta... | — *(subject deleted — ledger L-098)* | RETIRED |
| REQ-AS-02 | Instance discovery SHALL try direct match (Strategy 1) before child-walk fallback (Strategy 2), as observed on the disjoint fixture cases exercised (no dual-match part-def case exists to show the short-circuit directly) | — *(subject deleted — ledger L-098)* | RETIRED |
| REQ-AS-03 | Instance paths SHALL be converted from `__`-separated to dotted format with design prefix... | — *(subject deleted — ledger L-098)* | RETIRED |
| REQ-AS-04 | CHAIN aliases SHALL only be produced for non-deep-path redefinitions whose `source_path` ... | — *(subject deleted — ledger L-098)* | RETIRED |
| REQ-AS-05 | Phase 1b SHALL register a canonical channel for each `ScopedAggregationData` | — *(subject deleted — ledger L-098)* | RETIRED |
| REQ-AS-06 | Phase 2 SHALL resolve `ChannelAlias.canonical_name` in registry before registering alias | — *(subject deleted — ledger L-098)* | RETIRED |
| REQ-AS-07 | `module_eqn` property SHALL be `"{instance_path}__{attribute_name}"` | — *(subject deleted — ledger L-098)* | RETIRED |
| REQ-AS-08 | The scoping function SHALL log a WARNING (not just info) when an | — *(subject deleted — ledger L-098)* | RETIRED |

### AST

**AST Dispatch Invariant** — Component C07 — [reference/19-ast-dispatch-invariant.md](reference/19-ast-dispatch-invariant.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-AST-01 | Every `is_instance()` dispatch that checks both FCE and OE SHALL check FCE first | `test_ast_dispatch_invariant.py`, `test_expression_compiler.py` | PASS |
| REQ-AST-02 | Every dispatch site checking both FCE and OE SHALL include a comment: "MUST be before Ope... | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-03 | Among reference/operator branches, dispatch ordering SHALL be FCE, OE, FRE (the cited test pins this ordering clause only; literal-before-catch-all is REQ-AST-08's row) | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-04 | New dispatch sites SHALL follow REQ-AST-03 ordering | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-05 | `hierarchy_resolver._walk_aggregation_ast()` SHALL classify FCE nodes as `SingletonTerm` ... | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-06 | A feature-chain reference in a CalcDef output SHALL be rejected as unsupported by the renderer (`calc_compat_renderer._render_reference`), not misread as an operator | `test_expression_compiler.py::TestRenderCalcExpression::test_feature_chain_raises_compilation_error` | PASS |
| REQ-AST-07 | `expression_utils.reconstruct_expression()` SHALL return `"name.attr"` for FCE (not `".(n... | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-08 | `reconstruct_expression` SHALL dispatch all literal/`NullExpression` branches (via `is_instance`) before the invocation catch-all | `test_expression_reconstruction_fidelity.py`, offline totality guard | PASS |
| REQ-AST-09 | `reconstruct_operator_expression` SHALL parenthesize a child operand iff it binds looser than its parent, or equal and on the associativity-unfavored side | `test_expression_reconstruction_fidelity.py`, `test_expression_paren_helper.py` | PASS |
| REQ-AST-10 | `hierarchy_resolver._walk_aggregation_ast()` SHALL dispatch all literal/null branches before the invocation catch-all | `test_agg_literal_dispatch.py` (`agg_literal_probe` fixture) | PASS |

### BASE

**Baseline Conformance** — Baseline Tests

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-BASE-01 | ComputationGraph JSON matches captured baseline | `test_baselines.py`, `test_public_route_baselines.py::test_regenerating_from_the_same_v6_snapshot_is_byte_identical` | PASS |
| REQ-BASE-02 | Baseline JSON deserializes back to valid ComputationGraph | `test_baselines.py` | PASS |
| REQ-BASE-03 | Registry __init__.py baseline is syntactically valid Python | `test_baselines.py` | PASS |
| REQ-BASE-04 | execution_order length equals modules length in every baseline | `test_baselines.py` | PASS |
| REQ-BASE-05 | solar_battery (YAML + graph + registry) and catf_mfe (graph + registry) re-captured via scripts, ordering-only, reviewed | — *(subject deleted — ledger L-147 / L-200 / L-278)* | RETIRED |
| REQ-BASE-06 | `entry_point_groups` SHALL be name-sorted in every ComputationGraph, so a model-discovery-order shift cannot redden a byte-exact baseline | `test_public_route_baselines.py::test_regenerating_from_the_same_v6_snapshot_is_byte_identical` | PASS |

### BT

**Backtracker** — Component C11 — [reference/11-analysis-backtracker.md](reference/11-analysis-backtracker.md)

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_elaboration_expose_shapes.py`, `test_elaboration_aggregations.py`, `test_elaboration_projection.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-BT-01 | Every non-literal binding SHALL be resolved via `_resolve_binding_via_registry()` through... | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-02 | Resolution SHALL dispatch on binding format: CHAIN bindings (no `::` in source_path) quer... | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-03 | DFS SHALL detect cycles via path tracking and raise `CircularDependencyError` | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-04 | Every binding SHALL resolve to exactly one `BindingResolution` — no binding left dangling | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-05 | `binding_resolutions` key format SHALL be `"{usage_qn}\ | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-06 | Topological sort SHALL produce dependency-first ordering or raise on cycles | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-07 | Self-reference guard SHALL prevent a usage from wiring to its own output | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-08 | Resolution SHALL use type-directed dispatch on `BindingType` format to select the correct... | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-BT-09 | The FORMULA `::`-QN REFERENCE path SHALL per-segment sanitize (`sanitize_qualified_name`) before comparison/lookup so a quoted-owner QN matches the sanitized design-attribute QN (Bug A; six-site lockstep flip, INV-1) | — *(subject deleted — ledger L-229 / L-126)* | RETIRED |
| REQ-BT-10 | A design attribute owned by a part **def** (empty `parent_part`) SHALL match its binding via a leaf-unique fallback over design-part attributes (calc-def I/O excluded), returning a QN only when exactly one candidate exists, else None (Bug B; INV-2, no cross-wire) | — *(subject deleted — ledger L-229)* | RETIRED |
| REQ-BT-11 | `_resolve_chain_dispatch` SHALL query the structured `_scoped_alias` namespace (Step 1c) by splitting `source_path` at the last dot, trying the consumer-scope-prefixed key `(consumer_scope.prefix, leaf)` before the bare `(prefix, leaf)` (Item 10 #1 / D-D sibling disambiguation), ordered after Step 1b and before the unscoped Step 2 (INV-A: additive, only where the ladder fell through) | — *(subject deleted — ledger L-173)* | RETIRED |
| REQ-BT-12 | For a 3+-segment CHAIN (`source_path.count(".") >= 2`), `_resolve_chain_dispatch` SHALL, after Step 2 misses, retry `scoped_lookup` over progressively shorter ancestor prefixes of the consumer scope (Step CLIMB, Item 2), collect every distinct non-self-reference hit, resolve iff exactly one, and refuse (return None → loud Step-4 fallback) on two or more — never silently pick (M-1 / INV-2b). Gated so 2-segment resolutions stay byte-identical (D4) | — *(subject deleted — ledger L-217 / L-122)* | RETIRED |
| REQ-BT-13 | A 3+-segment CHAIN that reaches the Step-4 fallback SHALL emit a genuine `logger.warning` (WARNING level, distinct from the benign per-binding DEBUG line) naming the full untruncated chain, and surface as an entry point — never truncated to root, never silently wired (Item-5 loud-diagnostic contract, D3 home) | — *(subject deleted — ledger L-217)* | RETIRED |

> **Contract disposition — REQ-BT-13: `PARTIAL`** (SOURCE-IDENTITY Item 3). The loud-warning /
> never-truncated / never-silently-wired clause `stands`. The surface-as-entry-point outcome for
> a bound model reference is `SUPERSEDED` (contract D-17; Appendix B row "A bound model reference
> that fails resolution may lenient-mint a per-consumer entry point").

### CA

**Computed Attributes** — Component C05 — [reference/16-computed-attributes.md](reference/16-computed-attributes.md)

**Classification contract (Item 4, fixed):** an attribute that references only inherited and/or local attributes classifies FORMULA. An inherited attribute's QN resolves into the **supertype (ancestor PartDef)** namespace; Step-2b now prefix-matches the owning part QN OR any ancestor PartDef QN (`computed_attribute_extractor._ancestor_part_qns`), so an inherited-attr ref is a sibling, not a cross-namespace calc output. A genuine calc output (D3 `mixed_expose`) still classifies EXPOSE_COMPUTED — the over-correction control. Pinned positively by **REQ-CA-12** and the 7-row `TestInheritedAttrClassification` table; the old `test_misclassification_documented` xfail site is deleted (no vacuous parametrization). The prior framing called this misclassification "**loud** (EXPOSE_COMPUTED rejection)" — that was wrong: a misclassified inherited-attr FORMULA was a **silent no-op**, dropped by the graph builder with no module and no diagnostic; only the "not a silent wrong value" half was true. That whole paragraph is now history — the graph builder and its D5 diagnostic were deleted by the Item 7 retirement, and so was `test_computed_attributes_e2e.py`. The filed follow-on `[TRUTH-DEBT-INHERITED-FORMULA-COMPILE]` outlived them and applies to the elaborator instead.

**Where this family stands after the retirement.** The classifier these rows describe, `extraction/computed_attribute_extractor.py`, is still in the tree but **off the shipped route** — nothing in `src/` imports it (the disposition and its reason are recorded in the module docstring). What keeps the PASS rows honest is `test_computed_attribute_golden.py`, a whole-corpus golden over `extract_computed_attributes` that pins the classification and compilation output exactly. The shipped route lifts computed attributes in the elaborator instead; its evidence is `test_elaboration_computed_attrs.py` and `tests/integration/test_computed_attributes_exact_route.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-CA-01 | Classification SHALL assign each attribute expression exactly one enum member | `test_computed_attribute_golden.py`, `test_elaboration_computed_attrs.py::test_all_fifteen_computed_attributes_lift` | PASS |
| REQ-CA-02 | FORMULA attributes SHALL compile to Python via the ExpressionIR render path (`extract_expression_ir()` + `render_calc_expression()`) | `test_computed_attribute_golden.py`, `tests/integration/test_computed_attributes_exact_route.py::test_every_formula_computed_attribute_becomes_an_auto_implemented_module` | PASS |
| REQ-CA-03 | EXPOSE_PURE SHALL produce a `ChannelAlias` for a PartUsage-level derived attribute; a PartDef-level EXPOSE (shape A) SHALL be expanded per design instance path into the structured `_scoped_alias` namespace (`_register_partdef_expose_scoped_aliases`, Item 10 #4) rather than emitting a template alias | — *(subject deleted — ledger L-104)* | RETIRED |
| REQ-CA-10 | A pure `FeatureChainExpression` whose `reference_chain` is a part-rooted ≥2-segment single-terminal chain (INV-E) SHALL be tagged `EXPOSE_CHAIN_TENTATIVE`, then the Phase-3b confirm walk over `reference_chain` SHALL finalize it to EXPOSE_PURE (+register the transitive channel) or revert to FORMULA; no tentative SHALL survive to any reader (INV-F raises) | `test_computed_attribute_golden.py` (whole-corpus classification + compilation golden) | PASS |
| REQ-CA-04 | LITERAL attributes SHALL be excluded from computed attributes | `test_computed_attribute_golden.py` | PASS |
| REQ-CA-05 | No `EXPOSE_PURE` alias exists for a non-EXPOSE_PURE attribute; and all fixtures contain zero UNRESOLVABLE computed attributes (the "UNRESOLVABLE SHALL not generate modules/aliases" contract is unexercised — documented coverage gap) | `test_computed_attribute_golden.py` | PASS |
| REQ-CA-06 | `AttributeResolutionKind` SHALL classify each FORMULA input as FORMULA or EXPOSE_ALIAS as exercised (the LITERAL classification is exercised via the design-attribute/entry-point path, not this route) | — *(subject deleted — ledger L-104)* | RETIRED |
| REQ-CA-07 | FORMULA self-reference SHALL be excluded from `input_names` | `test_computed_attribute_golden.py` | PASS |
| REQ-CA-08 | FORMULA compilation SHALL NOT resolve sibling FORMULA outputs | `test_computed_attribute_golden.py` | PASS |
| REQ-CA-09 | Shape-A resolution (part-def EXPOSE): the wi014_toy `demo_plant.total_cost` consumer SHALL resolve via `_scoped_alias` to the `cost_calc__cost` channel (the Item-1 malformed-refs deferral, discharged by Item 10 #4/#1) | `test_wi014_toy.py::test_wi014_toy_shape_a_resolves_via_scoped_alias` — repointed onto the exact route, which asserts the public shape-A `OutputAlias`; the `_scoped_alias` registry the text names retired with the v5 family | PASS |
| REQ-CA-11 | Shape-A EXPOSE_PURE (part def) in the attribute resolution map SHALL route by `is_on_part_definition` to a LITERAL fallback (not the refs-parser) and consult `_scoped_alias` to decide the warning: a registered leaf is silent (the name resolves via Item 10 and surfaces via Item 11), an unregistered one warns naming the real cause — retiring the Item-1 malformed-refs warning (`_resolve_expose_pure` in `graph_builder.py`) for the resolvable case | — *(subject deleted — ledger L-223)* | RETIRED |
| REQ-CA-12 | A reference whose QN sits under the owning part OR any **ancestor PartDef** namespace SHALL be treated as a sibling (Step-2b widened via `_ancestor_part_qns`, transitive), so an attribute referencing only inherited/local attributes classifies FORMULA — not EXPOSE_COMPUTED; a reference under a top-level CalcDef namespace SHALL stay a `calc_ref` (D3 over-correction control, `mixed_expose`). A FORMULA computed attribute that reaches graph-build without being FULLY_COMPILABLE SHALL emit a WARN and produce no module (D5 — the no-module outcome is loud, never a silent drop) | `test_computed_attribute_golden.py`, `test_silent_failure_d316.py` — classification clause only; the graph-build D5 WARN clause retired with `graph_builder.py` (ledger L-223) | PASS |

### CL

**Constraint Lowering & Catalog** — Items 5-9, Item 14 — [reference/28-constraint-lowering-and-catalog.md](reference/28-constraint-lowering-and-catalog.md)

Partial register (Item 14 docs pass): these five rows cover the mechanisms Item 14
directly touched or verified test-first; the full Items 5-9 surface (module wiring
detail, occurrence expansion, tracking-key correlation) is broader than this pass
re-derives from scratch and is named here as a known gap, not silently covered.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-CL-01 | `resolve_actual`'s strict ladder SHALL resolve a bound actual through, in order: registry scoped/alias/scoped-alias lookup, occurrence-scoped design attribute, definition-scoped target QN, definition-scoped base-literal-default (Item 14 D2-twin) — before the shared terminal-disposition switch (`strict=True`, never synthesizes) | — *(subject deleted — ledger L-214)* | RETIRED |
| REQ-CL-02 | Every concrete entry expanded from one `ConstraintUsageFact` SHALL share one compile-once predicate (grouped by `usage_qualified_name`), even across N owner-instance occurrences | `test_constraint_emission.py` | PASS |
| REQ-CL-03 | `assemble_constraint_catalog` SHALL build `source_records` from every `ConstraintDefinition` in the model's facts (visible even with zero eligible entries) and `concrete_entries` from eligible concrete constraints only, fingerprinted deterministically | `test_constraint_emission.py` — but see the divergence note below: the subject is the **retired** assembler, not the shipped one | PASS |
| REQ-CL-04 | The domain->catalog mapping SHALL be total and silent-drop-free: every member of `InstanceGraph.constraint_usages` has exactly one `usage_records` row, joined by `declaration_id` and never by qualified name, and every occurrence row joins exactly one member | `test_constraint_catalog_totality.py::test_the_catalog_carries_every_domain_member`, `::test_catf_mfe_d5_ships_all_sixty_five_rows`, the four preflight mutations (removed disposition, duplicated row, orphaned occurrence row, disagreeing counts) and the three graph-level mutations refused at `validate()` | PASS *(audit-7 F2 closed: the heir is no longer a 2-constraint specimen — the totality claim is asserted over the whole domain on every constraint-bearing fixture, and a dropped carrier fails by identity)* |
| REQ-CL-05 | A constraint input resolved to a design attribute SHALL mint a deduped entry point (reused, not re-minted, if already present); a resolved module-output input SHALL wire the producer channel with no mint; a resolved modeled-default input SHALL mint a `LIBRARY_DEFAULT` entry point scoped to its constraint | `test_exact_constraint_route.py::test_identified_facts_gate_and_projected_constraints_agree_by_usage_id`, `test_exact_route_constraint_portability.py::test_the_predicate_module_and_pipeline_are_identical_on_every_route` | PASS |

> **Divergence surfaced — REQ-CL-03 does not describe the shipped catalog** (Revise step 6d).
> The total-inventory guarantee in this row — a `source_record` for *every* `ConstraintDefinition`
> in the model's facts, visible with zero eligible entries — belongs to
> `assemble_constraint_catalog`, which the legacy route called and which now lives in
> `tests/helpers/retired_catalog_assembly.py` as a fixture builder. The shipped catalog is built
> by the projector (`elaboration/project.py`, `_build_constraint_catalog`), which derives
> `source_records` from the constraints it actually projected: a definition with no eligible
> entry produces no source record. Exclusion records diverge the same way. The cited test still
> passes, on the retired assembler. **Whether the shipped catalog should carry the
> total-inventory guarantee is an open product question with no recorded authority** — surfaced,
> parked, and deliberately not answered by re-citing the row onto a projector test that proves
> something else.

> **Contract disposition — REQ-CL-05: `PARTIAL`** (SOURCE-IDENTITY Item 3). The dedup-mint
> clause `stands`; the producer-wiring clause `stands` (cell C24 owns the computed-source
> mixed-consumer target and C17 the aggregation-producer target); the `LIBRARY_DEFAULT` scoping clause `stands` under the per-usage ruling
> (contract D-12, cell C23). All three stand as mechanics
> under the single identity authority; the row's evidence does not yet certify the
> source-identity contract.

### CON

**Contracts & Sealing** — Item 9 — [reference/29-contracts-and-sealing.md](reference/29-contracts-and-sealing.md)

Register covering the two contracts (`ModelContract` semantic identity,
`PackageContract` physical seal), fingerprint determinism, seal/verify parity, and the
emit/re-seal/subcommand wiring. The `contract INV-*` labels are the contracts
machinery's own numbering (a distinct namespace from the matrix REQ IDs). The
`verify_package` diagnostic surface beyond the verbatim-emission guard is exercised
indirectly via the emitted verifier.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-CON-01 | `build_model_contract` SHALL be a pure function of the `ComputationGraph` — no filesystem, no templates (contract INV-1) | `test_contract_models.py` | PASS |
| REQ-CON-02 | Both fingerprints SHALL be deterministic; `semantic_fingerprint` SHALL exclude itself from its own payload (contract INV-2, no circularity) | `test_contract_models.py` | PASS |
| REQ-CON-03 | A constraint-free graph SHALL still seal into a well-formed, stable contract (contract INV-7) | `test_contract_models.py` | PASS |
| REQ-CON-04 | On-disk `ModelContract` JSON bytes SHALL be a deterministic function of the graph (contract INV-6) | `test_contract_models.py` | PASS |
| REQ-CON-05 | The `seal.py` and `verify.py` glob-matcher bodies SHALL stay byte-identical (drift guard) | `test_contract_models.py` | PASS |
| REQ-CON-06 | `generate` SHALL emit three `contracts/` files (`model_contract.json`, `package_contract.json`, `verify.py`) and the result SHALL verify on load | `test_exact_route_seal_step9.py` | PASS |
| REQ-CON-07 | The emitted `contracts/verify.py` SHALL be byte-identical to the canonical verifier (contract INV-8 drift guard) | `test_exact_route_seal_step9.py` | PASS |
| REQ-CON-08 | The seal SHALL exclude its own `package_contract.json` from coverage | `test_exact_route_seal_step9.py` | PASS |
| REQ-CON-09 | Re-sealing after a stencil edit SHALL recompute only the `PackageContract` (graph-free) | `test_exact_route_seal_step9.py` | PASS |
| REQ-CON-10 | The `seal` subcommand SHALL require an already-sealed package (an existing `ModelContract`) | `test_exact_route_seal_step9.py` | PASS |

### DM

**Data Models** — Component C01 — [reference/09-data-models.md](reference/09-data-models.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-DM-01 | Every model referenced by another doc in this set SHALL appear here or have an explicit d... | `test_data_models.py` | PASS |
| REQ-DM-02 | Every enum SHALL list ALL values with no omissions | `test_data_models.py` | PASS |
| REQ-DM-03 | Field lists SHALL match source code (name) | `test_data_models.py` | PASS |
| REQ-DM-04 | Every model SHALL be importable from its documented source file | `test_data_models.py` | PASS |
| REQ-DM-05 | At least one populated `ComputationGraph` example SHALL demonstrate both `entry_point` an... | `test_data_models.py` | PASS |
| REQ-DM-06 | The delegated data models (`ComputedAttributeData`, `ExpressionRef`, `PhantomDetectionReport`) are importable from their source modules (the doc-linking / no-duplication claim is not tested) | `test_data_models.py` | PASS |
| REQ-DM-07 | Resolution-model field type annotations (`ComputationGraph`, `PipelineModule`, `ModuleInput`, `ParameterGroup`) match the documented containment hierarchy from doc 09 (no data-flow diagram is checked) | `test_data_models.py` | PASS |
| REQ-DM-08 | The typed-registry **enforced surface** SHALL use NewType wrappers: the wrappers in `identifier_types.py` are genuine `NewType`s over their bases, the four `OutputRegistry` registry dicts are annotated `dict[NewType, NewType]`, and `make_scoped_key`/`make_canonical_channel` return their NewType. (The `resolution/models.py` field annotations remain bare `str` by design — documented in 09-data-models.md and filed `[DM08-MODEL-FIELD-TYPING]`; `register_alias`'s `\| str` unions are a designed boundary, not drift) | `test_dm08_enforced_surface.py` (AST-scan — PEP-526 `self.x` annotations never reach `__annotations__`) | PASS |
| REQ-DM-09 | `ComputationGraph.output_aliases: list[OutputAlias]` SHALL be a serialized field (no `exclude`, contrast `fallback_entry_points`) carrying each EXPOSE_PURE modeler name, its canonical channel (validated to exist — INV-3), instance path, and `shape`; stable-sorted by `(instance_path, alias_name)` (INV-5) so regen yields no ordering-only diff | `test_data_models.py`, `test_exact_route_alias_aggregation.py::test_the_aggregation_and_its_chain_alias_both_reach_a_consumer` | PASS |

### DIAG

**Diagnostic Severity** — [reference/30-diagnostic-severity.md](reference/30-diagnostic-severity.md)

Filed 2026-08-14 by CONSTRAINT-SEMANTICS Item 7 (`[MATRIX-EPIC-SURFACE-ROWS]`, BACKLOG:447). These
four requirements were traced in doc 30 and had **no rows here** — the family existed in prose and
not in the matrix. Every cited test was run before its row was written; the run is recorded in
`.project/completed/20260814_constraint-docs-agent-sync/verification.md`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-DIAG-01 | A diagnostic's severity is fixed at construction from the writer table and never recomputed by a reader-side `kind → severity` lookup | `test_upstream_pins.py` (pins the upstream schema string; the construction rule itself lives in `agentic-mbse constraint_facts.py:78-95,230-233`) | PARTIAL *(the kept codegen test pins the pinned-upstream contract, not the no-reader-side-table property. That property is proved by absence — no reader-side mapping exists in `src/` — which no codegen test asserts. A reader-side table reintroduced upstream would not fail this row's test.)* |
| REQ-DIAG-02 | A blocking diagnostic halts generation before lowering, on both the live and snapshot routes, naming every blocking diagnostic | `test_extraction_diagnostic_screen.py` | PASS |
| REQ-DIAG-03 | An advisory diagnostic is rendered and generation continues; advisory rendering cannot swallow the blocking halt | `test_extraction_diagnostic_screen.py` | PASS |
| REQ-DIAG-04 | Severity skew fails closed in both directions | — *(discharged by construction — no **diagnostic** severity crosses a process boundary on disk; the v6 envelope carries no diagnostic `severity` field and `constraint_facts.parse` has no caller in `src/` or `tests/`. Corrected at Item 7's audit, 2026-08-14: the envelope *does* carry a **disposition** `severity` — `snapshot/instance_graph.py:724,759,803` — which is a different field with a different writer and is not what this row is about)* | UNTESTED *(the failure mode is impossible rather than guarded here, so there is nothing to assert. Recorded as UNTESTED rather than PASS because no kept test would fail if the v6 envelope started carrying diagnostic severity again.)* |

### DRA

**Dual Resolution Architecture** — Component X02 — [reference/24-dual-resolution-architecture.md](reference/24-dual-resolution-architecture.md)

**Status (historical).** This family described the two-path resolution architecture and the shared `resolve_producer()` table both paths called. `resolution/producer_resolution.py`, the backtracker, and the aggregation factory are all deleted, so the architecture the rows contrast no longer has two sides. On the shipped route references resolve once, against occurrence identity, in the elaborator. The `REQ-PR-*` family the lifecycle item filed for the shared table was never written and now has no subject.

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_exact_projection_aggregation.py`, `test_exact_pipeline_context.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-DRA-01 | CalcUsage resolution SHALL happen during backtracker DFS; the DFS decision (recurse vs st... | — *(subject deleted — ledger L-101)* | RETIRED |
| REQ-DRA-02 | Positive resolution runs through the one shared `resolve_producer()` table for calc bindings, constraint actuals, and aggregation terms (via `_build_agg_input_source()`, `graph_builder.py`); FORMULA uses the pre-computed attribute resolution map | — *(subject deleted — ledger L-239 / L-126)* | RETIRED |
| REQ-DRA-03 | Both paths SHALL use typed registries (10-output-registry): `scoped_lookup(ScopedKey)` fo... | — *(subject deleted — ledger L-101 / L-126)* | RETIRED |
| REQ-DRA-04 | Both paths SHALL produce the same wiring for the same reference. A binding `"cost_model.t... | — *(subject deleted — ledger L-126 / L-239)* | RETIRED |
| REQ-DRA-05 | The backtracker SHALL produce `BindingResolution` objects; the aggregation factory SHALL produc... | — *(subject deleted — ledger L-126)* | RETIRED |

### EC

**Expression Compiler** — Component C04 — [reference/14-expression-compiler.md](reference/14-expression-compiler.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-EC-01 | `FeatureChainExpression` SHALL be checked BEFORE `OperatorExpression` (FCE is OE subtype ... | `test_expression_compiler.py` | PASS |
| REQ-EC-02 | N-ary operands SHALL be left-folded into nested binary operations | `test_expression_compiler.py` | PASS |
| REQ-EC-03 | Unit annotations (`[` operator) SHALL be stripped; only the value operand is retained | `test_expression_compiler.py` | PASS |
| REQ-EC-04 | Every compiled expression SHALL be validated via `python_ast.parse(result, mode="eval")` | `test_expression_compiler.py` | PASS |
| REQ-EC-05 | Cycle detection in dependency graph SHALL mark ALL outputs as `MANUAL_REQUIRED` | `test_expression_compiler.py` | PASS |
| REQ-EC-06 | `classify_compilability()` SHALL use worst-case roll-up semantics | `test_expression_compiler.py` | PASS |
| REQ-EC-07 | Undeclared intermediates SHALL be discovered iteratively from `member_expressions` | `test_expression_compiler.py` | PASS |

### EPC

**Entry Point Classification** — Component C17 — [reference/06-entry-point-classifier.md](reference/06-entry-point-classifier.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-EPC-01 | Every entry point SHALL be classified as exactly one EntryPointType: {`DESIGN_ATTRIBUTE`,... | `test_exact_pipeline_context.py::test_the_live_and_v6_contexts_agree_on_the_public_entry_point_surface`, `test_exact_projection_aggregation.py::test_every_member_occurrence_is_its_own_entry_point` | PARTIAL *(audit-7 F2: the heirs prove route parity and per-occurrence minting, not that every entry point lands in exactly one of the three types; a misclassified-but-route-consistent type would not fail them)* |
| REQ-EPC-02 | Classification SHALL follow strict precedence: `DESIGN_ATTRIBUTE` > `LIBRARY_DEFAULT` > `... | — *(subject deleted — ledger L-131)* | RETIRED |
| REQ-EPC-03 | `default_value` SHALL be converted to `float` at classification time; if conversion fails... | — *(subject deleted — ledger L-131)* | RETIRED |
| REQ-EPC-04 | Every classified entry point SHALL be assigned a `param_group` via ParameterGroupDeriver.... | — *(subject deleted — ledger L-131)* | RETIRED |
| REQ-EPC-05 | Every entry point SHALL belong to exactly one ParameterGroup. Orphans SHALL land in a `"s... | — *(subject deleted — ledger L-131)* | RETIRED |
| REQ-EPC-06 | After FORMULA and aggregation module construction, parameter groups SHALL be rebuilt from... | — *(subject deleted — ledger L-131)* | RETIRED |
| REQ-EPC-07 | `_classify_entry_points()` SHALL be a pure function: input data in, `dict[str, EntryPoint... | — *(subject deleted — ledger L-131)* | RETIRED |
| REQ-EPC-08 | Entry points created by FORMULA and aggregation factories SHALL have `entry_type=DESIGN_A... | — *(subject deleted — ledger L-131)* | RETIRED |

### EXT

**Extraction** — Component C03 — [reference/01-extraction.md](reference/01-extraction.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-EXT-01 | Extraction SHALL produce exactly one CalculationDefinitionData per `calc def` in the SysM... | `test_extractor.py` | PASS |
| REQ-EXT-02 | Every parameter binding on a CalcUsageData SHALL have exactly one BindingType from {CHAIN... | `test_extractor.py` | PASS |
| REQ-EXT-03 | Every `:>>` redefinition SHALL be classified as exactly one RedefinitionType from {LITERA... | `test_extractor.py` | PASS |
| REQ-EXT-04 | Every aggregation expression SHALL be decomposed into typed terms: SumTerm, SingletonTerm... | `test_extractor.py` | PASS |
| REQ-EXT-05 | Template calc usages (`is_template=True`) SHALL produce one virtual CalcUsageData per Par... | `test_extractor.py` | PASS |
| REQ-EXT-06 | Extraction SHALL NOT import from `analysis/`, `resolution/`, or `generation/`. | `test_extractor.py` | PASS |
| REQ-EXT-07 | The `CalculationDefinitionData.output_expression_asts` field SHALL exist as `dict[str, Any]` and be nullified at the snapshot serialization boundary (raw-AST content is exercised via REQ-EXT-10's live-extraction population check, not here) | `test_extractor.py` | PASS |
| REQ-EXT-08 | A `calc def` extracting with zero output attributes SHALL raise `ValueError` at extraction (V7), never reaching generation | `test_extractor.py` | PASS |
| REQ-EXT-09 | Every `ConstraintUsage` (calc-def, part-def, part-usage, package, and requirement-def owners) SHALL be a member of the constraint usage domain and carry exactly one disposition, with nothing silently absent (CONSTRAINT-SEMANTICS Item 2 re-anchor; the `collect_constraint_manifest` sweep this row previously named is retired) | `test_constraint_population_oracle.py` (reviewed expected-population file per constraint-bearing fixture, asserted by identity list; missing file fails by name), `test_constraint_usage_domain_totality.py::test_catf_mfe_d5_authored_population_is_total` | PASS |
| REQ-EXT-10 | A direction-carrying `ReferenceUsage` member (named `return`, bare `in`) SHALL extract as a parameter; a named inline `return y : Real = expr` SHALL auto-implement | `test_return_style_extraction.py` | PASS |
| REQ-EXT-11 | A calc def with an anonymous `return` (empty `declared_name`) SHALL raise the V8 diagnostic before V7 | `test_return_style_extraction.py` | PASS |
| REQ-EXT-12 | The `return attribute y; y = expr` form SHALL extract `y` once with no double-ingestion (direction-None body ref excluded) | `test_return_style_extraction.py` | PASS |
| REQ-EXT-13 | `_build_part_usage_index` SHALL index each PartUsage under all its owned FeatureTyping targets and every user-model PartDef in `usage.types` (user-filtered), never by list position | `test_type_indexing.py` | PASS |
| REQ-EXT-14 | Same-named templates from a retyped usage's super/subtype (same virtual QN) SHALL keep the most-specific owner + emit V9; differently-named templates SHALL both instantiate (the collision warning fires only for same-named clashes) | `test_type_indexing.py` | PASS |

### GA

**Graph Assembly** — Component C18 — [reference/07-graph-assembly.md](reference/07-graph-assembly.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-GA-01 | `execution_order` SHALL be a valid topological sort: no module reads from a module that e... | `test_elaboration_projection.py::test_projection_is_topological_and_every_input_is_covered` | PASS |
| REQ-GA-02 | If a cycle exists, `_unified_topological_sort` SHALL raise `CircularDependencyError` list... | — *(subject deleted — ledger L-152)* | RETIRED |
| REQ-GA-03 | Every `module_output` `producer_channel` SHALL resolve to a declared output channel. | `test_elaboration_projection_one_way.py::test_graph_validation_rejects_missing_occurrence_and_typed_producer_cycle` | PARTIAL *(audit-7 F2: the cited arms exercise a missing occurrence and a typed producer cycle, not an unresolvable producer channel; the specific violation this row names has no failing arm)* |
| REQ-GA-04 | A module SHALL NOT depend on itself, even if its own output channel name appears in its i... | `test_elaboration_projection_one_way.py::test_graph_validation_rejects_missing_occurrence_and_typed_producer_cycle` | PASS |
| REQ-GA-05 | The returned `ComputationGraph` SHALL contain exactly the reviewed field set: sorted `modules`, `entry_point_groups`, `execution_order`, in-memory `fallback_entry_points` (REQ-GA-08), serialized `output_aliases` (REQ-DM-09); any field-set change is a deliberate reviewed rev (the exact-set test flips red) | — *(the exact-field-set pin retired with `test_graph_assembly.py` (ledger L-152) and has no recorded replacement; no kept node asserts the `ComputationGraph` field set)* | UNTESTED |
| REQ-GA-06 | `execution_order` list SHALL equal `[m.name for m in modules]` (names match module orderi... | `test_exact_target_selection.py::test_selection_renumbers_execution_order_without_gaps` | PASS |
| REQ-GA-07 | Static: `_unified_topological_sort` source uses `deque`, `popleft()`, and Kahn-pattern identifiers (`in_degree`, `successors`); O(V + E) complexity is asserted structurally, not measured | — *(subject deleted — ledger L-152)* | RETIRED |
| REQ-GA-08 | A two-layer params-coverage check SHALL exist: a pure collector `collect_uncovered_params(graph)` returning the wired fell-through-valueless violations (sibling to REQ-GA-03), and an always-strict generation boundary raising V11 on any violation. `ComputationGraph.fallback_entry_points` (in-memory, `exclude=True`) feeds it | `test_uncovered_params.py`, `test_data_models.py` | PASS |

### GEN

**Generation** — Component C21 — [reference/08-generation.md](reference/08-generation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-GEN-01 | Pipeline YAML generation SHALL consume only `ComputationGraph` -- no extraction models. | `test_generation_boundary.py` | PASS |
| REQ-GEN-02 | Every CalcUsage `PipelineModule` renders non-empty wrapper code in memory (no filesystem or exactly-one-file check; FORMULA/aggregation modules excluded) | `test_elaboration_generation_boundary.py::test_exact_projection_renders_real_pipeline_and_registry`, `test_exact_route_generated_package.py::test_both_routes_generate_the_same_package_files` | PASS |
| REQ-GEN-03 | Multi-output modules (2+ outputs) SHALL get a `MultiOutput` schema in `schemas/`; single-... | — *(the MultiOutput-vs-single-output schema rule retired with `test_gen_schemas.py` (ledger L-149, no recorded replacement); the rendered shape survives only inside the byte-identical package comparison)* | UNTESTED |
| REQ-GEN-04 | FULLY_COMPILABLE calc defs SHALL produce auto-implemented stencils; all others SHALL prod... | `test_generation_boundary.py`, `tests/unit/test_stencils.py` | PASS |
| REQ-GEN-05 | Each ParameterGroup SHALL produce one JSON template (`inputs/`) and one Pydantic schema (... | `test_exact_group_identity.py`, `test_generated_schema_importable.py::test_each_params_schema_imports_and_validates_its_own_json` | PASS |
| REQ-GEN-06 | SysML type mapping (`Real`->`float`, `Integer`->`int`, `Boolean`->`bool`, `String`->`str`... | `test_type_mapping_consolidation.py` | PASS |
| REQ-GEN-07 | Every generated module SHALL be registered in `__init__.py` for TEAx framework discovery. | `test_exact_route_registry.py::test_the_registry_covers_every_module_the_graph_projected` | PASS |

### HR

**Hierarchy Resolver** — Component C06 — [reference/25-hierarchy-resolver.md](reference/25-hierarchy-resolver.md)

**Where this family stands after the retirement.** The component these rows describe,
`extraction/hierarchy_resolver.py`, is in the tree but **off the shipped route** — nothing in
`src/` imports it. It is retained because `tests/helpers/live_extraction.py` (the evidence
source six conformance modules read) depends on it (disposition and reason recorded in the
module docstring, REVISE step 6d). So a PASS here certifies component correctness, not
shipped-route coverage; the shipped route lifts aggregation in the elaborator, whose evidence
the GA and elaboration families carry. (Added at audit-7 finding F1 — this family previously
read as shipped coverage with no disclosure, unlike its CA sibling.)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-HR-01 | Every `:>>` redefinition SHALL be classified as exactly one RedefinitionType from {LITERA... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-02 | Both `FeatureChainExpression` and `FeatureReferenceExpression` value expressions SHALL pr... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-03 | Deep-path redefinitions SHALL set `is_deep_path=True` and populate `target_path` from `ch... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-04 | Multiplicity extraction SHALL use `cached_lower_bound` (not `cached_upper_bound`) due to ... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-05 | `_walk_aggregation_ast()` SHALL check `FeatureChainExpression` BEFORE `OperatorExpression... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-06 | `sum(child.attr)` SHALL be transformed to `(count_attr * child.attr)` using the `mult_loo... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-07 | CHAIN-type sibling redefinitions that reference the aggregation attribute SHALL be added ... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-08 | `extract_design_overrides()` SHALL scan `:>>` overrides on plain part usages (not only `part redefines`), keeping a newly-scanned plain-usage override only when its RHS is LITERAL; `part redefines` keeps all RHS types | `test_uncovered_params.py` | PASS |

### IR

**Input Resolver** — Component C12 — [reference/04-producer-resolution.md](reference/04-producer-resolution.md)

**Status (historical).** The lifecycle item re-projected this family onto the shared `resolve_producer()` table the standalone input resolver had become. That table is now deleted too (`resolution/producer_resolution.py`), so the rows below describe a resolution mechanism the product no longer has. The shipped route resolves a reference once, at elaboration, against occurrence identity — there is no key-form table, no tier order, and no lenient mint. The `REQ-PR-*` family filed for the shared table was never written and has no subject.

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_elaboration_identity_collisions.py`, `test_elaboration_fail_closed.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-IR-01 | `resolve_producer()` under LENIENT SHALL never raise — a terminal miss mints an ENTRY_POINT; under STRICT a terminal miss raises `CodeGenerationError` (INV-2). | — *(subject deleted — ledger L-239)* | RETIRED |
| REQ-IR-02 | `KEY_FORMS` SHALL execute in declared table order, tier 1 before tier 2; the first admissible hit wins. | — *(subject deleted — ledger L-239)* | RETIRED |
| REQ-IR-03 | The self-reference guard SHALL reject a channel whose producing-module EQN matches `consumer_eqn`, at every tier-1 hit, skipping the candidate and continuing the table. | — *(subject deleted — ledger L-239)* | RETIRED |
| REQ-IR-04 | `ProducerContext` SHALL be immutable (`frozen=True`); no key form mutates it. | — *(subject deleted — ledger L-239)* | RETIRED |
| REQ-IR-05 | `KEY_FORMS` SHALL declare each form's tier and `lenient_only` flag as data; name-based forms SHALL be inadmissible under STRICT (`_admissible`). | — *(subject deleted — ledger L-239)* | RETIRED |
| REQ-IR-06 | A LENIENT terminal miss SHALL mint an entry point with QN `{consumer_eqn}__{param_name-or-flattened-reference}` (`entry_point_qualified_name`, D9). | — *(subject deleted — ledger L-238)* | RETIRED |
| REQ-IR-07 | The same reference SHALL resolve to the same channel across consumers (one shared table); two consumers of one design attribute converge on one producer. | — *(subject deleted — ledger L-172 / L-126)* | RETIRED |

> **Contract disposition — REQ-IR-01: `PARTIAL`** (SOURCE-IDENTITY Item 3). The STRICT
> terminal-miss raise clause `stands`. The LENIENT unconditional-mint clause is `SUPERSEDED` for
> bound model references (contract D-17; Appendix B lenient-mint row); minting survives only
> under the explicit external-input contract.

> **Contract disposition — REQ-IR-06: `SUPERSEDED`** (SOURCE-IDENTITY Item 3). Minting an entry
> point for a bound model reference is impermissible (contract D-17; Appendix B row "A bound
> model reference that fails resolution may lenient-mint a per-consumer entry point"). The
> QN-format clause survives only for the explicit external-input contract.

> **Contract disposition — REQ-IR-07: `PARTIAL`** (SOURCE-IDENTITY Item 3). The
> one-shared-table clause `stands`; the two-consumer convergence clause `stands`. The reading
> that this route-specific evidence certifies convergence generally is `SUPERSEDED` (Appendix B
> row "Route-specific convergence evidence certifies source convergence generally"; cells C2,
> C4, C11–C15, C24, and C25 own the acceptance).

### LVP

**Literal Value Propagation** — Component C16 — [reference/18-literal-value-propagation.md](reference/18-literal-value-propagation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-LVP-01 | `_find_literal_redefinition()` SHALL try type-aware resolution (Strategy 1) before name-b... | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-LVP-02 | SumTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution fails | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-LVP-03 | SingletonTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution ... | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-LVP-04 | LocalTerms SHALL NOT use literal redefinition lookup (different resolution path) | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-LVP-05 | Entry point default backfill SHALL replace `None` defaults with literal values discovered... | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-LVP-06 | `usage_type_map` SHALL be threaded from `HierarchyExtractionResult` through `build_comput... | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-LVP-08 | `usage_type_map` SHALL resolve each `(owning_qn, usage_name)` to the most-specific owned FeatureTyping target (not `next(iter(member.types))`); incomparable multi-typings resolve sorted-first with V10 | `test_type_indexing.py` | PASS |
| REQ-LVP-09 | `_index_usage_level_retypes` SHALL index usage-level retypes of inherited part usages (`part hif_plant : Base { part :>> driver : Subtype }`) into `usage_type_map` keyed by the CONTAINER usage's instance QN, limited to GENUINE retypes (a `:>>` redefinition whose most-specific owned type differs from the base def's declared type for that member) so value-only `:>>` overrides are excluded and non-two-level snapshots stay byte-identical (REQ-HR-09 released) | — *(subject deleted — ledger L-184)* | RETIRED |
| REQ-LVP-07 | Literal default found SHALL keep module `FULLY_COMPILABLE`; no default SHALL set `MANUAL_... | — *(subject deleted — ledger L-136)* | RETIRED |

### MF

**Module Factory** — Component C14 — [reference/05-module-factory.md](reference/05-module-factory.md)

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_elaboration_projection.py`, `test_exact_route_generated_package.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-MF-01 | All three factory functions SHALL be pure data transformers: return `(PipelineModule, dic... | — *(subject deleted — ledger L-136 / L-137 / L-138 / L-139)* | RETIRED |
| REQ-MF-02 | CalcUsage factory SHALL fail-fast (`ValueError`) on missing `binding_resolutions` key -- ... | — *(subject deleted — ledger L-137)* | RETIRED |
| REQ-MF-03 | FORMULA factory SHALL set `module_kind=ModuleKind.FORMULA` and `compilability=FULLY_COMPILABL... | — *(subject deleted — ledger L-138)* | RETIRED |
| REQ-MF-04 | Aggregation factory SHALL handle all three extraction term types: SumTerm, SingletonTerm,... | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-MF-05 | Every ModuleInput SHALL have exactly one InputSource with `source_type` in {`module_outpu... | — *(subject deleted — ledger L-136 / L-137 / L-138)* | RETIRED |
| REQ-MF-06 | SumTerm and SingletonTerm LITERAL fallback SHALL use `_find_literal_redefinition()` to pr... | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-MF-07 | LocalTerm resolution SHALL try: (1) sibling aggregation output, (2) EXPOSE_PURE alias, (3... | — *(subject deleted — ledger L-136)* | RETIRED |
| REQ-MF-08 | Single-output modules SHALL use `field_name="root"`; multi-output SHALL use attribute nam... | — *(subject deleted — ledger L-137)* | RETIRED |
| REQ-MF-09 | The aggregation compile step SHALL substitute each symbolic ref with its `inputs.X` form on whole-token boundaries (`re.sub(r"\bref\b", …)`), never a plain substring `.replace()` — a ref that is a substring of another (`cost`/`cost_total`) SHALL NOT corrupt to `inputs.inputs.cost_total`; disjoint refs compile byte-identically (TRUTH-DEBT Item 6, Site 2) | — *(subject deleted — ledger L-226)* | RETIRED |

### NC

**Naming Conventions** — Component C02 — [reference/15-naming-conventions.md](reference/15-naming-conventions.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-NC-01 | EQN SHALL be constructed by joining sanitized owner-chain segments with `__` | `test_naming_conventions.py` | PASS |
| REQ-NC-02 | PQN SHALL extend an EQN with `__{param_name}` | `test_naming_conventions.py` | PASS |
| REQ-NC-03 | Module name SHALL equal the EQN lowercased | `test_naming_conventions.py` | PASS |
| REQ-NC-04 | Module type SHALL use `{namespace}.{ElementName}Module` format | `test_naming_conventions.py` | PASS |
| REQ-NC-05 | Channel names SHALL be PQNs — no separate channel concept exists | `test_naming_conventions.py` | PASS |
| REQ-NC-06 | `sanitize_name()` SHALL apply 6 transforms in order: strip quotes, spaces→`_`, non-alnum→... | `test_naming_conventions.py` | PASS |
| REQ-NC-07 | Registry keys SHALL use typed wrappers: scoped and alias registries use `ScopedKey` (dott... | `test_naming_conventions.py` | PASS |
| REQ-NC-08 | Identifier derivation SHALL sanitize each qualified-name segment before it becomes a class name, module file path, or FORMULA module_eqn/channel | `test_exact_route_alias_aggregation.py::test_every_derived_identifier_is_quote_and_space_free`, `test_elaboration_identity_collisions.py::test_output_and_expression_keys_do_not_collapse_on_rendered_name` | PASS |
| REQ-NC-09 | Generation SHALL fail fast when two distinct SysML names sanitize to one output path, naming both source names and the shared path | `test_duplicate_path_failfast.py` | PASS |

### OR

**Output Registry** — Component C08 — [reference/10-output-registry.md](reference/10-output-registry.md)

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_elaboration_identity_collisions.py`, `test_exact_route_registry.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-OR-01 | Registry SHALL map every reference format (FCE dotted path, FRE qualified name, redefinit... | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-02 | Each typed registry SHALL have its own exact-match lookup method — no single `resolve()` ... | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-03 | Collision policy: scoped and SysML QN registries SHALL raise on duplicate (unique by cons... | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-04 | `register_alias()` SHALL enforce phase ordering — target must already be in `_canonical` | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-05 | Phase 1 SHALL register: Key_C as `ScopedKey` and Key_A as a guarded first-wins alias (`register_alias`) per CalcUsage output (Phase 1a); Key_E_stripped scoped for aggregation (Phase 1b); Key_F scoped for FORMULA REFERENCE-secondary (Phase 1c). The ambiguous Key_A format is kept out of the scoped registry — it exists only as a phase-order-guarded alias (target must be in `_canonical`, REQ-OR-04) | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-06 | Phase 2-4 aliases SHALL resolve their canonical target through typed **resolution-time** lookup (`scoped_lookup`/`alias_lookup`) before registering. The construction-time `instance_attr_to_channel` Key_A dict is a build-time helper that feeds only guarded `register_alias` calls — it registers nothing itself | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-07 | Key_C SHALL be constructed via `make_scoped_key()` — strip design prefix from EQN, join w... | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-08 | Key_A SHALL NOT be registered as a scoped key — the ambiguous format is kept out of the scoped registry (Key_C is its scoped form). Key_A IS registered as a guarded first-wins alias (Phase 1a `register_alias`), reachable via `alias_lookup` for cross-scope CHAIN resolution | — *(subject deleted — ledger L-159 / L-232)* | RETIRED |
| REQ-OR-09 | The FORMULA sysml-QN key SHALL be registered per-segment sanitized (`sanitize_qualified_name`), and the per-collision alias line SHALL be DEBUG with one WARNING count-summary at build (Item 7 / D5, lockstep site 1) | — *(subject deleted — ledger L-159 / L-233 / L-251)* | RETIRED |

### ORCH

**Orchestration** — Component C19 — [reference/02-orchestration.md](reference/02-orchestration.md)

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_exact_pipeline_context.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-ORCH-01 | `build_pipeline_context()` SHALL execute steps in strict dependency order: 3.5 before 4, ... | — *(subject deleted — ledger L-158)* | RETIRED |
| REQ-ORCH-02 | Step 3.5 SHALL rewrite virtual bindings in-place before any downstream step reads `calc_u... | — *(subject deleted — ledger L-158)* | RETIRED |
| REQ-ORCH-03 | Step 4.5 SHALL remove FORMULA-classified computed attributes from `design_attrs` before P... | — *(subject deleted — ledger L-158)* | RETIRED |
| REQ-ORCH-04 | OutputRegistry SHALL register outputs in strict phase order: 1a/1b/1c (canonical) then 2/... | — *(subject deleted — ledger L-158)* | RETIRED |
| REQ-ORCH-05 | Each aggregation expression SHALL be scoped to its concrete design instance path(s) via v... | — *(subject deleted — ledger L-158)* | RETIRED |
| REQ-ORCH-06 | `build_pipeline_context()` SHALL return a PipelineContext where `computation_graph` is th... | — *(subject deleted — ledger L-158)* | RETIRED |
| REQ-ORCH-07 | CHAIN alias canonical names SHALL resolve to Phase 1 channels. Unresolvable aliases produ... | — *(subject deleted — ledger L-158)* | RETIRED |

### OSR

**Output Schema Rules** — Component C22 — [reference/22-output-schema-rules.md](reference/22-output-schema-rules.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-OSR-01 | Single-output modules SHALL use `RootModel[float]` with `field_name="root"` | `tests/integration/test_full_pipeline_exact_route.py`, `tests/unit/test_computed_attr_generation.py` | PASS |
| REQ-OSR-02 | Multi-output modules (2+ outputs) SHALL generate a named `MultiOutput` subclass | — *(the MultiOutput subclass rule retired with `test_gen_schemas.py` (ledger L-149, no recorded replacement))* | UNTESTED |
| REQ-OSR-03 | Generated MultiOutput schema field names SHALL match `PipelineModule.outputs[i].field_name` (template-fidelity; both sides are drawn from the same graph, not independently verified against the original SysML `output_attributes` names) | — *(the field-name fidelity check retired with `test_gen_schemas.py` (ledger L-149, no recorded replacement))* | UNTESTED |
| REQ-OSR-04 | SysML types SHALL map to Python types per the type mapping table | `test_type_mapping_consolidation.py` | PASS |
| REQ-OSR-05 | Output fields on `MultiOutput` MUST NOT have `default=...` values | — *(the no-defaults check retired with `test_gen_schemas.py` (ledger L-149, no recorded replacement))* | UNTESTED |
| REQ-OSR-06 | Aggregation and computed-attribute modules SHALL always be single-output (`"root"`) | `tests/unit/test_computed_attr_generation.py`, `tests/unit/test_aggregation_generation.py` | PASS |
| REQ-OSR-07 | Output channels SHALL use PQN format via `get_channel_name()` | `test_naming_conventions.py`, `test_elaboration_identity_collisions.py::test_output_and_expression_keys_do_not_collapse_on_rendered_name` | PASS |

### PGD

**Parameter Group Deriver** — Component C13 — [reference/17-parameter-group-deriver.md](reference/17-parameter-group-deriver.md)

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_exact_group_identity.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PGD-01 | Every entry point SHALL be assigned to exactly one parameter group | — *(subject deleted — ledger L-160)* | RETIRED |
| REQ-PGD-02 | Four indexes SHALL be built with strict precedence: attr > binding > unbound > literal | — *(subject deleted — ledger L-160)* | RETIRED |
| REQ-PGD-03 | Grouping SHALL produce at least one group per source file with literal-default design attributes (not exactly one group per file -- a file whose attributes are all non-literal-default produces zero groups, and unbound-param-derived groups may merge into an existing group by name rather than adding one per file) | — *(subject deleted — ledger L-160)* | RETIRED |
| REQ-PGD-04 | `derive_groups_filtered()` SHALL remove parameters not in `backtracking_result.entry_poin... | — *(subject deleted — ledger L-160)* | RETIRED |
| REQ-PGD-05 | `classify()` SHALL check indexes in precedence order and return group name or `None` | — *(subject deleted — ledger L-160)* | RETIRED |
| REQ-PGD-06 | The deriver SHALL resolve each entry point's numeric default inline from its owning index (attr / binding / unbound / literal) via `_parse_default_value` in `_derive_from_*` | — *(subject deleted — ledger L-160)* | RETIRED |
| REQ-PGD-07 | Group names SHALL follow `{snake_case_stem}_params` / `{PascalCaseStem}Params` convention | — *(subject deleted — ledger L-160)* | RETIRED |
| REQ-PGD-08 | No deriver change is required for def-owned design-attribute matching (D1): once the backtracker (REQ-BT-10) returns the design-attr QN, the deriver's `_attr_index`-keyed classification and inline default resolution handle grouping and default automatically | — *(subject deleted — ledger L-160)* | RETIRED |

> **Contract disposition — REQ-PGD-06: `SUPERSEDED`** (SOURCE-IDENTITY Item 3). Inline default
> resolution at group derivation is the parameter-group value backfill — a superseded fourth
> value authority (contract D-18; Appendix B row "The parameter-group deriver's default backfill
> is a benign value repair"); it derives from the single identity authority or is deleted
> (Item 5). Status is now RETIRED: the deriver itself was deleted (ledger L-160), so the row records a removed mechanism rather than an untested live one.

### PIPE

**Pipeline** — Component C19 — [reference/00-pipeline-overview.md](reference/00-pipeline-overview.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PIPE-01 | The pipeline SHALL produce exactly one ComputationGraph from a set of SysML model files. | `test_elaboration_projection.py::test_projection_is_topological_and_every_input_is_covered`, `test_exact_route_generated_package.py::test_both_routes_generate_the_same_package_files` | PASS |
| REQ-PIPE-02 | Every ModuleInput SHALL be wired to exactly one source: `module_output` or `entry_point`. | `test_elaboration_projection.py::test_projection_is_topological_and_every_input_is_covered` | PASS |
| REQ-PIPE-03 | Every `module_output` reference SHALL resolve to a canonical channel in the OutputRegistr... | `test_elaboration_projection_one_way.py::test_graph_validation_rejects_missing_occurrence_and_typed_producer_cycle` — the clause "in the OutputRegistry" names deleted code; the projector's channel claim is the live equivalent | PASS |
| REQ-PIPE-04 | `execution_order` SHALL be a valid topological sort -- no module reads from a module that... | `test_elaboration_projection.py::test_projection_is_topological_and_every_input_is_covered` | PASS |
| REQ-PIPE-05 | Every EntryPoint SHALL be classified as exactly one of {`LIBRARY_DEFAULT`, `DESIGN_ATTRIB... | `test_exact_pipeline_context.py::test_the_live_and_v6_contexts_agree_on_the_public_entry_point_surface` | PASS |
| REQ-PIPE-06 | The graph SHALL tag each module with its `module_kind`; a calc-bearing model includes `CALCULATION`, `FORMULA`, and `AGGREGATION` modules (the `CONSTRAINT` / `REPORT_AGGREGATOR` families appear when constraints are lowered) | `test_elaboration_projection.py::test_projection_covers_every_live_module_kind`, `test_module_kind_faildloud.py` | PASS |
| REQ-PIPE-07 | Generation SHALL produce output exclusively from `ComputationGraph` -- no back-references... | `test_generation_boundary.py`, `test_elaboration_generation_boundary.py::test_exact_projection_renders_real_pipeline_and_registry` | PASS |

### PMM

**PipelineModule Migration** — Component C26 — [reference/26-pipeline-module-migration.md](reference/26-pipeline-module-migration.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PMM-01 | `PipelineModule` SHALL carry all metadata needed by module wrapper generation (calc def n... | `test_elaboration_generation_boundary.py::test_exact_projection_renders_real_pipeline_and_registry`, `test_exact_route_registry.py::test_the_registry_covers_every_module_the_graph_projected` | PASS |
| REQ-PMM-02 | `ModuleInput` and `ModuleOutput` SHALL carry `description` and `default_value` fields for... | `test_elaboration_generation_boundary.py::test_exact_projection_renders_real_pipeline_and_registry`, `test_exact_route_registry.py::test_the_registry_covers_every_module_the_graph_projected` | PASS |
| REQ-PMM-03 | `PipelineModule` SHALL carry `calc_expressions` for stencil comment generation. | `test_elaboration_generation_boundary.py::test_exact_projection_renders_real_pipeline_and_registry`, `test_exact_route_registry.py::test_the_registry_covers_every_module_the_graph_projected` | PASS |
| REQ-PMM-04 | Every generated module SHALL remain valid, non-empty Python after the field migration (the one-time byte-identity-vs-pre-migration-baseline gate ran once at cutover and is not re-asserted here) | `test_exact_route_alias_aggregation.py::test_every_generated_file_parses` | PASS |
| REQ-PMM-05 | Migrated modules SHALL be importable in all variants with fields unchanged (the phased-sequence claim -- add/create/deprecate/remove -- is a one-time process record, not a testable module property) | — *(subject deleted — ledger L-162)* | RETIRED |

### PY

**Pipeline YAML** — Component C20 — [reference/21-pipeline-yaml-generation.md](reference/21-pipeline-yaml-generation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PY-01 | No entry-point qualified name appears as a bare (unprefixed) source in pipeline-YAML module-input lines (the `param_group.` prefix string itself is not positively validated — blacklist coverage) | `test_public_route_baselines.py::test_the_public_route_writes_the_pipeline_yaml_the_capture_script_used_to` | PASS |
| REQ-PY-02 | `InputSource.param_group` SHALL NOT be None for any entry point in the ComputationGraph | `test_public_route_baselines.py::test_the_public_route_writes_the_pipeline_yaml_the_capture_script_used_to` | PASS |
| REQ-PY-03 | No pipeline-YAML module-input line declares type `"int"` (numeric-is-`"float"` verified as a blacklist, not positively; multiplicity counts not separately asserted) | `test_public_route_baselines.py::test_the_public_route_writes_the_pipeline_yaml_the_capture_script_used_to` | PASS |
| REQ-PY-04 | MODULE_OUTPUT sources with `field_name == "root"` SHALL append `.root` to the channel name | `tests/unit/test_exit_pin.py` | PASS |
| REQ-PY-05 | `ModuleOutput` channel_names are unique across the graph (a rebuilt `{channel: field}` dict has one entry per output); the generated YAML `channel_field_map` is not inspected; first 2 models only | `test_elaboration_identity_collisions.py::test_output_and_expression_keys_do_not_collapse_on_rendered_name` | PASS |
| REQ-PY-06 | Exit point type SHALL be `RootModel[T]` when `field_name == "root"`, else `T` | `tests/unit/test_exit_pin.py` | PASS |
| REQ-PY-07 | Entry point module inputs SHALL list one JSON file per `ParameterGroup` | `test_exact_group_identity.py`, `test_public_route_baselines.py::test_the_public_route_writes_the_pipeline_yaml_the_capture_script_used_to` | PASS |
| REQ-PY-08 | An aliased channel's exit line SHALL render the modeler's instance-qualified name as its output filename (`{instance_path}__{alias_name}.json`); the exit **key** stays the canonical channel and the type token is unchanged (REQ-PY-06 holds), so simkit's key-is-a-channel check still passes | `tests/unit/test_exit_point_aliases.py` | PASS |

### REG

**Module Registry** — Component C24 — [reference/20-module-registry-generation.md](reference/20-module-registry-generation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-REG-01 | Aggregation module import paths SHALL use design-scoped EQN (`module_eqn`), not library Q... | `test_exact_route_registry.py` | PASS |
| REQ-REG-02 | Import paths in registry SHALL match actual filesystem paths generated by CLI | `test_exact_route_registry.py::test_the_registry_covers_every_module_the_graph_projected` | PASS |
| REQ-REG-03 | Class names in `module_type_override` dict SHALL be globally unique | `test_exact_route_registry.py`, `tests/unit/test_sc11_recheck.py` | PASS |
| REQ-REG-04 | When class names collide, registry SHALL use aliased imports (`import X as Assembly_X`) | `tests/unit/test_registry_generation.py`, `tests/unit/test_sc11_recheck.py` | PASS |
| REQ-REG-05 | CalcUsage, computed attribute, and aggregation modules SHALL all derive paths from design... | `test_exact_route_registry.py` | PASS |
| REQ-REG-06 | `CUSTOM_SCHEMA_TYPES` SHALL include all exit point primitive types used by any module | `tests/unit/test_registry_generation.py` | PASS |
| REQ-REG-07 | Registry generation SHALL detect and report name collisions before rendering | `tests/unit/test_sc11_recheck.py` | PASS |
| REQ-REG-08 | After parent-segment aliasing, registry SHALL re-check class-name uniqueness and fail fast on any residual collision | `test_sc11_recheck.py` | PASS |
| REQ-REG-09 | `_collect_exit_point_primitive_types` SHALL warn (not silently skip) on a single-output (`field_name="root"`) exit point whose `python_type` is outside `{float,int,str,bool}` — notably `"Any"` (latent on the current corpus, reachable live via `extractor.py:492`; TRUTH-DEBT Item 6, Site 3) | `test_hygiene_tail_registry.py` | PASS |

### RES

**Resolution Overview** — Component — — [reference/03-resolution-overview.md](reference/03-resolution-overview.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-RES-01 | Every ModuleInput SHALL resolve to exactly one of {`module_output`, `entry_point`}. | `test_elaboration_projection.py::test_projection_is_topological_and_every_input_is_covered` | PASS |
| REQ-RES-02 | Positive resolution has one authority, `resolve_producer()` (04), called by the CalcUsage (during backtracker DFS, 11), constraint, and aggregation (`_build_agg_input_source()`, `graph_builder.py`) consumers; FORMULA uses the pre-computed attribute resolution map (16) | — *(subject deleted — ledger L-101 / L-104 / L-136)* | RETIRED |
| REQ-RES-03 | Factory functions SHALL return `(PipelineModule, dict[str, EntryPoint])` -- no mutation o... | — *(subject deleted — ledger L-139)* | RETIRED |
| REQ-RES-04 | Every `module_output` reference SHALL resolve to a canonical channel in the OutputRegistr... | `test_elaboration_projection_one_way.py::test_graph_validation_rejects_missing_occurrence_and_typed_producer_cycle` | PASS |
| REQ-RES-05 | The orchestrator SHALL be a linear sequence: classify -> build modules -> rebuild groups ... | — *(subject deleted — ledger L-158)* | RETIRED |
| REQ-RES-06 | `binding_resolutions` from the backtracker SHALL be the single source of truth for CalcUs... | — *(subject deleted — ledger L-137)* | RETIRED |
| REQ-RES-07 | Resolution of scope-relative references (CHAIN `source_path`) SHALL use the consumer's pa... | — *(subject deleted — ledger L-239)* | RETIRED |
| REQ-RES-08 | Consumer-scope application SHALL hold on each live resolution path, per that path's own mechanism: backtracker base leg (`_consumer_scope_dotted`, QN `segments[1:-1]`), backtracker ancestor-scope climb (Step CLIMB, 3+-segment chains), aggregation (`ResolutionContext.consumer_scope` from the module EQN, consumed by Strategy A's primary form), and FORMULA (owner-keyed resolution map — the owner IS the consumer; no dotted scope string). Per-path application over the enumerated paths, not an exhaustiveness proof | — *(subject deleted — ledger L-166)* | RETIRED |

### SNAP

**Extraction Snapshots** — Extraction Snapshots — [reference/27-snapshot-generation.md](reference/27-snapshot-generation.md)

> **These rows are the v5 extraction snapshot, and its code is gone.** REQ-SNAP-01..21 describe
> a format the product no longer produces or consumes; `generate --from-snapshot` takes a **v6
> instance-graph** snapshot and refuses a v5 document by name. The v5 loader, serializer and
> rebuild modules were deleted by the retirement, and so were the tests these rows cite —
> "current: 5" in REQ-SNAP-09 named the deleted loader's gate, never the product's snapshot
> version, and REQ-SNAP-16's `--design-path-filter` clause survives as a refusal but not as a
> flag (Gate 4B-G0 removed it, so argparse rejects it before a snapshot is opened). Read the
> whole family as history. The v6 envelope's evidence is
> `test_snapshot_v6_{envelope,capture,routes}.py` and `test_source_admission_routes.py`; a REQ
> family for it is unwritten and needs an owner.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-SNAP-01 | Snapshot files exist and deserialize without error | — *(subject deleted — ledger L-134)* | RETIRED |
| REQ-SNAP-02 | CalculationDefinitionData fields populated | — *(subject deleted — ledger L-134)* | RETIRED |
| REQ-SNAP-03 | CalcUsageData bindings have typed BindingType | — *(subject deleted — ledger L-134)* | RETIRED |
| REQ-SNAP-04 | HierarchyExtractionResult round-trips with tuple keys | — *(subject deleted — ledger L-134)* | RETIRED |
| REQ-SNAP-05 | AST fields are None (not serialized Java objects) | — *(subject deleted — ledger L-134)* | RETIRED |
| REQ-SNAP-06 | Path fields are Path instances, not strings | — *(subject deleted — ledger L-134)* | RETIRED |
| REQ-SNAP-07 | Enum fields are typed enum instances, not raw strings | — *(subject deleted — ledger L-134)* | RETIRED |
| REQ-SNAP-08 | Promoted snapshot helpers live only in `src`; no second copy (INV-3) | — *(subject deleted — ledger L-178)* | RETIRED |
| REQ-SNAP-09 | Missing/mismatched `snapshot_format_version` (current: 5) is a hard error before deserialization — no cross-version coexistence (INV-2, V1/V2) | — *(subject deleted — ledger L-178)* | RETIRED |
| REQ-SNAP-10 | Re-captured expression-bearing snapshot carries `compilation_results` (INV-5) | — *(subject deleted — ledger L-178)* | RETIRED |
| REQ-SNAP-11 | Version-current snapshot missing `compilation_results` degrades with a warning (V4) | — *(subject deleted — ledger L-178)* | RETIRED |
| REQ-SNAP-12 | Stale source hash warns; run continues (V3) | — *(subject deleted — ledger L-178)* | RETIRED |
| REQ-SNAP-13 | Snapshot context has null extractor/backtracker and still generates (INV-4/B1) | — *(subject deleted — ledger L-179)* | RETIRED |
| REQ-SNAP-14 | `generate --from-snapshot` completes with no license at runtime (INV-1) | — *(subject deleted — ledger L-179)* | RETIRED |
| REQ-SNAP-15 | No provenance/version text appears in a generated artifact (INV-6) | — *(subject deleted — ledger L-179)* | RETIRED |
| REQ-SNAP-16 | CLI accepts exactly one extraction input; rejects `--design-path-filter` + snapshot (INV-7/V6) | — *(subject deleted — ledger L-179)* | RETIRED |
| REQ-SNAP-17 | CalcUsage auto-implements from a snapshot (SC-10) | — *(subject deleted — ledger L-179)* | RETIRED |
| REQ-SNAP-18 | Regression guard: no production render site under `src/sysml_codegen` SHALL pass `generation_timestamp` -- the template that once carried it (`pydantic_schema.py.jinja2`) is deleted; the token still appears in the test itself, this row, and `.project/` history, so "the token exists nowhere in the repo" is not the claim | — *(subject deleted — ledger L-179)* | RETIRED |
| REQ-SNAP-19 | Live generation is byte-identical to snapshot generation, incl. symlinked models (license-gated; skips cleanly without a license, verified live during Item 2) | — *(subject deleted — ledger L-179)* | RETIRED |
| REQ-SNAP-20 | A missing load-bearing field on a deserialized dict is loud (V7): `python_type`/`binding_type`/`parent_part_path`/`owning_part_def_qn` warn and degrade to their defaults; `qualified_name` (keying) raises `SnapshotFormatError`; benign fields keep their `.get(default)` silently (TRUTH-DEBT Item 6, Site 1) | — *(subject deleted — ledger L-227)* | RETIRED |
| REQ-SNAP-21 | v5 referent shape gate: every real `source_file` in a loaded snapshot SHALL be a portable `root-N/<relpath>` referent — `_validate_source_referents` (`snapshot/loader.py:912`, called at `:837`) rejects an absolute, snapshot-dir-relative, or blank/missing value with `SnapshotFormatError` (the `unknown`/`hierarchy` sentinels pass through), closing Item 4 note N1 that a version bump alone would leave the checkout-absolute leak open (Item 5) | — *(subject deleted — ledger L-246 — the surviving half is the v6 envelope's own refusal of a v5 document, `test_snapshot_v5_gate.py`)* | RETIRED |
| REQ-SNAP-22 | Whole-tree portability (Item 5, Axis 1): the same semantic input captured under two different checkout roots SHALL produce a byte-identical output tree with no checkout-absolute path anywhere in it — a completeness gate that does not depend on enumerating leaking fields by hand | `test_exact_route_whole_tree_portability.py` | PASS |

### SR

**Smart Regen / Preservation** — Component C23 — [reference/23-smart-regen-preservation.md](reference/23-smart-regen-preservation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-SR-01 | Signature comparison SHALL use two-level matching: type-level (required) then field-level... | — *(the two-level signature comparison retired with `test_gen_stencils.py` (ledger L-150, no recorded replacement))* | UNTESTED |
| REQ-SR-02 | Field comparison SHALL be order-independent (sorted) | — *(the order-independent field comparison retired with `test_gen_stencils.py` (ledger L-150, no recorded replacement))* | UNTESTED |
| REQ-SR-03 | `should_regenerate_stencil()` SHALL implement the 6-case decision tree (Item 5 split the unparseable leaf: preserve-on-transient / preserve-non-empty / regenerate-empty) | `tests/unit/test_stencils.py::TestSmartRegenStubUpgrade` (four of the six leaves: stub-upgrade, handwritten-preserved, auto-impl-preserved, stub-preserved-when-not-compilable) | PASS |
| REQ-SR-04 | Stub upgrade SHALL require all 3 conditions: signature match, `NotImplementedError` prese... | `tests/unit/test_stencils.py::TestSmartRegenStubUpgrade::test_stub_upgraded_when_fully_compilable` | PASS |
| REQ-SR-05 | Backup SHALL be created before every regeneration or upgrade | `tests/unit/test_stencils.py::TestSmartRegenStubUpgrade::test_backup_created_before_regen_through_real_stencil_path` | PASS |
| REQ-SR-06 | All module types (including aggregation and FORMULA) SHALL route through the single unified `_generate_stencils()` smart-regen code path (static analysis; not a runtime proof that aggregation/FORMULA are always regenerated in practice) | — *(the single-unified-path static analysis retired with `test_gen_stencils.py` (ledger L-150, no recorded replacement))* | UNTESTED |
| REQ-SR-07 | Static: `_generate_stencils` source contains a `preserve_handwritten` + `output_path.exists()` branch whose body does not call `should_regenerate_stencil` (the skip behavior is not executed) | — *(the preserve-branch static check retired with `test_gen_stencils.py` (ledger L-150, no recorded replacement))* | UNTESTED |

### SVM

**Supplied-Value Materializer** (PIPELINE-TRUTH Item 2) — `resolution/supplied_values.py` — [reference/25-hierarchy-resolver.md](reference/25-hierarchy-resolver.md#supplied-value-materializer-req-svm-0104). Reuses doc 18's shared `_find_literal_redefinition` helper (Strategy 1); sibling of doc 12's per-consumer VBR-03 (this mechanism keys by source QN and collapses across consumers).

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_zero_default_exact_route.py`, `test_elaboration_identity_collisions.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-SVM-01 | For a referenced subsystem-attr binding, synthesize a design attribute carrying the LITERAL value resolved by precedence (usage override > specialized-def `:>>` > base def), `default_value` as a string | — *(subject deleted — ledger L-248)* | RETIRED |
| REQ-SVM-02 | Key the synthetic attribute by source QN so differently-named consumers collapse to one entry point | — *(subject deleted — ledger L-248 / L-142)* | RETIRED |
| REQ-SVM-03 | A synthetic attribute SHALL never overwrite a real captured design attribute; on collision the real one wins and the materializer WARNs | — *(subject deleted — ledger L-248)* | RETIRED |
| REQ-SVM-04 | Apply LITERAL only; emit a count-summary WARN naming non-literal (CHAIN/EXPRESSION) skips; a referenced non-literal-only binding falls through to Step-4 (V11), never a silent drop | — *(subject deleted — ledger L-248)* | RETIRED |

> **Contract disposition — REQ-SVM-01: `PARTIAL`** (SOURCE-IDENTITY Item 3). The synthesis
> clause — materialize the precedence-resolved LITERAL as a design attribute — `stands` as
> value-adapter behavior once it derives from the single identity authority; as an independent
> identity authority it is `SUPERSEDED` (Appendix B row "Supplied-value synthesis may decide
> source identity on its own authority"). The reference→literal stamp is a different mechanism
> (VBR tier 1) with its own Appendix B row, not an SVM clause.

> **Contract disposition — REQ-SVM-02: `PARTIAL`** (SOURCE-IDENTITY Item 3). The source-QN
> convergence direction `stands` (cell C14 owns the target topology); keying as an independent
> identity decision is `SUPERSEDED` (Appendix B synthesis row).

> **Contract disposition — REQ-SVM-04: `PARTIAL`** (SOURCE-IDENTITY Item 3). The LITERAL-only
> application clause `stands`; the skip-summary WARN clause `stands`; the
> no-silent-drop/V11-fall-through clause `stands` — all as value-adapter behavior. The row is
> `SUPERSEDED` only insofar as tier matching by name/scope is read as an independent identity
> decision (Appendix B synthesis row) — the same authority boundary as REQ-SVM-01.

### VBR

**Virtual Binding Rewrite** — Component C09 — [reference/12-virtual-binding-rewrite.md](reference/12-virtual-binding-rewrite.md)

> **Retired family — every row below is the record of deleted code.** The Item 7 retirement removed this component; the per-row cells name the deletion-ledger rows. Nothing here describes what the product does. The behaviour that survived is proved by `test_elaboration_shadowing.py`, `test_elaboration_specialization_retypes.py`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-VBR-01 | Override index SHALL be keyed by `(full_parent_path, leaf_attribute_name)` | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-02 | Deep-path overrides SHALL join intermediate `target_path` segments with `__` to form `ful... | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-03 | LITERAL override SHALL set `binding_type=LITERAL`, copy `literal_value`, clear `source_pa... | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-04 | CHAIN override SHALL replace `source_path` with the redefinition's `source_path` | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-05 | Template copies (`is_template=True`) SHALL be skipped during rewriting | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-06 | Bindings already LITERAL or with no `source_path` SHALL be skipped (no double-rewrite) | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-07 | Rewriting SHALL complete BEFORE any downstream processing (Step 3.5 ordering) | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-08 | `_create_virtual_calc_usage` SHALL shallow-copy each `BindingInfo` so no two virtual instances share a binding object (divergent-sibling rewrite correctness; Item 10 precondition) | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-09 | `_rewrite_virtual_bindings` SHALL NOT raise on a bare-name `source_path`; it logs DEBUG and skips the override match | — *(subject deleted — ledger L-187 / L-250)* | RETIRED |
| REQ-VBR-10 | Mechanism-D home (Item 10 #3): `_rewrite_specialized_chain` SHALL rewrite a `part_usage.attr` CHAIN binding through the retyped usage's specialized-def `:>>` chain (three-tier merge: usage override > specialized-def `:>>` > base def); and `_rescue_self_named_bindings` SHALL rewrite a full-QN self-reference (`in x = x`) to its upstream channel when an outer same-named EXPOSE resolves, else leave it as-is (the `self_named_binding_trap` negative) | — *(subject deleted — ledger L-183 / L-171)* | RETIRED |
| REQ-VBR-11 | The `_rewrite_specialized_chain` type-select SHALL be instance-aware: it SHALL try the consumer INSTANCE's path key (`usage.qualified_name.rsplit("__",1)[0]`, `part_usage`) in `usage_type_map` before the declaring-def key, so a two-level specialization (usage-level `:>> driver : Subtype` on an inherited part usage) selects the specialized def where the declaring-def key sees only the base type | — *(subject deleted — ledger L-184)* | RETIRED |

> **Contract disposition — REQ-VBR-03: `SUPERSEDED`** (SOURCE-IDENTITY Item 3). Clearing
> `source_path` while stamping a literal converts a reference-derived value into a
> consumer-local literal — the reference→literal stamp, impermissible as an identity mechanism
> (contract D-16; Appendix B row "Stamping an occurrence override literal onto same-named
> consumer inputs preserves the modeled source"). Any surviving value-adapter behavior derives
> from the single identity authority (Item 5).

> **Contract disposition — REQ-VBR-10: `PARTIAL`** (SOURCE-IDENTITY Item 3). The
> `_rewrite_specialized_chain` clause `stands` (kin of cell C21; test Status untouched). The
> `_rescue_self_named_bindings` clause is `SUPERSEDED`: the self-binding is inert and is never
> rewritten to an outer channel (contract D-4, family SRC-01; Appendix B row "A consumed input
> whose value expression resolves to its own parameter is rescued by binding to a same-named
> outer feature").

---

## Untested Requirements

Ten rows describe live behaviour that nothing in the tree proves. Nine of them got there the same
way: the only pin was a conformance module the Item 7 retirement deleted, and the deletion ledger
recorded no replacement. This is the retirement's real coverage debt, listed rather than papered over
with a citation to a test that proves something else.

The tenth is a different kind and is recorded separately below.

All nine trace to two deleted modules:

- **`test_gen_schemas.py`** (ledger L-149) — REQ-GEN-03, REQ-OSR-02, REQ-OSR-03, REQ-OSR-05.
  The output-schema rules: when a module gets a named `MultiOutput` subclass rather than
  `RootModel[float]`, that its field names track `ModuleOutput.field_name`, and that output
  fields carry no defaults. The generator still applies all three; the rendered result is
  compared byte-for-byte between routes (`test_exact_route_generated_package.py`), but no kept
  node asserts the rule, so a rule change that moved both routes together would pass.
- **`test_gen_stencils.py`** (ledger L-150) — REQ-SR-01, REQ-SR-02, REQ-SR-06, REQ-SR-07.
  Smart-regen internals: two-level signature comparison, order-independent field comparison,
  and the two static checks over `_generate_stencils`. The stub-upgrade and backup leaves did
  survive, in `tests/unit/test_stencils.py::TestSmartRegenStubUpgrade` (REQ-SR-03/04/05).

And one from the graph-assembly deletion:

- **REQ-GA-05** — the exact-`ComputationGraph`-field-set pin retired with
  `test_graph_assembly.py` (ledger L-152). A field added to or removed from the graph now
  passes silently instead of flipping a test red.

The tenth, filed 2026-08-14 and **not** retirement debt:

- **REQ-DIAG-04** (severity skew fails closed) — the failure mode is impossible on this product
  rather than guarded: no severity crosses a process boundary on disk, so there is nothing for a
  test to assert. It is UNTESTED and not PASS because no kept test would fail if the v6 envelope
  started carrying a `severity` field again. The upstream exact-equality guards still exist in
  `agentic_mbse.sysml.constraint_facts` for callers that parse serialized facts; codegen does not
  exercise them.

REQ-PGD-06, previously the matrix's single UNTESTED row, is now RETIRED: the deriver it
describes was deleted (ledger L-160).

(TRUTH-DEBT Item 3's three discharges stand where their subjects do: REQ-DM-08 via
`test_dm08_enforced_surface.py`, which is in the tree. REQ-RES-05 and REQ-RES-08 read RETIRED
— `TestInnerStepOrdering` and `test_res08_consumer_scope_paths.py` both pinned deleted code.)

## Related Documents

- [Architecture Overview](overview.md)
- [Modeling Assumptions](modeling-assumptions.md)
- Design docs: [reference/](reference/) (28 documents)
- Conformance tests: `tests/conformance/`, `tests/unit/`, `tests/integration/` (55 distinct kept test files cited by non-RETIRED rows — recounted 2026-08-14, CONSTRAINT-SEMANTICS Item 7, method recorded in the item's verification.md; this line read 50 before, and an intermediate 59 was corrected at the audit resume)
