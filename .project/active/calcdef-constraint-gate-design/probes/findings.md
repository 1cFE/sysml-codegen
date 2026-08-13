# Spike: Calculation-definition constraint attachment

**Date:** 2026-08-13
**Branch:** `item7-rebuild`
**Commit inspected:** `488747b`
**Upstream:** `.project/backlog/epic_constraint_semantics_contract.md`, Item 6

## Summary of Findings

**Verdict: confirmed at the exact elaboration seam, with one required occurrence-identity
extension.** The landed identities are enough to select zero, one, or many concrete calculation
occurrences without rendered-name lookup: compare the asserted constraint's live semantic-owner
`DeclarationId` with each `CalcNode.calculation_definition_id`. The probe returned `0`, `1`, and
`2` matches. All three variants kept the same owner definition ID and constraint usage ID.

For each match, the landed calculation node also carries enough information to recover explicit
actuals and modeled defaults by exact formal identity while elaboration's canonical feature-slot
index is in scope. The probe recovered:

- a design attribute as a resolved `NodeRef`;
- an authored usage literal as `LiteralInput(7.0)`;
- the modeled definition default `3.0` from the unbound formal's `PortMetadata`.

The v3 codec preserved the calculation node IDs and resolved input edges field for field.

**Repeated use exposes a real representation gap, not a need for a second authority.** Two sibling
calculation usages of the same definition share one part scope. Their full `CalcNode.node_id`
values are distinct, but today's candidate `ConstraintNode` identity
`(scope, constraint_usage_id)` is identical for both. One asserted check cannot therefore be
represented once per calculation occurrence with the current constraint `NodeId` shape. The
smallest exact attachment identity supported by the evidence is:

```text
(constraint usage DeclarationId, concrete CalcNode.node_id)
```

The graph schema must carry that calculation-occurrence component. The exact node already exists;
this does not require a new occurrence inventory.

**Attachment must happen inside elaboration, before serialization.** The serialized
`ConstraintUsageRecord` does not carry its calc-definition owner's `DeclarationId`, and an explicit
calculation input port does not carry its root definition-formal identity. Recovering either after
build would require rendered qualified-name matching or a parallel lookup. The live exact
elaborator already has both facts: `declaration_id_for(_semantic_owner(usage))` and the canonical
feature-slot index. The supported design direction is therefore to expand and bind calc-def gates
there, place the resulting concrete constraint occurrences in the same `InstanceGraph`, then
serialize them. Post-build fill is ruled out by the evidence.

No premise conflict requires a second constraint or occurrence authority. There is a narrower
premise correction for Item 6: the landed `ConstraintNode` identity is not sufficient unchanged,
and the landed serialized graph is not a lawful place to reconstruct attachment. Dependent design
work should use the elaboration-time rule below and must not assume scope alone identifies a
calculation occurrence.

## Question / Goal

Test this assumption: one asserted constraint owned by a `CalculationDefinition` can expand to
zero, one, or many concrete calculation occurrences using the exact identities and formal actuals
already owned by the exact elaborator. Confirmation requires repeated uses of one definition to
stay distinct, explicit actuals and modeled defaults to recover by exact identity, and no lookup by
rendered name, post-build repair, or parallel occurrence/constraint inventory.

The probe serves CONSTRAINT-SEMANTICS Item 6. The owner-ratified semantic rule is one asserted
check per concrete calculation occurrence
(`.project/active/constraint-semantics-contract/rulings-20260812.md`, Q2). Coverage remains one
authored usage while results are concrete occurrences (Q5).

## Log

### 2026-08-13 — source and landed-representation inspection

Read the required Item 6 sources before probing. The landed representation differs from Item 2's
design sketch in the details that matter here:

- `CalcNode` carries both the calculation-usage declaration identity and the exact
  `calculation_definition_id`; its `node_id` composes scope plus usage identity
  (`src/sysml_codegen/elaboration/graph.py`).
- Calculation inputs are already resolved to typed `InputRef` values in `CalcNode.inputs`, while
  modeled defaults live on the corresponding `PortMetadata` and in `unbound_formals`
  (`src/sysml_codegen/elaboration/elaborate.py`).
- The exact feature-slot index maps a usage-level redefining input declaration back to its
  calculation-definition formal during elaboration. That root identity is not serialized on
  explicit calculation input ports (`src/sysml_codegen/elaboration/occurrence.py`,
  `src/sysml_codegen/snapshot/instance_graph.py`).
