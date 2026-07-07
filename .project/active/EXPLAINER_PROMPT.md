# Prompt: Interactive Pipeline Explainer (post-PIPELINE-TRUTH)

Copy everything below the line into a fresh agent session in
`/home/reid/1cfe/sysml-codegen`, on branch `pipeline-truth-epic` (or `main` once that
branch merges). The docs-scrub pass merged to `main` as PR #4; the PIPELINE-TRUTH epic
then landed on `pipeline-truth-epic` and re-verified every doc it touched at that HEAD.

---

Build a single self-contained interactive HTML explainer of the **sysml-codegen
pipeline** — what it is for, how it works algorithmically, and how it is operated —
current as of `pipeline-truth-epic` HEAD (the post-epic docs there were scrubbed, then
re-verified at epic close against code at HEAD; trust them and cite them rather than
re-deriving). The facts below are certified true by the GREEN Item-3 fusion-tea
acceptance run — full package generates at zero V11 offenders and run-C's lcoe
reproduces bit-exactly ($270.1211779380445/MWh) through the generated package alone.

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
  generation, plus the snapshot path (`generate --from-snapshot`) as a first-class
  alternative front end. One interactive diagram is the spine of the page; everything
  deeper hangs off it.
- **L2 — Each stage's tight responsibility** (see the responsibility table below) with
  its inputs/outputs and the invariant it owns.
- **L3 — Mechanisms.** The algorithms: virtual CalcUsage instantiation, computed-
  attribute classification, the registry's phased build, the backtracker's dispatch
  ladders, V11's fell-through∩valueless∩wired set logic, alias surfacing.
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
| `resolution/supplied_values.py` (REQ-SVM; PIPELINE-TRUTH Item 2) | Pre-pass that materializes design attributes for cross-part/in-part supplied values, keyed by source QN, before the backtracker | A literal on a subsystem attribute must fill a plant-calc input, or generation aborts at V11 — the whole-plant idiom fusion-tea uses; fan-out collapses to one shared EP per source QN |
| `orchestration/pipeline_builder.py` (docs 02/12) | Ordered assembly: rewrite virtual bindings through the specialization chain (usage override > specialized-def `:>>` > base def), then backtrack, then derive groups | Step order IS the correctness argument (e.g. group deriver runs after the registry confirm pass) |
| `resolution/graph_builder.py` (doc 07) | Emit the `ComputationGraph` — sole input to generation — and gate it (V11 params-coverage, channel validation) | A generated pipeline that `KeyError`s at load is worse than a loud abort |
| `analysis/` param-group deriver (doc 17) | Entry points → per-design-file JSON input groups | Which literals are user-facing knobs (ADR-001: LIBRARY_DEFAULT / DESIGN_ATTRIBUTE / USAGE_LITERAL) |
| `generation/` (docs 08/20/21/22/23) | Render graph → wrappers, stencils, schemas, YAML; alias filename overrides; smart-regen preserves handwritten impls | Generated code people edit must survive regeneration |
| `snapshot/` (doc 27) | Versioned extraction capture; regeneration from it is byte-identical to live | Generation, debugging, and CI shouldn't require the live parser toolchain on every run |

**2. Diagnostics as contract.** V1–V11 (modeling-assumptions.md "Validation Rules") are
the user-facing surface of every internal invariant — present them as "what the modeler
sees when an assumption breaks", noting V1–V10 fire at extraction and V11 at the
generation boundary.

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
real at post-PIPELINE-TRUTH HEAD. State them exactly as hedged; do not present them as
solved, and do not resurrect the pre-epic caveats the epic retired (see the note below).

- **Constraints are dropped** — but loudly, subtype-aware, and on both paths (§8). The drop
  report sweeps every `ConstraintUsage` including subtypes, so an `assert constraint`
  (`AssertConstraintUsage`) is reported, not silent; it runs on the live and
  `generate --from-snapshot` paths (REQ-EXT-09, Item 4). There is still no execution path
  for constraints — encode a gate as a calc-def output if you need one enforced.
