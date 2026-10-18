# Design Review, round 2: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a)

**Design:** `.project/active/subset-profile-conformance/design.md` (revision 2, at `79614a91`)
**Spec:** `.project/active/subset-profile-conformance/spec.md` (with `spec-review.md` Resolutions)
**Review File:** `.project/active/subset-profile-conformance/design-review.md` (this file replaces the round-1 review; round 1 is in git at `315f9e88`)
**Date:** 2026-10-18

Checked against sysml-codegen `subset-conformance` at `26cfc841` and the agentic-mbse sibling worktree at its current `subset-conformance` head. Also read: spike S1 findings, `briefs/align.md`, the round-1 review, and `.claude/rules/`. Product-lens re-run; its block is appended to `product-lens.md`.

---

## The Point

**[INFERRED]** (ratified by owner, 2026-10-18) Prove, with evidence independent of the screen, that the shared subset contract in agentic-mbse matches what the generator actually does, and make drift between them fail a test in sysml-codegen. Test volume is not the goal, and neither are tests that check the screen against itself.

Why it matters: Item 1 wrote the contract as rule records and checked them once, against 80 probe runs of codegen `b5663c07`. Nothing fails today when the generator changes. Items 2b, 3 and 5 will tell modelers what will generate on the strength of this contract. Owner gates bound the work: RG-1 (generator accept/refuse), RG-2 (String policy), RG-3 (merges and ADR filing), and P-0003 (follow KerML, SysML v2 and SysIDE, no workarounds).

## Fundamental Assessment

**Sound. Verdict Revise, with four Major fixes that are each a sentence or a short list in the design and can be verified without another review round.**

- **The round-1 tripwire no longer fires.** The design now says plainly that enforcement of ADR 0001 invariant 1 is split, with a table of which repository runs which check (§ Cross-repo enforcement). It stages the right amendment (cases replace probes). The product-lens agrees: neither structural smell fires (ledger, "design rev 2" block).
- **The core is unchanged and still right.** Two stored answers per case, a pure agreement test between them, and a hand-edited disagreement record. Screen mutations now count only when they break agreement with the stored generator answer (D5), which closes the self-check route round 1 found.
- **The two new mechanisms are the right kind of mechanism.** They have fixable defects, covered below.
  - **D13, the receipt.** It is the smallest thing that makes agentic-mbse's own suite fail when a contract change skips the codegen check. There is no CI, and agentic-mbse cannot import codegen, so no simpler mechanism gives the same guarantee. But its file list is hand-written and already misses the agentic-mbse modules the generator imports most (R2-M1). It also lands too early, which would force dozens of re-stamps during 2a itself (R2-M4).
  - **D14, packaged cases.** Given the `[HARD]` boundary (codegen reads agentic-mbse only through its package) and O2 (one copy of each model), package data is the only placement left, and its size is trivial. The defect is in D4: it makes the runtime record loader read the packaged cases, and that breaks agentic-mbse's synthetic-record tests (R2-M2).
- **One gap was not visible in round 1.** The live route rebuilds every refusal object field by field, so the new `reason` field would be silently dropped before the harness sees it (R2-M3). D5's mutation judgment depends on that field.

---

## Round-1 must-fix status

| Round-1 item | Status | Where in revision 2 |
|---|---|---|
| C1 ownership move unstated, no gate | Resolved, with R2-M1 and m1 on the gate | D4, D13, § Cross-repo enforcement, staged `adr-0001-amendment.md` |
| C2 agentic-mbse loses screen-on-real-model tests | Resolved | D14 keeps and repoints `test_subset_profile_rules_{instantiation,modelwide}.py`; Appendix B lists every touched file, except R2-M2 |
| M1 screen mutations self-check | Resolved | D5 "Screen mutations", Required Invariant 6 |
| M2 write path unspecified | Resolved | D3 (no writer, writer-guard test, entry checks), Invariant 2 |
| M3 fixture rule too strict | Resolved | § C "Multi-construct fixtures (O7)" |
| M4 two meanings of `reason` | Resolved | `SubsetDiagnostic` is a separate type (§ A Renderer) |
| M5 `Diagnostic` in the snapshot encoding | Resolved | D8: encoder unchanged, refuses a reason-carrying `Diagnostic`, pure test that the 22 snapshots carry no diagnostics. Verified: `envelope.py:310` calls `require_projectable` (`graph.py:922-926`) before sealing. The design cites `validate`, which is the wrong method; the claim holds (m8) |
| M6 generation-stage refusals have no code | Resolved | D15 `GenerationCode` |
| M7 split has no estimate; E5 in the tail | Resolved, trigger needs a measurable proxy (m7) | § E estimate, E5 in P7, P7 dependency |
| m1–m9 | Resolved | D2, O8, D7 (packaged `agentic_site_witnesses`), D6 cites invariant 6, "codegen CI" gone, Appendix B, `mutate.py` name table, scanner fold-in |

