# Product-lens ledger — constraint-semantics-contract

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they
amend.

## spec — 2026-08-12 — rev 2ebf638 (+ untracked `.project/completed/20260814_constraint-semantics-contract/spec.md`)
Epic: none (spawned from ELABORATE-FIRST Item 7 correction; not a listed epic item)

Point (re-derived, written before reading the WORK):
1. Every constraint usage the model authors stays visible with exactly one disposition; every supported
   asserted one executes and yields read-only evidence; no report or study label may claim more coverage
   than was assessed. [source: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
   invariants 1, 28, 32, 33, 41, 49 + the "mental model" three-jobs separation, grade: agent/ratified —
   the contract is owner-ratified ("Ratified.") but its invariant text is agent-authored, and the contract
   itself says owner approval does not rewrite origin]
2. Enforcement/derivation gaps are closed by direct modeled resolution and one authority, never by a
   passthrough, adapter, bridge, or post-build seam. [source: same file, D-1/D-2/D-3, grade: owner-verbatim]
3. Coverage/catalog truth has exactly one schema authority that TEAx consumes directly, with no consumer
   adapter and no seam that re-derives constraint context outside the graph+catalog. [source: invariants
   40, 48, LC-G07, grade: agent/ratified; D-3 grade: owner-verbatim]
Falsifier: a run in which a swept constraint usage has no catalog carrier, or the report/study label
reads `all_satisfied`/`unconstrained` while authored gates went unassessed, or coverage truth is
computed from a second inventory that must be hand-kept in sync with the catalog.

Findings:
- spec-F1 [DON'T] The headline vocabulary change (Q5: `all_satisfied` = every applicable authored gate
  assessed and passed, plus a new partial tier) contradicts invariant 33 and LC-E11 as written ("else any
  assessed result → `all_satisfied`") — `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:232`,
  `.project/concepts/constraint-execution-lifecycle-requirements.md:299-301` (agent/ratified, INHERITED) —
  NOT owner-grade, and the original concept's own edge case ("documented-only constraints never create a
  false `all_satisfied` result", `constraint-execution-and-design-space-studies.md:198`) supports the
  correction. This is an intentional product-contract change, so per §2 it must be filed:
  disposition: INTENDED-CHANGE — file `.project/scripts/adr.sh new` + `amend` the affected entry with
  owner-ratified provenance and cite the id here. Not blocking.
  Filed: ADR-009 — docs/architecture/modeling-assumptions.md §9 (2026-08-12).
- spec-F2 [DO] The amendment set is under-scoped. The spec names only invariants 8, 32, 33 (Open
  Questions) but its rulings also touch: invariant 1 (spec narrows "any `BLOCK` halts the model" to
  "`BLOCK` on an asserted constraint", relying unstated on the profile's pre-predicate form gate — the
  consequence, that an unsupported predicate hidden in a bare `constraint` permanently escapes the halt,
  is a product statement that must be written down); invariant 9 (a new generation-halting severity for an
  ADMIT-side structural cause); invariant 28 / LC-E05 (a third disposition kind, "non-reaching-with-reason");
  invariant 46 and **46a** (new report fields change the persisted-exact-report contract, and 46a is the
  obligation that makes "constraint-free stays report-free" safe on the TEAx side — a new headline token
  needs the same fail-closed-not-`KeyError` treatment); invariant 48; and Appendix C's "Excluded-only
  usages", "Zero constraint usages", "Mixed satisfied/violated/indeterminate population" cells.
  — contract invariants 1/9/28/46/46a/48 + Appendix C (agent/ratified) — disposition: design must publish
  the complete amendment set, invariant-by-invariant, before code lands.
- spec-F3 [DO] No amendment route is named for the **frozen** requirements companion, whose header says
  "forward requirement amendments happen here only". LC-E10, LC-E11, LC-E12 and LC-E05/E06 all state the
  behavior the spec changes; the spec cites only the contract as "ratified authority being amended"
  (`spec.md:250`). — `.project/concepts/constraint-execution-lifecycle-requirements.md:3-7,276-306`
  (agent/ratified) — disposition: name the companion in the amendment set alongside the contract.
- spec-F4 [DO] The totality gate introduces a second constraint inventory without assigning ownership.
  Q3 gates by comparing "the manifest sweep against catalog carriers" and defers "the completeness gate's
  mechanical home" — but invariant 48 makes the embedded catalog the sole catalog authority and invariant 40
  forbids downstream constraint seams that consume anything other than the graph + embedded catalog.
  The sweep is also already a *third* representation: `modeling-assumptions.md:482-488` records
  `collect_constraint_manifest()` + `test_constraint_migration_mapping.py` as the license-free totality
  proof surface, and ELABORATE-FIRST **Item 7 scope item 2** is deleting the dual constraint-fact
  extraction pass (`epic_elaborate_first_architecture.md:427-450`). — invariants 40, 48; D-3
  (owner-verbatim for "no second catalog authority"); Item 7 deletion ledger (agent/ratified) —
  disposition: design must state which single authority owns totality and that the gate reads graph+catalog,
  not a parallel sweep. **Smells fired: #1 (two representations kept in sync) and #7 (ownership of the
  totality invariant moves silently).** Both must escalate into the stage judgment, not sit in a rubric.
