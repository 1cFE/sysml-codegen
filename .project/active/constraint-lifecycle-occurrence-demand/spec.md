# Spec: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Status:** Revised — ready for independent re-review
**Owner:** Reid W
**Created:** 2026-07-19 15:13 PDT
**Revised:** 2026-07-19
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — Item 1, register row 1
**Item 0 RED predecessor:** sysml-codegen `ecdc7285be1508c08e82830c93072306f40e6b34`

---

## Problem

The current constraint path has the right finite-occurrence and supplied-value pieces, but their
composition is not total.

- Demand discovery converts the profile's ordered usage decisions into nullable qualified-name set
  membership. Anonymous admitted and excluded usages can then alias. The excluded usage may expand,
  synthesize a value it never consumes, or query an owner absent from a valid replay transcript.
- The part-instance walk treats a revisited definition as an empty subtree. Recursive containment
  can therefore return a plausible finite prefix after silently discarding the cycle.
- Calculation bindings and constraint actuals enter supplied-value materialization as appended
  actionable records. A later duplicate overwrites the earlier target's grouping provenance,
  doubles counts, and can duplicate warnings.

These are three symptoms of one lifecycle gap: usage disposition, finite occurrence expansion, and
materializer demand do not preserve one complete identity-bearing thread. Item 1 must restore that
thread through public live generation and delete the nullable and duplicate paths. It must not grow
into Item 2's general producer resolver, Item 5's relocated whole-tree proof, or Item 13's composed
sealed-artifact proof.

## Success Criteria

These four outcomes are owner-originated. They are the only `[NEED]` items in this contract. The
detailed requirements and proof choices below remain inherited or agent-authored under the
capture-fidelity absorb mapping.

- [x] **[NEED]** The original occurrence and demand lifecycle invariants are met, rather than only
      the three reproduced lines being patched. Source: owner stage input, 2026-07-19.
      Evidence: the lifecycle boundary itself was rebuilt — verified association, an
      all-or-nothing prepared batch, explicit owner dispatch, structural cycle failure, and
      one logical demand per normalized target. evidence.md §2, §4.
- [x] **[NEED]** Public functionality works for Item 1's live occurrence, anonymous-actual,
      owner-filter, shared-demand, and per-occurrence-override outcomes. Source: owner stage input,
      2026-07-19. Evidence: six public licensed nodes pass with no skip, and the
      per-occurrence-override outcome is proved through real TEAx execution
      (4.0/6.0 -> violated/satisfied). evidence.md §2, §3.
- [x] **[NEED]** Code quality improves and the superseded nullable/duplicate paths are deleted.
      Source: owner stage input and simplification direction, 2026-07-19. Evidence: every
      named superseded path is deleted with no wrapper, flag, alias, or dead fallback
      remaining (`rg` returns no matches); `lower_constraints` complexity fell 34 -> 19.
      Judged qualitatively per the owner's 2026-07-19 LOC ruling. evidence.md §1, §4.
- [x] **[NEED]** Delivery is judged by those working outcomes and truthful evidence, not by making
      every supporting artifact perfect. Source: owner revision direction, 2026-07-19.
      Evidence: evidence.md records eight deviations, a review-confirmed defect and its
      fix, a Phase 0 digest mis-recording correction, an unexecutable-RED caveat, and the
      open Items 4/5/13 — rather than a clean-looking record. evidence.md §5-§8.

## Known Requirements

### A. Scope and lifecycle authority

- **OD-R01 [INHERITED]** Owner kind controls occurrence expansion; source form controls predicate
  selection. The axes remain independent. Source: lifecycle LC-D01 and ratified invariant 16.
- **OD-R02 [INHERITED]** Every finite concrete occurrence receives its own execution identity,
  catalog entry, module, and result channel. A truly shared producer may serve several occurrences,
  but the per-occurrence bindings record that sharing. Source: LC-D02, LC-D03, and invariant 17.
