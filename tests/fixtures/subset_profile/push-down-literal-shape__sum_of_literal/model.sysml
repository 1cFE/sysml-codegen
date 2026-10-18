package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site {
        attribute total : Real = sum(5.0);
        calc t : Twice { in v = total; }
    }
    part site : Site;
}
