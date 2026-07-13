# Spec: Contracts and Sealing — `ModelContract` / `PackageContract`

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-13
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC, Item 9

---

## Problem

A generated package is currently a loose directory of files. Nothing binds those files
together as one verifiable unit, and nothing lets a downstream consumer confirm the package
it loaded is the package the generator wrote.

Two consequences matter for this epic:

- **No integrity check.** A study runs thousands of design points against one generated
  forward model and records evidence bound to it. If any artifact is edited, replaced, or an
  extra file slips in, the run silently proceeds against a package that no longer matches what
  was generated. There is no seal to catch it.
- **No stable identity the runtime can trust.** The study layer must bind each run to a
  fingerprint so a changed model starts a new lineage and a resumed run refuses a changed
  package. Item 7 gives the graph a *catalog* fingerprint over constraint IDs, but there is no
  *executable* fingerprint over the actual artifact bytes, and no graph-derived *semantic*
  contract the runtime can consume without reaching into module filenames or YAML internals.

The S4 spike proved the shape works: it built a test-only `ModelContract`, a content-hash
seal, and a `verify_seal` pass (`s4_lib.py:903-975`). But that seal was throwaway probe code
with three named gaps — it never declared its coverage set explicitly, never detected a
coverage-set file gone missing (only extra files), and never checked environment
compatibility. This item makes the contracts and the seal production code, and turns those
three gaps into requirements.

## Success Criteria

- [x] **Tamper fails load.** A modified generated *or* preserved (handwritten) artifact fails
  load verification with a named diagnostic identifying the offending file.
  *(Audit 2026-07-13: `test_tamper_fails` — TAMPER names the file, through the load path.)*
- [x] **Stale-file detection.** An unhashed extra file in the package fails load verification
  with a named diagnostic; a coverage-set file that is absent from disk also fails (the
  missing-file half S4 never covered).
  *(Audit: `test_extra_fails` + `test_missing_fails`; both halves closed.)*
- [x] **Environment compatibility.** A package whose recorded generator/runtime version is
  incompatible with the loading environment fails or flags load verification with a named
  diagnostic (fatal-vs-advisory and the version source are design decisions — see Open
  Questions).
  *(Audit: `test_env_compat_advisory_then_strict` — runtime axis, advisory/strict. Note:
  `GENERATOR_MISMATCH` axis reserved-but-unreachable; deferred to Item 10/14 — see audit.md.)*
- [x] **Fingerprint stability.** The `PackageContract` executable fingerprint and the
  `ModelContract` semantic fingerprint each reproduce byte-exactly across independent live
  loads, snapshot generation, and separate sessions (S4 demonstrated this for the executable
  fingerprint — keep it). Contingent on Item 8's byte-identical live/snapshot artifacts.
  *(Audit: offline + `@requires_license` live-vs-snapshot legs; plan records green vs Item 8
  `847bbba`. License-leg re-run requested as a live probe.)*
- [x] **ModelContract is graph-only.** Building the `ModelContract` touches no filesystem and
  no YAML — it is a pure function of `ComputationGraph` fields (test-enforced: no file or
  template read on the `ModelContract` path).
  *(Audit: holds by construction (clean import set); `test_model_contract_is_graph_only` is a
  partial guard — catches `builtins.open` only. See audit.md Finding 3.)*
- [x] **Zero-constraint packages seal.** A package with no admitted constraints still produces
  a well-formed `ModelContract` and `PackageContract` (the contract path never assumes a
  catalog exists).
  *(Audit: `test_zero_constraint_graph_seals` — `null` catalog, stable fingerprint.)*

## Known Requirements

### `ModelContract` (graph-derived)

- **[INHERITED]** *(concept "Contracts and the Evaluator")* `ModelContract` derives solely
  from graph fields: stable parameter IDs, stable output IDs, the constraint catalog, required
  evaluation semantics, and a semantic fingerprint. Force is stated in the brief — "graph
  fields ONLY."
- **[HARD]** The graph fields it reads already exist: `ComputationGraph.entry_point_groups[].parameters`
  (`qualified_name`, `python_type`, `default_value`, `entry_type`), `modules[].outputs`
  (`channel_name`, `python_type`, `field_name`), and `constraint_catalog`
  (`source_records`, `concrete_entries`, `fingerprint`) — see `resolution/models.py:357-407`.
- **[INHERITED]** *(concept)* *Provided* capabilities — available backends, in-memory entry
  support, persistence modes — are **not** graph facts and must be kept out of `ModelContract`.
  They belong to `PackageContract`. (Seam: who populates provided capabilities is a runtime /
  Item-10 concern; this item only reserves their home and enforces the ModelContract
  exclusion.)
- **[INFERRED]** `ModelContract` must be well-formed when `constraint_catalog is None`
  (a package with zero admitted constraints — the `exclude=True` catalog field is `None` in
  that case per `resolution/models.py:407`).

### `PackageContract` seal (verified on load)

- **[INHERITED]** *(concept / epic §2)* The seal is content hashes over the generated **and**
  preserved (handwritten) artifact set, **excluding the seal file itself and runtime outputs**
  (report JSON, study DB, and other run-time-produced files). Force stated.
