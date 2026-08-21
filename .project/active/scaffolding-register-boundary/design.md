# Design: Scaffolding Reinstall and Register Boundary

**Status:** Certified — audit 2026-08-21 at `3566fdd` (`audit.md`)
**Owner:** Reid W
**Created:** 2026-08-21
**Branch:** repo-cleanup
**Spec:** `.project/active/scaffolding-register-boundary/spec.md`

---

## Overview

Install the two decision registers and their engines from the `agentic-project-init` pack, state
the rule that routes a decision to one register or the other, and migrate the product ledger onto
the naming the engine actually reads.

## Related Artifacts

- **Spec:** `.project/active/scaffolding-register-boundary/spec.md`
- **Epic:** `.project/backlog/epic_repo_cleanup.md` — Item 1
- **Product-lens:** `.project/active/scaffolding-register-boundary/product-lens.md` (spec run, DISPOSED)
- **Research:** `.project/research/20260820-201945_line-count-anatomy-and-salvageability.md`
- **Required Reading:** the pack's `adr/README.md`, `product/README.md`, `scripts/adr.sh`,
  `scripts/product.sh`; `.project/product/INDEX.md` and `0001`…`0004`;
  `docs/architecture/modeling-assumptions.md`; `claude-pack/rules/capture-fidelity.md`
- **Decision records:** `.project/adr/0001` carries the routing criterion; `.project/adr/0002` and
  `0003` carry D3 and D4. The generated index is `.project/adr/INDEX.md`.

## The Point

The product is three steps: parse the models with a SysML v2 parser, walk the AST to reconstruct
the math, write it into TEAx Python — and any manual fallback for an unresolved reference is a
smell, because ill-formed models are refused with a diagnostic rather than accommodated.
`[OWNER-VERBATIM, 2026-08-16]`, `.project/product/0004` and `0003`.

This item does not touch that product. It serves it one hop back: those two promises are written
down precisely so a future agent cannot quietly undo them, and the ledger's own contract is *"if a
promise is not reachable from here, it has no home"*. A register nobody can route into, whose index
is maintained by hand against a spec saying a script owns it, is a promise-keeping mechanism that
has already started to drift. The work is to make the mechanism true.

The obligation that governs every decision below: **the four promises must come out the other side
reachable, unaltered, and correctly graded.** Two are the owner's verbatim words.

## Research Findings

**The pack's two engines are structurally identical.** `adr.sh` and `product.sh` both allocate
four-digit ids under a lock (`product.sh:cmd_new`), read every field from YAML frontmatter that
must begin at line 1 (`product.sh:29-35`), and regenerate `INDEX.md` from a
`[0-9][0-9][0-9][0-9]-*.md` glob (`product.sh:77`, `adr.sh:76,111`). `set_field` fails loudly when a
field is absent rather than no-opping.

**Our ledger is invisible to its engine, twice over.** The four entries are named
`P-00N-slug.md` and none has frontmatter — each opens with `# P-00N — …`. So the glob misses them
*and* `field()` would return nothing even after a rename.

**The generated index is terser than ours.** `regen_index` (`product.sh:74-109`) emits
`- <id> · <title>` plus optional `surfaces`, `status`, `checked`. No link, no filename, no
provenance grade. Our hand-written `INDEX.md` carries all three plus an id rule, an ADR-convention
paragraph, a back-registered ADR-009 row, and a "Cited from" trail.

**The pack's frontmatter vocabulary already fits our entries.** `provenance` accepts `[OWNER]`,
`[AGENT] (ratified by owner, date)`, `[INHERITED: src]`. Our `[OWNER-VERBATIM]` entries map to
`[OWNER]` with the quote staying in the Authority section — which is exactly the pack's documented
"First capture" shape, so no information is lost in the mapping.

**Install is a merge, not a clobber.** `init-project.sh --force` (`:136-167`) skips four protected
files (`CURRENT_WORK.md`, `backlog/BACKLOG.md`, `completed/CHANGELOG.md`, `memories/index.json`) and
updates the rest. Diffed against this repo: four files are missing outright (`scripts/adr.sh`,
`scripts/product.sh`, `adr/README.md`, `product/README.md`), four are older pack copies with no
local edits (`EPIC_GUIDE.md` 327→425, `epic_template.md` 130→160, `README.md`, `backlog/README.md`),
and the rest match. `.claude/` here is a real directory, so `--include-claude` must not be passed.

