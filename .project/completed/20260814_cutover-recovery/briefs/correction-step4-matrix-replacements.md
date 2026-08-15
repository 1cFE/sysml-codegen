# Stage brief — narrow-correction step 4: close replacement and matrix coverage (rev 2)

> **Rev 2, 2026-08-14 — revised at the phase-B resumption.** Rev 1 (2026-08-12, in git history)
> predated the CONSTRAINT-SEMANTICS epic and was marked partially superseded at the pause. This
> revision executes the pause record's consequences and routes the epic's Item 7
> Evidence-Invalidation Register (`.project/completed/20260814_epic_constraint_semantics_contract.md`
> §"Item 7 Evidence-Invalidation Register"); the register walk that produced it is recorded in
> `plan.md` ("RESUMED at step 4"). Retired rev-1 instructions appear once, as decision records,
> at the end — not as work.

You are executing step 4 of the narrow correction for ELABORATE-FIRST Item 7. The authority is
`.project/active/cutover-recovery/plan.md`, "Narrow correction — executable sequence",
`owner-disposition-20260811.md` dispositions 5–9, and — for everything this revision changed — the
landed constraint-semantics contract
(`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` as amended by
CONSTRAINT-SEMANTICS Item 1) with the epic's archived close records. Rev-1 decisions are **[AGENT]
(ratified for execution by owner, 2026-08-12)**. Rev-2 changes are **[AGENT] 2026-08-14**,
produced at the owner-directed resumption; the one open ruling (REQ-CL-03) was resolved by the
owner the same day and is recorded in its section. Executing this brief needs only the owner's
go. Work synchronously. Never pause for background
agents. Finish or stop on a concrete premise conflict.

## Preflight and boundaries

Use only `/home/reid/1cfe/item7-rebuild-venv/bin/python`, with that venv's `bin` first on `PATH`.
Load the SysIDE license from `/home/reid/1cfe/agentic-mbse/.env`; the only licensed-run proof is
zero `no live syside license` skip lines. Assert imports resolve into the two rebuild worktrees
(`/home/reid/1cfe/sysml-codegen-item7-rebuild`, `/home/reid/1cfe/agentic-mbse-item7-rebuild`) and
the TEAx checkout on `constraint-semantics-item3`. Confirm the codegen worktree is clean and check
`git log` for commits you did not make (the owner runs parallel agents here). Do not edit
agentic-mbse or TEAx.

Measure the drifting baselines at preflight and hold every later run to zero-new against that
measurement, explaining any delta from the last recorded numbers by a named epic change. The
step-3 record's numbers predate the epic (licensed suite 1,689 passed then; the epic close
recorded 2,070 passed, collect 2104/2183 with 79 deselected). Do not treat the rev-1 pins
(capture verify 15/22/0, corpus 9, execution lane 65, ruff 14, mypy 57-in-11) as current without
re-measuring — the epic added fixtures (`tests/fixtures/catf_mfe_gated`), tests, and execution
lanes.

Read the current verification matrix. Its summary block (280 rows / 136 PASS / 3 PARTIAL /
131 RETIRED / 10 UNTESTED / 0 DEFERRED / 33 families / 55 test files) was recounted 2026-08-14;
re-verify by recount before and after your edits — index totals AND per-family counts, never the
summary block on trust (memory `verification-matrix-drift-modes`). Read audit-7 F2/F4
(`evidence/audit-7-retired.md`), the step-3 completion record, and the pause record. Before
editing, print a declared path set. It may contain only focused tests, the matrix/reference/spec
records, the Item-7 plan/current-work/backlog records, the four CONSTRAINT-SEMANTICS archives
named in the minting section (dated amendments only), and production code only if a required
public-behavior probe exposes an actual defect. A product defect or materially false premise
stops the stage for surfacing before production code changes.

Untick spec SC9 (`.project/active/elaborator-cutover/spec.md`, "Closed API and deletion surface")
before claiming closure. Retick it only if every row below receives an honest final disposition
and all replacement checks pass. Amend stale claims in place; do not append a contradictory
history note.

## Evidence rules (from the Item 7 Evidence-Invalidation Register — binding through step 10)

- No observation taken against `instance-graph/v2` bytes may be reused. Item 2 bumped the schema
  to v3 and kept no v2 reader; re-observe against the recaptured v3 bytes.
- No byte-identity comparison against pre-recapture fixture bytes may be reused. All 21
  snapshot-bearing fixtures were recaptured once at v3 (Item 2, 2026-08-12); re-baseline against
  the recaptured bytes (reviewed diff: Item 2's `verification.md`,
  `.project/completed/20260813_constraint-catalog-totality/`).
