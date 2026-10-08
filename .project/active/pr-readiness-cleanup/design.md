# Design: PR-readiness cleanup

**Status:** Ready for implementation under the owner's orchestration authorization
**Owner:** Reid W
**Created:** 2026-10-08
**Branch / starting commit:** `pr-readiness-cleanup` / `6872977541eae935d4be2789f48f723ffea7101b`
**Decision authority:** Mechanism choices below are `[AGENT]`; owner requirements retain the grades recorded in the spec. The owner authorized best judgment and a simple implementation, including implementation and independent audit.

## Overview

Repair the ten bounded cleanup groups without changing the elaborator architecture. Freeze independently generated package expectations first, apply narrow changes, and prove the final candidate against licensed models and immutable runtime/customer artifacts.

## Related Artifacts

- Contract: [spec.md](spec.md); owner resolutions: [spec-review.md](spec-review.md); corrected numerical-channel count: [spec-review-20261008.md](spec-review-20261008.md).
- Discovery map: [cleanup research](../../research/20261005-205701_pr-readiness-cleanup-remainder.md). Its earlier unit/assurance recommendations are superseded by the resolutions.
- Inherited architecture: [.project/adr/0005](../../adr/0005-exact-identity-elaboration-replaces-string-resolution.md), [.project/adr/0007](../../adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md), and merge identity: [.project/adr/0008](../../adr/0008-cross-repo-merges-use-merge-commits.md). This design contradicts none of them and needs no new durable architecture decision.

## The Point

`[NEED]` Get the shipped elaborator into a good working state for a PR without remnant code, misleading documentation, or overstated evidence. Real functional tests must catch regressions caused by the fixes. Current customer compatibility must be learned before the PR; reproduced model or consumer issues may be repaired in coordination with its ongoing cleanup rather than treated automatically as codegen regressions. Owner wording and authority are preserved in the spec's Known Requirements.

## Research Findings

- Public generation already builds one exact context and refuses context failures before rendering (`src/sysml_codegen/cli/__init__.py:1132`); shared preflights precede output clearing (`:1239`, `:1280`). Reuse this order.
- Contract encoders are two ordinary JSON calls (`src/sysml_codegen/contracts/serialize.py:28`, `:34`); the input writer is another (`src/sysml_codegen/generation/entry_point.py:130`). Snapshot canonical serialization already rejects non-finite values (`src/sysml_codegen/snapshot/envelope.py:173`).
- Both live extraction and elaboration call the same guessed-unit helper (`src/sysml_codegen/extraction/extractor.py:456`, `src/sysml_codegen/elaboration/elaborate.py:2119`). Removing that shared behavior closes both callers without replacing it with another inference rule.
- Existing public generation tests prove deterministic output but lack an independent complete expected result (`tests/conformance/test_public_route_baselines.py:130`). The narrow zero-entry golden drives private helpers (`tests/conformance/test_zero_entry_package_golden.py:91`); retain its useful assertions while the new oracle exercises the public route.
- Existing preservation checks exercise private stencil behavior (`tests/unit/test_stencils.py:596`). Add public real-package regeneration evidence rather than weakening those checks. Current license availability depends on a particular fixture loading (`tests/conftest.py:24`); final acceptance needs independent license establishment.
- C8's finite documentation inventory and C5's six-file typing inventory are in the research's corresponding tables. Current product promises 0002, 0005, and 0006 preserve source propagation, full assessment, and package integrity; those are the semantic boundaries for this cleanup.

## Core Concept

This is a cleanup of the existing exact generation route plus an independent record of what it emitted before the fixes. A small JSON manifest records every generated path and its byte digest, or the public refusal, for each committed snapshot. Candidate output compares against that fixed record with explicit reviewed changes for the owner-directed unit removal and historical driver deletion. Live checks prove snapshot freshness; archived candidate/customer runs prove execution and preservation. No new production layer is needed. [AGENT, implementation finding 2026-10-08] The unchanged licensed baseline also exposes preexisting quote-display and plural-port ordering drift in two snapshots. Exact recapture differences require separate old/new hashes and graph/binding comparison; the original oracle stays immutable.

## Key Bets

