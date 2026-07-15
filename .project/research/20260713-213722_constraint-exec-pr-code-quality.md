---
date: 2026-07-13T21:37:22-07:00
researcher: Codex
topic: "Code quality, brittleness, duplication, and interpretability in the CONSTRAINT-EXEC PR"
tags: [research, code-quality, architecture, constraints, resolution]
status: complete
last_updated: 2026-07-13
---

# Research: CONSTRAINT-EXEC PR Code Quality

**Date:** 2026-07-13 21:37 PDT
**Researcher:** Codex
**Research Type:** Codebase / Architecture

## Research Question

Investigate the massive PR strategically rather than reading every changed file. Focus on the
quality and responsibilities of `part_instance_index.py` and `constraint_lowering.py`, whether the
implementation took brittle or test-driven shortcuts, duplication, more efficient approaches, and
whether the system can be explained coherently. Use the original `.project/` designs where useful.

**[OWNER] Expanded question:** the two named files were examples, not the intended
sample boundary. Determine how pervasive the same characteristics are across the PR by identifying
and sampling other likely hotspots, while also looking for counterexamples.

## Executive Summary

- **The concern is pervasive at integration boundaries, not uniformly across the PR.** The worst
  responsibility mixing is concentrated in `constraint_lowering.py`, `pipeline_builder.py`, and the
  live/offline graph-assembly pair. The same brittle style recurs elsewhere through tuple protocols,
  private cross-layer calls, raw qualified-name surgery, duplicated IR walks, and prose-only model
  invariants.
- **The two examples were not the whole finding.** A census of all 37 changed production Python
  files found that the PR introduced ten new Ruff complexity-threshold violations and removed two.
  Only three of the ten introduced violations are in `part_instance_index.py` and
  `constraint_lowering.py`; the rest occur in contract verification, CLI/registry generation,
  pipeline orchestration, and supplied-value materialization.
- **There are serious defects outside the focal files.** New Pydantic constraint models claim
  tagged-union and eligibility invariants but enforce neither (`resolution/models.py:250-322`).
  Snapshot rebuilding repeats the live constraint/materialization sequence
  (`snapshot/graph_rebuild.py:62-114,206-230`). Both new ExpressionIR renderers independently treat
  every unary arithmetic node as negation (`calc_compat_renderer.py:121-136`;
  `predicate_compiler.py:117-126`).
- **This is still not slapdash code written only to make tests green.** The implementation has
  strong corpus regression, parity, corruption, generated-code, and execution tests. The expanded
  license-free sample ran **138 passed, 43 skipped**. The weakness is adversarial coverage at
  representation boundaries: invalid model states, resolver conflicts, malformed IR arity, and
  live/offline phase drift.
- **The PR also contains real quality improvements.** `expression_compiler.py` shrank from 622 to
  339 lines, `constraint_report.py` from 176 to 70, `ModuleKind` replaces ambiguous Boolean flags,
  and most of the contract schema/sealing code is cohesive. The accurate verdict is **clustered
  architectural debt plus recurring boundary brittleness**, not blanket low quality.
- **I would not treat the current architecture as finished.** The shipped behavior is credible,
  but changes to path syntax, resolution precedence, IR shapes, aliases, multiplicity, graph
  topology, or snapshot phases remain expensive and risky.

## Scope and Sampling Method

The full local diff against `main` is **319 files, 46,509 insertions, 2,359 deletions**. The
production `src/` slice is much smaller and therefore enumerable: **41 files, +3,881/-607**, made
up of 37 Python files and four templates. Tests account for another **132 files,
+19,202/-1,706**.

The expanded investigation used a census first, then stratified sampling:

1. **Production census:** ranked every changed Python file by new/existing status, total size,
   churn, Ruff C901/branch/statement thresholds, broad exception/assert/private-access signals,
   and whether the diff crossed a complexity threshold.
2. **All new production Python:** read all 13 new Python files, **2,527 lines total**. The focal
   pair is 1,355 lines, or 54% of that new-code surface. The remaining 1,172 lines cover contracts,
   catalog/compiler generation, the calc compatibility renderer, and generation errors.
