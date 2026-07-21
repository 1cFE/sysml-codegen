# Spec Review: Lowering Outcome Integrity — Warning Order and Excluded Identity

**Spec:** `.project/active/gap-lowering-integrity/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/gap-lowering-integrity/spec-review.md`
**Date:** 2026-07-18

---

## Reality Check

**Concerns.** The spec is about the right work item and preserves the important boundary: warnings
become observable before a halt, but a halting run still returns no pipeline context, catalog, or
package. Current code confirms both defects exactly: the blocking preflight raises before the
warning loop, and excluded lowering computes then discards the anonymous location component
(`src/sysml_codegen/analysis/constraint_lowering.py:752`, `:779`, `:791`). The spec is sound enough
for a full audit, but its identity and evidence criteria need revision before design can safely use
it as the contract.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The live/snapshot success criterion weakens the requested identity outcome
to “make the same decisions from the same facts.” Decisions do not include the minted
`constraint_id`, and named live/snapshot parity cannot exercise the anonymous branch. The inherited
I5 contract is stronger: identical warnings and exclusions, which include the excluded record ID
and location. The success criteria must explicitly require byte-identical anonymous IDs, warning
values, exclusion locations, and excluded records across repeated live lowering and snapshot
lowering. Otherwise design could satisfy the current words while producing route-dependent IDs
(`spec.md`, “Success Criteria,” item 8; `numerical-constraint-profile/design.md`, I5;
`tests/conformance/test_constraint_non_numerical.py:50`).

**L1-2 · Direct claim:** The spec promises that named IDs stay byte-stable, but its proof is limited
to “existing named fixtures and their generated artifacts.” Current coverage does not pin a named
ID for every exclusion kind: `unsupported_owner` is an offline record test with no ID assertion,
while the migration corpus primarily exercises named `unassessed_form` records
(`tests/conformance/test_constraint_lowering.py:144`; `tests/conformance/test_constraint_migration_mapping.py:102`).
Because the requested change is anonymous-only across all three exclusion kinds, the success
criteria need direct before/after named-ID pins for `non_numerical`, `unassessed_form`, and
`unsupported_owner`, not only a corpus byte comparison.

**L1-3 · Direct claim:** The `[HARD]` tag on “anonymous assessed statement without a source location
remains a generation error” is justified only by the current helper. Existing code is not itself a
non-negotiable interface, and `LocationFact` remains optional in the upstream schema
(`src/sysml_codegen/analysis/constraint_lowering.py:456`;
`../agentic-mbse/src/agentic_mbse/sysml/constraint_facts.py:134`;
`numerical-constraint-profile/design.md`, D10). Retag this as `[INFERRED]` unless an actual
interface constraint is cited. The outcome can remain scoped out without overstating its
authority.

### Lens 2 — Problem & Approach

No material finding. The spec frames F4 as reporting-before-halt rather than partial generation,
limits F5 to excluded records, and keeps the eligible-anonymous compile-key limitation separately
booked. That is the correct decomposition relative to the research and verification records.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** The exact anonymous source identity is deferred without an outcome-level
portability constraint. `LocationFact.file` comes directly from SysIDE, constraint-fact snapshot
serialization preserves it verbatim, and the committed snapshot demonstrates an absolute,
checkout-specific path (`../agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py:225`;
`src/sysml_codegen/snapshot/serializer.py:98`;
`tests/fixtures/constraint_non_numerical/extraction_snapshot.json:47`). If design hashes that raw
string, the same model in two checkout roots receives different IDs, and a relocated snapshot can
retain the capture machine's identity. Keep the tuple mechanism deferred, but require a canonical
source referent whose ID is deterministic across repeated extraction, live/snapshot replay, and
checkout relocation. Include a two-file same-line/same-column case so file identity is proved
rather than accidentally reduced to line and column.

**L3-2 · Direct claim:** The RED-evidence criterion pins only sysml-codegen revision
`6db321225a5c8568db0287b67ed1d04c03079cc2`. F4/F5 disposition depends on the companion's v3
profile, and the verification record establishes the paired pre-fix baseline as agentic-mbse
`4ed2a0728ea49298666415cd389d9a6173a81a3e`. Evidence produced against an unspecified companion
revision is not reproducible and may fail for the wrong reason. Pin both revisions and record that
the profile version is `executable-profile/v3` (`20260718_gap-review-verification.md`, opening
baseline and F4/F5 rows; `src/sysml_codegen/analysis/constraint_lowering.py:747`).

**L3-3 · Rewrite request:** The anonymous-pair criteria say “distinct source locations,” but do not
state which identity dimensions must distinguish records. The current extraction sort key already
recognizes that the same line in different files and multiple columns on one line are legal
(`../agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py:234`). Ask the spec agent to make
the test matrix explicit at the outcome level: distinct line, distinct column, and distinct file
must remain distinct for each of the three exclusion kinds. The design should still choose the ID
tuple and encoding.

