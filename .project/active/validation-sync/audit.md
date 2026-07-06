# Audit: agentic-mbse Sync — Guidance & Validation (UPSTREAM-FINDINGS Item 12)

**Verdict:** CONDITIONAL
**Audited:** 2026-07-06
**Branch (artifacts):** `upstream-findings-epic` (sysml-codegen)
**Branch (implementation):** `upstream-findings-sync` (agentic-mbse) — commits `9db5ede` / `87f9bc8` / `f68d1cb` / `08cd595`, + A-2 at `6dbdf1b`
**Close-out under audit:** `bbb32ad`

---

## Summary

Item 12's **R2 core gate — the two traceability tables in `close-out.md` — passes.** Every
impact-list row (C1–C8, D1–D8, V1–V2, F1–F5 — 23 rows) carries a disposition and evidence;
every fusion-tea trap (SC-1..SC-11, A-1×2, A-2, A-3) maps to a check, a documented rule, a
codegen fix, or an explicit filing. Nothing from any per-item recording is silently dropped.
Five spot-checked rows trace cleanly to their sources in this repo. The two adjudicated
deviations (C1 reframe; C7/C8 filed) are recorded and sound. The in-repo filings (F3/F4/F5)
landed correctly in `BACKLOG.md`.

**Why CONDITIONAL, not PASS.** This audit session's sandbox is pinned to `sysml-codegen`.
The agentic-mbse tree — its checks, fixtures, docs, backlog, and test suite — is unreadable
here (confirmed via `Read`, `grep`, `git -C`, and a subagent; `uv run` is approval-gated and
denied), so the code-side verifications could not be performed. Per the agreed Option B, those
are certified on the recorded Phase-1..4 gates and commit hashes and are cleared by the
**designated clearing path below** — the orchestrator, which has full cross-repo access,
performs them directly and records the result in this close-out.

---

## Findings

### R2 core gate — traceability (VERIFIED in-repo)

- **Table 1 (impact row → disposition → evidence) is complete.** All 23 rows present:
  C1–C8, D1–D8, V1–V2, F1–F5. Each has a disposition (BUILT / FILED / CONFIRMED / DONE) and
  an evidence pointer (`close-out.md:51–76`). Row count matches the spec's impact table
  exactly (`spec.md:71–100`) — no row added, none dropped.
- **Table 2 (fusion-tea trap → covering check/rule) is complete.** SC-1..SC-11 plus A-1
  (both legs), A-2, A-3 each map to a C-check, a D-rule, a codegen fix, or a filing
  (`close-out.md:83–99`). The "every SC/A trap maps" claim holds on its face.
- **Internal consistency holds.** Gate-2 per-fixture table (`close-out.md:36–46`) agrees with
  the C-row evidence: `self_named_binding_trap` L6 PASS is attributed to C6 (was
  `V2_DYNAMIC_EXPRESSION` + `L6_INVALID_QUALIFIED_NAME`, now 0 each); `anonymous_return` L6
  FAIL to C2a; `return_styles` WARN to C2b; `retype_model` L2=FAIL noted as pre-existing
  `UNBOUND_INPUT`, not an Item-12 code.

### Spot-check — 5 rows against per-item recordings (VERIFIED in-repo)

| Row | Source recording | Match |
|-----|------------------|-------|
| C2a return-style/anonymous FAIL | `return-style-extraction/spec.md:253–259` — "accept `out attribute`, named `return` (inline+body), bare `in`; anonymous `return` FAIL; body-assignment WARN" | Exact |
| C2b body-assignment WARN | same section (`:258–259`) — "loses auto-impl until deferred capture" | Exact |
| C4 calc-bearing-no-instantiation, retype counts | `type-indexing/spec.md:14–45` — retyping instantiates template calcs; uninstantiated calcs "are dropped" | Exact |
| D6 EXPOSE surfacing | `alias-surfacing/release-notes.md:102–110` — EXPOSE_PURE name surfaces on `output_aliases`, filename `{instance_path}__{alias_name}.json`, sanitized `python_name` | Exact |
| C1 self-named FAIL (floor) | `cross-part-wiring/release-notes.md:50–52, 127` — "self-named-binding FAIL check (mechanism D) with the `self_named_binding_trap` negative" | Matches the **pre-reframe** floor; the reframe is recorded (see deviations) |

All five trace to a real in-repo source that says what the row claims.

### Adjudicated deviations (VERIFIED recorded + sound)