**ADR-007 and ADR-009 are the misfiled entries.** Sections 1–6 and 8 of
`modeling-assumptions.md` bind a model author (library/design separation, aggregation via
redefinition, template instantiation, executable constraint forms). Section 7 tells downstream
code never to re-derive identifiers (`:430-446`), which binds a system builder. Section 9,
Coverage Truth and Headline Semantics (`:704-742`), governs report token spellings, generation
templates, TEAx's `CANONICAL_HEADLINE`, and a normalization seam. No model author can uphold either
implementation rule. ADR-007's correction is `[OWNER, 2026-08-21]` after the conflict surfaced
during implementation.

**The guard on the owner's words is one test.** `tests/conformance/test_stop_parser_documentation_contract.py:208-245`
reads `0003` and `0004` by path, asserts the owner quote and the three product-identity step lines,
and asserts both filenames appear in `INDEX.md`.

## Core Concept

Both registers already exist in substance. What is missing is a routing rule and a working engine.

The design is three moves. **First, install the engines** — a merge that adds four files and
refreshes four stale ones. **Second, state the routing rule** as one question a reader can answer
without a subject list: *who is bound by this decision — the person writing the system's inputs, or
the person changing the system itself?* Input-facing decisions stay in the product's own
documentation; system-facing decisions go to `.project/adr/`. That question is the first entry in
the new register, and it is written to be citable by the claude-commands work rather than
re-derived there. **Third, migrate the ledger** to the naming its engine reads.

The insight that makes the third move safe: **the ledger's reachability contract does not need the
index to carry links.** Adopting the pack means adopting its information architecture — the index is
a discovery surface keyed by id, and authority lives in the entry you open. So reachability becomes
a *naming rule* (`<id>` in the index resolves to exactly one `<id>-*.md`), which is mechanically
checkable in a way hand-written prose links never were. The invariant does not weaken in the
handover; it gets a stronger enforcement. Provenance follows the same logic — it moves from index
prose into the `provenance` frontmatter field, where the product-lens reads it on the second hop,
which is the flow the pack was built around.

That reframes the migration as purely mechanical: rename by a fixed map, prepend a frontmatter block
derived from what each entry already states, verify byte-identity below the block, and re-express
the one test's index assertions as real reachability checks.

## Key Bets

- **B1.** The pack's index-then-entry information architecture is sufficient for how agents actually
  resolve product truth here — an id in the index plus a naming rule is a real path, and provenance
  read from frontmatter is as usable as provenance read from an index line.
  *If false → the product-lens and cold agents lose the first hop, promises stop being discoverable,
  and the ledger's "no home" condition bites the four entries we were protecting.*
- **B2.** Nothing outside the four files and the one conformance test depends on the `P-00N`
  filename form in a way a mechanical repoint cannot fix.
  *If false → a rename silently breaks a citation path we did not sweep, and an entry's Authority or
  a doc's pointer dangles.*
- **B3.** Prepending frontmatter is a metadata addition, not a body mutation, so it does not trip
  the registers' append-only rule and does not require superseding `0003` or `0004`.
  *If false → the migration is a material change to owner-verbatim payload and must instead be done
  as four supersessions, roughly tripling the item and leaving two dead entries in the index.*
- **B4.** One routing question, stated abstractly, is enough for a cold agent to file correctly
  without a per-subject list.
  *If false → entries land in the wrong register from day one and the boundary problem returns in a
  new form, having cost a migration.*

## Key Decisions

- **D1.** Install via `init-project.sh --source <pack> --force`, dry-run first, without
  `--include-claude`. *Rejected: copying the four missing files by hand (leaves `EPIC_GUIDE.md` and
  `epic_template.md` stale, which is the drift this epic exists to stop, and hand-copying is exactly
  how the ledger got hand-rolled in the first place).*
- **D2.** Map `P-00N` → `000N` preserving each slug, so `P-003-no-workarounds-for-bad-models.md`
  becomes `0003-no-workarounds-for-bad-models.md`. *Rejected: re-slugging or re-ordering (makes the
  citation repoint a judgment call per site instead of one mechanical substitution).*
- **D3.** Reachability is enforced by a naming rule plus a test, not by adding links to the
  generated index. *Rejected: forking `regen_index` to emit links and grades (a local delta on a
  pack script — the maintenance shape the owner ruled against when choosing to harmonize the ledger
  rather than patch the tool).*
- **D4.** Cite decision records by register path, never by bare number:
  `docs/architecture/modeling-assumptions.md ADR-009` versus `.project/adr/0001-…`. *Rejected:
  minting a distinguishing prefix such as `DR-0001` (the script does not know it, so prose and
  filesystem would disagree; and renumbering the published `ADR-0NN` ids would break existing
  citations for a cosmetic gain).*
- **D5.** The displaced `INDEX.md` prose lands in `.project/product/README.md` as a repo-local
  section — the id rule, the naming/resolution rule, and the two-register convention. The generated
  product index contains promise rows only; decision discovery belongs to the decision registers,
  and inbound citations remain at their source sites. *Rejected: dropping the resolution rule (it
  is what makes B1 true and must be written down somewhere a reader finds).*
