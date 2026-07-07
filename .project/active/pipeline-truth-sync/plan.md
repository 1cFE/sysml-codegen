# Implementation Plan: agentic-mbse Sync — Guidance, Validation, Companion Audit (PIPELINE-TRUTH Item 9)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06

## Source Documents

- **Spec (the contract — the 18-row consolidated impact table IS the work list):**
  `.project/active/pipeline-truth-sync/spec.md`
- **Prior-epic template (followed here):**
  `.project/active/validation-sync/{plan,close-out}.md` +
  `.project/active/AGENTIC_MBSE_PR_BODY.md` (consolidated-impact-list + traceability-table
  + companion-PR-body pattern).
- **Epic Item 9 + cross-cutting R1/R2:** `.project/backlog/epic_pipeline_truth.md`.
- **Contract the check/docs mirror:** `docs/architecture/modeling-assumptions.md`
  (§5 retyping, §8 constraints, V1–V11).

There is **no design.md** — the epic budgets spec + plan + execute only. Component detail
lives in the spec's 18-row table (D1–D4, C7, V1–V3, R-*, S-F*, A1/A2, I5). This plan does
not restate those rows; it sizes them, sequences them under the scope guard, and says how
each is proven. **Read a row's spec entry before building it.**

## Two repos, one item

The execute session works in **two trees** and never writes across a boundary it can't reach
(spec §Filing homes):

- **`/home/reid/1cfe/agentic-mbse`** (branch `pipeline-truth-item4`, already carrying Item 4's
  four commits — Decision B1) — the C7 check + its two fixtures, MODELING_GUIDE /
  `docs/patterns/` / sysml-conventions edits, the R-C8 keep-filed / R-VENDOR decline / R-F6
  verify, and the A1/A2 audit fixes-if-small. The companion PR is opened from here.
- **`/home/reid/1cfe/sysml-codegen`** (this repo, branch `pipeline-truth-epic`) — every
  artifact: this plan, the companion-audit evidence note, the S-F3/S-F4/S-F5 filings in
  `.project/backlog/BACKLOG.md`, the close-out with the 18-row traceability table, the
  companion-PR body draft, and `CURRENT_WORK.md`. The sysml-codegen fixture corpus under
  `tests/fixtures/` is the **read-only cross-repo acceptance target**.

**This planning session could not read agentic-mbse** — its git is un-runnable in this
non-interactive sandbox (memory `agentic-mbse-repo-path` / `orchestrated-run-gotchas`; spec
Open Questions #1). The runner layout, check-function naming, C7 build site, negative-fixture
format, and `docs/patterns/` structure are **assumed** from the prior-epic close-out and PR
body. **Phase 0 confirms them live before any code is written.** If Phase 0 contradicts an
impact-list assumption, surface it before building.

**Settled facts (orchestrator-verified — do not re-litigate):** PR #7 (`upstream-findings-sync`)
is OPEN/unmerged and stays the human's to merge — the plan does **not** wait on it (B1's
base-then-retarget handles it). Item 4's four commits (`64a097e`, `cc64b1d`, `bc24ae3`,
`bc196df`) are on `pipeline-truth-item4`. Canonical checkout is `/home/reid/1cfe/agentic-mbse`.

---

## Implementation Strategy

**Phasing rationale.** The spec's scope guard sets a hard ordering and this plan obeys it:
survey the unread repo first, land the one must-land check (C7) and the headline doc (D1),
then the cheap docs/verifies, then the dispositions, then the bounded audit, with the
close-out last — filing throughout. C7 is the only real build and the only real risk (the
prior epic **filed** it precisely because its trigger boundary is subtle — close-out
`ITEM-SYNC-C7`), so it comes first and gets the first proof point. Docs, dispositions, and
the audit are cheap-to-bounded and land regardless.

