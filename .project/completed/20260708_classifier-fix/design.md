# Design: Inherited-Attr Classifier Fix (flip the 5 xfails)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-07
**Branch:** truth-debt-epic (HEAD 1548734)
**Epic:** TRUTH-DEBT, Item 4 (SC-D); R1–R4
**Spec:** `.project/active/classifier-fix/spec.md` (revised through `spec-review.md`)

---

## Overview

Widen the computed-attribute classifier's Step-2b sibling check to accept a reference
whose qualified name sits under an **ancestor PartDef's** namespace, so an inherited-attr
reference is a sibling (→ FORMULA), not a cross-namespace calc output (→ EXPOSE_COMPUTED).
The ancestor set is computed transiently during extraction; nothing new is serialized. Correct
classification is the win; a small companion graph-builder diagnostic (D5) makes the residual
"FORMULA that can't compile" no-op *loud* instead of silent at generation.

## Related Artifacts

- **Spec:** `.project/active/classifier-fix/spec.md`; **Spec review:** `.project/active/classifier-fix/spec-review.md`
- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 4, R1–R4, SC-D)
- **Required Reading:** `.project/backlog/BACKLOG.md` `[ITEM7-CLASSIFIER-FIX]`;
  `.project/active/matrix-truth/design.md` (xfail re-frame, D4);
  `docs/architecture/reference/01-extraction.md`, `.../16-computed-attributes.md`
- **Substrate found:** `src/sysml_codegen/extraction/usage_extractor.py:197-218` (`_supertype_closure`)

## Research Findings

**The classifier and the bug.** `_classify_attribute_expression`
(`computed_attribute_extractor.py:64-163`) classifies each feature ref by QN. Step-2b
(`:123`) calls a ref a sibling iff `qn.startswith(owning_part_qn + "::")`. SysIDE resolves
an inherited attr's QN into the **supertype** namespace, so `base_rate` on `'Derived
Component'` is `…::'Base Component'::base_rate` — the prefix check fails, it falls to
Step-2c as a `calc_ref` (`:127`), and a non-empty `calc_refs` forces EXPOSE_COMPUTED
(`:163`).

**Reachability gate — PASSES (proven, not just probable).** The owning part's ancestor
PartDef QNs are reachable from `part_element` alone. The codebase already walks PartDef
supertypes transitively in `_supertype_closure` (`usage_extractor.py:197-218`): iterate
`part_element.heritage` → `(relationship, target)` pairs, keep the ones where
`SysideAdapter.is_instance(relationship, "Subclassification")` (a `:>` generalization),
recurse on each `target` element. `target.qualified_name` yields the raw `::`-form QN
(`UnresolvableAttrProbeLibrary::'Base Component'`) — the *same* format as `ref.qualified_name`
and as the classifier's existing `owning_part_qualified_name` (`:194`), so a prefix match
is apples-to-apples. **Do not** route through `build_element_qualified_name(target)` — that
returns the sanitized `__`-form and would never match the `::`-form ref QNs.

**No serialized field exists or is needed.** `PartDefinitionData` (`data_models.py:97-118`)
carries no supertype field, and `_extract_part_definition` (`extractor.py:183-218`) never
reads `heritage`. Classification runs **live during extraction** and only its *result* is
serialized. So the ancestor set is a transient input to classification — computed on the
fly, never stored. This is what keeps every other snapshot byte-identical.

**The compile consequence (pinned by reading the compiler).** After the flip, the 5 attrs
become FORMULA and hit compilation. Their inherited refs (`base_rate`, `base_factor`) are
**not** in the compiler's `input_names` — that set is built from `owned_members`, which by
SysML v2 semantics excludes inherited attrs (`computed_attribute_extractor.py:188-191`,
`247-249`). A name absent from `input_names` compiles to `UNSUPPORTED`
(`expression_compiler.py:384-392`) → `compile_expression` raises `CompilationError` (`:209`)
→ the extractor catches it and sets `compilability=MANUAL_REQUIRED`, `compiled_expression=None`,
and logs a "FORMULA compilation failed" warning (`:259-267`). So all five land
**FORMULA + MANUAL_REQUIRED + compiled=None**, and the *only* value that moves in the
committed JSON is `classification`.

