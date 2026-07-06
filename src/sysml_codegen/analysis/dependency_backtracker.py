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

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.analysis.phantom_detector import PhantomDetectionReport, PhantomDetector
from sysml_codegen.core.identifier_types import ScopedAliasKey, ScopedKey, SysMLQN
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import sanitize_qualified_name

if TYPE_CHECKING:
    from agentic_mbse.sysml.types import BindingInfo
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
        entry_point_sources: Maps qualified entry point name -> source value string.
            For non-literal bindings: the binding source path (for design attr matching).
            For literal bindings: str(literal_value) (for default value propagation).
        phantom_report: Report of suspected phantom entry points
        trace_log: Debug trace of resolution steps (for troubleshooting)
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
    # Unified mapping for ALL binding resolutions
    binding_resolutions: dict[str, BindingResolution] = Field(default_factory=dict)
    # Step-4 fall-through entry point QNs: bound bindings that matched no
    # resolution strategy and no design attribute (Item 7 / D4). The V11 collector
    # intersects this with valueless + wired to find genuinely-uncovered inputs.
    fallback_entry_points: set[str] = Field(default_factory=set)

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
        *,
        output_registry: OutputRegistry,
    ):
        """Initialize with all available usages, calc definitions, and design attributes.

        Args:
            all_usages: All CalcUsageData from usage_extractor
            calc_defs: All CalculationDefinitionData from model
            design_attributes: Design attributes by file (for design attr resolution)
            output_registry: OutputRegistry from Step 5.5 (sole resolution path)
        """
        self.all_usages = all_usages
        self.calc_defs = calc_defs
        self._design_attributes = design_attributes or {}
        self._output_registry = output_registry

        # Build lookup tables
        self._calc_def_by_name: dict[str, object] = {c.name: c for c in calc_defs}

        # Sanitized calc-def QNs, for filtering calc-def I/O attributes out of the
        # leaf-unique design-attribute matcher (Bug B / A1; see _is_calc_def_owned).
        # Built lazily on first use.
        self._calc_def_qns: set[str] | None = None

        # Primary index: qualified name (unique, no collisions)
        self._usage_by_qualified: dict[str, CalcUsageData] = {
            u.qualified_name: u for u in all_usages
        }

        # Secondary index: instance name (used by find_required_modules() for target lookup).
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

        # Phantom detector for inline detection
        self._phantom_detector = PhantomDetector(all_usages, calc_defs)

        # Tracking for inline phantom detection
        self._entry_point_context: dict[str, CalcUsageData] = {}
        self._entry_point_sources: dict[str, str] = {}  # qname -> source path or literal value
        self._trace_log: list[str] = []

        # Authoritative mapping from (usage_qn, param) -> entry_point_qn
        # Key format: "{usage_qualified_name}|{param_name}"
        # Unified binding resolutions
        # Key format: "{usage_qualified_name}|{param_name}"
        # Value: BindingResolution describing how binding is wired
        self._binding_resolutions: dict[str, BindingResolution] = {}

        # Step-4 fall-through entry points (Item 7 / D4). Initialized here so
        # direct callers of _resolve_binding_via_registry (unit tests) work
        # without find_required_modules; reset per run in find_required_modules.
        self._fallback_entry_points: set[str] = set()

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
        self._binding_resolutions = {}
        # Step-4 fall-through entry points (bound bindings that matched no
        # resolution strategy and no design attribute). Item 7 / D4: the V11
        # collector reads this to find genuinely-uncovered wired inputs.
        self._fallback_entry_points = set()

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
                if "." in target:
                    instance_name = target.split(".")[0]
                else:
                    instance_name = target
                usage = self._usage_by_name.get(instance_name)

                if not usage:
                    available = list(self._usage_by_name.keys())[:10]
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
            binding_resolutions=self._binding_resolutions,
            fallback_entry_points=self._fallback_entry_points,
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

                self._entry_point_context[entry_point_qn] = usage

                # Carry literal value for entry point classification
                if binding.literal_value is not None:
                    self._entry_point_sources[entry_point_qn] = str(binding.literal_value)

                continue

            if binding.source_path:
                # Sole resolution path via OutputRegistry (typed dispatch)
                resolution = self._resolve_binding_via_registry(binding, usage)
                self._binding_resolutions[mapping_key] = resolution

                if resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT:
                    self._trace_log.append(
                        f"    {param_name} -> MODULE_OUTPUT ({resolution.qualified_name})"
                    )
                    # DFS into producing usage
                    producing_usage = self._find_usage_for_channel(resolution.qualified_name)
                    if producing_usage and producing_usage.qualified_name not in visited:
                        transitive = self._trace_dependencies(producing_usage, visited, path)
                        dependencies.update(transitive)
                else:
                    # ENTRY_POINT
                    self._trace_log.append(
                        f"    {param_name} -> ENTRY_POINT ({resolution.qualified_name})"
                    )
                    self._entry_point_context[resolution.qualified_name] = usage
                    if resolution.source_path:
                        self._entry_point_sources[resolution.qualified_name] = resolution.source_path

            elif binding.binding_type == BindingType.EXPRESSION:
                # EXPRESSION bindings: no dispatch path, treat as entry point
                entry_point_qn = f"{usage.qualified_name}__{param_name}"
                logger.warning(
                    "EXPRESSION binding %s|%s: no dispatch path, treating as entry point",
                    usage.qualified_name, param_name,
                )
                self._binding_resolutions[mapping_key] = BindingResolution(
                    resolution_type=BindingResolutionType.ENTRY_POINT,
                    qualified_name=entry_point_qn,
                    source_path=None,
                    is_transitive=False,
                )
                self._entry_point_context[entry_point_qn] = usage

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

        return dependencies

    def _get_parent_part_for_usage(self, usage: CalcUsageData) -> str | None:
        """Return segments[-2] of usage.qualified_name (the parent part name).

        E.g., "Design__solar_battery_plant__lcoe" -> "solar_battery_plant"
        """
        segments = usage.qualified_name.split("__")
        if len(segments) >= 2:
            return segments[-2]
        return None

    def _consumer_scope_dotted(self, usage: CalcUsageData) -> str:
        """Extract consumer scope from usage QN for ScopedKey construction.

        "Design__solar_battery_plant__lcoe" -> "solar_battery_plant"
        "Design__catf_radial_build__vacuum_gap__volume_calc"
            -> "catf_radial_build.vacuum_gap"
        """
        segments = usage.qualified_name.split("__")
        if len(segments) <= 2:
            return ""
        return ".".join(segments[1:-1])

    def _find_usage_for_channel(self, channel: str) -> CalcUsageData | None:
        """Extract producing CalcUsage from a channel name for DFS traversal.

        Channel format: "Design__part__usage__output" (PQN format).
        Producing usage EQN: everything before the last "__" segment.
        """
        if "__" not in channel:
            return None
        usage_eqn = channel.rsplit("__", 1)[0]
        return self._usage_by_qualified.get(usage_eqn)

    def _resolve_reference_via_registry(
        self,
        source_path: str,
        usage: CalcUsageData,
    ) -> str | None:
        """Secondary REFERENCE resolution via leaf + parent scope.

        For REFERENCE bindings (FeatureReferenceExpression), the source_path
        is often a SysML qualified name (Package::Part::attr) or dotted path.
        Extract the leaf, combine with parent_part from the consuming CalcUsage,
        and look up via scoped_lookup then alias_lookup.
        """
        assert self._output_registry is not None
        # Extract leaf name
        if "::" in source_path:
            leaf = source_path.rsplit("::", 1)[-1]
        elif "." in source_path:
            leaf = source_path.rsplit(".", 1)[-1]
        else:
            leaf = source_path

        # Try immediate parent scope first (segments[-2].leaf)
        parent_part = self._get_parent_part_for_usage(usage)
        if parent_part:
            sk = ScopedKey(f"{parent_part}.{leaf}")
            channel = self._output_registry.scoped_lookup(sk)
            if channel is None:
                channel = self._output_registry.alias_lookup(sk)
            if channel is not None and not self._is_self_reference(channel, usage):
                return channel

        # Try full consumer scope (design_root.....parent.leaf)
        consumer_scope = self._consumer_scope_dotted(usage)
        if consumer_scope and consumer_scope != parent_part:
            sk = ScopedKey(f"{consumer_scope}.{leaf}")
            channel = self._output_registry.scoped_lookup(sk)
            if channel is None:
                channel = self._output_registry.alias_lookup(sk)
            if channel is not None and not self._is_self_reference(channel, usage):
                return channel

        return None

    def _resolve_binding_via_registry(
        self,
        binding: BindingInfo,
        usage: CalcUsageData,
    ) -> BindingResolution:
        """Resolve a binding via the OutputRegistry using type-directed dispatch.

        Dispatch by binding format:

        CHAIN (no "::" in source_path):
          Step 1: scoped_lookup(consumer_scope.source_path)
          Step 1b: scoped_lookup(source_path) — direct (Key_F FORMULA)
          Step 2: alias_lookup(source_path) — cross-scope
          Step 3: design_attribute match -> ENTRY_POINT
          Step 4: fallback -> ENTRY_POINT with warning

        REFERENCE ("::" in source_path):
          Step 1: sysml_qn_lookup(source_path)
          Step 1b: Normalize :: to dotted -> scoped_lookup
          Step 2: leaf + parent scope -> scoped_lookup then alias_lookup
          Step 3: design_attribute match -> ENTRY_POINT
          Step 4: fallback -> ENTRY_POINT with warning
        """
        assert self._output_registry is not None
        source_path = binding.source_path
        param_name = binding.param_name

        if "::" in source_path:
            # --- REFERENCE dispatch ---
            channel = self._resolve_reference_dispatch(source_path, usage)
        else:
            # --- CHAIN dispatch ---
            channel = self._resolve_chain_dispatch(source_path, usage)

        if channel is not None:
            return BindingResolution(
                resolution_type=BindingResolutionType.MODULE_OUTPUT,
                qualified_name=channel,
                source_path=source_path,
                is_transitive=False,
            )

        # Step 3: Design attribute resolution (existing method, unchanged)
        design_attr_qn = self._resolve_to_design_attribute(source_path, usage)
        if design_attr_qn:
            return BindingResolution(
                resolution_type=BindingResolutionType.ENTRY_POINT,
                qualified_name=design_attr_qn,
                source_path=source_path,
                is_transitive=False,
            )

        # Step 4: Fallback entry point. Item 7 / D5: the per-binding line is
        # DEBUG, not WARNING — it fired per binding and was the primary benign
        # noise. The post-assembly reconciliation summary (unwired remainder) and
        # V11 (wired remainder) are now the operator digest for genuine residue.
        logger.debug(
            "Registry unresolved: %s|%s source_path='%s'",
            usage.qualified_name, param_name, source_path,
        )
        fallback_qn = f"{usage.qualified_name}__{param_name}"
        # Record the fall-through so the V11 collector can find genuinely
        # uncovered wired inputs (Item 7 / D4). Only bound bindings that failed
        # every resolution strategy reach here.
        self._fallback_entry_points.add(fallback_qn)
        return BindingResolution(
            resolution_type=BindingResolutionType.ENTRY_POINT,
            qualified_name=fallback_qn,
            source_path=source_path,
            is_transitive=False,
        )

    def _resolve_chain_dispatch(
        self, source_path: str, usage: CalcUsageData
    ) -> str | None:
        """CHAIN dispatch: scoped_lookup then alias_lookup."""
        # Step 1: Consumer-scoped lookup
        consumer_scope = self._consumer_scope_dotted(usage)
        if consumer_scope:
            scoped_key = ScopedKey(f"{consumer_scope}.{source_path}")
            channel = self._output_registry.scoped_lookup(scoped_key)
            if channel is not None and not self._is_self_reference(channel, usage):
                return channel

        # Step 1b: Direct scoped lookup (no consumer scope prefix)
        # Covers Key_F (FORMULA outputs registered as owning_part.attr)
        channel = self._output_registry.scoped_lookup(ScopedKey(source_path))
        if channel is not None and not self._is_self_reference(channel, usage):
            return channel

        # Step 1c: Structured part-def / consumer-scoped alias lookup (Item 10 #1).
        # Split the source_path at the LAST dot into (scope, leaf) and query the
        # structured _scoped_alias namespace. This reaches a part-def EXPOSE (D7,
        # e.g. demo_plant.total_cost) that no flat string key constructs. Ordered
        # after both scoped steps and before the unscoped alias step (INV-A): it
        # only ADDS a hit where the old ladder fell through, never overrides one.
        #
        # D-D (Item 10 b2, REQ-BT-11): try the consumer-scope-prefixed key FIRST,
        # mirroring Step 1's `consumer_scope + '.' + source_path` prepend. A binding
        # like `chamber_b.power` in a two-sibling plant registers as
        # `('twin_plant.chamber_b','power')`; the bare `('chamber_b','power')` misses
        # it and the def-level `power` name first-wins-collides. Prepending the
        # consumer's instance scope disambiguates to the correct sibling channel.
        if "." in source_path:
            prefix, leaf = source_path.rsplit(".", 1)
            channel = None
            if consumer_scope:
                channel = self._output_registry.scoped_alias_lookup(
                    ScopedAliasKey((f"{consumer_scope}.{prefix}", leaf))
                )
            if channel is None:
                channel = self._output_registry.scoped_alias_lookup(
                    ScopedAliasKey((prefix, leaf))
                )
            if channel is not None and not self._is_self_reference(channel, usage):
                return channel

        # Step 2: Cross-scope alias lookup
        channel = self._output_registry.alias_lookup(ScopedKey(source_path))
        if channel is not None and not self._is_self_reference(channel, usage):
            return channel

        return None

    def _resolve_reference_dispatch(
        self, source_path: str, usage: CalcUsageData
    ) -> str | None:
        """REFERENCE dispatch: sysml_qn_lookup, then normalization, then leaf+parent."""
        # Step 1: Direct SysML QN lookup.
        # Site 2 of the FORMULA sysml-QN lockstep flip (Item 7 / INV-1): the
        # registry key is registered per-segment sanitized, so the lookup key
        # must be too, or a quoted-owner REFERENCE never matches.
        channel = self._output_registry.sysml_qn_lookup(
            SysMLQN(sanitize_qualified_name(source_path))
        )
        if channel is not None and not self._is_self_reference(channel, usage):
            return channel

        # Step 2: REFERENCE secondary (leaf + parent scope)
        channel = self._resolve_reference_via_registry(source_path, usage)
        return channel

    def _is_self_reference(self, channel: str, usage: CalcUsageData) -> bool:
        """Check if resolved channel points back to the consuming usage."""
        producing_usage_qn = channel.rsplit("__", 1)[0] if "__" in channel else channel
        if producing_usage_qn == usage.qualified_name:
            logger.debug(
                "Registry self-reference: %s, treating as entry point",
                channel,
            )
            return True
        return False

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

            # Bug B (REQ-BT-10): a design attribute owned by a part *def* extracts
            # with parent_part='' (get_parent_part_name is empty for def owners),
            # so the exact parent_part match above never fires for it. Fall back to
            # a leaf-unique match: gather design-part attributes carrying this leaf
            # name; use it only when exactly one exists (unambiguous target), else
            # refuse (return None -> Step-4, kept loud). Never guesses among
            # ambiguous candidates (INV-2, no cross-wire).
            cands = [
                attr
                for attrs in self._design_attributes.values()
                for attr in attrs
                if attr.name == attr_name
                and not self._is_calc_def_owned(attr.qualified_name)
            ]
            if len(cands) == 1:
                return cands[0].qualified_name

            # 0 or >1 design-part candidates: fall to Step-4, kept loud.
            return None

        # Handle SysML qualified names (contain '::' separator)
        # These come from REFERENCE bindings using expr.referent.qualified_name
        # Convert to Python format and do exact qualified name match
        if "::" in source_path:
            # Bug A (REQ-BT-09) / lockstep site 3: per-segment sanitize so a
            # quoted-owner QN (Lib::'Magnet Part'::attr) matches the design
            # attribute's per-segment-sanitized qualified_name. A bare ::->__ swap
            # keeps the quotes and never matches.
            python_qname = sanitize_qualified_name(source_path)
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

    def _is_calc_def_owned(self, attr_qualified_name: str) -> bool:
        """True when a "design attribute" QN is really a calc-def I/O attribute.

        ``_design_attributes`` is extracted from every AttributeUsage carrying a
        value expression, which includes calc-def ``out attribute y = expr``
        outputs, not just user design-part attributes. The leaf-unique matcher
        (Bug B) must exclude these: matching a dotted calc-output reference by leaf
        name would cross-wire a module-output binding into a DESIGN_ATTRIBUTE entry
        point with a library default (A1 ruling; INV-2). An attribute is
        calc-def-owned when its QN, minus the leaf segment, equals a calc def's
        sanitized qualified name.
        """
        if self._calc_def_qns is None:
            self._calc_def_qns = {
                sanitize_qualified_name(cd.qualified_name)
                for cd in self.calc_defs
                if getattr(cd, "qualified_name", "")
            }
        owner = attr_qualified_name.rsplit("__", 1)[0]
        return owner in self._calc_def_qns

    def _build_dependency_graph(
        self,
        required_usages: list[CalcUsageData],
    ) -> dict[str, list[str]]:
        """Build dependency graph from required usages.

        Uses pre-computed _binding_resolutions from _trace_dependencies()
        to identify MODULE_OUTPUT dependencies between usages.

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

                mapping_key = f"{usage.qualified_name}|{binding.param_name}"
                resolution = self._binding_resolutions.get(mapping_key)
                if (
                    resolution
                    and resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
                ):
                    producing = self._find_usage_for_channel(resolution.qualified_name)
                    if (
                        producing
                        and producing.qualified_name in required_names
                        and producing.qualified_name != usage.qualified_name
                    ):
                        if producing.qualified_name not in deps:
                            deps.append(producing.qualified_name)

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
