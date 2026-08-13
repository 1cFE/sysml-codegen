# Implementation Plan: Predicate Defect Hardening (CONSTRAINT-SEMANTICS Item 4)

**Status:** Draft
**Created:** 2026-08-13
**Last Updated:** 2026-08-13
**Size:** 0.5–1 day. Seven phases, each one sitting; each ends committed and green in **both** trees.

## Source Documents

- **Spec (requirements authority):** `.project/active/constraint-predicate-hardening/spec.md`
- **Design (mechanism authority):** `.project/active/constraint-predicate-hardening/design.md`
  ← component detail, seams, keys, message shape, invariants live there and are **not** repeated here
- **Review + resolutions:** `.project/active/constraint-predicate-hardening/design-review.md`
- **Companion evidence (orchestrator-verified at `bc69f04`, incl. P4 verdict and the verbatim
  `REASON_CODES` list):** `.project/active/constraint-predicate-hardening/probes/companion-evidence.md`
- **Epic (scope authority):** `.project/backlog/epic_constraint_semantics_contract.md` — Item 4

---

## The Point

A modeler writing an asserted physics gate must be stopped only by the product's real limits, and
when stopped, must be told what to write instead (**[INHERITED: rulings-20260812.md Q8]**).

Neither holds today.

- A modeler who writes the **supported** form — an inequality carrying a unit-annotated literal,
  `gap_width >= 0.25 [m]` — is refused by a bug that has nothing to do with the limit:
  `SI_OCCURRENCE_MISSING` against `SI::metre`. The product already owns the rule "a unit annotation
  contributes its value and never a reference," and that rule is applied at exactly one call site.
  This is a failure of *reach*, not of policy — the same category error already cured twice.
- A modeler who writes an **unsupported** form — a feature chain in a predicate body — is refused
  with `feature_chain: block_feature_chain`. That names no reference, no location, and no rewrite.
  `LayerContinuity` renders 13 identical copies of it in one string.

Why now: **Item 5 migrates all 65 CATF constraints into the bindings-only recipe, and this
diagnostic is the instrument that migration is performed with.** A tautology makes 65 rewrites a
manual hunt; a diagnostic naming the chain and the rewrite makes them mechanical. The same reasoning
carries the fourth lane (`in tol = 0.05 [m];`): the rewrite the new message advertises *is* a
binding, and a tolerance band's binding is exactly that shape. Advertising a lane that still refuses
would be worse than the tautology it replaces.

The published promise this discharges is `docs/architecture/modeling-assumptions.md:535` — "If the
profile BLOCKs an asserted constraint, the generation error names the exact construct to fix."

**What this item does not do:** admit chains in predicate bodies, give `==` tolerance semantics,
move the profile's admitted set in either direction, mint a `REASON_CODES` entry, touch the Item 2
disposition/severity contract, migrate the frozen twins, or touch TEAx.

---

## Implementation Strategy

### Phasing rationale

The landing order is **taken verbatim from `design.md#landing-order`** — it is not re-derived here.
Its constraint is the editable install: the companion (`/home/reid/1cfe/agentic-mbse-item7-rebuild`)
is imported live by the codegen licensed suite, so a companion commit is in force for codegen the
instant it lands. Both trees must therefore be green at every commit.

That collides with the epic's red-first posture, and D8 is the reconciliation: characterizations
land as `@pytest.mark.xfail(strict=True)`, so the tree is green while the tests are genuinely red,
and `strict=True`'s XPASS failure forces the marker off in the fix commit. Red is proven by running
each characterization once with the marker removed and **capturing that output into the item folder**
(`probes/red-evidence.md`) — a commit-message sentence is unfalsifiable after the fact (review A3).

Phase ordering beyond that: the two unit-annotation seams (D1, D2) are independent of the companion
and of each other, so they land first and de-risk the two live probes early. The Defect B renderer
must follow the companion message, because its green assertions read that message.

### Critical path

