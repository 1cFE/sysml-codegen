# Implementation Plan: agentic-mbse Sync — Guidance, Validation, Companion Audit (PIPELINE-TRUTH Item 9)

**Status:** COMPLETE — Phases 0–5 done (agentic-mbse `fa3b706`/`1fab4d6`/`9cc7ab4`, pushed to origin; this-repo close-out landed)
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
- [x] **Confirm the settled facts live:** PR #7 OPEN (base main); the four Item-4 commits at tip over `7f77510`.
- [x] **Record the gate baseline:** `uv run --env-file .env pytest tests/` → 1238 passed, 1 skipped, 33 deselected.
- [x] **Locate C7's build site.** `level6_architecture.py`; drop is `hierarchy_resolver.py:102` (ReferenceUsage-only).
  Live probe cleanly separates AttributeUsage (dropped) from ReferenceUsage (accepted). STOP gate cleared.
- [x] **Confirm the fixture convention** — `tests/fixtures/item12/<name>/{library,designs}/`; C7 carries its own
  mirror fixtures under a sibling `item9/` (agentic-mbse cannot point at a sysml-codegen fixture path).
- [x] **Confirm the doc surfaces** — `plant-idiom.md` (D1), `semantic-operators.md` (already teaches C7's D5
  boundary), `MODELING_GUIDE.md`, `sysml-conventions/{SKILL.md, references/stencils.md}`.
- [x] **Confirm the prior-epic filings** in `.project/backlog/BACKLOG.md`: C7 (86), C8 (106), F1 vendor (58).
- [x] **Confirm A1/A2 probe targets:** `extract_feature_refs` (expression.py:119); `str(direction)` keying.

### Validation
- [x] Findings note written (above); every impact-list assumption confirmed, none corrected.
- [x] Gate baseline recorded (1238/1/33) — the regression yardstick for Phases 1–4.
- [x] **Gate:** no correction changed C7's size; the build site holds; no floor assumption broke → proceed.

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
- [x] **C7** — the WARN check at the Phase-0 site (`check_attr_redef_expression_dropped`, level6_architecture.py).
  Fires on AttributeUsage-`:>>` with expression RHS; silent on bare-literal/ReferenceUsage/attribute-literal forms.
  New `L6_ATTR_REDEF_EXPR_DROPPED`. Discharges `ITEM-SYNC-C7`. *(agentic-mbse `fa3b706`.)*
- [x] **C7 fixtures** — `item9/attr_redef_expr` (fires) + `item9/attr_redef_literal` (silent). Authored the mirror
  pair (agentic-mbse cannot point at a sysml-codegen fixture path — Open-Questions "Negative-fixture reuse" resolved).
- [x] **D1** — the whole-plant value idiom doc: four mechanisms (a/b/c/d), the precedence rule
  (usage override > specialized-def `:>>` > base def), entry-point QN-keying (rename-per-consumer
  collapses to one parameter; one attr → N consumers is one channel), LITERAL-only propagation
  (CHAIN/EXPRESSION falls to the uncovered-parameter diagnostic, not a silent drop). Anchors on
  the landed fixtures: `plant_values` shapes a/b/c/d + the fusion-tea vendored models as the real
  exemplar, plus `plant_value_shapes`, `spec_chain_twolevel`. Extends the Item-12
  `docs/patterns/plant-idiom.md`. Spec row D1. *(agentic-mbse.)*

### Validation
**Automated (agentic-mbse suite + cross-repo acceptance):**
- [x] C7 negative fixture WARNs its expected code; the silent-on-clean fixture does **not** fire.
- [x] `validate_architecture` on `plant_values` / `plant_value_shapes` / `spec_chain_twolevel` — C7 count 0;
  stash-verified n_errors unchanged (10/18/9) vs baseline (no L1–L6 regression).
- [x] agentic-mbse own suite green (1240, = baseline + 2 C7 tests); ruff clean; mypy 0 new errors.

