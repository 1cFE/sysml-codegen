# Implementation Plan: agentic-mbse Sync — Guidance & Validation (Item 12)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06

## Source Documents

- **Spec (the contract — the consolidated impact table IS the work list):**
  `.project/active/validation-sync/spec.md`
- **Spec review + resolutions:** `.project/active/validation-sync/spec-review.md`
- **Epic Item 12 + cross-cutting R2:** `.project/backlog/epic_upstream_findings.md`
- **Contract the checks mirror:** `docs/architecture/modeling-assumptions.md`
  (§3 operators/EXPOSE, §5 retyping, §8 constraints, Validation Rules V1–V11)

There is **no design.md** — the epic budgets spec + plan + execute only. Component
detail lives in the spec's impact table (rows C1–C8, D1–D8, V1–V2, F1–F5). This plan
does not restate those rows; it sizes them, sequences them under the scope guard, and
says how each is proven. Read a row's spec entry before building it.

## Two repos, one item

The execute session works in **two trees** and never writes across a boundary it can't reach:

- **`~/1cfe/agentic-mbse`** (branch `upstream-findings-sync`, already carries the A-2
  stencil fix at `6dbdf1b`) — all checks, negative fixtures, MODELING_GUIDE /
  sysml-conventions edits, and the F1/F2 backlog filings + the syside vendor note.
- **`~/1cfe/sysml-codegen`** (this repo, branch `upstream-findings-epic`) — the close-out
  artifacts: the traceability table, the F3/F4/F5 filings in `.project/backlog/BACKLOG.md`,
  and `CURRENT_WORK.md`. The sysml-codegen fixture corpus under `tests/fixtures/` is the
  **read-only cross-repo acceptance target** — the updated validators run against it.

