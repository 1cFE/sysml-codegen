# Spec Review: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Spec:** `.project/active/warning-reconciliation/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/warning-reconciliation/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound, with concrete fixes required.** The spec is about the right work item, the
problem framing is accurate, and the three defects it names are real and correctly
diagnosed. I re-traced the load-bearing claims against HEAD and they hold: the
`magnet_volume` dangling input is exactly as described, the two matcher bugs are at
the cited lines, and the xfail root is a genuine nested-part EXPOSE. But three
things are wrong or under-decided enough to block approval as-is: one requirement
number is already taken, the lockstep flip set is incomplete (two consumer sites
missing), and the catf_mfe xfail footprint is materially undercounted. This is a
**Revise** — the work item is sound; the contract needs targeted corrections.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim: `REQ-GA-04` is already taken — the spec picks an occupied number.**
The Diagnostics section says "`REQ-GA-04` — params-coverage check … sibling to
REQ-GA-03." But `REQ-GA-04` through `REQ-GA-07` all exist today:
`docs/architecture/reference/07-graph-assembly.md:18-21` defines GA-04 (self-reference
guard), GA-05, GA-06, GA-07, and the verification matrix (`verification-matrix.md:220-221`)
lists them PASS. The next free graph-assembly number is **REQ-GA-08**. The rest of the
numbering census is correct: `REQ-BT-09/10` (max is BT-08), `REQ-OR-09` (max OR-08),
`REQ-PGD-08` (max PGD-07), and **V11** (V1–V10 in use at `modeling-assumptions.md:370-379`)
are all genuinely free. Doc ownership (07/10/11/17/24) is correct — all five files exist
with the topics claimed. Fix the GA number; the rest of the section stands.

**L1-2 · Direct claim: the lockstep flip set is incomplete — two consumer sites are missing.**
The spec enumerates the flip set as `:130` registration + `:595` lookup + `:660`
conversion + `pipeline_builder.py:70` twin, and calls it the complete set. It is not.
Grepping every producer/consumer of the two raw-QN paths turns up two sites the spec
never names:

- **`resolution/input_resolver.py:120` — a second consumer of the FORMULA sysml-QN
  registry.** `register_sysml_qn` has exactly one producer (`output_registry_builder.py:131`),
  but `sysml_qn_lookup` has **two** consumers: `dependency_backtracker.py:595` (the spec
  lists it) and `input_resolver.py:120` `SysMLQNLookup` (Strategy B), which the spec does
  not. Strategy B passes `SysMLQN(ref)` **raw**. The moment `:130` flips to a sanitized
  key, this lookup silently misses for any quoted-owner FORMULA output consumed through
  the aggregation strategy chain. Its own docstring says "Zero-exercise for aggregation
  scope (spike confirmed)" — so it may be provably dead for the current corpus, but the
  spec must say that explicitly and either flip it in lockstep or record why it can't fire.
  A registry whose key form changes cannot leave one of its two consumers on the old form
  undocumented.

- **`analysis/parameter_groups.py:439` (`_find_source_file`) — a bare-swap twin of the
  `:660` bug.** It builds a lookup key with `sysml_to_python_qualified_name(source_path)`
  (bare `::`→`__`, no per-segment sanitize) and matches it against `self._attr_index`,
  which is keyed by `DesignAttributeData.qualified_name`. That index key is per-segment
  **sanitized** (`build_element_qualified_name` calls `sanitize_name` on every segment,
  `qualified_names.py:57,76`). So for a quoted design attribute, `_find_source_file`
  builds `Lib__'Magnet Part'__attr` and the index holds `Lib__Magnet_Part__attr` — the
  exact miss the `:660` fix targets, in a second location. The spec's [HARD] REFERENCE-path
  fix names only `:660`. This site lives in the same file the spec assigns REQ-PGD-08, but
  it is a *different* fix from the def-owned matcher — a third instance of the name-form
  bug class, un-enumerated.

Also worth a line in the regen footprint: the flip itself is byte-invariant on every
committed baseline (no baseline model has a quoted calc-def owner, so `sanitize` is the
identity there), and the FORMULA registry keys are built at orchestration time, not
serialized into extraction snapshots — so "does flipping change snapshot content" is
**no** for the registered keys. Only downstream resolution churn (from the *matcher*
fixes, not the flip) touches baselines. The spec should state this so the reader isn't
left guessing whether the flip alone forces a regen.

