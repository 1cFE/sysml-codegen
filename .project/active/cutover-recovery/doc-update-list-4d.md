# Gate 4D — the subject-by-subject documentation update list

**Scope:** the 34 documents under `docs/architecture/` (31 numbered reference docs, plus
`overview.md`, `modeling-assumptions.md`, `verification-matrix.md`) and `CLAUDE.md`.

**What this list is for.** Gate 4D's restore step is already satisfied — Gate 4A measured all
22 incident-modified documents byte-identical to the Item 6 base at rebuild HEAD (ledger rows
L-252..L-274). What remains is the rewrite, and the plan requires the stale claims to be named
before any of them is rewritten. Each row below says which claims stopped being true and which
public behaviour replaces them, or says "no stale claims" with the basis for that.

## The state the documents must describe

Since Slice 3E the **exact route is the only public authority**: source admission → strict
elaboration → `InstanceGraph` → one-way projection → generation, with v6 instance-graph
snapshots as the offline source. `run_codegen` (`src/sysml_codegen/cli/__init__.py:956`)
constructs one way; `--models` and `--from-snapshot` are two *sources* for that one authority,
not two implementations.

The legacy string-resolution machinery (`analysis/`, `resolution/graph_builder.py`,
`orchestration/pipeline_builder.py`, the v5 snapshot loader/serializer/rebuild) is **present in
the tree and importable, and publicly unreachable**. Its retirement is fully prepared and gated
on owner acceptance at the Phase 5 stop. Two conformance nodes pin exactly that state:

- `test_public_authority_switch.py::test_the_construction_path_reaches_no_legacy_authority_even_transitively`
  — nothing in the construction closure reaches a legacy authority module.
- `test_public_authority_switch.py::test_the_generation_half_still_reaches_v5_modules_and_that_residual_is_pinned`
  — `sysml_codegen.cli`'s *import* closure still contains `pipeline_builder`,
  `snapshot.loader`, and `snapshot.graph_rebuild`. Importable is importable; Phase 4's
  retirement empties that set.

So a document must not describe the legacy route as live, and must not describe it as deleted.

## Content sources this gate treats as authoritative

The 3E and 4C mechanism records in `plan.md`, each re-verified against the tree at HEAD:

| Mechanism | What it says | Verified at |
|---|---|---|
| Consumer collapse | A design-attribute entry point is keyed by the **supplying attribute's** display path, so every consumer of one modelled attribute shares one JSON key. Legacy minted one key per consuming formal. | `elaboration/project.py:430-457` (`_source_for_edge`, `NodeRef` branch) |
| Declaration-site groups (option C) | A group is named after the file that **declares** the owner node, not the file that uses it. `model.sysml` — the one stem carrying no identity — falls back to the declaring package of the root occurrence. | `elaboration/project.py:308-355` (`_group_base`, `_declaring_package`) |
| Per-occurrence expansion | An arrayed child is enumerated: one attribute node and one entry point per occurrence, keys carrying the index (`…__battery_pack[0]__capacity_kwh`). There is no parametric multiply. | `tests/conformance/test_elaboration_aggregations.py:135`, `test_exact_projection_aggregation.py::test_every_member_occurrence_is_its_own_entry_point` |
| Zero-constraint early return | The exact route emits no `constraint_report_aggregator` when there are no constraint outputs; legacy emitted one unconditionally. | `elaboration/project.py:887` |
| Units annotation rule | A unit annotation is unwrapped to the expression it annotates, once, up front — a unit is not a data dependency. | `_ExactElaborator._without_unit_annotation` in `elaboration/elaborate.py`; pins in `tests/conformance/test_unit_annotation_values.py` |
| Envelope identity model | Constants, environment facts, and the graph are anchored; `sources` is a self-declared manifest checked for canonical form, never against the files, unless the caller passes `source_roots`. What no offline check can prove is that the sealed graph is the elaboration of the sealed sources. | `snapshot/envelope.py:1-53` (module docstring), `orchestration/exact_pipeline_context.py:236-249` |
| S4 rendering collision | An expression parameter is named after the reference's **last member**, qualifier dropped, so two aggregation terms reading a same-named attribute off different children both render `capital_cost` and the model is refused `SI_RENDERING_COLLISION`. | `elaboration/elaborate.py:1937` (`fact.resolved_member_names[-1]`), `elaboration/project.py:598-604`; pinned by `tests/integration/test_costed_component_exact_route.py::test_a_two_term_same_name_rollup_is_refused` |

