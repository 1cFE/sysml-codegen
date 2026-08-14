# Audit: CONSTRAINT-SEMANTICS Item 7 — ADR, Product Promise, and Agent-Facing Documentation Sync

**Verdict:** **CERTIFY-WITH-RESIDUALS**
**Audited:** 2026-08-14 · **Cure re-verification pass:** 2026-08-14 (A-3, A-4)
**Branch:** `item7-rebuild` (codegen) · `item7-rebuild` (agentic-mbse worktree) · `constraint-semantics-item3` (TEAx)
**Commit audited:** `5e2373f`, plus three audit cures written on top (C-1..C-3, below), plus the
implement resume's A-3 and A-4 cures — **both re-verified by the auditor and confirmed**

**Residuals still standing:** two, both owner calls — A-1's symlink residual (resolves on merge) and
A-2's `[CONSTRAINT-GATES-UNTAGGED]` backlog vehicle. A-3 and A-4 are closed.

---

## The Point

A design search only means something if the feasibility answer can be trusted. The owner stated the
product's purpose in their own words on 2026-08-13: engineering design parameters vary freely,
viability and outcomes get assessed, and the engineering logic is **not** embedded by predetermining
the free variables and backing into all others. The CONSTRAINT-SEMANTICS epic built the trust half of
that — a report headline that cannot confuse "checked and passed" with "not checked," and a visible
disposition on every authored constraint.

The behavior changed across Items 1–6, 8 and 9. Almost none of the documentation that teaches it
changed with it. That gap has a specific cost: the next authoring session — human or agent — reads a
shipped skill, a pattern doc, or an expert-agent prompt, copies the superseded shape, and produces a
model that generates no gate at all. The report will then say something true about nothing.

Item 7 closes that gap in three repositories, gives the owner's promise its first durable home, and
executes four obligations that Item 1's archival left with no vehicle. It documents what landed; it
changes no behavior.

## Summary

Every claim I probed reproduced, including the ones that are expensive to fake: the licensed suite,
the three-repo post-edit sweep, the owner-verbatim diff, the boundary discipline, and the matrix
recount. The record is unusually honest — it flags its own aggregation deviation, its own scope
defect, and its own unmet criteria rather than rounding them green.

Three defects survived my probes and are cured here (C-1..C-3); four findings were raised (A-1..A-4).
A-3 — a documentation defect the item itself introduced and my probe caught — and A-4 were then cured
by an implement resume and **re-verified by me end to end** (see each finding's re-verification
block). The two residuals the orchestrator ruled on are both loudly recorded; the SC5 residual was
missing its named vehicle, which is now filed. **Two residuals remain, both owner calls.**

## Product Judgment

**Is this the right piece of work? Yes.** Documentation is the only delivery mechanism for a behavior
change that is invisible from the code — a modeler who writes `constraint` where they meant
`assert constraint` gets a model that generates cleanly and checks nothing. Item 7 is the item that
stops that, and it is correctly scoped to the surfaces an author actually reads.

**Product-lens ledger gate: DISPOSED → CLEAR after the re-verification pass.** Full block appended to
`product-lens.md` (audit run), with a resolution-by-citation note added when A-3 closed. No block in
the ledger's history is unresolved: spec-stage DISPOSED (item7-F1..F3, all three folded into the spec
body), implement-stage CLEAR, audit-stage DISPOSED(A-3) now resolved. Epic gate CLEAR. No
owner-graded or `[HARD]` contradiction.

**One structural smell fired, and I am resolving it explicitly rather than leaving it in the rubric.**
agentic-mbse tracks **two divergent copies** of the agent definitions (`claude/` 37 files, `.claude/`
23 files) that must be kept synchronized by hand — the "two representations manually kept in sync"
tripwire. It resolves for certification because Item 7 **found** it (Item 1 had corrected only
`claude/`), **reduced** it (`sysml-expert.md` brought level), and **recorded** it loudly in
`verification.md` and `CURRENT_WORK.md`. Item 7 did not introduce it and cannot fix the topology —
that is the symlink residual, an owner merge. Left silent it would have blocked; recorded, it does
not.

**The finding that controlled something — now closed.** A-3 was a real product contradiction: the
`@inapplicable:` example the new authoring doc told a modeler to copy was refused by the shipped
generator. It was the exact failure class this item exists to prevent, one level up. The implement
resume fixed it and I re-verified the fix by running the corrected example through the real
generator: it now completes and seals, and the marker's reason reaches the generated catalog. No
product contradiction remains.

