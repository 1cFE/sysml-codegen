# Design Review: Lifecycle Item 4 — Diagnostic Severity and Modeled-Default Fidelity

**Design:** `.project/active/constraint-lifecycle-diagnostics-defaults/design.md`
**Spec:** `.project/active/constraint-lifecycle-diagnostics-defaults/spec.md`
**Brief:** `.project/active/constraint-lifecycle-diagnostics-defaults/briefs/design.md`
**Review File:** `.project/active/constraint-lifecycle-diagnostics-defaults/design-review.md`
**Date:** 2026-07-19
**Reviewer:** independent session; no authoring context. Every claim below was checked against
working-tree code in both repos (`/home/reid/1cfe/sysml-codegen`, `/home/reid/1cfe/agentic-mbse`).

---

## Fundamental Assessment

**Sound, with one falsified mechanism claim.**

The approach is right and the design earns most of its length. DD-B1 is settled correctly and for
the right reason — I re-derived the snapshot-route argument from the code and it holds (see
Dimension 7). Severity-as-a-construction-time-value is the correct shape; the two-sink decision
resists the routing layer the spec named as a Non-Goal; the warning fix is correctly localized to
the pre-pass because `_raise_on_blocking` genuinely does read raw locations; and the phase order
(carry before schema) is the right call for exactly the diff-isolation reason D8 gives. This is not
an over-engineered design. Nothing in it is abstraction for its own sake.

**But Phase 1's mechanism rests on a claim that is false in code, and Phase 1's safety gate is the
wrong instrument for the risk.**

D5 asserts that supplying `target_qn` explicitly "holds every existing row's input constant, so row
16 is the only form that newly fires." It does not. Only row 17 reads `target_qn`; eighteen of the
twenty-one `KEY_FORMS` rows read `req.reference` directly — including the entire CHANNEL tier, which
runs *before* the DESIGN_ATTRIBUTE tier row 16 lives in (C1a). Separately, supplying `instance_path`
at all wakes two dormant CHANNEL rows the calc consumer has never reached (C1b). And Gate 3 proposes
to verify safety by a subset check over `fallback_entry_points` — which is blind to the failure that
actually matters here, a binding migrating from tier 2 to tier 1 and re-wiring the graph while
leaving that set byte-identical (C2).

These are three views of one thing: **the design reasons about the resolver ladder structurally, and
the ladder does not behave the way the structural argument assumes.** The repair is correspondingly
one thing — a dedicated request field for the written name, plus a per-binding resolution probe that
replaces set-membership as Phase 1's gate.

I am **not** recommending Rework. The scope of the problem is Phase 1's mechanism and gate; DD-B1,
the severity architecture, the warning fix, the default resolver, and the phase ordering all stand
and were independently verified. But this is more than an editorial pass, and round 2 should check
the repair rather than rubber-stamp it.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every one of the spec's 20 acceptance cells is claimed by a phase exit, and the mapping is real —
I checked each cell against the phase that claims it. Provenance is carried faithfully: the design
does not harden any `[INFERRED]` spec item into a fixed constraint, and it correctly treats DD-B1
(explicitly challengeable) as something it must argue rather than inherit. The `[OWNER]`
qualitative-simplicity item is honored — no LOC accounting appears anywhere, and "Named deletions"
is the right instrument.

Two compliance gaps:

**M1 — DD-A11 cannot be earned in a codegen-only phase.** The design puts the signed/unit fixtures
in Phase 3, listed as codegen-only, and mitigates licence risk with "Sequenced last so a licence
problem cannot block the four codegen-only phases." That mitigation is false. Across all 34
committed snapshots there are **zero `unit` IR nodes**, and every constraint-formal default is a
plain `LiteralNode` (verified: node kinds present are `operator` 21, `package` 12, `literal` 10).
Unit-annotated defaults exist in fixture *source* (`tests/fixtures/catf_mfe_model/designs/catf_mfe/
shield.sysml:75,106,130` and ~12 more) but never reach the default lane. DD-A11 requires **both
public routes** — the snapshot route needs a captured fixture, which needs the SysIDE licence. So
Phase 3 has a licence dependency the design denies it has, and the unit/sign branches would
otherwise ship with no offline test data.

**m1 — DD-A04's "structured result" claim is under-specified against the type.** `ValidationIssue`
(`agentic-mbse/src/agentic_mbse/sysml/types.py:146-177`) carries `location: str` — a preformatted
`file:line` string, not a structured location. D3 adds `reason_code` and that satisfies DD-R10, but
DD-A04 also asks that the truncation not drop the code from the structured result; the design should
say which object is "the structured result" here, since the L6 return type is what a consumer
branches on.

### 2. Pattern Consistency
**Assessment:** Pass

The design composes with what exists rather than inventing. `KEY_FORMS` untouched (modulo C1),
`_raise_on_blocking` untouched, `EntryPoint` extended not replaced, the `ModeledDefault` resolver
explicitly modeled on the shape `predicate_compiler.py:156-171,191-193` already implements for the
predicate lane. The "Kept lanes, each with its stated distinct input" table is the right answer to
DD-R23 and it is honest about leaving one boundary open with DD-A13 as the instrument.

