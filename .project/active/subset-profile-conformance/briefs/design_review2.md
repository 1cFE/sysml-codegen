# Brief: /_my_design_review round 2 for EXEC-SUBSET-CONTRACT Item 2a

Review `.project/active/subset-profile-conformance/design.md` (revision 2) against `spec.md`, the round-1 review `design-review.md`, spike `spikes/s1/findings.md`, `briefs/align.md` and `.claude/rules/`. Orchestrator decisions are in design § Orchestrator decisions (O1–O14); challenge one only with concrete harm. Sibling agentic-mbse worktree: `/home/reid/src/subset-conformance/agentic-mbse`.

This is the last review round. Confirm each round-1 must-fix is resolved, and look hardest at two new mechanisms, judged for engineering quality and proportion, not only correctness:
- **D13 receipt (`codegen_gate.json`)**: a hash of screen-dependent files; a test fails if they change without a new receipt. Is it sound, proportionate, and maintainable for a solo-owner repo with no CI, or is it ceremony that will be routinely re-stamped? Is there a simpler mechanism with the same guarantee?
- **D14 packaged cases (`agentic_mbse/sysml/subset_cases/`)**: conformance models shipped as wheel package data so codegen can read them through the package. Is shipping test inputs in the product wheel justified versus alternatives (e.g. codegen reading them via the editable sibling path, or a separate test-data distribution)? Size, coupling, what users of the wheel get.

Also re-check non-circularity end to end and phasing (P1 order, group E split trigger). Do not edit the design. Give a clear verdict. End with `ARTIFACT: <path>`.
