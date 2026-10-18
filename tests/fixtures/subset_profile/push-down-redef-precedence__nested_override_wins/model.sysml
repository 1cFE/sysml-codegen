package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Driver { attribute efficiency : Real default 0.2; calc t : Twice { in v = efficiency; } }
    part def FastDriver :> Driver { :>> efficiency default 0.3; }
    part def Site { part driver : FastDriver; }
    part site : Site { part :>> driver { :>> efficiency = 0.35; } }
}
