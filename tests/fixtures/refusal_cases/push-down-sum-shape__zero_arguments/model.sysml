package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::*;
    part def Site {
        attribute t : NumericalValue = sum();
    }
    part site : Site;
}
