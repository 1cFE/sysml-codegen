# Stage brief — narrow-correction step 4: close replacement and matrix coverage

> **PARTIALLY SUPERSEDED — DO NOT EXECUTE AS WRITTEN (2026-08-12).** The owner paused steps
> 4–10 pending the constraint-semantics contract
> (`.project/completed/20260814_constraint-semantics-contract/spec.md`). This brief's runtime-report
> instruction and its REQ-CL-03/REQ-CL-04 row closures are subordinate to that contract, which
> also re-grades REQ-EXT-09. A revised brief is required at resumption; see the pause record in
> `.project/active/cutover-recovery/plan.md` ("PAUSED at step 4").

You are executing step 4 of the 2026-08-12 narrow correction for Item 7. The authority is
`.project/active/cutover-recovery/plan.md`, "Narrow correction — executable sequence", and
`owner-disposition-20260811.md` dispositions 5–9. Every decision is **[AGENT] (ratified for
execution by owner, 2026-08-12)**. Work synchronously. Never pause for background agents. Finish
or stop on a concrete premise conflict.

## Preflight and boundaries

Use only `/home/reid/1cfe/item7-rebuild-venv/bin/python`, with that venv's `bin` first on `PATH`.
Load the SysIDE license from `/home/reid/1cfe/agentic-mbse/.env`. Assert imports resolve into the
two rebuild worktrees and TEAx checkout. Confirm both rebuild worktrees are clean; never touch the
protected originals. Do not edit agentic-mbse or TEAx.

Read the current verification matrix, its nine UNTESTED rows and three PARTIAL rows; the matching
reference requirements; the tests adjacent to each shipped implementation; audit-7 F2/F4 and the
step-3 completion record. Before editing, print a declared path set. It may contain only focused
tests, the matrix/reference/spec records, the Item-7 plan/current-work records, and production code
only if a required public-behavior probe exposes an actual defect. A product defect or materially
false premise stops the stage for surfacing before production code changes.

Untick spec SC9 before claiming closure. Retick it only if every row below receives an honest final
disposition and all replacement checks pass. Amend stale claims in place; do not append a
contradictory history note.

## Nine UNTESTED rows

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

Recount the matrix mechanically. No UNTESTED row may remain when this stage closes.

## Three PARTIAL rows

Add focused failing-edge assertions, then cite exact kept nodes and move each row to PASS:

- REQ-CL-04: prove total mapping over every constraint usage swept by the shipped manifest route.
  Each usage must have an eligible or unassessed carrier, or a named justified
  requirement/satisfy exclusion. A silently dropped third usage must fail.
- REQ-EPC-01: prove every emitted entry point has exactly one member of the three-value
  `EntryPointType` classification, not merely route parity.
- REQ-GA-03: construct an unresolved `module_output` producer channel and prove graph validation
  rejects it specifically.

## REQ-CL-03 pre-amendment public proof

Before amending REQ-CL-03, add a public exact-route test for a model that has constraint usages but
zero eligible assertions. Prove it still emits the `not_assessed` report and prove every
instance-reaching usage is present in the shipped catalog as unassessed or a named justified
exclusion. If any usage is silently dropped, stop and report the product defect; do not amend the
requirement. If green, amend REQ-CL-03 and its matrix row to the shipped public contract, replacing
the stale retired-assembler wording.

The two non-shipping extraction modules remain explicitly nonblocking cleanup, and missing
elaborator REQ families remain backlog. Do not expand this certification stage to either.

## `gain = 100` three-route execution proof

Extend the existing `tests/execution/test_fusion_tea_mutation_teax.py` `_harness` / `sealed`
fixture over `ROUTES`; do not create a parallel harness. Discover the exact existing gain entry
channel and its modeled default from the graph. Mutate it to exactly `100` on live,
in-place-snapshot, and relocated-snapshot routes.

- Structurally assert its every-and-only consumer set, including the exact calculation consumer
  and exact constraint consumer.
- At runtime assert the dependent calculation output and constraint response change as expected,
  and compare the full output/response sets so every independent output and response is unchanged.
- Keep the seal active and use typed entry injection. Do not edit sealed JSON or add a synthetic
  route.

## Records and validation

Amend `docs/architecture/verification-matrix.md`, relevant reference documents and
`.project/active/elaborator-cutover/spec.md` in place. Update the recovery plan with every row's
disposition, exact kept nodes, matrix counts, the REQ-CL-03 measured result, and the gain=100 exact
consumer/mover sets. Check correction step 4 only after validation. Update `.project/CURRENT_WORK.md`
so portable provenance (step 5) is next.

At minimum run:

1. Every changed/focused test, including all three gain mutation routes.
2. Full licensed sysml-codegen suite with `-rs`; zero license-skip lines and explained node delta.
3. `capture_v6_batch.py --verify` (15/22/0), corpus (9), and the full execution lane.
4. Ledger paths/surface/groups/replacements, proof integrity, retirement worklist, and matrix
   citation/collection checks already used by the project.
5. Ruff on changed Python files; `ruff check src` no worse than 14; `mypy src` no worse than 57 in
   11 files.
6. `git diff --check`, exact declared path set, both rebuild worktrees clean after commit.

Commit the bounded implementation and record changes. Report the commit OID, every row
disposition, exact matrix counts, gain=100 consumer/mover results, REQ-CL-03 result, all gates, and
any premise conflict.

`ARTIFACT:` `docs/architecture/verification-matrix.md`
