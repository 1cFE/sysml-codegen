package TestModels {
    public import ScalarValues::*;

    /**
     * Simple calculation for testing extraction.
     *
     * Specification: result = input_a + input_b
     *
     * Tests basic input/output attribute extraction.
     */
    calc def SimpleCalc {
        in attribute input_a : Real;
        in attribute input_b : Real;
        out attribute result : Real = input_a + input_b;
    }
}
