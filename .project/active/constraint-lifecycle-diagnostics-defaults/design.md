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
(`producer_resolution.py:436-455`) is not touched — row 16 simply becomes reachable from a second
consumer. `_raise_on_blocking` (`constraint_lowering.py:553-576`) is not touched — it already reads
raw locations, so it was never the vulnerable half. `EntryPoint` (`resolution/models.py:56-86`) is
extended by two optional fields rather than replaced.

---

## Key Bets

- **B1 — Severity is a property of the writer, not the reader.** Two readers at different versions
  must never disagree about whether the same bytes block. *If false → the fact-schema bump, the
  envelope bump, and the 34-snapshot re-capture are all cost with no benefit, and DD-B1's cheaper
  alternative should have won.* Settled above with the snapshot-route argument.
- **B2 — `source_attribute_name` on disk equals the written reference the constraint side already
  uses.** The serializer writes the referent's simple name (`serializer.py:248-251`, via the AST
  property `usage_extractor.py:96-100`); the constraint side's `FeatureReferenceFact.source_name`
  is the same notion from the same node class (`expression.py:549-569` returns `referent.name`).
  *If false → the two consumers key differently, SR-A02 does not converge, and the carry needs a
  new extraction field with an agentic-mbse change and a second schema bump.* Phase 1 proves it by
  equality on `shared_producer` before any call site changes.
- **B3 — The 22 newly-resolving self-named bindings are identity movement only, never value
  movement.** All 22 are single-consumer (Item 2 `design.md:141-149`), so no second consumer's
  value is being displaced. *If false → we are silently changing computed results across six
  fixtures under cover of a rename, which is a stop, not a forced difference.* The precedence gate
  in D6 is the instrument that would catch it.
- **B4 — No production caller depends on a fall-through entry-point key by name.** The 22 keys move
  from `{consumer_eqn}__{param_name}` to `{instance_path}__{written_name}`. *If false → generated
  JSON input files that users hand-edit lose their keys, and the movement needs a narrower gate.*
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
  lowering. Authoring: a loop in `level6_architecture.py:607-610`, which already holds `facts`
  between extraction and `evaluate_profile` and needs zero plumbing.
- **D3 — `ValidationIssue` gains one optional `reason_code: str | None` field.** *Rejected: minting a
  `ValidationCode` member per profile reason* (24 members → ~50; the enum is a UI-facing category
  vocabulary, not a diagnostic vocabulary). This is the minimum that makes DD-R10's "a field a
  consumer branches on" true. The two existing L6 constraint codes stay; the reason survives
  alongside the interpolated text rather than only inside it.
- **D4 — The written-reference carry rides a stored fallback behind the existing property, excluded
  from serialization.** *Rejected: converting `source_attribute_name` from a property to a plain
  dataclass field.* The serializer iterates `dataclasses.fields()` (`serializer.py:238-243`) and
  then appends the computed property (`:248-251`), so a new field would add a second key to every
  snapshot. Keeping the wire form identical means the carry works on **unmodified v3 snapshots**,
  which is what lets it land before the schema work (D8).
- **D5 — The calc consumer passes `reference` (written), `target_qn` (resolved QN), and
  `instance_path` together.** *Rejected: passing the written name as `reference` alone.* Rows other
  than 16 read `reference` expecting a QN, and `_target_qn` (`producer_resolution.py:370-373`) falls
  back to `reference` when `target_qn is None`. Supplying `target_qn` explicitly holds every
  existing row's input constant, so row 16 is the only form that newly fires. `KEY_FORMS` itself is
  unchanged. Item 3's vacuity dividing line is preserved by construction — see Invariant I4.
- **D6 — The blast radius is gated by an enumerated forced-difference table with a value-change stop
  rule**, not by baseline regeneration plus review. See "The carry's blast radius" below.
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
  guard. Evidence the current scheme drifts: `predicate_compiler.py:150,201` still say
  `executable-profile/v3` while the profile is at v4.

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

The mechanism is three edits: the loader stops discarding `source_attribute_name`
(`loader.py:1022-1035`), `BindingInfo` carries it behind the existing property
(`usage_extractor.py:55-100`), and `dependency_backtracker.py:577-588` passes it. The consequence is
that row 16 `_occurrence_materialized_qn` (`producer_resolution.py:363-367`), which short-circuits
to `_MISS` today because `instance_path` is never supplied from that call site, starts firing.

**Gate 1 — the forced-difference table.** Before any generated baseline is regenerated, evidence
carries one row per moved entry point across the six fixtures (`fusion_tea`, `solar_battery_model`,
`catf_mfe_model`, `chain_spike_model`, `return_styles`, `expression_binding_probe`), Item 2's
measurement being 22:

| fixture | old key | new key | default carried | param group | numeric result |
|---|---|---|---|---|---|

