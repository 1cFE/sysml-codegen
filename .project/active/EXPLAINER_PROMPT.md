# Prompt: Interactive Pipeline Explainer (post-CONSTRAINT-LIFECYCLE, merged main)

Copy everything below the line into a fresh agent session in
`/home/reid/1cfe/sysml-codegen`, on branch `main` — the constraint PR wave is merged
(sysml-codegen `936315c`, agentic-mbse `f4ebdce`, teax `fa0e06a`). Three epics landed since
the Gen-1 explainer: **PIPELINE-TRUTH** (whole-plant value resolution, the F4 aggregation
cutover, silent-failure hardening); then **CONSTRAINT-EXEC** (modeled assertions now
*execute* — they lower to constraint modules evaluated under three-valued Kleene semantics,
snapshots went to v3, and packages seal); and then **CONSTRAINT-LIFECYCLE** (the lifecycle
remediation — it unified the three drifted resolver ladders into one `resolve_producer`
table, made extraction diagnostics load-bearing with a versioned severity contract, took
snapshots to v5 with a portable whole-tree referent, added trusted-package bootstrap and
seal provenance, made the embedded model-contract catalog the sole schema authority (catalog
schema 2.0.0), and landed the stock multi-entry TEAx bridge). The sysml-codegen reference
docs were re-projected onto merged main in the docs-lifecycle-sync sweep; trust them and cite
them rather than re-deriving.

---

Build a single self-contained interactive HTML explainer of the **sysml-codegen
pipeline** — what it is for, how it works algorithmically, and how it is operated —
current as of merged main (`936315c`). The facts below carry through: the GREEN
PIPELINE-TRUTH Item-3 fusion-tea acceptance run generated the full package at zero V11
offenders with run-C's lcoe reproducing bit-exactly ($270.1211779380445/MWh) through the
generated package alone; CONSTRAINT-EXEC then added the constraint-execution path on top
of that without disturbing the constraint-free byte-identity baselines; and CONSTRAINT-LIFECYCLE
then certified the whole lifecycle on one pinned, sealed artifact thread — all 41 mandatory
acceptance cases through public live and relocated-snapshot routes, the stellarator's five
constraint verdicts with six bit-exact anchors, and IFE's 2,301-point grid with unchanged
numerics.

## The one-paragraph subject

sysml-codegen turns SysML v2 system models into executable Python simulation pipelines
(TEAx-style). A modeler writes calc definitions (algorithms) and part hierarchies with
attribute values and bindings (configuration); the pipeline extracts those via the
syside parser, resolves who-feeds-whom into a `ComputationGraph`, and generates module
wrappers, implementation stencils, JSON input schemas, and pipeline YAML. Its sibling
repo **agentic-mbse** teaches and enforces the modeling patterns this pipeline assumes —
the two form one contract: `docs/architecture/modeling-assumptions.md` says what models
must look like; sysml-codegen executes that subset; agentic-mbse's validation checks
catch violations before execution does.

## Voice and explanatory method (non-negotiable)

Follow `~/agentic-project-init/claude-pack/rules/working-voice.md`, applied to an
explainer:

- Plain language first; anchor the precise term in parentheses on first use — e.g.
  "a name that forwards a calc output to the part boundary (the EXPOSE pattern,
  `EXPOSE_PURE`)". Never coin a phrase and reuse it as if memorized.
- Lead with the point. Every section opens with what the thing is FOR, then how it
  works, then the edge cases.
- Build a mental model in layers; each layer earns the next. No hedging, no resume
  words, no inflated stakes.
- Exact over vague: if a simplification erases a real distinction (e.g. shape A vs
  shape B EXPOSE), it's wrong, not simple.

## Structure: top-down, detail easy but OPTIONAL

The reader chooses their depth. Suggested layer stack (each layer is complete and
honest on its own; drilling down is a click, never required):

- **L0 — Why this exists.** Model-based systems engineering meets executable
  simulation: one SysML model, generated code, no hand-plumbing. Who uses it
  (fusion-tea's plant models are the real consumer) and what "done" looks like (an
  importable package + pipeline YAML + pre-filled input JSONs).
