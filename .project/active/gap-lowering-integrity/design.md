# Design: Lowering Outcome Integrity — Warning Order and Excluded Identity

**Status:** Approved and Implemented — awaiting independent audit

**Owner:** Reid W

**Created:** 2026-07-18 14:43 PDT

**Revised:** 2026-07-18 14:59 PDT

**Branch:** `constraint-exec-epic`

**Commit:** `6db321225a5c8568db0287b67ed1d04c03079cc2`

**Companion commit:** `4ed2a0728ea49298666415cd389d9a6173a81a3e`

## Overview

Constraint lowering will report every non-numerical statement before a sibling blocking decision
halts the run, without constructing a catalog or reaching package mutation. Only anonymous
excluded records receive a portable file/line/column identity and a wider digest. Every named mint
input and output byte remains unchanged.

## Related Artifacts

- Approved contract: [spec.md](spec.md)
- Approved spec review: [spec-review.md](spec-review.md)
- Design review: [design-review.md](design-review.md)
- Epic Item 2: [../../backlog/epic_gap_close.md](../../backlog/epic_gap_close.md)
- F4/F5 research: [../../research/20260718-123558_constraint-expression-final-gap-review.md](../../research/20260718-123558_constraint-expression-final-gap-review.md)
- F4/F5 verification: [../../research/20260718_gap-review-verification.md](../../research/20260718_gap-review-verification.md)
- Upstream I2/D5 design: [../numerical-constraint-profile/design.md](../numerical-constraint-profile/design.md)
- Tracked limitation: `[ANON-ELIGIBLE-KEY]` in [../../backlog/BACKLOG.md](../../backlog/BACKLOG.md)

## Research Findings

- The BLOCK preflight raises before the warning loop
  (`src/sysml_codegen/analysis/constraint_lowering.py:752-769`, `:775-786`). The facts/profile zip
  already supplies source order, and each diagnostic list retains profile walk order.
- BLOCK precedes concrete-record construction. Catalog assembly runs only after lowering returns in
  live and snapshot flows (`src/sysml_codegen/orchestration/pipeline_builder.py:882-896`,
  `:994-1012`; `src/sysml_codegen/snapshot/graph_rebuild.py:211-230`). CLI output mutation begins
  later (`src/sysml_codegen/cli/__init__.py:949-993`).
- `_source_local_identity` derives a raw file/line/column component for every anonymous usage
  (`constraint_lowering.py:456-469`). Eligible minting retains it (`:817-821`, `:917-921`). Excluded
  minting discards it (`:788-813`). Canonicalizing every anonymous location would therefore change
  eligible-anonymous IDs and violate this item's scope.
- Exclusion is one existing decision: unsupported owner, or any non-ADMIT profile outcome
  (`constraint_lowering.py:479-491`, `:788-815`). That selection must be shared by lowering and
  snapshot-copy canonicalization; the serializer must not reproduce it independently.
- SysIDE location extraction provides `LocationFact(file, line, column)` with the document URL
  stripped to a string (`../agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py:225-246`;
  `../agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py:373-391`). Values can contain redundant
  leading separators such as `///home/...`. Snapshot facts currently preserve the string verbatim
  (`src/sysml_codegen/snapshot/serializer.py:93-103`).
- The snapshot loader's established source-path rule is lexical `os.path.abspath`, deliberately not
  filesystem `resolve`, so symlink spelling is preserved
  (`src/sysml_codegen/snapshot/loader.py:314-323`). Portable anonymous routing should use the same
  lexical normalization for both parser locations and supplied model roots.
- The duplicate guard remains unconditional and post-sort (`constraint_lowering.py:306-321`,
  `:941-943`). Its current message asserts an unproved cause and identifies only owner instances.
- `mint_constraint_id` truncates SHA-256 to 16 hex characters, or 64 bits
  (`constraint_lowering.py:292-303`). Adding location removes the deterministic F5 collision but
  leaves a birthday-collision assumption. Anonymous excluded IDs can be widened without changing
  any named or eligible byte.
