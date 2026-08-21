package MultifileGroupLibrary {
    private import ScalarValues::*;

    calc def Observe {
        in attribute value : Real;
        in attribute inherited : Real;
        out attribute result : Real = value + inherited;
    }

    part def Host {
        attribute library_value : Real = 1.0;
    }
}
