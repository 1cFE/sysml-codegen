# Audit: Lifecycle Item 6 — Public Documentation and F1 Evidence Reconciliation

**Verdict:** Certify
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic
**Commit:** f917787 (codegen), db23719 (TEAx)

---

## Summary

Light reconciliation audit; every one of the seven requested areas reproduced first-hand.
All eight STALE corrections (S1–S8) now make a claim that is TRUE against landed code. The
one production-behavior change (explicit invalid `TEAX_SIMKIT_PATH`) is genuinely RED-first
and correct. F1 evidence names the right commit, the 15-test cluster passes, and the
`OUTPUT_WRITE` limitation is recorded honestly. Gates match the claim exactly (3064/0, mypy
72, no baseline bytes). No blocking findings; no corrections needed.

## Findings

### Plan completion (§5 checklist)

All six folded-plan boxes verified:

- Three inventory sweeps with per-claim citations — the S1–S8 citations all resolve (below).
- RED-first `TEAX_SIMKIT_PATH` change — reproduced RED and GREEN (below).
- Eight STALE claims corrected with citations — all TRUE against landed code.
- F1 audit reference `927a9e1` → `d545701` — landed at TEAx `db23719` (1-line change).
- PR drafts staged (no push) — both present, accurate.
- Gates green — reproduced (3064/0, mypy 72, ruff not re-run this pass).

### Spec conformance

**S1–S8 corrections — every landed claim is TRUE.**

- S1 — doc 27:37 now reads "Current: **5**" with the `snapshot/__init__.py:28` cite;
  `SNAPSHOT_FORMAT_VERSION = 5` confirmed.
- S2 — doc 27 `source_file` block now describes the v5 `root-N/<relpath>` portable referent,
  loader reconstructs no absolute path (`_validate_source_referents`). Matches
  `snapshot/__init__.py:20-27` and the code.
- S3 — doc 27 now carries a "Format migrations (v2 → v5)" record; no frozen-v3 language.
- S4 — doc 27:136-137 reads "executable-profile v4 behavior" with the
  `PROFILE_SEMANTIC_VERSION = "executable-profile/v4"` cite; `_upstream_pins.py:33` confirmed.
- S5 — doc 27:142 reads floor `agentic-mbse>=0.1.2` (`pyproject.toml:24`); "pre-v3 companion"
  replaced with "predating the pinned profile."
- S6 — verification-matrix REQ-SNAP-09 reads "(current: 5) … no cross-version coexistence."
- S7/S8 — `predicate_compiler.py:152,203` both interpolate `{PROFILE_SEMANTIC_VERSION}`; no
  literal remains. Pinning test `test_predicate_compiler.py:384` matches
  `r"not admitted by executable-profile/v\d"` — regex-hardened, cannot re-drift to a fixed
  version. `grep executable-profile/v3 src/ docs/ tests/` returns empty.

Disambiguation for the record: "package 0.1.2" is the *agentic-mbse dependency floor* (S5).
The codegen package's own version is `0.1.0` (`pyproject.toml:7`), which evidence §6 correctly
states is unchanged. Both are accurate; no stale claim conflates them.

**`TEAX_SIMKIT_PATH` (evidence §1) — verified.** The helper makes an explicitly-set path
authoritative: `discover_teax_simkit` (`tests/helpers/teax_discovery.py:26-31`) returns
`_require_simkit_root` on the explicit path with **no** sibling fallback; the sibling is tried
only when no explicit path is set. RED reproduced against the parent helper (`f917787^`): the
new test `test_explicit_invalid_path_fails_instead_of_discovering_the_sibling` fails with
"DID NOT RAISE RuntimeError"; the pre-fix tree was restored clean afterward. GREEN at HEAD:
6 passed, including the unchanged unset/default and symlink-loop/expanduser tests. No `src/`
caller (grep confirms tests-only scope).

**F1 (spec §4, evidence §2) — verified.**

- `927a9e1` touches only `docs/teax-study-explainer.html` (`git show --stat`) — provably lacks
  the F1 change. `d545701` carries `pipeline_executor.py`, `evaluator.py`, the F1 tests, and
  the audit — the correct commit.
- TEAx `db23719` corrects `gap-close-f1-normalization/audit.md:6` to `d545701` (1 insertion,
  1 deletion). Sibling `design.md:9` correctly left at "Base commit: 927a9e1" (written against
  the parent).
- 15-test F1 cluster reproduced GREEN (`15 passed`) via the `../../.venv/bin/python` env.
- `OUTPUT_WRITE` limitation honest: `failure.py:23` defines it; `evaluator.py` sets only
  `MODULE_EXECUTION` (`:62`) and `PREPARATION` (`:113,:185`) — never `OUTPUT_WRITE`. The
  Item 11 ownership is stated, not reimplemented.

**"Already accurate" list (§3b) — two spot-checks hold.**

- V11 settled branch: `extend_graph_with_constraints` docstring
  (`analysis/constraint_lowering.py:1470`) states it runs no V11 coverage check; the only
  *invoking* caller of `collect_uncovered_params` is the final gate `cli/__init__.py:278`
  (`_reconcile_params_coverage`). No active extension-time check exists. Accurate.
- Embedded catalog / CE-F1: no `constraint_catalog.json` emission in `src/` (grep empty) —
  the standalone catalog is correctly flagged open, not landed. Accurate.

**Success criteria (§6) — all four met:** every correction-register claim agrees with landed
code; F1 names `d545701` and compares exact report content; invalid explicit simkit path never
falls through (RED→GREEN); no stale `executable-profile/v3` literal remains.

### Design conformance (correction law)

The two surfaced gaps (§3c) are recorded as decisions, not instructions to future agents.
G1 (undocumented diagnostic severity) and G2 (no Item-5 verification-matrix row) each state
what is landed, why nothing is STALE, and whose territory the backfill is (Item 4 / Item 13) —
ownership records, not "future agents must" imperatives. Compliant with the correction law.
No "this used to say X" prose found in the doc amendments.

### Code integrity

No slop or failure-honesty issues. The `TEAX_SIMKIT_PATH` change *removes* a silent fallback
(the invalid-explicit-path → sibling rescue) rather than adding one — policy (explicit is
authoritative) at the call site, mechanical resolve-and-check in `_require_simkit_root`. The
single-sourcing of S7/S8 deletes duplicate version literals. Both are the right direction.

---

## Certification

Checked and reproduced first-hand: S1–S8 doc/code claims against landed code; the
`TEAX_SIMKIT_PATH` RED (parent helper) and GREEN (HEAD, 6 passed); F1 commit reconciliation,
the 15-test cluster (15 passed), and the `OUTPUT_WRITE` honesty; the two "already accurate"
spot-checks (V11, catalog); the two surfaced gaps' phrasing; full suite **3064 passed / 44
skipped / 0 failed** (license sourced, no bare license skips); mypy **72 errors** (baseline);
no fixture/`baseline_outputs` bytes in the commit. Working tree clean but for untracked
`.claude/projects/`.

Spec §6 criteria marked; epic Item 6 rows checked below.

**Not checked:** ruff (`check`/`format`) not re-run this pass — evidence claims clean and the
touched surface is docs + 3 small code files; the full agentic-mbse suite (1811) not re-run
(this item does not move the mbse pin — Item 4 did); the actual PR update/push (Item 13's, out
of scope); the F1 cluster's internal report-content assertions were run green but not read
line-by-line. The v5/profile-v4/floor-0.1.2 values themselves are inherited from certified
Items 4/5 and verified only for doc-agreement here, not re-derived.
