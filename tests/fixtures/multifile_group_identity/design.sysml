package MultifileGroupDesign {
    private import ScalarValues::*;
    private import MultifileGroupLibrary::*;

    part host : Host {
        attribute design_value : Real = 2.0;
        calc observe : Observe {
            in value = design_value;
            in inherited = library_value;
        }
    }
}