- **B1.** Committed snapshots capture the finite package shapes needed for emission regression protection. If false, the oracle alone misses behavior; its coverage inventory must expose the gap and the live/preservation/runtime checks must supply that evidence.
- **B2.** Unit removal changes labels and related fingerprints, not arithmetic or wiring. If false, SC3/SC13 are not satisfied; stop and diagnose rather than broadening expected differences.
- **B3.** Immutable customer model trees distinguish candidate behavior from concurrent cleanup. If false, compatibility conclusions lack an attributable source revision; recapture identities and rerun the affected comparison.

## Key Decisions

- **D1 — Digests over generated trees.** Use stdlib JSON and SHA-256 for complete path-to-digest manifests and refusal records for all 22 snapshots. Include baseline commit, dependency identities, snapshot digests, generation configuration, and successful/refused inventory. Rejected: committing generated Python trees, which invites pytest collection, lint rewriting, and trailing-whitespace cleanup; digests satisfy SC7 without those hazards.
- **D2 — Preserve the original oracle.** Capture at the exact starting commit before implementation. Keep that baseline immutable and record reviewed intended differences separately with old/new file digests and reasons; candidate checks resolve only those exact changes. Rejected: overwriting all expectations from the candidate or allowing entire fixtures to differ, which would hide regressions.
- **D3 — Pin version fields.** Compare full file bytes including the current `generator_version`; this cleanup does not bump the version. Any later deliberate bump needs a reviewed version-only expectation update, including its physical-contract consequences. Rejected: silently stripping version fields or normalizing all contract JSON, which weakens byte protection.
- **D4 — Retain snapshot diagnostic classification.** Keep the existing `SI_INTERNAL_DEFECT` non-finite snapshot classification and pin its public identity/timing. Rejected: redesigning snapshot diagnostics in C2, since the existing refusal is already before output mutation. Contract and generated-input JSON get `allow_nan=False`; finite serialization settings remain unchanged.
- **D5 — Delete guessed units at the shared boundary.** Remove the type, source-comment, and description guessers and their dead helpers/call paths. Retain parser-native written-value units and the v6 schema. Rejected: fixing offsets, bracket parsing, or a replacement unit resolver, which conflicts with the final owner ruling.
- **D6 — Existing types and validators.** Annotate with the existing graph/template/module types and narrow optional values at the existing preflight boundary when validation is needed. Rejected: unchecked casts, broad ignores, or a new rendering interface. Preserve handwritten code and trusted verifier bytes.
- **D7 — Committed companion evidence.** C1 is a narrow warning repair in an isolated Agentic branch, committed before acceptance and recorded by revision/content identity. Preserve detection of unmarked executable examples. Rejected: accepting an uncommitted neighboring template edit or changing the general guidance rules.
- **D8 — Candidate-bound evidence.** Final runtime/customer runs use archives or wheels built from the named candidate commit with resolved dependency roots recorded. Rejected: running against the inherited research archive, editable original checkouts, or a customer failure-count threshold without reproduced causes.

## Architecture

The production path remains live parse or v6 envelope → exact context → one projection → preflight → existing renderers → semantic and physical sealing. The oracle sits in tests beside that path and invokes the same public generation entry point. Documentation and tracking describe the resulting behavior and evidence; they do not create another semantic authority.

## Required Invariants

- Baseline capture precedes any production/template/fixture change and covers exactly the 22 committed snapshots, including refusals and complete file sets. Snapshot/dependency identity is recorded, not inferred from current files later.
- Finite contract bytes and fingerprints match the baseline, including extreme, subnormal, exponent, and signed-zero values. Non-finite public refusals leave a nonexistent output nonexistent and an existing sentinel/output tree byte-identical.
- C4 changes only the six spec-named generated files; C3 allowances require observed removed-label effects and corresponding seals/fingerprints. Any other output delta is a finding.
- The historical fixture retains seven numerical exits plus constraint evaluation/report, preserves all remaining baseline values, and proves source propagation to dependent and unrelated outputs.
- No verifier byte/hash change, typing relaxation, license skip masquerading as acceptance, or unrelated owner draft enters this work.

## Component Overview

- Contract/input writers: existing JSON calls gain strict finite encoding; public-boundary tests cover unchanged finite bytes and refusal before output mutation.
- Extraction/elaboration: shared guessed-unit behavior is deleted; consumed-declaration fixtures prove live/snapshot behavior and retained parser unit facts.
- Fixtures: licensed C3/C4 recaptures, regenerated D5 sources, mechanical batch/breadth pins, and provenance updates stay with their existing fixtures.
- Regression evidence: one small public-generation test/helper and JSON manifests under the existing expectations convention. Expected data contains no executable generated source and requires no formatting exclusion.
- C6/C8–C10: bounded deletion and record correction in the existing tests, documents, matrix, and tracking homes; preserve evidence/provenance guards when retargeting them.

