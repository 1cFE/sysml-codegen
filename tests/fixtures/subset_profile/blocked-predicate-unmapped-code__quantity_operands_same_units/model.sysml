package fx {
    private import ScalarValues::*;
    private import ISQ::*;
    private import SI::*;
    part def Site {
        attribute len : LengthValue = 1.0 [m];
        attribute wid : LengthValue = 2.0 [m];
        assert constraint fits { len + wid <= 3.0 [m] }
    }
    part site : Site;
}
