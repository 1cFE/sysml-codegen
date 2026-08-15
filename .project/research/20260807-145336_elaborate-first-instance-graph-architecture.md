---
date: 2026-08-07T14:53:36-07:00
researcher: Claude (fresh-perspective review, owner-requested)
topic: "The simpler design: elaborate the model first, project second"
tags: [research, source-identity, architecture, simplification, instance-graph, elaboration]
status: complete
last_updated: 2026-08-07
branch: source-identity-epic
base_commit: 224bfa6
---

# The simpler design: elaborate first, project second

## Research question

**[OWNER]** (2026-08-07): the codebase feels like compounding bad decisions — "we are solving the
wrong fucking problem." Item 4's approved fix added a 742-line shadow identity subsystem the
resolver ignores by design. The owner's premises, stated directly in review:

1. **[OWNER]** `in R = R` is a modeling bug. We should not work around bad modeling.
2. **[OWNER]** When we load the models, the resolved referents are available. The AST has
   uniqueness built in.
3. **[OWNER]** Snapshots are just a serialization-format choice, not an architectural constraint.

Question: taking those premises seriously, what is the simpler architecture — not the smallest
next diff, but the design under which source identity stops being a problem at all?

This report is an **[AGENT]** assessment. It complements, and in one respect disagrees with,
`.project/research/20260807-143615_source-identity-recovery-assessment.md` (the Codex recovery
report). All evidence below was gathered fresh from the current tree by four scoped
investigations (seam check, machinery inventory, hard-shape pressure test, SysIDE capability
survey); file:line citations are theirs.

## Executive conclusion

The library never performs SysML **elaboration** — expanding definitions and usages into a tree
of concrete occurrences, applying `:>>` redefinitions innermost-wins, and resolving every
binding's referent to a node in that tree. Instead it flattens declarations to name strings at
extraction and then simulates elaboration after the fact, in at least five accreted layers
(~3,400 lines of production code) that guess identity back out of strings. Source identity is
not a missing feature of this architecture; it is the hole in the middle of it.

The simpler design:

```
SysIDE AST (referents resolved, redefinition edges known; license required)
        │
        ▼
ELABORATOR — one pass, at load/capture time
  expand part usages → occurrence tree, stable node IDs (occurrence paths)
  apply :>> redefinitions innermost-wins → each attribute node holds ONE effective value/expr
  resolve every binding referent → a node ID, while the AST is in hand
  self-binding / unsupported form → hard diagnostic, right here
        │
        ▼
INSTANCE GRAPH — the single IR and the snapshot format
  nodes: part / attribute / calc / constraint occurrences
  edges: "input X of calc node C is bound to node N"
        │
        ▼
PROJECTION — mechanical, license-free
  calc node → PipelineModule;  edge to calc-output node → channel wiring
  externally suppliable attribute node → ONE public input (the node IS the identity)
        │
        ▼
ComputationGraph → existing generation layer, unchanged
```

Under this design the epic's mission invariant — one modeled source, one runtime source — holds
**by construction**: three consumers hold three edges to the same node, so they share one input.
There is nothing to preserve, reconstruct, manifest, or audit, because identity is never encoded
as a string that a later stage could mangle.

