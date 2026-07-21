# Audit: Docs + Explainer-Brief Refresh (post-CONSTRAINT-EXEC)

**Verdict:** PASS-WITH-NOTES
**Audited:** 2026-07-13
**Branch:** constraint-exec-epic
**Commit:** 2cb13ef (item commits 0fad7bf, 78a6a7d, dbc60b8, d5328cc)

---

## Summary

Every deliverable in the home repo (sysml-codegen) is verified and solid: the surveyed
staleness is corrected, the new machinery is documented where its siblings live, contracts/sealing
has a real doc + a matrix family anchored to tests that actually exist, the matrix recount is
internally consistent at 32/274/73, and the explainer brief passes both its mechanical and its
judgment bar. The inherited-history invariants (INV-1/2/3) hold across every edited doc, and scope
was disciplined — the diff touches exactly the design's Component Overview surfaces and nothing
else.

Two reasons this is PASS-WITH-NOTES rather than Certify: (1) the three cross-repo legs
(SC-4 agentic-mbse, SC-5 teax, SC-7 fusion-tea) live in repos this sandbox cannot read, so they are
certified only by requested probes below, not by direct verification here; (2) the plan's Phase 5
and Phase 7 completion notes were left blank even though their checkboxes are ticked — an
audit-trail gap, not evidence the work is missing (the Phase 7 commit and BACKLOG entries exist).

## Findings

### Plan completion

All seven phase gates are ticked and the four home-repo commits exist on `constraint-exec-epic`
(`git log`: 0fad7bf → 78a6a7d → dbc60b8 → d5328cc). Phases 1–3 (home repo) and Phase 6 (fusion-tea)
carry full Implementation Notes.