**This planning session could not read agentic-mbse.** Its runner layout, check-function
naming, negative-fixture format, `references/stencils.md` line range, and MODELING_GUIDE
section structure are all **assumed** from the epic floor and the per-item recordings.
Phase 0 confirms them before any code is written. If Phase 0 contradicts an impact-list
assumption, surface it before building (spec Open Questions #1).

---

## Implementation Strategy

**Phasing rationale.** The spec's scope guard sets a hard ordering and this plan obeys it:
survey the unread repo first, land the four non-fileable checks that caught the traps that
actually bit fusion-tea, then the fileable checks (build-or-file per size), then docs, with
filing throughout. Docs and filings are cheap and land regardless; the risk is all in the
checks against an unconfirmed runner, so the checks come first and the must-land four come
first among those.

**Critical path:**
Phase 0 (confirm structure) → Phase 1 (C1, C3, C2a, C4 + fixtures — the HARD floor) →
Phase 2 (C5, C6, C2b, C7, C8 — build or FILE) → Phase 3 (D1–D8 docs + V1/V2 skill sweep) →
Phase 4 (cross-repo acceptance + close-out: traceability, F1–F5 filings, vendor note).

**First proof point:** end of Phase 1 — a single agentic-mbse test run shows the four
non-fileable checks each FAIL/WARN on their negative fixture and each catch their trap on
the WI-014 toy / ife_plant shapes, while L1–L5 well-formedness on those fixtures still
passes. That is the epic's success gate in miniature.

**Scope guard (HARD — from spec §Scope guard).** Must-land, non-fileable: **C1** (self-named
FAIL), **C2a** (return-style output update + anonymous-return FAIL), **C4**
(calc-bearing-no-instantiation FAIL), **C3** (constraint WARN). The guard MAY file C5, C6,
C2b, C7, C8 — but never those four. C6 is the named risk: if it needs a structural rework of
the L6 architecture check rather than a scoping tweak, file it. A doc section that balloons
files too. The plan's Phase-2 sizing pass makes each build-vs-file call against the real
runner; every FILE decision is logged, never silent.

**Test-first, here.** The unit of test-first work is the **negative fixture**: author the
trap shape, assert the runner does NOT yet catch it (or mis-catches it), then implement the
check until the fixture FAILs/WARNs exactly. No check lands without its fixture (R2, HARD).

**Cross-repo acceptance (runs at each check phase, hard at Phase 4).** Two gates, both green:
1. agentic-mbse's **own** test suite passes (its conventions — confirmed in Phase 0).
2. The updated validators run against sysml-codegen's fixture corpus
   (`agentic_mbse.validation.runner.run_all_checks` on `tests/fixtures/{wi014_toy,ife_plant,
   self_named_binding_trap,…}` — the Item 8 invocation) and produce the expected
   FAIL/WARN/PASS per fixture, with **no regression** on the L1–L5 well-formedness the three
   plant fixtures already pass.

---

## Phase 0: Survey the agentic-mbse validation framework

### Goal
Replace every "assumed" in the impact list with a confirmed fact about the real repo, before
a line of check code is written. This is Phase 0 precisely because the spec session was pinned
to sysml-codegen and could not read agentic-mbse (spec Open Questions #1).

### Assumption Under Test
That agentic-mbse's runner is `agentic_mbse.validation.runner.run_all_checks` over a 6-level
(L1–L6) structure, that negative fixtures have a discoverable home and format, and that the
sysml-conventions skill + MODELING_GUIDE have the section structure the D-rows target. If any
is false, the impact-list check designs need re-sizing before Phase 1.

### Survey checklist (read-only; produces a short findings note in the execute log)
- [ ] Confirm the runner entry point and how it dispatches L1–L6 (the Item 8 session called
  `run_all_checks` — confirm signature, per-level check registration, severity model FAIL/WARN/INFO).
- [ ] Locate the **L2** binding checks (for C1) and the **L6** architecture check (for C2a/C4/C6)
  — file paths, check-function naming convention, how a check emits a finding.
- [ ] Locate the **adr002 operator-set** definition (for C5) — the operator table and where a
  static-expression scope is walked.
- [ ] Confirm the **negative-fixture convention**: do checks point at `.sysml` files, inline
  strings, or a fixtures dir? Can they point at sysml-codegen's `tests/fixtures/` shapes, or
  must agentic-mbse carry mirror fixtures in its own tree? (spec Open Questions — "Negative-fixture reuse".)
- [ ] Confirm agentic-mbse's **own test convention** and the command to run its suite green.
- [ ] Confirm `references/stencils.md` teaches inline `return <r> : Real = <expr>` /
  `out attribute <r> : Real = <expr>` (V1 spot-check target — note the exact line range).
- [ ] Confirm the **MODELING_GUIDE / sysml-conventions section structure** the D-rows will edit
  (plant idiom, retyping, quoted names, operators, constraints, EXPOSE).

### Validation
- [ ] Findings note written; each impact-list assumption marked confirmed or corrected.
- [ ] **Gate:** if any correction changes a must-land check's size (C1/C2a/C3/C4), state the
  new size and confirm it still fits before Phase 1. If a correction breaks a floor assumption,
  STOP and surface it (spec: "surface it before building").

**What we know after this phase:** the real shape of every surface the next three phases touch.

---

## Phase 1: The four non-fileable checks (HARD floor)

### Goal
Land the checks catching the traps that actually bit fusion-tea, each with a negative fixture,
each shown to catch its trap on the WI-014 toy / ife_plant shapes. If the day runs out, this
is what got fixed.

### Assumption Under Test
That each of the four traps is a small check-plus-fixture against the real runner (Phase 0
confirmed the sites). C2a and C4 are the sizing risk here — they update an existing L6 output/
architecture check rather than adding a standalone one.

### Ordering (cheapest-first, per spec)
C1 and C3 already have in-repo negative fixtures (`self_named_binding_trap`; an inline
constraint usage — plant fixtures carry constraint shapes), so they land first. Then C2a
(return-style, own anonymous-return fixture), then C4 (calc-bearing-no-instantiation).

### Test Stencil (negative fixture first, per check)
```
# For each check: author/point-at the trap, assert the runner's verdict.
# C1 — self-named binding, unresolvable, at L2:
run_all_checks(self_named_binding_trap)  →  finding(level=L2, severity=FAIL, rule="self-named-binding")
# The RESOLVABLE case (self_named_rescue) must NOT fire — Item 10's rescue handles it.
run_all_checks(self_named_rescue)        →  no self-named FAIL

# C2a — anonymous return has no name → no output channel (mirrors codegen V8):
run_all_checks(anonymous_return_fixture) →  finding(level=L6, severity=FAIL, rule="anonymous-return")
# and the newly-legal forms are ACCEPTED (out attribute, named return inline+body, bare in):
run_all_checks(return_styles)            →  no output-style FAIL

# C3 — constraint usage present → not executable, dropped:
run_all_checks(model_with_inline_constraint) → finding(level=L6, severity=WARN, rule="constraint-non-exec")

# C4 — calc-bearing part def, never instantiated (plainly OR by retyping):
run_all_checks(calc_bearing_no_instantiation) → finding(level=L6, severity=FAIL, rule="no-instantiation")
# Retyped usages count as instantiation (Item 4) — a retyped instantiation must NOT fire:
run_all_checks(retype_model)             →  no no-instantiation FAIL
```

### Changes Required (see spec rows for full detail)
- [ ] **C1** — L2 self-named-binding FAIL. Spec row C1. Negative fixture: `self_named_binding_trap`
  shape (in-repo). Assert the resolvable `self_named_rescue` shape does **not** fire.
- [ ] **C2a** — L6 return-style output check: accept `out attribute`, named `return`
  (inline-expr + body-assignment), bare `in`; FAIL anonymous `return`. Spec row C2a. Mirrors
  codegen V8. Own negative fixture: an anonymous-return calc def (`anonymous_return` shape exists in-repo).
- [ ] **C3** — L6 constraint non-executability WARN, pointing at modeling-assumptions §8. Spec
  row C3 + D7 (paired doc pointer). Negative fixture: a model with an inline constraint usage.
- [ ] **C4** — L6 calc-bearing-part-def-no-instantiation FAIL; "instantiated" must include
  retyped usages (Item 4). Spec row C4. Mirrors the retyping support (V9/V10). Negative
  fixture: a calc-bearing part def with no usage.

### Validation
**Automated (agentic-mbse suite + cross-repo acceptance):**
- [ ] Each of the four negative fixtures produces exactly its expected finding (severity + level + rule).
- [ ] The **negative-of-the-negative** holds: `self_named_rescue` (C1), `return_styles` (C2a),
  `retype_model` (C4) do **not** fire — the checks don't flag what codegen accepts.
- [ ] `run_all_checks` on `wi014_toy` / `ife_plant` still PASS L1–L5 (no well-formedness regression).
- [ ] agentic-mbse's own test suite green.

**What we know after this phase:** the must-land floor is enforceable — a model the auditor
FAILs on these four is a model codegen would reject, and vice versa. First proof point met.

---

## Phase 2: The fileable checks (build-or-file, sized against the real runner)

### Goal
Land C5, C6, C2b, C7, C8 as far as the guard allows. Each is desirable but fileable: if a row
exceeds a small check-plus-fixture, it drops to an agentic-mbse backlog item — logged, not dropped.

### Assumption Under Test
That most of these are scoping tweaks, not reworks. **C6 is the named risk**: if scoping the L6
architecture check to stop flagging (a) `out attribute X = <expr>` inside a calc def and (b)
quoted multi-word names needs a structural rework rather than a predicate tweak, FILE it.

### Sizing pass (do this first, before building any Phase-2 row)
- [ ] Size each of C5, C6, C2b, C7, C8 against the Phase-0 findings. For each, decide BUILD or FILE.
- [ ] Log every FILE decision with its reason (→ becomes an F-row in Phase 4, agentic-mbse backlog).

### Test Stencil
```
# C5 — adr002 operator correction: ** / functions are NOT static operators.
run_all_checks("attribute x : Real = a ** b;")   →  operator-table correct; ** flagged as non-static
run_all_checks("attribute x : Real = sqrt(a);")  →  finding(WARN, "static-function-invocation")  # steer to calc def
# C6 — the L6 false-positives must STOP firing (this is a correction, not a new catch):
run_all_checks(ife_plant)                          →  no "derived-expr-in-calc-def" flag  (was flagged, Item 8)
run_all_checks(model_with_quoted_name)             →  no "cannot derive EQN" flag          (sanitization handles it)
# C2b — body-assignment loses auto-impl until codegen's deferred capture lands:
run_all_checks(body_assignment_calc_def)           →  finding(L6, WARN, "body-assignment-impl-loss")
# C7 (candidate) — attribute :>> with expression RHS is silently dropped at extraction:
run_all_checks(attribute_redef_with_expr)          →  finding(WARN, "attribute-redef-expr-dropped")
# C8 (candidate) — two names collapsing to one Python identifier:
run_all_checks(two_names_one_identifier)           →  finding(WARN, "identifier-collision")
```

### Changes Required (see spec rows)
- [ ] **C5** — adr002 operator-set correction: fix `**`'s status in the operator table;
  function-invocation in a static expression → WARN. Spec row C5. Mirrors codegen V4. Negative
  fixtures: `= a ** b;` and `= sqrt(a);` at design-attribute scope.
- [ ] **C6** — L6 false-positive corrections (a) calc-def-internal `out attribute = <expr>`,
  (b) quoted multi-word names. Spec row C6. **The named FILE risk.** Both shapes verified on
  Item 8 fixtures (all three flagged derived-expr; toy + trap flagged quoted-name).
- [ ] **C2b** — L6 body-assignment auto-impl-loss WARN, separate check + own fixture. Spec row C2b.
- [ ] **C7** (candidate) — attribute-`:>>`-with-expression WARN. Spec row C7. Paired with doc D5.
- [ ] **C8** (candidate) — two-names-one-identifier WARN. Spec row C8. Precedes codegen's
  duplicate-path error (REQ-NC-09).

### Validation
- [ ] Each BUILT row: negative fixture fires its expected finding; the corrected checks (C6)
  stop firing on the Item-8 fixtures that previously tripped them.
- [ ] Cross-repo acceptance re-run: no regression on Phase-1 checks or L1–L5.
- [ ] Each FILED row logged with reason (carried to Phase 4 F-rows).
- [ ] agentic-mbse suite green.

**What we know after this phase:** the checking surface no longer contradicts codegen — nothing
teaches-or-checks a pattern codegen now accepts as an error (C6), and the operator set is correct (C5).

---

## Phase 3: Teaching-surface updates (D1–D8) + the skill sweep (V1, V2)

### Goal
Make MODELING_GUIDE / sysml-conventions match the supported subset, and run the load-bearing
sweep that is the epic's "nothing else teaches a broken pattern" gate.

### Assumption Under Test
That the D-rows are additive doc content against the section structure Phase 0 confirmed, and
that V2 finds nothing else stale (A-2 is already committed; V1 only spot-checks it). If V2 finds
a broken stencil, that's new work — surface it and fix inline (it's the whole point of the sweep).

### Changes Required (see spec rows D1–D8; reference fixtures are all in-repo)
- [ ] **D1** — plant-idiom patterns. Reference shapes: `ife_plant`, `spec_chain_channel`,
  `spec_chain_twolevel`, `sibling_channel_ambiguity`, `wi014_toy`. Spec row D1.
- [ ] **D2** — retyping (`part :>> driver : 'HIF Driver'`; subtype specializes base; same-QN
  redefinition). Spec row D2.
- [ ] **D3** — quoted names are fine; identifiers are derived. Spec row D3.
- [ ] **D4** — no-loops rule (register A-3), pure documentation. Spec row D4.
- [ ] **D5** — bare-`:>>` value idiom + plain-usage literal override + attribute-`:>>` warning +
  redefinition-precedence rule (usage override > specialized-def `:>>` > base def). Pairs with C7. Spec row D5.
- [ ] **D6** — EXPOSE surfacing: EXPOSE_PURE name lands on `output_aliases`, becomes
  `{instance_path}__{alias_name}.json`, surfaced name is the sanitized `python_name`; both
  shapes surface; EXPOSE_COMPUTED stays rejected. Spec row D6.
- [ ] **D7** — constraint pointer to modeling-assumptions §8. Pairs with C3. Spec row D7.
- [ ] **D8** — def-owned design attributes are supported (Item 7). One-line note alongside D2.
  Spec row D8 permits downgrade to the no-impact paragraph if the plan judges the note redundant
  — **keep it as a cheap line** so the R2 trail is complete unless it reads as pure redundancy.
- [ ] **V1** — spot-check `references/stencils.md` reads as the committed A-2 form (inline
  `return`/`out attribute`, not body-assignment). Spec row V1. A read, not a re-verification —
  A-2 is committed at `6dbdf1b`.
- [ ] **V2** — sweep the **whole** sysml-conventions skill for any other stencil/rule teaching a
  pattern codegen now rejects (or rejecting one it now accepts). Spec row V2. **This is the
  load-bearing gate.** Fix anything found inline; if a find is large, log it and file.

### Validation
- [ ] V1: stencils.md confirmed as the A-2 form (note the line range from Phase 0).
- [ ] V2: sweep complete; either "nothing else stale" recorded, or each find fixed/filed.
- [ ] D-rows: each doc section renders and points at a real in-repo reference fixture.
- [ ] A doc that balloons is filed (guard), not force-fit.

**What we know after this phase:** the teaching surface matches the supported subset, and the
skill has been swept end-to-end — the epic's "nothing else teaches a broken pattern" gate is closed.

---

## Phase 4: Cross-repo acceptance + close-out

### Goal
Prove the two acceptance gates green, then write the close-out that makes the R2 trail complete:
every impact-list row reported done or filed, every fusion-tea trap traced to a check or rule,
and every FILE row landed in a repo the writing session can reach.

### Assumption Under Test
That every SC-1..SC-11 trap maps to a C-check or D-rule (the set was designed against them, so
coverage is expected — the table confirms it), and that no filing crosses a boundary its session
can't reach (the spec's Filing-homes paragraph pre-resolved this).

