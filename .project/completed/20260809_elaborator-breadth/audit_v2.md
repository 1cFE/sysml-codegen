# Audit v2: Exact-Identity Elaborator Breadth (ELABORATE-FIRST Item 5, post-remediation)

**Verdict:** Needs Work
**Audited:** 2026-08-09
**Branch:** `source-identity-epic` (codegen) + `elaborate-first-salvage` @ `65a35d7` (agentic-mbse), coordinated dirty trees
**Commit:** `6bed968` (base; work uncommitted)

This audit supersedes nothing by fiat: the 2026-08-09 pre-remediation audit (`audit.md`) is the
historical record of the checkpoint state; this v2 certifies the remediated state. Prior findings
are referenced by their stable IDs from `product-lens.md`.

---

## The Point

SysIDE has already resolved which declaration each semantic reference denotes. Codegen must
preserve that exact declaration identity, interpret it in one exact concrete occurrence, and store
the resulting node or output-port edge — never reduce the referent to a name and later guess which
same-named object was intended. One semantic source occurrence becomes exactly one runtime source
across calculation, constraint, FORMULA, alias, and aggregation consumers; unsupported or unstable
identity produces a named blocking outcome; strings enter only after semantic identity is settled.
Item 5 builds and proves that complete new front end while the legacy front end stays the unchanged
shipped authority; Item 6 owns the cutover. (Sources: epic owner rulings, contract invariants
54–60 + referent table, spec R1–R9.)

## Summary

The remediation is substantial and most of it is genuine: all 29 contract cells now execute real
public evidence with no xfails, finite modeled multiplicity expands, the corpus ledger closed with
zero unresolved rows, and every recorded gate reproduces exactly. But the fix that closed the
usage-qualified-reference finding (audit-F16) was implemented by string-matching authored qualifier
text against rendered display paths inside the exact-ID resolver — the precise defect class this
epic exists to delete, in direct violation of spec R9 and the owner-stated point — and it fails
open when the match comes up empty. The contract's own referent-table witness fixture still
produces no public graph under a classification the owner never specifically ruled on. The
product-lens gate is BLOCKED; Certify is forbidden.

## Product Judgment

**Is this the right piece of work? Almost — but its last mile reintroduced the disease.** The
product-lens ledger gate is **BLOCKED (audit-F20, audit-F21)**; audit-F1/F3 stay resolved,
audit-F2/F11–F15/F17/F18 are resolved by citation in the v2 lens block, audit-F19 stays deferred
to Item 6.

