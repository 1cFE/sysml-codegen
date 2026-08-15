# Design: Authoritative Source-Identity Contract (SOURCE-IDENTITY Item 3)

**Status:** Final, audit certified and owner-ratified (rev 7 — 2026-08-07 audit corrections: the customer binding-context premise is
corrected (see Research Findings and A.8), C24/C25 added and aggregation C17/C26 split by explicit
D8 reopenings (counts 29/35), flagged coordinates made exact. Rev 5: owner decision checkpoint resolved 2026-08-05;
incorporates design_review_v4.md V4-M1..M5, V4-N1..N3; earlier closures per the v3/v4 audits)
**Owner:** Reid W
**Created:** 2026-08-05
**Branch:** `source-identity-epic` @ `5be8276`
**Spec:** `.project/active/source-identity-contract/spec.md` (post-review revision)
**Reviews:** `design-review.md` (v1), `design_review_v2.md` (v2), `design_review_v3.md` (v3),
`design_review_v4.md` (v4, Revise — authority + route-outcome architecture confirmed sound;
coordinate-enumeration findings addressed here)

## Overview

Item 3 turns the Item-1/Item-2 spike evidence and the recorded owner rulings into one authoritative
source-identity contract. This design says which artifact owns each kind of statement, defines a
deterministic scenario schema (referent-aware keys, derivation table, and exact enumeration in
Appendix A), and sequences the owner checkpoints. No code changes.

## Related Artifacts

- Spec: `spec.md` · Spec review (resolved): `spec-review.md` · Design reviews: `design-review.md`,
  `design_review_v2.md`, `design_review_v3.md`, `design_review_v4.md`
- Epic: `.project/backlog/epic_semantic_source_identity.md` (Item 3, lines 479–567)
- Evidence: Item-1 spike (`.project/active/source-identity-binding-semantics-spike/`), Item-2 spike
  (`.project/active/source-identity-route-evidence-spike/`), research log
  `.project/research/20260805-054752_source-identity-route-evidence.md`
