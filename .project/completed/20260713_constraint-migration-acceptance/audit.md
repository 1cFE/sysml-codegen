# Audit: Migration, Docs, and IFE Acceptance (CONSTRAINT-EXEC Item 14 — epic-closing)

**Verdict:** Certify-with-notes
**Audited:** 2026-07-13
**Branch:** constraint-exec-epic
**Commit:** c4a8618 (Item 14 Phases 1–6; audit range `9dcd1ab^..c4a8618`)

---

## Summary

The in-repo work is correct and complete. The gain fix lands with exactly the promised
two-snapshot blast radius, the no-silent-drop mapping test is a genuine per-usage join over both
carrier surfaces (not a count match), the drop-manifest retirement is grep-clean, and the docs
flip is real. The acceptance passes with a **pre-decided, model-favoring boundary divergence** —
2294/2301 rows match and the 7 that differ are exactly the `eta*gain == 10.0` rows where the old
hand rule's strict `>` was *unfaithful* to the model's `>=`. That divergence is the epic
succeeding at its stated purpose (killing hand-rule drift), not failing acceptance. Three
integration gaps surfaced consumer-side; each narrows a certified item's (9/10/12) claim surface
and must become a follow-on item, not a permanent adapter. Net: certify, with an honest close-out
record required on the CSF wording, the three gaps, and one minor doc recount drift.

**Verification limits (read first).** Two legs I could not execute directly:
- **No test execution.** `uv run` is permission-gated in this headless session; the license `.env`
  is outside the sandbox and cannot be granted here. I verified the in-repo phases *statically* —
  reading the tests and mechanism code, and inspecting the committed artifacts (snapshots, grep
  gates, git diffstat). The gate numbers (suite 2330/23, mypy 76, ruff clean) are the implement
  session's self-report in `run-report.md`, re-run under license; I did not re-run them.
- **No cross-repo read.** agentic-mbse / teax / fusion-tea are outside the sandbox. Appendices A/B/C
  are the orchestrator-verified summaries; my adjudication of acceptance and the integration gaps
  rests on those summaries, stated as such where load-bearing.

---

## Findings

### Plan completion

All six phases verified against committed evidence.

- **Phase 1 (gain fix + re-land) — verified.** The D2 instance-self-redefinition tier is present in
  `_match_override` (`resolution/supplied_values.py:130-138`), correctly placed *below* the tier-1
  bare-override branch so it never shadows a genuine usage override. The owner-approved deviation
  for `plant_values` (its `gain` is a plain base-def literal default, not an instance `:>>`) landed
  as the def-scoped base-literal-default rung (iii) in `resolve_actual`
  (`analysis/constraint_lowering.py:252-260`), plus the mid-implementation demand-widening
  (`collect_bare_actual_demand`, `constraint_lowering.py:397`) that the run-report flags. Both
  target snapshots now carry `constraint_lowering_mode: "applied"` (lowered, not grandfathered_off).
  `GRANDFATHERED` is `frozenset()` (`scripts/capture_extraction_snapshots.py:129`) — INV-D holds.
- **Blast radius (INV-C, R2) — verified by git.** Across `9dcd1ab^..c4a8618` exactly two
  `extraction_snapshot.json` files change: `fusion_tea` and `plant_values`. The other 27 are
  untouched. This is the R2 backstop met exactly.
- **Phase 2 (mapping test) — verified structurally.** `test_constraint_migration_mapping.py` reads
  *both* carriers — eligible `concrete_entries` grouped by `usage_qualified_name` **and**
  `ctx.concrete_constraints` where `not eligible` (explicitly not the catalog, which filters to
  eligible-only) — joins per usage identity, and asserts no-silent-drop with a *named* justified
  carrier-free category (`REQUIREMENT`/`SATISFY`), failing loudly on anything else. This is the
  per-usage total function the design promised (D1/INV-A), not a count match. The anonymous-usage
  case raises `NotImplementedError` rather than mis-joining. Correct.
- **Phase 3 (retirement + grep-clean, INV-B) — verified.** In `src/`: zero hits for
  `report_dropped_constraints`/`render_constraint_report`, zero for the blanket `"not executable"`
  warning, zero for `dropped_constraints`. The kept generation-halt (`constraint_lowering.py:536`)
  survives and still raises `_generation_error` for BLOCK dispositions — it does not match the
  `"not executable"` grep because its message string breaks across a line, so the distinct-diagnostic
  boundary (spec `[HARD]`) holds cleanly. The documented deviation (keeping `collect_constraint_manifest`
  and its vocabulary because the kept mapping test calls the sweep directly) is sound and correctly
  recorded — design Appendix B named it a deletion target, and the mapping test's dependency
  legitimately overrides that.
