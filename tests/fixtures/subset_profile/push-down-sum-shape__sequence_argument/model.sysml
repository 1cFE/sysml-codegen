package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::*;
    part def Site {
        attribute a : Real = 1.0;
        attribute b : Real = 2.0;
        attribute t : Real = sum((a, b)) * 1.0;
    }
    part site : Site;
}
