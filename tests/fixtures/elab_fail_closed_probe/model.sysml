package ElabFailClosedProbe {
    private import ScalarValues::*;
    private import NumericalFunctions::*;

    calc def Doubler {
        in attribute value : Real;
        return result : Real = value * 2.0;
    }

    part def Probe {
        attribute source : Real = 4.0;

        // Pure references form a typed alias cycle. The exact route must name
        // the cycle and must not turn either member into an unbound value.
        attribute alias_a : Real = alias_b;
        attribute alias_b : Real = alias_a;

        // A general behavior invocation is not neutral expression IR. Only
        // the exact standard sum declaration receives plural aggregation
        // semantics in this phase.
        attribute unsupported_formula : Real = Doubler(value = source);
    }

    part probe : Probe;
}
