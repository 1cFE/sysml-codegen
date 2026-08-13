# Changelog

Historical record of completed work.

---

## [2026-08-13] - [CONSTRAINT-SEMANTICS Item 5] CATF Derivative and End-to-End Acceptance

**Type**: Item (orchestrated run; audited *Needs work* → two blocking findings cured same day →
re-verdict **Certify-with-residuals**, SC-2 earned)
**Duration**: spec 2026-08-13 → closed 2026-08-13 (same day)
**Archived to**: `.project/completed/20260813_catf-constraint-policy-acceptance/`
**Commits**: codegen `886a11f..ba51980` (branch `item7-rebuild`, unpushed) / companion untouched /
TEAx untouched on `constraint-semantics-item3` @ `5b70ae9` (the acceptance lane runs against that
checkout; nothing pushed, no `main` touched anywhere)

### Summary
The constraint-semantics contract was built across Items 1–4 and verified only against purpose-built
fixtures. This item ran it end to end on the richest model in the tree. `catf_mfe_d5` carries 65
authored constraint usages and executes **zero** of them, so it reports `not_assessed` and nothing
in it has ever contradicted its own design point — that is the counter-example the epic exists to
close. A derivative, `catf_mfe_gated`, was forked from it under an owner-ruled disposition for all
65 usages, and driven through generation, sealing, execution, TEAx policy, and durable case storage
on all three routes.

The result: 47 modules, 58 usage rows, 2 executing gates (A2, A3), histogram `{eligible 2,
excluded 3, non_reaching 53}`, coverage `58 / 2 / 2 / 0 / 0 / {} / complete`. The cross-fixture
accounting identity is **65 = 58 carriers + 7 named deletions** — the SC-3 amendment the owner
authorized when the ruled `derive-instead` deletions made "exactly 65 carriers" arithmetically
wrong — and it is machine-proved by `scripts/check_gated_manifest.py --check`, which also ties each
deletion to the derivation that replaces it in source. Expected outputs were committed before the
confirmation run (`1247a3b` → `7369b3e`) and were not reverse-engineered afterwards.

### Deliverables
- `spec.md`, `owner-disposition.md` (the RULED all-65 table), `design.md`, `design-review.md`,
  `plan.md`, `verification.md`, `audit.md` (8 findings + cure addendum + re-verdict),
  `product-lens.md` (spec/design/design-2/audit blocks, gate CLEAR), `briefs/`, `probes/`,
  `cryo_derivation.py` (runnable, self-checking, reproduces the executed cryo value bit-exactly).
- Product artifacts staying in the tree: the derivative fixture `tests/fixtures/catf_mfe_gated`
  and its `PROVENANCE.md`; `scripts/check_gated_manifest.py`; the expected-coverage ledger row;
  the SC-8 committed-bytes golden; `tests/fixtures/catf_mfe_d5/PROVENANCE.md`'s corrected
  acceptance paragraph (the only byte moved on either frozen twin).
- Gates at audit: licensed suite **2106 passed / 34 skipped / 1 known pre-existing failure**
  (`test_the_lane_runs_the_real_simkit`, collection-order artifact, out of floor), **zero
  license-skip lines**; ruff 12; mypy 55; `git diff --check` clean; `make_d5_variant --check` 0
  problems ×3; manifest identity closes 65 = 58 + 7.

### Decisions and deviations
- **Three owner rulings amended inherited criteria**, all recorded with provenance in the epic's
  Item 5 section: **item5-F1** — SC-3 becomes the accounting identity 65 = 58 + 7 (owner-authorized;
  the original wording predated the ruled deletions). **D-S1/D-S2 option 3** — A5, A6 and A9 are
  marked `blocked-by-defect` and their ruled intent is *held*, not withdrawn, because the unit-lane
  port defect makes their target forms unbuildable ([AGENT] ratified by owner). **6-D option (a)**
  — candidates are labeled gate-feasible/gate-infeasible under the model as authored, and the
  authored point is the reject candidate ([AGENT] ratified by owner).
- **Two epic items were filed out of the D-S1/D-S2 ruling**: Item 8 (unit-lane port metadata
  defect, standalone by a later owner ruling) and Item 9 (derivative upgrade under held intent).
  A5/A6's ruled basis and A9's **[OWNER] 1% relative** tolerance stay in force and are Item 9's
  input, at the archived `owner-disposition.md`.
- **Three toolchain limits found, all "correct authoring, toolchain refuses" class**: unit-lane
  port metadata (epic Item 8); `@inapplicable:` markers silently dropped on inline-predicate
  constraints (`[INLINE-PREDICATE-MARKER-DROP]`, so B1–B5's inapplicability is recorded in
  PROVENANCE instead — epic Item 7 documents the two mechanisms, Item 9 retires the workaround);
  catalog fingerprint not route-portable (`[CATALOG-FINGERPRINT-ROUTE-PORTABILITY]`, pre-existing,
  reproduces on the untouched frozen twin).
- **Residuals homed at close**: A-4 → `[GOLDEN-BYPASSES-RUN-CODEGEN]`; A-5 →
  `[CATF-ACCEPTANCE-LANE-MANUAL]`; A-8 → epic Item 7's verification-matrix reconciliation pass;
  A-7 (satisfied leg probe-asserted) accepted as recorded, no vehicle needed.
- ADR/product-ledger infra is still absent in this repo (no `.project/adr/`, no `.project/product/`,
  no `adr.sh`/`product.sh`); the coverage-truth promise home is epic Item 7's owner checkpoint, so
  nothing was hand-minted here.

### Lessons Learned
- **The founding failure mode was demonstrated and closed by the same item.** The first execution
  of these gates caught a model defect that had been invisible for the CATF model's entire life:
  the magnet cryoplant draws 8396.05 MW against 1546.72 MW of gross electric output (5.43×), so the
  authored design point is rejected on physics before any mutation. Root cause `heat_leak =
  magnet_volume * 0.05` (`library/analyses/thermal_loads.sysml:59`) — 116.72 MW of static heat leak
  into a 20 K system, filed `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` P1. This is exactly the epic's
  critical success factor — a design search can tell a candidate that passed its physics gates from
  one nobody checked — working on its first real outing, against a defect nobody was looking for.
- **De-risk probes must generate, not only elaborate.** Phase 1 was designed as the cheap place to
  find refusals before an atomic fixture landing, and it re-elaborated after every edit group. It
  never ran generation, so the five **generation preflights** went untested — and one of them then
  refused the ruled A2 spelling at Phase 6, because `value` is a reserved generated local. Elaboration
  admitting is only half of "it lands"; any probe gating an atomic landing needs a generation step.
- **An expectation can be wrong in a way no cross-check catches**, because it encodes an assumption
  about the world rather than about the code: `expected-coverage.md`'s headline cell said
  `full_satisfaction` on the reasonable assumption that a model's authored design point satisfies
  its own gates. Every count around it was right. Only running the physics could tell.

---

## [2026-08-13] - [CONSTRAINT-SEMANTICS Item 4] Predicate Defect Hardening

**Type**: Item (orchestrated run; audited Certify-with-residuals → all findings cured same day,
F5 resolved by owner ruling at close)
**Duration**: spec 2026-08-13 → closed 2026-08-13 (same day)
**Archived to**: `.project/completed/20260813_constraint-predicate-hardening/`
**Commits**: codegen `7f1b943..886a11f` (branch `item7-rebuild`, unpushed) / companion `0a52942`
in `/home/reid/1cfe/agentic-mbse-item7-rebuild` (one file, `executable_profile.py`) / TEAx
untouched on `constraint-semantics-item3`

