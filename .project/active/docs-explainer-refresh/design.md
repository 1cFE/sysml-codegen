# Design: Docs + Explainer-Brief Refresh (post-CONSTRAINT-EXEC)

**Status:** Complete (implemented 2026-07-13)
**Owner:** Reid W
**Created:** 2026-07-13
**Branch:** constraint-exec-epic (sysml-codegen home; touches agentic-mbse, teax, fusion-tea)
**Commit:** 556e391

## Overview

Re-project the surveyed teaching surfaces onto code-at-HEAD so every touched surface tells
one story, and re-anchor `EXPLAINER_PROMPT.md` into a truthful, buildable v2 brief. A
targeted survey-driven sweep across four repos — not a docs scrub.

## Related Artifacts

- **Spec:** `.project/active/docs-explainer-refresh/spec.md` (revised post-review 2026-07-13)
- **Spec review + resolutions:** `.project/active/docs-explainer-refresh/spec-review.md`
- **Primary evidence:** `.project/active/docs-explainer-refresh/staleness-survey.md` (verified at HEAD twice)
- **Explainer prior art:** `.project/active/EXPLAINER_PROMPT.md` (Gen-2 brief, stale),
  `.project/active/new-pipeline-explainer/`, `.project/diagrams/new_pipeline_explainer.html` (Gen-1 built)
- **Epic (archived):** `.project/completed/20260713_epic_constraint_execution.md`

## Research Findings

Verified in this session (sysml-codegen HEAD):

- `ModuleKind` has five values — `CALCULATION`/`FORMULA`/`AGGREGATION`/`CONSTRAINT`/`REPORT_AGGREGATOR`
  (`resolution/models.py:161-170`); `PipelineModule.module_kind` is required, replacing the two
  retired bool flags (`resolution/models.py:193`); `ComputationGraph` carries `constraint_catalog`
  (confirmed via `tests/unit/test_contract_models.py:79-84`).
- `08-generation.md`, `09-data-models.md`, `00-pipeline-overview.md` have **zero** hits for
  `ModuleKind`/`module_kind`/`constraint_catalog`/`report_aggregator`. Gap confirmed.
- Contract/seal machinery is real and tested but undocumented: `test_contract_models.py`
  (7 test functions, 8 collected — one 2-way parametrize: graph-only build, deterministic
  semantic+executable fingerprints, zero-constraint seal, stable on-disk bytes, glob-matcher drift
  guard) and `test_seal_step9.py` (5 tests: three emitted files, verbatim verifier,
  seal-excludes-itself, re-seal recomputes only PackageContract, `seal` subcommand). Neither file is cited in the verification matrix; neither carries
  `@pytest.mark.req` marks (unlike SNAP rows) — the matrix anchors rows via the Test File column,
  so req-marks are not a prerequisite.
- Matrix summary: 264 reqs / 31 families / 71 test files (`verification-matrix.md:9-14`); Index at
  `:34-64`; CL family at `:156-171` (5 rows, "partial register" note). `overview.md:218` says "29
  requirement families" — stale against the matrix's 31 (this item pushes it to 32; see INV-4).
- Retired-symbol rows confirmed: REQ-AST-06 (`:96`) and REQ-CA-02 (`:144`) both name
  `build_expression_ast()`/`compile_expression()`, which are gone from `src/` (IR is now
  `ExpressionIR`; only `compile_calc_def`/`classify_compilability` remain). REQ-SNAP-09 (`:506`)
  narrates V1/V2.
- Doc 28 (`28-constraint-lowering-and-catalog.md`) is tightly about the constraint-execution path
  (Items 5-9, 14); its only contracts content is a "Contracts (seam disposition)" stub pointing at
  a run report (`:76-80`).

**Sandbox boundary:** this session can only read sysml-codegen. Cross-repo reads (agentic-mbse,
teax, fusion-tea) are blocked. The three cross-repo deliverables (SC-4/5/7) are designed from the
survey's file:line cites, which the orchestrator re-verified at those repos' HEADs (spec-review
Resolutions, L1-2). The implementer must re-grep each cite in-repo before editing.