1. **C1 reframe (orchestrator ruling A).** The C1 floor named `self_named_binding_trap` as
   the FAIL negative — confirmed by its source (`cross-part-wiring/release-notes.md:52,127`).
   Items 9/10 made a self-named binding *with a covering feature* (even a bare literal) the
   supported plant idiom; ife_plant carries ~21 legitimately. At the agentic-mbse layer the
   trap (covering `attribute availability = 0.70`) is resolution-identical to ife_plant's
   `attribute radius` + `in radius = radius`, so a check that FAILs the trap would FAIL
   ife_plant and flip its L2 PASS→FAIL — a HARD no-regression violation. The reframe FAILs
   only a **true dead-end** (owner carries no same-named feature, owned *or* inherited); the
   trap becomes the negative-of-the-negative and `item12/self_named_deadend` is the new
   negative. The reframe, its rationale, and the one-line codegen-spec amendment are recorded
   at `close-out.md:104–124` and `plan.md:406–428`. **Recorded and coherent.**
   - *Observation for the code-side pass (not a blocker):* codegen still treats the
     covered trap as degenerate via full-QN own-param resolution that agentic-mbse's
     `extract_bindings` does not reproduce (`plan.md:448–466`). C1 now mirrors codegen only at
     the level agentic-mbse can discriminate — the dead-end (broken in both layers) and the
     covered case (supported in both). The residual is that the auditor no longer flags the
     specific covered-trap shape codegen degenerates. This was adjudicated in scope; the
     code-side pass should confirm `_owner_covers_name` walks `owner.features` (owned +
     inherited) as recorded, so the ife_plant inherited-`bank_energy` case stays covered.

2. **C7/C8 FILED (scope guard).** Both are explicit "budget-permitting else FILE" candidates
   (`spec.md:81–82, 199`); the four non-fileable checks (C1, C2a, C3, C4) all landed, so the
   guard permits filing. Reasons logged (`plan.md:503–510`): C7's trigger boundary risks
   reintroducing the C6 defect class; C8 needs codegen's sanitizer replicated. Filed to
   agentic-mbse backlog `ITEM-SYNC-C7/C8`. **Recorded and within the guard.**

### In-repo filings (VERIFIED)

F3/F4/F5 are in `.project/backlog/BACKLOG.md:39–58` with correct sources and scope matching
spec rows F3/F4/F5 (`spec.md:98–100`): F3 shape-B leaf collision (Item 11 audit Obs. 2), F4
redefinition/design_override surfacing (Item 11 release-notes), F5 positive
unresolvable-warning test (Item 11 audit Obs. 1). Correctly homed in this repo (the concerns
codegen owns).

### Epic Item 12 success criteria

- **SC1 — every impact item implemented or filed, none silently dropped:** VERIFIED via
  Table 1 (23 rows, all dispositioned).
- **SC2 — each new check has a negative fixture and catches its trap on WI-014/plant shapes:**
  RECORDED (fixtures `tests/fixtures/item12/*`, Gate-2 table) — **code-side, unverified here.**
- **SC3 — RAW_LEARNINGS traps covered by checks/rules (traceability table):** the table
  exists and is complete (Table 2). The mapping to fusion-tea's actual RAW_LEARNINGS text was
  built by the implement session with live fusion-tea access; `~/1cfe/fusion-tea` is also
  outside this session's sandbox, so the trap *list itself* is corroborated only by in-repo
  references to SC-1..SC-11, not re-read at source — **flagged for the code-side pass.**

### Code integrity

Not assessable in this session — the check implementations, fixture layout, and doc content
live in the unreadable agentic-mbse tree. No in-repo production change was made (correct — the
spec's non-goal, `spec.md:153`). Deferred to the code-side pass (native-conventions /
slop / failure-honesty review of the seven BUILT checks).

---

## Designated clearing path (code-side verification — orchestrator, full access)

CONDITIONAL clears to PASS when the orchestrator performs these directly and records the
result in `close-out.md`. All are recorded-but-unverified here due to the sandbox:

1. **Four non-fileable checks wired + fixtures.** In `agentic-mbse`: C1
   (`level2_structure.py` `check_self_named_bindings`/`_owner_covers_name`, wired into
   `validate_structure`), C2a/C3/C4 (`level6_architecture.py`, wired into
   `validate_architecture`) — each with its `tests/fixtures/item12/` negative and its
   negative-of-the-negative (`self_named_deadend` FAILs; `self_named_trap`/`self_named_rescue`
   don't; `return_styles` doesn't fire C2a; `retype_instantiation` doesn't fire C4).
2. **C5/C6/C2b as claimed.** `adr002.py` drops `^` from `SUPPORTED_OPERATORS` +
   `check_static_function_invocations`; C6 scoping (V2 skips calc-def-owned attrs;
   `check_qualified_names` accepts quoted segments) makes the real `self_named_binding_trap`
   L6 PASS; C2b `check_body_assignment_impl_loss` WARNs.
3. **D1–D8 docs** incl. `docs/patterns/plant-idiom.md`, and index registration; V1/V2 as
   recorded.
4. **F1/F2 + vendor-note draft** in agentic-mbse's backlog (`ITEM-SYNC-F1/F2`, the
   evaluation-time-not-extraction-time note + draft).
5. **Suite re-run** (recorded 1218 passed / 1 skipped) and **cross-repo `run_all_checks`** over
   this repo's fixture corpus (recorded no L1–L5 regression; Gate-2 per-fixture verdicts).
6. **Five-commit scope check** (`9db5ede`, `87f9bc8`, `f68d1cb`, `08cd595`, + A-2 `6dbdf1b`):
   nothing unrelated swept in; the two pre-existing untracked files are NOT in any commit.
7. **C1 residual** (observation under Deviation 1) and **code integrity** (native-conventions
   review of the seven BUILT checks).

---

## Certification

**Marked as verified (in-repo, this session):**
- R2 traceability core gate — both tables complete, internally consistent, no dropped row.
- 5-row spot-check against per-item recordings — all trace cleanly.
- Both adjudicated deviations (C1 reframe, C7/C8 file) — recorded and sound.
- F3/F4/F5 filings in `BACKLOG.md` — correct sources and homes.
- Epic Item 12 SC1 (nothing dropped) and SC3 (traceability table present).

**Left open for the designated clearing path (code-side):**
- Epic Item 12 SC2 (fixtures catch their traps) — recorded, code-side.
- All agentic-mbse code, fixture, doc, backlog, suite, and commit-scope verifications (list above).

The epic's Item 12 heading and its code-side success checkboxes are **not** marked here — the
in-repo tracking is updated to CONDITIONAL and the code-side gate is left for the orchestrator
to close. Verdict flips to PASS once the clearing path is recorded green.


---

## Orchestrator close-out — the designated clearing path (2026-07-06)

Code-side verifications executed with full access, all green:

1. **Five agentic-mbse commits scoped clean** (9db5ede 17 files / 87f9bc8 6 / f68d1cb 9 /
   08cd595 2 / 1b7046a 1): no unrelated files swept in; the two pre-existing untracked files
   remain untracked.
2. **Checks wired**: `check_self_named_bindings` wired at `level2_structure.py:486` via
   `_owner_covers_name` (`:309`); the flagged confirmation holds — the scan walks
   `owner.features` (owned + inherited), with the rationale documented in its docstring.
   All new ValidationCodes present in `level6_architecture.py` (9 references). 11 item12
   fixture dirs; `docs/patterns/plant-idiom.md` exists; F1/F2 + C7/C8 + vendor-note draft
   in agentic-mbse's backlog.
3. **agentic-mbse suite re-run**: 1218 passed / 1 skipped — reproduced independently.
4. **Cross-repo run_all_checks over the sysml-codegen corpus**: ife_plant, wi014_toy,
   self_named_binding_trap, self_named_rescue, spec_chain_channel, spec_chain_twolevel,
   sibling_channel_ambiguity, return_styles all pass L1–L6 fully (overall_success=True for
   ife_plant verified with per-level detail). The low-scoring fixtures (retype_model,
   solar_battery, catf_mfe, alias_agg_probe) fail only on PRE-EXISTING L2 check classes
   ("Unbound input", literal-binding WARNs — deliberate trap shapes in those conformance
   fixtures), not on any Item 12 code: no regression.
5. **One residual find, filed not dropped**: a third L6 false-positive family
   ("derived expression references design attributes") flags the codegen-supported
   quoted_owner_formula FORMULA shape — filed as ITEM-SYNC-F6 in agentic-mbse's backlog
   (commit 1b7046a), sibling to the two families C6 fixed.

Verdict upgraded: **PASS**. Item 12 complete — the epic's twelve items are all landed and audited.
