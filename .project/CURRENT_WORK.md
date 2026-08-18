# Current Work

**Last Updated**: 2026-08-18 (**stop-reinventing-the-parser: Phase 4 audit remediation implemented;
`audit-phase4-F1` independently re-audited and **FIXED** at `571ed39` (targeted pass; record appended
to `run-records/phase4-audit.md`). Six adversarial mutations — canonical-root and `ADDED_ROOT`
comment edits, an over-edited owned file, a duplicate row, a wrong-hash row, and an added file — all
refuse through the real `--check` gate, and the unmutated tree passes with identical reconciliation
numbers. Finding 2 (the six under-asserting refusal rows and `audit-phase4-F2`) was **not**
re-audited; the audit's bounded Needs Work verdict remains the certification record until it is. Codegen candidate `stop-parser-impl-r2` is now `571ed39`; Agentic remains
read-only at `3f8bd58` (0.1.3 / `semantic-evidence/v2`). `audit-phase4-F1` is answered by an
independent current-byte guard over all 110 fixture sources in all 43 roots, with the one intentional
comment difference ledger-owned. `audit-phase4-F2` is answered by per-cell route strength and named
licensed parser/structure proofs for the two unauthorable deep-override cells. The six narrower
refusal rows' actual assertions are recorded in the plan. Snapshot refusal, graph-driven registry
rendering, and stale reference 08 are fixed; `audit-phase3-F2` is scheduled before Phase 5 names
`C_prod`. Fresh-extraction validation at `571ed39`: **2,496 passed, 34 skipped, 94 deselected**;
focused Phase 4 **206 passed**; lock/reconciliation contracts **32 passed**; TEAx mutation **6
passed**; scoped strict mypy green; broad mypy unchanged at 30 errors / 8 files; changed-file Ruff
clean. `occurrence.py` remains byte-identical to `C_base`. Phase 5 has not started. Do not close or
run pre-PR; `elaborator-downstream` stays blocked. Records:
`.project/active/stop-reinventing-the-parser/run-records/phase4-audit.md` and
`.project/active/stop-reinventing-the-parser/run-records/phase4-remediation.md`.**).
Prior status: 2026-08-17 (**Phase 1 complete and audited — plan
Revision 3 executing design Revision 7; three-leg lock verification green (118/118 against the
tree the lock names); 25-node red set across live/admitted/capture × strict on implementation
branches `stop-parser-impl-r2` `d257ef1` / `stop-parser-evidence-r2` `8d27fb3`; D1-D4 plus
retained harness 162 passed; dedicated audit verdict Pass with findings, all four Majors closed on
execution-backed confirmation (`.project/active/stop-reinventing-the-parser/run-records/phase1-audit.md`).
Orchestrated run paused before Phase 2 by owner directive; Phases 2-5 handoff written to
`/tmp/handoff-20260817-221050.md` (temp-dir per handoff convention — copy before reboot).**).
Prior status: 2026-08-17 (**canonical implementation-plan Revision 2 from the approved Revision-6
design; a Phase-1 stop-rule trip then returned the item to design — rulings 1-7 owner-ratified,
design amended to Revision 7, plan to Revision 3**). Earlier same day: (**fresh independent audit:
Needs Work; the replacement chain is
mechanically sound but semantic and execution-evidence blockers remain**). Earlier: 2026-08-16
(**self-binding-replacement closed and archived** — all ten
functional criteria were independently verified. `[OWNER 2026-08-16]` The dangling-symlink
behavior in the migration/fixture helper is a testing/developer-tooling edge case and accepted
risk; closure was directed without another remediation cycle. Record:
`completed/20260816_self-binding-replacement/audit.md`. Prior item:
**qualified-reference-occurrence-anchoring certified and archived**. Prior context:
**PHASE D FULLY CLOSED; Item 8 sequencing
decided.** The
three-repo merge wave landed and is smoked — squash merges in the pin-enforced order:
agentic-mbse#12 → `main` `1decd95`; codegen#10 → `main` `385e163` (the Item-7 cutover + the whole
CONSTRAINT-SEMANTICS epic + the two contained 20260724 branches); teax#4 → `main` `744745f`. Each
main tree verified byte-identical to its acceptance branch tip. Post-merge licensed smoke on
merged codegen `main`: **2086/34/88, zero license-skip lines**. The CHANGELOG Item-7 "Lessons
Learned" TODO is filled (#12). **Cleanup is now complete**: both item7-rebuild worktrees, both
`item7-rebuild` branches, and `/home/reid/1cfe/item7-rebuild-venv` are deleted, and the CLAUDE.md
`uv` route is verified as the working route from the main checkouts (licensed conformance
1224/34, zero license-skip lines) — the old "never `uv run`" warning is dead. **Next**: roadmap
§C ELABORATE-FIRST Item 8 in owner-decided order **A → B** — the bounded scope scrub first (its
written scope is verified stale two ways), then fusion-tea whole-plant regeneration. See the
2026-08-15 Active Work entry. Held for an owner call: merged remote-branch deletion. **The `in R = R` guidance
obligation question is CLOSED as superseded** — `[OWNER 2026-08-15]` restated the obligation from
scratch (know the right patterns / document them / fix the models / detect the wrong one), ruled the
old epic wording out of context, and directed the epic be amended; so whether an earlier docs pass
partly discharged the old wording no longer matters. Epic amended at `:71-78` and `:503-511`.)

---

## ✅ Item 7 — CLOSED and archived (2026-08-14)

**Verdict: CERTIFY-WITH-RESIDUALS**, archived to
`.project/completed/20260814_constraint-docs-agent-sync/`. Every probed claim reproduced under
independent re-run, including the licensed suite (`2070 passed`, zero license-skip lines), the
post-edit sweep in all three repos (hit-for-hit), the owner-verbatim diff (empty), the matrix
recount (280/136/3/131/10/0, 33 families), and the branch/boundary discipline (no code, fixture or
schema path in any commit; nothing pushed; the out-of-bounds checkout clean). Collect check after
archiving: `2104/2183 tests collected (79 deselected)`, matching the verification baseline.

Four audit findings, all dispositioned. **A-3** — the new `@inapplicable:` "How to write it" example
was refused by the shipped generator under its own D9 rule — was **CLOSED** at the auditor's
re-verification pass after an implement resume took route (a): the exact authored text now generates
to completion and seal, and the marker's reason reaches the generated catalog
(`inapplicability_reason` in `model_contract.json`, `inapplicable_gate_count: 1` with
`coverage_state: 'none'`). **A-4** — the "distinct kept test files" count — was **CLOSED**, method
recorded and **55** reproduced from it independently. **A-1** and **A-2** stand as the two residuals
below.

What landed: the item3-F2 and design-F2 contract amendments, the first `.project/product/` ledger
with P-001 carrying the owner's promise verbatim, the cross-repo `@inapplicable:` /
disposition-vocabulary / six-states teaching, the `modeling-assumptions.md` §8 unit-on-binding
rewrite, the B1–B5 marker rule stated with both its conditions, and the epic-level
verification-matrix reconciliation. SC1/SC3/SC4/SC6 ticked; SC2/SC5 unticked, each naming its
residual.

## ⚠️ The two residuals that ride out of the epic — both owner calls

Neither is work left undone.

**1. Codegen's agent surfaces are symlinks into an out-of-bounds checkout (A-1, blocks SC2/SC3).**
Codegen `.claude/agents/*` and `.claude/skills/sysml-conventions` resolve to
`/home/reid/1cfe/agentic-mbse/claude/…` — the **main** agentic-mbse checkout, on branch
`elaborate-first-salvage`. The item's boundaries allowed agentic-mbse edits only in the worktree
`/home/reid/1cfe/agentic-mbse-item7-rebuild`. The corrected skill is committed there, so a codegen
agent session keeps reading the superseded constraint example until `item7-rebuild` reaches the
branch those symlinks resolve to. Also found: agentic-mbse tracks **two divergent copies** of the
agent definitions (`claude/` 37 files, `.claude/` 23 files) and Item 1 corrected only `claude/`;
this item brought `.claude/agents/sysml-expert.md` level.

**2. Items 3, 5, 8 and 9 carry no REQ tags (A-2, blocks SC5).** The recount is done and both count
blocks were corrected — each was falsified by it — and the one tag-backed gap (the REQ-DIAG family,
absent from the matrix but present in doc 30) is filed. Filing rows for the untagged gates would
mean minting REQ tags first, which is a requirements decision, not a matrix reconciliation. Parked
rather than invented; vehicle `[CONSTRAINT-GATES-UNTAGGED]` in `BACKLOG.md`.

---

## Active Work

### 2026-08-18: stop-reinventing-the-parser — PHASE 4 REMEDIATED; RE-AUDIT PENDING

[AGENT] The bounded Phase 4 audit response is implemented on `stop-parser-impl-r2` at `571ed39`.
No shipped source changed. The current fixture guard now reads all 110 live source files separately
from P_seed reconstruction and requires an exact transition row for every difference. Consumer
closure now states route force per cell; the deep indexed override has a real parser rejection probe,
and the non-expression cell has a real Feature-only structural proof.

The cheap audit notes are also closed in implementation: snapshot refusal is driven publicly,
registry render tests consume graph input, reference 08 is current, and `audit-phase3-F2` is scheduled
in Phase 5 before `C_prod`. The exact validation and setup-only deviations are in
`active/stop-reinventing-the-parser/run-records/phase4-remediation.md`. Phase 5 remains unstarted and
an independent Phase 4 re-audit is next.

### 2026-08-18: stop-reinventing-the-parser — PHASE 4 IMPLEMENTED; AUDIT PENDING

[AGENT] Phase 4 is implemented on `stop-parser-impl-r2` at **`e5f73e6`**. The registry derives its
exit wrappers from the immutable graph before mutation on the CLI, direct generator, and exported
aliases. The full public expression-consumer matrix now covers live, admitted, and capture routes,
with strict and lenient arms where available, and pairs each inventory-first refusal with its real
consumer backstop. A5a and A5b record the indexed bare-chain transitions explicitly.

Fresh-extraction validation is green: full Codegen **2,492 passed, 34 skipped, 94 deselected**;
focused Phase 4 routes **204 passed**; D1–D4 **163 passed**; public TEAx mutation **6 passed**;
Agentic ownership/reference-use **58 passed**; Codegen static closure **68 passed**. Scoped strict
mypy is green. Repository-wide Codegen mypy remains the Phase 3 baseline of 30 errors in 8 files;
Ruff remains a non-green 608-error baseline, with every Phase 4 Python change clean under targeted
Ruff. The owner-retired PDF/HTML suite was not run.

The run discovered that the historical fixture validator compared locked sources with working-tree
bytes even though the lock names `P_seed`; it now reads those bytes from Git history. It also found
that three backlog rows required by the binding design had not actually been filed. They are now
recorded as agent-grade follow-ups. Neither discovery changes product semantics.

Implementation is not certification. Run an independent `$my-audit` for Phase 4 next. Phase 5 and
close remain blocked, and `elaborator-downstream` remains blocked until the whole predecessor is
implemented, audited, and closed.

### 2026-08-18: stop-reinventing-the-parser — PHASE 3 RE-AUDITED; N1/N2 CLOSED

[AGENT] The Phase 3 audit findings were addressed at `3377cd0` and independently re-audited **Pass
with findings**. The two follow-ups are closed at **`1451615`**: N1 took route (b), deleting the
redundant elaborator refusal so `require_exact_binding_use` owns it once, and N2 records exact suite
commands. The implementation response, mutation kill, source hashes, and record-correction commit
are in `active/stop-reinventing-the-parser/run-records/phase3-remediation.md`.

The four blockers now have direct closure evidence. Role assignment is inventory-owned and unit
normalized. Consumers retrieve the authoritative site. `ExpressionInventoryError` converts at the
public boundary with authored reference, root-relative location, and cause. Each consumer adapter
has a real inventory-bypass test. Every binding-union switch is pinned, including the helper arm
found missing during the remediation's own mutation pass. Ownership rows include the receiver, so a
second unannotated receiver inside a reviewed function fails equality.

All 15 Minors and 9 Informationals have code, test, or record dispositions. The audit's exact
weakenings now kill their proofs: five consumer nodes fail when the backstops are removed; the four
binding switches fail when their arms are weakened; and the non-`Feature` deep-path test fails when
the refusal becomes a silent `continue`. L-181's replacement gate is green.

Closure validation: exact 13-file battery **290 passed, 1 deselected**; prior `3377cd0` aggregate
suite **1 failed, 2,388 passed, 34 skipped, 94 deselected**. The sole failure is the owner-declared
Phase 4 consumer-cell proof table. The recorded ledger/fingerprint topology subset is **83 passed**;
scoped strict mypy is zero and targeted Ruff is clean.

The historical audit below remains **Needs Work**. This pass does not self-certify. Run an
independent Phase 3 re-audit next. Phase 4 and Phase 5 remain unstarted; close and pre-PR remain
blocked.

### 2026-08-18: stop-reinventing-the-parser — PHASE 3 AUDITED, NEEDS WORK

Phase 3 ("make Codegen accept only closed evidence") is implemented on `stop-parser-impl-r2` at
**`e3e1a39`** against Agentic `3f8bd58`. The dedicated adversarial audit plan rev 4 requires is at
`active/stop-reinventing-the-parser/run-records/phase3-audit.md`. **Verdict: Needs Work.**

What holds. The architecture is real: one pre-graph inventory is genuinely first in the conversion
boundary, an `IndexedReferenceUse` cannot be converted to an exact one by any route found, the
deep-relationship path factory is total in production, the value-site unit policy delegates every
structural question to Agentic's primitive, and the ownership closure is repository-wide rather than
a narrowed scan. Every number in the completion record reproduces from an independent extraction,
including the declared archive SHA-256, matched byte for byte. The product-lens block `audit3-F1`,
standing since 2026-08-17, is recorded **FIXED** with measured evidence across six authored shapes.

What blocks.

- **M1 (also product-lens BLOCK `audit-phase3-F4`, owner-grade).** A valid, diagnostic-free model —
  `attribute mirror_len : Real = base_len [m];`, and the feature-chain form — crashes
  `sysml-codegen generate` with a raw `ExpressionInventoryError` carrying no code, no authored
  reference, no `file:line`, no cause. The ALIAS-vs-COMPUTED_ATTRIBUTE role is decided twice by two
  identical predicates on different inputs (`expression_evidence.py:245` raw,
  `elaborate.py:871,894` unit-unwrapped). Phase-3-introduced; invisible to the suite because the
  only `= ref [unit]` fixtures use the binding role, which is keyed by owner.
