# Spec: Scaffolding Reinstall and Register Boundary

**Status:** Implementation In Progress
**Owner:** Reid W
**Created:** 2026-08-20 21:47
**Complexity:** MEDIUM
**Branch:** repo-cleanup
**Implementation Progress:** Phase 4 of 5 complete; decision boundary filed and nine entries triaged

---

## Problem

This repo has two places to record a settled decision and no rule saying which one to use.

`docs/architecture/modeling-assumptions.md` holds nine ADRs as numbered sections. The
`agentic-project-init` pack expects a `.project/adr/` directory managed by `adr.sh`, and wires
`/_my_design` and `/_my_concept_design` to sweep its index. `CLAUDE.md` and
`.project/product/INDEX.md` currently assert there is only one ADR home, which the owner has now
superseded.

**`[OWNER, 2026-08-20]` The registers split by subject:** decisions that bind the **model author**
stay in `modeling-assumptions.md`; decisions that bind the **toolchain builder** go to
`.project/adr/`. The owner added that the same boundary problem exists across the claude commands,
so the criterion must be written to generalize rather than list this repo's subjects.

Two supporting problems fall out of the same neglect:

**The product ledger is not managed by the tool that owns it.** The pack's `product.sh` landed
2026-08-12. This repo's ledger was created 2026-08-14 in the ELABORATE-FIRST merge (`385e163`) by
an agent that never installed the script and hand-rolled a `P-NNN` naming scheme. `product.sh`
globs `[0-9][0-9][0-9][0-9]-*.md` (`product.sh:77`), so it matches none of our four entries, and
running `product.sh index` today would overwrite `INDEX.md` with an empty generated file. None of
the four entries has YAML frontmatter at all — each opens with an `# P-00N — …` heading — so
`product.sh` could not read their fields even after a rename.

**Handing `INDEX.md` to a generator moves an invariant, and that move must be deliberate.** The
ledger's contract is "if a promise is not reachable from here, it has no home"
(`.project/product/INDEX.md` preamble). Today that reachability is guaranteed by hand-written index
prose carrying a link and a provenance grade per promise. `regen_index` emits
`- <id> · <title> · surfaces · checked` — no link, no filename, no grade. So the invariant passes
from prose a human maintains to a generator whose output format cannot currently express it. This
item owns that transfer and must leave reachability and grade demonstrable afterwards, not assume
the generator carries them.

## Success Criteria

- [x] A cold agent reading the repo can tell which register a new decision belongs in, from one
      stated criterion, without asking
- [x] `.project/adr/` exists and holds that criterion as its first entry, graded `[OWNER]`
- [x] Each of the nine existing ADRs has a recorded triage outcome against the criterion
- [x] `product.sh` and `adr.sh` manage their registers for real: `product.sh index` regenerates
      `INDEX.md` from the actual entries, and `adr.sh new` allocates the next id
- [x] The regenerated `INDEX.md` still resolves to each entry file and still exposes each entry's
      provenance grade — the ledger's "reachable from here" contract survives the handover to the
      generator
- [x] The four product promises survive with every visible word and owner payload unchanged below
      the added frontmatter block. The only permitted body-byte changes are the five mechanical
      Markdown destination repoints required by the filename migration; citations resolve **in both
      directions**: every reference pointing at a promise entry, and every path a promise entry cites
- [x] `CLAUDE.md` and `.project/product/INDEX.md` no longer claim a single ADR home
- [x] The owner-verbatim quote assertions in
      `tests/conformance/test_stop_parser_documentation_contract.py` still run unweakened, and its
      index-reachability assertions are re-expressed against the harmonized index rather than
      deleted
- [x] Licensed runnable suite green with `SYSIDE_LICENSE_KEY` loaded under the owner's accepted
      missing-manifest limitation; the exact full-suite gate remains unavailable rather than green

## Known Requirements

- **[OWNER]** The two registers split by subject — model-author decisions in
  `modeling-assumptions.md`, toolchain-builder decisions in `.project/adr/`. Settled;
  owner-originated 2026-08-20.
- **[OWNER]** The criterion is stated so it generalizes to the claude commands, not as a list of
  this repo's subjects. Owner-stated 2026-08-20.
- **[OWNER]** The product ledger harmonizes to the pack's naming standard rather than the pack's
  script being modified to fit this repo. Owner-stated 2026-08-20.
- **[HARD]** `.project/product/0001`…`0004` bodies are append-only. Every visible word and owner
  payload is immutable; the exact five destination-only citation repoints recorded below are the
  sole migration exception. Entries `0003` and `0004` carry `[OWNER-VERBATIM]` quotes. A material
  change is a supersession, never a rewrite.
  Source: `agentic-project-init/project-pack/product/README.md`, "Lifecycle".
- **[HARD]** Harmonization is **rename plus prepend plus five mechanical Markdown destination
  repoints**, and nothing else. No entry has frontmatter today, and `product.sh` reads every index
  field from it (`product.sh:29-35, 77-88`), so the four entries each gain the script-managed block
  above their existing first line. The five existing relative links among the four entries change
  only their hidden destination from `P-00N-*.md` to `000N-*.md`; their labels, every visible word,
  and all owner-verbatim payload remain unchanged. Every other byte below the block stays identical
  to its pre-item state, verified mechanically. `[AGENT] (ratified by owner, 2026-08-21)` after the
  implementation surfaced that literal byte identity and outbound-link resolution could not both
  hold after the rename.
- **[HARD]** The post-harmonization index must resolve to entry files and expose each entry's
  provenance grade. `regen_index` emits `- <id> · <title> · surfaces · checked` — no link, no
  filename, no grade — so this needs either a `provenance` field surfaced in the generated line or
  a documented `<id>-*.md` resolution rule stated in `.project/product/README.md`.
  Source: `.project/product/INDEX.md` preamble; product-lens SOURCES protocol.