- **L1 — The pipeline shape.** Extraction → analysis/resolution → ComputationGraph →
  generation, plus the snapshot path (`generate --from-snapshot`, now format v5) as a
  first-class alternative front end. One interactive diagram is the spine of the page;
  everything deeper hangs off it. Every graph module carries a `module_kind`
  (`resolution/models.py`, doc 09) — colour the diagram nodes by it: `CALCULATION`,
  `FORMULA`, `AGGREGATION` are the three calc families; `CONSTRAINT` and
  `REPORT_AGGREGATOR` are the two families CONSTRAINT-EXEC added (a lowered assertion and
  the run-report roll-up), present only when the model carries constraints.
- **L2 — Each stage's tight responsibility** (see the responsibility table below) with
  its inputs/outputs and the invariant it owns.
- **L3 — Mechanisms.** The algorithms: virtual CalcUsage instantiation, computed-
  attribute classification, the registry's phased build, the backtracker's dispatch
  ladders, the unified producer-resolution table (`resolve_producer`,
  `resolution/producer_resolution.py`, doc 04) that replaced the three drifted resolver
  ladders, V11's fell-through∩valueless∩wired set logic, alias surfacing, and the
  constraint-execution path — **lowering** a modeled assertion to a concrete constraint
  (`analysis/constraint_lowering.py`, doc 28), assembling the **catalog** embedded on the
  graph (`generation/constraint_catalog.py`), and **compiling each predicate** to Python
  under three-valued Kleene semantics (`generation/predicate_compiler.py`) — an Act-3
  hard part in its own right (a non-finite leaf makes the predicate `unknown`, not
  `False`).
- **L4 — SysML v2 primitives and the parsed AST.** This layer is REQUIRED content:
  show real SysML snippets side-by-side with the AST node kinds the code dispatches on —
  `FeatureChainExpression` (dotted paths), `OperatorExpression`,
  `FeatureReferenceExpression`, literal nodes (`LiteralRational` etc.),
  `FeatureTyping` (a usage's declared type — read from the owned relationship, never a
  type-list position, which is order-unstable), `ReferenceUsage` vs `AttributeUsage`
  members (why bare `:>> attr = value` is captured but
  `attribute :>> attr = <expression>` is silently dropped — a real, documented trap),
  and redefinition (`:>>`) as the load-bearing SysML idiom. The FCE-before-OE dispatch
  ordering invariant (doc 19) belongs here.

Use progressive disclosure mechanics (collapsed sections, click-to-expand nodes on the
diagram, tabbed depth within a mechanism). Wrong approach: a wall of prose with
headings. Right approach: L0/L1 readable in two minutes; L3/L4 reachable in two clicks.