- **[INHERITED]** *(epic §2 — coverage set gap)* The seal explicitly enumerates the artifacts
  it covers, with an explicit inclusion/exclusion policy. Coverage is declared, not implied by
  "whatever files happen to be present at seal time" (S4's implicit `rglob`).
- **[INHERITED]** *(epic §2 — stale-file gap)* Load verification fails on a file present on
  disk but outside the coverage set (extra/unhashed file), **and** on a coverage-set file
  absent from disk (missing file). S4 caught only the extra-file half.
- **[INHERITED]** *(epic §2 — environment-compatibility gap)* The seal records generator and
  runtime versions, and load verification performs an environment-compatibility check that
  emits a named diagnostic on mismatch.
- **[INHERITED]** *(concept)* Verification happens **on package load**, not only at packaging.
  Force stated ("verified on package load, not just at packaging").
- **[HARD]** Verification must be a capability shipped with / in the generated package and
  callable against a generated package from within sysml-codegen — so the tamper and
  extra/missing-file success criteria are testable in-repo without teax (mirrors S4's
  in-repo `verify_seal`). Study-side wiring of this capability into the teax loader is Item 10.
- **[INHERITED]** *(Item 0 mismatch 8, via epic)* Package loading/verification names the
  package by its **declared package name** (`GenerationConfig.package_name`,
  `cli/__init__.py:69`), not by directory or filename. *Could not independently verify against
  the teax `simkit/evaluation/` loader — see Open Questions.*
- **[INFERRED]** The seal must reflect the **final** artifact state, including filled-in
  handwritten stencils (generation-time stencils are stubs). This forces either a re-seal
  capability or a seal-at-package-time step distinct from initial generation. (Mechanism
  deferred to design.)

### Fingerprint

- **[INHERITED]** *(concept)* **No circularity.** IDs (constraint, parameter, output) never
  depend on any fingerprint. Artifacts contain the IDs; the artifact hashes then form the
  executable fingerprint. The fingerprint *namespaces* IDs — it is never an input to them.
- **[INHERITED]** *(concept / epic §3)* The executable fingerprint (over artifact content
  hashes) is stable across live loads and snapshot generation. This is the fingerprint the
  study layer binds to for lineage and resume. Stability is contingent on Item 8's
  byte-identical live/snapshot artifacts.
- **[HARD]** The catalog fingerprint already exists and is not replaced: assembled once in
  `generation/constraint_catalog.py:103`, carried on `ConstraintCatalog.fingerprint`, and
  embedded into the aggregator as `CATALOG_FINGERPRINT`
  (`templates/report_aggregator.py.jinja2:38`). Item 9 builds the semantic fingerprint
  (ModelContract) and the executable fingerprint (PackageContract) *on top of* the artifacts
  that carry it.

## Non-Goals

- **Study-side contract consumption** (Items 10–11): the teax evaluator/loader wiring,
  `ModelEvidence` projection onto generic response keys, and study fingerprint binding. This
  item owns the seal + verification capability; the runtime consumes it. Note the seam.
- **Signing / cryptographic attestation** beyond content hashes.
- **Headline vocabulary** (Item 0 mismatch 5) — pinned runtime-owned in Item 10.
- **Changing the constraint catalog or its fingerprint** — Item 7 owns that; Item 9 reads it.

## Open Questions / Deferred to design

- **Where sealing runs and how re-sealing works.** A final step of `generate` vs a separate
  `seal` / package command; and how a package is re-sealed after handwritten stencils are
  filled in (stub-state coverage at generation vs final-state coverage at package time).
- **Environment-compatibility mechanism.** Where the compatible runtime version comes from
  (a pinned generator constant, a config flag, or a marker read from the installed runtime),
  and whether the check is a hard load-failure or an advisory. The epic mandates the check
  exists and names a diagnostic; it does not fix its force.
- **Seal file format, location, and canonicalization.** S4 wrote `contracts/model_contract.json`
  + `contracts/package_contract.json` and used sha256 over canonical JSON; likely inherited,
  but the exact layout and hash/canonicalization policy is a design choice.
- **The teax loader verify interface (mismatch 8).** The teax repo
  (`/home/reid/1cfe/teax/simkit/evaluation/`) is outside this session's sandbox, so the real
  loader's verify path could not be read. The load-verification seam here is specified from the
  concept + epic; harden the interface against the actual loader during design / Item 10.
- **Snapshot coordination.** Whether `ModelContract` / `PackageContract` are persisted into the
  snapshot or recomputed on the `generate --from-snapshot` path (coordinate with Item 8, which
  is in flight). The fingerprint-parity criterion assumes the from-snapshot path reproduces the
  same artifacts and therefore the same seal.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 9)
- **Required Reading:** concept `.project/concepts/constraint-execution-and-design-space-studies-claude.md` —
  "Contracts and the Evaluator" (§ line 108-110), Architectural Bets (sealing, line 74), and
  the S4 "Not exercised" contract sentence (line 297) + S4 review carry-forward (4) (line 299).
- **Upstream (certified):** Item 7 — landed catalog + fingerprint
  (`generation/constraint_catalog.py`, `resolution/models.py:357`,
  `templates/report_aggregator.py.jinja2`). S4 test-only seal:
  `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py:903-975` and its
  `findings.md`.
- **Upstream (in flight):** Item 8 — snapshot v3 live/snapshot artifact parity
  (`.project/active/snapshot-v3/spec.md`) — the input for fingerprint stability from snapshot.
- **Downstream seam:** Item 0 findings
  (`/home/reid/1cfe/teax/.project/active/constraint-study-integration-spike/findings.md`,
  inaccessible this session) — mismatches 5 (Item 10) and 8 (Item 9 protocol).
- **Design:** `.project/active/package-contracts/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_spec_review`, then `/_my_design`.
