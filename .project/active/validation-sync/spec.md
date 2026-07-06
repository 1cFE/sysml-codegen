# Spec: agentic-mbse Sync — Guidance & Validation (UPSTREAM-FINDINGS Item 12)

**Status:** Complete (2026-07-06 — see `close-out.md`; C1 reframed per orchestrator ruling, amendment recorded)
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH (breadth, cross-repo; bounded by a hard 1–1.5 day scope guard)
**Branch (artifacts):** `upstream-findings-epic` (this repo, sysml-codegen)
**Branch (implementation):** `upstream-findings-sync` (in `~/1cfe/agentic-mbse` — already carries the A-2 stencil fix, commit `6dbdf1b`)

---

## Problem

sysml-codegen changed what SysML it accepts across eleven items of this epic. agentic-mbse
— which teaches modelers the correct patterns (MODELING_GUIDE, the sysml-conventions skill)
and audits models before generation (the L1–L6 validation runner) — has not moved with it.
The two have drifted, and the drift cuts both ways:

- **agentic-mbse teaches at least one broken pattern.** Its calc-def stencil taught the
  expression-losing body-assignment form (register finding A-2). Item 3 fixed it inline
  (committed, `6dbdf1b`); Item 12's job is to sweep for anything *else* stale.
- **agentic-mbse's checks contradict what codegen now supports.** The L6 architecture check
  flags legal `out attribute X = <expr>` inside calc defs and flags quoted names — both now
  first-class in codegen (Items 3, 5). A model can pass generation but fail the auditor, or
  vice versa.
- **The traps that broke fusion-tea have no checks.** The self-named binding, the
  cross-part chain, the retype-with-no-instantiation, the unsupported operators — every one
  surfaced as a runtime failure or a silent drop that no agentic-mbse check would have
  caught. The register's A-1 gap matrix is the list of what's missing.

Every prior item recorded its agentic-mbse impact and deferred the work here (epic R2). This
is the final item: consolidate those recordings into one sourced list, execute the floor,
and file the rest. When it lands, the validated-subset contract is enforceable again — a
model the auditor passes is a model codegen accepts.

## Success Criteria

- [ ] **The consolidated impact list is built and dispositioned** — one deduplicated,
  sourced table (item → impact → disposition), with nothing from any per-item recording
  silently dropped. (This spec delivers the table; the plan/execute honors it.)
- [ ] **Every floor check exists with a negative fixture and catches its trap** on the
  WI-014 toy / plant fixture shapes: L2 self-named-binding (FAIL); L6 return-style output
  check, constraint non-executability (WARN), calc-bearing-part-def-no-instantiation (FAIL);
  adr002 operator-set corrections (`**` status, function-invocation → WARN).
- [ ] **No agentic-mbse surface teaches or checks a pattern codegen now accepts as an
  error.** A-2 confirmed landed; the L6 false-positives on calc-def-internal derived
  expressions and on quoted names are corrected; the sysml-conventions skill sweep finds
  nothing else broken.
- [ ] **The teaching surfaces match the supported subset** — MODELING_GUIDE / sysml-conventions
  cover: plant-idiom patterns, retyping, quoted names, the no-loops rule, the bare-`:>>`
  value idiom + the attribute-`:>>` warning, and EXPOSE surfacing.
- [ ] **fusion-tea's RAW_LEARNINGS traps are each covered by a check or a documented rule**,
  shown in a traceability table in the close-out. (Built from an implement session that can
  read fusion-tea — see Open Questions.)
- [ ] **Everything out of scope is filed as an agentic-mbse (or sysml-codegen) backlog
  item**, including the syside vendor note — which records the Item-8 finding that the
  trap's recursion is evaluation-time, not extraction-time.

---

## Consolidated Impact List (the deliverable)