3. **Changed legacy hotspots:** fully read and diff-attributed `dependency_backtracker.py`,
   `parameter_groups.py`, `pipeline_builder.py`, `graph_builder.py`, `cli/__init__.py`, and
   `supplied_values.py`. This separated inherited complexity from PR-introduced complexity.
4. **Extraction/snapshot stratum:** fully read ten files spanning computed extraction, expression
   compilation, the main extractor, hierarchy, snapshot capture/rebuild/load/serialization, and
   resolution models. This supplied both boundary findings and clean counterexamples.
5. **Generation/control stratum:** read the module, pipeline, registry, stencil, test-generation,
   pipeline-context, snapshot-context, and template changes. This checked how new module kinds and
   constraints spread through output seams.
6. **Design and test trace:** read the relevant Item 4/5/6/7/8/9/13/14 designs, reviews, audits,
   and focused tests. Three subagents independently owned the new-subsystem, legacy-hotspot, and
   extraction/snapshot strata; the main pass cross-read their cited production files and reconciled
   attribution.

The expanded license-free validation selected 12 relevant test files across these strata:
**138 passed, 43 skipped**. Skips are the license-gated live/corpus cases. This remains a strategic
code-quality investigation, not a correctness certification of all 319 files or the companion repos.

## Priority Findings

| Priority | Finding | Assessment |
|---|---|---|
| High | Parallel resolver ladders | Predicted drift has already happened |
| High | `constraint_lowering.py` responsibility accretion | A subsystem is presented as one analysis module |
| High | Three definitions of concrete part instances | Cross-feature disagreement is possible |
| High | Constraint model invariants are prose-only | Impossible states construct successfully |
| High | Live and snapshot constraint phases are duplicated | Parity depends on two sequences staying aligned |
| High | Item 14 adds tuple/string repair protocols | Corpus gaps became new integration branches |
| High/Medium | String algebra at semantic boundaries | NewTypes provide labels, not invariants |
| Medium | Both new IR renderers repeat a unary-operator defect | Shared shape assumptions are not centralized |
| Medium | Production carries a test-only exit-selection seam | The production default makes the mechanism a no-op |
| Medium | Tests are deep but precedence-light | Golden-path confidence exceeds change-safety confidence |
| Medium | Materializer demand and graph extension compensate across boundaries | Control flow is harder to explain than it should be |

### 1. Parallel resolver ladders are the main brittleness source

The original spec required strict and lenient resolution to share one path so they could not drift.
The design explicitly reinterpreted this as **two ladders sharing only terminal disposition** and
acknowledged that the lookup rungs could diverge
(`.project/completed/20260713_constraint-lowering/design.md:124-148`). The design review warned that
the strict ladder omitted aliases, scoped aliases, scope climbing, and self-reference behavior used
by calc resolution (`.project/completed/20260713_constraint-lowering/design-review.md:114-128`).

That predicted drift occurred immediately:

- The first strict ladder was scoped lookup, alias lookup, target-QN design attribute, then error.
- `fusion_tea` forced a structured `scoped_alias_lookup` rung and an occurrence-scoped synthesized-QN
  match (`constraint_lowering.py:184-250`).
- Item 14 found a different `plant_values` shape and added a definition-scoped default rung plus a
  second demand pass (`constraint_lowering.py:252-266,397-440`;
  `.project/completed/20260713_constraint-migration-acceptance/run-report.md:6-24`).

The calc path still has a different algorithm: consumer-scoped and direct scoped keys, structured
aliases, flat aliases, ancestor-scope climb, SysML-QN lookup, leaf/parent and full-scope fallbacks,
self-reference rejection, and design-attribute heuristics
(`dependency_backtracker.py:480-838`). Only `terminal_disposition` is shared
(`dependency_backtracker.py:28-72`).

This is not merely verbose. Correctness depends on independently ordered algorithms remaining
semantically compatible. The next valid corpus shape can add another rung to only one path.

### 2. `constraint_lowering.py` no longer has a clear responsibility

