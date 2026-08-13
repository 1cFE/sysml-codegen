# Product-lens ledger — catf-constraint-policy-acceptance (CONSTRAINT-SEMANTICS Item 5)

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they amend.

---

## spec — 2026-08-13 — rev 2927dbb (+ untracked `.project/active/catf-constraint-policy-acceptance/spec.md`)
Epic: CONSTRAINT-SEMANTICS (`epic_constraint_semantics_contract.md`, Item 5 — CATF Derivative and
End-to-End Acceptance)

**Runner note:** `~/.claude/scripts/product-lens.md` and its pack source
(`/home/reid/agentic-project-init/claude-pack/scripts/product-lens.md`) are outside this session's
sandbox and were refused on every read route, so the lens was run from its stated purpose — an
independent two-direction check (does the WORK contradict or narrow the product point; does it omit
an obligation the point requires) — in the ledger format used by the sibling ledgers
`.project/completed/20260813_constraint-predicate-hardening/product-lens.md` and
`.project/active/constraint-semantics-contract/product-lens.md`. Obligations owned by sibling items
(Items 1–4 landed, Item 6 not run) were treated as out of scope, per the run instruction. The TEAx
checkout `/home/reid/1cfe/teax` was **not** read, so no TEAx-side claim below is first-hand; every
codegen, docs, and fixture line cited was opened this session.

**Existing epic findings carried forward (grades preserved, not restated):**
`constraint-semantics-contract/product-lens.md` **spec-F6 [DO]** (the Q4 restriction is
*predicate-body-only*; the D-2 vs D-4/SRC-01 self-named-binding conflict is surfaced and parked) and
**spec-F7 [DO]** (a criterion that goes green only because it selects one interpretation) — both
**(agent/ratified)**. Item 5 sits directly on top of both; item5-F1 and item5-F5 below are their
first contact with a real model.

**Point** (re-derived from SOURCES; the WORK was opened only after the sources were read):

1. Constraints exist to make design search viable — the search must be able to tell a candidate
   that passed its physics gates from one nobody checked. [source: `rulings-20260812.md:13-15`
   **[OWNER-VERBATIM]**; epic Critical Success Factor `epic_constraint_semantics_contract.md:18-20`
   **[OWNER]**; grade: owner]
2. The evidence must represent **every applicable asserted physics gate**, while **every other
   authored constraint remains visibly dispositioned**. Two totals, never conflated: inventory
   totality over all authored usages, and feasibility coverage over applicable asserted gates only.
   [source: CSF **[OWNER]**; L2-1/L2-2 `rulings-20260812.md:44-51`; ADR-009
   (`docs/architecture/modeling-assumptions.md` §9); grade: owner for the factor, agent/ratified for
   the two-totals mechanism]
3. **The owner decides the dispositions and every tolerance.** Tolerances are modeled,
   modeler-chosen values; the pipeline never invents one, and neither does an agent. The equality
   intent taxonomy is the classification vocabulary, and class 1 ("structural identity → derive it,
   don't constrain it") is dispositioned *as a derivation, not as a banded constraint*. [source:
   umbrella `spec.md:270-276` **[NEED]** owner-gated; `spec.md:144-158` **[NEED]** owner-stated +
   R-POL-4; grade: owner-gated need, agent-drafted content]
4. Narrow bands of viability make exploration hard, so the product must instruct *when* an equality
   should be used at all — and the band idiom is made ergonomic by a small reusable
   constraint-definition library. [source: `rulings-20260812.md:16-18` **[OWNER-VERBATIM]**; Q4
   `:32`; grade: owner for the instruction obligation, agent/ratified for the library]
5. Severity by cause: asserted + structurally unattachable is a **generation-halting error**, and a
   BLOCK on any asserted constraint halts the **whole model**. Migration is therefore atomic.
   [source: Q3 `rulings-20260812.md:31`; umbrella `spec.md:184-189`, `:195-197` **[HARD]**;
   `elaborate.py:488`; grade: agent/ratified, with the halt itself [HARD]]
6. The proof is end to end through the real TEAx route: a valid candidate reaches the satisfied
   path, an unphysical mutation reaches `reject`, and coverage lands in durable case records.
   [source: epic Item 5 scope 5; Q6 `rulings-20260812.md:34`; grade: agent/ratified]

**Falsifier:** a landing in which the derivative's numbers were fixed before the owner chose the
dispositions that determine them; or one in which the approved table can be authored faithfully and
the model then refuses to generate; or one where the mutation proof has no surviving executable gate
to cross because the taxonomy correctly derived them all away; or a band that reads satisfied while
its tolerance carries the wrong dimension, with no owner for that invariant anywhere in the product.

### Findings

