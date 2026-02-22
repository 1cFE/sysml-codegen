package ExpressionBindingLibrary {
    private import ScalarValues::Real;

    calc def CombinedCostCalc {
        in attribute combined_input : Real;
        in attribute tax_rate : Real;

        out attribute total_with_tax : Real = combined_input * (1.0 + tax_rate);
    }

    calc def DeltaCalc {
        in attribute value_a : Real;
        in attribute value_b : Real;

        out attribute delta : Real = value_a - value_b;
    }

    calc def PassthroughCalc {
        in attribute x : Real;

        out attribute result : Real = x;
    }
}
