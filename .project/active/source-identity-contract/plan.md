# Implementation Plan: Authoritative Source-Identity Contract

**Status:** Complete — implementation and audit certified; owner ratification recorded 2026-08-07
**Created:** 2026-08-05
**Last Updated:** 2026-08-07
**Branch:** `source-identity-epic`

## Source Documents

- **Spec:** `.project/active/source-identity-contract/spec.md`
- **Design:** `.project/active/source-identity-contract/design.md` — component details,
  authority boundaries, matrix derivation, and risks live here
- **Epic:** `.project/backlog/epic_semantic_source_identity.md`, Item 3

## The Point

`sysml-codegen` must trace each modeled value consumed by calculations, constraints, and
aggregations to its actual runtime source. A study must vary that source once and reach every and
only its consumers. Today the pipeline can reinterpret a legal but inert self-binding, discard its
actual referent, and mint several consumer-local inputs that merely share a default value. This item
creates the one authoritative contract that fixes the language meaning, source-occurrence identity,
diagnostic boundary, and public mutation outcome before any implementation item changes code.

## Implementation Strategy

**Phasing rationale:** Draft the highest-risk acceptance authority first, then make normative prose
answer those concrete cells. Project the stable contract into the durable requirement and
verification layers only afterward. Finish with an end-to-end authority-chain audit and owner
ratification. This follows the sequencing in
[design.md § Implementation Notes](design.md#implementation-notes).

**Critical path:** Complete 28-cell/34-coordinate authority → governing invariants and corrections
→ durable requirement projection → verification and epic projections → whole-chain audit and owner
ratification.

**First proof point:** Appendix C contains exactly 28 complete acceptance cells and 34 evidence
coordinates derived from Appendix A, with no `PENDING_CHECKPOINT` state and no semantic choice left
to Items 4 or 5.

**Validation approach:**

- Start each phase with a small phase-local assertion that fails before the required document edit.
- Use document assertions rather than new product tests because Item 3 changes no production code,
  fixtures, snapshots, or runtime behavior.
- Preserve a before-edit digest for the archived companion and before-edit projections of the
  verification matrix's Status and Summary/Index data.
- Finish with the existing license-free source-identity route tests, structural document checks,
  diff checks, and an owner ratification checkpoint.

## Implementation Traceability

This table assigns each spec requirement to a concrete edit without repeating its behavioral
wording. The contract locations follow the ownership and projection rules in
[design.md § Core Concept](design.md#core-concept) and
[design.md § Component Overview](design.md#component-overview).

| Spec item | Authoritative contract edit | Companion projection / downstream edit | Phase and check |
|---|---|---|---|
| SI-01 | Source-identity invariant, D-4+ disposition, SRC-01; preserve the owner quote exactly | `LC-SI-01` | P1/P2; payload and grade check |
| SI-02 | Referent definition, A.2 table, referent-fidelity invariant | `LC-SI-02` | P1/P2; referent-key check |
| SI-03 | A.2 table and supported-form cells C1–C6/C25 | `LC-SI-03` | P1/P2; context/form coverage check |
| SI-04 | Redefinition definition/invariant and cells C7/C8/C19/C21 | `LC-SI-04` | P1/P2; occurrence-state coverage |
| SI-05 | Occurrence-identity invariant and cells C7–C10 | `LC-SI-05` | P1/P2; distinct/ambiguous outcomes |
| SI-06 | Indexed-value disposition and SRC-02 | `LC-SI-06` | P1/P2; no index-flattening reading |
| SI-07 | Bracket-form disposition and SRC-03 | `LC-SI-07` | P1/P2; load-boundary outcome |
| SI-07a | Deferred-expression disposition and C22 | `LC-SI-07A` | P1/P2; final deferral state |
| SI-08 | Semantic-source definition/invariant and runtime-source cells | `LC-SI-08` | P1/P2; declaration + occurrence key |
| SI-09 | One-occurrence/one-source invariant and runtime-source cells | `LC-SI-09` | P1/P2; cross-form convergence check |
| SI-10 | Shared aggregation identity invariant and C11–C15/C17/C18/C26 | `LC-SI-10` | P1/P2; consumer-family coverage |
| SI-11 | Authored-literal invariant and C16 | `LC-SI-11` | P1/P2; independent-literal outcome |
| SI-11a | Unbound-default disposition and C23 | `LC-SI-11A` | P1/P2; per-usage outcome |
| SI-12 | Terminal-policy amendment and C18 | `LC-SI-12` | P1/P2; exact strict/lenient outcomes |
| SI-13 | Route-parity invariant and R5 execution-route projection | `LC-SI-13` | P1/P2; route applicability check |
| SI-14 | Public-mutation invariant and R5 mutation projection | `LC-SI-14` | P1/P2; every runtime cell owes mutation |
| SI-15 | Self-binding validation obligation and SRC-01; preserve owner request at its home | `LC-SI-15` | P1/P2; payload and diagnostic boundary |
| SI-16 | Indexed-expression readiness obligation and SRC-02; preserve owner request at its home | `LC-SI-16` | P1/P2; valid-but-unsupported wording |
| SI-17 | Independent codegen fail-closed invariant and diagnostic cells | `LC-SI-17` | P1/P2; no validator dependency |
| SI-18 | Modeling-guidance obligation; preserve the owner quote including `quesiton` | `LC-SI-18` | P2; exact payload placement |
| SI-19 | Guidance-content/example-force obligation | `LC-SI-19` | P2; example/referent force check |
| SI-20 | Amend invariants 19/20/22/26, Appendix B, status, and durable companion | `LC-SI-20`; companion status touch-ups | P2/P3; authority consistency |
| SI-21 | Appendix B corrections and Appendix C ownership | `LC-SI-21`; eleven verification annotations | P2/P4; clause-vocabulary check |
| SI-22 | Simplification invariant and superseded-mechanism corrections | `LC-SI-22` | P2; one-authority derivability check |
| SI-23 | Appendix C schema, R1–R6 derivation, 29 cells, 35 coordinates | `LC-SI-23` citation only | P1/P3; enumeration and projection checks |

---

## Phase 1: Establish the Acceptance Authority

### Goal

Draft the source-identity disposition table, binding-owner referent table, and Appendix C scenario
subsection. This is first because every later normative and downstream statement must be checkable
against a complete target cell. See
[design.md § Architecture](design.md#architecture),
[design.md § Key Decisions](design.md#key-decisions), and
[design.md Appendix A](design.md#appendix-a--scenario-derivation-and-cell-enumeration-binding-excluded-from-main-body-budget).

### Assumption Under Test

The closed evidence inventory can produce exactly 29 complete acceptance cells and 35 evidence
coordinates without a new probe, an unclassified source, or a downstream semantic decision.

### Test Stencil (Write This First)

```python
contract = Path(CONTRACT).read_text()
section = contract.split("Source-identity scenarios", 1)[-1]
cell_ids = parse_cell_ids(section)          # SRC-01..03 and C1..C26
coordinate_ids = parse_coordinate_ids(section)
assert len(cell_ids) == 29
assert len(coordinate_ids) == 35
assert "PENDING_CHECKPOINT" not in section
assert all_fields_present(coordinate_ids, required_si23_fields)
```

Run the assertion before editing to establish the red state. Keep the final checker command and
result in the Phase 1 completion notes.

### Changes Required

**See the design for:** the three-field scenario schema and R1–R6
([design.md § Architecture](design.md#architecture)); exact enumeration and evidence roles
([design.md Appendix A.3–A.6](design.md#a3-row-enumeration)); required citation fidelity
([design.md § Required Invariants](design.md#required-invariants)).

**Specific file changes:**

#### 1. Lifecycle contract

**File:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`

- [x] Extend the decision section near current lines 279–306 with the provenance-graded D-4+
  source-identity dispositions and the resolved checkpoint record.
- [x] Add the binding-owner-context referent table and supporting definitions at the contract home
  selected by the design.
- [x] Add the Appendix C source-identity subsection after the current acceptance matrix near line
  462, using all 29 cells and 35 evidence coordinates from Appendix A.
- [x] Give every `BLOCKED` cell its full target coordinate and evidence owner; do not create or edit
  any fixture.

### Validation

**Automated:**

- [x] Run the phase-local parser → 29 cells, 35 coordinates, and all required SI-23 fields.
- [x] Assert each Appendix A.4 source has exactly one evidence role and each counted row has one
  valid disposition, boundary outcome, and certification state.
- [x] Assert R5 applies route and mutation obligations from boundary outcome; every
  `RUNTIME_SOURCE` cell owes route parity and off-default mutation.
- [x] Run `git diff --check -- .project/concepts/constraint-execution-authoritative-lifecycle-contract.md`.

**Manual:**

- [x] Diff-read SRC-01b against supported targets C25/C2; confirm the bare-renamed recommendation
  remains agent-grade and the mixed-context correction does not claim owner-origin provenance.
- [x] Sample AFT, DCS, RM9, RM12, and RM13 citations against their authored form, binding-owner
  context, semantic referent, topology, and consumer mix.

**What We Know Works After This Phase:** The authoritative artifact publishes the complete target
population and downstream work can cite a cell instead of choosing semantics.

---

## Phase 2: Amend the Governing Contract

### Goal

Make the contract's definitions, invariants, correction register, and status agree with the Phase 1
acceptance authority. Run the Item 4/5 derivability dry-run before finalizing the wording. See
[design.md § Required Invariants](design.md#required-invariants),
[design.md § Implementation Notes](design.md#implementation-notes), and
[design.md § Integration Strategy](design.md#integration-strategy).

### Assumption Under Test

One set of governing statements can answer every Item 4 and Item 5 scope bullet while preserving
the source grade and exact force of every owner payload.

### Test Stencil (Write This First)

```python
contract = Path(CONTRACT).read_text()
assert amended_once(contract, [19, 20, 22, 26])
assert has_source_identity_invariants_from_54(contract)
assert owner_payload_count(contract, "Never reinterpret") == 1
assert owner_payload_count(contract, "Can we add that") == 1
assert "quesiton" in guidance_owner_quote(contract)
assert every_item4_item5_scope_has_governing_citation(contract)
```

### Changes Required

**See the design for:** amendment ownership and projection
([design.md § Core Concept](design.md#core-concept)); exact invariant constraints and payload homes
([design.md § Required Invariants](design.md#required-invariants)); superseded mechanism boundaries
([design.md § Key Decisions](design.md#key-decisions)).

**Specific file changes:**

#### 1. Lifecycle contract

**File:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`

- [x] Amend invariants 19, 20, 22, and 26 at current lines 172–195, then append the numbered
  `Source identity` invariant family from 54 without renumbering 1–53.
- [x] Add exactly one Appendix B correction row for each superseded reading named by the design;
  preserve correction-record phrasing rather than future-agent prohibitions.
- [x] Reconcile the status section at current lines 3 and 27–40 against the composed 41/41 release
  record and merged-state changelog, without claiming source-identity certification.
- [x] Record the validation and guidance obligations, including the exact SI-01, SI-15/SI-16, and
  SI-18 owner payloads at their designated homes.

#### 2. Phase completion evidence

**File:** `.project/active/source-identity-contract/plan.md`

- [x] Record the derivability dry-run: every Item 4 and Item 5 scope bullet → governing invariant,
  disposition, correction row, or Appendix C cell.

### Validation

**Automated:**

- [x] Run the phase-local assertion → all amended/new invariants and payload checks pass.
- [x] Check the traceability table → every SI item maps to at least one contract edit and every
  contract edit maps back to an SI item or checkpoint outcome.
- [x] Search the contract amendments for duplicate normative sentences outside their sole home.
- [x] Assert every superseded mechanism has exactly one Appendix B row.

**Manual:**

- [x] Re-derive every provenance grade from the spec and resolved owner checkpoint; record zero
  upgrades.
- [x] Read the Item 4/5 dry-run from top to bottom and stop if any bullet still requires a semantic
  choice.

**What We Know Works After This Phase:** The lifecycle contract alone answers the semantic,
diagnostic, route, mutation, and simplification questions that downstream design must inherit.

---

## Phase 3: Create the Durable Requirements Companion

### Goal

Create the forward-editable requirements companion from the archived close state, project the
contract through graded `LC-SI-*` rows, and fix the contract pointer in the same phase. See
[design.md § Key Decisions, D6](design.md#key-decisions) and
[design.md § Component Overview](design.md#component-overview).

### Assumption Under Test

The requirement-ID layer can remain checkable and provenance-graded while citing the contract's
single behavioral wording rather than copying it.

### Test Stencil (Write This First)

```python
archive = Path(ARCHIVED_COMPANION)
durable = Path(DURABLE_COMPANION)
assert sha256(archive) == archive_sha_before
assert durable.exists()
assert archived_source_path in durable.read_text().splitlines()[:12]
assert projected_si_ids(durable) == expected_si_ids
assert projection_rows_cite_contract_without_restating_rules(durable)
assert durable_scenario_section_is_citation_only(durable)
```

Capture `archive_sha_before` before the copy and retain it in the Phase 3 completion notes.

### Changes Required

**See the design for:** copy-and-freeze semantics and coupled pointer update
([design.md § Key Decisions, D6](design.md#key-decisions)); the `LC-SI-*` projection rule
([design.md § Core Concept](design.md#core-concept)); allowed status touch-ups
([design.md § Research Findings](design.md#research-findings)).

**Specific file changes:**

#### 1. Durable companion

**File:** `.project/concepts/constraint-execution-lifecycle-requirements.md` (NEW)

- [x] Copy `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md` exactly,
  then add the provenance header naming its archived path and close state.
- [x] Add one graded `LC-SI-*` projection for every SI traceability entry, keeping SI-07A and
  SI-11A distinct; each row cites its governing contract invariant/cell instead of restating it.
- [x] Apply only the designed LC-D06, LC-D07, LC-D09, LC-E04B, status, and scenario-citation
  touch-ups.

#### 2. Lifecycle contract pointer

**File:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:8`

- [x] Point `Requirements:` to the durable companion in the same change that creates the copy.

#### 3. Archived companion

**File:** `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md`

- [x] Make no changes; verify its digest against `archive_sha_before` after every edit operation.

### Validation

**Automated:**

- [x] Run the phase-local assertions → digest unchanged, provenance header present, complete
  projected ID set, and citation-only scenario projection.
- [x] Compare the archive with its Git object and recorded digest → byte-identical.
- [x] Assert the contract has exactly one requirements pointer and it resolves to the durable copy.
- [x] Run `git diff --check` on the durable companion and contract.

**Manual:**

- [x] Diff the new durable file against the archive and classify every changed hunk as provenance
  header, approved status correction, LC-SI projection, minimal LC touch-up, or scenario citation.
- [x] Sample every provenance grade family, including `[NEED]`, `[INFERRED]`, and `[INHERITED]`,
  against the spec absorb mapping.

**What We Know Works After This Phase:** Historical citations still resolve to an untouched archive,
while all forward requirement edits have one durable, correctly graded home.

---

## Phase 4: Correct Downstream Tracking Surfaces

### Goal

Annotate the eleven affected verification rows without changing test state, then update the epic's
Item 3 deliverables to the checkpoint-approved homes. See
[design.md § Key Decisions, D4–D6](design.md#key-decisions) and
[design.md § Component Overview](design.md#component-overview).

### Assumption Under Test

Contract disposition can be added locally without changing any verification Status value,
Summary/Index count, historical test reference, or archived evidence claim.

### Test Stencil (Write This First)

```python
before = capture_matrix_status_summary_and_index(MATRIX)
apply_document_edits()
after = capture_matrix_status_summary_and_index(MATRIX)
assert after == before
assert annotated_ids(MATRIX) == AFFECTED_ELEVEN_ROWS
assert each_row_has_one_disposition(MATRIX)
assert every_partial_clause_is_labeled(MATRIX, {"stands", "SUPERSEDED"})
assert legend_defines_contract_disposition_without_redefining_status(MATRIX)
```

Save the before-edit projection outside the repository or in the Phase 4 completion notes before
touching the matrix.

### Changes Required

**See the design for:** exact row and clause dispositions
([design.md § Key Decisions, D4](design.md#key-decisions)); immutable matrix properties
([design.md § Required Invariants](design.md#required-invariants)); checkpoint-approved artifact
homes ([design.md § Integration Strategy](design.md#integration-strategy)).

**Specific file changes:**

#### 1. Verification matrix

**File:** `docs/architecture/verification-matrix.md`

- [x] Add one legend line near current lines 5–23 defining row-local contract disposition.
- [x] Annotate REQ-CL-05 (current line 172), REQ-IR-06/07 (335–336), REQ-SVM-01/02/04
  (566–569), REQ-VBR-10 (586), REQ-BT-13, REQ-IR-01, REQ-PGD-06, and REQ-VBR-03 with the exact
  row and clause vocabulary from D4.
- [x] Leave Status cells, Summary/Index counts, table structure, and test references unchanged.

#### 2. Epic Item 3

**File:** `.project/backlog/epic_semantic_source_identity.md:481`

- [x] Reconcile Item 3's status and deliverable list with the contract-owned decisions/matrix,
  durable companion, absence of standalone decision/matrix files, and frozen archive.

#### 3. Source spec workflow footer

**File:** `.project/active/source-identity-contract/spec.md:240`

- [x] Replace the stale next-step footer that still points to spec review/design with the current
  implementation/audit sequence; change no requirement or provenance content.

### Validation

**Automated:**

- [x] Run the before/after matrix comparison → byte-identical Status projection and Summary/Index
  counts.
- [x] Assert exactly eleven affected IDs have one row annotation each; every `PARTIAL` row labels
  every clause.
- [x] Assert REQ-VBR-10 is `PARTIAL`, with specialized-chain `stands` and self-binding rescue
  `SUPERSEDED`.
- [x] Run `git diff --check` on all Phase 4 files.

**Manual:**

- [x] Confirm every annotation points to its owning Appendix B row or Appendix C cell.
- [x] Confirm the epic and spec footer describe workflow state only and do not duplicate normative
  semantics.

**What We Know Works After This Phase:** Test-state reporting remains historically honest while the
matrix and epic point readers to the new contract authority.

---

## Phase 5: Audit the Authority Chain and Obtain Ratification

### Goal

Run the complete structural and evidence-fidelity audit, present the assembled disposition table
and Appendix C subsection to the owner, and record the result without upgrading agent-originated
decisions. See [design.md § Validation Approach](design.md#validation-approach) and
[design.md § Next-Stage Handoff](design.md#next-stage-handoff).

### Assumption Under Test

A fresh Item 4 or Item 5 author can derive its work solely from the contract chain, and the owner
can ratify the assembled table without correcting omitted or regraded decisions.

### Test Stencil (Write This First)

```python
assert traceability_is_bidirectional(SPEC, touched_artifacts)
assert derive_counts(CONTRACT) == {"cells": 28, "coordinates": 34}
assert archive_digest_unchanged()
assert matrix_status_projection_unchanged()
assert all_touched_links_resolve()
assert no_provenance_grade_upgrades()
assert item4_item5_derivability_dry_run_is_complete()
```

### Changes Required

**See the design for:** validation gates
([design.md § Validation Approach](design.md#validation-approach)); final checkpoint ordering
([design.md § Key Decisions, D7](design.md#key-decisions)); known risks and failure branches
([design.md § Potential Risks](design.md#potential-risks)).

**Specific file changes:**

#### 1. Lifecycle contract

**File:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`

- [ ] After presenting the complete table to the owner, record the ratification response at the
  designated checkpoint home; retain `[AGENT] (ratified by owner, date)` on agent-originated rows.
- [x] Correct only issues found by the audit; any genuinely new scenario shape reopens the contract
  explicitly under D8 and updates derivation, enumeration, and counts together.

#### 2. Plan completion evidence

**File:** `.project/active/source-identity-contract/plan.md`

- [x] Record each phase's commands, results, deviations, archive digest, matrix baseline result,
  derivability map, and ratification status in Implementation Notes.

### Validation

**Automated:**

- [x] Run the complete phase-local audit stencil with no failures.
- [x] Run `uv run pytest tests/conformance/test_source_identity_routes.py -q` → the 11 retained,
  license-free HEAD-evidence tests still pass.
- [x] Run `git diff --check` across every touched file.
- [x] Run `git status --short` and verify no production code, fixture, snapshot, generated package,
  or `completed/` file changed; verify every tracked Item-1/Item-2 evidence artifact is
  byte-identical to `HEAD`.
- [ ] Establish a pre-Item-3 byte baseline for the untracked Item-2 route test. Git has no object
  for that file, so this historical claim cannot be certified from the current worktree.

**Manual:**

- [x] Re-derive all 29 cells and 35 coordinates from Appendix A.4 rather than trusting the printed
  totals.
- [x] Audit every evidence citation for authored form, binding-owner context/referent, topology,
  and consumer mix.
- [x] Diff-read the contract, companion, verification annotations, epic, and spec footer as one
  authority chain.
- [x] Obtain and record owner ratification of the assembled disposition table and Appendix C
  subsection before declaring Item 3 complete.

**What We Know Works After This Phase:** Item 3 has one ratified, provenance-honest authority chain;
Items 4 and 5 can begin without inventing language semantics, identity policy, terminal behavior,
or proof coordinates.

---

## Environment Setup

Use the repository environment and commands in `CLAUDE.md`.

- No SysIDE license is required for these document edits or the retained route test.
- Use `uv run pytest tests/conformance/test_source_identity_routes.py -q` for the evidence smoke.
- Use `git diff --check` for Markdown whitespace and patch hygiene.
- Preserve all pre-existing worktree changes; this item starts from an intentionally dirty branch.

## Risk Management

See [design.md § Potential Risks](design.md#potential-risks) for the governing failure branches.

- **Phase 1:** Count cells and coordinates from parsed IDs and fields, not headings or prose totals.
- **Phase 2:** Use bidirectional SI traceability, exact payload checks, and the Item 4/5 dry-run to
  catch authority gaps before projection.
- **Phase 3:** Hash the archive first and treat any digest change as an immediate stop condition.
- **Phase 4:** Compare a captured Status/Summary/Index projection before accepting the matrix diff.
- **Phase 5:** Do not convert ratification into owner-origin provenance; reopen the contract if a
  genuinely new shape changes the closed population.

## Implementation Notes

### Phase 1 Completion

**Completed:** 2026-08-05

**Actual Changes:**

- Contract: added "Source identity — definitions and referent table" after invariant 53
  (definitions for referent/context/declaration/occurrence/semantic-source-occurrence/runtime
  source/redefinition; the form × context referent table; AFT/RM/DCS/NOP/HIF abbreviations).
- Contract: added "Source-identity dispositions (D-4 onward)" after D-3 — the resolved 2026-08-05
  checkpoint record (owner verbatim, eight ratified `[AGENT]` items) and D-4..D-19 (6 forms, 6
  source classes, 4 impermissible mechanisms), each with ruling, provenance grade, evidence, and
  migration consequence. The SI-01 owner quote lives at D-4 (sole home).
- Contract: added Appendix C "Source-identity scenarios" subsection — schema, key/counting rules,
  the R5 route/mutation derivation table, coordinate-field locality, and the original 26 cells / 32
  coordinates before the audit reopening (families SRC-01/02/03/C22 with subrows 01a–01g, 02a,
  03a, 22a; individual cells C1–C21, C23). The correction pass extends this to 29/35 with
  C24/C25 and the C17/C26 topology split. Every `BLOCKED` cell publishes its full target key and owning item; no fixture created
  or edited.

**Validation Results:**

- `python3 <scratchpad>/phase1_check.py` → GREEN at the original Phase-1 close: 26 cells / 32 coordinates, no
  `PENDING_CHECKPOINT`, required SI-23 fields present per row, one valid
  disposition/outcome/certification per counted row, every `RUNTIME_SOURCE` cell carries a
  mutation field (route parity derives via the R5 table), D-4..D-19 present, checkpoint verbatim
  present, design A.4 rows each carry exactly one role arrow.
- `git diff --check` on the contract → clean.
- Manual: 01b (under D-4 `[OWNER-VERBATIM]`) and C4 (under D-5 `[AGENT]` ratified) keep distinct
  grades and mutual paired-acceptance markers. Citation sample verified against fixtures:
  DCS `design.sysml:63,71,83,92` + `extraction_snapshot.json:404,448,478` (occurrence-level QNs),
  `hif_plant.sysml:215` (self-binding), `hif_driver.sysml:6,76,118` (RM 9 def-context), solar
  `library.sysml:697,721` (modeled `permitting` targets), NOP `model.sysml:22,25,37`.

**Issues:** None.

**Deviations:** None. One formatting note: the checkpoint owner quote is kept on its own line so
the verbatim payload never wraps mid-quote.

### Phase 2 Completion

**Completed:** 2026-08-05

**Actual Changes:**

- Contract: amended invariants 19 (aggregation terms join the shared procedure; keying by semantic
  source identity, never name coincidence), 20 (genuine-terminal-miss policy for every consumer
  type; no same-named candidate, no consumer-local mint for a bound reference), 22 (authored-literal
  independence; per-usage `LIBRARY_DEFAULT`), and 26 (producer completeness under semantic source
  identity; owner/name reconstruction unsupported). Each carries one
  `(amended 2026-08-05, SOURCE-IDENTITY Item 3)` marker; 1–53 unrenumbered.
- Contract: subsection renamed to "Source identity"; appended invariants 54–60 (referent fidelity;
  semantic source identity; one occurrence one source with cross-form convergence; public mutation
  acceptance; route identity parity; diagnostic boundary with the SI-16 wording constraint; one
  identity authority) and the obligations block carrying the exact SI-15/SI-16 owner payload
  ("Can we add that…", once) and the SI-18 payload with the preserved "quesiton" typo (once), plus
  the Items-4/6 snapshot blast-radius obligations.
- Contract: six new Appendix B rows (self-binding rescue; lenient consumer-local mint;
  reference→literal stamp; group-deriver backfill; route-specific convergence reading; synthesis
  as identity authority), phrased as decision records.
- Contract: status line and "Implementation candidate status" reconciled — 41/41 composed proof +
  2026-07-20 merge (mains `f4ebdce`/`936315c`/`fa0e06a`) citing both the release record and
  `CHANGELOG.md:74-100`; explicitly states source-identity cells remain uncertified.
- Disposition rows D-10..D-13 and D-16..D-18 tightened to cite the governing invariant instead of
  restating behavioral wording (one-home rule).

**Validation Results:**

- `phase2_check.py` → GREEN: 19/20/22/26 amended exactly once each and nowhere else; invariants
  54–60 present, no 61, spot checks 1/27/53 intact; "Never reinterpret" ×1 (D-4); "Can we add
  that" ×1 (obligations); "quesiton" preserved inside the intact guidance quote; six superseded
  mechanisms each in exactly one Appendix B row; stale candidate claim gone; release-record and
  changelog citations present; "uncertified" stated.
- `phase1_check.py` re-run → GREEN (Phase 1 authority unchanged by Phase 2 edits).
- `git diff --check` → clean.
- Provenance re-derivation: zero upgrades — D-4 `[OWNER-VERBATIM]`; D-5..D-8, D-12..D-15, D-19
  `[AGENT] (ratified by owner, 2026-08-05)`; D-9 `[INHERITED: KerML]`; D-10/D-11/D-16..D-18
  `[INHERITED]` from lifecycle invariants/standards; both obligation quotes `[OWNER-VERBATIM]`.

**Derivability dry-run (every Item 4 / Item 5 scope bullet → governing statement):**

Item 4 — 1 identity representation → inv 55 (+ inv 54; Appendix B stamp row for no binding-type
mutation), C24 (direct calculation-output declaration and producer occurrence), C17/C26
(producer-backed versus literal-valued aggregation sources); 2 occurrence authority → inv 60
(one bridge), C19 (nested target key, adjacent-work
row 2), adjacent-work row 1 via D-16 migration (reuse Item-10 machinery); 3 live/snapshot
transport → inv 58 + blast-radius obligation (bump, fail-closed, recapture, rebuild, no shim);
4 foundation tests → C19 (nested/flat), C7/C8 (multi-occurrence equal/distinct), C21
(specialization), C24 (computed mixed consumers), C25 (mixed binding-owner contexts), C17/C26
(aggregation topology split), referent table + NOP rows (per-child redefinition), pre-existing Appendix C
recursive/non-finite rows (cycles/cardinality), inv 58 (moved snapshot); 5 authoring validation →
obligations L2 bullet + inv 59 + SRC-01 + Appendix B rescue row (self-binding), D-8/D-19 + SRC-02
+ inv 59 (indexed readiness).

Item 5 — 1 reference/value separation → inv 54/55 + Appendix B stamp row; C16 + inv 22 (authored
literals); 2 one consumer route → inv 19 (amended) + inv 56; convergence targets C1–C6, C11–C15 +
R5, C24's producer channel, C25's mixed-context convergence, and C17/C26's exact aggregation
topologies; 3 terminal policy/diagnostics → inv 20 (amended) + D-17 (mint only for explicit external
inputs), C9/C10 (ambiguity), C18 (per-policy outcomes), D-14 (aggregation same rule); 4
superseded-route deletion → D-16/D-17/D-18 + inv 60 + Appendix B rows (VBR clearing, rescue,
minting, backfill, synthesis derive-or-delete); wrong-oracle test replacement → inv 57 + R5
mutation obligations + Appendix B rescue row; 5 adversarial tests → SRC-01 subrows + C1/C4/C5
(both fan-out paths), C16 (equal-value literals), C9/C10 + inv 26 (same-leaf ambiguity),
C17/C18/C26
(aggregation asymmetry), C11–C13 (mixed consumers), inv 57 (off-default mutation).

No bullet requires a semantic choice not already fixed by the contract chain.

**Issues:** None.

**Deviations:** Disposition rows D-10..D-13/D-16..D-18 cite governing invariants rather than
carrying parallel behavioral wording — a tightening within the design's one-home rule, decided
during implementation to keep the duplicate-sentence sweep clean.

### Phase 3 Completion

**Completed:** 2026-08-05

**Actual Changes:**

- Created `.project/concepts/constraint-execution-lifecycle-requirements.md` as an exact copy of
  the archived companion, then edited only: provenance header (archived path + close-state
  digest, within the first 12 lines); status line + Current proof verdict reconciliation (41/41,
  2026-07-20 merge, LC-SI uncertified); LC-D06/LC-D07/LC-D09/LC-E04B amendment notes citing the
  amended contract invariants; the `### SI.` section with 25 graded `LC-SI-*` projections
  (SI-07A and SI-11A distinct), each citing its governing contract statement by number/name
  without restating wording; and the scenario-citation line naming Appendix C
  "Source-identity scenarios" as the sole scenario authority.
- Contract `Requirements:` pointer (line 8) now names the durable companion (was the stale
  pre-archive `active/` path) — same change set as the copy.
- Archived companion untouched.

**Validation Results:**

- `phase3_check.py` → GREEN: archive digest unchanged; durable header names the archived path and
  digest; projected ID set exactly the 25 expected; every row grade ∈
  {NEED, HARD, INFERRED, INHERITED} with a governing citation and no restated cell fields;
  scenario section citation-only; exactly one contract `Requirements:` pointer resolving to the
  durable copy. `phase2_check.py` and `phase1_check.py` re-run GREEN. `git diff --check` clean.
- `git status --porcelain .project/completed/` → 0 changes (Git object untouched).
- Manual hunk classification (6 hunks): header+status (1,7→1,14), proof verdict (46→53),
  LC-D06/D07 (206→215), LC-D09 (218→233), LC-E04B (253→270), LC-SI section + scenario citation
  (424→444). No hunk outside the approved categories.
- Grade sample vs absorb mapping: owner-stated SI-01/09/15/16/18 → `[NEED]`; standards SI-02/04/07
  → `[HARD]`; ratified agent recommendations SI-03/05/06/07A/10/11A/19 → `[INFERRED]`; inherited
  evidence/contract sources SI-08/11/12/13/14/17/20/21/22/23 → `[INHERITED]`. Zero upgrades.

**Archive SHA-256:**
`3b7014bfc3973df0031c61a6f836e7a8c1f9b7da7ae5960ffcb37992e5afe56c` (before copy; identical after
every Phase 3 edit).

**Issues:** None.

**Deviations:** Checker refinement only: LC-SI-18/19/23 cite the contract's named obligations
block / Appendix C rather than a numbered invariant (obligations are unnumbered contract
statements); the phase checker accepts named-home citations for exactly that case.

### Phase 4 Completion

**Completed:** 2026-08-05

**Actual Changes:**

- Verification matrix: one legend line under the Status definitions defining the row-local
  `Contract disposition` annotation (and stating historical tests remain evidence of old
  behavior, not certification); the original seven blockquote annotations directly under their
  family tables —
  REQ-IR-06 `SUPERSEDED` (D-17, Appendix B lenient-mint row); REQ-IR-07 `PARTIAL` (both clauses
  `stands`; the route-general certification reading `SUPERSEDED` via the Appendix B
  route-specific-convergence row; cells C2/C4/C11–C15 own acceptance); REQ-SVM-01/02/04 `PARTIAL`
  (value-adapter clauses `stands`; independent-identity-authority reading `SUPERSEDED` via the
  Appendix B synthesis row; C14 cited at SVM-02); REQ-CL-05 `PARTIAL` (dedup-mint,
  producer-wiring, and `LIBRARY_DEFAULT` scoping clauses `stands` under D-12/C23; evidence does
  not yet certify the new contract); REQ-VBR-10 `PARTIAL` (`_rewrite_specialized_chain` `stands`,
  C21 kin; `_rescue_self_named_bindings` `SUPERSEDED` via D-4/SRC-01/Appendix B rescue row).
  Status cells, Summary metric table, Index counts, table structure, and test references
  untouched.
- Epic Item 3: status → amendments landed, audit + ratification pending; Current State ⚠️ bullet
  replaced with the landed-artifact inventory + remaining-work bullet; Dependencies line updated;
  deliverables list gains the no-standalone-files note (checkpoint item 1).
- Spec footer: stale spec-review/design next-step replaced with the implement → audit →
  ratification sequence; no requirement or provenance content changed.

**Validation Results:**

- `phase4_check.py` → GREEN: all 276 REQ row projections byte-identical to the before-capture;
  Summary metric table + Status definitions unchanged (legend line is the only permitted delta);
  Index byte-identical; exactly the original seven affected IDs annotated once each; PARTIAL
  clause labels present; REQ-VBR-10 clause split as designed; every annotation carries an Appendix
  B/C pointer. The audit correction adds four rows and the live checker now requires eleven.
- `phase3/2/1_check.py` re-run → all GREEN. `git diff --check` clean on all Phase 4 files.
- `uv run pytest tests/conformance/test_source_identity_routes.py -q` → 11 passed.
- `git status --short` → only the intended documents changed; no production code, fixture,
  snapshot, generated package, Item-1/Item-2 evidence artifact, or `completed/` file touched.

**Matrix Baseline Result:** before-edit projection captured to the session scratchpad
(`matrix_before.json`: 276 rows + Summary + Index); after-edit comparison byte-identical for all
immutable properties.

**Issues:** None.

**Deviations:** None.

### Correction Pass (2026-08-07, post-audit)

**Driver:** `audit.md` (2026-08-07, Needs Work) + `product-lens.md` audit-F1 BLOCK. Full
correction record: `design.md` A.8. Changes, by finding:

- **audit-F1 (computed-source topology):** cell C24 added (feature chain to a computed value ×
  1 calc + 1 constraint + 1 agg → `RUNTIME_SOURCE`, one producer channel, no minted public
  input) under an explicit D8 reopening — the first correction moves counts 26/32 → 27/33,
  changed together in the contract
  preamble (`contract:733,735`), cell (`contract:1153`), and design A.3/A.4/A.6/A.8. D-10 now
  names C24. Resolved by citation in `product-lens.md` (correction entry, 2026-08-07).
- **Customer binding-owner context:** verified against the model — mixed contexts
  (`meier_coe_calc` usage-authored, `hif_plant.sysml:205,215`; `lcoe_calc`/`recirc_calc`
  def-authored, `generic_ife/ife_plant.sysml:7,98,114,126,134,148`). 01b re-derived; the
  first correction's C4 + C1/C2 placement still lacked the exact one-usage/one-definition-context
  availability key. Double-checking added C25 for that full source occurrence; C2 owns the two
  definition-authored thermal-efficiency consumers, and C4 remains supporting DCS referent
  evidence. Final reopened counts are 28/34. Design Research Findings/representative cells/A.5
  were corrected (rev 6); stale `epic:145-148` citations → `epic:147-150`.
- **Aggregation topology and exact coordinates:** the final authority check showed that C17
  combined a producer-backed source with three literal-valued modeled sources. D8 reopened the
  population again: C17 now owns the exact `permitting.capital_cost` producer-channel coordinate;
  C26 owns the three literal-valued feature coordinates with one public input per source. C24 now
  names one direct calculation-output declaration, and 22a names one concrete expression binding.
  Current counts are 29/35.
- **SI-23 exactness:** C7/C8 (two occurrences, 1 calc per occurrence), C9/C10 (two-occ context,
  def default, 1 calc), C15 (1 parent agg + 1 parent constraint + 1 child calc), C16 (two
  literals, 1 calc each), 01g, and C11–C13 counts made exact; no `value_state: any` or
  per-occurrence parametric values remain (phase1 checker now rejects them).
- **SC4 (contradictory rows):** REQ-BT-13 `PARTIAL`, REQ-IR-01 `PARTIAL`, REQ-PGD-06
  `SUPERSEDED`, REQ-VBR-03 `SUPERSEDED` annotated with owning Appendix B pointers — 11
  annotations total; Status projection/Summary/Index still byte-identical.
- **Authority-state consistency:** the contract's Current conclusion is now the single
  authority-state statement (lifecycle ratified/merged; source-identity material draft-of-record
  pending owner ratification; stale closed-epic handoff removed); matrix legend no longer says
  "ratified" and points to it; spec status/footer, design handoff/footer, and the epic tail all
  direct to re-audit → ratification.
- **Invalid citation:** VBR stamp corrected to
  `src/sysml_codegen/orchestration/pipeline_builder.py:363-369` (D-16); verified on disk.

**Validation:** phase1 (29/35 + exact-key sweep), phase2, phase3 (archive SHA unchanged:
`3b7014bf…5afe56c`), phase4 (276-row projection byte-identical; 11 annotations) all GREEN;
`git diff --check` clean; 11/11 route tests pass. Counts in the Phase-1/Phase-5 stencils read
26/32 as written in the historical 2026-08-05 completion notes; the live stencils and D8 reopening
record govern — re-derivation target is 29/35.

**Next:** Item 3 complete; proceed to Item 4.

### Phase 5 Completion

**Completed:** Audit corrections, double-check, independent certification, and owner ratification
completed 2026-08-07. The retained route test's previously untracked status prevents a Git-based
proof that its bytes stayed unchanged during Item 3.

**Actual Changes:**

- Added C24 for the owner-required computed-source producer topology.
- Re-derived the customer from the actual mixed binding-owner contexts. The first correction's
  C4 + C1/C2 placement still lacked the exact one-usage/one-definition availability key, so D8
  reopened the population for C25. C25 owns mixed-context availability; C2 owns the two
  definition-authored thermal-efficiency consumers; C4 is supporting DCS referent evidence only.
- Made every flagged SI-23 key exact; annotated all eleven contradictory verification rows;
  corrected the VBR source path; and reduced authority state to the contract's Current conclusion
  with citation-only downstream references.
- Split aggregation's producer-backed and literal-backed source topologies into exact C17/C26
  coordinates; made C24's declaration identity and 22a's kept coordinate exact.
- Synchronized the live design, plan, companion, epic, spec, matrix annotations, and current-work
  handoffs to 29 cells / 35 coordinates and the corrected workflow state.

**Validation Results:**

- Structural checker: 29 unique cells, 35 unique coordinates, exact expected ID sets, every
  required coordinate field present, no parametric key phrases, and no `PENDING_CHECKPOINT`.
- Matrix checker: eleven unique expected annotations; every `PARTIAL` row uses the required clause
  vocabulary and carries a contract pointer; all 276 REQ rows remain byte-identical to `HEAD`.
- Projection/archive: 25 exact `LC-SI-*` IDs; archived companion byte-identical to `HEAD`, SHA-256
  `3b7014bfc3973df0031c61a6f836e7a8c1f9b7da7ae5960ffcb37992e5afe56c`.
- Links and hygiene: 79 local Markdown targets resolve; `git diff --check HEAD --` clean; status
  shows no production code, fixture, snapshot, generated package, Item-1/Item-2 evidence-directory,
  or `completed/` change. The retained Item-2 route-test file remains untracked, so Git cannot
  independently prove its bytes stayed unchanged throughout Item 3; the status checkbox remains
  open for that reason.
- Retained evidence test: `uv run pytest tests/conformance/test_source_identity_routes.py -q` →
  11 passed. The sandboxed first run could not open uv's read-only home cache; the approved rerun
  against the existing cache passed.
- Product lens: `audit-F1` explicitly resolved by citation to C24; fresh gate `CLEAR`. C25 closes
  the audit's exact customer-context gap.

**Owner Ratification:**

Recorded 2026-08-07. `[OWNER-VERBATIM]` “ok we just finished that item
(.project/active/source-identity-contract/audit.md)”. This completion declaration ratifies the
audit-certified C17/C24/C25/C26 population and assembled authority. It does not upgrade any
agent-originated disposition or correction to owner-originated provenance.

**Issues:**

- Double-checking the first correction found that C4 has two usage-authored consumers, while the
  customer has one usage-authored and one definition-authored availability consumer. Resolved by
  explicit D8 reopening and exact cell C25, not by broadening C4 parametrically.
- The final independent authority check found that C17 combined two source-topology classes and
  that C24/22a still carried alternative or parametric declaration coordinates. Resolved by the
  C17/C26 split and exact C24/22a declarations. The same check verified that C17 already has a
  producer channel at HEAD; only C26 is contradicted by the observed per-term mints.
- An initial local annotation assertion incorrectly required every `PARTIAL` row to contain a
  `SUPERSEDED` clause. D4 requires every clause to be labeled either `stands` or `SUPERSEDED`;
  REQ-CL-05 legitimately labels all three clauses `stands`. The corrected checker passes.

**Deviations:**

- The post-audit correction record initially stopped at 27/33. Evidence-faithful correction of the
  customer key required a second added cell in the same D8 audit-correction reopening, producing
  28/34. Exact separation of aggregation's producer-backed and literal-backed sources required a
  third D8 reopening, producing 29/35. These changes follow D8's failure branch and are recorded
  across derivation, enumeration, counts, and handoffs.

---

**Status:** Draft → In Progress → Audit Certified → Complete (owner ratified 2026-08-07)
