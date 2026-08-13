# Stage brief: spec — CONSTRAINT-SEMANTICS Item 3 (Coverage Report and TEAx Policy)

You are writing the spec for one backlog item of an approved epic. The behavioral rulings are
settled, owner-ratified authority — capture THIS item's requirements precisely; do not
re-litigate. Work in `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`).

**Deliverable:** `.project/active/constraint-coverage-policy/spec.md`

## The work item (epic Item 3)

Provenance: behavioral requirements **[INHERITED: constraint-semantics-contract/spec.md]**;
slicing **[AGENT] (ratified by owner, 2026-08-12)**. Read the epic's Item 3 section in full:
`.project/backlog/epic_constraint_semantics_contract.md` — objective, current state (including
the M-1 hand-off note and the TEAx re-vendor hand-off), scope 1–6, out-of-scope, success
criteria. Repos in play: codegen (this worktree) and TEAx (`/home/reid/1cfe/teax`, clean `main`
at pinned `fa0e06a` — all TEAx work goes on a branch; TEAx main is never committed to). The
companion (agentic-mbse) is expected untouched; say so as a scope statement.

## Required reading (in this order)

1. Epic Item 3 section (above).
2. Umbrella behavioral contract `.project/active/constraint-semantics-contract/spec.md` —
   "Report and coverage contract" (Q5: coverage in the headline, denominator = applicable
   asserted gates; two-tier accounting; compact embedded coverage joined by catalog
   fingerprint), "Study policy" (Q6 defaults; L1-1 two-vocabularies obligation, fail-closed
   normalization), and L2-2 (vacuous asserted counts as missing assessment until dispositioned
   inapplicable — Item 2 built the mechanism; YOU consume its coverage consequence).
3. Item 1's definitions home: lifecycle contract
   `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — the
   "Headline states and coverage truth" subsection (applicable-asserted-gate test on the form,
   the six states, the precedence, both-vocabularies obligation) and invariants 32, 33, 41,
   46/46a, 48, 49; companion requirements LC-E05/E06/E10/E11/E12 in
   `.project/concepts/constraint-execution-lifecycle-requirements.md`.
4. Item 2's landed authority you consume (read its design's Item 3-citable section):
   `.project/active/constraint-catalog-totality/design.md` — disposition vocabulary
   (`eligible`/`excluded`/`non_reaching`, closed reasons, precedence), the usage-tier record
   fields (`declaration_id`, `source_form`, `disposition.kind/severity`, `inapplicability`,
   `occurrence_count`; Item 3 adds no usage-tier field), catalog `3.0.0` keyed by
   `declaration_id`, and the `ships_constraint_machinery` rule your zero-input aggregator
   deliberately supersedes (the supersession note is at the seam in codegen source). Also its
   `verification.md` "Cross-repo" section: the TEAx re-vendor hand-off
   (`ACCEPTED_CATALOG_SCHEMA_VERSIONS` += `3.0.0`, TEAx fails closed until then, never bump
   TEAx first).
5. Research §§2, 4–5: `.project/research/20260812-101200_constraint-semantics-end-to-end.md` —
   the report-can-lie mechanics (`assessed_count`-only headline), excluded-only no-report gap,
   TEAx `unconstrained` mislabel.
6. Product-lens obligations `.project/active/constraint-semantics-contract/product-lens.md` —
   spec-F1 (ADR filed by Item 1: ADR-009 — cite, don't re-file), spec-F2, spec-F3, spec-F5
   (coverage derivation direction: design must fix report-derived-from-catalog so the pair
   cannot diverge).
7. The four `all_satisfied` assertions in codegen `tests/execution/` (Item 1 audit M-1 hand-off
   — this item owns their correction to the new vocabulary).
8. TEAx surfaces you will touch: `evaluation/projection.py` (`CANONICAL_HEADLINE`),
   `study/policy.py`, durable case-record layer. Locate and cite them; TEAx tests run in
   `/home/reid/1cfe/teax`.

## Success criteria to carry (epic Item 3, inherited)

- Six states independently pinned in report AND canonical TEAx vocabularies: fully-covered
  satisfaction, partial coverage, violation, indeterminate, descriptive-only `not_assessed`,
  truly unconstrained.
- `all_satisfied` impossible when any applicable asserted usage lacks assessment.
- Plain/requirement-side-only model → zero-input `not_assessed` report; zero-usage model →
  report-free, maps to `unconstrained`.
- Report coverage derived from the catalog one direction; cannot diverge without a
  generation/verification failure.
- Partial coverage defaults keep-for-boundary; feed-strategy only via explicit config line;
  both persist coverage counts and catalog linkage in durable case records.
- Unknown report/runtime headline tokens fail closed (no fallthrough, no unnormalized key
  error).
- Cross-repo compatibility tests, codegen + TEAx full suites, ruff/mypy zero-new,
  generated-artifact review, `git diff --check` — exact counts recorded.

## Environment notes

- Codegen gates: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` (NEVER `uv run` — it
  resolves the companion to the wrong checkout). License:
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; licensed proof = zero
  `no live syside license` skip lines.
- TEAx suite runs in `/home/reid/1cfe/teax` (its own venv/pytest — check its README/pyproject;
  the epic's prior wave ran it green at 53+ in the real lane).
- Generated baselines/fixtures are format-exempt.

## Process

- Provenance grades on every requirement; agent-grade stays agent-grade.
- Open questions that belong to design (exact token spelling — the umbrella defers
  `satisfied_partial` vs `partially_satisfied`; report field names/shapes; schema migration
  path; config opt-in spelling; landing order incl. the re-vendor) go to "Open Questions /
  Deferred to design" — deferred, not silently decided.
- Surface premise conflicts; park dependent conclusions; never resolve silently.
- Finish with `ARTIFACT: <path>` as the last line of your final message.
