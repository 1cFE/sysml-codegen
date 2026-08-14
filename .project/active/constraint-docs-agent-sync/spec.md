# Spec: Item 7 — ADR, Product Promise, and Agent-Facing Documentation Sync

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-14
**Complexity:** MEDIUM (documentation-only, but three repos and a first-capture product/ADR home)
**Branch:** `item7-rebuild` (codegen); agentic-mbse worktree `item7-rebuild`; TEAx `constraint-semantics-item3`
**Epic:** CONSTRAINT-SEMANTICS — `.project/backlog/epic_constraint_semantics_contract.md`, Item 7

---

## Problem

The CONSTRAINT-SEMANTICS epic landed a new constraint-semantics contract across Items 1–6, 8 and 9
(all closed, archived under `.project/completed/20260813_*`). The behavior changed; most of the
documentation that teaches it did not. Three things are wrong today, and each has a named cost.

**The coverage-truth promise has no durable home.** Item 3's audit filed this as `audit-F4` with
"no home available" — this repo has no `.project/product/` ledger and no ADR registry beyond
`modeling-assumptions.md` sections (`epic_constraint_semantics_contract.md:540-543`). The promise
exists only as a concept subsection plus ADR-009 at `[AGENT] (ratified)`. The owner has now stated
it in their own words, so the blocking condition on that filing is discharged:

> **[OWNER-VERBATIM, 2026-08-13]**
> The system seeks to enable a design search where:
> - engineering design parameters can be freely varied, and viability and outcomes (like LCOE)
>   can be assessed
> - we differentiate from 1costingFE in that we do not embed the engineering logic:
>   predetermining the free variables and backing into all others

(`.project/active/constraint-docs-agent-sync/owner-checkpoint-20260813.md:9-13`. This text is
payload under capture-fidelity law 2: it survives verbatim, never reworded.)

**Shipped docs and agent prompts teach the superseded policy.** The codegen `sysml-conventions`
skill's constraint example (`.claude/skills/sysml-conventions/SKILL.md:136`) is an inline assert
with a unit literal — exactly the shape the blessed bindings-only pattern supersedes. agentic-mbse
`docs/patterns/constraints.md` has zero mention of `@inapplicable:` authoring or the
eligible+inapplicable refusal. TEAx docs have zero mention of `partial_coverage` /
`full_satisfaction`, the keep-for-boundary default, or the feed-strategy opt-in config. Nothing
documents the disposition vocabulary or carrier concepts as shipped
(`epic_constraint_semantics_contract.md:1063-1070`). The next authoring session — human or agent —
will copy the old shape.

