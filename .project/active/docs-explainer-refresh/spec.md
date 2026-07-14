# Spec: Docs + Explainer-Brief Refresh (post-CONSTRAINT-EXEC)

**Status:** Complete (implemented 2026-07-13)
**Owner:** Reid W
**Created:** 2026-07-13
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic (sysml-codegen home; touches agentic-mbse, teax, fusion-tea)

---

## Problem

The CONSTRAINT-EXEC epic changed what the system *is* — modeled assertions execute, snapshots
are v3, packages seal, a study layer exists — but Item 14 flipped only the minimum doc surface
(sysml-codegen `ccfe9db`, agentic-mbse `d83109a`, teax `245f687`). A spec-time survey
(`staleness-survey.md`, same folder) found the rest: sysml-codegen docs still teach the retired
`ExpressionAST` symbols and snapshot "version 1", contracts/sealing and the five-value
`ModuleKind` have zero doc coverage, agentic-mbse's decision table still teaches the retired
drop model that its own `constraints.md` now contradicts, and the explainer rewrite brief
(`EXPLAINER_PROMPT.md`) — the designated Gen-2 prior art — still lists "constraints are
dropped" as an honest caveat. A reader today gets two contradicting stories depending on which
file they open.

## Success Criteria

- [x] **The surveyed inventory is corrected.** (Scope: the stale claims inventoried in
      `staleness-survey.md` + the named gap areas — not a repo-wide scrub; see Non-Goals.)
      - Snapshot docs say v3 with the constraint-facts section and a v2→v3 note
        (27-snapshot-generation.md, REQ-SNAP-09).
      - Expression docs (14/16/19-*.md + matrix rows REQ-AST-06, REQ-CA-02) teach
        `ExpressionIR` and the current symbol set with zero remaining
        `ExpressionAST`/`build_expression_ast`/`compile_expression` references outside
        deliberate historical notes.
      - `overview.md` family count matches the matrix.
- [x] **The new machinery is documented where its siblings are.** `ModuleKind` (all five
      values) appears in 09-data-models.md (PipelineModule, replacing the retired bool-flag
      description; ComputationGraph gains `constraint_catalog`), 08-generation.md (constraint +
      report-aggregator render seams), and 00-pipeline-overview.md (REQ-PIPE-06 corrected; the
      lowering phase named in the step narrative and `overview.md`).
