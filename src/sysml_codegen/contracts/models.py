"""Contract pydantic models (CONSTRAINT-EXEC Item 9 / D6, Component Overview).

``ModelContract`` is the package's semantic identity (graph-only); ``PackageContract`` is
its physical seal (directory content hashes). Both are plain pydantic ``BaseModel``s in the
``resolution/models.py`` style — no methods beyond what pydantic gives for free.
"""

from __future__ import annotations

from pydantic import BaseModel

from sysml_codegen.resolution.models import ConstraintCatalog

EVALUATION_SEMANTICS = "kleene-three-valued"
"""The evaluation-semantics tag recorded on every ``ModelContract`` (concept: "Generated
predicate code evaluates under three-valued (Kleene) semantics")."""


class ContractParameter(BaseModel):
    """One entry-point parameter projected onto the semantic contract.

    Attributes:
        qualified_name: The entry point's qualified name (ADR-001).
        param_group: The JSON input group this parameter belongs to.
        python_type: Python type string.
        default_value: Default value if available.
        entry_type: ``EntryPointType`` value (ADR-001 classification).
    """

    qualified_name: str
    param_group: str
    python_type: str
    default_value: float | None = None
    entry_type: str


class ContractOutput(BaseModel):
    """One module output projected onto the semantic contract.

    Attributes:
        channel_name: Channel name for wiring (e.g. "alphaneutronsplit_p_neutron").
        python_type: Python type string.
        field_name: Field name ("root" for single-output, attr name for multi).
    """

    channel_name: str
    python_type: str
    field_name: str


class ModelContract(BaseModel):
    """The package's semantic identity — a pure function of the ``ComputationGraph``.

    Touches no filesystem and no templates (INV-1): a study reads this to know what it
    may vary, what it may observe, and which constraints exist, without parsing YAML or
    module filenames.

    Attributes:
        parameters: Every entry-point parameter across all groups.
        outputs: Every module output across all modules.
        constraint_catalog: The graph's assembled catalog, embedded by value; ``None``
            on a constraint-free corpus serializes as an explicit ``null`` (D6/INV-7).
        evaluation_semantics: Fixed tag naming the evaluation model generated predicate
            code follows.
        catalog_schema_version: The embedded-catalog schema shape token (Item 8). A consumer
            fails closed on an unaccepted value before reading any catalog field (INV-4). It is
            inside the fingerprinted payload, so a schema bump moves ``semantic_fingerprint``.
        semantic_fingerprint: sha256 of the canonical payload with this field absent
            (INV-2 no-circularity) — set after the rest of the contract is built.
    """

    parameters: list[ContractParameter]
    outputs: list[ContractOutput]
    constraint_catalog: ConstraintCatalog | None
    evaluation_semantics: str
    catalog_schema_version: str
    semantic_fingerprint: str


class CoveragePolicy(BaseModel):
    """The seal's self-describing include/exclude ruleset (D3).

    Attributes:
        exclude_globs: Relative-path glob patterns never covered by the seal (the seal
            file itself, ``__pycache__``, ...).
        runtime_output_globs: Relative-path glob patterns reserved for a runtime's own
            writes into the package tree — excluded from coverage so a study's run
            artifacts never trip an "extra file" diagnostic. Empty until Item 10 wiring
            confirms the real teax loader's write location (P1).
    """

    exclude_globs: list[str]
    runtime_output_globs: list[str]


class GenerationManifest(BaseModel):
    """Per-artifact generation provenance the re-seal gate consults (Item 7, D4/D5).

    A codegen-side record — written by ``generate``, consulted by ``seal`` — that lets re-seal
    refuse to launder a foreign file as codegen-produced. It is a covered (hashed) artifact, so
    its bytes are frozen across re-seals; nothing in it depends on the verifier's bytes (it
    lists ``contracts/verify.py`` as a path, never a hash), so a verifier edit does not perturb
    it. It carries no ``runtime_contract_version`` — the seal (`PackageContract`) owns that.

    Attributes:
        codegen_produced: The enumerated relative paths codegen produced — the covered tree at
            first seal minus ``handwritten_globs`` minus ``runtime_globs`` (Major 4
            completeness construction). Hash-frozen at re-seal (INV-F).
        handwritten_globs: Glob patterns for the human-owned region (``handwritten/**``);
            files here may be added or edited across re-seals.
        runtime_globs: Glob patterns reserved for runtime writes; mirrors the seal's
            ``coverage_policy.runtime_output_globs`` (empty until Item 10).
    """

    codegen_produced: list[str]
    handwritten_globs: list[str]
    runtime_globs: list[str]


class PackageContract(BaseModel):
    """The package's physical seal — content hashes over final artifact bytes (D3).

    Self-describing: it records its own coverage policy and the full enumerated
    coverage set, so any consumer re-verifies with no out-of-band knowledge.

    Attributes:
        package_name: The declared package name (load-by-declared-name, mismatch 8).
        coverage_policy: The recorded policy verification must apply (never a
            hard-coded one — D3).
        artifact_hashes: ``{relative_path: sha256}`` over every covered file.
        executable_fingerprint: sha256 over the sorted ``"path:hash"`` lines.
        generator_version: ``sysml_codegen.__version__`` at seal time.
        runtime_contract_version: The pinned ``RUNTIME_CONTRACT_VERSION`` at seal time.
    """

    package_name: str
    coverage_policy: CoveragePolicy
    artifact_hashes: dict[str, str]
    executable_fingerprint: str
    generator_version: str
    runtime_contract_version: str


__all__ = [
    "EVALUATION_SEMANTICS",
    "ContractParameter",
    "ContractOutput",
    "ModelContract",
    "CoveragePolicy",
    "GenerationManifest",
    "PackageContract",
]
