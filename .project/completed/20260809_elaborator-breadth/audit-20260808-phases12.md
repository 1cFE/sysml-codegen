# Audit: Elaborator Breadth — Exact-Identity Phases 1–2

**Verdict:** Partial Certify — Phases 1–2 verified complete; item certification withheld
(product-lens ledger remains BLOCKED by audit-F1/F2/F3, resolvable only at Phase 5)
**Audited:** 2026-08-08
**Branch:** source-identity-epic (coordinated with agentic-mbse `elaborate-first-salvage` @ 65a35d7)
**Commit:** 6bed968 + uncommitted working tree (the audited state)
**Scope:** plan Phases 1–2 only. Phases 3–5 were not evaluated for completion.
**Prior audit:** the superseded rendered-path implementation's audit is preserved at
`audit-20260808-rendered-path.md`.

---

## The Point

SysIDE has already resolved which declaration each semantic reference denotes. Codegen must
preserve that exact declaration identity, interpret it in one exact concrete occurrence, and store
the resulting node or output-port edge — never reduce the referent to a name and later guess which
same-named object was intended. One semantic source occurrence becomes exactly one runtime source
across calculation, constraint, FORMULA, alias, and aggregation consumers; unsupported or unstable
identity produces a named blocking outcome; strings enter only after semantic identity is settled.
Item 5 builds and proves that complete new front end while the legacy front end remains the
unchanged shipped authority.

## Summary

Phases 1–2 deliver what they claim. The kept identity kill probes pin the SysIDE 0.8.4 boundary
(UUIDv5 stability, referent equality, endpoint families, null-QN/relationship-ID exclusion), and
the vertical slice carries exact IDs from the parser through an independent occurrence walker into
typed node/output-port edges, proven under adversarial same-name and reversed-order conditions.
All recorded gates reproduce exactly. The item as a whole is not certifiable: the ledger's
audit-F1/F2/F3 stand by design until the Phase-5 public-mutation observation, and the product lens
filed seven new dispositioned (non-blocking) findings that Phase 3 must absorb.

## Product Judgment

This is the right piece of work in the right order: the two paths that discarded resolved identity
(chain leaf-reanchoring, `sum(...)` name reconstruction) are structurally gone from the new route,
and the plan deliberately proves identity before breadth and projection.

Ledger gate: **BLOCKED**. The 2026-08-08 lens run on this rev returned Gate: DISPOSED for its own
findings (audit-F4..F10, all dispositioned to Phase 3/4/5 or Item 6), but the prior block's
audit-F1/F2/F3 have no resolution block and remain in force. That is expected — the design's
validation approach states only the Phase-5 landed-code public-mutation observation can clear
them — and it forbids item-level Certify today. Nothing in Phases 1–2 contradicts an owner/`[HARD]`
ruling.

Two lens smells fired and are escalated here, not resolved: (1) the `ElaborationCode` enum and the
exception classes name the same failure set in two unsynchronized vocabularies (audit-F6); (2) the
fusion_tea retype test is green while seven references in the same lenient graph carry unasserted
`SI_OCCURRENCE_MISSING` diagnostics (audit-F5; I reproduced the exact multiset: six EXPOSE `scope`
aliases + `chamber.wall_type`). Both are evidence/vocabulary gaps inside Phase 3's declared
fail-closed scope — the elaborator diagnoses rather than guesses — so they are carried as Phase-3
obligations, not Phase-2 defects.

## Findings

### Plan completion

**Phase 1 — verified complete.** All four change items and all validation items check out:

- `tests/conformance/test_elaboration_identity_foundation.py` — 4 tests covering independent
  loads, reversed file order, relocation + harmless edits, referent-ID equality, UUIDv5/UUIDv4
  version boundary, redefinition-endpoint stability with relationship-ID exclusion, and the
  null-QN executable negative on the new `elab_identity_collision_probe` fixture. Ran: 4 passed,
  zero license-skip lines.
- `../agentic-mbse/tests/test_sysml/test_syside_identity_contract.py` — 3 tests (raw
  `element_id`, referent/chain/typing surfaces, authored+implied endpoint stability). Ran: 3
  passed, zero license-skip lines.
