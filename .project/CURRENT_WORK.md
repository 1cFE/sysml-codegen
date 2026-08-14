# Current Work

**Last Updated**: 2026-08-14 (**Item 7 CLOSED and archived** to
`.project/completed/20260814_constraint-docs-agent-sync/`, verdict CERTIFY-WITH-RESIDUALS. **All
nine CONSTRAINT-SEMANTICS items are now closed.** Epic close, the epic's Lessons Learned, and
`pre_pr` are unrun by ruling and remain with the owner; nothing is pushed and no `main` is touched)

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

### 2026-08-14: CONSTRAINT-SEMANTICS epic — all nine items closed; the tail is the owner's

Items 1–9 are all closed and archived (Item 7 today; the rest 2026-08-13 — see Recently Completed).
What is live now:

- **The epic itself is still open, by ruling `[OWNER 2026-08-14]`.** Item 7's close archived the
  item only. Epic close, the epic's **Lessons Learned**, and `pre_pr` have not run and are the
  owner's to schedule. The umbrella folder `.project/active/constraint-semantics-contract/` stays
  active until epic close.
- **Two residuals ride out of the epic, both owner calls** (detail in the Item 7 sections above):
  the codegen `.claude/` **symlink target**, which resolves when the owner merges the
  `item7-rebuild` agentic-mbse worktree branch into whatever branch those symlinks point at, and
  **`[CONSTRAINT-GATES-UNTAGGED]`**, which needs REQ tags minted before Items 3/5/8/9 can get
  verification-matrix rows.
- **Item 6's production implementation is out of this epic `[OWNER 2026-08-13]`** and is now the
  unowned backlog entry `[CALCDEF-GATE-IMPLEMENTATION]` (P1, 7–9 days, graph v4 + catalog 4.0.0,
  codegen + TEAx), parked with the owner. It competes for the next slot with
  `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` and the paused ELABORATE-FIRST Item 7 resumption. Its plan of
  record is
  `.project/completed/20260813_calcdef-constraint-gate-design/implementation-item.md`. The Item 8
  start gate is satisfied at `62a07e5`; the only remaining block is owner authorization. No agent
  starts it without a new ruling.
- **Nothing pushed; no `main` touched anywhere; TEAx stays on `constraint-semantics-item3` @
  `5b70ae9`.** `pre_pr` remains with the owner.

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
**Spec: `.project/active/constraint-semantics-contract/spec.md` — reviewed (verdict Revise) and
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

### Unmerged branches awaiting owner (both items CLOSED 2026-07-24, owner-directed)

- **`docs-lifecycle-sync`** — docs + `.project/` only. Item archived to
  `completed/20260724_docs-lifecycle-sync/` (audit: no open findings).
- **`nested-override-tripwire`** (stacked on it) — the only `src/` change. Item archived to
  `completed/20260724_nested-override-tripwire/`.

Merge the first for bookkeeping+docs, the second on top for the tripwire. Both items were
closed on-branch before merge (owner-directed); their CHANGELOG entries note merge pending.

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

### 2026-07-24: docs-lifecycle-sync + nested-override-tripwire (closed on-branch; merge pending)
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

**A. Finish CONSTRAINT-SEMANTICS (in flight).** Item 7 (docs/ADR/agent prompts) is running;
then epic close with Lessons Learned. **No pre_pr at epic close** — the epic's changes live on
the unmerged `item7-rebuild` line and ship with it; the branch gate runs once, at phase D.

**B. Resume ELABORATE-FIRST Item 7 (cutover recovery steps 4–10),**
`.project/active/cutover-recovery/plan.md` ("PAUSED at step 4", now released):
1. Revise the step-4 brief per the pause record (its zero-input-report instruction and
   REQ-CL-03/04 closures are superseded by the landed contract) and discharge the epic's
   Item 7 Evidence-Invalidation Register row by row
   (`epic_constraint_semantics_contract.md` §register — each row names rerun vs absorbed).
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

**D. The PR wave (the answer to "PR into what").** One coordinated branch-level shipment,
July-wave pattern, after step 10's owner acceptance:
1. Owner runs `pre_pr` once per repo over the whole branch line (ship-together rule).
2. Merge order enforced by pins: **agentic-mbse first** (`agentic-mbse-item7-rebuild` → its
   main; `test_upstream_pins` compares codegen against the installed companion), then
   **codegen** (`item7-rebuild` → main — one PR carrying the Item-7 cutover + the whole
   CONSTRAINT-SEMANTICS epic), then **TEAx last** (`constraint-semantics-item3` → main; TEAx
   is never bumped first and fails closed until codegen lands; remote needs explicit HTTPS).
3. Until then the TEAx checkout stays on its branch (codegen execution lane imports simkit
   from that working tree).
4. **agentic-mbse branch fact, settled 2026-08-14 [verified by git]:** `elaborate-first-salvage`
   is fully contained in `item7-rebuild` (main → +3 → salvage → +9 → item7-rebuild; one line, no
   fork). The authoritative branch is `item7-rebuild`; the authoritative working tree is
   `/home/reid/1cfe/agentic-mbse-item7-rebuild`. The main checkout is parked 9 commits behind on
   the same line (legacy pre-rebuild environment + `.env` host only). At this phase's merge:
   delete the `elaborate-first-salvage` label (subsumed), return the main checkout to `main`,
   and **restore codegen's `.claude/skills/sysml-conventions` symlink to the main checkout**
   (repointed to the worktree on 2026-08-14, owner-approved interim, commit pending in this
   change).

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
