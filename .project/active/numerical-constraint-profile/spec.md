# Spec: Numerical Constraint Executable Profile

**Status:** Complete  
**Owner:** Reid W  
**Created:** 2026-07-18 08:11 PDT  
**Complexity:** HIGH  
**Branch:** constraint-exec-epic  
**Epic:** CONSTRAINT-EXEC — Item 3 contract correction and remediation follow-on

---

## Problem

The executable constraint profile and the generated runtime promise different value domains.
Profile v2 admits equality over Boolean, string, integer, and enumeration values, while generated
constraint inputs, defaults, observations, and evidence are float-shaped. Some admitted predicates
therefore fail generation or execution, and others lose their original type or integer precision.

This broader profile also misses the owner's intended use. Constraint execution is for numerical
validity evaluation: a value is calculated from input characteristics, then checked to determine
whether it is valid. A non-numerical statement may still be useful to its author, but it is outside
this executor's purpose. The current codegen preflight treats an asserted statement outside the
executable profile as a generation halt. That prevents authors from retaining valid SysML
statements for other tools or purposes.

The contract must define one honest numerical executable subset and a three-way outcome rule. A
numerical claim the profile admits must execute. A numerical claim the profile cannot prove
correct — unsafe units, an unresolvable operand, equality without faithful semantics — is
malformed and fails generation, as it does today. A non-numerical statement remains visible,
produces warnings in both model-building checks and code generation, and never prevents
generation.

## Success Criteria

- [x] Every assertion admitted by the numerical profile compiles and executes through a generated
      package without changing its numerical meaning.
- [x] The admitted matrix covers numerical ordering, supported arithmetic, Boolean composition of
      numerical predicates, assertion negation, and quantity comparisons whose existing unit rules
      prove execution safe.
- [x] Equality never reaches predicate compilation as an admitted shape, with the outcome split by
      operand category: Boolean, string, and enumeration equality are non-numerical statements
      (warned, never executed); real, quantity, and integer equality are malformed numerical claims
      (generation errors naming the statement and its rewrite). `!=` follows the same
      operand-category rule.
- [x] A non-numerical asserted statement produces a source-specific warning — one warning per
      offending statement, naming its source location — during agentic-mbse model checks and during
      code generation. Code generation continues.
- [x] A malformed numerical claim — an ordering or arithmetic predicate with unprovable or unsafe
      units, an unresolvable operand, numerical equality, or an unsupported construct such as a
      feature chain or invocation inside it — remains a generation error naming the statement, the
      construct, and the fix.
- [x] A statement excluded only because it is outside the numerical execution purpose remains
      represented in the facts/snapshot and in a visible downstream inspection surface; it is not
      executed or silently discarded.
- [x] Malformed facts, unresolved executable inputs, unsafe unit relationships, and other failures
      that prevent trustworthy numerical evaluation remain distinguishable from valid statements
      that are merely outside this executor's scope.
- [x] Existing admitted numerical constraint fixtures retain their verdicts, margins, generated
      execution behavior, and live/snapshot parity.
- [x] The revised profile has an explicit semantic-version boundary, and sysml-codegen proves
      compatibility against the exact companion revision that defines it.

## Known Requirements

- **[NEED]** Constraint execution serves numerical evaluation: a value is a function of input
  characteristics, and the constraint checks that the resulting value is valid. Owner statement,
  2026-07-18.
- **[NEED]** Authors may add non-numerical statements for their own purposes without those
  statements preventing code generation; those statements warn rather than error. Owner statement,
  2026-07-18.
- **[NEED]** A numerical claim that is not correctly formed — one the profile cannot prove safe to
  execute — raises a generation error rather than degrading to a warning. Owner statement,
  2026-07-18 (spec review, L3-1/L3-2 resolution).
- **[INHERITED]** The non-numerical warnings surface in both agentic-mbse model-building checks
  and sysml-codegen generation — the two seams where the executable profile already runs. Source:
  concept executable-profile paragraph (the profile runs at design review and at codegen
  preflight); the warn-and-continue outcome itself is owner-stated, 2026-07-18.
- **[HARD]** Profile admission must be a total contract for the downstream compiler. The compiler
  strips unit annotations and generated constraint values are float-shaped, so a predicate whose
  numerical meaning cannot be preserved must not be admitted. The float data path itself is
  settled: the owner ratified preserving the generated numerical data model (remediation design
  addendum D5, 2026-07-18). The numerical domain is therefore IEEE double — "preserving numerical
  meaning" means float semantics, which keeps integer ordering admissible and excludes
  exact-integer equality. Evidence:
  `.project/active/constraint-exec-code-quality-remediation/audit.md` findings 1–2.
