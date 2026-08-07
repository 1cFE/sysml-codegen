from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from spike_pkg.modules.source_identity_mixed_consumers.reading_consumer import Reading_ConsumerModule
from spike_pkg.modules.source_identity_mixed_consumers.source_identity_producer import Source_Identity_ProducerModule

from spike_pkg.schemas.design_params import DesignParams as DesignParams



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
        [            Reading_ConsumerModule,            Source_Identity_ProducerModule,        ],
        module_type_override={            Reading_ConsumerModule: "Reading_ConsumerModule",            Source_Identity_ProducerModule: "Source_Identity_ProducerModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    DesignParams,]
