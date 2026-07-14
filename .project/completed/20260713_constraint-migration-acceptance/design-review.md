# Design Review: Migration, Docs, and IFE Acceptance (Item 14)

**Design:** `.project/active/constraint-migration-acceptance/design.md`
**Spec:** `.project/active/constraint-migration-acceptance/spec.md`
**Review File:** `.project/active/constraint-migration-acceptance/design-review.md`
**Date:** 2026-07-13
**Reviewer posture:** skeptical; every claim checked against code, not the design's word.

---

## Fundamental Assessment

**Sound.** The approach is right and not over-engineered. This item removes a rival surface
(the drop manifest) proven redundant against the already-load-bearing catalog, fixes one
named extraction gap, flips docs, and accepts through the study layer. No new subsystem, no
speculative abstraction. The five workstreams map cleanly onto the spec's four workstreams
plus the three seams. The design is honest and it surfaced its central premise conflict
instead of resolving it silently.

It is **not** a rework. But three must-fixes are corrections that change what the owner
ratifies and where the mapping test reads its data. Two of them touch the epic's single most
load-bearing outcome (the migration invariant and the no-silent-drop guarantee), so they are
must-fix, not nice-to-have.

The headline: the design's D1 premise conflict is **misdiagnosed**. It reads the concept as
unsatisfiable and asks the owner to ratify an *amendment*. The concept is satisfiable exactly
as written; what actually diverged is Item 7's landed *code*, which repurposed the term
"source record." The test the design lands on is correct — only the narrative and the owner's
question are wrong. That distinction matters because this is the epic's closing record.

---

## What I verified against code

- **`ConstraintCatalogSourceRecord` is per-definition.** Two fields only —
  `definition_qualified_name`, `formal_names` (`resolution/models.py:325-335`). Assembled one
  per entry in `facts.definitions` (`generation/constraint_catalog.py:77-83`). It carries no
  usage identity, no membership kind, no polarity, no source location. The design's claim
  that source records "cannot carry an inline constraint or distinguish N instances of one
  usage" is **correct about the code**.
- **The concept's "source record" is per-usage.** Concept line 102: "a **source record** per
  asserted or applied constraint *usage* (source identity and form, membership kind, polarity,
  scope, source location, display expression, referenced-definition metadata when one exists)."
  That is the per-usage carrier — a *different structure* from the code's
  `ConstraintCatalogSourceRecord`. The per-usage level exists in the landed code only as the
  shared `usage_qualified_name` grouping key across concrete entries, not as its own record.
- **`concrete_entries` is eligible-only.** `assemble_constraint_catalog` filters
  `eligible = [c for c in concrete if c.eligible]` (`constraint_catalog.py:76`) and builds
  entries from `eligible` alone (`:85`). **Unassessed (`eligible=False`) records are not in
  the catalog.** They live in `ctx.concrete_constraints` (`pipeline_context.py:119`), produced
  at `constraint_lowering.py:517`.
- **Gain miss diagnosis is right.** A bare `in gain = gain` routes to `qn =
  f"{instance_scope}__gain"` (`supplied_values.py:96`). An instance self-redef owned by
  `instance_scope` misses tier 1 (`_match_override` matches owner
  `f"{instance_scope}__gain"`, `:129`), tier 2a (needs a `usage_type_map` key, `:172`), and
  tier 2b (needs owner == consuming part def, `:189`). All three miss. Confirmed.
- **Loader tolerates `dropped_constraints` absence.** `raw.get("dropped_constraints", [])`
  (`loader.py:239`).
- **The three-key gate does not include `dropped_constraints`.** The Item 8 load-bearing gate
  covers `constraint_facts`, `part_occurrences`, `constraint_lowering_mode` only
  (`loader.py:159-167`). D3's removal does not touch it. **D3 is safe.**
- **Both blanket warnings and the retirement targets exist as cited** — the per-predicate INFO
  (`constraint_report.py:125`) and summary WARN (`:135`), the replay
  (`snapshot_context.py:44-45`), the serializer emit (`serializer.py:133`).
