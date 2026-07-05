package StyleDLibrary {
    private import ScalarValues::Real;

    // Style D: return attribute declared, expression assigned in the body.
    calc def StyleDCalc {
        in x : Real;
        return attribute y : Real;
        y = x * 2;
    }
}