- **D3 heterogeneous corpus — verified.** `fusion_tea`/`plant_values` omit `dropped_constraints`;
  sampled others (`wi014_toy`, `ife_plant`) retain it as an ignored vestige. Within-v3, no version bump.
- **Phase 4 (docs) — verified.** `modeling-assumptions.md:400` §8 retitled "Constraints Execute
  Under a Profile — Block List and Fallback"; new `reference/28-constraint-lowering-and-catalog.md`;
  the only `"not executable"` in `docs/` is one historical/decision-record line in doc 28. The
  verification-matrix CL family (REQ-CL-01..05) is present, each row backed by a real test file.
- **Phase 5 (W5a) — verified.** `contracts/verify.py`: `GENERATOR_MISMATCH` removed from the
  `strict` fatal check (it could never fire), reserved constant kept with a decision-record-phrased
  comment (states what is reserved and why nothing produces it — not an instruction to future
  agents). Correct disposition; correct capture-fidelity phrasing.
- **Phase 6 (reconcile) — verified as honest-partial.** In-repo boxes checked with commit links;
  acceptance/cross-repo boxes left `[ ]`/`[~]` with named pending notes. No self-certification of
  work other sessions had not landed.

### Spec conformance

Every in-repo success criterion is met (Prerequisite, Migration, sysml-codegen Docs slice, W5a
seam). The Acceptance criteria and the two cross-repo doc criteria are delivered by the S-FUSION /
S-MBSE / S-TEAX sessions and adjudicated below on the orchestrator summaries.

**One structural observation (not a defect).** The kept mapping-test guard (INV-A) is
`@requires_license`. Its protection therefore exists only in license-bearing runs; a license-free
CI silently skips it (memory `syside-license-key-explicit-env-needed` — a skipped guard reads as a
fake-pass baseline). This matches the design (the join needs live `build_pipeline_context`), but
the "kept guard" is only kept where extraction runs. Worth a one-line note in the epic close so a
future reader does not mistake a license-free green run for the invariant being enforced.

### Design conformance

Implementation follows design rev 2 — the five invariants (INV-A..E) each have concrete evidence
above. The recorded naming divergence (concept "source record" = per-usage; landed
`ConstraintCatalogSourceRecord` = per-definition; per-usage identity carried on the concrete
entry / unassessed record) is faithfully realized by the join and honestly boxed as an
agent-grade orchestrator decision — no Item 7 rework, no concept amendment. Correct handling.

### Code integrity

No slop or failure-honesty issues in the Item 14 diff. The gain-fix tier is demand-scoped and
literal-only (no over-broad match), the retirement deletes rather than shims, and W5a removes a
dead branch rather than papering over it. One minor doc drift below.

**[minor] Verification-matrix recount is incomplete.** `verification-matrix.md:14` was recounted
to `Distinct test files cited | 71`, but the "Related Documents" footer
(`verification-matrix.md:580`) still reads `(66 distinct test files cited by matrix rows)`. This
is exactly the index-vs-prose divergence the drift-modes memory warns about: the index summary was
updated, a second copy of the same count was not. Non-blocking; fix the footer to 71 (or make it
reference the index rather than restate the number).

---

## Adjudication 1 — Acceptance vs. the Critical Success Factor

**Criterion (epic line 15 / spec line 98):** "the IFE sweep's hand-coded viability rule is replaced
by the generated assertion and **every existing grid classification matches**" (spec: "100%
agreement... across the full grid").

**Result (Appendix C):** hand rule deleted; 2294/2301 exact matches; the 7 divergent rows are
exactly the `eta*gain == 10.0` epsilon-boundary rows — hand rule strict `>` vs. modeled `>=`.

**Disposition: MET-WITH-RECORDED-DIVERGENCE.** Not 100% as literally worded, but the 7 rows are not
an acceptance failure — they are the epic's whole reason for existing. The epic's Problem statement
is that "every design study re-implements the judgment by hand and drifts from the model." The 7
divergent rows *are* that drift, caught: `fusion_cycle.sysml:50` says `eta * gain >= threshold`
(inclusive), the hand rule at `sweep_ife.py:82` used strict `>`. At the boundary the model says
viable and the hand rule said not-viable — **the hand rule was unfaithful; the generated assertion
is correct.** The migration did not merely replace the rule, it corrected it. B3/D5 pre-decided this
divergence and required it surfaced in the committed table (epsilon window, not `== 10.0`), which
Appendix C reports it did. The CSF's second clause — "no modeled limit anywhere ends in silence" —
is independently met by the retirement + the no-silent-drop guard.

