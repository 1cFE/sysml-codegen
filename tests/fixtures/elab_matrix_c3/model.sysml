package ElabMatrixC3 {
    private import ScalarValues::*;

    calc def Twice { in attribute x : Real; out attribute y : Real = x * 2.0; }
    calc def Thrice { in attribute x : Real; out attribute y : Real = x * 3.0; }

    part def 'Qualified Host' {
        attribute source : Real default 3.0;
        calc first_calc : Twice { in x = 'Qualified Host'::source; }
        calc second : Thrice { in x = 'Qualified Host'::source; }
    }

    part host : 'Qualified Host' { :>> source = 12.7; }
}
