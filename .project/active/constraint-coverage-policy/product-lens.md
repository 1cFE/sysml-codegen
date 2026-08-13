# Product-lens ledger — constraint-coverage-policy (CONSTRAINT-SEMANTICS Item 3)

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they amend.

---

## spec — 2026-08-12 — rev ec1ae2a (+ untracked `.project/active/constraint-coverage-policy/spec.md`)
Epic: CONSTRAINT-SEMANTICS, Item 3 (Coverage Report and TEAx Policy)

**Runner note:** `/home/reid/.claude/scripts/product-lens.md` and its pack source are outside this session's sandbox and could not be read. The §3 ledger format was recovered from the sibling ledgers `.project/active/constraint-semantics-contract/product-lens.md` and `.project/active/constraint-semantics-contract-amendments/product-lens.md` and followed. `/home/reid/1cfe/teax` is also unreadable here, so no TEAx-side claim in the WORK was verified against that repository.

**Point** (re-derived from SOURCES; the WORK was opened only after the sources were read):

1. Item 1 already fixed what every headline state *means*; Item 3 owns spellings, schema, and seam code only, and may not re-decide a meaning. [source: contract "Headline states and coverage truth" preamble, ADR-009 **Scope**; grade: agent/ratified]
2. No report or study label may claim more coverage than was assessed. Full satisfaction is a coverage claim over applicable **asserted** gates; inventory totality and feasibility coverage stay two separate totals. [source: invariants 32, 33, 61; LC-E10/E11/E12/E13; refinements L2-1/L2-2; grade: agent/ratified]
3. Coverage truth has exactly one authority — the embedded catalog — derived in one direction, never a second inventory, and TEAx consumes it with no adapter and no re-derivation of constraint context. [source: invariant 48, 40; LC-G07 (owner-sourced NEED); **D-3 owner-verbatim** "100% Option A. We need to purge this mess."]
4. Every state has a counterpart in both vocabularies across one seam; an unknown or unmapped headline fails closed with a named error, never a `KeyError` and never a fallthrough to satisfied or unconstrained. [source: invariant 46a, contract "Both vocabularies"; umbrella `[HARD]` L1-1]
5. Policy reads evidence, never writes it; partial coverage keeps for boundary, feed-strategy only by explicit auditable per-study opt-in, coverage lands in durable case records either way, and study identity is never silently reassigned across a catalog/report schema move. [source: invariants 41, 49, 50; Q6; grade: agent/ratified]

**Falsifier:** a run in which a constraint-bearing model still emits no report (or reads `unconstrained`/`not_assessed`) while it carries an applicable asserted gate; or coverage counts computed from anything other than the catalog; or a state that exists in one vocabulary with no counterpart; or an existing study store silently rebound across the report/catalog schema move.

### Findings

- **item3-F1 [DO] — the report-required trigger is published for only one of its two branches, and the missing branch is the one Appendix C names twice.** The spec's aggregator requirement reads "A constraint-bearing model with **no applicable asserted gate** still requires the zero-input aggregator and a not-assessed report" (`constraint-coverage-policy/spec.md:126-128`), and Success Criterion 3 pins only the descriptive-only shape (`:71-72`). The other zero-entry shape — applicable asserted gates present, **zero eligible concrete entries** — also produces no evidence inputs and so also needs a zero-input aggregator, but reads *partial coverage*. The contract states it three times: Appendix C "Excluded-only usages" ("a partial-coverage surface when any excluded usage is asserted", `constraint-execution-authoritative-lifecycle-contract.md:792`), Appendix C "Asserted vacuous gate" ("generation does not halt, and the report headline reads partial coverage", `:793`), and LC-E12 amended (`constraint-execution-lifecycle-requirements.md:326-333`). The spec's own `[INFERRED]` supersession of `ships_constraint_machinery` says the replacement "must be the invariant-32 trigger" (`:131-135`) but never states what that trigger *is* — and both candidate readings on the page (Item 2's "≥1 concrete entry" and the spec's "no applicable asserted gate") leave an asserted-vacuous-only model with no aggregator at all. That model is Item 5's post-migration CATF shape: today all 65 usages are bare `constraint`, and 5 of them are `owner_has_no_occurrences` (`constraint-catalog-totality/verification.md:19-28`). — source: invariants 32, 61; Appendix C:792-793; LC-E12 (agent/ratified) — **disposition:** state the report-required trigger once, positively (a report is required whenever the model authors any constraint usage), and add a success criterion pinning asserted-gates-with-zero-eligible-entries → zero-input aggregator → **partial**, distinct from the descriptive-only → not-assessed criterion.

