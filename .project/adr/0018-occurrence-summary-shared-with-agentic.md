---
id: 0018
title: Occurrence summary has a second reviewed owner in agentic-mbse, held by a parity test
date: 2026-10-18
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-10-18)"
seams: [elaboration, agentic-mbse]
supersedes: null
promoted_to: null
---

## Decision

ADR 0012's invariant "Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership" is amended. These reads now have two reviewed owners. Codegen keeps them for elaboration. agentic-mbse's `sysml/occurrence_extraction.py` performs the same reads for the shared executable-subset contract, through its own reviewed accessors. The two are held together by end condition (ii): codegen keeps its occurrence index, and a permanent parity test in codegen CI compares agentic-mbse's occurrence summary with codegen's own occurrence index on a shared seed and fails on any difference. Every other 0012 invariant is unchanged.

## Why

L6 and the shared contract need instantiation facts, and agentic-mbse cannot import codegen (ADR 0007). Spike F1 (agentic-mbse EXEC-SUBSET-CONTRACT Item 1, 2026-10-15) showed a summary port matching codegen `b5663c07` on 72 of 72 cases; Item 1's recorded parity run matched 73 of 73 (34 seed fixtures, 37 v6 corpus fixtures, both dc3 trees). The port shipped in agentic-mbse PR #30, merged as `ccd57d83`; its ownership decision is agentic-mbse ADR 0001. 0012's concern, that a weaker alternate read could drop evidence, is answered by parity on exact evidence (ADR 0004), not by exclusive location. The owner chose end condition (ii) over (i) (codegen swapping onto the shared module): codegen keeps its elaboration code, and the parity test makes drift fail in codegen CI where the change is made. The owner chose to file this amendment when agentic-mbse Item 1 merged rather than at EXEC-SUBSET-CONTRACT Item 2, so this record matches reality from that merge.

## Invariants established

- agentic-mbse's occurrence summary and codegen's occurrence index agree on the parity seed at every codegen commit; the CI parity test is the gate.
- Until EXEC-SUBSET-CONTRACT Item 2 lands that CI test, the guard is agentic-mbse's parity test against stored codegen oracle outputs (`tests/test_sysml/test_occurrence_parity.py`, recaptured with `scripts/subset_profile/occurrence_parity.py`); a codegen change to these reads is caught on recapture, not on every codegen commit.
- A change to codegen's declaration discrimination, slot construction or multiplicity reading that changes occurrence facts is not complete until agentic-mbse's summary matches or the contract is re-pinned.

## Rejected alternatives

- Keeping exclusive codegen ownership (option A′): rejected because it leaves the contract unable to decide instantiation-dependent refusals until a single move.
- End condition (i), codegen swaps onto the shared module and deletes its copy: not chosen by the owner (2026-10-18).