- Amendment targets: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`,
  `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md` (frozen; durable
  copy per D6), `docs/architecture/verification-matrix.md`

## Research Findings

**The amendment targets already contain a home for every kind of statement Item 3 must record.**

- The ratified lifecycle contract has: numbered invariants 1–53 (19/20/22/26 are the amendment
  targets, `constraint-execution-authoritative-lifecycle-contract.md:176-195`), a correction
  register (Appendix B, `:386-408`), an owner-decision section using the `[OWNER-VERBATIM]` +
  `[AGENT]` option-referent pattern (D-1..D-3, `:284-306`), a proof-standard evidence coordinate
  (`:334-341`), and a mandatory acceptance matrix (Appendix C, `:410-462`, ~40 scenario rows).
- Precedent for inserting invariants without renumbering: invariant `46a` (`:255`).
- The companion spec carries the graded requirement-ID layer (`LC-A01`…`LC-I09`); its declared
  split with the contract is: behavioral authority in the contract, requirement IDs and provenance
  grades in the companion (`contract:15-25`).
- **`completed/` is an archive and audit trail** (`.project/completed/README.md:49-54`); the
  changelog records the companion spec as an archived deliverable
  (`.project/completed/CHANGELOG.md:92-100`). Historical path/line citations must keep resolving —
  the durable home therefore gets a *copy*, never a move (D6). Separately, the contract's
  `Requirements:` header (`:8`) points at the pre-archive path and is stale.
- The contract and archived companion carry **stale status prose** ("no certified implementation
  candidate exists", contract `:3,27-30`; "proof not established", companion `:47-56`). The
  correction must cite both the 41/41 composed-proof record
  (`.project/completed/20260720_constraint-lifecycle-composed-proof/release-readiness.md`) and the
  changelog's merged state (`CHANGELOG.md:74-100`) — the release record alone still says merge
  pending (V2-N1).
- **Eleven** verification rows are affected: the original REQ-CL-05,
  REQ-IR-06/07, REQ-SVM-01/02/04, and REQ-VBR-10 set, plus audit-discovered REQ-BT-13,
  REQ-IR-01, REQ-PGD-06, and REQ-VBR-03. The matrix is a
  test-traceability table (Status = "does a dedicated test exist and pass", `:1-23`); several rows
  are compound. Known drift mode is the Summary/Index counts.
- **Two distinct value mechanisms sit behind the SVM rows (V3-M4).** REQ-SVM-01's behavior is
  *synthesis*: after resolving a demand by precedence, materialize a design attribute carrying the
  value (`src/sysml_codegen/resolution/supplied_values.py:646-660`). The *reference→literal stamp*
  is a different, earlier mechanism — VBR tier 1
  (`src/sysml_codegen/orchestration/pipeline_builder.py:363-369`). The adjacent-work
  register permits synthesis to remain as a value adapter when it derives from the single identity
  authority (`.project/active/source-identity-route-evidence-spike/adjacent-work-register.md:16`).
- **Binding-owner context changes the semantic referent of the same written form (V4-M3,
  verified this revision).** The Item-1 probes author their calcs *inside the PartDef*
  (`form_control_renamed.sysml`: `calc c1` inside `part def 'Probe Plant'`), so the bare-renamed
  and def-qualified forms resolve to the **def-level** attribute (AFT rows 1c/2). The
  deep_cross_scope bindings are authored *inside the concrete `analyzer` part usage*, and all three
  resolve to the **occurrence-level** feature
  `DeepCrossScopeDesign::measurement_system::analyzer::baseline_value`
  (`tests/fixtures/deep_cross_scope_probe/design.sysml:63,71,83,92`;
  `extraction_snapshot.json:404,448,478`). RM9 is def-context: `in rep_rate = pulse_rate_ref`
  (`fusion_tea/designs/hif_ife/hif_driver.sysml:76`) sits inside `part def 'HIF Driver'` (`:6`)
  with the override on the usage (`:118`). Written spelling alone therefore cannot derive the
  referent — context is key material.
- **CORRECTED (2026-08-07 audit): the customer composition's binding contexts are mixed, not
  all usage-authored.** Rev 5 claimed every customer binding sits inside the concrete `hif_plant`
  usage; that was false. The concrete usage `hif_plant` (`hif_plant.sysml:8`) carries the `:>>`
  overrides (`:69` availability, `:100` thermal_efficiency) and exactly one usage-authored
  consumer binding (`meier_coe_calc`, `hif_plant.sysml:205,215`). The other consumers are
  def-authored inside `part def 'IFE Power Plant'`
  (`generic_ife/ife_plant.sysml:7`): `lcoe_calc` (`:98,114` availability, `:126`
  thermal_efficiency) and `recirc_calc` (`:134,148` thermal_efficiency). Consequence for
  checkpoint item 8: bare-renamed in place still holds per binding. C25 owns availability's exact
  mixed-context convergence; C2 owns thermal efficiency's two definition-authored legs; invariant
  56 owns convergence per source occurrence. C4 remains usage-context referent evidence. See A.8.
- **RM13's frozen `permitting.*` summary is overbroad, and it is not a genuine terminal-miss
  record (V4-M4).** The solar model declares the child part and its referenced cost features
  (`tests/fixtures/solar_battery_model/library.sysml:569-578,697-721`). Direct committed-graph
  evidence shows producer-backed `capital_cost` already uses one producer channel (C17 control).
  The raw parity evidence shows the three literal-valued features become per-consumer entry points
  (C26 contradiction). RM13 remains historical C26 evidence only; it is neither C17 evidence nor
  evidence about genuine absence.
- The L2 validation seam is exactly as the spec claims: `_owner_covers_name`
  (`../agentic-mbse/src/agentic_mbse/validation/level2_structure.py:309-355`), applied at `:402`,
  suppresses the self-binding error whenever a same-named attribute or sibling calc output exists.
  SI-15 is a semantic reversal of this predicate.
- No `.project/adr/` directory or `adr.sh` exists; decision records use the contract's correction
  register + D-x mechanism.
- The group-deriver backfill (fourth value authority) is at `graph_builder.py:620-630`; Item 3 only
  names it as a superseded reading (deletion is Item 5's, adjacent-work register row 5).

## Core Concept

Item 3 creates **no new normative document at all**. The ratified lifecycle contract stays the
single behavioral authority, and every statement Item 3 produces lands in the existing structure
built for that kind of statement:

| Statement kind | Sole normative home | Everyone else |
|---|---|---|
| Definitions + behavioral invariants | Contract (amended 19/20/22/26; new §"Source identity" 54+) | cites |
| Dispositions, rulings, provenance | Contract owner-decision section (source-identity disposition table, D-4 onward) | cites |
| Superseded readings | Contract Appendix B (new rows) | cites |
| Acceptance scenarios (target cells) | Contract Appendix C (new source-identity subsection; schema below) | cites |
| Graded requirement IDs (`LC-SI-*`) | Durable companion requirements copy (D6) | cites |
| Test state (does a test exist and pass) | Verification matrix — Status column untouched | n/a |
| Contract disposition of a test clause | Row-local annotation under the row's family table → Appendix C/B | n/a |
| Observed evidence | Item-1/Item-2 artifacts, frozen | cited as exhibits |

**Projection rule for `LC-SI-*` (V2-N3):** the contract owns all behavioral wording; each `LC-SI-*`
row carries its ID, provenance grade, source citation, and a one-line checkable summary that cites
the governing invariant/cell by number and never restates normative wording. The one-home grep
check is therefore mechanical: normative sentences exist once, in the contract.

The semantic spine everything projects:

- **Referent fidelity (SI-01/02/03):** a binding means what KerML resolution says it means; codegen
  and validation may support or reject a form, never reinterpret it. The referent depends on the
  written form **and the binding-owner context**: the same spelling resolves def-level from inside
  a definition and occurrence-level from inside a concrete usage (Research Findings).
- **Identity = declaration + concrete occurrence (SI-05/08):** the referent supplies declaration
  identity; the consumer's concrete featuring context supplies occurrence identity; no unique
  occurrence in context → named diagnostic, never a guess.
- **One occurrence, one runtime source (SI-09):** every and only the consumers of one semantic
  source occurrence resolve to its one public input or producer channel — regardless of which
  supported form each binding uses — proven by off-default mutation at the public boundary (SI-14).

**The matrix speaks at three named levels.** A *disposition family* is one authored-form ruling
covering all its variants — legitimate to collapse only where the referent is context-invariant
(the self-binding always resolves to the own formal; the rejected forms never resolve to a feature
identity). An *acceptance cell* is one complete R1 key with one expected boundary outcome. An
*evidence coordinate* is one full published SI-23 record — the certification unit. Grouping
headers organize the enumeration but are never counted; cells and coordinates are counted only
when complete (V4-M1).

## Key Bets

- **B1.** The classified Item-1/Item-2 evidence — with each observation assigned exactly one
  evidence role (direct observation, topology referent, principle-derived target, or blocked
  obligation) — is sufficient to fix every form disposition and every published target key/outcome
  without new probes. Closing a `BLOCKED` gap can certify or contradict HEAD but cannot change a
  recorded disposition or target. *If false → a disposition or target is wrong and the contract
  must reopen mid-Items-4/5.*
- **B2.** The contract's existing structures can host source-identity semantics as section
  extensions without strain — Appendix C already holds ~40 scenario rows of comparable shape, and
  the new subsection adds 29 cells. *If false → the subsection splits out as the sole scenario
  authority, an explicit surfaced change, not a quiet fork.*
- **B3.** Target behavior for every supported-form cell — including the cells whose correct
  boundary outcome is a diagnostic rather than a runtime source — is derivable now from referent
  semantics plus the identity principle, even where HEAD behavior is broken. *If false → Appendix A
  ships with undefined cells and Item 4 design stalls or invents semantics.*
- **B4.** The decision checkpoint's agenda items were decidable from the evidence already in hand;
  the 2026-08-05 resolution confirmed this bet without a new probe.

## Key Decisions

- **D1. Amend the existing contract; no standalone source-identity authority.** *Rejected: a new
  peer document (the competing-authority failure the epic's authority-chain gate exists to
  prevent).*
- **D2. Dispositions live in the contract's owner-decision section, not a separate
  `decision-register.md`.** A "Source-identity dispositions" table (D-4 onward) extends the
  existing D-1..D-3 pattern: ~16 rows, each with disposition, provenance grade (quote or
  ratification date), evidence citation, migration consequence. *Rejected: the epic's listed
  `decision-register.md` file (second normative decision home — duplication); item-folder home
  (archives rot).* The epic deliverable list now records the approved home (checkpoint item 1).
- **D3. New invariants append as a "Source identity" subsection numbered from 54,** after "Runtime
  and studies"; 19/20/22/26 amended in place. Document order and all citations of 1–53 survive.
  *Rejected: sub-letters at family scale (clumsy for ~6-8); renumbering (breaks citations).*
- **D4. Verification matrix: Status stays test-state; contract disposition is a row-local,
  clause-level annotation with the spec's exact vocabulary.** Each of the **eleven** affected rows
  gets its own annotation line directly under its family table, assigning the row exactly one of
  `SUPERSEDED`, `PARTIAL`, or `FAILED` and labeling every clause inside a `PARTIAL` row `stands` or
  `SUPERSEDED`, pointing to the owning Appendix C cell / Appendix B row. The clause map (drafted
  here, finalized at implement):
  - REQ-IR-06 — `SUPERSEDED`: minting for bound model references is impermissible; the QN-format
    clause survives only under the explicit external-input contract.
  - REQ-IR-07 — `PARTIAL`: the convergence requirement stands; evidence is route-specific.
  - REQ-SVM-01 — `PARTIAL` (V3-M4): the synthesis behavior — materialize the precedence-resolved
    literal as a design attribute (`supplied_values.py:646-660`) — stands as a value adapter once
    it derives from the single semantic identity authority (adjacent-work row 6); it is
    `SUPERSEDED` only as an independent identity authority. The reference→literal *stamp* is a
    different mechanism (VBR tier 1,
    `src/sysml_codegen/orchestration/pipeline_builder.py:363-369`); its superseded reading is an
    Appendix B row, not an SVM clause.
  - REQ-SVM-02 — `PARTIAL`: source-QN convergence direction stands; synthesis acting as an
    independent identity authority is `SUPERSEDED` (adjacent-work row 6).
  - REQ-SVM-04 — `PARTIAL` (V3-M4): the LITERAL-only application, skip-summary WARN, and
    no-silent-drop/V11-fall-through clauses all stand as value-adapter behavior; `SUPERSEDED` only
    insofar as tier matching by name/scope is read as an independent identity decision — the same
    authority boundary as SVM-01.
  - REQ-CL-05 — `PARTIAL`: dedup and producer-wiring clauses stand; the per-concrete-usage
    `LIBRARY_DEFAULT` scoping clause stands under checkpoint resolution 3's per-usage ruling.
  - REQ-VBR-10 — `PARTIAL` (V4-N1): the `_rewrite_specialized_chain` clause `stands` (test Status
    untouched); the `_rescue_self_named_bindings` clause is `SUPERSEDED`.
  - REQ-BT-13 — `PARTIAL`: loud, untruncated, non-silent failure `stands`; surfacing a bound miss
    as an entry point is `SUPERSEDED`.
  - REQ-IR-01 — `PARTIAL`: the STRICT terminal-miss raise clause `stands`; unconditional LENIENT
    minting for a bound reference is `SUPERSEDED`.
  - REQ-PGD-06 — `SUPERSEDED`: inline default resolution in group derivation is the fourth value
    authority recorded at D-18.
  - REQ-VBR-03 — `SUPERSEDED`: clearing the reference while stamping a literal is D-16's
    impermissible reference→literal identity mechanism.
  Row restructuring and test replacement are Item 6's. *Rejected: new Status values (conflates
  proof execution with contract disposition); a fifth column on all 276 rows (noise); backlog-only
  enumeration (spec requires the rows be marked).* Status values and Summary/Index counts are
  byte-identical before and after; the legend gains one line defining the annotation.
- **D5. Contract Appendix C is the sole scenario home; no separate `acceptance-matrix.md`.** The
  "Source-identity scenarios" subsection uses the deterministic schema below (Appendix A). The
  companion's scenario table gains one citation line, not a mirrored copy. *Rejected: a separate
  normative matrix file (third acceptance authority); evolving Item-2's `route-matrix.md`
  (observed-at-HEAD evidence stays frozen).* Confirmed by checkpoint item 1.
- **D6. Copy-and-freeze the companion spec; never move or amend the archive.** Copy
  `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md` to
  `.project/concepts/constraint-execution-lifecycle-requirements.md` with a provenance header
  ("copied from <archived path> at its close state; forward amendments happen here only"); the
  archived file stays **byte-for-byte intact**; the contract's stale `:8` pointer moves to the
  durable copy; `LC-SI-*` and the minimal LC-D06/D07/D09/E04B touch-ups land in the copy only.
  *Rejected: `git mv` + stub (breaks historical path/line citations — V2-M3); amending the archive
  in place (DR-M4); a fresh SI-only requirements file (splits the requirement-ID layer).*
  Confirmed by checkpoint item 2.
- **D7. Two checkpoints: the resolved decision checkpoint, then a ratification pass after
  drafting.** The decision checkpoint closed on 2026-08-05, before `/_my_plan`, because artifact
  homes and semantic rulings determine the file-level plan. Ratification of the assembled
  disposition table remains a separate, short pass at the end of implementation. The owner cannot
  ratify a table that does not exist yet (V2-M4). *Rejected: one checkpoint mid-implement with
  parameterized drafting (rev 1); one checkpoint that both decides and ratifies (internally
  impossible ordering).*
- **D8. Blocked cells publish their full target coordinate now; Item 4 realizes fixtures, never
  chooses semantics.** Every `BLOCKED` cell — ambiguity, cross-consumer, cross-owner, nested,
  shadowing, specialization, constructed terminal miss — carries a complete R1 key and expected
  boundary outcome in Appendix A; Item 4's obligation is a fixture realizing the published key. A
  genuinely new shape discovered downstream reopens the contract explicitly; it never edits the
  count silently. The 2026-08-07 audit-correction reopenings exercised this rule for C24, C25,
  and the C17/C26 source-topology split.
  *Rejected: rev-4's R6 placeholder families with Item-4 enumeration (delegated a
  semantics choice and made the authoritative count downstream-mutable — V4-M1/M2 and the spec's
  derivability criterion).*

## Architecture

```text
ratified lifecycle contract
  ├── definitions + invariants 19/20/22/26 amended, new 54+   (behavioral authority)
  ├── owner-decision section: source-identity dispositions     (who decided what)
  ├── Appendix B: new superseded-reading rows                  (corrections)
  ├── Appendix C: source-identity scenario subsection          (sole acceptance authority)
  └── names → durable companion requirements copy (LC-SI-*)    (graded IDs; projection rule)
        └── verification-matrix row-local annotations → Appendix C/B (clause dispositions;
            Status untouched)
