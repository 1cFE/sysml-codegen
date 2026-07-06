package InvocationBindingLibrary {
    private import ScalarValues::Real;

    calc def PassthroughCalc {
        in attribute x : Real;
        out attribute result : Real = x;
    }
}
