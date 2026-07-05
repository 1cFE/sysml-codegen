"""Core data models shared across layers.

These types are used by multiple layers (analysis, resolution, generation)
and are placed here to avoid layer violations.
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class BindingResolutionType(str, Enum):
    """Classification of how a calc input binding resolves.

    Every calc input binding resolves to exactly one of these outcomes:
    - ENTRY_POINT: The binding becomes a pipeline entry point (cases 1-3 in spec)
      - Case 1: Unbound param with no binding
      - Case 2: Bound to literal value
      - Case 3: Bound to design attr with literal value
    - MODULE_OUTPUT: The binding wires to an upstream calc output (cases 4-5 in spec)
      - Case 4: Direct binding to instance.output
      - Case 5: Transitive binding via design attr that EXPOSEs calc output

    See ADR-003 and binding-resolution-fix spec for full taxonomy.
    """

    ENTRY_POINT = "entry_point"
    MODULE_OUTPUT = "module_output"


class BindingResolution(BaseModel):
    """Resolution of a calc input binding.

    Every calc input binding resolves to exactly one BindingResolution.
    This is the SINGLE SOURCE OF TRUTH for how inputs are wired.

    Attributes:
        resolution_type: Either entry_point or module_output
        qualified_name: The target identifier
            - For entry_point: the entry point qualified name (EQN or PQN)
            - For module_output: the channel name (PQN of upstream output)
        source_path: Original binding source path (for debugging)
        is_transitive: True if resolved through at least one design attribute
            EXPOSE pattern. For multi-hop chains (A → B → C), this is True
            if ANY hop went through a design attribute.

    Example (entry_point):
        BindingResolution(
            resolution_type=BindingResolutionType.ENTRY_POINT,
            qualified_name="CATFMFEHeating__catf_heating__delivered_power",
            source_path="catf_heating::delivered_power",
            is_transitive=False,
        )

    Example (module_output via EXPOSE):
        BindingResolution(
            resolution_type=BindingResolutionType.MODULE_OUTPUT,
            qualified_name="CATFMFERadialBuild__catf_radial_build__plasma_region__minor_calc__a",
            source_path="plasma_region.minor_radius",
            is_transitive=True,
        )
    """

    resolution_type: BindingResolutionType
    qualified_name: str
    source_path: str | None = None
    is_transitive: bool = False


class ChannelAlias(BaseModel):
    """An explicit alias for a pipeline output channel.

    Aliases map alternative lookup keys to canonical channel names.
    They are produced by two sources:
    - `:>>` CHAIN redefinitions (source="redefinition")
    - EXPOSE_PURE computed attributes (source="expose_pure")

    All fields use scoped dotted keys -- no bare names, no SYSML_QN (::) format.

    Attributes:
        alias_name: The alias lookup key. For CHAIN aliases, this is scoped
            (e.g., "solar_array.total_capex"). For EXPOSE_PURE aliases, this
            is bare (e.g., "total_capex") -- scoping happens at registration.
        canonical_name: The dotted target key that resolves to a canonical
            channel via the OutputRegistry (e.g., "component_cost.total_cost").
        owning_part_qn: Qualified name of the PartDef/PartUsage where the
            alias originates (e.g., "SolarBatteryLibrary__Solar_Array").
        source: Provenance tag: "redefinition" | "expose_pure" | "design_override".

    Example (CHAIN redefinition):
        ChannelAlias(
            alias_name="solar_battery_plant.solar_array.total_capex",
            canonical_name="solar_battery_plant.solar_array.cost_model.total_cost",
            owning_part_qn="SolarBatteryLibrary__Solar_Array",
            source="redefinition",
        )

    Example (EXPOSE_PURE):
        ChannelAlias(
            alias_name="total_capex",
            canonical_name="component_cost.total_cost",
            owning_part_qn="E2EAttrExprDesign__e2e_plant",
            source="expose_pure",
        )
    """

    alias_name: str
    canonical_name: str
    owning_part_qn: str
    source: Literal["redefinition", "expose_pure", "design_override"]


__all__ = [
    "BindingResolution",
    "BindingResolutionType",
    "ChannelAlias",
]