- **Phase 5 (teax) and Phase 7 (close-out) completion notes are blank** —
  `plan.md:694-696` and `plan.md:714-716` show empty `**Completed:**` fields despite the phase
  checkboxes being ticked. For Phase 7 the work is independently evidenced (commit d5328cc; BACKLOG
  entries present, below), so the gap is documentation only. For Phase 5 the completion is *asserted*
  (Phase 3 spot-read #6 says `entry_models` is "confirmed in Phase 5") but its own evidence field is
  empty and it cannot be verified in-sandbox — see the SC-5 probe. Fix: backfill both note blocks
  with the re-grep result and commit hash.

### Spec conformance

- **SC-1 — surveyed inventory corrected. VERIFIED.** `SNAPSHOT_FORMAT_VERSION = 3`
  (`src/sysml_codegen/snapshot/__init__.py:19`); doc 27 reads "Current: **3**" with the
  `constraint_facts` section and a v2→v3 migration note (`27-snapshot-generation.md:37,39,76`). The
  four retired-symbol hits under `docs/architecture/` are all inside explicitly-marked history frames
  (`14-…:17-18,97`, `19-…:91`, `09-…:73` — each says "retired"/"was dropped"/"replaced in Item 13"),
  satisfying INV-5. `overview.md` family count reads 32 (`overview.md:223`).
- **SC-2 — new machinery documented. VERIFIED.** `ModuleKind` shows all five values
  (`resolution/models.py:161-170`) in `09-data-models.md:54,292,298`, `08-generation.md:134-161`
  (a new "Module-Kind Render Seams" section with the fail-loud `unrenderable_module_kind_error`
  path — `generation/errors.py:12`), and `00-pipeline-overview.md:22` (REQ-PIPE-06 reworded off
  "all three module types"). `ComputationGraph.constraint_catalog` is documented
  (`09-…:261`) and real (`resolution/models.py:407`). The constraint-lowering phase is named in the
  step narrative (`00-…:137`, Step 5.7) and `overview.md`.
- **SC-3 — contracts/sealing home. VERIFIED.** New `29-contracts-and-sealing.md` covers
  `ModelContract`/`PackageContract` (`contracts/models.py:51,92`), `seal_package`, verify-on-load,
  and the `seal` subcommand (`cli/__init__.py:704,876`). The `CON` matrix family has 10 rows
  (REQ-CON-01..10), each anchored to a test function that exists and pins the claimed behavior in
  `tests/unit/test_contract_models.py` (7 fns) or `tests/conformance/test_seal_step9.py` (5 fns) —
  mapping checked row-by-row, all 10 map.
- **SC-4 — agentic-mbse one story. PROBE REQUIRED** (sandbox-blocked). The SC-4 amendment
  (`is_droppable_constraint` kept as a live symbol, only the drop *framing* retired) is recorded in
  the spec (`spec.md:44-48`) and the plan Phase 4 deviation note (`plan.md:684-692`) — legitimate,
  not a defect. Direct verification needs the probes below.
- **SC-5 — teax `entry_models`. PROBE REQUIRED** (sandbox-blocked). Also see the blank Phase 5 note
  above.
- **SC-6 — explainer, both bars. VERIFIED.** *Mechanical:* the stale caveats ("constraints are
  dropped / no execution path", `resolve_input` unwired) appear only inside a clearly-framed RETIRED
  block (`EXPLAINER_PROMPT.md:202-208`); `pipeline-truth-epic` and the stale "253 / 30 families"
  counts are zero-hit; corrected "274 … 32 families" is present (`:267`). All eight areas are slotted
  (lowering, module_kind, Kleene, report aggregator, catalog, contracts/sealing, snapshot v3, teax
  study layer). INV-6 buildability infra is present: an 8-row responsibility map (`:105-125`), a
  reading list naming the two contract test files and the lowering/Kleene sources (`:269-274`), and a
  stated reuse-guidance delta (~70–80% reusable, `:286-295`). *Judgment:* I independently sampled 10
  substantive claims across the eight areas and verified each against `src/` — `constraint_lowering.py`,
  `constraint_catalog.py`, `predicate_compiler.py` (Kleene non-finite → `unknown`, docstring
  `:1-6`), `unrenderable_module_kind_error`, `_resolve_aggregation_input_channel` deleted
  (`input_resolver.py:6`), `seal` subcommand, `constraint_catalog` field, `ModelContract`/
  `PackageContract`, `ModuleKind` 5 values, snapshot v3. **No claim contradicted by HEAD.**
- **SC-7 — fusion-tea residue. PROBE REQUIRED** (sandbox-blocked). The SC-7 drop-default decision and
  the sequencing caveat are recorded (`spec.md:72-78`, plan Phase 6 notes complete at `plan.md:699-712`).
- **SC-8 — inherited history straight. VERIFIED.** INV-1: `lower_constraints_enabled` is described as
  landed history with GRANDFATHERED empty, never a live drop path (`00-…:143-144`). INV-2: no doc
  claims `collect_constraint_manifest` was removed — it is described as the active sweeper
  (`01-extraction.md:20`, `modeling-assumptions.md:434`, matrix REQ-CL-04/REQ-EXT-09). INV-3:
  CE-F1/CE-F2 are referenced as open follow-ons (`29-…:57`, `08-…:159`, `EXPLAINER_PROMPT.md:194-196,245-247`).
- **SC-9 — v2 HTML follow-on registered. VERIFIED.** `[V2-HTML-BUILD]` in `BACKLOG.md:703` points at
  the refreshed `EXPLAINER_PROMPT.md`, not built here.

### Design conformance

Implementation follows the design's routing decisions.

- **D1 (CON family, not a CL extension). Followed.** New `CON` family with a short register + an
  indirect-coverage note, mirroring the CL precedent (`verification-matrix.md:174-197`).
- **D2 (new doc 29, not absorbed into 28). Followed.** Doc 29 created; doc 28's "Contracts (seam
  disposition)" stub became a forward pointer (11-line diff to doc 28).
- **D3 (durable summary+pointer page in agentic-mbse). Probe** — page path recorded as
  `docs/constraint-facts-and-expression-ir.md` (`plan.md:680`); verify via SC-4 probe.
- **D4 (Gen-1 banner + BACKLOG). Followed.** A one-line "⚠ Superseded (Gen-1)" banner is at
  `new_pipeline_explainer.html:1256`; the 268 KB content is otherwise untouched (4-line diff).
- **D5 (reword retired matrix rows, preserve REQ IDs). Followed with a recorded refinement.** REQ-AST-06
  and REQ-CA-02 keep their IDs; the Phase 1 note (`plan.md:567-579`) records that REQ-AST-06 was
  actually *retired* in Item 13 (not merely renamed) and its Test File column was re-pointed to the
  covering test `test_expression_compiler.py::…::test_feature_chain_raises_compilation_error` — which
  exists and is cited at `verification-matrix.md:97`. Count-neutral.
- **INV-4 (matrix recount). VERIFIED consistent.** 32 `###` family headers = 32 Index bullets;
  274 `| REQ-` rows = summary "Total requirements 274"; distinct test files 73 (summary) = prior 71
  + the 2 net-new CON files; `overview.md` = 32. All surfaces agree.

### Code integrity

No issues found. The only code change (fusion-tea alias drop) is out-of-sandbox; its py_compile
result is recorded (`plan.md:705`). The home-repo work is docs plus the additive doc 29 — no god
functions, fallbacks, or shims introduced.

The two recorded out-of-scope surfacings are legitimate, not scope-dodging:

- **`[MODULEKIND-DOC-SWEEP]`** (`BACKLOG.md:718`) — the `is_computed_attribute`/`is_aggregation` →
  `module_kind` migration is un-swept in doc 05 / doc 22 / the MF matrix family (`plan.md:582-590`).
  Correctly left out: it is a coherent surface *not in the survey inventory*, and a partial fix would
  create a matrix-vs-doc-05 divergence. This is exactly the B1 "un-surveyed stale doc is out of
  contract, not a defect" boundary the design drew. The diff confirms doc 05 and doc 22 are untouched.
- **`[DOC19-DISPATCH-REAUDIT]`** (`BACKLOG.md:712`) — doc 19's dispatch inventory drifted beyond the
  surveyed `:89` cite; the flagged row was fixed and the rest filed as a follow-on (`plan.md:574-579`).

Item-14 surfaces (`modeling-assumptions.md`, doc 28 body) were not rewritten — `modeling-assumptions.md`
is absent from the diff and doc 28 changed only its stub. No docs-scrub creep.

---

## Requested live probes (cross-repo legs — sandbox cannot read these paths)

Run from a session with the sibling repos in reach. Each is the SC's verification gate.

**SC-4 — agentic-mbse** (`/home/reid/1cfe/agentic-mbse`, branch `constraint-exec-epic`, expect HEAD `9e24c93`):
```bash
# retired vocabulary gone (expect ZERO hits):
grep -rn 'dropped predicates\|revisited by the constraint-execution epic\|report_dropped_constraints' \
  /home/reid/1cfe/agentic-mbse/docs/subtype-enumeration-decision-table.md
# MODELING_GUIDE no longer "not executable" (expect ZERO):
grep -n 'not executable' /home/reid/1cfe/agentic-mbse/modeling_project/MODELING_GUIDE.md
# durable page exists (expect the file):
ls /home/reid/1cfe/agentic-mbse/docs/constraint-facts-and-expression-ir.md
# amendment: is_droppable_constraint KEPT as a live reframed reference (expect exactly 1, by design):
grep -c 'is_droppable_constraint' /home/reid/1cfe/agentic-mbse/docs/subtype-enumeration-decision-table.md
# and the symbol is live at HEAD (expect a def/use at :418):
grep -n 'is_droppable_constraint' /home/reid/1cfe/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py
```

**SC-5 — teax** (`/home/reid/1cfe/teax`, branch `constraint-exec-epic`, expect HEAD `4c96b99`):
```bash
# entry_models named in the doc as the channel->typed-model map (expect >=1 hit):
grep -n 'entry_models' /home/reid/1cfe/teax/docs/evaluation-and-study.md
# property is real at HEAD:
grep -rn 'entry_models' /home/reid/1cfe/teax/src --include='evaluator.py'
git -C /home/reid/1cfe/teax log --oneline -3
```

**SC-7 — fusion-tea** (`/home/reid/1cfe/fusion-tea`, branch `main`, expect HEAD `bfff2b4f`):
```bash
# alias gone from the two DRIVER scripts (expect ZERO under study/*.py; findings.md may retain it as history):
grep -rn 'ToyPlantParams' /home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/bench_prepare_once.py \
  /home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/run_viability_study.py
# both scripts compile (expect clean):
python3 -m py_compile /home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/bench_prepare_once.py \
  /home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/run_viability_study.py
# walkthrough carries a retirement note (expect >=1 hit):
grep -n 'Superseded\|retirement\|EXPLAINER' /home/reid/1cfe/fusion-tea/pipeline-walkthrough.html
```

---

## Certification

Verified in-sandbox and certified: SC-1, SC-2, SC-3, SC-6 (both bars, 10-claim spot-read),
SC-8, SC-9; design decisions D1, D2, D4, D5; invariants INV-1..6; the matrix recount
(32/274/73, consistent across summary / Index / `overview.md`); the CON family's 10 rows against
real test functions; scope discipline (diff = design's Component Overview surfaces; doc 05/22 and
Item-14 surfaces untouched); both out-of-scope BACKLOG follow-ons registered and legitimate.

Spec success-criteria checkboxes were already ticked by the Phase 7 close-out; I did not add or
remove any — SC-4/5/7 remain ticked but are certified here only by requested probe, not direct
verification.

**Not checked:**
- **SC-4, SC-5, SC-7 (cross-repo legs)** — agentic-mbse, teax, fusion-tea paths are outside this
  session's sandbox; `grep`/`ls`/`git` against them are blocked. Certified only via the requested
  probes above. This includes D3 (durable-page existence) and the fusion-tea py_compile.
- **Cross-repo commit hashes** (agentic-mbse `9e24c93`, teax `4c96b99`, fusion-tea `bfff2b4f`) —
  not confirmed; the probes include `git log` to check them.
- **Rendered output** of the Gen-1 banner and `EXPLAINER_PROMPT.md` — verified by source/grep, not
  by rendering the HTML or building the v2 explainer (the v2 build is out of scope by design, SC-9).
- **Prose quality** of the new doc 29 and the explainer narrative beyond the 10 sampled claims — I
  verified factual correctness against code, not completeness or readability of every sentence.
- **Phase 5 completion in fact** — asserted in the Phase 3 note but its own evidence field is blank;
  the SC-5 probe settles it.

---

ARTIFACT: .project/active/docs-explainer-refresh/audit.md

---

## Orchestrator addendum — requested probes executed (2026-07-13)

All three probe legs run by the orchestrator (all four repos in reach). Results verbatim
against the expectations above:

**SC-4 (agentic-mbse `9e24c93` — confirmed HEAD... see note):** retired-vocabulary grep zero-hit;
"not executable" zero-hit in MODELING_GUIDE.md; durable page
`docs/constraint-facts-and-expression-ir.md` exists; `is_droppable_constraint` exactly 1 hit in
the decision table (by design, SC-4 amendment) and live at `syside_adapter.py:418`. **VERIFIED.**

**SC-5 (teax `4c96b99`):** `entry_models` named at `docs/evaluation-and-study.md:53`; property
live at `packages/teax-simkit/simkit/evaluation/evaluator.py:107`. **VERIFIED.** Note: teax HEAD
at probe time is `1f4cb7c`, not `4c96b99` — a concurrent owner-session pair
(`6ab3fcc` + `1f4cb7c`, `docs/teax-study-explainer.html` only) landed around the phase commit.
Different file, no interaction with this item's edit; the orchestrator will push teax only up
to `4c96b99` so the concurrent work is not published by this run.

**SC-7 (fusion-tea `bfff2b4f` — confirmed HEAD):** `ToyPlantParams` zero-hit in both driver
scripts; `python3 -m py_compile` clean on both; retirement banner present in
`pipeline-walkthrough.html:17` pointing at the canonical explainer artifacts. **VERIFIED.**

The Phase 5 / Phase 7 blank completion notes (audit note 2) are cured in `plan.md` with
post-hoc-recorded provenance.

**Verdict after probes: all nine success criteria verified — PASS (Certify).** The two
PASS-WITH-NOTES conditions are discharged: cross-repo legs probe-verified above; plan notes
cured.