### Summary
Two reproduced defects sat exactly on the boundary a modeler crosses when writing an asserted
physics gate (must-fix per rulings Q8): a unit-annotated literal such as `8.55 [m]` in an
asserted predicate raised `SI_OCCURRENCE_MISSING` because the reference walk recursed into the
`[` annotation's second operand (`SI::metre`), and the blocked-feature-chain diagnostic was the
tautology `feature_chain: block_feature_chain` — no reference, no location, no rewrite. Both are
now cured under the product's one existing rule ("a unit annotation contributes its value and
never a reference"): one unwrap at the head of `_expression_references` (Defect A), one at the
binding read (the fourth lane, `in tol = 0.05 [m];`, found during spec and cured under the
recorded same-rule test), and a companion `message=` at both chain-block sites that codegen
de-duplicates and orders on one normalized key (Defect B). The pinned end state is a *working*
gate — admitted, catalogued, assessed, on an inequality — not the absence of an error code.

The admitted set changed only by the two named annotation shapes; chains stay blocked,
equalities stay untoleranced, BLOCK still halts. All 23 `block_*` reasons reconciled against
the promise "the generation error names the exact construct to fix"
(`reason-codes-reconciliation.md`).

### Deliverables
- `spec.md`, `design.md` (rev 2 after Revise review, 7 must-fixes applied), `design-review.md`,
  `plan.md`, `verification.md` (8 deviations + cure addendum), `audit.md` (7 findings + R1–R7
  orchestrator probe addendum), `product-lens.md`, `reason-codes-reconciliation.md`, `briefs/`
  (every stage brief), `probes/` (companion evidence + captured red).
- Codegen: walk-head + binding unwraps in `elaboration/elaborate.py`; `_render_block_reasons`
  de-dup/order; five new fixtures; three characterization files (red-first, strict-xfail, red
  captured); `modeling-assumptions.md` §8 worked message + unit-authoring rules; the coverage
  ledger's durable home moved to `tests/unit/data/` (owner ruling, F5).
- Companion (`0a52942`): `_feature_chain_message` naming the joined written chain at both block
  sites; no `REASON_CODES` change.
- Gates: codegen full licensed suite **2010/34/0**, zero license-skip lines; `ruff check src`
  **12**; `mypy src` **55**; companion **1821 passed / 10 pre-existing failures** (failing node
  IDs proven identical with the change reverted), ruff 1 / mypy 108 at baseline;
  `git diff --check` clean; frozen twins byte-untouched.

