package ExpressionBindingDesign {
    private import ScalarValues::Real;
    private import ExpressionBindingLibrary::*;

    part expr_probe {

        // Entry-point attributes (LITERAL sources)
        attribute material_cost : Real = 100.0;
        attribute labor_cost : Real = 50.0;
        attribute overhead : Real = 25.0;
        attribute tax_rate : Real = 0.08;

        // =============================================
        // PATTERN 1: Binary OperatorExpression (two references)
        //   in combined_input = material_cost + labor_cost
        //   Produces BindingType.EXPRESSION (OperatorExpression with + operator)
        // =============================================
        calc cost_calc : CombinedCostCalc {
            in combined_input = material_cost + labor_cost;
            in tax_rate = tax_rate;
        }

        // =============================================
        // PATTERN 2: OperatorExpression with reference and literal
        //   in combined_input = material_cost * 1.2
        //   Produces BindingType.EXPRESSION (OperatorExpression with * operator)
        // =============================================
        calc adjusted_calc : CombinedCostCalc {
            in combined_input = material_cost * 1.2;
            in tax_rate = tax_rate;
        }

        // =============================================
        // PATTERN 3: Multi-term OperatorExpression (3 references)
        //   in combined_input = material_cost + labor_cost + overhead
        //   Produces BindingType.EXPRESSION (nested binary OperatorExpression)
        // =============================================
        calc full_cost_calc : CombinedCostCalc {
            in combined_input = material_cost + labor_cost + overhead;
            in tax_rate = tax_rate;
        }

        // =============================================
        // PATTERN 4: Two EXPRESSION bindings on same CalcUsage
        //   in value_a = material_cost + labor_cost
        //   in value_b = overhead * 2.0
        //   Both produce BindingType.EXPRESSION
        // =============================================
        calc delta_calc : DeltaCalc {
            in value_a = material_cost + labor_cost;
            in value_b = overhead * 2.0;
        }

        // =============================================
        // PATTERN 5: Subtraction OperatorExpression
        //   in x = material_cost - overhead
        //   Produces BindingType.EXPRESSION (OperatorExpression with - operator)
        // =============================================
        calc net_calc : PassthroughCalc {
            in x = material_cost - overhead;
        }
    }
}
