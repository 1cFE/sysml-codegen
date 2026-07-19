# Design Review: Snapshot Portability and Shape Gates

**Design:** `.project/active/constraint-wave-snapshot-portability/design.md`  
**Spec:** `.project/active/constraint-wave-snapshot-portability/spec.md`  
**Review File:** `.project/active/constraint-wave-snapshot-portability/design-review.md`  
**Date:** 2026-07-18

---

## Fundamental Assessment

**Concerns.** The overall approach is right. The design extends the existing excluded-usage
projection instead of creating a new path codec, keeps named and anonymous ID minting separate,
puts v3 shape checks immediately before the two strict reconstructors, and leaves legacy loader
compatibility and Item 3 occurrence/demand semantics alone. This is the smallest credible design
for the revised spec.

The design is not ready for planning. Its lowering flow maps or validates the same
`NON_NUMERICAL` location once for warning rendering and again for record construction. That
violates the required once-per-route boundary and preserves two failure points in one lowering run.
The design also rests on a false compatibility premise about unknown extra keys, and its fixture
updater is not safe enough to enforce the exact two-file byte contract before mutation.

The historical spec review's four findings are otherwise reflected in the revised spec and design:
the comparison is an excluded-facts projection rather than whole-facts parity, the gate stops at the
three v3 constraint sections, field presence/nullability/default policy is explicit, and the
relocation outputs are enumerated (`spec-review.md:28-94`; `spec.md:93-207`;
`design.md:176-216`).

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Fail

- **DR-1 — Lowering canonicalizes or validates a non-numerical location twice.** The current warning
  pre-pass consumes the location before the excluded-record loop
  (`src/sysml_codegen/analysis/constraint_lowering.py:861-867,889-930`). The design says the new
  helper remains shared by both consumers (`design.md:156-160`), so a selected `NON_NUMERICAL`
  usage still takes the live mapper or replay validator once for its warning and again for its
  exclusion. This conflicts with the requested once-at-boundary rule and with the design's own
  claim that the location is “one portable projection” (`design.md:14-17,72-80`). It also lets one
  lowering run observe root state twice.
  
  **Recommendation:** Compute a located exclusion's route projection lazily once per lowering run,
  keyed by usage index, and pass the resulting referent/rendered location to both warning and record
  consumers. Do not pre-project `BLOCK` usages: they halt before record construction today, and
  mapping them early would broaden the R-8 warning-pre-pass masking defect. Keep the named mint tuple
  exactly unchanged and let only the anonymous mint consume the cached referent.

- **DR-2 — Unknown-extra-key compatibility is asserted against contrary current behavior.** The
  design says unknown keys remain ignored, matching the companion codec (`design.md:174,189-191,
  236-238`). The current loader recursively scans every mapping and list below `constraint_facts`
  for any `expression-ir/*` schema tag, including data under unknown keys
  (`src/sysml_codegen/snapshot/loader.py:178-189,251-269`). A kind-directed validator that ignores
  extras would therefore accept an extra payload containing `schema_version: expression-ir/v2`
  that current code rejects. The spec repeats the same false “as they are today” premise
  (`spec.md:202-203`). The design silently resolves neither side of this premise conflict.
  
  **Recommendation:** Surface and resolve this contract explicitly before planning. Either retain
  the broad version scan in addition to the new shape gate, or revise the spec to authorize
  kind-directed unknown-key behavior and add a regression that pins the intended result.

- **Required/nullable/optional/degradable policy is otherwise faithful.** The tables match the
  companion codec's direct indexing and `.get` behavior: facts aggregate/item fields are directly
  indexed (`../agentic-mbse/src/agentic_mbse/sysml/constraint_facts.py:205-339`), while only the
  documented literal/feature/unit `operand_type` fields default in ExpressionIR
  (`../agentic-mbse/src/agentic_mbse/sysml/expression_ir.py:190-283`). The design correctly excludes
  degradable `/compilation_results` and legacy `.get(...)` behavior (`design.md:176-191`).

- **Reconstruction error boundaries are correctly scoped.** JSON syntax/root normalization occurs
  before `.get`, section validation precedes reconstruction, and facts/occurrence reconstruction
  gets separate chained `SnapshotFormatError` translation with section pointers and recapture text
  (`design.md:122-134,162-174,231-238,355-364`). The proposed exception set covers the actual direct
  indexing and dataclass reconstruction failures demonstrated by R-11.