- **item3-F2 [DO] — the inherited "BLOCK stays in the denominator" clause is unreachable under invariant 1, and the spec carries both without noticing.** Known Requirements reproduce the contract's form-not-predicate test verbatim: "an asserted usage whose predicate is `BLOCK`ed or classified `NON_NUMERICAL` stays in the denominator as an unassessed gate" (`spec.md:106-109`). Invariant 1 as amended by Item 1 says "A `BLOCK` on an **asserted** usage halts the model" (`constraint-execution-authoritative-lifecycle-contract.md:130-135`), and Appendix C's "ADMIT + NON_NUMERICAL + BLOCK mix" cell says "one halt before mutation" (`:794`). A halted model generates no package and no report, so the BLOCK half of that requirement can never be exercised; only the `NON_NUMERICAL` half is live. The spec's Non-Goals separately keep "Changing BLOCK-halts-generation semantics" (`:191`), so it holds both sides without reconciling them. An implementing agent reading this page will write a fixture for "asserted + BLOCKed predicate → partial coverage" that cannot be generated. — source: contract invariant 1 (amended) vs "Headline states and coverage truth":439-445 (both agent/ratified) — **disposition:** surface it, do not resolve it (capture-fidelity law 4). Move it into "Surfaced, not resolved" alongside the epic scope-4 note, and scope the live requirement to `NON_NUMERICAL` until Item 1's authority rules on whether the BLOCK clause is dead text or invariant 1 is narrower than written.

- **item3-F3 [DO] — the all-inapplicable edge has two published answers and Item 3 writes the code that picks one.** Appendix C's "Asserted vacuous gate" cell says a usage carrying an explicit inapplicability disposition "drops out of the feasibility denominator and the headline reads **full satisfaction** when every remaining gate passed" (`:793`). State 5 says "the model has constraint usages but **no applicable asserted gate at all**" reads **not assessed** (`:459-460`). A model whose only asserted gates are all dispositioned inapplicable satisfies both: zero remaining gates all vacuously passed, and zero applicable asserted gates. The spec reproduces the inapplicability rule (`spec.md:111-115`) and the state list (`:100-105`) without noticing they cross, and its Open Questions do not list this. Item 3 implements the precedence function, so it will decide by accident. — source: contract Appendix C:793 vs states 5/precedence:459-464; invariant 61 (agent/ratified) — **disposition:** add it to "Surfaced, not resolved" or to Open Questions with the two readings named, so design rules it explicitly rather than in code.

- **item3-F4 [DO] — the migration question stops at generated packages and never reaches the study stores the item is about to change.** Success Criterion 5 requires coverage counts and catalog linkage to persist "in durable case records" on both policy paths (`spec.md:76-78`), and the open question covers "already-generated packages and captured baselines" for the `ConstraintReport` and package-contract version bump (`:207-208`). Neither names existing durable study stores, whose records were written against catalog `2.x` and a report with no coverage block. Invariant 50 requires an explicit transition — a migration proving old and new artifact equivalence, or the old store archived as lineage with a new store begun — and states "Identity is never silently reassigned" (`:301-305`); LC-G07A mirrors it (`constraint-execution-lifecycle-requirements.md:408-410`). With TEAx also re-vendoring `ACCEPTED_CATALOG_SCHEMA_VERSIONS` to `3.0.0` in this item, resume/query across the boundary is exactly the case invariant 50 governs. — source: invariants 48, 50; LC-G07A (agent/ratified) — **disposition:** extend the migration open question to durable study stores and name invariant 50's two permitted routes, so design cannot land a silent rebind.