Every impact recorded by Items 1–11 plus the register's A-1/A-2/A-3 floor, deduplicated and
dispositioned. Disposition codes: **BUILD-CHECK** (new/corrected validation check + negative
fixture), **BUILD-DOC** (MODELING_GUIDE / sysml-conventions content), **VERIFY** (confirm a
prior inline change landed), **FILE** (out of scope → backlog, not dropped).

Where two items recorded the same impact, they share one row (Source column lists both). The
self-named-binding check is the clearest example — Items 8, 9, and 10 each touched it.

| # | Impact | Disposition | Source(s) |
|---|--------|-------------|-----------|
| **Checks (the A-1 floor + item-recorded checks)** ||||
| C1 | **Self-named-binding check (FAIL, L2).** A binding/redefinition that binds an attribute to itself with no resolvable upstream is a modeling error. The rescue (Item 10) resolves the *resolvable* case; the unresolvable case still FAILs. Negative fixture: the `self_named_binding_trap` shape. | BUILD-CHECK | plant-fixtures/spec §impact; cross-part-wiring/release-notes + REQ-VBR-10; plant-prefill/spec (stays FAIL until rescue) |
| C2a | **Return-style output check — accept + FAIL (L6).** Accept the newly legal forms: `out attribute`, named `return` (inline-expr *and* body-assignment), and bare `in` params. FAIL an **anonymous `return`** (no name → no output channel; mirrors codegen V8). Its own negative fixture: an anonymous-return calc def. | BUILD-CHECK | return-style-extraction/spec §"Recorded for Item 12"; epic Item 12 floor |
| C2b | **Body-assignment auto-impl-loss (WARN, L6).** WARN the body-assignment `return attribute y; ... y = expr` form — it extracts an output but loses auto-impl until codegen's deferred capture lands. Separate check, its own negative fixture: a body-assignment calc def. | BUILD-CHECK | return-style-extraction/spec §"Recorded for Item 12" |
| C3 | **Constraint non-executability (WARN, L6).** A model carrying constraint usages should WARN that constraints are not executable and are dropped. Points at modeling-assumptions §8. Negative fixture: a model with an inline constraint usage. | BUILD-CHECK | baseline-diagnostics/spec §impact (endorse A-1); epic floor |
| C4 | **Calc-bearing part def with no instantiation (FAIL, L6).** A part def owning template calcs that is never instantiated — plainly *or by retyping* — FAILs, because its template calcs are dropped. Retyped usages (Item 4) now count as instantiation, so the check's notion of "instantiated" must include them. Negative fixture: a calc-bearing part def with no usage. | BUILD-CHECK | type-indexing/spec §impact item 2; epic floor (A-1 row 4) |
| C5 | **adr002 operator-set correction.** In static design-attribute / FORMULA expressions the supported set is `+ - * /` and unit `[...]`; `**`/`^`, functions, and conditionals are NOT static operators and must move to a calc def. Correct `**`'s status in the operator table and make a **function-invocation in a static expression a WARN** (steer to a calc def). Negative fixtures: `attribute x : Real = a ** b;` and `= sqrt(a);` at design-attribute scope. | BUILD-CHECK | epic Item 12 floor (register A-1 adr002 corrections); modeling-assumptions §3 "Supported Operators" |
| C6 | **L6 false-positive corrections.** The current L6 check flags two shapes codegen now treats as legal: (a) `out attribute X = <expr>` *inside a calc def* (ADR-002 says derived expressions belong there — all three Item-8 fixtures were flagged); (b) quoted multi-word names (`'Panel Area'`) whose EQN it "cannot derive" — but sanitization (Item 5) handles these. Scope the check so neither is flagged. This is part of "nothing checks a broken pattern." | BUILD-CHECK | plant-fixtures/plan Phase 4 (L6 flag enumeration); identifier-sanitization/close-out (quoted names are fine) |
| C7 | **attribute-`:>>`-with-expression warning (WARN) — candidate.** `attribute :>> attr = <expression>` is silently dropped at extraction (`hierarchy_resolver.py` `_extract_single_redefinition` scans only ReferenceUsage). WARN when this shape carries an expression RHS; teach the bare form instead (see D5). Negative fixture: the dropped attribute-`:>>` shape. **Budget-permitting — else FILE** (see Scope guard). | BUILD-CHECK (or FILE) | cross-part-wiring/design D-F + release-notes |
| C8 | **Two-names-one-identifier warning (WARN) — candidate.** Two distinct SysML names that sanitize to one Python identifier — WARN before generation fails on codegen's duplicate-path error (REQ-NC-09). Negative fixture: two calc defs whose names collapse to one identifier. **Budget-permitting — else FILE.** | BUILD-CHECK (or FILE) | identifier-sanitization/close-out §impact |
| **Documentation (MODELING_GUIDE / sysml-conventions)** ||||
| D1 | **Plant-idiom patterns.** The supported cross-part shapes Items 9–10 wired: multi-hop EXPOSE through a nested part on a plain usage; cross-part calc chains through retyped nested parts; part-def-level EXPOSE reaching a calc output, expanded per instance; sibling disambiguation by instance scope. Reference fixtures: `ife_plant`, `spec_chain_channel`, `spec_chain_twolevel`, `sibling_channel_ambiguity`, `wi014_toy`. | BUILD-DOC | plant-fixtures/spec §impact; cross-part-wiring/spec+release-notes; plant-prefill |
| D2 | **Retyping.** A design may retype a part usage to a subtype (`part :>> driver : 'HIF Driver'`) to pull in the subtype's template calcs. Document: the subtype should specialize the base def (`part def 'HIF Driver' :> 'IFE Driver'`); a calc replacing an inherited one reuses its name (same-QN redefinition). | BUILD-DOC | type-indexing/spec §impact item 1 |
| D3 | **Quoted names.** "Quoted names are fine — identifiers are derived." Modelers may use `'Fusion Power Plant'` freely; codegen sanitizes to `Fusion_Power_Plant`. | BUILD-DOC | identifier-sanitization/close-out §impact |
| D4 | **No-loops rule (A-3).** Pure documentation — state the no-loops constraint. | BUILD-DOC | epic Item 12 floor (register A-3) |
| D5 | **Bare-`:>>` value idiom + attribute-`:>>` warning.** The value-carrying redefinition idiom is the **bare** `:>> attr = value` form (parses as ReferenceUsage, captured). Also teach the plain-usage literal override `part x : Type { :>> nested.attr = <literal>; }`. `attribute :>> attr = <expression>` is known-unsupported (paired with check C7). State the redefinition-precedence rule: usage override > specialized-def `:>>` > base def. | BUILD-DOC | plant-prefill/release-notes §impact; cross-part-wiring/design D-F + release-notes |
| D6 | **EXPOSE surfacing.** An EXPOSE_PURE name is no longer internal wiring convenience only — it surfaces as a named output capture: it lands on `output_aliases` and becomes the output filename `{instance_path}__{alias_name}.json`. The surfaced name is the sanitized `python_name` (teach the sanitized form). Both shapes (part-def A, part-usage B) surface. EXPOSE_COMPUTED (calc output + arithmetic) stays rejected. | BUILD-DOC | alias-surfacing/release-notes §impact |
| D7 | **Constraint pointer.** The MODELING_GUIDE constraint guidance points at modeling-assumptions §8 (canonical "constraints are not executable"). Pairs with check C3. | BUILD-DOC | baseline-diagnostics/spec §impact |
| D8 | **Def-owned design attributes are supported.** A design attribute owned directly by a part def (empty `parent_part`) now resolves through the matcher (Item 7). Add a one-line note that this shape is supported, alongside the retyping pattern (D2). Item 7 recorded this as a *soft* candidate ("worth a note?") and its own Phase-5 answer leaned "no note needed — codegen matcher concern"; included here as a cheap BUILD-DOC line rather than dropped, so the R2 trail is complete. The plan may downgrade it to the no-impact paragraph if it judges the note redundant. | BUILD-DOC | warning-reconciliation/spec §impact (third bullet); plan Phase 5 |
| **Verify** ||||
| V1 | **A-2 spot-check (in passing).** The calc-def stencil fix is **committed** (agentic-mbse `upstream-findings-sync`, `6dbdf1b`) — `references/stencils.md` teaches inline `return <r> : Real = <expr>` / `out attribute <r> : Real = <expr>`, not the body-assignment form. Read it once to confirm it reads as expected. This is a spot-check, not a re-verification of whether A-2 landed — it did. | VERIFY | return-style-extraction/spec §"Inline in this item"; Item 3 plan (`6dbdf1b`) |
| V2 | **Skill sweep — the load-bearing check.** Sweep the whole sysml-conventions skill for any *other* stencil or rule that teaches a pattern codegen now rejects (or rejects one it now accepts). This, not re-checking A-2, is the epic's "nothing else teaches a broken pattern" gate. | VERIFY | epic Item 12 scope item 3 |
| **File (out of scope → backlog, not dropped)** ||||
| F1 | **syside vendor note** → **agentic-mbse backlog** (implement session writes it on `upstream-findings-sync`). The self-named-binding recursion the WI-014 toy documents is **evaluation-time syside behavior, not extraction-time** — extraction is finite/degenerate (Item 8 probe, `timeout 150`, exit 0). File the note with this distinction recorded; do not build the vendor report or contact Sensmetry here. | FILE (agentic-mbse) | epic Item 12 out-of-scope; plant-fixtures/plan Phase 2 + audit |
| F2 | **V11 model-side mirror check (candidate)** → **agentic-mbse backlog**. A design-attribute binding whose `*_params` key no parameter group provides — the model-side mirror of codegen V11. Item 7 recorded it as a *candidate*, not floor; codegen V11 (hard FAIL) is the backstop. | FILE (agentic-mbse) | warning-reconciliation/spec+plan §impact |
| F3 | **Shape-B leaf-collision** → **this repo, `.project/backlog/BACKLOG.md`** (filed during Item 12's close-out here, which runs in sysml-codegen). Two distinct shape-B owning parts sharing a leaf name and exposing the same alias to different channels → a filename collision codegen does not yet disambiguate. Not triggered in-repo. | FILE (sysml-codegen) | alias-surfacing/audit Obs. 2 |
| F4 | **Redefinition / design_override name surfacing** → **this repo, `.project/backlog/BACKLOG.md`** (Item 12 close-out here). `:>>` and design-override names resolve as channels but are not EXPOSE_PURE-sourced, so they do not surface. | FILE (sysml-codegen) | alias-surfacing/release-notes §impact |
| F5 | **Positive unresolvable-warning test (opportunistic)** → **this repo, `.project/backlog/BACKLOG.md`** (Item 12 close-out here). Item 11's INV-6 "unresolvable refs still warn" leg has no positive live assertion; add opportunistically in sysml-codegen or file. | FILE (sysml-codegen) | alias-surfacing/audit Obs. 1 |

**Filing homes (no cross-repo write needed).** The FILE rows split by which repo owns the
concern, and each is written from a session that can reach it: F1/F2 (agentic-mbse concerns —
the vendor note, the model-side check) go into agentic-mbse's backlog, written by the
implement session on `upstream-findings-sync`. F3/F4/F5 (sysml-codegen concerns — a filename
edge, channel surfacing, a codegen test) go into this repo's `.project/backlog/BACKLOG.md`,
written during Item 12's close-out step, which runs here in sysml-codegen. No filing crosses
a repo boundary the writing session can't reach.

**Explicitly recorded as no-impact (kept so the trail is complete):** Item 2 (snapshot
generation — docs pointer only); Item 6 (expression reconstruction — the fix travels with
the PUSH-DOWN move, a sysml-codegen concern); Item 7 matcher fixes (internal resolution, no
MODELING_GUIDE change — only the C-F2 candidate came out of it).

**Not agentic-mbse work (noted, owned elsewhere):** the fusion-tea `sanitize_names.py`
retirement (Item 5) and the `hif_driver_instance` / two-pass gamma removal (Item 10) are
fusion-tea coordination, tracked as a BACKLOG P1 follow-up upstream; the body-assignment
expression-capture follow-up (Item 3) is a sysml-codegen backlog item.

## Known Requirements

- **[HARD]** *(R2)* Every new or corrected validation check ships with a **negative fixture**
  in agentic-mbse's fixture layout, and the check is shown to catch its trap on the WI-014
  toy / plant fixture shapes. No check lands without a fixture.
- **[HARD]** The sysml-conventions skill is **swept** (V2) for any stencil or rule teaching a
  pattern codegen now rejects or now accepts. A-2 itself is already committed (`6dbdf1b`) —
  confirm it in passing (V1), but the load-bearing gate is that nothing *else* is stale.
- **[HARD]** Check designs mirror codegen's already-shipped behavior — they must not
  contradict the V1–V11 diagnostics or the modeling-assumptions supported subset. C2 mirrors
  V8 (anonymous return), C5 mirrors V4 (unknown operator), C4 mirrors the retyping support
  (V9/V10). A check that flags a shape codegen accepts is a defect (that is exactly what C6
  corrects).
- **[NEED]** The consolidated impact list above is the contract: the plan works it row by
  row, and the close-out reports each row as done or filed. A reader can trace any per-item
  recording to a row and a disposition.
- **[NEED]** fusion-tea's RAW_LEARNINGS traps each map to a check (C1–C8) or a documented
  rule (D1–D7), shown as a traceability table in the close-out.
- **[HARD]** Four checks are **non-fileable** — the traps that actually bit fusion-tea: C1
  (self-named FAIL), C2a (return-style output update), C4 (calc-bearing-no-instantiation
  FAIL), C3 (constraint WARN). The guard may file everything else (C5, C6, C2b, C7, C8), but
  not these. (See Scope guard.)
- **[INFERRED]** C5/C6/C2b and the two candidate WARNs (C7, C8) are in scope only if they fit
  the guard, else they join the FILE set. The plan makes the call after sizing each against
  agentic-mbse's actual check structure.
- **[INFERRED]** agentic-mbse's L1–L6 runner and fixture conventions are as the impact lists
  describe them (`agentic_mbse.validation.runner.run_all_checks`, a 6-level structure). The
  implement session confirms the exact layout, check-function naming, and fixture format
  before writing code — this session could not read the repo (see Open Questions).

## Non-Goals

- **The syside vendor report** for self-named-binding recursion (F1 files the note with the
  evaluation-time finding recorded; it does not write the report or contact Sensmetry).
- **Any sysml-codegen production change.** This item works in agentic-mbse. Codegen behavior
  is frozen as of Item 11; the checks and docs *describe* it, they do not change it.
- **Building the FILE-set items (F2–F5).** They are filed as backlog, not implemented.
- **New codegen diagnostics.** V12/V13 were considered in Item 10 and reframed as REQ
  coverage, not new diagnostics — nothing here adds a V-code.
- **Constraint execution, EXPOSE_COMPUTED, non-uniform arrays** — epic-deferred, unchanged.

## Open Questions / Deferred to plan

This item has no design phase (epic budget: spec + plan + execute). These resolve in the
plan or the first execute step from an implement session with agentic-mbse read access.

- **agentic-mbse repo structure — confirm before coding.** This spec session's permission
  scope was pinned to sysml-codegen; the agentic-mbse repo, the sysml-conventions skill, and
  the fusion-tea register were all unreadable. The check designs are specified from the
  epic's floor and the per-item recordings, which is sufficient at requirements level. The
  plan/execute session must first confirm: the validation runner's L1–L6 layout and
  check-function naming; where negative fixtures live and their format (`.sysml` files vs
  inline strings); the exact `references/stencils.md` line range for V1; and the MODELING_GUIDE
  section structure. If any of these contradicts the impact-list assumptions, surface it
  before building.
- **RAW_LEARNINGS traceability — needs a fusion-tea-readable session.** The RAW_LEARNINGS
  file was unreadable here. Building its trap→coverage table (a close-out deliverable) needs
  a session that can read `~/1cfe/fusion-tea`. Defer the table to close-out; the check/doc
  set is designed against the SC-1..SC-11 findings the traps generated, so coverage is
  expected — the table confirms it.
- **C7 / C8 in-or-out.** The plan sizes both against the real check structure and decides
  build-vs-file under the 1–1.5 day guard.
- **Negative-fixture reuse.** Whether agentic-mbse can point its checks at the sysml-codegen
  fixtures (`self_named_binding_trap`, `ife_plant`, `wi014_toy`) or must author mirror
  fixtures in its own tree — a plan call once the fixture convention is known.

## Scope guard

**1–1.5 days in agentic-mbse.** Not every floor row is equal under the guard, so state the
line explicitly:

- **Must-land — non-fileable.** The checks catching traps that *actually bit fusion-tea*
  ship no matter what: **C1** (self-named-binding FAIL), **C2a** (return-style output update
  — accept the legal forms + FAIL anonymous return), **C4** (calc-bearing-part-def-no-instantiation
  FAIL), **C3** (constraint non-executability WARN). If the day runs out, these four are what
  got fixed. C1 and C3 already have in-repo negative fixtures, so they are the cheapest to
  land first.
- **May file if the day runs out.** The adr002 operator corrections (**C5**), the L6
  false-positive corrections (**C6**), the body-assignment WARN (**C2b**), and both candidate
  WARNs (**C7**, **C8**) are desirable but fileable — each drops to an agentic-mbse backlog
  item if it exceeds a small check-plus-fixture. C6 is the named risk: if it needs a
  structural rework of the architecture check rather than a scoping tweak, file it.
- **Docs and filing are cheap and expected to land** (D1–D8, F1–F5), but a doc section that
  balloons files too.

The plan sizes each row against the real runner before starting and honors this ordering:
must-land first, then the fileable checks, then docs, filing throughout.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 12; cross-cutting R2 — the
  per-item impact-list mechanism this item executes)
