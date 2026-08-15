package ElabMatrixC7 {
    private import ScalarValues::*;

    calc def Identity { in attribute x : Real; out attribute y : Real = x; }
    part def Source { attribute value : Real default 5.0; }

    part def Host {
        part left : Source;
        part right : Source;
        calc left_calc : Identity { in x = left.value; }
        calc right_calc : Identity { in x = right.value; }
    }

    part host : Host;
}