## Core Concept

The system-of-record is the **code at HEAD**; the docs are a projection of it that drifted when
CONSTRAINT-EXEC changed the system but Item 14 flipped only the minimum surface. This item
re-projects the surveyed surfaces onto HEAD. There is **no new mechanism** — the design is a
*routing decision*, applied once per surveyed finding:

1. **What is the correct claim at HEAD?** (Answered already: the survey + spec supply it; do not
   re-derive.)
2. **Which surface owns that claim?** (Existing doc/row, or a new home.)
3. **In place or new home?** Corrections go in place; machinery with zero coverage gets a new
   section or doc.

The four delegated calls are exactly the "new home vs existing home" routing questions the survey
left open. Everything else is a mechanical correction against verified cites. The explainer brief
is the same routing applied to a generation brief: retire the stale caveats, slot the eight
constraint-exec artifact areas into the existing structure, re-anchor to current HEAD.

The concept composes with existing pieces, routing each concern to the surface that already owns
its kind: reference docs are one-concept-per-file (so contracts/sealing earns its own doc, not a
bolt-on to constraint-lowering); the verification matrix is families-of-REQ-rows anchored to test
files (so contracts earns a family); `overview.md` is the doc index and count-of-record (so it
tracks the matrix). The single-story bar is the acceptance test for every routing choice: after
the edit, a reader opening *that* surface must not be able to reach a claim HEAD contradicts.

## Key Bets

- **B1.** The survey is complete for the in-scope surfaces — the inventoried stale claims plus the
  named gap areas are the whole of what contradicts HEAD among *targeted* surfaces. *If false → a
  stale claim outside the inventory survives.* Failure is bounded: a full verify-every-doc scrub is
  an explicit Non-Goal with its own item shape, so an un-surveyed stale doc is out of contract, not
  a defect of this item.
- **B2.** The cross-repo survey cites are accurate at agentic-mbse / teax / fusion-tea HEADs. *If
  false → a cross-repo edit targets a wrong or already-fixed line.* Mitigation: the implementer
  re-greps each cite in-repo before editing (the cites are line-numbered and symbol-named); the
  orchestrator already re-verified them once at spec time.
- **B3.** `test_contract_models.py` and `test_seal_step9.py` pin the behaviors the new contracts
  reference doc will teach, so the CON matrix rows have real anchors. *If false → the CON family is
  UNTESTED placeholders.* Verified false-risk is low: both files exist and assert the fingerprint,
  seal-ordering, verbatim-verifier, and re-seal behaviors directly.

## Key Decisions

- **D1 — Verification-matrix shape: a new family `CON — Contracts & Sealing`.** Rows anchored to
  `test_contract_models.py` (unit) and `test_seal_step9.py` (conformance). *Rejected: extend CL.*
  CL is constraint lowering & catalog; sealing is orthogonal (a zero-constraint graph still seals —
  `test_zero_constraint_graph_seals`), lives in different test files, and the survey explicitly
  names contracts/sealing as a *missing family*, not a CL gap. Follow the CL precedent of a short
  register with an honest "partial coverage" note if the doc'd surface exceeds the pinned rows.
  Candidate rows (plan settles exact count/text): graph-only build (contract INV-1), deterministic
  semantic + executable fingerprints, zero-constraint seal, stable on-disk bytes, three emitted
  files + verify-on-load, verbatim emitted verifier (contract INV-8), seal-excludes-itself-from-
  coverage, re-seal recomputes only PackageContract, `seal` subcommand requires an existing
  ModelContract. (The `contract INV-*` labels are the contracts machinery's own numbering in
  `contracts/*.py` + the two test files — a **distinct namespace** from this design's Required
  Invariants INV-1..6, which is what SC-8 audits against.)

