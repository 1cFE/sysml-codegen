# Product Ledger

The product's implemented promises and the decision records behind them. One line per entry; the
entry body lives in the sibling file the line links to. A product-lens run resolves against this
file — if a promise is not reachable from here, it has no home.

**Id rule.** `P-NNN`, zero-padded, minted in the order entries are added to this index. Ids are
never reused and never renumbered.

**ADR convention (this repo).** An ADR is a numbered section of
`docs/architecture/modeling-assumptions.md`, titled `## N. Title (ADR-0NN)`. There is no separate
`docs/adr/` directory and this ledger does not become one. ADRs are **back-registered** here as
rows so this file is the single index a lens run resolves against; the ADR text itself never moves.
Next free id: **ADR-010**.

---

## Promises

- [P-001 — A design search where parameters vary freely and viability is assessed](P-001-design-search-free-variation.md) — the owner-stated promise, with the causal-toolchain tension surfaced and its unbuilt half filed as `[ACAUSAL-RELATIONS-CAPABILITY]`

## Decision records (ADRs, back-registered)

- ADR-009 — Coverage Truth and Headline Semantics — `docs/architecture/modeling-assumptions.md:588`. `[AGENT] (ratified by owner, 2026-08-12)`. The enforcement-side record behind [P-001](P-001-design-search-free-variation.md): a headline that cannot tell "checked and passed" from "not checked" is not evidence.

---

**Cited from:** the epic's product-lens block
(`.project/backlog/epic_constraint_semantics_contract.md`, Product-Lens section) — the durable trail
node a lens run for any CONSTRAINT-SEMANTICS item starts from.
