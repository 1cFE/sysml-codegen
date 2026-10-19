package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    private import TrigFunctions::pi;
    part def Site { attribute t : Real = pi; }
    part site : Site;
}
