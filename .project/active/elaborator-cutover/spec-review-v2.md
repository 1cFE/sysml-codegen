# Spec Rereview: Atomic Cutover — Switch, Delete, Snapshot, Recapture

**Spec:** `.project/active/elaborator-cutover/spec.md`
**Prior Review:** `.project/active/elaborator-cutover/spec-review.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/elaborator-cutover/spec-review-v2.md`
**Date:** 2026-08-10

---

## Reality Check

**Concerns, but not a Stage-0 failure.** The revised spec is still about the right work item, and
the previous P0/P1 findings were corrected in substance rather than answered with headings alone.
The route matrix, owner-gated accepted batch, API/deletion censuses, envelope tamper cases,
measurable customer proof, two-repository gates, and Item-7/Item-8 boundary are now usable contract
language. One new contradiction inside R9 makes the required Fusion Tea migration impossible as
written, so the spec is not yet safe to hand to design.

Item 6's certified dirty state was treated as the prerequisite of record. This rereview did not
reopen its certification and did not modify code or `spec.md`.

---

## Prior P0/P1 Finding Recheck

| Prior finding | Rereview status | Basis |
|---|---|---|
| **L1-1 — provenance collapse** | **Corrected in substance; minor residue remains.** | Owner outcomes are now `[NEED]`, agent-authored ratified strategy is `[INFERRED]`, and inherited contract behavior cites its source. Two mixed-grade success criteria still need a mechanical split; see **L1-1** below. |
| **L1-2 — F19 scope and C25/C2 loss** | **Topology and in-place scope corrected; new contradiction introduced.** | R9 pins the one maintained fixture, all 15 current sites, the D-5 form, exact C25/C2 declarations, occurrences, consumers, and mutations (`spec.md:234-256`). Its final preservation sentence conflicts with the required form; see **L2-1**. |
| **L1-3 — invented diagnostic snapshot** | **Corrected.** | R7 now derives behavior from each contract outcome. `AUTHORING_DIAGNOSTIC` refuses capture, `LOAD_ERROR` ends at load, and a diagnostic-bearing graph cannot become a persisted or public snapshot (`spec.md:194-217`; governing matrix at `constraint-execution-authoritative-lifecycle-contract.md:760-768`). |
| **L2-1 — accepted-recapture atomicity** | **Corrected.** | R13 defines a replaceable candidate, excludes exploratory/rejected candidates from corpus authority, requires explicit owner accept/revise disposition, and gates completion, final landing, and merge (`spec.md:298-312`). The remaining manifest issue does not weaken the owner gate; see **L3-1**. |
| **L2-2 — Item-7/Item-8 boundary** | **Corrected.** | Item 7 may edit the maintained codegen fixture and create temporary generated packages. Item 8 retains committed packages, studies, certification repair, guidance, and architecture documentation; TEAx remains evidence-only unless the spec is amended (`spec.md:267-279,314-322`). |
| **L3-1 — open public API disposition** | **Corrected.** | R3 requires a closed row for live, capture, load, CLI, return/container, exception, constructor, import, and re-export surfaces, with final signatures and acceptance tests before design approval (`spec.md:126-159`). |
| **L3-2 — open deletion/test replacement** | **Corrected.** | R4 names the legacy responsibilities and all four Item-6 transitional duals. R6 requires a mechanically populated, closed production/export/caller/script/test census and a one-to-one independent replacement for each deleted behavioral oracle (`spec.md:160-233`). |
| **L3-3 — envelope tamper coverage** | **Corrected.** | R2 classifies load-bearing fields, binds or proves them non-authoritative, and names outer-field, source-skew, profile/schema-skew, graph-replacement, inner-fingerprint, re-fingerprinted-inner/tampered-outer, and canonicalization cases (`spec.md:97-125`). |
| **L3-4 — unmeasurable scale and TEAx evidence** | **Corrected.** | R10 pins the model, environment record, repeated-run thresholds, size/count stability, and pass/fail limits. R11 pins the seal oracles, public registry and execution APIs, real TEAx state, temporary outputs, and the independently derived `270.1211779380445` LCOE oracle (`spec.md:257-279`). The value reproduces from the recorded Fusion Tea equations and defaults. |
| **L3-5 — ambiguous repository gates** | **Corrected.** | R12 names `sysml-codegen` and `../agentic-mbse`, preserves fresh exact counts, distinguishes clean production Ruff from zero-new full-tree baselines, pins mypy limits and license evidence, and treats TEAx as unchanged evidence (`spec.md:280-297`). |

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Rewrite request [MINOR — objectively verifiable]:** The broad provenance correction is
real, but two success criteria still combine different source grades.

