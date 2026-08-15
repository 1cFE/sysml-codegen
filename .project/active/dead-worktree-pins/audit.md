# Audit: Dead Worktree Pins

**Verdict:** Certify
**Audited:** 2026-08-15
**Branch:** main
**Commit:** 14fe868

---

## The Point

The cleanup correctly deleted obsolete worktrees, but two gates still treated those deleted paths
as their authority. This repair must make both gates inspect the main checkouts while preserving
their ability to reject false evidence. A missing checkout or a wrong import resolution must fail
or abstain loudly, never produce a green result by absence.

## Summary

The implementation is the right narrow repair and works on its live paths: the targeted unit suite
passes, the ledger checks all 304 rows against the main companion checkout, and the licensed
execution lane passes all 88 nodes. The audit follow-up now falsifies the real L-036 and L-037 rows
in a kept test, and the stale checker contract wording is corrected.

## Product Judgment

**Yes, this is the right piece of work.** The audit product-lens gate is **CLEAR**. Its full-ledger
scan found no unresolved `BLOCK`, and no product-drift smell fired. The older agent-grade `spec-F7`
deferral remains non-blocking but still needs its recorded plan-or-close disposition.

## Findings

### Plan completion

Not applicable. This low-complexity item intentionally has no plan; the owner directed execution
from the approved spec (`spec.md:3`, `spec.md:192-196`). Completion was checked directly against
the spec.

### Spec conformance

- **SC1 — verified.** The three live pins now derive from the current repositories
  (`scripts/check_ledger_4a.py:98-101`, `tests/execution/environment_pins.py:19-25`), and the
  reference sweep leaves only the archived probe, historical fixture data, and the deliberate
  wrong-resolution test input.
- **SC2 — verified.** The licensed main-checkout execution command collected and passed all 88
  nodes, including all 12 nodes in `test_fusion_tea_real_teax.py`.
- **SC3 — verified.** The execution fixture consumes the pure pin predicate
  (`tests/execution/test_fusion_tea_real_teax.py:90-114`). Five kept default-suite tests prove the
  expected resolution passes and wrong SimKit, site-packages codegen, and dead-worktree agentic
  resolutions fail (`tests/unit/test_environment_pins.py:28-74`).
- **SC4 — verified.** The live gate resolves L-036/L-037 against the main companion checkout and
  parses their existing files (`scripts/check_ledger_4a.py:98-101`, `:195-229`). The kept
  parameterized regression loads both committed rows, replaces each removal claim with a symbol the
  live file still declares, and asserts the removal check fails
  (`tests/unit/test_check_ledger_4a.py:854-881`).
- **SC5 — verified.** `paths` checks configured roots before walking rows and returns 2 with an
  abstention message (`scripts/check_ledger_4a.py:821-836`); the missing-root regression pins the
  exit and message (`tests/unit/test_check_ledger_4a.py:818-851`).

Tagged requirements:

- **[NEED] fixes-only scope — met.** The implementation changes only the two pins, their checks,
  and item records.
- **[HARD]/[NEED] deleted worktrees stay deleted — met.** Worktree and branch inventories contain
  neither `sysml-codegen-item7-rebuild` nor `agentic-mbse-item7-rebuild`.
- **[HARD] execution environment — met.** The lane remains explicitly excluded from the default
  suite and documents its dependency route (`pyproject.toml:44-50`); the licensed command passed.
- **[INFERRED] invocation is not frozen — met.** No implementation code hardcodes the validation
  command.
- **[HARD] missing row-path semantics — met.** An absent row path remains valid removal evidence
  after the root-level premise is checked (`scripts/check_ledger_4a.py:208-210`).
- **[HARD] main companion is real verification — met.** Both companion files exist, all four named
  symbols are absent, and `paths` reports `304 rows checked, 0 problems`.
- **[NEED] missing configured root exits nonzero — met.** The CLI and kept regression both return
  2 before row checks.
- **[INFERRED] anchor-derived pins — met.** Both repository roots derive from the current files'
  locations (`scripts/check_ledger_4a.py:88-101`, `tests/execution/environment_pins.py:19-25`).

Non-goals were respected: the archive and historical fixtures remain; product assertions in the
execution lane are unchanged; the ledger headline was not redesigned; and `replacements`,
`surface`, and `groups` behavior was not changed.

### Design conformance

Not applicable. The owner intentionally skipped a design for this small repair. The implementation
resolved the spec's mechanism question with anchor-derived roots and a pure predicate.

### Code integrity

No abstraction slop, silent fallback, broad exception swallowing, compatibility shim, or
product-drift smell was found. The new helpers each have one readable job and the failure paths are
explicit. The audit follow-up corrected the stale “either rebuild repo” wording to “either
configured checkout” (`scripts/check_ledger_4a.py:198`).

---

## Certification

Checked the spec, spec review, every product-lens ledger block, implementation diff, affected call
paths, worktree/branch state, and the five audit-stage code smells. Ran:

- targeted unit tests after the audit fixes: **65 passed**;
- ledger `paths`: **304 rows checked, 0 problems**;
- licensed execution lane from the main checkouts: **88 passed**;
- Ruff on the new and directly changed checker/helper/unit files: passed;
- `git diff --check`: passed.

Marked all five success criteria verified. No epic tracking applies to this cleanup residue.

**Not checked:** The full default/conformance suite; `replacements`, `surface`, and `groups` runtime
modes; the historical byte-identical merge proof; remote branch state. Full-file Ruff on the
pre-existing execution module still reports its unchanged unused imports at lines 37-38.