### Decisions and deviations
- Fourth lane cured in-scope under the orchestrator's pre-recorded rule (same rule, one more
  lane); an annotated *chain* in a binding is admitted (design's named set), pinned on both
  sides of the refusal bound.
- Two limits surfaced and parked for Item 5 (carried into the epic's Item 5 section): a unit on
  a constraint binding is dimensionally inert to the profile, and a blocked chain's location is
  the usage's line, not the term's.
- R6 measured D1's blast radius: deleting the cure fails exactly 7 Item-4-fixture tests,
  nothing else. R5 proved the flagged assertion rewrite concealed nothing (naming artifact).
- Process residual, recorded at close: the product-lens ledger has spec + design blocks only
  (both DISPOSED); no plan/implement/audit-stage entries — same class Items 2/3 carried.
- ADR/product-ledger infra absent in this repo (no `adr.sh`/`product.sh`); the F5 durable-home
  ruling and the block-diagnostic promise are recorded in the item artifacts, the epic, and
  `modeling-assumptions.md` §8 respectively.

### Lessons Learned
[TODO: Add lessons learned]

---

## [2026-08-13] - [CONSTRAINT-SEMANTICS Item 1] Contract and Authoring Policy

**Type**: Item (orchestrated run; audited Certify-with-residuals → H-1/M-1/M-2 cured, M-3 ratified
at close)
**Duration**: spec 2026-08-12 → closed 2026-08-13
**Archived to**: `.project/completed/20260813_constraint-semantics-contract-amendments/`
**Commits**: codegen item tip `76e3ab7` (branch `item7-rebuild`, unpushed) / companion `dcb187b` in
`/home/reid/1cfe/agentic-mbse-item7-rebuild` (five documentation/guidance files, none under `src/`
or `tests/`) / TEAx untouched

### Summary
The constraint-semantics contract was settled, and nothing a modeler or an implementing agent
actually reads said so. The ratified lifecycle contract and its frozen requirements companion still
defined the old headline and disposition behaviour; no ADR recorded the intentional
coverage-vocabulary change; seven documentation statements across both repositories taught that a
bare `constraint` or a `require constraint` is an enforced gate, or cited a retired test as living
totality evidence; and the blessed authoring pattern was unpublished. This item is the documentation
half of the owner's required sequence — settle semantics, fix the documentation to match, *then*
test — so Items 2–5 build against text that agrees with the contract they implement.

What published: **ADR-009** as a numbered section in `docs/architecture/modeling-assumptions.md`,
quoting what invariant 33 and LC-E11 said before and carrying `[AGENT] (ratified by owner,
2026-08-12)` with its challenge route stated; contract amendments to invariants 1, 9, 28, 32, 33,
46/46a and 48 plus new invariant 61, an Appendix B row and three Appendix C cells; companion
amendments to LC-E05/E06/E10/E11/E12 and LC-G07 plus new LC-E13, every `[INHERITED]` grade left
intact; the **applicable asserted gate** membership test defined where it is first used, the
inventory-versus-feasibility split, the six headline states with their precedence in both
vocabularies, and the blessed assert-with-bindings gate shape with its three carve-outs; the
four-class equality-intent taxonomy with the owner's narrow-bands reason and the rule that
tolerances are modeler-chosen; D1–D7 corrected at their locations across both repositories.

Nothing executable changed. The Python diff is one module docstring and two
test-docstring/comment citations of a retired test, verified line by line at audit.

### Deliverables
- `spec.md`, `spec-review.md`, `design.md`, `design-review.md`, `plan.md` (91 checkboxes with
  completion notes), `verification.md` (pre-edit and post-edit sweeps with per-hit dispositions,
  the pairwise precedence-agreement check, the RI-1..RI-7 discharge table), `audit.md` (+
  orchestrator probe addendum), `product-lens.md` (spec + close blocks), `briefs/`.
- Codegen: ADR-009 §9 in `modeling-assumptions.md`; amended
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` and
  `.project/concepts/constraint-execution-lifecycle-requirements.md`; D1/D2/D6/D7 corrections in
  `modeling-assumptions.md`, `reference/28-constraint-lowering-and-catalog.md`,
  `reference/01-extraction.md`; the dated "re-grade pending, Item 2" pointer at
  `verification-matrix.md:336`; two future-capability lines filed in `BACKLOG.md`.
- Companion (`dcb187b`): D3's reason substituted with the row-1 subtype enumeration preserved
  verbatim, D4 and D5-b..f corrections, the four-class equality taxonomy rendered in full in
  `docs/patterns/constraints.md` with its ADR-009 cite and not-a-second-authority clause.
- Gates: `check_doc_distinctness.py` **31 documents / 0 identical-content groups**;
  `git diff --check` clean in both repositories; companion
  `tests/test_validation/test_item9_checks.py` **2 passed** on a licensed run. No suite was re-run
  at close — the verification record stands.

### Decisions and deviations
- **M-3 ratified at close, not reversed.** The 52 companion sweep hits in `docs/sysmlv2/` and
  `docs/syside/` stay aggregated into four rows by term and corpus — every file named, every count
  given, one uniform "out of class — vendored upstream reference corpus" disposition. Project-
  authored hits are still one row each. The aggregated class is the OMG specification, the standard
  library, and generated SysIDE API documentation, which this item has no authority to amend; the
  audit reproduced all five sweep terms independently. Expanding to 52 rows adds rows, not
  information. The deviation from the spec's raw-hit-list wording is recorded as a decision.
- **D5-a: `require constraint` kept inside the requirement-def example**, against the design's
  instruction to swap the form, with a settled-semantics sentence added instead
  (companion `claude/agents/sysml-expert.md:124`). The audit judged this **sounder than the
  design's instruction**: the nested `require constraint` is the SysML v2 idiom that makes a
  constraint requirement-side at all, so substituting `assert constraint` would have taught invalid
  requirement modeling and deleted the visible requirement-side form ruling Q7 exists to preserve.
  The published rule never forbids the form — it says the form never executes and the assert family
  is the sole enforcement opt-in. Recorded with its reasoning *before* it was taken.
- **Invariant 61 and LC-E13 were minted by the implementer** and stamped
  `(ratified by owner, 2026-08-12)`. The owner did not see those texts; their substance is the
  umbrella's Q3 warning tier, which was ratified that day. A challenger re-derives against Q3's
  reasoning, which is the correct route for an agent-with-ratification grade.

### Carried forward (not closed by this item)
- **Both deliberate hand-offs are DISCHARGED**, recorded at close: Item 3's token migration
  corrected the four `all_satisfied` assertions in `tests/execution/`, and Item 2 landed
  REQ-EXT-09's replacement totality proof (`test_constraint_population_oracle.py` plus 42 reviewed
  expected-population files) and performed the REQ-EXT-09/REQ-CL-04 re-grade.
- **Residuals other closes homed against "Item 1's authoring guidance" are re-homed to epic
  Item 7**, not reabsorbed here: Item 3's design-F2 (the Appendix C vacuous-gate cell), the D9
  advisory guidance, and item3-F2 (the unreachable `BLOCK`ed-asserted-usage clause, still a
  surfaced premise conflict in both directions).
- **The parked D-2 vs D-4/SRC-01 premise conflict stays parked** at the umbrella level
  (`.project/active/constraint-semantics-contract/spec.md:325`), verified byte-untouched across the
  item range at close. It needs the owner.
- **No product-promise entry was filed and no id was hand-minted** — this repo still has no
  `.project/adr/` or `.project/product/` ledger and no `adr.sh`/`product.sh`. Item 1's decision
  record is ADR-009 itself. The coverage-truth promise needs an owner-originated statement, which
  is epic Item 7's first beat.
- **The umbrella shaping folder `.project/active/constraint-semantics-contract/` stays active** —
  it is cited by every item and archives at epic close.

### Lessons Learned
- **Documentation-first only works if the documentation is written from the settled rule, not from
  the code.** The spec's hardest constraint was that no amendment may soften toward today's
  behaviour; where the published text describes a target it says so and names the item that makes
  it true. That is why Items 2–4 could build against it while the code still disagreed.
- **A definition nobody owns is the one that goes missing.** "Applicable asserted gate" is the term
  every state meaning, the precedence, and both totals turn on — and no later item had the mandate
  to define it. The lens caught it as item1-F2 before drafting, not after.
- **The contract can misdescribe its own governance.** H-1 was one stale sentence saying the
  companion "cites and does not restate" the equality instruction, written for a design that
  changed under it — the only place a future editor is told what maintenance obligation the
  arrangement carries, and it said "none."
- **A sweep is what makes a universal claim checkable.** "No statement remains anywhere" is not
  auditable as an assertion; five named terms over named directories, with every hit dispositioned
  and the raw list kept, is. The auditor re-ran all five and reproduced the record term for term —
  which is also what made ratifying the one aggregated class an informed decision instead of a
  concession.

---

## [2026-08-13] - [CONSTRAINT-SEMANTICS Item 3] Coverage Report and TEAx Policy

**Type**: Item (orchestrated run; audited Certify-with-residuals → all six residuals cured)
**Duration**: spec 2026-08-12 → closed 2026-08-13
**Archived to**: `.project/completed/20260813_constraint-coverage-policy/`
**Commits**: codegen item tip `3d32ae4` (branch `item7-rebuild`, unpushed) / TEAx branch
`constraint-semantics-item3` tip `5b70ae9` in `/home/reid/1cfe/teax` (**unmerged**, four commits
off pinned `main` `fa0e06a`) / companion untouched at `5088b41`

### Summary
A generated package could report `all_satisfied` while most of the model's authored feasibility
checks were never assessed, and TEAx could label such a package `unconstrained` — the same
disposition a genuinely constraint-free model gets. The headline was a not-failed claim, not a
coverage claim: it read violation → indeterminate → `all_satisfied` (any non-empty result list) →
`not_assessed`, and never consulted exclusions. There was no state between "all good" and "nothing
assessed", and an excluded-only model emitted no report at all, because generation returned before
minting the aggregator when nothing was eligible. A design search therefore could not tell "this
candidate passed its physics gates" from "nobody checked."

This item makes the report say exactly how much applicable asserted feasibility was assessed, using
Item 2's canonical catalog as the one authority it derives from. The report now carries a coverage
account — authored total, assessed count, excluded and non-reaching counts, an unassessed-reason
histogram, and a coverage state — computed in one direction from the sealed catalog, with identity
enforced at construction on both the producer dataclass and the generated validator. The headline
vocabulary gains `partial_coverage` in both repos, `full_satisfaction` replaces `all_satisfied` and
is impossible unless `unassessed_gate_count == 0 and assessed_gate_count > 0`, and a constraint-
bearing model with nothing eligible now generates a zero-input aggregator instead of silence. A
zero-usage model stays report-free and byte-identical.

The load-bearing design resolution was to keep **coverage as a second axis rather than a slot in the
headline**. The headline stays a single precedence-ordered token; the account is always present and
always reaches the durable case record, so a `violation` report still says how much was checked. On
the TEAx side the two vocabularies are split (`ConstraintStatus` / `HeadlineResponse`), all three
former bare subscripts fail closed by name via `UnknownHeadlineToken`, `partial_coverage` defaults
to **keep-for-boundary**, and `feed-strategy` requires an explicit, fingerprint-bearing config line
whose key or value typo fails closed. `ships_constraint_report` became the single consumer
authority and the spec-derived default was **deleted** rather than re-synced — a second derivation
can only ever say "the two must agree."

### Deliverables
- `spec.md`, `spec-review.md`, `design.md` rev 2, `design-review.md`, `plan.md` (8 phases with
  completion notes and deviations), `verification.md` (+ dated cure addendum), `audit.md`,
  `product-lens.md` (spec / design / design_review / audit / close blocks), `briefs/`,
  `expected-coverage.md`, `red-window.txt`.
- Codegen: `coverage_account()`, the nested coverage block, five headline tokens, the zero-input
  aggregator with its channel asserted as a real exit point, four named fail-before-mutate refusals,
  `RUNTIME_CONTRACT_VERSION` `1.x`→`2.0.0`, `has_executable_content` deleted.
- TEAx: split vocabularies, `UnknownHeadlineToken` at all three seams, `partial_coverage` in both
  dispatch tables, coverage persisted into `assessment_json` and onto `CaseView`, evidence schema
  `v1`→`v2`, accepted schema sets re-vendored (**replaced, not extended**), all five committed
  fixture packages regenerated.
- `expected-coverage.md` — 13 expected accounts, hand-derived from `.sysml` source **before** the
  code existed, plus `test_coverage_ledger_agreement.py` which parses the ledger rather than
  transcribing it.
- Six states pinned twice, once in each vocabulary, each by a test no other state satisfies.
- Gates: codegen **2050 passed / 34 skipped / zero licence-skip**, TEAx **337 / 0**, ruff and mypy
  counters unchanged in both repos, `git diff --check` clean in both, **zero baseline byte churn**.

### Deviations, all judged ACCEPTABLE at audit
- **PD5 was a probe-and-stop, and the orchestrator ruled replace-and-regenerate.** The design parked
  the fixture-package question rather than guessing it; the probe measured the real blast radius,
  and the ruling regenerated all five committed TEAx fixture packages instead of hand-patching them.
- **`f1_arithmetic`'s pinned generation script was deleted, not repaired — its premise was false.**
  It called modules the cutover recovery removed, so it could not run at any current revision. The
  replacement is `models/toy_plant.sysml` driven through the ordinary public route,
  byte-reproducible, with unchanged case values. The audit endorsed the swap on the merits: it
  removes a bespoke exemption rather than creating one.
- **`sealed_package`'s model was regenerated from codegen's `wi014_toy`** (adopted, recorded in
  TEAx `GENERATION.md`).
- **The `Free_Plant → freePlant` entry-key drift is pre-existing** (`fa0e06a`→HEAD, ADR-001),
  surfaced by regeneration rather than caused by it — accepted and annotated at every site, not an
  Item 3 semantic change.
- **`excluded_only` moved `not_assessed` → `partial_coverage`, which LC-E12's owner-ratified
  amendment mandates.** An excluded asserted gate stays in the denominator, so a package with one is
  partially covered, not unassessed. This is a required correction, not a widening.

### Carried forward (not closed by this item)
- **The TEAx branch `constraint-semantics-item3` (`5b70ae9`) is complete but unmerged.** Keep the
  TEAx checkout on it until merge — codegen's execution lane imports simkit from that working tree.
  **Publication order: codegen first, TEAx second**; the reverse makes TEAx accept a runtime
  contract no generator produces. Item 2's re-vendor hand-off is **discharged on this branch**; what
  remains is merge sequencing, owned by `pre_pr` and the owner.
- **design-F2** — Appendix C's vacuous-gate cell over-permits in the degenerate case and wants "…and
  at least one gate remains". D4 published a ruling with its reasoning, so behaviour is settled;
  the contract text is not. Owner: Item 1.
- **D9 follow-on** — the authoring-time advisory for the eligible-plus-`@inapplicable:` combination
  belongs in companion authoring guidance. D9 already refuses the combination loudly at generation
  time. Owner: Item 1.
- **item3-F2 (surfaced, not resolved)** — the inherited "a `BLOCK`ed asserted usage stays in the
  denominator" clause is unreachable under invariant 1 as amended, since a `BLOCK` on an asserted
  usage halts the model and no report exists to carry it. Item 3 carried the clause as one row of a
  total map (a totality claim, not a reachability claim) and correctly did not write the unbuildable
  fixture. Item 1 must rule whether the clause is dead text or invariant 1 is narrower than written.
- **The epic's scope-4 wording correction was performed at close**, not deferred again: the trigger
  is the absence of an *applicable asserted gate*, not of executable assertions (LC-E10).

### Known issues (pre-existing, not caused by this item)
- **`test_the_lane_runs_the_real_simkit` fails on a whole-set run and passes in isolation** — a
  collection-order artifact, reproduced at the parent commit. Item 3 touched neither
  `tests/runtime/` nor the guard, and `tests/execution` alone is green. Recorded here and in
  `CURRENT_WORK.md` so it is not rediscovered as a regression. **Still needs an owner.**
- The two stale-baseline classes `deep_cross_scope` and `plant_values` remain untouched and
  unowned.

### Lessons Learned
- **An unearned checkbox is worse than an unchecked one, because it stops the next reader looking.**
  Two `[x]`s in this item claimed evidence they did not have: one cited a pre-existing test that
  varied `strategy_config` where invariant 50 needed `evidence_schema_version` — the exact
  substitution the design had warned would "pass today and silently stop proving anything" — and one
  ticked a validation step that had not run. Neither was caught by a failing test. Both were caught
  by someone reading the claim against the artifact it cited. The cure corrected both in place and
  wrote down what they had previously claimed.
- **All six audit residuals were the same shape: a mechanism built correctly that no test pinned.**
  The auditor verified each by direct probe, so nothing was broken — but a probe is not a regression
  test, and any of the six could have been removed by a refactor and gone green. Building it right
  and pinning it are two separate pieces of work, and the second is the one that survives you.
- **A stopped probe beat a guess.** PD5's design parked the fixture-package question instead of
  assuming an answer, and the measurement it produced is what made replace-and-regenerate an
  obviously right call rather than a defensible one.
- **A pinned script whose premise has expired is not an asset.** `f1_arithmetic`'s generator had
  been unable to run since the cutover deleted the modules it called. Deleting it for an authored
  model on the public route removed a bespoke exemption; keeping it would have preserved the *look*
  of reproducibility with none of the substance.
- **The gap noted at Item 2's close is unchanged:** no `.project/adr/` or `.project/product/` ledger
  and no `adr.sh`/`product.sh` in this repo. The audit's own lens pass flagged that the
  coverage-truth promise has no product-promise home (audit-F4). No ids were hand-minted, and no
  entry was invented — the promise needs an owner-originated statement, and manufacturing one at
  close would be the provenance failure the ledger exists to prevent. Item 3's decisions live in its
  archived `design.md` (D1–D9) and in ADR-009.

---

## [2026-08-13] - [CONSTRAINT-SEMANTICS Item 2] Canonical Usage Domain and Catalog Totality

**Type**: Item (orchestrated run; audited Needs-work → cured → re-audited Certify-with-residuals)
**Duration**: spec 2026-08-12 → closed 2026-08-13
**Archived to**: `.project/completed/20260813_constraint-catalog-totality/`
**Commits**: codegen item tip `35ee82f` (branch `item7-rebuild`, unpushed) / companion
`bc69f04` in `/home/reid/1cfe/agentic-mbse-item7-rebuild`

### Summary
The lifecycle contract promised that every authored constraint usage stays visible with exactly one
disposition, and the exact route did not keep it. Constraint records only began *after*
owner-to-scope expansion, so on `catf_mfe_d5` — the richest model in the corpus — 65 authored
constraint usages produced 9 carriers and the other 56 were not excluded, not deferred, but
**absent**: nothing recorded that they had ever been written. Worse, a totality gate written against
that data would have been circular, comparing two projections of an already-truncated set, and the
two requirement rows meant to catch this read PASS because each specimen fixture happened to have a
carrier.

This item makes the domain total and proves it with evidence that does not descend from the domain.
The instance graph now mints one `ConstraintUsageRecord` per authored usage **before** occurrence
expansion, each carrying exactly one disposition (eligible / excluded-with-reason /
non-reaching-with-reason) plus its severity, occurrence count, and inapplicability state, joined to
the per-occurrence tier by declaration identity. Severity follows cause, not convenience. A
generation-time completeness gate fails on a removed, duplicated, or misjoined disposition and names
the offending usage. The domain travels through a bumped `instance-graph/v3` codec that fails closed
on v2 and on stripped-tier shapes, with live, in-place-snapshot, and relocated-snapshot routes
verified field for field.

The result on the fixture: **65 members, 9 reaching, 0 eligible** — a measured correction to the
item's inherited "9 eligible" premise (all 65 usages are bare `constraint`, so the 9 that expand
grade `excluded`/`unassessed_form`). And the strongest evidence that this was the right piece of
work is what it deleted: `collect_constraint_manifest`, its two classifiers,
`extraction/constraint_report.py`, and all seven test call sites are **gone** from `src/` and
`tests/` rather than demoted to a second inventory kept in sync. The replacement oracle reads
`.sysml` source through a licence-free scanner that shares no code, no adapter, and no parse with
the elaborator.

### Deliverables
- `spec.md`, `spec-review.md` (11 findings resolved), `design.md` rev 3, `design-review.md`,
  `plan.md` (8 phases with completion notes and deviations), `verification.md` (+ dated cure
  addendum), `audit.md` (original record + re-audit with per-finding cure verdicts),
  `product-lens.md` (spec / design / audit / close blocks), `briefs/`, `probes/`,
  `v2-refusal-list.txt`.
- Canonical authored-usage domain, disposition minting, `@inapplicable:` mechanism, completeness
  preflight (the fifth), `instance-graph/v3` codec, and named diagnostics.
- Independent totality oracle: 42 reviewed expected-population files + licence-free source scanner
  (`tests/conformance/test_constraint_population_oracle.py`).
- Schema pins: `instance-graph/v2`→`v3`, `CATALOG_SCHEMA_VERSION` `2.0.0`→`3.0.0`, companion
  `constraint-facts/v2`→`v3` (new `vacuous_asserted_gate` ADVISORY kind, agentic-mbse `bc69f04`).
  All 21 snapshot-bearing fixtures recaptured **once** at the final schema.
- REQ-EXT-09 and REQ-CL-04 re-graded and re-anchored to the oracle; REQ-EXT-09's domain-vs-carrier
  self-contradiction resolved; reference doc 28 banner-retired; CLAUDE.md preflight count corrected.
- Gates: codegen **1860 passed / 34 skipped / 65 deselected / 0 failed**, zero licence-skip lines;
  `ruff check src` 12, `mypy src` 55 (both at/below baseline); `git diff --check` clean.

### Carried forward (not closed by this item)
- **TEAx must re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` with `3.0.0`.** B3 forbids TEAx importing
  sysml-codegen, so nothing here can enforce it. While pending, TEAx fails closed on every newly
  generated package — loudly, which is the intended direction. Do not bump TEAx first.
- **Residual R1** — the internal bare-`ComputationGraph` seam is seal-only; a *resealed* removal of a
  non-reaching row passes silently there. No production caller reaches it; both public routes hold.
- **Residual R3** — the calc-def-only package shape has no pre-item baseline, so the A4 cure's
  "this is alignment, not new behaviour" justification is asserted rather than demonstrated. Pinned
  only by two generation-level tests. Natural home: Item 5.
- **The [AGENT] severity exception the owner has not ruled on** — a malformed `@inapplicable:`
  directive halts at `error` grade **whatever the usage's form**, overriding an `[INHERITED]` line
  that says plain forms are never errors. Recorded beside that line in the spec, surfaced in the
  epic's Item 2 section and the lens close block.
- Both R1/R3 and the exception are recorded in
  `.project/backlog/epic_constraint_semantics_contract.md` §Item 2.

### Lessons Learned
- **A totality proof must not descend from the thing it checks.** The tempting build here was a
  second constraint inventory compared against the graph; it would have produced a green gate that
  could never detect the failure that mattered. Deleting the sweep and reading `.sysml` source
  through an independent scanner is what made the evidence worth anything.
- **Absence is worse than a bad answer, because it is invisible.** Two requirement rows read PASS
  for as long as this defect existed, purely because every specimen fixture happened to have a
  carrier. Selection bias in the fixture set is a failure mode a green matrix cannot show you.
- **Two deviations were accepted at audit, both because they were surfaced rather than smoothed
  over**: the 42 expectation files were scanner-generated then reviewed (independence *from the
  domain* is the load-bearing property, and a full 42-fixture cross-check before any file was
  written found and fixed two scanner bugs); and Phase 5's codec work was pulled into the Phase 3
  window when the plan's own recorded contingency fired, with the intermediate gate redefined as a
  committed, enumerated 61-node frozen refusal list that the Phase 8 recapture discharged to zero.
- **The product-lens ledger was not run at plan or implement stage** (audit A7 / residual R5). The
  point was still checked — later, once, by the audit, with probes — but the audit-stage pass fired
  the ledger's own falsifier and two structural smells that an earlier pass could plausibly have
  caught before they reached an auditor. Dispositioned at close as a recorded gap; retroactive
  stage entries were deliberately **not** written, because a judgment made with the outcome in hand
  is not stage-time evidence.
- **Tooling gap noted at close:** this repo has no `.project/adr/` or `.project/product/` ledger and
  no `adr.sh`/`product.sh` (decision records live as ADR sections in
  `docs/architecture/modeling-assumptions.md`). No ids were hand-minted. Item 2's cross-cutting
  decisions are recorded in its archived `design.md` (D1–D10, invariants 1–9) and in the
  requirement rows it re-anchored.

---

## [2026-08-10] - [SOURCE-IDENTITY] Epic + Item 4 archived as SUPERSEDED

**Type**: Supersession archive (not a completion)
**Duration**: epic 2026-08-03 → superseded 2026-08-07 → archived 2026-08-10

### Summary
Archived the SOURCE-IDENTITY epic (`20260810_epic_semantic_source_identity.md`) and its Item 4
(`20260810_source-identity-occurrence-foundation/`) with superseded markers. The Item-4
shadow-layer architecture — a production identity manifest running beside the legacy string
resolver that ignored it by design — was stopped after Phases 1–2 (audit: Needs Work; product
lens BLOCKED on C24). The recovery assessment led the owner to ratify the elaborate-first
replacement on 2026-08-07: the major pivot the ELABORATE-FIRST epic executes, with the string-
compensation machinery deleted at cutover rather than wrapped. Items 1–3 (binding-semantics
spike, route-evidence spike, ratified source-identity contract with the 29-cell matrix) remain
complete and inherited unchanged as the semantic authority; Items 6–8 intent is absorbed into
ELABORATE-FIRST Items 7–8. The stopped Phase-1–2 implementation is preserved forensically on
`item4-phases12-forensic` (codegen `69eef3b`, agentic-mbse `9724f1d`); the salvage subset
landed via ELABORATE-FIRST Item 2.

### Deliverables
- `20260810_epic_semantic_source_identity.md` — epic with supersession record and final status.
- `20260810_source-identity-occurrence-foundation/` — Item-4 spec, design, plan (do-not-resume
  banner), audit (Needs Work), spec/design reviews, product-lens ledger; superseded markers on
  spec/design/plan.
- No code shipped from this item; salvaged evidence types/queries/fixtures are recorded in the
  ELABORATE-FIRST Item 2 entry (codegen `66a61f3`, agentic-mbse `65a35d7`).

### Lessons Learned
Recorded in the recovery assessment
(`.project/research/20260807-143615_source-identity-recovery-assessment.md`): the epic/spec/
design chain explicitly required a parallel identity subsystem the runtime would ignore until a
later item — artifact-to-artifact gates passed while no observable behavior changed. The
ELABORATE-FIRST epic rules (product-behavior gates, one-authority gate, fail-fast spikes) are
the direct answer.

---

## [2026-08-10] - [ELABORATE-FIRST Item 6] Exact-Identity Completion — Payload, Occurrence, Projection

**Type**: Item (three audit rounds: phases-1/2 Needs Work, phases-3/4 Needs Work, full-item v3
Needs Work → certified 2026-08-10 after targeted re-audit of F7–F9)
**Duration**: spec 2026-08-09 → certified 2026-08-10

### Summary
Closed the remaining exact-identity gaps on the internal elaborate-then-project route before the
Item-7 authority switch. Calculation definitions, formals, outputs, compilation results, port
metadata, and constraint profile decisions now attach by exact SysIDE declaration UUID — display
renames, normalized-name collisions, duplicate QNs, and enumeration reorders cannot move
executable payload, and missing/duplicate/mismatched identity blocks with named `SI_*`
diagnostics instead of defaulting to `UNKNOWN`/`float`/null-metadata/`ADMIT`. SysIDE's native
`Usage.usages` view became the sole effective-child-declaration authority (codegen keeps only
finite concrete expansion; audit-F31 closed with a scoped valid-model witness). The validated
graph gained structured occurrence records, typed `ExpressionIR`, declaration-bound formal
provenance, and closed eligibility/compilability inside a fingerprinted internal
`instance-graph/v2`; projection became one-way (ownership/aliases from occurrence records,
execution order from `ProducerRef` edges, entry classification from `ValueSite`) with semantic
collision guards on every public spelling. Nine audit findings across three rounds were
remediated and independently verified — headline fixes: the public constraint source key is
rendered from model metadata, not a parser UUID (F1); formal provenance flows through typed ports
instead of a rendered-name join with a fabricated fallback (F5); profile `BLOCK` halts with the
new `SI_CONSTRAINT_BLOCKED` D10 diagnostic on strict, lenient, and snapshot round-trip routes
where it previously generated an executable module (F7); and the F30 boundary guard is
deny-by-default over every function in all six boundary files with five named, mechanically
exercised exemptions (F9). Every runtime-source matrix cell proves off-default mutation reaching
every and only its bound consumers at the generated public boundary. The shipped legacy route,
snapshot v5 bytes, neutral constraint-fact schema, and generated baselines stayed frozen
throughout; Item 7's deletion ledger now names the four Item-6 transitional dual mechanisms.

### Deliverables
- `20260810_elaborator-identity-completion/`: spec, design authority map, five-phase plan with
  red-first evidence and three remediation records, audit rounds (`audit.md`, `audit_v2.md`,
  `audit_v3.md` — certification in the v3 re-audit addendum), product-lens ledger (spec-F1 +
  audit-F1..F9, full resolution-by-citation history, final gate CLEAR).
- Code: exact-ID sidecars and maps in `extraction/{data_models,extractor,expression_compiler}.py`
  (`compile_calc_def_exact`); UUID-keyed payload/constraint attachment, `SI_CONSTRAINT_BLOCKED`
  enforcement, and native-child occurrence authority in `elaboration/{elaborate,occurrence}.py`;
  occurrence records, typed IR, formal provenance, and closed state in `elaboration/graph.py` +
  `snapshot/instance_graph.py` (internal v2 codec); one-way projection in
  `elaboration/project.py`; deny-by-default guard in `tests/unit/test_elaboration_import_boundaries.py`;
  new fixtures `elab_payload_identity`, `elab_constraint_formal_identity`,
  `elab_native_plural_scope`; coordinated agentic-mbse identified constraint
  extraction/evaluator (`extract_identified_constraint_facts`, `evaluate_identified_profile`) on
  `elaborate-first-salvage`.
- Gates at certification: codegen 3,358 passed / 47 skipped / 18 deselected (zero license-skip
  lines); agentic 1,819 / 1 / 33; corpus 37/37 matching the archived Item-5 ledger; frozen
  artifact hash unchanged (`25e45ad6…`).

### Lessons Learned
[TODO: Add lessons learned]

---

## [2026-08-09] - [ELABORATE-FIRST Item 5] Exact-Identity Elaborator Breadth

**Type**: Item (five audit rounds: phases-1/2 partial certify, rendered-path Needs Work, v1/v2
Needs Work, v3 certified after two remediation waves)
**Duration**: plan 2026-08-08 → certified 2026-08-09 (exact-ID rewrite; supersedes the 2026-08-07
rendered-path implementation)

### Summary
Built and proved the complete exact-identity elaboration front end (ELABORATE-FIRST Item 5) while
the legacy string-resolution route stayed shipped and byte-frozen. SysIDE declaration UUIDs are
wrapped once into typed declaration/slot/occurrence/node identities; a finite occurrence walker,
one contextual resolver, and fail-closed diagnostics feed a typed instance graph that projects
mechanically onto the existing `ComputationGraph` seam and round-trips through canonical
`instance-graph/v1` JSON. Evidence: all 29 inherited contract cells execute at generated-public or
named-diagnostic tier with off-default mutations on live and relocated routes; the 37-fixture
dual-run ledger is machine-verified against a live corpus run (26 expected-collapse / 11
expected-fix, zero unresolved). Audit rounds successively removed rendered-path edge selection
(spec R9), fail-open qualifier fallback, source-text-as-evidence, and — the v3 finding — silent
admission of an invalid same-name inherited/owned part re-declaration, which now blocks
`SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before occurrence expansion via SysIDE's own validation
diagnostic (loader diagnostics are now a required elaborate() input). The deep-cross-scope witness
fixture was repaired to valid explicit `:>>` form and its deep producer-output reference resolves
to its one exact producer channel.

### Deliverables
- `20260809_elaborator-breadth/`: plan (5 phases + two remediation decision records, all
  owner-ratified `[AGENT]`), `diff-ledger.md` (37 rows), `product-lens.md` (findings F1–F31 with
  full resolution-by-citation history), audit rounds (`audit-20260808-phases12.md`,
  `audit-20260808-rendered-path.md`, `audit.md`, `audit_v2.md`, `audit_v3.md` — certification in
  the v3 addendum).
- Code: `src/sysml_codegen/elaboration/` (identity, occurrence, elaborate, graph, project,
  diagnostics, diff, display), `snapshot/instance_graph.py`, `orchestration/elaborated_pipeline.py`
  (internal, no shipped flag), shared `extraction/{source_evidence,binding_evidence}.py`,
  `scripts/run_elaboration_corpus.py`; coordinated agentic-mbse exact-UUID adapter surface.
- Tests: 154 exact-elaboration tests (identity foundation, occurrence, fail-closed, collisions,
  contract matrix, projection, round-trip, public mutation, corpus ledger, model validation,
  import/AST boundaries) plus new fixtures incl. `elab_matrix_c2..c23`,
  `elab_namespace_distinguishability_probe`, repaired `deep_cross_scope_probe`.
- Contract: referent-table "Deep-cross-scope evidence boundary" amendment (corrected premise,
  owner-ratified) in the authoritative lifecycle contract.
- Carried forward: audit-F30 (guard scope) and audit-F31 (plural-fallback fixture) open
  non-blocking; F19 customer-scale proof and F26 legacy-oracle replacement are Item-6
  obligations.

### Lessons Learned
- A ruling is only as good as its premise: the F21 "parser limitation" classification survived
  one audit round because nobody counted the modeled occurrences behind the ambiguity. Reproduce
  the subject of a ruling, not just its record.
- SysML has no name-based implicit redefinition; a same-named nested re-declaration is an invalid
  model. Prefer promoting the parser's own validation diagnostic over reimplementing spec checks,
  and make the diagnostics feed a required argument so no caller can skip it.
- Kept falsifier-shaped assertions (`[x] = list-comp` destructuring on the expected-unique node)
  turn a duplication bug into a loud test failure instead of a green suite.

---

## [2026-07-24] - [DOCS-LIFECYCLE-SYNC] Post-Epic Documentation Reconciliation

**Type**: Item (orchestrated: Opus implement stages + two independent audits; briefs committed)
**Duration**: spec 2026-07-20 (re-verified 07-24); implemented + audited in one orchestrated run 2026-07-24

### Summary
Reconciled `docs/architecture/` and `EXPLAINER_PROMPT.md` with merged main `936315c` after the
CONSTRAINT-LIFECYCLE epic. Five phases against a four-sweep claim register: replaced
`04-input-resolver.md` (documented a deleted module) with `04-producer-resolution.md`,
rewrote doc 24 to the unified-ladder narrative, wrote `30-diagnostic-severity.md` (severity
contract had zero public coverage; documents three stacked fail-closed guards), added matrix
rows REQ-SNAP-21/22 (274→276, index reconciled; pre-existing DM/RES drift fixed), swept the
retired module_kind bool flags, added the nested-override honesty note, re-anchored the
explainer prompt (19 registered re-anchors). Final audit Pass with notes; the one note
(agentic-mbse citations unreachable from the audit sandbox) closed by orchestrator
verification at `f4ebdce` — no open findings.

### Deliverables
- `20260724_docs-lifecycle-sync/`: spec (R1–R7), 5-phase plan, `inventory.md` (the full
  per-claim register incl. E1–E19 and matrix-row candidates MG1–MG3), `audit-midrun.md`,
  `audit.md` (+ N1-closure addendum), stage briefs.
- Follow-on ticketed: `[MATRIX-EPIC-SURFACE-ROWS]` (P3) for the three surfaces registered
  but not added to the matrix.
- NOTE at close: delivered on branch `docs-lifecycle-sync`; owner merge pending.

### Lessons Learned
- Re-verify a spec written from a close-handoff against the merged diff before implementing:
  the original spec missed the epic's largest doc casualty (the resolver unification, six
  stale files) because the handoff's deferred-docs list predated a late refactor.
- Stage briefs that seed verified facts but demand re-verification pay off: the stages
  corrected two orchestrator-supplied citations and surfaced a third fail-closed guard no
  design doc named.

---

## [2026-07-24] - [NESTED-OVERRIDE-TRIPWIRE] Unmatched-Override Warning (interim guard)

**Type**: Item (probe-first; single Opus implement stage; gates re-verified by orchestrator)
**Duration**: same-day (2026-07-24)

### Summary
Made the `[NESTED-OCCURRENCE-OVERRIDE]` calc-path value loss loud: the supplied-value
materializer now warns when a dotted demand falls through silently while the capture carries
an override for that attribute of that part usage, naming captured vs demanded scopes. The
naive predicate false-fired 4× on the clean corpus (reference-form aggregation rollups); two
narrowings (dotted-form gate + part-usage gate) reached 0 fires across all 19 snapshot
fixtures before any production code was written. No resolution outcome or output byte changes;
suite 3118/47 licensed, ruff clean. The occurrence→definition-bridge fix remains filed in
`[NESTED-OCCURRENCE-OVERRIDE]` with an explicit filed-fix scope block.

### Deliverables
- `src/sysml_codegen/resolution/supplied_values.py`: `_BindingTarget.form` (diagnostics-only),
  `_unmatched_override_scopes`, collect-then-drain warning.
- `tests/unit/test_supplied_values.py`: RED-verified positive on the recorded coordinate +
  two pinned silent-on-clean negatives.
- `20260724_nested-override-tripwire/`: brief, probe (`unmatched_override_scan.py`),
  corpus verdict, evidence. No independent audit (orchestrator-verified gates; probe verdict
  committed as the acceptance record).
- NOTE at close: delivered on branch `nested-override-tripwire` (stacked on
  docs-lifecycle-sync); owner merge pending.

### Lessons Learned
- The corpus false-fire scan earned its gate status: the obvious predicate was wrong in a way
  only the corpus could show (site-4 precedent repeated exactly).

---

## [2026-07-20] - [CONSTRAINT-LIFECYCLE] Constraint Execution Lifecycle Remediation

**Type**: Epic (includes the superseded CONSTRAINT-WAVE-REMEDIATION epic doc, archived alongside as frozen history)
**Duration**: ~1.5 days wall-clock (created 2026-07-19; merged + archived 2026-07-20; orchestrated multi-session run + owner merge)

### Summary
The open constraint PR wave carried semantic, graph, package, evaluator, and study-seam defects
that item-level certification alone could not close. This epic implemented the owner-ratified
lifecycle contract across agentic-mbse, sysml-codegen, TEAx, IFE, and the stellarator consumer:
occurrence/demand integrity, shared producer resolution (Gate A), Gate B vacuity deletion,
diagnostic severity (constraint-facts/v2), whole-tree snapshot portability (v5), trusted package
bootstrap/seal provenance, canonical embedded catalog (schema 2.0.0), multi-entry candidate
bridge, producer completeness, TEAx evidence durability, and legacy identity closure — then
proved one sealed artifact thread end-to-end with a 41/41 composed public proof at a
commit-pinned set (16 negative mutations at boundary, 6/6 byte checks). Merged 2026-07-20 in
the test-enforced order agentic-mbse #11 → sysml-codegen #9 → teax #3; post-merge smoke on
codegen main 3115 passed / 47 skipped with zero license-skip lines.

### Deliverables
- 14 items (0–13) plus the ratified lifecycle-contract spec; item folders archived here as
  `20260720_constraint-lifecycle-*` and `20260720_constraint-execution-lifecycle-contract/`
  (specs, designs, design reviews, plans, evidence, independent audits, briefs).
- Composed-proof records: `20260720_constraint-lifecycle-composed-proof/release-readiness.md`
  (pinned set, mutations, byte checks, remaining-state ledger) and
  `evidence-coordinate-register.md` (the 41/41 register).
- Ratified authority remains at
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`.
- Merged mains: agentic-mbse `f4ebdce`, sysml-codegen `936315c`, teax `fa0e06a`. fusion-tea
  (`be1ee7c0`) and stellarator (`342cc799`) evidence branches stay local pending owner delivery.
- Follow-ons filed, not silently dropped: `[NESTED-OCCURRENCE-OVERRIDE]` (BACKLOG P2, probe
  fixture in-tree), Item-10 completeness-check MODULE_OUTPUT exemption (owner ruling pending),
  stale-baseline class (four members, pre-existing), deferred documentation debt (severity
  system, portability matrix row, docs/architecture sweep).

### Lessons Learned
- The composed proof caught what component certification could not: every item certified in
  isolation, yet the composed run surfaced the case-40 IFE harness drift and the case-18
  fixture over-build. Consumer acceptance scripts rot unless something smoke-runs them.
- Byte-identity discipline held — the pinned codegen reproduced the sealed thread
  byte-for-byte, so "run at HEAD" was provably "run at the pin."
- Strict resolution stayed strict: the case-18 halt was INV-2 fail-loud behavior; the fix was
  a fixture correction, not a loosening. Check "author if absent" fixtures against the row
  verbatim before concluding a product defect.
- A general occurrence-materialization gap hid behind a constraint symptom
  (`[NESTED-OCCURRENCE-OVERRIDE]` — def-relative capture vs occurrence-relative demand).
- Merge-order enforcement by a test (`test_upstream_pins`), not a note, survived a long
  multi-session epic; mechanical enforcement beats documentation.

---

## [2026-07-13] - [CONSTRAINT-EXEC] Constraint Execution and Design-Space Studies

**Type**: Epic
**Duration**: ~1 day wall-clock (created 2026-07-12; archived 2026-07-13; one ~14h orchestrated run + owner close session)

### Summary
Modeled physical limits (`assert constraint`) previously died at a drop-report warning, and every
design study re-implemented the judgment by hand. This epic makes modeled assertions execute inside
the generated forward model — Kleene-compiled graph modules feeding an exact-schema report
aggregator, verdicts as data beside ordinary outputs — and adds sealed package contracts plus a
crash-safe study layer (evaluator → store/runner → policy/query/CLI) in teax. Snapshots carry
constraint facts load-bearing (v3); `ExpressionAST` retired onto the shared `ExpressionIR`; the IFE
sweep's hand-coded viability rule is deleted, replaced by the generated assertion (2294/2301 exact,
7 model-favoring boundary rows, [OWNER] ratified).

### Deliverables
- 15 items (0–14) across four repos, each with spec/design/plan/audit + briefs; 8 item folders
  archived here, 3 in agentic-mbse, 4 in teax; fusion-tea acceptance evidence in
  `exploration/ife_e2e/study/` there.
- Independent findings audit: `20260713_epic_constraint_execution_audit_independent.md` (every
  sampled claim reproduced exactly: both mutation probes verbatim, all final gates, boundary rows
  at data level, CE-F1..F3 at source).
- Follow-ons: CE-F1 (standalone catalog emission) and CE-F2 (multi-channel CandidateBridge) in
  BACKLOG; CE-F3 fixed post-run (teax `0d606a4`).
- Gates at close: sysml-codegen 2330/23, mypy 76 baseline, ruff clean; agentic-mbse 1401/1; teax
  fully green 262.

### Lessons Learned
- Item-level certification covers what the item's fixtures exercise: the first real
  multi-entry-channel package through the certified path surfaced three integration gaps the
  single-channel toy fixture could not. An epic-level integration acceptance (real package, all
  layers) belongs in the plan, not just at the end.
- Audits that cannot execute should write "requested live probes" for the orchestrator; the
  probe-addendum + independent re-execution pattern held (both re-run probes reproduced verbatim).

---

## [2026-07-10] - [PUSH-DOWN] agentic-mbse Push-Down

**Type**: Epic (doc archived 2026-07-20 with audit, independent audit, and pre-PR reports)
**Duration**: ~2 days (created 2026-07-08; certified 2026-07-10 after independent-audit remediation)

### Summary
Reusable SysML helpers moved from sysml-codegen into agentic-mbse under a "moves, not behavior
changes" contract: expression reconstruction, the qualified-name utility split, hierarchy
primitives/data models, and aggregation decomposition with compatibility gates. Design
overrides, usage-type indexing, Python rewriting, aliases, scoping, and module construction
stayed in sysml-codegen. Merged as sysml-codegen PR #8 + agentic-mbse PR #10.

### Deliverables
- 4 items, each with spec/design/plan/audit, archived as `20260720_{expression-reconstruction-push-down,qualified-name-utility-split,hierarchy-primitives-models,aggregation-decomposition}/`.
- Independent audit (`20260720_epic_push_down_audit_independent.md`): original verdict Needs
  Work (over-claimed SC-D hazards, undocumented behavior changes in Item 1's move); remediated
  same day; final Certify.

### Lessons Learned
- A "moves only" epic needs its certification record held to the same bar as the code: the
  independent audit caught certified-as-resolved claims the epic audit missed.

---

## [2026-07-08] - [TRUTH-DEBT] Truth-Debt Retirement

**Type**: Epic
**Duration**: ~2 days (created 2026-07-06; archived 2026-07-08)

### Summary
Retired the PIPELINE-TRUTH follow-on ledger in one pass. The live aggregation path now runs
through `resolve_input(AGG_STRATEGIES)`, 3+-segment calc-usage chains resolve instead of
hard-rejecting, matrix test gaps are pinned, inherited-attr classification is fixed, and the
remaining sweep and hygiene debt is either closed or filed with named residue.

### Deliverables
- Archived item artifacts: `spec.md`, `design.md` where present, `plan.md`, `audit.md`, and
  supporting probes/impact notes for six TRUTH-DEBT items.
- Item 1: F4 aggregation-resolution cutover, Strategy D deletion, and `param_groups` typing cleanup.
- Item 2: resolved multi-hop CHAIN bindings with loud fallback diagnostics and live/offline parity.
- Item 3: REQ-DM-08, REQ-RES-05, and REQ-RES-08 test pins and matrix flips.
- Item 4: inherited-attribute classifier fix, snapshot recapture, and xfail retirement.
- Item 5: matrix sweep residue pass, EC-04/AS-06 mutation-proven strengthens, reframes, citations,
  and named overflow filing.
- Item 6: D3 hygiene-tail hardening for loader, aggregation compile, and registry warnings, plus
  site-4 reclassification.
- Pre-PR gates: 2120 passed / 4 skipped / 0 xfailed; ruff src clean; mypy src 97.

### Lessons Learned
- [TODO: Add lessons learned]

---

## [2026-07-06] - [PIPELINE-TRUTH] The Generated Package Is the Truth

**Type**: Epic (doc archived 2026-07-20)
**Duration**: ~2 days (orchestrated)

### Summary
Made the generated package the ground truth for fusion-tea: end-to-end generation/wiring/execution
at true zero V11 offenders, run-C LCOE reproduced bit-exact ($270.1211779380445), and every
downstream workaround deleted upstream. Also: constraint drop report made subtype-aware
(catches `assert constraint`), 13 silent-failure findings fixed by family, 25 self-referential
tests re-anchored, verification matrix reconciled to 253 rows (249 PASS + 4 UNTESTED-argued),
dead code cleared, agentic-mbse guidance taught + checked, docs and explainer refreshed.

### Deliverables
- 10 items, all landed and audited PASS. Epic doc: `20260720_epic_pipeline_truth.md` (Lessons
  Learned inside). Follow-on filings retained in BACKLOG.md (F4 cutover, matrix gaps, classifier
  fix — all later retired by TRUTH-DEBT; plus the still-filed P3 tail).

### Lessons Learned
- See the epic doc's Lessons Learned section (archived with full detail).

---

## [2026-07-06] - [UPSTREAM-FINDINGS] Upstream Findings Remediation & Plant-Idiom Support

**Type**: Epic (doc archived 2026-07-20)
**Duration**: ~2 days (orchestrated); merged as PR #3

### Summary
Fixed the SC-1–SC-11 findings and six research defects surfaced by fusion-tea's real plant
model, added staged cross-part wiring and the snapshot CLI, and synced agentic-mbse. Residue
(10 V11 offenders, assert-constraint silence, F2/F4) was shaped into — and later closed by —
PIPELINE-TRUTH.

### Deliverables
- 12 items, all landed and audited PASS. Epic doc: `20260720_epic_upstream_findings.md`.

### Lessons Learned
- See the epic doc (archived).

---

## [2026-02-22] - [OUTPUT-REGISTRY] Output Registry & Backtracker Redesign

**Type**: Epic (doc archived 2026-07-20)
**Duration**: ~9 days (created 2026-02-13)

### Summary
Replaced the single-dict output registry with typed registries and cut the backtracker over to
typed dispatch: ~715 lines of legacy resolution removed, 39 tests migrated, E2E YAML diffs
clean on all 4 models, 641 tests passing at close.

### Deliverables
- 4 items. Epic doc: `20260720_epic_output_registry_backtracker_redesign.md`.

### Lessons Learned
- See the epic doc (archived).

---

## [2026-02-10] - [COST-PATTERN] Item 4: Pipeline Integration -- Hierarchy-Aware Module Generation

**Type**: Epic Item (COST-PATTERN Item 4)
**Duration**: ~1 day

### Summary
Integrated hierarchy-aware extraction (Items 2-3) into the full codegen pipeline. Virtual CalcUsage binding rewriting resolves `:>>` redefinitions (LITERAL, CHAIN, design deep-path) before the backtracker runs. Aggregation modules generate from `AggregationExpressionData` with symbolic channel resolution, multiplicity entry points, and `# source: aggregation` YAML comments. Extended CLI generation layer with aggregation module wrappers, auto-implementations, registry entries, and backlog reporting.

### Deliverables
- Pipeline Step 3.5: `_extract_hierarchy_and_rewrite_bindings()` in initialization.py
- Pipeline Step 4.7: Aggregation expression storage on `PipelineContext`
- Graph builder: `_build_aggregation_module()`, `_extend_output_catalog_with_aggregation()`, symbolic channel resolution
- Backtracker: `_resolve_from_aggregation_output()` strategy (Strategy 7)
- CLI: `_generate_aggregation_modules()`, `_generate_aggregation_stencils()`, registry and backlog extensions
- Generation: `_module_to_context()` aggregation comment, `generate_registry_function()` and `generate_backlog_report()` aggregation params
- 454 tests, 0 failures (141 new tests across 4 phases)

### Lessons Learned
- Computed attribute pattern provided clean template for aggregation CLI generation
- `ScopedAggregationData` with `module_eqn` property cleanly handled ADR-003 naming
- Deriving input names from `PipelineModule` (vs regex-parsing expressions) was the cleaner approach

---

## [2026-02-09] - [ATTR-EXPR] Attribute Expression Capture

**Type**: Epic
**Duration**: ~2 days (estimated: ~6.5-8.5 days)

### Summary
Enabled SysML modelers to express computations as attribute-level expressions (`attribute volume = pi * r^2 * h`) instead of requiring full CalcDef+CalcUsage ceremony. Codegen detects computed attributes on PartDefs, classifies them via a 5-way scheme (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE), generates synthetic pipeline modules for FORMULA patterns, and auto-implements them using the Phase 1 expression compiler.

### Deliverables
- `ComputedAttributeData` model and 5-way `ComputedAttributeClassification` enum
- `extract_computed_attributes()` extraction module (Step 4.5 in pipeline)
- Graph builder extension for FORMULA synthetic module generation
- Backtracker computed attribute awareness (FORMULA -> MODULE_OUTPUT resolution)
- 21 E2E tests validating probe fixture (9 ground-truth values) and solar_battery `p_net_kw`
- ADR-004: Computed Attribute Pipeline Integration
- ADR-005: Computed Attribute Classification
- ADR-001 clarification (computed attribute entry points)
- ADR-002 amendment (FORMULA pattern exemption, modeling guidance)
- Full test suite: 285 tests, 0 failures, 0 xfail

### Lessons Learned
- Spike de-risked the entire epic with purpose-built probe fixture
- Phase 1 expression compiler reused with zero changes
- Option C (direct graph integration) cleaner than original Option A recommendation
- Chain handling was a non-issue (biggest simplification)
- ADR migration from monorepo should have been done during repo split

---

## [2026-02-08] - [EXPR-CODEGEN] Expression-Aware Code Generation

**Type**: Epic
**Duration**: ~8.5 days

### Summary
Built expression compiler that auto-implements CalcDef output expressions as Python code. 15/15 solar_battery CalcDefs, 19/21 CATF CalcDefs auto-implemented. Eliminated the `_impl.py` handwriting bottleneck.

### Deliverables
- Expression compiler (`expression_compiler.py`)
- Auto-implementation template (`auto_implementation.py.jinja2`)
- Step 6.5 pipeline integration
- 167 tests, 0 xfail

### Lessons Learned
- CalcDef-agnostic compiler design enabled reuse in Phase 2 (ATTR-EXPR) with zero changes

---
