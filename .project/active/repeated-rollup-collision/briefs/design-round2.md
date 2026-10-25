# Brief: design round 2, repeated-rollup-collision

Sent to the design session on 2026-10-25 after `design-review.md` (verdict Revise). Orchestrator decisions [AGENT].

Revise `design.md` and its plan:

1. **M1: accept.** One class per distinct shape, named and placed from that shape's first copy (the D2 rule), instead of one class per copy in a differing group. Re-run the review's `nestdiv` probe and the spec's value set with it, and restate what limit, if any, remains, with a probe. File only a limit that survives.
2. **S1: accept.** Add a plan step: generate every generating fixture on `main` and on the branch, and diff the trees; single-copy fixtures must be byte-identical, and every difference is explained.
3. **S2: accept.** Imports use the writers' path function, so every written file is imported and every import has a file by construction.
4. **S4: accept.** A unit test on the shape comparison, and the structural test run over every package the oracle builds.
5. **S5: accept.** Check every computed value in both flipping fixtures before any baseline is re-captured.
6. **S3:** the orchestrator filed it as `[NESTED-OVERRIDE-LEAKS-TO-SIBLING]` (reproduced on stock: `a`'s leaves get `b`'s override). Out of scope here. Do not let this item's tests depend on that defect either way; where a test uses different values per copy, set them at the leaf def or through usage-level values the stock generator keeps separate, and say so.
7. Copy the review's product-lens block into `product-lens.md`.

Don't change `src/`, don't commit. End with `ARTIFACT: <path>`.
