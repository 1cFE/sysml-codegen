# Audit 7 (REVISE step 7b) — the retired tree, independent

**Verdict:** **FINDINGS** — 10 findings, none blocking; **certification withheld on one
controlling item I could not reach** (audit-F1, in `agentic-mbse`).
**Audited:** 2026-08-12
**Auditor:** independent stage session. Implemented none of this work.
**Subject:** sysml-codegen `item7-rebuild` @ `48bf1b0` (product content @ `c0ceb24`;
`48bf1b0` and `9458a26` add only `.project/` files — verified: `git diff --name-only
c0ceb24..HEAD` outside `.project/` is empty, working tree clean).
**Paired:** agentic-mbse `item7-rebuild` @ `3fbda2f` — **NOT READABLE THIS SESSION** (see
"What I could not verify"). TEAx pinned `fa0e06a9`.

---

## The Point

Item 7 replaces the legacy string-resolution front end with one exact instance-graph
authority, without breaking the product. One modelled source occurrence must produce one
runtime source for every and only its calculation, constraint, aggregation, FORMULA and
alias consumers, and the answer must survive the public live and portable snapshot routes.
Unsupported self-bindings must fail before generation and must never be reinterpreted as an
outer feature. The cutover is complete only when the old authority, its adapters, its
wrong-oracle tests and the dual-run scaffolding are gone, and the owner has accepted the
recapture batch.

---

## Summary

The retirement really happened, and the tree is in much better shape than the candidate the
previous audit refused. Every legacy module the ledger named is gone from the working tree,
not merely unreferenced; `snapshot/__init__.py` re-exports nothing; the CLI-shaped test shim
is deleted; the v5 fixtures are gone; the six-cell all-route mutation matrix exists and its
consumer sets are the ones I re-derived by hand from the SysML. The three new mechanisms
(REQ-DIAG re-homing, typed `AutoImplContext`, single-owner compatibility markers) are real
code doing what their notes say. The three-run gate table is reproducible from the committed
logs and is not overstated.

What I am withholding certification on is not a defect I found — it is a gap in what I could
check. The product-lens ledger's controlling **BLOCK is audit-F1**, which lives entirely in
`agentic-mbse`, and this session has no read access to that repository or to any interpreter.
`audit-F2` I confirmed closed by reading the tree. `audit-F1` I confirmed nothing about. A
certification that treats an unread repository as green is the exact failure mode that caused
the original incident, so I have not written one.

The ten findings below are real but small. The largest is a documentation-honesty issue: the
re-cited verification matrix presents some green rows whose proof is weaker than the row's
text, and one whole family (HR) reads 8/8 pass over a component that ships nothing, without
the disclosure banner its sibling family (CA) got.

---

## Product Judgment

**Is this the right piece of work?** Yes, and it is now substantially the finished piece
rather than a direction. The structural result the owner asked for — one authority, no
duplicate route, no shim around a superseded mechanism — is visible in the tree, not just
asserted in a note.

**Product-lens ledger gate: still BLOCKED, on audit-F1 only, and unverifiable here.**

The five smells the previous audit fired, re-evaluated on the retired tree:

| # | Smell | Verdict now |
|---|---|---|
| 1 | Two representations manually kept synchronized (legacy + exact builders) | **Cleared.** `pipeline_builder.py`, `graph_builder.py`, `producer_resolution.py`, `producer_completeness.py`, `output_registry.py`, `snapshot/{loader,serializer,graph_rebuild}.py`, `elaboration/diff.py` are all absent from the tree. `build_pipeline_context` has 0 definitions and 0 live call sites; every surviving mention is an absence pin, a prose decision record, or the work-list's own data table. |
| 3 | A special category exempts a case whose meaning is unchanged (self-binding exemption) | **Pending probe.** Lives in `agentic-mbse/src/agentic_mbse/validation/level2_structure.py`. Not readable here. |
| 4 | Correctness depends on downstream knowledge of an internal representation (validator predicts elaboration rescue) | **Pending probe.** Same file. |
| 5 | Compatibility preserved against the product's reason (v5/string route beside exact identity) | **Cleared.** 0 `extraction_snapshot.json` files in the tree; both v5 capture scripts and `capture_filter.py` gone; the v5 payload is refused by name at the loader. One documented residual: `_upstream_pins.CONSTRAINT_FACTS_SCHEMA_VERSION` has no `src/` consumer and is kept deliberately with its reader named in the module docstring. |
| 6 | A test passes by selecting one duplicate/route/interpretation | **Cleared for the original instance** — `tests/helpers/legacy_route.py` is deleted. **One weaker successor exists** — see finding F9. |

No new smell fires that the stage notes had not already surfaced.

---

## Part 1 — Closing the loop on `audit.md`

### The four product-lens findings