**Manual:**
- [x] D1 renders; every referenced fixture (`plant_values`, `plant_value_shapes`,
  `spec_chain_twolevel`, the fusion-tea vendored exemplar) confirmed present.

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
- [x] **D2** — secondary shapes with observed labels (plant-idiom.md "Secondary shapes and their limits"). Spec D2.
- [x] **D3** — keep cross-part chains shallow (multi-hop dot chain truncates `source_path`). Ref `deep_cross_scope_probe`. Spec D3.
- [x] **D4** — subtype-aware note in constraints.md **+ VERIFY** `docs/subtype-enumeration-decision-table.md` published
  (Item-4 `bc196df`, confirmed present — not redone). Assert constraints now visible to drop report + L4/L6. Spec D4.
- [x] **I5** — derived from Item 5's landed artifacts, folded into the D2 section: non-float EPs diagnosed
  (`plant_value_shapes` `wall`); multi-hop loud-reject (D3-2); `^` operator-map (no longer silent XOR). Spec I5.
- [x] **V1** — `references/stencils.md:39` confirmed as the inline-`return` form. Spec V1.
- [x] **V2** — swept skill + `docs/patterns/`: **nothing else stale** (the load-bearing gate). Spec V2.
- [x] **V3** — Item 3 no new impact (recorded in close-out, Phase 5; no agentic-mbse write). Spec V3.

### Validation
- [x] Each D-row renders and points at a real in-repo reference fixture.
- [x] D4: the Item-4 decision table confirmed published; the modeler note added.
- [x] V1: stencils.md confirmed as the inline form (line 39).
- [x] V2: sweep complete — "nothing else stale" recorded.
- [x] agentic-mbse own suite still green (1240; D4 VERIFY / F6 re-run clean).

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
- [x] **R-PR7** — PR #7 OPEN (base main), stays the human's; not merged. *(recorded above + close-out.)*
- [x] **R-C8** — **Keep filed** (codegen SC-4 backstop; pre-warn needs shared sanitizer, not small). *(agentic-mbse `ITEM-SYNC-C8`.)*
- [x] **R-F6** — **Verified closed**: both F6 tests green under current validators. *(agentic-mbse.)*
- [x] **R-VENDOR** — **Decline the Sensmetry filing** (evaluation-time; extraction finite/degenerate). *(agentic-mbse `ITEM-SYNC-F1`.)*
- [x] **S-F5** — **Discharge**: covered by `chain_override_probe` loud-on-gap + V11 raise + family2 INV-6 tests. *(close-out.)*
- [x] **S-F3** — **Keep filed** (no model hits it). *(this-repo BACKLOG — Phase-5 write, not this session.)*
- [x] **S-F4** — **Keep filed** (no consumer). *(this-repo BACKLOG — Phase-5 write, not this session.)*

### Validation
- [x] Each of the seven rows has a recorded decision with evidence and filing home.
- [x] R-F6's verification re-runs its fixtures green under the current validators.
- [x] R-C8/R-VENDOR filed in agentic-mbse's backlog (`9cc7ab4`); S-F3/S-F4 keep-filed + S-F5 discharge recorded
  here for the Phase-5 close-out to file into this repo's BACKLOG.md (HARD BOUNDARY — not this session's write).
- [x] agentic-mbse own suite still green (backlog is docs; 1240 unchanged).

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
- [x] **A1** — probed `extract_feature_refs` over multi-segment chain, self-named binding, cross-part ref.
  Verdict **COVERED** (all traverse, none dropped). No fix needed. Spec A1.
- [x] **A2** — probed `str(direction)` on syside 0.8.4. Verdict **STABLE** (clean enum string; codegen substring
  keys resolve it, resilient to `<…>` drift). No fix needed. Spec A2.
- [x] **Evidence note** — `companion-audit.md` written: probe command, output, per-primitive verdict.

### Validation
- [x] `companion-audit.md` exists with a written verdict per primitive (no silent pass).
- [x] No A1/A2 fix needed (both covered); nothing filed; suite unchanged (1240).

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
- [x] agentic-mbse's own test suite passes (1240/1/33 = baseline + 2 C7 tests); ruff clean; mypy 0 new errors.
- [x] `validate_architecture` over the plant fixtures — C7 count 0; stash-verified no L6-error regression (10/18/9).

