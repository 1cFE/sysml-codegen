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
**Completed:** 2026-07-06.

**Findings (every impact-list assumption confirmed against the real repo):**
- **Runner** = `agentic_mbse.validation.runner.run_all_checks(models_path, fail_fast, specific_level, verbose)`.
  Takes a **directory** (globs `**/*.sysml`), runs L1–L6, each `validate_*(models_path)`. CONFIRMED.
- **Severity model**: `Severity.ERROR|WARNING|INFO` on `ValidationIssue(level, severity, code, message,
  element_name, location, suggestion)`. Codes are a `ValidationCode` str-enum in `sysml/types.py`.
  L6 `success = no ERROR` (WARN passes). **L2 `success = len(all_issues)==0`** — L2 fails on WARN too
  (matters for where a WARN-severity check lands; C1 is a FAIL so unaffected).
- **C1 site** = `level2_structure.py` (`validate_structure`). **C2a/C3/C4/C6 site** = `level6_architecture.py`
  (`validate_architecture`). **C5 site** = `adr002.py` (`SUPPORTED_OPERATORS = {"+","-","*","/","[","^"}`
  — note `^` is currently IN the set; C5 removes it; `check_supported_operators` uses `extract_operators`).
- **Negative-fixture convention**: agentic-mbse carries its OWN fixture dirs under `tests/fixtures/`
  (`l6_negative/`, `adr002_violations/` use `library/`+`designs/` subdirs). **Decision (Open-Q "reuse"):**
  author compact mirror fixtures in agentic-mbse's tree under `tests/fixtures/item12/` — do NOT couple
  agentic-mbse's suite to sysml-codegen paths. Cross-repo acceptance (Phase 4) runs separately over the
  sysml-codegen corpus.
- **Own-suite command**: `uv run --env-file .env pytest tests/` (testpaths=["tests"]); license valid to 2026-08-06.
- **stencils.md** (V1): `claude/skills/sysml-conventions/references/stencils.md:39` teaches inline
  `return result : Real = input_a * input_b;` — the committed A-2 form. Skill = SKILL.md + references/stencils.md
  (no MODELING_GUIDE in the skill; MODELING_GUIDE.md lives at `modeling_project/MODELING_GUIDE.md`).
- **Item-8 L6 baseline reproduced live** over `self_named_binding_trap`: L1–L5 pass; L6 FAILs with exactly
  `V2_DYNAMIC_EXPRESSION` (calc-def-internal `out attribute … = expr`, the C6a false positive) +
  `L6_INVALID_QUALIFIED_NAME` (`'Trap Plant'` quoted name, the C6b false positive). Confirms C6 is a
  scoping tweak, not a rework.

**Check-design facts probed live (drive Phase 1):**
- **C1**: `extract_bindings` gives `source_path == param_name` for a self-named `in P = P` in BOTH trap and
  rescue (`references` list is empty for REFERENCE bindings, so key off `source_path`). Distinguisher =
  a **producer** of the name in the owner: rescue has `attribute throughput = source_calc.throughput`
  (chain into a calc), trap has only `attribute availability = 0.70` (literal). Predicate: self-named +
  no producer → FAIL.
- **C2a**: anonymous `return : Real = x*2` → an output member (`dir=Out`) with `declared_name = None`
  (synthesized `name='result'`). Named returns carry `declared_name='y'`. Predicate: output member with
  empty/None `declared_name` → FAIL.
- **C4**: part-usage `.types` includes the **full supertype chain AND retype targets** — the Variant's
  retyped `driver` usage has `.types = [IFE Driver, …, HIF Driver]`. So "instantiated" = partdef name ∈
  union of all part-usage `.types`; retyping counts automatically. Predicate: calc-bearing partdef whose
  name is absent from that union → FAIL.

**Deviations:** none. No floor assumption broke; Phase 1 proceeds at planned size.

### Phase 1 Completion
**Status:** COMPLETE — all four checks landed + green; committed in agentic-mbse at `9db5ede`.

