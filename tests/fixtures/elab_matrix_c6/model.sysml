package ElabMatrixC6 {
    private import ScalarValues::*;

    calc def Twice { in attribute x : Real; out attribute y : Real = x * 2.0; }
    calc def Thrice { in attribute x : Real; out attribute y : Real = x * 3.0; }
    part def Source { attribute value : Real default 3.0; }

    part def Host {
        part source : Source { :>> value = 12.7; }
        calc first_calc : Twice { in x = source.value; }
        calc second : Thrice { in x = source.value; }
    }

    part host : Host;
}
