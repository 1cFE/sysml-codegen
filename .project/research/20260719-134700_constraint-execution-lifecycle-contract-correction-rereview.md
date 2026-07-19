---
date: 2026-07-19T13:47:00-07:00
researcher: Claude (focused correction-delta re-review, three independent lanes + sequencing analysis)
topic: "Re-review of the corrected constraint-execution lifecycle contract: are the adversarial corrections faithful, complete, and sufficient for ratification?"
tags: [research, constraints, lifecycle, architecture, adversarial-review, re-review, ratification]
status: complete
last_updated: 2026-07-19
---

# Correction Re-Review: Constraint Execution Authoritative Lifecycle Contract

**Reviewed artifacts:**
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` (contract),
`.project/active/constraint-execution-lifecycle-contract/spec.md` (spec).
**Baseline:** `.project/research/20260719-125806_constraint-execution-lifecycle-contract-adversarial-review.md` (§8 is the required-correction list).

**Method:** three independent lanes — (1) correction traceability, (2) acceptance-proof attack,
(3) architecture/provenance fidelity with git-state verification — plus a sequencing analysis of the
ratification gate. Lanes 2 and 3 ran read-only code and git probes (sysml-codegen, agentic-mbse,
teax, stellarator repos). Nothing was modified. This is a correction-delta review; it did not rerun
prior remediation audits or test suites (§6).

---

## 1. Verdict

**Ratifiable after minor enumerated edits — as the normative target architecture only.**

The correction pass is faithful and nearly complete: 12 of the 14 required §8 corrections are fully
applied in both documents, all 15 previously missing acceptance cells exist in both matrices, every
hash/tense/status claim checked against git state is accurate, and D-1/D-2/D-3 and the
simplification constraint survive intact with no settled decision weakened or reopened.

Three things stop an unconditional verdict, all bounded text edits (§5):

1. **One proof hole of the original E-1 class survives:** producer completeness (invariant 26 second
   sentence / LC-E04B) is acceptance-orphaned — a concrete supported model (two same-leaf candidate
   attributes feeding a constrained calc) still fails end-to-end while every cell passes as worded
   (§3.1). Two smaller between-green-cells compositions also survive (constraint-free × file-backed
   evaluator; excluded-only × evaluation).
2. **The ratification gate is circular as worded** and conflates ratifying the target architecture
   with certifying an implementation candidate. The gates must be separated (§4).
3. A short tail of wording defects: one present-tense regression (invariant 21), two misleading
   Appendix B source labels, several contract-vs-spec table divergences, and a register rows 1↔5
   ordering inversion (§3).

None of these requires reopening an owner decision or restructuring the architecture. With the §5
edits applied, the owner can ratify the contract as the behavioral authority.

---

## 2. Correction traceability (review §8 → contract + spec)

| § 8 item | Status | Notes |
|---|---|---|
| 1. Pin/re-tense candidate claims (C-1/C-2) | **Fully applied** | New "Ratification candidate status" section; invariants 10/12 and LC-C05/C07/C08/C12 re-tensed to "ratification target"; Appendix A row 2 honest. All three base hashes and dirty-tree characterizations verified true against git (`512786c` codegen HEAD; `4ed2a07` companion HEAD with v3 committed / v4 uncommitted, `is_negated` absent from committed profile; teax `d545701` with only untracked logs; committed floor `agentic-mbse>=0.1.1` vs committed companion `0.1.0` — mutually unsatisfiable, exactly as stated). |
| 2. Re-tense Appendix B row 4 + resolver gap row (B-3) | **Fully applied** | "Shared resolver implementation is required but does not exist today"; LC-D06 names the three drifted ladders; register row 2 in both docs. |
| 3. Matrix pinning rule (E-1) | **Fully applied as a record obligation** | Proof standard + LC-I09 + Appendix C preambles; "Live" excludes prebuilt `ConcreteConstraint`. Residual: the coordinate *records* shape but only route/shape-named cells *mandate* one — see §3.2. |
| 4. Fifteen missing cells | **Fully applied** | All fifteen present in both tables, each verified individually; most at failure-coordinate strength (nullable-QN crash named; distinct-override values make collapse visible; constraint-free cell reaches TEAx evaluation; fact-consumer cell is behavioral). |
| 5. D-3 scope expansion (D-4) | **Fully applied** | Five fields named in inv 28/LC-E05; migration-or-archive in inv 50/LC-G07/LC-G10; hand-authored fixture + stand-in fingerprint named purge targets; additive LOC booked under LC-I08/row 10. Minor: field *placement* not pinned (§3.4). |
| 6. Broaden portability (B-2) | **Fully applied** | Inv 34/LC-F04 cover docstrings, loader fields, IDs, full tree; relocated cell demands "no checkout-absolute bytes anywhere" (absolute, not differential — kills same-machine cancellation for that cell). |
| 7. Invariant 26 producer completeness (B-4) | **Applied in requirement, orphaned in proof** | Inv 26/LC-E04B name both proxy failure modes; new "graph-complete producer validation" lifecycle stage. But no acceptance cell drives the ambiguous/defaulted shape — §3.1. |
| 8. WI-027 D7 supersession (A-2) | **Fully applied** | Owner-ruling provenance in D-2 text, Appendix B row 4 source column, LC-D08; stellarator cells require passthrough removal. (The stellarator artifact's back-pointer is imposed work, verified still absent — implementation, not a contract defect.) |
| 9. Option lists under D-1/D-2/D-3 (A-1) | **Fully applied** | Both options recorded under each decision, correctly graded `[AGENT]`; all four owner quotes character-identical between contract and spec. |
| 10. Split gap row 10 (D-13) | **Fully applied** | Row 3 carries the check-scope defect + "file fusion finding #8"; row 12 carries the cost-rollup half. |
| 11. Four missing invariants (F-4, F-5/D-1, F-2, B-6) | **Fully applied** | Inv 46a/LC-G12 (constraint-free, choice made: TEAx tolerates); inv 39/LC-F09 (verifier + version skew); inv 37/LC-F06 (seal provenance manifest); inv 53/LC-F01 (grandfather fail-closed). Each has matching cells and register rows. |
| 12. Rescope gap rows 4 and 12 (C-3, D-5) | **Fully applied** | LC-B08 requires the facts-schema bump + two-direction skew tests; LC-G11/Appendix A frame persistence as build work. |
| 13. Register housekeeping (A-3/A-4/A-5/F-15) | **Partially applied** | Census C-5 row added; source column added; `assessment_failed` (inv 51/LC-G13), margin discipline (inv 52), aggregator exit-ancestry (inv 32) restored; LC-E02 surviving rationale stated; Gate B vacuity-probe-first ordered in inv 24/LC-E02/row 3. **Gap:** Appendix B rows 7 and 19 label conversational supersessions "Historical snapshot prose"/"Historical architecture prose" — document-style attributions for claims the review found exist in no document (§3.5). |
| 14. Strengthen stub-satisfiable observations (E-obs) | **Partially applied** | Rows 12 (`-0.1`/`[MW]`), 21 (report content, not shared wrapper), 23 (concrete bypass), 24 (nested models) strengthened in both docs. **Gaps:** the spec's shared-demand row kept the pre-correction "deterministic grouping" wording (contract has "with no overwrite"); the row-16 margin silent-corruption probe exists only implicitly (inv 52 + polarity cells, no dedicated probe); the four-arithmetic cell is still agreement-based — both evaluators agreeing on a wrong hardcoded `MODULE_EXECUTION` phase passes (§3.3). |

---

## 3. Remaining defects (exact references)

### 3.1 Proof holes — the matrix can still go green over a failing model

- **CX-1 (highest severity): producer completeness has no cell.** Supported in-family model: two
  concrete part usages with same-leaf attributes (`pumpA.power`, `pumpB.power`), a calc def with an
  unbound `power` input, a constraint on the calc output. Today the calc ladder logs a WARNING and
  binds `candidates[0]` (`src/sysml_codegen/analysis/dependency_backtracker.py:851-857`); after
  unification the calc consumer legitimately keeps a lenient terminal (LC-D07 reserves the
  synthesized fallback for calcs). Either way: V11 clean, package seals, TEAx returns a confident
  verdict about the wrong or defaulted value. "Producer completeness" appears in the success
  criteria, LC-E04B, contract prose, and register row 12 — and in **zero acceptance rows**. Row 12's
  exit names no proof cell, so it is satisfiable by a unit test on a fixture without the ambiguous
  shape. Same acceptance-orphaned class the baseline review flagged for invariants 37/50; those got
  cells, this did not. Edit E8.
- **CX-2: constraint-free × file-backed evaluator.** The zero-usages cell reaches TEAx evaluation
  (closing F-4 at the prepared evaluator, `teax .../simkit/evaluation/evaluator.py:132`), but a
  second unconditional `result.outputs[REPORT_CHANNEL]` read exists on the file-backed route
  (`evaluator.py:203`). The file-backed cells cover completed constraint reports only. Fix `:132`
  alone and every cell is green while the public file-backed route dies on a constraint-free
  package. Edit E9.
- **CX-3: excluded-only × evaluation.** The excluded-only cell's observation stops at codegen
  ("Portable exclusions plus `not_assessed`"); whether a zero-eligible-entry model emits an
  aggregator is stated nowhere (inv 32's "whenever a constraint report is required" leaves
  required-ness undefined for that population), and the row-13 fix maps *absent* report → *empty*
  evidence, not `not_assessed`. No cell reaches excluded-only × TEAx evaluation. Edit E10.
- **Gate A cell shape not pinned.** "Literal design-attribute actual (D-2)" (contract line 420; spec
  merges it into one vaguer row at 434) does not mandate the real failure shape — usage-owned
  attribute on a concrete PartUsage, self-named actual (`stellarator_plant.sysml:700-753`). LC-I09
  makes the certifier *record* owner kind; nothing requires the usage-owned shape, so the existing
  def-owned fixture (`tests/fixtures/constraint_inline/model.sysml:16-21`) certifies it. The
  stellarator row eventually forces the shape, but ten register rows later. Edit E11.
- **Route ambiguity.** LC-I09 puts "both public live/relocated routes" in every coordinate, yet
  cells still name routes ("× snapshot") — pointless under the every-cell reading. Under the
  cell-specific reading, no cell replays a negated assertion from a snapshot and none combines
  negation with a modeled default; a replay-lane or default-wiring polarity defect escapes green.
  Edit E12.
- **Four-arithmetic cell is agreement-based.** "Both evaluators agree on phase/module/cause and
  complete report content" — the phase tag is hardcoded `MODULE_EXECUTION` and `OUTPUT_WRITE` is
  never emitted (baseline D-8, no register row); two evaluators agreeing on the wrong phase pass.
  Edit E23.

### 3.2 Ordering-rule enforcement

- The register footers claim the evidence coordinate enforces ordering by "naming every open
  predecessor" (contract 509–510; spec 487–488, attributing it to LC-I09). **LC-I09 defines no
  open-predecessors field** — neither does the contract's proof-standard list. A certifier fully
  compliant with LC-I09 never names a predecessor. The revision-binding half is real and auditable
  ("Release readiness is false if a mandatory cell … uses a different revision"); the predecessor
  half is an unspecified claim. Edit E12.
- **Register rows 1↔5 inversion.** Row 1's exit requires the anonymous-actual cell, whose relocated
  leg requires "no identity drift" — but anonymous eligible IDs digest the raw absolute `loc.file`
  (`constraint_lowering.py`, `_source_local_identity`), and portable anonymous IDs are **row 5**'s
  exit. As ordered, row 1 must either certify around an open later dependency (violating the rule it
  sits under) or silently block on row 5. Edit E13.
- **Row 17 is narrower than the ratification sentence.** "That one revision set passes the mandatory
  public-path matrix" lives only in the ratification-gate paragraph; row 17's exit names the
  composed thread but not "all cells at the pinned revision." A literal row-17 reading permits cells
  certified at stale mid-epic revisions plus one passing composed thread. Folds into the §4
  restructuring (edit E7).

### 3.3 Contract ↔ spec divergences (meaning-changing)

1. Shared-demand cell: contract 416 "survives deterministically **with no overwrite**" vs spec 433
   "deterministic grouping/count/warning" — the spec wording is exactly what the baseline review
   showed passes on last-wins overwrite. Edit E14.
2. "Excluded-only usages" report-surface cell exists only in the contract (408); the spec's nearest
   rows cover a different population or a channel shape. Edit E10.
3. "Remediation simplification" cell exists only in the spec (456); the contract's mandatory matrix
   never requires the LC-I08 accounting proof its own simplification constraint declares. Edit E15.
4. The spec merges the contract's three actual-source cells into one vaguer D-2 row (434), losing
   "Default applies and an override changes verdict," and drops "legitimate shared producer recorded
   in the catalog" from the multi-occurrence row — the only observation that would prove
   catalog-visible sharing (baseline §9 flagged sharing as graph-visible only). Edit E16.
5. Invariant 50 binds to "semantic/executable" fingerprints; LC-G10 to
   "semantic/**catalog**/executable." The invariant is the odd one out. Edit E20.
6. LC-I09's non-certifying list omits "same-machine path cancellation" (present in the contract
   proof standard, 329). Edit E12.
7. The tables are not row-for-row alignable (≈39 vs ≈37 rows) — tolerable once 1–4 are fixed, but it
   weakens cross-document ordering audits.

### 3.4 Provenance and tense

- **Invariant 21 present-tense regression** (contract 172–174): "It **is available** during graph
  construction and **reuses** the same QN-keyed typed entry point" — reads as current behavior while
  Gate A is open and Appendix B row 4 says the shared resolver "does not exist today." The exact
  tense class the corrections were purging. Edit E17.
- **Contract 101–102**: "The normal product path rejects grandfathered skip-lowering snapshots" —
  present indicative about a known-open gap (`snapshot/graph_rebuild.py:236` warns and proceeds).
  Edit E18.
- **LC-G07 grade stretch**: the migration-or-archive transition mechanics inside the `[NEED]` are
  agent-derived (from baseline D-4), not owner-originated; binding to real identity is the owner
  content. No enforcement loss (duplicated in `[INHERITED]` LC-G10/inv 50), but per the absorb
  mapping that sentence belongs at `[INFERRED]` or in LC-G10 only. Edit E21.
- **Five-field placement imprecision**: inv 28/LC-E05 name all five fields but not where each lives
  (per-eligible concrete entry; `owner_qn` as a real QN distinct from the existing
  `owner_instance_path`, whose semantics differ — verified: `generation/constraint_catalog.py:96-117`
  carries `owner_instance_path` only; `source_form` exists only on excluded records). Enforceable via
  LC-H02A's no-reconstruction rule, but an implementer could waste a cycle. Edit E24.
- Verified non-defects worth recording: LC-C06's "No equality or `!=` currently executes" is **true
  of both committed v3 and the v4 worktree** (probed: `classify_equality` warns/blocks on every
  path) — lane 1 flagged the tense, lane 3's probe clears it. All honest "current code lacks/
  violates" admissions were re-probed and none is stale (`tracking_key` still zero writers;
  codegen's `semantic_fingerprint` still zero real consumers — teax's same-named
  `study/config.py:60` digest is a different object; nested evidence still mutable).

### 3.5 Register-honesty

- **Appendix B rows 7 and 19** source labels ("Historical snapshot prose," "Historical architecture
  prose") assert document-style sources for supersessions the baseline review (A-4) found exist in
  no document. The source column was added to fix indistinguishability; for these two rows it now
  reads as positive misattribution. Edit E19.
- The contract's "Current conclusion" open-work list omits register row 16 (grandfather/
  tracking-key); every other row is represented. Edit E22.

---

## 4. Ratification vs. candidate pin: yes, it is circular — separate the gates

**The circularity is real, in two strengths.**

- **Hard circle:** the contract blocks ratification "until every relevant change is committed, the
  exact cross-repository hashes and locks are recorded, **and that one revision set passes the
  mandatory public-path matrix**" (Ratification candidate status, final paragraph). Passing the
  matrix is register **row 17** — the last row, dependent on rows 0–16, i.e., the entire remediation
  program. Meanwhile both registers say the rows "become epic commitments only after owner
  ratification," and the spec's Next step says "do not resume implementation orchestration before
  those steps" (the epic's Next Action likewise records orchestration paused). Ratification waits on
  the whole program; the program waits on ratification.
- **Soft circle:** even the weakest internal reading (spec Next step: land candidate → ratify)
  requires row 0 first — but landing the candidate means committing the uncommitted profile-v4 and
  lifecycle work, which is exactly the implementation activity the same texts pause until
  ratification. The three internal statements of the gate (status lines, "Current conclusion"/"proof
  verdict," candidate-status paragraph) also disagree with each other about which strength applies.

**Diagnosis:** the documents conflate two different owner acts.

- **(a) Ratification of the normative target architecture** — an owner act on the *document*. Its
  prerequisites are documentary: corrections faithful, no present-tense overclaims, provenance
  sound, matrix well-formed. After the item-1 re-tensing, no invariant makes a current-state claim
  that needs a pinned commit to be falsifiable — which was the entire reason baseline correction 1
  tied hashes to ratification. The re-tensing branch of that correction is done; the pin branch is
  no longer needed *for ratification* and survives only as a certification prerequisite.
- **(b) Certification of an implementation candidate** against the ratified architecture — needs row
  0's pinned, mutually installable revision set and ultimately row 17's composed matrix pass.

Requiring (b) before (a) inverts the documents' own design: the contract explicitly separates "what
the architecture must do" from "what current code proves" (Appendix A), and the register's ordering
rule has normative force only after ratification — exactly the period during which the work it must
bind is happening. **Ratify first; the register becomes binding; row 0 lands the candidate; row 17
certifies it.** Ratification must state that it certifies no current behavior; Appendix A remains
the honest ledger in the meantime. LC-I09's revision binding already prevents any cell from being
certified before a pinned candidate exists, so separating the gates loses no rigor.

Sequencing edits are E1–E7 below. With them, the answer to "must a commit-pinned compatible
candidate exist before the owner can ratify?" is **no** — it must exist before anything can be
*certified*, and that is register row 0's job, activated by ratification.

---

## 5. Proposed text edits

### Contract edits (blocking = B, minor = m)

- **E1 (B)** Status line: → "Proposed authority — adversarial corrections applied and re-reviewed;
  awaiting owner ratification as the normative target architecture. No certified implementation
  candidate exists."
- **E2 (B)** Retitle "Ratification candidate status" → "Implementation candidate status." Replace
  the final paragraph with: "Ratifying this contract adopts the target architecture and activates
  the remediation register; it certifies no current behavior. Certification and release readiness
  remain blocked until every relevant change is committed, the exact cross-repository hashes and
  locks are recorded (register row 0), and that one revision set passes the mandatory public-path
  matrix (register row 17)."
- **E3 (B)** "Current conclusion": replace "The contract is not ratifiable until a commit-pinned
  compatible candidate exists, the correction set here receives focused re-review, and the expanded
  matrix is owned." with "With the correction set re-reviewed, the contract is ratifiable as the
  normative target architecture. Ratification certifies no implementation: no matrix cell may be
  certified and no release claim made until register row 0 pins a compatible candidate and row 17's
  composed proof passes on it."
- **E7 (B)** Row 17 exit (both docs): append "…and every mandatory matrix cell is certified at the
  pinned revision set."
- **E8 (B)** New acceptance cell (both docs): "Ambiguous/defaulted producer resolution | A model
  with two same-leaf candidate design attributes and a defaulted-fallback shape fails generation
  with a named ambiguity/producer error (or resolves only under exact QN); no verdict is ever
  produced from a guessed or defaulted binding while V11 is clean." Strengthen register row 12 exit:
  "…proven independently of V11 **through the ambiguous/defaulted acceptance cell**…"
- **E9 (B)** Zero-constraints cell (both docs): "…loads/evaluates in TEAx **through both the
  prepared and file-backed evaluators** with empty constraint evidence."
- **E10 (m)** Excluded-only cell: append "; the sealed package evaluates in TEAx with a
  `not_assessed` report surface." Add the missing excluded-only report-surface row to the spec
  table. State in inv 32/LC-E10 whether a zero-eligible-entry model requires the aggregator.
- **E11 (m)** D-2 literal cell (both docs): "…with a usage-owned attribute on a concrete PartUsage
  and a self-named actual; no passthrough required."
- **E12 (m)** LC-I09: add "same-machine path cancellation" to the non-certifying list; add an "open
  predecessor register rows" field to the evidence coordinate (or delete "naming every open
  predecessor" from both register footers); add one sentence: "Every cell certifies on both routes;
  a route named in a cell title pins the historically failing coordinates and exempts nothing."
- **E13 (m)** Register row 1 exit (both docs): "…cells pass **on the live leg; the anonymous cell's
  relocated leg completes with row 5**."
- **E14 (m)** Spec shared-demand row: append "with no overwrite."
- **E15 (m)** Add the "Remediation simplification" row to contract Appendix C (mirror spec 456).
- **E16 (m)** Spec table: split the merged D-2 row back into producer-channel / literal
  design-attribute / modeled-default (restoring "Default applies and an override changes verdict"),
  and restore "legitimate shared producer recorded in the catalog" on the multi-occurrence row.
- **E17 (m)** Invariant 21: "is available … reuses" → "must be available … must reuse."
- **E18 (m)** Contract 101–102: "rejects" → "must reject."
- **E19 (m)** Appendix B rows 7/19 source column: → "Conversational supersession (no documentary
  source); historical snapshot/architecture prose."
- **E20 (m)** Invariant 50: "semantic/executable" → "semantic/catalog/executable."
- **E21 (m)** LC-G07: mark the transition-mechanics sentence `[INFERRED]` (or move it into LC-G10).
- **E22 (m)** "Current conclusion" open list: add "grandfather fail-closed and tracking-key
  lifecycle."
- **E23 (m)** Four-arithmetic cell (both docs): append "with the expected phase for each shape
  pinned by the fixture, not established by mutual agreement."
- **E24 (m)** LC-E05: one clause pinning placement — "each on the per-eligible concrete entry;
  `owner_qn` is a real qualified name distinct from `owner_instance_path`; the join is entry-level."

### Spec-side sequencing edits

- **E4 (B)** Status: → "Draft — adversarial corrections applied and re-reviewed; awaiting owner
  ratification as target architecture. Implementation certification separately blocked on register
  rows 0 and 17."
- **E5 (B)** "Current proof verdict" last sentence: → "Certification of any candidate requires
  committed hashes, locks, and one public-path artifact thread; ratification of the target
  architecture does not wait on them."
- **E6 (B)** "Next step": → "Seek owner ratification of the target architecture and amend the
  remediation epic so every register row has an owner. Then land the commit-pinned candidate set
  (row 0) and resume implementation orchestration; certification follows the register order and
  row 17 runs last."

### Implementation backlog (not contract edits; distinct from §5)

- The `evaluator.py:203` file-backed unconditional read joins the row-13 fix scope (the contract
  edit E9 makes it provable; the code fix is row 13's).
- D-8 phase-tag honesty (`OUTPUT_WRITE` never emitted / collapse the enum) still has no register
  row; it was baseline implementation backlog and remains so — E23 only makes the cell able to see
  it. Consider attaching it to row 7 or row 15.
- WI-027 back-pointer + passthrough removal (row 12), stellarator artifact refresh — imposed by the
  contract, verified still absent, correctly classified as open work.
- All baseline §8 "implementation backlog" items (R-4/5/7/8/9, tracking_key, stale comments, v3
  literals) remain open in the working tree and remain correctly owned by register rows.

---

## 6. Not re-audited; remains unproven

- **No test suite was run** and no prior remediation audit re-executed; component certifications
  (Items 1/2/4/6, GAP-CLOSE) were taken at their recorded status.
- **Committed-state claims** were verified only via targeted git probes (HEADs, status, committed
  profile/pyproject contents) — not by installing or building any pair.
- **Companion repos** were spot-probed only at disputed coordinates (`evaluator.py:132/:203`,
  committed vs worktree `executable_profile.py`, WI-027 `design.md`, teax `study/config.py`,
  `graph_rebuild.py:236`, `constraint_catalog.py`, `dependency_backtracker.py:851-857`). No broad
  re-audit of teax/fusion-tea/stellarator behavior.
- **IFE acceptance numbers** (2,294/2,301) and the evidence census's ledger were not re-verified.
- **The owner quotes** still have no corroboration outside contract+spec; per the baseline's
  accepted Lane-A position this is resolved by the recorded `[AGENT]` option referents, not by
  external evidence — it remains a durability, not a fidelity, risk.
- **Implementability of the matrix** was not tested: cells were attacked as text; whether each can
  be built as a real fixture/test at reasonable cost is unassessed and lands with its register row.
- The counterexamples in §3.1 were constructed against current code paths; their post-remediation
  reachability depends on row-2/row-12 design choices and should be re-checked when those rows'
  specs exist.
