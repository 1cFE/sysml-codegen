# Design Review: Lowering Outcome Integrity — Warning Order and Excluded Identity

**Design:** `.project/active/gap-lowering-integrity/design.md`
**Spec:** `.project/active/gap-lowering-integrity/spec.md`
**Review File:** `.project/active/gap-lowering-integrity/design-review.md`
**Date:** 2026-07-18

---

## Fundamental Assessment

**Concerns.** The core approach is sound. A read-only warning pre-pass before the existing BLOCK
raise is the smallest change that preserves halt atomicity, and branching the excluded mint on the
source name can preserve the current named-ID inputs exactly. The existing lowering order supports
both choices (`src/sysml_codegen/analysis/constraint_lowering.py:752-815`). No new catalog model or
lowering phase is justified.

The design is not ready to implement because its canonicalization boundary contradicts its own
scope. D4 and the component overview say snapshot capture rewrites every anonymous usage location
(`design.md:124-129`, `:200-206`), while I8 says eligible-anonymous minting and IDs remain unchanged
(`design.md:195-196`, `:210-213`). Current eligible minting consumes the same location-derived
component (`constraint_lowering.py:456-465`, `:818`, `:917-921`). Rewriting by missing name alone
therefore changes eligible-anonymous IDs or creates live/snapshot drift. The design must select
anonymous *excluded* usages at the canonicalization boundary and show how that selection reaches
snapshot serialization without duplicating or weakening profile/owner classification.

**Stage 0 verdict:** Revise, not Rework. The warning and ID-mint approach should remain. The
anonymous canonicalization data flow needs correction before planning.

**Post-revision verdict (2026-07-18): Approved.** The revised design keeps the warning and mint
approach, replaces missing-name-wide rewriting with one authoritative excluded-index selector,
separates live-raw mapping from snapshot-canonical validation, and installs explicit named and
eligible-anonymous byte firewalls. Detailed dispositions are recorded under Resolutions.

---

## Dimensional Review

### 1. Spec Compliance

**Post-revision assessment:** Pass

- **Eligible-anonymous scope is not preserved.** The design promises anonymous-only *excluded*
  minting in D2, but D4 broadens the location rewrite to every missing-name usage. That violates the
  explicit non-goal of leaving eligible-anonymous IDs and grouping unchanged (`spec.md:119-127`;
  `design.md:108-129`, `:195-217`). Narrow both live and snapshot canonicalization to anonymous
  exclusions, then add a test whose eligible anonymous fact retains its exact pre-change ID and raw
  location behavior.
- **The three RED/GREEN exclusion nodes are not explicitly live-shaped.** The overlay promises one
  node per kind, and the kept matrix promises constructed anonymous facts (`design.md:257-275`,
  `:285-294`), but neither says that each kind's RED and GREEN facts pin `name=None`,
  `qualified_name=None`, and a non-null file/line/column `LocationFact`. Those fields are populated
  independently by extraction (`../agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py:191-198`,
  `:225-231`). Make that shape an assertion in every kind-specific overlay node. State which
  line/column/file cases pass through live SysIDE, or explain why a live shape-lock plus synthetic
  matrix is sufficient.
- **Warning behavior is almost complete, but the regression list should pin the non-blocking side.**
  The mixed test's exact warning list proves source order and exactly once before the synchronous
  raise. Add an explicit exact-count assertion for a non-blocking NON_NUMERICAL batch so retaining
  the old loop emission cannot double-warn after the pre-pass (`design.md:101-107`, `:221-222`,
  `:279-284`; current single-warning guard at
  `tests/conformance/test_constraint_non_numerical.py:25-38`).
- **Capture fidelity is mostly honest.** The design retains the owner-specified revisions, profile
  version, three exclusion kinds, and exact named-ID pins. There is no owner-tagged `[REFERENT]` or
  `[EXAMPLE]` in the approved spec to carry. However, anonymous-only minting is explicitly
  `[INFERRED]` and challengeable (`spec.md:103-109`). The design acknowledges that at D2, then its
  handoff says to treat all D1-D8 as fixed (`design.md:108-112`, `:311-317`). Reword the handoff so
  the ratchet does not silently promote this agent-grade scope choice to owner-settled authority.

### 2. Pattern Consistency

**Post-revision assessment:** Pass

- The pre-pass reuses the existing facts/profile zip and logger, and the excluded branch reuses
  `_source_local_identity` and `mint_constraint_id`. Those choices fit the codebase.
- The source helper is appropriately small, but current facts carry an untagged string path. A
  helper that treats a value matching `root-<n>/...` as already canonical at every call site creates
  an implicit routing convention not present elsewhere (`design.md:113-129`, `:198-206`). Use
  explicit live-raw and snapshot-canonical entry points, or an explicit mode at the caller. Live
  mode must always prove root containment; replay mode may validate the canonical grammar.

