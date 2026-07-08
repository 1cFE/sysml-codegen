# Epic: agentic-mbse Push-Down

**Epic ID**: PUSH-DOWN
**Status**: Ready
**Priority**: P1 (High)
**Created**: 2026-07-08
**Estimated Effort**: 6–8 days

---

## Executive Summary

The extraction layer mixes pure SysML model understanding with codegen-specific transformation
in the same files. This epic moves the reusable SysML semantics — expression reconstruction,
qualified-name utilities, hierarchy/redefinition extraction, and aggregation decomposition
(~800 lines) — into `agentic-mbse/sysml/`, so any SysML tool (validation, docs, simulation)
can use them without depending on sysml-codegen. That includes the checking stack: agentic-mbse
should be able to enforce both general SysML quality and the optional "codegen-compatible
profile" from shared SysML facts, not by importing sysml-codegen. The design doc's two-phase
strategy stands (verified twice: 2026-07-06 refresh + this pass); TRUTH-DEBT has landed, so the
moved code is in its final shape ("born correct" per the sequencing ruling).

**Critical Success Factor**: after the move, each package answers one question — agentic-mbse
"what does this SysML model *mean*?", sysml-codegen extraction "how do we *transform* it for
codegen?" — with both suites green, baselines byte-identical, and the INV-1/INV-5 invariant
tests traveling with the moved code. agentic-mbse may know the sysml-codegen supported subset
as a named validation profile; it must not depend on sysml-codegen implementation.

---

## Why This Epic?

**Current State** (verified against HEAD `09d6a03`, branch `truth-debt-epic`, 2026-07-08):
- `extraction/expression_utils.py` (356 ln) is pure SysML — AST→text reconstruction,
  precedence-aware parenthesization, chain-segment extraction — but lives in codegen.
  5 src callers, all in extraction/. Untouched by TRUTH-DEBT (Item 2's diff was
  usage_extractor + dependency_backtracker; the segment extractor itself is stable).
- `core/qualified_names.py` (181 ln) is a **mixed** file: 6 SysML-general functions
  (`sanitize_name`, `build_element_qualified_name`, QN converters) plus 4 codegen name
  builders (`get_module_name`, `get_channel_name`, `build_parameter_qualified_name`,
  `owning_part_leaf`). The move is a split, not a whole-file move. 12 src importers.
- `extraction/hierarchy_resolver.py` (742 ln) mixes "what IS a redefinition/multiplicity"
  (SysML-general) with codegen text rewrite (`build_aggregation_expression`) and
  design-override extraction. Its data models live in `extraction/data_models.py` and are
  imported across four layers (resolution, orchestration, snapshot loader) — the re-export
  surface is production code, not a test helper.
- Reuse is blocked: agentic-mbse can traverse expressions but cannot reconstruct text,
  build qualified names, or read hierarchy — every consumer would have to depend on
  sysml-codegen.
- Checking is artificially weaker than generation: agentic-mbse can teach and audit some
  codegen-compatible modeling rules, but several rules require helpers that still live in
  sysml-codegen. That forces either duplicated logic or late failure inside generation.
- **Gate satisfied**: TRUTH-DEBT Items 1/2/6 all landed and audited (epic closed 2026-07-08).
  Item 1 finalized the aggregation path (`resolve_input(AGG_STRATEGIES)`, Strategy D and
  `_resolve_aggregation_input_channel` deleted); Item 6's hygiene fixes landed *outside* the
  move set (graph_builder, generation/registry, snapshot/loader).
- **Q10 answered this pass**: every `SysideAdapter.is_instance` type name used in the moving
  files is already in the adapter's TYPE_MAP whitelist (hard-error contract verified live at
  `syside_adapter.py:163`; the agentic-mbse repo at `/home/reid/1cfe/agentic-mbse` is readable
  from this session).

**Future State**:
- `agentic_mbse.sysml` gains `expression` extensions (reconstruction + literal helpers),
  `qualified_names` (general subset), `hierarchy`, and `aggregation` modules.