**What the honest close-out must say** (this goes to the owner): record it as **2294/2301 (99.7%)
match, with 7 boundary-row divergences where the model's `>=` corrected the hand rule's `>`** — do
**not** write a bare "100%." As worded, the criterion says "every ... matches"; a literal reading is
not satisfied, and a close-out that claims 100% would be false. The owner's call is only on wording:
either (a) mark the box met-with-divergence and re-word the criterion to "matches except where the
hand rule was unfaithful to the model," or (b) treat 99.7% + a correcting divergence as the criterion
met in substance. I recommend (a) — it keeps the record honest and makes the divergence a *feature*
of the result, not a footnote. (Adjudicated on the orchestrator-verified Appendix C summary; I did
not read the fusion-tea grid myself.)

---

## Adjudication 2 — the three integration gaps

All three surfaced during the fusion-tea acceptance, were bridged consumer-side, and are documented
in fusion-tea's `findings.md` (per Appendix C; I could not read that file directly). None invalidates
Item 14 — acceptance still passed *because* the consumer-side bridges made the wiring work. But each
is a real limitation that **narrows a certified item's claim surface**, and each must become a
follow-on item, not a permanent adapter:

1. **No standalone `constraint_catalog.json` (embedded in `model_contract.json` under different
   names) — narrows Item 9.** Item 9 certified `ModelContract`/`PackageContract` and "the constraint
   catalog." The catalog is not emitted as a discrete, catalog-named artifact; a consumer expecting
   one must reach into `model_contract.json` under renamed fields. This is a packaging/naming
   narrowing — and an echo of the same source-record naming divergence Item 14 already boxed.
2. **teax `CandidateBridge` is single-entry-channel-only — narrows Item 12.** The study/candidate
   surface can wire one entry channel; the IFE grid varies two parameters (`eta`, `gain`), so a
   multi-parameter candidate needed a consumer-side bridge. This narrows the claim that the study
   layer drives arbitrary multi-variable candidates.
3. **`PreparedEvaluator` hardcodes `ToyPlantParams` — narrows Item 10.** Item 10 certified a *generic*
   typed in-memory entry source whose "runtime types never import generated classes." A hardcoded
   `ToyPlantParams` is exactly that genericity claim failing for a different model's param class; the
   fusion-tea package needed a shim. This is the sharpest of the three — it contradicts a stated
   Item 10 invariant, not just a packaging convenience.

**Recommendation.** These are legitimate post-epic follow-on items (one per gap, in teax/sysml-codegen
respectively), and the epic close-out must record them as such. If `findings.md` leaves the three
consumer-side bridges as *permanent* adapters rather than recommending real fixes, that itself
reintroduces the drift this epic set out to kill — a bridge that hardcodes `ToyPlantParams` or a
single entry channel is a new single-source-of-truth violation. Per the brief, the findings are said
to recommend real follow-on items; I cannot confirm that wording from here, so I flag it as a
required close-out check: **confirm findings.md recommends fixes, not permanent shims, before the
epic is marked closed.**

---

## Adjudication 3 — Epic Success Criteria walk (8 boxes)

1. **[ ] Acceptance (CSF).** Delivered (Appendix C). Met-with-recorded-divergence per Adjudication 1.
   The box is still `[ ]` with a "Pending S-FUSION" note that is now stale — S-FUSION ran. **Action:**
   update to met-with-divergence (owner wording call), not a bare `[x]`, and record the 7 boundary rows.
2. **[x] Assertions lower/block; non-assert unassessed; manifest+warnings retire with 1:1 mapping.**
   Verified in-repo (grep-clean, mapping test, gain fix). Correctly checked.
3. **[x] Live/snapshot byte-identical; version rejection.** Verified (graph_rebuild mirrors the
   widening; 2-snapshot blast radius). Correctly checked.
4. **[ ] Violated assertion completes with 3 distinct outcomes.** Left `[ ]` as "out of Item 14
   scope" — its evidence is Item 7's. **Gap:** as an *epic* box it must trace to Item 7's certification,
   not sit dark. Reconcile action: point it at Item 7's audit and mark accordingly.
5. **[ ] Report aggregator exact schema / guaranteed exit ancestor.** Same as (4) — Item 7's evidence;
   trace it, don't leave bare.
6. **[ ] Contracts seal / ModelContract from graph / study-layer S6 invariants.** Item 14 touched only
   the `GENERATOR_MISMATCH` seam. Evidence is Items 9–12. **And this box is actively narrowed by all
   three integration gaps** — reconcile it against Items 9/10/12 audits *and* against the three
   follow-on items from Adjudication 2 before marking.
