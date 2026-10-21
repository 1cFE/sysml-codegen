package fx {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        assert constraint bare;
    }
    part site : Site;
}
