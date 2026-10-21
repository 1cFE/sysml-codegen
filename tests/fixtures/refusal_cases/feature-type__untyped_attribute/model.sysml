package fx {
    private import ScalarValues::*;
    part def Site {
        attribute a = 1.0;
        attribute t : Real = a * 2;
    }
    part site : Site;
}