7. **[~] All suites pass in three repos.** sysml-codegen green (implement self-report; I could not
   re-run); agentic-mbse/teax "green except the 4 known" (Appendix B). Reasonable `[~]`; note the 4
   known teax skips explicitly at close.
8. **[~] Docs across three repos.** sysml-codegen verified done; agentic-mbse (Appendix A) and teax
   (Appendix B) now landed per the summaries. Can move toward `[x]` on the orchestrator summaries,
   with the caveat that I verified only the sysml-codegen slice directly.

**Net epic state:** boxes 2, 3 solidly closed on verified in-repo evidence; 7, 8 closable on the
cross-repo summaries; 1 met-with-divergence (owner wording); 4, 5, 6 are the real remaining
close-out work — not new *implementation*, but a **reconcile** that traces each to its delivering
item's certification (Items 7, 9–12) and folds in the three integration follow-ons. The epic is not
"fully checkable" until that trace is done and the three gaps are booked as follow-on items.

---

## Certification

**Certify-with-notes.** Checked and verified in-repo (static + committed-artifact evidence):
- Gain fix mechanism (D2 tier + def-scoped rung + demand-widening) and the exactly-two-snapshot
  blast radius (git); `GRANDFATHERED` emptied (INV-D).
- Both fixtures re-land lowered (`constraint_lowering_mode: applied`); D3 heterogeneous corpus.
- Mapping test reads both carriers, joins per-usage, no-silent-drop with a named carrier-free
  category (INV-A) — structurally sound as a kept guard.
- Retirement grep-clean in `src/` (INV-B); kept generation-halt survives and stays distinct.
- Docs flip (§8 retitle, doc 28, CL matrix family); W5a document-and-remove with correct phrasing.
- Phase 6 reconcile is honest-partial (no over-claim).

Adjudicated on orchestrator-verified summaries (not read directly): the acceptance grid
(met-with-recorded-divergence), the three integration gaps (real narrowings of Items 9/10/12), and
the agentic-mbse/teax doc + suite landings.

**Required before the epic is marked closed** (notes, not blockers to Item 14 itself):
1. Fix the acceptance close-out wording — 99.7% + 7 model-favoring boundary rows, never a bare 100%.
2. Book three follow-on items for the integration gaps (Items 9/10/12 claim-narrowings); confirm
   fusion-tea `findings.md` recommends fixes, not permanent shims.
3. Reconcile epic boxes 4/5/6 against Items 7/9–12 certifications rather than leaving them dark.
4. Minor: fix the `verification-matrix.md:580` footer recount (66 → 71).

**Not checked:**
- **No test execution.** The suite/mypy/ruff gate numbers are the implement session's self-report,
  re-run under license; I did not re-run them (`uv run` permission-gated, license `.env` outside the
  sandbox in this headless session). The mapping test and grandfather-carveout tests are
  `@requires_license` and were verified by reading, not running.
- **No cross-repo verification.** agentic-mbse / teax / fusion-tea diffs, the acceptance grid table,
  the prepare-once benchmark (~168×), the 200/200 verdict parity, and fusion-tea `findings.md` were
  taken from the orchestrator's Appendix A/B/C summaries, not read.
- **Prior items' contracts.** Items 5–12's own success criteria (epic boxes 4/5/6) are their audits'
  to certify; this pass did not re-verify them, only named the reconcile they still need.

---

## Epic-level assessment (for the close-out)

CONSTRAINT-EXEC set out to make modeled assertions execute and to kill the hand-coded viability
drift the IFE sweep embodied. It succeeded: the drop-manifest era is retired against a proven
per-usage no-silent-drop mapping, the gain gap that blocked the one real executable assertion is
fixed under a tight two-snapshot blast radius, the docs now teach the executable profile, and the
IFE acceptance replaced the hand rule with the generated assertion — matching 2294/2301 rows and, at
the 7 boundary rows, *correcting* the hand rule to the model's `>=`. That correcting divergence is
the epic's thesis proven, not a failed acceptance. What remains before the epic is stamped closed is
close-out bookkeeping, not build work: record the acceptance as 99.7%-plus-a-correcting-boundary
(never a bare 100%), book the three consumer-side integration gaps as real follow-on items against
Items 9/10/12 so no permanent adapter re-introduces drift, and trace the three "out of Item 14 scope"
epic boxes to the Items 7/9–12 certifications that actually deliver them. Item 14 itself is certified;
the epic is one honest reconcile away from closed.