---

## Findings

### A-1 — The symlink residual's recorded evidence was falsified by re-running it *(CURED, C-1)*

`verification.md` recorded the discriminator as
`grep -c "assert constraint TempLimit" .claude/skills/sysml-conventions/SKILL.md` → 1 in codegen,
"the in-bounds copy of the same file reads 0."

**Reproduced: the in-bounds copy also returns 1.** The corrected SKILL.md deliberately *keeps*
`assert constraint TempLimit { temperature < 1000 [K] }` at `:151` as a labelled **negative** example
under rule 2 ("Bind formals; don't inline the predicate"). The count does not discriminate the two
files at all, so the recorded evidence proves nothing.

**The residual itself is real and independently reproduced.** `readlink -f` on codegen
`.claude/skills/sysml-conventions/SKILL.md` →
`/home/reid/1cfe/agentic-mbse/claude/skills/sysml-conventions/SKILL.md`, and that file's `:136` still
reads the stale example as the **blessed** shape. Working discriminator, verified both ways:

| Probe | codegen (symlink → out-of-bounds) | agentic-mbse worktree (in-bounds) |
|---|---|---|
| `grep -c 'blessed shape is bindings-only'` | 0 | 1 |
| `grep -c '@inapplicable:'` | 0 | 3 |

**Cure C-1:** `verification.md`, "Named residual" section — the false line replaced with the
correction stated as a correction, plus the working discriminator table. The ruling is untouched.

### A-2 — The SC5 parked half had no named vehicle *(CURED, C-2)*

The orchestrator's ruling requires the parked half of SC5 to have a named vehicle. At implement time
it had none. It was recorded narratively in four places — `spec.md:81-87`, `verification.md`'s Phase 5
⚠️ block, `plan.md:909-915`, `CURRENT_WORK.md:26-31` — and in **no** backlog entry and **no**
close-stage obligation. `[MATRIX-EPIC-SURFACE-ROWS]` (`BACKLOG.md:447`) is a different subject: three
*lifecycle* surfaces, not the untagged constraint-semantics gates.

An owner call recorded only in an item folder that archives at `close` is an owner call that
disappears at `close`.

**Cure C-2:** `[CONSTRAINT-GATES-UNTAGGED]` filed in `.project/backlog/BACKLOG.md`, P2 unowned,
stating what Item 7 discharged, why the rest was not done, and the two routes the owner can take.
Filing the ticket mints no REQ tags and makes no requirements decision — it is the vehicle, not the
call.

### A-3 — The `@inapplicable:` "How to write it" example is refused by the shipped generator — **CURED AND RE-VERIFIED, CLOSED**

> ### Auditor re-verification, 2026-08-14 — **the cure holds. A-3 is closed.**
>
> I did not take the cure note on trust. Every claim in it was re-run under the licensed terms
> (`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`, then
> `/home/reid/1cfe/item7-rebuild-venv/bin/sysml-codegen`; never `uv run`).
>
> **1. The corrected example is accepted by the shipped generator.** I lifted the exact authored text
> from `docs/patterns/constraints.md:428-446` — verbatim, comment included — into a package with
> minimal instantiated content, and ran the real generator. It elaborates and generates to completion
> and seal: `INFO: Sealing package...` → `INFO: Code generation complete`. Where the pre-cure example
> died with *"marked inapplicable but produced 1 executable entries,"* this one does not.
>
> **2. The teaching point is true at the output, not just in the prose.** The doc claims the reason
> "travels into the catalog with the disposition." It does. In the generated package:
>
> | Claim | Where I found it |
> |---|---|
> | `inapplicability_reason: "no vacuum system in the direct-drive variant"` | `contracts/model_contract.json:17` |
> | `inapplicable_gate_count: 1` | `modules/constraints/constraintreportaggregatormodule.py:25` |
>
> The same `COVERAGE` line reads `applicable_gate_total: 0`, `assessed_gate_count: 0`,
> `coverage_state: 'none'` — the marked gate left the denominator and the headline does **not** claim
> full satisfaction over an empty set. That is D4's ruling holding at the generated bytes.
>
> **3. Both fixture citations are real and behave as cited.** I generated each one:
>
> - `tests/fixtures/constraint_coverage_all_inapplicable` → completes and seals. **Accepted.**
> - `tests/fixtures/constraint_coverage_eligible_inapplicable` → *"`…::Live::live_but_marked` … is
>   marked inapplicable but produced 1 executable entries."* **Refused by design**, and its header
>   says so in as many words ("GENERATION MUST FAIL ON THIS MODEL"). Both fixtures pre-date this item
>   — cited, not authored, so the no-fixture-changes Non-Goal holds.
>
> **4. All surfaces carrying the shape are consistent.** `grep -rn "vac_ok"` across the three repos
> returns exactly two authoring surfaces, both carrying the corrected shape — agentic-mbse
> `docs/patterns/constraints.md:441` and `claude/skills/sysml-conventions/SKILL.md:169` — plus this
> item's own audit and verification records. TEAx has none, correctly: it does not teach SysML
> authoring. Codegen's `modeling-assumptions.md:651-653` carries no code block and now states the
> rule with **both** conditions: *"write it in the bindings form … **and put it on a gate that does
> not run.** The form decides whether the marker arrives; whether the gate runs decides whether it is
> accepted."* That was the missing half. Each surface also carries the D9 refusal beside the example,
> so a reader meets the rule at the same moment as the shape.
>
> Nothing about the cure was over-claimed. The residual is discharged.

