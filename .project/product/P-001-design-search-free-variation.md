# P-001 — A design search where parameters vary freely and viability is assessed

**Status:** Directional intent — partly built, partly filed as a capability bet
**Filed:** 2026-08-14, CONSTRAINT-SEMANTICS Item 7 (first capture)
**Grade:** `[OWNER-VERBATIM, 2026-08-13]` core, with `[INHERITED]` supplement
**Source:** `.project/completed/20260814_constraint-docs-agent-sync/owner-checkpoint-20260813.md:9-13`
**Closes:** Item 3 `audit-F4` ("no home available")

---

## The promise — **[OWNER-VERBATIM, 2026-08-13]**

> The system seeks to enable a design search where:
> - engineering design parameters can be freely varied, and viability and outcomes (like LCOE)
>   can be assessed
> - we differentiate from 1costingFE in that we do not embed the engineering logic:
>   predetermining the free variables and backing into all others

Reproduced exactly from `owner-checkpoint-20260813.md:9-13`. This is the owner-originated core of
this entry. It is payload under capture-fidelity law 2: it survives verbatim, at the owner's
emphasis, and is never reworded, paraphrased, or "improved." Everything below supplements it and
nothing below rewrites it.

---

## The enforcement-side companion — cited beside, not merged

**[OWNER]** Critical Success Factor, CONSTRAINT-SEMANTICS epic
(`.project/backlog/epic_constraint_semantics_contract.md:18-20`):

> A design search can trust the generated feasibility evidence to represent every applicable
> asserted physics gate, while every other authored constraint remains visibly dispositioned.

These are two different statements and they stay apart. The promise above says what the system is
*for*. The Critical Success Factor says what has to be true of the evidence for the promise to mean
anything — a design search that cannot trust its feasibility answers is not a design search, it is a
random walk with a report attached. The CONSTRAINT-SEMANTICS epic built the second one. It did not,
and could not, build the first.

---

## What supplements it

**[INHERITED: `.project/concepts/constraint-execution-and-design-space-studies.md:15`]**
Three responsibilities, kept separate. Calculations compute one candidate design state. Constraints
judge that state. A study varies candidate inputs, records every outcome, and applies user-selected
feasibility and search policy. The separation is what lets a violated physics limit stay visible
without being confused with broken code, and it is what lets manual, agent-led, grid, uncertainty,
and optimization workflows all run against the same model evidence.

**[INHERITED: `.project/concepts/constraint-execution-and-design-space-studies.md:17`]** The layer
split that follows from it: the modeling layer owns meaning, the generated model owns deterministic
evaluation, and the study layer owns exploration and decisions. A parameter is "freely varied" only
if varying it does not require re-authoring the engineering logic — which is why the logic lives in
the model, not in the harness that sweeps it.

**[INHERITED: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`,
"Headline states and coverage truth"]** Feasibility is a coverage claim, not the absence of a
failure. Full satisfaction means every applicable asserted gate was assessed **and** passed. A model
where gates went unassessed reads partial coverage, and the study layer keeps that design point at
the boundary rather than accepting it on a coverage gap. Two totals are kept apart: inventory
totality counts every authored usage of every form; feasibility coverage counts applicable asserted
gates only. Descriptive and requirement-side constraints appear in the inventory and never in the
feasibility denominator.

**[INHERITED: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`,
invariant 1 as amended 2026-08-14]** Every authored constraint has a visible disposition —
`eligible`, `excluded`, or `non_reaching`, each with a reason from that kind's closed set. Nothing a
modeler wrote is silently absent from the record. This is the mechanical form of "visibly
dispositioned" in the Critical Success Factor above.

**[INHERITED: `docs/architecture/modeling-assumptions.md` §9, ADR-009]** The decision record behind
the coverage-truth headline. Grade `[AGENT] (ratified by owner, 2026-08-12)` — ratification does not
make it owner-originated, and it is challengeable by re-deriving against its recorded reasoning.

---

## The tension with the basis rulings — surfaced, not resolved

**This section resolves nothing. It states a known tension in daylight so that a later reader cannot
mistake either side for a settled contradiction.** Carried from
`owner-checkpoint-20260813.md:28-36`, not re-derived here. It is not open for re-resolution by this
entry or by the item that filed it.

The promise's second bullet says the system does not embed engineering logic by predetermining the
free variables and backing into all others. The owner-ratified A5/A6/A7 basis rulings sit next to
that, and in those rulings a derivation **does** fix a parameter basis. Read flat, the two disagree.

The recorded reconciliation, as given:

- The toolchain is **causal by construction**. It computes forward from inputs; it does not solve a
  relation in whichever direction a study asks for.
- **Equality gates over free parameters strangle search** — the owner's own R-POL-4 rationale. An
  equality constraint over a parameter you meant to vary does not judge the design, it deletes the
  degree of freedom.
- Bases are therefore **owner-signed, visible, in-model choices**, not hidden harness configuration.
  The choice of what is fixed is a modeling decision a reader can see and challenge.

**The unbuilt half is filed, not forgotten.** `[ACAUSAL-RELATIONS-CAPABILITY]`
(`.project/backlog/BACKLOG.md:439`, filed at owner direction 2026-08-13): relation-style parametrics
whose solve direction is study-selectable. "Don't force independent vs dependent." That capability
is what would close the gap between the promise's second bullet and the landed behavior. It is an
unowned P3 capability bet, recorded so it does not quietly die.

So: the promise is stated here as **directional intent**. The landed behavior implements it under a
causal toolchain with visible bases. The distance between the two has a name and a backlog id.

---

## Related

- Owner checkpoint (payload source): `.project/completed/20260814_constraint-docs-agent-sync/owner-checkpoint-20260813.md`
- Epic: `.project/backlog/epic_constraint_semantics_contract.md` (CONSTRAINT-SEMANTICS)
- ADR-009, coverage truth and headline semantics: `docs/architecture/modeling-assumptions.md:588`
- Capability bet: `[ACAUSAL-RELATIONS-CAPABILITY]`, `.project/backlog/BACKLOG.md:439`
- audit-F4, the filing this closes: `.project/backlog/epic_constraint_semantics_contract.md:540-543`
