# GAP-CLOSE Item 2 Implementation Evidence

## Independent audit warning-parity cure — 2026-07-18

The audit found that the route-parity projection omitted logger values. A kept regression now
captures the real lowering logger and compares exact bytes across repeated live lowering, an
equivalent relocated tree, and serialized snapshot replay. Every route emits, in order:

```text
Constraint <anonymous> at root-0/model.sysml:10:2 is not numerical and will not execute: warn_non_numerical_equality: equality is a valid non-numerical statement and is not executed
Constraint <anonymous> at root-0/model.sysml:20:2 is not numerical and will not execute: warn_non_numerical_equality: equality is a valid non-numerical statement and is not executed
```

The isolated regression passed. Relevant codegen selections passed 63 tests / 13 skipped in both
normal and optimized mode, followed by 16 licensed route/snapshot tests. Fixture diffs remain empty.

This record captures the frozen, isolated RED/GREEN overlay and the Item 2 validation gates.
Every historical record pins both coordinated repository revisions and the executable-profile
semantic version. Commands and outputs are appended as the phases run.

## Coordinated Baseline

- sysml-codegen: `6db321225a5c8568db0287b67ed1d04c03079cc2`
- agentic-mbse: `4ed2a0728ea49298666415cd389d9a6173a81a3e`
- profile: `executable-profile/v3`
- Detached roots: `/tmp/gap-lowering-integrity.aXkaZz/{codegen-baseline,codegen-candidate,companion}`.
- Baseline codegen tree: `40cfc0fcd69b63edada31a3c5fe9efdf14c8758b` (clean).
- Baseline companion tree: `ef483a41adce1318bc13e94afc36629e41945ee0` (clean).
- Frozen overlay SHA-256:
  `f4ae82df188eec3ded737c7720b7caa8b26ff128c7775976f4fac30029719323`.
- Fixture manifest: 179 files; manifest SHA-256
  `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`.

## Pre-Fix RED

Every command used codegen-then-companion `PYTHONPATH`, `PYTHONNOUSERSITE=1`,
`PYTHONDONTWRITEBYTECODE=1`, the exact detached-root environment assertions, and the frozen overlay
hash above. Each node ran in a fresh pytest process.

- F4: exit 1. The only assertion delta was `['raised']` versus the required two ordered warning
  values followed by `raised`. The caught halt still named `Evidence__blocked`,
  `block_real_equality_requires_tolerance`, and the `two-inequality` repair.
- F5 `non_numerical`: exit 1. Both source-specific warnings were emitted, then uniqueness rejected
  `anonymous__anon__2d86ce3777bf5f49` for the two live-shaped records.
- F5 `unassessed_form` (`satisfy`): exit 1 with no profile warning. Uniqueness rejected
  `anonymous__anon__10b15174e5bf22c8`.
- F5 `unsupported_owner`: exit 1 with no profile warning. Uniqueness rejected
  `anonymous__anon__84efb820788022e4`.
- Non-blocking warning control: passed with two warnings in source order and no duplicate.

The F5 failures were the production duplicate guard, not collection, setup, import, route, profile,
or license failures. The overlay asserted `name is None`, `qualified_name is None`, and exact
non-null file/line/column locations before every lowering call.

Focused command form (one fresh process per selector):

```text
env PYTHONPATH=<codegen-baseline>/src:<companion>/src PYTHONNOUSERSITE=1 \
  PYTHONDONTWRITEBYTECODE=1 EXPECTED_CODEGEN_REPO=<codegen-baseline> \
  EXPECTED_COMPANION_REPO=<companion> EXPECTED_OVERLAY_SHA=<sha> \
  uv run pytest -q <overlay>::test_f4_warnings_precede_block
env ... uv run pytest -q <overlay> -k 'anonymous_pair and <kind>'
```

Direct coordinated-baseline byte pins:

- named `non_numerical`: `Evidence_named_nonnum__named_nonnum__ae00ccca8ea0d861`
- named `unassessed_form`: `Evidence_named_unassessed__named_unassessed__ccbd872f5c3f2298`
- named `unsupported_owner`: `Evidence_named_unsupported__named_unsupported__e7202a6c6ee2d32a`
- eligible anonymous: `Pkg__Owner__anon__016538f43a48a34e`, raw identity
  `/evidence/root/model.sysml:10:2`, owner instance `Pkg__Owner`, 16-hex suffix, compile key
  `<anonymous>`

