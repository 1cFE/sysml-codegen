# Spec: Snapshot v3 — Constraint Facts Load-Bearing

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC — Item 8

---

## Problem

Constraint lowering (Item 5) now runs on the **live** pipeline, but only there. The
from-snapshot generation path is a separate code path — `build_full_graph_from_snapshot`
in `snapshot/graph_rebuild.py:144` — and it never lowers anything. It re-derives the output
registry and backtracker offline, then builds the graph, with no constraint phase at all.

Two consequences follow, and both are the problem this item fixes:

1. **Snapshots cannot carry constraint semantics.** The serializer writes only the old
   `dropped_constraints` drop-manifest (`snapshot/serializer.py:108`); the neutral
   `ConstraintFacts` never reach the snapshot. A snapshot-first workflow loses every modeled
   assertion permanently. This is exactly why Item 5 left `build_pipeline_context`'s
   `lower_constraints_enabled` defaulting **False** (`pipeline_builder.py:697`): with it on,
   every constraint-bearing model diverges live-vs-snapshot (22 measured conformance
   divergences, recorded at `pipeline_builder.py:856-863`), because the live graph gains
   constraint structure the offline graph can't reproduce.

2. **The default is stuck off.** Lowering is built, tested, and dead on the shared path. Item 5
   handed this item the job of making facts load-bearing in snapshots, proving live/snapshot
   parity, and **flipping the default** under that parity gate — turning the 22 divergences
   into a parity test's baseline expectation to eliminate.

This item makes the neutral `ConstraintFacts` a load-bearing, versioned snapshot section;
wires lowering into the from-snapshot rebuild path so it re-derives the same extended graph
offline; rejects stale or sectionless snapshots loudly rather than generating an
assertion-free package; and flips the default. It does **not** emit any constraint code —
that is Item 7. The parity it proves is at the ComputationGraph / catalog-identity level; if
Item 7 has not landed when this implements, artifact-level parity is re-proven in Item 7's
wake (see Non-Goals and Open Questions).

Two known traps shape the work:

- **The silence trap.** A model that asserts something must never quietly generate an
  assertion-free package. A current-version snapshot missing the constraint-facts section is a
  corruption, not an empty catalog — it must fail loudly with a re-capture instruction.
- **The re-derivation trap.** Live/snapshot parity is worthless if the offline path only
  *carries* a pre-computed answer. S3 carry-forward (2) warned exactly this: the snapshot leg
  must re-derive IDs from the carried facts through the real lowering path, not reload a frozen
  catalog. That forces a real question — offline lowering needs the part-instance index, which
  today needs a live model (see Open Questions).

## Success Criteria

The first three are the epic's Item-8 acceptance bar. The last two are the two named
responsibilities this item inherits from the run (the default flip and the `gain` handoff),
stated as their own criteria so they can't be folded into the others.

- [ ] **Both rejection cases fire with re-capture messages** (kept tests, mirroring the
      existing strict version hard-gate). An old-version snapshot is rejected by the version
      gate; a current-version (v3) snapshot **missing the constraint-facts section** fails with
      a re-capture instruction — it never loads as an empty catalog.
