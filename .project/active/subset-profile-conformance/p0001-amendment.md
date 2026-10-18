# Staged: agentic-mbse P-0001 amendment (refused only with a retained conformance case)

**Target:** agentic-mbse `.project/product/0001-executable-subset-contract.md`:

- `:3`, the title ("refused only with a recorded generator probe").
- `:17`, the Promise ("A shape is reported `refused` only when a retained probe of the pinned generator observed that refusal in that context").
- `:27-28`, the Evidence lines, which cite `tests/test_subset_probe_evidence.py` and "80/80 probes certify at sysml-codegen `b5663c07`".

Promise bodies are immutable, so the amendment is a new ledger entry plus a status flip by agentic-mbse's script. Source: 2a design § Cross-repo enforcement of ADR 0001 invariant 1, D4 and O20. D4 retires probe citations, which makes the current promise false once 2a P2.1 lands. It is filed with the ADR 0001 amendment (`adr-0001-amendment.md`), which it rests on.

## Commands (run in agentic-mbse at merge)

```bash
.project/scripts/product.sh new executable-subset-contract-case-backed --title "agentic-mbse publishes a versioned executable-subset contract: refused only with a retained conformance case, CLEAR only over the implemented rules"
# fill the new entry's body from the section below, then:
.project/scripts/product.sh amend 0001 <new-id>
.project/scripts/product.sh check <new-id> <merge commit>
.project/scripts/product.sh index
```

Frontmatter to set: `provenance: "[AGENT] (EXEC-SUBSET-CONTRACT Item 2a design rev 3, D4; orchestrator decision O20) — owner ratification to be recorded at filing"`, `surfaces: [agentic_mbse.sysml.subset_profile, agentic_mbse.sysml.subset_cases, sysml-codegen, l6, guidance]`.

## Entry body

### Promise

agentic-mbse ships one versioned record (`SUBSET_PROFILE_VERSION`) of which model shapes, in which contexts, the sysml-codegen generator refuses, excludes, omits or admits, plus a pure evaluator that applies it to a user model. A shape is reported `refused` only when a retained conformance case shows the generator refusing it in that context. The case is checked against the live generator in sysml-codegen, and agentic-mbse changes are carried to that check by a required pre-merge run. Anything else is `unconfirmed`, missing facts are `unverified`, and `CLEAR` means clean over the implemented rules only, not "will generate".

### Authority

- The ADR 0001 amendment filed with this entry (staged as `adr-0001-amendment.md`): cases replace probes, and enforcement is split across the repositories.
- `.project/adr/0001-subset-profile-capability-ownership.md`, invariants 2–5, unchanged.
- [INHERITED: epic] `.project/backlog/epic_executable-subset-contract.md` Item 2 objective and success criteria.

### Evidence

- agentic-mbse: the records loader's citation-form check, `tests/test_subset_case_citations.py`, and the screen-answer tests over every packaged case.
- sysml-codegen: `tests/conformance/subset_profile/`, which checks each case's stored generator answer live and against the screen answer.
- The gate receipt `tests/fixtures/subset_profile/codegen_gate.json`, and `tests/test_subset_gate_receipt.py`.
- Counts and revisions are filled in at filing from the 2a P7 gate run.

### Scope

Library-level contract. Codegen reads it through `sysml_codegen/subset_profile_adapter.py`; nothing on the generate route uses it until Item 2b. L6 is Item 3, rendered guidance is Item 5.

Filing: owner, at merge (RG-3).