> **Cure note from the implement resume, 2026-08-14 (retained for the record).** Option (a) taken: the
> example now puts the marked gate on a `part def` the variant never instantiates, so it reaches no
> occurrence and the marker stands, with a one-line comment saying why. The exact authored text was
> elaborated **and** run through the real generator to completion and seal
> (`sysml-codegen generate` → `Sealing package…` → `Code generation complete`), and the marker is
> verified to have reached the domain: the generated catalog carries
> `inapplicability_reason: "no vacuum system in the direct-drive variant"` and
> `inapplicable_gate_count: 1`. All three surfaces swept and made consistent — two carried the code
> example (`docs/patterns/constraints.md`, `claude/skills/sysml-conventions/SKILL.md`), and codegen's
> `modeling-assumptions.md` §8 carried no code block but stated only the *form* condition, so its
> practical rule now names both (bindings form **and** does-not-run). Full record and the probe
> command: `verification.md`, "A-3 cure".

`agentic-mbse docs/patterns/constraints.md:427-433` gives this as the canonical way to write the
marker:

```sysml
assert constraint vac_ok : ProductWithinBand {
    doc /* @inapplicable: no vacuum system in the direct-drive variant */
    in actual = plant.pumping_speed_total;
    in reference = plant.pumping_speed_required;
}
```

I built that shape into a minimal model and ran the real generator under a licensed toolchain. It
elaborates, and then generation **refuses it by name**:

```
ERROR: Code generation failed: item7_audit_doc_examples::Plant::vac_ok (…) is marked inapplicable
but produced 1 executable entries: an inapplicability marker states a gate is not part of the
feasible set, and this gate ran. Remove the marker, or stop asserting the gate.
```

That is D9 — which the *same document* explains correctly 30 lines later (`:459-473`). The document
contradicts itself between its example and its rule, and the example is the part a reader copies. The
same shape appears in codegen `docs/architecture/modeling-assumptions.md` §8's marker section and in
the skill.

**A working shape exists and I verified it.** Move the marked gate onto an owner with zero
occurrences — the non-reaching case the contract's own vacuous-gate cell describes. Same model,
`vac_ok` relocated into a `part def` that is never instantiated: generation completes and seals.

**What should change:** in all three authoring surfaces, either (a) replace the example with a shape
that survives generation and say in one line *why* that owner has no occurrences, or (b) keep the
example and label it explicitly as the refused combination, forward-referencing D9 at the point of
use. Not fixed here: choosing between (a) and (b) is authoring judgment across three documents, and
the cure rules reserve that. *(Route (a) was taken by the implement resume and is verified above.)*

### A-4 — The "distinct kept test files" count does not reproduce, and its method is unrecorded — **CURED AND RE-VERIFIED, CLOSED**

