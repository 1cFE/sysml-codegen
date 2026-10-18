# Staged: sysml-codegen ADR 0016 amendment (the subset contract is pinned the same way)

**Target:** sysml-codegen `.project/adr/0016-installer-reuse-through-an-api-version-pin.md`:

- `:17`, the Decision, which applies the API-version-pin rule to the installer only.
- `:30`, the invariant that `installer/v1` names the installer surface and `tests/conformance/test_upstream_pins.py` fails on a change.
- `:35`, the rejected 0.1.4 bump, whose reason (every committed v6 snapshot becomes unloadable) is the same reason here.

ADR bodies are immutable, so the amendment is a new entry plus a status flip by the script. Source: 2a design D12 (orchestrator decision O14). Evidence: `evidence/versioning.md`.

## Commands (run in sysml-codegen at merge)

```bash
.project/scripts/adr.sh new subset-contract-pinned-by-profile-version --title "The executable-subset contract is pinned by SUBSET_PROFILE_VERSION, not a package-version bound"
# fill the new entry's body from the section below, then:
.project/scripts/adr.sh amend 0016 <new-id>
.project/scripts/adr.sh index
```

Frontmatter to set: `provenance: "[AGENT] (EXEC-SUBSET-CONTRACT Item 2a design rev 3, D12; orchestrator decision O14) — owner ratification to be recorded at filing"`, `seams: [agentic-mbse, subset-profile]`.

## Entry body

### Decision

ADR 0016's rule, that sysml-codegen pins an agentic-mbse API by a version string and not by a package-version bound, also covers the executable-subset contract. agentic-mbse exports `SUBSET_PROFILE_VERSION` from `agentic_mbse.sysml.subset_profile`, and sysml-codegen pins it in `_upstream_pins.py`. `sysml_codegen/subset_profile_adapter.py` compares the two when it is imported and raises `ImportError` on a difference. The dependency bound stays `agentic-mbse>=0.1.3,<0.2`, and agentic-mbse is not bumped or published for the contract.

### Why

- The producer gap from ADR 0016 holds here too. agentic-mbse added `SUBSET_PROFILE_VERSION` in `b2d5768d` without changing its package version: it reports 0.1.3 before and after (`evidence/versioning.md`). No version bound can tell the two apart.
- A bump to 0.1.4 costs the same as in ADR 0016: the v6 snapshot loader refuses a snapshot whose recorded `agentic_mbse_version` differs, so every committed v6 snapshot becomes unloadable.
- `REASON_MAPPING` is reviewed against one set of rule records. The profile version changes whenever a record's decision changes, so it names exactly what the mapping was reviewed against.

### Invariants established

- `SUBSET_PROFILE_VERSION` in `_upstream_pins.py` equals the installed agentic-mbse's value, and `tests/conformance/test_upstream_pins.py` fails when it does not.
- Importing `subset_profile_adapter.py` against a different profile version raises. The check is at import, not lazy inside a handler as in ADR 0016, because the adapter is the mapping's only reader. In 2a nothing on the generate route imports it (pinned by `tests/conformance/subset_profile/test_reason_mapping.py`). Once Item 2b wires the adapter into generation, a profile mismatch stops `generate`; 2b decides whether that is wanted.
- One profile-version change, `subset-profile/v1` → `v2`, covers all of 2a's record changes (2a plan PD13). A later record change moves it again.

### Rejected alternatives

- Bumping agentic-mbse to 0.1.4 with a `>=0.1.4` bound: it makes every committed v6 snapshot unloadable, which is Item 2b's work to redo.
- No pin, reading whatever the installed screen reports: a mapping reviewed against one contract would be read against another without any failure.

Filing: owner, at merge (RG-3).
