package InvocationBindingLibrary {
    private import ScalarValues::Real;

    calc def PassthroughCalc {
        in attribute x : Real;
        out attribute result : Real = x;
    }

    // Invoked as an InvocationExpression binding RHS in the design.
    calc def Doubler {
        in attribute v : Real;
        return dbl : Real = v * 2;
    }
}
