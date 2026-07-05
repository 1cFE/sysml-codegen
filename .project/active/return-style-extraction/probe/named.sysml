package NamedProbe {
    private import ScalarValues::Real;

    calc def NamedReturn {
        in x : Real;
        return y : Real = x * 2;
    }
}
