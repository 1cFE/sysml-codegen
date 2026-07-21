# Brief: Item 7 spec review — Constraint Generation

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this spec; review it adversarially.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `spec-review.md` in `.project/active/constraint-generation/`.

## Review target
`.project/active/constraint-generation/spec.md` (brief + [OWNER] gate evidence in this directory).

## Ground truth
Concept ("Catalog, Evaluation, and Report" + Required Invariants + S2/S4 carry-forwards, Appendix B); S4's emitters + findings (`spike-vertical-slice-constraint-execution/`); S2's Kleene findings (probe results in `spike-expression-tree-parity/`); certified upstream code: `analysis/constraint_lowering.py` (ConcreteConstraint incl. predicate_ir as serialized IR string + bound_channel), `resolution/models.py` (ModuleKind), the four kind-dispatched generation seams (Item 6), the teax runtime vocabulary (`~/1cfe/teax/packages/teax-simkit/simkit/evaluation/evidence.py` if readable; else the Item 10 audit's record).

## What to probe hardest
1. **Kleene semantics completeness.** Walk S2's documented truth table + carry-forwards against the spec's requirements: leaf-unknown on non-finite, propagation rules (true-or-unknown=true, false-and-unknown=false), negated-polarity status vs expected value, margin sign under negation, boundary margin zero-no-sign. Anything S2 proved that the spec drops, or overstates (n-ary capacity is latent — no parity evidence)?
2. **The five S4-unexercised cases** (zero-assertion aggregator, indeterminate point, negated + inline at execution, multi-instance, modeled-default formals): does each have a precise requirement + named test shape, or just a list mention? Modeled-default formals: Item 5 emits MODELED_DEFAULT inputs with default_ir — is the runtime semantics of a default (entry point? compiled constant?) actually specified?
3. **Exit-ancestry.** The [HARD] requires guaranteed ancestry: are BOTH candidate mechanisms named with the decision deferred properly, and is the narrowed-exit test specified so it fails under incidental-only ancestry?
4. **The serialization-equality same-IR arm**: Item 7 compiles predicate_ir (a string re-parsed at compile time) — the wiring brief flagged the compiler-side assertion must be serialization-equality. Does the spec require it?
5. **Break-the-YAML test**: specified end-to-end (executor surfaces failure), not constructor-level (S4 carry-forward (2))?
6. **Catalog completeness**: source records + concrete entries + recorded producer binding + unused-defs-as-inventory — consistent with what Item 5's ConcreteConstraint actually carries (check the fields exist)?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code and spikes — do not take the spec's word.
