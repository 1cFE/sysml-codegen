# Design: Part-Instance Index — Subtype Closure and Cardinality Expansion

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12 17:37 PDT
**Branch:** constraint-exec-epic (commit 00ea1eb)
**Epic:** CONSTRAINT-EXEC — Item 4
**Complexity:** MEDIUM

---

## Overview

A new, standalone part-structure analysis that enumerates every concrete part instance in a
model — over subtype closure and fixed-multiplicity expansion — independent of calculation
templates. Item 5 (constraint lowering) is the only planned consumer; this item builds and
tests the index and wires nothing.

## Related Artifacts

- **Spec:** `.project/active/part-instance-index/spec.md`
- **Spec brief:** `.project/active/part-instance-index/briefs/spec.md`
- **Design brief:** `.project/active/part-instance-index/briefs/design.md`
- **Spike S3:** `.project/active/spike-concrete-expansion-instance-index/` (findings, `probe_instance_index.py`, `model.sysml`)
- **Concept:** `.project/concepts/constraint-execution-and-design-space-studies-claude.md` ("Concrete Lowering"; Design Principle 5; Appendix B, S3)
- **Reference:** `docs/architecture/reference/25-hierarchy-resolver.md` (multiplicity extraction)

---

## Research Findings

**The primitives the probe proved already exist**, all in `extraction/usage_extractor.py`:

- `_build_part_usage_index(model)` (`usage_extractor.py:272`) — maps every user PartDef QN to
  the PartUsages that carry it. A **retyped** `part :>> leaf : Sub` is keyed under *both* `Sub`
  and its preserved user supertype (`usage_extractor.py:284-289`) — the double-keying that makes
  the same occurrence reachable twice.
- `_supertype_closure(qn, lookup)` (`usage_extractor.py:197`) — transitive `:>` supertypes of a
  PartDef via `heritage`.
- `user_partdef_lookup(model)` (`usage_extractor.py:256`) — `{QN: PartDefElement}` for user
  PartDefs (library excluded).
- `_find_instantiation_paths(qn, index)` (`usage_extractor.py:313`) — recursively resolves
  design-relative `__`-joined paths to a PartDef's usages. **Keys by exact type, no subtype
  closure** — the S3 miss. Internally it *knows* the owning def at each recursion step
  (`parent_def_qn`, `usage_name`) but **flattens that into a string**, discarding the per-segment
  owner the correct multiplicity key needs.

**Multiplicity facts** (`MultiplicityData`, 5 fields only): `part_usage_name`,
`owning_part_def_qn`, `count`, `count_attribute_name`, `default_value`
(`data_models.py` re-export; `snapshot/loader.py:413`). Confirmed behavior
(`docs/.../25-hierarchy-resolver.md:145-178`; `test_hierarchy_resolver.py:850-896`):

- Fixed `[3]` → `count=3`, `count_attribute_name=None`.
- Parameterized `[module_count]` → `count=20` (cached **lower** bound), `count_attribute_name="module_count"`.
- `count` is `cached_lower_bound`; `count_attribute_name` is `upper_bound.referent.name`.
- **MultiplicityData carries no upper-bound, ordered, or unbounded marker.** See Bet B1 — this
  is the crux the cardinality gate turns on.

**Blocking convention:** the codebase blocks with a named `Exception` subclass —
`MissingCalcDefError`, `CircularDependencyError` (`graph_builder.py:75,1658`) — raised at the
point the invariant breaks. No warn-and-drop for structural impossibilities.

---

## Core Concept

The index is a **second, structure-only enumerator that runs beside the calc-driven one, never
through it.** Given the live model, it answers one question per part definition: *what are all
the concrete occurrences of this definition, counting subtype instances and fixed-multiplicity
siblings, each as its own identity?*

It works by composing three existing facts the S3 probe already validated live:

1. **Subtype closure over a source owner.** To find every instance of `ConstrainedLeaf`, don't
   look up `ConstrainedLeaf` alone — look up `ConstrainedLeaf` *and every user PartDef whose
   supertype closure contains it* (`SpecializedLeaf`, `RetypedContainer`'s retyped feature).
   This is the one line the current calc lookup omits, and the whole reason a constraint-only
   plain subtype is invisible today.

2. **Structured paths, not flat strings.** The index walks instantiation paths keeping each
   step's `(owning_def_qn, feature_name)`, because that pair — not the bare leaf name — is the
   correct multiplicity key. Two definitions can own a same-named `member[...]`; keying by leaf
   name collides (spec success criterion #2). The flat path the calc finder returns cannot do
   this, so the index has its own walker.

3. **Fail-closed cardinality.** A step expands into N siblings **only when the multiplicity is
   provably a single fixed literal count.** Anything else — parameterized, a range, ordered,
   unbounded — blocks with a named diagnostic that states the owner and feature. There is no
   arm that quietly emits a reduced set. This is Design Principle 5 made mechanical: silence is
   never an outcome.

The key insight is #3 read against the facts: `MultiplicityData` alone **cannot** prove "fixed
literal" — a fixed `[3]` and an unbounded `[*]` can both surface with `count_attribute_name is
None`. So the gate reads the **live multiplicity range node** (the same node
`extract_multiplicities` already reads) to *positively confirm* a single literal bound, and
treats everything it cannot confirm as blocking. Reading the live range is reading "live
PartUsage heritage already exposed," which the spec's own [HARD] permits — see the Surfacing
note below.

The index is **pure addition**: it reuses the existing part-usage index and heritage helpers
read-only, and no existing discovery path calls it. Item 5 wires it in.

## Key Bets

- **B1 — The live multiplicity range node exposes enough to positively identify a single fixed
  literal count** (lower bound, upper bound, whether the bound is a literal vs an attribute
  referent, and an ordered/nonunique marker). `extract_multiplicities` already reads
  `cached_lower_bound`, `cached_upper_bound`, and `upper_bound.referent`, so the numeric bounds
  are reachable; the ordered marker is the unconfirmed part. *If false → the gate cannot
  fail-closed from live facts and would need a new extracted field, which the [HARD]
  "no new SysIDE facts" forbids — the two constraints then genuinely conflict and must go back
  to the owner.* **De-risk first (see Handoff).**

- **B2 — `extract_multiplicities` may omit non-fixed multiplicities entirely** (it excludes
  singletons; a `[*]` or `[0..5]` might likewise produce no `MultiplicityData`). Therefore the
  gate must decide finiteness from the **live usage node per path step**, not from
  `MultiplicityData` *presence*. *If false and we relied on MultiplicityData presence → a
  non-fixed member would look like a plain singleton and emit one silent occurrence — the exact
  no-silent-drop violation the item exists to stop.* The design reads the live node precisely to
  neutralize this bet; it is stated so the plan spikes it rather than trusts it.

- **B3 — Subtype-closure projection finds every constraint-only instance.** S3 proved 9/9 live,
  including the plain subtype the current lookup misses. *If false → a constraint-only instance
  is still invisible and its assertion silently never executes.*

- **B4 — Retyped double-keying is the only source of duplicate occurrences, and dedup by
  canonical instance path is complete.** A retyped usage is keyed under both its subtype and its
  preserved supertype (`usage_extractor.py:284-289`), so closure projection reaches the same
  path twice. *If false → the index double-counts an occurrence (Item 5 mints two constraint IDs
  for one real element) or, if the dedup key is too coarse, drops a genuine sibling.*

## Key Decisions

- **D1 — New module `analysis/part_instance_index.py`.** *Rejected: extend `usage_extractor.py`*
  (it is calc-usage extraction; the index is structure analysis over extraction output — mixing
  them muddies the additive boundary). *Rejected: an orchestration seam* (the index is a fact
  provider, not orchestration; it must be unit-testable without a pipeline). Placement in
  `analysis/` matches its siblings (`dependency_backtracker`, `parameter_groups`) — derived
  analysis over extracted facts.

- **D2 — Own structured-occurrence walker, beside `_find_instantiation_paths`, reusing the
  part-usage index and heritage helpers read-only.** *Rejected: reuse the flat path finder +
  leaf-name multiplicity match* (the S3 probe's shape, `probe_instance_index.py:81`) — it keys
  multiplicity by bare leaf name and **provably collides** when two defs own a same-named member
  (spec success criterion #2; carry-forward (1)). The flat string discards the per-segment
  owning def the correct key needs, so a new walker is the minimum that satisfies the criterion.
  The original finder is untouched (additive [HARD]).

- **D3 — Fail-closed cardinality gate.** A path step expands **iff** its live multiplicity is a
  single fixed integer literal: bounds present, lower == upper, bound is a literal (no attribute
  referent, i.e. `count_attribute_name is None`), and not ordered/nonunique. Every other
  shape — parameterized, `[lo..hi]` range, `[*]`, ordered — **blocks**. *Rejected: expand on
  `count is not None` (the probe's gate, `probe_instance_index.py:70`)* — lets a parameterized
  or unbounded count expand silently ([HARD]). *Rejected: expand on `count_attribute_name is
  None` alone* — cannot distinguish `[3]` from `[*]` (B1), so it would silently expand a
  non-finite shape. The parameterized case is fully decidable from `MultiplicityData`; the
  range/ordered/unbounded cases need the live node (B1/B2).

- **D4 — Blocking diagnostic: a `NonFiniteCardinalityError(Exception)` raised when the index is
  built/queried, naming `owning_part_def_qn` and `part_usage_name`.** *Rejected: raise at
  extraction time* — extraction is shared with corpus generation; raising there would break the
  byte-identity [HARD] the moment a corpus model contains a parameterized multiplicity (which the
  real corpus has everywhere, e.g. `Solar_Array[module_count]`). The block must fire only on the
  path to a **queried** owner, so it lives in the index, which no corpus-generation path calls in
  this item. *Rejected: warn-and-drop* — violates Design Principle 5.

- **D5 — Per-occurrence identity is a structured `InstanceOccurrence`; the human-readable
  `instance_path` string is derived, not primary.** A multiplicity member renders as
  `owner__…__member[index]` (brackets, matching the S3 probe spelling that round-tripped through
  snapshot). Item 5 owns final `constraint_id` minting and any identifier sanitization; the index
  only guarantees a stable, unique, structured identity. *Rejected: a bare string as the primary
  type* — Item 5 needs the retained `(owning_def, feature, index)` structure to wire siblings and
  key collisions; a flattened string throws it away.

- **D6 — Deterministic order by a structured sort key**, `(tuple(segment_names), tuple(indices))`,
  with the string rendered after sorting. *Rejected: sort the rendered strings* — `member[10]`
  would sort before `member[2]`. The probe's `sorted(...)` held only because its fixture stayed
  single-digit; production must sort on the integer index.

- **D7 — Dedup by canonical instance path (the structured key), set-style**, mirroring the
  probe's set-dedup over closure paths (`probe_instance_index.py:100-106`). Two closure hits on a
  retyped usage collapse to one occurrence.

## Architecture

**Inputs (read-only):** the live SysIDE `model`, and the extracted `list[MultiplicityData]`
(from `HierarchyExtractionResult.multiplicities`) for owning-def+feature keying and the literal
count. The gate additionally reads each path step's **live multiplicity range node** for the
finite determination (B1/B2).

**Output:** a `PartInstanceIndex` object exposing:
- `occurrences_of(part_def_qn) -> list[InstanceOccurrence]` — all concrete occurrences of a
  definition over its subtype closure, deterministically ordered, multiplicity expanded or
  blocked. This is the Item-5 entry point.
- (optional convenience) `all_source_owners()` / `all_occurrences()` for tests and diagnostics.

**Data flow, per `occurrences_of(owner_qn)`:**

1. **Closure set** — `applicable = {owner_qn} ∪ {qn : owner_qn ∈ _supertype_closure(qn, lookup)}`,
   sorted (D6). (S3 §"subtype-closure prototype".)
2. **Structured walk** — for each applicable type, the new walker yields structured paths
   (`list[PathStep(owning_def_qn, feature_name)]`), reusing `_build_part_usage_index` and the
   same owning-type recursion `_find_instantiation_paths` uses — but retaining each step.
3. **Cardinality expansion** — for each step, classify its live multiplicity (D3). Fixed literal
   → fan out into `count` indexed members; non-finite → raise `NonFiniteCardinalityError` (D4);
   singleton → pass through. Expansion is a Cartesian product down the path (a fixed
   `Bank[2]` containing `member[3]` yields 6 — see Non-Fixture Shapes).
4. **Dedup + order** — collapse duplicate canonical paths (D7); sort by structured key (D6).

**Boundaries:** the index imports the three helpers from `usage_extractor` and
`MultiplicityData` from `data_models`. It does **not** import or call `pipeline_builder`,
`graph_builder`, or any generation code. Nothing existing imports it.

## Required Invariants

- **INV-1 (additive):** no existing symbol's behavior changes. `_find_instantiation_paths`,
  `find_instance_paths_for_partdef`, and template expansion keep their exact output; the corpus
  regenerates byte-identically. The index is new code beside them, called by nothing in this item.
- **INV-2 (totality / no silent drop):** every multiplicity a queried path passes through is
  either expanded to a proven finite count or blocks with a named diagnostic. No third arm.
- **INV-3 (determinism):** `occurrences_of(qn)` returns byte-identical, identically-ordered
  results across repeated live loads of the same model (D6; no reliance on `heritage`/`types`
  iteration order — closure and keys sort by QN string, as `most_specific` already does).
- **INV-4 (occurrence uniqueness):** each concrete occurrence appears exactly once, carrying its
  own identity (D5/D7). Fixed-multiplicity siblings are distinct occurrences, not copies.
- **INV-5 (collision-free keys):** multiplicity expansion keys by `(owning_part_def_qn,
  part_usage_name)`, never bare leaf name (carry-forward (1)).

## Component Overview

- **`analysis/part_instance_index.py`** (new) — the whole feature. Holds:
  - `PathStep`, `InstanceOccurrence` — small frozen dataclasses (structured identity, D5).
  - `NonFiniteCardinalityError` — the blocking diagnostic (D4).
  - the structured-occurrence walker (D2) and the cardinality classifier (D3).
  - `build_part_instance_index(model, multiplicities) -> PartInstanceIndex` and the
    `PartInstanceIndex` query object.
- **Reused, unchanged:** `_build_part_usage_index`, `_supertype_closure`, `user_partdef_lookup`
  (`usage_extractor.py`); `MultiplicityData` (`data_models.py`).
- **Test fixture** — the S3 `model.sysml`, promoted into `tests/fixtures/` and **extended** with
  the collision shape and a blocking shape (see Validation).

## Non-Goals

- Constraint expansion, actual resolution, `constraint_id` minting, catalog construction — Item 5.
- Wiring fixed-multiplicity siblings to channels — Item 5 (carry-forward (3)).
- Changing calc-driven instance discovery, or retrofitting subtype closure onto it — [HARD] INV-1.
- Any constraint fact schema, snapshot section, or live/snapshot ID re-derivation parity —
  Items 1–2 / Item 5 (spec Surfacing note).
- Expanding non-fixed multiplicities — blocked, not supported (S3 open follow-up).

## Implementation Notes

- **Do not modify `_find_instantiation_paths`.** The walker is a *new* function that mirrors its
  owning-type recursion but yields `list[PathStep]` instead of a joined string. Copy the
  recursion shape (`owning_type` → `PartDefinition` recurse; else terminal); do not refactor the
  original into a shared core in this item (that would risk INV-1).
- **The cardinality classifier is the risky surface.** Give it one job: return
  `Fixed(count) | NonFinite(reason)` for a `(usage_node, owning_def_qn, feature_name)`. It reads
  the live multiplicity range; it cross-checks the literal count against the matching
  `MultiplicityData` for consistency. Keep it a pure function so its truth table is unit-tested
  directly against mock range nodes (as `test_hierarchy_resolver.py` mocks them).
- **Sort keys carry integers, not `[10]` strings** (D6).
- Interface sketch (illustrative, not implementation):

```python
@dataclass(frozen=True)
class PathStep:
    owning_def_qn: str
    feature_name: str
    occurrence_index: int | None   # set only for a fixed-multiplicity member

@dataclass(frozen=True)
class InstanceOccurrence:
    part_def_qn: str               # concrete type instantiated (may be a subtype)
    steps: tuple[PathStep, ...]
    @property
    def instance_path(self) -> str: ...   # "root__bank__member[0]"

class NonFiniteCardinalityError(Exception): ...  # names owner + feature
```

## Potential Risks

- **Ordered/unbounded API (B1).** If the live range node does not expose an ordered marker, the
  gate cannot distinguish ordered from a plain fixed `[3]`. Mitigation: de-risk with a spike
  before finalizing the classifier (Handoff); design stays fail-closed so an *unrecognized* shape
  blocks rather than expands.
- **Non-fixed multiplicity omitted by extraction (B2).** Mitigation: the gate decides from the
  live usage node per step, not from `MultiplicityData` presence — a member with any
  multiplicity range that is not a proven single literal blocks.
- **Intermediate-container multiplicity.** A multiplicity on a container on the path (not just the
  leaf) must expand or block too. The structured walk sees every step, so this is handled by
  construction — but it is untested by S3; the fixture must cover it (Validation).
- **Closure cost.** `_supertype_closure` runs per applicable candidate; for a large corpus this
  is O(defs × closure). Acceptable — the index is queried per constraint-owner, not per instance,
  and the corpus PartDef count is small. Note only; no premature caching.

## Integration Strategy

Additive and inert this item. `build_part_instance_index` is importable and tested in isolation;
no production caller. Item 5 will call `occurrences_of(owner_qn)` for each constraint-owning
definition, mint a `constraint_id` per `InstanceOccurrence`, and wire siblings — the seam is the
`PartInstanceIndex` query object, most naturally constructed in `pipeline_context` assembly
alongside the existing `HierarchyExtractionResult`. That construction is Item 5's edit, not this
item's.

## Validation Approach

**Promote and extend the S3 fixture** into `tests/fixtures/` (calc-free). Kept tests assert:

1. **9/9 oracle** — `occurrences_of("…ConstrainedLeaf")` returns exactly the nine concrete
   occurrences (two direct, two nested, one retyped inherited feature, one plain subtype, three
   `[3]` members), zero unexpected, including the plain subtype (spec criterion #1; S3 oracle).
2. **Collision case** — extend the fixture so two definitions own a same-named `member` with
   **different** counts; assert each expands to its own count keyed by owning def (criterion #2).
   This is the test the probe asserted away (`probe_instance_index.py:74-77`).
3. **Blocking** — add a parameterized `[n]` member (decidable from `MultiplicityData`) and assert
   `NonFiniteCardinalityError` names owner+feature. Add an unbounded/ordered member to exercise
   the live-range gate **once B1 is confirmed** (criterion #3).
4. **Determinism** — two fresh live loads produce identical ordered `instance_path` lists
   (criterion #4).
5. **Byte-identity** — a corpus-regeneration test confirms adding the module perturbs no existing
   artifact (criterion #5). Since nothing calls the index, this is expected to hold trivially;
   the test guards against an accidental import-time side effect.
6. **Classifier truth table** — unit tests over mock range nodes: fixed `[3]`→Fixed(3),
   `[module_count]`→NonFinite, `[0..5]`→NonFinite, `[*]`→NonFinite, ordered→NonFinite.

Manual: run the promoted fixture through the same licensed environment S3 used
(`PYTHONPATH=…/sysml-codegen/src uv run --directory …/agentic-mbse`) — the codegen venv has no
SysIDE license (S3 findings §2; memory "syside license via scripts").

## Next-Stage Handoff

- **Fixed:** module placement (D1), the fail-closed gate principle (D3), the diagnostic type and
  its raise site (D4), owning-def+feature keying (INV-5), structured occurrence identity (D5),
  determinism mechanism (D6), additive boundary (INV-1). The concept/spec settle these.
- **Open (plan decides):** exact `instance_path` spelling within the D5 convention; whether
  `PartInstanceIndex` also offers a bulk `all_occurrences()`; fixture package name.
- **De-risk first — before writing the classifier:** a throwaway spike (`/_my_spike`) that loads
  a model with `[3]`, `[module_count]`, `[0..5]`, `[*]`, and an ordered member, and prints what
  the live multiplicity range node exposes for each (bounds, referent, ordered marker) and what
  `extract_multiplicities` emits for each. This confirms B1 and B2 — the two bets the whole
  no-silent-drop guarantee rests on. If the ordered/unbounded markers are not reachable, **stop
  and surface**: the [HARD] "no new SysIDE facts" and Design Principle 5 conflict, and the owner
  must choose (extend extraction vs narrow the executable scope).

## Surfacing note (do not resolve silently)

The spec's [HARD] says the index "consumes the existing extraction facts only: `MultiplicityData`
(…) and the live PartUsage / PartDefinition heritage already exposed," and separately that the
gate must "treat a present `count_attribute_name` (and **any ordered/unbounded marker**) as
non-finite and block it." **`MultiplicityData`'s five fields carry no ordered or unbounded
marker.** So a gate reading `MultiplicityData` alone cannot honor the second clause for
range/ordered/unbounded shapes: it would either expand a non-finite multiplicity silently
(violating Design Principle 5, the higher invariant) or block all multiplicities (breaking the
`[3]`→3 success criterion).

This design resolves the tension **toward no-silent-drop** by reading the *live multiplicity range
node* — which the same [HARD]'s first clause explicitly permits ("the live PartUsage … heritage
already exposed") and which `extract_multiplicities` already reads. It does **not** add an
extracted field. The residual risk is B1 (is the ordered marker reachable on the live node?),
quarantined to the de-risk spike above. Flagged here rather than resolved silently in code.

---

**Next Step:** After approval → `/_my_spike` (confirm B1/B2), then `/_my_plan` or `/_my_implement`.
