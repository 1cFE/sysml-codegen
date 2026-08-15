# Spec: Exact-Identity Completion (ELABORATE-FIRST Item 6)

**Status:** Certified — independent re-audit 2026-08-10 (`audit_v3.md` addendum); all seven
success criteria verified
**Owner:** Reid W
**Created:** 2026-08-09 15:59:37 PDT
**Complexity:** HIGH
**Branch:** `source-identity-epic`

---

## Problem

**[OWNER] (2026-08-08)** SysIDE has already resolved which semantic element a reference denotes.
Codegen must use that exact identity rather than replace it with a non-unique name and reconstruct
the target later. Item 5 proved that consumer edges meet this obligation, but the new route is not
yet safe to become authoritative: calculation payload and compilation attach by definition QN,
port metadata attaches by member name, and constraint profile decisions attach by usage QN. Misses
can silently become `UNKNOWN`, `float`, null metadata, or `ADMIT`. Projection also recovers owner
and dependency structure from strings it rendered itself. Switching the route in that state would
move the original defect pattern across the cutover boundary instead of removing it.

## Success Criteria

- [x] **[INHERITED]** Calculation data, compilation, input/output metadata, and constraint decisions
  attach to their exact declarations. Renaming, normalized-name collision, duplicate QN, and
  enumeration order cannot change the selected executable payload.
- [x] **[INFERRED]** Missing, duplicate, mismatched, anonymous, or invalid-vocabulary executable
  payload has one explicit tested outcome. No required payload silently defaults or admits
  execution. *(audit-F7 fix verified by the 2026-08-10 re-audit, `audit_v3.md` addendum: every
  profile `BLOCK` yields the named `SI_CONSTRAINT_BLOCKED` halt before generation on strict,
  lenient, and round-tripped routes.)*
- [x] **[INHERITED]** SysIDE's effective usage declarations and codegen's concrete occurrence
  contexts have one proven ownership boundary across inheritance, retyping, explicit/implied
  redefinition, and finite multiplicity. *(Verified by the Phases 3–4 audit, `audit_v2.md`
  2026-08-09.)*
- [x] **[INHERITED]** The validated instance graph contains enough typed structure for projection
  to derive public ownership, aliases, expression/predicate inputs, and execution order without
  parsing rendered display paths, module names, or channels.
- [x] **[INHERITED]** The full semantic-resolution boundary is protected against
  name/QN/rendered-path selectors, and the two plural fallback branches have a kept valid-model
  disposition. *(audit-F9 fix verified by the 2026-08-10 re-audit, `audit_v3.md` addendum: the
  guard is deny-by-default over every function in all six boundary files, with five named,
  mechanically exercised wire-decoding/rendering exemptions.)*
- [x] **[INHERITED]** The inherited 29-cell matrix and 37-fixture dual-run corpus remain
  green-or-named-diagnostic with zero unclassified rows. The shipped legacy route and v5 snapshot
  bytes remain unchanged.
- [x] **[INHERITED]** For every supported matrix cell with a runtime source, an off-default value
  projected through the internal exact route reaches every and only its bound calculation,
  constraint, FORMULA, alias, and aggregation consumers at the public generation boundary. Item 7
  retains the final shipped live-and-relocated-snapshot mutation proof.

## Known Requirements

- **[NEED] R1 — A separate pre-cutover item.** Exact-identity completion is Item 6 and finishes
  before Item 7 may switch authority. The owner requested the insertion on 2026-08-09.
- **[INHERITED] R2 — Exact identity covers executable lookup.** Names, qualified names, owner/name
  pairs, rendered paths, sanitized spellings, source locations, current values, and enumeration
  order may not perform semantic equality or select executable payload. Missing required identity
  fails closed (`.project/active/elaborator-design/spec.md`, R9).
- **[INHERITED] R3 — Payload attachment becomes exact.** Calculation definitions, compilation,
  exact formals/outputs, and constraint usage decisions require ID-bearing associations; current
  QN/name fallbacks are pre-cutover defects
  (`.project/research/20260809-153245_item6-identity-completion-and-cutover-census.md`, Finding 1).
