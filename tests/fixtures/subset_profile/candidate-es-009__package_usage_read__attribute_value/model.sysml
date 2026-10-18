package fx {
    private import ScalarValues::*;
    part ac_facility { attribute area : Real = 10.0; }
    part def Site { attribute double : Real = 2.0 * ac_facility.area; }
    part site : Site;
}
