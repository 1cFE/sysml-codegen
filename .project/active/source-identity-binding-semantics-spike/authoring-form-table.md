# Authoring-Form Evidence Table (SOURCE-IDENTITY Item 1)

**Date**: 2026-08-05 · **Branch**: `nested-override-tripwire` @ `fa9e0d0`
**Probes**: `probes/probe_referents.py`, `probes/probe_redef_link.py`,
`probes/scan_corpus.py` · raw evidence in `probes/raw/`
**Provenance**: all "observed" columns are SysIDE-level facts read directly off AST
nodes (licensed live load); "extractor view" is the implementation under test,
recorded for comparison only and never used to fill another column. Standards
columns cite primary normative text (KerML 1.0 / SysML v2 Part 1).

This table is decision input for the Item-3 owner disposition. It names proven
meaning, uncertainty, prevalence, and migration consequence. It does **not** choose
project support policy.

## The forms

Common topology in every probe model: one `part def 'Probe Plant'` attribute
`R : Real default 3.0`, two calc consumers, one concrete occurrence with
`:>> R = 12.7` where expressible.

| # | form | written RHS | probe model |
|---|---|---|---|
| 1 | bare self-named | `in R = R;` | `form_bare.sysml` |
| 1c | bare renamed (control) | `in r_in = R;` | `form_control_renamed.sysml` |
| 2 | owner-qualified | `in R = 'Probe Plant'::R;` | `form_owner_qualified.sysml` |
| 3 | feature chain | `in R = plant.R;` | `form_chain.sysml` |
| 4a | occurrence index, KerML spelling | `in R = plants#(1).R;` | `form_bracket_hash.sysml` |
| 4b | occurrence index, square bracket | `in R = plants[1].R;` | `form_bracket_sq.sysml` |

## Evidence

| # | SysIDE referent (observed) | intended outer source | concrete-occurrence evidence | diagnostics | extractor view (comparison only) |
|---|---|---|---|---|---|
| 1 | the calc usage's **own `in` parameter** (`…::c1::R`, ReferenceUsage) — a degenerate self-binding | `'Probe Plant'::R` at occurrence `plant` | none in the referent; the override lives on an unrelated-by-referent node | **none — silent** | `REFERENCE`, `source_path` = own param QN, written qualifier `None` |
| 1c | outer `'Probe Plant'::R` (AttributeUsage) — shadowing is the entire cause of form 1's degeneracy | same | referent is def-level, not occurrence-level | none | `REFERENCE`, `source_path` = def attribute QN |
| 2 | def-level `'Probe Plant'::R` (AttributeUsage) | same | referent is def-level; occurrence must be recovered from context | none | `REFERENCE` + written qualifier `'Probe Plant'` carried |
| 3 | the **redefining feature at the usage** (`'Design Ctx'::plant::R`, ReferenceUsage — the `:>> R = 12.7` site); chain root referent = the `plant` usage | same | **referent IS the concrete-occurrence feature**; its `owned_redefinitions` edge names `redefined_feature = 'Probe Plant'::R` | none | `CHAIN`, `source_path='plant.R'` |
| 4a | chain target = **def-level** `'Probe Plant'::R`; the index lives only in an `IndexExpression(plants, LiteralInteger i)` operand, not in the target's identity | `R` of the i-th occurrence of `plants[2]` | occurrence selection present syntactically, absent from referent identity | none | `CHAIN`, **`source_path='R'` — the index segment is silently dropped** (new identity-loss site, `_parse_chain_expression` skips non-FRE first operands) |
| 4b | chain target = `<placeholder Feature>` (unresolved) | same as 4a | n/a | **4 load errors**: `quantity-operator-expression` ×2, `No Feature named 'R'` ×2 — `[i]` is the quantity/unit bracket, not an index | `CHAIN`, `source_path='<placeholder Feature>'`; pipeline fail-closes earlier (`load_models()` returns False on errors) |

## Standards meaning (KerML 1.0 / SysML v2 Part 1)

Full rulings with quoted normative text: `standards/kerml_ruling.md`,
`standards/sysml_ruling.md`. Both were produced against the observed table above
and asked to reconcile, not to rubber-stamp. Condensed:

| # | normative meaning | key citations | residual ambiguity |
|---|---|---|---|
| 1 | **Degenerate self-binding, normatively required.** Nearest-scope resolution reaches the calc's own parameter first; no carve-out excludes a feature from its own value expression's scope. The resulting binding asserts the tautology `R == R` — legal, inert, and no diagnostic is required by the spec. The spec provides NO mechanism by which the bare form reaches the outer attribute. | KerML §8.2.3.5.2/§8.2.3.5.4 (resolution), §7.4.11 (feature value = binding); SysML Part 1 §7.5 (defers to KerML), §7.13.4, §7.19.2 | Low. Part 1 never exemplifies this exact collision; the verdict derives from the general rule. |
| 1c | Bare name with no collision resolves outward to the enclosing part's attribute — ordinary nearest-scope resolution. | KerML §8.2.3.5.4 | Low. |
| 2 | Qualified name legally and unambiguously denotes the **definition-level** attribute; multi-segment names bypass shadowing. | KerML §8.2.3.5.1 step 3, §8.2.3.5.3 | Last-segment resolution uses *visible* (public) memberships; the spec has no explicit "features default public" sentence. Observed behavior implies default-public. |
| 3 | Chain resolves the trailing segment in the context of the first segment's result parameter → the **redefining feature at the usage** (occurrence-relative). Redefinition creates a distinct feature that *replaces* the inherited one and its value (12.7) wins over the default in that context. | KerML §7.4.9.3, §8.2.3.5.2, §7.3.4.5, §7.3.4.6; SysML Part 1 §7.6, §7.13 | Moderate: the spec doesn't spell out sentence-for-sentence that a referenced feature's *nested* redefinitions are exposed through its result parameter; SysIDE's reading is defensible, not verbatim-mandated. |
| 4a | **Well-formed, value semantics only.** `#(i)` is genuine 1-based sequence indexing (`BaseFunctions::'#'`), but the whole expression denotes a computed value sequence, NOT a feature identity: there is no "first plants occurrence" feature for `.R` to anchor to, and the index is not part of the referent's identity. | KerML §7.4.9.3, §8.2.5.8.2 + Table 7; SysML Part 1 §7.17 example, §7.6 (ordered usages) | Whether `#` applies cleanly to a composite part usage of multiplicity `[2]` (vs an ordered attribute sequence) is not illustrated; and the observed def-level referent is the *only* identity the expression carries. |
| 4b | `[...]` after an expression is the **undefined bracket operator** (`BaseFunctions::'['`) that SysML overloads for quantity/units (`2000[kg]`). It is not indexing, in any conforming tool. SysIDE's hard error is consistent (spec says a tool "should give a warning" absent a domain definition). | KerML §8.2.5.8.2 Note 2 + Table 7; SysML Part 1 `:8515` unit example | None at KerML level. |

**The cross-form finding that matters for Item 3**: even the two spec-correct
spellings for "the enclosing part's attribute" denote **different elements** — an
owner-qualified name reaches the def-level general feature, while an
occurrence-rooted chain reaches the redefining feature at that occurrence. Part 1
supplies both mechanisms and never adjudicates which one is THE idiom; there is no
`self`/`this` keyword to root a chain at the current occurrence. Any project
disposition that migrates the bare form must therefore also choose *which* of the
two correct forms carries the intended "one modeled value at its concrete
occurrence" semantics — the standards do not choose for us
(`standards/sysml_ruling.md` Q5 residual ambiguity 2).

## Prevalence and migration consequence

From `scan_corpus.py` over live authored trees (usage bindings only; calc-def typed
parameter defaults excluded):

| form | codegen fixtures (329) | fusion-tea models (32) | stellarator-demo models (236) | migration consequence if rejected |
|---|---|---|---|---|
| 1 bare self-named | 91 | 15 | 109 | ~124 live external bindings + 91 fixture bindings must be rewritten (qualified or chain), plus snapshot/baseline recapture for every touched fixture |
| 1c bare renamed | 45 | 2 | 56 | n/a — resolves to the outer attribute today; residual risk only if a rename collides with another calc member |
| 2 owner-qualified | 85 | 0 | 0 | none externally; the form exists only in the in-repo fixture corpus |
| 3 feature chain | 85 | 13 | 64 | n/a — resolves occurrence-relative today |
| 4a `#(i)` indexed | 0 | 0 | 0 | zero-cost to reject or defer; no authored instance exists |
| 4b `[i]` bracketed | 0 | 0 | 0 | already rejected by the language (load error); zero-cost to document as invalid |

## Uncertainty register

- Form 2's referent is the **definition-level** attribute. Which concrete occurrence
  applies is not in the referent; whether written-reference + occurrence-owner
  evidence suffices to recover it is Item 2's evidence-sufficiency question, not
  settled here.
- Form 4a loads cleanly and evaluates as an expression, but whether SysIDE (or the
  standard) gives `plants#(1).R` a *feature identity* usable as a binding source —
  rather than only a value — is standards-pending below.
- The corpus scan is textual (regex over single-line bindings). Multi-line binding
  expressions would be missed; none were observed in spot checks.
- Constraint-side and aggregation-side consumers of these same forms are Item 2
  scope (route matrix), deliberately not probed here.
