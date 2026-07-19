# Current Work

**Last Updated**: 2026-07-19

---

## Active Work

### Constraint Execution Lifecycle — RATIFIED; NEW REMEDIATION EPIC READY (2026-07-19)

The owner ratified the corrected lifecycle contract as the normative target architecture. The
focused correction re-review found it ratifiable after bounded edits; all 24 edits were applied and
mechanically verified. Ratification certifies no implementation. Candidate certification remains
blocked until register row 0 pins a compatible committed revision set and row 17 passes every
mandatory acceptance case on one artifact thread.

The old PR-wave remediation epic is superseded and frozen as partially completed. Items 1/2 remain
complete and Items 4/6 remain certified within their recorded scopes. Their evidence is inherited,
not automatically re-audited. Unfinished and newly discovered work is mapped into the new 14-item,
19–23 day P0 epic covering ratified register rows 0–17.

The epic makes simplification an execution gate: every item records production LOC before/after and
names deleted duplicate/workaround paths. The overall touched production surface must shrink unless
the owner explicitly approves a surfaced exception. The known additive catalog-schema work is
reported separately and paired with deletion of the alternate TEAx schema/materializer/stand-in
system.

Active artifacts:

- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- `.project/active/constraint-execution-lifecycle-contract/spec.md`
- `.project/research/20260719-134700_constraint-execution-lifecycle-contract-correction-rereview.md`
- `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`
- `.project/backlog/epic_constraint_pr_wave_remediation.md` (superseded history)

The owner confirmed that delivery means updating the existing open agentic-mbse PR #11 first and
sysml-codegen PR #9 second, not opening a replacement upstream wave. The new epic now states that
objective in its executive summary, success criteria, Item 0, Item 13, and dependencies.

Pre-Item 0 preservation checkpoints requested by the owner:

- agentic-mbse `205debd` preserves the profile-v4 implementation and evidence. It sits above the
  unrelated local modeling-orchestrator commit `4ed2a07`, so Item 0 must reconcile only the
  constraint changes onto the PR #11 line at remote `54a95d2`.
- stellarator `bceaf40a` preserves the WI-027 Gate-B capture blocker record.
- sysml-codegen `e217119` preserves the constraint remediation, evidence, ratified contract, and
  new epic.

No commit was pushed and no PR was updated. Next: begin new epic Item 0, reconcile and pin the
committed compatible candidate, and record the cross-repository production LOC baseline before
certifying any acceptance cell.

### CONSTRAINT-WAVE Item 1 — Profile Semantics — COMPLETE; INHERITED BY NEW EPIC

Implementation and fresh audit evidence verify the approved ordering and polarity semantics,
source-identity rejection before mutation, four-route positive-IR continuity, compound diagnostic
sentinels, one neutral body with per-usage polarity, TEAx execution, package/skew controls, and the
shared Items 2/4/6 regression union in normal and optimized Python. After audit, the owner removed
agent-authored clean-overlay and pre-edit-hash gates and requested no re-audit. The replacement
lifecycle epic inherits this evidence and lands/pins it in Item 0. The absent provenance is recorded
without retroactive claims. Artifacts:
`../agentic-mbse/.project/active/constraint-wave-profile-semantics/`.

### CONSTRAINT-WAVE Item 4 — Snapshot Portability and Shape Gates — CERTIFIED (2026-07-19)

The fresh independent re-audit certifies Item 4. Every prior **Needs Work** finding remains closed:
live and replay collectors use distinct routes; the licensed node is ordered
live A, live B, replay A; the explicit loader matrix has 336 cases; the fixture transaction stages
and verifies full fixture and baseline manifests with 11 reproducible recovery/failure tests; and
BLOCK zero-call behavior plus exact canonical warning/excluded-record bytes are pinned. The
production fixture delta remains exactly 65+1 location lines across two snapshots.

Fresh licensed evidence: the complete relocation file passed 3/3, including live A/live B/replay A
and moved replay; Item 4 plus transaction tests passed 407/407 in normal and optimized modes; and
the independently run full suite passed 2,950 with 26 skips and 10 deselections. Fresh Ruff, format,
and diff checks pass. Prior frozen-overlay, fixture, baseline, 30-snapshot inventory, Item 2/6
overlap, and Item 3 isolation evidence remains preserved. The spec, Phase 5, epic criterion, and
backlog item are closed. Audit and evidence:
`.project/active/constraint-wave-snapshot-portability/{audit,evidence.md}`.

### CONSTRAINT-WAVE Item 6 — Seal and Verify Symlink Symmetry — CERTIFIED (2026-07-18)

Epic Item 6 (R-10) is independently certified in
`.project/active/constraint-wave-seal-symmetry/audit.md`. Seal, canonical/emitted verification,
generation, Step 9, and re-seal reject every symlink before target use. Fresh audit evidence
reproduced 23 historical RED nodes and six controls, then passed the 29-node candidate overlay,
76 focused tests and 22 audit probes in normal and optimized modes, and the 84-test package gate.
Verifier/fingerprint, static, fixture, and scope checks passed; licensed live nodes remain
unclaimed.

### CONSTRAINT-WAVE Item 2 — Generated Constraint Name Safety — COMPLETE (execution gate closed 2026-07-19)

The re-audit certified the license-free implementation. The missing-catalog fail-open is closed
with a structured `catalog_module_join` before renderer, writer, or orchestration mutation. Fresh
evidence passed the original validator/renderer/`run_codegen()` probe, 20 missing-catalog writer and
orchestration cases, 16 ordering permutations with a safe-order control, and all four independent
historical-impact nodes at `512786c`. Augmented focused normal and optimized gates passed 174/174;
Item 6 overlap passed 122 with 2 licensed skips; patch, static, diff, fixture, and isolation checks
passed.

**Execution gate closed 2026-07-19.** The one criterion the audit left open (real TEAx execution,
then blocked by missing `pandas`) was run green in the agentic-mbse venv (pandas 2.3.3, teax-simkit
on `sys.path`), fresh subprocesses, not mocked: pinned node `1 passed, 14 deselected`; satisfied
`(True, 'satisfied', 1.0, {'x': 2.0, 'limit': 3.0})`, violated `(False, 'violated', -1.0, {'x': 4.0,
'limit': 3.0})` (`evidence/collision-free-execution-tuples.txt`). Spec SC-9 and all three epic Item 2
success criteria are now met; the item is complete. Licensed Syside live/snapshot parity (design
I11) stays out of scope, tracked under Item 8. Audit + post-audit addendum:
`.project/active/constraint-wave-name-safety/audit.md`.

### Independent GAP-CLOSE completion audit + PR-wave code review (2026-07-18, evening)

Two deliverables, both agent-fan-out verified:

1. **Independent audit of GAP-CLOSE completion** (`.project/backlog/epic_gap_close_audit_independent.md`):
   the certified-partial status HOLDS. Items 1–4 re-confirmed against code with fresh test runs;
   pushed companion `54a95d2` byte-identical to the local gap-close worktree, no orchestrator
   contamination. Corrections: Item 5's "diff --check clean on both branch ranges" box was false of
   the pushed companion range (one archived-plan EOF blank line; cure uncommitted) — annotated in the
   epic; the partial pre-PR has in fact been EXECUTED (`512786c` pushed + both PRs commented
   2026-07-19T00:59/01:10Z), so the epic's old Next Action was stale — corrected. Still genuinely
   open: F1 external leg, and licensed full suites at the final commits (2,516-pass evidence is from
   the pre-cure candidate; the companion "1,506 passed" run exists only in the PR comment).