## Candidate GREEN

- Final normalized production patch SHA-256:
  `37f5b8c3e0ad4d74ce392f20fc6906c9df88157efdebd5550f66c607c0c9899e`. Applying it regenerates
  the original detached-candidate binary diff with SHA-256
  `4fb99f6803e62f01e92b6853ad35fdeb0a3cd9695f3808e988287caef463a374`.
- Exact candidate path set:
  `constraint_lowering.py`, `source_referent.py`, `pipeline_builder.py`, `capture.py`,
  `graph_rebuild.py`, and `serializer.py` under their approved production paths.
- Candidate worktree remained at codegen HEAD
  `6db321225a5c8568db0287b67ed1d04c03079cc2`; the companion remained clean at
  `4ed2a0728ea49298666415cd389d9a6173a81a3e`. The new source file was marked
  intent-to-add so the binary diff included it while `ls-files --others` stayed empty.
- The unchanged final overlay ran with candidate `src` first and companion `src` second. It
  reasserted both revisions, all import roots, profile v3, overlay hash, and candidate diff hash,
  then reported **5 passed**: F4, all three F5 kinds, and the non-blocking warning control.
- Direct candidate tests retained the three exact named IDs and eligible-anonymous ID recorded in
  Pre-Fix RED. Named IDs remain 16-hex. The eligible-anonymous raw location, 16-hex suffix, and
  `<anonymous>` compile key remain unchanged; `[ANON-ELIGIBLE-KEY]` is not implemented.

## Byte, Fixture, Migration, and Quality Gates

- Fixture manifest after implementation is byte-identical to Phase 1: 179 files, manifest SHA-256
  `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`.
  `git diff -- tests/fixtures` is empty. No fixture was added or recaptured.
- `tests/conformance/test_constraint_migration_mapping.py` is unchanged. Its focused command ran in
  the unlicensed environment and reported 12 license skips. The broader gate also selected it;
  no source, fixture-list, anonymous-corpus guard, or catf_mfe expected count changed.
- Final focused normal: **102 passed, 8 skipped**. Optimized control-flow run before the final
  type-narrowing-only guard: **102 passed, 8 skipped**, with pytest's expected `-O` assertion
  warning. Final normal rerun after that guard: **102 passed, 8 skipped**.
- Broader constraint/snapshot/catalog/CLI regression: **45 passed, 37 skipped**.
- Full default-environment suite: **2,206 passed, 205 skipped, 9 deselected, 23 failed, 96
  errors**. Every failure/error was in the existing SysIDE-license-dependent collection/setup or
  live integration families. No focused or license-free Item 2 test failed. This is not claimed as
  licensed live evidence.
- `ruff check src/` plus every Item 2 test/evidence file passed. Nine Item 2-owned/touched files
  pass `ruff format --check`. The untouched baseline and candidate both report the same three
  inherited whole-file format failures in `pipeline_builder.py`, `graph_rebuild.py`, and
  `serializer.py`; those files were not bulk-formatted because that would add unrelated churn.
- Full mypy initially exposed two Item 2 optional-location errors; an explicit fail-loud narrowing
  guard removed them. Final full mypy is the recorded project baseline: **76 errors in 17 files**.
  Targeted mypy reports **74 inherited transitive errors in 16 files**, with no Item 2 error; the
  only error on an approved touched file is the pre-existing `pipeline_builder.py:172` finding.
- Candidate `git diff --check` and Item 2-scoped current-worktree `git diff --check` passed.
  Candidate `ls-files --others --exclude-standard` is empty. The regenerated binary diff matches
  the recorded patch hash and its path allowlist is exactly six files.
- Item 1 files were not edited by this stage. Their final SHA-256 values are recorded in
  `evidence/hashes.txt`; none appears in the isolated candidate patch. No agentic-mbse, TEAx,
  catalog/schema model, snapshot-version, fixture, push, or close action is present.
