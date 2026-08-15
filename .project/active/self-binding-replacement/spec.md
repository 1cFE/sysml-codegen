# Spec: Self-Binding Replacement — Establish, Document, Migrate

**Status:** Draft (rev 4 — corrects qualified-reference semantics after F-6 attribution)
**Owner:** Reid W
**Created:** 2026-08-15 09:16 PDT
**Revised:** 2026-08-15 (rev 4)
**Complexity:** MEDIUM
**Branch:** main (codegen `9ce5548`)

---

## Problem

A modelled value can be bound into a calculation with a right-hand side that names the same
identifier as the parameter it feeds — `in availability = availability`. This reads as “feed the
owning part's attribute in.” It does not do that. The reference resolves to the calculation's own
input parameter, so the attribute's value never arrives and the calculation returns a confident
wrong number. Legal SysML, silently inert.

This is the defect family the ELABORATE-FIRST epic exists to delete, and it is the direct negation
of the product's design-search promise: if a varied design parameter never reaches the calculation,
the viability number is confidently wrong (`P-001`).

Three things follow, and together they are the work:

**1. The customer models cannot generate.** The exact route refuses this shape as
`SI_SELF_BINDING` before generation. The fusion-tea whole-plant model carries **15** such bindings.
The stellarator model carries **114**, including a literal `in R = R`. Fusion-tea must be migrated;
stellarator must be triaged once without reversing its July hold.

**2. The published teaching does not state the situational rule.** It gives two spellings of one
local fix and one sentence about a value on another part, without explaining why the situations
differ. It also contains four worked `in x = x` examples that the exact route refuses. The
agent-facing SysML authoring skill carries binding guidance but no self-binding warning, so an agent
can still author the blocked shape while following the published instructions.

**3. The owner restated the obligation from scratch.** The work must establish the right pattern
for each situation, document those patterns, fix the models to use them, and detect the wrong
`in R = R` pattern. The epic's former “two valid replacement forms” count was agent-authored under
an owner-verbatim stamp; it has been corrected at the source and does not govern this item.

**Why now.** Item 7's cutover landed and merged; the exact route is the only route. The motivating
fusion-tea model remains blocked from regeneration until its authored bindings are corrected.

### The three authoring shapes this item must distinguish

- **Make the names differ (D-5).** When the value is an attribute on the part that owns the
  calculation, rename the calculation input and bind it to the attribute, for example
  `in availability_in = availability`. The bare reference then lands on the outer attribute. This
  is the rule for all 15 fusion-tea sites and matches the existing codegen fixture.
- **Name the path (D-7).** When the value lives on a different part, name that occurrence path, for
  example `in driver_cost = driver.cost`. The reference lands on that occurrence's feature.
- **Qualify by owner (D-6).** SysIDE resolves a usage-qualified local redefinition to the exact
  feature owned by that usage. The shipped elaborator currently loses that owner before occurrence
  selection, which can produce a false missing/ambiguity or silently select a competing occurrence.
  That is codegen defect F-6, not the meaning of `::`; it is owned by the separate
  `qualified-reference-occurrence-anchoring` repair. This item must not teach the defect as a
  modeling rule. It still does not recommend this shape for the fusion-tea migration: D-5 remains
  the local migration form, and D-7 remains the advice for taking a value from another part.

## Success Criteria

- [ ] **Spine — an off-default mutation of a migrated fusion-tea design attribute reaches every
      and only its bound consumers.** This observable public behavior proves that the intended
      value arrives; generation without a diagnostic is not enough.
- [ ] **The behavior relied on by the situational rule is re-established by measurement on the
      shipped exact route.** D-5 and D-7 are measured directly. Any D-6 explanation is checked
      against the landed exact-owner repair, not today's positional defect. For each taught shape,
      the evidence identifies the feature the reference lands on and demonstrates the concrete
      value or diagnostic that follows.
