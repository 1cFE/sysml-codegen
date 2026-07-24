# Mid-Run Audit: Docs Lifecycle Sync — Phases 1–2

**Verdict:** Pass with notes
**Audited:** 2026-07-24
**Branch:** docs-lifecycle-sync
**Commits:** b2e0fc3 (Phase 1: register + 2 in-place fixes), 6909dea (Phase 2: resolver reconciliation)
**Baseline:** merged main 936315c
**Scope:** Phases 1–2 ONLY. Phases 3–5 (severity doc, matrix portability row, EXPLAINER re-anchor) not yet run and not audited here. This is a docs-only item — claims-vs-code truth, not test coverage.

---

## Summary

The Phase 1–2 documentation work is accurate against merged code. Every behavioral claim I spot-checked in the new doc 04 resolves to the right symbol at the cited line; the register's dispositions hold; the exit greps are genuinely clean of live stale claims; the matrix row count is uncorrupted at 274. One minor internal imprecision in doc 04's `ProducerRequest` field table is the only real defect. One cosmetic ordering compression is noted but not a defect. Nothing blocks continuing to Phase 3.

## Findings

### 1. Doc 04 (`04-producer-resolution.md`) — behavioral claims vs code

Verified against `resolution/producer_resolution.py` and `producer_completeness.py` at HEAD. All the load-bearing citations are exact:

- **Single entry / structure.** `resolve_producer` at `:616`; `KEY_FORMS` at `:527`; `TerminalPolicy` at `:84`; `_terminal_miss` at `:688`; `entry_point_qualified_name` at `:553`; `_scope_climb` at `:580`; `_unique_or_tie` at `:465`; `_admissible` at `:606`; `_is_self_reference` at `:568`. **All correct.**
- **Dataclass anchors.** `ProducerRequest` `:99`, `ProducerResolution` `:132`, `ProducerContext` `:181`. Correct. `outcome ∈ {MODULE_OUTPUT, DESIGN_ATTRIBUTE, ENTRY_POINT}` matches the `Outcome` enum (`:94-96`).
- **Ladder order and tier semantics.** The 21-row `KEY_FORMS` table in the doc matches the code row-for-row, including tier partition (rows 1–15 CHANNEL, 16–21 DESIGN_ATTRIBUTE) and the lenient-only marks: rows 13/14/15 and 19/20/21 carry `lenient_only=True` in code and `L` in the doc; all others are unmarked in both. **Exact.**
- **Terminal behavior.** STRICT raises `CodeGenerationError` naming reference + attempted forms + ties, "no fallback, no entry-point synthesis — INV-2" (`_terminal_miss`, `:692-700`); the strict miss raises before the capture-sink append in `resolve_producer` (`:632-635`), so "never reaches the capture sink" is true. LENIENT mints `f"{consumer_eqn}__{key}"` with `key = param_name or reference.replace(".", "_")` (`:564`). **Correct.**
- **Tier-1 before tier-2, scope climb between them.** `_run_resolution` iterates `(CHANNEL, DESIGN_ATTRIBUTE)`, runs the scope climb after the CHANNEL forms and before the DESIGN_ATTRIBUTE forms (`:645-683`). Self-reference guard applied at every tier-1 hit and rejection *continues the table* (`:656` `continue`). **Correct.**
- **Three consumer call sites — all exact.** Constraint `resolve_actual` (`constraint_lowering.py:149`, `resolve_producer` at `:174`); calc binding `_resolve_binding_via_registry` (`dependency_backtracker.py:571`, call at `:596`); aggregation `_build_agg_input_source` (`graph_builder.py:1369`, call at `:1403`), EXPOSE-alias reroute (`:1640`), LocalTerm plain-attribute path (`:1663`). Verified the D5 guard prose ("take the channel ONLY on a `MODULE_OUTPUT`") against the code at `:1652-1656`. The "five call sites" figure in the code's own docstring reconciles: 1 constraint + 1 calc + 3 aggregation. **Correct.**
- **Producer completeness.** `check_producer_completeness` at `:98`; `CompletenessViolationKind` at `:75`; `NAME_BASED_KEY_FORMS` at `:64`. The frozenset holds exactly the five rows the doc names (`dotted_pair`, `leaf_unique`, `bare_name_unique`, `leaf_parent_scoped`, `leaf_consumer_scoped`), and `chain_redefinition_follow` is excluded as the doc states. Both violation kinds (Ambiguous producer / Leaf-name guess) and the "spans tier-1 rows 14–15 and tier-2 rows 19–21" claim match the code and its docstring, including the audit-Major-1 MODULE_OUTPUT-exemption history. **Correct.**