- **OD-R03 [INHERITED]** Recursive, non-finite, malformed, or unsupported occurrence expansion
  blocks loudly and never returns partial expansion as complete. Source: LC-D04 and invariant 18.
- **OD-R04 [INHERITED]** Register row 1 closes when its required public live anonymous-actual,
  shared-demand, recursive, finite, and per-occurrence-override cells pass. Relocated replay and
  full-tree certification remain row 5; the composed artifact thread remains row 17. Source:
  lifecycle register row 1, proof standard, and lifecycle spec LC-I09.
- **OD-R05 [INHERITED]** Item 2 owns the shared calculation/aggregation/constraint producer and
  exact-QN resolver. Item 5 owns relocated whole-tree portability. Item 13 owns the final sealed
  load/evaluate/persist proof. Source: lifecycle remediation epic Items 2, 5, and 13.
- **OD-R06 [INFERRED]** Public live certification starts from source through the supported codegen
  generation seam. Synthetic facts, occurrence tables, or concrete constraints may isolate a
  negative but cannot close a row-1 public-live cell. Basis: lifecycle proof standard and LC-I09.
- **OD-R07 [INFERRED]** Item 1 promises association stability within one extracted facts batch and
  the same semantic capture. It does not create cross-version anonymous identity or `tracking_key`
  semantics. Basis: LC-D11 and Item 12 ownership.
- **OD-R08 [INFERRED]** Same-checkout replay is valuable R-4/R-7 regression evidence but is not an
  LC-I09 certifying snapshot route. Basis: LC-I09 defines the certifying route as relocated replay
  with the full coordinate and artifact thread.

### B. Usage/decision association and occurrence totality

- **OD-R10 [INFERRED]** Every extracted usage is associated one-to-one with exactly one profile
  decision before owner filtering or demand collection. The association distinguishes anonymous
  siblings even when their names and qualified names are null. Cardinality mismatch, deletion,
  duplication, or reorder mismatch fails before expansion. Basis: R-4 and the verified profile
  behavior at `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:996-1008`.
- **OD-R11 [INFERRED]** Ordered usage/decision pairing is permissible only with explicit
  cross-checks. At minimum, usage and decision counts must agree,
  `decision.identity == usage.identity`, and `decision.location == usage.location` before
  eligibility is consumed. A durable new identity is not required. Basis: R-4, the current
  `UsageDecision` fields, and spec-review finding L2-1.
- **OD-R12 [INHERITED]** Eligibility and supported owner kind are filtered before occurrence
  expansion. Admitted `part_def`, `calc_def`, and `package` owners use their existing explicit
  expansion rules. Excluded usages, `requirement_def`, and unknown kinds contribute no executable
  demand. Source: remediation epic Item 1 scope 1 and R-4.
- **OD-R13 [INFERRED]** `package` is an explicit expansion branch. An unrecognized owner reaching
  executable expansion fails contextually rather than inheriting package cardinality from a default
  arm. Rationale: a fallback would silently add support for future owner kinds.
- **OD-R14 [INFERRED]** Capture and same-checkout replay make the same supported admitted-owner
  queries. A missing frozen entry is corruption only when such a query legitimately requires the
  owner; the error keeps owner/section context and recapture guidance. Excluded or unsupported
  usages never manufacture a corruption query. Basis: R-4 and the frozen-index contract.
- **OD-R15 [INFERRED]** An owner query containing any recursive cycle is atomic. This includes an
  owner whose traversal visits a valid finite branch before the cycle and permutations that reorder
  those branches. The query raises with usage, requested owner, offending edge, and full cycle path;
  it returns no owner result, records no entry for that owner, and triggers no demand,
  `PipelineContext`, transcript, graph, catalog, or output-target mutation. Basis: invariant 18,
  R-5, and `RecordingOccurrenceIndex` record-after-complete behavior.
