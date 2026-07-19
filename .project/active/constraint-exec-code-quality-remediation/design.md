# Design Addendum: CONSTRAINT-EXEC Audit Closure

**Status:** Draft — numerical-profile correction specified separately
**Owner:** Reid W
**Created:** 2026-07-17
**Branch:** constraint-exec-epic
**Commit:** 036ec39 + uncommitted remediation

## Overview

Close the independent audit findings without changing the verified formal-binding and occurrence-
ordering cures. This addendum records the new mechanisms needed at the profile/compiler,
inline-lowering, model-lifetime, and package-verification boundaries. It parks the conflicting
generated-value contract until the owner chooses its direction.

## Related Artifacts

- Audit requirements: `audit.md`
- Execution record: `plan.md`
- Lowering contract: `.project/completed/20260713_constraint-lowering/{spec,design}.md`
- Generation contract: `.project/completed/20260713_constraint-generation/{spec,design}.md`
- Original review: `.project/research/20260713-213722_constraint-exec-pr-code-quality.md`

## Core Concept

The executable profile is the admission boundary. Every admitted expression must have one complete
path from typed IR through compilation, lowering, module rendering, and execution. Each later
boundary must preserve the earlier boundary's semantics and reject impossible or hostile records
before consuming them. The four independent cures extend existing mechanisms rather than adding
parallel pipelines: compiler dispatch follows profile categories, inline lowering uses the existing
strict reference resolver, model validators run on assignment, and the stdlib verifier validates a
seal's semantic form before touching recorded paths.

## Key Bets

- **B1.** Profile-v2 facts contain enough category and unit information to compile every admitted
  numeric expression without re-running profile policy. *If false → `ADMIT` cannot be a total
  compiler contract and the companion API must change.*
- **B2.** Inline predicate feature references name values in the owning occurrence scope and can use
  the same strict resolver as definition actuals. *If false → inline constraints need a new binding
  contract, and the committed fixture is not representative.*
- **B3.** Existing callers do not rely on temporarily invalid constraint or catalog records. *If
  false → assignment validation exposes a caller bug that must be repaired, not hidden.*
- **B4.** Package seals are intended to contain canonical package-relative POSIX artifact paths and
  SHA-256 hex digests. *If false → the package contract itself must be amended before verification
  can enforce containment.*

## Key Decisions

- **D1.** Extend the existing predicate compiler's typed numeric path to quantity references and
  profile-derived arithmetic categories. *Rejected: duplicating the companion admission matrix as
  production policy; parity tests own the cross-repo matrix.*
- **D2.** For an inline predicate, collect its feature-reference leaves in predicate order and
  resolve each unique leaf through the existing strict owner-scope resolver, producing ordinary
  `ConcreteConstraintInput` records. For an inherited inline constraint, resolve in each concrete
  inheriting occurrence while retaining the referenced base-definition attribute as the modeled
  value source when no occurrence override exists. The caller must supply the same extracted and
  materialized design-attribute set used by production lowering; an empty mapping is not a valid
  resolution-parity probe. *Rejected: synthesizing float inputs during rendering; that bypasses
  lowering and leaves graph inputs absent.*
- **D3.** Set Pydantic `validate_assignment=True` on `ConcreteConstraint` and
  `ConstraintCatalogEntry`, retaining their existing model validators. Revalidate nested values
  when catalog assembly, serialization, filtering, or fingerprinting consumes them. *Rejected:
  freezing the models; current tests and generation guards deliberately exercise post-construction
  mutation.*
- **D4.** Validate digest syntax, canonical relative paths, and the derived executable fingerprint
  while loading the seal. Normalize recorded-artifact stat/read and package-walk failures into
  fatal path-specific diagnostics. *Rejected: resolving untrusted paths and checking containment
  afterward; invalid paths must never be read.*
- **D5.** Narrow executable admission to numerical validity predicates and preserve the generated
  numerical data model. Valid non-numerical assertions warn in agentic-mbse and sysml-codegen and
  do not halt generation. *[AGENT] recommendation ratified by owner, 2026-07-18; warning/continue
  behavior stated by owner.* The dedicated requirements contract is
  `.project/active/numerical-constraint-profile/spec.md`.

## Required Invariants

- Every profile-v2 `ADMIT` operator/category case compiles; every `BLOCK` case fails before
  compilation or is explicitly rejected by the compiler boundary test.
- Inline predicate leaves and rendered module inputs reconcile exactly and execute from the
  committed offline fixture. Direct, inherited, subtype, retyped, and fixed-multiplicity owner
  occurrences resolve through the same strict ladder with production-equivalent inputs.
- Neither constraint model can serialize, filter, catalog, or fingerprint a state that its
  construction validators reject.
- Verification never reads an absolute, parent-traversing, or non-canonical recorded artifact
  path. All verifier boundary failures return `VerificationResult` diagnostics.
- The executable fingerprint equals SHA-256 of the canonical recorded artifact-hash mapping.

## Non-Goals

- Reworking the verified formal-target binding or part-occurrence ordering cures.
- Hiding license-dependent or paid-corpus gates.
- Fixing the unrelated assertion-dependent expression-compiler test under `python -O`.

## Validation Approach

Each cure starts with a regression that fails against the current worktree. Focused tests run in
normal and optimized Python. The final gate covers the exact companion commit, generated execution,
stdlib-only verifier identity, Ruff/format, targeted mypy with baseline labeling,
`git diff --check`, fixture preservation, placeholder scans, and the broad unlicensed suite when
available.

## Next-Stage Handoff

The four independent decisions above are implementation-ready. D5 proceeds only after the
dedicated numerical-profile spec is approved and designed. The active plan records that
cross-repository dependency explicitly.
