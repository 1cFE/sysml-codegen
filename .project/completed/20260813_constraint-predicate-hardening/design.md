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
(`elaborate.py:1652`) and classifies it with `_binding_evidence` (`:1839-1846`): chain →
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
  suppressing the annotation as a *data reference* cannot suppress it as a *unit*. *If false →
  the fix silently disables `block_incompatible_dimensions` / `block_unknown_exact_unit`, the
  spec's named failure ([HARD], spec:106-111).*
  - **Scoped by review (A1).** For **D1** this bet is structurally safe, not merely likely: the
    profile verdict is computed at `elaborate.py:403` (`evaluate_identified_profile(identified)`)
    from the companion's own extraction, *before and independent of* the reference walk that runs
    later in resolution. D1 cannot reach the profile's dimension checking by construction. The
    incompatible-unit fixture is therefore a **regression guard on the companion path**, not a
    discriminator for D1.
  - The live exposure is **D2**, where the annotation is the carrier of both the value and the
    unit on the same binding node, and codegen's unwrap decides what the binding contributes.
    Guarded by probe P3.
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
  has one owner. The walk is recursive (`:2411`), so "at the head" means the unwrap fires at
  every node — which is what makes the nested case work. **[AGENT]**
  - Ordering is safe: `annotated_ast_value` returns the expression unchanged unless it is an
    `OperatorExpression` whose operator is `[`. A `FeatureChainExpression` is an
    `OperatorExpression` subtype but its operator is not `[`, so the unwrap cannot preempt the
    chain-before-operator dispatch the walk depends on (`elaborate.py:2374-2377`).
  - **Lane inventory (corrected, M6a).** `_expression_references` has exactly two external
    callers: `:2220` is `_resolve_aliases` (the **typed-alias** lane) and `:2286` is
    `_resolve_computed_expressions`, where computed attribute expressions and constraint
    predicates enter **together**. An earlier draft called `:2220` the computed-attribute lane;
    that was wrong.
  - **Widening bound (M6b).** The alias and computed lanes are *already* unwrapped at their top
    level: both `_pending_aliases.append` (`:805`) and `_pending_expressions.append` (`:841`)
    sit inside `_create_value_node`, which unwrapped at `:757`. So D1 newly changes those two
    lanes only for a **nested** annotation (`= a * 2.0 [m]`), and changes the predicate lane
    wholesale (nothing unwraps there today). Every one of those shapes fails today —
    `SI_OCCURRENCE_MISSING`, or "does not contain one exact reference" in the alias lane — so
    **the widening admits models that are currently refused and changes no currently-green
    behaviour.** The one exception, stated so the plan can test for it: if a `[`-annotation's
    second operand ever resolved to a *user-model* feature rather than a library element, D1
    would drop a real dependency edge. No supported authoring shape produces that (the second
    operand of `[` is a unit), and invariant 7 pins it.
  - **New hard-refusal route (M7), decided deliberately.** Inside the walk,
    `_without_unit_annotation` converts a malformed annotation's `ValueError` into
    `ElaborationInvariantError(SI_EDGE_DANGLING)`. That escapes `:2286-2295`, which catches only
    `_UnsupportedExpressionError`, so a malformed annotation anywhere in a predicate or computed
    expression becomes a **hard elaboration refusal**, not a readiness finding. This is the
    chosen answer, not a side effect: an annotation carrying no annotated value is a model the
    product cannot read, and `_create_value_node` already refuses it that way at `:757`. Refusing
    it identically in the walk keeps one rule with one refusal. *Rejected: catching it in the
    walk and downgrading to `_UnsupportedExpressionError`* — that would make the same malformed
    model hard-refuse in one lane and warn in another, which is the asymmetry this item exists to
    remove.