The file grew from **61 → 215 → 471 → 707 → 821 → 843 → 889 → 913 lines** across Items 5, 7, 8,
and 14. The current responsibilities are:

- import-cycle error construction and path normalization (`constraint_lowering.py:61-115`);
- producer/design-value resolution (`:117-276`);
- identity minting and collision policy (`:279-308`);
- owner expansion and materializer demand discovery (`:341-440`);
- profile preflight and concrete lowering (`:504-664`);
- module naming, entry-point minting, graph construction, aggregator construction, and graph
  validation (`:667-898`).

The original design rejected putting this logic in `pipeline_builder.py` because that file was
already 900+ lines (`.project/completed/20260713_constraint-lowering/design.md:149-154`). The new
module has now reached the same size. More importantly, graph extension lives in `analysis/` while
`graph_builder.py` already builds calculation, formula, and aggregation modules, classifies and
groups entry points, topologically sorts, and validates channels
(`graph_builder.py:162-442,446-612,1599-1669`).

The module should be described as a constraint subsystem, not a lowering function. Its current name
and placement hide the real ownership graph.

### 3. Concrete-instance discovery is duplicated three ways

There are three definitions of “where a part exists”:

1. `_find_instantiation_paths` recursively discovers flat `__` paths for template calculations
   (`usage_extractor.py:313-369`).
2. `_structured_paths` duplicates that recursion to retain owners and expand multiplicity. Its
   docstring says it must be kept in sync **by hand** (`part_instance_index.py:139-194`). The design
   intentionally deferred a shared core to protect byte identity
   (`.project/completed/20260713_part-instance-index/design.md:159-165,323-330`).
3. `find_instance_paths_for_partdef` infers design instances from virtual calculation QNs and a
   child-name heuristic; aggregation later reconstructs EQNs from those dotted paths and the first
   design prefix (`pipeline_builder.py:380-466,632-717`).

The second implementation fixed a real gap: calculation-driven discovery cannot see a part that
has constraints but no calculations. The duplication was defensible inside an additive Item 4.
It is no longer a good end-state after the whole epic. Constraints, template calculations,
aliases, and aggregations can disagree about instance identity because they do not project from one
structure index.

### 4. Identifier types do not make invalid states unrepresentable

`ScopedKey`, `CanonicalChannel`, `SysMLQN`, and related identifiers are `NewType` wrappers. Their
docstrings say some separators are rejected, but construction performs no validation
(`identifier_types.py:21-43`). Every consumer still performs string algebra:

- `occurrence_scope` drops the first `__` segment (`constraint_lowering.py:77-90`);
- `_deindexed_scope` deletes every character inside brackets without validating numeric indices,
  balance, nesting, or segment boundaries (`:93-106`);
- `_reference_dotted` prefers any non-empty segment list and joins it with dots (`:109-115`);
- supplied-value materialization independently parses `::`, `.`, and bare names, then manufactures
  EQNs (`supplied_values.py:61-99`);
- aggregation scoping converts `__` → `.` and later `.` → `__`
  (`pipeline_builder.py:439-446,687-694`).

The registry provides exact getters over four namespaces but no canonical resolution request or
ordered policy (`output_registry.py:26-60,168-196`). This forces every consumer to know registry
key formats and lookup order. `_deindexed_scope` and `_reference_dotted` are symptoms; the missing
abstraction is a structured instance/reference path and a registry-owned resolver.

### 5. The test suite is substantial, but fragile seams lack conflict tests

Positive evidence matters:

- the live instance fixture asserts an exact nine-instance oracle, owner-name collision behavior,
  Cartesian multiplicity, subtype closure, diagnostics, and determinism
  (`tests/conformance/test_part_instance_index.py:48-179`);
- pipeline tests prove roots survive pruning, channel validation passes, identities repeat, and
  blocked profiles halt (`tests/conformance/test_constraint_pipeline_threading.py:20-187`);
- snapshot tests compare full graph bytes plus catalog identity
  (`tests/conformance/test_snapshot_constraint_parity.py:24-76`);
