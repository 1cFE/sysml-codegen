# Release Readiness — CONSTRAINT-EXEC Lifecycle (register row 17, composed public proof)

**Status:** Composed proof complete — **41/41** Appendix C cells pass at the pinned set. Items
1–12 certified; Item 13 (this composed proof) complete. **Merge pending human.** No release/merge
is claimed beyond the evidence recorded here and in the evidence-coordinate register.
**Date:** 2026-07-20.
**Authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
(Appendix C matrix); evidence in `evidence-coordinate-register.md` (this directory).

---

## 1. The pinned revision set (final commits, all five repos)

| Repo | Final commit | Branch | Delivery path |
|---|---|---|---|
| sysml-codegen | pin `7526665` (certified src); branch tip **`d7ad714`** | `constraint-exec-epic` | **push PR #9** (SECOND) |
| agentic-mbse | **`4c18d61`** | `constraint-exec-epic` | **push PR #11** (FIRST) — see §7 caveat |
| teax | **`c342b10`** | `constraint-exec-epic` | **push + update PR #3** (independent) |
| fusion-tea | **`be1ee7c0`** | `item8-fusion-embedded-catalog` | **STAYS LOCAL** (human delivery decision) |
| stellarator | pin `342cc799` | `feat/stellarator-mbse-demo` | **STAYS LOCAL** (human delivery decision) |

- The codegen **src surface is byte-identical to the pin `7526665`** (`git diff 7526665 d7ad714 --
  src tests` is empty); `d7ad714` adds only `.project/` docs + the Item-13 fixtures. The evidence
  pin is `7526665`; the branch tip carrying the docs/fixtures is `d7ad714`.
- Locks: frozen `uv` resolution of the pinned triple; profile lock `executable-profile/v4`;
  companion/runtime-contract versions single-sourced and fail-closed on skew (invariants 14, 39).
  Re-asserted at execution: sysml-codegen `0.1.0`, agentic-mbse `0.1.2` (per Item 0 evidence).

---

## 2. Register summary — 41/41 with the rerun / compose split

Classification (strict rule — the chain advanced ~97 commits; every non-Item-12 surface certified
at a codegen rev earlier than the pin): **inherit 0 · rerun 22 · compose 19 · total 41.**

- **Reruns (22): all PASS, 0 findings, 0 unexpected skips.** Codegen-internal cases re-observed on
  `7526665` (license-active, `--frozen`, `-rs` clean). Cases 3, 8, 9, 10, 11, 12, 13, 14, 16, 17,
  19, 20, 21, 22, 23, 24, 26, 27, 32, 37, 38, 39. (Case 37 fact-consumer tests in agentic-mbse
  `4c18d61`.)
- **Composes (19): all PASS.** Cases 1, 2, 4, 5, 6, 7, 15, 18, 25, 28, 29, 30, 31, 33, 34, 35, 36,
  40, 41 — via the sealed artifact thread, the codegen execution lane (17 passed), the teax suite
  (310 passed), and the two consumer acceptances.
  - **Case 18** (definition-owned assert through redefining usage): CLOSED by fixture-shape
    correction to the contract row's canonical package-level form — Item 2's resolver was correct;
    the Stage-2 fixture over-built the row. End-to-end verdict now runs (satisfied at `80.0`,
    flips to violated at `120.0`). A **general** supplied-value gap (nesting-only) was isolated and
    filed — see §5.
  - **Case 40** (IFE grid): the IFE package regenerates **byte-identical** at pinned codegen; the
    stale breadth harness was migrated (test-infra, fusion-tea `be1ee7c0`) and the true
    2,301-point (η×G) grid runs (anchor B LCOE `$68.6902` exact; anchors A/B/C byte-exact).
  - **Case 41** (stellarator): five verdicts satisfied, six anchors bit-exact vs oracle (reldev
    0.00e+00), single-pass / no bridge, at pin `342cc799`.

The **sealed artifact thread** (epic core) was demonstrated on `constraint_multi_instance`:
generate live A / live B (two independent absolute roots) → seal → trusted-load → prepared +
file-backed evaluate → persist → resume/query, same artifact identity throughout (fingerprints
identical across roots; seal verify strict PASS both).

---

## 3. Negative mutations (16) and full-tree byte checks (6)

**Mutations N1–N16: all fail at their intended boundary.** N15 was executed as a real source
mutation (restore the deleted Gate B `collect_uncovered_params` V11 re-check → exactly **5 of 14**
gate-b tests flip red → reverted, tree clean — the deletion-persistence proof). N1–N14 and N16 are
input-level mutations encoded in passing boundary tests (across the reruns, teax, and execution
lanes).

**Byte checks: 6/6 PASS.**
1. Live A vs Live B (two independent roots) — byte-identical (forbids same-machine path cancellation).
2. Live vs relocated snapshot — full-tree byte-identical (rerun case 21).
3. Absolute-path scan — no checkout-absolute path in the generated tree.
4. Constraint-free byte stability — `test_baselines` inside the full licensed suite.
5. IFE unchanged anchors — package byte-identical at pin; anchors A/B/C byte-exact.
6. Stellarator unchanged numerics — six anchors bit-exact.

---

## 4. Quality-gate matrix (at the pinned set)