- The migration mapping rejects an anonymous committed-corpus entry because its join is named-QN
  only (`tests/conformance/test_constraint_migration_mapping.py:48-70`). The corpus has none.
- **Surfaced premise conflict:** numerical-profile D5 requires actionable warning messages, while
  this approved spec makes warning-content changes a non-goal and GAP-CLOSE Item 5 owns that fix
  (`spec.md:124`; `.project/backlog/epic_gap_close.md:297-313`). Item 2 preserves current warning
  bytes and fixes ordering only. Full D5 message-content closure remains parked on Item 5.

## Core Concept

Lowering keeps one profile evaluation and one record-building loop. A read-only reporting pass
first emits all non-numerical warnings; the existing BLOCK check then raises before record or
catalog construction. For identity, one shared selector returns the indices that lowering already
treats as excluded. Live lowering maps a source path only when its index is both selected and
anonymous. Snapshot capture uses the same selector to canonicalize a serialized copy of those same
locations, leaving named and eligible-anonymous facts untouched. Replay validates stored canonical
referents through an explicit snapshot route. The excluded anonymous mint alone adds the canonical
file/line/column component and uses a 128-bit suffix; all other mint calls retain their current
tuples, prefixes, and 64-bit suffixes.

## Key Bets

- **B1.** Ordered `model_paths` is stable configuration for equivalent live runs. *If false → the
  root-slot portion of an anonymous excluded identity changes even when source bytes do not.*
- **B2.** Every live anonymous excluded usage has a non-null location inside at least one supplied
  model boundary. The verified SysIDE reproduction has that shape. *If false → portable identity
  cannot be established and lowering must halt rather than guess.*
- **B3.** The v1 facts schema treats `LocationFact.file` as an opaque source referent, so a
  canonical root-relative value is valid snapshot data. *If false → portable replay requires an
  upstream schema change and this localized design cannot ship.*

## Key Decisions

- **D1. Report before halt with a read-only pre-pass.** Zip facts and decisions, emit each
  `NON_NUMERICAL` warning once, then run the existing BLOCK aggregation and raise. Remove warning
  emission from the record loop. *Rejected: moving BLOCK after record construction (partial state);
  a new preflight model (parallel mechanism).* The current reason-bearing warning bytes stay fixed;
  Item 5 owns actionable message text.
- **D2. One authoritative exclusion selector.** A pure helper accepts facts plus the already
  computed profile and returns the ordered usage indices satisfying the existing branch:
  unsupported owner or decision not ADMIT. Lowering uses that set for its excluded branch. Snapshot
  serialization calls the same helper with `evaluate_profile(facts)` only when the recorded
  lowering mode is `applied`, and rewrites only selected indices whose `identity.name is None`.
  *Rejected: selecting by missing name (touches eligible
  anonymous); reimplementing owner/profile classification in the serializer (drift).* `_exclusion_for`
  remains the sole exclusion-kind projector.
- **D3. Preserve a byte firewall around every non-target mint.** Named excluded records execute the
  current call unchanged: current prefix, tuple `(usage_qn, owner_kind, source_form)`, and 16-hex
  suffix. Eligible records, including eligible anonymous records, keep the current path and raw
  location component unchanged. Only `index in excluded_indices AND name is None` enters the new
  mint path. *Rejected: refactoring all calls through one reconstructed tuple (named-byte risk);
  changing all excluded IDs (fixture churn).* Anonymous-only remains `[INFERRED]`, not owner-settled.
- **D4. Use explicit live-raw and snapshot-canonical routes.** Live pipeline and snapshot capture
  call `map_live_source_referent(raw_file, model_paths)`. Snapshot graph rebuild calls
  `validate_snapshot_source_referent(stored_file)`. There is no automatic “already canonical”
  detection. Anonymous excluded processing requires an explicit route; named and eligible paths do
  not invoke either function. *Rejected: pattern-based idempotence (a live raw path could bypass
  root containment); implicit default route.*