- **[HARD] R4 — SysIDE supplies declarations, not concrete contexts.** On supported SysIDE 0.8.4,
  `Usage.usages` supplies effective semantic declarations but no native API distinguishes every
  concrete parent and multiplicity index. Codegen must retain finite concrete expansion while
  consuming SysIDE's declaration authority
  (`.project/active/spike-syside-occurrence-authority/findings.md`).
- **[INHERITED] R5 — Projection is one-way.** Public strings may be rendered only after semantic
  identity is settled. Execution order comes from direct producer edges, and the graph carries
  structured occurrences and neutral expression IR
  (`.project/active/elaborator-design/design.md`, D8–D9).
- **[INFERRED] R6 — Graph validation covers executable payload.** A projectable graph has total,
  internally consistent names/metadata for required ports and outputs, valid compilation state,
  and a closed constraint-eligibility vocabulary. Snapshot decoding may not repair an invalid graph
  with defaults.
- **[INHERITED] R7 — Fail closed, never first match.** Missing or ambiguous identity, invalid slot
  families, dangling payload/edges, and unsupported plural scope block with a named diagnostic.
  Traversal order is not a tiebreaker (`.project/active/elaborator-design/design.md`, D6 and D10).
- **[INHERITED] R8 — The whole boundary is guarded.** The audit-F30 protection expands beyond
  `_resolve_leaf`; audit-F31 receives a kept model witness that either proves scoped plural behavior
  or proves the branch unreachable and removes it
  (`.project/completed/20260809_elaborator-breadth/audit_v3.md`, addendum).
- **[INHERITED] R9 — Cross-repository authority stays put.** `agentic-mbse` owns live SysIDE
  extraction and its validated element-ID boundary. Codegen owns calculation extraction,
  compilation, elaboration, graph validation, and projection
  (`.project/active/elaborator-design/design.md`, Component Overview).
- **[INHERITED] R10 — No authority switch in this item.** The legacy front end remains the shipped
  black-box route and v5 snapshots remain byte-identical. Item 7 owns the complete route switch,
  new snapshot envelope, recapture, deletion ledger, and harness removal
  (`.project/backlog/epic_elaborate_first_architecture.md`, Items 6–7).

## Non-Goals

- **[INHERITED]** Switching `build_pipeline_context`, changing the shipped snapshot version,
  recapturing the 37 fixtures, deleting legacy mechanisms, or removing the dual-run harness. Item 7
  owns that atomic landing.
- **[INHERITED]** Migrating downstream packages/studies, repairing the assurance record, or
  publishing modeling guidance. Item 8 owns those outcomes.
- **[INHERITED]** Changing generated public naming policy or automatically disambiguating rendering
  collisions.
- **[INHERITED]** Fixing semantic defects inside the legacy route.
- **[INHERITED]** Supporting non-finite multiplicity.

## Resolved During Implementation

- **[INFERRED]** The kept valid-model fixture reaches package-scoped and cross-root
  occurrence-scoped plural selection. Both start from an exact top-level occurrence declaration;
  candidates outside the consumer lineage remain excluded. The disposition and evidence are
  recorded in `plan.md`, Phase 3.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_elaborate_first_architecture.md` (ELABORATE-FIRST Item 6)
- **Required Reading:**
  - `.project/research/20260809-153245_item6-identity-completion-and-cutover-census.md`
  - `.project/active/spike-syside-occurrence-authority/findings.md`
  - `.project/active/elaborator-design/spec.md`
  - `.project/active/elaborator-design/design.md`
- **Governing contract:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:287-368`
- **Item-5 certification:**
  `.project/completed/20260809_elaborator-breadth/audit_v3.md`
- **Item-5 corpus ledger:**
  `.project/completed/20260809_elaborator-breadth/diff-ledger.md`
- **Design:** `.project/active/elaborator-design/design.md` (owner-approved shared design)
- **Product lens:** `.project/active/elaborator-identity-completion/product-lens.md`

---

**Next Steps:** Request an independent re-audit of audit-F7 through audit-F9. Item 7 remains blocked
until Item 6 is certified.