- No evidence may cite `collect_constraint_manifest` as the population definition — deleted in
  Item 2 Phase 7c. The population authority is
  `tests/conformance/test_constraint_population_oracle.py` and its expected-population files.
- No new snapshot recapture unless a step 4–6 code change alters snapshot bytes; if one does, it
  is one reviewed batch with a classified, timestamp-churn-controlled diff (memory
  `byte-identity-captured-at-churn`).

## Nine legacy UNTESTED rows

Close every row without weakening its requirement into whatever an existing test happens to prove.

1. Add kept output-schema coverage for REQ-GEN-03 and REQ-OSR-02/03/05. Through a real generated
   package, prove the multi-output versus single-output schema choice, exact graph-declared output
   field names, and absence of output defaults. Prefer one compact vertical test over copied unit
   implementation tests.
2. Re-derive REQ-SR-01/02/06/07 against current shipping behavior. If the behavior remains a
   product promise, prove it with vertical behavior through the real smart-regeneration path. Do
   not restore the retired source-inspection/static tests. If a row is obsolete or states an
   implementation detail rather than a product promise, amend or retire the requirement and its
   reference text honestly, with its reason. Preserve the ratified provenance.
3. Keep REQ-GA-05 only if the exact field set is intentionally public or serialized. Inspect the
   current `ComputationGraph`, its public exports, and v6 serialization. If intentional, pin the
   actual reviewed field set at the relevant public/serialized boundary. If its old exact list is
   stale or private, amend/retire it rather than adding a brittle internal-shape test.

Recount the matrix mechanically. No legacy UNTESTED row may remain when this stage closes; the
REQ-DIAG-04 exemption below is the only permitted exception, on its recorded basis.

## The tenth UNTESTED row (REQ-DIAG-04) and the third PARTIAL row (REQ-DIAG-01)

Both grades were recorded deliberately at CONSTRAINT-SEMANTICS Item 7's audit (2026-08-14) as
absence-proofs with no asserting test; they post-date rev 1.

- REQ-DIAG-04: attempt one focused tripwire — assert the v6 envelope schema carries no diagnostic
  `severity` field. The disposition `severity` at `snapshot/instance_graph.py:724,759,803` is a
  different field with a different writer and must not be swept in. If the tripwire can be stated
  against the public envelope boundary without freezing incidental structure, add it and move the
  row to PASS; otherwise leave the recorded UNTESTED grade — it is a decision, not a gap — and
  record why.
- REQ-DIAG-01: leave as recorded. Its gap is a code-shape absence claim (no reader-side
  `kind → severity` mapping) whose only codegen-side test would be the retired static-inspection
  style this stage explicitly does not restore; the construction rule lives upstream and is
  pinned there.

## Two PARTIAL rows

Add focused failing-edge assertions, then cite exact kept nodes and move each row to PASS:

- REQ-EPC-01: prove every emitted entry point has exactly one member of the three-value
  `EntryPointType` classification, not merely route parity.
- REQ-GA-03: construct an unresolved `module_output` producer channel and prove graph validation
  rejects it specifically.

## REQ-CL-03 — re-derive against the landed contract

The rev-1 pre-amendment proof is retired: the behavior it wanted proved (a constraint-bearing
model with zero eligible assertions still reports honestly, with every instance-reaching usage
carried) is now landed, tested contract — six report states, catalog totality hard-gated, a
missing disposition halts generation (Items 2–3). What remains is the row itself: it still grades
PASS against `test_constraint_emission.py`, whose subject is the **retired** assembler (now the
fixture builder `tests/helpers/retired_catalog_assembly.py`), under the surfaced divergence note
at `verification-matrix.md:226`.

**RULED — the usage domain is the totality boundary** **[AGENT] (ratified by owner,
2026-08-14)**. Recorded reasoning: the landed contract founded coverage truth on the usage
domain deliberately; a definition with no usages participates in no coverage claim, and the
silent-absence failure mode is already hard-gated by the totality oracle. The definition-level
total inventory was the retired assembler's design, not a promise anyone restated; if
definition-level visibility ever matters it gets its own filed item.

Execute accordingly: amend REQ-CL-03 to describe the shipped projector-built catalog
(`elaboration/project.py`, `_build_constraint_catalog`), re-cite live tests, clear the
divergence note, and record the rejected total-inventory reading as a one-line decision record
carrying the ruling above.

## Mint the REQ-tag family for the CONSTRAINT-SEMANTICS Items 3/5/8/9 gates

