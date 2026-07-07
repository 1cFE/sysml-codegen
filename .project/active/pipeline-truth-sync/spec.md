# Spec: agentic-mbse Sync — Guidance, Validation, and the Companion Audit (PIPELINE-TRUTH Item 9)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH (breadth, cross-repo; bounded by a hard 1–1.5 day scope guard)
**Branch (artifacts):** `pipeline-truth-epic` (this repo, sysml-codegen)
**Branch (implementation):** `pipeline-truth-item4` (in `/home/reid/1cfe/agentic-mbse` — already carries Item 4's four companion commits; Item 9 continues on it — see Decision B1)

---

## Problem

Across nine items, PIPELINE-TRUTH changed what SysML sysml-codegen accepts, wires, and
executes — most of all the whole-plant value idiom (Items 1–2), which now resolves
end-to-end with zero bridges. agentic-mbse teaches modelers the correct patterns
(MODELING_GUIDE, the sysml-conventions skill) and audits models before generation (the
L1–L6 validation runner). Item 4 already moved the adapter and three validators in
lockstep (a coordinated pair on `pipeline-truth-item4`), but the rest of the epic's
teaching-and-checking debt has only been *recorded*, per epic R2, for this item to execute.

Three concrete gaps remain:

- **The teaching surface does not yet cover the newly supported subset.** The whole-plant
  value idiom (four value-provision mechanisms + precedence + entry-point QN-keying + the
  LITERAL-only propagation rule) is supported in codegen but taught nowhere in agentic-mbse.
  A modeler has no reference for the shape the epic exists to enable.
- **One warning the prior epic designed was never built.** `attribute :>> attr =
  <expression>` is silently dropped at extraction; the prior epic specified a WARN (its
  C7 / D-F candidate) and filed it. It is still unbuilt. A modeler authoring that shape
  gets a silent drop with no diagnostic on either side of the boundary.
- **Cross-repo residue from the prior epic was recorded but never verified closed.** The
  prior epic's companion PR (`upstream-findings-sync`, now GitHub PR #7) was left awaiting
  a human merge; C7/C8/F6 and the syside vendor note were filed but their final
  dispositions were never confirmed. And two agentic-mbse primitives that sysml-codegen's
  extraction silences bottom out in — `extract_feature_refs` traversal coverage and
  `str(direction)` repr stability — have never been audited.

Every prior item recorded its agentic-mbse impact and deferred the work here. This is that
item: consolidate the recordings into one sourced list, execute the floor, build the one
missing warning, verify the prior-epic residue closed, run the companion audit, and file
the rest. When it lands, the validated-subset contract is enforceable again — a model the
auditor passes is a model codegen accepts — and every cross-repo thread from two epics is
either closed or explicitly re-filed.

## Success Criteria

Mirrors epic Item 9's three success criteria, made concrete.

- [x] **SC-1 — The consolidated impact list is built and dispositioned.** One
  deduplicated, sourced table (item → impact → disposition), with nothing from any per-item
  recording silently dropped. This spec delivers the table; the plan/execute honors it and
  the close-out reports each row done or filed. (Epic Item 9 SC row 1 + §6 traceability.)
- [x] **SC-2 — Every new or corrected check has a negative fixture and catches its trap on
  the Item-1 fixture shapes.** Specifically the D-F expression-RHS warning (§the deliverable
  C7 row) fires on `attribute :>> attr = <expression>` and stays silent on the bare
  `:>> attr = <literal>` form. (Epic Item 9 SC row 2.)
- [x] **SC-3 — The teaching surfaces match the newly supported subset.** MODELING_GUIDE /
  sysml-conventions cover the whole-plant value idiom (four mechanisms a/b/c/d, precedence,
  QN-keying, LITERAL-only), the subtype-aware validation semantics Item 4 landed, and the
  Item-5 diagnostics a modeler can trip (non-float entry points, deep-chain truncation).
- [x] **SC-4 — Prior-epic cross-repo residue is verified closed or explicitly re-filed.**
  PR #7 merge status recorded; C7 built (this item), C8 and F6 dispositioned; the syside
  vendor note filed-with-Sensmetry or explicitly declined, with the decision recorded.
- [x] **SC-5 — SYNC-F3/F4/F5 each get a recorded decision.** F5 verified against Item 5's
  fires-on-shape work (discharge or re-file); F3 and F4 each get a decision.
- [x] **SC-6 — The companion audit is complete.** `extract_feature_refs` traversal coverage
  and `str(direction)` repr stability are audited against the shapes sysml-codegen's
  extraction relies on; findings fixed-if-small or filed.
- [x] **SC-7 — Both repos' suites green** at close (R2 pair); nothing in agentic-mbse now
  teaches or checks a pattern codegen accepts (the "fires on a supported subset" defect
  class the epic exists to remove).

---

## Consolidated Impact List (the deliverable)

Every impact recorded by Items 1–5, plus the prior-epic residue and the SYNC-F* filings,
deduplicated and dispositioned. Disposition codes:

- **BUILD-CHECK** — new/corrected validation check + negative fixture.
- **BUILD-DOC** — MODELING_GUIDE / sysml-conventions / pattern-doc content.
- **VERIFY** — confirm a prior change landed (Item 4 already committed it; do not redo — R2/D4).
- **AUDIT** — the companion-audit task (§5).
- **DECIDE** — a disposition the plan/implement records (build-or-file / file-or-decline), not a code build.
- **FILE** — out of scope → backlog, not dropped.

Where two items recorded the same impact they share one row (Source lists both). The
whole-plant value idiom is the clearest example — Items 1 and 2 both recorded it; it is one
headline BUILD-DOC row.

| # | Impact | Disposition | Source(s) |
|---|--------|-------------|-----------|
| **Documentation (MODELING_GUIDE / sysml-conventions / patterns)** ||||
| D1 | **Whole-plant value idiom (the headline).** Teach the four value-provision mechanisms: (a) subtype-def literal `:>>` reached cross-part through a usage-level retype; (b) bare no-retype `part :>> name { :>> attr = <literal>; }` override block; (c) plain one-hop cross-part attribute with a usage-level dotted override `:>> chamber.cost_per_unit = 7.0`; (d) in-part inherited-attr redefine `in flow_rate = throughput` with `:>> throughput = 8.0` below. State the **precedence** rule (usage override > specialized-def `:>>` > base def), that **entry points key by the source attribute QN** (so renaming an input per consumer still collapses to one parameter, and one attr feeding N consumers is one channel), and that **only LITERAL values propagate** — a CHAIN/EXPRESSION-supplied value falls to the uncovered-parameter diagnostic, not a silent drop. Reference fixtures: `plant_values`, `plant_value_shapes`, `spec_chain_twolevel`. | BUILD-DOC | plant-value-fixtures/spec §agentic-mbse impact (a/b/c + fan-out); whole-plant-resolution/spec §agentic-mbse Impact (a/b/c/d + precedence/QN/LITERAL) |
| D2 | **Secondary supported-subset shapes, with observed labels.** attribute-def-typed nested `:>>` (DEGRADED — nested value doesn't reach the cross-part input); bare `default 10.0` no `:=` (CORRECT); quoted enum def + usage `:>>` (CORRECT); quoted output-param `out attribute 'net cost'` (CORRECT, de-quotes to `net_cost`); Style-E mixed `out attribute`+`return` (CORRECT); 5-deep specialization chain with abstract ends (CORRECT); inherited-attr-redefined-below (DEGRADED). Teach the CORRECT shapes; document the two DEGRADED shapes as known-incomplete. Reference: `plant_value_shapes`. | BUILD-DOC | plant-value-fixtures/spec §agentic-mbse impact |
| D3 | **Keep cross-part chains shallow.** A multi-hop dot chain (`station.array.derived_calc.derived_value`) TRUNCATES its `source_path` to the first segment. Teach: keep cross-part references to one hop where a value must resolve. Reference: `deep_cross_scope_probe`. Pairs with check C7's family and the D3-2 loud-reject Item 5 landed. | BUILD-DOC | plant-value-fixtures/spec §agentic-mbse impact (deep cross-scope); discovery §D3 |
| D4 | **Subtype-aware validation semantics — teaching surface.** Item 4 landed the adapter `include_subtypes` sweep and the 8-row decision table (what a subtype-aware sweep now sees: `AssertConstraintUsage` counts as a dropped constraint; `RequirementUsage`/`SatisfyRequirementUsage` decisions; `NamespaceImport`/`MembershipImport` under `Import`). Verify the decision table is published in the adapter docs (Item 4 committed it) and add the modeler-facing note: assert-shaped constraints are now visible to the drop report and the L4/L6 constraint checks. | BUILD-DOC (+ VERIFY the table landed) | subtype-enumeration/register-update-pending.md (decision table); plan Phase 6 (table published on `pipeline-truth-item4`) |
| **Checks (new / to-build)** ||||
| C7 | **D-F expression-RHS warning (WARN) — BUILD IT NOW.** WARN when `attribute :>> attr = <expression>` carries an expression RHS — the shape `hierarchy_resolver._extract_single_redefinition` silently drops (it scans only ReferenceUsage). Teach the bare `:>> attr = <literal>` form (D1) instead. **Negative fixture:** the dropped attribute-`:>>`-with-expression shape; **silent-on-clean:** the bare literal form. This is epic Item 9 §2, and it discharges the prior epic's C7 / D-F candidate (recorded, never built). Substrate exists: `plant_value_shapes` carries the enum-valued/non-float shape one hop from this. | BUILD-CHECK | epic Item 9 §2; prior epic AGENTIC_MBSE_PR_BODY C7/D5; plant-value-fixtures §non-float EP |
| **Verify (Item 4 already landed — do not redo, R2/D4)** ||||
| V1 | **Item-4 companion commits landed on `pipeline-truth-item4`** (base `7f77510`): `64a097e` (adapter: `elements_of_type(model, name, *, include_subtypes=False, exclude=())`, both methods raise `ValueError` on unmapped, `EXCLUDED_CONSTRAINT_TYPES` + `is_droppable_constraint`, `InvocationExpression` mapped); `cc64b1d` (level3/4/6 validators + level3 graph re-key by importing-package QN); `bc24ae3`, `bc196df` (fixtures + adapter docs, per Item-4 plan Phase 5/6). Read once to confirm they read as expected — a spot-check, not a re-verification. | VERIFY | subtype-enumeration/register-update-pending.md; plan Phases 1/2/5/6; epic §4 pointer (4 commits) |
| V2 | **A-2 / stencil sweep still holds.** The prior epic's calc-def stencil fix and skill sweep landed (PR #7). Confirm the sysml-conventions skill still teaches no pattern codegen now rejects — re-run the load-bearing sweep now that Items 2/4/5 changed the accepted set (the whole-plant idiom, subtype-aware constraints, the Item-5 loud shapes). | VERIFY | prior epic validation-sync V2; PR #7 body |
| V3 | **Item 3 — no new agentic-mbse impact.** Item 3 changed no executable SysML subset and no auditor behavior; recorded R2 = none new. Row kept so the trail is complete. | VERIFY (no-op) | fusiontea-acceptance/run-report.md §Item-9/R2; plan Phase 5 |
| **Prior-epic residue (§3) — verify closed / decide** ||||
| R-PR7 | **Companion PR #7 (`upstream-findings-sync`) merge status.** OPEN mid-epic (a concurrent session ran `gh pr create`); the prior-epic residue is DISCHARGED as *created*, but the merge is the human's. Record open/merged at implement; if open, it stays the human's to merge — do not merge it. `pipeline-truth-item4` is stacked on it (Decision B1). | VERIFY | epic §3; subtype-enumeration/plan (PR #7 OPEN at Item-4 time) |
| R-C8 | **Two-names-one-identifier warning (C8).** Prior epic FILED it to agentic-mbse backlog (Phase 4, `08cd595`). Now lower-value: Item 5 landed SC-4 sanitizer-injectivity **fail-fast in codegen** — the collision fails loudly at generation. **Recommendation: keep filed** (the codegen backstop exists); plan may build the pre-warn if it costs a small check-plus-fixture. Record the decision. | DECIDE | epic §3; prior epic C8; silent-failure-hardening SC-4 |
| R-F6 | **F6 (static-expression false-FAIL).** Prior epic FIXED it in post-review (`49c7b7a`): `check_static_expressions` exempts same-part owned-sibling FORMULA refs while still firing on calc-output-in-arithmetic / self-ref / dotted paths. Verify it is still correct after Item 4's validator changes; confirm closed. | VERIFY | epic §3; prior epic AGENTIC_MBSE_PR_BODY post-review |
| R-VENDOR | **syside vendor note (self-named-binding recursion).** Prior epic drafted it to agentic-mbse backlog (Phase 4, `08cd595`) with the evaluation-time-not-extraction-time finding. **Recommendation: DECLINE the Sensmetry filing** — the recursion is evaluation-time syside behavior; extraction is finite/degenerate (Item 8 probe, `timeout 150`, exit 0), so no codegen path is affected. Keep the backlog note as the durable record. Record the decision (file-or-decline is the item's call). | DECIDE | epic §3; prior epic F1 / plant-fixtures probe |
| **SYNC-F3/F4/F5 (§4) — sysml-codegen concerns, decision each** ||||
| S-F5 | **Positive unresolvable-warning test (SYNC-F5).** Epic says "absorbed by Item 5's fires-on-shape rule — verify + record." Item 5 landed fires-on-shape tests for the extraction-silence family (D3-1 unknown binding-expr-type WARN; unbound-ledger surfacing), but did **not** add a test named against SYNC-F5's INV-6 leg (no `unresolvable` match in Item 5's plan). **Verify** whether an Item-5 test already asserts an unresolvable ref emits its warning; if yes, discharge S-F5; if no, decide (add opportunistically or keep filed). | DECIDE (verify-first) | epic §4; BACKLOG SYNC-F5; silent-failure-hardening audit (INV-6 holds) |
| S-F3 | **Shape-B leaf-collision filename edge (SYNC-F3).** sysml-codegen concern (P2, BACKLOG). Not triggered in-repo. **Recommendation: keep filed** — no model hits it; decide. | DECIDE | epic §4; BACKLOG SYNC-F3 |
| S-F4 | **Redefinition / design_override name surfacing (SYNC-F4).** sysml-codegen concern (P2, BACKLOG). Whether `:>>`/design-override names should surface as named outputs (mirror of EXPOSE) or stay internal. **Recommendation: keep filed** unless a consumer needs it; decide. | DECIDE | epic §4; BACKLOG SYNC-F4 |
| **Companion audit (§5)** ||||
| A1 | **`extract_feature_refs` traversal coverage.** The agentic-mbse primitive sysml-codegen's binding extraction bottoms out in. Audit: does it traverse every reference shape codegen relies on (multi-segment feature chains, self-named bindings, cross-part refs)? A gap here is a silent-drop root. Fix-if-small or file. | AUDIT | discovery §D3 cross-repo pointer; silent-failure-hardening Non-Goals |
| A2 | **`str(direction)` repr stability.** codegen keys parameter direction (in/out) off the stringified `direction`. Audit that the repr is stable across syside versions and shapes (no `<Direction.IN: ...>`-vs-`in` drift). Fix-if-small or file. | AUDIT | discovery §D3 cross-repo pointer; silent-failure-hardening Non-Goals |
| **Derive-then-execute (Item 5 impact block was deferred)** ||||
| I5 | **Item 5 diagnostics → guidance.** Item 5's own Item-9 impact block was DEFERRED under stage budget (never written). Derive the modeler-facing subset from its spec/plan and fold into D2/D3: non-float entry-point literals (bool/string/enum) now diagnosed (SC-5, `plant_value_shapes` `wall`); multi-hop chain loud-reject (D3-2); aggregation operator-map (`^` no longer silently XORs). These are codegen-side diagnostics — the agentic-mbse surface is guidance ("entry points must be float-valued", "chains stay shallow"), not new checks unless a shape warrants one. | BUILD-DOC (derive) | silent-failure-hardening/spec + plan (impact list DEFERRED, plan:315); audit.md |

**Filing homes (no cross-repo write the writing session can't reach).** Agentic-mbse
concerns (C7 build, C8 keep-filed, F6 verify, vendor-note decision, A1/A2 audit findings)
are written by the implement session on `pipeline-truth-item4` (agentic-mbse access).
sysml-codegen concerns (S-F3/S-F4/S-F5 dispositions) are recorded in this repo's
`.project/backlog/BACKLOG.md` and this item's close-out, which run in sysml-codegen. No
filing crosses a repo boundary the writing session cannot reach.

**Explicitly recorded as no-impact (trail complete):** Item 3 (V3 above); Item 6
(self-referential tests — test-only, no SysML subset change); Item 7 (matrix
reconciliation — runs after this item's inputs settle; its own agentic-mbse impact, if
any, is F2/F4 REQ-side, not a modeling-guide change); Item 8 (dead-code — codegen-internal).

## Known Requirements

- **[HARD]** *(R2)* Every new or corrected validation check ships with a **negative
  fixture** in agentic-mbse's fixture layout and is shown to catch its trap on the Item-1
  fixture shapes. C7 (the D-F warning) is the only new check; it lands with its negative
  fixture and a silent-on-clean fixture. No check lands without a fixture.
- **[HARD]** Check designs mirror codegen's already-shipped behavior — they must not
  contradict the V1–V11 diagnostics or the modeling-assumptions supported subset. C7 mirrors
  the codegen-side silent-drop it warns about; a check that flags a shape codegen accepts is
  the defect class this epic exists to remove (re-run V2's sweep against the *new* accepted
  set: whole-plant idiom, subtype-aware constraints, Item-5 loud shapes).
- **[HARD]** Item-4 companion work is **verified, not redone** (V1). The four commits on
  `pipeline-truth-item4` are the landed coordinated pair; this item builds on them.
- **[NEED]** The consolidated impact list above is the contract: the plan works it row by
  row, the close-out reports each row done or filed, and a reader can trace any per-item
  recording to a row and a disposition (epic §6 traceability table).
- **[NEED]** The companion audit (A1/A2) produces a written verdict per primitive
  (covered / gap-found-and-fixed / gap-found-and-filed), not a silent pass.
- **[INFERRED]** agentic-mbse's L1–L6 runner, adapter, MODELING_GUIDE, sysml-conventions
  skill, and fixture conventions are as the Item-4 register notes and prior-epic PR body
  describe them (`agentic_mbse.validation`, the 6-level structure, `docs/patterns/`,
  `references/stencils.md`). The implement session confirms the exact layout, check-function
  naming, and fixture format before writing code — this spec session's permission scope is
  pinned to sysml-codegen (see Open Questions).
- **[INFERRED]** Item 5's deferred impact block (I5) is derivable from its spec/plan; the
  implement session extracts the concrete diagnostics rather than inventing them.

## Non-Goals

- **sysml-codegen production changes.** This item works in agentic-mbse and in this repo's
  docs/backlog only. Codegen behavior is frozen as of its own items; the checks and docs
  *describe* it. (S-F3/S-F4/S-F5 are dispositions recorded in BACKLOG, not codegen builds.)
- **Merging PR #7.** Its merge is the human's. This item records status and stacks on it.
- **Re-doing Item 4's landed work.** V1 is a spot-check, not a re-verification.
- **The syside vendor *report* / contacting Sensmetry.** R-VENDOR files-or-declines the
  note; it does not write a vendor report.
- **Building the FILE/keep-filed set** (C8 if kept filed, S-F3/S-F4, any audit gap too large
  to fix small). Filed as backlog, not implemented.
- **New codegen diagnostics.** No V-code is added here.
- **Constraint execution, EXPOSE_COMPUTED, non-uniform arrays** — epic-deferred, unchanged.

## Decisions (made at spec-time, autonomous run)

**B1 — Item 9 continues on the same `pipeline-truth-item4` branch; one companion PR for the
whole epic.** The epic asks: same branch as Item 4, or a new branch stacked on it?

- *Situation.* Item 4's four commits sit on `pipeline-truth-item4` (base `7f77510`), which is
  itself stacked on `upstream-findings-sync` (the prior epic's PR #7, still open). No PR
  exists yet for the epic's agentic-mbse work.
- *Chosen: same branch.* Item 9 is the epic's accumulation item and the only remaining
  agentic-mbse code; there is no independent reviewer boundary between "Item 4's coordinated
  pair" and "Item 9's sync" — both are *this epic's* agentic-mbse companion work. One branch,
  one PR keeps the epic's agentic-mbse story in one place, mirroring the prior epic's single
  companion PR (#7). A new stacked branch adds rebase/merge coordination for zero benefit.
- *PR base.* Open the companion PR against `upstream-findings-sync` while PR #7 is unmerged,
  so the diff shows only the epic's work (Item 4 + Item 9), not #7's commits. Retarget to
  `main` once #7 merges. If #7 is already merged at PR-creation time, base against `main`.
- *Risk.* If the human squashes/rebases #7 on merge, `pipeline-truth-item4` needs a rebase
  onto the merged `main`. This is true of any stacking choice; a single branch minimizes the
  number of branches to rebase. Accepted.

**B2 — Artifacts live in sysml-codegen, code lands in agentic-mbse.** This spec, the plan,
and the close-out live at `.project/active/pipeline-truth-sync/` in *this* repo, following
the prior-epic `validation-sync` precedent (its spec/plan/audit/close-out were all in
sysml-codegen even though code landed in agentic-mbse). The epic's Deliverables line naming
`agentic-mbse .project/active/...` is superseded by that precedent and the item prompt.

**B3 — The impact list is the deliverable; the plan sizes and sequences it under the guard.**
As the prior epic did: this spec builds the sourced table; the plan sizes each row against
the real agentic-mbse structure and honors the scope guard (must-land first). C7 is the one
must-land build; docs and dispositions are cheap; the audit is bounded.

**B4 — Recommendations, not pre-commitments, on the DECIDE rows.** C8 keep-filed (codegen
backstop exists), vendor-note decline (evaluation-time, no codegen impact), S-F3/S-F4
keep-filed (no consumer), S-F5 verify-then-decide. The implement session makes the final
call with agentic-mbse read access and records it; these are the spec's defaults.

## Scope guard

**1–1.5 days.** Not every row is equal under the guard; state the line:

- **Must-land.** **C7** (the D-F expression-RHS warning + negative + silent-on-clean fixture)
  — epic Item 9 §2, the one unbuilt check. **D1** (the whole-plant value idiom doc) — the
  headline teaching surface the epic exists to enable. **The traceability table** (SC-1/§6).
- **Expected to land (cheap).** D2/D3/D4/I5 docs; V1/V2/V3 verifies; the R-* and S-F*
  dispositions (recording a decision is cheap); the A1/A2 audit verdicts.
- **May file if a row balloons.** An audit finding (A1/A2) whose fix needs a structural
  change files as an agentic-mbse backlog item rather than being built here. C8's pre-warn
  stays filed unless it is a small check-plus-fixture. A doc section that balloons files its
  remainder.

The plan sizes each row against the real runner and honors this ordering: C7 + D1 first,
then the cheap docs/verifies/dispositions, then the audit, filing throughout.

## Open Questions / Deferred to plan

This item has no design phase (epic budget: spec + plan + execute). These resolve in the
plan or the first execute step from a session with agentic-mbse read access.

- **agentic-mbse repo state — confirm before coding (sandbox-blocked here).** This spec
  session's permission scope is pinned to sysml-codegen; `/home/reid/1cfe/agentic-mbse` is
  unreadable and its git is un-runnable in this non-interactive run (a known orchestration
  trap). The plan/execute session must first confirm, live: PR #7's merge status; that the
  four Item-4 commits (`64a097e`, `cc64b1d`, `bc24ae3`, `bc196df`) are on
  `pipeline-truth-item4`; the L1–L6 runner layout and check-function naming; where negative
  fixtures live and their format; the MODELING_GUIDE / `docs/patterns/` section structure;
  and that the C8 filing + vendor-note draft from the prior epic's Phase 4 (`08cd595`) are
  in agentic-mbse's backlog. If any contradicts the impact-list assumptions, surface it
  before building. (This mirrors the prior-epic spec's identical deferral.)
- **S-F5 verification** — whether an Item-5 test already asserts an unresolvable ref emits
  its warning (INV-6 leg). Resolved by reading Item 5's landed tests at execute; discharge or
  decide.
- **Item-5 impact derivation (I5)** — the exact modeler-facing diagnostics folded into
  D2/D3, read from Item 5's spec/plan/audit at execute.
- **Negative-fixture reuse** — whether agentic-mbse can point C7's check at a sysml-codegen
  fixture (`plant_value_shapes`) or must author a mirror fixture in its own tree — a plan
  call once the fixture convention is confirmed.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 9; cross-cutting R2 — the
  per-item impact-list mechanism this item executes; R1 negative-fixture addition).
- **Prior-epic template (followed here):**
  `.project/active/validation-sync/{spec,plan,audit,close-out}.md` (Item 12 of
  UPSTREAM-FINDINGS — the consolidated-impact-list + traceability-table pattern);
  `.project/active/AGENTIC_MBSE_PR_BODY.md` (the companion PR body, C7/C8/F6/vendor-note
  provenance).
- **Per-item recordings (raw material for the table):**
  - Item 1: `.project/active/plant-value-fixtures/spec.md` §"agentic-mbse impact — Item 9
    accumulation list".
  - Item 2: `.project/active/whole-plant-resolution/spec.md` §"agentic-mbse Impact (Item 9
    accumulation)".
  - Item 4: `.project/active/subtype-enumeration/register-update-pending.md` + `plan.md`
    Phases 5–7 (the landed companion work; commits `64a097e`/`cc64b1d`/`bc24ae3`/`bc196df`).
  - Item 5: `.project/active/silent-failure-hardening/{spec,plan,audit}.md` (impact block
    DEFERRED — derive I5).
  - Item 3: `.project/active/fusiontea-acceptance/run-report.md` §Item-9/R2 (none new).
- **Contract mirrored by the checks/docs:**
  `docs/architecture/modeling-assumptions.md` (§5 retyping, §8 constraints, V1–V11).
- **Companion-audit pointer:** `.project/research/20260706_pipeline-truth-discovery.md` §D3
  cross-repo pointer (line 115) + item 8 (line 289).
- **Backlog:** `.project/backlog/BACKLOG.md` (SYNC-F3/F4/F5).
- **Implementation target:** `/home/reid/1cfe/agentic-mbse` (branch `pipeline-truth-item4`)
  — adapter, L1–L6 validators, MODELING_GUIDE, `docs/patterns/`, sysml-conventions skill.
- **Memory:** `agentic-mbse-repo-path` (canonical checkout + sandbox note),
  `orchestrated-run-gotchas` (cross-repo permission trap), `multihop-expose-offline-parity`
  (D3 truncation context).
- **Plan:** `.project/active/pipeline-truth-sync/plan.md` (to be created).

---

**Next Steps:** After approval, proceed to `/_my_plan` — the plan confirms the agentic-mbse
structure live, sizes each impact-list row, sequences C7 + D1 first under the 1–1.5 day
guard, and schedules the companion audit and the dispositions.

ARTIFACT: .project/active/pipeline-truth-sync/spec.md
