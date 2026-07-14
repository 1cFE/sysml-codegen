# Contracts & Sealing

Component: package integrity (CONSTRAINT-EXEC Item 9). A generated package carries
two contracts — a **semantic identity** and a **physical seal** — plus a verifier
emitted alongside them, so a consumer can confirm it is loading exactly the package
sysml-codegen generated, and know what it may vary and observe without parsing YAML.

This is a package-integrity concern, orthogonal to constraint lowering
([28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md)); the two
couple only where `ModelContract` embeds the constraint catalog by value.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-CON-01 | `build_model_contract` SHALL be a pure function of the `ComputationGraph` — no filesystem, no templates (contract INV-1) | `test_contract_models.py` |
| REQ-CON-02 | Both fingerprints SHALL be deterministic; the `semantic_fingerprint` SHALL exclude itself from its own payload (contract INV-2, no circularity) | `test_contract_models.py` |
| REQ-CON-03 | A constraint-free graph SHALL still seal into a well-formed, stable contract (contract INV-7) | `test_contract_models.py` |
| REQ-CON-04 | On-disk `ModelContract` JSON bytes SHALL be a deterministic function of the graph (contract INV-6) | `test_contract_models.py` |
| REQ-CON-05 | The `seal.py` and `verify.py` glob-matcher bodies SHALL stay byte-identical (drift guard) | `test_contract_models.py` |
| REQ-CON-06 | `generate` SHALL emit three files under `contracts/` (`model_contract.json`, `package_contract.json`, `verify.py`) and the result SHALL verify on load | `test_seal_step9.py` |
| REQ-CON-07 | The emitted `contracts/verify.py` SHALL be byte-identical to the canonical in-repo verifier (contract INV-8 drift guard) | `test_seal_step9.py` |
| REQ-CON-08 | The seal SHALL exclude its own `package_contract.json` from coverage | `test_seal_step9.py` |
| REQ-CON-09 | Re-sealing after a stencil edit SHALL recompute only the `PackageContract` (graph-free) | `test_seal_step9.py` |
| REQ-CON-10 | The `seal` subcommand SHALL require an already-sealed package (an existing `ModelContract`) | `test_seal_step9.py` |

> The `contract INV-*` labels above are the contracts machinery's own numbering (in
> `contracts/*.py` and the two test files), a distinct namespace from the design's
> Required Invariants.

---

## Two contracts, two jobs

| Contract | What it is | Pure over | Source |
|----------|-----------|-----------|--------|
| `ModelContract` | The package's **semantic identity** — what a study may vary (`parameters`), observe (`outputs`), and which constraints exist (`constraint_catalog`) | the `ComputationGraph` only | `contracts/models.py`, built by `contracts/model_contract.py` |
| `PackageContract` | The package's **physical seal** — content hashes over the final artifact bytes | the generated directory | `contracts/models.py`, built by `contracts/seal.py` |

A study reads the `ModelContract` to know its degrees of freedom without touching a
single YAML file or module filename (contract INV-1). Verification reads the
`PackageContract` to confirm the bytes on disk are the bytes that were sealed.

## The semantic contract — `build_model_contract` (REQ-CON-01)

`build_model_contract(graph)` (`contracts/model_contract.py`) projects a graph into a
`ModelContract`:

- **`parameters`** — one `ContractParameter` per entry point across every parameter
  group (qualified name, group, python type, default, `entry_type`).
- **`outputs`** — one `ContractOutput` per module output (channel name, python type,
  field name).
