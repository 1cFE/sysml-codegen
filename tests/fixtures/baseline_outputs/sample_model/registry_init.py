from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from sample_model.modules.testmodels.finalcalc import FinalCalcModule
from sample_model.modules.testmodels.firstcalc import FirstCalcModule
from sample_model.modules.testmodels.multioutputcalc import MultiOutputCalcModule
from sample_model.modules.testmodels.secondcalc import SecondCalcModule
from sample_model.modules.testmodels.simplecalc import SimpleCalcModule




def create_sample_model_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            FinalCalcModule,            FirstCalcModule,            MultiOutputCalcModule,            SecondCalcModule,            SimpleCalcModule,        ],
        module_type_override={            FinalCalcModule: "testmodels.FinalCalcModule",            FirstCalcModule: "testmodels.FirstCalcModule",            MultiOutputCalcModule: "testmodels.MultiOutputCalcModule",            SecondCalcModule: "testmodels.SecondCalcModule",            SimpleCalcModule: "testmodels.SimpleCalcModule",        },
    )