## Review method, stated so the record is honest

- **Rewritten documents** (00, `overview.md`, 27, 02, `modeling-assumptions.md`, 06, 17, 23,
  `verification-matrix.md`, `CLAUDE.md`) were read in full before the edit and re-read after.
- **Banner-only documents** got their subject, requirement set, and every code reference they
  make reviewed; the body is unchanged and remains an accurate description of the component it
  documents, which is the whole basis for a banner rather than a rewrite. They were not re-read
  line by line. This is a deliberate narrowing of the plan's "read every changed document in
  full", recorded here rather than glossed.

## The per-document verdicts

### Rewritten this gate

| Doc | Stale claims | Replacing public behaviour |
|---|---|---|
| `reference/00-pipeline-overview.md` | The whole "7-step pipeline" diagram and its step-by-step trace describe `build_pipeline_context`; the snapshot paragraph describes v5 and `PipelineContext`; the package-structure block lists `analysis/`, `resolution/`, and the v5 snapshot modules as live pipeline stages; REQ-PIPE-01's verifier names `build_computation_graph()`. | The exact route's five stages, the v6 snapshot source, and the retirement state. Requirement text kept; verifiers re-pointed at the projector where they named a legacy function. |
| `overview.md` | Same route description in prose and diagram; the second, license-free path is described as `build_pipeline_context_from_snapshot` rebuilding a `PipelineContext`; the package-structure block and Component Index attribute live components to `pipeline_builder.py` / `graph_builder.py`; "Typed Registries" and "Producer Resolution Architecture" are presented as current architecture. | Same as 00, at overview altitude. The registry and producer-resolution sections are re-framed as the retiring implementation with a pointer, not deleted — their subjects are real and their docs survive. |
| `reference/27-snapshot-generation.md` | Every claim is about the **v5 extraction** snapshot: `snapshot_format_version: 5`, the V1–V7 policy table, `PipelineContext` rebuild, the capture-script split, REQ-SNAP-08..20. `generate --from-snapshot` no longer accepts any of it. | The v6 instance-graph envelope: what it seals, what is anchored, the `source_roots` provenance step, the documented offline limit, and the v5 refusal by name. The v5 section is retained under a retiring heading because the format still exists in the tree and 14 runtime snapshots still depend on it. |
| `reference/02-orchestration.md` | `build_pipeline_context()`'s 7-step sequence, the step-ordering requirements REQ-ORCH-01..07, the 4-phase registry protocol, virtual-binding rewriting, and aggregation scoping are all the retiring orchestrator's. | The public surface: one construction entry point, two sources, a receipt-bound context, and the named single-authority pins. The legacy sequence is retained under a retiring heading — it is still the accurate description of `pipeline_builder.py`. |
| `modeling-assumptions.md` | §4 "Aggregation via Redefinition" permits `sum(pv_module.capital_cost) + array_bos.capital_cost` — the exact route refuses two same-named terms. §6 "Uniform-Array Assumption" documents parametric multiply (`sum(child.attr)` → `count * child.attr`) and one aggregation module per assembly attribute. §2 "Parameter Grouping" describes grouping by design file without the declaration-site rule. | The S4 modelling requirement (one named intermediate per child role, `costed_cart_d5` as the worked example, the Item 10 cross-reference), per-occurrence expansion, and the declaration-site grouping rule. |
| `reference/06-entry-point-classifier.md` | The three types survive, but every mechanism claim is the retiring classifier's: `_classify_entry_points()`, the `design_attr_by_qname` / `unbound_lookup` / `entry_point_sources` indexes, the two creation paths, the `system_design` orphan fallback, REQ-EPC-02..08. | The projection's rule: a design attribute keys by the supplying attribute's display path (consumer collapse); a library default and a usage literal key by `{consumer}__{formal}`; there are no orphans because a group is chosen at mint time. |
| `reference/17-parameter-group-deriver.md` | The whole document describes `analysis/parameter_groups.py`: four indexes, precedence, `derive_groups_filtered`, the Step-5.7 construction site, and grouping by the *using* file. | Banner plus the live rule: declaration-site identity (option C), the `model.sysml` package fallback, and the normalized label that reaches generated bytes. |
| `reference/23-smart-regen-preservation.md` | Cites `analysis/signature_extractor.py` in four places as a parallel copy. **That module was deleted by this recovery** (Gate 4B-G1, `6ba346e` — "retire the dead signature extractor"). | The single copy in `generation/preservation.py`. Everything else in the document is unchanged and true. |
| `verification-matrix.md` | Rows pointing at now-false claims only: the `resolution/input_resolver.py` reference (that module was deleted before the recovery, at `936315c`), and rows whose subject moved to the exact route. | Pointer-level corrections only. No wholesale rewrite — the matrix is subject-specific by plan rule 8 and its REQ-to-test traceability is intact. |
| `CLAUDE.md` | Install line names `~/agentic-mbse`, which does not exist (the wired checkout is `../agentic-mbse`). `uv run pytest tests/` does not run — `dev` is an optional extra, so the command needs `--extra dev`. The Processing Pipeline section describes extraction → analysis → resolution → generation with `build_computation_graph()` as the graph source. The Snapshot bullet describes v5 (`snapshot_format_version`, `compilation_results`). ADR-001's classification description is the retiring classifier's. | The exact route, the v6 snapshot flag semantics, the corrected commands, and the pending-retirement note. Own disposition, own commit (plan rule 8). |

