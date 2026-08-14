# Item 7 owner checkpoint — DISCHARGED 2026-08-13 (pre-captured before item start)

Both owner inputs for Item 7 (epic scope 1) were given in session on 2026-08-13, before Item 9
completed, so the item starts unblocked. Captured here verbatim; Item 7's filing work consumes
this record.

## 1. The coverage-truth product promise — **[OWNER-VERBATIM, 2026-08-13]**

> The system seeks to enable a design search where:
> - engineering design parameters can be freely varied, and viability and outcomes (like LCOE)
>   can be assessed
> - we differentiate from 1costingFE in that we do not embed the engineering logic:
>   predetermining the free variables and backing into all others

Accompanying owner instruction, same session: *"You could probably glean more from the concept
docs that we developed over time."*

**Filing guidance (orchestrator, agent-grade):**

- The two bullets above are the owner-originated core; they go into the first-capture product
  entry verbatim. Material gleaned from the concept docs
  (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` and companions)
  may supplement it, marked `[INHERITED: <source>]` — it never rewrites the verbatim core.
- The epic's `[OWNER]` Critical Success Factor ("A design search can trust the generated
  feasibility evidence to represent every applicable asserted physics gate, while every other
  authored constraint remains visibly dispositioned") is the enforcement-side companion of this
  promise and should be cited beside it, not merged into it.
- **Known tension to handle in daylight, not silently:** the promise's second bullet (no
  embedded engineering logic / no predetermined free variables) sits next to the owner-ratified
  A5/A6/A7 basis rulings, where derivations DO fix a parameter basis. The recorded
  reconciliation: the toolchain is causal by construction; equality gates over free parameters
  strangle search (owner's own R-POL-4 rationale); bases are therefore owner-signed, visible,
  in-model choices — and the aspirational acausal capability is filed as
  `[ACAUSAL-RELATIONS-CAPABILITY]` (BACKLOG, 2026-08-13). The product entry should state the
  promise as directional intent and point at that filing for the unbuilt half, so the promise
  and the landed behavior cannot be read as contradicting silently.

## 2. item3-F2 ruling — option (a) — **[AGENT] (ratified by owner, 2026-08-13)**

The parked BLOCK-clause premise conflict is resolved in favor of the landed behavior: the
lifecycle contract's blanket "a profile BLOCK on an asserted constraint halts generation of the
whole model" clause is **amended to reaching-gates scope** — BLOCK-halts applies to asserted
gates that reach occurrences; a non-reaching asserted usage is governed by severity-by-cause
and the coverage rules (non_reaching, missing assessment, partial coverage), never a
model-wide halt. Rationale as presented and ratified: the non-raising mint, the vacuous-gate
warning grade, and the derivative's held-intent rows all depend on non-reaching-never-halts;
the alternative would flip a vacuous gate from warning to model-killing halt whenever its
predicate happens to contain a BLOCKed construct.

**Execution note:** the contract amendment itself (the clause's wording, with provenance
preserved and the original text recorded per the amendment conventions Item 1 set) is Item 7
sweep work, performed under this ruling. The umbrella spec's parked-conflict record
(item3-F2's home) is updated to RESOLVED-with-citation at the same time.