- **OD-R16 [INHERITED]** Existing finite behavior remains stable: subtype closure, most-specific
  type identity, owning-definition-plus-feature cardinality keys, retype/redefinition dedup,
  integer sibling order, equal finite bounds, same-name owner separation, and Cartesian expansion.
  Source: completed part-instance spec/design/audit and lifecycle invariants 17–18.

### C. Supplied-value demand identity and precedence

- **OD-R20 [INFERRED]** Cross-route demand identity is defined only at the existing supplied-value
  materializer target-normalization seam, `_binding_target(source_path, instance_scope)` in
  `src/sysml_codegen/resolution/supplied_values.py:61-99`. Its existing rules prove equivalence as
  follows:
  1. a sanitized `::` reference identifies `_BindingTarget.qn` directly;
  2. one-hop `part.attribute` identifies
     `{instance_scope}__{part}__{attribute}`; and
  3. a bare identifier identifies `{instance_scope}__{identifier}`.
  Two route records are the same demand only when these existing rules produce the same
  `_BindingTarget.qn`. Numeric, multi-hop, or unparseable paths remain outside this materializer.
  Basis: R-7 and spec-review finding L2-2.
- **OD-R21 [INFERRED]** Deduplication occurs after `_binding_target` normalization and before
  `_resolve_value`, literal resolution, or `DesignAttributeData` materialization. Syntactic
  equivalences not already proven by OD-R20 do not coalesce in Item 1. General producer/exact-QN
  resolution remains Item 2. Basis: current supplied-value phase ordering and Item 2 ownership.
- **OD-R22 [INFERRED]** When calc and constraint routes normalize to one target, calc-route grouping
  provenance wins. Adding an assertion must not regroup an existing calculation input. This is an
  agent bet derived from R-7 and the lifecycle matrix's “exact parameter group survives” outcome;
  it is not owner-settled.
- **OD-R23 [INFERRED]** A constraint-only target uses the normalized target's authoritative
  model/source provenance when available, then the admitted usage's portable source file. If no
  deterministic group provenance exists, collection fails with usage/target context. It never uses
  a sentinel, current working directory, or silent `source_file is None` drop. This is an agent bet
  preserving constraint-only functionality without inventing grouping.
- **OD-R24 [INHERITED]** Existing supplied-value literal precedence and direct-owner scoping remain
  unchanged. A real captured design attribute still wins over synthesis. Source: supplied-values
  contract and kept tests.
- **OD-R25 [INFERRED]** Unique demands are processed in ascending normalized target-QN order.
  Scan/apply/non-literal counts describe unique targets; collision/non-literal warnings occur once
  per target in that order; synthesized attributes follow the same order. Route and input reversal
  changes none of those observations. Rationale: append order and unordered set/dict iteration
  cannot be lifecycle precedence.
- **OD-R26 [INHERITED]** A shared calc/constraint target retains one intended producer through
  pruning, while a constraint-only target remains discoverable and materializes once. Source:
  lifecycle mandatory shared-demand and producer-retention cases plus R-7.
- **OD-R27 [INFERRED]** Same-checkout replay exercises the same OD-R20–OD-R26 demand rules and must
  match live demand identity, grouping, counts, exact warning values/order where applicable,
  retained producer, and catalog values. This is non-certifying R-7 regression evidence; it does
  not claim relocation or full-tree parity.

### D. Evidence coordinate and regression breadth

