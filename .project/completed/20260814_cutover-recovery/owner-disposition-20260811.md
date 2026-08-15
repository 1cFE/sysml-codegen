# Owner Disposition — Item 7 Cutover Recovery

**Date:** 2026-08-11; amended 2026-08-12
**Disposition:** **REVISE — narrow correction active**
**Provenance:** [INHERITED: `handoff-20260811.md`] — the owner's review was given in the
orchestrated recovery session's transcript; this record carries the orchestrator's
near-verbatim structure of it from the session handoff. The raw transcript is not available
to the recording session. The 2026-08-11 rulings below are owner-originated per that handoff;
the execution ordering and slotting notes are agent work and are marked so. The 2026-08-12
narrow-correction proposal is agent-authored. The owner forwarded it for execution, so its
dispositions retain agent-grade provenance exactly as recorded below.

## The verdict

The owner accepted the candidate (`800ec84` + `cc6c7a7`) as a credible **pre-retirement
checkpoint** and refused to call Item 7 complete. The prescribed path:

1. **[OWNER]** Record the 15/22 v6 batch as **accepted**.
2. **[OWNER]** Implement the seven gated migrations instead of holding them out:
   - items 1–2: the coordinated exact-ID type migration in BOTH repos is Item 7 scope;
   - items 3–5: replace or repoint the ~111/113 affected behavior tests before deleting
     their evidence sources;
   - item 6: carry unknown-fixture rejection into the v6 capture driver;
   - item 7: remove the dead v5 exports (this is what closes Blocker 1).
3. **[OWNER]** Add the missing off-default mutation tests on all three routes (live,
   in-place-snapshot, relocated-snapshot) as kept vertical tests.
4. **[OWNER]** Resolve or explicitly shipping-gate R8 (the qualifier-dropping rollup
   refusal) — the accept-the-refusal ruling in Gate 4D S4 is **overruled**; and add a
   collision test for R10 (same-named constraint threshold keys under one owner).
   - **R10 — EXECUTED** 2026-08-12 [AGENT status note]. Measured outcome (b): the product
     refuses, typed, before generation (`SI_ID_UNSTABLE`, via the null qualified name
     SysIDE leaves on the shadowed usage). Pinned by
     `tests/conformance/test_constraint_name_collision.py` (4 nodes) over two new
     non-corpus fixtures. No rule-10 surfacing. Plan: "Revise step 5 (partial)".
   - **R8 — FIX FIRST.** **[AGENT] (ratified for execution by owner, 2026-08-12)** Preserve
     qualified identity through rendering. Fall back to a shipping gate only if measurement
     shows a substantially larger naming-contract change; see narrow-correction disposition 1.
5. **[OWNER]** Execute retirement with **no provisional trim** — the 113-node deselection
   list (`runbook-patches/provisional-trim.txt`) must not be used in the final run.
6. **[OWNER]** Run the full licensed suites and real TEAx against the **actual retired
   tree**, not a simulation.
7. **[OWNER]** Audit that tree, then regenerate ONE internally consistent candidate record
   at the final paired OIDs (the current record has five internal discrepancies, listed in
   the handoff under "Record integrity").

Also in scope from the review: fix the record-integrity discrepancies. The production-ruff
spec-vs-baseline conflict is resolved by narrow-correction disposition 2 below.

## Narrow-correction dispositions — ratified for execution 2026-08-12

The following questions are resolved for execution. Their substance came from the
agent-authored correction proposal and was ratified by the owner without becoming owner-originated.

1. **[AGENT] (ratified for execution by owner, 2026-08-12)** **R8: fix first.** Preserve
   qualified identity through rendering. Fall back to a shipping gate only if measurement shows
   a substantially larger naming-contract change. Item 10 is not an Item 7 dependency when R8 is
   fixed here; it becomes an explicit dependency only under that fallback.
2. **[AGENT] (ratified for execution by owner, 2026-08-12)** **Ruff: amend spec requirement
   R12 to a zero-new baseline.** The recorded canonical `src` baselines are sysml-codegen
   **14** and agentic-mbse **1**. No new findings; changed files clean unless a recorded
   pre-existing finding is unchanged; totals no worse.
