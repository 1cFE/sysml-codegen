# Brief — Phase 3 implement (fresh session): finish making Codegen accept only closed evidence

You are executing **Phase 3 only** of plan **Revision 4**, resuming from committed work a prior
session left in a good state. That session correctly halted on a design conflict; the owner
ruled on everything it raised; the design and plan were amended; a new upstream landing fixed
the blocker. You start from clean, committed trees — verify them first, then execute the
remaining Phase 3 checklist. Read in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — **Revision 4**, your contract:
   "Phase 3" (its "Starting state" block describes exactly where you begin), the Global
   Execution Contract, and the "Phase 2b completion" section (your upstream's record).
2. `design.md` — **Revision 8** — especially `#one-total-inspection-operation` (opaque unit
   operand, the shared `unit_annotation_value` primitive, the arity ruling),
   `#d7-one-codegen-conversion-boundary`, the Codegen-gate subsection under the manifests
   section ("The Codegen gate keeps repository-wide scope"),
   `#binding-and-deep-path-values-are-valid-by-construction`, `#scoped-strict-type-boundary`,
   `#d8-diagnostic-ownership`, `#codegen-pin-and-dependency-contract`.
3. `run-records/phase3-stop-report.md` — what the prior session landed and why it halted.
4. `run-records/phase2-audit.md` — including its final "Phase 2b addendum" section, which
   clears your upstream.
5. `run-records/phase1-audit.md` — Minors 6, 7, 8 and Informational 12 are assigned to this
   phase.
6. `run-records/entry-status.md` — run scaffolding and checkout-integrity rules.

Provenance: plan rev 4 and design rev 8 are binding. The owner's rulings (2026-08-18) are
encoded there with their grades — implement them exactly; on any conflict the plan/design win
and you surface the conflict in your final message instead of resolving it silently.

## Where you work

- **Codegen worktree:** `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch
  `stop-parser-impl-r2` at **`b4e97dd`**, verified clean. ALL implementation commits go here.
  Do NOT roll back `b4e97dd` — the owner ruled it stands.
- **Agentic worktree:** `/tmp/stop-parser-rev2/worktrees/agentic-mbse` at **`3f8bd58`** —
  **read-only**. This is your upstream: Agentic `0.1.3` / `semantic-evidence/v2` with the
  audit-confirmed `unit_annotation_value` primitive exported. Build its wheel/archive into a
  directory under `/tmp/stop-parser-rev2/` if the pin contract needs an installable artifact;
  commit nothing there.
- **Docs checkout:** `/home/reid/1cfe/sysml-codegen` (branch `stop-reinventing-the-parser`).
  Only the plan.md "Phase 3 completion" section update is committed here, as your final act.
  Never run implementation commands from it.
- Touch NOTHING else — no user checkout, no `/tmp/stop-parser.QVJIIP/*` (read-forbidden), no
  stash/reset/switch anywhere.

## What `b4e97dd` already contains (do not redo; do not reopen)

- All 12 indexed bare-chain red nodes green with exact-field assertions
  (`reference == "cells#(2).mass"`, `source_file == "root-0/model.sysml"`,
  `source_line == 15`, refusal before consumers and before occurrence resolution, no
  graph/snapshot) across live/admitted/capture × strict/lenient. Turned green by satisfying
  them — keep it that way.
- `elaboration/expression_evidence.py` and `extraction/binding_source.py` exist and pass the
  scoped strict gate.
- The weak-surface deletions (`SourceReferenceEvidence`, `SourceForm`,
  `screen_source_readiness`, the four `binding_evidence` builders, `annotated_ast_value`, the
  dead `SysMLDataExtractor` cluster, and the rest listed in the stop report).
- `occurrence.py` byte-identical to `C_base`; `deep_cross_scope_probe` still refused.

## The remaining work (plan rev 4 Phase 3 is the contract; this is the map)

1. **Pin the dependency:** Agentic `0.1.3` at the `3f8bd58` landing, `semantic-evidence/v2`;
   bump Codegen to `0.1.1`; update `_upstream_pins.py`, `pyproject.toml`, version tests,
   `uv.lock` per the design's pin contract.
2. **Re-base the value-site helper:** `expression_evidence.unit_annotated_value` becomes
   value-site **policy only**, delegating ALL structural interpretation (metatype, operator,
   arity, operand shape) to Agentic's `unit_annotation_value`. The interim implementation in
   `b4e97dd` still interprets parser structure itself — that is what you replace.
3. **Ownership closure, per the design's Codegen-gate subsection** (the owner rejected
   adapter-import scoping here — the m2 hole must never become load-bearing):
   - repository-wide selector discovery stays;
   - collision-aware reviewed rows for the six neutral `ExpressionIR.operands` readers and the
     five `SourceFile.referent` readers, each with the design-defined proof artifact (a kept
     test pinning the annotation/declaring type at the read site; an unannotated receiver
     never qualifies and stays red);
   - an adapter-free evasion mutant (e.g. `def consume(node): return node.referent`) that must
     appear in the discovered set **and fail the manifest equality gate**;
   - the genuine raw reads (e.g. `usage_extractor`) migrated onto the closed boundary or
     mechanically excluded, judged against the full 20-row measurement — a red count that
     shrinks because the scan narrowed is not progress.
4. **The disposition table:** `tests/conformance/test_source_identity_extraction.py` currently
   blocks collection and may be removed only via the **14-row disposition table** plan rev 4
   enumerates (replacement test ID or precise retirement reason per row, against
   `ledger-4a.md:628`), with replacements landing **in the same commit** that deletes the file.
5. **The missing kept tests** (owner condition on the tests-after deviation): constructor/
   exhaustiveness, inventory-missing/duplicate, per-consumer inventory-bypass, deep-path
   totality — plus mutation-testing of the important boundaries. The closing audit will attack
   six weak variants (skipped inventory, indexed-to-exact conversion, shortened deep paths,
   adapter-free selector reads, malformed unit arity, missing diagnostic provenance); your kept
   tests, not the audit, must be what catches them.
6. **Carried findings:** Phase-1 audit Minor 6 (closure-proof names must resolve to real
   tests), Minor 7 (off-route reachability transitive from public roots), Minor 8 (parse the
   ledger row for the path, no whole-file substring matching), Informational 12 (structural
   fixture/verification row classification in the lock check).
7. **Everything else plan rev 4 Phase 3 lists:** one inventory + exact resolver wired through
   `elaborate.py` / `expression_compiler.py`, closed binding variants, total deep-path factory,
   single public conversion, runtime rejection proofs (indexed use, legacy fact, IR node,
   duck-typed lookalike), sealed from-snapshot route unable to import the raw enumerator, and
   the full validation battery.

## Validation (binding; plan rev 4 has the complete list)

- **Compound-unit elaboration proof:** the `catf_mfe_*` fixtures and the stop report's exact
  `density = 9400 [kg/m^3]` case must elaborate with zero refusals through your boundary.
- All Phase-1 Codegen red nodes green except `test_every_consumer_cell_names_a_proof`, which
  plan rev 4 defers to Phase 4 — name it and cite that deferral in your record.
- Scoped strict zero on both boundary modules; repo-wide mypy baseline (30 errors in 8 files at
  `C_base`) unchanged; targeted Ruff clean on changed files.
- `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` empty; focused D1-D4 rerun
  green; `deep_cross_scope_probe` still refused (global stop condition).
- Authoritative full-suite numbers from a fresh declared extraction under
  `/tmp/stop-parser-rev2/` (plain-worktree collection failures are a known `C_base` property —
  see plan.md Phase 1 deviations 1-2); the extraction path for any Agentic artifact must
  contain `agentic-mbse`.
- SysIDE license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; never copy a
  secret anywhere. **[OWNER-VERBATIM]** "do not rerun the PDF suite anymore" — the Agentic slow
  PDF/HTML corpus and 15 paid/network cases stay unrun.
- No compatibility wrapper, alias, exemption, optional path, or second resolution mode for any
  deleted surface. A production consumer that still needs a raw expression is a design
  conflict: **STOP and report** — do not work around it.

## Deliverables

1. Commits on `stop-parser-impl-r2` on top of `b4e97dd`, in reviewable units (tests with or
   before the production they prove; the disposition-table commit pairs deletions with
   replacements).
2. Every Phase 3 validation box executed with commands and results recorded.
3. plan.md "Phase 3 completion" section filled (completed date, commit SHAs, red-to-green
   account naming every Phase-1 node, actual changes, issues/deviations, rollback point) and
   committed in the docs checkout.
4. Final message: prose summary — what you built, the ownership-closure account against the
   20-row measurement, the disposition table outcome, gates, deviations — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. If any stop rule trips,
   say so plainly at the top and stop.

Phase 3 is the end of your scope. Do not begin Phase 4 work (registry closure, full
natural-route matrix, ledger rows A5a/A5b, documentation sweep) of any kind.