> ### Auditor re-verification, 2026-08-14 — **55 reproduces. A-4 is closed.**
>
> I re-implemented the recorded method from its written description alone, without reading the cure's
> arithmetic first: rows whose status is **not** `RETIRED`, `*.py` taken from the **Test File column
> only**, and the file must **exist under `tests/`**. Result: **55** — the same number I reached
> independently at the first pass, and the number now recorded.
>
> The exists-on-disk decision is the one that was missing, and it is the one that matters. The three
> files the cure names as cited-but-not-kept — `test_gen_schemas.py`, `test_gen_stencils.py`,
> `test_graph_assembly.py` — are all absent from the tree in my run, cited by UNTESTED rows precisely
> *as the deleted pin*. My extraction also drops three **source** modules named inside cells
> (`graph_builder.py`, `constraint_facts.py`, `instance_graph.py`), which is why the looser readings
> inflate.
>
> Both places the number appears now read 55 and agree: the summary block (`verification-matrix.md:16`)
> and the Related Documents note (`:817`), the latter pointing at the recorded method. My own C-3 cure
> had propagated the then-current 59 into `:817`; that is superseded.
>
> **One honest limit.** Only the authoritative row of the cure's four-reading table reproduces on my
> re-run. My looser `*.py` extraction gives 71 / 68 / 61 for the three comparison readings against
> their 60 / 59 / 58, because I match source-module filenames the cure's extraction evidently does
> not. Those rows are illustration; the authoritative reading is the one the count is taken from, and
> it lands on 55 exactly, twice, by two independently written implementations.

> **Cure note from the implement resume, 2026-08-14 (retained for the record).** Method written down in
> `verification.md`, "A-4 cure": non-RETIRED rows only, Test File column only, and the file must
> **exist in the tree** — that last decision was the missing one. Three files cited by UNTESTED rows
> (`test_gen_schemas.py`, `test_gen_stencils.py`, `test_graph_assembly.py`) are cited precisely *as
> the deleted pin*; they are cited but not kept. The count is **55**, matching the auditor's
> independent number, and all four readings are tabulated so it reproduces. Corrected in both places
> it appeared: `verification-matrix.md:16` and `:817`.

`verification.md`'s recount table records "Distinct kept test files 50 → 57 (tables) → 59 (post-filing)."
Every other recount number reproduces exactly (below). This one does not: taking the last status
field per `^| REQ-` row and extracting `*.py` from the cited-test cell gives **55** (one of which,
`graph_builder.py`, is a deleted *source* module named inside a cell, not a test file); extracting
across the whole row gives **61**. The verification record states the counting method for the status
tallies and for the family count, but not for this one.

Nothing depends on the number and it is not a correctness claim about any requirement. Recorded so a
future recount does not treat 59 as a verified baseline. **What should change:** state the exact
command alongside the count, as the status tallies do.

---

### Plan completion

All six phases carry `- [x]` with per-phase notes; zero unchecked boxes across 78 checkboxes. Phase
notes are substantive, including the two that record their own failure to complete as specified
(Phase 4's scope correction, Phase 5's premise conflict). No placeholders or TODOs found.

### Spec conformance

