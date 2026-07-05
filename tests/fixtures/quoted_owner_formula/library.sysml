package QuotedOwnerFormulaLibrary {
    private import ScalarValues::Real;

    // Minimal calc def so the model has at least one calculation definition
    // (a generation precondition). Its usage binds to a plain entry attribute,
    // not the FORMULA attribute, so it stays off the tested wire.
    calc def ScaleCalc {
        in attribute value : Real;
        out attribute result : Real = value * 2.0;
    }
}
