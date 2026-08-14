# Verification Record: ADR, Product Promise, and Agent-Facing Documentation Sync (CONSTRAINT-SEMANTICS Item 7)

**Created:** 2026-08-14 · **Branches:** codegen `item7-rebuild`; agentic-mbse worktree
`/home/reid/1cfe/agentic-mbse-item7-rebuild` (`item7-rebuild`); TEAx `/home/reid/1cfe/teax`
(`constraint-semantics-item3`)
**Spec:** `spec.md` · **Plan:** `plan.md`
**Record shape copied from:** `.project/completed/20260813_constraint-semantics-contract-amendments/verification.md`
(Item 1's executed record; its Appendix D defines the shape)

This file is the item's evidence. It carries the recorded sweep (pre-edit and post-edit), the
per-hit disposition, and the results of every mechanical check. SC2 asserts a **three-repository**
claim, so all three repositories are recorded here in one set of tables — an auditor checking that
claim reads one file, not three.

---

## Sweep scope, and what is deliberately outside it

### Codegen and agentic-mbse — the DD5 scope

**In scope (DD5):** `docs/`, `src/`, `tests/`, `scripts/`, `README.md`, `CLAUDE.md`,
`.project/concepts/`, `.project/backlog/`.

**Excluded (DD5), and why:** `.project/research/`, `.project/completed/`, `.project/active/`. These
are dated records of what was believed when. The lifecycle contract's own reading rule (`:19-21`)
already makes them provenance that cannot override an explicit correction in the contract.
Rewriting them would falsify the audit trail. The boundary is recorded here so it is auditable
rather than silent.

**Scope additions made by this item, recorded.** Adding a scope directory is permitted (Item 1
Appendix D: "adding a term is allowed, dropping one is not"); dropping one is not.

- `.claude/` in both repositories — agent prompts and skills are shipped surfaces that teach, and
  they sit under neither `docs/` nor any other DD5 directory. This item's epic scope 3 names
  `.claude/skills/sysml-conventions/SKILL.md` explicitly. Item 1 added `claude/` in the companion
  for the same reason.
- agentic-mbse `BACKLOG.md` sits at the repository root, not under `.project/backlog/`. Swept at
  its actual location.

### TEAx — the scope this item defines (plan D-4)

No TEAx sweep scope existed before this item. S1–S5 transfer **unchanged**; no local term is added.
The plan-stage pre-run found no TEAx idiom the five terms miss: S1, S2, S3 and S5 return zero, and
every one of S4's nine hits is TEAx's own migration text naming `all_satisfied` as the *retired*
token. The exclusions, not the terms, are the load-bearing part of this boundary.

**In scope:** `docs/`, `README.md`, `CLAUDE.md`, `.claude/`, and `packages/*/` source and tests,
with `--include=*.md --include=*.py --include=*.sysml`.

**Excluded, and why:**

- `.venv/` and `node_modules/` — installed third-party code, not authored here.
- `.pytest_cache/` — generated.
- `thoughts/` and `.project/{completed,active,research}/` — dated records, the DD5 exclusion rule
  and the same reasoning.

**Deliberately kept in scope:** the generated fixture trees under
`packages/teax-simkit/simkit/tests/evaluation/fixtures/*/package_live/`. They are dispositioned as
generated output rather than excluded, because they are what a reader of the test suite actually
sees.

### Vendored-corpora sub-exclusion (agentic-mbse), recorded with its reason

Carried forward from Item 1's recorded precedent (`verification.md:32-40`). agentic-mbse's
`docs/sysmlv2/` and `docs/syside/` trees are third-party reference material — the OMG SysML v2
specification documents, the SysML v2 standard library, and generated SysIDE API documentation.
They are not project-authored guidance, this item has no authority to amend them, and editing them
would corrupt a reference corpus. Their hits are aggregated below by directory with counts and file
lists rather than one row per line, and **the aggregation is flagged** so an auditor sees exactly
what was set aside. Every project-authored hit gets its own row.

This is a recorded deviation from one-row-per-hit, not a silent one, and it is load-bearing: the
vendored trees carry **64 of agentic-mbse's 80 raw hits**.

---

## Sweep terms

Item 1's five-term method, S1–S5 (`design.md:1202-1218`). The epic's SC2 calls this the
"three-sweep method"; that label is superseded and is named here once so the citation trail back to
SC2 still resolves.

| # | Term | Command shape |
|---|------|---------------|
| S1 | retired test name | `grep -rn "test_constraint_migration_mapping" <scope>` |
| S2 | `require constraint` taught as a check | `grep -rn "require constraint" <scope>` |
| S3 | plain-constraint-enforces claims | `grep -rniE "constraint[s]? (are \|is )?(enforced\|checked\|verified\|evaluated\|a gate\|gates\|blocks)\|enforced (gate\|constraint)\|plain constraint.*(execut\|enforc\|gate\|check\|verif\|evaluat\|block)" <scope>` |
| S4 | the superseded headline precedence | `grep -rniE "all[_ ]satisfied\|else any assessed\|any assessed result" <scope>` |
| S5 | `assume`/`satisfy` taught as a check | `grep -rn "assume constraint\|satisfy requirement" <scope>` |

All five run with `--include=*.md --include=*.py --include=*.sysml`.

**S4 runs pre-edit.** The collision is real: this item's amendment notes quote the superseded
precedence verbatim, so a post-edit S4 would hit the amendments themselves. Item 1 resolved this in
advance (`design.md:1220-1222`) — run S4 before the edits, and disposition any post-edit hit inside
an amendment note as "quoted supersession, correct as written."

### Raw hit counts, pre-edit (run 2026-08-14, before any edit in any repository)

| Repo | S1 | S2 | S3 | S4 | S5 | Total |
|---|---|---|---|---|---|---|
| codegen | 0 | 13 | 7 | 20 | 5 | **45** |
| agentic-mbse (all) | 0 | 21 | 8 | 0 | 51 | **80** |
| agentic-mbse (project-authored) | 0 | 6 | 4 | 0 | 6 | **16** |
| agentic-mbse (vendored, aggregated) | 0 | 15 | 4 | 0 | 45 | **64** |
| TEAx | 0 | 0 | 0 | 9 | 0 | **9** |

**Divergence from the plan's sizing run, recorded.** The plan estimated the vendored share of
agentic-mbse's hits at "roughly S2 15 / S3 4 / S5 33" (~44). The executed sweep measures S5's
vendored share at **45**, not 33 — 35 of them in
`docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md` alone. The project-authored counts (6/4/6) are
what the item actually acts on and they are unchanged in character; only the aggregated set is
larger than estimated. Every other sizing number matched the executed run exactly.

---

## Table 1 — Pre-edit sweep hits and dispositions

Run 2026-08-14, before any edit in any of the three repositories. One row per raw hit, except the
vendored corpora, aggregated with counts per the flagged sub-exclusion above. A hit left unchanged
is a disposition and gets its row.

### Codegen (45 rows)

| # | Term | File:line | Quoted hit | Disposition | Note |
|---|------|-----------|------------|-------------|------|
| 1 | S2 | `docs/architecture/modeling-assumptions.md:472` | "`require constraint`, an `assume constraint`, and the requirement-side" | correct as written | inside §8's **unassessed** bullet — a classification statement naming the forms that never execute, which is the corrected teaching |
| 2 | S2 | `docs/architecture/modeling-assumptions.md:553` | "enforcement opt-in: a bare `constraint`, a `require constraint`, an `assume constraint`, and a" | correct as written | §8 "What a modeler needing an enforced gate should do" — Item 1's corrected D1 text; it names these forms as *never* executing |
| 3 | S2 | `src/sysml_codegen/generation/coverage.py:166` | "a requirement-side ``require constraint``, and a ``satisfy`` reference state a condition without asking for it to be checked" | correct as written | docstring stating the corrected rule; also out of this item's edit authority (no code changes) |
| 4 | S2 | `tests/fixtures/constraint_domain_satisfy_calc_def/model.sysml:11` | "require constraint within {" | correct as written | fixture model source; executable text, and no fixture changes |
| 5 | S2 | `tests/fixtures/constraint_domain_satisfy/model.sysml:16` | "require constraint within {" | correct as written | same |
| 6 | S2 | `tests/fixtures/item4_require/model.sysml:5` | "the `require constraint` shape as a reported plain ConstraintUsage, and a" | correct as written | classification statement in a fixture; Item 1 dispositioned the same row |
| 7 | S2 | `tests/fixtures/item4_require/model.sysml:17` | "`require constraint` is a plain ConstraintUsage reached through a" | correct as written | classification statement |
| 8 | S2 | `tests/fixtures/item4_require/model.sysml:19` | "require constraint within_budget {" | correct as written | fixture model source; executable text |
| 9 | S2 | `tests/unit/data/expected-coverage.md:22` | "A bare `constraint …`, a `require constraint …` inside a requirement, and a `satisfy` reference are **not** asserted." | correct as written | reviewed expectation data; states the corrected rule |
| 10 | S2 | `tests/unit/data/expected-coverage.md:226` | "`model.sysml:16` — `require constraint within` inside a requirement definition" | correct as written | source-evidence citation in expectation data |
| 11 | S2 | `.project/backlog/epic_constraint_semantics_contract.md:235` | "at companion `claude/agents/sysml-expert.md:124` the `require constraint` example was kept inside its `requirement def`" | correct as written | Item 1's recorded D5-a deviation; a decision record, not teaching |
| 12 | S2 | `.project/backlog/BACKLOG.md:282` | "and require constraint\" support while using the same blind query (line 50) — check" | correct as written | dated historical finding block naming modules the cutover retired; Item 1 dispositioned this identical hit the same way (`verification.md` row 16) |
| 13 | S2 | `.project/backlog/BACKLOG.md:283` | "`require constraint` (`RequireConstraintUsage`?) too." | correct as written | same finding block, continuation line |
| 14 | S3 | `docs/architecture/modeling-assumptions.md:552` | "**What a modeler needing an enforced gate should do.** Use the assert family. It is the only" | correct as written | Item 1's corrected heading; the sentence it introduces is the fix |
| 15 | S3 | `tests/fixtures/catf_mfe_gated/PROVENANCE.md:393` | "it encodes exactly what the authored constraint checked," | correct as written | Item 5 owns this file — **cite, do not rewrite** (spec Non-Goals). A derivation record describing one authored predicate, not a claim that constraints are checked generally |
| 16 | S3 | `.project/backlog/BACKLOG.md:214` | "[CALCDEF-GATE-IMPLEMENTATION] Implement calculation-definition constraint gates" | correct as written | a backlog item title naming unbuilt work; "gates" here is the asserted-gate sense |
| 17 | S3 | `.project/backlog/BACKLOG.md:862` | "a plain constraint could additionally be *evaluated* and surfaced as a non-gating advisory was left open as a candidate" | correct as written | a filed candidate, explicitly *non-gating* and explicitly not landed |
| 18 | S3 | `.project/backlog/epic_constraint_semantics_contract.md:62` | "enforced gates; requirement-side forms remain visible and non-executable." | correct as written | the corrected rule stated in the epic's own scope |
| 19 | S3 | `.project/backlog/epic_constraint_semantics_contract.md:292` | "Codegen and agentic-mbse contain no remaining statement that a plain or requirement-side constraint is an enforced gate." | correct as written | a **negated** success criterion — it asserts the absence of the claim |
| 20 | S3 | `.project/backlog/epic_constraint_semantics_contract.md:429` | "a plain constraint with a blocked predicate still generates and catalogs as unassessed." | correct as written | states the corrected non-halting behavior |
| 21 | S4 | `docs/architecture/modeling-assumptions.md:601` | "indeterminate, then all satisfied, then not assessed.\" Frozen companion LC-E11: \"Report headline" | correct as written | ADR-009 §9 "What the contract said" — quoted supersession, immediately followed by "What it says now" |
| 22 | S4 | `docs/architecture/modeling-assumptions.md:603` | "assessed result → `all_satisfied`; else `not_assessed`.\"" | correct as written | same quoted-supersession block |
| 23 | S4 | `docs/architecture/modeling-assumptions.md:621` | "`all_satisfied` was renamed rather than redefined, so a stale reader refuses by name" | correct as written | ADR-009's account of the rename |
| 24 | S4 | `src/sysml_codegen/generation/coverage.py:3` | "A report that says `all_satisfied` when two of nine gates ran is not wrong about the two —" | correct as written | module docstring explaining why the token was retired; no code changes |
| 25 | S4 | `src/sysml_codegen/contracts/versions.py:23` | "the ``headline`` vocabulary is replaced, not extended — ``all_satisfied`` becomes" | correct as written | version-history docstring; quoted supersession |
| 26 | S4 | `tests/unit/conftest.py:24` | "which is the failure mode the retired `all_satisfied` headline shipped under." | correct as written | names it as retired |
| 27 | S4 | `tests/unit/test_report_precedence.py:147` | "\"\"\"B5: a stale producer writing `all_satisfied` is refused at construction, not read.\"\"\"" | correct as written | the test that *pins* the refusal |
| 28 | S4 | `tests/unit/test_report_precedence.py:154` | "headline=\"all_satisfied\"," | correct as written | the refused input in that test |
| 29 | S4 | `tests/conformance/test_runtime_contract_version.py:23` | "replaced the headline vocabulary (`all_satisfied` -> `full_satisfaction`," | correct as written | states the replacement |
| 30 | S4 | `tests/conformance/golden/zero_entry_package/modules/constraints/constraintreportaggregatormodule.py:58` | "# `all_satisfied` meant \"nothing that arrived failed\", whatever fraction arrived." | correct as written | **generated golden output**, byte-identity-gated (memory: `generated-baselines-format-exempt`). The comment explains the retired meaning; editing it would break the gate and is a code change |
| 31 | S4 | `tests/execution/test_constraint_coverage_characterization.py:7` | "one gate assessed and one gate never checked used to report `all_satisfied`," | correct as written | "used to" — the characterization test's own history |
| 32 | S4 | `.project/concepts/constraint-execution-and-design-space-studies.md:99` | "otherwise one or more satisfied assertions gives `all_satisfied`; zero assertions gives `not_assessed`." | correct as written (as provenance) | **Disposition carried from Item 1 row 25.** `Status: Proposed`; its own banner (`:9`) defers to the `-claude.md` design, and the lifecycle contract's reading rule (`:19-21`) demotes both to provenance. The contract governs |
| 33 | S4 | `.project/concepts/constraint-execution-and-design-space-studies.md:198` | "documented-only constraints never create a false `all_satisfied` result." | correct as written (as provenance) | same reason as row 32; carried from Item 1 row 26 |
| 34 | S4 | `.project/concepts/constraint-execution-lifecycle-requirements.md:325` | "assessed result → `all_satisfied`; else `not_assessed`.\" See contract invariant 33 (amended)." | correct as written | already carries its own amendment pointer — quoted supersession |
| 35 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:52` | "A report can claim `all_satisfied` over partial assessment," | correct as written | the epic's statement of the **problem** it fixed |
| 36 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:89` | "`all_satisfied` requires every applicable asserted gate to be assessed and pass;" | correct as written | the epic's statement of the strengthened rule |
| 37 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:218` | "The four `all_satisfied` assertions in `tests/execution/` were corrected by **Item 3**'s token" | correct as written | a completion record |
| 38 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:583` | "⚠️ The report has no authored or excluded population, and `all_satisfied` means only that some" | correct as written | a dated ⚠️ finding block recording the pre-epic condition |
| 39 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:587` | "⚠️ Hand-off from Item 1 (audit M-1): four `all_satisfied` assertions in codegen" | correct as written | dated hand-off record; row 37 records its discharge |
| 40 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:625` | "`all_satisfied` is impossible when any applicable asserted usage lacks assessment." | correct as written | a ticked success criterion, stated as an impossibility |
| 41 | S5 | `docs/architecture/modeling-assumptions.md:472` | "`require constraint`, an `assume constraint`, and the requirement-side" | correct as written | same line as row 1; S2 and S5 both match it |
| 42 | S5 | `docs/architecture/modeling-assumptions.md:553` | "a bare `constraint`, a `require constraint`, an `assume constraint`, and a" | correct as written | same line as row 2 |
| 43 | S5 | `tests/fixtures/constraint_domain_satisfy_calc_def/model.sysml:24` | "satisfy requirement budget_met : MassBudget;" | correct as written | fixture model source |
| 44 | S5 | `tests/fixtures/constraint_domain_satisfy/model.sysml:26` | "satisfy requirement budget_met : MassBudget;" | correct as written | fixture model source |
| 45 | S5 | `.project/concepts/constraint-execution-and-design-space-studies-claude.md:88` | "requirement-owned require/assume constraints … and plain non-asserted constraint usages … are catalog entries, never executions" | correct as written | already states the never-executes rule; provenance document (row 32's reasoning). Carried from Item 1 row 34 |

**Codegen fix-here count from the sweep: zero.** Item 1 swept this repository with the same five
terms and corrected what it found; nothing has regressed. The codegen corrections this item makes
(Phase 4) are **not** sweep hits — they are named obligations from the epic and from Items 8 and 2,
and the sweep's terms do not reach them:

- `modeling-assumptions.md:530` — the unit-on-binding paragraph, false since Item 8 landed. No S1–S5
  term matches "carried, not checked."
- `modeling-assumptions.md:451` and the §8 BLOCK bullet — the blanket BLOCK-halts statement, which
  the Phase 2 item3-F2 amendment scopes to reaching gates. Matched by neither S3 nor S4.
- The missing disposition vocabulary and severity-by-cause teaching. A sweep finds wrong text; it
  cannot find absent text.

This is recorded because "the sweep found nothing to fix in codegen" is otherwise easy to misread as
"codegen needed nothing."

### agentic-mbse — project-authored (16 rows)

| # | Term | File:line | Quoted hit | Disposition | Note |
|---|------|-----------|------------|-------------|------|
| 46 | S2 | `docs/patterns/constraints.md:111` | "require constraint ValidInput {" | correct as written | inside the "Require Constraint" syntax example. Kept in its requirement-side sense; see row 50, which states the non-execution rule for the same form. Item 1's D5-a precedent applies: swapping the form would teach invalid requirement modeling |
| 47 | S2 | `docs/patterns/constraints.md:116` | "require constraint NonZeroDenominator {" | correct as written | same example block |
| 48 | S2 | `tests/fixtures/constraint_fact_shapes/source_forms.sysml:15` | "require constraint below_limit {" | correct as written | fixture model source; no fixture changes |
| 49 | S2 | `docs/patterns/semantic-operators.md:520` | "`require constraint` — a requirement-side precondition. It is cataloged and visible; it is not" | correct as written | states the corrected rule |
| 50 | S2 | `docs/patterns/syntax-reference.md:185` | "`require constraint` - Precondition" | correct as written | a keyword-table gloss, not a claim about execution |
| 51 | S2 | `.claude/agents/sysml-expert.md:124` | "require constraint { system.flowRate >= requiredFlow }" | correct as written | **Item 1's recorded D5-a deviation**, judged sounder than the design's instruction and standing (`epic:233-237`): the example was kept inside its `requirement def` and given a settled-semantics sentence rather than swapped to `assert constraint` |
| 52 | S3 | `docs/patterns/common-mistakes.md:244` | "## Mistake 8: Expecting a Plain Constraint to Be Checked" | correct as written | a heading that names the mistake in order to correct it |
| 53 | S3 | `docs/patterns/common-mistakes.md:246` | "### Don't: Plain constraint block" | correct as written | the anti-pattern label |
| 54 | S3 | `docs/patterns/constraints.md:221` | "### Not a check: plain constraint block (no prefix)" | correct as written | the corrected heading Item 1 wrote |
| 55 | S3 | `docs/patterns/semantic-operators.md:493` | "### Not a check: plain constraint block" | correct as written | same |
| 56 | S5 | `docs/patterns/constraints.md:125` | "assume constraint SteadyState {" | correct as written | syntax example; row 49's companion sentence at `semantic-operators.md:522` states the rule |
| 57 | S5 | `docs/patterns/constraints.md:130` | "assume constraint IdealGas {" | correct as written | same example block |
| 58 | S5 | `tests/fixtures/constraint_fact_shapes/source_forms.sysml:12` | "assume constraint positive_limit {" | correct as written | fixture model source |
| 59 | S5 | `tests/fixtures/constraint_fact_shapes/source_forms.sysml:87` | "satisfy requirement satisfied_limit : LimitRequirement by sample;" | correct as written | fixture model source |
| 60 | S5 | `docs/patterns/semantic-operators.md:522` | "`assume constraint` — a modeling assumption. It is cataloged and visible; it is not executed and" | correct as written | states the corrected rule |
| 61 | S5 | `docs/patterns/syntax-reference.md:186` | "`assume constraint` - Assumption" | correct as written | keyword-table gloss |

**agentic-mbse fix-here count from the sweep: zero.** Same reading as codegen — Item 1 corrected
this repository and nothing regressed. The Phase 4 agentic-mbse work is **absent** teaching, which
no sweep term can surface: `@inapplicable:` authoring, the eligible-plus-inapplicable refusal (D9),
the D9 authoring-time advisory, and the bindings-form-vs-inline-predicate marker rule. Verified
absent: `grep -c "inapplicable" docs/patterns/constraints.md` → **0**.

### agentic-mbse — vendored corpora (aggregated, 64 hits, flagged)

**Not edited.** Third-party reference material; this item has no authority to amend it. Aggregated
by file with counts, per the sub-exclusion recorded above.

| # | Term | Directory / file | Hits | Disposition |
|---|------|------------------|------|-------------|
| V1 | S2 | `docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md` | 9 | out of class — OMG specification text |
| V2 | S2 | `docs/sysmlv2/SysML_SysTemp_MultiAgent/full_document.md` | 2 | out of class |
| V3 | S2 | `docs/sysmlv2/SysML_IntroGuide_v2/full_document.md` | 1 | out of class |
| V4 | S2 | `docs/sysmlv2/SysML_Spec_v2_Part2/full_document.md` | 1 | out of class |
| V5 | S2 | `docs/sysmlv2/Cheatsheet/sysml_textual_notation_cheatsheet.md` | 1 | out of class |
| V6 | S2 | `docs/sysmlv2/stdlib/Domain Libraries/Analysis/TradeStudies.sysml` | 1 | out of class — SysML v2 standard library |
| V7 | S3 | `docs/sysmlv2/SysML_FormalMethodsAerospace/full_document.md` | 2 | out of class |
| V8 | S3 | `docs/sysmlv2/SysML_IntegratingReasoning/full_document.md` | 1 | out of class |
| V9 | S3 | `docs/sysmlv2/stdlib/Systems Library/Items.sysml` | 1 | out of class — standard library |
| V10 | S5 | `docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md` | 35 | out of class |
| V11 | S5 | `docs/syside/python/v0.8.4/syside/FormatOptions.md` | 4 | out of class — generated SysIDE API docs |
| V12 | S5 | `docs/syside/v0.8.1/api/generated/syside.FormatOptions.md` | 2 | out of class — generated SysIDE API docs |
| V13 | S5 | `docs/sysmlv2/SysML_Spec_v2_Part2/full_document.md` | 2 | out of class |
| V14 | S5 | `docs/sysmlv2/stdlib/Systems Library/Views.sysml` | 1 | out of class — standard library |
| V15 | S5 | `docs/sysmlv2/SysML_Spec_v2_Part1/INDEX.md` | 1 | out of class — index of the specification above |

**Aggregation total: 64 hits across 12 distinct files, all under `docs/sysmlv2/` or `docs/syside/`.**
15 + 4 + 45 = 64 = the S2/S3/S5 vendored counts in the raw-count table.

### TEAx (9 rows)

Every hit is S4, and every one names `all_satisfied` as the **retired** token. This is the
quoted-supersession class the S4 collision rule describes, already correct as written before this
item ran. Item 3 corrected four TEAx sites; the sweep confirms it held.

| # | Term | File:line | Quoted hit | Disposition | Note |
|---|------|-----------|------------|-------------|------|
| 62 | S4 | `packages/teax-simkit/simkit/tests/evaluation/test_headline_vocabulary.py:3` | "Item 3 renamed `all_satisfied` to `full_satisfaction` *on purpose*" | correct as written | the test module that pins the rename |
| 63 | S4 | `…/test_headline_vocabulary.py:43` | "UNKNOWN_TOKENS = [\"all_satisfied\", \"invented_token\"]" | correct as written | the retired token used as a **negative** fixture |
| 64 | S4 | `…/test_headline_vocabulary.py:124` | "canonical_headline(\"all_satisfied\")" | correct as written | the call the test asserts must refuse |
| 65 | S4 | `…/tests/evaluation/fixtures/zero_channel/package_live/modules/constraints/constraintreportaggregatormodule.py:58` | "# `all_satisfied` meant \"nothing that arrived failed\", whatever fraction arrived." | correct as written — **generated output** | in scope per D-4 and dispositioned, not excluded: it is what a reader of the suite sees. Regenerating it is a code change |
| 66 | S4 | `…/fixtures/sealed_package/package_live/…/constraintreportaggregatormodule.py:58` | same | correct as written — generated output | same |
| 67 | S4 | `…/fixtures/f1_arithmetic/package_live/…/constraintreportaggregatormodule.py:60` | same | correct as written — generated output | same |
| 68 | S4 | `…/fixtures/excluded_only/package_live/…/constraintreportaggregatormodule.py:58` | same | correct as written — generated output | same |
| 69 | S4 | `packages/teax-simkit/simkit/evaluation/evidence.py:47` | "``all_satisfied`` became ``full_satisfaction`` because state 3's meaning strengthened from" | correct as written | migration docstring |
| 70 | S4 | `packages/teax-simkit/simkit/evaluation/package_load.py:40` | "a package built before that item emits the retired headline token ``all_satisfied`` and carries" | correct as written | the stale-package refusal path's docstring |

**TEAx fix-here count from the sweep: zero.** The Phase 4 TEAx work is absent teaching, verified
absent: `grep -cE "full_satisfaction|partial_coverage" docs/evaluation-and-study.md` → **0**.

---

## Table 1 validation

- **Row count.** 70 individual rows + 15 aggregation rows covering 64 vendored hits. Individual
  rows: 45 codegen + 16 agentic-mbse project + 9 TEAx = 70. Raw hits: 45 + 80 + 9 = 134.
  70 + 64 = 134. ✅ Every raw hit is accounted for.
- **Clean companion trees before any edit.** `git status --short` returned empty in
  `/home/reid/1cfe/agentic-mbse-item7-rebuild` (branch `item7-rebuild`) and `/home/reid/1cfe/teax`
  (branch `constraint-semantics-item3`), verified 2026-08-14 before this phase wrote anything. ✅
- **No fourth item3-F2 site.** `grep -rn "item3-F2" .project/active/ .project/backlog/` returns the
  three sites the spec names (`.project/active/constraint-semantics-contract/spec.md`, the epic
  residual) plus this item's own artifacts. `grep -rn "halts generation" .project/concepts/ docs/`
  returns the lifecycle contract's invariant 1 and three unrelated statements about extraction
  diagnostics and INV-2. No fourth carrier. ✅

---

## Scope correction and surfaced premise conflict (found in Phase 4, 2026-08-14)

Phase 4 found that the plan's model of the agent surfaces is wrong, in a way that changes what SC2
and SC3 can honestly claim. Recorded here rather than resolved silently (capture-fidelity law 4).

### What is actually there

**Codegen has no agent surfaces of its own.** Every file under codegen `.claude/agents/` and
`.claude/skills/sysml-conventions/` is a **symlink**, and all of them resolve to
`/home/reid/1cfe/agentic-mbse/claude/…` — the **main agentic-mbse checkout**, currently on branch
`elaborate-first-salvage`. Not the authorized worktree. Verified by `readlink -f`.

The plan's Phase 4 instruction "check the codegen equivalents the same way" rests on there being
codegen equivalents. There are none — they are the same files, reached by a second path.

**agentic-mbse tracks two divergent copies of the agent definitions.** `claude/` (37 tracked files)
and `.claude/` (23 tracked files) both exist and `sysml-expert.md` **differs** between them:

- `claude/agents/sysml-expert.md` carries Item 1's D5-a correction (the settled-semantics sentence
  after the `require constraint` example) and portable `{SYSML_DOCS_PATH}` placeholders.
- `.claude/agents/sysml-expert.md` carries **neither** — no D5-a sentence, and hardcoded absolute
  paths. Item 1 corrected `claude/` only.

**The checkout codegen actually reads is uncorrected.** In `/home/reid/1cfe/agentic-mbse` on
`elaborate-first-salvage`: `claude/agents/sysml-expert.md` has no D5-a sentence, and
`claude/skills/sysml-conventions/SKILL.md:136` still reads
`assert constraint TempLimit { temperature < 1000 [K] }`. Item 1's and this item's corrections live
on the `item7-rebuild` branch and have not reached that branch.

### Sweep-scope defect this exposes in Table 1

`grep -r` does not follow symlinked files. **Codegen's `.claude/` tree was therefore swept as empty**
— the recorded codegen S1–S5 counts (45) exclude it. Had the symlinks been followed, S2 would have
picked up `sysml-expert.md:124`. Table 1's codegen rows are correct for the files codegen *owns*;
they were never a statement about the symlink targets.

Correcting it: the agentic-mbse worktree's `claude/` tree was **not** in the Phase 1 agentic-mbse
scope either (that run used `.claude`). Swept in Phase 4, results below. Both trees are now covered.

| # | Term | File:line | Quoted hit | Disposition | Note |
|---|------|-----------|------------|-------------|------|
| 71 | S2 | agentic-mbse `claude/agents/sysml-expert.md:124` | "require constraint { system.flowRate >= requiredFlow }" | correct as written | Item 1's D5-a deviation, standing |
| 72 | S2 | agentic-mbse `claude/agents/sysml-expert.md:132` | "`require constraint` inside a `requirement def` is the correct way to state a requirement's required constraint" | correct as written | **this is Item 1's correction itself** |

S1, S3, S4, S5 return zero over `claude/`. Raw-hit total rises 134 → 136; rows 70 → 72.

### What was fixed in bounds

- agentic-mbse worktree `claude/skills/sysml-conventions/SKILL.md` — the stale example replaced.
  This is the authored copy the codegen symlinks point at, so the fix propagates to codegen readers
  when the branch merges.
- agentic-mbse worktree `.claude/agents/sysml-expert.md` — brought level with `claude/` by adding
  Item 1's D5-a sentence. It was a tracked, shipped surface still teaching the uncorrected shape.

### Named residual — SC2/SC3 are not fully discharged for codegen agent readers

**A Claude session in the codegen checkout today still reads the superseded constraint example**,
because its symlinks resolve to `/home/reid/1cfe/agentic-mbse` on `elaborate-first-salvage`, which
this item may not edit (hard boundary: agentic-mbse edits are worktree-only). The falsifier is
therefore **open** on that one path until the `item7-rebuild` branch reaches the branch those
symlinks resolve to.

Evidence, run post-edit: `grep -c "assert constraint TempLimit" .claude/skills/sysml-conventions/SKILL.md`
in codegen → **1** (expected 0 by the plan's Phase 4 check). The count is 1 because the file read is
the out-of-bounds one; the in-bounds copy of the same file reads 0.

**In-boundary excursion, caught and reverted.** Before the symlink topology was understood, one edit
was written through the codegen path and therefore landed in `/home/reid/1cfe/agentic-mbse` on
`elaborate-first-salvage`. It was reverted with `git checkout --` on discovery. That checkout is
verified clean (`git status --short` → empty, branch unchanged). No commit was made there and
nothing was pushed. Recorded because a silent revert is not a record.

---

## Table 2 — Post-edit sweep

*Filled in Phase 6.*

---

## Mechanical checks

*Filled in Phase 6.*