2. **PR-wave code review** (`.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`):
   four NEW High findings, all reproduced, all outside prior review coverage — PR #11 profile:
   ordering comparisons ADMIT string/boolean/enum operands (live-reproduced); `is_negated` never
   consulted → negated asserts admit inverted semantics (live-reproduced). PR #9: model formals named
   `value`/`status`/`verdict`/`self` shadow generated locals → silent margin corruption incl. sign
   inversion / runtime TypeError / SyntaxError; nullable-QN ADMIT filter in
   `collect_bare_actual_demand` crashes from-snapshot rebuild on a valid snapshot. Plus 8 Medium
   (named-excluded path leak into fingerprints, recursive-part silent truncation, demand overwrite,
   warning-pre-pass masking, seal/dangling-symlink gaps, loader raw KeyError, lost signed/unit
   defaults, TEAX_SIMKIT_PATH silent fallback) and a Low/latent tail. Recommendation: fix the four
   Highs before the wave merges (it is already held on F1); R-1/R-2 need an owner call on BLOCK vs
   IR-fold semantics. Nothing committed or pushed this session.

### GAP-CLOSE epic — LOCAL SCOPE CERTIFIED; PARTIAL PRE-PR MAY PROCEED (2026-07-18)

The final focused re-audit certifies all local and in-scope GAP-CLOSE work. F2 through F9 remain
certifiable, including exact warning bytes across repeated live, relocated live, and snapshot
replay. The hash-identified rebuilt companion wheel contains the corrected BLOCK/L6 severity and
asserted-outcome statements, and its guide is byte-identical to source.

TEAx explicit-path expansion, resolution, and validation now share the route-aware normalization
boundary; kept tests cover an injected `expanduser()` `RuntimeError` and a symlink loop. Fresh
focused audit selections passed 132 codegen tests normally, 110 under optimized Python, and 143
companion guide/profile tests. The rebuilt wheel hash is `160e7eb5…a8d4f`. External
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open, so the epic is not complete. `my-pre-pr` may now
run only as an explicitly partial wave. No commit, push, PR comment, or close action occurred.
Merge order remains agentic-mbse PR #11 before sysml-codegen PR #9.

### GAP-CLOSE Item 3 — Model and seal boundary guards — CERTIFIED IN EPIC AUDIT (2026-07-18)

All four phases in `.project/active/gap-boundary-guards/plan.md` are implemented. Every
post-initialization declared-field assignment on the transactional Pydantic base now validates a
complete candidate before changing the live model, including constructor-defaulted fields. The
canonical and emitted package verifiers now reject internal and escaping directory symlinks with a
fatal `INVALID_PATH` diagnostic at the link path.

Pinned source-isolated evidence at exact HEAD `6db3212` is four independently defect-specific RED
nodes, followed by 4/4 GREEN over a candidate containing only the two production files. Focused
normal and optimized gates are 57 passed; broader is 53 passed. The unlicensed default full suite
is 2,213 passed with 23 failures and 96 errors confined to the known license-dependent families.
Ruff/format/diff checks pass, mypy remains at the 76-error baseline, and all 179 fixture hashes are
unchanged. Item 1–2 and unrelated dirty files were preserved. The final GAP-CLOSE re-audit retains
this certification; do not push or close outside the explicitly partial pre-PR wave.

### GAP-CLOSE Item 2 — Lowering outcome integrity — CERTIFIED IN RE-AUDIT (2026-07-18)

Epic: `.project/backlog/epic_gap_close.md`, Item 2. The stricter warning-byte route parity is now
pinned at the real lowering logger: repeated live, relocated live, and snapshot replay produce the
same two exact `root-0/model.sysml` warning strings. Lowering reports every
NON_NUMERICAL sibling exactly once before a BLOCK halt, while the halt still precedes concrete
records, catalog assembly, and package mutation. Anonymous excluded statements alone receive a
portable root-slot/file/line/column identity and 128-bit suffix across live, relocated, and snapshot
routes. Named IDs and eligible-anonymous bytes remain pinned to the coordinated baseline.

Isolated evidence uses codegen `6db3212`, companion `4ed2a07`, profile v3, and a frozen overlay;
four historical nodes are independently RED and the exact six-path candidate is 5/5 GREEN. Fixture
bytes and the migration guard are unchanged. Focused gates are 102 passed/8 license skips; broader
45/37; the default full suite is 2,206 passed with 23 failures and 96 errors confined to the known
license-dependent families. Ruff is clean and mypy remains at the 76-error baseline. Licensed live
shape/CLI atomicity legs are accurately unclaimed. `[ANON-ELIGIBLE-KEY]` remains open. The GAP-CLOSE
re-audit independently certified the exact warning-byte route criterion; do not push or close from
this item.

### GAP-CLOSE Item 1 — Runtime evaluation contract — CODEGEN LEG COMPLETE (2026-07-18)

Epic: `.project/backlog/epic_gap_close.md`, Item 1. All five phases in
`.project/active/gap-runtime-contract/plan.md` are implemented. Codegen now rejects all verified
case-fold, underscore-run, and quoted-hyphen predicate-name collisions deterministically before
any output mutation, while direct compilation rechecks the same invariant. Saved isolated evidence
at baseline `6db3212` reproduces each old `DID NOT RAISE` failure and the later-body overwrite.

F1 remains deliberately split: codegen tests characterize unchanged native propagation for div-zero,
zero-to-negative power, exponent overflow, nested connective, and the production-generated wrapper.
The narrowed docstring promises only that an adverse verdict does not itself raise. Licensed
`plant_values` live/snapshot trees were byte-identical; before/after changes were only that sentence
and its derived package contract. Focused gates are green; the default full suite recorded 2,169
passes with all failures/errors license-dependent, while licensed live/focused execution passed in
the companion environment. The final GAP-CLOSE re-audit certifies the local codegen/F2 scope.
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains an external open P0; do not claim evaluator
normalization or end-to-end F1 closure.

### Numerical constraint executable profile — ✅ COMPLETE: CERTIFIED, COMMITTED, PR WAVE UPDATED (2026-07-18)

**Audit verdict: Certify** (`.project/active/numerical-constraint-profile/audit.md`). All 8 spec
success criteria verified against code/tests, not just records: totality/execution, split-equality
outcomes, both-tools warnings, catalog `excluded_records` with the eligible⇔exclusion validator
(construction-probed unrepresentable), live/snapshot value parity, frozen golden untouched, v3 pin
in both repos (companion `05cde35`). Parent-remediation booking (`096c29f`) for the mid-run licensed
failure confirmed genuine.

**Committed and pushed 2026-07-18** as `da3b495` (separable remediation cures + ledger),
`9c0291c` (the v3 item + artifacts), `3f215ac` (touched-file formatting; the `constraint_inline`
baseline deliberately left as generator-emitted bytes). Pre-PR gates green: licensed suite
**2450 passed / 26 skipped / 8 deselected**; companion **1511 passed / 1 skipped**; ruff src
clean; mypy at the 76 baseline; no debug artifacts/secrets. PR #9 and PR #11 updated with
appended-commit comments. Only merge remains (see Up Next — the #11-first order is now
load-bearing). After merge: `/_my_close` archives this item and the remediation.

