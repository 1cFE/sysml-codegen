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

## design_review — 2026-10-26 — rev 90c01150 (named-subset-members), .project/active/named-subset-members/design.md

Copied from `design-review.md` (Product Lens block) by the design session in round 2; dispositions added against the round-2 design and prototype.

Point (re-derived): The generator reproduces the members and count the model states, read from parser evidence (KerML 7.3.4.4: a subsetting part's values are values of the collection). A read of the whole collection reaches every modeled member exactly once, each with its own values. Any shape it cannot derive exactly is refused by name; it never builds a confident wrong number. [source: .project/adr/0004 ([OWNER], active); .project/product/0003 and 0004 ([OWNER-VERBATIM]: "we follow what KerML, SysMLv2 and SysIDE support"); option A in spec.md:22, grade: owner/HARD]

Falsifier: A valid model whose collection has a named subset generates without refusal, and sum() over the collection differs from the KerML value, or the built members do not equal its count.

Findings:

- design_review-F1 [DON'T] D6 refused a non-sibling named subset only if the collection stated a multiplicity, so with D4 a member of an inherited-count collection was built as an extra part left out of the sum (p12: 20.0, KerML 25). — ADR 0004 [OWNER] / P-003, P-004 (owner/HARD) — disposition: DISPOSED. Round-2 D6 refuses every non-sibling named member, whatever the count; p12 is refused `occurrence_named_member_not_sibling` on the round-2 prototype.
- design_review-F2 [DON'T] D6 built a count-1 non-sibling member beside its target. — P-003 by inference (AGENT) — disposition: DISPOSED. Same D6 rule: p6 and p6b refuse. Cost recorded in the design: the four `candidate-es-009` cases refuse (two of them generated before).
- design_review-F3 [DO] D7 relied on SysIDE's usages view. — ADR 0004 obligation; remedy inferred (AGENT) — disposition: DISPOSED. Round-2 D7 reads what the collection's declaration and the declarations it redefines own; p5 and p5b refuse `occurrence_named_member_collection_owns_features`; the `KeyError` skip is gone.
- design_review-F4 [DO] Option A was graded [OWNER]. — capture-fidelity settled rule — disposition: DISPOSED. Regraded `[AGENT] recommended, ratified by owner 2026-10-26` in spec.md:22 and the design.
- (Reviewer addition) M1, a redefined named member dropping out of its collection (p10, p10b: 20.0, KerML 25). — same grade as F1 — disposition: DISPOSED. Membership is keyed by slot (D1); p10 and p10b give 25.0 in real TEAx.

Smells: none fired.

Gate: DISPOSED (design_review-F1, F2, F3, F4, M1)

Not checked by the lens: native SysIDE values for the probes; slow tests.
