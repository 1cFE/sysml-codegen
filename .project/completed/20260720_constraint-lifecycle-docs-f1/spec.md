# Spec — Lifecycle Item 6: Public Documentation and F1 Evidence Reconciliation

**Register rows:** 6–7. **Depends on:** Item 5 (landed, `4c6223c` + audit commits).
**Authority:** Item 6 in `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`.

Pinned landed chain this reconciles against: sysml-codegen through Item 5
(`4c6223c`), agentic-mbse `4c18d61` (profile `executable-profile/v4`,
`constraint-facts/v2`), TEAx `d545701`.

This is a single-stage item: inventory → spec-as-checklist → fix → evidence. The plan is
folded in here (§5). No reimplementation of landed normalization; no release-readiness
claim anywhere.

---

## 1. Intent

Make every public claim and the F1 evidence agree with the landed candidate. A
correction shrinks or amends the stale claim in place with a code/evidence citation; it
never adds "this used to say X" prose. The item's success criterion is *every
correction-register claim agrees with landed code and versions.*

## 2. Method

Three independent inventory sweeps read `docs/architecture/` and `src/` against landed
code, each returning a per-claim disposition (STALE / ACCURATE / AMBIGUOUS / GAP). Every
STALE verdict carries the code citation that proves it stale. Sweeps covered: (A) version
literals, (B) snapshot replay / V11-Gate B / catalog, (C) equality-ordering, subtype
coverage, diagnostics severity, portability.

## 3. Inventory and disposition

### 3a. STALE — corrected in this item

| # | Claim (file:line) | Was | Landed reality (citation) | Fix |
|---|---|---|---|---|
| S1 | `docs/architecture/reference/27-snapshot-generation.md:37` | snapshot format "Current: **3**" | `SNAPSHOT_FORMAT_VERSION = 5` (`snapshot/__init__.py:28`) | → **5** with code cite |
| S2 | `27-snapshot-generation.md:57-64` | `source_file` "byte-identity": capture relativizes, loader **re-absolutizes** by lexical join → reproduces the exact absolute string | v5 stores a portable `root-N/<relpath>` referent; loader reconstructs **no** absolute path and validates referent shape (`serializer.py:277-282`; `loader.py` `_validate_source_referents`; `snapshot/__init__.py:20-27`) | replaced with the v5 referent model |
| S3 | `27-snapshot-generation.md:78-84` | "v2 → v3 migration … no v2/v3 coexistence … re-captured at v3" (froze v3 as current) | Format advanced v3→v4 (Item 4 severity field) →v5 (Item 5 referent); gate rejects anything ≠ 5 (`snapshot/__init__.py:12-28`) | amended to the v2→v5 migration record |
| S4 | `27-snapshot-generation.md:126-128` | re-lowering applies "executable-profile **v3** behavior" | `PROFILE_SEMANTIC_VERSION = "executable-profile/v4"` (`_upstream_pins.py:33`) | → **v4** with cite |
| S5 | `27-snapshot-generation.md:131` | package floor "`agentic-mbse>=0.1.1`" | floor is `>=0.1.2` (`pyproject.toml:24`) | → **0.1.2**; "pre-v3 companion" → "predating the pinned profile" |
| S6 | `docs/architecture/verification-matrix.md:531` (REQ-SNAP-09) | "(current: **3**) … no v1/v2/v3 coexistence" | current is 5; gate rejects any non-5 (`snapshot/__init__.py:28`) | → "(current: 5) … no cross-version coexistence" |
| S7 | `src/sysml_codegen/generation/predicate_compiler.py:150` | error string "not supported in executable-profile/**v3**" — a **duplicate version literal** of the v4 pin | profile is v4 (`_upstream_pins.py:33`) | single-sourced: `f"... {PROFILE_SEMANTIC_VERSION}"` |
| S8 | `predicate_compiler.py:201` | error string "not admitted by executable-profile/**v3**" — duplicate version literal | profile is v4 | single-sourced from the pin; pinning test `test_predicate_compiler.py:384` re-matched on `executable-profile/v\d` so it cannot re-drift |

### 3b. ACCURATE — verified, no change (recorded so the next auditor need not re-derive)