- The `[NEED]` mission criterion adds `FORMULA` and alias consumers (`spec.md:38-42`). The cited
  owner mission names calculation, constraint, and aggregation consumers
  (`epic_elaborate_first_architecture.md:78-80`). FORMULA/alias coverage is supported by the
  certified Item-6 contract, but it is not part of that owner-originated wording. Keep the owner
  outcome `[NEED]` and carry the additional certified surface separately as `[INHERITED]` or
  `[INFERRED]`.
- The `[INHERITED]` C19 criterion combines the inherited C19 runtime outcome with deletion of the
  supplied-value tripwire and mechanism test (`spec.md:64-68`). That deletion belongs to the
  agent-authored cutover strategy. Split the criterion by grade, or grade the combined criterion
  `[INFERRED]` while retaining both citations.

These are provenance repairs, not scope decisions. The obligations already have recorded support,
so a focused grade-and-citation check is sufficient after amendment.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim [P1 — material contract contradiction]:** R9 simultaneously requires the
Fusion Tea bindings to become bare-renamed and forbids the calculation change needed to make that
form exist. The recorded D-5 control is `in r_in = R`: the formal identifier and source feature
identifier must differ (`source-identity-binding-semantics-spike/authoring-form-table.md`, form 1c).
All 15 current Fusion Tea sites are same-named `in x = x` bindings: ten in
`tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml:114-168`, three in
`tests/fixtures/fusion_tea/designs/hif_ife/hif_plant.sysml:186,215-216`, and two in
`tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml:73-75`. R9 also fixes the source
attribute declarations and intended referents (`spec.md:234-249`). Therefore at least the
calculation formal identifiers, and the expressions that use them, must be renamed. The sentence
that the fixture's “calculations … do not change” (`spec.md:251-254`) leaves no legal migration.

The correction must say exactly what is preserved and what may change:

- Preserve the physical source attributes, defaults, semantic referents, numerical equations, and
  model physics.
- Permit the calculation formal-identifier renames required by D-5, with no semantic arithmetic
  change.
- Put the resulting generated module/schema/input-name and test consequences into the closed R3/R6
  census. Item 7 may exercise those names in temporary packages; committed downstream package and
  study migration remains Item 8.

This is not a request to choose another migration form. Bare-renamed-in-place is the recorded
agent recommendation ratified by the owner. The spec must make that chosen migration executable.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request [MINOR — objectively verifiable]:** R13 makes the 37-path manifest total
only over R7 outcomes, but the corpus and the 29-cell matrix are not one-to-one. In particular,
`agg_literal_probe` is one of the 37 inherited paths and its classified exact outcome is the
non-source-identity `CodeGenerationError` for having no calculation definition
(`diff-ledger.md:15-18`). It is not a `RUNTIME_SOURCE`, `AUTHORING_DIAGNOSTIC`,
`AMBIGUITY_DIAGNOSTIC`, `POLICY_DIAGNOSTIC`, or `LOAD_ERROR` cell. As written, “exactly the
inherited 37 paths with one contract-appropriate outcome per R7” (`spec.md:298-302`) cannot reach
zero unclassified paths.

Make the manifest record the actual public outcome for every inherited path. Apply R7's outcome
semantics to every matrix-derived result, preserve already classified non-R7 control outcomes from
the Item-5 ledger, and keep all relevant cell obligations when one fixture covers several cells.
This is a manifest-schema correction only. The owner acceptance gate and one-committed-batch rule
remain sound.

### Lens 4 — Hygiene

No material hygiene-only finding.

### Lens 5 — Reader Comprehension

No separate voice finding. Correcting L2-1 will make the intended preservation boundary clear:
formal names may move to express the approved D-5 referent, while equations and physics do not.

---

## Engagement Summary

**Overall take:** The revised spec genuinely repairs the prior review's P0/P1 defects. It now has a
strong atomic-cutover contract, but R9 overconstrains the approved Fusion Tea migration so no
implementation can satisfy it. That is material contract risk and requires **Revise**. The two
other findings are mechanical and objectively verifiable; they do not reopen architecture or owner
decisions.

**Required revisions, in priority order:**

1. **[L2-1]** Allow the formal-identifier renames that make all 15 bindings bare-renamed, while
   preserving source attributes, defaults, equations, referents, and physics. Census the generated
   API/test consequences and keep committed downstream artifacts in Item 8.
2. **[L1-1]** Split the two mixed-grade success criteria so owner-originated outcomes remain
   `[NEED]` and agent/inherited additions retain their actual grades.
3. **[L3-1]** Make the 37-path manifest total over both R7-governed outcomes and classified non-R7
   controls such as `agg_literal_probe`.

---

## Resolutions

None recorded. This was a fresh non-interactive rereview.

---

**Verdict:** Revise

**Next Steps:** Return this review to the spec agent. Correct L2-1, apply the two mechanical
repairs, and run a focused rereview of those three findings before technical design. Do not reopen
the already-corrected envelope, census, scale/TEAx, repository-gate, atomicity, or Item-7/Item-8
decisions unless the amendments change them.