- **audit-F20 (owner/[HARD], BLOCK):** `_resolve_leaf` selects a producer edge for a
  `QUALIFIED_REFERENCE` by sanitizing the CST-scraped qualifier text and suffix/prefix-matching it
  against rendered display paths and qualified names (`src/sysml_codegen/elaboration/elaborate.py:1268-1301`,
  fed from `extraction/binding_evidence.py:107-127` via `elaborate.py:1559-1563`). Verified by
  direct read in this audit, independently by two verification passes and the lens. When the
  string match finds nothing it silently falls back to unqualified resolution
  (`elaborate.py:1300-1301`) — fail-open, not fail-closed. This contradicts spec R9 ("sanitized
  spellings … rendered occurrence paths … may not participate in … edge selection"), the design's
  component contract ("It contains no path parsing or name matching"), Required Invariants 7/9,
  Appendix A case 10, and the owner's stated point ("must not replace it with a non-unique name
  and later try to recover the target").
- **audit-F21 (owner/[HARD], BLOCK):** `deep_cross_scope_probe` — the contract's normative witness
  for two supported referent-table rows — still yields no public graph
  (`SI_RENDERING_COLLISION`). I reproduced the collision live; the runner names the colliding
  channel (`DeepCrossScopeDesign__…__core__metric_value`), so the collision is genuine, but no
  artifact records the colliding trio or an owner ruling that blocking the witness fixture at the
  naming layer is intended, and the cell's only fixture-level evidence runs the internal route.
  The identical failure class on `retype_model` (audit-F17) was treated as a defect and fixed.

Fired smells escalated here, none resolved silently: Smell 1 (ledger vs. run; enum vs. exception
hierarchy — audit-F22/F25), Smell 3 (finite-but-computed bound still labeled non-finite —
audit-F27), Smell 4 (leaf resolution depends on projection's rendered paths — audit-F20), Smell 6
(C5 green via synthetic fixture while the witness model is evidenced internally — audit-F21).
Smells 4 and 6 attach to the blocking findings; 1 and 3 to disposed ones.

An unresolved owner/[HARD] BLOCK forbids Certify regardless of the green rubric below.

## Findings

### Plan completion

Phases 1–4: verified complete in the prior audit round and re-confirmed by gate reproduction; no
regression found. All Phase 1–4 checkboxes stand.

Phase 5: contradicted in one leg, otherwise complete.

- **Contradicted:** remediation-sequence leg "Fix most-specific calculation instantiation and
  usage-context occurrence resolution." The most-specific-writer half is verified
  (`elaborate.py:341-394`, ID-keyed, incomparable writers fail loudly). The usage-context half is
  the audit-F20 string-matching mechanism — implemented, but by a means the spec and design forbid.
  Checkbox reopened.
- The plan honestly records the Phase-5 red-first deviation (internal route implemented before its
  kept test); no contrary claim found.
- Gate reproduction (all exact): contract matrix 30 passed, 0 xfail; full codegen
  **3301 passed / 47 skipped / 18 deselected, zero `no live syside license` lines**; agentic-mbse
  **1814 / 1 / 33**; mypy **72 errors, 0** in elaboration/codec/internal-route files; ruff check +
  format clean on the Phase-3–5 file scope; `git diff --check` clean; corpus runner reproduces the
  ledger's route outcomes exactly (37 rows, 12 exact graphs / 25 typed errors, legacy 36 graphs,
  byte-equal = `sample_model`, `quoted_owner_formula`); legacy dirs
  (`generation/`, `cli/`, `resolution/`, `analysis/`, `orchestration/pipeline_builder.py`,
  snapshot v5 paths) have **zero diff**; no baseline or snapshot fixture file modified.
- Bookkeeping nit: the recorded "exact-elaboration scope passes 200 tests" is not reproducible as
  stated — `tests/{conformance,unit}/test_elaboration_*.py` collects 146; the plan does not record
  the selection that produced 200. All other recorded counts reproduced exactly.

### Spec conformance

- **R1 (one pass, no string re-resolution) — met** for every path except the R9 breach below:
  `_ExactElaborator.run()` (`elaborate.py:208-220`); codec decodes without model/resolver imports
  (`snapshot/instance_graph.py:583-632`).
- **R2 (identity by construction) — met.** One `AttrNode` per (scope, slot) with duplicate
  rejection (`elaborate.py:497-503`); typed `NodeRef`/`ProducerRef` edges; one public input per
  suppliable consumed node with collision block (`project.py:225-275`); no consumer-local minting
  for bound modeled references (`project.py:297-324`).
- **R3 (self-binding hard error) — met.** Exact `element_id` equality
  (`source_evidence.py:130-138`), blocking `SI_SELF_BINDING` (`elaborate.py:999-1009,1585-1586`);
  indexed/expression forms carry their contract codes.
- **R4 (distinct occurrences, distinct sources) — met** by construction of `OccurrenceId`/node
  keys (`identity.py:100-163`); no value-equality merge exists.
- **R5 (projection on the verified seam) — met.** All five module kinds, entry-point groups list,
  topological order, output aliases, constraint catalog (`project.py:566-990`);
  `fallback_entry_points=set()` (`project.py:191`); V11 coverage as hard `SI_EDGE_DANGLING`
  assertions (`project.py:374-380,430-435`); `src/sysml_codegen/generation/` byte-unchanged.
- **R6 (dual-run, no shipped flag) — met.** `orchestration/elaborated_pipeline.py:22-39` internal
  only; zero CLI references; diff harness compares complete public graphs only.
- **R7 (matrix as authority) — met.** The matrix parses the cell set out of the contract at test
  time and asserts equality with its 29 evidence callables
  (`test_elaboration_contract_matrix.py:737-758`); no cell definitions in production code.
- **R8 (deletion ledger respected) — met** for the dual-route phase: the new route imports zero
  ledger machinery; only non-ledger string renderers (`mint_constraint_id`,
  `resolve_modeled_default`, ADR-003 helpers) are shared.
- **R9 (exact parser identity) — GAP.** The audit-F20 mechanism (`elaborate.py:1268-1301`) puts
  sanitized spellings, qualified names, and rendered display paths directly into edge selection.
  Everything else on the semantic path checked out ID-keyed (slot families from redefinition
  endpoints, `sum` plurality by pinned UUID, sorts by wire encoding, no direct `element_id` reads
  outside the adapter boundary).

Non-goals respected: no snapshot format change, no legacy removal, no cross-repo validator
changes, non-finite multiplicity still blocks (with the audit-F27 naming residue).

### Design conformance

D1–D9 verified at their load-bearing points (frozen ID types with adapter-only `element_id`
access; slots from `redefined_feature`/`redefining_feature` endpoints with relationship IDs
excluded; walker imports no legacy occurrence types; typed IDs with wire encodings parsed only in
the codec; occurrence > most-specific-definition > default precedence with loud incomparability;
consumer-port/target edges; projection-owned strings with blocking collisions; codec performs no
semantic resolution; blocking diagnostics make a graph unprojectable via `require_projectable`,
`project.py:175` / `graph.py:262-266`).

Deviations, all undocumented in the design/plan:

1. **The audit-F20 string-matching resolver** (`elaborate.py:1268-1301`) — breaks the design's
   "no path parsing or name matching" component contract and Appendix A case 10. The plan's
   remediation note describes it as "constrains its exact leaf declaration to the parser-accepted
   occurrence qualifier," which does not disclose that the mechanism is string matching.
2. **The import-boundary guard does not catch it** (`tests/unit/test_elaboration_import_boundaries.py:11-34`):
   token-based, three files only; `display.py` is recorded as an allowed consumer but the guard
   bans neither rendered-path prefix/suffix matching nor list-index first-match forms, and
   `project.py`/`graph.py` are unscanned. Appendix A case 10 asks for more than this guard checks.
3. **D10 partial:** `NonFiniteMultiplicityError` and `RecursiveContainmentError` are plain
   `ValueError`s outside the diagnostic vocabulary (`occurrence.py:42,46`), uncaught by
   `elaborate()`; four `ElaborationCode` members are cited by no test (audit-F25).
4. **D8 letter deviation:** projection never reads the graph's `value_site` record; entry-point
   class is decided structurally by edge kind (`project.py:318,330,351`). Outcomes coincide today
   and the discriminator is not name-derived; `ValueSite` is computed and serialized but dead.
5. **Order-dependent display metadata:** `base_by_slot` keeps the first-enumerated candidate when
   no slot-root declaration is present (`elaborate.py:312-322`), and `alternatives[0]` is an
   unguarded model-order fallback in the calc-node builder (`elaborate.py:583-590`). Edges are
   unaffected (Invariant 9 covers edges), but a rendered public name could shift with file order;
   D8's collision check would catch a clash loudly.

### Code integrity

- **Silent fallback on the semantic path (part of audit-F20):** `elaborate.py:1300-1301` discards
  the qualifier when the contextual match is empty instead of diagnosing — the fail-open branch.
- **Silent skips:** `except KeyError: continue` drops slot-less features from the value-writer
  pool with no diagnostic (`elaborate.py:306-309`); `except KeyError: return None` in
  `_modeled_integer_bound` hides *why* a bound was unresolvable (`occurrence.py:277-280` region).
- **Two representations by hand:** `ElaborationCode` enum vs. the surviving exception hierarchy
  (audit-F25); the diff-ledger table vs. the corpus run (audit-F22); two classes named
  `RecursiveContainmentError` in `occurrence.py:46` and `analysis/part_instance_index.py:72`.
- **Source-text-as-evidence residue:** `test_elaboration_dual_run.py:34` and
  `test_elaboration_corpus_ledger.py:29-33` still certify by grepping source text — the exact
  pattern the ratified decisions removed from the matrix (audit-F23).
- **Legacy route as oracle:** `test_public_compatibility_keeps_names_but_uses_occurrence_sources`
  (`test_elaboration_phase5_remediation.py:102-120`) pins new-route public names by executing
  `build_pipeline_context` at test time; dies with the legacy route at Item 6 (audit-F26).
- **Matrix evidence edges:** C23's "mutation" writes a value into already-generated JSON and reads
  it back — bookkeeping, not an elaboration mutation
  (`test_elaboration_contract_matrix.py:456,663-666`); the isolation assertion iterates baseline
  keys only, so a minted extra entry point is invisible (`:671-673`, audit-F24); the decoded-route
  leg stops at `ComputationGraph` equality — YAML/JSON are rendered from the live route only
  (`:660-669`, also true of the public-mutation tests at
  `test_elaboration_public_mutation.py:105,139`).
- **String surgery in projection:** `project.py:664,694,803` reconstruct instance paths by
  `rsplit("__")`/`split("__")` on display strings; acceptable in the string-owning layer but it is
  structure recovered from renderings, worth replacing when the graph carries the structure.
- **Untested block-loud branch:** no elaboration-route test asserts
  `NonFiniteMultiplicityError` for a genuinely unbounded/unresolved cardinality; the d38_caret
  expansion itself is well-tested (`test_elaboration_aggregations.py:132-146`).
- **QN-keyed metadata lookups degrade silently:** `_constraint_decisions`/`_calc_defs`/
  `_compilation_results` key projection payload by qualified name (`elaborate.py:175,752-753,828,862,940`);
  inside R9's metadata carve-out, but a null/colliding QN degrades to `None`/`UNKNOWN` rather than
  failing closed as D10 prescribes.

---

## Certification

**Not certified.** The product-lens gate is BLOCKED (audit-F20, audit-F21, both owner/[HARD]);
under the audit contract that forbids Certify regardless of the rubric.

What this pass checked and marked:

- Verified and left standing: all Phase 1–4 plan checkboxes; Phase-5 legs other than the
  usage-context leg; every recorded gate count (reproduced exactly, listed under Plan completion);
  the corpus ledger's route outcomes (independently rerun); spec R1–R8; design D1–D9 load-bearing
  points; legacy freeze (zero diff in shipped paths, snapshot v5 and baselines untouched).
- Reopened: plan Phase-5 progress checkbox and the "most-specific calculation instantiation and
  usage-context occurrence resolution" remediation leg (audit-F20).
- Epic Item-5 success criteria: left unchecked (correct as found). "Every matrix cell
  green-or-named-diagnostic" is genuinely close — the matrix itself is now real evidence — but the
  C5 family rests on the blocked mechanism, and the ledger's witness-fixture classification is
  unadjudicated (audit-F21).
- Product-lens ledger: v2 block appended with resolutions-by-citation for
  audit-F2/F4/F7/F8/F11–F15/F17/F18 and new findings audit-F20–F27.

**What Needs Work, concretely:**

1. Replace the qualifier string-match in `_resolve_leaf` with an identity-based mechanism (e.g.
   resolve the qualifier's own referent chain to declaration IDs at evidence-capture time, then
   contextualize by slot), and make the no-match case diagnose instead of fall open (audit-F20).
   The guard should then ban rendered-path prefix/suffix matching so it cannot return.
2. Take audit-F21 to the owner: record the colliding output trio for `deep_cross_scope_probe` and
   get a ruling — either the D8 block on the witness fixture is intended (record it as a decision)
   or it is the audit-F17 rendering-defect class and gets the same fix.
3. The disposed findings (audit-F22–F27) need their dispositions executed or explicitly deferred
   with an owner-visible record; none blocks on its own.

**Not checked:** live behavior of licensed tests beyond reproducing recorded counts and the corpus
run (individual cell assertions were verified by reading, not by mutating them); the agentic-mbse
side beyond its full-suite gate and adapter-boundary greps; generated-package execution under a
real TEAx simkit; snapshot-v5 byte identity beyond confirming no snapshot/baseline file is
modified in the tree; performance; and any Item-6 cutover concern. The three verification passes
(product-lens plus two code-verification subagents) read the elaboration package closely but did
not line-audit `graph.py`, `diff.py`, or `display.py` in full.
