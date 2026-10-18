# Staged: sysml-codegen ADR 0012 amendment (occurrence summary has a second owner, held by a parity test)

**Target:** sysml-codegen `.project/adr/0012-exclusive-semantic-evidence-ownership.md:27`, the invariant "Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership". ADR bodies are immutable, so the amendment is a new entry plus a status flip by the script.

**Source.** agentic-mbse `.project/completed/20261018_exec-subset-profile/evidence/adr-0012-amendment-draft.md`, left as it is (spec criterion A). Two things change from the draft:

- The draft's "until Item 2 lands" invariant named agentic-mbse's stored-oracle test. That test is retired (2a P1.5, agentic-mbse `8be21e04`). The invariant now names sysml-codegen `tests/conformance/subset_profile/test_occurrence_parity.py` and the pre-merge run that carries it to agentic-mbse changes (design D6, D13).
- The draft said "codegen CI". There is no codegen CI (design O1), so the entry names what actually runs the test.

The draft's ratified filing time was "when Item 1 merges". Item 1 merged (agentic-mbse PR #30) and the entry was not filed (spec § Open Questions, surfaced). It is filed with 2a.

## Commands (run in sysml-codegen at merge)

```bash
.project/scripts/adr.sh new occurrence-summary-shared-with-agentic --title "Occurrence summary has a second reviewed owner in agentic-mbse, held by a parity test"
# fill the new entry's body from the section below, then:
.project/scripts/adr.sh amend 0012 <new-id>
.project/scripts/adr.sh index
```

Frontmatter to set: `provenance: "[AGENT] (ratified by owner, 2026-10-18; parity guard revised by EXEC-SUBSET-CONTRACT Item 2a design D6)"`, `seams: [elaboration, agentic-mbse]`.

## Entry body

### Decision

ADR 0012's invariant "Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership" is amended. These reads now have two reviewed owners. Codegen keeps them for elaboration. agentic-mbse's `occurrence_extraction` performs the same reads for the shared executable-subset contract, through its own reviewed accessors. The two are held together by end condition (ii): codegen keeps its occurrence index, and a permanent parity test in codegen compares agentic-mbse's occurrence summary with codegen's own occurrence index and fails on any difference. Every other 0012 invariant is unchanged.

### Why

L6 and the shared contract need instantiation facts, and agentic-mbse cannot import codegen (ADR 0007). Spike F1 (agentic-mbse `exec-subset-profile`, 2026-10-15) showed a summary port matching codegen `b5663c07` on 72 of 72 cases; Item 1's recorded parity run matched 73 of 73 (34 seed fixtures, 37 v6 corpus fixtures, both dc3 trees). 0012's concern, that a weaker alternate read could drop evidence, is answered by parity on exact evidence (ADR 0004), not by exclusive location. The owner chose end condition (ii) over (i) (codegen swapping onto the shared module): codegen keeps its elaboration code, and the parity test makes drift fail where the change is made.

### Invariants established

- The parity test is `tests/conformance/subset_profile/test_occurrence_parity.py`. It loads each model once and compares agentic-mbse's `extract_occurrence_structure` with codegen's live occurrence index, over the 34 seed models in `tests/fixtures/subset_profile_occurrence_seed/` and the 37 fixtures in `tests/fixtures/v6_recapture_batch/batch.json`. A missing input fails by name. It needs the SysIDE license and skips without one, so a run with no key is not a parity check.
- Two runs carry it. A codegen change meets it in codegen's own licensed suite. An agentic-mbse change meets it in agentic-mbse's required pre-merge run, `scripts/subset_profile/codegen_suite.py`, whose default selection is `tests/conformance/subset_profile` and which, from 2a P7, fails on any skip of a license-gated test; the gate receipt makes skipping that run fail agentic-mbse's suite (2a design D13).
- A change to codegen's declaration discrimination, slot construction or multiplicity reading that changes occurrence facts is not complete until agentic-mbse's summary matches or the contract is re-pinned.

### Rejected alternatives

- Keeping exclusive codegen ownership (option A′): rejected because it leaves the contract unable to decide instantiation-dependent refusals until a single move.
- End condition (i), codegen swaps onto the shared module and deletes its copy: not chosen by the owner (2026-10-18).
- Stored oracle outputs compared in agentic-mbse (Item 1's interim guard): retired by 2a, because a codegen change was caught only when someone re-captured the oracle.

Filing: owner, at merge (RG-3).
