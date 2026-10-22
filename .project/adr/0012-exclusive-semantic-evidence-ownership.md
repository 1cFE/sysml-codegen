---
id: 0012
title: Semantic evidence has one acquisition owner and complete closed values
date: 2026-10-12
owner: Reid W
status: amended
amended_by: [0018]
superseded_by: null
provenance: "[INHERITED: approved parser-remediation design cited below]"
seams: [extraction, elaboration, generation, agentic-mbse]
supersedes: null
promoted_to: null
---

## Decision

Each production semantic fact has one reviewed acquisition owner. Expression consumers use the pre-graph evidence inventory and Agentic's total reference inspection; complete exact references and indexed references are distinct closed values, and a deep relationship path either preserves every segment or refuses. Generation derives registry metadata from its graph authority rather than accepting a caller's second type inventory.

## Why

A correct helper cannot protect consumers that bypass it. Earlier alternate reads silently dropped indices, omitted referents, shortened paths, or supplied an empty registry type set. Exclusive ownership, closed values, and reviewed route guards remove those weaker accounts instead of relying on a shared exception handler to discover the damage later.

## Invariants established

- Indexed references refuse before graph allocation and defensively at exact-only consumption; they cannot masquerade as resolved paths.
- Math `ExpressionIR` is rendering/compilation evidence, not an alternate occurrence-resolution authority.
- Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership; reviewed manifests guard the acquisition operations rather than banning all raw reads.

## Sources and bounds

The recommendation was [AGENT] in `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260817-164828_expression-evidence-boundary-convergence-assessment.md`, Architecture insights and Recommendations. Its adopted mechanisms are inherited from `7e82a9ce5ddedad07f299fd7f0e87af719ba9781:.project/completed/20260819_stop-reinventing-the-parser/design.md`, total inspection, D7, D9, and the ownership table. Approval does not make these owner-originated decisions. The general boundaries remain `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md` and `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`.

Implementation: `src/sysml_codegen/elaboration/expression_evidence.py`, `src/sysml_codegen/extraction/binding_source.py`, and `src/sysml_codegen/generation/registry.py`. Controls: `tests/conformance/test_expression_evidence_ownership.py`, `test_expression_evidence_integrity.py`, and `test_generation_exit_type_preflight.py`. These establish scoped ownership/value boundaries; internal-defect diagnostic totality remains separately tracked in `.project/backlog/BACKLOG.md`.