- **M2, M3 — two unmet owner conditions on the accepted tests-after deviation.** The per-consumer
  inventory-bypass tests do not exist (the test carrying that name calls one library function five
  times with a different label); deleting the backstop from all five consumer adapters gives 0 new
  failures across 2206 tests. The closed union is not pinned exhaustively at every switch; four arms
  removed at once — including the one that reclassifies an authored index as *supported* — also give
  0 new failures.
- **M4.** The ownership manifest keys on `(module, function, selector, form)`, so a second
  unannotated receiver inside an already-rowed function is invisible to both gates — bypassing the
  design's own "an unannotated receiver can never qualify" rule in 20 rowed functions.

Fifteen Minors and nine Informationals are recorded. Carried Phase-1 Minors 6, 7, 8 and
Informational 12 are verified closed by mutation. Note for the record: the ownership closure moved
zero reads — it is 16 typed reclassifications plus 4 mechanical exclusions, both permitted, but the
completion record's phrasing reads as though reads were removed.

Recommended order: M1 first (a live regression, and fixing the duplicated role decision also closes
the site-set/role coverage gap), then M2 and M3, then M4. Phases 4 and 5 are not started. Do not
close, do not run pre-PR; `elaborator-downstream` stays blocked.

### 2026-08-17: stop-reinventing-the-parser — NEEDS WORK AFTER FRESH AUDIT

The audited replacement chain is Agentic `A_final`
`2171016d3e3e0805525aa4cf787c55c6293dd00c`, codegen `C_prod`
`78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, Fusion `F_final`
`028f98741a2aea7c238beed961402857af82d15f`, and direct-child six-path `C_evidence`
`588d5f7c9013d98c838a376ab9c69c95ef444649`. All earlier chains remain historical. The six first-
audit findings remain fixed on their intended routes, but the new audit reproduced additional
public gaps. A computed-attribute `cells#(2).mass` can lose its index and bind `cells[0].mass`; B3
unit/depth and B4 binding paths can escape typed diagnostics; deep-literal reference construction
can drop an unresolved middle segment; and the exported B9 registry seam accepts an empty or wrong
exit-type set. Product-lens gate `audit3-F1` is `BLOCKED`.

The exact retained auditor still reports four structural PASS groups, topology tests pass 18/18,
both maintained Fusion roots pass their 23/23 live/snapshot/real-TEAx mutation proof, and all four
audited implementation/evidence worktrees are clean. Those checks do not certify the execution
record. Final `independent-green.json` was assembled by an unlocked external staging script rather
than emitted by the committed runner, so recorded subprocess output/import claims are not
reconstructable. **[OWNER-VERBATIM 2026-08-17]** “do not rerun the PDF suite anymore. It's fine --
it is totally separate to everything we doing. I have ZERO concerns about it. Please mark this
SOMEWHERE so we never run it again.” This settled owner correction permanently retires
`uv run pytest tests/ -m slow -k "not test_claude_extraction"` from parser-work validation. It is
not a certification gate, and its historical result is informational only. Nonzero baselines
remain named as non-green, 13 harness attempts remain nonverdicts, and the 15 paid/network cases
remain unrun. See
`active/stop-reinventing-the-parser/audit.md`. Do not close or run pre-PR. `elaborator-downstream`
remains blocked.

**[AGENT] Research conclusion (2026-08-17):** the occurrence core is holding, but the current
site-by-site remediation method is not demonstrably converging. The indexed, B3, B4, and B9
findings converge on one bounded enforcement defect: a typed semantic owner exists while alternate
public consumers can still acquire weaker evidence or accept a second caller-supplied invariant.
The live raw-SysIDE route set is finite and can be closed mechanically. Return to technical design
before another implementation pass: revise D5/D7/D9 around exclusive evidence ownership,
valid-by-construction paths, graph-derived registry types, and a checked consumer/ownership
manifest. Preserve D1-D4 and the general `ExpressionIR`. Research and exact closure criteria:
`.project/research/20260817-164828_expression-evidence-boundary-convergence-assessment.md`.

**[AGENT] Design response (2026-08-17):** `active/stop-reinventing-the-parser/design.md` is now
draft Revision 5. D1-D4 and D6 remain intact. Revised D5/D7 make exact reference evidence exclusive
with `ExactReferenceUse` / `IndexedReferenceUse`, one pregraph consumer inventory, closed binding
variants, a total deep-relationship path factory, repository-local raw-selector manifests, and a
natural-route closure matrix. Revised D9 derives registry wrapper types from the graph at every
exported seam. The Revision-4 review is marked historical and the existing plan is superseded. Do
not implement from it. Next stage is a fresh `$my-design-review`, then a replacement `$my-plan` if
the review approves the design.

**[AGENT] Revision-6 response (2026-08-17):** the finalized Revision-5 review is incorporated in
`active/stop-reinventing-the-parser/design.md`. Implementation branches from the old `C_prod`
`78a9beb9` and preserves D1-D4, probes, and the verification harness. Agentic's permissive fact API,
bool index marker, aliases, and exports are deleted; every measured Agentic and Codegen consumer
migrates to provenance-complete closed variants. Closure now requires three separate green legs:
selector ownership with AST-evasion coverage, unrepresentable weak states with scoped strict type
gates, and natural-route matrices that distinguish inventory refusal from consumer backstops. The
registry and elaborated-pipeline code facts are corrected. Do not implement from the superseded
plan.

**[AGENT] Revision-6 review confirmation (2026-08-17): APPROVE.** The targeted re-check verified
every finalized Revision-5 resolution incorporated without reopening D1-D4, vetted the design
agent's provenance-complete-payload pushback against the universal-tree rejection (the line
holds — reference-target provenance only, IR stays the sole math representation), and
independently confirmed the `IndexExpression` stub citation and the `ExpressionRef`
no-unrelated-consumer deletion claim. Record:
`active/stop-reinventing-the-parser/design-review.md` ("Revision-6 targeted re-check"). All three
base/API/type-gate rulings are `[OWNER 2026-08-17]` (build on old `C_prod` `78a9beb9`; delete the
permissive API rather than manifest it; add the scoped strict type gate). Product-lens gate stays
`BLOCKED (audit3-F1, DEFERRED)` until the live-and-capture computed-attribute proof is green on a
production commit. Next stage: replacement `$my-plan` from design Revision 6, then implement,
then independent `$my-audit`.

**[AGENT] (ratified by owner, 2026-08-17) Plan Revision-2 draft:** the owner approved the five-phase
strategy: verify the exact base and establish the red closure harness; close Agentic's evidence
contract; make Codegen consume only closed evidence; close public routes and graph-derived registry
authority; then rebuild the immutable artifact chain for independent audit. The 2,356-line
superseded checklist is preserved as
`active/stop-reinventing-the-parser/plan.failed-candidate.md`. The fresh canonical
`active/stop-reinventing-the-parser/plan.md` is Revision 2 and does not resume or append to that
checklist. No production code was changed. Next stage after plan acceptance is `$my-implement`,
followed by an independent `$my-audit`.

### 2026-08-16: stop-reinventing-the-parser — SPEC REV 4

`.project/active/stop-reinventing-the-parser/spec.md`. The corrected contract preserves P-002 and
targets two bounded problems: occurrence election that is not derivable from the model, and evidence
loss between SysIDE and generation. Each scoped site now names its own proof; forced failures are
used only where failure swallowing is the defect, while semantic rows use real models through
SysIDE. The dirty worktree is excluded from the baseline. The closed predecessor changes must land
on named commits before design. The P-004-aware product lens is `CLEAR`; the fresh adversarial spec
review verdict is `Approve`.

**[AGENT] (ratified by owner, 2026-08-16):** this item is the explicit gate for
`elaborator-downstream`; it must be implemented, audited, and closed before downstream design or
implementation starts. The premise audit at
`.project/research/20260816-205035_premise-audit-fallback-census.md` is the primary research input.
The older census is superseded and is not a contract.

### 2026-08-16: elaborator-downstream — SPEC REVISED AFTER REVIEW (Item 8 remainder)

Draft: `.project/active/elaborator-downstream/spec.md`. Scope is the post-self-binding Fusion Tea
package/contract regeneration, stock-API TEAx execution and new lineage, July IFE impact audit,
an independently anchored `REQ-SI` family, README/reference-doc repair, and one closing composed
proof. The codegen fixture now converges on the customer's measured post-R-2 shape; document 25 is
retained and bounded as test-only/off-route. **[AGENT] (ratified by owner, 2026-08-16):** Stellarator
migration stays in `[STELLARATOR-D5-MIGRATION]`, and the July impact claim uses named repository and
project roots plus owner attestation. The self-binding sibling is closed at
`completed/20260816_self-binding-replacement/`: all functional criteria are independently verified,
and the owner accepted the remaining testing/developer-tooling edge risk. This item performs none
of that sibling's remediation. The adversarial review's resolutions are incorporated; the revised
product-lens rerun is `CLEAR` and explicitly resolves prior `spec-F1`. Its contract is ready, but
design and implementation wait for `stop-reinventing-the-parser` to close.

### 2026-08-15: dead-worktree-pins — CERTIFIED, awaiting close confirmation

Residue of the phase-D cleanup, not an epic item. Both gates the cleanup broke are repaired at the
working tree (uncommitted): the execution-lane `environment` fixture now pins anchor-derived main
checkouts via a pure predicate (`tests/execution/environment_pins.py`, negative checks kept in the
default suite), and `check_ledger_4a.py` points its companion root at `../agentic-mbse` and
abstains with exit 2 when a configured checkout is missing. Verified: execution lane **88 passed,
0 errors** from the main checkouts (first main-checkout reproduction); `paths` gives
`304 rows checked, 0 problems` with the two agentic rows (L-036/L-037) genuinely parsed. The audit
follow-up at `14fe868` falsifies both real rows in a kept regression and corrects the stale checker
docstring; both targeted files pass all **65** tests. Audit verdict is **Certify** and product
judgment is **CLEAR**. Spec: `.project/active/dead-worktree-pins/spec.md`; audit: `audit.md`.
`spec-F7` (durable home for the deferred coverage-split idea) still needs its recorded close-time
disposition.

**⚠ Surfaced while verifying, unowned:** the full default suite (licensed, project `.venv`) shows
**17 pre-existing ordering-dependent failures at clean HEAD `9ce5548`** — byte-identical failure
set with and without this item's changes; every affected file passes when run alone
(`tests/unit/test_report_precedence.py` 12, `tests/runtime/test_fusion_tea_acceptance.py` 4,
`tests/conformance/test_output_schema_contract.py` 1). The phase-D `2086`-green figure does not
reproduce as a full-suite run in this venv even at HEAD. Out of this item's scope (Non-Goals: no
re-certification); needs an owner.

### 2026-08-15: Item 8 sequencing — OWNER DECISION: scope scrub first, then fusion-tea regeneration

**`[OWNER 2026-08-15]` Order is A → B**: run the mandated Item-8 scope scrub first, then put
fusion-tea whole-plant regeneration at the front of the test half. Two options were declined:
straight-to-regeneration (B first) and the clean-up sweep (C first).

**Why the scrub is load-bearing, not ceremony** — Item 8's written scope was verified stale in
two ways this session, so it cannot be executed against its own text:

1. **The doc-repair list conflicts.** Epic §C item 3 names docs **11/12/13/16/24/25**; CLAUDE.md's
   retiring banner names **03/04/05/07/10/11/12/13/17/24/25/28**. Twelve versus six, **five overlap**
   (11, 12, 13, 24, 25) — an earlier revision of this line said four, which was wrong.
   Reconciling them is scrub output.
2. **Epic §C item 4 is an `[OWNER-VERBATIM]` obligation**, restated from scratch by the owner on
   2026-08-15: know the right pattern(s) for the situation, document them, fix the models to use
   them, and detect the wrong `in R = R` form. It carries **no count of replacement forms** — the
   former "two valid replacement forms" wording was agent-authored under an owner-verbatim stamp
   and is retracted at the source (`epic_elaborate_first_architecture.md:503-511`). The question of
   whether an earlier docs pass discharged the old wording is **closed as superseded** by the same
   restatement (see `:15-19` above); it is not an open owner question.

**Scrub bounds `[OWNER 2026-08-15]`**: one scope table (each §C sub-item vs what Items 1/7 already
delivered) plus the reconciled doc list. **Zero repairs performed**, ~half a day. Fold in the
missing `.project/scripts/adr.sh` / `product.sh` (promise + ADR filing broken until the pack
re-inits) since the scrub's output wants filing. The table splits Item 8 into "test now" and
"repair later" halves.

**Then B**: fusion-tea whole-plant regeneration on the exact route. **Two carried premises for B
were falsified 2026-08-15 — do not plan against them:**

- ❌ "stopped at 10 unresolved cross-part bindings" — **the 10 were resolved 2026-07-06** by
  PIPELINE-TRUTH Item 2's supplied-value materializer, verified by toggling it
  (`.project/active/whole-plant-resolution/audit.md:12-45`); the BACKLOG row is closed as
  superseded (`BACKLOG.md:953-958`). The exact route resolves them *by construction* — the
  materializer was deleted in retirement step 2 (`82c7951`) because supplied values are a
  legacy-resolver concept (ledger L-014); the mechanism is now a typed `NodeRef` edge onto the
  modelled `AttrNode` (`elaboration/project.py:436-470`).
- ❌ "has never been regenerated since" — **the whole plant WAS regenerated on the exact route
  2026-08-11**, cutover-recovery Slice 3D: loaded, elaborated, projected, generated, sealed,
  verified by TEAx's own loader, discovered through the public SimKit registry builder, executed by
  `simkit.core.pipeline.execute_pipeline`. 11 channels, LCOE `270.1211779380445`, live and
  relocated legs equal, mutation every-and-only proved on two axes
  (`.project/completed/20260814_cutover-recovery/plan.md:1944-2100`).

**So B is not a codegen question — it is a customer-repo model migration**, and nobody had recorded
it as such. The whole divergence between the codegen fixture and `/home/reid/1cfe/fusion-tea/models/`
is two things (9 of 11 files are byte-identical after stripping the authorized `_in` suffixes):

1. **15 self-named bindings still in the customer repo** — verified 2026-08-15 by direct count
   (`grep -rnP '\bin (\w+) *= *\1\s*;'`; the codegen fixture is at **0**, which is F19 discharged).
   The exact route refuses these as `SI_SELF_BINDING`. Sites: `designs/generic_ife/ife_plant.sysml`
   ×10, `designs/hif_ife/hif_driver.sysml` ×2, `designs/hif_ife/hif_plant.sysml` ×3. Recipe is
   mechanized and self-checking: `scripts/make_d5_variant.py` (proof is a strip check, so a stray
   reformat cannot hide). **Editing the customer's model needs an owner ruling.**