### Status banner — the document's sole subject is a retiring-legacy component

Each is accurate about the component it describes. None is stubbed, none is deleted; their full
disposition ships with the retirement.

| Doc | Subject | Owner module | Basis |
|---|---|---|---|
| `reference/03-resolution-overview.md` | The scope problem and the 270-combination resolution space | `resolution/`, `analysis/dependency_backtracker.py` | Not in the construction closure. Also cites `resolution/input_resolver.py`, deleted at `936315c`. |
| `reference/04-producer-resolution.md` | `resolve_producer()`, the 21 key forms, the strict/lenient fork | `resolution/producer_resolution.py` | Not in the construction closure; reached only from `generation/initialization.py`, which the public route does not call. |
| `reference/05-module-factory.md` | The three legacy factory functions | `resolution/graph_builder.py` | Not in the construction closure. The *subject* (three calc module kinds) survives — projection builds them — which the banner points at. |
| `reference/07-graph-assembly.md` | Legacy toposort, channel validation, graph packing | `resolution/graph_builder.py` | Not in the construction closure. Subject survives in `elaboration/project.py` (`_topological_modules`). Separately, this doc cites `core/graph_algorithms.py`, which has never existed in this tree — recorded, not fixed here (rule 10). |
| `reference/09-data-models.md` | All data models | mixed | **Scoped banner, no rows removed.** `ComputationGraph`/`PipelineModule`/`EntryPoint`/`ParameterGroup` are live; the extraction models, `BacktrackingResult`, `DesignAttributeData`, `DerivedParameterGroup`, and `ParameterSource` describe retiring owners. Removing those rows is ledger row **L-120**, which the plan couples to a `tests/conformance/test_data_models.py` edit in the same commit — a test change this gate's brief forbids. The banner adds information and removes nothing, so it forces no test change; the row deletions ship with L-120. |
| `reference/10-output-registry.md` | The 4-phase typed registry | `core/output_registry.py`, `orchestration/output_registry_builder.py` | Not in the construction closure. The exact route indexes output channels directly from the instance graph. |
| `reference/11-analysis-backtracker.md` | DFS dependency backtracking | `analysis/dependency_backtracker.py` | Not in the construction closure. |
| `reference/12-virtual-binding-rewrite.md` | Template expansion and binding rewrite | `orchestration/pipeline_builder.py` | Not in the construction closure. The elaborator does occurrence enumeration instead. |
| `reference/13-aggregation-scoping.md` | PartDef-level aggregation scoped to instances | `orchestration/pipeline_builder.py` | Not in the construction closure. Banner also carries the pointer to the S4 modelling requirement, which is the aggregation subject a modeller now needs. |
| `reference/24-dual-resolution-architecture.md` | Why the calc consumer resolves during DFS | `analysis/` + `resolution/` | Not in the construction closure. Also cites `resolution/input_resolver.py`, deleted at `936315c`. |
| `reference/25-hierarchy-resolver.md` | `:>>`, multiplicity, and `sum()` extraction | `extraction/hierarchy_resolver.py` | Not in the exact construction closure (measured: the closure reaches `extraction/extractor.py` and `expression_compiler.py`, not `hierarchy_resolver.py`). |

### No stale claims