- Evidence record appended (kept-test section at the end of
  `.project/research/20260808-103243_syside-identity-and-redefinition-probe-record.md`) without
  rewriting the earlier session-evidence provenance.

**Phase 2 — verified complete.** Every checklist item traced to code:

- Identity boundary: `elaboration/identity.py` — frozen `DeclarationId`/`FeatureSlotId`/
  `OccurrenceId`/`NodeId`/`OutputPortId`/port types with runtime type checks, canonical wire
  round-trip, and the UUIDv5+QN fail-closed gate in `declaration_id_for` (`identity.py:55-71`).
- Independent occurrence authority: `elaboration/occurrence.py` — slot families from
  `redefined_feature`/`redefining_feature` endpoint IDs (relationship IDs excluded,
  `occurrence.py:84-119`), finite-multiplicity block-loud (`occurrence.py:248-271`), containment
  and specialization cycle detection. No legacy walker import.
- Typed graph and one resolver: `graph.py` keys nodes by `NodeId` and ports by
  `ConsumerPortId`/`ExpressionPortId`; `elaborate.py` resolves every form through
  `_resolve_semantic_reference` over exact root/segment/leaf IDs
  (`elaborate.py:615-649`) — no leaf-name search, no rendered-path parsing.
- Exact evidence: `extraction/source_evidence.py` carries `bound_formal_id` +
  `semantic_reference` UUIDs; self-binding is exact ID equality
  (`source_evidence.py:133-144`); `binding_evidence.py` builds facts from
  `SysideAdapter.element_id`.
- Isolation guard: `tests/unit/test_elaboration_import_boundaries.py` bans legacy types,
  `sanitize_name`, `instance_path`, and `next(iter` in the three semantic modules — passes. (See
  audit-F9: the guard does not scan `display.py`; carried to Phase 3.)
- Agentic surface: `SysideAdapter.element_id` is the sole accessor
  (`syside_adapter.py:239-254`), `ResolvedTargetFact`/`ResolvedSemanticReferenceFact` carry exact
  UUIDs, and `pyproject.toml` pins `syside==0.8.4`.
- Existing-test migration: suites query typed identities through
  `tests/helpers/elaboration_graph.py` display helpers at assertion edges; no production
  rendered-path compatibility index exists.
- Legacy freeze: the only `src/` changes are `elaboration/` plus the two evidence modules;
  `analysis/`, `orchestration/`, `resolution/`, and `snapshot/` are untouched, and no snapshot or
  baseline fixture bytes changed.

**Red-first evidence:** accepted as recorded in plan Implementation Notes (collection errors
before the files existed; two named agentic failures before the adapter surface existed). The
working tree is uncommitted, so git cannot independently confirm the sequence; this matches the
plan's own recording convention and is noted in Not checked.

### Spec conformance

Spec success is scoped: R1/R2 breadth, R5 projection, R6 dual-run, and R7 matrix are Phase 3–5
deliverables and were not claimed by Phases 1–2. Verified for the audited scope:

- **R9 (ratified) — met for the covered forms.** Exact parser declaration IDs, structured
  occurrence IDs, typed edge targets; names/QNs confined to display/provenance fields (manual
  graph dump on `source_identity_mixed_consumers`: all node keys, ports, and edges typed;
  `rendered_names_are_metadata_only()` true; zero diagnostics). Self-binding compares declaration
  IDs. Redefinition families key from endpoint IDs, never the relationship object
  (`occurrence.py:92-112`).
- **R3 — met at the screened boundary.** Self/indexed/expression forms produce their contract
  codes and strict elaboration raises the complete aggregated finding set
  (`elaborate.py:935-944`); fusion_tea lenient shows all 15 `SI_SELF_BINDING` findings.
- **R4 — met.** One `AttrNode` per (scope, slot) by construction; equal-valued distinct
  occurrences pinned by the migrated shadowing suite.
- **R2 partial evidence.** C25-style convergence proven: definition-authored and usage-authored
  consumers reach the same `availability` node (`test_elaboration_identity_vertical.py:81-97`).
  The no-minting guarantee at the public surface is unprovable before projection (Phase 4).