One note, not a finding: D9's `_upstream_pins` would be the first single-sourcing of its kind, and
the evidence cited for drift (`predicate_compiler.py:150,201` saying `executable-profile/v3`) is
real but weaker than the design implies — those are **error-message strings only**, nothing keys off
them. The actual guard at `constraint_lowering.py:476` is correct and current at v4. D9 is still the
right call; the argument should rest on `loader.py:777,:782` (real `RuntimeError` guards, hand-copied
literals) rather than on cosmetic message drift.

### 3. Abstraction Quality
**Assessment:** Pass

`ModeledDefault` earns its existence: `float | None` cannot express "unresolved, and here is the node
kind that stopped it," which is precisely what DD-R21/DD-R22 require. Two optional fields on
`EntryPoint` beat a parallel structure. `DiagnosticSeverity` as a shared *type* with per-writer
tables — rather than a merged diagnostic class — is the correct reading of "one typed
representation," and D1's rejection of folding `force` into it is right: `"non_numerical"` is not a
severity.

The Core Concept section does real work. "One writer-side classification, serialized once, read by
nobody" is a mental model a reader can hold, and the follow-on paragraph makes the rest fall out
from it.

### 4. Duplication Avoidance
**Assessment:** Concerns

Named deletions are specific and verifiable by `rg`, which is the right bar. But the consolidation
is narrower than the design implies.

**m2 — the resolver unifies one of three string lanes, not the family.** `_literal_float` is the IR
lane. `parameter_groups._parse_default_value:820` and `producer_resolution._modeled_default:519` each
do their own bare `float()` over a captured string and would **still** diverge on a signed or
unit-annotated string after Phase 3. The design deletes `parameter_groups.design_attribute_default_value`
and `producer_resolution._modeled_default` — good — but `_parse_default_value:820` is explicitly
kept, and it is a bare-`float()` lane that will silently return `None` for `"-0.1"`-adjacent forms
the IR lane now handles. Either state why that asymmetry is safe (the captured-string input never
carries a sign or unit) or cut it over too. As written, DD-R23's "no second representation" is
arguable.

### 5. Data Structure Clarity
**Assessment:** Concerns

`ModeledDefault` is clean and its invariant (`value is None ⇔ unresolved`) is stated. The
`ExtractionDiagnosticFact` shape and the closed-frozenset `kind` are clear.

**M2 — two new `EntryPoint` fields are a wider serialized-surface change than the design accounts
for.** `EntryPoint` is a Pydantic `BaseModel` (`resolution/models.py:56`) and it is serialized
verbatim into `entry_point_groups` in **12 committed baselines** at
`tests/fixtures/baseline_outputs/*/computation_graph.json`. Those dump with `exclude_none=False`
(proved by `"source_calc_usage": null` appearing in `plant_values`), so two optional fields emit two
new null keys on **every entry point in all 12 baselines** — compared by at least seven test modules.
The null-not-omitted change at `generation/entry_point.py:272-273` rewrites the emitted
`inputs/*.json` templates as a second, independent churn.

The design's whole diff-isolation story (D8, Gate 1, "baselines regenerate **once**") covers the
carry's 22 moved keys in Phase 1 and says nothing about this. Phase 3 forces a second, much broader
baseline regeneration touching every entry point in every baseline. That is not a violation of Gate
1 as written, but it defeats Gate 1's purpose unless Phase 3 gets its own named forced-difference
pin. Add one.

### 6. Route Safety
**Assessment:** Fail

**C1 (Critical) — D5's "holds every existing row's input constant" is false.**

Verified in `src/sysml_codegen/resolution/producer_resolution.py`:

- The ladder driver (`:542`) walks `Tier.CHANNEL` rows **first**, then `Tier.DESIGN_ATTRIBUTE`.
  Row 16 is a DESIGN_ATTRIBUTE row (`:453`); rows 1–15 are all CHANNEL (`:437-452`).
- Only row 17 `_target_qn` reads `req.target_qn` (`:371`). **Eighteen rows read `req.reference`
  directly** — `:203,211,216,222,230,235,239,241,248,250,256,258,264,266,274,280,282,298,329,360,
  366,379,393,395,404,406,416,418`.

So changing `reference` from the resolved referent QN (`SharedProducer::the_rig::scaler::gain`) to
the written simple name (`gain`) mutates the input to almost the whole ladder, and mutates it for
rows that run **before** row 16. Concrete consequences:

- Row 11 `_sysml_qn` (`:274`) does `sanitize_qualified_name(req.reference)`. Today that yields
  `SharedProducer__the_rig__scaler__gain` and probes the channel registry. Under the change it
  probes `gain`. Different answer.
- Row 21 `_bare_name_unique` (`:416-418`) guards `if "." in req.reference or "::" in req.reference:
  return _MISS`. Today a `::`-form reference **always** misses this row. Under `reference="gain"`
  the row becomes live and performs a unique-bare-name lookup across all design attributes, with a
  tie path. This row is exactly the kind that could newly resolve — or newly tie — for the 22
  bindings.
- Row 18 `_owner_def_qn` (`:379`) builds `{owner_def_qn}__{reference}`. Different answer.

Because the CHANNEL tier runs first, a mutated `reference` can make a calc binding newly resolve to
a **module output** rather than an entry point. That is a wiring change, not an identity rename, and
it is a different failure class than the one Gate 2 was designed around.

