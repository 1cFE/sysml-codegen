"""Phantom entry point detection for dependency backtracking.

Detects parameters incorrectly classified as entry points ("phantoms") using
two strategies:
1. Direct output name match (highest confidence)
2. Binding context check (high confidence)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sysml_codegen.extraction.usage_extractor import CalcUsageData

logger = logging.getLogger(__name__)

__all__ = [
    "DomainKeywords",
    "PhantomCandidate",
    "PhantomDetectionReport",
    "PhantomDetector",
]


@dataclass
class DomainKeywords:
    """Configurable domain-specific keywords for semantic matching.

    This class makes the phantom detector configurable for different domains
    (R12: Configurable DomainKeywords). Provides factory methods for common
    domains like fusion energy.

    Attributes:
        power_keywords: Keywords related to power/energy (e.g., "power", "load")
        efficiency_keywords: Keywords related to efficiency (e.g., "eta", "ratio")
        physics_keywords: Domain-specific physics terms (e.g., "fusion", "neutron")
        custom_keywords: Additional keywords for specific domains
    """

    power_keywords: set[str] = field(default_factory=lambda: {
        "power", "load", "cooling", "heating", "pump", "cryo"
    })
    efficiency_keywords: set[str] = field(default_factory=lambda: {
        "efficiency", "eta", "factor", "ratio"
    })
    physics_keywords: set[str] = field(default_factory=lambda: {
        "fusion", "plasma", "neutron", "alpha", "thermal"
    })
    custom_keywords: set[str] = field(default_factory=set)

    @classmethod
    def for_domain(cls, domain: str) -> DomainKeywords:
        """Factory method to get domain-specific keywords.

        Args:
            domain: Domain name (e.g., "fusion", "aerospace", "automotive")

        Returns:
            DomainKeywords configured for the specified domain
        """
        if domain == "fusion":
            return cls(
                power_keywords={"power", "load", "cooling", "heating", "pump", "cryo", "blanket"},
                efficiency_keywords={"efficiency", "eta", "factor", "ratio", "carnot"},
                physics_keywords={"fusion", "plasma", "neutron", "alpha", "thermal", "tritium", "magnet"},
                custom_keywords={"tokamak", "stellarator", "mfe", "ife", "radial"},
            )
        elif domain == "aerospace":
            return cls(
                power_keywords={"power", "thrust", "propulsion", "fuel"},
                efficiency_keywords={"efficiency", "isp", "factor", "ratio"},
                physics_keywords={"aerodynamic", "drag", "lift", "velocity"},
                custom_keywords={"orbit", "trajectory", "payload"},
            )
        else:
            # Default keywords
            return cls()

    @property
    def all_keywords(self) -> set[str]:
        """Get all keywords combined."""
        return (
            self.power_keywords |
            self.efficiency_keywords |
            self.physics_keywords |
            self.custom_keywords
        )


@dataclass
class PhantomCandidate:
    """A suspected phantom entry point.

    Attributes:
        param_name: Parameter name (e.g., "p_coils")
        usage_name: Usage where it appears as entry point (e.g., "net_electric")
        expected_source: What it should resolve to (if known)
        reason: Why we suspect it's phantom (for debugging)
        confidence: 0.0-1.0 confidence score
    """

    param_name: str
    usage_name: str
    expected_source: str | None
    reason: str
    confidence: float


@dataclass
class PhantomDetectionReport:
    """Report of phantom entry point detection.

    Attributes:
        phantoms: List of suspected phantom entry points
        true_entry_points: Confirmed external inputs (not phantoms)
        total_parameters_checked: Number of parameters analyzed
        detection_rate: Fraction of params flagged as phantoms
    """

    phantoms: list[PhantomCandidate] = field(default_factory=list)
    true_entry_points: set[str] = field(default_factory=set)
    total_parameters_checked: int = 0
    detection_rate: float = 0.0


class PhantomDetector:
    """Detects parameters incorrectly classified as entry points.

    A "phantom entry point" occurs when:
    - Binding resolution failed (couldn't find source usage)
    - But the source actually exists in the model (just wasn't found)

    Detection matches parameters against calc outputs through two strategies:
    1. Direct output match: param name matches an output in the model
    2. Binding context: param had a binding that failed to resolve
    """

    def __init__(
        self,
        all_usages: list[CalcUsageData],
        calc_defs: list,
    ):
        """Initialize with model context.

        Args:
            all_usages: All CalcUsageData from usage_extractor
            calc_defs: All CalculationDefinitionData from model
        """
        self.all_usages = all_usages
        self.calc_defs = calc_defs

        # Build output name catalog for matching
        self._output_names: set[str] = set()
        self._output_to_source: dict[str, str] = {}

        calc_def_map = {c.name: c for c in calc_defs}
        for usage in all_usages:
            calc_def = calc_def_map.get(usage.calc_def_name)
            if calc_def:
                for attr in calc_def.output_attributes:
                    self._output_names.add(attr.name)
                    self._output_to_source[attr.name] = (
                        f"{usage.instance_name}.{attr.name}"
                    )

    def detect_phantoms(
        self,
        entry_points: set[str],
        usage_context: dict[str, CalcUsageData],
    ) -> PhantomDetectionReport:
        """Detect phantom entry points in the given set.

        Args:
            entry_points: Set of parameter names classified as entry points
            usage_context: Maps param_name -> CalcUsageData where it appears

        Returns:
            PhantomDetectionReport with suspected phantoms and true entry points
        """
        phantoms: list[PhantomCandidate] = []
        true_entries: set[str] = set()

        for param_name in entry_points:
            usage = usage_context.get(param_name)
            usage_name = usage.instance_name if usage else "unknown"

            # Strategy 1: Direct output name match (highest confidence)
            if match := self._check_output_match(param_name):
                phantoms.append(
                    PhantomCandidate(
                        param_name=param_name,
                        usage_name=usage_name,
                        expected_source=match,
                        reason="Direct output name match",
                        confidence=0.95,
                    )
                )
                continue

            # Strategy 2: Binding context check (high confidence)
            if usage and (
                binding_source := self._check_binding_context(param_name, usage)
            ):
                phantoms.append(
                    PhantomCandidate(
                        param_name=param_name,
                        usage_name=usage_name,
                        expected_source=binding_source,
                        reason="Had binding but resolution failed",
                        confidence=0.90,
                    )
                )
                continue

            # Not a phantom - true entry point
            true_entries.add(param_name)

        total = len(entry_points)
        return PhantomDetectionReport(
            phantoms=phantoms,
            true_entry_points=true_entries,
            total_parameters_checked=total,
            detection_rate=len(phantoms) / total if total > 0 else 0.0,
        )

    def _check_output_match(self, param_name: str) -> str | None:
        """Check if param name matches any calc output exactly."""
        if param_name in self._output_names:
            return self._output_to_source.get(param_name)

        stripped = param_name
        for prefix in ["p_", "in_", "out_"]:
            if param_name.startswith(prefix):
                stripped = param_name[len(prefix):]
                break

        if stripped in self._output_names:
            return self._output_to_source.get(stripped)

        return None

    def _check_binding_context(
        self,
        param_name: str,
        usage: CalcUsageData,
    ) -> str | None:
        """Check if param had binding that failed to resolve."""
        for binding in usage.bindings:
            if binding.param_name == param_name:
                if binding.source_path and param_name in usage.unbound_params:
                    return binding.source_path
        return None
