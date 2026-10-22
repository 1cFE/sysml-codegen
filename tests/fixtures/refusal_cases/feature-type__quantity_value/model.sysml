package fx {
    private import ScalarValues::*;
    private import ISQ::*;
    part def Site {
        attribute m : MassValue;
        attribute t : Real = m * 2;
    }
    part site : Site;
}
