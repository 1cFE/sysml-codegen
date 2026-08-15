package S9QualOutsideOne {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — same as s8 but with exactly ONE occurrence of the qualifying
    // part definition in the enclosing part.
    calc def Revenue {
        in attribute availability : Real;
        out attribute revenue : Real = availability * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real default 0.85;
    }

    part def 'Fleet' {
        part plant_a : 'Plant' { :>> availability = 0.11; }

        calc revenue_calc : Revenue {
            in availability = 'Plant'::availability;
        }
    }

    part fleet : 'Fleet';
}