- execution tests cover satisfied, violated, indeterminate, negated, default override, and broken
  wiring (`tests/execution/test_constraint_execution.py:100-542`).

The gap is **precedence**, not rung existence. Resolver unit tests register one successful rung at a
time (`tests/unit/test_constraint_resolver.py:42-209`). There are no tests where occurrence and
de-indexed keys both exist, scoped and alias keys disagree, a channel competes with a design
attribute, or occurrence-QN and target-QN attributes both exist. Reordering the ladder could change
behavior while all direct tests remain green.

The normalization helpers also lack adversarial tests: malformed brackets, empty chain segments,
disagreement between `source_name` and `chain_segments`, or separator-bearing names. The instance
walker has no cycle, diamond-inheritance, zero-count, multi-blocked-path, or 10+-index numeric-sort
test. The live fixture is valuable, but it concentrates many claims in one model
(`tests/unit/test_part_instance_index.py:69-120`;
`tests/conformance/test_part_instance_index.py:20-179`).

The right characterization is: **strong regression depth on discovered corpus paths, weak change
safety at the representation and precedence seams.**

### 6. Materialization and graph extension reveal inverted responsibilities

`collect_bare_actual_demand` exists because supplied-value materialization originally scanned only
calculation bindings. It re-runs profile evaluation and owner expansion, catches generation errors,
and skips them so authoritative lowering can fail later (`constraint_lowering.py:397-440`). The
materializer then accepts this second demand stream and synthesizes `DesignAttributeData` using QN
formats the resolver reconstructs later (`supplied_values.py:206-312`). This is integration by
shared representation convention rather than an explicit value-resolution contract.

Likewise, `extend_graph_with_constraints` locally reimplements entry-point grouping, dedup/minting,
module creation, ordering, sorting, and validation after the main graph has already been assembled
and topologically sorted (`constraint_lowering.py:713-898`; `graph_builder.py:162-442`). Appending is
currently safe because constraints only depend on prior modules and the aggregator only depends on
constraints. A future constraint-to-constraint edge or richer aggregator topology would invalidate
that assumption.

### 7. `part_instance_index.py` is mostly deliberate complexity

The core types provide a good model: `PathStep` keeps structured owner/name/index identity,
cardinality is positively classified and otherwise blocked, ordering uses integer indices, and bulk
results expose blocked definitions (`part_instance_index.py:26-136,197-345`). The audit found one
test-motivated shortcut—bulk APIs silently swallowed blocked definitions so a determinism test could
finish—and required an explicit blocked mapping; that cure landed
(`.project/completed/20260713_part-instance-index/audit.md:32-108`).

Remaining debt:

- six helpers are imported from `usage_extractor`, including private functions
  (`part_instance_index.py:15-23`);
- closure and traversal are recomputed per query, and bulk APIs repeat queries per definition
  (`:291-345`); the design explicitly accepted this for the current corpus
  (`.project/completed/20260713_part-instance-index/design.md:376-378`);
- snapshot recording, frozen replay, corruption policy, and deserialization are a second
  responsibility added later (`part_instance_index.py:363-442`).

This module warrants consolidation, but it is not the same quality risk as the resolver ladder.

### 8. The PR added new hotspots outside the focal files

Comparing identical Ruff complexity checks on `main` and the PR prevents inherited debt from being
misattributed. The changed Python surface has 63 current C901/branch/statement findings versus 55
on `main`: ten findings were introduced and two disappeared with the old expression-AST builder.

| PR-introduced threshold crossing | Current result | Assessment |
|---|---:|---|
| `constraint_lowering.resolve_actual` | C901 19, 18 branches | New focal hotspot |
| `part_instance_index._structured_paths` | C901 11 | New focal hotspot |
| `contracts.verify_package` | C901 12 | Cohesive, but needs decomposition/error normalization |
| CLI `_generate_stencils` | 51 statements | Existing hotspot worsened |
| `generation.generate_registry` | 67 statements | Kind-specific accretion |
| `pipeline_builder.build_pipeline_context` | C901 14, 13 branches, 62 statements | New orchestration hotspot |
| `supplied_values.materialize_supplied_values` | C901 14 | New repair/materialization hotspot |