### Cross-repo acceptance (HARD — both green)
- [ ] agentic-mbse's own test suite passes (its convention, from Phase 0).
- [ ] `run_all_checks` over sysml-codegen's fixture corpus produces the expected per-fixture
  verdicts with **no L1–L5 regression** on the three plant fixtures.

### Close-out deliverables
- [ ] **Traceability table** (in the close-out): impact-list row → disposition → evidence, AND
  fusion-tea RAW_LEARNINGS trap → covering check/rule. **Needs a fusion-tea-readable session**
  (spec Open Questions) — read `~/1cfe/fusion-tea` RAW_LEARNINGS, map each trap to C1–C8 / D1–D7.
  Nothing from any per-item recording silently dropped (SC-1).
- [ ] **F1 → agentic-mbse backlog** (implement session, `upstream-findings-sync`): the syside
  vendor note, recording the Item-8 finding that the self-named recursion is **evaluation-time
  syside behavior, not extraction-time** (extraction is finite/degenerate — probe exit 0). Note
  only; do not write the vendor report or contact Sensmetry. Spec row F1.
- [ ] **F2 → agentic-mbse backlog**: V11 model-side mirror check (candidate). Spec row F2.
- [ ] **F3 → this repo `.project/backlog/BACKLOG.md`**: shape-B leaf-collision filename edge. Spec row F3.
- [ ] **F4 → this repo `BACKLOG.md`**: redefinition / design_override name surfacing. Spec row F4.
- [ ] **F5 → this repo `BACKLOG.md`**: positive unresolvable-warning test (opportunistic — add
  in sysml-codegen if cheap, else file). Spec row F5.
