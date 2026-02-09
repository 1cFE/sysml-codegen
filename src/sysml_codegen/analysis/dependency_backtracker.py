"""Dependency backtracking algorithm for code generation.

Given target outputs, finds the minimal required module set and orders them
topologically for execution. Integrates with existing AST tracing and usage
extraction components.

Example:
    >>> backtracker = DependencyBacktracker(usages, calc_defs)
    >>> result = backtracker.find_required_modules(["net_electric.p_net"])
    >>> print(f"Required: {len(result.required_usages)} modules")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

# Import BindingType directly from agentic-mbse (runtime)
from agentic_mbse.sysml.types import BindingType
from pydantic import BaseModel, Field

# UPDATED: Import from sysml_codegen package structure
from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.analysis.phantom_detector import PhantomDetectionReport, PhantomDetector
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability

if TYPE_CHECKING:
    from sysml_codegen.extraction.usage_extractor import CalcUsageData

logger = logging.getLogger(__name__)

class CircularDependencyError(Exception):
    """Raised when circular dependency detected during backtracking."""

    pass


class TargetNotFoundError(Exception):
    """Raised when target output doesn't exist in model."""

    pass


class BacktrackingResult(BaseModel):
    """Result of dependency backtracking operation.

    Pydantic model providing validation at construction time.

    Attributes:
        required_usages: Calc usages in topological order (dependencies first)
        dependency_graph: Maps instance_name -> list of dependency instance_names
        entry_points: Set of qualified parameter names that are true external inputs
        entry_point_sources: Maps param_name -> binding source path for design attr matching
        phantom_report: Report of suspected phantom entry points
        trace_log: Debug trace of resolution steps (for troubleshooting)
        binding_to_entry_point: DEPRECATED - Use binding_resolutions instead.
            Authoritative mapping from (usage_qn, param) -> entry_point_qn.
            Key format: "{usage_qualified_name}|{param_name}" (uses | to avoid conflict with SysML's ::).
            Value: The entry point qualified name to use for this binding.
            Graph builder uses this for lookup instead of constructing identifiers.
            Will be removed after all consumers updated.
        binding_resolutions: Unified mapping for ALL binding resolutions (entry_point OR module_output).
            Key format: "{usage_qualified_name}|{param_name}".
            Value: Complete BindingResolution describing how the binding is wired.
            This is the SINGLE SOURCE OF TRUTH for binding resolution.
    """

    required_usages: list[CalcUsageData]
    dependency_graph: dict[str, list[str]]
    entry_points: set[str]
    entry_point_sources: dict[str, str]
    phantom_report: PhantomDetectionReport
    trace_log: list[str] = Field(default_factory=list)
    # DEPRECATED: Keep for backward compatibility during migration
    binding_to_entry_point: dict[str, str] = Field(default_factory=dict)
    # Unified mapping for ALL binding resolutions
    binding_resolutions: dict[str, BindingResolution] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


_backtracking_result_rebuilt = False


def _ensure_backtracking_result_rebuilt():
    """Rebuild BacktrackingResult model with CalcUsageData type (lazy)."""
    global _backtracking_result_rebuilt
    if not _backtracking_result_rebuilt:
        from sysml_codegen.extraction.usage_extractor import CalcUsageData  # noqa: F401
        BacktrackingResult.model_rebuild()
        _backtracking_result_rebuilt = True


