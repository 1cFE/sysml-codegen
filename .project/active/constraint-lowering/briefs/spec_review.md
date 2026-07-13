# Brief: Item 5 spec review — Concrete Lowering

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this spec; review it adversarially.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `spec-review.md` in `.project/active/constraint-lowering/`.

## Review target
`.project/active/constraint-lowering/spec.md` (brief at `briefs/spec.md`).

## Ground truth
- Concept: `.project/concepts/constraint-execution-and-space-studies-claude.md` — if that path 404s, it's `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — "Concrete Lowering" + Required Invariants.
- S4's proven lowering shape: `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py` + findings.
- S3 carry-forwards (concept Appendix B).
- **Landed upstream types the spec references by name**: reference copies at `.project/reference/agentic-mbse-landed/` (Item 1 facts + Item 2 IR, certified) — the spec author couldn't read these; a prime review angle is whether the spec's assumptions about fact shapes match the real types (tagged owner fact kinds, actuals shapes, defaulted-formal representation).
- Current pipeline: `analysis/dependency_backtracker.py` (the fallback the strict seam must NOT reuse — EP-key collapse), `core/output_registry.py`, `resolution/graph_builder.py`, `analysis/part_instance_index.py` (Item 4, incl. AllOccurrencesResult.blocked).
- Memory-grade risk note (from the epic risk table): the F4-cutover lesson — parity comparand = the exact replaced function.

## What to probe hardest
1. **Fact-shape fidelity.** Walk the spec's requirements against the real landed types: does anything assume a field or shape that doesn't exist (e.g. how `owning_definition.kind` maps to expansion rules; where actuals carry formal targets; how omitted defaulted formals appear)?
2. **Phase-placement precision.** "After aliases, output registry, supplied-value materialization; before backtracking" — locate those exact points in today's orchestration code and check the spec names a well-defined seam (function/call-site grade), not a vibe.
3. **Blocked-definitions handling.** Item 4 surfaces blocked defs explicitly. Does the spec say what lowering does when a constraint-owning definition has a blocked (non-finite) multiplicity — validation error naming it (concept: an expected instance that cannot form fails validation)? Silence here would recreate the swallow the Item 4 audit killed.
4. **Strict-resolution completeness.** For each actual category (owner-scope chain, design-attribute reference, literal, omitted defaulted formal): is the resolution rule + failure mode fully specified? Is the DESIGN_ATTRIBUTE entry-point minting scoped so it cannot collide with existing EP keys (the F4 lesson)?
5. **Identity spec.** constraint_id inputs: is "source-local identity" defined precisely enough for anonymous assertions (ordinal semantics, and the no-cross-version-stability caveat)? tracking_key: authoring surface named? Multiplicity-sibling channels: per-occurrence wiring stated?
6. **Success-criteria testability**: the four criteria — is each verifiable by a named test shape (control-prune vs retained; V11 on extended graphs; repeated-load byte-identity; corpus byte-identity)?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code and the reference copies — do not take the spec's word.
