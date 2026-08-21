# Implementation Plan: Scaffolding Reinstall and Register Boundary

**Status:** Certified — audit 2026-08-21 at `3566fdd` (`audit.md`)
**Created:** 2026-08-21
**Last Updated:** 2026-08-21 (Phase 5 complete; ready for independent audit)

## Source Documents

- **Spec:** `.project/completed/20260821_scaffolding-register-boundary/spec.md`
- **Design:** `.project/completed/20260821_scaffolding-register-boundary/design.md` ← component detail,
  architecture, bets, decisions, invariants, gotchas all live there
- **Epic:** `.project/backlog/epic_repo_cleanup.md` — Item 1
- **Product-lens:** `.project/completed/20260821_scaffolding-register-boundary/product-lens.md` (spec run, DISPOSED)

## The Point

The product is three steps: parse the models with a SysML v2 parser, walk the AST to reconstruct the
math, write it into TEAx Python — and any manual fallback for an unresolved reference is a smell,
because ill-formed models are refused with a diagnostic rather than accommodated.
`[OWNER-VERBATIM, 2026-08-16]`, `.project/product/0004` and `0003`.

This work does not touch that product. It serves it one hop back. Those two promises are written
down precisely so a future agent cannot quietly undo them, and the ledger's own contract is *"if a
promise is not reachable from here, it has no home."* Today that ledger is maintained by hand
against a specification saying a script owns it, and the repo has two places to file a decision with
no rule for which. A promise-keeping mechanism that has already started to drift is the problem.

**The obligation every phase is checked against: the four promises come out reachable, unaltered,
and correctly graded.** Two of them are the owner's verbatim words. If a phase would trade any of
those three properties for convenience, stop and surface it.

## Implementation Strategy

**Phasing Rationale.** The only step that could re-scope this item is whether a prepended
frontmatter block is legal and readable on an append-only entry, so that goes first on a throwaway
copy where being wrong is free. Everything after it is ordered by hard dependency: the engine must
exist before the ledger can be migrated onto it, and the register must exist before decisions can be
filed into it. The design's own decisions are filed last because `adr.sh` — the thing that allocates
their ids — is installed by this same item.

**Critical Path.** Prove the frontmatter shape → install the engines → migrate the ledger →
file the criterion and triage → write back and validate.

**First Proof Point.** End of Phase 1: a scratch copy of `P-003` carrying a prepended frontmatter
block, where `product.sh index` emits its row and the prose below the block diffs clean against the
original. If that works, nothing else in this item is architecturally uncertain.

**Overall Validation Approach.** Invariants I1–I6 (`design.md#required-invariants`) are the
acceptance surface. I1, I2 and I5 become real tests in the conformance suite rather than one-time
manual checks, and they are written before the migration they guard. Every phase ends with the full
suite green.

**Risk lowered since the design.** B3 is close to settled by the pack's own code: `supersede`,
`amend` and `check` all call `set_field` to rewrite frontmatter in place on already-filed entries
(`product.sh:211-213, 230-236, 249`). Frontmatter is the designed-mutable surface; "the body is
immutable" governs the prose. Phase 1 is therefore a mechanical confirmation, not a genuine kill
gate — but it still runs, because the line-1 parsing gotcha fails silently.

---

## Phase 1: Prove the Migration Shape on a Throwaway Copy

### Goal

Confirm that a prepended YAML frontmatter block is readable by `product.sh` and leaves the entry's
prose byte-identical. No register or scaffolding target under `.project/` is touched; only the
required phase record and progress tracking change.

### Assumption Under Test

**B3** (`design.md#key-bets`) — prepending frontmatter is a metadata addition, not a body mutation,
so the migration is four renames rather than four supersessions. Plus the line-1 gotcha from
`design.md#implementation-notes`: `field()` requires `---` at `NR==1`, and a leading blank line makes
every field read empty **without erroring**.

**Kill criterion:** if the prose cannot survive the prepend byte-identical, or if `field()` cannot
read a prepended block, stop and re-scope the item as four supersessions. Report before proceeding.

