# Spike: S4 — Vertical Slice: Lowering, Liveness, Generation, Execution

## Summary of Findings

**Verdict: the whole cross-repo seam works. All three pass criteria hold, on the first
execution run, with zero changes to production code in any repo.**

1. **Both truth values complete with identical ordinary outputs and the expected report**
   — under the *real* TEAx runtime (simkit from the teax working tree), not a stub. At the
   satisfied point (budget 5000) the run returns area 12.0, cost 3000.0, evaluation
   `satisfied` with margin +2000.0 and observed operands `{cost: 3000, budget: 5000}`,
   headline `all_satisfied`. At the violated point (budget 2500) the run **completes** —
   violation is evidence, not an exception — with `violated`, margin −500.0, headline
   `violation`, and byte-identical ordinary outputs. The report and evaluation persist as
   JSON artifacts beside the ordinary outputs on the file-backed run, and the aggregator's
   exact input schema rejects a missing assertion result with a `ValidationError`.

2. **Targeted generation retains the producer only via the constraint dependency.** The
   control run (pruning enabled, minimal exit selection: only `area_calc.area` targeted, no
   lowering) produces a graph containing **only** `area_calc` — `cost_calc` is pruned. The
   lowered run strictly resolves the `cost` actual to the producer channel
   `toy_plant__demo_plant__cost_calc__cost`, joins it to the backtracking roots before
   pruning (via the existing `_find_usage_for_channel` seam — no backtracker changes), and
   `cost_calc` survives. The liveness claim was falsifiable and did not falsify.

3. **Live and snapshot artifacts are byte-identical**: 24/24 generated files equal across
   the two legs, same catalog and executable fingerprints, and a second independent live
   load reproduces the same executable fingerprint
   (`3be9f72d237e8c1c…`). The snapshot leg reads constraint facts from a test-only sidecar
   and **refuses** when the sidecar is absent (S3's strict boundary, honored here).

Strict resolution held with no fallback anywhere: the chain actual resolved by
`OutputRegistry.scoped_lookup` in the owner-instance scope, the reference actual by exact
sanitized-QN match against design attributes, minting
`toy_plant__Toy_Plant__plant_budget` (default 5000.0) as a `DESIGN_ATTRIBUTE` entry point
in its derived group `toy_plant_params` — V11 coverage and channel-reference validation
both pass on the extended graph.

### Seam findings for spec/design (what production work must change)

- **`module_kind` is confirmed as a real need, everywhere.** Production generation is
  calc-shaped at four seams the probe had to route around: `_get_python_path` /
  `_check_duplicate_output_paths` assume `calc_def_qualified_name`; `generate_registry`
  derives class names from `calc_def_name` and dedups by it; `_generate_modules` and
  `_generate_stencils` would render calc wrappers/stencils for a constraint
  `PipelineModule`. The probe generated ordinary artifacts through production code and
  constraint module / aggregator / constraint schemas / registry through test-only
  emitters. This is exactly the `PipelineModule.module_kind` redesign the concept bets on.
- **TEAx needed zero changes.** Registry introspection accepted
  `ModuleBase[Input, MultiOutput-subclass]` constraint modules; a single-field
  `MultiOutput` output puts the whole `ConstraintEvaluation` on one channel (no scalar
  field-reference gap); the validator type-checked structured channels end-to-end via the
  generated `CUSTOM_SCHEMA_TYPES`; the JSON output router persisted the custom types by
  name. Caveat: the `RootModel[float]` exit writers used here are part of teax's
  **uncommitted** scalar-persistence working tree (HEAD `c9e1e85` lacks them) — the
  concept's S5 prerequisite (finish/audit/merge that work) stands.
- **Constraint-module identity:** a YAML module instance does not learn its own key at run
  time, so the probe generated **one class per concrete assertion** with `CONSTRAINT_ID`
  embedded. Production must choose class-per-concrete-assertion or an id-injection
  mechanism; per-definition classes alone cannot label their evidence.
- **Aggregator exit-ancestry is currently free, not guaranteed:** the generated exit point
  captures *every surviving module output*, so the report channel rides along. "Minimal
  exit selection" lives at the graph/pruning level (backtracker targets), not in the YAML
  exit. If production ever narrows the YAML exit, the aggregator must be an explicit
  member.
- **Def-level compile, usage-level wire, works.** The predicate compiles once from the
  definition's IR with formal-named arguments (S2's compiler, embedded Kleene runtime);
  actual resolution only decides what the YAML wires into those arguments. No
  per-instance predicate rewriting was needed.