**Where the silence actually is (corrected — this drove the review).** That capture-time
"FORMULA compilation failed" warning is **not serialized**, and it does not make the
*generation* boundary loud. The graph builder's computed-attribute loop builds a module only
for `FORMULA and compilability == FULLY_COMPILABLE` (`graph_builder.py:271-274`); its single
`elif` handles `EXPOSE_CHAIN_TENTATIVE`; there is **no `else`**. So a `FORMULA +
MANUAL_REQUIRED` attr falls through `graph_builder.py:269-288` with no module, no `raise`, no
warning — the *same* silent no-op the spec pins as the original EXPOSE_COMPUTED sin, now
reached by a different branch. `generate --from-snapshot` (the license-free path) re-runs no
extraction, so it sees zero signal. The real win of the classification fix is therefore
**correct classification**, not a louder failure — and the residual generation-time silence is
addressed head-on by D5 below, not waved away.

**Corpus scan for the D5 scope call (evidence).** A new graph-builder diagnostic (WARN when a
FORMULA attr reaches module-build without compiling) would fire on any committed fixture that
carries a FORMULA + MANUAL_REQUIRED computed attribute today. Scanning every committed
`extraction_snapshot.json`: only **four** fixtures have any FORMULA computed attr at all
(`attr_expr_probe`, `deep_cross_scope_probe`, `quoted_owner_formula`, `solar_battery_model`),
and of those only **`deep_cross_scope_probe`** has one that is MANUAL_REQUIRED (the rest are
all FULLY_COMPILABLE). `deep_cross_scope_probe` is a **probe / drift-pin** fixture that already
emits LOUD-REJECT warnings by design (D3-2, `test_deep_cross_scope_probe.py:83-99`) — it is
**not** in the INV-6 zero-WARNING clean sweep. Every clean corpus model (fusion_tea, wi014_toy,
ife_plant, solar_battery_model, plant_values, quoted_owner_formula, …) carries **zero**
FORMULA + MANUAL_REQUIRED attrs. So the diagnostic fires only on dirty/probe fixtures →
per the orchestrator ruling, it is added in this item (D5).

**The snapshot content (exact diff target).** `unresolvable_attr_probe/extraction_snapshot.json`
bakes 6 computed attrs, all `"classification": "expose_computed"`. The 6 refs and their QNs
(read from the JSON) decide each flip:

| Case | owning part | expr | inherited refs (QN namespace) | post-fix |
|------|-------------|------|-------------------------------|----------|
| L1 | Derived_Component | `base_rate * base_factor` | both in `'Base Component'` | **FORMULA** |
| L2 | Derived_Component | `base_rate * local_multiplier` | `base_rate`→Base; `local_multiplier`→own | **FORMULA** |
| D1 | Design_Derived | `base_rate * base_factor` | both in `'Base Component'` | **FORMULA** |
| D2 | Design_Derived | `base_rate * local_val` | `base_rate`→Base; `local_val`→own | **FORMULA** |
| D3 | Design_Derived | `my_calc.result * base_rate` | `result`→`SimpleCalc` (CalcDef, **not** ancestor) | **EXPOSE_COMPUTED** (unchanged) |
| D4 | Design_Derived | `base_rate + base_factor + local_val` | two in `'Base Component'`; `local_val`→own | **FORMULA** |

D3 is safe because `SimpleCalc` is a CalcDef, never in `ancestor_part_qns` (`{'…Base Component'}`),
so `result` stays a `calc_ref` and `calc_refs` stays non-empty → EXPOSE_COMPUTED.

## Core Concept

