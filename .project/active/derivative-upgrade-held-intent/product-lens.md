# Product-lens ledger — derivative-upgrade-held-intent (CONSTRAINT-SEMANTICS Item 9)

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they amend.

---

## spec — 2026-08-13 — rev ad7de50 (+ untracked `.project/active/derivative-upgrade-held-intent/`)

Epic: CONSTRAINT-SEMANTICS

**Runner note.** `~/.claude/scripts/product-lens.md` and its pack source
(`/home/reid/agentic-project-init/claude-pack/scripts/product-lens.md`) are outside this session's
sandbox and were refused on every read route. The lens was run from its stated purpose — an
independent two-direction check (does the WORK contradict or narrow the product point; does it omit
an obligation the point requires) — in the ledger format of the sibling ledger
`.project/completed/20260813_catf-constraint-policy-acceptance/product-lens.md`. Every codegen,
fixture, script, and expectation line cited below was opened this session. The TEAx checkout was not
read, so no TEAx-side claim is first-hand.

**Existing epic-level finding against this item (grade preserved, not restated):**
`.project/completed/20260813_catf-constraint-policy-acceptance/product-lens.md` **audit-F5 [DO]**
— **§9/ADR-009 + D-S1/D-S2 (agent/ratified)** — **DISPOSED** by the D-S1/D-S2 ruling, *"carried
forward as an explicit obligation on the epic Item 9 follow-on"* (`product-lens.md:483-495`). This
spec is that follow-on and discharges it: A5/A6 leave the catalog by deletion and A9 moves
`excluded → eligible`, so no instance-reaching physics gate sits outside the denominator.

**Point** (re-derived from SOURCES before the WORK was opened):

1. The derivative is the **worked example of the ruled policy** — its rows must be the shape the
   owner ruled, not the shape a defect allowed. [source: epic Item 9
   `epic_constraint_semantics_contract.md:1260-1291` **[AGENT] ratified by owner**; grade:
   agent/ratified]
2. **The owner decides dispositions, bases, and tolerances; agents execute them.** A parameterization
   is an engineering decision carrying owner sign-off, never a side effect of classification.
   [source: `owner-disposition.md:102-103` A5/A6 basis **[AGENT] ratified 2026-08-13**;
   `:106` A9 **[OWNER 2026-08-13] 1% relative**; grade: owner for the tolerance, agent/ratified for
   the basis]
3. **Every accounting number is a mechanical consequence of the ruled table, never a re-decision and
   never read off a run.** [source: item5-F1 ruling `owner-disposition.md:270-293` **[OWNER
   2026-08-13]**; SC-6 discipline; `gated_manifest/catf_mfe_gated.json` `_comment`; grade: owner]
4. **A deletion is only accepted against outside evidence.** Every `derive-instead` deletion must
   tie to a derivation that exists in source and carries the undirected relation plus the
   chosen-basis statement — the gap that shipped two bare initializers past four gates (audit A-1).
   [source: `owner-disposition.md:37-41` **[OWNER 2026-08-13, structural amendment]**;
   `scripts/check_gated_manifest.py:200-241`; grade: owner for the obligation, agent for the check]
