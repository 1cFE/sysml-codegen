# Spec: Trusted Package Bootstrap and Seal Provenance (Lifecycle Item 7)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic rows:** 8–9

---

## Problem

A generated package is sealed so a consumer can prove the bytes it runs are the bytes
codegen produced. Two holes in that chain let untrusted bytes through today. Both are
reproducible now — one on the live TEAx load path, one on the `seal` subcommand.

**Hole 1 — the package certifies itself.** The seal ships a verifier *inside* the package:
`_seal_package` copies the canonical `src/sysml_codegen/contracts/verify.py` verbatim into
each package as `contracts/verify.py` (`cli/__init__.py:655-657`). The intent (INV-8, B3) is
that a TEAx runtime with no sysml-codegen installed can verify a package using only the
package itself. But nothing authenticates that in-package verifier before it runs. On the
real TEAx load path, `ProvisionalPackageLoader._verify_seal` imports the package's *own*
`contracts/verify.py` (`teax` `package_load.py:38-51`, `exec_module` at :50) and trusts the
`verify_package` result it returns (`package_load.py:74-84`), and only then imports the
package (`load()` at :69-72). So a tampered package that ships an unconditional-success
`verify.py` certifies itself: its verifier's module body executes, returns `ok=True`, and the
malicious package loads. The verifier's byte-identity to the canonical source is checked only
at *generation* time (INV-8 drift guard), never at load. This is the "no untrusted package
code runs before verification" gap, and it is realized, not latent.

**Hole 2 — re-seal launders foreign files.** `seal_package` hashes "whatever is on disk now"
under a coverage policy that excludes only the seal file itself and `__pycache__`
(`seal.py:18-21`, :93-122). The `seal` subcommand (`cli/__init__.py:728-768`) gates only on
"no symlinks" and "a prior `model_contract.json` exists" — it does no provenance
classification. Drop an arbitrary foreign file anywhere in the tree, run `sysml-codegen seal`,
and that file is hashed into `artifact_hashes` as a legitimate covered artifact. A later
`verify_package` passes and TEAx loads it. There is no record of which files codegen produced
versus which a human preserved versus which the runtime writes, so re-seal cannot tell a
stencil edit from an injection.

**Why now.** Item 6 certified the seal→verify symlink/path policy; the trust chain above it is
the next uncertified seam and gates the composed proof (Item 13, register rows 8–9). The
verifier/runtime-contract version is also duplicated as a bare literal `"1.0.0"` across the
repo boundary (`versions.py:11` and `teax` `package_load.py:22`) with only symmetric-equality
skew handling, so the two copies can drift silently in either direction.

**Scope finding (verified, not inherited):** the epic lists Item 7 as sysml-codegen **+ TEAx**.
That listing is correct, not stale. Hole 1 lives on the TEAx loader (`package_load.py`), so a
faithful fix requires a TEAx-side change; sysml-codegen alone cannot close it.

## Success Criteria

Each criterion below is a testable outcome. The two named attacks are RED-first: an acceptance
test must reproduce the exploit against current code before the fix, then go GREEN after.

