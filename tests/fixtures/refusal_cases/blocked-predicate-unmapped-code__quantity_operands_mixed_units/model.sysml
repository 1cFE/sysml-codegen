package fx {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;
    part def Site {
        attribute len : LengthValue = 1.0 [m];
        attribute mass : MassValue = 2.0 [kg];
        assert constraint fits { len + mass <= 3.0 [m] }
    }
    part site : Site;
}