- **D2 — the fourth lane is cured in this item**, by applying the same
  `_without_unit_annotation` **once** to the binding expression read at `elaborate.py:1652`,
  which covers both `_binding_evidence` (`:1656`) and `extract_literal_value` (`:1657`);
  nothing else in `_collect_bound_members` reads the raw expression. *Rejected: characterize
  and file.* The brief's rule is "cure iff the cure is the same unit-annotation rule reaching
  one more lane." It is exactly that — the same wrapper, the same one owner, one call site, no
  new classification branch. Unwrapped, `is_literal_node` is true and `_binding_evidence` yields
  `AUTHORED_LITERAL` evidence with value `0.05` through the path literal bindings already take
  (`elaborate.py:2415-2420`). The lane sits on Item 5's blessed tolerance-band recipe and on the
  rewrite Defect B advertises, so leaving it refused would make D3's message point at a refused
  form. **[AGENT]** (spec Open Question 1, priced both ways; orchestrator ruling **[AGENT]**
  authorised the call.)
  - **The newly admitted set is exactly two shapes (M6c), and it is bounded.**
    (i) `in x = <literal> [unit];` → `AUTHORED_LITERAL`, the fourth lane the spec names.
    (ii) `in x = <reference> [unit];` and `in x = <chain> [unit];` → after the unwrap these
    classify as reference / chain bindings instead of falling to `expression_evidence`. This
    second shape was not named in the earlier draft; it is admitted, it is consistent with the
    rule (the annotation contributed its operand, whatever that operand is), and the fourth-lane
    fixture pins it alongside the literal form.
    **Genuine expression sources stay refused:** `annotated_ast_value` returns `a + b` unchanged
    because its operator is `+`, so `_binding_evidence` still falls through to
    `expression_evidence` and `_unsupported_code` (`:1848-1858`) still maps it to
    `SI_EXPRESSION_SOURCE_UNSUPPORTED`.
  - Consequence to accept: the annotation disappears from the *evidence text* in both shapes.
    `literal_evidence` sets `written_text = str(literal_value)`, so it reads `"0.05"`, not
    `"0.05 [m]"`; `reference_evidence`'s CST read (`binding_evidence.written_reference_text`)
    now spans the unwrapped operand, so it reads `"other_feature"`, not `"other_feature [m]"`.
    That is the rule, not a loss — the annotation contributed its operand. The unit itself
    reaches the profile by its own path (B2), which is what probe P3 confirms.

- **D3 — Defect B splits: the companion supplies the message, codegen supplies the location,
  the de-duplication, and the order.** *Rejected: codegen re-derives the written reference from
  the usage AST.* Codegen does not know *which* operand the profile objected to; it would have
  to re-implement the profile's chain detection to find out, which duplicates the decision in
  the repo that does not own it. The companion holds `node.reference.chain_segments` at the
  decision point (evidence file, `executable_profile.py:535-537`, `:702-707`) — the payload is
  already there and only the `message=` argument is missing. **[AGENT]**

- **D4 — multi-chain identification is one *entry per distinct reference* inside the single
  existing `SI_CONSTRAINT_BLOCKED` diagnostic.** *Rejected: one codegen `Diagnostic` per
  blocked chain.* That multiplies `SI_CONSTRAINT_BLOCKED` rows, and two existing tests hold the
  count: `test_elaboration_payload_identity.py:250` (`assert len(blocked) == 1`) and
  `tests/unit/test_constraint_usage_record_mint.py:94` (asserts *no* `SI_CONSTRAINT_BLOCKED`
  row). Changing the diagnostic count is a disposition-contract change this item is barred from
  (spec Non-Goals). The message gets richer; the row count does not move. **[AGENT]**
  *(An earlier draft also cited `generation/coverage.py`; that file counts catalog rows and
  dispositions and contains no diagnostic reference — citation corrected, A2.)*

