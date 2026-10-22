package fx {
    private import ScalarValues::*;
    part def Fac { attribute area : Real = 10.0; }
    part ac_facility : Fac;
    part def Site { part facility :> ac_facility; attribute double : Real = 2.0 * facility.area; }
    part site : Site;
}
