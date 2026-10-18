package fx {
    private import ScalarValues::*;
    calc def Rem { in a : Real; in b : Real; return r : Boolean = a > b; }
    part def Site {
        attribute x : Real = 7.0;
        attribute y : Real = 2.0;
        calc t : Rem { in a = x; in b = y; }
    }
    part site : Site;
}