**Critical path:**
Phase 0 (confirm structure + record gates) →
Phase 1 (**C7** check + fixtures + **D1** headline doc — the must-land floor) →
Phase 2 (D2/D3/D4/I5 docs + V1/V2/V3 skill sweep & verifies) →
Phase 3 (R-PR7/R-C8/R-F6/R-VENDOR + S-F3/S-F4/S-F5 dispositions — a recorded decision each) →
Phase 4 (companion audit A1/A2 → evidence note) →
Phase 5 (cross-repo acceptance + close-out: 18-row traceability, BACKLOG, PR body, CURRENT_WORK).

**First proof point:** end of Phase 1 — one agentic-mbse test run shows C7 **fires** on the
`attribute :>> attr = <expression>` negative fixture and stays **silent** on the bare
`:>> attr = <literal>` form (the epic-R1 fires-on-shape + silent-on-clean discipline, applied
cross-repo), while the plant fixtures (`plant_values`, `plant_value_shapes`) still pass L1–L6
unchanged. That is the epic's success gate in miniature.

**Scope guard (HARD — spec §Scope guard).**
- **Must-land:** **C7** (WARN + negative + silent-on-clean fixture), **D1** (whole-plant value
  idiom doc), **the 18-row traceability table** (SC-1). These land or the item is not done.
- **Expected (cheap):** D2/D3/D4/I5 docs; V1/V2/V3 verifies; the R-* and S-F* dispositions
  (recording a decision is cheap); the A1/A2 audit verdicts.
- **May file if a row balloons:** an audit finding whose fix needs a structural change files as
  an agentic-mbse backlog item; a doc section that balloons files its remainder. **C7 does not
  get filed** — it is this item's whole reason for existing; if its boundary is hard, spend the
  time (Phase 1 test-first collapses that risk), don't defer.

**Test-first, here.** The unit of test-first work is the **negative fixture**: author the
`attribute :>> attr = <expression>` trap shape, assert the runner does **not** yet WARN, then
build C7 until it WARNs on that shape and stays silent on the bare-literal form. No check lands
without its fixture and its silent-on-clean counterpart (epic R1/R2, HARD).

**Suite green at every phase close (R2 pair).** agentic-mbse's own suite passes at the close of
Phases 1–4; the Phase-0 baseline is recorded so a regression is visible. Cross-repo acceptance
(run_all_checks over the sysml-codegen corpus, no plant-fixture regression) is re-checked at
each check-touching phase and is HARD at Phase 5.

---

## Phase 0: Survey agentic-mbse structure + record the gate baseline

### Goal
Replace every "assumed" in the impact list with a confirmed fact about the real repo, and
record the agentic-mbse gate baseline, before a line of C7 code is written. This is Phase 0
precisely because the spec session was sandbox-pinned to sysml-codegen (spec Open Questions #1).

### Assumption Under Test
That the repo is as the prior-epic close-out left it: runner
`agentic_mbse.validation.runner.run_all_checks` over L1–L6; C7's silent-drop is mirrored at a
locatable validator site; fixtures live under `tests/fixtures/item12/` (or a sibling); the
whole-plant docs target `docs/patterns/` + `modeling_project/MODELING_GUIDE.md` +
`claude/skills/sysml-conventions/`; and the prior-epic `08cd595` filing carries `ITEM-SYNC-C7`,
`ITEM-SYNC-C8`, and the syside vendor note.

### Survey checklist (read-only; produces a short findings note in the execute log / Phase-0 completion)
- [ ] **Confirm the settled facts live:** `gh pr view 7` state (OPEN/MERGED); `git log
  pipeline-truth-item4` shows the four Item-4 commits at tip over base `7f77510`.
- [ ] **Record the gate baseline:** run agentic-mbse's own suite (prior epic:
  `uv run --env-file .env pytest tests/`; confirm the exact command + `.env`/license validity)
  and record pass/skip counts, `ruff`, `mypy` new-error count **at `pipeline-truth-item4` tip**.
- [ ] **Locate C7's build site.** The shape `attribute :>> attr = <expression>` is silently
  dropped by codegen's `hierarchy_resolver._extract_single_redefinition` (scans only
  ReferenceUsage). Find where an L-level validator can *see* an AttributeUsage redefinition with
  an expression RHS — the mirror check site (likely `level6_architecture.py` or the redefinition
  path). Confirm how a check emits a WARN and registers a `ValidationCode`.