### Test Stencil (Write This First)

```bash
# scratch: $T=$(mktemp -d)/product ; cp P-003 -> $T/0003-no-workarounds-for-bad-models.md
# 1. prepend the block, then:
PRODUCT_DIR=$T product.sh index
grep -q '^- 0003 · ' $T/INDEX.md                      # entry is discoverable
# 2. prose survived:
diff <(sed '1{/^---$/!q1}; 1,/^---$/d; 1,/^---$/!d' new) original   # empty
# 3. the gotcha is loud, not silent:
#    insert a leading blank line -> field() returns empty -> row vanishes from INDEX.md
```

### Changes Required

**See `design.md` for:** the frontmatter schema and field semantics →
`design.md#research-findings`; the gotcha → `design.md#implementation-notes`.

- [x] Create a scratch product register outside the repo; copy `P-003` in under its target name
- [x] Derive and prepend the frontmatter block from what the entry already states
- [x] Run `product.sh index` against the scratch register; confirm the row appears
- [x] Diff the prose below the block against the original — empty
- [x] Reproduce the leading-blank-line failure and record what it looks like
- [x] Record the outcome in `.project/completed/20260821_scaffolding-register-boundary/phase1-findings.md`

### Validation

**Automated:**
- [x] Scratch `INDEX.md` contains the `0003` row with its title
- [x] Prose diff is empty

**Manual:**
- [x] Blank-line variant reproduces the silent-empty-field mode and it is written down

**What We Know Works After This Phase:** the migration mechanism, and the shape of its worst
failure mode. No product-register or scaffolding target in the repo has changed.

**Owner disposition:** `[OWNER, 2026-08-21]` The owner accepted the recorded missing-manifest
environment limitation and authorized Phase 2. The exact full-suite gate remains unavailable, not
green.

---

## Phase 2: Install the Scaffolding

### Goal

`adr.sh`, `product.sh`, `adr/README.md` and `product/README.md` present; the four stale pack files
refreshed; nothing else disturbed.

### Assumption Under Test

`init-project.sh --force` merges without collateral damage — it updates exactly the four differing
template files and adds exactly the four missing ones, and does not touch `CURRENT_WORK.md`,
`BACKLOG.md`, `CHANGELOG.md`, or `memories/index.json`.

### Test Stencil (Write This First)

```bash
# The dry run IS the first test. Capture and inspect it before the real run.
/home/reid/agentic-project-init/scripts/init-project.sh \
  --source /home/reid/agentic-project-init --force --dry-run > /tmp/dry.txt
grep -c 'Would add'    /tmp/dry.txt   # 4: adr.sh, product.sh, adr/README.md, product/README.md
grep -c 'Would update' /tmp/dry.txt   # 10: --force reports 4 differences and 6 identical files alike
grep 'Protected'       /tmp/dry.txt   # the four user-data files, untouched
# Classify reported updates with cmp before installation: expect 4 different and 6 identical.
```

### Changes Required

**See `design.md` for:** the install decision and why not hand-copying → `design.md#key-decisions`
(D1); the measured diff → `design.md#research-findings`.

- [x] Run the dry run from the repo root and review it against the expected counts above
- [x] **Do not pass `--include-claude`** — `.claude/` here is a real directory, not a pack vendor point
- [x] Run for real; commit the scaffolding as its own commit so the migration diff stays readable
- [x] Run the pack's `test_adr.sh` and `test_product.sh` against this checkout

### Validation

**Automated:**
- [x] Byte-level dry-run census matches; no protected file appears as updated
- [x] `test_adr.sh` and `test_product.sh` pass
- [x] The installation delta contains only the expected eight files

**Manual:**
- [x] `.project/EPIC_GUIDE.md` now contains the Slicing Principles section
- [x] `adr.sh new --help`-equivalent path works from the repo root

**What We Know Works After This Phase:** both engines run here, and the installer did not eat
anything.

### Phase 2 Completion — 2026-08-21