class DependencyBacktracker:
    """Traces dependencies backwards from target outputs to find required modules.

    Uses pre-computed binding information from CalcUsageData (no live AST tracing).
    Implements DFS with cycle detection pattern.

    Example:
        >>> backtracker = DependencyBacktracker(usages, calc_defs)
        >>> result = backtracker.find_required_modules(["net_electric.p_net"])
        >>> print(f"Required: {len(result.required_usages)} modules")
    """

    def __init__(
        self,
        all_usages: list[CalcUsageData],
        calc_defs: list,
        design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
        computed_attributes: list | None = None,
    ):
        """Initialize with all available usages, calc definitions, and design attributes.

        Args:
            all_usages: All CalcUsageData from usage_extractor
            calc_defs: All CalculationDefinitionData from model
            design_attributes: Design attributes by file (for transitive binding resolution)
            computed_attributes: Computed attributes from Step 4.5 (used in Phase 2)
        """
        self.all_usages = all_usages
        self.calc_defs = calc_defs
        self._design_attributes = design_attributes or {}
        self._computed_attributes = computed_attributes or []

        # Build FORMULA computed attribute lookup index for binding resolution.
        # Only FULLY_COMPILABLE FORMULAs are indexed -- MANUAL_REQUIRED won't get
        # synthetic modules in the graph builder, so bindings to them must fall
        # through to normal resolution.
        # Two key patterns per FORMULA attr: "part.attr" (dotted) and "attr" (bare).
        self._computed_attr_index: dict[str, ComputedAttributeData] = {}
        for ca in self._computed_attributes:
            if ca.classification != ComputedAttributeClassification.FORMULA:
                continue
            if ca.compilability != Compilability.FULLY_COMPILABLE:
                continue
            self._computed_attr_index[f"{ca.owning_part_name}.{ca.python_name}"] = ca
            self._computed_attr_index[ca.python_name] = ca

        # Build lookup tables
        self._calc_def_by_name: dict[str, object] = {c.name: c for c in calc_defs}

        # Primary index: qualified name (unique, no collisions)
        self._usage_by_qualified: dict[str, CalcUsageData] = {
            u.qualified_name: u for u in all_usages
        }

        # Secondary index: instance name (for backward compatibility)
        # Only stores first occurrence; logs on collision at DEBUG level.
        # Collisions are expected and benign: SysML allows same instance names in
        # different parent scopes (e.g., pump_load in blanket vs vacuum). All internal
        # processing uses qualified names (EQN) which are globally unique.
        self._usage_by_name: dict[str, CalcUsageData] = {}
        for u in all_usages:
            if u.instance_name not in self._usage_by_name:
                self._usage_by_name[u.instance_name] = u
            else:
                existing = self._usage_by_name[u.instance_name]
                logger.debug(
                    f"Instance name collision: '{u.instance_name}' used by both "
                    f"{existing.calc_def_name} and {u.calc_def_name}"
                )

        # Build output catalog: "instance.output" -> CalcUsageData
        # Uses both qualified keys (unique) and simple keys (for resolution)
        self._output_catalog: dict[str, CalcUsageData] = {}
        for usage in all_usages:
            calc_def = self._calc_def_by_name.get(usage.calc_def_name)
            if calc_def:
                for attr in calc_def.output_attributes:
                    # Primary key: qualified format (unique)
                    qualified_key = f"{usage.qualified_name}__{attr.name}"
                    self._output_catalog[qualified_key] = usage

                    # Secondary key: simple format (for resolution strategies)
                    simple_key = f"{usage.instance_name}.{attr.name}"
                    if simple_key not in self._output_catalog:
                        self._output_catalog[simple_key] = usage
                    # Note: collision on simple_key is expected; qualified_key is authoritative

        # Build design attribute binding index for transitive resolution
        self._design_attr_binding_index: dict[str, str] = {}
        if design_attributes:
            self._build_design_attr_binding_index(design_attributes)

        # Phantom detector for inline detection
        self._phantom_detector = PhantomDetector(all_usages, calc_defs)

        # Tracking for inline phantom detection
        self._entry_point_context: dict[str, CalcUsageData] = {}
        self._entry_point_sources: dict[str, str] = {}  # param_name -> binding source path
        self._trace_log: list[str] = []

        # Authoritative mapping from (usage_qn, param) -> entry_point_qn
        # Key format: "{usage_qualified_name}|{param_name}"
        # DEPRECATED: Use _binding_resolutions instead
        self._binding_to_entry_point: dict[str, str] = {}

        # Unified binding resolutions (replaces _binding_to_entry_point)
        # Key format: "{usage_qualified_name}|{param_name}"
        # Value: BindingResolution describing how binding is wired
        self._binding_resolutions: dict[str, BindingResolution] = {}

    def find_required_modules(
        self,
        target_outputs: list[str],
        include_all: bool = False,
    ) -> BacktrackingResult:
        """Find minimal set of modules needed for target outputs.

        Algorithm:
            1. If include_all: return all usages sorted
            2. For each target: find producing usage, validate exists
            3. Recursively trace dependencies using DFS
            4. Build dependency graph from required set
            5. Topologically sort for execution order
            6. Run phantom detection on entry points

        Args:
            target_outputs: List of "instance.output" strings (e.g., ["net_electric.p_net"])
            include_all: If True, include all usages (--all flag)

        Returns:
            BacktrackingResult with required usages in execution order

        Raises:
            CircularDependencyError: If cycle detected in dependencies
            TargetNotFoundError: If target output doesn't exist
        """
        self._trace_log = []
        self._entry_point_context = {}
        self._entry_point_sources = {}
        self._binding_to_entry_point = {}
        self._binding_resolutions = {}

        # Handle --all flag
        # Use dict keyed by instance_name since CalcUsageData is not hashable
        if include_all:
            self._trace_log.append("Mode: include_all - tracing all usages for entry points")
            required_dict: dict[str, CalcUsageData] = {}

            # Still trace each usage to identify entry points
            # Use shared visited set to avoid duplicate tracing
            visited: set[str] = set()
            for usage in self.all_usages:
                deps = self._trace_dependencies(usage=usage, visited=visited, path=[])
                required_dict.update(deps)
        else:
            required_dict = {}

            for target in target_outputs:
                self._trace_log.append(f"Processing target: {target}")

                # Find usage that produces this target
                usage = self._output_catalog.get(target)
                if not usage:
                    # Try parsing instance.output format
                    if "." in target:
                        instance_name = target.split(".")[0]
                        usage = self._usage_by_name.get(instance_name)

                    if not usage:
                        available = list(self._output_catalog.keys())[:10]
                        raise TargetNotFoundError(
                            f"Target '{target}' not found. Available: {available}..."
                        )

                # Trace dependencies recursively
                deps = self._trace_dependencies(
                    usage=usage,
                    visited=set(),
                    path=[],
                )
                required_dict.update(deps)

        # Build dependency graph from required usages only
        graph = self._build_dependency_graph(list(required_dict.values()))

        # Collect entry points (unbound params + unresolvable bindings)
        # Per ADR-001 Phase 2, use qualified names with __ separator
        entry_points: set[str] = set()
        for usage in required_dict.values():
            # Build qualified names for unbound params
            qualified_unbound = [
                f"{usage.qualified_name}__{param}" for param in usage.unbound_params
            ]
            entry_points.update(qualified_unbound)
        # Also include bindings that couldn't be resolved (tracked during tracing)
        # These are already qualified names from _trace_dependencies
        entry_points.update(self._entry_point_context.keys())

        # Topological sort (graph now uses qualified names as keys)
        sorted_names = self._topological_sort(graph)
        sorted_usages = [
            self._usage_by_qualified[name]
            for name in sorted_names
            if name in self._usage_by_qualified
        ]

        # Run phantom detection
        phantom_report = self._phantom_detector.detect_phantoms(
            entry_points=entry_points,
            usage_context=self._entry_point_context,
        )

        # Ensure Pydantic model is rebuilt with CalcUsageData type
        _ensure_backtracking_result_rebuilt()

        return BacktrackingResult(
            required_usages=sorted_usages,
            dependency_graph=graph,
            entry_points=entry_points - {p.param_name for p in phantom_report.phantoms},
            entry_point_sources=self._entry_point_sources,
            phantom_report=phantom_report,
            trace_log=self._trace_log,
            binding_to_entry_point=self._binding_to_entry_point,  # DEPRECATED
            binding_resolutions=self._binding_resolutions,
        )

    def _trace_dependencies(
        self,
        usage: CalcUsageData,
        visited: set[str],
        path: list[str],
    ) -> dict[str, CalcUsageData]:
        """Recursively find all dependencies for a calc usage.

        Uses DFS pattern:
        - visited: All nodes ever visited (prevents re-processing)
        - path: Current recursion path (for cycle detection)

        Args:
            usage: Current calc usage to trace
            visited: Set of already-visited qualified names
            path: Current trace path for cycle detection

        Returns:
            Dict of qualified_name -> CalcUsageData for all required usages

        Raises:
            CircularDependencyError: If cycle detected
        """
        qualified_name = usage.qualified_name

        # Cycle detection
        if qualified_name in path:
            cycle_start = path.index(qualified_name)
            cycle = path[cycle_start:] + [qualified_name]
            raise CircularDependencyError(
                f"Circular dependency detected: {' -> '.join(cycle)}"
            )

        # Skip if already fully processed
        if qualified_name in visited:
            return {}

        visited.add(qualified_name)
        path = path + [qualified_name]  # Create new list to avoid mutation

        self._trace_log.append(f"  Tracing: {usage.instance_name} ({usage.calc_def_name})")

        # Use dict keyed by qualified_name to prevent instance name collisions
        dependencies: dict[str, CalcUsageData] = {qualified_name: usage}

        # For each binding, find the source usage
        for binding in usage.bindings:
            param_name = binding.param_name
            # Build mapping key with | separator (avoids conflict with SysML's ::)
            mapping_key = f"{usage.qualified_name}|{param_name}"

            if binding.binding_type == BindingType.LITERAL:
                # Case 2: Literal binding -> entry point
                entry_point_qn = f"{usage.qualified_name}__{param_name}"

                # Unified resolution
                self._binding_resolutions[mapping_key] = BindingResolution(
                    resolution_type=BindingResolutionType.ENTRY_POINT,
                    qualified_name=entry_point_qn,
                    source_path=None,
                    is_transitive=False,
                )

                # DEPRECATED: Keep for backward compat
                self._binding_to_entry_point[mapping_key] = entry_point_qn
                self._entry_point_context[entry_point_qn] = usage
                continue

            if binding.source_path:
                # Check computed attribute resolution first (before normal resolution)
                ca = self._computed_attr_index.get(binding.source_path)
                if ca is None and "." in binding.source_path:
                    bare = binding.source_path.split(".")[-1]
                    ca = self._computed_attr_index.get(bare)

                if ca is not None:
                    channel = self._build_computed_attr_channel(ca)
                    self._binding_resolutions[mapping_key] = BindingResolution(
                        resolution_type=BindingResolutionType.MODULE_OUTPUT,
                        qualified_name=channel,
                        source_path=binding.source_path,
                        is_transitive=False,
                    )
                    self._trace_log.append(
                        f"    {param_name} -> COMPUTED_ATTR ({channel})"
                    )
                    continue  # No recursive tracing -- graph builder creates the module

                source_usage = self._resolve_binding_to_usage(binding.source_path)

                if source_usage:
                    # Cases 4-5: Resolved to calc output -> module_output wiring
                    # Determine if transitive (went through design attr)
                    is_transitive = binding.source_path in self._design_attr_binding_index

                    # Build channel name from resolved usage
                    channel_name = self._build_channel_name_for_binding(
                        binding.source_path, source_usage
                    )

                    # Unified resolution for module output wiring
                    self._binding_resolutions[mapping_key] = BindingResolution(
                        resolution_type=BindingResolutionType.MODULE_OUTPUT,
                        qualified_name=channel_name,
                        source_path=binding.source_path,
                        is_transitive=is_transitive,
                    )

                    # NOTE: Do NOT add to binding_to_entry_point - this is module output wiring
                    self._trace_log.append(
                        f"    {param_name} -> {source_usage.instance_name}"
                        + (" (transitive)" if is_transitive else "")
                    )
                    # Recursively trace
                    transitive = self._trace_dependencies(source_usage, visited, path)
                    dependencies.update(transitive)
                else:
                    # Unresolved binding - becomes entry point
                    # Try to resolve to a design attribute for deduplication
                    if binding.source_path:
                        design_attr_qualified = self._resolve_to_design_attribute(
                            binding.source_path, usage
                        )
                        if design_attr_qualified:
                            # Case 3: Use design attribute qualified name for deduplication
                            self._trace_log.append(
                                f"    {param_name} -> ENTRY (design attr: {design_attr_qualified})"
                            )
                            self._entry_point_context[design_attr_qualified] = usage
                            self._entry_point_sources[design_attr_qualified] = binding.source_path

                            # Unified resolution
                            self._binding_resolutions[mapping_key] = BindingResolution(
                                resolution_type=BindingResolutionType.ENTRY_POINT,
                                qualified_name=design_attr_qualified,
                                source_path=binding.source_path,
                                is_transitive=False,
                            )

                            # DEPRECATED: Keep for backward compat
                            self._binding_to_entry_point[mapping_key] = design_attr_qualified
                        else:
                            # Fallback to calc-input qualified name
                            self._trace_log.append(
                                f"    {param_name} -> ENTRY (unresolved: {binding.source_path})"
                            )
                            qualified_param_name = f"{usage.qualified_name}__{param_name}"
                            self._entry_point_context[qualified_param_name] = usage
                            self._entry_point_sources[qualified_param_name] = binding.source_path

                            # Unified resolution
                            self._binding_resolutions[mapping_key] = BindingResolution(
                                resolution_type=BindingResolutionType.ENTRY_POINT,
                                qualified_name=qualified_param_name,
                                source_path=binding.source_path,
                                is_transitive=False,
                            )

                            # DEPRECATED: Keep for backward compat
                            self._binding_to_entry_point[mapping_key] = qualified_param_name
                    else:
                        # No source path - use calc-input qualified name
                        self._trace_log.append(
                            f"    {param_name} -> ENTRY (no source path)"
                        )
                        qualified_param_name = f"{usage.qualified_name}__{param_name}"
                        self._entry_point_context[qualified_param_name] = usage

                        # Unified resolution
                        self._binding_resolutions[mapping_key] = BindingResolution(
                            resolution_type=BindingResolutionType.ENTRY_POINT,
                            qualified_name=qualified_param_name,
                            source_path=None,
                            is_transitive=False,
                        )

                        # DEPRECATED: Keep for backward compat
                        self._binding_to_entry_point[mapping_key] = qualified_param_name

        # Also track unbound params as entry points (Case 1: use qualified name)
        for param in usage.unbound_params:
            qualified_param_name = f"{usage.qualified_name}__{param}"
            self._entry_point_context[qualified_param_name] = usage

            # Add to mapping for graph builder lookup
            mapping_key = f"{usage.qualified_name}|{param}"

            # Unified resolution
            self._binding_resolutions[mapping_key] = BindingResolution(
                resolution_type=BindingResolutionType.ENTRY_POINT,
                qualified_name=qualified_param_name,
                source_path=None,
                is_transitive=False,
            )

            # DEPRECATED: Keep for backward compat
            self._binding_to_entry_point[mapping_key] = qualified_param_name

        return dependencies

    def _build_computed_attr_channel(self, ca: ComputedAttributeData) -> str:
        """Build output channel name for a FORMULA computed attribute's synthetic module."""
        part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
        module_eqn = f"{part_qn_python}__{ca.python_name}"
        return get_channel_name(module_eqn, ca.python_name)

    def _resolve_to_design_attribute(
        self,
        source_path: str,
        usage: CalcUsageData,
    ) -> str | None:
        """Resolve a binding source path to its root design attribute qualified name.

        When a calc input is bound to a design attribute, the binding source_path may be:
        - A bare name: "p_fusion" (for simple references)
        - A dotted path: "catf_heating.delivered_power" (for parent.attribute references)

        This method looks up the corresponding design attribute using file context
        for disambiguation.

        This enables entry point deduplication: multiple calcs binding to the same
        design attribute will share a single entry point with the attribute's qualified name.

        Args:
            source_path: Bare name or dotted path from binding extraction
            usage: The calc usage for file context

        Returns:
            Design attribute qualified name if found, None otherwise
        """
        # Get file context from usage for disambiguation
        usage_file = usage.source_file if hasattr(usage, "source_file") else None

        # Handle dotted paths (parent_part.attribute_name)
        if "." in source_path:
            parts = source_path.split(".")
            parent_part = parts[0]
            attr_name = parts[-1]

            # Look for design attribute matching parent_part and name
            for file_path, attrs in self._design_attributes.items():
                for attr in attrs:
                    if attr.name == attr_name and attr.parent_part == parent_part:
                        return attr.qualified_name

            # No matching design attribute found for dotted path
            return None

        # Handle SysML qualified names (contain '::' separator)
        # These come from REFERENCE bindings using expr.referent.qualified_name
        # Convert to Python format and do exact qualified name match
        if "::" in source_path:
            python_qname = sysml_to_python_qualified_name(source_path)
            for file_path, attrs in self._design_attributes.items():
                for attr in attrs:
                    if attr.qualified_name == python_qname:
                        return attr.qualified_name
            # No exact match found
            return None

        # Handle bare names (attribute name only)
        # Build candidates from design attributes with matching name
        candidates: list[tuple[Path, DesignAttributeData]] = []
        for file_path, attrs in self._design_attributes.items():
            for attr in attrs:
                if attr.name == source_path:
                    candidates.append((file_path, attr))

        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0][1].qualified_name

        # Multiple candidates - prefer same file
        if usage_file:
            for file_path, attr in candidates:
                if file_path == usage_file or str(file_path) == str(usage_file):
                    return attr.qualified_name

        # Fallback: use first candidate with warning
        logger.warning(
            f"Ambiguous design attribute '{source_path}': {len(candidates)} matches found. "
            f"Using {candidates[0][1].qualified_name}"
        )
        return candidates[0][1].qualified_name

    def _build_channel_name_for_binding(
        self,
        binding_source: str,
        resolved_usage: CalcUsageData,
    ) -> str:
        """Build channel name for a binding that resolves to a calc output.

        When a binding goes through a design attribute (EXPOSE pattern),
        we need to trace the chain to find the actual output attribute name.

        IMPORTANT: This method relies on _design_attr_binding_index containing
        fully qualified channel names (with __ separators), not simple
        instance.output format. This is ensured by _build_design_attr_binding_index()
        calling _resolve_target_to_qualified().

        For multi-hop chains (A → B → C), the index lookup for A returns the
        final channel name for C directly, because the index is built with
        recursive resolution.

        Args:
            binding_source: Original binding source (e.g., "plasma_region.minor_radius")
            resolved_usage: The calc usage that produces the output

        Returns:
            Channel name in PQN format (e.g., "...plasma_region__minor_calc__a")

        Raises:
            ValueError: If unable to determine output attribute (fail-fast)
        """
        # Check if this was a transitive resolution through design attr
        if binding_source in self._design_attr_binding_index:
            target = self._design_attr_binding_index[binding_source]

            # If target is already a qualified name (contains __), use it directly
            # This handles multi-hop chains where the index stores final resolution
            if "__" in target:
                return target

            # Otherwise, parse instance.output format
            if "." in target:
                parts = target.split(".")
                output_attr = parts[-1]
                return f"{resolved_usage.qualified_name}__{output_attr}"

        # Direct binding (e.g., "other_calc.output")
        if "." in binding_source:
            parts = binding_source.split(".")
            output_attr = parts[-1]
            return f"{resolved_usage.qualified_name}__{output_attr}"

        # Unable to determine - fail fast with clear error
        raise ValueError(
            f"Unable to determine output attribute for binding '{binding_source}' "
            f"resolved to usage '{resolved_usage.qualified_name}'. "
            f"Expected either a key in _design_attr_binding_index or "
            f"'instance.output' format. This may indicate a bug in the "
            f"backtracker or malformed SysML binding."
        )

    def _resolve_binding_to_usage(
        self,
        binding_source: str,
        visited: set[str] | None = None,
    ) -> CalcUsageData | None:
        """Resolve binding source path to producing calc usage.

        Multi-strategy resolution with transitive design attribute support:
        1. Exact match in output catalog
        2a. Direct instance match (for same-file references)
        4. Transitive design attribute resolution (BEFORE cross-file)
        2b. Cross-file attribute matching (fallback when transitive doesn't apply)
        3. Bare instance name lookup

        Args:
            binding_source: Source path (e.g., "gross_electric.p_electric_gross")
            visited: Set of paths already visited (for cycle detection)

        Returns:
            CalcUsageData if found, None if unresolvable (becomes entry point)
        """
        # Initialize visited set for cycle detection
        if visited is None:
            visited = set()

        # Cycle detection
        if binding_source in visited:
            logger.warning(f"Cycle detected in binding chain: {binding_source}")
            return None
        visited.add(binding_source)

        # Strategy 1: Exact match
        if binding_source in self._output_catalog:
            return self._output_catalog[binding_source]

        # Strategy 2: Parse and match instance
        if "." in binding_source:
            parts = binding_source.split(".")
            instance_name = parts[0]

            # Strategy 2a: Direct instance match
            if instance_name in self._usage_by_name:
                return self._usage_by_name[instance_name]

        # Strategy 4: Transitive design attribute resolution (MOVED UP)
        # This has file context - design attributes reference outputs in same/related files
        # Must run BEFORE cross-file matching to use binding chain instead of attribute name guessing
        if binding_source in self._design_attr_binding_index:
            target = self._design_attr_binding_index[binding_source]
            logger.debug(f"Transitive resolution: {binding_source} -> {target}")
            # Recurse to resolve the target (may be another design attr or calc output)
            return self._resolve_binding_to_usage(target, visited)

        # Strategy 2b: Cross-file attribute matching (MOVED DOWN - fallback only)
        # Only used when transitive resolution doesn't apply
        if "." in binding_source:
            parts = binding_source.split(".")
            attr_name = parts[-1]
            matches = [
                (key, usage)
                for key, usage in self._output_catalog.items()
                if key.endswith(f".{attr_name}")
            ]
            if len(matches) > 1:
                match_keys = [k for k, _ in matches]
                logger.warning(
                    f"Ambiguous cross-file binding '{binding_source}': "
                    f"multiple outputs match '.{attr_name}': {match_keys}. "
                    f"Using first match: {matches[0][0]}"
                )
            if matches:
                return matches[0][1]

        # Strategy 3: Bare instance name
        if binding_source in self._usage_by_name:
            return self._usage_by_name[binding_source]

        return None  # Unresolvable - will become entry point

    def _build_design_attr_binding_index(
        self,
        design_attributes: dict[Path, list[DesignAttributeData]],
    ) -> None:
        """Build index of design attribute bindings for transitive resolution.

        Extracts path bindings from design attributes. When an attribute's
        default_value is a path reference (e.g., "cryo_load.cooling_power"),
        it's a binding to another source - either a calc output or another
        design attribute.

        Args:
            design_attributes: Dict mapping source file to list of DesignAttributeData
        """
        for file_path, attrs in design_attributes.items():
            for attr in attrs:
                if not attr.default_value:
                    continue

                # Check if default_value is a path reference (not a literal)
                if not self._is_path_reference(attr.default_value):
                    continue

                # Build the key: parent_part.attr_name
                # e.g., "catf_tf_system.cooling_power"
                key = f"{attr.parent_part}.{attr.name}"
                target = attr.default_value  # e.g., "pump_load.pump_power"

                # Resolve target to qualified key using file context
                # This ensures that "pump_load.pump_power" in vacuum.sysml resolves
                # to VacuumPumpPower, not CoolantPumpPower from blanket.sysml
                qualified_target = self._resolve_target_to_qualified(target, file_path)

                # Use qualified target if found, otherwise fall back to simple target
                self._design_attr_binding_index[key] = qualified_target or target

                logger.debug(f"Design attr binding: {key} -> {qualified_target or target}")

    def _is_path_reference(self, value: str) -> bool:
        """Check if a default value is a path reference vs a literal.

        Path references contain '.' and cannot be parsed as numeric/boolean.
        Examples:
            "2600.0" -> False (literal float)
            "cryo_load.cooling_power" -> True (path reference)
            "true" -> False (literal boolean)
        """
        if not value or "." not in value:
            return False

        # Try to parse as float - if it works, it's a literal
        try:
            float(value)
            return False
        except ValueError:
            pass

        # Check for boolean literals
        if value.lower() in ("true", "false"):
            return False

        # Contains '.' and not a numeric literal - likely a path
        return True

    def _resolve_target_to_qualified(
        self,
        target: str,
        source_file: Path,
    ) -> str | None:
        """Resolve a simple target path to a qualified output key using file context.

        When a design attribute in file_a.sysml references "pump_load.pump_power",
        we should resolve it to the pump_load usage that exists in file_a.sysml,
        not just any pump_load usage.

        Args:
            target: Simple target path (e.g., "pump_load.pump_power")
            source_file: The file where this binding is defined

        Returns:
            Qualified output key (e.g., "CATFMFEVacuum__...pump_load__pump_power")
            or None if no matching usage found in same file
        """
        if "." not in target:
            return None

        parts = target.split(".")
        instance_name = parts[0]  # e.g., "pump_load"
        attr_name = parts[-1]  # e.g., "pump_power"

        # Find usage with this instance_name in the same source file
        for usage in self.all_usages:
            if usage.instance_name == instance_name and usage.source_file == source_file:
                # Build qualified output key
                return f"{usage.qualified_name}__{attr_name}"

        # No match in same file - return None to fall back to simple target
        return None

    def _build_dependency_graph(
        self,
        required_usages: list[CalcUsageData],
    ) -> dict[str, list[str]]:
        """Build dependency graph from required usages.

        Args:
            required_usages: List of required CalcUsageData

        Returns:
            Dict mapping qualified_name -> list of dependency qualified_names
        """
        graph: dict[str, list[str]] = {}
        required_names = {u.qualified_name for u in required_usages}

        for usage in required_usages:
            deps: list[str] = []

            for binding in usage.bindings:
                if binding.binding_type == BindingType.LITERAL:
                    continue

                if binding.source_path:
                    source_usage = self._resolve_binding_to_usage(binding.source_path)
                    if source_usage and source_usage.qualified_name in required_names:
                        if source_usage.qualified_name not in deps:
                            deps.append(source_usage.qualified_name)

            graph[usage.qualified_name] = deps

        return graph

    def _topological_sort(
        self,
        graph: dict[str, list[str]],
    ) -> list[str]:
        """Sort usages in valid execution order using Kahn's algorithm.

        Args:
            graph: Maps instance_name -> list of dependency instance_names

        Returns:
            List of instance names in execution order (dependencies first)

        Raises:
            CircularDependencyError: If graph has cycle
        """
        if not graph:
            return []

        # Calculate in-degrees (number of dependencies each node has)
        in_degree: dict[str, int] = {node: 0 for node in graph}

        for node, deps in graph.items():
            # Count how many of this node's dependencies are in the graph
            in_degree[node] = sum(1 for d in deps if d in graph)

        # Start with nodes having no dependencies (in_degree == 0)
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result: list[str] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            # Decrement in-degree for nodes that depend on current
            for node, deps in graph.items():
                if current in deps and node not in result:
                    in_degree[node] -= 1
                    if in_degree[node] == 0 and node not in queue:
                        queue.append(node)

        if len(result) != len(graph):
            remaining = set(graph.keys()) - set(result)
            raise CircularDependencyError(f"Circular dependency in: {remaining}")

        return result


__all__ = [
    "BacktrackingResult",
    "CircularDependencyError",
    "DependencyBacktracker",
    "TargetNotFoundError",
]