- **item5-F1 [BLOCK] — SC-3 pre-commits to a usage count that only the owner's not-yet-made
  dispositions can determine, and the owner check-in is the very next step.** SC-3 requires the
  derivative to produce "exactly 65 catalog carriers" (`spec.md:92-95`). SC-1 asks the owner to
  choose, per usage, between intent classes including derive-instead (`spec.md:83-87`,
  `:139-145`), and the classification vocabulary the spec itself carries says class 1 is
  "structural identity → derive it, don't constrain it" (`spec.md:152-158`). A derivation
  **removes the authored usage**; the derivative then has 64 or fewer, and totality still holds at
  64/64. The umbrella states this in an owner-gated `[NEED]`: "equality-class-1 constraints
  dispositioned as derivations, not banded constraints, where the taxonomy applies"
  (`constraint-semantics-contract/spec.md:270-276`). The count can move the other way too: the Q4
  bindings-only rewrite of `LayerContinuity` (13 chained equalities) and
  `RadiusThicknessConsistency` (14) has no loop construct, so preserving one usage each means one
  `constraint def` carrying ~26–28 formals — an authoring shape chosen to protect a number rather
  than to read well. Meanwhile the Non-Goals forbid an agent from inventing intent classes
  (`spec.md:244`), so no agent may steer the table back to 65. SC-1 and SC-3 cannot both be
  satisfied under every lawful owner answer, and the item's next action is to put that table in
  front of the owner with one column of answers already excluded. That is a capture-fidelity law 4
  failure at the exact hop the law governs. **Consequence for SC-5:** apply the taxonomy honestly
  to CATF's nine and most are structural identities or an envelope pin (class 1/3/4) — of the nine,
  only `ViabilityCheck` (`p_electric_net_out > 0`) admits today as a real one-sided feasibility
  gate. Nothing in the spec requires the approved table to leave at least one executable physics
  gate for the mutation to cross, so SC-5 silently depends on an owner decision it never names.
  — source: umbrella `[NEED]` owner-gated table (owner-gated), R-POL-4 taxonomy (owner-stated
  need, agent-drafted content), epic Item 5 criterion 3 (agent) — **disposition:** restate SC-3 as
  totality over the derivative's *own* authored-usage domain — every authored usage carries exactly
  one disposition, zero absences — and keep "65/65" where it is a fact: the frozen `catf_mfe_d5`.
  If a 65-carrier derivative is genuinely wanted, that is an owner decision to make **at the same
  check-in**, not an inherited criterion. Add one criterion that the approved table leaves at least
  one applicable asserted gate that SC-5's mutation crosses.

- **item5-F2 [DO] — `awaits-capability` has no authored form attached, and the wrong one halts
  generation of the whole model.** The Non-Goals say the 51 calc-def usages are "dispositioned
  `awaits-capability` in the table, not built" (`spec.md:240-242`), and SC-4 says those groups
  "land exactly where `owner-disposition.md` puts them" (`spec.md:96-98`). Neither says what the
  usage may be *authored as*. Under Q3 an asserted, structurally-unattachable constraint is a
  **generation-halting error** by design (`rulings-20260812.md:31`; umbrella `spec.md:184-189`) —
  that error is the deliberate interim behavior, not a bug — and the spec's own `[HARD]` says a
  BLOCK-class halt takes the whole model with it, so migration is atomic (`spec.md:178-181`). So
  if the approved table calls for asserting any of the 51 while the capability is staged to Item 6,
  the derivative does not generate at all and SC-3, SC-4, SC-5 and SC-7 fail together. The table is
  owner-gated and drafted **before** design, so the spec is the only artifact that can carry this
  constraint into the draft. — source: Q3 severity by cause (agent/ratified), `[HARD]` whole-model
  halt (hard) — **disposition:** state it as a requirement: `awaits-capability` means the usage
  stays in a non-asserted form in the derivative, and the draft table says so on every one of the
  51 rows. Same treatment for any part-def guard the owner dispositions inapplicable rather than
  attaching.