- [ ] **A constraint-bearing fixture generates byte-identically live and from snapshot** — same
      artifacts, same `constraint_id`s, same catalog ordering — through
      `generate --from-snapshot`. The parity fixture is one that lowers cleanly
      (`wi014_toy` / S4's model, or `constraint_multi_instance`), not one carrying an unrelated
      extraction gap.
- [ ] **Re-captured corpus shows only expected diffs; conformance suite green.** Constraint-free
      fixtures regenerate byte-identically (timestamps excepted). Constraint-bearing fixtures
      that lower cleanly gain constraint structure — a reviewable, expected diff. The two
      grandfathered fixtures (below) stay byte-identical (un-lowered).
- [ ] **The default flips, under the parity gate.** `build_pipeline_context`'s
      `lower_constraints_enabled` defaults **True**; the from-snapshot path lowers from carried
      facts. The 22 previously-measured live/snapshot divergences are eliminated (they become
      the parity test's baseline expectation, now met).
- [ ] **The two `gain`-blocked fixtures are grandfathered honestly.** `plant_values` and
      `fusion_tea` are generated/captured **flag-off** (today's un-lowered behavior, baselines
      byte-identical) behind a loud, named exclusion list, because their `'Viability Threshold'`
      assertion hits the `gain` hierarchy-extraction gap and would halt lowering. The gap is
      handed to Item 14 as a **named prerequisite**, not a silent deferral.

## Known Requirements

### Serialize the neutral facts section — plus the occurrence data offline re-lowering needs

- **[INHERITED: concept "make constraint facts a load-bearing, versioned snapshot section",
  line 354/287; epic Item 8 §1]** Serialize the **neutral `ConstraintFacts`** section into the
  extraction snapshot. `ConstraintFacts` (reference
  `.project/reference/agentic-mbse-landed/constraint_facts.py:171`) is the owner-ratified
  subject of "constraint facts load-bearing" — the section carries `usages`
  (`list[ConstraintUsageFact]`), `definitions`, and `schema_version`. The from-snapshot path
  re-lowers from this section; it does **not** reload a pre-computed catalog (the re-derivation
  trap).
- **[INFERRED]** *(orchestrator decision Q2, 2026-07-12 — agent-grade)* Serialize, alongside the
  facts, the **minimal lowering-relevant fields** the epic's own "+ lowering-relevant fields"
  wording licenses (epic Item 8 §1): the **part-instance occurrence data** that offline
  re-lowering needs, because `build_part_instance_index()` takes a live model the snapshot path
  does not have (`analysis/part_instance_index.py`; consumed by `lower_constraints` via
  `occ_index.occurrences_of`). Whether this is the serialized occurrences, or the index inputs
  from which the index rebuilds offline, is design's first decision (see Open Questions). The
  rejected alternative — carrying only the resolved `ConcreteConstraint` catalog — is *carriage,
  not re-derivation*, the weaker parity S3 carry-forward (2) warned against; recorded here as a
  decision, not an option.
- **[HARD]** The facts section serializes byte-stably and round-trips losslessly. Membership
  kind, polarity, ownership, actuals, defaults, and inheritance facts survive the round-trip
  unchanged (concept Required Invariant, line 140). `ConstraintFacts` and its `ExpressionIR`
  predicates already provide canonical JSON round-trip upstream (Items 1, 2); the snapshot
  serializer must preserve, not re-derive, that canonical form.
- **[HARD]** The serializer needs the raw `ConstraintFacts` at capture time. Today
  `capture_snapshot` (`snapshot/capture.py:42`) runs `build_pipeline_context` and serializes
  its `PipelineContext` fields, but the context exposes `concrete_constraints`
  (lowering *output*), not the raw `ConstraintFacts` (lowering *input*). Capture must reach the
  raw facts — thread them onto `PipelineContext`, or re-extract at capture. Design picks; the
  requirement is that the *neutral* facts, not the concrete catalog, land in the snapshot.

### Pin both schema versions

- **[HARD]** *(per Item 1 design D9 + its amended forward-record; brief)* The snapshot pins
  **both** `constraint-facts/v1` (`CONSTRAINT_FACTS_SCHEMA_VERSION`,
  `constraint_facts.py:39`) and the embedded `expression-ir/v1` predicate sub-document version.
  A facts section whose `schema_version` does not match the pinned value is a version mismatch,
  handled by the rejection semantics below — not silently coerced. These are the coordinated-pair
  versions the epic's cross-repo skew discipline requires consumers to pin.

### Version bump and rejection semantics

- **[HARD]** Bump `SNAPSHOT_FORMAT_VERSION` from 2 to 3 (`snapshot/__init__.py:15`). There is no
  v2/v3 coexistence: the loader hard-gates on the version (`snapshot/loader.py:135-140`), so
  every committed snapshot is re-captured at v3 in the same change (the established discipline
  recorded in `snapshot/__init__.py:12-14`).
- **[INHERITED: concept Required Invariant, line 142; epic Item 8 §2]** Two rejection cases,
  both with a re-capture instruction, mirroring S3's strict boundary:
  1. **Old-version snapshot** (v2 or a missing version): rejected by the **existing** version
     hard-gate (`snapshot/loader.py:127-140`) — the bump alone makes every pre-v3 snapshot fail
     there. No new gate needed; a kept test pins it.
  2. **Current-version (v3) snapshot missing the constraint-facts section**: fails with a
     re-capture instruction. This is a **new** gate and must **not** follow the degrade-with-a-
     warning precedent that `compilation_results` uses (`snapshot/loader.py:184-203`). A missing
     constraint-facts section on a v3 snapshot is a corruption — it **raises**
     `SnapshotFormatError`, never loads as an empty catalog (the silence trap; concept line 66:
     "including the offline path, where a stale snapshot without constraint facts must be
     rejected, not quietly generated without assertions").
- **[INFERRED]** The distinction between "section absent" (raise) and "section present but empty"
  (a model that genuinely asserts nothing — load as an empty catalog, legitimately) must be
  explicit in the format. A constraint-free model has an *empty facts section*, not a *missing*
  one; the loader distinguishes the two. Design pins how the format encodes "present-and-empty"
  vs "absent" (e.g. section always written, even when empty).

### Live/snapshot parity through the from-snapshot rebuild path

- **[HARD]** Lowering wires into `build_full_graph_from_snapshot`
  (`snapshot/graph_rebuild.py:144`) / `build_classifier_inputs_from_snapshot`
  (`:26`), mirroring the live path's three threading points (P1 resolve, P2 inject-roots, P3
  extend — `pipeline_builder.py:849-979`) against the deserialized facts + occurrences. The
  offline registry, `design_attrs`, and `group_deriver` are already rebuilt there (`:40-105`);
  the constraint phase joins them. The snapshot path always runs `include_all=True`
  (`graph_rebuild.py:94,175`), so P2's roots-before-pruning is inert offline — but P3's extend
  (the CONSTRAINT + REPORT_AGGREGATOR nodes + minted entry points) is what produces the parity
  structure and must run.
- **[INHERITED: concept Required Invariant, line 139; epic Item 8 §3; S3/S4]** `constraint_id`s
  and catalog ordering are **byte-identical** across live and snapshot generation. One
  `constraint_id` maps to exactly one effective predicate source, usage, concrete owner
  instance, membership kind, and polarity within an executable fingerprint, identical on both
  paths.
- **[INHERITED: S4 carry-forward (3), concept line 299; epic Item 8 §3]** **Serialization
  fidelity is a named property.** S4's sidecar re-derived the registry/backtracker offline but
  *carried* the facts; production moves the sidecar into the versioned snapshot, so the
  carriage must be lossless — a fact that changes across the round-trip changes the derived ID.
  A test asserts the facts (and occurrences) reload identical to what was captured.
- **[INFERRED]** Parity is proven on a fixture that **lowers cleanly** — `wi014_toy` (S4's own
  proven model) or `constraint_multi_instance` (the Item-5 multi-occurrence fixture). Not on
  `plant_values`/`fusion_tea` (the `gain`-blocked pair). The multi-instance fixture is the
  stronger parity target: it exercises per-occurrence expansion, the exact path that needs the
  serialized occurrence data offline.

### The default flip and the carve-out

- **[NEED]** *(named responsibility from the run, recorded in Item 5's plan/audit; orchestrator
  decision Q1(a), 2026-07-12)* Flip `build_pipeline_context`'s `lower_constraints_enabled`
  default from False to True (`pipeline_builder.py:697`). The flip is gated on the parity
  criterion above being met. The transitional comment block at `pipeline_builder.py:856-863`
  retires with the flip.
- **[INFERRED]** *(orchestrator decision Q1(a))* **Carve-out flag-off grandfather.**
  `plant_values` and `fusion_tea` are generated/captured **flag-off** (un-lowered, today's
  behavior — baselines byte-identical) behind a **loud, named exclusion list**, because their
  `'Viability Threshold'` assertion (`in eta = driver.efficiency; in gain = gain;`) hits the
  `gain` hierarchy-extraction gap: `hif_plant.sysml:87`'s `:>> gain = 80.0` is a top-level
  design-instance self-redefinition that `materialize_supplied_values`
  (`resolution/supplied_values.py`) does not synthesize a design attribute for, so the strict
  resolver raises `unresolved actual 'gain'` — a **halt** (INV-2), not the non-halting
  "cataloged unassessed" path. A global flip without the carve-out would halt these two
  fixtures' capture and break the corpus.
  - The exclusion list is **named and visible** in code and docs, not an implicit skip — a
    reader must see exactly which two fixtures run flag-off and why (Design Principle: loud on
    gap). Design picks the mechanism (an explicit per-fixture flag-off in the capture script's
    MODELS handling, or equivalent) that keeps the two baselines byte-identical while the rest
    flip.
- **[NEED]** *(orchestrator decision Q1(a) — the "named prerequisite, not deferral" addition)*
  The `gain` extraction gap is a **named Item-14 prerequisite**. Item 14's acceptance test —
  "the IFE sweep's hand-coded viability rule is replaced by the generated assertion" (epic
  Success Criteria; Item 14 §3) — *requires* `fusion_tea`'s `'Viability Threshold'` to lower,
  which requires the `gain` gap fixed first. Item 14's scope note "regenerate the fusion-tea IFE
  package" implies generating it **lowered**. So this spec hands Item 14, explicitly, as its
  first work: fix the `materialize_supplied_values` gap (synthesize top-level design-instance
  `:>>` self-redefinitions) and **re-land the two grandfathered fixtures lowered** under their
  own byte-identity gates, removing them from the exclusion list. This is a prerequisite for
  Item 14's acceptance, not optional cleanup.

  *(Rejected alternatives, recorded as decision records — do not re-litigate: (b) convert the two
  fixtures to expected-halt rejection fixtures — retires the acceptance fixture's real baseline
  for a full epic-item span; (c) pre-filter the constraint via Item 3's profile — mislabels an
  admissible constraint as unassessed and reaches into Item 3's territory. Both were weighed and
  declined for (a).)*

### Corpus re-capture discipline

- **[HARD]** *(memory: byte-identity captured_at churn; epic Item 8 §4)* The corpus re-capture
  runs under the established discipline: regenerate, run the **timestamp-only churn check**
  (`captured_at` rewrites on every full re-capture), then revert the timestamp-only churn so
  only the intended fixtures show a diff. Review each remaining diff **deliberately** — the two
  known pre-existing stale baselines (`deep_cross_scope`, `ife_plant` — memory:
  `deep-cross-scope-stale-baseline`) are drift to review, not wave through.
- **[INFERRED]** The v2→v3 bump forces a re-capture of **every** committed snapshot (no version
  coexistence). Expected diffs, enumerated for review: (1) `snapshot_format_version: 2 → 3`
  everywhere; (2) the new constraint-facts section on every snapshot (empty for constraint-free
  models); (3) constraint structure in the `baseline_outputs/` graphs of clean-lowering
  constraint-bearing fixtures; (4) `captured_at` churn (reverted). Anything outside this set is
  investigated, not accepted.

## Non-Goals

- **The facts schema itself** — Item 1 owns `ConstraintFacts` / `ConstraintUsageFact` /
  `ExpressionIR`. This item serializes and version-pins them; it does not change their shape.
- **Constraint code emission** — the Kleene predicate compiler, the constraint module `.py`,
  the aggregator schema, the catalog runtime, module/registry wiring — all Item 7. This item
  wires lowering (graph *structure*) into the snapshot path; it emits nothing.
- **Graph rebuild logic beyond wiring facts in** — the offline registry/backtracker/graph-builder
  re-derivation already exists (`graph_rebuild.py`). This item adds the constraint phase to it
  and the occurrence data that phase needs; it does not redesign the rebuild.
- **Fixing the `gain` hierarchy-extraction gap** — that is Item 14's named prerequisite (above).
  This item grandfathers the two affected fixtures flag-off and hands the fix on; it does not
  touch `materialize_supplied_values`.
- **Fingerprint sealing and contracts** — Item 9. The parity this item proves is graph/catalog
  identity, an input to the fingerprint, not the fingerprint itself.
- **Artifact-level live/snapshot parity when Item 7 has not yet landed** — if this item
  implements before Item 7, parity is proven at the ComputationGraph / catalog-identity level,
  and re-proven at the emitted-artifact level in Item 7's wake (Item 7's own success criterion
  "live/snapshot generation byte-identical for a constraint-bearing fixture" carries it).

## Open Questions / Deferred to design

- **The offline part-instance index — design's first decision.** Offline re-lowering needs
  per-occurrence expansion, but `build_part_instance_index()` takes a live model the snapshot
  path lacks. Two shapes: (a) serialize the computed **occurrences** (`InstanceOccurrence`
  records with `instance_path` / `occurrence_index`) and feed them to lowering directly; (b)
  serialize the **index inputs** and rebuild the index offline from `hierarchy_data`. Design
  picks, with the constraint that the offline occurrences are byte-identical to the live ones
  (or the derived `constraint_id`s diverge). This is the highest-risk new surface — the
  multi-instance parity fixture is what catches a divergence.
- **Where the raw `ConstraintFacts` reach capture.** Thread them onto `PipelineContext`
  alongside `concrete_constraints`, or re-extract inside `capture_snapshot`. The requirement is
  that the *neutral* facts land in the snapshot; the plumbing is design's.
- **Format encoding of present-and-empty vs absent.** How the v3 format distinguishes a
  constraint-free model's empty facts section (load as empty catalog) from a corrupt v3
  snapshot with the section missing (raise). Likely "always write the section, even when empty,"
  but design pins it against the loader's raise/degrade branches.
- **The exclusion-list mechanism.** How `plant_values`/`fusion_tea` are held flag-off while the
  default flips globally — a per-fixture override in the capture script's MODELS handling, or
  equivalent — kept explicit and named, not an implicit skip.
- **Coordinating the two flip surfaces.** The live `build_pipeline_context` default and the new
  from-snapshot lowering behavior must agree, and the byte-identity corpus is captured through
  the snapshot path (`capture_pipeline_baselines.py:100`). Design sequences the two so the
  corpus stays green throughout, not only at the end.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 8)