- **D6.** ADR-007's and ADR-009's re-homes are **deferred to Item 3** `[OWNER, 2026-08-21]`. By the
  criterion this item files, ADR-007 (Compute Once, Look Up Thereafter) binds downstream code, and
  ADR-009 (Coverage Truth and Headline Semantics) binds report generation and runtime
  normalization. Sections 1–6 and 8 are author-facing and stay. This item records the triage
  outcomes; Item 3 performs the moves because it is already authoring builder-facing ADRs with that
  context loaded. *Rejected: moving them here (bolts unrelated re-homes and citation repoints onto
  a scaffolding item). Rejected: grandfathering them (the register would carry known exceptions on
  the day its rule is written).* **Consequence for Item 3:** re-derive and repoint every citation to
  both sections; ADR-009's move must include `0001`'s Authority citation.

## Architecture

Three surfaces change, and they are independent of each other except at one seam.

```
pack (source of truth for scaffolding)
  └── init-project.sh --force ──> .project/{adr,product,scripts,EPIC_GUIDE.md,…}

.project/adr/            (new)      0001-<criterion>.md  +  INDEX.md   [adr.sh]
.project/product/        (migrated) 000N-<slug>.md       +  INDEX.md   [product.sh]
docs/architecture/modeling-assumptions.md  (unchanged except D6)

seam: 0001's Authority cites modeling-assumptions.md ADR-009.
      Item 3 moves that decision and repoints the Authority in one change.
```

Data flow for the migration, per entry: read the entry's existing prose → derive the script-managed
frontmatter → `git mv` to the new name → prepend the block → repoint only the five internal
Markdown destinations → assert no other body bytes changed → `product.sh index`.

`date` and `owner` are backfilled from each file's git history rather than stamped today, so the
frontmatter tells the truth about when the promise was filed. `checked` is stamped via
`product.sh check <id> <ref>` after the migration verifies, not written by hand.

## Required Invariants

- **I1.** For every id listed in `.project/product/INDEX.md`, exactly one `.project/product/<id>-*.md`
  exists. This is the reachability contract in its enforceable form.
- **I2.** Below its frontmatter block, every visible word and owner payload is identical to its
  pre-migration content. The only permitted byte changes are the five relative Markdown
  destinations repointed from `P-00N-*.md` to `000N-*.md`; every other byte is identical.
  `[AGENT] (ratified by owner, 2026-08-21)` after implementation surfaced the conflict between
  literal byte identity and I4's outbound-link requirement.
- **I3.** Every entry's `provenance` field agrees with the grade its own prose states.
- **I4.** Every path cited *by* a promise entry resolves, and every reference *to* a promise entry
  resolves — both directions.
- **I5.** `product.sh index` is idempotent: running it twice produces identical bytes, and the
  committed `INDEX.md` equals a fresh regeneration.
- **I6.** No document claims a single ADR home.

## Component Overview

- **`.project/scripts/adr.sh`, `product.sh`** — the two engines, installed verbatim from the pack.
  Own id allocation, status flips, `checked` stamps, and index generation. Not modified.
- **`.project/adr/0001-<criterion-slug>.md`** — the routing rule, `[OWNER]` provenance, settled.
  The register's first entry and the artifact the claude-commands work cites.
- **`.project/adr/INDEX.md`** — generated by `adr.sh index`.
- **`.project/product/000N-*.md`** — the four migrated promises. Prose untouched below frontmatter.
- **`.project/product/README.md`** — pack contract plus a repo-local section carrying the id rule,
  the `<id>-*.md` resolution rule, and the two-register convention (D5).
- **`.project/product/INDEX.md`** — now generated. Hand edits are lost by design.
- **`docs/architecture/modeling-assumptions.md`** — keeps the author-facing ADRs. Its ADR-010 slot
  stays open. ADR-007 and ADR-009 are triaged here and moved by Item 3.
- **`CLAUDE.md`** — its ADR-convention paragraph rewritten to describe two registers and D4's
  citation form.
- **`tests/conformance/test_stop_parser_documentation_contract.py`** — quote assertions unchanged;
  the two `"P-00N-….md" in index` assertions re-expressed as I1 checks against the new ids.
- **`.project/active/scaffolding-register-boundary/adr-triage.md`** — the nine outcomes, including
  ADR-007 and ADR-009 recorded as builder-facing with their moves carried to Item 3.

## Non-Goals

- Authoring harvested domain decisions or new product promises. Items 3 and 4 own that; this item
  files only its own D3 and D4 writebacks.