Dedicated CONSTRAINT-EXEC Item 3 contract correction:
`.project/active/numerical-constraint-profile/{spec,spec-review,design,design-review,plan}.md`.
Spec reviewed and revised in-session (owner resolved all findings; three-way rule: admitted
numerical claims execute, malformed numerical claims error naming the fix, non-numerical
statements warn in both tools and never block generation). Design approved after review — key
owner-ratified calls: numerical-claim **containment** decides force (mixed `(x > 0) and flag`
errors), one tagged exclusion payload on `ConcreteConstraint` projected into catalog
`excluded_records`, single v3 pin at shared lowering, location-fallback rendering. Plan is 5
phases, agentic-mbse first (profile v3 + answer key → L4/L6 → codegen re-pin → exclusion/catalog
+ re-capture → end-to-end families + gates).

All five phases are complete. Agentic-mbse profile v3 core landed as `b251e95`; L4/L6 consumers
and the exact compatible companion state landed as `05cde35`. Codegen now pins v3, renders fixes
on malformed numerical halts, warns once per non-numerical statement, validates a total exclusion
payload, and projects excluded statements into the constraint catalog. New live families prove
warn-and-continue with an admitted numerical sibling and error-force containment for
`(value > 0.0) and flag`; the warning, graph, and complete catalog are identical live/offline.

R4 proved the inherited-inline licensed failure predated Phase 3. Commit `096c29f` corrected the
parent remediation's invalid empty-design-attributes regression harness, and `aaa579e` refreshed
its stale inline baseline. Final licensed codegen evidence is **2450 passed, 26 skipped, 8
deselected**; optimized focused evidence is **125 passed**. The exact `05cde35` companion archive
passed **1491 tests, 1 skipped, 5 deselected**. Targeted mypy and touched-file Ruff/format passed.
The independent audit (Certify) closed this item; see the header block above for the commit and
PR-wave state.

### CONSTRAINT-EXEC code-quality remediation — ✅ CURES COMMITTED; D5 DISCHARGED BY THE V3 ITEM (2026-07-18)

All audit cures are now committed on `constraint-exec-epic`: the separable
package-verification/occurrence-ordering cures in `da3b495`, the entangled cures (profile/compiler
quantity parity, inline-leaf strict wiring, assignment validation) inside `9c0291c` with the v3
work that shares those files, and the R4 test-defect correction in `096c29f`/`8cc20d4`/`aaa579e`
(the inherited-inline "failure" was an invalid empty-`design_attrs` test harness, not a resolver
bug). The addendum's D5 contract choice is discharged by the numerical-profile item. The full
licensed suite (2450/26/8) is the first licensed whole-suite evidence over these cures. Ledgers
closed in `.project/active/constraint-exec-code-quality-remediation/{audit,plan}.md`. Archive via
`/_my_close` after the PR wave merges. The original in-progress record follows below.

The four decision-independent audit cures are implemented in the dirty worktree. Profile-v2
quantity references and the complete admitted arithmetic/ordering operator matrix now compile;
the committed `constraint_inline` snapshot renders and executes with its owner feature wired as a
module input; constraint/catalog assignment validation is transactional and catalog assembly
revalidates before filtering/fingerprinting; and package verification validates digest/path/
fingerprint semantics while normalizing artifact I/O failures. The active design addendum and
amended execution record are in
`.project/active/constraint-exec-code-quality-remediation/{design,plan}.md`.

Focused validation passed **149 tests with 13 license skips** in both normal and optimized Python.
The committed inline snapshot executed under the documented agentic-mbse/TEAx environment (**1
passed**). The exact companion profile suite at `82fef09` passed **113 tests**. Targeted mypy passed
on all five touched production files; touched-file Ruff/format, `git diff --check`, fixture
preservation, and the production placeholder scan passed.

The owner resolved the remaining contract choice on 2026-07-18: preserve the generated numerical
data path and narrow executable admission. The dedicated numerical-profile item is now implemented
and its final combined gates are green. The parent remediation still needs its independent audit
and closeout; the numerical implementation record is not self-certification.

#### Independent audit basis

The independent audit verified the formal-target binding and total occurrence-ordering cures. It
did not certify the full remediation. Exact companion profile v2 still admits quantity-reference
predicates the compiler rejects, while newly admitted non-real equality has no typed generated
input/evidence path. The committed inline-constraint fixture also lowers to a module whose
predicate leaf has no matching input.

Two local boundary gaps remain. Construction-time model validators can be bypassed by assignment,
which can silently drop a mutated constraint during catalog or graph assembly. Package verification
does not validate fingerprint derivation or artifact-path containment, and recorded artifact I/O
can still escape as a raw exception. The affected plan checkboxes were reopened and the unresolved
work is registered in `.project/backlog/BACKLOG.md`. Full evidence is in
`.project/active/constraint-exec-code-quality-remediation/audit.md`.

Independent focused validation passed in normal mode (**174 passed, 5 skipped, 7 deselected**).
The same changed scope under `python -O` produced **173 passed, 5 skipped**, plus the one unrelated
pre-existing assertion-dependent failure. Touched-file Ruff and formatting, `git diff --check`,
fixture preservation, and the placeholder scan passed. Targeted mypy remains non-green on the
imported project surface.

The implementing agent's broader, carried evidence remains: exact companion compatibility **92
passed**; combined remediation **189 passed, 18 skipped**; optimized remediation **138 passed, 18
skipped**; and the unlicensed full suite **2,107 passed, 197 skipped, 7 deselected, 23 failed, 96
errors**, with the failures/errors reported as license-dependent. The independent audit did not
rerun the full suite or reproduce the exact 92-test command, so these results are implementation
evidence rather than independent certification.

The initial remediation pass completed on 2026-07-14 as follows.

The independent code-quality review
(`.project/research/20260713-213722_constraint-exec-pr-code-quality.md`) was verified
finding-by-finding against the code (census numbers reproduced exactly; both "impossible"
model states construction-probed; unary-plus reachability traced through the agentic-mbse IR
builder). Verification disagreed with the review on two points only: graph-extension
*validation* is shared, not duplicated, and its "ordering" is an append counter, not a
reimplemented topo sort. Its pre-merge bar then landed as four commits on
`constraint-exec-epic`:

- `5785055` — ConcreteConstraint/Input model validators + rejection tests (tagged-union
  resolution fields; eligible ⇒ predicate_ir + evaluation_channel; expected_value derives
  from is_negated). Preserved pinned edge: MODELED_DEFAULT's `default_ir` may be None.
- `baca960` — both IR renderers: one-operand render now requires operator `-` (a modeled
  `+x` silently rendered as `(-x)` — reachable, not latent); arity + identifier validation
  in the predicate compiler (raw IndexError → PredicateCompileError).
- `c756fc7` — load-bearing asserts → explicit errors (version pins, same-IR, capture
  presence, eligibility dereferences, most-specific-PartDef) so they survive `python -O`.
- `05690f0` — resolver precedence-under-conflict pins (6 two-rungs-both-match tests) +
  path-grammar characterization (brackets, empty segments, chain-vs-source_name).

Reported gates at the remediation close: licensed suite **2364 passed / 23 skipped** (was 2330/23;
+34 new tests), `tests/fixtures` byte-identical throughout, Ruff clean on the remediation scope,
mypy at the 76 baseline. The independent audit verified touched production files as Ruff-clean; one
touched test file retains five pre-existing whole-file violations. The architectural remainder is
registered as `[CONSTRAINT-ARCH-UNIFY]` (P1) and
`[EXIT-PIN-SEAM]` (P3) in `BACKLOG.md` — merging PR #9 does not bless the current parallel
ladders / triple walker / mirrored live-offline phases as the permanent architecture.

### docs-explainer-refresh — ✅ COMPLETE: audited Certify, pushed to the open PRs (2026-07-13)