**Forward links are part of the method.** When a concept surfaces before its full
treatment, say so with an in-page anchor link — "resolved per instance
(→ [Scoped aliases](#scoped-aliases))" — so the reader knows depth is coming and can
jump or keep reading. Every mechanism named at L1/L2 links forward to its L3/L4
section; every L3/L4 section links back up to where it sits in the pipeline diagram.
A reader should never wonder "will this be explained?" — the link answers it.

## Required content

**1. Responsibility map.** One section that pairs every module/mechanism with a
one-sentence responsibility and the challenge that forced it to exist. Work from this
skeleton (verify names against the docs; each has a scrubbed reference doc):

| Owner | Tight responsibility | The challenge it answers |
|---|---|---|
| `extraction/extractor.py` (doc 01) | Pull calc defs/usages with typed I/O out of the AST | SysML lets one output be spelled 4 ways (`out attribute`, `return x`, bare `in`); anonymous `return` is unbuildable → V8 |
| `extraction/usage_extractor.py` (doc 25/12) | Templates → per-instance virtual CalcUsages | A calc inside a part def is a stencil, not an instance; retyping (`part :>> x : Subtype`) must index under every carried user type |
| `extraction/hierarchy_resolver.py` (doc 25) | Capture the design hierarchy + `:>>` overrides | Values live scattered across usage overrides / specialized defs / base defs |
| `extraction/computed_attribute_extractor.py` (doc 16) | Classify design-attribute expressions (FORMULA / EXPOSE_PURE / EXPOSE_COMPUTED-rejected / tentative / literal / unresolvable) | An attribute expression can be an algorithm, an alias, or a config value — each takes a different pipeline path |
| `core/output_registry.py` + `orchestration/output_registry_builder.py` (doc 10) | One authoritative name→channel registry, typed keys, phased build incl. the Phase 3b multi-hop confirm walk | Ambiguous string keys caused silent mis-wires; a multi-hop chain can't be classified at extraction (leaf lacks the registry) |
| `analysis/dependency_backtracker.py` (docs 11/24) | Resolve every binding to exactly one source via typed dispatch ladders (CHAIN vs REFERENCE) | Quoted names, def-owned attributes, sibling instances of one type, cross-part chains |
| `resolution/producer_resolution.py` (doc 04) + `resolution/producer_completeness.py` | One registry-owned ordered resolution table (`resolve_producer`, `KEY_FORMS`) serving calc / aggregation / constraint consumers alike — strict-vs-lenient behavior forks only at the terminal miss (`TerminalPolicy`); a separate completeness check (`check_producer_completeness`) proves every model-derived consumed value has a real producer, independent of V11 | Three drifted resolver ladders let the same meaning resolve three ways; a passing component test could still mis-resolve a supported combination — lifecycle Item 2 collapsed them to one authority and deleted `input_resolver.py` (`resolve_input`/`AGG_STRATEGIES`) |
| `resolution/supplied_values.py` (REQ-SVM; PIPELINE-TRUTH Item 2) | Pre-pass that materializes design attributes for cross-part/in-part supplied values, keyed by source QN, before the backtracker | A literal on a subsystem attribute must fill a plant-calc input, or generation aborts at V11 — the whole-plant idiom fusion-tea uses; fan-out collapses to one shared EP per source QN |
| `orchestration/pipeline_builder.py` (docs 02/12) | Ordered assembly: rewrite virtual bindings through the specialization chain (usage override > specialized-def `:>>` > base def), then backtrack, then derive groups | Step order IS the correctness argument (e.g. group deriver runs after the registry confirm pass) |
| `resolution/graph_builder.py` (doc 07) | Emit the `ComputationGraph` — sole input to generation — and gate it (V11 params-coverage, channel validation) | A generated pipeline that `KeyError`s at load is worse than a loud abort |
| `analysis/` param-group deriver (doc 17) | Entry points → per-design-file JSON input groups | Which literals are user-facing knobs (ADR-001: LIBRARY_DEFAULT / DESIGN_ATTRIBUTE / USAGE_LITERAL) |
| `generation/` (docs 08/20/21/22/23) | Render graph → wrappers, stencils, schemas, YAML; alias filename overrides; smart-regen preserves handwritten impls | Generated code people edit must survive regeneration |
| `snapshot/` (doc 27) | Versioned extraction capture (now **v5**: v3 added `constraint_facts`/`part_occurrences`/`constraint_lowering_mode` so the offline path re-lowers constraints; v4 added the diagnostic-severity field; v5 replaced the snapshot-relative `source_file` with a portable `root-N/<relpath>` referent for whole-tree portability); an old snapshot is a hard error, and regeneration from a current one is byte-identical to live | Generation, debugging, and CI shouldn't require the live parser toolchain on every run |
| `analysis/constraint_lowering.py` (doc 28) | Lower each eligible modeled assertion to a concrete constraint (strict formal resolution per owner-instance); default-on | A modeled `assert` used to be *dropped*; it now executes, so the value it checks must be resolved like any calc input |
| `resolution/models.py` `ModuleKind` (doc 09) | Tag every module with one of five families (`CALCULATION`/`FORMULA`/`AGGREGATION`/`CONSTRAINT`/`REPORT_AGGREGATOR`) | Two accreted bool flags could not name the constraint and report-roll-up families; one enum set once, dispatched on at every generation seam |
| `generation/constraint_catalog.py` + `ConstraintCatalog` on the graph (docs 28/09) | Assemble one fingerprinted catalog (source records + concrete entries), embedded on the `ComputationGraph`, read only from the graph at generation | Generation must read constraint data from the single-source-of-truth graph, never from mutable context |
| `generation/predicate_compiler.py` (doc 28) | Compile each predicate's `ExpressionIR` to Python under three-valued (Kleene) semantics; one shared predicates module compiled once | A non-finite leaf must make a predicate `unknown`, not silently `False` — a lying gate is worse than a loud one |
| `generation/` constraint + report-aggregator render seams (doc 08) | Render `CONSTRAINT` / `REPORT_AGGREGATOR` modules; a seam with no rendering for a kind fails loud (`unrenderable_module_kind_error`) | Every module_kind must render or refuse — never be mis-rendered as a calculation |
| `contracts/` (docs 29) | Emit the package's semantic `ModelContract` (graph-only) + physical `PackageContract` seal + a verbatim verifier + a generation manifest (`contracts/manifest.py`: `build_generation_manifest` tags codegen-produced / preserved-handwritten / runtime files, `check_reseal_provenance` refuses to launder foreign files into generated provenance); the `seal` CLI re-seals in place, and verification trust is runtime-owned so no untrusted package code runs before it is verified | A consumer must confirm it loads exactly the bytes generated, know what it may vary/observe without parsing YAML, and never execute a package that forged its own verifier |
| teax `simkit/study/` + `PreparedEvaluator.entry_models` (teax `docs/evaluation-and-study.md`) | The top-of-stack consumer: load a generated+sealed package, obtain typed entry models (`entry_models`, channel→typed-model), and drive many cases through an evaluator | The generated pipeline is a means; a study sweeping designs over it is the end the whole stack serves |

**2. Diagnostics as contract.** V1–V11 (modeling-assumptions.md "Validation Rules") are
the user-facing surface of every internal invariant — present them as "what the modeler
sees when an assumption breaks", noting V1–V10 fire at extraction and V11 at the
generation boundary. Extend the same frame to the diagnostic-severity contract and the two
CONSTRAINT-EXEC surfaces:

- **Extraction-diagnostic severity** (doc 30) is the contract on *which* diagnostics halt.
  Each extraction diagnostic carries a versioned severity (`DiagnosticSeverity`:
  `BLOCKING` / `ADVISORY`), set by the writer at construction from a closed table — never a
  reader-side lookup — and screened at one sink (`screen_extraction_diagnostics`). Advisory
  rendering can never mask a later `BLOCK` (order is enforced), and a severity/version skew
  fails closed in both directions (version gate → per-diagnostic severity cross-check →
  unknown-kind refusal). Present it as "how the pipeline decides a broken assumption is fatal,
  not merely noise."
- **The executable profile** classifies each constraint usage ADMIT / BLOCK / unassessed
  (in agentic-mbse); a BLOCK-eligible usage halts generation loudly, naming every
  diagnostic. This is a contract on which assertions may execute, and why one cannot.
- **Package contracts / sealing** (doc 29) are the *load-time* contract: the emitted
  `verify.py` re-hashes the package against its `PackageContract` and reports
  `TAMPER` / `MISSING` / `EXTRA` / name-mismatch (always fatal) and an env-compat mismatch
  (advisory unless strict). A `ModelContract` fingerprint is the package's semantic
  identity. Present sealing as "how a consumer knows it loaded exactly what was generated."

**3. A worked example.** Trace one real value end-to-end using committed fixtures
(`tests/fixtures/solar_battery_model/` + `tests/fixtures/baseline_yaml/solar_battery.yaml`,
or `wi014_toy` for the part-def EXPOSE shape). SysML source line → AST nodes → extracted
data → registry entries → resolved binding → graph module → YAML exit line. Real names
from the baselines, not invented ones.

**4. The cross-part story (the epic's centerpiece).** Two complementary halves — channel
wiring and value resolution — cover the whole-plant idiom that fusion-tea uses.

*Channel wiring* (an output of one calc reaches another calc's input): multi-hop EXPOSE
(`EXPOSE_CHAIN_TENTATIVE` → Phase 3b confirm), part-def EXPOSE expanded per instance
(shape A, `_scoped_alias` / `ScopedAliasKey`), specialized-def `:>>` chains (single- and
two-level — the `gamma → lcoe` shape), sibling disambiguation, and alias surfacing
(`ComputationGraph.output_aliases`, serialized, vs `fallback_entry_points`, in-memory —
a deliberate contrast; the modeler's name becomes the exit-point output filename
`{instance_path}__{alias_name}.json`).

*Value resolution* (a literal sitting on a subsystem attribute fills a plant-calc input —
the PIPELINE-TRUTH headline): the **supplied-value materializer**
(`resolution/supplied_values.py`, REQ-SVM-01..04). A pre-pass synthesizes design
attributes for cross-part and in-part supplied values, keyed by **source QN**, merged into
`design_attributes` before the backtracker runs. It covers the four value-provision shapes
Item 2 landed — (a) subtype-def literal through a usage-level retype, (b) a bare no-retype
`part :>>` override block, (c) a plain one-hop cross-part attribute with a dotted usage
override, (d) an in-part supplied value — with precedence **usage override >
specialized-def `:>>` > base def** (REQ-VBR-10). Fan-out collapses by source QN: one
attribute feeding three consumers is one shared entry point, not three keys. This is what
retired the V11 10-offender abort — fusion-tea's full YAML now emits with zero offenders.
One honest exception to shape (b): when the `part :>>` override sits on a usage nested inside
an *instantiated* part def, capture is definition-relative while demand is occurrence-relative
and the literal is lost (`[NESTED-OCCURRENCE-OVERRIDE]` — see §7). The flat and array
deep-path shapes capture correctly.

**5. Operational reality.** How you actually run it: `generate --models` (live
extraction) vs `snapshot` + `generate --from-snapshot` (mutually exclusive with
`--models`, rebuilds the same pipeline context from the captured JSON); baselines
regenerated via the capture scripts only, with reviewed diffs; the format-version hard
error and stale-source-hash warning. Skip licensing details entirely — they are not
this explainer's topic.

**6. agentic-mbse, the complement.** A dedicated section: sysml-codegen defines the
executable subset; agentic-mbse *teaches* it (MODELING_GUIDE, the sysml-conventions
skill stencils) and *checks* it (leveled validation checks with negative fixtures —
e.g. self-named-binding FAIL, constraint-drop WARN, calc-bearing-def-never-instantiated
FAIL). Every epic item recorded matching agentic-mbse updates so teaching and checking
never drift from what codegen accepts. Frame it as the enforcement half of the
modeling-assumptions contract.

**7. Honest caveats — preserve, never strengthen.** These are the limits that are still
real at merged main. State them exactly as hedged; do not present them as
solved, and do not resurrect the pre-epic caveats the three epics retired (see the note below).

- **`attribute :>> attr = <expression>` is silently dropped at extraction** — use the bare
  `:>> attr = value` form. agentic-mbse WARNs on the expression form, but codegen extraction
  still drops it. Genuinely unsupported.
- **EXPOSE_COMPUTED is rejected** and does not surface.
- **A `:>>` override on a usage nested inside an *instantiated* part def is captured
  definition-relative while demand resolves occurrence-relative, so the supplied-value
  materializer never matches and the literal is lost** (`[NESTED-OCCURRENCE-OVERRIDE]`,
  BACKLOG P2; probe `tests/fixtures/nested_occurrence_override_probe/`). It drops on *both*
  the calc path (silent manual-required) and the constraint path (halt under strict INV-2).
  Genuinely unsupported at merged main — surfaced by the lifecycle epic's case-18, filed, not
  fixed. Use the flat/array deep-path shapes, which do capture.
- **The constraint catalog is embedded on the graph as the sole schema authority, not emitted
  standalone.** This is the ratified design (owner decision D-3): TEAx consumes the embedded
  `ModelContract` catalog directly, so a standalone `constraint_catalog.json` export (CE-F1)
  is explicitly out of scope — any future export must be mechanically identical to the
  embedded schema. Describe the embedded catalog as the authority, not as a temporary state
  pending CE-F1. (The multi-channel bridge, formerly CE-F2, *landed* — see §4/§9.)

**Retired by PIPELINE-TRUTH, CONSTRAINT-EXEC, and CONSTRAINT-LIFECYCLE — do NOT present these
as open caveats** (they were true earlier; they are not now):

- **"Constraints are dropped / no execution path"** — RETIRED by CONSTRAINT-EXEC. Modeled
  assertions now lower and execute under Kleene semantics (§8). Do not present constraints as
  drop-only; do not claim the `collect_constraint_manifest` collector was removed (it
  survives — only the report/render/serialize surface was retired).
- **"`resolve_input()` / `AGG_STRATEGIES` is a separate aggregation ladder"** — RETIRED and
  DELETED. CONSTRAINT-LIFECYCLE Item 2 unified the three drifted resolver ladders into one
  registry-owned ordered table: `resolve_producer` (`resolution/producer_resolution.py`)
  serves calc, aggregation, and constraint consumers alike, and `input_resolver.py` — with
  `resolve_input` / `AGG_STRATEGIES` / `DesignAttributeLookup` — was deleted. Do not describe
  any path as calling `resolve_input(AGG_STRATEGIES)`; that symbol no longer exists. (The F4
  cutover that first wired the aggregation path is now subsumed by this unification.)
- **"The candidate bridge is single-channel"** — RETIRED. CONSTRAINT-LIFECYCLE Item 9 landed
  the stock multi-entry TEAx bridge (formerly filed as CE-F2): it builds complete typed
  mappings for zero, one, or many generated entry channels with no consumer wrapper.
- **"Snapshots are format v1/v2/v3"** — RETIRED. The format is v5 (v4 added the
  diagnostic-severity field, v5 the portable whole-tree referent); there is no coexistence —
  an old snapshot is a hard error and is re-captured at v5.
- The V11 10-offender abort (fusion-tea's full YAML emits at zero offenders via the
  supplied-value materializer — PIPELINE-TRUTH Item 2/3); the assert-constraint silence
  (fixed subtype-aware — Item 4); the "four specific cross-part shapes" limit (now four
  wiring shapes + SVM value-fill a/b/c/d — Item 2); the two "open" REQ-vs-code divergences
  (DOCS-SCRUB-F2/F4, retired by Item 7); and the run-C anchor being "recorded not reproduced"
  (it reproduces bit-exactly — SC-B).

**8. The constraint-execution path (the CONSTRAINT-EXEC centerpiece).** The second
epic-scale story, parallel to the cross-part story in §4. Trace a modeled assertion from
source to execution:

- A modeler writes `assert constraint { ... }` (an `AssertConstraintUsage`). Pre-epic it
  was **dropped** — reported loudly, but never executed. It now **lowers**.
- **Lowering** ([P1 RESOLVE], `analysis/constraint_lowering.py`, doc 28): the executable
  profile admits the usage; every formal is strictly resolved to a real value per
  owner-instance through the same unified producer-resolution table calc inputs use
  (`resolve_producer`, `resolution/producer_resolution.py`) — constraints take the strict
  `TerminalPolicy` fork, so an unresolved formal fails contextually rather than inventing a
  value; an admitted usage becomes a concrete constraint.
- **Catalog** (`generation/constraint_catalog.py`): the concrete constraints plus their
  source records assemble into one fingerprinted `ConstraintCatalog`, embedded on the
  `ComputationGraph` (doc 09) — generation reads it only from the graph.
- **Predicate compilation** (`generation/predicate_compiler.py`): each predicate's
  `ExpressionIR` compiles to Python under **three-valued (Kleene)** semantics — a
  non-finite leaf yields `unknown`, never a silent `False`. Show this as an Act-3 hard
  part with a real predicate and its compiled body.
- **Modules**: the graph gains `CONSTRAINT` modules (one per concrete constraint, sharing
  one compiled predicate) and a `REPORT_AGGREGATOR` module (the run-report roll-up), both
  new `module_kind` families rendered at their own generation seams (doc 08).
- **Sealing** (doc 29): the generated package is sealed and carries a verifier, so its
  constraint semantics travel with a checkable fingerprint.

Keep the inherited history straight: `lower_constraints_enabled` is landed history
(default-on, its GRANDFATHERED carve-out now empty), **not** a live drop path — and
CONSTRAINT-LIFECYCLE Item 12 made a `grandfathered_off` snapshot fail closed on the product
path, so it cannot silently drop constraints; the `collect_constraint_manifest` collector
**survives** (a kept migration-mapping test needs it — only the report/render/serialize
surface was retired); the multi-channel bridge (formerly CE-F2) **landed** (Item 9 — the
stock multi-entry TEAx bridge); and CE-F1 (standalone `constraint_catalog.json` emission) is
**out of scope by design**, not a pending follow-on — the embedded catalog is the sole schema
authority (owner decision D-3), and any future export must be mechanically identical to it.

**9. The teax study layer (top of the stack).** Close the loop: the generated, sealed
package is not the end — it is what a **study** drives. teax
(`docs/evaluation-and-study.md`) loads a package (verifying its seal), obtains typed entry
models via `PreparedEvaluator.entry_models` (a channel → typed-model map derived from the
pipeline spec), and sweeps many designs through an evaluator. Frame sysml-codegen as the
means and the study as the end the whole four-repo stack serves.

## Reading list (in order; re-verified at CONSTRAINT-LIFECYCLE close / docs-lifecycle-sync sweep)

1. `docs/architecture/modeling-assumptions.md` — the contract; read end-to-end first
2. `docs/architecture/overview.md` + `reference/00-pipeline-overview.md` — shape + reading guide
3. `.project/active/docs-scrub/fact-sheet.md` — condensed "true at HEAD" facts F1–F12 with
   provenance; read its **F6/F10 POST-EPIC UPDATE** for what PIPELINE-TRUTH changed
4. Reference docs per the responsibility table above (01, 25, 12, 16, 10, 11, **04** for the
   unified producer-resolution ladder, 24, 02, 07, 17, 08, 20, 21, 27; 19 for the AST
   invariant; **09** for `ModuleKind` + `ConstraintCatalog`; **28** for constraint lowering /
   catalog / predicate compiler; **29** for contracts / sealing; **30** for the extraction-
   diagnostic severity contract)
5. `docs/architecture/verification-matrix.md` — skim; the REQ counts and families
   (**276 = 275 PASS + 1 UNTESTED, 32 families** — the `CON` family is contracts/sealing; the
   portability rows REQ-SNAP-21/22 were added in place, no new family) if you cite coverage.
   Recount from the family index, never the summary block.
6. **Constraint-execution data sources** (the concrete pins for §8 and the constraints/sealing
   rows): the two contract test files `tests/unit/test_contract_models.py` (graph-only build,
   deterministic fingerprints, zero-constraint seal, stable bytes) and
   `tests/conformance/test_seal_step9.py` (three emitted files, verbatim verifier,
   seal-excludes-itself, re-seal, `seal` subcommand); plus `analysis/constraint_lowering.py`
   and `generation/predicate_compiler.py` for the lowering and Kleene mechanisms.
7. `.project/completed/20260720_epic_constraint_execution_lifecycle_remediation.md` — the
   newest epic and the authority for everything the lifecycle remediation changed (resolver
   unification, severity/defaults, whole-tree portability, package trust, catalog store,
   multi-entry bridge, producer completeness, legacy/tracking closure — 14 items, composed
   41/41 proof, Lessons Learned) +
   `.project/completed/20260713_epic_constraint_execution.md` — the CONSTRAINT-EXEC epic
   (constraint lowering, catalog, predicate compiler, contracts/sealing, snapshot v3 — the
   version state *before* v4/v5) + `.project/research/20260706_pipeline-truth-discovery.md`
   — the PIPELINE-TRUTH discovery register (D1–D7 + adversarial); the evidence base for the
   earlier epic's mechanisms
8. `.project/completed/20260720_epic_pipeline_truth.md` — the PIPELINE-TRUTH epic (goals,
   per-item scope, Lessons Learned) + `.project/completed/20260720_epic_upstream_findings.md`
   (prior epic)
9. `.project/active/{warning-reconciliation,cross-part-wiring,alias-surfacing,plant-prefill}/release-notes.md`
   (UPSTREAM-FINDINGS mechanisms) + the PIPELINE-TRUTH item close-outs
   (`.project/active/{whole-plant-resolution,fusiontea-acceptance,subtype-enumeration,silent-failure-hardening}/`)
   — the why behind the newest mechanisms (SVM, subtype-aware enumeration, silent-failure hardening)

Prior art (reuse-guidance delta): `.project/diagrams/new_pipeline_explainer.html` (268KB, the
Gen-1 build) and its design at `.project/active/new-pipeline-explainer/design.md`. The Gen-1
HTML now carries a deprecation banner — it predates the UPSTREAM-FINDINGS / PIPELINE-TRUTH,
CONSTRAINT-EXEC, **and** CONSTRAINT-LIFECYCLE epics, so treat its *content* as stale against
merged main. The split is roughly: its **rendering machinery + 4-act frame are ~70–80%
reusable** (viewBox zoom/pan controller, tier-slot DAG layout, narrative callouts,
progressive disclosure — lift these), while its **content/data layer is largely a rewrite**
(it knows nothing of the supplied-value materializer, the unified `resolve_producer` ladder,
constraint lowering, `module_kind`, Kleene predicates, the catalog, contracts/sealing, the
generation manifest / trusted bootstrap, the diagnostic-severity contract, the multi-entry
bridge, snapshot v5, or the teax study layer). Do not
retrofit it node-for-node; this explainer's scope (SysML/AST layer, responsibility map,
constraint execution, operations, agentic-mbse, teax study layer) is larger.

## Technical constraints

- One self-contained HTML file: vanilla HTML + inline SVG + vanilla JS, zero external
  requests (no CDNs, no webfonts). Light/dark theme aware.
- Ground every symbol you name with a grep against `src/` before citing it; use
  file + symbol anchors, never `file.py:NNN` line numbers (they rot — repo convention).
- **SysML v2 code blocks are a first-class element, not decoration.** Every pattern the
  explainer discusses gets a small, well-formed, syntax-highlighted SysML snippet at the
  point of discussion: the calc-def output styles (`out attribute` / `return x : Real =`
  / bare `in`), both EXPOSE shapes, a multi-hop chain, retyping
  (`part :>> driver : 'HIF Driver'`), the `:>>` value/CHAIN/deep-path forms (and the
  unsupported `attribute :>>` counter-example, clearly marked as the trap), and an
  aggregation redefinition. Snippets must be real (from `tests/fixtures/`) or minimally
  adapted from real fixtures; label which fixture each comes from. Pair the L4 snippets
  with their AST node breakdown. Use the `sysml-conventions` skill (and the
  `sysml-expert` agent if unsure) to keep every snippet canonically correct — a syntax
  error in an explainer teaching syntax is disqualifying.
- Save to `.project/diagrams/pipeline_explainer_v2.html` (do not overwrite the prior
  explainer). Docs-only working tree: no code/test/fixture edits.
- Before writing the page, load the `artifact-design` and `dataviz` skills if you will
  render it as an Artifact; the same design bar applies to a raw HTML file.

## Done means

A newcomer gets the L0/L1 story in two minutes; an engineer can drill from any diagram
node to the mechanism and the SysML/AST primitives underneath it in two clicks; every
claim traces to a scrubbed doc or a grep-verified symbol; the caveats read exactly as
hedged as the docs hedge them; and the agentic-mbse section makes clear why the
pipeline can assume the patterns it assumes.
