# Spec: Seal and Verify Symlink Symmetry

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-07-18 19:50 PDT
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 6 (R-10)

---

## Problem

Package sealing and package verification do not enforce the same filesystem boundary. Sealing
currently hashes a file symlink's target, skips directory and dangling symlinks, and can return a
contract for a tree that unchanged verification rejects. Verification now rejects directory
symlinks, but it can still skip a dangling link and report success. The error therefore appears
late at package load, or not at all, instead of at the operation that first accepts the invalid
tree.

This breaks the physical seal's core promise. A successful seal does not prove that the unchanged
package is verifiable, and a link can leave mutable or escaping content outside the enumerated
artifact contract.

## Success Criteria

- [x] Every package tree has the same symlink outcome at both boundaries: seal rejects it before
      producing a new `PackageContract`, and verify rejects it with a fatal diagnostic.
- [x] A kept case matrix covers regular files and directories plus file and directory symlinks
      whose targets are internal, escaping, or dangling. Every forbidden case identifies the
      package-relative link path and the symlink policy violation.
- [x] No successfully sealed package can fail immediate unchanged verification because seal and
      verify classified the same filesystem entry differently.
- [x] For identical symlink-free input bytes, direct seal and re-seal retain the same artifact
      hashes and executable fingerprint. Newly generated packages preserve every non-verifier
      artifact hash; the covered emitted verifier hash and downstream executable fingerprint
      intentionally change once to reflect the canonical verifier policy update. Canonical and
      emitted verifier bytes remain identical.
- [x] The canonical verifier remains standalone and standard-library-only, and its emitted copy
      remains byte-identical and enforces the same policy.

## Known Requirements

- **[NEED]** Sealing and verification enforce one explicit, fail-closed symlink policy across
  regular-file, regular-directory, internal-target, escaping-target, dangling-target, file-link,
  and directory-link cases. Source: stage request.
- **[NEED]** A symlink package root, symlinked `contracts/` directory, and symlinked contract file
  are classified before any route follows, opens, resolves, traverses, or writes through them. The
  root diagnostic path is `"."`; descendant diagnostics use canonical package-relative POSIX
  paths. Source: current owner revision request.
