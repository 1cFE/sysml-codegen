package S8QualOutsideTwo {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — owner-qualified reference authored OUTSIDE the qualifying part
    // definition, in an enclosing part that owns TWO occurrences of it.
    calc def Revenue {
        in attribute availability : Real;
        out attribute revenue : Real = availability * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real default 0.85;
    }

    part def 'Fleet' {
        part plant_a : 'Plant' { :>> availability = 0.11; }
        part plant_b : 'Plant' { :>> availability = 0.99; }

        calc revenue_calc : Revenue {
            in availability = 'Plant'::availability;
        }
    }

    part fleet : 'Fleet';
}