---

## The two new mechanisms

### D13: the gate receipt (`codegen_gate.json`)

**How it works, in plain terms.** Before merging an agentic-mbse change to the contract code, someone runs `codegen_suite.py`. It exports both repos at committed revisions into a temporary tree, installs them, and runs codegen's licensed subset-profile tests. On a pass it writes a small JSON file into agentic-mbse holding a hash of the covered files. A pure agentic-mbse test recomputes the hash on every run and fails when it differs. So any edit to a covered file turns agentic-mbse's own suite red until the gate is run again.

**Is it sound?** Mostly yes.
- It hashes file contents, not revisions. So committing the receipt does not invalidate it, and a merge whose result differs from both parents correctly needs a fresh run.
- It puts the obligation in the repository where the change is made. That matters because Items 3 and 5 read agentic-mbse directly, so a check that runs only in codegen would come too late.
- Its stated limit is honest: a hand-computed hash passes. One correction: the design says a forged receipt is "visible in the diff". It is not, because a forged receipt and a real one produce the same diff. The honest limit is that a forged receipt cannot be told apart from a real one (m3 offers a cheap partial check).

**Is it proportionate, or ceremony that will be re-stamped routinely?** It will be re-stamped routinely, and that is acceptable, because each stamp can only come from a real gate run. The risk is the other kind of routine: an agent faced with one red test "fixes" it by recomputing the hash. Two design choices make that more or less likely.
- **Too many stamps during 2a (R2-M4).** P1 lands the receipt test. P2–P6 then edit records, cases and `sysml/` code many times, and every edit turns agentic-mbse red until a licensed gate run. During 2a the gate adds nothing: codegen's path dependency already runs every codegen test against the live sibling working tree. That is exactly the setting in which re-stamping becomes reflexive.
- **Too few files covered (R2-M1).** A list that misses files gives a green receipt for an ungated change, which is worse than no receipt.

**Is there a simpler mechanism with the same guarantee?** I looked at four and none matches it.
- A git pre-push hook is not versioned or enforced.
- Adding the extractor and evaluator code to `SUBSET_PROFILE_VERSION`'s digest only fails on the codegen side, and only when codegen's suite runs.
- An agentic-mbse test that runs codegen's suite itself makes agentic-mbse depend on its downstream checkout and the license.
- Relying on the owner's `pre_pr` alone has no check behind it.

Keep D13, with the fixes below.

### D14: conformance cases as agentic-mbse package data

**Is shipping test inputs in the product wheel justified?** Yes, as the least-bad placement.
- **Reading through the sibling path** (models in agentic-mbse `tests/`) breaks the spec's `[HARD]` boundary as written. The editable install would make it work today, but that is the coupling the boundary forbids.
- **Excluding `subset_cases/` from the wheel** while keeping it under `src/` works only for editable installs. Codegen's tests would then break silently on a wheel install of agentic-mbse.
- **A separate test-data distribution** adds a second package, a second path dependency and a version relation between the two, all for about 100 KB. That is not proportionate for one owner.
- **Size is a non-issue.** The 80 probe models total 25 KB (`du -cb …/probes/*/model.sysml`). The 1.3 MB probe directory is mostly `observation.json`, which retires.

**What it costs.**
- **The design's precedent is weaker than stated (m5).** `extraction/check_corpus/` is read at runtime by `agentic-mbse extract --check` (`extraction/check.py:120`). It is a product feature's data, not test inputs for another repository.
- **What wheel users get.** They get inert example models with the screen's verdict for each. That is defensible, and arguably useful to Item 5's guidance, but the design should say so rather than lean on the precedent.
- **The `case.json` layout becomes an interface between the repositories.** It has no version. Gate runs catch a layout change, so this is acceptable, but a `schema` field would make the failure clearer (m5).
- **The real defect is D4's loader check (R2-M2).** It is covered in the next section.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns (minor)

- All six criterion groups trace to design elements. The round-1 gaps (B5 screen half, C2, E5) are closed.
- The spec staged the ADR 0001 amendment as "cases admissible alongside probes" (`[INFERRED]`). The design says why it replaces that text. That is the right handling of an inferred item.
- **The P-0001 amendment is missing (m4, lens design-rev2-F1).** agentic-mbse `.project/product/0001-executable-subset-contract.md:3, :17` promises "refused only when a retained probe of the pinned generator observed that refusal". D4 makes that false. It needs a staged amendment beside ADR 0001's.
- **Two group A tests can't pass in P1 (m6).** The mapping-witness test ("every (reason, code) pair has a case") and occurrence parity over "every case whose summary has nodes" need P2's cases. P1 can't satisfy them.

### 2. Pattern Consistency
**Assessment:** Concerns