**Finding 1a — Minor (imprecision):** `04-producer-resolution.md:60`. The `consumer_eqn` field row says it is the "**Sole input** to the self-reference guard and to the entry-point QN rule." True for the self-reference guard, but **not** for the entry-point QN: `entry_point_qualified_name` (`producer_resolution.py:553-565`) also reads `param_name` and `reference`. The doc contradicts itself two rows later, where `param_name` is described as "**Drives** the entry-point QN" (`:62`). Fix: drop "and to the entry-point QN rule" from the `consumer_eqn` row, or reword to "prefix of the entry-point QN." The terminal-fork section (`:163-168`) already describes the QN rule fully and correctly, so this is a table-cell imprecision, not a wrong mental model.

**Finding 1b — Cosmetic (not a defect):** `04-producer-resolution.md:44-47`. The single-entry-point summary lists "runs the declared table … tier 1 before tier 2. Then it runs the tier-1 terminal search (the scope climb). Then … the terminal policy." Read strictly in sequence, that places the scope climb after tier 2, whereas the code runs it between tier 1 and tier 2. This mirrors the code's own `resolve_producer` docstring verbatim (`:621-623`), and the doc's dedicated scope-climb section (`:110-116`) correctly says "After the tier-1 rows miss." The "tier-1 terminal search" label already scopes it to tier 1. No change required; noted only for completeness.

### 2. Doc 24 rewrite — dated history accurate, no live claim describes deleted architecture

`24-dual-resolution-architecture.md` retitled to "One Authority, Called at Two Pipeline Stages." The live body describes only `resolve_producer()` and the surviving DFS-timing distinction. The one structural distinction claimed (calc bindings resolve *during* the backtracker DFS; others after) is real — `_trace_dependencies` branches on the resolution result to decide recursion. The deleted names (`resolve_input`, `AGG_STRATEGIES`, `ResolutionContext`, `input_resolver.py`) appear **only** inside the block-quoted "Dated history — the pre-unification 'two resolvers' story" (`:136-149`), explicitly marked "Historical, not current" and "describes no live code." That history is factually correct: those symbols were deleted and replaced by the one table. **No live claim describes the deleted architecture.** Pass.

### 3. module_kind sweep (doc 05, 22:179, matrix REQ-MF-03) vs ModuleKind code

`ModuleKind` is a real `str, Enum` at `resolution/models.py:197` with members CALCULATION/FORMULA/AGGREGATION/CONSTRAINT/REPORT_AGGREGATOR; `PipelineModule.module_kind: ModuleKind` at `:229`; the retired `is_computed_attribute`/`is_aggregation` bool fields are absent. Swept claims now match:
- `22-output-schema-rules.md:179` — "Module tagged with `module_kind` (`ModuleKind.AGGREGATION` for aggregation)." Correct.
- `verification-matrix.md:362` (REQ-MF-03) — "FORMULA factory SHALL set `module_kind=ModuleKind.FORMULA`." Correct.
- Doc 05 bool-flag claims (C1–C6): grep for `is_computed_attribute|is_aggregation` across `docs/architecture/` returns **only** `09-data-models.md:71,301`, which is the retirement narrative (register C9 = ACCURATE, correctly untouched). Zero live claims. Pass.

### 4. verification-matrix.md — row count and index integrity

`grep -cE '^\| REQ-'` returns **274**; the summary block "Total requirements | 274" reconciles (`:9`). No index/count corruption introduced by the Phase-2 text edits. The residual resolver-name hit at `:218` is a clearly-marked deletion-status note ("the standalone aggregation resolver (`input_resolver.py`) was deleted"), which the success criterion explicitly allows. The banner also surfaces the deferred `REQ-PR-*` family as a filed GAP (spec R2), consistent with the register. Pass.

### 5. Register (inventory.md) — spot-checked dispositions

