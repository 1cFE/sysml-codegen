# Design Review: Subtype-Aware Enumeration & Constraint-Report Truth

**Design:** `.project/active/subtype-enumeration/design.md`
**Spec:** `.project/active/subtype-enumeration/spec.md`
**Review File:** `.project/active/subtype-enumeration/design-review.md`
**Date:** 2026-07-06
**Posture:** Adversarial. Assume the design is wrong until the code says otherwise.

---

## Fundamental Assessment

**Sound — proceed to detailed review.**

The design solves the actual problem and does not invent an adjacent, more interesting one. The
core concept is right and stated plainly: one blindness (exact-type enumeration) and one silence
(the report reads the live model, so it can't run offline), both fixed at their real choke points.
The two load-bearing mechanisms — one adapter parameter for the sweep, and a collect/render split
for offline parity — are the minimum machinery the spec's success criteria demand. Neither is
over-engineered. Each new abstraction earns its place:

- `include_subtypes` on the adapter is one additive parameter at the single documented choke point,
  exactly what the spec's `[HARD]` "one parameter, not fifteen patches" requires.
- The collect/render split is not gold-plating — it is the only way to make the live and
  from-snapshot reports identical without maintaining two report implementations, which is the
  precise anti-pattern Item 3's parity work exists to catch.

So the foundation holds. But the design has **one critical gap that makes the mechanism silently
wrong as written** (the TYPE_MAP finding the orchestrator flagged — confirmed below), plus several
must-address items where a claim is overstated or a verified code hazard is left unmentioned. The
verdict is **APPROVED-WITH-CHANGES**, not approval — the critical gap would ship a report that
over-counts requirements as dropped constraints and passes its own tests while doing so.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec requirement maps to a design element: the decision table's 8 rows, the format bump, the
serialization carrier, the re-anchor, the sentinel, the docs. The satisfy-excluded resolution
(spec review L1-1 → resolution (a)) is carried correctly into B2, the kind-ladder, and INV-C. Good.

Two compliance gaps:

- **The mutation check is not executable as the design words it** (see Dimension 5 / MF5). The spec
  `[HARD]` (spec:152–158) requires a mutation check that fails when the query is broken. The design
  says "run `collect_constraint_manifest` with `include_subtypes=False`" — but collect is described
  as hardcoding `include_subtypes=True`. As written, the test cannot pass that flag. This is a spec
  requirement the design cannot yet satisfy.
- **The part-usage-owner leg is deferred to "confirm at implement, else add a fixture"** (design:220–223).
  The spec makes the part-usage leg `[HARD]`. Deferring the fixture *discovery* to implement is a
  legal design/implement boundary, but the design should state the fallback concretely as owned work
  (it does, in Potential Risks) so it can't quietly fall out of scope.

### 2. Pattern Consistency
**Assessment:** Pass

The design follows existing idioms rather than inventing new ones: the V-diagnostic pattern for the
sentinel, the versioned-snapshot pattern for the format bump, a pure render function mirroring other
license-free offline paths. D5 consciously diverges from Item 10's additive-optional `reference_chain`
approach and states why (a v1 snapshot silently reporting "no constraints" would reintroduce the
blind-vs-empty ambiguity this item kills). That is a real, argued decision, not an inconsistency.

One positive the design *under*-claims: `capture_snapshot` already calls `build_pipeline_context`
(`snapshot/capture.py:42`) and serializes the boundary from that `ctx`. So the manifest produced in
`build_pipeline_context` step 2.5 rides on the same `ctx` the live generate path builds — capture
does **not** need a separate collect call. The "manifest written separately" seam the review posture
worried about does not exist. The design should say this explicitly (see MF4); right now "capture —
thread the manifest through" is vague enough to invite the wrong wiring.

### 3. Abstraction Quality
**Assessment:** Concerns

The abstractions are mostly right-sized (see Fundamental Assessment). The concern is the `exclude`
adapter capability (D1). It exists to serve agentic-mbse rows 6/7, which want only the droppable set.
But codegen row 1 — the repo that *owns* the report — cannot use `exclude`, because INV-C needs the
full swept subtree with excluded entries tagged. So the design ships **two mechanisms for one
semantic**: `exclude=("RequirementUsage",)` in one repo, sweep-and-`is_instance`-partition in the
other. D1's headline is "one predicate, defined once," but that is true only of the `is_instance`
*mechanism*; the requirement-side *policy* (the string `"RequirementUsage"`) is written at three-plus
call sites across two repos. That is the drift surface D1 claims to have removed. See MF3 for the
resolution — this is fixable without heavy machinery, but the "defined once" framing is currently
overstated.

### 4. Duplication Avoidance
**Assessment:** Concerns

Same root as Dimension 3. The `render_constraint_report` sharing genuinely removes the live/offline
report duplication — that half is clean. The residual duplication is the requirement-side type-name
policy across the repo boundary (MF3) and the display-string coupling in the serialized `owner_kind`
(MF6). Neither is structural, but both will drift silently if not single-sourced and pinned.

### 5. Data Structure Clarity
**Assessment:** Concerns

`ConstraintManifestEntry` is a frozen dataclass with explicit fields, and `ConstraintKind` is a
closed enum — good, R1-conformant. Two clarity gaps that both bite the snapshot round-trip:

- **`owner_kind` is a display string, not a token.** `_constraint_owner_kind` returns human-readable
  text (`"calc def"`, `"part usage"`, and the fallbacks `"element"` / `"model"`, per
  `extractor.py`). Serializing that text into the manifest couples the snapshot format to display
  wording — reword the diagnostic and every constraint-bearing snapshot's byte-diff changes, and the
  re-capture gate ("version field + manifest only") gets noisier. Serialize a stable token; let
  render map token → display (MF6).
- **`ConstraintKind` serialization form is unspecified.** Name vs value matters for round-trip
  fidelity and for the byte-identical parity test (MF4). Pin it.

### 6. Route Safety
**Assessment:** Fail (as written — this is the critical finding)

The kind-ladder's fallthrough default is unsafe *because* of the TYPE_MAP gap. The ladder is
`assert → satisfy → requirement → plain`, with `plain` (droppable) as the fallthrough. Every rung is
an `is_instance(x, "<TypeName>")` call. The adapter resolves those names through a whitelist TYPE_MAP
via `type_map.get(type_name)` (`syside_adapter.py:244–246`, orchestrator-verified), and that map
contains **neither `AssertConstraintUsage` nor `RequirementUsage` nor `SatisfyRequirementUsage`**
(register §D4 L129: "TYPE_MAP … contains zero subtype names"). An unmapped name makes `is_instance`
return `False` silently. Consequences, all silent:

- The exclusion `is_instance(x, "RequirementUsage")` never fires → swept `RequirementUsage` elements
  fall through to `PLAIN` → **requirements are reported as dropped constraints**, the exact
  over-report the spec's exclusion exists to prevent.
- Every rung fails to match → **all constraints classify as `PLAIN`** → the sentinel's
  assert/require/requirement/satisfy breakdown is uniformly wrong.
- Tests may still pass, because wi014_toy has no `RequirementUsage` to mis-classify — so the bug
  ships green and surfaces only on a model that carries a requirement.

The fallthrough-to-droppable default converts a lookup miss into a plausible-looking wrong answer.
That is the worst failure shape for a truth item. This is MF1 and it gates the mechanism.

Separately, the `level6_architecture.py:601` `except Exception: constraints = []` swallow
(orchestrator-verified) is an unsafe route at a site row 7 edits: even after the `include_subtypes`
fix, any exception collapses to "zero constraints," reintroducing the blind-vs-empty ambiguity. The
design never mentions it (MF2).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets (B1–B4) are genuine reality-claims with "if false" consequences, and the decisions
(D1–D5) each name a rejected alternative. That structure is honest.

**The most expensive bet is hidden.** B1 states "`is_instance` is hierarchy-aware." True — but the
load-bearing belief the whole mechanism rests on is narrower and unstated: *the specific type names
the filter and ladder resolve on (`RequirementUsage`, `SatisfyRequirementUsage`,
`AssertConstraintUsage`) are present in the adapter's TYPE_MAP.* That is false today (Dimension 6),
and it is exactly the bet whose silent failure is most expensive. Surface it as a first-class bet and
close it in the design (MF1), not at implement.

Two smaller integrity notes:

- D1's rejected alternative ("three call-site `is_instance` filters — drift risk") is undercut by the
  chosen design, which still spreads the `"RequirementUsage"` policy across sites (MF3). The decision
  is fine; its rationale needs the honest caveat that policy single-sourcing is still required.
- The design's "parity by construction" is a decision-grade claim that is half true. Render identity
  is by construction; the serialize→deserialize→render round-trip is a matched pair that can drift
  (MF4). Calling the whole thing "by construction" hides a real, testable risk behind a label.

### 8. Reader Comprehension
**Assessment:** Pass

A tired engineer can read the Core Concept once and get the model: one blindness, one silence, and
the two fixes. The R4 verification table is clear about what was confirmed by source-read vs deferred
to a live probe. No section hides complexity behind an undefined coined term.

One phrase to fix, not for style but because it misleads on substance: "parity by construction"
(Core Concept, D3, Integration Strategy). It tells the reader the round-trip is safe by structure
when the round-trip is actually the one part guarded only by a test. Precision here is comprehension,
not polish (MF4).

---

## Issues by Severity

### Critical
- **MF1 — TYPE_MAP gap makes the mechanism silently wrong.** The filter/ladder type names are absent
  from the adapter whitelist; `is_instance` no-ops on unmapped names → requirements over-reported as
  dropped, kinds collapse to PLAIN, tests ship green. Design must specify the added names and the
  adapter's unknown-name behavior. [Dim 6, 7]

### Major
- **MF2 — `level6 except Exception: constraints = []` swallow, at a site row 7 edits, is unaddressed.**
  Fix it in the row-7 change or record it explicitly as a D3-family deferral to Item 5/9. Do not drop
  it silently. [Dim 6]
- **MF3 — One semantic, two mechanisms; requirement-side policy duplicated across repos.** `exclude`
  vs sweep-and-partition, with `"RequirementUsage"` written at 3+ sites. Single-source the policy per
  repo and pin cross-repo equality; justify keeping both mechanisms (INV-C legitimately forces
  codegen's full sweep) instead of claiming "defined once." [Dim 3, 4]
- **MF4 — "Parity by construction" overclaims; capture wiring under-specified.** State that capture
  reuses `build_pipeline_context` (so collect is single-path), and reframe: render = by construction,
  round-trip fidelity = by test (INV-B). Pin `ConstraintKind`/`owner_kind` serialized form; make the
  INV-B test compare from-snapshot output against the *live* output of the same model. [Dim 2, 5, 7]
- **MF5 — REQ-EXT-09 mutation check not executable as designed.** "Run collect with
  `include_subtypes=False`" needs a signature that accepts the flag, but collect hardcodes `True`.
  Resolve the signature, or retarget the mutation to the production call path. [Dim 1, 5]

### Minor
- **MF6 — `owner_kind` serialized as a display string** couples snapshot bytes to diagnostic wording;
  serialize a stable token, map to display in render. [Dim 5]
- **M7 — "all 20 snapshots" is a pre-Item-1 count.** Item 1 adds fixtures re-captured at v2. Say "all
  committed snapshots including Item-1 additions," not a frozen 20 (confirmed: 20 today).
- **M8 — Loader error message points at `sysml-codegen snapshot --models`** while the mandated
  re-capture tooling is `scripts/capture_extraction_snapshots.py --fixtures`. Align the message or
  note the discrepancy so the implementer isn't sent to the wrong command.
- **M9 — Manifest list ordering unstated.** For byte-identical parity, state that serialized order =
  swept order and render preserves it (no re-sort).

---

## Recommendations

1. **Close MF1 in the design before implement.** Name the exact TYPE_MAP additions
   (`AssertConstraintUsage`, `RequirementUsage`, `SatisfyRequirementUsage`; check whether row 5 needs
   `MembershipImport`/`NamespaceImport`) in both repos, and specify that the adapter **hard-errors on
   an unknown type name in both `elements_of_type` and `is_instance`** — `elements_of_type` already
   raises (probe error lists the valid names); `is_instance` currently returns `False` silently, which
   is itself a D3-family silent failure. Add a pin: `is_instance` on an unmapped name raises. This one
   change turns the whole mechanism from silently-wrong to loud-if-wrong, which is the epic's stance.
2. **Address MF2 explicitly** — the swallow is at a site you're already editing; fixing it is nearly
   free and prevents the row-7 fix from being masked. If you defer, record it in Non-Goals and the
   register so Item 5/9 inherits it.
3. **Reframe the parity claim and single-source the policy** (MF3, MF4) — small edits that make two
   overstated claims honest and remove two real drift surfaces.
4. **Resolve the mutation-check signature** (MF5) so the spec's `[HARD]` re-anchor is buildable as
   written; prefer a mutation that exercises the production call, not one the test parametrizes.

---

## Resolutions

Incorporated 2026-07-06 (orchestrator rulings). Keyed by ID. All landed in `design.md`.

- **MF1 (critical) — FIXED.** New decision **D6**: adapter `TYPE_MAP` gains the exact syside classes
  `AssertConstraintUsage`, `RequirementUsage`, `SatisfyRequirementUsage`; **both** `elements_of_type`
  and `is_instance` **hard-error (ValueError + valid-names list) on an unknown type name**. The
  `is_instance` hard error is gated on "name not in TYPE_MAP" **before** the documented mock
  string-match fallback, so the mock path survives. A fires-on-unknown-name unit pin lands in the
  companion. The hidden bet is surfaced as first-class **B2** (names must resolve) and closed by D6 —
  silent-wrong becomes loud-if-wrong. Core Concept, INV-F, Validation, and the R4 table (row 5 note)
  updated.
- **MF2 (major) — FIXED.** New decision **D7**: the `level6_architecture.py:601 except Exception:
  constraints = []` swallow is fixed in this item (narrow/remove; fail loud), since it sits at the
  line row 7 edits. Recorded as absorbing one D3-family site early, **noted for Item 5's ledger**;
  Non-Goals updated to carve out this one site; a level6 error-injection test row added; R4 row 5
  now names the swallow.
- **MF3 (major) — FIXED.** **D1** rewritten: policy single-sourced in the adapter as
  `EXCLUDED_CONSTRAINT_TYPES = ("RequirementUsage",)` + `is_droppable_constraint`, imported by both
  repos → `"RequirementUsage"` lives in exactly one production location. The two *mechanisms*
  (`exclude` param vs codegen's sweep-and-partition, forced by INV-C) are kept and justified honestly;
  the "defined once" claim now applies to the *policy*, pinned by a cross-repo consistency test
  (INV-D). Abstraction/Duplication concerns retired.
- **MF4 (major) — FIXED.** Parity reframed everywhere ("parity by construction" removed): **render
  identity = by construction; round-trip fidelity = by the INV-B test.** D3 states collect is
  single-path (capture.py:42 reuses `build_pipeline_context`). INV-B now compares from-snapshot output
  against **live** output for the same model and pins a **golden serialized manifest fragment**.
  `ConstraintKind`/`OwnerKind` serialized form pinned (D8).
- **MF5 (major) — FIXED.** `collect_constraint_manifest(*, include_subtypes=True,
  excluded_types=EXCLUDED_CONSTRAINT_TYPES)` — the policy is an **injectable parameter defaulting to
  production**, so the mutation check runs it with `include_subtypes=False` and watches the assert-pin
  fail. This also serves MF3's single-sourcing. REQ-EXT-09 re-anchor bullet (d) updated.
- **MF6 (minor) — FIXED.** **D8**: `owner_kind`/`constraint_kind` serialize as stable enum tokens
  (`OwnerKind`: CALC_DEF/PART_DEF/PART_USAGE/ELEMENT/MODEL); render maps token → display wording. A
  reword never changes snapshot bytes.
- **M7 (minor) — FIXED.** "all committed snapshots including Item-1's additions" replaces the frozen
  "20" (20 today, stated as such) in D5 and the re-capture note.
- **M8 (minor) — FIXED.** Loader error message aligned to the real recapture tooling
  `scripts/capture_extraction_snapshots.py` (not `sysml-codegen snapshot --models`).
- **M9 (minor) — FIXED.** New **INV-G**: `collect_constraint_manifest` stable-sorts by
  `(owner_qualified_name, constraint_name)`; serialize and render preserve that order — deterministic
  parity bytes regardless of swept order (adopts the orchestrator's stable-sort recommendation over
  raw swept order).

---

**Overall:** APPROVED-WITH-CHANGES (address MF1 before implement; MF2–MF5 before the affected
edits; MF6/M7–M9 are cleanups).

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. MF1 in particular must land in the design — it
changes what the implementer writes at the adapter and at every `is_instance` call in the ladder. The
reviewer does not edit the design.

ARTIFACT: .project/active/subtype-enumeration/design-review.md
