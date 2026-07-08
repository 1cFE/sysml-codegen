# Audit: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Verdict:** PASS-WITH-NOTES
**Audited:** 2026-07-06
**Branch:** truth-debt-epic
**Commit:** c6a323e
**Epic:** TRUTH-DEBT, Item 1 (SC-A, SC-G; R1–R4)

---

## Summary

The cutover is delivered as specified and designed. The live aggregation path runs through
`resolve_input(AGG_STRATEGIES)` via the `_build_agg_input_source` choke-point helper; the old
channel-only function, its three inline fallbacks, and Strategy D are gone; Strategy E is added;
the `param_groups` typing is untangled and both `type: ignore`s are cleared. Every [HARD]
requirement, INV, and key decision (D1–D5) is realized in the code as written. The byte-identity
claim is the strongest single result: **zero fixture files changed across the entire implementation
range** (ba3bca4..HEAD), including the cutover and byte-identity commits — the cutover provably
altered no generated output.

The notes are not defects. **Execution is sandbox-blocked** here (pytest / mypy / ruff are all
approval-gated and refused), so the gate-count legs (`2072/4/5`, ruff 17, mypy 97) and the
required mutation spot-check are **static-only** — verified by reading code, tests, and git
history, not by running them. One cosmetic test-assertion gap is noted below. Nothing found
blocks certification; the open items are auditor-execution limits, honestly bounded.

---

## Findings

### Plan completion (Phases 0–6)

All seven phases verified against code and git. Highlights:

- **Phase 0 (re-verify):** the plan records live line numbers and the reproduced D4 mypy errors
  verbatim; consistent with the current tree.
- **Phase 1 (value-half):** `input_resolver.py:281` mints `param_name = ref.replace(".", "_")`
  (D1 value half, INV-1). Strategy E `DirectChannelConstruction` (`:201`) is dotted-ref-only and
  gated on `canonical_channels` (B3 no-op design). Helper `_build_agg_input_source` present
  (`graph_builder.py:1252`).
- **Phase 2 (gates before rewire):** git-confirmed. At P2 (`32626a7`) the old function still
  existed in src **and** the old-comparand test `test_m3_full_inputsource_parity` called it. This
  is the load-bearing INV-3 ordering.
- **Phase 3 (cutover, one commit):** at P3 (`58adf4d`) `-def _resolve_aggregation_input_channel`
  and the old-comparand test are deleted **in the same commit** — exactly the atomic cutover the
  design required. Strategy D removed from src entirely.
- **Phase 4 (byte-identity):** no fixture churn (see Spec conformance SC-4). The orthogonal
  `deep_cross_scope_probe` diff is disclosed honestly in the plan, root-caused to a pre-existing
  non-aggregation stale baseline (reproduces on the parent commit), reverted, and memory-filed.
- **Phase 5 (typing):** no `type: ignore` remains in `graph_builder.py`; loop variable renamed to
  `dg` (`:327`); orphan `_group_entry_points_via_deriver` and dead Step-5 call deleted. The plan
  honestly records the B4 mechanism correction (below).
- **Phase 6 (docs/matrix):** IR rows re-pinned; matrix recounts cleanly; docs carry only
  historical "deleted" mentions.

No placeholder code, TODO, FIXME, or `NotImplementedError` in the touched source
(`graph_builder.py`, `input_resolver.py`) — grep clean.

### Spec conformance

- **SC-1 — cutover / deletions — MET.** `_build_agg_input_source` (`graph_builder.py:1252`) wraps
  `resolve_input(ref, ctx, AGG_STRATEGIES)`; called at the SumTerm (`:1393`) and SingletonTerm
  (`:1452`) sites. `_resolve_aggregation_input_channel` deleted (src grep: only a historical
  docstring at `input_resolver.py:6`; `__all__` export gone). The two inline `else:` blocks are
  collapsed into the helper; LocalTerm keeps its own simpler fallback (D5).
- **SC-2 — fallback reconciled (M4) — MET.** The helper owns every side effect the M4 target
  named: part-usage-prefixed EP QN via `resolve_input`'s reconciled key (INV-1); literal-default
  lookup via `_find_literal_redefinition`; register/dedup guard (`ep_qn not in entry_points and
  ep_qn not in new_entry_points`, `:1303`); literal-default backfill (`:1312-1323`);
  `param_group` via `group_deriver.classify` and `DESIGN_ATTRIBUTE` typing; and the load-bearing
  `MANUAL_REQUIRED` signal returned as `manual_required` and applied at both call sites
  (`:1398-1403`, `:1457-1462`) — INV-2.
- **SC-3 — parity gate over full `InputSource`, green before rewire — MET (static).** The M3 gate
  compared the full `InputSource` (old-comparand half, P2). Confirmed by git ordering; the
  permanent new-side assertion survives (below).