- [ ] **Confirm the fixture convention** — `tests/fixtures/item12/` layout (`library/`+`designs/`),
  and whether C7 can point at a sysml-codegen shape (`plant_value_shapes` carries the non-float /
  enum-valued shape one hop from the expression-RHS form) or must carry a mirror fixture (spec
  Open Questions — "Negative-fixture reuse").
- [ ] **Confirm the doc surfaces** the D-rows edit: `docs/patterns/plant-idiom.md` (Item-12
  landed it — D1 extends it), `docs/patterns/semantic-operators.md` (D5 from Item 12 pairs with
  C7), `modeling_project/MODELING_GUIDE.md`, the sysml-conventions skill
  (`SKILL.md` + `references/stencils.md`).
- [ ] **Confirm the prior-epic filings exist** in agentic-mbse's backlog (`08cd595`):
  `ITEM-SYNC-C7`, `ITEM-SYNC-C8`, the vendor note — so R-C8/R-VENDOR dispose against a real record.
- [ ] **Confirm A1/A2 probe targets:** `extract_feature_refs` (the binding-extraction primitive)
  and `str(direction)` (parameter-direction keying) exist where the spec says.

### Validation
- [ ] Findings note written; each impact-list assumption marked confirmed or corrected.
- [ ] Gate baseline recorded (suite counts, ruff, mypy) — the regression yardstick for Phases 1–4.
- [ ] **Gate:** if a correction changes C7's size or moves its build site, state the new size and
  confirm it still fits the guard before Phase 1. If a floor assumption breaks (C7 unbuildable at
  the located site, as C1 broke in the prior epic), **STOP and surface it** before building.

**What we know after this phase:** the real shape of every surface the next four phases touch,
and the number a Phase-1 regression would move.

---

## Phase 1: C7 (the must-land check) + D1 (the headline doc)

### Goal
Land the one unbuilt check (the D-F expression-RHS warning) with its negative fixture and its
silent-on-clean fixture, and the whole-plant value idiom doc the epic exists to enable. If the
day runs out, these two are what got done.

### Assumption Under Test
That C7's trigger boundary is a small check-plus-fixture against the site Phase 0 located — it
WARNs on an **AttributeUsage** redefinition carrying an **expression** RHS, and does **not**
fire on the supported bare `:>> attr = <literal>` (D1 mechanism b) nor on the ReferenceUsage
bare-`:>>` form. This is the exact boundary the prior epic filed C7 to avoid rushing (close-out
`ITEM-SYNC-C7`): get it wrong and C7 reintroduces the "fires on a supported subset" defect the
epic exists to remove.

### Test Stencil (negative fixture first — write this before the check)
```
# Fires-on-shape: attribute :>> with an EXPRESSION rhs is silently dropped by codegen → WARN.
run_all_checks(item9/attr_redef_expr)   → finding(WARN, code="…ATTR_REDEF_EXPR_DROPPED")
# Silent-on-clean #1: the supported bare :>> literal override (D1 mechanism b) must NOT fire.
run_all_checks(item9/attr_redef_literal) → no ATTR_REDEF_EXPR_DROPPED finding
# Silent-on-clean #2: the plant idiom the epic enables passes L1–L6 unchanged.
run_all_checks(plant_values)             → L1–L6 unchanged vs Phase-0 baseline
run_all_checks(plant_value_shapes)       → L1–L6 unchanged vs Phase-0 baseline
```

### Changes Required (see spec rows C7, D1 for full detail — do not restate)
- [ ] **C7** — the WARN check at the Phase-0 site. Spec row C7. Fires on AttributeUsage-`:>>`
  with expression RHS; silent on the bare-literal and ReferenceUsage forms. New `ValidationCode`.
  Discharges the prior epic's filed `ITEM-SYNC-C7`. *(agentic-mbse, `pipeline-truth-item4`.)*
- [ ] **C7 fixtures** — `attr_redef_expr` (negative, fires) + `attr_redef_literal`
  (silent-on-clean), in the Phase-0-confirmed fixture dir. Point at `plant_value_shapes`'
  non-float shape if the convention allows reuse; else author the mirror pair.