### Close-out deliverables
- [x] **18-row traceability table** in `close-out.md` — 18/18 rows → disposition → evidence, zero dropped (SC-1).
- [x] **S-F3/S-F4/S-F5 → `BACKLOG.md`** (this repo) with recorded decisions (F3/F4 keep-filed, F5 discharged).
- [x] **Companion-PR body draft** — `COMPANION_PR_BODY.md` (saved under this name per the Phase-5 instruction):
  Item-4's four commits + Item-9's three; B1 base-then-retarget stated. Draft only — PR not created.
- [x] **CURRENT_WORK.md** updated: Item 9 COMPLETE, both gate results, every disposition.

### Validation
- [x] All 18 rows appear in the traceability table with a disposition and evidence.
- [x] Every FILE row written into a reachable repo (S-F* here; R-C8/R-VENDOR in agentic-mbse backlog).
- [x] Both acceptance gates green and recorded.
- [x] The PR body draft enumerates both items' commits and states the B1 base/retarget rule.

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
**Completed:** 2026-07-06

**Gate baseline (agentic-mbse @ `pipeline-truth-item4` tip `bc196df`):**
- `uv run --env-file .env pytest tests/` → **1238 passed, 1 skipped, 33 deselected, 6 warnings in ~16s**.
- This is the regression yardstick for Phases 1–4. ruff/mypy new-error counts checked at each phase close.

**Settled facts confirmed live:**
- PR #7 (`upstream-findings-sync`) is **OPEN**, base `main`, head `upstream-findings-sync`. Stays the human's.
- The four Item-4 commits (`64a097e`/`cc64b1d`/`bc24ae3`/`bc196df`) sit at tip over base `7f77510`.

**Every impact-list assumption confirmed (none corrected):**
- **Runner:** `agentic_mbse.validation.runner.run_all_checks` over L1–L6; check functions live in
  `level6_architecture.py`, each returning `list[ValidationIssue]`, aggregated in `validate_architecture`.
- **C7 build site — STOP GATE CLEARED.** Codegen drop is `hierarchy_resolver._extract_single_redefinition`
  (`hierarchy_resolver.py:102`): `if not is_instance(member, "ReferenceUsage"): return None`. A live syside
  probe (`/tmp/c7probe`) proved the boundary is **cleanly distinguishable**:
  | shape | syside kind | is_AttributeUsage | is_ReferenceUsage | codegen |
  |---|---|---|---|---|
  | `attribute :>> a = 2.0*3.0` (expr) | AttributeUsage + OperatorExpression | True | False | **dropped** |
  | `attribute :>> b = 5.0` (literal) | AttributeUsage + LiteralRational | True | False | dropped |
  | bare `:>> c = 7.0` (literal) | ReferenceUsage + LiteralRational | False | **True** | extracted (mechanism b) |
  | bare `:>> d = 4.0+1.0` (expr) | ReferenceUsage + OperatorExpression | False | True | extracted (CHAIN/EXPR) |
  AttributeUsage and ReferenceUsage are disjoint (the `attribute` keyword is the discriminator, 1:1 with the
  drop condition). Every codegen-**accepted** `:>>` form is a ReferenceUsage → C7 fires only on AttributeUsage,
  so it cannot fire on a supported shape. **Design confirmed (Design B):** the prior-epic filing `08cd595`
  framed C7 as "attribute-`:>>`-**with-expression** WARN" with boundary "expression-vs-literal" — so C7 fires on
  AttributeUsage-`:>>` with a **non-literal** RHS; the literal AttributeUsage form (shape b) stays taught (D5),
  not checked. Literal detection mirrors codegen's `is_literal_expression` (5 literal types + NullExpression).
- **Fixtures:** `tests/fixtures/item12/<name>/{library,designs}/`. C7 fixtures go under a sibling `item9/`.
  C7 must carry its own mirror fixtures (agentic-mbse cannot point at a sysml-codegen fixture path); the
  substrate shape lives in sysml-codegen `plant_value_shapes` but the check runs on in-repo fixtures.