Six dispositions verified across sweeps A–D plus R5:
- **A2 (ACCURATE):** `PROFILE_SEMANTIC_VERSION = "executable-profile/v4"` at `_upstream_pins.py:33`. Confirmed accurate. (Note the file is `src/sysml_codegen/_upstream_pins.py`, not under `snapshot/`; the register cites the bare filename, which is unambiguous.)
- **A1/A3 (STALE line-drift / ACCURATE):** `SNAPSHOT_FORMAT_VERSION = 5` at `snapshot/__init__.py:30`. The A1 fix landed — `27-snapshot-generation.md:37` now cites `:30`. Confirmed.
- **B1 (GAP):** `CATALOG_SCHEMA_VERSION = "2.0.0"` at `contracts/versions.py:18`, no doc mention. Confirmed a real gap, not a stale literal.
- **B4 (GAP→Phase-3):** `screen_extraction_diagnostics` at `analysis/diagnostic_screen.py:51`. Citation correct.
- **B6 (GAP→Phase-4):** `_validate_source_referents` at `snapshot/loader.py:912`. Citation correct.
- **C9 (ACCURATE):** `09-data-models.md:71,301` describe `is_computed_attribute`/`is_aggregation` as the *retired* flags module_kind replaced. Confirmed accurate — leaving it untouched is correct.
- **R5 note factual claims:** `[NESTED-OCCURRENCE-OVERRIDE]` is at `.project/backlog/BACKLOG.md:168` (exact). The note added to `modeling-assumptions.md:355-357` states the override is captured "definition-relative while demand resolves occurrence-relative, so the materializer never matches and the model literal is lost" — this matches the backlog gap description and does not claim nested-occurrence capture works. Correct.

All spot-checked dispositions hold. The register is trustworthy.

### 6. plan.md Phase 1–2 boxes/notes vs reality

- Phase 1 changes-required and validation boxes all `[x]`; the completion note's headline sweep findings match the register (A1 line-drift, B GAPs, C bool-flags deferred, D resolver family deferred). The surfaced brief-vs-plan boundary (module_kind deferred to Phase 2) is honestly recorded in both plan and inventory per capture-fidelity rule 4.
- Phase 2 boxes all `[x]`; the completion note matches the diff (04 renamed + rewritten, 24 rewritten, in-place 03/05/overview/matrix, doc-19 reconciled, module_kind C1–C8 fixed). The surfaced REQ-IR/REQ-DRA re-projection deviation is recorded with its rationale.
- Phases 3–5 boxes all `[ ]` — consistent with a mid-run audit. Correct.

## Certification

Checked and confirmed against merged main 936315c:
- Doc 04: all cited symbols/line numbers, the full 21-row ladder with tier + lenient-only marks, strict/lenient terminal behavior, tier ordering + scope-climb placement, all three consumer call sites (five call sites), and the producer-completeness contract.
- Doc 24: dated-history accuracy and the no-live-deleted-architecture invariant.
- module_kind sweep: doc 05 / 22:179 / matrix REQ-MF-03 against `ModuleKind`.
- Matrix row count (274) and index integrity.
- Six register dispositions (incl. two ACCURATE verdicts) and the R5 note's factual claims.
- Plan Phase 1–2 checkboxes and completion notes.

One Minor imprecision (Finding 1a) and one cosmetic note (Finding 1b) in doc 04. Neither blocks Phase 3. No fixes applied (report-only).

**Not checked:**
- Phases 3–5 deliverables (severity reference doc, portability matrix row + recount, EXPLAINER_PROMPT re-anchor) — not yet produced.
- Doc 04's design-invariant cross-references (I1, I3, I6, I7, I9, I10, D-1, DD-R27) as *labels* — these point at Item 2 / Item 10 design docs, not code, so I verified the described *behavior* against code but did not confirm each label maps to the design doc's numbering.
- Full prose read of `03-resolution-overview.md`, `05-module-factory.md`, `overview.md`, `00-pipeline-overview.md`, and the doc-06/07/10/13/15/21 one-line reference fixes in commit 6909dea — I confirmed the mechanical exit greps are clean and spot-checked the anchors, but did not read every reframed sentence.
- The B2/B3 GAP surfaces (written_qualifier, trust manifest) beyond confirming the cited symbols exist.
- Any byte-identity / test-suite behavior — out of scope for a docs-only item.

ARTIFACT: .project/active/docs-lifecycle-sync/audit-midrun.md
