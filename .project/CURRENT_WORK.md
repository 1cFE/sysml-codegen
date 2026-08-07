# Current Work

**Last Updated**: 2026-08-07 (ELABORATE-FIRST Items 1–4 complete + Item 5 Phase 1 done; next: Item 5 Phase 2 shape learning tests)

---

## Active Work

### 2026-08-07: ELABORATE-FIRST epic ratified — Item 1 (forensic freeze + transition) DONE

**[OWNER 2026-08-07]** ruling: the string-resolution architecture itself is the defect home.
`in R = R` is a modeling bug to reject, referents must be consumed at load time, and snapshots are
a format choice. Direction ratified: replace the front end with elaborate-then-project (instance
graph as the single IR and snapshot payload; projection onto the existing `ComputationGraph` seam;
the ~3,450-line string-compensation machinery deleted at cutover, not wrapped).

- Plan of record: `.project/backlog/epic_elaborate_first_architecture.md` (7 items,
  spike/learning-test-first so failures are cheap; Item-3 elaborator spike is the go/no-go).
- Direction evidence: `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`
  (diagnosis, deletion inventory, seam verification, 7-shape pressure test, SysIDE capability
  survey) alongside the recovery assessment below.
- SOURCE-IDENTITY epic amended: Items 4–5 superseded, Items 1–3 inherited as semantic authority
  (29-cell matrix unchanged), Items 6–8 absorbed into ELABORATE-FIRST Items 6–7.
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
- **ELABORATE-FIRST Item 5 Phase 1 DONE 2026-08-07** (`.project/active/elaborator-breadth/plan.md`
  has full notes): production `src/sysml_codegen/elaboration/` landed (graph.py + elaborate.py,
  D1–D5; AST-walked calc/constraint population with `expand_templates=False` + the def-context
  remap rule — D10's rejected shortcut avoided); per-binding evidence builders factored to
  `extraction/binding_evidence.py` (shared by both front ends); `screen_source_readiness`
  template-skip moved to caller policy (elaborator screens declarations, templates included —
  that's where fusion_tea's self-binding lives). Spike parity gate GREEN: 16 kept licensed tests
  in `tests/conformance/test_elaboration_spike_parity.py` (C25/C8/C24/C12/C13/C15/stamp/C11/
  deep-path/C19/self-binding/Bank/node-ID stability). `_constraint_actuals` registered in the
  AST-dispatch guardrail (4 dual-check / 6 multi-type sites). Committed `f8870a7`.
- **Item 5 Phase 2 leg 1 (cross-package / multi-hop EXPOSE) DONE 2026-08-07**: learning test +
  implementation in one leg. Discoveries: real plant models are untyped-part-based (all 42
  catf_mfe calcs), EXPOSE = alias edge, and **catf_mfe authors a real SRC-01 self-binding**
  (`vacuum.sysml:176`) — forced the D9 `strict` halt-vs-report switch early (lenient records
  findings, skips only offending bindings; Phase 3's grind needs it). 15 kept tests
  (`test_elaboration_expose_shapes.py`); findings
  `.project/research/20260807-163643_elaborator-crosspackage-expose-shapes.md`. Gates:
  3187/47/18 licensed (zero skip lines), ruff clean, mypy 72-baseline, no fixture churn.
  **Next: Phase 2 leg 2 — sibling same-name channels (sibling_channel_ambiguity).**

### 2026-08-07: SOURCE-IDENTITY Item 4 — architecture recovery assessment

Recovery report:
`.project/research/20260807-143615_source-identity-recovery-assessment.md`. It records an agent
recommendation to stop before Phase 3 and reopen the Item-4/Item-5 boundary. The epic, spec review,
design review, and plan explicitly required a production identity subsystem whose output the legacy
runtime resolver would ignore until Item 5; the 742-line `analysis/source_identity.py` is therefore
the designed result, not an isolated implementation embellishment. Across codegen and agentic-mbse,
phases 1–2 add a net 1,413 production-Python lines, 1,497 test-Python lines, and about 451 fixture /
provenance lines before snapshot v6 or resolver cutover. The report classifies exact extraction
facts, occurrence queries, fixtures, and semantic oracles as salvage candidates; it classifies the
manifest, coordinate ledgers, query recorder, wrapper authority, and attach-but-ignore integration
as presumptive rewrite/removal candidates. It recommends one vertical replacement that carries a
small exact source reference through the existing `ProducerRequest` into the actual runtime selector
and deletes the superseded decision path in the same landing unit. No implementation files were
deleted, reverted, committed, or reset at assessment time. **Disposed 2026-08-07:** the owner
ratified the elaborate-first replacement (entry above), which goes further than this report's
recommended vertical repair — the thread-a-ref-through-the-existing-resolver variant was rejected
as retaining the ladder skeleton.

The dirty tree is not currently green: a post-audit chain-fact API change returns five values while
three callers still unpack four, aggregation term-contract tests are stale, and codegen still drops
the new chain-root/member evidence. The audit's green counts describe the earlier audited state.

### 2026-08-07: SOURCE-IDENTITY Item 4 — Phases 1–2 AUDIT: NEEDS WORK

Audit: `.project/active/source-identity-occurrence-foundation/audit.md`. The owner-grade product
lens is BLOCKED on C24: calculation projection identifies `producer_calc.result`, while the
aggregation leg loses its chain root and raises `SI_OCCURRENCE_MISSING`. The audit also reproduced
identity changing with diagnostic authored spelling, found invocation expressions bypassing
readiness, and confirmed aggregation scoping still joins legacy rendered paths to structured
occurrences. The contradicted plan items are reopened. No spec or epic criterion was certified.
Phases 3–5 remain unstarted.

Implementation evidence retained from the phase pass:

- **Phase 1 (extraction evidence):** immutable `SourceReferenceEvidence` on handled bindings
  (exact SysIDE referent + bound formal + authored form; `#(i)` retained as
  INDEXED_SOURCE, never flattened), shared `ResolvedTargetFact` on aggregation terms and nodes,
  value-site identity on `RedefinitionData`/`DesignAttributeData`, and emit-only D8 readiness
  screening before registry construction. Invocation expressions are not handled, and aggregation
  term transport drops the chain root. All new fields are snapshot-excluded; v5 wire bytes were
  verified unchanged. Evidence types live in `extraction/source_evidence.py` (REQ-EXT-06),
  re-exported by `analysis/source_identity.py`.
- **Phase 2 (authority + projection):** `SemanticSourceIdentity` (declaration + structured
  occurrence), typed coordinates, immutable manifest with duplicate/missing rejection,
  per-phase `OccurrenceQueryRecorder` (finalize ≠ seal), contextual projection
  (unique/missing/ambiguous, `SI_OCCURRENCE_*` codes), redefinition remap (usage override →
  specialized def) that already converges C25's def/usage legs and recovers C21's specialized
  declaration; `PartInstanceIndex` gained exact raw-QN reverse queries with the same atomic
  cycle/non-finite failures (constraint-free fail-closed boundary tested). The audit found that
  `member_path` still comes from diagnostic `authored_segments`, a no-context projection can use
  global uniqueness, and aggregation eligibility still originates in the legacy path finder.
- **Gates:** full licensed codegen suite 3189 passed / 52 skipped / 18 deselected (zero
  license-skip lines), focused phase selection 191 passed / 5 skipped, ruff clean, mypy at the
  72-error baseline, agentic-mbse 1811 passed / 1 skipped / 33 deselected, and `git diff --check`
  clean. These green commands do not clear the structural audit findings.
- **Surfaced for the owner / Phase 3:** (1) D8 fail-closed enforcement scoping — the pinned
  fixtures (fusion_tea, ife_plant, solar) are full of SRC-01 self-bindings and must keep
  generating through Item 4, so Phase 1 emits dispositions without halting; the exact
  enforcement boundary needs the Phase-3 ruling. (2) C18's constructed-fixture premise fails at
  the SysIDE boundary: a genuinely absent term target refuses to load (`reference-error`), so
  the POLICY_DIAGNOSTIC outcome is unreachable live for that form — pinned in the fixture's
  PROVENANCE, ABSENT_REFERENT proven unit-level, reconcile at Phase 5.

### 2026-08-07: SOURCE-IDENTITY Item 4 — implementation plan (background)

Spec: `.project/active/source-identity-occurrence-foundation/spec.md`. It inherits the ratified
declaration-plus-occurrence contract, the one-bridge constraint, all Item-4-owned Appendix C
coordinates, snapshot version/fail-closed obligations, and the owner-requested `agentic-mbse`
diagnostics. An agent recommendation ratified by the owner on 2026-08-07 moves the atomic
37-extraction-snapshot recapture into Item 4 with the format cutover; the single-version loader and
snapshot gate make a later Item-6 recapture impossible without leaving Items 4–5 red or adding the
forbidden compatibility shim. The spec-review findings are incorporated: Item 4 reviews that
recapture for format/identity correctness, route parity, and unrelated drift; Item 5 owns the C14
synthesis and C26 public-topology flips; Item 6 owns final post-cutover semantic certification and
downstream migration. The absorbed repair introduces no parallel walker, the `agentic-mbse`
wrong-oracle tests must be replaced rather than disabled, and that cross-repository validation leg
may phase independently of the atomic codegen snapshot unit. Product-lens rev 3 is CLEAR with no
findings or smells. The owner advanced the revised spec to design on 2026-08-07.

Design: `.project/active/source-identity-occurrence-foundation/design.md`. It chooses one immutable
source-identity manifest, one authority over the existing structured occurrence index, snapshot v6
transport with a shared union query transcript, and an identity-derived C19 repair that leaves the
Item-5 resolver cutover untouched. The design-review findings are incorporated: modeled value sites
now have an exact definition and coordinate, transcript sealing is separate from manifest
finalization, replay coverage is route-aware and testable, universal indexing's fail-closed boundary
is explicit, and structured aggregation scoping must preserve the existing eligible output set. The
handoff also states plainly that Item 4 does not fix the customer-visible fan-out defect; the legacy
key table and C14/C26 current-defect pins remain until Item 5. The owner advanced the revised design
to planning on 2026-08-07.

Plan: `.project/active/source-identity-occurrence-foundation/plan.md`. The owner approved the
five-phase strategy on 2026-08-07: preserve exact extraction evidence; build the identity authority
and contextual occurrence projection; integrate the live route and repair C19; cut snapshots
atomically to v6 with all 37 recaptures; then land the independent `agentic-mbse` diagnostics leg and
run the full acceptance gates. Phases 1–4 are one atomic codegen landing unit. The plan explicitly
reconciles extraction-only diagnostic snapshots with fail-before-registry generation, requires
route-aware transcript coverage, and keeps the Item-5 fan-out defect pins. The written plan is
awaiting implementation approval.

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