### 3. Abstraction Quality

**Post-revision assessment:** Pass

- One pure source-referent helper earns its place because live lowering and snapshot capture need
  the same encoding. No new class or protocol is needed.
- The helper currently combines two responsibilities without a reliable discriminator: mapping a
  raw parser path against roots and validating an already-canonical referent. A raw relative path
  that resembles the canonical grammar could bypass I7's no-matching-root failure. Split those
  operations or require an explicit mode. Also specify how the caller identifies excluded usages
  before rewriting; “missing name” is insufficient.

### 4. Duplication Avoidance

**Post-revision assessment:** Pass

- Sharing the referent encoder avoids live/serializer drift.
- Narrowing serialization to excluded usages may tempt implementation to reimplement the
  `owner-kind OR non-ADMIT` selector outside lowering. The revised design must name one source of
  that selection and show how capture receives it. Do not create a second exclusion classifier
  beside `_exclusion_for` and the profile result (`constraint_lowering.py:479-491`, `:752-815`).

### 5. Data Structure Clarity

**Post-revision assessment:** Pass

- `root-<input-index>/<relative-posix-path>` is understandable and distinguishes same-relative-path
  files in different roots. File, line, and column remain explicit inputs to anonymous identity.
- The raw and canonical values share the same untagged `LocationFact.file: str` field. The design
  needs an unambiguous canonical grammar or explicit processing mode, including escaping and
  validation rules for path segments. Otherwise idempotence and root containment cannot both be
  trusted.
- Collision resistance remains an unstated scale assumption. `mint_constraint_id` truncates
  SHA-256 to 64 bits (`constraint_lowering.py:292-303`), and the design only adds fields to the
  hashed tuple (`design.md:108-123`, `:182-191`). The genuine-duplicate guard is good, but it does
  not make a legal anonymous model collision-free. Quantify why 64 bits is acceptable for the
  maximum catalog size, or widen only anonymous IDs while preserving every named byte. Keep the
  forced-duplicate test either way.

### 6. Route Safety

**Post-revision assessment:** Pass

- Live and snapshot routes are explicit, but the proposed automatic “already canonical” branch can
  send a live raw path down the replay route. That can bypass root containment and absolute-root
  rejection (`design.md:124-129`, `:192-206`). Route selection must come from the caller, not from
  pattern-matching an untrusted path string.
- The route parity matrix is otherwise strong: repeated live, relocated live, capture/replay, two
  roots with the same relative filename, and exact serialized-output comparisons are all named
  (`design.md:285-294`). Preserve those cases after fixing route selection.

### 7. Bets & Decisions Integrity

**Post-revision assessment:** Pass

- B1-B3 are genuine bets and each states what fails. B1's ordered-root premise is reflected in the
  non-goal that differently ordered invocations need not share identity (`design.md:85-97`,
  `:210-216`).
- **Hidden bet:** 64-bit anonymous digests are sufficient at all supported catalog scales. The epic
  objective says legal models mint collision-free identities, while the retained mint is
  probabilistic and the duplicate guard only fails loud after a collision. State and justify the
  scale bound or change the anonymous encoding.
- D1 and D2 name rejected alternatives and are well justified. D4 is not yet a valid decision
  because its “anonymous” rewrite is broader than the excluded-only problem and because it does not
  explain how the serializer obtains the exclusion selection.
- D7's isolation controls are strong but incomplete. Exact HEAD values do not prove detached
  worktrees are unmodified. Record clean baseline status/tree state, hash the candidate production
  diff, and assert the candidate worktree differs from the baseline by exactly that diff
  (`design.md:257-275`). This matters in the current coordinated repositories, where both HEADs are
  pinned but the working trees can carry unrelated uncommitted state.

### 8. Reader Comprehension

**Post-revision assessment:** Pass

The overview, core concept, diagram, decisions, invariants, and validation matrix give a usable
mental model. The source identity is explained before its grammar, and the design surfaces the D5
message-content premise conflict rather than silently claiming closure (`design.md:66-83`). The
problems above are contract/data-flow defects, not prose defects.

---

## Issues by Severity

### Critical

- **Anonymous snapshot rewriting expands eligible scope.** Rewriting all missing-name locations
  changes the location component used by eligible-anonymous minting, contradicting I8 and the spec's
  non-goal. Narrow canonicalization to anonymous excluded usages and define one authoritative
  selection/data flow. — Spec Compliance, Route Safety

### Major

- **Raw and canonical path modes are ambiguous.** Pattern-based idempotence can let a live raw path
  bypass root containment. Make route mode explicit and validate each mode independently. — Pattern
  Consistency, Abstraction Quality, Route Safety
