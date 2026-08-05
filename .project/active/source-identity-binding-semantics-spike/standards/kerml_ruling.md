# KerML 1.0 normative ruling per authoring form

**Provenance**: [AGENT] kerml-expert subagent (Opus), 2026-08-05, reading
`/home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_KerMLSpec/full_document.md`.
Question set and observed-behavior inputs are in the spike findings log. Report
retained verbatim below; nothing edited.

---

FORM-1 through FORM-5 KerML 1.0 normative analysis. All citations are to the KerML 1.0 spec (`SysML_KerMLSpec/full_document.md`).

---

**Q1 — FORM 1 `in R = R` bare-name self-binding**

VERDICT: The calc usage's own `in` parameter is the normatively-required resolution. Nearest-scope name resolution reaches it before the outer `'Probe Plant'::R`, and the spec contains no carve-out excluding the feature-being-valued from its own value expression's scope. The self-reference is what the algorithm produces, not a tool artifact.

Mechanism, in three steps, each grounded:

1. The RHS `R` is a bare qualified name in expression position, i.e. a `FeatureReferenceExpression`. §8.2.5.8.3: "`FeatureReference : Feature = [QualifiedName]`" and §7.4.9.4: "A feature reference expression is represented simply by the qualified name of the feature being referenced."

2. The local Namespace for resolving that name is fixed by §8.2.3.5.2, Membership case: "If the membershipOwningNamespace is a `FeatureReferenceExpression` … then the local Namespace is the non-invocation Namespace … the nearest containing Namespace that is none of the following: FeatureReferenceExpression, InstantiationExpression, ownedFeature of an InstantiationExpression, ownedFeature of the result of a ConstructorExpression." The nearest such namespace is the owning feature `in R` (a Feature, not an expression).

3. Resolution then climbs by §8.2.3.5.4 (Full Resolution): "If the name has a local resolution relative to a Namespace … then that is also its full resolution … Otherwise: If the Namespace is not a root Namespace, then the full resolution … is determined as its full resolution relative to the owningNamespace." The feature `in R` has no member named `R` (a redefining feature is not a member of itself, and per §7.3.4.5 redefined features "are not inherited"), so resolution climbs to the calc usage `c1`, whose membership named `R` is exactly the `in` parameter. That is the first match.

Carve-out check: the only special exclusion in the whole resolution algorithm is for redefined-feature qualified names. §8.2.3.5.1: "The basic name resolution process is used directly … except when the qualified name specifies the redefinedFeature of a Redefinition with an owningFeature that has an owningType." §7.3.4.5 restates it: "the local namespace of the owning type of the redefining feature is not included in the name resolution of the redefined features." That carve-out governs the LHS `:>>`/`redefines` target, NOT a value-expression RHS. No provision excludes the owning feature from its own value expression's scope.

RESIDUAL AMBIGUITY: Low. Whether the local Namespace is taken as the owning feature `in R` or the enclosing usage `c1`, full resolution lands on the same parameter `c1::R`, because `R` is a member of `c1` and the parameter shadows the inherited/outer attribute. The result is stable either way.

---

**Q2 — FORM 2 `'Probe Plant'::R` qualified name**

VERDICT: Denotes the definition-level attribute `'Probe Plant'::R`. Legal and unambiguous; a multi-segment qualified name bypasses nearest-scope shadowing.

§8.2.3.5.1, step 3: "Otherwise, resolve the qualification part of the qualified name relative to the local Namespace of the original qualified name. This must resolve to a Namespace, and the resolution of the original qualified name is then the visible resolution of its last segment name relative to this Namespace." So `'Probe Plant'` resolves (climbing out of `c2` to package `P`) to the part def, then `R` is resolved by visible resolution within it.

§8.2.3.5.3 defines what "visible" admits: "All ownedMemberships of the Namespace with visibility = public … If the Namespace is a Type, then all inheritedMemberships of the Type with visibility = public." The attribute `R` declared directly in `'Probe Plant'` is an owned member; unless marked `private` it is visible, so the last segment resolves to it. Referring to a definition-level feature from inside a nested calc is not restricted anywhere in §8.2.3.5 — the qualification part simply names the part def as the context namespace.