| SC | Verdict at audit |
|---|---|
| SC1 — promise owner-stated, filed, cited from the trail | **✅ VERIFIED.** `diff` of `owner-checkpoint-20260813.md:9-13` against `P-001:13-17` is **empty**. All five supplementing paragraphs carry `[INHERITED: <source>]`. The tension section exists, states it resolves nothing, and names `[ACAUSAL-RELATIONS-CAPABILITY]` for the unbuilt half. Trail reaches P-001 in one hop from `epic_constraint_semantics_contract.md:118-125`. |
| SC2 — no superseded teaching in three repos; every hit dispositioned | **⚠️ RESIDUAL STANDS (symlink).** Post-edit sweep re-run by me in all three repos matches Table 2 **exactly**: codegen 0/13/7/20/5 (identical to pre-edit), agentic-mbse 0/25/8/0/52, TEAx 0/0/0/10/0. All 10 TEAx hits match Table 1 rows 62–70 plus P6. 11 dispositions spot-checked against source; every quoted hit still exists (line numbers shifted by the edits, as the record says) and every "correct as written" reading holds on inspection. |
| SC3 — `@inapplicable:`, disposition vocabulary, six states, TEAx opt-in documented | **✅ VERIFIED** in the authoring repos, subject to SC2's symlink residual only (**A-3 closed at the re-verification pass**; the post-cure sweep re-run shows agentic-mbse unchanged hit-for-hit at 0/25/8/0/52, so the fix introduced no new superseded teaching). Probed: codegen `modeling-assumptions.md:575,596,599` (the closed reason set and precedence), `reference/30-diagnostic-severity.md:151` (severity by cause), agentic-mbse `constraints.md` (8 `inapplicable` mentions, was 0), TEAx `docs/evaluation-and-study.md` (`full_satisfaction`/`partial_coverage` present, was 0). |
| SC4 — marker-works-where rule, B1–B5 cited | **✅ VERIFIED.** Decision table present in both authoring repos (`modeling-assumptions.md:639`, `constraints.md:440-443`); `catf_mfe_gated` B1–B5 and `test_constraint_population_oracle.py` rule 3 cited, not rewritten. **Independently confirmed by execution:** the bindings-form marker *does* reach the domain — my elaboration probe returns `inapplicability=Inapplicability(reason='no vacuum system in the direct-drive variant')`. The doc's central claim is true. |
| SC5 — matrix rows for landed gates, recount done | **⚠️ PARTIALLY MET, now with a vehicle (A-2).** Recount reproduced from the tables: total **280**, PASS **136**, PARTIAL **3**, RETIRED **131**, UNTESTED **10**, DEFERRED **0**, families **33** — every number matches the corrected summary block, and per-status sums to total. Both corrected blocks agree with the tables. Both newly cited test files exist and pass (`test_extraction_diagnostic_screen.py`, `test_upstream_pins.py`, in the 2070). A third count statement was still stale — cured, C-3. |
| SC6 — doc checks and `git diff --check` in every repo | **✅ VERIFIED BY RE-RUN.** Licensed suite re-run by me end to end: **`2070 passed, 34 skipped, 79 deselected` in 157.5s**, exit 0, and `grep -c "no live syside license"` → **0**. `git diff --check` clean in all three repos. |

**Non-goals respected.** No code, fixture, or schema path appears in any of this item's commits
(`git diff --name-only ec1fd10~1 HEAD` — 4 docs/CLAUDE.md paths, 14 `.project/` paths, nothing else).
Zero files under `.project/completed/` were touched. The derivative fixture docs were cited, not
rewritten. Nothing was pushed.

**Boundaries** (claim 6, fully reproduced): codegen on `item7-rebuild`, agentic-mbse worktree on
`item7-rebuild` with exactly one item commit (`a496aeb`), TEAx on `constraint-semantics-item3` with
exactly one item commit (`75eecb3`). `/home/reid/1cfe/agentic-mbse` (out-of-bounds) is on
`elaborate-first-salvage` with an **empty** `git status --short` — the stray edit's revert holds, and
the excursion is documented rather than silently reverted. No branch is ahead of a remote.

### Design conformance

No design stage ran; four design calls were made in-plan (D-1 ledger + existing-ADR convention, D-2
single sweep record, D-3 row-per-REQ-tag, D-4 TEAx S1–S5 unchanged). All four are followed as written:
`.project/product/INDEX.md` back-registers ADR-009 rather than minting a `docs/adr/` tree; one
verification record carries all three repos; D-3's "a gate without a REQ tag has nothing for the
Status column to be about" is exactly why SC5 parked; the TEAx scope is stated with its exclusions and
its terms unchanged.

### Code integrity

No code was changed, so the usual slop and failure-honesty rubric has no surface. Two integrity checks
that do apply to a documentation item:

- **Failure honesty in the record — strong.** The item records a one-row-per-hit deviation with its
  reason and count (64 vendored hits, flagged), a divergence between its own sizing estimate and the
  executed sweep (S5 vendored 33 → 45), a scope defect it created and then corrected mid-run
  (`grep -r` does not follow symlinks, so codegen's `.claude/` swept as empty), and an in-boundary
  excursion it caught and reverted. None of these had to be written down.
- **Aspirational citation — none found.** Every REQ-DIAG row was run before it was cited, and
  REQ-DIAG-01 is filed PARTIAL and -04 UNTESTED rather than rounded to PASS, with the gap named in
  each cell. I confirmed the -04 justification's load-bearing half (`constraint_facts.parse` has no
  caller in `src/` or `tests/`) and corrected its imprecise half (C-3).

---

## Cures applied at audit