| Gate | Result | Note |
|---|---|---|
| Full licensed suite (codegen `7526665`) | **3115 passed, 47 skipped** | exact Item-12 baseline |
| Focused (constraint lifecycle) | green | subset of the full run |
| Optimized (`PYTHONOPTIMIZE=1`) | **2 failed, 3113 passed** | the 2 pre-existing Item-4 `-O` failures — baseline, see §5 |
| Lint (`ruff check src/`) | clean | config-deprecation warning only |
| Format (`ruff format --check src/`) | 22 src files would reformat | **pre-existing pin baseline** (src == pin) — see §5 |
| Type (`mypy src/`) | 72 errors / 17 files | **pre-existing pin baseline** (mypy-zero-new gate) — see §5 |
| Fixture diff review | only the Item-13 fixtures | no `captured_at` churn |
| agentic-mbse companion (`4c18d61`) | **344 passed** | profile/skew/facts/version gates |
| teax (`c342b10`) | **310 passed, 0 failed** | study/durability/immutability/identity |
| fusion-tea consumer (`2422e715` code; harness `be1ee7c0`) | PASS | anchors + 2,301 grid |
| stellarator consumer (`342cc799`) | PASS | five verdicts + six anchors |

---

## 5. Honest remaining-state (open-adjacent, not certification blockers)

None of the following block the 41/41 composed proof; all are recorded so the merge decision is
made with eyes open.

- **`[NESTED-OCCURRENCE-OVERRIDE]` general gap (filed, `BACKLOG.md`).** A `:>>` design-override on a
  usage nested inside an *instantiated* part def is captured **definition-relative** while demand
  resolves **occurrence-relative**, so the supplied-value materializer never matches the literal
  (0 applied — both the calc binding and the constraint actual). Affects nested shapes only; the
  canonical flat plant-idiom resolves correctly. **Owner: the Item-10 occurrence-materialization
  family.** Reproducible probe: `tests/fixtures/nested_occurrence_override_probe/` (expected to
  halt; PROVENANCE pins the verbatim coordinate). Surfaced by the case-18 addendum; not a row-18
  requirement.
- **Pre-existing stale-baseline class (`deep_cross_scope` + `plant_values`, since Item 4).** These
  baselines reproduce their divergence on the parent commit too, so they never block a
  byte-identity gate; both still need an owner. (Memory `deep-cross-scope-stale-baseline`.)
- **Two pre-existing optimized-suite (`-O`) failures.** The accepted Item-4 baseline ("2 failed,
  3113 passed, exactly the two named"). Recorded, not a regression.
- **`ruff format` / `mypy` pre-existing baselines.** `ruff format --check src` reports 22 files and
  `mypy src` reports 72 errors — but the codegen src is **byte-identical to the pin `7526665`**, so
  these are the exact state Item 12 certified against. The maintained gates are `ruff check`
  (clean) and **mypy zero-new** (satisfied: no src change). The register's earlier "src clean"
  phrasing overstates the raw `ruff format`/`mypy` state; this is the accurate version.

---

## 6. Required merge order and its mechanical reason

**agentic-mbse PR #11 merges FIRST, then sysml-codegen PR #9. teax PR #3 is independent;
fusion-tea / stellarator stay local.**

- **Why #11 before #9 (load-bearing, not convention):** sysml-codegen pins the upstream schema/
  profile version strings in `sysml_codegen/_upstream_pins.py`, and `tests/conformance/test_upstream_pins.py`
  asserts each equals the value **imported from the installed `agentic_mbse`**. If #9 merged to
  codegen `main` before #11, codegen `main` would import the *old* agentic-mbse from `main` (old
  schema/profile versions) while pinning the *new* `constraint-facts/v2` / `executable-profile/v4`
  → `test_upstream_pins` fails on `main`. Merging #11 first makes the new upstream versions present
  before the downstream pin lands. (This is the same guard, now version-string-based; the earlier
  `executable-profile/v3` runtime-pin variant is superseded by v4.)

---

## 7. Push / delivery state (this session)

See §8 for exact results. Caveats the human must weigh before merge:

- **agentic-mbse `4c18d61` ancestry includes the `4ed2a07` "modeling workflow orchestrator"
  commit** (a separate workstream). Item 0 evidence records it "remains in the candidate by owner
  direction"; the earlier pr-wave memory (2026-07-18) flagged it "deliberately NOT pushed." `4c18d61`
  is a fast-forward descendant of the current PR-#11 head, but pushing it necessarily brings
  `4ed2a07` into PR #11 (it is in the pin's ancestry — push-by-ref cannot exclude an ancestor).
  This tension is surfaced, not silently resolved.
- **teax** remote is SSH `git@github.com:rwestwood89/teax.git`; no SSH key in sessions — push via
  HTTPS (`gh` is authenticated over HTTPS).
- **fusion-tea** (`be1ee7c0`) and **stellarator** (`342cc799`) branches **stay local** — their
  repos' delivery path was not epic-authorized for push; recorded here as the human's decision.

---

## 8. Push results (2026-07-20)

All three epic-authorized pushes succeeded as **fast-forwards** (no force); PR descriptions
refreshed to final and a final-state comment added to each.

| Repo | PR | Push | Body | Comment |
|---|---|---|---|---|
| agentic-mbse (FIRST) | #11 (1cFE/agentic-mbse) | `54a95d2..4c18d61` ✓ | updated | added (with `4ed2a07` ancestry flag) |
| sysml-codegen (SECOND) | #9 (1cFE/sysml-codegen) | `512786c..d7ad714` ✓ | updated | added |
| teax (independent) | #3 (rwestwood89/teax) | `927a9e1..c342b10` ✓ (HTTPS) | — | added |

- No foreign commits entered codegen #9 (all `origin..HEAD` commits are constraint-lifecycle
  items 9–13). agentic #11 carries `4ed2a07` in `4c18d61`'s ancestry — pushed per Item 0 owner
  direction, flagged in the PR comment for the reviewer.
- **fusion-tea** (`be1ee7c0`, `item8-fusion-embedded-catalog`) and **stellarator** (`342cc799`,
  `feat/stellarator-mbse-demo`) branches stay **local** — human delivery decision.
- **Merge stays human**, in order: #11 → #9 (teax #3 independent).