Scale of the exposure, measured across all committed snapshots: **249 bound bindings, 167 of them
carrying a `::`-qualified `source_path`** (e.g. `DeepCrossScopeProducer::'Core Metric'::metric_value`)
and 82 dotted. All 167 hand a `::` QN to rows 1–15 today. The change cuts both ways — rows 1–10 and
14–15 build scoped/alias keys from dotted paths, so a `::` QN near-certainly misses them today while
a written dotted name is a plausible hit (resolutions migrating *up* from tier 2 to tier 1), and row
11 moves the other way (a binding resolving there today loses its key when `reference` becomes
`gain`). Row 11 is live, not theoretical: FORMULA outputs register under `sysml_qn_lookup` and
resolve through it (`tests/conformance/test_output_registry.py:110-125`,
`tests/conformance/test_agg_key_forms.py:80-83`).

**C1(b) — supplying `instance_path` alone independently perturbs the ladder.** This is a second
mechanism, and it survives the obvious repair to C1(a). Rows 12 `_direct_channel` (`:280`) and 13
`_chain_redefinition_follow` (`:329`) both guard `if "." not in req.reference or not
req.instance_path: return _MISS`. The calc-binding request passes `instance_path=None` today
(`dependency_backtracker.py:577-586`), so **both rows are dead from this consumer**. Supplying it
wakes them — at CHANNEL tier, ahead of every design-attribute row. A binding that resolves today at
row 17 as a `DESIGN_ATTRIBUTE` could newly resolve at row 12 as a `MODULE_OUTPUT`
(`producer_resolution.py:554-559`). That is a graph re-wire: different outcome kind, different
identity. Not a rename, and not something the design anticipates anywhere.

**The repair, both parts.** For C1(a), D5 correctly diagnoses that "rows other than 16 read
`reference` expecting a QN" — that is why it rejects passing the written name as `reference` alone.
The conclusion drawn from that diagnosis is the error: adding `target_qn` does not neutralize it,
because row 16 does not read `target_qn` either. Carry the written name as its **own** request field
(e.g. `ProducerRequest.written_reference`, defaulting to `None`) read by row 16 and only row 16.
Cost: one optional field plus one line inside `_occurrence_materialized_qn`, which softens the
design's "`KEY_FORMS` itself is unchanged" claim to "the table and every other row's function are
unchanged." Far better than mutating the input to eighteen rows.

C1(b) has no equally clean structural fix, because row 16 genuinely needs `instance_path` and rows
12/13 legitimately read the same field. The options are to gate rows 12/13 on something the calc
consumer does not supply, or to accept the activation and **prove empirically that it changes
nothing** — which requires the probe in Recommendation 2b, not the Gate 1 table.

**Two knock-on corrections this forces:**
- Gate 2's stated structural reason ("`target_qn` being passed explicitly is the structural reason it
  should not happen") is void as written. Under the repair it becomes true again.
- Gate 1's predicted new-key form `{instance_path}__{written_name}` is only guaranteed under the
  repair. Without it, a binding could resolve via row 21 or a CHANNEL row instead, producing a key
  the table does not predict.

**C2 (Critical) — Gate 3's vacuity subset argument is narrower than stated, and set size is the
wrong instrument.**

Two of the design's three supporting facts check out. Row 16 cannot starve later rows: `_hit(None)`
returns the same `_MISS` tuple (`:196-197`) and the driver `continue`s on `identity is None`
(`:541-553`) — no row can return a definitive negative, so there is no poisoning path. And the
single population site is real: `dependency_backtracker.py:603` is the **only** write to
`fallback_entry_points` (init at `:263,:298`; read-and-copy at `:391`, `graph_builder.py:446`,
`constraint_lowering.py:1503`; reads at `graph_builder.py:835,875`).

The claim that fails is the generalization. "Resolved keys leave, none enter" is sound **for the 22
self-named bindings** — they are already fallback members by construction (they reach `_terminal_miss`
today), so for that population resolution can only be a net departure. It does **not** hold for the
change as a whole, because C1(a) and C1(b) each perturb the ladder for the other ~227 bindings, and
the design's Gate 3 evidence ("post-change membership is a subset of pre-change membership, and every
remaining member is calc-EQN-shaped") cannot detect the failure mode that matters.

Concretely: a binding migrating from tier 2 to tier 1 — row 17 `DESIGN_ATTRIBUTE` → row 12
`MODULE_OUTPUT` — **leaves `fallback_entry_points` unchanged in both size and shape while re-wiring
the graph.** A subset check over a set of keys is blind to it. This is the same trap
`tests/conformance/test_snapshot_generation.py:216-218` already warns about in this repo: verify
channel identity, not merely that the set emptied. (Project memory `multihop-expose-offline-parity`
records the same lesson from a prior item.)

The honest restatement is: *no self-named binding newly enters the fallback set.* Anything stronger
needs the per-binding probe in Recommendation 2b. Fix C1 and C2's residual is measurable; without
the probe it stays unproven either way.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

