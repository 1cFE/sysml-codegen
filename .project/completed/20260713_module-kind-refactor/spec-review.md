# Spec Review: `module_kind` and the Generation-Seam Refactor (Item 6)

**Spec:** `.project/active/module-kind-refactor/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/module-kind-refactor/spec-review.md`
**Date:** 2026-07-12

---

## Reality Check

**Sound, with one scope gap to close.** The spec is about the right work item, the problem
framing is accurate, and the core requirements are directionally correct. Two of the highest-risk
claims — that the refactor is decoupled from Item 8's snapshot work, and that the four S4 seams
plus `pipeline.py`/`test_gen.py` are the src consumers — both check out against the code. The one
material gap is that the spec's "every flag consumer" migration list is **src-only**, while its
own success criterion demands a repo-wide zero-hit grep plus a green suite. 22 test files read
these flags today. That is a real sizing and completeness miss, not a wording nit. Revise, don't
rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (verified — in the spec's favor):** The decoupling-from-Item-8 claim
(spec lines 103-110, 118-121) is **correct**, and it survives the sharper question the review
brief raised. Two facts hold:
- `extraction_snapshot.json` fixtures carry neither flag — `grep` returns zero (confirmed;
  the only JSON hits are `computation_graph.json` baselines, which are graph artifacts, not
  snapshots).
- The snapshot *rebuild* path does **not** reconstruct `PipelineModule` from serialized graph
  JSON. `snapshot/graph_rebuild.py:158` calls `build_computation_graph(...)` — it re-runs the
  graph builder from snapshot facts, so `module_kind` is *reconstructed* at rebuild, never
  read back from a serialized field. The field is therefore not snapshot-version-relevant.

  This is exactly the failure mode the brief told me to rule out, and it is ruled out. Record
  the verification; no change needed.

**L1-2 · Direct claim:** The "Every other flag consumer" section (spec lines 82-89) enumerates
only **src** consumers (`test_gen.py`, `pipeline.py`, the three construction sites). But
success criterion 4 (spec line 42-43) reads "no reader of `is_computed_attribute` or
`is_aggregation` remains" and criterion says "A repo-wide grep … must return zero hits at the
end" (line 89). **22 test files** consume these flags today — assertions like
`assert module.is_aggregation is True` (`tests/unit/test_graph_builder_aggregation.py:482`),
factory helpers that take `is_computed_attribute=` kwargs
(`tests/unit/test_aggregation_generation.py:68-81`), and baseline-comparison harnesses
(`tests/conformance/test_pipeline_e2e.py:86-90`). None are mentioned. The migration surface the
spec describes is a fraction of the migration surface the gate demands. Either the consumer list
must acknowledge the test suite as in-scope, or the zero-hit gate must be scoped to `src/`.

**L1-3 · Direct claim (verified — affirm):** "formula" as the reading of `is_computed_attribute`
(spec line 59) is **correct and consistent with the codebase**. The conformance suite already
names these modules FORMULA (`tests/conformance/test_factory_formula.py:8,340`:
"`is_computed_attribute == True` for every FORMULA module"). The kind name doesn't invent a
term; it adopts the existing one. No change.

**L1-4 · Rewrite request (minor):** The Open Question on enum values (spec line 139) says "the
concept spells `report_aggregator`." The concept prose at line 98 actually spells it
"report aggregator" (with a space); it's the **epic** scope (line 279) that uses the underscore
`report_aggregator`. The value the spec adopts is right; the citation of where it comes from is
slightly off. Fix the attribution so design doesn't chase the wrong source for the canonical
string.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The spec defers "what a constraint/report-aggregator kind does
at each seam in this item" to design, offering a menu: "raise a clear `NotImplementedError`-style
guard, **skip the module**, or route to a stub" (spec lines 127-132). But the concept's Design
Principle 5 is "silence is never an outcome," the S4 evidence is that these kinds *mis-render
silently as calcs* today, and the review brief states constraint kinds "must fail loud, not
mis-render." **"Skip the module" is a silent outcome** — it's a softer version of the exact bug
this item exists to kill. The recommendation (fail loud) is right, but leaving "skip" on the menu
as a co-equal design choice contradicts the governing principle. Should "fail loud" be pinned as
a **[HARD]** requirement here (the *form* and message stay design-open, but skip/stub are off the
table), rather than one of three open options?

**L2-2 · If-then tradeoff:** The [HARD] mapping (spec lines 56-60) asserts the three kinds "map
one-to-one from today's flags." The two-flag space has **four** cells, not three — and the fourth,
`is_computed_attribute=True AND is_aggregation=True`, has *defined* behavior in the current code
(`tests/unit/test_aggregation_generation.py:158`: "If both … aggregation wins"; and the seams
resolve it inconsistently — `modules.py:40-42` gives computed precedence, others differ). The
mapping is total and unambiguous **only because construction never sets both flags** — verified:
`graph_builder.py:1183` sets computed-only, `1586` sets aggregation-only, `1783` sets neither.
So collapsing to one enum is genuinely lossless. But the spec asserts the one-to-one map without
stating *why* the fourth cell is safe to ignore. The brief asks specifically whether the mapping
is "total and unambiguous" — the answer is yes, and the spec should say the one sentence that
makes it yes: no construction site ever produces both flags, so the ambiguous cell is unreachable.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (sizing):** Complexity is marked MEDIUM and the epic budgets 7h execute
(epic line 274). That estimate fits the ~8 src edit sites the spec enumerates. It does **not** fit
migrating 22 test files off the flags to satisfy the zero-hit gate (see L1-2). Design and plan
will discover this surface the hard way if the spec doesn't name it. Either raise the scope
acknowledgment (test migration is part of this item) or explicitly file the test-suite migration
as its own tracked slice. A silent 3× scope discovery mid-implementation is the risk.

**L3-2 · Direct claim:** The spec frames baseline regeneration as "an intentional, reviewable
fixture update" (spec line 108-109) — as if only the JSON files change. It's more coupled than
that. Several tests *read the flag keys back out of the baseline JSON* and compare:
`tests/conformance/test_pipeline_e2e.py:86-90` (`m.is_aggregation == bm["is_aggregation"]`),
`tests/conformance/test_graph_assembly.py:563-567`, and `tests/conformance/test_data_models.py:584-585`
lists `"is_computed_attribute"`/`"is_aggregation"` as expected model fields. Regenerating the
baselines to a `module_kind` key forces **lockstep edits to these comparison harnesses**, or they
break. This is design-relevant coupling the spec currently hides inside "reviewable fixture
update." Name it so design plans the baseline change and the harness change as one move.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** The spec cites the three graph-builder construction sites with
two different line sets: `1183, 1586, 1783` in the [HARD] mapping (lines 58-60) and
`1175, 1578, 1783` in the consumer list (line 88). Both are defensible — `1175/1578/1783` are the
`PipelineModule(` calls; `1183/1586` are the flag-assignment lines *inside* the first two. But an
unexplained mismatch reads as an error. Pick one convention (the construction-call lines are
clearer) or note that the assignment lines differ from the call lines.

### Lens 5 — Reader Comprehension

No findings. The spec leads with the point, the byte-identity gate is stated plainly and early,
and the Open Questions are genuinely design-stage. A tired engineer can skim it once and know the
work item and the gate.

---

## Engagement Summary

**Overall take:** The bet is sound and the two claims most likely to be wrong — snapshot
decoupling and the src consumer list — both hold up against the code. The spec's real weakness is
that it describes a src-only migration while committing to a repo-wide zero-flag gate and a green
suite; the 22 test files that read these flags are the unpriced two-thirds of the job. Fix the
scope, pin fail-loud, and this is a clean contract.

**Here's what I need you to weigh in on:**

1. **[L1-2, L3-1, L3-2]** The zero-hit grep + green-suite gate pulls **22 test files** and several
   baseline-comparison harnesses into scope, none of which the spec's migration section names.
   Decide: expand the consumer list (and the effort estimate) to include the test suite, or scope
   the zero-hit gate to `src/` and treat test migration as follow-on. Right now the gate and the
   enumerated work don't match.
2. **[L2-1]** Should "fail loud" be a **[HARD]** requirement for a constraint/report-aggregator
   kind reaching a not-yet-wired seam — with only the *message/form* left to design — rather than
   one of three open options that includes "skip the module"? The concept says silence is never an
   outcome; "skip" is a silent outcome.
3. **[L2-2]** The two-flag → three-kind map is total only because construction never sets both
   flags (verified). Add the one sentence that says so, so the "total and unambiguous" claim is
   grounded rather than asserted.
4. **[L1-1]** For your confidence: the decoupling-from-Item-8 claim is verified correct — snapshots
   don't carry the flag and rebuild reconstructs the graph via `build_computation_graph`, so
   `module_kind` is never a serialized snapshot field. No action; noted so you can trust it.

---

## Resolutions

*(To be filled in as the owner engages. Keyed by finding ID.)*

---

**Verdict:** Revise (Approved-with-must-fixes)

**Must-fix:**
- **L1-2 / L3-1 / L3-2** — reconcile the migration scope with the zero-hit gate; the test suite
  and baseline-comparison harnesses are in-scope work the spec doesn't name.
- **L2-1** — resolve whether fail-loud is [HARD] here; drop "skip the module" if so.

**Nice-to-have:**
- **L2-2** — state why the flag→kind map is total (construction never sets both flags).
- **L1-4** — fix the `report_aggregator` source attribution (epic, not concept prose).
- **L4-1** — reconcile the two graph-builder line-number sets.

**Next Steps:** Once resolutions are recorded, re-run `/_my_spec` (or return to the spec-agent
session) and point it at this review to incorporate. The reviewer does not edit the spec.