```
P1 fixtures + xfail characterizations (red captured)
   → D1 walk-head unwrap  [probe P1 fires here; P2 insurance]
   → D2 binding unwrap    [probe P3 gates this]
   → companion message=   (git -C companion)
   → codegen _render_block_reasons
   → docs + REASON_CODES reconciliation
   → verification.md
```

Phases 2 and 3 may swap (design's Landing Order note). Phase 4 must precede Phase 5.

### First proof point

**End of Phase 2:** the `predicate_unit_annotation` fixture elaborates with no
`SI_OCCURRENCE_MISSING`, and probe P1 says whether the profile admits it. That single run collapses
the largest remaining unknown on the Defect A side and tells us whether the demonstration fixture
stands as authored.

### Probes — where they fire and what they select

Design authority: `design.md#requested-probes`. None of them can move a seam.

| Probe | Fires | Discriminating outcome → branch |
|---|---|---|
| **P1** | Phase 2, immediately after D1 lands | `disposition_kind == "eligible"` + assessed catalog row → primary, fixture stands. Any `block_unknown_exact_unit` / `block_unit_conversion_required` → the LHS attribute must itself carry a compatible declared unit; **amend the Phase-1 fixture, not the design.** |
| **P3** | Phase 3, after the D2 unwrap and **before** the marker comes off | value is `0.05`, no readiness finding, and the profile's verdict matches the same model written `in tol = 0.05;` + a declared unit → primary. If the profile loses the unit, **invariant 6 fires**: the advertised rewrite in Phase 4's message drops the annotation and reads `in tol = 0.05;`. |
| **P2** | Phase 2, once, as cheap insurance | Expected: still BLOCKs on a dimension reason. **Gates nothing** (review A1) — the profile verdict is computed at `elaborate.py:403` independent of the walk, so it would pass either way. If it *fails*, something outside this design's model changed: **surface, do not patch.** |
| **P4** | Answered statically (companion evidence) | `chain_segments` includes the root; `".".join(chain_segments)` reproduces the authored spelling. Phase 4 **re-verifies the citation before editing**, per the evidence file's working constraint. |

---

## Environment (restated where you will trip on it)

These are spec `[HARD]` items. Getting any of them wrong makes a run unreportable.

- **Interpreter:** `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`. **Never `uv run`** — uv
  resolves the companion to the wrong checkout.
- **License:** `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` before any run. Every new
  test here is `requires_license` (they load real models). **A run carrying license-skip lines is
  not a full run and may not be reported as one.**
- **Companion:** `/home/reid/1cfe/agentic-mbse-item7-rebuild` @ `bc69f04`, editable install. Commit
  there with `git -C /home/reid/1cfe/agentic-mbse-item7-rebuild ...` — **never mix the two repos in
  one commit.**
- **Companion suite:** default selection only. **NEVER `-m ""`** — that is the corpus trap.
- **TEAx:** untouched by this item; its checkout stays on `constraint-semantics-item3`.
- **Frozen twins:** `catf_mfe_model` and `catf_mfe_d5` keep their constraint syntax unchanged
  (`catf_mfe_d5` is byte-reversal-pinned, `test_d5_variants.py:29`). **New fixtures only.**
- **Lint baselines:** `ruff check src` = 12, `mypy src` = 55. Gate is zero-new.

### Commit discipline

- One commit per phase minimum. Subject leads with the decision, e.g.
  `fix(Item 4): unit annotation unwraps at the reference-walk head (D1)`.
- Codegen commits in the codegen tree; companion commits via `git -C` in the companion worktree.
- Every commit leaves **both** trees green.

---

## Phase 1: Fixtures + red-first characterizations (xfail strict)

**Landing order step 1.**

### Goal

Land all five fixtures and all three characterization test files, every failing test marked
`@pytest.mark.xfail(strict=True, reason="CONSTRAINT-SEMANTICS Item 4 — <defect>")`, with the
marker-removed red output captured into the item folder. Tree green, defects pinned.

### Assumption under test

That each defect reproduces on a *new, minimal* fixture — not only on the research shape. If a
characterization passes with the marker removed, the fixture does not reproduce the defect and the
fixture is wrong (surface it; do not weaken the test).

### Fixtures (all new, under `tests/fixtures/`, each with the repo's fixture-header comment block —
see `tests/fixtures/unit_annotation_lanes/model.sysml:5-21` for the convention)

