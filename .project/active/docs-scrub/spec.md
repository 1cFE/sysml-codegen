# Spec: docs/ Full Scrub After UPSTREAM-FINDINGS

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06 06:44
**Complexity:** MEDIUM
**Branch:** `docs-scrub` (off `upstream-findings-epic`)

---

## Problem

The UPSTREAM-FINDINGS epic landed 12 items (~90 commits) on `upstream-findings-epic`.
Each item updated the docs it directly touched, but no one has read the docs tree as a
whole since. Three kinds of debt are known to exist:

- **Deliberate gaps**: Item 7 left the prose bodies of reference docs 07/10/11/17/24
  thin — the REQ text lives in the verification matrix and modeling-assumptions, but the
  docs' prose was never rewritten to match.
- **Untouched docs that may now lie**: `overview.md`, reference docs 00, 03, 04, 05, 06,
  08, 13, 14, 22, 23, 26, and the repo-root `CLAUDE.md` architecture section predate the
  epic's changes (new `snapshot/` package, `--from-snapshot`, renamed types, new terms).
- **Known drift mechanics**: the verification-matrix summary block drifts from its own
  table rows, and `file:line` anchors rotted repeatedly during the epic.

A reader at epic HEAD cannot currently trust that any given reference doc describes the
code as it exists.

## Success Criteria

- [ ] Every file in `docs/architecture/` (overview, modeling-assumptions,
      verification-matrix, reference 00–27) has been read against epic HEAD and either
      verified accurate or corrected.
- [ ] The verification-matrix summary counts are recomputed from the actual table rows,
      not the existing summary block.
- [ ] `modeling-assumptions.md` reads as one coherent contract end-to-end; in
      particular the EXPOSE story across §3, §5, and the V-table tells one story.
- [ ] Reference docs 07/10/11/17/24 prose bodies describe the current behavior (Item 7's
      known gap closed), consistent with the REQ rows that carry the authoritative text.
- [ ] No doc uses pre-epic names for renamed/new concepts: `ConsumerScopedKey` is gone
      (now `ScopedAliasKey`); `reference_chain`, `EXPOSE_CHAIN_TENTATIVE`/Phase 3b,
      `fallback_entry_points` (in-memory only) vs `output_aliases` (serialized) are used
      consistently where those subsystems are described.
- [ ] Docs describing the capture workflow say which scripts are snapshot-driven
      (license-free) vs live-license (`capture_extraction_snapshots.py` only), matching
      the script docstrings.
- [ ] Docs 22/23/26 are each either verified live, corrected, or explicitly marked with
      their status after checking whether they still describe current code.
- [ ] Repo-root `CLAUDE.md` architecture section mentions the `snapshot/` package and
      `--from-snapshot`.
- [ ] Code anchors in touched docs use symbol names, not `file:line` (new convention;
      applied where docs are edited, and stale line anchors are removed wherever found).
- [ ] The gate is unchanged: 1989 passed / 4 skipped / 5 xfailed; ruff src/ 21;
      mypy src/ 109. No code, test, or fixture changes.

## Known Requirements

- **[HARD]** Docs-only change. No source, test, template, or fixture edits. Known dead
  template `pydantic_schema.py.jinja2` stays — if a doc references it, fix the doc and
  file the template deletion as a follow-up.
- **[HARD]** No fixture renames or moves: agentic-mbse's `docs/patterns/plant-idiom.md`
  (branch `upstream-findings-sync`) names `ife_plant`/`spec_chain_*` as reference shapes.
- **[HARD]** Honest-caveat language is preserved. SC-2 is proven at graph level only
  (10 fusion-tea cross-part bindings remain, BACKLOG P1). The scrub must not strengthen
  carefully-worded caveats into claims the code doesn't support.
- **[NEED]** Claims are verified against code at HEAD (or against the per-item
  release-notes/audits), not against other docs — a coherent-but-wrong pair of docs must
  not survive because they agree with each other.
- **[INFERRED]** Where the epic's per-item release notes (Items 7/10/11) enumerate
  behavioral changes, the corresponding docs reflect them.
- **[INFERRED]** "Doc 27" always refers to `reference/27-snapshot-generation.md`; any
  ambiguous link that could mean `27-typed-registry-refactor.md` (a `.project` design
  doc, different tree) is disambiguated.

## Non-Goals

- Rewriting docs for style or restructuring the tree. This is a correctness pass.
- Any code change, including deleting the dead template (file it instead).
- The companion agentic-mbse PR (user's action, unrelated).
- Merging or growing PR #3 — this work PRs separately after the epic merges.

## Open Questions / Deferred to design

- None deferred to a design stage — this goes spec → plan → implement → audit. The
  handoff's open questions were decided at spec time: branch off the epic (keeps PR #3
  reviewable), symbol anchors (line numbers rotted repeatedly during the epic), and
  docs 22/23/26 get a liveness check as part of the scrub itself.

---

## Related Artifacts

- **Handoff:** `/tmp/handoff-20260706-064033.md` (primary input; includes the ten Key
  Discoveries this spec's criteria derive from)
- **Epic:** `.project/backlog/epic_upstream_findings.md` (the 12-item map of what
  changed where)
- **Release notes:** `.project/active/*/release-notes.md` (Items 7, 10, 11)
- **Plan:** `.project/active/docs-scrub/plan.md` (to be created)

---

**Next Steps:** `/_my_plan` for the doc-by-doc checklist, then implement, then `/_my_audit`.
