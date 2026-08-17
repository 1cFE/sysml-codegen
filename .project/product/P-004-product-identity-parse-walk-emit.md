# P-004 — What this product is: parse the models, walk the AST, reconstruct the math, write it into TEAx Python

**Status:** Standing product definition
**Filed:** 2026-08-16, demo-and-design-search status session
**Grade:** `[OWNER-VERBATIM, 2026-08-16]`
**Source:** owner instruction in the 2026-08-16 status/research working session, given after
reviewing the July fan-out defect and the project's architecture history

---

## The promise — **[OWNER-VERBATIM, 2026-08-16]**

> Here's what I want. I just want you to capture in the product ledger what this product is
> supposed to be:
> - Use a SysMLv2 parser to interpret the models
> - Walk the AST to reconstruct the math
> - Write the math into python using TEAx
>
> and any type of manual fallback or workaround for an unresolved reference is a massive,
> disgusting smell

Reproduced exactly. This is the owner-originated core of this entry; it survives verbatim under
capture-fidelity law 2 and nothing below rewrites it.

---

## What it binds

The product is those three steps. The parser's resolved tree is the interpretation; the walk
reconstructs the math from it; the emission writes that math into TEAx Python. Anything standing
in for one of those steps — a rebuilt proxy of the tree, a positional guess, a harness-injected
value, a per-consumer input stub left behind by a reference that didn't resolve — is not a lesser
variant of the product; it is the smell the owner names. An unresolved reference has two honest
outcomes: resolve it through the parser, or refuse with a diagnostic ([P-003](P-003-no-workarounds-for-bad-models.md)).

Canonical instance of the smell, for the record: the July stellarator package, where dropped
bindings left the same physical quantity as 4–5 separate unwired input keys and the runner
hand-injected three values the generator couldn't wire.

## Related

- [P-003 — No workarounds to accept bad models](P-003-no-workarounds-for-bad-models.md) — the
  refusal side of the same rule, from the same owner stance.
- [P-002 — exact owner anchoring](P-002-exact-owner-anchoring.md) — one modeled occurrence, one
  runtime source: the walk step done right.
