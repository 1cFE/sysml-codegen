package calcdef_gate_probe {
    private import ScalarValues::*;

    calc def Sizer {
        in attribute explicit_load : Real;
        in attribute default_factor : Real = 3.0;
        out attribute size : Real = explicit_load * default_factor;

        assert constraint positive_inputs {
            explicit_load > 0.0 and default_factor > 0.0
        }
    }
}
