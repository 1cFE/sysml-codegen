---
date: 2026-08-15T10:39:05-07:00
researcher: Claude
topic: "Bounded ELABORATE-FIRST Item-8 stocktake: scope table, reconciled document-repair list, and validation of the self-binding spec's two dependent scope calls"
tags: [research, elaborate-first, item-8, documentation, scope, provenance]
status: complete
last_updated: 2026-08-15
---

# Research: Bounded Item-8 Stocktake

**Date**: 2026-08-15 10:39 PDT
**Researcher**: Claude (stage `research`, orchestrated run of `self-binding-replacement`)
**Research Type**: Project / Scope reconciliation
**Repo state**: codegen `main` @ `58bc6aa`, working tree carrying the uncommitted `dead-worktree-pins` edits

## Research Question

Three bounded deliverables, per `.project/active/self-binding-replacement/briefs/01-research-stocktake.md`:

1. A scope table of each ELABORATE-FIRST epic §C (Item 8) sub-item against what CONSTRAINT-SEMANTICS
   Items 1 and 7 already delivered, split into "test now" and "repair later".
2. One reconciled document-repair list, replacing the conflicting six-doc (epic) and twelve-doc
   (`CLAUDE.md`) lists.
3. Validation of the two scope calls the approved spec depends on — the restated `[OWNER 2026-08-15]`
   documentation obligation, and the declared home `.project/active/elaborator-downstream/`.

**Zero repairs were performed.** Nothing in the tree was edited. This file is the only artifact.

## Summary

- **Both of the spec's dependent scope calls hold in substance.** The epic *was* amended at both
  sites, and `.project/active/elaborator-downstream/` genuinely does not exist — exactly as the spec
  says. Neither premise is false.
- **But every line citation attached to those two calls is stale.** The amendments live at
  `:71-78` and `:503-511`, not the cited `:70-77` and `:495-503`. Four live documents carry the
  wrong ranges. This is citation drift, not a substantive defect — flagged, not repaired.
- **One live document still restates the retracted "two valid replacement forms" wording as if it
  governs**: `.project/CURRENT_WORK.md:158`, inside the very 2026-08-15 entry that commissioned this
  stocktake. Its neighbour at `:1360-1361` carries the softened "replacement forms" plus the stale
  six-doc list. Everything else that quotes the phrase is either the corrected source, an
  append-only ledger whose findings are explicitly resolved, or an archived record.
- **The overlap is five documents (11, 12, 13, 24, 25) — the brief's count is right, and the earlier
  "four" was wrong.** The reconciled union is **fourteen** documents, not six and not twelve:
  `CLAUDE.md`'s banner list omits two documents that carry banners (16, 18) and mentions 09 only in
  prose. The epic's list names 16, which `CLAUDE.md` omits, and omits seven that `CLAUDE.md` names.
- **Item 8 is roughly one-third already discharged and two-thirds untouched.** CONSTRAINT-SEMANTICS
  Items 1 and 7 delivered real work against sub-item 3's *guidance* clause and the epic-level matrix
  reconciliation, and ELABORATE-FIRST Item 7 (the cutover) delivered the retiring banners. Nothing
  has been delivered against the July IFE impact audit (sub-item 2), the source-identity matrix
  family, the README (sub-item 3), or the composed proof thread (sub-item 5).

---

## A note on "Item 7" — two different items, both closed on 2026-08-14

This tree has two closed items numbered 7, and the stocktake brief's phrasing ("Items 1 and 7")
could resolve to either epic. They are distinguished throughout this report:

- **CONSTRAINT-SEMANTICS Item 7** — "ADR, Product Promise, and Agent-Facing Documentation Sync",
  archived to `.project/completed/20260814_constraint-docs-agent-sync/`. This is the one the brief
  means: a documentation and agent-prompt sync, paired with CONSTRAINT-SEMANTICS **Item 1**
  ("Contract and Authoring Policy", archived to
  `.project/completed/20260813_constraint-semantics-contract-amendments/`). The pairing is
  confirmed by `.project/CURRENT_WORK.md:164` ("each §C sub-item vs what Items 1/7 already
  delivered") reading against `:1362` ("Items 1/7 landed part of the guidance obligations").
- **ELABORATE-FIRST Item 7** — the atomic cutover, archived to
  `.project/completed/20260814_cutover-recovery/`. This item wrote the retiring banners on the
  architecture reference documents (2026-08-12, `19072ad` / `82c7951` / `882fc8d` / `3071fba`).

Both are relevant to Item 8's scope, so both are credited below where they delivered.

---

## Deliverable 1 — Scope table: Item 8 sub-items vs what is already delivered

Source: `.project/backlog/epic_elaborate_first_architecture.md:486-521` (Item 8, five scope
sub-items). "Delivered by" is verified against the archived item records and the live tree, not
inherited from the epic's own claims.

### Sub-item 1 — Regenerate Fusion Tea and Stellarator packages/contracts

| Clause | State | Evidence |
|---|---|---|
| Fusion-tea regenerates on the exact route | **Proven once, on the wrong shape** | Slice 3D, 2026-08-11: loaded → elaborated → projected → generated → sealed → executed by `simkit.core.pipeline.execute_pipeline`; 11 channels, LCOE `270.1211779380445`, live and relocated legs equal (`.project/completed/20260814_cutover-recovery/plan.md:1944-2100`). But two of its 11 pinned channels are `hif_driver__hif_driver_instance__meier_cost__*` (`tests/execution/test_fusion_tea_real_teax.py:56-68`), and `hif_driver_instance` was **deleted from the customer repo** in July as workaround R-2. The certified evidence is of the pre-retirement shape. |
| Customer fusion-tea model migrated off self-bindings | **Not delivered** | 15 self-named bindings remain in `/home/reid/1cfe/fusion-tea/models/` (`designs/generic_ife/ife_plant.sysml` ×10, `designs/hif_ife/hif_driver.sysml` ×2, `designs/hif_ife/hif_plant.sysml` ×3). This is the work the approved `self-binding-replacement` spec covers. |
| Stellarator regenerates | **Not delivered; scope-split recommended** | 114 self-named bindings, of which 99 are its own (`generic_mfe/mfe_plant.sysml` ×94 incl. the literal `in R = R` at `:117`; `stellarator_09/stellarator_plant.sysml` ×5). `[OWNER 2026-08-15]`: triage only, one run, no fixes, July hold not reversed. |
| Duplicate-field workaround removal | **Not delivered** | The workaround-free shape is unproven on this route. Expected 9 channels is an inference, not evidence. |
| New study lineage where identity changed | **Not delivered, and unowned** | Named as an orphan by `product-lens.md:92-102` (spec-F6). Rev 3 of the spec homes it to Item 8 at `.project/active/elaborator-downstream/` — which does not exist (Deliverable 3B). |
| TEAx compatibility through stock APIs | **Delivered, in fusion-tea's own repo** | Branch `item8-fusion-embedded-catalog` (fusion-tea's own CONSTRAINT-EXEC numbering, commits 2026-07-20): stock multi-channel bridge, wrappers deleted, per-definition predicate API. 6 ahead / 0 behind `main`, inherits the workaround-free model from PR #101 (`91d03a7f`). Working tree dirty. |
| Acceptance-pin re-anchoring | **Not delivered** | 9-vs-11 channel question; needs one capture run plus an owner call (re-anchor to 9, or restore the instance and contradict R-2). |

### Sub-item 2 — July IFE impact audit

**Not delivered. No artifact of any kind exists.** A tree-wide search for "IFE impact" / "impact
audit" returns exactly one hit — the roadmap line that schedules it
(`.project/CURRENT_WORK.md:1359`). No spec, no research, no backlog row, no partial record.

### Sub-item 3 — Certification repair (four clauses; they diverge sharply)

