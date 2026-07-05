from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from attr_expr_probe.modules.attrexprprobelibrary.scalecalc import ScaleCalcModule
from attr_expr_probe.modules.attrexprprobelibrary.splitcalc import SplitCalcModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.area import areaModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.cost import costModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.cost_density import cost_densityModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.gross_electric_simple import gross_electric_simpleModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.marked_up_cost import marked_up_costModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.minor_radius import minor_radiusModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.net_length import net_lengthModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.p_alpha import p_alphaModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.p_blanket_thermal import p_blanket_thermalModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.p_neutron import p_neutronModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.perimeter import perimeterModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.q_scientific import q_scientificModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.total_dim import total_dimModule
from attr_expr_probe.modules.attrexprprobedesign.probe_design.volume import volumeModule

from attr_expr_probe.schemas.design_params import DesignParams as DesignParams

from attr_expr_probe.primitives import Float


def create_attr_expr_probe_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            areaModule,            costModule,            cost_densityModule,            gross_electric_simpleModule,            marked_up_costModule,            minor_radiusModule,            net_lengthModule,            p_alphaModule,            p_blanket_thermalModule,            p_neutronModule,            perimeterModule,            q_scientificModule,            total_dimModule,            volumeModule,            ScaleCalcModule,            SplitCalcModule,        ],
        module_type_override={            areaModule: "attrexprprobedesign.probe_design.areaModule",            costModule: "attrexprprobedesign.probe_design.costModule",            cost_densityModule: "attrexprprobedesign.probe_design.cost_densityModule",            gross_electric_simpleModule: "attrexprprobedesign.probe_design.gross_electric_simpleModule",            marked_up_costModule: "attrexprprobedesign.probe_design.marked_up_costModule",            minor_radiusModule: "attrexprprobedesign.probe_design.minor_radiusModule",            net_lengthModule: "attrexprprobedesign.probe_design.net_lengthModule",            p_alphaModule: "attrexprprobedesign.probe_design.p_alphaModule",            p_blanket_thermalModule: "attrexprprobedesign.probe_design.p_blanket_thermalModule",            p_neutronModule: "attrexprprobedesign.probe_design.p_neutronModule",            perimeterModule: "attrexprprobedesign.probe_design.perimeterModule",            q_scientificModule: "attrexprprobedesign.probe_design.q_scientificModule",            total_dimModule: "attrexprprobedesign.probe_design.total_dimModule",            volumeModule: "attrexprprobedesign.probe_design.volumeModule",            ScaleCalcModule: "attrexprprobelibrary.ScaleCalcModule",            SplitCalcModule: "attrexprprobelibrary.SplitCalcModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    DesignParams,    Float,]