- **Doc surfaces:** `docs/patterns/plant-idiom.md` (D1 extends), `docs/patterns/semantic-operators.md`
  (**already teaches C7's boundary** — "attribute `:>>` with expression is DROPPED" + precedence rule, lines
  132–171; this is the D5 the filing references), `modeling_project/MODELING_GUIDE.md`,
  `claude/skills/sysml-conventions/{SKILL.md, references/stencils.md}`.
- **Prior-epic filings** in agentic-mbse `.project/backlog/BACKLOG.md`: `ITEM-SYNC-C7` (line 86),
  `ITEM-SYNC-C8` (line 106), `ITEM-SYNC-F1` vendor note (line 58, draft at
  `.project/research/20260706_syside-self-named-recursion-vendor-note.md`).
- **A1/A2/R-F6 targets:** `extract_feature_refs` at `sysml/expression.py:119`; codegen keys direction via
  `str(member.direction)` (extractor.py:381, usage_extractor.py:891) — A2 probes syside-side repr stability;
  `check_static_expressions` at `adr002.py:567` (R-F6). R-F6's tests already exist in
  `test_item12_checks.py` (`test_f6_formula_computed_attrs_not_flagged`, `test_f6_calc_output_ref_still_fires`)
  — R-F6 verification = these pass under current validators.

**Deviations:** None. No floor assumption broke; C7 fits the guard as a small check-plus-fixture at the located
site. C7's teaching (D5) already exists, so Phase 1's doc work is D1 (new whole-plant section), not C7-teaching.

### Phase 1 Completion
**Completed:** 2026-07-06 — agentic-mbse commit **`fa3b706`**.

**C7 fixture evidence (test-first, red→green):**
- Wrote `tests/fixtures/item9/attr_redef_expr/model.sysml` (one `attribute :>> gain = 2.0 * 3.0`) and
  `attr_redef_literal/model.sysml` (bare `:>> gain = 7.0` literal + bare `:>> rate = 2.0*4.0` expr +
  `attribute :>> level = 5.0` literal), plus `test_item9_checks.py`. Ran it → **red** (ImportError, check absent).
- Built `check_attr_redef_expression_dropped` (level6_architecture.py) + `L6_ATTR_REDEF_EXPR_DROPPED` code +
  aggregator/metric wiring. Ran it → **green: 2 passed**.
  - `test_c7_attr_redef_expression_warns`: exactly 1 WARN on `gain`.
  - `test_c7_bare_and_literal_redefs_do_not_fire`: 0 findings — the two bare (ReferenceUsage) forms and the
    one `attribute :>>`-literal form all stay silent.

**Design (confirmed against prior-epic filing `08cd595`):** fire on AttributeUsage `:>>` with a **non-literal**
RHS; literal AttributeUsage redefine is taught (D5), not warned. Literal detection mirrors codegen's
`is_literal_expression` (5 literal types + NullExpression).

**Gates at phase close:**
- agentic-mbse own suite: **1240 passed, 1 skipped, 33 deselected** (baseline 1238 + the 2 C7 tests). ruff clean.
  mypy: 9 pre-existing "Returning Any" errors, all outside the C7 edits → **0 new**.
- Cross-repo acceptance: `validate_architecture` over `plant_values` / `plant_value_shapes` / `spec_chain_twolevel`
  → `L6_ATTR_REDEF_EXPR_DROPPED` count **0** on all three. Stash-verified no regression: n_errors 10/18/9 identical
  with and without C7 (C7 is WARNING-only and fires 0 times, so the error set is unchanged).

**D1:** `plant-idiom.md` gained "The whole-plant value idiom (the headline)" — four mechanisms a/b/c/d, precedence
(usage `:>>` > specialized-def `:>>` > base def), QN-keying, LITERAL-only propagation; anchored on `plant_values`
(a/b/c/d + fusion-tea exemplar), `plant_value_shapes`, `spec_chain_twolevel` — all confirmed present.

**Deviations:** C7's *teaching* (D5 in semantic-operators.md) already existed from Item 12 — Phase 1 doc work was
D1 only (the new headline section), as noted in Phase 0. First proof point met.

