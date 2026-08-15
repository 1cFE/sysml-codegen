from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from spike_pkg.modules.s4aqualoneocc.revenue import RevenueModule

from spike_pkg.schemas.s4_a_qual_one_occ_params import S4AQualOneOccParams as S4AQualOneOccParams

from spike_pkg.primitives import Float


def create_spike_pkg_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            RevenueModule,        ],
        module_type_override={            RevenueModule: "s4aqualoneocc.RevenueModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    S4AQualOneOccParams,    Float,]