- **SC-4 — aggregation baseline byte-identical — MET (git, strongest).**
  `git diff --stat ba3bca4 HEAD -- tests/fixtures/` is **empty**; per-commit checks on the cutover
  (`58adf4d`) and byte-identity (`0e85044`) commits show zero baseline files touched. Zero churn
  is literally true at the git level — not just aggregation baselines but every fixture.
- **SC-5 — Strategy D removed — MET.** `DesignAttributeLookup` absent from src; `AGG_STRATEGIES =
  [A, C, B, E]` (`input_resolver.py:228-233`); docstring gone.
- **SC-6 — IR matrix + docs move with code (R1) — MET.** REQ-IR-05/07 pin the live `[A,C,B,E]`
  path and drop "not-yet-wired" (`verification-matrix.md:288-289`); docs 03/04/05/24 carry only
  historical "deleted" narrative; doc-24 strategy chain updated D→E (close-out `c6a323e`).
- **SC-7 — param_groups untangled, both ignores cleared — MET.** Loop-variable split (`dg` at
  `:327`); no `type: ignore` in the file; dead Step-5 + orphan deleted (D4b).
- **SC-8 / gate ceilings — MET (static-only).** See Note 1 — counts not independently runnable.

Epic SC-A and SC-G (epic `epic_truth_debt.md:59`, `:75`) both map cleanly onto the above.

**[HARD] requirements** — all realized: M4 reconciliation (incl. `MANUAL_REQUIRED`); full-
`InputSource` gate green-before-rewire; R3 byte-identity (aggregation as the hard bar); R4
verify-then-fix (Phase 0 reproduced the mypy error verbatim before the fix); gate ceilings
(static-only); R1 docs-move-with-code.

**Non-goals respected:** no Strategy D capability, no schema change, no multi-hop (Item 2) work,
no rewrite of the 22 skipifs / Strategy B / parity suite.

### Design conformance

Implementation follows the design precisely.

- **D1 (pure resolver + choke-point helper) — followed.** `resolve_input` keeps its `(ref, ctx,
  strategies)` signature (INV-5); the helper owns the side effects.
- **D2 (M3 two halves) — followed.** `test_m3_reconciled_ep_key_survives`
  (`test_input_resolver.py:837`) survives as the permanent new-side EP-key guard with a
  `checked > 0` vacuity guard; the old-comparand half was deleted at cutover.
- **D3 (Strategy E in shared list) — followed** (`:232`).
- **D4 / D4b (loop-var rename; dead Step-5 delete) — followed** (`:327`; orphan gone).
- **D5 (LocalTerm `module_output`-only reroute guard) — followed.** `graph_builder.py:1499` takes
  the alias channel **only** when `alias_resolved.source_type == "module_output"`, else falls
  through to LocalTerm's own `{module_eqn}__{attribute_name}` fallback (`:1507`). The reroute pin
  `TestLocalTermExposeAliasReroutePin` (`:900`) survives with a `channel_hits > 0` vacuity guard.
- **INV-7 (`ctx.module_eqn == agg.module_eqn`) — honored** (`:1382`).
- **Minor 4 (dotless SingletonTerm) — honored.** `literal_lookup_key=None` skips the lookup
  (`:1447-1450`, helper `:1295`).

**Deviations — all recorded honestly in the plan, none material:**
- M3 new-side and reroute pin scoped to `solar_battery_model` (issue22's agg inputs all resolve to
  channels → vacuous new-side; `alias_agg_probe` carries no EXPOSE_PURE attrs). Disclosed in Phase
  2; the vacuity guards make the scoping safe.
- **B4 mechanism correction:** the design claimed `derive_groups_filtered` does not reach
  `derive_groups()`; it does (`parameter_groups.py:575`). The plan (Phase 5 DEVIATION) records
  this and shows the *conclusion* still holds — Step 6.6 fires the non-float warning independently,
  Step-5's was a duplicate, deletion loses nothing. Correct call.

### Code integrity

No slop or failure-honesty issues.

- The helper's contract is readable from its signature and returns an explicit
  `(InputSource, manual_required)` tuple — no sentinel-mode god function. Policy (`MANUAL_REQUIRED`)
  lives at the call site, not buried in the helper.
- No broad `except`, no backwards-compat shim, no optional-parameter-papering. The one optional
  parameter (`literal_lookup_key: … | None`) is a real domain case (dotless SingletonTerm), not a
  missing-data cover, and is documented.
- Self-reference guard and fallback in `resolve_input` raise nothing and return typed results by
  design (REQ-IR-01) — intentional, not a silent-fallback smell.

