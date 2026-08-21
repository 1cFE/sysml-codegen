package FeatureMetadataLibrary {
    private import ScalarValues::*;

    calc def Observe {
        in attribute value : Real;
        out attribute result : Real = value;
    }

    part def Reservoir {
        attribute library_flow : Real = 4.0; // [kg/s] - library document witness
    }
}
