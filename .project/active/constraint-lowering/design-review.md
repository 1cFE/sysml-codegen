# Design Review: Concrete Constraint Lowering (Item 5)

**Design:** `.project/active/constraint-lowering/design.md`
**Spec:** `.project/active/constraint-lowering/spec.md`
**Review File:** `.project/active/constraint-lowering/design-review.md`
**Date:** 2026-07-12
**Reviewer posture:** adversarial; every claim below checked against the real code, the landed
Item-1 types, and `s4_lib.py`, not the design's word.

---

## Fundamental Assessment

**Sound.** The approach is right and the design is a faithful productionization of the S4
spike. The core frame — a fact-to-structure expander with a strict resolver, dispatching
expansion on the four-value `owning_definition.kind` and predicate selection on the orthogonal
`source.form` — matches the landed facts exactly (`constraint_facts.py:52-63`, `73-91`). The
three threading points are real seams at the lines claimed. The design is honest where it
matters most: it names B1 (per-occurrence producer channels) as the highest-risk bet and calls
for a blocking spike.

I am **not** recommending Rework. But three must-fixes below are load-bearing, and the first
one is serious: I verified against the code that **B1 is almost certainly false**, and the
design's stated mitigation for that case ("errors loud, never collapses") is wrong in the most
likely failure mode. That doesn't sink the approach — it changes what this item can promise.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec requirement has a design element, and the provenance carried from the spec is
faithful (four-kind dispatch `[HARD]`, `LocationFact` identity `[HARD]`, strict-no-synthesis
`[HARD]`, the two orthogonal axes). Two compliance gaps:

- **The blocked-owner `[HARD]` has no fixture.** Spec §Expansion requires a constraint-owning
  part def whose expansion hits a non-finite multiplicity to surface a *named generation
  error*. The design's Validation Approach lists a "Blocked owner" check, but Appendix B names
  **no fixture** for it. A `[HARD]` with no committed test is unverified. (Must-fix 2.)
- **The multi-instance success criterion (S5) is treated as reachable by resolution alone.**
  The code says it is not (Must-fix 1). This is a spec-compliance problem because S5 is a
  committed acceptance criterion, not a stretch goal.

### 2. Pattern Consistency
**Assessment:** Pass

`ConcreteConstraint` in `resolution/models.py` beside `ComputationGraph` (D4) matches where the
repo keeps graph-serializable Pydantic data. `constraint_id` = scannable prefix + `sha256[:8]`
matches both repo idioms (the `__`-joined EQN/PQN names and the `sha256` content-fingerprint
use at `extractor.py:804`). Reusing `_find_usage_for_channel` unchanged for P2 (D-note) is the
right call — S4 proved that exact seam. New module `analysis/constraint_lowering.py` (D2) is
the correct home; the rejected alternatives are argued, not hand-waved.

### 3. Abstraction Quality
**Assessment:** Concerns

The abstractions are mostly well-judged. One is overstated: the **"shared terminal-disposition
switch" (D1).** See Bets & Decisions and Route Safety — the switch buys less than the design
implies, and the real divergence risk runs the opposite direction from the one D1 guards.

### 4. Duplication Avoidance
**Assessment:** Pass

D1 explicitly refuses to duplicate or deeply refactor the backtracker's tuned ladder, keeping
the corpus byte-identity gate safe. The narrow strict resolver is a deliberate, separate path
over typed `FeatureReferenceFact` inputs rather than a fork of the `source_path` ladder — a
reasonable non-duplication call (with a caveat in §7).

### 5. Data Structure Clarity
**Assessment:** Concerns

`ConcreteConstraint`'s field list is clear except the one field that carries the most weight:
the **effective predicate.** The design calls it an "effective-predicate IR reference" and
asserts the model is "graph-serializable by construction." Neither is pinned:

- `ExpressionIR` is an agentic-mbse **dataclass**, not Pydantic/JSON-native. Embedding it in a
  Pydantic model needs `arbitrary_types_allowed` (already used elsewhere in `models.py:88`)
  **and** an explicit serialization contract for Item 8's snapshot — arbitrary types do not
  round-trip through Pydantic's JSON by default. `expression_facts`/`expression_ir` ship
  `_canonical_json` + a `parse`, so a contract exists, but the design doesn't say it will use
  it.
- "Reference" vs. inline is undecided. If Item 5 stores only a *reference* (an `IdentityFact`
  or QN), Item 7's Kleene compiler must re-hydrate the predicate from the facts — but the
  spec's own Non-Goal defers snapshot round-trip of constraint facts to Item 8, so by the time
  Item 7/8 run offline the facts may not be present. Pin inline-IR-with-a-serialization-contract
  vs. reference-plus-rehydration; both Item 7 and Item 8 depend on the answer. (Must-fix 3.)

### 6. Route Safety
**Assessment:** Concerns

INV-2 (no fallback synthesis for a constraint actual) is **structurally true**, but not for the
reason D1 emphasizes. I traced it: the fallback that synthesizes `{usage_qn}__{param}` lives
only inside `_resolve_binding_via_registry` (`dependency_backtracker.py:594-604`). Lowering
uses its *own* narrow resolver and never calls that method for a constraint actual, so the
synthesis branch is unreachable by construction — independent of any `strict` flag. Good.

The unsafe route is the opposite one, and the design under-plays it: **the multi-instance
resolver can silently collapse** (Must-fix 1). The Implementation Note asserts a missing
per-occurrence channel "errors loud … never collapses." That is false when the occurrence
scope de-indexes to a key the registry *does* hold — three siblings then resolve to one shared
channel with no error. A silent collapse is exactly the failure INV-3 exists to prevent.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The bets are genuine claims about reality with stated failure modes — good discipline. But:

- **B1 is stated honestly as highest-risk, and it is false against the current code.** The
  design earns credit for flagging it and demanding a spike. It loses credit for pairing it
  with a mitigation ("loud error if absent") that doesn't hold, and for writing S5's validation
  as if resolution will satisfy it.
- **Hidden bet behind D1.** The narrow strict ladder is `scoped_lookup` → design-attr-by-QN. It
  deliberately omits the backtracker's `alias_lookup`, `scoped_alias_lookup`, the scope CLIMB,
  and the self-reference guard (`dependency_backtracker.py:520-604`). The unstated bet is:
  *no in-profile constraint actual needs any of those omitted rungs.* If false, a reference the
  calc path resolves fine will strict-**error** on a valid model. This is B4's failure mode, but
  the design frames B4 as "can't form a lookup key," not "the narrow ladder is narrower than the
  calc ladder by design." Name the narrowing and tie it to the executable profile.
- **D1's "one code path with an explicit switch" reinterpretation.** The spec item is `[HARD]`:
  "strict and lenient modes should be one code path with an explicit switch so they cannot
  silently diverge again." The design delivers *two* paths (separate ladders) that share only
  the terminal branch, and argues the `[HARD]` intent is satisfied because the fallback is
  unreachable in strict mode. That is a defensible reading, but it **is** a reinterpretation of
  a `[HARD]` mechanism, and since the ladders are separate they *can* diverge (previous bullet).
  Surface this to the owner rather than settling it inside the design — the `[HARD]` was written
  precisely to stop silent divergence, and separate ladders reintroduce the possibility.

### 8. Reader Comprehension
**Assessment:** Pass

Strong. The two-axis frame is stated plainly up front, the core concept precedes the mechanism,
and the S4-reproduction / new-surface split is clear. The Appendix A open-question table and
Appendix B fixtures make the handoff legible. No voice issue blocks the model.

---

## The B1 probe recipe (for the orchestrator to execute)

The brief asks for an exact live-probe recipe. Here is what the code says and what the probe
must check.