- **D5 — one key, used for both de-duplication and ordering: the full normalized identity
  `(basename(file), line, column, reason, construct, message)`.** Every field is normalized
  independently at key-construction time so no `None` ever reaches a comparison:
  `basename(file) if file else ""`, `line if line is not None else -1`,
  `column if column is not None else -1`. A `LocationFact` that is entirely `None` produces
  `("", -1, -1, …)` and sorts first. Because the order key **is** the de-dup identity, no two
  surviving entries can tie, so the sort never falls back to Python's stable-sort residue — i.e.
  never to the companion's walk order, which D5 exists to refuse.
  *Rejected: de-duplicating on `reason` alone* — it would collapse two *different* blocked chains
  at different lines into one entry and lose the identification criterion.
  *Rejected: an order key without `construct`* — two entries differing only in `construct`
  survive de-dup and then tie, reintroducing walk-order dependence (M1).
  *Rejected: `None`-only normalization of the whole `LocationFact`* — a present `LocationFact`
  with a `None` `line` or `column` would compare `None` against `int` and raise `TypeError` at
  sort time (M1).
  *Rejected: the raw absolute path in the key* — checkout-dependent; basenaming in the key as
  well as the rendering keeps every key portable (A4).
  Precedent: `_record_readiness`'s `(formal, code)` collapse (`elaborate.py:1867-1870`).
  **[AGENT]**

- **D6 — codegen renders the location for *every* block reason, as ` [basename:line]`, and
  omits the suffix entirely when the location is absent.** "Absent" means the `LocationFact` is
  `None`, or its `file` is empty, or its `line` is `None` — any of those renders no suffix
  rather than a placeholder, so the message is a function of the payload and never of the
  renderer's mood (M4). `column` is used for ordering only, never rendered.
  *Rejected: rendering the absolute path.* Absolute paths differ per checkout and would make any
  baseline machine-dependent (a known trap in this repo). *Rejected: a `[unknown:?]` placeholder
  for a missing location* — it advertises a location that does not exist. *Rejected: chain-only
  location.* Location is generic and cheap in the renderer, and rendering it for all reasons
  moves every other block reason measurably closer to the `modeling-assumptions.md:535` promise
  without touching the closed reason vocabulary. **[AGENT]**

- **D7 — `test_elaboration_payload_identity.py:236-266` is NOT edited.** Verified by reading it:
  all three assertions are reason-code substring / regex matches over one diagnostic, its
  fixture blocks on `block_real_equality_requires_tolerance` (not a chain), and that reason keeps
  the companion's default message. D6 appends ` [basename:line]` to its detail, which the `.*`
  regex and `in` checks tolerate. **Conditional on invariant 8**: the regex `.` does not cross a
  newline, so a multi-line detail would break it. If implementation finds otherwise, changing the
  test is a **stated** amendment to this design, never a silent test edit. **[AGENT]**

- **D8 — red-first characterizations land as `@pytest.mark.xfail(strict=True)` citing this
  item, and the fix commit removes the marker.** This reconciles the two standing constraints
  that otherwise collide: kept characterizations must land red *before* the fixes (epic
  de-risking), and both trees must be green at every commit (editable-install coupling). Red is
  demonstrated by running each test once with the marker removed and **capturing the failure
  output into the item's close record**, not merely asserting it in a commit message — a
  sentence is unfalsifiable after the fact (A3). `strict=True` is what keeps the pairing from
  rotting: once the fix lands, XPASS fails the suite until the marker is removed. **[AGENT]**

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
codegen    elaborate._build_constraint_nodes     :1097 ─── de-dup + sort on ONE key (D5)
                                                          → "reason: message [basename:line]"
                                                          → joined with "; ", single line (inv 8)
                                                          → ONE SI_CONSTRAINT_BLOCKED Diagnostic

codegen    elaborate._expression_references      :2371 ─── _without_unit_annotation at head,
                                                          recursively (D1); callers are
                                                          :2220 _resolve_aliases and
                                                          :2286 _resolve_computed_expressions
                                                          (computed attrs + predicates)
codegen    elaborate._collect_bound_members      :1652 ─── _without_unit_annotation once on the
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
3. **The *profile's* admitted set is unchanged in both directions.** Nothing newly admitted,
   nothing newly blocked by the profile. Chains stay blocked; `==` stays untoleranced.
   **Codegen's readiness-refused set shrinks**, by exactly the two binding shapes D2 names
   (`in x = <literal> [unit]`, `in x = <reference|chain> [unit]`) and by the currently-refused
   annotation shapes D1 names. Genuine expression sources stay refused. (M5 — the earlier
   unscoped wording contradicted D2 on the page.)
