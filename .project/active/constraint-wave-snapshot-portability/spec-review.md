# Spec Review: Snapshot Portability and Shape Gates

**Spec:** `.project/active/constraint-wave-snapshot-portability/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/constraint-wave-snapshot-portability/spec-review.md`
**Date:** 2026-07-18

---

## Reality Check

**Concerns.** The spec is about the right work item and its core location bet is sound: extend the
existing excluded-only selector to named exclusions, keep live and replay routes explicit, and do
not change either named-ID inputs or anonymous-ID identity. The committed-corpus claim is also
correct: an independent profile-selector inventory of all 30 extraction snapshots found exactly 65
named exclusions with locations in `catf_mfe_model`, one in `constraint_non_numerical`, and none
elsewhere. The draft is not ready as the design contract because one relocation criterion is
impossible under its own non-goals, R-11 has expanded into a legacy-loader schema project without a
source-backed boundary, and neither the malformed-field policy nor the relocated-byte projection is
specific enough to audit.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The whole-`constraint_facts` relocation criterion cannot pass while
eligible locations remain unchanged. The spec requires byte-identical “canonical constraint-facts
payloads” across checkout roots (Success Criteria, lines 38–41), but also requires eligible records
to retain their locations and serialized bytes (lines 42–44) and makes eligible-location
canonicalization a Non-Goal (line 139). This is not hypothetical:
`constraint_non_numerical/extraction_snapshot.json` contains the excluded named
`status_annotation` and the eligible named `positive_value`, both with the capture machine’s
absolute path. The specified selector stops at excluded usages (lines 73–76), matching the current
selector seam in `src/sysml_codegen/snapshot/serializer.py:145-159`; therefore the eligible usage
keeps a root-dependent byte and the complete facts payload differs. Rewrite the success criterion
to name an excluded-facts projection, or broaden the work item and its ID/location byte guarantees.
As written, design cannot satisfy both contracts.

The exact two-fixture claim does not produce a finding. I independently evaluated the current
profile and production exclusion selector over every committed extraction snapshot. The result is
exactly the inventory and counts stated at spec lines 122–128.

### Lens 2 — Problem & Approach

**L2-1 · Rewrite request:** Narrow the R-11 contract to the demonstrated v3 constraint boundary, or
establish separate authority and scope for legacy-loader hardening. The Problem correctly identifies
the three load-bearing sections (lines 23–27), and primary R-11 reproduces malformed
`constraint_facts` and `part_occurrences` shapes. The spec then expands acceptance to the JSON root
and every reconstructed top-level section, including `calc_defs`, `calc_usages`, hierarchy,
aggregation, computed attributes, aliases, and compilation results (lines 45–52 and 97–102). Epic
Item 4 repeats that agent-authored expansion, but the primary review does not demonstrate defects
across those legacy sections. The current loader has an extensive compatibility surface of
intentional `.get(...)` defaults and warning-based degradation, for example
`src/sysml_codegen/snapshot/loader.py:272-310` and `:547-625`. Treating every nested access as a
shape-gate target turns this 1–1.5 day remediation into a de facto schema definition for the entire
legacy snapshot. The evidence-backed boundary is: JSON root enough to reach the v3 gate, the three
load-bearing constraint sections, their required nested shapes, and normalization of failures from
their typed reconstructors. Wider legacy validation should be a separately justified item.

The portability approach itself survives this lens. Live mapping and replay validation remain
separate in `src/sysml_codegen/analysis/source_referent.py:32-80`; named IDs remain stable because
their mint tuple omits location (`src/sysml_codegen/analysis/constraint_lowering.py:925-930`); and
anonymous IDs continue to use canonical referent, line, and column (`:898-923`). Expanding the
excluded-location projector does not require route inference or ID churn.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** Define the presence/nullability/default policy for every in-scope shape
before design. “Missing reconstruction-required key” plus “preserve current optional/degradable
fields” (lines 45–52 and 103–116) is circular: the current code is the disputed behavior, and it
mixes required indexing, nullable values, `.get(...)` defaults, and warning-and-degrade behavior.
For example, every canonical constraint-facts field is emitted even when its value is `null`, and
the companion parser directly indexes all aggregate and usage keys
(`../agentic-mbse/src/agentic_mbse/sysml/constraint_facts.py:191-202` and `:264-339`); in contrast,
an absent or empty `compilation_results` block intentionally degrades to `{}`
(`src/sysml_codegen/snapshot/loader.py:272-288`). Require a field-policy table for the in-scope
sections with four distinguishable states: required key, required-but-nullable value, optional with
default, and absent-with-warning degradation. Without that table, two correct implementations will
promote different historical defaults into errors, and the malformed-shape matrix cannot prove the
optional-field guarantee.

**L3-2 · Rewrite request:** Make the relocation projection an exact manifest at spec stage instead
of deferring its meaning to design. The success criterion claims canonical facts, warning values,
excluded records, catalog fingerprints, model-contract semantic fingerprints, and “other semantic
generated artifacts,” then says moving a snapshot preserves “the same projection” (lines 38–41).
The deferred question leaves design to choose that projection and exclude volatile provenance
(lines 151–153). This lets two implementations pass different byte sets and makes the criterion
self-defining. Name the exact compared values or artifact paths, state whether comparison is between
two live captures, repeated replay of one moved snapshot, or both, and list the only permitted
normalizations. At minimum, separate the excluded-facts projection from the complete snapshot,
because the complete snapshot deliberately retains unrelated absolute-path fields and
`captured_at`.

### Lens 4 — Hygiene

No separate hygiene finding. The material problems are contract contradictions and scope, not
formatting or prose polish.

### Lens 5 — Reader Comprehension

No separate comprehension finding. Resolving L1-1 and L3-2 will remove the only phrases that force
the reviewer to guess what bytes are actually promised.

---

## Engagement Summary

**Overall take:** The work item is sound and the exact two-snapshot inventory is independently
confirmed. The location route is also safe and preserves both named and anonymous ID contracts.
The spec needs revision because its whole-facts parity claim is impossible under its eligible-field
non-goal, and its shape/projection boundaries do not yet define one auditable implementation.

**Here's what I need you to weigh in on:**

1. **[L1-1]** Replace whole-`constraint_facts` byte parity with an exact excluded-facts projection,
   unless eligible-location canonicalization is intentionally brought into scope with its byte
   consequences.
2. **[L2-1]** Keep R-11 at the demonstrated v3 constraint boundary. Treat full legacy-section schema
   hardening as separate work unless new source authority explicitly requires it here.
3. **[L3-1]** Add a required/nullable/optional/degradable field-policy table for every in-scope
   malformed-shape gate.
4. **[L3-2]** Specify the exact relocation comparison manifest and the two route scenarios it must
   prove; do not let design define what the success criterion means.

---

## Resolutions

No resolutions recorded in this non-interactive review stage.

---

**Verdict:** Revise
**Next Steps:** Return this review to the spec stage. The spec agent should incorporate the four
findings without editing unrelated code or broadening fixture churn, then re-run `my-spec-review`
before design.