- **Non-goals respected.** No snapshot change, no legacy deletion, no shipped flag
  (`elaboration/__init__.py` exports internal construction only).

### Design conformance

- **D1–D5, D7 (edge identity):** implemented as designed for the vertical-slice forms; typing read
  from owned `FeatureTyping` heritage rather than the flattened `types` list is a recorded
  parser-shape adaptation, not a semantic deviation (`elaborate.py:479-495`).
- **D6:** the writer-rank tiers (occurrence exact > occurrence > definition specificity > default,
  with equal-rank ambiguity raising, `elaborate.py:271-290`) are present; full precedence breadth
  is Phase 3. Two residual order-sensitivities to close there: base-attribute selection when no
  occurring root writer exists (`elaborate.py:242-252`) and definition-writer ranking by
  type-closure depth, which silently orders incomparable multiple-inheritance siblings of unequal
  depth (`occurrence.py:317-325`).
- **D10:** partial by plan — three extraction codes plus `SI_OCCURRENCE_MISSING`, `SI_ALIAS_CYCLE`
  (raises, no fallback edge), and dangling-edge validation are live; six catalog codes are
  declared but unwired (lens audit-F4/F6), and ambiguity currently collapses into
  `SI_OCCURRENCE_MISSING` (`elaborate.py:641,957-972`). Phase 3 owns the catalog.
- **Integration strategy:** honored — two complete routes, no shared occurrence types, no legacy
  imports, coordinated cross-repo unit.

### Code integrity

- No TODO/FIXME/placeholder, no broad excepts, no silent fallback edges: alias cycles raise,
  unsupported forms block or record findings, misses leave the port unbound with a diagnostic.
- `_resolve_leaf`'s final global-uniqueness scan (`elaborate.py:769-775`) is the one
  resolve-by-search residue (lens audit-F8, [DON'T], dispositioned): it binds a globally unique
  slot occurrence outside the consumer's lineage instead of naming the condition. Phase 3 must
  either record it as a rule or replace it with the ambiguity diagnostic.
- `sum` plurality is detected by function *name* (`elaborate.py:903-905`); harmless for the slice
  but Phase 3's aggregation work should key off the resolved library declaration to stay inside
  R9's no-name-lookup line.
- Diagnostic vocabulary is split between enum codes and exception classes (lens audit-F6) —
  consolidate in Phase 3's fail-closed pass.

---

## Certification

Verified and left checked: plan Progress boxes for Phases 1 and 2 and every Phase-1/Phase-2
changes-required and validation checkbox. No spec or epic success criterion was marked (none is
met yet — they are Phase 3–5 scope). Appended the 2026-08-08 product-lens block to
`product-lens.md`; the ledger gate remains **BLOCKED** (audit-F1/F2/F3, resolution scheduled at
Phase 5), which withholds item-level Certify by rule.

Gates reproduced on this tree (licensed, zero `no live syside license` skip lines):

- Focused Phase-1/2 gates: **14 passed** (4 foundation + 2 vertical + 4 identity + 3 occurrence +
  1 isolation).
- Elaboration-suite selection: **77 passed**.
- Full codegen: **3230 passed, 47 skipped, 18 deselected**. Full agentic-mbse: **1814 passed,
  1 skipped, 33 deselected**.
- Changed-file `ruff check`: clean. `mypy src/`: 72-error baseline, **0 in `elaboration/`**.
  `git diff --check`: clean in both repos. `uv lock` resolves. No snapshot/baseline byte changes.

**Not checked:** Phase 3–5 deliverables (fail-closed catalog, collision suite, projection,
round-trip, dual-run harness, 29-cell matrix, 37-fixture ledger, public mutation); test-first
chronology beyond the plan's own notes (trees are uncommitted, so git history cannot confirm the
red-first sequence); full-tree ruff/mypy debt beyond the recorded baselines; downstream consumers
of the changed agentic-mbse fact types outside the two suites run here; and live behavior of
fixtures not exercised by the kept suites (only `fusion_tea` and `source_identity_mixed_consumers`
were probed manually).
