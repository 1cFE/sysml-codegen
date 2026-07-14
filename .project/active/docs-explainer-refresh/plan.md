# Implementation Plan: Docs + Explainer-Brief Refresh (post-CONSTRAINT-EXEC)

**Status:** Draft
**Created:** 2026-07-13
**Last Updated:** 2026-07-13
**Branch:** constraint-exec-epic (sysml-codegen home; touches agentic-mbse, teax, fusion-tea)

## Source Documents
- **Spec:** `.project/active/docs-explainer-refresh/spec.md` (revised 2026-07-13)
- **Design:** `.project/active/docs-explainer-refresh/design.md` ← component routing, key decisions (D1-D5), Required Invariants (INV-1..6)
- **Evidence:** `.project/active/docs-explainer-refresh/staleness-survey.md` ← the stale-claim inventory (trust; do not re-survey)

This is a **docs sweep**, not a code feature. There is no new mechanism (design "Core Concept"):
each edit is a routing decision — correct-in-place, or give machinery with zero coverage a new
home. So "test-first" here means **the verification grep/recount is defined before the edit**, and
each phase's gate is a cheap check (retired-symbol grep, matrix recount from the Index, or a
two-script syntax check), not a pytest run.

## Implementation Strategy

**Phasing Rationale:** Serialize by repo to keep commits coherent and auditable. Home repo
(sysml-codegen) first and in three coherent commits — in-place corrections, then the new doc +
matrix family + recount, then the explainer brief (the biggest single deliverable, its own commit).
Then the three cross-repo repos one at a time, each gated on a re-grep of its survey cites. Finally
the close-out (BACKLOG follow-on + CURRENT_WORK + checkbox reconciliation). The brief's ordering is
followed exactly; sysml-codegen reappears at the end only for the administrative close-out.

**Critical Path:**
Phase 1 (in-place corrections) → Phase 2 (doc 29 + CON family + **recount**) → Phase 3 (explainer
brief + Gen-1 banner) → Phase 4 (agentic-mbse) → Phase 5 (teax) → Phase 6 (fusion-tea alias drop) →
Phase 7 (BACKLOG + close-out). Phases 4/5/6 have no dependency on each other and could run in any
order, but commit them separately per repo.

**First Proof Point:** Phase 1's retired-symbol grep goes clean on the corrected sysml-codegen docs
(`ExpressionAST`/`build_expression_ast`/`compile_expression` zero-hit outside marked history). That
proves the correct-in-place routing works before any new-home or cross-repo work.

**The two risk points (design "De-risk first"):**
1. **Matrix recount (INV-4)** — Phase 2. The recurring drift trap: edit rows without recounting, or
   update the summary but not the Index. Recount families / total reqs / distinct test files **from
   the family Index**, not the summary block, then set `overview.md:218` equal to the family count.
2. **Cross-repo cite drift (B2)** — Phases 4/5/6. Survey lines were verified 2026-07-13 but can
   drift. **Re-grep each cite in-repo before editing.** If a cite does not match, STOP and record it
   in this plan's Implementation Notes rather than guessing a new target.

**Repo → path map (all four on their live branches; NEVER rebase/force-push; do NOT push — the
orchestrator pushes at the end):**