- `ConstraintUsageRecord` carries the usage declaration identity, owner kind, and owner rendered
  qualified name, but not the owner's exact declaration identity
  (`src/sysml_codegen/elaboration/graph.py`).
- A current constraint occurrence uses `NodeId(CONSTRAINT, scope, constraint_usage_id)`. That shape
  has no calculation-occurrence component (`src/sysml_codegen/elaboration/identity.py`,
  `src/sysml_codegen/elaboration/elaborate.py`).

These observations set two falsifiers for the executable probe: exact definition matching may be
impossible, or two uses of one definition in one scope may mint the same constraint node identity.

### 2026-08-13 — executable attempts

Command for each attempt:

```bash
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python \
  .project/active/calcdef-constraint-gate-design/probes/probe_calcdef_attachment.py
```

1. The first scratch model used `first` as a calculation usage name. SysIDE rejected it as a
   reserved token at `probes/models/one/model.sysml:17`. Renaming the scratch usages to
   `sizing_a` / `sizing_b` fixed the probe input. This was not a product observation.
2. The second scratch model tried to bind `5.0` over a calc-definition input that already carried a
   modeled default. SysIDE rejected the authored shape as `feature-value-overriding`. The probe did
   not need that unsupported shape: `sizing_b.explicit_load = 7.0` exercises a resolved usage
   literal, while both occurrences exercise the modeled `default_factor = 3.0` path. The final
   inputs stay within supported authored syntax.
3. The corrected probe exited zero and printed `"probe_status": "PASS"`.

### 2026-08-13 — executable observations

All lookup decisions in the script use `DeclarationId`, `FeatureSlotId.root_declaration`,
`CalcNode.calculation_definition_id`, `CalcNode.node_id`, or `ConsumerPortId.formal`. Rendered
names are emitted only to make the JSON readable.

| scenario | exact calc matches | recovered inputs | candidate exact IDs | current constraint IDs |
|---|---:|---|---:|---:|
| `zero` | 0 | none | 0 | 0 |
| `one` | 1 | design `NodeRef`; modeled default `3.0` | 1 | 1 |
| `multiple` | 2 | design `NodeRef`; usage literal `7.0`; default `3.0` on both | 2 | **1** |

The exact identities stayed stable across the three independently loaded variants:

- asserted constraint usage: `9336d800-536b-558f-b3a9-991b75d6399e`;
- owning calculation definition: `f8ca2f59-2d8f-5ef4-8022-c04a12c2c2ca`;
- definition formal `explicit_load`: `74d7b410-ddb4-51a4-9585-2ff9af15bda7`;
- definition formal `default_factor`: `06aa3d0e-1232-5733-91bd-c2dbd7ae1ea1`.

In `multiple`, the two exact calculation usage IDs were
`617a94b8-5610-5e80-9ea0-3943774bc07b` and
`75b803e6-3bc9-50d9-bcc3-3fc8d8fdd84d`. Their `CalcNode.node_id` values differ by those
declaration IDs. Both live under the same `rig` occurrence, so replacing each node ID with today's
constraint shape produced the same wire identity. The script asserts both sides: two composite
attachment keys and one current constraint key.

For explicit inputs, the occurrence-level binding declarations were not the definition formal:

- `sizing_a.explicit_load`: `2d9a5c24-55fd-5bbf-8848-1142a7d9feba`;
- `sizing_b.explicit_load`: `3f62fa5b-9c6d-5ca3-a4f3-3cd3a85b9d52`.

The live feature-slot authority mapped both to the exact root formal
`74d7b410-ddb4-51a4-9585-2ff9af15bda7`. Neither calculation port's serialized
`PortMetadata.formal_provenance` carried that root identity. This confirms why exact formal
recovery works during elaboration and why the same work cannot be deferred until after decode.

The current usage-tier disposition was, as expected before capability, `non_reaching /
owner_kind_unattachable / error` in all three scenarios. That is the present Item 2 behavior, not
the proposed capability result.

### Attachment rule supported by the evidence

The following is **[AGENT — executable spike evidence, 2026-08-13]**. Q2's one-check-per-occurrence
semantics and Q3's severity-by-cause remain **[INHERITED: rulings-20260812.md]**.

