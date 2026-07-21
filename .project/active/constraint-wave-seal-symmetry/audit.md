# Audit: CONSTRAINT-WAVE Item 6 — Seal and Verify Symlink Symmetry

**Verdict:** Certify
**Audited:** 2026-07-18
**Branch:** constraint-exec-epic
**Commit:** 512786c (candidate changes are uncommitted)

---

## Summary

The implementation satisfies the revised all-symlinks-forbidden contract at direct seal,
canonical and emitted verification, generation preflight, Step 9, and re-seal. Independent normal,
optimized, historical RED, fingerprint, no-follow, ordering, mutation, static, fixture, and scope
checks found no production gap or undocumented design deviation.

## Findings

### Plan completion

All five phases verified. The frozen overlay reproduces 23 defect-specific failures and six
controls at reviewed commit `512786c`, then passes all 29 nodes unchanged on the candidate. The
implementation is confined to the four planned production files and five planned kept-test files;
other dirty work remains outside Item 6.

### Spec conformance

- **SC-1 — seal/verify symmetry: verified.** Direct seal rejects before contract construction
  (`src/sysml_codegen/contracts/seal.py:93`); canonical verification preflights before seal loading
  (`src/sysml_codegen/contracts/verify.py:332`); the CLI guards before output mutation, Step 9
  integrity writes, and re-seal contract checks (`src/sysml_codegen/cli/__init__.py:625`,
  `src/sysml_codegen/cli/__init__.py:724`, `src/sysml_codegen/cli/__init__.py:917`).
- **SC-2 — kept case matrix and diagnostics: verified.** Root, descendant, contract, excluded,
  regular-file/directory, file/directory-link, and internal/escaping/dangling cases produce sole
  `INVALID_PATH` results with `"."` or canonical relative POSIX paths and the exact common message
  (`tests/unit/test_contract_models.py:126`, `tests/unit/test_verify_package.py:213`,
  `.project/active/constraint-wave-seal-symmetry/evidence/test_constraint_wave_seal_symmetry_overlay.py:158`).
- **SC-3 — unchanged seal verifies: verified.** Seal and verifier use AST-identical root-first,
  fully materialized, lexically sorted inspectors; seal hashes from the inspected entries and the
  verifier reuses them for extras (`src/sysml_codegen/contracts/seal.py:36`,
  `src/sysml_codegen/contracts/verify.py:57`, `tests/unit/test_contract_models.py:263`).
- **SC-4 — regular-tree and fingerprint consequences: verified.** Same-version generation,
  direct seal, and re-seal remain deterministic. The reviewed/candidate comparison preserves every
  non-verifier artifact hash, changes only `contracts/verify.py` from `24eb3565…0276` to
  `ad0a855a…7284`, and changes the derived executable fingerprint from `493a9caa…aa6e` to
  `ccc5efc1…ba3a` (`tests/conformance/test_fingerprint_stability.py:44`,
  `tests/conformance/test_fingerprint_stability.py:100`).
- **SC-5 — standalone/emitted verifier: verified.** The canonical verifier imports only the
  standard library, Step 9 copies it verbatim, and its recorded artifact hash matches the exact
  canonical bytes (`src/sysml_codegen/cli/__init__.py:651`,
  `tests/unit/test_verify_package.py:400`, `tests/conformance/test_seal_step9.py:49`).
- **Requirements and non-goals: met.** Root and descendant classification precedes target use;
  excluded and contract paths cannot evade it; root/walk/link/integrity/extra/runtime precedence is
  deterministic; no link target is resolved, opened, traversed, or hashed; failures return no
  partial `PackageContract` or replacement seal; coverage semantics and schema/layout remain
  unchanged; no external F1 or PR operation was absorbed.

### Design conformance

Implementation follows revised D1–D7 and INV-1–INV-8. `PackageSealError` is limited to policy
failure, the verifier normalizes preflight `OSError` to one `ARTIFACT_UNREADABLE`, the duplicated
inspector is mechanical and AST-pinned, recorded findings precede extras in sorted order, and CLI
routes reuse the seal-side guard without adding a verifier dependency. No historical review finding
remains in the revised design or implementation.

### Code integrity

No issues found. The new inspector and guard each have one readable responsibility; policy stays at
the seal/verifier boundary; no broad fallback, optional-data shim, implicit mode, placeholder, or
load-bearing assertion was added. The existing broad `run_codegen` exception boundary predates and
is outside this item; Item 6's policy and filesystem failures are handled explicitly before it.

---

## Certification

- Reproduced reviewed-state overlay result: 6 passed, 23 defect-specific failures.
- Re-ran candidate focused tests: 76 passed, 2 license-gated skips, normally and under
  `PYTHONOPTIMIZE=1`.
- Re-ran candidate frozen overlay: 29 passed normally and optimized.
- Re-ran broader package gate: 84 passed, 3 license-gated skips.
- Ran 22 audit-only probes normally and optimized. They covered target-operation tripwires, root
  no-walk/no-seal-load, late walk failure after a yielded link, deterministic mixed findings,
  generation descendant preflight, Step 9 model/seal/verifier/excluded links, linked-model re-seal
  preservation, and the full emitted root × file/directory × internal/escaping/dangling matrix.
- Re-ran Ruff, format, scoped diff, verifier/overlay SHA-256, fixture diff, and fixture-manifest
  gates. All nine editable Python files are clean; fixture bytes remain at
  `01de9728…3284`; verifier and frozen-overlay hashes are `ad0a855a…7284` and
  `e928cdc6…1fed`.
- All five spec success criteria and all five plan phases remain checked. Parent Item 6 tracking is
  certified from this audit.

**Not checked:** Licensed live-vs-snapshot fingerprint nodes (license unavailable), the full test
suite, and the existing 76-error mypy baseline were not rerun in this independent pass. Their
implementation evidence remains accurately unclaimed or non-green; certification covers the
license-free Item 6 behavior, optimized execution, package gates, static checks, and saved fixture
scope.
