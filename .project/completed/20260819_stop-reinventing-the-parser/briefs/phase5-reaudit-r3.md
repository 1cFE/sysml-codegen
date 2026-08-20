# Brief — independent re-audit rev 3: the r3 chain and the fabrication fix

You are the independent auditor for the third pass on this item's Phase 5 chain. Rev 1 blocked
on refusal quality (fixed, confirmed in rev 2); rev 2 blocked on one class — **the public
catch-all fabricated provenance** (model-facing code + invented first-`.sysml`-line-1
location). Fix round 2 claims that class is closed under the recorded rule: *a diagnostic
field is either measured or absent, never defaulted.* Your job is to break that claim, then
re-verify the re-minted chain. Trust nothing that is only asserted; your two predecessors'
methods (in `audit.md`, rev-1 and rev-2 sections) are your floor, not your ceiling.

Read: `audit.md` (both sections), the fix-round-2 closure account in plan.md's records,
`design.md` rev 8's D8 section including the new dated correction note, and the brief that
drove the round (`briefs/phase5-fix-round-2.md`).

## Where the work is

- Codegen `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch `stop-parser-impl-r2` at
  `C_evidence-r3` `875ba01`; production candidate `C_prod-r3` `14130a8` (fix commits on top of
  `C_prod-r2` `2234845`). Preservation refs `evidence-chain-r1` / `-r2` must still resolve.
- Agentic closed at `A_final-r2` `4433888` — verify untouched, read-only.
- Fusion `F_final-r3` `83551fb` in its dedicated worktree; frozen TEAx / 1costingfe pins
  unchanged.
- Build your own extractions under `/tmp/stop-parser-rev2/` (extraction-lane env and Agentic
  sibling layout as recorded; `agentic-mbse` in Agentic paths). License:
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. Never the PDF/paid suites.
  Modify nothing, commit nothing, push nothing.

## Obligations

1. **Attack the fabrication fix (R1/R2 — the blocking set).** From the real CLI and API, try
   to make ANY public route emit (a) a fabricated reference or location, (b) a raw Python
   traceback, or (c) a model-facing code for an internal defect. Rerun rev 2's two
   reproductions (line-N syntax error; `zzz_broken`/`aaa_fine` misattribution) and invent your
   own: multi-root models, unreadable files, snapshot arm, capture arm, planted internal
   failures at seams the fix didn't name. Verify `SI_INTERNAL_DEFECT` vs model-facing codes
   split "our bug" from "your model" correctly, the deleted invention helpers
   (`diagnostic_context.py` + the two `elaborated_pipeline.py` siblings) are gone with no
   re-implementation, and the passthrough tuples are now symmetric at every public seam (the
   audit found one; the fix claims two — sweep for a third).
2. **The six raise-site provenance shapes** (`SI_REDEFINITION_INVALID` sites, item-def arm of
   `SI_CONSTRAINT_UNATTACHED`, capture-arm staging, twelve `SI_RENDERING_COLLISION` sites,
   `SI_CONTAINMENT_RECURSIVE`, extraction screen): each carries true authored context measured
   at the site; the `/tmp/…sources…` staging leak is gone from message and console.
3. **The guards fail closed.** Mutation-check `assert_no_location_is_invented` (plant a
   fabricated-but-non-empty field — it must fail) and the AST guard's four-code enumeration
   (add a fifth unguarded raise — discovered?). Verify the claimed 25-failed/7-passed run of
   the proof files against the unfixed parent.
4. **The calibration deviation.** The mypy-baseline lane hash was recomputed through the
   runner's own `_output_hash` after a first wrong declaration. Verify by recomputation that
   the amended calibration matches what the runner measures, that the "same 30 errors,
   two line shifts, one deleted file" account is exactly true against `C_prod-r2`, and that
   the two provisional runner passes supplied nothing to the final chain.
5. **The chain.** Topology (`C_evidence-r3^ == C_prod-r3`, exactly six evidence paths, Fusion
   pins `C_prod-r3` never the evidence commit), all artifact/evidence hashes recomputed, the
   21 lanes' declared counts against retained JUnit, the four-group mechanical auditor
   including its refusal of a byte-mutated wheel, full-suite figure (claimed 2,542/9/94 with
   the +18 delta explained) from your own extraction, licensed zero-skip check, both user
   checkouts and the entry-status digests, `deep_cross_scope_probe` still refused.
6. **Carried rows.** R3-R6 remain DISPOSE-grade: confirm each is recorded with an owner and
   none has silently become load-bearing.

## Deliverable

Append a dated rev-3 section to `audit.md` (do not commit): per-obligation results with your
own reproductions, any findings ranked, and the verdict — is the item's implementation now
**certifiable** (Pass / Pass with findings), or what exactly still blocks. State plainly what
you did not check. Final message: prose summary ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/audit.md`.