- **[HARD]** `tests/conformance/test_stop_parser_documentation_contract.py:208-245` reads two
  promise files by exact filename and asserts those filenames appear in `INDEX.md`. Renaming the
  entries breaks this test, so the test moves with them in the same change.
- **[HARD]** `product.sh` allocates ids and flips statuses; `INDEX.md` is generated and hand edits
  to it are lost by design. Whatever the index must say has to be derivable from entry
  frontmatter, or live somewhere that is not the index.
  Source: `agentic-project-init/project-pack/product/README.md`, "Lifecycle".
- **[HARD]** The quote-text assertions in
  `tests/conformance/test_stop_parser_documentation_contract.py:208-245` survive unweakened — only
  paths change. Its two `assert "P-00N-….md" in index` assertions cannot pass under any rename,
  because a generated index contains no filenames; they are **re-expressed** against what the
  harmonized index does guarantee (id and title), never dropped. This test is the only mechanical
  guard on the owner-verbatim payload and the epic's deletion lock does not cover it, since no
  ledger entry names it as Evidence.
- **[INFERRED]** The prose currently in `INDEX.md` that the generated format cannot carry
  relocates to `.project/product/README.md` or to the criterion ADR rather than being dropped: the
  id rule, the ADR-convention paragraph, the per-promise provenance grades, and index→entry
  reachability itself. Grades live in entry frontmatter; reachability is the documented naming rule
  plus its conformance test.
- **[OWNER]** `ADR-007` and `ADR-009` are triaged here and re-homed by Item 3, not by this item
  `[OWNER, 2026-08-21]`. The owner classified ADR-007 from its binding rule: “Downstream code never
  re-derives identifiers” belongs in `.project/adr/`. When
  Item 3 moves ADR-009, `0001`'s Authority citation is repointed in the same change — `0001` is
  `[OWNER-VERBATIM, 2026-08-13]` and its Authority must not dangle.
- **[INFERRED]** Sections 1–6 and 8 of `modeling-assumptions.md` are author-facing and stay there.
  This item records all nine triage outcomes and moves none of them.
- **[INHERITED]** The two registers' id forms must not be confusable in prose. `adr.sh` allocates
  four-digit ids; `modeling-assumptions.md` uses `ADR-0NN`.
  Source: `.project/backlog/epic_repo_cleanup.md`, Register Boundary section.
- **[INHERITED]** Taking the pack's newer `EPIC_GUIDE.md` (327L → 425L) and `epic_template.md`
  (130L → 160L) is safe — the repo's copies are older pack versions with no local edits, verified
  by diff. Source: this item's investigation, 2026-08-20.

## Non-Goals

- Authoring any decision or promise content beyond the criterion entry. That is Items 3 and 4.
- Deleting anything from `.project/`. That is Item 5.
- Changing `agentic-project-init` itself, or applying the criterion to the claude commands.
- Re-verifying that the four existing promises still hold in code. A `checked` stamp asserts
  "I looked", not a certification.
- Re-homing `ADR-007` or `ADR-009`. Triaged here, moved by Item 3 `[OWNER, 2026-08-21]`.
- The `allow_nan=False` defect in `contracts/serialize.py` and the false V11 preflight claims in
  `CLAUDE.md`, `docs/architecture/overview.md`, and
  `docs/architecture/modeling-assumptions.md`. Both were briefly attached to this item because the
  epic's product-lens wanted them off Item 8's tail; they have nothing to do with scaffolding.
  Filed as standalone `[SERIALIZE-NAN-SEAL]` and `[V11-DEAD-GATE-DOCS]` at the top of
  `.project/backlog/BACKLOG.md` `[OWNER, 2026-08-20]`.

## Open Questions / Deferred to design

- How the four entries are renamed without stranding citations. Most of the 331 `P-00N`
  references sit in `.project/completed/`, which Item 5 deletes anyway. The live set must be
  re-derived mechanically at design time rather than from a remembered list — a sweep on
  2026-08-20 found **thirteen** files outside `completed/`, including `CLAUDE.md`,
  `.project/backlog/BACKLOG.md`, `.project/CURRENT_WORK.md`, `.project/active/elaborator-downstream/`
  (spec and product-lens), `.project/active/dead-worktree-pins/product-lens.md`, three research
  documents, two reports, and the conformance test. Whether to repoint all, repoint only the live
  ones, or leave a redirect is a design call.
- Where the displaced `INDEX.md` prose lands — `product/README.md`, the criterion ADR, or split.
- The exact citation convention that keeps `ADR-009` and pack entry `0009` distinguishable. The
  design settles this as D4 — cite by register path, never by bare number.
- Whether the pack's newer Slicing Principles change the REPO-CLEANUP decomposition. Principle 3,
  "composition is a deliverable," has no owning item in the current epic. Raised here because this
  item installs the guide that says so; resolving it belongs to the epic, not to this item.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_repo_cleanup.md` — Item 1
- **Required Reading:**
  - `agentic-project-init/project-pack/adr/README.md`
  - `agentic-project-init/project-pack/product/README.md`
  - `agentic-project-init/project-pack/scripts/adr.sh`, `scripts/product.sh`
  - `.project/product/INDEX.md` and `0001`…`0004`
  - `docs/architecture/modeling-assumptions.md`
  - `claude-pack/rules/capture-fidelity.md`
- **Research:** `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md`
- **Product-lens:** `.project/active/scaffolding-register-boundary/product-lens.md`
- **Design:** `.project/active/scaffolding-register-boundary/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
