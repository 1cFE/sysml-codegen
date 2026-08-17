package S2NamesDiffer {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — shape 2 (D-5), renamed formal `in availability_in = availability`.
    calc def Revenue {
        in attribute availability_in : Real;
        out attribute revenue : Real = availability_in * 100.0;
    }

    part def 'Plant' {
        attribute availability : Real = 0.42;

        calc revenue_calc : Revenue {
            in availability_in = availability;
        }
    }

    part plant : 'Plant';
}
