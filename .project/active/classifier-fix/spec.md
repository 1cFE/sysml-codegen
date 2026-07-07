# Spec: Inherited-Attr Classifier Fix (flip the 5 xfails)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06 23:55
**Complexity:** MEDIUM
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT, Item 4

---

## Problem

The computed-attribute classifier misclassifies **inherited** attributes. When a
PartDef inherits from a supertype (`part def 'Derived' :> 'Base'`) and a computed
attribute references an inherited attribute, that attribute is classified
`EXPOSE_COMPUTED` when `FORMULA` is correct.

**Why it happens.** The classifier's Step-2b decides "is this reference a sibling
attribute on my own part?" by a QN prefix check: `qn.startswith(owning_part_qn + "::")`
(`extraction/computed_attribute_extractor.py:112,123`). But SysIDE resolves an
inherited attribute's qualified name into the **supertype's** namespace, not the
subtype's. So `base_rate` on `'Derived Component'` resolves to
`…::'Base Component'::base_rate`, the prefix check fails, and the reference falls
through Step-2c as a `calc_ref` (a cross-namespace calc output). A calc_ref present
→ `EXPOSE_COMPUTED`. The root cause is pinned by
`test_computed_attributes.py::TestInheritedAttrClassification::test_inherited_refs_have_supertype_qn`
(`:794`).

**Why it matters now.** `EXPOSE_COMPUTED` decomposition is deferred, so an attribute
that lands there is unhandled — a **loud** wrong classification (a rejection, not a
silent wrong value). No fusion-tea model hits it today, so nothing in production
breaks, but the classifier is wrong on a shape SysML v2 fully supports (inheritance),
and the codebase carries that debt as five `xfail`ed test cases plus a "known
contract" note in the matrix and a "Confirmed bug" section in the reference doc. This
item retires that debt: fix the classifier, flip the xfails to real PASSes, and move
the matrix rows and doc/REQ text in the same change so no reader inherits a ghost.

The evidence is already in place — the root cause is pinned, the fixture
(`tests/fixtures/unresolvable_attr_probe/`) exercises every shape, and the fix scope
is sketched in `docs/architecture/reference/16-computed-attributes.md:397-404`. This
is debt-retirement against filed evidence, not discovery (re-verified at HEAD
`e78c6a4`; Item 1 touched `graph_builder.py`/`input_resolver.py`, not this file).

## Success Criteria

- [ ] An inherited-attribute reference (QN in a supertype namespace of the owning
  part) is treated as a **sibling** reference, so an attribute that references only
  inherited/local attributes classifies `FORMULA`, not `EXPOSE_COMPUTED`.
- [ ] The five previously-xfailed cases (L1, L2, D1, D2, D4 in `INHERITED_ATTR_PATTERNS`,
  `test_computed_attributes.py:642`) **PASS as real assertions** — each positively
  asserts the corrected classification. The parametrized set does not silently collapse
  to zero cases (see the [HARD] no-fake-test requirement below).
- [ ] **No over-correction**: the genuine `EXPOSE_COMPUTED` case D3 (`mixed_expose =
  my_calc.result * base_rate` — calc output **plus** inherited attr) still classifies
  `EXPOSE_COMPUTED` after the fix. A fires-on-shape + silent-on-clean pair proves the
  fix reclassifies inherited-attr FORMULA shapes without reclassifying a genuine
  EXPOSE_COMPUTED shape.
- [ ] Matrix and REQ/doc text move in the **same change** (R1): the "Known contract
  (Item 7)" block (`verification-matrix.md:136`) and the "Inherited Attribute
  Misclassification" Known-Issues section (`16-computed-attributes.md:365-408`) are
  rewritten from "confirmed bug / deferred" to the fixed state; the classification
  contract is positively pinned. Matrix recount from rows holds.
- [ ] Suite green; ruff/mypy not worse than the epic gates (ruff ≤ 17, mypy ≤ 104);
  baselines byte-identical (no fusion-tea/corpus model hits this shape, so generated
  output does not change).

## Known Requirements