**L3-4 · Direct claim:** The duplicate-diagnostic criterion correctly demands that genuine
collisions still halt, but no success criterion requires an adversarial genuine-collision test
after anonymous minting is fixed. The existing test only checks that a duplicate raises and matches
the ID; it does not protect the new requirement to identify both records by available source and
owner data (`tests/unit/test_concrete_constraint_model.py:91`). Add a kept test that injects a true
duplicate ID, proves the halt remains, and pins the two record descriptions without asserting the
old “broken model” or hash-collision diagnosis.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The final Next Steps line says to run `my-spec-review` after approval,
even though that is the current stage. Correct the handoff so approval proceeds to design. Leaving
the current line risks repeating the review stage instead of advancing the pipeline
(`spec.md`, final line; `/home/reid/.agents/skills/my-spec/SKILL.md`, Stage 4).

### Lens 5 — Reader Comprehension

No separate material finding. The main comprehension risk is the under-specified phrase “same
facts” in the parity criterion, covered by L1-1 and L3-1.

---

## Engagement Summary

**Overall take:** The spec has the right problem, scope, and warning-before-halt contract. It should
not become the design contract yet because it does not require portable anonymous identity, does
not directly prove named-ID stability across all three exclusion kinds, and leaves the RED baseline
under-pinned.

**Here's what I need you to weigh in on:**

1. **[L1-1, L3-1, L3-3]** Require exact anonymous ID and exclusion parity across live, snapshot,
   repeated, and relocated-checkout runs, with location cases that cover file, line, and column.
2. **[L1-2]** Add direct named-ID byte-stability evidence for all three exclusion kinds so the
   anonymous-only boundary is actually enforced.
3. **[L3-2]** Pin agentic-mbse `4ed2a0728ea49298666415cd389d9a6173a81a3e` beside codegen
   `6db321225a5c8568db0287b67ed1d04c03079cc2` in every saved RED record.
4. **[L3-4]** Keep a true duplicate-ID regression so correcting the misleading message cannot
   weaken collision detection.
5. **[L1-3, L4-1]** Correct the unsupported `[HARD]` provenance tag and the stale pipeline handoff.

---

## Resolutions

- **[L1-1] Resolved.** The revised parity criterion now covers the observable outputs, not only the
  profile decision: constraint IDs, applicable warning values, canonical exclusion locations, and
  serialized excluded records must be byte-identical across repeated live lowering and snapshot
  replay.
- **[L1-2] Resolved.** The revised spec requires a direct exact-ID before/after pin for one named
  record in each exclusion kind: `non_numerical`, `unassessed_form`, and `unsupported_owner`.
  Fixture-wide or corpus-wide byte comparison alone is explicitly insufficient.
- **[L1-3] Resolved.** The missing-location requirement is retagged from `[HARD]` to `[INFERRED]`.
  Its text now distinguishes the current boundary and agent-grade scope choice from the upstream
  schema, which permits a missing location.
- **[L3-1] Resolved.** The revised contract defines observable anonymous identity as canonical
  source referent plus line and column. The referent must distinguish logical files and multiple
  roots without carrying an absolute checkout or capture-machine prefix. It also requires stable
  IDs and excluded output across equivalent model trees relocated to different checkout roots.
- **[L3-2] Resolved.** Every pre-fix RED record now pins sysml-codegen
  `6db321225a5c8568db0287b67ed1d04c03079cc2`, agentic-mbse
  `4ed2a0728ea49298666415cd389d9a6173a81a3e`, and semantic profile v3.
- **[L3-3] Resolved.** The anonymous regression matrix now crosses all three exclusion kinds with
  distinct-line, distinct-column, and distinct-file cases. The same-line/same-column two-file case
  prevents an implementation from dropping file identity.
- **[L3-4] Resolved.** A kept adversarial regression must inject two genuinely different records
  with one duplicate ID, prove uniqueness validation still halts, and pin a truthful diagnostic
  that distinguishes both records without blaming a legal anonymous model.
- **[L4-1] Resolved.** The spec handoff now proceeds directly to `my-design`; it no longer repeats
  the completed review stage.

The revised spec retains the agent-grade anonymous-only minting decision, F4 warning-before-halt
with no package or catalog, all three F5 exclusion kinds, named-byte discipline, and the separate
`[ANON-ELIGIBLE-KEY]` non-goal.

---

## Re-review

Approved. Every must-fix finding is now represented as a testable outcome. Design still owns the
canonical referent and ID encoding, but it cannot use absolute checkout paths, drop file/line/column
identity, change named excluded IDs, under-pin the coordinated RED baseline, or weaken genuine
duplicate detection.

---

**Verdict:** Approve
**Next Steps:** Proceed to `my-design` for
`.project/active/gap-lowering-integrity/design.md`.