4. **One `SI_CONSTRAINT_BLOCKED` diagnostic per blocked constraint node**, before and after.
5. **Determinism by construction.** The rendered detail is a function of the de-duplicated set
   ordered by the D5 key — never of the companion's walk order, and never of a tie-break.
6. **The advertised rewrite is a supported form.** After D2, `in tol = 0.05 [m];` is supported,
   so the message may name the annotated binding. If P3 falsifies that, the message drops the
   annotation and reads `in tol = 0.05;`.
7. **A `[`-annotation's second operand is never a user-model feature.** D1's one behavioural
   exception (M6b): if it were, the unwrap would drop a real dependency edge. No supported
   authoring shape produces it, and the test plan asserts no dependency edge is lost by the
   bare/annotated twin comparison.
8. **The rendered detail is a single line — it contains no newline.** Two existing consumers
   depend on it: `test_elaboration_payload_identity.py:243` matches
   `SI_CONSTRAINT_BLOCKED.*blocked_guard.*block_real_equality_requires_tolerance`, where regex
   `.` does not cross a newline, and `project.py:97` folds the same detail into
   `ProjectionError`'s message for the `pytest.raises` at `:265`. Multi-entry details join with
   `"; "`, never a newline; the message examples below are wrapped for the document only (M2).

## Component Overview

| Component | Location | Responsibility after this item |
|---|---|---|
| Unit-annotation rule | `src/sysml_codegen/extraction/unit_annotation.py` | Unchanged. Still both spellings, still the only owner. |
| Elaborator refusal policy | `elaborate.py:862-878` (`_without_unit_annotation`) | Unchanged. Gains two more callers. |
| Reference walk | `elaborate.py:2371-2412` | Applies the rule at its head before dispatch, at every recursion level (D1). |
| Binding collector | `elaborate.py:1619-1662` | Applies the rule once at `:1652`, covering both classification and the literal read (D2). |
| Block renderer | `elaborate.py:1097-1108` | De-duplicates, orders, and renders location (D3–D6). New private helper `_render_block_reasons(decision)`. |
| Companion chain-block sites | `agentic-mbse: executable_profile.py:535-537`, `:702-707` | Pass an explicit `message` (D3, D9). |

The renderer helper is the only new named thing in either repo. Without it the de-dup, sort,
and location render would inline into `_build_constraint_nodes`, which already carries the node
minting loop; the helper exists so the ordering key is testable on its own.

## The Message Shape (rendered text)

**Every example below is one line.** The wrapping is this document's; a newline in the string
would break invariant 8.

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
each distinct reference once, joined by `"; "`, ordered by the D5 key. The 13 identical copies
collapse to the number of distinct references.

Unchanged reasons keep the companion default and gain only the location:

```
constraint profile blocked execution: block_real_equality_requires_tolerance: real_equality: block_real_equality_requires_tolerance [model.sysml:19]
```

With no usable location, the suffix is omitted entirely (D6):

```
constraint profile blocked execution: block_xor: logical_operator: block_xor
```

**Residue to record (success criterion 3).** Every block reason other than
`block_feature_chain` still renders the companion's `construct: reason` default. After this
item they name *where* (D6) but not *what construct* beyond the reason code. Per the spec, that
residue is named here rather than left implied. The published block list
(`docs/architecture/modeling-assumptions.md:480-486`) has nine members; eight are residue:

| Residue reason | Still unable to name the construct |
|---|---|
| `block_invocation` | yes (M3 — omitted from the earlier draft) |
| `block_assert_by_reference` | yes |
| `block_real_equality_requires_tolerance` | yes |
| `block_xor` | yes |
| `block_implies` | yes |
| `block_incompatible_dimensions` | yes |
| `block_unknown_exact_unit` | yes |
| `block_unit_conversion_required` | yes |
| `block_feature_chain` | **no — cured by this item** |