- [ ] Any **Phase-2 FILED check** → agentic-mbse backlog with its logged reason.
- [ ] **CURRENT_WORK.md** updated (this repo): Item 12 status, gate results, disposition of every row.

### Validation
- [ ] Every impact-list row (C1–C8, D1–D8, V1–V2, F1–F5) appears in the traceability table with
  a disposition and evidence — a reader can trace any per-item recording to a row (NEED, spec).
- [ ] Every fusion-tea RAW_LEARNINGS trap maps to a check or a documented rule (NEED, spec).
- [ ] Every FILE row written into a repo its session can reach (F1/F2 agentic-mbse; F3/F4/F5 here).
- [ ] Both acceptance gates green and recorded.

**What we know after this phase:** the validated-subset contract is enforceable again, and the
R2 trail across all twelve items is closed with nothing dropped.

---

## Environment Setup

**See CLAUDE.md** for sysml-codegen commands. Two-tree specifics:

- **agentic-mbse** (`~/1cfe/agentic-mbse`, branch `upstream-findings-sync`): its own test
  convention — confirm the exact command in **Phase 0** before relying on it. Do not commit
  unless instructed (orchestration).
- **sysml-codegen** (this repo): fixture corpus is read-only acceptance input; only
  `.project/backlog/BACKLOG.md` and `CURRENT_WORK.md` are written here, in Phase 4.