- **Required Reading (from the epic):** concept Required Invariants (snapshot bullets — lines
  66, 139, 140, 142, 191) + S3/S4 results and carry-forwards (concept lines 287–299); memory:
  `byte-identity-captured_at-churn`.
- **Concept (owner-ratified):**
  `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — Required
  Invariants (the snapshot rejection + parity + fidelity bullets); Appendix B S3/S4 results and
  carry-forwards (S3 CF(2) re-derivation-vs-carriage; S4 CF(3) serialization-fidelity).
- **Certified upstream:**
  - Item 1 (agentic-mbse) — `constraint-facts/v1` envelope + `expression-ir/v1` predicate
    sub-document; both pinned here (Item 1 design D9 + amended forward-record). Reference:
    `.project/reference/agentic-mbse-landed/constraint_facts.py`,
    `.../constraint_extraction.py`.
  - Item 5 (this repo) — lowering phase + the `lower_constraints_enabled` transitional flag;
    named handoffs (the default flip; the `gain` hierarchy-extraction gap) recorded in
    `.project/active/constraint-lowering/plan.md` (Phase 4 third pass, lines 558–631) and
    `.../audit.md`.
- **Landed surfaces (read directly for design):**
  - `snapshot/__init__.py:15` (`SNAPSHOT_FORMAT_VERSION`, `SnapshotFormatError`);
    `snapshot/serializer.py` (the section list, `dropped_constraints` precedent);
    `snapshot/loader.py:127-203` (version hard-gate + the `compilation_results`
    degrade-with-warning precedent to **not** follow); `snapshot/capture.py:42`;
    `snapshot/graph_rebuild.py:26,144` (the offline rebuild path lowering wires into);
    `orchestration/snapshot_context.py` (`generate --from-snapshot` convergence).
  - `orchestration/pipeline_builder.py:697,849-979` (the flag default + P1/P2/P3 threading);
    `orchestration/pipeline_context.py` (`concrete_constraints` field).
  - `analysis/constraint_lowering.py` (`lower_constraints`, `extend_graph_with_constraints`);
    `analysis/part_instance_index.py` (`build_part_instance_index`, `occurrences_of`).
  - `scripts/capture_pipeline_baselines.py` (the byte-identity corpus, captured through the
    snapshot path; `MODELS` dict — `plant_values` is in it, the two grandfathered fixtures).
- **Orchestrator decisions (agent-grade, ratified 2026-07-12):** Q1 = (a) carve-out flag-off
  grandfather + `gain` as named Item-14 prerequisite; Q2 = serialize neutral facts + occurrence
  data for true re-derivation parity. Recorded inline above at their requirements.
- **Design:** `.project/active/snapshot-v3/design.md` (to be created)

---

**Next Steps:** After approval, `/_my_spec_review` (fresh session), then `/_my_design`.
