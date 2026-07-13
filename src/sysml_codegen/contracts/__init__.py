"""Contracts and sealing (CONSTRAINT-EXEC Item 9).

Two graph/artifact contracts turn a generated package into one verifiable unit: a
``ModelContract`` (graph-only semantic identity) and a ``PackageContract`` (a content-hash
seal over final artifact bytes), verified on load by the stdlib-only ``verify`` module.
"""

from __future__ import annotations

from sysml_codegen.contracts.model_contract import build_model_contract
from sysml_codegen.contracts.models import (
    EVALUATION_SEMANTICS,
    ContractOutput,
    ContractParameter,
    CoveragePolicy,
    ModelContract,
    PackageContract,
)
from sysml_codegen.contracts.seal import DEFAULT_COVERAGE_POLICY, seal_package
from sysml_codegen.contracts.versions import RUNTIME_CONTRACT_VERSION, generator_version

__all__ = [
    "EVALUATION_SEMANTICS",
    "RUNTIME_CONTRACT_VERSION",
    "DEFAULT_COVERAGE_POLICY",
    "ContractOutput",
    "ContractParameter",
    "CoveragePolicy",
    "ModelContract",
    "PackageContract",
    "build_model_contract",
    "generator_version",
    "seal_package",
]