- **ID stability is correctly protected.** Named exclusions retain the location-free tuple at
  `constraint_lowering.py:925-930`; anonymous exclusions retain referent/line/column and the 32-hex
  suffix at `:907-918`; the eligible path begins separately at `:952`. The design does not move
  canonical locations into facts decisions or common ID builders (`design.md:103-114,363-367`).

- **Capture fidelity has one metadata/hardening defect.** The design labels the revised draft an
  “Approved contract” (`design.md:21`), but `spec.md:3` remains Draft and the only persisted review
  still says Revise with no resolutions (`spec-review.md:129-137`). It also tells planning to treat
  inferred manifest and fixture details as fixed (`design.md:423-428`). Those items remain
  agent-grade and challengeable even if the design is approved. The owner-given snapshot-v3 and
  GAP-CLOSE referents are otherwise retained with their intended force.
  
  **Recommendation:** Correct the approval/status claim and replace “fixed” with a design-decision
  handoff that preserves agent-grade provenance.

### 2. Pattern Consistency

**Assessment:** Concerns

- Reusing `excluded_usage_indices`, `map_live_source_referent`,
  `validate_snapshot_source_referent`, `SnapshotFormatError`, and the loader-local boundary follows
  existing patterns (`design.md:35-59,103-134`). No new cross-repo abstraction is justified.
- DR-1 is the pattern break: two consumers call a mapper/validator rather than consuming one
  projected value. A small per-run projection cache is consistent with the existing single-selector
  model and avoids moving state into `ConstraintFacts` or `UsageDecision`.
- The exhaustive loader validator necessarily mirrors the pinned companion codec. DR-2 shows why
  that duplication needs an explicit compatibility decision and a version-pin review obligation,
  not only the drift risk note at `design.md:372-376`.

### 3. Abstraction Quality

**Assessment:** Concerns

- The proposed primitives and three explicit validators are a reasonable level of abstraction for
  exact JSON Pointer errors (`design.md:115-121`). JSON Schema, new Pydantic wire models, or a
  companion-repository change would add more machinery than this item needs.
- The location abstraction is incomplete because it exposes an operation rather than the projected
  per-usage result. DR-1 should be fixed without a new public class or global facts rewrite: one
  lowering-local indexed result/cache is enough.
- The validator's authority must stay structural. The independent mutation matrix described at
  `design.md:339-342` is important because sharing production tables with tests would hide omitted
  fields.

### 4. Duplication Avoidance

**Assessment:** Concerns

- Selector/profile logic is correctly reused rather than reimplemented (`design.md:220-225`).
- The shape gate duplicates the companion codec's accessed-field structure, but exact path errors
  make some duplication unavoidable under the single-repository scope. The design limits it to
  structural shape and pins it to v1.
- Calling the location operation from warning and record paths duplicates boundary work. DR-1 must
  consolidate the result, not merely share the function.

### 5. Data Structure Clarity

**Assessment:** Concerns

- The field-policy tables and JSON Pointer rules make nullability and nested list/map shapes
  traceable (`spec.md:139-203`; `design.md:176-191`). Boolean-versus-integer rejection is explicit.
- **DR-3 — The relocation test inputs are not exact enough to execute the manifest.** Output paths
  and pointers are exact and correspond to current code, including
  `contracts/model_contract.json`, the report-aggregator filename, and package hash keys
  (`design.md:193-216`). However, the design never names the model/fixture or construction recipe
  that supplies both named and anonymous excluded controls for the live-A/live-B/replay-A scenario.
  The committed `constraint_non_numerical` model has one named excluded and one named eligible usage,
  but no anonymous exclusion (`tests/fixtures/constraint_non_numerical/model.sysml:9-22`). The
  current anonymous parity coverage is a separate synthetic facts test
  (`tests/conformance/test_constraint_snapshot_identity.py:130-163`). “Relevant licensed live legs
  where available” (`design.md:419-421`) is also weaker than the mandatory two-scenario criterion.
  
  **Recommendation:** Name the exact harness and inputs for each manifest row. State how one test
  includes named excluded, anonymous excluded, and eligible controls; which leg requires a SysIDE
  license; its marker/command; and how unavailable licensed evidence is reported rather than treated
  as a passing portability gate.

### 6. Route Safety

**Assessment:** Concerns

- Live mapping and replay grammar validation are explicit and separate
  (`source_referent.py:32-80`; `design.md:143-160,218-230`). Capture deep-copies facts and performs
  one selected copied-facts projection (`snapshot/serializer.py:139-160`). No string self-selects a
  route.
