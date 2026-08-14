# Product-lens ledger — Item 7 (constraint-docs-agent-sync)

Append-only. One block per lens run.

---

## spec — 2026-08-14 — rev `.project/active/constraint-docs-agent-sync/spec.md` (draft, untracked)

Epic: CONSTRAINT-SEMANTICS (`.project/backlog/epic_constraint_semantics_contract.md`)

Epic gate at time of writing: **CLEAR** — the epic's own product-lens block records "None. No item
narrows or contradicts the point" (`epic_constraint_semantics_contract.md:130-135`). No epic
finding exists to reference. Nothing from the epic blocks this spec.

**Runner note — reconstructed provenance.** `~/.claude/scripts/product-lens.md` and its pack source
`/home/reid/agentic-project-init/claude-pack/scripts/product-lens.md` are both outside this
session's sandbox and unreadable. Per the epic convention, the **method was reconstructed from the
in-tree ledgers, not the canonical script** — principally
`.project/completed/20260813_constraint-coverage-policy/product-lens.md` (Item 3, the referent) and
`.project/completed/20260813_constraint-catalog-totality/product-lens.md` (Item 2). Reconstructed
method as followed: read SOURCES first and re-derive the Point from them before opening the WORK;
state a Falsifier; check both directions (does the WORK contradict or narrow the point; does it omit
an obligation the point requires); one finding per defect with path-cited evidence, its source and
that source's grade, and a disposition; record what was checked and found clean; close with a Gate.
Treat this entry as method-reconstructed: a canonical-script run may weigh findings differently.
Cross-repo limitation, same as Item 3's run: `/home/reid/1cfe/agentic-mbse-item7-rebuild` and
`/home/reid/1cfe/teax` are unreadable from this sandbox, so **no agentic-mbse or TEAx claim in the
WORK was verified against those repositories.**

**Point** (re-derived from SOURCES; the WORK was opened only after the sources were read):

1. The coverage-truth promise is the owner's own words and is payload, not prose: it survives into
   its first durable home verbatim, at the owner's emphasis, and supplementary material never
   rewrites it. [source: `owner-checkpoint-20260813.md:7-16`; grade: **owner-verbatim**]
2. A design search can trust the generated feasibility evidence to represent every applicable
   asserted physics gate, while every other authored constraint remains **visibly dispositioned**
   — visible meaning a modeler can find and read the disposition, which is a documentation
   obligation as much as a code one. [source: epic Critical Success Factor `:18-20`; grade: **owner**]
3. The promise's second bullet (no embedded engineering logic, no predetermined free variables) and
   the ratified A5/A6/A7 basis rulings are reconciled **in daylight** — stated as directional intent
   with the unbuilt half pointed at `[ACAUSAL-RELATIONS-CAPABILITY]` — and never silently resolved
   in either direction. [source: `owner-checkpoint-20260813.md:28-36`; grade: agent/ratified,
   over owner-ratified basis rulings]
4. After this item, no shipped doc, skill, or agent prompt in **any of the three repos** teaches the
   superseded constraint semantics, and the evidence for that claim is a recorded sweep with one row
   per raw hit — not a summary. [source: epic Item 7 SC2 `:1122-1124`, executing Item 1's recorded
   sweep, `20260813_constraint-semantics-contract-amendments/design.md` Appendix D `:1191-1230`;
   grade: agent/ratified]
5. A modeler can tell, **before authoring**, which mechanism carries their inapplicability
   disposition — in-model `@inapplicable:` on bindings form, PROVENANCE on inline-predicate form
   while `[INLINE-PREDICATE-MARKER-DROP]` is open. [source: epic Item 7 scope 5 `:1099-1106`, Item 5
   close obligation; grade: agent/ratified]

**Falsifier:** a next authoring session — human or agent — that reads a shipped surface in any of
the three repos and reproduces the superseded constraint shape; or a coverage-truth promise filed in
a home where its owner wording has drifted, its tension with the basis rulings reads as silently
resolved, or a reader cannot find it from the product-lens trail the epic points at.

### Findings