RESIDUAL AMBIGUITY: One dependency worth naming — resolution of the last segment uses *visible* (public-only) memberships (§8.2.3.5.1 step 3 + §8.2.3.5.3), whereas resolution of a single bare name uses *full* resolution (§8.2.3.5.4). The spec does not state a default visibility for an owned attribute of a `part def`; if a tool treated it as non-public, the last-segment visible resolution would fail. Observed behavior implies default-public, which is the natural reading but is not pinned by an explicit "features are public by default" sentence in the resolution clauses.

---

**Q3 — FORM 3 `plant.R` feature chain expression**

VERDICT: The normative referent is the redefining feature under `plant` (`'Design Ctx'::plant::R`, the `:>> R = 12.7` site), reached by resolving the trailing segment in the context of `plant`'s result parameter, whose visible members include `plant`'s nested redefinition. Redefinition is normatively a distinct feature that replaces the inherited one in that namespace, and the chain resolves through it.

Two grounds:

Chain resolution context — §7.4.9.3 (Feature chain expression): "The qualified name for the referent feature is resolved using the result parameter of the primary expression as the context namespace (see 8.2.3.5), but considering only visible memberships." §8.2.3.5.2 (Membership → FeatureChainExpression case) makes this precise: "the local Namespace is the result parameter of the argument Expression of the FeatureChainExpression." The argument expression is the reference to `plant`; its result parameter carries `plant`'s members, which include the nested owned redefinition of `R`.

Redefinition creates a distinct, replacing feature — §7.3.4.5: "When redefined, however, these otherwise inheritable features are not inherited and are, instead, replaced by the redefining feature." And the values coincide: "Redefinition is a kind of subsetting that requires the values of the redefining feature and the redefined feature to be the same on each instance." So `plant`'s namespace exposes `plant::R` (the redefining feature, value 12.7), not the inherited `'Probe Plant'::R`; local resolution finds the redefining feature first. The referent is the usage-site feature, whose value semantics are the composition (`plant` then its `R`) per §7.3.4.6: "The values of a chained feature are the same as the values of the last feature in the chain."

RESIDUAL AMBIGUITY: Moderate. The spec says the context is "the result parameter of the primary expression … considering only visible memberships," but does not explicitly state that a `FeatureReferenceExpression`'s result parameter re-exposes the *nested owned redefinitions* of the referenced feature (as opposed to only the declared type `'Probe Plant'`'s def-level members). SysIDE's choice of the nested `:>> R` is a defensible reading — `plant` owns that redefinition as a visible member — but the interaction between "result parameter as namespace" and a referenced feature's nested body members is not spelled out sentence-for-sentence.

---

**Q4 — FORM 4 `plants#(1).R` (index then chain)**

VERDICT: Well-formed. It is a `FeatureChainExpression` whose primary operand is the `IndexExpression` `plants#(1)`; the trailing `.R` resolves to the DEF-level `'Probe Plant'::R`. Critically, KerML gives this expression **value semantics only** — it denotes a computed sequence of values, not a feature identity. The `#(1)` index is a value computation, so there is no "the first `plants` occurrence" feature for `.R` to hang an identity on; only the trailing referent `R` is a feature, and the index is not part of that feature's identity.

Grounds:

Parse — §8.2.5.8.2: "`FeatureChainExpression = ownedRelationship += NonFeatureChainPrimaryArgumentMember '.' ownedRelationship += FeatureChainMember`" and "`IndexExpression = … PrimaryArgumentMember '#' '(' … SequenceExpressionListMember ')'`". The index operand is an expression, so the whole thing is a FeatureChainExpression, not a plain feature chain.

`#` is genuine sequence indexing — §7.4.9.3: "An index expression specifies the invocation of the indexing function '#' from the BaseFunctions library model … the first operand is expected to evaluate to a sequence of values, and the second operand is expected to evaluate to an index into that sequence. Default indexing is from 1." Table 7 (§8.2.5.8.2): "`# | BaseFunctions::'#' | Indexing`".