**What the code already tells us (static, high-confidence):**
- The calc-driven producer pipeline does **not** fan fixed multiplicity.
  `_find_instantiation_paths` (`usage_extractor.py:313-369`) builds each path as
  `f"{parent_path}__{usage_name}"` with **no occurrence index**, and `_create_virtual_calc_usage`
  (`:387`) mints one QN `f"{instantiation_path}__{calc_name}"` per path. A `[3]` part yields
  **one** path, **one** virtual calc usage, **one** registered channel.
- Only Item 4's *structure* index fans `[i]`: `_structured_paths` + `_cardinality_indices`
  (`part_instance_index.py:139-193`), rendering `Owner__feat[i]__…` (`:211-218`).
- No `ScopedKey` anywhere in `core/` or `output_registry_builder` is built with an occurrence
  index (grep clean). `OutputRegistry._scoped` is keyed by design-prefix-stripped dotted paths
  with no `[i]`.

**Prediction:** B1 is **false** by default — the registry holds one channel for the `[3]`
part's calc, not three.

**Model shape (author `constraint_multi_instance`):**
```
part def Cell {
    calc power_calc { out p; ... }        // a per-instance producer
}
part def Container {
    part cell : Cell [3];
    assert constraint <bound> ( cell.power_calc.p );   // or an inline predicate over it
}
part def Design { part c : Container; }   // a design root that instantiates it
```

**Registry query (run inside `build_pipeline_context`, after Step 5.5/5.56):**
1. `output_registry.canonical_channels` — count channels whose name derives from
   `…__cell…__power_calc__p`.
2. Enumerate `output_registry._scoped` keys (or the public read views) for the same producer.
3. Independently, `PartInstanceIndex.occurrences_of("…::Cell")` — expect **3**
   `InstanceOccurrence`s with distinct `instance_path` (`…cell[0]/[1]/[2]`).

**Outcomes:**
- **Refute B1 (expected):** exactly **one** canonical channel and **one** scoped key for the
  producer, while `occurrences_of` returns **three** occurrences. Confirms the design's premise
  is false: three expanded constraints, one producer channel.
- **Confirm B1 (surprising):** three distinct canonical channels, each reachable by a
  `scoped_lookup` keyed from a distinct occurrence path. Would require the calc pipeline to fan
  multiplicity somewhere the static read missed — check whether `_expand_template_calc_usages`
  produced three virtuals.

**If refuted (the likely branch), the probe must also answer the design's blind spot:** with one
channel in the registry, does the occurrence→`ScopedKey` transform (a) strip `[i]` and hit that
one channel for all three siblings → **silent collapse** (INV-3 violation), or (b) keep `[i]` and
miss → three loud errors (S5 unmeetable)? Have the probe try both key forms against the real
`_scoped` dict and report which the design's transform would produce. This is the decision that
determines whether S5 is achievable in Item 5 at all, or whether meeting it requires *building*
per-occurrence producers (a scope increase this design does not cost).

---

## Issues by Severity

### Critical (must address before implementation)

- **[Must-fix 1] B1 is false against the code, and the collapse claim is wrong.** The calc
  producer pipeline registers one channel per part-def calc regardless of `[N]` multiplicity
  (`usage_extractor.py:313-369, 387`); only Item 4's structure index fans `[i]`. So resolution
  cannot hand three siblings three distinct producer channels — they either collapse onto one
  channel (silent, INV-3 violation — the Implementation Note's "errors loud, never collapses" is
  false) or all miss (S5 unmeetable). **Fix:** (a) make the R1/B1 spike *blocking* and run it
  before committing S5's wording; (b) correct the "never collapses" note; (c) state the fallback
  when B1 is false — either S5 defers to Item 7, or Item 5 acquires a per-occurrence
  producer-expansion responsibility, which must be scoped and costed here, not discovered in
  implementation. — Dimensions 1, 6, 7

### Major (should address)

