# Design Review: Seal and Verify Symlink Symmetry

**Design:** `.project/active/constraint-wave-seal-symmetry/design.md`
**Spec:** `.project/active/constraint-wave-seal-symmetry/spec.md`
**Review File:** `.project/active/constraint-wave-seal-symmetry/design-review.md`
**Date:** 2026-07-18
**Reviewer posture:** skeptical; filesystem ordering claims checked against the current implementation and Python 3.12 traversal behavior.

---

## Fundamental Assessment

**Concerns.** The core approach is right: reject links in one deterministic guard before the
existing seal/verify work, duplicate only the small classifier across the standalone-verifier
boundary, and leave the regular-file hashing algorithm alone. This fits the package-contract
architecture and is simpler than changing schemas or coverage semantics.

The design is not ready to implement. Its preflight is not actually first on every route, and its
walker omits the package root itself. Verification loads and parses the seal before preflight, so a
symlink at the root, `contracts/`, or `contracts/package_contract.json` is followed before it can be
rejected. The CLI routes also perform target-following checks or writes before `seal_package`.
These are direct contradictions of the design's no-target-use and earliest-boundary invariants.

There is also a premise conflict in the byte-stability requirement. The canonical verifier must
change to enforce the new policy. Step 9 copies that changed file into the package and includes its
hash in the physical seal. Therefore newly generated packages cannot retain their complete
pre-change `artifact_hashes` and `executable_fingerprint` bytes. The design can preserve the seal
algorithm for an unchanged regular tree, and it can preserve canonical/emitted verifier equality,
but it cannot preserve the old full generated-package fingerprint at the same time.

**Stage 0 result:** proceed with detailed findings and **Revise**, not Rework. The guard-first
architecture remains viable once its scope, call order, root handling, and byte-stability contract
are corrected.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Fail**

- The design promises that every entry is classified before `resolve()`, `is_file()`, `is_dir()`,
  or target access (`design.md:64-71`, `design.md:145-150`). It then places verifier preflight only
  after the seal is loaded and structurally validated (`design.md:168-170`). `_load_seal` opens
  `contracts/package_contract.json` immediately (`src/sysml_codegen/contracts/verify.py:185-201`).
  A symlink at the seal file or an ancestor directory is therefore followed before classification.
- `Path.rglob("*")` exposes directory and dangling links beneath a real root without descending
  into them, so the chosen traversal closes the `os.walk`-style pruning blind spot for descendant
  links. It does not classify `package_dir` itself. On Python 3.12, invoking `rglob` on a symlink
  root traverses the root target. The design has neither a root check nor a diagnostic path for the
  root, so it does not detect all link locations without following targets (`design.md:79-81`,
  `design.md:90-92`, `design.md:123-127`).
- The forbidden-case matrix covers file and directory links, internal/escaping/dangling targets,
  excluded paths, and multiple-link ordering (`design.md:209-239`). It omits the package-root link,
  a symlinked `contracts/` directory, and a symlinked seal file. Those are the cases that expose the
  proposed ordering defect.
- The design correctly puts descendant-link classification before coverage, so excluded and
  runtime-output links do not evade the rule (`design.md:85-89`, `design.md:145-146`). It also
  preserves stable lexical relative-POSIX ordering for links that the walk actually exposes.
- The regular-tree claim is overbroad. Direct `seal_package` output can remain identical for an
  unchanged input tree because the current hash loop and fingerprint formula stay unchanged
  (`src/sysml_codegen/contracts/seal.py:67-86`). Generated-package bytes cannot remain identical to
  the reviewed state because `verify.py` changes, is copied verbatim, and is covered by the new seal
  (`src/sysml_codegen/cli/__init__.py:630-639`; `tests/conformance/test_seal_step9.py:72-82`). The
  tiny-tree control at `design.md:235-237` does not prove the spec's literal generated-package
  claim (`spec.md:34-37`).
- The standalone and emitted-verbatim referents are preserved. The design uses the established
  stdlib-only import scan, canonical/emitted byte comparison, and AST drift-guard pattern rather
  than weakening them (`design.md:51-54`, `design.md:160-161`).
- Capture fidelity needs one correction. The all-links-under-exclusions rule is `[INFERRED]` in the
  spec (`spec.md:44-52`) but is presented as unqualified **Fixed** and non-negotiable in the handoff
  (`design.md:288-296`). The current stage request reinforces testing that boundary, so this does
  not undermine the technical recommendation. It still must remain identified as inferred unless
  the owner originates the decision. No owner-given package-contract referent was dropped or
  softened; the design follows the named architecture and current verifier tests directly.