2. **`hif_driver_instance`** — present in the codegen fixture
   (`tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml:100`), **deleted from the customer
   repo** in July as workaround R-2. ⚠ **The Slice-3D proof depends on the workaround being
   present**: two of its 11 pinned channels are `hif_driver__hif_driver_instance__meier_cost__*`
   (`tests/execution/test_fusion_tea_real_teax.py:56-68`). So the certified evidence is of the
   **pre-retirement** shape; the workaround-free shape the customer actually has is **unproven on
   this route**. Expected 9 channels (July's legacy run went 7 modules → 6 on deletion) — inference,
   not evidence. One capture run answers it. Needs an owner call: regenerate workaround-free and
   re-anchor the pin to 9, or restore the instance and contradict R-2.

**Branch question resolved**: `item8-fusion-embedded-catalog` is **fusion-tea's own** item numbering
(its CONSTRAINT-EXEC epic, commits all 2026-07-20), **not** codegen ELABORATE-FIRST Item 8 — so it is
not already-started Item 8 work. It is 6 ahead / 0 behind `main`, already did the TEAx-compat half of
scope item 1 (stock multi-channel bridge, wrappers deleted, per-definition predicate API), and
inherits the workaround-free model from `main` (PR #101, `91d03a7f`). **It is the right base.** Its
working tree is dirty (modified `uv.lock` + ~20 untracked dirs) — clean or stash first.

**Split the Stellarator out of scope item 1** `[recommended 2026-08-15]`: the model lives at
`/home/reid/1cfe/fusion-tea-stellarator-mbse-demo` (branch `feat/stellarator-mbse-demo`) and carries
**114 self-named bindings** (verified by the same count), including a literal `in R = R` at
`models/designs/generic_mfe/mfe_plant.sysml:117`. That is ~99 renames beyond the IFE 15, on a model
never elaborated on the exact route. It does not belong in the same item as fusion-tea.

`SI_RENDERING_COLLISION` (the Item-10 cross-part blocker) **does not apply to the IFE plant** — grep
for `sum(`/`collect`/`reduce` over the customer models returns zero hits, and the model demonstrably
captures at HEAD.

**Environment and cleanup, both closed this session:**

- **The two item7-rebuild worktrees, both `item7-rebuild` branches, and
  `/home/reid/1cfe/item7-rebuild-venv` are deleted.** Containment re-verified before deletion:
  agentic's `main`-vs-tip diff empty; codegen's diff was three files with **`main` ahead** (the
  restored symlink + the filled CHANGELOG TODO), nothing branch-only. `branch -D` was required —
  squash merges hide ancestry. Left alone deliberately: the `wi029-pin` and `/tmp/*` detached
  pins, `item7-recovery-archive`, and codegen's `source-identity-epic` label.
- **The CLAUDE.md `uv` route is now the proven route** — the old "never `uv run`" warning is
  dead, it existed only because `../agentic-mbse` was parked behind. Verified: `uv pip install -e
  ../agentic-mbse` then both imports resolve into the **main** checkouts (no worktree paths), and
  licensed `tests/conformance` gives **1224 passed / 34 skipped, zero license-skip lines** (all 34
  skips the benign "no computed attributes in the golden" family). The `sysml-conventions` symlink
  resolves into the main agentic checkout.
- **The `uv` route does NOT cover the execution lane** — that lane needs teax-simkit's own deps
  (`pandas`), which this project's `.venv` does not carry, exactly as the marker at
  `pyproject.toml:50` says. The lane is excluded from the default run, so it must be selected
  explicitly (`pytest -m execution`, or override `-m` entirely — `pyproject.toml:44-50`). The
  working invocation, verified 2026-08-15:

  ```bash
  set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
  PYTHONPATH=/home/reid/1cfe/teax/packages/teax-simkit:/home/reid/1cfe/sysml-codegen/src \
    /home/reid/1cfe/agentic-mbse/.venv/bin/python -m pytest tests/execution -m execution -q
  ```

  ⚠ **CORRECTED 2026-08-15 — an earlier version of this block claimed both worktree-pin defects
  were "repaired" and reported `88 passed` plus a re-verified `304 rows / 0 problems`. That was
  written before the repairs were REVERTED at owner instruction, and was left stale for part of the
  session.** At HEAD `9ce5548` **both defects are live**: the lane gives **76 passed, 12 errors**
  (the `environment` fixture still asserts `-item7-rebuild/`), and `check_ledger_4a.py paths` still
  prints `304 rows checked, 0 problems` while its companion root is absent — so the
  `repo: agentic-mbse` rows pass by absence rather than by verification. The `88 passed` figure was
  only ever reached **with** the reverted repair applied; do not cite it as a HEAD result. Both
  defects are specified in `.project/active/dead-worktree-pins/spec.md`.
- **Still awaiting an owner call** (held, not forgotten): deleting merged remote branches (codegen
  `item7-rebuild`, `post-merge-wrapup`, `item7-lessons-learned`; agentic `item7-rebuild`; teax
  `constraint-semantics-item3`) and the teax local `constraint-semantics-item3` label.

### 2026-08-14: ELABORATE-FIRST Item 7 — CLOSED and archived; phase-D pre_pr checks green

- **Archived** (owner-authorized after step-10 acceptance): `cutover-recovery/` →
  `.project/completed/20260814_cutover-recovery/`; `elaborator-cutover/` →
  `.project/completed/20260814_elaborator-cutover/` (spec/design/census; superseded plan kept
  as shaping evidence). Epic Item-7 success criteria ticked with dated provenance.
- **Product-lens gate CLEAR**: the 2026-08-11 `BLOCKED (audit-F1, audit-F2)` state resolved by
  citation in a dated close block — F1 (exemption deleted, pinned by `test_item12_checks.py`),
  F2 (retirement executed, absence pinned), F3/F4 (three-route mutation proof; step-5 portable
  provenance) — each citing the owner REVISE disposition, step-9 audit, and step-10 acceptance.
- **Deletion ledger rehomed** `[OWNER 2026-08-14]`: `ledger-4a.{json,md}` →
  `.project/ledger/` (living gate data — future test renames still sweep it); constants in
  `check_ledger_4a.py` / `_ledger_edit.py` / `retirement_worklist.py` repointed; the F1
  docstring disclosure (sixth ceiling: `replacements` skips the two `repo: agentic-mbse`
  rows) added in the same touch per the phase-D ruling. Re-verified: paths 304/0, groups
  READY, 62 ledger-script tests pass.
- **pre_pr checks green in all three repos** at the acceptance OIDs (suite numbers in the top
  block). Post-repoint full-suite re-run recorded below. One superseded-item residual noted:
  `completed/20260810_source-identity-occurrence-foundation/` archives its lens BLOCKED — a
  supersession record (that implementation never entered this branch), not a shipping blocker.
- Remaining phase D is owner-run: merge agentic-mbse → codegen → TEAx, delete the
  `elaborate-first-salvage` label, return the main agentic checkout to `main`, restore the
  `sysml-conventions` symlink, clean up worktrees.

### 2026-08-14: Phase B — cutover COMPLETE: step 9 audit CERTIFY-WITH-RESIDUALS, step 10 OWNER ACCEPTED

Independent audit (`evidence/audit-9-final.md`): **CERTIFY-WITH-RESIDUALS, 0 blocking /
1 major / 3 minor** — all six subjects verify on substance; findings record-accuracy/spec-text
only. **[OWNER 2026-08-14] dispositioned all four and ACCEPTED** (full rulings + verbatim
acceptance basis: plan.md "Narrow-correction step 10 completion"; gate summary: plan.md
"Gate 3 — final acceptance"). The disposition pass (same commit as the acceptance tick):
L-036/L-037 re-pointed to `tests/test_sysml/` (65 passed, verified twice); the 302-of-304
sweep wording corrected everywhere; R12 mypy amended to the measured 73-in-18 / 118-in-28
(dated, owner-approved); the governed `src tests` ruff numbers added beside T4; T1 gains the
18 renames (builder fixed, record rebuilt, tables re-verified verbatim).

**Left for phase D, by the owner's F1 ruling:** the optional `check_ledger_4a.py` docstring
line disclosing the cross-repo skip (touches `scripts/`; folds in when the tree changes for
PR prep). **No push, tag, promote, close, or archive happened; item close and the phase-D
merge wave remain owner-directed.**

### 2026-08-14: Phase B — cutover steps 7–8 EXECUTED (batteries + final candidate record) — record

**[OWNER 2026-08-14]** ruled the tree final ("no changes in flight") at `540ad59` and directed
steps 7–9. Full record: plan.md "Narrow-correction steps 7 and 8 completion". Headlines:

- **Three consecutive complete batteries, 51/51 fields identical**, at codegen `2819501` /
  agentic `6372ef7` / TEAx `75eecb3` (`evidence/phase5-runs/final-runs/`, comparator exit 0).
  Suite 2086/34/88 zero license-skip; agentic 1831/1/5; lane 88 (incl. the gain=100 three-route
  proof — register row-3 single-shot obligation discharged); verify 15/22/0, fixture churn 0;
  ruff 12/1 = the R12 baseline sets exactly; mypy 52-in-11; ledger 304/0, replacements
  223/79/**0 FAIL** (302-of-304-row sweep, first since REVISE; the two skipped agentic rows
  verified directly — audit-9 F1); diff checks clean.
- **The battery caught one defect first pass**: L-179 still cited the step-5-renamed
  differ-only pin. Cured (`2819501`, ledger citation re-pointed, shipped-path diff vs the ruled
  `540ad59` empty), partial runs discarded, all three recorded runs measure the repaired tree.
- **Step 8**: `evidence/candidate.{md,json}` + `final-candidate-tables.md` regenerated by
  `build_candidate_final.py` — every number derived from logs/git/bytes. Four things surfaced,
  not silently resolved (candidate.md §6): the L-179 cure; **the R12 agentic-mypy clause
  discrepancy** (spec ≤105-in-23 vs every recorded measurement 108-in-26 — parked to step-9
  audit + owner); the TEAx docs-only pin move; the known pre-existing artifacts.
- **Steps 7–8 are spent**: further substantive shipped-path change invalidates them.

**Next: step 9 fresh narrow audit** (compiler convergence + symbol removal, replacement
coverage, R8, portable provenance, final gate semantics, evidence consistency — not a
re-review of the 195 deletions), **then step 10 owner final acceptance** (no
push/tag/close/archive from agents).

### 2026-08-14: Phase B — cutover step 6 EXECUTED (ruff R12 amendment) — record

Step 6 ran per the pre-declared brief
`.project/active/cutover-recovery/briefs/correction-step6-ruff-r12-amendment.md` (disposition 2,
`[AGENT] (ratified for execution by owner, 2026-08-12)`). Full record: plan.md
"Narrow-correction step 6 completion". Headlines:

- **Spec R12 no longer demands clean production Ruff** — it carries the zero-new baseline with
  both finding **sets** recorded by name (codegen `src` **12**, all UP042, enumerated; companion
  `src` **1**, `extraction/index.py:146 N806` at `6372ef7`). Set comparison, not counts; changed
  files clean unless their only findings are recorded pre-existing ones; totals no worse. The
  ratified 14 was stale; the measured 12 is recorded per the standing instruction.
- **Two recorded judgment calls:** the R12 command list drops `uv run` and `../agentic-mbse`
  (both resolve the parked checkout — commands restate against the item7-rebuild venv until
  phase D); the "coordinated repository gates" SC box **stays unticked** — its ruff blocker is
  discharged (tick-provenance note updated, dated) but the tick belongs to the fresh
  exact-count step 7–8 batteries at the final paired OIDs.
- **No code, test, fixture, matrix, or ledger path touched.** Ruff measured identical before
  and after; `git diff --check` clean; step-5 gate baselines stand as the current-tree record.

Steps 7–8 executed later the same day on the owner's tree-final ruling — see the entry above.

### 2026-08-14: Phase B — cutover step 5 EXECUTED (portable provenance) — record

Step 5 ran in-session directly after step 4, per the ratified disposition 4 and the
pre-declared plan `briefs/correction-step5-portable-provenance.md`. **Commit: `a4669af`
(the one bounded step-5 change — brief, code, flipped pins, records; parent `98dc3ec`).**
Full record: plan.md "Narrow-correction step 5 completion". Headlines:

- **The live route now renders the portable `root-N/` source referent on every graph node**
  (`_rewrite_live_sources_as_referents` in `orchestration/elaborated_pipeline.py`, plus NFC in
  the shared encoding) — same shape as capture, derived from the caller's roots, routes NOT
  converged (arm-independence pin stands). **Live and snapshot generation are byte-identical**;
  invariant 35 amended (dated), invariant 34 now true as written; design A1 carries the
  audit-F4-answered note.
- **No snapshot bytes moved** (`--verify` 15/22/0, fixture tree clean — no recapture batch);
  no baseline churn; **zero matrix row edits** (flipped tests are uncited; counts stand).
- Every tripwire pinning the old divergence flipped to assert the new equality by value:
  package byte-identity, fingerprint equality, v6-routes provenance agreement (renamed node —
  ledger L-007/L-010 re-pointed, gate green), usage-domain parity unmasked, execution-lane tree
  equality, `capture_v6_batch.py --verify` unmasked.
- **Gates:** licensed suite **2086/34/88, zero license-skip lines** (+1 = the new NFC unit
  test); collect 2120/2208; execution lane **88**; corpus 9; ledger 304/0, surface 0, groups
  READY; proof integrity 0/0; distinctness 31/0; gated manifest 65 = 56 + 9; ruff src **12**
  and mypy **52-in-11** (zero-new held); `git diff --check` clean. No premise conflict.

Step 6 executed later the same day — see the entry above.

### 2026-08-14: Phase B — cutover step 4 EXECUTED in-session (record)

**[OWNER 2026-08-14]** triggered the resumption, ruled the execution mode (in-session), and made
two in-session rulings; step 4 then ran to completion. **Commits: `cc268d5` (rev-2 brief +
register walk + REQ-CL-03 ruling), `7ebe447` (the bounded step-4 implementation).** The full
record is the plan's "Narrow-correction step 4 completion"
(`.project/active/cutover-recovery/plan.md`). Headlines:

- **The matrix has zero UNTESTED rows for the first time since the retirement.** Recount:
  **288 rows / 156 PASS / 1 PARTIAL (REQ-DIAG-01, recorded deliberate) / 131 RETIRED /
  0 UNTESTED / 34 families / 64 kept test files, none missing from disk.** The nine
  L-149/L-150/L-152 replacement rows closed on behavioral tests through the public route; the
  REQ-DIAG-04 tripwire, the REQ-EPC-01/REQ-GA-03 failing arms, and the REQ-CL-03 amendment
  (usage-domain ruling) landed in the same pass; the REQ-CS family (8 rows, Items 3/8/9) is
  minted per `[CONSTRAINT-GATES-UNTAGGED]` — that backlog entry is complete and the epic/item SC
  boxes are ticked with dated amendments.
- **One product defect surfaced and was cured under the stop-and-surface rule**: smart regen's
  exact-set field comparison churned the generator's own output on defs with declared-but-unused
  inputs. Cure **[AGENT] (ratified by owner, 2026-08-14)**: subset comparison in
  `generation/preservation.py`; doc 23 and REQ-SR rows amended; no generated bytes changed.
- **The gain=100 three-route proof is in** (`test_fusion_tea_mutation_teax.py`, 29 passed):
  exact three-port consumer set including the viability constraint, hand-arithmetic movers at
  100, constraint consumption proved via observed value + margin, and a verdict-flip leg at 20
  in the six-state vocabulary. The single-shot authoritative observation re-runs at steps 7–8.
- **Gates:** licensed suite **2085/34/88, zero license-skip lines** (delta = the 24 new tests);
  execution lane **88**; capture verify **15/22/0**; corpus **9**; ledger 304/0, surface 0,
  groups READY; proof integrity 0/0; distinctness 31/0; gated manifest 65 = 56 + 9; ruff src
  **12** and mypy **52-in-11** (both improved over the epic, zero-new held); `git diff --check`
  clean. Evidence-Invalidation Register rows 1–7 discharged; rows 3/8/9's single-shot
  obligations ride to steps 7–8.

Step 5 executed later the same day — see the entry above.

### 2026-08-14: CONSTRAINT-SEMANTICS epic — CLOSED and archived; next is phase B

The epic is done. Nothing in it is live work any more. Where things stand:

- **Epic closed and archived 2026-08-14** by owner ruling, after all nine items closed:
  `.project/completed/20260814_epic_constraint_semantics_contract.md`, with the umbrella shaping
  folder preserved whole beside it at
  `.project/completed/20260814_constraint-semantics-contract/` (spec, rulings, spec-review,
  product-lens) as the epic's decision record.
- **`pre_pr` was NOT run, by ruling.** It is deferred to the **phase-D branch gate** below. The
  epic's changes live on the unmerged `item7-rebuild` line and ship with it; the gate runs once over
  the whole branch line.
- **The Item 7 Evidence-Invalidation Register is HANDED, not discharged.** Its nine rows are
  complete and archived with the epic; walking them row by row is **phase B step 1**. No paused
  ELABORATE-FIRST Item 7 step 4–10 evidence may be reused without that walk — every row marked
  *Invalid* really is.
- **Three open decisions survive the epic, all the owner's:** the codegen `.claude/` **symlink
  target** (resolves at merge); **`[CONSTRAINT-GATES-UNTAGGED]`** (REQ tags for Items 3/5/8/9 —
  assigned 2026-08-14 to cutover step 4 so the matrix is touched once); and the **parked D-2 vs
  D-4/SRC-01 premise conflict** at umbrella `spec.md:325`, which no item resolved in either
  direction and which archived still open.
- **Surfaced at close, unresolved:** `.project/product/INDEX.md` and `P-001` name the epic file as
  the durable one-hop lens trail node, on the recorded reasoning that it does not archive. The close
  falsifies that. The **paths** were repointed so the trail resolves; **no promise text or authority
  grade was touched**. Whether a trail node in `completed/` is good enough, or whether it belongs
  somewhere that never archives, is the owner's call.
- **Item 6's production implementation is out of this epic `[OWNER 2026-08-13]`** and is now the
  unowned backlog entry `[CALCDEF-GATE-IMPLEMENTATION]` (P1, 7–9 days, graph v4 + catalog 4.0.0,
  codegen + TEAx), parked with the owner. It competes for the next slot with
  `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` (P1). Its plan of record is
  `.project/completed/20260813_calcdef-constraint-gate-design/implementation-item.md`. The Item 8
  start gate is satisfied at `62a07e5`; the only remaining block is owner authorization. No agent
  starts it without a new ruling.
- **Nothing pushed; no `main` touched anywhere; TEAx stays on `constraint-semantics-item3` @
  `5b70ae9`** until the phase-D merge (codegen first, TEAx second — never the reverse).

### 2026-08-12: Constraint-semantics contract — spec drafted (owner-directed priority)

**[OWNER 2026-08-12]** redirected priority after the Item 7 step-4 probe: settle constraint
semantics first ("get to the bottom of 'how do constraints work'"), fix docs and the test model to
match, then test. Research:
`.project/research/20260812-101200_constraint-semantics-end-to-end.md` (65 authored CATF checks →
9 visible dispositions → 0 executed; 56 usages with no catalog carrier; docs contradict code and
standard; report can claim `all_satisfied` over partial coverage; TEAx sees such models as
`unconstrained`). Eight rulings recorded 2026-08-12 (assert-only enforcement; calc-def gate
semantics ruled + staged; catalog totality hard-gated with severity by cause; bindings-only
predicates + equality-usage instruction; coverage-true headline; boundary-default study policy;
requirements-side non-executable; migration in a new CATF derivative).
**Spec: `.project/completed/20260814_constraint-semantics-contract/spec.md` (archived at epic close
2026-08-14; was `.project/active/constraint-semantics-contract/`) — reviewed (verdict Revise) and
revised same day; all findings resolved in `spec-review.md`, four owner-selected refinements
recorded in `rulings-20260812.md` (asserted-gates denominator; vacuous = missing assessment until
dispositioned; all-65 CATF disposition table; umbrella structure). Next: `/_my_epic_plan`
decomposition.** Item 7 narrow-correction steps 4–10 resume after this contract lands.

### 2026-08-12: Item 7 cutover recovery — R8 complete; replacement coverage next

**Where it stands.** Narrow-correction steps 1–3 are complete. The real compiler convergence and
ledger-checker hardening landed in codegen commit
`057bf29a3209470cd6ccfd882b1d3e6dd6d76a45`. R8 now keeps the shortest resolved qualifier only
when distinct reference chains in one expression share a leaf name; unique chains keep their
prior leaf-only public names, and repeated exact sources still deduplicate. **[AGENT] (ratified
for execution by owner, 2026-08-12)** The recovered implementation stays in place. Item 7 remains
open for narrow-correction steps 4–10.

- **Correction authority:** all ten ratified dispositions are recorded question by question in
  `.project/active/cutover-recovery/owner-disposition-20260811.md`; the persistent ten-step
  execution sequence is in `.project/active/cutover-recovery/plan.md`.
- **Progress:** narrow-correction steps 1–3 are complete. **[OWNER 2026-08-12] Steps 4–10 are
  PAUSED until the constraint-semantics contract work (entry above) lands.** The pause record
  with resumption consequences is in `plan.md` ("PAUSED at step 4"): the step-4 brief is
  partially superseded and needs revision before execution; steps 7–8 (batteries + candidate
  record) run once, after the contract work, at the true final tree; the contract epic owns the
  evidence-invalidation register. Steps 1–3's committed work stands (orthogonal subjects).
- **R8 result:** the direct two-term witness projects exact
  `panel_capital_cost_{0,1}` and `caster_capital_cost_{0,1}` inputs to four distinct occurrence
  channels and executes to **16.0**. A unique `panel.capital_cost` chain remains
  `capital_cost_{0,1}`. The D-5-renamed stage-one solar model now preserves its PV-module,
  inverter, and array-BOS same-leaf families. Named intermediates remain a useful authored
  pattern, but are not required to avoid `SI_RENDERING_COLLISION`.
- **Dependency conclusion:** fix-first succeeded within the elaboration name seam. Item 10 is not
  an Item 7 dependency.
- **Step-2 node account:** L-281 retired 10 exact legacy-shape nodes and L-284 retired 11; three
  redundant extractor schema assertions also retired and six checker nodes were added. The
  structured 21-node list and named replacements are in `ledger-4a.json`; the full collection
  decreased by 18 nodes exactly.
- **Step-3 gates:** focused suite **101 passed**; full licensed suite **1689 passed / 34 skipped /
  65 deselected** from the unchanged 1,788-node collection, zero license-skip lines; v6 recapture
  **15/22/0**; corpus **9**; execution **65**. Ledger `paths` **304/0**, `surface` **0**, all six
  `groups` READY, proof integrity **0/0**, and doc distinctness **31/0**. Changed Python files are
  ruff-clean; `ruff check src` remains **14** and mypy remains **57 errors in 11 files**.
- **Superseded checkpoint OIDs:** codegen `6c35aa0`, agentic-mbse `3fbda2f`, TEAx pinned
  `fa0e06a9`.
- **Checkpoint gates:** codegen suite **1707 passed / 34 skipped / 65 deselected**, zero
  `no live syside license` skip lines; ledger **304 rows / 0 problems**; `git diff --check` clean
  in both repos. The three step-7a runs (at `c0ceb24`) agree field for field —
  `evidence/phase5-runs/revise-runs/comparison.md`.
- **Checkpoint audit:** `evidence/audit-7-retired.md`, verdict FINDINGS (10, none blocking). All eight
  requested probes were executed and CONFIRM, so its own clause resolves to *Certify with the
  residual list* now that F1–F3 are dispositioned. The narrow correction requires a fresh audit
  after the substantive fixes; it is not a re-review of all 195 deletions.
- **Final acceptance remains owner-grade.** The correction proposal authorizes no push, tag,
  promotion, close, or archive.
- **Do not** treat the numbers in the superseded 2026-08-11 record as current; that record
  described the pre-retirement tree and lives at commit `013d6a1`.

The pre-REVISE state, kept for context:

### 2026-08-11: Item 7 cutover recovery — owner disposition REVISE (superseded by the entry above)

**The Item 7 cutover execution recorded further down this file is superseded.** It produced no
commit. Its uncommitted candidate mixed useful work with 222 tracked deletions, 22 corrupted
architecture documents, a smaller test suite, and one unresolved corpus outcome, so it could not
show that the cutover preserved the product. Nothing from it is authority.

- **Plan of record:** `.project/active/cutover-recovery/plan.md` **[OWNER 2026-08-10 approved]**.
  `.project/active/elaborator-cutover/` is retained as shaping and census evidence only, and its
  plan carries a superseded banner.
- **Phases 1–3 DONE.** The incident is preserved, the rebuild started from the certified Item 6
  baseline, and the exact route now serves the public CLI. The pre-retirement checkpoint is
  codegen `800ec84` with companion `cc6c7a7`.
- **[OWNER 2026-08-11] Disposition: REVISE.** The candidate is a credible pre-retirement
  checkpoint, not a completed Item 7. The prescribed path is
  `.project/active/cutover-recovery/owner-disposition-20260811.md`: v6 batch accepted (done),
  implement the seven formerly-gated migrations, all-route mutation tests, R8/R10, retirement
  with no provisional trim, full gates + audit on the retired tree, one regenerated candidate
  record. The R8, ruff, audit-F4, and related questions open at that checkpoint are now
  dispositioned by **[AGENT] (ratified for execution by owner, 2026-08-12)** in the current
  correction record.
- **Phase 4 PARTIAL.** The retirement runbook is prepared, but owner-gated deletion of v5,
  legacy builders, dual-run code, test shims, and wrong-oracle tests has not run.
- **Phase 5 AUDITED — NEEDS WORK.** The independent audit is
  `.project/active/cutover-recovery/audit.md`; its product-lens ledger is
  `.project/active/cutover-recovery/product-lens.md`. Only the instance-graph snapshot success
  criterion was certified.
- **[AGENT] Blocking findings.** Companion validation still suppresses the owner-forbidden true
  self-binding diagnostic when an outer same-named feature exists. The duplicate legacy authority
  and CLI-shaped test shim remain executable. Public live/relocated mutation and generated-byte
  parity evidence also remain incomplete. These findings block certification even though the
  current suites are green.
- **Fresh audit gates:** codegen **3862 passed / 47 skipped / 53 deselected**; companion **1825
  passed / 1 skipped / 5 deselected**; real TEAx lane **53 passed**. `ruff check src` still reports
  16 findings, and mypy remains at the recorded 69-error baseline.
- **Next (as of 2026-08-11, now done):** revise-path steps 2–7. See the 2026-08-12 entry above
  for the executed state; the gate numbers in this entry are pre-retirement and stale.
- **Environment:** one task-specific venv at `/home/reid/1cfe/item7-rebuild-venv`. Re-assert
  resolved import paths after any rebuild of it — uv's global cache silently produced an editable
  install pointing at the original worktree (finding F2).

---

### 2026-08-07: ELABORATE-FIRST epic ratified — Item 1 (forensic freeze + transition) DONE

**[OWNER 2026-08-07]** ruling: the string-resolution architecture itself is the defect home.
`in R = R` is a modeling bug to reject, referents must be consumed at load time, and snapshots are
a format choice. Direction ratified: replace the front end with elaborate-then-project (instance
graph as the single IR and snapshot payload; projection onto the existing `ComputationGraph` seam;
the ~3,450-line string-compensation machinery deleted at cutover, not wrapped).

- Plan of record: `.project/backlog/epic_elaborate_first_architecture.md` (8 items,
  spike/learning-test-first so failures are cheap; Item-3 elaborator spike is the go/no-go).
- Direction evidence: `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`
  (diagnosis, deletion inventory, seam verification, 7-shape pressure test, SysIDE capability
  survey) alongside the recovery assessment below.
- SOURCE-IDENTITY epic amended: Items 4–5 superseded, Items 1–3 inherited as semantic authority
  (29-cell matrix unchanged), Items 6–8 absorbed into ELABORATE-FIRST Items 7–8.
- Item 1 executed: dirty trees frozen on `item4-phases12-forensic` (codegen `69eef3b`,
  agentic-mbse `9724f1d`; agentic-mbse `main` clean again); working branch `source-identity-epic`
  is clean at `224bfa6` plus plan-of-record docs. The Item-4 plan carries a do-not-resume banner.
- **Item 2 (salvage landing) DONE 2026-08-07**: codegen `66a61f3` + agentic-mbse `65a35d7` (on
  `elaborate-first-salvage` — merge decision with owner; codegen's editable install reads that
  working tree, so keep it checked out there until merged). Landed: `ResolvedTargetFact` + the
  5-tuple `feature_chain_facts` with both aggregation callers fixed, `source_evidence.py`
  (evidence types + the three extraction-detectable readiness codes moved out of the retired
  module), evidence capture in `usage_extractor`, chain-evidence threading through aggregation
  terms, `PartInstanceIndex` exact reverse queries with `redefining_target_on` made
  query-order-independent, four fixtures, and the falsifier tests. Not salvaged:
  `analysis/source_identity.py` manifest/authority/recorder and its API tests. Gates: codegen
  3153/47/18 licensed (zero license-skip lines), ruff clean, mypy 72-baseline, baselines
  byte-identical; agentic-mbse 1811/1/33.
- **Item 3 (elaborator spike) EXECUTED 2026-08-07 — assumption CONFIRMED, no kill criterion
  triggered.** Findings: `.project/active/elaborator-spike/findings.md`. 381-line prototype:
  C25 collapse to one input proven in real generated YAML; C8 twins distinct; C24 producer edge;
  **C19 80.0 applied on both calc and constraint paths** (def-context remap rule); fusion_tea
  `in gain = gain` → hard SI_SELF_BINDING; Bank sum terms on `cell[i]` nodes; stable node IDs;
  generation layer accepted the projected graph unchanged. Discovery for Item-4 design: the
  legacy extractor leaves def-nested-usage calcs definition-relative (`owner_def=None`).
- **Owner GO recorded 2026-08-07** ("hell yeah. clean this fucker up."). **Item 4 design pair
  landed same day**: `.project/active/elaborator-design/{spec,design}.md` — AST-walked consumer
  population (extractor-consuming shortcut rejected, D10), one def-context remap rule (C19 fix),
  innermost-wins value tiers driving EP classification, computed nodes for EXPRESSION
  redefinitions, constraint lowering adapted to node edges, deletion ledger attached. The
  multi-occurrence-default question is answered by the contract's ratified 2026-08-05 rule
  (distinct occurrences = distinct sources) — cited, not re-asked.
- **Item 5 (exact-identity elaborator breadth) CERTIFIED and CLOSED 2026-08-09** — archived to
  `.project/completed/20260809_elaborator-breadth/` (plan, diff-ledger, product-lens ledger, and
  all audit rounds; certification is the `audit_v3.md` addendum; CHANGELOG carries the summary).
  The exact-ID route covers all 29 contract cells with public/named-diagnostic evidence, the
  37-fixture dual-run ledger is live-run-verified (26 collapse / 11 fix / zero unresolved), and
  invalid inherited/owned part conflicts block `SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before
  occurrence expansion. Open non-blocking residues carried forward: audit-F30 (AST guard covers
  only `_resolve_leaf`), audit-F31 (plural-fallback reachability fixture unauthored), the leg-4
  computed-attr `:>>` literal question, and attribute-level namespace conflicts not promoted
  (surface at projection collision instead). **Next: Item 6 exact-identity completion; F30/F31
  move there. Atomic cutover is Item 7; F26 legacy-oracle deletion and F19 customer-scale proof
  remain cutover obligations.**

- **Item 6 (exact-identity completion) CERTIFIED and CLOSED 2026-08-10** — archived to
  `.project/completed/20260810_elaborator-identity-completion/` (spec, design authority map, plan,
  three audit rounds, product-lens ledger; certification is the `audit_v3.md` re-audit addendum;
  CHANGELOG carries the summary). Calculation payload/compilation/formals/outputs and constraint
  usage decisions attach by exact UUID; SysIDE's native `Usage.usages` feeds exact concrete
  occurrences (F31 closed with a scoped witness); the graph carries structured occurrences, typed
  IR, formal provenance, and closed eligibility/compilability; projection is one-way with semantic
  collision guards; profile `BLOCK` halts by `SI_CONSTRAINT_BLOCKED` on strict, lenient, and
  round-tripped routes; the F30 guard is deny-by-default over all six boundary files with five
  named exercised exemptions. Nine audit findings (F1–F9) across three rounds all verified fixed.
  Shipped legacy route, snapshot v5, neutral facts, and generated baselines stayed byte-frozen.
  Open non-blocking residue: `_constraint_module_type` public-spelling collision guard (rendering
  policy). Coordinated agentic-mbse half (identified constraint extraction/evaluator) lives on
  `elaborate-first-salvage`. **Next: Item 7 atomic cutover (unblocked). Item 7's deletion ledger
  now also names the four Item-6 transitional duals; F26 legacy-oracle deletion and F19
  customer-scale proof remain cutover obligations.**

### 2026-08-07: SOURCE-IDENTITY Item 4 — SUPERSEDED (archived 2026-08-10)

The Item-4 shadow-layer architecture (identity manifest beside the legacy resolver that ignored
it by design) was stopped after Phases 1–2. The audit's owner-grade product lens was BLOCKED on
C24 and the phases were never certified; the recovery assessment
(`.project/research/20260807-143615_source-identity-recovery-assessment.md`) led to the owner
ratifying the elaborate-first replacement — the "major pivot" the ELABORATE-FIRST epic executes.
Artifacts (spec, design, plan, audit, reviews, product-lens) are archived with superseded
markers at `.project/completed/20260810_source-identity-occurrence-foundation/`; the epic is
archived at `.project/completed/20260810_epic_semantic_source_identity.md` (supersession record
inside). The stopped implementation is preserved on `item4-phases12-forensic` (codegen
`69eef3b`, agentic-mbse `9724f1d`); the salvage subset landed via ELABORATE-FIRST Item 2.
Items 1–3 remain the inherited semantic authority (entries below).

### 2026-08-07: SOURCE-IDENTITY Item 3 — COMPLETE

Audit: `.project/active/source-identity-contract/audit.md` (2026-08-07, **Certify**). The owner
declared the audited item finished on 2026-08-07, closing the final ratification checkpoint without
changing provenance grades. All findings and final recheck findings were corrected the same day;
full record in `design.md` A.8 + plan Correction Pass:

- **audit-F1 resolved by citation** (`product-lens.md` correction entry): computed-source cell
  **C24** (1 calc + 1 constraint + 1 agg through one producer channel; no minted public input)
  published under an explicit D8 reopening.
- **Customer context corrected**: mixed, not all usage-authored — `meier_coe_calc` usage-authored
  (`hif_plant.sysml:205,215`); `lcoe_calc`/`recirc_calc` def-authored
  (`generic_ife/ife_plant.sysml:98,114,126,134,148`). 01b re-derived; exact supported-form cell
  **C25** owns availability's one usage-authored + one definition-authored consumer, while C2 owns
  thermal-efficiency's two definition-authored consumers. C4 remains DCS referent evidence.
  The exact topology split below moves the reopened counts to **29 cells / 35 coordinates**;
  `epic:147-150` citations fixed.
- **Aggregation topology corrected**: C17 now owns producer-backed
  `permitting.capital_cost` (one producer channel, zero public inputs); C26 owns the three
  literal-valued modeled `permitting` cost features (one public input per source). The committed
  graph proves C17's producer wiring, while current parity evidence contradicts C26's target.
  C24 now names one direct calculation-output declaration and 22a one exact kept expression binding.
- **SI-23 exactness**: C7/C8/C9/C10/C15/C16/01g/C11–C13 keys now carry exact occurrence counts,
  value states, and consumer counts/types (checker rejects parametric key values).
- **SC4**: REQ-BT-13/IR-01 `PARTIAL`, REQ-PGD-06/VBR-03 `SUPERSEDED` annotated (11 total);
  Status projection still byte-identical.
- **Authority state reconciled**: contract Current conclusion is the single authority-state
  statement (source-identity material ratified; runtime certification remains assigned to Items
  4–8); stale closed-epic handoff removed; matrix legend/spec/design/epic handoffs aligned. VBR stamp citation fixed to
  `orchestration/pipeline_builder.py:363-369`.

Gates after corrections: all four phase checkers GREEN (29/35, exact keys, 11 annotations,
projection byte-identical), archive SHA unchanged, `git diff --check` clean, 11/11 route tests.
**Next: Item 4 specification.**

Plan: `.project/active/source-identity-contract/plan.md` (per-phase completion notes + the Item
4/5 derivability dry-run live there). Landed in the lifecycle contract
(`constraint-execution-authoritative-lifecycle-contract.md`): the "Source identity" subsection
(definitions, form × context referent table, invariants 54–60, validation/guidance obligations
with the exact owner payloads — SI-01 quote at D-4, SI-15/16 request, SI-18 quote with the
preserved "quesiton" typo); dispositions D-4..D-19 with the resolved checkpoint record; invariants
19/20/22/26 amended in place; six new Appendix B correction rows; Appendix C "Source-identity
scenarios" — originally 26 cells / 32 evidence coordinates, reopened by the audit correction to
29/35, no PENDING_CHECKPOINT, every BLOCKED cell with a published target key; status reconciled to
the 41/41 + 2026-07-20 merged state. New durable
companion `.project/concepts/constraint-execution-lifecycle-requirements.md` (copy-and-freeze;
25 graded LC-SI projections; archive byte-identical, SHA pinned in the plan; contract
Requirements pointer moved). Verification matrix: 7 row-local contract-disposition annotations +
1 legend line; Status projection/Summary/Index byte-identical. Epic Item 3 + spec footer
reconciled. All four phase checkers GREEN (scratchpad `phase{1..4}_check.py`); 11 route tests
pass; no code/fixture/snapshot/completed changes. Those mechanical results do not clear the audit
findings above.

### 2026-08-05: SOURCE-IDENTITY Item 3 — authoritative contract spec DRAFT

Spec: `.project/active/source-identity-contract/spec.md`. Owner ruling: never reinterpret a
self-binding as an outer reference. The contract supports owner-qualified references and
occurrence-rooted feature chains under their distinct SysIDE/KerML meanings, classifies indexed
value expressions as unsupported for source-bearing calculation bindings, and absorbs aggregation
consumers into the same identity family. Required downstream work includes correcting the existing
`agentic-mbse` L2 self-binding validator, which currently suppresses its error when a same-named
outer feature exists; adding a distinct indexed-expression readiness diagnostic; keeping codegen
independently fail-closed; and publishing allowable modeling patterns in `agentic-mbse` docs.
Post-review revision now explicitly supports the bare-renamed definition-reference form, requires
matrix evidence coordinates, and records the ratified rule that equal inherited defaults on
distinct concrete occurrences remain distinct sources unless the model explicitly shares them.

Design is at rev 5 (`design.md`) after four Revise reviews; the authority architecture (amend the
lifecycle contract, no new normative doc) and the three-field/boundary-outcome schema are confirmed
sound. Rev 5 repaired the v4 findings with a key semantic discovery, verified against fixtures:
**binding-owner context changes the referent of the same written form** — the AFT probes author
calcs inside the PartDef (def-level referent) while deep_cross_scope and the customer bindings sit
inside concrete usages (occurrence-level referent, snapshot-verified). Semantic referent is now key
material (referent table A.2); supported families dissolved into per-form cells; RM13 reclassified
as a broken positive resolution (solar's `permitting` features are modeled), so the terminal-miss
cell is BLOCKED on a constructed fixture; blocked cells publish full target coordinates (D8) so
Item 4 realizes fixtures, never chooses semantics. The owner then agreed to all eight checkpoint
recommendations (`[OWNER-VERBATIM]` “ok agreed with each one”). Their substance remains `[AGENT]`
(ratified by owner, 2026-08-05): keep the decisions and matrix in the lifecycle contract; create a
copy-and-freeze companion requirements artifact while leaving the archived spec untouched; model
one independently overridable `LIBRARY_DEFAULT` per concrete calculation usage; defer expression
source support while failing closed with a readiness diagnostic; assign blocked fixtures to Item
4; file the aggregation finding into this epic; reconcile stale project status; and migrate the
customer binding bare-renamed-in-place. The then-current enumeration was 26 cells / 32 evidence
coordinates with no pending checkpoint classes; the audit later corrected the exact customer home
to C25/C2 and reopened the population to 28/34; the later C17/C26 exact-topology split produces
29/35. Next: see the current Item-3 audit-correction entry
above.

### 2026-08-05: SOURCE-IDENTITY Item 2 — COMPLETE

Dedicated branch `source-identity-epic` was created from `nested-override-tripwire` at `fa9e0d0`
after the Item-1/Item-2 evidence legs. Source-identity work continues there.

Executed via `/_my_learning_test` (kept tests + findings; item's spec/design/plan skipped —
noted in findings). Kept tests: `tests/conformance/test_source_identity_routes.py`
(11 passing, license-free) — pin both fan-out paths, the authored-vs-reference-derived
literal discriminator (`written_reference is None` ⇔ authored), and the cross-owner cell
(solar `pack_count`) where owner-local reconstruction fails. Findings + identity trace +
initial census + evidence-sufficiency verdict + adjacent-work register:
`.project/research/20260805-054752_source-identity-route-evidence.md` (back-referenced in
the epic's Item 2 Current State; Item-1 results cross-referenced).

New load-bearing facts beyond the forensics: snapshot capture persists the post-VBR stamp
(`snapshot/capture.py` runs the full pipeline; `graph_rebuild.py` has no VBR step — any
evidence repair ⇒ recapture + rebuild change); written-form fields survive the stamp; a
fourth value authority (group-deriver backfill, `graph_builder.py:620-630`) masks Path-B
identity loss. Census: 277 corpus entry points, 75 model-derived per-consumer mints
(37 Path A / 38 Path B). Joint synthesis with Item 1 makes the evidence-sufficiency verdict
final: extraction must publish a semantic source ID from referent/redefinition evidence;
owner-local reconstruction cannot cover 40/75 cross-owner/tail cases, and the surviving
self-reference `source_path` is normatively the wrong element. Licensed live, snapshot, and
relocated routes are identical on four representative fixtures; retained matrix/trace/parity
artifacts live in `.project/active/source-identity-route-evidence-spike/`. All six Item-2 criteria
are met. The queued aggregation-scoping finding is classified in the adjacent-work register and its
absorption into the same terminal-mint family was ratified at the Item-3 checkpoint.

### 2026-08-05: SOURCE-IDENTITY epic Item 1 — binding-semantics spike COMPLETE

Executed via `/_my_spike` (probes + findings + table; item's spec/design/plan
deliverables consciously skipped — noted in findings). Home:
`.project/active/source-identity-binding-semantics-spike/`. Headlines: bare
`in R = R` self-binding is normatively required (clause-cited KerML/SysML rulings
retained in `standards/`); qualified vs chain forms denote def-level vs
occurrence-level features and the spec doesn't pick one (Item-3 decision); `#(i)`
parses value-only and the extractor silently drops the index segment (NEW
identity-loss site → Item 2 route matrix); `[i]` fails to load; both indexed forms
have zero corpus prevalence; bare self-named is ~47% of external usage bindings.
Decision input for Item 3: `authoring-form-table.md`. Item 2 (route/evidence spike)
completed the other pre-disposition leg.

### 2026-08-03: Entry-surface fan-out forensics — COMPLETE, filing + rulings pending

A customer (fusion-tea demo) found that calc-usage self-named rebindings (`in R = R` on a
shared plant attribute) fan out into per-usage entry fields; sweeping one copy leaves the
others frozen. Forensic report:
`.project/research/20260803-203011_entry-surface-fanout-forensics.md`.

- **Verdict: NEVER-BUILT and never specified** (per-usage minting is REQ-IR-06, present
  since the initial commit; the two big refactor PRs were byte-identity preservation and
  pinned the fan-out into baselines). Not a regression.
- Mechanism: SysIDE resolves the bare RHS to the calc's own param (spec-conformant — the
  idiom is degenerate per KerML scoping); Path A (instance `:>>` override literal-stamped
  per-usage by name coincidence, `src/sysml_codegen/orchestration/pipeline_builder.py:363-369`)
  is fully silent; Path B
  (def-default, lenient-miss) warns. Constraints converge — hence the asymmetry.
- **Resolved 2026-08-05:** never reinterpret the self-binding as an outer reference; honor
  SysIDE/KerML referents, support qualified and chain forms under their actual meanings, and absorb
  aggregation consumers into the same source-identity contract.
- **Still pending:** filing this + the remaining queued Fusion Tea upstream findings; fix-first vs
  workaround for demo Item 5; and whether anything consumed LCOE off the July IFE study rows.

### Post-merge state — CONSTRAINT-LIFECYCLE epic MERGED and CLOSED (2026-07-20)

The constraint-execution lifecycle wave is merged, in the load-bearing order:

- agentic-mbse PR #11 → main `f4ebdce` (merged FIRST)
- sysml-codegen PR #9 → main `936315c`
- teax PR #3 → main `fa0e06a`

All three repos are back on `main` and pulled. Post-merge smoke on codegen main:
**3115 passed / 47 skipped, zero `no live syside license` skip lines** (the skip-line check is
the only valid license proof; pass/skip counts do not discriminate).

Epic archived: `.project/completed/20260720_epic_constraint_execution_lifecycle_remediation.md`
plus all 15 item folders (`20260720_constraint-lifecycle-*`, `20260720_constraint-execution-lifecycle-contract`).
The superseded PR-wave epic is archived alongside
(`20260720_epic_constraint_pr_wave_remediation.md`). Key records, post-archive:

- Release record: `.project/completed/20260720_constraint-lifecycle-composed-proof/release-readiness.md`
- 41/41 register: `.project/completed/20260720_constraint-lifecycle-composed-proof/evidence-coordinate-register.md`
- Ratified authority (unchanged home): `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`

### Unmerged branch: TEAx `constraint-semantics-item3` (CONSTRAINT-SEMANTICS Item 3, closed 2026-08-13)

`/home/reid/1cfe/teax`, branch `constraint-semantics-item3` at `5b70ae9` — four commits off pinned
`main` `fa0e06a`, complete, **not merged**, nothing pushed. Item 3 closed in codegen bookkeeping
with this branch as a named deliverable; merge sequencing belongs to `pre_pr` and the owner.

- **Do not switch the TEAx checkout off this branch until merge.** codegen's execution lane imports
  simkit from that working tree (D8's checkout inversion), so switching breaks codegen's own suite.
- **Publication order is codegen first, TEAx second.** The reverse makes TEAx accept a runtime
  contract no generator produces.
- Item 2's hand-off is **discharged on this branch**: the accepted schema sets were re-vendored —
  replaced, not extended — so a pre-item package fails at seal verification before any report is
  read.

### 20260724 branches (both items CLOSED 2026-07-24; merged 2026-08-14 inside codegen#10)

- **`docs-lifecycle-sync`** — docs + `.project/` only. Item archived to
  `completed/20260724_docs-lifecycle-sync/` (audit: no open findings).
- **`nested-override-tripwire`** (stacked on it) — the only `src/` change. Item archived to
  `completed/20260724_nested-override-tripwire/`.

Both were verified ancestors of `item7-rebuild` and landed with the phase-D squash merge;
nothing separate remains to merge.

### pipeline_explainer_v2.html — BUILT (2026-07-24, `[V2-HTML-BUILD]`)

`.project/diagrams/pipeline_explainer_v2.html` (144KB, uncommitted on `docs-lifecycle-sync`)
built from the re-anchored `EXPLAINER_PROMPT.md`. Self-contained vanilla HTML/SVG/JS,
light/dark themed, L0–L4 progressive disclosure; interactive stage strip + module_kind-coloured
solar-battery mini-DAG (13 real modules from the committed baseline YAML); all snippets verbatim
from committed fixtures except the `attribute :>>` trap counter-example, which is a labeled
minimal adaptation of `spec_chain_channel` (no committed fixture encodes that form — noted in
the page). Every cited symbol grep-verified against src/ at merged main; §7 caveats preserved
as hedged; Gen-1 explainer untouched. Not yet visually smoke-tested in a browser (no browser in
this session) — open the file once before sharing.

### Open decisions — owner rulings recorded 2026-07-24

1. **fusion-tea + stellarator local branches — HOLD [OWNER 2026-07-24].** Stay local until
   the owner says otherwise. Epic evidence pinned at immutable `342cc799`/`c2f10960`; the
   stellarator tip moves from EXTERNAL processes — check `git log origin/<branch>..HEAD`
   before touching.
2. **Local `constraint-exec-epic` branches — DELETED [OWNER 2026-07-24]** in all three merged
   repos (teax needed `-D`: PR #3 was squash-merged; tree verified byte-identical to main
   before deletion).
3. **Stale-baseline class — LEAVE FILED [OWNER 2026-07-24]**, now a proper backlog entry:
   `[STALE-BASELINE-CLASS]` (P3, no assignee).
4. **`[NESTED-OCCURRENCE-OVERRIDE]`** (BACKLOG P2) — **tripwire SHIPPED [OWNER 2026-07-24]**
   on branch `nested-override-tripwire` (stacked on docs-lifecycle-sync): the calc path's
   silent value loss now warns, naming captured vs demanded scopes
   (`supplied_values.py` `_unmatched_override_scopes` + drain; probe-first, 0 false fires
   across all 19 snapshot fixtures — `completed/20260724_nested-override-tripwire/probes/verdict.md`;
   suite 3118/47, ruff clean, byte-identical outputs). The full occurrence→definition-bridge
   fix is now an explicit filed-fix block in the `[NESTED-OCCURRENCE-OVERRIDE]` BACKLOG entry
   (scope, acceptance, blast radius, sequencing vs `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2);
   scheduling still open.
5. **Item-10 completeness-check MODULE_OUTPUT exemption — MOOT: already closed in code.**
   Surfaced at the 2026-07-24 ruling pass: audit Major 1 (`b987869`, pre-merge) removed the
   exemption — the check flags name-based key forms regardless of outcome
   (`producer_completeness.py:141`, pinned by
   `test_qualified_channel_tier_leaf_guess_is_flagged`). The "ruling pending" note in the
   archived epic lessons/handoff was stale. The check remains a diagnostic, not a hard
   generation gate — that part is unchanged and by design.
6. **teax remote is SSH** (`git@github.com:rwestwood89/teax.git`) but sessions have no SSH key —
   pulls/pushes need explicit HTTPS URLs. Consider switching the remote to HTTPS. (Still open.)
7. **Archive stragglers in `active/`** — item dirs from already-closed epics remain; need a
   mapping pass first (several are referenced by live BACKLOG entries, e.g.
   `matrix-truth/probes/`, `hygiene-tail/probes/`). (Still open.)

Also ticketed 2026-07-24: `[MATRIX-EPIC-SURFACE-ROWS]` (P3) — the three uncovered lifecycle
surfaces as matrix-row candidates.

### Pre-existing accepted baselines (unchanged)

- `ruff format --check src` fails on 22 files and `mypy src` has 72 errors — accepted baselines;
  the maintained gates are `ruff check` clean + mypy-zero-new.
- Two `-O` failures in `test_expression_compiler` are pre-existing (assert-stripped).
- **`tests/runtime/…::test_the_lane_runs_the_real_simkit` fails on a whole-set run and passes in
  isolation** — a collection-order artifact, reproduced at the parent commit and therefore
  pre-existing. Surfaced (and re-confirmed) by CONSTRAINT-SEMANTICS Item 3, which touched neither
  `tests/runtime/` nor the guard; `tests/execution` alone is green. Recorded here so it is not
  rediscovered as a regression. **Still needs an owner** — no item has claimed it.
- The two known stale-baseline classes (`deep_cross_scope`, `plant_values`) remain pre-existing,
  untouched, and still need an owner.

---

## Recently Completed

### 2026-08-16: self-binding-replacement — CLOSED WITH OWNER-ACCEPTED RISK

- Self-named calculation bindings now refuse before generation; the situational D-5/D-6/D-7 guidance, Fusion Tea D-5 migration, agentic validation, and definition-owned lineage-miss refusal are delivered.
- Independent audit verified all ten functional criteria and the Product-Lens gate is CLEAR. **[OWNER 2026-08-16]** The remaining dangling-symlink behavior in the migration/fixture helper is a testing/developer-tooling edge case and accepted risk; closure was directed without another remediation cycle.
- Archived to `.project/completed/20260816_self-binding-replacement/`; the audit evidence and unchecked accepted-risk plan boxes remain in the archive.

### 2026-08-16: qualified-reference-occurrence-anchoring — CERTIFIED AND CLOSED

- The shared one-segment resolver now honors the exact `PartUsage` owner before selecting the leaf
  slot. The cross-owner silent wrong-edge case is gone, and missing/ambiguous exact-owner states
  refuse by name instead of falling back to consumer position.
- Final audit verdict: **Certify**. Findings 1, 2, 4, 5, and 6 are closed; the arrayed aggregation
  split is owner-disposed to `[ANCHORING-ARRAYED-DIAGNOSTIC]`; historical companion-revision
  provenance remains an explicit nonblocking residual. Product lens: **DISPOSED (passing)**, no
  BLOCK. Focused licensed suite: **116 passed**.
- Evidence: 20 changed outcomes adjudicated, 139 identity blocks unchanged, 0 structural problems;
  bounded census 154 roots / 770 observed calls / 0 observed absent leaves / 15 residual roots.
  Archived to `.project/completed/20260816_qualified-reference-occurrence-anchoring/`; P-002 keeps
  the product promise and evidence bounds live.

### 2026-08-14: CONSTRAINT-SEMANTICS EPIC — Constraint Semantics and Design-Search Feasibility (all nine items closed; epic closed + archived)
- **The measured failure the epic was filed against is closed.** CATF authored 65 constraint usages
  and produced 9 visible dispositions and **0 executed checks**. It now produces 65/65 dispositions
  on the frozen witness and a derivative that closes `65 = 56 carriers + 9 named deletions` with
  **three executing physics gates** and `{eligible 3, excluded 0, non_reaching 53}` — no
  instance-reaching gate outside the coverage denominator. Reports and TEAx distinguish six states
  instead of two, `all_satisfied` is gone as a token, and a missing disposition halts generation.
- **The epic's founding failure mode was demonstrated by its own proof item.** The first execution
  of these gates rejected CATF's **authored** design point on physics (cryo load 8396.05 MW vs
  1546.72 MW gross) — a defect invisible for the model's whole life, because a model that executes
  zero gates reports `not_assessed` and nothing ever contradicts it. Filed
  `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` (P1).
- **Ten Success Criteria ticked against their amended forms**, with each amendment named under its
  box and its ruling dated — the SC-3 accounting identity, D-S1/D-S2 (A5/A6/A9 held, then EXECUTED
  by Item 9), finding 6-D (the authored point *is* the reject candidate), and the scope-4 LC-E10
  wording. The Evidence-Invalidation Register is **HANDED to the cutover resumption**, not
  discharged: its record is complete, phase B step 1 walks it row by row.
- **Lessons Learned written for real** from the nine close records — the 6-D story, the two unearned
  checkboxes and the probe-don't-trust discipline that caught them, stop-and-surface working three
  times, the O-1 cross-repo invariant narrowing, the orchestration-mechanics traps (`uv run`
  interpreter, resume permission-mode drop, archival-breaks-readers, characterizations-first), and
  honest cost accounting: planned 8.5–9.5 days over 6 items, delivered 9 items at 10–12, with two
  of the three additions born from findings the shaping stage could not have known.
- **`pre_pr` deferred to phase D by ruling; nothing pushed; no `main` touched.** Archived to
  `.project/completed/20260814_epic_constraint_semantics_contract.md` with the umbrella shaping
  folder preserved at `.project/completed/20260814_constraint-semantics-contract/`. Post-move
  collect check `2104/2183 (79 deselected)`, no collection errors.

### 2026-08-14: CONSTRAINT-SEMANTICS Item 7 — ADR, Product Promise, and Agent-Facing Documentation Sync (audited Certify-with-residuals + closed)
- **The owner's promise finally has a durable home, and the trail to it survives archiving.**
  `.project/product/INDEX.md` → `P-001-design-search-free-variation.md` carries the
  `[OWNER-VERBATIM, 2026-08-13]` design-search promise byte-for-byte (payload diff empty), with the
  epic's `[OWNER]` Critical Success Factor beside it, ADR-009 back-registered as a row under this
  repo's ADR convention, and the promise-vs-basis tension surfaced rather than resolved
  (`[ACAUSAL-RELATIONS-CAPABILITY]` names the unbuilt half). The durable citation lives in the epic
  file's Product-Lens header and in `CLAUDE.md`, both outside the archived folder. Closes Item 3
  `audit-F4`, which had no home available when it was filed.
- **The teaching surfaces in three repositories now match what shipped.** `@inapplicable:`
  authoring and the eligible+inapplicable refusal, the disposition vocabulary and severity-by-cause,
  the six report states and the TEAx feed-strategy opt-in, the `modeling-assumptions.md` §8
  unit-on-binding rewrite Item 8's behavior change required, and the corrected `sysml-conventions`
  skill example. The B1–B5 marker rule is stated with **both** its conditions: a marker on a
  bindings-form constraint reaches the domain (proved by a licensed elaboration probe), and on an
  inline-predicate constraint SysIDE drops it silently, so PROVENANCE carries the disposition until
  `[INLINE-PREDICATE-MARKER-DROP]` closes.
- **The audit's own probe caught the one defect the item introduced, and it was fixed rather than
  argued.** A-3: the new `@inapplicable:` "How to write it" example was refused by the shipped
  generator under the same document's D9 rule. An implement resume took route (a) and the auditor
  re-ran it end to end — the authored text generates, seals, and carries the marker's reason into
  the catalog. A-4 (an unreproducible kept-test-file count) closed with its method recorded and 55
  reproduced independently.
- **Two residuals carried past close, both owner calls** — the codegen `.claude/` symlink target
  (resolves on merge) and `[CONSTRAINT-GATES-UNTAGGED]` (REQ tags must be minted before Items
  3/5/8/9 get matrix rows). Gates: licensed **2070 passed**, zero license-skip lines; `git diff
  --check` clean in three repos; collect `2104/2183 (79 deselected)` after archiving. No code,
  fixture, schema, or generated path in any item commit. Archived to
  `.project/completed/20260814_constraint-docs-agent-sync/`.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 9 — Derivative Upgrade Under Held Intent (audited Certify-with-residuals + closed)
- **The worked example is now the shape the owner ruled, not the shape a defect allowed.** Three
  rows moved: A5 and A6's 27 radius derivations were authored on the ruled basis (axis root radius
  + 14 thicknesses free) and their asserting usages deleted; A9 asserts `ProductWithinBand` at the
  ruled 1% relative band. The disposition histogram is `{eligible 3, excluded 0, non_reaching 53}`,
  so **no instance-reaching physics gate sits outside the coverage denominator** — which discharges
  the epic-level lens obligation Item 5's close carried against this item. Nothing was
  re-dispositioned; the item executed held intent.
- **Every accounting number is a mechanical consequence, and the audit proved it that way.**
  `65 = 56 carriers + 9 named deletions` (53 by name, 3 by `renamed_from:`) is machine-proved by
  `scripts/check_gated_manifest.py --check`, and the audit re-derived it from the ruled table
  without reading a run. SC-6 order holds: expectations landed at `185dec7` and are byte-unchanged
  through HEAD. Licensed suite **2070 passed / 34 skipped / 0 failed**, zero license-skip lines;
  ruff and mypy zero-new; the frozen twins and the archived owner ruling are byte-identical by tree
  hash.
- **The deletion gate is per-occurrence now.** Each of the 27 derivations must resolve to its own
  declaration and comment block — five occurrence-scoped mutations on a scratch fixture each
  produced a reported problem naming the layer, never a skip and never a sibling-satisfied pass.
  That closes the A-1 gap (two bare initializers past four gates) per occurrence rather than per
  row.
- **Three things surfaced rather than absorbed**, all on the live surface (`PROVENANCE.md`), not
  only in the archiving design: the D3 `tf_coil.thickness` comment amendment (the one edit outside
  the ruled 27, ratified); the per-dimension cost of `ProductWithinBand` (a constraint formal's
  port unit comes from its own declaration, so a generic band cannot carry a unit) filed unowned as
  `[CONSTRAINT-FORM-PER-DIMENSION-COST]`; and a one-ULP float drift on four layers' derived
  `outer_radius` (−8.88e-16 m), visible only under the `execution` marker, which is deselected by
  default and was not run.
- **The epic's third Item 9 criterion stays unticked by owner ruling** — retiring the B1–B5
  PROVENANCE workaround is a conditional on `[INLINE-PREDICATE-MARKER-DROP]`, which has not closed,
  so it never fired. Recorded on both sides (fixture `PROVENANCE.md` §3b and the amended BACKLOG
  entry). Residuals R1 (a wrong stencil count, 58 → 34) cured at `d713f21`; R2/R3 disposed at
  close; R4/R5 recorded as forward-looking notes for the next item touching this fixture or prover.
  Archived to `.project/completed/20260813_derivative-upgrade-held-intent/`.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 6 — Calculation-Definition Gate Capability Design (audited Certify + closed)
- **A design/planning delivery, not a capability.** An executable probe attached one
  calculation-definition constraint across zero, one, and two calculation occurrences by exact
  identity — matching the constraint owner's `DeclarationId` to `CalcNode.calculation_definition_id`
  — and recovered resolved attributes, literals, and modeled defaults with no rendered-name lookup.
  It also proved that two sibling uses of one definition collide on the current constraint key, so
  concrete identity must carry the calculation node. The repeated-use gap was closed inside the v4
  wire grammar, with no second authority. Spec, revised design, three-round independent review, and
  a file-level implementation item followed; all six epic criteria are ticked. Archived to
  `.project/completed/20260813_calcdef-constraint-gate-design/`.
- **The implementation is ruled out of this epic `[OWNER 2026-08-13]`.** The 7–9 day follow-on
  (graph v4 + catalog 4.0.0, codegen + TEAx) is filed as the named, unowned backlog entry
  `[CALCDEF-GATE-IMPLEMENTATION]`, with the archived `implementation-item.md` as its plan of
  record. Authorization is parked with the owner. The production-acceptance boxes in the archived
  spec stay open on purpose — they belong to that item.
- **Item 8's start gate is satisfied and recorded.** No lawful start SHA existed until Item 8's
  unit-lane characterizations landed; they landed at `62a07e5`, so the gate dissolves and only
  owner authorization remains. Three things ride along: the SC8 guard (the future v4 record
  re-derives its own tracked set, never reusing Item 8's 23 paths), the TEAx re-vendor consequence
  of catalog 4.0.0, and R5 joint delivery staying declined until a new owner ruling.
- **Bookkeeping done at this close:** the two `active/unit-lane-port-metadata/` citations in
  `design.md` and `implementation-item.md` were repointed to the archive before the move, and
  BACKLOG's CONSTRAINT-SEMANTICS list caught up on Items 1 and 4, which were closed and archived
  earlier but never ticked.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 8 — Unit-Lane Port Metadata Defect (audited Certify + closed)
- **The refusal is cured at its source.** Constraint-formal and computed-attribute entry-point
  ports now carry the same authored unit text calc-usage bindings always carried, so one design
  attribute read by a calc *and* a constraint (or a derivation) is one public entry point instead
  of a whole-model `SI_RENDERING_COLLISION` refusal. Both kept customer characterizations — the A9
  assert-band shape and the radius-derivation shape — are red against the parent tree and green at
  the freeze `62a07e5c870158672eb100f1cba73adfe4c9df28`, with exact authored text (`m³/s`,
  `Dimensionless`, `m`). Declaration identity owns unit selection: no inference, conversion, or
  normalization, and unequal metadata still refuses fail-closed.
- **Zero fixture churn — the conditional recapture never fired.** The complete Git-derived
  inventory assessed **23 tracked / 23 assessed / 0 stale / 0 missing / 0 extra / 0 duplicate**, so
  no v3 recapture was allowed or performed and no tracked snapshot or manifest byte moved. Three
  routes (licensed live, in-place v6, relocated v6) mint identical port metadata.
- **Gates and handoff.** Focused 244 passed; default licensed 2066/34/79; all-marker 2144/34/1
  (the one inherited collection-order failure, which passes in isolation); ruff and mypy zero-new.
  The Item 6 handoff is evidence-only: full freeze SHA, five proof-node IDs, both complete path
  sets, the zero-recapture disposition, and a guard forbidding any future graph-v4 record from
  reusing 23 or the 15-path subset instead of re-deriving its own tracked set. Shipped standalone
  as ruled; no residuals. Archived to `.project/completed/20260813_unit-lane-port-metadata/`.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 5 — CATF Derivative and End-to-End Acceptance (audited + cured + closed)
- **The contract ran end to end on the richest model in the tree.** `catf_mfe_gated` landed: 47
  modules, 58 usage rows, 2 executing gates (A2, A3), histogram `{eligible 2, excluded 3,
  non_reaching 53}`, coverage `58/2/2/0/0/{}/complete`. The accounting identity **65 = 58 carriers
  + 7 named deletions** (SC-3 amendment, owner-authorized) is machine-proved by
  `scripts/check_gated_manifest.py --check`, which now also ties each `derive-instead` deletion to
  its in-source derivation and chosen-basis statement. SC-6 proved by commit order (`1247a3b` →
  `7369b3e`), three named post-fixture expectation edits, each value-free.
- **The epic's founding failure mode was demonstrated and closed by the same item.** Finding 6-D:
  the first execution of these gates caught that the **authored** CATF design point is
  gate-infeasible under its own cryo model (8396.05 MW cryo load vs 1546.72 MW gross; `heat_leak =
  magnet_volume * 0.05` at `thermal_loads.sysml:59`). Reproduces on untouched `catf_mfe_d5`, which
  executes zero gates and so reported `not_assessed` for the model's whole life. Filed
  **[CATF-CRYO-HEAT-LEAK-COEFFICIENT]** P1. Ruled option (a) **[AGENT] ratified by owner**:
  candidates are labeled gate-feasible/infeasible under the model as authored; the authored point
  is the reject candidate, the raised-`p_fusion` leg is a machinery exemplar, not a design.
- Audited **Certify-with-residuals** (`2b490f8`) after two blocking PROVENANCE findings were cured
  (`995a058`, `1869c29`) and A-3 gated the shape that let A-1 through (`b083c47`). Residuals homed
  at close: A-4 → `[GOLDEN-BYPASSES-RUN-CODEGEN]`, A-5 → `[CATF-ACCEPTANCE-LANE-MANUAL]`, A-8 →
  epic Item 7's matrix reconciliation, A-7 recorded as accepted. Gates: licensed **2106 / 34 /
  1 known**, zero license-skip lines, ruff 12, mypy 55, frozen twins byte-untouched except d5's
  corrected PROVENANCE paragraph.
- Archived to `completed/20260813_catf-constraint-policy-acceptance/`. Epic Items 8 and 9 were
  filed out of this item's D-S1/D-S2 ruling; A5/A6/A9's held intent lives in the archived
  `owner-disposition.md` and is Item 9's input.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 4 — Predicate Defect Hardening (audited + cured + closed)
- Both Q8 must-fix predicate-boundary defects cured under the one existing unit-annotation rule,
  plus a fourth lane (`in tol = 0.05 [m];` bindings) found at spec and cured under the recorded
  same-rule test; a blocked chain now names the joined written chain, location, and bindings
  rewrite (companion `0a52942` + codegen render de-dup/order). End state pinned positively: an
  admitted, catalogued, assessed inequality gate.
- Audit Certify-with-residuals with all 7 requested probes run by the orchestrator (R6: deleting
  the cure fails exactly the 7 item-fixture tests, nothing else); all findings cured; F5 resolved
  **[OWNER 2026-08-13]** — the coverage ledger's durable home is `tests/unit/data/`.
- Two limits parked for Item 5 in the epic's Item 5 section: binding units are dimensionally
  inert to the profile; a blocked chain's location is the usage's line. Archived to
  `completed/20260813_constraint-predicate-hardening/`; gates 2010/34/0 licensed, ruff 12,
  mypy 55, companion 10 failures proven pre-existing.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 1 — Contract and Authoring Policy (audited + cured + closed)
- **Every durable authority a modeler or an implementing agent reads now teaches the settled
  rule.** Before this item, the ratified lifecycle contract, its frozen requirements companion,
  and seven documentation statements across both repositories still taught that a bare
  `constraint` or a `require constraint` is an enforced gate, and that any assessed pass means
  satisfaction. Now assert-only enforcement, the applicable-asserted-gate membership test, the
  inventory-versus-feasibility split, the six headline states and their precedence, and the
  warning tier for a vacuous asserted gate are published — with **ADR-009**
  (`docs/architecture/modeling-assumptions.md` §9) as the decision record, cited back into the
  umbrella product-lens trail. This was the documentation half of the owner's sequence (settle →
  fix docs → then test), and Items 2–4 built against it.
- **Nothing executable changed, and that boundary was verified by reading the diff, not by
  trusting the claim.** The only Python touched is a module docstring and two test-docstring/
  comment citations of a retired test. The four `all_satisfied` assertions that carry the
  superseded meaning were **handed to Item 3** rather than forced through.
- **Both deliberate hand-offs are now DISCHARGED** — recorded at close: Item 3's token migration
  corrected the four `all_satisfied` assertions (`full_satisfaction`, with `UnknownHeadlineToken`
  failing closed), and Item 2 landed REQ-EXT-09's replacement totality proof
  (`test_constraint_population_oracle.py` + 42 reviewed expected-population files) and performed
  the REQ-EXT-09/REQ-CL-04 re-grade Item 1 deliberately did not.
- Audited **Certify-with-residuals**; H-1, M-1 and M-2 cured in `76e3ab7`; all five requested live
  probes run and matched, including the licensed companion run. **M-3 dispositioned at close: the
  vendored-corpora aggregation is RATIFIED as final** — the 52 hits in the OMG spec, the standard
  library, and generated SysIDE API docs stay aggregated per corpus with every file named and one
  uniform out-of-class disposition; every project-authored hit is still one row each. Expanding to
  52 rows would add rows, not information.
- **The D5-a deviation stands and was judged sounder than the design's instruction:**
  `require constraint` was kept inside its `requirement def` example in the companion's
  `sysml-expert.md` and given a settled-semantics sentence, because swapping it to
  `assert constraint` would have taught invalid requirement modeling and deleted the visible
  requirement-side form ruling Q7 exists to preserve.
- Archived to `.project/completed/20260813_constraint-semantics-contract-amendments/`. Companion
  commit `dcb187b` in `/home/reid/1cfe/agentic-mbse-item7-rebuild`. Nothing pushed, no `main`
  touched, TEAx untouched — **`pre_pr` remains with the owner.** Residuals other closes homed
  against "Item 1's authoring guidance" (design-F2's Appendix C cell, the D9 advisory, item3-F2's
  premise conflict) are **re-homed to epic Item 7**, not reabsorbed here. The parked D-2 vs
  D-4/SRC-01 premise conflict stays parked at the umbrella level, verified byte-untouched.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 3 — Coverage Report and TEAx Policy (audited + cured + closed)
- **A generated report can no longer claim more coverage than was assessed, and TEAx can no longer
  read silence as freedom.** Before this item, two-of-nine assessed read `all_satisfied`, an
  excluded-only model emitted no report at all, and TEAx labelled such a package `unconstrained` —
  the same disposition a genuinely constraint-free model gets. Now every report carries a coverage
  account derived in one direction from the sealed catalog, the vocabulary has a `partial_coverage`
  state in both repos, and a constraint-bearing-but-unassessed package is distinguishable from a
  constraint-free one at the study-policy seam.
- **The load-bearing design resolution held all the way through: coverage is a second axis, not a
  slot in the headline.** The headline stays one precedence-ordered token (violation →
  indeterminate → full satisfaction → partial coverage → not assessed) while the coverage account
  is always present and always reaches the durable case record — so a `violation` report still says
  how much was checked. Partial coverage defaults to **keep-for-boundary**; `feed-strategy` needs an
  explicit, fingerprint-bearing config line, and a typo in either the key or the value fails closed.
- Audited **Certify-with-residuals**; **all six residuals (A-1..A-6) cured the same night** with
  **+29 pinning tests** (+26 TEAx, +3 codegen). Every residual was the same shape — a mechanism
  built correctly that no test pinned — so no cure fixed a defect and no production behaviour
  changed. All twelve spec success criteria are now verified and marked. Final gates: codegen
  **2050 passed / 34 skipped / zero licence-skip**, TEAx **337 / 0**, lint counters unchanged in
  both, **zero baseline byte churn**, companion untouched at `5088b41`. Nothing pushed; no `main`
  touched anywhere — **`pre_pr` remains with the owner.**
- **The coordinated TEAx work is a named unmerged deliverable**, branch `constraint-semantics-item3`
  at `5b70ae9`, four commits off pinned `main` `fa0e06a`. Keep the TEAx checkout on that branch
  until merge — codegen's execution lane imports simkit from its working tree. Publication order is
  codegen first. Item 2's re-vendor hand-off is discharged on that branch (accepted sets replaced,
  not extended). Details in §Unmerged branch above.
- **Two unearned checkboxes were found and corrected in this item's own records** — one ticked
  against a test varying the wrong field, one over an unrun validation step. Both were caught by
  looking, not by a failure, which is the point: an unearned `[x]` is what stops the next reader
  looking.
- Archived to `.project/completed/20260813_constraint-coverage-policy/`. Traveling residuals
  (design-F2's Appendix C cell, D9's companion advisory, item3-F2's unreachable `BLOCK` clause) are
  homed in the epic's Item 3 section with named owners; the epic's scope-4 wording correction was
  **performed** at close.

### 2026-08-13: CONSTRAINT-SEMANTICS Item 2 — Canonical Usage Domain and Catalog Totality (audited + closed)
- **Every authored constraint usage now has exactly one visible disposition, minted before
  occurrence expansion.** `catf_mfe_d5` was 65 authored usages → 9 carriers, with 56 simply
  *absent*; it is now **65 members, 9 reaching, 0 eligible** (the "9 eligible" premise the spec
  inherited was wrong — all 65 are bare `constraint`, so the 9 that expand grade
  `excluded`/`unassessed_form`). The proof is independent of the thing it checks: the
  `collect_constraint_manifest` sweep was **deleted** rather than kept in sync, and the oracle is 42
  reviewed expected-population files plus a licence-free `.sysml` scanner sharing no code, adapter,
  or parse with the elaborator.
- **What Items 3, 5, 6 build against** (unchanged by close):
  `InstanceGraph.constraint_usages: dict[DeclarationId, ConstraintUsageRecord]`;
  `catalog.usage_records` is the whole domain keyed by `declaration_id`; schema pins moved
  `instance-graph/v2`→`v3`, `CATALOG_SCHEMA_VERSION` `2.0.0`→`3.0.0`, companion
  `constraint-facts/v2`→`v3`; all 21 snapshot-bearing fixtures recaptured once at the final schema.
  A consumer wanting the old narrower set filters `disposition_kind == "eligible"`.
  **TEAx must still re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` with `3.0.0`** — hand-off filed in
  the epic; until then TEAx fails closed on newly generated packages, which is the intended
  direction.
- Audited **Certify-with-residuals** after a Needs-work first pass; A1–A4 cured one commit per
  family and re-probed at `77b4e3c`, R2/R4 record corrections landed (`014597b`, `35ee82f`). Final
  gates: codegen **1860 passed / 34 skipped / 0 failed**, zero licence-skip; `ruff` 12, `mypy` 55
  (both at/below baseline); `git diff --check` clean; companion untouched at `bc69f04`. Nothing
  pushed, `main` untouched in both repos — **`pre_pr` remains with the owner.**
- **Owner should read** the epic's Item 2 section: an **[AGENT]** severity exception now sits beside
  an **[INHERITED]** line — a malformed `@inapplicable:` directive halts at `error` grade whatever
  the usage's form, overriding "plain forms are never errors" for that one cause. Accepted at audit,
  orchestrator-ratified, not owner-ruled. Traveling residuals **R1** (internal bare-`ComputationGraph`
  seam is seal-only; no production caller) and **R3** (calc-def-only shape has no pre-item baseline)
  are carried in that same section; **R5** (no plan/implement-stage product-lens entry) is
  dispositioned as a recorded process gap in the ledger's close block, not backfilled.
- Archived to `.project/completed/20260813_constraint-catalog-totality/`. Environment fact worth
  keeping: **`uv run` is the wrong interpreter for this pair of worktrees** — it resolves
  `agentic_mbse` to the main checkout and the suite does not collect; use
  `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`.

### 2026-08-10: ELABORATE-FIRST Item 6 — Exact-Identity Completion (certified + closed)
- Exact declaration identity now covers the whole internal route: calc payload/compilation/
  formals/outputs and constraint decisions attach by UUID; native `Usage.usages` child authority;
  structured occurrences + typed IR + formal provenance in a fingerprinted `instance-graph/v2`;
  one-way projection ordered from typed producer edges; profile `BLOCK` halts by
  `SI_CONSTRAINT_BLOCKED`; deny-by-default F30 guard across all six boundary files.
- Three audit rounds (F1–F9) all remediated and independently verified; certification in
  `completed/20260810_elaborator-identity-completion/audit_v3.md` (re-audit addendum, lens CLEAR).
- Shipped legacy route, snapshot v5, neutral constraint facts, and generated baselines
  byte-frozen throughout; Item 7 atomic cutover unblocked, its deletion ledger extended with the
  four Item-6 transitional duals.

### 2026-08-09: ELABORATE-FIRST Item 5 — Exact-Identity Elaborator Breadth (certified + closed)
- Complete exact-ID front end proven beside the frozen legacy route: identity kill probes,
  cross-repo exact-UUID evidence, occurrence walker, typed graph, one resolver, projection to
  `ComputationGraph`, `instance-graph/v1` round-trip, 29-cell contract matrix at public/
  named-diagnostic evidence, live-verified 37-fixture dual-run ledger, and off-default public
  mutations on live and rebuilt routes.
- Five audit rounds drove out rendered-path selectors, fail-open branches, source-text evidence,
  and finally the invalid-namespace silent admission (now blocks
  `SYSML_NAMESPACE_NOT_DISTINGUISHABLE` pre-expansion; DCS witness repaired with explicit `:>>`).
- Archived to `.project/completed/20260809_elaborator-breadth/`; certification in `audit_v3.md`
  addendum; residues audit-F30/F31 + Item-6 obligations (F19/F26) recorded there and in the epic.

### 2026-07-24: docs-lifecycle-sync + nested-override-tripwire (closed on-branch; merged 2026-08-14 via codegen#10)
- Docs reconciled to merged main `936315c`: new `04-producer-resolution.md` +
  `30-diagnostic-severity.md`, doc 24 rewritten, REQ-SNAP-21/22 (matrix 276), module_kind
  sweep, explainer prompt re-anchored. Final audit: no open findings.
- Tripwire: unmatched-override warning in the supplied-value materializer (0 false fires
  across 19 fixtures; suite 3118/47). Full bridge fix filed in `[NESTED-OCCURRENCE-OVERRIDE]`.
- Archived to `completed/20260724_*`; CHANGELOG entries carry the detail.

### 2026-07-20: CONSTRAINT-LIFECYCLE Epic — Constraint Execution Lifecycle Remediation
- All 14 items (0–13) done; composed public proof 41/41 at the pinned set (rerun 22 / compose 19;
  16 negative mutations at boundary; 6/6 byte checks). Sealed artifact thread
  (generate→seal→trusted-load→evaluate→persist→resume/query) demonstrated end-to-end; IFE
  2,301-point + stellarator five-constraint acceptances pass.
- Merged 2026-07-20: agentic-mbse #11 first (enforced by `test_upstream_pins`), then codegen #9,
  then teax #3. Post-merge smoke green on main.
- Epic + 15 item folders archived to `completed/20260720_*`; release-readiness and the 41/41
  evidence-coordinate register live in `20260720_constraint-lifecycle-composed-proof/`.

### 2026-07-19: CONSTRAINT-WAVE epic — superseded
- Items 1 (profile semantics) and 2 (name safety) complete; Items 4 (snapshot portability) and
  6 (seal symlink symmetry) certified. All unfinished work mapped into CONSTRAINT-LIFECYCLE.
- Epic doc archived to `completed/20260720_epic_constraint_pr_wave_remediation.md`.

### 2026-07-18: GAP-CLOSE epic — local scope certified
- Items 2/3/4 certified; Item 1 codegen leg complete. External TEAx leg
  `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open in BACKLOG; epic doc still in `backlog/`.
- Same day: numerical-constraint-profile certified + committed; CONSTRAINT-EXEC code-quality
  remediation cures committed (D5 discharged by the v3 item).

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
- Also 2026-07-13: docs-explainer-refresh audited Certify and pushed to the open PRs.

### 2026-07-10: PUSH-DOWN epic — independently audited and certified
- Expression reconstruction, qualified-name split, hierarchy primitives/models, aggregation
  decomposition moved to agentic-mbse (PRs #8 codegen / #10 agentic-mbse merged).

### 2026-07-08: TRUTH-DEBT Epic
- Archived all six audited items plus the epic ledger to `.project/completed/`.
- Retired the F4 aggregation cutover, resolved multi-hop chain support, matrix test gaps,
  inherited-attr classifier fix, matrix sweep residue, and D3 hygiene tail.
- Pre-PR gates: 2120 passed / 4 skipped / 0 xfailed; ruff src clean; mypy src 97;
  matrix 259 = 258 PASS + 1 UNTESTED.

### 2026-07-06: PIPELINE-TRUTH epic complete; UPSTREAM-FINDINGS + docs-scrub merged
- PIPELINE-TRUTH: all 10 items landed and audited PASS. UPSTREAM-FINDINGS merged (PR #3);
  docs-scrub certified and merged (PR #4).

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

## Up Next — the road back from the detour (written 2026-08-14, orchestrator + owner)

The CONSTRAINT-SEMANTICS epic was a nested detour inside ELABORATE-FIRST Item 7's branch,
triggered by the step-4 probe. The sequence back out, in order:

**A. Finish CONSTRAINT-SEMANTICS — ✅ DONE 2026-08-14.** Item 7 closed and archived; the epic
closed and archived with all ten Success Criteria ticked against their amended forms and Lessons
Learned written. **`pre_pr` was not run at epic close, by ruling** — the epic's changes live on the
unmerged `item7-rebuild` line and ship with it; the branch gate runs once, at phase D.

**B. Resume ELABORATE-FIRST Item 7 (cutover recovery steps 4–10) — ✅ DONE 2026-08-14.**
Steps 4–10 all executed; **[OWNER 2026-08-14] ACCEPTED** the final candidate at Gate 3
(plan.md "Gate 3 — final acceptance" + "Narrow-correction step 10 completion"; audit
CERTIFY-WITH-RESIDUALS, 0 blocking). Item closed and archived 2026-08-14, owner-authorized
(`completed/20260814_cutover-recovery/` + `20260814_elaborator-cutover/`). The
original sub-list, kept for the record:
1. Revise the step-4 brief per the pause record (its zero-input-report instruction and
   REQ-CL-03/04 closures are superseded by the landed contract) and discharge the epic's
   Item 7 Evidence-Invalidation Register row by row
   (`.project/completed/20260814_epic_constraint_semantics_contract.md` §"Item 7
   Evidence-Invalidation Register" — nine rows, each naming rerun vs absorbed; **HANDED at epic
   close, undischarged**). Step 4 also **mints the REQ-tag family for the Items 3/5/8/9 gates**
   (owner-authorized 2026-08-14, `[CONSTRAINT-GATES-UNTAGGED]`) so the matrix is touched once.
2. Execute steps 4–6, then 7–8 ONCE at the true final paired codegen/companion OIDs (three
   batteries + one regenerated candidate record), step 9 fresh narrow audit, step 10 **owner
   final acceptance** (owner-grade; no push/tag/close from agents).

**C. ELABORATE-FIRST Item 8 — Downstream Remediation and Certification (3–5 days,**
`epic_elaborate_first_architecture.md:472`): Fusion Tea + Stellarator regeneration on the
corrected architecture, the July IFE impact audit, certification/doc repair (the retired
reference docs 11/12/13/16/24/25), the `[OWNER-VERBATIM]` allowable-modeling-pattern guidance
(`in R = R` diagnostic + replacement forms), one composed proof thread. **Scrub its scope
against what CONSTRAINT-SEMANTICS already delivered first** — Items 1/7 landed part of the
guidance obligations; don't re-do them.

**D. The PR wave — DONE 2026-08-14.** One coordinated branch-level shipment, July-wave
pattern, after step 10's owner acceptance. Executed in the pin-enforced order as squash-merge
PRs (owner bypassed the base-branch review policy to merge): agentic-mbse#12 (`1decd95`),
codegen#10 (`385e163`), teax#4 (`744745f`); each main tree verified byte-identical to its
acceptance branch tip. Post-merge licensed smoke on merged codegen `main`: 2086/34/88, zero
license-skip. Cleanup executed the same day: `elaborate-first-salvage` label deleted, all
three checkouts returned to `main`, the `sysml-conventions` symlink restored to the main
agentic checkout (this commit). Worktree/venv deletion remains (owner timing — see top
block).

**E. Back to the original goals** (what triggered all of this — the demo, and the
design-search *policy*):
- The **policy substance is now landed**: assert-only enforcement, coverage-truth headlines,
  study-policy defaults, the equality taxonomy, and the owner's coverage-truth product promise
  (first-capture via CONSTRAINT-SEMANTICS Item 7). What was never written is a single
  user-facing design-search policy narrative — candidate follow-on, owner's call whether the
  product entry + guidance suffice.
- The **demo** route back: fusion-tea regenerates in phase C (its `in R = R` fan-out cause is
  structurally fixed by the exact route; the old workaround question dissolves into
  migration); a real CATF design-search campaign additionally needs
  `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` (P1 — without it the search rejects everything near the
  authored regime).
- **Next-slot competitors after D** (owner picks): the cryo fix (P1, small),
  `[CALCDEF-GATE-IMPLEMENTATION]` (P1, 7–9 days, authorization parked), and a composed
  design-search demo item that would close the loop on the original intent.

Superseded Up Next items (pre-detour): CE-F1/F2 follow-ons and `[V2-HTML-BUILD]` remain in
BACKLOG; the old "documentation update pass" was absorbed by CONSTRAINT-SEMANTICS Items 1/7
and ELABORATE-FIRST Item 8's doc-repair scope.

---
