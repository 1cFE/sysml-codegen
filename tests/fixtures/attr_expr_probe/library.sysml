package AttrExprProbeLibrary {
    private import ScalarValues::Real;

    // Simple 2-input calc for testing "computed attr feeds CalcUsage" pattern
    calc def ScaleCalc {
        in attribute value : Real;
        in attribute factor : Real;
        out attribute result : Real = value * factor;
    }

    // Multi-output calc for testing EXPOSE from multiple outputs
    calc def SplitCalc {
        in attribute total : Real;
        out attribute half : Real = total / 2.0;
        out attribute quarter : Real = total / 4.0;
    }
}