- **[Must-fix 2] No fixture for the blocked-owner `[HARD]`.** Add a committed fixture: a
  constraint-owning part def reached through a `[*]`/parameterized/ranged multiplicity, asserting
  a named generation error (not a skip). Without it the `[HARD]` and the Item-4 audit cure it
  depends on are untested here. — Dimension 1
- **[Must-fix 3] Predicate-IR carriage and Item 7/8 boundary unpinned.** Decide and state:
  inline `ExpressionIR` with an explicit (de)serialization contract (via the landed
  `_canonical_json`/`parse`) vs. a reference Item 7 re-hydrates from facts — and, if reference,
  where those facts come from offline given Item 8 owns snapshot round-trip. "Graph-serializable
  by construction" is not automatic for an arbitrary dataclass field. — Dimension 5
- **[D1 reinterpretation] Surface the `[HARD]` divergence to the owner.** Two separate ladders
  sharing only a terminal switch can diverge; the narrow strict ladder omits alias/scoped-alias/
  CLIMB/self-ref rungs the calc path uses, so a valid in-profile reference can strict-error
  (B4's real failure mode). Either justify the narrowing against the executable profile in the
  design, or flag to the owner that the `[HARD]` "one code path" is being read as "one terminal
  switch." — Dimension 7

### Minor (consider)

- **[N1] `constraint_id` collision-as-error over `sha256[:8]`.** 32 bits means a spurious
  same-prefix hash collision between two genuinely distinct constraints would halt generation on
  a valid model. Very low probability, but "collision = generation error" makes it a hard halt.
  Consider `[:16]`. Determinism itself is fine (inputs are stable fact fields; `LocationFact`
  disambiguates two anonymous asserts on one instance, closing D3's cited gap). — Dimension 2
- **[N2] S1 (S4-reproduction) fixture unnamed.** The control-prune/retain criterion is implicitly
  `wi014_toy` (S4's model, present in `tests/fixtures/`), but Appendix B never lists it. Name it,
  and note the prune behavior only bites under `include_all=False` — the corpus runs
  `include_all=True`, so the test must select subset mode. — Dimension 1
- **[N3] P3 / group_deriver ordering.** `group_deriver` is constructed once at
  `pipeline_builder.py:831` over `graph_design_attrs`; P3 mints EPs into derived groups *after*
  Step 7. No mutation-after-read hazard found (P3 is additive and post-build, matching S4), but
  pin that P3 reuses the same deriver instance and that a minted EP lands in an existing derived
  group. — Dimension 5

**Threading points (probe 3) — verified, no finding.** All three seams are real and correctly
ordered: `graph_design_attrs` finalized at `:815-827`, `group_deriver` at `:831` (P1 safe
after), `find_required_modules` target list at `:840` (P2), `build_computation_graph` at `:888`
with the graph returned at `:905` (P3 after). Registry is final by Step 5.56 (`:800`). Nothing
lowering reads at P1 is mutated before it reads it.

---

## Recommendations

1. **Run the B1 spike first and let it rewrite S5's promise.** The most important thing this
   review found is that the multi-instance criterion, as written, rests on channels the pipeline
   doesn't build. Resolve that before `/_my_plan`, not during implementation.
2. **Correct the "never collapses" note and add the collapse-vs-miss analysis** from the probe
   recipe to the design's Risks and Implementation Notes.
3. **Add the blocked-owner fixture** and **pin the predicate-IR carriage decision.**
4. **Take the D1 `[HARD]` reinterpretation to the owner** — it's a capture-fidelity surfacing
   obligation, not a call the design should make silently.

---

## Resolutions

_To be filled in as the owner resolves findings. Keyed by ID; this is what the design agent reads
to incorporate the review. The reviewer records resolutions here and does not edit `design.md`._

---

**Overall:** Approved-with-must-fixes.
**Next Steps:** Record resolutions above, then return to the design-agent session (re-run
`/_my_design`) pointed at this review to incorporate. Run the R1/B1 spike before `/_my_plan`;
its result governs Must-fix 1. The reviewer does not edit the design.