**Totality caveat, to be discharged at implement.** That list is the *published* one, and
`modeling-assumptions.md:480` hedges it with "most commonly." The authoritative set is the
companion's `REASON_CODES` (`executable_profile.py`, closed and enforced in `__post_init__`),
which this design's sandbox cannot read. The implement stage must grep `REASON_CODES` for its
`block_*` members and, if any is absent from the table above, add it to the close record. The
close record carries the final list, not this table.

## Fixture Plan

Frozen twins (`catf_mfe_model`, `catf_mfe_d5`) untouched. All four are new fixtures under
`tests/fixtures/`, each carrying the repo's fixture-header comment convention (see
`tests/fixtures/unit_annotation_lanes/model.sysml`).

| Fixture | Shape | Pins |
|---|---|---|
| `predicate_unit_annotation` | Part def with an in-scope attribute and an **inline asserted** constraint: an inequality carrying a compatible unit-annotated literal. Plus a `Noop` calc def so the pipeline has a module (the `constraint_blocked_profile` idiom). | Defect A cured; the gate *works* (admitted, catalogued, assessed, counts toward coverage). |
| `predicate_unit_annotation_bare` | The same model with `[m]` removed. | The asymmetry pin, mirroring `unit_annotation_lanes_bare`. |
| `predicate_unit_annotation_incompatible` | The same predicate with a dimensionally incompatible annotation. | Invariant 2 as a **regression guard on the companion path** — the profile still blocks. Not a discriminator for D1 (A1): the profile runs at `elaborate.py:403` before the walk, so it would pass either way. |
| `constraint_binding_unit_annotation` | A constraint usage binding `in tol = 0.05 [m];` **and** a second binding `in ref = other_feature [m];`, predicate an inequality using both. | The fourth lane cured in both shapes D2 admits (M6c): `AUTHORED_LITERAL` with value `0.05`, a reference binding for the second, no readiness finding for either. |
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
| Unit semantics survive (invariant 2) | incompatible fixture still BLOCKs with the profile's dimension reason (regression guard, A1) | same |
| No dependency edge is lost (invariant 7) | annotated and bare twins produce identical module inputs; no `SI::` source | same |
| Malformed annotation route (M7) | a predicate carrying `[` with no annotated value hard-refuses with `SI_EDGE_DANGLING` | same |
| Fourth lane, both admitted shapes (M6c) | `in tol = 0.05 [m]` → `LiteralInput(0.05)`; `in ref = other_feature [m]` → reference binding; neither yields `SI_EXPRESSION_SOURCE_UNSUPPORTED`; `in bad = a + b` still does | new `tests/conformance/test_constraint_binding_unit_annotation.py` |
| Chain block names reference + rewrite | rendered detail contains the joined chain text, the `in <formal> = <chain>;` rewrite, and `basename:line` | new `tests/conformance/test_blocked_chain_diagnostic.py` |
| Multi-chain, distinct, deterministic | 3 occurrences → 2 entries; two elaborations of one model produce byte-identical detail | same |
| Single-line detail (invariant 8, M2) | `assert "\n" not in blocked[0].detail` | same |
| Missing location renders no suffix (M4) | a diagnostic with `location=None` renders without ` [...]` — unit test over `_render_block_reasons` | new `tests/unit/test_render_block_reasons.py` |
| Order key is total and type-safe (M1) | `_render_block_reasons` over hand-built diagnostics with `None` `line`/`column` and with two entries differing only in `construct`: no `TypeError`, stable output under input permutation | same |
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
- **P2 — regression guard, not a discriminator (A1).** Elaborate
  `predicate_unit_annotation_incompatible` after D1.
  *Expected:* still BLOCKs on a dimension reason. This confirms the companion path is intact; it
  does **not** discriminate D1, because the profile verdict is computed at `elaborate.py:403`
  before and independent of the reference walk, so it would pass whether or not the walk drops
  the unit. Run it once as cheap insurance; **do not gate step 2 on it.** If it *does* fail,
  something outside this design's model has changed — surface, do not patch.
- **P3 — the real unit-loss exposure (A1). Does the fourth-lane cure keep the binding's unit
  visible to the profile?** Elaborate `constraint_binding_unit_annotation` after D2.
  *Discriminating:* value is `0.05`, no readiness finding, and the profile's verdict matches the
  same model written `in tol = 0.05;` plus a declared unit → primary. If the profile loses the
  unit, invariant 6 fires: the advertised rewrite drops the annotation.