| Doc | Basis |
|---|---|
| `reference/01-extraction.md` | Its subject — what `SysMLDataExtractor` extracts from a loaded model — is live: the exact route loads and extracts calculation definitions through it (`orchestration/elaborated_pipeline.py:46,57`). Its binding-type and redefinition taxonomies are extraction facts, not resolution claims. |
| `reference/08-generation.md` | The generation layer is unchanged and is the exact route's back half. Every claim is about `generation/*.py` reading a `ComputationGraph`, which is what projection hands it. |
| `reference/14-expression-compiler.md` | `extraction/expression_compiler.py` is in the exact construction closure and is called by the projector (`elaboration/project.py` imports `Compilability`). |
| `reference/15-naming-conventions.md` | EQN/PQN/module-name/channel-name rules are `core/qualified_names.py` and `core/identifier_types.py`, both live and both used by projection (`get_channel_name`, `derive_module_type`, `sanitize_name`). §7 "Output Registry Key Formats" describes a retiring structure but states no false claim about the public route; folded into the registry subject's disposition at the retirement rather than split across two gates. |
| `reference/16-computed-attributes.md` | **Recorded as stale-minor, not fixed here.** Its classification taxonomy is extraction-level and true; its resolution-map and Phase-3b claims are the retiring route's. The document's replacement content is the elaborator's computed-attribute handling, which has no settled written form yet — writing one is content authorship, not a repair, and belongs with the Item 8 doc pass. Rule 10: recorded rather than guessed. |
| `reference/18-literal-value-propagation.md` | **Recorded as stale-minor, not fixed here.** Same shape as 16: subject is real, owner (`resolution/graph_builder.py::_find_literal_redefinition`) is retiring, and the exact route's equivalent is `ValueSite` on the attribute node. Ships with the retirement. |
| `reference/19-ast-dispatch-invariant.md` | The FCE-before-OE invariant is an AST-dispatch fact about SysIDE's type system, enforced at extraction sites that remain live. |
| `reference/20-module-registry-generation.md` | `generation/registry.py` is unchanged and live. The Gate 4C part 7 re-derivation confirmed the load-bearing rule (design-scoped import paths from the module's own EQN) holds identically on the exact route. |
| `reference/21-pipeline-yaml-generation.md` | `generation/pipeline.py`, unchanged, graph-fed. |
| `reference/22-output-schema-rules.md` | `generation/schemas.py`, unchanged, graph-fed. |
| `reference/26-pipeline-module-migration.md` | Already carries a "Status: Historical" banner, and the end state it documents (no generator imports `CalculationDefinitionData`) still holds on the exact route. |
| `reference/28-constraint-lowering-and-catalog.md` | Split subject that stays true: the lowering half names `analysis/constraint_lowering.py` explicitly in its own heading, so it reads as a description of that module rather than of the public route; the catalog half (`generation/constraint_catalog.py`) is live and the exact route assembles the same `ConstraintCatalog`. One behavioural delta is recorded on the pipeline-overview subject instead of here: the zero-constraint report aggregator. |
| `reference/29-contracts-and-sealing.md` | `contracts/` is unchanged and is Step 9 of the public route. |
| `reference/30-diagnostic-severity.md` | The severity contract (writer-set field, blocking vs advisory, fail-closed skew) is an extraction-diagnostic fact and its sinks run before any route choice. |

## Surfaced, not resolved (rule 10)

1. **`reference/07-graph-assembly.md` cites `core/graph_algorithms.py`, which has never existed
   in this tree** (no creating and no deleting commit). Pre-existing, unrelated to the incident,
   and outside this gate's subject set. Needs an owner.
2. **Two production docstrings are stale in the same way the documents were**, and this gate is
   forbidden to touch production code: `orchestration/exact_pipeline_context.py:3-6` still says
   the legacy `PipelineContext` and its builders "remain the shipped authority", and
   `elaboration/__init__.py:5-7` still says projection "never becomes a shipped flag" until the
   Item-6 cutover. Both were true when written and are false at HEAD. They belong to the
   retirement commit that touches those files.
3. **The full-suite battery could not be measured against the recorded 3790-node baseline.** The
   wired companion checkout (`/home/reid/1cfe/agentic-mbse`, branch `elaborate-first-salvage`,
   `5088b41`) does not export `preflight_identified`, so
   `tests/conformance/test_exact_constraint_route.py` fails to import and pytest interrupts
   collection. Reproduced on a clean tree before any Gate 4D edit — pre-existing environment
   divergence, not caused by this gate. Batteries below are measured with that one module
   ignored, and both the before and after numbers are measured the same way so the delta stays
   meaningful.