- [x] **Contracts/sealing has a home.** A reference doc covers `ModelContract` /
      `PackageContract`, `seal_package`, verify-on-load, and the `seal` CLI subcommand; the
      verification matrix covers the family (shape of the family is design's call).
- [x] **agentic-mbse teaches one story.** `docs/subtype-enumeration-decision-table.md` speaks
      profile vocabulary (no `is_droppable_constraint` / "dropped predicates" / "revisited by
      the constraint-execution epic"); `MODELING_GUIDE.md:280` no longer says "not executable";
      ConstraintFacts and ExpressionIR have a durable `docs/` home (depth is design's call —
      at minimum an architecture pointer that survives `.project/` archival).
- [x] **teax names the mechanism.** `docs/evaluation-and-study.md` documents the
      `entry_models` property (channel → typed model, derived from the pipeline spec) as the
      way callers obtain entry types.
- [x] **`EXPLAINER_PROMPT.md` is a truthful, buildable v2 brief.** Two bars, audited
      differently:
      - *Mechanical checklist:* re-anchored off current HEAD (not `pipeline-truth-epic`);
        stale caveats retired ("constraints are dropped", `resolve_input()` unwired — grep
        clean); the eight constraint-exec artifact areas slotted per the survey's mapping
        (lowering phase, `module_kind` as a 4th+5th module family with colors, Kleene modules
        as an Act-3 hard part, report aggregator, catalog, contracts/sealing in the
        diagnostics-as-contract frame, snapshot v3 in operational reality, teax study layer
        as the top-of-stack consumer).
      - *Judgment bar (Item 10's bar):* a spot-read of the remaining claims finds **no claim
        contradicted by HEAD**. The auditor samples claims and checks them against code; this
        is a read-and-verify pass, not a grep.
- [x] **New/edited docs keep the inherited history straight.** Checkable bar for the
      `[INHERITED]` cautions below: any doc this item writes or edits (a) describes
      `lower_constraints_enabled` as landed history (default-on, GRANDFATHERED empty) — never
      as a live drop path; (b) does not claim `collect_constraint_manifest` was removed; (c)
      references CE-F1 (standalone catalog emission) and CE-F2 (multi-channel bridge) as open
      follow-ons, never as landed behavior.
- [x] **fusion-tea residue closed.** `pipeline-walkthrough.html` carries a pointer/retirement
      note; the two `ife_e2e/study` driver scripts drop the now-unneeded `ToyPlantParams`
      alias (default is *drop*, decided at orchestration 2026-07-13; three alias sites —
      `bench_prepare_once.py:36,61`, `run_viability_study.py:135` — plus the stale comment at
      `run_viability_study.py:130`. Sequencing caveat: the scripts then require a teax with
      CE-F3 (`0d606a4`); they are exploration drivers, not CI-gated, and already run against
      the epic-branch teax).
- [x] **The v2 HTML build is registered as its own follow-on item** (BACKLOG), pointing at the
      refreshed brief — not built here.

## Known Requirements

- **[NEED]** The explainer deliverable of THIS item is the refreshed `EXPLAINER_PROMPT.md`
  brief; building `pipeline_explainer_v2.html` is a separate follow-on another agent picks up.
  ([OWNER] 2026-07-13: "update the EXPLAINER_PROMPT.md. I will have another agent pick this
  up.")
- **[NEED]** The sysml-codegen explainer artifacts (`.project/active/new-pipeline-explainer/`
  + `EXPLAINER_PROMPT.md`) are the canonical prior art; fusion-tea's `pipeline-walkthrough.html`
  gets a pointer or retirement note only. ([OWNER] 2026-07-13.)
- **[HARD]** Code is the truth the docs must match, verified at spec time:
  `SNAPSHOT_FORMAT_VERSION = 3` (`snapshot/__init__.py:19`); `ModuleKind` has five values
  (`resolution/models.py:161-170`); `ExpressionAST` and its two entry points no longer exist in
  `src/`; `PreparedEvaluator.entry_models` replaced the hardcoded attribute (teax `0d606a4`).
- **[INFERRED]** The sweep is *targeted* — fix the surveyed findings and gap areas, not a
  docs-scrub-style re-verification of all 28 reference docs (that is a separate chore if
  wanted; see Non-Goals).
- **[INHERITED]** Background the new docs should reflect correctly (from the archived Item
  5/8/14 artifacts, `.project/completed/20260713_*`): the `lower_constraints_enabled` flag
  landed default-off and flipped default-on in Item 8 with the GRANDFATHERED set now empty —
  the flag story is *history*, not current behavior; `collect_constraint_manifest` survives
  deliberately (the kept migration-mapping test needs it) — only the report/render/serialize
  surface was retired, so docs must not claim the collector is gone.
- **[INHERITED]** CE-F1 (standalone `constraint_catalog.json` emission) and CE-F2
  (multi-channel `CandidateBridge`) are open follow-ons (BACKLOG, registered at epic close) —
  new docs must describe the *current* embedded-catalog / single-channel-bridge reality, with
  the follow-ons referenced rather than documented as if landed.

## Non-Goals

- Building `pipeline_explainer_v2.html` (follow-on item), or patching the Gen-1
  `new_pipeline_explainer.html` content (superseded by the v2 brief; at most a deprecation
  pointer).
- A full verify-every-doc scrub of `docs/architecture/` (docs-scrub precedent exists as its
  own item shape if wanted later).
- Fixing CE-F1/CE-F2, or any code change beyond the fusion-tea driver-script alias removal.
- PDF/DOCX-extraction docs in agentic-mbse (unrelated surface).

## Open Questions / Deferred to design

- Verification-matrix shape for contracts/sealing: new family (e.g. REQ-CON-*) vs extending an
  existing one; which existing tests anchor the rows.
- Depth of the agentic-mbse ConstraintFacts/ExpressionIR durable docs: full architecture doc
  vs a pointer page into the archived design artifacts.
- Numbering/home of the new sysml-codegen contracts reference doc (29-contracts-and-sealing.md?)
  and whether 28.md absorbs it instead.
- Whether the Gen-1 HTML gets an in-file deprecation banner or only the BACKLOG follow-on
  mentions it.
- Whether the matrix rows citing retired symbols (REQ-AST-06, REQ-CA-02) are reworded or
  re-anchored to renamed requirements.

---

## Related Artifacts

- **Epic:** none (post-epic follow-on; CONSTRAINT-EXEC archived at
  `.project/completed/20260713_epic_constraint_execution.md`)
- **Survey (primary evidence):** `.project/active/docs-explainer-refresh/staleness-survey.md`
- **Prior art:** `.project/active/new-pipeline-explainer/{spec,design,plan,update-list,update-plan}.md`,
  `.project/active/EXPLAINER_PROMPT.md`, `.project/diagrams/new_pipeline_explainer.html`
- **What-changed base:** sysml-codegen `ccfe9db`; agentic-mbse `d83109a`; teax `245f687`
- **Design:** `.project/active/docs-explainer-refresh/design.md` (to be created)

---

**Next Steps:** `/_my_spec_review` in a fresh session (this item spans four repos and retires
teaching surfaces), then `/_my_design`.