1. At the existing constraint-usage loop, get the constraint usage's semantic owner and require a
   `CalculationDefinition`. Convert it once to `owner_definition_id: DeclarationId`.
2. Select concrete calculations only where
   `calc.calculation_definition_id == owner_definition_id`. Do not compare
   `calc_def_qualified_name` or any rendered path.
3. If the exact set is empty, emit no concrete constraint occurrence. The owner kind now has an
   attachment capability, so this is vacuity (`owner_has_no_occurrences`), not structural
   unattachability. **[INHERITED: Q3]** An asserted usage is warning-grade and visible; Q5/L2-2
   keeps it in missing assessment until explicitly dispositioned inapplicable.
4. Otherwise, emit one concrete constraint occurrence per matched `CalcNode`. Its stable identity
   includes both the authored constraint usage `DeclarationId` and the full `CalcNode.node_id`.
   Scope alone is insufficient.
5. Resolve each calc-definition formal through the canonical feature-slot root. For that matched
   calc occurrence, require exactly one input port whose root is the formal. Reuse its resolved
   `InputRef`; if the formal is unbound, use the same modeled default metadata. A missing or
   duplicate exact match is a named diagnostic, never a name fallback.
6. Build and validate these nodes in the same `InstanceGraph` authority before snapshot encoding.
   Projection renders them; it does not rediscover or repair attachment.

This rule preserves Item 2's two tiers: one `ConstraintUsageRecord` for inventory and coverage,
zero-to-many concrete constraint occurrences for results, joined by the existing constraint usage
`DeclarationId`. The calculation-occurrence component provides the drill-down identity Q5 needs.

### Exact code and data paths inspected

- Calculation and constraint graph shapes:
  `src/sysml_codegen/elaboration/graph.py:117`, `:159`, `:201`, `:335`.
- Exact ID vocabulary and current `NodeId` composition:
  `src/sysml_codegen/elaboration/identity.py:87`, `:149`, `:198`.
- Calculation-definition matching data and current constraint construction:
  `src/sysml_codegen/elaboration/elaborate.py:603`, `:1034`, `:1105`, `:1119`, `:1132`.
- Exact formal/root mapping, defaults, and input resolution:
  `src/sysml_codegen/elaboration/elaborate.py:1664`, `:1759`, `:1803`, `:1823`, `:2473`.
- v3 calculation/usage carriage and codec round trip:
  `src/sysml_codegen/snapshot/instance_graph.py:523`, `:568`, `:706`, `:1014`, `:1031`.
- Probe script and authored cases:
  `.project/active/calcdef-constraint-gate-design/probes/probe_calcdef_attachment.py` and
  `probes/models/{zero,one,multiple}/model.sysml`.

## Reproduction

Run from the repository root with the task venv and SysIDE license loaded:

```bash
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python \
  .project/active/calcdef-constraint-gate-design/probes/probe_calcdef_attachment.py
```

Expected: the script exits zero, prints one JSON document, and ends with
`"probe_status": "PASS"`. The document contains scenario counts `0`, `1`, and `2`; exact formal
actual observations for `node_ref`, `literal`, and `modeled_default`; and the repeated-use identity
collision observation.

## Open Questions / Follow-ups

- **Occurrence schema choice.** The evidence fixes the information content: concrete constraint
  identity must include the full calculation node identity. It does not choose whether production
  extends `NodeId`, adds a typed constraint-occurrence owner field, or introduces another
  graph-native composite type. Design owns that choice. It may not create a parallel inventory.
- **Construction ordering.** Resolved `CalcNode.inputs` exist by the end of binding resolution,
  while constraints are currently populated before that pass. Design must place expansion and
  binding so the same canonical resolution feeds both consumers without a post-build repair pass.
- **Defaultless formals.** The probe confirms a modeled default. It does not settle how a
  defaultless `LIBRARY_DEFAULT` public entry point is shared between the calculation and its gate;
  the mission invariant requires one semantic source occurrence, not two independently minted
  entry points.
- **Predicate breadth.** The probe uses one admitted inline asserted predicate over local calc
  formals. Definition-typed assertions, `assert not`, calc outputs, and profile-BLOCK behavior still
  need design/acceptance coverage, but they do not change the attachment identity result.
- **Snapshot proof after implementation.** The existing v3 codec preserved the inputs needed by
  the probe. The new concrete attachment representation will itself change the graph schema and
  needs a live/in-place/relocated snapshot parity test after it exists.