| Clause | State | Evidence |
|---|---|---|
| Verification matrix gains an independently anchored **source-identity family** with public mutation evidence | **Not delivered** | `docs/architecture/verification-matrix.md` carries 34 families (AS, AST, BASE, BT, CA, CL, CON, CS, DM, DIAG, DRA, EC, EPC, EXT, GA, GEN, HR, IR, LVP, MF, NC, OR, ORCH, OSR, PGD, PIPE, PMM, PY, REG, RES, SNAP, SR, SVM, VBR). **There is no SI / source-identity family.** The mutation evidence exists as tests (`test_fusion_tea_mutation_teax.py`, the gain=100 three-route proof) but is not anchored as a matrix family. |
| Contradictory acceptance claims corrected | **Substantially delivered** | CONSTRAINT-SEMANTICS Item 7 scope 6 + ELABORATE-FIRST cutover step 4: full recount (288 rows / 156 PASS / 1 PARTIAL / 131 RETIRED / **0 UNTESTED** / 34 families / 64 kept test files), both count blocks corrected, REQ-CS family (8 rows) minted, REQ-DIAG gap filed. |
| Architecture reference docs rewritten or retired | **Banners delivered; rewrite not started** | ELABORATE-FIRST Item 7's retirement wrote status banners on 16 documents (Deliverable 2). CLAUDE.md is explicit: "Their rewrite is a separate authorship pass that **has not run**." |
| **README states the library's purpose plainly** | **Not delivered, and the README is actively wrong** | `README.md` is 65 lines and says nothing about the retired stack (so no retirement repair is owed), but four claims are false at HEAD: the usage line `sysml-codegen --models …` (`:47`, `:53`) omits the required `generate` subcommand (`src/sysml_codegen/cli/__init__.py:1047-1050`); install paths are `~/sysml-codegen` / `~/agentic-mbse` (`:14`, `:17`, `:24`) where the wired-in checkouts are under `/home/reid/1cfe/`; test/lint commands omit the `--extra dev` the optional extra requires (`:32-41` vs CLAUDE.md); and the `snapshot` / `seal` / `install` subcommands (`cli/__init__.py:1096`, `:1113`, `:1126`) — including the whole license-free from-snapshot route — go unmentioned. |

### Sub-item 4 — The restated `[OWNER-VERBATIM]` authoring obligation

| Clause | State | Evidence |
|---|---|---|
| Know the right pattern(s) for each situation | **Not delivered as measurement** | The spec's `[HARD]` `SI_OCCURRENCE_AMBIGUOUS` row is marked *measurement pending re-establishment*; the reverted branches' measurements are evidence, not fact. This is what the orchestrated run's spike leg exists to do. |
| Document those patterns | **Adjacent work delivered; this obligation not** | CONSTRAINT-SEMANTICS Item 1 published the equality-intent taxonomy in `agentic-mbse/docs/patterns/constraints.md` and ADR-009; Item 7 delivered `@inapplicable:`, the disposition vocabulary, the six states, and the `sysml-conventions` skill correction. **None of it touches self-binding.** Verified directly: grepping the five agent surfaces symlinked into codegen (`.claude/agents/{kerml,syside,sysml}-expert.md`, `sysmlv2-validator.md`, `.claude/skills/sysml-conventions/`, 1,340 lines total, symlinks resolving into `/home/reid/1cfe/agentic-mbse/claude/`) for `in R = R` and `self-bind` returns **zero hits**, while a "binding" control returns three files. The spec-review's gap finding still holds at HEAD. |
| Fix the models | **Not delivered** | Same as sub-item 1's migration clause. |
| Detect the wrong pattern | **Delivered in codegen; agentic-mbse leg unconfirmed** | `src/sysml_codegen/extraction/source_evidence.py:230` + `src/sysml_codegen/elaboration/elaborate.py:2005` refuse it as a readiness finding. The align record scopes this to *confirmation*, not new detector work. |

### Sub-item 5 — One composed model→package→study proof thread

**Partially delivered, on the superseded shape.** Slice 3D is a real composed thread
(model → elaborate → project → generate → seal → SimKit registry discovery → execute), and the
gain=100 three-route mutation proof landed at cutover step 4. Both were taken on the fixture that
still carries `hif_driver_instance`. As the epic's *closing* evidence over the migrated, workaround-
free customer model, it is not delivered.

### The split the brief asked for

**Test now** — work whose subject exists and only needs to be exercised or measured:

1. Fusion-tea whole-plant capture run to settle 9-vs-11 channels (sub-item 1). One run answers it.
2. Stellarator one-shot triage run (sub-item 1). `[OWNER 2026-08-15]` bounded to exactly this.
3. Confirm both detection paths refuse `in R = R` (sub-item 4). Codegen side is cited; the
   agentic-mbse validation leg needs the confirming run.
4. Re-establish the per-shape referent measurements on the shipped exact route (sub-item 4). This is
   the approved item's spike leg, not stocktake work.

**Repair later** — work that needs authorship, a decision, or a vehicle that does not yet exist:

1. The July IFE impact audit (sub-item 2) — no artifact exists; needs a spec and an owner.
2. The source-identity verification-matrix family (sub-item 3) — needs REQ tags minted, which is a
   requirements decision, not a matrix reconciliation. Same shape as the parked
   `[CONSTRAINT-GATES-UNTAGGED]` precedent.
3. The fourteen-document rewrite pass (sub-item 3) — see Deliverable 2.
4. README correction (sub-item 3) — four falsified claims, small and contained.
5. Study lineage, duplicate-field workaround removal, acceptance-pin re-anchoring (sub-item 1) —
   all homed to a folder that does not exist.
6. Stellarator's 99 own-model renames (sub-item 1) — recommended out of this item entirely.
7. The closing composed proof thread on the migrated model (sub-item 5).

---

## Deliverable 2 — Reconciled document-repair list

### The two conflicting lists

- **Epic §C sub-item 3** (`epic_elaborate_first_architecture.md:501-502`): "docs
  **11/12/13/16/24/25** rewritten or retired to match the new front end" — six.
- **`CLAUDE.md`, "Retired — read before trusting a document"**: "Reference documents **03, 04, 05,
  07, 10, 11, 12, 13, 17, 24, 25, and 28** describe that stack and open with a retiring banner;
  document **09** is mixed" — twelve named as banner-carriers, thirteen counting 09.

**Overlap = five: 11, 12, 13, 24, 25.** The brief is correct and the prior "four" was wrong. Epic-only: **16**. CLAUDE.md-only: **03, 04, 05, 07, 10, 17, 28** (plus **09** in prose).

### Both lists are incomplete against the tree

Sixteen documents in `docs/architecture/reference/` open with a `> **Status:` banner. Two of them
appear on **neither** list:

- **`16-computed-attributes.md`** — has a banner ("mixed, and the resolution half is historical"),
  is on the epic list, and is **missing from `CLAUDE.md`'s** enumeration.