## Non-Goals

The spec's recorded scope exclusions apply. This design adds no physics refactor, new elaboration machinery, snapshot migration, generalized golden framework, or July assurance census.

## Implementation Notes

- Work only in the isolated `pr-readiness-cleanup` clone. Preserve the original checkout's staged/unstaged state against `/tmp/pr-readiness-original-state.json`; the isolated branch includes the necessary spec/research but no mental-alignment drafts.
- Before C4 changes, licensed recapture must reproduce its committed snapshot byte for byte. Regenerate `catf_mfe_d5` with the existing D5 script before freshness/recapture checks; compare normalized sealed evidence without inventing a schema migration.
- Establish license availability independently of one model's validity. Required model-load failures fail unconditionally. Keep the expected skip set explicit and give each missing parity golden its own disposition.
- Source `/tmp/pr-readiness-run-env.sh` for the original licensed key, explicit isolated source roots, and `PYTHONDONTWRITEBYTECODE`. Use its `PR_READINESS_PYTHON=/home/reid/1cfe/sysml-codegen/.venv/bin/python`; the companion branch is `/tmp/pr-readiness-agentic-mbse` (`pr-readiness-guidance`). Do not sync dependencies or write virtualenvs. Record the original companion `.env` path without printing its contents. C1 source changes follow the all-22 baseline capture.
- Preserve the diagnostic-accounting test name cited by three ledger replacement rows. Derive matrix counts with a rerunnable mechanical recount; remove dangling backlog references and preserve owner grades and historical audit verdicts.

## Potential Risks

- A digest says which file changed, not why. Retain generated baseline output in scratch evidence for textual comparison and review every allowed delta before recording its digest; durable acceptance remains the committed manifest.
- C3 label removal can alter more than description text through contract identities. Check semantic arithmetic/wiring separately and list exact downstream file changes rather than approving a broad fingerprint exemption.
- Customer cleanup may advance while validation runs. Archive its current committed model tree first; coordinate repairs in isolated customer work, never overwrite its active checkout, and record revisions before/after any repair.
- Type annotations may expose additional real optional-value errors. Diagnose them with existing preflights and preservation tests; a late writer exception alone does not prove fail-before-mutate.

## Integration Strategy

First establish the pre-change oracle and licensed/customer starting identities. Apply the companion warning and bounded C2–C6 fixes, then add the candidate oracle comparisons and reviewed recaptures. Update C8–C10 against the resulting evidence. Produce immutable candidate artifacts only after implementation stabilizes; any later runtime-affecting fix requires a new candidate identity and rerun of affected acceptance.

## Validation Approach

- SC1–SC6: focused guidance, finite/public-refusal, live/snapshot unit, licensed historical recapture, channel/mutation/report, mypy, and real-package handwritten-preservation checks.
- SC7: all-22 license-free public comparisons plus a failing mutation for each calculation/multi-output, aggregation/alias, constraint/report template shape and one rendering-code mutation. Record actual coverage limits for stubs, smart regeneration, preservation, and non-float outputs.
- SC8–SC10: document/register/distinctness checks, ledger paths/surface/replacements, requirement dispositions, source-identity authority mapping, mechanical matrix recount, and original-checkout/draft-state comparison.
- SC11–SC13: licensed default suite with explicit skips and zero license skips, live freshness for every snapshot, candidate-bound real TEAx, Ruff/mypy/build/whitespace, and complete three-case current customer generation/runtime/mutation/preservation evidence. Classify every unexpected customer result by reproduced cause.

## Next-Stage Handoff

The plan must put baseline capture before all code changes and assign finite file ownership to concurrent workers, including shared tests. Use four or five persistent phases rather than one pipeline per cleanup group. Routine choices above need no additional owner gate under the existing authorization. `[AGENT]` Skip standalone design review: architecture is unchanged, storage is stdlib digests, and guards use the existing boundary; independent implementation audit covers the material behavior/provenance risks. Use that final audit against the spec and a focused requirement/evidence review. Record fresh evidence separately from inherited reports and keep unresolved material contradictions blocking.

**Next step:** Create the short phased plan, implement the authorized cleanup, then run the independent audit.