Old key form is `entry_point_qualified_name` = `{consumer_eqn}__{param_name}`
(`producer_resolution.py:462-475`). New key form is `{instance_path}__{written_name}`. The table is
produced by a probe applying only the plumbing, before call-site behavior is committed — the design
does not pre-enumerate rows it has not measured, and the implement phase must not regenerate
baselines until the table is filled. Baselines regenerate **once**, under that table.

**Gate 2 — the precedence stop rule (brief item 4).** If any of the rows shows a changed *value* —
`default carried` differs, or `numeric result` differs — that is a **stop**, not a rename. The
change is reverted and the design is amended. A positive written-name resolution overriding a
differently-sourced existing behavior is the failure this gate exists to catch; `target_qn` being
passed explicitly (D5) is the structural reason it should not happen, and the gate is what proves
it did not.

**Gate 3 — Item 3's vacuity dividing line, re-verified after the shrink.** Item 3 proved V11
vacuity by closed enumeration and deleted the extension-time coverage check (`c5cc1b4`;
`.project/active/constraint-lifecycle-gate-b/decision.md`). Membership in `fallback_entry_points`
shrinks here: keys enter it at exactly one site, `dependency_backtracker.py:603`, only on a lenient
terminal miss, and each entering key is `{consumer_eqn}__{param_name}` — calc-EQN-shaped. A key
that now resolves positively through row 16 **leaves** the set rather than entering it under a new
shape, so no design-attribute QN can enter the fallback set. Evidence records that the post-change
membership is a subset of the pre-change membership and that every remaining member is
calc-EQN-shaped. Final-generation V11 (`cli/__init__.py:263,:278`) stays strict and unchanged
(DD-A16).

**Gate 4 — `shared_producer` flips to the convergence proof, RED-first.** No test asserts the
current two-entry-point state — PROVENANCE.md:62's "a test asserts it" is false at HEAD, and the
fixture appears in `tests/` only as a registered snapshot (`tests/conformance/conftest.py:62`). So
the acceptance surface is **newly authored against the current state first**: a test asserting the
two present keys, confirmed green at the predecessor, then rewritten in the same shape to assert
the single converged key `SharedProducer__the_rig__gain` with one modeled default (40.0) and one
group assignment. Both public routes. Without the first step there is no RED and DD-A14 is
unfalsifiable.

**Load-bearing assumption for the reviewer.** The constraint consumer reaches
`SharedProducer__the_rig__gain` by passing `instance_path=owner_instance_path` — the *owning
occurrence path*, not the constraint usage's own EQN (`constraint_lowering.py:1174,:1197,:1221`
supply `owner_instance_path`; `:1095,:1245` supply `usage_qn`). The calc consumer must supply the
same notion. `dependency_backtracker._get_parent_part_for_usage` is the candidate source but is
currently passed as `parent_scope`, and its separator form is unverified. **Implement must make both
consumers derive `instance_path` from one shared helper and prove equality on `shared_producer`
before the call site is committed** (Phase 1 exit). If the two notions cannot be made identical,
that is a surfacing event, not a workaround.

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
- **I5** — Every member of `fallback_entry_points` after the carry is calc-EQN-shaped, and the set
  is a subset of its pre-carry membership.
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
| L6 extraction-diagnostic sink | `agentic_mbse/validation/level6_architecture.py:607-610` | Emits `ValidationIssue`s from `facts.diagnostics`; carries `reason_code` |
| `ValidationIssue.reason_code` | `agentic_mbse/sysml/types.py:146-176` | The branchable field DD-R10 requires |
| warning-local location rendering | `sysml_codegen/analysis/constraint_lowering.py:532-551` | Renders a marked fallback instead of raising; does not touch the strict cache |
| `ModeledDefault` resolver | replaces `_literal_float`, `constraint_lowering.py:1300-1310` | Structural unwrap + sign fold over the IR; explicit unresolved otherwise |
| `EntryPoint` | `sysml_codegen/resolution/models.py:56-86` | Gains `unit_text`, `unresolved_default_kind` |
| `BindingInfo` carry | `sysml_codegen/extraction/usage_extractor.py:55-100`, `snapshot/loader.py:1022-1035` | Stored fallback behind the existing property; wire form unchanged |
| tier-2 malformed collector | `sysml_codegen/resolution/supplied_values.py:267-287,:528-597` | A second collected list drained as a **new** log record |
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
  `AttributeData.default_value`, a string produced by AST extraction, for which no IR exists. Kept.
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

---

## Phased Plan

No `plan.md` — this is the plan. Phases are ordered by what each one de-risks.

**Phase 0 — probes, no production change.** Confirm B2 by equality on `shared_producer`: the
loader-visible `source_attribute_name` equals the constraint side's `FeatureReferenceFact.source_name`
for the shared `gain`. Confirm the `instance_path` parity question (the load-bearing assumption
above) by printing both consumers' candidate values. Confirm whether any committed fixture carries a
unit-annotated or signed modeled default today, which sizes the D7/I6 baseline movement. **Exit:
B2 proven or surfaced.**