- **OD-R30 [INFERRED]** The exact unchanged-test RED coordinate is the Item 0 compatible predecessor:

  | Repository | Revision | Package/profile | `uv.lock` SHA-256 |
  |---|---|---|---|
  | agentic-mbse | `515e08bbcd70aa9d23212765161bd02b3e3d8f23` | package `0.1.2`; `executable-profile/v4` | `ed48eb993406d6dba1ed1c2a64ff752bf871a283f9157ae41ffcbb9ff7036a4f` |
  | sysml-codegen | `ecdc7285be1508c08e82830c93072306f40e6b34` | package `0.1.0` | `fea88fbb1b4cb2b3aadf27f7511999533bcbb70c841ea928c5399cd7f3be08f2` |
  | TEAx | `d545701f575133350474108c96202a2ac5244462` | teax-simkit `0.1.0` | `d9b41eef19354cd009448e9bed8317e66a4dd8ba34c8e3fb774f6bf14a22413d` |

  TEAx remains pinned even where a RED node stops in codegen. Source: Item 0 candidate evidence.
  The original review reproduced R-4/R-5/R-7 on sysml-codegen `512786c7dfab44fba7a0185d09e845b7494c702d`
  with agentic-mbse review ref `54a95d2ffe18f8e7b437a7f895843e0c89c98c27`; that is historical origin evidence, not the
  coordinated RED certification point.
- **OD-R31 [INFERRED]** New defect-specific tests are authored once and run unchanged at OD-R30 RED
  and the implementation candidate GREEN. They contain no baseline/candidate conditional. RED must
  fail for the intended defect: anonymous association/spurious query for R-4, finite-prefix/no-raise
  for R-5, and duplicate count/regrouping for R-7. A setup, license, import, or unrelated assertion
  failure does not count.
- **OD-R32 [INFERRED]** The 31 current focused tests reported green by the historical spec review do
  not satisfy RED because all three defects remain. RED evidence comes from the new unchanged nodes,
  not from relabeling a current green baseline.
- **OD-R33 [INFERRED]** The affected regression union includes part-instance, occurrence round-trip,
  supplied-value, parameter-group, lowering/integrity, pipeline-threading, snapshot parity,
  generated execution, and migration mapping. Control-flow-sensitive focused tests run normally and
  under optimized Python; compatible full and licensed public-live suites run at the same candidate
  revisions. Basis: LC-I02, LC-I05, and the changed surfaces.
- **OD-R34 [INFERRED]** Item 1 evidence records exact revisions/locks, fixture, owner kind, source
  form/polarity, anonymity, actual source, occurrence/override shape, open predecessor rows, and
  public/private seam. It labels same-checkout replay non-certifying and leaves the relocated/full
  LC-I09 coordinate open for Items 5 and 13. Basis: LC-I09 and register row 1.
- **OD-R35 [INFERRED]** Per-occurrence override proof observes generated execution values and
  verdicts, not only distinct IDs or copied input records. Rationale: distinct wrappers can hide a
  shared-value collapse.

### E. Simplification, deletion, and production accounting

- **OD-R40 [INFERRED]** Implementation removes, rather than wraps, these superseded production
  control-flow paths:
  1. admission membership keyed by nullable `identity.qualified_name`;
  2. recursive revisit returning an empty occurrence subtree;
  3. unsupported owner reaching implicit package fallback;
  4. calc and constraint demands remaining independently actionable after target normalization; and
  5. last-write-wins `synth[target.qn]` deciding grouping provenance.
  Basis: R-4/R-5/R-7 and lifecycle epic Item 1 deletion scope.
- **OD-R41 [INFERRED]** Before the first production edit, evidence freezes the complete Item 0
  production manifest and this accounting rule: the measured scope is the union of every production
  file touched, added, moved, or deleted between OD-R30 sysml-codegen and the Item 1 candidate. The
  union cannot be narrowed after implementation. A new path has baseline LOC 0; a deleted path has
  candidate LOC 0; a move records the old path to 0 and the new path from 0.
- **OD-R42 [INFERRED]** Production counting follows Item 0's tracked `*.py`, `*.jinja2`, and lifecycle
  `*.sysml` rule. Tests, fixtures, generated output, docs, project artifacts, blank/comment-only
  reductions, and formatting churn are reported separately and cannot offset added production
  control flow. Basis: Item 0 evidence and the owner's simplification outcome.