Items 4–8 derive from the contract chain; obligations assigned by epic items
(L2 reversal → Item 4; guidance publication → Item 8; test replacement → Item 6).
```

**Disposition table rows** (closed population): forms — bare self-named, bare renamed,
owner-qualified, feature chain, `#(i)`, `[i]`; source classes — converged design attribute,
authored usage literal, unbound formal (C23, per-usage), multi-occurrence def default (ratified,
SI-05), aggregation term reference (absorbed, SI-10), expression binding (C22, deferred);
impermissible mechanisms — VBR stamp/rescue, lenient consumer-local mint, group-deriver backfill;
plus the `#(i)` extractor index-drop (adjacent-work row 7).

**Scenario schema.** Each Appendix C row carries three orthogonal fields:

- `form_disposition`: `SUPPORTED | UNSUPPORTED | LANGUAGE_REJECTED | PENDING_CHECKPOINT |
  DEFERRED(owner, date)` — the contract's ruling on the authored form or source class. `DEFERRED`
  is the terminal state for a checkpoint class the owner explicitly defers (V4-M2);
  `PENDING_CHECKPOINT` cannot survive Item-3 close.
- `expected_boundary_outcome`: `RUNTIME_SOURCE | AUTHORING_DIAGNOSTIC | AMBIGUITY_DIAGNOSTIC |
  POLICY_DIAGNOSTIC | LOAD_ERROR` — what the executable boundary must do for this cell's topology.
  Route and mutation obligations derive from this field alone (R5).
- `certification_state`: `UNPROVEN | CONTRADICTED_AT_HEAD | BLOCKED(<missing evidence> → <owning
  item>) | CERTIFIED` — the proof status. At Item-3 close, no cell is `CERTIFIED`.

Derivation rules:

- **R1 — Cell key** = (authored form, **semantic referent class** — fixed by form + binding-owner
  context per the published referent table (A.2), or the exact per-binding referent/context tuple
  when one source is consumed across contexts, source-topology class, consumer-mix class, value
  state). Cells exist only where a source in the A.4 inventory produces the key; no Cartesian
  enumeration. Where one source's consumers bind it through different forms (RM12), each form
  observation is cited at its own form's cell; SI-09 spans them — convergence is per source
  occurrence, across forms.
- **R2 — Family collapse, pre-source outcomes only:** legitimate when the boundary ends before a
  runtime source exists and topology cannot change that outcome. This covers the three unsupported /
  language-rejected forms because their referent behavior is context-invariant (self-binding always
  denotes the own formal; `#(i)` carries value semantics only; `[i]` never resolves). It also covers
  C22: the deferred expression-binding class always stops at readiness validation, before operand
  topology or consumer mix can affect source behavior. Observed variants become coordinate subrows
  only when they carry distinct evidence roles; C22's seven-EP census is population evidence, while
  its one kept readiness fixture is the proof coordinate. Supported runtime forms never collapse
  (V4-M1).
- **R3 — Merge rule:** two sources producing one key merge into one cell carrying all citations.
- **R4 — Gaps are fields, not cells:** missing evidence lands in `certification_state` on the
  affected cells with the owning item named. Off-default mutation evidence is owed by **every
  `RUNTIME_SOURCE` cell** and is Item 6's.
- **R5 — Route and mutation applicability follow the boundary outcome:**

  | `expected_boundary_outcome` | live route | snapshot/replay | off-default mutation |
  |---|---|---|---|
  | `RUNTIME_SOURCE` | one public source | full `live = snapshot = relocated` parity (SI-13) | required (SI-14) |
  | `AUTHORING_DIAGNOSTIC` | blocking diagnostic before generation; codegen independently fail-closed (SI-17) | capture refuses | N/A |
  | `AMBIGUITY_DIAGNOSTIC` | named diagnostic before a source exists (SI-05/08) | same diagnostic on any route that reaches resolution; no route yields a source | N/A |
  | `POLICY_DIAGNOSTIC` | exact per-policy outcomes stated in the cell (V4-N3); never a mint or same-named candidate (SI-12) | same disposition on any route that reaches resolution | N/A |
  | `LOAD_ERROR` | load fails | N/A — everything downstream ends at load | N/A |