- **D2 — Contracts doc home: new `29-contracts-and-sealing.md`.** Covers `ModelContract` /
  `PackageContract` (`contracts/models.py`), `seal_package` (`contracts/seal.py:57`), verify-on-load
  (`contracts/verify.py`, `verify_package`), and the `seal` CLI subcommand (`cli/__init__.py:704`).
  *Rejected: absorb into 28.* Reference docs are one-concept-per-file; contracts/sealing is a
  package-integrity concern orthogonal to constraint lowering, coupled only by ModelContract
  embedding the catalog. Doc 28's "Contracts (seam disposition)" stub (`28:76-80`) becomes a
  forward pointer to 29. Register 29 (and 28, if still absent) in `overview.md`'s doc-list and
  component tables (`overview.md:148-192`).

- **D3 — agentic-mbse ConstraintFacts / ExpressionIR: a durable summary+pointer page, not a full
  architecture doc.** A real `docs/` page (agentic-mbse) that carries the core mental model for
  each — ConstraintFacts neutral schemas + extraction (Item 1), production `ExpressionIR` (Item 2):
  what it is, why it exists, the key types/modules — then points to the archived `.project/` design
  artifacts for full mechanism depth. *Rejected: full architecture doc.* Re-deriving both mechanisms
  in full is scrub-scale work out of proportion for a docs-refresh item, and the depth already
  exists in the archived artifacts. The bar (spec SC-4) is durability: the page must stand on its
  own for the mental model so it survives `.project/` archival — pointers may rot, the summary must
  not depend on them for the core story.

