from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from spike_pkg.modules.s3pathnamed.drivercost import DriverCostModule

from spike_pkg.schemas.s3_path_named_params import S3PathNamedParams as S3PathNamedParams

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
        [            DriverCostModule,        ],
        module_type_override={            DriverCostModule: "s3pathnamed.DriverCostModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    S3PathNamedParams,    Float,]
