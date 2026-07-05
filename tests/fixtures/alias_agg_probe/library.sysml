package AliasAggProbeLibrary {
    private import ScalarValues::Real;
    private import NumericalFunctions::sum;

    // Simple CalcDef: computes unit cost from base cost
    calc def 'Unit Cost Calc' {
        in attribute base_cost : Real;
        in attribute markup : Real default := 1.5;

        out attribute unit_cost : Real = base_cost * markup;
    }

    // CalcDef: computes margin from cost basis
    calc def 'Margin Calc' {
        in attribute cost_basis : Real;
        in attribute margin_rate : Real;

        out attribute margin : Real = cost_basis * margin_rate;
    }

    // CalcDef: passthrough for testing alias-based resolution
    calc def 'Report Calc' {
        in attribute cost_input : Real;

        out attribute report_value : Real = cost_input;
    }

    // Abstract base with two cost attributes:
    //   total_cost   — will be redefined as aggregation (sum)
    //   reported_cost — will be redefined as CHAIN alias of total_cost
    abstract part def 'Costed Item' {
        attribute total_cost : Real;
        attribute reported_cost : Real;
    }

    // Leaf part with embedded CalcUsage
    part def 'Widget' :> 'Costed Item' {
        attribute base_cost : Real;

        calc cost_model : 'Unit Cost Calc' {
            in base_cost = base_cost;
        }

        :>> total_cost = cost_model.unit_cost;
    }

    // =============================================
    // Assembly with aggregation + CHAIN alias
    // This is the REQ-HR-07 test case.
    // =============================================
    part def 'Widget Assembly' :> 'Costed Item' {
        part widget : 'Widget' [3];

        // AGGREGATION: sum of child costs
        // Produces AggregationExpressionData with attribute_name="total_cost"
        :>> total_cost = sum(widget.total_cost);

        // CHAIN ALIAS: alias targeting the aggregation attribute
        // hierarchy_resolver.py:550-557 checks:
        //   sibling.redefinition_type == CHAIN
        //   sibling.source_path.endswith(agg.attribute_name)
        //   sibling.attribute_name != agg.attribute_name
        // Expected: agg.aliases = ["reported_cost"]
        :>> reported_cost = total_cost;

        // CalcUsage binding to aggregation output (DIRECT reference)
        calc margin_calc : 'Margin Calc' {
            in cost_basis = total_cost;
            in margin_rate = 0.15;
        }

        // CalcUsage binding through the ALIAS (indirect reference)
        // Tests whether alias registration + resolution works end-to-end
        calc report_calc : 'Report Calc' {
            in cost_input = reported_cost;
        }
    }
}
