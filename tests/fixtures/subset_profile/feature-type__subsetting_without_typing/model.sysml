package fx {
    private import ScalarValues::*;
    part def Site {
        attribute b : Real = 1.0;
        attribute a :> b;
        attribute t : Real = a * 2;
    }
    part site : Site;
}