**B1 / DD-B1 — verified, and the argument is stronger than the design claims.** Every load-bearing
citation checks out:
- Codegen imports `agentic_mbse` directly with an editable path override (`pyproject.toml:23-27`,
  `:64-65`), so the single-sourcing claim is correct and the strong form of the alternative is the
  one the design beat.
- Live route `pipeline_builder.py:764` vs snapshot route `loader.py:637` → `constraint_facts.parse`
  at `:793`: two different commits by construction. Correct.
- Both gates are exact string/int equality and fail closed in **both** directions with no ordering
  comparison anywhere: `constraint_facts.py:323-334`, `loader.py:718-731`. Correct.
- Reclassification-under-a-map really would silently change blocking behavior for on-disk bytes.
  Confirmed by construction: nothing in the snapshot records severity, so a map change is invisible
  to the data.
- The residual-honesty item is exactly right: `ExtractionDiagnosticFact` has **one producer**
  (`constraint_extraction.py:365-372`) and **zero consumers**. I grepped both repos; every
  `.diagnostics` read hits a different type (`AggregationDiagnostic`, `EligibilityDiagnostic`, syside
  load diagnostics, contract-verify). The claim is exact.

Stating what the field does *not* buy (unrecognized `kind` fails closed either way) is the kind of
self-limiting honesty that makes the rest credible. This section is the design's strongest.

**B2 — verified true.** `serializer.py:239` iterates `dataclasses.fields()` then appends the computed
properties at `:246-250`; `BindingInfo.source_attribute_name` is a `@property` at
`usage_extractor.py:87-92` over the `source_attribute_elem` field; the loader's
`_deserialize_binding_info` (`:1022-1035`) never reads the key back. D4's reasoning for keeping the
property (a plain field would add a second key to every snapshot) is correct and is what makes the
"works on unmodified v3" claim true.