The classifier already answers one question — *"is this reference a sibling attribute on my
own part?"* — with one test: does the ref's QN start with my part's QN. The bug is that
"my own part" is too narrow: an inherited attribute genuinely *is* mine, but SysIDE files it
under the supertype's QN. The fix widens the notion of "mine" from a single prefix to a small
set of prefixes — my part **plus each ancestor PartDef** — and answers the same question
against that set. The ancestor set is not new data to store; it is a three-line transitive
walk of the raw element's `heritage` we already do elsewhere. Everything else — the LITERAL
short-circuit, the calc-ref decision, the multi-hop tentative gate, the EXPOSE variants —
is untouched. The classifier change itself is *one predicate, one new transient input*, plus
the honest bookkeeping that follows: re-capture the one fixture whose baked classifications now
change, collapse the test table to record the post-fix truth, and correct the docs/matrix that
described the (now-fixed) bug — including the loud→silent severity inversion.

Correct classification is the win, but it does not by itself make the pipeline loud: a
FORMULA that can't compile still drops silently at the graph builder. So the fix carries a
second, small move (D5): a graph-builder diagnostic that WARNs when a FORMULA computed
attribute reaches module-build without compiling — turning that silent drop loud. The corpus
scan shows this fires only on probe fixtures, never on a clean model, so it is safe to add
here as an R1 fires-on-shape + silent-on-clean pair rather than deferred.

Key insight: because classification is computed live and only its result is serialized,
a code-only predicate change is **invisible to the suite** until the fixture snapshot is
re-captured — and **inert for every other baseline** precisely because they are *not*
re-captured. The same fact gives us both the required snapshot churn and the byte-identity
guarantee for everything else.

## Key Bets

- **B1.** SysIDE reports the supertype PartDef's `qualified_name` in the same `::`-form (quotes
  and spaces preserved) that it uses for `ref.qualified_name` on inherited attrs, so
  `ancestor_qn + "::"` is a valid prefix of the inherited ref QN. *If false → the prefix match
  never fires, the 5 cases stay EXPOSE_COMPUTED, and Phase 0 re-capture shows no flip.* (Strongly
  supported: both strings come from the same `.qualified_name` attribute; the JSON already shows
  `owning_part_qualified_name` and ref QNs sharing the `::`+quotes form. Phase 0 confirms.)
- **B2.** `part_element.heritage` on a PartDefinition exposes its `:>` generalization as a
  `Subclassification` relationship whose `target` is the supertype PartDef element. *If false →
  `ancestor_part_qns` is empty and nothing flips.* Scope of confidence: **depth-1 is proven** —
  the `heritage`→`Subclassification`→`target` step is the exact step `_supertype_closure`
  (`usage_extractor.py:211-214`) and other walkers (`extractor.py:398-401`) run live, and the
  fixture is single-level (`Derived :> Base`). The **transitive** step in our walk is a *new
  variation* (see D2/D5 note): `_supertype_closure` recurses by re-resolving each supertype QN
  through a prebuilt `qn_to_partdef` map and so **prunes at the user-model boundary**; our leaf
  has no such map and instead recurses on the raw `target` element, which also descends into
  library supertypes. That is harmless for prefix matching (a stdlib QN is never the namespace
  of a user inherited-attr ref) but is broader, and multi-level user inheritance is not exercised
  by the current fixture. D2's note requires exercising it (a depth-2 fixture case).
