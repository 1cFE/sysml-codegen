package zero_library {
    private import ScalarValues::*;

    calc def 'Constant Calc' {
        doc /* Zero-entry probe: a calc with no `in` parameters, only a
        constant output. Produces no entry-point parameters, hence zero
        parameter groups / zero entry channels. */
        out attribute value : Real = 2.0 * 3.0;
    }
}