**Four obligations have no execution vehicle.** Item 1 is archived, so the two orphans re-homed
to it (design-F2's Appendix C cell; the D9 authoring-time advisory) plus the item3-F2 ruling and
the Item 5 residual A-8 matrix reconciliation all land here or nowhere
(`epic_constraint_semantics_contract.md:518-543`).

This is the last item before epic close. It documents what landed; it changes no behavior.

## Success Criteria

The epic section's six checkboxes are the acceptance frame, adopted unchanged
(`epic_constraint_semantics_contract.md:1118-1132`):

- [ ] **[OWNER]** The coverage-truth promise is owner-stated, filed in a named home, and cited
      from the product-lens trail (closes Item 3 audit-F4).
- [ ] No shipped doc, skill, or agent prompt in the three repos teaches the superseded constraint
      semantics; the sweep record lists every hit and disposition (Item 1's three-sweep method).
- [ ] `@inapplicable:`, the disposition vocabulary, the six states, and the TEAx opt-in are
      documented where their users (human and agent) will find them.
- [ ] The authoring docs state when an in-model `@inapplicable:` marker works (bindings-form) and
      when PROVENANCE has to carry the disposition instead (inline-predicate form), with the
      B1–B5 worked case cited (Item 5 close obligation).
- [ ] Verification-matrix rows exist for the constraint-semantics gates landed in Items 2–5, filed
      in one reconciliation pass with the index recount done (Item 5 residual A-8).
- [ ] Documentation checks and `git diff --check` pass in every touched repository.

## Known Requirements

### The promise and its home (epic scope 1)

- **[NEED]** The first-capture product entry reproduces the `[OWNER-VERBATIM]` two-bullet promise
  above exactly, at the owner's emphasis, as its core. Path-cite:
  `owner-checkpoint-20260813.md:9-13`. No rewording, no paraphrase, no "improved" version.
- **[NEED]** Material gleaned from the concept docs supplements the verbatim core and never
  rewrites it, marked `[INHERITED: <source>]` per source. Owner instruction, same session:
  *"You could probably glean more from the concept docs that we developed over time."*
  (`owner-checkpoint-20260813.md:15-16`). Named starting sources:
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` and
  `.project/concepts/constraint-execution-and-design-space-studies.md` (its `:15` framing —
  calculations compute a candidate state, constraints judge it, a study varies inputs and applies
  user-selected feasibility policy — is the closest concept-side statement of the same promise).
- **[INFERRED]** The epic's `[OWNER]` Critical Success Factor ("A design search can trust the
  generated feasibility evidence to represent every applicable asserted physics gate, while every
  other authored constraint remains visibly dispositioned") is cited **beside** the promise as its
  enforcement-side companion, not merged into it
  (checkpoint filing guidance, orchestrator agent-grade, `owner-checkpoint-20260813.md:24-27`).
- **[INFERRED]** The entry states the promise as **directional intent** and points at
  `[ACAUSAL-RELATIONS-CAPABILITY]` (BACKLOG:439, filed at owner direction 2026-08-13) for the
  unbuilt half, so the promise's second bullet and the owner-ratified A5/A6/A7 basis rulings
  cannot be read as silently contradicting. The recorded reconciliation — the toolchain is causal
  by construction; equality gates over free parameters strangle search (the owner's own R-POL-4
  rationale); bases are therefore owner-signed, visible, in-model choices — is carried, not
  re-derived. **This tension is surfaced in daylight in the entry itself; it is never resolved
  silently in either direction** (capture-fidelity law 4;
  `owner-checkpoint-20260813.md:28-36`). It is not open for re-resolution by this item.
- **[INFERRED]** Home shape, default of record: a first `.project/product/INDEX.md` ledger entry
  plus a per-repo ADR convention, minted by this item (neither directory exists today). Design and
  plan may refine the shape; they may not relocate the authority.
- **[NEED, epic SC1 `:1120-1121` (OWNER)] [amended per lens item7-F2, `[AGENT, orchestrator
  2026-08-14]`]** The filed entry is **cited from the product-lens trail**, and wiring that citation
  is part of this item's work — not a downstream side effect. This is SC1's second half and the
  enforceable one: audit-F4's complaint was that the promise had no entry a lens run could resolve
  against (`epic_constraint_semantics_contract.md:540-543`), so a promise filed in a new ledger the
  trail does not point at reproduces that condition one directory over. The ledger entry is what a
  future lens run resolves against. Design names **which** ledger carries the citation, given that
  audit-F4's own ledger (`completed/20260813_constraint-coverage-policy/product-lens.md`) is
  archived and is cited, not edited.

### The item3-F2 amendment (epic scope 1, ruling pre-recorded)

- **[INFERRED]** The lifecycle contract's blanket BLOCK clause amends to **reaching-gates scope**:
  BLOCK-halts applies to asserted gates that reach occurrences; a non-reaching asserted usage is
  governed by severity-by-cause and the coverage rules (`non_reaching`, missing assessment, partial
  coverage), never a model-wide halt. Ruling grade `[AGENT] (ratified by owner, 2026-08-13)`,
  recorded in full at `owner-checkpoint-20260813.md:38-53`. Amendment mechanics follow the
  conventions Item 1 set: provenance preserved and the original text recorded, not overwritten.
  Known clause sites to reconcile:
  `constraint-execution-authoritative-lifecycle-contract.md:131` (invariant 1), `:441`
  ("Headline states and coverage truth"), `:794` (Appendix C "ADMIT + NON_NUMERICAL + BLOCK mix").
- **[INFERRED]** The parked-conflict record for item3-F2 flips to **RESOLVED-with-citation** at
  the same time, at every site that currently carries it as unresolved:
  `.project/active/constraint-semantics-contract/spec.md:195` (the `[HARD]` blanket clause) and
  `:294` (the Non-Goal "changing BLOCK-halts-generation semantics"), and the epic's residual entry
  at `epic_constraint_semantics_contract.md:531-539` ("It stays a surfaced premise conflict in
  both directions until then"). Item 3's own spec-side disposition record
  (`completed/20260813_constraint-coverage-policy/product-lens.md:58-66`) is archived and is
  cited, not edited. The point of the flip is the epic's own instruction: *do not let a later
  agent read the clause as a live requirement.*

### Cross-repo documentation sweep (epic scope 2)

- **[INHERITED: epic scope 2, `:1087-1091`]** agentic-mbse `docs/patterns/constraints.md` gains
  `@inapplicable:` authoring, the eligible+inapplicable refusal (D9), and the D9 authoring-time
  advisory guidance.
- **[INHERITED: epic scope 2]** Codegen reference docs gain the disposition vocabulary
  (`eligible` / `excluded` / `non_reaching`, the closed reason set, and precedence — the
  Item 3-citable section of
  `completed/20260813_constraint-catalog-totality/design.md`), carriers, the totality gate, and
  severity-by-cause.
- **[INHERITED: epic scope 2]** TEAx docs gain the six report states, the coverage block, the
  policy defaults, the keep-for-boundary default with the feed-strategy opt-in config, and the
  durable-record fields.
- **[INHERITED: epic SC2, `:1122-1124`] [amended per lens item7-F1, `[AGENT, orchestrator
  2026-08-14]`]** The sweep is **Item 1's five-term recorded sweep, S1–S5**
  (`completed/20260813_constraint-semantics-contract-amendments/design.md:1202-1218`). The epic's
  SC2 calls it the "three-sweep method"; that label is **superseded** — it is named here once so the
  citation trail back to SC2 still resolves, and it is not the method. Four properties of the
  method are load-bearing and travel with it:
  - **Five terms, S1–S5.** S1 retired test name; S2 `require constraint` taught as a check; S3
    plain-constraint-enforces claims (verb alternation widened by review M5); S4 the superseded
    headline precedence; S5 `assume`/`satisfy` taught as a check. S4 and S5 exist to catch the
    epic's *own* corrected vocabulary, which the first three terms miss. **Adding a term is
    allowed, dropping one is not** (`design.md:1224-1225`).
  - **The DD5 scope, with its exclusions written into the record** (`design.md:1196-1200`). In:
    `docs/`, `src/`, `tests/`, `scripts/`, `README.md`, `CLAUDE.md`, `.project/concepts/`,
    `.project/backlog/`. Excluded: `.project/research/`, `.project/completed/`, `.project/active/`
    — dated records. The boundary is recorded, not silent.
  - **One row per raw hit. A summary does not discharge the criterion** (`design.md:1227-1228`). A
    hit left unchanged is a disposition, recorded as one.
  - **The S4 collision is resolved in advance:** run S4 before the edits, and disposition any
    post-edit hit inside an amendment note as "quoted supersession, correct as written"
    (`design.md:1220-1222`).
- **[INFERRED, lens item7-F1]** A **TEAx sweep scope is defined and stated in the sweep record.**
  Item 1 ran S1–S5 in two repositories ("Run S1–S5 in the companion repository with the same
  scope", `design.md:1224`); this item's SC2 asserts the no-superseded-teaching claim over **three**,
  and no TEAx scope exists anywhere today. Plan decides the exact boundary — whether S1–S5 transfer
  unchanged or a local term is added for a TEAx idiom (adding is allowed, dropping is not) — but the
  sweep record must state that boundary. An undeclared third-repo scope cannot substantiate SC2.

### Agent prompts and skills (epic scope 3)

- **[INHERITED: epic scope 3, `:1092-1096`]** The codegen `sysml-conventions` skill teaches the
  bindings-only blessed pattern, points at the equality-intent taxonomy, covers `@inapplicable:`
  usage, and its stale example is corrected. Named stale site:
  `.claude/skills/sysml-conventions/SKILL.md:136` (inline assert with a unit literal).
- **[INHERITED: epic scope 3]** CLAUDE.md in all three repos and the expert-agent definitions are
  swept for superseded constraint teaching.
- **[INHERITED: epic scope 3] [dependency named per lens item7-F3, `[AGENT, orchestrator
  2026-08-14]`]** Agent-facing examples are verified to elaborate cleanly under the current profile.
  This is the **one requirement in this item that needs a licensed toolchain run**; every other one
  is satisfiable by reading and writing text. Its execution terms:
  - **License.** `SYSIDE_LICENSE_KEY` from `/home/reid/1cfe/agentic-mbse/.env`, loaded with
    `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. There is no `.env` in this repo.
  - **Interpreter.** `/home/reid/1cfe/item7-rebuild-venv/bin/python`. **Never `uv run`.**
  - **Proof the run was licensed.** Zero `no live syside license` skip lines. A green run with
    those skips present is not a licensed run and does not discharge this requirement.
  - **Fallback if the license is unavailable at implement time.** The check becomes a **named
    residual**, recorded as one — never silently skipped, and never ticked unverified.

### Where an inapplicability marker actually works (epic scope 5, Item 5 close obligation)

- **[INHERITED: epic scope 5, `:1099-1106`]** The authoring docs state plainly that an
  `@inapplicable:` marker on a **bindings-form** constraint reaches the domain, and that on an
  **inline-predicate** constraint SysIDE silently drops it — so until
  `[INLINE-PREDICATE-MARKER-DROP]` (BACKLOG:1152) closes, that disposition is recorded in the
  fixture's PROVENANCE instead of in source. The worked case
  (`catf_mfe_gated` B1–B5: five markers written, zero carried) and the loud detector
  (`tests/conformance/test_constraint_population_oracle.py` rule 3) are both cited. The test the
  documentation has to pass: a modeler can tell, **before authoring**, which mechanism carries
  their disposition.

### Re-homed orphans (epic scope 4)

- **[INHERITED: epic residuals, `:520-530`]** design-F2 — Appendix C's vacuous-gate cell
  over-permits in the degenerate case and wants "…and at least one gate remains" added
  (`constraint-execution-authoritative-lifecycle-contract.md:793`). Behavior is already settled by
  Item 3 design D4's published RULING (**not assessed**); the contract text is not. Executed here.
- **[INHERITED: epic residuals, `:526-530`]** D9 follow-on — the authoring-time advisory for the
  eligible-plus-`@inapplicable:` combination lands in agentic-mbse authoring guidance. D9 already
  refuses the combination loudly at generation time, so nothing ships wrong; the advisory catches
  it a step earlier.

### The final landed state to document

- **[INHERITED: `completed/20260813_derivative-upgrade-held-intent/`]** Item 9's final state:
  three executing gates (A2, A3, A9), the accounting identity
  `65 = 56 carriers + 9 named deletions` (`tests/fixtures/catf_mfe_gated/PROVENANCE.md:14`,
  restated at `:19-30` with the measured shape), and `[CONSTRAINT-FORM-PER-DIMENSION-COST]` filed
  in BACKLOG:1168.
- **[INHERITED: `completed/20260813_unit-lane-port-metadata/`]** Item 8's final state:
  `modeling-assumptions.md` §8's unit-on-binding account is rewritten to describe authored unit
  text on constraint-formal and computed-attribute ports, with fail-closed
  `SI_RENDERING_COLLISION` on unequal metadata. The current §8 text describes the pre-Item-8
  behavior and is therefore false as written.

### Verification-matrix reconciliation (epic scope 6, Item 5 residual A-8)

- **[INHERITED: epic scope 6 + `[MATRIX-EPIC-SURFACE-ROWS]` `[OWNER]`, BACKLOG:447-466]** Matrix
  rows for the constraint-semantics gates landed across Items 2–5 are filed in
  `docs/architecture/verification-matrix.md` in **one pass**, deliberately not per item — per-item
  filing is how the matrix drifted. The recount discipline applies: index totals and per-family
  counts, not just the summary block (project memory `verification-matrix-drift-modes`). No
  aspirational citations — verify which test pins which claim before citing it.

### Working boundaries

- **[NEED, OWNER 2026-08-14]** The item runs through `close` (archive). The **epic stays open**:
  epic close, `pre_pr`, and any push are reserved to the owner.
- **[NEED, OWNER, standing]** All TEAx edits stay on branch `constraint-semantics-item3`; `main`
  is never touched in any repo. The agentic-mbse surface is the worktree
  `/home/reid/1cfe/agentic-mbse-item7-rebuild` (branch `item7-rebuild`) — the editable install
  reads it.

## Non-Goals

- Any code, fixture, or schema change. This item documents what landed.
- Re-litigating the contract, or re-resolving the promise-vs-basis tension. Both are settled
  above by recorded ruling.
- The derivative fixture docs — Item 5 owns its PROVENANCE and worked example. This item cites
  them; it does not rewrite them.
- Epic close, `pre_pr`, and pushing anything anywhere.

## Open Questions / Deferred to design

- **Exact ADR convention.** The `.project/product/INDEX.md` ledger plus a per-repo ADR convention
  is the default of record; the concrete file layout, id-minting rule, and whether ADR-009 is
  back-registered into it are design's call. Design may refine the shape, not the authority.
- **Sweep-record home.** The method and the record's row format are fixed in the body (Item 1's
  S1–S5, one row per raw hit); where the record file lives — item home vs a per-repo file — is open.
- **Matrix row granularity.** One row per landed gate vs one row per REQ family — settled by
  reading the existing matrix at design time, against the recount baseline (276 rows / 275 PASS /
  32 families as of the last recount, BACKLOG:464-466).
- **Cross-repo access at execution time.** At spec stage the session sandbox is scoped to the
  codegen checkout, so the agentic-mbse and TEAx surface facts in this spec are carried from the
  brief and the epic, not independently re-verified. Design or implement must re-grep both repos
  before relying on any of them.
- **[lens item7-F1 — RESOLVED BY AMENDMENT, `[AGENT, orchestrator 2026-08-14]`]** The sweep is
  Item 1's five-term S1–S5 method, not "three-sweep." Folded into the body: see Known Requirements
  → "Cross-repo documentation sweep" (five terms, DD5 scope, one-row-per-hit, S4 collision, and the
  defined-TEAx-scope requirement). Nothing left open here.
- **[lens item7-F2 — RESOLVED BY AMENDMENT, `[AGENT, orchestrator 2026-08-14]`]** SC1's
  "cited from the product-lens trail" half is now an explicit requirement in the body: see Known
  Requirements → "The promise and its home," last bullet. Which ledger carries the citation stays
  design's call; that the citation is wired is not open.
- **[lens item7-F3 — RESOLVED BY AMENDMENT, `[AGENT, orchestrator 2026-08-14]`]** The licensed-run
  dependency and its fallback are named in the body: see Known Requirements → "Agent prompts and
  skills," last bullet (license source, interpreter, zero-skip-lines proof, named-residual
  fallback). Nothing left open here.
