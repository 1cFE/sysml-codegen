# `REASON_CODES` reconciliation — success criterion 3, discharged against the full set

**Why this file.** The spec's third success criterion is that
`docs/architecture/modeling-assumptions.md:535` — "If the profile BLOCKs an asserted constraint,
the generation error names the exact construct to fix" — is *true* after this item, and that any
reason still unable to keep it is **named in the item's record rather than left implied**.

The design answered that against the **published** block list, which has nine members and is
hedged "most commonly". The authoritative set is the companion's closed `REASON_CODES`
(`agentic-mbse: src/agentic_mbse/sysml/executable_profile.py:66-100`, enforced in
`EligibilityDiagnostic.__post_init__`, DD-R05): **23 `block_*` members** and 4 `warn_*`. This
file reconciles all 23, read at companion `0a52942`. **This is the list, not the design's table.**
The close record carries it forward.

## What changed for every reason, cured or not

Codegen now renders ` [basename:line]` on **every** block reason and collapses repeats
deterministically (D5/D6). So every one of the 23 gained *where*. What separates the rows below
is whether the message also says *what to write instead*.

Three grades:

- **Names the fix** — the message states the offending thing and the supported rewrite. A modeler
  can act without reading the profile's source.
- **Names the shape** — the message states the construct and the rule it broke, in words. The
  modeler still locates the term themselves, from the line.
- **Names the reason only** — `construct: reason`, plus the location. The construct is a category
  (`invocation`, `assert_by_reference`), not the authored text.

## The 23

| Reason | Grade after this item | Message it carries |
|---|---|---|
| `block_feature_chain` | **Names the fix** | **Cured here.** Names the chain as authored and the bindings rewrite: `feature chain 'bioshield.outer_radius' is not executable in a predicate body; bind it to a constraint formal in the usage (in outer_radius = bioshield.outer_radius;) and use the formal in the predicate` |
| `block_real_equality_requires_tolerance` | Names the shape | explicit, `:646` |
| `block_integer_equality_unpreservable` | Names the shape | explicit, `:651` |
| `block_ordering_category_pair` | Names the shape | explicit; reports both categories and asks for one admitted pair |
| `block_unresolved_operand` | Names the shape | explicit; "resolve both operands to typed model features" |
| `block_unsupported_operand_category` | Names the shape | explicit; "use Integer, Real, or exact-unit Quantity" |
| `block_unknown_exact_unit` | Names the shape | explicit; "declare the exact modeled units" |
| `block_incompatible_dimensions` | Names the shape | explicit; "use operands with the same modeled dimension" |
| `block_unit_conversion_required` | Names the shape | explicit; "express both operands in the same exact modeled unit" |
| `block_malformed_operand_fact` | Names the shape | explicit at both sites; "re-capture the model facts with a compatible companion package" |
| `block_invalid_assertion_polarity` | Names the shape | explicit; names the offending JSON type and the repair |
| `block_unsupported_node` | Mixed | explicit where it is an operand-count violation (arithmetic, comparison, connective) or an unrecognized source form; **reason only** at the two catch-alls (`:609`, `:862`), where the construct is `type(node).__name__` |
| `block_unsupported_operator` | Names the reason only | default, but the *construct* is the operator itself, so the text reads e.g. `mod: block_unsupported_operator` |
| `block_xor` | Names the reason only | default; construct is the operator |
| `block_implies` | Names the reason only | default; construct is the operator |
| `block_non_predicate_root` | Names the reason only | default; construct is the node kind that stood in the predicate position (`comparison`, `feature_ref`, `literal`, `unit_annotation`, `arithmetic`) |
| `block_invocation` | Names the reason only | default; construct `invocation`. Does not name which function |
| `block_assert_by_reference` | Names the reason only | default; construct `assert_by_reference` |
| `block_unresolved_definition` | Names the reason only | default; construct `definition_lookup`. Does not name the definition it failed to find |
| `block_missing_predicate` | Names the reason only | default; construct `missing_predicate` |
| `block_derived_unit_unsupported` | Names the reason only | default; construct `arithmetic`. Does not name the operator or the units |
| `block_unitless_dimensioned` | Names the reason only | default; construct `arithmetic` |
| `block_non_numerical_containment` | Names the reason only | inherits the replaced warning's message, which describes non-numerical semantics rather than a fix |

## The residue, stated plainly

**One of 23 names the fix. Eleven name the shape. Ten name the reason only, and one is mixed.**

That is the honest reading of criterion 3 after this item: the published promise is now true for
`block_feature_chain`, and *closer* for everything else — every reason names where it was decided,
where before none did. It is **not** true in the strong sense for the ten reason-only rows.

**Why that is acceptable here rather than filed as a defect.** This item's scope was the two
reproduced Q8 defects. The reason-only rows split into two kinds:

- **Cheap and worth doing** — `block_invocation` (name the function), `block_unresolved_definition`
  (name the definition it looked for), `block_derived_unit_unsupported` (name the operator and the
  two units). Each needs one `message=` at one companion site, exactly like this item's fix.
- **Already adequate in practice** — `block_xor`, `block_implies`, and `block_unsupported_operator`
  carry the operator as their construct, and `block_non_predicate_root` carries the node kind. With
  a location, a modeler has what they need.

**Filed:** the three cheap rows above are the natural follow-on, and Item 5's all-65 migration is
what will show whether they actually cost anyone time. Recorded here rather than opened as work
this item did not scope.

## Also surfaced, and not a `REASON_CODES` matter

- **The location is the constraint usage's, not the offending term's.** The `LocationFact` the
  companion attaches to a decision is the usage's; there is no per-node location in the payload.
  For a long predicate every entry reads the same `file:line`. Naming the reference is what
  disambiguates within a predicate, and `block_feature_chain` now does. A per-node location is a
  companion payload change.
- **A unit written on a constraint *binding* is dimensionally inert to the profile.** Measured at
  Phase 3 (P3): `in measured = width [m]; in tol = 0.05 [s];` is *admitted*. A bound formal takes
  its operand category from the definition's declared type, so the binding's annotation never
  reaches `classify_ordering`. True before and after this item. It matters for Item 5, whose
  tolerance-band recipe is exactly that shape: the band can carry a unit for a human reader, and
  the gate will not check it.