- **`18-literal-value-propagation.md`** — has a banner ("the mechanism below was deleted; the
  shipped equivalent is described first"), and appears on **neither** list.
- **`25-hierarchy-resolver.md`** — banner-carrying, on both lists, but its banner says the module
  **survived** the retirement. It is a different disposition class from the other twelve.

### The reconciled list

Fourteen documents. Column meanings: **Banner?** = does it open with a `> **Status:` block; **Class**
= what the banner actually claims about its subject; **Repair owed** = what a rewrite pass would have
to do. No repair was performed.

| Doc | Banner? | On epic list | On CLAUDE.md list | Class | Repair owed |
|---|---|---|---|---|---|
| `03-resolution-overview.md` (283 ln) | yes | — | yes | Historical — subject deleted (`producer_resolution.py`, `core/output_registry.py`, plus `resolution/input_resolver.py` deleted earlier at `936315c`) | Rewrite or formally retire; no live subject remains |
| `04-producer-resolution.md` (273 ln) | yes | — | yes | Historical — `resolution/producer_resolution.py` deleted | Rewrite or retire |
| `05-module-factory.md` (277 ln) | yes | — | yes | Historical — `resolution/graph_builder.py` deleted | Rewrite or retire |
| `07-graph-assembly.md` (392 ln) | yes | — | yes | Historical — `build_computation_graph()` / `graph_builder.py` deleted | Rewrite or retire |
| `09-data-models.md` (424 ln) | yes | — | prose only | **Mixed** — some models live, some describe deleted types | Split: keep the live models, retire the rest. Explicitly named as mixed by CLAUDE.md |
| `10-output-registry.md` (478 ln) | yes | — | yes | Historical — `core/output_registry.py` + 4-phase protocol deleted | Rewrite or retire |
| `11-analysis-backtracker.md` (412 ln) | yes | **yes** | yes | Historical — `analysis/dependency_backtracker.py` deleted | Rewrite or retire |
| `12-virtual-binding-rewrite.md` (303 ln) | yes | **yes** | yes | Historical — VBR / `pipeline_builder.py` deleted | Rewrite or retire |
| `13-aggregation-scoping.md` (235 ln) | yes | **yes** | yes | Historical — `pipeline_builder.py` deleted | Rewrite or retire |
| `16-computed-attributes.md` (515 ln) | yes | **yes** | **missing** | **Mixed** — the extraction-level taxonomy is live (`extraction/computed_attribute_extractor.py` is in the tree); the resolution map, Phase 3b, `AttributeResolutionKind`, REQ-CA-06, REQ-CA-11 are deleted code | Split. **CLAUDE.md's list is incomplete here** |
| `17-parameter-group-deriver.md` (276 ln) | yes | — | yes | **Half live, half historical** — `analysis/parameter_groups.py` deleted | Split |
| `18-literal-value-propagation.md` | yes | **missing** | **missing** | Mechanism deleted; shipped equivalent described first | **Neither list names it.** Repair scope unassessed by either authority |
| `24-dual-resolution-architecture.md` (173 ln) | yes | **yes** | yes | Historical — `resolve_input`, `AGG_STRATEGIES`, `ResolutionContext` deleted | Rewrite or retire |
| `25-hierarchy-resolver.md` (377 ln) | yes | **yes** | yes | **Still in the tree, off the shipped route** — `extraction/hierarchy_resolver.py` survived; no public caller reaches it; retained because `tests/helpers/live_extraction.py` depends on it. Disposition recorded in the module docstring; **deletion waits on an owner** | Not a rewrite. An owner decision on deletion |
| `28-constraint-lowering-and-catalog.md` (154 ln) | yes | — | yes | **Double-superseded** — lowering half historical (`analysis/constraint_lowering.py` deleted); catalog half superseded by CONSTRAINT-SEMANTICS Item 2 (2026-08-12) | Rewrite; the catalog half already has a live replacement to point at |

Four documents (`00-pipeline-overview.md`, `02-orchestration.md`, `06-entry-point-classifier.md`,
`27-snapshot-generation.md`) reference the retirement commits without carrying a status banner —
they were updated in place rather than banner-flagged, and need no repair.

### What this means for the epic's six

The epic's list of six is not a subset of a correct list — it is a different, smaller, and partly
disjoint selection made before the retirement ran. **Nine of the fourteen documents that need a
disposition are absent from it.** Any Item-8 execution against the epic's own text would leave
those nine untouched. This is exactly the staleness the `[OWNER 2026-08-15]` scrub ruling
anticipated.

---

## Deliverable 3 — Validating the spec's two dependent scope calls

### 3A. The restated documentation obligation

**Verdict: the substance holds; every line citation attached to it is stale.**

**The amendment is present at both sites.** The epic carries:

- The `[OWNER-VERBATIM]` (2026-08-15) restatement in "Owner-originated rulings carried forward",
  quoting the owner's four clauses verbatim and closing "it carries no count of replacement forms."
- The rewritten Item-8 scope sub-item 4, carrying a `*Provenance correction 2026-08-15:*` note that
  quotes the retracted wording, states that no owner utterance enumerating two forms exists, and
  ends "Nothing downstream should treat a form count as owner-given."

Both are amendments in place with the correction recorded as one note, which is what
capture-fidelity law 3 asks for. **This call is sound.**

**The line ranges are wrong.** The brief, the spec, and `CURRENT_WORK.md` all cite `:70-77` and
`:495-503`. Measured at HEAD:

| Cited as | Actually at | Drift |
|---|---|---|
| `:70-77` (owner ruling) | **`:71-78`** | +1 |
| `:495-503` (sub-item 4) | **`:503-511`** | +8 |

Line `:70` is the previous ruling about snapshot serialization format; `:495-503` straddles the end
of sub-item 1 and the whole of sub-items 2 and 3. Four documents carry the stale ranges:
`.project/CURRENT_WORK.md:19`, `:111`, and the brief itself at both mentions. Separately,
`product-lens.md:16-17` cites `:497-499` and `:71-72` for the *pre*-amendment text. All are
citation drift, not substantive error — **flagged, not repaired**.

**Sweep for surviving governance by the retracted wording.** Searching the codegen tree for
"two valid replacement forms", "valid replacement forms", "replacement forms",
"allowable modeling pattern(s)", "allowable patterns", "allowable-modeling" yields these hits,
classified:

| Site | Classification |
|---|---|
| `epic_elaborate_first_architecture.md:78`, `:507-508` | The correction itself, quoting what it replaces. Correct. |
| `.project/active/self-binding-replacement/spec.md:39` | The spec's own retraction. Correct. |
| `spec-review.md:41,52,54,121,283,294,347` | The review that *found* the defect. Correct. |
| `product-lens.md:14-15,33,48-58` | Append-only ledger, first block. Its `spec-F2` finding is explicitly resolved by citation in the rev-3 block (`:120`: "no fixed form count governs"). Under the ledger's own rule (`:4-5`), a BLOCK resolved by citation is not blocking. **Does not govern.** |
| `.project/completed/20260810_epic_semantic_source_identity.md:290`, `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:444`, `.project/active/source-identity-contract/spec.md:151`, `audit.md:97` | The **original** 2026-08-05 owner quote ("we MUST document allowable patterns…"), which the epic explicitly says "is the same obligation in its original wording; it carries no count." Not the retracted count. Correct. |
| `.project/completed/20260809_elaborator-breadth/product-lens.md:79` | Archived audit finding F19, citing "epic line 402". Historical record. |
| **`.project/CURRENT_WORK.md:158`** | ⚠ **Live, and still governs by the retracted count.** In the 2026-08-15 "Item 8 sequencing" entry: *"Epic §C item 4 is an `[OWNER-VERBATIM]` obligation (publish the `in R = R` diagnostic guidance and its **two valid replacement forms** in agentic-mbse docs)"*, and the following line says whether Item 7 discharged it "is unknown and needs the owner." Both clauses are superseded by the same day's restatement recorded 139 lines above at `:15-19`. A reader entering at the Active Work section gets the retracted framing. |
| **`.project/CURRENT_WORK.md:1360-1361`** | ⚠ Live roadmap §C entry. Softer — "the `[OWNER-VERBATIM]` allowable-modeling-pattern guidance (`in R = R` diagnostic + replacement forms)" carries no count — but it still pairs the retracted framing with the **stale six-document list** (`11/12/13/16/24/25`). |

**Companion repositories: partial coverage, stated plainly.** `/home/reid/1cfe/agentic-mbse`,
`/home/reid/1cfe/fusion-tea`, and `/home/reid/1cfe/teax` are outside this session's sandbox and could
not be swept in full. What *was* swept, through the resolving symlinks in `codegen/.claude/`, is the
five agent-facing surfaces (four expert agents plus the `sysml-conventions` skill, 1,340 lines):
zero hits for "replacement forms", zero for "in R = R", zero for "self-bind". So the retracted
wording has not reached the agent surfaces, and the spec-review's gap finding (no self-binding
warning anywhere an agent reads) is **reconfirmed at HEAD**. The remaining ~32 files under
`agentic-mbse/claude/`, the divergent `.claude/` tree, and `docs/patterns/` are **unswept** — a
design or implement stage with companion-repo access must repeat this sweep there.