- **item3-F5 [DO] — invariant 41 is cited for its read-only half and dropped for its enforcement half, over a surface this item is adding.** The study requirement carries "Policy consumes evidence read-only. It cannot mutate status, margin, observations, identity, or catalog linkage" (`spec.md:158-159`). Invariant 41's full text adds the mechanism and a live defect: "enforce this by deep freeze or defensive isolation. **Current nested models violate it**" (`:269-271`). This item adds a nested coverage block (counts plus a reason histogram) to `ConstraintReport` — new nested mutable surface on exactly the models the contract records as already violating the rule. The spec neither carries the enforcement obligation nor declares it out of scope, and Appendix C's "Nested evidence mutation attempt" cell (`:824`) has no counterpart in the success criteria. — source: invariant 41; Appendix C:824 (agent/ratified) — **disposition:** either state that the new coverage block is frozen/isolated to the same standard, or record the pre-existing violation as explicitly out of scope so the new fields are not quietly enrolled in it.

- **item3-F6 [DO, low] — the load-bearing half of invariant 32 is paraphrased away.** The spec cites invariant 32 for the zero-input aggregator but drops its first clause: "the aggregator is structurally retained as an exit ancestor whenever a constraint report is required" (`:232-235`; LC-E10 repeats it, `constraint-execution-lifecycle-requirements.md:305-310`). Retention is what the *zero-input* case actually needs — an aggregator with no inputs is exactly the node ordinary reachability pruning drops, so "generate it" without "retain it as an exit ancestor" is half the obligation. — source: invariant 32; LC-E10 (agent/ratified) — **disposition:** one clause added to the existing requirement; no new section.

**Not findings (checked, clean):**
- No owner-graded statement is contradicted. D-1 (no post-build seam), D-2 (direct design-attribute actuals), and **D-3** (canonical embedded catalog, no consumer materializer) are untouched; the spec's one-direction derivation requirement (`:123-125`) is the correct D-3/invariant-48 posture and repeats no second inventory.
- The `[OWNER-VERBATIM]` design-search quote (`:51-53`) reproduces `rulings-20260812.md:13-15` exactly, at the owner's emphasis, and is carried as the governing obligation rather than paraphrased.
- The owner-directed sequence is graded `[NEED]` (`:180-183`), the correct concept→spec absorb mapping for the rulings' `[OWNER]` grade, and it explicitly forbids reverse-engineering expectations from current behavior — the strongest single line in the spec, and pointed at the right risk.
- Q6's default dispositions are reproduced exactly against the umbrella (`spec.md:151-157` vs `constraint-semantics-contract/spec.md:238-243`), including the auditable-opt-in and the record-regardless clause.
- Invariant 61 / LC-E13 (asserted vacuous gates) are carried even though the epic's Item 3 Required Reading predates them and omits both — the spec caught the gap on its own.
- The epic scope-4 vs LC-E10 divergence is surfaced under law 4, not silently reconciled (`:218-224`), and the second-hand TEAx citations are flagged as needing re-grep before reliance (`:225-230`).
- The Item 1 audit M-1 hand-off (four `all_satisfied` assertions in `tests/execution/`) is carried into Success Criteria as an eighth criterion rather than lost between items.
- The `ships_constraint_machinery` supersession is marked `[INFERRED]`, attributed to the docstring that anticipated it, and required to stay in one place — no second rule, no silent drift.

**Gate: DISPOSED (item3-F1..item3-F6)** — nothing blocks. No owner-grade statement and no Item 1 ruling is contradicted; the spec's provenance discipline is clean throughout. **item3-F1 is the one to fix in the spec text**, because it is a missing obligation rather than an under-specified one: as written, the item can ship with the asserted-but-zero-eligible model still emitting no report, which is the epic's own Current-State defect surviving the item that exists to remove it. F2 and F3 are surfacing obligations (two published rules that cross), and both belong in "Surfaced, not resolved" before design, not in design's judgment. F4 and F5 are contract clauses cited by number but carried by half. The recurring shape across F1, F5, and F6 is the same: an invariant is cited for the clause the spec needed and trimmed of the clause that makes it enforceable — quoting the invariants whole would close all three.