- The installer was run from its actual pack location,
  `/home/reid/agentic-project-init/scripts/init-project.sh`, without `--include-claude`.
- With `--force`, its dry run reported all ten existing non-protected pack files as updates. A
  pre-install byte census separated four real differences from six identical no-ops. It also found
  the planned four additions and all four protected files.
- The protected files, the existing product index, and all four promise entries retained their
  pre-install SHA-256 hashes. `.claude/` was untouched.
- The eight-file scaffolding change is commit `59ed5b9` (`chore(project): install decision register
  scaffolding`) on the existing `repo-cleanup` branch. The spec's stale `main` branch label was
  corrected to match the checkout.
- Pack validation passed: `test_adr.sh` 32/32 and `test_product.sh` 46/46. The installed scripts are
  byte-identical to the tested pack scripts. The Slicing Principles and repo-root usage checks also
  passed.
- Licensed working-checkout validation passed every runnable test: 2,371 passed and 9 policy skips.
  Nine files that require the unavailable external artifact manifest were omitted before
  collection; pytest separately deselected 94 `execution`-marker tests by project default. The
  focused product-document contract passed 1/1. Per the owner's Phase 1 disposition, the exact
  full-suite gate remains unavailable rather than green.

---

## Phase 3: Migrate the Ledger

### Goal

The four promises are named `000N-<slug>.md`, carry accurate frontmatter, are reachable from a
generated `INDEX.md`, and every citation resolves in both directions.

### Assumption Under Test

**B2** (`design.md#key-bets`) — nothing outside the four files and the one conformance test depends
on the `P-00N` filename form in a way a mechanical repoint cannot fix.

### Test Stencil (Write This First)

Write these as conformance tests **before** moving anything. I1 and I5 fail today; that is correct.

```python
def test_every_indexed_promise_resolves_to_exactly_one_entry() -> None:      # I1
    for entry_id in _ids_in(_read(".project/product/INDEX.md")):
        assert len(list(PRODUCT.glob(f"{entry_id}-*.md"))) == 1

def test_product_index_is_a_faithful_regeneration() -> None:                 # I5
    assert _read(".project/product/INDEX.md") == _regenerate_index()
```

### Changes Required

**See `design.md` for:** the id map → `design.md#key-decisions` (D2); reachability-by-naming-rule →
D3 and `design.md#required-invariants` (I1); the per-entry data flow → `design.md#architecture`.