3. **[AGENT] (ratified for execution by owner, 2026-08-12)** **Final audit: run a fresh,
   narrow audit.** Cover compiler convergence and symbol removal, replacement coverage for
   deleted tests, R8, portable provenance, final gate semantics, and evidence consistency. This
   is not a re-review of all 195 deletions.
4. **[AGENT] (ratified for execution by owner, 2026-08-12)** **audit-F4: make provenance
   referents portable.** Amend invariant 35 to semantic equality plus generated-byte equality
   after defined normalization of permitted provenance metadata.
5. **[AGENT] (ratified for execution by owner, 2026-08-12)** **REQ-CL-03: amend only after
   one public-behavior check passes.** The check must prove that a model with constraint usages
   but zero eligible assertions still emits the `not_assessed` report and that no
   instance-reaching constraint usage is silently dropped. A failed check is a product defect to
   surface, not authority to amend.
6. **[AGENT] (ratified for execution by owner, 2026-08-12)** **The two non-shipping
   extraction modules are nonblocking cleanup.** Delete them or fold them into test helpers;
   they are not a certification dependency.
7. **[AGENT] (ratified for execution by owner, 2026-08-12)** **Nine UNTESTED matrix rows:**
   add coverage for REQ-GEN-03 and REQ-OSR-02/03/05. For smart-regen rows, add vertical
   behavioral tests if they remain product behavior; otherwise retire or amend the requirements.
   Retain REQ-GA-05 only if its field set is an intentional public or serialized contract.
8. **[AGENT] (ratified for execution by owner, 2026-08-12)** **Three PARTIAL matrix rows:**
   add focused assertions for REQ-CL-04 total swept-usage mapping, REQ-EPC-01 exactly-one
   classification, and REQ-GA-03 rejection of an unresolved producer channel.
9. **[AGENT] (ratified for execution by owner, 2026-08-12)** **Missing elaborator REQ
   families are backlog**, not an Item 7 certification dependency.
10. **[AGENT] (ratified for execution by owner, 2026-08-12)** **D3 and R2 amendments are
    ratified.**

## Narrow-correction verdict

**[AGENT] (ratified for execution by owner, 2026-08-12)** The recovered implementation stays in
place: no rollback and no second rebuild. Item 7 remains open because compiler convergence was
falsely recorded as executed, replacement proof is incomplete, and record-integrity corrections
remain. Final acceptance remains an owner-grade decision after the correction sequence.

## Additional scope folded into the path [AGENT slotting, from `audit.md`]

The independent certification audit (verdict: Needs Work) ran after the owner review. Its
blocking findings audit-F2/F3 and most spec-conformance gaps are the same work the owner
prescribed above. The following are additional and are folded into the path so the final
audit does not re-fire them:

- **audit-F1 — companion validator self-binding exemption** (`level2_structure.py:309-357`
  `_owner_covers_name`): remove the exemption, align `test_item12_checks.py`, correct
  `docs/patterns/plant-idiom.md:35`. No new ruling needed — D-4 [OWNER-VERBATIM 2026-08-05]
  and the contract's violation table already require exactly this. → with step 2.
- **Invalid-manifest fallback** (`level6_architecture.py:47,:111`; blessed at
  `test_sysml_quality_checks.py:969`): represent invalid input explicitly, fail validation.
  → with step 2.
- **Code-integrity items** (duplicated compatibility pins, untyped `auto_impl_context`,
  CLI catch-all at `cli/__init__.py:1133`, duplicated unit-annotation normalization, stale
  module docstrings): → folded into the migration/retirement commits they are adjacent to.
- **SC7 residue** (named C19 fixture lacks a kept public-v6 route test): → with step 3.
- **Design deviations D3 (split source-admission ownership), R2 (envelope omits the
  designed capture object), audit-F4 (byte parity)**: D3 and R2 are ratified by
  narrow-correction disposition 10; audit-F4 executes under disposition 4 before the new narrow
  final audit.