### Phase 2 Completion
**Completed:** 2026-07-06 — agentic-mbse commit **`1fab4d6`** (docs only). Suite still green (1240).

- **D2** — `plant-idiom.md` "Secondary shapes and their limits": the CORRECT shapes (bare `default`,
  quoted enum `:>>`, quoted output param, Style-E mixed, 5-deep chain) taught; the two DEGRADED shapes
  (attribute-def nested `:>>`, inherited-attr-redefined-below) documented as known-incomplete. Refs `plant_value_shapes`.
- **I5** (derived from Item 5's landed artifacts, not invented) — folded into the same section: non-float
  entry points now diagnosed ("keep EPs float-valued", the `wall` shape); aggregation `^` maps to `**`
  (was silent bitwise-XOR). These are codegen-side diagnostics surfaced as guidance.
- **D3** — "Keep cross-part chains shallow": multi-hop dot chain truncates `source_path` to the first segment;
  keep refs one hop, surface deep values via an EXPOSE attribute. Pairs with Item-5 D3-2 loud-reject. Ref `deep_cross_scope_probe`.
- **D4** — `constraints.md` "Subtype-aware validation" note: `assert` (AssertConstraintUsage) is now visible to
  the drop report and L4/L6; requirement-side usages excluded. Points at the published
  `docs/subtype-enumeration-decision-table.md`. **VERIFY leg:** that table is present (Item-4 `bc196df`) — confirmed, not redone.
- **V1** — `references/stencils.md:39` reads `return result : Real = input_a * input_b; // inline expression`
  — the committed inline-`return` form (not body-assignment). Confirmed by read.
- **V2 (the load-bearing gate)** — swept `claude/skills/sysml-conventions/*` + `docs/patterns/*` against the new
  accepted set. **Nothing else stale.** The one risk surface (`attribute :>>` value form) is correctly taught as
  DROPPED (semantic-operators.md, Item-12 D5); the `^` hits are ASCII unit notation (`[m^2]`), not the operator;
  SKILL.md pitfalls/anti-patterns/operator list all hold. No surface teaches a now-rejected pattern or checks a
  now-accepted one; the green suite (incl. C7 + item12 negative-of-the-negative) confirms no check flags a supported shape.
- **V3** — Item 3 = no new agentic-mbse impact (recorded in the close-out, Phase 5; no agentic-mbse write).

**Deviations:** None.

### Phase 3 Completion
**Completed:** 2026-07-06 — agentic-mbse commit **`9cc7ab4`** (backlog dispositions). Suite unaffected (docs).

Each row → a recorded decision:
- **R-PR7** — PR #7 (`upstream-findings-sync`) is **OPEN**, base `main` (confirmed Phase 0). Stays the human's;
  not merged. *(recorded here + close-out.)*
- **R-C8** — **KEEP FILED.** Not a small check-plus-fixture: the pre-warn still needs a shared sanitizer to avoid
  drift against codegen REQ-NC-09 (~0.5–1 day). Item-5 SC-4 sanitizer-injectivity fail-fast is the codegen
  backstop. *(agentic-mbse backlog `ITEM-SYNC-C8` updated.)*
- **R-F6** — **VERIFIED CLOSED.** `test_item12_checks.py::test_f6_formula_computed_attrs_not_flagged` and
  `::test_f6_calc_output_ref_still_fires` both pass under the current (post-Item-4) validators — same-part FORMULA
  siblings stay exempt while calc-output-in-arithmetic still fires. *(agentic-mbse; verify-only, no change.)*
- **R-VENDOR** — **DECLINE the Sensmetry filing.** Evaluation-time syside recursion; extraction finite/degenerate
  (Item-8 probe `timeout 150` exit 0); no codegen path. Note kept as durable record. *(agentic-mbse `ITEM-SYNC-F1`.)*
- **S-F5** — **DISCHARGE.** The `unresolvable_attr_probe` fixture was absorbed by Item 9's plain-usage-override fix
  (it now resolves); the positive loud-on-gap proof is re-anchored on `chain_override_probe`
  (`test_uncovered_params.py::test_collector_pins_chain_override_probe` — unresolved calc-output ref stays LOUD;
  `::test_reconcile_raises_v11_on_wired_gap` — V11 raises), and the INV-6 silent-on-clean leg is covered by
  `test_silent_failure_family2.py` (`test_d34_clean_report_no_warn`, `test_d313_all_known_no_warn`). No new test needed.
- **S-F3** — **KEEP FILED.** No model hits the Shape-B leaf-collision filename edge.
- **S-F4** — **KEEP FILED.** No consumer needs redefinition/design_override name surfacing.

**Filing-home note (HARD BOUNDARY):** the S-F3/S-F4 keep-filed entries and the S-F5 discharge land in *this repo's*
`.project/backlog/BACKLOG.md` — a Phase-5 close-out write. This session does not touch this repo's BACKLOG.md (an
Item-7 session is concurrently editing it); the decisions are recorded here for the close-out to file. R-C8/R-VENDOR
(agentic-mbse) were filed live above.