- **D5. Canonical referent is `root-<slot>/<encoded-relative-posix-path>`.** Normalize the SysIDE
  file string and each supplied model path with `os.path.abspath(os.path.normpath(...))`, never
  `Path.resolve`, matching snapshot lexical source semantics. A directory input matches contained
  files. A file input matches only itself and uses its parent as boundary. Exact file input wins;
  otherwise the most-specific directory wins, then earliest slot for an exact duplicate. Each
  UTF-8 path segment is percent-encoded with only RFC 3986 unreserved bytes literal. Validation
  requires canonical percent-encoding, at least one segment, no empty/`.`/`..` decoded segment, no
  encoded separator, and no absolute payload. *Rejected: absolute/hash-of-absolute paths; basename;
  common-path inference; raw unescaped segments.*
- **D6. Snapshot-copy canonicalization is excluded-only.** Serialize facts to a copy, obtain the
  shared excluded indices, and replace `location.file` only for anonymous selected indices using
  the live mapper. Named and eligible-anonymous serialized locations remain byte-identical. Replay
  passes explicit snapshot mode into lowering and validates only anonymous excluded locations.
  *Rejected: a new top-level identity table/version (more state and churn); rewriting all anonymous
  facts (critical scope violation).* The loader format gate stays unchanged.
- **D7. Widen only anonymous excluded suffixes to 128 bits.** Add an explicit digest-length option
  to the existing mint primitive with its current 16-hex default. The new anonymous excluded call
  alone requests 32 hex characters. At one million anonymous exclusions, the birthday-bound
  collision probability is below `1.5 × 10^-27`; the guard still detects any actual duplicate.
  *Rejected: retaining 64 bits for the new legal-model surface (about `2.7 × 10^-8` at one million);
  globally widening IDs (breaks named and eligible bytes); embedding the full tuple (unbounded and
  awkward identifiers).*
- **D8. Duplicate diagnostics describe evidence, not cause.** Keep the hard post-sort guard. On a
  duplicate, report the ID and, for both records, available usage QN, source-local identity,
  exclusion location, owner definition, and owner instance with explicit fallbacks. Do not claim a
  hash collision or broken model. *Rejected: removing the guard; silently suffixing after a
  collision; causal blame unsupported by the records.*
- **D9. One unchanged, isolated RED/GREEN overlay.** Store and hash a test-only overlay outside all
  detached worktrees. It shape-locks each F5 kind and uses signature inspection: on the baseline it
  calls the old `lower_constraints` signature; on the candidate it detects and passes explicit
  live mode plus the temp source root. *Rejected: separate pre/post tests (not the same test-first
  claim); candidate-only helper imports (baseline collection failure).*
- **D10. No committed anonymous fixture.** Kept licensed tests create temporary model trees, so
  `tests/fixtures` and the migration anonymous-corpus guard remain byte-identical. *Rejected: adding
  a fixture and widening the retired manifest record for this lowering-only item; weakening the
  guard.*

## Architecture

```text
ConstraintFacts ──> evaluate_profile ──> excluded_usage_indices (one selector)
       │                    │                         │
       │                    ├─ report NON_NUMERICAL ─┤
       │                    └─ BLOCK ────────────────> raise before records/catalog/package
       │                                              │
       ├─ live route + roots ──> map raw source ──────┤ anonymous + excluded only
       └─ replay route ─────────> validate referent ──┤
                                                      ▼
              named excluded: unchanged mint   anonymous excluded: location tuple + 128-bit suffix
                                                      │
                                              duplicate-ID guard → catalog

capture: facts copy + same excluded indices + live mapper → canonical anonymous exclusions only
replay: canonical facts + explicit snapshot validator ──────> shared lowering path
```