- **The docs block list matches** the concept (line 188): invocation, conditional, temporal,
  unit conversion, real equality → two-inequality band.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec success criterion has a design element. But two spec-derived guarantees are put at
risk by imprecise surfaces (see Must-Fix 2 and Must-Fix 3):

- The spec's **no-silent-drop** guarantee (INV-A; success criterion "a source with no
  concrete instance is inventory, never silent") is asserted against "the catalog," but the
  catalog cannot answer the unassessed arm of the query (eligible-only). The test must read
  unassessed carriers from `ctx.concrete_constraints`.
- The spec inherits the concept invariant verbatim. The design's "vocabulary-coverage arm"
  asserts the opposite of a concept invariant (unused definitions are legitimate inventory).

Capture-fidelity: the design surfaced the premise conflict (good — Law 4) but with an
inverted diagnosis (Must-Fix 1). It treats the concept's `[INHERITED]` invariant as
unsatisfiable when the concept's own text (line 102) makes it satisfiable.

### 2. Pattern Consistency
**Assessment:** Pass

The gain fix adds one precedence tier in the existing demand-scoped, literal-only style of
`supplied_values.py`. The mapping test re-anchors the existing REQ-EXT-09 conformance family.
The acceptance re-points an existing harness through the already-certified study layer. D3
reuses the `.get()` tolerance already in the loader. No new patterns invented.

### 3. Abstraction Quality
**Assessment:** Pass

No new abstractions. The design explicitly removes a rival rather than adding a mechanism.

### 4. Duplication Avoidance
**Assessment:** Pass

The whole point is de-duplication: two surfaces describing the same usages collapse to one.

### 5. Data Structure Clarity
**Assessment:** Concerns

The three-granularity model (manifest per-usage; source records per-definition; concrete
entries per-instance) is real and correctly identified. But the design conflates the concept's
per-usage "source record" with the code's per-definition `ConstraintCatalogSourceRecord`
(Must-Fix 1), and it names "the catalog" as the carrier surface for unassessed records, which
the catalog does not hold (Must-Fix 2). The data flow is traceable once those two surfaces are
pinned; as written they are ambiguous at exactly the join the whole item rests on.

### 6. Route Safety
**Assessment:** Pass

D3 correctly stays within v3; the loader's `.get()` and the three-key gate both verified. The
kept generation-halt (`constraint_lowering.py:481`) is preserved as an explicit non-goal. The
boundary-row rule (INV-E) is stated as a decision, not a wildcard.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1–B4 are genuine bets with honest "if false" clauses. B1 (same population) is strongly
evidenced (both sweep `elements_of_type("ConstraintUsage", ...)`). One **hidden bet** worth
stating: B1 covers *population* but the migration also rests on *every manifest entry having a
lowering carrier regardless of its manifest disposition* — an ADMIT usage → eligible entries,
a not-ADMIT usage → an unassessed record, a requirement-side excluded usage → unassessed or
"legitimately carrier-free." The "legitimately carrier-free" category is a silent-drop
loophole if its membership is a catch-all rather than a tightly-justified set (e.g.,
`requirement_def` owners the lowering explicitly skips). Name the justified category; do not
let it absorb surprises.

D3 and D4/D5 name their rejected alternatives with reasons — good. D1's rejected alternatives
are stated, but D1's *premise* is the misdiagnosis (Must-Fix 1).

### 8. Reader Comprehension
**Assessment:** Concerns

The Core Concept section is well-written and gives a reader the model. But its load-bearing
sentence — "The spec and concept say 'source record,' but source records are per-definition
and cannot carry an inline constraint" — is the misdiagnosis itself, stated as settled fact. A
reader (or the owner) takes away "the concept was wrong." That is the one sentence that most
needs to be exactly right, and it is inverted. Fix the sentence and the surfaced-conflict box
with it.

---

## Must-Fix