- **[INFERRED]** Every symlink found beneath a real package root is forbidden, including file and
  directory links, internal and escaping targets, dangling links, and links whose paths would
  otherwise be excluded by the recorded coverage policy. GAP-CLOSE F9 already rejects every
  directory symlink regardless of containment, and R-10 establishes file and dangling links as the
  same uncovered mutable-content threat class. Extending that boundary to all links is the narrow
  fail-closed rule; no link target needs to be trusted or traversed. Sources:
  `.project/active/gap-boundary-guards/spec.md`, F9 requirements;
  `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`, R-10; and
  `.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 6.
- **[NEED]** An unsupported link fails at the earliest boundary that encounters it. Seal reports
  the link before returning or writing a replacement package contract. Verify reports it during
  integrity checking instead of skipping it or allowing a later load failure. Source: stage
  request.
- **[INFERRED]** Link diagnostics use the canonical package-relative POSIX path and identify the
  entry as a forbidden symlink. They do not relabel it as `MISSING`, `EXTRA`, or `TAMPER`, and a
  single link does not produce duplicate or target-dependent diagnoses. This preserves the current
  fatal `INVALID_PATH` security surface while making the cause actionable at both boundaries.
  Sources: GAP-CLOSE F9 behavior in `src/sysml_codegen/contracts/verify.py` and Item 6's
  path-specific diagnostic requirement.
- **[NEED]** Root and descendant symlink classification precedes seal loading, contract-path
  checks or writes, coverage filtering, path resolution, and file/directory tests. No symlink
  target is opened, hashed, traversed, or written through, including a target outside the package
  root. This is required for the all-links-forbidden policy to remain fail-closed for root,
  dangling, and mutable targets. Source: current owner revision request.
- **[HARD]** `src/sysml_codegen/contracts/verify.py` remains standard-library-only and imports no
  sysml-codegen, agentic-mbse, or third-party module because the file is shipped inside generated
  packages and must run without the generator environment. Existing contract: package-contract
  design D7/INV-8 and `tests/unit/test_verify_package.py`.
- **[HARD]** The verifier copied into `contracts/verify.py` remains byte-identical to the canonical
  verifier. Generated packages rely on that copy as their verification capability. Existing
  contract: REQ-CON-07 and contract INV-8 in
  `docs/architecture/reference/29-contracts-and-sealing.md`.
- **[INHERITED]** Seal and verify continue to apply the same recorded coverage-policy glob
  semantics, guarded by the existing matcher-body parity check. This item adds a filesystem-entry
  boundary before those semantics; it does not redesign coverage. Source:
  `.project/completed/20260713_package-contracts/design.md`, D3/D7, and REQ-CON-05.
- **[NEED]** For identical trees containing only regular files and directories, direct sealing and
  re-sealing preserve the artifact set, per-file hashes, deterministic ordering, and executable
  fingerprint. New generation preserves those properties for every non-verifier artifact, while
  the covered emitted-verifier hash and derived executable fingerprint change to reflect the
  required canonical-verifier policy update. Canonical and emitted verifier bytes remain
  identical. Source: current owner revision request, correcting the earlier impossible
  whole-generated-package byte-identity wording.
- **[NEED]** The seal-to-verify matrix includes package-root, symlinked-`contracts/`, linked
  seal-file, excluded-path, direct `seal_package`, Step 9, and re-seal coverage plus the verifier's
  canonical and emitted-package routes. Each forbidden case is shown RED on the reviewed state
  where that state exposes the defect, then GREEN after correction; ordinary symlink-free packages
  remain the symmetry control. Source: current owner revision request, extending epic Item 6's
  existing Step 9, re-seal, verifier, and emitted-verifier routes.

## Non-Goals

- Archive-format changes, package-layout changes, coverage-policy schema changes, or a broader
  `PackageContract` redesign.
- Supporting, copying, dereferencing, or fingerprinting symlink targets or link metadata.
- Redesigning runtime-output exclusions, package installation, or external loader behavior.
- Implementing or claiming closure of external `[GAP-CLOSE-F1-TEAX-NORMALIZATION]`.
- Commit, push, PR comment, merge, or any other PR-state change.

## Open Questions / Deferred to design

- Choose the smallest shared classification shape that keeps seal and the stdlib-only verifier
  behaviorally identical without making the emitted verifier import project code. The public
  outcome, ordering, paths, and all-links-forbidden policy are fixed above.
- Choose the seal-side exception or result type and message construction. It must carry the same
  forbidden-symlink classification and canonical relative path as verification without changing
  the `PackageContract` schema.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 6
- **Required Reading:**
  - `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`, R-10 and Verified
    Clean
  - `.project/active/gap-boundary-guards/spec.md`
  - `.project/active/gap-boundary-guards/plan.md`
  - `.project/active/gap-boundary-guards/evidence.md`
  - `docs/architecture/reference/29-contracts-and-sealing.md`
- **Package-contract history:**
  - `.project/completed/20260713_package-contracts/spec.md`
  - `.project/completed/20260713_package-contracts/design.md`
  - `.project/completed/20260713_package-contracts/audit.md`
- **Current implementation and tests:**
  - `src/sysml_codegen/contracts/seal.py`
  - `src/sysml_codegen/contracts/verify.py`
  - `src/sysml_codegen/cli/__init__.py`
  - `tests/unit/test_contract_models.py`
  - `tests/unit/test_verify_package.py`
  - `tests/conformance/test_seal_step9.py`
  - `tests/conformance/test_fingerprint_stability.py`
- **Design:** `.project/active/constraint-wave-seal-symmetry/design.md`
- **Design review:** `.project/active/constraint-wave-seal-symmetry/design-review.md`

---

**Next Steps:** After revised-design approval, proceed to `my-plan`.