- **D4 changes the loader's job (R2-M2).** Today `load_rule_records(text)` is pure over text, and its docstring (`subset_profile.py:587-596`) leaves checking that each cited probe certifies to a test. D4 moves the "case exists in the package and shows the pair" check into the loader, which breaks that split for no stated gain.
- **Reuse is good.** It keeps `codegen_suite.py`, moves the probe helpers to `isolated_tree.py`, folds the narrow scanner into `site_scan.py` and keeps the `tests/expectations` idiom.

### 3. Abstraction Quality
**Assessment:** Concerns

- `SiteReason`, `GenerationCode` and `SubsetDiagnostic` are each justified and kept small.
- **The carrier list is incomplete (R2-M3).** D8 names the four exception types and `Diagnostic` as carriers. But the live route turns every refusal into a fresh object in `orchestration/elaborated_pipeline.py:289-356` (and `:423`, `:438-452`, `_readiness_with_referent`). `_diagnostic_with_referent` (`:446`) rebuilds `Diagnostic` field by field, so a defaulted `reason` is dropped on every path through it. Two raising types that pass through there, `ExactTypeError` (`:315`) and `ExpressionInventoryError` (`:297`), are not among D8's carriers.

### 4. Duplication Avoidance
**Assessment:** Pass

- One copy of each model. The account's codegen half lives once, in codegen. One normalizer. The occurrence seed moves, as invariant 6 already decided.

### 5. Data Structure Clarity
**Assessment:** Concerns (minor)

- The receipt holds "the sha256 of those files, the codegen revision and the outcome". It does not say whether the hash is taken from the archived tree at `--agentic-rev` or from the working tree. Hashing the working tree would let uncommitted, untested edits into a receipt (m2).
- `outcome` is redundant if only a passing run writes the receipt (m2).
- Appendix A's schema is clear.

### 6. Route Safety
**Assessment:** Pass

- O8 states the per-site condition for turning a plain exception into a coded refusal. The encoder refuses a reason-carrying `Diagnostic` loudly rather than dropping it.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- B2, B3 and B6 now rest on S1 evidence, and B6 names its fallback.
- **Hidden bet H5: "the covered file list is everything the generator and screen take from agentic-mbse."** It is false today (R2-M1). Codegen imports `agentic_mbse.sysml.expression_ir` 12 times, `syside_adapter` 9 times, and also `expression`, `constraint_extraction`, `constraint_facts`, `data_models`, `expression_facts`, `qualified_names`, `helpers`, `types` and `agentic_mbse.errors`. The screen imports `subset_facts`, `occurrence_facts`, `fact_refs`, `expression` and `constraint_extraction`. None of these is on D13's list.
  - Why it matters: agentic-mbse's own tests run only the screen. So a change in `expression_ir.py` that moves the generator on a packaged case leaves agentic-mbse green and the receipt valid. That is exactly the drift D13 says "only this run catches".
- **Hidden bet H6: "the codegen revision in the receipt is the one that merges."** Nothing checks it (m1).

### 8. Reader Comprehension
**Assessment:** Pass

- The Core Concept and "where each fact lives" read in one pass. The Orchestrator decisions table makes provenance clear.
- D13's "What only this run catches" paragraph is the clearest statement in the design of why the gate exists.

---

## Issues by Severity

### Critical

None.

### Major

- **R2-M1. The receipt covers a hand-written file list that misses the agentic-mbse modules both halves run.** (Bets H5 / D13)
  - *Fix:* cover a set computed by pattern, not by name: every file under `src/agentic_mbse/sysml/` (code, TOML and `subset_cases/`) plus `src/agentic_mbse/errors.py`. Say in D13 that a hand list was rejected because it already missed `expression_ir.py`.
  - *Cost:* more agentic-mbse edits need a gate run. That is the honest cost, because codegen consumes those modules.
- **R2-M2. D4 puts the packaged-case check in the runtime loader, which breaks synthetic records and makes the loader read test data.** (Pattern / D4, D14)
  - *What breaks:* `tests/helpers/subset_records.py:85, :101` builds synthetic records that cite `probe:<pair>` for every pair and loads them with `load_rule_records`. Appendix B marks that helper "unchanged". Under D4 those records fail to load, and switching them to `case:` would need a packaged case for every synthetic pair.
  - *Fix:* the loader checks only the citation's form (kind `case:`, ID prefix names the pair), as it does for `probe:` today. An agentic-mbse test checks that each cited case exists in the package and that its `case.json` shows the pair, which keeps today's split between loader and test. Update Appendix B for `subset_records.py`, and D14's last sentence ("the loader requiring cited cases … enforces the placement" becomes "the citation test").