- **D4 — Gen-1 HTML: in-file deprecation banner + BACKLOG follow-on.** A small fixed banner at the
  top of `.project/diagrams/new_pipeline_explainer.html` ("Superseded — predates CONSTRAINT-EXEC /
  PIPELINE-TRUTH; see `EXPLAINER_PROMPT.md` for the current brief"), plus the BACKLOG item that
  registers the v2 HTML build pointing at the refreshed brief. *Rejected: BACKLOG-mention only.* A
  reader opening the HTML directly would get a two-epochs-stale story with no signal — the exact
  single-story failure this item exists to kill. The banner is a one-element top-of-`<body>` insert,
  not a content patch (patching the 268 KB content is a Non-Goal).

- **D5 — Retired-symbol matrix rows (REQ-AST-06, REQ-CA-02): reword in place, preserve the REQ
  IDs.** Update the requirement text to name the current symbols (the FCE-unsupported / FORMULA-
  compile behavior now lives on the `ExpressionIR` path: `compile_calc_def` /
  `classify_compilability`), matching corrected doc 14. *Rejected: re-anchor/rename to new IDs.*
  The behavior still exists — only the symbol name changed — and renaming breaks the stable
  ID↔test mapping and ripples through the matrix counts and any cross-references. Implementer
  confirms each reworded row still describes what its cited test pins.

## Architecture

The sweep is organized by repo. Home-repo work is directly editable this session; cross-repo work
is specified from verified survey cites for an implementer with those repos in reach.

**sysml-codegen (home) — corrections, gaps, new doc + family, explainer brief:**

- *Corrections (in place):* snapshot v3 + constraint-facts section + v2→v3 note
  (`27-snapshot-generation.md`, and REQ-SNAP-09 matrix text); `ExpressionIR` symbol set across
  `14-`, `16-`, `19-*.md` and matrix rows REQ-AST-06 / REQ-CA-02 (D5); `overview.md` family count
  (INV-4); REQ-PIPE-06 in `00-pipeline-overview.md`.
- *Gap-fills (new sections):* `ModuleKind` (all five values) into `09-data-models.md`
  (PipelineModule, replacing the bool-flag description; ComputationGraph gains `constraint_catalog`),
  `08-generation.md` (constraint + report-aggregator render seams), `00-pipeline-overview.md` +
  `overview.md` (lowering phase named in the step narrative).
- *New doc + family:* `29-contracts-and-sealing.md` (D2) and the `CON` matrix family (D1).
- *Explainer brief:* `EXPLAINER_PROMPT.md` re-anchored to current HEAD (content re-projection per
  the survey's eight-area slot map) **and** its buildability infrastructure refreshed (INV-6):
  responsibility-map rows + reading-list data sources for the eight areas (incl. docs 28/29 and the
  two contract test files), reuse-guidance delta, and the stale reading-list matrix counts corrected.
  Narrative slotting and infrastructure refresh are two distinct edits to the same file — the plan
  should list them separately.

**agentic-mbse (from survey cites):** decision-table reword to profile vocabulary
(`docs/subtype-enumeration-decision-table.md:13-14,18,24,33-35` — drop `is_droppable_constraint` /
"dropped predicates" / "revisited by the constraint-execution epic"); `MODELING_GUIDE.md:280` no
longer "not executable"; new durable ConstraintFacts/ExpressionIR page (D3).

**teax (from survey cites):** document the `entry_models` property in
`docs/evaluation-and-study.md` (`:51` currently describes typed entry generically;
`evaluator.py:107` defines it) as the channel→typed-model map derived from the pipeline spec.

**fusion-tea (from survey cites):** `pipeline-walkthrough.html` pointer/retirement note (settled:
note only); drop the `ToyPlantParams` alias at the three sites (`bench_prepare_once.py:36,61`,
`run_viability_study.py:135`) plus the stale comment (`run_viability_study.py:130`). This is the
item's only code change.

## Required Invariants

The `[INHERITED]` cautions are checkable bars any doc this item writes or edits must satisfy:

- **INV-1.** `lower_constraints_enabled` is described as landed history (default-on, GRANDFATHERED
  set now empty) — **never** as a live drop path.
- **INV-2.** No doc claims `collect_constraint_manifest` was removed. Only the report/render/
  serialize surface was retired; the collector survives (a kept migration-mapping test needs it —
  `test_constraint_migration_mapping.py`, REQ-CL-04).
- **INV-3.** CE-F1 (standalone `constraint_catalog.json` emission) and CE-F2 (multi-channel
  `CandidateBridge`) are referenced as open follow-ons; docs describe the **current** embedded-
  catalog / single-channel-bridge reality, never CE-F1/F2 as landed.
- **INV-4.** Matrix counts stay internally consistent. After adding CON, **recount families / total
  reqs / distinct test files from the family Index** (not the summary block), and set
  `overview.md:218` equal to the matrix family count. Adding CON: families 31→32; total +N(CON rows);
  test files +2 if `test_contract_models.py` / `test_seal_step9.py` are net-new citations (confirm —
  neither appeared in a matrix row grep). This is the known matrix drift trap.
- **INV-5.** No new stale symbol: every symbol an edited doc names greps clean in `src/`, unless it
  is an explicitly-marked historical note.
- **INV-6 (explainer buildability).** The refreshed `EXPLAINER_PROMPT.md` must be buildable by the
  v2 HTML agent **from the brief alone** — truthful prose is not enough. Concretely, the refresh must
  update the brief's *buildability infrastructure*, not just its narrative: (a) each of the eight new
  constraint-exec areas has a **responsibility-map row** naming its owner (module/symbol) and its
  reference-doc pointer, including the new/renamed homes (docs 28 and 29); (b) the **reading list**
  names the concrete data-source files for those areas (the new docs + `test_contract_models.py` /
  `test_seal_step9.py` for contracts/sealing); (c) any **reuse-guidance** delta vs the Gen-1
  machinery is stated. One hard sub-check: the brief's cited matrix counts / family number match the
  recounted matrix (INV-4) — the reading list currently reads a stale "253 … 30 families"
  (`EXPLAINER_PROMPT.md:~189`), which must be corrected. This makes "buildable" auditable, not
  implicit; SC-6's mechanical checklist discharges it.

## Component Overview

Surfaces and their action (the "components" of a docs sweep):

| Surface | Repo | Action |
|---|---|---|
| `27-snapshot-generation.md` + REQ-SNAP-09 | sysml-codegen | correct v1→v3, add constraint-facts key + v2→v3 note |
| `14-` / `16-` / `19-*.md`, REQ-AST-06, REQ-CA-02 | sysml-codegen | `ExpressionAST`→`ExpressionIR` symbol set; D5 row rewords |
| `09-data-models.md` | sysml-codegen | ModuleKind (5 values) on PipelineModule; ComputationGraph `constraint_catalog` |
| `08-generation.md` | sysml-codegen | constraint + report-aggregator render seams |
| `00-pipeline-overview.md`, `overview.md` | sysml-codegen | REQ-PIPE-06; lowering phase in narrative; family count |
| `29-contracts-and-sealing.md` (new) | sysml-codegen | contracts/sealing reference doc (D2) |
| `verification-matrix.md` | sysml-codegen | new CON family (D1); count recount (INV-4) |
| `EXPLAINER_PROMPT.md` | sysml-codegen | re-anchor to HEAD; slot eight areas; retire caveats; refresh buildability infra (INV-6) |
| `new_pipeline_explainer.html` | sysml-codegen | in-file deprecation banner (D4) |
| BACKLOG | sysml-codegen | register v2 HTML build follow-on |
| `subtype-enumeration-decision-table.md`, `MODELING_GUIDE.md:280` | agentic-mbse | profile vocabulary reword |
| ConstraintFacts/ExpressionIR page (new) | agentic-mbse | durable summary+pointer (D3) |
| `evaluation-and-study.md` | teax | document `entry_models` |
| `pipeline-walkthrough.html`, driver scripts | fusion-tea | retirement note; drop alias |

## Non-Goals

- Building `pipeline_explainer_v2.html` (registered as a follow-on), or patching Gen-1 HTML content
  (banner only).
- A full verify-every-doc scrub of `docs/architecture/` (separate item shape).
- Fixing CE-F1/CE-F2, or any code change beyond the fusion-tea alias removal.
- PDF/DOCX-extraction docs in agentic-mbse.

## Implementation Notes

- **Matrix recount is the top gotcha.** Update the summary block *and* the Index counts *and*
  `overview.md:218` together, recomputed from the family Index after CON lands. See INV-4.
- **Re-grep every cross-repo cite before editing** — the survey lines are verified but this session
  couldn't independently confirm them; a wrong line risks editing an already-fixed or moved surface.
- **Historical-note exception:** the D5 rewords and any deliberate "this used to be X" note may name
  a retired symbol *if* clearly framed as history — INV-5 is about live claims, not history.
- **Explainer brief has a two-bar audit:** (a) *mechanical* — grep-clean of "constraints are
  dropped" / `resolve_input()`-unwired caveats, eight areas slotted per the survey map, anchor is
  current HEAD (not `pipeline-truth-epic`), **plus the buildability infrastructure refreshed per
  INV-6** (responsibility-map rows, reading-list data sources, reuse-guidance delta, corrected
  matrix counts); (b) *judgment* — a spot-read of remaining claims finds none contradicted by HEAD.
  Keep the honest caveats that are *still* true (e.g. `attribute :>> attr = <expression>` silently
  dropped; EXPOSE_COMPUTED rejected) at their current hedge; do not strengthen or resurrect retired
  ones. Note the two INV namespaces do not collide: this design's Required Invariants are INV-1..6;
  the `contract INV-*` labels in D1 are the contracts machinery's own numbering.
- **fusion-tea alias sequencing caveat:** after the alias drop, the two driver scripts require a
  teax with CE-F3 (`0d606a4`). They are exploration drivers, not CI-gated, and already run against
  the epic-branch teax — so this is safe, but note it in the change.

## Potential Risks

- **Cross-repo cite drift (B2).** Mitigated by re-grep-before-edit; the cites carry symbol names, so
  a moved line is recoverable.
- **Matrix count divergence (INV-4).** The recurring drift mode: editing rows without recounting, or
  updating the summary but not the Index (or vice-versa). Mitigated by recounting from the Index and
  cross-checking `overview.md:218`.
- **Reintroducing a retired story.** An implementer writing the new ModuleKind/contracts/lowering
  docs could accidentally re-teach "constraints are dropped" or "the manifest collector was removed."
  Mitigated by INV-1/2/3 as explicit acceptance bars.

## Integration Strategy

Additive and corrective; nothing is replaced structurally. New doc 29 slots into the existing
reference-doc numbering; the CON family slots into the matrix; the explainer brief edit supersedes
its own stale content in place. The one runtime-affecting change (fusion-tea alias drop) lands in an
exploration-driver path, not a CI-gated one. Work lands as appended commits on the existing branches
(sysml-codegen `constraint-exec-epic`; agentic-mbse PR #11; teax PR #3; fusion-tea `main`).

## Validation Approach

Each success criterion maps to a check:

- *Corrections/gaps (SC-1/2/3):* grep the edited docs for the retired symbols (must be clean outside
  marked history); confirm ModuleKind's five values, `constraint_catalog`, and the render seams
  appear where specified; confirm doc 29 covers the four contract/seal surfaces; confirm the CON
  family exists and the recounted totals agree across matrix summary, Index, and `overview.md:218`.
- *Cross-repo (SC-4/5/7):* re-grep each survey cite in-repo; confirm the retired vocabulary is gone,
  `entry_models` is documented, the walkthrough note and alias drop are in place.
- *Explainer (SC-6):* run the mechanical grep checklist **and the INV-6 buildability audit** — every
  one of the eight areas has a responsibility-map row (owner + reference-doc pointer, incl. 28/29),
  reading-list data sources (incl. the two contract test files), and any reuse-guidance delta; the
  brief's cited matrix counts match the recounted matrix — then the judgment spot-read.
- *Inherited history (SC-8):* audit every written/edited doc against INV-1/2/3.
- *Follow-on (SC-9):* the v2 HTML build item is in BACKLOG pointing at the brief.

## Next-Stage Handoff

- **Fixed:** the four delegated calls (D1-D4) and the retired-symbol call (D5) are settled — do not
  relitigate. The survey is ground truth; do not re-survey. The correct claims are supplied by
  spec + survey; the plan's job is to apply them, not re-derive them.
- **Open (plan settles):** exact CON row count and wording; exact section placement within each
  target doc; the precise durable-page location in agentic-mbse's `docs/` tree (its layout is
  unread this session).
- **De-risk first:** the matrix recount (INV-4) and the cross-repo re-grep (B2) — both are cheap and
  both are where a silent wrong-story or count divergence would slip through.

## Design-Review Resolutions

Applied 2026-07-13 from `design-review.md` (verdict Revise; approach sound, three tightenings).

- **[Major] SC-6 secured truth, not buildability → Fixed.** Added **INV-6 (explainer
  buildability)** requiring the refresh to update the brief's buildability infrastructure —
  responsibility-map rows (owner + reference-doc pointer, incl. docs 28/29), reading-list data
  sources (incl. `test_contract_models.py` / `test_seal_step9.py` for contracts), reuse-guidance
  delta, and corrected matrix counts (the stale "253 … 30 families"). Routed into the Architecture
  explainer line, the Implementation-Notes two-bar audit, and Validation SC-6 so the plan and
  auditor both see it.
- **[Minor] INV-N namespace collision → Fixed.** D1's parentheticals now read `contract INV-1` /
  `contract INV-8`, with an explicit note that the contracts machinery's numbering is a distinct
  namespace from this design's Required Invariants INV-1..6 (what SC-8 audits against).
- **[Minor] Overstated test counts → Fixed.** Research Findings now reads 7 functions / 8 collected
  for `test_contract_models.py` and 5 for `test_seal_step9.py`.

---
Next Step: After approval → `/_my_plan` (multi-repo, multi-surface — a checklist plan keeps the
sweep auditable), then `/_my_implement`.

ARTIFACT: .project/active/docs-explainer-refresh/design.md