5. **Surfacing beats absorbing.** A ruled form that cannot be built, or a number that moves when the
   arithmetic says it should not, is an owner event — not a re-baselined expectation.
   [source: capture-fidelity law 4; Item 5's D-S1/D-S2 precedent; grade: rule]

**Falsifier:** a landing where a ruled row is quietly re-shaped to fit the tooling; where a deletion
closes the identity on a citation alone because the prover could not distinguish 27 near-identical
derivations; or where a record whose stated cause is now gone is left standing as if still true.

**Verdict: CONCERNS.** Nothing in the spec contradicts or narrows the ruled point. It reproduces the
held intent faithfully — the A5/A6 basis, A9's 1% relative band and target form, O6's edit count, the
restated `65 = 56 + 9` identity and its 53-by-name/3-by-rename split all check out against source,
and the `[HARD]` arithmetic claim (every `outer_radius` literal equals `inner_radius + thickness`,
every `inner_radius` equals the layer below's `outer_radius`) was verified line by line across all
14 layers in `tests/fixtures/catf_mfe_gated/designs/catf_mfe/radial_build.sysml:57-560`. The
findings below are executability gaps and un-surfaced stale records, not re-dispositions.

### Findings

- **F1 [DO] — the "disposition table" success criterion names no file, and the only artifact that
  fits is an archived owner-graded document.** SC-3 requires the `blocked-by-defect` markings gone
  "from PROVENANCE §3a and from **the disposition table's** A5/A6/A9 rows" (`spec.md:67-68`),
  echoing the epic's "retired from table and PROVENANCE" (`epic_...:1275-1276`). The only disposition
  table is `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md:102-106`
  — a closed, archived, owner-ruled artifact. It appears in neither the `[HARD]` "artifacts that must
  move together" list (`spec.md:173-177`) nor the staging rules (`:216-218`). So a mechanical
  implementer either skips the criterion or edits a closed owner record in place, and the spec gives
  no instruction on which. — source: epic Item 9 SC-1 (agent/ratified), `owner-disposition.md` (owner
  rulings) — **disposition:** name the artifact and the manner. Recommend: the archive stays
  immutable and the retirement is recorded in this item's own records plus PROVENANCE §3a, with a
  dated pointer line if the archived table is touched at all.

- **F2 [DO] — the prover requirement as written cannot pass: 14 of the 27 derivations are
  byte-identical lines, and the existing check refuses a non-unique initializer.**
  `spec.md:182-185` requires only that `DERIVATIONS` "accept a set" instead of one initializer per
  deleted usage. But `check_derivations` matches an initializer as a substring and fails the row
  outright when `len(matches) > 1` (`scripts/check_gated_manifest.py:219-227`), and A6's derivation
  is the same text — `attribute outer_radius : Real = inner_radius + thickness;` — in all 14 layers.
  A set of identical strings still trips the uniqueness guard; the alternative failure (matching only
  the first occurrence) would accept 13 undocumented derivations, which is exactly the A-1 gap the
  check exists to close. — source: `owner-disposition.md:37-41` derivation documentation obligation
  (**[OWNER 2026-08-13]**), prover (agent) — **disposition:** state the requirement per *occurrence*,
  not per row: each of the 27 derivations resolves to one identified declaration and its own comment
  block, and both falsification cases fail closed for **each** layer, not for the row.

- **F3 [DO] — three PROVENANCE §1 records go false and the spec's PROVENANCE obligation names only
  §3a.** SC-3 and the artifacts list cover §3a and the deletion records. Untouched are §1's
  *"`ProductWithinBand` is deliberately not authored"* (`PROVENANCE.md:33-36`), *"A5, A6, A9 are left
  exactly as `catf_mfe_d5` wrote them"* (`:96`), and *"The axis-region layer is not derived … One
  consistent basis, per the D-S2 ruling"* (`:98-103`) — all three are reversed by this item, the
  third being precisely the leg the spec's `[INHERITED]` note un-parks (`spec.md:131-134`). §2's
  heading and its `65 = 58 carriers + 7 named deletions` line move too. — source: fixture
  `PROVENANCE.md` (agent, orchestrator-confirmed) — **disposition:** add the §1/§2 records to the
  `[HARD]` artifacts list, each retired by amendment (law 3: shrink or amend), citing Item 8's fix
  commit as the cause.

- **F4 [DO] — the entry-point surface change is predictable and unnamed; only module count is
  flagged as measured.** `spec.md:171-172` says the module count is not predictable and is measured.
  The larger, *predictable* change is unstated: all 27 radii are today literal design attributes
  consumed by calc usages (`in r_inner = plasma_region::inner_radius`,
  `radial_build.sysml:97-98` and per layer), so each mints a `DESIGN_ATTRIBUTE` entry point in the
  generated schemas and inputs JSON (ADR-001, `CLAUDE.md`). Once derived they stop being entry points
  and 27 public input keys disappear. Any consumer keyed on a radius input breaks. The study
  expectation reads `p_fusion = 20000.0, all else authored`
  (`gated_manifest/catf_mfe_gated.json:88`), so no committed artifact pins those keys today — but
  the spec should say the surface moves rather than leave it to be discovered at implement. —
  source: ADR-001 entry-point classification (`CLAUDE.md`, product doc) — **disposition:** name the
  entry-point/inputs-schema surface alongside module count as measured-not-assumed, and record the
  27 removed keys in the implement record.

- **F5 [DO] — A9's removal from the SC-5 candidate set rests on a cause this item cures, and the
  spec resolves that silently.** The owner endorsed probing all three candidates and recorded A9's
  mutation lever — *"Change `n_pumps` or `pump_capacity_each` so the product leaves the approved
  band"* (`owner-disposition.md:321`, **[OWNER 2026-08-13] Endorsed as laid out** at `:329`). D-S1
  then put A9 *"out of the SC-5 candidate set"* (`:333`) **because of the defect Item 8 fixed**. The
  spec restores A9 as an executing gate but concludes only that it *"adds a satisfied gate and does
  not move the fixture's `violation` headline"* (`spec.md:151-154`), never naming the D-S1 record
  whose stated cause is gone. That is a premise-conflict resolved in passing. — source: D-S1 ruling
  (agent/ratified) over an owner-endorsed candidate table (owner) — **disposition:** surface it in
  one line: A9 re-enters or stays out of the SC-5 candidate set as an explicit, stated choice, with
  the D-S1 record amended to say the defect-based exclusion has lapsed. Do not add a mutation case
  under this item's 0.5-day boundary without an owner ruling.

- **F6 [note] — stale citations and stale counts inside artifacts this item must rewrite.** The
  manifest expectation's `_comment` cites `.project/active/catf-constraint-policy-acceptance/owner-disposition.md`
  and its `_basis` cites `.project/active/…/cryo_derivation.py`
  (`gated_manifest/catf_mfe_gated.json:2-7`, `:80`); both moved to `.project/completed/20260813_…/`
  at Item 5 close, so the SC-6 evidence chain path-cites a directory that no longer exists. The
  prover's module docstring states the identity as `65 = 58 carriers + 7 deletions`
  (`scripts/check_gated_manifest.py:1`), and `histogram_rows` describes A5/A6/A9 as excluded
  (`:102-106`). — source: derived (agent) — **disposition:** fold a citation-and-count sweep into the
  same commit as the restated identity.

- **F7 [note] — two small transcription drifts in pre-committed expectations.** (a) The expected
  ledger row `catf_mfe_gated | 56 | 3 | 3 | 0 | 0 | {} | violation | 3` (`spec.md:166-167`) drops the
  `complete` column the real table carries between `{}` and the headline
  (`tests/unit/data/expected-coverage.md:347`); the bullet above it has the column, so this is a
  transcription slip in the row an implementer would copy. (b) O6 is quoted as *"~27 edits"*
  (`spec.md:51`, `:119`) where the source says **27**, exactly
  (`owner-disposition.md:368-369`); the tilde entered via the orchestrator brief. The spec's own
  `[HARD]` pins 13 + 14 = 27, so no number is wrong — only the quotation. — source:
  `owner-disposition.md` O6 (owner-ratified), coverage ledger (agent) — **disposition:** correct both
  in place.

- **F8 [note] — N-4's second side is already present in the backlog entry; adding a line risks
  accretion.** `spec.md:194-198` requires `[INLINE-PREDICATE-MARKER-DROP]` to gain one line so the
  next owner inherits the B1–B5 obligation from the entry. The entry already closes with *"an
  inapplicability disposition on an inline-predicate usage has to be recorded in PROVENANCE instead
  of in source (the Item 5 workaround that epic Item 9 retires)"* (`BACKLOG.md:1157-1160`). The
  two-sided recording the owner ruled is satisfied in substance; a second statement of it is the
  accretion law 3 forbids. — source: **[OWNER 2026-08-13, ruled at Align]** via
  `briefs/spec.md:44-52` (owner) — **disposition:** amend the existing sentence to name the
  migration (move the five markers from PROVENANCE into source) rather than appending a new line,
  and record that the ruled obligation was met by amendment.

**Not checked / out of scope:** the TEAx lane and `expected_study_outcomes`' runtime tokens
(no TEAx checkout read); sibling-item obligations (Items 6, 7 not run); whether the ruled A5/A6/A9
target forms in fact generate at Item 8's fix commit — that is design's probe, and any refusal is a
surfacing event under this spec's own Non-Goals, not a lens finding.

---

### Disposition — spec, 2026-08-13

All eight findings accepted and folded into `spec.md` in the same session; none blocks.

- **F1** → requirement **P-1**, ruled by the orchestrator the same day (`[AGENT]`, 2026-08-13):
  **freeze the archive.** `owner-disposition.md` stays byte-untouched and Item 9 verifies it so;
  the retirement lands on the live surface (the fixture's PROVENANCE) and this item's records.
  The open question the first draft carried is closed by that ruling and removed.
- **F2** → the prover requirement is now **per-occurrence**, naming the 14 byte-identical A6 lines
  and the uniqueness refusal at `check_gated_manifest.py:219-227`.
- **F3** → the PROVENANCE obligation enumerates §1's three now-false records, §2's heading and
  identity, and the measured-shape paragraph — not just §3a.
- **F4** → new requirement: up to 27 `DESIGN_ATTRIBUTE` input keys leave the generated schemas,
  recorded before/after, with any other key movement a surfacing event.
- **F5** → new requirement to record that A9 re-enters the SC-5 candidate set, since D-S1's cause
  is cured. A record, not a re-disposition.
- **F6** → the stale citations are corrected in the same pass that rewrites those artifacts.
- **F7** → the ledger row is restated with its `complete` column; O6 is quoted as 27 exactly.
- **F8** → N-4 side 2 is an **amendment** of `BACKLOG.md:1158-1159`'s now-false sentence, not an
  added line.

---

## design — 2026-08-13 — rev 2c624cc

Epic: CONSTRAINT-SEMANTICS. Run at `design_review`, over `design.md` (WORK) against the durable
product statements (SOURCES).

**Runner note.** Same constraint as the spec-stage block above: `~/.claude/scripts/product-lens.md`
and its pack source are outside this session's sandbox and were refused again on read
(`ls` blocked, 2026-08-13). The lens was run from its stated purpose — an independent two-direction
check (does the WORK contradict or narrow the product point; does it omit an obligation the point
requires) — in this ledger's format. SOURCES read this session: `CLAUDE.md`, `owner-disposition.md`,
the fixture's `PROVENANCE.md`, `scripts/check_gated_manifest.py`,
`tests/conformance/test_gated_manifest_identity.py`,
`tests/expectations/gated_manifest/catf_mfe_gated.json`, and the fixture `.sysml` sources.
`.project/adr/` and `.project/product/` do not exist in this tree (verified), so there is no ledger
index to read first.

**Point** — carried unchanged from the spec-stage block (points 1–5). It was re-derived there from
SOURCES and nothing in SOURCES has moved since; re-deriving it a second time would restate, not
check.

**Verdict: CONCERNS.** The design does not contradict or narrow the point. It executes held intent,
adapts no ruled form, and strengthens point 4's deletion gate from per-row to per-occurrence. Two
findings are omissions against the point, not contradictions of it.

### Findings

- **D-F1 [DO] — point 2 ("the owner decides… agents execute") is met in substance but not made
  checkable for A9.** The design records that `ProductWithinBand`'s def-shape changed materially
  (genericity lost) and states that *"the relative form and the 1% value are all exactly as ruled"*
  (`design.md:205-206`), but the predicate that carries the relative form is written nowhere in the
  design. A reader cannot check the ruled semantics — band scales under design-search resizing
  (`owner-disposition.md:106`, **[OWNER 2026-08-13]**) — against an unwritten predicate. The probe
  already authored one (`probes/apply_item9_edits.py:132-139`) and it does preserve the semantics.
  — source: A9 row (owner) — **disposition:** carry the predicate into the design and check it
  against the row there.

- **D-F2 [DO] — point 5 ("surfacing beats absorbing") is honoured in the design doc but not on the
  live surface.** The one-ULP float drift (`design.md:408-416`) and the out-of-27 `tf_coil.thickness`
  comment edit (D3) are both recorded only in `design.md`, which archives with the item. The
  fixture's `PROVENANCE.md` is the live record a later reader opens. — source: capture-fidelity
  law 4 (rule); `PROVENANCE.md` as the live surface (agent, orchestrator-confirmed) —
  **disposition:** fold both into the PROVENANCE edit pass the design already plans.

### Structural smells (product-lens spec §4)

- **"Consumer compensating for a platform guarantee" — FIRED, and disclosed.** A constraint
  formal's port unit is read from the formal's own declaration, so a generic band cannot carry a
  unit and `ProductWithinBand` must be authored per dimension. The fixture pays a
  one-definition-per-dimension cost for a platform modeling limit. The design does not hide this —
  it is the substance of its NOTE (`design.md:186-206`) and it names the cost explicitly. Escalated
  to the judgment and dismissed there: disclosed, ruled-form-preserving, and correctly scoped out
  of this item. Recommend one unowned backlog line so the cost is findable outside an archived
  design doc.
- **"Changes who owns an invariant without saying so" — did not fire.** The prover's move from
  per-file-unique matching to per-occurrence anchoring strengthens the same owner-held
  obligation and is stated as such (D5).