**Phase 1 — the carry (codegen only, works on unmodified v3 snapshots).** Loader plumbing,
`BindingInfo` stored fallback, one call site. Author the `shared_producer` RED surface against the
*current* two-key state first, confirm green at `3fbec63`, then flip it. Produce the Gate 1 table
from the probe; apply the Gate 2 stop rule; verify Gate 3 membership. Regenerate the six fixtures'
baselines **once**, under the table. Correct the falsified artifacts (DD-R31) and apply PC-2's
one-line SR-R16 amendment (DD-R33). **Exit: DD-A14, DD-A15, DD-A16, DD-A18 pass; no value moved.**

**Phase 2 — warning totality and BLOCK preservation (codegen only).** The warning-local fallback,
with the `location_cache` trap (I3) as the review focus. Name every moved Item-1-pinned byte
sequence with its reason (DD-A10); DD-R18's other callers proven still strict (DD-A09).
**Exit: DD-A08, DD-A09, DD-A10.**

**Phase 3 — modeled-default fidelity and lane consolidation (codegen only).** The `ModeledDefault`
resolver, `EntryPoint` fields, `null`-not-omitted JSON, the unresolved diagnostic, the lane
deletions, and the tier-2 malformed collector (DD-R32 — a *new* log record; the tier-1 aggregate
string at `supplied_values.py:583-590` is byte-frozen by a Phase-0 acceptance overlay SHA-256 and
must not be edited). New fixtures for `:= -0.1` and `= 40.0 [MW]`. **Exit: DD-A11, DD-A12, DD-A13,
DD-A17.**

**Phase 4 — the coordinated pair (agentic-mbse first).** This is the only phase that touches
agentic-mbse, and it exists because DD-B1 landed on a facts-side change. Severity enum and
writer-side table, closed `kind` vocabulary, `REASON_CODES` enforced at construction,
`ValidationIssue.reason_code`, the L6 sink, `constraint-facts/v2`. Then codegen: envelope v4, the
screening function at both call sites, `_upstream_pins` and its guard test.
**Exit: DD-A01–DD-A05, DD-A07, DD-A20.**

**Phase 5 — licensed re-capture.** All 34 snapshots at v4. Byte-identity gate as a timestamp-only
diff check with `captured_at` churn reverted; only the payload movement Phases 1 and 4 predict is
reviewed, each entry named. Requires `SYSIDE_LICENSE_KEY` from `~/1cfe/agentic-mbse/.env` — export
it explicitly or the suite reads as a false baseline (project memory
`syside-license-key-explicit-env-needed`). **Exit: DD-A06.**

**Phase 6 — evidence and delivery.** DD-A19: the exact new agentic-mbse commit, the codegen commit,
the resolved lock, and the additive-certified status of the Items 1–3 chain since `515e08bb`.
Merge order is load-bearing: agentic-mbse PR #11 before sysml-codegen PR #9 (project memory
`constraint-exec-v3-pr-wave`).

---

## Potential Risks

- **The re-capture hides the identity movement.** Mitigated by D8's ordering: the carry's baseline
  regeneration happens in Phase 1, three phases before the re-capture, so each diff has one cause.
- **The warning fallback leaks into the strict path** via the shared `location_cache`. This is the
  single most likely way to pass every new test and still break DD-R18. I3 names it; DD-A09 tests it.
- **`null` in generated JSON breaks input loading at run time.** Today the key is omitted, which
  fails differently. Phase 0 must establish what the generated schema does with a missing vs null
  field before Phase 3 commits; if `null` fails validation where omission did not, that is a
  behavior change to pin, not to absorb silently.
- **`instance_path` parity turns out to be unreachable.** Then row 16 stays unreachable from the calc
  consumer, SR-A02 does not close by these means, and this is a surfacing event.
- **Re-capture requires a licence and rewrites 34 files.** Sequenced last so a licence problem cannot
  block the four codegen-only phases.

## Integration Strategy

Extends, never reworks, the Items 1–3 seams: Item 1's warning/BLOCK ordering bytes change only where
DD-R16/R17 require it, each named; Item 2's shared resolver gains a second consumer reaching an
existing row with `KEY_FORMS` untouched; Item 3's generation-gate V11 caller is unchanged and its
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
value; `KEY_FORMS` untouched.

**Open, for implement to settle with a stated reason:** which of `extractor._extract_default_value`
and the AST lane survives (DD-A13); the exact fallback rendering string for an unmappable warning
location; whether `unit_text` reaches the generated schema description or only the model.

**De-risk first:** Phase 0's `instance_path` parity check. Everything in Phase 1 rests on it, and it
is the assumption most likely to be wrong.

---
**Next Step:** independent `/_my_design_review` in a fresh session, then `/_my_implement`.
