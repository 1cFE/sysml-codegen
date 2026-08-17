package def_qual_two_occ_inside {
    private import ScalarValues::*;

    // D-6, definition-owned leaf: the owner-qualified reference is authored
    // INSIDE the part definition, and TWO occurrences of 'Plant' exist. Each
    // occurrence redefines the attribute to a DIFFERENT value, so a wrong pick
    // is visible. Expected: generates, and each occurrence's calc reads its
    // own occurrence's value.
    calc def Revenue {
        in attribute availability : Real;
        out attribute revenue : Real = availability * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real default 0.85;

        calc revenue_calc : Revenue {
            in availability = 'Plant'::availability;
        }
    }

    part plant_a : 'Plant' {
        :>> availability = 0.11;
    }

    part plant_b : 'Plant' {
        :>> availability = 0.99;
    }
}