**B3 — the gate is the right instrument, but C1/C2 widen what it must catch.** Gate 2's value-change
stop rule is concrete enough to act on ("`default carried` differs, or `numeric result` differs →
stop"). But under C1 a binding can re-wire to a module output while still producing the same numeric
result on a given fixture — **passing Gate 2 while having changed the graph.** Gate 2 needs a third
column that closes this: *did the resolution's `key_form` or `outcome` change?* That column is free
once the Recommendation 2b probe exists, since the probe produces exactly those tuples.

**Hidden bet, unstated — H1: that one shared helper can produce the same `instance_path` for both
consumers in general.** The design flags the parity question honestly, which I credit, but it
under-states the difficulty and its Phase 0 exit is too weak.

Measured: the constraint side's `owner_instance_path` comes from four different owner-expansion
paths (`constraint_lowering.py:711-722`). For a `part_def` owner it is `occ.instance_path` from
`part_instance_index.py:262-270` — a package-rooted `__`-path that **carries `[i]` occurrence
brackets** (e.g. `InstanceIndexProbe__root__bank__member[0]`). A calc usage QN never has brackets.
For the `PartUsage`-owned case it is `sanitize_qualified_name(owner_qn)`.

`_get_parent_part_for_usage` (`dependency_backtracker.py:523-531`) returns `segments[-2]` — a **bare
single segment** (`the_rig`), not a path, and it is wired to `parent_scope` (`:583`), not
`instance_path`. The calc request passes no `instance_path` at all today.

So: for `shared_producer` specifically, the two notions **can** be made equal — the constraint side
yields `SharedProducer__the_rig` and the calc side can get there with
`usage.qualified_name.rsplit("__", 1)[0]`. Cheap and correct for that fixture. **But the design's
Phase 0 exit is "prove equality on `shared_producer`," and `shared_producer` is a non-occurrence-
indexed `PartUsage`-owned case — the one shape where the two derivations coincide by accident.**
Proving equality there does not establish the general claim, and the occurrence-indexed shape is
where it demonstrably fails.

Recommendation: Phase 0's exit should be "equality on `shared_producer` **and** a stated disposition
for the occurrence-indexed shape" — either the helper reproduces brackets on the calc side, or the
design states that row 16 is expected to miss for bracketed owners and that missing is safe (which,
given `_hit(None) → _MISS`, it is). Say which, rather than leaving it to a single-fixture probe.

**m3 — B4 is under-tested by the phases.** B4 says no production caller depends on a fall-through
entry-point key by name. The Gate 1 table records moved keys but the design does not say how B4
itself is falsified — the natural instrument is a grep of `tests/` and generated `inputs/*.json` for
the 22 old keys. Name it.

### 8. Reader Comprehension
**Assessment:** Pass

A reader can get the model. "One writer-side classification, serialized once, read by nobody" is a
real frame, and the Core Concept paragraph that follows it does the work of connecting all four
fronts to that one idea. The DD-B1 section leads with the conclusion, gives the one measured
asymmetry, and states the counter-claim it does not get to make. Gates 1–4 are each one idea with a
named instrument. Phase exits name their cells.

Two small comprehension costs, both worth fixing because they cost a reader a lookup:

- **The load-bearing-assumption paragraph buries its own conclusion.** It opens with mechanism
  (which line supplies what) and reaches "the calc consumer must supply the same notion" three
  sentences in. Lead with the question.
- **Citation drift** — a reader who follows these lands in the wrong place:
  - `constraint_lowering.py:1095,:1245` are cited as supplying `usage_qn` as an instance path. They
    are not instance-path supply sites at all; both are `usage_qualified_name=usage_qn` on the
    `ConcreteConstraint` record. The nearby instance-path sites are `:1074,:1088,:1145` (minting).
  - `serializer.py:248-251` for the property append → actually `:246-250`.
  - `level6_architecture.py:607-610` → `facts` is assigned at `:610` and consumed at `:611`; `:607-609`
    is a comment.
  - `cli/__init__.py:263,:278` for the V11 gate → `:263` is an import-list entry, `:278` is the
    collector call, and the actual `raise CodeGenerationError(f"V11: ...")` is at `:280-284`.
  - `usage_extractor.py:55-100` → `BindingInfo` is `:54-93`, property at `:87-92`.

---

## Issues by Severity

### Critical
- **C1(a) — D5's "holds every existing row's input constant" is false.** Only row 17 reads
  `target_qn`; eighteen rows read `reference` directly, and the CHANNEL tier runs before row 16.
  Mutating `reference` to the written name changes the input for all 167 `::`-form bindings across
  the fixtures, can re-wire bindings to module outputs (row 11), and newly activates row 21.
  Repair: carry the written name as its own `ProducerRequest` field read only by row 16.
  — Dimension 6
- **C1(b) — supplying `instance_path` independently wakes two dormant CHANNEL rows.** Rows 12 and 13
  gate on `req.instance_path`, which the calc consumer passes as `None` today. Supplying it activates
  them at tier 1, ahead of every design-attribute row, so a row-17 `DESIGN_ATTRIBUTE` resolution can
  become a row-12 `MODULE_OUTPUT`. This survives the C1(a) repair and needs empirical proof, not a
  structural argument. — Dimension 6
- **C2 — Gate 3's vacuity subset argument does not generalize, and set membership is the wrong
  instrument.** True only for the 22 self-named bindings (already fallback members, can only leave).
  A tier-2 → tier-1 migration re-wires the graph while leaving `fallback_entry_points` identical in
  size and shape, so the stated subset evidence is blind to it. — Dimension 6

### Major
- **M1 — Phase 3 has an undeclared licence dependency.** Zero `unit` IR nodes and only literal
  defaults exist across all 34 snapshots, so DD-A11's snapshot route needs a new licensed capture.
  The stated risk mitigation ("four codegen-only phases" insulated from licence risk) is false as
  written. — Dimension 1
- **M2 — Phase 3's baseline churn is unnamed and much wider than Phase 1's.** Two optional
  `EntryPoint` fields emit two new null keys on every entry point in 12 committed baselines
  (`exclude_none=False`, proved by `"source_calc_usage": null`), and the null-not-omitted change
  rewrites `inputs/*.json` again. Gate 1's "regenerate once, one cause per diff" needs a Phase 3
  analogue. — Dimension 5
- **H1 — hidden bet: one shared `instance_path` helper works for both consumers *in general*.**
  True for `shared_producer` (`PartUsage`-owned, unbracketed); false for occurrence-indexed
  `part_def` owners, whose `instance_path` carries `[i]` brackets a calc usage QN never has. Phase
  0's single-fixture exit cannot detect this. — Dimension 7

### Minor
- **m1 — DD-A04's "structured result" is not pinned to an object.** `ValidationIssue.location` is a
  preformatted string; say which return type the code must survive in. — Dimension 1
- **m2 — `_parse_default_value:820` stays a bare-`float()` lane** and will still diverge from the IR
  lane on signed/unit strings. State why that is safe or cut it over. — Dimension 4
- **m3 — B4 has no named falsification instrument.** A grep of `tests/` and generated `inputs/*.json`
  for the 22 old keys is the obvious one. — Dimension 7
- **m4 — D9's drift evidence is cosmetic.** `predicate_compiler.py:150,201` are error-message strings
  with nothing keying off them; the real guards are `loader.py:777,:782`. Rest the argument there.
  — Dimension 2
- **m5 — five citation drifts** (listed in Dimension 8). — Dimension 8

### Surfaced, out of scope — recorded, not assigned
While verifying DD-R32 I found the *mirror* defect one tier up: a malformed tier-1 literal sets
`saw_non_literal = True` (`supplied_values.py:230`) and `_resolve_value` returns early at `:264-265`,
**suppressing tiers 2a and 2b entirely** — which is precisely the bug Item 1 deliberately fixed
*within* tier 2 (see the rationale comment at `:281-285`). DD-R32 scopes this item to tier-2 silence
only, so this is not Item 4's. Recording it so it is not lost.

---

## Verified Clean (no action)

Stated explicitly so the design agent does not re-litigate these:

- **DD-B1 and all three consequences.** Argument verified end to end; see Dimension 7.
- **Both skew directions, both routes, both gates fail closed.** Exact equality, no ordering
  comparison, gate runs before any field deserialization. `constraint_facts.py:323-334`,
  `loader.py:718-731`.
- **Item 12 interaction is safe and correctly stated.** `grandfathered_off` is a *lowering-mode*
  carve-out validated at `loader.py:765-772` with its behavior in `graph_rebuild.py:228-236`. It has
  no interaction with the version gate, which runs first at `:718-731` on the raw envelope before
  `constraint_lowering_mode` is even read at `:739`. A grandfathered snapshot **cannot** bypass the
  bump. No second grandfathering route is introduced. DD-R15/DD-A20 hold.
- **v3-vs-v4 reconciliation is coherent.** D8's ordering is what makes both claims true at once: the
  carry lands in Phase 1 against unmodified v3 (D4 keeps the wire form identical), and v3 snapshots
  are uniformly rejected only from Phase 4/5. No contradiction.
- **Gate 3's two supporting facts, but not its conclusion.** The single population site is confirmed
  by repo-wide grep (`dependency_backtracker.py:603` is the only write), and `_hit(None) → _MISS`
  means row 16 cannot starve later rows. The conclusion drawn from them is over-general — see C2.
- **Gate 4 is buildable and RED-first is achievable.** No test asserts the current state — the only
  test-tree reference to the fixture anywhere is `tests/conformance/conftest.py:59` (comment) and
  `:62` (registration). PROVENANCE.md:57's "a test asserts it" is false, as the spec says. Both
  current entry points are known and nameable (`SharedProducer__the_rig__gain` DESIGN_ATTRIBUTE;
  `SharedProducer__the_rig__scaler__gain` USAGE_LITERAL), corroborated by
  `.project/active/constraint-lifecycle-gate-b/decision.md:181-185`. Default 40.0 confirmed at
  `model.sysml:41`.
- **Gate 1's ordering is correct as phrased.** Phase 1 produces the table from the probe, then
  regenerates once. Probe-before-regeneration is genuinely ordered that way.
- **I3 is aimed at a real trap, and the trap is exactly as described.** `location_cache` (`:678`) is
  written solely by the `projected_location` closure at `:689`, read at `:681` and — the load-bearing
  part — by the exclusion path at `:709`. Warnings at `:692` populate the cache the exclusion path
  later reads. A fallback written into that cache would make `:709` read a degraded value instead of
  raising. I3 names precisely the right thing and DD-A09 is the right test.
- **The warning fix is correctly localized.** `_raise_on_blocking` (`:553-575`) builds its location
  from raw `decision.location.file` at `:562`, never consults the projector, and takes no
  `projected_location` parameter. The asymmetry the design rests on is real.
- **Phases 1 and 2 are genuinely codegen-only.** Two same-named `BindingInfo` classes exist; the
  carry touches the **codegen** one (`usage_extractor.py:55`, disambiguated by an explicit comment at
  `dependency_backtracker.py:30-32`). Phase 2's location handling is entirely codegen-local types.
- **Phase 3 needs no agentic-mbse schema change.** `UnitAnnotationNode` and `OperatorNode` are
  already defined (`expression_ir.py:86`, `:51-130`), already in the union at `:130`, already
  exported, and already emitted by the parser at `:266`. The Phase 3 dependency is empirical
  (M1: no committed fixture exercises them), not structural.
- **34 snapshots confirmed** by count.
- **REASON_CODES: 27, unenforced in production** — confirmed; the only check is a subset assertion
  over answer-key values at `test_executable_profile_matrix.py:71-74`, and the `I3` invariant claimed
  in its own docstring at `executable_profile.py:61` is unenforced. DD-R05 is well-founded.

---

## Recommendations

1. **Repair C1(a) before anything else.** Add `written_reference` (or equivalent) to
   `ProducerRequest`, read only by `_occurrence_materialized_qn`. Leave `reference` untouched. Then
   restate D5's rejected alternative to say why a dedicated field beats both "written name as
   `reference`" and "`reference` + `target_qn`", and restore Gate 2's structural rationale on that
   basis.
2. **Add the per-binding resolution probe, and make it Phase 1's real gate (closes C1(b) and C2).**
   Resolve every binding in every fixture under both request shapes and diff the tuple
   `(outcome, identity, key_form)` per binding — not the size or shape of `fallback_entry_points`,
   which is provably blind to a tier-2 → tier-1 migration. Any binding whose `outcome` or `key_form`
   changes to anything other than row 16 is a stop under Gate 2. This probe subsumes the Gate 1
   table (it produces the old/new key columns for free) and is the only instrument that can prove
   C1(b) benign. Order it before baseline regeneration, as Gate 1 already requires.
2b. **Strengthen Phase 0's exit for H1.** "Equality on `shared_producer`" is not enough — that
   fixture is the `PartUsage`-owned, unbracketed shape where the two derivations coincide by
   accident. Add a stated disposition for the occurrence-indexed (`[i]`-bracketed) owner shape.
   Given `_hit(None) → _MISS`, "row 16 misses for bracketed owners and that is safe" is very likely
   the right answer; the design should state it rather than discover it.
3. **Fix Phase 3's licence claim (M1)** and move the new signed/unit fixtures' capture into the
   licensed sequence — or state that DD-A11's snapshot route rides Phase 5 and say so in the cell
   mapping. Do not leave the "four codegen-only phases" mitigation standing as written.
4. **Add a Phase 3 forced-difference pin (M2)** covering the `EntryPoint`-field null-key churn across
   12 baselines and the `inputs/*.json` rewrite, so Gate 1's one-cause-per-diff discipline survives
   past Phase 1.
5. **Sweep the five citation drifts (m5)** and re-lead the load-bearing-assumption paragraph with its
   question. Cheap, and these are the citations a reviewer and implementer will actually follow.
6. Address m1–m4 inline; none needs a structural change.

---

## Round 2 — verification of the revised design

Narrow re-verification against the revised `design.md` (664 lines). Everything below was re-checked
in code; nothing was taken from the round-1 pass or from the author's account of the revision.

### 1. The C1(a)/C1(b)/C2 repair — structurally sound, with one gap the repair itself opens

**The two-field repair works, and it is better than what I recommended.** I recommended one field
plus an empirical proof for C1(b); two fields turn C1(b) from something the probe must disprove into
something that cannot happen. Verified:

- `req.instance_path` is read at **exactly three rows** — 12 (`:280,:283`), 13 (`:329,:354`), 16
  (`:364,:366`). No other row and no other tier touches it.
- Row 12 is **not** `lenient_only`; row 13 **is** (`:450`). So the design's stated reason for the
  constraint side continuing to supply `instance_path` — "row 12 is admissible under STRICT and
  reads it" — is exactly right.
- Once row 16 stops reading `instance_path`, and the calc consumer continues never to set it, rows
  12 and 13 are **provably dead from that consumer**. Confirmed: `dependency_backtracker.py:578` is
  the calc consumer's only `ProducerRequest` and it passes no `instance_path=` kwarg.
- **Constraint-side byte-identity is stronger than the design claims.** There is exactly **one**
  constraint-side `ProducerRequest` builder (`constraint_lowering.py:174`, `instance_path=
  usage_qualified_name` at `:181`). All of `:1174/:1197/:1221` funnel through it. So
  `occurrence_owner_path` and `instance_path` come from the same parameter in the same expression —
  identity holds by construction, not by matching two call sites. The design can state this more
  cheaply than it does.
- New fields read at one site (I9): sound as a design commitment; nothing in current code contradicts
  it.

**C3 (blocking, mechanical) — the repair silently disables row 16 for the three `graph_builder`
consumers.**

The parity argument covers the constraint consumer only. There are **five** `ProducerRequest`
builders, not two. The other three are in `graph_builder.py` — `:1369` (LocalTerm), `:1606` (EXPOSE
alias), `:1629` (aggregation LocalTerm pre-mint lookup) — and **all three supply `instance_path`
(`:1374`, `:1611`, `:1634`) and run `TerminalPolicy.LENIENT`**, so every row including 16 is
admissible for them. Row 16 is live for these consumers today.

Moving row 16's inputs to two fields that only the constraint and calc consumers set makes row 16
**unreachable** for all three. The site at `:1629` is the sharp case — its own comment reads:

> *"Ask the shared table before minting: a plain literal-valued attribute on the aggregating part def
> is a real design attribute, and this path used to ignore that and mint a defaultless entry point
> with no diagnostic at all."*

It passes `reference=l_term.attribute_name` (a bare name) and `instance_path=agg.instance_path` —
precisely row 16's `{instance_path}__{bare_name}` shape. Disabling row 16 there plausibly reverts the
exact defect that comment records, and a binding that stops resolving falls to a lenient terminal
miss and **newly enters `fallback_entry_points`** — the C2 failure mode running in reverse.

**Fix, one line:** have row 16 read `req.occurrence_owner_path or req.instance_path`. This preserves
every current reader byte-identically, adds the calc consumer, and keeps rows 12/13 dead for the calc
consumer (which still never sets `instance_path`). It does not reintroduce C1(a) (`reference` is
untouched) or C1(b) (the calc consumer still supplies no `instance_path`). I9 survives unchanged —
the new fields are still read at exactly one row. The alternative — having the three `graph_builder`
sites pass `occurrence_owner_path=<their current instance_path>` — also works but touches three call
sites to achieve the same thing.

**Gate 3's probe scope needs one sentence.** The probe is specified over "every bound binding in
every committed fixture — 249 bound bindings." Aggregation and LocalTerm resolutions are not
bindings, so as scoped the probe would **not** catch C3. Either widen it to every `resolve_producer`
call across all five builders, or state that the three `graph_builder` consumers' inputs are
unchanged and why. With the one-line fix, the latter becomes true and cheap.

**Gates 2 and 3 otherwise verified.** Gate 2's second clause (`outcome` or `key_form` moved to
anything other than row 16) is the right widening and closes B3. Gate 3 correctly replaces set
membership, states the surviving Item-3 claim at the strength it actually holds ("no self-named
binding newly enters"), and cites the in-repo precedent — I confirmed
`tests/conformance/test_snapshot_generation.py:215-222` carries the CHANNEL-IDENTITY warning quoted.
Gate 3b closes m3.

### 2. M1 — resolved

DD-A11's snapshot route moved to Phase 5 (`:562-564`, `:581-582`, `:598`) with the licence dependency
declared and its cause named (zero `unit` IR nodes in any committed snapshot). The false insulation
claim is replaced by an accurate one at `:620-622`: "Licence risk is real for Phases 3 and 5, not
just Phase 5." Phase 3's exit correctly claims only DD-A11's live route.

### 3. M2 — resolved

Second forced-difference pin named separately at `:568-574`, with the mechanism correct
(`exclude_none=False`, two null keys × every entry point × 12 baselines) and the `inputs/*.json`
churn carried as a distinct cause. Gate 1's one-cause-per-diff discipline now extends past Phase 1.

### 4. Bracket disposition — honestly labeled

This is the item I checked hardest, since partial coverage is where a design is most tempted to
overclaim. It is clean:

- The disposition is stated as a decision, not discovered by a probe (`:404-409`), with the
  safe-miss mechanism correctly grounded in `_hit(None) → _MISS` (`:196-197`) and the driver's
  `continue` on `identity is None` (`:541-553`).
- "Deliberate partial coverage, not silent partial coverage" is the right framing, and the scope
  limit is stated in the same breath as the claim: convergence "closes for the unbracketed shape and
  is **explicitly not claimed** for the bracketed one."
- The stop condition is genuinely falsifiable — any bracketed binding whose resolution tuple moves
  *at all* is a stop, not just a wrong hit (`:411-415`).
- Phase 0's exit is two checks (`:417-420`), and the second is the bracketed-owner fixture proving a
  miss, which is what the single-fixture exit could not have caught.
- The design credits the measurement to the review and flags that it could not independently
  disconfirm the bracket claim (`:401-402`) — appropriate, and the disposition is safe either way.

Checked for overclaim elsewhere: B4 (`:140`), the Gate 1 table (`:334`), I5 (`:440`), and the risk
entry (`:617-619`) all restate the scope limit rather than reverting to an unqualified convergence
claim. Success-criterion SR-A02 is carried as closing on `shared_producer`, which is the unbracketed
shape — consistent. **No unlabeled convergence claim found.**

### 5. m1–m5 and verified-clean sections

- **m1 — resolved, well.** DD-A04's structured result is pinned to a named object: "`QualityCheckResult.issues`
  — the list of `ValidationIssue` the L6 check returns" (`:172-176`), with `ValidationIssue.location`
  explicitly left a preformatted string and terminal rendering explicitly out.
- **m2 — resolved as a stated open item.** The `_parse_default_value` asymmetry is acknowledged at
  `:485-488` (DD-R23's "no second representation" is "only" conditionally true) and the cutover
  question is carried into the handoff under DD-A13 (`:651`). Acceptable — it is now visible rather
  than assumed safe.
- **m3 — resolved.** Gate 3b (`:369-370`).
- **m4 — resolved.** D9's case now rests on the two real `RuntimeError` guards at `loader.py:777,:782`
  (`:206`), with the cosmetic message drift demoted.
- **m5 — all five corrected.** `serializer.py:246-250` (`:128`, `:181`), `usage_extractor.py:87-92`
  (`:129`), `level6_architecture.py:610-611` (`:166`, `:462`), `cli/__init__.py:278` raising at
  `:280-284` (`:367`, `:628`). The `constraint_lowering.py:1095/:1245` mis-citation is gone; the
  owner-path section now cites `:1174,:1197,:1221` and the four expansion paths at `:709-722`.
- **Verified-clean sections: untouched and still accurate.** Re-spot-checked DD-B1's argument and
  consequences (`:71-76`), the I2 both-directions claim, the Item 12 non-interaction, and Gate 4's
  RED-first construction. No drift, no quiet weakening, nothing added that would need re-verifying.

### Round-2 verdict

**Approve-with-notes.**

The repair is correct in its structure and in every claim I could check, and it improved on the
recommendation rather than merely complying with it. M1, M2, m1–m5 and the bracket disposition are
resolved. C2's replacement gate is the right instrument and is honestly scoped.

**C3 is the one must-fix**, and it is mechanical: add the `or req.instance_path` fallback in row 16
and widen Gate 3's probe scope by one sentence. I am not calling this Needs-rework because the fix
is fully specified, touches one expression, and does not disturb any argument the revised design
makes. It must land in implement, not be deferred to a gate — Gate 3 as currently scoped would not
catch it.

---

## Resolutions

*Empty — to be filled when the owner engages with this review. The reviewer does not edit the
design.*

---

**Overall (round 2, final):** Approve-with-notes — one must-fix (C3), specified exactly. The
round-1 verdict and findings below are retained as the record of what was raised; see the Round 2
section above for their dispositions.

**Overall (round 1, superseded):** Approve-with-revisions

The foundation is sound and DD-B1 — the thing the brief said to settle first — is settled correctly,
with evidence that survives independent re-derivation. Recommendations 1, 2, 2b, 3 and 4 are
**mandatory before implement**: C1(a) is a falsified mechanism claim at the heart of Phase 1, C1(b)
is an unanticipated second perturbation of the same ladder, C2 means Phase 1's stated safety gate
cannot see the failure it exists to catch, and M1/M2/H1 each break a guarantee the design explicitly
makes. Recommendations 5–6 are non-blocking.

Read the verdict as: *the design is approved everywhere except Phase 1's carry mechanism and its
gate, which need a real amendment.*

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. Max-two-round discipline: this is round 1, and
the round-2 check should be scoped to the C1/C2 repair (dedicated written-name field + per-binding
resolution probe as Gate 1/2/3's shared instrument), Phase 0's strengthened parity exit, and the two
Phase 3 corrections — not a re-review of the whole design.