- **`constraint_catalog`** — the graph's assembled
  [`ConstraintCatalog`](09-data-models.md#resolution-models), embedded **by value**;
  a constraint-free corpus serializes it as explicit `null` (contract INV-7). The
  catalog is embedded on the contract, the current reality — standalone
  `constraint_catalog.json` emission is the open follow-on CE-F1, not landed.
- **`evaluation_semantics`** — the fixed tag `"kleene-three-valued"`, naming the
  evaluation model generated predicate code follows.
- **`semantic_fingerprint`** — sha256 over the canonical JSON of the payload **with the
  fingerprint field itself absent** (contract INV-2, no circularity).

The projection reads `graph.entry_point_groups`, `graph.modules`, and
`graph.constraint_catalog` and nothing else, so it holds even when the filesystem is
unreachable (`test_model_contract_is_graph_only`).

## The physical seal — `seal_package` (REQ-CON-08, REQ-CON-09)

`seal_package(package_dir, package_name, policy=DEFAULT_COVERAGE_POLICY)`
(`contracts/seal.py`) walks the directory and hashes every **policy-covered** file into
a `PackageContract`:

- **`artifact_hashes`** — `{relative_path: sha256}` over every covered file.
- **`executable_fingerprint`** — sha256 over the sorted `"path:hash"` lines.
- **`coverage_policy`** — the `CoveragePolicy` recorded *in the seal* (never a
  hard-coded one), so a consumer re-verifies with no out-of-band knowledge. The default
  policy excludes `contracts/package_contract.json` (the seal cannot cover itself,
  REQ-CON-08) and `**/__pycache__/**`.
- **`generator_version`** / **`runtime_contract_version`** — `sysml_codegen.__version__`
  and the pinned `RUNTIME_CONTRACT_VERSION` (`contracts/versions.py`) at seal time.

`seal_package` is pure over the directory — it hashes whatever is on disk *now* (stubs
or preserved handwritten code alike), so the identical call re-seals after an edit
(REQ-CON-09).

## Verify-on-load — `verify.py` (REQ-CON-06, REQ-CON-07)

`contracts/verify.py` is the canonical verifier and is emitted **verbatim** into every
generated package (contract INV-8, `test_emitted_verifier_is_verbatim`) so a package
verifies with zero out-of-band knowledge. `verify_package(package_dir, package_name,
runtime_version=None, strict=False)` re-hashes the covered files against the recorded
`artifact_hashes` and returns a `VerificationResult` of `Diagnostic`s:

- **Integrity failures — always fatal:** `TAMPER` (content hash mismatch), `MISSING`
  (recorded file absent), `EXTRA` (an uncovered file present that is not in the seal),
  and a `package_name` mismatch (load-by-declared-name).
- **Environment-compat — advisory unless `strict`:** a `runtime_contract_version`
  mismatch. `GENERATOR_MISMATCH` is reserved for a generator-version mismatch.

`verify_package_or_raise` is the raising wrapper for callers that want a hard failure.
The seal's `seal.py` and the verifier's `verify.py` keep **byte-identical** glob-matcher
bodies, guarded against drift (REQ-CON-05).

## Emission — Step 9 of `generate`

`_seal_package` (`cli/__init__.py:610`, Step 9 of `run_codegen`, D1) runs after all
artifacts are final on disk and writes three files under `contracts/`:

1. `model_contract.json` — `build_model_contract(graph)` serialized.
2. `verify.py` — the canonical verifier copied verbatim.
3. `package_contract.json` — `seal_package(...)` over the now-final tree (which includes
   the first two files but excludes `package_contract.json` itself).

## The `seal` CLI subcommand (REQ-CON-10)

```bash
sysml-codegen seal <package_dir> --package-name <name>
```

Re-seals an already-generated package **in place** — recomputes the `PackageContract`
only, graph-free and license-free (`cmd_seal`, `cli/__init__.py:704`). Use it after
editing a handwritten stencil to make the seal match the edited bytes again. It requires
an existing `ModelContract` (a package already sealed once by `generate`).

## Related Documents

- **Data models**: [09-data-models](09-data-models.md) — `ConstraintCatalog` (embedded
  by value on `ModelContract`)
- **Constraint machinery**: [28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md)
  — the catalog `ModelContract` embeds
- **Generation**: [08-generation](08-generation.md) — the generation seams Step 9 seals
- **Snapshot**: [27-snapshot-generation](27-snapshot-generation.md) — the seal runs the
  same on a from-snapshot generation