The current complexity in `graph_builder.py`, `dependency_backtracker.py`, most of
`parameter_groups.py`, and the extraction functions is severe but largely predates this PR. That is
still relevant architectural context, but it is not evidence that this PR created those functions.

The strongest new non-focal example is `build_pipeline_context`, now roughly 337 lines. The
constraint phases call the private backtracker method `_find_usage_for_channel`, split channel
strings with `rsplit("__", 1)`, reconstruct target strings, and build a `PartInstanceIndex` twice in
one pipeline call (`pipeline_builder.py:844,866-930`). The comments make the required ordering
traceable, but the ordering exists as one long procedure rather than composable phase objects.

### 9. Item 14 repairs representation gaps with new tuple and string protocols

`materialize_supplied_values` previously had no C901 finding. It now accepts
`constraint_actual_demand: list[tuple[str, str, str | None]]`, builds a nested `_demand` list, and
merges it with calc-binding demand (`supplied_values.py:206-269`). The tuple positions carry instance
scope, source path, and source file without a named type. A missing source file silently removes the
demand (`:264-268`). Constraint demand supplies no owning PartDef, so resolution relies on a new
special case: when `part_usage == attr`, compare an override owner directly to `instance_scope`
(`:126-135`).

The Item 14 plan honestly records this as a migration-discovered gap rather than original design
(`.project/completed/20260713_constraint-migration-acceptance/plan.md:336-345`). That provenance is
good. The implementation is still patch-on-patch repair: a constraint-only source was invisible to
the calc-only materializer, so the feature adds a second demand producer and a fixture-shaped
matching tier rather than introducing one typed value-demand contract.

### 10. New constraint models document invariants they do not enforce

`ConcreteConstraintInput` says exactly one resolution-specific field is populated, and
`ConcreteConstraint` describes executable fields as required whenever `eligible=True`
(`resolution/models.py:250-322`). Both are ordinary Pydantic models with nullable fields and no
model validators.

An explicit construction probe succeeded for both invalid states:

- `resolution=MODULE_OUTPUT`, `bound_channel=None`, and `design_attribute_qn="wrong"`;
- `eligible=True` with `predicate_ir=None` and `evaluation_channel=None`.

The direct model tests only construct and round-trip valid values
(`tests/unit/test_concrete_constraint_model.py:40-78`). Downstream code compensates with
load-bearing assertions and dereferences (`constraint_lowering.py:793-813`;
`constraint_catalog.py:86`). This is broader than path brittleness: the central data contract
permits states its consumers assume are impossible.

### 11. Live and snapshot graph assembly duplicate the same phase protocol

`snapshot/graph_rebuild.py` repeats the live pipeline's constraint-demand/materialization sequence
and its lower/extend/catalog sequence (`:62-114,206-230`). It also imports private live helpers from
`pipeline_builder.py` and `_classify_entry_points` from `graph_builder.py` (`:24-31,62-80`). The
comments explicitly say the path mirrors the live sequence.

Snapshot parity tests are valuable, but several live parity legs require a SysIDE license. The
default test environment therefore cannot always catch drift between the two orchestrators
(`tests/conformance/test_snapshot_constraint_parity.py:24-75`). The design chose behavioral parity,
but did not create a shared, serializable phase interface. This is the same maintenance pattern as
the resolver ladders: two sequences are kept equal by convention and tests.

The new snapshot gates themselves are otherwise careful. The avoidable weakness is using `assert`
for schema-version and capture-presence pins, which vanish under optimized Python
(`snapshot/loader.py:199-209`; `snapshot/capture.py:44-53`).

### 12. Both new IR renderers repeat unchecked shape assumptions

The new predicate compiler and calc compatibility renderer are cohesive modules, not god files.
They nevertheless repeat a latent semantic defect: every one-operand arithmetic operator renders
as unary minus, without checking that the operator is `-`
(`predicate_compiler.py:117-126`; `calc_compat_renderer.py:121-136`). A unary `+` therefore becomes
`-x` in both implementations.