- **The three exclusion-kind RED/GREEN nodes do not pin live extraction shape.** Require missing
  name, missing QN, and non-null location in every node, plus an explicit live coverage boundary. —
  Spec Compliance
- **64-bit collision resistance is assumed, not justified.** Quantify the supported scale or widen
  only anonymous IDs without changing named IDs; retain the truthful forced-duplicate guard. — Data
  Structure Clarity, Bets & Decisions Integrity
- **Pinned evidence can still contain uncommitted contamination.** Assert clean baseline worktrees
  and record/verify the exact candidate production diff in addition to HEADs, import paths, and the
  overlay hash. — Bets & Decisions Integrity

### Minor

- **The validation matrix should state the non-blocking exactly-once assertion explicitly.** This
  guards against leaving the old loop emission in place after adding the pre-pass. — Spec Compliance
- **The handoff overstates the authority of D2.** Preserve the design's own statement that the
  anonymous-only `[INFERRED]` choice remains challengeable rather than calling every decision fixed.
  — Spec Compliance, Bets & Decisions Integrity

---

## Recommendations

1. Redraw D4's data flow around an explicit set of anonymous excluded usages. Show how the same
   selection drives live lowering and snapshot-copy canonicalization without touching eligible
   anonymous facts or duplicating classification.
2. Split raw-path mapping from canonical-referent validation. Require live callers to supply roots
   and prove containment; allow only snapshot replay to accept the canonical grammar.
3. Make each F5 overlay node shape-lock the verified live fields and explain how the unchanged
   overlay passes the new root input on GREEN while remaining runnable at the old signature on RED.
4. Choose and justify the anonymous collision budget. Preserve the post-sort uniqueness halt and
   diagnostic that describes both records without asserting a cause.
5. Strengthen evidence isolation with clean-tree assertions and an exact candidate-diff hash, then
   keep the fixture manifest, named-ID pins, and migration guard unchanged.
6. Add explicit exact-count assertions for both halting and non-blocking warning batches.

---

## Resolutions

- **Critical — eligible-anonymous scope: Resolved.** D2 defines one shared excluded-usage-index
  selector from facts plus the profile result. D6 canonicalizes a serialized location only when the
  index is selected and the name is missing. D3 keeps named exclusions on the exact old mint call
  and keeps eligible anonymous location, tuple, suffix, ID, and grouping unchanged. I3-I5 and the
  before/after gates make both byte firewalls testable. No serializer-side classifier is introduced.
- **Major — route ambiguity: Resolved.** D4 provides separate live mapping and snapshot validation
  entry points selected explicitly by pipeline-builder/capture versus graph-rebuild callers. D5
  defines lexical normalization from the actual SysIDE `LocationFact.file` shape, exact root
  containment, segment encoding, and canonical validation. A path string cannot select its route.
- **Major — live-shaped RED/GREEN facts: Resolved.** D9 and the evidence section require every kind
  node to assert `name=None`, `qualified_name=None`, and an exact non-null file/line/column location.
  Signature inspection lets the same overlay call the old baseline signature and pass explicit
  live mode/roots only on the candidate. Licensed temporary models lock all three live extraction
  shapes; the synthetic matrix covers the full kind-by-file/line/column product.
- **Major — collision resistance: Resolved.** D7 widens only anonymous excluded suffixes to 128 bits,
  quantifies the birthday bound at one million records, and preserves the 16-hex default for every
  named and eligible call. D8 and I9 retain an unconditional forced-duplicate halt with truthful
  two-record diagnostics and no causal blame.
- **Major — evidence contamination: Resolved.** The overlay stays outside detached worktrees. The
  protocol requires exact clean baseline statuses/tree hashes for both repositories, exact HEADs,
  worktree-contained imports for codegen and companion modules, worktree-first path order, overlay
  hash, candidate binary-patch hash, exact changed-path set, no candidate untracked files, and a
  regenerated-diff hash match.
- **Minor — exactly-once warnings: Resolved.** I1 and the overlay require the blocking event sequence
  `[warning-1, warning-2, raised]` and a separate non-blocking exact list
  `[warning-1, warning-2]`, preventing both suppression and double emission.
- **Minor — decision authority: Resolved.** The handoff identifies anonymous-only D3 as
  `[INFERRED]`, challengeable, and ratified only by design approval. It is not relabeled as
  owner-originated or silently promoted to settled authority.
- **Fixture and migration scope: Resolved.** D10 uses temporary live model trees. Fixture hashes,
  direct named IDs, the eligible-anonymous pin, and the existing loud migration guard must remain
  unchanged; fixture recapture is prohibited.

---

**Overall:** Approved after revision

**Next Steps:** Proceed to `my-plan`. Planning must preserve the explicit named/eligible byte
firewalls, capture isolated RED before production edits, and retain all fixture and migration gates.
