# Design: Part-Instance Index — Subtype Closure and Cardinality Expansion

**Status:** Draft (rev 2 — must-fixes C1–C3, M1–M2, minors folded in from design-review + B1/B2 evidence)
**Owner:** Reid W
**Created:** 2026-07-12 17:37 PDT
**Revised:** 2026-07-12 (post design-review)
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
- **B1/B2 evidence:** `.project/active/part-instance-index/b1-probe-evidence.md` (live multiplicity surface, confirmed 2026-07-12; `probe_b1_multiplicity.py`)
- **Design review:** `.project/active/part-instance-index/design-review.md` (Approved-with-must-fixes)
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

**Multiplicity — the live surface (B1/B2 evidence, confirmed live SysIDE 0.8.4).** The gate reads
the usage's live `multiplicity` node, not the extracted `MultiplicityData`. Per the evidence table
(`b1-probe-evidence.md`), each shape is identified by the **node type of `upper_bound`** plus two
flags on the **usage**:

| shape | `upper_bound` node | `lower_bound` node | usage flags | verdict |
|---|---|---|---|---|
| `[3]` | `LiteralInteger(3)` | `None` | — | admit, count 3 |
| `[3..3]` | `LiteralInteger(3)` | `LiteralInteger(3)` | — | admit, count 3 (C2) |
| `[0..5]` | `LiteralInteger(5)` | `LiteralInteger(0)` | — | block (range) |
| `[*]` | `LiteralInfinity` | `None` | — | block (unbounded) |
| `[n]` (attr) | `FeatureReferenceExpression` | `None` | — | block (parameterized) |
| `[3] ordered` | `LiteralInteger(3)` | `None` | `is_ordered=True` | block |
| `[3] nonunique` | `LiteralInteger(3)` | `None` | `is_nonunique=True` | block |
| singleton | `usage.multiplicity is None` | | | pass through (1 occurrence) |

Two facts kill any cached-value or `MultiplicityData`-based gate: (1) `cached_upper_bound` is
**exclusive** (4 for `[3]`), and (2) a parameterized `[n]` resolves its default into
`cached_upper_bound` (non-`None`) — so a gate keyed on cached counts silently expands the default.
**Node-type dispatch on `upper_bound` is mandatory.** For reference, `MultiplicityData` (5 fields:
`part_usage_name`, `owning_part_def_qn`, `count`, `count_attribute_name`, `default_value`;
`data_models.py`; `snapshot/loader.py:413`) still drives the aggregation path unchanged, but the
index does **not** use it — see D8.

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

The key insight is #3 read against the confirmed live surface (B1/B2 evidence): the extracted
`MultiplicityData` **cannot** distinguish the shapes — a fixed `[3]` and a parameterized `[n]`
both carry a non-`None` cached count, so any cached-value gate silently expands the parameter's
default. The finiteness verdict lives only in the **node type of the live `upper_bound`**
(`LiteralInteger` vs `LiteralInfinity` vs `FeatureReferenceExpression`) plus the usage's
`is_ordered`/`is_nonunique` flags. So the gate dispatches on those live nodes to *positively
confirm* a single literal bound and blocks everything else. Reading the live multiplicity node is
reading "live PartUsage heritage already exposed," which the spec's own [HARD] permits — see the
Surfacing note below.

The index is **pure addition**: it reuses the existing part-usage index and heritage helpers
read-only, and no existing discovery path calls it. Item 5 wires it in.

## Key Bets

B1 and B2 were the load-bearing bets; the orchestrator's live probe (`b1-probe-evidence.md`)
**confirmed both as facts**. They are recorded here as settled evidence, not open risk.

- **B1 — CONFIRMED. The live multiplicity node positively identifies a single fixed literal.**
  `upper_bound`'s node type is `LiteralInteger` for a literal, `LiteralInfinity` for `[*]`,
  `FeatureReferenceExpression` for a parameterized `[n]`; `is_ordered`/`is_nonunique` live on the
  **usage**, not the range node. The gate dispatches on these (D3). No new extracted field is
  needed, so the [HARD] "no new SysIDE facts" and Design Principle 5 no longer conflict.

