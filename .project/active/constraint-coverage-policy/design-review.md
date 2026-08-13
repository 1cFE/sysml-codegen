# Design Review: Coverage Report and TEAx Policy (CONSTRAINT-SEMANTICS Item 3)

**Design:** `.project/active/constraint-coverage-policy/design.md`
**Spec:** `.project/active/constraint-coverage-policy/spec.md`
**Review File:** `.project/active/constraint-coverage-policy/design-review.md`
**Date:** 2026-08-12
**Reviewed at:** codegen `328032e` (branch `item7-rebuild`), TEAx `fa0e06a` (clean `main`, read-only)

---

## The Point

A design search is only useful if it can tell a candidate that passed its physics gates from a
candidate nobody checked. Today it cannot. A generated package reports `all_satisfied` when two of
nine authored gates were assessed, and TEAx labels a model with 65 unassessed checks
`unconstrained` — the same label a genuinely constraint-free model gets. The obligation is
owner-graded at its root:

> **[OWNER-VERBATIM]** (2026-08-12) "when we started this whole cleanup, it was while defining a
> policy around how to use constraints to enforce things like physics in a way that make our overall
> 'design search' viable"

and the rule that follows is **[INHERITED]**: no report and no study label may claim more coverage
than was assessed.

Item 1 fixed what each state means. Item 2 made the embedded catalog own the complete authored-usage
domain. Item 3 builds the consumer: a report that states its coverage, a vocabulary in both places
that can say "partial", and a study policy that keeps a partially-covered candidate out of the
search's steering loop.

---

## Fundamental Assessment

**Sound — with a specification gap that has to close before the plan.**

This is the right piece of work and the right approach. The two moves that carry it are both correct
and both cheap:

- **Coverage is a baked generation-time constant, derived from the sealed catalog.** It rides the
  rail `CATALOG_FINGERPRINT` and `EXPECTED_IDS` already ride (`generation/modules.py:353-380`,
  verified). No new mechanism, no second reader of the catalog inside the generated package, no
  per-candidate recomputation of a per-model fact.
- **Coverage is a second axis, not a slot in the headline.** The account is emitted in every report
  whatever the headline says, and because TEAx's evidence artifact already stores the whole report
  tree (`evaluation/evidence.py:87-90`, verified), it reaches the durable case record for free. That
  is the orchestrator-ratified two-axes ruling implemented rather than restated.

I could not find a simpler design that satisfies the spec. The obvious cheaper alternatives are both
worse and the design rejects both with reasons that hold: flat fields on `ConstraintReport` (loses
the "hand coverage over as one thing" property TEAx needs), and computing the account in the
aggregator at runtime (the catalog lives in `contracts/model_contract.json`, outside the importable
path — verified).

**One-authority holds.** The coverage block is six counts plus a reason histogram, addressed to the
catalog by the fingerprint the report already carries. It carries no per-usage rows. It is a summary,
not a second inventory. Invariant 48 is respected.

**Smell 7 does not fire.** No invariant changes owner silently. Three ownership moves happen here and
all three are stated in the open: coverage truth moves from a runtime observation to a
generation-time constant (Core Concept and D3, with B2 stating it as a falsifiable bet);
`expects_report` authority moves from `concrete_entries` to `usage_records` (D7, which the design
raised as its own finding); and `ships_constraint_machinery` changes what it says while D5 explicitly
preserves where it lives.