---

### Spec-side disposition record (2026-08-12, same session)

- **item3-F1 → fixed in spec.** The report-required trigger is now stated once and positively ("a
  report is required whenever the model authors any constraint usage at all"), with both zero-input
  branches named and their differing headlines. A new success criterion pins
  asserted-gates-with-zero-eligible-entries → zero-input aggregator → partial coverage, separate from
  the descriptive-only → not-assessed criterion. The `ships_constraint_machinery` supersession now
  points at that stated trigger instead of at an unstated one.
- **item3-F2 → accepted in substance, corrected in detail.** The finding's premise is one step too
  strong: `SI_CONSTRAINT_BLOCKED` is raised inside the scope loop (`elaborate.py:1018-1029`), so an
  asserted `BLOCK`ed usage halts only when it expands to at least one scope. A `BLOCK`ed asserted
  usage that reaches no instance catalogs `non_reaching` and does stay in the denominator — Item 2's
  design says so explicitly. So the clause is live for the non-reaching case and dead for the
  expanded case, which is a reconcilable reading rather than a crossed rule. Recorded that way in the
  requirement itself, with the warning that a fixture for "asserted + BLOCKed + reaches an instance →
  partial" cannot be generated. Not moved to "Surfaced, not resolved", because nothing is left
  unresolved once the two cases are separated.
- **item3-F3 → surfaced, not resolved.** Added to "Surfaced, not resolved" with both readings and
  their sources named, and with the observation that Item 3 writes the precedence function and will
  otherwise pick one by accident. Both readings are agent-grade Item 1 text; this spec does not
  choose.
- **item3-F4 → fixed in spec.** Invariant 50 / LC-G07A now appears as an `[INHERITED]` requirement
  naming its two permitted routes for existing durable study stores, and the schema-migration open
  question explicitly extends to those stores.
- **item3-F5 → fixed in spec.** An `[INFERRED]` requirement states the new nested coverage block is
  frozen or defensively isolated to invariant 41's standard, and that fixing the pre-existing
  nested-model violation elsewhere is out of scope — so the new fields are not quietly enrolled in
  it.
- **item3-F6 → fixed in spec.** Invariant 32's exit-ancestor retention clause is carried as its own
  requirement line beside the zero-input trigger.

---

## design — 2026-08-12 — rev 01c4b34 (+ untracked `.project/active/constraint-coverage-policy/design.md`)
Epic: CONSTRAINT-SEMANTICS, Item 3 (Coverage Report and TEAx Policy)

**Runner note / provenance flag:** `/home/reid/.claude/scripts/product-lens.md` and its pack source
are outside this session's sandbox and could not be read. The ledger format is reconstructed from
this file's spec-stage entry and from `.project/active/constraint-catalog-totality/product-lens.md`,
per this epic's convention. **Unlike the spec stage, `/home/reid/1cfe/teax` was readable this stage**
(read-only, at clean `main` `fa0e06a`), so every TEAx-side claim below was verified first-hand.

**Point:** re-derived from SOURCES; all five items recorded at the spec stage still hold unchanged
and are not restated here.

**Falsifier** (unchanged): a run in which a constraint-bearing model still emits no report (or reads
`unconstrained`/`not_assessed`) while it carries an applicable asserted gate; or coverage counts
computed from anything other than the catalog; or a state that exists in one vocabulary with no
counterpart; or an existing study store silently rebound across the report/catalog schema move.

### Findings

- **design-F1 [DONE, resolved inside the design] — the `expects_report` authority was about to be
  silently invalidated, and it is invisible from the codegen repo.** TEAx derives
  `expects_report = bool(load_model_contract(...).concrete_entries)` (`study/cli.py:42`), documented
  as "empty iff constraint-free" (`evaluation/projection.py:44-46`). Design decision D5 makes a
  constraint-bearing package with **zero** concrete entries ship a report, at which point that
  derivation tells the projection seam not to expect one — silently disabling the invariant-46a
  corruption check (`projection.py:50-55`) for exactly the packages this item teaches to emit a
  zero-input report. The spec could not have caught it: it flagged the TEAx surfaces as second-hand
  and this line is not among the four it cites. — source: invariant 46a; contract "Headline states
  and coverage truth" (agent/ratified) — **disposition:** owned by design D7 — the authority moves to
  `usage_records`, the same population as the report-required trigger, so the two cannot disagree.

- **design-F2 [FILED — Item 1 territory, not performed here] — Appendix C's vacuous-gate cell
  over-permits in the degenerate case.** The cell reads "…drops out of the feasibility denominator
  and the headline reads full satisfaction **when every remaining gate passed**"
  (`constraint-execution-authoritative-lifecycle-contract.md:793`). The conditional presupposes
  surviving gates; read literally it also licenses `full_satisfaction` for a model with none, which
  crosses state 5 (`:459-460`). — source: Appendix C:793 vs states 5/precedence:459-464 (both
  agent/ratified) — **disposition:** design D4 publishes a RULING (**not assessed**) with its
  reasoning against the contract, as the spec's surfaced item required. The cell wants "…and at
  least one gate remains" added; recorded for close, not edited by this item.

- **design-F3 [ACCEPTED, recorded] — the epic's scope-4 wording remains looser than the amended
  contract.** Design D5 follows LC-E10 (the trigger is any authored constraint usage; an applicable
  gate with zero eligible entries reads partial coverage), which is what the spec already surfaced.
  Nothing new to resolve. — **disposition:** no design change; the epic text still wants the same
  correction at close.

**Not findings (checked, clean):**
- No owner-graded statement is contradicted. D-1 (no post-build seam), D-2 (direct design-attribute
  actuals), and **D-3** (canonical embedded catalog, no consumer materializer) are untouched; design
  D3 derives coverage from the sealed catalog in one direction and adds no second inventory and no
  consumer-side reconstruction.
- The `[OWNER-VERBATIM]` design-search quote is carried whole in **The Point**, at the owner's
  emphasis, as the governing obligation — not reduced to a pointer at the spec.
- The `[NEED]` owner sequencing instruction is honoured explicitly in D8 step 1, including the
  prohibition on reverse-engineering the `test_fusion_tea_real_teax.py:244-259` expectation from
  observed behaviour, and it is named again in Next-Stage Handoff as one of the two de-risk-first
  items.
- Q6's default dispositions are reproduced exactly in D7, including keep-for-boundary as the default,
  the auditable per-study opt-in, and coverage landing in durable case records on both paths.
- Invariants carried **whole**, not to the needed clause: 32 (zero-input aggregator *and*
  exit-ancestor retention — the retention half verified already mechanized at
  `generation/pipeline.py:284-296`), 41 (read-only *and* the deep-freeze enforcement, verified
  already covered by `evidence.py:17-28`), 48, 49, 50, 61.
- Invariant 50 is resolved by **verified fact rather than assumption**: no durable study store with
  results worth keeping exists (the only two `study.db` files are archived spike work dirs under
  `.project/completed/20260713_constraint-study-integration-spike/_work/`), and TEAx's eight-field
  compatibility binding (`study/compatibility.py`, `study/store.py:147-151`) already implements the
  archive-and-begin route. The additive-or-versioned constraint holds and **no owner-visible
  surfacing is required** — the spec's escape hatch was checked and not needed.
- The spec's own open question "does a durable study store with results worth keeping exist yet?" is
  answered **no**, so the item is not undersized on that account (review L2-2 discharged).
- Every second-hand TEAx line number the spec flagged was re-grepped; the one wrong cite
  (`CANONICAL_HEADLINE` is defined in `evaluation/evidence.py:44`, not `projection.py`) is corrected
  in Research Findings, and one surface the spec did not know about (two policy dispatch tables, not
  one) is carried into D7. As the spec predicted, the cost was a re-grep and no requirement moved.
- The four `all_satisfied` assertions are carried into D8's landing order with the fourth's
  hand-written-first obligation stated separately from the three bare ones.

**Gate: DISPOSED (design-F1..design-F3)** — nothing blocks. The one finding that changes the build,
design-F1, is a premise the spec could not see from its sandbox and is resolved inside D7; the other
two are records for close. The design's own weak point is not a lens finding but a bet: B1 (the
catalog's per-usage dispositions are correct) is unfalsifiable from inside this item, and the
mitigation — hand-written expected accounts per fixture rather than generated ones — is the same
discipline the owner's sequencing instruction already demands.

---

## design_review — 2026-08-12 — rev 328032e (codegen) / fa0e06a (TEAx, read-only)
Epic: CONSTRAINT-SEMANTICS, Item 3 (Coverage Report and TEAx Policy). This is the
**design-review-stage** entry; it does not replace the design-stage entry above.

**Runner note:** unlike both prior entries, `/home/reid/.claude/scripts/product-lens.md` was **read
directly this session** — the §1 oracle-first protocol, the §2 grade table, this §3 format, and the
§4 smell list are the spec's own text, not a reconstruction. `/home/reid/1cfe/teax` was readable
(read-only, clean `fa0e06a`); every TEAx line cited below was opened first-hand this session, as was
every codegen line.

**Point** (re-derived from SOURCES before the WORK was opened; consistent with the prior two entries,
restated in the form this stage tested):

1. A design search must be able to tell a candidate that passed its physics gates from one nobody
   checked — so no report and no study label may claim more coverage than was assessed. [source:
   `.project/active/constraint-semantics-contract/spec.md:17` **[OWNER-VERBATIM]**; grade: owner]
2. Full satisfaction is a coverage claim over **applicable asserted gates**; inventory totality and
   feasibility coverage stay two totals. [source: contract "Headline states and coverage truth",
   invariants 32/33/61, ADR-009, LC-E10/E11/E12/E13; grade: agent/ratified]
3. Coverage truth has exactly one authority — the embedded catalog — derived in one direction, with
   TEAx consuming it directly and reconstructing nothing. [source: invariant 48; **D-3
   [OWNER-VERBATIM]** "100% Option A. We need to purge this mess."; grade: owner for the no-second-
   catalog rule, agent/ratified for the derivation direction]
4. Every state has a counterpart in both vocabularies across one seam; an unknown or unmapped
   headline fails closed with a named error. [source: invariant 46a; umbrella `[HARD]` L1-1]
5. Policy reads evidence, never writes it; partial coverage keeps for boundary; coverage reaches
   durable case records on both paths; study identity is never silently reassigned. [source:
   invariants 41/49/50, Q6; grade: agent/ratified]

**Falsifier** (design-stage form): the design would show a constraint-bearing model still emitting no
report; a coverage number sourced from anything but the sealed catalog; a state present in one
vocabulary only; a report-required or report-expected predicate that two components can answer
differently; or a durable store rebound without a stated route.

### Findings

- **design_review-F1 [DO] — the report-expected predicate has two live derivations in TEAx and D7
  moves only one.** `evaluator.py:79-87` (`_report_declared_in_spec`) is the default `expects_report`
  for **both** `PreparedEvaluator` and `FileBackedEvaluator` (`evaluator.py:139-143`, `:243-246`); its
  own docstring states the coupling — "The study layer overrides this with the catalog authority; the
  two must agree." D7 moves the catalog-side authority (`study/cli.py:42`) from `concrete_entries` to
  `usage_records` and never names the spec-side default, so the design changes one half of a stated
  two-way agreement and leaves the other unexamined. It happens to stay true — the report channel is
  pinned as an exit output for every minted aggregator (`generation/pipeline.py:284-296`), so a
  zero-input aggregator does appear in the spec — but that is now load-bearing and unstated, over the
  exact check (invariant 46a corruption detection, `projection.py:50-55`) that design-F1 was raised to
  keep alive. The design closes the same hazard *inside* codegen with a preflight (D5, "Two readings of
  one rule is the drift A4 exists to stop") and does not apply that standard across the repo boundary.
  — source: invariant 46a; Item 2's A4 one-rule cure carried in the spec (agent/ratified) —
  **disposition:** DISPOSE — D7 names `evaluator.py:79-87`, states why the spec-declared report
  channel and non-empty `usage_records` agree, and pins the agreement with a test on a zero-input
  package; or the producer states the answer once in the model contract and both TEAx sites read it.

- **design_review-F2 [DO, low] — the unassessed-reason histogram is specified as a token list, where
  the obligation is a rule, and the list is 7 of the landed 9.** D2 keys `unassessed_reasons` by seven
  tokens. The landed closed vocabulary (`elaboration/graph.py:258-278`) has nine: D2 omits
  `out_of_scope_satisfy` and `out_of_profile_owner`. Both omissions are *correct* — they fire for
  satisfy references and `requirement_def`-owned usages (`elaborate.py:1253-1265`), which the contract
  says are never applicable asserted gates — but the design gives the list without the criterion, and
  the criterion is the two-totals rule this item exists to implement. An implementer comparing D2
  against the enum sees two missing buckets and no way to tell oversight from exclusion; Required
  Invariant 2's `sum(unassessed_reasons) == unassessed_gate_count` validator is what breaks if the call
  goes the other way. — source: contract "Headline states and coverage truth", two-totals paragraph;
  invariant 33 (agent/ratified) — **disposition:** DISPOSE — state denominator membership as a rule
  over the landed vocabulary (which reasons are inside the feasibility denominator and which are
  inventory-only), and derive the histogram keys from it.

- **design_review-F3 [DO, low] — invariant 46's persist/harvest clause is carried by mechanism and
  pinned by nothing.** The contract requires the file-backed route to carry the coverage accounting
  through persistence and harvest unchanged, with no consumer schema adapter. Verified this session
  that the mechanism gives it for free: `FileBackedEvaluator` shares the same `project(...)`
  (`evaluator.py:270`) and `encode_evidence` passes the sealed report tree whole
  (`study/evidence_io.py:49-56`). But neither the Component Overview nor any of the twelve Validation
  Approach items names the file-backed route or a persist-then-harvest round-trip of `coverage` — the
  design's TEAx-side evidence is entirely `PreparedEvaluator`-shaped. — source: invariants 45 and 46
  (agent/ratified) — **disposition:** DISPOSE — add the round-trip to Validation, or state that the
  existing prepared/file-backed parity test already covers the new block and cite it.

### Smells (§4, design pair)

- **Smell 2 — a consumer compensates for something the producer guarantees: FIRES**, on
  design_review-F1. "Does this package ship a constraint report" is a producer rule: codegen decides it
  in `ships_constraint_machinery` (`resolution/models.py:643-656`, D5) and mints the aggregator
  accordingly. TEAx answers the same question twice more, independently — once from the pipeline spec
  and once from catalog rows — and the design's own design-F1 is the record of that duplication
  already going wrong once. D7 repairs the instance by re-syncing a copy rather than by removing the
  duplication, and adds a third consumer-side check in the same shape (D3 point 3, the report/contract
  fingerprint comparison, which inside one sealed and seal-verified package can only fail on a codegen
  defect). **Escalation:** the review's leading judgment should ask whether the model contract states
  `ships_constraint_report` once as a producer fact. Grade agent/ratified (invariant 48, Item 2's A4
  cure) — a real finding, not a BLOCK: D-3's owner-verbatim prohibition is on QN/predicate-text
  reconstruction and a consumer materializer, and reading a row count is direct consumption, so
  stretching D-3 to owner-grade here would be manufactured authority.
- **Smell 7 — the solution changes who owns an invariant without saying so: DOES NOT FIRE.** Three
  ownership moves are in this design and all three are stated in the open: coverage truth moves from a
  runtime observation to a generation-time constant (Core Concept, D3, and **B2 states it as a
  falsifiable bet with its failure mode**); the report-expected authority moves from `concrete_entries`
  to `usage_records` (D7, and the design raised it as its own finding); and `ships_constraint_machinery`
  changes what it says while D5 explicitly preserves where it lives. Nothing here relocates an
  invariant quietly.

**Not findings (checked first-hand, clean):**
- **No owner-graded statement is contradicted.** D-1 — the account is baked at generation, so no
  post-build or late-fill mutation seam is added. D-2 — untouched. D-3 — the compact account is a
  summary the contract itself mandates (invariant 46, "the exact report carries compact coverage
  accounting derived from the catalog"), derived one-directionally, addressed back to the catalog by
  fingerprint, carrying no per-usage rows; no second inventory and no consumer materializer.
- The `[OWNER-VERBATIM]` design-search quote is carried whole in **The Point**, at the owner's
  emphasis, as the governing obligation. The `[NEED]` sequencing instruction is honoured in D8 step 1
  (fusion expectation hand-written before the run), and the `[NEED]` TEAx-branch-only instruction is
  honoured with the publication/checkout distinction stated rather than assumed.
- **A hazard the two-tier rule could have hidden does not exist.** A usage-tier `assessed_gate_count`
  would be wrong if one usage could have both eligible and excluded occurrences. It cannot:
  `project.py:1093-1114` branches on `node.eligibility`, which is one profile decision per usage
  (invariant 1), so occurrence-tier exclusions never hide inside an "assessed" usage.
- **B1's inputs are landed, verified field by field**: `ConstraintCatalogUsageRecord`
  (`resolution/models.py:476-521`) carries `declaration_id`, `source_form`, `membership_kind`,
  `disposition_kind`/`_reason`/`_severity`, `inapplicability_reason`, `occurrence_count`. One cite
  drift for the plan, not a finding: D2/D4 speak of reading `inapplicability is not None`; the landed
  field is `inapplicability_reason`.
- **D8's landing order rests on a verified fact.** TEAx pins
  `ACCEPTED_CATALOG_SCHEMA_VERSIONS = frozenset({"2.0.0"})` (`evaluation/package_load.py:39`) while
  codegen ships `CATALOG_SCHEMA_VERSION = "3.0.0"` (`contracts/versions.py:18`), so the fail-closed
  window is genuinely already open and codegen-first is safe as claimed.
- **D8's "the verifier hash does not move" is consistent with the rule it could have broken.**
  `versions.py:43-47` binds bytes to version in one direction — a `verify.py` byte change forces a
  version bump — not the converse, so bumping `RUNTIME_CONTRACT_VERSION` with unchanged verifier bytes
  breaks nothing. `RUNTIME_CONTRACT_VERSION` is marked "Owner-overridable; this is the initial token",
  i.e. agent-grade, so the bump contradicts no owner decision.
- D4's ruling stays inside this item's mandate: it publishes reasoning against the contract, files the
  Appendix C amendment to Item 1 rather than performing it, and its added non-vacuity condition
  (`assessed_gate_count > 0`) is the reading the governing obligation forces.
- D1's token map is a bijection over five states plus report-absent, satisfying invariant 46a's
  counterpart requirement in both directions, with fail-closed on each side by a different mechanism
  (pydantic `Literal` on the report side, `UnknownHeadlineToken` on the runtime side).

**Gate: DISPOSED (design_review-F1..design_review-F3)** — nothing blocks. No owner-graded statement is
contradicted and no Item 1 ruling is overturned, so no finding reaches BLOCK grade. F1 is the one that
should change the artifact: it is the same class of defect as the design's own design-F1, one layer
out, and the design's in-repo standard for it (make the agreement a check, not a convention) is the
standard to apply. F2 and F3 are precision gaps that cost a sentence each. The design's real exposure
remains B1, which no lens finding can reach from inside this item; the hand-written-expected-accounts
mitigation is the right one and is the owner's sequencing instruction applied.
