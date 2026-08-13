# Current Work

**Last Updated**: 2026-08-12 (CONSTRAINT-SEMANTICS Item 1 implemented; Items 2–5 have a published contract)

---

## Active Work

### 2026-08-12: CONSTRAINT-SEMANTICS Item 1 — contract and authoring policy (IMPLEMENTED)

**All six phases landed.** The documentation half of the owner's sequence is done: the ratified
contract, the frozen requirements companion, and every living-surface statement across both
repositories now teach assert-only enforcement and coverage-truthful headlines.

**What Items 2–5 may now build against:**

- **The definitions home** — the lifecycle contract's `### Headline states and coverage truth`
  subsection: the applicable-asserted-gate test (on the form, not the predicate), the
  inventory-versus-feasibility split, the six states, the precedence, and the both-vocabularies
  obligation. Item 3 reads this for state meanings, and invariants 46/46a for fail-closed behavior.
- **New invariant 61** (vacuous gate at warning grade), with its companion mirror LC-E13 and its
  Appendix C acceptance cell.
- **Invariant 28 + LC-E05** — the third disposition kind, non-reaching-with-reason, for Item 2.
- **Invariant 48 + LC-G07** — the embedded catalog as sole authority for coverage truth.
- **ADR-009** (`docs/architecture/modeling-assumptions.md` §9) — why the change was made and what
  the superseded contract and companion text said.
- **The equality instruction** — authority copy in the contract's supported boundary, rendered in
  full in agentic-mbse `docs/patterns/constraints.md` for Item 5's all-65 owner checkpoint.

**Two things stayed open, deliberately.** Four `all_satisfied` assertions in `tests/execution/`
are executable text and the token spelling is Item 3's — handed on, not corrected. REQ-EXT-09's
totality evidence carries a pointer to Item 2 and keeps its `PASS` status; choosing the
replacement proof is Item 2's.

Evidence: `.project/active/constraint-semantics-contract-amendments/verification.md` — the
pre-edit and post-edit sweeps with per-hit dispositions, the pairwise precedence-agreement check,
the RI-1..RI-7 discharge table, and every mechanical check. Companion commit `dcb187b` in
`/home/reid/1cfe/agentic-mbse-item7-rebuild`. Next: `/_my_audit`.

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

---

## Recently Completed

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

## Up Next

1. **Documentation update pass** (see Documentation debt above): severity-system doc home,
   portability matrix row, `docs/architecture/` sweep vs merged main, EXPLAINER_PROMPT
   re-anchoring. Reuse the Item 6 three-sweep inventory method.
2. **CE-F1/F2 follow-ons** (BACKLOG): direct TEAx consumption of codegen's embedded catalog with
   the alternate catalog schema/materializer removed, plus multi-channel CandidateBridge (teax).
3. **pipeline_explainer_v2.html build** (`[V2-HTML-BUILD]`, P2, owner-assigned elsewhere) — after
   EXPLAINER_PROMPT re-anchoring.
4. **Owner decisions** listed under Open decisions (branch delivery/deletion, stale-baseline
   owner, nested-occurrence-override scheduling, Item-10 completeness ruling).

---