- Re-homing ADR-007 or ADR-009. Triaged here, moved by Item 3 `[OWNER, 2026-08-21]`.
- Deleting anything from `.project/`. Item 5.
- Changing `agentic-project-init`, or applying the criterion to the claude commands.
- Re-verifying the four promises hold in code. A `checked` stamp asserts "I looked."
- The `contracts/serialize.py` `allow_nan` defect and the V11 doc claims — now
  `[SERIALIZE-NAN-SEAL]` and `[V11-DEAD-GATE-DOCS]` in `BACKLOG.md` `[OWNER, 2026-08-20]`.

## Implementation Notes

- **Frontmatter must start at line 1.** `field()` requires `NR==1 && $0=="---"` (`product.sh:30`).
  A leading blank line makes every field read empty and the index silently loses the entry.
- **`git mv` before prepending**, so history follows the file and the byte-identity check in I2 can
  diff against the pre-move blob.
- **Dry-run the installer first.** `init-project.sh --force` overwrites any non-protected file that
  differs; the dry run is the review step that confirms the four expected updates and nothing else.
- **`product.sh check` needs the entries to already validate** — stamp after I1/I2/I3 pass, not
  during the migration.
- **Provenance mapping is not mechanical.** `0001` is mixed-grade (owner-verbatim core, inherited
  and agent parts); its frontmatter grade describes the *summary*, per the pack's rule that an
  entry's summary carries only its own grade and never inherits from what it cites.
- **The repoint sweep must be re-derived, not remembered.** `grep -rl 'P-00[0-9]'` at
  implementation time; a sweep on 2026-08-20 found 13 live sites outside `.project/completed/`,
  and that set will have moved.

## Potential Risks

| Risk | Mitigation |
|---|---|
| Frontmatter prepend counts as a body mutation on owner-verbatim entries (B3 false) | I2 makes the claim checkable; if the owner rules it material, fall back to supersession and re-scope |
| A missed citation site leaves a dangling path (B2 false) | I4 checks both directions; sweep is mechanical and run at implementation time, not from this document |
| `init-project.sh --force` overwrites something unexpected | Dry run reviewed before the real run; the four protected files cover the volatile ones |
| Generated index is less orienting than the prose it replaces (B1 false) | D5 puts the resolution rule in README; if it still reads worse, the fallback is a hand-maintained sibling, not a script fork |
| ADR-007's or ADR-009's deferred move is forgotten, leaving the register permanently misfiled | Recorded in the triage document, in Item 3's epic scope, and in this design's handoff — three places, none of which Item 5 deletes |

## Integration Strategy

`/_my_design` and `/_my_concept_design` already sweep `.project/adr/INDEX.md`; creating the register
switches those touch points on with no further wiring. `/_my_close` files promises through
`product.sh` once installed. Nothing gates on either register, so a half-finished migration degrades
to "no entries found", which both commands treat as normal.

Downstream in this epic: Item 2's harvest classifies candidates using the criterion filed here, and
Item 5's purge is bound by I4 to leave every ledger citation resolving.

## Validation Approach

1. **Installer**: dry-run output shows exactly four adds and four updates, no protected file touched.
2. **I1** — for each id in `INDEX.md`, `glob(<id>-*.md)` has length 1. Add to the conformance test.
3. **I2** — for each entry, `git show <pre-move-blob> | diff - <(sed '1,/^---$/d;1,/^---$/d' new)` is empty.
4. **I3** — read each entry's `provenance` and confirm against its prose by inspection; recorded in
   the triage document.
5. **I4** — `grep -rl 'P-00[0-9]'` returns no live site expecting the old form; every path cited by
   an entry resolves.
6. **I5** — run `product.sh index` twice, diff; and diff against the committed file.
7. **I6** — grep `CLAUDE.md`, `product/README.md`, `product/INDEX.md` for single-home language.
8. Conformance test passes with quote assertions unchanged.
9. Full suite green with `SYSIDE_LICENSE_KEY` loaded.

## Next-Stage Handoff

**Fixed:** the install mechanism (D1), the id map (D2), reachability-by-naming-rule (D3), the
citation form (D4), and I1–I6.

**Open:** nothing blocking. D6 is settled as a deferral, so this item records triage outcomes for
ADR-007 and ADR-009 and does not move them. The plan can start.

**Carried to Item 3:** the ADR-007 and ADR-009 re-homes. Re-derive both citation sets during that
item; bind ADR-009's `0001` Authority repoint to the same change.

**De-risk first:** B3. Before any rename, prepend frontmatter to a throwaway copy of `P-003` and run
the I2 byte-check and `product.sh index` against it. If the append-only reading turns out to forbid
the prepend, that is a re-scope, and it costs ten minutes to find out rather than four files in.

---

**Next Step:** After approval → `/_my_plan`.
