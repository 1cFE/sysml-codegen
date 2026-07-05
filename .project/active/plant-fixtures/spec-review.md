# Spec Review: Plant-Idiom Conformance Fixtures

**Spec:** `.project/active/plant-fixtures/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/plant-fixtures/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound, with two structural gaps to close before it's the contract.** The spec is
about the right work item: it builds the fixture substrate Items 9–11 need,
captures known-incomplete baselines, and discharges the deferred REQ-CA-09
obligation. The problem framing is accurate — the "0 cross-part refs" evidence
base really is invalid because no fixture models the idiom, and the code claims I
spot-checked (`graph_builder.py:689/700`, the two capture scripts, the snapshot
CLI subcommand) are all true as cited.

Two things keep it from Approve. First, the six-shape enumeration is asserted as
the "full substrate" for Items 9–11 but **misses a shape Item 10's success
criterion explicitly names** (two same-type sibling parts). Second, the
conformance-test and capture requirements lean on Item 7's *collector*, yet the
epic gives Item 8 **no dependency on Item 7** and both are in flight — so if Item 8
lands first, a HARD requirement is unsatisfiable. Both are fixable with targeted
edits; the work item is right. Verdict: **Revise**.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The tiered-capture requirement (spec 161–167) says a
fixture that can't build a graph "fall[s] back to the **extraction-only** capture
path (`_capture_extraction_only` / `EXTRACTION_ONLY_MODELS`)." Those symbols live
in `capture_extraction_snapshots.py`, **not** in `capture_pipeline_baselines.py`.
The pipeline-baseline script (`scripts/capture_pipeline_baselines.py:51`) has a
single `MODELS` dict and **no fallback tier at all** — a fixture either is in
`MODELS` (gets `computation_graph.json` + `registry_init.py`) or it is absent and
gets *no pipeline baseline whatsoever*. So the two "tiers" are not a fallback
inside one script; they are two different scripts, and the extraction-only path
produces only an extraction snapshot. The consequence is material, not cosmetic:
if ife_plant lands in the extraction-only tier (the spec names mechanism B as the
likely trigger), then **success criterion "CURRENT pipeline baselines are captured
and committed for both fixtures" cannot be met for ife_plant**, and the
collector-based conformance assertions (L1-2 / L3-1) have no graph to run against.
The spec should state plainly what the extraction-only outcome *costs* — no
pipeline baseline, no collector assertion, weaker Item 9/10 diff substrate — not
present it as an equivalent tier.

**L1-2 · Direct claim:** Two HARD requirements assume Item 7's collector exists at
implement time: the capture-path bullet (spec 148–152) and the conformance-test
bullet (spec 172–176, "assert the collector reports the *expected* set of
uncovered cross-part inputs"). But the collector is an Item 7 deliverable
(`warning-reconciliation/spec.md` 149–170), the epic dependency graph gives Item 8
**no dependency on Item 7** (`epic_upstream_findings.md:300,452`), and both are in
flight. If Item 8 implements first, the collector does not exist — and the spec's
own Non-Goal forbids writing it ("No `src/` production code changes," spec 156,
195). The collector-based assertion is then doubly blocked. See L3-1 for the fix
framing; flagging here because the spec states the requirement as unconditional
when its precondition is not guaranteed.

**L1-3 · Question to the user:** The self-named-binding trap (shape 6, spec
119–122) is specced on the assumption it produces a "degenerate resolution (binds
to the calc's own parameter)" that captures cleanly as a baseline. But the epic's
own Item 12 out-of-scope list names "**self-named-binding recursion** (register
A-1 vendor note)" (`epic_upstream_findings.md:420`) — i.e. a known syside-level
recursion concern, not a benign degenerate resolve. If `in availability =
availability` triggers syside recursion during *extraction*, snapshot capture
could hang or crash — and because the trap is (by default) co-located inside
ife_plant, it would poison the entire ife_plant snapshot, not just its own shape.
**What is the actual failure mode of the trap under the current syside build — a
finite degenerate resolution, or the recursion the register flags?** The spec
rests shape 6 on the former; the epic implies the latter is at least possible.
This needs to be settled before the trap is co-located (see L3-2).

**L1-4 · Direct claim (minor):** The capture-path bullet (spec 131–134) says the
extraction snapshot is captured via a path where "both call
`snapshot.capture_snapshot`." True for the `snapshot` CLI subcommand
(`cli/__init__.py:547`) and the script's full-`MODELS` path, but the
extraction-only path (`_capture_extraction_only`, `capture_extraction_snapshots.py:66`)
does **not** — it runs `SysMLDataExtractor` directly and skips the full pipeline
context (so no `compilation_results`/CalcUsage auto-impl). Harmless for the
prose's intent, but if ife_plant lands extraction-only (L1-1), its snapshot is
also the thinner kind — worth knowing when judging whether the retyping-works
assertion (which reads virtual CalcUsages from the snapshot) still holds.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** The spec asserts the six shapes give Items 9–11 their
"full substrate" (spec 105), but **Item 10's success criterion requires a shape
the six do not contain**: "Instance-ambiguity case (two same-type sibling parts)
covered by a test" (`epic_upstream_findings.md:370`). Item 10's core machinery is
per-instance binding rewrite through the specialization chain — the exact thing
two same-type siblings exercise and a single retyped part does not. None of the
six shapes guarantees ≥2 same-type sibling instances. Either ife_plant must
include that shape (cleanest — it's the substrate item), or the spec must
explicitly hand it to Item 10 to add. As written the completeness claim is false
against a downstream consumer's own success criterion.

**L2-2 · If-then tradeoff:** Item 9's success criterion is "pre-fills the
plant/driver input JSONs (against WI-015 evidence: previously 2/16 and 0 keys)" —
a *meaningful* pre-fill, ~14 Hawker parameters (`epic_upstream_findings.md:334,340`).
The spec's shape 1 ("generic plant part def with def-declared attributes") sets no
floor on how many def-attribute literals exist, and Open Question 3 defers "how
many subsystems, which attribute names" entirely to implement. **If** the author
produces a minimal fixture with 1–2 def literals, Item 8 passes but Item 9's
pre-fill diff is trivial — you cannot demonstrate a 16-key JSON filling from a
2-key fixture. **If** the intent is a realistic pre-fill demonstration, the spec
should set a richness floor (enough def-attribute literals that Item 9's baseline
diff is non-trivial — the ~14-parameter target is the natural anchor). Right now a
too-thin fixture would satisfy the letter of Item 8 and starve Item 9. Which is
it — is a richness floor a spec-time contract, or genuinely an authoring detail?

**L2-3 · Question to the user:** Granularity. The existing corpus splits into
focused single-shape probes (`chain_override_probe`, `unresolvable_attr_probe`,
`expression_binding_probe`) and realistic multi-part models (`catf_mfe_model`).
This spec bundles four known-incomplete mechanisms (A/C/D + chain B) plus one
working shape (retyping) into one realistic ife_plant model. The upside is the
idiom's *interaction* is what SC-5 is about. The downside lands on the exact goal
of this item — legible baseline diffs: when Item 9 fixes mechanism C, the ife_plant
baseline diff shows C's change amid still-broken A/B/D, noisier than a focused
fixture would be. The spec requires per-shape documentation of correct
vs. known-incomplete (spec 123–127), which mitigates this. **Is one bundled
ife_plant the right granularity, or should mechanisms A/C/D also get minimal
focused probes so each downstream item's diff is isolated to the shape it fixes?**
Not a blocker — a deliberate call worth making at spec time rather than discovering
at Item 9's review.

### Lens 3 — Pipeline Risk

**L3-1 · If-then tradeoff:** (Pairs with L1-2.) The spec's dependency on Item 7's
collector is unstated and order-sensitive. Two paths in this item have different
sensitivities, and the spec conflates them:
- **Baseline capture** (`build_full_graph_from_snapshot` → `computation_graph.json`)
  does **not** invoke the collector — it is order-independent and works whether or
  not Item 7 has landed. Good.
- **The collector-based conformance assertion** ("collector reports exactly
  `[...]`", spec 174–176) needs Item 7's `src/` code to exist.

**If** Item 7 lands before Item 8, everything the spec says works as written.
**If** Item 8 lands first, the collector assertion is unsatisfiable and forbidden
to build (Non-Goal). The spec should make the collector assertion explicitly
conditional — falling back to a plain "graph builds without raising" assertion when
Item 7 hasn't landed — and add a soft sequencing note (schedule Item 7 first if the
collector pin is wanted). Otherwise the implement session hits a HARD requirement
it cannot meet and has no specced escape.

**L3-2 · Question to the user:** The self-named-binding trap's isolation is
deferred to implement (Open Question 4: "whether the trap needs a separate isolated
fixture vs living inside ife_plant"). Given L1-3 (the register flags syside
recursion, not a benign degenerate resolve), the safe default is a **separate
fixture dir** so the trap's failure mode cannot poison ife_plant's snapshot — the
one fixture Items 9–11 all depend on. Deferring the location to implement is only
safe if the failure mode is known-benign. **Should the spec pin the trap to its own
fixture dir by default (reversible if the probe shows it's benign), rather than
defer the decision?** The asymmetry favors isolation: if it's benign, a separate
dir costs nothing; if it recurses, co-location loses all six shapes.

**L3-3 · Rewrite request:** Success criterion "Fixture models pass agentic-mbse
validation (or failures are understood and recorded)" (spec 71–74) sits in tension
with the fixtures' whole purpose. The fixtures **deliberately exceed the supported
subset** (spec 253), and agentic-mbse's job is to *catch* exactly those shapes —
the mechanism-D trap is explicitly the negative fixture for the agentic-mbse
Level-2 self-named-binding check (spec 232–234). So agentic-mbse validation
*should* flag the traps; that is success, not failure. As worded, "pass" invites an
implement session to either treat an expected flag as a blocker or, worse, "fix"
the fixture to pass — violating the Non-Goal against altering the shapes. The
criterion needs to distinguish two things the spec currently merges: (a) SysML
well-formedness / parse validity, which the fixtures **must** pass; (b)
supported-subset conformance, where the deliberately-unsupported shapes are
**expected** to be flagged and that flag is recorded, not fixed. Name which checks
are the bar.

**L3-4 · Question to the user:** REQ-CA-09 discharge allows a second deferral —
"recorded finding … deferring the reworded-warning test to Items 10/11" (spec
67–70, 177–183). Item 1 already deferred this test once (to Item 8). This spec
permits deferring it again. The chain closes only if Items 10/11 actually pick it
up — Item 11's scope says "the WI-014 toy from Item 8 covers shape A"
(`epic_upstream_findings.md:387`), which suggests it does. **Confirm Items 10/11
explicitly own the reworded-warning test if Item 8 defers it**, so this doesn't
become a third silent punt. The probe-gating itself (which warning fires is a live
probe) is sound and correctly specced.

**L3-5 · Question to the user (minor):** agentic-mbse validation executability
(spec 187–191) names "the agentic-mbse checking scripts (`~/1cfe/agentic-mbse`)"
but no specific entry point / command. Given the repo is sandbox-blocked from the
spec session, the spec can't enumerate — but should it at least direct the
implement session to *identify the checking entry point from the agentic-mbse repo*
and name it, rather than leaving "run the scripts" undefined? Otherwise the SC is
hard to execute deterministically.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** Fixture naming diverges from the corpus
convention for full models. The multi-part model fixtures carry a `_model` suffix
on the snapshot dir and a bare name on the baseline dir
(`capture_pipeline_baselines.py:52`: `"catf_mfe": "catf_mfe_model"`,
`"solar_battery": "solar_battery_model"`, `retype_model`). The spec names the
fixtures `tests/fixtures/wi014_toy/` and `tests/fixtures/ife_plant/` — bare, like
the probes. ife_plant is a full multi-subsystem model, closer to the `_model`
cohort. Not wrong (convention is genuinely mixed — `return_styles`,
`alias_agg_probe` are bare), but the plan will need to pick baseline-dir vs
snapshot-dir names for the two `MODELS` dicts anyway; worth deciding the naming
against the `X`/`X_model` split now rather than at capture time.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The "Capture path (the V11 / non-strict interaction)"
section (spec 129–167) is the hardest part of the spec to hold in one read. It
interleaves three distinct paths — graph-level baseline capture, the Item 7
collector, and strict CLI generation — with three different order-sensitivities and
three different "expected" outcomes, across nested bullets. A tired engineer can't
extract the load-bearing distinction: *baseline capture is order-independent; the
collector assertion needs Item 7; strict generate is expected to raise V11 and gets
xfailed.* That three-way split (which L1-1, L1-2, L3-1 all turn on) is the spec's
riskiest content and is currently buried. Ask the spec agent to lead the section
with those three paths stated plainly — what each is, whether it depends on Item 7,
and what "success" means for each — before the mechanism detail.

---

## Engagement Summary

**Overall take:** The spec is pointed at the right work and its code claims hold
up, but it over-claims completeness and rests two HARD requirements on an Item 7
dependency the epic says doesn't exist. Both gaps are real substrate problems that
would surface as blocked or under-specified work in Items 9–10, not cosmetic. Fix
those and it's a solid contract.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Item 10's success criterion needs "two same-type sibling parts" and
   the six shapes don't include it. Add the shape to ife_plant, or explicitly hand
   it to Item 10 — but don't leave the "full substrate" claim standing as-is.
2. **[L1-2, L3-1]** The collector-based capture and conformance requirements assume
   Item 7 has landed, but Item 8 has no dependency on it and both are in flight.
   Decide: sequence Item 7 first, or make the collector assertion conditional with a
   "graph builds without raising" fallback so Item 8-first is buildable.
3. **[L1-3, L3-2]** The self-named-binding trap — is its failure mode a benign
   degenerate resolution (what the spec assumes) or the syside recursion the epic's
   Item 12 note flags? If recursion is possible, default it to a separate fixture
   dir so it can't poison ife_plant's snapshot.
4. **[L1-1]** The "tiered capture with extraction-only fallback" describes a
   mechanism that doesn't exist in the pipeline-baseline script. Clarify that the
   extraction-only outcome means *no pipeline baseline* for that fixture — and what
   that costs Items 9–10 — rather than presenting it as an equivalent tier.
5. **[L2-2]** Set a richness floor for ife_plant's def-attribute literals (or
   consciously decide it's an authoring detail). A 2-literal fixture satisfies Item
   8 but can't demonstrate Item 9's meaningful pre-fill.
6. **[L3-3]** "Fixtures pass agentic-mbse validation" contradicts the fixtures'
   purpose — they deliberately model shapes agentic-mbse should flag. Split the
   criterion into well-formedness (must pass) vs. supported-subset (expected to
   flag, recorded, not fixed).

---

## Resolutions

*To be filled in as the user resolves findings (Stage 5). Keyed by finding ID.*

---

**Verdict:** Revise

**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does
not edit the spec. The two must-fix items before the spec is the contract are the
missing sibling-ambiguity shape (L2-1) and the unstated Item 7 / collector
dependency (L1-2, L3-1); the rest are clarifications and one syside-safety question
(L1-3, L3-2) that should be settled before the trap is co-located.