- [ ] **A different candidate pattern found to resolve silently and wrongly is either fixed when
      the repair is small and contained, or filed with a name, owner, and vehicle.** Documentation
      alone is not a disposition for an unsupported silent form.
- [ ] **The guidance is organized by situation and teaches the applicable rule.** It tells authors
      to make names differ for an attribute on the part that owns the calculation and name the path
      for a value on another part. If it explains owner qualification, it states that codegen honors
      the exact usage owner SysIDE resolved after the separate repair; it never presents positional
      slot search as the language semantics.
- [ ] **The wrong self-named form is both explained and detected before generation.** The guidance
      states why `in R = R` binds the calculation input to itself, and the shipped codegen and
      agentic-mbse validation paths are confirmed to refuse it.
- [ ] **No document that forbids the self-named form still teaches it by example.** In particular,
      the four refused bindings currently in `agentic-mbse/docs/patterns/plant-idiom.md` are
      corrected, including the EXPOSE example at line 200.
- [ ] **The rule reaches the agent-facing SysML authoring surfaces.** The surfaces under both
      tracked `agentic-mbse/claude/` and `agentic-mbse/.claude/` trees are inventoried, and every
      live surface that can instruct an agent about calculation bindings either carries the rule
      or reaches one authoritative copy without leaving contradictory guidance behind.
- [ ] **The fusion-tea whole-plant model generates, seals, and captures a snapshot on the exact
      route with zero readiness diagnostics.** This is necessary but does not replace the spine
      mutation check.
- [ ] **The migration preserves the author's intended meaning while changing the referent.** The
      referent changes from the calculation's own input to the intended modelled value; arithmetic,
      physical values, and model physics do not change. A mechanical check establishes the bounded
      diff.
- [ ] **The stellarator model is run through the exact pipeline once and the result is recorded.**
      The triage names what breaks and files any follow-on. It fixes nothing and does not reverse
      the July owner hold.

## Known Requirements

- **[NEED]** The owner restated the outcome verbatim on 2026-08-15: *“We know what the RIGHT
  pattern(s) are for the given situation / We document those right patterns / We fix the models to
  use the right patterns. `in R = R` is the wrong pattern. I would like to detect the use of it so
  we avoid it in the future.”* The earlier form count does not carry into this requirement.
- **[NEED]** The rule is situational, and the agentic-mbse agents must know and understand the
  difference (`.project/active/self-binding-replacement/spec-review.md`, resolution
  L1-2/L2-2/L3-3, owner-verbatim agreement, 2026-08-15).
- **[NEED]** Stellarator receives triage only: one pipeline run, a record of what breaks, no fixes,
  and no reversal of the July hold (`.project/active/self-binding-replacement/spec-review.md`,
  resolution L3-4; owner-verbatim “triage is good,” 2026-08-15).
- **[INHERITED]** The epic's critical success factor, owner grade
  (`.project/backlog/epic_elaborate_first_architecture.md:31-33`): every consumed modelled value
  resolves to exactly one runtime source across all bound consumers; an unsupported authored form
  fails loudly before generation. The epic's `[OWNER]` mission invariant at `:84-86` adds that a
  public mutation reaches every and only the bound consumers.
