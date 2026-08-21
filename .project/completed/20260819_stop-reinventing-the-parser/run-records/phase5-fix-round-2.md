# Phase 5 fix round 2 — measured-or-absent diagnostics

**Date:** 2026-08-19
**Brief:** [`briefs/phase5-fix-round-2.md`](../briefs/phase5-fix-round-2.md)
**Audit answered:** `audit.md`, re-audit rev 2 (`Needs Work`), findings R1 and R2.

## The principle this round holds every change to

**A diagnostic field is either measured or absent, never defaulted.**

Totality means a formed diagnostic always crosses the public boundary. It does not mean all four
elements are always non-empty. A fabricated citation is worse than the silence it replaced: it is
indistinguishable in form from a real one, so it survives review and misdirects the reader. Where an
authored site is in hand, the raise site attaches it; where none was read, the refusal says nothing
rather than something plausible.

## What was wrong, measured before the fix

Both cases reproduce at `C_prod-r2` `2234845` through the shipped CLI:

- A syntax error at line 18 of `model.sysml` reported as
  `SI_EVIDENCE_INCOMPLETE … unexpected internal failure: SysMLParsingError … [root-0/model.sysml:1]`.
  `SysMLParsingError` was missing from the passthrough tuple at
  `orchestration/exact_pipeline_context.py:288` while the sibling tuple one frame down had it, so a
  user's own syntax error was reported as an internal failure at a line nobody read.
- A failure caused by an unreadable `zzz_broken.sysml` reported against a valid
  `aaa_fine.sysml`: `SI_EVIDENCE_INCOMPLETE: root-0/aaa_fine.sysml … [root-0/aaa_fine.sysml:1]`.
  The catch-all's location came from the first `.sysml` file found under the first model root.

## What changed

1. **The seam reports only what it measured.** `unexpected_public_failure` now takes the failure and
   nothing else. It carries the new `SI_INTERNAL_DEFECT` code — a defect in the generator, not a
   statement about the model — and the whole cause chain, and it names neither a reference nor a
   location. `orchestration/diagnostic_context.py`, whose only job was to invent them, is deleted,
   along with `_caller_model_context` and `_nearest_model_context` in `elaborated_pipeline.py`.
2. **Formed refusals pass through as themselves.** `SysMLParsingError` joins the tuple at
   `exact_pipeline_context.py:288` and its snapshot sibling; a `CodeGenerationError` raised inside
   generation is logged as the refusal it already is rather than relabelled an internal defect.
3. **Parse failures carry the parser's own measured sites.** The refusal reads `filename`, `line`,
   `col`, and `code` off the SysIDE diagnostics — `root-0/model.sysml:18:1: (parsing-error) …` — and
   renders them through the manifest referents on the capture arm. The extractor's console report
   does the same, so a capture-time refusal no longer names a private staging directory. The
   extraction screen renders its blocking diagnostics the same way and attaches the anchor
   diagnostic's raw location, leaving the one fail-closed referent lookup where it already lived.
4. **Named raise sites attach their real authored context.** `SI_REDEFINITION_INVALID` (every site),
   the `item def` arm of `SI_CONSTRAINT_UNATTACHED`, `SI_RENDERING_COLLISION` (all twelve sites) and
   `SI_CONTAINMENT_RECURSIVE` name the declarations involved and cite the site they were read from.
   The generation preflight family gained stable code tokens — `DUPLICATE_OUTPUT_PATH`,
   `PARAMS_KEY_UNCOVERED`, `CONSTRAINT_DOMAIN_INCOMPLETE`, `COVERAGE_ACCOUNT_INVALID`,
   `REGISTRY_CLASS_NAME_COLLISION`, `PARAM_FIELD_COLLISION`, `PREDICATE_COMPILE_FAILED`,
   `CONSTRAINT_PREDICATE_MISSING` — and cites a module's source when the graph measured one.
5. **The totality proofs enforce the principle.** `assert_no_location_is_invented` fails on a
   fabricated field, not merely on an empty one, and an AST guard in
   `tests/conformance/test_diagnostic_provenance_sites.py` enumerates the four guarded codes rather
   than a list of scenarios, so a new raise site for one of them is covered the day it is written.

## Behaviour after the fix, same two models

```text
ERROR: SysML parsing failed: Failed to load SysML models: root-0/model.sysml:18:1: (parsing-error) …
ERROR: Model failed exact-route validation: SI_INTERNAL_DEFECT: <internal defect>: unexpected
internal failure: PermissionError: [Errno 13] Permission denied: '…/zzz_broken.sysml'
```

The second names the file that caused the failure, never the innocent one beside it, and cites no
location because none was read.

## Mutation check

The two new proof files were run against the unfixed parent with its own sources
(`PYTHONPATH` at `C_prod-r2`): **25 failed, 7 passed**. Every new or changed kept test fails there;
the 7 that pass are pre-existing proofs the round did not touch.

## Gates rerun

From the sealed extraction (license loaded, `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` naming that
build's own manifest):

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
cd /tmp/stop-parser-rev2/artifacts-r3-provisional/extracted/codegen/sysml-codegen-0.1.1
STOP_PARSER_ARTIFACT_SOURCE_INPUTS=/tmp/stop-parser-rev2/artifacts-r3-provisional/artifact-source-inputs.json \
PYTHONPATH=$PWD/src \
/tmp/stop-parser-rev2/worktrees/sysml-codegen/.venv/bin/python -m pytest tests/ -q -p no:randomly
```

**2,542 passed, 9 skipped, 94 deselected, zero failures.** The count rises from 2,524 by exactly the
18 nodes this round added: the totality suite grows from 14 to 23, and the new raise-site provenance
suite adds 9. `ruff check src/` is clean; `mypy src/` holds its 30-error baseline in the same 8
files, with two line numbers shifted and the file count down from 76 to 75 with the deleted
`diagnostic_context.py`.

## Re-mint

Identities, artifact and evidence hashes, the full 21-lane table, and the runner and auditor
commands are recorded in the plan's "Phase 5 fix round 2 completion — the r3 chain" section.
In short: `C_prod-r3` `14130a89a3b9423a235eaa6c88f356a41a6767fd`, `F_final-r3`
`83551fbb81fc8cdd34fe0b12c64703ab5eab7ed9`, `C_evidence-r3`
`875ba01a8fd10b49928cb3e69b7245850128a844`, Agentic unchanged at
`443388823f0db46c14df1728d3843d0a74ee7590`. All 21 lanes matched their declared status and counts;
the four-group mechanical auditor returned PASS. The r2 chain is preserved at `evidence-chain-r2`.

Two lane expectations were recalibrated in the committed runner, and only two: `codegen-default`'s
counts (the 18 new nodes) and the `codegen-mypy-baseline` declared hash (same 30 errors, shifted
line numbers, one fewer file). One provisional runner pass was needed first to measure them, and a
second to re-pin Fusion to the calibrated production commit; neither supplied evidence to the final
chain.

## Deviations

- The first calibration attempt declared the raw `stdout` digest for `codegen-mypy-baseline`. The
  runner hashes a normalized `stdout + stderr` payload instead, so the lane refused, the calibration
  commit was amended with the value recomputed through the runner's own `_output_hash`, and the
  chain was rebuilt from there. The method was checked against the two unchanged nonzero baselines,
  which reproduce their declared hashes exactly.
- Two existing proofs changed with the messages they pin: the incomparable-writers detail now names
  the three declarations it could not order, and the preflight prose pins moved to the new code
  tokens. One reviewed raw-selector row was retired because the read it recorded no longer exists.
