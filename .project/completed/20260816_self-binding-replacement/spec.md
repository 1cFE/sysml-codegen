# Spec: Self-Binding Replacement — Establish, Document, Migrate

**Status:** Closed — all functional criteria verified; tooling edge accepted as risk by owner
**Owner:** Reid W
**Created:** 2026-08-15 09:16 PDT
**Revised:** 2026-08-16 (rev 8)
**Complexity:** MEDIUM
**Branch:** main (codegen `0f89673`)

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
  feature owned by that usage. The elaborator used to lose that owner before occurrence selection,
  which produced a false missing/ambiguity or silently selected a competing occurrence.
  That is codegen defect F-6, not the meaning of `::`; it was owned and repaired by the separate
  `qualified-reference-occurrence-anchoring` item, which landed exact usage-owner anchoring in
  `src/sysml_codegen/elaboration/elaborate.py` on 2026-08-15 (`98970c9`). The shipped elaborator now
  honors the exact usage owner SysIDE resolved. This item must not teach the defect as a
  modeling rule. It still does not recommend this shape for the fusion-tea migration: D-5 remains
  the local migration form, and D-7 remains the advice for taking a value from another part.

## Success Criteria

- [x] **Spine — an off-default mutation of a migrated fusion-tea design attribute reaches every
      and only its bound consumers.** This observable public behavior proves that the intended
      value arrives; generation without a diagnostic is not enough.
- [x] **The behavior relied on by the situational rule is re-established by measurement on the
      shipped exact route.** D-5 and D-7 are measured directly. Any D-6 explanation is checked
      against shipped post-repair behavior; no conclusion may rely on the superseded positional
      behavior for a usage-owned leaf. For each taught shape, the evidence identifies the feature
      the reference lands on and demonstrates the concrete value or diagnostic that follows.
- [x] **A different candidate pattern found to resolve silently and wrongly is either fixed when
      the repair is small and contained, or filed with a name, owner, and vehicle.** Documentation
      alone is not a disposition for an unsupported silent form. *(`[DEF-OWNED-SIDEWAYS-REACH]`
      now records the owner-verbatim anti-fallback ruling, owner Reid W, the bounded
      `_resolve_leaf` implementation, independently verified on 2026-08-16.)*
- [x] **The guidance is organized by situation and teaches the applicable rule.** It tells authors
      to make names differ for an attribute on the part that owns the calculation and name the path
      for a value on another part. If it explains owner qualification, it states that codegen honors
      the exact usage owner SysIDE resolved after the separate repair; it never presents positional
      slot search as the language semantics.
- [x] **The wrong self-named form is both explained and detected before generation.** The guidance
      states why `in R = R` binds the calculation input to itself, and the shipped codegen and
      agentic-mbse validation paths are confirmed to refuse it. *(Re-audit 2026-08-16: agentic
      inspection failures now surface as `L2_CHECK_UNVERIFIABLE` errors, and the focused
      validation/integration suite passed 29 tests.)*
- [x] **No document that forbids the self-named form still teaches it by example.** In particular,
      the four refused bindings currently in `agentic-mbse/docs/patterns/plant-idiom.md` are
      corrected, including the EXPOSE example at line 200.
- [x] **The rule reaches the agent-facing SysML authoring surfaces.** The surfaces under both
      tracked `agentic-mbse/claude/` and `agentic-mbse/.claude/` trees are inventoried, and every
      live surface that can instruct an agent about calculation bindings either carries the rule
      or reaches one authoritative copy without leaving contradictory guidance behind.
- [x] **The fusion-tea whole-plant model generates, seals, and captures a snapshot on the exact
      route with zero readiness diagnostics.** This is necessary but does not replace the spine
      mutation check.
- [x] **The migration preserves the author's intended meaning while changing the referent.** The
      referent changes from the calculation's own input to the intended modelled value; arithmetic,
      physical values, and model physics do not change. A mechanical check establishes the bounded
      diff.
- [x] **The stellarator model is run through the exact pipeline once and the result is recorded.**
      The triage names what breaks and files any follow-on. It fixes nothing and does not reverse
      the July owner hold.

## Known Requirements

- **[NEED]** The owner restated the outcome verbatim on 2026-08-15: *“all I care about is: We know
  what the RIGHT pattern(s) are for the given situation / We document those right patterns / We fix
  the models to use the right patterns. `in R = R` is the wrong pattern. I would like to detect the
  use of it so we avoid it in the future. that's it, that's all I care about.”* The bookends are the
  scope ceiling. The earlier form count does not carry into this requirement.
- **[NEED]** The rule is situational, and the agentic-mbse agents must know and understand the
  difference (`.project/active/self-binding-replacement/spec-review-20260815-rev3.md`, resolution
  L1-2/L2-2/L3-3, owner-verbatim agreement, 2026-08-15).
