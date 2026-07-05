package ZeroOutputDesign {
    private import ScalarValues::Real;
    private import ZeroOutputLibrary::*;

    part zero_design {
        attribute x : Real = 1.0;

        calc no_out : NoOutputCalc {
            in x = x;
        }
    }
}