The predicate compiler also indexes comparison operands without arity validation and can raise a
raw `IndexError` rather than `PredicateCompileError`; generated function signatures interpolate
raw leaf names without validating Python identifiers (`predicate_compiler.py:131-184,197-205`).
Its tests strongly cover Kleene truth-table semantics but not malformed arity, unary plus, or unsafe
identifiers (`tests/unit/test_predicate_compiler.py:67-160`).

The calc renderer separately classifies references once during rendering and again during
`collect_calc_refs` (`calc_compat_renderer.py:106-174`). Its literal dispatch depends on substring
matching the source class name (`:89-103`). The design reasonably rejected one dual-mode renderer,
because the two dialects have different output policy. A shared validated IR visitor or shared
arity helpers would remove duplicated shape bugs without forcing the policies together.

### 13. Some production code exists solely to make a structural test possible

`generation/pipeline.py` added `selected_channels` and `pin_report_channels` to the production exit
builder. Its documentation states that production has no exit-narrowing feature and always calls
the no-op default; the parameters exist so a test can exclude the report channel, turn the pin off,
and prove that turning it on restores the channel (`pipeline.py:233-288`). The design review itself
required this seam because the intended control leg was otherwise unconstructible
(`.project/completed/20260713_constraint-generation/design-review.md:80-108`).

This is direct evidence of test-shaped production code. It is not a hidden shortcut—the design,
plan, and docstring all disclose it—but the implementation proves a hypothetical future selection
mechanism rather than current production behavior. Either real exit selection should own this API,
or the test should prove the actual capture-everything behavior without adding dormant production
branches.

### 14. Clean counterexamples constrain the verdict

The broader review found code that is small and interpretable:

- contract models, deterministic serialization, versions, and sealing have clear responsibilities
  (`contracts/models.py:19-113`; `serialize.py:22-25`; `seal.py:57-86`);
- the deliberately duplicated glob matcher is required by the standalone stdlib verifier and has
  an AST-body drift test (`tests/unit/test_contract_models.py:161-184`);
- catalog assembly is cohesive and explicit (`constraint_catalog.py:60-108`);
- `ModuleKind` replaces a two-Boolean invalid state with one enum
  (`resolution/models.py:161-203`);
- the expression migration deletes the old private AST surface: `expression_compiler.py` shrank
  622→339 lines and `constraint_report.py` 176→70.

`contracts/verify.py` is a middle case rather than a god module. Its one algorithm is readable, but
missing/malformed seals and absent keys escape the advertised `VerificationResult` API, it uses
string identity in the strict mismatch check, and `verify_package` is C901 12
(`contracts/verify.py:100-181`). The earlier package-contract audit already noted the missing-seal
behavior (`.project/completed/20260713_package-contracts/audit.md:146`). This is boundary hardening
debt, not responsibility chaos.

The prevalence conclusion is therefore specific: **extreme responsibility mixing is clustered;
representation-driven brittleness is widespread across the constraint integration seams; clean
leaf components and meaningful deletions also exist.**

## Architecture Mental Model

```text
live SysML model
  ├─ usage_extractor ── flat calc-instance paths ── calc usages
  │                                              ├─ pipeline_builder phase sequence
  │                                              ├─ OutputRegistry exact string keys
  │                                              └─ DependencyBacktracker resolver ladder
  │                                                   └─ graph_builder calc/formula/agg graph
  │
  └─ constraint facts ── PartInstanceIndex structured paths
                         └─ constraint_lowering's separate resolver ladder
                              └─ append constraint/aggregator nodes after graph build

snapshot v3 ── graph_rebuild repeats registry enrichment, value materialization,
               constraint lowering, graph extension, and catalog assembly

combined graph ── per-ModuleKind dispatch repeated across CLI + six generation seams
```