- **P4 — ANSWERED (orchestrator static read, carried in the design review).** `chain_segments`
  **includes the root**, and `source_name` carries the full authored text as a second carrier.
  So the message uses `".".join(chain_segments)`, and B3 holds — no companion CST read is
  needed. The implement stage re-verifies this citation before editing (per the evidence file's
  working constraint), but the design branch is selected.

## Non-Goals

Carried unchanged from the spec, restated only where design could be misread as touching them:
no chains admitted in predicate bodies; no `==` tolerance semantics; no profile expansion in
either direction; no new `REASON_CODES` entry (D9); no change to BLOCK-halts-generation or any
part of the Item 2 disposition/severity contract; no frozen-twin migration; no unit conversion
or constant folding (DD-R25); TEAx untouched.

## Potential Risks

Re-ranked per review advisory A1 — the earlier draft's top risk was structurally unreachable.

- **Unit loss on the binding lane (D2) — the largest.** In `in tol = 0.05 [m];` the annotation
  carries both the value and the unit on one node, and codegen's unwrap decides what the binding
  contributes. This is where "carried, never applied" can actually break. Guarded by P3 and by
  invariant 6's fallback (the advertised rewrite drops the annotation if P3 falsifies).
- **The order key raises or ties at sort time.** A `None` `line`/`column` compared against an
  `int`, or two entries differing only in `construct`, would produce a `TypeError` or a
  walk-order-dependent detail — a flaky landing, not a documentation gap. Closed by D5's
  per-field normalization and full-identity key; pinned by the `_render_block_reasons` unit test.
- **A newline reaches the rendered detail.** It would break
  `test_elaboration_payload_identity.py:243` and the `project.py:97` fold. Closed by invariant 8
  and the `"\n" not in detail` assertion.
- **D1's malformed-annotation route (M7)** turns a bad model into a hard refusal in lanes that
  previously produced a readiness finding. Decided deliberately, but it can surface in an
  unrelated fixture. Mitigation: run the full licensed suite at step 2, not only the new tests.
- **B2 false on the D1 side — structurally low, not zero.** The profile runs at
  `elaborate.py:403` from companion facts, independent of the walk, so D1 cannot disable
  dimension checking by construction. The incompatible fixture is kept as a companion-path
  regression guard (cheap), not as this bet's discriminator.
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

**Fixed for the plan:** D1's seam (walk head, recursive, not predicate entry) and its stated
widening bound; M7's hard-refusal route; D2 (the fourth lane is cured here) and its two admitted
shapes; D3's split (companion message, codegen location + de-dup + order); D4 (one diagnostic,
richer detail); D5's single normalized key for both de-dup and ordering; D6's no-location
rendering; invariant 8 (single line); D7 (that test is not edited); D8's xfail mechanism with
captured red output; the landing order.

**Open:** the probes. P1 can change a fixture; P3 can change the advertised rewrite (invariant
6); P4 can change which companion field the message joins. None can move a seam — the review
confirmed all three.

**De-risk first: P3, then P1.** P3 is the genuine unit-loss exposure and gates step 3's fix.
P1 selects the demonstration fixture. P2 runs once as insurance and gates nothing (A1).

## Review Resolutions

Against `design-review.md` (verdict **Revise**, 2026-08-13). The review confirmed all three
seams — D1 head-of-walk, D2 one unwrap at `:1652`, and the Defect B split — and none moved.

