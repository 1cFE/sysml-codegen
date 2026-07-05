package StyleDDesign {
    private import ScalarValues::Real;
    private import StyleDLibrary::*;

    part styled_design {
        attribute x : Real = 3.0;

        calc styled_calc : StyleDCalc {
            in x = x;
        }
    }
}