- [ ] `predicate_unit_annotation/model.sysml` — one part def, one attribute, one **inline asserted**
      inequality carrying a compatible unit-annotated literal, plus a `Noop` calc def so the pipeline
      has a module (idiom: `tests/fixtures/constraint_blocked_profile/model.sysml:6-9`).
      **Keep it to exactly that** — an over-built fixture has tripped an unrelated gap in this
      project before (`design.md#potential-risks`).
- [ ] `predicate_unit_annotation_bare/model.sysml` — the same model with `[m]` removed (the asymmetry
      twin, mirroring `unit_annotation_lanes_bare`).
- [ ] `predicate_unit_annotation_incompatible/model.sysml` — the same predicate with a dimensionally
      incompatible annotation.
- [ ] `constraint_binding_unit_annotation/model.sysml` — a constraint usage with **both**
      `in tol = 0.05 [m];` and `in ref = other_feature [m];`, predicate an inequality using both,
      plus `in bad = a + b;` on a second usage to pin that genuine expression sources stay refused.
- [ ] `constraint_blocked_chain_multi/model.sysml` — a **plain** (not asserted) constraint whose
      predicate is a 3-term `and` over two distinct chains, one repeated. Plain, not asserted,
      because an asserted block halts before the detail can be read.

### Test stencil (write these first)

```python
# tests/conformance/test_predicate_unit_annotation.py
pytestmark = requires_license
ANNOTATED = FIXTURES_DIR / "predicate_unit_annotation"
BARE = FIXTURES_DIR / "predicate_unit_annotation_bare"

@pytest.mark.xfail(strict=True, reason="CONSTRAINT-SEMANTICS Item 4 — Defect A (D1)")
def test_an_asserted_predicate_carrying_a_unit_annotation_elaborates() -> None:
    graph = build_elaborated_pipeline([ANNOTATED])          # today: SI_OCCURRENCE_MISSING
    assert graph.constraint_catalog.usage_records           # a carrier exists

@pytest.mark.xfail(strict=True, reason="CONSTRAINT-SEMANTICS Item 4 — Defect A, working gate")
def test_the_cured_predicate_is_a_working_gate() -> None:
    catalog = build_elaborated_pipeline([ANNOTATED]).constraint_catalog
    row = one_row_for(catalog, "gap_guard")
    assert row.disposition_kind == "eligible"               # assessed, not blocked, not non-reaching
```