Owner-authorized 2026-08-14 (`[CONSTRAINT-GATES-UNTAGGED]`, BACKLOG). One matrix pass, landing
together with the row edits above.

Derive requirement text and gates from the items' archived records — never from memory:

- Item 3 (coverage report + TEAx policy): `.project/completed/20260813_constraint-coverage-policy/`
- Item 5 (CATF derivative + end-to-end acceptance): `.project/completed/20260813_catf-constraint-policy-acceptance/`
- Item 8 (unit-lane port metadata): `.project/completed/20260813_unit-lane-port-metadata/`
- Item 9 (derivative upgrade under held intent): `.project/completed/20260813_derivative-upgrade-held-intent/`

Rules, in the REQ-DIAG family's footsteps (filed the same way at `verification-matrix.md` §DIAG):

- Family naming follows the existing 33-family convention; each new family header names its
  filing date, the authorizing ruling, and the archive it traces to.
- A row states the landed gate as a product promise, graded by what the archived spec/close
  records actually say (`[INHERITED: <archive path>]` where text is carried; owner-verbatim
  material is never re-worded).
- Run every cited test before citing it and record the run. No aspirational citations.
- When the rows exist: tick CONSTRAINT-SEMANTICS Item 7's SC2/SC5 in its archived record
  (`.project/completed/20260814_constraint-docs-agent-sync/`) with a dated amendment citing the
  minted rows; mark `[CONSTRAINT-GATES-UNTAGGED]` complete in BACKLOG; update both BACKLOG
  baseline lines (currently `280 rows / 136 PASS / 33 families`) to the new recounted numbers.

## `gain = 100` three-route execution proof

Extend the existing `tests/execution/test_fusion_tea_mutation_teax.py` `_harness` / sealed
fixtures over `ROUTES`; do not create a parallel harness. Discover the exact existing gain entry
channel and its modeled default from the graph. Mutate it to exactly `100` on live,
in-place-snapshot, and relocated-snapshot routes.

- Structurally assert its every-and-only consumer set, including the exact calculation consumer
  and exact constraint consumer.
- At runtime assert the dependent calculation output and constraint response change as expected,
  and compare the full output/response sets so every independent output and response is
  unchanged.
- Keep the seal active and use typed entry injection. Do not edit sealed JSON or add a synthetic
  route.
- Constraint response assertions use the landed six-state vocabulary; `all_satisfied` is retired.

Register row 3: the test lands here and its step-4 run is working evidence; the authoritative
single-shot observation is the steps 7–8 battery at the true final paired OIDs, where the full
suite re-runs it.

## Retired rev-1 instructions (decision records, not work)

- The REQ-CL-04 partial-row work and the zero-input-report proof are retired — absorbed by
  Items 2–3 under the amended contract (register row 1). REQ-CL-04 and REQ-EXT-09 grade PASS on
  live tests (`test_constraint_catalog_totality.py`; `test_constraint_population_oracle.py` with
  `test_constraint_usage_domain_totality.py`); their old closures are superseded. No step-4 work
  on either row.
- The two non-shipping extraction modules remain explicitly nonblocking cleanup, and missing
  elaborator REQ families remain backlog. Do not expand this certification stage to either.

## Records and validation

Amend `docs/architecture/verification-matrix.md`, relevant reference documents and
`.project/active/elaborator-cutover/spec.md` in place. Update the recovery plan with every row's
disposition, exact kept nodes, recounted matrix counts, the REQ-CL-03 outcome, the minted
family's row list, and the gain=100 exact consumer/mover sets. Check correction step 4 only after
validation. Update `.project/CURRENT_WORK.md` so portable provenance (step 5) is next.

At minimum run:

1. Every changed/focused test, including all three gain mutation routes.
2. Full licensed sysml-codegen suite with `-rs`; zero license-skip lines and explained node delta
   against the epic-close baseline (2,070 passed; collect 2104/2183, 79 deselected).
3. `capture_v6_batch.py --verify`, corpus selection, and the full execution lane — record the
   measured numbers and explain any delta from the step-3 record (15/22/0, 9, 65) by named epic
   changes.
4. Ledger paths/surface/groups/replacements, proof integrity, retirement worklist, and matrix
   citation/collection checks already used by the project.
5. Ruff on changed Python files; `ruff check src` and `mypy src` zero-new against preflight.
6. `git diff --check`, exact declared path set, worktree clean after commit.

Commit the bounded implementation and record changes. Report the commit OID, every row
disposition, exact recounted matrix counts, the minted rows, gain=100 consumer/mover results, the
REQ-CL-03 outcome, all gates, and any premise conflict.

`ARTIFACT:` `docs/architecture/verification-matrix.md`