**Smell 2 fires, and it escalates into this judgment.** *"Does this package ship a constraint
report"* is a producer rule — codegen decides it in `ships_constraint_machinery` and mints the
aggregator accordingly. TEAx answers the same question twice more on its own. D7 moves one of those
two consumer-side derivations and never names the other (DR-2, verified: `evaluator.py:79-87`, whose
own docstring says *"The study layer overrides this with the catalog authority; the two must
agree"*). The design's own `design-F1` is the record of exactly this duplication going wrong once
already, one layer in; D7 repairs that instance by re-syncing a copy rather than by removing the
duplication, and leaves its sibling unexamined. Note that inside codegen the design applies the right
standard to the identical hazard — D5 makes the two readings of the report-required rule a preflight
check because *"two readings of one rule is the drift A4 exists to stop"*. The finding is that the
standard stops at the repo boundary.

This does **not** force Rework. The finding is agent-graded (invariant 48 and Item 2's A4 cure, both
agent/ratified) — no owner-graded statement is contradicted, and the owner-verbatim D-3 prohibition
is on QN/predicate-text reconstruction and consumer-side materializers, which reading a row count is
not. But it is the first thing the design should fix, and the fix it needs is the one the design
already knows how to write.

**Product-lens ledger gate: DISPOSED** (`design_review-F1..F3`, appended to
`.project/active/constraint-coverage-policy/product-lens.md`). Nothing blocks. `F1` is carried here
as DR-2, `F3` as DR-13; `F2` sharpened DR-3 and is folded into DR-1.

**What stops this from being Approve.** D3 is the load-bearing decision and it is named, not
specified. It gives the output shape, the arithmetic identities, and where the function lives — but
never the rules that map a `ConstraintCatalogUsageRecord` to a bucket. That gap is not pedantic: one
reachable record shape breaks the identities the design does state (DR-4), and the one place D2 does
publish a concrete set it publishes seven of the landed nine tokens with no criterion for telling
oversight from exclusion (DR-3). Everything downstream — B1's hand-written expected accounts, the
preflight recomputation, the D4 ruling, D6's precedence — rests on rules that are not written down.
Close DR-1..DR-6 and this is a strong design.

---

## Premise Verification

Every load-bearing claim the brief named was checked first-hand this session.

**Confirmed as the design states.**

| Claim | Verdict |
|---|---|
| `CANONICAL_HEADLINE` at `evaluation/evidence.py:44`, four tokens | ✅ (design's correction of the spec's `projection.py` cite is right — projection only imports it) |
| `ResponseEntry` (`evidence.py:40`) does two jobs: per-constraint status and aggregate headline | ✅ |
| TWO bare-subscript dispatch tables: `policy.py:32-37` and `:76-80`, subscripted at `:70` and `:135` | ✅ exactly as stated |
| `projection.py:59` bare subscript, `KeyError` today | ✅ |
| `unconstrained` produced by *absence* of a headline key (`policy.py:65-68`, `:112-116`) | ✅ |
| `expects_report = bool(load_model_contract(...).concrete_entries)` at `study/cli.py:42` | ✅ — and `ModelContractData` already carries `usage_records` (`study/model_contract.py:36`), so D7's authority move is a one-word change |
| `ACCEPTED_CATALOG_SCHEMA_VERSIONS = {"2.0.0"}`, `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = {"1.0.0"}`, `TRUSTED_VERIFIER_SHA256` at `package_load.py:33/39/47` | ✅ — the fail-closed window is indeed already open |
| `_freeze` (`evidence.py:17-28`) recurses mappings and sequences | ✅ — a nested `coverage` block needs a test, not a mechanism |
| `PolicyConfig` is a `StrictBaseModel`, digested whole into `StudyConfig.semantic_fingerprint()`, which becomes `study_definition_fingerprint` in `Compatibility` (`config.py:139`) | ✅ — flipping the opt-in really does start a new lineage |
| Eight-field `Compatibility`, `IncompatibleStore` on rebind | ✅ |
| Only `study.db` files in the TEAx tree are two archived spike work dirs | ✅ — B4's factual half holds; the open question resolves to "no store worth keeping" |
| Exit-ancestor retention already structural (`generation/pipeline.py:284-296`) | ✅ |
| `render_report_aggregator` already bakes `catalog_fingerprint` / `EXPECTED_IDS` | ✅ |
| `ships_constraint_machinery` one home, three seams | ✅ |
| The four `all_satisfied` assertions | ✅ at `test_constraint_verdicts_exact_route.py:171,416,540` and `test_fusion_tea_real_teax.py:245` (whole-dump) |
| D8's checkout-order inversion: codegen's venv imports `simkit` from the TEAx working tree | ✅ — `/home/reid/1cfe/item7-rebuild-venv/bin/python -c "import simkit"` resolves to `/home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py`. The order inversion is forced, exactly as D8 says. |
| D4's contract cites | ✅ — Appendix C's vacuous-gate cell and state 5's unconditional text both read as quoted |

**Contradicted or over-claimed.** See DR-4 (the invariant-50 carrier) and DR-6 (D3's third check).

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every success criterion has a design element, and the ones that were hardest to get right are right.

- The two-axes ruling is **implemented**, not restated: D6 emits the account whatever arm fired, and
  D2 carries `coverage_state` on the block so the coverage axis survives a higher-precedence
  headline. SC2's "violation + non-full coverage" case is pinned in Validation item 2.
- The two-tier `[INFERRED]` rule is honoured properly. `assessed_gate_count` (usage tier, new) beside
  `assessed_entry_count` (occurrence tier, renamed) satisfies the spec's "distinct in the field
  names, not only in the prose" — and paying the rename is the right call given the schema bump is
  already being paid.
- **D4 is published as a ruling with reasoning, against the contract, which is what the spec's
  "Surfaced, not resolved" required.** I checked both cites first-hand. Appendix C's cell really is
  conditional on survivors ("…the headline reads full satisfaction **when every remaining gate
  passed**"), and state 5's test really is unconditional ("the model has constraint usages but no
  applicable asserted gate at all"). Reading a vacuous conditional as an entitlement *is* the weaker
  inference, and awarding the strongest token in the vocabulary for zero assessments would be
  today's defect in new clothes. The ruling is correct, its reasoning is sound, and its
  contract-amendment consequence is filed rather than performed. Endorsed as written.
- **The token choice is right and its blast radius is genuinely fully designed.** I swept both repos.
  `all_satisfied` appears in exactly four codegen source/test files (the two templates and the two
  test modules the design names), in TEAx only in `CANONICAL_HEADLINE` plus archived spike work
  dirs, and in **no committed baseline** — `tests/fixtures/baseline_outputs/*` holds only
  `registry_init.py` and `computation_graph.json`, neither of which carries a headline token. The
  one remaining mention, `docs/architecture/modeling-assumptions.md:551-554`, is ADR-009's frozen
  "what the contract said" quotation and must *not* move. The design's enumeration is complete.
  Rejecting both umbrella-offered spellings is inside design's authority (the umbrella deferred the
  choice rather than narrowing it to two) and the reason given — "partial was never a kind of
  satisfaction; what is partial is the denominator" — is the right reason.
- Invariant 50's route is resolved by verified fact rather than assumption, which is the correct
  posture. The **conclusion** survives review; the **stated mechanism** does not (DR-4).

Capture fidelity: the `[OWNER-VERBATIM]` quote is carried whole at the owner's emphasis; the
`[NEED]` sequencing instruction is honoured explicitly in D8 step 1 including the prohibition on
reverse-engineering the fusion expectation; no challengeable spec item is silently hardened.

Concerns: DR-1 through DR-6, and DR-13 (invariant 46's persist/harvest clause is carried by
mechanism and pinned by no Validation item).

### 2. Pattern Consistency
**Assessment:** Pass

Every mechanism this design reaches for already exists in the tree and is used the way the tree uses
it: baking constants into the aggregator template, a sixth preflight beside five, one rule in one
home read by three seams, versioned-and-re-vendored cross-repo constants, fail-closed lookups beside
`CorruptConstraintEvidence`. `UnknownHeadlineToken` deliberately not being an `AssessmentFailed` is
the right distinction and matches the reasoning already recorded on `CorruptConstraintEvidence`
(`evidence.py:31-37`): a token the runtime cannot map means the runtime does not understand the
package, which must stop the run rather than record a healthy-looking case.

No new pattern is invented. Deletion-over-shims is respected in D8 (TEAx **replaces** rather than
extends both vendored sets) — with one lapse, DR-7.

### 3. Abstraction Quality
**Assessment:** Concerns

`CoverageAccount` as a nested model earns its existence: it is the unit TEAx hands to a case record,
and six loose ints on `ConstraintReport` would read as peers of `headline` and `results`. One pure
function in `generation/coverage.py` is the right granularity — license-free, unit-testable against a
hand-built catalog, one derivation.

The concern is not the shape, it is that the function is a name with no contents (DR-1).

One boundary question the design should answer while it is in D3: `ships_constraint_report` is a
producer fact that TEAx currently reconstructs twice (DR-2). Stating it once in the model contract
and having both TEAx sites read it would remove the duplication instead of re-syncing it. That is a
larger change than DR-2's minimum fix and may belong to a later item — but the design should say
which it is choosing, rather than leaving the second derivation unmentioned.

### 4. Duplication Avoidance
**Assessment:** Pass

This is the dimension I pushed hardest on and the design holds. Per-usage detail exists in exactly
one place. The report carries a compact summary addressed to that place by fingerprint. TEAx
re-derives nothing — `study/query.py`'s `_EmbeddedCatalog` still reads the contract, not the report.
The one place a second reading could creep in — `project.py`'s early return versus the generation
seams — the design closes as a **preflight check** rather than a convention (D5), which is the right
instinct: an agreement a machine checks is not duplication, an agreement a human maintains is.

### 5. Data Structure Clarity
**Assessment:** Concerns

Field names are good and the two-tier disambiguation is exactly right. Types are explicit; the
histogram is `dict[str, int]` over a closed token set rather than a free-form map, which is the right
call — and the design's claim that Item 2's reason tokens are unique across kinds is **true**
(verified against `DISPOSITION_REASONS`, `elaboration/graph.py:259-278`), so no compound key is
needed.

But the design never states which usage record lands in which bucket, and the closed key set it does
publish is incomplete. See DR-1 and DR-3.

### 6. Route Safety
**Assessment:** Concerns

Both dispatch tables are treated, which is the thing most likely to have been half-done: the design
found the second table (`_HEADLINE_DISPOSITION`, the real study path) that the spec's second-hand
cite did not distinguish, and fixes both subscripts. Verified that both exist and both are bare. The
report side keeps a closed `Literal` so pydantic refuses an unknown token at construction. Unknown
tokens never fall through to a satisfied or unconstrained reading. Invariant 46a is discharged on
both sides.

The remaining route concern is D6's precedence reading raw `statuses` with no applicability filter
(DR-2).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The bets are mostly genuine claims about reality with real "if false" consequences. B2 (coverage is a
model property, not a design-point property) is the one the whole baking strategy rests on and it is
plainly true. B3 is a genuine unknown, correctly sized as a one-run probe rather than a spike, and
correctly placed first in the landing order. B5 is a real claim about reader behaviour and is
mitigated by making both sides fail closed.

Three problems:

- **B4's mechanism is wrong even though B4 is true** (DR-4). The design says a catalog/report schema
  move changes `model_contract_fingerprint`. It does not, for the packages that could have a store.
- **B1's mitigation is under-specified in the one way that decides whether it tests B1 at all**
  (DR-5).
- **A hidden bet, and it is false.** The design bets throughout that a usage's disposition and its
  inapplicability marker cannot co-occur in a way that matters. `@inapplicable:` is read off the
  usage's documentation independently of the disposition (`elaborate.py:1184`, `:1189-1200`) and
  Item 2's own docstring says it "never rewrites the disposition beside it." An **eligible** usage
  carrying `@inapplicable:` is reachable, and it breaks D2's arithmetic, D6's precedence, and the
  edges of D4's ruling at once (DR-2).

Decisions are otherwise well-formed: each names its rejected alternative with a reason, and the
rejections are real rather than strawmen (the "one widened type, cheaper and wrong" note in D7 is a
good example — widening `ResponseEntry` would have implied a per-constraint status can be partial).

### 8. Reader Comprehension
**Assessment:** Pass

The design gives the mental model before the mechanism. "The Point" states the problem in two
sentences a tired reader can hold. Core Concept's closing move — *"partial was never a kind of
satisfaction. It is a statement about the denominator"* — is the sentence that makes the rest
obvious, and it is placed where a reader needs it. Every coined term is anchored to a plain
explanation. Research Findings marks its corrections. Nothing hides behind a label.

The one thing a reader cannot get from this document is what the derivation actually computes — but
that is DR-1, a substance finding, not a voice one.

---

## Issues by Severity

### Critical

- **DR-1 — D3's derivation is named, not specified.** The design fixes the output shape, the
  arithmetic identities, the function's home, and its purity, but never states the predicate that
  maps a `ConstraintCatalogUsageRecord` to `applicable_gate_total`, `assessed_gate_count`,
  `unassessed_gate_count`, or `inapplicable_gate_count`. `coverage_account(catalog)` is a signature.
  Everything downstream depends on those rules being settled: B1's hand-written expected accounts
  cannot be hand-written without them, the preflight recomputation has nothing to recompute against,
  D4's ruling ("the precedence function's full-satisfaction arm requires `assessed_gate_count > 0`")
  presumes a definition of assessed that is never given, and D6's arms read fields whose meaning is
  implied rather than stated. That the gap is real and not pedantic is demonstrated by DR-2 and DR-3,
  both of which are reachable record shapes that break the identities the design *does* state.
  **Resolution:** add a bucket table to D3 — one row per (`source_form` class, `disposition_kind`,
  `inapplicability` present?) combination, naming the bucket each lands in, over the closed
  vocabularies in `elaboration/graph.py:244-278`. It is a table of about a dozen rows and it is the
  artifact the plan and the hand-written fixtures both need.

### Major

- **DR-2 — TEAx has two live derivations of "does this package ship a report", and D7 moves only
  one.** This is the fired smell-2 finding, carried from the product lens (`design_review-F1`) and
  verified first-hand. `_report_declared_in_spec` (`evaluation/evaluator.py:79-87`) is the
  `expects_report` default for **both** `PreparedEvaluator` (`:139-143`) and `FileBackedEvaluator`
  (`:243-246`), and its own docstring states the coupling: *"The study layer overrides this with the
  catalog authority; the two must agree."* D7 moves the catalog side (`study/cli.py:42`) from
  `concrete_entries` to `usage_records` and never mentions the spec side.

  The agreement happens to survive — the report channel is pinned as an exit output for every minted
  aggregator (`generation/pipeline.py:284-296`, verified), so a zero-input aggregator does appear in
  the spec and the spec-derived default answers `True` for exactly the packages `usage_records` now
  covers. But that is a load-bearing fact the design does not state, sitting under the invariant-46a
  corruption check (`projection.py:50-55`) that the design's own `design-F1` was raised to keep
  alive. It is `design-F1` one layer out, and the design already knows the right treatment: D5 makes
  the two readings of the report-required rule a preflight check because *"two readings of one rule
  is the drift A4 exists to stop"*. That standard should not stop at the repo boundary.

  **Resolution, minimum:** D7 names `evaluator.py:79-87`, states why the spec-declared report channel
  and non-empty `usage_records` agree, and pins the agreement with a test on a zero-input package.
  **Resolution, better:** the producer states `ships_constraint_report` once in the model contract and
  both TEAx sites read it, removing the duplication instead of re-syncing it. If that is out of scope
  for this item, say so in Non-Goals rather than leaving it unmentioned.

- **DR-3 — D2 publishes a token list where the obligation is a rule, and the list is seven of the
  landed nine.** `DISPOSITION_REASONS` (`elaboration/graph.py:259-278`) holds nine non-`admitted`
  reasons; D2's histogram keys name seven, omitting `out_of_scope_satisfy` and `out_of_profile_owner`.
  On inspection both omissions are **correct**: `out_of_scope_satisfy` fires only for
  `source_form == "satisfy_reference"`, which is not in `ASSERTED_SOURCE_FORMS` (`graph.py:244`), and
  `out_of_profile_owner` fires on `owner_kind == "requirement_def"` (`elaborate.py:1261-1268`) — both
  are the "plain and requirement-side usages are never applicable asserted gates" clause in code. So
  this is not a wrong list. It is a list where a rule belongs.

  The cost is real. An implementer diffing D2 against the enum sees two missing buckets and no way to
  tell exclusion from oversight, and Required Invariant 2's
  `sum(unassessed_reasons.values()) == unassessed_gate_count` validator is what breaks if the call is
  made the other way — a generation-time refusal on a legal model. **Resolution:** state denominator
  membership as a rule over the landed vocabulary (which reasons sit inside the feasibility
  denominator and which are inventory-only) and derive the seven keys from it. This is the same fix
  as DR-1 and should be written as one artifact.

- **DR-4 — an eligible usage carrying an explicit inapplicability marker is reachable and
  unhandled.** `@inapplicable:` is read off the usage's documentation at mint
  (`elaborate.py:1184`, `_read_annotation` at `:1188`) independently of the disposition, and Item 2
  states it "never rewrites the disposition beside it." The contract agrees it is unconditional:
  *"A usage stops being applicable only when it carries an explicit inapplicability disposition"*
  (lifecycle contract, "Headline states and coverage truth"). So an asserted usage whose owner *does*
  expand, which produces concrete entries and real verdicts, can also be inapplicable. Three
  consequences the design does not address:
  1. **The arithmetic breaks.** If it counts in `assessed_gate_count`, then
     `assessed + unassessed == applicable_gate_total` fails, because it is not in
     `applicable_gate_total`. D3's validator turns that into a construction refusal on a legal model.
  2. **D6's top arm fires from a non-applicable gate.** `violated in statuses -> "violation"` reads
     raw runtime statuses with no applicability filter. Contract state 1 requires *"at least one
     **applicable** asserted gate was assessed and failed."* A violated occurrence of an inapplicable
     gate produces a `violation` headline the contract does not license.
  3. **D4's ruling has an unstated edge.** "Every asserted gate dispositioned inapplicable" reads
     `not_assessed` — but if those gates were eligible, the report carries a non-empty `results` list
     and `assessed_entry_count > 0` beside `assessed_gate_count == 0` and headline `not_assessed`.
     Coherent under the two-tier rule, and startling to any reader who has not internalized it.

  **Resolution:** rule on it in D3/D6 the way D4 ruled on its crossing. The likely answer is that
  inapplicability removes the usage from the feasibility denominator *and* its occurrences from the
  headline's status set, with the occurrence-tier `results` list unchanged — but that is a ruling,
  not something to leave to the implementer. If the answer is instead that the combination is
  forbidden at authoring time, that is an Item 2 change and a surfacing event, not a quiet edit.

- **DR-5 — invariant 50's discharge names a carrier that does not fire.** The design's B4 and its
  Research Findings both say: *"A catalog/report schema move changes the fingerprint, so an old store
  cannot be silently rebound."* The fingerprint in `Compatibility.model_contract_fingerprint` is
  codegen's `semantic_fingerprint`, computed over `parameters`, `outputs`, `constraint_catalog`,
  `evaluation_semantics`, and `catalog_schema_version` only (`contracts/model_contract.py:59-70`,
  verified). This item **adds no catalog field** and **keeps `CATALOG_SCHEMA_VERSION` at `3.0.0`**
  (D8, deliberately). For an already-constraint-bearing package whose module/channel set does not
  change, none of those five inputs move — the report's *schema* is not in the payload, and
  `RUNTIME_CONTRACT_VERSION` is not either. So `model_contract_fingerprint` can be byte-identical
  across this item for exactly the packages that could have a store.

  The **conclusion still holds**, and holds robustly, but for two different reasons the design
  states elsewhere without connecting them: `evidence_schema_version` bumps `v1 -> v2` (D7), and it
  is one of the eight bound fields; and `executable_fingerprint` moves because the generated bytes
  move. Both are in `Compatibility`. The store refusal is over-determined.

  This matters because it is the discharge of the spec's owner-visible escape. **Resolution:** state
  the real carrier. Make `evidence_schema_version: v1 -> v2` the *primary* invariant-50 mechanism
  rather than a lineage-legibility nicety, and make Validation item 9 pin the store refusal against
  that field specifically — a test that only varies the model-contract fingerprint could pass today
  and silently stop proving anything.

- **DR-6 — B1's mitigation is under-specified in the one way that decides whether it tests B1.**
  B1 is that Item 2's dispositions are correct, and the design correctly calls it unfalsifiable from
  inside this item. The mitigation is *"the six-state matrix is pinned against **hand-written**
  expected accounts per fixture, never against generated output."* Whether that mitigates B1 depends
  entirely on **what the account is hand-written from**:
  - From each fixture's **SysML source** — reading what the author actually wrote and deciding, by
    the contract's rules, how many gates there are and which were assessed — the account is an
    independent oracle. It falsifies B1 for the covered fixtures. Strong.
  - From **Item 2's disposition table** — reading the catalog's own output and transcribing it into a
    Python literal — the expectation inherits the exact error B1 names. It falsifies nothing. It is
    "never against generated output" in letter and "against generated output" in effect.

  As written the design does not say which, and the second reading is the one an implementer under
  time pressure will take, because it is far easier. **Resolution:** say it in one sentence in
  Potential Risks: expected accounts are derived from the fixture's `.sysml` source and the
  contract's applicability rules, never from a catalog dump, and the fixture source is small enough
  to make that practical. Then B1's mitigation is as strong as the design claims. Note also that
  `catf_mfe_d5` at 65 usages is at the edge of hand-countable — say how that one is counted.

### Minor

- **DR-7 — D3's third check is over-claimed, and is the same shape as the smell.** "Checked from both
  ends" lists runtime verification as comparing the report's `catalog_fingerprint` against the model
  contract's catalog fingerprint. That proves the report and the catalog are the *same catalog*. It
  does not verify the baked account at all — a mis-derived account passes it. The real runtime
  protection is the package seal over the bytes. Worse, it sits inside one sealed, seal-verified
  package, so it can only ever fail on a codegen defect: it is a third consumer-side re-derivation of
  a producer fact, added in the same breath as DR-2's second one. Keep it if it is cheap, but stop
  counting it as one of the "both ends" and do not let it stand in for removing the duplication. One
  smaller note: `ModelContractData` exposes no named catalog-fingerprint field, so the comparison has
  to go through `.raw["constraint_catalog"]["fingerprint"]`.

- **DR-8 — `has_executable_content` becomes dead code, and D5 keeps it.** D5 says it is "retained for
  callers that genuinely mean 'is there anything to execute'". There are none:
  `ships_constraint_machinery` is its only caller in the tree (verified across `src/` and `tests/`),
  and D5 changes that caller's body to `bool(usage_records)`. Retaining a property with no reader for
  a hypothetical future one is the shim this epic's quality bar rejects. Delete it, or name the
  caller that keeps it alive.

- **DR-9 — D7 conflates disposition with case state.** "`DispositionPolicy`'s
  `_DISPOSITION_BY_HEADLINE` maps it to a `partial_coverage` case state." That table's values
  (`feasible` / `infeasible` / `indeterminate` / `not_assessed`) are **dispositions**, surfaced as
  `CaseView.disposition` from `assessment_json` (`study/query.py:130`). `cases.state` is the
  lifecycle state (`completed` / `execution_failed` / `assessment_failed`, `study/runner.py:122-171`)
  and is unaffected. The `cases.state` column has no CHECK constraint, so nothing breaks either way,
  but a plan that reads this literally will go looking for a case-state migration that does not
  exist. Say "disposition".

- **DR-10 — cite drift (trivial, listed so the plan inherits correct pointers).**
  `project.py`'s early return is at `:892`, not `:891`. The catalog row's field is
  `inapplicability_reason` (`resolution/models.py:519`); `inapplicability` is the graph record's
  field (`elaboration/graph.py:318`) — D2's "reading `inapplicability is not None`" should name the
  catalog spelling since that is what `coverage_account(catalog)` sees. `StudyConfig`'s digest is
  built at `config.py:61-73`, not a single `:69`.

- **DR-11 — D5's trigger change alters what all three seams do, and only the rule change is
  described.** Under the new trigger a descriptive-only package (`catf_mfe_d5`, 65 bare constraints,
  zero concrete entries) starts emitting `schemas/constraint_types.py`, starts importing
  `ConstraintEvaluation`/`ConstraintReport` in its registry (`generation/registry.py:353-362`), and
  starts running the constraint-name-safety preflight (`cli/__init__.py:404-414`) over an empty
  entry set. All three are correct — the package now genuinely ships a report — but the design names
  the rule change without naming the per-seam consequence, and one of those seams also carries a
  redundant `catalog is not None and …` guard at `cli/__init__.py:411` that the plan should
  collapse. Also worth noting for baseline expectations: `tests/fixtures/baseline_outputs/*` holds
  only `registry_init.py` and `computation_graph.json`, so the churn is narrower than "every
  constraint-bearing baseline regenerates" suggests — the fixtures that gain an aggregator churn in
  both files, the rest do not churn at all.

- **DR-12 — name the surprising-but-correct corner.** Under D4 (and more so under DR-2's resolution)
  a report can carry `assessed_entry_count > 0` and a non-empty `results` list beside
  `assessed_gate_count == 0` and headline `not_assessed`. That is the two-tier rule working
  correctly. It will still read as a bug to the first person who sees it. One sentence in D2 or D4
  saying so, and one test asserting it deliberately, costs almost nothing and saves a future
  investigation.


- **DR-13 — invariant 46's persist/harvest clause is carried by mechanism and pinned by nothing.**
  Carried from the lens (`design_review-F3`) and verified. The contract requires the file-backed
  route to carry the coverage accounting through persistence and harvest unchanged, with no
  consumer-side schema adapter. The mechanism gives it for free — `FileBackedEvaluator` shares the
  same `project(...)` and `encode_evidence` passes the sealed report tree whole
  (`study/evidence_io.py:49-56`, verified). But none of the twelve Validation Approach items names
  the file-backed route or a persist-then-harvest round-trip of `coverage`; the design's TEAx-side
  evidence is entirely `PreparedEvaluator`-shaped. **Resolution:** add the round-trip to Validation,
  or cite the existing prepared/file-backed parity test and state that it already covers the new
  block.

---

## Recommendations

1. **Write the bucket table into D3** (DR-1, and it resolves DR-3 at the same time). One row per
   (`source_form` class, `disposition_kind`, inapplicability present?) over the closed vocabularies
   in `elaboration/graph.py:244-278`, naming the bucket each lands in, and derive D2's seven histogram
   keys from it rather than listing them. This is the single highest-value change in the review: it
   is the artifact the preflight, the validators, the hand-written fixtures, and the plan all need,
   and it is what makes DR-4 visible rather than discovered at implementation.
2. **Name the second `expects_report` derivation and pin the agreement** (DR-2), or state in
   Non-Goals that collapsing it into one producer fact is a later item. This is the fired smell and
   the first thing to fix.
3. **Rule on eligible + inapplicable** (DR-4), in D3 for the accounting and in D6 for whether an
   inapplicable gate's occurrences enter the headline's status set. Publish it as a ruling with
   reasoning, the way D4 is published.
4. **Restate invariant 50's carrier as `evidence_schema_version`** and point Validation item 9 at it
   (DR-5). The conclusion does not change; the mechanism and the test do.
5. **Say what the hand-written accounts are written from** (DR-6). One sentence turns B1's mitigation
   from ambiguous into strong.
6. Sweep the rest: DR-7 (state what the runtime check proves), DR-8 (delete
   `has_executable_content` or name its caller), DR-9 (disposition, not case state), DR-10 (cites),
   DR-11 (per-seam consequences + narrower baseline churn), DR-12 (the two-tier corner), DR-13
   (file-backed round-trip in Validation).

Nothing above asks for a different design. D1, D4, D6, D7's vocabulary split, and D8's landing order
should all land as written.

---

## Resolutions

Recorded 2026-08-12 by the design agent, incorporating into `design.md` **rev 2**. Every finding is
resolved in the design; nothing is deferred. Orchestrator steers on DR-1..DR-6 followed as given.

**Numbering note.** §7 "Bets & Decisions Integrity" cross-references DR-2/DR-4/DR-5 for what "Issues by
Severity" numbers DR-4/DR-5/DR-6, and §6 "Route Safety" cites DR-2 for DR-4's subject. The **Issues by
Severity** numbering is treated as authoritative throughout (it matches the Recommendations list and
the orchestrator's steers). No finding was dropped in the reconciliation.

- **DR-1 (critical) — RESOLVED.** D3 now carries the bucket table: two predicates (**asserted** ≡
  `source_form in ASSERTED_SOURCE_FORMS`; **inapplicable** ≡ `inapplicability_reason is not None`) over
  four exhaustive, mutually exclusive rows — inventory only / inapplicable gate / assessed gate /
  unassessed gate — each naming the fields it contributes to, with the contract clause each row
  implements. Totality is argued explicitly rather than assumed: `disposition_kind` is closed to three
  values by `DISPOSITION_REASONS` and `_preflight_constraint_totality` already refuses an unknown
  kind/reason pair, so the rows cover every record. The one combination that is *not* counted (row 2 ∧
  `eligible`) is stated as a refusal rather than omitted — that is DR-4/D9. `authored_usage_total`
  falls out as the sum. Required Invariant 6 and Validation item 7 (a unit test over hand-built records
  covering every row and every reason token) make the table checkable rather than aspirational, and
  Implementation Notes instructs the plan to implement it as the function's literal structure, not as
  scattered conditionals.

- **DR-2 (major) — RESOLVED by removal, not by re-syncing.** D7 now names both derivations
  (`study/cli.py:42` and `_report_declared_in_spec`, `evaluator.py:79-87`, the default for both
  `PreparedEvaluator` and `FileBackedEvaluator`) and Research Findings records the coupling docstring
  verbatim. The fix takes the review's "better" option and the orchestrator's steer: TEAx gains one
  function, `study/model_contract.py::ships_constraint_report(contract) -> bool(contract.usage_records)`
  — the same population as codegen's D5 trigger — and `_report_declared_in_spec` is **deleted**, with
  `expects_constraint_report` becoming a required constructor argument on both evaluators. The "two must
  agree" docstring becomes a single-authority read. Reasoning recorded: the evaluation layer is
  isolation-clean and genuinely has no catalog authority, so inventing one from the pipeline spec was
  the defect the docstring was papering over. Required Invariant 10 states the one-place rule per repo;
  Validation item 12 pins it on a zero-input package (authority answers `True`, the 46a corruption check
  still fires, no fallback exists to disagree). The fourteen affected test call sites are sized in
  Potential Risks so the plan does not discover them. Nothing is deferred to Non-Goals.

- **DR-3 (major) — RESOLVED.** The seven-token list is gone. D2 now states that histogram keys are
  *derived* from D3's table — a key exists iff some record lands in the unassessed-gate bucket carrying
  that reason — with no zero-filled keys and no list to drift against `DISPOSITION_REASONS`. Which of
  the nine non-`admitted` reasons can appear is a consequence, not an input, so the "seven of nine"
  question dissolves rather than being answered. Per the orchestrator's steer, D3 also states the
  behaviour when Item 2's vocabulary grows: `generation/coverage.py` pins a frozen `KNOWN_REASONS` set
  and compares it against `DISPOSITION_REASONS` **at preflight** — not only when a record happens to
  carry a new token — refusing by name with the instruction that a new cause needs a coverage ruling.
  Required Invariant 6; Validation item 7's second half.

- **DR-4 (major) — RESOLVED by a published ruling, D9, following the orchestrator's steer.** An
  eligible usage carrying `@inapplicable:` is an **authoring contradiction** and refuses generation by
  name at the coverage preflight, before any output is written, naming the usage QN, its
  `declaration_id`, and its entry count. It is never silently dropped from the denominator. Reasoning is
  published with the ruling, led by the risk the steer named: honouring the marker would make an
  annotation a silent kill-switch — one doc comment could remove a failing physics check from the
  feasible set while the headline read `full_satisfaction`, which is the exact defect class this epic
  exists to end. Supporting reasons: it is a *directive* defect and Item 2 already grades those loudly
  (a malformed marker is error-grade, audit A3/R2); inapplicability stays legitimate on every unassessed
  gate (rows 2 and 4), so only the gate that demonstrably ran is refused; and `eligible` ⇔ "produced
  entries" (Item 2 precedence step 3), so no separate occurrence test is needed. Three rejected
  alternatives recorded, including forbidding it at authoring time in Item 2 — declined as the wrong
  layer and a surfacing event, with the companion authoring advisory **filed** as a follow-on (Item 2
  D10's home) rather than built. The refusal also discharges the review's three named consequences at
  once: the arithmetic cannot break, D6's top arm cannot fire from a non-applicable gate (stated in D6
  with contract state 1's "applicable" quoted, and no runtime applicability filter added — a second
  place for the rule), and D4's startling edge becomes unreachable. Required Invariant 9; Validation
  item 6; Potential Risks records that nothing in the tree carries the combination — verified: the
  marker appears in five fixtures and sits on a zero-occurrence `Detached` owner in every one.

- **DR-5 (major) — RESOLVED, mechanism corrected.** The review's premise is confirmed first-hand:
  `semantic_fingerprint` is computed over `parameters`, `outputs`, `constraint_catalog`,
  `evaluation_semantics`, `catalog_schema_version` only (`contracts/model_contract.py:59-70`), and this
  item adds no catalog field and holds `CATALOG_SCHEMA_VERSION` at `3.0.0`, so
  `model_contract_fingerprint` can be byte-identical for exactly the packages that could have a store.
  Research Findings now states this as a rev-1 correction; B4 names `evidence_schema_version` as the
  carrying field; D7's invariant-50 paragraph makes the `v1 -> v2` bump the **primary** mechanism rather
  than a legibility nicety, with `executable_fingerprint` noted as the second, over-determining carrier.
  Validation item 11 pins the refusal against `evidence_schema_version` specifically, with the reason
  spelled out: a test varying only the model-contract fingerprint could pass today and silently stop
  proving anything.

- **DR-6 (major) — RESOLVED.** Potential Risks now states which of the two readings is required, in
  the design's own words rather than by implication: each fixture's expected account is written from
  that fixture's `.sysml` source and D3's bucket table — reading what the author wrote — and **never**
  transcribed from a catalog dump, a generated report, or Item 2's disposition table, because a
  transcription inherits the exact error B1 names and falsifies nothing. B1's bullet points at it so the
  bet and its mitigation are not read separately. The `catf_mfe_d5` question the review asked is
  answered concretely and the answer was run this stage: two greps over the fixture source give
  `assert` = 0 and bare `constraint` = 65, which puts all 65 in bucket 1 and fixes every field of the
  account without counting to 65 by eye — still source-derived, since it reads what the author wrote
  rather than what the catalog concluded. Next-Stage Handoff carries it as an **inherited instruction,
  not a note**, so the plan is bound by it.

- **DR-7 (minor) — RESOLVED by deletion.** The third "check" is removed rather than demoted. D3 now
  reads "checked from both ends" truthfully (generation preflight + construction validators) and records
  why the runtime fingerprint comparison went: it proves the report and the catalog are the same
  catalog and verifies no account; it could only ever fail on a codegen defect inside one seal-verified
  package; and it would have been a third consumer-side re-derivation added in the same breath as DR-2
  removes the second. The package seal is named as the real runtime protection. The
  `.raw["constraint_catalog"]["fingerprint"]` access note is moot with the check gone.

- **DR-8 (minor) — RESOLVED.** `has_executable_content` is deleted, not retained. Verified the review's
  claim first-hand: `ships_constraint_machinery` is its only caller in `src/` and `tests/`. D5 and the
  Component Overview say deleted; the "retained for future callers" sentence is gone.

- **DR-9 (minor) — RESOLVED.** D7 says **disposition**, not case state, and adds the pointer that makes
  it unambiguous for the plan: those values surface as `CaseView.disposition` from `assessment_json`
  (`study/query.py:130`), while the `cases.state` lifecycle column is untouched and needs no migration.

- **DR-10 (minor) — RESOLVED, all three.** `project.py:892` (was `:891`); the catalog spelling
  `inapplicability_reason` (`resolution/models.py:519`) is used everywhere `coverage_account` is
  described, with the graph-record spelling `inapplicability` (`graph.py:318`) distinguished in Research
  Findings; `config.py:61-73` (was `:69`). D3's bucket table uses the catalog spelling in its predicate
  definition, which is the place an implementer will copy from.

- **DR-11 (minor) — RESOLVED.** D5 gains a "What the three seams then do" paragraph naming each
  consequence for a descriptive-only package (`schemas/constraint_types.py` emitted; registry imports
  added; the name-safety preflight running over an empty entry set), states that all three are correct,
  and instructs collapsing the redundant `catalog is not None and …` guard at `cli/__init__.py:411`.
  Implementation Notes replaces rev 1's over-broad "every constraint-bearing baseline regenerates" with
  the accurate account: baselines hold only `registry_init.py` and `computation_graph.json`, so fixtures
  that gain an aggregator churn in both, fixtures already carrying one churn in neither unless their
  channel set moves, and constraint-free fixtures must stay byte-identical.

- **DR-12 (minor) — RESOLVED, and the corner the review named is now unreachable.** D9's refusal means
  an inapplicable gate never produces an entry, so `results` non-empty beside `assessed_gate_count == 0`
  cannot occur; Required Invariant 9 states the property and D2 says so explicitly rather than leaving a
  reader to infer it. The *genuine* two-tier asymmetry that remains — one gate over many occurrences,
  `assessed_gate_count = 1` beside `assessed_entry_count = n` — is named in D2 and pinned by Validation
  item 16, asserted deliberately so it is not later "fixed".

- **DR-13 (minor) — RESOLVED.** Validation item 13 adds the invariant-46 round-trip: generate, persist,
  and harvest through `FileBackedEvaluator`, asserting the `coverage` block survives byte-equal with no
  consumer-side adapter, homed in TEAx's existing
  `tests/evaluation/test_constraint_evidence_durability.py` (which already covers the prepared/
  file-backed pair). Research Findings records the mechanism that makes it cheap —
  `study/evidence_io.py:47-56` passes the sealed report tree through without a second dump — so the
  test pins a property rather than building one.

**Not changed, per the review's own instruction** ("nothing above asks for a different design"): D1's
token map, D4's ruling and its reasoning, D6's precedence arms, D7's vocabulary split and opt-in
mechanism, and D8's landing order all land as written at rev 1.

---

**Overall:** Revise

**Next Steps:** Once resolutions are recorded here, re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The reviewer does not edit the
design. After incorporation, `/_my_plan` — with DR-1's bucket table as a plan input, and B3's probe
plus the hand-written fusion account still first in the order, as D8 says.
