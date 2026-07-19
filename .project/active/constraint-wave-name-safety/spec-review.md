# Spec Review: Generated Constraint Name-Safety Boundary

**Spec:** `.project/active/constraint-wave-name-safety/spec.md`
**Contract:** `/home/reid/.claude/commands/_my_spec.md`
**Review File:** `.project/active/constraint-wave-name-safety/spec-review.md`
**Date:** 2026-07-18

---

## Reality Check

**Concerns.** The spec is about the right work item, and deterministic rejection is a defensible
choice under the epic's agent-graded reject-or-map option. The current code confirms the four named
bindings and the two generated scopes. Design would still be misled in three places: the spec
silently substitutes collision-free controls for one literal epic acceptance clause, it treats two
different name-derivation paths as one undefined "final identifier" operation, and it does not pin
whether rejection must precede every output mutation.

The current focused compiler/emission/integration selection passes 61 tests at `512786c7dfab`, so
the present suite does not catch R-3. The reproduced mechanism remains visible in
`predicate_compiler.py:240-270`, `modules.py:188-238`, and
`constraint_module.py.jinja2:32-42`.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** Rejection is coherent with the epic's policy choice, but not with all of
the epic's literal acceptance wording. Epic Item 2 permits deterministic rejection or mapping
(`epic_constraint_pr_wave_remediation.md:195-203`), while the same item asks the generated modules
for all four reproduced names to import and execute (`:200-201`) and the epic-level criterion joins
"rejects or collision-safely maps" to generated-module execution (`:82-83`). The spec recognizes
the contradiction and substitutes collision-free controls (`spec.md:86-90`), but calls the original
execution request "retained as pre-fix symptom evidence." That is an amendment to an agent-graded
upstream criterion, not retention of the same post-fix criterion. Ask the spec agent to state this
traceability break plainly and require the epic criterion to be read conditionally: rejection is
GREEN through deterministic no-output failure; mapping would be GREEN through execution of the
four names; collision-free controls preserve ordinary execution in either case.

**L1-2 · Direct claim:** The spec's single phrase "final identifiers" hides two different current
code paths. Definition formal names become wrapper inputs through `sanitize_name()`
(`constraint_lowering.py:702-707,982-1000,1231-1237`), while predicate parameters are collected
directly from `FeatureReferenceFact.source_name` and are only checked with
`isidentifier()`/`iskeyword()` (`predicate_compiler.py:202-217,240-256`). No shared final-name
derivation currently exists. `spec.md:66-73` therefore cannot yet tell an implementer whether a
formal-formal collision means two raw definition formals sanitizing to one wrapper name, two emitted
predicate parameters, or disagreement between the predicate and wrapper names. Ask the spec agent
to define these collision domains as outcomes, with repeated references to one model formal kept
distinct from two model formal identities. Do not imply that the current compiler already derives
both names the same way.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** The requested formal-formal diagnostic cannot be implemented at every
proposed boundary with the identity currently available there. `ConcreteConstraintInput` carries
only the derived `formal_name` (`resolution/models.py:268-300`), `PipelineModule.inputs` carry only
`param_name`, and `_leaf_ref_names()` deduplicates equal source-name strings before
`compile_predicate()` returns its argument list (`predicate_compiler.py:202-217`). By the compiler
and wrapper-rendering seams, two raw formal identities that collapsed earlier may be unavailable.
Yet `spec.md:77-80` asks the diagnostic to name every colliding model formal identity available, and
`:70-76` asks one decision to serve both those late seams. Ask the spec agent to say which boundary
must retain or receive raw formal identity, and which diagnostic fields are mandatory at the direct
compiler boundary versus the package-generation boundary. Otherwise design can discover too late
that the requested evidence requires either an earlier lowering guard or a data-model change.

The reserved inventory itself is coherent for the two stated scopes. The predicate binds model
parameters plus local `value` and `status` (`predicate_compiler.py:262-270`); the wrapper binds
`self`, model parameters, and local `verdict` (`constraint_module.py.jinja2:32-42`). Because every
accepted formal is used in both functions, rejecting against the union `{self, verdict, value,
status}` closes the reproduced family without changing accepted names.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** Rejection timing is not pinned tightly enough to produce one testable package
contract. `spec.md:35-37,74-76` requires rejection before colliding constraint Python is written or
treated as generated. A check inside `compile_shared_predicates()` satisfies that wording, but on the
real CLI it runs only during `_generate_modules()` (`cli/__init__.py:333-363`), after overwrite
clearing, directory setup, `primitives.py`, and schemas (`cli/__init__.py:987-1007`). The required
GAP-CLOSE F2 precedent deliberately validates before clearing or any output creation
(`gap-runtime-contract/design.md:55-61,196-201,343-354`), and the current CLI implements that
preflight at `cli/__init__.py:968-980`. Ask the spec agent to choose and state the observable rule:
either the output tree is byte-for-byte untouched on rejection, including an absent target staying
absent, or partial non-constraint output mutation is explicitly allowed. "Before a colliding module
is written" leaves both behaviors conforming.

**L3-2 · Rewrite request:** The completeness outcome is implementable without brittle textual source
parsing, but the deferral currently permits such an implementation. A structured inventory can be
compared with names bound in `ast`-parsed, rendered representative functions; this observes Python
scope semantics and avoids regex or Jinja-template text matching. `spec.md:41-42,81-83` correctly
pins the mutation test: adding or renaming a generated parameter/local must fail the guard. Ask the
spec agent to preserve that outcome while making the design deferral at `:109-111` exclude raw
string/regex parsing of templates or emitted source. The spec need not choose the production
representation or AST helper, but it should prevent a test coupled to whitespace and template
formatting from satisfying the completeness criterion.

The collision-free byte criterion is otherwise strong enough. `spec.md:51-52,84-85` requires all
accepted generated bytes, signatures, wiring, and names to remain unchanged, not merely equivalent
behavior. The satisfied/violated execution controls at `:45-47` independently protect verdict,
status, margin, and observed values.

### Lens 4 — Hygiene

No material hygiene finding.

### Lens 5 — Reader Comprehension

No separate voice finding. The phrases that block an implementation decision are the technical
ambiguities recorded in L1-2 and L3-1, not general prose problems.

---

## Engagement Summary

**Overall take:** Deterministic rejection is a sound, byte-preserving interpretation of the epic's
agent-graded option, and the four-name reserved inventory matches the emitted code. Revise before
design because the current contract does not yet say how rejection satisfies the epic's execution
criterion, what exact final-name collision domains exist, or whether package rejection is a
no-output preflight.

**Here's what I need you to weigh in on:**

1. **[L1-1]** Record rejection as a conditional amendment to the epic's four-name post-fix execution
   wording; use collision-free controls for post-fix execution.
2. **[L1-2, L2-1]** Define wrapper-formal, predicate-parameter, and cross-path collision domains, and
   preserve enough raw identity at the boundary responsible for diagnostics.
3. **[L3-1]** Decide whether a rejected generation leaves the entire target tree untouched. The F2
   precedent and current preflight structure support that stronger rule.
4. **[L3-2]** Keep the completeness mechanism open to design, but exclude regex/string parsing as an
   acceptable guard; use structured scope evidence.

---

## Resolutions

No resolutions recorded. This autonomous stage produced the draft review for the next spec-agent
turn.

---

**Verdict:** Revise
**Next Steps:** Return this review to the spec agent and incorporate the unresolved findings without
editing the spec from the reviewer session. After revision, re-run `my-spec-review` before design.