- **[INHERITED]** Dispositions D-4 through D-7
  (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:604-627`): D-4 is
  `[OWNER-VERBATIM]`; D-5, D-6, and D-7 are `[AGENT] (ratified by owner, 2026-08-05)`. D-5 already
  carries the ratified bare-renamed-in-place recommendation for the customer migration. This item
  applies those semantics and does not silently reopen them.
- **[HARD]** The exact route refuses a self-named binding before generation, as a readiness finding
  rather than a warning, so an affected model produces no output
  (`src/sysml_codegen/extraction/source_evidence.py:230`,
  `src/sysml_codegen/elaboration/elaborate.py:2005`).
- **[HARD]** Redefinition (`:>>`) cannot name an enclosing part's attribute from inside a
  calculation usage. After `redefines`, the name resolves through the owning type's supertypes with
  the owner's own namespace excluded (KerML §7.3.4.5 and §8.2.3.5.1), and the redefined feature
  must otherwise be inherited from a supertype of its owning type.
- **[HARD]** *(corrected after F-6 attribution and the semantic corpus scan, 2026-08-15)* SysIDE
  resolves a usage-qualified local redefinition to a distinct usage-owned feature. Codegen retains
  that exact declaration and owner, but the current one-segment resolver normalizes to a feature
  slot before using the owner and then selects by consumer position. This can silently wire a
  competing occurrence (`u6`) or report false missing/ambiguity (`u4`, `u5`, `u7`). The separate
  `qualified-reference-occurrence-anchoring` item owns the broader invariant selected by the owner:
  every one-segment usage-owned leaf anchors its exact owner across all resolver consumers.
  Definition-owned inherited leaves remain on the definition route. This correction does **not**
  reopen the fusion-tea migration form; D-5 remains the ratified local shape.
- **[HARD]** SysML v2 Part 1 §7.17.2 is an action-parameter example. It does not state a shadowing
  rule or establish owner qualification as the normative repair for this calculation-binding
  collision. The rewritten guidance must not cite it as that authority.
- **[INFERRED]** Guidance examples must be parser-validated before publication. Specification text
  and grammar alone have proven insufficient: the current guidance teaches examples the exact
  route refuses.
- **[INFERRED]** A different silently wrong pattern is filed rather than expanding this
  docs-and-models item into production generator work, unless its fix is small and contained. This
  is the review's `[AGENT]` recommendation, not an owner-originated decision, and remains
  challengeable on evidence (`.project/active/self-binding-replacement/spec-review.md`, resolution
  L3-2).

### Provenance note on measured requirements

Measurements taken by the reverted 2026-08-15 work survive as evidence, not as settled fact. Any
`[HARD]` row marked “measurement pending re-establishment” must be reproduced under the approved
plan before design or implementation relies on it. Guidance and migration criteria gate on that
reviewed evidence, never on the reverted branches' own assertions.

## Non-Goals

- **The rest of Item 8:** the July IFE impact audit, certification repair including the
  source-identity requirement family and README, and the composed model→package→study proof thread.
- **The regeneration remainder of sub-item 1.** It stays with Item 8 at its declared home,
  `.project/active/elaborator-downstream/`, which must be created before that remainder is worked.
  That remainder includes package and contract regeneration, duplicate-field workaround removal,
  new study lineage where identity changed, TEAx compatibility through stock APIs, and acceptance-
  pin re-anchoring.
- **Migrating or repairing stellarator.** This item performs the one-run triage only.
- **Changing D-4 through D-7 support policy.** A newly discovered silent form may produce a small
  diagnostic repair or an owned follow-on, but this item does not relitigate the ratified forms.
- **Codegen fixtures authored to pin the refused shape.** Fixtures that exist precisely to prove
  the route refuses a self-binding keep carrying it.
- **Any change to arithmetic, physical values, or model physics.**

## Open Questions / Deferred to design

- **Agent-surface rollout:** which tracked surfaces should contain the rule directly and which
  should point to one authoritative copy, given the divergent `agentic-mbse/claude/` and
  `agentic-mbse/.claude/` trees. Design chooses the mechanism; the success criterion fixes the
  outcome.
- **ADR owner call:** whether the lasting modelling rule should be promoted to ADR-010. The review
  identified this as an owner decision but records no disposition; it is not silently delegated to
  design.
- **Push and pull-request sequencing** across the three repositories, given the pin order the epic
  has used previously.

---

## Change Record

### 2026-08-15 — qualified-reference semantics corrected; separate repair named `[OWNER 2026-08-15]`

The F-6 attribution report and semantic corpus scan proved that the positional behavior previously
described in this spec is a codegen defect, not the meaning of a usage qualifier. The owner selected
the broader exact-owner invariant for the separate repair and directed this spec to be corrected.
The D-5 local rename, D-7 cross-part path advice, and fusion-tea migration choice are unchanged.
Implementation and regression ownership lives in
`.project/active/qualified-reference-occurrence-anchoring/spec.md`.

### 2026-08-15 — work executed before this spec existed, then reverted in full `[OWNER 2026-08-15]`

Implementation ran before written requirements existed: the guidance was rewritten, 15 fusion-tea
sites were migrated, and two codegen gate repairs were made. The owner then ruled **“REVERT ALL.”**
The fusion-tea and agentic-mbse branches were deleted, the codegen edits were reverted, both model
and guidance trees were confirmed restored, and nothing was pushed or merged.

The three diffs remain as evidence under `reverted/` in this folder:

- `reverted/fusion-tea-model-migration.patch`
- `reverted/agentic-mbse-guidance.patch`
- `reverted/codegen-gate-repairs.patch`

The reverted work measured candidate-form behavior, generated the qualified migration, and compared
live and snapshot output. An independent audit reproduced its recorded counts and comparisons.
Those results remain evidence to re-establish under the approved plan; they do not select the
migration form or certify the new work.

Reverting the codegen gate repairs restored references to deleted Item-7 worktrees. That separate
defect is owned by `.project/active/dead-worktree-pins/`, not this item.

**Citation corrections retained from the audit:** the “owner's own namespace excluded” wording is
from KerML §7.3.4.5; §8.2.3.5.1 describes the corresponding abstract-syntax mechanism. The SysML
action example's qualifier points toward an enclosing usage name, not the definition-qualified
spelling used by ten sites in the reverted migration.

## Related Artifacts

- **Epic:** `.project/backlog/epic_elaborate_first_architecture.md` — ELABORATE-FIRST, Item 8.
  This item covers the restated sub-item 4 and the model-migration part of sub-item 1.
- **Required Reading:** none listed for Item 8 in the epic.
- **Contract (semantic authority):**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — D-4 through D-7.
- **Measured evidence (authority for the `[HARD]` binding-shape rows):**
  `.project/active/self-binding-replacement/spike/findings.md` — 2026-08-15 re-establishment on the
  shipped route at `6e3c18d`. Corrects the `SI_OCCURRENCE_AMBIGUOUS` row; records F-2 (agentic-mbse
  validator false-positive on D-6), F-3 (unhandled traceback on the D-5 rename collision), F-4
  (sideways reach), F-5 (chain source paths).
- **Prior evidence:** `.project/active/source-identity-binding-semantics-spike/authoring-form-table.md`
  — the 2026-08-05 probe table of six authored forms and their observed referents.
- **Spec review:** `.project/active/self-binding-replacement/spec-review.md` — final Revise verdict;
  all recorded resolutions incorporated in rev 3.
- **Product lens:** `.project/active/self-binding-replacement/product-lens.md` — append-only gate
  ledger; rev 3 explicitly resolves `spec-F1` through `spec-F6`, and the rev-4
  qualified-reference correction independently records `Gate: CLEAR`.
- **Separate qualified-reference repair:**
  `.project/active/qualified-reference-occurrence-anchoring/spec.md` — owns F-6 implementation,
  promoted u4–u7 coverage, shared-caller regressions, and the broader exact-owner invariant selected
  by the owner.
- **Qualified-reference evidence:**
  `.project/research/20260815-140630_qualified-binding-corpus-scan.md` — exact owner/edge census and
  snapshot/baseline disposition.
- **Post-approval stocktake:** a research report to be created after spec approval. It validates
  the two scope calls this spec depends on (the restated documentation obligation and the home for
  leftover regeneration work) and reconciles the epic's six-document repair list against the
  twelve retired-reference documents named by `CLAUDE.md`.
- **Design:** `.project/active/self-binding-replacement/design.md` (to be created)

---

**Next Steps:** After approval, run the bounded Item-8 stocktake research, then proceed to
`/_my_design`.