**MF1 — The D1 premise conflict is misdiagnosed; the invariant is met as written, not amended.**
*Why:* This is the epic's closing item and the migration invariant is `[INHERITED]` from the
owner-ratified concept. The design frames the conflict as "the concept says 'source record'
but source records are per-definition, so the invariant is unsatisfiable — I'm reinterpreting
to per-usage carrier," and flags it for the owner to *confirm the amendment*. That is
inverted. Concept line 102 **explicitly defines** "source record" as per asserted/applied
constraint *usage*. The invariant (`manifest-usage → one source record → ≥1 concrete entry`)
is satisfiable and correct as authored. What actually diverged is **Item 7's landed code**,
which named a *per-definition* structure `ConstraintCatalogSourceRecord` — narrower than the
concept's per-usage source record (`models.py:325`, assembled from `facts.definitions` at
`constraint_catalog.py:77`). The concept's per-usage "source record" was **not landed as a
distinct structure**; it survives only as the `usage_qualified_name` grouping of concrete
entries. So the design's join (manifest-usage → per-usage carrier) *is* the concept's
invariant, faithfully realized — not an amendment to it.
*Fix:* Rewrite the surfaced-conflict box and the Core Concept sentence so the owner adjudicates
the real question: **"Item 7's landed catalog uses the term 'source record' for a per-definition
structure, narrower than the concept's per-usage 'source record' (concept line 102). The 1:1
test bridges the manifest to the concept's per-usage carrier (the catalog's concrete entries
grouped by `usage_qualified_name`, plus unassessed records). The invariant is met as written;
no amendment is needed."** The test mechanics are unchanged. Only the narrative and the owner's
question change — but recording the epic's closing invariant as "met" vs "amended" is exactly
what the owner must sign off correctly.

**MF2 — The unassessed carrier is not in the catalog; name the real surface.**
*Why:* The design's Core Concept says "sweep the catalog" and maps each manifest usage to "an
eligible concrete entry (≥1) or an explicit unassessed record," implying both live in the
catalog. They do not. `assemble_constraint_catalog` filters to `eligible` only
(`constraint_catalog.py:76`); **unassessed records are excluded from the catalog** and live in
`ctx.concrete_constraints` with `eligible=False` (`pipeline_context.py:119`,
`constraint_lowering.py:517`). As written, the test's unassessed arm has no data source — and
the unassessed arm is precisely what proves INV-A (no silent drop) for not-ADMIT usages. An
implement session following the design literally would either fail to locate unassessed
carriers or discover mid-build that the eligible-only catalog cannot answer the query.
*Fix:* Pin the two surfaces explicitly in the Implementation Notes: eligible carriers from
`graph.constraint_catalog.concrete_entries` (grouped by `usage_qualified_name`); unassessed
carriers from `ctx.concrete_constraints` where `eligible=False`; manifest from
`collect_constraint_manifest()`. (Equivalently, join the manifest against the full
`lower_constraints` output, which carries both dispositions in one list — arguably the cleaner
home, and it reconciles the spec's "anchor onto the catalog" wording with the fact that the
catalog is eligible-only.)

**MF3 — The "vocabulary-coverage arm" contradicts the concept's inventory rule.**
*Why:* D1 adds an arm that "asserts every `source_record` (definition) is referenced by ≥1
usage." Concept line 102: "An unused `ConstraintDefinition` is authoring inventory, not
execution coverage — it never appears as unassessed." Unused definitions are **legitimate**.
`assemble_constraint_catalog` puts **all** `facts.definitions` into `source_records` regardless
of use (`constraint_catalog.py:77-83`), so an unused inventory definition *will* appear as a
source record — and this arm, as a kept test, would fail on it. The arm enforces the opposite
of a concept invariant.
*Fix:* Drop the arm, or invert it to the safe coverage direction — "every concrete entry's
definition appears in `source_records`" (no dangling reference) — which is a real integrity
check and does not forbid inventory. If a "definitions are reachable" check is wanted, it must
allow unused definitions as inventory.

---

## Nice-to-haves

