# Brief: Item 9 spec — Contracts and Sealing (ModelContract / PackageContract)

You are the spec stage for Item 9 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 8 implement session is committing to this tree concurrently — write ONLY spec.md (+ CURRENT_WORK entry); touch no code.
- Artifact: `spec.md` in `.project/active/package-contracts/`.

## Provenance
- Concept (owner-ratified): "Contracts and the Evaluator" + Architectural Bets (sealing) + S4 "Not exercised" contract sentence.
- Epic Item 9: `.project/backlog/epic_constraint_execution.md`.
- **Certified upstream**: Item 7 (generation emits the full artifact set + embedded ConstraintCatalog + a fingerprint constant — read the real code in `generation/`, the catalog on ComputationGraph, and S4's test-only seal in `s4_lib.py` with its named gaps: coverage set, stale-file detection, environment compatibility); Item 8 in flight (snapshot-generated packages must seal identically — its live/snapshot artifact parity is your input).
- **Item 0's eight interface findings**: mismatch 5 (headline vocabulary — pinned runtime-owned in Item 10), mismatch 8 (package-load names by declared package name — Item 9 owns the protocol per Item 10's spec). The teax consumer (`simkit/evaluation/` loader) is the real downstream — read it for what load-verification must satisfy.

## Scope (epic Item 9 §1–3)
1. **ModelContract**: stable parameter and output IDs, constraint catalog, required evaluation semantics, semantic fingerprint — graph fields ONLY (test: no filesystem/YAML introspection on the ModelContract path); provided capabilities live in PackageContract.
2. **PackageContract seal**: content hashes over generated + preserved artifacts (excluding the seal and runtime outputs), generator/runtime versions; **verified on package load** (the teax loader's verify path), not just at packaging; coverage set, stale-file detection, environment compatibility — the S4 gaps become requirements.
3. Fingerprint namespaces IDs, never feeds them (no circularity); executable fingerprint stable across live loads and snapshot generation.

## Out of scope
Study-side contract consumption details (Items 10–12 landed their own surface; note the seam); signing/crypto beyond content hashes.

## Success criteria (from the epic)
- A tampered artifact and an unhashed extra file both fail load verification with named diagnostics.
- Fingerprint reproduces byte-exactly across independent live loads, snapshot generation, and sessions.
- Contract data derives from the graph alone.
