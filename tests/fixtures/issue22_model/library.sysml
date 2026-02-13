package Issue22Library {
    private import ScalarValues::Real;
    private import NumericalFunctions::sum;

    // Simple abstract base (mirrors Costed Component)
    abstract part def CostBearer {
        attribute total_cost : Real;
    }

    // Simple CalcDef: computes widget cost from base_cost
    calc def WidgetCostCalc {
        in attribute base_cost : Real;
        in attribute markup_factor : Real default := 1.75;

        out attribute cost : Real = base_cost * markup_factor;
    }

    // Simple CalcDef: computes margin from component total + rate
    calc def MarginCalc {
        in attribute component_total : Real;
        in attribute margin_rate : Real;

        out attribute margin : Real = component_total * margin_rate;
    }

    // Leaf part: Widget with embedded cost model
    part def Widget :> CostBearer {
        attribute base_cost : Real;

        calc cost_model : WidgetCostCalc {
            in base_cost = base_cost;
        }

        :>> total_cost = cost_model.cost;
    }

    // Assembly part: THE ISSUE 22 PATTERN
    // CalcUsage (margin_calc) references sibling :>> EXPRESSION aggregation (total_cost)
    part def WidgetAssembly :> CostBearer {
        part widget : Widget [3];

        // THE EXPRESSION: aggregation via sum()
        :>> total_cost = sum(widget.total_cost);

        // THE REFERENCE: CalcUsage with binding to aggregation attribute
        calc margin_calc : MarginCalc {
            in component_total = total_cost;
            in margin_rate = 0.15;
        }
    }
}