| Area | Where | Landed check |
|---|---|---|
| Extension/final V11 (the settled branch) | `07-graph-assembly.md:274-304`, `11-analysis-backtracker.md:49-51`, `24-dual-resolution-architecture.md:136`, `modeling-assumptions.md:465-485`, `overview.md:44`, `00-pipeline-overview.md:144-158`, `verification-matrix.md` REQ-GA-08 | Every V11 mention already describes the **final-generation gate only**. No doc describes an active extension-time / differential coverage check — the exact settled branch Item 3 proved (extension is vacuous; check deleted). Code: `analysis/constraint_lowering.py` `extend_graph_with_constraints` "Runs **no** V11 coverage check"; `collect_uncovered_params` has one caller, the final gate (`cli/__init__.py` `_reconcile_params_coverage`). |
| Embedded catalog / CE-F1 open | `08-generation.md:159`, `28-constraint-lowering-and-catalog.md:74-99`, `29-contracts-and-sealing.md:53-57` | Describe the embedded single-channel catalog on the graph and flag standalone `constraint_catalog.json` (CE-F1) as the open follow-on, not landed. Matches `src/` (no `constraint_catalog.json` emission). |
| Equality / ordering | `modeling-assumptions.md:427-444`, `28-…:111-112` | Equality (`==`/`!=`) is never compiled — `_compile_equality` raises; ordering compiles via `_cmp` with three-valued (Kleene) semantics (`predicate_compiler.py:199-217`). The block decision lives in agentic-mbse's `executable_profile.py`. |
| Subtype coverage | `01-extraction.md:20` (REQ-EXT-09), `modeling-assumptions.md:412-413` | `ConstraintUsage` swept with `include_subtypes=True`; the mutation check flips it to prove `assert` is then missed (`extraction/extractor.py:98,121`). |

### 3c. GAP — surfaced, not fixed here (no stale claim exists; owner/Item 13 territory)

Per the correction law, a missing doc is a coverage gap, not a claim to amend. Recorded so
they are not mistaken for "covered":

- **G1 — Diagnostic severity (Item 4) is undocumented.** No `docs/` file mentions the
  `DiagnosticSeverity` field, the `screen_extraction_diagnostics` sink, or the fail-closed
  contract. It is real and landed (`analysis/diagnostic_screen.py`, `_upstream_pins.py:24-27`,
  `snapshot/loader.py:588-591`) and documented inside Item 4's own artifacts. No public doc
  describes an *old* pre-severity model, so there is nothing STALE — only absent. Backfilling
  reference/matrix coverage is Item 4-owned or a documentation follow-on, not an Item 6
  correction.
- **G2 — Item 5 portability has no verification-matrix row.** The v5 referent shape gate
  (`_validate_source_referents`) and the whole-tree portability contract have no REQ-SNAP row;
  the family stops at REQ-SNAP-20. Adding a row changes matrix index counts — Item 13's
  composed-proof territory. Doc 27 §"source_file portable referent" (S2) now carries the prose
  description.

### 3d. AMBIGUOUS — left as dated history (line 37/126 fixes remove the confusion)

- `27-…:41` "constraint_facts … Always present (**v3**)" — an origin marker ("added at
  v3"), correct as history. With line 37 now reading "5", it no longer reads as a current-
  version claim. Left in place.

## 4. F1 evidence reconciliation (register row 7)

- **F1 landed at TEAx `d545701`**, not `927a9e1`. `d545701` ("Normalize exceptional
  arithmetic failures") carries `pipeline_executor.py`, `evaluator.py`, the F1 tests, and
  the audit itself; `927a9e1` ("Reframe battery demo as an example") touches only a demo
  HTML — it provably lacks the F1 change (`git show --stat`).
- **Stale audit reference corrected:** the F1 audit header
  `teax/.project/active/gap-close-f1-normalization/audit.md` line 6 read `**Commit:**
  927a9e1` → `d545701`. The sibling `design.md:9` "**Base commit:** 927a9e1" is left: the
  design was legitimately written against the parent.
- **Complete report-content comparison across evaluators** is exercised by
  `test_f1_arithmetic_normalization.py` at `d545701` — see evidence.md §2. Surfaced honest
  limitation (not reimplemented): the normalized failure phase is hardcoded
  `MODULE_EXECUTION` and `OUTPUT_WRITE` is defined but never emitted (`evaluator.py:62`,
  `failure.py:23`). Owned by Item 11 ("Emit `OUTPUT_WRITE` honestly or collapse the unused
  phase"), not Item 6.

## 5. Folded plan / checklist

- [x] Three inventory sweeps run against landed code with per-claim citations (§3).
- [x] RED-first production change: explicit invalid `TEAX_SIMKIT_PATH` fails instead of
      discovering the sibling — new failing test then fix (evidence.md §1).
- [x] Eight STALE doc/code claims (S1–S8) corrected with citations.
- [x] F1 audit reference `927a9e1` → `d545701`; report-content comparison recorded (§4).
- [x] PR-description drafts for agentic-mbse #11 and codegen #9 into this directory
      (`PR_DRAFT_agentic_mbse_11.md`, `PR_DRAFT_codegen_9.md`) — no push, no PR edit.
- [x] Gates green (evidence.md §3): full suite 3064 passed / 44 skipped / 0 failed,
      mypy 72 (baseline), ruff clean.

## 6. Success criteria (epic Item 6)

- [x] Every correction-register claim agrees with landed code and versions (S1–S8 fixed;
      3b verified accurate).
- [x] F1 evidence names the correct commit (`d545701`) and compares exact report content.
- [x] Invalid explicit simkit path never falls through (RED→GREEN, evidence.md §1).
- [x] Stale documentation helpers and duplicate version literals removed where superseded
      (S7/S8 single-sourced; no stale `executable-profile/v3` literal remains in `src`/`docs`).