- **OD-R43 [INFERRED]** The Item 1 default close gate is non-positive executable production LOC over
  OD-R41's frozen union. Any increase is surfaced with its reason and requires the owner-reviewed
  deviation mandated by the epic. This per-item gate is an agent bet supporting, but not upgrading,
  the owner's cross-remediation reduction outcome.
- **OD-R44 [INFERRED]** Closeout pairs LOC with structural evidence: before/after branch/complexity
  counts for every changed hotspot and a source/diff check proving each OD-R40 path absent. A lower
  comment count cannot hide more branches, a second materializer, or retained duplicate demand
  handling. Basis: spec-review finding L3-5.
- **OD-R45 [INFERRED]** Load-bearing docs/comments describe the landed association, owner filter,
  cycle atomicity, replay role, and target-normalized demand rules. Stale claims are amended or
  deleted without adding compensating prohibition prose. Basis: capture-fidelity correction law.

### Frozen Item 0 starting inventory

**[INFERRED] Accounting fixture for OD-R41.** This section is the pre-implementation freeze. These
known Item 1 files may not be removed from accounting, and implementation may not revise OD-R41's
union rule or baselines. Any additional production path enters automatically.

| Existing production file | Item 0 baseline LOC | Candidate rule |
|---|---:|---|
| `src/sysml_codegen/analysis/part_instance_index.py` | 447 | Actual candidate LOC; 0 if deleted/moved |
| `src/sysml_codegen/analysis/constraint_lowering.py` | 1,454 | Actual candidate LOC; 0 if deleted/moved |
| `src/sysml_codegen/resolution/supplied_values.py` | 332 | Actual candidate LOC; 0 if deleted/moved |
| `src/sysml_codegen/orchestration/pipeline_builder.py` | 1,051 | Actual candidate LOC; 0 if deleted/moved |
| `src/sysml_codegen/snapshot/graph_rebuild.py` | 243 | Actual candidate LOC; 0 if deleted/moved |
| **Known existing total** | **3,527** | Union closeout, never a post-hoc allowlist |

At freeze time, Item 1 has **0 new production files** and **0 deleted production files**. Every new
file enters with baseline 0. Every deleted file enters with candidate 0. Tests, fixtures, generated
output, docs, and project artifacts have separate ledgers.

## Mandatory Acceptance Cases

Requirements above are the single normative decision home. Each row below is an `[INFERRED]` proof
instrument and cites the requirements it tests; it does not create a second grade or precedence
rule.