| Finding | Resolution |
|---|---|
| **M1** — order key not total, not type-safe | D5 rewritten. **One** key now serves de-dup *and* ordering: `(basename(file), line, column, reason, construct, message)`. `construct` is in it, so no two surviving entries tie and the sort never falls back to walk order. Each field is normalized independently at construction (`file or ""`, `line`/`column` `-1` when `None`), so no `None`-vs-`int` comparison can occur. Both failure modes are pinned by the new `tests/unit/test_render_block_reasons.py` row in the test plan. |
| **M2** — no-newline is an unstated bet | Promoted to **invariant 8**, citing both consumers (`test_elaboration_payload_identity.py:243`, `project.py:97`→`:265`). The Message Shape section now opens by stating the examples are wrapped for the document only, and the multi-reason example is shown unwrapped. D7's "not edited" claim is now explicitly *conditional on invariant 8*. Test plan gains `assert "\n" not in detail`. |
| **M3** — residue list omits `block_invocation` | Residue rewritten as a nine-row table covering the full published block list (`modeling-assumptions.md:480-486`), including `block_invocation` and `block_assert_by_reference`. Because that list is hedged "most commonly" and this sandbox cannot read the companion, a **totality caveat** requires implement to grep `REASON_CODES` for `block_*` members and reconcile; the close record carries the final list. |
| **M4** — no rendering specified for absent location | D6 now defines absent (`LocationFact` `None`, empty `file`, or `None` `line`) and specifies **omit the suffix entirely**, with a worked example. Placeholder rendering rejected in writing. `column` is ordering-only, never rendered. |
| **M5** — invariant 3 contradicts D2 | Invariant 3 scoped: *the profile's* admitted set is unchanged in both directions; **codegen's readiness-refused set shrinks** by exactly the shapes D1 and D2 name, with genuine expression sources still refused. |
| **M6** — reach mis-stated in three places | (a) Lane inventory corrected in D1: `:2220` is `_resolve_aliases`; computed attributes enter at `:2286` with predicates. The architecture diagram carries the same correction. (b) Widening bound stated: alias and computed lanes are already top-level-unwrapped at `:757`, so D1 newly affects them only for *nested* annotations, all of which fail today — **no currently-green behaviour changes**, with the single exception of a `[` second operand resolving to a user-model feature, now pinned as **invariant 7** with a test-plan row. (c) D2's second admitted shape `in x = <reference\|chain> [unit]` is named, the fourth-lane fixture gains a binding for it, and the "genuine expression sources stay refused" verification is recorded. |
| **M7** — new hard-refusal route | Stated as a deliberate decision inside D1: `_without_unit_annotation`'s `SI_EDGE_DANGLING` escapes `:2286-2295` (which catches only `_UnsupportedExpressionError`), so a malformed annotation hard-refuses. Rationale given (one rule, one refusal — matching `:757`), the downgrade alternative rejected in writing, a test-plan row added, and a suite-wide run at step 2 listed as mitigation. |
| **A1** — re-rank risks, re-state B2 | **Taken.** B2 gains a scoping note: D1 is structurally safe (profile computed at `elaborate.py:403`, independent of the walk); the live exposure is D2's binding lane. "Potential Risks" re-ranked with D2 unit loss first. P2 relabelled a **regression guard, not a discriminator**, and explicitly does not gate step 2. Handoff de-risk order changed from "P2 then P1" to "P3 then P1". |
| **A2** — D4's citation | **Taken.** `generation/coverage.py` removed; replaced with `test_elaboration_payload_identity.py:250` and `tests/unit/test_constraint_usage_record_mint.py:94`, with a note recording the correction. |
| **A3** — D8's red evidence unfalsifiable | **Taken.** D8 now requires capturing the marker-removed failure **output** into the close record, not a commit-message sentence, and names `strict=True`'s XPASS as the anti-rot mechanism. |
| **A4** — basename in the keys | **Taken.** Folded into M1's single key: `basename(file)` in the key, not only the rendering. |
| **A5** — line drift `:1651` → `:1652` | **Taken.** Corrected in D2, the Research Findings paragraph, the component table, and the architecture diagram. |
| **A6** — `written_text` note incomplete | **Taken.** D2's consequence note now covers both shapes: `"0.05"` for the literal and `"other_feature"` for the reference (CST span follows the unwrap). |

**Nothing declined.** No finding required re-deciding a seam, so per the review's own note a
second full review is not warranted — a diff read against M1–M7 is enough.

---
**Next Step:** diff read against M1–M7, then `/_my_plan`.