**C1 RESOLVED (orchestrator ruling A — reframe to a true dead-end).** The C1 blocker below
was resolved by reframing the check, not forcing the old fixture:
- `_owner_produces_name` → **`_owner_covers_name`**: coverage is ANY same-named feature
  (attribute incl. bare literal, or a sibling calc output) in the owner. Dropped the
  `extract_feature_refs` non-literal condition + its import.
- **Key correction found during re-wire:** the scan must walk **`owner.features`** (owned +
  inherited), not `owned_members`. ife_plant's `'Hif Driver' :> 'Base Driver'` binds
  `in bank_energy = bank_energy` against a `bank_energy` attribute **inherited** from its base
  def (Item 4 retype path). Scanning only `owned_members` missed it and FALSELY flagged 1
  dead-end → flipped ife_plant L2 PASS→FAIL. With `features`, ife_plant + wi014_toy both PASS,
  0 self-named FAILs.
- **Role flip (ruling step 3):** NEW `self_named_deadend` fixture (`in gain = gain`, NO
  covering feature) FAILs; `self_named_trap` (has covering `attribute availability`) and
  `self_named_rescue` (has covering `attribute throughput`) both do NOT fire; ife_plant L2 PASS.
- **Rationale (for traceability + sysml-codegen spec amendment):** C1's floor was written
  pre-Items-9/10. Item 9's rescue made self-named-with-covering-attribute a SUPPORTED pattern,
  so the trap fixture's role flipped to negative-of-the-negative; only a self-named binding with
  no covering feature at all is a real error.
- **Gate:** 8 item12 tests pass (was 7 — +1 dead-end test); full agentic-mbse suite
  **1213 passed / 1 skipped**; ruff clean.

**Original C1 blocker (kept for the trail — resolved above):**

**Landed (C2a, C3, C4 — all built, tested, suite-green, zero corpus regression):**
- **C2a** `check_anonymous_returns` (`level6_architecture.py`): output member with empty/None
  `declared_name` → `L6_ANONYMOUS_RETURN` FAIL. Fixture `item12/anonymous_return` FAILs;
  `item12/return_styles` (all four legal forms) does NOT fire. Mirrors codegen V8.
- **C3** `check_constraint_executability` (`level6_architecture.py`): each ConstraintUsage →
  `L6_CONSTRAINT_NON_EXECUTABLE` WARN (L6 stays passing). Fixture `item12/constraint_model`.
- **C4** `check_calc_bearing_instantiation` (`level6_architecture.py`): calc-bearing part def whose
  name ∉ union of all part-usage `.types` → `L6_CALC_DEF_NO_INSTANTIATION` FAIL. Fixture
  `item12/no_instantiation` FAILs; `item12/retype_instantiation` does NOT (retype target lands in
  `.types`, so retyping counts — Item 4). 
- New `ValidationCode`s in `sysml/types.py`; metrics added to L6 result.
- **Gate:** agentic-mbse own suite **1212 passed / 1 skipped**; ruff clean; mypy adds 0 new errors
  (23 pre-existing, none in the new functions). Cross-repo: C2a/C3/C4 fire **0** times on
  `wi014_toy` and `ife_plant` — no L1–L5 regression, no L6 change on the plant fixtures.
- 7 direct-call tests in `tests/test_validation/test_item12_checks.py` (incl. all negatives-of-negatives).

**C1 BLOCKER — floor-assumption break (the Phase-0/Phase-1 STOP gate fired).**
C1 assumes the `self_named_binding_trap` shape is a self-named binding "with no resolvable upstream"
that a validator can FAIL while the plant idiom passes. **Phase-1 evidence refutes this at the
agentic-mbse layer:**
- Probed the resolved RHS referent for three fixtures. **All three resolve `in X = X` to the calc's
  OWN parameter** (refOwner = the CalculationUsage):
  - trap `avail_calc`: `TrapLib::'Trap Plant'::avail_calc::availability`
  - ife_plant `volume_calc`: `IfePlantLib::Coil::volume_calc::radius`  ← the legitimate plant idiom
  - rescue `sink_calc`: `RescueLib::'Rescue Plant'::sink_calc::throughput`
- The trap (`attribute availability = 0.70` + `in availability = availability`) is **structurally and
  resolution-identically the same** as ife_plant's `attribute radius = <lit>` + `in radius = radius`.
  ife_plant carries **21** such legitimate design-attribute bindings.
