# Design: Predicate Defect Hardening (CONSTRAINT-SEMANTICS Item 4)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-13
**Codegen branch:** `item7-rebuild` @ `c93a5e3`
**Companion:** `/home/reid/1cfe/agentic-mbse-item7-rebuild` @ `bc69f04`
**Complexity:** MEDIUM

---

## Overview

Two fixes on the boundary a modeler crosses writing an asserted physics gate: make the
existing unit-annotation rule reach the lanes it does not reach yet (Defects A and the
fourth lane), and make the blocked-chain diagnostic name the offending reference, its
location, and the supported rewrite (Defect B).

## Related Artifacts

- **Spec (requirements authority):** `.project/active/constraint-predicate-hardening/spec.md`
- **Epic (scope authority):** `.project/backlog/epic_constraint_semantics_contract.md` — Item 4
- **Companion evidence:** `.project/active/constraint-predicate-hardening/probes/companion-evidence.md`
- **Product lens:** `.project/active/constraint-predicate-hardening/product-lens.md`
- **Required reading:** `.project/active/constraint-semantics-contract/spec.md`;
  `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §6;
  `.project/active/constraint-semantics-contract/rulings-20260812.md` Q4, Q8

## The Point

**[INHERITED: rulings-20260812.md Q8]** A modeler writing an asserted physics gate must be
stopped only by the product's real limits, and when stopped, must be told what to write
instead.

Today neither holds. A modeler who writes the *supported* form — an inequality carrying a
unit-annotated literal — is refused by a bug that has nothing to do with the limit
(`SI_OCCURRENCE_MISSING` against `SI::metre`). A modeler who writes an *unsupported* form —
a feature chain in a predicate body — is refused with `feature_chain: block_feature_chain`,
which names no reference, no location, and no rewrite.

This ladders directly into Item 5. That item migrates all 65 CATF constraints into the
bindings-only recipe, and the blocked-chain diagnostic is the instrument that migration is
performed with. A tautology makes 65 rewrites a manual hunt; a diagnostic that names the
chain and the rewrite makes them mechanical. The same reasoning covers the fourth lane: the
rewrite the new message advertises is a binding, and a tolerance band's binding is exactly
`in tol = 0.05 [m]`. Advertising a lane that still refuses would be worse than the tautology.

The published promise this discharges is `docs/architecture/modeling-assumptions.md:535` —
"If the profile BLOCKs an asserted constraint, the generation error names the exact construct
to fix."

## Research Findings

All codegen citations below were read directly at `c93a5e3`. Companion citations are from the
orchestrator's evidence file (`probes/companion-evidence.md`), gathered at `bc69f04`.

**The unit-annotation rule and its one owner.** `extraction/unit_annotation.py:1-28` states the
rule and holds both spellings: `annotated_ast_value` (syside AST) and `annotated_ir_value`
(parsed IR). The elaborator's refusal policy wraps the AST spelling in
`_without_unit_annotation` (`elaboration/elaborate.py:862-878`), which converts the module's
`ValueError` into `SI_EDGE_DANGLING`. Today it is called from exactly **one** site:
`_create_value_node` (`elaborate.py:757-759`). That is why the rule reaches attribute values
and calc-def defaults and nothing else.

**Defect A's actual seam.** An inline/requirement-constraint usage pushes its
`result_expression` into `_pending_expressions` (`elaborate.py:1112-1117`); resolution walks it
with `_expression_references` (`elaborate.py:2371-2412`), which recurses into *every* operand of
an `OperatorExpression` (`:2409-2411`). A unit annotation is an `OperatorExpression` with
operator `[` whose second operand is `SI::metre`. The walk reaches `_resolve_leaf`
(`elaborate.py:2162-2168`), `FeatureSlotIndex` has no slot for a library element, and it raises
`SI_OCCURRENCE_MISSING`. The walk is entered from two callers (`:2220`, `:2286`), so it is the
lane boundary for computed attribute expressions as well as predicates.

**The fourth lane's seam.** `_collect_bound_members` reads the binding expression
(`elaborate.py:1651`) and classifies it with `_binding_evidence` (`:1839-1846`): chain →
reference → `is_literal_node` → else `expression_evidence`. `in tol = 0.05 [m]` is an
`OperatorExpression`, so it is none of the first three and falls to
`extraction/binding_evidence.py:expression_evidence`, which stamps `EXPRESSION_SOURCE`;
`_unsupported_code` (`elaborate.py:1848-1858`) then maps that to
`SI_EXPRESSION_SOURCE_UNSUPPORTED` and `_record_readiness` refuses it. Note the literal read at
`:1657` uses the same un-unwrapped expression, so both the classification and the value need
the unwrap.

**Defect B's two halves.** The companion decides and phrases the block: `_diagnostic(...)`
defaults `message = f"{construct}: {reason}"` (`executable_profile.py:357-374`), and both chain
sites pass no message (`:535-537` in `_walk_value`, `:702-707` in the proposition walk). Both
sites hold `node.reference.chain_segments` (ordered path names) and a `LocationFact`
(file/line/column). `EligibilityDiagnostic.reason` is validated against a closed `REASON_CODES`
vocabulary in `__post_init__` (DD-R05).

Codegen renders the pair and joins the list with `"; "` (`elaborate.py:1097-1108`), producing
one `SI_CONSTRAINT_BLOCKED` `Diagnostic` per constraint node. `_diagnose` (`elaborate.py:2454`)
de-duplicates whole `Diagnostic` records but cannot see inside the joined string — which is why
`LayerContinuity` renders 13 identical copies in one detail.

**The precedent for a legible diagnostic.** `_record_readiness` (`elaborate.py:1860-1892`)
renders `unsupported exact source form {form} ({written_text!r})` and de-duplicates on
`(formal, code)`. `SourceReferenceEvidence.written_text` comes from
`binding_evidence.written_reference_text`, which reads the CST byte span. That is the shape
Defect B's message should read like.

**The test that constrains the rendering.** `tests/conformance/test_elaboration_payload_identity.py:236-266`
asserts a `pytest.raises` regex `SI_CONSTRAINT_BLOCKED.*blocked_guard.*block_real_equality_requires_tolerance`,
`len(blocked) == 1`, and `"block_real_equality_requires_tolerance" in blocked[0].detail`. All
three are reason-code substring matches over one diagnostic — read directly, not assumed. See
D6 for what this permits and forbids.

**No test anywhere asserts the tautology.** `grep -rn "block_feature_chain"` over `tests/`,
`src/`, and `docs/` returns only `docs/architecture/modeling-assumptions.md:482` (a prose list
of block reasons). The companion message change therefore cannot break a codegen assertion.

## Core Concept

Both defects are the same failure of *reach*, not of policy, and each is cured by extending an
existing owner rather than minting a new mechanism.

Defect A and the fourth lane are one defect in two more lanes: the product already owns the
rule "a unit annotation contributes its value and never a reference," and that rule is applied
at exactly one call site today. The cure is to call it at the two remaining places where an
authored expression is classified — the reference walk, and the binding classifier — using the
existing `_without_unit_annotation` wrapper. No new code path, no second special case, no
change to what the profile admits.

Defect B is a message that was never written. The companion already holds the offending chain
and its location where it decides the block; it just passes no `message` and takes a default
that repeats the reason. The cure is: the companion says *what* is wrong and *what to write
instead*, codegen says *where* and collapses repeats deterministically. The reason-code
vocabulary is untouched, the diagnostic count is untouched, and who gets stopped is untouched.

## Key Bets

- **B1.** A unit annotation's second operand is the *only* reason `_expression_references`
  reaches a standard-library element. *If false → unwrapping the annotation at the walk head
  cures the reproduction but leaves `SI_OCCURRENCE_MISSING` reachable from another library
  reference, and the characterization passes while the class stays open.*
- **B2.** The unit text reaches the profile and the predicate IR through the companion's own
  extraction of the AST (`UnitAnnotationNode`), not through codegen's reference walk. So
  suppressing the annotation as a *data reference* in `_expression_references` and
  `_collect_bound_members` cannot suppress it as a *unit*. *If false → the fix silently
  disables `block_incompatible_dimensions` / `block_unknown_exact_unit`, which is the spec's
  named failure ([HARD], spec:106-111). Probe P2 discriminates.*
- **B3.** The offending chain's authored spelling is reconstructible at the companion block
  site from `chain_segments` (optionally with `source_name`), without re-reading the CST.
  *If false → Defect B needs a companion-side CST read equivalent to codegen's
  `written_reference_text`, which is a materially larger companion change. Probe P4
  discriminates.*
- **B4.** An inline asserted inequality over an in-scope feature carrying a compatible
  unit-annotated literal is *admitted* by the profile once Defect A is cured — nothing else in
  that shape trips a block reason. *If false → the demonstration fixture cannot pin a working
  gate and the fixture (not the design) changes. Probe P1 discriminates and both branches are
  designed below.*

## Key Decisions

- **D1 — Defect A's cure lands at the head of `_expression_references`
  (`elaborate.py:2371`), applying `_without_unit_annotation` to the expression before any
  structural dispatch.** *Rejected: unwrapping at the predicate entry
  (`elaborate.py:1112-1117`).* The entry sees only the top-level node. In the demonstration
  shape `gap_width >= 0.25 [m]` the annotation is nested under `>=`, so an entry-level unwrap is
  a **no-op on the actual defect**. It would also be a second application site of a rule that
  has one owner. Head-of-walk placement is the rule's actual scope: every lane the walk covers,
  both callers (`:2220`, `:2286`), at once. **[AGENT]**
  - Ordering is safe: `annotated_ast_value` returns the expression unchanged unless it is an
    `OperatorExpression` whose operator is `[`. A `FeatureChainExpression` is an
    `OperatorExpression` subtype but its operator is not `[`, so the unwrap cannot preempt the
    chain-before-operator dispatch the walk depends on (`elaborate.py:2374-2377`).

- **D2 — the fourth lane is cured in this item**, by applying the same
  `_without_unit_annotation` to the binding expression read at `elaborate.py:1651`, before both
  `_binding_evidence` (`:1656`) and `extract_literal_value` (`:1657`). *Rejected: characterize
  and file.* The brief's rule is "cure iff the cure is the same unit-annotation rule reaching
  one more lane." It is exactly that — the same wrapper, the same one owner, one call site, no
  new classification branch. Unwrapped, `is_literal_node` is true and `_binding_evidence` yields
  `AUTHORED_LITERAL` evidence with value `0.05` through the path literal bindings already take
  (`elaborate.py:2415-2420`). The lane sits on Item 5's blessed tolerance-band recipe and on the
  rewrite Defect B advertises, so leaving it refused would make D3's message point at a refused
  form. **[AGENT]** (spec Open Question 1, priced both ways; orchestrator ruling **[AGENT]**
  authorised the call.)
  - Consequence to accept: `literal_evidence` sets `written_text = str(literal_value)`, so the
    evidence text reads `"0.05"`, not `"0.05 [m]"`. That is the rule, not a loss — the
    annotation contributed its value.

- **D3 — Defect B splits: the companion supplies the message, codegen supplies the location,
  the de-duplication, and the order.** *Rejected: codegen re-derives the written reference from
  the usage AST.* Codegen does not know *which* operand the profile objected to; it would have
  to re-implement the profile's chain detection to find out, which duplicates the decision in
  the repo that does not own it. The companion holds `node.reference.chain_segments` at the
  decision point (evidence file, `executable_profile.py:535-537`, `:702-707`) — the payload is
  already there and only the `message=` argument is missing. **[AGENT]**

- **D4 — multi-chain identification is one *entry per distinct reference* inside the single
  existing `SI_CONSTRAINT_BLOCKED` diagnostic.** *Rejected: one codegen `Diagnostic` per
  blocked chain.* That multiplies `SI_CONSTRAINT_BLOCKED` rows, which the Item 2 disposition
  contract, the coverage account (`generation/coverage.py`), and
  `test_elaboration_payload_identity.py:250` (`assert len(blocked) == 1`) all count on.
  Changing the diagnostic count is a disposition-contract change this item is barred from
  (spec Non-Goals). The message gets richer; the row count does not move. **[AGENT]**

- **D5 — the de-duplication key is the full rendered identity
  `(reason, construct, message, file, line, column)`; the order key is
  `(file, line, column, reason, message)` with a missing location normalized to `""`/`-1` and
  sorting first.** *Rejected: de-duplicating on `reason` alone.* That would collapse two
  *different* blocked chains at different lines into one entry and lose the identification
  criterion. *Rejected: preserving the companion's emission order.* It is a walk order, not a
  source order, and nothing in the companion contract pins it. Sorting on a source-derived key
  is what makes "same model, same message, every run and every order" true by construction.
  Precedent: `_record_readiness`'s `(formal, code)` collapse (`elaborate.py:1867-1870`).
  **[AGENT]**

- **D6 — codegen renders the location for *every* block reason, using the file's basename.**
  *Rejected: rendering the absolute path.* Absolute paths differ per checkout and would make any
  baseline machine-dependent (a known trap in this repo). *Rejected: chain-only location.*
  Location is generic and cheap in the renderer, and rendering it for all reasons moves every
  other block reason measurably closer to the `modeling-assumptions.md:535` promise without
  touching the closed reason vocabulary. **[AGENT]**

- **D7 — `test_elaboration_payload_identity.py:236-266` is NOT edited.** Verified by reading it:
  all three assertions are reason-code substring / regex matches over one diagnostic, its
  fixture blocks on `block_real_equality_requires_tolerance` (not a chain), and that reason keeps
  the companion's default message. D6 appends ` [file:line]` to its detail, which the `.*` regex
  and `in` checks tolerate. If implementation finds otherwise, changing it is a **stated**
  amendment to this design, never a silent test edit. **[AGENT]**

- **D8 — red-first characterizations land as `@pytest.mark.xfail(strict=True)` citing this
  item, and the fix commit removes the marker.** This reconciles the two standing constraints
  that otherwise collide: kept characterizations must land red *before* the fixes (epic
  de-risking), and both trees must be green at every commit (editable-install coupling). Red is
  demonstrated by running the test once with the marker removed and recording the failure in the
  commit message. **[AGENT]**

- **D9 — no new `REASON_CODES` entry.** The companion change is `message=` only, at two call
  sites. Minting a reason code would be a deliberate vocabulary extension (DD-R05) and buys
  nothing: the reason is unchanged, only its explanation was missing. **[AGENT]**

## Architecture

Three seams, two repos, one direction of flow.

```
companion  executable_profile._walk_value        :535  ─┐  message= naming the chain
           executable_profile (proposition walk) :702  ─┘  + the bindings rewrite
                                   │  EligibilityDiagnostic(reason, message, location)
                                   ▼
codegen    elaborate._build_constraint_nodes     :1097 ─── de-dup (D5) → sort (D5)
                                                          → render "reason: message [file:line]"
                                                          → ONE SI_CONSTRAINT_BLOCKED Diagnostic

codegen    elaborate._expression_references      :2371 ─── _without_unit_annotation at head (D1)
codegen    elaborate._collect_bound_members      :1651 ─── _without_unit_annotation on the
                                                          binding expression (D2)
```

The two unit-annotation seams are independent of the companion and of each other; the Defect B
seam is the only cross-repo coupling.

## Required Invariants

1. **One owner for the unit rule.** `extraction/unit_annotation.py` stays the only place that
   decides what a unit annotation means. Every application goes through
   `_without_unit_annotation` (`elaborate.py:862-878`). A structural `operator == "["` test
   written anywhere else is a design violation.
2. **Carried, never applied.** No fix converts, folds, or drops a unit's *semantic* effect. The
   profile's `block_incompatible_dimensions`, `block_unknown_exact_unit`, and
   `block_unit_conversion_required` decisions reach the same verdicts before and after
   (spec [HARD], and DD-R25).
3. **The admitted set is unchanged in both directions.** Nothing newly admitted, nothing newly
   blocked. Chains stay blocked; `==` stays untoleranced.
4. **One `SI_CONSTRAINT_BLOCKED` diagnostic per blocked constraint node**, before and after.
5. **Determinism by construction.** The rendered detail is a function of the de-duplicated set
   ordered by a source-derived key (D5) — never of the companion's walk order.
6. **The advertised rewrite is a supported form.** After D2, `in tol = 0.05 [m];` is supported,
   so the message may name the annotated binding. If P3 falsifies that, the message drops the
   annotation and reads `in tol = 0.05;`.

## Component Overview

| Component | Location | Responsibility after this item |
|---|---|---|
| Unit-annotation rule | `src/sysml_codegen/extraction/unit_annotation.py` | Unchanged. Still both spellings, still the only owner. |
| Elaborator refusal policy | `elaborate.py:862-878` (`_without_unit_annotation`) | Unchanged. Gains two more callers. |
| Reference walk | `elaborate.py:2371-2412` | Applies the rule at its head before dispatch (D1). |
| Binding collector | `elaborate.py:1619-1662` | Applies the rule to the binding expression before classification and literal read (D2). |
| Block renderer | `elaborate.py:1097-1108` | De-duplicates, orders, and renders location (D3–D6). New private helper `_render_block_reasons(decision)`. |
| Companion chain-block sites | `agentic-mbse: executable_profile.py:535-537`, `:702-707` | Pass an explicit `message` (D3, D9). |

The renderer helper is the only new named thing in either repo. Without it the de-dup, sort,
and location render would inline into `_build_constraint_nodes`, which already carries the node
minting loop; the helper exists so the ordering key is testable on its own.

## The Message Shape (rendered text)

Companion `message` for a blocked chain — the payload half:

```
feature chain 'bioshield.outer_radius' is not executable in a predicate body;
bind it to a constraint formal in the usage (in outer_radius = bioshield.outer_radius;)
and use the formal in the predicate
```

Codegen's rendered detail for a single-chain block:

```
constraint profile blocked execution: block_feature_chain: feature chain
'bioshield.outer_radius' is not executable in a predicate body; bind it to a constraint
formal in the usage (in outer_radius = bioshield.outer_radius;) and use the formal in the
predicate [radial_build.sysml:605]
```

For the `LayerContinuity` shape (13 occurrences, N distinct references), one detail listing
each distinct reference once, joined by `"; "`, ordered by `(file, line, column, reason,
message)`. The 13 identical copies collapse to the number of distinct references.

Unchanged reasons keep the companion default and gain only the location:

```
constraint profile blocked execution: block_real_equality_requires_tolerance:
real_equality: block_real_equality_requires_tolerance [model.sysml:19]
```

**Residue to record (success criterion 3).** Every block reason other than
`block_feature_chain` still renders the companion's `construct: reason` default. After this
item they name *where* (D6) but not *what construct* beyond the reason code. Per the spec, that
residue is named here rather than left implied: `block_real_equality_requires_tolerance`,
`block_xor`, `block_implies`, `block_incompatible_dimensions`, `block_unknown_exact_unit`,
`block_unit_conversion_required`, and the assert-by-reference reason
(`docs/architecture/modeling-assumptions.md:482`) are out of scope for the naming half of the
promise in this item. The close record must carry that list.

## Fixture Plan

Frozen twins (`catf_mfe_model`, `catf_mfe_d5`) untouched. All four are new fixtures under
`tests/fixtures/`, each carrying the repo's fixture-header comment convention (see
`tests/fixtures/unit_annotation_lanes/model.sysml`).

| Fixture | Shape | Pins |
|---|---|---|
| `predicate_unit_annotation` | Part def with an in-scope attribute and an **inline asserted** constraint: an inequality carrying a compatible unit-annotated literal. Plus a `Noop` calc def so the pipeline has a module (the `constraint_blocked_profile` idiom). | Defect A cured; the gate *works* (admitted, catalogued, assessed, counts toward coverage). |
| `predicate_unit_annotation_bare` | The same model with `[m]` removed. | The asymmetry pin, mirroring `unit_annotation_lanes_bare`. |
| `predicate_unit_annotation_incompatible` | The same predicate with a dimensionally incompatible annotation. | Invariant 2: the profile still blocks. Guards B2. |
| `constraint_binding_unit_annotation` | A constraint usage binding `in tol = 0.05 [m];`, predicate an inequality using `tol`. | The fourth lane cured: `AUTHORED_LITERAL`, value `0.05`, no readiness finding. |
| `constraint_blocked_chain_multi` | **Plain** (not asserted) constraint whose predicate is a 3-term `and` over two distinct chains, one repeated. | Defect B: distinctness (3 occurrences → 2 entries), order, location, and — via *plain* — that the Item 2 contract still generates and catalogs unassessed. |

Plain, not asserted, for the Defect B fixture: an asserted block halts, so reading the detail
would require the non-strict path. A plain constraint reads the same rendered detail off a
graph that generates, and exercises the unchanged half of the Item 2 contract at the same time.
One asserted-chain assertion is added to the existing strict-path test to pin that halting is
unchanged.

## Test Plan (mapped to the spec's success criteria)

| Spec criterion | Test | File |
|---|---|---|
| A elaborates without `SI_OCCURRENCE_MISSING` | annotated fixture builds; bare/annotated values agree | new `tests/conformance/test_predicate_unit_annotation.py` |
| No `SI::` element as a graph dependency | follow `test_unit_annotation_values.py:53-60` verbatim | same |
| End state is a **working gate** | catalog carrier exists, `disposition_kind == "eligible"`, assessed, counted in the coverage account | same |
| Unit semantics survive (invariant 2) | incompatible fixture still BLOCKs with the profile's dimension reason | same |
| Fourth lane | `in tol = 0.05 [m]` → `LiteralInput(0.05)`, no `SI_EXPRESSION_SOURCE_UNSUPPORTED` readiness finding | new `tests/conformance/test_constraint_binding_unit_annotation.py` |
| Chain block names reference + rewrite | rendered detail contains the joined chain text, the `in <formal> = <chain>;` rewrite, and `file:line` | new `tests/conformance/test_blocked_chain_diagnostic.py` |
| Multi-chain, distinct, deterministic | 3 occurrences → 2 entries; two elaborations of one model produce byte-identical detail | same |
| Item 2 contract unchanged | plain+blocked still generates and catalogs unassessed; asserted+blocked still halts | same + existing `test_elaboration_payload_identity.py` (unedited, D7) |
| No regressions | `test_unit_annotation_values.py`, `test_elaboration_payload_identity.py`, constraint catalog/coverage suites | existing |

All new tests are license-gated (`requires_license`, `tests/conftest.py`) because they load real
models. A run carrying license-skip lines is not a run (spec [HARD]).

**Interpreter and license (spec [HARD], non-negotiable):**
`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` then
`/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`. Never `uv run` — it resolves the
companion to the wrong checkout.

## Landing Order

The companion is an editable install, so a companion commit is live for codegen the instant it
lands. Sequenced so both trees are green at every commit:

1. **codegen** — characterizations for A, the fourth lane, and B, all `xfail(strict=True)` (D8).
   Green tree; red demonstrated by a marker-removed run recorded in the commit message.
2. **codegen** — D1 (walk-head unwrap). Remove A's markers. Independent of the companion.
3. **codegen** — D2 (binding unwrap). Remove the fourth lane's marker. Independent.
4. **companion** — D3/D9: explicit `message=` at `executable_profile.py:535-537` and `:702-707`.
   Message-only, no vocabulary change, cannot hard-error. Safe alone: no codegen test asserts
   the tautology (verified by grep across `tests/`, `src/`, `docs/`).
5. **codegen** — D4/D5/D6: `_render_block_reasons`. Remove B's markers. Must follow step 4,
   because B's green assertions read the companion's new message.
6. **codegen** — docs: the `modeling-assumptions.md:535` residue list, and any reference-doc
   text describing the old rendering.

Steps 2 and 3 may swap. Step 4 must precede step 5.

## Requested Probes

Design is complete for either branch of each; the orchestrator runs these and the results
select a branch (or confirm the primary). None blocks the plan's shape.

- **P1 — is the demonstration predicate admitted?** Elaborate `predicate_unit_annotation` (after
  D1) and print the constraint's disposition.
  *Discriminating:* `disposition_kind == "eligible"` and an assessed catalog row → primary
  branch, fixture stands. Any `block_unknown_exact_unit` / `block_unit_conversion_required` →
  the LHS attribute must itself carry a compatible declared unit; **fixture changes, design does
  not**. (Guards B4.)
- **P2 — do units still reach the profile after D1?** Elaborate
  `predicate_unit_annotation_incompatible`.
  *Discriminating:* still BLOCKs on a dimension reason → B2 holds, invariant 2 is testable as
  planned. Admits → B2 is false, D1 is the wrong seam, and the walk must skip only the
  annotation's *second* operand rather than replace the node — surface before proceeding.
- **P3 — does the fourth-lane cure keep the binding's unit visible to the profile?** Elaborate
  `constraint_binding_unit_annotation` after D2.
  *Discriminating:* value is `0.05`, no readiness finding, and the profile's verdict matches the
  same model written `in tol = 0.05;` plus a declared unit → primary. If the profile loses the
  unit, invariant 6 fires: the advertised rewrite drops the annotation.
- **P4 — what does `chain_segments` contain?** At companion `executable_profile.py:535`, print
  `node.reference.chain_segments` and `node.reference.source_name` for the CATF `LayerContinuity`
  predicate.
  *Discriminating:* segments include the root (`["bioshield", "outer_radius"]`) → message uses
  `".".join(chain_segments)`. Root omitted (`["outer_radius"]`) → prefix with `source_name`. If
  neither reproduces the authored spelling, B3 is false: the companion needs a CST read and the
  companion half grows — surface before implementing step 4.

## Non-Goals

Carried unchanged from the spec, restated only where design could be misread as touching them:
no chains admitted in predicate bodies; no `==` tolerance semantics; no profile expansion in
either direction; no new `REASON_CODES` entry (D9); no change to BLOCK-halts-generation or any
part of the Item 2 disposition/severity contract; no frozen-twin migration; no unit conversion
or constant folding (DD-R25); TEAx untouched.

## Potential Risks

- **B2 false (the largest).** A cure that silences the walk by stripping units would pass the
  characterization and quietly disable dimension checking. Mitigated by making the incompatible
  fixture a *kept* test, not a probe, and by P2 running before step 2 is trusted.
- **The demonstration fixture is over-built.** A fixture richer than the shape it pins has
  tripped an unrelated gap in this project before. Keep it to one part def, one attribute, one
  inline asserted inequality, and the `Noop` calc def.
- **Companion message drift.** Codegen tests asserting on the companion's exact wording couple
  the repos tightly. Mitigation: codegen assertions match on the *chain text*, the *`in ... =`
  rewrite fragment*, and the *location* — never on the full sentence.
- **`written_text`/CST recovery unavailable in the companion.** Covered by P4 and B3.

## Integration Strategy

Nothing in the pipeline's shape changes: elaboration still refuses what it refused, projection
still halts on `SI_CONSTRAINT_BLOCKED`, the catalog and coverage account keep their row counts.
This item makes two already-owned rules reach two more lanes and rewrites one string. Item 5
consumes the result: the diagnostic becomes the migration instrument, and the tolerance-band
binding it advertises is supported by D2.

## Next-Stage Handoff

**Fixed for the plan:** D1's seam (walk head, not predicate entry); D2 (the fourth lane is cured
here); D3's split (companion message, codegen location + de-dup + order); D4 (one diagnostic,
richer detail); D5's keys; D7 (that test is not edited); D8's xfail mechanism; the landing order.

**Open:** the four probes, each with both branches designed. P2 is the only one that can move a
seam.

**De-risk first:** P2, then P1. Run them against the characterization fixtures from step 1
before writing step 2's fix, so B2 is settled before any behavior changes.

---
**Next Step:** `/_my_design_review`, then `/_my_plan`.
