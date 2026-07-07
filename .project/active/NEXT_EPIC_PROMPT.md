# Prompt: Define the next epic — "the whole pipeline works"

Copy everything below the line into a fresh agent session in
`/home/reid/1cfe/sysml-codegen`. Branch state: **PR #3 (UPSTREAM-FINDINGS) is merged** —
plan against current `main` (run `git fetch` and confirm; the local `origin/main` ref
may be stale). The `docs-scrub` branch (certified docs pass) is now unblocked and PRs
separately; treat its content as landed-or-imminent and cite the scrubbed docs freely.

---

Define the next epic for sysml-codegen using `/_my_epic_plan`. The mission, in one
sentence: **the generated package is the truth — a consumer's real model set generates,
wires, and executes end-to-end with zero bridges, zero hand-plumbing, and every
diagnostic firing on the shape it claims to cover.**

The UPSTREAM-FINDINGS epic (12 items, PR #3) fixed the verified findings and staged
cross-part support. A follow-up validation run in fusion-tea (2026-07-06) confirmed the
fixes hold on the real models AND sharpened exactly what remains: one unfinished
feature, one new bug, and a tail of filed divergences. Your job is to shape the epic
that finishes this — not to implement anything.

## Non-negotiable inputs (read fully before shaping)

1. `~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md` — the
   follow-up validation: per-SC verification matrix, the 10-offender gap analysis, the
   bridge methodology, workaround retirement table, post-merge coordination checklist.
   This is the closest thing to a findings register for the new epic.
2. `.project/backlog/epic_upstream_findings.md` — the prior epic: its cross-cutting
   requirements R1 (design-pattern consistency), R2 (agentic-mbse lockstep), R3
   (baseline/license discipline) carry forward unless you argue otherwise.
3. `.project/backlog/BACKLOG.md` — every DOCS-SCRUB-F*, SYNC-F*, the P1 whole-plant
   item, and the Ideas section (real bugs hide there — see below).
4. `docs/architecture/modeling-assumptions.md` — the supported-subset contract
   (scrubbed and audited 2026-07-06; trustworthy).
5. `.project/active/docs-scrub/fact-sheet.md` — condensed "true at HEAD" facts with
   provenance.
6. Release notes: `.project/active/{warning-reconciliation,cross-part-wiring,alias-surfacing,plant-prefill}/release-notes.md`.

## Known gaps and bugs (the epic's floor — verify each, then absorb or explicitly defer)

**A. The headline: whole-plant cross-part wiring (P1).**
`generate` on fusion-tea's models aborts at V11 on exactly 10 plain
subsystem-attribute → plant-calc-input references (`driver.efficiency`, `driver.energy`,
`driver.lifetime_shots`, `chamber.blanket_energy_multiple`,
`chamber.yield_cost_constant`, `target_factory.cost_per_target`, plus
`hif_driver_instance`'s inputs). This is a different shape from Item 10's
specialized-`:>>`-chain and multi-hop-EXPOSE cases. The fusion-tea run proved the fix
is small and the payoff is total: the entry-point slots already exist in the derived
groups; the values are literals sitting in the model; with a 10-value bridge, anchor C
reproduces **bit-exactly** ($270.1211779380445/MWh) through the teax executor in a
single pass, and BOTH feedback edges (`gamma→lcoe` AND `cost_billions→meier_capital`)
close via generated wiring. Filing note: this item currently sits under BACKLOG
"Ideas / Future Considerations" despite its P1 tag — promote it. Its acceptance test is
already drafted in that entry (extend `spec_chain_twolevel` with the plain
cross-part-attribute shape; fusion-tea generate emits full YAML, zero V11 offenders;
run-C reproduces within tolerance).

**B. New bug, NOT yet filed in this repo: assert-constraint silence (SC-1 regression-in-effect).**
`report_dropped_constraints` (`extraction/extractor.py`) enumerates
`elements_of_type("ConstraintUsage")`; syside's `model.elements()` is exact-type, so
`assert constraint` (`AssertConstraintUsage`, a subtype) is invisible — the report is
completely silent (both INFO and the summary WARN gate on a non-empty list) for exactly
the shape fusion-tea uses. Verified in-repo 2026-07-06. Compounding factors the fix
must address, not just the query:
- The REQ-EXT-09 test (`tests/conformance/test_extractor.py::TestReqExt09`) computes
  its expected count **with the same query the implementation uses** — self-referential,
  structurally unable to catch this. Re-anchor the expectation independently.
- Its fixture (catf_mfe) has only plain constraints; `tests/fixtures/wi014_toy` already
  carries an `assert constraint` (toy_plant.sysml) but nothing asserts the report
  against it. Item 1's success criterion "the WI-014 toy emits the constraint
  diagnostics" was never actually true for that constraint.
- `extraction/constraint_extractor.py`'s docstring claims support for
  "constraint, assert constraint, and require constraint" while using the same blind
  query — check `require constraint` too while you're there.
- `generate --from-snapshot` never runs the report; constraint data IS serialized
  (`_deserialize_constraint_info`, `snapshot/loader.py`), so a from-snapshot report is
  implementable. Decide whether that's in scope.
- Docs impact: modeling-assumptions §8 ("scans the whole model for constraint usages
  and reports them") overclaims until the fix lands.
- Meta-item: this is a *pattern*, not one bug — see Discovery mandate D4.

**C. REQ-vs-code divergences (filed, unresolved):**
- `DOCS-SCRUB-F2`: REQ-OR-05/06/08 say Key_A/Key_F are never registered; the code
  registers both and Phases 3–4 consult a Key_A-format dict before typed lookups.
  Decide the intended contract; land it or re-frame the REQs.
- `DOCS-SCRUB-F4`: `resolve_input()`/`AGG_STRATEGIES` has **zero production callers**
  while REQ-IR-05/07 and REQ-RES-02 are marked PASS (pinned by tests that call the
  bypassed function directly). Strategy D is a documented-intent no-op, so the
  aggregation-EP dedup it promises never happens. Land the cutover or excise it.

**D. Real behavioral bugs hiding in BACKLOG "Ideas":**
- Aggregation-literal dispatch (from Item 6/SC-6): `_walk_aggregation_ast` keeps the
  old literal-after-invocation ordering — a literal operand in an aggregation
  expression is mis-dispatched and marked `has_unsupported`. Doc 19 carries this as a
  known-deviation note; it's a bug, not an idea.
- The dotted-leaf alias edge in `extract_hierarchy_data` (spurious alias for
  `parent.attr`-style CHAIN redefinitions) is live behavior guarded only by "no
  current model triggers this" — a cheap unit pin retires the hedge (doc 25 flag).

**E. Cleanup debt (filed):** `DOCS-SCRUB-F1` (two dead templates + four dead-code
candidates incl. `generate_derived_group_json`, which still emits null-default keys —
the shape Item 7 corrected), `DOCS-SCRUB-F3` (four stale code docstrings), the
DEPRECATED `binding_to_entry_point`, `REQ-DM-08` (NewType field annotations genuinely
unimplemented; doc 09 now says so). Also 5 xfails (`TestInheritedAttrClassification`
inherited-attribute classification) and 4 skips in the gate — inventory them; decide
which the epic should convert to green.

**F. Cross-repo and coordination:**
- fusion-tea: harness re-anchoring when `hif_driver_instance` is deleted (Meier channel
  EQNs move); retirement of `sanitize_names.py`, the two-pass gamma feedback, the
  hand-written input JSONs; anchors A/B are now module-level checks by the model's own
  semantics. The post-merge coordination checklist in their report is the map.
- agentic-mbse: C7/C8/F6 backlog items; the D-F validation warning
  (`attribute :>> attr = <expression>` — silently dropped shape) recorded but not
  built; the companion PR (`upstream-findings-sync`) still unmerged; the syside vendor
  note (self-named-binding recursion) unfiled. R2 lockstep applies to every new item.
- SYNC-F3/F4/F5 (P2, filed): shape-B leaf-collision filenames, redefinition/
  design_override name surfacing, positive unresolvable-warning test.

**G. Deferred features to re-weigh (not obviously in scope — argue each way):**
constraint execution (SC-1 full epic), supertype-chain template inheritance for plain
usages (blocks part of the MFE idiom), EXPOSE_COMPUTED, function calls/conditionals,
non-uniform arrays, body-assignment capture, hierarchical output (draft item),
PUSH-DOWN epic (design ready; its Item-6 prerequisite has landed — sequencing
interaction with this epic must be stated), generation-boundary item (In Progress,
Step 7.6).

## Discovery mandate — subagents REQUIRED

The list above is the floor, not the ceiling. Before writing the epic, fan out
subagents (Explore for searches; general-purpose where reasoning over code is needed)
and consolidate their findings into the epic's evidence base. Minimum sweep:

- **D1 — Filed-but-unlanded:** every `release-notes.md`, `audit.md`, and close-out under
  `.project/active/*/` — harvest every "filed as follow-up", "deferred", "not yet",
  "recorded for Item 12", CONDITIONAL-audit residue. Cross-check each against BACKLOG;
  anything mentioned-but-never-filed is a finding.
- **D2 — Code-marker sweep:** TODO/FIXME/XXX/DEPRECATED/HACK/`xfail`/`skip` across src/
  and tests/, plus `warnings.warn`/`logger.warning` sites whose wording promises
  behavior (each promise is a claim to verify).
- **D3 — Silent-failure hunt:** broad excepts, silent fallbacks on invariant
  violations, `return None`/default on lookup misses in resolution paths, warnings
  gated on non-empty collections (the SC-1 silence pattern: zero-found == no report).
- **D4 — The exact-type enumeration pattern:** audit EVERY `elements_of_type(...)` call
  site (and any raw `model.elements(...)`) against the SysML type hierarchy — the SC-1
  bug is one instance; subtype-blind queries may lurk elsewhere (PartUsage subtypes?
  AttributeUsage? ReferenceUsage?). Also audit the agentic-mbse `SysideAdapter.TYPE_MAP`
  itself.
- **D5 — Self-referential tests:** find every conformance test whose expected value is
  computed by the same code path it verifies (the REQ-EXT-09 anti-pattern). Each is a
  test that cannot fail; list them all.
- **D6 — Fixture blind spots:** diff the SysML shapes fusion-tea's real models use
  (read `~/1cfe/fusion-tea/models/`) against what `tests/fixtures/` covers — the prior
  epic's root lesson was that 1,500+ tests missed everything the fixtures didn't model.
  Name each uncovered shape.
- **D7 — Matrix truth:** REQs marked PASS whose tests pin something weaker than the
  REQ text (F2/F4 are two; find the rest). Also the UNTESTED-12 — which should the
  epic convert?
- **Adversarial pass:** for every "confirmed fixed" claim in the fusion-tea report,
  have one subagent try to name a shape/path the verification did NOT exercise (e.g.
  SC-4 verified on their current models — what about the quoted-name + FORMULA + alias
  interaction?). Discovery ends when a sweep round returns nothing new, not when the
  checklist is done.

Constraints on discovery: read-only; no fixes, no commits; live syside probes are
optional (the license key may not be loaded in this environment — license-gated tests
skip cleanly; note what you could not probe rather than guessing).

## Shaping requirements for the epic itself

- **Success criteria must be outcome-anchored and falsifiable**, at minimum:
  (1) `generate --models ~/1cfe/fusion-tea/models` emits the full package, zero V11
  offenders, zero bridges; (2) run-C's lcoe reproduces through the generated package
  alone (state where that gate runs — in-repo tolerance test on the twolevel fixture +
  a fusion-tea acceptance run); (3) every fusion-tea workaround in the retirement
  table is deleted, not just deletable; (4) every V-diagnostic demonstrably fires on
  every syntactic shape it claims (assert/require constraints included), with
  independently-anchored expected counts; (5) zero self-referential diagnostic tests
  remain; (6) REQ text, tests, and code agree — no PASS row pins less than its text.
- **Carry forward R1/R2/R3** from UPSTREAM-FINDINGS (patterns, agentic-mbse lockstep,
  scripts-only baselines with reviewed diffs). The syside license is now on monthly
  renewal — **no expiry pressure**; do not let the prior epic's license-window
  scheduling language leak into this one. Capture work schedules on its merits.
- **Per-item Required Reading** pointing into the scrubbed `docs/architecture/reference/`
  docs (they are current as of 2026-07-06; keep them current — doc+matrix updates move
  with code per R1).
- **Architecture-docs refresh is in scope, not incidental.** Beyond per-item R1 updates,
  the epic must include an explicit end-of-epic docs pass: every reference doc,
  `modeling-assumptions.md` section, and verification-matrix row touched by the epic's
  changes is re-verified against post-epic HEAD, and every caveat the epic retires
  (the V11 10-offender abort, the assert-constraint silence, "four specific shapes",
  F2/F4 divergences) is removed or reworded — the docs-scrub certification must still
  hold at epic close.
- **Include an item to update `.project/active/EXPLAINER_PROMPT.md`.** That prompt
  builds the interactive pipeline explainer and is executed only once the pipeline
  fully works — i.e. after this epic's success criteria hold. It hard-codes facts the
  epic will change: the `docs-scrub` branch anchor, the "Honest caveats" section
  (10 remaining V11 bindings, four cross-part shapes, open DOCS-SCRUB-F2/F4), the
  cross-part story, and the reading list. The epic's closing item revises that prompt
  to match post-epic reality (and gates its execution on the epic's acceptance run),
  so the explainer is built from true facts, not stale ones.
- Structure as parallel tracks where dependencies allow (the prior epic's two-track
  layout worked); the wiring item (A) gates fusion-tea and should be first-class, not
  buried. Give every item the fit/lift/risk sizing treatment and an explicit
  out-of-scope list.
- Anything discovered but NOT absorbed into the epic gets filed in BACKLOG with a
  pointer — nothing silently dropped. File item B in BACKLOG immediately even before
  the epic is approved (it is currently recorded nowhere in this repo).
- Deliverable: `.project/backlog/epic_<name>.md` via `/_my_epic_plan`, a BACKLOG.md
  update (promote A out of Ideas, add B, link the epic), and a short summary of
  discovery findings that did NOT make the epic and why.
