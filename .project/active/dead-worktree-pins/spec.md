# Spec: Dead Worktree Pins — Repair the Gates the Phase-D Cleanup Broke

**Status:** Certified (2026-08-15) — all five success criteria verified
**Owner:** Reid W
**Created:** 2026-08-15 09:29 PDT
**Complexity:** LOW
**Branch:** main (codegen `9ce5548`)

---

## Problem

The phase-D cleanup on 2026-08-15 deleted two git worktrees, their `item7-rebuild` branches, and the
task venv at `/home/reid/1cfe/item7-rebuild-venv`. That deletion was owner-directed and is correct —
the content had landed on `main` in all three repos and was verified byte-identical.

Two files — three references in all — still name those deleted paths. Verified 2026-08-15, worktrees
confirmed absent:

| location | what it names |
|---|---|
| `tests/execution/test_fusion_tea_real_teax.py:110-111` | asserts `-item7-rebuild/` appears in the resolved import paths of `sysml_codegen` and `agentic_mbse` |
| `scripts/check_ledger_4a.py:99` | `REPO_ROOTS["agentic-mbse"]` → `../agentic-mbse-item7-rebuild` |

**1. Loud: 12 execution-lane nodes error at setup.** The `environment` fixture is module-scoped and
asserts the import paths before any test body runs, so every test in that module errors. Measured
from the main checkout: `76 passed, 12 errors`. The fixture's *intent* is sound and worth keeping —
it exists so acceptance evidence cannot be silently produced against the wrong tree — only its
target moved.

**2. Quiet, and worse: the ledger gate silently lost two rows.** The `paths` mode of
`check_ledger_4a.py` checks all 304 rows across several dimensions — duplicate paths, exact diff-set
equality, carried-row presence, row state, deleted responsibility, removed symbols, surface
coverage, data coverage, blockers, dispositions, recorded reasons (`check_paths`,
`scripts/check_ledger_4a.py:534-594`). One of those dimensions, `check_removed_symbols`
(`:179-213`), verifies executed removed-symbol claims: **12** rows carry one at HEAD, and **2** of
them (L-036/L-037) are `repo: agentic-mbse` rows resolved against `REPO_ROOTS["agentic-mbse"]`.

For that check, a missing *row path* is the intended proof — an executed delete row's file is
supposed to be gone, so absence is verification, **provided the configured checkout exists**. The
defect is that the check cannot tell a missing row path from a missing *repository root*: with the
agentic root pointing at a deleted directory, the 2 companion rows are silently skipped instead of
parsed, and the run still prints `304 rows checked, 0 problems`. The gate did not fail loudly; it
lost two rows without saying so. The checker's documented-ceilings list names the analogous skip in
`replacements` mode (ceiling 6, `:64-66`) but not this one in `paths` — and a gate that cannot fail
is worse than one that fails loudly.

**Why now.** These are gates. While the execution lane errors, the strongest acceptance evidence in
the repo cannot be reproduced at all; while the two rows are silently skipped, a green run
overstates what was checked. Both were working before this morning and were broken by cleanup, not
by design work.

**Current-fact note.** Both defects are live at HEAD `9ce5548` (verified 2026-08-15). A phase-D
`88 passed` lane figure exists in the record but was reached only *with* a since-reverted repair
applied — it is not a HEAD result. The full correction history lives in
`.project/CURRENT_WORK.md:205-213` and the sibling item's Change Record; design should trust HEAD,
not either status narrative.

## Success Criteria

- [x] **These three references, and only these, no longer name a nonexistent path:**
      `tests/execution/test_fusion_tea_real_teax.py:110`, `:111`, and `scripts/check_ledger_4a.py:99`.
      Named exactly rather than by a repository-wide rule, so acceptance does not depend on an
      implementer's reading of "live code." Two categories of `item7-rebuild` text are deliberately
      **out of scope and must remain**: the archived probe under `scripts/archive/` (see Non-Goals),
      and historical strings inside test-data fixtures such as
      `tests/unit/data/item8-snapshot-inventory-{pre,final}.json`, which record past output rather
      than pinning a path.
