# Staged: sysml-codegen ADR draft (where conformance cases live, and what codegen checks of them)

**Target:** a new sysml-codegen entry under `.project/adr/`, refining `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md:39-40` (a model fact is computed in agentic-mbse, an output fact in sysml-codegen) for conformance-case data. It amends nothing; 0007 stays as it is. This is the sysml-codegen half of one decision filed in both registers, each where it binds (2a design § Next-Stage Handoff). The agentic-mbse half is `adr-0001-amendment.md`.

Source: 2a design D4, D14, and § Cross-repo enforcement of ADR 0001 invariant 1 (orchestrator decisions O2, O16). Register routing: it binds code-generator builders, so it goes in `.project/adr/` (`.project/adr/0001-route-decisions-by-who-they-bind.md`).

## Commands (run in sysml-codegen at merge)

```bash
.project/scripts/adr.sh new conformance-cases-placed-by-what-they-test --title "Conformance cases live where what they test can read them; codegen checks generator backing"
# fill the new entry's body from the section below, then:
.project/scripts/adr.sh index
```

Frontmatter to set: `provenance: "[AGENT] (EXEC-SUBSET-CONTRACT Item 2a design rev 3, D4/D14; orchestrator decisions O2, O16) — owner ratification to be recorded at filing"`, `seams: [agentic-mbse, subset-profile, tests]`.

## Entry body

### Decision

A conformance case that tests the subset screen keeps its models and its stored screen answer as agentic-mbse package data, at `agentic_mbse/sysml/subset_cases/<id>/`. Every other case lives in sysml-codegen at `tests/fixtures/subset_profile/<id>/`, with its screen answer in codegen's expectation file. Each model has one copy. sysml-codegen reads agentic-mbse's cases through the installed package only, never through agentic-mbse's `tests/` tree.

sysml-codegen owns the generator half of each case: `tests/expectations/subset_profile/cases/<id>.json` is its stored generator answer, and sysml-codegen's tests check it.

### Why

- Both repositories must read a screen-tested case. agentic-mbse runs the screen on it, and sysml-codegen runs the generator on it. Package data is the one place both can read without a reverse dependency (ADR 0007) or a read of agentic-mbse's `tests/` tree, which the 2a spec rules out ([HARD], spec Boundaries).
- A copy of a model in each repository can drift, and a hash guard on the copy only reports drift after it happens.
- agentic-mbse cannot run the generator, so the check that a case's generator answer holds live can only run here.

### Invariants established

- Every case, in either home, has exactly one stored generator answer in `tests/expectations/subset_profile/cases/`, and no case ID exists in both homes. A pure test in `tests/conformance/subset_profile/` checks both.
- For every case, sysml-codegen's tests require the stored generator answer to match the generator live and to agree with the case's screen answer.
- Every record citation to a `corpus:` fixture is checked the same way as a `case:` citation.
- sysml-codegen reads a packaged case's layout through its `case.json` `schema` field (`subset-case/1`), and checks that field before it reads the rest.

### Rejected alternatives

- Models in agentic-mbse's `tests/`, read by sysml-codegen through the sibling path: it breaks the package-only boundary, and it fails on any install that is not a sibling checkout.
- Models in sysml-codegen, read by agentic-mbse: agentic-mbse's suite would depend on its downstream checkout.
- Excluding `subset_cases/` from the wheel: codegen's tests would break silently on a wheel install.
- A separate test-data distribution: a second package and version relation for about 100 KB.
- A hash-guarded copy: kept only as the fallback (O2), and not used.

Filing: owner, at merge (RG-3).
