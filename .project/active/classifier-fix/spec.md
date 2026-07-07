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

**Why it matters now — and the severity is worse than the epic says.** `EXPOSE_COMPUTED`
decomposition is deferred, so an attribute that lands there is a **silent no-op**: the
graph builder's computed-attribute loop handles only `FORMULA` and
`EXPOSE_CHAIN_TENTATIVE` (which raises), and `EXPOSE_COMPUTED` falls through with no
`else`, no `raise`, and no warning (`resolution/graph_builder.py:269-288`); the
extractor returns it with no diagnostic (`computed_attribute_extractor.py:163`). The
integration test asserts exactly this — codegen doesn't error, no module is produced
(`test_expose_computed_no_module_no_error`,
`tests/integration/test_computed_attributes_e2e.py:135-142`). So a misclassified
inherited-attr FORMULA silently produces **no pipeline module and no diagnostic** —
which is what `docs/architecture/reference/16-computed-attributes.md:392-395` already
says ("silently produce no pipeline module … silent no-ops").

The epic and matrix get the severity mechanism **backwards**: they call it "loud
(EXPOSE_COMPUTED rejection, not silent wrong output)"
(`verification-matrix.md:136`). Only the "not a silent wrong value" half is true (no
wrong number is emitted); the "loud / a rejection" half is false. A silent drop is
*more* dangerous than a loud rejection — a model author gets no signal that a computed
attribute vanished. That raises the importance of this item. No fusion-tea model hits
the shape today, so nothing breaks in production, but the classifier is wrong on a
shape SysML v2 fully supports (inheritance), and the codebase carries that debt as five
`xfail`ed test cases, a "known contract" note in the matrix, and a "Confirmed bug"
section in the reference doc. This item retires that debt: fix the classifier,
re-capture the fixture snapshot, flip the xfails to real PASSes, and move the matrix
rows and doc/REQ text — correcting the loud→silent inversion — in the same change so no
reader inherits a ghost.

The evidence is already in place — the root cause is pinned, the fixture
(`tests/fixtures/unresolvable_attr_probe/`) exercises every shape, and the fix scope
is sketched in `docs/architecture/reference/16-computed-attributes.md:397-404`. This
is debt-retirement against filed evidence, not discovery (re-verified at HEAD
`e78c6a4`; Item 1 touched `graph_builder.py`/`input_resolver.py`, not this file).

## Success Criteria

- [ ] An inherited-attribute reference (QN in a supertype namespace of the owning
  part) is treated as a **sibling** reference, so an attribute that references only
  inherited/local attributes classifies `FORMULA`, not `EXPOSE_COMPUTED`.
- [ ] The `unresolvable_attr_probe` extraction snapshot is **re-captured** via
  `scripts/capture_extraction_snapshots.py` (scoped to that fixture) so the committed
  JSON records the corrected classifications (5 flip `expose_computed → formula`; D3
  stays `expose_computed`). The conformance suite reads this baked value, not a live
  classifier run, so without the re-capture a code fix changes nothing the suite
  observes. Landed as a reviewed committed-JSON diff (R3).
- [ ] The five previously-xfailed cases (L1, L2, D1, D2, D4 in `INHERITED_ATTR_PATTERNS`,
  `test_computed_attributes.py:642`) **PASS as real assertions** — each positively
  asserts the corrected classification (a literal `FORMULA` expectation). The
  parametrized set does not silently collapse to zero cases (see the [HARD] no-fake-test
  requirement below).
- [ ] **No over-correction**: the genuine `EXPOSE_COMPUTED` case D3 (`mixed_expose =
  my_calc.result * base_rate` — calc output **plus** inherited attr) still classifies
  `EXPOSE_COMPUTED` after the fix. A fires-on-shape + silent-on-clean pair proves the
  fix reclassifies inherited-attr FORMULA shapes without reclassifying a genuine
  EXPOSE_COMPUTED shape.
- [ ] Matrix and REQ/doc text move in the **same change** (R1): the "Known contract
  (Item 7)" block (`verification-matrix.md:136`) and the "Inherited Attribute
  Misclassification" Known-Issues section (`16-computed-attributes.md:365-408`) are
  rewritten from "confirmed bug / deferred" to the fixed state; the classification
  contract is positively pinned. The loud→silent inversion is corrected in the same pass
  — the matrix `:136` "loud (EXPOSE_COMPUTED rejection)" phrase (and the epic Item-4
  text that repeats it) is fixed **toward "silent no-op," citing the code**
  (`graph_builder.py:269-288` / the e2e test), since doc 16 is the one that was right.
  Matrix recount from rows holds.
- [ ] The integration e2e suite (`test_computed_attributes_e2e.py`) does not move:
  confirmed because its classification lists (`EXPOSE_COMPUTED_ATTRS`, `:44-48`) run on
  `attr_expr_probe`, which uses no PartDef inheritance (`:>`) — verified: zero `:>` in
  its `.sysml`. If a later check finds an inherited-attr computed attribute there, those
  lists move too and land in the same change.