- [ ] **D1** — the whole-plant value idiom doc: four mechanisms (a/b/c/d), the precedence rule
  (usage override > specialized-def `:>>` > base def), entry-point QN-keying (rename-per-consumer
  collapses to one parameter; one attr → N consumers is one channel), LITERAL-only propagation
  (CHAIN/EXPRESSION falls to the uncovered-parameter diagnostic, not a silent drop). Anchors on
  the landed fixtures: `plant_values` shapes a/b/c/d + the fusion-tea vendored models as the real
  exemplar, plus `plant_value_shapes`, `spec_chain_twolevel`. Extends the Item-12
  `docs/patterns/plant-idiom.md`. Spec row D1. *(agentic-mbse.)*

### Validation
**Automated (agentic-mbse suite + cross-repo acceptance):**
- [ ] C7 negative fixture WARNs its expected code; the two silent-on-clean fixtures do **not** fire.
- [ ] `run_all_checks` on `plant_values` / `plant_value_shapes` unchanged vs the Phase-0 baseline
  (no L1–L6 regression — C7 is silent on the supported subset).
- [ ] agentic-mbse own suite green (≥ baseline + the new C7 tests); ruff clean; mypy 0 new errors.

**Manual:**
- [ ] D1 renders; every referenced fixture (`plant_values`, `plant_value_shapes`,
  `spec_chain_twolevel`, the fusion-tea vendored exemplar) is confirmed present.

**What we know after this phase:** the one silent-drop shape now WARNs before generation without
flagging anything codegen accepts, and the headline teaching surface exists. First proof point met.

---

## Phase 2: Teaching-surface docs (D2/D3/D4/I5) + the skill sweep (V1/V2/V3)

### Goal
Make MODELING_GUIDE / `docs/patterns/` / sysml-conventions match the newly supported subset, and
run the load-bearing sweep (V2) — the epic's "nothing else teaches or checks a pattern codegen
accepts" gate. All *(agentic-mbse, `pipeline-truth-item4`)* except the V3 no-op record.

### Assumption Under Test
That D2/D3/D4/I5 are additive doc content against the section structure Phase 0 confirmed, and
that V2 finds nothing else stale now that Items 2/4/5 changed the accepted set. If V2 finds a
surface teaching a now-rejected pattern (or checking a now-accepted one), that's the point of the
sweep — fix it inline; if large, log and file.

### Changes Required (see spec rows — reference fixtures are in-repo)
- [ ] **D2** — secondary supported-subset shapes with observed labels (CORRECT vs DEGRADED), teach
  the CORRECT, document the two DEGRADED as known-incomplete. Reference `plant_value_shapes`. Spec D2.
- [ ] **D3** — keep cross-part chains shallow (multi-hop dot chain TRUNCATES `source_path`).
  Reference `deep_cross_scope_probe`; pairs with the Item-5 D3-2 loud-reject. Spec D3.
- [ ] **D4** — subtype-aware validation semantics teaching note **+ VERIFY** the Item-4 8-row
  decision table is published in the adapter docs (Item 4 committed it — `bc196df`; do not redo,
  R2/D4). Modeler-facing note: assert-shaped constraints are now visible to the drop report + L4/L6.
  Spec D4.
