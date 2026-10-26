# Product lens: named-subset-members

Append-only ledger.

## spec — 2026-10-26 — rev 2a6609a6 (named-subset-members), .project/active/named-subset-members/spec.md

Point (re-derived): The generator rebuilds the math the model actually states under KerML/SysML v2 as SysIDE parses it. Each modeled member becomes exactly one concrete copy, or the generator refuses by name. It never emits a confident wrong number. Applied here: a named subset (`server_1 :> servers`) is one of the declared members of `servers`. A read of the whole collection counts it once and counts the unnamed copies once each. The declared count holds. [source: .project/product/0004-product-identity-parse-walk-emit.md, .project/product/0003-no-workarounds-for-bad-models.md, .project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md (active, [OWNER]), owner option A 2026-10-26, grade: owner/HARD]

Falsifier: s2 (`servers : Server[2]`, named `server_1` 15 and `server_2` 20) builds more than two servers, or `sum(servers.power)` is anything other than 35. Or a model of a shape the spec does not list builds a count that differs from the model's, with no refusal.

Findings:

- spec-F1 [DO] The premise-conflict decision was written per fixture and did not cover the shape behind it (named subsets with a redefinition that does not restate its count). — ADR 0004 / P-003 (owner/HARD obligation; gap is [AGENT] inference) — disposition: DISPOSED. The spec's [AGENT] decision now states the rule for the shape and requires a case beyond the two fixtures.
- spec-F2 [DO] Shipped agentic-mbse guidance warns against `sum()` over a collection with named members; it becomes false after the fix. — ADR 0007 seam, P-004 ([AGENT] inference) — disposition: DISPOSED. Success criterion added: correct the guidance or file a cross-repo follow-up before close.
- spec-F3 [DO] Some new refusals reject valid KerML (subset of a subset; named subset with its own count) and are not recorded as user-visible limits. — P-003 (owner) / ADR 0004 ([AGENT] inference on scope) — disposition: DISPOSED. Success criterion added: record them in `docs/architecture/modeling-assumptions.md`.

Smells: none fired.

Gate: DISPOSED (spec-F1, spec-F2, spec-F3)

Not checked by the lens: shape models, fixtures, `corpus-receipt.md`, backlog rows; current-output claims checked against the investigation report only. (The spec author checked the fixture models and stored answers.)