#### 1. Conformance tests (NEW assertions — write first)
**File:** `tests/conformance/test_stop_parser_documentation_contract.py`
- [x] Add the I1 and I5 tests above
- [x] Leave the owner-quote assertions at `:208-245` **unchanged** — only the two read paths move
- [x] Re-express `assert "P-003-….md" in index` as an id-plus-resolution check (I1's form), never delete it

#### 2. The four entries
- [x] `git mv` each `P-00N-<slug>.md` → `000N-<slug>.md`, preserving slugs (D2)
- [x] Prepend frontmatter; backfill `date` and `owner` from each file's git history, not today
- [x] Map provenance: `0003`/`0004` → `[OWNER]` with the verbatim quote staying in Authority
      (the pack's documented first-capture shape); `0002` → `[AGENT] (ratified by owner, 2026-08-16)`;
      `0001` grades the **summary**, not what it cites
- [x] Verify I2 per file: below the block, the diff contains only the five approved Markdown
      destination repoints and no visible-text or owner-payload change

#### 3. Index and citations
- [x] `product.sh index`; commit the generated `INDEX.md`
- [x] Re-derive the live citation set with `grep -rl 'P-00[0-9]'` — **do not use the 2026-08-20 list**
- [x] Repoint the live sites. Hand-check `CLAUDE.md` and `.project/backlog/BACKLOG.md`; both are read
      by tooling and by every session, so a sloppy sweep there is more damaging than a renamed file
- [x] Confirm I4's other direction: every path cited *by* an entry still resolves

### Validation

**Automated:**
- [x] I1, I5 tests pass; owner-quote assertions still pass unchanged
- [x] Licensed runnable suite green under the accepted missing-manifest disposition; the exact full
      suite remains unavailable rather than green
- [x] `grep -rn 'P-00[0-9]'` returns no live site expecting the old form

**Manual:**
- [x] Read the generated `INDEX.md` end to end — can a cold agent get from it to each promise?
- [x] Spot-check `0001`'s Authority citations resolve

**What We Know Works After This Phase:** the ledger is script-managed, reachable, and no citation
dangles.

**Implementation ruling:** literal body byte identity conflicted with outbound citation integrity:
five relative links inside the renamed entries named files that no longer existed. The agent
recommended repointing only those hidden destinations while preserving all visible prose and owner
payload; the owner ratified that recommendation on 2026-08-21. I2 and the spec are amended to state
the exact exception rather than silently choosing one invariant over the other.

---

## Phase 4: File the Criterion, Triage the Nine, Fix the Docs

### Goal

`.project/adr/0001` carries the routing rule; all nine existing ADRs have a recorded triage outcome;
no document claims a single ADR home.

### Assumption Under Test

**B4** (`design.md#key-bets`) — one abstract routing question is enough to file correctly without a
per-subject list. Applying it to nine real entries is the test: if any of the nine cannot be routed
without appealing to its subject matter, the criterion is under-specified and needs rewording before
it is filed.

### Test Stencil (Write This First)

```python
def test_no_document_claims_a_single_adr_home() -> None:                     # I6
    for path in ("CLAUDE.md", ".project/product/README.md", ".project/product/INDEX.md"):
        text = _read(path)
        assert "no separate" not in text.lower() or "two register" in text.lower()
        # and: .project/adr/ is named as a register wherever the convention is described
```

### Changes Required

**See `design.md` for:** the criterion's shape and why it must generalize →
`design.md#core-concept`; the citation form → D4; where displaced index prose lands → D5.

- [x] `.project/scripts/adr.sh new <criterion-slug>` — never hand-mint the id
- [x] Write the rule as **one question** answerable without a subject list, so the claude-commands
      work can cite it rather than re-derive it. Set `provenance: "[OWNER]"`; it is settled
- [x] Triage all nine against it into
      `.project/completed/20260821_scaffolding-register-boundary/adr-triage.md`. **Move nothing**
      `[OWNER, 2026-08-21]` — record §§1–6 and 8 as author-facing, and ADR-007 plus ADR-009 as
      builder-facing with their re-homes carried to Item 3 (epic step 2a)
- [x] Rewrite the ADR-convention paragraph in `CLAUDE.md` and add D4's citation form
- [x] Add the repo-local section to `.project/product/README.md`: the id rule, the `<id>-*.md`
      resolution rule, and the two-register convention (D5)
- [x] `adr.sh index`

### Validation

**Automated:**
- [x] I6 test passes; the licensed runnable suite is green under the accepted missing-manifest
      limitation
- [x] `adr.sh index` output equals the committed `.project/adr/INDEX.md`

**Manual:**
- [x] I3: read each entry's `provenance` against its own prose; record agreement in the triage doc
- [x] Apply the criterion without a subject list to three representative entries (§1, §7, §9).
      The owner independently confirmed the disputed §7 route from its binding sentence

**What We Know Works After This Phase:** a cold agent can route a new decision, and the register the
epic's later items file into exists.

### Phase 4 Completion

**Completed:** 2026-08-21 09:12 PDT
**Phase status:** Complete; awaiting owner authorization for Phase 5

**Changes Made:**
- Allocated `.project/adr/0001-route-decisions-by-who-they-bind.md` through `adr.sh new`, filled the
  owner-grade routing question, and generated `.project/adr/INDEX.md`.
- Triaged all nine existing decisions. Sections 1–6 and 8 bind model authors; ADR-007 and ADR-009
  bind system builders and are carried to REPO-CLEANUP Item 3 for re-homing. Nothing in
  `modeling-assumptions.md` moved.
- Recorded the I3 provenance review for all four product entries in `adr-triage.md`.
- Replaced the single-home convention in `CLAUDE.md` and added the id resolution, two-register rule,
  and path-qualified citation form to `.project/product/README.md`.
- Added red-first I6 and criterion-discoverability tests to the documentation contract.

**Issue Surfaced:**
- ADR-007 says downstream code never re-derives identifiers, so the new criterion classifies it as
  builder-facing. The owner confirmed that classification on 2026-08-21. Item 3 now owns ADR-007's
  re-home beside ADR-009's.

**Validation:**
- The two new contract tests failed before implementation for the expected missing-path reasons,
  then passed. The safe documentation contract passed 12/12 with its three manifest-dependent tests
  deselected; the edited test passes Ruff.
- The triage contains nine outcomes, the four provenance fields agree with their bodies, and three
  representative decisions route from the audience question without a subject list. The owner
  independently routed the disputed ADR-007 case.
- Two `adr.sh index` runs produced identical SHA-256
  `1b20ba5eaf93f20cb9360a6352f42ce925786d1866ac63a3918c6ca32aa2c11f`.
- Licensed runnable suite: 2,371 passed, 9 policy skips, and 94 default `execution`-marker
  deselections. Nine manifest-dependent test files were omitted before collection under the
  owner's accepted Phase 1 limitation. The exact full-suite gate remains unavailable, not green.
  The omitted files are `test_v6_snapshot_inventory.py`, `test_check_ledger_4a.py`,
  `test_ast_dispatch_invariant.py`, `test_exact_route_fingerprint_stability.py`,
  `test_hierarchy_resolver.py`, `test_probe_fixture_lock.py`,
  `test_self_binding_guidance_contract.py`, `test_stop_parser_documentation_contract.py`, and
  `test_check_proof_integrity.py`. The safe subset above exercises this phase's documentation tests.

**Validation-record correction:**
- The earlier Phase 2/3 notes conflated the nine omitted manifest-dependent files with pytest's 94
  default execution-marker deselections. The runnable result remains 2,371 passed / 9 skipped; the
  two categories are now recorded separately.

---

## Phase 5: Write Back the Design's Decisions and Close

### Goal

The decisions this design settled are filed in the register it built, and every invariant is green.

### Assumption Under Test

None new. This phase closes the loop the design flagged: it could not file its own decisions because
`adr.sh` did not exist yet.

### Test Stencil (Write This First)

```bash
# The full invariant sweep is the test. All six, in one run.
uv run --extra dev pytest tests/ -k "product_ledger or adr_home or documentation_contract"
.project/scripts/product.sh index && git diff --exit-code .project/product/INDEX.md   # I5
.project/scripts/adr.sh index     && git diff --exit-code .project/adr/INDEX.md
```

### Changes Required

**See `design.md#key-decisions`** for D1–D6 and their rejected alternatives — the bodies are already
written there and need only be carried into entries, cited not restated.

- [x] File the decisions that pass the density bar in `.project/adr/README.md`. Expect **few**:
      D3 (reachability by naming rule, not an index fork) and D4 (cite by register path) are the
      load-bearing ones a future agent could plausibly re-derive wrongly. D1, D2 and D5 are
      mechanism detail the design already records — cite, do not re-file
- [x] D6 is a deferral, not a decision this design settled; it is recorded in the epic's Item 3 and
      the triage doc, and gets no entry
- [x] `product.sh check <id> <ref>` on all four promises — stamp only now that I1–I3 pass
- [x] Update `.project/CURRENT_WORK.md` from "spec in progress" to the completed state

### Validation

**Automated:**
- [x] I1–I6 all green
- [x] Licensed runnable suite green with `SYSIDE_LICENSE_KEY` loaded under the accepted
      missing-manifest limitation
- [x] Ruff clean; mypy holds the established zero-new gate at 30 errors in 8 files
      `[AGENT] (ratified by owner, 2026-08-21)`

**Manual:**
- [x] Re-read `design.md#the-point`: are the four promises reachable, unaltered, and correctly
      graded? That is the item's acceptance, not the checklist above

**What We Know Works After This Phase:** the item is done and Item 2 can start.

---

## Environment Setup

**See CLAUDE.md.** The license matters here: without `SYSIDE_LICENSE_KEY` the gated tests skip
rather than fail, so a green run with no key is not a full run. Load it with
`set -a; source ../agentic-mbse/.env; set +a`.

## Risk Management

**See `design.md#potential-risks`.**

**Phase-Specific Mitigations:**
- **Phase 1** — being wrong is free; nothing in the repo is touched until the mechanism is proven
- **Phase 2** — dry run reviewed before the real run; scaffolding committed separately so the
  migration diff stays readable
- **Phase 3** — the citation sweep is re-derived with `grep`, never from a remembered list;
  `CLAUDE.md` and `BACKLOG.md` are hand-checked rather than swept
- **Phase 4** — if any of the nine cannot be routed without appealing to its subject, the criterion
  is reworded before filing, not after
- **Phase 5** — `check` stamps come last, so no promise is marked verified before it is

## Implementation Notes

### Phase 1 Completion
**Proof completed:** 2026-08-21 07:54 PDT
**Phase status:** Implementation complete; exact full-suite disposition required before Phase 2

**Actual Changes:**
- Added `phase1-findings.md` with the isolated proof record.
- Built a scratch product register under `/tmp/scaffolding-register-boundary-phase1.bDGvKX`.
- Confirmed the generated `0003` row and byte-identical promise body. Both body hashes were
  `ffdbdf03991965c252005da39d4cc28149f4c4ab1d4b0cd2b7ff62dd48ec5f32`.
- Reproduced the line-1 parser failure. No product-register file in this repository changed.

**Issues:**
- The source `product.sh` ignores a `PRODUCT_DIR` environment override. The test ran the
  unmodified script from an isolated temporary project root instead.
- A leading blank line does not remove the entry from generated output completely. It removes the
  identifiable row and leaves an empty `-  ·  · ` ghost row while exiting successfully.

**Deviations:**
- Replaced the non-functional environment override in the test stencil with an equivalent
  scratch-project-root isolation. The phase goal and production script were unchanged.
- Corrected the phase wording that said nothing under `.project/` would change. The required
  findings and progress records changed; no register or scaffolding target did.

**Validation:**
- Scratch index row, body byte comparison, blank-line failure, and `git diff --check` passed.
- The direct documentation-contract run passed 8 tests, including the owner-verbatim product
  assertions. Its remaining 3 tests refused the absent hash-identified artifact manifest.
- The licensed working-checkout suite, excluding the six modules that cannot collect without that
  manifest, finished **2,387 passed / 9 skipped / 10 failed / 2 errors**. Every failure and error
  was the same `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` refusal in three additional process-evidence
  modules; no product assertion failed.
- No manifest for current commit `da15f14138249ac507e1ad74e01da8ad50f9fb04` exists locally.
  Building one requires the separate five-repository artifact pipeline. The plan's exact full-suite
  gate is therefore pending owner disposition, not marked green.

### Phase 2 Completion

### Phase 3 Completion

**Completed:** 2026-08-21 08:35 PDT
**Phase status:** Complete; awaiting owner authorization for Phase 4

**Changes Made:**
- Added real I1 and I5 conformance tests. They failed before migration because the manual index ids
  resolved to no `000N-*` files and differed from a fresh `product.sh index`, then passed after it.
- Renamed the four entries to `0001`…`0004`, preserving every slug. Added full script-managed
  frontmatter, including the lifecycle link fields omitted by the plan's shorthand schema.
- Backfilled `date` and `owner` from each file's first Git commit: 2026-08-14 / `rwestwood89` for
  `0001`; 2026-08-16 / Reid W for `0002` and `0003`; 2026-08-17 / Reid W for `0004`.
- Regenerated `INDEX.md` twice through the installed engine. Both runs produced SHA-256
  `cb0dabb4443c6459680b97621df4bc29500da97ac68d4be6a5ef560ba28016e8`.
- Re-derived the live inbound citation set from the checkout, repointed it to the `000N` names,
  and hand-checked `CLAUDE.md` and `BACKLOG.md`. All outbound authority/evidence paths resolve.

**Issues Encountered:**
- Five relative links inside the immutable promise bodies named the files being renamed. Literal
  body byte identity and outbound citation integrity could not both hold. The agent recommended a
  five-destination-only exception; the owner ratified it on 2026-08-21. The spec, design, and plan
  now state the narrowed invariant. Visible prose and owner payload did not change.

**Deviations from Plan:**
- Added `amended_by`, `superseded_by`, and `supersedes` to every frontmatter block. The installed
  lifecycle commands require those fields and fail loudly without them.
- The full-suite result is recorded under the owner's accepted current-manifest limitation rather
  than mislabeled green.

**Validation:**
- I2 mechanical comparison passed for all four entries. `0001` matched its original body hash
  `77f63d0c…`; `0002`–`0004` matched originals normalized by exactly the five ratified destination
  substitutions, with no other difference.
- I1, I5, and the unchanged owner-payload assertions passed in the focused three-test gate. The
  safe documentation-contract subset passed 10/10 with 3 manifest-bound tests deselected.
- The edited conformance test passes Ruff. All internal links and every named outbound citation
  resolve; no live external path expects a `P-00N-*.md` filename.
- Licensed runnable suite: 2,371 passed and 9 policy skips after omitting nine manifest-dependent
  files; pytest separately deselected 94 `execution`-marker tests by project default. The exact
  full-suite gate remains unavailable under the accepted Phase 1 environment limitation.

### Phase 5 Completion

**Completed:** 2026-08-21 09:32 PDT
**Phase status:** Implementation complete; independent audit is next

**Changes Made:**
- Added red-first closing tests for the two load-bearing convention decisions and all four
  script-managed product checks.
- Filed D3 as `.project/adr/0002-resolve-generated-index-ids-by-sibling-filename.md` and D4 as
  `.project/adr/0003-cite-decisions-by-register-path.md`, both `[AGENT] (ratified by owner,
  2026-08-21)`. D1, D2, and D5 remain design mechanism detail; D6 remains an Item 3 deferral.
- Ran `product.sh check` for `0001`…`0004` at verified Phase 4 ref `02733b4`. Only the mutable
  `checked` frontmatter lines changed in the four promise entries.
- Regenerated both indexes and synchronized the plan, spec, design, epic, and current-work status.

**Issue and Approved Deviation:**
- The plan expected `mypy src/` to be clean, but the repository's established baseline is 30 errors
  in 8 files. Phase 5 changes no production source, and the current result exactly matches the
  recorded baseline. The agent recommended the maintained zero-new gate; the owner selected that
  option on 2026-08-21. No unrelated source refactor was added to this scaffolding item.

**Validation:**
- The two closing tests failed before the entries and stamps existed, then passed. The safe
  documentation contract passed 14/14 with its three manifest-dependent tests deselected; the
  edited test and all production source pass Ruff.
- I1–I6 pass. The four product bodies are byte-unchanged from `02733b4`; their diffs contain only
  `checked: 2026-08-21 @ 02733b4`.
- Repeated regeneration produced stable hashes: product index
  `7590b8267e9e312e2cf00610a78f59df0cb8e1dfb8175b78b7107c82f514c1d4`; ADR index
  `c2003ee5ac2ee2d69874f4abad7a60e5d1ea297ee036d5f3e124103d75975299`.
- Licensed runnable suite: 2,371 passed, 9 policy skips, and 94 default `execution`-marker
  deselections after omitting the nine manifest-dependent files recorded in Phase 4. The exact
  full-suite gate remains unavailable under the owner's accepted Phase 1 limitation.
- `mypy src/` reports the unchanged 30-error/eight-file baseline; `git diff -- src` is empty.

---

**Status**: Draft → In Progress → Complete
