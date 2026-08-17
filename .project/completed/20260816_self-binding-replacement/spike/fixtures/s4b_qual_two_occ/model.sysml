package S4BQualTwoOcc {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — shape 4 (D-6), owner-qualified reference authored INSIDE the
    // part definition, with TWO occurrences of 'Plant' in the model. Each occurrence
    // redefines the attribute to a DIFFERENT value, so a wrong pick is visible.
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