| Repo | Path | Branch |
|---|---|---|
| sysml-codegen (home) | `/home/reid/1cfe/sysml-codegen` | `constraint-exec-epic` |
| agentic-mbse | `/home/reid/1cfe/agentic-mbse` | `constraint-exec-epic` (PR #11) |
| teax | `/home/reid/1cfe/teax` | `constraint-exec-epic` (PR #3) |
| fusion-tea | `/home/reid/1cfe/fusion-tea` | `main` (local) |

**Commit discipline (every phase):** one commit per phase, **pathspec-limited** so unrelated
untracked files (`.claude/projects/`, `.project/research/*`) never sweep in:
`git -C <repo> add <explicit paths> && git -C <repo> commit -- <same explicit paths>`. Commit
subject leads with the decision.

**Sandbox reality:** the implement session usually has in-repo execution but may lose it on resume.
Every phase is completable **file-edit-first**; the verification tail is a short grep/check the
orchestrator can run if the implementer can't.

---

## Phase 1: sysml-codegen — in-place corrections + gap-fills

### Goal
Correct every stale claim in existing sysml-codegen docs and fill the ModuleKind / lowering-phase
gaps into the docs that already own those concepts. First and largest correction batch; proves the
correct-in-place routing. **One commit.**

### Assumption Under Test
The survey's stale-claim inventory for sysml-codegen is complete and its cites are accurate at HEAD
(B1/B2) — a retired symbol does not survive outside this list, and each cited line still says what
the survey recorded.

### Verification Gate (define before editing)
```bash
cd /home/reid/1cfe/sysml-codegen
# After edits, retired symbols must be zero-hit outside deliberately-marked history:
grep -rn 'ExpressionAST\|build_expression_ast\|compile_expression' docs/architecture/
# ModuleKind five values present where specified:
grep -rn 'REPORT_AGGREGATOR\|CONSTRAINT\|module_kind\|constraint_catalog' docs/architecture/reference/09-data-models.md
# Snapshot v3 landed, no "Current: 1":
grep -n 'Current' docs/architecture/reference/27-snapshot-generation.md
```
Zero retired-symbol hits (outside a marked "this used to be X" note) = gate green (SC-1, SC-2; INV-5).

### Changes Required

**See `design.md` for:** Component Overview table (surface → action), Key Decision D5 (matrix-row
reword), INV-1/2/3/5 (inherited-history bars), Implementation Notes (historical-note exception).

Re-read each target region before editing (design cites were verified at 556e391; confirm they
still match):

- [ ] **Snapshot v3** — `27-snapshot-generation.md`: `:37` "Current: **1**" → **3**; `:40-43`
      format-schema key list gains the **constraint-facts** section; `:58-64` narrative gains a
      **v2→v3 migration note**. (SC-1; survey L15-18)
- [ ] **Snapshot matrix text** — `verification-matrix.md:506` REQ-SNAP-09: reword V1/V2 narration to
      cover v3 (reword in place, same REQ ID; count-neutral).
- [ ] **ExpressionIR symbol set** — replace retired `ExpressionAST`/`build_expression_ast()`/
      `compile_expression()` with `ExpressionIR` + current symbols (`compile_calc_def`,
      `classify_compilability`; rendering in `extraction/calc_compat_renderer.py`) across:
      `14-expression-compiler.md` (pervasive, ~lines 28-226); `16-computed-attributes.md`
      (`:15,62,156,157`); `19-ast-dispatch-invariant.md` (`:42,89`). (SC-1; survey L19-25)
- [ ] **Matrix rows REQ-AST-06 (`:96`) and REQ-CA-02 (`:144`)** — reword text to name current
      symbols, **preserve the REQ IDs** (D5, count-neutral). Each reworded row must still describe
      what its cited test pins — confirm against the Test File column.
- [ ] **ModuleKind gap (09-data-models.md)** — document all five `ModuleKind` values
      (`CALCULATION`/`FORMULA`/`AGGREGATION`/`CONSTRAINT`/`REPORT_AGGREGATOR`,
      `resolution/models.py:161-170`) on `PipelineModule.module_kind` (`:193`, required), **replacing
      the two retired bool-flag description**; add `constraint_catalog` to the `ComputationGraph`
      field list. (SC-2; survey L33-37)
- [ ] **Render seams (08-generation.md)** — document the constraint + report-aggregator render
      seams. (SC-2)
- [ ] **Lowering phase + REQ-PIPE-06 (00-pipeline-overview.md)** — name the constraint-lowering
      phase in the step narrative; correct REQ-PIPE-06 (`:22` "all three module types"). (SC-2;
      survey L37)
- [ ] **Lowering phase in overview narrative (overview.md)** — add the constraint-lowering phase to
      the 7-step narrative. (SC-2; survey L38) **Do NOT touch the `:218` family count here** — that
      is finalized in Phase 2 after the recount.

**Inherited-history bars (apply to every edit above):** INV-1 — describe
`lower_constraints_enabled` only as landed history (default-on, GRANDFATHERED empty), never a live
drop path. INV-2 — never say `collect_constraint_manifest` was removed. INV-3 — reference CE-F1/CE-F2
as open follow-ons, describe the embedded-catalog / single-channel-bridge reality as current.

### Commit
```bash
cd /home/reid/1cfe/sysml-codegen
git -C /home/reid/1cfe/sysml-codegen add \
  docs/architecture/reference/27-snapshot-generation.md \
  docs/architecture/reference/14-expression-compiler.md \
  docs/architecture/reference/16-computed-attributes.md \
  docs/architecture/reference/19-ast-dispatch-invariant.md \
  docs/architecture/reference/09-data-models.md \
  docs/architecture/reference/08-generation.md \
  docs/architecture/reference/00-pipeline-overview.md \
  docs/architecture/overview.md \
  docs/architecture/verification-matrix.md
git -C /home/reid/1cfe/sysml-codegen commit -- <same paths> \
  -m "Docs: re-project stale sysml-codegen surfaces onto HEAD (snapshot v3, ExpressionIR, ModuleKind, lowering phase)"
```

### Validation
- [ ] Retired-symbol grep clean outside marked history (gate above).
- [ ] `09-data-models.md` shows all five ModuleKind values + `constraint_catalog`.
- [ ] `git -C /home/reid/1cfe/sysml-codegen status` shows only the intended paths staged (no
      `.claude/`, no `.project/research/`).

**What We Know Works After This Phase:** every existing sysml-codegen doc that taught a retired
symbol or a missing-machinery gap now reads correct at HEAD; matrix row counts are unchanged
(reword-in-place only).

---

## Phase 2: sysml-codegen — new doc 29 + CON matrix family + recount

### Goal
Give contracts/sealing a reference-doc home and a verification-matrix family, then recount the
matrix and reconcile `overview.md:218`. **One commit.** This phase owns the matrix-recount risk
point.

### Assumption Under Test
`test_contract_models.py` and `test_seal_step9.py` pin the behaviors the new doc teaches, so the CON
rows have real anchors (B3), and the recount lands internally consistent (INV-4).

### Verification Gate (define before editing)
```bash
cd /home/reid/1cfe/sysml-codegen
# CON family present and anchored to the two test files:
grep -n 'CON\|test_contract_models\|test_seal_step9' docs/architecture/verification-matrix.md
# Recount families from the Index (NOT the summary block):
awk '/^## Index/{f=1;next} /^## Requirements by Family/{f=0} f&&/^- \[/{c++} END{print "families:",c}' \
  docs/architecture/verification-matrix.md
# overview.md family count equals the matrix family count:
grep -n 'requirement families' docs/architecture/overview.md
```
Families = 32 (31 + CON), and `overview.md:218` equals 32 = gate green (SC-3, INV-4).

### Changes Required

**See `design.md` for:** D1 (CON family shape, candidate rows, the `contract INV-*` vs design
`INV-*` namespace split), D2 (doc 29 home + scope), INV-4 (recount procedure).

- [ ] **New doc `29-contracts-and-sealing.md`** — cover `ModelContract`/`PackageContract`
      (`contracts/models.py:51,92`), `seal_package` (`contracts/seal.py:57`), verify-on-load
      (`contracts/verify.py`, `verify_package`), and the `seal` CLI subcommand
      (`cli/__init__.py:704,876`). One-concept-per-file; embedded catalog is the current reality
      (INV-3). (SC-3; D2)
- [ ] **Doc 28 forward pointer** — `28-constraint-lowering-and-catalog.md:76-80` "Contracts (seam
      disposition)" stub becomes a forward pointer to doc 29. (D2)
- [ ] **CON matrix family** — add `CON — Contracts & Sealing` to the family Index and the
      Requirements-by-Family section; rows anchored to `test_contract_models.py` (unit) and
      `test_seal_step9.py` (conformance). Settle exact row count/wording from D1's candidate list;
      follow the CL precedent of a short register + honest "partial coverage" note if the doc'd
      surface exceeds the pinned rows. Use `contract INV-*` labels only where D1 does (distinct
      namespace from this design's INV-1..6). (SC-3; D1)
- [ ] **Recount (INV-4)** — after CON lands, recompute from the **family Index**: families 31→**32**;
      total reqs +N(CON rows); distinct test files **+2** (confirm `test_contract_models.py` /
      `test_seal_step9.py` are net-new citations — neither appeared in a prior matrix-row grep).
      Update the **summary block AND the Index counts** together.
- [ ] **overview.md:218** — set "29 requirement families" to **32** (= the recounted matrix family
      count). Register doc 29 (and doc 28 if still absent) in `overview.md`'s doc-list and component
      tables (`overview.md:148-192`). (INV-4; D2)

### Commit
```bash
git -C /home/reid/1cfe/sysml-codegen add \
  docs/architecture/reference/29-contracts-and-sealing.md \
  docs/architecture/reference/28-constraint-lowering-and-catalog.md \
  docs/architecture/verification-matrix.md \
  docs/architecture/overview.md
git -C /home/reid/1cfe/sysml-codegen commit -- <same paths> \
  -m "Docs: add contracts/sealing reference (doc 29) + CON matrix family; recount matrix to 32 families"
```

### Validation
- [ ] Recount gate green: Index families = 32, summary = 32, `overview.md:218` = 32, all three agree.
- [ ] Distinct-test-files count reflects +2 (confirm the two files were net-new).
- [ ] Doc 29 covers all four contract/seal surfaces; doc 28 stub now points forward.

**What We Know Works After This Phase:** contracts/sealing has a durable home and a tested matrix
family; the matrix is internally consistent across summary / Index / overview.

---

## Phase 3: sysml-codegen — explainer brief rewrite + Gen-1 deprecation banner

### Goal
Re-anchor `EXPLAINER_PROMPT.md` to current HEAD as a truthful, **buildable** v2 brief, and stamp the
superseded Gen-1 HTML with a deprecation banner. The biggest single deliverable — **its own commit.**

### Assumption Under Test
The brief can be made buildable-from-the-brief-alone (INV-6) by refreshing its buildability
infrastructure, not just its prose — and no remaining claim contradicts HEAD (SC-6 judgment bar).

### Verification Gate (define before editing) — two bars, audited differently
```bash
cd /home/reid/1cfe/sysml-codegen
# (a) MECHANICAL: stale caveats gone, anchor is HEAD (not pipeline-truth-epic):
grep -n 'constraints are dropped\|no execution path\|resolve_input\|pipeline-truth-epic' .project/active/EXPLAINER_PROMPT.md
# stale reading-list matrix counts corrected (was "253 ... 30 families"):
grep -n '253\|30 families' .project/active/EXPLAINER_PROMPT.md
```
- **(a) Mechanical checklist (SC-6):** the greps above go clean (or only inside a clearly-framed
  "was true, now retired" note); the **eight constraint-exec areas** are slotted per the survey map
  (lowering phase; `module_kind` as 4th+5th module family with colors; Kleene modules as an Act-3
  hard part; report aggregator; catalog; contracts/sealing in the diagnostics-as-contract frame;
  snapshot v3 in operational reality; teax study layer as top-of-stack consumer); **INV-6
  buildability infra refreshed** (below); the brief's cited matrix counts match the Phase-2 recount
  (**32 families**, not "30 … 253").
- **(b) Judgment bar (Item 10's bar):** a spot-read samples remaining claims and checks each against
  code — **no claim contradicted by HEAD**. Read-and-verify, not a grep.

### Changes Required

**See `design.md` for:** Architecture "Explainer brief" bullet, INV-6 (buildability sub-checks a/b/c
+ the hard matrix-count sub-check), Implementation Notes "two-bar audit" (which honest caveats to
**keep** at their current hedge — `attribute :>> attr = <expression>` silently dropped;
EXPOSE_COMPUTED rejected — and not to resurrect retired ones). D4 (banner).

**These are two distinct edits to the same file — list them separately:**
- [ ] **Narrative slotting** — retire stale caveats ("constraints are dropped … no execution path",
      `resolve_input()` unwired); re-anchor to current HEAD; slot the eight areas into the existing
      4-act structure per the survey's map. Keep still-true honest caveats at their current hedge.
      (SC-6 bar a, narrative)
- [ ] **Buildability infrastructure refresh (INV-6)** — (a) each of the eight areas gets a
      **responsibility-map row** naming its owner (module/symbol) and its reference-doc pointer,
      including the new/renamed homes (docs 28 and 29); (b) the **reading list** names the concrete
      data-source files (the new docs + `test_contract_models.py` / `test_seal_step9.py` for
      contracts/sealing); (c) any **reuse-guidance delta** vs the Gen-1 machinery is stated; (d) the
      stale reading-list count (`~:189` "253 … 30 families") corrected to the Phase-2 recount.
      (SC-6 bar a, buildability; INV-6)
- [ ] **Gen-1 HTML banner (D4)** — insert a small fixed banner at top-of-`<body>` in
      `.project/diagrams/new_pipeline_explainer.html`: "Superseded — predates CONSTRAINT-EXEC /
      PIPELINE-TRUTH; see `EXPLAINER_PROMPT.md` for the current brief." One-element insert only;
      patching the 268 KB content is a Non-Goal.

### Commit
```bash
git -C /home/reid/1cfe/sysml-codegen add \
  .project/active/EXPLAINER_PROMPT.md \
  .project/diagrams/new_pipeline_explainer.html
git -C /home/reid/1cfe/sysml-codegen commit -- <same paths> \
  -m "Explainer: re-anchor EXPLAINER_PROMPT.md to HEAD (eight areas slotted, buildability infra refreshed); deprecate Gen-1 HTML"
```

### Validation
- [ ] Mechanical grep clean (gate a); eight areas present; buildability rows + reading-list sources
      present; cited matrix counts = 32 families (match Phase 2).
- [ ] Judgment spot-read (gate b): sample ~5-8 remaining claims, verify each against `src/` — none
      contradicted.
- [ ] Banner renders at top-of-body; Gen-1 content otherwise untouched.

**What We Know Works After This Phase:** the v2 brief is truthful and buildable-from-the-brief-alone;
a reader opening the Gen-1 HTML directly sees the supersession signal.

---

## Phase 4: agentic-mbse — decision-table reword + durable ConstraintFacts/ExpressionIR page

### Goal
Make agentic-mbse teach one story: retire the dropped-constraint vocabulary the decision table still
carries, and give ConstraintFacts + ExpressionIR a durable `docs/` home. **One commit.**
Repo: `/home/reid/1cfe/agentic-mbse` (branch `constraint-exec-epic`, PR #11 — never rebase/force-push).

### Assumption Under Test
The cross-repo survey cites are accurate at agentic-mbse HEAD (B2).

### Verification Gate (define before editing)
```bash
cd /home/reid/1cfe/agentic-mbse
# RE-GREP CITES FIRST (before editing) — if any miss, STOP and record in Implementation Notes:
grep -n 'is_droppable_constraint\|report_dropped_constraints\|dropped predicates\|revisited by the constraint-execution epic' docs/subtype-enumeration-decision-table.md
grep -n 'not executable' modeling_project/MODELING_GUIDE.md
# After edits, the retired vocabulary is gone:
grep -rn 'is_droppable_constraint\|dropped predicates' docs/subtype-enumeration-decision-table.md
```
Retired vocabulary zero-hit after edit = gate green (SC-4).

### Changes Required

**See `design.md` for:** Architecture "agentic-mbse" bullet, D3 (durable summary+pointer page, NOT a
full architecture doc — durability is the bar: the page must stand on its own for the mental model
so it survives `.project/` archival).

- [ ] **Decision-table reword** — `docs/subtype-enumeration-decision-table.md:13-14,18,24,33-35`:
      speak profile vocabulary; drop `is_droppable_constraint` / "dropped predicates" / "documented
      v2 limitation, revisited by the constraint-execution epic". (SC-4; survey L47-50)
- [ ] **MODELING_GUIDE.md:280** — patterns index no longer says "constraints.md | … not
      executable". (SC-4; survey L51-52)
- [ ] **New durable page** — a real `docs/` page carrying the core mental model for ConstraintFacts
      (neutral schemas + extraction, Item 1) and production `ExpressionIR` (Item 2): what each is,
      why it exists, key types/modules — then a pointer to the archived `.project/` design artifacts
      for full depth. Settle the precise location in the `docs/` tree (unread this session — inspect
      the layout first; at minimum an architecture pointer that survives archival). (SC-4; D3)

**Test-suite note:** doc-only phase — no suite required. **Never run `pytest tests/ -m ""`** (pulls
in the PDF-corpus subsystem). If a sanity check is wanted at all, it is the greps above.

### Commit
```bash
git -C /home/reid/1cfe/agentic-mbse add \
  docs/subtype-enumeration-decision-table.md \
  modeling_project/MODELING_GUIDE.md \
  <new durable page path>
git -C /home/reid/1cfe/agentic-mbse commit -- <same paths> \
  -m "Docs: retire dropped-constraint vocabulary from decision table; add durable ConstraintFacts/ExpressionIR page"
```

### Validation
- [ ] Re-grep cites matched before editing (or a miss recorded).
- [ ] Retired vocabulary gone; MODELING_GUIDE:280 corrected; new page stands alone for the mental
      model (pointer rot would not erase the core story).
- [ ] Staged paths only; no unrelated files.

**What We Know Works After This Phase:** agentic-mbse no longer contradicts its own `constraints.md`;
ConstraintFacts/ExpressionIR have a durable home.

---

## Phase 5: teax — document `entry_models`

### Goal
Name the CE-F3 mechanism callers use to obtain entry types. **One commit.**
Repo: `/home/reid/1cfe/teax` (branch `constraint-exec-epic`, PR #3 — never rebase/force-push).

### Assumption Under Test
The survey cite is accurate at teax HEAD (B2); `entry_models` is the current mechanism
(`evaluator.py:107`, teax `0d606a4`).

### Verification Gate (define before editing)
```bash
cd /home/reid/1cfe/teax
# RE-GREP FIRST: confirm the generic typed-entry description and the property definition:
sed -n '45,60p' docs/evaluation-and-study.md
grep -n 'entry_models' src/**/evaluator.py 2>/dev/null || grep -rn 'entry_models' --include=evaluator.py .
# After edit, the property is documented:
grep -n 'entry_models' docs/evaluation-and-study.md
```
`entry_models` named in the doc = gate green (SC-5).

### Changes Required

**See `design.md` for:** Architecture "teax" bullet.

- [ ] **`docs/evaluation-and-study.md`** (`:51` currently describes typed entry generically) —
      document the `entry_models` property as the channel→typed-model map derived from the pipeline
      spec (defined `evaluator.py:107`). (SC-5; survey L59-62)

**Test-suite note:** doc-only phase — no suite required.

### Commit
```bash
git -C /home/reid/1cfe/teax add docs/evaluation-and-study.md
git -C /home/reid/1cfe/teax commit -- docs/evaluation-and-study.md \
  -m "Docs: document PreparedEvaluator.entry_models as the channel->typed-model entry map (CE-F3)"
```

### Validation
- [ ] Re-grep cite matched before editing.
- [ ] `entry_models` documented as the channel→typed-model map.

**What We Know Works After This Phase:** teax docs name the mechanism callers use for entry types.

---

## Phase 6: fusion-tea — walkthrough retirement note + drop the ToyPlantParams alias

### Goal
Close the fusion-tea residue: a retirement note on the stale walkthrough, and drop the now-unneeded
`ToyPlantParams` alias from the two driver scripts. **This is the item's only code change.**
**One commit.** Repo: `/home/reid/1cfe/fusion-tea` (branch `main`, local).

### Assumption Under Test
The three alias sites + the stale comment are at the survey's lines at fusion-tea HEAD (B2); the
alias is safe to drop because the scripts already run against an epic-branch teax with CE-F3.

### Verification Gate (define before editing)
```bash
cd /home/reid/1cfe/fusion-tea
# RE-GREP CITES FIRST — if any miss, STOP and record:
grep -n 'ToyPlantParams' exploration/ife_e2e/study/bench_prepare_once.py
grep -n 'ToyPlantParams' exploration/ife_e2e/study/run_viability_study.py
sed -n '128,136p' exploration/ife_e2e/study/run_viability_study.py   # stale comment ~:130
# After edit — alias gone, scripts still parse (the minimal check for a code change):
grep -rn 'ToyPlantParams' exploration/ife_e2e/study/
python -m py_compile exploration/ife_e2e/study/bench_prepare_once.py exploration/ife_e2e/study/run_viability_study.py
```
`ToyPlantParams` zero-hit AND both scripts compile clean = gate green (SC-7).

### Changes Required

**See `design.md` for:** Architecture "fusion-tea" bullet, Implementation Notes "alias sequencing
caveat" (default is *drop*, decided at orchestration 2026-07-13).

- [ ] **`pipeline-walkthrough.html`** (repo root) — add a pointer/retirement note only (settled: note
      only, not a content rewrite). (SC-7; survey L88)
- [ ] **`bench_prepare_once.py:36,61`** — drop the `module.ToyPlantParams = module.IfePlantParams`
      alias at both sites. (SC-7; survey L90-91)
- [ ] **`run_viability_study.py:135`** — drop the alias; **`:130`** — remove the now-stale comment.
      (SC-7)
- [ ] Note in the commit body: after the drop, the scripts require a teax with CE-F3 (`0d606a4`);
      they are exploration drivers (not CI-gated) already running against epic-branch teax — safe.

**Minimal check (this is the one code change):** `py_compile` of the two edited scripts (gate above).
No test suite.

### Commit
```bash
git -C /home/reid/1cfe/fusion-tea add \
  pipeline-walkthrough.html \
  exploration/ife_e2e/study/bench_prepare_once.py \
  exploration/ife_e2e/study/run_viability_study.py
git -C /home/reid/1cfe/fusion-tea commit -- <same paths> \
  -m "Drop ToyPlantParams alias (unneeded since teax CE-F3); add retirement note to pipeline-walkthrough.html"
```

### Validation
- [ ] Re-grep cites matched before editing (or a miss recorded).
- [ ] `ToyPlantParams` zero-hit under `exploration/ife_e2e/study/`; both scripts `py_compile` clean.
- [ ] Walkthrough carries the retirement note.

**What We Know Works After This Phase:** fusion-tea has no stale alias residue and its walkthrough
signals its own staleness.

---

## Phase 7: sysml-codegen — BACKLOG follow-on + close-out

### Goal
Register the v2 HTML build as its own follow-on item, then reconcile the tracking surfaces.
**One commit.** Repo: `/home/reid/1cfe/sysml-codegen`.

### Assumption Under Test
None new — this is administrative close-out (SC-9 + tracking hygiene).

### Changes Required

- [ ] **BACKLOG** — `.project/backlog/BACKLOG.md` (NOT a repo-root `BACKLOG.md` — that path does not
      exist): register the **v2 HTML build** follow-on (`pipeline_explainer_v2.html`), pointing at
      the refreshed `EXPLAINER_PROMPT.md` brief. Not built here. (SC-9)
- [ ] **CURRENT_WORK** — `.project/CURRENT_WORK.md`: update the docs-explainer-refresh entry to
      reflect completion across the four repos.
- [ ] **Checkbox reconciliation** — tick the Success-Criteria boxes in `spec.md` and mark
      `design.md`/this `plan.md` status Complete; fill the Implementation Notes section below with
      what actually changed and any cite drift found.

### Commit
```bash
git -C /home/reid/1cfe/sysml-codegen add \
  .project/backlog/BACKLOG.md \
  .project/CURRENT_WORK.md \
  .project/active/docs-explainer-refresh/spec.md \
  .project/active/docs-explainer-refresh/design.md \
  .project/active/docs-explainer-refresh/plan.md
git -C /home/reid/1cfe/sysml-codegen commit -- <same paths> \
  -m "Close-out: register v2 HTML build follow-on (BACKLOG); reconcile docs-explainer-refresh tracking"
```

### Validation
- [ ] BACKLOG carries the v2 HTML follow-on pointing at the brief.
- [ ] CURRENT_WORK + spec/design/plan checkboxes reconciled.
- [ ] **Do NOT push** — the orchestrator pushes all four repos at the end.

**What We Know Works After This Phase:** the follow-on is registered; tracking reflects the completed
sweep.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** No install/build needed for a docs sweep. The only
executable check is `py_compile` on the two fusion-tea scripts (Phase 6). agentic-mbse: never run
`pytest tests/ -m ""`.

## Risk Management

**See `design.md#potential-risks`.** Phase-specific mitigations:
- **Phase 2 (matrix recount, INV-4):** recount from the Index, update summary + Index + overview
  together, cross-check all three agree at 32.
- **Phases 4/5/6 (cross-repo cite drift, B2):** re-grep every cite before editing; on a miss, STOP
  and record in Implementation Notes — never guess a moved target.
- **Phases 1-4 (reintroducing a retired story):** INV-1/2/3 are explicit acceptance bars on every
  new/edited doc (SC-8) — no live "constraints are dropped" or "manifest collector removed" claim.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Cite drift / issues:**

### Phase 2 Completion
**Completed:**
**Recount result (families / total reqs / distinct test files):**
**Issues:**

### Phase 3 Completion
**Completed:**
**Judgment spot-read (claims sampled → verdict):**
**Issues:**

### Phase 4 Completion
**Completed:**
**Cite re-grep result:**
**Durable-page location chosen:**

### Phase 5 Completion
**Completed:**
**Cite re-grep result:**

### Phase 6 Completion
**Completed:**
**py_compile result:**

### Phase 7 Completion
**Completed:**
**BACKLOG item id:**

---

**Status**: Draft → In Progress → Complete