### 3B. The declared home `.project/active/elaborator-downstream/`

**Verdict: it does not exist. Confirmed, and not created.**

`.project/active/` contains 47 entries. `elaborator-downstream` is not among them. The name is
referenced by three live documents — `epic_elaborate_first_architecture.md:519` (Item 8's
**Location** field), `spec.md:154` (the Non-Goal homing the regeneration remainder), and
`product-lens.md:98` (spec-F6, which first surfaced the absence) — and by nothing on disk.

The spec's wording is accurate: it says the remainder "stays with Item 8 at its declared home …
**which must be created before that remainder is worked**." That is a correct statement of a future
obligation, not a claim that the folder exists. **The scope call is sound as written.**

The practical consequence, unchanged by this report: the concrete orphans — study lineage where
identity changed, duplicate-field workaround removal, TEAx compatibility through stock APIs,
acceptance-pin re-anchoring — have a named home and no vehicle. Creating it is the first act of
whoever works that remainder.

---

## ⚠ Surfaced, not resolved

Per capture-fidelity law 4 and the brief's hard bound, these are named with their dependent
conclusions parked. **No premise the approved spec rests on was found false.**

1. **`CURRENT_WORK.md:158` still governs by retracted wording** (Deliverable 3A). Dependent and
   parked: the "whether CONSTRAINT-SEMANTICS Item 7 discharged the obligation is unknown and needs
   the owner" question on the following line. `CURRENT_WORK.md:15-19` closes that question as
   *superseded* — the restatement makes prior partial discharge irrelevant. The two statements
   contradict each other inside one file. Resolving it is a repair; this report does not.

2. **`CLAUDE.md`'s retiring-banner list is incomplete** (Deliverable 2). Documents 16 and 18 carry
   banners and are not enumerated. Anyone using CLAUDE.md's list as the do-not-trust set will read
   16 and 18 as trustworthy. Dependent and parked: the scope of the "separate authorship pass that
   has not run."