**Deviations:** None. Every one of the seven rows has a recorded decision with evidence.

### Phase 4 Completion
**Completed:** 2026-07-06 — evidence note `.project/active/pipeline-truth-sync/companion-audit.md` (this repo).
No agentic-mbse code change (both primitives covered), so no Phase-4 agentic-mbse commit; suite unchanged (1240).

- **A1 — `extract_feature_refs`: COVERED.** Probed multi-segment chain, one-hop cross-part ref, and self-named
  `in x = x` binding — all three traverse to a **non-empty** ref set (no silent drop). The D3 `source_path`
  truncation lives on codegen's side (`extract_feature_chain_name`), not in this traversal-complete primitive.
- **A2 — `str(direction)`: STABLE.** syside 0.8.4 yields `FeatureDirectionKind.In` / `.Out` (a clean enum string,
  not an angle-bracket repr). Codegen's substring keys (`"In" in str(direction)`, extractor.py:381 /
  usage_extractor.py:891) resolve it correctly and are resilient even to a `<…>` repr — the drift A2 worried about
  cannot silently break them (it would break both repos' identical `"Out" not in direction` checks loudly).

Verdict per primitive written (no silent pass). No gap fixed, no gap filed.

**Deviations:** None.

### Phase 5 Completion
**Completed:** 2026-07-06. HARD BOUNDARY lifted (Item 7 landed + audited PASS); this-repo close-out executed.

- **18-row traceability table** — `.project/active/pipeline-truth-sync/close-out.md`. Every row (D1–D4, C7,
  V1–V3, R-PR7/R-C8/R-F6/R-VENDOR, S-F5/S-F3/S-F4, A1/A2, I5) → disposition → evidence. **18/18, zero dropped.**
- **Both acceptance gates green** (recorded in close-out): agentic-mbse suite 1240/1/33; cross-repo C7-silent
  with stash-verified no-regression (10/18/9).
- **S-F* BACKLOG filings** — appended Item-9 dispositions to this-repo `BACKLOG.md`: `SYNC-F3`/`SYNC-F4`
  keep-filed, `SYNC-F5` discharged. Item 7's `[ITEM7-F4-CUTOVER]` / `[ITEM7-MATRIX-SWEEP-RESIDUE]` untouched.
- **Companion-PR body** — `.project/active/pipeline-truth-sync/COMPANION_PR_BODY.md`: Item 4's four commits +
  Item 9's three, with the B1 base-then-retarget rule (base `upstream-findings-sync` while PR #7 open → `main` on merge).
  Draft only — PR creation stays the human's.
- **CURRENT_WORK.md** — Item 9 marked COMPLETE with both gate results and every disposition.
- **agentic-mbse branch** `pipeline-truth-item4` pushed to origin (branch only, no PR).
- **This-repo commit** (pathspec-scoped): plan + close-out + companion-audit + COMPANION_PR_BODY + BACKLOG + CURRENT_WORK.

**Deviations:** None. The plan's "traceability table in close-out.md" is honored via a dedicated `close-out.md`.

---

**Status:** Draft → In Progress → Complete