- sysml-codegen's extraction/ is codegen-only; `hierarchy_resolver.py` is a thin wrapper;
  shims/re-exports keep every existing import path working (permanent, by design — conformance
  tests assert filesystem paths).
- The INV-1 dispatch-totality and INV-5 sanitize-name invariant tests live next to the moved
  code; moved models stay dataclasses (no serialization churn); baselines byte-identical.
- The agentic-mbse validation stack can use these shared facts to enforce a named optional
  codegen-compatible profile: unsupported expression shapes, naming collisions, hierarchy
  idiom violations, and unsupported aggregation structures are caught while still in SysML.
- Tier 2c (template detection, virtual-binding matching) stays deferred until a second
  consumer exists; `constraint_report.py` stays (codegen reporting artifact).

---

## Success Criteria

- [ ] **SC-A (Phase 1 — expression + names)**: `expression_utils` functions extended into
  `agentic_mbse.sysml.expression` (with the `is_literal_node` rename and the
  `binding._extract_literal_value` fold-in); the SysML-general subset of `qualified_names`
  moves to a new `agentic_mbse.sysml.qualified_names`; sysml-codegen keeps working shims
  (`expression_utils.py` shim persists — conformance tests assert its path).
- [ ] **SC-B (Phase 2 — hierarchy + aggregation)**: `extract_redefinitions` /
  `extract_multiplicities` + `RedefinitionData` / `MultiplicityData` / `RedefinitionType`
  move to `agentic_mbse.sysml.hierarchy`; the aggregation decomposition core
  (`_walk_aggregation_ast`, `SumTerm` / `SingletonTerm` / `LocalTerm`) to
  `agentic_mbse.sysml.aggregation`; `hierarchy_resolver.py` becomes a thin wrapper (codegen
  text rewrite + design overrides stay); permanent re-exports in `data_models.py`; moved
  models stay dataclasses.
- [ ] **SC-C (governance)**: the INV-1 (`reconstruct_operator_expression` dispatch,
  `AGG_PYTHON_OPS`) and INV-5 (`sanitize_name`) fires-on-shape + silent-on-clean tests move
  with the code (R1); TYPE_MAP whitelist re-verified per move; every move lands
  branch-parked (agentic-mbse branch → re-export → green suite → merge; the editable-install
  pair is never left half-migrated).
- [ ] **SC-D (pre-flight hazards)**: the four standing hazards are resolved before their
  phase — `is_literal_expression`→`is_literal_node` rename (Q5), sysml-codegen `BindingInfo`
  renamed (Q4), `# INTENTIONAL DIVERGENCE` comment on `expression_compiler._sanitize_name`
  (Q6/R8), docstring cross-refs for `extract_feature_chain_name` vs `get_reference_name` (R6).
- [ ] **SC-E (gates)**: both suites green at every landing point (anchors: sysml-codegen
  2120 passed / 4 skipped / 0 xfailed; agentic-mbse 1240 passed / 1 skipped); ruff src ≤ 17;
  mypy src ≤ 97; baselines byte-identical (zero capture churn expected — moves, not behavior
  changes); docs + matrix rows updated with the code per R1.
- [ ] **SC-F (deferrals stay honest)**: Tier 2c (template detection, virtual binding) is
  re-filed with its post-refactor function inventory (`_find_instantiation_paths`,
  `_expand_template_calc_usages`, ...), not silently dropped; `constraint_report.py` stays
  with a recorded disposition (Q8: codegen artifact).
- [ ] **SC-G (checking profile)**: every pushed-down semantic helper either powers an existing
  agentic-mbse validation rule, adds a codegen-compatible profile rule, or files a named
  agentic-mbse backlog item with the exact rule, fixture shape, severity, and rationale. The
  profile is expressed as a contract over SysML facts, not by importing sysml-codegen.

---

## Epic Strategy

Land one coordinated cross-repository move at a time: add the agentic-mbse API and tests, switch sysml-codegen through permanent compatibility imports, then gate both repositories.
For each move, also close the checking loop: decide what the newly shared fact lets
agentic-mbse validate, then implement or file the codegen-compatible profile rule before the
item closes.

## Backlog Items

### Item 1: Expression Reconstruction Push-Down ✅