- [ ] **I5** — derive Item 5's deferred modeler-facing diagnostics from its spec/plan/audit and
  fold into D2/D3: non-float entry points (bool/string/enum) now diagnosed (`plant_value_shapes`
  `wall`); multi-hop loud-reject (D3-2); aggregation operator-map (`^` no longer silently XORs).
  Guidance, not new checks. Spec I5 (derive; do not invent — read Item 5's landed artifacts).
- [ ] **V1** — spot-check `references/stencils.md` still reads as the committed inline-`return`
  form (not body-assignment). A read, not a re-verification. Spec V1.
- [ ] **V2** — sweep the whole sysml-conventions skill + `docs/patterns/` for any surface teaching
  a pattern codegen now rejects, or checking one it now accepts — against the **new** accepted set
  (whole-plant idiom, subtype-aware constraints, Item-5 loud shapes). Fix inline; file if large.
  **The load-bearing gate.** Spec V2.
- [ ] **V3** — record Item 3 = no new agentic-mbse impact (no-op row kept so the trail is complete).
  Spec V3. *(recorded in the close-out; no agentic-mbse write.)*

### Validation
- [ ] Each D-row renders and points at a real in-repo reference fixture.
- [ ] D4: the Item-4 decision table is confirmed published (VERIFY leg); the modeler note added.
- [ ] V1: stencils.md confirmed as the inline form (note the line range).
- [ ] V2: sweep complete — either "nothing else stale" recorded, or each find fixed/filed.
- [ ] agentic-mbse own suite still green (docs don't touch tests, but the D4 VERIFY re-runs clean).

**What we know after this phase:** the teaching surface matches the supported subset and the skill
has been swept end-to-end — the "nothing else teaches a broken pattern" gate is closed.

---

## Phase 3: Verifies + dispositions (R-* residue, S-F* SYNC concerns)

### Goal
Give every prior-epic residue thread and every SYNC-F* concern a **recorded decision** — verified
closed, kept filed, or declined — with nothing silently dropped. Spec §B4 gives the defaults;
this phase confirms each against the live repo and records the final call.

### Assumption Under Test
That the spec's recommendations hold once checked live: R-C8 keep-filed (codegen SC-4 backstop),
R-VENDOR decline (evaluation-time, no codegen path), R-F6 still-correct after Item-4's validator
changes, S-F3/S-F4 keep-filed (no consumer), S-F5 already covered by an Item-5 test. Any that
doesn't hold gets the opposite decision — and it's recorded either way.

### Rows (each → a recorded decision; filing home noted)
- [ ] **R-PR7** — record PR #7 OPEN/MERGED status (`gh pr view 7`). If open, it stays the human's;
  do **not** merge. *(recorded in close-out.)*
- [ ] **R-C8** — two-names-one-identifier warning. **Keep filed** (Item-5 SC-4 sanitizer-injectivity
  fails loudly in codegen — the backstop exists); build the pre-warn only if it's a small
  check-plus-fixture. Record the decision. *(agentic-mbse backlog `ITEM-SYNC-C8`.)*
- [ ] **R-F6** — static-expression false-FAIL fix (`49c7b7a`): verify `check_static_expressions`
  still exempts same-part owned-sibling FORMULA refs while firing on calc-output-in-arithmetic /
  self-ref / dotted paths **after Item-4's validator changes**. Confirm closed. *(agentic-mbse.)*
- [ ] **R-VENDOR** — syside self-named-binding recursion note. **Decline the Sensmetry filing**
  (evaluation-time syside behavior; extraction is finite/degenerate — Item 8 probe exit 0; no
  codegen path affected). Keep the backlog note as the durable record. Record the decision.
  *(agentic-mbse backlog.)*
- [ ] **S-F5** — positive unresolvable-warning test. **Verify first:** read Item 5's landed tests;
  if one already asserts an unresolvable ref emits its warning (INV-6 leg), discharge S-F5; else
  add opportunistically if cheap, or keep filed. Record which. *(this-repo BACKLOG + close-out.)*
- [ ] **S-F3** — Shape-B leaf-collision filename edge. **Keep filed** (no model hits it). Record.
  *(this-repo `.project/backlog/BACKLOG.md`.)*
- [ ] **S-F4** — redefinition / design_override name surfacing. **Keep filed** (no consumer).
  Record. *(this-repo BACKLOG.)*

### Validation
- [ ] Each of the seven rows has a one-line recorded decision with its evidence and filing home.
- [ ] R-F6's verification re-runs its fixtures green under the current validators.
- [ ] S-F3/S-F4/(S-F5 if filed) written into this repo's `BACKLOG.md`; R-C8/R-VENDOR confirmed
  present in agentic-mbse's backlog (no new cross-repo write the session can't reach).
- [ ] agentic-mbse own suite still green.

**What we know after this phase:** every cross-repo thread from both epics is closed, kept-filed,
or declined — with a decision on record, none dropped.

---

## Phase 4: The companion audit (A1, A2) → evidence note

### Goal
Audit the two agentic-mbse primitives that sysml-codegen's extraction bottoms out in, and write a
**verdict per primitive** (covered / gap-found-and-fixed / gap-found-and-filed) — not a silent
pass (spec NEED). Prior-epic style: the probe output is the evidence.

### Assumption Under Test
That both primitives cover the shapes codegen relies on (so the expected verdict is "covered"),
and that any gap is small enough to fix here — else it files as an agentic-mbse backlog item (guard).

### Test Stencil (probe → recorded output, per primitive)
```
# A1 — extract_feature_refs traversal coverage. Feed each reference shape codegen relies on:
extract_feature_refs(multi_segment_chain)  → does it reach every segment? (D3 truncation context)
extract_feature_refs(self_named_binding)    → traversed, not dropped?
extract_feature_refs(cross_part_ref)        → traversed?
#   A gap here is a silent-drop root. Verdict: covered / gap-fixed-small / gap-filed.

# A2 — str(direction) repr stability. codegen keys param direction off the stringified repr:
str(direction) for in/out params across shapes → stable "in"/"out"? no "<Direction.IN: …>" drift?
#   Verdict: stable / drift-found-and-fixed / drift-found-and-filed.
```

### Changes Required
- [ ] **A1** — probe `extract_feature_refs` over multi-segment feature chains, self-named
  bindings, cross-part refs. Write the verdict. Fix-if-small (small = a contained traversal patch
  with a fixture), else file to agentic-mbse backlog. Spec A1. *(agentic-mbse.)*
- [ ] **A2** — probe `str(direction)` repr stability across syside versions/shapes. Write the
  verdict. Fix-if-small (e.g. normalize the keying), else file. Spec A2. *(agentic-mbse.)*
- [ ] **Evidence note** — `.project/active/pipeline-truth-sync/companion-audit.md` (this repo):
  the two probe commands, their output, and the per-primitive verdict.

### Validation
- [ ] `companion-audit.md` exists with a written verdict per primitive (no silent pass).
- [ ] Any A1/A2 fix ships with a fixture and leaves the agentic-mbse suite green; any filed gap
  is logged with its reason (→ a Phase-5 traceability row + agentic-mbse backlog).

**What we know after this phase:** the two silent-drop-root primitives are audited with evidence —
covered, fixed, or filed, none assumed.

---

## Phase 5: Cross-repo acceptance + close-out

### Goal
Prove both acceptance gates green, then write the close-out that makes the R2 trail complete:
all 18 impact-list rows reported done or filed (zero silently dropped), the companion-PR body
draft, and CURRENT_WORK updated.

### Assumption Under Test
That every one of the 18 rows maps to a disposition with evidence (the table is the contract, so
coverage is expected — the traceability table confirms it), and that no filing crosses a boundary
its session can't reach (spec §Filing homes pre-resolved this).

### Cross-repo acceptance (HARD — both green)
- [ ] agentic-mbse's own test suite passes (≥ Phase-0 baseline + new C7/audit tests); ruff clean;
  mypy 0 new errors.
- [ ] `run_all_checks` over the sysml-codegen fixture corpus — the plant fixtures pass L1–L6 with
  no regression vs the Phase-0 baseline; the only L6 change is C7's WARN on its negative fixture.

### Close-out deliverables
- [ ] **18-row traceability table** (in `close-out.md`): every row (D1–D4, C7, V1–V3, R-PR7/R-C8/
  R-F6/R-VENDOR, S-F5/S-F3/S-F4, A1/A2, I5) → disposition → evidence. **Zero rows silently
  dropped** (SC-1). A reader can trace any per-item recording to a row and a disposition.
- [ ] **S-F3/S-F4/(S-F5 if filed) → `.project/backlog/BACKLOG.md`** (this repo) with their recorded
  decisions.
- [ ] **Companion-PR body draft** — `.project/active/pipeline-truth-sync/AGENTIC_MBSE_PR_BODY.md`,
  prior-epic pattern, covering **Item 4 + Item 9 commits together** (B1: one PR for the epic's
  agentic-mbse work). Enumerate Item-4's four commits (`64a097e`/`cc64b1d`/`bc24ae3`/`bc196df`)
  and Item-9's commits (C7+D1, D2/D3/D4/I5, dispositions, audit). **PR base per B1:** against
  `upstream-findings-sync` while PR #7 is open (diff shows only epic work); retarget to `main`
  once #7 merges; base `main` if #7 is already merged. Draft only — **do not create/merge the PR**
  (the human's call; Non-Goal).
- [ ] **CURRENT_WORK.md** updated (this repo): Item 9 status, both gate results, disposition of
  every row.

### Validation
- [ ] Every one of the 18 rows appears in the traceability table with a disposition and evidence.
- [ ] Every FILE row written into a repo its session can reach (S-F* here; R-C8/R-VENDOR/any audit
  gap in agentic-mbse backlog).
- [ ] Both acceptance gates green and recorded.
- [ ] The PR body draft enumerates both items' commits and states the B1 base/retarget rule.

**What we know after this phase:** the validated-subset contract is enforceable again — a model
the auditor passes is a model codegen accepts — and every cross-repo thread from two epics is
closed or explicitly re-filed, with nothing dropped.

---

## Environment Setup

**See CLAUDE.md** for sysml-codegen commands. Two-tree specifics:

- **agentic-mbse** (`/home/reid/1cfe/agentic-mbse`, branch `pipeline-truth-item4`): own test
  command confirmed + baseline recorded in **Phase 0** (prior epic: `uv run --env-file .env
  pytest tests/`; license via `.env`). Do **not** commit unless instructed; do **not** create or
  merge the companion PR (orchestration; Non-Goal).
- **sysml-codegen** (this repo, branch `pipeline-truth-epic`): fixture corpus is read-only
  acceptance input; only `.project/active/pipeline-truth-sync/*`, `.project/backlog/BACKLOG.md`,
  and `CURRENT_WORK.md` are written here.
- **Cross-repo validator run:** `agentic_mbse.validation.runner.run_all_checks` against
  `tests/fixtures/{plant_values,plant_value_shapes,spec_chain_twolevel,deep_cross_scope_probe,…}`
  — the Item-8 invocation pattern, no L1–L6 regression on the plant fixtures.

---

## Risk Management

| Risk | Phase | Mitigation |
|------|-------|------------|
| agentic-mbse structure differs from the prior-epic-derived assumptions | 0 | Phase 0 is a read-only survey with a gate: correct sizes before building; STOP + surface if the C7 site breaks (as C1 broke last epic). |
| C7's trigger boundary is subtle — reintroduces the "fires on a supported subset" defect | 1 | Test-first on both silent-on-clean fixtures (bare-literal + plant idiom) before the check lands; C7 is NOT fileable, so spend the time here. |
| An audit gap (A1/A2) needs a structural fix | 4 | Guard: fix-if-small with a fixture, else file to agentic-mbse backlog — logged, not dropped. |
| A doc section (D1) balloons | 1,2 | Guard: file the overflow rather than force-fit; D1's must-land core is the four mechanisms + precedence + QN + LITERAL rule. |
| PR #7 merges/rebases mid-item | 5 | B1 base-then-retarget: draft PR against `upstream-findings-sync` now, retarget to `main` on merge; do not wait on #7. |
| A disposition needs a repo the session can't reach | 3,5 | Filing-homes split: S-F* here; R-C8/R-VENDOR/audit-gaps in agentic-mbse backlog — every filing is reachable. |

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 0 Completion
**Completed:** [Timestamp]
**Findings:** [Each impact-list assumption confirmed/corrected; gate baseline recorded]
**Deviations:** [...]

### Phase 1 Completion
[Same structure]

### Phase 2 Completion
[Same structure]

### Phase 3 Completion
[Same structure]

### Phase 4 Completion
[Same structure]

### Phase 5 Completion
[Same structure]

---

**Status:** Draft → In Progress → Complete
