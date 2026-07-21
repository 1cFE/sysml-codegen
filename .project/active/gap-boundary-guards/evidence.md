# GAP-CLOSE Item 3 Implementation Evidence

## Phase 1 — Pinned RED

- Revision: `6db321225a5c8568db0287b67ed1d04c03079cc2`
- Clean source materialization: `git archive` extracted beneath
  `/tmp/gap-boundary-guards-red.eCxVR2/baseline`
- Overlay: `/tmp/gap-boundary-guards-red.eCxVR2/overlay/test_gap_boundary_guards_overlay.py`
- Overlay SHA-256: `b1cf09fbc3588ef23029b90b829a8a9b1049d2ac3b7bded41d920821fc426fa6`
- Python: 3.12.3; Pydantic: 2.12.5; pytest: 9.0.2
- Fixture baseline: 179 files; sorted-manifest SHA-256
  `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`
- Inherited dirty-file manifest SHA-256:
  `41ff93f8d2919e1c29a07547fccbb9b3766ee76efd029959a9381ffe516a9a01`
- Pre-item `tests/unit/test_concrete_constraint_model.py` SHA-256:
  `6e66af4cd3fe4314f950727bf35f6a044c134d5555b0eba6d55c490b556661d5`
- Resolved model source:
  `/tmp/gap-boundary-guards-red.eCxVR2/baseline/src/sysml_codegen/resolution/models.py`
- Resolved verifier source:
  `/tmp/gap-boundary-guards-red.eCxVR2/baseline/src/sysml_codegen/contracts/verify.py`

Each node ran in a fresh pytest process with the clean baseline `src` first on `PYTHONPATH`,
`PYTHONNOUSERSITE=1`, and `PYTHONDONTWRITEBYTECODE=1`:

```text
python -m pytest -q OVERLAY::test_default_eligible_assignment_is_transactional  # exit 1
python -m pytest -q OVERLAY::test_default_exclusion_assignment_is_transactional # exit 1
python -m pytest -q OVERLAY::test_internal_directory_symlink_is_fatal           # exit 1
python -m pytest -q OVERLAY::test_escaping_directory_symlink_is_fatal           # exit 1
```

The F6 nodes reached the expected `ValueError`, then failed because the live model no longer
equaled its saved state. The F9 nodes failed because `VerificationResult(ok=True, diagnostics=[])`
was returned. There were no setup, import, collection, or unrelated failures.

## Candidate and Repository Gates

### Isolated candidate

- Clean candidate source: `/tmp/gap-boundary-guards-green.GELIIT/candidate`
- Resolved model source:
  `/tmp/gap-boundary-guards-green.GELIIT/candidate/src/sysml_codegen/resolution/models.py`
- Resolved verifier source:
  `/tmp/gap-boundary-guards-green.GELIIT/candidate/src/sysml_codegen/contracts/verify.py`
- Unchanged overlay SHA-256:
  `b1cf09fbc3588ef23029b90b829a8a9b1049d2ac3b7bded41d920821fc426fa6`
- Two-file binary diff SHA-256:
  `ce1944fd824e945349f51d6779402845842fad05730519430822ba6792847447`
- Production allowlist: `src/sysml_codegen/resolution/models.py` and
  `src/sysml_codegen/contracts/verify.py`

Each of the same four Phase 1 commands ran in a fresh candidate process with the same environment
controls. Every node exited 0 with `1 passed`.

### Repository gates

```text
focused:             57 passed
optimized focused:   57 passed (plus pytest's expected -O assertion warning)
broader:              53 passed
default full:       2213 passed, 205 skipped, 9 deselected, 23 failed, 96 errors
project mypy:         76 errors in 17 files (recorded baseline: 76)
touched Ruff:         passed
touched format:       passed
scoped diff check:    passed
```

The full-suite failures and errors are confined to the known SysIDE-license-dependent families and
have the same 23-failure/96-error shape recorded before Item 3. No licensed full-suite result is
claimed.

All 179 fixture hashes matched the Phase 1 manifest, and `git diff -- tests/fixtures` was empty.
All inherited dirty-file hashes matched except `tests/unit/test_concrete_constraint_model.py`, the
pre-dirty test file intentionally extended for Item 3. Its existing Item 2 duplicate-ID regression
remains unchanged. `git diff --name-only` against pinned HEAD for the production allowlist named
exactly the two permitted files.