| ID | Governing requirements | Case and required observation |
|---|---|---|
| OD-A01 | OD-R10–OD-R12 | Public live source has anonymous admitted and excluded usages with actual-shaped data and null QNs. Exactly one decision pairs with each usage. Only the admitted usage contributes demand. Deleting, duplicating, or reordering a decision, or changing list cardinality, fails before owner expansion. |
| OD-A02 | OD-R12–OD-R14 | An excluded/unsupported owner with a feature-reference actual causes zero `occurrences_of` calls, no demand, and one visible exclusion. A supported anonymous admitted owner still expands. Removing its required frozen owner entry fails as genuine corruption; retaining the valid transcript succeeds. |
| OD-A03 | OD-R02, OD-R16, OD-R26 | Existing finite multi-occurrence live fixture preserves exact ID/module/channel/catalog order and records one legitimate shared producer on every occurrence. Repeated live loads are byte-stable. |
| OD-A04 | OD-R02, OD-R35 | Public live sibling occurrences carry literal overrides on opposite sides of the predicate boundary. Generated execution returns the pinned distinct values and verdicts. |
| OD-A05 | OD-R03, OD-R15 | One queried owner has a finite branch listed before a recursive branch. Self-cycle, indirect-cycle, reversed feature order, reversed usage/index order, and repeated traversal all raise with the same structured cycle context. No owner result is returned or recorded; demand/materializer calls remain zero; no context, transcript, graph, catalog, or target bytes are produced or changed. |
| OD-A06 | OD-R03, OD-R16 | Parameterized, ranged, ordered, nonunique, unbounded, and unknown bounds retain loud owner/feature failures. Equal finite bounds, nested Cartesian shapes, subtype/retype/diamond dedup, same-name different-owner members, zero-count behavior, and multi-digit sibling order preserve their pinned finite observations. |
| OD-A07 | OD-R04, OD-R08, OD-R10, OD-R14, OD-R27 | A valid same-checkout capture/replay of the anonymous R-4 fixture matches live association, demand identity, grouping, counts, retained producer, and catalog values without a corruption diagnosis. The unsupported-owner exclusion fixture pins the exact warning byte sequence to `[]` on live and replay. The evidence is labeled non-certifying; no relocation/full-tree claim is made. |
| OD-A08 | OD-R20–OD-R22, OD-R25–OD-R27 | Shared calc/constraint target across files normalizes to one `_BindingTarget.qn`. Live and same-checkout replay both keep the calc-route group, process `scanned=1` and `applied=1`, synthesize/retain one producer, match catalog values, emit the exact INFO summary `supplied-value materializer scanned 1 referenced bindings: 1 literal applied, 0 non-literal skipped.`, and have an exact warning sequence of `[]`. Route and input reversal change nothing. Replay is non-certifying. |
| OD-A09 | OD-R20–OD-R27 | Constraint-only target normalizes/materializes once in public live and same-checkout replay. Both routes match target identity, chosen constraint-only group provenance, `scanned=1`, `applied=1`, the exact INFO summary `supplied-value materializer scanned 1 referenced bindings: 1 literal applied, 0 non-literal skipped.`, warning byte sequence `[]`, retained producer, and catalog values. Removing required group provenance fails under OD-R23 instead of dropping demand. Replay is non-certifying. |
| OD-A10 | OD-R20–OD-R25 | Multi-target fixture uses `DemandOrder__plant__source__a_collision`, `DemandOrder__plant__source__b_nonliteral`, and `DemandOrder__plant__source__c_clean`. Under calc/constraint route reversal and complete input-order reversal, normalized target order remains `[DemandOrder__plant__source__a_collision, DemandOrder__plant__source__b_nonliteral, DemandOrder__plant__source__c_clean]`; synthesized-QN order remains `[DemandOrder__plant__source__c_clean]`; counts remain `scanned=3`, `applied=2`, `non_literal_skips=1`. Exactly two warnings occur in order: `supplied-value materializer: a real design attribute already covers DemandOrder__plant__source__a_collision (source.a_collision); keeping the real value, skipping synthesis (REQ-SVM-03).` then `supplied-value materializer scanned 3 referenced bindings: 2 literal applied, 1 non-literal skipped (deferred: ['source.b_nonliteral']).` Live and same-checkout replay match. |
| OD-A11 | OD-R30–OD-R32 | New unchanged RED nodes `test_r4_live_anonymous_association`, `test_r4_valid_replay_not_corrupt`, `test_r5_finite_first_cycle_is_atomic`, `test_r7_shared_target_dedup_grouping_counts`, and `test_r7_multi_target_order_permutations` run at OD-R30. Each fails only for its named defect. The identical test bytes pass at candidate GREEN. The historical 31 green tests are recorded only as baseline regression evidence. |
| OD-A12 | OD-R06, OD-R33–OD-R35 | Public live row-1 cells pass at one candidate coordinate; focused normal/optimized, affected union, compatible full, and licensed live suites pass. Evidence names same-checkout replay as regression-only and leaves relocated/full LC-I09 cells open. |
| OD-A13 | OD-R40–OD-R44 | Frozen-union ledger reports every touched/new/moved/deleted production path, new=0 baseline/deleted=0 candidate treatment, executable LOC, branch/complexity movement, and OD-R40 deletion proof. Separate non-production ledgers cannot offset the result. |

## Explicit Agent Bets

