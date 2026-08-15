# Spec Review: Constraint Semantics and Design-Search Feasibility Contract

**Spec:** `.project/completed/20260814_constraint-semantics-contract/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md` (generated from `claude-pack/commands/_my_spec.md`)
**Review File:** `.project/completed/20260814_constraint-semantics-contract/spec-review.md`
**Date:** 2026-08-12

---

## Reality Check

**Concerns, but fundamentally sound.** This is the right work item. The plain-versus-asserted distinction agrees with the current profile and the official SysML/KerML semantics, and the main implementation gaps reproduce in the current code: calc-definition owners have no scope branch, the catalog is built only from instance-graph constraint nodes, and the projector drops the report aggregator when no assertion executes. Design would still be misled by the current coverage denominator, the claim of full CATF coverage while most CATF guards remain out of executable scope, and a circular totality-gate formulation. Those are targeted contract revisions, not a reason to discard the work item.

Official standards checked: [SysML v2.0 Part 1](https://www.omg.org/spec/SysML/2.0/Language/PDF), especially the constraint/assertion semantics in clauses 7.20 and 8.4.16; [KerML 1.0](https://www.omg.org/spec/KerML/1.0/PDF), especially invariant semantics.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The TEAx policy vocabulary in “Study policy” is wrong at the boundary the section names. The spec says `violation → reject` and `all_satisfied → feed-strategy` (`spec.md:196-203`), but those are generated-report tokens. TEAx first maps them to runtime-owned `violated` and `satisfied` (`packages/teax-simkit/simkit/evaluation/evidence.py:38-50`; `evaluation/projection.py:48-64`), and policy dispatches on the canonical tokens (`study/policy.py:73-80,133-150`). The requirement must name both vocabularies and the normalization seam. Otherwise design can add the partial token on the generated side while leaving projection or policy unable to consume it.

**L1-2 · Direct claim:** The ADR obligation is misgraded as `[NEED]` (`spec.md:207-211`). Its stated source is the product-lens gate, and that ledger records it as an agent finding (`product-lens.md:25-34,112-113`). Under the spec-generation contract, `[NEED]` means the owner stated the outcome. Ratification would leave this agent-originated rule `[INFERRED]`; absent a separate owner-originated statement, the tag must change. It is also a workflow obligation, not a product behavior.

**L1-3 · Rewrite request:** The Problem says this spec captures a “settled product rule” from eight owner-ratified rulings (`spec.md:52-55`), while the requirements preamble correctly says those rulings are agent-proposed, ratified, and challengeable (`spec.md:98-101`). Capture fidelity reserves “settled” for owner-originated substance. Rewrite the status claim so it says these are ratified agent recommendations, then keep the owner-stated needs distinct.

**L1-4 · Question to the user:** Two `[OWNER-VERBATIM]` quotes in the spec are not present in the supplied handoff or research: the design-search framing (`spec.md:17-19`) and the equality-guidance instruction (`spec.md:136-138`). They may have come from the intervening Q&A, but this fresh review cannot verify them. **Do these reproduce your words exactly?** If yes, record that confirmation in this review or cite a durable Q&A capture. If not, correct their text or grade.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The central coverage population is internally unresolved. Q1 says a plain `constraint` is deliberately descriptive and never a gate (`spec.md:109-117`). Q5 then says coverage counts authored usages and a partial headline applies whenever exclusions exist (`spec.md:184-194`). Taken literally, adding one descriptive constraint downgrades an otherwise fully assessed set of asserted physics gates to partial coverage and changes study policy. **Should feasibility coverage count only applicable asserted gates, while the catalog separately reports every authored usage, or should descriptive/plain/requirement-side usages intentionally make the design-search result partial?** I recommend separate counts: inventory totality covers every usage; feasibility coverage is over applicable asserted gates.

**L2-2 · Question to the user:** The spec makes a vacuous asserted constraint warning-grade and says it does not block “full” coverage (`spec.md:165-169,192-194`). That is reasonable for an intentionally unused library definition, but dangerous when zero occurrences mean the modeler forgot a typing or instantiation relationship. CATF already supplies the dangerous shape: five part-definition-owned checks attach to nothing because the design parts are untyped (research `:153-159`). **May an asserted-but-vacuous usage coexist with full feasibility coverage by default, or must the author explicitly mark it inapplicable before it stops counting as missing assessment?** Without that decision, the product can report full coverage while an intended gate is detached.

**L2-3 · If-then tradeoff:** The scope is defensible **if this is an umbrella behavioral contract that will be decomposed**. It is too large **if the next step is one technical design and one implementation plan**, as the footer currently says. The item combines normative contract amendments, two documentation stacks, canonical usage inventory, catalog and report schema changes, TEAx projection and study policy, a new CATF derivative, two unrelated defect fixes, an ADR, verification-row regrading, and coordinated work in three repositories. Treating all of that as one shippable item will couple decisions that have different owners and validation routes. I recommend making this the umbrella contract, then decomposing at least authoring/docs, totality/catalog, report/TEAx, CATF migration, and the two defects into auditable child items.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** “The migrated CATF derivative ... executes with full coverage” is not currently a testable success criterion (`spec.md:80-82`). Of CATF's 65 usages, 51 are calc-definition-owned and five are part-definition-owned with no occurrence; the spec explicitly excludes building calc-definition gate execution from this item (`spec.md:242-245`) and requires an owner disposition table only for the nine instance-reaching constraints (`spec.md:229-232`). A faithful implementation can therefore migrate nine gates, leave most intended physics guards non-executable, and still argue that “full” means all currently applicable gates. The criterion must name its denominator and require a disposition for all 65 authored usages, or defer the full-CATF claim until the calc-definition capability lands.

**L3-2 · Direct claim:** The totality check is circular as written. The spec requires the check to read “the graph and embedded catalog” (`spec.md:160-164`), but current elaboration adds constraint nodes only after owner-to-scope expansion (`src/sysml_codegen/elaboration/elaborate.py:522-539,997-1005`), and catalog assembly iterates only those nodes (`src/sysml_codegen/elaboration/project.py:1083-1094`). Comparing that graph with its catalog cannot detect the 56 usages that vanished before either representation existed. Preserve the one-authority rule, but add a requirement that the canonical graph/catalog authority carry a complete authored-usage domain before occurrence expansion. The gate must compare dispositions against that domain, not compare two projections of the same already-truncated set.

**L3-3 · If-then tradeoff:** The nine CATF intent classes and tolerance values are deferred as owner sign-off “during migration” (`spec.md:229-232,268-269`), yet the same spec requires the derivative to generate, execute, and reject an unphysical candidate. Those are domain requirements, not choices a technical designer should make. **If CATF migration remains inside this work item, resolve them before design. If it becomes a child item, give that item its own spec and owner checkpoint.** Leaving them as design deferrals makes the current document incomplete as the implementation contract it claims to be.

### Lens 4 — Hygiene

No material hygiene finding beyond the provenance and process-placement issues above.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The human-facing contract relies on private review labels that have no durable decision record in Related Artifacts: Q1–Q8, `R-POL-4`, and `lens spec-F1` through `spec-F8` appear throughout the requirements and success criteria (`spec.md:89-94,109-149,157-218,256-282`). The reader must reverse-engineer which conversation or ledger each label names before they can tell what was decided. Preserve traceability, but make the requirement text stand alone and cite one durable ruling record for the Q labels; keep product-lens finding IDs in the ledger or citations rather than in the primary success criteria.

---

## Engagement Summary

**Overall take:** The spec has the right semantic direction and is grounded in real code and a rich-model measurement. I would not hand it to design yet because “coverage” still mixes descriptive constraints, asserted gates, and non-reaching usages; that ambiguity also makes the full-CATF success claim and study-policy contract unstable.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Decide whether plain/descriptive and requirement-side usages affect feasibility coverage, or only inventory visibility. I recommend separating those two totals.
2. **[L2-2]** Decide whether an asserted usage with zero occurrences may coexist with full coverage without an explicit inapplicability decision.
3. **[L3-1, L3-3]** Define what “full CATF coverage” means and either disposition all 65 usages now or move CATF migration into a child spec with the nine owner-chosen tolerances.
4. **[L2-3]** Confirm that this becomes an umbrella contract with child work items rather than one cross-repository implementation item.
5. **[L1-1, L3-2]** Require the two-stage headline vocabulary and a non-circular, canonical authored-usage domain before design chooses schemas.
6. **[L1-2, L1-3, L1-4]** Correct the ADR provenance and “settled” wording, and confirm the two owner-verbatim quotes.

---

## Resolutions

Recorded 2026-08-12 by the authoring session; owner decisions marked pending until answered.

- **L1-1 — ACCEPTED, fixed.** New `[HARD]` requirement names both headline vocabularies and the
  projection normalization seam (`CANONICAL_HEADLINE`); the Q6 defaults are restated on the
  canonical vocabulary. A report-side-only token is defined as a failure, not a fallthrough.
- **L1-2 — ACCEPTED, fixed.** ADR obligation re-graded `[NEED]` → `[INFERRED]`
  (agent-originated process obligation from the product-lens gate).
- **L1-3 — ACCEPTED, fixed.** "Settled product rule" wording replaced: the spec now states the
  rulings are agent-proposed recommendations owner-ratified in a recorded Q&A, agent-grade and
  challengeable, with only the quoted owner statements owner-originated.
- **L1-4 — ATTESTED by the authoring session; owner confirmation requested.** Both
  `[OWNER-VERBATIM]` quotes reproduce the owner's messages from the 2026-08-12 session exactly;
  they are now durably captured with attestation in `rulings-20260812.md`. Owner asked to flag
  any discrepancy when resolving the open decisions.
- **L2-1 — RESOLVED (owner-selected 2026-08-12): two totals.** Feasibility-coverage denominator
  = applicable asserted gates; inventory totality separately covers every authored usage. Spec
  coverage requirements rewritten; headline success criterion now says "asserted".
- **L2-2 — RESOLVED (owner-selected 2026-08-12): vacuous counts as missing assessment.** Partial
  coverage until fixed or explicitly dispositioned inapplicable (mechanism to design). Supersedes
  the earlier "vacuous doesn't block full" detail; Q3 severity requirement cross-references it.
- **L2-3 — RESOLVED (owner-selected 2026-08-12): umbrella + child items.** New Structure section
  in the spec; next step changed to `/_my_epic_plan`; the epic owns the Item 7 invalidation
  register.
- **L3-1 / L3-3 — RESOLVED (owner-selected 2026-08-12): all-65 disposition table.** CATF success
  criterion rewritten with the named denominator and per-class dispositions; the owner tolerance
  checkpoint lives in the CATF child item before its design.
- **L3-2 — ACCEPTED, fixed.** New requirement: the canonical authority records the complete
  authored-usage domain before occurrence expansion; the gate compares dispositions against that
  domain, never two projections of the truncated set.
- **L5-1 — ACCEPTED, fixed (with one retained mechanism).** Durable ruling record
  `rulings-20260812.md` created; Q-labels and lens-F labels now cite named durable artifacts
  declared in the requirements preamble; the R-POL-4 success criterion restated standalone.
  Retained: parenthetical `(Qn)`/`(spec-Fn)` citations in requirement text — they are citations
  to now-durable records, which is the traceability the finding asked to preserve.

---

**Verdict:** Revise

**Next Steps:** Record owner resolutions here by finding ID. Then re-run `my-spec` (or return to the spec-authoring session) and point it at this review to incorporate. The reviewer does not edit the spec.