**L1-3 · Direct claim: reclassification changes pre-filled *values*, not just JSON key layout.**
The spec's [INFERRED] churn note and the three-part review procedure treat the
`USAGE_LITERAL → DESIGN_ATTRIBUTE` churn as key-layout + dedup. It is more than that.
`entry_type` selects the **default-value source** (`graph_builder.py:397-404`, applied
at `:442/:452/:467`):

- `DESIGN_ATTRIBUTE` → `DesignAttributeData.default_value`
- `USAGE_LITERAL` → `BindingInfo.literal_value`

So a reclassified entry point switches which object supplies the value that pre-fills
the params JSON. For a correctly-resolving design attribute these are the same underlying
literal and the value won't move — but that is an assumption the spec is silently making,
not a fact it states. This is exactly what scrutiny point 3 asks ("does anything downstream
key off entry_type beyond key layout — defaults?"): **yes, defaults.** (Schema field types
appear to derive from the attribute's declared type, not `entry_type` — worth a one-line
design confirmation, but I found no `entry_type`→schema-type coupling.)

**L1-4 · Confirmed (not a defect): the catf_mfe xfail root is real and correctly traced.**
Verified end to end: `magnets.sysml:87` binds `in magnet_volume = catf_radial_build.magnet_volume_total`;
`radial_build.sysml:582` declares `attribute magnet_volume_total : Real = tf_coil.volume`
under the "valid EXPOSE patterns" comment (`:581`); `tf_coil.volume` is itself
`= volume_calc.volume` on a nested part. It is a genuine nested-part cross-part EXPOSE the
pipeline cannot wire until Items 9–11. The spec's characterization is accurate. (Trivia:
the attribute is `radial_build.sysml:582`; the spec cites `:581`, which is the comment
line — harmless.)

### Lens 2 — Problem & Approach

**L2-1 · Question to the user: the xfail is not "a single narrow mark" — it hits ≥5 tests across 2 files, one via a shared fixture, and degrades unrelated coverage.**
The spec's rationale rests on "the xfail is a single narrow mark on the catf_mfe E2E
generation test." Two test files run full `run_codegen` on catf_mfe:

- `test_computed_attributes_e2e.py::test_catf_mfe_still_works` — 1 test (asserts codegen
  succeeds + exactly 18 impl files).
- `test_expression_compilation_e2e.py::TestCATFMFEValidation` — a **class-scoped fixture**
  `catf_mfe_output` (`:208-219`) that runs `run_codegen` and `assert success`, feeding
  `test_codegen_succeeds`, `test_auto_implementation_classification` (18 FC / 0 stubs),
  `test_unused_calcdefs_excluded_from_graph_output`, and more below `:259`.

A hard V11 error inside `run_codegen` fails the fixture's `assert success`, which
**cascades as a fixture error to every test in that class** — you cannot suppress a
fixture-level failure with one xfail mark; you'd mark each consuming test, or restructure.
So the real footprint is ~5+ tests, and the counter-position in the scrutiny brief lands:
xfailing them abandons coverage for the 18-impl regression guard, the auto-impl
classification, and the unused-calcdef exclusion — none of which relate to
`magnet_volume`. The narrower alternative (xfail only a params-coverage assertion) isn't
freely available, because V11 aborts generation *before* those tests get their output.
**Decide:** accept the wider xfail set and enumerate every affected test in the spec, or
require design to structure the check so generation still completes and only a dedicated
coverage assertion reddens (keeping the other E2E assertions live). Either is defensible;
"a single narrow mark" as written is not accurate and will surprise whoever implements it.

### Lens 3 — Pipeline Risk

**L3-1 · If-then tradeoff: the reconciliation-summary level is deferred, but the epic already decided it must be LOUD for the SC-5 cases.**
V11 fires only on inputs whose `*_params.X` key is **absent** from every parameter group.
But a Step-4 fallback can mint a *covered* key that is still semantically unresolved
(cross-part binding that fell through but got a synthetic entry point with a key). Those
cross-part cases (Items 9–11, out of scope) are caught **not** by V11 but by the
post-assembly reconciliation summary ("fell through AND still lacks a value"). The epic's
obligation is explicit: "the coverage check keeps them loud in the meantime." Yet the
spec files the summary's level as an Open Question — "whether the summary is INFO or
WARNING when non-empty." **If** V11 provably catches every cross-part shape that Step-4
warnings surface today, INFO is fine. **If not** (and the covered-but-unresolved case
suggests not), then demoting Step-4 to DEBUG plus an INFO summary makes the SC-5 cases go
*quiet* — the opposite of the epic's requirement. This isn't a design-stage question; the
epic has already answered it. The spec should pin the fell-through-and-lacks-value summary
to WARNING (or prove V11 subsumes the cross-part set), not defer the loudness decision.

