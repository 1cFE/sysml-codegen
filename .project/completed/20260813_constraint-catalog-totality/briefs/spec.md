# Stage brief: spec — CONSTRAINT-SEMANTICS Item 2 (Canonical Usage Domain and Catalog Totality)

You are writing the spec for one backlog item of an approved epic. The behavioral rulings are
already settled and owner-ratified — your job is to capture THIS item's requirements precisely,
not to re-litigate the contract. Work in
`/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`).

**Deliverable:** `.project/active/constraint-catalog-totality/spec.md`

## The work item (epic Item 2, verbatim scope)

Provenance: behavioral requirements are **[INHERITED: constraint-semantics-contract/spec.md]**;
the item slicing is **[AGENT] (ratified by owner, 2026-08-12)**. Epic source:
`.project/backlog/epic_constraint_semantics_contract.md` (read the Item 2 section in full —
objective, current state, scope 1–7, out-of-scope, success criteria).

Objective: make the graph and embedded catalog account for every authored constraint usage
before occurrence expansion can erase it. Today constraint records begin after owner-to-scope
expansion, so 56 of CATF's 65 authored usages disappear before either the instance graph or
the catalog can see them.

Scope highlights (full list in the epic):
1. Complete authored-usage domain in the same instance-graph/catalog authority used by live
   and snapshot generation; exact declaration identity and form classification preserved.
2. Exactly one disposition per usage: executable, excluded-with-reason, or
   non-reaching-with-reason. Per-occurrence executable entries stay separate from usage-level
   inventory.
3. Severity by cause: asserted structurally-unattachable = generation-halting error; asserted
   vacuous = warning + authoring advisory; plain and out-of-scope forms = visible records.
4. Explicit vacuous-inapplicability mechanism, without a second hand-maintained inventory.
   (The mechanism choice — model annotation vs reviewed catalog-level acceptance — is deferred
   to this item's DESIGN per umbrella spec L2-2; the spec states the requirements it must meet.)
5. Non-circular generation-time completeness gate over the canonical authored domain and
   catalog dispositions; mutations that remove/duplicate/misjoin a disposition must fail.
6. Carry the authority through the instance-graph codec, snapshot path, and sealing
   fingerprints. If the schema changes, this item owns ONE reviewed final-schema fixture
   recapture (37 fixtures).
7. Re-grade and re-anchor REQ-EXT-09 and REQ-CL-04 against independent totality evidence.

Out of scope (owned elsewhere — state these as non-goals): report headline / coverage schema /
TEAx projection and policy (Item 3); executing calc-def-owned gates (Item 6 designs it); any
parallel manifest or catalog inventory kept in sync with the graph; the four `all_satisfied`
assertions in `tests/execution/` (handed to Item 3 by Item 1's audit — do not touch).

## Required reading (in this order)

1. Epic Item 2 section: `.project/backlog/epic_constraint_semantics_contract.md`
2. Umbrella behavioral contract: `.project/active/constraint-semantics-contract/spec.md` —
   especially "Pipeline invariants" (totality hard-gate Q3, non-circularity L3-2, one-authority
   D-3/spec-F4, severity by cause, vacuous = missing assessment L2-2) and the
   inventory-vs-feasibility denominator distinction (Item 3 consumes the denominator; you
   provide the inventory).
3. Item 1's landed definitions (what you build against — summarized in
   `.project/CURRENT_WORK.md` top entry): lifecycle contract invariant 28 + LC-E05 (third
   disposition kind: non-reaching-with-reason), invariant 48 + LC-G07 (embedded catalog as sole
   authority), new invariant 61 + LC-E13 (vacuous gate at warning grade), ADR-009 in
   `docs/architecture/modeling-assumptions.md` §9. The contract lives at
   `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`; the frozen
   companion at `.project/concepts/constraint-execution-lifecycle-requirements.md`.
4. Research §§2–4: `.project/research/20260812-101200_constraint-semantics-end-to-end.md` —
   the measured 65→9→0 failure, where usages vanish (`elaborate.py:522-539` scope expansion),
   and the census of forms (9 part-usage-owned, 5 part-def-owned vacuous, 51 calc-def-owned).
5. Product-lens obligations: `.project/active/constraint-semantics-contract/product-lens.md`
   — spec-F4 (one authority), spec-F7 (REQ-EXT-09 re-grade), spec-F8 (Item 7 evidence register).
6. Item 7 constraints: `.project/backlog/epic_elaborate_first_architecture.md` (single-authority
   and recapture obligations) and `.project/active/cutover-recovery/plan.md` (paused step-4
   evidence — your changes must not silently invalidate more than the epic's register records).

## Success criteria to carry into the spec (from the epic, inherited)

- Frozen `catf_mfe_d5` produces exactly 65 usage carriers, zero absence, no change to its
  authored constraint syntax (the twins are byte-pinned — `test_d5_variants.py:29`).
- Removing or duplicating any carrier fails generation with a named, usage-identifying
  completeness diagnostic.
- Asserted structurally-unattachable fixture halts; asserted vacuous fixture warns visibly;
  plain constraint with a blocked predicate still generates and catalogs as unassessed.
- Inapplicability mechanism explicit, fingerprinted, cannot silently change an asserted
  usage's coverage role.
- Live, in-place snapshot, and relocated snapshot routes produce the same authored domain and
  dispositions; old/malformed snapshot shapes fail closed under the selected version rule.
- REQ-EXT-09 and REQ-CL-04 cite non-self-referential tests that fail if a pre-expansion usage
  vanishes.
- Focused tests, full licensed codegen/companion suites, ruff zero-new, mypy zero-new, fixture
  diff review, `git diff --check` — exact counts recorded.

## Environment notes

- Companion repo worktree: `/home/reid/1cfe/agentic-mbse-item7-rebuild` (editable install reads
  it). SysIDE license: no `.env` in the codegen repo — `set -a; source
  /home/reid/1cfe/agentic-mbse/.env; set +a` before licensed runs; a green run with zero
  license-skip verification is not a licensed run.
- Test command: `uv run --extra dev pytest tests/`. Generated baselines and fixtures are
  format-exempt (never ruff-format them).
- A full snapshot re-capture rewrites every `captured_at` timestamp — the byte-identity check
  method is a timestamp-only diff check, then revert untouched fixtures.

## Process

- Keep provenance grades on every requirement you write ([INHERITED: …], [AGENT], etc.), per
  capture-fidelity. Do not upgrade agent-grade rulings to owner-grade.
- Open questions that belong to design (mechanism choice, gate's mechanical home
  extraction-time vs generation-preflight, snapshot schema/version rule, composition with the
  existing ledger checks) go in an "Open Questions / Deferred to design" section — deferred,
  not silently decided.
- If you hit a genuine premise conflict with recorded authority, surface it in the spec and
  park dependent conclusions; do not resolve it silently.
- Finish with `ARTIFACT: <path>` as the last line of your final message.