- [x] The execution lane runs to completion from the main checkouts with **zero errors** — 88 nodes,
      none erroring at setup. (Current state at `9ce5548`: 76 passed, 12 errors.)
- [x] **The `environment` fixture still fails when imports resolve somewhere unintended.** The pin's
      purpose is preserved, not deleted: demonstrated by showing it rejects a wrong resolution, not
      merely that it now passes. A pin that can no longer fail is the same defect as the one being
      fixed. **Kept as a negative check in the suite, not a one-off demonstration** — this item exists
      because a pin that was once demonstrated working later stopped checking anything, silently.
- [x] **The `repo: agentic-mbse` rows (L-036/L-037) are parsed and checked, not skipped.** The
      companion root resolves to the main `agentic-mbse` checkout, where both row paths exist and
      all four claimed-removed symbols are in fact absent — verified 2026-08-15 — so the rows reach
      real verification. Acceptance is a **kept negative check**: a deliberately falsified removal
      claim on one of those rows must make the gate fail. A green run alone does not distinguish
      verified from skipped, which is the defect being fixed. Cheap to write:
      `check_removed_symbols` already accepts an injectable `repo_roots` (`:180-183`).
- [x] **A configured-but-missing repo root makes the gate exit nonzero** `[OWNER 2026-08-15]`.
      Checked once at the start of a `paths` run, before any row is walked, so it is a distinct
      check from the per-row rule that a deleted row path proves its own removal. **Gates `paths`
      mode only** — the mode this cleanup blinded. `replacements` keeps its documented partial-run
      behavior without the companion checkout (ceiling 6), per the Non-Goals mode boundary and the
      owner's stated consequence, which names `paths`. Acceptance is a regression check that points
      a root at a nonexistent directory and asserts a nonzero exit.

## Known Requirements