- **R6 — Counting:** cells = complete R1 keys (an R2 family is one cell); evidence coordinates =
  complete SI-23 records (family subrows count individually); grouping headers are never counted
  as cells. C22/C23 resolve the former checkpoint classes; the count changes only by explicit
  contract reopening (D8) — exercised on 2026-08-07 for audit-F1 → C24, the exact customer
  mixed-context correction → C25, and aggregation topology exactness → C17/C26 (A.8).

Applying R1–R6 to the A.4 inventory yields **29 concrete acceptance cells and 35 concrete
evidence coordinates** (26/32 at the resolved checkpoint; +C24/C25 and the C17/C26 split by the
2026-08-07 reopenings). The
derivation table (A.4) maps every source to exactly one evidence role; the audit re-derives the
enumeration and both counts from it.

**Representative cells — the paired customer acceptance.** The epic requires the original form to
fail and the migrated form to converge (`epic:147-150`). The customer has two source occurrences.
`availability` has one usage-authored and one definition-authored consumer, so its exact migrated
target is C25. `thermal_efficiency` has two definition-authored consumers, so its target is C2.
SRC-01b owns the original self-bound form for both sources. C4 remains the two-usage-consumer DCS
coordinate that supplies usage-context referent evidence; it is not the customer coordinate:

> **SRC-01b** (coordinate subrow of the bare-self-named family) · form: bare self-named
> `in availability = availability` · referent: own formal (context-invariant) · topology: PartDef
> attr on `'IFE Power Plant'`, occurrence `:>>` override at `hif_plant`; binding contexts
> **mixed** (rev 6 correction, A.8): `meier_coe_calc` usage-authored (`hif_plant.sysml:205,215`),
> `lcoe_calc`/`recirc_calc` def-authored (`generic_ife/ife_plant.sysml:98,114,126,134,148`) ·
> consumers: 2 calcs per source occurrence · `UNSUPPORTED` · `AUTHORING_DIAGNOSTIC` — blocking L2
> diagnostic (SI-15), codegen fail-closed (SI-17) · `CONTRADICTED_AT_HEAD` (RM 2) · paired
> acceptance spanning C25 (availability) and C2 (thermal_efficiency).
>
> **C25** · form: bare renamed in mixed usage/definition binding-owner contexts · referents:
> occurrence-level on the usage-authored leg and def-level plus occurrence bridge on the
> definition-authored leg · topology: `hif_plant.availability`, occurrence `:>>` override ·
> consumers: 2 calculations, one in each context · `SUPPORTED` · `RUNTIME_SOURCE` — one public
> input and two consumer edges; off-default mutation reaches both · `BLOCKED` on the supported-form
> fixture/migration and public mutation evidence (Items 4/6) · cites epic `:147-150`, the exact HIF
> and generic IFE fixture lines, AFT 1c, and DCS referent evidence. Checkpoint resolution 8 ratified
> the bare-renamed-in-place recommendation. Its C4/no-count-change placement was agent-authored and
> depended on the false all-usage-context premise; C25 is the evidence-driven correction, pending
> final owner ratification with the assembled table.

**Owner decision checkpoint — resolved 2026-08-05.** After the eight recommendations and their
tradeoffs were presented individually, the owner replied: `[OWNER-VERBATIM]` “ok agreed with each
one”

The recommendations remain `[AGENT] (ratified by owner, 2026-08-05)`; ratification does not upgrade
their provenance:

1. **Artifact homes (D2/D5):** decisions and matrix stay in the contract; update the epic's
   deliverable list.
2. **Companion durable home (D6):** copy-and-freeze to
   `.project/concepts/constraint-execution-lifecycle-requirements.md`; archive untouched.
3. **Unbound calc-def input defaults:** one independently overridable `LIBRARY_DEFAULT` source per
   concrete usage; no unmodeled sharing. PC-2 resolves to C23.
4. **Expression-binding sources:** explicitly deferred; add a fail-closed readiness diagnostic.
   PC-1 resolves to C22 with `DEFERRED(owner, 2026-08-05)`.
5. **Evidence gaps:** Item 4 owns fixtures for every published `BLOCKED` key; it proves the target
   and does not choose semantics.
6. **Aggregation finding:** file it as absorbed by this epic; calculations, constraints, and
   aggregations share the same identity authority.
7. **Stale status:** reconcile the full contract and companion status sections against both the
   41/41 release record and merged-state changelog.
8. **Customer migration:** bare-renamed in place (for example,
   `in availability_in = availability`). The owner ratified the form recommendation. The
   agent-authored C4/no-count-change placement depended on the false all-usage-context premise and
   was re-derived after audit: C25 owns mixed-context availability; C2 owns def-only
   thermal-efficiency. The corrected placement remains agent-grade pending final ratification.

*Ratification pass — end of implementation:* the owner ratifies the assembled, provenance-graded
disposition table and the Appendix C subsection built from these decisions.

## Required Invariants

- One normative home per statement kind, exactly as the ownership table states; every other
  appearance is a citation (`LC-SI-*` rows follow the projection rule). Audit greps the amendments
  for restated rules.
- Provenance grades survive every hop unchanged; owner approval of an agent recommendation never
  becomes owner origin.
- Item 3 records only: recorded owner rulings, ratified agent recommendations, standards-forced
  meaning, and checkpoint outcomes.
- Every superseded reading gets exactly one Appendix B row, phrased as a decision record, never as
  an instruction.
- Verification-matrix Status values and Summary/Index counts are byte-identical before and after.
  Every affected row's annotation assigns the row exactly one of `SUPERSEDED`/`PARTIAL`/`FAILED`;
  inside a `PARTIAL` row every clause is explicitly labeled `stands` or `SUPERSEDED` (V3-N3).
- Every evidence citation matches the cell key it certifies in authored form, semantic referent
  (binding-owner context), topology, and consumer mix; an unobserved composition is never
  certified from an adjacent observation; each source has exactly one evidence role (V3-M3/V4-M3).
- The Appendix A derivation table, enumeration, and counts change only together, in the same edit;
  after the resolved checkpoint, only explicit contract reopening changes them (D8/R6).
- Owner payloads verbatim at their correct homes: the SI-01 ruling quote; the SI-15/SI-16
  validation-stack request ("Can we add that (and probably the `in.R=R`) pattern…"); the SI-18
  documentation quote **including the preserved "quesiton" typo** (SI-18's payload, not SI-15/16's).

## Component Overview

| Artifact | Home | Action | Carries |
|---|---|---|---|
| Lifecycle contract | `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` | amend | Definitions; inv 19/20/22/26 + new 54+; disposition table (D-4+); Appendix B rows; Appendix C subsection (29 cells / 35 coordinates); pointer + status fixes |
| Companion requirements (durable) | `.project/concepts/constraint-execution-lifecycle-requirements.md` | new (copy) | Provenance header; `LC-SI-*` family; minimal LC-D06/D07/D09/E04B touch-ups; scenario citation line |
| Archived companion | `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md` | **untouched** | Frozen close-state audit trail |
| Verification matrix | `docs/architecture/verification-matrix.md` | amend | Row-local clause annotations on 11 rows; one legend line; Status/counts untouched |
| Epic Item 3 | `.project/backlog/epic_semantic_source_identity.md` | amend | Deliverable list updated to checkpoint-approved homes |
| plan.md | item folder | new | Post-checkpoint sequence; SI-xx → edit traceability table (incl. payload-placement and clause-vocabulary checks) |

## Non-Goals

- No implementation: no validator change, no source-ID type/field names, no diagnostic enum names,
  no snapshot layout, no fixture/corpus migration (spec Non-Goals; Items 4–8).