- **[HARD]** Changing which expressions `PROFILE_SEMANTIC_VERSION` admits is a semantic contract
  change. Consumers must be able to distinguish the revised behavior from executable-profile v2;
  the fact-schema version alone does not identify that change. Existing contract:
  `../agentic-mbse/.project/completed/20260713_executable-profile/design.md`, D8.
- **[INFERRED]** The numerical executable subset admits `<`, `<=`, `>`, and `>=`; supported
  arithmetic in operand position; `and`, `or`, and `not`; negated assertion polarity; and
  compatible quantity ordering under the existing exact-unit policy. This was recommended by the
  agent and ratified by the owner on 2026-07-18.
- **[INFERRED]** Exact equality is excluded for every current value category, with the outcome
  split by operand category: Boolean, string, and enumeration equality are non-numerical (warn);
  real, quantity, and integer equality are malformed numerical claims (generation error). Real and
  quantity equality lack modeled tolerance semantics; integer equality cannot preserve exact
  semantics through the float data path. `!=` follows the same rule. Recommended by the agent and
  ratified by the owner, 2026-07-18 (spec review, L3-1a).
- **[INFERRED]** Numerical intent is classified structurally: a predicate whose root is an
  ordering comparison or arithmetic is a numerical claim regardless of whether its operand
  categories are recoverable, so an unsupported construct inside it (feature chain, invocation,
  unresolved operand) makes the claim malformed (error), while `xor`/`implies` and equality over
  Boolean/string/enumeration operands are non-numerical (warn). Recommended by the agent and
  ratified by the owner, 2026-07-18 (spec review, L3-1b); the exact classifier mechanics are a
  design decision.
- **[INFERRED]** A valid non-numerical asserted statement is a non-executable warning, not a
  modeling error. It follows the owner's requirement that such a statement remain usable for
  another purpose. The exact internal classification vocabulary is a design decision.
- **[INHERITED]** Unit-sensitive numerical operations execute only when authoritative operand facts
  prove compatible exact units; required conversion, incompatible dimensions, or unknown exact
  units do not execute. Source:
  `../agentic-mbse/.project/completed/20260711_spike-constraint-fact-shapes/findings.md`, §5.
- **[INHERITED]** False supported predicates remain successful evaluations that return evidence;
  they are not execution failures. Source:
  `.project/concepts/constraint-execution-and-design-space-studies-claude.md`, Design Principle 4.
## Non-Goals

- Generalizing generated inputs, defaults, observations, or evidence to Boolean, string,
  enumeration, or exact-integer runtime values.
- Executing non-numerical assertions in the first scope.
- Inventing tolerance semantics for real or quantity equality.
- Treating warnings as proof that an unsupported statement was enforced.
- Temporal constraint monitoring, requirement satisfaction execution, optimizer policy, or changes
  to false/violated numerical verdict semantics.
- Reworking formal-target binding, inline owner-reference wiring, occurrence ordering, model
  lifetime invariants, or package-verification hardening from the parent remediation.

## Open Questions / Deferred to design

- What vocabulary and diagnostic labels express the settled three-way rule (execute / malformed
  numerical claim errors / non-numerical warns) without overloading the existing `BLOCK` label,
  and what are the exact classifier mechanics for structural numerical intent (spec review,
  L3-1b)?
- Which downstream inspection surface carries a valid non-executable assertion so codegen can warn
  without silently dropping it: the existing unassessed record path, the generated catalog, or
  another existing carrier?
- How should duplicate warnings be reconciled when agentic-mbse checks and codegen run in the same
  workflow, while still guaranteeing that either tool used alone reports the statement?
- What exact profile semantic-version identifier and coordinated dependency pin express the
  corrected contract?

---

## Related Artifacts

- **Epic:** `.project/completed/20260713_epic_constraint_execution.md`, Item 3
- **Required Reading:**
  - `.project/concepts/constraint-execution-and-design-space-studies-claude.md`, executable-profile
    paragraph and Required Invariants
  - `../agentic-mbse/.project/completed/20260711_spike-constraint-fact-shapes/findings.md`, S1 type/
    unit evidence and equality matrix
  - `.project/active/spike-expression-tree-parity/findings.md`, S2 operator matrix and compiler
    boundary evidence
- **Prior profile contract:**
  `../agentic-mbse/.project/completed/20260713_executable-profile/{spec,design}.md`
- **Spec review:** `.project/active/numerical-constraint-profile/spec-review.md` (Revise verdict;
  all findings resolved with the owner and incorporated 2026-07-18)
- **Triggering audit:** `.project/active/constraint-exec-code-quality-remediation/audit.md`
- **Remediation design addendum:**
  `.project/active/constraint-exec-code-quality-remediation/design.md`
- **Research:** `.project/research/20260710-095634_constraint-execution-and-design-space-exploration.md`
- **Design:** `.project/active/numerical-constraint-profile/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `my-design`.
