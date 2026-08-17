package S4AQualOneOcc {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — shape 4 (D-6), owner-qualified reference authored INSIDE the
    // part definition. Exactly ONE occurrence of 'Plant' exists.
    calc def Revenue {
        in attribute availability : Real;
        out attribute revenue : Real = availability * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real = 0.85;

        calc revenue_calc : Revenue {
            in availability = 'Plant'::availability;
        }
    }

    part plant : 'Plant';
}
