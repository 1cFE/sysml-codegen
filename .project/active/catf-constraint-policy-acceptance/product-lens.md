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