3. **Document 25 is a different disposition class and should not ride the rewrite pass.** Its
   subject survived; its question is "delete or keep", and the module docstring records that the
   deletion waits on an owner because the elaborator's equivalents are not shown to be equivalent.
   Bundling it into a documentation rewrite would silently convert an owner decision into an agent
   one. Parked as an owner call.

4. **Line-range citations are the recurring failure mode here.** Three separate ranges into one epic
   file drifted between authorship and this reading. Dependent and parked: whether Item-8 artifacts
   should cite epic *headings* rather than line numbers. Not this report's call.

## Code References

- `.project/backlog/epic_elaborate_first_architecture.md:71-78` — the `[OWNER-VERBATIM]` 2026-08-15
  restatement (cited elsewhere as `:70-77`)
- `.project/backlog/epic_elaborate_first_architecture.md:486-521` — Item 8, five scope sub-items
- `.project/backlog/epic_elaborate_first_architecture.md:503-511` — amended sub-item 4 with the
  provenance-correction note (cited elsewhere as `:495-503`)
- `.project/CURRENT_WORK.md:15-19` — the obligation closed as superseded
- `.project/CURRENT_WORK.md:158`, `:1360-1361` — the two live sites still carrying retracted framing
- `docs/architecture/verification-matrix.md:113-803` — 34 families, no source-identity family
- `docs/architecture/reference/16-computed-attributes.md:3-14` — banner absent from CLAUDE.md's list
- `docs/architecture/reference/25-hierarchy-resolver.md:3-19` — the survived-the-retirement banner
- `README.md:14-53` — the four falsified claims
- `src/sysml_codegen/cli/__init__.py:1047-1126` — `generate` / `snapshot` / `seal` / `install`
- `src/sysml_codegen/extraction/source_evidence.py:230`,
  `src/sysml_codegen/elaboration/elaborate.py:2005` — the shipped `SI_SELF_BINDING` refusal
- `.project/completed/20260814_epic_constraint_semantics_contract.md:284-393` — CONSTRAINT-SEMANTICS
  Item 1 close record
- `.project/completed/20260814_epic_constraint_semantics_contract.md:1139-1257` —
  CONSTRAINT-SEMANTICS Item 7 close record, including the two unticked criteria
- `.project/completed/20260814_cutover-recovery/plan.md:1944-2100` — Slice 3D composed thread

## Recommendations

Ordered, and all downstream of the approved item — none of it is this report's to execute.

1. **The `self-binding-replacement` item proceeds unchanged.** Both dependent scope calls survive
   verification. Nothing here should reopen the spec.
2. **Fix the two `CURRENT_WORK.md` sites as a quick edit**, not as Item-8 work. `:158`'s retracted
   count and its already-answered owner question, and `:1360-1361`'s stale six-doc list.
3. **Re-cite the epic by heading, not line range**, wherever an Item-8 artifact points at it.
4. **Treat the reconciled fourteen-document list as the doc-repair scope**, and correct
   `CLAUDE.md`'s banner enumeration to name 16 and 18 — that correction is small, contained, and
   makes the do-not-trust set true.
5. **Split document 25 out of the rewrite pass** and route it to the owner as a delete-or-keep call.
6. **File the July IFE impact audit as its own item.** It has no artifact and no vehicle, and it is
   the only Item-8 sub-item with literally nothing behind it.
7. **Create `.project/active/elaborator-downstream/` when the regeneration remainder is worked**, not
   before. The brief forbade creating it here, and there is no reason to pre-create it.

## Open Questions

Owner-grade, surfaced by this stocktake and not answered by it:

- Does the source-identity verification-matrix family get REQ tags minted (the
  `[CONSTRAINT-GATES-UNTAGGED]` precedent), or does it stay parked?
- `hif_driver_instance`: re-anchor the acceptance pin to the workaround-free 9 channels, or restore
  the instance and contradict July's R-2?
- Delete `extraction/hierarchy_resolver.py`, or keep it with `live_extraction.py`'s dependency?
- Does the Item-8 document rewrite pass run as one authorship item, or per-document alongside the
  code it describes?

---

**Scope discipline record:** zero files edited, zero documents rewritten, zero epic edits, zero code
changes. `.project/active/elaborator-downstream/` was not created. D-4 through D-7 were not reopened
and the spec was not restated.
