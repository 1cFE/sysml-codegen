# Product-Lens Ledger — stop-reinventing-the-parser

Append-only. One block per run. A `BLOCK` stays in force until a later block cites its id and
records an authorized disposition.

---

## spec — 2026-08-16 — rev `26e19f9` / `.project/active/stop-reinventing-the-parser/spec.md`

Epic: ELABORATE-FIRST (`.project/backlog/epic_elaborate_first_architecture.md`)

Point (re-derived): When authored model text has no defined meaning under KerML, SysML v2, or
SysIDE's resolution, the product refuses with a diagnostic and never invents resolution behavior —
**and** the designs an engineer needs stay expressible, because a design search whose parameters
cannot be authored is as dead as one that returns a confident wrong number.
[source: `.project/product/P-003-no-workarounds-for-bad-models.md` (`[OWNER-VERBATIM, 2026-08-16]`)
bounded by `.project/product/P-001-design-search-free-variation.md` (`[OWNER-VERBATIM, 2026-08-13]`),
grade: **owner**]

Secondary point (inherited, epic): every consumed modeled value resolves to exactly one runtime
source across all bound consumers, **and an unsupported authored form fails loudly before
generation**. [source: `epic_elaborate_first_architecture.md:31-34` Critical Success Factor, grade:
**owner** (inherited SOURCE-IDENTITY mission invariant)]

Falsifier: the item would show the point violated if (a) a model form the language defines becomes
unauthorable with no stated replacement spelling that is verified to resolve, or (b) an authored
form that the product cannot honor continues to produce output silently, or (c) a scope decision the
census explicitly parked for the owner is landed carrying an owner-grade stamp the owner did not
give.

Findings:

- spec-F1 [DON'T] The supersession of `[DEF-OWNED-SIDEWAYS-REACH]`'s bound is stamped **[HARD]**
  (spec.md:138-141), but the question it answers is the one the census explicitly parked as *needing
  the owner* — "an author who writes `sibling_usage::attr` has named a usage SysIDE resolved but
  still has not named an occurrence: inside the ruling, or inside its carve-out?"
  (`…_syside-authority-fallback-census.md` §3.4, §10 Q1: *"Evidence cannot decide this — it is a
  scope question about the owner's own words … Needs the owner."*). The parser evidence that both
  spellings produce a pathless reference is genuinely `[HARD]`; the **scope ruling drawn from it** —
  that no usage-owned lane exists to carve out — is an agent inference riding on that fact. The
  2026-08-16 owner quote is general and is not recorded as an answer to §3.4. Capture-fidelity law 4
  forbids resolving a surfaced premise conflict silently in either direction.
  — source: `.project/research/…-census.md` §3.4 (WORK-grade evidence) against
  `P-003` + `BACKLOG.md:321-323` bound (`[OWNER 2026-08-16]`, **owner**) — disposition: **owner line
  required before design starts.** Either record the owner answering §3.4 by name, or regrade the
  consequence line to `[INFERRED]` and keep the `[HARD]` stamp only on the parser fact. If the
  outcome is "the product contract is intentionally changing," it files as an ADR (next free id
  **ADR-010**, `.project/product/INDEX.md:14`) per product-lens §2, not as a spec bullet.

- spec-F2 [DO] The spec asserts refusals but never obliges each refusal shape to carry a
  **replacement spelling that was verified to resolve.** Success Criterion 1 promises a diagnostic
  saying "what to write instead," yet for `sum(cells#(2).mass)` — aggregation over one indexed
  element — no supported spelling is named anywhere in the spec, and the Open Questions do not ask
  for one. Today's behavior (silently summing all three) must go; but refusing it with no authorable
  alternative removes a design a modeler can express today, which is the second half of the P-001
  failure mode. Same gap, smaller, for the definition-qualified-with-no-occurrence shape, which the
  spec itself calls "not mechanically fixable."
  — source: `P-001-design-search-free-variation.md` (**owner-verbatim** core; the "every refusal has
  a working alternative" obligation is my inference from it, `[INFERRED]`) — disposition: design must
  produce, per refusal shape, a replacement spelling proven against the licensed parser, **or**
  record the expressiveness loss explicitly and file it as a capability row. Add it as a success
  criterion; do not leave it to the diagnostic's wording.

- spec-F3 [DO] **Non-Goal "first-wins when one channel carries two output aliases" drops a
  loud-failure obligation, not just a cleanup.** The census records the observable: the second
  authored alias "survives in `graph.output_aliases` but produces no exit-point line, so no
  `<name>.json` is ever written. A name the modeller wrote produces no output, and nothing says so"
  (§5 Mechanism 5, L-13). The epic's Critical Success Factor requires an unsupported authored form to
  **fail loudly before generation**. M4 chose *determinism* between two aliases; it did not authorize
  *silence*. The spec's reason ("a recorded deliberate decision") disposes of the ordering question
  and not of the silence question.
  — source: `epic_elaborate_first_architecture.md:31-34` (**owner**, inherited) — disposition: the
  Non-Goal may stand as *scope*, but the spec must say the loud-failure obligation is unmet there and
  file a backlog row for it. Leaving it under an unqualified Non-Goal reads as settled and it is not.

- spec-F4 [DO] **P-003 is the durable home of this spec's own governing rule and is never cited.**
  The spec re-derives the rule from two raw owner quotes and from language clauses. P-003
  (`[OWNER-VERBATIM, 2026-08-16]`) already states it, already names `[DEF-OWNED-SIDEWAYS-REACH]` as
  its first application, and carries a "First application" section whose scope this item widens. An
  owner-grade promise being extended without the extending item naming it is how a ledger goes stale.
  — source: `.project/product/P-003-no-workarounds-for-bad-models.md` (**owner-verbatim**) —
  disposition: cite P-003 as the governing promise in Related Artifacts and in the Consequences
  block, and update P-003's "First application" section at close.

- spec-F5 [DO] The supersession bookkeeping is honest but **incomplete by one row.**
  `[ANCHORING-ARRAYED-DIAGNOSTIC]` (`BACKLOG.md:465`, filed at owner direction 2026-08-16) exists
  only to reconcile the two spellings `sum(comp_a::length)` vs `sum(comp_a.length)`. Under this spec
  the `::` spelling is refused outright, so that row's premise is gone. The spec records the
  supersession of P-002 and of `[DEF-OWNED-SIDEWAYS-REACH]`'s bound but not of this row.
  — source: `P-002-exact-owner-anchoring.md` "Known inconsistency, dispositioned"
  (`[OWNER, 2026-08-16]` acceptance) — disposition: add the row to the supersession list with its
  cause, or state why it survives.

- spec-F6 [DO/informational] **The P-002 supersession itself is handled correctly** — outcome kept
  and strengthened, mechanism retired, entry rewritten rather than deleted so the reasoning stays
  challengeable (spec.md:132-137). P-002 is `[AGENT] (ratified by owner)`, which product-lens §2
  makes challengeable by re-deriving against its recorded reasoning — exactly what the spec does with
  parser evidence and KerML clauses. **No finding on the supersession as such.** What is missing is
  the filing: an intentional product-contract change is the one disposition that files a decision
  record (product-lens §2), and no ADR id appears in the spec. Same disposition as spec-F1's second
  half: file **ADR-010** and have the rewritten P-002 row cite it.

- **Not findings, checked and cleared:** the inline sibling-dot form's acceptance is *consistent*
  with the owner rule, not an exception to it — P-003's test is "KerML, SysML v2, **or SysIDE**," and
  the form is exemplified normatively (Part 1 §7.24) and resolves in SysIDE, so the "true feature the
  spec doesn't consider" exception is never invoked and never needed. The spec also states plainly
  that SysIDE does not enforce KerML §8.4.4.6 and that we therefore enforce it ourselves, so the
  ownership transfer is declared, not smuggled. The parameter-group filename rule, the three
  off-route extraction modules, and the stellarator are correctly out of scope: the first is endorsed
  by `CLAUDE.md` as a product rule, the second cannot reach a generated package, and the third is
  held by an owner decision recorded at `BACKLOG.md:334`.

Smells fired:

- **Smell 7 (ownership of an invariant moves without saying so)** — *fires and is already disposed by
  the spec itself.* KerML §8.4.4.6 moves from "the parser's job" to "our job" for the inline sibling
  form. The spec names the move (`[INFERRED]`, spec.md:116-117). It must stay named in the design's
  refusal catalog, not evaporate into the implementation.
- **Smell 6 (a route passes only because it selects one interpretation)** — fires on the alias
  first-wins Non-Goal, spec-F3. `tests/unit/test_exit_point_aliases.py` pins the selection, not the
  authored meaning.

Gate: **DISPOSED (spec-F1, spec-F2, spec-F3, spec-F4, spec-F5, spec-F6)**

spec-F1 and spec-F2 are the two that must be answered before `/_my_design` produces anything
load-bearing: F1 because an owner-grade stamp is resting on an agent inference over a question the
census parked for the owner, and F2 because a refusal with no authorable alternative trades one
P-001 failure mode for the other. Neither is a proven contradiction of an owner statement, so the
stage proceeds — but F1 escalates to a **BLOCK** if the owner turns out not to have ruled on §3.4 and
the `[HARD]` stamp stays.

---

## spec (RERUN) — 2026-08-16 — rev 3 — `.project/active/stop-reinventing-the-parser/spec.md` (worktree; baseline `26e19f9` + uncommitted tree)

Epic: ELABORATE-FIRST (`.project/backlog/epic_elaborate_first_architecture.md`)

**Supersedes the prior block's acceptance of the P-002 retirement.** The prior block
(`spec — 2026-08-16 — rev 26e19f9`, findings spec-F1..spec-F6) read rev 2 under rev 2's own premise
that SysIDE discards the owning usage for every `::` reference. That premise is false
(`.project/research/20260816-205035_premise-audit-fallback-census.md` §3; owner resolution
`spec-review.md` Resolutions L1-1). Every prior finding whose force depended on the supersession is
re-dispositioned in `Resolves` below. Finding **ids from the prior block are never reused**; this
block mints `spec2-F*`.

Point (re-derived): When authored model text has no defined meaning under KerML, SysML v2, or
SysIDE's resolution, the product refuses with a diagnostic and never invents resolution behavior —
**and** the designs an engineer needs stay expressible, because a design search whose parameters
cannot be authored is as dead as one that returns a confident wrong number.
[source: `.project/product/P-003-no-workarounds-for-bad-models.md` (`[OWNER-VERBATIM, 2026-08-16]`)
bounded by `.project/product/P-001-design-search-free-variation.md` (`[OWNER-VERBATIM, 2026-08-13]`),
grade: **owner**]

Secondary point (inherited, epic, **original grade preserved**): every consumed modeled value
resolves to exactly one runtime source across all bound consumers, **and an unsupported authored
form fails loudly before generation**. [source: `epic_elaborate_first_architecture.md:31-34` Critical
Success Factor, grade: **owner** (inherited SOURCE-IDENTITY mission invariant)]

Third point (preserved, not superseded): one modeled source occurrence becomes exactly one runtime
source; where the exact owner cannot be selected, elaboration refuses **by name** rather than
choosing a candidate. [source: `.project/product/P-002-exact-owner-anchoring.md`, grade: **agent /
ratified** (`[AGENT] (ratified by owner, 2026-08-16)`) — challengeable by re-deriving against its
recorded reasoning, which is exactly what the premise audit did, and it came out **confirming** it]

Falsifier: the item would show the point violated if (a) a model form KerML/SysML v2/SysIDE define
becomes unauthorable **and is refused under a bad-model diagnostic** rather than a named
not-yet-supported one with a filed capability row, or (b) an authored form the product cannot honor
continues to produce output silently past close, or (c) either lane certifies on the other lane's
evidence, or (d) the "byte-identical output" gate is measured against a baseline no later reader can
reconstruct.

### The reversal — checked directly, no residue found

Searched rev 3 end to end for surviving rev-2 consequences. **Complete.** P-002 is preserved in
outcome *and* mechanism (`spec.md:63`, `199-201`, Success Criterion 3 at `162-163`); the blanket `::`
refusal, the P-002 supersession, ADR-010, and the model re-authoring scope are all in Non-Goals
(`spec.md:216-221`); the false premise is recorded as a named error rather than deleted
(`spec.md:54-66`), which is the correct capture-fidelity law-3 shape for a correction; the census's
`::` addendum is explicitly marked wrong and demoted from contract to suspect list
(`spec.md:203-214`); ADR-010 is unminted (`.project/product/INDEX.md:14` still reads "Next free id:
**ADR-010**"). The `[HARD]` stamps that remain (`spec.md:180-186`) are parser and spike facts, not
scope rulings — the exact defect the prior spec-F1 named is gone rather than moved.

Also checked and cleared: the uncommitted worktree's fixture-comment rewrites
(`def_qual_sibling_scope`, `def_qual_two_occ_above`, `u3_usage_qual_multi_occ`) encode the
**definition-owned** lineage-miss refusal, which the premise audit independently affirms
(`…premise-audit…md:189-194`). They are not residue of the false premise and they do not re-author
any model to remove `::` (comment-only edits), so Non-Goal 3 holds.

Findings:

- spec2-F1 [DO] **Rev 3 refuses a form the language and the parser both support, under the
  bad-model banner.** A5 refuses `sum(cells#(2).mass)` while recording that the parser *does* report
  the index segment and that the real cause is "no indexing support anywhere"
  (`spec.md:104`, `110-111`). That is a **valid-but-unsupported** refusal, not an ill-formed model,
  and P-003 does not authorize the second label for the first case — P-003's test is what
  KerML/SysML v2/**SysIDE** support, and this form passes it. Success Criterion 4 then promises every
  refusal names "what the model must supply instead" (`spec.md:164-166`), which for this shape
  cannot be honored and by A5's own text does not exist. The epic already carries the correct
  classification by name — "the valid-but-unsupported indexed-expression limitation"
  (`epic_elaborate_first_architecture.md:530`) — and rev 3 neither cites it nor inherits it.
  — source: `P-003` (**owner-verbatim**) for the classification boundary;
  `epic_elaborate_first_architecture.md:530` (**agent / ratified**, inherited) for the existing row —
  disposition: **DISPOSE.** Rev 3 must split the two refusal classes: an ill-formed-model diagnostic
  says what to write instead; a not-yet-supported diagnostic says the form is valid, that we do not
  implement it yet, and names the capability row. Success Criterion 4's wording must be narrowed to
  the bad-model class, and Success Criterion 8's capability row (`spec.md:174`) is the named home.
  **On the question of whether filing is enough: it is.** P-001's own entry files its unbuilt half as
  `[ACAUSAL-RELATIONS-CAPABILITY]` and calls that "filed, not forgotten"
  (`P-001-design-search-free-variation.md:99-106`) — a named capability row is the ledger's
  sanctioned disposition for an expressiveness gap, not an evasion. And nothing correct is lost:
  today's behaviour summed all three occurrences (`spec.md:111`), so a wrong number is being removed,
  the same "nothing that worked was lost" shape P-002 records. **Escalates to BLOCK** only if the
  item closes with the row unfiled or with the refusal shipped under a bad-model diagnostic.

- spec2-F2 [DO] **The alias-silence obligation is named honestly but left ungated — carries prior
  spec-F3 forward.** Rev 3 states the unmet obligation plainly and refuses to call the deferral clean
  (`spec.md:146-148`), which discharges capture-fidelity law 4's surfacing duty. It then says "File
  the gap" inside a Non-Goals bullet, with **no success criterion, no owner, and no filed row** —
  compare A5, whose identical situation got Success Criterion 8. Grep confirms no
  backlog row exists for it (`.project/backlog/BACKLOG.md`). A sentence in a spec that closes is not
  a filing; when the item closes the epic's loud-failure invariant goes back to being violated
  silently, which is the exact state the invariant forbids.
  — source: `epic_elaborate_first_architecture.md:31-34` (**owner**, inherited — original grade
  preserved from the prior block's spec-F3) — disposition: **DISPOSE.** Add a success criterion
  mirroring SC8: the alias-silence gap is filed as its own backlog row with the observable
  (second authored alias produces no file, nothing says so) and its `pipeline.py:226` site. Scope may
  stay a Non-Goal; the filing may not.

- spec2-F3 [DO] **Specifying against a dirty tree is a defect in the contract, and this tree is
  another item's uncertified output.** The baseline is "`26e19f9` **plus the uncommitted worktree**"
  (`spec.md:7`, `73-80`). Measured: 22 changed files under `src/`+`tests/`, including
  `elaboration/elaborate.py` (+90/-…), split across index *and* worktree (several `MM` entries), so
  the baseline is a three-way state (HEAD / index / worktree) that no later reader can reconstruct
  and no sha names. Two consequences bite: Success Criterion 4's "good models generate byte-identical
  output" (`spec.md:164`) has no reference bytes to be identical *to*; and the tree is the
  `self-binding-replacement` repair set, which the epic records as **not certified** with "the final
  three-repository repair set remains uncommitted" as a delivery finding
  (`epic_elaborate_first_architecture.md:552-562`). The epic's own remedy for exactly this situation
  is Item 1's rule — dirty trees go to named branches, working branches clean at base
  (`…:165-168`).
  — source: `epic_elaborate_first_architecture.md:165-168` and `:552-562` (**agent / ratified**) —
  disposition: **DISPOSE.** Before design starts, stamp the baseline: commit or branch the worktree
  and name the sha in `spec.md:7`. If the sibling's certification is a prerequisite rather than a
  parallel, say so as a dependency instead of absorbing its unlanded work as "Lane A work in
  progress."

- spec2-F4 [DO] **Withdrawing the blast-radius number is right; leaving the re-derivation without a
  scope rule is the hole.** Deferring the *measurement* does not hollow the contract — rev 3 keeps a
  concrete, enumerated scope floor (A1–A5, B1–B8, each with a file:line site and a per-site verdict),
  and re-deriving a number that was provably wrong beats freezing it (`spec.md:212-214`, SC6 at
  `169-170`). What is missing is the rule for the re-derivation's *outcome*: Success Criterion 2 says
  "every Lane B site," but the site set is the provisional table, and nothing says what happens if
  re-derivation finds a semantic site outside A1–A5/B1–B8 — in scope, or surfaced. The epic's own
  breadth rule for this is explicit: a shape outside the inherited set "is an owner question, not
  silent scope growth" (`epic_elaborate_first_architecture.md:571-573`).
  — source: `epic_elaborate_first_architecture.md:571-573` (**agent / ratified**) — disposition:
  **DISPOSE.** Add one line to SC6: a site the re-derivation finds outside the tables is added to its
  lane with its category, or surfaced to the owner; it is never absorbed silently and never dropped.

- spec2-F5 [DO] **P-003's own ledger entry is left stale by this item — carries the unfixed half of
  prior spec-F4.** Rev 3 now cites P-003 as the governing promise (`spec.md:199-201`, Related
  Artifacts `:249-250`), which fixes the citation half. The second half is not carried: P-003's
  "First application" section states the bounded definition-owned removal "landed on 2026-08-16"
  (`P-003-no-workarounds-for-bad-models.md:41-46`), while rev 3's A3 records that the descendant
  search "is still present and still runs for every other caller" (`spec.md:76-79`, `102`). An
  owner-verbatim promise entry that overstates what landed is how the ledger goes stale, and this
  item is the one that knows better.
  — source: `.project/product/P-003-no-workarounds-for-bad-models.md` (**owner-verbatim** entry;
  the "First application" section is its agent-written status text) — disposition: **DISPOSE.** Add
  a close-time obligation: reconcile P-003's First-application section against A3's shipped outcome,
  and record the pending independent audit's result there.

- spec2-F6 [DO/informational] **Two lanes under one completion authority: checked, and the proof
  obligations are genuinely separable and separately sufficient.** No finding on the split itself.
  The separation is stated as a rule ("must not be certified by one another's evidence",
  `spec.md:86-94`), the two obligations are different *kinds* of proof (real-model-through-real-parser
  vs forced-failure), and Success Criterion 2 forecloses the one real cross-certification path by
  name — "proved by a forced-failure test, not by a corpus run" (`spec.md:160-161`) — which is the
  path a corpus-green Lane A run would otherwise open. Success Criteria 1/5 are Lane A, 2 is Lane B,
  and neither is satisfiable by the other's evidence. The confident-wrong-number risk P-001 cannot
  tolerate lives in Lane B (B3/B4/B5 drop references before the graph boundary), and it is the lane
  whose criterion is the strictest. **One residual, folded into spec2-F4:** "every Lane B site" is
  quantified over a table the spec itself calls provisional, so the strictness is only as good as the
  re-derived inventory. Open Question 5's assumption that Lane B has "no expected output change"
  (`spec.md:235-236`) is unproven for B6 and B7 and should be tested, not assumed, in design.

- **Not findings, checked and cleared:** the P-002 preservation (see The reversal above);
  `[ANCHORING-ARRAYED-DIAGNOSTIC]` (`BACKLOG.md:465`), whose premise the prior block correctly said
  rev 2 destroyed and which rev 3's reversal **restores intact** — it needs no supersession row and
  correctly gets none; the `sum` fan-out kept as language behaviour (`spec.md:118-122`), which is a
  restriction narrower than the language, not an invention; the withdrawal of rev 2's ban on
  candidate enumeration (`spec.md:192-194`), correctly regraded `[INFERRED]` as an implementation
  technique rather than a contract term; and the inline sibling form's acceptance, unchanged from the
  prior block's clearing.

Smells fired:

- **Smell 6 (a route passes only because it selects one interpretation)** — still fires on the alias
  first-wins Non-Goal, now spec2-F2. `tests/unit/test_exit_point_aliases.py` exists at HEAD and pins
  the selection, not the authored meaning. Unchanged from the prior block; escalation is not
  resolution, and rev 3 escalates it without disposing of it.
- **Smell 7 (ownership of an invariant moves without saying so)** — fires and remains disposed by the
  spec itself: KerML §8.4.4.6 moves from the parser's job to ours for the inline sibling form, and
  rev 3 keeps it named and `[INFERRED]` (`spec.md:195-198`). It must stay named in the design's
  refusal catalog.

Gate: **DISPOSED (spec2-F1, spec2-F2, spec2-F3, spec2-F4, spec2-F5, spec2-F6)**

Rev 3 is a materially safer contract than rev 2 and design may start from it. spec2-F3 should be
cleared **before** design starts, because it costs one commit and every later byte-identity claim
depends on it. spec2-F1 and spec2-F2 are the two that decide whether this item leaves the product
more honest than it found it, and both escalate to **BLOCK at close** if the item ships with an
unfiled capability row, an unfiled alias-silence row, or a valid-but-unsupported refusal wearing a
bad-model diagnostic.

Resolves:

- spec-F1: **FIXED** — authority: owner (`spec-review.md` Resolutions L1-1/L2-1, `[OWNER 2026-08-16]`
  "rework, follow the reviewer") — basis: the `[HARD]`-stamped scope ruling the finding objected to
  is withdrawn with rev 2's premise; census §3.4's parked question is now answered in the
  *preserving* direction by the owner's recorded resolution, and rev 3's surviving `[HARD]` stamps
  carry only live-verified parser facts. The finding's escalation-to-BLOCK condition can no longer
  trigger — its subject no longer exists in the work.
- spec-F2: **FIXED (in part; remainder carried as spec2-F1)** — authority: the finding's own recorded
  disposition — basis: rev 3 took the disposition's second branch exactly as written — the
  expressiveness loss is recorded explicitly (`spec.md:104`, `110-111`), a capability row is required
  rather than a bug fix, and it is a success criterion (SC8, `spec.md:174`), not diagnostic wording.
  The remainder is the refusal-class label, filed fresh as spec2-F1.
- spec-F3: **FIXED (in part; remainder carried as spec2-F2)** — authority: `epic…md:31-34`
  (**owner**, grade unchanged) — basis: the disposition's honesty half landed verbatim in intent
  (`spec.md:146-148`); the filing half did not, and no backlog row exists.
- spec-F4: **FIXED (in part; remainder carried as spec2-F5)** — authority: the finding's own recorded
  disposition — basis: P-003 is now cited as the governing promise in both required places; the
  close-time update to P-003's "First application" section is not carried into rev 3.
- spec-F5: **FIXED** — authority: owner (`spec-review.md` Resolutions L1-1) — basis: the finding
  existed only because rev 2's blanket `::` refusal destroyed
  `[ANCHORING-ARRAYED-DIAGNOSTIC]`'s premise. Rev 3 restores the premise, so the row survives
  unchanged and correctly appears in no supersession list. **The finding is void by reversal, not
  by compliance.**
- spec-F6: **INTENDED-CHANGE withdrawn** — authority: owner (`spec-review.md` Resolutions L2-1,
  "the proposed P-002 supersession, ADR-010 … are all withdrawn") — basis: no product-contract change
  occurs, so the one disposition that files a decision record does not apply. ADR-010 stays unminted
  (`.project/product/INDEX.md:14`). **This is the finding whose acceptance this rerun supersedes:**
  the prior block judged the P-002 supersession "handled correctly" and asked only that it be filed
  as an ADR. It was handled correctly *given rev 2's premise*, and that premise was false — the
  supersession should never have been proposed. Cause of the prior error: the block derived its
  reading of the parser's behaviour from the WORK's own census addendum, which product-lens §1 rule 2
  forbids treating as a SOURCE, and no independent parser check was run.

---

## spec (RERUN) — 2026-08-16 — rev 4 — `.project/active/stop-reinventing-the-parser/spec.md`

Epic: ELABORATE-FIRST (`.project/backlog/epic_elaborate_first_architecture.md`)

Point (re-derived): Codegen preserves SysIDE's resolved declaration evidence through exact modeled
occurrence identity to runtime output. When KerML, SysML v2, and SysIDE do not supply enough modeled
authority, it refuses by name instead of reconstructing identity from names, proximity, order, or
uniqueness. Valid but unimplemented forms are filed as capability gaps, not blamed as bad models.
[source: `P-003-no-workarounds-for-bad-models.md` (**owner**),
`P-002-exact-owner-anchoring.md` (**agent / ratified**), bounded by
`P-001-design-search-free-variation.md` (**owner**)]

Falsifier: the spec permits a runtime source or occurrence to be selected from textual names,
nearest or sole candidates, traversal order, or other non-modeled evidence; silently drops parser
evidence; or labels a parser-supported but unimplemented form as ill-formed.

Findings: none.

Smells:

- **Smell 6 — a route passes only because it selects one interpretation:** still present in the
  shipped output-alias first-wins behavior. Rev 4 disposes it for this stage by naming the silent
  loss, keeping it out of implementation scope, and gating item closure on a separately owned
  backlog filing (`spec.md:113-115,143-144`). It becomes unresolved again if the item closes without
  that filing.
- **Smell 7 — ownership of an invariant moves without saying so:** cleared. Rev 4 assigns declaration
  identity to SysIDE and concrete occurrence materialization to codegen (`spec.md:26-30,157-161,
  172-174`).

Gate: **CLEAR**

Resolves:

- spec2-F1: **FIXED** — authority: owner (`P-003`) — basis: A5 is valid-but-unimplemented, carries
  an unsupported-capability diagnostic, and requires its own backlog row.
- spec2-F2: **FIXED** — authority: owner (ELABORATE-FIRST Critical Success Factor) — basis: alias
  silence is named and independently gated for backlog ownership before close.
- spec2-F3: **FIXED** — authority: agent / ratified — basis: rev 4 names immutable committed
  baselines, excludes dirty worktrees, and blocks design until the predecessor lands on named
  descendant commits.
- spec2-F4: **FIXED** — authority: agent / ratified — basis: A1-A6/B1-B10 plus the checked historical
  reconciliation gate make omission visible.
- spec2-F5: **FIXED** — authority: owner (`P-003`) — basis: close reconciles P-003's agent-written
  application status while preserving its owner-verbatim promise.
- spec2-F6: **FIXED** — authority: agent — basis: every row carries its own proof form and neither
  lane can certify the other.

---

## spec (RERUN) — 2026-08-16 — rev 4 + P-004 — `.project/active/stop-reinventing-the-parser/spec.md`

Epic: ELABORATE-FIRST (`.project/backlog/epic_elaborate_first_architecture.md`)

Point (re-derived): The product uses SysIDE to parse models, walks the resolved semantic tree to
reconstruct the modeled math, and emits that math through TEAx Python. Unresolved identity is never
replaced by names, proximity, ordering, uniqueness, manual inputs, or another fallback. [source:
`P-004-product-identity-parse-walk-emit.md` and `P-003-no-workarounds-for-bad-models.md`, grade:
**owner**]

Falsifier: the spec permits parser evidence to be discarded or reconstructed heuristically, permits
an unresolved reference to become a manual or runtime stub, or allows positive proof to stop before
the modeled source reaches its generated runtime consumers.

Findings: none. Rev 4 states the parse → semantic walk → TEAx obligation, assigns parser and
occurrence authority explicitly, enumerates the fallback sites to remove, and requires public
mutation evidence beyond internal graph assertions. P-002 remains the exact-occurrence companion;
P-003 remains the refusal rule.

Smells:

- **P-004's owner-named manual-fallback/workaround smell:** does not fire against the spec.
- **Smell 6 — a route passes only because it selects one interpretation:** remains only in the
  out-of-scope output-alias behavior and is disposed for this stage by its close-gated backlog filing.
- **Smell 7 — ownership of an invariant moves without saying so:** clear. SysIDE owns resolved
  declarations; codegen owns modeled concrete-occurrence materialization.

Gate: **CLEAR**. The prior rev-4 CLEAR remains valid; P-004 makes explicit the same product
obligation rev 4 enforces.

---

## design — 2026-08-16 — rev `7b29d8b` / `.project/active/stop-reinventing-the-parser/design.md` (worktree)

Point (re-derived): The product must consume the semantic classifications SysIDE already
establishes, preserve them through the AST walk, and emit the resulting math through TEAx. A
downstream reconstruction of parser-owned meaning is not an exact-evidence implementation.
[source: `.project/product/P-004-product-identity-parse-walk-emit.md`, grade: **owner**]

Falsifier: the design derives whether a reference belongs to the standard library from paths,
names, normalized origins, or another downstream comparison when SysIDE already provides that
classification.

Findings:

- design-F1 [DON'T] D6 recreates standard-library classification by comparing normalized document
  origins even though SysIDE assigns each loaded document `DocumentTier.StandardLibrary` or
  `DocumentTier.Project`. Because this classification decides whether an AST reference is
  discarded, the consumer would reconstruct parser-owned meaning and could drop or retain the wrong
  dependency. Revise D6/B5 to consume `DocumentTier` directly and treat missing or unknown tier as
  `SemanticEvidenceError`; keep document-origin handling only for source-location metadata such as
  B10. — source: `.project/product/P-004-product-identity-parse-walk-emit.md` (**owner**) and
  `.venv/lib/python3.12/site-packages/syside/_loading.py:63-68,499-502` (`[HARD]` platform behavior)
  — disposition: **BLOCK**

Smells:

- **Smell 2 — a consumer compensates for something the producer or platform claims to guarantee:**
  fires at design-F1. SysIDE already supplies the classification D6 proposes to reproduce.
- **Smell 7 — the proposed solution changes who owns an invariant without saying so:** fires at the
  same site. D6 assigns standard-library classification to an agentic origin predicate without
  acknowledging that SysIDE owns it through `DocumentTier`.

Gate: **BLOCKED (design-F1)**

---

## design — 2026-08-16 — rev 2 / `.project/active/stop-reinventing-the-parser/design.md` (worktree; baseline `7b29d8b`)

Point (re-derived): SysIDE's resolved semantic classifications are authoritative through the AST
walk; missing evidence must cause named refusal rather than downstream reconstruction or fallback.
[source: `.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`, grade: **owner**]

Falsifier: a project document named `SI` is discarded by name/path/origin, or a reference with
missing document-tier evidence reaches generated TEAx output instead of refusing.

Findings: none.

Smells:

- **Smell 2 — a consumer compensates for something the producer or platform claims to guarantee:**
  clear. D6 consumes `element.document.document_tier` directly, retains Project and External
  references, and removes every QN/path/origin classifier (`design.md:314-336`); SysIDE exposes the
  element document, `BasicDocument.document_tier`, and the closed `DocumentTier` enum
  (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:1300,1420,5676-5690`).
- **Smell 7 — the proposed solution changes who owns an invariant without saying so:** clear. The
  responsibility table explicitly leaves metatype truth and `DocumentTier` with SysIDE,
  semantic-evidence preservation with agentic, and concrete-occurrence materialization with
  codegen (`design.md:476-490`).

Gate: **CLEAR**

Resolves:

- design-F1: **FIXED** — authority: owner (P-004) — basis: Revision 2 consumes SysIDE's public
  `DocumentTier` directly, fails on missing or unknown tier, and confines document origin to
  source-location evidence (`design.md:42-54,314-336,460-471`).

---

## design (REVISION 3 FINAL REVIEW) — 2026-08-16 — rev 3 / `.project/active/stop-reinventing-the-parser/design.md`

Point (re-derived): The product uses SysIDE to parse models, walks its resolved semantic tree to
reconstruct the modeled math, and emits that math through TEAx. Missing identity or classification
must cause named refusal, never downstream reconstruction, guessing, or manual fallback. [source:
`.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`, grade: **owner**]

Falsifier: the design derives a referent, metatype, document tier, owner occurrence, or calculation
producer from names, paths, proximity, candidate count, or declaration order; or incomplete
semantic evidence reaches an `InstanceGraph`, snapshot, or generated package.

Findings: none.

Smells:

- **Smell 2 — a consumer compensates for something the producer or platform claims to guarantee:**
  clear. D5/D6 consume SysIDE's resolved targets, mapped metatypes, and `DocumentTier` directly. D2
  materializes concrete occurrence identities that SysIDE does not provide, rather than
  reconstructing evidence SysIDE claims to provide.
- **Smell 7 — the proposed solution changes who owns an invariant without saying so:** clear. The
  responsibility table explicitly leaves metatype truth and document classification with SysIDE,
  semantic-evidence preservation with agentic-mbse, and concrete-occurrence materialization with
  codegen. Revision 3 also confines closed owner-kind validation to containment-address
  construction while preserving existing attachment and formal-domain ownership.

Gate: **CLEAR**

Resolves:

- design-F1: **FIXED (remains fixed)** — authority: owner (`P-004`) — basis: Revision 3 retains
  direct use of SysIDE's public `DocumentTier`, refuses missing or unknown tier evidence, and
  forbids qualified-name, path, origin, or package-name classification.

---

## design-r4-final — 2026-08-16 — rev `.project/active/stop-reinventing-the-parser/design.md` (Revision 4 worktree)

Point (re-derived): The product uses SysIDE to parse models, walks its resolved semantic tree to
reconstruct the modeled math, and emits that math through TEAx. Missing identity or classification
causes named refusal, never downstream reconstruction, guessing, or manual fallback. [source:
`.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`, grade: **owner**]

Falsifier: the design derives a referent, metatype, document tier, owner occurrence, or calculation
producer from names, paths, proximity, candidate count, or declaration order; or incomplete
semantic evidence reaches an `InstanceGraph`, snapshot, or generated package.

Findings: none.

Smells:

- **Smell 2 — a consumer compensates for something the producer or platform claims to guarantee:**
  clear. D5/D6 consume SysIDE's resolved targets, mapped metatypes, and `DocumentTier` directly. D2
  materializes concrete occurrence identities that SysIDE does not supply. B10 permits deletion of
  the sole-glob compensation only after the retained probe proves direct document origin total.
- **Smell 7 — the proposed solution changes who owns an invariant without saying so:** clear. The
  responsibility table explicitly assigns parser truth to SysIDE, evidence preservation to
  agentic-mbse, occurrence materialization to codegen, and artifact provenance to the verification
  records. Revision 4 also names the new `C_prod` → `F_final` → `C_evidence` ownership boundary.

Gate: **CLEAR**

Resolves:

- design-F1: **FIXED (remains fixed)** — authority: owner — basis: Revision 4 retains direct
  `DocumentTier` use, named refusal for missing or unknown tier evidence, and the prohibition on
  name/path/origin classification.

---

## audit — 2026-08-17 — rev A_final `1804827cb2cc877b3c0bc74309bd3470fb2ee90b` / C_prod `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e` / F_final `4fdd78f53334e5a9bcd695259b27afeb0b347f62` / C_evidence `58495607bdf140f1f716aafb95f7122228a4bf52` / artifacts `/tmp/stop-parser.QVJIIP/artifacts/final-identities-v5`

Point (re-derived): Use SysIDE's resolved semantic tree as the model interpretation, preserve exact source-occurrence identity through TEAx Python emission, and refuse unresolved or ambiguous references instead of reconstructing or choosing them. [source: `.project/product/P-004-product-identity-parse-walk-emit.md` and `P-003-no-workarounds-for-bad-models.md`, grade: owner; exact-occurrence outcome bounded by `P-002-exact-owner-anchoring.md`, grade: agent/ratified]

Falsifier: On licensed live and relocated-snapshot routes, mutating one modeled source does not change every and only its bound TEAx consumers, or incomplete semantic evidence reaches a graph, snapshot, or package instead of a named diagnostic.

Findings:

- audit-F1 [DON'T] C_prod declares one canonical scalar type map in `core/type_mapping.py`, but exact elaboration retains a second four-entry literal map in `_feature_python_type`; extraction and graph materialization therefore require manual synchronization. Falsifier: add or change one supported scalar in the canonical table and elaborate a feature of that type; extraction accepts it while exact elaboration rejects or types it differently. — `P-004-product-identity-parse-walk-emit.md` (AGENT/INFERRED) — disposition: use the canonical map in exact elaboration and extend the no-copy guard to that path.
- audit-F2 [DON'T] Fusion retains two manually synchronized model trees and compensates with a test that strips one tree's `library/` prefix before byte comparison, while the new live/snapshot TEAx and mutation proofs select only `models/`. Falsifier: change only the corresponding binding under `exploration/ife_e2e/models`; the selected acceptance tests remain green while the compensating cross-tree gate alone detects the split. — `P-002-exact-owner-anchoring.md` and `P-004-product-identity-parse-walk-emit.md` (AGENT/INFERRED) — disposition: designate one canonical model tree and derive the other, or run the customer-shaped proof against both without layout normalization.

Fired smells:

- Smell 1, **two representations must be manually kept synchronized** — both the scalar type maps and Fusion model trees.
- Smell 3, **a special category exempts unchanged user-visible meaning** — `strip_library=True` normalizes one duplicate's special layout.
- Smell 4, **correctness depends on downstream knowledge of an internal representation** — the divergence gate knows and rewrites the two trees' directory layouts.
- Smell 6, **a test passes only because it selects one duplicate, one route, or one interpretation** — Fusion's new acceptance tests hard-select `models/`.

Gate: DISPOSED (audit-F1, audit-F2; no owner/HARD contradiction found)

---

## audit2 — 2026-08-17 — rev f4d7351 / 1af5705 / 2228c60

Point (re-derived): Use SysIDE's resolved semantic tree as the model interpretation, preserve exact
modeled-occurrence identity through emitted TEAx Python, and refuse incomplete or ambiguous evidence
instead of selecting by names, order, proximity, or uniqueness. [source:
`.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`, grade: owner; exact-occurrence companion
`.project/product/P-002-exact-owner-anchoring.md`, grade: agent/ratified]

Falsifier: On either maintained Fusion model root, a licensed live or v6-snapshot run binds a modeled
source to different consumers, a source mutation fails to move every and only its bound TEAx results,
or incomplete evidence reaches a package instead of an exact reference-and-location diagnostic.

Findings: none.

Smells:

- Smell 1, **two representations must be manually kept synchronized**, still fires mechanically on
  Fusion's two byte-identical model roots. It is disposed for this judgment by independently parsing,
  generating, snapshot-roundtripping, TEAx-executing, and mutation-proving both roots in their actual
  layouts.
- Smell 3, **a special category exempts unchanged user-visible meaning**, remains only in the
  redundant cross-tree byte-sync guard's `library/` layout mapping. No semantic or runtime verdict
  consumes that normalization; both layouts are exercised directly.
- Smell 4, **correctness depends on downstream knowledge of an internal representation**, is clear.
  The customer proofs use each real root, public graphs, generated packages, and TEAx results; the
  normalized sync view is not their oracle.
- Smell 5, **a baseline or compatibility requirement preserves contradictory behavior**, fires on
  retained L-13 output-alias silence. It is visibly disposed outside this item at
  `[OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE]`; the evidence ledger does not relabel it as correct.
  Nonzero project baselines are exact-hash-locked and explicitly recorded as non-green.
- Smell 6, **a test passes only because it selects one duplicate, route, or interpretation**, is
  clear for the audited claim. Both Fusion roots and both live/snapshot routes execute, and the
  focused 23-test Fusion battery has zero skips.

Gate: CLEAR

Resolves:

- audit-F1: FIXED — authority: AGENT/INFERRED — basis: exact elaboration now consumes
  `QUALIFIED_SYSML_TO_PYTHON`, a derived view of the canonical map, with a kept no-second-map guard.
- audit-F2: FIXED — authority: AGENT/INFERRED — basis: both maintained Fusion roots now run the
  customer-shaped live/snapshot TEAx and every-and-only mutation proofs directly, without layout
  normalization; the pinned artifact audit reports all four evidence groups PASS.

---

## audit3 — 2026-08-17 — rev A `2171016d3e3e0805525aa4cf787c55c6293dd00c` / C `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6` / E `588d5f7c9013d98c838a376ab9c69c95ef444649` / F `028f98741a2aea7c238beed961402857af82d15f`

Point (re-derived): Resolve every modeled reference from SysIDE's exact semantic tree to its concrete source occurrence, carry that identity unchanged through live and snapshot TEAx generation, and refuse unsupported or incomplete evidence by name before graph, snapshot, or output. [source: `.project/product/P-003-no-workarounds-for-bad-models.md` and `.project/product/P-004-product-identity-parse-walk-emit.md`, grade: owner; exact-occurrence companion `.project/product/P-002-exact-owner-anchoring.md`, grade: agent/ratified]

Falsifier: A valid public SysML model can move the same `#(...)` reference into another expression-bearing feature and thereby reach a graph, snapshot, or package with the index erased, or live and snapshot routes bind it differently.

Findings:

- audit3-F1 [DON'T] Indexed-source refusal is limited to input-directed `FeatureChainExpression` features. In a licensed public-route probe, moving `cells#(2).mass` into a computed attribute under `cells : Cell[1]` bypassed the refusal, built a zero-diagnostic graph, and aliased the out-of-range reference to `cells[0].mass`. The two detection sites also identify SysIDE's exported `IndexExpression` through `type(...).__name__` instead of the exact metatype adapter. The same user-visible reference therefore changes meaning by feature category and depends on downstream knowledge of SysIDE's runtime representation. Falsifier: keep a licensed live-and-snapshot test for an indexed reference through a computed attribute; both routes must stop before graph construction with one `SI_INDEXED_SOURCE_UNSUPPORTED` diagnostic carrying the authored reference and location. — `.project/product/P-003-no-workarounds-for-bad-models.md` and `.project/product/P-004-product-identity-parse-walk-emit.md` (OWNER) — disposition: BLOCK

Smell search: Smells 3 and 4 fire in audit3-F1. Smell 1 has no product-source synchronization obligation: both maintained Fusion trees are independently parsed, generated, snapshot-roundtripped, TEAx-executed, and mutation-proved. Smell 5's recorded nonzero baselines are explicitly non-green and do not preserve the indexed-reference behavior. Smell 6 is clear because both model roots and both public routes run, with exact channel and every-and-only mutation assertions.

Gate: BLOCKED (audit3-F1)

---

## design-rev5 — 2026-08-17 — design.md Revision 5 draft (code facts at C_prod `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6` / A_final `2171016d3e3e0805525aa4cf787c55c6293dd00c`)

Point (re-derived): The product is three steps and nothing else — parse the models with a SysMLv2
parser, walk the parser's resolved tree to reconstruct the math, write that math into TEAx Python.
Every modeled reference arrives in generated math meaning what the model wrote, decided from the
parser's own resolved evidence. A reference the toolchain cannot honor is refused by name; it is
never quietly turned into a different expression and never patched by a manual fallback. [source:
`.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`, grade: **owner**; exact-occurrence
companion `.project/product/P-002-exact-owner-anchoring.md`, grade: agent/ratified]

Falsifier: the design shows a route where a parser-resolved reference reaches the graph, snapshot,
or package with its meaning changed and no diagnostic; or a decision rule reading something other
than resolved parser evidence (Python class names, qualified-name prefixes, positional /
sole-candidate / nearest-ancestor election); or a closure argument with a hole, so a newly authored
expression-bearing site carries an unhonorable reference past the refusal.

Findings:

- design-rev5-F1 [DO] The mechanical closure condition cannot observe the `audit3-F1` defect class.
  Its AST discovery set is raw *reads* — `.operands`, `.referent`, `.target_feature`,
  `.chaining_features`, and runtime metatype-name dispatch. The audited defect was not a read; it
  was a consumer receiving a permissive fact and **ignoring** its `has_index_segment` field
  (design.md:78). A dropped field is invisible to a selector scan. The real closure for that class
  is the unrepresentable-state design (`IndexedReferenceUse` carries no path; the resolver signature
  admits only `ExactReferenceUse`), and D5 explicitly leaves an opening beside it: the permissive
  `ResolvedSemanticReferenceFact` survives, and `extract_feature_refs` / `feature_reference_facts` /
  `feature_chain_facts` "may remain for non-codegen compatibility" (design.md:381-384). Agentic's own
  live consumers of those index-flag-bearing facts —
  `agentic-mbse/src/agentic_mbse/sysml/aggregation.py:251-271` (a `FeatureChainNode` /
  `SingletonTerm` pair carrying `has_index_segment` that a consumer may drop) and
  `sysml/binding.py:164` — are named nowhere in the design, and the closure matrix's consumer list
  omits aggregation entirely. Verified at A_final: they are held off codegen's public route today
  only by the `hierarchy_resolver.py` reachability exclusion, which is a route fact, not a shape
  guarantee. Falsifier: an agentic-side proof that a permissive chain fact with an index cannot
  produce an index-free path on any route the design counts as live, or deletion of the permissive
  index-bearing fact API from the production surface. — `.project/product/P-004` (owner) applied via
  my inference about closure scope (`[AGENT]/[INFERRED]`) — disposition: DISPOSE — record the two
  agentic modules with their route state and proof in agentic's ownership manifest, or delete the
  permissive fact API on the production route; not a blocker at the current route boundary.

- design-rev5-F2 [DO] The consumer backstop's stated benefit has no observable, so the layer it
  guards degrades untested. D7 claims the per-consumer exhaustive branch "makes an omitted preflight
  category a failing test rather than a silent de-indexing route" (design.md:475-478). But the
  backstop raises the same `SI_INDEXED_SOURCE_UNSUPPORTED` the pre-graph inventory raises, and the
  closure matrix asserts only "the exact public diagnostic" (design.md:1080). An omitted preflight
  row therefore yields an identical **passing** test. The same asserted-not-proved pattern appears in
  the matrix's deep-literal-override row, where indexed refusal is marked "not an expression route"
  (design.md:1078) with no case showing a redefinition relationship path cannot carry an index — the
  exact form of assumption that produced `audit3-F1`. Product outcome stays correct (both layers
  refuse), so this is closure-argument integrity, not a contract violation. Falsifier: a test that
  distinguishes which layer refused (e.g. asserting the pre-graph inventory refused before any
  consumer ran), plus one case fixing the deep-override index claim. —
  `.project/product/P-003` (owner) applied via my inference (`[AGENT]/[INFERRED]`) —
  disposition: DISPOSE — add the layer-distinguishing assertion and the deep-override case to the
  closure matrix in the replacement plan.

Smells:

- **Smell 2 — a consumer compensates for something the producer or platform claims to guarantee:**
  **fires, disclosed.** Two compensations are stated in the open with their reasons. The resolver's
  runtime concrete-value check exists "because the repository's full static type lane is not
  currently a green gate" (design.md:346-348) — an honest compensation for a platform guarantee that
  is not enforced here, and correct while mypy is not a gate. The per-consumer index backstop
  compensates for the pre-graph inventory's completeness guarantee (design.md:475-478); it is
  justified after `audit3-F1`, but see design-rev5-F2 — the compensation is indistinguishable from
  the thing it backs up, so the producer guarantee cannot be seen failing. Escalate F2 into the
  design review's judgment; the smell does not otherwise indicate drift.
- **Smell 7 — the proposed solution changes who owns an invariant without saying so:** **clear.**
  Index classification, authored reference form, operand materialization, exact targets, and the
  depth budget move from codegen into agentic `inspect_reference_uses`, and the move is stated three
  times over: the ownership table (design.md:690-708), the cross-repository
  `semantic-evidence/v2` API marker with a version bump, and the per-repository ownership manifests.
  D8 separately records that agentic owns detection while codegen owns the
  `SI_INDEXED_SOURCE_UNSUPPORTED` refusal. Nothing changes hands quietly.

Gate: **BLOCKED (audit3-F1)** — new findings design-rev5-F1 and design-rev5-F2 are DISPOSED

Resolves:

- audit3-F1: **DEFERRED** — authority: owner-grade source unchanged (`P-003`/`P-004`) — basis:
  Revision 5 specifies a mechanism that would fix it (closed `ExactReferenceUse | IndexedReferenceUse`
  with no path on the indexed variant; `IndexExpression` in the mapped metatype table so runtime
  class names never identify it; indexed refusal returned "regardless of whether the enclosing site
  is a binding, alias, computed attribute, predicate, or calculation-definition expression",
  design.md:378-379) and names a proof matching the recorded falsifier exactly (closure matrix,
  computed-attribute row, indexed refusal required on live + admitted/capture, asserting one public
  diagnostic token, authored reference, root-relative `file:line`, and no graph or snapshot byte
  change). A design is a plan, not a code change: the defect is still live at `C_prod`, so the block
  clears only when that named live-and-capture computed-attribute test is green on the production
  commit — not on this revision.

---

## audit-phase3 — 2026-08-18 — rev `e3e1a39` (Codegen `stop-parser-impl-r2`; upstream Agentic `3f8bd58`, 0.1.3 / `semantic-evidence/v2`)

Point (re-derived): The product is three steps and nothing else — parse the models with a SysMLv2
parser, walk the parser's resolved tree to reconstruct the math, write that math into TEAx Python.
Every decision on the way is read from the parser's own resolved evidence. An authored form the
toolchain cannot honor has exactly two honest outcomes: resolve it through the parser, or refuse by
name before anything is built. One modeled source occurrence becomes exactly one runtime source.
[source: `.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`, grade: **owner**
(`[OWNER-VERBATIM, 2026-08-16]`); exact-occurrence companion
`.project/product/P-002-exact-owner-anchoring.md`, grade: agent/ratified]

Falsifier: an authored form the toolchain cannot honor reaches a graph, snapshot, or generated
package with its meaning silently changed; or a decision rule reads something other than the
parser's resolved evidence (Python class names, qualified-name prefixes, positional or
sole-candidate election); or two distinct modeled sources collapse onto one runtime source without a
refusal.

Findings:

- audit-phase3-F1 [DO] The consumer closure table is 20 of 24 cells empty and its gate test is
  committed **red** (`tests/conformance/test_expression_evidence_integrity.py::test_every_consumer_cell_names_a_proof`,
  the sole substantive failure in a 2206-passed run). Four of the six consumer rows —
  calc-definition dependency, alias, constraint predicate, deep literal override — carry **no
  committed indexed-refusal proof**, and the deep-override row still reads "not an expression
  route", the same asserted-not-proved shape that produced `audit3-F1`. Behavior was measured on six
  independently authored shapes (computed attribute, constraint-usage predicate, nested operator,
  postfix `cells.mass#(2)`, calc-definition body, deep literal override `:>> pick = cells#(2).mass`):
  **all six refuse with one `SI_INDEXED_SOURCE_UNSUPPORTED` carrying the authored reference and a
  root-relative `file:line`**. So this is a proof gap, not a contract violation. Falsifier: fill the
  four rows with public-route cases, and assert which layer refused (pre-graph inventory vs
  per-consumer backstop) so an omitted preflight row cannot yield an identical passing test. —
  `.project/product/P-003`/`P-004` (owner) applied via agent inference about closure scope
  (`[AGENT]`/`[INFERRED]`) — disposition: DISPOSE — declared Phase 4 deferral, recorded
  `[INHERITED: plan Revision 4]` in plan.md#phase-3-completion; carries design-rev5-F2 forward.

- audit-phase3-F2 [DO] The new qualified-predicate rendering seam is a **positive capability
  change** admitted on hand-built-IR unit tests only. `predicate_reference_name`
  (`src/sysml_codegen/generation/constraint_name_safety.py:97`) now binds Python by the exact
  target's local name, so `comp_a::length > 0.0` — which at `b4e97dd` died as "leaf reference is not
  a safe Python identifier" — now generates. Its two named pins build
  `FeatureReferenceFact`/`IdentityFact` by hand; the plan's claim that "the public six-consumer
  mutation test … pin[s] the result" (plan.md, deviation 2) is inaccurate —
  `test_combined_named_source_reaches_every_and_only_its_consumers` asserts on the `InstanceGraph`
  and never renders Python. The shipped package generated from
  `tests/fixtures/usage_owned_reference_consumers` binds `length` correctly, and the P-002 collapse
  risk fails closed: two distinct qualified targets sharing one local name in one predicate refuse
  at projection with `SI_RENDERING_COLLISION` before generation. Correct, under-evidenced.
  Falsifier: a licensed public-route generation test on that fixture asserting the emitted predicate
  source and its arg names, plus a real-model collision case. — `.project/product/P-002`
  (agent/ratified) and the spec's own "positive shapes need real-model + public proof" criterion —
  disposition: DISPOSE — add the public-route pin; correct the plan's evidence claim.

- audit-phase3-F3 [DO] The closed site set does not include a `ConstraintDefinition` body.
  `_enumerate_sites` (`src/sysml_codegen/elaboration/expression_evidence.py:200`) enumerates
  features carrying `feature_value_expression` plus `ConstraintUsage.result_expression`; a
  constraint **definition** body is neither. A model whose def body carries `h.cells#(2).mass` is
  not refused by the inventory — it dies later at `SI_EDGE_DANGLING` naming the wrong thing, which
  is the exact "named after whichever check fired first" failure the inventory exists to remove.
  Measured bound: the same model refuses identically with the index replaced by a literal, so
  part-typed constraint-definition inputs are independently unsupported and no wrong output can ship
  through this hole today. Falsifier: an authored constraint-definition body reaching a plural
  through supported inputs and producing anything other than `SI_INDEXED_SOURCE_UNSUPPORTED`. —
  `.project/product/P-003` (owner) applied via agent inference (`[AGENT]`/`[INFERRED]`) —
  disposition: DISPOSE — record the site-set boundary and its unreachability reason in Phase 4's
  closure table rather than leaving it unstated.

Smells:

- **Smell 3 — a special category exempts a case whose user-visible meaning is unchanged: cleared.**
  This was half of `audit3-F1`. `ExpressionSiteRole` is contextual routing only; the refusal is
  uniform across binding, computed attribute, alias, predicate, calc-definition dependency, and deep
  literal override, measured on all six.
- **Smell 4 — correctness depends on downstream knowledge of an internal representation: cleared.**
  This was the other half. `type(...).__name__` dispatch is gone from the detection path;
  `IndexExpression` is identified by `SysideAdapter.is_instance` against the installed metatype map,
  which raises `ValueError` on an unmapped name rather than answering False
  (`agentic-mbse/src/agentic_mbse/sysml/reference_use.py:294,467,513`; adapter at
  `syside_adapter.py:414`). Codegen's remaining `type(...).__name__` uses are error-message text,
  not decisions.
- **Smell 1 — two representations manually kept synchronized: fires weakly, disposed.**
  `extraction/computed_attribute_extractor.py` gained a hand-written fail-closed policy for
  three-segment part-rooted chains — a second, divergent classifier of a shape the elaborator owns
  positively. It is proved unreachable from both public raw-source arms by transitive import
  analysis (`test_public_raw_source_arms_do_not_reach_off_route_modules`), and the spec explicitly
  dispositions the three off-route modules out of scope with deletion tracked as a coverage problem.
  Hardening dead code instead of deleting it is the weaker move; not drift.
- **Smells 5 and 6 — clear.** The one committed red is a deliberate Phase-4 marker, not a baseline
  preserving contradicting behavior; the indexed tests are parametrized over live/admitted/capture
  and both strict modes, and independent probes reproduced the refusal on six shapes none of those
  tests use.

Gate: **DISPOSED (audit-phase3-F1, audit-phase3-F2, audit-phase3-F3)**

Resolves:

- audit3-F1: **FIXED** — authority: owner-grade source unchanged (`P-003`/`P-004`); resolved against
  the recorded falsifier by measurement, not by recency. Basis: (a) the computed-attribute route
  specifically — `tests/fixtures/indexed_bare_chain_singular` is
  `attribute picked : Real = cells#(2).mass` under `part cells : Cell[1]`, the exact audited shape,
  and `test_indexed_bare_chain_singular_slot_refuses_before_consumers` is licensed and green across
  all three public arms (`live`, `admitted`, `capture`) and both strict modes, asserting one
  `SI_INDEXED_SOURCE_UNSUPPORTED`, `reference == "cells#(2).mass"`,
  `source_file == "root-0/model.sysml"`, `source_line == 15`, no downstream consumer call, and no
  snapshot written; (b) reproduced independently outside the fixture set on a fresh model — live and
  capture both refuse with that one diagnostic before any graph exists; (c) refusal is pre-graph by
  construction — `build_expression_evidence_inventory` is the first call in
  `elaborate_loaded_extractor` (`orchestration/elaborated_pipeline.py:163`), ahead of extraction,
  elaboration, and graph allocation, and `_acquire` raises on the first `IndexedReferenceUse`;
  (d) metatype identification now goes through the mapped adapter, not `type(...).__name__`, per
  Smell 4 above; (e) the escape class the finding named — the same reference changing meaning by
  feature category — does not reproduce on any of six authored routes probed, including the deep
  literal override row the design left as an assumption.

---

## audit-phase3 (AUDITOR ADDENDUM) — 2026-08-18 — rev `e3e1a39`

Appended by the Phase 3 audit after the lens run above. The lens agent did not probe the
unit-annotated value-site shape; two independent audit lanes did, and both reproduced the same
defect. This addendum records it against the same Point and Falsifier as the block above.

Findings:

- audit-phase3-F4 [DON'T] **A valid, diagnostic-free model crashes the public generation route with
  an internal invariant exception and no diagnostic at all.** A unit-annotated reference at an
  attribute value site — `attribute mirror_len : Real = base_len [m];`, and the feature-chain form
  `= inner.w [m]` — loads with `extractor.diagnostics.validation == []` and then raises
  `ExpressionInventoryError: expression site alias <uuid> is absent from the evidence inventory`
  out of `sysml-codegen generate`, in both strict and lenient arms. The refusal carries **none** of
  the four required elements: no code token, no authored reference, no root-relative `file:line`, no
  cause chain. The message names a UUID the modeller cannot map to anything they wrote.

  Cause: the ALIAS-vs-COMPUTED_ATTRIBUTE role is decided **twice, on two different inputs**. The
  enumerator applies `_is_plain_reference` to the **raw** `feature_value_expression`
  (`src/sysml_codegen/elaboration/expression_evidence.py:245,250-254`), where a `[` annotation is an
  `OperatorExpression`, so the site is filed `COMPUTED_ATTRIBUTE`. The consumer applies the textually
  identical `_is_reference_expression` to the **unit-unwrapped** expression
  (`src/sysml_codegen/elaboration/elaborate.py:871,894,1017-1019`), so it looks up `ALIAS`. The row
  is absent, `require` raises (`expression_evidence.py:111`, via `elaborate.py:2343`), and
  `ExpressionInventoryError` appears in no `except` clause at the D7 boundary
  (`orchestration/elaborated_pipeline.py:171-218`).

  Phase-3-introduced, not pre-existing: `expression_evidence.py` is born at `b4e97dd`, and at
  `C_base` (`78a9beb`) `_PendingAlias` carried the expression object itself, so there was no site key
  and no role to disagree about. The shape is a supported capability the phase removed without a
  refusal.

  Not caught by the suite because the only fixtures exercising `= ref [unit]`
  (`tests/fixtures/constraint_binding_unit_annotation/model.sysml:62,77`) use the **binding** role,
  which `_role_for_owner` keys by `owning_type` and which therefore never takes the expression-shape
  branch (`expression_evidence.py:241-244`). No kept test pins that the enumerator's role decision
  and each consumer's role decision agree over a real model.

  Falsifier: compute the role once — enumerate on the unwrapped expression, or key the consumer off
  the raw one — and add a licensed public-route test over a real model carrying a unit-annotated
  reference at an attribute value site and at a feature-chain value site, asserting a graph (or a
  named diagnostic), never an `ExpressionInventoryError`. Independently, contain
  `ExpressionInventoryError` at the D7 boundary so an internal-defect class can never reach a user as
  a bare traceback.

  — `.project/product/P-003-no-workarounds-for-bad-models.md` and
  `.project/product/P-004-product-identity-parse-walk-emit.md` (**OWNER**), bounded by
  `.project/product/P-001-design-search-free-variation.md` (a form the language defines becoming
  unauthorable with no stated replacement spelling) — disposition: **BLOCK**

Smells:

- **Smell 1 — two representations manually kept synchronized: FIRES, unresolved.** The alias/computed
  role split is implemented twice, in two modules, by two identical predicates applied to different
  nodes, with no static check or kept test pinning their agreement. Only a runtime invariant crash
  reveals divergence. This is the structural cause of F4, and it is escalated into the audit's
  Product Judgment rather than resolved here.

Gate: **BLOCKED (audit-phase3-F4)**

The prior `audit-phase3` block's `DISPOSED` gate and its `audit3-F1: FIXED` resolution both stand —
F4 is a distinct defect on a different shape and does not reopen the indexed-source finding.

---

## audit-phase3-remediation — 2026-08-18 — rev `3377cd0`

[AGENT] Implementation response to the auditor's owner-grade `audit-phase3-F4` block. This entry
records the candidate fix and its evidence. It does not replace the auditor's verdict.

The role split now has one owner. The inventory normalizes a unit annotation before assigning the
site role, stores that authoritative site by declaration, and each consumer retrieves the stored
site instead of re-running an alias/computed predicate. A unit-annotated bare reference and a
unit-annotated feature chain both complete the public conversion route in strict and lenient modes.

`ExpressionInventoryError` is also contained at the public boundary. The diagnostic is
`SI_EVIDENCE_INCOMPLETE` and carries the authored expression, root-relative `file:line`, and the
inventory exception as its cause. An expression-keyed upstream semantic error receives the same
authored site context before conversion.

The falsifier named by F4 is pinned directly by:

- `tests/unit/test_expression_evidence_boundary.py::test_unit_annotated_plain_reference_is_an_alias_site`;
- `tests/conformance/test_expression_evidence_integrity.py::test_unit_annotated_alias_survives_the_public_conversion_boundary`;
- `tests/conformance/test_expression_evidence_integrity.py::test_inventory_invariant_is_contained_with_authored_provenance`.

Gate: **PENDING INDEPENDENT RE-AUDIT**. The implementation evidence satisfies F4's recorded
falsifier, but only the independent audit may change the historical **BLOCKED** verdict.

---

## audit-phase4 — 2026-08-18 — rev C_prod `e5f73e6` (stop-parser-impl-r2) / plan artifacts `a5ff0a2`

Epic: ELABORATE-FIRST (`.project/backlog/epic_elaborate_first_architecture.md`)

Point (re-derived): The product is three steps and nothing else — parse the models with a SysMLv2
parser, walk the parser's resolved tree to reconstruct the math, write that math into TEAx Python.
Every decision on the way reads the parser's own resolved evidence, and an authored form the
toolchain cannot honor has exactly two honest outcomes: resolve it through the parser, or refuse by
name before anything is built. No second account of a fact the graph already owns.
[source: `.project/product/P-004-product-identity-parse-walk-emit.md` and
`.project/product/P-003-no-workarounds-for-bad-models.md`, grade: **owner**
(`[OWNER-VERBATIM, 2026-08-16]`); exact-occurrence companion
`.project/product/P-002-exact-owner-anchoring.md`, grade: agent/ratified]

Falsifier: a generation decision is taken from a caller-supplied account rather than the sealed
graph, or an internal invariant reaches a user as an untyped traceback instead of a named refusal;
or a claimed proof of a refusal route does not exist on the public route it claims; or the evidence
machinery that attributes a behavior transition can no longer detect a change to the inputs the
transition was measured on.

Findings:

- audit-phase4-F1 [DON'T] The fixture-inventory validator lost its only current-bytes check, inside
  the phase whose own edit tripped it. `1ce8638` (a documentation sweep) rewrote a comment in the
  locked fixture `tests/fixtures/deep_cross_scope_probe/design.sysml`; the next commit, `8919232`,
  deleted the `_sha(ROOT / path) != source["sha256"]` comparison from
  `verification/capture_baseline.py::validate_manifest` and rebased `_historical_source_rows` onto
  the P_seed git tree. After the change no committed check compares any fixture's **current** bytes
  to its locked bytes: leg 1 (`tests/conformance/test_probe_fixture_lock.py:102`) recomputes the 118
  locked hashes against history at `20f9e60` only; leg 2 (`validate_current_batch`) pins outputs for
  the 37 canonical roots; and the manifest rebuild is now a tautology — it compares a rebuild from
  P_seed against the frozen P_seed manifest bytes. The six `ADDED_ROOTS`, including
  `indexed_expression_source` (a fixture Phase 4's own indexed-BINDING matrix cell depends on, with a
  hard-coded line number), are in neither the batch nor any current-bytes check, so they now have no
  byte pin on any leg. The disclosure row at `verification/expected-transitions.md:116` states the
  change was made "as the three-leg lock requires" and does not name the coverage that was dropped.
  Falsifier: restore a current-vs-locked byte comparison over all 43 roots, with any deliberate
  difference owned by a named ledger row the way leg 3 already owns `capture_baseline.py`; or state
  the loss plainly in the ledger and name what covers the six added roots instead. —
  `.project/active/stop-reinventing-the-parser/spec.md` "Immutable baseline and entry gate"
  (`[INHERITED]`) and the design's three-leg lock (agent) — disposition: DISPOSE — record the
  coverage loss in the transition ledger and restore or replace the current-bytes leg before close.

- audit-phase4-F2 [DO] The consumer closure table asserts public-arm coverage it does not have for
  the deep-literal-override row. `test_the_consumer_closure_table_covers_every_reviewed_consumer`
  asserts `public_arms == ("live", "admitted/capture")` for **every** row, but that row's
  `indexed_refusal` cell names a hand-built-IR unit test with monkeypatched facts
  (`tests/unit/test_expression_evidence_boundary.py:543`), and its `operand_or_depth_failure` cell is
  still the prose string `"not an expression route"` — which `test_every_consumer_cell_names_a_proof`
  accepts because it only tests for a non-empty string. The reason is legitimate and is the
  product's point working correctly: the authored form `:>> rig.cells#(2).mass = 7.0;` is refused by
  SysIDE at parse (`parsing-error: Unexpected 'DECIMAL_VALUE'`), while the same override without the
  index parses and elaborates. So there is no authorable public route for that cell — but nothing in
  the table or the run record says so, and a reader takes the row as equal in force to the other five.
  Falsifier: mark the two deep-override cells with their measured unauthorability and the probe that
  established it, and make the `public_arms` assertion per-cell rather than per-row, so a future
  empty-in-substance cell cannot pass as covered. — `audit-phase3-F1`'s own recorded falsifier
  ("assert which layer refused … so an omitted preflight row cannot yield an identical passing test")
  applied by agent inference (`[AGENT]`/`[INFERRED]`) — disposition: DISPOSE — record the boundary in
  the table; no behavior change required.

Verified positive (no finding): the registry closure does what the point asks.
`required_exit_point_wrapper_types(graph)` (`src/sysml_codegen/generation/registry.py:48`) is the
single owner of the root-output wrapper set and of its refusal; the caller-supplied
`exit_point_primitive_types` argument and the CLI's `_collect_exit_point_primitive_types` collector
are gone (`src/sysml_codegen/cli/__init__.py:319-323,716-727`), and the untyped `RuntimeError` that
fired when the caller's list disagreed with the graph is replaced by the typed
`EXIT_POINT_TYPE_UNSUPPORTED` carrying module, output, python_type, and `file:line`
(`src/sysml_codegen/generation/errors.py:58-74`). No second wrapper map survives anywhere in `src/`.
The phase's suites ran independently under license in the recorded extraction: 166 passed
(`test_expression_evidence_integrity.py` + `test_expression_evidence_boundary.py`), 46 passed
(registry, exit-type preflight, module-kind, documentation contract, hygiene tail), 21 passed
(probe-fixture lock + v6 snapshot inventory). Zero skips, so the licensed arms really ran.

Smells:

- **Smell 1 — two representations manually kept synchronized: one instance removed, one created.**
  Removed: the registry's caller-supplied type set beside the graph's own root outputs, whose only
  synchronization check was an internal `RuntimeError`. Created: the frozen fixture inventory and the
  on-disk fixtures, whose content synchronization is now unchecked by any committed test (F1). Fires,
  and escalates into the audit's judgment as F1.
- **Smells 3, 4, 5: clear.** No new category exempts a case, no decision reads a Python class name
  (`type(...).__name__` is absent from every decision path touched here), and the two recorded
  nonzero baselines (30 mypy errors, 608 broad ruff) are declared non-green rather than preserving
  contradicting behavior.
- **Smell 6 — a test passes by selecting one route: does not fire for the matrix, fires weakly for
  the lock.** The new indexed-refusal matrix runs 5 roles × 5 arms (live/admitted strict and lenient,
  capture) on real parsed models, asserts the exact authored reference, root-relative `file:line`, the
  `SemanticEvidenceCode` cause, that the consumer's real adapter was never called, and that no
  snapshot byte moved. That is the opposite of route selection. The manifest check, by contrast, now
  passes by comparing a P_seed rebuild against P_seed bytes (F1).

Gate: **DISPOSED (audit-phase4-F1, audit-phase4-F2)** — no owner/`[HARD]` contradiction found in
Phase 4.

Resolves:

- audit-phase3-F4: **FIXED** — authority: owner-grade source unchanged (`P-003`/`P-004`); resolved
  against the recorded falsifier by independent code reading and a licensed run, not by the
  remediation record. Basis: (a) the role is decided once, on the unit-unwrapped expression, inside
  the inventory (`elaboration/expression_evidence.py:327,342-347`), stored per declaration, and each
  consumer retrieves it via `_site_for_expression` -> `inventory.site_for(declaration_id)`
  (`elaboration/elaborate.py:2079-2090`, used at 893, 926, 2053, 2151) — the duplicate predicate
  applied to a different node is gone; (b) `ExpressionInventoryError` is caught at the D7 boundary
  and converted to `SI_EVIDENCE_INCOMPLETE` carrying the authored reference and root-relative
  `file:line` (`orchestration/elaborated_pipeline.py:178-198`), so the class can no longer reach a
  user as a bare traceback; (c) the public-route pin
  `test_unit_annotated_alias_survives_the_public_conversion_boundary` now runs over **all five**
  public arms rather than two strict modes, on a real model carrying both `= base_len [m]` and
  `= inner.w [m]`, and passed in an independent licensed run alongside
  `test_inventory_invariant_is_contained_with_authored_provenance`.
  This discharges the `PENDING INDEPENDENT RE-AUDIT` gate left by the `audit-phase3-remediation`
  block, consistent with the Phase 3 re-audit verdict in `run-records/phase3-audit.md`.
- audit-phase3-F1: **FIXED, with a named residue.** All 24 cells of the consumer closure table are
  filled and `test_every_consumer_cell_names_a_proof` is green rather than committed red. Twenty-two
  cells are public-route conformance proofs over five arms; the layer discrimination F1 demanded is
  present as `acquired[-1].role is case.role` plus `not downstream.called` against a spy on the real
  consumer adapter, so an omitted preflight row cannot produce an identical passing test. The residue
  is the two deep-override cells, carried forward as audit-phase4-F2.
- audit-phase3-F3: **FIXED** — `_enumerate_sites` now enumerates `ConstraintDefinition.result_expression`
  as well as `ConstraintUsage`'s (`elaboration/expression_evidence.py:309-323`), and Phase 4's
  `INDEXED_PREDICATE_SOURCE` case authors exactly the shape F3 named — a `constraint def` body
  carrying `h.cells#(2).mass` — and asserts one `SI_INDEXED_SOURCE_UNSUPPORTED` at the authored
  reference and line across all five arms. F3's falsifier is directly pinned.
- audit-phase3-F2: **NOT RESOLVED — still standing as DISPOSED-but-undelivered.** F2's disposition
  was "add the public-route pin; correct the plan's evidence claim." At C_prod the qualified-predicate
  rendering seam is still evidenced only by `tests/unit/test_predicate_compiler.py` (hand-built
  `FeatureReferenceFact`/`IdentityFact`); no test generates Python from
  `tests/fixtures/usage_owned_reference_consumers` and asserts the emitted predicate source and arg
  names. `audit-phase3-F2` appears nowhere in `plan.md` or the Phase 4 brief, so the disposition was
  never scheduled. Basis for carrying it: grep of `tests/` for `predicate_reference_name` and for
  that fixture at `e5f73e6`. Authority: agent/ratified (`P-002`); it does not block, but it must not
  be read as closed by the Phase 4 gate.
