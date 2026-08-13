package CATFMFERadialBuild {
    private import ScalarValues::*;

    calc def TorusMinorRadius {
        in attribute r_inner : Real;  // m
        in attribute r_outer : Real;  // m
        in attribute r_major : Real;  // m
        out attribute a : Real = (r_inner + r_outer) / 2.0 - r_major;  // m
    }

    part catf_radial_build {
        attribute major_radius : Real = 3.0;  // m

        part plasma_region {
            attribute inner_radius : Real = 3.0;  // m
            attribute thickness : Real = 1.1;     // m
            attribute outer_radius : Real = inner_radius + thickness;  // m

            calc minor_calc : TorusMinorRadius {
                in r_inner = inner_radius;
                in r_outer = outer_radius;
                in r_major = major_radius;
            }
        }
    }
}
