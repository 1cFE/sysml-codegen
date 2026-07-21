# Item 6 Implementation Evidence

## Phase 1 — Frozen Reviewed-State RED and Controls

- Reviewed revision: `512786c7dfab44fba7a0185d09e845b7494c702d`
- Archived source: `/tmp/constraint-wave-seal-red.VfryFN`
- Python: 3.12.3
- pytest: 9.0.2
- Overlay:
  `.project/active/constraint-wave-seal-symmetry/evidence/test_constraint_wave_seal_symmetry_overlay.py`
- Overlay SHA-256: `e928cdc64eb514dd28e051259888499c695c4307e13ebb3a46c72d5dc50a1fed`
- Fixture-manifest SHA-256:
  `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`
- Resolved package source:
  `/tmp/constraint-wave-seal-red.VfryFN/src/sysml_codegen/__init__.py`
- Resolved seal source:
  `/tmp/constraint-wave-seal-red.VfryFN/src/sysml_codegen/contracts/seal.py`
- Resolved verifier source:
  `/tmp/constraint-wave-seal-red.VfryFN/src/sysml_codegen/contracts/verify.py`

Each node ran in a fresh process with the archived `src` first on `PYTHONPATH`, user-site imports
disabled, bytecode disabled, and the task-specific uv cache under `/tmp`. Collection found exactly
the 29 plan-required node names.

Controls and reviewed-behavior characterizations exited 0:

- regular file/directory sealing;
- reviewed escaping-file hashing and directory-link skipping;
- reviewed dangling-link verifier acceptance;
- both inherited F9 directory-link verifier controls.

The remaining 23 nodes exited 1 at their named behavior assertion. Direct seal did not raise for
the root, the six file/directory target cells, or the excluded seal path. Verification accepted or
misclassified root/file/dangling/excluded links, used the old directory-link message, reported
integrity findings instead of the link, and used the old walk-error phase. Generation reached its
patched clear seam, Step 9 wrote through linked `contracts/`, re-seal returned success through the
linked model-contract route, and the emitted verifier accepted a dangling link. There were no
collection, import, setup, or unrelated failures.

The kept tests were added before production edits and independently failed on the same missing
error type, dangling-link acceptance, linked re-seal, Step 9, and emitted-verifier behavior.

### Inherited dirty-work baseline

The pre-item dirty paths were project-management artifacts and three other active Item directories.
Recorded file hashes:

- `.project/CURRENT_WORK.md`: `2417e9ce…da98`
- `.project/backlog/BACKLOG.md`: `dd9beb3f…9801`
- `.project/backlog/epic_gap_close.md`: `a498a985…c16d0`
- `.project/backlog/epic_constraint_pr_wave_remediation.md`: `e37bb3c1…cadc3`
- `.project/backlog/epic_gap_close_audit_independent.md`: `295880d9…e0bd`
- `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`:
  `90e7b86a…24f`

No production file was dirty before Item 6.

## Candidate Evidence

### Source isolation and scope

- Final isolated candidate: `/tmp/constraint-wave-seal-final.GbGeYq`
- Candidate base: the same archived `512786c7…` source as Phase 1
- Production allowlist:
  - `src/sysml_codegen/contracts/seal.py`
  - `src/sysml_codegen/contracts/verify.py`
  - `src/sysml_codegen/contracts/__init__.py`
  - `src/sysml_codegen/cli/__init__.py`
- Four-file production binary-diff SHA-256: `55af22cd…4137`
- Complete production/kept-test binary-diff SHA-256: `49e930fc…60c6`
- Resolved candidate imports were under
  `/tmp/constraint-wave-seal-final.GbGeYq/src/sysml_codegen/`.
- The unchanged overlay SHA-256 remained `e928cdc6…1fed`.

Every one of the 29 frozen nodes ran in its own fresh process against the final isolated candidate
with the same user-site, bytecode, and `PYTHONPATH` controls as Phase 1. Every node exited 0.

### Canonical behavior and route gates

- Seal/verifier unit files: 55 passed normally; 55 passed optimized.
- CLI focus: 3 passed.
- Step 9 conformance: 9 passed.
- CLI plus Step 9 optimized: 19 passed.
- Canonical/emitted byte identity and stdlib-only import nodes: 2 passed independently.
- Final five-file focus: 76 passed, 2 licensed skips, both normally and optimized.
- Broader package gate: 84 passed, 3 licensed skips.

The root token is `"."`; descendants use relative POSIX paths. Every link result is the sole fatal
`INVALID_PATH` with message `symlinks are forbidden beneath the package root`. Preflight walk
failure is the sole `ARTIFACT_UNREADABLE`. Generation guards before clear/setup, Step 9 guards
before contract writes, and re-seal guards before its model-contract check.

### Fingerprint consequences

Source-isolated generation from the same snapshot produced:

| Value | Reviewed | Candidate |
|---|---|---|
| canonical/emitted verifier SHA-256 | `24eb3565…0276` | `ad0a855a…7284` |
| executable fingerprint | `493a9caa…aa6e` | `ccc5efc1…ba3a` |

The complete artifact maps differed at exactly `contracts/verify.py`. Every non-verifier artifact
hash was identical. Both executable fingerprints were independently recomputed from sorted
`path:hash` lines. The candidate emitted verifier is byte-identical to canonical source and its
recorded artifact digest equals SHA-256 of those exact bytes. Two licensed live-vs-snapshot nodes
were unavailable and remain unclaimed.

### Repository and static gates

- Default full suite: 2,243 passed, 205 skipped, 9 deselected, 23 failed, 96 errors. Every
  failure/error is in the known SysIDE-license-dependent families. This is not claimed green.
- Mypy target and full commands: the exact recorded 76 errors in 17 files; no Item 6 error.
- All nine editable production/kept-test Python files: Ruff clean and format clean.
- Frozen overlay: exact Ruff command found only one unused import, import ordering, and four
  line-length findings. The file was restored to its Phase 1 SHA rather than invalidating historical
  evidence. Ruff passes it with `I001,F401,E501` excluded. This is a recorded validation-command
  deviation, not a production or test-behavior exception.
- Scoped `git diff --check`: passed.
- Fixture diff: empty; fixture-manifest SHA-256 remains
  `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`.
- Saved unrelated dirty-file hashes all remain unchanged. `CURRENT_WORK.md` changed only for the
  required Item 6 status synchronization. Other active-item directories were preserved.

No commit, push, PR comment, merge, external F1 change, fixture refresh, schema/version change, or
external-system mutation occurred.