| ID | Recorded resolution | My verification |
|---|---|---|
| **audit-F1** — companion validator exempts a true `in P = P` self-binding when an outer same-named feature exists | Disposition folded it into REVISE step 2; the step-2 note says `_owner_covers_name` and its guard are gone, the message was rewritten, the firing set went 1 → 4 on the agentic item12 fixtures, and `plant-idiom.md` was corrected — including the core-shape example at `:24` | **NOT VERIFIED.** No read access to `agentic-mbse-item7-rebuild`. The premise check recorded in the step-2 note *is* independently corroborated from this side: the exact route already refuses all 25 affected codegen fixtures, and the owner accepted that batch (`tests/fixtures/v6_recapture_batch/batch.json:455` reads `"status": "ACCEPTED — owner ruling 2026-08-11 (REVISE disposition, step 1)"`). So the direction of the fix is consistent with the shipped generator. The fix itself is unread. → **probe P1** |
| **audit-F2** — legacy builders, v5 exports and CLI-shaped test adapter remain executable | Executed by the retirement's four steps; the gated item 7 (dead v5 exports) landed as a third `removes` block on L-028 at step 4 | **CLOSED, verified.** `src/sysml_codegen/snapshot/__init__.py` is a docstring re-exporting nothing (`git show 3071fba` removes 87 lines from it). `tests/helpers/legacy_route.py` deleted in the same commit. `orchestration/pipeline_context.py` survives as the two-error re-export point with no `PipelineContext`. Grepped `src/`, `tests/`, `scripts/` (excluding `scripts/archive/`) for all seven v5 loader symbols: no definition and no caller. |
| **audit-F3** — no public live + relocated off-default mutation evidence | REVISE step 4 built the six-cell matrix | **CLOSED, verified statically.** `tests/execution/test_fusion_tea_mutation_teax.py` parametrizes a module-scoped `sealed` fixture over `ROUTES = ("live", "in_place_snapshot", "relocated_snapshot")` (`:85`, `:138`); two mutation tests × 3 routes = the six cells. See Part 3 for the hand re-derivation of the anchors. |
| **audit-F4** — route-dependent generated bytes (live provenance is checkout-absolute, v6 replay is portable) | Raised as open question 5 in the owner disposition; explicitly not touched | **PROPERLY PARKED, verified.** The behaviour is unchanged: `orchestration/elaborated_pipeline.py:65-71` still keeps raw parser paths on `source_file` for the live route and normalizes only the excluded-constraint location. `tests/conformance/test_exact_route_snapshot_generation.py:17-31` states in its own docstring that byte identity "does not hold on the exact route, and must not be asserted", and names the two pins that carry what survives. The design amendment A1 (`design.md:633`) explicitly declines to converge D3 *because* convergence would answer audit-F4 by side effect. This is a faithful park, not a silent resolution. |

### Design deviations D1–D3, R2, invariants 34–35

- **D1/D2 — resolved.** `build_pipeline_context` no longer exists; there is one canonical
  public construction surface. Verified by grep for a surviving definition (none) and by the
  absence pins at `tests/unit/test_elaboration_import_boundaries.py:302-324`.