- **Cross-repo validator run:** `agentic_mbse.validation.runner.run_all_checks` against
  `tests/fixtures/{wi014_toy,ife_plant,self_named_binding_trap,retype_model,return_styles,
  anonymous_return,self_named_rescue}` — the Item 8 invocation pattern.

---

## Risk Management

| Risk | Phase | Mitigation |
|------|-------|------------|
| agentic-mbse structure differs from the impact-list assumptions | 0 | Phase 0 is a read-only survey with a gate: correct sizes before building; STOP + surface if a floor assumption breaks. |
| C6 needs a structural L6 rework, not a scoping tweak | 2 | The named FILE candidate — file it if it exceeds a small check; the must-land four don't depend on it. |
| Day runs out mid-Phase-2 | 2 | Scope guard: C5/C6/C2b/C7/C8 all fileable; only the Phase-1 four are HARD. Log every FILE. |
| Traceability / vendor note need repos this session can't read | 4 | Table + F1 need a fusion-tea-readable session; F1/F2 are written from the agentic-mbse session, F3/F4/F5 from the sysml-codegen close-out — the spec's Filing-homes split guarantees reach. |
| A doc section balloons | 3 | Guard: file the overflow rather than force-fit. |
| A check flags a shape codegen accepts (the C6 defect class) | 1,2 | Every check phase asserts the negative-of-the-negative (rescue/return_styles/retype_model don't fire). |

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 0 Completion
**Completed:** — **Findings (structure confirmed/corrected):** — **Deviations:** —

### Phase 1 Completion
**Completed:** — **Actual Changes:** — **Issues:** — **Deviations:** —

### Phase 2 Completion
**Completed:** — **BUILD/FILE decisions (per row, with reason):** — **Deviations:** —

### Phase 3 Completion
**Completed:** — **V2 sweep result:** — **Deviations:** —

### Phase 4 Completion
**Completed:** — **Acceptance gates:** — **Filings landed:** — **Deviations:** —

---

**Status:** Draft → In Progress → Complete
