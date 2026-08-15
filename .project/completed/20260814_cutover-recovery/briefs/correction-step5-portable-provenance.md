# Step-5 plan — portable provenance and invariant 35

**Written 2026-08-14 at `98dc3ec`, before implementation.** Ratified instruction: plan.md step-5
checkbox + `owner-disposition-20260811.md` disposition 4 — make provenance referents portable,
amend invariant 35 to semantic equality plus generated-byte equality after defined normalization
of permitted provenance metadata. Every decision below is `[AGENT]` under that ratification.

## The defect, measured this session

The live route keeps raw parser paths on every node's `source_file`
(`orchestration/elaborated_pipeline.py`, live arm) and normalizes only `exclusion_location`.
Consequences, each verified in the tree at `98dc3ec`:

- Live-generated `modules/` and `handwritten/` files carry checkout-absolute `SysML Source:`
  lines; v6-replay files carry portable `root-N/` referents. Pinned as a *permitted divergence*
  by `test_exact_route_generated_package.py::test_the_two_packages_differ_only_in_provenance_comments`
  and (execution lane) `test_fusion_tea_real_teax.py::test_the_two_packages_carry_the_same_model_and_differ_only_in_provenance`.
- The raw paths are not even canonical: SysIDE hands back the same file in two spellings, one
  with a leftover `//` URI prefix (`test_snapshot_v6_routes.py:198` pins
  `{None, absolute, "//" + absolute}` by value).
- Latent same-family leak: an unassessed-form constraint would put the raw path into the sealed
  catalog (`elaboration/project.py:1121`) — no fixture reaches it today.
- Invariant 34 (no checkout-absolute paths in generated code) is violated live; invariant 35's
  generated-byte clause is false on the exact route.

## Design decision — converge the rendering, not the route

Two candidate mechanisms:

1. **Route live through admission** (converge design D3). Rejected: design amendment A1
   (`elaborator-cutover/design.md:633`) records why the arms must stay independent — the
   route-parity comparison is blind to an `elaborate_admitted_sources` defect if both arms share
   it. The pin `test_the_live_arm_does_not_share_the_capture_route` stays.
2. **Rewrite live `source_file` in place through `map_live_source_referent`** — the exact
   mechanism the live route already uses for `exclusion_location`, extended to the whole graph
   (attrs, calcs, constraints, constraint_usages), mirroring capture's
   `_rewrite_sources_as_referents`. **Chosen.** The two mappings are independently derived
   (caller paths vs. staged admission) and provably agree — exclusion-location parity already
   rests on that agreement. The `//` artifact is handled (verified empirically: `commonpath`/
   `relpath` collapse redundant separators).

One real encoding gap closes with it: admission NFC-normalizes each path segment before
percent-encoding (`extraction/source_manifest.py:453`); `map_live_source_referent` does not.
`_encode_relative_path` gains the same NFC step so a non-NFC filename cannot split the routes.

**The "defined normalization of permitted provenance metadata" is therefore the shared portable
referent rendering itself** (`root-N/<NFC, percent-encoded relpath>`), applied by each route from
its own evidence at elaboration time. After it, **no permitted route-dependent metadata remains**:
generated-byte equality is byte-for-byte, with an empty residual normalization. Invariant 35 is
amended to say exactly that; invariant 34 becomes true as written and is not reworded.

## Blast radius, answered at preflight

- **Committed `baseline_outputs/`**: snapshot-shaped already (`root-0/…`), and no test
  regenerates them live (`test_baselines.py` is structural; goldens and
  `test_public_route_baselines.py` are snapshot-route). **No churn.**
- **v6 snapshot fixtures**: capture route untouched → bytes unchanged → **no recapture batch**
  (per the rev-2 evidence rules). Proven by the capture-verify gate (15/22/0) and an empty
  `git diff` over `tests/fixtures/` after the suite.
- **Fingerprints/contracts**: the semantic fingerprint already excludes node `source_file`
  (route parity holds today while paths differ), so `model_contract.json` bytes do not move.
  The live *instance-graph* fingerprint moves toward the captured one — a strengthening the
  tests will now assert as equality.
- **Group naming**: stem-based and already route-invariant (`project.py:330`); a `root-0/x.sysml`
  referent has the same stem as the absolute path. No generated-name churn.

## Path set (declared before editing)

Code:
- `src/sysml_codegen/orchestration/elaborated_pipeline.py` — live rewrite + docstring/comment
  corrections (the module docstring currently *claims* shared portable referents; false today).
- `src/sysml_codegen/analysis/source_referent.py` — NFC in `_encode_relative_path`; module
  docstring widens from "excluded constraints" to live provenance.

Tests:
- `tests/unit/test_source_referent.py` — NFC/route-encoding parity case.
- `tests/conformance/test_snapshot_v6_routes.py` — drop the source mask where it can now assert
  full equality; rewrite `…differ_only_on_module_provenance` to assert agreement by value.
- `tests/conformance/test_exact_route_generated_package.py` — the differ-only pin flips to
  whole-package byte identity.
- `tests/conformance/test_exact_route_snapshot_generation.py` — module docstring: claim 3 holds
  now; cite the byte-identity pin (Gate 4C cite-don't-duplicate).
- `tests/conformance/test_constraint_usage_domain_parity.py` — portable-referent assertion
  extends from the two snapshot routes to all three.
- `tests/execution/test_fusion_tea_real_teax.py` — differ-only-in-provenance flips to byte
  identity (execution lane).

Docs/records:
- `docs/architecture/reference/27-snapshot-generation.md` — the route-divergence account.
- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — invariant 35
  amendment (dated).
- `.project/active/elaborator-cutover/design.md` — dated note under A1: audit-F4 is answered by
  shared rendering; D3 stays un-converged and the pin stands.
- `.project/active/cutover-recovery/plan.md` — step-5 checkbox + completion record;
  `.project/CURRENT_WORK.md` status.

Matrix: no row cites the flipped tests (the v6 REQ family is the parked backlog item,
disposition 9); REQ-SNAP-22 and REQ-GEN-02/REQ-PIPE-01 citations are unaffected. Expect zero
row edits; recount only if that expectation breaks.

## Gates (zero-new against the step-4 baselines)

Licensed suite 2085/34/88 with zero license-skip lines (delta = deliberate test changes only);
execution lane 88; capture verify 15/22/0; corpus 9; ruff `src` 12; mypy 52-in-11;
`git diff` empty over `tests/fixtures/`; matrix untouched or recounted.

## Path-set delta, recorded at execution (2026-08-14)

Three surfaces outside the declared set turned out to carry the old premise and were amended in
the same bounded change:

- `tests/conformance/test_exact_route_fingerprint_stability.py` — its claim-3 test asserted the
  executable-fingerprint *divergence* by value and was built to fail when the divergence died
  ("the divergence claim is stale"); it did, and now asserts equality.
- `scripts/capture_v6_batch.py` — `--verify` masked module `source_file` in its live-vs-sealed
  comparison and its error text named the pinned divergence; the mask is removed, so the batch
  gate now proves full graph equality.
- `.project/active/cutover-recovery/ledger-4a.{json,md}` — rows L-007/L-010 cite the renamed
  route-parity node (`test_the_two_routes_agree_on_module_provenance`); re-pointed via
  `scripts/_ledger_edit.py`, `paths` and per-row `replacements` re-run green.