Extraction produces several partially structured representations. `pipeline_builder` rewrites and
materializes them. `OutputRegistry` stores exact keys but does not own resolution policy. Calc and
constraint resolution independently interpret those keys. The snapshot path repeats the phase
ordering, and generation redispatches kinds at each output seam. That parallelism—not one
intrinsically hard algorithm—is why the codebase is difficult to understand.

## Feasibility Assessment

Refactoring is feasible without changing generated artifacts, but the order matters. A direct
rewrite of both resolver ladders inside this PR would be high risk because byte identity and
cross-repo acceptance are load-bearing. The code already has strong behavior-level fixtures, which
can protect a staged refactor.

The lowest-risk first move is to introduce typed, behavior-preserving path and resolution-request
objects behind existing APIs. After parity gates hold, consumers can migrate one at a time. A
mechanical file split alone would improve navigation but would not remove brittleness; it would only
move the string conventions into more files.

## Recommendations

These are `[AGENT]` recommendations, not owner-settled decisions.

1. **Validate the new constraint models now.** Make `ConcreteConstraintInput` a discriminated union
   or add a model validator for its resolution-specific field. Validate the `eligible` relationship
   to predicate IR, evaluation channel, polarity, and input payload. Add negative construction tests.
2. **Before treating the PR as architecture-complete, write a refactor design around one canonical
   path and resolution model.** Define `InstancePath`, `ReferencePath`, `ConstraintDemand`, and a
   public resolution-root type. Give each explicit, validated conversions to EQN, dotted scope,
   de-indexed scope, and SysML QN.
3. **Add conflict/precedence tests before refactoring.** Pin occurrence vs de-indexed, scoped vs
   alias, channel vs design attribute, occurrence-QN vs target-QN, and ambiguity behavior. Add
   adversarial path grammar tests and a differential singleton test between recursive walkers.
4. **Move lookup policy behind the registry.** Normalize calc `BindingInfo` and constraint
   `FeatureReferenceFact` into one resolution request. A shared ordered strategy should handle both;
   `strict` vs `lenient` should change only terminal disposition.
5. **Build one `PartStructureIndex` once per pipeline.** Use it for template expansion, constraint
   occurrences, alias expansion, materializer demand, and aggregation scoping. Project legacy
   strings at the edges until byte-identity gates permit deleting the old walkers.
6. **Extract shared live/offline phases.** Registry enrichment, value-demand materialization,
   lowering, graph extension, and catalog assembly should be callable phase objects over explicit
   inputs. `pipeline_builder.py` and `snapshot/graph_rebuild.py` should orchestrate the same phases,
   not mirror their bodies and import each other's private helpers.
7. **Separate constraint expansion from graph construction.** Keep fact/profile/owner expansion in
   analysis. Move constraint module and entry-point factories into graph assembly, then run one
   grouping, topological sort, and validation pass across every module kind.
8. **Introduce shared ExpressionIR shape validation.** Centralize operator arity, unary-operator,
   and identifier validation. Keep calc and predicate rendering policies separate, but make both
   consume the same validated node contracts.
9. **Remove or promote the exit-pin test seam.** If user-selectable exits are real future behavior,
   implement and own that API. Otherwise do not carry `selected_channels`/`pin_report_channels`
   branches in production solely to construct a test control.
10. **Replace load-bearing `assert`s with explicit errors.** Current semantic-version, same-IR,
    capture-presence, leaf-type, and eligible-input invariants can disappear under `python -O`
    (`constraint_lowering.py:531-534,597-604,793-802`; `part_instance_index.py:280-289`;
    `snapshot/loader.py:199-209`; `snapshot/capture.py:44-53`).
11. **Split snapshot transport from the live index.** Keep `OccurrenceIndex` near analysis, but move
    recording/frozen/deserialization adapters to the snapshot package
    (`part_instance_index.py:363-442`).
12. **Measure before optimizing occurrence lookup.** Cache subtype closure and occurrence queries
    only after a corpus benchmark shows it matters; the maintainability risks are more urgent
    (`part_instance_index.py:291-345`).

## Merge-Risk Judgment

I found no evidence that the feature is broadly incorrect, and the existing audits plus test depth
make a functional rollback hard to justify. I also would not bless the current form as a clean
long-term architecture.

