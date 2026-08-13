# Verification Record: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Created:** 2026-08-12 · **Branch:** `item7-rebuild`, both worktrees
**Design:** `design.md` (Appendix D defines this record's shape) · **Plan:** `plan.md`

This file is the item's evidence. It carries the recorded sweep (pre-edit and post-edit), the
per-hit disposition, the discharge record for everything the sweep does not reach, and the results
of every mechanical check.

---

## Sweep scope, and what is deliberately outside it

**In scope (DD5), both repositories:** `docs/`, `src/`, `tests/`, `scripts/`, `README.md`,
`CLAUDE.md`, `.project/concepts/`, `.project/backlog/`.

**Excluded (DD5), and why:** `.project/research/`, `.project/completed/`, `.project/active/`. These
are dated records of what was believed when. The lifecycle contract's own reading rule (`:19-21`)
already makes them provenance that cannot override an explicit correction in the contract.
Rewriting them would falsify the audit trail. The boundary is recorded here so it is auditable
rather than silent.

**Scope additions made by the implementer, recorded:**

- Companion repository: `claude/` was added to the scope. The design names
  `claude/agents/sysml-expert.md:124` as correction D5-a, and that path is under neither `docs/`
  nor any other DD5 directory. Adding a scope directory is permitted (Appendix D: "adding a term is
  allowed, dropping one is not"); the same reasoning covers a directory.
- Companion repository: `BACKLOG.md` sits at the repository root, not under `.project/backlog/`.
  It was swept at its actual location.

**Vendored corpora sub-exclusion, recorded with its reason.** The companion's `docs/sysmlv2/` and
`docs/syside/` trees are third-party reference material — the OMG SysML v2 specification documents,
the SysML v2 standard library, and generated SysIDE API documentation. They are not project-authored
guidance, this item has no authority to amend them, and editing them would corrupt a reference
corpus. Their hits are aggregated below by directory with counts and file lists rather than one row
per line, and the aggregation is flagged so an auditor can see exactly what was set aside. Every
project-authored hit gets its own row.

---

## Sweep terms

| # | Term | Command shape |
|---|------|---------------|
| S1 | retired test name | `grep -rn "test_constraint_migration_mapping" <scope>` |
| S2 | `require constraint` taught as a check | `grep -rn "require constraint" <scope>` |
| S3 | plain-constraint-enforces claims | `grep -rniE "constraint[s]? (are \|is )?(enforced\|checked\|verified\|evaluated\|a gate\|gates\|blocks)\|enforced (gate\|constraint)\|plain constraint.*(execut\|enforc\|gate\|check\|verif\|evaluat\|block)" <scope>` |
| S4 | the superseded headline precedence | `grep -rniE "all[_ ]satisfied\|else any assessed\|any assessed result" <scope>` |
| S5 | `assume`/`satisfy` taught as a check | `grep -rn "assume constraint\|satisfy requirement" <scope>` |

All five run with `--include=*.md --include=*.py --include=*.sysml`.

---

## Table 1 — Pre-edit sweep hits and dispositions

Run 2026-08-12, before any edit in either repository.

### Codegen

| # | Term | File:line | Quoted hit | Disposition | Note |
|---|------|-----------|------------|-------------|------|
| 1 | S1 | `docs/architecture/reference/01-extraction.md:20` | "`test_constraint_migration_mapping.py` proves this total across every constraint-bearing fixture;" | fix-here (C6c) | dead citation; only the first clause is replaced (DD7) |
| 2 | S1 | `src/sysml_codegen/extraction/constraint_report.py:6` | "no-silent-drop mapping test (`tests/conformance/test_constraint_migration_mapping.py`," | fix-here (C7a) | comment/docstring only |
| 3 | S1 | `docs/architecture/modeling-assumptions.md:484` | "conformance test (`test_constraint_migration_mapping.py`) reads directly, not a generation-time" | fix-here (C6a) | dead citation to a deleted file |
| 4 | S1 | `docs/architecture/reference/28-constraint-lowering-and-catalog.md:100` | "The migration mapping test (`test_constraint_migration_mapping.py`, D1/INV-A)" | fix-here (C6b) | dead citation |
| 5 | S1 | `tests/conformance/test_extractor.py:880` | "source of truth, `test_constraint_migration_mapping.py`); what survives here" | fix-here (C7b) | class docstring only |
| 6 | S1 | `tests/conformance/test_extractor.py:902` | "# confirmed empirically — see test_constraint_migration_mapping.py)." | fix-here (C7c) | inline comment only |
| 7 | S2 | `docs/architecture/modeling-assumptions.md:490` | "`constraint`/`require constraint`) against a defined `constraint def`, bind every formal to a real" | fix-here (C2) | this is D1 |
| 8 | S2 | `src/sysml_codegen/extraction/constraint_report.py:35` | "PLAIN = \"plain\"  # constraint / require constraint -> ConstraintUsage" | correct as written | a classification statement, not check guidance |
| 9 | S2 | `tests/fixtures/item4_require/model.sysml:5` | "the `require constraint` shape as a reported plain ConstraintUsage, and a" | correct as written | classification statement in a fixture |
| 10 | S2 | `tests/fixtures/item4_require/model.sysml:17` | "`require constraint` is a plain ConstraintUsage reached through a" | correct as written | classification statement |
| 11 | S2 | `tests/fixtures/item4_require/model.sysml:19` | "require constraint within_budget {" | correct as written | fixture model source; executable text (RI-6) |
| 12 | S2 | `tests/conformance/test_extractor.py:983` | "`require constraint` is a reported plain predicate; a requirement usage is" | correct as written | classification statement |
| 13 | S2 | `tests/conformance/test_extractor.py:987` | "live: ``within_budget`` (a ``require constraint``, a plain ConstraintUsage)" | correct as written | classification statement |
| 14 | S2 | `tests/conformance/test_extractor.py:995` | "assert len(require_entries) == 1, \"the require constraint must be swept\"" | correct as written | executable text; asserts sweeping, not execution (RI-6) |
| 15 | S2 | `tests/conformance/test_extractor.py:1008` | "# scanned 2, reported 1 (the require constraint), excluded 1 (the" | correct as written | classification statement |
| 16 | S2 | `.project/backlog/BACKLOG.md:170-171` | "…claims \"constraint, assert constraint, and require constraint\" support while using the same blind query (line 50) — check `require constraint` (`RequireConstraintUsage`?) too." | correct as written | **Explicit disposition, not a skip.** This sits inside a dated historical finding block about a past extraction bug; it names modules retired by the cutover recovery (`pipeline_builder.py`, `snapshot_context.py`). It records a question asked in 2026, not guidance teaching `require` as a check. Rewriting a dated finding would falsify the record, the same reason DD5 excludes `.project/research/`. |
| 17 | S3 | `docs/architecture/modeling-assumptions.md:489` | "**What a modeler needing an enforced gate should do.** Author an `assert constraint` (or bare" | fix-here (C2) | D1's own heading |
| 18 | S3 | `.project/backlog/epic_constraint_semantics_contract.md:62` | "enforced gates; requirement-side forms remain visible and non-executable." | correct as written | states the settled semantics; this is the epic that ordered the correction |
| 19 | S3 | `.project/backlog/epic_constraint_semantics_contract.md:234` | "a plain or requirement-side constraint is an enforced gate." | correct as written | quotes the defect it is scoping for correction |
| 20 | S3 | `.project/backlog/epic_constraint_semantics_contract.md:314` | "the visible warning/advisory; a plain constraint with a blocked predicate still generates" | correct as written | states the settled semantics |
| 21 | S4 | `tests/execution/test_fusion_tea_real_teax.py:245` | "\"headline\": \"all_satisfied\"," | hand-to-Item-3 | **executable text (RI-6).** The token spelling is Item 3's to change; this item may not touch it. |
| 22 | S4 | `tests/execution/test_constraint_verdicts_exact_route.py:171` | "assert from_files.outputs[REPORT_CH].headline == \"all_satisfied\"" | hand-to-Item-3 | executable text (RI-6) |
| 23 | S4 | `tests/execution/test_constraint_verdicts_exact_route.py:416` | "assert report.headline == \"all_satisfied\"" | hand-to-Item-3 | executable text (RI-6) |
| 24 | S4 | `tests/execution/test_constraint_verdicts_exact_route.py:540` | "assert satisfied.outputs[REPORT_CH].headline == \"all_satisfied\"" | hand-to-Item-3 | executable text (RI-6) |
| 25 | S4 | `.project/concepts/constraint-execution-and-design-space-studies.md:99` | "…otherwise one or more satisfied assertions gives `all_satisfied`; zero assertions gives `not_assessed`." | correct as written (as provenance) | `Status: Proposed`; its own banner (`:9`) defers to the `-claude.md` design, and the ratified lifecycle contract's reading rule (`:19-21`) demotes both to provenance. DD3 declines to write normative text into a provenance document; the same reasoning declines to rewrite one. The contract governs. |
| 26 | S4 | `.project/concepts/constraint-execution-and-design-space-studies.md:198` | "documented-only constraints never create a false `all_satisfied` result." | correct as written (as provenance) | same reason as row 25 |
| 27 | S4 | `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:232` | "33. Headline precedence is violation, then indeterminate, then all satisfied, then not assessed." | fix-here (A6) | the contract statement this item amends |
| 28 | S4 | `.project/concepts/constraint-execution-lifecycle-requirements.md:300` | "indeterminate → `indeterminate`; else any assessed result → `all_satisfied`; else" | fix-here (B4) | LC-E11, the direct contradiction |
| 29 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:52` | "A report can claim `all_satisfied` over partial assessment…" | correct as written | states the defect being corrected |
| 30 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:89` | "`all_satisfied` requires every applicable asserted gate to be assessed and pass; missing" | correct as written | states the settled semantics |
| 31 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:366` | "…`all_satisfied` means only that some" | correct as written | states the defect being corrected |
| 32 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:398` | "`all_satisfied` is impossible when any applicable asserted usage lacks assessment." | correct as written | states the settled semantics as an acceptance criterion |
| 33 | S5 | `src/sysml_codegen/extraction/constraint_report.py:37` | "SATISFY = \"satisfy\"  # satisfy requirement -> SatisfyRequirementUsage (excluded)" | correct as written | classification statement; already says excluded |
| 34 | S5 | `.project/concepts/constraint-execution-and-design-space-studies-claude.md:88` | "…requirement-owned require/assume constraints … and plain non-asserted constraint usages … are catalog entries, never executions" | correct as written | already states the never-executes rule; a provenance design document (row 25's reasoning) |

**S4 finding (not pre-run before this session).** 12 codegen hits. Four are executable test text
asserting today's `all_satisfied` token — handed to Item 3, which owns the spelling. Two are the
statements this item amends (A6, B4). Six are correct as written: four in the epic backlog file that
either state the settled semantics or quote the defect, and two in a `Status: Proposed` provenance
concept. **The design's expectation that S4 would hit "living prose around the report template and
its tests" is confirmed for the tests and not for a template** — no report-template prose restates
the precedence; the four hits are assertions on the runtime token. This is the sixth living
statement of the superseded precedence the design predicted, and it is executable, so RI-6 hands it
on rather than correcting it here.

**S5 finding (not pre-run before this session).** 2 codegen hits, both correct as written. No
codegen surface teaches `assume constraint` or `satisfy requirement` as an enforcement form.

### Companion repository (agentic-mbse)

Vendored corpora, aggregated (see the sub-exclusion above):

| Term | Directory | Hits | Files | Disposition |
|------|-----------|------|-------|-------------|
| S2 | `docs/sysmlv2/` | 15 | `SysML_IntroGuide_v2/full_document.md`, `SysML_SysTemp_MultiAgent/full_document.md` (×2), `stdlib/Domain Libraries/Analysis/TradeStudies.sysml`, `Cheatsheet/sysml_textual_notation_cheatsheet.md`, `SysML_Spec_v2_Part2/full_document.md`, `SysML_Spec_v2_Part1/full_document.md` (×9) | out of class — vendored upstream reference corpus, not project-authored guidance |
| S3 | `docs/sysmlv2/` | 4 | `SysML_FormalMethodsAerospace/full_document.md` (×2), `SysML_IntegratingReasoning/full_document.md`, `stdlib/Systems Library/Items.sysml` | out of class — same reason |
| S5 | `docs/sysmlv2/` | 27 | `stdlib/Systems Library/Views.sysml`, `SysML_Spec_v2_Part1/INDEX.md`, `SysML_Spec_v2_Part1/full_document.md` (×23), `SysML_Spec_v2_Part2/full_document.md` (×2) | out of class — same reason |
| S5 | `docs/syside/` | 6 | `python/v0.8.4/syside/FormatOptions.md` (×4), `v0.8.1/api/generated/syside.FormatOptions.md` (×2) | out of class — generated third-party API documentation |

Project-authored hits, one row each:

| # | Term | File:line | Quoted hit | Disposition | Note |
|---|------|-----------|------------|-------------|------|
| C1 | S2 | `docs/patterns/constraints.md:82` | "require constraint ValidInput {" | correct as written | a syntax example under "### Require Constraint"; the same document states at `:43` that `require` is not executed. See the D5-e-analogue ruling below. |
| C2 | S2 | `docs/patterns/constraints.md:87` | "require constraint NonZeroDenominator {" | correct as written | same reason as C1 |
| C3 | S2 | `docs/patterns/semantic-operators.md:520` | "- `require constraint` - Preconditions that must be satisfied" | fix-here (D5-c) | |
| C4 | S2 | `docs/patterns/semantic-operators.md:545` | "-> Use `assert constraint` or `require constraint` (with prefix!)" | fix-here (D5-d) | |
| C5 | S2 | `docs/patterns/syntax-reference.md:185` | "- `require constraint` - Precondition" | correct as written (DD8 no-edit branch) | ruling recorded below |
| C6 | S2 | `claude/agents/sysml-expert.md:124` | "require constraint { system.flowRate >= requiredFlow }" | fix-here (D5-a, deviated) | deviation recorded below |
| C7 | S2 | `tests/fixtures/constraint_fact_shapes/source_forms.sysml:15` | "require constraint below_limit {" | correct as written | fixture source exercising form classification; executable text (RI-6) |
| C8 | S3 | `docs/patterns/common-mistakes.md:246` | "### Don't: Plain constraint block" | fix-here (D5-f, design addition) | reason below |
| C9 | S3 | `docs/patterns/constraints.md:192` | "### Wrong: Plain constraint block (no prefix)" | fix-here (D4) | |
| C10 | S3 | `docs/patterns/semantic-operators.md:493` | "### Wrong: Plain constraint block" | fix-here (D5-b′, design addition) | reason below |
| C11 | S5 | `docs/patterns/semantic-operators.md:521` | "- `assume constraint` - Assumptions made by the model" | fix-here (D5-c companion line) | the same list D5-c corrects; leaving the `assume` line alone would make the list say `require` never executes and stay silent on `assume`, which C2/C3 put in the same never-executes set |
| C12 | S5 | `docs/patterns/constraints.md:96` | "assume constraint SteadyState {" | correct as written | syntax example, same reason as C1 |
| C13 | S5 | `docs/patterns/constraints.md:101` | "assume constraint IdealGas {" | correct as written | syntax example, same reason as C1 |
| C14 | S5 | `docs/patterns/syntax-reference.md:186` | "- `assume constraint` - Assumption" | correct as written (DD8 no-edit branch) | same ruling as C5; the entry names the form without claiming it is checked |
| C15 | S5 | `tests/fixtures/constraint_fact_shapes/source_forms.sysml:12` | "assume constraint positive_limit {" | correct as written | fixture source; executable text (RI-6) |
| C16 | S5 | `tests/fixtures/constraint_fact_shapes/source_forms.sysml:87` | "satisfy requirement satisfied_limit : LimitRequirement by sample;" | correct as written | fixture source; executable text (RI-6) |

**S1 finding, companion:** zero hits. **S4 finding, companion:** zero hits. The superseded
precedence is not stated anywhere in the companion repository, vendored corpora included.

---

## Companion re-verification (design bet B4)

Every design-quoted companion string was read at its stated location before any edit.

| Site | Design's quote | Read result |
|------|----------------|-------------|
| `docs/subtype-enumeration-decision-table.md` row 1 Rationale (`:24`) | "`assert` (`AssertConstraintUsage`) and `require`/plain are executable constraint usages (lowered under the profile); `RequirementUsage` + its `satisfy` subtype are requirement-side and excluded" | **confirmed verbatim** |
| `docs/patterns/constraints.md:190-199` | heading "### Wrong: Plain constraint block (no prefix)"; comment "// WRONG: Not recognized as ConstraintUsage!"; "**Error:** Parser does not create proper AST node without prefix." | **confirmed verbatim**, at `:192`, `:194`, `:199` |
| `claude/agents/sysml-expert.md:124` | "require constraint { system.flowRate >= requiredFlow }" | **confirmed verbatim at `:124`**; the *characterization* differs — see the deviation below |
| `docs/patterns/semantic-operators.md` three sites | "### Correct: Assert/require prefix" / "assert constraint TempLimit {  // Creates ConstraintUsage!" (`:503-512`); "- `require constraint` - Preconditions that must be satisfied" (`:520`); "-> Use `assert constraint` or `require constraint` (with prefix!)" (`:545`) | **confirmed verbatim** at `:503`, `:507`, `:520`, `:545` |
| `docs/patterns/syntax-reference.md:185` | "- `require constraint` - Precondition" | **confirmed verbatim** |

**B4 is resolved: the companion tree has not moved.** No quoted string mismatched, so no site is a
recorded stop.

### DD8 ruling, `docs/patterns/syntax-reference.md:185`

**Branch fired: no edit** (the design's default expectation).

The framing sentence that decided it, quoted: **`**Constraint Prefixes:**`** — a bare label over a
three-entry inventory (`assert constraint` / `require constraint` / `assume constraint`), inside a
document titled by syntax number ("## Syntax 7: Geometry Calculations" follows immediately), and
closed by "For detailed constraint patterns, see [constraints.md](constraints.md)." The list is a
syntax inventory. The entry "- `require constraint` - Precondition" describes the form as a
requirement-side precondition and does not claim it is checked, enforced, or gates anything. Under
the ruled semantics a `require` *is* a precondition conjunct in its owning requirement's
implication, so the entry is correct as written. `:186` (`assume constraint` - Assumption) is ruled
the same way by the same test.

### Deviation, D5-a (`claude/agents/sysml-expert.md:124`)

**The quote matched; the design's characterization of it did not.** The design describes the line as
"`require constraint { … }` presented as check guidance" and directs "Replace the form with
`assert constraint { … }`, keeping the predicate and surrounding prose."

On disk the line sits inside a section headed "### Example Pattern: Requirement with Constraint",
within a `requirement def FlowRequirement { … subject system : System; … }`. A `require constraint`
nested in a `requirement def` is the correct SysML v2 idiom for a requirement's required constraint —
it is what makes the constraint requirement-side at all. Substituting `assert constraint` there
would teach invalid requirement modeling and would contradict the very classification this item
publishes.

**Dispositioned against the design's stated intent** — which is that no modeler reads
`require constraint` as an enforced gate. The example keeps its SysML-correct form and gains a
sentence stating the settled semantics: the requirement-side form is cataloged and visible, never
executed, and `assert constraint` is the sole enforcement opt-in. Recorded here rather than
improvised silently.

### Design additions in the companion, with reasons

- **D5-b′ — `docs/patterns/semantic-operators.md:493-501`, the "### Wrong: Plain constraint block"
  block.** D5-b corrects the "Correct:" half of the same pair and states that the inline comment's
  claim "is the D4 defect again". The "Wrong:" half carries that identical false claim
  ("// Not recognized as ConstraintUsage!"). Correcting one half and leaving the other would leave
  the document self-contradicting inside a nine-line span.
- **D5-f — `docs/patterns/common-mistakes.md:246-259`, "Mistake 8: Forgetting Constraint Prefix".**
  A third instance of the D4 defect, in the document a modeler reads *for* mistakes: "// BAD: Not
  recognized as constraint" and "**Why:** Parser requires prefix to create proper ConstraintUsage
  node," under "### Do: Use assert/require prefix". Surfaced by S3, which is what the sweep is for.
  The design's register is a floor ("design may add, may not drop").
- **`docs/patterns/constraints.md:43`** — "`require` and `assume` constraints are unassessed today
  (only `assert` predicates are walked)." The word "today" reads the assert-only rule as a temporary
  implementation state. The settled semantics make it permanent. Corrected in the same file the
  equality instruction and D4 land in.

---

## Table 1b — Post-edit sweep hits and dispositions

Re-run 2026-08-12 after every edit in both repositories, same scope and same five terms.

### Codegen

**S1 → zero hits.** Every citation of the retired test is gone from the living surfaces.

| # | Term | File:line | Disposition |
|---|------|-----------|-------------|
| P1 | S2 | `docs/architecture/modeling-assumptions.md:472`, `:499` | correct as written — this item's own text, naming `require constraint` as a form that never executes |
| P2 | S2 | `constraint_report.py:35`, `item4_require/model.sysml:5,17,19`, `test_extractor.py:984,988,996,1009` | unchanged from pre-edit rows 8–15; classification statements and fixture/executable text |
| P3 | S2 | `.project/backlog/BACKLOG.md:170-171` | unchanged from pre-edit row 16; dated historical finding |
| P4 | S3 | `docs/architecture/modeling-assumptions.md:498` | correct as written — this item's own corrected heading, "**What a modeler needing an enforced gate should do.** Use the assert family." |
| P5 | S3 | `.project/backlog/epic_constraint_semantics_contract.md:62,234,314` | unchanged from pre-edit rows 18–20 |
| P6 | S3 | `.project/backlog/BACKLOG.md:724` | correct as written — this item's own C10 filing, which describes a plain constraint as never-executed and asks whether an advisory tier is worth building |
| P7 | S4 | `docs/architecture/modeling-assumptions.md:544`, `:546` | **quoted supersession, correct as written** — ADR-009's "What the contract said" block, which exists to preserve the superseded text |
| P8 | S4 | `.project/concepts/constraint-execution-lifecycle-requirements.md:326` | **quoted supersession, correct as written** — LC-E11's amendment note quoting what it replaced |
| P9 | S4 | `tests/execution/test_fusion_tea_real_teax.py:245`, `tests/execution/test_constraint_verdicts_exact_route.py:171,416,540` | unchanged; **handed to CONSTRAINT-SEMANTICS Item 3**, which owns the token spelling (RI-6) |
| P10 | S4 | `.project/concepts/constraint-execution-and-design-space-studies.md:99,198` | unchanged from pre-edit rows 25–26; provenance under the contract's reading rule |
| P11 | S4 | `.project/backlog/epic_constraint_semantics_contract.md:52,89,366,398` | unchanged from pre-edit rows 29–32 |
| P12 | S5 | `docs/architecture/modeling-assumptions.md:472`, `:499` | correct as written — this item's own text, which names `assume constraint` precisely to say it never executes |
| P13 | S5 | `constraint_report.py:37`, `constraint-execution-and-design-space-studies-claude.md:88` | unchanged from pre-edit rows 33–34 |

**The four `all_satisfied` test assertions are the item's one open residue**, and they are open by
design: RI-6 forbids touching executable text, and Item 3 owns the token. They are recorded here as
handed on, not as closed.

### Companion repository

**S1 → zero. S4 → zero.** Vendored corpora unchanged and still out of class.

| # | Term | File:line | Disposition |
|---|------|-----------|-------------|
| PC1 | S2 | `docs/patterns/constraints.md:111`, `:116` | correct as written — syntax examples; the same document now states the assert-only rule as settled at `:43` |
| PC2 | S2 | `docs/patterns/syntax-reference.md:185` | correct as written — DD8 no-edit branch, ruled above |
| PC3 | S2 | `docs/patterns/semantic-operators.md:520` | correct as written — this item's own D5-c replacement, which says `require` is not executed |
| PC4 | S2 | `claude/agents/sysml-expert.md:124`, `:132` | correct as written — the requirement-def example and this item's own D5-a sentence stating that it never executes |
| PC5 | S2/S5 | `tests/fixtures/constraint_fact_shapes/source_forms.sysml:12,15,87` | correct as written — fixture source exercising form classification (RI-6) |
| PC6 | S3 | `docs/patterns/common-mistakes.md:244,246`, `semantic-operators.md:493`, `constraints.md:221` | correct as written — this item's own corrected headings, each of which says the plain form is *not* a check |
| PC7 | S5 | `docs/patterns/constraints.md:125`, `:130` | correct as written — syntax examples, same reason as PC1 |
| PC8 | S5 | `docs/patterns/semantic-operators.md:522` | correct as written — this item's own text saying `assume` is not executed |
| PC9 | S5 | `docs/patterns/syntax-reference.md:186` | correct as written — DD8 no-edit branch |

---

## Pairwise precedence-agreement check (design Validation Approach step 2)

Five statements of the headline precedence exist because five documents each need to carry their own.
No checker enforces their agreement, so they are compared here against A0, in full rather than by
verdict.

| Copy | Location | Statement as written |
|------|----------|----------------------|
| **A0 (home)** | contract, "Headline states and coverage truth" | "violation → indeterminate → full satisfaction → partial coverage → not assessed" |
| A6 | contract invariant 33 | "violation, then indeterminate, then full satisfaction, then partial coverage, then not assessed" |
| A10 | contract Appendix C, mixed-population cell | "violation → indeterminate → full satisfaction → partial coverage → not assessed" |
| B4 | companion LC-E11 | "violation, then indeterminate, then full satisfaction, then partial coverage, then not assessed" |
| C1 | ADR-009 | "violation → indeterminate → full satisfaction → partial coverage → not assessed" |

**Verdict: all five agree in meaning and order.** Five terms, same sequence, no copy adding,
dropping, or reordering a state. The only variation is the connective (arrow versus "then"), which
carries no meaning. Each of A6, A10, B4 and C1 also points back at A0 or ADR-009 by name.

The definition of full satisfaction is restated in four of the five (A0, A6, B4, C1) and reads the
same each time: every applicable asserted gate was assessed and passed, a coverage claim rather than
the absence of a failure. A10's cell states the precedence only, which is what an acceptance cell is
for.

Three statements of the disposition kinds, compared the same way:

| Copy | Location | Statement as written |
|------|----------|----------------------|
| **A0/A4 (home)** | contract invariant 28 | "one of three kinds — eligible, excluded-with-reason, or non-reaching-with-reason — and every authored usage carries exactly one … 'reaches no instance' is a disposition, not an absence" |
| B1 | companion LC-E05 | "one of three kinds — eligible, excluded-with-reason, or non-reaching-with-reason — and the dispositions cover the complete authored-usage domain" |
| C5 | `reference/28-…md`, catalog text | does not enumerate the kinds; instantiates the third — "An owner kind with no expansion rule … yields no occurrence, and the usage is cataloged with one record, `eligible=False`" |

**Verdict: agreement holds.** A0/A4 and B1 name the same three kinds in the same order with the same
totality claim. C5 is not a restatement and was never going to be one — it describes what happens to
one kind at one pipeline step, and what it describes is that kind. **Recorded ambiguity:** the
design's Validation Approach names "the catalog text in C5", while its Component Overview assigns C5
to the equality instruction, which has no catalog text. The comparison above uses Appendix C's
section C5 (D6, doc 28), the only C5 with catalog text. The alternative reading has nothing to
compare, so this reading is the one that discharges the check.

---

## Table 2 — Discharge record

| Entry | Disposition | Verification note |
|-------|-------------|-------------------|
| contract invariant 8 | verified already-correct | Four outcomes unchanged; the new severity in A3 is a named contextual failure of the kind invariant 9 already admits, not a fifth outcome, and `ADMIT` is not reclassified. Byte-identity confirmed: `git diff \| grep "^-.*Outcomes are exactly"` is empty |
| contract Appendix C, "Zero constraint usages" | verified already-correct | Reads as state 6 (unconstrained, report absent). Byte-identity confirmed by the same diff grep |
| contract Appendix B, "Catalog is absent when no assertion is admitted" | verified already-correct | The catalog/report visibility claim is unaffected by the coverage change. Byte-identity confirmed by the same diff grep; A0 and A11 moved its line number from `:660` to `:725` and did not touch it |
| contract D-2 and D-4/SRC-01 | untouched, both directions (RI-5) | `git diff \| grep -E "^[-+].*D-2 \[OWNER-VERBATIM\]\|D-4 \[OWNER-VERBATIM\]"` is empty. A11 inserted between D-3 and D-4 and shifted D-4 down without editing it. The parked conflict stays parked |
| C4 / D2b ("three outcomes" → four) | design addition | §8 contradicted invariant 8, the guardrail this item pins. Leaving it would ship a modeler doc contradicting a guardrail in the same item that pins the guardrail |
| A10b (Appendix C "Asserted vacuous gate") | design addition | Invariant 61 introduces observable behavior and Appendix C is the mandatory acceptance matrix; a new invariant with no cell is a rule nothing has to demonstrate |
| B7 (LC-E13) | design addition | Companion mirror for invariant 61, by the LC-G07 symmetry argument. The frozen companion is what Items 2 and 3 read for requirements |
| D5-b′ (`semantic-operators.md:493-501`) | design addition | The "Wrong:" half of the pair D5-b corrects carries the identical false parser claim; correcting one half leaves the document self-contradicting inside nine lines |
| D5-f (`common-mistakes.md` Mistake 8) | design addition | A third instance of the D4 defect, in the document a modeler reads *for* mistakes. Surfaced by S3 |
| `constraints.md:43` ("unassessed **today**") | design addition | Read the assert-only rule as a temporary implementation state, in the same file the equality instruction and D4 land in |
| C2 (D1) RI-1 disposition | **verified true of current behavior at `882161e`** | The assert-family-only rule is what the profile does today: `executable_profile.py:949-950` routes `satisfy`, `requirement_constraint`, and `plain_usage` to UNASSESSED before predicate inspection, and `constraint_extraction.py:726-735`'s `_effective_predicate_source` returns `None` for `plain_usage`. Evidence: research register `20260812-101200_constraint-semantics-end-to-end.md` §2. No pending marker; no item named in the published text |
| C3 (D2) RI-1 disposition | **split — never-executed half current, cataloged half a target** | Never-executed under any non-assert form: verified true at `882161e`, same evidence. Catalog totality: target — the published text says so in a parenthetical and names CONSTRAINT-SEMANTICS Item 2 |
| C5 (D6) RI-1 disposition | **split, same shape as C3** | Status-follows-form: verified true at `882161e`. Catalogs unassessed under *any* owner kind: target — `elaborate.py:522-539` has no `CalculationDefinition` branch, so calc-def-owned usages produce no carrier. The published text names CONSTRAINT-SEMANTICS Item 2 |
| D5-e (`syntax-reference.md:185`) | **branch fired: no edit** (the design's default) | Framing sentence quoted above: `**Constraint Prefixes:**`, a syntax inventory. The entry does not claim the form is checked, enforced, or gates anything. `:186` ruled the same way |
| D5-a (`sysml-expert.md:124`) | **deviation, dispositioned against the design's stated intent** | The quote matched; the design's characterization did not. Substituting `assert constraint` inside a `requirement def` would teach invalid SysML. The form stays; a settled-semantics sentence is added. Full reasoning above |
| The four `all_satisfied` test assertions | **handed on — CONSTRAINT-SEMANTICS Item 3** | `test_fusion_tea_real_teax.py:245`, `test_constraint_verdicts_exact_route.py:171,416,540`. Executable text (RI-6), and the headline token spelling is Item 3's by RI-3 |
| REQ-EXT-09 / REQ-CL-04 re-grade | **not done, by design** | A stated non-goal. C8 appends a pointer to REQ-EXT-09's Test File cell (DD6) and leaves the requirement text and the `PASS` status alone. Choosing the replacement proof is Item 2's |
| B1 convention statement | recorded | The companion's first in-place rewrite. Licensed by the copy-and-freeze header's "forward requirement amendments happen here only" (`:3-7`), not by LC-E04B, which is a pure append. Every rewrite quotes what it supersedes, so an owner who prefers append-only can recover mechanically |
| DD5 scope exclusion | recorded | `.project/research/`, `.project/completed/`, `.project/active/` excluded as dated provenance; reason stated at the head of this file, with the vendored-corpora sub-exclusion |
| Companion doc-check finding | recorded | See below |
| New consistency tooling | **not built, by design** | A cross-document checker for constraint semantics is a stated non-goal. The pairwise agreement check above is the price paid instead, and it is a gate, not a read-through |

---

## Mechanical checks

**Codegen**

- `python3 scripts/check_doc_distinctness.py` → `31 numbered reference documents checked, 0
  identical-content groups`. **Note:** bare `python` is not on PATH in this environment; the plan's
  stencil needs `python3`.
- `git diff --check` → clean at every phase and at close.
- `git diff -- '*.py'` → two files, comment and docstring lines only. No assertion, name, or value
  changed. Read in full at Phase 4.
- No `pytest` run was required and none was run in this repository. This is a documentation item and
  it changes no executable text (RI-6). Adding a test run to feel complete would prove nothing.

**Companion (agentic-mbse)**

- `git diff --check` → clean.
- `git status --short` → five files, all this item's, no `uv.lock`.
- Relative-link resolution: no link target was added or changed in any edited file. The two new
  cross-repository references (the equality instruction's authority-copy pointer and the ADR-009
  cite) are deliberately plain prose paths rather than Markdown links, because a companion reader
  may not have the codegen tree — a relative link to `../../sysml-codegen/...` would resolve for
  nobody.
- **The docs-referencing-test finding.** The companion has no doc-check script. Grepping `tests/`
  for the edited documentation paths returned **two hits**, both naming `semantic-operators.md` in
  prose about the literal binding form, not about constraints:
  `tests/fixtures/item9/attr_redef_literal/model.sysml:22` and
  `tests/test_validation/test_item9_checks.py:17`. The referencing test was run —
  `uv run --extra dev pytest tests/test_validation/test_item9_checks.py` → **2 passed**. It needs
  `SYSIDE_LICENSE_KEY` from `/home/reid/1cfe/agentic-mbse/.env`; without it the same command reports
  2 failed on an ImportError, which is not a real result. So the finding is *not* "no
  docs-referencing tests" as the design anticipated: two exist, they reference a file this item
  edited, they do not depend on the edited passage, and they pass.

**Guardrail and boundary checks**

- RI-4 (three guardrail statements byte-identical): confirmed, anchored on quoted text. Diff grep
  empty.
- RI-5 (D-2 and D-4 untouched in both directions): confirmed. Diff grep empty.
- RI-3 (no normative token spelling or report field name): confirmed by reading the diff. The only
  headline tokens in the diff are inside ADR-009's "What the contract said" block and LC-E11's
  amendment note, both quotations of pre-amendment text. `ADMIT`, `BLOCK`, `NON_NUMERICAL` and
  `UNASSESSED` appear as invariant 8's profile outcomes, which are not headline tokens and are
  unchanged.
- RI-6 (no executable text): confirmed. The Python diff is comment and docstring lines only, and the
  one class of correction that could not avoid executable text — the four `all_satisfied`
  assertions — was handed on rather than made.
- RI-7 (visible discharge): Table 2 above. Silence discharges nothing, so every entry has a row.