Post-CONSTRAINT-EXEC docs + explainer-brief refresh across four repos, run as a full
orchestrated pipeline (spec_review → design → design_review → plan → implement → audit; all
artifacts + stage briefs in `.project/active/docs-explainer-refresh/`). Audit
PASS-WITH-NOTES cured to **Certify**: the three cross-repo legs probe-verified by the
orchestrator (addendum in `audit.md`), Phase 5/7 notes reconstructed. Branches pushed
(sysml-codegen/agentic-mbse full; teax already carried `4c96b99` via a concurrent owner push)
with appended-commit comments on PRs #9 / #11 / teax#3; fusion-tea `bfff2b4f` stays local per
the merge sequencing in Up Next. All 7 phases landed as one commit per phase per repo:
- **sysml-codegen** (`constraint-exec-epic`): `0fad7bf` re-project stale surfaces onto HEAD
  (snapshot v3, ExpressionIR, ModuleKind, lowering phase); `78a6a7d` new doc 29 contracts/sealing
  + CON matrix family + recount to 32 families; `dbc60b8` `EXPLAINER_PROMPT.md` re-anchored + Gen-1
  banner; Phase-7 close-out commit (this one).
- **agentic-mbse** (`constraint-exec-epic`, PR #11): `9e24c93` decision-table reword + durable
  ConstraintFacts/ExpressionIR page.
- **teax** (`constraint-exec-epic`, PR #3): `4c96b99` document `PreparedEvaluator.entry_models`.
- **fusion-tea** (`main`): `bfff2b4f` drop `ToyPlantParams` alias + walkthrough retirement note.

Matrix recount landed at 32 families / 274 reqs / 73 test files (summary/Index/overview agree).
Discoveries surfaced (registered in `.project/backlog/BACKLOG.md`): `[V2-HTML-BUILD]` (the actual
v2 HTML build, [OWNER]: another agent), `[DOC19-DISPATCH-REAUDIT]`, `[MODULEKIND-DOC-SWEEP]`. See
the plan's Implementation Notes for the full per-phase record + the `is_droppable_constraint`
live-symbol deviation.

### PUSH-DOWN epic — INDEPENDENTLY AUDITED + REMEDIATED: CERTIFIED (2026-07-10)

Independent technical audit of PRs #8 (sysml-codegen) / #10 (agentic-mbse) found the code
functionally sound but the certification record over-claiming (SC-D Q4/R8 falsely checked;
Item 1's move not mechanical; mypy 97→98 misrecorded). All findings remediated same day —
full audit + per-finding remediation record:
`.project/backlog/epic_push_down_audit_independent.md`. Remediation highlights: Item 1
expression bodies restored to the mechanical-move originals with the test mocks upgraded to
the real syside shape; Q4 descoped with rationale (its live annotation bug in
dependency_backtracker fixed — surfaced by mypy the moment `py.typed` landed); R8
`# INTENTIONAL DIVERGENCE` marker added; `py.typed` added to agentic-mbse and the
TYPE_CHECKING mirror dataclasses deleted (sysml-codegen mypy 98→77 vs main's 97); TYPE_MAP
inventory tests de-self-certified; `**` added to shared SUPPORTED_OPERATORS; unary-minus
render deviation recorded in Item 4's audit. Post-remediation gates: 2138/4 + 1290/1 green,
ruff src clean, fixtures byte-identical. Epic and prior audit/pre_pr carry correction
addenda. **Note for the PRs: the remediation commits are not yet made/pushed** — both repos
have uncommitted working-tree changes on `push-down-item1-expression`.

### PUSH-DOWN epic — CERTIFIED (superseded by the 2026-07-10 independent audit above)

Epic: `.project/backlog/epic_push_down.md`. Epic audit:
`.project/backlog/epic_push_down_audit.md`.

All four PUSH-DOWN items are implemented and item-audited with `Certify` verdicts. The epic audit
certifies the top-level success criteria SC-A through SC-G against the source concept-design,
boundary research, TRUTH-DEBT sequencing ruling, and item audits. The reusable SysML semantic
helpers now live in agentic-mbse; sysml-codegen keeps transformation policy, Python rendering,
aliases, design overrides, scoping, pipeline assembly, and deferred template/virtual-binding work.
No pre_pr or PR preparation was run during the audit stage. Next stage is whole-epic pre_pr/PR
preparation only.

### PUSH-DOWN Item 4 — Aggregation Decomposition and Compatibility Gates — CERTIFIED

Epic: `.project/backlog/epic_push_down.md`. Artifacts:
`.project/active/aggregation-decomposition/{spec,spec-review,design,design-review,plan,audit}.md`.
Spec review and design review both reached Approved after revision. This item moves neutral
aggregation AST decomposition into agentic-mbse; sysml-codegen keeps Python rewriting, local
`AggregationExpressionData` assembly, pipeline-facing identifiers, alias handling, and downstream
resolution policy. No item-level PR closeout is planned because the user wants the whole PUSH-DOWN
epic implemented before PR.

Implemented `agentic_mbse.sysml.aggregation` with neutral aggregation decomposition, wrapper facts,
diagnostics, dispatch-order guardrails, and no sysml-codegen imports. `SumTerm`, `SingletonTerm`,
and `LocalTerm` now live in agentic-mbse and are re-exported by sysml-codegen as the same runtime
class objects. sysml-codegen's aggregation builder now delegates raw decomposition to the shared
module and renders local `AggregationExpressionData` through a compatibility adapter. The
aggregation-profile loop filed three future rows in agentic-mbse backlog:
`PUSH-DOWN-AGG-PROFILE-SUM-SHAPE`, `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE`, and
`PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE`.

Validation: agentic-mbse aggregation suite `12 passed`; shared expression/hierarchy/aggregation
suite `93 passed`; agentic-mbse full suite `1290 passed, 1 skipped, 33 deselected, 6 warnings`;
sysml-codegen local model/builder suite `166 passed`; sysml-codegen downstream compatibility suite
`202 passed, 1 skipped`; sysml-codegen full suite `2138 passed, 4 skipped`; sysml-codegen
`ruff check src/` clean; touched-file ruff clean in both repos; `git diff -- tests/fixtures` empty.
Audit: `.project/active/aggregation-decomposition/audit.md` certifies the item. Audit reran the
focused high-risk gates: sysml-codegen builder/model/literal/dispatch subset `190 passed`, and
agentic-mbse aggregation suite `12 passed`. Remaining caveat: project-wide mypy baselines are still
dirty but unchanged after cleanup (agentic-mbse 107, sysml-codegen 98). No item-level PR closeout was
performed; continue to the PUSH-DOWN epic audit and PR preparation only through the whole-epic flow.

### PUSH-DOWN Item 3 — Hierarchy Primitives and Data Models — CERTIFIED

Epic: `.project/backlog/epic_push_down.md`. Artifacts:
`.project/active/hierarchy-primitives-models/{spec,spec-review,design,design-review,plan}.md`.
Item 1 and Item 2 are implemented, audited, and committed in both repos. This item starts only
the hierarchy primitive/model split; no item-level PR closeout is planned because the user wants
the whole PUSH-DOWN epic implemented before PR.

Implemented shared `agentic_mbse.sysml.hierarchy` with primitive redefinition and multiplicity
extraction; moved `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` into
agentic-mbse as field-identical standard-library models; sysml-codegen now re-exports the same
runtime class objects and delegates primitive extraction through compatibility wrappers. Design
overrides, aggregation, usage-type indexing, hierarchy orchestration, and `HierarchyExtractionResult`
remain local to sysml-codegen. Hierarchy-profile rows that require codegen policy were filed in
agentic-mbse backlog; missing instantiations remain covered by existing `L6_CALC_DEF_NO_INSTANTIATION`.

Validation: agentic-mbse hierarchy test `10 passed`; agentic-mbse full suite `1278 passed, 1 skipped,
33 deselected`; sysml-codegen focused hierarchy/model/dispatch suite `156 passed`; sysml-codegen full
suite `2127 passed, 4 skipped`; sysml-codegen `ruff check src/` clean; touched-file ruff clean in
agentic-mbse; `git diff -- tests/fixtures` empty. Remaining caveat: project-wide mypy baselines are
still dirty but unchanged for this item (agentic-mbse 107, sysml-codegen 98). Audit:
`.project/active/hierarchy-primitives-models/audit.md` certifies the item. No item-level PR closeout;
continue to PUSH-DOWN Item 4.

### PUSH-DOWN Item 2 — Qualified-Name Utility Split — CERTIFIED

Epic: `.project/backlog/epic_push_down.md`. Artifacts:
`.project/active/qualified-name-utility-split/{spec,spec-review,design,design-review,plan}.md`.
Spec review and design review are both Approved. Implementation is complete on the full
PUSH-DOWN epic branch in both repos, with no item-level PR closeout.

Moved pure qualified-name helpers into `agentic_mbse.sysml.qualified_names`; sysml-codegen now keeps
`sysml_codegen.core.qualified_names` as a compatibility shim and retains codegen-owned module,
channel, parameter, and owning-part builders locally. The `ITEM-SYNC-C8` backlog row was updated
instead of duplicated: the shared sanitizer dependency is gone, while the sibling-scope Level-6
collision collector remains filed.

Validation: agentic-mbse targeted qualified-name suite `21 passed`; agentic-mbse full suite
`1268 passed, 1 skipped, 33 deselected`; sysml-codegen targeted naming/shim suite `52 passed`;
sysml-codegen full suite `2122 passed, 4 skipped`; touched-file ruff clean in both repos;
sysml-codegen `ruff check src/` clean; `git diff -- tests/fixtures` empty. Remaining caveat:
project-wide mypy baselines are still dirty outside this item (agentic-mbse 107, sysml-codegen 98).
Audit: `.project/active/qualified-name-utility-split/audit.md` certifies the item. Next: continue
PUSH-DOWN Item 3.

### PUSH-DOWN Item 1 — Expression Reconstruction Push-Down — CERTIFIED

Artifacts: `.project/active/expression-reconstruction-push-down/{spec,spec-review,design,design-review,plan}.md`.
Spec review and design review are both Approved. Implementation is complete on
`push-down-item1-expression` in both repos.

Moved reusable expression reconstruction, feature-chain, chain-segment, and literal helpers into
`agentic_mbse.sysml.expression`; sysml-codegen now keeps
`sysml_codegen.extraction.expression_utils` as a compatibility shim. Level-6 C7 now uses shared
`is_literal_node`, and the expression-profile close-out filed three follow-up rules in
agentic-mbse backlog.

Validation: agentic-mbse full suite `1247 passed, 1 skipped, 33 deselected`; sysml-codegen full
suite `2119 passed, 4 skipped`; sysml-codegen snapshot-specific suite `87 passed`; touched-file
ruff clean in both repos; sysml-codegen `ruff check src/` clean; `git diff -- tests/fixtures`
empty. Remaining caveat: project-wide ruff/mypy baselines are still dirty outside this item
(agentic mypy 104, sysml-codegen mypy 97, sysml-codegen full ruff 332).

Audit: `.project/active/expression-reconstruction-push-down/audit.md` certifies the item. Next:
run `$my-pre-pr` for PR preparation.

### PIPELINE-TRUTH epic — ✅ COMPLETE (all 10 items landed and audited PASS, 2026-07-06)

**The generated package is the truth.** fusion-tea's models generate, wire, and execute
end-to-end from generated artifacts alone — TRUE ZERO V11 offenders (supplied-value
materializer, Item 2), run-C lcoe bit-exact ($270.1211779380445) with every workaround
deleted upstream (Item 3), constraint drop report subtype-aware incl. `assert` (Item 4),
13 silent-failure findings fixed by family (Item 5), 25 self-referential tests re-anchored
(Item 6), matrix 253 = 249 PASS + 4 UNTESTED-argued + 0 DEFERRED with F2/F4 resolved by
decision (Item 7), dead code cleared + REQ-AST-10 (Item 8), agentic-mbse taught+checked
(Item 9), docs + explainer prompt refreshed and caveats retired (Item 10). Gate:
2069 passed / 4 skipped / 5 xfailed; ruff src 17; mypy src 104. Epic + Lessons Learned:
`.project/backlog/epic_pipeline_truth.md`. Item-10 artifacts:
`.project/active/epic-close-docs/{spec,plan}.md`.

**Human actions outstanding (the only ones):**
1. **agentic-mbse companion PR** — branch `pipeline-truth-item4` is pushed to origin; open
   the PR from `.project/active/pipeline-truth-sync/COMPANION_PR_BODY.md` (base `upstream-findings-sync` while
   PR #7 is open; retarget to `main` on its merge).
2. **Merge PR #7** (the UPSTREAM-FINDINGS agentic-mbse companion, `upstream-findings-sync`) —
   still pending; the Item-4 companion bases on it until it merges.
3. **fusion-tea workaround-retirement PR** — open from
   `chore/retire-pipeline-truth-workarounds` (Item 3 end state).

### PIPELINE-TRUTH Item 9 — agentic-mbse Sync (Guidance, Validation, Companion Audit) — COMPLETE
Phases 0–5 landed 2026-07-06. **C7** (the one unbuilt check) WARNs on `attribute :>> attr =
<expr>` — the AttributeUsage redefinition codegen silently drops; test-first, cross-repo-clean.
**D1–D4/I5** teaching surfaces synced (whole-plant value idiom, secondary shapes, shallow chains,
subtype-aware asserts, Item-5 diagnostics). Prior-epic residue closed: R-F6 verified, R-C8 &
S-F3/S-F4 keep-filed, R-VENDOR & S-F5 declined/discharged, PR #7 stays the human's. Companion
audit (`extract_feature_refs`, `str(direction)`) — both COVERED/STABLE.
- **agentic-mbse** `pipeline-truth-item4`: commits `fa3b706` / `1fab4d6` / `9cc7ab4` (over Item 4's
  four). Suite **1240 passed / 1 skipped**; pushed to origin. Companion PR is the human's to open
  (B1 base-then-retarget: base `upstream-findings-sync` while PR #7 open, retarget to `main` on merge).
- **This repo:** 18-row traceability + acceptance in `.project/active/pipeline-truth-sync/close-out.md`;
  companion-audit evidence, plan, and `COMPANION_PR_BODY.md` alongside; S-F3/F4/F5 dispositions in `BACKLOG.md`.

### PIPELINE-TRUTH Item 3 — fusion-tea Acceptance & Workaround Retirement — CERTIFIED
Audit PASS-WITH-NOTES (`.project/active/fusiontea-acceptance/audit.md`, 2026-07-06). Crux
(runner multi-output completion) confirmed test-harness-only, zero `src/`. All 4 acceptance
tests pass; anchor + perturbed-lcoe (216.55528392479388) arithmetic re-derived independently;
retirement greps zero; both offender states zero with canonical Meier channels; SNAP-19 parity
green over 6 fixtures + fusion_tea leg (license live). Gates 2066/4/5, ruff 17, mypy 104.
Only note: fusion-tea teax executor not re-run in audit (needs their venv) — corroborated via
byte-identical wiring + in-repo executor. Next: fusion-tea PR from
`chore/retire-pipeline-truth-workarounds`.

### PIPELINE-TRUTH Item 5 — Silent-Failure Hardening — SPEC IN PROGRESS
Track B. Spec phase is a verification pass (R4): the D3 floor findings are static-read
verdicts reproduced/refuted before design. Verification table + spec:
`.project/active/silent-failure-hardening/spec.md`; live probes (python execution is
sandbox-blocked, so verdicts rest on code-trace + committed tests):
`.project/active/silent-failure-hardening/probes/`.

### PIPELINE-TRUTH Item 1 — Plant-Value & Blind-Spot Fixtures — IMPLEMENTED (awaiting audit)
Track A head (Items 2, 4, 5, 9 build on its fixtures). Fixtures + captures only, zero
`src/` production code. Spec/plan: `.project/active/plant-value-fixtures/{spec,plan}.md`.
Implemented across 6 commits on `pipeline-truth-epic` (Phases 0–5). Full suite: 2017
passed; ruff src 21 / mypy 109 (baseline unchanged). `/_my_audit` suggested next.

- **D6 gate (PASS):** `plant_values` trips V11 with 3 offenders on module
  `plantvaluesdesign__plant__cost_calc`, covering all three value-provision mechanisms —
  `driver_efficiency` (a, subtype-def literal via retype → redefinition 0.35),
  `target_cost` (b, override BLOCK → design_override 10.0), `chamber_cost` (c, plain one-hop
  cross-part attr with a usage-level DOTTED override → design_override 7.0). All three
  offenders are valueless EPs TODAY **and each carries a captured literal Item 2 flips it TO**
  (audit-F1 cure: (c) is no longer trip-only — the `:>> chamber.cost_per_unit = 7.0` override
  lands in `hierarchy_data.design_overrides`, pinned by
  `test_mechanism_c_plain_cross_part_attr_valueless_ep_with_flippable_literal`). This is the
  SC-1 before-state Item 2 flips; hand-computed after: `plant_cost = (target_cost + chamber_cost)
  / driver_efficiency = (10.0 + 7.0) / 0.35 = 48.571`, constraint `eta*gain>=threshold` →
  `0.35*40.0=14.0>=10.0` holds. Every operand is reproducible from the fixture source (see the
  plan's Phase-4 cure note for file:line).
- **Per-shape labels:** `plant_value_shapes` — CORRECT (bare default, 5-deep chain, quoted
  `'net cost'` output, Style-E, quoted return), DEGRADED (econ-param nested `:>>`,
  inherited-redefined-below), DIAGNOSTIC (non-float enum EP / Item 5). No extractor crash →
  no escape-hatch filings.
- **Rider (own commit):** `quoted_owner_formula` `net_margin`/`total_payout` design-attr →
  computed reclassification reviewed and CONFIRMED (prior-epic UPSTREAM-FINDINGS Item 7
  behavior, not a forward dep). `wi014_toy`/`self_named_binding_trap` = timestamp/path canon.
- **Capture surfaces:** `plant_values`, `plant_value_shapes`, `deep_cross_scope_probe` all
  full-pipeline (extraction snapshot + pipeline baseline). `deep_cross_scope_probe` gained
  its first committed snapshot (closed D1-F6 drift); un-broken by renaming `derived`→
  `derived_calc` (reserved KerML modifier).
- **Downstream handoffs:**
  - **Item 2 before-pin:** `tests/conformance/test_plant_values.py::test_plant_values_trips_v11_all_three_mechanisms`
    (the 3-offender set). Extended `spec_chain_twolevel` carries the value-carrying (c) +
    fan-out for Item 2's SC-B tolerance test.
  - **Item 4/5 substrate:** the `assert constraint viability` in `plant_values` is INVISIBLE
    to extraction today (pinned in `test_plant_values.py`); the non-float enum EP is in
    `plant_value_shapes` (`test_plant_value_shapes.py::test_shape9...`).
  - **Item 9 impact list:** finalized in `spec.md` "agentic-mbse impact — Item 9 accumulation
    list" (concrete fixture paths); deferred shapes in
    `.project/active/plant-value-fixtures/fixture-gap-register.md`.
- **Known degradation surfaced (filed):** multi-hop CHAIN `source_path` truncates to the
  first segment (why (c) is one-hop; `deep_cross_scope_probe` Pattern A pins it).

### PIPELINE-TRUTH Item 2 — Whole-Plant Cross-Part Value Resolution — CERTIFIED (PASS-WITH-NOTES, 2026-07-06)
Audit: `.project/active/whole-plant-resolution/audit.md`. 10→0 offenders verified structurally
(all clear by synthesis; 10 applied → 7 source-QN EPs via dedup, **zero** collision-defers).
One doc correction owed before close: the Phase-7 close-out misattributes the clearing path as
"collision guard defers, real wins" — no real-wins defer fired; fix the narrative (no code change).

Track A headline (gates fusion-tea). Value-fill via the supplied-value materializer
(`resolution/supplied_values.py`, REQ-SVM-01..04): a pre-pass synthesizes design
attributes for cross-part/in-part supplied values, keyed by source QN, merged into
`design_attributes` before the backtracker. Plan/design/spec:
`.project/active/whole-plant-resolution/`. **All 8 phases landed** across commits
2de8f60→(Phase 8), acceptance ladder held:
- **SC-1**: `plant_values` zero offenders; a/b/c → 0.35/10.0/7.0 on source-QN EPs; anchor
  `(10+7)/0.35=48.5714` hand-transcribed (INV-5).
- **SC-1d**: `'Flow Sub'` flips DEGRADED→8.0 via tier-2b direct-owner leg.
- **SC-4 (epic CSF)**: committed fusion-tea v2 snapshot (`tests/fixtures/fusion_tea`)
  → **TRUE ZERO** V11 offenders (8 cross-part a/b/c + 2 in-part d), full YAML emits
  license-free. Item 3 reuses this v2 capture + the SC-3 runner.
- **SC-3**: `tests/runtime/pipeline_runner.py` (pinned signature) executes twolevel to
  lcoe=100.0 within rel 1e-6.
- **SC-5**: four cross-part baselines byte-identical (catf_mfe, ife_plant); V11 raise-proof
  re-anchored to Shape 1 (`rated_cost.rate`).
- Suite 2056 passed / 4 skipped / 5 xfailed; ruff 17, mypy 104 (baselines unchanged).
- **Two documented deviations** (see plan Implementation Notes): materializer runs at the
  caller seam (not inside `build_computation_graph`, which post-dates the backtracker);
  precedence + renamed-consumer proven at the mechanism/real-fusion-tea level rather than
  via bespoke captured fixtures. `/_my_audit` suggested next.

### PIPELINE-TRUTH Item 4 — Subtype-Aware Enumeration & Constraint-Report Truth — AUDITED: PASS-WITH-NOTES (2026-07-06)
Track B head (no deps). Coordinated pair with agentic-mbse (R2): one adapter choke
point (`include_subtypes`), per-call-site decision table, constraint drop report fires
on assert constraints, REQ-EXT-09 re-anchored independently, snapshot constraint
serialization. Spec: `.project/active/subtype-enumeration/spec.md`. Audit:
`.project/active/subtype-enumeration/audit.md`.
- **Codegen side solid** — verified by artifact/source: collect/render split, REQ-EXT-09
  re-anchor with executable mutation check, full serialize→replay chain (from-snapshot
  report available), INV-B/D/E/G pins, dead-code deletions, docs rewrite, all 23 committed
  snapshots at v2, wi014 assert manifest committed.
- **Note 1 (gate disclosure):** the Phase-5 reviewed-diff gate under-itemized
  `self_named_rescue` — its v2 diff carries a `binding_type` reference→chain reclassification
  filed as "relativization." NOT Item-4-caused (Item 4 touches no binding code) but the
  gate's itemization is inaccurate; re-itemize + pin/justify the reclassification.
- **Note 2 (fusion-tea):** no committed fusion-tea snapshot exists in this repo, so the
  "wi014 AND fusion-tea" SC is only half-met here; the v2 hard-gate now rejects any external
  v1 fusion-tea snapshot until Item 2 re-captures it — carry to Item 2's SC-A/SC-4.
- **Note 3 (limit):** sandbox blocked all code execution + all agentic-mbse access, so both
  suites green, ruff/mypy (20/105 claimed), a live mutation run, and the entire agentic-mbse
  half (rows 5–8, decision table, TYPE_MAP, Level-3 circular-FAILS) are plan-recorded only,
  not re-executed. Needs a licensed/unsandboxed confirmation run before epic close.

### PIPELINE-TRUTH Item 8 — Dead Code & Cleanup Debt — IMPLEMENTED (2026-07-06)
**All 6 phases landed on `pipeline-truth-epic`** (`3314264`, `d5032c3`, `529dc74`, `3ec4efa`,
`024028b`, `b1dece5`). Tree GREEN: **suite 2000 passed / 4 skipped / 5 xfailed; ruff src 19;
mypy src 104** (both better than the 20/105 gate). SC-G clean: zero grep hits for all 12 deleted
symbols. Row-D aggregation-literal bug fixed under a passing byte-identity gate (reproduced RED
first on `agg_literal_probe`; REQ-AST-10 governs it). Count story: net **−5** passed (2005→2000) =
−11 deleted dead-symbol self-tests + 6 new pins/probe. Every D1 residue dispositioned to FILE/NO-OP
(`[SANITIZER-MERGE]`, `[SC11-IMPORT-REWRITE]`, `[GB-PARAMGROUPS-TYPING]`). Handoffs live:
`[ITEM7-PGD06]` activated + REQ-AST-10 flagged for Item 7; doc-19/doc-25 caveats to Item 10.
**Next: `/_my_audit`.** Full close-out in `.project/active/cleanup-debt/plan.md`.

<details><summary>original spec-stage description</summary>

Track B, no deps (schedule before PUSH-DOWN). One reviewed pass: delete two dead
templates + verify-then-delete four dead functions (DOCS-SCRUB-F1), fix four stale
docstrings (F3), fix the `_walk_aggregation_ast` literal-before-invocation dispatch bug
(R4 reproduce + byte-identity gate + literal-bearing fixture; retires doc-19 hedge), pin
the dotted-leaf alias edge (retires doc-25 hedge), disposition D1 residue F1–F5, assess
SC-11 import rewrite, drop 4 vacuous skipifs. Handoffs: `_deserialize_constraint_info`/
`extract_all_constraints` → Item 4; REQ-PGD-06 re-frame → Item 7; doc caveats → Item 10.
Sequencing: agg-fixture capture runs entirely before OR after Item 4's snapshot v2 bump,
not interleaved. Spec: `.project/active/cleanup-debt/spec.md`.

</details>

### PIPELINE-TRUTH Item 6 — Self-Referential Test Remediation — audited PASS-WITH-NOTES (2026-07-06)
Track B, no deps. Re-anchor the 25 §D5 flagged tests (7 HIGH + 10 MEDIUM + 8 LOW) to
hand-transcribed fixture literals; convert `test_localterm_sibling_agg_output` (MF-07)
from pass-or-skip to pass-or-FAIL; re-anchor REQ-REG-02 to on-disk paths; add SC-6
render pins + a tests/conformance anchoring note. EXT-09 handed off to Item 4. Matrix
rows are Item 7's. Spec: `.project/active/test-truth/spec.md`.
**Audit (`.project/active/test-truth/audit.md`):** anti-pattern gone (static sweep + 5
spot-checks); 5 literals independently confirmed vs committed snapshots; −26 count = param
reduction + 4 new fns, no fn deleted; all 25 dispositioned; EXT-09 handoff clean; doubling
notes present; README accurate. **Open (1 note):** the mutation spot-check (SC-2) could not
be reproduced at audit — pytest gated in the non-interactive stage context; corroborated
statically + by the orchestrator's live gate (2005/4/5) + the close-out's 3 RED→revert→GREEN.
Recommend one licensed reproduction to close SC-2.

### PIPELINE-TRUTH epic — DEFINED (Draft, awaiting scope review)
Shaped 2026-07-06 from `.project/active/NEXT_EPIC_PROMPT.md` via `/_my_epic_plan` with
the mandated 8-agent discovery sweep. Mission: the generated package is the truth —
fusion-tea generates/wires/executes end-to-end, zero bridges; every diagnostic fires on
the shape it claims; zero self-referential tests; REQ/matrix truth. 10 items,
~10.5–13.5 days, two tracks (headline: Items 1–3 fixtures → whole-plant resolution →
fusion-tea acceptance; truth track: Items 4–8 parallel; 9–10 close).
- Epic: `.project/backlog/epic_pipeline_truth.md`
- Evidence base: `.project/research/20260706_pipeline-truth-discovery.md` (D1–D7 +
  adversarial; 16 silent-failure sites, 25 tests-that-cannot-fail, the D6 fixture
  recipe reproducing 9/10 V11 offenders, subtype-blind enumeration verdict table incl.
  agentic-mbse's always-passing Level-3 validator)
- BACKLOG updated: PIPELINE-TRUTH added (P1), whole-plant item promoted out of Ideas,
  [CONSTRAINT-SILENCE] filed (P1, absorbed into Item 4), UPSTREAM-FINDINGS moved to
  Completed, PUSH-DOWN sequencing ruling recorded (after Items 5+8).
- Notable corrections made during discovery: the fusion-tea report's line-74
  capture-path claim is wrong (capture DOES run the constraint report; the silence was
  the assert bug itself), and constraints are NOT serialized into snapshots (the
  NEXT_EPIC_PROMPT claim was wrong; `_deserialize_constraint_info` is dead code).
- Next: user reviews scope/decomposition; then spec Item 1 (fixtures) and Item 4
  (subtype enumeration) — the two no-dependency track heads.

### docs-scrub — CERTIFIED and MERGED (PR #4, 2026-07-06)
Post-epic coherence pass over `docs/architecture/` on branch `docs-scrub` (off
`upstream-findings-epic`): 31 docs verified/corrected against HEAD; matrix now
248 = 236 PASS + 12 UNTESTED (SNAP/NC/REG rows added); thin docs 07/10/11/17/24
closed; 22/23 verified live, 26 marked Historical; gate byte-identical
(1989/4/5, ruff 21, mypy 109). Independent audit: Certify (3 gaps found+cured).
Follow-ups filed: BACKLOG DOCS-SCRUB-F1..F4 (F4 = resolve_input() has zero
production callers while its REQs are marked PASS). Artifacts:
`.project/active/docs-scrub/{spec,plan,fact-sheet,audit}.md`.

### Next-epic definition — EXECUTED (2026-07-06)
`.project/active/NEXT_EPIC_PROMPT.md` was executed; deliverables are the
PIPELINE-TRUTH entry above. The prompt file is kept for provenance.

### UPSTREAM-FINDINGS Epic — MERGED (PR #3, 2026-07-06)

All 12 items landed and audited PASS on branch `upstream-findings-epic`
(orchestrated run, 2026-07-05..06). PR: https://github.com/1cFE/sysml-codegen/pull/3

**One action for the human**: the companion agentic-mbse PR. Branch
`upstream-findings-sync` is pushed to origin (6 commits); the prepared PR body is
committed at `.project/active/AGENTIC_MBSE_PR_BODY.md` — create with:
`gh pr create --repo 1cFE/agentic-mbse --base main --head upstream-findings-sync --title "UPSTREAM-FINDINGS sync: validation checks + guidance for the newly supported subset" --body-file .project/active/AGENTIC_MBSE_PR_BODY.md`

Post-merge follow-ups already filed: BACKLOG P1 (remaining 10 fusion-tea
cross-part bindings), the stale-fixture drift chore, C7/C8/F6 in agentic-mbse's
backlog, and the fusion-tea coordination notes in the three release-notes files.


## Recently Completed

### 2026-07-13: CONSTRAINT-EXEC Epic — Constraint Execution and Design-Space Studies
- All 15 items (0–14) implemented, adversarially reviewed, and audit-certified across four
  repos in one orchestrated run; independent findings audit reproduced every sampled claim
  exactly (`completed/20260713_epic_constraint_execution_audit_independent.md`).
- Modeled `assert constraint` now lowers to Kleene-compiled graph modules + exact-schema report
  aggregator; snapshots carry constraint facts (v3); packages seal with verified-on-load
  contracts; crash-safe study layer (evaluator → store/runner → policy/query/CLI); IFE
  acceptance 2294/2301 + 7 model-favoring boundary rows ([OWNER] ratified); hand viability rule
  deleted. CE-F3 fixed post-run (teax `0d606a4`); CE-F1/F2 registered follow-ons.
- Gates at close: sysml-codegen 2330/23, mypy 76 baseline, ruff clean; agentic-mbse 1401/1;
  teax fully green 262 (pre-existing path bug also fixed, `1b63272`).

### 2026-07-08: TRUTH-DEBT Epic
- Archived all six audited items plus the epic ledger to `.project/completed/`.
- Retired the F4 aggregation cutover, resolved multi-hop chain support, matrix test gaps,
  inherited-attr classifier fix, matrix sweep residue, and D3 hygiene tail.
- Pre-PR gates: 2120 passed / 4 skipped / 0 xfailed; ruff src clean; mypy src 97;
  matrix 259 = 258 PASS + 1 UNTESTED.

### 2026-02-17: Phase 5 — E2E Pipeline Validation (5.2) — Checkpoint 5
- 16 conformance tests in `tests/conformance/test_pipeline_e2e.py`
- catf_mfe baseline generated: 42 modules (all CalcUsage), 8 EP groups
- Baseline comparison for all 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-01 through REQ-PIPE-06 validated end-to-end
- Checkpoint 5: All 4 models match baselines — refactored pipeline composes correctly
- No production code changes — conformance-only

### 2026-02-17: Phase 5 (partial) — Orchestrator Step Ordering (C19)
- 39 conformance tests in `tests/conformance/test_orchestrator.py`
- Static analysis: `build_pipeline_context()` 10-step DAG ordering verified
- FORMULA removal safety net verified (zero natural overlap in fixtures; constructed overlap exercises logic)
- Registry 4-phase ordering: all aliases target Phase 1 canonical channels (solar_battery + catf_mfe)
- Pipeline invariants (PIPE-01–06) verified across 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-07 baseline: 9 generation/ files import from extraction/analysis (Phase 7.6 target)
- No production code changes — conformance-only

### 2026-02-17: Phase 4 — Module Factory + Graph Assembly
- C14 CalcUsage Factory (48 tests), C15 FORMULA Factory (34 tests), C16 Aggregation Factory (32 tests)
- C17 Entry Point Classification (35 tests), C18 Graph Assembly (34 tests)
- Checkpoint 4 baseline comparison: solar_battery, chain_spike, attr_expr_probe match Phase 0 baselines
- All 3 module types verified (CalcUsage + FORMULA + Aggregation)
- Baseline normalization documented: CalcUsage compilability (snapshot serialization boundary), parameter ordering (dict iteration order)
- All design doc amendments applied (06-entry-point-classifier.md, 11-analysis-backtracker.md)

### 2026-02-17: Phase 3 — Analysis Components
- C11a Backtracker Conformance (43 tests), C11b Typed Dispatch Migration (17 tests)
- C12 Input Resolver (26 tests), C13 ParameterGroupDeriver (30 tests), X02 Dual Resolution (20 tests)
- Backtracker fully migrated to typed dispatch: scoped_lookup/sysml_qn_lookup/alias_lookup
- `_compat` dict, `resolve()`, `register()` removed from OutputRegistry
- 14 previously compat-only resolutions (12 catf_mfe + 2 solar_battery) now typed
- D3: Static analysis helpers extracted to `tests/helpers/static_analysis.py`

### 2026-02-17: Phase 2 — Core Infrastructure Spikes
- C08 Output Registry (32 tests), C09 Virtual Binding Rewrite (38 tests), C10 Aggregation Scoping (47 tests)
- 5 NewType wrappers + 3 typed registries implemented
- Phase 2 audit: 6 fixture coverage gaps investigated (C1-C6), 4 closed, 1 partially closed, 1 pending

### 2026-02-17: Phase TRR — Typed Registry Refactor (Design Docs)
- All 8 TRR design doc updates applied (docs 03, 04, 09, 10, 11, 15, 24, 27)
- New design intent doc: `27-typed-registry-refactor.md`

### 2026-02-17: Phase 1 — Foundation & Extraction Components
- C01-C07, all 49 requirement IDs verified

### 2026-02-17: Phase 0 — Test Infrastructure & Baselines
- Extraction snapshots for 6 models, pipeline baselines for 4 models

### 2026-02-10: COST-PATTERN Items 1-4
- Hierarchy-aware codegen: templates, redefinitions, aggregation, pipeline integration

---

## Up Next

1. **Merge the CONSTRAINT-EXEC PR wave** (human): agentic-mbse #11 FIRST — **now load-bearing,
   not just convention**: #9's codegen pins `executable-profile/v3` at runtime and refuses the
   pre-v3 profile, so merging #9 before #11 (at `05cde35`) breaks main. Then sysml-codegen #9;
   teax rwestwood89/teax#3 independent; after #11+#9 merge, push fusion-tea:
   `git -C ~/1cfe/fusion-tea push origin main` (4 acceptance commits waiting). Note: agentic-mbse
   local branch tip `4ed2a07` ("modeling workflow orchestrator", separate workstream) was
   deliberately NOT pushed — PR #11 was updated by ref to `05cde35`; that commit awaits its own
   owner. After the wave merges: `/_my_close` for numerical-constraint-profile + the remediation.
2. **pipeline_explainer_v2.html build** (`[V2-HTML-BUILD]`, P2): the refreshed
   `EXPLAINER_PROMPT.md` is landed and buildable — another agent picks this up.
3. **CE-F1/F2 follow-ons** (BACKLOG): direct TEAx consumption of codegen's embedded catalog with the
   alternate catalog schema/materializer removed, plus multi-channel CandidateBridge (teax). CE-F3
   is fixed.

---