- [ ] Suite green; ruff/mypy not worse than the epic gates (ruff ≤ 17, mypy ≤ 104).
  **All snapshots and baselines byte-identical except** the single intended, reviewed
  churn `tests/fixtures/unresolvable_attr_probe/extraction_snapshot.json`. The
  byte-identity gate is run and proves the carve-out (only that one file moves).

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
  excludes inherited attributes (`computed_attribute_extractor.py:188-191`). The
  supertype chain must be supplied from extraction. The reference doc sketches this as an
  `ancestor_part_qns: set[str]` parameter fed by supertype-chain extraction
  (`16-computed-attributes.md:401-404`). Exact plumbing is a design choice — but see the
  first design gate below: the whole fix is dead if the chain isn't reachable.

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
  shapes now classify `FORMULA`. The expected value is a literal (`FORMULA`), so the
  assertion is independently anchored by construction (R1 — never computed by the code
  under test). Filtering `INHERITED_ATTR_PATTERNS` on `correct_cls == FORMULA` selects
  exactly the five (L1/L2/D1/D2/D4) and excludes D3 — a stable selection that does not
  collapse when the `actual` column updates. The mechanism (rewrite the xfail body into
  a positive assertion; the exact stable filter) is deferred to design.

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

- **[HARD]** The fix is **not code-only** — it requires re-capturing the
  `unresolvable_attr_probe` extraction snapshot. Classification is computed in the
  extraction layer and **serialized** into the committed snapshot; the fixture reads
  `load_extraction_snapshot("unresolvable_attr_probe")` (`conftest.py:128`), and that
  JSON bakes `"classification": "expose_computed"` ×6. Re-capture via
  `scripts/capture_extraction_snapshots.py` (the fixture is in `EXTRACTION_ONLY_MODELS`,
  `:118`; scope with the `requested` argument so only this fixture regenerates). This is
  **live extraction → needs the syside license** (memory:
  `syside-license-via-scripts-not-dashc`) and falls under R3 capture discipline
  (reviewed committed-JSON diff, one regen at a time).

- **[HARD]** **Byte-identity — the real mechanism, not the reason first given.** The
  guarantee is not "no model hits the shape"; it is that every other baseline derives
  from an **un-recaptured** snapshot, so a code-only classifier change cannot move it —
  its classifications are frozen in its committed JSON. Byte-identity therefore holds
  **as long as re-capture is scoped to `unresolvable_attr_probe` only**. The one file
  that must change is `unresolvable_attr_probe/extraction_snapshot.json` (carved out
  above); "baselines byte-identical" as a blanket claim is wrong for that file. Corollary
  worth verifying (R4 — a filed "no model hits it" is a static-read verdict until
  reproduced): PartDef inheritance (`:>`) is used across the corpus including
  `fusion_tea`, a baseline model (`capture_extraction_snapshots.py:110`). If anyone ever
  re-captures a baseline snapshot, a corpus computed attribute that references an
  inherited attr *would* flip. Verify the "no corpus model hits this shape" claim — grep
  the corpus for computed attributes referencing inherited attributes, or
  re-capture-and-diff `fusion_tea` once — rather than assert it.

- **[INFERRED]** Doc 16's **Impact** wording ("silent no-ops in the pipeline",
  `16-computed-attributes.md:392-395`) is **correct**; the epic/matrix "loud
  (EXPOSE_COMPUTED rejection)" framing (`verification-matrix.md:136`) is **wrong**. The
  reconciliation runs toward "silent no-op," pinned to the code
  (`graph_builder.py:269-288` / the e2e test) — do not merely make the two agree; fix the
  matrix/epic text and keep doc 16's description. (R4 step 4: close the loop in the docs
  in the same change.)

- **[INFERRED]** The inline `⚠ KNOWN BUG` comment in doc 16's Step-2b pseudocode
  (`16-computed-attributes.md:133`) and the `114-116` note that inherited QNs resolve
  to the supertype namespace must be updated to describe the fixed behavior.

## Non-Goals

- **EXPOSE_COMPUTED decomposition** (a computed attribute mixing a calc output with
  arithmetic — the D3 shape and `adjusted_cost = cost_model.total_cost * 1.1` in doc 16)
  stays deferred. This item makes inherited-attr FORMULA shapes classify correctly; it
  does not build handling for genuine EXPOSE_COMPUTED attributes.
- Any behavior change for models that don't use PartDef inheritance. Every baseline
  except the deliberately re-captured `unresolvable_attr_probe/extraction_snapshot.json`
  stays byte-identical — guaranteed by scoping re-capture to that one fixture (see the
  byte-identity [HARD] requirement), not by assuming no model uses inheritance.
- The `UNRESOLVABLE` "likely dead code" question (`16-computed-attributes.md:410-419`) —
  separate documented disposition, out of scope here.

## Open Questions / Deferred to design

- **FIRST DESIGN GATE — can the classifier even see the ancestor chain?** The entire
  fix rests on reaching the owning part's ancestor PartDef QNs. The spec assumes SysIDE
  surfaces the generalization/supertype chain off the raw `part_element` the extractor
  holds; that is **not confirmed**. Everything downstream (the `ancestor_part_qns`
  parameter, the Step-2b predicate) is dead if it isn't reachable. Design must **probe
  this first** — a small live extraction against `unresolvable_attr_probe` confirming the
  supertypes/generalizations are queryable — before committing to a mechanism. Likely
  reusable substrate: the codebase already reaches inheritance data for the `:>>`
  retype/redefinition machinery behind REQ-LVP-09 / REQ-VBR-11
  (`hierarchy_resolver.py`); name it as the source if it exposes generalizations, or
  treat the reachability check as the first gate if it does not.
- **Where the ancestor QNs come from.** Given reachability, extract the supertype chain
  during part extraction and thread it to the classifier (doc 16 sketches
  `ancestor_part_qns: set[str]`), vs computing ancestors inside
  `extract_computed_attributes` from `part_element` at classification time. Design
  decides the cleanest plumbing and the exact Step-2b predicate (prefix-match against any
  ancestor QN).
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