- The full-QN own-param resolution that sysml-codegen's extractor uses to mark the trap "degenerate"
  is **not reproduced by agentic-mbse's `extract_bindings`** (it yields only the short name). No signal
  available at this layer (source_path, referent, referent-owner, producer scan) separates trap from
  ife_plant.
- Consequence: a C1 that FAILs the trap FAILs ife_plant 21× and flips its L2 PASS→FAIL — a HARD
  no-regression violation. C1-as-specced is unbuildable here.

**State left for resume:** `check_self_named_bindings` + `_owner_produces_name` are written in
`level2_structure.py` but **intentionally NOT wired** into `validate_structure` (commented, with
reason). The `item12/self_named_trap` + `self_named_rescue` fixtures and the two direct-call C1 tests
pass in isolation (my mirror trap has only the literal, so the current predicate fires on it) — but the
predicate is WRONG for the corpus. Nothing committed. ife_plant L2 verified back to PASS.

**Decision needed before C1 can land — see final orchestrator message.** Options sketched:
(A) Reframe C1 to fire only on a self-named binding with **no same-named attribute/producer at all** in
the owner (a true dead-end), and author a NEW agentic-mbse negative fixture for that (the sysml-codegen
trap, which carries the literal, would then correctly NOT fire — so it stops being C1's fixture).
(B) Keep the sysml-codegen trap as the fixture but accept C1 cannot be a corpus-safe FAIL → downgrade/FILE
(C1 is HARD non-fileable, so this needs explicit approval).
(C) Some other discriminator the spec author knows that I could not find at this layer.

**Deviations:** C1 unwired pending decision (above). No other deviation.

### Phase 2 Completion
**Completed:** 2026-07-06 — committed in agentic-mbse at `87f9bc8`. Full suite **1218 passed /
1 skipped**; ruff clean; mypy 0 new errors.

**BUILD/FILE decisions (per row, with reason):**
- **C5 — BUILD.** (a) dropped `^` from `SUPPORTED_OPERATORS` (was wrongly present); (b) new
  `check_static_function_invocations` WARNs `V4_STATIC_FUNCTION_INVOCATION` on a design-scope
  function call. Sized live: `sqrt(a)` → InvocationExpression (Operator=False), `a ^ b` →
  OperatorExpression (Invocation=False) — `is_instance` distinguishes them cleanly.
- **C6 — BUILD (the named FILE risk — turned out a scoping tweak, not a rework).** (a)
  `check_static_expressions` skips attributes owned by a `CalculationDefinition` (owner-type
  predicate, independent of the `library/` path convention the flat-layout trap fixture defeats);
  (b) `check_qualified_names` accepts single-quoted segments (`'Trap Plant'`). **Confirmed on the
  real Item-8 trap:** `self_named_binding_trap` L6 now PASSES, 0 V2_DYNAMIC_EXPRESSION + 0
  L6_INVALID_QUALIFIED_NAME (both fired pre-C6).
- **C2b — BUILD.** `check_body_assignment_impl_loss` WARNs `L6_BODY_ASSIGNMENT_IMPL_LOSS`. Sized
  live: the body-assignment `return attribute y; y = expr` yields an Out member with `has_fve=False`
  plus a same-named sibling member carrying the value expression — precise detector, inline forms
  don't fire.
- **C7 — FILE (agentic-mbse backlog).** Attribute-`:>>`-with-expression WARN. Reason: its correct
  trigger boundary is subtle — must fire on an *AttributeUsage* redefinition with an *expression*
  RHS but NOT on the supported bare-`:>>` (ReferenceUsage) form nor a literal-valued redefinition.
  Getting that wrong reintroduces the C6 defect class (flagging a shape codegen accepts). Explicit
  candidate under the guard → filed rather than shipped rushed. Paired doc D5 still lands.
- **C8 — FILE (agentic-mbse backlog).** Two-names-one-identifier WARN. Reason: requires replicating
  codegen's identifier sanitizer in agentic-mbse to compute collisions — real duplication risk
  (drift from codegen's REQ-NC-09). Explicit candidate → filed; codegen's duplicate-path error is
  the backstop.

**Deviations:** none — the guard's build-or-file split executed as written; both FILEs are the
named candidates, logged here and carried to Phase 4 F-rows.

### Phase 3 Completion
**Completed:** 2026-07-06 — committed in agentic-mbse at `f68d1cb`.

**D-rows landed:**
- **D1/D2/D8** — new `docs/patterns/plant-idiom.md`: template calcs, design-attribute
  bindings, retyping (D2), def-owned attributes (D8, kept as a cheap section, not downgraded),
  cross-part chains + EXPOSE, sibling disambiguation. References the 5 sysml-codegen fixtures
  (all verified present).
- **D3** — SKILL.md naming: quoted names are fine, codegen derives the identifier.
- **D4** — adr002-calculations.md: no-loops rule (A-3), DAG.
- **D5** — semantic-operators.md: bare-`:>>` value idiom, plain-usage literal override,
  `attribute :>>`-with-expression warning (pairs with FILED C7), redefinition precedence.
- **D6** — expose-pattern.md: EXPOSE surfacing (output_aliases, filename, sanitized name,
  both shapes, EXPOSE_COMPUTED rejected).
- **D7** — constraints.md: not executable, dropped at extraction (pairs with C3, points at
  modeling-assumptions §8).
- Registered plant-idiom.md in all three indices (stencils.md, MODELING_GUIDE.md, README.md).

**V1:** confirmed — `references/stencils.md:39` teaches the committed A-2 inline
`return result : Real = input_a * input_b;` form (not body-assignment).

**V2 sweep result (the load-bearing gate — CLOSED):** swept the whole sysml-conventions skill
+ all `docs/patterns/`. Nothing else teaches a now-rejected pattern.
- The operator taxonomy in `adr002-calculations.md` ALREADY matched C5 (supported `+ - * /`
  and `[`; unsupported `**`/`^`, functions sin/sqrt/abs, conditionals, derived design-attr
  refs) — no correction needed, it agrees with the shipped check.
- The only stale stencil was the A-2 body-assignment calc-def form, fixed at `6dbdf1b`.
- The `out attribute result : Real;` forms in semantic-operators.md are usage-based-dataflow
  output channels (value wired by downstream usage bindings), NOT the C2b body-assignment
  anti-pattern — checked, they don't trip C2b (no same-named valued sibling). Left as-is.
- Minor note (not fixed, not stale): SKILL.md:121 shows conditional syntax without a
  design-vs-calc-def scope caveat; the authoritative taxonomy in adr002-calculations.md is
  correct. Not a broken pattern — left as general-syntax reference.

**Deviations:** none. No doc section ballooned (guard not triggered).

### Phase 4 Completion
**Completed:** 2026-07-06. Full detail in `close-out.md` (two traceability tables).

**Acceptance gates (both green):**
- agentic-mbse own suite: **1218 passed / 1 skipped**; ruff clean; mypy 0 new errors.
- run_all_checks over the sysml-codegen corpus: three plant fixtures L1–L5 PASS (no
  regression); L6 changes are exactly the designed ones (C6 makes the real trap L6 PASS;
  C2a FAILs anonymous_return by design; C2b WARNs return_styles). `retype_model` L2=F is a
  pre-existing `UNBOUND_INPUT`, not an Item-12 code.

**Filings landed:**
- agentic-mbse (`upstream-findings-sync`, committed `08cd595`): F1 (vendor note + draft),
  F2, C7, C8.
- sysml-codegen (this repo, WRITTEN not committed): F3/F4/F5 in `.project/backlog/BACKLOG.md`.

**Traceability:** every impact-list row (C1–C8, D1–D8, V1–V2, F1–F5) dispositioned with
evidence; every fusion-tea trap (SC-1..SC-11, A-1/A-2/A-3) mapped to a check, rule, codegen
fix, or filing — nothing dropped. RAW_LEARNINGS + register read live (this session had
fusion-tea access).

**Deviations:** C1 reframed from its spec floor (dead-end, not the trap shape) per orchestrator
ruling A — recorded as the spec amendment in close-out.md. No other deviation.

---

**Status:** Draft → In Progress → **Complete**