**Recommendation:** Move verifier classification before any seal read; define root-link handling
and path representation; add ancestor/seal-link cases; and resolve the impossible historical
generated-fingerprint criterion by distinguishing unchanged-input algorithm stability from
canonical/emitted equality after the verifier source changes.

### 2. Pattern Consistency

**Assessment: Concerns**

- Duplicating one small stdlib helper and AST-comparing it matches the existing glob-matcher
  isolation pattern (`tests/unit/test_contract_models.py:161-177`). Copying the canonical verifier
  verbatim also preserves the established emission architecture (`cli/__init__.py:630-632`).
- `PackageSealError` is a small domain error and fits the existing compute-before-write boundary.
  It avoids changing `PackageContract` or every direct caller.
- Route placement is inconsistent with the guard pattern the design describes. `cmd_seal` calls
  target-following `model_contract_path.is_file()` before `seal_package`
  (`src/sysml_codegen/cli/__init__.py:717-727`). Step 9 writes `model_contract.json` and copies
  `verify.py` before calling `seal_package` (`src/sysml_codegen/cli/__init__.py:623-639`). A
  symlinked `contracts/` directory or either output path can therefore be followed or overwritten
  before the guard raises.

**Recommendation:** State the boundary precisely. Either run the same entry preflight at the start
of each CLI integrity route, before target-following checks/writes, or narrow the no-target-use
guarantee to direct `seal_package` and explain why earlier generation mutations are outside scope.
The current document claims the broader guarantee while designing only the narrower one.

### 3. Abstraction Quality

**Assessment: Concerns**

- The classifier earns its existence. One local `str | None` guard is easier to maintain than a
  new shared module that the emitted verifier cannot import.
- Its contract is underspecified for the real routes. A root symlink has no package-relative child
  path, and a recursive walk can raise `OSError`. The design says the helper returns only the first
  path or `None` (`design.md:90-92`) while also promising verifier walk failures remain
  `ARTIFACT_UNREADABLE` (`design.md:198-200`). It does not say where the verifier catches helper
  failures or how root failure is represented without breaking seal/verifier AST parity.

**Recommendation:** Define the helper's exact algorithm and caller boundary. Include a non-following
root `is_symlink()` check, the root diagnostic path convention, sorted descendant enumeration, and
where verifier-side `OSError` becomes one `ARTIFACT_UNREADABLE` result while seal-side errors
propagate.

### 4. Duplication Avoidance

**Assessment: Pass**

The only new production duplication crosses a hard standalone-emission boundary and is guarded by
AST equality plus shared behavior tests. Reusing a project helper would violate the verifier's
stdlib-only contract. No schema, serializer, coverage matcher, or second emitted implementation is
introduced.

### 5. Data Structure Clarity

**Assessment: Concerns**

- `PackageSealError(kind, path, message)` and the matching `Diagnostic` fields make the public data
  flow explicit. Exact string formatting and immediate-return behavior are specified.
- The path domain is incomplete. Every descendant can use canonical package-relative POSIX form,
  but the root cannot. Until the design chooses a root representation, “same path on every route”
  is not implementable for that case.
- The classifier's `str | None` result carries neither walk failure nor the distinction between an
  absent link and an uninspectable tree. Caller-side exception handling can solve this without a
  larger result type, but the design must say so.

**Recommendation:** Specify the root-path value and exception boundary. Keep the public error and
diagnostic shapes otherwise unchanged.

### 6. Route Safety

**Assessment: Fail**

- Canonical and emitted verification follow the seal path before preflight. If the seal is also
  malformed, missing, or unreadable, the design does not define whether seal failure or the
  lexically first link wins. Its overview promises the first link on every route
  (`design.md:14-17`), while its file-level placement makes seal loading win
  (`design.md:168-170`).
- Direct sealing handles descendant links before hashing, but a symlink-valued root is traversed by
  `rglob`. Re-seal also follows the model-contract path before direct sealing. Step 9 can write
  through a symlink under `contracts/` before sealing.
- For a real root and descendant links, the proposed `rglob` guard avoids directory-symlink pruning,
  catches dangling links using `is_symlink()` alone, rejects excluded paths before filtering, and
  provides stable lexical first-path diagnostics. Those parts are sound.
- Compute-before-write preserves the existing `package_contract.json` during a direct re-seal
  failure (`src/sysml_codegen/cli/__init__.py:726-727`). The proposed catch preserves that useful
  boundary. Step 9 likewise calls `seal_package` before writing a replacement seal
  (`src/sysml_codegen/cli/__init__.py:636-639`). Tests should cover a pre-existing seal, not only
  absence of a newly created file.

**Recommendation:** Define one route ordering table that starts before every filesystem access:
root check, descendant preflight, then seal load/model-contract check/writes, then existing
integrity work. Add mixed-failure tests so diagnostic precedence is a contract rather than an
accident.

