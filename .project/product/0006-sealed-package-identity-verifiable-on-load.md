---
id: 0006
title: A generated package's identity and integrity are verifiable on load
date: 2026-08-23
owner: Reid W
status: active
amended_by: []
superseded_by: null
supersedes: null
provenance: "[AGENT] (ratified by owner, 2026-07-19)"
surfaces: [contracts, generation, teax]
checked: 2026-08-23 @ f0a7b0a
---

# P-006 — A generated package's identity and integrity are verifiable on load

**Grade:** `[AGENT] (ratified by owner, 2026-07-19)` — an agent-originated promise whose
mechanism was ratified with the lifecycle contract. Challenge it by re-deriving against the
recorded reasoning, not by asking the owner.
**Serves:** [P-001](0001-design-search-free-variation.md) — a study run binds to a stable package
identity, so its results are attributable to exactly one generated artifact.

## The promise

Every generated package is sealed with two contracts: a semantic `ModelContract` (fingerprint
over the computation graph — parameters, outputs, constraint catalog) and a physical
`PackageContract` (content hashes over the on-disk artifacts). A consumer verifies both on load
via a stdlib-only `verify.py` shipped inside the package; a tampered, incomplete, or extended
package fails fatally before use. TEAx loads no generated package it has not verified.

## Authority

- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — ratified
  normative authority (`[OWNER-VERBATIM, 2026-07-19]` "Ratified."): the Contracts/seal
  responsibility row ("Incomplete/unsafe tree cannot seal") and invariant 37 ("Anything that
  seals verifies unchanged … A seal proves integrity, not generation provenance").
- CLAUDE.md, pipeline stage 5 (Sealing) — the standing description on live and from-snapshot
  paths alike.

## Evidence

- `src/sysml_codegen/contracts/`; `tests/unit/test_contract_models.py`,
  `tests/unit/test_verify_package.py`, `tests/conformance/test_exact_route_seal_step9.py`,
  `tests/conformance/test_exact_route_fingerprint_stability.py`.

## Scope

A seal proves coherence and integrity, not authenticity or generation provenance — the digests
are unkeyed (see also the same bound on the v6 snapshot envelope in CLAUDE.md). Integrity
failures are always fatal; environment mismatches are advisory unless strict mode is set.