- **Surfaced locator mismatch (not resolved here).** The brief located the item3-F2 parked record
  in the umbrella spec's *Open Questions*; that section carries a different parked item (lens
  spec-F6, D-2 vs D-4/SRC-01, `:324-328`). The item3-F2 conflict is actually carried at
  `spec.md:195` and `:294` plus the epic residual. The requirement above names all three real
  sites. If a fourth site turns up during the sweep, it flips too.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` → "Item 7: ADR, Product
  Promise, and Agent-Facing Documentation Sync" (`:1041-1150`)
- **Owner checkpoint (discharged, pre-captured):**
  `.project/active/constraint-docs-agent-sync/owner-checkpoint-20260813.md`
- **Umbrella contract spec:** `.project/active/constraint-semantics-contract/spec.md`
- **Concepts (glean sources):**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`,
  `.project/concepts/constraint-execution-and-design-space-studies.md`,
  `.project/concepts/constraint-execution-lifecycle-requirements.md`
- **Closed items this documents:** `.project/completed/20260813_constraint-catalog-totality/`
  (Item 2), `.../20260813_constraint-coverage-policy/` (Item 3),
  `.../20260813_catf-constraint-policy-acceptance/` (Item 5),
  `.../20260813_unit-lane-port-metadata/` (Item 8),
  `.../20260813_derivative-upgrade-held-intent/` (Item 9)
- **Product lens:** `.project/active/constraint-docs-agent-sync/product-lens.md` — spec-stage entry,
  **Gate: DISPOSED (item7-F1..item7-F3)**, nothing blocks. Method reconstructed from the in-tree
  ledgers, not the canonical script (which is outside this session's sandbox); the three findings
  are recorded in Open Questions above.
- **Design:** `.project/active/constraint-docs-agent-sync/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