The live caller already owns ordered roots (`src/sysml_codegen/orchestration/pipeline_builder.py:701-706`)
and threads them with explicit live mode at the lowering call (`:889-895`). Capture owns the same
roots (`src/sysml_codegen/snapshot/capture.py:20-68`) and supplies them to serialization. Offline
rebuild explicitly selects snapshot mode (`src/sysml_codegen/snapshot/graph_rebuild.py:211-221`).
Catalog and graph interfaces do not change.

## Required Invariants

- **I1. Warning order and count.** A mixed batch logs its exact ordered NON_NUMERICAL list once,
  then raises BLOCK. A non-blocking NON_NUMERICAL batch logs the same exact list once, not twice.
- **I2. Halt atomicity.** BLOCK returns no context and reaches no completed concrete list, catalog,
  graph return, output clearing, or package creation.
- **I3. Excluded-only canonicalization.** A fact is canonicalized only if its shared selector index
  is excluded and its name is missing. Missing name alone is never sufficient.
- **I4. Named byte stability.** Named excluded mint arguments and exact IDs for `non_numerical`,
  `unassessed_form`, and `unsupported_owner` match the coordinated baseline byte-for-byte.
- **I5. Eligible-anonymous stability.** Eligible anonymous raw location, mint tuple, 16-hex suffix,
  exact ID, and compile grouping remain unchanged. `[ANON-ELIGIBLE-KEY]` stays open.
- **I6. Portable excluded identity.** Anonymous excluded identity is canonical referent, line, and
  column plus the existing exclusion tuple. File, line, and column independently distinguish each
  of the three exclusion kinds.
- **I7. Route safety.** Live mode always proves lexical root containment. Replay mode accepts only
  the canonical grammar. No path string chooses its own route, and no absolute root is rendered.
- **I8. Route parity.** Repeated live, relocated live, and snapshot replay produce byte-identical
  anonymous excluded IDs, applicable warnings, canonical locations, excluded records, and catalog
  fingerprints for equivalent ordered trees.
- **I9. Collision defense.** Anonymous excluded IDs use 128-bit suffixes. Any actual duplicate ID,
  including a forced adversarial duplicate, still halts with truthful two-record diagnostics.
- **I10. Missing identity fails loud.** Missing location, no matching live root, malformed snapshot
  referent, or selector/facts cardinality mismatch raises; no basename/CWD/absolute fallback exists.

## Component Overview

- **Shared selection helper in lowering** — returns excluded usage indices from facts and one
  profile result. Both record lowering and snapshot-copy canonicalization use it.
- **Pure source-referent helper** — has separate live mapping and snapshot validation entry points,
  backed by one encoder/validator. No class or protocol is introduced.
- **Constraint lowering** — owns warning pre-pass, explicit route use, byte-firewalled mint branch,
  wider anonymous digest request, and duplicate diagnostic.
- **Live orchestration and snapshot capture/rebuild** — supply explicit route and roots at their
  existing calls. Capture changes only a serialized facts copy.
- **Tests/evidence** — live-shaped license-free facts establish RED/GREEN; temporary licensed model
  trees establish SysIDE shape and route parity without fixture migration.

## Non-Goals

- Widening eligible-anonymous compile grouping or changing eligible IDs (`[ANON-ELIGIBLE-KEY]`).
- Changing profile outcomes, diagnostic force/content, exclusion schema, or catalog schema.
- Returning partial graph/catalog/package state after BLOCK.
- Defining identity across differently ordered model-root invocations.
- Refactoring the wider live/snapshot lowering protocol or `[CONSTRAINT-ARCH-UNIFY]`.
- Adding or recapturing committed fixtures.

## Implementation Notes

- The selector must verify `len(facts.usages) == len(profile.decisions)` before returning indices.
- Determine anonymous from `identity.name is None`; preserve `qualified_name=None` as observed live.
- Keep the named excluded mint expression physically on the current code path. Do not route it
  through reconstructed canonical data, even if tests show the same value.
