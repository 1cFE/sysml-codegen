package ElabMatrixC23 {
    private import ScalarValues::*;

    calc def Defaulted {
        in attribute x : Real default 3.0;
        out attribute y : Real = x;
    }

    part host {
        calc first_calc : Defaulted;
        calc second : Defaulted;
    }
}
