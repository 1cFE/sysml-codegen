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

Evidence, run post-edit — **corrected at audit, 2026-08-14 (audit finding A-1).** The originally
recorded discriminator was `grep -c "assert constraint TempLimit" …/SKILL.md` → 1 in codegen, with
"the in-bounds copy of the same file reads 0." **That is false.** The corrected in-bounds file also
returns 1, because the corrected text *keeps* `assert constraint TempLimit { temperature < 1000 [K] }`
at `:151` as a deliberately labelled **negative** example under rule 2 ("Bind formals; don't inline
the predicate"). The count does not discriminate the two files at all.

The residual itself is unchanged and independently reproduced. The discriminator that actually
separates them is the corrected teaching's own text:

| Probe | codegen `.claude/skills/sysml-conventions/SKILL.md` (symlink → out-of-bounds) | agentic-mbse worktree `claude/skills/sysml-conventions/SKILL.md` (in-bounds) |
|---|---|---|
| `grep -c 'blessed shape is bindings-only'` | **0** | **1** |
| `grep -c '@inapplicable:'` | **0** | **3** |
| `readlink -f` | `/home/reid/1cfe/agentic-mbse/claude/skills/sysml-conventions/SKILL.md` | n/a |

The out-of-bounds copy still carries the stale example as the *blessed* shape at
`/home/reid/1cfe/agentic-mbse/claude/skills/sysml-conventions/SKILL.md:136`. Verified at audit.

**In-boundary excursion, caught and reverted.** Before the symlink topology was understood, one edit
was written through the codegen path and therefore landed in `/home/reid/1cfe/agentic-mbse` on
`elaborate-first-salvage`. It was reverted with `git checkout --` on discovery. That checkout is
verified clean (`git status --short` → empty, branch unchanged). No commit was made there and
nothing was pushed. Recorded because a silent revert is not a record.

---

## Verification-matrix reconciliation (Phase 5, 2026-08-14)

### The recount, and what it falsified

Counted from the tables, never from the summary block (project memory
`verification-matrix-drift-modes`). Method: for each `^| REQ-` row, take the **last** field matching
a status keyword — a plain column-position or `grep -c` count is wrong here, because several cells
carry a status word inside an explanatory note and one row has an extra pipe. A naive
`grep -oE "\| (PASS|…) "` returns 281 against 276 rows.

| Metric | Summary block claimed | Tables actually held | Verdict |
|---|---|---|---|
| Total rows | 276 | 276 | agreed |
| PASS | 133 | **134** | **block was stale** |
| PARTIAL | 3 | **2** | **block was stale** |
| RETIRED | 131 | 131 | agreed |
| UNTESTED | 9 | 9 | agreed |
| DEFERRED | 0 | 0 | agreed |
| Families | 32 | 32 | agreed |
| Distinct kept test files | 50 | **57** | **block was stale** |

**The drift, named.** `REQ-CL-04` was upgraded PARTIAL → PASS when audit-7 F2 closed, and the summary
block was never updated to follow. That is one row moving between two buckets, which is exactly why
both numbers were off by one in opposite directions and the total still summed. The test-file count
had simply not been recomputed in some time.

### The surfaced count conflict, resolved by recount (plan D-3)

The plan carried two conflicting baselines and forbade picking one on trust.

- **BACKLOG:464-466** read "276 rows / 275 PASS / 32 families."
- **The matrix summary** read Total 276 / PASS 133 / PARTIAL 3 / RETIRED 131 / UNTESTED 9 / 32
  families.

**The recount falsifies BACKLOG outright**, and falsifies the matrix block partially. "275 PASS" was
true against no reading of the matrix at any point — the tables held 134 and the block claimed 133.
The plan's own reasoning ("BACKLOG's 275 PASS is stale — it predates the Item 7 retirement re-cite")
is close but not the whole story: 275 is not a stale PASS count, it is a wrong one. It looks like a
row-count minus one that was labelled PASS by mistake.

**Both blocks corrected**, neither adopted: `verification-matrix.md`'s summary (with a note naming
the drift) and `BACKLOG.md:464-466` (with the correction and the reason stated).

### Rows filed: the REQ-DIAG family

| REQ tag | Status filed | Cited test | Run before citing? |
|---|---|---|---|
| REQ-DIAG-01 | PARTIAL (gap named in the cell) | `test_upstream_pins.py` | **yes — 4 passed** |
| REQ-DIAG-02 | PASS | `test_extraction_diagnostic_screen.py` | **yes — 7 passed** |
| REQ-DIAG-03 | PASS | `test_extraction_diagnostic_screen.py` | **yes — 7 passed** |
| REQ-DIAG-04 | UNTESTED (reason named) | — (discharged by construction) | n/a |

