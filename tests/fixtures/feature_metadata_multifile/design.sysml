package FeatureMetadataDesign {
    private import ScalarValues::*;
    private import FeatureMetadataLibrary::*;

    part reservoir : Reservoir {
        attribute design_length : Real = 5.0; // [m] - design document witness

        calc observe_length : Observe {
            in value = design_length;
        }
    }
}
