package fx {
    private import ScalarValues::*;
    calc def Add { in 'x y' : Real; in x_y : Real; return r : Real = 'x y' + x_y; }
    part def Site {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        calc c : Add { in 'x y' = a; in x_y = b; }
    }
    part site : Site;
}