**Recommendation:** stop extending the string architecture (both the Item-4 shadow layer and
the recovery report's thread-a-ref-through-the-existing-resolver variant). Redesign the front
end of the pipeline as elaborate-then-project, landing on the existing `ComputationGraph` seam,
proven by dual-running both front ends over the 37-fixture corpus before cutover.

## Diagnosis: five simulations of the missing step

Every mechanism below re-derives, from flattened names, a fact the elaborator would compute
once. Line counts are physical lines in the current tree (inventory investigation, 2026-08-07).

| # | Mechanism | Where | ~Lines | What it simulates |
|---|---|---|---:|---|
| 1 | Virtual calc-usage expansion | `extraction/usage_extractor.py:248-626` | 378 | occurrence multiplication — clones template calcs per instantiation path, minting string QNs |
| 2 | Virtual-binding rewrite + rescue | `orchestration/pipeline_builder.py:204-645` | 442 | redefinition application — mutates binding strings in place; the literal stamp clears `source_path` (the identity-loss site) |
| 3 | Aggregation scope re-derivation | `orchestration/pipeline_builder.py:646-877` | 232 | occurrence discovery — scans virtual QNs, splits on `__`, re-dots |
| 4 | Backtracker resolution ladder | `analysis/dependency_backtracker.py:394-632` | ~300 | reference resolution — hands strings to the key table, interprets misses |
| 5 | Producer key-form table | `resolution/producer_resolution.py` (21 forms + scope-climb) | 713 | reference resolution — "is this name findable under some spelling?"; 6 rows are name-based guessers, 4 rows take zero corpus hits |
| 6 | Supplied-value materializer | `resolution/supplied_values.py` | 715 | effective-value computation — synthesizes fake design attributes from unread redefinitions |
| 7 | OutputRegistry (4 key namespaces) | `core/output_registry.py` + `orchestration/output_registry_builder.py` | 662 | node identity — string-keyed lookup surface for #5 |
| 8 | Group-deriver value backfill | `resolution/graph_builder.py:618-632` | 15 | patches values the other layers dropped ("ParameterSource may have resolved bindings that EntryPoint classification missed") |

Aggregate: **≈3,450 lines whose only job is to reconstruct occurrence identity and effective
values from strings.** The genuinely necessary pieces inside these subsystems are small: the
toposort (~97 lines, `dependency_backtracker.py:650-746`) and the hierarchy resolver's AST fact
extraction (~600 lines, `extraction/hierarchy_resolver.py` — real redefinition/override/
multiplicity/aggregation facts read off the parse tree; it keeps its job as elaborator input).

The Item-4 shadow layer (`analysis/source_identity.py` 742 lines, plus ~520 lines of related
additions) is a **sixth** layer: a manifest/authority/recorder that describes semantic truth
alongside the strings while the resolver ignores it by design. Its audit verdict is `Needs
Work`, and the dirty tree is currently broken cross-repo (`feature_chain_facts` returns 5
values; `agentic_mbse/sysml/aggregation.py:249,405` still unpack 4 — licensed aggregation
extraction raises `ValueError`).

The pattern across all six layers is the same: each exists because the previous one lost
information. The customer fan-out defect (75 of 277 public entry points are per-consumer mints)
is not a bug in any one layer — it is the composition working as built.

## Evidence the simpler design is real, not a fantasy

### 1. SysIDE already supplies every elaboration input

Proven on the live AST (capability survey; Items 1–2 spike evidence):

- **Resolved referents per authored form** — bare → the calc's own formal (the shadowing trap),
  `'Plant'::R` → def-level attribute, `plant.R` → the occurrence-level redefining feature.
  Captured today in `ResolvedTargetFact` (`agentic-mbse sysml/data_models.py:54-69`) and
  `SourceReferenceEvidence` (`extraction/source_evidence.py:61-116`), with exact-QN
  self-binding detection (never name-match).
- **Redefinition edges** — `owned_redefinitions[].redefined_feature` links an occurrence
  override to the definition feature it redefines (binding-semantics findings, redefinition
  micro-probe; consumed exactly in `PartInstanceIndex.redefining_target_on`,
  `analysis/part_instance_index.py:432-462`).
- **Occurrence expansion** — `PartInstanceIndex` already walks nested containment, expands
  fixed multiplicity into indexed occurrences (`Root__bank__member[0]`), closes over subtypes,
  and fails loud on non-finite multiplicity and containment cycles
  (`part_instance_index.py:102-166, 190-246, 321-513`).
- **Feature-chain structure** — `feature_chain_facts` returns root, leaf, resolved segment QNs,
  member-name path, and index presence (`agentic-mbse sysml/expression.py:670-747`).

### 2. The elaborator's core already exists in-repo, and one route already uses it

`PartInstanceIndex` (576 lines) *is* the occurrence enumerator. Constraint lowering already
expands `part_def` owners via `OccurrenceIndex.occurrences_of()` and resolves each formal
per-instance (`analysis/constraint_lowering.py:84,109`). The constraint route is the working
proof-of-concept: elaboration-shaped resolution is not speculative in this codebase.

### 3. The landing seam is clean

Generation reads **only** the populated `ComputationGraph` (seam investigation): every driver
access in `cli/__init__.py` goes through `ctx.computation_graph`; no generation function reads
`BacktrackingResult`, extraction data, classifier state, or registry state. The documented
contract agrees ("the ComputationGraph is the only thing the generation layer should see",
`docs/architecture/reference/07-graph-assembly.md:340`).

Caveats a replacement front end must honor — the seam is the **in-memory** graph, not just the
serialized fields:

- `output_aliases` (serialized) drives exit-point capture names.
- `fallback_entry_points` (`exclude=True`) feeds the V11 coverage check
  (`cli/__init__.py:279`). Under the new design this field should be empty or deleted — there
  is no fallback minting — but the boundary check survives as an invariant.
- `constraint_catalog` (`exclude=True`) is assembled separately and attached
  (`orchestration/pipeline_builder.py:1213-1224`); the projection must produce it.
- Name minting conventions stay: `get_module_name` / `get_channel_name` /
  `derive_module_type` (`core/qualified_names.py`, `core/identifier_types.py`) are pure string
  helpers the projection calls. Public naming (ADR-003) is unchanged by this design — names
  become *rendered from* node identity instead of *being* identity.

### 4. The seven hardest shapes, pressure-tested

| Shape | Current mechanism | Under the elaborator | Verdict |
|---|---|---|---|
| Aggregation scoping | scans virtual QNs, `__`↔dot surgery, per-instance alias minting (doc 13) | fold over `occurrences_of(child_def)` under the parent node; per-child `:>>` via `redefining_target_on` | natural, strictly better |
| Constraint route / dual resolution | one `resolve_producer` called at two times; backtracker must resolve during DFS to decide recurse-vs-stop | recurse-vs-stop becomes "does the referent node have a producer edge?" — read off the graph | natural; one graph subsumes both |
| Cross-package EXPOSE | alias registry exists solely because scope-string prepending cannot cross packages; multi-hop needs a tentative-tag + confirm walk | an EXPOSE is an edge to a node ID; packages are irrelevant once referents are IDs | natural; deletes the alias registry's reason to exist |
| Sibling channel ambiguity | structured `_scoped_alias` tuple namespace + Step 1c ordering (REQ-BT-11) | `chamber_a`/`chamber_b` are distinct nodes; no shared key to collide | natural; problem vanishes |
| Multiplicity `[3]` | legacy string minting from virtual QNs; new `PartInstanceIndex` does it properly | already built (`classify_cardinality`, indexed occurrences, fail-loud on non-finite) | natural; already built |
| **Nested occurrence override (C19, the 80.0 fixture)** | **BROKEN** — definition-relative capture vs occurrence-relative demand cannot meet in the string tiers (`[NESTED-OCCURRENCE-OVERRIDE]` tripwire, `supplied_values.py:623`) | overrides applied during elaboration; both consumers read the node that holds 80.0 | the string model's impossible case is the instance graph's trivial case |
| Computed attributes / FORMULA | the one path that bypasses `resolve_producer` via a separate pre-computed `attr_resolution_map`; FORMULA→FORMULA unsupported | a FORMULA attribute is a calc node with input edges to sibling nodes; the separate map folds into the one model, and FORMULA→FORMULA lifts naturally | natural; subsumes the special case |

Six of seven are natural; the seventh is the defect that motivated the epic, unfixable by
string surgery and structural under elaboration. Nothing on the list is genuinely hard for an
instance-graph model. The one real hazard — non-finite multiplicity — already has the correct
disposition (expand-finite or block-loud; no third option).

### 5. Snapshots map cleanly

The only license-gated operation is invoking the SysIDE parser (`syside_adapter.py:237-253`).
Elaboration is AST-touching, so it lives in the licensed capture half; the serialized instance
graph is the snapshot payload; everything downstream is deserialization plus projection. This
**dissolves** the Item-2 pathology (capture persists the post-VBR stamp; rebuild has no VBR):
there is no rewrite step to replay, so live/snapshot divergence of that kind becomes
unrepresentable. The cost is the already-known one: a snapshot format bump, fail-closed old
versions, and one full 37-fixture recapture — paid **once, after** the representation is proven
live, per the sequencing lesson.

## What this resolves by construction

- One modeled source → one public input or one producer channel (the epic's mission invariant).
- `in R = R` → hard diagnostic at elaboration, per the owner ruling. No rescue, no
  reinterpretation. Zero ongoing code cost.
- `'Plant'::R` vs `plant.R` → both land on the correct node: a def-level referent is
  contextualized to the consumer's enclosing occurrence during elaboration; the chain referent
  is already occurrence-level. The Item-3 dual-form disposition is honored with one rule in one
  place.
- Equal-valued independent literals stay distinct (different nodes); same-source references
  with different consumer spellings converge (same node). Spelling can never change identity.
- C19 / nested occurrence override: fixed structurally, not bridged.
- Live/relocated-snapshot parity: same graph, by construction.

## Honest costs and risks

- **This is a front-end rewrite.** Extraction stays (as elaborator input), generation stays;
  extraction-to-graph is redesigned. Plausibly comparable effort to the *remaining* Items 4–6
  budget on the current path — but it replaces ~3,450 lines instead of adding a sixth layer,
  and the current path's effort buys coexistence with the string machinery, not its removal.
- **Corpus semantics shift on purpose.** The 75 per-consumer mints collapse; every diff needs
  the semantic review Item 6 already prescribes. Dual-running old and new front ends over the
  37 fixtures and diffing ComputationGraphs produces that ledger mechanically.
- **Known evidence gaps** (capability survey): no shadowing/specialization *referent* fixtures
  exist yet; the multi-occurrence definition-default question (one shared source vs
  one-per-occurrence) is an open Item-3-grade ruling the elaborator forces explicitly —
  surfaced here rather than resolved silently; `REFERENCE_FORM_UNKNOWN` means the authored
  spelling is diagnostic-only, which is fine precisely because spelling is not identity here.
- **Expression compilation seam.** Expression IR/compilation stays in `agentic-mbse`; the
  elaborator holds nodes and resolved input edges, projection emits compiled bodies. A seam to
  preserve, not a difficulty.
- **The dirty tree is broken right now** (the 5-tuple/4-tuple arity mismatch above) and must be
  preserved as a forensic checkpoint, not treated as a green salvage base.

## Relationship to the current work and the recovery report

**Salvage into the elaborator** (the Item-4 money was not wasted; it bought the elaborator's
inputs): exact referent/redefinition evidence capture (`ResolvedTargetFact`,
`SourceReferenceEvidence`, the extraction-side additions), the `PartInstanceIndex` extensions,
the semantic fixtures and red tests (mixed consumers, ambiguity, indexed-source, C24/C25, the
fan-out pins) as falsifiers for the new front end, and the audit reproductions.

**Do not carry forward:** the manifest, the four coordinate types, the query recorder, the
wrapper index protocol, `SourceIdentityAuthority` — all joins between two string
representations, with no place in a design that has one representation. Snapshot v6 as
specified (persisting the shadow layer) is superseded by "the snapshot is the instance graph."

**Where this differs from the Codex recovery report:** its recovery architecture threads a
`SemanticSourceRef` through the existing `ProducerRequest` into the existing resolver and
registry. That is better than Item 4 — the identity would at least be load-bearing — but it
retains the ladder, the registry namespaces, VBR-adjacent machinery, and the simulation
pattern itself: identity becomes a rider on the string skeleton rather than the skeleton.
Its own falsifier list (authored spelling must not change identity; consumers must converge
structurally) is what the instance graph gives by construction. If the design boundary is being
reopened anyway — and both reports agree it must be — reopen it to the real question: why does
this library resolve references by string matching at all?

## Proposed path (deliberately small)

1. **Owner decision first.** This report vs. the recovery report's incremental vertical repair
   is an architecture choice with real cost either way; it is the owner's call, not an agent
   ratification.
2. **Concept + design for the elaborator** — sized to the decision it carries, naming the
   types/functions it replaces and deletes. No manifest, no transcript, no second authority.
3. **Prototype on three fixtures**: the customer shape (fan-out collapse), the
   nested-occurrence 80.0 fixture (C19), and fusion_tea's aggregation shape. Success = correct
   ComputationGraph from the instance graph, existing generation untouched.
4. **Dual-run the 37-fixture corpus**, diff ComputationGraphs old-vs-new. The diff *is* the
   semantic-diff ledger; the 75 mints collapsing is the expected signal, anything else is
   review material.
5. **Cut over and delete** — the table in the diagnosis section is the deletion ledger. One
   authority per responsibility; no old+new coexistence across completed items.
6. **Then** snapshot format bump + one atomic recapture + downstream regeneration (existing
   Items 6–8 scope, unchanged in intent).

## Open questions

1. Node ID scheme: `InstanceOccurrence.instance_path` is the obvious stable ID; confirm it
   stays stable under model edits we care about (it is positional for indexed occurrences).
2. The multi-occurrence definition-default ruling (shared vs per-occurrence input) — owner
   decision the elaborator will force explicitly.
3. How much of `ComputationGraph` assembly (parameter grouping, constraint catalog attachment)
   moves into projection vs stays shared with the old front end during the dual-run window.
4. Whether `agentic-mbse` should own the elaborator (it owns the AST adapter and the instance
   walker's inputs) or codegen keeps it — a coordinated-pair decision.

## Primary references

- `.project/research/20260807-143615_source-identity-recovery-assessment.md` — the recovery
  report this one extends and partially disagrees with
- `.project/research/20260803-202453_backtracking-fanout-forensics.md` and
  `20260803-203011_entry-surface-fanout-forensics.md` — the defect forensics
- `.project/active/source-identity-binding-semantics-spike/findings.md` and
  `.project/active/source-identity-route-evidence-spike/findings.md` — the language/route
  evidence this design consumes
- `src/sysml_codegen/analysis/part_instance_index.py` — the existing occurrence enumerator
- `docs/architecture/reference/07-graph-assembly.md`, `11-analysis-backtracker.md`,
  `12-virtual-binding-rewrite.md`, `13-aggregation-scoping.md`,
  `24-dual-resolution-architecture.md` — the current architecture record