Run: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/conformance/test_extraction_diagnostic_screen.py tests/conformance/test_upstream_pins.py -q` → **11 passed**. No aspirational
citations: REQ-DIAG-01 is PARTIAL rather than PASS because the kept codegen test pins the upstream
schema string, not the no-reader-side-table property, and REQ-DIAG-04 is UNTESTED rather than PASS
because nothing would fail if the envelope started carrying severity again.

### Post-filing counts

Total 280 · PASS 136 · PARTIAL 3 · RETIRED 131 · UNTESTED 10 · DEFERRED 0 · families 33 · distinct
kept test files 59. Per-status counts sum to the total (136+3+131+10+0 = 280) ✅. Family count matches
the distinct REQ-prefix count from the tables ✅.

### ⚠️ Surfaced premise conflict — Phase 5 cannot be executed as written

**The plan's Phase 5 assumption under test is false.** It assumes "the landed gates have REQ tags to
file rows against." Most of them do not:

| Closed item | Distinct REQ tags in its record |
|---|---|
| Item 2 — `constraint-catalog-totality` | 4 (`REQ-CL-04`, `REQ-DIAG-01`, `REQ-DIAG-03`, `REQ-EXT-09`) |
| Item 3 — `constraint-coverage-policy` | **0** |
| Item 5 — `catf-constraint-policy-acceptance` | **0** |
| Item 8 — `unit-lane-port-metadata` | **0** |
| Item 9 — `derivative-upgrade-held-intent` | **0** |
| `calcdef-constraint-gate-design` | **0** |
| `constraint-predicate-hardening` | 1 |
| Item 1 — `constraint-semantics-contract-amendments` | 2 |

Of Item 2's four, `REQ-CL-04` and `REQ-EXT-09` were **already filed**. The genuinely missing rows
were `REQ-DIAG-01` and `REQ-DIAG-03` — a family that existed in doc 30's prose and had zero rows in
the matrix. Those are filed above, together with `-02` and `-04` from the same doc-30 table, since
filing half a family would leave the same gap one row over.

**What cannot be done here.** Filing matrix rows for the Item 3, 5, 8 and 9 gates would require
**minting new REQ tags for them first**. That is a different act from "filing rows for landed gates,"
and D-3 forbids the alternative in as many words: "a gate without a REQ tag has nothing for the
Status column to be about." Minting a tag family is a requirements decision, not a matrix
reconciliation, and doing it silently inside this item would put agent-minted requirement ids into a
document whose whole value is that its rows trace to stated requirements.

**Parked, not resolved.** The Item 5 residual A-8 is therefore **partially** discharged: the recount
is done and the one tag-backed gap is filed, but the untagged gates of Items 3, 5, 8 and 9 remain
untraced. This needs an owner call — see the questions at the end of this run.

**Named vehicle, added at audit 2026-08-14 (audit finding A-2).** At implement time the parked half
was recorded in four narrative places and had **no execution vehicle** — no backlog entry, no
close-stage obligation. It now has one: `[CONSTRAINT-GATES-UNTAGGED]`, `.project/backlog/BACKLOG.md`,
P2 unowned, which states the two routes the owner can take and forbids leaving the gap implicit.
Filing the ticket mints no REQ tags and makes no requirements decision.

---

## Table 2 — Post-edit sweep

Re-run 2026-08-14 after every edit, same five terms, same scopes (plus the `claude/` tree the Phase 4
scope correction added).

| Repo | S1 | S2 | S3 | S4 | S5 | vs pre-edit |
|---|---|---|---|---|---|---|
| codegen | 0 | 13 | 7 | 20 | 5 | **identical** |
| agentic-mbse | 0 | 25 | 8 | 0 | 52 | S2 +4, S5 +1 |
| TEAx | 0 | 0 | 0 | 10 | 0 | S4 +1 |

**Codegen is unchanged, hit for hit.** Only line numbers moved. The edits introduced no new
superseded teaching and removed no hit, which is the expected result: the codegen sweep found zero
fix-here rows, so there was nothing for an edit to clear.

### Every new hit, dispositioned

| # | Term | File:line | Why it is new | Disposition |
|---|------|-----------|---------------|-------------|
| P1 | S2 | agentic-mbse `claude/agents/sysml-expert.md:124` | scope correction added the `claude/` tree | correct as written — Item 1's D5-a deviation |
| P2 | S2 | agentic-mbse `claude/agents/sysml-expert.md:132` | same | correct as written — **is** Item 1's correction |
| P3 | S2 | agentic-mbse `.claude/agents/sysml-expert.md:132` | **this item wrote it** — D5-a sentence added to the stale copy | correct as written — the corrected teaching |
| P4 | S2 | agentic-mbse `claude/skills/sysml-conventions/SKILL.md:147` | **this item wrote it** — "A bare `constraint`, a `require constraint`, an…" | correct as written — names the never-executing forms in order to rule them out |
| P5 | S5 | agentic-mbse `…/SKILL.md:147` | same line; S5 matches `assume constraint` in it | correct as written — same reason |
| P6 | S4 | TEAx `docs/evaluation-and-study.md:113` | **this item wrote it** — "`all_satisfied` is retired, not renamed-in-place" | correct as written — **quoted supersession**, the exact class Item 1's S4 collision rule pre-authorized (`design.md:1220-1222`) |

No post-edit hit is a defect. Four of the six are text this item authored, and every one names a
superseded token in order to retire it — which is why S4 had to run pre-edit.

---

## Mechanical checks

### The licensed elaboration check — **DISCHARGED**

```
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/ -q
```

**Result: `2070 passed, 34 skipped, 79 deselected, 1 warning in 156.97s`.**

**Proof the run was licensed:** `grep -c "no live syside license" /tmp/item7-licensed.log` → **0**.
Zero skip lines of that kind is the only proof the spec accepts, and it is met. The named-residual
fallback was not needed.

**All 34 skips accounted for**, none license-related — 25 `no computed attributes in the golden` and
9 `no calc output expressions in the golden`, both fixture-shape skips in
`test_computed_attribute_golden.py`.

**One honest limit on what this discharges.** The suite proves the *tree* elaborates under a licensed
toolchain. It does not elaborate the new SKILL.md snippet directly, because that snippet is
illustrative and is not a fixture. Adding it as one would be a fixture change, which this item's
Non-Goals forbid. What the check does establish is that nothing this item wrote broke elaboration,
and that the blessed pattern the skill now teaches is the same bindings shape the passing
constraint fixtures use.

### Collect sanity — **PASS**

`… -m pytest tests/ --collect-only -q | tail -3` → `2104/2183 tests collected (79 deselected)`.
No collection errors, so no archival or path breakage — the known failure mode at close.

### `git diff --check` — **CLEAN in all three repositories**

codegen ✅ · agentic-mbse worktree ✅ · TEAx ✅. No whitespace damage.

### Branch discipline — **VERIFIED**

| Repo | Path | Branch | State |
|---|---|---|---|
| codegen | `/home/reid/1cfe/sysml-codegen-item7-rebuild` | `item7-rebuild` | committed, **not pushed** |
| agentic-mbse | `/home/reid/1cfe/agentic-mbse-item7-rebuild` (worktree) | `item7-rebuild` | committed, **not pushed** |
| TEAx | `/home/reid/1cfe/teax` | `constraint-semantics-item3` | committed, **not pushed** |
| agentic-mbse | `/home/reid/1cfe/agentic-mbse` (main checkout) | `elaborate-first-salvage` | **clean, untouched** — one accidental edit reverted, see the Phase 4 record |

**`main` was not touched in any repository. Nothing was pushed anywhere.**

---

## Epic success criteria — evidence

| # | Criterion | Verdict |
|---|---|---|
| SC1 | The coverage-truth promise is owner-stated, filed in a named home, and cited from the product-lens trail (closes audit-F4) | **✅ MET.** `.project/product/P-001-…md`, verbatim diff empty; trail cited at the epic's Product-Lens header, one hop |
| SC2 | No shipped doc, skill, or agent prompt in the three repos teaches the superseded semantics; the sweep record lists every hit and disposition | **⚠️ MET WITH ONE NAMED RESIDUAL.** Sweep record complete (Tables 1 and 2, 136 raw hits, every one dispositioned). The residual: codegen's `.claude/` symlinks resolve to a checkout this item may not edit, so a codegen agent session still reads the superseded skill example until `item7-rebuild` reaches that branch |
| SC3 | `@inapplicable:`, the disposition vocabulary, the six states, and the TEAx opt-in are documented where their users will find them | **✅ MET** in the authoring repos — `modeling-assumptions.md` §8, `30-diagnostic-severity.md`, agentic-mbse `docs/patterns/constraints.md`, TEAx `docs/evaluation-and-study.md`. Subject to SC2's residual for the codegen-symlinked skill |
| SC4 | The authoring docs state when an in-model marker works and when PROVENANCE carries it, with B1–B5 cited | **✅ MET.** Stated as a table in both authoring repos, plus the skill; B1–B5 and the rule-3 detector cited, not rewritten |
| SC5 | Verification-matrix rows exist for the gates landed in Items 2–5, filed in one pass with the recount done | **⚠️ PARTIALLY MET.** Recount done and both count blocks corrected; the one tag-backed gap (REQ-DIAG) filed. **Not met** for Items 3/5/8/9, which carry zero REQ tags — filing rows for them requires minting tags, an owner call. Parked, not silently skipped |
| SC6 | Documentation checks and `git diff --check` pass in every touched repository | **✅ MET.** `git diff --check` clean in three repos; licensed suite 2070 passed with zero license-skip lines; collect clean |
