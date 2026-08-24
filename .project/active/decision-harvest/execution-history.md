# Execution History — `.project/completed/`

Reconstructed chronology of every archived work item. One record per folder,
produced by a per-folder summarization pass and joined mechanically.
Ordered by epic, earliest first; items within an epic ordered by date.

**Items**: 126  |  **Epics (incl. `unknown`)**: 14


## Timeline

| ID | Date | Epic | Item | Subject | Title | Status | Bin |
|---|---|---|---|---|---|---|---|
| H-001 | 2026-02-02 | unknown | — | generated output, TEAx runtime execution | Fix three codegen output gaps that blocked generated packages from executing directly under TEAx's execute_pipeline() | unknown |  |
| H-002 | 2026-02-03 | EXPR-CODEGEN | Item 1 | expression AST extraction | Spike: validate that SysIDE exposes CalcDef output expression ASTs and that feature references resolve | shipped |  |
| H-003 | 2026-02-04 | EXPR-CODEGEN | Item 2 | expression compilation spike | Spike proving syside expression ASTs compile to correct Python and that a compilability classifier partitions CalcDefs with zero false positives | shipped |  |
| H-004 | 2026-02-06 | EXPR-CODEGEN | Item 3 | expression compiler | Build a standalone expression compiler module that converts SysML expression ASTs into executable Python | unknown |  |
| H-005 | 2026-02-07 | EXPR-CODEGEN | Item 4 | expression compiler pipeline wiring | Wire the expression compiler into the codegen pipeline so compilable CalcDefs get auto-generated implementations instead of NotImplementedError stubs | shipped |  |
| H-006 | 2026-02-08 | EXPR-CODEGEN | Item 4.1 follow-on | auto-impl output generation | Fix NameError in generated multi-output CalcDef auto-implementations when a later output references an earlier declared output | shipped |  |
| H-007 | 2026-02-08 | EXPR-CODEGEN | Item 5 | expression codegen e2e validation | End-to-end validation of the expression compiler on real solar_battery and newly-built CATF fusion model fixtures | shipped |  |
| H-008 | 2026-02-09 | ATTR-EXPR | Item 2 | computed attribute extraction | Build data models and extraction logic to classify and compile PartDef/PartUsage attribute expressions | unknown |  |
| H-009 | 2026-02-09 | ATTR-EXPR | Item 3 | computed attribute modules | Wire computed-attribute extraction into the codegen pipeline so FORMULA attributes generate executable modules | shipped |  |
| H-010 | 2026-02-09 | ATTR-EXPR | Item 1 | attribute expression AST discovery | Spike: confirm SysIDE exposes expression ASTs on PartDef attributes, as the hard go/no-go gate before building automatic computed-attribute codegen | shipped |  |
| H-011 | 2026-02-09 | ATTR-EXPR | Item 5a | ADR documentation, epic closure | Write ADR-001 through ADR-005 for attribute-expression architecture and close the ATTR-EXPR epic | shipped |  |
| H-012 | 2026-02-09 | ATTR-EXPR | Item 4 | computed attribute e2e validation | End-to-end numerical validation of computed attribute expression pipeline on real models | shipped |  |
| H-013 | 2026-02-10 | unknown | — | codegen bug fixes | Fix seven codegen bugs found during fusion-tea E2E validation, as a blocking prerequisite for the COST-PATTERN epic | shipped |  |
| H-014 | 2026-02-10 | COST-PATTERN | Item 4 | hierarchy-aware module generation | Pipeline-integrate hierarchy extraction so virtual CalcUsages and aggregation rollups generate real modules | unknown |  |
| H-015 | 2026-02-10 | COST-PATTERN | Item 3 | redefinition and aggregation extraction | Extract redefinition, multiplicity, and aggregation-expression data to bridge virtual CalcUsages to the pipeline | shipped |  |
| H-016 | 2026-02-10 | COST-PATTERN | Item 1 | SysIDE AST, hierarchy/redefinition probing | Research spike probing how SysIDE's AST represents hierarchy, redefinition, multiplicity, and aggregation patterns needed for the Costed Component pattern | shipped | keep |
| H-017 | 2026-02-10 | COST-PATTERN | Item 2 | calc usage template expansion | Detect template CalcUsages owned by PartDefinitions and expand them into per-instance virtual CalcUsages | unknown |  |
| H-018 | 2026-02-13 | COST-PATTERN | Item 5 | costed component hierarchy pipeline | End-to-end validation of the Costed Component pipeline on the solar_battery model, plus three ADRs | unknown |  |
| H-019 | 2026-02-11 | COST-PATTERN | Item 5 | hierarchy aggregation pipeline | Eight production bug fixes at hierarchy-aware aggregation pipeline subsystem boundaries, found during E2E validation | unknown |  |
| H-020 | 2026-02-12 | COST-PATTERN | Item 5 | hierarchy extraction AST dispatch | Five probe-validated AST dispatch fixes to make hierarchy E2E tests pass against the real SysIDE model | unknown |  |
| H-021 | 2026-02-13 | unknown | Item 4 | OutputRegistry design spikes | Three empirical spikes resolving OutputRegistry design-comment gaps in CHAIN redefinitions, REFERENCE bindings, and design-attribute defaults | shipped |  |
| H-022 | 2026-02-13 | OUTPUT-REGISTRY | Item 1 | backtracker output indexing | Add the ChannelAlias model and OutputRegistry class as a single exact-match lookup, replacing five ad-hoc backtracker indexes | shipped |  |
| H-023 | 2026-02-13 | unknown | — | output registry key formats | Spike 8 -- validate OutputRegistry key-format compatibility end to end before implementing it | unknown |  |
| H-024 | 2026-02-13 | unknown | — | SysIDE AST key formats | Four diagnostic spikes to empirically verify SysIDE AST assumptions behind the planned OutputRegistry design | shipped |  |
| H-025 | 2026-02-14 | OUTPUT-REGISTRY-BACKTRACKER-REDESIGN | Items 2a + 2b | channel alias production pipeline | Produce first-class ChannelAlias objects from EXPOSE_PURE and CHAIN redefinitions for the OutputRegistry | shipped |  |
| H-026 | 2026-02-14 | OUTPUT-REGISTRY-BACKTRACKER-REDESIGN | Item 3 | OutputRegistry backtracker wiring | Wire the OutputRegistry into the pipeline as a shadow resolution path validated against the existing backtracker cascade | unknown |  |
| H-027 | 2026-02-15 | OUTPUT-REGISTRY-BACKTRACKER-REDESIGN | Item 4 | backtracker output resolution | Cut the dependency backtracker over to OutputRegistry as the sole resolution path, removing the old 5-index/7-strategy cascade and validating end-to-end | unknown |  |
| H-028 | 2026-02-15 | unknown | — | aggregation registry wiring | Runtime spikes validating the root-cause analysis of an aggregation-wiring gap before committing a fix | shipped |  |
| H-029 | 2026-02-16 | COST-PATTERN | — | aggregation graph-builder wiring | Fix aggregation module input wiring so resolvable inputs resolve via the OutputRegistry instead of falling through to ENTRY_POINT | shipped |  |
| H-030 | 2026-02-16 | COST-PATTERN | — | aggregation expression wiring | Fix two aggregation-wiring bugs misclassifying 58 of 70 solar_battery aggregation inputs as entry points | shipped |  |
| H-031 | 2026-02-16 | COST-PATTERN | — | aggregation input wiring | Four diagnostic spikes to empirically verify or falsify root-cause hypotheses for 58 misclassified aggregation inputs | unknown |  |
| H-032 | 2026-02-16 | unknown | — | codegen output directory setup | Add missing __init__.py stubs to the 6 top-level generated output subdirectories | shipped |  |
| H-033 | 2026-02-16 | COST-PATTERN | — | entry point literal propagation | Propagate :>> redefinition literal values through the backtracker and aggregation builder into JSON input templates | shipped |  |
| H-034 | 2026-02-17 | unknown | — | aggregation module factory | Conformance tests for the aggregation module factory (component C16), covering SumTerm/SingletonTerm/LocalTerm resolution and literal-value propagation | shipped |  |
| H-035 | 2026-02-17 | unknown | C10 | aggregation instance scoping | Conformance-test aggregation scoping (PartDef-to-instance expansion, CHAIN aliasing, module_eqn derivation) and add the missing zero-instance warning | shipped |  |
| H-036 | 2026-02-17 | unknown | C07 | AST dispatch ordering invariant | Codebase-wide audit enforcing that FeatureChainExpression is always dispatch-checked before OperatorExpression at every dual-check site | shipped |  |
| H-037 | 2026-02-17 | unknown | C11a | backtracker resolution outcomes | Conformance-test DependencyBacktracker's current resolution outcomes before the typed-dispatch migration (C11b) | shipped |  |
| H-038 | 2026-02-17 | unknown | C11b | output registry resolution | Migrate DependencyBacktracker resolution from the deprecated resolve()/_compat cascade to type-directed registry dispatch | shipped |  |
| H-039 | 2026-02-17 | unknown | — | calc usage module factory | Conformance tests for the CalcUsage module factory (component C14), covering REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08 | shipped |  |
| H-040 | 2026-02-17 | unknown | — | computed attribute classifier | Conformance tests for computed attribute classification (component C05) against REQ-CA-01 through REQ-CA-07 | shipped |  |
| H-041 | 2026-02-17 | unknown | — | data models | Conformance tests for the data model layer (component C01) against design doc 09-data-models.md | unknown |  |
| H-042 | 2026-02-17 | unknown | — | dual/triple resolution consistency | Prove the three resolution paths (backtracker DFS, FORMULA attribute map, resolve_input strategy chain) agree on wiring decisions (X02) | shipped |  |
| H-043 | 2026-02-17 | unknown | — | entry point classification | Conformance tests for the entry point classifier (component C17), covering REQ-EPC-01 through REQ-EPC-08 | shipped |  |
| H-044 | 2026-02-17 | unknown | C04 | expression compiler conformance | Add requirement-traceable conformance tests for the expression compiler (SysIDE AST -> ExpressionAST IR -> Python string, plus compilability verdicts) | shipped |  |
| H-045 | 2026-02-17 | unknown | — | extraction layer | Conformance tests for the SysMLDataExtractor (component C03) against REQ-EXT-01 through REQ-EXT-07 | shipped |  |
| H-046 | 2026-02-17 | unknown | — | FORMULA module factory | Conformance tests for the FORMULA Module Factory (C15), which builds a PipelineModule from a FORMULA computed attribute | shipped |  |
| H-047 | 2026-02-17 | unknown | — | graph assembly / toposort | Conformance tests for Graph Assembly (C18): topological sort, channel validation, and final ComputationGraph packing | shipped |  |
| H-048 | 2026-02-17 | unknown | — | hierarchy resolver extraction | Conformance tests for the Hierarchy Resolver (C06), which extracts SysML redefinition, multiplicity, and aggregation-expression structure | shipped |  |
| H-049 | 2026-02-17 | unknown | C12 | aggregation input resolver | Extract aggregation input resolution into a standalone resolve_input() strategy-chain function | shipped |  |
| H-050 | 2026-02-17 | unknown | C02 | identifier naming utilities | Conformance-test the identifier/naming utility functions (EQN, PQN, module name/type, channel name, Key_C, sanitize_name) | shipped |  |
| H-051 | 2026-02-17 | unknown | — | pipeline orchestrator | Conformance tests for orchestrator step ordering (component C19), covering build_pipeline_context() composition and pipeline-level invariants | shipped |  |
| H-052 | 2026-02-17 | unknown | C08 | output registry typed lookups | Refactor OutputRegistry from a single flat dict[str,str] resolve() into three typed registries (scoped, SysML QN, alias) | shipped |  |
| H-053 | 2026-02-17 | unknown | — | parameter group deriver | Conformance tests for ParameterGroupDeriver (C13), which groups pipeline entry points into JSON input file groups by source file | shipped |  |
| H-054 | 2026-02-17 | unknown | Phase 0 | test infrastructure, snapshots | Build the license-free conformance test harness: extraction snapshots, pipeline JSON/YAML baselines, and shared fixtures | shipped |  |
| H-055 | 2026-02-17 | unknown | — | pipeline end-to-end output | Checkpoint 5 end-to-end pipeline validation (step 5.2 / C19 companion) proving the refactored pipeline matches Phase 0 baselines | shipped |  |
| H-056 | 2026-02-17 | unknown | — | typed registry design | Design-intent spec replacing the flat string-keyed OutputRegistry with typed identifier wrappers and separate typed registries | shipped |  |
| H-057 | 2026-02-17 | unknown | C09 | virtual binding override rewrite | Conformance-test the existing virtual-binding rewrite function that applies :>> design overrides to virtual CalcUsage bindings | shipped |  |
| H-058 | 2026-02-18 | unknown | — | JSON template and schema generation | Conformance tests for the JSON template and parameter schema generator (component C25), covering REQ-GEN-05 and REQ-PY-07 | shipped |  |
| H-059 | 2026-02-18 | unknown | — | module registry generator | Fix the module registry generator (C24) so aggregation import paths and class names stop colliding | shipped |  |
| H-060 | 2026-02-18 | unknown | — | module wrapper generation | Conformance tests for the TEAx module wrapper generator (component C21), covering REQ-GEN-02 | shipped |  |
| H-061 | 2026-02-18 | unknown | — | pipeline YAML generator | Fix two upstream graph_builder bugs (Bug 9: missing param_group prefix, Bug 10: int instead of float) surfaced by the Pipeline YAML generator (C20) | shipped |  |
| H-062 | 2026-02-18 | unknown | — | output schema generator | Conformance tests for the Schema Generator (C22), which produces Pydantic MultiOutput classes for multi-output calc defs | shipped |  |
| H-063 | 2026-02-18 | unknown | — | stencil generation / smart regen | Conformance tests for the Stencil Generator + Smart Regen (C23): auto-impl vs stub generation and handwritten-code preservation | shipped |  |
| H-064 | 2026-02-19 | unknown | — | SysML-to-Python type mapping | Consolidate SysML-to-Python type mapping (X01), which had 6 independently drifted copies, into one shared module | shipped |  |
| H-065 | 2026-02-20 | unknown | Bug 11 | generated output schema defaults | Fix generated MultiOutput Pydantic schemas rendering spurious defaults on output fields, breaking TEAx output-channel detection | shipped |  |
| H-066 | 2026-02-20 | unknown | C26 | pipeline module data model | Expand PipelineModule/ModuleInput/ModuleOutput with metadata fields so generators can run from the ComputationGraph alone | unknown |  |
| H-067 | 2026-02-20 | unknown | — | dead code cleanup | Remove confirmed-dead code paths (step 7.4) plus fix one deferred bug (endswith false positive) | shipped |  |
| H-068 | 2026-02-20 | unknown | — | module factory functions | Make the three module factory functions pure (return entry points instead of mutating a shared dict) | shipped |  |
| H-069 | 2026-02-20 | unknown | — | naming and identifier-type utilities | Delete the naming/identifier-types backward-compat shim modules and point all importers at core/ (Step 7.3) | shipped |  |
| H-070 | 2026-02-20 | unknown | Phase 7.1 | orchestration package extraction | Pure structural refactor: move pipeline orchestration functions out of generation/initialization.py into a new orchestration/ package | shipped |  |
| H-071 | 2026-02-22 | unknown | — | architecture documentation | Consolidate scattered post-refactor design notes and stale ADRs into a single docs/architecture/ authority | shipped |  |
| H-072 | 2026-07-07 | TRUTH-DEBT | Item 4 | computed-attribute classifier | Fix the computed-attribute classifier so inherited PartDef attributes classify FORMULA instead of silently-dropped EXPOSE_COMPUTED | shipped |  |
| H-073 | 2026-07-08 | TRUTH-DEBT | Item 1 | aggregation input resolution | Wire the consolidated resolve_input aggregation resolver into the live pipeline path, deleting the old channel-only function and its inline entry-point fallbacks | shipped |  |
| H-074 | 2026-07-08 | TRUTH-DEBT | Item 2 | backtracker chain resolution | Resolve 3+-segment (multi-hop) calc-usage chain bindings to their upstream channel instead of hard-rejecting | shipped |  |
| H-075 | 2026-07-08 | TRUTH-DEBT | Item 6 | silent-failure hardening, diagnostics | Harden four benign-leaning silent-fallback sites (D3 hygiene tail) so each fires a diagnostic on its silent shape or is formally reclassified | shipped |  |
| H-076 | 2026-07-08 | TRUTH-DEBT | Item 5 | verification matrix integrity | Retire the verification-matrix sweep residue: 17 strengthens, 11 reframes, 5 citation fixes, and the unswept ~46-row tail | shipped |  |
| H-077 | 2026-07-08 | TRUTH-DEBT | Item 3 | verification matrix test-gap closure | Author independently-anchored tests for three UNTESTED verification-matrix rows (REQ-DM-08, REQ-RES-05, REQ-RES-08), flipping them to PASS with honest text reframes | shipped |  |
| H-078 | 2026-07-10 | PUSH-DOWN | Item 4 | aggregation decomposition boundary | Split aggregation-expression handling so agentic-mbse owns neutral SysML decomposition facts and sysml-codegen keeps Python rendering and pipeline assembly | shipped | ADR |
| H-079 | 2026-07-10 | PUSH-DOWN | Item 1 | expression reconstruction helpers | Move reusable SysML expression reconstruction and literal-node helpers from sysml-codegen into agentic-mbse's shared SysML layer | shipped |  |
| H-080 | 2026-07-10 | PUSH-DOWN | Item 3 | hierarchy extraction, redefinition/multiplicity models | Move the reusable SysML hierarchy primitive layer (redefinition and multiplicity extraction) from sysml-codegen into agentic-mbse | shipped |  |
| H-081 | 2026-07-10 | PUSH-DOWN | Item 2 | qualified-name utilities module boundary | Split qualified-name utilities so SysML-general helpers move to agentic-mbse | shipped |  |
| H-082 | 2026-07-13 | CONSTRAINT-EXEC | Item 7 | constraint code generation | Generate the constraint module, Kleene predicate compiler, aggregator, and embedded catalog so a modeled assertion can actually execute | shipped |  |
| H-083 | 2026-07-13 | CONSTRAINT-EXEC | Item 5 | constraint lowering phase | Productionized concrete constraint lowering: strict-resolution expansion of modeled assertions into graph structure with execution identity | shipped |  |
| H-084 | 2026-07-13 | CONSTRAINT-EXEC | Item 6 | PipelineModule kind dispatch | Replace the is_computed_attribute/is_aggregation boolean flags on PipelineModule with a single module_kind enum, dispatched at all generation seams | shipped |  |
| H-085 | 2026-07-13 | CONSTRAINT-EXEC | Item 4 | part instance discovery index | Build a part-structure-only instance index (subtype closure + fixed-cardinality expansion) so constraint-only part definitions get discovered | shipped |  |
| H-086 | 2026-07-13 | CONSTRAINT-EXEC | Item 8 | snapshot constraint parity | Make constraint facts a load-bearing snapshot section and flip the from-snapshot default to lower constraints, closing live/snapshot divergence | shipped |  |
| H-087 | 2026-07-13 | CONSTRAINT-EXEC | Item 14 | constraint catalog migration, docs, IFE acceptance | Retire the drop-manifest era, flip authoring docs to the executable profile, and pass IFE-sweep acceptance against the generated viability assertion | shipped |  |
| H-088 | 2026-07-13 | CONSTRAINT-EXEC | Item 13 | expression tree retirement | Retire the legacy ExpressionAST calc-side tree, moving all calc consumers onto ExpressionIR plus a byte-identical compat renderer | shipped |  |
| H-089 | 2026-07-13 | CONSTRAINT-EXEC | Item 9 | package sealing, contracts, fingerprints | Build production ModelContract/PackageContract sealing so a generated package's identity and integrity can be verified on load | shipped | PDR |
| H-090 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | — | constraint execution lifecycle | Ratify one authoritative end-to-end contract for constraint execution across agentic-mbse, sysml-codegen, and TEAx | unknown | ADR |
| H-091 | 2026-07-19 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 0 | cross-repo version pinning | Pin one compatible agentic-mbse/sysml-codegen/TEAx/fusion-tea/stellarator revision set as the epic's starting baseline | shipped |  |
| H-092 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 8 | constraint catalog identity | Make codegen's embedded constraint catalog the sole schema authority; delete TEAx's parallel reconstructed catalog and its byte-hash fingerprint stand-in | shipped | keep |
| H-093 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 4 | constraint diagnostics and modeled defaults | Diagnostic severity/closed codes, warning-vs-BLOCK ordering, modeled-default fidelity, and the written-reference carry closing SR-A02 | shipped |  |
| H-094 | 2026-07-19 | unknown | Item 3 | constraint extension V11 coverage | Prove extension-time V11 coverage checking is vacuous, then delete it | shipped |  |
| H-095 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 1 | occurrence expansion, demand materialization | Rebuild the occurrence/demand lifecycle thread as one identity-preserving path through public live generation | shipped |  |
| H-096 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 2 | producer resolution, constraint Gate A | Replace three drifted producer-resolution ladders with one shared resolver and make Gate A resolve literal design-attribute constraint actuals | shipped |  |
| H-097 | 2026-07-20 | CONSTRAINT-EXEC | Item 13 | constraint execution lifecycle release proof | Composed public proof for the CONSTRAINT-EXEC lifecycle register: all 41 Appendix C cells pass at a pinned five-repo revision set | shipped |  |
| H-098 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 6 | docs and snapshot version claims | Reconcile public docs and F1 evidence with landed constraint-execution-lifecycle code | shipped |  |
| H-099 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 11 | TEAx constraint evidence | Make TEAx constraint evidence durable: tolerate missing reports, freeze evidence against mutation, pin failure phases, and settle OUTPUT_WRITE | shipped |  |
| H-100 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 12 | grandfathered snapshot gating | Fail closed on grandfathered (unlowered) snapshots before sealing, and delete the dead tracking_key correlation field | shipped |  |
| H-101 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 9 | TEAx study candidate bridge | Make TEAx's study candidate bridge build complete typed mappings for zero, one, or many entry channels, and delete the stale fusion consumer wrapper that patched around the single-channel limit | shipped |  |
| H-102 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 7 | package seal/verify trust chain | Close two trust holes in sealed-package verification and re-seal provenance | shipped | keep |
| H-103 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 5 | snapshot path portability | Make the whole generated output tree checkout-root portable by collapsing three path-normalization schemes into one certified referent | shipped | keep |
| H-104 | 2026-07-20 | CONSTRAINT-LIFECYCLE-REMEDIATION | Item 10 | producer resolution completeness | Prove producer completeness independent of V11 and retire the private stellarator generation bridge in favor of a general resolver fix | shipped | keep |
| H-105 | 2026-07-24 | unknown | — | architecture documentation reconciliation | Reconcile docs/architecture/ with merged main after the CONSTRAINT-LIFECYCLE epic's late changes | shipped |  |
| H-106 | 2026-07-24 | unknown | — | supplied-values resolution, warnings | Add a warning for silent value loss on the nested-occurrence-override calc path | shipped |  |
| H-107 | 2026-08-10 | SOURCE-IDENTITY | Item 4 | occurrence identity manifest | Shadow-layer identity manifest running beside the legacy string resolver, stopped after Phases 1-2 and archived as superseded | superseded | keep |
| H-108 | 2026-08-09 | ELABORATE-FIRST | Item 5 | elaboration front end | Exact-identity elaboration front end built and certified, replacing rendered-name resolution | shipped | ADR |
| H-109 | 2026-08-10 | ELABORATE-FIRST | Item 6 | exact-identity elaboration/projection | Closed remaining exact-identity gaps in the elaborate-then-project route ahead of the Item 7 authority switch | shipped | keep |
| H-110 | 2026-08-14 | ELABORATE-FIRST | Item 7 | generation authority / legacy retirement | Atomic cutover of the codegen front end to the exact instance-graph route, recovered after the first attempt was refused at owner disposition | shipped | ADR |
| H-111 | 2026-08-14 | ELABORATE-FIRST | Item 7 | elaborator authority, v6 snapshot | Atomic cutover from the legacy string-resolution front end to the exact instance-graph elaborator as the sole generation authority | shipped | ADR |
| H-112 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 2 | constraint catalog domain | Constraint usage domain made total: every authored constraint usage now gets exactly one recorded disposition before occurrence expansion | shipped | PDR |
| H-113 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 3 | constraint coverage reporting | Coverage report and TEAx policy so a generated package can no longer claim full satisfaction when most authored feasibility checks were never assessed | shipped | PDR |
| H-114 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 1 | constraint documentation, ADR-009 | Constraint-semantics contract and authoring policy documentation amendments | shipped |  |
| H-115 | 2026-08-14 | CONSTRAINT-SEMANTICS | — | constraint semantics contract | Umbrella spec settling constraint semantics and design-search feasibility across sysml-codegen, agentic-mbse, and teax | shipped | keep |
| H-116 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 6 | calc-def constraint gate | Designed (but did not build) the capability to attach a calc-definition-owned constraint to concrete calculation occurrences | shipped | keep |
| H-117 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 5 | constraint diagnostics, unit annotations | CATF derivative and end-to-end acceptance of the constraint-semantics contract | shipped |  |
| H-118 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 4 | constraint predicate unit annotations | Cure two reproduced defects at the unit-annotation boundary of asserted physics-gate predicates | shipped |  |
| H-119 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 9 | catf_mfe_gated fixture derivations | Execute held ruled intent on the catf_mfe_gated fixture: derive A5/A6 radii, upgrade A9 to a relative-band assert, and retire stale blocked-by-defect PROVENANCE records | shipped |  |
| H-120 | 2026-08-13 | CONSTRAINT-SEMANTICS | Item 8 | elaborator unit selection, projection dedup | Fix unit-lane port metadata defect blocking constraint-formal and computed-attribute entry-point dedup | shipped |  |
| H-121 | 2026-08-14 | CONSTRAINT-SEMANTICS | Item 7 | docs, ADR, product ledger, agent prompts | Sync ADR, product-promise ledger, and agent-facing documentation to the constraint-semantics behavior shipped in Items 1-6, 8, 9 | shipped |  |
| H-122 | 2026-08-16 | ELABORATE-FIRST | Item 8 (bounded child) | reference resolution, occurrence anchoring | Anchor one-segment references to the exact owner's occurrence before falling back to the shared feature slot | shipped | keep |
| H-123 | 2026-08-16 | ELABORATE-FIRST | Item 8 (bounded child) | self-binding detection, exact route | Self-named calculation bindings are refused before generation instead of silently reading their own inputs | shipped | keep |
| H-124 | 2026-08-19 | ELABORATE-FIRST | — | occurrence resolution, evidence extraction | Replace proximity-based occurrence guessing and silent evidence-dropping in extraction/elaboration with exact SysIDE-derived derivation or named refusal | shipped | ADR |
| H-125 | 2026-08-20 | unknown | — | cross-repo PR shipment | Ship the already-closed stop-reinventing-the-parser work to GitHub main across agentic-mbse, sysml-codegen, and fusion-tea, preserving Fusion's exact commit pin | shipped | ADR |
| H-126 | 2026-08-21 | REPO-CLEANUP | Item 1 | decision register scaffolding | Install script-managed ADR and product-promise registers with an owner-grade routing rule for which register a decision belongs in | shipped |  |

---

## Binning (2026-08-23)

Marked rows are the ones worth keeping. Everything unmarked is out: superseded by the
2026-08-14 cutover, already recorded in a register or in code, or process history with no
decision a future agent would get wrong. 21 of 126 rows are marked; several share one
eventual register entry.

**ADR candidates** (builder register, `.project/adr/` — Item 3 authors these):

- **H-124** — the owner's seed, "use the parser, do not create custom patches": occurrence
  resolution derives from SysIDE's exact declaration evidence or refuses by name — never
  proximity, arrival order, or class-name-substring guessing.
- **H-108 + H-110 + H-111** (one entry) — elaborate-first: exact identity (declaration
  UUIDs, occurrence enumeration) over rendered-name/string matching; the legacy
  string-resolution stack was deleted outright, no compat shims, v5 snapshots refused by
  name. Without this a future agent re-adds a "small" name-matching fallback.
- **H-090** — three owner decisions that still bind: no public late-fill or post-build
  graph mutation; a direct literal design attribute is a valid constraint actual (no
  passthrough calculation); codegen's embedded catalog is TEAx's sole schema authority.
- **H-078** — the repo boundary: agentic-mbse owns neutral SysML facts, sysml-codegen owns
  Python rendering and pipeline assembly, dependency strictly one-way. (H-079/080/081 are
  instances of the same ruling.)
- **H-125** — cross-repo merges use explicit merge commits, never squash or rebase, because
  fusion-tea pins exact codegen SHAs; a squash makes the pinned commit unreachable.

**Product-promise candidates** (`.project/product/` — Item 4 authors these):

- **H-112 + H-113** (one entry) — coverage truth: every authored constraint usage gets
  exactly one recorded disposition, and a package can never report full satisfaction while
  authored gates went unassessed. H-112 itself records that no ledger entry was ever
  minted for this — the gap is known-open.
- **H-089** — sealed packages: a generated package's identity and integrity are verifiable
  on load (ModelContract / PackageContract). Check it isn't already covered by ledger
  0001–0004 before filing.

**Keep** (worth remembering; no new artifact — cited from the ADR/PDR bodies or the
test-and-code rationale register, git history is the backstop):

- **H-107** — why the shadow-layer approach was abandoned (artifact-to-artifact gates could
  pass with zero runtime behavior change); this is the Why behind elaborate-first.
- **H-109, H-122, H-123** — exact-identity gap closures and refuse-by-name rulings,
  including the owner ruling that self-binding is a modeling error, never an outer reference.
- **H-016** — SysIDE AST facts that still bite: `:>>` redefinitions are ReferenceUsage, and
  cached_upper_bound is exclusive (reads N+1) — count from the lower bound.
- **H-092, H-102** — TEAx consumes codegen identity as on-disk JSON and never imports
  sysml_codegen; the package-local verifier is authenticated by hash before execution.
- **H-103** — the checkout-root portability contract (two roots, byte-identical output).
  Mechanism since superseded by v6; re-verify before citing.
- **H-104** — the known blind spot: the completeness check can't see a qualifier-dropping
  collapse through channel-tier leaf-name rows; the cross-part gap family is still open.
- **H-115** — the eight owner-ratified constraint rulings from the 2026-08-12 Q&A. The
  headline ones are already homed (ADR-009, product P-001); the rest cite from here.
- **H-116** — the calc-def constraint gate is designed but deliberately unbuilt and
  unauthorized; concrete identity must carry the calculation node, not just the definition.

**Seed check** — all three owner seeds surfaced independently: "use the parser" (H-124),
exact identity / occurrence enumeration (H-108/H-110/H-111/H-122), refuse rather than work
around (H-123/H-124).


## By Epic


### unknown  
*49 item(s), 2026-02-01 → 2026-08-20*


#### H-001 · 2026-02-02 —  Fix three codegen output gaps that blocked generated packages from executing directly under TEAx's execute_pipeline()
`20260202_codegen-runtime-gap-fixes`  ·  subject: **generated output, TEAx runtime execution**  ·  status: **unknown**