- spec-F5 [DO] Coverage truth is duplicated into the report while the catalog already carries it. Q5 puts
  authored-total / assessed / excluded-with-reason-histogram in `ConstraintReport`, joined by fingerprint,
  while per-usage detail stays in the catalog TEAx already consumes directly (invariant 48). Two places
  now state the same coverage fact and must agree. — invariants 46, 48; LC-E06 (agent/ratified) —
  disposition: design must state the derivation direction (which artifact is computed from which) so the
  pair cannot diverge. **Smell #1 again.**
- spec-F6 [DO] Q4's "in-predicate feature chains remain blocked" is stated without reconciling it against
  invariant 12 (the ratification target admits inline assertions), Appendix C's "Positive/negated ×
  inline/definition-typed" cell, D-7 (occurrence-rooted feature chains SUPPORTED), and invariant 20
  (amended): "Positive resolution may not fork into consumer-specific ladders." As written, "the blessed
  gate shape is a `constraint def` with formals" reads as narrowing inline admission and as a
  constraint-only restriction on a form calculations support. — invariants 12, 20; D-7; Appendix C
  (agent/ratified) — disposition: state explicitly that the restriction is predicate-body-only, that
  binding-position chains stay supported per D-7/invariant 20, and that inline asserted forms remain
  admitted. Related: the owner-decided D-2 acceptance cell requires "a usage-owned attribute on a concrete
  `PartUsage` and a self-named actual" while D-4/SRC-01 makes bare self-named bindings UNSUPPORTED — a
  pre-existing conflict this spec's blessed-shape ruling now sits on top of. Surface it (capture-fidelity
  law 4); do not resolve it silently.
- spec-F7 [DO] `REQ-EXT-09` is still marked **PASS** ("every `ConstraintUsage` swept … SHALL have a catalog
  carrier … nothing silently absent", `docs/architecture/verification-matrix.md:336`) while the spec's own
  evidence shows 56/65 absent. The spec corrects only REQ-CL-04's PARTIAL row (`spec.md:38-39`). The green
  row and its conformance test pass because the specimen fixtures each have a carrier — the exact signature
  of **smell #6** (a test passes only because it selects one interpretation). — verification matrix,
  `modeling-assumptions.md:482-488` (INHERITED) — disposition: REQ-EXT-09 must be re-graded and its proof
  re-anchored in the same landing as the totality gate.
- spec-F8 [DO] Item 7 obligations the pause can orphan. The spec's non-goal keeps narrow-correction steps
  4–10 as the plan of record but records no interaction, and this contract work lands catalog/report/schema
  and fixture changes ahead of them: step 4's "recorded REQ-CL-03 pre-amendment behavior check" and the
  three-route `gain = 100` proof, step 7's "three complete final batteries at one final paired OID", step 8's
  regenerated candidate record, and Item 7 scope item 3's **one** 37-fixture recapture (a second recapture is
  now likely). — `.project/active/cutover-recovery/plan.md:6531-6577`,
  `.project/backlog/epic_elaborate_first_architecture.md:427-450` (agent/ratified) — disposition: design must
  record which Item 7 evidence is invalidated and must be re-run after this contract lands, and whether the
  recapture is deferred into this item or repeated.

Not findings (checked, clean): no owner-graded statement was contradicted. The eight rulings do not touch
D-1 (no late-fill/post-build seam — the totality gate is a check, not a mutation), D-2 (direct
design-attribute actuals), D-3 (canonical embedded catalog), invariant 11 (no equality executes — Q4's
two-inequality bands and the deferred `==` tolerance non-goal are consistent), invariants 41/49 (read-only
policy, correctly cited), or the owner's handoff sequencing. The D1–D7 doc corrections target
agent-authored text: `modeling-assumptions.md` and `reference/28-*.md` carry no OWNER/HARD/ADR markers, so
the "bare constraint gives an enforced gate" line (`:489-491`) is agent text and correcting it by deletion
is the capture-fidelity-correct move, not a contract override.

Gate: DISPOSED (spec-F1..spec-F8) — no owner/[HARD] contradiction found, so nothing blocks. Two smells
fired (#1 twice, #6, #7) and must appear in the stage's leading judgment. spec-F1 requires an ADR before
implementation, and spec-F2/F3 (the complete amendment set) are the precondition for the design stage.

**Spec-side disposition record (2026-08-12, same session):** F1 → ADR obligation added to Known
Requirements. F2 → bare-constraint-escapes-halt product statement added to modeling policy; full
invariant amendment set replaced the partial list in Open Questions. F3 → frozen companion named in
the amendment requirement and Related Artifacts. F4 → single-totality-authority requirement added
(gate reads graph + embedded catalog; no parallel synced inventory); mechanical home stays deferred
within that constraint. F5 → derivation-direction obligation recorded in Open Questions for design.
F6 → predicate-body-only clarification written into the Q4 requirement; D-2/D-4 pre-existing
conflict surfaced in Open Questions as an owner item, not resolved. F7 → REQ-EXT-09 re-grade added
to Success Criteria. F8 → Item 7 evidence-invalidation register added to Open Questions for design.