### 7. Bets & Decisions Integrity

**Assessment: Fail**

- B1 is an honest bet with a clear failure consequence. It accurately keeps concurrent mutation
  outside this item.
- B2 is honest for descendants beneath a real root, and current Python 3.12 behavior supports it.
  It silently assumes the root is a real directory. That assumption is false for an accepted
  `Path`: `rglob` on a symlink root traverses the target.
- A hidden bet says no operation before `_first_forbidden_symlink` can follow a link. Current
  verifier and CLI call order disproves it (`verify.py:185-201`; `cli/__init__.py:623-639,
  717-727`). This hidden bet carries the design's strongest security claim.
- Another hidden bet says changing only guard code leaves generated fingerprint bytes stable. The
  emitted verifier is itself a covered artifact, so that is false even when the seal algorithm is
  unchanged.
- D1-D5 generally name real alternatives and explain why they were rejected. The decisions are
  maintainable once the false placement and byte-stability premises are corrected.

**Recommendation:** Amend B2 to cover a real root only, make root acceptance an explicit decision,
surface pre-guard route operations as a bet or move the guard ahead of them, and split byte
stability into two checkable claims.

### 8. Reader Comprehension

**Assessment: Pass**

The document gives a clear mental model before implementation detail. The two-phase boundary,
route diagram, invariants, failure table, and case matrix are easy to trace. The problem is not
voice; it is that several plain claims conflict with the stated call order. Correcting those claims
and adding the root/seal-path routes will make the document implementation-ready.

---

## Issues by Severity

### Critical

- **C1 — Preflight follows forbidden targets before classifying them.** Verification opens the
  seal before preflight; a root symlink is not enumerated and is traversed; re-seal follows the
  model-contract path first; Step 9 writes under `contracts/` first. This violates the spec's
  earliest-boundary/no-target requirement and design INV-2/INV-3. — Spec Compliance, Route Safety
- **C2 — Historical generated-package fingerprint stability conflicts with verifier enforcement.**
  Changing canonical `verify.py` changes the byte-identical emitted copy, its covered artifact
  hash, and the executable fingerprint. The design's tiny regular-tree control proves algorithm
  stability, not the literal full-generation requirement. — Spec Compliance, Bets & Decisions

### Major

- **M1 — Root and seal-path link cases are absent from the matrix.** The tests cannot catch the
  current design's known traversal blind spots or define a path for a root diagnostic. — Spec
  Compliance, Data Structure Clarity
- **M2 — Mixed-error precedence is undefined.** A malformed/missing/unreadable seal plus a symlink
  yields route-dependent ordering, despite the promise that every route reports only the lexical
  first link. — Route Safety
- **M3 — Walk-error transport is missing from the helper design.** `str | None` plus AST-identical
  bodies can work, but the verifier catch point required to retain `ARTIFACT_UNREADABLE` is not
  specified. — Abstraction Quality

### Minor

- **m1 — An inferred rule is presented as settled.** The spec's all-links-under-exclusions rule is
  `[INFERRED]`, but the design handoff marks it Fixed without preserving that grade. — Spec
  Compliance

---

## Recommendations

1. Put non-following root and descendant classification before `_load_seal`, before `cmd_seal`'s
   model-contract check, and before any Step 9 integrity-file write if the route-level no-target-use
   claim is retained.
2. Define the root diagnostic path and add root, `contracts/`, seal-file, excluded-path, dangling,
   directory-link-pruning, and mixed-error-order cases to both canonical and emitted matrices.
3. Resolve the byte premise explicitly: preserve seal output for an identical regular input tree
   and preserve canonical/emitted equality, while acknowledging the intentional one-time generated
   fingerprint change caused by the covered verifier update. If the spec literally requires old
   generated fingerprints, surface that as unsatisfiable rather than weakening tests.
4. Specify caller-side walk-error handling around the duplicated helper so seal still propagates
   I/O errors and verify still returns `ARTIFACT_UNREADABLE`.
5. Keep the current `PackageSealError`, unchanged hash loop, coverage semantics, stdlib-only
   verifier, AST drift guard, and compute-before-package-contract-write boundary. Those choices fit
   the existing architecture.

---

## Resolutions

No resolutions are recorded in this autonomous review stage. The design agent must incorporate the
findings, and the owner must resolve the generated-fingerprint premise if literal historical byte
stability was intended.

---

**Overall:** Revise

**Next Steps:** Return to `my-design` and point it at this review. Revise the call order, root/path
contract, mixed-error ordering, and byte-stability claim before planning. The reviewer does not edit
the design.
