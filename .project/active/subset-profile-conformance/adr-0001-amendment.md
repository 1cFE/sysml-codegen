# Staged: agentic-mbse ADR 0001 amendment (conformance cases replace probes; enforcement split across the repositories)

**Target:** agentic-mbse `.project/adr/0001-subset-profile-capability-ownership.md`:

- `:17`, the Decision's last two sentences ("…EXEC-SUBSET-CONTRACT Item 2 adds a permanent parity test in codegen CI").
- `:29`, invariant 1 (outcomes rest on "a probe of the pinned generator whose observed code matches, or a corpus citation for `admitted`").
- `:34`, invariant 6 ("a permanent parity test in codegen CI … Until it exists, the recorded parity run (`scripts/subset_profile/occurrence_parity.py compare --all`) … is the check").

ADR bodies are immutable, so the amendment is a new agentic-mbse entry plus a status flip by agentic-mbse's script. Source: 2a design § Cross-repo enforcement of ADR 0001 invariant 1, D4, D13, D14. It replaces the spec's staged wording ("cases admissible alongside probes"), which is `[INFERRED]` and too weak once probes retire (2a P2.1).

**Already stale.** Invariant 6's interim check names `scripts/subset_profile/occurrence_parity.py`, which 2a P1.5 removed (agentic-mbse `8be21e04`). The check it stood in for now exists: sysml-codegen `tests/conformance/subset_profile/test_occurrence_parity.py`. Until this entry is filed, invariant 6 points at a deleted script.

## Commands (run in agentic-mbse at merge)

```bash
.project/scripts/adr.sh new subset-evidence-is-a-conformance-case --title "Subset contract outcomes rest on conformance cases, enforced where each check can see"
# fill the new entry's body from the section below, then:
.project/scripts/adr.sh amend 0001 <new-id>
.project/scripts/adr.sh index
```

Frontmatter to set: `provenance: "[AGENT] (EXEC-SUBSET-CONTRACT Item 2a design rev 3, D4/D13/D14; orchestrator decisions O1, O2, O16, O20) — owner ratification to be recorded at filing"`, `seams: [agentic-mbse, sysml-codegen, l6, guidance]`.

## Entry body

### Decision

ADR 0001's Decision and invariants 1 and 6 are amended. A record's outcome now rests on a conformance case, not a probe. A `case:<id>` citation resolves to the packaged case `agentic_mbse/sysml/subset_cases/<id>/` and to sysml-codegen `tests/expectations/subset_profile/cases/<id>.json`, the case's stored generator answer. `probe:` citations are removed. The occurrence summary and codegen's occurrence index are held together by sysml-codegen's parity test, run by codegen's suite and by agentic-mbse's required pre-merge run. Every other 0001 invariant is unchanged.

Enforcement is split by what each repository can see:

| Check | Where it runs |
|---|---|
| Citation form | agentic-mbse records loader |
| The cited case exists in the package, and its stored screen answer shows the pair | agentic-mbse `tests/test_subset_case_citations.py` |
| The screen reproduces every packaged case's stored answer | agentic-mbse `tests/test_sysml/test_subset_profile_rules_{instantiation,modelwide}.py` |
| The case's stored generator answer exists, matches the generator live, and agrees with the screen answer | sysml-codegen `tests/conformance/subset_profile/` |
| An agentic-mbse change was run through the codegen check | agentic-mbse `tests/test_subset_gate_receipt.py` |

### Why

- Item 1's probes judged the generator once, at one pinned revision, and stored the verdict in agentic-mbse. A generator change made them stale without failing anything. A case is checked against the live generator every time sysml-codegen's suite runs.
- agentic-mbse cannot run the generator (ADR 0001 invariant 3, codegen ADR 0007), so it cannot check generator backing. sysml-codegen cannot read agentic-mbse's `tests/` tree (2a spec Boundaries, [HARD]), so it reads the cases as package data. Each check sits where its inputs are readable.
- The loader checks only the citation's form, so it stays pure over text and synthetic records in `tests/helpers/subset_records.py` keep loading (O16).
- There is no codegen CI (O1). Without a required run, an extractor or evaluator change would meet the generator only when someone ran codegen's suite by hand.

### Invariants established

1. *(replaces 0001 invariant 1)* The contract reports any outcome other than `unconfirmed` only when the record cites at least one `case:` or `corpus:` evidence item. Each cited case is packaged, its screen answer shows the pair, and sysml-codegen's tests show the generator's stored answer holding live and agreeing with it.
6. *(replaces 0001 invariant 6)* The occurrence summary and codegen's occurrence index are held together by end condition (ii): sysml-codegen's `tests/conformance/subset_profile/test_occurrence_parity.py`, run by codegen's suite and by the pre-merge run.
7. *(new)* A merge into agentic-mbse that changes any file under `src/agentic_mbse/sysml/` or `src/agentic_mbse/errors.py` requires a passing `scripts/subset_profile/codegen_suite.py` run, recorded in `tests/fixtures/subset_profile/codegen_gate.json`. The receipt test fails when the covered files' digest differs or a packaged case is missing from the receipt. A `pre_pr` check ties the receipt's `codegen_rev` to the codegen branch being merged.

### Limits

- A forged receipt cannot be told apart from a real one.
- The `pre_pr` check on `codegen_rev` is procedural: it runs only when `pre_pr` runs.

### Rejected alternatives

- Probe citations beside cases: two live authorities for one outcome, against invariant 5.
- A citation file written by sysml-codegen and read by agentic-mbse: a reverse dependency.
- Relying on codegen CI: none exists.
- A check in sysml-codegen alone: it runs only when someone runs sysml-codegen.

Filing: owner, at merge (RG-3).