- No edits to Item-1/Item-2 evidence artifacts or to any `completed/` file; frozen exhibits and
  archives stay byte-identical.
- No verification-matrix row restructuring or test deletion — Item 6 replaces tests; Item 3 only
  annotates.
- No general documentation projection — Item 8 publishes; Item 3 defines required content
  (SI-18/19) inside the contract.
- No new ADR store; decision records use the contract's register/D-x mechanism.

## Implementation Notes

- **Sequence:** `/_my_plan` → disposition table → Appendix C rows (from Appendix A) → invariant amendments +
  definitions → companion copy + `LC-SI-*` → verification annotations → derivability dry-run →
  consistency sweep → ratification pass.
- SI-16's diagnostic wording constraint ("valid SysML, unsupported by this executable subset —
  never 'invalid SysML'") belongs in the invariant text, not just a cell, so Item 4 can't lose it.
- SI-09's cross-form convergence obligation belongs in the invariant text: certification is
  per-form-cell, but convergence is per source occurrence across all its consumers regardless of
  which supported form each binding uses (RM12 is the concrete case).
- The binding-owner-context referent table (A.2) belongs in the contract's definitions — it is the
  semantic fact the whole key system rests on.
- The 37-fixture recapture, `snapshot_format_version` bump, and companion-repo regeneration
  obligations (SI-13) enter the contract as Item-4/6 obligations with the Item-2 blast-radius
  citation, scope neither softened nor restated.
- The companion copy's provenance header names the archived source path and close state; the
  contract's pointer fix and the copy land in one commit.
- Every amended contract line must be attributable to a specific SI requirement or checkpoint
  outcome — the plan's traceability table enforces this and carries the payload-placement (DR-M5)
  and clause-vocabulary (V2-M5/V3-N3) checks.

## Potential Risks

- **Amendment churn on a ratified artifact** — bounded by the traceability table, additive 54+
  numbering, and the one-home rule; audit diff-reads the contract against the SI list.
- **Grade laundering during absorption** — audit re-runs the absorb mapping over every disposition
  row and `LC-SI-*` row.
- **Appendix C outgrows the contract** — 29 cells atop ~40 existing rows is within precedent; B2's
  failure branch (explicit split-out) covers the surprise case.
- **Items 4/5 still find a semantics hole** — the derivability dry-run is the tripwire; a later
  hole reopens the contract explicitly (D8), never gets patched downstream.

## Integration Strategy

Item 3 sits between the completed evidence spikes and all implementation items. Its outputs are
read-only inputs to Items 4–8: Item 4 consumes the identity/occurrence semantics, validation
obligations, and the published `BLOCKED` target coordinates (fixtures realize keys, D8); Item 5
the impermissible-mechanism rows; Item 6 the Appendix C rows (all RUNTIME_SOURCE cells owe it
mutation evidence) and annotated verification rows; Item 7 inherits via 4–6; Item 8 the
guidance-content definition and certification-correction pointers. The epic's Item-3 deliverable
  list changes under D2/D5/D6 — updated with the checkpoint resolution, in the same change.

## Validation Approach

- **Traceability:** every SI-01…SI-23 maps to ≥1 concrete artifact edit and every edit back to an
  SI requirement or checkpoint outcome; includes the payload-placement and clause-vocabulary
  checks.
- **Enumeration re-derivation:** apply R1–R6 to the six source categories via the A.4 derivation
  table and confirm the cells, coordinates, and counts (28 / 34)
  exactly; confirm every route-matrix row, authoring form, census class, blocked bullet, and
  checkpoint class appears with exactly one evidence role.
- **Evidence-fidelity audit (V3-M3/V4-M3):** for every citation, confirm the cited observation's
  authored form, binding-owner context/referent, topology, and consumer mix match the cell key it
  certifies.
- **One-home check:** grep amendments for restated rules; `LC-SI-*` rows must cite, not restate.
- **Provenance audit:** re-derive every grade from its source; zero upgrades.
- **Derivability dry-run:** for each Item-4 and Item-5 scope bullet in the epic, name the contract
  statement that answers it; an unanswered bullet is a gap to close before Item 3 ships.
- **Mechanical gates:** verification-matrix Status/count byte-check; archive byte-identity check on
  the untouched companion; link check on every touched path.
- Then `/_my_audit` per the workflow.

## Next-Stage Handoff

- **Fixed:** the ownership table + projection rule; the amendment approach; the disposition-row
  population; the three-field cell schema with referent-aware keys, derivation rules R1–R6, and
  the Appendix A derivation table + enumeration; clause-level verification annotations with exact
  vocabulary; copy-and-freeze migration; resolved-decision/final-ratification sequencing; D8's
  published-target rule for blocked cells.
- **Resolved (decision checkpoint):** all eight `[AGENT]` recommendations ratified by the owner on
  2026-08-05; PC-1 → C22, PC-2 → C23, and the customer's bare-renamed migration form was
  ratified. The audit re-derived its exact evidence homes as C25 + C2. Counts were fixed at 26/32
  at the checkpoint and reopened under D8 on
  2026-08-07 for audit-F1 → C24, the exact customer shape → C25, and aggregation's distinct
  producer/literal topologies → C17/C26; now 29/35 (A.8).
- **Closed:** the corrected chain was audit-certified and owner-ratified on 2026-08-07. Appendix A
  and its counts change only by explicit D8 reopening.

---

## Appendix A — Scenario derivation and cell enumeration (binding; excluded from main-body budget)

Abbreviations: RM n = Item-2 route-matrix row n (`route-matrix.md`); AFT n = Item-1
authoring-form-table form n (`authoring-form-table.md`); DCS =
`tests/fixtures/deep_cross_scope_probe/design.sysml`; NOP =
`tests/fixtures/nested_occurrence_override_probe/model.sysml`; HIF =
`tests/fixtures/fusion_tea/designs/hif_ife/`.

### A.1 Evidence-coordinate row schema (SI-23)

Every counted row (concrete cell or family subrow) publishes these fields. "Family" locality means
stated once at the family row and inherited by subrows; "derived" means fixed by another field via
a published rule (restated only on exception).

| # | Field | SI-23 coordinate | Locality |
|---|---|---|---|
| 1 | `cell_id` | — | row-local |
| 2 | `authored_form` — vocabulary (V4-M2): bare self-named / bare renamed / owner-qualified / feature chain / `#(i)` / `[i]` / authored literal (no written reference) / expression binding / none (unbound formal) / aggregation-term dotted reference | authored form | row-local (family rows name the form; subrows cite exact bindings) |
| 3 | `semantic_referent` — own formal / def-level feature / occurrence-level feature / value expression / none, or an exact per-binding tuple of these for one source consumed across contexts — **key material**, fixed by form + binding-owner context per A.2 (V4-M3) | semantic referent | row-local |
| 4 | `declaration_identity` (owner kind + declaration site) | declaration identity | row-local |
| 5 | `concrete_occurrence` (single / multi / cross-part / cross-owner / nested; binding-owner context) | concrete occurrence | row-local |
| 6 | `value_state` (def default / occurrence override / authored literal / library default / value at source / absent) | override/default state | row-local |
| 7 | `consumer_mix` (types + count) | consumer type and count | row-local |
| 8 | `form_disposition` | — (schema field) | family |
| 9 | `expected_boundary_outcome` | — (schema field) | row-local |
| 10 | `expected_public_topology` (exact public-source shape, or "none") | expected public-source topology | row-local |
| 11 | `diagnostic_disposition` (named diagnostic + wording constraint, or "none"; `POLICY_DIAGNOSTIC` cells state both policy outcomes — V4-N3) | diagnostic disposition | row-local; SI-16 wording constraint inherited from the invariant |
| 12 | `execution_routes` | execution route | derived from field 9 via R5 |
| 13 | `mutation_result` (expected off-default observation, or N/A per R5) | off-default mutation result | row-local for `RUNTIME_SOURCE` cells; derived N/A otherwise |
| 14 | `certification_state` (+ owed evidence → owning item) | — (schema field) | row-local |
| 15 | `citations` (RM row / AFT form / fixture file:line / census class / ruling) | — (evidence) | row-local |

