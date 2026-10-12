# Brief: spec revision — study-layer-to-codegen

Sent by the orchestrator to the spec session (resume), 2026-10-12, after the fresh review at `.project/active/study-layer-to-codegen/spec-review.md` (verdict Revise, committed `7224e54`). Read the review in full, then revise `spec.md`. Apply every must-fix and the should-fix list, subject to the orchestrator decisions below. Where a decision below settles a point differently from the review, follow the decision and record it in the spec.

## Orchestrator decisions [AGENT, orchestrator, 2026-10-12]

The owner delegated these at Align ("take accountability"). Record each one in the spec as an `[AGENT]` decision with its reason, and record each rejected alternative as one line.

**D6. Package form, inside the sysml-codegen distribution (closes OQ10 and L2-1, L1-5).**
- The tools ship as an importable package inside the `sysml-codegen` distribution.
- Reason: the tools read contracts that sysml-codegen's generator writes (`model_contract.json`, `package_contract.json`, pipelines, inputs). One distribution keeps the reader and the writer at the same version.
- Rejected: a separate distribution. Its benefit, adopting without moving fusion-tea's generator pin, is temporary, because fusion-tea has to move that pin to get generator fixes anyway. Meanwhile it opens a version skew between the contract writer and the contract reader.
- Rejected: installing the tool files into each target (L2-1). It brings back hand-copied drift, which is the problem this epic removes: copies that local edits keep, while tests run against the source. It also breaks the co-versioning above.
- Accepted cost: the root split, the tool-identity change and the fusion-tea wrappers. This is not an owner question.

**D7. Schemas stay byte-identical (settles L3-2, L3-3).**
- Every schema file and every `schema_version` string stays byte-identical to fusion-tea `b06585709`.
- Tool identity after the move fits the existing fields:
  - `tool.path` is the tool module's path relative to the installed distribution's import root, for example `sysml_codegen/<pkg>/indicators.py`;
  - `tool-source-digest/v1` is computed over those package-relative paths and bytes. The spec states that v1's "repo-relative path" means "relative to the root the tool's sources live under", which is the meaning at both homes. Record the reasoning.
- A reader tells pre-move from post-move by the `tool.path` prefix: `scripts/study/` versus the package prefix. The digest is the revision, because it is content-addressed. sysml-codegen's `0.1.1` version names nothing, as the review notes.
- SC7 becomes concrete: name the field and the prefix rule. A test runs a moved tool and checks the prefix. A test validates one real pre-move document from the staged fusion-tea sources against the unchanged schemas and checks its `scripts/study/` prefix.
- If design finds a field that cannot fit, it raises that through the orchestrator. It does not bump a version on its own.

**D8. Undeclared repo gate = the existing "unasked" blocker (settles L3-1's gate question).**
- A repo-scope gate the target did not declare blocks with `integrate`'s existing unasked/not-run outcome. Use the slug the code already has, and name it.
- A CANDIDATE still means all ten gates passed. A target that wants a CANDIDATE declares its repo gates.
- L3-1's other half also applies. Behaviour changes are a closed, enumerated list in the spec: each one says what changes and why. The parity check the review recommends becomes a criterion: run the original and the moved tool on the same inputs and compare outputs, with only the enumerated differences allowed. Cover every tool the fixture can drive, not only `indicators`.

**D9. Two import tiers (settles L1-4, L3-7).**
- The supported target API is what the installed runbook and record template tell a target to call, for example `identity.build_sealed` from a route module. It is documented.
- The fusion-tea compatibility surface is every other symbol in `CONSUMER_SURFACE.md`. It exists with the same name and behaviour, it is not documented as public, and SC6 tests it.
- The design enumerates both lists, including module attributes. It also defines the behaviour of root-dependent functions under the split, for example `manifest.repo_root()`.

**D10. The fusion-tea runbook lives in agentic-mbse (settles L3-12).**
- The runbook's durable home is agentic-mbse's epic tracking, next to the shared ledger. The epic owns the fusion-tea integration step.
- The implementing stage drafts it in this item folder. The orchestrator moves it to agentic-mbse before close, so there is one copy and this repo's delete-at-close rule loses nothing.

**D11. Scope, estimate and cut order (settles L2-2).**
- Add an estimate per criterion and a total. Overrunning the epic's 2 days is acceptable if it is stated: the owner accepted Item 2 at 2.4 days. The orchestrator reports the overrun to the owner at the end, so do not hide it.
- Cut order, first to last, applied only if the plan's estimate demands it:
  1. SC9's fusion-tea suite steps in the rehearsal. Keep the install, wrapper and re-verify steps.
  2. Requiring `integrate` to reach CANDIDATE on the neutral fixture. Keep its refusal paths and the gate-declaration tests.
  3. SC4's agent writing the manifest: the fixture supplies it instead.
  4. SC4's second (administrator) agent.
- This order puts the administrator reading last, unlike the review's order. That reading directly tests an owner-verbatim statement ("sufficient structure in the artifacts … so that another agent can effectively pick up the results"), and it is one short read-only run.
- Also: SC4 cites Item 2's dry run as its model, but that run stopped after round 1. Say so, and state what this dry run must reach.

## Verified fact for L3-8 [AGENT, verified by orchestrator 2026-10-12]

fusion-tea code outside `scripts/study/` and `tests/study/` never calls `tool_source_digest` or reads `TOOL_SOURCE_FILES`. The only caller outside the tools themselves is `scripts/integrate.py:89` and `:687`, and that file moves too. I ran `git grep` at `b06585709` over `exploration/**/*.py`, `tests/**/*.py` and `scripts/*.py`, excluding committed records. The root split therefore has no fusion-tea caller outside the moved set to preserve.

## Other review points

- **L1-1:** grade the Problem section's bar as `[AGENT] (orchestrator Align reading, 2026-10-12; the owner did not contest it)`.
- **L1-6, L2-3, L3-5, L3-6, L3-9, L3-10, L3-11, L3-13, L3-14:** apply as the review proposes. For L3-9:
  - if the design reuses agentic-mbse's `Installer`, the dependency bound has to guarantee the API exists, and the spec records that as a requirement on the design;
  - SC9 checks fusion-tea's agentic-mbse pin.
- **SC5 (L3-4):** widen the grep as the review lists. Add a line-by-line read-through record of the four ported instruction files plus the policy template. It gives a verdict per fusion-specific line, and those verdicts feed SC10's ledger rows. Drop the contradictory LCOE sentence. Vocabulary in labelled examples is legal.
- **ADR-0007:** cite its lesson that a "behaviour-preserving" move must be byte-faithful.

When done, add a short "Revision 2026-10-12" note to the spec that lists what changed against the review IDs. Do not commit. Do not start background tasks. Finish with `ARTIFACT: <path>`.