- **NTH1 — Retirement list is incomplete.** Appendix B / the Architecture retire-list omits
  `pipeline_context.py:110` (the `constraint_manifest` dataclass field) and
  `snapshot_context.py:86` (threading `constraint_manifest` through). INV-B's grep-clean gate
  catches leftover *emissions*, not a vestigial field. List them so the retirement is clean.
- **NTH2 — W5b (teax loader seal wiring) is a precondition for W4, not parallel to it.** The
  Architecture diagram shows workstream 5 as a parallel lane with no arrow into W4. But the
  spec (lines 222-223) says the acceptance run *loads a sealed IFE package through teax*, so
  W5b enables W4. Add the W5b→W4 dependency so acceptance is not discovered blocked late. (This
  compounds R3: W4 already depends on Items 10-12 *and* on W5b.)
- **NTH3 — After D3 the snapshot corpus is intentionally heterogeneous.** Once the serializer
  stops emitting `dropped_constraints`, the two re-captured fixtures lose the key while the
  other 27 keep it (not re-captured). Harmless (loader `.get()`), but state it: the INV-C
  timestamp-gate reviewer should expect `plant_values` and `fusion_tea` to change for **two**
  reasons (gain fix *and* key removal), and a later snapshot auditor should not be surprised by
  27 snapshots carrying a now-dead key.
- **NTH4 — Boundary detection on exact float equality is fragile.** `eta*G == 10.0` (Impl
  Notes / B3) can miss a grid point intended at 10.0 that computes as 9.999… A note on grid
  exactness or a tolerance band would harden the boundary-row detection.
- **NTH5 — D2 does not say which capture bucket holds the instance self-redef.** The new tier
  matches `owning_part_qn == instance_scope`, but `_match_override` scans `design_overrides`
  while tier 2b scans `redefinitions`. Say which bucket `hif_plant.sysml:87`'s `:>> gain = 80.0`
  lands in so the tier scans the right list. (Implement confirms empirically, but the design
  should state the expectation.)

---

## Issues by Severity

### Critical
- (none — the approach is sound)

### Major
- MF1 — D1 premise conflict misdiagnosed; invariant met as written, not amended (Spec / Reader
  Comprehension / capture-fidelity Law 4).
- MF2 — Unassessed carrier surface is not the catalog; the no-silent-drop arm has no stated
  data source (Data Structure / Spec).
- MF3 — Vocabulary-coverage arm contradicts the concept's inventory rule (Spec / Bets).

### Minor
- NTH1 retirement-list completeness; NTH2 W5b→W4 ordering; NTH3 heterogeneous corpus note;
  NTH4 boundary float equality; NTH5 D2 capture bucket.

---

## Recommendations

1. Rewrite D1's surfaced-conflict box and Core Concept sentence to state the truth: the concept
   invariant is met as written; Item 7's *code* repurposed "source record" to per-definition.
   The owner confirms "no amendment," not "approve the amendment." (MF1)
2. Pin the mapping test's data surfaces — eligible from the catalog, unassessed from
   `ctx.concrete_constraints` (or join against the full `lower_constraints` output). (MF2)
3. Drop or invert the vocabulary-coverage arm so unused-inventory definitions stay legitimate.
   (MF3)
4. Close the small gaps: retirement-list completeness, the W5b→W4 arrow, the corpus-heterogeneity
   note, boundary float care, and the D2 capture bucket. (NTH1-5)

---

## Resolutions

_(Filled in during Stage 4, when the owner engages. One entry per resolved issue — this is what
the design agent reads to incorporate the review. The reviewer does not edit the design.)_

---

**Overall:** Approved-with-must-fixes.

The foundation is right and verifies against the code: remove the rival surface, fix one named
extraction gap, flip the docs, accept through the study layer. The three must-fixes are
corrections, not a rework — but two of them (MF1, MF2) sit on the epic's most load-bearing
outcomes (the migration invariant and the no-silent-drop guarantee), so they must land before
implement. MF1 in particular decides whether the epic closes with its migration invariant
recorded as *met* or as *amended*; the code evidence says **met as written**.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design.