| # | What | Where |
|---|---|---|
| C-1 | Falsified symlink-residual discriminator replaced with the correction stated as a correction, plus a working two-probe table | `.project/active/constraint-docs-agent-sync/verification.md`, "Named residual" |
| C-2 | `[CONSTRAINT-GATES-UNTAGGED]` filed as the SC5 parked half's named vehicle; cross-referenced from the Phase 5 record | `.project/backlog/BACKLOG.md`; `verification.md` Phase 5 block |
| C-3 | Two stale/imprecise matrix statements corrected: `:820` still read "50 distinct kept test files" against a summary block the recount had moved to 59; REQ-DIAG-04's cell claimed "the v6 envelope carries no `severity` field" when it carries a **disposition** severity (`snapshot/instance_graph.py:724,759,803`) — a different field from the **diagnostic** severity the row is about | `docs/architecture/verification-matrix.md` |

Each cure was reproduced before it was written. None touches owner-verbatim text, the amendments'
meaning, or either residual ruling.

---

## Certification

**CERTIFY-WITH-RESIDUALS** *(verdict restated after the A-3/A-4 re-verification pass; unchanged in
kind, narrower in residuals — from four open findings to two owner calls).* Four of six epic success criteria are met and verified by re-running the
item's own evidence rather than reading it. Two carry named residuals that are owner calls, not
missing work, and both are now recorded with a vehicle.

Marked at audit:
- Epic file `epic_constraint_semantics_contract.md`: SC1, SC3, SC4, SC6 ticked; SC2 and SC5 left
  unticked with their residuals named inline. Item heading **not** given ✅ — two criteria are open.
- `spec.md` success criteria: already correct as written; SC2/SC5 stay unticked. No change needed.
- `plan.md`: all phases already checked and verified complete. No change needed.
- `CURRENT_WORK.md`: status updated to certified-with-residuals, with the three findings named.

**Residuals carried to `close` — two, both owner calls, neither of them work left undone:**
1. **Symlink residual (SC2/SC3)** — resolves when the owner merges `item7-rebuild` into whatever
   branch `/home/reid/1cfe/agentic-mbse/claude/` resolves to. Evidence corrected (A-1/C-1).
2. **Untagged-gates residual (SC5)** — owner call, vehicle `[CONSTRAINT-GATES-UNTAGGED]` (A-2/C-2).

**Closed at the re-verification pass, 2026-08-14:**
3. ~~**A-3, the refused `@inapplicable:` example**~~ — **CLOSED.** Fixed by the implement resume via
   route (a); re-verified by the auditor end to end. The corrected example generates and seals, the
   marker's reason reaches the generated catalog, both fixture citations behave as cited, and all
   three surfaces are consistent with the D9 refusal stated beside the example.
4. ~~**A-4, the unreproducible test-file count**~~ — **CLOSED.** Method recorded; **55** reproduced
   from the written method by an independently written implementation, matching the auditor's
   original independent count. Both places the number appears now agree.

**Not checked:**
- **The pre-edit sweep (Table 1) was not re-run.** It cannot be — the edits have landed. I verified it
  by a different route: 11 quoted hits confirmed still present in source with their dispositions read
  in context, plus the arithmetic (70 rows + 64 aggregated = 134 raw; +2 from the Phase 4 scope
  correction = 136). I did not verify the remaining ~59 individual rows one by one.
- **The vendored-corpora aggregation** (64 hits, 15 rows) was accepted on its recorded reasoning and
  its arithmetic (15+4+45=64), not re-grepped file by file.
- **agentic-mbse and TEAx content beyond the sweep terms and the named additions.** I verified the new
  teaching is present and that the sweep is clean; I did not read either repository's full diff for
  prose quality or internal consistency, and A-3 is the kind of defect that reading would surface.
- **The six report states and feed-strategy opt-in in TEAx** were confirmed present by grep, not read
  for accuracy against the shipped TEAx behavior. No TEAx test suite was run.
- **Byte-identity of generated baselines** was not separately gated; the licensed suite covers it, and
  no generated path is in any item commit.
- **Whether ADR-009's back-registration is the right ADR convention** for this repo long-term. It was
  a plan-stage design call (D-1), recorded, and I checked only that it was followed.
- **Nothing was pushed and no PR exists.** Epic close and `pre_pr` remain the owner's.
