package S1SelfNamed {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — shape 1, self-named binding `in availability = availability`.
    calc def Revenue {
        in attribute availability : Real;
        out attribute revenue : Real = availability * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real = 0.85;

        calc revenue_calc : Revenue {
            in availability = availability;
        }
    }

    part plant : 'Plant';
}
