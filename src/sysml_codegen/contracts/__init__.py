"""Contracts and sealing (CONSTRAINT-EXEC Item 9).

Two graph/artifact contracts turn a generated package into one verifiable unit: a
``ModelContract`` (graph-only semantic identity) and a ``PackageContract`` (a content-hash
seal over final artifact bytes), verified on load by the stdlib-only ``verify`` module.
"""

from __future__ import annotations

from sysml_codegen.contracts.manifest import (
    ProvenanceError,
    build_generation_manifest,
    check_reseal_provenance,
)
from sysml_codegen.contracts.model_contract import build_model_contract
from sysml_codegen.contracts.models import (
    EVALUATION_SEMANTICS,
    ContractOutput,
    ContractParameter,
    CoveragePolicy,
    GenerationManifest,
    ModelContract,
    PackageContract,
)
from sysml_codegen.contracts.seal import (
    DEFAULT_COVERAGE_POLICY,
    PackageSealError,
    ensure_package_tree_is_link_free,
    seal_package,
)
from sysml_codegen.contracts.verify import (
    Diagnostic,
    VerificationResult,
    verify_package,
    verify_package_or_raise,
)
from sysml_codegen.contracts.versions import (
    RUNTIME_CONTRACT_VERSION,
    TRUSTED_VERIFIER_SHA256,
    generator_version,
)

__all__ = [
    "EVALUATION_SEMANTICS",
    "RUNTIME_CONTRACT_VERSION",
    "TRUSTED_VERIFIER_SHA256",
    "DEFAULT_COVERAGE_POLICY",
    "ContractOutput",
    "ContractParameter",
    "CoveragePolicy",
    "Diagnostic",
    "GenerationManifest",
    "ModelContract",
    "PackageContract",
    "PackageSealError",
    "ProvenanceError",
    "VerificationResult",
    "build_generation_manifest",
    "build_model_contract",
    "check_reseal_provenance",
    "generator_version",
    "ensure_package_tree_is_link_free",
    "seal_package",
    "verify_package",
    "verify_package_or_raise",
]