- **item7-F1 [DO] — the sweep the spec inherits is cited by a wrong name, a wrong locator, and a
  count that would drop two of its five terms.** The spec carries the sweep obligation as
  "**[INHERITED: epic Current State, `:1058-1059`]** The sweep uses Item 1's three-sweep method"
  (`spec.md:136-138`). Three things are wrong, and they compound. (a) The locator is wrong: epic
  `:1058-1059` is the Current-State line about Items 2–3 correcting falsified docs; the sweep
  obligation is epic SC2 at `:1122-1124`. (b) The epic's own phrase "Item 1's three-sweep method" is
  stale, and the spec inherits the staleness: Item 1's recorded sweep is **five terms**, S1–S5
  (`20260813_constraint-semantics-contract-amendments/design.md:1202-1218`), because design review
  M5 widened S3's verb alternation and added S4 and S5 to cover the item's *own* corrected
  vocabulary — the superseded headline precedence and `assume`/`satisfy` taught as a check. That
  design says in terms: "adding a term is allowed, dropping one is not" (`:1224-1225`). An agent
  executing this spec as written runs three. (c) Two load-bearing halves of the method are absent
  from the spec entirely: the DD5 **scope** (in: `docs/`, `src/`, `tests/`, `scripts/`, `README.md`,
  `CLAUDE.md`, `.project/concepts/`, `.project/backlog/`; excluded, with the exclusion written down:
  `.project/research/`, `.project/completed/`, `.project/active/` — `:1196-1200`) and the
  disposition format's "one row per raw hit. A summary does not discharge the criterion"
  (`:1227-1228`). The spec's own success criterion is the one that fails: SC2 claims the sweep
  record "lists every hit and disposition," which a three-term summary sweep cannot substantiate.
  Compounding it, Item 1's sweep ran in **two** repositories ("Run S1–S5 in the companion repository
  with the same scope", `:1224`) while this item's SC2 asserts the claim over **three** — TEAx has
  no sweep scope defined anywhere. — source: epic SC2 `:1122-1124` (agent/ratified) vs Item 1
  design Appendix D `:1191-1230` (agent/ratified) — **disposition:** name the sweep as Item 1's
  **five-term** S1–S5 sweep with a path-cite to Appendix D, carry the DD5 scope and the
  one-row-per-hit rule, correct the locator to epic SC2, and require the TEAx scope to be stated
  (design's call whether S1–S5 transfer unchanged or a local term is added — adding is allowed,
  dropping is not).

