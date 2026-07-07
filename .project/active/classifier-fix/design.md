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
The ancestor set is computed transiently during extraction; nothing new is serialized.

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
committed JSON is `classification`. See "Key Decisions / D1" for why we stop there.

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
is untouched. The change is *one predicate, one new transient input*, plus the honest
bookkeeping that follows: re-capture the one fixture whose baked classifications now change,
collapse the test table to record the post-fix truth, and correct the docs/matrix that
described the (now-fixed) bug — including the loud→silent severity inversion.

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
  `ancestor_part_qns` is empty and nothing flips.* (Strongly supported: `_supertype_closure` is
  live-exercised for REQ-LVP-08 via this exact walk.)
- **B3.** No baseline snapshot other than `unresolvable_attr_probe` contains a computed
  attribute that references an inherited attr, so re-capturing only that fixture cannot desync
  any other baseline. *If false → some baseline is silently stale after this item (its committed
  JSON still says EXPOSE_COMPUTED while live extraction would now say FORMULA).* (Must be
  **verified**, not assumed — see Validation. Byte-identity gate is inert here because we don't
  re-capture those; the risk is latent, surfacing only on a future re-capture. R4 says reproduce,
  don't static-read.)

## Key Decisions

- **D1. Classification-only; do not teach the compiler about inherited inputs.** The five flip
  to FORMULA and stay MANUAL_REQUIRED (inherited refs remain outside `input_names`, so they
  don't compile to a module). *Rejected: also threading inherited attr names into `input_names`
  so they compile to real modules.* Reasons: (a) the spec scopes the item to **classification**
  (SC-1 says "classifies FORMULA, not EXPOSE_COMPUTED" — never "produces a module"); (b) it
  matches existing behavior — a FORMULA referencing a non-input name is already UNSUPPORTED →
  MANUAL_REQUIRED (REQ-CA-08, doc 16:355-363); (c) it keeps the committed JSON diff to exactly
  the 5 `classification` strings, nothing else; (d) it converts the old **silent** EXPOSE_COMPUTED
  drop into a **loud** FORMULA-compile-failure warning, which is strictly better on the very
  severity axis this item corrects. Making them compile is a legitimate follow-on, filed, not
  done here (see Non-Goals).
- **D2. Compute `ancestor_part_qns` inside `extract_computed_attributes`, pass it as a new
  parameter to `_classify_attribute_expression`.** *Rejected: extract supertypes during part
  extraction into `PartDefinitionData` and serialize.* Serializing a new field rewrites every
  snapshot → breaks the byte-identity carve-out. The ancestor set is transient classification
  input; it belongs where classification happens.
- **D3. Widen Step-2b to `startswith(own_prefix) OR any(startswith(ancestor_prefix))`.**
  *Rejected: "accept any non-owning namespace as sibling."* That reclassifies genuine calc
  refs (D3's `result`) and breaks the EXPOSE_COMPUTED case. Only **ancestor PartDef** QNs are
  accepted (the spec's [HARD] boundary).
- **D4. Collapse `INHERITED_ATTR_PATTERNS` to a single authoritative classification column and
  delete `test_misclassification_documented`.** *Rejected: keep the two-column
  (actual, correct) table and the xfail test.* Post-fix `actual == correct` for every row, so
  the two columns are redundant and the xfail test's `v[0] != v[1]` filter collapses to zero
  cases — the exact "green empty parametrization" trap the spec's [HARD] no-fake-test names.
  A single column recording post-fix truth cannot collapse and cannot silently vacate.

## Architecture

Single leaf module changes: `extraction/computed_attribute_extractor.py`. Data flow:

```
extract_computed_attributes(adapter, part_element, calc_usage_names)
  ├─ ancestor_part_qns = _ancestor_part_qns(part_element, adapter)   # NEW, transient
  │     walk part_element.heritage → Subclassification targets → target.qualified_name, recurse
  └─ for each AttributeUsage:
        _classify_attribute_expression(..., ancestor_part_qns=ancestor_part_qns)   # NEW param
            Step-2b: qn.startswith(own_prefix) OR any ancestor_prefix → sibling_ref
```

No change to `graph_builder.py`, `data_models.py`, the snapshot schema, or any other extractor.
The classifier result flows into the serialized `ComputedAttributeData.classification`, which
is what the conformance fixture reads after re-capture.

**Test/doc surface (same change, R1):**
- `tests/conformance/test_computed_attributes.py` — collapse the table; rewrite the two consumer
  tests into positive assertions; delete the xfail test; keep the root-cause pin.
- `tests/fixtures/unresolvable_attr_probe/extraction_snapshot.json` — re-captured (5 strings).
- `docs/architecture/reference/16-computed-attributes.md` — Known-Issues → fixed; pseudocode
  `⚠ KNOWN BUG` (`:133`) and the supertype-namespace note (`~:114-117`) updated.
- `docs/architecture/verification-matrix.md:136` — "Known contract (Item 7)" block rewritten,
  loud→silent corrected; new positive REQ-CA row.
- `.project/backlog/epic_truth_debt.md` — Item-4 "loud (rejection, not silent…)" text
  (`:340`) corrected toward silent, cited.

## Required Invariants

- **INV-1 (D3 negative control):** `mixed_expose` stays EXPOSE_COMPUTED. A ref whose QN is
  under a CalcDef namespace is never in `ancestor_part_qns`.
- **INV-2 (byte-identity carve-out):** every baseline/snapshot byte-identical **except**
  `unresolvable_attr_probe/extraction_snapshot.json`; within that file, only 5 `classification`
  values move (`expose_computed`→`formula`), D3 unchanged, `compilability`/`compiled_expression`
  unchanged, `captured_at` re-verified (timestamp-only diff reverted per memory
  `byte-identity-captured-at-churn`).
- **INV-3 (no fake test):** the five FORMULA cases exist as real, positively-asserting
  parametrized cases keyed on a literal `FORMULA` expectation; the set never collapses to zero.
- **INV-4 (root cause still true):** inherited refs still carry supertype-namespace QNs after
  the fix — the fix *reinterprets* them, it does not change SysIDE. `test_inherited_refs_have_supertype_qn`
  stays green and anchors *why* the widening is needed.

## Component Overview

- **`_ancestor_part_qns(part_element, adapter) -> set[str]`** (new, module-private in
  `computed_attribute_extractor.py`): transitive `heritage`/`Subclassification` walk returning
  raw `::`-form supertype QNs. Mirrors `_supertype_closure` but recurses on elements (no
  `qn_to_partdef` map) and returns `::`-form (not `__`-form).
- **`_classify_attribute_expression`** (edit): gains `ancestor_part_qns: set[str]`; Step-2b
  predicate widened (D3).
- **`extract_computed_attributes`** (edit): computes the ancestor set once per part, threads it in.
- **`INHERITED_ATTR_PATTERNS` + `TestInheritedAttrClassification`** (edit): single-column table;
  `test_inherited_attr_classification` asserts the literal classification for all 6 rows (5
  FORMULA + D3 EXPOSE_COMPUTED); `test_misclassification_documented` deleted;
  `test_inherited_refs_have_supertype_qn` kept (docstring reworded to "now treated as sibling").

## Non-Goals

- **Compiling inherited-attr FORMULAs into modules.** Left MANUAL_REQUIRED (D1). Making them
  fully compilable (thread inherited names into `input_names`) is a separate, filed follow-on.
- **EXPOSE_COMPUTED decomposition** (the D3 shape) — stays deferred per spec.
- **Any behavior change for non-inheritance models** — guaranteed by scoping re-capture to the
  one fixture, not by assuming no model uses `:>`.
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
- Re-capture command (R3, one fixture only):
  `uv run python scripts/capture_extraction_snapshots.py unresolvable_attr_probe`
  (the `requested` positional scopes regen; the fixture is in `EXTRACTION_ONLY_MODELS`,
  `:118`). Needs the syside license — runs via the capture script, not a bare `-c` probe
  (memory: `syside-license-via-scripts-not-dashc`).
- Expect 5 "FORMULA compilation failed … unresolved reference: base_rate/base_factor"
  warnings during re-capture. These are not serialized and no conformance test asserts
  zero-warnings on this extraction-only probe — but confirm no `caplog` gate covers it.

## Potential Risks

- **QN-format mismatch (B1).** If the supertype `.qualified_name` differs in quoting from the
  ref QN, the prefix fails silently. *Mitigation:* Phase 0 re-capture is the test — a non-flip
  is the signal. Cheap to see.
- **Latent baseline staleness (B3).** A corpus/`fusion_tea` computed attr referencing an
  inherited attr would be a ticking desync (fine now, flips on a future re-capture).
  *Mitigation:* grep the corpus for inherited-attr computed attributes (or re-capture-and-diff
  `fusion_tea` once) and record the verdict; if any exist, widen scope deliberately.
- **Table-collapse regression (INV-3).** *Mitigation:* the single-column test asserts a literal
  expectation over a fixed 6-row set; add a guard `len(INHERITED_ATTR_PATTERNS) == 6` and
  `sum(v[0] == FORMULA) == 5` so an accidental empty/short table fails loudly.

## Integration Strategy

Drop-in within the extraction leaf. No new module, no schema change, no cross-layer coupling
(the module stays a leaf per its header contract). Complements the existing `heritage` walkers
(`usage_extractor.py`, `extractor.py`) by reusing their proven pattern rather than adding a
parallel mechanism. Replaces the filed debt (xfail + Known-Issues + matrix "known contract")
with a positively-pinned contract.

## Validation Approach

1. **Phase 0 (gate → confirm):** re-capture the fixture; assert the 5 flip to `formula` and D3
   stays `expose_computed`. This simultaneously confirms B1/B2 and produces the committed diff.
2. **Suite:** `test_inherited_attr_classification` green with literal expectations (5 FORMULA +
   D3); `test_inherited_refs_have_supertype_qn` green; xfail test gone; full suite green.
3. **Byte-identity gate:** run the repo's snapshot diff; only `unresolvable_attr_probe/extraction_snapshot.json`
   moves, and within it only the 5 classification strings (timestamp-only churn on `captured_at`
   reverted).
4. **B3 verification:** corpus grep / `fusion_tea` re-capture-and-diff; record verdict in the plan.
5. **Gates:** ruff ≤ 17, mypy ≤ 104; matrix recounted from rows.

## Next-Stage Handoff

- **Fixed:** the predicate (D3), the plumbing (D2), classification-only scope (D1), the table
  collapse + xfail deletion (D4), the R1 doc/matrix/epic set.
- **Open (Phase 0 resolves):** exact QN-format confirmation (B1) and the precise re-captured
  diff (whether `compilability` truly stays `manual_required` for all 5 — expected yes).
- **De-risk first:** run Phase 0 re-capture before touching tests/docs — the whole item is
  contingent on the 5 actually flipping. If they don't, stop and re-probe QN format.

---
Next Step: After approval → `/_my_plan` (Phase 0 re-capture is the first plan step and the gate).