- **B2 — CONFIRMED, stronger than feared. Cached counts are untrustworthy for the gate.** A
  parameterized `[n]` resolves its default into `cached_upper_bound` (non-`None`), so a gate keyed
  on cached counts or `MultiplicityData` presence would silently expand the default — the exact
  no-silent-drop violation. This is why the gate is node-type dispatch on the live `upper_bound`
  and the classifier ignores `MultiplicityData` entirely (D8).

- **B3 — Subtype-closure projection finds every constraint-only instance.** S3 proved 9/9 live,
  including the plain subtype the current lookup misses. *If false → a constraint-only instance
  is still invisible and its assertion silently never executes.*

- **B4 — Retyped double-keying is the only source of duplicate occurrences, and
  entry-independent dedup is complete.** A retyped usage is keyed under both its subtype and its
  preserved supertype (`usage_extractor.py:284-289`), so closure projection reaches the same
  usage from two entry types. B4 holds **only if** the occurrence's `part_def_qn` and the dedup
  key are derived from the usage itself, not the closure-entry type (D5/D7/C3). *If false — if the
  record carries the entry type — the two hits differ by `part_def_qn` and dedup keeps an
  arbitrary one, recording the supertype as the concrete type and dropping the real subtype.*

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

- **D3 — Fail-closed cardinality gate, by node-type dispatch on the live `upper_bound`** (re-pinned
  to the B1 evidence table). For a usage's live `multiplicity` node:
  - `usage.is_ordered` **or** `usage.is_nonunique` → **block** (read off the *usage*, not the range
    node).
  - else on the `upper_bound` node type:
    - `LiteralInfinity` → **block** (`[*]`, unbounded).
    - `FeatureReferenceExpression` (referent an attribute) → **block** (`[n]`, parameterized).
    - `LiteralInteger(u)`:
      - `lower_bound` node is `None` → **admit**, count = `u` (bare `[u]`).
      - `lower_bound` node is `LiteralInteger(l)`, `l == u` → **admit**, count = `u` (`[u..u]`; see C2).
      - `lower_bound` node is `LiteralInteger(l)`, `l != u` → **block** (`[lo..hi]` range).
    - any other `upper_bound` node type → **block** (unrecognized ⇒ fail-closed).
  - `usage.multiplicity is None` → singleton, pass through as one occurrence.

  The gate reads the live nodes only — **not** cached bounds, **not** `MultiplicityData` (B2: a
  parameterized default leaks into `cached_upper_bound`, so cached values lie). *Rejected: expand on
  `count is not None` (the probe's gate, `probe_instance_index.py:70`)* — lets a parameterized or
  unbounded count expand silently. *Rejected: "bounds present, lower == upper" on cached values (an
  earlier draft of this gate)* — `[3]` presents as `lower_bound` node `None`, `cached 3/4`, so that
  test blocks the simplest fixed case; the node-type dispatch above is what the live surface
  actually supports.

- **C2 decision — `[3..3]` (equal literal bounds) is admitted as fixed count 3.** It is
  semantically identical to `[3]`. Recorded as an orchestrator decision (agent-grade), following
  the review and evidence recommendation; a dedicated test pins it (Validation #7). *Rejected:
  block `[3..3]`* — it is a determinate finite singleton set; blocking it would be a spurious
  false-positive with no safety benefit.

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
  snapshot). `InstanceOccurrence.part_def_qn` is the **most-specific user type of the usage node
  itself** (via `most_specific`, `usage_extractor.py:221`), computed once from the usage —
  **entry-independent**, never the closure-entry type the walk arrived through. Item 5 owns final
  `constraint_id` minting and any identifier sanitization; the index only guarantees a stable,
  unique, structured identity. *Rejected: a bare string as the primary type* — Item 5 needs the
  retained `(owning_def, feature, index)` structure to wire siblings and key collisions.
  *Rejected: `part_def_qn` = the closure-entry type* — a retyped `part :>> leaf : SpecializedLeaf`
  is keyed under **both** `SpecializedLeaf` and its preserved supertype `ConstrainedLeaf`
  (`usage_extractor.py:283-289`), so the walk reaches it from two entry types; setting the field to
  the entry type makes the two records differ, and dedup (D7) would keep an arbitrary one —
  `ConstrainedLeaf` sorts first and would wrongly win, recording the *supertype* as the concrete
  type and dropping `SpecializedLeaf` (C3). The usage-derived type is identical from both entries.

- **D8 — The classifier reads the live multiplicity node as its single source of truth; it does
  not read `MultiplicityData` at all.** B1 proves the live `upper_bound` node yields both the
  finiteness verdict and the count; B2 proves extraction *omits* the non-fixed shapes we most need
  to block (and `[3..3]`), so `MultiplicityData` is absent exactly where a cross-check would
  matter. The owning-def+feature key (INV-5) comes from the walk's `PathStep`
  (`owning_def_qn`, `feature_name`), the same `(owning def, feature)` identity carry-forward (1) names,
  — not from `MultiplicityData`. *Rejected: read `MultiplicityData` and cross-check the count* — it
  introduces a missing-data ambiguity (is an absent `MultiplicityData` an inconsistency that
  blocks, or benign?) with no benefit, since the live node is already authoritative and mandatory.
  This challenges the [INHERITED] carry-forward (1) phrasing "keyed … on the extracted
  `MultiplicityData`": the key *fields* are honored, but sourced from the live walk, because the
  B1/B2 evidence shows `MultiplicityData` cannot be the finiteness authority. Surfaced, not silent.

- **D6 — Deterministic order by a structured sort key**, `(tuple(segment_names), tuple(indices))`,
  with the string rendered after sorting. *Rejected: sort the rendered strings* — `member[10]`
  would sort before `member[2]`. The probe's `sorted(...)` held only because its fixture stayed
  single-digit; production must sort on the integer index.

- **D7 — Dedup by canonical instance path (the structured key), set-style**, mirroring the
  probe's set-dedup over closure paths (`probe_instance_index.py:100-106`). Two closure hits on a
  retyped usage collapse to one occurrence.

## Architecture

**Inputs (read-only):** the live SysIDE `model` — and nothing else. Owning-def+feature keys and
the fixed count both come from the live walk and each step's live `multiplicity` node (D8); the
extracted `MultiplicityData` is not consumed.

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
3. **Cardinality expansion** — for each step, the classifier dispatches on the usage's live
   `multiplicity` node (D3). Fixed literal → fan out into `count` indexed members; non-finite →
   raise `NonFiniteCardinalityError` (D4); singleton → pass through. Expansion is a **Cartesian
   product down the path**: a fixed `Bank[2]` containing `member[3]` yields 6 occurrences, each
   carrying both step indices (`bank[i]__member[j]`). Every multiplicity on the path is gated, not
   just the leaf.
4. **Dedup + order** — collapse duplicate occurrences by entry-independent key (D7); sort by
   structured key (D6).

**Boundaries:** the index imports `_build_part_usage_index`, `_supertype_closure`,
`user_partdef_lookup`, and `most_specific` from `usage_extractor`. It does **not** import
`MultiplicityData`, `pipeline_builder`, `graph_builder`, or any generation code. Nothing existing
imports it.

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
  own identity (D5/D7). The identity — `part_def_qn` and the dedup key — is derived from the usage,
  **entry-independent**, so a double-keyed retyped usage collapses to one record with the correct
  most-specific type (C3). Fixed-multiplicity siblings are distinct occurrences, not copies.
- **INV-5 (collision-free keys):** multiplicity expansion keys by `(owning_part_def_qn,
  part_usage_name)` from the walk's `PathStep`, never bare leaf name (carry-forward (1)).

## Component Overview

- **`analysis/part_instance_index.py`** (new) — the whole feature. Holds:
  - `PathStep`, `InstanceOccurrence` — small frozen dataclasses (structured identity, D5).
  - `NonFiniteCardinalityError` — the blocking diagnostic (D4).
  - the structured-occurrence walker (D2) and the cardinality classifier (D3).
  - `build_part_instance_index(model) -> PartInstanceIndex` and the `PartInstanceIndex` query
    object.
- **Reused, unchanged:** `_build_part_usage_index`, `_supertype_closure`, `user_partdef_lookup`,
  `most_specific` (`usage_extractor.py`).
- **Test fixture** — the S3 `model.sysml`, promoted into `tests/fixtures/` and **extended** with
  the collision, blocking (`[n]`/`[*]`/`[0..5]`/ordered/nonunique), `[3..3]`, and
  Cartesian/nested-multiplicity shapes (see Validation).

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
  original into a shared core in this item (that would risk INV-1). **Replicate the `_visited`
  cycle guard** (`usage_extractor.py:335-337`) — without it the walker infinite-loops on cyclic
  part containment. The two recursions must be kept in sync by hand; note it at both sites.
- **The cardinality classifier is the risky surface.** Give it one job: return
  `Fixed(count) | NonFinite(reason)` for a `(usage_node, owning_def_qn, feature_name)`. It reads
  the usage's live `multiplicity` node and the usage's `is_ordered`/`is_nonunique` flags (D3) —
  **and nothing else; no `MultiplicityData`** (D8). Dispatch on the `upper_bound` node *type*, not
  on cached values (B2). Keep it a pure function so its truth table is unit-tested directly against
  mock nodes (as `test_hierarchy_resolver.py` mocks multiplicity nodes).
- **`part_def_qn` is computed from the usage, once, via `most_specific`** — entry-independent (C3),
  so the dedup key is stable across both keying entries of a retyped usage.
- **Sort keys carry integers, not `[10]` strings** (D6). The key `(tuple(segment_names),
  tuple(indices))` compares `indices` only when `segment_names` are equal — which guarantees the
  same feature and therefore aligned `None`/`int` positions, so a `None < int` `TypeError` never
  arises. This is a real invariant the sort rests on; note it, or normalize `occurrence_index` to a
  sortable sentinel (e.g. `-1` for singletons) so a future key change cannot reintroduce the hazard.
- Interface sketch (illustrative, not implementation):

```python
@dataclass(frozen=True)
class PathStep:
    owning_def_qn: str
    feature_name: str
    occurrence_index: int | None   # set only for a fixed-multiplicity member

@dataclass(frozen=True)
class InstanceOccurrence:
    part_def_qn: str               # usage's own most-specific type (entry-independent, C3)
    steps: tuple[PathStep, ...]
    @property
    def instance_path(self) -> str: ...   # "root__bank__member[0]"

class NonFiniteCardinalityError(Exception): ...  # names owner + feature
```

## Potential Risks

- **Ordered/unbounded/parameterized detection (B1/B2) — retired by evidence.** The live surface is
  confirmed sufficient (`b1-probe-evidence.md`); the gate dispatches on `upper_bound` node type and
  usage flags. Residual: the classifier must handle an *unrecognized* `upper_bound` node type by
  blocking (fail-closed default arm), so a future SysIDE change cannot silently expand.
- **`nonunique` may fail model load.** The evidence notes a `nonunique` subsetting of a unique
  feature emits a load-**error** diagnostic (`subsetting-uniqueness-conformance`), so such a model
  may never reach the gate. The gate still blocks it if it does arrive; it does not rely on the
  load error.
- **Intermediate-container multiplicity.** A multiplicity on a container on the path (not just the
  leaf) must expand or block too. The structured walk sees every step, so it is handled — and it is
  now **explicitly tested** (Validation #8), not left to "by construction."
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
3. **Blocking** — add a parameterized `[n]` member and assert `NonFiniteCardinalityError` names
   owner+feature. Add `[*]`, `[0..5]`, `[3] ordered`, and `[3] nonunique` members and assert each
   blocks (criterion #3; B1 confirmed, so these run now — no gating on a future spike).
4. **Determinism** — two fresh live loads produce identical ordered `instance_path` lists
   (criterion #4).
5. **Byte-identity** — a corpus-regeneration test confirms adding the module perturbs no existing
   artifact (criterion #5). Since nothing calls the index, this is expected to hold trivially;
   the test guards against an accidental import-time side effect.
6. **Classifier truth table** — unit tests over mock multiplicity nodes, one row per B1 shape:
   `[3]`→Fixed(3), `[3..3]`→Fixed(3), `[0..5]`→NonFinite, `[*]`→NonFinite, `[n]`→NonFinite,
   `[3] ordered`→NonFinite, `[3] nonunique`→NonFinite, and an unrecognized `upper_bound` node
   →NonFinite (fail-closed default).
7. **`[3..3]` admit (C2)** — a dedicated fixture member `[3..3]` expands to exactly 3 occurrences,
   pinning the equal-literal-bounds decision.
8. **Cartesian / intermediate-multiplicity (M1)** — a container with `[2]` owning a `[3]` leaf
   expands to exactly 6 occurrences with the right per-step indices (`c[i]__leaf[j]`); and a
   multiplicity under a subtype (multiplicity reached via closure) expands correctly. Covers the
   two shapes S3 never exercised.

Manual: run the promoted fixture through the same licensed environment S3 used
(`PYTHONPATH=…/sysml-codegen/src uv run --directory …/agentic-mbse`) — the codegen venv has no
SysIDE license (S3 findings §2; memory "syside license via scripts").

## Next-Stage Handoff

- **Fixed:** module placement (D1); the node-type-dispatch gate (D3) and the `[3..3]`-admit
  decision (C2); the classifier's live-node-only source of truth (D8); the diagnostic type and its
  raise site (D4); owning-def+feature keying from the walk (INV-5); entry-independent occurrence
  identity and dedup (D5/D7/C3); determinism mechanism (D6); additive boundary (INV-1). Concept,
  spec, and B1/B2 evidence settle these.
- **Open (plan decides):** exact `instance_path` spelling within the D5 convention; whether
  `PartInstanceIndex` also offers a bulk `all_occurrences()`; fixture package name; whether
  `occurrence_index` uses `None` or a `-1` sentinel for singletons (m1).
- **The B1/B2 de-risk spike is already done** (`b1-probe-evidence.md`). The plan cites that
  evidence and writes the classifier directly against the truth table (Validation #6) — no further
  spike. Build the classifier and its truth-table tests first; it is the load-bearing surface.

## Surfacing note (do not resolve silently)

The spec's [HARD] says the index "consumes the existing extraction facts only: `MultiplicityData`
(…) and the live PartUsage / PartDefinition heritage already exposed," and separately that the gate
must "treat a present `count_attribute_name` (and **any ordered/unbounded marker**) as non-finite
and block it." **`MultiplicityData`'s five fields carry no ordered or unbounded marker**, and B2
proves cached counts lie for parameterized shapes. So a gate reading `MultiplicityData` cannot
honor the second clause without either expanding a non-finite multiplicity silently (violating
Design Principle 5, the higher invariant) or blocking all multiplicities (breaking the `[3]`→3
criterion).

This design resolves the tension **toward no-silent-drop** by reading the *live multiplicity node*
— which the same [HARD]'s first clause explicitly permits ("the live PartUsage … heritage already
exposed") and which the B1 probe confirmed is sufficient. It does **not** add an extracted field.
Two consequences, both surfaced not silent:

1. **The classifier does not read `MultiplicityData` at all (D8).** The [INHERITED] carry-forward
   (1) phrasing "keyed … on the extracted `MultiplicityData`" is honored in its *intent* — keys are
   `(owning_part_def_qn, part_usage_name)` — but sourced from the live walk's `PathStep`, because
   the evidence shows `MultiplicityData` cannot be the finiteness authority and is absent for the
   non-fixed shapes.
2. The earlier B1-risk is retired; the gate is pinned to the confirmed live surface. No open
   spike remains.

---

**Next Step:** B1/B2 already confirmed (`b1-probe-evidence.md`) and must-fixes folded in →
`/_my_plan` or `/_my_implement`. No further spike.
