# Design: Lifecycle Item 4 — Diagnostic Severity and Modeled-Default Fidelity

**Status:** Draft — ready for independent `/_my_design_review`
**Owner:** Reid W
**Created:** 2026-07-19
**Branch:** `constraint-exec-epic`
**Commit at authoring:** `98f00c1`
**Spec:** `.project/active/constraint-lifecycle-diagnostics-defaults/spec.md`
**Stage brief:** `.project/active/constraint-lifecycle-diagnostics-defaults/briefs/design.md`

## Overview

Give extraction diagnostics a severity and a closed code that travel with the data, make warning
rendering incapable of swallowing the BLOCK halt, make signed and unit-annotated modeled defaults
survive to the generated JSON, and land the written-reference carry that closes SR-A02 — accepting
and pinning its measured six-fixture blast radius.

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` — register row 4
- **Ratified authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — invariants 14, 15, 21, 26
- **Requirements authority:** `.project/active/constraint-execution-lifecycle-contract/spec.md` — LC-B06/B08/C04/D09/I09
- **Referral source:** `.project/active/constraint-lifecycle-shared-resolution/{spec,design,evidence}.md` — SR-A02, SR-R23, design I9, PC-2, PC-4
- **Item 3 decision record:** `.project/active/constraint-lifecycle-gate-b/decision.md` (V11 vacuity, `c5cc1b4`)
- **Fixture provenance:** `tests/fixtures/shared_producer/PROVENANCE.md` — two claims falsified, corrected under DD-R31

**Decision-record index.** `.project/adr/` does not exist in this repo. There is no INDEX.md to
check and no prior entry this design could contradict. Item 3's `decision.md` is the nearest
equivalent and is cited above and in D5. If the reviewer expects an ADR directory to exist, that is
a gap to raise, not something this design invents.

---

## DD-B1, settled: severity is a field on the fact, not a reader-side table

The brief says open here, so this is first. **The bet holds.** The reasoning is short and it rests
on one measured asymmetry, not on preference.

**What a reader-side table would actually look like.** Codegen imports `agentic_mbse` directly
(`pyproject.toml:22-27`, with an editable path override at `:64-65`). So a `kind → severity` map
would be *single-sourced by import*, not hand-copied. That is the strong form of the alternative,
and it is the one worth beating.

**Where it breaks: the snapshot route, and only there.** Codegen reads facts two ways.

- **Live** (`orchestration/pipeline_builder.py:764` calls `extract_constraint_facts`): one process,
  one version of the map. Field and map are indistinguishable. No skew is possible.
- **Snapshot** (`snapshot/loader.py:637`, then `constraint_facts.parse` at `:793`): the facts were
  written by agentic-mbse at capture time and read by an imported map at load time. These are two
  different commits by construction — that is what a snapshot is *for*.

Reclassifying a diagnostic family is an anticipated operation, not a hypothetical: the spec's own
DD-B6 says the answer to a noisy advisory family is to reclassify it. Under the map, a
reclassification changes the answer for bytes already on disk, and nothing in the snapshot signals
it. The 34 committed fixtures would silently change blocking behavior on an agentic-mbse commit
that touched no fixture. That is precisely the version skew invariant 14 closes.

**The map can be made strict — and that is what kills it.** The spec's stated challenge condition
is "if design shows the map can be single-sourced and version-gated as strictly as the codec." It
can: bump `CONSTRAINT_FACTS_SCHEMA_VERSION` whenever a severity assignment changes, and the exact-
equality gate at `loader.py:727` / `constraint_facts.py:330-334` rejects the stale snapshot. But
that bump is the entire cost the map was supposed to avoid. **The map is cheaper only in exactly
the configuration where it is unsound.** There is no version of the alternative that is both safe
and cheap, so it loses on its own terms.

**One thing the field does not buy, stated so the reviewer does not credit it.** An *unrecognized*
`kind` fails closed under both designs (DD-R01), because the reader must refuse a code it cannot
interpret either way. The field's advantage is confined to *recognized* kinds whose classification
moved. That is a narrower claim than the spec's framing and it is still sufficient.

**Consequences committed to, per the brief.** DD-R06 stands: `constraint-facts/v1` →
`constraint-facts/v2`. DD-R12 stands: `SNAPSHOT_FORMAT_VERSION` 3 → 4. DD-R13 stands: all 34
fixture snapshots re-captured under licence in a named phase, using the documented byte-identity
procedure — capture, diff, confirm the only churn outside the predicted payload movement is
`captured_at`, revert the timestamp-only churn, review what remains (project memory
`byte-identity-captured_at-churn`). No requirement is amended and no acceptance cell falls away.

**The residual honesty item.** `ExtractionDiagnosticFact` today has one producer and zero consumers
(confirmed: `constraint_extraction.py:359-379` is the only construction site; nothing in either
repo reads `facts.diagnostics` — `loader.py:585-600` shape-validates and discards). So this bump
buys a contract before it buys a behavior. DD-R08 is what makes it real, and it is why both sinks
in D2 are non-optional.

---

## Core Concept

**One writer-side classification, serialized once, read by nobody.**

The system has three places a diagnostic can be born — agentic-mbse extraction, agentic-mbse profile
evaluation, and codegen's own analysis — and the temptation is to build something that routes
between them. We do not. Instead we share exactly two *types*: a severity enum and the closed code
vocabularies, and we fix each diagnostic's severity **at construction, from the writer's own table**.
By the time a diagnostic is data, its severity is already an answer. Every reader — the codegen
sink, the L6 authoring sink — branches on the field it was handed and consults no table.

That is the insight that makes the rest fall out. Severity is not a lookup, it is a value; the
version gate protects the value; and "one typed representation" means one *severity type*, not one
merged diagnostic class. The two profile consumers stay independent (LC-C04, DD-R37): codegen
re-evaluates facts and never consumes an authoring decision as state.

The same discipline settles the other three fronts. **Warnings:** the warning pre-pass renders a
degraded location rather than raising, so a location failure can never occupy the slot the BLOCK
halt needs — and the degradation is confined to the warning's own text, never written into the
strict cache the exclusion path shares. **Defaults:** one structural resolver over the expression
IR that unwraps a unit annotation and folds a unary sign, returning either a value or an *explicit*
unresolved carrying the node kind — never a silent `None` that disappears from the JSON.
**The carry:** the calc consumer supplies the reference as written, which is already on disk in
every snapshot; the shared resolver does the rest, unchanged.

It composes with what exists rather than adding layers: `resolve_producer`'s `KEY_FORMS` table
(`producer_resolution.py:436-455`) keeps its rows, its tier order, and every row function except
row 16's, which gains two dedicated inputs so it becomes reachable from a second consumer **without
changing what any other row sees** (D5 — the first draft got this wrong and design review C1 caught
it). `_raise_on_blocking` (`constraint_lowering.py:553-576`) is not touched — it already reads raw
locations, so it was never the vulnerable half. `EntryPoint` (`resolution/models.py:56-86`) is
extended by two optional fields rather than replaced.

---

## Key Bets

- **B1 — Severity is a property of the writer, not the reader.** Two readers at different versions
  must never disagree about whether the same bytes block. *If false → the fact-schema bump, the
  envelope bump, and the 34-snapshot re-capture are all cost with no benefit, and DD-B1's cheaper
  alternative should have won.* Settled above with the snapshot-route argument.
- **B2 — the written reference is on disk in every snapshot, and both consumers mean the same thing
  by it.** *(AMENDED at implement, ratified 2026-07-19. The original form said
  `source_attribute_name` alone equals the written reference; that is true only for `reference`
  bindings and **false for `chain` bindings**, where the field holds only the leaf and the qualifier
  lives in `source_instance_name`.)*

  **Recorded counterexample.** `catf_mfe_model` binds `in cryo_pump_count = cryo_pumps.n_pumps`
  (`designs/catf_mfe/vacuum.sysml:184`). Carrying the leaf alone re-anchored `n_pumps` at the owning
  part and selected a **different attribute of the same name** — `catf_vacuum_pumping__n_pumps`
  (48.0) instead of `catf_vacuum_pumping__cryo_pumps__n_pumps` (32.0). That is the silent
  same-named-wrong-anchor family this epic exists to close, so the chain-aware form is the faithful
  DD-R26 reading, not a concession. Gate 2 clause 1 caught it, which is what the gate is for.

  **The bet as it now stands:** `written_reference` is
  `{source_instance_name}.{source_attribute_name}` for a chain and the leaf otherwise
  (`usage_extractor.BindingInfo.written_reference`). Both component fields are already serialized in
  every committed snapshot, so **DD-R27 survives** — no extraction field, no agentic-mbse change, no
  schema bump. The constraint side's `FeatureReferenceFact.source_name` is the same notion from the
  same node class (`expression.py:549-569` returns `referent.name`).
  *If false → the two consumers key differently, SR-A02 does not converge, and the carry needs a
  new extraction field with an agentic-mbse change and a second schema bump.* Proven at implement by
  equality on `shared_producer` plus the whole-corpus Gate 3 probe.
- **B3 — The 22 newly-resolving self-named bindings are identity movement only, never value
  movement.** All 22 are single-consumer (Item 2 `design.md:141-149`), so no second consumer's
  value is being displaced. *If false → we are silently changing computed results across six
  fixtures under cover of a rename, which is a stop, not a forced difference.* The precedence gate
  in D6 is the instrument that would catch it.
- **B4 — No production caller depends on a fall-through entry-point key by name.** The 22 keys move
  from `{consumer_eqn}__{param_name}` to `{occurrence_owner_path}__{written_name}`. *If false →
  generated JSON input files that users hand-edit lose their keys, and the movement needs a narrower
  gate.* Falsified by Gate 3b's `rg` over `tests/` and generated `inputs/*.json`.
- **B6 — Row 16 is the only key form the calc consumer should newly reach.** The two dedicated
  fields (D5) make this structural rather than hoped-for: no shared request field's value changes,
  so no other row's input changes. *If false → the carry is a resolver-wide perturbation wearing a
  rename's clothes, which is what design review C1 caught in the first draft.* Gate 3's probe is the
  check.
- **B5 — A modeled default whose IR is a feature reference or an invocation is a legitimate model,
  not an authoring error.** It is why D7 disposes those as explicitly-unresolved rather than
  fail-generation. *If false → we are permitting a model that should have been refused, and users
  discover it as a runtime validation failure instead of a generation failure.*

---

## Key Decisions

- **D1 — One shared `DiagnosticSeverity` enum (`BLOCKING` | `ADVISORY`); `EligibilityDiagnostic.force`
  is left alone.** *Rejected: promoting `force: Literal["error","non_numerical"]` to the shared
  severity type (the spec's open question).* `force` is an input to the eligibility decision, not a
  transport severity, and `"non_numerical"` is not a severity — folding them would put a
  meaningless value on the wire. "One typed representation" is satisfied by one severity type and
  one closed-code discipline shared across the diagnostic classes, not by merging the classes.
- **D2 — Two production sinks, each a single function with two call sites.** *Rejected: a diagnostic
  routing/registry layer* (explicit Non-Goal). Codegen: one screening function invoked from the
  live route (`pipeline_builder.py:764`) and the snapshot route (`loader.py`, after parse), before
  lowering. Authoring: a loop in `level6_architecture.py:610-611`, which already holds `facts`
  between extraction and `evaluate_profile` and needs zero plumbing.
- **D3 — `ValidationIssue` gains one optional `reason_code: str | None` field.** *Rejected: minting a
  `ValidationCode` member per profile reason* (24 members → ~50; the enum is a UI-facing category
  vocabulary, not a diagnostic vocabulary). This is the minimum that makes DD-R10's "a field a
  consumer branches on" true. The two existing L6 constraint codes stay; the reason survives
  alongside the interpolated text rather than only inside it. **The object DD-A04 pins is
  `QualityCheckResult.issues` — the list of `ValidationIssue` the L6 check returns**, not the
  terminal rendering. `ValidationIssue.location` stays a preformatted `file:line` string
  (`types.py:146-177`); this design does not structure it. The five-issue print truncation
  (`validation/common.py:124-152`) is presentation and stays out of scope, so DD-A04 is satisfied by
  the code surviving in the returned list regardless of what the terminal shows.
- **D4 — The written-reference carry rides stored fallbacks behind the existing properties, excluded
  from serialization.** *Rejected: converting `source_attribute_name` from a property to a plain
  dataclass field.* The serializer iterates `dataclasses.fields()` (`serializer.py:239`) and
  then appends the computed property (`:246-250`), so a new field would add a second key to every
  snapshot. Keeping the wire form identical means the carry works on **unmodified v3 snapshots**,
  which is what lets it land before the schema work (D8).

  **Amended with B2 (ratified 2026-07-19): two stored fallbacks, not one.** The chain qualifier is a
  separate field, so `source_instance_name` needs the same treatment as `source_attribute_name`.
  `BindingInfo` gains `stored_source_attribute_name` and `stored_source_instance_name`, both marked
  `metadata={"snapshot_exclude": True}`; `_serialize_dataclass` honours that metadata by skipping the
  key **entirely** — unlike `_AST_FIELDS`, which writes `None` and would therefore have added keys to
  all 34 committed snapshots. `BindingInfo.written_reference` composes the two. Wire form unchanged;
  the `REQ-DM-03` field-set pin is updated deliberately with its reason recorded.
- **D5 — Row 16 gets two dedicated request fields, with an owner-path fallback to `instance_path`;
  no shared field's value changes for any consumer.** `ProducerRequest` gains
  `written_reference: str | None` and `occurrence_owner_path: str | None`, both defaulting to
  `None`, both read **only** inside `_occurrence_materialized_qn`
  (`producer_resolution.py:363-367`). Row 16 keys on
  `req.occurrence_owner_path or req.instance_path` for the owner path and on
  `req.written_reference or req.reference` for the name, missing when either resolves empty.
  `reference`, `target_qn`, and `instance_path` are untouched from every call site.
  *Rejected: passing the written name as `reference`* and *rejected: `reference` + `target_qn`
  together* — design review C1 falsified both, and re-verification confirms it. See "Why the
  dedicated fields" below; this replaces the mechanism the first draft proposed.

  **The `or` fallback is design review C3's must-fix, applied.** There are **five**
  `ProducerRequest` builders, not two: the constraint consumer (`constraint_lowering.py:174`), the
  calc consumer (`dependency_backtracker.py:578`), and three in `graph_builder.py` — `:1369`
  (LocalTerm), `:1606` (EXPOSE alias), `:1629` (aggregation LocalTerm pre-mint lookup). All three
  `graph_builder` sites supply `instance_path` (`:1374`, `:1611`, `:1634`) and run
  `TerminalPolicy.LENIENT`, so **row 16 is live for them today**. Making row 16 read only the two
  new fields would silently disable it for all three; `:1629` is the sharp case, since its own
  comment records the defect that reverting row 16 there would reintroduce (a defaultless entry
  point minted with no diagnostic), and a binding that stops resolving falls to a lenient terminal
  miss and **newly enters** `fallback_entry_points` — C2's failure mode in reverse. The fallback
  preserves all three byte-identically without touching their call sites. It reintroduces neither
  C1(a) (`reference` is untouched) nor C1(b) (the calc consumer still supplies no `instance_path`,
  so rows 12 and 13 stay dead for it). I9 survives: the new fields are still read at exactly one
  row.
- **D6 — Phase 1's gate is a per-binding resolution probe over the whole corpus, not a set-membership
  check.** *Rejected: verifying safety by a subset check over `fallback_entry_points`* — review C2,
  confirmed: a binding migrating tier 2 → tier 1 re-wires the graph while leaving that set identical
  in size and shape. See "The carry's blast radius" below.
- **D7 — Unsupported default IR is disposed as explicitly-unresolved, not fail-generation, and the
  generated JSON emits `null` rather than omitting the key.** *Rejected: failing generation on any
  non-foldable default* (B5: it would refuse legitimate models); *rejected: keeping the omission*
  (DD-R21 retires it explicitly).
- **D8 — The carry lands first, the schema work second.** *Rejected: one combined change.* Answers
  the spec's ordering open question: it keeps DD-A06's re-capture diff free of the six-fixture
  identity movement, so each forced-difference review has exactly one cause.
- **D9 — Downstream version pins move to one `_upstream_pins` module with a test that compares
  imported constants against it.** *Rejected: making the `agentic-mbse>=0.1.2` floor real* — the
  editable path override at `pyproject.toml:65` always wins in dev, so the floor cannot be the
  guard. The case rests on the two real `RuntimeError` guards at `loader.py:777,:782`, which are
  hand-copied literals in the downstream repo that a bump must not be able to slip past. (The stale
  `executable-profile/v3` text at `predicate_compiler.py:150,201` is error-message copy with nothing
  keying off it — real drift, but cosmetic, and not load-bearing for this decision. The live guard at
  `constraint_lowering.py:476` is correct and current at v4.)

---

## Architecture

**Data flow, agentic-mbse → codegen.**

```
extraction  ──constructs──▶ ExtractionDiagnosticFact(kind, severity, ...)
                             │  severity fixed here, from the writer's table
        ┌────────────────────┴────────────────────┐
   serialize (constraint-facts/v2)          in-memory (live route)
        │                                          │
   snapshot envelope v4                            │
        │                                          │
   loader.parse ──┐                    ┌───────────┘
                  ▼                    ▼
          screen_extraction_diagnostics(facts)   ← one function, two call sites
                  │ BLOCKING → CodeGenerationError, before lowering
                  │ ADVISORY → logger.warning
                  ▼
            constraint lowering
```

**Boundaries this design does not cross.** Codegen-side diagnostics (the tier-2 malformed literal,
the unresolved modeled default) are **not** `ExtractionDiagnosticFact`s and do not travel on the
wire. They share the severity type and the closed-code discipline and are emitted locally. Stating
this is what keeps D2 from becoming a routing layer.

**Warning pre-pass, `prepare_constraint_usages` (`constraint_lowering.py:675-693`).** Order is
already correct: associate (`:675`) → warnings (`:692`) → `_raise_on_blocking` (`:693`). The defect
is that `_report_non_numerical_warnings` calls the memoized `projected_location` closure *inside*
its `logger.warning` call (`:544-551`), and that closure delegates to `_project_excluded_location`,
which raises on an unmappable root (`:519-525`) or an anonymous usage with no location (`:507-513`).
The change is a warning-local rendering function that calls the strict projector and converts its
failure into an explicitly-marked fallback string.

`_raise_on_blocking` is untouched. It reads `decision.location.file` raw (`:553-576`) and never
consults the projector, so the halt was never itself vulnerable — only the pre-pass in front of it.
That asymmetry is why the fix is local.

**Default resolution.** `_literal_float` (`:1300-1310`) is replaced by a structural resolver over
the same serialized-IR input, returning a small result type instead of `float | None`:

```python
@dataclass(frozen=True)
class ModeledDefault:
    value: float | None          # None ⇔ unresolved
    unit_text: str | None        # carried, never converted (DD-R25)
    unresolved_node_kind: str | None   # the IR kind that stopped resolution
```

Node dispositions: `LiteralNode` → value; `UnitAnnotationNode` → recurse into `.value`, carry
`unit_text`; `OperatorNode` with one operand and operator in `("+","-")` → fold sign over the
recursive result; everything else (`FeatureReferenceNode`, `InvocationNode`, `UnsupportedNode`,
n-ary `OperatorNode`) → unresolved with its `kind`. This is exactly the shape
`predicate_compiler.py:156-171,191-193` already implements for the predicate lane; the drift the
spec names is that the default lane never got it.

**Entry-point surface.** `EntryPoint` (`resolution/models.py:56-86`) gains `unit_text: str | None`
and `unresolved_default_kind: str | None`, both defaulting to `None`. `generate_all_derived_jsons`
(`generation/entry_point.py:268-273`) stops skipping `None` and writes `null`; the parameter-group
schema renders `unit_text` in the field description.

---

## The carry's blast radius — the enumerated decision

The mechanism is four edits: the loader stops discarding `source_attribute_name`
(`loader.py:1022-1035`), `BindingInfo` carries it behind the existing property
(`usage_extractor.py:54-92`), `ProducerRequest` gains the two dedicated fields (D5), and
`dependency_backtracker.py:577-588` supplies them. The consequence is that row 16
`_occurrence_materialized_qn` (`producer_resolution.py:363-367`), which short-circuits to `_MISS`
today because the calc consumer supplies no owner path, starts firing.

### Why the dedicated fields — the first draft's mechanism was wrong

Design review C1 falsified it and re-verification confirms every count.

- **Row 16 reads `req.reference` itself** (`:366`). So the written name has to reach row 16
  *somehow*, and the first draft's answer was to put it in `reference`.
- **`req.reference` is read 31 times across the file**, by eighteen of the twenty-one rows,
  including the entire CHANNEL tier. `req.target_qn` is read at **exactly one line** (`:371`, row
  17). The driver walks `Tier.CHANNEL` fully before `Tier.DESIGN_ATTRIBUTE` (`:541-542`), so a
  mutated `reference` perturbs rows that run *before* row 16. Supplying `target_qn` does not
  neutralize that, because row 16 does not read `target_qn` either. The first draft's "holds every
  existing row's input constant" was false.
- Two concrete perturbations: row 11 `_sysml_qn` sanitizes `reference` and probes the channel
  registry — a live path (`tests/conformance/test_output_registry.py:110-125`); row 21
  `_bare_name_unique` (`:414-418`) guards `if "." in req.reference or "::" in req.reference: return
  _MISS`, so a bare written name makes a dormant unique-lookup row live, with a tie path.
- **`instance_path` is independently dangerous** (C1b). Rows 12 `_direct_channel` (`:280`) and 13
  `_chain_redefinition_follow` (`:329`) both guard `or not req.instance_path`, and the calc consumer
  passes `None` today — both rows are **dead from this consumer**. Supplying `instance_path` wakes
  them at CHANNEL tier, ahead of every design-attribute row, so a row-17 `DESIGN_ATTRIBUTE`
  resolution could become a row-12 `MODULE_OUTPUT`. That is a graph re-wire, not a rename.

The repair closes both **structurally**, which is why row 16 gets *two* fields rather than the
review's one. `written_reference` closes C1(a); `occurrence_owner_path` closes C1(b) by letting row
16 have an owner path without `instance_path` ever becoming non-`None` from the calc consumer. Row
16's `or req.instance_path` fallback (C3, D5) does not weaken that: the fallback is *read* inside
row 16 only, and the calc consumer sets no `instance_path`, so for that consumer the fallback is
`None` and only the dedicated field can supply the owner path. Rows 12 and 13, which guard on
`req.instance_path` at CHANNEL tier, remain dead from the calc consumer. The
review judged C1(b) to have "no equally clean structural fix" and asked for empirical proof instead;
a second dedicated field is that fix, and it turns C1(b) from a thing the probe must *disprove* into
a thing that cannot happen. The probe still runs — C2 needs it regardless — but now as confirmation.

**Constraint-consumer parity.** The constraint side supplies both new fields with the same values it
passes today (`written_reference = dotted`, `occurrence_owner_path = usage_qualified_name`, i.e.
`owner_instance_path` at the call sites) *and* keeps supplying `instance_path` unchanged, since row
12 is admissible under STRICT and reads it. Its behavior is therefore byte-identical by
construction, and row 16 becomes explicit for it rather than incidental. The claim "`KEY_FORMS`
itself is unchanged" softens correctly to: **the table, the tier order, and every row function other
than `_occurrence_materialized_qn` are unchanged.**

### The gates

**Gate 1 — the forced-difference table**, produced by Gate 3's probe rather than separately.
Before any generated baseline is regenerated, evidence carries one row per moved entry point across
the six fixtures (`fusion_tea`, `solar_battery_model`, `catf_mfe_model`, `chain_spike_model`,
`return_styles`, `expression_binding_probe`), Item 2's measurement being 22:

**FILLED AND ACCEPTED (orchestrator ruling, 2026-07-19).** Measured by Gate 3's probe over all 34
fixtures and all five builders; supersedes DD-R29's *estimate* of 22-across-six. This is
estimate → probe truth, not a scope change. Baselines regenerated **once** under this table.

Resolution-level movement: **89** of 303 `resolve_producer` calls moved, **every one to row 16**
(51 `target_qn`→row 16 identity-preserved, 15 `dotted_pair`→row 16 identity-preserved, 23
`entry_point`→row 16 positive resolutions). Zero MODULE_OUTPUT transitions in either direction.

Entry-point-level movement, **24 across seven fixtures**:

| class | count | fixtures | default carried | numeric result |
|---|---|---|---|---|
| pure rename (key moves, value preserved) | 18 | catf_mfe_model 1, chain_spike_model 3, expression_binding_probe 1, fusion_tea 2, return_styles 3, solar_battery_model 8 | unchanged | unchanged |
| **convergence** (two keys collapse to one that already existed) | 5 | shared_producer 1 (`__scaler__gain`→`__gain`, 40.0), expression_binding_probe 2 (`tax_rate`, 0.08), solar_battery_model 2 (`p_net_mw` 0.008, `plant_lifetime` 25.0) | unchanged | unchanged |
| **convergence onto correct scope** (identity moves to a correctly-scoped attribute of identical value) | 2 | catf_mfe_model 1 (`catf_radial_build__elongation`→`__plasma_region__elongation`, 3.0), fusion_tea 1 (`hif_driver__HIF_Driver__efficiency`→`hif_plant_pkg__hif_plant__driver__efficiency`, 0.35) | unchanged | unchanged |

Entry-point classification consequence, uniform and value-free: `entry_type` flips
`usage_literal` → `design_attribute` for 13 entry points, because a binding that resolves positively
to a design attribute is one, where a fall-through was previously recorded as a usage literal.

**Regenerated file set — exactly the pinned prediction, no extras:**
`baseline_outputs/{catf_mfe,chain_spike,solar_battery}/computation_graph.json` and
`baseline_yaml/{chain_spike,solar_battery}.yaml`.

**Recorded non-participant:** `baseline_outputs/plant_values/` is **stale at the predecessor** — it
regenerates differently with Item 4 reverted, so it is pre-existing drift of the same class as the
recorded `deep_cross_scope` stale baseline, not carry churn. Deliberately left untouched to keep
one cause per diff. No test compares it byte-exactly, so it fails nothing. It needs an owner
elsewhere.

Old key form is `entry_point_qualified_name` = `{consumer_eqn}__{param_name}`
(`producer_resolution.py:462-475`). New key form is `{occurrence_owner_path}__{written_name}` — and
under D5 that prediction is now guaranteed rather than hoped for, because no other row's input
moved. The design does not pre-enumerate rows it has not measured; the implement phase must not
regenerate baselines until the table is filled. Baselines regenerate **once**, under that table.

**Gate 2 — the precedence stop rule (brief item 4), widened past value.** A **stop** — revert and
amend the design — if any row shows either:
- a changed *value*: `default carried` differs, or `numeric result` differs; **or**
- a changed *resolution shape*: `outcome` or `key_form` moved to anything other than row 16.

The second clause exists because review B3 is right that a re-wired binding can still produce the
same numeric result on a given fixture and thereby pass a value-only gate while having changed the
graph. D5 is the structural reason neither should happen; the gate is what proves it did not.

**Gate 3 — the per-binding resolution probe, replacing the fallback-set subset check.** For every
bound binding in every committed fixture — 249 bound bindings, 167 carrying a `::`-qualified
`source_path` — resolve under both request shapes and diff the tuple `(outcome, identity, key_form)`
per binding. This is the gate; set membership is not.

**Probe scope covers all five `ProducerRequest` builders, not only bindings** (design review C3).
Aggregation and LocalTerm resolutions are not bindings, so a binding-only probe cannot see the
regression class C3 names. Two of the five builders are covered by construction rather than by
sampling, and the design states which is which:

- **Bindings (calc + constraint consumers)** — covered empirically by the per-binding probe above.
- **The three `graph_builder` consumers (`:1369`, `:1606`, `:1629`)** — covered *structurally*: with
  D5's `or req.instance_path` fallback, every input row 16 reads for these three resolves to exactly
  the value it reads today (`instance_path` unchanged, `written_reference` unset so the name falls
  back to `reference`), and no other row function changed. Their resolutions are byte-identical by
  construction. Implement proves the premise, not the consequence: an `rg` confirming none of the
  three call sites sets either new field, plus the whole-suite and byte-identity gates that would
  fail if any aggregation or LocalTerm resolution moved.

The first draft's subset argument over `fallback_entry_points` was true only for the 22 self-named
bindings, which are already fallback members by construction and can therefore only leave. It said
nothing about the other ~227, and it is blind to the failure that matters: a tier-2 → tier-1
migration leaves the set **identical in size and shape** while re-wiring the graph. This repo
already carries that lesson in a comment on the gate that catches it —
`tests/conformance/test_snapshot_generation.py:215-222`: *"CHANNEL IDENTITY, not merely
`fallback_entry_points` vacated ... Do NOT narrow this to a metadata-only or graph-only diff."* It
cites the multi-hop EXPOSE precedent, which is the same trap recorded in project memory
`multihop-expose-offline-parity`.

What survives of Item 3's dividing line, stated at the strength it holds: **no self-named binding
newly enters `fallback_entry_points`**, because keys enter at exactly one site
(`dependency_backtracker.py:603`) only on a lenient terminal miss, and a key resolving positively
through row 16 leaves rather than enters. Anything stronger is the probe's job. Final-generation V11
(`cli/__init__.py:278`, raising at `:280-284`) stays strict and unchanged (DD-A16).

**Gate 3b — B4's falsification instrument.** `rg` the 22 old keys across `tests/` and every
generated `inputs/*.json`. A hit means a consumer depends on a fall-through key by name and B4 loses.

**Gate 4 — `shared_producer` flips to the convergence proof, RED-first.** No test asserts the
current two-entry-point state — PROVENANCE.md:62's "a test asserts it" is false at HEAD, and the
fixture appears in `tests/` only as a registered snapshot (`tests/conformance/conftest.py:62`). So
the acceptance surface is **newly authored against the current state first**: a test asserting the
two present keys, confirmed green at the predecessor, then rewritten in the same shape to assert
the single converged key `SharedProducer__the_rig__gain` with one modeled default (40.0) and one
group assignment. Both public routes. Without the first step there is no RED and DD-A14 is
unfalsifiable.

### The owner-path parity question, and its bracket trap

**The question, first: can the calc consumer produce the same owner path the constraint consumer
produces?** Row 16 keys on it, so if the two derivations disagree the key differs and convergence
does not happen.

The constraint side's value is the *owning occurrence path*, not the constraint usage's own EQN
(`constraint_lowering.py:1174,:1197,:1221` supply `owner_instance_path`, dispatched through four
owner-expansion paths at `:709-722`). The calc side has no equivalent today:
`_get_parent_part_for_usage` (`dependency_backtracker.py:523-531`) returns `segments[-2]` — a bare
single segment (`the_rig`), not a path — and it is wired to `parent_scope` (`:583`), not to an owner
path.

**Two shapes, and they do not behave alike.**

- **`PartUsage`-owned, unbracketed** — `shared_producer`'s shape. The constraint side yields
  `SharedProducer__the_rig`; the calc side reaches it from `usage.qualified_name.rsplit("__", 1)[0]`.
  They coincide, and the carry works.
- **Occurrence-indexed `part_def` owner.** The constraint side's path comes from
  `part_instance_index.py:263` and carries `[i]` occurrence brackets. **A calc usage QN never has
  brackets**, so no derivation from the QN can reproduce it. (This is the review's measurement; I
  could not disconfirm it, and the disposition below is safe whether or not it holds.)

**Disposition, stated rather than discovered: row 16 misses for bracketed owners, and missing is
safe.** `_hit(None)` returns the same `_MISS` tuple as any other miss (`:196-197`) and the driver
`continue`s on `identity is None` (`:541-553`), so a bracketed owner falls through to exactly
today's behavior — the lenient terminal mint. No row is starved and nothing regresses. This is
deliberate partial coverage, not silent partial coverage: the convergence property closes for the
unbracketed shape and is **explicitly not claimed** for the bracketed one.

**Stop condition.** If Gate 3's probe shows any bracketed-owner binding whose `(outcome, identity,
key_form)` changes at all, the assumption above is wrong and that is a stop under Gate 2 — the
bracketed shape must not resolve *partially* or *differently*, only miss. If a bracketed owner ever
needs convergence, that is a new item with its own owner-path derivation, not an extension smuggled
in here.

**Phase 0 exit, accordingly, is two checks not one:** equality on `shared_producer` (the
unbracketed shape), **and** a bracketed-owner fixture confirming row 16 *misses* rather than hits a
wrong key. A single-fixture exit would have proven the general claim from the one shape where the
derivations coincide by accident.

---

## Required Invariants

- **I1** — A diagnostic's severity is fixed at construction and never recomputed by a reader. No
  `kind → severity` lookup exists on any read path in either repo. Provable by `rg`.
- **I2** — Both schema-skew directions fail closed before field deserialization, for the fact schema
  and the snapshot envelope. The advance preserves the existing exact-equality property
  (`constraint_facts.py:330-334`, `loader.py:719-730`); no new mechanism is built and no
  grandfathering route is added (DD-R15).
- **I3** — No failure inside warning preparation can reach the caller. `_raise_on_blocking` runs on
  every path where it runs today. The warning-local fallback **never writes into
  `location_cache`** (`constraint_lowering.py:678`); if it did, the exclusion path at `:709` would
  read a degraded value instead of raising, leaking the degradation and breaking DD-R18.
- **I4** — `map_live_source_referent` and `validate_snapshot_source_referent` keep raising for every
  other caller: `serializer.py:165`, `constraint_lowering.py:619,:625`, and `:709`'s exclusion
  projection. Only the warning text degrades.
- **I5** — No self-named binding newly *enters* `fallback_entry_points`, and every remaining member
  is calc-EQN-shaped. The stronger whole-corpus safety claim is carried by Gate 3's per-binding
  probe, not by this set — set membership cannot see a tier-2 → tier-1 migration.
- **I9** — `written_reference` and `occurrence_owner_path` are read at exactly one site,
  `_occurrence_materialized_qn`. Provable by `rg`, and it is what makes B6 structural. No other row
  function and no shared request field changes value for any consumer.
- **I10** — Row 16 stays reachable from all three `graph_builder` consumers (`:1369`, `:1606`,
  `:1629`) via D5's `or req.instance_path` fallback, and none of the three sets either new field.
  Provable by `rg`. Without this, C3's regression reverts the defect `:1629`'s comment records.
- **I6** — A modeled default's unit is carried or the default is refused; it is never converted and
  never silently discarded (DD-R25).
- **I7** — The generated JSON contains a key for every entry point in the group. Absence of a value
  is `null`, never absence of the key.
- **I8** — The two profile consumers stay independent: codegen re-evaluates facts and consumes no
  authoring decision as state (LC-C04, DD-R37).

---

## Component Overview

| Component | Location | Responsibility |
|---|---|---|
| `DiagnosticSeverity` | agentic-mbse, alongside `constraint_facts.py:49` | The shared two-member severity enum, and the writer-side kind→severity table used at construction |
| `ExtractionDiagnosticFact` | `agentic_mbse/sysml/constraint_facts.py:170-178` | Gains `severity`; `kind` constrained to a closed frozenset at construction |
| `EligibilityDiagnostic` | `agentic_mbse/sysml/executable_profile.py:108-118` | `reason` enforced against `REASON_CODES` (`:62-96`) in production, not by test convention (DD-R05) |
| codegen diagnostic screen | new, `sysml_codegen/analysis/` | One function; BLOCKING raises before lowering, ADVISORY logs. Called from both routes |
| L6 extraction-diagnostic sink | `agentic_mbse/validation/level6_architecture.py:610-611` | Emits `ValidationIssue`s from `facts.diagnostics`; carries `reason_code` |
| `ValidationIssue.reason_code` | `agentic_mbse/sysml/types.py:146-176` | The branchable field DD-R10 requires |
| warning-local location rendering | `sysml_codegen/analysis/constraint_lowering.py:532-551` | Renders a marked fallback instead of raising; does not touch the strict cache |
| `ModeledDefault` resolver | replaces `_literal_float`, `constraint_lowering.py:1300-1310` | Structural unwrap + sign fold over the IR; explicit unresolved otherwise |
| `EntryPoint` | `sysml_codegen/resolution/models.py:56-86` | Gains `unit_text`, `unresolved_default_kind` |
| `BindingInfo` carry | `sysml_codegen/extraction/usage_extractor.py:54-92`, `snapshot/loader.py:1022-1035` | Stored fallback behind the existing property; wire form unchanged |
| tier-2 malformed collector | `sysml_codegen/resolution/supplied_values.py:267-287,:528-597` | A second collected list drained as a **new** log record |
| `ProducerRequest.written_reference`, `.occurrence_owner_path` | `sysml_codegen/resolution/producer_resolution.py:97-120` | Row 16's two dedicated inputs; read at exactly one site (I9) |
| `_upstream_pins` | new, `sysml_codegen/` | Single home for the three expected upstream version strings (D9) |

**Named deletions** (DD-R36 — proved by `rg` returning no match, not by a wrapper):
`_literal_float`; `parameter_groups.design_attribute_default_value` (`:504-522`) and
`producer_resolution._modeled_default` (`:519-526`), which are the same bare-`float()` lane over two
indexes; the `if ep.default_value is not None` guard at `entry_point.py:271`; the raising branch of
warning-location preparation; the hand-copied version literals at `loader.py:777,:782` and
`constraint_lowering.py:476`.

**Kept lanes, each with its stated distinct input** (DD-R23). The consolidation target is the
*float-producing* lanes over a captured value; the AST→string extractors are a different boundary.

- **IR lane** (the new `ModeledDefault` resolver) — input is serialized `ExpressionIR`. The only lane
  that sees constraint modeled defaults. Subsumes lanes 3 and 5 above where they read a captured
  string that originated from the same IR.
- **Captured-string lane** (`parameter_groups._parse_default_value`, `:820-829`) — input is
  `AttributeData.default_value`, a string produced by AST extraction, for which no IR exists. Kept —
  **with a condition.** It is a bare `float()`, so it returns `None` for exactly the signed and
  unit-annotated forms the IR lane now handles, and DD-R23's "no second representation" is only
  defensible if that asymmetry is justified rather than inherited. Its input is produced by the AST
  lane (`:207-247`), which routes operator expressions through `evaluate_true_static_expression` and
  therefore already folds signs and strips units *before* the string is captured. **Implement must
  confirm that** — the captured string never carries a sign or a unit — and record it; if it can,
  this lane cuts over to the resolver too. DD-A13 covers it.
- **AST lane** (`parameter_groups._extract_default_value`, `:207-247`) — input is a SysIDE AST node;
  output is `str`, not `float`. It is a *producer* of the captured string, not a competitor to it,
  and it is pinned by `tests/conformance/test_ast_dispatch_invariant.py:82-108`. Kept.
- `extractor._extract_default_value` (`:504-529`) duplicates the AST lane's literal handling with a
  narrower node set. Implement determines whether it collapses into the AST lane or has a distinct
  input; the survivor is stated with its reason in evidence. **This is the one lane boundary the
  design leaves open**, and DD-A13 is the instrument.

---

## Non-Goals

Inherited from the spec unchanged: general constant folding and unit conversion; any diagnostics
framework beyond the versioned contract; Item 5's portability and Item 12's grandfathered-snapshot
closure; reworking the certified seams of Items 1–3. `AggregationDiagnostic` stays out of scope.
Making L4's rendering load-bearing stays out. Fixing the L6 five-issue print truncation
(`validation/common.py:124-152`) stays out — DD-A04 requires the code in the structured result, not
in the terminal output.

Additionally, and settled here: the diagnostic **classes** are not merged. D1 shares types, not
representations.

**Recorded from design review, not assigned here.** The mirror of DD-R32 exists one tier up: a
malformed *tier-1* literal sets `saw_non_literal = True` (`supplied_values.py:230`) and
`_resolve_value` returns early at `:264-265`, suppressing tiers 2a and 2b entirely — the same class
of bug Item 1 deliberately fixed *within* tier 2 (rationale comment at `:281-285`). DD-R32 scopes
this item to tier-2 silence only, so this is out of scope. Recorded so it is not lost; it needs an
owner elsewhere.

---

## Phased Plan

No `plan.md` — this is the plan. Phases are ordered by what each one de-risks.

**Phase 0 — [x] COMPLETE — probes, no production change.** Confirm B2 by equality on `shared_producer`: the
loader-visible `source_attribute_name` equals the constraint side's `FeatureReferenceFact.source_name`
for the shared `gain`. Settle owner-path parity on **both** shapes — equality on `shared_producer`
and a bracketed-owner fixture confirming row 16 misses. Establish what the generated schema does
with a missing vs `null` field, before Phase 3 commits to `null`. **Exit: B2 proven or surfaced;
both parity checks answered; the `null` question answered.** The unit/sign fixture-inventory
question is already answered — see Phase 3.

**Phase 1 — [x] COMPLETE — the carry (codegen only, works on unmodified v3 snapshots).** Loader plumbing,
`BindingInfo` stored fallback, the two `ProducerRequest` fields plus the one-line row-16 change, and
both consumers' call sites. Author the `shared_producer` RED surface against the *current* two-key
state first, confirm green at `3fbec63`, then flip it. Run Gate 3's per-binding probe over all 249
bound bindings under both request shapes; it produces the Gate 1 table as a by-product. Apply the
Gate 2 stop rule on both clauses; run Gate 3b's `rg`. Regenerate the six fixtures' baselines
**once**, under the table. Correct the falsified artifacts (DD-R31) and apply PC-2's one-line SR-R16
amendment (DD-R33). **Exit: DD-A14, DD-A15, DD-A16, DD-A18 pass; no binding's `(outcome, identity,
key_form)` moved except to row 16.**

**Phase 2 — [x] COMPLETE — warning totality and BLOCK preservation (codegen only).** The warning-local fallback,
with the `location_cache` trap (I3) as the review focus. Name every moved Item-1-pinned byte
sequence with its reason (DD-A10); DD-R18's other callers proven still strict (DD-A09).
**Exit: DD-A08, DD-A09, DD-A10.**

**Phase 3 — [x] COMPLETE (live route; snapshot route deferred to Phase 5 as declared) — modeled-default fidelity and lane consolidation.** The `ModeledDefault` resolver, `EntryPoint` fields, `null`-not-omitted JSON,
the unresolved diagnostic, the lane deletions, and the tier-2 malformed collector (DD-R32 — a *new*
log record; the tier-1 aggregate string at `supplied_values.py:583-590` is byte-frozen by a Phase-0
acceptance overlay SHA-256 and must not be edited). New fixtures for `:= -0.1` and `= 40.0 [MW]`.

**The licence dependency, declared** (review M1, re-verified): there are **zero `unit` IR nodes
across all 34 committed snapshots**, and every constraint-formal default present is a plain
`LiteralNode`. Unit-annotated defaults exist in fixture *source* — e.g.
`tests/fixtures/catf_mfe_model/designs/catf_mfe/shield.sysml:75,106,130` — but never reach the
default lane. DD-A11 requires **both public routes**, so its snapshot route needs a newly captured
fixture, which needs the SysIDE licence. The new fixtures' capture therefore joins the licensed
sequence in Phase 5, and DD-A11's live route is what Phase 3 earns on its own. No agentic-mbse
change is implied: `UnitAnnotationNode` and `OperatorNode` already exist, are already in the union,
and are already emitted by the parser (`expression_ir.py:51-130,:266`).

**Second forced-difference pin — the Phase 3 baseline churn** (review M2, re-verified). This is
named separately because it is broader than Phase 1's and has a different cause; folding it into the
carry's regeneration would defeat Gate 1's one-cause-per-diff discipline. `EntryPoint` is a Pydantic
`BaseModel` serialized verbatim into `entry_point_groups` across **12 committed baselines**
(`tests/fixtures/baseline_outputs/*/computation_graph.json`), dumped with `exclude_none=False` —
proved by `"source_calc_usage": null` appearing in ten of the twelve. So `unit_text` and
`unresolved_default_kind` emit two new `null` keys on **every entry point in all 12 baselines**. The
`null`-not-omitted change at `generation/entry_point.py:271-273` rewrites the emitted `inputs/*.json`
templates as a **second, independent** churn. Evidence pins both: the field-addition churn is
justified as mechanical and uniform (every entry point, two keys, no value movement), and the
`inputs/*.json` churn is justified per file as the DD-R21 behavior change it is. Baselines regenerate
once for Phase 3, under that pin.

**Exit: DD-A12, DD-A13, DD-A17, and DD-A11's live route. DD-A11's snapshot route completes in
Phase 5.**

**Phase 4 — the coordinated pair (agentic-mbse first).** This is the only phase that touches
agentic-mbse, and it exists because DD-B1 landed on a facts-side change. Severity enum and
writer-side table, closed `kind` vocabulary, `REASON_CODES` enforced at construction,
`ValidationIssue.reason_code`, the L6 sink, `constraint-facts/v2`. Then codegen: envelope v4, the
screening function at both call sites, `_upstream_pins` and its guard test.
**Exit: DD-A01–DD-A05, DD-A07, DD-A20.**

**Phase 5 — licensed capture.** Two jobs, not one: capture the new Phase 3 signed/unit fixtures (the
M1 dependency), and re-capture all 34 snapshots at v4. Byte-identity gate as a timestamp-only diff
check with `captured_at` churn reverted; only the payload movement Phases 1 and 4 predict is
reviewed, each entry named. A full re-capture rewrites every `captured_at`, so the new fixtures must
be visibly separable from the churn (project memory `byte-identity-captured_at-churn`). Requires
`SYSIDE_LICENSE_KEY` from `~/1cfe/agentic-mbse/.env` — export it explicitly or the suite reads as a
false baseline (project memory `syside-license-key-explicit-env-needed`).
**Exit: DD-A06, and DD-A11's snapshot route.**

**Phase 6 — evidence and delivery.** DD-A19: the exact new agentic-mbse commit, the codegen commit,
the resolved lock, and the additive-certified status of the Items 1–3 chain since `515e08bb`.
Merge order is load-bearing: agentic-mbse PR #11 before sysml-codegen PR #9 (project memory
`constraint-exec-v3-pr-wave`).

---

## SURFACED — B2 is falsified for CHAIN bindings (implement, Phase 1)

**Trigger:** genuine surprise producing evidence against a premise the plan rests on
(capture-fidelity rule 4). Recorded rather than resolved silently. **Dependent conclusions are
parked pending owner ratification; no baseline has been regenerated.**

**B2 as written says** `source_attribute_name` on disk equals the written reference the constraint
side uses. Measured over all 34 fixtures, that holds for `reference` bindings and **fails for
`chain` bindings**, where `source_attribute_name` is only the *leaf*. The qualifier lives in a
separate field, `source_instance_name`.

**The failure it caused, measured.** `catf_mfe_model` binds
`in cryo_pump_count = cryo_pumps.n_pumps` (`designs/catf_mfe/vacuum.sysml:184`). Carrying the leaf
alone re-anchored `n_pumps` at the owning part and selected a **different attribute of the same
name**:

| | key | value |
|---|---|---|
| model means | `CATFMFEVacuum__catf_vacuum_pumping__cryo_pumps__n_pumps` | **32.0** |
| leaf-only carry selected | `CATFMFEVacuum__catf_vacuum_pumping__n_pumps` | **48.0** |

That is a wrong-value regression, and Gate 2 clause 1 caught it — the gate worked as designed.

**The repair, applied and measured, still inside DD-R26.** `written_reference` is now the reference
*as written*: `{source_instance_name}.{source_attribute_name}` for a chain, the leaf otherwise
(`usage_extractor.BindingInfo.written_reference`). Row 16 already flattens dots, so the chain key
lands on the correct attribute. This is arguably the faithful reading of DD-R26 ("the reference as
written") and the leaf-only version was the incomplete one — but it amends B2 and D4, so it is
**surfaced, not assumed**. `source_instance_name` needed the same stored-fallback treatment as
`source_attribute_name`; it is likewise already in every committed snapshot, so DD-R27's "no new
extraction field" survives.

**Blast radius after the repair, superseding DD-R29's 22-across-six.** Gate 3 probe over all 34
fixtures, all five builders, 303 `resolve_producer` calls: **89 resolutions moved**, every one to
row 16. At the entry-point level: **18 pure renames** (value preserved), **5 convergences** onto a
key that already existed (SR-A02's class, `shared_producer` among them), **1 new entry point**
(`CATFMFERadialBuild__catf_radial_build__plasma_region__elongation`, 3.0 — same value as the outer
attribute it now correctly shadows). Seven fixtures, not six: DD-R29's six plus `shared_producer`.

**Gate results at this state:** shape stops **0** (no resolution moved to any key form other than
row 16; zero MODULE_OUTPUT transitions in either direction, so no graph re-wire); value stops **0**;
same-key value changes across every fixture's entry points **0**. The two identity changes that are
not pure renames both resolve to a *correctly scoped* attribute carrying the **identical** value.

**Parked for the owner:** whether to ratify the chain-aware `written_reference` (amending B2/D4),
and whether to accept the revised blast radius as the Gate 1 pin. Baseline regeneration and the
DD-R31/DD-R33 artifact corrections are blocked on that ratification.

## Potential Risks

- **The re-capture hides the identity movement.** Mitigated by D8's ordering: the carry's baseline
  regeneration happens in Phase 1, three phases before the re-capture, so each diff has one cause.
- **The warning fallback leaks into the strict path** via the shared `location_cache`. This is the
  single most likely way to pass every new test and still break DD-R18. I3 names it; DD-A09 tests it.
- **`null` in generated JSON breaks input loading at run time.** Today the key is omitted, which
  fails differently. Phase 0 must establish what the generated schema does with a missing vs null
  field before Phase 3 commits; if `null` fails validation where omission did not, that is a
  behavior change to pin, not to absorb silently.
- **Owner-path parity turns out to be unreachable even for the unbracketed shape.** Then row 16 stays
  unreachable from the calc consumer, SR-A02 does not close by these means, and this is a surfacing
  event. The bracketed shape is already dispositioned as a deliberate miss and is not this risk.
- **Licence risk is real for Phases 3 and 5, not just Phase 5.** Phases 1, 2 and 4's codegen half are
  genuinely licence-free; Phase 3's code is, but DD-A11's snapshot route is not. The first draft
  claimed "four codegen-only phases" were insulated — that was wrong and is corrected above.

## Integration Strategy

Extends, never reworks, the Items 1–3 seams: Item 1's warning/BLOCK ordering bytes change only where
DD-R16/R17 require it, each named; Item 2's shared resolver gains a second consumer reaching an
existing row with `KEY_FORMS` untouched; Item 3's generation-gate V11 caller (`cli/__init__.py:278`, raising at `:280-284`) is unchanged and its
vacuity dividing line is re-verified rather than re-derived. The delivery wave is unchanged: PR #11
then PR #9, no replacement upstream PR.

## Validation Approach

The spec's 20 acceptance cells are the criteria; the phase exits above map each cell to the phase
that earns it. RED-first throughout: each cell's public surface fails at `3fbec63` (codegen) /
`515e08bb` (agentic-mbse) for its named defect and passes at candidate GREEN with identical test
bytes. `shared_producer` is the one cell with no existing RED, and Gate 4 says how it is built.
Both public routes (live and snapshot) for every cell the spec marks. Suite, `PYTHONOPTIMIZE=1`,
mypy, ruff, and the byte-identity gate re-run at each phase exit — with generated baselines
format-exempt (project memory `generated-baselines-format-exempt`).

## Next-Stage Handoff

**Fixed:** DD-B1 and its three consequences (v2 facts, v4 envelope, 34-snapshot re-capture); the
phase order, in particular carry-before-schema; the two-sink shape; severity as a construction-time
value; row 16's two dedicated request fields and the rule that no shared field's value changes for
any consumer (D5/I9); Gate 3's per-binding probe as Phase 1's gate; the bracketed-owner disposition
(row 16 misses, and that is safe).

**Open, for implement to settle with a stated reason:** which of `extractor._extract_default_value`
and the AST lane survives, and whether `_parse_default_value` cuts over too (DD-A13); the exact
fallback rendering string for an unmappable warning location; whether `unit_text` reaches the
generated schema description or only the model.

**De-risk first:** Phase 0's two owner-path parity checks — the unbracketed equality *and* the
bracketed miss. Everything in Phase 1 rests on them, and the first draft's single-fixture exit would
have proven the general claim from the one shape where the derivations coincide by accident.

**Round-2 review scope** (per the review's max-two-round discipline): the C1/C2 repair — dedicated
`written_reference` and `occurrence_owner_path` fields plus the per-binding probe — Phase 0's
strengthened parity exit, and the two Phase 3 corrections. Not a re-review of the whole design.

---

## Implementation Notes

### Item 0 — C3 amendment (complete)

Applied before any production code, per the brief. D5 now specifies row 16 reading
`req.occurrence_owner_path or req.instance_path` (and `req.written_reference or req.reference`),
with the three `graph_builder` builders named and the reason the fallback preserves them. Gate 3's
probe scope widened to all five `ProducerRequest` builders, stating which two are covered
empirically and which three structurally. Added **I10** (row 16 stays reachable from the three
`graph_builder` consumers; neither new field is set there). Both proved by `rg`.

### Phase 0 — complete

`scripts/probes/probe_item4_phase0.py`, snapshot-only, no production change.

- **B2, unbracketed:** calc `source_attribute_name` = `'gain'`, constraint
  `FeatureReferenceFact.source_name` = `'gain'`. **Equal.** (Falsified later for chains — see the
  surfaced conflict above.)
- **Owner-path parity, unbracketed:** `shared_producer`'s calc owner path derives to
  `SharedProducer__the_rig`, row-16 key `SharedProducer__the_rig__gain` **hits**. Parity holds.
- **Bracketed miss proof:** `constraint_multi_instance` is the bracketed-owner fixture and already
  existed, so none was authored. Constraint side carries
  `constraint_multi_instance__the_design__c__cell[0]`; the calc usage QN has no brackets, and the
  design attribute is def-scoped (`constraint_multi_instance__Cell__cell_rating`). Row 16 **misses**
  rather than hitting a wrong key — the disposition holds, by a slightly different mechanism than
  predicted (def-scoping, not just bracket mismatch). The two-check exit earned its keep.
- **`null` vs missing (Phase 3 dependency):** the generated group schema
  (`templates/parameter_group_schema.py.jinja2`) renders a defaultless field as required with a
  non-optional type, under `extra: "forbid"`. Measured: omitted key → `ValidationError` `missing`;
  `null` → `ValidationError` `float_type`. **Both fail; only the error type changes.** D7's `null`
  does not turn a passing load into a failing one. Phase 3 may proceed; pin the message change.

### Phase 1 — mechanism landed, gates green, regeneration deliberately not run

Changed: `usage_extractor.BindingInfo` (two `snapshot_exclude` stored fallbacks, the
`written_reference` property, `source_instance_name` falling back); `serializer._serialize_dataclass`
(honours `snapshot_exclude` metadata — skips the key entirely, unlike `_AST_FIELDS` which writes
`None`, so committed wire forms are untouched); `loader._deserialize_binding_info` (stops discarding
both names); `ProducerRequest` (+`written_reference`, +`occurrence_owner_path`);
`_occurrence_materialized_qn` (both inputs with C3 fallbacks);
`dependency_backtracker` (+`_owner_instance_path_for_usage`, supplies both fields, docstring
corrected); `constraint_lowering` (supplies both fields with the values it already passed).

- **shared_producer RED→GREEN.** Surface newly authored
  (`tests/conformance/test_shared_producer_convergence.py`), both routes. Verified the two-key state
  first so the RED was not a plumbing failure, then RED for the right reason (extra
  `SharedProducer__the_rig__scaler__gain`), then GREEN on one key, default 40.0, one group.
- **I9/I10 by `rg`:** the two fields are read at exactly one site; `graph_builder` sets neither.
- **Gates:** Gate 2 **PASS** (0 shape stops, 0 value stops, 0 same-key value changes). Gate 3b: hits
  are generated baselines (regenerate under Gate 1), the DD-R31 artifacts, and one stale provenance
  *comment* in `tests/conformance/test_parameter_group_deriver.py:384-386` — that test still passes
  because `classify()` traces the binding index, not the entry-point set. **B4 holds.**
- **Suite:** 2989 passed / 22 failed, normal and `-O` (the two extra `-O` failures are
  `assert`-under-`PYTHONOPTIMIZE` tests that fail identically at the predecessor). mypy 72 errors
  before and after — **zero added**. ruff clean on `src/` and all new files.
- **The 22 failures, all expected and none masked:** 10 generated-baseline comparisons
  (solar_battery, chain_spike, catf_mfe) awaiting the Gate 1 regeneration; 7
  `TestResolveBindingViaRegistry` unit tests that construct `agentic_mbse.sysml.types.BindingInfo`
  — a **different type** that production never uses on this path and that lacks
  `source_attribute_name` entirely (a latent test-fidelity defect this change exposed);
  `test_req_dm_03_fields_binding_info` pinning `BindingInfo`'s field set, now +2; and 4
  entry-point-identity tests. **Deliberately not fixed** — each needs a disposition that follows
  from ratifying the surfaced amendment.

### Phase 1 — complete (post-ratification)

All five orchestrator rulings applied (2026-07-19). Baselines regenerated **once** under the
accepted Gate 1 table; artifact corrections landed; suite at **zero failures**.

**Regenerated file set — exactly the pinned prediction, no extras:** three
`baseline_outputs/*/computation_graph.json` (catf_mfe, chain_spike, solar_battery) and two
`baseline_yaml/*.yaml` (chain_spike, solar_battery). `plant_values` deliberately untouched as
pre-existing stale drift (verified: it regenerates differently with Item 4 reverted).

**One test mechanism changed, and it is the item most worth reviewing.**
`test_fingerprint_stability.py::test_policy_update_changes_only_verifier_hash_and_derived_fingerprint`
generated its "reviewed" side from a whole archived git revision, which silently assumed generated
output was otherwise stable across that revision boundary. The carry moved chain_spike's entry-point
keys, so **no revision can satisfy the test as written**: the verifier policy last changed at
`e217119`, strictly before the carry, so any revision with the old policy also has the old keys.
Advancing the revision pin removes the policy delta the test needs; leaving it fails on artifact
drift. The mechanism now takes **only** `contracts/verify.py` from the reviewed revision and
generates both sides from the working tree, isolating the single variable the test is about. The
asserted property is unchanged and strictly better isolated. **Flagged for audit scrutiny as a
certified-seam mechanism change, not a repin** (orchestrator ruling, 2026-07-19: noted for audit
rather than ruled on).

**Why no repin could work, in full.** The test needs a reviewed revision that differs from the
working tree in `contracts/verify.py` **and nothing else**. `verify.py` changed exactly once since
the old pin, at `e217119`, which is strictly before the carry. So every revision carrying the old
policy also carries the old entry-point keys, and every revision carrying the new keys also carries
the current policy. Advancing the pin to the carry commit makes `reviewed_verifier_hash ==
candidate_verifier_hash`, which fails the test's own `!=` assertions on the verifier hash and the
derived fingerprint; leaving the old pin fails on `pipeline.yaml`, `model_contract.json` and
`inputs/design_params.json` drift. Both directions fail, and no third revision exists. The coupling
the test carried — "generated output is stable across this revision boundary" — was an unstated
assumption, not part of its claim.

**What replaces it.** `REVIEWED_REVISION` now contributes exactly one file. The reviewed source
tree is the working tree with `src/sysml_codegen/contracts/verify.py` overwritten from
`git show <rev>:...`, everything else symlinked. Both sides then generate from the same code, so
the only difference that can reach the seal is the verifier policy.

**The new loud guard, and why it is the load-bearing part.** Isolating the variable this way makes
a silent no-op possible in a way the old form prevented structurally: if `REVIEWED_REVISION` ever
stops differing from the working tree's `verify.py` — because the policy is reverted, or the pin is
advanced carelessly — both sides become identical and every assertion would pass while testing
nothing. So the test now asserts, **before generating anything**:

```
assert reviewed_verify != (REPO_ROOT / "src/sysml_codegen/contracts/verify.py").read_bytes(), (
    "REVIEWED_REVISION must carry a different verifier policy than the working "
    "tree, or this test asserts nothing"
)
```

This guard is what makes the rewrite safe to accept: the failure mode the new mechanism introduces
is the one thing it checks first, with a message that names the cause. It was verified to fire —
the intermediate state with `REVIEWED_REVISION` pointed at the carry commit tripped it exactly as
intended, which is how the impossibility above was confirmed empirically rather than argued.

**Other pins repinned with reasons recorded in-line:** the snapshot-portability manifest SHA-256
(delta verified to be exactly two key movements and nothing else) and the `REQ-DM-03` `BindingInfo`
field set (+2, wire form unchanged).

**Two conformance tests re-pointed at the post-carry truth**, both of which had asserted the
*existence* of the defect the carry closes: `test_factory_formula`'s "the factory mints new entry
points" (now model-keyed — `solar_battery_model` converges onto pre-existing keys, `attr_expr_probe`
still mints) and `test_parallel_validation`'s "solar_battery emits unresolved-producer warnings" (now
asserts zero, with I7's visibility guard confirmed still covered directly in
`test_output_registry_construction.py`).

**Validation:** suite **3011 passed / 0 failed**, zero `no live syside license` skips.
`PYTHONOPTIMIZE=1`: same, except two `assert`-under-`-O` tests that fail identically at the
predecessor. mypy **72 errors before and after — zero added**. ruff **11 pre-existing errors before
and after — zero added**; `src/` and all new files clean.

### Phase 2 — complete

**R-8 warning totality (DD-A08), with order preserved before BLOCK (DD-A17).**
`_report_non_numerical_warnings` took a strict `projected_location` callable and resolved each
warning's location eagerly, so a mapping failure on the first warned usage aborted the whole
pre-pass: zero warnings, and the referent error standing in place of the actionable BLOCK halt.
It now takes a `warning_location` callable that cannot raise.

**The I3 trap, and the better answer.** The first implementation deliberately bypassed the shared
`location_cache` so a degraded value could never leak into the exclusion path. That broke a pinned
invariant — `test_each_named_and_anonymous_excluded_location_projects_once` requires each mappable
location to be projected exactly once (I10). The resolution is strictly better than the bypass:
`warning_location` delegates to the existing cached `projected_location` inside a `try`, because
that closure **raises before it caches**. Only a successful projection is ever written, so a
mappable location is memoized as before and a degraded one is never stored — the exclusion path at
the same index still re-attempts and still fails loudly. Both invariants hold, and neither is
traded for the other.

**Fallback rendering** (design open question, settled): `<unmapped {basename}>:{line}:{column}`.
The raw path is machine-specific and this string is user-facing, so it renders the basename; line
and column are the actionable part and are preserved.

**Forced differences: none.** A *mappable* location renders exactly the bytes it rendered before —
only the failure path changed, from raising to degrading. Every Item-1-pinned warning byte sequence
(`test_constraint_non_numerical.py`, `test_constraint_usage_preparation.py:409-443`,
`test_constraint_lowering.py`) passes unchanged, so **DD-A10 is satisfied with zero moved bytes**.

**DD-A09** is the sharpest available I3 test rather than a separate scenario: a NON_NUMERICAL usage
is also an *excluded* usage, so one fact reaches both paths at the same index. It asserts the
warning renders degraded **and** the exclusion projection still raises. If the fallback ever leaks
into the cache, that test goes green for the wrong reason — noted in the test itself.

**DD-R32 — the tier-2 malformed-literal silence, closed.** Tier 1 sets `saw_non_literal` and the
caller reports a loud deferred skip; tier 2 `continue`d past the same input and returned
`saw_non_literal=False`, so the caller dropped the target with no diagnostic at all. `_resolve_value`
now returns a fourth element, and `ValueResolution`/`ResolvedDemand` carry `malformed_literal`.
Item 1's fall-through is preserved exactly — a malformed literal still must not consume the tiers
below it, and `test_malformed_type_def_literal_does_not_suppress_part_def_literal` stays green;
only a target that resolves to *nothing* is reported.

Two deliberate scoping calls: the flag is **excluded from the `semantic` agreement check**, because
it is a diagnostic signal and not a semantic outcome (contexts that agree on "unresolved" still
agree), and it drains as a **new** log record. The tier-1 aggregate string at
`supplied_values.py` is byte-frozen by the Phase-0 acceptance overlay SHA-256 and is not edited —
`test_tier1_malformed_literal_message_bytes_are_unchanged` pins that it did not move.

### Phase 3 — complete (live route)

**`ModeledDefault` resolver replaces `_literal_float`**, which is deleted (`rg` finds only a
docstring back-reference). Dispositions: `LiteralNode` → value; `UnitAnnotationNode` → recurse and
carry `unit_text`; unary `+`/`-` `OperatorNode` → fold the sign over the recursive result;
everything else → unresolved carrying its node `kind`. Sign folding and unit unwrapping compose
(`-2.5 [W]` resolves). Absent IR is unresolved **without** a node kind — an absence is not an
unsupported node.

`mint` now takes a `ModeledDefault` rather than a bare float, so there is one contract for the
call site rather than a float plus two side fields. `EntryPoint` gains `unit_text` and
`unresolved_default_kind`; `generate_all_derived_jsons` emits a key for **every** entry point, with
`null` where there is no value (DD-R21, I7). DD-R22's diagnostic fires at the mint site, naming the
entry-point QN and the IR kind.

**New fixture** `tests/fixtures/modeled_default_fidelity/` covers all three shapes end-to-end:
`-0.1` → `-0.1`, `40.0 [W]` → `40.0` with `unit_text="W"`, and `2.0 + 3.0` → explicitly unresolved,
diagnosed, `null` in the JSON. Its PROVENANCE records an authoring trap worth keeping: a constraint
actual binds **positionally**, so each definition lists its bound formal first and its defaulted
formal second.

**DD-A13, the lane boundary the design left open — settled by measurement.**
`ParameterGroupDeriver.design_attribute_default_value` and `producer_resolution._modeled_default`
were the same bare-`float()` lane over two different QN-keyed indexes. They collapse to one
`design_attribute_float_default(attr)`; the indexes differ legitimately, the parsing did not, and
the duplicate is deleted rather than wrapped.

`_parse_default_value` **stays, and its asymmetry is now justified rather than inherited.** The
design's condition was to confirm the captured string never carries a sign or a unit. Both halves
of the evidence: measured across all 34 committed fixtures, 531 captured defaults parse as float,
**zero** signed and **zero** unit-bracketed (the 138 non-parsing values are feature references like
`split.half`, a different shape that resolves through the computed-attribute path); and
mechanically, the AST lane that produces the string routes operator expressions through
`evaluate_true_static_expression` at `parameter_groups.py:239`, folding signs and stripping units
*before* capture. So it reads a genuinely different input — a captured string for which no IR
exists — and does not cut over.

**Forced difference, pinned before regeneration and verified after.** The `EntryPoint` field
addition emits two new `null` keys on every entry point in every baseline
(`exclude_none=False`). Regenerated once: **9 computation graphs, 184 entry points, and the diff is
exactly `+unit_text: null`, `+unresolved_default_kind: null` and the trailing comma on
`python_type` — zero value movement, zero key movement.** No pipeline YAML changed (the YAML does
not serialize these fields), and no committed `inputs/*.json` exists to churn.

**Two baselines deliberately not regenerated**, both recorded rather than silently skipped:
`constraint_inline` (the capture script fails on it with a pre-existing constraint name-safety
violation that reproduces at the predecessor) and `plant_values` (pre-existing stale drift, excluded
in Phase 1 for the same reason). `sample_model` regenerated to no change — it has no entry points.

### Validation at the Phase 2+3 exit

Suite **3025 passed / 0 failed**, zero `no live syside license` skips. `PYTHONOPTIMIZE=1`: same,
except the two `assert`-under-`-O` tests that fail identically at the predecessor (re-confirmed by
stash). mypy **72 errors before and after — zero added**. ruff clean on `src/` and every file
touched.

**Phase 4 not started**, per instruction.

---
**Next Step:** owner ratification of the surfaced B2/D4 amendment and the revised Gate 1 pin, then
the Phase 1 regeneration and artifact corrections, then Phase 2.