- **B3.** No baseline snapshot other than `unresolvable_attr_probe` contains a computed
  attribute that references (a) an inherited attr **or (b) a CalcDef nested under an ancestor
  PartDef** (the D3-boundary over-correction route), so re-capturing only that fixture cannot
  desync any other baseline. *If false → some baseline is silently stale after this item (its
  committed JSON still says EXPOSE_COMPUTED while live extraction would now say FORMULA — or,
  for (b), vice-versa).* (Must be **verified**, not assumed — see Validation. Byte-identity gate
  is inert here because we don't re-capture those; the risk is latent, surfacing only on a future
  re-capture. R4 says reproduce, don't static-read.)

## Key Decisions

- **D1. Classification-only for the compiler; do not teach it about inherited inputs.** The
  five flip to FORMULA and stay MANUAL_REQUIRED (inherited refs remain outside `input_names`, so
  they don't compile to a module). *Rejected: also threading inherited attr names into
  `input_names` so they compile to real modules.* Reasons: (a) the spec scopes the item to
  **classification** (SC-1 says "classifies FORMULA, not EXPOSE_COMPUTED" — never "produces a
  module"); (b) it matches existing behavior — a FORMULA referencing a non-input name is already
  UNSUPPORTED → MANUAL_REQUIRED (REQ-CA-08, doc 16:355-363); (c) it keeps the committed JSON diff
  to exactly the 5 `classification` strings, nothing else.
  **(d) — corrected from the prior draft.** The prior draft claimed this converts a silent drop
  into a loud warning, "strictly better on severity." That is **false at the boundary that
  matters**: the only new signal is a non-serialized capture-time log; at generation the
  `FORMULA + MANUAL_REQUIRED` attr still drops silently through `graph_builder.py:269-288`, and
  `generate --from-snapshot` sees nothing. So the honest claim is narrower — **the win is
  correct classification; the module is still not produced; the generation-time drop is still
  silent under D1 alone.** The "loud" is delivered separately and deliberately by D5, not by D1.
  Making the attrs actually *compile* remains a filed follow-on (see Non-Goals).
- **D2. Compute `ancestor_part_qns` inside `extract_computed_attributes`, pass it as a new
  parameter to `_classify_attribute_expression`.** *Rejected: extract supertypes during part
  extraction into `PartDefinitionData` and serialize.* Serializing a new field rewrites every
  snapshot → breaks the byte-identity carve-out. The ancestor set is transient classification
  input; it belongs where classification happens. **Walk shape (not a `_supertype_closure`
  clone):** it recurses on raw `target` elements and returns `::`-form QNs, where
  `_supertype_closure` recurses through a `qn_to_partdef` map and returns `__`-form — two
  deliberate divergences (the leaf has no map; the classifier needs `::`-form). Name the
  divergence in the code so a future reader does not "unify" the two walkers and reintroduce the
  `__`-form trap. To exercise the transitive step (B2), **add one depth-2 case to the fixture**
  (`Derived2 :> Derived :> Base`, a computed attr referencing a grandparent attr) so a 2-level
  ancestor chain is a real PASS, not an assumed one.
- **D3. Widen Step-2b to `startswith(own_prefix) OR any(startswith(ancestor_prefix))`.**
  *Rejected: "accept any non-owning namespace as sibling."* That reclassifies genuine calc
  refs (D3-fixture's `result`) and breaks the EXPOSE_COMPUTED case. Only **ancestor PartDef** QNs
  are accepted (the spec's [HARD] boundary). **The real invariant (corrected from "an
  ancestor-prefix QN never belongs to a calc-output ref"):** a calc output resolves to its
  *CalcDef's* namespace, so the D3 fixture stays EXPOSE_COMPUTED because `SimpleCalc` is
  top-level and never in the ancestor set. The one over-correction route is a **CalcDef nested
  inside an ancestor PartDef** (`part def Base { calc def Foo { out result; } }`), whose output QN
  `…::'Base'::Foo::result` *does* start with the ancestor prefix `…::'Base'::` and would be
  swallowed as a sibling. We do **not** add predicate complexity to exclude it, because: (i) it
  is not a regression — a CalcDef nested in the *owning* part already behaves this way under the
  existing prefix check, so this only extends a pre-existing behavior to ancestors; (ii) the
  shape is absent from the corpus (folded into the B3 grep); (iii) matching the owning-part
  semantics keeps the predicate consistent. If the grep finds the shape, revisit before landing.
- **D5. Add a graph-builder diagnostic: WARN when a FORMULA computed attribute reaches
  module-build without being FULLY_COMPILABLE (no module produced).** This is the honest delivery
  of "loud" — it fires at `graph_builder.py:269-288`, the exact silent site, on the live
  *generation* path (and any from-snapshot generation of such an attr), retiring the silent drop
  D1 leaves. *Rejected: defer it as filed follow-on.* The orchestrator ruling gates this on
  evidence: the corpus scan (Research Findings) shows the diagnostic fires only on the
  `deep_cross_scope_probe` probe fixture (already a warns-by-design drift pin), never on a clean
  corpus model, so INV-6 (clean fixtures generate zero WARNINGs) is preserved — the condition for
  adding rather than deferring. Ships with an R1 fires-on-shape + silent-on-clean test pair.
  *Rejected alternative for the diagnostic site: warn at extraction instead.* The extraction
  warning already exists but isn't serialized and doesn't cover from-snapshot; the graph builder
  is the boundary both paths share.
- **D4. Collapse `INHERITED_ATTR_PATTERNS` to a single authoritative classification column and
  delete `test_misclassification_documented`.** *Rejected: keep the two-column
  (actual, correct) table and the xfail test.* Post-fix `actual == correct` for every row, so
  the two columns are redundant and the xfail test's `v[0] != v[1]` filter collapses to zero
  cases — the exact "green empty parametrization" trap the spec's [HARD] no-fake-test names.
  A single column recording post-fix truth cannot collapse and cannot silently vacate.

## Architecture

Two code sites change. Data flow:

```
# Site 1 (extraction leaf — the classification fix)
extract_computed_attributes(adapter, part_element, calc_usage_names)
  ├─ ancestor_part_qns = _ancestor_part_qns(part_element, adapter)   # NEW, transient
  │     walk part_element.heritage → Subclassification targets → target.qualified_name, recurse
  └─ for each AttributeUsage:
        _classify_attribute_expression(..., ancestor_part_qns=ancestor_part_qns)   # NEW param
            Step-2b: qn.startswith(own_prefix) OR any ancestor_prefix → sibling_ref

# Site 2 (resolution — the loud diagnostic, D5)
build_computation_graph(...)  # Step 6.5 loop, graph_builder.py:269-288
  for ca in computed_attributes:
     FORMULA and FULLY_COMPILABLE   → build module        (unchanged)
     EXPOSE_CHAIN_TENTATIVE         → raise (INV-F)        (unchanged)
     FORMULA and not FULLY_COMPILABLE → WARN "no module" + skip   # NEW (D5)
```

No change to `data_models.py`, the snapshot schema, or any other extractor. The classifier
result flows into the serialized `ComputedAttributeData.classification` (what the conformance
fixture reads after re-capture); the D5 warning is a runtime log, not serialized, so no
generated-code bytes or snapshots move.

**Test/doc surface (same change, R1):**
- `tests/conformance/test_computed_attributes.py` — collapse the table; rewrite the two consumer
  tests into positive assertions; delete the xfail test; keep the root-cause pin; **add a
  positive pin that the 5 FORMULA cases are MANUAL_REQUIRED + `compiled_expression=None`, and
  re-key `test_no_compiled_expressions` to the FORMULA set so it doesn't silently narrow 6→1**
  (should-fix #2).
- `tests/.../` (D5 pair) — a **fires-on-shape** test (a FORMULA + MANUAL_REQUIRED
  `ComputedAttributeData` through `build_computation_graph` → warning emitted, no module) and a
  **silent-on-clean** test (a FULLY_COMPILABLE FORMULA → module built, no warning). A crafted
  `ComputedAttributeData` unit test is cleaner than routing through a fixture.
- `tests/fixtures/unresolvable_attr_probe/{library,design}.sysml` + `extraction_snapshot.json` —
  re-captured; the 5 classification strings flip, plus the new depth-2 case (D2/B2).
- `docs/architecture/reference/16-computed-attributes.md` — Known-Issues → fixed; pseudocode
  `⚠ KNOWN BUG` (`:133`) and the supertype-namespace note (`~:114-117`) updated; the Impact
  section's "silent no-ops" description confirmed and tied to the new D5 diagnostic.
- `docs/architecture/verification-matrix.md:136` — "Known contract (Item 7)" block rewritten,
  the "**loud** (EXPOSE_COMPUTED rejection)" phrase corrected toward silent (cited to
  `graph_builder.py:269-288` / the e2e test); new positive REQ-CA row.
- `.project/backlog/epic_truth_debt.md` — sweep **every** "loud" tied to this misclassification,
  not just one line: the summary "classifier fix behind a loud xfail" (`:16`), the overview
  "Five xfail cases lock a **loud** … misclassification" (`:41`), and the Item-4 "The
  misclassification is **loud** (rejection, not silent…)" (`:340`) — all corrected toward silent,
  cited (note #5).

## Required Invariants

- **INV-1 (D3 negative control):** `mixed_expose` stays EXPOSE_COMPUTED. A ref whose QN is
  under a top-level CalcDef namespace is never in `ancestor_part_qns` (the one exception —
  a CalcDef nested under an ancestor PartDef — is bounded by D3 and B3, not by this invariant).
- **INV-2 (byte-identity carve-out):** every baseline/snapshot byte-identical **except**
  `tests/fixtures/unresolvable_attr_probe/` (its `{library,design}.sysml` gain the depth-2 case,
  and `extraction_snapshot.json` is re-captured). Within the snapshot the change is: the 5
  existing `classification` values flip (`expose_computed`→`formula`), D3 unchanged,
  `compilability`/`compiled_expression` unchanged for all pre-existing rows, **plus** the new
  depth-2 computed-attr object (FORMULA + MANUAL_REQUIRED) and its design-attribute entry;
  `captured_at` re-verified (timestamp-only diff reverted per memory `byte-identity-captured-at-churn`).
  It is a reviewed R3 diff, not a blind one; the "5 strings only" simplification from the prior
  draft is superseded by the depth-2 addition (D2/B2).
- **INV-3 (no fake test):** the FORMULA cases exist as real, positively-asserting parametrized
  cases keyed on a literal `FORMULA` expectation; the set never collapses to zero. Post-change
  the table has 7 rows — 6 FORMULA (L1,L2,D1,D2,D4 + the depth-2 case) and 1 EXPOSE_COMPUTED (D3).
- **INV-4 (root cause still true):** inherited refs still carry supertype-namespace QNs after
  the fix — the fix *reinterprets* them, it does not change SysIDE. `test_inherited_refs_have_supertype_qn`
  stays green and anchors *why* the widening is needed.
- **INV-5 (loud at the generation boundary, D5):** a `FORMULA` computed attribute that reaches
  the graph-builder loop without being `FULLY_COMPILABLE` emits a WARN and produces no module —
  never a silent fall-through. Proven by the fires-on-shape test.
- **INV-6 preserved (clean fixtures still zero-WARNING):** the D5 diagnostic fires only on a
  FORMULA+MANUAL_REQUIRED shape, which the corpus scan shows exists only in probe fixtures
  (`deep_cross_scope_probe`), never in a clean corpus model. Proven by the silent-on-clean test.

## Component Overview

- **`_ancestor_part_qns(part_element, adapter) -> set[str]`** (new, module-private in
  `computed_attribute_extractor.py`): transitive `heritage`/`Subclassification` walk returning
  raw `::`-form supertype QNs. **Deliberately not** a `_supertype_closure` clone — it recurses on
  raw `target` elements (no `qn_to_partdef` map, so it also descends into library supertypes) and
  returns `::`-form, not `__`-form. A code comment must name this divergence so the two walkers
  aren't later unified (which would reintroduce the `__`-form trap).
- **`_classify_attribute_expression`** (edit): gains `ancestor_part_qns: set[str]`; Step-2b
  predicate widened (D3).
- **`extract_computed_attributes`** (edit): computes the ancestor set once per part, threads it in.
- **Graph-builder Step-6.5 loop** (edit, D5): add the `FORMULA and not FULLY_COMPILABLE → WARN +
  skip` branch at `graph_builder.py:269-288`. The warning names the attr and that no module was
  produced; keep the existing FULLY_COMPILABLE and EXPOSE_CHAIN_TENTATIVE arms untouched.
- **`INHERITED_ATTR_PATTERNS` + `TestInheritedAttrClassification`** (edit): single-column table,
  7 rows; `test_inherited_attr_classification` asserts the literal classification for all rows
  (6 FORMULA + D3 EXPOSE_COMPUTED); `test_misclassification_documented` deleted;
  `test_inherited_refs_have_supertype_qn` kept (docstring reworded to "now treated as sibling");
  **`test_no_compiled_expressions` re-keyed** to also assert the 6 FORMULA rows are
  MANUAL_REQUIRED + `compiled_expression=None` (was: only EXPOSE_COMPUTED rows — which post-fix
  narrows to D3 alone, should-fix #2).
- **D5 test pair** (new): a fires-on-shape and a silent-on-clean test over `build_computation_graph`
  with crafted `ComputedAttributeData` inputs (INV-5 / INV-6).

## Non-Goals

- **Compiling inherited-attr FORMULAs into modules.** Left MANUAL_REQUIRED (D1). With D5 the
  no-module outcome is now *loud*, but making them actually compile (thread inherited names into
  `input_names` so a real module is built) is a separate, filed follow-on — file
  `[TRUTH-DEBT-INHERITED-FORMULA-COMPILE]` in BACKLOG naming the `input_names` enrichment.
- **Tightening the predicate against a nested CalcDef under an ancestor PartDef** (D3). Not done —
  it is not a regression (mirrors existing owning-part behavior) and is absent from the corpus
  (B3 grep). Revisit only if the grep finds the shape.
- **EXPOSE_COMPUTED decomposition** (the D3-fixture shape) — stays deferred per spec.
- **Any behavior change for non-inheritance models** — guaranteed by scoping re-capture to the
  one fixture, not by assuming no model uses `:>`; and by D5 firing only on the probe shape.
- **The UNRESOLVABLE "dead code" disposition** (doc 16:410-419) — out of scope.

## Implementation Notes

- Ancestor walk shape (pseudocode, ~10 lines — recurse on elements, `::`-form QN):
  ```python
  def _ancestor_part_qns(part_element, adapter) -> set[str]:
      result, stack = set(), [part_element]
      while stack:
          for rel, target in getattr(stack.pop(), "heritage", []):
              if not adapter.is_instance(rel, "Subclassification"):
                  continue
              qn = str(getattr(target, "qualified_name", "") or "")
              if qn and qn not in result:
                  result.add(qn); stack.append(target)
      return result
  ```
- Step-2b widening: build `ancestor_prefixes = tuple(a + "::" for a in ancestor_part_qns)`;
  sibling iff `qn.startswith(part_qn_prefix) or qn.startswith(ancestor_prefixes)`
  (`str.startswith` accepts a tuple). Keep 2c/2d unchanged.
- `is_instance` is a **static** method already called statically in this module
  (`:57`); calling it via the `adapter` instance or the class is equivalent — match the
  surrounding style (`SysideAdapter.is_instance`).
- Depth-2 fixture case (D2/B2): add a `part def 'Grandchild' :> 'Derived Component'` with a
  computed attr referencing a **grandparent** attr (`base_rate`), so the transitive ancestor
  walk (`Grandchild → Derived → Base`) is a real PASS. This is what lifts B2 from "depth-1
  proven" to "transitive exercised."
- Re-capture command (R3, one fixture only):
  `uv run python scripts/capture_extraction_snapshots.py unresolvable_attr_probe`
  (the `requested` positional scopes regen; the fixture is in `EXTRACTION_ONLY_MODELS`,
  `:118`). Needs the syside license — runs via the capture script, not a bare `-c` probe
  (memory: `syside-license-via-scripts-not-dashc`).
- Expect "FORMULA compilation failed … unresolved reference: base_rate/base_factor" warnings
  during re-capture (one per inherited ref). Not serialized; no conformance test asserts
  zero-warnings on this extraction-only probe — but confirm no `caplog` gate covers it.
- D5 lands a *new* warning during generation of `deep_cross_scope_probe` (its existing
  FORMULA+MANUAL_REQUIRED attr). Confirm its test uses an `any()`/subset warning check
  (`test_deep_cross_scope_probe.py:97-99` does), not an exact-set/count assertion, so the added
  warning doesn't break it; its committed `baseline_outputs/` bytes are unaffected (warnings
  aren't generated code).

## Potential Risks

- **QN-format mismatch (B1).** If the supertype `.qualified_name` differs in quoting from the
  ref QN, the prefix fails silently. *Mitigation:* Phase 0 re-capture is the test — a non-flip
  is the signal. Cheap to see.
- **Latent baseline staleness (B3).** A corpus/`fusion_tea` computed attr referencing an
  inherited attr — **or a CalcDef nested under an ancestor PartDef** (the D3 over-correction
  route) — would be a ticking desync (fine now, flips on a future re-capture). *Mitigation:*
  grep the corpus for both shapes (or re-capture-and-diff `fusion_tea` once) and record the
  verdict; if either exists, widen scope deliberately.
- **Table-collapse regression (INV-3).** *Mitigation:* the single-column test asserts a literal
  expectation over a fixed 7-row set; add a guard `len(INHERITED_ATTR_PATTERNS) == 7` and
  `sum(1 for v in INHERITED_ATTR_PATTERNS.values() if v[0] == FORMULA) == 6` so an accidental
  empty/short table fails loudly.
- **D5 warning breaks an unrelated fixture's warning assertion.** *Mitigation:* only
  `deep_cross_scope_probe` gains a warning (corpus scan); its test uses a subset check, not an
  exact set/count. Run the full suite after adding D5; if any exact-warning assertion trips,
  it named a previously-silent drop and should be updated to include the new loud line.

## Integration Strategy

Drop-in within the extraction leaf. No new module, no schema change, no cross-layer coupling
(the module stays a leaf per its header contract). Complements the existing `heritage` walkers
(`usage_extractor.py`, `extractor.py`) by reusing their proven pattern rather than adding a
parallel mechanism. Replaces the filed debt (xfail + Known-Issues + matrix "known contract")
with a positively-pinned contract.

## Validation Approach

1. **Phase 0 (gate → confirm):** add the depth-2 fixture case, then re-capture; assert the 5
   existing rows flip to `formula`, the depth-2 row lands `formula`, D3 stays `expose_computed`.
   This simultaneously confirms B1 (QN format) and B2 (transitive walk) and produces the
   committed diff.
2. **Classification suite:** `test_inherited_attr_classification` green with literal expectations
   (6 FORMULA + D3); `test_no_compiled_expressions` green over the 6 FORMULA (MANUAL_REQUIRED +
   `compiled=None`) and D3; `test_inherited_refs_have_supertype_qn` green; xfail test gone.
3. **D5 suite:** fires-on-shape (FORMULA+MANUAL_REQUIRED → warning, no module) and silent-on-clean
   (FULLY_COMPILABLE → module, no warning) both green; full suite green including
   `deep_cross_scope_probe`.
4. **Byte-identity gate:** run the repo's snapshot diff; only the `unresolvable_attr_probe/`
   files move (the reviewed R3 diff of INV-2); every other baseline byte-identical
   (`captured_at` timestamp-only churn reverted).
5. **B3 verification:** corpus grep for both shapes (inherited-attr computed attrs; CalcDef nested
   under an ancestor PartDef) / `fusion_tea` re-capture-and-diff; record verdict in the plan.
6. **Gates:** ruff ≤ 17, mypy ≤ 104; matrix recounted from rows.

## Next-Stage Handoff

- **Fixed:** the predicate (D3), the plumbing (D2), classification-only compiler scope (D1), the
  loud diagnostic (D5), the table collapse + xfail deletion (D4), the R1 doc/matrix/epic set
  (incl. the full "loud" sweep at epic `:16`/`:41`/`:340` + matrix `:136`).
- **Open (Phase 0 resolves):** exact QN-format confirmation (B1); transitive-walk confirmation
  at depth-2 (B2); the precise re-captured diff.
- **De-risk first:** run Phase 0 re-capture (with the depth-2 case) before touching tests/docs —
  the item is contingent on the rows actually flipping. If they don't, stop and re-probe QN
  format. Land D5 second, after the classification flip is green, so a D5 test failure is never
  confounded with a classification miss.

---
Next Step: After approval → `/_my_plan` (Phase 0 re-capture is the first plan step and the gate).