- **D3 — amendment recorded, not converged.** `design.md:625` opens "Amendments — recorded
  after implementation, pending owner ratification"; A1 is graded `[AGENT amendment,
  re-derived 2026-08-12 — pending owner ratification at the gate]`. That is the correct grade
  under capture-fidelity §1: an agent re-derivation against the design's recorded reasoning,
  offered for ratification, not asserted as settled.
- **R2 — amendment A2 recorded** on the same footing; spec R2 carries a pointer.
- **Invariants 34–35 — parked with audit-F4.** Not silently amended.

### Code-integrity items

| Item | Verification |
|---|---|
| Order-dependent constraint validation (`executable_profile.py:1036`, Levels 4 and 6) | **Pending probe P2** — agentic-side. The recorded fix (both call sites move to `evaluate_identified_profile(extract_identified_constraint_facts(model))`, keyed by definition UUID, raising on duplicate UUID) is coherent but unread. |
| Invalid-manifest fallback (`level6_architecture.py:47,:111`) | **Pending probe P3** — agentic-side. |
| Duplicated snapshot pins | **CLOSED, verified.** `PROJECTOR_SEMANTICS` is defined once at `elaboration/project.py:83` and imported by both readers (`snapshot/envelope.py:68`, `orchestration/exact_pipeline_context.py:40`). The two upstream pins are imported at `envelope.py:66` from `_upstream_pins.py:41,44`. Three literals became three imports. |
| Leaky snapshot/template protocol (`auto_impl_context` untyped) | **CLOSED, verified.** `AutoImplContext` / `AutoImplStep` / `AutoImplOutput` at `core/models.py:114-170`, frozen and `extra="forbid"`, with a `model_validator` making the `output_count` / `single_output_expression` redundancy a checked invariant. The codec encodes and decodes it exactly (`snapshot/instance_graph.py:291,308`) instead of `isinstance(dict)`. `generation/stencils.py:178-186` passes four named template inputs with a comment saying why a wholesale merge is wrong. |
| Silent unexpected-failure fallback (`cli/__init__.py:1133`) | **CLOSED, verified.** The only remaining `except` in that file at that layer is `except OSError` (`:1132`); no `except Exception` survives anywhere in `cli/__init__.py`. The deliberate non-change (a failure after step 2 leaves a partial output tree) is recorded in the 6b note and left for the owner. |
| Manually synchronized unit-annotation semantics | **CLOSED for the two named lanes**, narrower than the headline — see finding F8. |
| Stale contracts (three module docstrings) | **CLOSED, verified.** Amended in `82c7951`, which names all three in its commit message. |

### Spec success criteria at this HEAD

The spec's checkboxes are stale relative to the retired tree (finding F6). My reading:

| SC | Status at `48bf1b0` |
|---|---|
| SC1 Mission outcome | **Met on the codegen side**; the self-binding half depends on probe P1. |
| SC2 FORMULA/alias extension | Met — `test_exact_route_alias_aggregation.py` proves the aggregation and its chain alias both reach a consumer, on the public route. |
| SC3 Instance-graph snapshot | Met (already ticked). |
| SC4 One atomic shipped authority | **Met and not ticked.** |
| SC5 Outcome-specific route acceptance | Met — the recapture batch is `ACCEPTED`. |
| SC6 C25/C2 customer routes | Met (ticked). |
| SC7 C19 runtime proof | Met (ticked) — `tests/execution/test_c19_nested_occurrence_teax.py`, 18 nodes, three routes. |
| SC8 C19 legacy deletion | **Met and not ticked** — `resolution/supplied_values.py` and `tests/unit/test_supplied_values.py` are both absent. |
| SC9 Closed API/deletion surface | **Met and not ticked** — ledger 304 rows / 0 problems, 0 unrowed breakages, all six groups affected=0 READY, in three independent runs. |
| SC10 F26/dual-run removal | **Met and not ticked** — `elaboration/diff.py` and `test_elaboration_dual_run.py` are absent. The one surviving "dual" name, `test_elaboration_corpus_ledger.py::test_dual_run_ledger_classifies_all_snapshot_fixtures`, I read in full: it checks a historical ledger document's completeness and runs no comparison. |
| SC11 Scale and real TEAx | Met on the recorded evidence (65-node execution lane green in three runs; scale table in `comparison.md:118`). |
| SC12 Coordinated repository gates | **NOT met, correctly.** `ruff check src` = 14. R12 wants clean production. Owner question 2 is unanswered. |
| SC13 Accepted recapture batch | Met — batch `ACCEPTED`, `--verify` 15/22/0 with a zero-line non-timestamp diff in all three runs. |

---

## Part 2 — The retirement's completeness

I hunted for an escape hatch four ways.

**By grep, at HEAD.** `pipeline_builder.py`, `snapshot_context.py`, `graph_builder.py`,
`producer_resolution.py`, `producer_completeness.py`, `output_registry.py`,
`snapshot/{loader,serializer,graph_rebuild}.py`, `elaboration/diff.py`,
`tests/helpers/legacy_route.py`, `tests/conformance/test_elaboration_dual_run.py`,
`scripts/capture_filter.py`, `scripts/run_elaboration_corpus.py` — all absent.
`analysis/` now holds only `source_referent.py` (`diagnostic_screen.py` went with 6b).
0 `extraction_snapshot.json` files anywhere outside `.git`.

**Against the checker, by reading it rather than trusting its number.**
`scripts/check_ledger_4a.py:422-480` (`check_paths`) and `:505-556` (`check_states`) do the
thing the brief worries about: an executed `delete` row whose file is still at HEAD is a
problem, and an executed `migrate`/`retain` row whose file is gone is *also* a problem unless
its Gate 4C disposition authorises the absence (`ABSENCE_DISPOSITIONS_4C`, `:494`). The state
claim is checked against Git, not believed. I read the docstrings and the branches; the logic
is sound. 304 rows / 0 problems in three runs.

**Against the matrix, mechanically.** I extracted every `test_*.py` basename cited in a PASS
row (51 distinct) and compared against every test file in the tree: **zero PASS rows cite a
file that does not exist.** I extracted every ledger row id cited in a RETIRED cell (43
distinct) and compared against the ledger's ids: **all 43 exist.** All 10 families the note
calls retired end-to-end (AS, BT, DRA, IR, MF, OR, ORCH, PGD, SVM, VBR) carry the retired-family
banner. All 26 explicitly-cited pytest node ids exist by name in the file they name.

**Against the commit series.** `git show --name-only 82c7951` lists 167 paths; 151 match a
ledger row path, 11 are archive destinations of rows whose recorded path is the source, 1 is
the ledger, and **4 have no row at all**: `resolution/__init__.py`,
`resolution/uncovered_params.py`, `snapshot/instance_graph.py`,
`tests/unit/test_elaboration_import_boundaries.py`. I read the first two diffs: docstring and
comment corrections only, and the commit message names three of the four amendments
explicitly. Step 4 is exactly 4 paths = 2 deletion rows + the L-028 gated-item-7 edit + the
ledger, which matches its recorded shape. **No commit claims more than its diff.** Two claim
slightly less (see F7).

**Nothing found.** No legacy authority, no v5 loader, no dual run, no shim, no `retire`-marked
row whose file lives, no PASS claim over a deleted file.

---

## Part 3 — Anchors and the mutation matrix, re-derived by hand

I derived the consumer sets from the SysML without reading the test's expectations first.

`hif_plant` (`tests/fixtures/fusion_tea/designs/hif_ife/hif_plant.sysml`) specializes
`IFE Power Plant` (`designs/generic_ife/ife_plant.sysml`) and inherits `lcoe_calc` and
`recirc_calc` (comments at `hif_plant.sysml:221-222`). Grepping every binding of the two
formals across `designs/`:

- **`availability`** → `lcoe_calc.availability_in` (`ife_plant.sysml:114`, inherited) and
  `meier_coe_calc.availability_in` (`hif_plant.sysml:215`). **Exactly two.**
- **`thermal_efficiency`** → `lcoe_calc.thermal_efficiency_in` (`ife_plant.sysml:126`) and
  `recirc_calc.thermal_efficiency_in` (`ife_plant.sysml:148`). **Exactly two.**

The exposed values are `attribute lcoe = lcoe_calc.lcoe` (`ife_plant.sysml:130`) and
`attribute recirculating_fraction = recirc_calc.f_recirc` (`:151`). So the movers must be
{lcoe, Meier COE} for C25 and {lcoe, f_recirc} for C2.

That is exactly what `test_fusion_tea_mutation_teax.py:201-202` and `:237-238` assert as
`consumer_ports`, and `:216` / `:250` as the `_movers` set. **The anchors and consumer sets
are correct.** `_movers` is computed over every projected output and every constraint
response before and after, so it is an every-and-only claim, and the structural leg partitions
every `(module, formal)` port in the whole graph. The LCOE numbers are checked twice — against
`tests/execution/fusion_tea_arithmetic.py` (an independent hand transcription) *and* against
the literal forensic constants at `:78-79` — so a generator that produced a self-consistent
wrong number still fails.

**The R10 refusal pin exists and asserts what the notes claim.**
`tests/conformance/test_constraint_name_collision.py`, 4 nodes: the strip check that the
control is the probe with one name changed (`:79`), the typed refusal with the parser warning
verbatim, exactly one null QN among the two usages, and `[SI_ID_UNSTABLE]` with its exact
detail (`:87-130`), `run_codegen` returning `False` with the output path never created
(`:133-143`), and the control's whole entry-point key set by equality plus the two catalog ids
(`:146-172`). Measured outcome (b) — typed refusal before generation — is what the pin
states.

---

## Part 4 — The new mechanisms

**REQ-DIAG-02/03 re-homing.** `screen_extraction_diagnostics`
(`elaboration/extraction_screen.py:50`) is called from exactly one place,
`elaborate.py:248`, inside `_ExactElaborator.__init__`, before any node is built. I grepped
every caller of `elaborate(`: there are exactly two, `elaborated_pipeline.py:59` (live) and
`:116` (capture), and `snapshot/capture.py:30` reaches the second. So one sink genuinely
covers both routes. The refusal is `ElaborationInvariantError(EXTRACTION_DIAGNOSTIC_BLOCKING)`
(`diagnostics.py:27`), converted to `ElaborationDiagnosticError` at `elaborate.py:180-193` —
**unconditionally, outside the `strict` branch**, which I checked because a strict-only
conversion would have been a hole. `run_codegen` catches it by name at `cli/__init__.py:1009`.
The advisory path degrades a missing location to `<no location>` rather than raising, so it
cannot occupy the slot the blocking halt needs. **Verified end to end, statically.** The
honest limitation the file itself states: `EXTRACTION_DIAGNOSTIC_SEVERITY` has one entry and
it is BLOCKING, so the two advisory nodes are synthetic and the file says so.

**Typed `AutoImplContext`.** Verified above. The wire form is unchanged and that is proved by
`--verify` 15/22/0 over the accepted batch in all three runs.

**Unit-annotation single owner.** `extraction/unit_annotation.py` states the rule once and
carries both spellings; `elaborate.py:744` and `modeled_defaults.py:54` are its only callers.
See F8 for the scope of the claim.

**Single-owner compatibility markers.** Verified above.

---

## Part 5 — Faithfulness of the REVISE rulings

I sampled the step-2 Q1–Q5 rulings (`ledger-4a.md:281-345`) and the 6b/6d dispositions against
capture-fidelity.

- **Grades are correct.** All five step-2 rulings are graded
  `[AGENT (orchestrator, delegated deletion-ledger authority per plan), 2026-08-11]`. None
  claims owner authority. The step-3 note grades the owner's items `[OWNER 2026-08-11]` and
  marks the per-row execution notes as agent work. The design amendments A1/A2 are
  `[AGENT amendment … pending owner ratification]`.
- **No ruling exceeded its delegation that I can find.** The one that looked closest was the
  gated item 7: the owner ruled the dead v5 exports out "inside steps 1–2", and the
  orchestrator executed it at step 4 instead. The disposition text (`step 2, item 7`) does not
  name a runbook step number, the reason for the move is a *false premise it surfaced rather
  than hid* (L-028's `orphaned_after_step_2` was wrong — `tests/helpers/legacy_route.py:44,52`
  still read two of the symbols after step 2, and that file is a step-4 deletion), and both
  the row and the commit message say so. That is the surfacing rule working.
- **R8 is untouched and parked.** `git log 800ec84..HEAD -- elaboration/elaborate.py
  elaboration/project.py tests/conformance/test_d5_variants.py` returns three commits
  (`82c7951`, `bcb8989`, `8a96618`); I diffed `project.py` across the whole range and the only
  changes are the `PROJECTOR_SEMANTICS` constant, a logger rename, and the `AutoImplContext`
  typing. No `SI_RENDERING_COLLISION` logic moved. Open question 1 remains unanswered and no
  qualifier handling changed.
- **audit-F4 is untouched and parked.** Verified in Part 1.
- **One provenance caveat, not a finding.** `owner-disposition-20260811.md` is graded
  `[INHERITED: handoff-20260811.md]` and says plainly that the raw transcript is unavailable
  and the record carries the orchestrator's near-verbatim structure of it. Every `[OWNER]`
  ruling in this recovery therefore rests on an agent-written handoff rather than on the
  owner's own words. The record discloses this in its second paragraph, which is the right
  thing to have done. The owner should know that is the provenance floor for the whole REVISE
  path.

---

## Findings

### F1 — The HR family reads 8/8 PASS over a component that ships nothing, with no banner
**Severity: medium (documentation honesty).**
`docs/architecture/verification-matrix.md:370-383`. Seven of the eight HR rows cite
`test_hierarchy_resolver.py`. Its subject, `extraction/hierarchy_resolver.py`, has **zero
`src/` importers** — a fact the module's own docstring now records (lines 9-19, "Off the
shipped route, retained, and here is the measurement"). The CA family got an explicit
"Where this family stands after the retirement" note doing exactly this disclosure
(`verification-matrix.md:181`); HR did not. A reader scanning the index sees
"HR — Hierarchy Resolver (8/8 pass)" and reasonably concludes the shipped product is covered.
The same applies, more weakly, to the eight CA rows whose only citation is
`test_computed_attribute_golden.py`, and to REQ-AST-05 / REQ-AST-10, which pin
`hierarchy_resolver._walk_aggregation_ast`.
**Resolution:** give HR the same family note CA has, naming the module's off-route status and
the docstring that records it; and consider reporting the PASS count split into
on-shipped-route and off-route halves, since roughly 15–18 of the 136 are the latter.

### F2 — Some re-cited heirs prove less than their row's requirement text
**Severity: medium (documentation honesty).**
The 6d note says "Every one of those rows was re-read against its own requirement text". I
sampled and found three where the heir does not carry the text:

- **REQ-EPC-01** (`verification-matrix.md:311`) — text: "Every entry point SHALL be
  classified as exactly one EntryPointType". Heir:
  `test_exact_pipeline_context.py::test_the_live_and_v6_contexts_agree_on_the_public_entry_point_surface`
  (`:184-197`), which compares `entry_point_groups`, `execution_order` and `output_aliases`
  between the two routes. A route-parity test passes whether or not classification is total or
  exclusive; it would pass if both routes classified nothing. The second heir
  (`test_every_member_occurrence_is_its_own_entry_point`) is about aggregation members.
- **REQ-GA-03** (`:348`) — text: "Every `module_output` `producer_channel` SHALL resolve to a
  declared output channel". Heir:
  `test_elaboration_projection_one_way.py::test_graph_validation_rejects_missing_occurrence_and_typed_producer_cycle`
  (`:146-161`). I read it: arm 1 pops an occurrence, arm 2 wires a consumer's input to its own
  output. Arm 2 is a good fit for REQ-GA-04's self-dependency clause; neither arm exercises an
  unresolvable producer channel.
- **REQ-CL-04** (`:212`) — text asserts the manifest→catalog mapping is **total** and
  silent-drop-free over every usage `collect_constraint_manifest` sweeps. Heirs are two nodes
  on a two-constraint portability specimen
  (`test_exact_route_constraint_portability.py:163,171`) proving one exclusion is named and
  the numerical constraint still executes. Route invariance, not totality.

The matrix header does disclose a pre-existing class of this ("~30 PASS rows … pin *less*
than the full requirement text", enumerated in `[ITEM7-MATRIX-SWEEP-RESIDUE]`), but that
register predates the re-citation and these three citations are new.
**Resolution:** re-read the re-cited rows against text a second time with "would this test
fail if the requirement were violated?" as the question, and add the survivors to the residue
register rather than leaving them indistinguishable from full-strength PASS rows.

### F3 — `cmd_snapshot` has no exception handler: a typed model refusal exits as a traceback
**Severity: medium (product).**
`src/sysml_codegen/cli/__init__.py:725-747`. `cmd_generate` catches `ElaborationError`,
`ElaborationDiagnosticError`, `SysMLParsingError` and `CodeGenerationError` by name and
returns a logged failure (`:1006-1020`). `cmd_snapshot` calls
`capture_instance_graph_snapshot` bare. Any model the exact route refuses — which is 22 of the
37 corpus fixtures — reaches the user of `sysml-codegen snapshot` as a Python traceback rather
than a logged refusal and exit 1. The 6b note records this ("`cmd_snapshot` … has no handler
at all, so the typed refusal reaches the terminal as a traceback") and correctly says it was
out of that stage's scope, but it was never filed, never given a ledger row, and is **not** in
the owner-question list. Under the brief's test it is neither closed, executed, nor properly
parked, so I am re-firing it.
**Resolution:** either add the same named handlers to `cmd_snapshot`, or record it as an owner
question alongside the other four so it stops being invisible.

### F4 — One green cell in the three-run gate table is vacuous, and the summary drops the caveat
**Severity: low (evidence honesty).**
`evidence/phase5-runs/revise-runs/run1/proof_integrity.log` reads:
`proof integrity: 0 problems over 0 blocked files` followed by
`(0 blocked files means nothing left to check, not checked-and-clean)`. The comparison table
(`comparison.md:69`) reports it as `0 problems over 0 blocked files` and lists it among the
33 identical fields, without carrying the log's own disclaimer. The log is honest; the summary
a reader will actually read is not.
**Resolution:** carry the parenthetical into the table row, or drop the gate from the table
and say it has no subject on the retired tree.

### F5 — Matrix claims 50 distinct kept test files cited; I count 51
**Severity: low.**
`verification-matrix.md:14` and `:770` both say 50. Extracting every `test_*.py` basename from
a `| PASS |` row and de-duplicating gives 51. All 51 exist in the tree, so nothing is broken —
the count is just off by one, possibly because
`tests/integration/test_computed_attributes_exact_route.py` is counted under a different
convention.
**Resolution:** recount, or state the counting rule.

### F6 — The spec's success-criteria checkboxes are stale against the retired tree
**Severity: low (record integrity).**
`.project/active/elaborator-cutover/spec.md:51,73,76,80` — SC4, SC8, SC9 and SC10 read
unchecked, and all four are demonstrably satisfied at this HEAD (see the SC table in Part 1).
I did not tick them: the brief limits me to writing this one artifact. I understand step 7c
regenerates the candidate record, so this may be intentional sequencing — but a reader opening
the spec today reads "not met" against work that is done.
**Resolution:** tick SC4/SC8/SC9/SC10 at step 7c on this audit's evidence; leave SC12 open, and
SC1's self-binding half pending probe P1.

### F7 — "No file outside the work-list was touched by a step" is literally false for step 2
**Severity: low (record integrity).**
`plan.md:5712`. Step 2 (`82c7951`) touched four paths with no ledger row:
`src/sysml_codegen/resolution/__init__.py`, `src/sysml_codegen/resolution/uncovered_params.py`,
`src/sysml_codegen/snapshot/instance_graph.py`, and
`tests/unit/test_elaboration_import_boundaries.py`. I read the first two diffs — docstring and
comment corrections only — and the commit message names three of the four as the stale-docstring
amendments. The plan's own later paragraph ("Stale docstrings and an amended pin … all amended
in the step-2 commit") says the same thing. So the sentence contradicts the note two pages
later; nothing was hidden.
**Resolution:** qualify the sentence ("no *product* file outside the work-list, other than the
four docstring amendments named below").

### F8 — "Unit-annotation normalization, one owner" is true for two lanes, not for the tree
**Severity: low.**
`plan.md:6210` claims the rule now has one home. That is accurate for the two lanes the
original finding named (`elaborate.py:744`, `modeled_defaults.py:54`). But eight other modules
still recognise `UnitAnnotationNode` and decide what to do about it independently:
`calc_compat_renderer.py:71,156`, `constraint_name_safety.py:148`,
`predicate_compiler.py:142,193,250`, `project.py:675`, `graph.py:611,630,643`. Most are
dispatch branches rather than duplicated rules, so this is a scope-of-claim issue rather than a
defect.
**Resolution:** narrow the claim in the stage note to the two lanes, or extend the owner to
cover the rendering sites.

### F9 — The constraint-emission unit tests build catalogs the product no longer produces
**Severity: low (test fidelity).**
`tests/helpers/retired_catalog_assembly.py` is the deleted route's assembler, kept as a fixture
builder for `test_constraint_emission.py`, `test_catalog_usage_tier.py` and
`test_cli_generation.py`. Its own docstring is exemplary — it names the divergence from the
shipped projector (`source_records` from `facts.definitions` vs from projected constraints;
exclusion records derived differently) and refuses to reconcile it without authority. The
shipped code under test (`compile_shared_predicates`, `render_constraint_module`) is real, so
these are not fake-green tests. But the *input shape* they exercise is one the projector never
emits, so a divergence introduced in the projector's catalog would not redden them. REQ-CL-03
carries a row-local divergence note; **REQ-CL-02 (`verification-matrix.md:210`) does not** — it
reads a plain PASS on the same file.
**Resolution:** put the same divergence pointer on REQ-CL-02, and file migrating these fixtures
onto the projector's assembler behind the open REQ-CL-03 product question.

### F10 — Three ledger rows carry `disposition: retain` on files that were deleted
**Severity: informational.**
L-149 (`test_gen_schemas.py`), L-150 (`test_gen_stencils.py`) and L-152
(`test_graph_assembly.py`) read `"disposition": "retain"` with `"state": "executed"` at
`19072ad`, and their files are gone. This is *legal* and the checker knows it: absence is
authorised by `disposition_4c: "defer-to-v5-family"` via `ABSENCE_DISPOSITIONS_4C`
(`check_ledger_4a.py:494-502`), and the code comment explains exactly this case. But the
top-level field a human reads first says the opposite of what happened, and these are the three
rows the matrix's nine UNTESTED cells cite as the source of the coverage debt.
**Resolution:** no action required; noted so a future reader does not mistake it for an
unauthorised deletion.

---

## Accepted residuals (restated, so the owner sees them in one place)

These are known, recorded, and I am not re-firing them:

1. **`ruff check src` = 14** (down from 16; the two that went sat in deleted files). All are
   `UP042`-class style findings (`str, Enum` → `enum.StrEnum`) with unsafe-only fixes. R12 wants
   clean production; **owner question 2 is unanswered.**
2. **`mypy src` = 57 errors in 11 files.** Unchanged across the whole REVISE path.
3. **Nine UNTESTED matrix rows** — REQ-GEN-03, REQ-OSR-02/03/05 (lost with `test_gen_schemas.py`,
   L-149), REQ-SR-01/02/06/07 (lost with `test_gen_stencils.py`, L-150), REQ-GA-05 (lost with
   `test_graph_assembly.py`, L-152). I verified all three modules are absent, that none of the
   three rows records a `replacement_proof_node`, and that the surviving smart-regen leaves
   (REQ-SR-03/04/05) really are at `tests/unit/test_stencils.py:546`
   (`TestSmartRegenStubUpgrade`). This is real coverage the retirement removed, correctly
   itemised rather than papered over.
4. **131 RETIRED matrix rows.** The 275 → 136 PASS drop is the honest number.
5. **Two extraction modules kept by their tests** — `extraction/hierarchy_resolver.py` and
   `extraction/computed_attribute_extractor.py`. Neither is imported from `src/`. Both carry a
   measured disposition in their docstrings.
6. **`_upstream_pins.CONSTRAINT_FACTS_SCHEMA_VERSION`** has no runtime consumer; kept
   deliberately with its one reader named.
7. **`scripts/archive/` holds 19 files**, including `test_source_identity_routes.py`.
   Collection cannot reach them: `pyproject.toml:45` sets `testpaths = ["tests"]`.
8. **A partial output tree survives a mid-write failure.** Measured, deliberately unchanged,
   recorded for the owner.
9. **`tests/fixtures/catf_mfe_d5/PROVENANCE.md` is stale** — it says the exact route refuses the
   fixture; it no longer does. Left for whoever re-measures the D-5 set.
10. **~110 behaviour nodes are license-gated by fixture.** Confirmed the mechanism
    (`tests/conformance/conftest.py:69` skips with the shared string `no live syside license`,
    also used at `tests/conftest.py:41`), so a licence-less green run is detectable by the skip
    reason. All three runs read **zero** such lines with `-rs`.

## Parked owner questions (all five, verified still open)

1. **R8** — the qualifier-dropping rollup refusal: fix-first vs shipping-gate. Untouched;
   no `SI_RENDERING_COLLISION` logic moved anywhere in the REVISE range.
2. **The ruff findings** — clear them (recommended by the orchestrator) or amend the spec.
   Now 14, not 16.
3. **Item 10 scheduling** — raised by R8, not blocking.
4. **How the final audit runs** — this record answers it in practice: it ran as a fresh
   independent session.
5. **audit-F4** — make live provenance portable, or amend invariants 34–35 with proper
   authority. Untouched. D3's convergence is bound to it.

Plus the four raised at 6d, all genuinely owner-grade, none a stale artifact:

6. **REQ-CL-03's total-inventory guarantee** is false of the shipped catalog. Surfaced on the
   row; not answered by re-citing.
7. **Whether the two off-route extraction modules stay.**
8. **Whether the nine UNTESTED rows get replacement coverage.**
9. **Whether the elaborator's own mechanisms** (v6 envelope, occurrence identity, projection
   receipt) get REQ families. This pass deliberately did not invent one.

And, from this audit: **F3** (`cmd_snapshot`'s missing handler) should join this list if it is
not simply fixed.

---

## What I could not verify

**Named honestly, because a certification with unstated limits is a blank check.**

1. **The entire `agentic-mbse` half.** This session has no read access to
   `/home/reid/1cfe/agentic-mbse-item7-rebuild` — `grep`, `Read` and `git -C` against it are all
   refused by the session's directory policy. That means **audit-F1 is unverified**, and it is
   the finding that put the product-lens gate at BLOCK. Also unverified: the invalid-manifest
   fallback, the order-dependent constraint validation fix, the L-036/L-037 deletion at
   `3fbda2f`, and the agentic suite's 1826/1/5.
2. **Anything requiring execution.** No interpreter is available
   (`/home/reid/1cfe/item7-rebuild-venv/bin/python` is refused). I did not run the suites, the
   execution lane, `capture_v6_batch.py`, the ledger checkers, ruff or mypy. Every number I
   report from those tools is read out of the committed run logs, whose internal consistency I
   did check (three byte-identical `heads.tsv`, three `env.json` with `import_path_gate: PASS`
   and the three required worktree paths, `grep -c "no live syside license" = 0`, three
   identical suite tails at `1705 passed, 34 skipped, 65 deselected`).
3. **The six mutation cells' actual numbers.** I verified the test's structure, its oracle
   (independent hand arithmetic plus literal forensic constants), and its consumer sets against
   the SysML. I did not observe it pass.
4. **The 304-row ledger row by row.** I read the checker's logic and sampled ~10 rows.
5. **Scale timings and RSS.** Read from the logs, not re-measured.
6. **The remaining ~120 re-cited matrix rows.** I sampled 20 in depth and checked all 51 PASS
   file citations and all 26 node citations mechanically.
7. **TEAx internals.** Treated as a pinned dependency, as the plan does.
8. **The forensic branches and Item 6 bases.** Not diffed; nothing in my findings needed them.

---

## Requested live probes

For the orchestrator to execute and append. Each names the exact command and the observation
that would confirm or refute the pending line.

| ID | Command / inspection | Expected observation | Confirms |
|---|---|---|---|
| **P1** | `grep -rn "_owner_covers_name" /home/reid/1cfe/agentic-mbse-item7-rebuild/src /home/reid/1cfe/agentic-mbse-item7-rebuild/tests /home/reid/1cfe/agentic-mbse-item7-rebuild/docs` | **Zero hits.** Then read `src/agentic_mbse/validation/level2_structure.py` around the `SI_SELF_BINDING` emission and confirm no guard suppresses it when an outer same-named feature exists, and that the message no longer says "no feature named P is in scope to supply it". | audit-F1 (the controlling product-lens BLOCK) |
| **P2** | `grep -n "test_c1_self_named_binding_fires_over_a_covering_attribute\|test_c1_self_named_binding_fires_over_a_covering_calc_output\|test_c1_message_does_not_offer_the_outer_feature_as_a_rescue" /home/reid/1cfe/agentic-mbse-item7-rebuild/tests/test_validation/test_item12_checks.py` | All three node names present. | audit-F1's test realignment |
| **P3** | `sed -n '20,50p' /home/reid/1cfe/agentic-mbse-item7-rebuild/docs/patterns/plant-idiom.md` | The §"Design-attribute bindings" section reads "Self-named bindings are not supported", and the core-shape example at ~`:24` no longer teaches `in radius = radius`. | audit-F1's doc correction |
| **P4** | `grep -n "evaluate_identified_profile\|extract_identified_constraint_facts" /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/validation/level4_constraints.py /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/validation/level6_architecture.py` and `grep -rn "def evaluate_profile\|def extract_constraint_facts\|def preflight\b\|class ProfileResult" /home/reid/1cfe/agentic-mbse-item7-rebuild/src` | Both production call sites use the identified route; **zero** definitions of the four legacy members. | order-dependent constraint validation; L-036/L-037 deletion at `3fbda2f` |
| **P5** | `grep -n "ManifestError" /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/validation/level6_architecture.py` | A named `ManifestError` exists and `load_manifest` returns `None` only for the absent case; `_check_manifests` states the fail-the-level policy at the call site. | invalid-manifest fallback |
| **P6** | From `/home/reid/1cfe/item7-rebuild-venv/bin/python`: `pytest tests/execution/test_fusion_tea_mutation_teax.py -m execution -q` | 20 passed, including the six matrix cells. | audit-F3 / SC6 observed, not just read |
| **P7** | `python -c "import sysml_codegen, agentic_mbse, simkit; print(...)"` in `item7-rebuild-venv` | The three import paths resolve to the two rebuild worktrees and `teax/packages/teax-simkit`, as `env.json` records. | the environment assertion the brief asked me to make first, which I could not execute |
| **P8** | `python scripts/check_ledger_4a.py paths` and `... states` at `48bf1b0` | 304 rows, 0 problems. | that the committed run logs still hold at the audited OID (the runs were at `c0ceb24`; the delta is docs-only, so this should be a formality) |

Verdict lines marked **pending probe**: audit-F1 (P1–P3), the order-dependent constraint
validation item (P4), the invalid-manifest item (P5), smells 3 and 4, and SC1's self-binding
half.

---

## Certification

**Not certified.** Not because I found something that should stop the work — the ten findings
are all repairable in a sitting, and none of them touches the exact route's correctness — but
because the product-lens ledger's controlling BLOCK sits in a repository I could not open, and
I will not sign off on a green I did not see. Run P1–P5. If they come back as the stage notes
describe, the honest verdict on the evidence I *did* gather is Certify with the residual list
above, once F1–F3 are dispositioned.

**Marked nothing.** I edited no plan, spec, epic or ledger file, made no commit, and wrote only
this artifact, per the brief.

---

## One page for the owner

**The retirement is real.** I went looking for a way the old code could still be reached — a
surviving loader, a shim, a test that quietly picks the legacy answer — and there isn't one.
Every module the ledger promised to delete is gone from the working tree. The v5 snapshot
fixtures are gone. `snapshot/__init__.py` exports nothing. The one place the old builder still
appears is in tests that assert its *absence*. That was the thing the previous audit refused
to certify, and it is done.

**The customer proof holds up to an independent derivation.** I worked out from the SysML,
without looking at the test's answers first, which calculations consume `availability` and
`thermal_efficiency` in the Fusion Tea model. Two each, and they are exactly the two the
mutation matrix asserts, on all three routes a customer can generate through. The LCOE numbers
are checked against a hand-written arithmetic module as well as against the forensic constants,
so a generator that produced a self-consistent wrong answer would still fail.

**The record is honest about its own gaps, which is the part I most wanted to test.** The
matrix went from 275 PASS to 136 because the re-citation pass counted 205 rows of history as
current measurement and stopped doing that. Nine requirements now read UNTESTED with the
deleted test named — that is coverage the retirement removed, listed instead of hidden. The
open questions R8, the ruff findings and audit-F4 are all genuinely untouched; I checked the
code, not just the notes.

**Three things I would fix before this ships.** First, the HR family in the verification matrix
reads "8 of 8 pass" over a component nothing in the product imports, and unlike its sibling
family it carries no note saying so — that reads as coverage the product does not have. Second,
I sampled the re-cited rows and found a few whose new test would not fail if the requirement
were violated; they should go in the residue register rather than sit next to full-strength
green. Third, `sysml-codegen snapshot` has no error handler at all, so any model the exact
route refuses — 22 of the 37 corpus fixtures — greets the user with a Python traceback instead
of a refusal message. That last one was noticed during the work and written down, but never
filed anywhere the owner would see it.

**What I could not check, and why it matters.** This session had no access to the
`agentic-mbse` repository and no way to run anything. The finding that blocked the previous
audit — the authoring validator blessing a self-binding the owner forbade — lives entirely in
that repository. The stage notes say it was fixed, and everything I *can* see from this side is
consistent with that (the shipped generator already refuses those models, and you accepted that
batch). But I did not read the fix. Five short commands at the end of this record will settle
it. Until someone runs them, the honest state of Item 7 is "everything I could reach is in good
order, and one thing I could not reach decides the verdict."

---

## Probe addendum — executed by the orchestrator, 2026-08-12

All eight probes executed from the canonical environment (`item7-rebuild-venv`; import
paths asserted first, P7). Results, verbatim observation vs expectation:

| ID | Observation | Verdict |
|---|---|---|
| P1 | `grep -rn "_owner_covers_name"` over agentic `src`, `tests`, `docs`: **zero matches** (exit 1). `level2_structure.py`'s check docstring records the removal and cites D-4 [OWNER-VERBATIM 2026-08-05]; the emission is unconditional — no outer-feature guard. | **CONFIRMS audit-F1 fixed** |
| P2 | All three realigned node names present at `test_item12_checks.py:77,91,104`. | **CONFIRMS** |
| P3 | `plant-idiom.md` core example binds `in radius_in = radius` with the parameter/attribute name split stated; a dedicated section reads "Self-named bindings (`in x = x`) are not supported — do not write them", refusal + D-4 cited; `ife_plant` explicitly labeled refused. | **CONFIRMS** |
| P4 | `level4_constraints.py:65` and `level6_architecture.py:643` both run `evaluate_identified_profile(extract_identified_constraint_facts(model))`; grep for the four legacy definitions over agentic `src`: **zero matches** (exit 1). | **CONFIRMS** |
| P5 | `ManifestError` defined (`level6_architecture.py:47`), raised for unreadable/malformed (`:78,:82`), caught at the sweep call site (`:140`). | **CONFIRMS** |
| P6 | `pytest tests/execution/test_fusion_tea_mutation_teax.py -m execution -q` → **20 passed** in 1.36s. | **CONFIRMS** |
| P7 | The three imports resolve to `sysml-codegen-item7-rebuild`, `agentic-mbse-item7-rebuild`, and pinned `teax/packages/teax-simkit`. | **CONFIRMS** |
| P8 | `check_ledger_4a.py paths` at `48bf1b0` → **304 rows checked, 0 problems**. | **CONFIRMS** |

Every verdict line marked "pending probe" (audit-F1 via P1–P3, order-dependent validation
via P4, invalid-manifest via P5, smells 3 and 4, SC1's self-binding half) resolves to
CONFIRMED. Per this record's own Certification clause, the standing verdict is **Certify
with the residual list, once findings F1–F3 above are dispositioned**; the disposition of
F1–F3 is recorded in the plan's step-7 stage note.
