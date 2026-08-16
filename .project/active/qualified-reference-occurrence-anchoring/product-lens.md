# Product Lens — qualified-reference-occurrence-anchoring

Append-only ledger. One block per run, per `/home/reid/.codex/scripts/product-lens.md` §3. Gate
consumers scan every block; a finding remains live until a later block resolves it by stable ID.

---

## spec — 2026-08-15 — rev `.project/active/qualified-reference-occurrence-anchoring/spec.md`
Epic: ELABORATE-FIRST

Point (re-derived): A design search must use the resolved semantic referent available at model load
so each concrete source occurrence becomes exactly one runtime source reaching every and only its
bound consumers. For owner-qualified references, usage qualifiers resolve occurrence-level
features; definition qualifiers remain definition-level and bridge only through a unique occurrence
context. [sources: `.project/product/P-001-design-search-free-variation.md` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,67-68,84-86` (owner);
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:618-623`
(agent/ratified)]

Falsifier: From inside `comp_b`, bind a consumer to `comp_a::length`; the obligation is violated if
the edge targets `comp_b.length`, silently chooses any candidate, or an off-default mutation of
`comp_a.length` fails to reach every and only its bound consumers on live and snapshot routes.

Findings:

- spec-F1 [DON'T] The spec marks five code-derived mechanism statements `[HARD]`, including D-6's
  ambiguity/no-guess behavior. D-6 remains `[AGENT] (ratified by owner)`; ratification and current
  code do not upgrade it to `[HARD]`. The exact-owner availability, slot normalization,
  resolver-call surface, and snapshot-shape statements are inherited facts or inferences, not
  external constraints. —
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:584-588,618-623`
  (agent/ratified) — disposition: DISPOSE — preserve the required behavior, but regrade D-6's rule
  as `[INHERITED]`, the owner-selected outcome as `[NEED]`, and code/design facts as `[INHERITED]`
  or `[INFERRED]` before design.

Smells: none.

Gate: DISPOSED (spec-F1)

---

## spec — 2026-08-15 — rev `.project/active/qualified-reference-occurrence-anchoring/spec.md`
Epic: ELABORATE-FIRST (separate bounded child of Item 8; `[INFERRED]`)

Point (re-derived): A design search must use the semantic referent resolved at model load so each
concrete source occurrence becomes exactly one runtime source reaching every and only its bound
consumers. Owner-qualified usage references resolve occurrence-level features; definition-qualified
references remain definition-level and bridge only through a unique occurrence context. [sources:
`.project/product/P-001-design-search-free-variation.md` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,67-68,84-86` (owner);
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:618-623`
(agent/ratified)]

Falsifier: From inside `comp_b`, bind a consumer to `comp_a::length`; the obligation is violated if
the edge targets `comp_b.length`, silently selects another candidate, or an off-default mutation of
`comp_a.length` fails to reach every and only its bound consumers on live and snapshot routes.

Findings:

- None.

Resolves:

- spec-F1: FIXED — authority: agent/ratified — basis: D-6 is now `[INHERITED]`, the owner-selected
  broader outcome is `[NEED]`, and the code/design-derived mechanism statements are `[INHERITED]`
  or `[INFERRED]` with citations; none retains manufactured `[HARD]` authority.

Smells: none.

Gate: CLEAR

---

## spec — 2026-08-15 — rev `.project/active/qualified-reference-occurrence-anchoring/spec.md`
Epic: ELABORATE-FIRST

Point (re-derived): A design search must preserve the semantic referent resolved at model load and
anchor it to the exact concrete occurrence, so one source occurrence reaches every and only its
bound consumers. Usage-owned bare and qualified references retain that occurrence identity;
definition-qualified references bridge only through a unique occurrence context. [sources:
`.project/product/P-001-design-search-free-variation.md` (owner-verbatim);
`.project/backlog/epic_elaborate_first_architecture.md:31-33,67-68,84-86` (owner);
`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:394-409,613-626`
(agent/ratified)]

Falsifier: In a discriminating `comp_a`/`comp_b` topology, a direct reference whose resolved leaf
belongs to `comp_a` targets `comp_b`, guesses among occurrences, or an off-default `comp_a`
mutation fails to reach every and only its calculation, alias/computed, constraint, and aggregation
consumers on live and snapshot routes.

Findings:

- None.

Smells: none.

Gate: CLEAR