- **[NEED]** Scope is the fixes only (owner, 2026-08-15: *"just write a new /_my_spec JUST FOR THE
  FIXES"*). This item does not carry any self-binding, guidance, or model-migration work.
- **[HARD]** The worktrees `sysml-codegen-item7-rebuild` and `agentic-mbse-item7-rebuild` do not
  exist, and the content they carried is on `main` in each repo (verified byte-identical at the
  phase-D merge wave). A checked system fact.
- **[NEED]** They stay deleted — the owner directed the deletion on 2026-08-15 and it is settled, so
  recreating a worktree to satisfy a pin is not an available repair. *Owner policy, not a repo fact;
  graded separately from the `[HARD]` row above because its authority is a decision that could in
  principle be revisited, not a state of the world.*
- **[HARD]** The execution lane requires teax-simkit's dependencies (`pandas` among them), which
  this project's `.venv` does not provide, and the lane is excluded from the default pytest run
  (`pyproject.toml:46`).
- **[INFERRED]** `pytest -m execution` from the agentic venv with `PYTHONPATH` set is *a* verified
  working invocation, not the only valid one — the marker itself permits overriding `-m` entirely
  (`pyproject.toml:44-50`). The known-good recipe is recorded at
  `.project/CURRENT_WORK.md:193-203`; deliberately **not** frozen as a requirement.
- **[HARD]** `check_removed_symbols` skips any row whose path does not exist (`:192-193`). That skip
  is *correct row-level semantics* — a delete row's path is supposed to be gone, so absence is the
  expected proof — but it cannot distinguish that case from an entire configured checkout being
  missing, which is what produced the silent skips.
- **[HARD]** Pointing the companion root at the main `agentic-mbse` checkout restores real
  verification rather than papering over the skip: verified 2026-08-15 that both row paths exist
  there and that all four claimed-removed symbols (`extract_constraint_facts`, `ProfileResult`,
  `evaluate_profile`, `preflight`) are genuinely absent. The retirement content landed on `main`, so
  `main` is the correct root, not a substitute for one.
- **[NEED]** A configured-but-missing repo root exits nonzero, checked once at startup
  (owner, 2026-08-15). Rationale carried from the ledger's own reason for existing: the original
  Item 7 census failed because *"the gate accepted absence as proof of retirement"*
  (`.project/ledger/ledger-4a.md`), and this defect is that same class recurring inside the
  instrument built to prevent it.
- **[INFERRED]** Path pins should be derived from a known anchor (the test file's own repo root, the
  script's `REPO_ROOT`) rather than hardcoded host paths, so the next relocation does not break them
  again. Not stated by the owner; inferred from the fact that hardcoded absolute paths are precisely
  what failed here.

## Non-Goals

- **`scripts/archive/probe_constraint_profile_qualifier_drop.py`**, which also names the dead
  worktree. It is an archived one-off probe under `scripts/archive/` and is deliberately left alone.
- **Re-running or re-certifying the full suite.** This item restores two gates; it does not re-issue
  phase-D's acceptance numbers.
- **Any change to what the execution-lane tests assert about the product.** The channel set, the
  arithmetic, and the mutation checks are untouched — only the environment pin is in scope.
- **Redesigning the ledger CLI's output.** Out of scope: splitting the `paths` headline into
  verified / skipped counts is not required here, because the owner ruled the item stays limited to
  the pin repairs, the missing-root hard failure, and their regression checks
  `[OWNER 2026-08-15]` (spec-review L1-2 resolution). The idea is recorded as agent-grade at
  `product-lens.md` spec-F1 and stays challengeable there.
- **Checker modes other than `paths`.** `replacements`, `surface`, and `groups` are untouched, and
  all six entries in the checker's documented-ceilings list stay as written (the docstring's prose
  says "five ceilings" while numbering six — a drift this item does not adjudicate). Only the
  missing-root vacuity this cleanup introduced into `paths` is in scope.

## Open Questions / Deferred to design

- **Should the environment pin assert paths at all**, or assert a property that cannot rot — for
  instance that the resolved module is the one the current repo owns? Mechanism choice, and the one
  place this item still has real design latitude.

### Scope note on the ledger checker's ongoing value

Worth stating so implementation does not over-invest. The checker began as scaffolding — Gate 4A of
the cutover-recovery plan, now complete, accepted and archived — but the owner ruled the ledger
**living gate data** `[OWNER 2026-08-14]` when rehoming it to `.project/ledger/`, because future test
renames still sweep it. Its enduring job is that narrow one. There is no CI and no pre-commit hook in
this repo, so it is invoked by hand or by an agent following a runbook; it carries **54** tests in a
single file (verified by collection). Fix the gate properly, but do not build for an automation that
does not exist.

**Stated consequence of the approved startup hard-fail** `[OWNER 2026-08-15]`: `paths` becomes
unrunnable unless the `agentic-mbse` checkout sits beside this one. That is the intended trade — an
abstaining gate should not read as a passing gate — but it means the failure message is user-facing
and must be chosen deliberately: it should name the missing root and say the gate abstained rather
than that the ledger is wrong.

---

## Related Artifacts

- **Origin:** the phase-D cleanup recorded in `.project/CURRENT_WORK.md` (2026-08-15 top block) —
  worktree, branch, and venv deletion. This item is residue of that cleanup, not of any epic item.
- **Spec review:** `.project/active/dead-worktree-pins/spec-review.md` — verdict Revise; two owner
  resolutions (keep the item narrow; shrink the correction history) applied in this revision.
- **Product-lens ledger:** `.project/active/dead-worktree-pins/product-lens.md` — append-only;
  spec-F1's coverage-split disposition is superseded by the owner's L1-2 resolution, recorded there.
- **Sibling item:** `.project/active/self-binding-replacement/spec.md` — explicitly excludes this
  work in its Non-Goals and Change Record. The reverted repair attempt is preserved there as
  `reverted/codegen-gate-repairs.patch` and may be used as input, subject to review rather than
  inherited as correct.
- **Design/plan:** intentionally skipped for this low-complexity repair at owner direction
  `[OWNER 2026-08-15]`.

---

**Next Steps:** Close and archive this certified standalone item.

---

## Implementation Record (2026-08-15)

No design/plan stage — owner directed `/_my_implement` straight from the approved spec. The one
open question (paths vs unrottable property) was resolved in implementation: the pin asserts
anchor-derived trees, not host paths.

**Changes:**

- `scripts/check_ledger_4a.py` — `REPO_ROOTS["agentic-mbse"]` now derives from the script's own
  anchor (`REPO_ROOT.parent / "agentic-mbse"`); new `missing_repo_roots()`; the `paths` CLI branch
  abstains with exit 2 before walking any row when a configured checkout is missing, naming the
  root and saying the ledger is not wrong. One stale docstring phrase ("paired rebuild checkout")
  corrected; the six-ceiling list untouched.
- `tests/execution/environment_pins.py` (new) — stdlib-only `environment_pin_problems()` predicate;
  expected roots derived from the file's own location (`<repo>/src`, `<repo>/../agentic-mbse/src`).
  Pinning to `src` specifically rejects a stale site-packages copy under the repo's `.venv`.
- `tests/execution/test_fusion_tea_real_teax.py` — `environment` fixture asserts via the predicate;
  docstring no longer claims the rebuild worktrees.
- `tests/unit/test_environment_pins.py` (new, 5 tests) — kept negative checks in the default suite:
  correct resolution passes; wrong simkit / site-packages sysml_codegen / dead-worktree
  agentic_mbse each rejected. (This file deliberately names the dead-worktree path *as a wrong
  input* — a rejection case, not a pin.)
- `tests/unit/test_check_ledger_4a.py` — companion root pinned to the main checkout;
  configured roots exist on disk; `missing_repo_roots` names each absent checkout; `main(["paths"])`
  exits 2 with the abstention message and no problems line. The audit follow-up loads real rows
  L-036/L-037, falsifies each removal claim with a live declared symbol, and asserts the check
  fails; the older synthetic L-926 mechanism test remains as a separate unit case.

**Verification:**

- Execution lane from the main checkouts: **88 passed, 0 errors** (recorded invocation, agentic
  venv). First main-checkout reproduction of the full lane.
- `check_ledger_4a.py paths`: `304 rows checked, 0 problems`, exit 0 — with the companion rows now
  genuinely parsed (the committed-ledger unit test exercises the same path).
- Targeted unit files after audit fixes: 65 passed. Reference sweep: only the exempt archive probe, the two fixture
  JSONs, and the new negative test's wrong-input literal remain.
- Full default suite (licensed): **17 failed, 2078 passed, 34 skipped** — the 17 are byte-identical
  at clean HEAD (verified by stash + rerun) and ordering-dependent (each file passes alone):
  `test_report_precedence.py` (12), `test_fusion_tea_acceptance.py` (4),
  `test_output_schema_contract.py` (1). Pre-existing, not introduced or fixed here (Non-Goals:
  no re-certification); surfaced in CURRENT_WORK as an unowned finding.
- mypy not run: no `src/` changes. Two `F401` warnings in the execution test file pre-exist at HEAD.

**Audit response (2026-08-15, reverified and certified):** both findings were accepted and fixed.
SC4's kept falsification now targets the real rows: `tests/unit/test_check_ledger_4a.py::
test_falsifying_a_real_companion_row_makes_the_gate_fail` loads L-036 and L-037 from the committed
ledger, replaces each removal claim with a symbol the companion file still declares (picked from
the live surface), and asserts the gate fails — proving the committed rows reach the check, not
just a synthetic stand-in. The stale "either rebuild repo" contract wording in
`check_removed_symbols` is corrected. Checker suite after: 60 passed; both targeted files: 65 passed.
