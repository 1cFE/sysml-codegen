package S7SiblingInFormal {
    private import ScalarValues::*;

    // SPIKE THROWAWAY — the D-5 rename where the part attribute's name collides with
    // ANOTHER IN PARAMETER of the same calc def. Not a self-binding (different formal),
    // and no producer cycle. Does the bare RHS still shadow onto the calc's own formal?
    calc def Revenue {
        in attribute availability_in : Real;
        in attribute availability : Real;
        out attribute revenue : Real = availability_in * 100.0 + availability;
    }

    part def 'Plant' {
        attribute availability : Real = 0.85;

        calc revenue_calc : Revenue {
            in availability_in = availability;
        }
    }

    part plant : 'Plant';
}