**L3-2 · Rewrite request: the three-part review procedure omits value churn (ties to L1-3).**
The procedure enumerates (1) reclassified entry points, (2) collapsed keys, (3) params-JSON
key *set* after. It never asks for the pre-filled *values* before/after. Because
reclassification switches the default-value source (L1-3), a review that checks only key
sets would not catch a value that moved when `DesignAttributeData.default_value` differs
from the usage's `BindingInfo.literal_value`. Add a fourth item, or fold into (3): a
before/after of the pre-filled *values*, not just the key set, for each affected model.
Otherwise the procedure is concrete and executable.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** the Diagnostics & Requirement Numbering section reads
as settled fact ("next free numbers") while carrying the GA-04 error (L1-1). Once GA-04 →
GA-08 is fixed, add the one-line "verify again at design" it already gestures at, since
Item 6 is landing concurrently and could consume a number in a shared family. No other
hygiene issues — the cited line numbers (`:130`, `:595`, `:660`, `:70`) are all accurate.

### Lens 5 — Reader Comprehension

No material finding. The spec is dense but each requirement leads with its point, the
tags are honest, and the xfail decision is argued rather than asserted. A tired engineer
can follow it on one read. The only comprehension risk is L2-1 — the "single narrow mark"
phrasing reads as reassurance and will mislead the implementer about the test footprint;
that is captured above as a substance finding, not a wording one.

---

## Engagement Summary

**Overall take:** The spec is pointed at the right problem with an accurate diagnosis and
a verified xfail root — but it ships three concrete errors that would bite in
implementation: it claims an occupied requirement number, it under-enumerates the lockstep
flip set by two consumer sites, and it undercounts the catf_mfe xfail footprint by ~4
tests. None are fatal to the work item; all are targeted fixes. Revise.

**Here's what I need you to weigh in on:**

1. **[L1-2]** The lockstep flip set is incomplete. `input_resolver.py:120` (second
   `sysml_qn_lookup` consumer) and `parameter_groups.py:439` (a bare-swap twin of the
   `:660` bug against a sanitized index) are both un-enumerated. Add them to the flip set,
   or record why each is provably dead. This is the "any missed site silently breaks
   matching for quoted models" risk the scrutiny brief flagged — and it's real.
2. **[L1-1]** `REQ-GA-04` is taken (self-reference guard). Renumber the params-coverage
   check to **REQ-GA-08**. Everything else in the numbering census (BT-09/10, OR-09,
   PGD-08, V11, docs 07/10/11/17/24) checks out.
3. **[L2-1]** The catf_mfe xfail is not one mark — it breaks ≥5 tests across two files, one
   via a class-scoped fixture whose failure cascades. Decide: enumerate and accept the
   wider xfail set, or make design structure the check so the unrelated E2E assertions
   (18-impl guard, auto-impl classification) stay live.
4. **[L3-1]** The reconciliation-summary level is filed as open, but the epic already
   requires the SC-5 cross-part cases to stay LOUD, and V11 only catches *uncovered* keys —
   not covered-but-unresolved fallbacks. Pin the fell-through-and-lacks-value summary to
   WARNING, or prove V11 subsumes every cross-part shape Step-4 warnings surface today.
5. **[L1-3, L3-2]** Reclassification switches the default-*value* source
   (`DesignAttributeData.default_value` vs `BindingInfo.literal_value`), not just the JSON
   key. Add a before/after of pre-filled *values* to the review procedure; today it checks
   only key sets and would miss a moved value.

---

## Resolutions

*(To be filled in during Stage 5, keyed by finding ID.)*

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not edit
the spec. The five engagement items are the gate; the confirmations (L1-4, doc ownership,
V11/BT/OR/PGD numbering) need no action.