The checkpoint-resolved classes in A.5 publish all 15 fields through their C22/C23 rows. No
pending class remains outside the counted matrix.

### A.2 Referent table (form × binding-owner context → semantic referent)

Verified sources: AFT evidence table (def-context probes); DCS snapshot QNs
(`extraction_snapshot.json:404,448,478`); RM9 context (`HIF hif_driver.sysml:6,76,118`).

| Form | Authored inside the definition | Authored inside a concrete usage |
|---|---|---|
| bare self-named | own formal (context-invariant — nearest scope is the calc's own parameter) | own formal (context-invariant) |
| bare renamed | **def-level feature** (AFT 1c) | **occurrence-level feature** (DCS:71,83) |
| owner-qualified | def-level feature — def qualifier (AFT 2) | occurrence-level feature — usage qualifier (DCS:92) |
| feature chain | occurrence-level: the redefining feature at the named occurrence (AFT 3) | same, rooted at the named nested occurrence (NOP:22,25) |
| `#(i)` / `[i]` | value expression / unresolvable (context-invariant) | same |

### A.3 Row enumeration

Grouping headers are organizational only (R6). Fields 3/12 and N/A mutation entries derive per
A.1/A.2/R5. Every `RUNTIME_SOURCE` cell owes off-default mutation evidence to Item 6 (R4) and full
route parity (R5); not repeated per row.

**Unsupported and language-rejected forms (R2 families — 3 cells, 9 coordinates):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| SRC-01 | bare self-named `in R = R` × any topology (referent: own formal, context-invariant) | AUTHORING_DIAGNOSTIC — blocking L2 diagnostic (SI-15); codegen fail-closed (SI-17) | CONTRADICTED_AT_HEAD; corpus ~124 external + 91 fixture self-binding occurrences; the 75 model-derived mints are the broader affected population (V3-N2) |
| — 01a | PartDef attr, usage-context binding, occ `:>>` override × 2 calcs + constraint | ″ | RM 1 (fusion_tea `gain`: 3 public fields at HEAD) |
| — 01b | PartDef attr (`'IFE Power Plant'`), occ `:>>` override at `hif_plant`, **mixed binding contexts** (usage: `hif_plant.sysml:205,215`; def: `generic_ife/ife_plant.sysml:98,114,126,134,148` — A.8) × 2 calcs per source | ″ | RM 2 (`thermal_efficiency`, `availability`); **paired w/ C25 + C2** |
| — 01c | PartDef attr, def default × 2 calcs, one occ | ″ | RM 3 (ife `bank_energy`) |
| — 01d | PartDef attr, def default × 1 calc | ″ | RM 4 (ife `gain`, self_named_binding_trap) |
| — 01e | PartUsage-owned attr, usage literal × calc + constraint | ″ | RM 5 (shared_producer; converges at HEAD — control) |
| — 01f | parent-part attr, cross-owner × agg/constraint + child calc | ″ | RM 7 (solar `pack_count`: 2 fields at HEAD) |
| — 01g | two occurrences, def defaults × per-occ calcs | ″ | RM 10 (ife chambers; driver pair) |
| SRC-02 | `#(i)` indexed value expression as source binding (referent: value expression) | AUTHORING_DIAGNOSTIC — distinct readiness diagnostic; valid-SysML wording (SI-16); index never silently dropped | — |
| — 02a | PartDef attr, def-context binding, occ override × 2 calcs (probe `form_bracket_hash.sysml`) | ″ | CONTRADICTED_AT_HEAD (AFT 4a: extractor silently drops the index); zero corpus prevalence |
| SRC-03 | `[i]` bracketed (referent: unresolvable) | LOAD_ERROR — routes end at load (R5) | — |
| — 03a | PartDef attr, def-context binding, occ override × 2 calcs (probe `form_bracket_sq.sysml`) | ″ | UNPROVEN (kept negative cell → Item 6); AFT 4b — HEAD already behaves correctly |

**Supported forms, def-context (referent: def-level feature; occurrence bridge required):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C1 | bare renamed × def-context × single-occ `:>>` override × 1 calc | RUNTIME_SOURCE — one source; override value observed | CONTRADICTED_AT_HEAD (RM 9 stamp: `rep_rate` ← `pulse_rate_ref`, `HIF hif_driver.sysml:76,118`) |
| C2 | bare renamed × def-context × single-occ `:>>` override × 2 calcs | RUNTIME_SOURCE — both consumers converge on the one source | UNPROVEN (pipeline + mutation legs → Item 6); AFT 1c probe |
| C3 | owner-qualified (def qualifier) × def-context × single-occ `:>>` override × 2 calcs | RUNTIME_SOURCE — def referent + occurrence bridge → the one occurrence's value | UNPROVEN (pipeline + mutation legs → Item 6); AFT 2 probe; population: 85 fixture-corpus qualified bindings (contexts/states unenumerated) |

**Supported forms, usage-context (referent: occurrence-level feature):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C4 | bare renamed × usage-context × single-occ `:>>` override × 2 calcs | RUNTIME_SOURCE — one public input under occurrence identity | CONTRADICTED_AT_HEAD (DCS:71,83 stamped per-consumer; snapshot referent QNs :404,448); usage-context referent evidence for C25, not itself the one-usage/one-definition-context customer key |
| C5 | owner-qualified (usage qualifier) × usage-context × single-occ `:>>` override × 1 calc | RUNTIME_SOURCE — one source; occurrence referent direct | CONTRADICTED_AT_HEAD (DCS:92 stamped; snapshot :478) |
| C6 | feature chain (sibling context, occurrence-rooted) × single-occ `:>>` override × 2 calcs | RUNTIME_SOURCE — one source at the redefining feature | UNPROVEN (mutation → Item 6); AFT 3 probe |

**Supported forms, multi-occurrence (SI-05):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C7 | chain per occurrence × two occurrences, **equal defaults** × 1 calc per occurrence (2 calcs) | RUNTIME_SOURCE — distinct sources per occurrence; equal values never collapse; mutating one leaves others | UNPROVEN; SI-05 ruling; RM 10 topology; census multi-occ sharing note; catf `inner_radius` resolved by final census → Item 6 |
| C8 | chain per occurrence × two occurrences, **distinct overrides** × 1 calc per occurrence (2 calcs) | RUNTIME_SOURCE — each occurrence's value observed by its consumers only | UNPROVEN; Item-4 foundation; lifecycle Appendix C "Per-occurrence distinct overrides" kin row |

**Ambiguity cells (def-level referent, no unique occurrence in context):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C9 | owner-qualified (def qualifier) × two-occ context, def default × 1 calc | AMBIGUITY_DIAGNOSTIC — named diagnostic; never a guess (SI-05/08); no source on any route | BLOCKED(two-occ def-referent fixture realizing this key → Item 4); AFT uncertainty register; sysml_ruling residual ambiguity |
| C10 | bare renamed × def-context × two-occ context, def default × 1 calc | AMBIGUITY_DIAGNOSTIC — same | BLOCKED(fixture → Item 4); AFT 1c referent class |

**Cross-consumer cells (single-occ override; calc + constraint + aggregation), one per supported
form (spec `:43-45`; V4-M5):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C11 | feature chain × mixed consumers | RUNTIME_SOURCE — one source; all consumer types converge (SI-09/10) | BLOCKED(cross-consumer fixture → Item 4); nearest controls RM 5/6 (controls, not observations of this key) |
| C12 | owner-qualified (def qualifier) × mixed consumers | RUNTIME_SOURCE — same via occurrence bridge | BLOCKED(cross-consumer fixture → Item 4) |
| C13 | bare renamed (usage-context) × mixed consumers | RUNTIME_SOURCE — same via occurrence referent | BLOCKED(cross-consumer fixture → Item 4) |

**Cross-part / cross-owner:**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C14 | dotted chain × cross-part, value at source × 2 calcs (renamed formals) | RUNTIME_SOURCE — converged public field whose identity **derives from the one authority**, not parallel synthesis | UNPROVEN (authority derivation → Items 4/5); RM 6 (convergence topology observed; carried today by SVM synthesis — adjacent-work row 6) |
| C15 | chain × cross-owner (parent attr, occ override; 1 parent agg + 1 parent constraint + 1 child calc) | RUNTIME_SOURCE — one source across owners; mutation reaches all | BLOCKED(cross-owner supported-form fixture → Item 4); census cross-owner unknown class; topology kin RM 7 (observed only in the unsupported form → 01f) |

**Computed source (producer channel) — added 2026-08-07 by the audit-F1 reopening (A.8):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C24 | feature chain terminating at calc-def output `'Source Identity Producer'::result` on calculation usage `source_identity_computed.producer_calc` × single occurrence × 1 calc + 1 constraint + 1 agg | RUNTIME_SOURCE — one producer channel; every consumer wires to it; no public input minted for a computed value; upstream-input mutation reaches all three through the one channel | BLOCKED(computed-source mixed-consumer fixture → Item 4); epic mission invariant (owner); lifecycle "Producer-channel actual" kin row; REQ-IR-07/REQ-CL-05 producer-wiring clauses (route-specific controls) |

**Mixed binding-owner contexts (exact customer migration target):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C25 | bare renamed × mixed usage/definition binding contexts × single-occ `:>>` override × 2 calcs (1 usage-authored + 1 def-authored) | RUNTIME_SOURCE — occurrence-level usage referent and def-level referent plus occurrence bridge converge on one public input at the same source occurrence | BLOCKED(mixed-context supported-form fixture → Item 4; customer migration + public mutation → Item 6); exact HIF/generic IFE fixture lines; AFT 1c + DCS referent classes; epic `:147-150` |

**Literals and aggregation:**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C16 | authored usage literals (two; no written reference), equal values × 1 calc each | RUNTIME_SOURCE — distinct independent sources (SI-11); discriminator `written_reference is None`; mutating one leaves the other | UNPROVEN (mutation → Item 6); RM 8 |
| C17 | aggregation-term dotted reference to producer-backed `permitting.capital_cost` × 1 aggregation | RUNTIME_SOURCE — one producer channel reaches the aggregation; zero public inputs; no per-term mint (SI-10) | UNPROVEN (full route + mutation → Item 6); HEAD baseline already wires the term to `permitting__cost_model__total_cost` (`computation_graph.json:2695-2702`) |
| C26 | aggregation-term dotted references to three literal-valued modeled `permitting` cost features × one concrete child occurrence × 1 aggregation per source | RUNTIME_SOURCE — three independent public inputs, one per literal-backed source; no producer channel and no per-term mint (SI-10) | CONTRADICTED_AT_HEAD (RM 13: `library.sysml:576-578,697-721`; parity evidence shows three per-consumer mints — literal-backed evidence coordinate) |
| C18 | aggregation-term reference, **target genuinely absent** × aggregation consumer | POLICY_DIAGNOSTIC (V4-N3): strict → named pre-generation failure identifying the term; lenient → named diagnostic, the term contributes no source, no minted input, no same-named capture (SI-12) | BLOCKED(constructed genuine-miss fixture → Item 4); no observed evidence — RM 13 does not qualify (V4-M4) |

**Nested, shadowing, specialization (published target coordinates — D8):**

| ID | Key | Boundary outcome → target | Certification · citations |
|---|---|---|---|
| C19 | chain (`source.reading`, NOP:22,25) × nested-occurrence `:>>` override (NOP:37) × calc + constraint | RUNTIME_SOURCE — override (80.0) applies on both paths; tripwire silent | BLOCKED(live leg → Item 4; capture halts by design); adjacent-work row 2 |
| C20 | shadowing: bare renamed × an intervening same-named declaration between the consumer scope and the intended attribute | RUNTIME_SOURCE **at the KerML nearest-scope referent** (SI-02); no name-coincidence capture across the shadow | BLOCKED(fixture realizing this key → Item 4); census ambiguity count of zero is not proof of none |
| C21 | specialization: chain through a retyped usage whose specialized def carries `:>>` | RUNTIME_SOURCE — the redefining (specialized) value at that occurrence; the general feature is not a separate source (SI-03/04) | BLOCKED(fixture → Item 4); kin: REQ-VBR-10 `stands` clause (`spec_chain_channel` family) |

**Checkpoint-resolved classes (`[AGENT]`, ratified by owner 2026-08-05):**

| ID | Key | Form disposition | Boundary outcome → target | Certification · citations |
|---|---|---|---|---|
| C22 | expression binding × value-expression referent × any operand/topology variant at a source-identity-required boundary (R2 family) | `DEFERRED(owner, 2026-08-05)` | AUTHORING_DIAGNOSTIC — fail-closed codegen-readiness diagnostic; no flattening and no invented source | UNPROVEN (one kept readiness coordinate → Items 4/6); census expression class (7 EP population); `expression_binding_probe`, `plant_value_shapes`; checkpoint resolution 4 |
| C23 | none (unbound formal) × calculation-definition default × one concrete calculation usage | `SUPPORTED` | RUNTIME_SOURCE — one independently overridable `LIBRARY_DEFAULT` per concrete usage; no sharing without an explicit modeled relationship | UNPROVEN (mutation → Item 6); RM 11; ADR-001; census library-default class (58 EPs); checkpoint resolution 3 |

### A.4 Source inventory and derivation table

Six categories; every source has exactly one evidence role — direct observation, topology
referent, principle-derived target, control, or blocked obligation.

| Source | Role → row |
|---|---|
| RM 1 | observation → 01a |
| RM 2 | observation → 01b (+ paired-acceptance marker) |
| RM 3 | observation → 01c |
| RM 4 | observation → 01d |
| RM 5 | observation → 01e; named control for C11's expected convergence |
| RM 6 | observation → C14 |
| RM 7 | observation → 01f; topology referent for C15 |
| RM 8 | observation → C16 |
| RM 9 | observation → C1 (def-context per `hif_driver.sysml:6,76,118`) |
| RM 10 | observation → 01g; topology referent for C7 |
| RM 11 | observation → C23 |
| RM 12 | observation → C4 (DCS:71,83) + C5 (DCS:92); SI-09 cross-form note; referent evidence for C25 |
| RM 13 | historical observation → C26 literal-backed contradiction only; its `permitting.*` summary is overbroad and supplies neither C17 nor terminal-miss evidence (V4-M4) |
| Committed solar computation graph + raw parity evidence | direct observation → C17 producer-backed control (`computation_graph.json:2695-2702`) and exact bound on C26's three mints (`parity_solar_battery_model.json:194-216`) |
| AFT 1 | referent ruling → SRC-01 family |
| AFT 1c | observation → C2; referent class for C4 spelling, C10, C13, C20 |
| AFT 2 | observation → C3; referent class for C9, C12 |
| AFT 3 | observation → C6; referent class for chain cells C7/C8/C11/C19/C21 |
| AFT 4a | observation → 02a |
| AFT 4b | observation → 03a |
| AFT cross-form finding + uncertainty register | principle → A.2 table; C9/C10 targets |
| Census: converged class (123 EPs) | control → the expected topology of externally supplied `RUNTIME_SOURCE` cells (design-attribute-keyed public input); computed-source cells C17/C24 instead require their producer channels; SVM-synthesized subset flagged at C14 (V4-N2) |
| Census: Path A/B mints (75) + corpus (~124 + 91) | contradiction evidence → SRC-01, C1, C4, C5 |
| Census: authored-literal class | observation → C16 |
| Census: expression class (7 EPs) | checkpoint-resolved deferral and diagnostic target → C22 |
| Census: library-default class (58 EPs) | checkpoint-resolved per-usage target → C23 |
| Census: cross-owner unknowns (40 unresolved rows) | blocked obligation → C15 |
| Census: catf_mfe 13× `inner_radius` (intent unread) | principle note → C7; final census → Item 6 |
| Census: multi-occ def-default sharing | principle → C7 (ratified SI-05) |
| Blocked list: cross-consumer sweep | blocked obligation → C11/C12/C13 |
| Blocked list: nested-occurrence live leg | blocked obligation → C19 |
| Blocked list: shadowing / specialization | blocked obligation → C20 / C21 |
| Blocked list: mutation legs | R4 field on every `RUNTIME_SOURCE` cell → Item 6 |
| Epic paired customer acceptance (`epic:147-150`) + exact HIF/generic IFE owner-context lines | obligation / principle-derived target → 01b + C25 (mixed-context availability) + C2 (def-only thermal_efficiency; A.8) |
| Epic mission invariant (owner): one producer channel for a computed value | principle-derived target → C24 (added by the 2026-08-07 D8 reopening) |
| Lifecycle Appendix C "Producer-channel actual" row; REQ-IR-07/REQ-CL-05 producer-wiring clauses | topology referent / route-specific controls → C24 |
| Owner decision checkpoint (2026-08-05) | ratifies `[AGENT]` recommendations → C22, C23, and bare-renamed customer migration; the C4 placement was re-derived to C25/C2 after the audit disproved its premise; exact owner response recorded above |
| SI-05 / Item-4 foundation topologies | principle-derived targets → C7, C8 |

### A.5 Matrix checkpoint resolutions

- **Former PC-1 — expression bindings:** `DEFERRED(owner, 2026-08-05)` for source support in this
  epic. C22 makes the current boundary fail closed with a distinct readiness diagnostic.
- **Former PC-2 — unbound calculation-definition defaults:** C23 selects one independently
  overridable `LIBRARY_DEFAULT` source per concrete calculation usage.
- **Customer migration form:** bare-renamed-in-place per binding. C25 owns the exact mixed-context
  availability shape: the usage-authored `meier_coe_calc` leg resolves occurrence-level and the
  def-authored `lcoe_calc` leg resolves def-level through the occurrence bridge. C2 owns the two
  def-authored thermal-efficiency legs (`lcoe_calc`, `recirc_calc`). C4 remains DCS referent
  evidence, not the customer cell (rev 6 correction — the rev 5 all-usage-context premise was
  false; A.8).

All three form/behavior recommendations are `[AGENT]` recommendations ratified by the owner on
2026-08-05. Their original cell placement was agent-authored and remains challengeable by evidence;
the audit correction reopened the population under D8 for C24/C25 and the C17/C26 split (A.8).

### A.6 Count

**29 concrete acceptance cells** = 4 R2 family cells (SRC-01/02/03 and C22) + 25 individual cells
(C1–C21 and C23–C26). **35 concrete evidence coordinates** = 9 explicit family subrows
(7 + 1 + 1), C22's one kept readiness coordinate, and 25 individual-cell records. No pending
checkpoint class remains. (26/32 at the resolved checkpoint; C24/C25 added and C17/C26 split by
the 2026-08-07 D8 reopenings — A.8.)

### A.7 rev-4 → rev-5 mapping

- Supported families dissolved into cells (V4-M1): rev-4 SRC-09 → C9 + C10; SRC-10 → C11 + C12;
  new C13 closes the missing bare-renamed cross-consumer coordinate (V4-M5).
- Referent-context splits (V4-M3): rev-4 SRC-06 → C1 (def-context, RM9); SRC-07 → C2 (def-context,
  AFT 1c) + C4 (usage-context, DCS); SRC-08 → C3 (def-context, AFT 2) + C5 (usage-context, DCS:92,
  single-calc as observed).
- RM13 bounded role (V4-M4): rev-4 SRC-17 → C26 literal-backed contradiction only; the frozen
  summary's broader `permitting.*` claim is overbroad. Direct graph evidence owns C17's
  producer-backed control. SRC-22 → C18, now BLOCKED on a constructed genuine miss. The observed
  `permitting` terms are not terminal misses.
- Placeholders replaced by published targets (D8): rev-4 SRC-19/SRC-23 → C20/C21 with concrete
  keys and outcomes.
- Checkpoint classes resolved (V4-M1/M2): rev-4 SRC-04/05 → C22/C23. C22 records the deferred
  expression-support decision and fail-closed diagnostic; C23 records the per-usage default target.
- Renumbering note: rev-4 SRC-11/12/14/15/18/20/21 correspond to C7/C8/C16/C6/C19/C15/C14; the
  customer acceptance moved from the chain cell to C4 under the checkpoint-8 recommendation's
  then-recorded all-usage-context premise. A.8 records the later evidence correction to C25/C2;
  C4 remains usage-context referent evidence.

### A.8 rev-5 → rev-6 audit corrections (2026-08-07)

The Item-3 audit (`audit.md`, 2026-08-07, Needs Work) drove four correction classes, applied to
this appendix and the contract in the same change set (D8):

1. **audit-F1 — computed-source topology (D8 reopening).** The 26-cell population proved only the
   public-input half of the owner mission invariant ("one public input for an externally supplied
   value or **one producer channel for a computed value**"). C24 publishes the producer-channel
   target key.
2. **Customer binding-owner context.** Rev 5's premise that all customer bindings are
   usage-authored was false; only `meier_coe_calc` is (`hif_plant.sysml:205,215`). `lcoe_calc`
   and `recirc_calc` bind inside `part def 'IFE Power Plant'`
   (`generic_ife/ife_plant.sysml:98,114,126,134,148`). 01b records the original mixed contexts;
   C25 publishes availability's exact supported-form mixed-context target, while C2 owns the
   def-only thermal-efficiency target. C4 is supporting DCS referent evidence, not the customer
   coordinate. The stale `epic:145-148` citations moved to `epic:147-150`. Together C24/C25 move
   the reopened population from 26/32 to 28/34.
3. **Exact keys (R1/SI-23).** C7/C8 (two occurrences, 1 calc per occurrence), C9/C10 (two-occ
   context, def default, 1 calc), C15 (1 parent agg + 1 parent constraint + 1 child calc), C16
   (two literals, 1 calc each), and subrow 01g were re-published with exact consumer counts/types
   and value states; no parametric key values remain on counted rows.
4. **Additional superseded verification rows.** REQ-BT-13, REQ-IR-01, REQ-PGD-06, and REQ-VBR-03
   also certify superseded mechanisms; they now carry contract-disposition annotations (11 rows
   total). The VBR stamp citation was corrected to
   `src/sysml_codegen/orchestration/pipeline_builder.py:363-369`.
5. **Exact topology and coordinate cleanup.** RM 13's fixture contains a producer-backed cost
   feature and literal-valued modeled cost features, although the frozen RM 13 summary overstates
   the former's failure. C17 now owns the exact producer-backed aggregation coordinate from direct
   graph evidence;
   C26 owns the distinct literal-backed coordinate, reopening 28/34 to 29/35. C24 now fixes one
   declaration identity (`source_identity_computed.producer_calc.result`) for its blocked fixture,
   and 22a names one exact kept expression-binding coordinate.

---
Next Step: Item 4 semantic-identity and occurrence foundation.