- **R2-M3. The live route drops `reason` when it rebuilds refusals, and two raising types have no carrier.** (Abstraction / D8)
  - *Fix:* add `orchestration/elaborated_pipeline.py`'s converters to D8 and the Component Overview (`:289-356`, `:423`, `:438-452`, `_readiness_with_referent`, `_semantic_evidence_diagnostic`). Each must copy `reason`. Add `ExactTypeError` and `ExpressionInventoryError` to the carriers, or say why their sites need none.
  - *Test:* add a pure-or-licensed check that a reason set at a site arrives in the harness's `extra={"refusal": …}` observation, so the loss fails by name rather than as surviving mutations in P2.
- **R2-M4. The receipt test lands in P1, which forces re-stamping through P2–P6 when it guards nothing.** (Proportion / D13, Handoff)
  - *Why it guards nothing then:* during 2a, codegen's tests already run against the live sibling tree through the editable path dependency.
  - *Fix:* P1 keeps the gate script, because the baseline run uses it. Move the receipt test and the first real receipt to P7, written by a gate run at the final revisions of both repositories, so the receipt applies from merge onward.

### Minor

- **m1.** (lens design-rev2-F1) Nothing binds the receipt's codegen revision to the codegen commit merged alongside. Either add a `pre_pr` step that checks the receipt's revision is an ancestor of the codegen branch being merged, or list it as a limit next to the forged-receipt limit.
- **m2.** Say that the digest is computed from the tree exported at `--agentic-rev`, not the working tree. Drop `outcome`, or say what a non-pass receipt means. Make the receipt test's failure message name the exact command to run.
- **m3.** Correct "visible in the diff": a forged receipt cannot be told apart from a real one. Optional cheap check: the receipt lists the case IDs whose parametrized codegen tests passed, and the agentic-mbse test requires every packaged case ID to appear. A forger who only recomputes the hash then fails; a deliberate forger still passes.
- **m4.** (lens design-rev2-F2) Add a staged amendment of agentic-mbse P-0001 ("refused only with a recorded generator probe") to "Decision records to file". Filing is RG-3.
- **m5.** Restate D14's "Why". `check_corpus/` is runtime data for `extract --check`, not a test-input precedent. Say what wheel users get (inert minimal models with the screen's verdict) and why that is acceptable. Consider a `schema` field in `case.json`, since its layout is now read across repositories.
- **m6.** Two group A tests depend on cases that arrive in P2: the mapping-witness test and occurrence parity over cases. Say they land in P2, or that P1 lands them over the 80 probe models moved first.
- **m7.** The split trigger's "more than 7 engineer-days" is not measurable in an agent-run pipeline. Use a countable proxy, such as head sites with a reason and witness at P5's close against the head's site count, or keep only the re-estimate clause.
- **m8.** D8 and the Research Findings cite `InstanceGraph.validate` as raising on diagnostics. The method that does it is `require_projectable` (`graph.py:922-926`), called before sealing at `snapshot/envelope.py:310`. The claim holds; fix the citation.
- **m9.** (lens design-rev2-F3, narrowed) Say that the receipt is regenerated on the result of each coordinated merge. Item 4 changes that merge before 2a are then covered by 2a's final gate run on the merged tree. Item 4 changes after 2a hit the receipt test.

---

## Recommendations

1. **Make the receipt cover what the generator and screen actually import (R2-M1).** Use a glob over `sysml/` plus `errors.py`. Of all the fixes, this one closes a real drift path.
2. **Move the case-existence check out of the loader into a test (R2-M2)**, and fix Appendix B for `subset_records.py`.
3. **Name the live-route converters as `reason` carriers and test that the reason arrives (R2-M3).** Without it, P2's mutation tests fail for a reason that looks like shadowing.
4. **Land the receipt test in P7, not P1 (R2-M4).** That keeps the receipt from becoming something people re-stamp out of habit.
5. Minors in the same pass. m1, m3 and m4 come from the product-lens and keep the limits stated honestly.

These are objectively checkable edits to the design. Per `.claude/rules/pipeline.md`, the orchestrator can verify them against this list and go on to `/_my_plan` without a third review round.

---

## Resolutions

None yet. This review ran non-interactively for the orchestrator. No owner or orchestrator resolutions have been recorded.

---

**Overall:** Revise. The foundation is sound and the round-1 must-fixes are resolved. R2-M1 to R2-M4 must land in the design before planning. No further review round is needed if they land as written.
**Next Steps:** Record resolutions here, then return to the design agent with this review. The reviewer does not edit the design. After the design agent applies the fixes, verify them against the Major list and proceed to `/_my_plan`.

**Not checked:** how often the covered agentic-mbse files changed recently (the `git log` query was not permitted in this session), so the re-stamp rate after merge is estimated, not measured. Also not checked: how long one `codegen_suite.py` run takes end to end (tree export and `uv sync` included); whether any agentic-mbse wheel was ever published to an index; whether `OccurrenceResolutionError` and other occurrence-stage refusals pass through a converter not listed in R2-M3.
