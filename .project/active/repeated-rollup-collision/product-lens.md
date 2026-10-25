# Product-lens ledger: repeated-rollup-collision

## spec — 2026-10-25 — rev af981956 (.project/active/repeated-rollup-collision/spec.md)

Point (re-derived): A well-formed model must generate. Each copy of a repeated sub-assembly is its own occurrence, with its own inputs, its own rollup output and its own pipeline entry, and values are never merged across copies. Refusal is only for ill-formed models or for a genuine identity conflict, and it is a named diagnostic. The owner asked for a fix, not a documented limit. [sources: owner-verbatim 2026-10-25 "yes file it and orchestrate a fix in sysml-codegen" on BACKLOG [REPEATED-ROLLUP-REGISTRY-COLLISION]; .project/product/0003-no-workarounds-for-bad-models.md and 0004-product-identity-parse-walk-emit.md (owner); 0002-exact-owner-anchoring.md (agent/ratified); docs/architecture/modeling-assumptions.md §6 and ADR 0011 (INHERITED); grade: owner/HARD for "the ordinary repeated shape builds", INHERITED for per-copy separation]

Falsifier: `Top { part sub : Sub[2]; }`, where `Sub` sums `leaf : Leaf[3]`, fails `check`. Or it builds, but changing one leaf under `sub[1]` changes `sub[0]`'s value. Or the registry quietly picks one of several class definitions or entries, so that some pipeline entry runs a class whose inputs differ from the entry's own inputs.

Findings:
- spec-F1 [DO] The shape-divergence criterion allows a refusal for a well-formed model (`a : Sub; b : Sub { part :>> leaf[2]; }`). §6 calls non-uniform arrays a normal shape. A refusal would leave the owner's fix incomplete for a valid model. — docs/architecture/modeling-assumptions.md §6 (INHERITED) — disposition: design records the build-or-refuse decision; a refusal requires a filed backlog row. Applied to the spec's shape-divergence criterion and open question.
- spec-F2 [DO] The spec contradicted itself on where class identity comes from: "module_type keeps its current derivation" versus "a second class name for the differing copy". That second identity must be created once, at projection, and the registry must only look it up. — .project/adr/0009-compute-once-look-up-thereafter.md (INHERITED, live) — disposition: [INFERRED] line amended; design states where the divergent identity is created.
- spec-F3 [DON'T-risk] Keeping one rollup file per copy and registering the class once means the registry imports one of N identical definitions (smells 1 and 6). — smells 1 and 6 (AGENT) — disposition: spec now requires one file per shared class unless design justifies otherwise; design_review and audit check it.
- spec-F4 [DO] Every value criterion depended on the real-TEAx lane, and `simkit` is not importable on this machine. — README.md "Development" (INHERITED) — disposition: spec now names where the value criteria run (the `pytest -m execution` lane with `TEAX_SIMKIT_PATH`) and adds a registry-based structural check that runs in the default suite.

Gate: DISPOSED (spec-F1, spec-F2, spec-F3, spec-F4)