**Type**: Code/Integration
**Effort**: 1–1.5 days
**Dependencies**: None

**Objective**: Move reusable reconstruction, feature-chain, and literal helpers into `agentic_mbse.sysml.expression` while preserving the sysml-codegen public module.

**Scope**:
1. Pre-flight: add `extract_feature_chain_segments` to `expression_utils.__all__` and pin it. The function exists at line 279 but is currently omitted.
2. Move reconstruction, precedence, feature-chain, chain-segment, and literal helpers; retain old spellings as compatibility aliases.
3. Fold agentic-mbse binding's duplicate literal extraction into the shared API; move INV-1 tests; retain a permanent shim.
4. Checking-profile loop: update or file validation rules for expression shapes codegen relies
   on (operator support, literal-node handling, feature-chain segment support, and anonymous or
   unsupported expression forms). The rule must live in agentic-mbse as a SysML/profile check,
   not as a sysml-codegen import.

**Out of Scope**: Python compilation, binding classification, and CalcUsage extraction.

**Success Criteria**:
- [x] The segment helper is exported before and after migration.
- [x] Expression-profile validation impact is implemented or filed with fixture shapes and
  severity.
- [x] Both suites pass; baselines are byte-identical.

**Deliverables**: `.project/active/expression-reconstruction-push-down/{spec,design,plan}.md`

### Item 2: Qualified-Name Utility Split ✅

**Type**: Code/Integration
**Effort**: 1–1.5 days
**Dependencies**: Item 1

**Objective**: Move general name utilities to `agentic_mbse.sysml.qualified_names` while keeping codegen identifiers local.

**Scope**:
1. Move sanitization, element-QN/owner traversal, QN conversion, and simple-name extraction.
2. Move INV-5 tests and preserve sysml-codegen re-exports.
3. Checking-profile loop: update or file validation rules for naming hazards codegen relies on
   being caught early (non-injective sanitization, invalid generated identifiers, and
   qualified-name ambiguity).

**Out of Scope**: Parameter/module/channel builders and `owning_part_leaf` (codegen alias/scoping policy).

**Success Criteria**:
- [x] The shared API contains only the general subset; codegen builders remain local.
- [x] Name-profile validation impact is implemented or filed with fixture shapes and severity.
- [x] Both suites pass; baselines are byte-identical.

**Deliverables**: `.project/active/qualified-name-utility-split/{spec,design,plan}.md`

### Item 3: Hierarchy Primitives and Data Models ✅

**Type**: Code/Integration
**Effort**: 1.5–2 days
**Dependencies**: Items 1 and 2

**Objective**: Move reusable redefinition/multiplicity extraction and primitive models without moving design-specific policy.

**Scope**:
1. Add `agentic_mbse.sysml.hierarchy` with redefinition and multiplicity extraction.
2. Move `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` as field-identical standard-library dataclasses, following target `AttributeInfo`.
3. Re-export identical class objects and verify TYPE_MAP strings.
4. Checking-profile loop: update or file validation rules for hierarchy idioms codegen relies
   on (redefinition precedence, unsupported redefinition RHS, multiplicity shapes, missing
   instantiations, and ambiguous inherited attributes).

**Out of Scope**: Design overrides, usage-type and part-usage indexing, hierarchy orchestration, `HierarchyExtractionResult`, scoping, and module construction.

**Success Criteria**:
- [x] Design overrides and usage-type indexing remain in sysml-codegen.
- [x] Re-exports preserve type identity; snapshots remain byte-identical.
- [x] Hierarchy-profile validation impact is implemented or filed with fixture shapes and
  severity.

**Deliverables**: `.project/active/hierarchy-primitives-models/{spec,design,plan}.md`

### Item 4: Aggregation Decomposition and Compatibility Gates

**Type**: Code/Integration
**Effort**: 2–3 days
**Dependencies**: Item 3

**Objective**: Move neutral typed AST decomposition while preserving Python rewriting and pipeline assembly in sysml-codegen.