- **`attribute :>> attr = <expression>` is silently dropped at extraction** — use the bare
  `:>> attr = value` form. agentic-mbse now WARNs on the expression form (Item 9), but
  codegen extraction still drops it. Genuinely unsupported.
- **EXPOSE_COMPUTED is rejected** and does not surface.
- **`resolve_input()` / `AGG_STRATEGIES` is built and parity-validated but not yet wired**
  to the live aggregation path — the live path is `_resolve_aggregation_input_channel`. This
  is the honest current state (docs 03/04/05 + matrix say so), the rewire is filed as
  `[ITEM7-F4-CUTOVER]`, and the two implementations are proven equivalent on the committed
  corpus by `test_dual_resolution.py`. It is a not-yet-wired consolidation, **not** an
  unreconciled REQ-vs-code divergence.

**Retired by PIPELINE-TRUTH — do NOT present these as open caveats** (they were true
pre-epic; they are not now): the V11 10-offender abort (fusion-tea's full YAML now emits at
zero offenders via the supplied-value materializer — Item 2/3; workarounds deleted
upstream — SC-C); the assert-constraint silence (fixed subtype-aware — Item 4); the
"four specific cross-part shapes" limit (support is now broader: four wiring shapes + SVM
value-fill a/b/c/d — Item 2); the two "open" REQ-vs-code divergences (DOCS-SCRUB-F2
resolved fix-text-to-code, DOCS-SCRUB-F4 resolved land-with-split — both retired by Item 7);
and the run-C anchor being "recorded not reproduced" (it now reproduces bit-exactly in the
acceptance run — SC-B).

## Reading list (in order; scrubbed 2026-07-06, then re-verified at PIPELINE-TRUTH close)

1. `docs/architecture/modeling-assumptions.md` — the contract; read end-to-end first
2. `docs/architecture/overview.md` + `reference/00-pipeline-overview.md` — shape + reading guide
3. `.project/active/docs-scrub/fact-sheet.md` — condensed "true at HEAD" facts F1–F12 with
   provenance; read its **F6/F10 POST-EPIC UPDATE** for what PIPELINE-TRUTH changed
4. Reference docs per the responsibility table above (01, 25, 12, 16, 10, 11, 24, 02, 07, 17, 08, 20, 21, 27; 19 for the AST invariant)
5. `docs/architecture/verification-matrix.md` — skim; the REQ counts and families
   (253 = 249 PASS + 4 UNTESTED, 30 families) if you cite coverage. Recount from the
   family index, never the summary block.
6. `.project/research/20260706_pipeline-truth-discovery.md` — the PIPELINE-TRUTH discovery
   register (D1–D7 + adversarial); the evidence base for the epic's mechanisms
7. `.project/backlog/epic_pipeline_truth.md` — the PIPELINE-TRUTH epic (goals, per-item
   scope, Lessons Learned) + `.project/backlog/epic_upstream_findings.md` (prior epic)
8. `.project/active/{warning-reconciliation,cross-part-wiring,alias-surfacing,plant-prefill}/release-notes.md`
   (UPSTREAM-FINDINGS mechanisms) + the PIPELINE-TRUTH item close-outs
   (`.project/active/{whole-plant-resolution,fusiontea-acceptance,subtype-enumeration,silent-failure-hardening}/`)
   — the why behind the newest mechanisms (SVM, subtype-aware enumeration, silent-failure hardening)

Prior art: `.project/diagrams/new_pipeline_explainer.html` (268KB) and its design at
`.project/active/new-pipeline-explainer/design.md`. Reuse its proven machinery if
useful (viewBox zoom/pan controller, tier-slot DAG layout, narrative callouts,
progressive disclosure) but treat its *content* as unverified against HEAD — parts
predate the UPSTREAM-FINDINGS and PIPELINE-TRUTH epics. Do not just retrofit it; this
explainer's scope (SysML/AST layer, responsibility map, operations, agentic-mbse) is larger.

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
