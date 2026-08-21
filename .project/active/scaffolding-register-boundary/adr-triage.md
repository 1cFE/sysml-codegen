# Existing Decision Triage

**Date:** 2026-08-21
**Criterion:** `.project/adr/0001-route-decisions-by-who-they-bind.md`
**Scope:** Classify the nine numbered decision sections currently in
`docs/architecture/modeling-assumptions.md`. This record moves none of them.

## Routing rule

Ask who must obey the decision. A decision that binds the person writing the system's inputs stays
with the input-authoring documentation. A decision that binds the person changing the system goes
in `.project/adr/`.

The owner classified Section 7 on 2026-08-21 after reading its binding rule:

> I agree the example you gave “Downstream code never re-derives identifiers” should be in
> .project/adr

`[OWNER-VERBATIM, 2026-08-21]`

## Outcomes

| Existing decision | Who must obey it | Classification | Outcome |
|---|---|---|---|
| §1 / ADR-001 — Library/Design Separation | The model author choosing where declarations and values live | Author-facing | Stay in `docs/architecture/modeling-assumptions.md` |
| §2 / ADR-002 — Input Parameter Classification | The model author choosing which scenario values to expose | Author-facing | Stay in `docs/architecture/modeling-assumptions.md` |
| §3 / ADR-003 — Design Attribute Expression Rules | The model author choosing an admitted expression form | Author-facing | Stay in `docs/architecture/modeling-assumptions.md` |
| §4 / ADR-004 — Aggregation via Redefinition | The model author writing aggregation expressions | Author-facing | Stay in `docs/architecture/modeling-assumptions.md` |
| §5 / ADR-005 — Template Instantiation Convention | The model author instantiating templates and retyping parts | Author-facing | Stay in `docs/architecture/modeling-assumptions.md` |
| §6 / ADR-006 — Arrayed Children Are Enumerated, Not Multiplied | The model author choosing multiplicity and per-occurrence values | Author-facing | Stay in `docs/architecture/modeling-assumptions.md` |
| §7 / ADR-007 — Compute Once, Look Up Thereafter | The system builder implementing identifier creation and reuse | Builder-facing | Re-home to `.project/adr/` in REPO-CLEANUP Item 3 |
| §8 / ADR-008 — Constraints Execute Under a Profile | The model author choosing executable constraint forms | Author-facing | Stay in `docs/architecture/modeling-assumptions.md` |
| §9 / ADR-009 — Coverage Truth and Headline Semantics | The system builder maintaining report tokens, templates, and runtime normalization | Builder-facing | Re-home to `.project/adr/` in REPO-CLEANUP Item 3 |

Item 3 should move both builder-facing decisions and repoint their citations in the same change.

## Product provenance cross-check (I3)

The generated product index intentionally omits provenance. A reader resolves an id to exactly one
`<id>-*.md` entry, then reads that entry's frontmatter and body.

| Product entry | Frontmatter | What its prose says | Agreement |
|---|---|---|---|
| `0001-design-search-free-variation.md` | `[OWNER]` | The summary rests on an owner-verbatim design-search statement; inherited material is labeled separately in the body | Yes |
| `0002-exact-owner-anchoring.md` | `[AGENT] (ratified by owner, 2026-08-16)` | Its Grade line uses the same agent-originated, owner-ratified grade | Yes |
| `0003-no-workarounds-for-bad-models.md` | `[OWNER]` | Its promise and Grade line identify an owner-verbatim standing rule | Yes |
| `0004-product-identity-parse-walk-emit.md` | `[OWNER]` | Its promise and Grade line identify an owner-verbatim product definition | Yes |

No product entry's frontmatter claims more authority than its own prose supplies.