A chain-spike codegen run (Item 2 of an end-to-end pipeline derisking epic tracked in the fusion-tea repo) found three gaps requiring manual hand-editing before generated output could run under TEAx: design_params.json generated empty because the design-attribute extractor's path filter defaulted to 'models/designs' and excluded the test model; RootModel[float] exit points had no CUSTOM_SCHEMA_TYPES registration so TEAx's output router had no write handler; and a static, domain-specific FusionParams schema template was unconditionally copied into every generated package regardless of model. The fix broadened the default design-attribute path filter to accept all files (with a crash guard for OperatorExpressions that can't be statically evaluated), wired exit-point primitive types (e.g. Float) into the generated registry's CUSTOM_SCHEMA_TYPES, and deleted the static schemas_ref.py template plus its copy step. A chain-spike SysML model fixture was copied into sysml-codegen's own tests/fixtures/ so the new tests are self-contained.

**Key decisions**
  - extract_design_attributes()'s design_path_filter default changes from 'models/designs' to '' (accept all files); broadening is backward compatible since it is strictly more permissive.
  - _extract_default_value() catches ValueError/TypeError from evaluate_true_static_expression() on OperatorExpressions with feature references and returns None instead of crashing.
  - Exit point primitive types are collected from ComputationGraph.modules and rendered into CUSTOM_SCHEMA_TYPES alongside entry-point parameter-group schemas, importing the Float/Int/etc. aliases from the generated primitives.py.
  - templates/schemas_ref.py (the static FusionParams template) is deleted outright; no generated package should carry domain-specific schema content it doesn't own.

**Supersedes / retires**
  - The unconditional copy of templates/schemas_ref.py (hardcoded FusionParams schema) into every generated package's {package}_schemas.py.

#### H-013 · 2026-02-10 —  Fix seven codegen bugs found during fusion-tea E2E validation, as a blocking prerequisite for the COST-PATTERN epic
`20260210_codegen-bug-fixes`  ·  subject: **codegen bug fixes**  ·  status: **shipped**

E2E validation of the EXPR-CODEGEN and ATTR-EXPR phases in the fusion-tea project needed 7 manual workarounds to produce a correct, executable pipeline from the e2e_attr_expr and solar_battery models. This item fixed all 7: FORMULA module inputs missing from the DesignParams schema; CalcUsage bindings to FORMULA/EXPOSE_PURE attributes wrongly resolving as ENTRY_POINT instead of MODULE_OUTPUT; FORMULA module inputs typed as Float (RootModel) instead of plain float; missing a primitive write handler for multi-output CalcUsage float channels in the generated ExitPoint serialization; --smart-regen not upgrading NotImplementedError stubs to available auto-implementations; sanitize_name() not handling special characters like &, $, @ in SysML names (plus a duplicate _sanitize_name() in extractor.py to eliminate); and missing __init__.py in intermediate generated-package directories across all 4 namespace-creating functions. The spec required design-phase validation of each proposed fix against the real codebase, since the root-cause analyses were written by an AI researcher and could have line-number drift. Was declared blocking for the COST-PATTERN epic (P0 priority) and the acceptance bar was zero manual workarounds on both validation models plus all existing tests (285+ baseline) still green.

**Key decisions**
  - Bug 4's ExitPoint fix follows prior art from fusion_modeling (2024-12-24): multi-output channels carry bare primitives, so the fix is a primitive write handler, not a schema change
  - Bug 5 distinguishes stubs (raise NotImplementedError) from hand-written impls and from AUTO_IMPLEMENTED = True files; only stubs get upgraded by --smart-regen
  - Bug 6 sanitization must not collapse the ADR-003 '__' hierarchy separator -- it applies per name segment, not to full qualified names
  - Bug 7 fix applied to all 4 namespace-creating functions, not just the one that surfaced in validation, to head off latent bugs expected to manifest during COST-PATTERN

#### H-021 · 2026-02-13 — Item 4 Three empirical spikes resolving OutputRegistry design-comment gaps in CHAIN redefinitions, REFERENCE bindings, and design-attribute defaults
`20260213_iteration2-spikes`  ·  subject: **OutputRegistry design spikes**  ·  status: **shipped**

Iteration 1 of the OutputRegistry design left 3 of 6 iteration-2 review comments unresolved because they depended on empirical data not yet gathered: whether :>> CHAIN redefinition RHS is a bare name or resolvable path, whether REFERENCE bindings ever resolve to MODULE_OUTPUT (making SYSML_QN normalization live or dead code), and what format DesignAttributeData.default_value takes for reference-typed attributes. Three read-only diagnostic scripts (Spikes 5-7) ran against solar_battery, e2e_attr_expr, chain_spike, and catf_mfe models and produced a findings document. Results: build_pipeline_context() succeeded on all 4 models (no crash risk), CHAIN redefinition source_path is always populated as DOTTED or BARE (no AST fallback needed), and design-attribute default_value is 126/128 literal but 2/128 are transitive paths requiring Phase 4 handling. All three review-comment issues (9, 11, 12) got data-backed resolutions.

**Key decisions**
  - REFERENCE binding resolution and CHAIN redefinition format were resolved with concrete data rather than assumptions, closing design-comment Issues 9, 11, 12
  - DesignAttributeData.default_value is mostly literal (126/128) but Phase 4 transitive-alias handling is still needed for the 2 path-like cases

#### H-023 · 2026-02-13 —  Spike 8 -- validate OutputRegistry key-format compatibility end to end before implementing it
`20260213_output-registry-spike`  ·  subject: **output registry key formats**  ·  status: **unknown**

The planned OutputRegistry design was to replace 5 ad-hoc backtracker indexes with a single 4-phase registration/resolution protocol, but design review flagged that Phase 1 registration key formats might not match the dotted/double-underscore key formats used by Phase 2-4 alias resolution and backtracker resolve() calls -- the same key-format-mismatch root cause behind the existing bug stream. This spike wrote a diagnostic, read-only script (scripts/spikes/spike_output_registry_e2e.py) that builds a prototype dict-based registry from real extraction of the solar_battery and e2e_attr_expr models, and validates every Phase 1-4 registration and resolution path (CalcUsage outputs, aggregation outputs, FORMULA computed attributes, CHAIN aliases, EXPOSE_PURE aliases, transitive defaults, REFERENCE secondary resolution) against backtracker ground truth. No production code was touched. The folder contains only spec and plan; no findings document was archived alongside them, so the spike's concrete verdict is not recorded here.

**Key decisions**
  - (none stated)

#### H-024 · 2026-02-13 —  Four diagnostic spikes to empirically verify SysIDE AST assumptions behind the planned OutputRegistry design
`20260213_syside-assumption-spikes`  ·  subject: **SysIDE AST key formats**  ·  status: **shipped**

The revised algorithm design (08_algorithm_revised.md) planned an OutputRegistry to replace 5 ad-hoc backtracker indexes, but design review flagged 4 empirical uncertainties about SysIDE parser behavior that could not be resolved by inference alone. This spec commissioned four standalone, read-only diagnostic scripts against real models (solar_battery, e2e_attr_expr, chain_spike, catf_mfe): Spike 1 traces the exact source_path format SysIDE produces for template CalcUsage bindings; Spike 2 checks whether downstream bindings to virtual (template-expanded) CalcUsages use short or qualified instance_name keys; Spike 3 traces the full Bug 2 (EXPOSE_PURE two-hop) resolution chain with actual data to find where key-format mismatch breaks it; Spike 4 quantifies how often CalcUsage output names collide across a model, to decide whether bare-name registration is viable. No pipeline code was modified. The spec's own status line marks it Implementation Complete; the folder here holds only the spec, so the concrete answers/values are not captured in this record.

**Key decisions**
  - (none stated)

#### H-028 · 2026-02-15 —  Runtime spikes validating the root-cause analysis of an aggregation-wiring gap before committing a fix
`20260215_aggregation-fix-validation`  ·  subject: **aggregation registry wiring**  ·  status: **shipped**

A static root-cause analysis had identified 3 bugs explaining why aggregation module inputs failed to resolve as MODULE_OUTPUT (unscoped registry lookup keys, wrong SingletonTerm channel construction, missing scoped registration keys), but the analysis was code-reading only and the proposed fix risked breaking working pipelines if wrong. Three read-only spikes ran against the solar_battery model, dumping the registry, tracing each aggregation input's resolution path, and spot-checking proposed scoped keys against the real registry. Bug 1 (unscoped lookup) was fully confirmed: 0/12 current hits, 12/12 with scoped keys. Bug 2 (SingletonTerm) was not testable since the model has none. Bug 3 was only partially confirmed since top-level aggregations use bare LocalTerms rather than dotted refs. The spike also discovered a new failure mode, CHAIN_PART_MISMATCH (PartDef name vs PartUsage name mismatch, e.g. String_Inverter vs inverter), affecting 4 of 12 inputs, which the proposed scoped-key fix resolves as a side effect. Verdict: GO, proceed to implement the 3-part fix.

**Key decisions**
  - Go decision: proceed to implement the 3-part registry fix (scope the lookup key, add the missing registration key, fix SingletonTerm to use registry-first resolution)
  - Original ~70-input estimate was wrong; only 12 inputs are actually resolvable (the rest are LocalTerms, always entry points)
  - The newly discovered CHAIN_PART_MISMATCH bug does not need a separate fix since the scoped-registry change resolves it as a side effect

#### H-032 · 2026-02-16 —  Add missing __init__.py stubs to the 6 top-level generated output subdirectories
`20260216_bug7-init-py-broader-scope`  ·  subject: **codegen output directory setup**  ·  status: **shipped**

E2E validation runs (e2e_attr_expr_v3 and solar_battery_v3) flagged that generated packages were missing __init__.py in schemas/, modules/, handwritten/, pipelines/, inputs/, and tests/, causing import failures and manual fixups for consumers. This was the last open Bug 7 finding blocking a validation gate decision. The fix added guarded __init__.py stub creation to _setup_output_directories() in cli/__init__.py, excluding output_path/ itself (which _generate_registry() populates separately) and using a not-exists guard so --smart-regen does not clobber existing content. Scope was deliberately narrow: only that one function and its tests, no changes to the top-level registry init or to _ensure_package_init_files().

**Key decisions**
  - Fix lives only in _setup_output_directories() so it applies uniformly across fresh, --overwrite, and --smart-regen runs
  - output_path/ itself is excluded from stub creation because _generate_registry() writes its real registry content there
  - Guard stub creation with a not-exists check so re-runs (smart-regen) never overwrite custom content

#### H-034 · 2026-02-17 —  Conformance tests for the aggregation module factory (component C16), covering SumTerm/SingletonTerm/LocalTerm resolution and literal-value propagation
`20260217_aggregation-module-factory`  ·  subject: **aggregation module factory**  ·  status: **shipped**

C16 tested _build_aggregation_module() in resolution/graph_builder.py, which turns a ScopedAggregationData plus hierarchy redefinitions into a PipelineModule across three term types with different resolution strategies. No production code changed. 32 tests were added to tests/conformance/test_factory_aggregation.py against real solar_battery and issue22 fixture data, all passing, full suite at 1461 passed / 2 skipped / 5 xfailed / 0 failures. The plan's assumption that permitting soft costs were SumTerms was wrong -- they are SingletonTerms -- so several tests were rewired to constructed data instead of natural fixture cases. It documented two REQ-MF-01 gaps ('pure data transformer' contract) as known production behavior rather than fixing them: the factory mutates a shared entry_points dict in place instead of returning entry points, deferred to a later phase.

**Key decisions**
  - Test current mutation-based entry_points behavior as-is; the REQ-MF-01 'pure data transformer' gap is documented for Phase 7 refactoring, not fixed now
  - Confirmed via C12 that resolve_input()/AGG_STRATEGIES is equivalent to the legacy _resolve_aggregation_input_channel() (51/51 refs match); the call-site swap itself stays a deferred follow-up, not a C16 requirement
  - Where no natural fixture case existed (SumTerm literal fallback, LocalTerm entry-point fallback, MANUAL_REQUIRED compilability), tests used constructed data built from real QNs via dataclasses.replace()

#### H-035 · 2026-02-17 — C10 Conformance-test aggregation scoping (PartDef-to-instance expansion, CHAIN aliasing, module_eqn derivation) and add the missing zero-instance warning
`20260217_aggregation-scoping`  ·  subject: **aggregation instance scoping**  ·  status: **shipped**

Three existing functions bridge PartDef-level aggregation expressions to concrete design instances: find_instance_paths_for_partdef() (two resolution strategies), _scope_aggregation_expressions() (one-to-many expansion), and _build_chain_aliases() (CHAIN redefinition aliasing). None had dedicated conformance tests. A spike confirmed real solar_battery data gives full natural coverage (41 qualifying CHAIN redefinitions, both instance-path resolution strategies exercised, scoped output matching the snapshot exactly), so no constructed test data was needed. The only production change was adding a logger.warning() (previously silent/info-only) when an aggregation expression's owning PartDef produces zero design instances, per REQ-AS-08.

**Key decisions**
  - All aggregation-scoping test coverage uses real solar_battery/issue22 fixture data rather than constructed data, since the spike found natural coverage for every requirement including both instance-path strategies and CHAIN alias filters
  - Zero-instance aggregation expressions now log a WARNING (previously only an aggregate INFO count) naming the PartDef and attribute, so a design gap is visible instead of silently vanishing

#### H-036 · 2026-02-17 — C07 Codebase-wide audit enforcing that FeatureChainExpression is always dispatch-checked before OperatorExpression at every dual-check site
`20260217_ast-dispatch-invariant`  ·  subject: **AST dispatch ordering invariant**  ·  status: **shipped**

FeatureChainExpression (FCE) is a subtype of OperatorExpression (OE) in SysIDE's type system, so any dispatch site checking OE before FCE misclassifies FCE nodes -- the root cause of a prior production bug that broke 37 aggregation inputs. This cross-cutting item audited every is_instance() dispatch site across 5 source files, confirmed all 5 dual-check sites already check FCE before OE (the critical invariant held), but found 2 of the 5 sites lacked the required invariant comment and used non-canonical (though still safe, elif-chain) ordering; it added the missing comments and wrote 26 conformance tests including a total-dispatch-site-count guardrail so a future unaudited dispatch site would fail the count test. No behavioral changes were made.

**Key decisions**
  - Elif-chain sites (2 of 5) are accepted with non-canonical FRE/Literal placement as long as the critical FCE-before-OE invariant holds; full reordering was judged higher risk than value and is documented as an accepted deviation, not a defect
  - A total-dispatch-function-count test (8 functions checking 2+ expression types) acts as a guardrail so any future unaudited dispatch site fails the test and forces review
  - Only 2 one-line comment additions were needed; no dispatch logic was reordered or changed

#### H-037 · 2026-02-17 — C11a Conformance-test DependencyBacktracker's current resolution outcomes before the typed-dispatch migration (C11b)
`20260217_backtracker-conformance`  ·  subject: **backtracker resolution outcomes**  ·  status: **shipped**

DependencyBacktracker resolves calc-usage bindings to MODULE_OUTPUT or ENTRY_POINT via the deprecated OutputRegistry.resolve() cascade, and had no requirement-mapped conformance tests, only indirect integration coverage. This item wrote 43 conformance tests verifying resolution outcomes (which channel a binding resolves to, cycle detection, topological order, self-reference guard, key formats) across 6 fixture models, deliberately testing outcomes rather than the resolve() mechanism so the same tests would still hold after the later C11b typed-dispatch rewrite. A spike found 13 of 41 real MODULE_OUTPUT resolutions (12 catf_mfe cross-scope CHAIN + 1 solar_battery REFERENCE secondary) only resolve through the deprecated _compat dict, flagging them as the concrete migration risk for C11b, and discovered that EXPRESSION bindings do not crash the backtracker as previously documented -- they are silently skipped since they lack a source_path -- so a downstream (not backtracker) crash location was corrected in the test suite.

**Key decisions**
  - Tests verify resolution outcomes (which channel resolves), not the internal resolve() mechanism, so the same test suite remains valid evidence after C11b's typed-dispatch rewrite
  - 13 compat-only MODULE_OUTPUT resolutions (12 catf_mfe cross-scope CHAIN, 1 solar_battery REFERENCE secondary) are documented as the concrete risk set for C11b rather than fixed in this item
  - The EXPRESSION-binding crash documented in an earlier audit action was found not to occur in the backtracker itself; EXPRESSION bindings are silently skipped there (no source_path), and the actual crash happens downstream

**Supersedes / retires**
  - The prior belief that expression_binding_probe crashes inside the backtracker; corrected to document silent EXPRESSION-binding skip instead

#### H-038 · 2026-02-17 — C11b Migrate DependencyBacktracker resolution from the deprecated resolve()/_compat cascade to type-directed registry dispatch
`20260217_backtracker-typed-dispatch`  ·  subject: **output registry resolution**  ·  status: **shipped**

DependencyBacktracker and build_output_registry() relied on a deprecated resolve() cascade backed by a _compat dict with ad hoc key formats (Key_A/D/F/bare). This item replaced every resolve() call site across the backtracker, output registry, initialization, and graph_builder with typed scoped/alias/sysml_qn lookups, added a local instance_attr_to_channel helper for Key_A-format canonical names, and deleted _compat, resolve(), register(), and derive_key_c() from OutputRegistry entirely. A spike first verified all 14 previously compat-only resolutions (12 catf_mfe cross-scope CHAIN + 2 solar_battery REFERENCE secondary) still resolve correctly under the typed lookups before the migration was built.

**Key decisions**
  - Phase 2 CHAIN aliases resolve via scoped_lookup directly (canonical_name is already ScopedKey format); Phase 3/4 EXPOSE_PURE and transitive aliases require the local instance_attr_to_channel helper dict (canonical_name is Key_A format)
  - REFERENCE secondary resolution keeps the existing parent_part.leaf key construction and only swaps resolve() for a scoped_lookup-then-alias_lookup cascade, rejecting the originally planned full-path normalization which spike testing showed produced a wrong key for one of two solar_battery cases
  - FORMULA computed-attribute outputs (Key_F) are additionally registered as ScopedKeys during Phase 1c so the REFERENCE secondary path can find them without _compat

**Supersedes / retires**
  - OutputRegistry.resolve() and OutputRegistry.register() convenience methods and the _compat dict entirely removed
  - derive_key_c() static method removed

#### H-039 · 2026-02-17 —  Conformance tests for the CalcUsage module factory (component C14), covering REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08
`20260217_calc-usage-module-factory`  ·  subject: **calc usage module factory**  ·  status: **shipped**

C14 added conformance tests for _build_pipeline_module(), the pure data-transformer function in graph_builder.py that turns a CalcUsageData plus pre-computed binding_resolutions into a PipelineModule, with no resolution logic of its own. Tests verified it never mutates its inputs, fails fast with an ADR-003-violation error on missing bindings, wires every input to exactly one source (module output or entry point), and names outputs correctly for both single- and multi-output calc defs. No fixture model had a natural multi-output calc def, so that path was tested with constructed data built from real qualified names, following the same pattern used earlier for C09. It produced a reusable build_factory_inputs_from_snapshot() helper meant for reuse by the FORMULA and aggregation factory components. 48 tests were written and all passed; full suite was 1397 passed, 5 xfailed, lint clean.

**Key decisions**
  - C14 is conformance-only; the current tuple-mismatch between the checklist's documented interface and the implementation's read-by-reference behavior is accepted as correct per the design intent, with unification deferred to a later phase
  - No fixture model has a multi-output calc def, so that requirement is tested with data constructed from real qualified names rather than a natural fixture
  - build_factory_inputs_from_snapshot() is established as the shared test helper for the remaining module-factory components (FORMULA, aggregation, entry-point classification)

#### H-040 · 2026-02-17 —  Conformance tests for computed attribute classification (component C05) against REQ-CA-01 through REQ-CA-07
`20260217_computed-attribute-conformance`  ·  subject: **computed attribute classifier**  ·  status: **shipped**

C05 tested extraction/computed_attribute_extractor.py, which classifies PartDef/PartUsage attribute expressions into FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, or UNRESOLVABLE and compiles FORMULA patterns to Python. No production code changed. 37 tests were added to tests/conformance/test_computed_attributes.py (the file was already written, untracked, from a prior planning session) and all passed immediately; full suite at 991 passed with 2 pre-existing spike failures unrelated to C05. As with C03, one requirement clause (REQ-CA-05, UNRESOLVABLE classification) has zero coverage across all 6 fixture models, so the test suite instead proves its absence and exercises the code path only via existing mock-based unit tests.

**Key decisions**
  - Document UNRESOLVABLE's zero real-model coverage rather than block on it, following the same precedent set by C03's EXPRESSION binding-type gap
  - Building a lightweight OutputRegistry from snapshot data was sufficient to test _build_attribute_resolution_map(), avoiding the need for full pipeline infrastructure

#### H-041 · 2026-02-17 —  Conformance tests for the data model layer (component C01) against design doc 09-data-models.md
`20260217_data-model-conformance`  ·  subject: **data models**  ·  status: **unknown**

C01 verified every data model, enum, and field referenced in doc 09-data-models.md actually exists in source, is importable from its documented location, has correct fields/types, and constructs with real data. No production code changed. 91 conformance tests were written in tests/conformance/test_data_models.py (well above the ~35 estimate, due to parametrization), all passing, with the full suite at 758 tests and 0 failures. Two doc drift issues were found: CalcUsageData has an undocumented raw_element field, and ScopedAggregationData is miscategorized in the doc as an Analysis Model when it actually lives in extraction/data_models.py. The plan document's own Status field stays at VALIDATE and its commit checklist is unchecked, so completion of the commit/close step isn't confirmed by the text itself even though validation and test results are fully green.

**Key decisions**
  - Source code is authoritative over doc 09 for field lists (per REQ-DM-03); doc drift gets flagged for update rather than treated as a test failure
  - Kept the marker registration scoped to tests/conformance/conftest.py only, to keep conformance concerns isolated from the rest of the suite

#### H-042 · 2026-02-17 —  Prove the three resolution paths (backtracker DFS, FORMULA attribute map, resolve_input strategy chain) agree on wiring decisions (X02)
`20260217_dual-resolution-consistency`  ·  subject: **dual/triple resolution consistency**  ·  status: **shipped**

Conformance-only work item, no production code changes: verified the architectural invariant that separate resolution code paths (backtracker DFS for CalcUsage, the FORMULA attribute resolution map, and resolve_input()'s strategy chain for aggregation) never disagree when resolving the same reference. Extended an existing single-model, single-binding-type test from C12 into a dedicated cross-cutting suite covering all 4 fixture models and both CHAIN and REFERENCE binding types, plus new FORMULA-vs-registry and structural BindingResolution-to-InputSource mapping tests. Found one real asymmetry — the backtracker's REFERENCE Step 2 (leaf + parent-scope lookup) isn't replicated by resolve_input's Strategy B — but classified it as a known capability gap rather than a consistency violation, since it never occurs on aggregation-scope references in practice. Shipped with 20 new conformance tests, full-suite green (1349 passed).

**Key decisions**
  - Treat the backtracker's REFERENCE Step 2 (leaf+parent-scope lookup, not replicated by Strategy B) as a documented capability gap rather than a cross-path consistency failure, since it never triggers on aggregation-scope references in real fixtures
  - No natural three-way overlap exists in fixture data (a reference belongs to exactly one of CalcUsage/FORMULA/Aggregation context), so REQ-DRA-04 is tested as two pairwise comparisons instead of one three-way identity check
  - FORMULA consistency is verified structurally, not empirically discovered: EXPOSE_PURE and FORMULA channels are checked against the same typed OutputRegistry the backtracker itself uses

#### H-043 · 2026-02-17 —  Conformance tests for the entry point classifier (component C17), covering REQ-EPC-01 through REQ-EPC-08
`20260217_entry-point-classifier`  ·  subject: **entry point classification**  ·  status: **shipped**

C17 added conformance tests for _classify_entry_points() and the surrounding entry-point assembly steps in graph_builder.py, with no production code changes. The work verified the three-way classification (DESIGN_ATTRIBUTE, LIBRARY_DEFAULT, USAGE_LITERAL), float conversion, param_group assignment, orphan handling, purity, and that factory-created entry points are never re-classified. It found that solar_battery_model produces zero DESIGN_ATTRIBUTE entry points from the classifier itself (only via factory construction) and switched to catf_mfe_model for those tests, and that param_group can be None at the classifier level but is guaranteed non-None only after full graph assembly. 32 tests were written and all passed; full suite was 1495 passed, 5 xfailed, lint clean.

**Key decisions**
  - REQ-EPC-04 (every EP has a param_group) is a graph-level invariant, not a classifier-level one; the classifier can return param_group=None and orphan handling at graph assembly fixes it
  - catf_mfe_model, not solar_battery_model, is the model that exercises all three classifier-level entry point types
  - REQ-EPC-08 (factory entry points never re-classified) is guaranteed by call ordering in build_computation_graph, verified via static analysis rather than a runtime guard

#### H-044 · 2026-02-17 — C04 Add requirement-traceable conformance tests for the expression compiler (SysIDE AST -> ExpressionAST IR -> Python string, plus compilability verdicts)
`20260217_expression-compiler-conformance`  ·  subject: **expression compiler conformance**  ·  status: **shipped**

The expression compiler (extraction/expression_compiler.py), which converts CalcDef output expression ASTs into Python code and assigns per-output compilability verdicts, already had extensive unit and E2E test coverage but no requirement-tagged conformance test file. This item added 31 conformance tests covering all 7 REQ-EC requirements plus REQ-AST-01 (FCE-before-OE dispatch ordering), using a two-layer strategy: pure IR functions tested with real data (no stubs), and SysIDE-dependent functions tested with a mock adapter at the boundary since extraction snapshots null out AST fields and cannot carry real SysIDE nodes. It also corrected a mis-assignment in the implementation plan: the `.()` invalid-Python-syntax defect attributed to this component actually originates in the aggregation walker's reconstruct_expression(), which the expression compiler does not call, and was reassigned to the hierarchy-resolver/AST-dispatch-invariant components.

**Key decisions**
  - AST fields are permanently null in extraction snapshots, so 'real calc defs' testing means real calc-def metadata (attribute name sets) fed through mock AST nodes, not real AST content -- real AST coverage is left to the existing E2E integration tests
  - The `.()` invalid Python syntax defect previously attributed to this component was found not to originate here (expression compiler never calls reconstruct_expression()) and was reassigned to the hierarchy resolver / AST dispatch invariant components
  - No production code changes; this item is pure conformance-test coverage against an already-correct compiler

**Supersedes / retires**
  - The implementation plan's assignment of the aggregation '.()' syntax defect to this component; reassigned to the hierarchy resolver / AST dispatch invariant work

#### H-045 · 2026-02-17 —  Conformance tests for the SysMLDataExtractor (component C03) against REQ-EXT-01 through REQ-EXT-07
`20260217_extractor-conformance`  ·  subject: **extraction layer**  ·  status: **shipped**

C03 wrote conformance tests proving the extraction layer's dataclasses (CalculationDefinitionData, CalcUsageData, PartDefinitionData, HierarchyExtractionResult) conform to the 7 extraction requirements in design doc 01-extraction.md. No production code changed; this was pure test-writing against existing behavior. 44 tests were added in tests/conformance/test_extractor.py, all passing on first run, with the full suite at 918 tests and 0 failures. Two coverage gaps were found and documented rather than fixed: the EXPRESSION binding type and AST-node preservation are both absent from real fixture data, so those requirement clauses stay untested by real models.

**Key decisions**
  - Treat missing EXPRESSION binding-type coverage and nullified AST fields as documented fixture gaps, not blockers for closing C03
  - output_expression_asts is expected to be None in snapshots (SysIDE Java objects don't serialize), overriding the checklist's literal wording

#### H-046 · 2026-02-17 —  Conformance tests for the FORMULA Module Factory (C15), which builds a PipelineModule from a FORMULA computed attribute
`20260217_formula-module-factory`  ·  subject: **FORMULA module factory**  ·  status: **shipped**

C15 verified that _build_computed_attr_module() in graph_builder.py correctly wires FORMULA computed-attribute inputs to upstream module outputs or new entry points, and stamps is_computed_attribute/compilability flags. This was a conformance-only pass: no production code changed, only a new real-data test suite against attr_expr_probe and solar_battery_model fixtures. Work confirmed two known deviations from the design doc (entry_points dict is mutated rather than returned, and compiled_expression is not copied onto PipelineModule) and left them as documented gaps for a later Phase 7 interface change. Ended DONE with 34 passing / 2 skipped tests and the full suite green.

**Key decisions**
  - Accept entry_points mutation as a known deviation from REQ-MF-01's 'pure data transformer' claim rather than fixing it now; same pattern already accepted in C14, deferred to the Phase 7 return-tuple interface
  - Document PipelineModule.compiled_expression staying None as a gap rather than a bug; downstream stencil generation can read compiled_expression from ComputedAttributeData directly
  - Exclude catf_mfe_model from FORMULA parametrization because both its FORMULA attrs are MANUAL_REQUIRED, not FULLY_COMPILABLE

#### H-047 · 2026-02-17 —  Conformance tests for Graph Assembly (C18): topological sort, channel validation, and final ComputationGraph packing
`20260217_graph-assembly`  ·  subject: **graph assembly / toposort**  ·  status: **shipped**

C18 verified the final pipeline-construction step: _unified_topological_sort() (Kahn's algorithm) orders PipelineModules, _validate_channel_references() checks every wire points to a real output channel, and the result packs into a 3-field ComputationGraph. Tests covered all 7 requirements (REQ-GA-01 through 07), used constructed synthetic modules for cycle-detection and self-dependency paths since no fixture model naturally contains them, and added baseline-JSON comparison against Phase 0 snapshots for solar_battery, chain_spike, and attr_expr_probe. Conformance-only, no production code changed. Ended DONE with 34 passing tests and the full suite green; baseline comparison needed two documented normalizations for known live-vs-snapshot differences.

**Key decisions**
  - Build synthetic PipelineModules (not mocks) to exercise cycle detection and self-dependency guards, since no real fixture model has a circular or self-referencing dependency
  - Normalize two known live-vs-snapshot divergences (CalcUsage compilability field, entry_point_groups parameter ordering) when comparing against baseline JSON rather than treating them as regressions
  - Use plain json.load() + dict comparison for baseline checking instead of the originally planned model_validate_json(), to allow targeted normalization

#### H-048 · 2026-02-17 —  Conformance tests for the Hierarchy Resolver (C06), which extracts SysML redefinition, multiplicity, and aggregation-expression structure
`20260217_hierarchy-resolver-conformance`  ·  subject: **hierarchy resolver extraction**  ·  status: **shipped**

C06 added real-data conformance tests for extraction/hierarchy_resolver.py against REQ-HR-01 through REQ-HR-07, covering redefinition classification (LITERAL/CHAIN/EXPRESSION), deep-path design overrides, multiplicity extraction, FCE-before-OE dispatch ordering, and sum-term/alias detection. Conformance-only: no production code changed. Since AST fields are nulled out in extraction snapshots, tests verified output properties of already-extracted data plus static AST analysis of the source, rather than re-running extraction. Ended DONE with 36 passing tests and the full suite green; also flagged stale COMPONENT_CHECKLIST doc references for correction.

**Key decisions**
  - Use design doc 25-hierarchy-resolver.md (not the checklist's 01-extraction.md) as the authoritative REQ-HR source, and flag the checklist reference as wrong
  - Interpret the checklist's ambiguous 'template detection (is_template)' AC as verifying part_usage_names mapping instead, since is_template doesn't exist in this module
  - Document REQ-HR-07 alias detection as an untestable positive case (zero fixture coverage) rather than block on it, since all fixture aggregation expressions have empty aliases

#### H-049 · 2026-02-17 — C12 Extract aggregation input resolution into a standalone resolve_input() strategy-chain function
`20260217_input-resolver`  ·  subject: **aggregation input resolver**  ·  status: **shipped**

Aggregation SumTerm/SingletonTerm input resolution logic was scattered inline through _resolve_aggregation_input_channel() and _build_aggregation_module() in graph_builder.py. This item factored it into a new resolution/input_resolver.py module: a frozen ResolutionContext dataclass, four ordered strategy callables (ScopedRegistryLookup, ChainRedefinitionFollow, SysMLQNLookup, DesignAttributeLookup), and a resolve_input() function that tries them in order with a self-reference guard and an entry-point fallback that never raises. A spike over 51 real aggregation refs across 3 models confirmed the design doc's A-before-C strategy ordering is strictly correct (zero conflicts, A resolves 94% of refs) and that Strategy B (SysML QN) and Strategy D (design-attribute dedup) are currently zero-exercise but implemented for completeness. Wiring resolve_input() into graph_builder.py's actual call sites was explicitly deferred to a later component (C16); this item only proved the new function produces identical results to the existing inline logic via a regression test.

**Key decisions**
  - Strategy order is [ScopedRegistryLookup, ChainRedefinitionFollow, SysMLQNLookup, DesignAttributeLookup] (A before C), confirmed empirically safe and strictly more efficient than the current C-first code
  - resolve_input() requires an explicit strategies argument with no default STANDARD_STRATEGIES, since no non-aggregation caller was identified
  - Strategy D (design-attribute lookup) is implemented as a no-op returning None; it cannot return a CanonicalChannel and its real entry-point-deduplication value requires factory-level changes out of this item's scope
  - Actually wiring resolve_input() into graph_builder.py's _build_aggregation_module() call sites is deferred to C16 (Aggregation Module Factory) to avoid premature coupling; C12 only proves behavioral equivalence

#### H-050 · 2026-02-17 — C02 Conformance-test the identifier/naming utility functions (EQN, PQN, module name/type, channel name, Key_C, sanitize_name)
`20260217_naming-conventions`  ·  subject: **identifier naming utilities**  ·  status: **shipped**

The pipeline's identifier formats (SysML QN to EQN conversion, PQN construction, module name/type derivation, channel naming, Key_C derivation, and the sanitize_name() Python-safety transform) had only 13 test cases covering sanitize_name() alone, despite being the foundation every other component depends on for naming. This item wrote 46 conformance tests across all 7 documented requirements using real qualified names harvested from fixture models, with SysIDE adapter boundary stubs (FakeElement/FakeOwnership) standing in for AST ownership-chain traversal where build_element_qualified_name() needs live SysIDE elements. No source code changes were needed; all functions were already correct. The item surfaced two minor gaps for later attention: sanitize_name() only reserves 6 of Python's 35 keywords, and one existing test elsewhere in the suite calls derive_module_type() with malformed mixed __/:: separators.

**Key decisions**
  - No production code changes; this item is pure conformance-test coverage locking down already-correct naming functions
  - sanitize_name()'s reserved-word list covering only 6 of 35 Python keywords is flagged as a documented gap, not fixed, since no fixture model currently uses the missing keywords as element names
  - derive_key_c() is tested here (C02) rather than deferred entirely to the output registry component, since the design doc defines Key_C derivation as a naming convention

#### H-051 · 2026-02-17 —  Conformance tests for orchestrator step ordering (component C19), covering build_pipeline_context() composition and pipeline-level invariants
`20260217_orchestrator-step-ordering`  ·  subject: **pipeline orchestrator**  ·  status: **shipped**

C19 verified that generation/initialization.py's build_pipeline_context() calls extraction, analysis, resolution, and assembly steps in the right dependency order and that the resulting ComputationGraph satisfies pipeline-level invariants (every input wired, every producer channel declared, valid topological sort, entry points classified). No production code changed. Because the real orchestrator needs a live SysIDE JVM, tests combined static-analysis checks of call ordering with snapshot-driven reconstruction of the full pipeline. 39 tests were added to tests/conformance/test_orchestrator.py, all passing, full suite at 1571 passed / 2 skipped / 5 xfailed / 0 failures, committed at 29f1af8. It documented (but did not fix) a known violation of REQ-PIPE-07: generation modules still import from extraction, deferred to a later phase (7.6).

**Key decisions**
  - REQ-PIPE-07's generation-side fix (removing extraction imports from generation modules) is out of scope for C19; C19 only records the current violation count as a baseline for Phase 7.6
  - FORMULA-removal safety-net tests use constructed overlap data because real fixture models have zero overlap between FORMULA and design-attribute qualified names
  - CHAIN alias unresolvable-warning path is tested with constructed data since no fixture model naturally produces an unresolvable alias

#### H-052 · 2026-02-17 — C08 Refactor OutputRegistry from a single flat dict[str,str] resolve() into three typed registries (scoped, SysML QN, alias)
`20260217_output-registry`  ·  subject: **output registry typed lookups**  ·  status: **shipped**

OutputRegistry used one flat _index dict with a single resolve(str) method serving several deprecated ad hoc key formats. This item added five NewType identifier wrappers (ScopedKey, CanonicalChannel, SysMLQN, EQN, PQN), split the registry into three typed dicts with their own typed lookup methods, and refactored build_output_registry() to register through the typed methods. A spike found that fully eliminating the deprecated key formats broke the backtracker's resolution, since some resolution paths (Phase 3/4 aliases, backtracker Step 1) are load-bearing on the old Key_A/Key_F key formats; the resolution was to move those dead keys into a separate _compat dict, kept alive only for the deprecated resolve() pass-through, while the new typed registries stay clean. Updating the backtracker and graph_builder to stop calling resolve() and drop _compat entirely was explicitly deferred to later components (C11, C12).

**Key decisions**
  - resolve() is kept as a deprecated pass-through (scoped -> sysml_qn -> alias -> compat) rather than removed, because 8 production call sites and 150+ tests still depend on it; full removal is deferred to C11/C12
  - Dead legacy key formats (Key_A, Key_D, Key_E full, Key_F, bare) are moved into a separate _compat dict, invisible to the new typed lookup methods but still reachable via resolve()
  - build_output_registry() itself is refactored to register through the new typed methods and stop registering dead keys directly

#### H-053 · 2026-02-17 —  Conformance tests for ParameterGroupDeriver (C13), which groups pipeline entry points into JSON input file groups by source file
`20260217_parameter-group-deriver`  ·  subject: **parameter group deriver**  ·  status: **shipped**

C13 added real-data conformance tests for analysis/parameter_groups.py, covering the 4-index precedence system (attr, binding, unbound, literal), REQ-PGD-01 through 07: unique parameter assignment, file-based grouping, entry-point filtering, classify() lookup, default-value resolution, and _params/PascalCase naming conventions. Conformance-only, no production code changed. Ended DONE with 30 passing tests against solar_battery, chain_spike, and catf_mfe fixtures, and the full suite green.

**Key decisions**
  - Treat classify() returning None for synthetic FORMULA/aggregation-generated qnames as by-design, not a gap — the deriver only guarantees uniqueness among its own indexes, and graph_builder's orphan-to-system_design fallback handles the rest
  - Correct plan assumption that chain_spike has 2 source files; it has only 1 (design.sysml), so the group-count test target was adjusted
  - Rename planned test class names from TestREQ_PGD_* to TestReqPgd* to satisfy ruff N801 PascalCase rule

#### H-054 · 2026-02-17 — Phase 0 Build the license-free conformance test harness: extraction snapshots, pipeline JSON/YAML baselines, and shared fixtures
`20260217_phase-0-test-infrastructure`  ·  subject: **test infrastructure, snapshots**  ·  status: **shipped**

The planned component-by-component refactor of the resolution/generation pipeline needed a way to write and run conformance tests without a live SysIDE/JVM license. This foundational item designed the serialization boundary for extraction dataclasses (nullifying non-serializable AST/Java-object fields while preserving computed properties), built capture and load helpers, generated extraction_snapshot.json fixtures for 6 models, captured ComputationGraph JSON and generated __init__.py baselines for 4 models for diff-based regression detection, and wired session-scoped snapshot fixtures plus req/baseline pytest markers into the conformance conftest. All three sub-phases completed with the full suite passing (874 tests) and the req marker collecting 205+ conformance tests with no JVM dependency.

**Key decisions**
  - Non-serializable SysIDE AST/Java-object fields (expression ASTs, raw elements) are nulled out in snapshots rather than lossily serialized; tests needing real ASTs (e.g. the expression compiler) use live extraction instead
  - Snapshot serialization stores fixture-relative paths, not absolute paths, so diffs are machine-independent
  - Baseline drift is treated as intentional-and-documented via re-running the capture script, not silently accepted

#### H-055 · 2026-02-17 —  Checkpoint 5 end-to-end pipeline validation (step 5.2 / C19 companion) proving the refactored pipeline matches Phase 0 baselines
`20260217_pipeline-e2e-validation`  ·  subject: **pipeline end-to-end output**  ·  status: **shipped**

Step 5.2 was the Checkpoint 5 gate: run the full refactored pipeline (snapshots to registry to backtracker to classifier to module factories to graph assembly) end-to-end on multiple fixture models and check the resulting ComputationGraphs against Phase 0 baselines. No production code changed. It added a missing catf_mfe baseline and wrote 16 tests in tests/conformance/test_pipeline_e2e.py covering REQ-PIPE-01 through REQ-PIPE-07, all passing on first run, with the full suite at 1587 passed / 2 skipped / 5 xfailed / 0 failures. This closed the last gap versus the existing C18 (baseline comparisons) and C19 (orchestrator invariant) conformance tests, which together already covered most of the same ground.

**Key decisions**
  - Reused/duplicated C18's baseline-comparison helper as a module-level function rather than extracting a shared helper, since only two consumers existed
  - Scoped REQ-PIPE-06 (all three module types present) to solar_battery only, since catf_mfe legitimately has CalcUsage modules alone

#### H-056 · 2026-02-17 —  Design-intent spec replacing the flat string-keyed OutputRegistry with typed identifier wrappers and separate typed registries
`20260217_typed-registry-refactor`  ·  subject: **typed registry design**  ·  status: **shipped**

The OutputRegistry was a single dict[str, str] holding ~12 ambiguous key formats (Key_A, Key_D, Key_E, Key_F, bare names) resolved by a cascade of dict.get() calls, so a lookup succeeding gave no guarantee it hit the right key rather than an accidental collision; a spike proved Key_A had zero correct hits across all 6 models and that implementing REQ-BT-08 as literally written would break 12 correct resolutions. This item was scoped as design-intent documents only (explicitly not a source code change): it updated design docs 10, 11, 15, 24, 03 and authored a new doc 27 specifying typed identifier wrappers (SysMLQN, EQN, PQN, CanonicalChannel, ScopedKey) with validating constructors, separate typed registries in place of the flat dict, elimination of the 5 ambiguous key formats, and binding-type-directed dispatch (CHAIN vs REFERENCE) replacing the try-everything cascade. The plan step verified all 9 doc-27 acceptance criteria by document inspection and cross-consistency against the 7 amended downstream docs; actual code implementation was deferred to a later item.

**Key decisions**
  - This item's deliverable is design-intent documents only; production source code is explicitly out of scope, to be implemented against the updated design later
  - Key_A, Key_D, Key_E, Key_F, and bare keys are eliminated as ambiguous key formats, backed by a spike showing zero correct hits for Key_A across 6 models
  - Resolution dispatches on BindingType (CHAIN vs REFERENCE) to select the correct typed registry rather than trying every registry in a cascade
  - If an eliminated key format is ever load-bearing for an untested model, it must be made unique rather than reintroduced in ambiguous form (FR-6, no exceptions)

**Supersedes / retires**
  - REQ-OR-02, REQ-OR-05, REQ-OR-08 in 10-output-registry.md
  - REQ-BT-08 in 11-analysis-backtracker.md
  - REQ-NC-07 in 15-naming-conventions.md
  - REQ-DRA-03 in 24-dual-resolution-architecture.md
  - REQ-RES-07 in 03-resolution-overview.md

#### H-057 · 2026-02-17 — C09 Conformance-test the existing virtual-binding rewrite function that applies :>> design overrides to virtual CalcUsage bindings
`20260217_virtual-binding-rewrite`  ·  subject: **virtual binding override rewrite**  ·  status: **shipped**

_rewrite_virtual_bindings() patches virtual CalcUsage bindings in-place using :>> design overrides (LITERAL value flips, CHAIN source_path replacement) so downstream resolution sees design-intent values instead of template references, but had no dedicated conformance tests. Since extraction snapshots are captured post-rewrite, a spike proved a reliable strategy: reconstruct pre-rewrite REFERENCE bindings from the snapshot's design_overrides by reversing the QN format, then re-apply the rewrite and verify the mutation. All 13 solar_battery overrides (all LITERAL, all deep-path) were reconstructed and verified correctly; CHAIN, flat-override, template-skip, and EXPRESSION-skip paths had no natural fixture coverage across any of the 6 models and were tested with constructed data using real names. All 38 tests passed against the existing implementation with zero production code changes required.

**Key decisions**
  - No production code changes were needed; this item is pure conformance-test coverage that locks the existing implementation down ahead of a later structural extraction to orchestration/
  - Zero CHAIN, flat, or EXPRESSION-type design overrides exist in any of the 6 fixture models, so those code paths are tested only with constructed data, not real models -- documented as a fixture coverage gap
  - EXPRESSION-type overrides are confirmed to silently no-op (the rewrite function only handles LITERAL and CHAIN), matching the design intent doc but previously undocumented

#### H-058 · 2026-02-18 —  Conformance tests for the JSON template and parameter schema generator (component C25), covering REQ-GEN-05 and REQ-PY-07
`20260218_json-template-generator`  ·  subject: **JSON template and schema generation**  ·  status: **shipped**

C25 added conformance tests for the graph-only JSON template and Pydantic schema generation functions in generation/entry_point.py (generate_all_derived_jsons_from_graph and generate_all_derived_schemas_from_graph), which render one JSON template and one schema file per ParameterGroup. No production code changed. Tests verified file counts, filenames, that JSON values match entry point defaults, that entries with a None default are correctly excluded from JSON but still present in the schema, and that generated schema files parse as valid Python with matching class names and fields. It confirmed that python_type is always float across all real fixture data, so the type-mapping fallback path is defensive but never exercised. 28 test items (15 cases across 2 models) were written and all passed; full suite was 1733 passed, 6 xfailed, lint clean.

**Key decisions**
  - C25's scope is the JSON/schema file generation itself (REQ-GEN-05); REQ-PY-07's YAML-reference aspect is left to C20 and only cross-checked here by file count
  - Entry points with default_value=None are correctly omitted from JSON templates but still declared (with default=None) in the Pydantic schema; this is confirmed intentional behavior, not a bug

#### H-059 · 2026-02-18 —  Fix the module registry generator (C24) so aggregation import paths and class names stop colliding
`20260218_module-registry-generator`  ·  subject: **module registry generator**  ·  status: **shipped**

The generator that writes the pipeline's __init__.py (imports, create_registry() call, CUSTOM_SCHEMA_TYPES) had two bugs: aggregation import paths used a library-scoped qualified name that produced malformed directory paths, and 20 aggregation modules across 4 assemblies collapsed onto 5 shared class names with silent dict overwrite. Fixed the QN derivation to use the design-scoped module EQN, and added collision detection plus aliased imports keyed off the parent assembly segment. Left a known mismatch in graph_builder's aggregation module_type derivation (still library-scoped) as a documented cross-component gap for a later phase. Shipped with 22 new conformance tests and full-suite green (1675 passed).

**Key decisions**
  - Use agg.module_eqn.replace('__','::') instead of agg.expression.owning_part_qn for aggregation import paths (design-scoped, matches filesystem layout)
  - Add collision detection + PascalCase-parent-segment aliasing before rendering, rather than allowing module_type_override dict keys to silently overwrite
  - Defer the matching fix in graph_builder.py (module_type still library-scoped for aggregation) to a later phase rather than widen this component's scope
  - Interpret 'design-scoped' requirement as: all module types use the same QN-to-path derivation pipeline, not that every type's QN itself must be design-scoped (CalcUsage legitimately stays library-scoped)

#### H-060 · 2026-02-18 —  Conformance tests for the TEAx module wrapper generator (component C21), covering REQ-GEN-02
`20260218_module-wrapper-generator`  ·  subject: **module wrapper generation**  ·  status: **shipped**

C21 added conformance tests for generate_teax_module() in generation/modules.py, the function that renders TEAx module wrapper Python files for CalcUsage modules (FORMULA and aggregation wrappers are generated elsewhere in cli/__init__.py and were out of scope). No production code changed. Tests verified generated code parses as valid Python, class names match PipelineModule.module_type, input/output wiring matches the calc def, and type mapping is consistent with the graph builder's own type mapping. It confirmed teax_module_stub.py.jinja2 is dead code (unreferenced anywhere) and found no divergence between the generator's _map_input_type() and the graph builder's type mapping, despite that being flagged as a known duplication risk (REQ-GEN-06). 19 tests were written and all passed; full suite was 1633 passed, lint clean.

**Key decisions**
  - C21 scope is limited to generate_teax_module() (the CalcUsage path); FORMULA and aggregation wrapper generation in cli/__init__.py is left to a later consolidation
  - teax_module_stub.py.jinja2 confirmed dead (no source references) and flagged safe to delete in a later cleanup pass
  - No type-mapping divergence found between modules.py's _map_input_type() and the graph builder's python_type, so the REQ-GEN-06 consistency concern did not need a fix here

#### H-061 · 2026-02-18 —  Fix two upstream graph_builder bugs (Bug 9: missing param_group prefix, Bug 10: int instead of float) surfaced by the Pipeline YAML generator (C20)
`20260218_pipeline-yaml-generator`  ·  subject: **pipeline YAML generator**  ·  status: **shipped**

generation/pipeline.py (the 'gold standard' generator — consumes only ComputationGraph, no raw extraction data) was itself correct, but two upstream bugs in resolution/graph_builder.py corrupted its output. Bug 9: orphan entry points created during Step 6.8 never had their param_group written back onto the module input's InputSource, so the YAML generator fell back to an unprefixed qualified name. Bug 10: aggregation multiplicity inputs were hardcoded to python_type="int", the only int usage in a TEAx pipeline that requires float everywhere. Fixed both with a small Step 6.9 (propagate param_group after orphan handling) and a one-line type change, then regenerated the solar_battery YAML and ComputationGraph JSON baselines (the only ones affected — 28 entry point sources gained the system_design. prefix, ~12 multiplicity lines changed int to float). Shipped with 27 new conformance tests and full-suite green (1614 passed).

**Key decisions**
  - Fix both upstream bugs in graph_builder.py rather than working around them in the YAML template, since the ComputationGraph itself was carrying wrong data (param_group=None, python_type="int") consumed by other readers too
  - Only solar_battery's baselines needed regeneration — the other fixture models have no aggregation with named multiplicity attributes, so they were structurally immune to both bugs
  - sample_model YAML baseline (tested via the live-extraction path in test_e2e_output_registry.py) was left unregenerated since it has no aggregation and the fix can't affect it

**Supersedes / retires**
  - graph_builder.py's unprefixed entry-point param_group fallback for orphan entry points (Bug 9)
  - graph_builder.py's hardcoded python_type="int" for aggregation multiplicity inputs (Bug 10)

#### H-062 · 2026-02-18 —  Conformance tests for the Schema Generator (C22), which produces Pydantic MultiOutput classes for multi-output calc defs
`20260218_schema-generator`  ·  subject: **output schema generator**  ·  status: **shipped**

C22 added real-data conformance tests for generation/schemas.py against REQ-OSR-01 through 07: single-output modules use field_name 'root', 2+ output calc defs get a generated MultiOutput class, field names and types match the source calc def and the ComputationGraph, and aggregation/FORMULA modules are always single-output. Conformance-only, no production code changed. Testing confirmed a real bug (Bug 11): the Permitting_Interconnect fixture's generated schema has default=0.0 on 4 output fields, violating REQ-OSR-05 which forbids defaults on output fields; this was recorded as an xfail rather than fixed, since Phase 6 was conformance-only. Ended DONE with 20 passing + 1 xfailed test and the full suite green.

**Key decisions**
  - Confirm and document Bug 11 (output fields carrying default=0.0, violating REQ-OSR-05) as an xfail rather than fix it, because this phase is scoped to conformance testing only, not production code changes
  - Verify REQ-OSR-01/06/07 (root field, aggregation/FORMULA single-output invariant, PQN channel format) at the ComputationGraph level rather than the schema-generator level, since the schema generator itself never sees aggregation/FORMULA modules
  - Note _map_output_type() as one of four duplicate type-mapping implementations (REQ-GEN-06 violation), to be resolved later by the X01 type-mapping consolidation

#### H-063 · 2026-02-18 —  Conformance tests for the Stencil Generator + Smart Regen (C23): auto-impl vs stub generation and handwritten-code preservation
`20260218_stencil-smart-regen`  ·  subject: **stencil generation / smart regen**  ·  status: **shipped**

C23 added real-data conformance tests covering stencil generation (REQ-GEN-04: FULLY_COMPILABLE calc defs get auto-implemented code, others get NotImplementedError stubs) and smart regen preservation (REQ-SR-01 through 07: two-level signature matching, the 4-case regenerate decision tree, 3-condition stub-to-auto-impl upgrade, pre-regen backups, and the aggregation/FORMULA bypass of smart regen entirely). Because extraction snapshots null out compilation_results, tests constructed real CalcDefCompilationResult objects from real calc_def metadata to exercise the auto-impl path, and used tmp_path for real filesystem interaction on the preservation logic. Conformance-only, no production code changed. Ended DONE with 30 passing tests and the full suite green; also caught a stale function name in the plan (_generate_implementation_stencils renamed to _generate_stencils).

**Key decisions**
  - Construct real CalcDefCompilationResult objects from real calc_def output_attributes (not mocks) to work around extraction snapshots nulling compilation_results
  - Test the --preserve-handwritten flag and the aggregation/FORMULA smart-regen bypass via static source analysis rather than runtime behavior, since the gating logic lives inline in cli/__init__.py

#### H-064 · 2026-02-19 —  Consolidate SysML-to-Python type mapping (X01), which had 6 independently drifted copies, into one shared module
`20260219_type-mapping-consolidation`  ·  subject: **SysML-to-Python type mapping**  ·  status: **shipped**

The Real/Integer/Boolean/String to float/int/bool/str mapping existed as 6 separate copies across the generators (modules.py, entry_point.py, schemas.py x2, stencils.py, registry.py), each with subtly different signatures, ScalarValues:: prefix handling, and unknown-type fallback behavior. Created a single generation/type_mapping.py with map_sysml_type_to_python() and a derived map_sysml_type_to_rootmodel_wrapper() (registry.py needed wrapper type names like Float/Int, not primitives), then deleted all 6 duplicate definitions and repointed call sites. Chose pass-through for unknown types (not silent default-to-float) so mismatches stay visible; confirmed via existing fixture data that no real model exercises the unknown-type path, so the behavior change is inert in practice. Left extraction/extractor.py's separate type mapping untouched since it's a different layer. Shipped with 20 new conformance tests and full-suite green (1753 passed), no baseline changes.

**Key decisions**
  - Two public functions: map_sysml_type_to_python (canonical primitive mapping) and map_sysml_type_to_rootmodel_wrapper (derives from the primitive mapping) — registry.py's wrapper-type mapping is a distinct semantic function, not folded into the primitive one
  - Canonical unknown-type behavior is pass-through with a warning log, not silent default-to-float, even though this changes entry_point.py and schemas.py behavior — justified because no real fixture data hits that path
  - extraction/extractor.py's type mapping is left separate — it's a different layer (produces sysml_type values) from the generation-layer mapping (consumes them)
  - modules.py's call site changes from passing an AttributeInfo object to passing attr.sysml_type string, matching the other 5 copies' signature

**Supersedes / retires**
  - 6 independently-defined _map_input_type/_map_output_type/_map_sysml_to_python_type copies across modules.py, entry_point.py, schemas.py (x2), stencils.py, registry.py

#### H-065 · 2026-02-20 — Bug 11 Fix generated MultiOutput Pydantic schemas rendering spurious defaults on output fields, breaking TEAx output-channel detection
`20260220_bug11`  ·  subject: **generated output schema defaults**  ·  status: **shipped**

Generated MultiOutput schemas rendered Field(default=0.0, ...) on output fields whenever the SysML model had a fixed bound value (e.g. `out attribute material_cost : Real = 0.0`), because the extractor conflated a permanent fixed binding (isDefault=false) with an actual overridable SysML default (isDefault=true) and passed the value through unfiltered to schema generation. Since TEAx's create_registry() treats a Pydantic field with a default as optional and skips registering it as a pipeline output, this caused generated output channels to silently disappear from pipeline wiring with no error. The fix was a one-line change in generation/schemas.py forcing output-field defaults to always render as None (the generation layer's job to enforce REQ-OSR-05), leaving the misclassified extraction-layer default_value data intact and unrepurposed for a future upstream fix. The affected xfail test was hardened into a real assertion and extended from one model to all four.

**Key decisions**
  - Fix applied at the generation layer (schemas.py), not extraction or resolution, so the misclassified extraction data is preserved for a later upstream fix rather than discarded; only 1 line changes and zero baseline JSONs are affected
  - The underlying extraction bug (conflating fixed bound values with SysML defaults) is explicitly deferred as future work, not fixed in this item
  - The affected test moved from a soft pytest.xfail to a hard assertion and was extended from solar_battery only to all four fixture models

**Supersedes / retires**
  - The prior xfail-marked test acknowledging Bug 11 as known-broken; it now asserts the correct behavior as a hard requirement

#### H-066 · 2026-02-20 — C26 Expand PipelineModule/ModuleInput/ModuleOutput with metadata fields so generators can run from the ComputationGraph alone
`20260220_pipeline-module-migration`  ·  subject: **pipeline module data model**  ·  status: **unknown**

Component C26 of a larger refactor (doc 26, checklist-tracked) added metadata fields (description, default_value, unit, source_file, source_line, calc_def_name, calc_def_qualified_name, doc_comment, calc_expressions, is_computed_attribute, is_aggregation) to the three pipeline data models and built parallel _from_graph() generator variants intended to produce byte-identical output to the existing generators, removing the need for back-references to CalculationDefinitionData. Debug analysis found 13 failing tests traced to three root causes: single-output modules losing their real attribute name behind a placeholder field_name of 'root' (an existing helper, _output_attr_name(), existed but was never wired in); FORMULA/aggregation import ordering diverging between snapshot order (old path) and topological order (new path) in the registry generator; and conformance/baseline tests asserting stale field sets and pre-expansion JSON baselines. The debug doc recorded root causes and a fix sequence as analysis only, without applying fixes itself. It also flagged two known gaps deferred to a later phase (7.6): the _from_graph() stencil variant always produces stubs rather than dispatching into auto-implementation, and FORMULA/aggregation modules aren't covered by the old-vs-new identity tests.

**Key decisions**
  - Field expansion done as Phase 1-2 of the doc-26 migration strategy: add fields, populate during graph building, add parallel _from_graph() generators before switching call sites (deferred to phase 7.6)
  - Design doc undercounted required fields by 3 (source_file, source_line, unit on ModuleOutput); these were added after generator-consumption analysis to satisfy REQ-PMM-04 byte-identical output

#### H-067 · 2026-02-20 —  Remove confirmed-dead code paths (step 7.4) plus fix one deferred bug (endswith false positive)
`20260220_dead-code-removal`  ·  subject: **dead code cleanup**  ·  status: **shipped**

Step 7.4 triaged twelve candidate dead-code items collected from earlier research and conformance work, found seven already removed and one already absent, and acted on the remaining four: deleted the normalized SysML-QN fallback in input_resolver.py's Strategy B (kept the live direct-lookup path), deleted the mirrored Step 1b normalization in dependency_backtracker.py, replaced a bare-name fallback in initialization.py's virtual binding rewrite with a loud ValueError, and deleted the unreferenced teax_module_stub.py.jinja2 template. It also fixed a previously deferred bug, an endswith() false positive in hierarchy_resolver.py's alias detection, bundling it in as a one-line fix. Six new conformance tests lock in the removals; ten existing tests needed updates because they used since-proven-unrealistic bare-name test data. Full suite went from 1780 to 1783 tests, all passing, no baseline output changes.

**Key decisions**
  - Only the normalized-fallback sub-path of Strategy B is dead; the direct SysML QN lookup is live (exercised by attr_expr_probe) and was kept
  - Bare-name source_paths are proven never to occur in real models, so the VBR fallback was replaced with a hard ValueError rather than silently removed
  - The endswith() false-positive fix (Deferred Issue #11) was folded into this cleanup step rather than deferred further, since it was a one-line, risk-free change

**Supersedes / retires**
  - Strategy B's normalized SysML-QN fallback in input_resolver.py
  - dependency_backtracker.py's Step 1b QN normalization block
  - the bare-name fallback branch in initialization.py's _rewrite_virtual_bindings
  - templates/teax_module_stub.py.jinja2

#### H-068 · 2026-02-20 —  Make the three module factory functions pure (return entry points instead of mutating a shared dict)
`20260220_factory-purity-refactor`  ·  subject: **module factory functions**  ·  status: **shipped**

The FORMULA and aggregation module factories in resolution/graph_builder.py mutated a shared entry_points dict in place (7 mutation sites total); the CalcUsage factory was already pure but had a mismatched return type. Refactored all three to return (PipelineModule, dict[str, EntryPoint]), with the caller (build_computation_graph) merging returned entry points into the shared dict inside each loop so later calls in the same pass still see earlier ones. This was a purely mechanical, behavior-preserving refactor: ComputationGraph output was verified byte-identical before and after. Shipped with 10 new conformance tests and full-suite green (1791 passed, up from 1783).

**Key decisions**
  - All three factories return (PipelineModule, dict[str, EntryPoint]) for interface uniformity, even the CalcUsage factory which never creates entry points (returns empty dict)
  - Caller merges returned entry-point dicts into the shared dict inside the loop, not after all calls, so later factory calls in the same step see entry points created by earlier ones
  - EP backfill (updating an existing entry point's default) reads the shared dict read-only and writes an updated copy to the local new_entry_points dict, letting the caller's merge overwrite

**Supersedes / retires**
  - Mutation of the shared entry_points dict from inside _build_computed_attr_module() and _build_aggregation_module()

#### H-069 · 2026-02-20 —  Delete the naming/identifier-types backward-compat shim modules and point all importers at core/ (Step 7.3)
`20260220_naming-consolidation`  ·  subject: **naming and identifier-type utilities**  ·  status: **shipped**

analysis/qualified_names.py and resolution/identifier_types.py were backward-compatibility re-export shims left over from an earlier move of the real implementations into core/qualified_names.py and core/identifier_types.py. Migrated the 9 remaining importers (5 production files, 1 internal, 3 test files) to import from core/ directly, stripped the now-dead re-export blocks from analysis/__init__.py and resolution/__init__.py, and deleted both shim files. Also investigated two deferred issues from earlier research: the 'two BindingInfo classes' turned out to be legitimately different classes in different packages (local dataclass with AST refs vs. upstream Pydantic type-only reference) and was ruled out-of-scope as a cross-package concern; the 'three expression reconstruction implementations' turned out to already be a single implementation, so no action was needed there. Purely mechanical, zero behavior change, full-suite green (1783 passed).

**Key decisions**
  - Delete the shim files outright rather than keep them as compatibility layers, since analysis/qualified_names.py had zero importers and resolution/identifier_types.py's 9 importers were all migrated in the same change
  - Two BindingInfo classes (local dataclass in extraction/usage_extractor.py vs. upstream Pydantic model in agentic_mbse) ruled out-of-scope for this refactor — different base types, different fields, cross-package unification would be a separate future item
  - Three expression-reconstruction implementations claim was found to be stale — only one impl (extraction/expression_utils.py) exists — marked resolved with no code change

**Supersedes / retires**
  - analysis/qualified_names.py (re-export shim)
  - resolution/identifier_types.py (re-export shim)
  - re-export blocks in analysis/__init__.py and resolution/__init__.py for naming/identifier symbols

#### H-070 · 2026-02-20 — Phase 7.1 Pure structural refactor: move pipeline orchestration functions out of generation/initialization.py into a new orchestration/ package
`20260220_orchestration-extraction`  ·  subject: **orchestration package extraction**  ·  status: **shipped**

generation/initialization.py had grown to 888 lines mixing generation code with coordination logic (build_pipeline_context, build_output_registry, and their helpers). This item moved all coordination functions into a new orchestration/ package (pipeline_builder.py, output_registry_builder.py), leaving initialization.py with only PipelineContext and the two exception classes (109 lines). It updated 40+ import sites across production code, tests, and scripts. A circular import was discovered mid-build: generation/__init__.py re-exporting build_pipeline_context from orchestration while orchestration imported PipelineContext back from generation.initialization created a cycle; the fix was to drop build_pipeline_context from generation's public re-exports and have cli/__init__.py import it directly from orchestration.pipeline_builder, which is a small public-API change. No behavior changed; the full 1783-test suite passed with zero output-baseline differences.

**Key decisions**
  - PipelineContext stays in generation/initialization.py rather than moving to orchestration/, to avoid an import cycle and match the plan's acceptance criteria
  - build_pipeline_context is no longer re-exported from generation/__init__.py (removed to break a circular import); callers must import it directly from sysml_codegen.orchestration.pipeline_builder
  - _classify_entry_points, which the implementation plan mistakenly listed as needing a move, was confirmed already correctly placed in resolution/graph_builder.py and left untouched

**Supersedes / retires**
  - generation/initialization.py's role as home for build_pipeline_context() and build_output_registry(); those now live in orchestration/pipeline_builder.py and orchestration/output_registry_builder.py

#### H-071 · 2026-02-22 —  Consolidate scattered post-refactor design notes and stale ADRs into a single docs/architecture/ authority
`20260222_docs-consolidation`  ·  subject: **architecture documentation**  ·  status: **shipped**

After the February 2026 refactor, the implemented design lived across 40+ files in .project/concepts/refactor-design-intent/ (session logs, spike notes, validation matrices) while docs/architecture/ held only 8 ADR files, 3 with stale paths, and no consolidated overview. This item migrated all 27 design docs to docs/architecture/reference/ with session noise stripped, wrote a new architecture overview with a reading guide and data-flow diagram, extracted a modeling-assumptions document from ADR-001/002/006/007, built a verification-matrix.md mapping all 204 REQ-* tags to test files (192 PASS, 12 UNTESTED), removed all 8 ADR files (their unique content subsumed into modeling-assumptions.md), and archived the old concept folder with an ARCHIVED.md pointer. No code changed; 1812 tests passed with no regressions at close.

**Key decisions**
  - ADR-003/004/005/008 content was implementation-decision detail already covered by the reference docs, not SysML modeling prerequisites, so no unique content needed extraction into modeling-assumptions.md
  - All 8 ADR files were deleted from docs/architecture/ once their content was subsumed elsewhere
  - The old concept folder is preserved but marked ARCHIVED with a pointer to the new canonical docs/architecture/ location, not deleted

**Supersedes / retires**
  - The 8 ADR-001 through ADR-008 files previously in docs/architecture/, replaced by docs/architecture/modeling-assumptions.md and the reference/ doc set
  - .project/concepts/refactor-design-intent/ as the working documentation source, now archived and historical-only

#### H-094 · 2026-07-19 — Item 3 Prove extension-time V11 coverage checking is vacuous, then delete it
`20260720_constraint-lifecycle-gate-b`  ·  subject: **constraint extension V11 coverage**  ·  status: **shipped**

Investigated whether append-only constraint extension (extend_graph_with_constraints) could introduce a new V11 coverage violation that its whole-extended-graph check needed to catch separately from the final generation gate. A closed enumeration and corpus sweep across 35 fixture models showed every path an appended module input could take is either not entry-point-sourced, structurally unreachable (fallback keys vs design-attribute QNs occupy disjoint namespaces), or blocked at extraction. The extension-time check was deleted (3 lines in constraint_lowering.py) rather than replaced with a differential; the final generation gate still owns whole-graph V11 coverage. An independent audit passed the deletion with notes on citation accuracy in the decision record (stale/uncited mechanism references, off-by-one corpus counts, an overstated 'filed' status on the upstream fusion-tea filing) but did not change the verdict. A pre-existing stale in-model comment in the shared_producer fixture, found during the sweep, was corrected and reconciled against Item 2's evidence without contradiction.

**Key decisions**
  - Extension-time V11 coverage checking is deleted; the final generation gate is the sole owner of whole-graph coverage enforcement (contract row LC-E02, superseding old lowering INV-6)
  - No differential/scoped-check wrapper was built despite both upstream Gate B reports recommending one, because the introduced-offender set is provably always empty
  - Re-open trigger recorded: if any future change lets a design-attribute QN enter fallback_entry_points, vacuity breaks and this deletion must be revisited
  - The bridge workaround in the fusion-tea demo remains a private consumer workaround, not a sanctioned upstream late-fill seam (LC-E04A)

**Supersedes / retires**
  - Old lowering INV-6's requirement that the extended graph have zero V11 uncovered params

#### H-105 · 2026-07-24 —  Reconcile docs/architecture/ with merged main after the CONSTRAINT-LIFECYCLE epic's late changes
`20260724_docs-lifecycle-sync`  ·  subject: **architecture documentation reconciliation**  ·  status: **shipped**

The CONSTRAINT-LIFECYCLE epic (referred to in this item's own text as post-CONSTRAINT-LIFECYCLE work, not named as this item's parent epic) left documentation stale and owed two gap writeups: a diagnostics severity system with no doc coverage, and a missing portability verification-matrix row. This item swept docs/architecture/ against merged main across five phases, wrote a new severity doc (30-diagnostic-severity.md) with citations verified into both sysml-codegen and agentic-mbse, added two matrix rows (REQ-SNAP-21/22) with a reconciled 276-row recount, re-anchored EXPLAINER_PROMPT.md's stale claims, added override-capture-honesty notes, and rewrote the resolver-architecture docs to reflect Item 2's dual-ladder-to-single-registry unification (deleting input_resolver.py from the documented architecture). The audit found the work accurate everywhere reachable; one section citing agentic-mbse code was initially unverifiable from the audit sandbox, closed same-day by an orchestrator session with agentic-mbse access confirming all seven citations exact.

**Key decisions**
  - Corrections shrink or amend stale doc claims in place with a code citation, never accrete a 'used to say X' history outside a marked Dated-history block.
  - No release-readiness claims are added anywhere in the docs; the composed-proof archive stays the closed record for that.
  - Doc 04 (input-resolver) is replaced with a producer-resolution reference doc rather than patched, since the underlying module was deleted, not merely renamed.
  - Only claims about override-capture correctness get the nested-occurrence-override honesty note, not every mention of design_override/:>> capture.

**Supersedes / retires**
  - 04-input-resolver.md's description of the now-deleted resolution/input_resolver.py module and its dual-resolver-ladder narrative in 24-dual-resolution-architecture.md.

#### H-106 · 2026-07-24 —  Add a warning for silent value loss on the nested-occurrence-override calc path
`20260724_nested-override-tripwire`  ·  subject: **supplied-values resolution, warnings**  ·  status: **shipped**

The [NESTED-OCCURRENCE-OVERRIDE] shape lets a modeled override value drop silently when a dotted part_usage.attr demand falls through to a manual-required entry point. This item made that loss loud instead of fixing it: a corpus false-fire scan against 19 snapshot fixtures showed a naive name-only predicate misfired 4 times on legitimate reference-form aggregation, so the shipped predicate adds a dotted-shape gate and a part-usage gate, reaching zero false fires on the clean corpus before any production code was written. Implementation added _unmatched_override_scopes and a single collect-then-drain logger.warning per target in supplied_values.py. No resolution outcome or generated output changed; full licensed suite (3118 passed, 47 skipped), ruff clean, mypy at the pre-existing baseline. The underlying occurrence-to-definition bridge fix remains filed in the backlog as separate work.

**Key decisions**
  - Ship a diagnostic tripwire only, not a resolver fix — the real fix (occurrence-to-definition bridge) stays filed in BACKLOG.md as [NESTED-OCCURRENCE-OVERRIDE]
  - Gate the warning on both a dotted-form shape and a part-usage match, because a name-only predicate false-fires on legitimate reference-form aggregation rollups
  - Use the corpus false-fire scan as the acceptance gate for the predicate before writing any production code

#### H-125 · 2026-08-20 —  Ship the already-closed stop-reinventing-the-parser work to GitHub main across agentic-mbse, sysml-codegen, and fusion-tea, preserving Fusion's exact commit pin
`20260820_stop-parser-pr-shipment`  ·  subject: **cross-repo PR shipment**  ·  status: **shipped**

The stop-reinventing-the-parser item was finished and owner-closed, but existed only on local branches in three repositories, and Fusion Tea pins the exact Codegen commit SHA and wheel hash it depends on -- a squash or rebase merge would make that pinned commit unreachable and force a repin plus regenerated provenance evidence. This item published all three repositories' work to GitHub main in dependency order (Agentic, then a Codegen integration branch merging the docs-closure line into the production line without letting a separate evidence-only child commit leak in, then Fusion), using explicit merge commits throughout, verifying wheel byte-identity and differential test-suite parity at each gate, and fixing two stale contract tests that asserted pre-close state. All merges landed via owner-admin click (branch protection blocked the agent's own merge), and all four identity tags were published at the end.

**Key decisions**
  - Every merge uses an explicit merge commit, never squash or rebase, to keep the Fusion-pinned Codegen commit SHA reachable from main
  - A separate 6-file evidence-only child commit (924eadf) is deliberately never merged into main -- it is preserved only via a pushed tag, verified absent by an ancestry check gate
  - Owner explicitly authorized fast-forward pushing the local mains directly (40 and 5 commits) rather than routing them through baseline PRs, to avoid re-diverging local and GitHub main
  - Wheel-identity and test-suite-parity gates were re-derived to checkable equivalent forms (byte-identity-to-a-fresh-C_prod-build, and differential-outcome-parity) since the sealed baseline counts are not reproducible from an ordinary checkout

### EXPR-CODEGEN  
*6 item(s), 2026-02-03 → 2026-02-08*


#### H-002 · 2026-02-03 — Item 1 Spike: validate that SysIDE exposes CalcDef output expression ASTs and that feature references resolve
`20260203_expr-spike-ast`  ·  subject: **expression AST extraction**  ·  status: **shipped**

The expression-aware codegen effort (aiming to auto-generate real computation code instead of NotImplementedError stubs) rested on two unvalidated assumptions: that CalcDef output attributes expose their expression ASTs via feature_value_expression, and that every feature reference inside those expressions resolves to a declared input or sibling output. This spike wrote two diagnostic scripts run against chain_spike, sample_model, solar_battery, and catf_mfe, finding 95.8% AST coverage (100% on the three fixture suites, 86.7% on catf_mfe, with the gaps being physics stubs that would need manual implementation anyway) and 98.6% feature-reference resolution (100% on fixtures; 3 unresolvable refs in catf_mfe traced to same-CalcDef members with no direction annotation, i.e. undeclared intermediates). It inventoried 3 AST node types and 5 operators (including native `**`) and found zero cross-check mismatches in extract_feature_refs. The spike issued a GO recommendation for building the expression compiler.

**Key decisions**
  - GO decision to proceed with expression-compiler design: AST coverage and reference-resolution rates both cleared the spec's go threshold (>=80% and effectively 100% respectively)
  - Undeclared intermediate references (3 in catf_mfe) are flagged as a pattern the compiler must handle by checking all CalcDef members, not just declared input/output lists, and left for the next item (Item 2) to decide the approach
  - Output attributes within a CalcDef must be compiled in topological dependency order since many outputs (e.g. material_cost) are reused as intermediates by sibling outputs

#### H-003 · 2026-02-04 — Item 2 Spike proving syside expression ASTs compile to correct Python and that a compilability classifier partitions CalcDefs with zero false positives
`20260204_expr-spike-compile`  ·  subject: **expression compilation spike**  ·  status: **shipped**

Following Item 1's proof that ASTs are extractable and references resolvable, this spike answered whether the AST-to-Python transformation is semantically correct and whether a FULLY_COMPILABLE/PARTIALLY_COMPILABLE/MANUAL_REQUIRED classifier is trustworthy. Two scripts compiled 102 outputs across four model suites (chain_spike, sample_model, solar_battery, CATF) and classified all 44 CalcDefs; compiled expressions matched handwritten ground truth exactly (0.00e+00 relative error) for the 5 CalcDefs with runnable handwritten impls, and the classifier produced zero false positives. It found 3 CATF CalcDefs referencing undeclared same-CalcDef intermediates, and proved extended resolution against all owned_members discovers and compiles them correctly end-to-end. The verdict was GO to proceed to Item 3 (the real expression compiler module), with the caveat that 37 of 42 FULLY_COMPILABLE verdicts were syntax-validated only, and Pattern B (multi-step intermediates, the case most sensitive to topological-sort errors) had zero numerical ground truth since all its handwritten impls were stubs.

**Key decisions**
  - GO decision to proceed to Item 3 (expression compiler module) -- all five go/no-go conditions met
  - Undeclared intermediates handled by expanding INTERMEDIATE_REF to include same-CalcDef owned_members rather than adding a new AST node type; the real work is code emission (extract, compile, and emit them as local variables before dependent outputs), not just reference resolution
  - Compiler uses defensive over-parenthesization for every binary expression rather than precedence-aware minimal parenthesization, judged correct and readable enough to defer optimization to Item 3
  - Unary negation and the ^ operator alias get defensive handling even though neither was observed in any model, on the recommendation that the implementation is trivial

#### H-004 · 2026-02-06 — Item 3 Build a standalone expression compiler module that converts SysML expression ASTs into executable Python
`20260206_expr-compiler-module`  ·  subject: **expression compiler**  ·  status: **unknown**

Items 1-2 spiked and validated that SysIDE expression ASTs could be extracted and compiled to correct Python; this item turned that spike logic into a production-quality module. It added expression_compiler.py (Compilability/ExpressionNodeType enums, ExpressionAST IR, CompilationResult/CalcDefCompilationResult, and compiler functions for AST building, Python emission, compilability classification, and undeclared-intermediate discovery with topological ordering) plus a new expression_utils.py holding AST-to-text logic extracted out of constraint_extractor.py. The module was designed to be fully unit-testable without the syside dependency, using mocked syside nodes and monkeypatched adapters. Pipeline wiring was explicitly out of scope, deferred to Item 4.

**Key decisions**
  - N-ary OperatorExpression nodes are left-folded into binary ExpressionAST nodes at construction time, not at code-emission time
  - Undeclared CalcDef members referenced in output expressions are discovered, compiled, and emitted as local variables via topological ordering rather than left unsupported
  - The compiler uses defensive over-parenthesization and its own PYTHON_OPERATOR_MAP distinct from constraint_extractor's OPERATOR_MAP
  - Shared AST-to-text reconstruction logic is extracted into expression_utils.py so constraint_extractor.py and the new compiler do not duplicate it
  - SelectExpression/conditional expressions, InvocationExpression/function calls, and named-constant substitution (e.g. math.pi) are explicitly out of scope

#### H-005 · 2026-02-07 — Item 4 Wire the expression compiler into the codegen pipeline so compilable CalcDefs get auto-generated implementations instead of NotImplementedError stubs
`20260207_expr-pipeline-integration`  ·  subject: **expression compiler pipeline wiring**  ·  status: **shipped**

Items 1-3 built an expression compiler that could turn SysML expression ASTs into executable Python, but nothing in the pipeline called it, so every generated _impl.py still had a manual-authoring stub. This item added a Step 6.5 compilation phase between backtracking and graph building, captured raw ASTs during extraction, fixed a bug where OperatorExpression bindings were dropped to UNBOUND, added a compilability field to PipelineModule, and added a new auto_implementation.py.jinja2 template that emits real computation code with an AUTO_IMPLEMENTED sentinel while non-compilable CalcDefs still get stubs. Verified end to end on the chain_spike model producing real code for all three CalcDefs, with existing signature-based preservation confirmed to handle the auto-impl lifecycle unchanged. All 116 tests passed with zero regressions and no new mypy/ruff errors.

**Key decisions**
  - Compiled expression strings stay on CalcDefCompilationResult in PipelineContext rather than being added to PipelineModule, keeping resolution-layer data separate from compiled code
  - PARTIALLY_COMPILABLE CalcDefs fall through to full stub generation rather than partially auto-implementing some outputs
  - Auto-implemented files use the same function signature as stub templates so preservation's signature-match logic needs no changes

**Supersedes / retires**
  - The unconditional NotImplementedError stub generation for CalcDefs whose math is fully expressed in SysML
  - The legacy text-only _extract_expression_text() function, replaced by calls into expression_utils.py

#### H-006 · 2026-02-08 — Item 4.1 follow-on Fix NameError in generated multi-output CalcDef auto-implementations when a later output references an earlier declared output
`20260208_auto-impl-output-crossref-fix`  ·  subject: **auto-impl output generation**  ·  status: **shipped**

E2E validation of the EXPR-CODEGEN epic found that multi-output CalcDefs where a later output references an earlier declared output (e.g. f_recirculating = 1.0 / q_eng) generated a return tuple that inlined each output's expression independently, so q_eng was never assigned as a local variable and referencing it produced a runtime NameError. Two ground-truth E2E tests (EngineeringQFactor in CATF, AnnualizedFinancialCalc in solar_battery) were marked xfail because of this. The fix changed _build_auto_impl_context() in generation/stencils.py so that when any declared output is cross-referenced by another, all declared outputs for that CalcDef are emitted as local variable assignments before the return statement (matching how undeclared intermediates were already handled), with the return tuple referencing them by name; single-output CalcDefs remain unaffected. Both xfail markers were removed and all 167 tests (144 pre-existing plus new coverage) passed with 0 xfail, 0 failures, closing EXPR-CODEGEN Epic 1 cleanly before Epic 2 began.

**Key decisions**
  - When any declared output has a cross-reference to another declared output, ALL declared outputs for that CalcDef are promoted to local variable assignments (not just the referenced ones) as the simplest correct approach for partial-cascade cases
  - Single-output CalcDefs are left untouched, continuing to inline in the return statement

#### H-007 · 2026-02-08 — Item 5 End-to-end validation of the expression compiler on real solar_battery and newly-built CATF fusion model fixtures
`20260208_expr-e2e-validation`  ·  subject: **expression codegen e2e validation**  ·  status: **shipped**

Items 1-4 of EXPR-CODEGEN built and unit-tested the expression compiler, but only the trivial chain_spike model had been run through it end to end, and Pattern B (multi-step intermediates) had zero runtime ground truth. This item ran codegen on solar_battery (all 15 CalcDefs auto-implemented, exceeding the >=10 target) and on a newly-created self-contained CATF MFE fixture (28 SysML files copied and trimmed from an external fusion model repo; 19/21 CalcDefs auto-implemented, 2 correctly stubbed as manual_required). Hand-computed Pattern B ground truth was added for EngineeringQFactor and MagnetCryogenicLoad, independently derived from the SysML expressions rather than from the compiler. The run discovered a real codegen bug: when a declared output references another declared output in a multi-output CalcDef, the generated code inlines the reference into the return tuple instead of assigning it as a local variable first, causing a NameError. Two tests were marked xfail to document the bug and keep the suite green; a follow-up item was flagged to fix the auto-impl Jinja2 template.

**Key decisions**
  - PlasmaConfinement and TritiumBreedingRatio classified as manual_required rather than partially_compilable as the spec assumed, because both are Phase-2 interface placeholders with no meaningful compilable outputs -- deviation recorded, not corrected in the spec
  - The multi-output declared-output-cross-reference codegen bug is scoped to the auto-impl Jinja2 template (declared outputs referencing other declared outputs need local-variable assignment before the return statement); fix deferred to a separate follow-up item rather than fixed in this pass
  - CATF fixture ended up with 28 SysML files rather than the 21 originally scoped, adding a library/components/ directory for import-resolution safety

### ATTR-EXPR  
*5 item(s), 2026-02-08 → 2026-02-09*


#### H-008 · 2026-02-09 — Item 2 Build data models and extraction logic to classify and compile PartDef/PartUsage attribute expressions
`20260209_attr-expr-extraction`  ·  subject: **computed attribute extraction**  ·  status: **unknown**

The ATTR-EXPR epic aims to eliminate the CalcDef+CalcUsage ceremony for simple attribute-level formulas like 'attribute volume = length * width * height'. This item, following a spike that proved SysIDE exposes feature_value_expression on PartDef attributes, added a ComputedAttributeClassification enum (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE) and a ComputedAttributeData dataclass, plus a new extract_computed_attributes() function that classifies attribute expressions using qualified-name resolution and compiles FORMULA patterns through the existing Phase 1 expression compiler unchanged. The design specifically fixes a qualified-name collision bug the spike found (19 CATF misclassifications) by using ref.qualified_name namespace matching instead of simple name matching, and handles FeatureChainExpression's two-ref decomposition. Deliberately standalone with zero impact on existing code paths; pipeline integration is left to Item 3.

**Key decisions**
  - Classification uses ref.qualified_name namespace matching (not ref.name) to avoid misclassifying sibling-named CalcDef outputs as sibling attribute refs
  - CalcUsage-instance refs produced by FeatureChainExpression traversal are filtered by positive identification against calc_usage_names, not by 'not a sibling therefore calc ref' inference
  - No chain-awareness in extraction: a FORMULA referencing another computed attribute compiles identically to referencing a literal one; chain ordering is deferred to Item 3
  - FORMULA compilation failures degrade gracefully to MANUAL_REQUIRED rather than raising
  - Zero changes to the Phase 1 expression compiler; extraction-layer models use @dataclass per project convention

#### H-009 · 2026-02-09 — Item 3 Wire computed-attribute extraction into the codegen pipeline so FORMULA attributes generate executable modules
`20260209_attr-expr-pipeline`  ·  subject: **computed attribute modules**  ·  status: **shipped**

Item 2 built extraction and classification for computed attributes, but that data was never consumed: no modules, YAML entries, or code came from it. This item added a new pipeline step to extract computed attributes, remove FORMULA attributes from design_attributes so they aren't misclassified as entry points, teach the dependency backtracker to resolve CalcUsage bindings that target FORMULA attributes as module outputs, and extend the graph builder to synthesize PipelineModule objects for FORMULA attributes with correct input wiring (including EXPOSE_PURE alias resolution) and a unified topological sort across computed-attribute and CalcUsage modules. Code generation (module wrappers, auto-implementations, pipeline YAML, registry, backlog report) was extended in parallel to cover the new synthetic modules. All acceptance criteria were checked off and 264 tests passed after hardening.

**Key decisions**
  - Backtracker checks computed-attribute resolution before calling the normal binding resolver (Option A), rather than adding a strategy inside it, to avoid needing a fake CalcUsageData sentinel
  - Computed-attribute outputs are added to the output catalog before CalcUsage modules are built, so downstream bindings can validate against them
  - Ordering uses one unified topological sort across all modules (CalcUsage + computed attribute) rather than relying on the backtracker's CalcUsage-only pre-sort
  - EXPOSE_PURE CalcUsage bindings already resolve correctly via the existing backtracker transitive-resolution strategy; no code change needed there, only for FORMULA module input wiring

#### H-010 · 2026-02-09 — Item 1 Spike: confirm SysIDE exposes expression ASTs on PartDef attributes, as the hard go/no-go gate before building automatic computed-attribute codegen
`20260209_attr-expr-spike`  ·  subject: **attribute expression AST discovery**  ·  status: **shipped**

Phase 2 (ATTR-EXPR) aimed to let a modeler write a computed attribute directly on a PartDef instead of authoring a full CalcDef/CalcUsage pair, but that only works if SysIDE actually surfaces expression ASTs on ordinary attributes. A first pass against real models found only one FORMULA-pattern attribute among 540, so a purpose-built fixture (tests/fixtures/attr_expr_probe/) with 35 attributes across FORMULA, EXPOSE, LITERAL, and cross-reference patterns was authored to get a real read. All 35 attributes had feature_value_expression populated, reference resolution and qualified names worked, and the existing Phase-1 compiler successfully compiled 31 of 35 expressions directly (the 4 EXPOSE-pattern failures were expected, since EXPOSE requires cross-module chain handling the Phase-1 compiler doesn't yet do). The spike concluded GO: AST availability is confirmed and the compiler is reusable, clearing the way to Item 2.

**Key decisions**
  - GO decision: SysIDE reliably populates feature_value_expression on PartDef/PartUsage attributes, so Phase 2 (automatic computed-attribute codegen) is viable
  - The existing Phase-1 expression compiler can be reused as-is for attribute FORMULA expressions without modification; EXPOSE-pattern attributes need separate handling for cross-module feature-chain references

#### H-011 · 2026-02-09 — Item 5a Write ADR-001 through ADR-005 for attribute-expression architecture and close the ATTR-EXPR epic
`20260209_attr-expr-docs`  ·  subject: **ADR documentation, epic closure**  ·  status: **shipped**

The ATTR-EXPR epic had shipped 7 architectural decisions (FORMULA/EXPOSE classification, pipeline step 4.5, backtracker/graph-builder extensions) with no formal ADRs, and the repo's referenced ADR-001/002/003 existed only in the pre-split monorepo, not locally. This item created docs/architecture/ in sysml-codegen, migrated ADR-001/002/003 from the monorepo byte-identical, wrote new self-standing ADR-004 (computed attribute pipeline integration) and ADR-005 (computed attribute classification), amended ADR-001's entry-point table and ADR-002's Rule 3 for the FORMULA exemption, and closed out the epic (lessons learned, status, BACKLOG.md, concept-doc status) with all five attr-expr-* active folders archived. All phases and validations were checked complete; full suite (285 tests) passed with no regressions.

**Key decisions**
  - ADR-005 (classification) is written before ADR-004 (pipeline integration) since ADR-004 forward-references it
  - ADR-001's computed-attribute clarification and ADR-002's FORMULA amendment are appended/edited in place, not rewrites, preserving original monorepo-era text and its historical references
  - EXPOSE_COMPUTED classification is documented as a known deferred UX gap with a CalcDef workaround, not implemented in this item

#### H-012 · 2026-02-09 — Item 4 End-to-end numerical validation of computed attribute expression pipeline on real models
`20260209_attr-expr-e2e`  ·  subject: **computed attribute e2e validation**  ·  status: **shipped**

Items 1-3 of the ATTR-EXPR epic built computed-attribute extraction, classification, compilation, and pipeline wiring, but nothing had executed the generated code and checked numerical correctness. This item added 21 new E2E tests executing FORMULA auto-implementations against hand-computed ground truth on the attr_expr_probe fixture (9 attributes, including chains and fan-in) and on solar_battery's p_net_kw synthetic module, and verified EXPOSE_PURE/EXPOSE_COMPUTED classify with no spurious modules or errors. All 285 tests passed (0 failures, 0 xfail) with zero regressions to the 264 pre-existing tests. The item closed as the validation gate before Item 5 (ADRs/documentation) and epic closure.

**Key decisions**
  - EXPOSE_COMPUTED execution validation deferred out of scope, documented as a known gap
  - Numerical assertions use pytest.approx with relative tolerance to handle floating-point arithmetic
  - Production bugs found during validation are fixed but tracked separately from this validation item

### COST-PATTERN  
*11 item(s), 2026-02-10 → 2026-02-16*


#### H-014 · 2026-02-10 — Item 4 Pipeline-integrate hierarchy extraction so virtual CalcUsages and aggregation rollups generate real modules
`20260210_hierarchy-pipeline`  ·  subject: **hierarchy-aware module generation**  ·  status: **unknown**

Items 2 and 3 built template CalcUsage detection, virtual instantiation, redefinition resolution, and sum() aggregation transformation, but none of that data reached the pipeline: virtual CalcUsages had unresolvable bare-name bindings and aggregation expressions were produced but never consumed, so codegen on the solar_battery model only emitted the 5 system-level modules. This item added pipeline steps to extract hierarchy data and rewrite virtual CalcUsage bindings (resolving literal, chain, and deep-path :>> redefinitions), extended the graph builder with an aggregation-module builder that resolves symbolic child-output references to real pipeline channels, and taught the backtracker and output catalog to expose aggregation outputs to downstream system-level calculations. Generation code (module wrappers, auto-implementations, YAML with a `# source: aggregation` comment, registry, backlog) was extended to cover the new module classes. The spec document itself has all acceptance-criteria checkboxes left unchecked, unlike the sibling attr-expr-pipeline item, though its header marks Status: Complete.

**Key decisions**
  - Virtual CalcUsage binding rewriting handles three :>> redefinition patterns: LITERAL (direct value), CHAIN (retarget source_path to another calc's output), and design deep-path (trace target_path to a leaf attribute)
  - Multiplicity counts become DESIGN_ATTRIBUTE entry points typed as Integer; :>> literal redefinitions also become DESIGN_ATTRIBUTE entry points; CalcDef defaults stay LIBRARY_DEFAULT
  - Aggregation module naming is disambiguated by owning-part qualified name per ADR-003 to avoid collisions when multiple PartDefs share an attribute name
  - Aggregation expressions with has_unsupported_nodes=True still generate a module, but with MANUAL_REQUIRED compilability (stub) instead of an auto-implementation
  - Non-uniform array instances are explicitly out of scope; the solar_battery model's arrays are all uniform

#### H-015 · 2026-02-10 — Item 3 Extract redefinition, multiplicity, and aggregation-expression data to bridge virtual CalcUsages to the pipeline
`20260210_hierarchy-resolution`  ·  subject: **redefinition and aggregation extraction**  ·  status: **shipped**

Item 2 produced virtual CalcUsages with unresolved bindings and no way to feed sum() aggregation expressions into the pipeline; the expression compiler had no handler for InvocationExpression so sum() calls were classified UNRESOLVABLE. This item built extraction for `:>>` ReferenceUsage redefinitions (classified as LITERAL, CHAIN, or EXPRESSION), resolved deep-path overrides via chaining_features, detected PartUsage multiplicity via cached_lower_bound (explicitly not cached_upper_bound, which is off-by-one under syside's exclusive convention), transformed sum(array.attr) into a parametric multiply (count * attr), and introduced a new AggregationExpressionData model capturing sum/singleton/local terms plus input channels and entry points. All output is pure data with no pipeline, backtracker, or generation wiring — that is Item 4's job. Implementation matched the design exactly across all four phases with zero regressions against a 313-test baseline.

**Key decisions**
  - Item 3 produces data structures only; no pipeline, backtracker, or generation-layer changes, deferring integration to Item 4.
  - Multiplicity count must come from cached_lower_bound, never cached_upper_bound, because syside's exclusive convention makes the latter off by one (N+1).
  - extract_design_overrides() takes an Iterable of PartUsage elements rather than the raw model, for testability without mocking SysideAdapter.elements_of_type() — the orchestrator supplies the real call.
  - The transformed aggregation expression carries one extra layer of parentheses versus the design's expected text, accepted as mathematically equivalent since Item 4 consumes structured term data, not the string.

#### H-016 · 2026-02-10 — Item 1 Research spike probing how SysIDE's AST represents hierarchy, redefinition, multiplicity, and aggregation patterns needed for the Costed Component pattern
`20260210_hierarchy-spike`  ·  subject: **SysIDE AST, hierarchy/redefinition probing**  ·  status: **shipped**

Native support for the Costed Component pattern (PartDefinitions with embedded CalcUsages, :>> redefinition chains, parameterized multiplicity, sum() aggregation) needed empirical answers about SysIDE's AST representation before implementation could begin. A probe script ran 10 questions against the solar_battery model fixture, covering template-vs-concrete CalcUsage ownership, :>> redefinition structure (ReferenceUsage, not AttributeUsage), part redefines vs plain part, deep-path :>> resolution, multiplicity representation, sum() InvocationExpression structure, specialization chain traversal, new-vs-redefined attribute distinction, default := representation, and binding to inherited/redefined attributes. All 10 questions passed, including two audit follow-up corrections (deep-path chaining lives on the redefined_feature, not the redefining element; cached_upper_bound is systematically N+1 due to an exclusive-bound convention). The spike concluded GO and fed directly into Item 2's design phase.

**Key decisions**
  - GO decision to proceed with COST-PATTERN Items 2-5 implementation; SysIDE's AST has sufficient structure.
  - :>> redefinitions always produce ReferenceUsage (never AttributeUsage); all downstream code must check for ReferenceUsage.
  - Deep-path :>> resolution must use owned_redefinitions[0].redefined_feature.chaining_features, not heuristic value matching.
  - Multiplicity count must use cached_lower_bound or resolve upper_bound's referenced default, never cached_upper_bound (which is N+1).
  - Hierarchy traversal helper (traverse_hierarchy) and RedefinitionInfo/HierarchyNode models should live in sysml-codegen, not agentic-mbse, per the reuse assessment.

#### H-017 · 2026-02-10 — Item 2 Detect template CalcUsages owned by PartDefinitions and expand them into per-instance virtual CalcUsages
`20260210_template-detection`  ·  subject: **calc usage template expansion**  ·  status: **unknown**

Codegen was extracting a CalcUsage owned by a PartDefinition (a template, e.g. a cost calc inside a reusable 'PV Module' part def) only once, instead of once per PartUsage that instantiates that part def. This under-produced pipeline modules for the solar_battery model's LCOE pipeline. The spec added is_template/owning_part_def_qn/raw_element fields to CalcUsageData, a template-detection check on owning_type, a PartUsage index and recursive instantiation-path resolver to compute design-relative qualified names, and a virtual CalcUsage generator that replaces each template with one concrete CalcUsageData per instantiation, with bindings copied as-is for later backtracker resolution. extract_calculation_usages() gained an expand_templates flag defaulting to True so the pipeline picks this up transparently.

**Key decisions**
  - Use owning_type / SysideAdapter.is_instance() for template detection rather than type().__name__, matching the codebase's existing adapter-abstraction convention
  - Virtual CalcUsage instance_name is set to the full qualified_name (not a short name) because the backtracker indexes CalcUsages by instance_name and needs uniqueness across virtual instances
  - Specialization-chain matching for the PartUsage finder (FR-10) is deferred to Item 3; the index matches by direct type only
  - Deduplication by qualified_name handles the case where both a library PartUsage and a design 'part redefines' resolve to the same instantiation path

#### H-018 · 2026-02-13 — Item 5 End-to-end validation of the Costed Component pipeline on the solar_battery model, plus three ADRs
`20260213_hierarchy-e2e`  ·  subject: **costed component hierarchy pipeline**  ·  status: **unknown**

Items 1-4 of the COST-PATTERN epic built extraction, analysis, resolution, and generation for hierarchical costed components, but only against synthetic/mocked data. This item ran the pipeline on the real solar_battery fixture end to end: leaf-part cost modules, an allocation module, assembly-level aggregation modules, and system-level calcs, checking auto-implementation counts, numerical ground truth, pipeline YAML ordering, and a zero-item implementation backlog. It also added regression guards for the chain_spike and CATF MFE models and drafted ADR-006 (part hierarchy and template instantiation) and ADR-007 (parametric multiplicity and aggregation), plus an amendment to ADR-002 relaxing rules 1, 3, and 4 for uniform-array hierarchy patterns. No production code changes were planned unless the E2E run surfaced bugs. This closed out the COST-PATTERN epic.

**Key decisions**
  - Templates are detected by owning_type being a PartDefinition vs a concrete PartUsage; virtual CalcUsages are generated per (template, instance) pair (ADR-006)
  - Array aggregation uses parametric multiply (count * single-instance output) instead of flat per-instance expansion, valid only under a uniform-array assumption (ADR-007)
  - ADR-002 Rules 1, 3, and 4 are relaxed for CalcDefs embedded in library PartDefs, aggregation via `:>>` redefinition, and multiplicity as a structural property, but only under stated conditions; non-uniform arrays still require full Approach E
  - Aggregation module count and impl parameter names were left to be discovered empirically on the first real E2E run rather than guessed in advance

#### H-019 · 2026-02-11 — Item 5 Eight production bug fixes at hierarchy-aware aggregation pipeline subsystem boundaries, found during E2E validation
`20260211_hierarchy-bugfix`  ·  subject: **hierarchy aggregation pipeline**  ·  status: **unknown**

Running the COST-PATTERN pipeline on the real solar_battery model (Item 5 E2E work) surfaced broken aggregation output: garbage expression text, zero aggregation auto-implementations, mismatched module wrapper paths, a missing assembly (Site Infrastructure), and total_capex falling through to an ENTRY_POINT instead of the aggregation output chain. Two independent root-cause analyses converged on 8 unique bugs, each an integration gap between subsystems that worked correctly in isolation. This item fixed all 8: unwrapping SysIDE's InvocationExpression wrapper around sum() operands, adding a missing expression-compilation step, fixing a case-mismatch dict lookup, switching module/stencil paths from PartDef-scoped to instance-scoped EQNs, replacing exact-name-match scoping with a structural child-walk to find Site Infrastructure, registering `:>>` EXPOSE_PURE aliases in the aggregation output index, and surfacing orphan multiplicity entry points into a synthetic parameter group. All fixes were scoped to the aggregation pipeline with no public API changes and no effect on the existing CalcDef pipeline.

**Key decisions**
  - Unwrap logic handles any InvocationExpression wrapper (not just Evaluation), since SysIDE may use collect/select/other wrapper functions
  - Expression compilation (symbolic ref to inputs.X form) is built inline during ModuleInput construction rather than as a separate post-pass, to avoid duplicated/divergent param_name derivation
  - Site Infrastructure scoping fix uses a structural parent-child walk over MultiplicityData rather than a name-similarity heuristic, since PartDef name and PartUsage QN segment can differ
  - EXPOSE_PURE aliases for aggregation outputs are resolved at extraction time and stored on AggregationExpressionData, rather than threading redefinition data into the backtracker
  - Orphan entry points (not covered by any derived parameter group) are collected generically into a synthetic 'system_design' group, catching any future entry-point type the deriver doesn't know about, not just multiplicity

#### H-020 · 2026-02-12 — Item 5 Five probe-validated AST dispatch fixes to make hierarchy E2E tests pass against the real SysIDE model
`20260212_hierarchy-e2e-fixes`  ·  subject: **hierarchy extraction AST dispatch**  ·  status: **unknown**

COST-PATTERN Items 1-4 built the hierarchy-aware pipeline against synthetic mock data (69 unit tests), but running the new E2E suite (test_hierarchy_e2e.py) against the real solar_battery SysIDE model failed 4 of 10 tests. Root cause: FeatureReferenceExpression and FeatureChainExpression AST nodes both carry a function.name attribute, so any code using hasattr(node, 'function') as a proxy for InvocationExpression produced false positives, breaking all 20 aggregation expressions in the model. The spec defined five surgical, probe-validated fixes: reorder type checks in reconstruct_expression() and _walk_aggregation_ast() to check specific SysML types before the generic function.name check; add explicit is_instance() type guards to _unwrap_invocation() instead of relying on the fragile _KNOWN_WRAPPER_FUNCTIONS name-set (which collides on 'Evaluation'); add a part_usage_names field to HierarchyExtractionResult so all-singleton assemblies scope correctly; and add a new _enrich_aliases_from_bindings() function to populate aggregation aliases from CalcUsage binding parameter names before scoping and backtracking run. This superseded parts of an earlier hierarchy-bugfix spec (BF-1, BF-6, BF-7), whose fixes worked against mocks but not the real AST.

**Key decisions**
  - Fix ordering follows a dependency chain: FR-2 (reconstruct_expression reorder) before FR-1 (_unwrap_invocation guards) before FR-3 (_walk_aggregation_ast reorder), because extract_feature_chain_name() depends on the reordered reconstruct_expression()
  - Rejected using the _KNOWN_WRAPPER_FUNCTIONS name-set for _unwrap_invocation() guards because 'Evaluation' collides with FeatureReferenceExpression's function.name, and used explicit is_instance() type guards instead
  - Alias enrichment (RC5) is scoped to the generation layer (initialization.py), not the extraction layer, because it needs CalcUsage binding data that hierarchy_resolver.py does not have access to
  - part_usage_names widens Strategy 2 scoping to all child PartUsages (not just multiplicity children) rather than adding a new Strategy 3

**Supersedes / retires**
  - Portions of the earlier hierarchy-bugfix spec's BF-1, BF-6, and BF-7 fixes, which were valid against mock data but did not work against the real SysIDE AST

#### H-029 · 2026-02-16 —  Fix aggregation module input wiring so resolvable inputs resolve via the OutputRegistry instead of falling through to ENTRY_POINT
`20260216_aggregation-wiring-fix`  ·  subject: **aggregation graph-builder wiring**  ·  status: **shipped**

Aggregation modules roll child component costs up into assembly-level totals, but the graph builder's aggregation input resolution bypassed the OutputRegistry, using a fragile parallel CHAIN-search path that failed on PartDef-to-PartUsage name mismatches and unscoped keys. A prior spike on the solar_battery model found only 8 of 12 resolvable inputs succeeded (via CHAIN), 4 failed with CHAIN_PART_MISMATCH, and zero succeeded via the registry because every registry lookup was unscoped. This item fixed three bugs: added a scoped registry lookup (strip the design prefix, join the remaining path) tried between the existing CHAIN search and the unscoped Key_D fallback; added a new Key_E_stripped registration key in Phase 1b for sub-assembly-to-sub-assembly (agg-to-agg) references; and reordered SingletonTerm resolution to try the registry first before the CalcUsage-shaped direct-construction fallback, since aggregation outputs use a different double-attribute channel format. The fix was scoped to blocking COST-PATTERN's Item 5 E2E validation and targeted 12/12 resolvable solar_battery inputs reaching MODULE_OUTPUT with zero regressions across 454 existing tests.

**Key decisions**
  - Resolution order for aggregation inputs becomes CHAIN search, then scoped registry lookup, then unscoped Key_D fallback -- CHAIN is preserved rather than replaced because it still handles cases the registry doesn't
  - SingletonTerm resolution goes registry-first, then direct CalcUsage-style construction, then entry-point fallback, reversing the prior order
  - OutputRegistry.resolve() stays exact-match only; no normalization added to fix these bugs
  - Removing the CHAIN redefinition search path entirely, improving sanitize_name() for PartDef/PartUsage matching, and updating 08_algorithm_revised.md were explicitly deferred as future cleanup, not done here

#### H-030 · 2026-02-16 —  Fix two aggregation-wiring bugs misclassifying 58 of 70 solar_battery aggregation inputs as entry points
`20260216_aggregation-wiring-bugfix`  ·  subject: **aggregation expression wiring**  ·  status: **shipped**

COST-PATTERN's E2E validation item was blocked because most aggregation inputs in the solar_battery model wired to entry points instead of upstream module outputs. Bug A was a FeatureChainExpression/OperatorExpression check-ordering error present at three sites (hierarchy_resolver, expression_compiler, expression_utils) since FCE is a SysIDE subtype of OE and order-dependent is_instance checks routed FCE nodes to the wrong handler; Bug B was that LocalTerm handling in graph_builder unconditionally created entry points without checking for a sibling aggregation module output. Four prior spikes had confirmed both root causes and the fix approach before this item ran. The fix reordered the FCE check before OE at all three sites and added sibling-output resolution for LocalTerms, bringing wiring to 57 of 70 (13 correctly remaining as entry points), with a post-completion hardening pass adding tests after an audit found two integration tests were vacuous or exercising the wrong code path.

**Key decisions**
  - Fix all three FCE/OE ordering sites together even though only one (hierarchy_resolver) caused the blocking bug, since a codebase audit found the same latent defect in the other two.
  - Do not touch OutputRegistry, its key registration, or _resolve_aggregation_input_channel() — spikes confirmed those already work correctly once given properly classified terms.
  - Architecture doc updates (08_algorithm_revised.md, ADR-007, ADR-008) deferred to a follow-up rather than done in this item.

#### H-031 · 2026-02-16 —  Four diagnostic spikes to empirically verify or falsify root-cause hypotheses for 58 misclassified aggregation inputs
`20260216_aggregation-wiring-spikes`  ·  subject: **aggregation input wiring**  ·  status: **unknown**

COST-PATTERN's Item 5 (E2E validation) was blocked because 58 of 70 aggregation inputs in the solar_battery model were misclassified as entry points instead of wiring to upstream module outputs. Three prior research reports proposed root causes across extraction, resolution, and graph-builder layers, but an earlier fix attempt scoped to the wrong layer and only fixed 4 of 58 inputs. This spec commissioned four spikes against the real solar_battery model to test four hypotheses before committing to a fix: H1 whether FeatureChainExpression is a dual-match subtype of OperatorExpression in SysIDE's type system (Spike A); H2 whether reordering the AST walk check produces the expected ~37 term reclassifications with zero regression on the 12 working SumTerms (Spike B); H3 whether sibling aggregation outputs are present in the OutputRegistry when LocalTerms are processed (Spike C); H4 whether plant-level SingletonTerms actually resolve through the real 3-step resolution code path, with an expected nuanced outcome that only the unscoped Key_D fallback succeeds and Key_E_stripped is needed for robustness (Spike D). No production code was modified; results were meant to inform a subsequent fix design.

**Key decisions**
  - (none stated)

#### H-033 · 2026-02-16 —  Propagate :>> redefinition literal values through the backtracker and aggregation builder into JSON input templates
`20260216_redefinition-literal-propagation`  ·  subject: **entry point literal propagation**  ·  status: **shipped**

The solar_battery pipeline's hierarchy-aware codegen correctly extracted :>> redefinition literals (e.g. wattage :>> 400.0) but dropped the values before they reached generated JSON templates, forcing users to manually populate 13+ fields. A first fix (design.md) added 2 lines to the backtracker's LITERAL binding case so BindingInfo.literal_value flows into entry_point_sources, which Strategy 3 of _classify_entry_points() already consumed, fixing 13 design parameter literals. A second fix (design2.md) handled 4 remaining unwired aggregation inputs through a different code path: 3 permitting sub-costs needed a new _find_literal_redefinition() helper (mirroring the existing CHAIN-matching pattern) in the aggregation SingletonTerm/SumTerm fallbacks, and misc_hardware_cost needed a new EXPOSE_PURE alias map built from computed_attributes and consulted in the LocalTerm fallback so it wires to a MODULE_OUTPUT channel instead of becoming an entry point. Both fixes together eliminated all manual JSON workarounds for the solar_battery pipeline; 667 tests passed (3 new).

**Key decisions**
  - Literal values propagate via the existing entry_point_sources dict rather than adding a new data path (Strategy 3 already reads it)
  - BindingResolution.source_path stays None for LITERAL bindings; it is semantically a binding path, not a value
  - compilability stays MANUAL_REQUIRED for aggregation entry points even when a literal default is found (conservative judgment call, not FULLY_COMPILABLE)
  - Fix A required adding usage_type_map to HierarchyExtractionResult because usage names (e.g. 'permitting') don't match PartDef names, breaking simple name-matching
  - Fix B required QN normalization between ComputedAttributeData's '::' raw-name format and AggregationExpressionData's '__' sanitized-name format

### OUTPUT-REGISTRY  
*1 item(s), 2026-02-13 → 2026-02-13*


#### H-022 · 2026-02-13 — Item 1 Add the ChannelAlias model and OutputRegistry class as a single exact-match lookup, replacing five ad-hoc backtracker indexes
`20260213_output-registry-foundation`  ·  subject: **backtracker output indexing**  ·  status: **shipped**

The backtracker built five separate indexes with incompatible key formats bridged by a 7-strategy fallback cascade, which was the root cause of Bug 2 (EXPOSE_PURE two-hop resolution failure) and a class of key-format-mismatch bugs. This item added a purely additive ChannelAlias Pydantic model and an OutputRegistry class supporting a 4-phase registration protocol (CalcUsage/aggregation/FORMULA outputs, then CHAIN, EXPOSE_PURE, and transitive-default aliases) with exact-match resolution, no normalization, and explicit collision refusal. It shipped with comprehensive unit tests grounded in prior spike data, a smoke test against real solar_battery model data, and an xfail regression test capturing Bug 2 for later removal once the registry was wired in. Nothing existing was modified; the registry was not yet wired into the pipeline.

**Key decisions**
  - resolve() does exact-match dict lookup only -- no SYSML_QN normalization and no bare-name fallback, per prior spike evidence that normalization is broken and bare names don't occur
  - Collision policy is first-registration-wins with a logged warning, never silent overwrite
  - Key_C derivation (dotted hierarchy path stripping the design prefix) implemented as a static method on OutputRegistry since it's registry-specific, not a general qualified-name utility
  - is_transitive_default() named without a leading underscore (deviating from the spec's _is_transitive_default) because Item 3 needed to import it
  - register_alias() uses logger.warning()+skip instead of assert on phase-ordering violations, judged more actionable in a production pipeline

### OUTPUT-REGISTRY-BACKTRACKER-REDESIGN  
*3 item(s), 2026-02-13 → 2026-02-15*


#### H-025 · 2026-02-14 — Items 2a + 2b Produce first-class ChannelAlias objects from EXPOSE_PURE and CHAIN redefinitions for the OutputRegistry
`20260214_alias-producers-step-consolidation`  ·  subject: **channel alias production pipeline**  ·  status: **shipped**

The OutputRegistry (Item 1) needed authoritative alias data to populate, but EXPOSE_PURE computed attributes were incorrectly entering the module index (root cause of a wiring bug) and alias discovery relied on a brittle heuristic (Step 3.6) that inferred aliases from parameter-name divergence. This item made extract_computed_attributes() return EXPOSE_PURE attributes as ChannelAlias objects (filtering PartDef-level ones via a new is_on_part_definition field), produced scoped ChannelAlias objects from `:>>` CHAIN redefinitions in the hierarchy resolver, extended virtual binding rewrite to handle CHAIN overrides with SYSML_QN/DOTTED leaf extraction, and moved aggregation scoping (Step 4.7) into Step 3.5. The item completed with one deliberate deviation: the diagnostic test showed Step 3.6 was not fully subsumed by CHAIN-derived aliases (it also captures param_name aliases from binding divergence), so Step 3.6 was retained rather than removed, deferred to Item 3/4 when the backtracker moves to OutputRegistry.

**Key decisions**
  - Step 3.6 (_enrich_aliases_from_bindings) removal was gated on a diagnostic test proving its output is a subset of CHAIN-derived aliases; the diagnostic failed that premise (param_name aliases aren't covered), so removal was deferred rather than forced.
  - EXPOSE_PURE ChannelAlias.canonical_name is built from the references field, not expression_text, because SysIDE's expression_text for these nodes is unparseable.
  - EXPOSE_PURE alias_name stays unscoped (bare python_name) at production time; scoping with the owning part's short name happens later at Item 3's OutputRegistry registration, not here.
  - extract_design_overrides() and the aggregation orchestrator accept an Iterable of elements rather than the raw model, a deviation from the design chosen for testability without mocking SysideAdapter.elements_of_type().

#### H-026 · 2026-02-14 — Item 3 Wire the OutputRegistry into the pipeline as a shadow resolution path validated against the existing backtracker cascade
`20260214_backtracker-integration`  ·  subject: **OutputRegistry backtracker wiring**  ·  status: **unknown**

Items 1-2b built an OutputRegistry class, ChannelAlias data model, and alias producers, but none of it was wired into the pipeline, which still resolved bindings through the backtracker's 5 ad-hoc indexes and 7-strategy cascade. This item added build_output_registry() (a new Step 5.5) implementing a 4-phase registration protocol (CalcUsage outputs, CHAIN aliases, EXPOSE_PURE aliases, transitive design-attribute aliases), and gave the backtracker an optional parallel resolution path that runs the new single-lookup registry alongside the old cascade on every binding, logging any divergence while keeping the old cascade authoritative. It also fixed Bug 2 (EXPOSE_PURE two-hop resolution failure) via the new path and produced a migration audit of the 39 tests that access internal backtracker indexes, to guide Item 4's cut-over. The epic doc referenced is `.project/backlog/epic_output_registry_backtracker_redesign.md`, but that name is not confirmed against the folder's own text as a named epic elsewhere, so epic is left unknown per the no-inference rule despite the spec's own header naming it.

**Key decisions**
  - The new registry path runs in shadow/parallel mode only in this item; the old cascade stays authoritative for actual binding resolution until Item 4's cut-over
  - is_transitive is expected to always be False for registry-resolved bindings and is excluded from divergence comparison, since no downstream logic consumes it
  - Registry key formats are built to exactly match the old indexes' key patterns (Key_A through Key_F) so parallel validation compares like-for-like
  - Unresolved bindings in the new registry path must log a warning rather than silently falling through to an entry point

#### H-027 · 2026-02-15 — Item 4 Cut the dependency backtracker over to OutputRegistry as the sole resolution path, removing the old 5-index/7-strategy cascade and validating end-to-end
`20260215_cutover-validation`  ·  subject: **backtracker output resolution**  ·  status: **unknown**

Items 1-3 had built and parallel-validated OutputRegistry as a drop-in replacement for the backtracker's ad-hoc indexes and 7-strategy cascade, but the old cascade remained authoritative in production and a known bug (Bug 2, EXPOSE_PURE total_capex not wiring to MODULE_OUTPUT) stayed unfixed. This item removed the backtracker's five old indexes (keeping only _usage_by_name for find_required_modules) and the _resolve_binding_to_usage cascade, made _resolve_binding_via_registry the sole path and output_registry a required constructor parameter, migrated 39 tests off internal-index access, replaced the graph builder's three output-catalog-construction functions with OutputRegistry-backed lookups (research showed only the channel_name field of the old (module_type, channel_name, field_name) tuple was ever read, so registry.resolve() was a complete substitute), removed the Bug-2 xfail so it passes green, and ran E2E YAML-diff validation across all 4 models plus a new Issue 22 regression test.

**Key decisions**
  - A diagnostic determines whether Step 3.6 (_enrich_aliases_from_bindings) is dead code by building the registry without it and checking for divergence across all 4 models before any removal work begins
  - Research found the graph builder's output-catalog tuple exposed module_type and field_name but no consumer ever read them, so OutputRegistry.resolve() (returning only channel_name) is a complete direct replacement with no adapter needed
  - _usage_by_name is retained solely for find_required_modules() after all other backtracker indexes are removed
  - Test migration happens before the production cut-over commit so the cut-over diff only touches production code, not test setup
  - The Bug 2 xfail(strict=True) removal must land in the same commit as the backtracker cut-over, since a strict xfail that unexpectedly passes fails the suite
  - is_transitive on BindingResolution becomes permanently False after cutover since Phase 4 transitive aliases now resolve inside the registry, invisible to the backtracker

**Supersedes / retires**
  - The backtracker's _computed_attr_index, _aggregation_output_index, _output_catalog, and _design_attr_binding_index, plus the _resolve_binding_to_usage 7-strategy cascade and _compare_with_registry parallel-validation scaffolding
  - graph_builder.py's _build_output_catalog, _extend_output_catalog_with_computed_attrs, and _extend_output_catalog_with_aggregation functions
  - The Bug 2 xfail marker on test_bug2_regression.py

### TRUTH-DEBT  
*6 item(s), 2026-07-06 → 2026-07-08*


#### H-072 · 2026-07-07 — Item 4 Fix the computed-attribute classifier so inherited PartDef attributes classify FORMULA instead of silently-dropped EXPOSE_COMPUTED
`20260708_classifier-fix`  ·  subject: **computed-attribute classifier**  ·  status: **shipped**

The classifier's Step-2b sibling check used a QN-prefix test against the owning part's own namespace, so a reference to an inherited attribute (whose QN resolves into the supertype's namespace) fell through as a cross-namespace calc_ref and got misclassified EXPOSE_COMPUTED, which the graph builder silently drops with no module and no diagnostic. The fix widened Step-2b to accept a transitive ancestor-PartDef QN prefix, re-captured the affected extraction snapshot, flipped five xfailed tests into real positive assertions, added a D5 warn-and-skip diagnostic for the remaining not-fully-compilable case, and corrected doc/matrix text that had inverted the failure mode (called it a loud rejection when it was actually a silent no-op). Audited PASS: mutation-tested live, byte-identity scoped to one snapshot file, full suite green (2086 passed, 0 xfailed).

**Key decisions**
  - Step-2b now accepts any transitive ancestor-PartDef QN prefix, not just the owning part's own namespace, closing the inherited-attribute misclassification without over-broadening to genuine cross-part calc references
  - Doc/matrix text corrected from 'loud (EXPOSE_COMPUTED rejection)' to 'silent no-op', matching the actual graph-builder behavior
  - Added a D5 diagnostic (WARN + skip) for FORMULA-classified attributes that are not fully compilable, rather than leaving them silently dropped

**Supersedes / retires**
  - The five xfailed test cases documenting the classifier bug (INHERITED_ATTR_PATTERNS), replaced with positive-assertion passes
  - The prior 'loud rejection' framing in verification-matrix.md and the epic Item-4 text, corrected to 'silent no-op'

#### H-073 · 2026-07-08 — Item 1 Wire the consolidated resolve_input aggregation resolver into the live pipeline path, deleting the old channel-only function and its inline entry-point fallbacks
`20260708_f4-cutover`  ·  subject: **aggregation input resolution**  ·  status: **shipped**

resolve_input(AGG_STRATEGIES) had been built and parity-validated during PIPELINE-TRUTH but never wired into the live aggregation path, leaving the old _resolve_aggregation_input_channel function and three inline entry-point fallbacks as the authoritative code. This item reconciled resolve_input's fallback to reproduce the live path's richer entry-point construction (part-usage-prefixed keys, literal-default backfill, param-group classification, and the MANUAL_REQUIRED compilability signal), added a parity gate over the full InputSource before cutover, then deleted the old function, its three inline fallbacks, and the dead Strategy D stub. It also untangled a double-bound param_groups variable in graph_builder.py, clearing two mypy type-ignore comments. The aggregation baseline stayed byte-identical across the entire change (zero fixture churn), and the audit verdict was upgraded from PASS-WITH-NOTES to full PASS after the orchestrator reran the gate counts and mutation spot-check live.

**Key decisions**
  - Fallback ownership moved into resolve_input rather than keeping inline else-blocks at the three call sites, because resolve_input's fallback had to reproduce the live EP key format, literal-default backfill, and MANUAL_REQUIRED signal to avoid colliding an input entry point with an output channel
  - The parity gate compares the full InputSource the call-site block produces (channel plus entry-point fallback), not just the channel, because a channel-only gate is structurally blind to the entry-point-key divergence
  - Strategy D (DesignAttributeLookup) was deleted rather than implemented, since probing found zero live surface and it was a return-None stub
  - The aggregation baseline bar for this item is strict byte-identity, not byte-identical-or-reviewed-diff, since the reconciliation was designed to reproduce the live EP construction exactly
  - LocalTerm-EXPOSE was excluded from the fallback reconciliation because its undotted-ref key already matches resolve_input's leaf-only key

**Supersedes / retires**
  - _resolve_aggregation_input_channel (graph_builder.py) and its three inline entry-point fallback blocks (SumTerm, SingletonTerm, LocalTerm)
  - Strategy D (DesignAttributeLookup) stub in input_resolver.py
  - The double-bound param_groups variable and its two mypy type: ignore comments in graph_builder.py

#### H-074 · 2026-07-08 — Item 2 Resolve 3+-segment (multi-hop) calc-usage chain bindings to their upstream channel instead of hard-rejecting
`20260708_multihop-chain`  ·  subject: **backtracker chain resolution**  ·  status: **shipped**

A calc-usage parameter bound through three or more segments (e.g. station.array.derived_calc.derived_value) previously hard-rejected to an unbound entry point because the chain parser could not represent it. This item made extraction emit a full-path CHAIN binding for the deep chain, and gave the dependency backtracker an ancestor-scope climb (scoped_lookup only) that resolves it to the exact producing channel, refusing loudly (not silently truncating) when two ancestor scopes disagree. The prior epic's loud-reject contract for genuinely unresolvable chains was preserved, relocated to the backtracker's Step-4 WARNING. Audit verdict was PASS-WITH-NOTES, upgraded to PASS after gates were re-run live, a mutation spot-check confirmed the ambiguity guard was load-bearing, and a mis-attributed BACKLOG staleness note (ife_plant) was corrected to blame a pre-existing prior-epic drift rather than this item.

**Key decisions**
  - Deep-chain resolution added only to the calc-usage param-binding path (extraction + backtracker climb); the attribute value-binding path was already handled and left untouched (non-goal)
  - Climb uses scoped_lookup only, ordered after the 1-dot alias_lookup, to avoid colliding with existing alias resolution
  - On two ancestor scopes reaching distinct channels for the same chain, the resolver refuses (loud WARNING + entry point) rather than picking one, preserving the never-silently-truncate contract from the prior epic's Item 5
  - Re-capture scoped to only the deep_cross_scope_probe fixture; no other baseline was touched
  - No agentic-mbse code change needed; the deep chain shape was already valid SysML the adapter parsed

**Supersedes / retires**
  - The prior epic's loud hard-reject of 3+-segment calc-usage chains at extraction time (usage_extractor.py), which is replaced by resolution via the backtracker's ancestor climb; the loud diagnostic itself is preserved but relocated

#### H-075 · 2026-07-08 — Item 6 Harden four benign-leaning silent-fallback sites (D3 hygiene tail) so each fires a diagnostic on its silent shape or is formally reclassified
`20260708_hygiene-tail`  ·  subject: **silent-failure hardening, diagnostics**  ·  status: **shipped**

PIPELINE-TRUTH's earlier silent-failure hunt found four low-blast-radius sites that fall back quietly instead of surfacing a gap: the snapshot loader's .get() defaults on load-bearing fields (python_type, qualified_name, binding_type, scoping fields), a naive substring .replace() in aggregation compilation that can corrupt expressions when one attribute name is a substring of another (e.g. cost/cost_total), a registry type-map skip that silently drops unmapped exit-point types like 'Any', and a Phase-4 alias-rewrite branch with no else where sibling phases already warn. Three sites (loader, replace-to-regex, registry skip) were hardened with new diagnostics, each paired with an independently-anchored fires-on-shape test and a silent-on-clean sibling test, following the project's R1/R4 verify-then-fix discipline. The fourth site (transitive alias resolution) reproduced on 5 of 15 real corpus fixtures but its safe fix needed cross-module design work out of scope for a hygiene item, so it was deferred and filed to BACKLOG rather than shipped as a mechanical patch that would have broken the zero-WARNING invariant on clean corpora.

**Key decisions**
  - Harden at one choke point per site (loader's ~40 .get calls share one choke; no cross-site abstraction), since the four sites live in four unrelated modules.
  - Site 1's load-bearing subset (python_type, qualified_name, binding_type, parent_part_path, owning_part_def_qn) gets diagnostics; qualified_name (a keying field) raises, the rest warn; purely benign metadata fields (description, unit, source_line) are untouched.
  - Site 2 fixed via word-boundary regex substitution (re.sub with \b) instead of a placeholder pass, closing the prefix-collision corruption.
  - Site 3 gets its own diagnostic independent of Site 1, because 'Any' python_type is also minted on the live extraction path, not only from a malformed snapshot.
  - Site 4 is deferred (not mechanically fixed) because it reproduces on 5/15 real fixtures but the safe fix requires a cross-module derivation check beyond this item's scope; audit flagged the BACKLOG label 'RECLASSIFIED' as imprecise (R4 defines that term for non-reproducing findings) and recommended a one-line wording fix, non-blocking.

#### H-076 · 2026-07-08 — Item 5 Retire the verification-matrix sweep residue: 17 strengthens, 11 reframes, 5 citation fixes, and the unswept ~46-row tail
`20260708_matrix-sweep-residue`  ·  subject: **verification matrix integrity**  ·  status: **shipped**

PIPELINE-TRUTH Item 7 had run a leashed ~175-row deep-read of the verification matrix and found rows where the cited test passes but pins less than the requirement text claims (INV-B violations), filing 17 rows needing a strengthened assertion, 11 needing the text reframed down to what the test actually checks, 5 needing only a citation fix, and leaving ~46 qualifying rows unread. This item discharged that residue: strengthened the 17 (adding mutation-proven assertions, notably REQ-EC-04's internal parse-and-raise gate and REQ-AS-06's resolve-before-register gate), landed the 11 reframes as a byte-safe text-only batch, fixed the 5 citations, and completed the D7-qualifier read of the remaining rows rather than re-filing them wholesale, re-filing only the sub-budget overflow (32 rows named individually, 2 of which were deep-read) as `[ITEM5-SWEEP-RESIDUE-OVERFLOW]`. The audit found the item did what it claimed: mutation records for EC-04/AS-06 were concrete, the PGD-03 reclassification was a real over-claim retirement (not a laundered defect), and the matrix recount (259 rows, 258 PASS + 1 UNTESTED) reconciled exactly. Two strengthened tests (REQ-REG-06, REQ-OR-02) were flagged as advisory over-claims of their own coverage, non-blocking. Verdict: PASS-with-findings.

**Key decisions**
  - Complete the D7-qualifier read of the unswept rows at implement time rather than re-filing the whole ~46-row residue a third time; only genuinely budget-exceeding strengthens get re-filed, with a named count
  - REQ-PGD-03 was reclassified (text narrowed to a `>=` floor) rather than force-fixed to `== `, because the chain_spike fixture genuinely produces 1 group from 2 files and an exact-equality assertion would have been false
  - REQ-CA-01's INV-F over-claim (transient enum value never reaching a reader) is dropped from the row text because no cited test pins it and a sibling test treats the transient value as a valid classification member
  - DM-09 counted as one row with two defects (under-pinning text and a docstring-only marker), fixed together in a single strengthen row rather than double-counted

#### H-077 · 2026-07-08 — Item 3 Author independently-anchored tests for three UNTESTED verification-matrix rows (REQ-DM-08, REQ-RES-05, REQ-RES-08), flipping them to PASS with honest text reframes
`20260708_matrix-test-gaps`  ·  subject: **verification matrix test-gap closure**  ·  status: **shipped**

Three verification-matrix rows were marked UNTESTED with an argument standing in for a test. This item authored one independently-anchored pinning test per row and flipped all three to PASS in one change. REQ-DM-08 could not be flipped as originally framed -- re-verification found the documented model fields are still bare str, not the NewType wrappers the row's text claimed -- so the item ruled Route A: pin the actually-enforced surface (NewType wrappers plus the OutputRegistry's registry-dict and constructor annotations, using an AST scan since PEP-526 init-body annotations never populate __annotations__), reframe the row's text to match, and file the still-open model-field typing as its own backlog entry rather than fix it. REQ-RES-05 pinned build_computation_graph's real internal five-step call order, distinct from the existing outer-orchestrator pin. REQ-RES-08 required a similar text reframe (the row falsely claimed a universal ResolutionContext.consumer_scope mechanism, which FORMULA doesn't use) and ended up asserting four independently hand-derived legs across real fixtures: base consumer scope, the landed ancestor-scope climb, aggregation, and FORMULA's owning-part-keyed scoping. The audit (PASS verdict) independently traced every hand-authored expectation against real fixture and source content and found zero src/ changes, exact matrix recount, and consistent reframes across the matrix and both reference docs, but could not re-execute the suite or the three mutation red-green spot-checks because the audit sandbox blocked all process execution.

**Key decisions**
  - Route A ruling for REQ-DM-08: pin the enforced surface (wrappers + registry dict/constructor annotations) and reframe the row's text to that claim, rather than Route C (annotate the model fields, ruled out as production code churn outside a test-authoring item) or Route B (test the full table as a documented xfail, which would abandon the flip)
  - DM-08's enforced surface deliberately excludes register_alias's method params (ScopedKey | str / CanonicalChannel | str by design) -- the canonical surface is keys/values plus constructors, not method params
  - DM-08 test mechanism must be an AST/source scan, not typing.get_type_hints, because PEP-526 self.x: T assignments inside __init__ never populate a class __annotations__ and get_type_hints would stay green under the intended mutation
  - REQ-RES-08's row text is reframed to drop the false universal 'via ResolutionContext.consumer_scope' clause and instead state three per-path mechanisms, since FORMULA scopes via owning-part QN rather than that field
  - REQ-RES-05's test pins the inner build_computation_graph call order, explicitly not duplicating the existing outer build_pipeline_context pin (REQ-ORCH-01)
  - [DM08-MODEL-FIELD-TYPING] filed as a named backlog entry rather than silently dropped, per the epic's R1/INV-B honesty discipline

### PUSH-DOWN  
*4 item(s), 2026-07-08 → 2026-07-10*


#### H-078 · 2026-07-10 — Item 4 Split aggregation-expression handling so agentic-mbse owns neutral SysML decomposition facts and sysml-codegen keeps Python rendering and pipeline assembly
`20260720_aggregation-decomposition`  ·  subject: **aggregation decomposition boundary**  ·  status: **shipped**

The aggregation path in hierarchy_resolver.py mixed reusable SysML AST-walking (unwrapping invocations, classifying sum/singleton/local terms) with codegen-specific behavior (Python expression text, channel names, entry points, AggregationExpressionData). This item moved the reusable decomposition into agentic-mbse as a neutral fact-returning API, while sysml-codegen kept Python rewriting, aliasing, and pipeline assembly, rebuilding its existing AggregationExpressionData exactly from the shared facts. The SumTerm/SingletonTerm/LocalTerm dataclasses moved to agentic-mbse with sysml-codegen re-exporting the same runtime classes; a TYPE_MAP adapter-string inventory and an aggregation checking-profile disposition table were both required outputs. The item landed with a Certify audit verdict, zero sysml-codegen fixture churn, and a follow-up addendum that accepted an unpinned unary-minus rendering change as an improvement and added ** to the shared supported-operator set.

**Key decisions**
  - agentic-mbse owns only neutral aggregation facts (typed terms, literal/operator facts, wrapper disposition, unsupported diagnostics); sysml-codegen keeps all Python source generation, codegen identifiers, and AggregationExpressionData/HierarchyExtractionResult/ScopedAggregationData containers
  - Current permissive wrapper-unwrapping behavior (e.g. sum(filter(module.cost)) unwraps rather than warns) must not change in this item; any stricter wrapper warning is filed as separate profile work
  - Literal-before-invocation and feature-chain-before-operator AST dispatch order must be preserved and pinned by tests after the move
  - Aggregation-profile shapes (sum, singleton, local, wrapper, literal, unsupported node, operator) are each dispositioned as EXISTING, NEW RULE, FILED, or NO-OP with an exact rule/fixture/severity/rationale/backlog-ID row, rather than left unaddressed
  - No item-level PR closeout is performed here; PR preparation waits for the full PUSH-DOWN epic
  - Addendum: the pre-move vs post-move unary-minus render difference (-(x) vs -x) is accepted as a Python-semantically-identical improvement rather than reverted; ** was added to the shared SUPPORTED_OPERATORS set to avoid a future false-positive profile warning

**Supersedes / retires**
  - The prior hierarchy_resolver.py aggregation AST walker that mixed neutral SysML decomposition with Python rendering in a single sysml-codegen-local implementation

#### H-079 · 2026-07-10 — Item 1 Move reusable SysML expression reconstruction and literal-node helpers from sysml-codegen into agentic-mbse's shared SysML layer
`20260720_expression-reconstruction-push-down`  ·  subject: **expression reconstruction helpers**  ·  status: **shipped**

Reconstruction, feature-chain, chain-segment, and literal-node helpers lived only in sysml-codegen, so agentic-mbse could not reuse or validate against the same SysML facts codegen relies on without duplicating logic or creating a reverse dependency. This item moved the helpers into agentic_mbse.sysml.expression, introduced is_literal_node as a distinct name from the existing true-static-expression predicate, folded a duplicate literal-value helper in agentic-mbse's binding module into the shared one, and kept sysml_codegen.extraction.expression_utils as a permanent compatibility shim. The initial audit certified the move as behavior-preserving, but an independent epic audit on 2026-07-10 found two undocumented deviations from the original bodies (a widened membership-fallback gate and chain-segment fallback branches that only matched a test mock, not real syside nodes). Both were reverted to the pre-move originals and the test mock was corrected to match the real syside shape; both suites passed green afterward with byte-identical fixtures.

**Key decisions**
  - Dependency direction stays one-way: sysml-codegen depends on agentic-mbse.sysml, never the reverse
  - is_literal_node is introduced as the literal-node predicate name, kept distinct from agentic-mbse's existing is_literal_expression (which means true-static-expression), avoiding name overload
  - sysml_codegen.extraction.expression_utils is a permanent compatibility shim, not a temporary migration file, so old import paths keep working indefinitely
  - A move must be provably mechanical: the independent audit's finding of two undocumented behavioral deviations was treated as a correctness failure and both were reverted rather than kept as improvements

#### H-080 · 2026-07-10 — Item 3 Move the reusable SysML hierarchy primitive layer (redefinition and multiplicity extraction) from sysml-codegen into agentic-mbse
`20260720_hierarchy-primitives-models`  ·  subject: **hierarchy extraction, redefinition/multiplicity models**  ·  status: **shipped**

sysml-codegen owned reusable primitive SysML facts (:>> redefinition classification, multiplicity extraction, and the RedefinitionType/RedefinitionData/MultiplicityData dataclasses) mixed together with codegen-only hierarchy policy in hierarchy_resolver.py. This item moved only the neutral primitive layer into agentic-mbse as standard-library dataclasses, with sysml-codegen re-exporting the identical class objects and delegating extractor calls, while design-override filtering, usage-type indexing, aggregation decomposition, orchestration, and module construction stayed in sysml-codegen. Hierarchy-profile validation impact (redefinition precedence, multiplicity shapes, missing instantiations, ambiguous inherited attributes) was closed per-idiom in agentic-mbse or filed to its backlog with exact rule/fixture/severity. Certified after an independent epic audit remediation that removed an unpinned TYPE_CHECKING mirror-dataclass drift surface and strengthened a type-map inventory test.

**Key decisions**
  - Only the neutral primitive classifier/extractor and its three dataclasses move; design-level PartUsage scanning, override precedence, and aggregation stay in sysml-codegen.
  - Moved data models remain standard-library dataclasses (not Pydantic), with sysml-codegen re-exporting the exact shared class objects for identity.
  - Hierarchy-profile idioms needing usage-type indexing (missing instantiations, ambiguous inherited attributes) are closed by existing rules or filed to agentic-mbse backlog rather than moving indexing surfaces.
  - Remediation (2026-07-10): deleted sysml-codegen's TYPE_CHECKING mirror dataclasses in favor of a py.typed marker in agentic-mbse, and made the type-map inventory test assert against the real SysideAdapter map instead of a self-built fake.

#### H-081 · 2026-07-10 — Item 2 Split qualified-name utilities so SysML-general helpers move to agentic-mbse
`20260720_qualified-name-utility-split`  ·  subject: **qualified-name utilities module boundary**  ·  status: **shipped**

sysml_codegen.core.qualified_names mixed general SysML name operations with codegen-specific identifier builders, blocking reuse of the general helpers in agentic-mbse validation. Six SysML-general helpers (sanitize_name, build_element_qualified_name, sysml_to_python_qualified_name, sanitize_qualified_name, python_to_sysml_qualified_name, extract_simple_name) moved to a new agentic_mbse.sysml.qualified_names module; sysml-codegen kept a permanent compatibility re-export shim and retained the four codegen-owned builders (build_parameter_qualified_name, get_module_name, get_channel_name, owning_part_leaf) locally. The move was behavior-preserving with byte-identical fixture baselines and full suites green in both repos, certified with two remediation additions (an intentional-divergence marker and a docstring note) folded in after an independent epic audit.

**Key decisions**
  - sysml-codegen's import paths for the moved helpers are a permanent compatibility surface, kept as re-exports rather than removed.
  - Codegen-specific identifier builders (parameter/module/channel names, owning_part_leaf) stay in sysml-codegen because they encode ADR-003 policy, not general SysML semantics.
  - The existing agentic-mbse backlog row ITEM-SYNC-C8 (two names one identifier) was updated in place with the new shared sanitizer's rule, fixture shape, and severity rather than filing a duplicate row.
  - sanitize_qualified_name keeps its non-reentrant, apply-once-at-the-::-to-__-boundary contract; the split must not run it over an already __-joined name.

### CONSTRAINT-EXEC  
*9 item(s), 2026-07-12 → 2026-07-20*


#### H-082 · 2026-07-13 — Item 7 Generate the constraint module, Kleene predicate compiler, aggregator, and embedded catalog so a modeled assertion can actually execute
`20260713_constraint-generation`  ·  subject: **constraint code generation**  ·  status: **shipped**

Before this item, every layer upstream of code generation (constraint fact extraction, predicate compilation to a neutral IR, eligibility gating, lowering to ConcreteConstraint records, and module-kind plumbing) was in place, but nothing emitted the predicate code, constraint-module class, aggregator, runtime ConstraintEvaluation/ConstraintReport types, or embedded catalog, so a modeled assertion still could not run. Item 7 productionized the shapes proven by an earlier test-only spike (S4), filling the five generation seams that had been failing loud with a 'wired in Item 7' message. The audit verdict was Certify-with-notes: the Kleene three-valued logic, exit-pin guarantee, same-IR/leaf-name guards, and three Phase-4 bug fixes were verified correct by static review, but three named success criteria (indeterminate/negated-inline execution cases, modeled-default override changing the verdict, and a Break-the-YAML kept test) were deferred rather than delivered, and two of those had no test coverage at any level. Live/snapshot byte-identity for constraint-bearing fixtures was explicitly handed off as Item 8's job, not this item's exit gate.

**Key decisions**
  - Item 7's obligation was scoped to deterministic constraint_ids and catalog ordering across live loads, deferring artifact-level live/snapshot parity to Item 8
  - Three Phase-4 bug fixes were accepted as real structural corrections but shipped without a regression test in any CI-run lane, so a revert of any fix would stay green
  - Three named spec success criteria (SC-2 indeterminate/negated-inline execution, SC-3 default-override verdict change, Break-the-YAML) were explicitly deferred rather than delivered, and this deferral was surfaced honestly in the plan rather than silently dropped

#### H-083 · 2026-07-13 — Item 5 Productionized concrete constraint lowering: strict-resolution expansion of modeled assertions into graph structure with execution identity
`20260713_constraint-lowering`  ·  subject: **constraint lowering phase**  ·  status: **shipped**

Modeled assertions were extracted and classified but died at a drop-report warning, never reaching generated code. This item added the sysml-codegen phase that expands each assertion into its concrete design instances, resolves every actual through a strict resolver (real producer channel, real design attribute, or a named generation error, never synthesis), and mints a stable execution identity (constraint_id) per concrete assertion. It productionized the proven S4 vertical-slice spike shape, threading into build_pipeline_context at three points (resolve after group_deriver, inject roots before pruning, extend the graph after build_computation_graph), and stopped at graph structure only, leaving module/aggregator emission to Item 7. Audit found all six success criteria met with committed asserting tests, certified after an orchestrator-run addendum executed the live suite (2202 passed), a mutation probe, and two cures (documenting the as-built five-rung resolution ladder and adding a wired-path halt test).

**Key decisions**
  - Unresolved constraint actuals are always a generation error, never entry-point synthesis; the strict and lenient (calc) resolution modes share one code path with an explicit switch so they cannot silently diverge (the F4-cutover fallback-collapse lesson)
  - Expansion dispatches on the owner-kind axis (part_def, calc_def, package, requirement_def) and predicate selection dispatches independently on the source-form axis (inline vs definition_typed); the two axes are kept orthogonal
  - Registry-scope-before-design-attribute is the deliberate resolution order, reversing S4's incidental order, so an in-profile owner-scope reference to a sibling calc output is not mis-routed to a design attribute
  - Source-local constraint identity reuses the already-certified LocationFact (file/line/column) rather than inventing a new ordinal scheme
  - The strict resolution ladder was widened beyond the original three-rung design (adding scoped_alias_lookup and an occurrence-scoped design-attribute form), pre-authorized by design.md B4/R5, with the design doc left stale and flagged for later amendment

#### H-084 · 2026-07-13 — Item 6 Replace the is_computed_attribute/is_aggregation boolean flags on PipelineModule with a single module_kind enum, dispatched at all generation seams
`20260713_module-kind-refactor`  ·  subject: **PipelineModule kind dispatch**  ·  status: **shipped**

Generation code decided a module's kind by reading two accreted boolean flags on PipelineModule, with 'calculation' as the implicit else branch; a prior spike showed this could not represent an upcoming constraint kind without mis-rendering it as a calculation. This item introduced a five-member module_kind enum (calculation, formula, aggregation, constraint, report_aggregator), migrated all three construction sites and six generation-seam dispatch sites plus 22 test files and 9 baseline fixtures off the two flags, and made every seam fail loud (raise, never skip or mis-render) when it receives a constraint or report_aggregator module it isn't yet wired to handle. It was a pure refactor: byte-identity of the existing generated package corpus was the whole acceptance gate, and no constraint/report-aggregator emission was built. Audit verified the refactor by code trace and static grep in a sandbox that blocked test execution, then the orchestrator ran the four blocked dynamic gates (full suite, baseline round-trip, mypy/ruff, and a guard-deletion mutation test) live; one real mypy regression from the new error helper was found and fixed to restore the exact pre-item baseline, upgrading the verdict from certify-with-notes to certify.

**Key decisions**
  - module_kind is a required field with no default and no fourth ambiguous value, because no construction site ever sets both legacy flags, so the two-flag space's inconsistent fourth cell is provably unconstructible and safe to collapse away
  - Every generation seam that cannot yet render constraint/report_aggregator kinds must raise an explicit, identity-bearing error rather than skip or silently fall through to the calc path, per the epic's 'silence is never an outcome' principle
  - The test suite and 9 committed baseline fixtures are in scope for this item, not deferred as follow-on, because leaving them on the old flags would make the repo-wide zero-hit grep gate fail
  - The aggregation-vs-computed-attribute priority test was deleted rather than migrated, because the state it tested (both flags true) is unconstructible under the single-value enum
  - The refactor is decoupled from Item 8's snapshot-format version bump because module_kind is a ComputationGraph/graph field, not an extraction-snapshot field
  - mypy's 'clean' success criterion is reframed to 'no new errors versus the pre-item baseline' given standing project-wide mypy debt; the orchestrator later found and fixed a one-error regression to make even that reframed bar exactly hold

**Supersedes / retires**
  - The is_computed_attribute and is_aggregation boolean flags on PipelineModule, removed repo-wide (src and tests) and replaced by the module_kind enum

#### H-085 · 2026-07-13 — Item 4 Build a part-structure-only instance index (subtype closure + fixed-cardinality expansion) so constraint-only part definitions get discovered
`20260713_part-instance-index`  ·  subject: **part instance discovery index**  ·  status: **shipped**

Instance discovery was calc-driven: it derived instance paths only from virtual calculation-usage qualified names, so a part definition owning only constraints and no calculations produced zero discovered instances, and a plain subtype inheriting a base definition's assertion was invisible to exact-type lookup. This item built a new, additive production index (occurrences_of) derived purely from PartUsage structure and PartDefinition heritage: it projects a source owner over its full subtype closure and expands only fixed, finite, literal multiplicities to concrete occurrences, blocking with a named diagnostic (owner + feature) on any parameterized, variable, ordered, or unbounded cardinality rather than silently dropping or under-counting. It consumes only existing extraction facts, adds no new SysIDE facts, and does not touch or retrofit calc-driven discovery, so the existing generated corpus stays byte-identical. Audit found the specified occurrences_of entry point correct and fully tested, but caught a real defect in the bulk convenience methods (all_occurrences/all_source_owners), which silently swallowed the blocking exception per-definition -- a third, undocumented disposition that violated the item's own no-silent-omission invariant. That was cured (the bulk methods now return the occurrences plus an explicit blocked-owner mapping) and verified by live test execution, upgrading the verdict from certify-with-notes to certify.

**Key decisions**
  - The index is derived purely from part structure (PartUsage/PartDefinition heritage) and does not consume constraint fact schemas, letting it land before the constraint-fact items
  - A fixed multiplicity is defined strictly by node-type dispatch on the upper-bound expression, not by 'count is None', because a parameterized multiplicity still carries a non-None cached count and must still block
  - Fixed-multiplicity siblings are indexed as distinct entries keyed by owning definition plus feature (never bare leaf name), because leaf-name keying provably collides across different owning definitions
  - The index is strictly additive -- it does not retrofit subtype-closure projection onto existing calc-driven discovery, preserving byte-identity of the generated corpus
  - Bulk convenience methods must surface blocked definitions explicitly rather than silently skip them, since a completeness-named public method that silently drops entries is exactly the 'silence is never an outcome' failure the item exists to prevent

#### H-086 · 2026-07-13 — Item 8 Make constraint facts a load-bearing snapshot section and flip the from-snapshot default to lower constraints, closing live/snapshot divergence
`20260713_snapshot-v3`  ·  subject: **snapshot constraint parity**  ·  status: **shipped**

Before this item, constraint lowering ran only on the live pipeline; the from-snapshot rebuild path (build_full_graph_from_snapshot) never lowered constraints at all, so snapshots could not carry modeled assertions and the lowering feature defaulted off (22 measured live-vs-snapshot conformance divergences). This item made the neutral ConstraintFacts a versioned, load-bearing snapshot section, wired lowering into the from-snapshot rebuild so it re-derives the same extended graph offline (not by carrying a pre-computed catalog forward), made a current-version snapshot missing the constraint-facts section fail loudly with a re-capture instruction instead of silently generating an assertion-free package, and flipped the default on under a proven parity gate. The audit verdict was Certify. It explicitly does not emit constraint code itself, and full artifact-level parity depended on Item 7's generation work landing.

**Key decisions**
  - A current-version snapshot missing the constraint-facts section is treated as corruption and rejected loudly, never silently loaded as an empty catalog
  - Offline lowering must re-derive constraint IDs through the real lowering path from carried facts, not reload a frozen pre-computed catalog, to make the parity proof meaningful
  - The from-snapshot default for lowering constraints was flipped on once parity was proven, turning the prior 22 divergences into a parity test's baseline expectation to eliminate

**Supersedes / retires**
  - The prior from-snapshot rebuild path's silent lack of a constraint phase, and the lowering feature's default-off posture from Item 5

#### H-087 · 2026-07-13 — Item 14 Retire the drop-manifest era, flip authoring docs to the executable profile, and pass IFE-sweep acceptance against the generated viability assertion
`20260713_constraint-migration-acceptance`  ·  subject: **constraint catalog migration, docs, IFE acceptance**  ·  status: **shipped**

This was CONSTRAINT-EXEC's epic-closing item. It fixed a prerequisite extraction gap (materialize_supplied_values did not synthesize a design attribute for a top-level instance self-redefinition, blocking fusion_tea's viability assertion from lowering), retired the old drop-manifest reporting surface behind a proven per-usage 1:1 manifest-to-catalog mapping test, flipped authoring and architecture docs from 'constraints are not executable' to teaching the executable profile, and replaced the fusion-tea IFE sweep's hand-coded viability rule with the generated assertion consumed through the study layer. Acceptance matched 2294/2301 grid rows exactly; the 7 divergent rows were boundary cases where the old hand rule's strict '>' was less faithful to the model's '>=' than the generated assertion, so audit treated the divergence as the epic's thesis proving itself, not a failure. Audit verdict was certify-with-notes: it flagged that acceptance should be recorded as ~99.7% plus a correcting divergence rather than a bare '100%', and identified three integration gaps (no standalone constraint_catalog.json artifact, a single-entry-channel-only CandidateBridge, a hardcoded ToyPlantParams in PreparedEvaluator) that narrow the claim surfaces of Items 9, 12, and 10 respectively and should become follow-on items rather than permanent adapters.

**Key decisions**
  - The gain extraction gap is fixed with a demand-scoped, literal-only tier in materialize_supplied_values/resolve_actual rather than a broader synthesis mechanism, keeping the fix's blast radius to exactly two fixtures (fusion_tea, plant_values)
  - The manifest-to-catalog migration is verified by a kept per-usage mapping test (not a count match) before any retirement code is deleted
  - collect_constraint_manifest and its kind vocabulary are kept (deviating from the design's stated deletion target) because the kept mapping test still calls the sweep directly
  - The generation-halt diagnostic for out-of-profile constraints is explicitly kept; only the blanket drop-manifest warnings are retired
  - The 7-row acceptance divergence is treated as a correcting divergence (model's inclusive >= is more faithful than the old hand rule's strict >), not an acceptance failure, and should be recorded as such rather than claimed as literal 100% match
  - Three consumer-side integration gaps surfaced during acceptance are recorded as narrowings of certified Items 9, 10, and 12 and must become tracked follow-on items rather than permanent shims

**Supersedes / retires**
  - The drop-manifest reporting era (extraction/constraint_report.py, its two blanket 'not executable' warnings, and the snapshot dropped_constraints section), retired in favor of the constraint catalog as the single source of truth
  - The fusion-tea IFE sweep's hand-coded Python viability rule, replaced by the generated assertion consumed via the teax study layer
  - Authoring guidance in docs/architecture/modeling-assumptions.md section 8 that taught constraints are dropped/not executable

#### H-088 · 2026-07-13 — Item 13 Retire the legacy ExpressionAST calc-side tree, moving all calc consumers onto ExpressionIR plus a byte-identical compat renderer
`20260713_expression-ast-cutover`  ·  subject: **expression tree retirement**  ·  status: **shipped**

sysml-codegen carried two semantic expression trees: the neutral, serializable ExpressionIR that constraint predicates already compiled from, and the older calc-only ExpressionAST, which had to be kept in lock-step by hand. A prior spike proved a small codegen-side compat renderer over ExpressionIR reproduces ExpressionAST's compiled output byte-identically. This item migrated the two real calc consumers (compile_calc_def's seam and computed_attribute_extractor) onto the IR plus renderer path, each gated by a per-function byte-identity parity test against the exact function it replaced, then deleted ExpressionAST, build_expression_ast, and compile_expression, backed by a grep gate. The spec's own scope trace found that epic Item 13's listed aggregation-walking consumer never actually used ExpressionAST (it runs on agentic-mbse's separate shared_aggregation tree), so that consumer was correctly dropped from scope with the correction recorded rather than silently absorbed. The audit's initial verdict was Certify-with-notes because the sandboxed session could not run pytest/mypy/ruff itself; the orchestrator then executed the four requested live probes (full suite 2317 passed/23 skipped, mypy at the 76-error baseline, ruff clean, package/snapshot byte-identity, and independent golden-provenance reproduction), upgrading the verdict to unconditional Certify.

**Key decisions**
  - Scope correction: aggregation walking is dropped from Item 13 (it runs on agentic-mbse's shared_aggregation tree, never on ExpressionAST); converging shared_aggregation onto ExpressionIR is recorded as a separate future cross-repo item, not done here
  - Each staged consumer's parity gate compares against the exact function it replaces, captured before the flip, never a downstream proxy artifact (the comparand-discipline lesson from a prior item)
  - CompilationResult/CalcDefCompilationResult data model shape does not change; this is representation migration on the producing side only
  - Byte-identity baseline is the post-Item-8 (Snapshot v3) corpus, and Item 13 sequences after Item 8 certifies

**Supersedes / retires**
  - ExpressionAST, build_expression_ast, and compile_expression, deleted and grep-gated out of src/

#### H-089 · 2026-07-13 — Item 9 Build production ModelContract/PackageContract sealing so a generated package's identity and integrity can be verified on load
`20260713_package-contracts`  ·  subject: **package sealing, contracts, fingerprints**  ·  status: **shipped**

A generated package was a loose directory with no way to verify it was untampered or to bind a study run to a stable identity. This item made the S4 spike's throwaway test-only seal into production code: a graph-only ModelContract (semantic fingerprint over parameters, outputs, constraint catalog) and a PackageContract (executable fingerprint via content hashes over generated and preserved artifacts), verified on load via a stdlib-only verify.py shipped inside the package. It closed the two gaps the spike left open: detecting a coverage-set file missing from disk (not just extra files) and an environment-compatibility check with a named diagnostic. Certified after live probes ran the full suite green (2282 passed), a mutation probe proved the extra-file detection has teeth, and a follow-up cure added a drift guard so the seal-producer and verify-consumer glob matchers can never silently diverge.

**Key decisions**
  - ModelContract derives solely from ComputationGraph fields (graph-only, no filesystem/YAML access); 'provided capabilities' (backends, persistence modes) are runtime facts kept out of it and belong to PackageContract instead.
  - Sealing runs as CLI generation Step 9, with a separate `seal` subcommand for re-sealing after handwritten stencils are filled in (recomputes PackageContract only; refuses a directory with no prior ModelContract).
  - Environment-compatibility check compares only the runtime_version axis; GENERATOR_MISMATCH is reserved-but-unreachable, deferred as a documented seam to Item 10/14 integration work.
  - verify.py is stdlib-only and emitted verbatim into every package (no in-repo import), with a byte-identity drift test against the in-repo source; a body-equality test was added post-audit to guard against the seal producer's and verify consumer's glob-matcher functions silently diverging.
  - Integrity failures (tamper, extra, missing) are always fatal; environment mismatches are advisory by default, fatal only under strict mode.

**Supersedes / retires**
  - S4 spike's test-only ModelContract/seal/verify_seal code (s4_lib.py), which never declared its coverage set explicitly, never detected missing coverage-set files, and never checked environment compatibility.

#### H-097 · 2026-07-20 — Item 13 Composed public proof for the CONSTRAINT-EXEC lifecycle register: all 41 Appendix C cells pass at a pinned five-repo revision set
`20260720_constraint-lifecycle-composed-proof`  ·  subject: **constraint execution lifecycle release proof**  ·  status: **shipped**

This item composed the final release-readiness evidence for the CONSTRAINT-EXEC epic's lifecycle contract (register row 17), certifying that all 41 Appendix C matrix cells pass across five pinned repos (sysml-codegen, agentic-mbse, teax, fusion-tea, stellarator): 22 reruns, 19 composed proofs, 0 inherited, all PASS, plus 16 negative mutations failing at their intended boundary and 6/6 full-tree byte-identity checks. The codegen src tree was proven byte-identical to the certified pin 7526665 with the branch tip only adding docs and Item-13 fixtures. It established the required merge order (agentic-mbse PR #11 must land before sysml-codegen PR #9 because codegen's pinned upstream schema/profile version strings are asserted against the installed agentic-mbse), pushed all three epic-authorized branches as fast-forwards, and left fusion-tea and stellarator branches local by explicit human delivery decision. Merge itself was left to a human, not performed by this item.

**Key decisions**
  - Case 18 (definition-owned assert through redefining usage) was closed as a fixture-shape error in the Stage-2 contract row, not a resolver bug -- Item 2's resolver was correct all along
  - A general nested-occurrence-override gap (definition-relative capture vs occurrence-relative demand) was isolated from the Case-18 investigation and filed to the Item-10 occurrence-materialization family rather than fixed here
  - Required merge order is agentic-mbse PR #11 first, then sysml-codegen PR #9, because test_upstream_pins would fail on codegen main if the downstream pin landed before the upstream version strings it points to
  - agentic-mbse commit 4c18d61 is pushed to PR #11 carrying an unrelated 'modeling workflow orchestrator' commit (4ed2a07) in its ancestry, by prior owner direction, flagged for the reviewer rather than excluded
  - fusion-tea and stellarator branches stay local; their delivery path was not epic-authorized for push
  - Pre-existing baselines (two -O suite failures, ruff format's 22 files, mypy's 72 errors, deep_cross_scope/plant_values stale baselines) are recorded as inherited from the pin and explicitly not treated as certification blockers

### CONSTRAINT-LIFECYCLE-REMEDIATION  
*13 item(s), 2026-07-19 → 2026-07-20*


#### H-090 · 2026-07-20 —  Ratify one authoritative end-to-end contract for constraint execution across agentic-mbse, sysml-codegen, and TEAx
`20260720_constraint-execution-lifecycle-contract`  ·  subject: **constraint execution lifecycle**  ·  status: **unknown**

Constraint execution had accumulated correct individual pieces (extraction, profile validation, lowering, catalog, TEAx evaluation) with no single authoritative description of how they compose, and several certified components failed when combined in a real whole-plant route; recent defects had repeatedly crossed seams that local tests treated independently. This spec is a large ratified target-architecture document (owner-verbatim: 'Ratified.') spanning responsibility/authority, neutral fact extraction, the executable numerical profile, concrete lowering and actual resolution, graph extension and catalog generation, snapshot/contract/package integrity, runtime evidence and study execution, supported integration seams, and proof obligations, with three explicit owner decisions (no public late-fill graph mutation; direct literal design attributes are valid constraint actuals without a passthrough calculation; the embedded codegen catalog is TEAx's sole schema authority). It explicitly records that proof was NOT established at ratification time (the codegen/agentic-mbse/TEAx trees were not a mutually installable committed candidate set) and defines an 18-row dependency-ordered open implementation register (rows 0-17) to be executed by a companion epic, with certification following register order and the composed public proof running last.

**Key decisions**
  - The lifecycle contract becomes the single normative architecture description after ratification; where original concepts, completed specs, public docs, or PR bodies disagree, this contract's correction register governs
  - Owner Decision 1: no public late-fill or post-build graph/default mutation is supported; the lifecycle requires a fully representable graph plus ordinary declared external inputs
  - Owner Decision 2: direct literal-valued design attributes are valid constraint actuals via direct shared producer/exact-QN resolution, not model-authored passthrough calculations; this supersedes the same-day owner-ratified WI-027 D7 passthrough design
  - Owner Decision 3: codegen's embedded model-contract catalog is the sole schema authority TEAx consumes directly; the alternate TEAx schema, fusion materializer, and identity stand-in are deleted
  - Proof is explicitly NOT established at ratification; certification is deferred to a companion epic's 18-row dependency-ordered register, executed in order with the composed public proof (row 17) running last
  - Ratification of the target architecture proceeds independently of and does not wait on the commit-pinned installable candidate set

**Supersedes / retires**
  - the old equality matrix
  - the old whole-graph extension-time V11 invariant
  - stale profile-version claims
  - the 'profile is codegen-only' description
  - owner-ratified WI-027 D7 passthrough-calculation design (superseded by Owner Decision 2)
  - the alternate TEAx-side catalog schema, fusion catalog materializer, and identity stand-in (superseded by Owner Decision 3)

#### H-091 · 2026-07-19 — Item 0 Pin one compatible agentic-mbse/sysml-codegen/TEAx/fusion-tea/stellarator revision set as the epic's starting baseline
`20260720_constraint-lifecycle-candidate-pin`  ·  subject: **cross-repo version pinning**  ·  status: **shipped**

Before constraint-lifecycle remediation work could start, the epic needed one committed, installable revision set across five repositories with stable hashes and a production-code line-count baseline for later items to compare against. This item reconciled the local and remote agentic-mbse PR #11 lines with a non-destructive merge, selected matching sysml-codegen and TEAx revisions, and ran narrow install/import/profile-v4 smoke checks rather than full certification. It recorded exact commits, lockfile digests, and a per-repository production LOC table in evidence.md, and explicitly scoped itself as non-certifying integration bookkeeping — later items (4, 7, 8, 12, 13) still own schema, runtime, catalog, legacy, and composed-lifecycle proof obligations. No push or PR update was performed.

**Key decisions**
  - Treat this item as non-certifying bookkeeping only — it establishes a compatible pin, not lifecycle correctness, leaving certification to Item 13
  - Reconcile agentic-mbse's local and remote PR #11 tips with an ordinary merge rather than branch surgery or patch replay, per owner direction to keep the committed modeling-orchestrator commit intact
  - Record a reproducible production LOC baseline (tracked .py/.jinja2/.sysml, excluding tests/fixtures/generated/docs) so later items can measure their touched-file footprint against it

#### H-092 · 2026-07-20 — Item 8 Make codegen's embedded constraint catalog the sole schema authority; delete TEAx's parallel reconstructed catalog and its byte-hash fingerprint stand-in
`20260720_constraint-lifecycle-catalog-store`  ·  subject: **constraint catalog identity**  ·  status: **shipped**

Codegen already assembled a real constraint catalog inside the model contract, but TEAx ignored it and instead consumed a separately-shaped constraint_catalog.json built by a hand-authored fixture and a fusion-side materializer, reconstructing owner QN, definition QN, and source form by string-splitting and predicate-text search, and binding store compatibility to a byte-hash of that alternate file rather than codegen's real semantic_fingerprint. Per owner decision D-3 ('100% Option A, purge this mess'), this item added the missing fields (source_form, owner_qualified_name, definition_qualified_name, usage identity, an admitted-usage tier) to codegen's embedded ConstraintCatalogEntry, rewired TEAx to consume that catalog and the real semantic_fingerprint directly as on-disk JSON, deleted the alternate schema, the standalone fixture, and the fusion materializer across all three repos (codegen, teax, fusion-tea), and made catalog/schema skew fail closed with a named error in both directions. The audit certified the item with two moderate but non-blocking findings: the FK-gating regression test never exercised the named-inline case (code was correct, guard was vacuous), and the INV-6 source-scan test the spec explicitly required was never written, though the reconstruction anti-patterns were independently grep-verified absent across all three repos.

**Key decisions**
  - Owner decision D-3 settled: purge the alternate catalog system entirely rather than shim it; codegen's embedded catalog becomes the sole schema authority (Option A over a rejected Option B standalone canonical export)
  - TEAx continues to consume codegen identity as on-disk JSON, never by importing sysml_codegen, preserving the deliberate cross-repo dependency boundary
  - The fusion deletion target was corrected from the brief's named repo (fusion-tea-stellarator-mbse-demo, which had no such code) to the actual location at fusion-tea/exploration/ife_e2e/study/, surfaced and resolved before the deletion inventory was finalized
  - CatalogView/_Catalog names in TEAx were rewired/repurposed to read the embedded catalog rather than literally deleted, a design-level reframe of the spec's 'no surviving symbol' criterion that the audit flagged as under-reconciled
  - Store compatibility transition relies on the existing eight-field _check_compatibility gate to fail closed on the new fingerprint value, rather than building a new migration mechanism

**Supersedes / retires**
  - TEAx's alternate constraint_catalog.json schema, its CatalogView/_Catalog reconstruction logic, the hand-authored fixture, and the byte-hash fingerprint stand-in in study/config.py
  - The fusion-tea catalog materializer (materialize_constraint_catalog.py) and its committed generated/contracts/constraint_catalog.json artifact

#### H-093 · 2026-07-20 — Item 4 Diagnostic severity/closed codes, warning-vs-BLOCK ordering, modeled-default fidelity, and the written-reference carry closing SR-A02
`20260720_constraint-lifecycle-diagnostics-defaults`  ·  subject: **constraint diagnostics and modeled defaults**  ·  status: **shipped**

Extraction diagnostics carried no severity and had zero consumers, warning rendering could silently swallow the actionable BLOCK halt, signed/unit-annotated modeled defaults were dropped without any diagnostic, and default parsing was duplicated across six lanes. The item added a writer-fixed DiagnosticSeverity field with closed kind/reason vocabularies (bumping the fact schema to v2 and the snapshot envelope to v4, requiring a re-capture of all 34 fixtures), made the warning pre-pass degrade to a fallback location instead of raising so it can never preempt the BLOCK halt, replaced the default parser with a structural IR resolver that unwraps units and folds signs, and landed the written-reference carry so a shared attribute converges to one entry point across calc and constraint consumers. Went through three audit rounds: round 1 found the snapshot-route sink ran after lowering and the reference carry silently re-anchored a qualified reference onto a wrong local shadow (masked by a value coincidence); round 2 found the fix for that regressed a different binding; round 3 closed all findings by keying the carry off the CST-captured scope qualifier rather than resolved-QN indexing. Certified Pass with notes, coordinated across sysml-codegen and agentic-mbse (PR #11 before PR #9).

**Key decisions**
  - Severity is fixed at construction on the writer side and travels with the data (a field), not a reader-side kind-to-severity lookup table, because the snapshot route lets reader and writer be different commits and a table could silently reclassify already-captured diagnostics.
  - Diagnostic classes stay separate (EligibilityDiagnostic.force is not merged into the shared severity enum); only the severity type and closed-code discipline are shared.
  - Two production sinks (codegen pre-lowering halt, agentic-mbse L6 authoring) rather than a routing/registry layer.
  - Unsupported modeled-default IR is disposed as explicitly-unresolved (null in generated JSON, diagnosed) rather than fail-generation, since the IR shape can be a legitimate model.
  - The written-reference carry rides existing serialized fields (source_attribute_name/source_instance_name) behind stored fallbacks rather than adding a new extraction field, so it works on unmodified v3 snapshots and needs no agentic-mbse change.
  - Row 16 of the shared resolver gets two dedicated request fields (written_reference, occurrence_owner_path) read at exactly one site, so no other resolver row's input changes for any consumer.
  - The carry lands before the schema/severity work so each forced baseline diff has one cause.
  - Bracketed (occurrence-indexed part_def) owners are deliberately left as a resolver miss rather than attempting convergence; unbracketed PartUsage-owned shapes converge.
  - Amended mid-implementation: written_reference must be the full written form (instance.attribute for chain bindings), not the leaf name alone, after a leaf-only carry was found to silently re-anchor to a wrong same-named attribute.

**Supersedes / retires**
  - The leaf-only written_reference carry design (B2/D4 as originally stated), replaced after a measured wrong-anchor regression
  - The premise in tests/fixtures/shared_producer/PROVENANCE.md that the written reference is structurally unreachable from the calculation consumer
  - Item 2's referral note that convergence needed a snapshot format bump
  - Silent omission of an unresolvable modeled default's JSON key (generation/entry_point.py)
  - The bare _literal_float default parser and several duplicate string-based default-parsing lanes

#### H-095 · 2026-07-20 — Item 1 Rebuild the occurrence/demand lifecycle thread as one identity-preserving path through public live generation
`20260720_constraint-lifecycle-occurrence-demand`  ·  subject: **occurrence expansion, demand materialization**  ·  status: **shipped**

The constraint path had correct finite-occurrence and supplied-value pieces but they did not compose: demand discovery could alias anonymous usages, the part-instance walk silently treated a revisited definition as an empty subtree (masking recursion), and calculation/constraint actuals could be appended as duplicate records that overwrote earlier grouping provenance. Item 1 rebuilt these into one complete identity-bearing thread (verified association, an all-or-nothing prepared batch, explicit owner dispatch, structural cycle failure, one logical demand per normalized target) and deleted the superseded nullable and duplicate paths rather than wrapping them. An initial audit pass returned Needs work on two blockers (a resolved-value regression and an undisclosed byte-identity gap); both were closed and re-verification certified the candidate with recorded deviations.

**Key decisions**
  - Owner kind controls occurrence expansion and source form controls predicate selection, kept as independent axes (OD-R01, inherited from lifecycle LC-D01).
  - Every finite concrete occurrence gets its own execution identity, catalog entry, module, and result channel; sharing must be recorded in per-occurrence bindings (OD-R02).
  - Recursive, non-finite, malformed, or unsupported occurrence expansion must block loudly rather than return a partial result as complete (OD-R03).
  - Superseded production paths are removed outright, not wrapped, flagged, or kept as dead fallback (OD-R40).
  - Item scope is bounded: Item 2 owns the shared producer/exact-QN resolver, Item 5 owns relocated whole-tree portability, Item 13 owns the final sealed load/evaluate/persist proof (OD-R05).

**Supersedes / retires**
  - The nullable qualified-name-set membership approach to demand discovery, which allowed anonymous admitted/excluded usages to alias.
  - The part-instance walk's silent empty-subtree treatment of a revisited definition, which could mask recursion.
  - The appended-record model for calculation bindings and constraint actuals, which allowed duplicate overwrite of grouping provenance.

#### H-096 · 2026-07-20 — Item 2 Replace three drifted producer-resolution ladders with one shared resolver and make Gate A resolve literal design-attribute constraint actuals
`20260720_constraint-lifecycle-shared-resolution`  ·  subject: **producer resolution, constraint Gate A**  ·  status: **shipped**

Three independently ordered resolvers (calculation ladder, constraint ladder, aggregation ladder) answered the same producer-resolution question but had already drifted apart in ordering, candidate identification, and miss handling; the aggregation ladder in particular resolved leaf-name collisions by silently picking the first candidate, and Gate A could not resolve a literal design attribute owned by a concrete PartUsage even though owner decision D-2 requires it to be a valid constraint actual. This item deleted the three consumer-specific ladders and replaced them with one production resolver serving all consumer types, so a direct literal design attribute now resolves under its real qualified name with no passthrough-calculation workaround, and no verdict is produced from a guessed or defaulted binding while V11 reports clean. Independently audited Pass with notes: the code and behavior are sound and reproduced under full suite, -O, real-simkit, byte-identity, and EP-key manifest gates, but the evidentiary record (D2 falsification table, one forced-difference corpus count) diverged from what the shipped code actually does in six correctable, non-production-affecting places.

**Key decisions**
  - One production resolver serves calculation, aggregation, and constraint consumers; the three consumer-specific ladders (dependency_backtracker.py, constraint_lowering.py, input_resolver.py-driven aggregation) no longer exist, per owner-ratified contract invariant 20.
  - Owner retired every numeric LOC gate epic-wide on 2026-07-19 (epic commit a1435e1); this item's simplification is judged structurally per SR-R40, with no LOC target/budget/gate, superseding the epic text's stale '300-500 line reduction' scope point.
  - SR-A02/SR-R23 were not delivered in this item and were referred to Item 4 (design PC-4); every other requirement was met.
  - A direct literal design attribute owned by a concrete PartUsage, referenced by a self-named actual, must resolve under its real qualified name with no passthrough calculation (owner D-2, 2026-07-19).

**Supersedes / retires**
  - The calculation-ladder resolver (analysis/dependency_backtracker.py), the constraint-ladder resolver (analysis/constraint_lowering.py), and the aggregation-ladder resolver path in resolution/input_resolver.py and graph_builder.py, all deleted in favor of one shared resolver.
  - The stellarator consumer's passthrough-calculation workaround for design-attribute constraint actuals, superseded by direct Gate A resolution.

#### H-098 · 2026-07-20 — Item 6 Reconcile public docs and F1 evidence with landed constraint-execution-lifecycle code
`20260720_constraint-lifecycle-docs-f1`  ·  subject: **docs and snapshot version claims**  ·  status: **shipped**

Public documentation and audit evidence had drifted from landed code across several prior items: docs cited stale snapshot format versions, a stale executable-profile version, a stale agentic-mbse dependency floor, and duplicate hardcoded version-literal error strings, while the TEAx F1 normalization audit cited the wrong commit. Three independent inventory sweeps (version literals; snapshot/V11-gate/catalog; equality-ordering/subtype/diagnostics) classified every claim as STALE, ACCURATE, GAP, or AMBIGUOUS, and this item corrected the eight STALE claims (S1-S8) with code citations, single-sourced the two duplicate version-literal error strings from PROFILE_SEMANTIC_VERSION, fixed the F1 audit's commit reference from 927a9e1 to d545701, and added a RED-first fix so an explicitly invalid TEAX_SIMKIT_PATH fails instead of silently falling back to sibling discovery. Two real documentation gaps (undocumented diagnostic severity field; missing verification-matrix row for the Item 5 portability gate) were surfaced but explicitly left unfixed as other items' territory. Independently audited and certified with no blocking findings.

**Key decisions**
  - Only claims with a code citation proving them stale are 'corrected'; undocumented-but-real behavior (diagnostic severity, Item 5 portability) is recorded as a GAP, not silently fixed here, per the correction law
  - TEAX_SIMKIT_PATH: an explicitly set path is authoritative and must fail loudly if invalid, rather than silently falling back to sibling discovery
  - Duplicate hardcoded 'executable-profile/v3' error strings in predicate_compiler.py are single-sourced from PROFILE_SEMANTIC_VERSION so they cannot re-drift

**Supersedes / retires**
  - Doc claims of snapshot format 'current: 3' (actual: 5), executable-profile v3 (actual: v4), and agentic-mbse floor >=0.1.1 (actual: >=0.1.2) are all corrected
  - F1 audit's cited commit 927a9e1 replaced with the correct d545701

#### H-099 · 2026-07-20 — Item 11 Make TEAx constraint evidence durable: tolerate missing reports, freeze evidence against mutation, pin failure phases, and settle OUTPUT_WRITE
`20260720_constraint-lifecycle-evidence-durability`  ·  subject: **TEAx constraint evidence**  ·  status: **shipped**

TEAx turns a generated package's constraint outputs into durable study evidence, but three parts of that path were unsound: both evaluator routes crashed with a KeyError on a constraint-free package because they read the constraint_report channel unconditionally; the authoritative ModelEvidence was only shallow-frozen, so downstream policy code could mutate nested status, margin, or results on the live unfrozen report objects codegen generates, protected only by an incidental serialize-before-policy ordering accident; and EvaluationPhase.OUTPUT_WRITE was defined but never emitted, with failure phase agreement resting on the two evaluators simply matching rather than a pinned fixture expectation. This item fixed all three: one report-absence-tolerant read path replaces the two unconditional reads, evidence is sealed into a deep-frozen mappingproxy/tuple tree that defeats nested mutation, OUTPUT_WRITE is emitted off a positive in-output-write signal (never inferred from exception type or a null key), and fixture-pinned expected phases replace evaluator-agreement. It also proved excluded-only (zero-eligible, not_assessed) and constraint-free (zero-usage, empty evidence) are distinct evidence surfaces. The audit certified the item, reproducing the immutability, phase-signal, and catalog-authority mechanisms independently; findings were all minor (a catalog-to-corruption production path proven only in two separate halves, an overstated 'golden byte' framing, and a latent hardcoded fallback path for a future multi-group case).

**Key decisions**
  - Immutability lives on the TEAx side at the projection boundary, deep-freezing into a TEAx-owned mappingproxy/tuple tree, because codegen's generated report models are plain unfrozen pydantic and TEAx cannot force codegen to freeze them
  - OUTPUT_WRITE is emitted (not collapsed) off a positive in-output-write context flag set immediately before write and cleared only on success, so a mid-write exception is stamped OUTPUT_WRITE and every other failure stays MODULE_EXECUTION
  - The corruption path for an absent report on a constraint-bearing catalog raises a dedicated CorruptConstraintEvidence error deliberately outside EvaluationFailed, so it crashes past the runner's except clause rather than being swallowed as a normal evaluation failure
  - The incidental encode-before-policy ordering in the runner is removed as no longer load-bearing once deep-freeze owns immutability; encode_evidence is called inline at each commit site instead
  - The spec's opening premise that Item 9 already reproduced the constraint-free KeyError was corrected as unsupported by Item 9's own record; reproducing that RED became this item's own first implementation step rather than an inherited fact

**Supersedes / retires**
  - The two duplicated unconditional constraint_report reads in evaluator.py
  - The incidental encode-before-policy ordering in runner.py that had been the only protection for persisted evidence

#### H-100 · 2026-07-20 — Item 12 Fail closed on grandfathered (unlowered) snapshots before sealing, and delete the dead tracking_key correlation field
`20260720_constraint-lifecycle-legacy-identity`  ·  subject: **grandfathered snapshot gating**  ·  status: **shipped**

Two loose ends let a generated package look certified while resting on nothing: generate --from-snapshot on a grandfathered_off snapshot (lowering disabled at capture) only warned and silently dropped constraint assertions before sealing a package, and ConcreteConstraint.tracking_key was documented as a cross-version correlation key but had zero writers, zero readers, and never reached a serialized snapshot. The fix added a fail-closed gate at the generate command (not in seal_package, which is pure over the directory, and not in the shared inspection helper, which legitimately loads grandfathered probes) that raises before preflight, output, or seal; deleted the capture-time lower_constraints_enabled opt-out so a lowerable model can no longer be captured grandfathered; kept the grandfathered_off mode itself as the honest label for the 7 extraction-only probe snapshots that cannot be lowered at all; fixed a latent bug where every from-snapshot context misreported its mode as the dataclass default grandfathered_off regardless of the real snapshot; and deleted tracking_key entirely. An independent audit reproduced the pre-gate silent drop directly (1 usage to 0 catalog entries) and certified all six criteria with the full licensed suite green (3115 passed, 0 failed) and no format bump.

**Key decisions**
  - The fail-closed gate lives at the generate command boundary, not in seal_package (pure over directory, no context access) or the shared from-snapshot read-path helper (used by legitimate inspection tests on grandfathered probes)
  - grandfathered_off is retained as an honest inspection-only state for extraction-only models that cannot be lowered, rather than deleted outright
  - The capture-time lower_constraints_enabled opt-out for full-pipeline (lowerable) models is deleted; only extraction-only capture can still produce grandfathered_off
  - tracking_key is deleted rather than fully implemented, since no consumer correlates across versions today
  - The live build_pipeline_context(lower_constraints_enabled=...) test flag is kept since it serves 4 conformance tests and never reaches the sealed/certifying path

**Supersedes / retires**
  - capture_snapshot's lower_constraints_enabled parameter and the GRANDFATHERED set plumbing in scripts/capture_extraction_snapshots.py
  - ConcreteConstraint.tracking_key field, its docstring, and its round-trip test
  - the epic contract's cross-version correlation non-goal claims that leaned on tracking_key

#### H-101 · 2026-07-20 — Item 9 Make TEAx's study candidate bridge build complete typed mappings for zero, one, or many entry channels, and delete the stale fusion consumer wrapper that patched around the single-channel limit
`20260720_constraint-lifecycle-multi-entry`  ·  subject: **TEAx study candidate bridge**  ·  status: **shipped**

TEAx's stock CandidateBridge could only build a one-channel mapping, but a real package (the IFE fusion study) declares three typed entry channels from a single EntryPoint module. The gap had been patched by a hand-rolled fusion-side wrapper, MultiChannelEvaluator, that loaded non-swept channels out-of-band from committed JSON templates; codegen's Item 8 regeneration had already collapsed the entry decomposition from four groups to three, leaving the wrapper's hardcoded four-group shape broken with an AttributeError. This item rebuilt the stock bridge to construct a complete typed baseline-plus-override mapping for zero, one, or many channels directly from the embedded catalog's parameter/param_group data, moved bridge construction inside the runner's failure-classification try/except so a malformed candidate fails as a classified ENTRY_VALIDATION rather than an uncaught pydantic.ValidationError, fixed a related codegen zero-entry-channel template gap at its root (a two-file, byte-identity-preserving change), and deleted both fusion consumer wrappers (MultiChannelEvaluator and its bench_prepare_once.py sibling) with no shim. The real IFE viability study then ran green end to end through only public TEAx APIs (2301/2301 cases). The audit certified the item, confirming all three design-review majors held and finding only minor discrepancies: a stale commit hash in the evidence record, slightly favorable suite-count deltas, a weaker-than-ideal assertion in the zero-channel test, and one harmless leftover docstring mentioning the deleted wrapper.

**Key decisions**
  - The one-EntryPoint-module gate stays; 'multi-entry' means multiple typed channels from one module, not multiple entry modules — the evaluate seam itself (Mapping[str, BaseModel]) was already channel-agnostic and did not need to change
  - The channel partition and per-field baseline defaults are read from the embedded catalog's parameters[*].param_group/default_value (the Item 8 seam), replacing the wrapper's out-of-band read of committed JSON template files
  - 'Zero entry channels' and 'constraint-free report' are kept as separate axes (Item 11's firewall); the zero-channel fixture used here is deliberately constraint-bearing, not constraint-free
  - Bridge construction (bridge.build) is relocated inside the runner's try/except EvaluationFailed switch so malformed candidates classify as a StudyBridgeDefect instead of escaping uncaught
  - The fusion wrappers (MultiChannelEvaluator, its bench_prepare_once.py consumer, and the config's two scalar entry-channel keys) are deleted outright once the stock bridge proves green, not kept behind a compatibility shim, per the owner's no-LOC-metrics/qualitative-simplicity stance

**Supersedes / retires**
  - Fusion-tea's MultiChannelEvaluator/ThreeChannelEvaluator wrapper and its bench_prepare_once.py usage
  - TEAx StudyConfig/StudyDefinition's single scalar entry_channel/entry_model fields

#### H-102 · 2026-07-20 — Item 7 Close two trust holes in sealed-package verification and re-seal provenance
`20260720_constraint-lifecycle-package-trust`  ·  subject: **package seal/verify trust chain**  ·  status: **shipped**

A generated package's seal could be defeated two ways: the TEAx loader trusted a verifier shipped inside the package itself with no authentication before executing it, and re-sealing hashed any foreign file on disk into artifact_hashes as if codegen produced it. The fix added a TEAx-side authenticated-verifier gate (hash-check then exec the exact hashed bytes, closing a TOCTOU seam) and a codegen-side generation manifest that classifies every file as codegen-produced, preserved-handwritten, or runtime, with re-seal hard-failing on any file it cannot classify. A single-image version-compatibility set replaced a duplicated bare version literal, failing closed in both skew directions. Both attacks were reproduced RED against pre-fix code and GREEN after; the item spans sysml-codegen and TEAx.

**Key decisions**
  - Trust relocated to the consumer: TEAx authenticates package-local verify.py bytes by hash before executing them, rather than trusting the package's self-certification (preserves the no-sysml-codegen-import constraint on TEAx).
  - Producer-side re-seal provenance is explicitly defense-in-depth, not proof against a same-privilege adversary; seal signing stays out of scope.
  - Verifier/runtime-contract version story uses a single accepted-versions set on the loader rather than cross-repo import, since TEAx cannot depend on sysml-codegen being installed.
  - Seal walker and verify walker remain intentionally separate implementations (not merged), preserving an existing do-not-collapse boundary.

**Supersedes / retires**
  - The bare duplicated RUNTIME_CONTRACT_VERSION literal and its symmetric-equality version check.
  - Unauthenticated exec_module-based loading of the package-local verifier.

#### H-103 · 2026-07-20 — Item 5 Make the whole generated output tree checkout-root portable by collapsing three path-normalization schemes into one certified referent
`20260720_constraint-lifecycle-portability`  ·  subject: **snapshot path portability**  ·  status: **shipped**

Generating the same model from two different checkout roots produced non-byte-identical output because generated docstrings embedded the machine-absolute source path; measurement on catf_mfe_model showed 40 of 81 generated files differed between roots. The root cause was that the snapshot stored source_file paths portably (relative to the snapshot directory) but the loader re-absolutized them on load, destroying portability before docstring renderers used them. The fix generalized the already-certified root-N/<relpath> referent (previously used only for constraint-exclusion catalog entries) to every source_file field, bumped the snapshot format to v5 with a load-time shape gate that rejects absolute or field-less paths loudly, deleted the loader's re-absolutization and two other ad hoc normalization branches (a contingent snapshot-dir-relative scheme and a fragile 'models/' substring strip), and re-captured all 36 committed snapshots. An independent audit reproduced the two-root proof on two fixtures never used in development (solar_battery, fusion_tea) with zero diffs and zero absolute-path leaks, confirmed Item 1's deferred relocated-anonymous-constraint leg now passes licensed, and certified with three non-blocking notes on test coverage and comment precision.

**Key decisions**
  - Chose the heavier v5 format-bump-and-recapture design (D1) over a lighter alternative that would avoid the bump but inherit contingent portability from the deleted Branch B scheme
  - Deleted all three prior path-normalization schemes rather than adding a fourth; the certified root-N/ referent is now the single authority
  - Freshness checking becomes live-capture-only and skips on snapshot loads rather than reintroducing an absolute path to serve it
  - D3 (folding the param-group basename docstring onto the same referent) was deferred as a disambiguation nicety, not a portability fix, since the two-root scan found zero leaks there

**Supersedes / retires**
  - loader.py's _reabsolutize_source_files / _reabsolutize_source_file
  - the snapshot-dir-relative Branch B forward-relativization for source_file fields
  - the 'models/' substring-strip Branch C in stencils.py and test_gen.py
  - capture_pipeline_baselines.py's post-processing .replace() hack
  - snapshot format v4 (bumped to v5)

#### H-104 · 2026-07-20 — Item 10 Prove producer completeness independent of V11 and retire the private stellarator generation bridge in favor of a general resolver fix
`20260720_constraint-lifecycle-producer-completeness`  ·  subject: **producer resolution completeness**  ·  status: **shipped**

Two gaps stood between the constraint-execution machinery and its end-to-end claim: V11 passing didn't prove every consumed value found its intended producer (an ambiguous or defaulted binding could satisfy V11 while feeding the wrong value), and the stellarator demo could only generate through a private bridge plus a two-pass harness that the ratified boundary forbids. This item added a capture sink centralized inside resolve_producer covering all five call sites, a producer-completeness check reading that sink, and a three-part resolver fix (per-child :>> redefinition capture, dual-scope row-13 follow, transitive fixpoint) that lets cross-part aggregation resolve as a real graph producer, letting the bridge, glue, and two-pass harness be deleted. Audit certified with independently reproduced anchors (six bit-exact, oracle reldev 0.00e+00) and a 2956-test green corpus, but surfaced one unresolved gap: the completeness check only guards the design-attribute tier and is blind to a qualifier-dropping collapse through the channel-tier leaf-name rows (rows 14-15), which no current fixture trips but is not structurally guaranteed against.

**Key decisions**
  - Producer-resolution capture is centralized inside resolve_producer itself rather than threaded through each of the five call sites, closing the bypass risk by construction
  - Cross-part aggregation is now a real ModuleKind.AGGREGATION graph producer, not a Python-side rollup, retiring bridge_v11_generate.py and the run_stellaris.py two-pass glue
  - The reverted global _leaf_unique refusal was left reverted and documented in place, since the row-13 resolver fix resolves the cross-part case first and makes the refusal unneeded for the stellarator

**Supersedes / retires**
  - bridge_v11_generate.py (the private LOCAL BRIDGE for stellarator generation), deleted
  - run_stellaris.py's glue-2 two-pass harness and handshake_1costingfe.py rollup glue, deleted
  - WI-027's D7 bridge/placeholder disposition, superseded by this item's D-2 resolution and amended in WI-027's design.md

### SOURCE-IDENTITY  
*1 item(s), 2026-08-03 → 2026-08-10*


#### H-107 · 2026-08-10 — Item 4 Shadow-layer identity manifest running beside the legacy string resolver, stopped after Phases 1-2 and archived as superseded
`20260810_source-identity-occurrence-foundation`  ·  subject: **occurrence identity manifest**  ·  status: **superseded**

Item 4 attempted a production identity manifest that ran alongside the existing legacy string resolver while the resolver kept ignoring it by design. The implementation stopped after Phases 1-2: the audit verdict was Needs Work and the product-lens review was blocked on finding C24. A recovery assessment concluded the architecture itself was flawed (artifact-to-artifact gates could pass while no observable runtime behavior changed), leading the owner to ratify a different approach on 2026-08-07: elaborate-first replacement of the string-resolution stack rather than a parallel shadow layer. No code shipped from this item; the epic and this item were archived with superseded markers on 2026-08-10.

**Key decisions**
  - Owner ratified the elaborate-first replacement (2026-08-07) over continuing the shadow-layer approach, because gates could pass without changing runtime behavior
  - Item 4's stopped Phase 1-2 implementation was preserved only forensically on branch item4-phases12-forensic, not merged
  - Salvageable evidence types/queries/fixtures from the stopped work were carried forward into the ELABORATE-FIRST epic's Item 2 rather than discarded outright

**Supersedes / retires**
  - Item 4's own shadow-layer identity-manifest design (superseded by the ELABORATE-FIRST epic's elaborate-then-project architecture)

### ELABORATE-FIRST  
*7 item(s), 2026-08-08 → 2026-08-19*


#### H-108 · 2026-08-09 — Item 5 Exact-identity elaboration front end built and certified, replacing rendered-name resolution
`20260809_elaborator-breadth`  ·  subject: **elaboration front end**  ·  status: **shipped**

Built the complete exact-identity elaboration front end: SysIDE declaration UUIDs wrapped into typed declaration/slot/occurrence/node identities, a finite occurrence walker, one contextual resolver, and fail-closed diagnostics feeding a typed instance graph that projects onto the existing ComputationGraph and round-trips through canonical instance-graph/v1 JSON. All 29 inherited contract cells passed and a 37-fixture dual-run ledger matched a live corpus run with zero unresolved cases, while the legacy string-resolution route stayed shipped and byte-frozen alongside it. Went through five audit rounds (phases-1/2 partial certify, rendered-path Needs Work, v1/v2 Needs Work, v3 certified) that successively removed rendered-path edge selection, fail-open qualifier fallback, source-text-as-evidence, and a v3 finding of silent admission of an invalid same-name inherited/owned part re-declaration. Ended fully certified.

**Key decisions**
  - Loader diagnostics are now a required elaborate() input so SysIDE's own SYSML_NAMESPACE_NOT_DISTINGUISHABLE validation blocks invalid same-name re-declarations before occurrence expansion, instead of reimplementing spec checks
  - The deep-cross-scope witness fixture was repaired to valid explicit :>> form rather than accommodating the invalid model shape
  - Audit-F30 (guard scope) and audit-F31 (plural-fallback fixture) left open as non-blocking; F19 customer-scale proof and F26 legacy-oracle replacement deferred as Item-6 obligations

**Supersedes / retires**
  - The 2026-08-07 rendered-path implementation of the elaborator, replaced by this exact-ID rewrite

#### H-109 · 2026-08-10 — Item 6 Closed remaining exact-identity gaps in the elaborate-then-project route ahead of the Item 7 authority switch
`20260810_elaborator-identity-completion`  ·  subject: **exact-identity elaboration/projection**  ·  status: **shipped**

This item made calculation definitions, formals, outputs, compilation results, port metadata, and constraint profile decisions attach by exact SysIDE declaration UUID instead of by rendered name, so display renames, normalized-name collisions, duplicate qualified names, and enumeration reorders can no longer move executable payload silently. Missing, duplicate, or mismatched identity now fails loud with named SI_* diagnostics rather than silently defaulting to UNKNOWN/float/null metadata/ADMIT. It introduced structured occurrence records, a typed ExpressionIR, declaration-bound formal provenance, and a fingerprinted internal instance-graph/v2, and made projection strictly one-way from that graph. Nine audit findings across three rounds (audit.md, audit_v2.md, audit_v3.md) were remediated and independently verified, with full certification reached on the v3 re-audit of findings F7 through F9. The shipped legacy route, snapshot v5 bytes, and generated baselines stayed frozen throughout the item.

**Key decisions**
  - Payload and constraint attachment moved to exact SysIDE declaration UUID keys, closing rename/collision/reorder identity gaps
  - SysIDE's native Usage.usages view became the sole effective-child-declaration authority instead of a codegen-side name-matching pass
  - Constraint profile BLOCK now halts generation with a new SI_CONSTRAINT_BLOCKED diagnostic (D10) instead of silently emitting an executable module
  - The public constraint source key is rendered from model metadata rather than a parser-internal UUID (audit finding F1)
  - The boundary guard (F30/F9) is deny-by-default across all six boundary files with five named, mechanically exercised exemptions

**Supersedes / retires**
  - Four Item-6 transitional dual mechanisms are named in Item 7's deletion ledger as slated for removal at cutover

#### H-110 · 2026-08-14 — Item 7 Atomic cutover of the codegen front end to the exact instance-graph route, recovered after the first attempt was refused at owner disposition
`20260814_cutover-recovery`  ·  subject: **generation authority / legacy retirement**  ·  status: **shipped**

Item 7 switches sysml-codegen's public generation authority (run_codegen) to the exact elaborate-then-project route on both the live and v6-snapshot sources, and deletes the legacy string-resolution stack (pipeline builder, backtracker, producer resolution, v5 snapshot route) rather than wrapping it. The first cutover execution was refused by the owner because it landed as an uncommitted candidate with 222 unexplained deletions. This folder documents the recovery: rebuilding from the certified Item-6 baseline with a per-row deletion ledger (ledger-4a) and forensic preservation, running the owner's REVISE path (narrow corrections to compiler convergence, replacement/matrix coverage, ruff baseline, portable provenance, retirement execution, doc integrity), and re-auditing. The initial top-level audit.md recorded 'Needs Work'; after the REVISE steps the final independent audit (evidence/audit-9-final.md) returned CERTIFY-WITH-RESIDUALS with zero blocking findings, and the candidate passed three consecutive identical gate batteries (51/51 fields) before owner acceptance and close.

**Key decisions**
  - An atomic cutover is accepted or refused as a whole candidate, not as a diff — motivated the recovery's certified-baseline-plus-ledger shape rather than resuming the original uncommitted tree
  - Legacy string-resolution code is deleted outright, not kept behind a flag or wrapper, once the exact route covers its behavior
  - Every deletion must be accounted for in a per-row ledger (ledger-4a) with machine-checked replacement proof before it is executed
  - Repeated gate batteries (three consecutive identical runs) are required evidence before owner acceptance; a partial or single run is discarded
  - Spec requirement R12 amended to a zero-new-ruff-baseline rule (owner disposition, narrow-correction step 6)
  - Invariant 35 amended to semantic equality plus generated-byte equality after defined normalization, to make provenance portable (narrow-correction step 5)

**Supersedes / retires**
  - The legacy string-resolution stack: pipeline_builder.py, snapshot_context.py, the analysis/ backtracker, parameter groups and constraint lowering, resolution/graph_builder.py, producer_resolution.py, producer_completeness.py, core/output_registry.py, the v5 snapshot loader/serializer/graph_rebuild, elaboration/diff.py, both v5 capture scripts, and every committed extraction_snapshot.json fixture
  - The first (refused) cutover execution attempt, which left an uncommitted candidate with 222 unexplained deletions

#### H-111 · 2026-08-14 — Item 7 Atomic cutover from the legacy string-resolution front end to the exact instance-graph elaborator as the sole generation authority
`20260814_elaborator-cutover`  ·  subject: **elaborator authority, v6 snapshot**  ·  status: **shipped**

Codegen ran on two parallel authorities: the certified exact-ID instance-graph elaborator from Item 6, and the legacy string-resolution stack (pipeline builder, backtracker, producer resolution, v5 snapshot route) that the product still shipped. This item deleted the legacy stack outright, made the elaborate-then-project route the only path for both live (--models) and snapshot (--from-snapshot v6) generation, and migrated the public API, deletion ledger, and Fusion Tea fixture accordingly. A first cutover attempt was refused by the owner for landing as an uncommitted candidate with 222 unexplained deletions; the work was redone as a forensically tracked recovery from the certified Item-6 baseline with a per-row deletion ledger and machine-checked replacement proof. The redone candidate passed three consecutive identical gate batteries, an independent audit (CERTIFY-WITH-RESIDUALS, zero blocking findings), and owner acceptance.

**Key decisions**
  - An atomic cutover must be accepted or refused as a whole committed candidate, not judged as an incremental diff — the first attempt's refusal established this.
  - v5 snapshots receive no migration or compatibility adapter; only v6 (instance-graph) snapshots are accepted going forward.
  - Every deleted legacy behavioral test responsibility requires an independent one-to-one replacement test, tracked in a closed deletion ledger (ledger-4a).
  - TEAx stays evidence-only for this item; no TEAx production or test changes are in scope unless the spec is explicitly amended.
  - Self-binding remains a modeling error, never reinterpreted as an outer reference (owner ruling carried through from the epic).

**Supersedes / retires**
  - The legacy string-resolution stack: pipeline builder, snapshot context, dependency backtracker, producer resolution/completeness, output registry, v5 snapshot loader/serializer/graph-rebuild, elaboration diff, and their v5 capture scripts and wrong-oracle tests.
  - The parallel v5 extraction-snapshot capture/load route, replaced entirely by the v6 instance-graph envelope.
  - The dual-run diff/runner and parallel exact entry point used during the Item 6/7 transition.

#### H-122 · 2026-08-16 — Item 8 (bounded child) Anchor one-segment references to the exact owner's occurrence before falling back to the shared feature slot
`20260816_qualified-reference-occurrence-anchoring`  ·  subject: **reference resolution, occurrence anchoring**  ·  status: **shipped**

When a one-segment reference's exact leaf is owned by a PartUsage, the elaborator was reducing it to a shared redefinition slot and searching from the consumer's position, which could silently select the wrong occurrence (a consumer under comp_b naming comp_a::length could read comp_b.length) or wrongly refuse or report a named occurrence missing. The fix makes the resolver select the exact owner's occurrence first, before falling back to the shared slot, and refuse by name in unsupported or unclassifiable exact-owner states rather than falling back to consumer position. It kept coverage across calculation, alias, computed, constraint, aggregation, public-mutation, strict/lenient, codec, and snapshot routes, with before/after evidence of 20 adjudicated outcomes and 139 unchanged identity blocks. It closed as a bounded child item of ELABORATE-FIRST Item 8, independently audited, with a residual unmeasured population (15 of 154 roots) and a follow-up left for arrayed diagnostics.

**Key decisions**
  - Exact-owner resolution added at the shared one-segment resolver seam with no widening of occurrence, slot, graph, projection, codec, or schema surfaces
  - Unsupported or unclassifiable exact-owner states refuse by name instead of falling back to consumer position
  - Bounded census methodology adopted: count at the resolver boundary so a root that later refuses still reports the leaves it saw, with every root marked complete/partial/unmeasured rather than claiming whole-corpus coverage
  - Dangling-symlink behavior in the migration/fixture helper accepted as a testing/developer-tooling risk without another remediation cycle [OWNER 2026-08-16]

**Supersedes / retires**
  - The prior one-segment resolution path that reduced an exact owned feature to its shared redefinition slot before searching from consumer position

#### H-123 · 2026-08-16 — Item 8 (bounded child) Self-named calculation bindings are refused before generation instead of silently reading their own inputs
`20260816_self-binding-replacement`  ·  subject: **self-binding detection, exact route**  ·  status: **shipped**

The exact route previously let a calculation binding name itself as its own source, silently reading its own input instead of failing. This item adds exact-route SI_SELF_BINDING detection with named cycle failures, replacing positional descendant search with owner-directed refusal of definition-owned qualified lineage misses. It publishes one authoritative agentic-mbse guidance surface with a validator and packaged-wheel drift checks, migrates both Fusion Tea model trees mechanically (D-5) without changing model physics, and proves via public off-default mutations that intended source values reach every and only their bound consumers. Independent verification passed all ten functional success criteria; the owner accepted a dangling-symlink edge case in the migration/fixture helper as a testing/developer-tooling risk rather than requiring another remediation cycle.

**Key decisions**
  - [OWNER 2026-08-16] Dangling-symlink behavior in the migration/fixture helper is accepted as a testing/developer-tooling edge case; closure proceeded without another remediation or audit cycle.
  - Self-binding detection replaces positional descendant search with owner-directed refusal of definition-owned qualified lineage misses (SI_SELF_BINDING named cycle failures).

**Supersedes / retires**
  - Prior behavior where self-named calculation bindings silently read their own inputs instead of being refused.

#### H-124 · 2026-08-19 —  Replace proximity-based occurrence guessing and silent evidence-dropping in extraction/elaboration with exact SysIDE-derived derivation or named refusal
`20260819_stop-reinventing-the-parser`  ·  subject: **occurrence resolution, evidence extraction**  ·  status: **shipped**

The pipeline had two integrity gaps: occurrence resolution sometimes picked a target by nearest ancestor, descendant search, sole candidate, or first match instead of deriving it from SysIDE's exact declaration evidence and the modeled consumer domain (Lane A), and extraction could silently drop or misclassify SysIDE evidence via broad exception handling, class-name substring tests, or staged name fallbacks before it reached the graph (Lane B). The item required every one of ten Lane-A/B sites to either produce the modeled result or a named refusal, proved against real SysIDE models, with no result depending on proximity or arrival order. Implementation ran through five phases plus a failed candidate plan, three design-review revisions, and three audit passes; the rev-3 audit still returned Needs Work over provenance-fabrication findings (a catch-all error code with a fabricated file/line, and misattributed parser diagnostics). The owner closed the item anyway on 2026-08-19 after two further model-caused provenance fixes and one rebuilt dependent chain, explicitly without a fourth audit loop, and filed the remaining diagnostic-totality gap forward to a separate DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION item. It unblocks the downstream elaborator-downstream / epic Item 8 work that was gated on this item's closure.

**Key decisions**
  - [OWNER] Item closes 2026-08-19 after the two model-caused provenance fixes and one rebuilt chain, without running a fourth audit loop; the rev-3 'Needs Work' audit verdict is preserved as historical record rather than superseded.
  - Owner class (usage-owned vs definition-owned referent) is one required input to occurrence derivation, not the whole answer; both cases still refuse when modeled context cannot derive the occurrence.
  - Indexed-element expression support (cells#(2).mass) is explicitly out of scope; the item only makes the current inability to honor it an honest named refusal instead of a silent wrong answer.
  - Remaining diagnostic-totality/provenance-fabrication gap (rev-3 audit findings) is transferred to a separately owned follow-up item (DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION) rather than blocking this closure.
  - elaborator-downstream design/implementation must not start until this item is implemented, audited, and closed.

**Supersedes / retires**
  - Proximity/arrival-order-based occurrence selection rules (nearest ancestor, descendant search, sole-candidate election, first match) in _select_occurrences, _select_calc_nodes, and _resolve_leaf
  - Class-name-substring and qualified-name-prefix based type/origin decisions in syside_adapter.is_instance, expression.py's operator and standard-library checks, and extractor.py's type mapping
  - extraction/computed_attribute_extractor.py, deleted as a dead classifier (no producer or consumer under src/)
  - Warn-and-continue / silent evidence-dropping behavior on unmapped exit-point types in generation/registry.py

### CONSTRAINT-SEMANTICS  
*10 item(s), 2026-08-12 → 2026-08-14*


#### H-112 · 2026-08-13 — Item 2 Constraint usage domain made total: every authored constraint usage now gets exactly one recorded disposition before occurrence expansion
`20260813_constraint-catalog-totality`  ·  subject: **constraint catalog domain**  ·  status: **shipped**

The lifecycle contract promised every authored constraint usage stays visible with exactly one disposition, but the exact route only began recording constraints after owner-to-scope expansion; on the richest corpus model, 65 authored usages produced only 9 carriers and the other 56 were simply absent from any record. A totality gate built on that data would have been circular, and existing requirement rows read PASS only because specimen fixtures happened to have a carrier. This item mints one ConstraintUsageRecord per authored usage before occurrence expansion, each with exactly one disposition (eligible / excluded-with-reason / non-reaching-with-reason), severity by cause, and a generation-time completeness gate that fails on any removed, duplicated, or misjoined disposition. The domain travels through a bumped instance-graph/v3 codec that fails closed on v2 and stripped-tier shapes, verified across live, in-place-snapshot, and relocated-snapshot routes. The item deleted collect_constraint_manifest, its two classifiers, extraction/constraint_report.py, and all seven test call sites rather than keeping a second inventory in sync, and replaced them with a licence-free source-scanning totality oracle sharing no code with the elaborator. Audited Needs-work, cured, then re-audited Certify-with-residuals.

**Key decisions**
  - Constraint usage records are minted per authored usage before occurrence expansion, not after owner-to-scope expansion, to make the domain total.
  - Severity is assigned by cause, not convenience.
  - The totality oracle is an independent licence-free source scanner sharing no code, adapter, or parse path with the elaborator, to avoid circularity.
  - instance-graph/v2 codec bumped to v3, failing closed on v2 or stripped-tier input; all 21 snapshot-bearing fixtures recaptured once at the final schema.
  - collect_constraint_manifest, its classifiers, extraction/constraint_report.py, and their tests were deleted outright rather than kept as a second, sync-maintained inventory.
  - No new .project/adr/ or .project/product/ ledger entry was hand-minted for the coverage-truth promise; the gap from Item 2's earlier close remains, since manufacturing an entry without an owner-originated statement would itself be a provenance failure. Decisions live in design.md D1-D9 and ADR-009.

**Supersedes / retires**
  - collect_constraint_manifest, its two classifiers, and extraction/constraint_report.py, all removed from src/ and tests/.
  - instance-graph/v2 codec, replaced by instance-graph/v3.
  - The prior (circular) totality-checking approach for REQ-EXT-09 and REQ-CL-04, which are re-graded and re-anchored to the new oracle.

#### H-113 · 2026-08-13 — Item 3 Coverage report and TEAx policy so a generated package can no longer claim full satisfaction when most authored feasibility checks were never assessed
`20260813_constraint-coverage-policy`  ·  subject: **constraint coverage reporting**  ·  status: **shipped**

A generated package could report all_satisfied while most authored feasibility checks went unassessed, and TEAx could label that the same as a genuinely constraint-free model, so a design search could not tell 'passed' from 'nobody checked.' The item added a coverage account (authored total, assessed/excluded/non-reaching counts, unassessed-reason histogram, coverage state) computed one-directionally from Item 2's sealed catalog, added a partial_coverage headline token, made full_satisfaction impossible unless everything eligible was assessed, and made a constraint-bearing model with nothing eligible emit a zero-input aggregator instead of silence. On TEAx, vocabularies were split, unknown tokens fail closed by name, and all five committed fixture packages were regenerated. It closed via orchestrated run, audited Certify-with-residuals with all six residuals cured; the TEAx branch landed but remains unmerged, with codegen-first publication order required.

**Key decisions**
  - Coverage is a second axis on the report, not a slot in the single precedence-ordered headline token
  - full_satisfaction now requires unassessed_gate_count == 0 and assessed_gate_count > 0
  - excluded_only maps to partial_coverage, not not_assessed, per an owner-ratified amendment (an excluded asserted gate stays in the denominator)
  - ships_constraint_report became the single consumer authority; the spec-derived default was deleted rather than kept in sync
  - Publication order is codegen first, then TEAx, since TEAx would otherwise accept a runtime contract no generator produces

**Supersedes / retires**
  - The old headline logic (violation -> indeterminate -> all_satisfied on any non-empty result list -> not_assessed) that never consulted exclusions
  - has_executable_content, deleted
  - Silent no-report generation for excluded-only models (now emits a zero-input aggregator)

#### H-114 · 2026-08-13 — Item 1 Constraint-semantics contract and authoring policy documentation amendments
`20260813_constraint-semantics-contract-amendments`  ·  subject: **constraint documentation, ADR-009**  ·  status: **shipped**

The constraint-semantics contract had been settled but nothing a modeler or implementing agent read reflected it: the lifecycle contract, its requirements companion, and seven documentation statements across both repositories still taught the old headline and disposition behavior, no ADR recorded the coverage-vocabulary change, and the blessed authoring pattern was unpublished. This item is the documentation half of the owner's required sequence (settle semantics, fix docs, then test) so later items build against agreeing text. It published ADR-009, amended multiple invariants and lifecycle-contract entries across both repositories, defined the applicable-asserted-gate test and the four-class equality-intent taxonomy, and corrected D1-D7. No executable code changed beyond one docstring and two citation comments. Audited Certify-with-residuals after curing H-1/M-1/M-2, with M-3 ratified as-is at close.

**Key decisions**
  - M-3 ratified at close: 52 companion sweep hits in docs/sysmlv2 and docs/syside stay aggregated by term/corpus as vendored upstream reference material, not expanded to 52 rows.
  - D5-a: kept 'require constraint' inside the requirement-def example against the design's instruction to swap the form, judged sounder because it preserves the visible requirement-side SysML v2 idiom; a settled-semantics sentence was added instead.
  - Invariant 61 and LC-E13 were minted by the implementer and stamped ratified-by-owner on the day, though the owner saw only the umbrella Q3 warning tier they derive from; a challenger should re-derive against Q3's reasoning.
  - Both deliberate hand-offs from prior items (Item 3's token migration, Item 2's REQ-EXT-09 totality proof) are discharged and recorded closed here.
  - Residuals homed under 'Item 1's authoring guidance' by other closes are re-homed to epic Item 7, not reabsorbed.

**Supersedes / retires**
  - The old constraint-execution-lifecycle-contract headline and disposition behavior text.
  - Seven prior documentation statements teaching that a bare 'constraint' or 'require constraint' is an enforced gate.
  - A retired test previously cited as living totality evidence.

#### H-115 · 2026-08-14 —  Umbrella spec settling constraint semantics and design-search feasibility across sysml-codegen, agentic-mbse, and teax
`20260814_constraint-semantics-contract`  ·  subject: **constraint semantics contract**  ·  status: **shipped**

Against the richest model (catf_mfe_d5, 65 authored constraint usages), the product executed zero of them: 51 calc-def-owned constraints were structurally unreachable, 56 of 65 had no catalog record at all, docs contradicted both code and the SysML standard, and the report could claim full coverage while most gates went unassessed. This umbrella spec captures eight owner-ratified rulings from a 2026-08-12 Q&A session (assert-only gating, staged calc-def-owned execution, severity-by-cause errors, bindings-only predicates for now, two-tier coverage accounting, boundary-plus-opt-in study policy, non-executable requirement forms, and a new CATF derivative fixture for migration) as the behavioral authority for a 9-item epic. Spec review found the review-critical L1-L3 issues (vocabulary mismatch between generated tokens and TEAx runtime tokens, unresolved coverage-population ambiguity, oversized single-item scope) and the product-lens pass raised 8 findings (F1-F8), all disposed without contradicting any owner/HARD statement. The epic that grew from this spec closed 2026-08-14 with all 9 items shipped, but pre_pr was deliberately not run and nothing was pushed to main in any of the three repos.

**Key decisions**
  - Only assert constraints (not plain constraints) are enforced gates (Q1)
  - Calc-def-owned constraints get ruled semantics now but staged delivery as their own item; interim state treats asserted-unattachable as a loud error (Q2)
  - Error severity is graded by cause: asserted+structurally-unattachable errors, asserted+vacuous warns, plain/out-of-scope forms never error (Q3)
  - Gate predicates stay bindings-only for now; in-predicate feature chains are filed as a future capability; equalities become two-inequality tolerance bands (Q4)
  - Coverage headline uses two-tier accounting: usages for coverage, occurrences for results, with vacuous kept as a separate bucket (Q5)
  - Study-policy default keeps partial coverage at the boundary with explicit auditable per-study opt-in to feed-strategy (Q6)
  - Requirements-side forms (require/assume/satisfy) stay non-executable and visible; requirement evaluation is a declared out-of-scope capability (Q7)
  - CATF constraint migration happens via a new derivative fixture forked from catf_mfe_d5, with twins frozen and a per-constraint disposition table (Q8)
  - ADR-009 filed to record the all_satisfied headline vocabulary change as an intentional product-contract change

**Supersedes / retires**
  - The prior modeling-assumptions.md claim that a bare constraint gives an enforced gate
  - The prior ConstraintReport aggregator behavior where partial assessment could read as all_satisfied

#### H-116 · 2026-08-13 — Item 6 Designed (but did not build) the capability to attach a calc-definition-owned constraint to concrete calculation occurrences
`20260813_calcdef-constraint-gate-design`  ·  subject: **calc-def constraint gate**  ·  status: **shipped**

A constraint asserted by a calculation definition could never attach to any concrete calculation occurrence; it always ended as non_reaching/owner_kind_unattachable/error even when the graph held concrete calculations of its owning definition, leaving the owner-ratified one-check-per-occurrence rule visible in the contract but permanently unexecutable. This item designed the fix rather than implementing it: a throwaway probe attached such a constraint across zero, one, and two occurrences by matching the constraint owner's DeclarationId to CalcNode.calculation_definition_id, recovering resolved attributes, literals, and modeled defaults with no rendered-name lookup. The probe surfaced that two sibling uses of one definition collide on the current constraint key, so concrete constraint identity must carry the calculation node and attachment must precede serialization; that gap was resolved inside the v4 wire grammar. The delivery was a spec, revised design, three-round independent design review (all findings closed), and a filed follow-on implementation item; the design was independently audited and certified, with no production code touched.

**Key decisions**
  - Production implementation is not authorized in this epic (owner ruling at close); the 7-9 day follow-on (graph v4, catalog 4.0.0, codegen + TEAx changes) is filed as unowned backlog entry CALCDEF-GATE-IMPLEMENTATION, competing for the next work slot
  - The production-acceptance checkboxes in spec.md are left deliberately open, belonging to the future implementation rather than to this design-only item
  - Concrete constraint identity for a calc-def-owned constraint must carry the calculation node (not just the definition), because two sibling uses of one calc definition otherwise collide on the constraint key; resolved inside the v4 wire grammar with no second authority or occurrence inventory
  - The Item 8 implementation start gate is satisfied as of Item 8's unit-lane characterizations landing; the only remaining block on starting the follow-on implementation is owner authorization

#### H-117 · 2026-08-13 — Item 5 CATF derivative and end-to-end acceptance of the constraint-semantics contract
`20260813_catf-constraint-policy-acceptance`  ·  subject: **constraint diagnostics, unit annotations**  ·  status: **shipped**

The constraint-semantics contract built across Items 1-4 had only been verified against purpose-built fixtures, not an end-to-end acceptance case. Running it against a real derivative surfaced two defects: a unit annotation's second operand leaking into the reference-collection walk, and a blocked-feature-chain diagnostic that was a tautology with no reference or location. Both were cured under the product's existing rule that a unit annotation contributes its value and never a reference, plus a de-duplicated, ordered chain-block message. The admitted annotation set expanded by exactly the two named shapes; chains still block and equalities still go untoleranced. Audited Needs work for two blocking findings, both cured same day, re-verdict Certify-with-residuals.

**Key decisions**
  - Cured a fourth lane (annotated chain in a binding) in-scope under the orchestrator's pre-recorded same-rule policy.
  - Two further limits (unit on a constraint binding is dimensionally inert; blocked-chain location is the usage's line, not the term's) surfaced and parked for epic Item 5.
  - Coverage ledger's durable home moved to tests/unit/data/ per owner ruling (F5).

#### H-118 · 2026-08-13 — Item 4 Cure two reproduced defects at the unit-annotation boundary of asserted physics-gate predicates
`20260813_constraint-predicate-hardening`  ·  subject: **constraint predicate unit annotations**  ·  status: **shipped**

Two defects sat exactly where a modeler crosses into writing an asserted physics gate: a unit-annotated literal such as 8.55 [m] in an asserted predicate wrongly raised SI_OCCURRENCE_MISSING because the reference walk recursed into the unit annotation's second operand, and the blocked-feature-chain diagnostic gave only a tautological message with no reference or location. Both were cured under the product's existing rule that a unit annotation contributes its value and never a reference: one unwrap at the head of the reference-walk function, one at the binding read for a fourth affected lane found during spec, and a companion message= at both chain-block sites with de-duplication and stable ordering. The admitted set grew only by the two named annotation shapes; chains stay blocked and equalities stay untoleranced. The orchestrated run audited to Certify-with-residuals and all findings were cured the same day, with one item (F5, the coverage ledger's durable home) resolved by owner ruling at close.

**Key decisions**
  - A unit annotation contributes its value and never a reference; applied as one unwrap at the head of _expression_references and at the binding read for the fourth (in tol = 0.05 [m]) lane.
  - Chain-block diagnostics get a message= at both block sites, de-duplicated and ordered on one normalized key, so the error names the exact construct to fix.
  - The coverage ledger's durable home moved to tests/unit/data/ (owner ruling, F5).
  - Two newly surfaced limits (a unit on a constraint binding being dimensionally inert to the profile; a blocked chain's diagnostic location being the usage's line rather than the term's) were parked for epic Item 5 rather than fixed in-scope.

#### H-119 · 2026-08-13 — Item 9 Execute held ruled intent on the catf_mfe_gated fixture: derive A5/A6 radii, upgrade A9 to a relative-band assert, and retire stale blocked-by-defect PROVENANCE records
`20260813_derivative-upgrade-held-intent`  ·  subject: **catf_mfe_gated fixture derivations**  ·  status: **shipped**

Item 8's unit-lane port fix removed the defect that had forced three rows of tests/fixtures/catf_mfe_gated (A5 LayerContinuity, A6 RadiusThicknessConsistency, A9 PumpingSpeedConsistency) to stay as visible plain usages marked blocked-by-defect instead of the shape the owner had already ruled. This item executed that already-ruled intent: deleted A5/A6 and replaced them with 27 derived radius attributes (13 inner_radius, 14 outer_radius) over a free-parameter basis of the axis root radius plus 14 layer thicknesses; upgraded A9 to an asserted ProductWithinBand constraint at 1% relative tolerance; retired the blocked-by-defect markings on the live fixture surface while leaving the archived owner-disposition record byte-frozen; and restated the manifest identity as 65 = 56 carriers + 9 named deletions, extending the manifest prover to anchor derivations per-occurrence instead of by non-unique initializer text. Independent audit certified with residuals: all eight spec success criteria verified by re-measurement, two structural smells found and disposed, and only minor recorded-number/conditional-criterion residuals left open (none blocking).

**Key decisions**
  - No re-disposition: A5/A6 basis, A9 tolerance/form, and the blocked-by-defect retirement were already ruled by the owner on 2026-08-13; this item only executes and restates the arithmetic that follows.
  - The archived owner-disposition.md stays byte-untouched; the blocked-by-defect retirement lands only on the live fixture PROVENANCE, since the epic's criterion is satisfied by the live projection.
  - A9 asserts ProductWithinBand at rel_tol = 0.01 (relative, not absolute) so the band scales under design-search resizing.
  - The manifest prover (scripts/check_gated_manifest.py) is extended to match each derivation per-occurrence (owning declaration block) rather than by initializer text uniqueness, since A6's 14 derivations are byte-identical lines.
  - The epic's third Item 9 success criterion (author five @inapplicable: markers) is ruled a not-fired conditional because [INLINE-PREDICATE-MARKER-DROP] stays open and unowned; recorded as a decision on both the item's records and BACKLOG.md rather than fired here.
  - spec_review was skipped for this item as proportionate, with the orchestrator independently re-verifying the restated-identity arithmetic and design_review still run fresh.

**Supersedes / retires**
  - The blocked-by-defect visible-plain-usage forms of A5, A6, and A9 in tests/fixtures/catf_mfe_gated
  - The prior manifest identity accounting of 65 = 58 carriers + 7 deletions
  - The exact == comparison in the prior PumpingSpeedConsistency constraint
  - Stale citations in the manifest expectation and prover docstring pointing at the pre-archive .project/active/ path

#### H-120 · 2026-08-13 — Item 8 Fix unit-lane port metadata defect blocking constraint-formal and computed-attribute entry-point dedup
`20260813_unit-lane-port-metadata`  ·  subject: **elaborator unit selection, projection dedup**  ·  status: **shipped**

One modeled design attribute feeding more than one consumer only collapses to a single public DESIGN_ATTRIBUTE entry point when the consumers' metadata agrees, but the elaborator made agreement impossible: constraint-formal bindings and computed-attribute inputs both carried unit=None while calc-usage bindings carried a real unit, so valid models hit projection's fail-closed comparison and were refused with SI_RENDERING_COLLISION. This affected CATF's A9 assert-band and 26 of 27 radial-build radius derivations, forcing Item 5 to hold A5/A6/A9 as blocked-by-defect. The fix made declaration identity own unit selection on all three lanes (constraint ports via the selected effective constraint formal, computed ports via the exact referenced declaration, one shared exact-text extractor with no inference/conversion), and made v6 envelope build/load certify projectability before capture can write. Shipped standalone as an implementation/defect-fix item, independently audited Certify; both customer characterizations flipped red-to-green with exact authored units.

**Key decisions**
  - Declaration identity (not slot-root fallback) owns unit selection on all three metadata lanes; projection's equal-metadata-dedupes / unequal-refuses rule is unchanged.
  - Item 8 shipped standalone; the Item 6 design's R5 joint-delivery option stayed declined.
  - v6 envelope build and load now certify projectability before capture can write, so a non-projectable graph cannot reach a destination.
  - The complete tracked-path set (23 paths) and the older 15-path subset are recorded as dated evidence only; a future graph-v4 record must re-derive and prove equality against its own then-current set rather than reuse these numbers.
  - Zero v3 recapture fired (23 tracked / 23 assessed / 0 stale/missing/extra/duplicate), so no snapshot or manifest byte moved during this item.

**Supersedes / retires**
  - Prior elaborator behavior where constraint-formal bindings and computed-design-attribute inputs carried a manufactured unit=None instead of the authored unit.

#### H-121 · 2026-08-14 — Item 7 Sync ADR, product-promise ledger, and agent-facing documentation to the constraint-semantics behavior shipped in Items 1-6, 8, 9
`20260814_constraint-docs-agent-sync`  ·  subject: **docs, ADR, product ledger, agent prompts**  ·  status: **shipped**

Constraint-semantics behavior changed across Items 1-6, 8, and 9, but almost none of the teaching documentation (skills, pattern docs, expert-agent prompts) changed with it, so an authoring session would copy a superseded shape and generate a model with no gate at all. This item closed that gap across three repositories (sysml-codegen, agentic-mbse, TEAx), creating the repo's first product ledger (.project/product/INDEX.md and P-001, carrying the owner's verbatim design-search promise), back-registering ADR-009 into modeling-assumptions.md, updating cross-repo teaching for @inapplicable authoring, disposition vocabulary, the totality gate, coverage/policy defaults, and the sysml-conventions skill and expert-agent definitions. It changed no behavior, only documentation and ledger scaffolding. Independently audited CERTIFY-WITH-RESIDUALS with two residuals, both owner calls (a symlink pointing at a superseded branch, and untagged REQ gates on Items 3/5/8/9).

**Key decisions**
  - D-1: the promise/ADR home is a new .project/product/ ledger plus back-registering ADRs as numbered rows in the existing modeling-assumptions.md convention rather than creating a docs/adr/ tree; the durable citation lives in the epic file and INDEX.md so it survives archiving.
  - P-001 carries the owner's design-search promise byte-for-byte [OWNER-VERBATIM, 2026-08-13], with the promise-vs-basis tension surfaced (not resolved) and [ACAUSAL-RELATIONS-CAPABILITY] named for the unbuilt half.
  - The B1-B5 marker rule: a marker on a bindings-form constraint reaches the domain, but on an inline-predicate constraint SysIDE drops it silently, so PROVENANCE carries the disposition until [INLINE-PREDICATE-MARKER-DROP] closes.
  - Verification-matrix reconciliation done in one pass epic-wide: recount 280/136/3/131/10/0 across 33 families, both count blocks corrected, REQ-DIAG family filed.
  - A-3 auditor finding fixed in place rather than argued: the shipped generator refused the doc's own @inapplicable authoring example; resolved by moving the marked gate onto a part def the variant never instantiates.

**Supersedes / retires**
  - Stale documentation across sysml-codegen, agentic-mbse, and TEAx describing pre-Item-1-6/8/9 constraint-semantics behavior (superseded @inapplicable authoring examples, disposition vocabulary, coverage/policy text).

### REPO-CLEANUP  
*1 item(s), 2026-08-20 → 2026-08-21*


#### H-126 · 2026-08-21 — Item 1 Install script-managed ADR and product-promise registers with an owner-grade routing rule for which register a decision belongs in
`20260821_scaffolding-register-boundary`  ·  subject: **decision register scaffolding**  ·  status: **shipped**

The repo had two places to record a settled decision (a hand-maintained product ledger and an ad hoc ADR set) with no rule for which one a given decision belonged in, and the product ledger was maintained by hand despite the process pack saying a script should own it. This item installed both register engines (adr.sh, product.sh) from agentic-project-init, filed an owner-grade routing criterion keyed on who the decision binds (model authors go to docs/architecture/modeling-assumptions.md, code-generator-builder decisions go to .project/adr/), triaged the nine existing ADRs against that rule, and migrated the four product promises onto script-managed 000N ids with a generated index, keeping every visible word and owner payload unchanged. Six new conformance tests pin discoverability and citation conventions. Certified via audit; the licensed suite ran 2,371 passed / 9 skipped / 94 deselected under an owner-accepted missing-manifest limitation, so the exact full-suite gate remains not-yet-green by design, not a defect.

**Key decisions**
  - Decisions are routed by who they must bind: model-author decisions stay in docs/architecture/modeling-assumptions.md as numbered ADR-0NN sections; code-generator-builder decisions go to .project/adr/ as script-allocated NNNN ids
  - Register ids resolve by sibling filename, and citations must always name the register path plus id, never a bare number
  - Nine pre-existing ADRs were triaged against the new routing rule; ADR-007 and ADR-009 were carried forward to Item 3 rather than resolved here

**Supersedes / retires**
  - The hand-maintained product/README.md ledger process, replaced by product.sh-generated 000N ids and INDEX.md

---

## Supersession Index

Every item that explicitly replaced, retired, or deleted earlier work.


**H-001 · 2026-02-02 — 20260202_codegen-runtime-gap-fixes** (unknown)
  - The unconditional copy of templates/schemas_ref.py (hardcoded FusionParams schema) into every generated package's {package}_schemas.py.

**H-005 · 2026-02-07 — 20260207_expr-pipeline-integration** (EXPR-CODEGEN)
  - The unconditional NotImplementedError stub generation for CalcDefs whose math is fully expressed in SysML
  - The legacy text-only _extract_expression_text() function, replaced by calls into expression_utils.py

**H-020 · 2026-02-12 — 20260212_hierarchy-e2e-fixes** (COST-PATTERN)
  - Portions of the earlier hierarchy-bugfix spec's BF-1, BF-6, and BF-7 fixes, which were valid against mock data but did not work against the real SysIDE AST

**H-027 · 2026-02-15 — 20260215_cutover-validation** (OUTPUT-REGISTRY-BACKTRACKER-REDESIGN)
  - The backtracker's _computed_attr_index, _aggregation_output_index, _output_catalog, and _design_attr_binding_index, plus the _resolve_binding_to_usage 7-strategy cascade and _compare_with_registry parallel-validation scaffolding
  - graph_builder.py's _build_output_catalog, _extend_output_catalog_with_computed_attrs, and _extend_output_catalog_with_aggregation functions
  - The Bug 2 xfail marker on test_bug2_regression.py

**H-037 · 2026-02-17 — 20260217_backtracker-conformance** (unknown)
  - The prior belief that expression_binding_probe crashes inside the backtracker; corrected to document silent EXPRESSION-binding skip instead

**H-038 · 2026-02-17 — 20260217_backtracker-typed-dispatch** (unknown)
  - OutputRegistry.resolve() and OutputRegistry.register() convenience methods and the _compat dict entirely removed
  - derive_key_c() static method removed

**H-044 · 2026-02-17 — 20260217_expression-compiler-conformance** (unknown)
  - The implementation plan's assignment of the aggregation '.()' syntax defect to this component; reassigned to the hierarchy resolver / AST dispatch invariant work

**H-056 · 2026-02-17 — 20260217_typed-registry-refactor** (unknown)
  - REQ-OR-02, REQ-OR-05, REQ-OR-08 in 10-output-registry.md
  - REQ-BT-08 in 11-analysis-backtracker.md
  - REQ-NC-07 in 15-naming-conventions.md
  - REQ-DRA-03 in 24-dual-resolution-architecture.md
  - REQ-RES-07 in 03-resolution-overview.md

**H-061 · 2026-02-18 — 20260218_pipeline-yaml-generator** (unknown)
  - graph_builder.py's unprefixed entry-point param_group fallback for orphan entry points (Bug 9)
  - graph_builder.py's hardcoded python_type="int" for aggregation multiplicity inputs (Bug 10)

**H-064 · 2026-02-19 — 20260219_type-mapping-consolidation** (unknown)
  - 6 independently-defined _map_input_type/_map_output_type/_map_sysml_to_python_type copies across modules.py, entry_point.py, schemas.py (x2), stencils.py, registry.py

**H-065 · 2026-02-20 — 20260220_bug11** (unknown)
  - The prior xfail-marked test acknowledging Bug 11 as known-broken; it now asserts the correct behavior as a hard requirement

**H-067 · 2026-02-20 — 20260220_dead-code-removal** (unknown)
  - Strategy B's normalized SysML-QN fallback in input_resolver.py
  - dependency_backtracker.py's Step 1b QN normalization block
  - the bare-name fallback branch in initialization.py's _rewrite_virtual_bindings
  - templates/teax_module_stub.py.jinja2

**H-068 · 2026-02-20 — 20260220_factory-purity-refactor** (unknown)
  - Mutation of the shared entry_points dict from inside _build_computed_attr_module() and _build_aggregation_module()

**H-069 · 2026-02-20 — 20260220_naming-consolidation** (unknown)
  - analysis/qualified_names.py (re-export shim)
  - resolution/identifier_types.py (re-export shim)
  - re-export blocks in analysis/__init__.py and resolution/__init__.py for naming/identifier symbols

**H-070 · 2026-02-20 — 20260220_orchestration-extraction** (unknown)
  - generation/initialization.py's role as home for build_pipeline_context() and build_output_registry(); those now live in orchestration/pipeline_builder.py and orchestration/output_registry_builder.py

**H-071 · 2026-02-22 — 20260222_docs-consolidation** (unknown)
  - The 8 ADR-001 through ADR-008 files previously in docs/architecture/, replaced by docs/architecture/modeling-assumptions.md and the reference/ doc set
  - .project/concepts/refactor-design-intent/ as the working documentation source, now archived and historical-only

**H-072 · 2026-07-07 — 20260708_classifier-fix** (TRUTH-DEBT)
  - The five xfailed test cases documenting the classifier bug (INHERITED_ATTR_PATTERNS), replaced with positive-assertion passes
  - The prior 'loud rejection' framing in verification-matrix.md and the epic Item-4 text, corrected to 'silent no-op'

**H-073 · 2026-07-08 — 20260708_f4-cutover** (TRUTH-DEBT)
  - _resolve_aggregation_input_channel (graph_builder.py) and its three inline entry-point fallback blocks (SumTerm, SingletonTerm, LocalTerm)
  - Strategy D (DesignAttributeLookup) stub in input_resolver.py
  - The double-bound param_groups variable and its two mypy type: ignore comments in graph_builder.py

**H-074 · 2026-07-08 — 20260708_multihop-chain** (TRUTH-DEBT)
  - The prior epic's loud hard-reject of 3+-segment calc-usage chains at extraction time (usage_extractor.py), which is replaced by resolution via the backtracker's ancestor climb; the loud diagnostic itself is preserved but relocated

**H-078 · 2026-07-10 — 20260720_aggregation-decomposition** (PUSH-DOWN)
  - The prior hierarchy_resolver.py aggregation AST walker that mixed neutral SysML decomposition with Python rendering in a single sysml-codegen-local implementation

**H-084 · 2026-07-13 — 20260713_module-kind-refactor** (CONSTRAINT-EXEC)
  - The is_computed_attribute and is_aggregation boolean flags on PipelineModule, removed repo-wide (src and tests) and replaced by the module_kind enum

**H-086 · 2026-07-13 — 20260713_snapshot-v3** (CONSTRAINT-EXEC)
  - The prior from-snapshot rebuild path's silent lack of a constraint phase, and the lowering feature's default-off posture from Item 5

**H-087 · 2026-07-13 — 20260713_constraint-migration-acceptance** (CONSTRAINT-EXEC)
  - The drop-manifest reporting era (extraction/constraint_report.py, its two blanket 'not executable' warnings, and the snapshot dropped_constraints section), retired in favor of the constraint catalog as the single source of truth
  - The fusion-tea IFE sweep's hand-coded Python viability rule, replaced by the generated assertion consumed via the teax study layer
  - Authoring guidance in docs/architecture/modeling-assumptions.md section 8 that taught constraints are dropped/not executable

**H-088 · 2026-07-13 — 20260713_expression-ast-cutover** (CONSTRAINT-EXEC)
  - ExpressionAST, build_expression_ast, and compile_expression, deleted and grep-gated out of src/

**H-089 · 2026-07-13 — 20260713_package-contracts** (CONSTRAINT-EXEC)
  - S4 spike's test-only ModelContract/seal/verify_seal code (s4_lib.py), which never declared its coverage set explicitly, never detected missing coverage-set files, and never checked environment compatibility.

**H-090 · 2026-07-20 — 20260720_constraint-execution-lifecycle-contract** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - the old equality matrix
  - the old whole-graph extension-time V11 invariant
  - stale profile-version claims
  - the 'profile is codegen-only' description
  - owner-ratified WI-027 D7 passthrough-calculation design (superseded by Owner Decision 2)
  - the alternate TEAx-side catalog schema, fusion catalog materializer, and identity stand-in (superseded by Owner Decision 3)

**H-092 · 2026-07-20 — 20260720_constraint-lifecycle-catalog-store** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - TEAx's alternate constraint_catalog.json schema, its CatalogView/_Catalog reconstruction logic, the hand-authored fixture, and the byte-hash fingerprint stand-in in study/config.py
  - The fusion-tea catalog materializer (materialize_constraint_catalog.py) and its committed generated/contracts/constraint_catalog.json artifact

**H-093 · 2026-07-20 — 20260720_constraint-lifecycle-diagnostics-defaults** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - The leaf-only written_reference carry design (B2/D4 as originally stated), replaced after a measured wrong-anchor regression
  - The premise in tests/fixtures/shared_producer/PROVENANCE.md that the written reference is structurally unreachable from the calculation consumer
  - Item 2's referral note that convergence needed a snapshot format bump
  - Silent omission of an unresolvable modeled default's JSON key (generation/entry_point.py)
  - The bare _literal_float default parser and several duplicate string-based default-parsing lanes

**H-094 · 2026-07-19 — 20260720_constraint-lifecycle-gate-b** (unknown)
  - Old lowering INV-6's requirement that the extended graph have zero V11 uncovered params

**H-095 · 2026-07-20 — 20260720_constraint-lifecycle-occurrence-demand** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - The nullable qualified-name-set membership approach to demand discovery, which allowed anonymous admitted/excluded usages to alias.
  - The part-instance walk's silent empty-subtree treatment of a revisited definition, which could mask recursion.
  - The appended-record model for calculation bindings and constraint actuals, which allowed duplicate overwrite of grouping provenance.

**H-096 · 2026-07-20 — 20260720_constraint-lifecycle-shared-resolution** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - The calculation-ladder resolver (analysis/dependency_backtracker.py), the constraint-ladder resolver (analysis/constraint_lowering.py), and the aggregation-ladder resolver path in resolution/input_resolver.py and graph_builder.py, all deleted in favor of one shared resolver.
  - The stellarator consumer's passthrough-calculation workaround for design-attribute constraint actuals, superseded by direct Gate A resolution.

**H-098 · 2026-07-20 — 20260720_constraint-lifecycle-docs-f1** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - Doc claims of snapshot format 'current: 3' (actual: 5), executable-profile v3 (actual: v4), and agentic-mbse floor >=0.1.1 (actual: >=0.1.2) are all corrected
  - F1 audit's cited commit 927a9e1 replaced with the correct d545701

**H-099 · 2026-07-20 — 20260720_constraint-lifecycle-evidence-durability** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - The two duplicated unconditional constraint_report reads in evaluator.py
  - The incidental encode-before-policy ordering in runner.py that had been the only protection for persisted evidence

**H-100 · 2026-07-20 — 20260720_constraint-lifecycle-legacy-identity** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - capture_snapshot's lower_constraints_enabled parameter and the GRANDFATHERED set plumbing in scripts/capture_extraction_snapshots.py
  - ConcreteConstraint.tracking_key field, its docstring, and its round-trip test
  - the epic contract's cross-version correlation non-goal claims that leaned on tracking_key

**H-101 · 2026-07-20 — 20260720_constraint-lifecycle-multi-entry** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - Fusion-tea's MultiChannelEvaluator/ThreeChannelEvaluator wrapper and its bench_prepare_once.py usage
  - TEAx StudyConfig/StudyDefinition's single scalar entry_channel/entry_model fields

**H-102 · 2026-07-20 — 20260720_constraint-lifecycle-package-trust** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - The bare duplicated RUNTIME_CONTRACT_VERSION literal and its symmetric-equality version check.
  - Unauthenticated exec_module-based loading of the package-local verifier.

**H-103 · 2026-07-20 — 20260720_constraint-lifecycle-portability** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - loader.py's _reabsolutize_source_files / _reabsolutize_source_file
  - the snapshot-dir-relative Branch B forward-relativization for source_file fields
  - the 'models/' substring-strip Branch C in stencils.py and test_gen.py
  - capture_pipeline_baselines.py's post-processing .replace() hack
  - snapshot format v4 (bumped to v5)

**H-104 · 2026-07-20 — 20260720_constraint-lifecycle-producer-completeness** (CONSTRAINT-LIFECYCLE-REMEDIATION)
  - bridge_v11_generate.py (the private LOCAL BRIDGE for stellarator generation), deleted
  - run_stellaris.py's glue-2 two-pass harness and handshake_1costingfe.py rollup glue, deleted
  - WI-027's D7 bridge/placeholder disposition, superseded by this item's D-2 resolution and amended in WI-027's design.md

**H-105 · 2026-07-24 — 20260724_docs-lifecycle-sync** (unknown)
  - 04-input-resolver.md's description of the now-deleted resolution/input_resolver.py module and its dual-resolver-ladder narrative in 24-dual-resolution-architecture.md.

**H-107 · 2026-08-10 — 20260810_source-identity-occurrence-foundation** (SOURCE-IDENTITY)
  - Item 4's own shadow-layer identity-manifest design (superseded by the ELABORATE-FIRST epic's elaborate-then-project architecture)

**H-108 · 2026-08-09 — 20260809_elaborator-breadth** (ELABORATE-FIRST)
  - The 2026-08-07 rendered-path implementation of the elaborator, replaced by this exact-ID rewrite

**H-109 · 2026-08-10 — 20260810_elaborator-identity-completion** (ELABORATE-FIRST)
  - Four Item-6 transitional dual mechanisms are named in Item 7's deletion ledger as slated for removal at cutover

**H-110 · 2026-08-14 — 20260814_cutover-recovery** (ELABORATE-FIRST)
  - The legacy string-resolution stack: pipeline_builder.py, snapshot_context.py, the analysis/ backtracker, parameter groups and constraint lowering, resolution/graph_builder.py, producer_resolution.py, producer_completeness.py, core/output_registry.py, the v5 snapshot loader/serializer/graph_rebuild, elaboration/diff.py, both v5 capture scripts, and every committed extraction_snapshot.json fixture
  - The first (refused) cutover execution attempt, which left an uncommitted candidate with 222 unexplained deletions

**H-111 · 2026-08-14 — 20260814_elaborator-cutover** (ELABORATE-FIRST)
  - The legacy string-resolution stack: pipeline builder, snapshot context, dependency backtracker, producer resolution/completeness, output registry, v5 snapshot loader/serializer/graph-rebuild, elaboration diff, and their v5 capture scripts and wrong-oracle tests.
  - The parallel v5 extraction-snapshot capture/load route, replaced entirely by the v6 instance-graph envelope.
  - The dual-run diff/runner and parallel exact entry point used during the Item 6/7 transition.

**H-112 · 2026-08-13 — 20260813_constraint-catalog-totality** (CONSTRAINT-SEMANTICS)
  - collect_constraint_manifest, its two classifiers, and extraction/constraint_report.py, all removed from src/ and tests/.
  - instance-graph/v2 codec, replaced by instance-graph/v3.
  - The prior (circular) totality-checking approach for REQ-EXT-09 and REQ-CL-04, which are re-graded and re-anchored to the new oracle.

**H-113 · 2026-08-13 — 20260813_constraint-coverage-policy** (CONSTRAINT-SEMANTICS)
  - The old headline logic (violation -> indeterminate -> all_satisfied on any non-empty result list -> not_assessed) that never consulted exclusions
  - has_executable_content, deleted
  - Silent no-report generation for excluded-only models (now emits a zero-input aggregator)

**H-114 · 2026-08-13 — 20260813_constraint-semantics-contract-amendments** (CONSTRAINT-SEMANTICS)
  - The old constraint-execution-lifecycle-contract headline and disposition behavior text.
  - Seven prior documentation statements teaching that a bare 'constraint' or 'require constraint' is an enforced gate.
  - A retired test previously cited as living totality evidence.

**H-115 · 2026-08-14 — 20260814_constraint-semantics-contract** (CONSTRAINT-SEMANTICS)
  - The prior modeling-assumptions.md claim that a bare constraint gives an enforced gate
  - The prior ConstraintReport aggregator behavior where partial assessment could read as all_satisfied

**H-119 · 2026-08-13 — 20260813_derivative-upgrade-held-intent** (CONSTRAINT-SEMANTICS)
  - The blocked-by-defect visible-plain-usage forms of A5, A6, and A9 in tests/fixtures/catf_mfe_gated
  - The prior manifest identity accounting of 65 = 58 carriers + 7 deletions
  - The exact == comparison in the prior PumpingSpeedConsistency constraint
  - Stale citations in the manifest expectation and prover docstring pointing at the pre-archive .project/active/ path

**H-120 · 2026-08-13 — 20260813_unit-lane-port-metadata** (CONSTRAINT-SEMANTICS)
  - Prior elaborator behavior where constraint-formal bindings and computed-design-attribute inputs carried a manufactured unit=None instead of the authored unit.

**H-121 · 2026-08-14 — 20260814_constraint-docs-agent-sync** (CONSTRAINT-SEMANTICS)
  - Stale documentation across sysml-codegen, agentic-mbse, and TEAx describing pre-Item-1-6/8/9 constraint-semantics behavior (superseded @inapplicable authoring examples, disposition vocabulary, coverage/policy text).

**H-122 · 2026-08-16 — 20260816_qualified-reference-occurrence-anchoring** (ELABORATE-FIRST)
  - The prior one-segment resolution path that reduced an exact owned feature to its shared redefinition slot before searching from consumer position

**H-123 · 2026-08-16 — 20260816_self-binding-replacement** (ELABORATE-FIRST)
  - Prior behavior where self-named calculation bindings silently read their own inputs instead of being refused.

**H-124 · 2026-08-19 — 20260819_stop-reinventing-the-parser** (ELABORATE-FIRST)
  - Proximity/arrival-order-based occurrence selection rules (nearest ancestor, descendant search, sole-candidate election, first match) in _select_occurrences, _select_calc_nodes, and _resolve_leaf
  - Class-name-substring and qualified-name-prefix based type/origin decisions in syside_adapter.is_instance, expression.py's operator and standard-library checks, and extractor.py's type mapping
  - extraction/computed_attribute_extractor.py, deleted as a dead classifier (no producer or consumer under src/)
  - Warn-and-continue / silent evidence-dropping behavior on unmapped exit-point types in generation/registry.py

**H-126 · 2026-08-21 — 20260821_scaffolding-register-boundary** (REPO-CLEANUP)
  - The hand-maintained product/README.md ledger process, replaced by product.sh-generated 000N ids and INDEX.md
