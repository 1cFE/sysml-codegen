# Audit: Semantic Identity and Occurrence Foundation — Phases 1–2

**Verdict:** Needs Work
**Audited:** 2026-08-07
**Branch:** `source-identity-epic`
**Commit:** `224bfa6` (dirty worktree)

---

## The Point

One semantic source occurrence must become exactly one runtime source across all calculation,
constraint, and aggregation consumers. An externally supplied value gets one public input, and a
computed value gets one producer channel. The identity must come from the modeled declaration and
concrete occurrence before consumer resolution. It must not come from a consumer owner, parameter
name, written leaf, rendered path, or current value.

## Summary

Phases 1–2 add substantial extraction evidence, occurrence queries, immutable identity types, and
strong live tests. They do not yet establish the claimed foundation. The C24 aggregation route loses
the chain root and cannot identify the same computed source as the calculation route, which leaves an
owner-grade product-lens block. Identity also depends on diagnostic authored spelling, and aggregation
scoping still synchronizes legacy path strings with structured occurrences.

## Product Judgment

This is the right piece of work, but the current implementation does not yet do the piece faithfully.
The product-lens ledger is **BLOCKED** by `audit-phase1-2-F1`: a live C24 probe gives the calculation
consumer the identity of `producer_calc.result`, then raises `SI_OCCURRENCE_MISSING` for the
aggregation consumer of that same source. No earlier ledger block contains an unresolved block; this
new owner-grade finding controls the verdict.

Three structural smells fired and remain unresolved:

- **Smell 1 — two representations must be manually synchronized.** Aggregation scoping joins the
  legacy dotted-path result to `InstanceOccurrence.instance_path` by rendered string.
- **Smell 4 — correctness depends on downstream knowledge of an internal representation.** The
  string join and diagnostic `authored_segments` both affect semantic identity.
- **Smell 6 — a test selects the passing route.** C24 is tested on calculation extraction, while
  calc/aggregation convergence is tested on C11; the untested C24 aggregation leg fails live.

Ledger: `product-lens.md`, block `audit-phase1-2 — 2026-08-07`.

## Findings

### Plan completion

- **Phase 1 is not verified.** The aggregation path retains the resolved leaf but drops the resolved
  chain root when the neutral node becomes a term
  (`../agentic-mbse/src/agentic_mbse/sysml/aggregation.py:247`,
  `src/sysml_codegen/extraction/hierarchy_resolver.py:310`). That makes the C24 source occurrence
  underivable without returning to a name/path. Carry the exact structural chain evidence through
  the term record and prove the C24 aggregation leg uses it.
- **Phase 1 expression readiness is incomplete.** An `InvocationExpression` takes the unhandled arm,
  becomes `UNBOUND`, and receives no immutable evidence
  (`src/sysml_codegen/extraction/usage_extractor.py:888`). Readiness then skips bindings without
  evidence (`src/sysml_codegen/analysis/source_identity.py:689`). Preserve an explicit expression
  disposition for every unsupported expression shape so none becomes a public entry point by
  omission.
- **Phase 2 is not verified.** The evidence-to-demand constructor builds `member_path` from
  diagnostic-only `authored_segments`
  (`src/sysml_codegen/analysis/source_identity.py:596`,
  `src/sysml_codegen/extraction/source_evidence.py:73`). A probe with identical resolved facts and
  two authored spellings produced different identities. Construct member paths from resolved
  structural evidence and test through `demand_from_binding()`.
- **Phase 2 structured scoping is not complete.** The implementation starts from the legacy path
  finder, reconstructs an underscore path, and joins it to the authority by display string
  (`src/sysml_codegen/orchestration/pipeline_builder.py:714`). The equivalence test runs both sides
  from that same legacy eligible set (`tests/conformance/test_aggregation_scoping.py:742`). Have the
  authority supply structured eligible occurrences; keep the legacy helper only as an independent
  comparison oracle.

### Spec conformance

- **SC1:** Not met in this scope. Live extraction preserves much of the referent evidence, but C24
  cannot reach one exact identity across calculation and aggregation; snapshot transport was not
  checked.
- **SC2:** Not met. `authored_segments` changes identity, and a definition-level projection with no
  consumer anchor can pass by global uniqueness (`src/sysml_codegen/analysis/source_identity.py:486`,
  `tests/unit/test_source_identity.py:161`).
- **SC3:** Not checked; C19 value application belongs to Phase 3.
- **SC4:** Partial. C8 distinctness and C9/C10 ambiguity pass on direct authority calls, but the
  complete evidence-to-demand/manifest route is not proven.
- **SC5:** Not met. C24 is a required Item-4 coordinate and fails on its aggregation leg. C18 is a
  documented SysIDE load refusal rather than the published live policy outcome.
- **SC6:** Not checked; snapshot v6 and the 37-file recapture belong to Phase 4.
- **SC7:** Partial. No new walker algorithm was added, but aggregation scoping still depends on the
  legacy path representation beside the occurrence authority.
- **SC8:** Not met yet. Phase 1 logs readiness findings but continues into registry construction,
  and invocation expressions bypass readiness entirely. Upstream diagnostics belong to Phase 5.
- **SC9:** Not checked; recapture review belongs to Phase 4.
- **SC10:** Partial. Cycles, non-finite cardinality, shadowing, specialization, and focused gates
  pass; relocated replay was not part of this audit.

Tagged requirements:

- **SIF-01 `[NEED]`: Not met.** C24 cannot give all consumers one source identity.
- **SIF-02 `[INHERITED]`: Not met.** Written diagnostic segments participate in identity.
- **SIF-03 `[HARD]`: Not met.** Exact leaf referents are retained, but the aggregation chain root is
  dropped and redefinition support is optional duck typing
  (`src/sysml_codegen/analysis/source_identity.py:553`). Require the redefinition lookup contract
  and fail loudly if it is unavailable.
- **SIF-04 `[INHERITED]`: Partial.** Reference-derived versus authored literals remain distinct on
  tested live routes; complete value-site/manifest joining is not integrated.
- **SIF-05 `[INHERITED]`: Not met.** A missing consumer context can fall back to global `len == 1`,
  the exact shortcut design D5 rejected. Require concrete context for definition-level projection.
- **SIF-06 `[INHERITED]`: Not met.** Reverse occurrence queries reuse `PartInstanceIndex`, but
  aggregation scoping still couples that authority to the legacy path finder.
- **SIF-07 `[INHERITED]`: Not checked; Phase 3 owns C19 application.**
- **SIF-08 `[INHERITED]`: Partial.** C8 and atomic cycle/non-finite tests pass; complete manifest
  construction does not.
- **SIF-09–10 `[INHERITED]`: Not checked; Phase 4 owns snapshot transport and parity.**
- **SIF-11 `[INHERITED]`: Not met.** C24 fails and C18 remains an explicitly surfaced premise
  conflict; the Phase-5 exact coordinate map is not present.
- **SIF-12 `[NEED]`, SIF-13 `[INHERITED]`: Not checked; Phase 5 owns upstream diagnostics.**
- **SIF-14 `[INHERITED]`: Not met.** Codegen warns and continues, and invocation expressions bypass
  the readiness screen.
- **SIF-15 `[INHERITED]`: Not met.** The tests do not exercise the failing C24 mixed-consumer
  identity through one manifest route.
- **SIF-16 `[INFERRED]`: Not checked; it is an Item-4 completion/landing constraint.**

The non-goals were respected. The resolver/materialization cutover, public topology repair, package
mutation proof, study work, and modeling guide were not pulled into phases 1–2.

### Design conformance

- D1/D3 and I1/I3 are violated where authored segment spelling becomes occurrence identity
  (`src/sysml_codegen/analysis/source_identity.py:596`).
- D2/D4 are only partial. The immutable manifest and recorder APIs exist, but the required C24
  record set cannot be finalized and production does not yet publish the manifest.
- D5 is violated by the optional `consumer_anchor=None` global-uniqueness path
  (`src/sysml_codegen/analysis/source_identity.py:459`).
- D8/I6 are only partial. Named occurrence failures are loud, but unsupported invocation bindings
  become ordinary unbound inputs and readiness warnings do not halt.
- I5 is not met for aggregation scoping because eligibility and attachment still cross a rendered
  string join (`src/sysml_codegen/orchestration/pipeline_builder.py:714`).

### Code integrity

- `SourceIdentityAuthority` accepts an index whose protocol omits `redefining_target_on`, then
  silently treats the lookup as optional (`src/sysml_codegen/analysis/source_identity.py:397`,
  `:553`). All current authority indexes implement the method, so this is an unnecessary
  compatibility fallback that can silently publish a base declaration. Make redefinition lookup a
  required authority contract and fail on an unavailable capability.
- `ScopedAggregationData.occurrence` and the three `source_authority` parameters are optional
  compatibility modes (`src/sysml_codegen/extraction/data_models.py:305`,
  `src/sysml_codegen/orchestration/pipeline_builder.py:646`). This makes the same semantic record
  valid with or without structural identity. Remove the bypass from the live identity path; keep any
  legacy comparison isolated to tests or an explicitly separate pre-cutover route.
- A missing bound-formal qualified name becomes an empty string
  (`src/sysml_codegen/extraction/usage_extractor.py:1029`), while a resolved target without a QN
  becomes `None` (`../agentic-mbse/src/agentic_mbse/sysml/expression.py:645`). These invariant
  failures are indistinguishable from ordinary absence. Give them explicit blocking outcomes.

No god function, unrelated parameter-sprawl, broad exception fallback, or new TODO/placeholder was
found in the phase 1–2 implementation.

---

## Certification

No spec success criterion was marked complete. The plan checkboxes contradicted by the reproduced
findings were reopened; passing command/checklist evidence that remains valid was left checked.
`CURRENT_WORK.md` now records phases 1–2 as needs work.

Independent validation performed:

- Focused codegen phase 1–2 selection: **191 passed, 5 skipped**. The five skips are all in the new
  aggregation coverage.
- Full licensed codegen suite: **3189 passed, 52 skipped, 18 deselected**; no
  `no live syside license` skip line.
- Focused sibling evidence tests: **22 passed**.
- Full sibling suite: **1811 passed, 1 skipped, 33 deselected**.
- Scoped Ruff checks passed in both repositories.
- Codegen mypy reproduced the accepted **72-error baseline** with no new source-identity error.
- `git diff --check` passed in both repositories.
- Live C24 reproduction: calculation identity succeeded; aggregation demand raised
  `SI_OCCURRENCE_MISSING`.
- Authored-spelling reproduction: identical resolved evidence with `alias_a` versus `alias_b`
  produced unequal semantic identities.

**Not checked:** Phases 3–5; snapshot-v6 serialization/loading, 37 snapshot recaptures, and relocated
replay; C19 value application; producer-request threading; upstream author diagnostics; final
Appendix-C acceptance map; public topology or off-default mutation; downstream packages and studies.