- **[NEED]** Stellarator receives triage only: one pipeline run, a record of what breaks, no fixes,
  and no reversal of the July hold (`.project/active/self-binding-replacement/spec-review-20260815-rev3.md`,
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
- **[HARD]** SysIDE resolves a usage-qualified local redefinition to a distinct usage-owned feature.
  Since repair `98970c9`, the shipped elaborator anchors a one-segment usage-owned leaf on that exact
  owner across every resolver consumer that can reach the one-segment branch. The deep-literal-
  override lane cannot currently reach the branch and remains a named evidence gap under `P-002`.
  The pre-repair usage-qualified rows u4–u7 are superseded; post-repair authority is
  `tests/conformance/test_usage_owned_reference_anchoring.py` and the anchoring item's audit.
- **[NEED]** `[OWNER 2026-08-16]` SysIDE's resolved structure is authoritative; codegen must not
  invent a runtime occurrence through positional descendant search when a definition-owned
  qualified leaf has no occurrence on the consumer's lineage. The former F-4 sideways reach,
  reproduced at `0f89673`, was unsupported and now refuses with `SI_OCCURRENCE_MISSING`. The ruling is
  bounded to that lineage-miss fallback: definition-owned features mapped through the consumer's
  own occurrence lineage, exact usage-owner anchoring, explicit occurrence paths, D-5, and D-7 are
  unchanged. Owner-verbatim source and the implemented vehicle are recorded at
  `[DEF-OWNED-SIDEWAYS-REACH]` in `BACKLOG.md`.
- **[HARD]** An unindexed reference to an arrayed usage owner's leaf is deliberately scalar and
  refuses with `SI_OCCURRENCE_AMBIGUOUS`; `sum(comp_a::length)` therefore refuses while
  `sum(comp_a.length)` enumerates both occurrences. Before the repair, the first spelling silently
  selected a sibling, not either array element. **[OWNER 2026-08-16]** accepted that policy for the
  anchoring item and filed the author-facing diagnostic work as
  `[ANCHORING-ARRAYED-DIAGNOSTIC]` in `.project/backlog/BACKLOG.md`. This item records that boundary;
  it does not teach the dotted spelling as a workaround or expand self-binding guidance into
  arrayed-expression semantics.
- **[HARD]** SysML v2 Part 1 §7.17.2 is an action-parameter example. It does not state a shadowing
  rule or establish owner qualification as the normative repair for this calculation-binding
  collision. The rewritten guidance must not cite it as that authority.
- **[INFERRED]** Guidance examples must be parser-validated before publication. Specification text
  and grammar alone have proven insufficient: the current guidance teaches examples the exact
  route refuses.
- **[INFERRED]** A different silently wrong pattern is filed rather than expanding this
  docs-and-models item into production generator work, unless its fix is small and contained. This
  is the review's `[AGENT]` recommendation, not an owner-originated decision, and remains
  challengeable on evidence (`.project/active/self-binding-replacement/spec-review-20260815-rev3.md`, resolution
  L3-2).

### Provenance note on measured requirements

Measurements taken by the reverted 2026-08-15 work survive as evidence, not as settled fact. A
pre-repair result may be used only when current code proves its route unchanged or a post-repair run
reproduces it. The usage-owned rows u4–u7 are superseded by the exact-owner conformance test. The
definition-owned and D-5/D-7 routes survive on the anchoring corpus evidence. F-2 through F-5 were
reproduced at `0f89673`; see `verification/post-repair-spike-recheck.md`.

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
- **Arrayed-owner aggregation diagnostics or cardinality policy.** The owner accepted the shipped
  scalar policy and filed `[ANCHORING-ARRAYED-DIAGNOSTIC]` as the follow-up.

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

### 2026-08-16 — rev 8: assurance blockers and F-4 implementation complete `[AGENT]`

The two re-audit assurance gaps are closed in implementation: positional fixture mode validates
all operands before deletion, and Fusion Tea's retained cross-tree oracle rejects normalized-path
collisions before constructing its dictionaries. The owner-ruled F-4 vehicle is also implemented.
Qualified definition-owned leaves may map only through the consumer's occurrence lineage; a miss
refuses with `SI_OCCURRENCE_MISSING`. The one-occurrence-above, two-occurrences-above, and sibling
fixtures pin the refusal. Exact usage-owner anchoring, local definition-owned lineage mapping, bare
references, and explicit occurrence paths retain their established routes. The independent
re-audit verified SC1 and the F-4 repair, while reopening migration-tool path safety and
final-state delivery outside the functional success criteria.

### 2026-08-16 — rev 7: F-4 positional fallback ruled unsupported `[OWNER]`

The owner stated `[OWNER-VERBATIM]` “I really, truly hate fallbacks, especially to accomodate
something not explicitly supported in KerML / SysMLv2 and the parse”, completing the referent in
the next message as `[OWNER-VERBATIM]` “the parser (SysIDE).” The owner then asked that the derived
ruling be captured: SysIDE's resolved structure is authoritative, and codegen must refuse rather
than search descendants to invent an occurrence after a definition-owned lineage miss. The ruling
is bounded in `[DEF-OWNED-SIDEWAYS-REACH]`, with Reid W named as owner and `_resolve_leaf` plus its
retained tests and guidance named as the implementation vehicle. That filing satisfies SC3; the
implementation was still unbuilt at rev 7; rev 8 records its landing.

### 2026-08-16 — rev 6: review findings incorporated `[AGENT]`

The qualified-reference requirement is split by owner class. Usage-owned rows point to the landed
exact-owner conformance test; definition-owned and D-5/D-7 rows carry their unchanged-route
evidence; F-2 through F-5 were rerun against `0f89673`. The owner quote's scope-limiting bookends
are restored, the stale baseline is corrected, and the arrayed aggregation split is assigned to the
owner-directed `[ANCHORING-ARRAYED-DIAGNOSTIC]` follow-up rather than expanded into this guidance.
No owner decision was invented: ADR-010 remains an open owner call.

### 2026-08-16 — rev 5: the anchoring repair is landed; stale rows amended `[OWNER 2026-08-16 directed the accuracy pass]`

The `qualified-reference-occurrence-anchoring` repair landed at `98970c9` and was audited Certify on
2026-08-15; a 2026-08-16 independent re-audit verified the repair and its runtime behavior sound
while reopening two certification-evidence criteria (SC12, SC1), so that item is in evidence repair
ahead of its close. This spec's `[HARD]` qualified-reference row still described the positional
defect as current behavior; it now records the repaired state, the supersession of the spike's
pre-repair u4–u7/arrayed measurements, the arrayed-owner `SI_OCCURRENCE_AMBIGUOUS` refusal, and the
arrayed `::`-vs-`.` aggregation split the guidance must account for. The Related Artifacts rows for
the stocktake (complete since 2026-08-15) and the design (rev 2 exists, predates the repair) were
corrected from their "to be created" placeholders. No requirement was added or removed; D-5 remains
the ratified migration form.

### 2026-08-15 — qualified-reference semantics corrected; separate repair named `[OWNER 2026-08-15]`

The F-6 attribution report and semantic corpus scan proved that the positional behavior previously
described in this spec is a codegen defect, not the meaning of a usage qualifier. The owner selected
the broader exact-owner invariant for the separate repair and directed this spec to be corrected.
The D-5 local rename, D-7 cross-part path advice, and fusion-tea migration choice are unchanged.
Implementation and regression ownership lives in
`.project/completed/20260816_qualified-reference-occurrence-anchoring/spec.md`.

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
  (sideways reach), F-5 (chain source paths). **Superseded in part (2026-08-16):** the
  usage-qualified rows (u4–u7 and the arrayed-owner row) were measured on the pre-repair resolver;
  the landed anchoring repair changed their outcomes. Post-repair authority is
  `tests/conformance/test_usage_owned_reference_anchoring.py` and the anchoring item's audit.
- **Post-repair spike recheck:**
  `.project/active/self-binding-replacement/verification/post-repair-spike-recheck.md` — F-2 through
  F-5 reproduced at codegen `0f89673`; separates usage-owned exact-owner behavior from the surviving
  definition-owned positional route. Rev 7 retains that as current-state evidence while the owner-
  ruled removal is carried by `[DEF-OWNED-SIDEWAYS-REACH]`.
- **Prior evidence:** `.project/active/source-identity-binding-semantics-spike/authoring-form-table.md`
  — the 2026-08-05 probe table of six authored forms and their observed referents.
- **Spec review (rev 3, archived):**
  `.project/active/self-binding-replacement/spec-review-20260815-rev3.md` — final Revise verdict;
  all recorded resolutions incorporated in rev 3. The current rev-5 findings and rev-6 dispositions
  are in `spec-review.md`.
- **Product lens:** `.project/active/self-binding-replacement/product-lens.md` — append-only gate
  ledger; rev 3 explicitly resolves `spec-F1` through `spec-F6`, and the rev-6 spec plus rev-3
  design blocks both record `Gate: CLEAR`.
- **Separate qualified-reference repair:**
  `.project/completed/20260816_qualified-reference-occurrence-anchoring/spec.md` — owned F-6 implementation,
  promoted u4–u7 coverage, shared-caller regressions, and the broader exact-owner invariant selected
  by the owner. **Repair landed** (`98970c9`) and verified sound by the 2026-08-16 independent
  re-audit; two certification-evidence criteria (SC12 identity capture, SC1 deep-override lane) were
  reopened by that re-audit, so the item is back in evidence repair ahead of its close.
- **Qualified-reference evidence:**
  `.project/research/20260815-140630_qualified-binding-corpus-scan.md` — exact owner/edge census and
  snapshot/baseline disposition.
- **Stocktake (complete):** `.project/research/20260815-103905_item8-bounded-stocktake.md` —
  validated the two scope calls this spec depends on; Item-8 scope holds, and the retracted
  form-count was purged from its last live site.
- **Design:** `.project/active/self-binding-replacement/design.md` — rev 3, revised against the
  landed exact-owner repair and the current reviews. Design review: `design-review.md`.

---

**Next Steps:** Rev 6 is ready to serve as the design contract. ADR-010 remains an explicit owner
call and is not assumed by the design.
