package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Module { attribute cost : Real = 2.0; }
    part def Site {
        part modules : Module[2];
        attribute total : Real = sum(modules.cost) + 5.0;
        calc t : Twice { in v = total; }
    }
    part site : Site;
}
