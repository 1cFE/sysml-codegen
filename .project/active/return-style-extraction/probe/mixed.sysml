package MixedProbe {
    private import ScalarValues::Real;

    // Probe 1b: does an anonymous return alongside a named out attribute parse?
    calc def MixedAnon {
        in x : Real;
        return : Real = x * 2;
        out attribute z : Real = x * 3;
    }
}
