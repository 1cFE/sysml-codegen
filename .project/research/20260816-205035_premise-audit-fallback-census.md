---
date: 2026-08-16T20:50:35-07:00
researcher: Codex
topic: "Premise audit of the SysIDE-authority fallback census"
tags: [research, architecture, syside-authority, occurrence-semantics, premise-audit]
status: complete
baseline: "HEAD 26e19f9 plus the 2026-08-16 dirty working tree"
---

# Premise audit: SysIDE authority and the fallback census

## Question

`[OWNER]` The intended pipeline is: use a SysML v2 parser to interpret the model, walk the
resulting semantic structure to recover the math, and emit Python through TEAx. The question is
whether the current project has abandoned that premise and rebuilt model meaning through local
rules, and whether
`.project/research/20260816-201934_syside-authority-fallback-census.md` supports that conclusion.

## Verdict

The owner's interpretation is directionally right about the failure mode and too broad about its
extent.

The public architecture has **not** reverted wholesale to dictionaries, strings, and a rebuilt
tree. It still follows this shape:

```text
SysIDE semantic declarations
    -> exact declaration/context elaboration
    -> InstanceGraph
    -> mechanical ComputationGraph projection
    -> Python/TEAx
```

The exact graph, snapshot, and projection layers are real. They retain typed declaration,
occurrence, slot, node, and edge identity. The old name-based resolver is not on the public route.
The architecture also has one legitimate job that SysIDE 0.8.4 does not perform: materializing
finite, parent-contextual, multiplicity-indexed occurrences from semantic usage declarations
(`.project/active/spike-syside-occurrence-authority/findings.md:5-20`).

The premise breach is narrower and still serious. At the boundary between an exact SysIDE feature
declaration and a concrete codegen occurrence, several paths use nearest-ancestor, descendant,
sole-candidate, or first-match election. Those rules can invent an occurrence that the semantic
facts do not identify. The expression adapter also contains fail-open or lossy behavior before the
exact-ID compiler sees the expression.

The cited census found real defects, but it is **not reliable enough to be the design contract**.
Its count, CATF interpretation, and later `::` addendum need major correction.

## What remains faithful to the original premise

1. The elaborate-first design explicitly replaced flattened string reconstruction with a graph
   built from SysIDE declaration IDs and structured occurrence IDs
   (`.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md:34-77`;
   `.project/active/elaborator-design/design.md:180-207`).
2. Occurrence expansion consumes SysIDE's effective declaration view and adds only the concrete
   parent/index context SysIDE does not expose
   (`.project/active/elaborator-design/design.md:191-202`;
   `.project/active/spike-syside-occurrence-authority/findings.md:5-31`).
3. Graph and projection invariants prohibit names, qualified names, rendered paths, and candidate
   ordering from selecting an edge (`.project/active/elaborator-design/design.md:361-380`).
4. Snapshot projection does not rerun semantic resolution. The census itself found no class-A issue
   in CLI, snapshot, contracts, orchestration, or projection wiring
   (`.project/research/20260816-201934_syside-authority-fallback-census.md:61-71`).

This means the year of architecture work did produce a sound structural core. It did not finish
policing every semantic-authority boundary feeding that core.

## What the census got right

- Definition-owned sideways selection can silently invent a concrete occurrence for a reference
  that names only a definition feature. The `'Unit'::cost` case should refuse when no exact
  contextual `Unit` occurrence is supplied by the modeled context.
- The occurrence selectors still contain a generic nearest-anchor descendant search. Returning the
  first anchor with candidates lets proximity decide meaning
  (`src/sysml_codegen/elaboration/elaborate.py:2207-2239`).
- Indexed expression evidence is preserved upstream but can be dropped on the expression path,
  producing a wrong plural result instead of a refusal
  (`.project/research/20260816-201934_syside-authority-fallback-census.md:234-267`).
- The agentic expression layer contains broad exception handling, class-name tests, name-prefix
  standard-library filtering, and a staged resolution ladder. These deserve separate fail-closed
  audits because exact IDs downstream cannot recover an input that extraction omitted.

## Where the census is wrong or overstated

### 1. The headline count is not a coherent count of one failure class