- [ ] `tests/conformance/test_predicate_unit_annotation.py` — Defect A rows from
      `design.md#test-plan`: elaborates without `SI_OCCURRENCE_MISSING`; **working gate** (catalog
      carrier, `disposition_kind == "eligible"`, assessed, counted by
      `generation/coverage.py:coverage_account`'s `assessed_gate_count`); no `SI::` element as a
      graph dependency (follow `test_unit_annotation_values.py:54-60` verbatim); annotated/bare twins
      produce **identical module inputs** (invariant 7 — no dependency edge lost); incompatible
      fixture still BLOCKs on a dimension reason (invariant 2, regression guard on the companion
      path — **not** a D1 discriminator, review A1); a malformed annotation in a predicate
      hard-refuses with `SI_EDGE_DANGLING` (M7's stated route).
- [ ] `tests/conformance/test_constraint_binding_unit_annotation.py` — the fourth lane, **both**
      admitted shapes (M6c): `in tol = 0.05 [m]` → `LiteralInput(0.05)`; `in ref = other_feature [m]`
      → a reference binding; neither yields `SI_EXPRESSION_SOURCE_UNSUPPORTED`; `in bad = a + b`
      still does.
- [ ] `tests/conformance/test_blocked_chain_diagnostic.py` — the rendered detail contains the joined
      chain text, the `in <formal> = <chain>;` rewrite fragment, and `basename:line`; 3 occurrences →
      **2** entries; two elaborations of one model produce byte-identical detail;
      `assert "\n" not in blocked[0].detail` (invariant 8). **Assert on the chain text, the rewrite
      fragment, and the location — never on the companion's full sentence** (drift mitigation).
- [ ] `tests/unit/test_render_block_reasons.py` — over hand-built diagnostics, no license needed:
      `location=None` renders no ` [...]` suffix (M4); `None` `line`/`column` raise no `TypeError`;
      two entries differing only in `construct` produce stable output under input permutation (M1).
- [ ] Add one asserted-chain assertion to the existing strict-path test pinning that **halting is
      unchanged** (`design.md#fixture-plan`).
- [ ] **Do NOT edit** `tests/conformance/test_elaboration_payload_identity.py:236-266` (D7). If
      implementation finds it must change, that is a **stated amendment to the design**, recorded in
      this plan's Implementation Notes — never a silent test edit.

### Capture the red (D8 + review A3)

- [ ] Run each characterization file once with the `xfail` markers stripped (a scratch copy or
      `-p no:cacheprovider` + a temporary edit reverted before commit), licensed env sourced.
- [ ] Paste the failure output verbatim into
      `.project/active/constraint-predicate-hardening/probes/red-evidence.md`, one section per
      defect, with the command and the codegen/companion SHAs at the top.
- [ ] Confirm the markers are restored before committing.

### How to verify

```
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
  tests/conformance/test_predicate_unit_annotation.py \
  tests/conformance/test_constraint_binding_unit_annotation.py \
  tests/conformance/test_blocked_chain_diagnostic.py \
  tests/unit/test_render_block_reasons.py -q
```
Expect: all-xfailed (or passed, for the rows that already hold), **zero failures, zero xpassed,
zero license-skip lines**. Then the full licensed codegen suite, green. Commit.

**What we know works after this phase:** every defect reproduces on a minimal new fixture, the red
is on the record as output rather than as a claim, and both trees are green.

---

## Phase 2: D1 — unit annotation unwraps at the reference-walk head

**Landing order step 2. Independent of the companion.**

### Goal

Apply `_without_unit_annotation` at the head of `_expression_references`
(`elaborate.py:2371`) before any structural dispatch, so it fires at **every recursion level**.
Remove Defect A's `xfail` markers. See `design.md#key-decisions` D1 for the seam, the ordering
argument, the lane inventory, and the widening bound — do not re-derive them.

### Assumption under test

**B1** — a unit annotation's second operand is the only reason the walk reaches a standard-library
element. If the characterization goes green but `SI_OCCURRENCE_MISSING` is still reachable from
another library reference, the class stays open: record it, do not widen the fix.

### Changes

- [ ] `src/sysml_codegen/elaboration/elaborate.py:2371` — unwrap at the head. **No structural
      `operator == "["` test anywhere** (invariant 1) — the rule has one owner
      (`extraction/unit_annotation.py`) and one wrapper (`elaborate.py:862-878`).
- [ ] Remove `xfail` from the Defect A rows in `tests/conformance/test_predicate_unit_annotation.py`.
- [ ] **Probe P1** — elaborate `predicate_unit_annotation` and print the constraint's disposition.
      Record the outcome in Implementation Notes. If a unit reason appears, amend the **fixture**
      (give the LHS attribute a compatible declared unit); the design does not change.
- [ ] **Probe P2** — elaborate `predicate_unit_annotation_incompatible` once. Expected: still BLOCKs.
      Does not gate this phase. If it fails, **surface**, do not patch.

### How to verify

Focused: `pytest tests/conformance/test_predicate_unit_annotation.py tests/conformance/test_unit_annotation_values.py -q` — green, zero xpassed.
Then the **full licensed codegen suite**, because M7's malformed-annotation route now hard-refuses
in lanes that previously produced a readiness finding, and that can surface in an unrelated fixture
(`design.md#potential-risks`). Commit.

**What we know works after this phase:** Defect A is cured in the predicate lane, the two
already-cured lanes have not regressed, no dependency edge was lost, and P1 has selected the
demonstration fixture.

---

## Phase 3: D2 — the fourth lane (unit-annotated bindings)

**Landing order step 3. Independent of the companion. May swap with Phase 2.**

### Goal

Apply `_without_unit_annotation` **once** to the binding expression read at `elaborate.py:1652`,
covering both `_binding_evidence` (`:1656`) and `extract_literal_value` (`:1657`). Remove the
fourth-lane marker. Seam and admitted-set bounds: `design.md#key-decisions` D2 and invariant 3.

### Assumption under test

**B2 on its live side** — that the binding's unit still reaches the profile after codegen's unwrap
decides what the binding contributes. This is the item's largest risk: on `in tol = 0.05 [m];` the
annotation carries value *and* unit on one node.

### Changes

- [ ] `elaborate.py:1652` — one unwrap on the binding expression. One call site, no new
      classification branch.
- [ ] **Probe P3 — run before removing the marker.** Elaborate `constraint_binding_unit_annotation`;
      check the value is `0.05`, that there is no readiness finding, and that the profile's verdict
      matches the same model written `in tol = 0.05;` with a declared unit. Record the outcome.
      **If the profile loses the unit, invariant 6 fires** — Phase 4's advertised rewrite drops the
      annotation and reads `in tol = 0.05;`. Note that decision in Implementation Notes so Phase 4
      picks it up.
- [ ] Remove `xfail` from `tests/conformance/test_constraint_binding_unit_annotation.py`.
- [ ] Confirm the evidence-text consequence is what the tests assert: `written_text` reads `"0.05"`
      (not `"0.05 [m]"`) and `"other_feature"` (not `"other_feature [m]"`). That is the rule, not a
      loss (`design.md` D2 consequence note).

### How to verify

Focused: `pytest tests/conformance/test_constraint_binding_unit_annotation.py -q` plus the
constraint catalog/coverage suites. Then the full licensed codegen suite. Commit.

**What we know works after this phase:** `in x = <literal|reference|chain> [unit]` is admitted,
genuine expression sources (`a + b`) are still refused, and the rewrite Defect B is about to
advertise points at a **supported** form.

---

## Phase 4: Companion — the chain-block message (D3/D9)

**Landing order step 4. Companion tree only.** Must precede Phase 5.

### Goal

Pass an explicit `message=` at both chain-block sites so the companion says *what* is wrong and
*what to write instead*. **No `REASON_CODES` change** (D9) — the reason did not change, only its
explanation was missing.

### Assumption under test

**B3 / P4** — the offending chain's authored spelling is reconstructible from `chain_segments`
without a companion CST read.

### Changes

- [ ] **Re-verify the companion citations before editing** (the evidence file's standing
      constraint): `executable_profile.py:357-374` (`_diagnostic` default),
      `:535-537` (`_walk_value`), `:702-707` (proposition walk),
      `expression.py:611-637` (`extract_feature_chain_segments` appends the root first).
- [ ] `executable_profile.py:535-537` — pass `message=` naming `".".join(chain_segments)` and the
      bindings rewrite. Exact shape: `design.md#the-message-shape`. **One line, no newline**
      (invariant 8).
- [ ] `executable_profile.py:702-707` — the same message. **Both sites, or the fix covers one lane
      of two.**
- [ ] If P3 falsified the unit's survival, the rewrite in the message drops the annotation
      (invariant 6).

### How to verify

Full companion suite, **default selection — never `-m ""`**:
`/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` from the companion worktree, green.
Then the full licensed **codegen** suite — the editable install makes this message live for codegen
immediately. It is safe alone: no codegen test asserts the tautology (verified by grep across
`tests/`, `src/`, `docs/`; the only hit is prose at `modeling-assumptions.md:482`).

Commit **in the companion worktree**:
`git -C /home/reid/1cfe/agentic-mbse-item7-rebuild commit ...`. Never mixed with codegen.

**What we know works after this phase:** the block payload names the chain and the rewrite, the
reason vocabulary is untouched, and neither suite moved.

---

## Phase 5: Codegen — `_render_block_reasons` (D4/D5/D6)

**Landing order step 5. Must follow Phase 4** — its green assertions read the companion's new
message.

### Goal

De-duplicate, order, and render location for every block reason, inside the **one** existing
`SI_CONSTRAINT_BLOCKED` diagnostic. Remove Defect B's markers.

### Assumption under test

That one key can serve both de-duplication and ordering without ever tying or raising — the failure
mode here is a flaky landing, not a documentation gap.

### Changes

- [ ] New private helper `_render_block_reasons(decision)` in `elaborate.py`, called from
      `_build_constraint_nodes` (`:1097-1108`). It exists so the ordering key is testable alone.
- [ ] **One key**, used for de-dup *and* order:
      `(basename(file), line, column, reason, construct, message)`, each field normalized
      independently at construction — `basename(file) if file else ""`, `line if line is not None
      else -1`, `column if column is not None else -1` (D5, must-fix M1 + advisory A4). Because the
      order key **is** the de-dup identity, no two survivors tie, so the sort never falls back to the
      companion's walk order.
- [ ] Render ` [basename:line]` for **every** block reason; omit the suffix entirely when the
      location is absent — `LocationFact` is `None`, `file` empty, or `line` `None` (D6, M4).
      `column` is ordering-only, never rendered. **Never the absolute path.**
- [ ] Join multiple entries with `"; "`. **One line, no newline** (invariant 8) — two consumers
      depend on it: `test_elaboration_payload_identity.py:243` (regex `.` does not cross a newline)
      and `project.py:97` → `:265`.
- [ ] One `SI_CONSTRAINT_BLOCKED` diagnostic per blocked constraint node, before and after
      (invariant 4; held by `test_elaboration_payload_identity.py:253` and
      `tests/unit/test_constraint_usage_record_mint.py:94`).
- [ ] Remove `xfail` from `tests/conformance/test_blocked_chain_diagnostic.py` and
      `tests/unit/test_render_block_reasons.py`.

### How to verify

Focused: `pytest tests/conformance/test_blocked_chain_diagnostic.py tests/unit/test_render_block_reasons.py tests/conformance/test_elaboration_payload_identity.py tests/unit/test_constraint_usage_record_mint.py -q` — green, **and
`test_elaboration_payload_identity.py` unedited** (D7). Then the full licensed codegen suite. Commit.

**What we know works after this phase:** a blocked chain names the reference, the rewrite, and the
location; 13 copies collapse to the distinct count; the detail is byte-identical across runs and
contains no newline; the diagnostic row count did not move.

---

## Phase 6: Docs + the `REASON_CODES` reconciliation

**Landing order step 6.**

### Goal

Make the published promise text true, and discharge the design's **totality caveat**.

### Changes

- [ ] `docs/architecture/modeling-assumptions.md` — around `:480-486` and `:535`, update the block
      list / promise text to match what the diagnostic now says.
- [ ] Grep the companion's `REASON_CODES` (`executable_profile.py:66-100`) for its `block_*` members
      and reconcile against the design's nine-row published residue table. The verbatim list is
      already recorded in `probes/companion-evidence.md` — **23 `block_*` members**, of which the
      published list names nine. **The close record carries the final list, not the design's table.**
- [ ] Write the reconciliation into the close record: which of the 23 still cannot "name the exact
      construct to fix" after this item, and for each, why that is acceptable or what it is filed as.
      `block_feature_chain` is the one cured here.
- [ ] Update any reference-doc text describing the old rendering.

### How to verify

`pytest -q` docs-touching suites if any; `git diff --check`. Commit.

**What we know works after this phase:** success criterion 3 is discharged with a complete residue
list rather than an implied one.

---

## Phase 7: Verification

### Goal

Produce `.project/active/constraint-predicate-hardening/verification.md` with **exact counts**, not
adjectives.

### Steps

- [ ] Focused suites: the four new/edited test files, green.
- [ ] **Full licensed codegen suite:**
      ```
      set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
      /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest 2>&1 | tee /tmp/item4-codegen.log
      grep -ci "license" /tmp/item4-codegen.log   # any license-skip line ⇒ NOT a full run
      ```
      Record passed / failed / skipped / xfailed / xpassed exactly. **Zero license-skip lines or the
      run is not full and may not be reported as one.**
- [ ] **Full companion suite**, default selection, from the companion worktree. **Never `-m ""`.**
      Record the same counts.
- [ ] `ruff check src` → **12** (zero-new).
- [ ] `mypy src` → **55** (zero-new).
- [ ] `git diff --check` in **both** repos → clean.
- [ ] Confirm the frozen twins are untouched: `git status` shows no change under
      `tests/fixtures/catf_mfe_model/` or `tests/fixtures/catf_mfe_d5/`.
- [ ] Confirm TEAx is untouched and still on `constraint-semantics-item3`.
- [ ] Write `verification.md`: commands, exact counts, both repo SHAs, the P1/P2/P3 outcomes, and a
      pointer to `probes/red-evidence.md`.
- [ ] Carry the M3 `REASON_CODES` reconciliation into the close record.

**What we know works after this phase:** both suites are green on the recorded interpreter with the
license live, the lint gates held at baseline, and the item's claims are checkable against captured
output.

---

## Risk Management

**See `design.md#potential-risks` for the full analysis.** Phase-specific mitigations:

- **Phase 1 — the demonstration fixture is over-built.** A richer fixture than the shape it pins has
  tripped an unrelated gap in this project before. One part def, one attribute, one inline asserted
  inequality, one `Noop`.
- **Phase 2 — M7's malformed-annotation route** turns a bad model into a hard refusal in lanes that
  previously produced a readiness finding. Mitigation: run the **full** licensed suite at this phase,
  not only the new tests.
- **Phase 3 — unit loss on the binding lane (the largest risk).** Guarded by P3, with invariant 6 as
  the designed fallback. Run P3 *before* removing the marker.
- **Phase 4 — companion message drift.** Codegen assertions match the chain text, the `in ... =`
  rewrite fragment, and the location — never the full sentence.
- **Phase 5 — the order key raises or ties at sort time**, or a newline reaches the detail. Closed by
  D5's per-field normalization and full-identity key, and by the `"\n" not in detail` assertion;
  pinned by `tests/unit/test_render_block_reasons.py`.

**Surfacing rule (capture-fidelity §4):** if a probe or a suite produces evidence against a premise
this plan rests on — P2 failing, `test_elaboration_payload_identity.py` needing an edit, a
characterization that will not go red — **surface it in Implementation Notes and park the dependent
work.** Do not resolve it silently in either direction.

---

## Implementation Notes

_[TO BE FILLED DURING IMPLEMENTATION]_

### Phase 1 Completion
**Completed:**
**Actual changes:**
**Red evidence:** `probes/red-evidence.md`
**Issues / deviations:**

### Phase 2 Completion
**Completed:**
**P1 outcome (branch selected):**
**P2 outcome (insurance):**
**Issues / deviations:**

### Phase 3 Completion
**Completed:**
**P3 outcome (invariant 6 fired? yes/no):**
**Issues / deviations:**

### Phase 4 Completion
**Completed:**
**Companion citations re-verified:**
**Issues / deviations:**

### Phase 5 Completion
**Completed:**
**`test_elaboration_payload_identity.py` edited? (must be NO — any yes is a stated design amendment):**
**Issues / deviations:**

### Phase 6 Completion
**Completed:**
**REASON_CODES reconciliation (23 `block_*` members):**
**Issues / deviations:**

### Phase 7 Completion
**Completed:**
**Counts:** codegen suite · companion suite · ruff · mypy
**Issues / deviations:**

---

**Status:** Draft → In Progress → Complete
**Next step:** `/_my_implement`