- The overlay's baseline branch uses live-shaped temp absolute files but no new kwargs. Its candidate
  branch supplies `source_location_mode="live"` and `[temp_root]` after signature inspection.
- Snapshot serialization evaluates the profile only to call the shared selector. It emits no
  warnings and does not call `_exclusion_for`; lowering remains the behavior/reporting owner.
- Do not mutate `ctx.constraint_facts`. Do not add the temp live models to
  `CONSTRAINT_BEARING_FIXTURES`; the existing migration raise stays exact.

## Potential Risks

- **Selector drift.** Mitigation: the record loop and serializer consume the same returned indices;
  tests compare selected indices with resulting excluded records for all three kinds.
- **Live path spelling differs through symlinks.** Mitigation: match the existing lexical-abspath
  convention and explicitly avoid `resolve`; test redundant leading separators and symlink spelling.
- **Optional digest parameter accidentally changes defaults.** Mitigation: exact baseline IDs for
  named exclusions and eligible anonymous facts, plus direct default-mint tests.
- **Pre-pass leaves old warning emission.** Mitigation: exact-count tests for both blocking and
  non-blocking two-warning batches.
- **Historical evidence imports dirty sources.** Mitigation: detached clean worktrees, worktree-first
  paths, import-source assertions, and exact candidate-diff hashing.

## Integration Strategy

Create and hash the unchanged overlay first. Record baseline RED in clean detached codegen and
companion worktrees. Then land the selector, explicit source routes, excluded-only serializer copy,
anonymous-only digest width, warning pre-pass, and diagnostic correction. No agentic-mbse source,
catalog model, graph model, CLI ordering, or fixture change belongs in the candidate patch.

The production patch is limited to:

- `src/sysml_codegen/analysis/constraint_lowering.py`;
- new `src/sysml_codegen/analysis/source_referent.py`;
- `src/sysml_codegen/orchestration/pipeline_builder.py`;
- `src/sysml_codegen/snapshot/capture.py`;
- `src/sysml_codegen/snapshot/serializer.py`; and
- `src/sysml_codegen/snapshot/graph_rebuild.py`.

Tests and `.project/active/gap-lowering-integrity/evidence/` are recorded separately from that
production-only diff.

## Validation Approach

### Isolated test-first RED/GREEN evidence

Create detached codegen baseline and candidate worktrees at
`6db321225a5c8568db0287b67ed1d04c03079cc2`, and a detached agentic-mbse worktree at
`4ed2a0728ea49298666415cd389d9a6173a81a3e`, all under one `mktemp -d` root. Before running tests,
record `git status --porcelain` as empty and the tree hash for both untouched baselines. Keep the
overlay outside those worktrees so it does not contaminate status.

The overlay asserts before behavioral imports:

- both exact HEADs and the companion's clean status/tree hash;
- in baseline mode, the selected codegen worktree's clean status/tree hash;
- in candidate mode, the selected codegen worktree's exact expected production diff hash and
  changed-path set, with no untracked files;
- `sysml_codegen.__file__`, the lowering module source, `agentic_mbse.__file__`, constraint-facts
  source, and executable-profile source are beneath the selected detached roots;
- `PROFILE_SEMANTIC_VERSION == "executable-profile/v3"`; and
- its own SHA-256 equals the recorded value.

Export only the approved production paths to a binary candidate patch. Record its SHA-256, apply it
to the candidate codegen worktree, assert `git diff --check`, assert no untracked files, assert the
changed path set exactly equals the approved list, and hash the candidate's regenerated binary diff
against the baseline. Every test runs in a fresh process with candidate-or-baseline codegen `src`
first, the pinned companion `src` second, `PYTHONNOUSERSITE=1`, and
`PYTHONDONTWRITEBYTECODE=1`. Record commands, environment path order, revisions, imports, tree/diff
hashes, exit codes, profile version, and full defect-specific output in `evidence.md`.

