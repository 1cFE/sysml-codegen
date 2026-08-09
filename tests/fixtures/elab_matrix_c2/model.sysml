package ElabMatrixC2 {
    private import ScalarValues::*;

    calc def Twice { in attribute x : Real; out attribute y : Real = x * 2.0; }
    calc def Thrice { in attribute x : Real; out attribute y : Real = x * 3.0; }

    part def Host {
        attribute source : Real default 3.0;
        calc first_calc : Twice { in x = source; }
        calc second : Thrice { in x = source; }
    }

    part host : Host { :>> source = 12.7; }
}