- **Per-item recordings (the raw material for the table above):**
  - Item 1: `.project/active/baseline-diagnostics/{spec,plan}.md`
  - Item 3: `.project/active/return-style-extraction/spec.md` (§agentic-mbse Impact)
  - Item 4: `.project/active/type-indexing/spec.md` (§agentic-mbse impact)
  - Item 5: `.project/active/identifier-sanitization/close-out.md`
  - Item 7: `.project/active/warning-reconciliation/{spec,plan}.md`
  - Items 8–10: `.project/active/{plant-fixtures,plant-prefill,cross-part-wiring}/`
  - Item 11: `.project/active/alias-surfacing/release-notes.md`
- **Contract mirrored by the checks:** `docs/architecture/modeling-assumptions.md`
  (§3 operators / EXPOSE, §5 retyping, §8 constraints, Validation Rules V1–V11)
- **Floor source (blocked this session):**
  `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` (A-1 gap
  matrix, A-2, A-3, vendor note) — read from an implement session; the epic's Item 12 section
  restates the floor.
- **Implementation target:** `~/1cfe/agentic-mbse` (branch `upstream-findings-sync`) —
  validation runner, L1–L6 checks, MODELING_GUIDE, sysml-conventions skill.
- **Plan:** `.project/active/validation-sync/plan.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_plan` — the plan sizes each impact-list row,
confirms the agentic-mbse structure, and sequences the floor within the 1–1.5 day guard.