**Finding F1 (low / cosmetic) — `test_input_resolver.py:990-994`.**
`test_unresolved_no_default_term_is_manual_required` second leg asserts `src2.source_type ==
"module_output"` but does not assert `manual2 is False`, though the docstring says "A resolved term
returns manual_required=False." Structurally harmless — the helper returns `(resolved, False)` for
every `module_output` result (`graph_builder.py:1287`), so `module_output` implies `manual=False`.
Recommend adding `assert manual2 is False` so the test asserts the intent it states. Not blocking.

---

## Notes (auditor-execution limits — not defects)

**Note 1 — Gate counts are static-only.** pytest, mypy, and ruff are all approval-gated and
refused in this sandbox, so the claimed `2072 passed / 4 skipped / 5 xfailed`, `ruff 17`, `mypy 97`
could **not** be independently re-run. Static evidence is consistent with the claims: both
`type: ignore`s and the orphan function are gone (mypy dropping 104→97 is plausible: −2 cleared
ignores, −2 from removed unresolved-symbol lines in the deleted orphan/Step-5, plus the −3 the plan
attributes to Phase 3 deletions); no new lint-triggering constructs in the touched files. The
full-suite-green and count legs rest on the implementer's + orchestrator's runs, not the auditor's.

**Note 2 — Mutation spot-check is static-only.** The requested "mutate production code, confirm the
parity test fails" check could not be executed (same sandbox block). Static-mutation reasoning:
reverting `input_resolver.py:281` to the old leaf-only key (`ref.rsplit(".",1)[-1]`) would, for a
multi-dot ref such as `permitting.raw_material_cost`, make `_build_agg_input_source` return
`…__raw_material_cost`, while `test_m3_reconciled_ep_key_survives` asserts
`f"{agg.module_eqn}__{ref.replace('.','_')}"` = `…__permitting_raw_material_cost` — the assertion
(`:865-867`) would fail. The test is therefore genuinely sensitive to the reconciliation, not
vacuous (and carries its own `checked > 0` guard). This is reasoned, not executed.

**Note 3 — Matrix recount (R1), from rows.** PASS status cells = 249; UNTESTED = 4; no other status
tokens; 30 families. 249 + 4 = 253 = the summary block's Total. **No drift** in the authoritative
counts (memory: `verification-matrix-drift-modes`). The 254 unique `REQ-XXX-NN` tokens vs 253 rows
is cross-reference noise — UNTESTED notes cite other REQ IDs (e.g. REQ-RES-08 cites REQ-IR-07 /
REQ-DRA-04), inflating the distinct-ID count above the row count. Every row carries a status.

---

## Certification

Checked and verified (static + git; execution sandbox-blocked):

- Live path runs `resolve_input(AGG_STRATEGIES)` via `_build_agg_input_source`; old function + 3
  inline fallbacks + Strategy D deleted; Strategy E added — **code-verified**.
- Parity gates green before the cutover; old-comparand half + old function deleted atomically in
  P3; permanent new-side EP-key assertion, LocalTerm reroute pin, and MANUAL_REQUIRED test all
  survive with vacuity guards — **git + code-verified**.
- Aggregation (and every) baseline byte-identical — **git-verified, zero churn**.
- `param_groups` loop-var rename clears both ignores; orphan + dead Step-5 deleted — **code-verified**.
- IR matrix rows + docs 03/04/05/24 pin the live path; no surviving live stale-claim; matrix
  recounts from rows with no drift — **code-verified**.

Open (not defects): gate counts (`2072/4/5`, ruff 17, mypy 97) and the mutation spot-check are
**static-only** — not independently executed here (Notes 1–2). One cosmetic test-assertion gap
(F1). All plan deviations are disclosed honestly.

Recommend flipping SC-A and SC-G in the epic and marking the plan phases certified. The one caveat
to carry forward: a machine with execution access should re-run the full gate suite once to convert
Notes 1–2 from static-only to executed — the code and git evidence make green the expected outcome,
but the auditor did not run it.

ARTIFACT: .project/active/f4-cutover/audit.md

---

## Orchestrator addendum (post-audit, live execution)

The three notes are closed with live evidence (the orchestrator has execution access):

1. **Gate counts re-run live**: 2072 passed / 4 skipped / 5 xfailed; ruff 17; mypy 97.
   Matches the plan's claims exactly.
2. **Mutation spot-check executed**: `input_resolver.py:281` key regressed to leaf-only
   (`ref.rsplit(".", 1)[-1]`) → `test_m3_reconciled_ep_key_survives[solar_battery_model]`
   FAILS on the exact divergent key (`…__raw_material_cost`); revert → PASSES. The permanent
   EP-key guard is live, not vacuous.
3. **F1 refuted (R4)**: `test_input_resolver.py:995` DOES assert `manual2 is False` — the
   audit's read window ended at :994. No cure needed; reclassified not-a-finding.

**Verdict upgraded: PASS** (all notes discharged).
