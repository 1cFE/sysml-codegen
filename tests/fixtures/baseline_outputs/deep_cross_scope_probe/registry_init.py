from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from deep_cross_scope_probe.modules.deepcrossscopeconsumer.analysis_calc import Analysis_CalcModule
from deep_cross_scope_probe.modules.deepcrossscopeproducer.core_metric import Core_MetricModule
from deep_cross_scope_probe.modules.deepcrossscopeproducer.derived_metric import Derived_MetricModule

from deep_cross_scope_probe.schemas.design_params import DesignParams as DesignParams
from deep_cross_scope_probe.schemas.library_params import LibraryParams as LibraryParams
from deep_cross_scope_probe.schemas.system_design import SystemDesign as SystemDesign

from deep_cross_scope_probe.primitives import Float


def create_deep_cross_scope_probe_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            Analysis_CalcModule,            Core_MetricModule,            Derived_MetricModule,        ],
        module_type_override={            Analysis_CalcModule: "deepcrossscopeconsumer.Analysis_CalcModule",            Core_MetricModule: "deepcrossscopeproducer.Core_MetricModule",            Derived_MetricModule: "deepcrossscopeproducer.Derived_MetricModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    DesignParams,    LibraryParams,    SystemDesign,    Float,]