- **item5-F3 [DO] — the invariant "a band's tolerance carries the right dimension" is left without
  an owner in the product, and the escape hatch the spec names does not compose with the library it
  requires.** The spec records limit 1 correctly — a unit on a constraint *binding* is inert, a
  mis-united band is admitted silently (`spec.md:57-65`, matching
  `docs/architecture/modeling-assumptions.md` §8) — and mitigates it with an `[INFERRED]`
  unit-check column reviewed at the owner check-in and again at design review (`spec.md:159-161`).
  That is human review with no artifact and no test; nothing in the derivative or its expected
  outputs carries the reasoning forward, so a later edit to a tolerance re-opens the hole with no
  tripwire. The spec also names the documented alternative — "moving the comparison and both
  annotations into the predicate body" (`spec.md:63-65`) — without noting that it and the required
  reusable band library pull in opposite directions: a predicate body that annotates both operands
  (`measured [m] >= floor [m]`, the one supported unit-carrying spelling, `spec.md:182-186`) is
  **dimension-specific**, so a single reusable `WithinBand` cannot be the unit-checking form. Design
  is handed both as if they compose. — source: §8 as landed (agent/ratified), Q4 library
  (agent/ratified), CSF "can trust the generated feasibility evidence" (owner) — **disposition:**
  say which gates (if any) get the dimension-specific in-predicate spelling and which take the
  reusable unit-blind band under review, and require the unit reasoning per band to land in a
  committed artifact (the table row and the derivative's PROVENANCE), not only in a review
  conversation.

- **item5-F4 [DO, low] — the library that answers the owner's ergonomics concern is scoped to the
  test tree, so the product's authoring guidance never gains it.** Q4 pairs the two-inequality band
  with "a small reusable constraint-def library" as the thing that makes the band idiom bearable —
  the ruling's answer to the owner-verbatim worry that "narrow bands of viability may make design
  exploration really difficult" (`rulings-20260812.md:16-18`, `:32`). The spec's Open Question
  offers exactly two homes: "inside the derivative's `library/` or in a shared fixture library"
  (`spec.md:257-258`). Both are fixture-local. The published authoring section a modeler actually
  reads — `modeling-assumptions.md` §8, "What a modeler needing an enforced gate should do" —
  teaches the band idiom by hand and names no library, and this item is the only place in the epic
  that builds one. — source: Q4 (agent/ratified), owner-verbatim ergonomics statement (owner) —
  **disposition:** either widen the option set to include a product-facing home, or record as a
  decision (not a prohibition) that the library stays fixture-local for now and that the guidance
  gap is unclosed, so a later reader knows it was seen. No behavior change implied either way.

- **item5-F5 [DO, low] — "surface it and stop" will fire on a rewrite that a formal rename makes
  legal, and the landing is atomic.** The spec forbids bare self-named bindings and instructs the
  item to surface and stop if a rewrite appears to require one (`spec.md:170-173`, carrying epic
  ledger spec-F6's parked D-2 vs D-4/SRC-01 conflict). Two of the nine gates are the likely
  trigger: `ThicknessConsistency` (`vacuum.sysml:87`, `outer_radius == inner_radius +
  wall_thickness`) and `PumpingSpeedConsistency` (`vacuum.sysml:169`) compare **the owner's own
  attributes** by bare name, so the transcription-style rewrite is `in outer_radius =
  outer_radius;`. Naming the formal differently (`in measured = outer_radius;` — the fusion_tea
  shape, `research §5`) is not a self-named binding and does not touch the parked conflict. As
  written, an implementing agent that transcribes names can halt an atomic, all-or-nothing landing
  on a condition it created. — source: `[HARD]` D-4/SRC-01 (hard), epic ledger spec-F6
  (agent/ratified) — **disposition:** one clause on the stop condition: stop when renaming the
  formal cannot avoid the self-named binding. Do not resolve the parked conflict.

### Smells

- **A criterion that goes green only because it selects one interpretation: FIRES**, on item5-F1.
  "Exactly 65 catalog carriers" reads as a measurement but is a prediction about a decision the
  owner has not made, and the same signature is already recorded twice in this epic
  (`constraint-semantics-contract/product-lens.md` **spec-F7**, and
  `constraint-predicate-hardening/product-lens.md` **item4-F1**). Third occurrence in one epic; it
  escalates into this stage's judgment rather than sitting in a rubric.
- **Ownership of an invariant changing hands silently: FIRES**, on item5-F3. Band-unit correctness
  was the profile's job everywhere else in the contract; here it moves to human review, and the
  spec states the limit without naming the new owner or leaving a durable artifact.
- **Two representations kept in sync: fires weakly, and is accepted by owner ruling.** The table,
  the derivative source, and the pre-committed expected outputs state the same facts three times.
  The spec handles this the right way — the table is "the sole source of intent classes and
  tolerance values for everything downstream" (`spec.md:139-141`) and the other two are derived —
  and the hand-written-before-the-run shape is exactly what the owner's sequence asked for
  (SC-6). Not a finding.
- **Consumer compensating for a producer guarantee: does not fire.** The report's coverage account
  is consumed one-direction from the catalog (`spec.md:194-199`); this item adds no second path.

**Not findings (checked, clean):**
- **No owner-graded statement is contradicted by the spec's requirements.** The owner sequence is
  carried whole and made auditable as a commit-order argument (SC-6, `spec.md:103-106`), the
  owner-gated table is a distinct pre-design artifact that design may not start against in draft
  (`spec.md:146-148`), and "the pipeline never invents a tolerance, and neither does this item's
  agent — a placeholder is an explicit `TBD-OWNER` marker, never a plausible number"
  (`spec.md:149-151`) is a faithful and slightly strengthened carry of the owner-stated `[NEED]`.
- **Provenance grades are carried correctly across the hop.** SC-6 is `[OWNER, 2026-08-12
  sequence]`, matching `rulings-20260812.md:19-20` (owner-stated, not verbatim); the CSF is quoted
  as `[OWNER]` block-quote with its path; Q4/Q8 arrive as `[INHERITED] [AGENT] (ratified by owner,
  2026-08-12)` rather than being promoted; SC-8 is `[AGENT], announced at the Align checkpoint,
  unobjected` — correctly *not* upgraded to owner grade by non-objection.
- **The traveling residual is disposed, not restated.** Item 2's R3 lands as SC-8 with a named home
  and an open question about the baseline's shape (`spec.md:111-114`, `:267-269`) — a disposition,
  not a carried-forward complaint.
- **Both Item 4 limits are carried with their measurements and their consequences**, including the
  non-obvious one (drive the rewrites off the chain name, not the line, `spec.md:66-69`), which is
  the operational half most likely to be dropped in compression.
- **The unverified TEAx tip is surfaced, not assumed** (`spec.md:226-228`, "this session could not
  read the TEAx repo state"), with the verification pushed to the start of design — capture-fidelity
  law 4 applied correctly.
- **The `[INFERRED]` malformed-`@inapplicable:` hard stop is graded honestly** as an Item 2
  `[AGENT]` severity exception, "orchestrator-ratified, **not owner-ruled**" (`spec.md:208-213`).
  That is the settled rule applied exactly right.
- **Non-Goals read as decision records, not as instructions to future agents** — in-predicate
  chains stay "filed as a future capability candidate", and the parked self-named-binding conflict
  is a park, not a prohibition.
- **The Problem section corrects a stale premise rather than repeating it** ("older documents say
  '9 eligible'. The 9 are **reaching**, not eligible", `spec.md:30-32`), which matches the Item 2
  close record and the research measurement.

**Gate: BLOCK (item5-F1) — item5-F2..item5-F5 DISPOSED.** item5-F1 blocks because the item's next
action is the owner check-in, and an agent-grade inherited criterion (SC-3's "exactly 65") narrows
the answer set of an owner-gated `[NEED]` before the owner sees it — a lawful class-1 "derive it,
don't constrain it" answer makes SC-3 unsatisfiable, and Non-Goals forbid an agent from steering the
table back. Fix SC-3's wording before `owner-disposition.md` is drafted; the cost is one sentence
and the alternative is asking the owner a rigged question. item5-F2 is the same shape at the other
end: an approved table that asserts any of the 51 calc-def guards is a table the model cannot
generate against, and the spec is the last artifact that can say so before the table is drafted.
The thread running through F1, F2 and F3 is a boundary drawn around the *numbers* rather than around
the *decision that produces them* — the item measures a count where the product's promise is an
honest disposition per usage, an executable gate the search can cross, and a band whose units
someone owns.

---

## design — 2026-08-13 — rev 47e944a (`design.md` committed at `2821c38`)
Epic: CONSTRAINT-SEMANTICS (`epic_constraint_semantics_contract.md`, Item 5 — CATF Derivative and
End-to-End Acceptance)

**Runner note:** `~/.claude/scripts/product-lens.md` and its pack source
(`/home/reid/agentic-project-init/claude-pack/scripts/product-lens.md`) are outside this session's
sandbox and were refused on every read route again, so the lens was run from its stated purpose —
an independent two-direction check (does the WORK contradict or narrow the product point; does it
omit an obligation the point requires) — plus the two named structural smells, in this file's
existing format. The owner ruling on D-S1/D-S2 is out of scope by instruction; what is judged is
the design's **handling** of the surprise. `/home/reid/1cfe/teax` was not read. Every codegen,
docs, and fixture line cited below was opened this session.

**Point** (re-derived from SOURCES before the design was opened; unchanged in substance from the
spec-stage entry, so it is not restated in full — the two clauses this stage turns on):

- **A search must be able to tell a candidate that passed its physics gates from one nobody
  checked**, which requires the generated evidence to represent **every applicable asserted gate**
  *and* every other authored constraint to remain **visibly dispositioned** — visibly, in the
  shipped artifact a search reads, which in this product is the catalog and the coverage account.
  [source: epic CSF `epic_constraint_semantics_contract.md:17-19` **[OWNER]**;
  `rulings-20260812.md:13-15` **[OWNER-VERBATIM]**; ADR-009 / `modeling-assumptions.md` §9;
  grade: owner]
- **Two totals, never conflated**, and the machinery that keeps them apart is product-owned:
  `coverage_account`'s four-bucket table (`src/sysml_codegen/generation/coverage.py:7-27`), the
  catalog's one-disposition-per-authored-usage domain (`modeling-assumptions.md` §8, "Every
  authored usage has a carrier"), and the one bar the three generation seams read
  (`ships_constraint_machinery`, `src/sysml_codegen/resolution/models.py:625-644`).
  [grade: agent/ratified, over an owner-grade factor]

**Falsifier for this stage:** a design in which a constraint the owner ruled *should gate* ends up
indistinguishable, in the shipped artifact, from one nobody has gotten to yet; or one whose stated
validation asserts a check it has already shown cannot pass; or one that discharges a residual
against a package shape the product no longer produces.

### Findings

- **item5d-F1 [DO] — the three parked rows keep their disposition in `design.md` and lose it in
  the artifact a search reads.** Under D-S1/D-S2 the derivative cannot author A9's ruled
  `assert-band` or A5/A6's ruled derivations. Those usages therefore ship **as authored** — bare
  `constraint`, in-predicate `==` — and the catalog gives them `excluded / unassessed form`, which
  is the identical row `catf_mfe_d5` shows for them today (`owner-disposition.md:70-72`, Group A
  header; `spec.md:23-28`). A reader of the derivative cannot distinguish "the owner ruled this a
  1%-band physics gate and a named product defect refuses it" from "nobody has touched this yet".
  That is exactly the confusion the CSF names. The design's own artifact list makes the gap
  concrete: `PROVENANCE.md`'s contents are enumerated at `design.md:304-307` as per-change records,
  the nine deletion records, the two O3 model-debt entries, and the per-gate unit reasoning —
  **no parked-row records** — and Non-Goals says only "Resolving D-S1 or D-S2" (`design.md:319`).
  The surfacing itself is done right: the conflict is named, dependent conclusions are parked, the
  arithmetic consequence is stated and the ruled number left in force (`design.md:141-178`). What
  is missing is that the surfacing stops at the `.project/` boundary. — source: CSF (owner),
  catalog totality (agent/ratified, over owner-grade L2-1/L2-2) — **disposition:** whatever the
  owner rules, the derivative carries a named record per parked row — qualified name, ruled
  disposition, the refusing reason code and its measured probe, and the authorizing table row —
  in the same PROVENANCE that carries the nine deletions. If the ruling is "accept as
  awaits-capability", that record is the disposition; if it is "fix the defect", the record is what
  the fix discharges. One list either way, and it belongs beside the fixture, not only here.

- **item5d-F2 [DO] — D7's stated reason is false at HEAD, so SC-8 would be discharged against a
  package shape the product stopped producing in Item 3.** D7 picks
  `constraint_domain_satisfy_calc_def` as the R3 baseline because it is the calc-def-only example
  "whose package correctly ships no `schemas/constraint_types.py`" (`design.md:238-239`), and
  rejects `catf_mfe_gated` on the ground that it "cannot pin the absent-machinery shape"
  (`design.md:242-243`). At HEAD that package **does** ship `schemas/constraint_types.py`:
  `ships_constraint_machinery` moved its bar from one concrete entry to one authored usage
  (`src/sysml_codegen/resolution/models.py:634-644`), and the conformance suite asserts the
  shipping positively — `assert (output / "schemas/constraint_types.py").exists()` in
  `tests/conformance/test_constraint_catalog_totality.py`,
  `test_a_usage_only_package_ships_the_machinery_and_a_zero_input_report`. The premise is inherited
  from the spec's Problem section (`spec.md:71-76`), which restates Item 2's R3 wording verbatim;
  Item 3 superseded it and the design carried it forward as measured. The design elsewhere records
  the correct rule (`design.md:347`, "`ships_constraint_machinery` now keys on one authored
  usage"), so this is an internal contradiction, not a missing fact. The fixture choice survives
  the correction — but what it pins changes, and the change is the more valuable one: not "absent
  machinery" but **"declared constraints, assessed zero"**, the byte shape that lets a consumer
  tell that state from a constraint-free model, which is Item 3's central promise and has no byte
  baseline. — source: Item 3 as landed (agent/ratified), R3 residual (agent) — **disposition:**
  restate D7's reason and SC-8's claim to the assessed-zero-with-a-report shape. Keep the fixture
  and the `MODELS` row (`MODELS` covers only four of the thirteen baseline directories today,
  `tests/conformance/test_baselines.py:26-31`, so the new row is what actually gates it).

- **item5d-F3 [DO] — the Validation Approach asserts an integrity check the SURFACED section has
  already shown cannot pass, and the handoff calls the parks narrower than they are.** D2's script
  proves `65 = carriers + named deletions` by joining the ruled table against the derivative's
  catalog and PROVENANCE (`design.md:205-209`). Under the parked set — A5, A6, A9 not landable —
  A5/A6's usages are not deleted and A9 is not asserted, so the join against the ruled rows cannot
  close, by construction. Validation Approach items 1 and 3 nonetheless list
  "`check_gated_manifest.py --check` passes" and the coverage-row agreement unconditionally
  (`design.md:370-374`), and Potential Risks (`design.md:353-359`) carries no row for it. The
  handoff then labels the open group "**blocking their own rows only** … not a blocker on the item"
  while listing the accounting identity inside it (`design.md:390-392`) — but SC-3 and SC-4 are
  *item* criteria, not row criteria, so the parks block the item's acceptance, not three rows.
  The design was right not to restate the identity (`design.md:176-178`); the error is downstream,
  where the unrestated identity is still validated as if it held. — source: SC-3 as amended
  (`spec.md:93-105`, [AGENT] ratified by owner), B4 (agent) — **disposition:** state the landable
  identity as an explicit *conditional* — under the parks the check closes over the landable set
  plus a named parked list, and closes over the ruled table only once D-S1/D-S2 are ruled — and
  put the "identity cannot close while the parks stand" row in Potential Risks with the sequencing
  that follows from it.

- **item5d-F4 [DO, low] — the citation the "all-or-nothing landing" premise rests on points at
  unrelated code.** `elaborate.py:488` is cited for "a profile BLOCK on any asserted constraint
  halts the whole model" (`design.md:135`, inherited from `spec.md:206-207`, which says
  "verified"). Line 488 is an `SI_EDGE_DANGLING` raise for an unrecognized constraint-definition
  UUID. The whole-model halt is real and lives at
  `src/sysml_codegen/elaboration/elaborate.py:1145-1152` — `Eligibility.BLOCK` →
  `_diagnose(SI_CONSTRAINT_BLOCKED, …)`. The premise is correct; only the pointer is wrong, and the
  design's probe-first shape is built on it, so an implementer verifying it lands nowhere.
  — source: [HARD] BLOCK-halts-generation (hard) — **disposition:** repoint to
  `elaborate.py:1145-1152` here and in the spec.

- **item5d-F5 [DO, low] — an Implementation Note states a flat prohibition that the landed
  authoring contract contradicts.** "A `[unit]` literal must not appear in a predicate body"
  (`design.md:340`). The landed contract says the opposite for the both-operands spelling:
  `gap_width [m] >= 0.25 [m]` "is the supported way to write a unit-carrying gate, and the units
  are then compared" (`docs/architecture/modeling-assumptions.md:520-522`), carried into this
  item's own spec as `[HARD]` (`spec.md:209-213`). Only the *one*-operand form is refused. The
  note is harmless for this item — neither surviving gate needs a unit — but it is written as a
  rule, and `owner-disposition.md:99-101` separately gestures at an "`[m]`-literal elaborator
  failure (research §6)", so a reader cannot tell whether this is a local scoping choice or a
  measured contradiction of §8. If it is the latter, it is a §4 surfacing obligation, not an
  implementation note. — source: §8 as landed (agent/ratified), spec [HARD] (hard) —
  **disposition:** one clause saying which: "neither surviving gate carries a unit literal, so the
  question does not arise here", or a measurement against §8 with the contradiction surfaced.

### Smells

- **(a) A consumer compensating for a producer or platform guarantee: DOES NOT FIRE.** This is the
  case a reviewer should expect to fire, and the design is explicitly clean on it. The compensating
  move was available, named, and refused: "A shim attribute introduced solely to dodge the
  collision would be exactly the silent workaround the brief forbids" (`design.md:154-155`). The
  design chased the refusal to the producer seam instead of routing around it — constraint-formal
  port metadata takes `unit=None` by construction because the attribute lane is only consulted for
  a `CalcNode` (`src/sysml_codegen/elaboration/elaborate.py:1678-1689`, cite verified this
  session), and projection then refuses the mismatched `EntryPoint` pair
  (`src/sysml_codegen/elaboration/project.py:393-397`, verified) — and it names the product fix as
  the owner's first option (`design.md:155-156`). It also refused the second available
  compensation, editing the shared library calc defs' unit comments, as a Non-Goal
  (`design.md:321`). Two other candidates were checked and do not fire: D2's manifest script is a
  check the platform *cannot* provide (the identity is cross-fixture, and the totality preflight is
  per-model), and the seven derivations are the ruled class-1 policy, not a workaround.
- **(b) A solution that changes who owns an invariant without saying so: FIRES**, on item5d-F1.
  "Every other authored constraint remains visibly dispositioned" is owned, in the product, by a
  machine-produced catalog row with a closed disposition vocabulary. For A5, A6 and A9 that
  ownership moves to a `.project/` design document, and the design does not say so — the PROVENANCE
  contents list omits parked-row records entirely (`design.md:304-307`) and Non-Goals frames the
  parks as a resolution question only (`design.md:319`). Note the contrast with the *other* place
  ownership moves in this design, which is handled correctly: D2 states plainly that the
  cross-fixture accounting identity moves from byte-reversal to a bespoke script, says why the old
  mechanism cannot transfer, and books the transfer as bet B4 (`design.md:205-211`, `:195-198`).
  Same shape, said out loud — which is what makes the silence on the parked rows a finding rather
  than a preference.
- **A criterion that goes green only because it selects one interpretation: fires weakly, on
  item5d-F3, and is not the same defect as the spec stage's.** The identity is no longer a
  prediction about an unmade owner decision (that was `item5-F1`, resolved by ruling). It is now a
  ruled number validated unconditionally against a set the design has already measured as
  unreachable. The fix is a conditional, not a re-ruling.
- **Two representations kept in sync: accepted, unchanged from the spec stage.** The design
  tightens it rather than loosening it — "Nothing flows backwards. The catalog is read to
  cross-check *which usages exist*, never to obtain counts" (`design.md:265-267`), carrying Item
  3's PD2/DR-6 rule and the ledger-parsing precedent
  (`tests/unit/test_coverage_ledger_agreement.py:1-11`, whose docstring makes the same argument).
  Not a finding.

**Not findings (checked, clean):**
- **The SURFACED handling is correct on every axis capture-fidelity §4 asks for.** The conflict is
  named against owner-graded content, both dependent conclusions are parked rather than adjusted,
  the arithmetic consequence is stated *without* restating the identity ("Recomputing it would be
  an agent silently re-dispositioning owner-ruled rows", `design.md:176-178`), and the owner is
  given three options — fix the product, re-disposition, accept as `awaits-capability` — with no
  recommendation smuggled in. The refusals were chased to source and the blast radius **measured**
  (26 of 27, from `radial_build.sysml:96-565`), not estimated. This is the behavior the rule exists
  to produce.
- **D3 discharges the spec's `item5-F3` unit finding honestly, and by the right argument.** It does
  not transfer the unit invariant to a reviewer; it shows the invariant is vacuous for the landable
  set — A2 is a `real`/`real` comparison against an authored zero, A3's two edges are genuinely
  dimensionless — and it lands the reasoning in a committed artifact per gate rather than in a
  review conversation (`design.md:212-219`). Worth noting for the plan, not as a finding: that
  vacuity is contingent on A9's park. A9 is the one ruled band whose tolerance carries a real
  dimension (`m^3/s`), so if the owner unblocks it, item5-F3 returns intact and D3's answer does
  not cover it.
- **The probe-first shape is the right response to an atomic landing**, and the design does not
  overclaim from it: B2 is booked as a bet with a named falsifier, the de-risk instruction is
  specific (re-run the composite with the five markers and the C21/C28 deletions *before*
  authoring), and the caveat that A3/A9 were predicted rather than measured is carried from
  `owner-disposition.md` rather than quietly upgraded.
- **The coverage denominator is read correctly against the code.** The five part-def guards stay
  plain, so `coverage_account` puts them in bucket 1 — inventory only, never the denominator
  (`src/sysml_codegen/generation/coverage.py:218-219`) — and their `@inapplicable:` markers change
  the catalog row, not the account. Required Invariant 6 (`design.md:291-292`) states exactly this,
  and Invariant 4 correctly notes that a malformed marker halts "whatever the usage's form —
  including a plain one".
- **Provenance grades survive the spec → design hop.** The CSF is quoted `[OWNER]` with its path;
  the ruled table is cited as sole authority rather than re-derived; the A5/A6/A7 bases are used as
  `[AGENT] (ratified by owner)` and not promoted; D1–D7 are agent-grade by construction and marked
  as decisions with rejected alternatives, which is the design register's correct form.
- **Rejected alternatives read as decision records, not as prohibitions** — one line each, with the
  reason, inside the decision they belong to.

**Gate: PROCEED — item5d-F1..F5 DISPOSED, no BLOCK.** The reason this is not a BLOCK is the same
reason the spec stage was one: the test is whether the next step's question is rigged, and here it
is not. The next step is the owner ruling on D-S1/D-S2, and the design puts three genuine options
in front of the owner with the measurement behind each and no recommendation attached. Fix F1
through F3 before `/_my_plan`, not before the ruling — F1 because the ruling determines the
record's *content* but not whether one is needed, F2 and F3 because both are one-sentence
corrections that a plan would otherwise inherit as facts. The thread through F1, F2 and F3 is a
single habit: the design reasons carefully and then states its conclusions one register too
confidently downstream — a parked row is parked in the design but not in the fixture, a superseded
premise is carried as measured, and an identity the design pointedly declines to restate is
validated as if it held.

---

## audit — 2026-08-13 — rev 7c076b6
Epic: CONSTRAINT-SEMANTICS (`epic_constraint_semantics_contract.md`, Item 5 — CATF Derivative and
End-to-End Acceptance)

**Auditor note.** Findings audit-F1, audit-F2 and audit-F6 were re-verified independently by the
audit before the gate was accepted (see `audit.md` §Probe record). audit-F1 reproduces:
`grep -rn "CHOSEN BASIS\|Relation (undirected)" tests/fixtures/catf_mfe_gated --include=*.sysml`
returns `library/physics/power_balance.sysml` only, against a PROVENANCE §2 claim that the
statements "appear in both places". The audit adds a second instance of the same shape (the
`value` → `quantity` rename, `audit.md` finding **A-2**), which the lens caught only as a nit.

Point (re-derived): A design search can trust the generated feasibility evidence to represent
every applicable asserted physics gate, while every other authored constraint remains visibly
dispositioned — and every disposition the item claims is carried by the artifact it claims to
carry it, not only by the item's own records.
[source: `.project/backlog/epic_constraint_semantics_contract.md:18` (Critical Success Factor,
[OWNER]); supported by `docs/architecture/modeling-assumptions.md` §8 and §9/ADR-009,
grade: owner/HARD for the CSF, agent/ratified for §8–§9]

Falsifier: elaborate/generate `catf_mfe_gated` and find any of — (a) an authored `.sysml`
constraint usage with no catalog record; (b) `full_satisfaction` while an applicable asserted gate
went unassessed; (c) a disposition or obligation asserted in `owner-disposition.md` /
`PROVENANCE.md` that no committed check ties to the shipped fixture bytes.

Findings:
- audit-F1 [DON'T] The owner's derivation documentation obligation is unmet in source for two of
  the three derivations. Only C37 carries it (`tests/fixtures/catf_mfe_gated/library/physics/power_balance.sysml:66-70`);
  A7 (`designs/catf_mfe/shield.sysml:105`) and A8 (`designs/catf_mfe/vacuum.sysml:53`) are bare
  initializers with no undirected relation and no chosen-basis statement. PROVENANCE §2 asserts
  the opposite — "Those statements are carried in source beside each derivation" — and its
  recorded deviation covers only `//` vs `doc /* … */` form while reaffirming that the statements
  "are mandatory either way and appear in both places". The obligation exists so the relation
  intent survives the deletion in the model, not only in a sidecar doc.
  — `owner-disposition.md:37-41`, "Derivation documentation obligation **[OWNER 2026-08-13,
  structural amendment]**" (owner) — disposition: **BLOCK**
- audit-F2 [DO] No check ties a `derive-instead` deletion to the derivation that replaces it.
  `scripts/check_gated_manifest.py` joins four sources and never opens a `.sysml`. §8's standard is
  that domain completeness is proved by evidence outside the domain; the deletion side is owed the
  same. This is why audit-F1 landed green through Phases 3–7. — AGENT/INFERRED — disposition:
  extend the check to assert, per `derive-instead` record, that the named derivation exists in
  source and carries its relation + chosen-basis statement
- audit-F3 [DO] SC-5's end-to-end claim is not regression-protected. The coverage half is durably
  gated (population oracle by scan; `tests/unit/data/expected-coverage.md` drives
  `tests/unit/test_coverage_ledger_agreement.py`); the feasibility-rejection half exists only as a
  recorded run reproduced from `probes/acceptance_run.py`. — INHERITED/aspirational — disposition:
  record the TEAx lane as intentionally manual, or file it as a test
- audit-F4 [DO] No verification-matrix rows filed for this item's new gates. —
  `docs/architecture/verification-matrix.md` (INHERITED) — disposition: file rows, or record the
  matrix as out of scope for this epic
- audit-F5 [DO] The derivative ships `coverage_state: complete` / `full_satisfaction` with
  `applicable_gate_total = 2` while A5/A6/A9 — instance-reaching physics gates whose ruled target
  form is an executing assert — sit outside the denominator as plain usages, indistinguishable in
  the generated evidence from the 48 `awaits-capability` guards. — §9/ADR-009 + D-S1/D-S2
  (agent/ratified) — disposition: **DISPOSED** by the D-S1/D-S2 ruling ([AGENT], ratified by owner
  2026-08-13); carried forward as an explicit obligation on the epic Item 9 follow-on
- audit-F6 [DO] `tests/conformance/test_zero_entry_package_golden.py:69-87` hand-rolls the
  generation sequence from seven private `_generate_*` seams, omitting the preflight block,
  `_generate_primitives`, `_generate_backlog` and `_generate_tests` that `run_codegen` runs
  (`src/sysml_codegen/cli/__init__.py:1204-1299`). The tree's first committed-bytes gate pins a
  route kept in sync with the shipping route by hand. — `CLAUDE.md` ("`run_codegen` is the single
  public generation entry point and constructs exactly one way") (INHERITED) — disposition: drive
  the golden through `run_codegen`, or record why the private seams are the intended subject

Smells fired (escalated into the audit's Product Judgment):
- Smell 3 (a special category exempts a case whose user-visible meaning is unchanged) —
  `blocked-by-defect` removes A5/A6/A9 from the feasibility denominator while what the modeler
  wrote, a physics gate, is unchanged. Escalated at audit-F5; **disposed** by the D-S1/D-S2 ruling
  with the follow-on obligation named there.
- Smell 1 (two representations manually kept synchronized) — the zero-entry golden's generation
  sequence versus `run_codegen`'s. Escalated at audit-F6; **not resolved**.

**Gate: BLOCKED (audit-F1).**

**Gate resolution (audit cure re-verification, 2026-08-13, rev `b5f6fd8`):** audit-F1 **RESOLVED**
by `995a058` (both missing statements authored at `shield.sysml:105,107` and `vacuum.sysml:53,55`;
re-verified by the auditor) and `b083c47`. audit-F2 **RESOLVED** by `b083c47` — the manifest check
now opens the derivative's `.sysml` and gates the obligation, with both failure modes falsified by
the auditor. audit-F3 → residual A-5, audit-F4 → residual A-8, audit-F6 → residual A-4, each
carrying a stated disposition (`audit.md` §Addendum). Smell 1 remains open as residual A-4.
**Gate: CLEAR.**
