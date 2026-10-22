package fx {
    private import ScalarValues::*;
    part ac_facility { part hall { attribute area : Real = 10.0; } }
    part def Site { part facility :> ac_facility; attribute double : Real = 2.0 * facility.hall.area; }
    part site : Site;
}