- DR-1 leaves two route operations in lowering. The revised design must consume one projection in
  warning, exclusion, and anonymous mint paths.
- Named exclusions without locations and anonymous exclusions without identity-bearing locations
  retain distinct behavior (`design.md:103-109,151-154`).

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

- B1-B3 are genuine reality claims with explicit failure consequences (`design.md:88-99`). B1 is
  supported by shared selector use; B2 is supported by the 66-record inventory; B3 is supported by
  the companion codecs and independent shape matrix.
- **Hidden bet:** unknown extras can be ignored without changing accepted v3 data. Current recursive
  version scanning disproves that as a blanket claim. This is DR-2.
- **Hidden bet:** a two-file mechanical correction can be safely written after selector assertions.
  The design does not account for an exception or process interruption after the first file changes.
  This matters because the contract is exactly two coordinated fixture files, not an arbitrary
  recapture.
- Decisions generally name rejected alternatives and why. D6 is not yet executable enough to earn
  its claim that formatting and all non-allowlisted bytes are preserved.

### 8. Reader Comprehension

**Assessment:** Pass

The design gives the mental model before implementation detail, separates location and loader flows,
and makes the boundaries skimmable (`design.md:70-86,141-191`). The remaining problems are contract
and execution gaps, not prose that hides the system.

---

## Issues by Severity

### Critical

- **DR-1 — Once-per-route projection is violated.** Warning and record consumers map or validate the
  same non-numerical location twice. Consolidate one lazy per-usage result without pre-projecting
  BLOCK usages. — Spec Compliance / Route Safety

### Major

- **DR-2 — Unknown-extra compatibility rests on a false premise.** Current recursive ExpressionIR
  version scanning examines unknown-key payloads; the proposed validator says they are ignored.
  Resolve and test the intended behavior. — Spec Compliance / Bets & Decisions Integrity
- **DR-3 — The relocation manifest lacks exact scenario inputs and an evidence rule for the licensed
  live leg.** Output projections are exact, but the named/anonymous/eligible test corpus and commands
  are not. — Data Structure Clarity
- **DR-4 — The two-fixture update is not pre-write or partial-write safe.** The updater should build
  both candidates in memory, prove the exact 65+1 pointer delta and all manifests before any write,
  then replace both files through a documented recoverable/atomic procedure. A generic parse/dump
  must not reorder or reformat the files. — Bets & Decisions Integrity

### Minor

- **DR-5 — Byte preservation inside changed JSON files is asserted, not mechanically specified.** A
  structural pointer diff cannot detect whitespace or key-order churn. Define exact token-level
  replacement or compare each candidate's bytes against original bytes with only the allowlisted
  JSON string spans substituted. — Data Structure Clarity
- **DR-6 — Contract status and provenance wording are inaccurate.** The design calls a Draft/Revise
  spec approved and marks inferred details fixed for planning. Correct the metadata and preserve
  their agent-grade status. — Spec Compliance

No Item 3 overlap was found. Item 3 owns occurrence expansion and demand identity
(`epic_constraint_pr_wave_remediation.md:231-266`). Item 4's occurrence work is limited to validating
the serialized R-11 shape before the unchanged reconstructor, and the file plan explicitly leaves
`part_instance_index.py`, eligible expansion, and demand collection unchanged
(`design.md:256-288,344-353`). Keep implementation edits in `constraint_lowering.py` confined to
location projection and the excluded branch; the eligible occurrence path begins at
`constraint_lowering.py:952`.

---

## Recommendations

1. Replace repeated lowering map/validate calls with one lazy per-usage projection consumed by
   warnings, exclusions, and anonymous minting; preserve current BLOCK ordering and every mint tuple.
2. Resolve the unknown-extra/version-scan premise in the spec and design, then pin it with a focused
   regression.
3. Make the relocation test fully executable by naming its corpus, harness, license marker, commands,
   and required evidence for all named/anonymous/eligible controls.
4. Specify a pre-write, formatting-preserving, partial-write-safe two-fixture updater and byte-level
   allowlist proof.
5. Correct the spec approval/provenance wording before handing the design to planning.

---

## Resolutions

No resolutions recorded in this non-interactive review stage.

---

**Overall:** Revise  
**Next Steps:** Return this review to the design stage. Revise `design.md` without changing code or
fixtures, then re-run `my-design-review`. The reviewer does not edit the design.