The report calls L-01 through L-14 “14 confirmed live semantic fallbacks,” but several rows are
omission, failure-honesty, or rendering policy rather than invented parser meaning:

- L-05 drops a redefinition edge.
- L-08 drops a subtree after an iteration error.
- L-12 warns and omits a wrapper.
- L-13 chooses an output filename while retaining both aliases in the graph.
- L-14 is the documented parameter-file grouping policy.

Only four rows received runtime probes; other rows are static risks, and L-07 is explicitly masked.
L-02 also groups three implementation sites into one item while L-01 separately counts behavior at
one of the same sites. The report must distinguish **observable defect**, **static risk**,
**omission**, **rendering policy**, and **root mechanism** before publishing a total.

### 2. The CATF evidence is factually misdescribed

The report says CATF radial-build layers read adjacent layers, including
`plasma_region::inner_radius` from inside `vacuum_gap` and `first_wall::inner_radius` from inside
`blanket` (`...fallback-census.md:292-300`). The source says otherwise:

- `plasma_region::inner_radius` is inside `plasma_region`'s own calculation
  (`tests/fixtures/catf_mfe_model/designs/catf_mfe/radial_build.sysml:76-100`).
- `vacuum_gap` reads `vacuum_gap::inner_radius` (`radial_build.sysml:113-136`).
- `first_wall` reads itself (`radial_build.sysml:149-173`).
- `blanket` reads itself (`radial_build.sysml:186-217`).

The retained exact-edge evidence also records the owner of `plasma_region::inner_radius` as the
exact `PartUsage` declaration for `plasma_region`, and the selected target is in that same occurrence
scope
(`.project/completed/20260816_qualified-reference-occurrence-anchoring/verification/after.json:3043-3058`).
The same is true for `first_wall` (`after.json:2611-2626`).

A fresh instrumentation pass over the maintained CATF radial build observed 73 occurrence-selector
calls: 68 direct-lineage selections, five depth-zero downward selections, and **zero** outer-anchor
sideways selections. CATF therefore does not prove the report's usage-owned sideways mechanism.

### 3. The addendum conflates a discarded lexical path with a discarded semantic referent

The report's addendum correctly says that `a::b` is parsed as a
`FeatureReferenceExpression`, while `a.b` is a path-bearing `FeatureChainExpression`. KerML also
says the qualified name text does not remain in the abstract syntax and contrasts static
`axle::halfAxles` with contextual `axle.halfAxles`
(`/home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_KerMLSpec/full_document.md:1160-1164,2068-2073`).

The addendum then makes an unsupported jump: it says there is no parser-level usage-owned lane and
that every `::` value reference must be refused
(`...fallback-census.md:741-748,762-766,804-823`). That does not follow.

The lexical qualification path disappears, but the abstract syntax retains an exact reference to
the resolved Feature. SysIDE can resolve that referent to a usage-owned redefinition whose exact
owner is a `PartUsage`, or to a definition-owned feature whose owner is a `PartDefinition`. The
companion fact model was built to preserve exactly that distinction
(`/home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/data_models.py:55-89`). Live parser inspection
confirmed:

- `comp_a::length` -> exact leaf owned by `PartUsage comp_a`;
- the maintained CATF `plasma_region::inner_radius` -> exact leaf owned by
  `PartUsage plasma_region`;
- `'Unit'::cost` -> leaf owned by `PartDefinition Unit`.

That difference comes from SysIDE's resolved declaration identity. Codegen did not infer it from
the spelling. A `FeatureReferenceExpression` also binds its result to that exact referent Feature
(KerML `full_document.md:6363-6396,8164-8177`). Therefore, “no textual path” does not mean “no
semantic occurrence authority” in every case.

The addendum's displayed `plasma_region::inner_radius -> Plasma::inner_radius` probe is not the
maintained CATF fact shape. It was generalized to CATF despite the retained CATF evidence showing a
`PartUsage` owner. That invalidates the blanket conclusion and the draft spec built on it.

### 4. The corpus measurement cannot presently carry its claimed weight