- **Entry-point minting slots into the existing deriver.** The budget EP joined its
  derived parameter group by membership lookup in `derive_groups()`; no new grouping
  machinery.

### Not exercised here (bounded scope, for spec awareness)

Modeled-default formals (the probe's lowering refuses them; wi014 has none), the
zero-assertion aggregator, an indeterminate (non-finite) execution point, inline-source
and negated assertions at execution (S2 proved their compile-time semantics), and
multi-instance expansion (S3 proved discovery/ID determinism; wi014 has one instance).
Contracts here are test-only shapes: the seal covers content hashes and verifies on load,
but coverage sets, environment compatibility, and stale-file detection remain design work.

## Question / Goal

[INHERITED: `.project/concepts/constraint-execution-and-design-space-studies-claude.md`,
Appendix B, S4] Assumption under test: the whole cross-repo seam works on one real model.
Concretely, S1's captured facts for WI-014's `affordable` can be fed through a **test-only
lowering path** — strict resolution of `cost_calc.cost` (producer channel) and `plant_budget`
(design-attribute entry point), resolved constraint inputs joining the backtracking roots
**before pruning** — and generation then emits one structured constraint module, the
exact-schema report aggregator, schemas, registry, pipeline YAML, and sealed test-only
contracts, which execute under the real TEAx runtime.

Pass criteria (from the concept):

1. Both truth values (satisfied and violated points) complete with identical ordinary
   outputs and the expected constraint report.
2. Targeted generation retains the producer: with pruning enabled and a **minimal exit
   selection** (only `area_calc.area` targeted), `cost_calc` survives *only* via the
   constraint dependency — proven by a control run without lowering where it is pruned.
3. Live and snapshot generation produce byte-identical artifacts.

Failure selects the exact graph or schema seam to redesign before production work.

Consumes S1 (fact shapes — `agentic-mbse/.project/active/spike-constraint-fact-shapes/`),
S2 (ExpressionIR + Kleene compiler — `../spike-expression-tree-parity/`, whose `s2_ir.py`
this spike reuses), and S3 (instance index + strict snapshot boundary —
`../spike-concrete-expansion-instance-index/`).

Oracle note carried from S2: live SysIDE cannot resolve usage-supplied cross-part actuals,
so concrete verdicts here come from the generated code path; the fixture's hand-transcribed
literals (cost 3000 = 4·3·250, budget 5000) are the oracle.

Metadata at start:

- Date: 2026-07-11 13:48 PDT
- Repo: sysml-codegen, branch `constraint-design-explore`, commit `1c70e68`
- Companion repos: agentic-mbse `/home/reid/1cfe/agentic-mbse`, teax `/home/reid/1cfe/teax`
- teax state: HEAD `c9e1e85` with **uncommitted working-tree changes** to
  `simkit/io/output_router.py` and `simkit/core/pipeline_validator.py` (the in-flight
  scalar-persistence work). S4 executes against the working tree.

## Log

### 1. Context and baseline (read-only)

- Read the concept (S4 scope), S1/S2/S3 findings, `CURRENT_WORK.md`.
- Mapped the codegen seams the probe uses:
  - `build_pipeline_context(paths, targets, include_all=False)` is the pruning path;
    `run_codegen` never passes targets, so the probe drives the steps directly
    (`orchestration/pipeline_builder.py:685`).
  - Backtracker targets are `"instance.output"` where `instance` is the usage
    `instance_name` — which for these fixtures is the **full EQN**
    (`toy_plant__demo_plant__area_calc`), confirmed from the committed snapshot.
  - `_find_usage_for_channel` maps a resolved channel back to its producing usage — the
    seam that turns strictly-resolved constraint input channels into backtracking roots
    (`analysis/dependency_backtracker.py:466`).
  - Generation is graph-driven (`cli/__init__.py:780` orchestrates `_generate_*` helpers);
    the pipeline YAML exit point captures every module output, so the aggregator's report
    channel becomes an exit ancestor for free (`generation/pipeline.py:222`).
  - Snapshot leg: `build_classifier_inputs_from_snapshot` re-runs registry + backtracker
    offline (`snapshot/graph_rebuild.py:26`); the probe re-runs it **targeted** and reads
    constraint facts from a test-only sidecar file, refusing when the sidecar is absent
    (S3's strict-boundary lesson).
- Mapped the TEAx runtime surface (real simkit, `teax/packages/teax-simkit`):
  - `execute_pipeline(yaml, out_dir, registry=..., custom_schema_types=[...])`; registries
    are built by introspection of `ModuleBase[Input, Output]` type params.
  - A module whose OutputModel subclasses `MultiOutput` gets one channel per field — so a
    constraint module with a single `evaluation: ConstraintEvaluation` field emits one
    structured channel, and the aggregator binds that **whole channel** (no field
    reference), exactly the shape the concept prescribes for scalar-gap avoidance.
  - Exit outputs need a registered write handler per type name;
    `create_output_router_with_json_schemas` registers JSON writers for custom type names
    (the generated `CUSTOM_SCHEMA_TYPES` list is the carrier).
- Environment: this repo's venv has no syside license (S3 finding), so live legs run in the
  agentic-mbse venv with `PYTHONPATH=/home/reid/1cfe/sysml-codegen/src`. teax's `.venv` has
  no deps installed and `uv run` fails on the workspace root's setuptools discovery, but the
  agentic-mbse venv carries every simkit dependency (pydantic, yaml, pandas, dotenv,
  pyarrow), so execution also runs there with `sys.path` pointing at
  `teax/packages/teax-simkit` — the real simkit code, hosted in a licensed venv.

### 2. Probe design

Scripts in this folder:

- `s4_lib.py` — shared test-only lowering + generation library (fact capture, strict
  resolution, graph extension, constraint/aggregator/registry emitters, contracts, seal).
- `probe_a_live.py` — live leg: control pruning run, lowered run, full package generation,
  snapshot + constraint-facts sidecar capture.
- `probe_b_snapshot.py` — snapshot leg: targeted rebuild + lowering from the sidecar,
  package generation, missing-sidecar refusal check, byte-compare against the live package.
- `probe_c_execute.py` — real-simkit execution of the sealed package at the satisfied and
  violated points, plus the aggregator exact-schema negative check.

Generation on **both** legs consumes the *serialized* sidecar (probe A writes it, then
reloads it before generating), so the JSON round-trip is on the byte-identity path.

### 3. Probe A — live leg (PASSED, first run)

Observed:

- Fact capture (S1 shapes, live SysIDE 0.8.4): one `AssertConstraintUsage` `affordable`,
  definition-typed, positive polarity, owner `toy_plant::'Toy Plant'`; predicate IR
  `cost <= budget`; actuals `cost -> chain [cost_calc, cost]`,
  `budget -> reference target_qn [toy_plant, Toy Plant, plant_budget]`; formals recovered
  by owner-filtered `AttributeUsage` enumeration (S1's pinned 0.8.4 quirk: the definition's
  `parameters` omits them). Owner instance found from **part structure** (`PartUsage`
  `demo_plant` typed by the owner def — S3's direction, no calc templates):
  `toy_plant__demo_plant`.
- Control graph: `["toy_plant__demo_plant__area_calc"]` — cost_calc pruned.
- Lowered graph: area_calc, cost_calc, `toy_plant__demo_plant__affordable`,
  `constraint_report_aggregator`; root channel derived from strict resolution:
  `toy_plant__demo_plant__cost_calc__cost`.
- Entry points: the four design attributes incl. the minted
  `toy_plant__Toy_Plant__plant_budget`, all in group `toy_plant_params`.
- 24 artifacts generated + sealed; `executable_fingerprint=3be9f72d…`. A second live run
  reproduced the identical fingerprint (determinism across live loads).

### 4. Probe B — snapshot leg + byte parity (PASSED)

- Missing-sidecar refusal fires with a re-capture instruction (a current-version snapshot
  without constraint facts never loads as an empty catalog — test-only enforcement of the
  invariant; production must make the section load-bearing per S3).
- Snapshot-leg summary equal to the live leg on every compared key (module sets, roots,
  IDs, EPs, both fingerprints).
- Byte-compare: **0 differing files** out of 24.

### 5. Probe C — execution under real simkit (PASSED)

- Seal verified before execution (hash check over every artifact + no unhashed extras).
- Satisfied point: channels `area=12.0`, `cost=3000.0`, evaluation
  `satisfied/actual_value=True/margin=+2000.0/observed={cost:3000,budget:5000}`, report
  `all_satisfied`, `assessed_count=1`, result keyed by `constraint_id`.
- Violated point (inputs JSON `plant_budget=2500.0`): run completes without raising;
  evaluation `violated/actual_value=False/margin=-500.0`; report `violation`; ordinary
  outputs byte-equal to the satisfied point; `constraint_report.json` written in the run
  directory with the violated result, manifest records it as produced.
- Aggregator exact schema: constructing the input with a missing per-assertion field
  raises `ValidationError` — a missing result is a schema failure, not a silent gap.

Generated pipeline YAML shape (abridged; full file at
`out/package_live/pipelines/pipeline.yaml`):

```yaml
  toy_plant__demo_plant__affordable:
    module_type: toy_plant.DemoPlantAffordableConstraintModule
    inputs:
      budget: float toy_plant_params.toy_plant__Toy_Plant__plant_budget
      cost: float toy_plant__demo_plant__cost_calc__cost.root
    outputs:
      evaluation: ConstraintEvaluation toy_plant__demo_plant__affordable__evaluation

  constraint_report_aggregator:
    module_type: constraints.ConstraintReportAggregatorModule
    inputs:
      toy_plant__demo_plant__affordable: ConstraintEvaluation toy_plant__demo_plant__affordable__evaluation
    outputs:
      constraint_report: ConstraintReport constraint_report
```

(Also visible there: the EXPOSE alias machinery stayed consistent on the targeted graph —
the cost channel's exit file is the modeler-named `demo_plant__total_cost.json`.)

## Reproduction

From anywhere (paths are absolute; probes must run in order A → B → C; `out/` is fully
regenerable and safe to delete first):

```bash
# A: live leg — capture, control + lowered graphs, generate, snapshot + sidecar
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
uv run --directory /home/reid/1cfe/agentic-mbse python \
  /home/reid/1cfe/sysml-codegen/.project/active/spike-vertical-slice-constraint-execution/probe_a_live.py

# B: snapshot leg + missing-sidecar refusal + byte-compare
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
uv run --directory /home/reid/1cfe/agentic-mbse python \
  /home/reid/1cfe/sysml-codegen/.project/active/spike-vertical-slice-constraint-execution/probe_b_snapshot.py

# C: execute both truth points under real simkit (teax working tree)
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
uv run --directory /home/reid/1cfe/agentic-mbse python \
  /home/reid/1cfe/sysml-codegen/.project/active/spike-vertical-slice-constraint-execution/probe_c_execute.py
```

Expected: each probe prints `PROBE {A,B,C} PASSED` and exits 0. Probe B additionally
prints `0 differing file(s)`.

## Open Questions / Follow-ups

- **S6 handoff:** the sealed package at `out/package_live` (regenerate via probe A) is the
  real evaluator target S6's study-lifecycle spike can finish against.
- **Production `module_kind`:** the four calc-shaped generation seams listed in the
  Summary are the concrete work list for retiring the probe's emitters.
- **Constraint-module identity decision** (class-per-concrete-assertion vs id injection)
  goes to spec/design.
- **teax scalar-persistence work is still uncommitted**; the file-backed leg of this spike
  depends on it. S5's finish/audit/merge prerequisite is unchanged.
- **Not exercised:** modeled-default formals, zero-assertion aggregator, indeterminate
  execution point, negated/inline assertions at execution, multi-instance expansion —
  each has upstream spike coverage of its semantics but no vertical-slice execution yet.