- [x] **Attack (a) — unconditional-success verifier.** A package whose `contracts/verify.py` is
      replaced with a stub that returns `ok=True` unconditionally is **rejected before any
      package code executes** on the load path. Concretely: the loader must not derive its
      verdict from package-local verifier code, and must not execute package-local code
      (including that verifier's module body) ahead of authenticating it. RED today: the
      tampered package loads via `teax` `package_load.py:70-84`.
- [x] **Attack (b) — foreign-file laundering.** Take a validly generated+sealed package, drop a
      foreign file anywhere outside the excluded globs, run the re-seal path. The re-seal
      **refuses to classify that file as codegen-produced** — it fails, or the file is recorded
      as non-codegen, but it is never admitted as generated provenance. RED today: the file is
      hashed into `artifact_hashes` as a covered artifact via `cli/__init__.py:762`.
- [x] **Version skew fails closed in both directions.** A seal recorded against a
      verifier/runtime-contract version the loader does not accept is rejected — both when the
      package is newer than the runtime and when the runtime is newer than the package — with a
      diagnostic that names the mismatch. No skew silently passes.
- [x] **Item 6 guarantees stay green.** Every certified seal→verify regular-file and symlink
      regression test passes unchanged (`tests/unit/test_verify_package.py`,
      `tests/conformance/test_seal_step9.py`, `test_fingerprint_stability.py`,
      `test_contract_models.py`).
- [x] **One authority, no bypass.** Verification and generation-provenance each have one
      authoritative implementation with no duplicate path that skips it. Duplicated
      verifier/version machinery is consolidated. The seal walker and the verify walker remain
      distinct (see Known Requirements).
- [x] A generation manifest records, per artifact, whether it is codegen-produced,
      preserved-handwritten, or runtime-written, and the re-seal path consults it.

## Known Requirements

- **[INHERITED]** No untrusted package code runs before verification: relocate verification
  trust to runtime-owned code, or authenticate the package-local verifier bytes before they
  execute. An unconditional-success verifier inside a package must be rejected before any
  package code runs. *(Source: ratified lifecycle contract, epic rows 8–9; spec brief §Intent.)*
- **[INHERITED]** Verifier/runtime-contract versions are single-sourced, or an explicit
  fail-closed compatibility table covers both skew directions. *(Source: epic rows 8–9;
  brief §Intent.)*
- **[INHERITED]** A generation manifest distinguishes codegen-produced, preserved-handwritten,
  and runtime artifacts, and a re-seal cannot classify an arbitrary foreign file as
  codegen-produced. *(Source: epic rows 8–9; brief §Intent.)*
- **[HARD]** The certified stdlib-only seal→verify symlink/path policy (Item 6) must not
  regress: its regression tests stay green and its scope is not reopened. Forced by an existing
  certified system. *(`seal.py:36-57`, `verify.py:57-66`; tests named in Success Criteria.)*
- **[HARD]** The in-package verifier must stay stdlib-only — it imports nothing from
  sysml-codegen (`verify.py:1-11`). Forced by B3: a TEAx environment verifies a package with no
  sysml-codegen installed (`teax` `package_load.py:6-8`). This is why the loader cannot simply
  `import sysml_codegen.contracts.verify`, and it constrains how trust is relocated.
- **[HARD]** TEAx must not gain a runtime dependency on sysml-codegen being installed (B3, as
  above). Any runtime-owned verifier must therefore be a TEAx-carried copy or a
  known-good-bytes check, not a cross-repo import. This forecloses import-based single-sourcing
  of the version constant across the repo boundary; the version story must be a compatibility
  table or a vendored-constant-with-drift-check.
- **[NEED]** Qualitative simplicity, no LOC metrics: consolidate duplicated verifier/version
  machinery by deletion of superseded paths, not by adding a guard or shim. *(Owner-stated,
  brief §Intent line 21; epic simplification mandate.)*
- **[NEED]** Do not merge the seal walker and the verify walker. That boundary is a named
  do-not-collapse invariant — the deliberate duplication of `_glob_to_regex` /
  `_inspect_package_tree` between `seal.py` and `verify.py` exists so producer and consumer
  agree without coupling. Consolidation applies to version constants and provenance logic, not
  to this boundary. *(Owner-stated, brief §Intent; epic "do not collapse intentional
  boundaries.")*

## Non-Goals

- A second catalog schema authority (Item 8 / D-3 territory).
- Re-auditing or re-opening the certified Item 6 symlink/path matrix.
- TEAx constraint evidence-durability work (Item 11).
- Wiring `runtime_output_globs` to a real runtime write location — deliberately empty until
  Item 10 confirms the teax loader's write location (`models.py:84-86`). Item 7 defines the
  manifest's *runtime* class conceptually; it does not commit the runtime write path.
- Reviving the dead `GENERATOR_MISMATCH` seam as a load-bearing generator-version axis unless a
  version design specifically calls for it (`verify.py:24-30`).

## Open Questions / Deferred to design

- **Trust-relocation mechanism.** Two faithful shapes satisfy Requirement 1: (i) TEAx carries
  its own canonical verifier and uses *that* to verify, ignoring the package-local copy; or
  (ii) the loader byte-authenticates the package-local `contracts/verify.py` against a
  known-good hash it carries, before executing it. Both must preserve B3 (no sysml-codegen
  import). Which one — and whether the package-local `verify.py` is then still needed, or
  becomes just another hashed artifact — is a design decision.
- **Version story.** Compatibility table vs vendored-constant-with-drift-check, and whether the
  verifier gets a version axis distinct from `runtime_contract_version`. Cross-repo
  single-sourcing is unavailable (see [HARD] B3 above), so the mechanism, not the goal, is open.
- **Manifest home and shape.** Extend `PackageContract`/`CoveragePolicy` with per-artifact
  provenance, or add a separate manifest artifact; per-file classes vs glob classes; how
  preserved-handwritten files are recorded at generation time (`generation/preservation.py`
  decides preservation procedurally today and persists nothing) so re-seal can consult the
  record.
- **Re-seal failure mode for a foreign file.** Hard-fail the re-seal, or admit the file under a
  non-codegen class and let verification treat it accordingly. Either satisfies (b); the choice
  is design.
- **Cross-repo phasing.** sysml-codegen change and TEAx change land in their authorized
  vehicles (agentic-mbse PR #11, sysml-codegen PR #9, and TEAx's own path). The ordering and
  which repo owns the authenticated-verifier contract is a design/phasing decision. TEAx HEAD
  for grounding: `db23719`.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 7, rows 8–9)
- **Stage brief:** `.project/active/constraint-lifecycle-package-trust/briefs/spec.md`
- **Ratified authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- **Seal/verify reference:** `docs/architecture/reference/29-contracts-and-sealing.md`
- **Grounded code (HEAD `c578239`):**
  - Canonical verifier: `src/sysml_codegen/contracts/verify.py`
  - Seal + coverage policy: `src/sysml_codegen/contracts/seal.py`
  - Seal models: `src/sysml_codegen/contracts/models.py`
  - Version constant: `src/sysml_codegen/contracts/versions.py:11`
  - Step-9 seal + verbatim verifier copy: `src/sysml_codegen/cli/__init__.py:628-664`
  - Re-seal subcommand: `src/sysml_codegen/cli/__init__.py:728-768`
  - TEAx load/verify (the vulnerability): `../teax/packages/teax-simkit/simkit/evaluation/package_load.py` (HEAD `db23719`)
- **Design:** `.project/active/constraint-lifecycle-package-trust/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`. Design must resolve the
trust-relocation mechanism, the cross-repo version story, and the manifest shape, then drive
both named attacks RED-first before implementation.
