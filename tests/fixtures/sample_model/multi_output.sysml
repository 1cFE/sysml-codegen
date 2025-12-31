package TestModels {
    public import ScalarValues::*;

    /**
     * Multi-output calculation for testing.
     *
     * Tests extraction of multiple output attributes.
     */
    calc def MultiOutputCalc {
        in attribute x : Real;
        in attribute y : Real;
        out attribute sum : Real = x + y;
        out attribute diff : Real = x - y;
        out attribute product : Real = x * y;
    }
}