**Scope**:
1. Add shared invocation unwrapping, AST walking, unsupported-node reporting, and typed terms.
2. Move `SumTerm`, `SingletonTerm`, and `LocalTerm`; return no codegen identifiers or Python source.
3. Keep `build_aggregation_expression` as the local Python-rewrite/`AggregationExpressionData` adapter.
4. Gate sum, singleton, local, wrapper, literal, unsupported, and operator shapes; run both suites, import/type checks, and byte-identity gates.
5. Checking-profile loop: update or file validation rules for aggregation structures codegen
   accepts or rejects (sum, singleton, local, wrapper, literal, unsupported node, and operator
   shapes).

**Out of Scope**: Python rewriting, aliases, design overrides, usage-type indexing, scoping, graph resolution, module construction, template detection, and virtual-binding matching. These stay in sysml-codegen or deferred.

**Success Criteria**:
- [ ] Shared decomposition contains no Python source or codegen identifiers.
- [ ] The local adapter reproduces existing aggregation data exactly.
- [ ] Aggregation-profile validation impact is implemented or filed with fixture shapes and
  severity.
- [ ] Both suites pass; ruff/mypy do not regress; baselines are byte-identical.

**Deliverables**: `.project/active/aggregation-decomposition/{spec,design,plan}.md`

---

## Dependencies

**External**:
- `truth-debt-epic` branch merged to main (epic complete; human review + PR outstanding).
  PUSH-DOWN edits the same files — base on the merged state, not a parallel branch.
- agentic-mbse pending PRs merged first: PR #7 (`upstream-findings-sync`) and the
  `pipeline-truth-item4` companion. PUSH-DOWN lands new agentic-mbse modules; basing them on
  unmerged branches would stack three PRs deep.
- syside license NOT required for the moves themselves (conformance runs from committed
  snapshots; zero baseline churn expected). Needed only if an unexpected diff forces a
  reviewed re-capture.

**Internal**:
- TRUTH-DEBT — ✅ landed (the gate this epic waited on).

---

## Risks

*(Refined at decomposition; headline risks from the design doc's refresh:)*

| Risk | Impact | Mitigation |
|------|--------|------------|
| Half-migrated editable-install pair breaks the suite between sessions | High | Per-move branch-parking (SC-C); never end a session mid-move |
| Moved data models shift serialization (dataclass→Pydantic) | High | Keep dataclasses (explicit P3 exception); field-identical |
| Shim removal breaks path-asserting conformance tests | Med | Shims are permanent by design; direct-import cleanup is a separate, later decision |
| qualified_names split line drawn wrong (codegen builder leaks into agentic-mbse) | Med | Q7 answered at design; ADR-003 builders stay by name |
| Checking profile imports sysml-codegen and inverts the dependency | High | Profile rules are contracts over shared SysML facts in agentic-mbse; SC-G forbids sysml-codegen imports |

---

## Timeline

**Total Effort**: 6–8 days

| Item | Effort | Dependencies |
|---|---:|---|
| 1. Expression reconstruction | 1–1.5 days | None |
| 2. Qualified-name split | 1–1.5 days | Item 1 |
| 3. Hierarchy primitives/models | 1.5–2 days | Items 1–2 |
| 4. Aggregation decomposition/gates | 2–3 days | Item 3 |

---

## Source Documents

- `.project/concepts/agentic-mbse-push-down-design.md` — the design + 2026-07-06 refresh
  verdict (per-section callouts are the current truth; original prose is provenance) — *concept-design*
- `.project/research/20260220-163000_agentic-mbse-boundary-analysis.md` — the boundary
  analysis the design is based on (patterns P1–P6) — *research*
- `.project/backlog/epic_truth_debt.md` — the sequencing ruling this epic waited on; Items
  1/2/6 changed the move surfaces — *epic (completed)*
- `.project/backlog/BACKLOG.md` `[PUSH-DOWN]` entry — the gate note — *backlog*
- Verification pass 2026-07-08 (this epic_plan): line counts, function inventories, caller
  maps, TYPE_MAP whitelist coverage re-checked against HEAD `09d6a03` — recorded in
  "Why This Epic" above.

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-07-08
**Next Action**: Start Item 1 specification after external branch prerequisites merge.