Every F5 overlay node constructs and asserts the verified live shape before lowering:
`identity.name is None`, `identity.qualified_name is None`, and non-null `LocationFact` with exact
file, line, and column. Separate nodes cover `non_numerical`, `unassessed_form`, and
`unsupported_owner`. Each is RED at baseline only because its pair collides. On candidate, the
unchanged overlay detects the new kwargs by signature, supplies explicit live mode/root, and passes.
Collection, setup, route, profile, or license failures invalidate the record.

The F4 node uses two live-shaped NON_NUMERICAL facts and one BLOCK fact. A capture handler appends
each warning event; the exception handler appends `raised`. Candidate expectation is exactly
`[warning-1, warning-2, raised]`, proving source order, exactly-once count, and warning-before-BLOCK.
Baseline is RED only because it records `[raised]`. A separate non-blocking overlay/kept node expects
exactly `[warning-1, warning-2]`, protecting against retained loop emission.

### Kept behavioral and route matrix

- Parameterize each exclusion kind over different lines in one file, different columns on one
  line, and different files at the same line/column. Assert live-shaped inputs, two deterministic
  128-bit IDs, source association, warnings only for `non_numerical`, and exact excluded-record JSON.
- Pin an eligible anonymous fact before/after: raw location string, exact existing 16-hex ID, and
  catalog grouping behavior are unchanged in live and snapshot routes.
- Run repeated live lowering, two equivalent trees under different absolute prefixes, and capture /
  replay. Include two ordered roots with the same relative filename. Compare IDs, warning values,
  canonical locations, serialized excluded records, and fingerprints byte-for-byte.
- Licensed temporary live models assert missing name, missing QN, and non-null file/line/column for
  all three exclusion kinds. One live test per source dimension is sufficient because the full
  kind-by-dimension product is covered by live-shaped synthetic facts; live extraction owns shape,
  while lowering owns combinatorial identity behavior.
- Real `run_codegen(overwrite=True)` tests use a temporary licensed mixed model. An absent output
  stays absent; a populated tree manifest including bytes and symlink targets remains identical.
  Both assert the exact warning event sequence before returned failure.
- Force two different concrete records to the same ID. Assert the halt, ID, both source/owner
  descriptions, and absence of `hash collision`, `broken model`, or equivalent blame.

### Byte and scope gates

- Record exact baseline IDs for named `non_numerical`, `unassessed_form`, and `unsupported_owner`;
  compare after. Also pin one eligible-anonymous exact ID and raw location.
- Record a sorted SHA-256 manifest for `tests/fixtures`; require exact after equality and an empty
  `git diff -- tests/fixtures`. No recapture is allowed.
- Re-run named live/snapshot warning, graph, catalog, and generated-tree byte parity; migration
  mapping including catf_mfe's 65 exclusions; catalog determinism; focused lowering/model/CLI tests.
- Run focused normal and optimized Python, touched-file Ruff/format, targeted mypy, and
  `git diff --check`.

## Next-Stage Handoff

Treat warning-before-halt, explicit route separation, excluded-only canonicalization, named and
eligible byte firewalls, the 128-bit anonymous suffix, and evidence isolation as the reviewed design
contract. D3's anonymous-only boundary remains an `[INFERRED]` agent choice, ratified only if the
owner approves this design; it must not be relabeled owner-originated or settled. A future challenge
must re-derive it against the no-churn rationale and direct named-ID evidence.

The first plan phase must capture the unchanged overlay RED at both pinned clean source trees before
any production edit. Any need to canonicalize eligible anonymous facts, change named mint inputs,
alter the facts schema, or recapture fixtures triggers the surfacing duty and parks implementation.
The actionable-warning-message delta remains on GAP-CLOSE Item 5.

---

Next step after approval: `my-plan`, then `my-implement`; use `my-audit` for independent
certification.