- **[HARD]** The fix must distinguish an **inherited-attr sibling reference** (QN in a
  namespace of one of the owning part's ancestor PartDefs) from a **genuine
  cross-namespace calc reference** (a different, non-ancestor namespace). Only the
  former becomes a sibling ref; the latter stays a calc_ref. Over-broadening Step-2b to
  accept any non-owning namespace would reclassify real EXPOSE_COMPUTED attributes and
  break D3. (Enforced by the no-over-correction success criterion.)

- **[HARD]** The classifier needs the owning part's **ancestor PartDef QNs** to make
  this decision. `_classify_attribute_expression` currently receives only a single
  `owning_part_qualified_name` string (`computed_attribute_extractor.py:66`);
  `sibling_attr_names` is built from `owned_members`, which per SysML v2 semantics
  excludes inherited attributes (`16-computed-attributes.md:387-390`). The supertype
  chain must be supplied from extraction. The reference doc sketches this as an
  `ancestor_part_qns: set[str]` parameter fed by supertype-chain extraction
  (`16-computed-attributes.md:401-404`). Exact plumbing is a design choice.

- **[HARD]** **No fake test.** "Flip the xfails to PASS" must produce tests that
  positively assert the corrected classification, not tests that pass vacuously. Two
  hazards to avoid:
  - `test_misclassification_documented` (`:764`) currently only calls `pytest.xfail`
    when `classification != correct_cls`; if left as-is after the fix it passes without
    asserting anything.
  - Its parametrization filters `INHERITED_ATTR_PATTERNS` to `v[0] != v[1]` (the
    misclassified rows, `:757`). If the fix updates the table so `actual == correct`
    for those rows, the filter yields **zero** cases and the "5 cases PASS" become 5
    cases that no longer exist. A green empty parametrization reads as "covered" when
    it covers nothing.

  The end state must keep five real, positively-asserting cases proving the inherited
  shapes now classify `FORMULA`. The mechanism (rewrite the xfail body into a positive
  assertion; how to select the five cases stably after the table updates) is deferred
  to design.

- **[HARD]** `INHERITED_ATTR_PATTERNS` (`:642`) and its two consumer tests
  (`test_inherited_attr_classification` at `:726` asserting the `actual` column;
  `test_misclassification_documented` at `:764`) must be moved together with the code so
  the table records post-fix reality (the five `actual` values flip `EXPOSE_COMPUTED →
  FORMULA`; D3 stays `EXPOSE_COMPUTED`). The table's own docstrings say to update it
  when the classifier is fixed (`:732-733`).

- **[NEED]** The classification contract is **positively pinned** after the fix — a
  reader can point at a PASS test (and a matrix row) asserting "an inherited-attr
  reference classifies as a sibling → FORMULA," not merely at the absence of an xfail.
  Whether this is a new REQ-CA row or strengthened text on an existing one is a design
  choice; the outcome is that the contract is stated as what the code now does.

- **[INFERRED]** Doc 16's **Impact** wording ("silent no-ops in the pipeline",
  `16-computed-attributes.md:392-395`) conflicts with the epic/matrix framing of the
  same defect as **loud** (an EXPOSE_COMPUTED rejection, `verification-matrix.md:136`).
  Reconcile in the docs loop while rewriting the section — do not leave the two
  descriptions disagreeing. (R4 step 4: close the loop in the docs in the same change.)

- **[INFERRED]** The inline `⚠ KNOWN BUG` comment in doc 16's Step-2b pseudocode
  (`16-computed-attributes.md:133`) and the `114-116` note that inherited QNs resolve
  to the supertype namespace must be updated to describe the fixed behavior.

## Non-Goals

- **EXPOSE_COMPUTED decomposition** (a computed attribute mixing a calc output with
  arithmetic — the D3 shape and `adjusted_cost = cost_model.total_cost * 1.1` in doc 16)
  stays deferred. This item makes inherited-attr FORMULA shapes classify correctly; it
  does not build handling for genuine EXPOSE_COMPUTED attributes.
- Any behavior change for models that don't use PartDef inheritance. No corpus/fusion-tea
  model hits this shape, so generated baselines must not change.
- The `UNRESOLVABLE` "likely dead code" question (`16-computed-attributes.md:410-419`) —
  separate documented disposition, out of scope here.

## Open Questions / Deferred to design

- **Where the ancestor QNs come from.** Extract the supertype chain during part
  extraction and thread it to the classifier (doc 16 sketches `ancestor_part_qns:
  set[str]`), vs computing ancestors inside `extract_computed_attributes` from
  `part_element` at classification time. Design decides the cleanest plumbing and the
  exact Step-2b predicate (prefix-match against any ancestor QN).
- **How to keep the five cases real and stable** once `INHERITED_ATTR_PATTERNS`
  records post-fix reality: rewrite `test_misclassification_documented` into a positive
  assertion over a stably-selected five (e.g. a `was_misclassified` marker column, or a
  `correct_cls == FORMULA` filter), rather than the `actual != correct` filter that
  collapses to empty. Design picks the mechanism; the [HARD] no-fake-test requirement
  is the constraint.
- **Whether the over-correction guard needs a fresh fixture case.** D3 (`mixed_expose`)
  already provides a genuine EXPOSE_COMPUTED that must not flip. Design decides whether
  a purer negative — a non-inherited cross-namespace calc reference that must stay a
  calc_ref — adds value beyond D3, or whether D3 plus the existing EXPOSE_COMPUTED
  fixtures suffice.
- **The exact REQ-CA row** (new vs strengthened) that positively pins the fixed
  contract, and the precise rewrite of the matrix "Known contract" block.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 4; R1–R4; SC-D)
- **Required Reading:**
  - `.project/backlog/BACKLOG.md` → `[ITEM7-CLASSIFIER-FIX]` (`:280`)
  - `.project/active/matrix-truth/design.md` (the xfail re-frame — "Marker Hygiene,
    Counts, and the 5 Xfails"; D4)
  - `docs/architecture/reference/01-extraction.md`,
    `docs/architecture/reference/16-computed-attributes.md` (classifier contract +
    Known Issues)
  - The xfail site (`tests/conformance/test_computed_attributes.py:787`) and root-cause
    pin (`:794`); the Step-2b code (`src/sysml_codegen/extraction/computed_attribute_extractor.py:112-136`)
- **Fixture:** `tests/fixtures/unresolvable_attr_probe/{library,design}.sysml`
- **Design:** `.project/active/classifier-fix/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
