# Stage brief — Phase 3, Slice 3C: Coordinated compiler and constraint authority

**You are executing exactly one slice** of the owner-approved recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: Non-Negotiable Execution Rules, Phase 3 preamble (recovery/test import rules),
Slice 3C, per-slice validation, the 3A/3B completion notes, and `evidence/audit-3{a,b}.md`.
This is the first COORDINATED slice: both repositories change together.

## Intent

Converge the exact compiler and constraint authority across sysml-codegen and agentic-mbse —
collision behavior, declaration identity, ordering, and profile behavior proven by kept tests in
BOTH repos — while the old (suffixed/transitional) route remains available until the coordinated
new route is proven. Deletion of transitional duals is Phase 4 work, not 3C.

## State you inherit

- codegen rebuild: `/home/reid/1cfe/sysml-codegen-item7-rebuild`, branch `item7-rebuild`, head
  `38c2e15`, clean. Suite after 3B follow-up: **3520 / 47 / 18** licensed.
- agentic-mbse rebuild: `/home/reid/1cfe/agentic-mbse-item7-rebuild`, branch `item7-rebuild`,
  head `5088b417`, untouched so far. Phase 2 measured baseline: **1819 passed / 1 skipped /
  5 deselected** (1825 collected).
- Venv `/home/reid/1cfe/item7-rebuild-venv` — both packages editable from the rebuild worktrees;
  re-assert import paths first (F2 trap). License: `set -a; source
  /home/reid/1cfe/agentic-mbse/.env; set +a`; proof = zero `no live syside license` lines.
- Parts bins (read-only, per-hunk review): codegen `git -C /home/reid/1cfe/sysml-codegen show
  07531e64:<path>`; agentic-mbse `git -C /home/reid/1cfe/agentic-mbse show ed5b8b02:<path>`.

## What the forensics say about this material (evidence, not certification)

- The agentic-mbse side is the incident's cleanest phase boundary: one 15-file Phase 5 patch
  (+230/−150) — unsuffixed constraint extraction and profile evaluation become the one exact
  route, callers and exports migrate. BUT the plan requires the old route retained this slice:
  where the forensic patch deletes/renames-away a transitional name, keep both callable and
  record the dual for Phase 4's ledger (Item 6 already names four transitional duals there).
- Three quality-cleanup hunks ride inside otherwise-clean agentic files and need SEPARATE
  dispositions: duplicate helper removal in `executable_profile.py`; the direct-execution import
  fallback replaced with an absolute import in `level4_constraints.py` (may alter direct-file
  execution); type/exception cleanup in `level6_architecture.py`. Review each on its own merits —
  reject any that changes behavior without test cover.
- Codegen-side candidate material: the exact compiler/constraint changes (forensic Phase 5,
  17 codegen files) and `tests/conformance/test_exact_constraint_route.py` +
  `test_exact_compiler_core.py` from the forensic tree. The forensic map rates
  `test_exact_compiler_core.py` well (exact rendered expressions, hand-built cycle fixture) —
  still red/green review it, never blind-import.

## Requirements

1. Kept tests FIRST in both repos, red at the inherited heads: collision, declaration-identity,
   ordering, and profile behavior (strict/lenient, BLOCK semantics — Item 6 pinned
   `SI_CONSTRAINT_BLOCKED` on strict, lenient, and round-tripped routes; those pins must stay
   green throughout).
2. Declare the expected path set per repository BEFORE editing; unexpected changed path stops the
   slice.
3. No deletions in either repo. Both full suites must keep every baseline test; explain
   collection deltas exactly (agentic delta vs 1819/1/5, codegen vs 3520/47/18).
4. Run both full suites FROM THE PAIRED REBUILD WORKTREES (never the originals) after the
   production changes; also re-run the codegen v6 route-equality and generated-package tests to
   prove the coordinated change didn't move the 3A/3B surface.
5. Gates per repo before commit: ruff byte-identical (codegen) / lint clean (agentic per its own
   config); mypy no-new vs each repo's baseline; `git diff --check`; changed paths ⊆ declared.
6. Commit BOTH repositories and record the paired OIDs together in the plan's 3C commit-gate row
   (plus OID-record commit). The two commit messages must cross-reference each other's OIDs is
   impossible for the second one — instead: commit agentic first, then codegen naming the agentic
   OID, then the plan OID-record carries both.

## Hard rules

Unchanged: originals/archive/forensic branches untouched; only `item7-rebuild` refs move;
rule-10 conflicts STOP. If exact-vs-transitional convergence would change any behavior an Item 6
test pins, that is a premise conflict — stop with data, do not adjust the pin.

## Report back

What the coordinated slice proves, per-file dispositions in both repos (including the three
quality-cleanup hunks individually), red→green counts per repo, both full-suite results with
exact deltas, the retained duals recorded for Phase 4, gate results, paired commit OIDs.
`ARTIFACT:` the updated plan.