- **item7-F2 [DO] — audit-F4 is closed by half: the spec requires the promise to be filed, never to
  be cited from the trail that made it a finding.** Success Criterion 1 is adopted whole and reads
  "owner-stated, filed in a named home, **and cited from the product-lens trail** (closes Item 3
  audit-F4)" (`spec.md:57-58`, from epic `:1120-1121`). The Known Requirements then cover
  owner-stated (`:88-90`) and the named home (`:107-110`) and stop — no requirement mentions the
  product-lens trail at all. The citation half is the enforceable half: audit-F4's whole complaint
  was that the promise "exists as a concept subsection plus ADR-009 at `[AGENT] (ratified)`" with no
  entry a lens run could resolve against (`epic:540-543`). A promise filed in a new ledger that the
  lens trail does not point at reproduces exactly the condition audit-F4 named, one directory over.
  It also leaves a question the requirement would have forced: *which* trail — audit-F4 lives in
  the archived `20260813_constraint-coverage-policy/product-lens.md`, and archived ledgers are
  cited, not edited (the spec's own rule at `:129-131`). — source: epic SC1 `:1120-1121` (**owner**)
  and epic residual audit-F4 `:540-543` (agent/ratified) — **disposition:** add a requirement that
  the filed entry is reachable from the product-lens trail, and name which ledger carries the
  citation given that audit-F4's own ledger is archived. This is the recurring shape Item 3's lens
  named: an obligation cited for the clause the spec needed and trimmed of the clause that makes it
  enforceable.

- **item7-F3 [DO, low] — one requirement needs a licensed toolchain run that the spec never
  budgets.** Epic scope 3's third clause, carried at `spec.md:157-158`, requires that agent-facing
  examples are "verified to elaborate cleanly under the current profile." Elaboration is the one
  step that needs `SYSIDE_LICENSE_KEY` (`CLAUDE.md`, Architecture §1), which lives in the companion
  checkout's `.env` — a repository this spec's own Open Questions record as unreadable from the
  working sandbox (`:222-226`). Every other requirement in this item is satisfiable by reading and
  writing text. The spec neither names the dependency nor says what happens to the criterion if the
  run is unavailable, so an implementing agent either silently drops the verification or discovers
  the block late. Note this is not a Non-Goals contradiction: an example that fails to elaborate is
  fixed by editing the example, which is a doc change, not the code/fixture change the Non-Goals
  exclude. — source: epic scope 3 `:1092-1096` (agent/ratified) — **disposition:** name the licensed
  run as an execution dependency of that requirement, and state its fallback (defer the check with
  the gap recorded, rather than tick the criterion unverified).

**Not findings (checked, clean):**

- **The owner-verbatim promise is reproduced exactly.** `spec.md:24-30` matches
  `owner-checkpoint-20260813.md:9-13` word for word, including "(like LCOE)" and the 1costingFE
  contrast, and it is carried as a governing obligation in Problem rather than paraphrased into a
  requirement. Point 1 holds.
- **The tension is surfaced, not resolved.** `spec.md:98-106` states the promise as directional
  intent, carries the recorded reconciliation without re-deriving it, points at
  `[ACAUSAL-RELATIONS-CAPABILITY]` (verified present, `BACKLOG.md:439`), and says in terms that it
  is "never resolved silently in either direction." Point 3 holds. The Non-Goals reinforce it rather
  than reopening it.
- **Provenance grades absorb correctly.** `[OWNER-VERBATIM]` → `[NEED]` with a path-cite;
  the checkpoint's self-declared agent-grade filing guidance → `[INFERRED]`, not upgraded to
  `[NEED]` despite the brief's "[OWNER-ratified framing]" label; epic scope areas →
  `[INHERITED]` with sources. The `[MATRIX-EPIC-SURFACE-ROWS]` `[OWNER]` grade is preserved inside
  its citation rather than downgraded at the hop.
- **The locator-mismatch surfacing is right, and the three sites check out.** `spec.md:229-235`
  correctly reports that the umbrella spec's Open Questions carries lens spec-F6 (D-2 vs D-4/SRC-01,
  `:324-328`), not item3-F2. The three sites it names instead verify: `spec.md:195` (the `[HARD]`
  blanket BLOCK clause), `:294` (the Non-Goal), and `epic:531-539` (the residual, which ends "Do not
  let a later agent read the clause as a live requirement"). Surfacing rather than quietly
  substituting the locator is capture-fidelity law 4 applied correctly.
- **The matrix baseline is hedged honestly.** `spec.md:220-222` cites 276 rows / 275 PASS / 32
  families "as of the last recount" rather than as current truth. Correct: that baseline is dated
  2026-07-24 (`BACKLOG.md:464-466`), predates this epic, and the same ticket's three candidate
  surfaces are stale in a second way the spec does not borrow — `resolution/producer_resolution.py`
  and `producer_completeness.py` were deleted by the cutover retirement (`CLAUDE.md`, "Retired").
  The spec takes only the recount discipline. Worth one line at design time so nobody re-reads that
  ticket's surface list as live.
- **The two Item 7s are not conflated.** The epic's Item 7 evidence-invalidation register
  (`:175-185`) and success criterion `:111-114` are about **ELABORATE-FIRST** Item 7, a different
  item that shares a number. The spec claims none of that register's obligations. Correct, and the
  collision is a live trap for a later reader.
- **No owner-graded or `[HARD]` statement is contradicted anywhere in the WORK.**

**Gate: DISPOSED (item7-F1..item7-F3)** — nothing blocks. No owner-graded statement and no `[HARD]`
requirement is contradicted; the promise payload and the surfaced tension, which are the two things
this item exists to get right, are both clean. **item7-F1 is the one to fix in the spec text**,
because it is the difference between a sweep that can discharge SC2 and one that cannot: three terms
over an undeclared scope, recorded as a summary, would let the item close while a modeler still finds
the superseded shape in the two places S4 and S5 exist to catch. item7-F2 is the same defect class
Item 3's lens named twice — half an obligation carried — and item7-F3 is a dependency the spec can
name in one line.

### Spec-side disposition record (2026-08-14, same session)

Orchestrator ruling: **all three findings accepted as binding**, grade `[AGENT, orchestrator
2026-08-14]`, with the standing reason that a known-corrected requirement must not survive only as
an Open Question or the implement and audit agents execute the stale text. All three are therefore
**folded into the spec body**, and their Open Questions entries reduced to one-line
resolved-by-amendment pointers into the body.

- **item7-F1 → fixed in spec.** The sweep requirement now names Item 1's **five-term S1–S5**
  method with a path-cite to Appendix D, carries "adding a term is allowed, dropping one is not,"
  the DD5 scope with its written-down exclusions, "one row per raw hit; a summary does not discharge
  the criterion," and the pre-resolved S4 collision. The epic's "three-sweep" label is kept once,
  marked superseded, so the citation trail back to SC2 still resolves. A second requirement makes a
  **defined TEAx sweep scope** mandatory — plan picks the boundary, the sweep record must state it.
  The stale "three-sweep" phrase in the sweep-record Open Question was corrected in the same pass.
- **item7-F2 → fixed in spec.** SC1's second half is now an explicit `[NEED]` requirement: the filed
  entry is cited from the product-lens trail, and wiring that citation is this item's work. Which
  ledger carries it stays design's call, with the note that audit-F4's own ledger is archived and
  cited, not edited.
- **item7-F3 → fixed in spec.** The elaborate-cleanly requirement now names its execution terms:
  `SYSIDE_LICENSE_KEY` from `/home/reid/1cfe/agentic-mbse/.env` via `set -a; source`, the
  `/home/reid/1cfe/item7-rebuild-venv/bin/python` interpreter with `uv run` explicitly excluded,
  zero `no live syside license` skip lines as the only proof a run was licensed, and a **named
  residual** as the fallback if the license is unavailable at implement time — never a silent skip,
  never a criterion ticked unverified.

Gate unchanged: **DISPOSED**. The findings are now discharged in the spec body rather than deferred.