This is a non-normative reviewer index. The requirement IDs above are the single decision home.
These bets remain challengeable even if design proceeds with them.

| Bet | Requirement | Default and rationale |
|---|---|---|
| Association mechanism | OD-R10–OD-R11 | Ordered pairing is acceptable only with cardinality plus exact identity/location cross-checks; an explicit key is also allowed. |
| Demand equivalence | OD-R20–OD-R21 | Equality is exact `_BindingTarget.qn` equality after the existing normalizer, before literal resolution. No Item 2 resolver work is absorbed. |
| Shared-target grouping | OD-R22 | Calc-route provenance wins so an added assertion cannot regroup an existing input. |
| Constraint-only provenance | OD-R23 | Use authoritative target provenance, then portable usage source; missing provenance fails loudly. |
| Demand order | OD-R25 | Ascending normalized target QN pins counts, warnings, and synthesized output order. |
| Cycle error shape | OD-R15 | One structured cycle failure family/path; exact class hierarchy remains a design choice. |
| Item close gate | OD-R41–OD-R44 | Frozen union, non-positive executable production LOC, and branch/duplicate-path evidence. |

## Non-Goals

- **[INHERITED]** The OD-R05 ownership boundaries are non-goals here: Item 2's shared resolver,
  Item 5's relocated/full-tree portability, and Item 13's composed artifact proof.
- **[INHERITED]** OD-R03 requires loud failure for unsupported cardinality; Item 1 does not make
  recursive, parameterized, variable, ordered, nonunique, or unbounded structures executable.
- **[INFERRED]** Consolidating all repository part-instance walkers. That broader architecture debt
  is unnecessary for Item 1 totality and remains separately tracked.
- **[INFERRED]** Redesigning eligible-anonymous compile grouping, same-location anonymous collision,
  or cross-version correlation. Those require identity contracts outside row 1.
- **[INHERITED]** Diagnostic severity/default fidelity, package trust, catalog/store transition,
  TEAx evidence durability, IFE, and stellarator acceptance. Source: later lifecycle register rows.

## Open Questions / Deferred to design

- **[INFERRED]** The concrete usage/decision association representation is open. OD-R10–OD-R11
  fix its observable contract and mutation behavior.
- **[INFERRED]** The demand record type and module placement are open. OD-R20–OD-R25 fix its
  normalization seam, provenance, precedence, and order.
- **[INFERRED]** The cycle exception class hierarchy and exact rendered prose are open. OD-R15
  fixes structured context and atomic behavior.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` — Item 1 and
  simplification mandate.
- **Normative architecture:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — invariants 16–18,
  proof standard, acceptance matrix, and register row 1.
- **Lifecycle requirements:** `.project/active/constraint-execution-lifecycle-contract/spec.md` —
  LC-D01–D04, LC-I08–I09, acceptance scenarios, and register row 1.
- **Primary defect research:**
  `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` — R-4/R-5/R-7.
- **Item 0 coordinate:** `.project/active/constraint-lifecycle-candidate-pin/evidence.md`.
- **Superseded inherited detail:** `.project/backlog/epic_constraint_pr_wave_remediation.md` — old
  Item 3 only.
- **Part-instance contract:**
  `.project/completed/20260713_part-instance-index/{spec,design,audit}.md`.
- **Constraint-lowering contract:**
  `.project/completed/20260713_constraint-lowering/{spec,design,audit}.md`.
- **Prior lowering integrity:** `.project/active/gap-lowering-integrity/{spec,design,evidence.md}`.
- **Historical spec review:**
  `.project/active/constraint-lifecycle-occurrence-demand/spec-review.md` — verdict **Revise**,
  preserved unchanged; this revision awaits independent re-review.
- **Design:** `.project/active/constraint-lifecycle-occurrence-demand/design.md` (to be created).

---

**Next Steps:** Re-run `my-spec-review` in a fresh session. Proceed to `my-design` only after the
revised contract is accepted.
