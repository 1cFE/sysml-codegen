package D38Lib {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;

    abstract part def 'Costed Item' {
        attribute total_cost : Real;
    }

    part def 'Cell' :> 'Costed Item' {
        attribute base_cost : Real;
        :>> total_cost = base_cost;
    }

    // Assembly with an aggregation expression that uses the SysML power
    // operator `^`. Per KerML, `a ^ b` is exponentiation. The aggregation
    // walker (hierarchy_resolver) uses OPERATOR_MAP where `^` maps to the
    // Python XOR token, so `^` silently compiles to XOR rather than `**`.
    part def 'Pack' :> 'Costed Item' {
        attribute count : Integer = 4;
        attribute exponent : Real = 2.0;
        part cell : 'Cell'[count];

        // top-level operator of the aggregation is `^`
        :>> total_cost = sum(cell.total_cost) ^ exponent;
    }
}

// Minimal calc def so build_pipeline_context accepts the model (probe-runnability
// gate). Isolated from the 'Pack' aggregation D3-8 exercises.
package D38Probe {
    private import ScalarValues::*;
    calc def NoopCalc {
        in attribute x : Real;
        out attribute result : Real = x;
    }
}
