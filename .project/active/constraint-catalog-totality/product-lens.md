# Product-lens ledger — constraint-catalog-totality

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they
amend.

## spec — 2026-08-12 — rev 270e1ee (+ untracked `.project/active/constraint-catalog-totality/spec.md`)

Epic: CONSTRAINT-SEMANTICS (Item 2)
Epic gate: CLEAR — `.project/backlog/epic_constraint_semantics_contract.md` §Product-Lens,
epic-plan 2026-08-12, grade preserved: point sourced to `rulings-20260812.md`, **grade: owner**;
no item narrowed or contradicted the point.

Point (re-derived from the sources, not from the WORK):
1. Every authored constraint usage stays visible with exactly one disposition — eligible,
   excluded-with-reason, or non-reaching-with-reason — and "reaches no instance" is a disposition,
   never an absence. [source: contract invariants 1, 28, 61; LC-E05, LC-E06, LC-E13; grade:
   agent/ratified (2026-08-12, Item 1)]
2. One authority owns that inventory: the instance graph and its embedded catalog, which TEAx
   consumes directly. No second catalog, no parallel inventory kept in sync, no post-build seam.
   [source: contract invariants 40, 48; LC-G07; D-3 **[OWNER-VERBATIM]** "100% Option A. We need to
   purge this mess."; D-1 **[OWNER-VERBATIM]** no public late-fill]
3. Severity follows cause, not convenience: an asserted usage in executable scope with no
   attachment capability halts loudly and names the missing attachment; an asserted vacuous gate is
   warning-grade with an authoring advisory; plain and out-of-scope forms are visible records and
   never errors. [source: contract invariants 9, 61; Appendix C "Asserted vacuous gate"; LC-E13]
4. The reason any of this matters: constraints are how these models enforce physics so design
   search stays viable, and expectations are settled — documentation and expected outputs corrected
   and captured — *before* confirmation tests run. [source: umbrella spec Problem
   **[OWNER-VERBATIM]** "when we started this whole cleanup, it was while defining a policy around
   how to use constraints to enforce things like physics in a way that make our overall 'design
   search' viable"; epic success criterion **[OWNER]** "Documentation and the derivative's expected
   outputs are corrected and captured before confirmation tests run"]

Falsifier: a run in which an authored usage carries no disposition (or two), or in which totality
is proven by a second inventory that must be hand-kept in sync with the catalog, or a landing in
which the tests pass while shipped documentation still describes the pre-landing behavior.

Findings:

- spec-F1 [DO] **The authoring advisory's home is reopened as an Open Question that Item 1 already
  closed.** The spec defers "Where the authoring advisory surfaces for the vacuous case (elaboration
  diagnostic stream versus authoring validation in the companion repo), and at what grade"
  (`spec.md:226-227`), but contract invariant 61 and LC-E13 both state it: "authoring validation
  emits an advisory naming the usage and its detached owner", at warning grade, and invariant 59
  places unsupported/deferred-form reporting at authoring validation —
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:476-481`,
  `.project/concepts/constraint-execution-lifecycle-requirements.md:334-341` (agent/ratified
  2026-08-12, Item 1). Ratified agent-grade items are challengeable, but by re-deriving against the
  recorded reasoning — not by silently reopening them one item downstream. — disposition: either
  carry the contract's answer as an inherited requirement (advisory at authoring validation,
  warning grade, naming usage + detached owner), or state the question as a challenge to invariant
  61/LC-E13 and record what re-derivation would have to show. Not blocking.

- spec-F2 [DO] **The documentation half of the owner's sequencing rule is dropped, and two shipped
  statements point at this item by name.** The spec carries "[NEED: owner-directed sequence]
  Expected outputs are captured before confirmation tests run" (`spec.md:189-190`) but not the
  documentation half of the **[OWNER]** epic criterion (`epic_constraint_semantics_contract.md:108-110`).
  Item 1 deliberately left two forward pointers that this landing falsifies:
  `docs/architecture/modeling-assumptions.md:476-477` ("today a usage that reaches no instance gets
  no carrier at all. CONSTRAINT-SEMANTICS Item 2 closes that gap") and the migration-invariant
  paragraph at `:489-496` ("the independent proof that the invariant holds across every
  constraint-bearing fixture is pending, and CONSTRAINT-SEMANTICS Item 2 re-anchors it"). Nothing in
  the spec obliges correcting them. — disposition: add the doc-correction obligation for both
  statements, ordered before confirmation tests, alongside the requirement-row re-anchor.

- spec-F3 [DO] **The manifest sweep's disposition is left unstated while this item owns both the
  single-authority rule and the rows that are worded against it.** The spec forbids a parallel
  sweep and puts the gate on graph + embedded catalog (`spec.md:88-92`), and separately requires
  REQ-EXT-09 / REQ-CL-04 to be re-anchored to non-self-referential totality evidence
  (`spec.md:182-185`). But both rows define the swept population as
  `collect_constraint_manifest` (`docs/architecture/verification-matrix.md:214,336`), that sweep is
  live in the tree (`extraction/extractor.py:98`, `extraction/constraint_report.py:3`),
  `modeling-assumptions.md:489-492` still names it the migration invariant's subject, and
  ELABORATE-FIRST Item 7 scope item 2 is deleting the dual constraint-fact extraction pass. So after
  this item the sweep is either a retired mechanism, a retained license-gated independent oracle, or
  an unowned second representation — and the spec does not say which. — contract invariants 40, 48;
  D-3 (owner-verbatim, for "no second catalog authority"); lens spec-F4 (agent/ratified) —
  disposition: state the sweep's fate in this item and re-word the two rows so the authored domain,
  not the sweep, defines the population. **Smells fired: #1 (two representations kept in sync) and
  #7 (ownership of the totality invariant moves silently)** — both inherited unresolved from
  umbrella spec-F4; they must appear in the stage's leading judgment, not sit in a rubric.

- spec-F4 [DO] **The usage-tier record's field list omits the definition QN and the
  definition-to-usage join.** The spec's form-classification requirement names source form, owner
  kind, owner qualified name, source file, source line (`spec.md:98-102`), while invariant 28 and
  LC-E05 require the catalog to carry "source form, usage name and QN, owner QN, **definition QN**,
  an explicit **definition-to-usage join**, and per-occurrence identity" —
  `contract:221-231`, `requirements:275-283` (agent/ratified). Today's per-occurrence tier already
  carries both (`resolution/models.py:397-401`, `:492-497`; `elaboration/graph.py:213`), so the new
  usage tier — which is the only carrier the 56 non-reaching usages ever get — would be the one
  place a definition-typed asserted gate loses the name of the `constraint def` that went
  unassessed. — disposition: add definition QN and the entry-level join to the domain-member field
  list, or state in the spec why a non-reaching member cannot carry them.

- spec-F5 [DO] **The unattachable halt's diagnostic is under-specified against invariant 9.** The
  spec says the halt is "a generation-halting error with a named diagnostic" (`spec.md:120-122`);
  invariant 9 requires it to fail "naming the usage **and the missing attachment**"
  (`contract:149-155`). The spec is precise about the *completeness gate's* diagnostic (identity plus
  qualified name, `spec.md:146-148`) and vague about this one. — disposition: carry invariant 9's
  wording into the severity requirement.

Not findings (checked, clean):

- No owner-graded statement is contradicted. D-1 holds (the completeness gate is a check, not a
  post-build mutation seam); D-2 is untouched; D-3 is carried forward verbatim in the
  single-authority requirement. The **[HARD]** SysML assert-only semantics and the `catf_mfe_d5`
  byte-reversal pin are both preserved, and the spec's Non-Goals keep the twins' constraint syntax
  frozen.
- The "still generates after this item" claim is sound: `catf_mfe_d5` contains no `assert` at all
  (verified by grep over `tests/fixtures/catf_mfe_d5/**/*.sysml`), so the halting path in
  requirement 3 of the point is unreachable for the frozen fixture.
- The open domain boundary (whether `RequirementUsage`/`satisfy` join the domain) does not
  destabilise the "exactly 65" success criterion for this fixture: `catf_mfe_d5` authors no
  `satisfy` or requirement usage (only a doc-comment mention in `library/components/vacuum.sysml:126`).
  The spec surfaces the boundary rather than resolving it, which is the capture-fidelity-correct move.
- Scope handoffs are honest, not narrowings: the zero-input aggregator and the report's coverage
  accounting are Item 3 scope items 1 and 4; calc-def gate execution is Item 6; the CATF disposition
  table is Item 5; the two named defects are Item 4. Invariant 61's denominator consequence is
  correctly split (mechanism here, coverage effect Item 3), and Appendix C's "Asserted vacuous gate"
  cell splits the same way.
- The circularity correction (umbrella spec-review L3-2) is carried faithfully, including the
  independent-oracle requirement that the gate's evidence cannot be the gate agreeing with itself.

Gate: DISPOSED (spec-F1..spec-F5) — no owner/[HARD] contradiction found, so nothing blocks. Two
smells (#1, #7) fired on spec-F3 and are inherited unresolved from the umbrella ledger's spec-F4;
they must be carried into this stage's leading judgment. spec-F1 and spec-F3 are the two that
change what design must decide.

**Spec-side disposition record (2026-08-12, same session):**
- spec-F1 → advisory home closed in the spec, not deferred: invariant 61 / LC-E13's authoring-
  validation-at-warning-grade is stated in the severity requirement, and the open question was
  narrowed to which surface emits it, not whether the ruling stands.
- spec-F2 → the owner sequencing requirement now names the documentation half and the two Item 1
  forward pointers (`modeling-assumptions.md:476-477` and `:489-496`) this landing falsifies.
- spec-F3 → new requirement: the manifest sweep gets an explicit fate — retired, or a test-side
  independent oracle no generation path consults; unowned second representation is refused. The
  retire-versus-oracle choice is design's.
- spec-F4 → usage-tier records now required to carry definition QN and the explicit
  definition-to-usage join, per invariant 28 / LC-E05.
- spec-F5 → the unattachable halt's diagnostic must name the usage and the missing attachment
  (invariant 9), matching the precision already demanded of the completeness diagnostic.

---

## design — 2026-08-12 — rev ccf4c21 (+ untracked `design.md` rev 2, `design-review.md`)

**Method note.** `~/.claude/scripts/product-lens.md` is unreadable from this session (as it was
from the design-review session, which is why that stage's gate was left NOT DISCHARGED). Rather
than skip the gate a second time, the method was **reconstructed from in-tree examples** — this
ledger's own spec-stage entry above, and the two other in-tree ledgers. Structure, grading
vocabulary, and the falsifier/findings/gate shape follow those; anything the real script requires
beyond them is not represented here. Flagging it so a later reader knows the provenance of the
format, not just of the judgment.

Epic: CONSTRAINT-SEMANTICS (Item 2)
Epic gate: CLEAR — carried unchanged from the spec-stage entry; grade preserved (point sourced to
`rulings-20260812.md`, **grade: owner**). No design decision narrowed or contradicted the point.

Point (re-derived from the sources, not from the design): unchanged from the spec-stage entry
above — items 1–4 and their grades carry forward verbatim. Re-derivation confirmed them against
contract invariants 1, 9, 28, 40, 48, 61; LC-E05/E06/E13; D-1 and D-3 **[OWNER-VERBATIM]**; and
the umbrella spec's Problem statement.

Falsifier (design stage): a design in which some authored usage can end a run with no disposition
or two; or in which totality rests on a second inventory a generation path consults; or in which
shipped documentation is corrected after the tests that confirm the behavior.

Findings:

- design-F1 [DO] **An asserted usage whose classification raises leaves the whole model with no
  carriers — point 1 fails at exactly the moment it matters most.** Rev 1's invariant 5 made
  minting non-raising for non-asserted forms only, and let asserted forms "raise as they do today."
  But the two raises in question — `SI_REDEFINITION_INVALID` (`elaborate.py:1166-1175`) and the
  definition-identity disagreement (`:1149-1163`) — abort elaboration model-wide. Under rev 1 a
  single malformed asserted non-reaching gate would mean *no* usage in that model carries a
  disposition, which is the absence-not-disposition failure this whole item exists to end. It is
  also the wrong diagnostic against point 3: invariant 9's halt names the usage and the missing
  attachment; a bare invariant error names neither. — contract invariants 1, 9, 28; point items 1
  and 3 — disposition: **applied in rev 2.** Invariant 5 now reads "minting never raises, for any
  form"; an asserted non-reaching usage whose classification cannot complete gets a
  `classification_incomplete` disposition at error grade, and the completeness gate halts with a
  named diagnostic. The halt is preserved; what changes is that it arrives per-usage, with every
  other usage still carrying its carrier. B3's "if false" and the Potential Risks residual were
  re-pointed at the new mechanism.

- design-F2 [DO] **`owner_kind_unattachable` collapses `calc_def` and `requirement_def`, and
  shipped documentation already distinguishes them.** Point 3 says the halt is for an asserted
  usage *in executable scope* with no attachment capability. `docs/architecture/modeling-assumptions.md:473-474`
  is more specific and is already shipped: an out-of-profile owner such as a `requirement_def`
  "draws a named visible exclusion rather than an unreachable-assert error." Rev 1's table listed
  `requirement_def` inside `owner_kind_unattachable`, whose severity is `error` for an asserted
  form — so an `assert` authored inside a requirement def would halt where the shipped doc promises
  a visible exclusion. Reachability is narrow (such a usage is usually `requirement_constraint`
  form, hence non-asserted and `info`), but the rule as written contradicts a shipped statement,
  and this item's own falsifier includes shipped docs describing something other than the behavior.
  — contract invariant 9; point item 3; `modeling-assumptions.md:473-474` — disposition: **applied
  in rev 2.** `requirement_def` moved to a step-1 form/owner exclusion with its own token
  `out_of_profile_owner` at `info`, never `error`; `owner_kind_unattachable` narrowed to owner
  kinds *in executable scope* (`calc_def` today). The distinction and its source are stated in
  prose beneath the table.

- design-F3 [DO] **"Recapture runs last" collides with the confirmation tests that need its
  bytes.** Point 4's owner-graded rule is that documentation and expected outputs are corrected and
  captured *before* confirmation tests run. Rev 1's landing order said the single reviewed
  recapture "runs last within this repo," while Validation Approach requires three-route parity and
  fail-closed tests that cannot execute without v3 snapshot bytes. Left as written, an implementer
  resolves it either by running the recapture earlier (paying a second recapture, which the Item 7
  register forbids) or by reverse-engineering expectations from whatever the recapture produced —
  which is precisely the circular confirmation the owner's sequencing rule exists to prevent. —
  point item 4 **[OWNER]** "Documentation and the derivative's expected outputs are corrected and
  captured before confirmation tests run"; `epic_elaborate_first_architecture.md` Item 7 scope 3 —
  disposition: **applied in rev 2.** The recapture is restated as the last *fixture-committing*
  step, not the last step overall: development-time parity tests capture to a temp directory, the
  committed-fixture forms run after the reviewed recapture, and both violation directions are named
  in the landing order.

Not findings (checked, clean):

- **Smell #1 (two representations kept in sync) — cleared at this stage.** It fired at spec stage
  on spec-F3 and was inherited unresolved from the umbrella ledger's spec-F4. D7 retires
  `collect_constraint_manifest` outright, so no second representation survives in `src/`. The
  expectation files are test-side, read by no generation path, which is the latitude the spec
  granted explicitly; the scanner's missing-file failure rule is what keeps their hand-maintenance
  from silently decaying.
- **Smell #7 (ownership of the totality invariant moves silently) — cleared at this stage.** The
  design names elaboration as the owner of dispositions in three places (Core Concept, Architecture
  boundaries, D3) and states that nothing downstream re-derives one. The move is deliberate and
  written down, which is the opposite of silent.
- D-1 holds: the completeness gate is a check that refuses, never a post-build mutation seam
  ("the preflight reads and refuses, it never repairs"). D-3 is carried into D1's rejected
  alternatives verbatim in substance.
- Point 1's "exactly one" is structural after F3's precedence rule, not merely asserted: the
  ordered stop-at-first-match evaluation cannot produce two, and invariant 2 checks it in
  `graph.validate()`, which runs on the live route, both decode paths, and the sealed context.
- The **[HARD]** `catf_mfe_d5` byte-reversal pin is preserved — B5 restates the 65/9 outcome and the
  design changes no authored constraint syntax. The **[HARD]** identity row is now honored further
  than the spec required: design-review F1's fix carries `DeclarationId` into the catalog tier, so
  no join step anywhere uses a qualified-name string.
- Point 4's documentation half is discharged concretely, not gestured at: five line-anchored edits,
  ordered before confirmation tests, with D6's evidence pointer explicitly landing before the sweep
  it cites is deleted.
- Scope handoffs remain honest: Item 3 gets a named token section and provably needs no usage-tier
  schema change; Item 5, 6, and 4 boundaries are unchanged from the spec.

Gate: **DISPOSED** (design-F1..design-F3) — no owner-graded or **[HARD]** statement is contradicted
by the design, so nothing blocks. All three findings were applied in rev 2 rather than deferred.
design-F1 is the one that changes behavior; design-F2 and design-F3 are precision corrections
against shipped statements and against the owner's sequencing rule.

**Design-side disposition record (2026-08-12, same session):**
- design-F1 → invariant 5 widened to "minting never raises, for any form"; new
  `classification_incomplete` reason token at error grade; halt preserved, now per-usage and named.
- design-F2 → `requirement_def` split out as a step-1 `out_of_profile_owner` exclusion at `info`;
  `owner_kind_unattachable` narrowed to executable-scope owner kinds.
- design-F3 → recapture restated as the last fixture-committing step, with temp-directory capture
  for development-time parity tests and both violation directions named.