Value semantics, not feature identity — §7.4.9.3 (Feature chain expression): "The referenced feature is evaluated in the context of each of the result values of the primary expression, in order. The resulting feature values are then collected into a sequence in order of evaluation." So the expression yields values; the referent `R` is resolved against the *result parameter* of `plants#(1)` (typed by the `plants` element type `'Probe Plant'`), giving the def-level `R`. This is the value-semantics counterpart deliberately kept distinct from a plain feature chain, which does have feature identity — §7.3.4.6 Note: "A similar dot notation is also used for the related Kernel-layer concept of a feature chain expression … However, it is always syntactically unambiguous as to whether the notation should be parsed as a plain feature chain or as a feature chain expression"; and §7.3.4.6: a feature chain "is a separate feature." A plain feature chain cannot have an index segment (each segment "must resolve to a feature," §7.3.4.6), so `plants#(1).R` can only be the expression form.

RESIDUAL AMBIGUITY: Low on the parse and on the def-level `R` target. The load-bearing point for a source-identity use is unambiguous in the spec's favor: `#(1)` produces a value, so `plants#(1).R` has no stable feature-path identity distinguishing occurrence 1 from occurrence 2 — the identity content is just the def-level feature `R`.

---

**Q5 — FORM 5 `plants[1]` bracket**

VERDICT: Confirmed — `expr[expr]` is the bracket operator `BaseFunctions::'['`, which KerML leaves undefined (SysML overloads it for measurement/quantity-with-unit). It is NOT sequence indexing; sequence indexing is `#(…)`.

§8.2.5.8.2: "`BracketExpression : OperatorExpression = ownedRelationship += PrimaryArgumentMember operator = '[' ownedRelationship += SequenceExpressionListMember ']'`". Table 7: "`[ | BaseFunctions::'[' | Undefined | No`". Note 2 (§8.2.5.8.2): "The grammar allows a bracket syntax `[ ... ]` that parses to an invocation of the library Function `BaseFunctions::'['` … no default definition is provided in the Kernel Functions Library. If no domain-specific definition is available, a tool should give a warning if this operator is used." Indexing is separately and specifically the `#` operator (Q4 citations). The observed "No Feature named 'R'" follows because `plants[1]` invokes the overloaded bracket (measurement) function whose result type has no member `R`, so the trailing `.R` chain segment fails to resolve — consistent with the bracket having a non-indexing, domain-supplied meaning.

RESIDUAL AMBIGUITY: None at the KerML level — the operator is explicitly "Undefined" in the Kernel library. What `[` *means* is entirely delegated to a downstream library (SysML's quantity/unit definition), so the specific error is tool/library-determined, not KerML-normative.

---

**Q6 — Is the FORM-1 self-binding ever non-degenerate?**

VERDICT: Normatively a degenerate/no-op self-reference. It does not bind to the enclosing `'Probe Plant'::R`; the parameter shadows it, and the resulting binding connector asserts a tautology.

Grounds:

`=` on a feature creates a binding connector asserting equivalence — §7.4.11: "Features that have a feature value relationship of this form implicitly have a nested binding connector … between the feature and the result of the value expression." And: "The semantics of binding mean that such a feature value asserts that a feature is equivalent to the result of the value expression." With the RHS resolving to the same parameter (Q1), the assertion is `R == R` — always satisfied, contributing no value.

No mechanism reaches the outer feature — the only ways to name `'Probe Plant'::R` from inside the calc are a qualified name (FORM 2, §8.2.3.5.1 step 3) or a feature chain through a bearer (FORM 3). Bare `R` is captured by the nearest-scope parameter (Q1). There is no spec provision by which a bare self-named value expression binds to a shadowed inherited/outer feature; §7.3.4.5's redefinition carve-out (which *would* skip the local namespace) applies only to redefined-feature targets, not to value expressions.

RESIDUAL AMBIGUITY: Low. The one thing the spec does not do is *forbid* the self-binding or flag it — §7.4.11 and §8.2.3.5 permit it and give it well-defined (tautological) semantics. So it is legal but inert: a modeler intending "bind my parameter to the part's attribute" gets a self-binding instead, with no normative diagnostic required.

---

Spec files used: `/home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_KerMLSpec/full_document.md` (name resolution §8.2.3.5 lines 3083-3170; feature values §7.4.11 lines 2632-2681 and concrete syntax §8.2.5.10 line 3526; expressions §7.4.9 lines 2300-2569; primary-expression grammar + Tables 5/6/7 §8.2.5.8 lines 3364-3478; redefinition §7.3.4.5 lines 1655-1693; feature chaining §7.3.4.6 lines 1695-1727).
