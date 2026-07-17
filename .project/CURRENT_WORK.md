# Current Work

**Last Updated**: 2026-07-17

---

## Active Work

### CONSTRAINT-EXEC code-quality remediation — AUDITED: NEEDS WORK (2026-07-17)

An independent audit at `c2967f0` verified the four focused remediation commits but did not
certify the work. Two P1 contract defects remain: constraint lowering ignores
`ActualFact.formal_targets` and does not reject uncovered required formals; the executable profile
admits IR shapes, including proven integer equality, that the predicate compiler rejects. The new
eligibility validators are also incomplete, occurrence sorting has a hash-seed-dependent tie, and
package verification does not normalize missing or malformed seals. Audit:
`.project/active/constraint-exec-code-quality-remediation/audit.md`. All unresolved work
is filed in `BACKLOG.md` as `[CONSTRAINT-FORMAL-COVERAGE]`, `[PROFILE-COMPILER-PARITY]`,
`[CONSTRAINT-MODEL-INVARIANTS]`, `[PART-INDEX-TIEBREAK]`, and
`[CONTRACT-VERIFY-BOUNDARY]`.

The three companion agentic-mbse audit cures are committed and pushed at `82fef09`. Paired
sysml-codegen compatibility with that exact revision remains the next stage.

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

1. **Merge the CONSTRAINT-EXEC PR wave** (human): agentic-mbse #11 FIRST, then sysml-codegen #9
   (imports #11's symbols); teax rwestwood89/teax#3 independent; after #11+#9 merge, push
   fusion-tea: `git -C ~/1cfe/fusion-tea push origin main` (4 acceptance commits waiting).
2. **pipeline_explainer_v2.html build** (`[V2-HTML-BUILD]`, P2): the refreshed
   `EXPLAINER_PROMPT.md` is landed and buildable — another agent picks this up.
3. **CE-F1/F2 follow-ons** (BACKLOG): standalone catalog emission (sysml-codegen/teax shape
   decision) and multi-channel CandidateBridge (teax). CE-F3 is fixed.

---
