# Align record — CONSTRAINT-SEMANTICS Item 3 (orchestrated run, 2026-08-12)

**Owner instruction at launch:** continue the orchestrated epic run with Item 3 in the same
session after Item 2 closed out ("can you proceed to orchestrating item 3 when this closes
out?"), check-ins waived as before. Align is recorded here; the run proceeds autonomously.

## Reading of the work item

Item 3 (Coverage Report and TEAx Policy) makes generated reports and TEAx study policy state
exactly how much applicable asserted feasibility was assessed. It derives compact report
coverage one-way from Item 2's canonical catalog (authored total, assessed count,
excluded/non-reaching counts + reason histogram, coverage state), adds the partial-coverage
headline in BOTH vocabularies (report tokens and TEAx canonical runtime tokens) with a
fail-closed normalization seam, implements headline precedence (violation > indeterminate >
full satisfaction > partial coverage > not assessed), generates the zero-input aggregator for
constraint-bearing models with no executable assertions (keeping truly constraint-free models
report-free), sets TEAx defaults (partial → keep-for-boundary; feed-strategy only via explicit
auditable per-study opt-in; coverage persisted in durable case records), and versions/migrates
generated schemas, package contracts, and cross-repo pins with a specified landing order.

Intent (umbrella spec): the headline must be unable to claim more coverage than exists —
`all_satisfied` becomes impossible when any applicable asserted usage lacks assessment. The
feasibility denominator is applicable asserted gates only; inventory totality (Item 2's) and
feasibility coverage are different totals and must not be conflated.

## Reserved gates

- **None reserved for this item.** The epic's owner checkpoint (all-65 disposition table +
  tolerances) belongs to Item 5. Item 3's open decisions — headline token spelling, report field
  shapes, schema migration path, config opt-in spelling, landing order — are execution-tier,
  deferred to this item's design by the umbrella spec.

## Provenance and conflicts noted at orient

- Behavioral requirements are `[INHERITED: constraint-semantics-contract/spec.md]` (Q5/Q6
  rulings, L1-1/L2-1/L2-2 review resolutions); slicing is `[AGENT] (ratified by owner,
  2026-08-12)`. Definitions home: the lifecycle contract's "Headline states and coverage truth"
  subsection (Item 1), invariants 32/33/41/46/46a/48/49, LC-E05/E06/E10/E11/E12.
- Hand-offs INTO this item: the four `all_satisfied` assertions in codegen `tests/execution/`
  (Item 1 audit M-1); the TEAx re-vendor of `ACCEPTED_CATALOG_SCHEMA_VERSIONS` += `3.0.0`
  (Item 2 — TEAx fails closed on new packages until it lands; do not bump TEAx first);
  Item 2's `ships_constraint_machinery` rule, which invariant 32's zero-input aggregator
  deliberately supersedes in this item (recorded at the seam).
- Working repos: codegen worktree (`item7-rebuild`), companion worktree (bc69f04, likely
  untouched this item), TEAx at `/home/reid/1cfe/teax` on clean `main` at pinned `fa0e06a` —
  **branch there; never commit to TEAx main** (remote is SSH; no push either way).

## Run shape

Same as Item 2: `spec` → `spec_review` → `design` → `design_review` → `plan` → `implement` →
`audit`, fresh sessions for reviews and audit, cures fed back, one commit per stage/decision,
briefs committed. Close and pre_pr stay with the owner. Known process traps carried forward:
pass `--perm bypassPermissions` on implement/audit resumes; gates run under
`/home/reid/1cfe/item7-rebuild-venv/bin/python`, never `uv run`.
