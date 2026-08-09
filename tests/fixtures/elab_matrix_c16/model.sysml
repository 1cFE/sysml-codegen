package ElabMatrixC16 {
    private import ScalarValues::*;

    calc def Observe {
        in attribute x : Real;
        out attribute y : Real = x * 2.0;
    }

    part host {
        calc left : Observe { in x = 4.0; }
        calc right : Observe { in x = 4.0; }
    }
}