The report's reproduction command contains a placeholder plugin path, and its proving probes remain
only in a session scratchpad (`...fallback-census.md:841-860`). The 236 records are executions, not
236 unique semantic sites, and the report's own table divides them into 123 depth-zero and 113
depth-greater-than-zero records (`...fallback-census.md:311-340`). The interpretation of every
depth-greater-than-zero call as “sideways” is contradicted by the CATF source and fresh
instrumentation.

The measurement may help locate calls. It cannot currently prove the semantic classification or
blast radius.

### 5. The report is a baseline audit, not current-state truth

It targets commit `26e19f9`. The dirty worktree has already changed the qualified definition-owned
lineage-miss behavior and its tests. Focused validation of the current worktree passed 52 tests:

```text
tests/conformance/test_usage_owned_reference_anchoring.py
tests/conformance/test_definition_owned_reference_positions.py
52 passed in 0.39s
```

Those tests show internal contract consistency. They do not independently prove the language
semantics, which is why the parser/standard distinction above still matters.

## Answer to the quoted “delete or fix?” question

The question should not have been presented as an owner preference. The two cases have different
semantic facts, and the implementation should follow those facts.

### `'Unit'::cost`

Refuse it when the exact modeled context does not identify a `Unit` occurrence. SysIDE supplied an
exact definition-owned feature declaration, not an occurrence. Searching descendants and accepting
the nearest or only `Unit` occurrence adds meaning the model did not supply.

### `plasma_region::inner_radius` or `comp_a::length`

Do **not** blanket-delete this lane. When SysIDE's exact referent is owned by an exact `PartUsage`,
that owner declaration is semantic authority. Codegen must still instantiate it because SysIDE does
not emit concrete `OccurrenceId`s. The valid operation is:

```text
exact referent Feature
  + exact owning PartUsage declaration
  + exact consumer/domain occurrence context
  + modeled containment and multiplicity
  -> exact concrete occurrence, or named refusal
```

This is elaboration, not parser reinvention. P-002 records the same promise and the reason for it
(`.project/product/P-002-exact-owner-anchoring.md:9-29`).

The current generic selector is still too permissive. If two concrete copies exist, “take the
nearest” is not a valid rule. The resolver must derive the target occurrence from the target usage's
static owning/featuring context and the consumer's concrete domain occurrence:

- Copies under different outer occurrences are disambiguated by the consumer's matching domain.
- Multiple indexed copies under one exact context require authored plural/index semantics or a
  named ambiguity refusal.
- A target with no valid contextual relationship to the consumer is missing/uncontextualizable,
  not a candidate for global or nearest search.

The report's `'Holder'::the_unit::cost` probe demonstrates that nearest-anchor election is wrong. It
does not prove that all exact usage-owned contextualization is wrong.

## Consequences for the active work

1. Do not use the fallback census or its addendum as an approved implementation plan without major
   revision.
2. Do not approve `.project/active/stop-reinventing-the-parser/spec.md` as written. Its central
   claim that the maintained CATF `plasma_region::inner_radius` resolves to a `Plasma` definition is
   contradicted by the retained parser/edge evidence.
3. Keep the InstanceGraph and exact-ID occurrence walker. Removing them would discard the concrete
   context SysIDE 0.8.4 does not provide.
4. Replace nearest/sole-candidate occurrence election with a derived contextual mapping from exact
   declaration ownership, modeled containment, multiplicity/index, and consumer domain. Refuse when
   that mapping is not singular for a scalar reference.
5. Split the remaining census into separate proof obligations:
   - wrong semantic answer;
   - silently lost parser evidence;
   - fail-open adapter behavior;
   - downstream rendering/product policy.
6. Retain the real red-alert finding: a green suite does not prove the generated math is faithful
   while unsupported expression shapes can lose indices or dependencies before the graph boundary.

## Final assessment

The project is not “nothing works and nobody can tell.” Its identity-carrying core is materially
better than the old architecture and is aligned with the original parser-first premise.

The project is also not done fixing the premise breach. The remaining breach sits at a small number
of semantic conversion boundaries where code turns exact declarations into occurrences or turns
AST expressions into dependency facts. Those boundaries need a deletion-first, parser-evidence
audit. The cited report is useful as a list of suspects, but its headline story and proposed
usage-owned disposition are not trustworthy enough to steer the repair.