The minimum merge bar I recommend is:

- rejection tests and validators for impossible `ConcreteConstraintInput` / eligible-constraint
  states;
- precedence/conflict tests for `resolve_actual`;
- adversarial tests for path de-indexing and reference normalization;
- malformed-arity and unary-operator tests for both IR renderers;
- explicit errors in place of the load-bearing snapshot/constraint asserts;
- a recorded, owned follow-up design for unified path/instance/resolution infrastructure, with the
  duplicate walkers, live/offline phase duplication, and post-build graph extension explicitly in
  scope.

The model validators and renderer-shape guards are small correctness hardening and should land
before merge. The canonical paths, shared resolver, and shared live/offline phases are larger. If
the team expects this PR to establish the permanent constraint architecture, do that work before
merge. If the goal is to land the validated capability now, merge only with those items recorded as
owned architecture work rather than a vague cleanup note.

## Open Questions

1. Is calc-resolution fallback behavior meant to remain more permissive than constraint resolution,
   or should both share every lookup rung and differ only at the terminal disposition?
2. Can one model legitimately contain multiple design roots? Aggregation scoping currently warns
   and uses the first prefix (`pipeline_builder.py:650-672`). A unified instance index needs an
   explicit answer.
3. Are fixed-multiplicity calculation producers intentionally shared across sibling constraint
   occurrences? The current design records that as an accepted limitation rather than expanding
   producers (`.project/completed/20260713_constraint-lowering/design.md:99-112`).
4. Which artifact owns supplied-value precedence long term: extraction facts, a value-resolution
   service, or graph assembly? Today it is split between `supplied_values.py`, hierarchy data, and
   constraint demand discovery (`supplied_values.py:100-203`; `constraint_lowering.py:397-440`).
5. Are invalid `ConcreteConstraint` states expected to be constructible for transitional/offline
   use? No current caller or model documentation identifies such a need; the field documentation
   says the opposite (`resolution/models.py:250-322`).
6. Is exit selection a real upcoming production feature? If not, what production behavior is the
   test-only `selected_channels` seam intended to protect (`generation/pipeline.py:233-288`)?

## Key Code References

- `src/sysml_codegen/analysis/constraint_lowering.py:77-276` — path adapters and strict resolver.
- `src/sysml_codegen/analysis/constraint_lowering.py:397-440` — compensating constraint-demand pass.
- `src/sysml_codegen/analysis/constraint_lowering.py:504-898` — lowering plus graph extension.
- `src/sysml_codegen/analysis/part_instance_index.py:139-194` — duplicated structured walker.
- `src/sysml_codegen/analysis/part_instance_index.py:267-442` — live query plus snapshot adapters.
- `src/sysml_codegen/analysis/dependency_backtracker.py:480-838` — competing calc resolver.
- `src/sysml_codegen/extraction/usage_extractor.py:272-369` — part-usage index and flat walker.
- `src/sysml_codegen/orchestration/pipeline_builder.py:380-717` — third instance-path algorithm.
- `src/sysml_codegen/orchestration/pipeline_builder.py:833-1012` — PR-added constraint phases.
- `src/sysml_codegen/resolution/supplied_values.py:126-269` — repair tier and tuple demand protocol.
- `src/sysml_codegen/resolution/graph_builder.py:162-612` — normal graph/entry-point assembly.
- `src/sysml_codegen/resolution/models.py:250-322` — documented but unenforced constraint invariants.
- `src/sysml_codegen/snapshot/graph_rebuild.py:62-114,206-230` — duplicated offline phases.
- `src/sysml_codegen/generation/predicate_compiler.py:103-205` — unchecked IR shape assumptions.
- `src/sysml_codegen/extraction/calc_compat_renderer.py:70-174` — parallel renderer/traversal.
- `src/sysml_codegen/generation/pipeline.py:233-288` — test-only exit selection/pin seam.
- `src/sysml_codegen/contracts/verify.py:100-181` — cohesive but brittle verification boundary.
