---
id: 0013
title: Units come from parser-native values rather than prose guessing
date: 2026-10-12
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[OWNER]"
seams: [extraction, elaboration, generation]
supersedes: null
promoted_to: null
---

## Decision

Codegen does not infer unit labels from declaration comments, documentation text, or type-name tables. Parser-native units on written values and existing constraint operand validation remain. The human `// [units]` convention supplies documentation, not executable unit authority.

## Why

The guessers treated prose such as “T atoms” as a unit and supplied labels that no companion validation checked. Those labels could also trigger shared-input conflicts. The owner chose removal of all three guessers rather than repair of the comment reader; changes to generated descriptions and affected snapshots were an accepted consequence.

## Authority

[OWNER, 2026-10-08] Resolution L2-2 in `540826abd4cb55759fd80a731a65376e25ee8afa:.project/active/pr-readiness-cleanup/spec-review.md`. The final owner answer was [OWNER-VERBATIM] “throw it away”; that resolution also records removal of the doc-text reader and type-to-unit table, while preserving parser-native units on written values. This is the later compatibility ruling that superseded the offset-only proposal in the October 5 research.

## Evidence

`docs/architecture/reference/01-extraction.md`, Units; `docs/architecture/modeling-assumptions.md`, Units; `tests/conformance/test_unit_lane_port_metadata.py`. The removed implementation was `extraction/feature_metadata.py`. No automatic unit-conversion capability was added by this decision.
